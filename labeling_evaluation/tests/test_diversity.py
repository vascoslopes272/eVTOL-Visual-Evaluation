"""lib.diversity reproduces the archived functions and the document's tables."""
import numpy as np
import pandas as pd
import pytest

from lib import diversity as dv

ATOL = dict(rtol=0, atol=1e-12)


def _mods(archive):
    from src.dataset_facts import la_tables, metrics, sm_open
    return la_tables, metrics, sm_open


def _levels(v, sm_open, la_tables):
    w = sm_open._complete(v)
    out = {}
    for level in sm_open.DISCOVERY_LEVELS:
        key = la_tables._archetype_key(w, level)
        ok = key.notna()
        out[level] = (w.loc[ok, "year"].to_numpy(), key[ok])
    return w, out


def test_effective_number(archive, v):
    la, metrics, _ = _mods(archive)
    for col in ["topType", "archetype", "window", "year"]:
        a, b = metrics.effective_number(v[col]), dv.effective_number(v[col])
        assert (np.isnan(a) and np.isnan(b)) or a == b
    assert np.isnan(dv.effective_number(pd.Series([None, None], dtype=object)))


def test_hill_numbers(archive, v):
    la, _, _ = _mods(archive)
    for col in ["topType", "archetype"]:
        for kw in [dict(), dict(n=20, draws=50, seed=7), dict(n=500, draws=30)]:
            assert la.hill_numbers(v[col], **kw) == dv.hill_numbers(v[col], **kw)


def test_hill_by_window(archive, v, reference):
    la, _, _ = _mods(archive)
    a = la.hill_by_window(v)
    b = dv.hill_by_window(v, la.WINDOW_NAMES)
    pd.testing.assert_frame_equal(a, b)
    ref = pd.read_csv(reference / "la_hill_by_window.csv", keep_default_na=False)
    assert list(ref["window"]) == list(b["window"])
    for c in ["aircraft", "D0", "D1", "D2", "D2 low", "D2 high"]:
        assert np.allclose(ref[c].astype(float), b[c].astype(float), rtol=0, atol=0.005 + 1e-9), c


def test_rarefaction_and_chao(archive, v):
    la, _, sm = _mods(archive)
    w = sm._complete(v)
    for level in sm.DISCOVERY_LEVELS:
        counts = la._archetype_key(w, level).dropna().value_counts().to_numpy()
        ns = np.arange(0, counts.sum() + 1, 7)
        assert np.allclose(sm._rarefaction(counts, ns), dv.rarefaction_curve(counts, ns), **ATOL)
        a, b = sm._chao1(counts), dv.chao1_jackknife(counts)
        assert a.keys() == b.keys()
        for k in a:
            assert np.isclose(a[k], b[k], **ATOL, equal_nan=True), k
    # edge cases: no doubletons, N <= 2, f1 = 0
    for counts in [np.array([1, 1, 1, 1]), np.array([1, 1]), np.array([5, 5]), np.array([1, 2, 3])]:
        a, b = sm._chao1(counts), dv.chao1_jackknife(counts)
        for k in a:
            assert np.isclose(a[k], b[k], **ATOL, equal_nan=True), (counts, k)


@pytest.fixture(scope="module")
def curve_pair(archive, ds, v):
    la, _, sm = _mods(archive)
    t_arch = sm.discovery_curve(ds, v)
    _, levels = _levels(v, sm, la)
    return t_arch, dv.discovery_curve_levels(levels, orders=sm.ORDERS, seed=sm.SEED)


def test_discovery_curve(curve_pair, reference):
    a, b = curve_pair
    assert list(a.columns) == list(b.columns)
    for c in a.columns:
        if c == "level":
            assert (a[c].to_numpy() == b[c].to_numpy()).all()
        else:
            assert np.allclose(a[c].astype(float), b[c].astype(float), **ATOL), c
    ref = pd.read_csv(reference / "la_discovery_curve.csv", keep_default_na=False)
    assert len(ref) == len(b)
    for c in b.columns:
        if c != "level":
            assert np.allclose(ref[c].astype(float), b[c].astype(float), rtol=0, atol=0.0051), c


def test_discovery_estimators(archive, ds, v, curve_pair, reference):
    la, _, sm = _mods(archive)
    a_tab = sm.discovery_estimators(ds, v, curve=curve_pair[0])
    w = sm._complete(v)
    _, curve = curve_pair
    for _, r in a_tab.iterrows():
        level = r["level"]
        counts = la._archetype_key(w, level).dropna().value_counts().to_numpy()
        est = dv.chao1_jackknife(counts)
        c = curve[curve["level"].eq(level)].sort_values("aircraft")
        t = dv.discovery_tail(c["archetypes (date order)"].to_numpy(),
                              c["archetypes (random order)"].to_numpy())
        assert est["Chao1"] and round(est["Chao1"], 1) == r["Chao1"]
        assert round(est["jackknife 1"], 1) == r["jackknife 1"]
        assert round(est["jackknife 2"], 1) == r["jackknife 2"]
        assert round(est["coverage (Good–Turing)"], 4) == r["coverage"]
        assert round(t["last"], 2) == r["new in the last 100 aircraft"]
        assert round(t["prev"], 2) == r["new in the 100 before that"]
        assert round(t["rar_last"], 2) == r["new in the last 100, random order"]
        assert round(t["half"], 1) == r["archetypes by half the corpus"]
        code = dv.discovery_verdict_code(est, t["last"], t["rar_last"])
        assert r["verdict"].startswith(code)
    ref = pd.read_csv(reference / "la_discovery_estimators.csv", keep_default_na=False)
    for col in ["Chao1", "jackknife 1", "jackknife 2", "coverage", "aircraft"]:
        assert np.allclose(ref[col].astype(float), a_tab[col].astype(float), rtol=0, atol=1e-9), col
