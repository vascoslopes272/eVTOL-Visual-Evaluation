"""The three dominant-design conditions (counts, balance, form) and the rules that combine them.

Condition 1: one archetype above 50 % of a priority year's aircraft, two consecutive years.
Condition 2: rarefied ²D of a window below a permutation band (archetypes shuffled across windows).
Condition 3: Rao's Q of the Gower distance of a window, below the earliest windows by more than a
             permutation band (aircraft shuffled across windows).
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np
import pandas as pd

from .diversity import hill_numbers


# --------------------------------------------------------------------------- condition 1
def yearly_top_share(keys: pd.Series, years: pd.Series, year_range: Iterable[int],
                     min_cell: int) -> pd.DataFrame:
    """Largest archetype's share per priority year, with ties and the minimum-cell rule.

    For each year y: n = aircraft of the year; k1 = count of the most common key (first of
    value_counts, i.e. count descending, ties in order of first appearance); share = k1 / n
    rounded to 4 decimals; tied = more than one key has count k1; read = n >= min_cell;
    above 50 % = read and k1 / n > 0.5. A year with no aircraft has top "", k1 0, share NaN.

    Parameters: keys, years aligned (keys with no archetype already removed); year_range
    (document: 2008..2023); min_cell (document: TREND_MIN = 20).
    Ported from: archive/.../dataset_facts/sm_open.py:dd_yearly and family_yearly (share part)
    Used in: la_dd_yearly, la_family_dd.
    """
    rows = []
    for y in year_range:
        sub = keys[years.eq(y)]
        n = int(len(sub))
        if n:
            vc = sub.value_counts()
            top, k1 = str(vc.index[0]), int(vc.iloc[0])
            tied = int((vc == k1).sum()) > 1
        else:
            top, k1, tied = "", 0, False
        rows.append({"priority year": y, "aircraft": n, "largest archetype": top,
                     "its aircraft": k1, "its share": round(k1 / n, 4) if n else np.nan,
                     "tied": tied, "read": n >= min_cell,
                     "above 50 %": bool(n >= min_cell and k1 / n > 0.5)})
    return pd.DataFrame(rows)


def family_share_by_year(is_family: pd.Series, years: pd.Series, year_range: Iterable[int],
                         min_cell: int) -> pd.DataFrame:
    """Share of each priority year's aircraft that carry one given archetype (the family F).

    n = aircraft of the year; F aircraft = Σ is_family; F share = mean(is_family) rounded to 4
    decimals (NaN if n = 0); read = n >= min_cell.

    Ported from: archive/.../dataset_facts/sm_open.py:family_yearly (the "all" base)
    Used in: la_family_dd.
    """
    rows = []
    for y in year_range:
        s = is_family[years.eq(y)]
        n = len(s)
        rows.append({"priority year": y, "aircraft": n, "F aircraft": int(s.sum()),
                     "F share": round(float(s.mean()), 4) if n else np.nan,
                     "read": n >= min_cell})
    return pd.DataFrame(rows)


def consecutive_years(years: List[int]) -> List[Tuple[int, int]]:
    """Pairs (a, b) of consecutive entries of the sorted years with b = a + 1.

    Ported from: archive/.../dataset_facts/sm_open.py:_consecutive
    Used in: la_dd_levels (condition 1: two consecutive years above 50 %).
    """
    ys = sorted(years)
    return [(a, b) for a, b in zip(ys[:-1], ys[1:]) if b == a + 1]


def condition1_years(yearly: pd.DataFrame) -> Set[int]:
    """Years in which condition 1 is met: those in a pair of consecutive read years above 50 %.

    Takes the output of yearly_top_share (one level, one base). The set is empty when no two
    consecutive years are both read and above 50 %.

    Ported from: archive/.../dataset_facts/sm_open.py:dd_levels (condition 1 branch)
    Used in: la_dd_levels.
    """
    b = yearly[yearly["read"].astype(bool)]
    over = b[b["above 50 %"].astype(bool)]
    pairs = consecutive_years(over["priority year"].astype(int).tolist())
    return {x for p in pairs for x in p}


def all_three_windows(c1_years: Set[int], c2_windows: Set[str], c3_windows: Set[str],
                      window_of: Callable[[int], str]) -> List[str]:
    """Windows where all three conditions hold: 2 and 3 are met there and condition 1's years all lie in it.

    inside = [w in c2 ∩ c3 : c1_years non-empty and window_of(y) == w for every y in c1_years]

    Ported from: archive/.../dataset_facts/sm_open.py:dd_levels ("all three in the same period")
    Used in: la_dd_levels (last row).
    """
    both = c2_windows & c3_windows
    return [w for w in both if c1_years and all(window_of(y) == w for y in c1_years)]


# --------------------------------------------------------------------------- condition 2
def balance_band(keys: Sequence, windows: Sequence, window_names: Sequence[str], n: int = 40,
                 perms: int = 1000, seed: int = 42, rng: Optional[np.random.Generator] = None,
                 min_aircraft: int = 10, obs_draws: int = 1000, perm_draws: int = 40) -> pd.DataFrame:
    """Condition 2 for ONE level: rarefied ²D per window against a permutation band.

    Observed: for each window with >= min_aircraft aircraft, hill_numbers(keys, n, draws=1000) gives
    D2 = 1 / Σ p_i² averaged over rarefied draws of size n (and its 95 % band), plus the top and top-2
    archetype shares (rounded 3). Band: `perms` times, the keys are shuffled across all windows
    (rng.permutation, window sizes kept); for each window, in order, ²D of the shuffled keys of that
    window is computed with hill_numbers(draws=40, seed=int(rng.integers(1e9))). The band is the 2.5 and
    97.5 percentiles of those ²D (rounded 2). below band = D2 < permutation low; condition 1
    (> 50 %) = top share > 0.5.

    RNG: ONE generator, order of calls per permutation: permutation(keys), then one integers(1e9)
    per observed window in window_names order. The archive seeds one generator for the first two
    levels (A0c then A1t, shared) and a fresh one per other level: pass `rng` to share, or `seed`.

    Parameters: n=40, perms=1000, seed=42, min_aircraft=10, obs_draws=1000, perm_draws=40.
    Ported from: archive/.../dataset_facts/la_tables.py:dominant_design (one level) and
                 sm_open.py:dd_balance (levels C and F)
    Used in: la_dominant_design, la_dd_balance.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    ww = pd.DataFrame({"key": np.asarray(keys, dtype=object), "window": np.asarray(windows, dtype=object)})
    obs = {}
    for name in window_names:
        sub = ww[ww["window"].eq(name)]
        if len(sub) < min_aircraft:
            continue
        h = hill_numbers(sub["key"], n=n, draws=obs_draws)
        top = sub["key"].value_counts(normalize=True)
        obs[name] = {"window": name, "aircraft": int(len(sub)), "top archetype": top.index[0],
                     "top share": round(float(top.iloc[0]), 3),
                     "top-2 share": round(float(top.iloc[:2].sum()), 3),
                     "D2": h["D2"], "D2 low": h["D2 low"], "D2 high": h["D2 high"]}
    band = {name: [] for name in obs}
    pool = ww["key"].to_numpy()
    for _ in range(perms):
        shuffled = rng.permutation(pool)
        for name in obs:
            mask = ww["window"].eq(name).to_numpy()
            band[name].append(hill_numbers(pd.Series(shuffled[mask]), n=n, draws=perm_draws,
                                           seed=int(rng.integers(1e9)))["D2"])
    rows = []
    for name, r in obs.items():
        b = np.array(band[name])
        r["D2 permutation low"] = round(float(np.percentile(b, 2.5)), 2)
        r["D2 permutation high"] = round(float(np.percentile(b, 97.5)), 2)
        r["below band"] = bool(r["D2"] < r["D2 permutation low"])
        r["condition 1 (> 50 %)"] = bool(r["top share"] > 0.5)
        rows.append(r)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- condition 3
