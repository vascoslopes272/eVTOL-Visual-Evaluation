"""lib.dominant_design reproduces the archived three conditions (RNG sequences included)."""
import time

import numpy as np
import pandas as pd
import pytest

from lib import dominant_design as dd
from lib.distance import gower_distance, subsystem_weights, uniform_weights

ATOL = dict(rtol=0, atol=1e-12)


def _mods():
    from src.dataset_facts import a3, la_tables, sm_open
    return a3, la_tables, sm_open


def _same(a, b, cols):
    assert len(a) == len(b)
    for c in cols:
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiu" and y.dtype.kind in "fiu":
            assert np.allclose(x.astype(float), y.astype(float), **ATOL, equal_nan=True), c
        else:
            assert list(x) == list(y), c


# ------------------------------------------------------------ condition 1
def test_yearly_top_share(archive, ds, v):
    _, la, sm = _mods()
    arch = sm.dd_yearly(ds, v)
    state = sm._patent_state(ds, v)
    keys = sm._level_keys(ds, v)
    years = range(sm.DD_YEAR_FIRST, sm.DD_YEAR_LAST + 1)
    for level in sm.DD_LEVELS:
        k = keys[level]
        w = v.assign(_k=k)[k.notna()]
        w = w.assign(_live=w["aircraft_id"].map(state["in_force"]).astype(bool))
        for base, _ in sm.DD_BASES:
            b = w[w["_live"]] if base == "in force" else w
            mine = dd.yearly_top_share(b["_k"], b["year"], years, sm.DD_YEAR_MIN)
            a = arch[arch["level id"].eq(level) & arch["base"].eq(base)].reset_index(drop=True)
            _same(a, mine, ["priority year", "aircraft", "its aircraft", "its share", "tied", "read", "above 50 %"])
            assert list(a["largest archetype"]) == [sm._key_word(t, level) if n else ""
                                                    for t, n in zip(mine["largest archetype"], mine["aircraft"])]


def test_family_share(archive, ds, v):
    _, la, sm = _mods()
    arch = sm.family_yearly(ds, v)
    f = sm._level_keys(ds, v)["family_b"]
    w = v.assign(_f=f.eq(sm.FAMILY_LABEL))[f.notna()]
    mine = dd.family_share_by_year(w["_f"], w["year"], range(sm.DD_YEAR_FIRST, sm.DD_YEAR_LAST + 1), sm.DD_YEAR_MIN)
    _same(arch, mine, ["priority year", "aircraft", "F aircraft", "F share"])
    assert list(arch["read, all"]) == list(mine["read"])


def test_consecutive():
    _, _, sm = _mods()
    for ys in ([], [2010], [2012, 2010, 2011], [2008, 2010, 2011, 2013, 2014, 2015]):
        assert sm._consecutive(ys) == dd.consecutive_years(ys)


# ------------------------------------------------------------ condition 2
def test_balance_band_equals_archive_small(archive, ds, v):
    _, la, sm = _mods()
    arch = sm.dd_balance(ds, v, perms=20)
    keys = sm._level_keys(ds, v)
    w0 = v.dropna(subset=["window"])
    shared = np.random.default_rng(42)                     # dominant_design shares one rng over A0c, A1t
    for level in ("A0c", "A1t", "A0", "family_b"):      # the shared rng runs A0c first, then A1t
        k = keys[level].loc[w0.index]
        ww = w0[k.notna()].assign(key=k[k.notna()])
        if level in ("A0c", "A1t"):
            kk = la._archetype_key(w0, level)
            ww = w0[kk.notna()].assign(key=kk[kk.notna()])
            mine = dd.balance_band(ww["key"], ww["window"], la.WINDOW_NAMES, perms=20, rng=shared)
        else:
            mine = dd.balance_band(ww["key"], ww["window"], la.WINDOW_NAMES, perms=20, seed=42)
        a = arch[arch["level"].eq(level)].reset_index(drop=True)
        assert list(a["window"]) == list(mine["window"])
        assert list(a["top archetype"]) == [sm._key_word(t, level) for t in mine["top archetype"]]
        _same(a, mine, ["aircraft", "top share", "top-2 share", "D2", "D2 low", "D2 high", "D2 permutation low",
                        "D2 permutation high", "below band", "condition 1 (> 50 %)"])


