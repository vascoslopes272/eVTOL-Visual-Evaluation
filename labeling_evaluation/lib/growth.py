"""Growth of a count series: doubling time, ratio against a baseline, turning point, normalisation, publication lag.

Science only: pure functions of arrays / Series / DataFrames and parameters. No file reading, no config,
no text. Defaults are those of the document (seed 42, 2 000 draws, ...).
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats as _st

#: bootstrap draws and seed behind every interval of the doubling analysis (sm_open.py:DRAWS, SEED)
DRAWS: int = 2000
SEED: int = 42
#: fitted window and its sensitivities (sm_open.py:FIT_WINDOW = (2005, la_tables.LAST_COMPLETE), FIT_SENSITIVITY)
LAST_COMPLETE: int = 2023
FIT_WINDOW: Tuple[int, int] = (2005, LAST_COMPLETE)
FIT_SENSITIVITY: Tuple[Tuple[int, int], ...] = ((2005, 2019), (2010, 2023), (2013, 2023))
#: index base window of the baseline normalisation (la_baseline.py:BASE_YEARS)
BASE_YEARS: Tuple[int, int] = (2005, 2009)
#: candidate break years of the two-segment fit (sm_index.py:_turning_numbers, range(2009, 2021))
TURNING_BREAKS: Tuple[int, ...] = tuple(range(2009, 2021))
#: resamples behind the turning-point robustness (sm_index.py:_turning_numbers)
TURNING_DRAWS: int = 2000


def window_frame(s: pd.Series, lo: int, hi: int) -> Tuple[np.ndarray, np.ndarray]:
    """Years lo..hi (inclusive) and the series reindexed on them, missing years = 0 count.

    Ported from: archive sm_open.py:_window_frame
    """
    yrs = np.arange(lo, hi + 1)
    return yrs, s.reindex(yrs, fill_value=0).to_numpy()


def loglinear_fit(years, counts) -> Dict[str, float]:
    """Least squares of log(count) on year, as a doubling time with a 95 % interval and a curvature test.

    FORMULA: log(y) = a + b·t ;  doubling time = ln 2 / b (NaN if b <= 0) ;
    interval: slope ± t(0.975, n-2)·se, mapped through ln 2 / slope (low slope -> high doubling time) ;
    growth per year % = (exp(b) - 1)·100 ; R² = r² ;
    curvature: quadratic term c of log(y) = a + b·(t-tbar) + c·(t-tbar)², two-sided t test on c with n-3 df (n >= 6).
    Years with a zero count are dropped (log undefined); fewer than 4 usable years returns {}.

    Ported from: archive sm_open.py:_loglin
    Used in: la_doubling_time, la_doubling_ratio
    """
    years = np.asarray(years)
    counts = np.asarray(counts)
    ok = counts > 0
    x, y = years[ok].astype(float), np.log(counts[ok].astype(float))
    n = len(x)
    if n < 4:
        return {}
    r = _st.linregress(x, y)
    tcrit = float(_st.t.ppf(0.975, n - 2))
    lo, hi = r.slope - tcrit * r.stderr, r.slope + tcrit * r.stderr
    out = {"years fitted": int(n), "years dropped (zero count)": int((~ok).sum()),
           "slope (log count per year)": float(r.slope),
           "growth per year %": float((math.exp(r.slope) - 1) * 100),
           "R²": float(r.rvalue ** 2), "p": float(r.pvalue),
           "doubling time (years)": float(math.log(2) / r.slope) if r.slope > 0 else np.nan}
    out["doubling low"] = float(math.log(2) / hi) if hi > 0 else np.nan
    out["doubling high"] = float(math.log(2) / lo) if lo > 0 else np.nan
    if n >= 6:
        X = np.column_stack([np.ones(n), x - x.mean(), (x - x.mean()) ** 2])
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        s2 = float(resid @ resid) / (n - 3)
        se = math.sqrt(s2 * float(np.linalg.pinv(X.T @ X)[2, 2]))
        out["curvature"] = float(beta[2])
        out["curvature p"] = float(2 * _st.t.sf(abs(beta[2] / se), n - 3)) if se > 0 else np.nan
    else:
        out["curvature"], out["curvature p"] = np.nan, np.nan
    return out


def curvature_shape(fit: Dict[str, float]) -> str:
    """Is the straight line on log count a fair description: 'exponential' / 'bends_down' / 'bends_up'.

    RULE: 'exponential' if the curvature p is NaN or >= 0.05; otherwise 'bends_down' if the quadratic
    coefficient is < 0, else 'bends_up'.

    Ported from: archive sm_open.py:_fit_shape (the code only; the archive returns a sentence)
    Used in: la_doubling_time (column 'shape')
    """
    p = fit.get("curvature p", np.nan)
    if not np.isfinite(p) or p >= 0.05:
        return "exponential"
    return "bends_down" if fit["curvature"] < 0 else "bends_up"


def poisson_doubling_time(years, counts, maxiter: int = 100, atol: float = 1e-8) -> Optional[float]:
    """Doubling time from a Poisson GLM with log link (IRLS), a robustness check of the log-linear fit.

    FORMULA: E[count] = exp(a + b·t) fitted by iteratively reweighted least squares (start mu = (y + mean(y))/2,
    working response z = eta + (y - mu)/mu, weights mu, stop when the deviance changes by <= 1e-8);
    doubling time = ln 2 / b if b > 0 else NaN. Returns None if the iteration fails.
    This reproduces statsmodels' GLM(Poisson).fit() (default IRLS) step for step; lib may not import statsmodels.

    Ported from: archive sm_open.py:_poisson_slope
    Used in: la_doubling_time (column 'doubling, Poisson GLM')
    """
    y = np.asarray(counts, dtype=float)
    X = np.column_stack([np.ones(len(y)), np.asarray(years, dtype=float)])
    try:
        mu = (y + y.mean()) / 2.0
        eta = np.log(mu)
        dev_prev = np.inf
        params = None
        for _ in range(maxiter):
            w = mu
            z = eta + (y - mu) / mu
            sw = np.sqrt(w)
            params = np.linalg.pinv(X * sw[:, None]) @ (z * sw)
            eta = X @ params
            mu = np.exp(eta)
            with np.errstate(divide="ignore", invalid="ignore"):
                ylogy = np.where(y > 0, y * np.log(y / mu), 0.0)
            dev = float(2 * np.sum(ylogy - (y - mu)))
            if np.allclose(mu - y, 0):
                break
            if abs(dev - dev_prev) <= atol:
                break
            dev_prev = dev
        b = float(params[1])
    except Exception:
        return None
    return float(math.log(2) / b) if b > 0 else np.nan


def doubling_time_row(years, counts) -> Optional[Dict]:
    """One row of the doubling-time table for one series in one window (numbers, unrounded).

    Returns the loglinear_fit dict plus 'first count', 'last count', 'total', 'poisson doubling' and 'shape'
    (code), or None when the series has fewer than 4 non-zero years. The document rounds: doubling and
    interval to 2 decimals, growth to 1, R² to 3, curvature p to 4, Poisson doubling to 2 (see doubling_time_table).

    Ported from: archive sm_open.py:doubling_time (per-row part)
    Used in: la_doubling_time
    """
    counts = np.asarray(counts)
    fit = loglinear_fit(years, counts)
    if not fit:
        return None
    out = dict(fit)
    out.update({"first count": int(counts[0]), "last count": int(counts[-1]), "total": int(counts.sum()),
                "poisson doubling": poisson_doubling_time(years, counts), "shape": curvature_shape(fit)})
    return out


def doubling_time_table(series: Dict[str, pd.Series],
                        windows: Optional[Sequence[Tuple[int, int]]] = None) -> pd.DataFrame:
    """Doubling time of every named year-indexed count series in every window, rounded as the document prints.

    One row per window then per series. Columns as the archive's table, except 'shape' holds the code of
    curvature_shape and the printable '95 % interval' string is not built.
    Rounding: doubling and interval 2 dp, growth per year % 1 dp, R² 3 dp, curvature p 4 dp.
    Default windows: FIT_WINDOW followed by FIT_SENSITIVITY.

    Ported from: archive sm_open.py:doubling_time
    Used in: la_doubling_time
    """
    wins = list(windows) if windows else [FIT_WINDOW] + list(FIT_SENSITIVITY)
    rows = []
    for lo, hi in wins:
        for name, s in series.items():
            yrs, cnt = window_frame(s, lo, hi)
            r = doubling_time_row(yrs, cnt)
            if r is None:
                continue
            pois = r["poisson doubling"]
            rows.append({
                "series": name, "window": f"{lo}–{hi}",
                "first count": r["first count"], "last count": r["last count"], "total": r["total"],
                "doubling time (years)": round(r["doubling time (years)"], 2),
                "95 % low": round(r["doubling low"], 2),
                "95 % high": round(r["doubling high"], 2),
                "growth per year %": round(r["growth per year %"], 1),
                "R²": round(r["R²"], 3),
                "doubling, Poisson GLM": (round(pois, 2) if pois is not None and np.isfinite(pois) else None),
                "curvature p": (round(r["curvature p"], 4) if np.isfinite(r.get("curvature p", np.nan)) else None),
                "shape": r["shape"], "years fitted": r["years fitted"],
                "primary": (lo, hi) == FIT_WINDOW})
    return pd.DataFrame(rows)


def doubling_ratio_bootstrap(years, top, base, rng: np.random.Generator, draws: int = DRAWS) -> Dict:
    """Ratio of the corpus doubling time to the baseline doubling time with a paired bootstrap over years.

    FORMULA: ratio = T_top / T_base, T = ln 2 / slope of log(count) on year. A draw resamples the INDEX of the
    years with replacement (same indices for both series, so the fits stay paired), is skipped if it holds
    < 4 distinct years, or either fit fails, or either slope <= 0; the interval is the 2.5 / 97.5 percentiles
    of the kept draws (None when <= 50 draws are kept). times faster = 1 / ratio, its interval is
    1/high .. 1/low.
    `rng` is a numpy Generator and is CONSUMED: in the document one np.random.default_rng(42) is shared by every
    (window, corpus series) in turn, so callers must pass the same generator through the loop.

    Returns None if either full-window fit fails, else a dict with unrounded: corpus doubling, baseline
    doubling, ratio, low, high (None if <= 50 draws), draws used.

    Ported from: archive sm_open.py:doubling_ratio (per-row part)
    Used in: la_doubling_ratio
    """
    years, top, base = np.asarray(years), np.asarray(top), np.asarray(base)
    f_top, f_base = loglinear_fit(years, top), loglinear_fit(years, base)
    if not f_top or not f_base:
        return None
    ratio = f_top["doubling time (years)"] / f_base["doubling time (years)"]
    draws_l = []
    n = len(years)
    for _ in range(draws):
        ix = rng.integers(0, n, n)
        if len(np.unique(years[ix])) < 4:
            continue
        a, b = loglinear_fit(years[ix], top[ix]), loglinear_fit(years[ix], base[ix])
        if not a or not b:
            continue
        if a["slope (log count per year)"] <= 0 or b["slope (log count per year)"] <= 0:
            continue
        draws_l.append(a["doubling time (years)"] / b["doubling time (years)"])
    d = np.array(draws_l)
    ok = len(d) > 50
    return {"corpus doubling": f_top["doubling time (years)"], "baseline doubling": f_base["doubling time (years)"],
            "ratio": ratio,
            "low": float(np.percentile(d, 2.5)) if ok else None,
            "high": float(np.percentile(d, 97.5)) if ok else None,
            "draws used": int(len(d))}


def doubling_ratio_table(series: Dict[str, pd.Series], base_name: str, corpus_names: Sequence[str],
                         windows: Optional[Sequence[Tuple[int, int]]] = None,
                         draws: int = DRAWS, seed: int = SEED) -> pd.DataFrame:
    """The doubling ratio of each corpus series against the baseline in every window, rounded as printed.

    One generator np.random.default_rng(seed) is shared across windows and corpus series, in the order
    window -> corpus series (as the document). Rounding: doubling 2 dp, ratio 3 dp, times faster 2 dp,
    ratio interval 3 dp, times-faster interval 2 dp. The printable interval string is not built.

    Ported from: archive sm_open.py:doubling_ratio
    Used in: la_doubling_ratio
    """
    wins = list(windows) if windows else [FIT_WINDOW] + list(FIT_SENSITIVITY)
    rng = np.random.default_rng(seed)
    rows = []
    for lo, hi in wins:
        yrs, base = window_frame(series[base_name], lo, hi)
        for name in corpus_names:
            _, top = window_frame(series[name], lo, hi)
            r = doubling_ratio_bootstrap(yrs, top, base, rng, draws)
            if r is None:
                continue
            lo_, hi_ = r["low"], r["high"]
            rows.append({
                "window": f"{lo}–{hi}", "corpus series": name, "baseline": base_name,
                "corpus doubling (years)": round(r["corpus doubling"], 2),
                "baseline doubling (years)": round(r["baseline doubling"], 2),
                "ratio (corpus / baseline)": round(r["ratio"], 3),
                "times faster": round(1 / r["ratio"], 2),
                "95 % low": round(lo_, 3) if lo_ is not None else None,
                "95 % high": round(hi_, 3) if hi_ is not None else None,
                "times faster low": round(1 / hi_, 2) if hi_ is not None else None,
                "times faster high": round(1 / lo_, 2) if lo_ is not None else None,
                "draws used": r["draws used"],
                "primary": (lo, hi) == FIT_WINDOW})
    return pd.DataFrame(rows)


def growth_ratio_bootstrap(years, top, base, rng: np.random.Generator, draws: int = DRAWS) -> Optional[Dict]:
    """How many times faster a corpus series grows than a baseline, with a paired bootstrap over years.

    FORMULA: times as fast = T_base / T_top, T = ln 2 / slope of log(count) on year (the doubling-time ratio the
    other way up from doubling_ratio_bootstrap). A draw resamples the INDEX of the years with replacement (the same
    indices for both series), is skipped if it holds < 4 distinct years, either fit fails or either slope <= 0;
    each kept draw gives T_base / T_top and the interval is the 2.5 / 97.5 percentiles of those draws themselves
    (not the reciprocal of the percentiles of the other ratio: np.percentile does not commute with 1/x).
    None for an interval when <= 50 draws are kept. `rng` is CONSUMED, one shared generator per table.

    Returns None if either full-window fit fails, else dict(times, low, high, draws used), unrounded.

    Ported from: archive sm_open.py:growth_ratios (per-row part)
    Used in: la_growth_ratios (Figure 1 ii text: 1.32 times as fast as aeronautics, 1.20 to 1.46)
    """
    years, top, base = np.asarray(years), np.asarray(top), np.asarray(base)
    ft, fb = loglinear_fit(years, top), loglinear_fit(years, base)
    if not ft or not fb:
        return None
    ratio = fb["doubling time (years)"] / ft["doubling time (years)"]
    d = []
    for _ in range(draws):
        ix = rng.integers(0, len(years), len(years))
        if len(np.unique(years[ix])) < 4:
            continue
        a, b = loglinear_fit(years[ix], top[ix]), loglinear_fit(years[ix], base[ix])
        if not a or not b or a["slope (log count per year)"] <= 0 or b["slope (log count per year)"] <= 0:
            continue
        d.append(b["doubling time (years)"] / a["doubling time (years)"])
    d = np.array(d)
    ok = len(d) > 50
    return {"times": ratio, "low": float(np.percentile(d, 2.5)) if ok else None,
            "high": float(np.percentile(d, 97.5)) if ok else None, "draws used": int(len(d))}


def growth_ratio_table(series: Dict[str, pd.Series], top_keys: Sequence[str], base_keys: Sequence[str],
                       windows: Optional[Sequence[Tuple[int, int]]] = None, draws: int = DRAWS,
                       seed: int = SEED) -> pd.DataFrame:
    """The growth ratio of every corpus series against every baseline in every window (rounded as printed).

    One generator np.random.default_rng(seed) is shared in the order window -> corpus series -> baseline (as the
    document). Columns: window, eVTOL counted as (the key), against (the key), times as fast (2 dp), low, high
    (2 dp), reading ('faster' if low > 1, 'cannot be told apart' if high >= 1, else 'slower'), primary.
    Default windows: FIT_WINDOW then (2005, 2019).

    Ported from: archive sm_open.py:growth_ratios
    Used in: la_growth_ratios
    """
    wins = list(windows) if windows else [FIT_WINDOW, FIT_SENSITIVITY[0]]
    rng = np.random.default_rng(seed)
    rows = []
    for lo, hi in wins:
        for tk in top_keys:
            yrs, top = window_frame(series[tk], lo, hi)
            for bk in base_keys:
                _, base = window_frame(series[bk], lo, hi)
                r = growth_ratio_bootstrap(yrs, top, base, rng, draws)
                if r is None:
                    continue
                lo_ci, hi_ci = (r["low"], r["high"]) if r["low"] is not None else (np.nan, np.nan)
                rows.append({"window": f"{lo}–{hi}", "eVTOL counted as": tk, "against": bk,
                             "times as fast": round(r["times"], 2),
                             "low": round(lo_ci, 2), "high": round(hi_ci, 2),
                             "reading": ("faster" if lo_ci > 1 else "cannot be told apart" if hi_ci >= 1 else "slower"),
                             "primary": (lo, hi) == FIT_WINDOW})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- turning point
def _two_segment_design(t: np.ndarray, b: float) -> np.ndarray:
    return np.c_[np.ones_like(t), t, (t >= b).astype(float), np.maximum(t - b, 0)]


def two_segment_fit(t, y, b) -> Tuple[float, np.ndarray]:
    """Least squares of y on [1, t, 1(t >= b), max(t - b, 0)]: a level jump and a slope change at year b.

    FORMULA: y = c0 + c1·t + c2·1[t >= b] + c3·max(t - b, 0). Returns (sum of squared errors, coefficients c).

    Ported from: archive sm_index.py:_turning_numbers (inner function `fit`)
    Used in: turning point of eVTOL filing (sm_turn_* numbers)
    """
    t = np.asarray(t, dtype=float)
    X = _two_segment_design(t, b)
    c = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(((X @ c - y) ** 2).sum()), c


def turning_point(t, y, rng: np.random.Generator, breaks: Sequence[int] = TURNING_BREAKS,
                  draws: int = TURNING_DRAWS) -> Dict:
    """Turning point of a log series: the break year with the smallest squared error of the two-segment fit.

    RULE: break b* = argmin over `breaks` of the SSE of two_segment_fit(t, y, b) (first minimum on ties);
    jump factor = exp(c2) at b*; robustness by residual bootstrap: pred + resampled residuals (rng.choice with
    replacement), re-select the break each time, `draws` times. share = fraction of resampled breaks equal to b*;
    lo/hi = 2.5 / 97.5 percentiles of the resampled breaks, truncated to int.
    `rng` is CONSUMED; in the document one default_rng(42) is shared by the three series in the order
    representative patents, unique aircraft, aircraft per 1 000 B64.
    `y` is the LOG of the count (the caller takes the log).

    Returns dict(break, jump, share, lo, hi).

    Ported from: archive sm_index.py:_turning_numbers (inner function `run`)
    Used in: turning point of eVTOL filing (sm_turn_* numbers, Figure 1)
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    b = min(breaks, key=lambda bb: two_segment_fit(t, y, bb)[0])
    _, c = two_segment_fit(t, y, b)
    pred = _two_segment_design(t, b) @ c
    r = y - pred
    bs = np.array([min(breaks, key=lambda bb: two_segment_fit(t, pred + rng.choice(r, len(r)), bb)[0])
                   for _ in range(draws)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"break": b, "jump": float(np.exp(c[2])), "share": float((bs == b).mean()),
            "lo": int(lo), "hi": int(hi)}


# ----------------------------------------------------------------------------- baseline normalisation
def index_to_base(s: pd.Series, base_years: Tuple[int, int] = BASE_YEARS) -> pd.Series:
    """The series rescaled so the mean over the base window is 100.

    FORMULA: index_t = s_t / mean(s over lo..hi) · 100 (NaN everywhere if the base mean is 0 or not finite).

    Ported from: archive la_baseline.py:_index
    Used in: la_filings_per_year (eVTOL index / aviation index), Figure 1
    """
    lo, hi = base_years
    base = s.reindex(range(lo, hi + 1)).mean()
    if not base or not np.isfinite(base):
        return pd.Series(np.nan, index=s.index, dtype=float)
    return s / base * 100.0


def per_thousand(counts: pd.Series, baseline: pd.Series) -> pd.Series:
    """Counts per 1 000 baseline filings, rounded to 2 decimals.

    FORMULA: round(count / baseline · 1000, 2); division by zero gives inf/NaN silently.

    Ported from: archive la_baseline.py:attach (columns 'aircraft per 1 000 B64', 'patents per 1 000 B64')
    Used in: la_filings_per_year
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        return (counts / baseline * 1000).round(2)


def share_multiple(counts: pd.Series, baseline: pd.Series, base_years: Tuple[int, int] = BASE_YEARS) -> pd.Series:
    """Share of a baseline relative to its own base-window level.

    FORMULA: ratio_t = count_t / baseline_t ;  multiple_t = ratio_t / mean(ratio over lo..hi); 1 in the base window.
    `counts` and `baseline` are year-indexed; the base-window mean is taken over the years lo..hi of the ratio.

    Ported from: archive la_baseline.py:multiples (per baseline)
    Used in: la_baseline_multiples
    """
    lo, hi = base_years
    ratio = counts / baseline
    return ratio / ratio.reindex(range(lo, hi + 1)).mean()


def first_year_above(gap: pd.Series) -> Optional[int]:
    """First year from which a gap series stays strictly positive to the end (None if never).

    RULE: smallest y with gap_y > 0 and gap_{y'} > 0 for all later y'. `gap` = eVTOL index - aviation index
    over the complete years.

    Ported from: archive la_baseline.py:readings ('first_above')
    Used in: la_baseline readings / Figure 1 (ii)
    """
    above = gap[gap > 0]
    for y in above.index:
        if bool((gap.loc[y:] > 0).all()):
            return int(y)
    return None


# ----------------------------------------------------------------------------- publication lag
def lag_quantile(lag, q: float = 0.9) -> float:
    """The q-quantile (default 0.9) of the priority-to-publication lag, in years.

    FORMULA: lag = pub_year - priority_year per patent, missing dropped; pandas linear-interpolation quantile.
    `lag` is the already differenced Series (the caller restricts to representative primary patents).

    Ported from: archive la_tables.py:lag_p90 (arithmetic part)
    Used in: la_filings_per_year (completeness of a year)
    """
    return float(pd.Series(lag).dropna().quantile(q))


def year_is_complete(years, p90: float, snapshot: str = "2026-06-08") -> Tuple[np.ndarray, np.ndarray]:
    """Years since each priority year ended, and whether the year is complete.

    RULE: elapsed = (snapshot - 31 Dec of year) in days / 365.25; complete when elapsed >= p90 (the 90th-percentile
    lag). Returns (elapsed rounded to 1 decimal, complete). Note the flag uses the UNROUNDED elapsed.

    Ported from: archive la_tables.py:filings_per_year (completeness part)
    Used in: la_filings_per_year (columns 'years since year end', 'complete')
    """
    snap = pd.Timestamp(snapshot)
    elapsed = (snap - pd.to_datetime([f"{y}-12-31" for y in years])).days / 365.25
    return np.round(elapsed, 1), np.asarray(elapsed >= p90)


def visible_share(lags, years_after: int, snapshot_fraction: float) -> float:
    """The part of a priority year's aircraft that the snapshot can already see, from the lag distribution
    of a complete reference period.

    FORMULA: with k = snapshot year - priority year and f = the part of the snapshot year elapsed (day of year / 365):
    P(lag <= k - 1) + f * P(lag = k), the probabilities read on `lags` (whole years from priority to publication).
    NaN on an empty `lags`.

    Ported from: archive sm_open.py:region_years (inner function `vis`)
    Used in: la_region_years ('visible at the snapshot'; the 87 % to 92 % of the 2023 aircraft seen)
    """
    arr = np.asarray(lags, dtype=float)
    if not len(arr):
        return float("nan")
    return float(np.mean(arr <= years_after - 1) + snapshot_fraction * np.mean(arr == years_after))
