"""lib.drivers reproduces the archived trace trends, drift, driver verdicts and coupling selection."""
import numpy as np
import pandas as pd
import pytest

from lib import drivers

CLASS_OF = {"does_not_move": "trace does not move", "mixed_by_class": "mixed by class",
            "fixed_only": "moves, but only fixed physical drivers predict this trace",
            "opposed": "opposed drivers", "single": "single driver",
            "against_all": "moved against every driver that predicts a direction",
            "overdetermined": "overdetermined", "not_labelled": "not labelled"}


def _same(a: pd.DataFrame, b: pd.DataFrame, skip=()):
    assert len(a) == len(b)
    for c in b.columns:
        if c in skip:
            continue
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiub" and y.dtype.kind in "fiub":
            assert np.allclose(x.astype(float), y.astype(float), rtol=0, atol=1e-12, equal_nan=True), c
        else:
            xs = [None if (u is None or (isinstance(u, float) and np.isnan(u))) else u for u in x]
            ys = [None if (u is None or (isinstance(u, float) and np.isnan(u))) else u for u in y]
            assert xs == ys, c


@pytest.fixture(scope="module")
def la(archive):
    from src.dataset_facts import la_tables
    return la_tables


@pytest.fixture(scope="module")
def names(archive):
    from src.dataset_facts import metrics
    return metrics.ARCH_NAMES


@pytest.fixture(scope="module")
def tf(la, ds, v):
    return la.trace_frame(ds, v)


def test_constants_copied(la):
    assert drivers.DRIVERS == la.DRIVERS and drivers.TRACES == la.TRACES
    assert drivers.PREDICTED_COUPLINGS == la.PREDICTED_COUPLINGS
    assert drivers.DEFINITIONAL_PAIRS == la._DEF_PAIRS
    assert drivers.UNLABELLED_TRACES == la.UNLABELLED_TRACES and drivers.POOLED == la.POOLED
    assert (drivers.TREND_MIN, drivers.TREND_ALPHA, drivers.COUPLING_MIN_N) == (la.TREND_MIN, la.TREND_ALPHA, la.COUPLING_MIN_N)
    assert (drivers.WINDOW_NAMES, drivers.LAST_COMPLETE, drivers.MIN_CELL) == (la.WINDOW_NAMES, la.LAST_COMPLETE, la.MIN_CELL)


def test_class_selection(la, v):
    assert drivers.class_selection(v) == la.drawn_classes(v)
    assert drivers.class_selection(v, 3, 2) == la.drawn_classes(v, 3, 2)


def test_dimension_drift(la, v, names):
    cl = la.drawn_classes(v)
    _same(drivers.dimension_drift(v, cl, class_names=names), la.dimension_drift(v))