def mean_pairwise_distance(D: np.ndarray, idx: np.ndarray) -> float:
    """Rao's quadratic entropy Q of a set: mean of D over all ordered pairs (diagonal included), NaN-aware.

    Q = nanmean(D[idx, idx]); NaN when idx is empty. Note the diagonal zeros are in the mean
    (as in the archive), which lowers Q by roughly 1/n.

    Ported from: archive/.../dataset_facts/la_tables.py:dominant_design_q (inner q)
    Used in: la_dd_q.
    """
    return float(np.nanmean(D[np.ix_(idx, idx)])) if len(idx) else float("nan")


def cohesion_band(D: np.ndarray, rows: np.ndarray, windows: Sequence, window_names: Sequence[str],
                  baseline: int = 2, perms: int = 1000, seed: int = 42,
                  rng: Optional[np.random.Generator] = None, min_aircraft: int = 10) -> pd.DataFrame:
    """Condition 3 for ONE level and ONE weighting: Q per window against the earliest windows and a permutation band.

    Q_w = mean distance over ordered pairs of the aircraft of window w (mean_pairwise_distance);
    reference = mean Q over the first `baseline` windows (those with >= min_aircraft); ΔQ = Q_w - reference.
    Band: `perms` times shuffle the aircraft (rng.permutation of `rows`), cut the shuffled list into
    consecutive blocks of the window sizes (in window_names order; blocks of < min_aircraft give NaN),
    recompute Q per block, ΔQ* = Q*_w - mean of the baseline blocks' Q*; band = percentiles 2.5 / 97.5
    of ΔQ*. below band = ΔQ < low.

    Parameters: rows = row index into D of each aircraft; windows = window of each aircraft (aligned);
    baseline=2, perms=1000, seed=42, min_aircraft=10. Rounded to 4 decimals. The archive creates a
    fresh default_rng(seed) for every (weighting, level): pass `rng` only to share one.
    Ported from: archive/.../dataset_facts/la_tables.py:dominant_design_q (one weighting, one level)
    Used in: la_dd_q, la_dd_form.
    """
    rows = np.asarray(rows, dtype=int)
    win = pd.Series(np.asarray(windows, dtype=object))
    per = {w: rows[win.eq(w).to_numpy()] for w in window_names}
    obs = {w: mean_pairwise_distance(D, r) for w, r in per.items() if len(r) >= min_aircraft}
    base_windows = list(window_names)[:baseline]
    ref = float(np.mean([obs[w] for w in base_windows if w in obs]))
    if rng is None:
        rng = np.random.default_rng(seed)
    pool = rows
    band = {w: [] for w in obs}
    for _ in range(perms):
        shuffled = rng.permutation(pool)
        cut, drawn = 0, {}
        for w in window_names:
            take = len(per[w])
            drawn[w] = mean_pairwise_distance(D, shuffled[cut:cut + take]) if take >= min_aircraft else float("nan")
            cut += take
        r0 = float(np.mean([drawn[w] for w in base_windows if w in obs]))
        for w in obs:
            band[w].append(drawn[w] - r0)
    out = []
    for w in window_names:
        if w not in obs:
            continue
        arr = np.array(band[w])
        lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
        out.append({"window": w, "aircraft": int(len(per[w])), "Q": round(obs[w], 4),
                    "Q of the earliest windows": round(ref, 4),
                    "ΔQ": round(obs[w] - ref, 4),
                    "ΔQ permutation low": round(lo, 4), "ΔQ permutation high": round(hi, 4),
                    "below band": bool(obs[w] - ref < lo)})
    return pd.DataFrame(out)
