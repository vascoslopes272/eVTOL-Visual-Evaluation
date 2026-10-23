"""Diversity of a categorical distribution: effective number, Hill numbers, rarefaction,
Chao1 / jackknife richness estimators, and the archetype discovery curve.

Pure functions: arrays / Series in, numbers / arrays / frames out.
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

#: orderings drawn to break the ties inside a priority year (discovery curve)
ORDERS = 1000
#: the tail the flattening is read on: new archetypes over the last this-many aircraft
TAIL = 100
#: full random orders drawn for the band of the last-tail count (discovery_tail_band; supervisor review 2)
SHUFFLES = 10000


def effective_number(series: pd.Series) -> float:
    """Effective number of answers (Hill number of order 1) over the non-null values.

    D1 = exp(H),  H = -Σ_i p_i ln p_i,  p_i = share of answer i among non-null values.
    NaN when there is no non-null value.

    Ported from: archive/.../dataset_facts/metrics.py:effective_number
    Used in: la_archetype_levels / la_discovery_estimators ("effective number" columns), Part A spread.
    """
    p = series.dropna().value_counts(normalize=True)
    if p.empty:
        return float("nan")
    return float(np.exp(-(p * np.log(p)).sum()))


def hill_numbers(labels: pd.Series, n: int = 40, draws: int = 1000, seed: int = 42) -> Dict[str, float]:
    """Rarefied Hill numbers of orders 0, 1, 2 at sample size n (mean and 95 % band over draws).

    Each draw takes min(n, N) labels without replacement; with p_i the shares in the draw:
      D0 = number of distinct labels,  D1 = exp(-Σ p_i ln p_i),  D2 = 1 / Σ p_i²
    The result is the mean of the draws and their 2.5 / 97.5 percentiles, rounded to 2 decimals.
    Labels are cast to str; nulls dropped. A fresh np.random.default_rng(seed) per call.

    Parameters: n=40, draws=1000, seed=42 (the document also calls it with draws=300 and draws=40).
    Ported from: archive/.../dataset_facts/la_tables.py:hill_numbers
    Used in: la_hill_by_window, la_dominant_design, la_dd_balance.
    """
    x = labels.dropna().astype(str).to_numpy()
    rng = np.random.default_rng(seed)
    out = {0: [], 1: [], 2: []}
    for _ in range(draws):
        s = rng.choice(x, size=min(n, len(x)), replace=False)
        _, cnt = np.unique(s, return_counts=True)
        p = cnt / cnt.sum()
        out[0].append(len(cnt))
        out[1].append(float(np.exp(-(p * np.log(p)).sum())))
        out[2].append(float(1 / (p ** 2).sum()))
    res = {"aircraft": int(len(x)), "sample": int(min(n, len(x)))}
    for q in (0, 1, 2):
        a = np.array(out[q])
        res[f"D{q}"] = round(float(a.mean()), 2)
        res[f"D{q} low"] = round(float(np.percentile(a, 2.5)), 2)
        res[f"D{q} high"] = round(float(np.percentile(a, 97.5)), 2)
    return res


def hill_by_window(frame: pd.DataFrame, window_names: Sequence[str], n: int = 40,
                   levels: Sequence[Tuple[str, str]] = (("A0 class", "topType"),
                                                        ("A0c class × propulsive-unit bin", "archetype")),
                   min_aircraft: int = 10, window_col: str = "window") -> pd.DataFrame:
    """Rarefied Hill numbers per window for each (level name, column) pair.

    For each level and window with at least `min_aircraft` aircraft that carry both a window and a
    value: hill_numbers(values, n=n) (draws=1000, seed=42).

    Parameters: n=40, min_aircraft=10; `levels` as the document used them.
    Ported from: archive/.../dataset_facts/la_tables.py:hill_by_window
    Used in: la_hill_by_window.
    """
    rows = []
    for level, col in levels:
        w = frame.dropna(subset=[window_col, col])
        for name in window_names:
            sub = w[w[window_col].eq(name)]
            if len(sub) < min_aircraft:
                continue
            r = hill_numbers(sub[col], n=n)
            rows.append({"level": level, "window": name, **r})
    return pd.DataFrame(rows)


def rarefaction_curve(counts: np.ndarray, ns: np.ndarray) -> np.ndarray:
    """Expected distinct types in a random subsample of size n drawn without replacement.

    E[S_n] = S - Σ_i C(N - n_i, n) / C(N, n),  S = number of types, N = Σ n_i
    (binomials via log-gamma; terms with N - n_i < n are 0; E[S_0] = 0).

    Ported from: archive/.../dataset_facts/sm_open.py:_rarefaction
    Used in: la_discovery_curve ("archetypes (random order)"), la_discovery_estimators.
    """
    from scipy.special import gammaln

    N = int(counts.sum())
    out = []
    for n in ns:
        if n <= 0:
            out.append(0.0)
            continue
        terms = np.exp(gammaln(N - counts + 1) - gammaln(N - counts - n + 1)
                       - (gammaln(N + 1) - gammaln(N - n + 1)))
        terms = np.where((N - counts) >= n, terms, 0.0)
        out.append(float(len(counts) - terms.sum()))
    return np.array(out)


def chao1_jackknife(counts: np.ndarray) -> Dict[str, float]:
    """Bias-corrected Chao1 with its log-normal 95 % interval, first/second-order jackknives, coverage.

    S = types seen, N = individuals, f1 / f2 = types seen once / twice.
      Chao1  = S + f1 (f1 - 1) / (2 (f2 + 1))
      var    = a/2 + b + c  (0 if f1 = 0), a = f1(f1-1)/(2(f2+1)), b = f1(2f1-1)²/(4(f2+1)²),
               c = f1² f2 (f1-1)² / (4 (f2+1)⁴)
      unseen = Chao1 - S; k = exp(1.96 sqrt(ln(1 + var/unseen²)));  interval S + unseen/k .. S + unseen k
               (S .. Chao1 when unseen <= 0 or var <= 0)
      jackknife 1 = S + f1 (N-1)/N
      jackknife 2 = S + f1 (2N-3)/N - f2 (N-2)² / (N (N-1))   (S when N <= 2)
      coverage (Good–Turing) = 1 - f1/N

    Parameter: counts = abundance of each observed type.
    Ported from: archive/.../dataset_facts/sm_open.py:_chao1
    Used in: la_discovery_estimators.
    """
    S = int(len(counts))
    N = int(counts.sum())
    f1 = int((counts == 1).sum())
    f2 = int((counts == 2).sum())
    chao = S + f1 * (f1 - 1) / (2.0 * (f2 + 1))
    unseen = chao - S
    a = f1 * (f1 - 1) / (2.0 * (f2 + 1))
    b = f1 * (2 * f1 - 1) ** 2 / (4.0 * (f2 + 1) ** 2)
    c = f1 ** 2 * f2 * (f1 - 1) ** 2 / (4.0 * (f2 + 1) ** 4)
    var = a / 2 + b + c if f1 else 0.0
    if unseen > 0 and var > 0:
        k = math.exp(1.96 * math.sqrt(math.log(1 + var / unseen ** 2)))
        lo, hi = S + unseen / k, S + unseen * k
    else:
        lo, hi = float(S), float(chao)
    jack1 = S + f1 * (N - 1) / N
    jack2 = (S + f1 * (2 * N - 3) / N - f2 * (N - 2) ** 2 / (N * (N - 1))) if N > 2 else float(S)
    return {"observed": S, "aircraft": N, "singletons f1": f1, "doubletons f2": f2,
            "Chao1": chao, "Chao1 low": lo, "Chao1 high": hi,
            "jackknife 1": jack1, "jackknife 2": jack2,
            "coverage (Good–Turing)": 1 - f1 / N if N else np.nan}


def discovery_curve(years: np.ndarray, keys, orders: int = ORDERS, seed: int = 42,
                    rng: Optional[np.random.Generator] = None) -> pd.DataFrame:
    """Distinct archetypes seen against aircraft seen, in priority order, for ONE level.

    Aircraft are ordered by priority year, ties inside a year broken by a random shuffle
    (np.lexsort((rng.random(N), years)), one draw per ordering); the running number of distinct
    keys is counted. Mean over `orders` orderings, with 2.5 / 97.5 percentiles; the rarefaction
    expectation (random order) is added. All rounded to 2 decimals as the document prints them.

    `keys` and `years` are the aircraft that have a key (no nulls). To reproduce the document the
    SAME generator must be passed to the levels in sequence (the archive makes one
    np.random.default_rng(42) and uses it for A0, A0c, A1t in that order): pass `rng`, or use
    :func:`discovery_curve_levels`.

    Parameters: orders=1000, seed=42.
    Ported from: archive/.../dataset_facts/sm_open.py:discovery_curve (computation only)
    Used in: la_discovery_curve; its last 100 steps feed la_discovery_estimators.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    years = np.asarray(years)
    codes = pd.factorize(pd.Series(keys))[0]
    N, S = len(codes), int(codes.max() + 1)
    curves = np.zeros((orders, N), dtype=float)
    for d in range(orders):
        order = np.lexsort((rng.random(N), years))
        seen = np.zeros(S, dtype=bool)
        c = 0
        for i, ix in enumerate(order):
            if not seen[codes[ix]]:
                seen[codes[ix]] = True
                c += 1
            curves[d, i] = c
    mean = curves.mean(axis=0)
    lo = np.percentile(curves, 2.5, axis=0)
    hi = np.percentile(curves, 97.5, axis=0)
    counts = np.bincount(codes)
    ns = np.arange(1, N + 1)
    rar = rarefaction_curve(counts, ns)
    ysort = np.sort(years)
    return pd.DataFrame({"aircraft": ns.astype(int),
                         "priority year reached": ysort.astype(int),
                         "archetypes (date order)": [round(float(x), 2) for x in mean],
                         "2.5 %": [round(float(x), 2) for x in lo],
                         "97.5 %": [round(float(x), 2) for x in hi],
                         "archetypes (random order)": [round(float(x), 2) for x in rar]})