def test_trace_drift_and_trends(la, ds, v, tf, names, reference):
    cl = la.drawn_classes(v)
    da = la.trace_drift(ds, v)
    db = drivers.trace_drift(tf, cl, class_names=names)
    _same(db, da)
    ta = la.trace_trends(ds, v)
    tb = drivers.trace_trends(tf, db, cl, class_names=names)
    _same(tb, ta)
    ref = pd.read_csv(reference / "la_trace_trends.csv")
    assert (tb["movement"].to_numpy() == ref["movement"].to_numpy()).all()
    assert np.allclose(tb["rho"].to_numpy(float), ref["rho"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    assert np.allclose(tb["p"].to_numpy(float), ref["p"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    refd = pd.read_csv(reference / "la_trace_drift.csv")
    assert np.allclose(db[drivers.TRACES[0]["label"]].to_numpy(float), refd[drivers.TRACES[0]["label"]].to_numpy(float), equal_nan=True, atol=1e-12)


def test_trend_test_rules():
    yr = pd.Series(np.arange(2000, 2030))
    x = pd.Series(np.arange(30, dtype=float))
    assert drivers.trend_test(yr, x)["movement"] == "rises"          # only years <= 2023 counted: 24 pairs
    assert drivers.trend_test(yr, -x)["movement"] == "falls"
    assert drivers.trend_test(yr, pd.Series(np.ones(30)))["movement"] == "constant"
    assert drivers.trend_test(yr[:15], x[:15])["movement"] == "too thin"
    rng = np.random.default_rng(0)
    assert drivers.trend_test(yr, pd.Series(rng.normal(size=30)))["movement"] == "flat"


def test_driver_verdicts(la, ds, v, tf, names, reference):
    cl = la.drawn_classes(v)
    trends = la.trace_trends(ds, v)
    va = la.driver_verdicts(ds, v, trends)
    vb = drivers.driver_verdicts(trends)
    assert len(va) == len(vb)
    got = [CLASS_OF[c] for c in vb["verdict"]]
    assert got == list(va["verdict class"])
    ref = pd.read_csv(reference / "la_driver_verdicts.csv")
    assert got == list(ref["verdict class"])
    assert list(vb["driver kind"]) == list(va["driver kind"])
    # counts quoted in the sentence
    for (_, a), (_, b) in zip(va.iterrows(), vb.iterrows()):
        if b["verdict"] == "overdetermined":
            assert f"overdetermined ({len(b['consistent'])} drivers)" in a["verdict"]
        if b["verdict"] == "single":
            assert drivers.DRIVERS[b["consistent"][0]][1] in a["verdict"]
        if b["verdict"] == "opposed":
            for c in b["with"] + b["against"]:
                assert drivers.DRIVERS[c][1] in a["verdict"]


def test_driver_verdict_branches():
    D = {"A1.transition": "+", "C.development": "-"}
    assert drivers.driver_verdict(D, "0")["verdict"] == "does_not_move"
    assert drivers.driver_verdict(D, "mixed")["verdict"] == "mixed_by_class"
    assert drivers.driver_verdict({"A2.drag": "±"}, "+")["verdict"] == "fixed_only"
    r = drivers.driver_verdict(D, "+")
    assert r["verdict"] == "opposed" and r["with"] == ["A1.transition"] and r["against"] == ["C.development"]
    assert drivers.driver_verdict({"A1.dep": "+", "A2.drag": "±"}, "+") ["verdict"] == "single"
    assert drivers.driver_verdict({"A1.dep": "+", "A2.drag": "±"}, "+")["fixed"] == ["A2.drag"]
    assert drivers.driver_verdict({"A1.dep": "+"}, "-")["verdict"] == "against_all"
    assert drivers.driver_verdict({"A1.dep": "+", "B.noise": "+"}, "+")["verdict"] == "overdetermined"


@pytest.fixture(scope="module")
def couplings(la, ds, v):
    F = la._coupling_fields(ds, v)
    return F, F.attrs["fields"]


def test_couplings(la, ds, v, couplings, reference):
    F, fields = couplings
    pa = la.trace_couplings(ds, v)
    pb = drivers.coupling_table(F, fields, la.cramers_v_bc)
    _same(pb, pa)
    assert {k: pb.attrs[k] for k in pa.attrs} == pa.attrs
    ra = la.predicted_couplings(ds, v, pa)
    rb = drivers.predicted_couplings(pb)
    assert len(ra) == len(rb)
    assert list(rb["fields"]) == list(ra["fields"])
    assert np.allclose(rb["V"].to_numpy(float), ra["V"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    assert np.allclose(rb["percentile"].to_numpy(float), ra["percentile among non-definitional pairs"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    text = {"not_measurable": "not measurable (too few aircraft answer both)",
            "strongest_tenth": "among the strongest tenth of all pairs",
            "above_upper_quartile": "above the upper quartile of all pairs",
            "typical": "no stronger than a typical pair", "weaker": "weaker than a typical pair",
            "for_scale": "what the record does couple, for scale"}
    assert [text[x] for x in rb["reading"]] == list(ra["reading"])
    ref = pd.read_csv(reference / "la_trace_couplings.csv")
    assert [text[x] for x in rb["reading"]] == list(ref["reading"])
    assert np.allclose(rb["V"].to_numpy(float), ref["V"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    refall = pd.read_csv(reference / "la_trace_couplings_all.csv", keep_default_na=False)
    assert np.allclose(pb["V"].to_numpy(float), pd.to_numeric(refall["V"], errors="coerce").to_numpy(float), atol=1e-12, equal_nan=True)


def test_coupling_table_with_toy_measure():
    F = pd.DataFrame({"a": list("xxyy") * 10, "b": list("xyxy") * 10, "c": list("xxyy") * 10})
    t = drivers.coupling_table(F, ["a", "b", "c"], lambda x, y: (float(x.eq(y).mean()), len(x)),
                               predicted=[("A2.hover", "a", "c", "toy")], definitional={frozenset(("a", "b"))})
    assert t["definitional"].tolist() == [True, False, False]
    assert t.loc[1, "driver"] == "A2.hover" and t.attrs["rest"] == 2
    assert drivers.coupling_reading(np.nan, .1, .2, .3) == "not_measurable"
    assert drivers.coupling_reading(.3, .1, .2, .3) == "strongest_tenth"


def test_driver_windows_and_links(archive, ds, v, names):
    from src.dataset_facts import sm_open
    cf = sm_open.config_frame(ds, v)
    a = sm_open.driver_windows(ds, v, cf)
    b = drivers.driver_windows(cf, sm_open.CH3B_CLASSES, sm_open.CH3B_WINDOWS, sm_open.CH3B_FEW, class_names=names)
    _same(b, a)
    _same(drivers.driver_links(cf), sm_open.driver_links(ds, v, cf))


def test_coupling_table_default_measure_is_lib_cramers_v(archive, ds, v):
    """With no measure given, coupling_table uses lib.association.cramers_v_bc and equals the archive's."""
    from src.dataset_facts import la_tables as la
    from lib import drivers
    F = la._coupling_fields(ds, v)
    fields = list(F.columns)
    a = drivers.coupling_table(F, fields)
    b = drivers.coupling_table(F, fields, measure=la.cramers_v_bc)
    pd.testing.assert_frame_equal(a, b)