def test_balance_full_default_vs_reference(archive, ds, v, reference):
    _, la, sm = _mods()
    t0 = time.time()
    w0 = v.dropna(subset=["window"])
    shared = np.random.default_rng(42)
    parts = []
    for level in ("A0c", "A1t"):
        kk = la._archetype_key(w0, level)
        ww = w0[kk.notna()].assign(key=kk[kk.notna()])
        d = dd.balance_band(ww["key"], ww["window"], la.WINDOW_NAMES, rng=shared)    # perms=200, n=40
        parts.append(d.assign(level=level))
    mine = pd.concat(parts, ignore_index=True)
    ref = pd.read_csv(reference / "la_dominant_design.csv", keep_default_na=False)
    assert list(ref["level"]) == list(mine["level"]) and list(ref["window"]) == list(mine["window"])
    for c in ["aircraft", "top share", "top-2 share", "D2", "D2 low", "D2 high",
              "D2 permutation low", "D2 permutation high"]:
        assert np.allclose(ref[c].astype(float), mine[c].astype(float), **ATOL), c
    assert list(ref["top archetype"]) == list(mine["top archetype"])
    assert list(ref["below band"].astype(str)) == list(mine["below band"].astype(str))
    print("balance full run s:", time.time() - t0)


# ------------------------------------------------------------ condition 3
def _q_inputs(ds, v, a3, la):
    frame = a3.gower_frame(ds)
    fields = a3.gower_fields(ds, pooled=True)
    numeric = {f for f in fields if a3._is_numeric(ds, f)}
    ids = frame["aircraft_id"].to_numpy()
    at = {a: i for i, a in enumerate(ids)}
    Ds = {"subsystem": gower_distance(frame, fields, numeric, subsystem_weights(fields, a3.SUBSYSTEM_OF)),
          "uniform": gower_distance(frame, fields, numeric, uniform_weights(fields))}
    return at, Ds


def _q_mine(v, la, at, Ds, levels, perms):
    parts = []
    for weighting in la.Q_WEIGHTINGS:
        for level in levels:
            key = la._archetype_key(v, level)
            sub = v[key.notna()].dropna(subset=["window"]).copy()
            sub["row"] = sub["aircraft_id"].map(at)
            sub = sub[sub["row"].notna()]
            t = dd.cohesion_band(Ds[weighting], sub["row"].astype(int).to_numpy(), sub["window"].to_numpy(),
                                 la.WINDOW_NAMES, perms=perms)
            t.insert(0, "weighting", weighting)
            t.insert(0, "level", level)
            parts.append(t)
    return pd.concat(parts, ignore_index=True)


def test_cohesion_band_equals_archive_small(archive, ds, v):
    a3, la, sm = _mods()
    at, Ds = _q_inputs(ds, v, a3, la)
    arch = la.dominant_design_q(ds, v, levels=("A0c", "A1t", "A0"), perms=20)
    mine = _q_mine(v, la, at, Ds, ("A0c", "A1t", "A0"), 20)
    assert list(arch.columns) == list(mine.columns)
    _same(arch, mine, list(arch.columns))


def test_cohesion_full_default_vs_reference(archive, ds, v, reference):
    a3, la, sm = _mods()
    t0 = time.time()
    at, Ds = _q_inputs(ds, v, a3, la)
    mine = _q_mine(v, la, at, Ds, ("A0c", "A1t"), 200)
    ref = pd.read_csv(reference / "la_dd_q.csv", keep_default_na=False)
    assert list(ref["level"]) == list(mine["level"]) and list(ref["window"]) == list(mine["window"])
    for c in ["aircraft", "Q", "Q of the earliest windows", "ΔQ", "ΔQ permutation low", "ΔQ permutation high"]:
        assert np.allclose(ref[c].astype(float), mine[c].astype(float), **ATOL), c
    assert list(ref["below band"].astype(str)) == list(mine["below band"].astype(str))
    print("Q full run s:", time.time() - t0)


# ------------------------------------------------------------ verdict rules
def test_verdict_rules(archive, ds, v, reference):
    a3, la, sm = _mods()
    yearly = pd.read_csv(reference / "la_dd_yearly.csv", keep_default_na=False)
    balance = pd.read_csv(reference / "la_dd_balance.csv", keep_default_na=False)
    form = pd.read_csv(reference / "la_dd_form.csv", keep_default_na=False)
    levels = pd.read_csv(reference / "la_dd_levels.csv", keep_default_na=False)
    complete = [w for w in la.WINDOW_NAMES if "partial" not in w]
    main = la.Q_WEIGHTINGS[0]
    arch = sm.dd_levels(yearly, balance, form)
    assert arch.equals(levels) or arch.astype(str).equals(levels.astype(str))
    all_row = arch[arch["condition"].eq("all three in the same period")].iloc[0]
    for level in sm.DD_LEVELS:
        y = yearly[yearly["level id"].eq(level) & yearly["base"].eq(sm.DD_BASES[0][0])]
        m1 = dd.condition1_years(y)
        c2 = set(balance[balance["level"].eq(level) & balance["window"].isin(complete)
                         & balance["below band"].astype(str).eq("True")]["window"])
        c3 = set(form[form["level"].eq(level) & form["window"].isin(complete) & form["weighting"].eq(main)
                      & form["below band"].astype(str).eq("True")]["window"])
        inside = dd.all_three_windows(m1, c2, c3, la.a2.window_of)
        cell = all_row[sm._level_word(level)]
        assert cell == (("met in " + ", ".join(inside)) if inside else "no")
