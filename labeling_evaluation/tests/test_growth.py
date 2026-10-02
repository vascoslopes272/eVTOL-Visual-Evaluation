"""lib.growth reproduces the archived doubling time / ratio / turning point / baseline arithmetic / lag p90."""
import numpy as np
import pandas as pd
import pytest

from lib import growth


def _same(a: pd.DataFrame, b: pd.DataFrame, skip=()):
    cols = [c for c in b.columns if c not in skip]
    assert len(a) == len(b)
    for c in cols:
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiu" and y.dtype.kind in "fiu":
            assert np.allclose(x.astype(float), y.astype(float), rtol=0, atol=1e-12, equal_nan=True), c
        else:
            xs = [None if (v is None or (isinstance(v, float) and np.isnan(v))) else v for v in x]
            ys = [None if (v is None or (isinstance(v, float) and np.isnan(v))) else v for v in y]
            assert xs == ys, c


def _sm_open(archive):
    from src.dataset_facts import sm_open
    return sm_open


@pytest.fixture(scope="module")
def series(archive, ds, v):
    return _sm_open(archive)._series_for_fit(ds, v)


def test_loglin_and_window_frame(archive, series):
    so = _sm_open(archive)
    for s in series.values():
        for lo, hi in [(2005, 2023), (2005, 2019), (2010, 2023), (2013, 2023), (2000, 2004)]:
            ya, ca = so._window_frame(s, lo, hi)
            yb, cb = growth.window_frame(s, lo, hi)
            assert (ya == yb).all() and (ca == cb).all()
            fa, fb = so._loglin(ya, ca), growth.loglinear_fit(yb, cb)
            assert fa.keys() == fb.keys()
            for k in fa:
                assert np.allclose(fa[k], fb[k], rtol=0, atol=1e-12, equal_nan=True), k
            if fa:
                code = growth.curvature_shape(fb)
                txt = so._fit_shape(fa)
                assert {"exponential": "exponential", "bends_down": "bends down", "bends_up": "bends up"}[code] == txt.split(" —")[0]


def test_poisson_matches_statsmodels(archive, series):
    so = _sm_open(archive)
    for s in series.values():
        for lo, hi in [(2005, 2023), (2005, 2019), (2010, 2023), (2013, 2023)]:
            y, c = so._window_frame(s, lo, hi)
            a, b = so._poisson_slope(y, c), growth.poisson_doubling_time(y, c)
            assert np.allclose(a, b, rtol=0, atol=1e-9, equal_nan=True), (a, b)
            assert round(a, 2) == round(b, 2)


def test_doubling_time_table(archive, ds, v, series, reference):
    a = _sm_open(archive).doubling_time(ds, v)
    b = growth.doubling_time_table(series)
    shape = {"exponential": "exponential", "bends_down": "bends down — doubling time is a window average",
             "bends_up": "bends up — doubling time is a window average"}
    b = b.assign(shape=b["shape"].map(shape))
    _same(b, a, skip=["95 % interval"])
    ref = pd.read_csv(reference / "la_doubling_time.csv")
    assert np.allclose(b["doubling time (years)"], ref["doubling time (years)"], rtol=0, atol=1e-12)
    assert np.allclose(b["R²"], ref["R²"], rtol=0, atol=1e-12)
    assert (b["total"].to_numpy() == ref["total"].to_numpy()).all()


def test_doubling_ratio_small_draws(archive, ds, v, series):
    so = _sm_open(archive)
    name = f"aeronautics — {so.BASELINE_LABEL}"
    corpus = ["eVTOL aircraft (this corpus)", "eVTOL patents (this corpus)"]
    old = so.DRAWS
    so.DRAWS = 200
    try:
        a = so.doubling_ratio(ds, v)
    finally:
        so.DRAWS = old
    b = growth.doubling_ratio_table(series, name, corpus, draws=200)
    _same(b, a, skip=["times faster interval"])


def test_doubling_ratio_full_vs_reference(archive, series, reference):
    name = f"aeronautics — {_sm_open(archive).BASELINE_LABEL}"
    corpus = ["eVTOL aircraft (this corpus)", "eVTOL patents (this corpus)"]
    b = growth.doubling_ratio_table(series, name, corpus)
    ref = pd.read_csv(reference / "la_doubling_ratio.csv")
    for c in ["corpus doubling (years)", "baseline doubling (years)", "ratio (corpus / baseline)", "times faster",
              "95 % low", "95 % high", "times faster low", "times faster high", "draws used"]:
        assert np.allclose(b[c].astype(float), ref[c].astype(float), rtol=0, atol=1e-12, equal_nan=True), c


