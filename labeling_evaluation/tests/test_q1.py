"""Question 1 (notebook 40): the wrangling of viz.frames, the two new lib equations and viz.checks reproduce the archive.

The archive is imported HERE ONLY (conftest fixtures ``ds``, ``v``). The new frame is built with the document's own
fold (FOLD5) wherever the archive's five-class column enters, so equality is exact."""
import numpy as np
import pandas as pd
import pytest

from lib import growth
from viz import checks, config, data, frames


@pytest.fixture(scope="module")
def cfg():
    return config.load()


@pytest.fixture(scope="module")
def dsn(cfg):
    return data.load_dataset(cfg)


@pytest.fixture(scope="module")
def vn(dsn, cfg, archive):
    from src.dataset_facts import la_tables
    return frames.base(dsn, cfg, fold=la_tables.FOLD5)


def _num_equal(a: pd.DataFrame, b: pd.DataFrame):
    assert list(a.columns) == list(b.columns)
    assert len(a) == len(b)
    for c in b.columns:
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiub" and y.dtype.kind in "fiub":
            assert np.allclose(x.astype(float), y.astype(float), rtol=0, atol=1e-12, equal_nan=True), c
        else:
            xs = [None if (u is None or (isinstance(u, float) and np.isnan(u))) else u for u in x]
            ys = [None if (u is None or (isinstance(u, float) and np.isnan(u))) else u for u in y]
            assert xs == ys, c


