"""lib.regional reproduces the archived specialisation, lead/lag, lag offsets / constancy, region lag, proximity test."""
import time

import numpy as np
import pandas as pd
import pytest

from lib import regional


def _same(a: pd.DataFrame, b: pd.DataFrame, skip=()):
    assert list(a.columns) == [c for c in a.columns]
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
def mods(archive):
    from src.dataset_facts import la_tables, sm_open, metrics
    return la_tables, sm_open, metrics


def test_specialisation(mods, v, reference):
    la, _, _ = mods
    for m in (5, 3, 10):
        lq_a, c_a = la.specialisation(v, m)
        lq_b, c_b = regional.specialisation(v, regional.REGIONS, m)
        assert lq_a.equals(lq_b) and c_a.equals(c_b)
    lq, c = regional.specialisation(v)
    ref = pd.read_csv(reference / "la_specialisation.csv")
    assert list(ref["archetype"]) == list(lq.index)
    assert ref["aircraft"].tolist() == c.sum(axis=1).tolist()
    assert np.allclose(lq[list(regional.REGIONS)].to_numpy(), ref[list(regional.REGIONS)].to_numpy(), rtol=0, atol=1e-12)
    assert regional.location_quotient(pd.DataFrame({"a": [2, 2], "b": [1, 3]}, index=["x", "y"])).loc["x", "a"] == round((2 / 4) / (3 / 8), 2)


def test_lead_lag(mods, v, reference):
    la, _, metrics = mods
    for by, top in (("region3", None), ("topType", 7), ("topType", None)):
        ca, qa = la.lead_lag(v, by, top)
        cb, qb = regional.lead_lag(v, by, top, names=metrics.ARCH_NAMES)
        assert np.allclose(ca.to_numpy(), cb.to_numpy(), rtol=0, atol=1e-12) and list(ca.columns) == list(cb.columns)
        _same(qb, qa)
    _, q = regional.lead_lag(v, "region3")
    ref = pd.read_csv(reference / "la_lead_lag_region.csv")
    assert q[["25 %", "50 %", "75 %", "aircraft"]].to_numpy().tolist() == ref[["25 %", "50 %", "75 %", "aircraft"]].to_numpy().tolist()


def test_lag_frame_and_offsets(mods, v, reference):
    _, so, metrics = mods
    wa = so.lag_frame(v)
    wb = regional.lag_frame(v, class_names=metrics.ARCH_NAMES)
    assert wa.equals(wb)
    oa, ob = so.lag_offsets(v), regional.lag_offsets(wb)
    _same(ob, oa)
    ref = pd.read_csv(reference / "la_lag_offsets.csv")
    for c in ["aircraft", "median priority year", "offset vs North America (years)", "95 % low", "95 % high"]:
        assert np.allclose(ob[c].to_numpy(float), ref[c].to_numpy(float), rtol=0, atol=1e-12), c


def test_lag_offsets_since(mods, v, reference):
    _, so, metrics = mods
    a = so.lag_offsets_since(v)
    b = regional.lag_offsets_since(v, class_names=metrics.ARCH_NAMES)
    _same(b, a)
    ref = pd.read_csv(reference / "la_lag_offsets_2016.csv")
    assert np.allclose(b["offset vs North America (years)"].to_numpy(float), ref["offset vs North America (years)"].to_numpy(float), atol=1e-12)
    assert (b["priority years"] == ref["priority years"]).all()


def _verdict_code(text):
    return ("not_constant" if text.startswith("not a constant") else
            "borderline" if text.startswith("borderline") else "consistent")


def _constancy(so, v, metrics, perms):
    wb = regional.lag_frame(v, class_names=metrics.ARCH_NAMES)
    off = regional.lag_offsets(wb)
    return regional.lag_constancy(wb, off, perms=perms)