def test_turning_point(archive, ds, v):
    from src.dataset_facts import la_tables, sm_index
    f = la_tables.filings_per_year(ds, v)
    exp = sm_index._turning_numbers({"la_filings_per_year": f}, {})
    d = f[(f["priority year"] >= 2006) & (f["priority year"] <= 2023)]
    t = d["priority year"].to_numpy(float)
    rng = np.random.default_rng(42)
    pat = growth.turning_point(t, np.log(d["patents representative"].to_numpy(float)), rng)
    ac = growth.turning_point(t, np.log(d["unique aircraft"].to_numpy(float)), rng)
    sh = growth.turning_point(t, np.log(d["aircraft per 1 000 B64"].to_numpy(float)), rng)
    assert str(pat["break"]) == exp["sm_turn_pat_year"]
    assert f"{pat['jump']:.1f}" == exp["sm_turn_pat_x"]
    assert f"{pat['share']:.0%}".replace("%", " %") == exp["sm_turn_pat_boot"]
    assert (str(ac["break"]), f"{ac['jump']:.1f}", str(ac["lo"]), str(ac["hi"])) == (
        exp["sm_turn_ac_year"], exp["sm_turn_ac_x"], exp["sm_turn_ac_lo"], exp["sm_turn_ac_hi"])
    assert (str(sh["lo"]), str(sh["hi"])) == (exp["sm_turn_sh_lo"], exp["sm_turn_sh_hi"])


def test_two_segment_fit_direct(archive):
    t = np.arange(2006, 2024, dtype=float)
    y = np.log(np.arange(1, 19) ** 1.5 + 3)
    sse, c = growth.two_segment_fit(t, y, 2014)
    X = np.c_[np.ones_like(t), t, (t >= 2014).astype(float), np.maximum(t - 2014, 0)]
    c2 = np.linalg.lstsq(X, y, rcond=None)[0]
    assert np.allclose(c, c2, rtol=0, atol=1e-12)


def test_baseline_normalisation(archive, ds, v):
    from src.dataset_facts import la_tables, la_baseline as lb
    f = la_tables.filings_per_year(ds, v)
    tab = f.set_index("priority year")
    base = lb.series(lb.PRIMARY).reindex(tab.index)
    for c, ac in (("unique aircraft", "aircraft per 1 000 B64"), ("patents acquired", "patents per 1 000 B64")):
        got = growth.per_thousand(tab[c], base)
        assert np.allclose(got.to_numpy(float), tab[ac].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    ix = growth.index_to_base(tab["patents acquired"].astype(float)).round(0)
    assert np.allclose(ix.to_numpy(float), tab["eVTOL index (2005-09 = 100)"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    ix2 = growth.index_to_base(base.astype(float)).round(0)
    assert np.allclose(ix2.to_numpy(float), tab["aviation index (2005-09 = 100)"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    assert growth.index_to_base(pd.Series([0.0, 0.0], index=[2005, 2006])).isna().all()
    # share multiples
    mult = lb.multiples(tab)
    done = tab[tab["complete"].astype(bool) & (tab.index >= 2005)]
    mine = growth.share_multiple(pd.to_numeric(done["patents acquired"]), pd.to_numeric(done["B64 families (worldwide)"]))
    assert np.allclose(mine.to_numpy(float), mult["B64"].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True)
    # first year above
    r = lb.readings(tab)
    t = tab[tab.index >= 2005]
    comp = t[t["complete"].astype(bool)]
    gap = comp["eVTOL index (2005-09 = 100)"] - comp["aviation index (2005-09 = 100)"]
    assert growth.first_year_above(gap) == r["first_above"]
    assert growth.first_year_above(pd.Series([-1, 2, -1, 3], index=[1, 2, 3, 4])) == 4
    assert growth.first_year_above(pd.Series([-1, -2], index=[1, 2])) is None


def test_lag_p90_and_completeness(archive, ds, v):
    from src.dataset_facts import la_tables
    j = ds.patents_analysis.merge(ds.identity[["patent_id", "priority_year", "pub_year"]], on="patent_id",
                                  how="left", suffixes=("", "_id"))
    lag = pd.to_numeric(j["pub_year"], errors="coerce") - pd.to_numeric(j["priority_year"], errors="coerce")
    p90 = growth.lag_quantile(lag)
    assert p90 == la_tables.lag_p90(ds)
    f = la_tables.filings_per_year(ds, v)
    el, comp = growth.year_is_complete(f["priority year"], p90)
    assert np.allclose(el, f["years since year end"], rtol=0, atol=1e-12)
    assert (comp == f["complete"].to_numpy()).all()