def discovery_curve_levels(levels: Dict[str, Tuple[np.ndarray, object]], orders: int = ORDERS,
                           seed: int = 42) -> pd.DataFrame:
    """discovery_curve for several levels in order, sharing ONE generator seeded with `seed`.

    `levels` maps level name -> (years, keys) of the aircraft that have a key at that level.
    Adds a `level` column first.

    Ported from: archive/.../dataset_facts/sm_open.py:discovery_curve
    Used in: la_discovery_curve.
    """
    rng = np.random.default_rng(seed)
    parts = []
    for level, (years, keys) in levels.items():
        c = discovery_curve(years, keys, orders=orders, rng=rng)
        c.insert(0, "level", level)
        parts.append(c)
    return pd.concat(parts, ignore_index=True)


def discovery_tail(date_order: np.ndarray, random_order: np.ndarray, tail: int = TAIL) -> Dict[str, float]:
    """Flattening of a discovery curve read on its tail.

    With y = mean date-order curve, r = random-order curve, n = len(y), i0 = max(0, n-1-tail),
    i1 = max(0, n-1-2 tail):
      last = y[-1] - y[i0];  prev = y[i0] - y[i1];  rar_last = r[-1] - r[i0];  half = y[n//2 - 1]

    Parameter: tail=100.
    Ported from: archive/.../dataset_facts/sm_open.py:discovery_estimators
    Used in: la_discovery_estimators (new in the last 100 / before that / random order).
    """
    y = np.asarray(date_order)
    r = np.asarray(random_order)
    n = len(y)
    last = float(y[-1] - y[max(0, n - 1 - tail)])
    prev = float(y[max(0, n - 1 - tail)] - y[max(0, n - 1 - 2 * tail)])
    rar_last = float(r[-1] - r[max(0, n - 1 - tail)])
    half = int(n // 2)
    return {"last": last, "prev": prev, "rar_last": rar_last, "half": float(y[half - 1])}


def _new_in_tail(codes: np.ndarray, order: np.ndarray, tail: int) -> int:
    """Archetypes whose first aircraft in `order` is among the last `tail` (none in the first N - tail)."""
    _, first = np.unique(codes[order], return_index=True)
    return int((first >= len(codes) - tail).sum())


def discovery_tail_band(levels: Dict[str, Tuple[np.ndarray, object]], tail: int = TAIL, orders: int = ORDERS,
                        shuffles: int = SHUFFLES, seed: int = 42) -> pd.DataFrame:
    """Significance band of the new archetypes in the last `tail` aircraft (supervisor review 2, 2026-10).

    Date order: the `orders` tie-breaking orderings of :func:`discovery_curve_levels`, redrawn from the SAME generator stream
    (np.random.default_rng(seed), levels in the order given, one rng.random(N) per ordering), so the mean is the curve's
    "new in the last 100". The levels must be passed as to discovery_curve_levels (A0, A0c, A1t) for the stream to match.
    Random order: `shuffles` full permutations per level from a second np.random.default_rng(seed), levels in the order given.
    The random mean printed is the exact expectation (rarefaction_curve at N and N - tail), as la_discovery_estimators;
    the shuffle mean is returned beside it as the check. Two one-sided p:
      p (share >= date mean)   = share of shuffles with count >= mean date-order count
      p (whole counts, ...)    = mean over the date orderings j of the share of shuffles with count >= d_j

    Parameters: tail=100, orders=1000, shuffles=10000, seed=42.
    Used in: q6_discovery_last100_band (notebook 50).
    """
    rng_d = np.random.default_rng(seed)
    rng_r = np.random.default_rng(seed)
    rows = []
    for level, (years, keys) in levels.items():
        years = np.asarray(years)
        codes = pd.factorize(pd.Series(keys))[0]
        N = len(codes)
        d = np.array([_new_in_tail(codes, np.lexsort((rng_d.random(N), years)), tail) for _ in range(orders)])
        r = np.array([_new_in_tail(codes, rng_r.permutation(N), tail) for _ in range(shuffles)])
        rar = rarefaction_curve(np.bincount(codes), np.array([N - tail, N]))
        r_sorted = np.sort(r)
        ge = 1.0 - np.searchsorted(r_sorted, d, side="left") / shuffles        # share of shuffles >= d_j, per date ordering
        rows.append({"level": level, "designs": N, "date mean": float(d.mean()),
                     "date 2.5 %": float(np.percentile(d, 2.5)), "date 97.5 %": float(np.percentile(d, 97.5)),
                     "random mean (exact)": float(rar[1] - rar[0]), "random mean (shuffles)": float(r.mean()),
                     "random 95th": float(np.percentile(r, 95)), "random 99th": float(np.percentile(r, 99)), "random max": int(r.max()),
                     "p (share >= date mean)": float((r >= d.mean() - 1e-12).mean()), "p (whole counts)": float(ge.mean()),
                     "orders": orders, "shuffles": shuffles, "seed": seed})
    return pd.DataFrame(rows)


def discovery_verdict_code(est: Dict[str, float], last: float, rar_last: float) -> str:
    """Rule behind the discovery verdict sentence: 'filling up', 'still opening' or 'slowing, not closed'.

    found = observed / Chao1; cov = Good–Turing coverage.
      filling up  if found >= 0.95 and cov >= 0.99 and last <= max(1, rar_last)
      still opening  elif last >= rar_last and found < 0.95
      slowing, not closed  otherwise

    Ported from: archive/.../dataset_facts/sm_open.py:_discovery_verdict (rule only, no wording)
    Used in: la_discovery_estimators ("verdict").
    """
    found = est["observed"] / est["Chao1"]
    cov = est["coverage (Good–Turing)"]
    if found >= 0.95 and cov >= 0.99 and last <= max(1.0, rar_last):
        return "filling up"
    if last >= rar_last and found < 0.95:
        return "still opening"
    return "slowing, not closed"