def test_lag_constancy_small_perms(mods, v):
    _, so, metrics = mods
    a = so.lag_constancy(v, perms=200)
    b = _constancy(so, v, metrics, 200)
    _same(b, a, skip=["effect", "verdict"])
    assert b.attrs["verdict_code"] == _verdict_code(a.attrs["verdict"])
    assert b.attrs["offset_spread"].equals(a.attrs["offset_spread"])
    # named regions agree with the archive sentence
    for kind, reg, *_ in b.attrs["verdict_regions"]:
        assert reg in a.attrs["verdict"]


def test_lag_constancy_full_vs_reference(mods, v, reference):
    _, so, metrics = mods
    t0 = time.time()
    b = _constancy(so, v, metrics, 5000)
    print("lag_constancy full run", time.time() - t0, "s")
    ref = pd.read_csv(reference / "la_lag_constancy.csv")
    for c in ["df", "F (on ranks)", "p (parametric)", "p (permutation)", "partial η²", "aircraft", "classes",
              "p (Holm, across the two regions)"]:
        assert np.allclose(b[c].to_numpy(float), ref[c].to_numpy(float), rtol=0, atol=1e-12, equal_nan=True), c
    assert b.attrs["verdict_code"] == _verdict_code(ref["verdict"].iloc[0])


def test_lag_verdict_branches():
    spread = pd.DataFrame()
    reg = pd.DataFrame({"region tested": ["Europe", "Asia-Pacific"], "p (permutation)": [0.03, 0.2], "holm": [0.06, 0.2]})
    assert regional.lag_verdict(0.01, spread, reg) == ("not_constant", [])
    assert regional.lag_verdict(0.07, spread, reg) == ("borderline", [("raw", "Europe", 0.03, 0.06)])
    reg2 = reg.assign(holm=[0.04, 0.2])
    assert regional.lag_verdict(0.07, spread, reg2) == ("borderline", [("holm", "Europe", 0.04)])
    assert regional.lag_verdict(0.5, spread, None) == ("consistent", [])


def test_region_lag(mods, ds, v, reference):
    _, so, _ = mods
    a = so.region_lag(ds, v)
    j = v.merge(ds.identity[["patent_id", "pub_year"]], on="patent_id", how="left", suffixes=("", "_pub"))
    j["pub_year"] = j["pub_year_pub"] if "pub_year_pub" in j else j["pub_year"]
    b = regional.region_lag(j)
    _same(b, a)
    ref = pd.read_csv(reference / "la_region_lag.csv")
    for c in ["aircraft 2016-21", "median lag (years)", "its share", "published within 0 y", "published within 3 y"]:
        assert np.allclose(b[c].to_numpy(float), ref[c].to_numpy(float), rtol=0, atol=1e-12), c


def test_region_proximity(mods, ds, v, reference):
    la, so, _ = mods
    m, summ = la.proximity_by_region(ds, v)
    labels = m.attrs["region"].to_numpy()
    res = regional.region_proximity_test(m.to_numpy(), labels)
    a = summ.attrs
    assert res["same_mean"] == a["same mean"] and res["same_pairs"] == a["same pairs"]
    assert res["different_mean"] == a["different mean"] and res["different_pairs"] == a["different pairs"]
    assert res["gap"] == a["gap"] and res["p"] == a["p"] and res["draws"] == a["draws"]
    _same(regional.region_pair_summary(m.to_numpy(), labels), summ)
    # small draws, different seed: still equal to a hand permutation of the archive routine
    small = regional.region_proximity_test(m.to_numpy(), labels, draws=300, seed=7)
    la_small = la.proximity_by_region(ds, v, draws=300, seed=7)[1].attrs
    assert small["p"] == la_small["p"] and small["gap"] == la_small["gap"]
    ref = pd.read_csv(reference / "la_region_proximity_test.csv").iloc[0]
    assert (len(labels), res["same_pairs"], res["same_mean"], res["different_pairs"], res["different_mean"], res["p"]) == (
        ref["firms"], ref["same-region pairs"], ref["same-region mean"], ref["different-region pairs"],
        ref["different-region mean"], ref["p (permutation)"])