def test_filings_per_year_and_lag(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import la_tables, a2
    old = la_tables.filings_per_year(ds, v).set_index("priority year")
    new = frames.filings_per_year(dsn, vn, cfg)
    assert new.attrs["p90"] == old.attrs["p90"] and new.attrs["snapshot"] == old.attrs["snapshot"]
    _num_equal(new.reset_index(), old.reset_index())
    pd.testing.assert_frame_equal(frames.publication_lag(dsn, "region"), a2.d9_publication_lag(ds, "region"))


def test_growth_series_and_events(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import sm_open, la_figures
    old, new = sm_open.growth_series(ds, v), frames.growth_series(dsn, vn, cfg)
    assert set(old) == set(new)
    for k in old:
        pd.testing.assert_series_equal(new[k], old[k], check_names=False)
    snap = frames.snapshot_date(dsn)
    e_old, e_new = la_figures.sector_events(snap), frames.sector_events(cfg, snap)
    assert list(e_new["event"]) == list(e_old["event"]) and list(e_new["year"]) == list(e_old["year"])


def test_ari(archive, v, vn, cfg):
    from src.dataset_facts import la_tables
    old = la_tables.ari_timeline(v)
    new = frames.ari_timeline(vn, cfg)
    pd.testing.assert_frame_equal(new, old.drop(columns=[], errors="ignore"), check_dtype=False)
    assert list(frames.ari_firms(vn, cfg)["company"]) == sorted(la_tables.ari_firms(v)["company"])


def test_force_frame(archive, ds, v, dsn, vn):
    from src.dataset_facts import sm_open
    for first in (False, True):
        old = sm_open._force_frame(ds, v, first_only=first)
        new = frames.force_frame(dsn, vn, first_only=first)
        pd.testing.assert_frame_equal(new, old, check_dtype=False)
        assert new.attrs["unread"] == old.attrs["unread"]


def test_trl_and_public_frames(archive, ds, dsn):
    from src.dataset_facts import a2
    pd.testing.assert_frame_equal(frames.trl_frame(dsn), a2.trl_frame(ds))
    pd.testing.assert_frame_equal(frames.public_arch_frame(dsn), a2.public_arch_frame(ds))


def test_linked_ids_and_evtolnews(archive, v, vn, cfg):
    from src.dataset_facts import la_tables, sm_open
    assert frames.linked_aircraft_ids(vn, cfg) == set(la_tables.linked_aircraft(v)["aircraft_id"])
    old = sm_open._evn_long(v)
    new = frames.evtolnews_long(vn, cfg, frames.windows_from_config(cfg))
    cols = ["source", "window", "class5"]
    pd.testing.assert_frame_equal(new[cols].reset_index(drop=True), old[cols].reset_index(drop=True))


def test_representativeness(archive, ds, v, vn, dsn, cfg):
    from src.dataset_facts import la_tables, a2
    names = [n for n, _, _ in frames.windows_from_config(cfg)]
    t = a2.trl_frame(ds)[["aircraft_id", "trl"]]
    w_old = v.merge(t, on="aircraft_id", how="left")
    m_old = pd.to_numeric(w_old["trl"], errors="coerce").fillna(2).gt(2)
    a = la_tables._representativeness(w_old, m_old, "above TRL 2")
    tn = frames.trl_frame(dsn)[["aircraft_id", "trl"]]
    w_new = vn.merge(tn, on="aircraft_id", how="left")
    b = frames.representativeness(w_new, pd.to_numeric(w_new["trl"], errors="coerce").fillna(2).gt(2), "above TRL 2", names)
    _num_equal(b, a)
    firms = set(la_tables.ari_firms(v)["company"])
    _num_equal(frames.representativeness(vn.copy(), vn["company_canonical"].isin(firms), "index firms", names),
               la_tables._representativeness(v.copy(), v["company_canonical"].isin(firms), "index firms"))


def test_trace_frame(archive, ds, v, dsn, vn):
    from src.dataset_facts import la_tables
    pd.testing.assert_frame_equal(frames.trace_frame(dsn, vn), la_tables.trace_frame(ds, v), check_dtype=False)


def test_visible_at_snapshot(archive, ds, v, dsn, vn):
    from src.dataset_facts import sm_open
    old = sm_open.region_years(ds, v)
    old = old[old["priority year"] == 2023].set_index("region")["visible at the snapshot"]
    new = frames.visible_at_snapshot(dsn, vn, 2023)
    assert np.allclose(new.reindex(old.index).to_numpy(), old.to_numpy(), rtol=0, atol=1e-12)


def test_growth_ratio_table_equals_archive(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import sm_open
    keys = ["evtol_families", "evtol_aircraft"], ["b64", "secb", "all"]
    old_draws = sm_open.DRAWS
    sm_open.DRAWS = 200
    try:
        a = sm_open.growth_ratios(ds, v)
    finally:
        sm_open.DRAWS = old_draws
    b = growth.growth_ratio_table(frames.growth_series(dsn, vn, cfg), *keys, draws=200)
    assert np.allclose(a["times as fast"].to_numpy(float), b["times as fast"].to_numpy(float), rtol=0, atol=1e-12)
    ci = [f"{lo:.2f} to {hi:.2f}" for lo, hi in zip(b["low"], b["high"])]
    assert list(a["95 % interval"]) == ci
    assert list(a["reading"]) == list(b["reading"]) and list(a["primary"]) == list(b["primary"])


def test_visible_share_formula():
    lags = np.array([1, 1, 2, 2, 2, 3])
    assert growth.visible_share(lags, 2, 0.5) == pytest.approx(2 / 6 + 0.5 * 3 / 6)
    assert np.isnan(growth.visible_share([], 2, 0.5))


# ------------------------------------------------------------------------------------------ viz.checks
def test_checks_numbers_tolerate_format_only():
    ok = checks.numbers({"acquired_s": "1 639", "snapshot": "2026-06-08"}, "1")
    assert list(ok["match"]) == ["yes", "yes"]
    bad = checks.numbers({"acquired_s": "1 640", "nope": "1"}, "1")
    assert list(bad["match"]) == ["NO", "not in the document"]
    exp = checks.numbers({"acquired_s": "1 640"}, "1", expected={"acquired_s": checks.SRW_RULING})
    assert exp["match"].iloc[0] == checks.SRW_RULING


def test_checks_table_rounding_and_expected(cfg):
    ref = checks.reference_table("la_public_pairwise", cfg)
    f = pd.DataFrame({"comparison": ref["comparison"], "agree": ref["agree"].astype(int), "of": ref["of"].astype(int),
                      "share": [0.8969, 0.9175, 0.9588]})          # more decimals than printed: still a match
    assert checks.table(f, "la_public_pairwise", cfg, key=["comparison"], columns=["comparison", "agree", "of", "share"]).iloc[0]["status"] == "match"
    g = f.copy()
    g.loc[0, "share"] = 0.93                                         # a different value is never absorbed
    r = checks.table(g, "la_public_pairwise", cfg, key=["comparison"], columns=["comparison", "agree", "of", "share"])
    assert r.iloc[0]["differences"] == 1 and r.iloc[0]["status"] == "DIFFERS"
    r2 = checks.table(g, "la_public_pairwise", cfg, key=["comparison"], columns=["comparison", "agree", "of", "share"],
                      expected=checks.changed_cells(g, f, ["comparison"]))
    assert r2.iloc[0]["differences"] == 0 and r2.iloc[0]["expected differences"] == 1
    assert checks.detail(r2)["label"].iloc[0] == checks.SRW_RULING
