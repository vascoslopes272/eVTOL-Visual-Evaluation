"""Confidence intervals: Wilson score and percentile bootstraps (science only)."""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional, Tuple

import numpy as np

DRAWS = 2000   # bootstrap draws behind every interval of the document
SEED = 42      # and the seed


def wilson_interval(k: float, n: float, z: float = 1.96) -> Tuple[float, float]:
    """95 % Wilson score interval of the share k/n as (low, high), clamped to [0, 1]; (NaN, NaN) if n is empty.

    Formula: p = k/n; centre = (p + z^2/2n) / (1 + z^2/n);
             half = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n); interval = centre -/+ half.
    z = 1.96.
    Ported from: sm_figures.py:_wilson
    Used in: sm_* class-share figures (error bars)
    """
    if not n or n <= 0:
        return float("nan"), float("nan")
    ph = k / n
    den = 1 + z * z / n
    ctr = (ph + z * z / (2 * n)) / den
    half = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, ctr - half), min(1.0, ctr + half)


def wilson_half_width(k: int, n: int, z: float = 1.96) -> float:
    """Half-width of the 95 % Wilson interval of k/n (NaN if n is empty); NOT clamped to [0, 1].

    Formula: half = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n), p = k/n.
    Ported from: la_figures.py:_wilson_half
    Used in: la_figures (class-share panel, 'Wilson half-width' column of the median-window table)
    """
    if not n:
        return float("nan")
    p = k / n
    d = 1 + z * z / n
    return float(z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d)


def wilson_fpc_interval(x: float, n: float, N: Optional[int], z: float = 1.96) -> Optional[Tuple[float, float]]:
    """95 % Wilson interval of x/n with a finite-population correction on the sample size.

    Formula: effective n_e = n (N - 1) / (N - n) when N > n; a census (N <= n) returns (p, p);
             then as wilson_interval with n_e. N=None means no correction. None on an empty base.
    Ported from: sm_index.py:wilson_fpc
    Used in: the brief's agreement / pairwise-match intervals (sm_pw_ci)
    """
    if not n or n <= 0:
        return None
    ph = x / n
    ne = n
    if N and N > n:
        ne = n * (N - 1) / (N - n)
    elif N and N <= n:
        return (ph, ph)
    den = 1 + z * z / ne
    ctr = (ph + z * z / (2 * ne)) / den
    half = z * math.sqrt(ph * (1 - ph) / ne + z * z / (4 * ne * ne)) / den
    return (max(0.0, ctr - half), min(1.0, ctr + half))


def percentile_interval(draws, low: float = 2.5, high: float = 97.5) -> Tuple[float, float]:
    """Percentile bootstrap interval of a vector of draws (2.5th and 97.5th percentile, numpy linear).

    Ported from: sm_open.py:lag_offsets / doubling_ratio / growth_ratios (np.percentile(d, 2.5/97.5))
    """
    d = np.asarray(draws, dtype=float)
    return float(np.percentile(d, low)), float(np.percentile(d, high))


def bootstrap_median_difference(sample: np.ndarray, reference: np.ndarray, rng: np.random.Generator,
                                draws: int = DRAWS) -> Dict[str, float]:
    """Observed difference of medians and its percentile bootstrap interval, resampling each group.

    Formula: obs = median(sample) - median(reference); each draw resamples both groups with
             replacement (sample first, then reference, from the same generator) and takes the
             difference of medians; interval = 2.5th / 97.5th percentile of the draws.
    Defaults: 2000 draws. ``rng`` is a numpy Generator the caller seeds once with 42 and SHARES across
    all cells, as the document did (the draws depend on the order of calls).
    Ported from: sm_open.py:lag_offsets
    Used in: la_lag_offsets, la_lag_offsets_2016
    """
    obs = float(np.median(sample) - np.median(reference))
    d = np.array([np.median(rng.choice(sample, len(sample), replace=True))
                  - np.median(rng.choice(reference, len(reference), replace=True))
                  for _ in range(draws)])
    lo, hi = percentile_interval(d)
    return {"observed": obs, "low": lo, "high": hi}


def paired_year_bootstrap_ratio(years: np.ndarray, top: np.ndarray, base: np.ndarray,
                                fit: Callable[[np.ndarray, np.ndarray], dict],
                                rng: np.random.Generator, draws: int = DRAWS,
                                numerator: str = "top", min_distinct_years: int = 4,
                                slope_key: str = "slope (log count per year)",
                                doubling_key: str = "doubling time (years)") -> np.ndarray:
    """Draws of a ratio of two doubling times from a paired bootstrap over YEARS.

    Formula: each draw resamples the indices of the window's years with replacement
             (ix = rng.integers(0, n, n)), refits both series on the SAME drawn years with ``fit``
             (a callable (years, counts) -> dict with a slope and a doubling time, empty dict if it
             cannot fit), skips a draw if fewer than 4 distinct years or either fit is empty or
             either slope <= 0, and keeps doubling(top)/doubling(base) (numerator="top") or
             doubling(base)/doubling(top) (numerator="base").
    The interval is then percentile_interval(draws) read only when more than 50 draws survive.
    ``rng`` is a numpy Generator seeded with 42 and shared across windows/series, as the archive.
    Ported from: sm_open.py:doubling_ratio (numerator="top"), sm_open.py:growth_ratios (numerator="base")
    Used in: la_doubling_ratio, la_growth_ratios
    """
    out = []
    n = len(years)
    for _ in range(draws):
        ix = rng.integers(0, n, n)
        if len(np.unique(years[ix])) < min_distinct_years:
            continue
        a, b = fit(years[ix], top[ix]), fit(years[ix], base[ix])
        if not a or not b:
            continue
        if a[slope_key] <= 0 or b[slope_key] <= 0:
            continue
        out.append(a[doubling_key] / b[doubling_key] if numerator == "top"
                   else b[doubling_key] / a[doubling_key])
    return np.array(out)
