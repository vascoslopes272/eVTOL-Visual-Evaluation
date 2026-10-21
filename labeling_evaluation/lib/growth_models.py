"""Three models of a growth series, compared by AIC and BIC (supervisor review 2, 2026-10; Figure 4.2, q1_growth_rates).

Each model is fitted to y = ln(count) on the priority year t, by least squares (Gaussian errors on the log scale):
  (a) step:     two lines with a free level step at the break b:  y = c0 + c1 (t - b) + c2 1[t >= b] + c3 max(t - b, 0)
  (b) hinge:    two lines that meet at b (slope change only):      y = c0 + c1 (t - b) + c3 max(t - b, 0)
  (c) logistic: an S-curve of the count, fitted on its log:        y = ln K - ln(1 + exp(-r (t - t0)))
The break of (a) and (b) is the series' own: every integer year that leaves at least MIN_SEGMENT years on each side is tried and the
smallest squared error kept (first minimum on ties). The break counts as a parameter, and so does the error variance:
k = 6 (a), 5 (b), 4 (c). AIC = n ln(SSE / n) + 2k, BIC = n ln(SSE / n) + k ln n (constants dropped, the same for every model);
AICc = AIC + 2k(k + 1) / (n - k - 1) is printed beside them for the small n.

Intervals: residual bootstrap of each model, DRAWS times (pred + residuals drawn with replacement, the break searched again every
time), one numpy Generator per series and model seeded with the caller's seed; 2.5 and 97.5 percentiles.

Pure functions: arrays in, dicts / frames out. Used in: viz/thesis_q1.py (growth_models), viz/thesis_v2_part1.py (fig_growth_rates_ts).
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

#: years each segment of models (a) and (b) keeps at least (a line through 2 points has no residual)
MIN_SEGMENT = 3
#: bootstrap resamples behind every interval of this module
DRAWS = 1000
#: a model wins "clearly" when it is lowest on AIC AND BIC by at least this much (Burnham & Anderson 2002: > 10, essentially no
#: support for the other model)
CLEAR_DELTA = 10.0
MODELS = {"a": "two lines, free level step", "b": "two lines meeting at the break (slope change only)", "c": "logistic S-curve"}
N_PARAMS = {"a": 6, "b": 5, "c": 4}


def _design(t: np.ndarray, b: int, step: bool) -> np.ndarray:
    cols = [np.ones_like(t), t - b]
    if step:
        cols.append((t >= b).astype(float))
    cols.append(np.maximum(t - b, 0.0))
    return np.column_stack(cols)


def candidate_breaks(t: np.ndarray, min_segment: int = MIN_SEGMENT) -> range:
    """Every integer year with at least ``min_segment`` years before it and at least ``min_segment`` from it on (the break opens the second line)."""
    return range(int(t[0]) + min_segment, int(t[-1]) - min_segment + 2)


def fit_piecewise(t, y, step: bool, min_segment: int = MIN_SEGMENT) -> Dict:
    """Model (a) (``step=True``) or (b): the break with the smallest SSE and its coefficients.

    Returns dict(break, sse, pred, pre slope, post slope, step) where the slopes are per year on the log scale and step = exp(c2)
    (1.0 for model b). Coefficients are centred on the break, so c0 is the pre-break line's value at b."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    best = None
    for b in candidate_breaks(t, min_segment):
        X = _design(t, b, step)
        c = np.linalg.lstsq(X, y, rcond=None)[0]
        sse = float(((X @ c - y) ** 2).sum())
        if best is None or sse < best[0]:
            best = (sse, b, c, X @ c)
    sse, b, c, pred = best
    return {"break": int(b), "sse": sse, "pred": pred, "coef": c, "pre slope": float(c[1]), "post slope": float(c[1] + c[-1]),
            "step": float(np.exp(c[2])) if step else 1.0}


def piecewise_curve(fit: Dict, x, step: bool, side: Optional[str] = None) -> np.ndarray:
    """ln count of a fitted model (a) or (b) at the years ``x`` (any real values). ``side`` = 'pre' or 'post' evaluates that segment's
    line at every x (to draw each segment up to the half year before the break without the step showing as a vertical line)."""
    x = np.asarray(x, float)
    X = _design(x, fit["break"], step)
    if side is not None:
        on = 1.0 if side == "post" else 0.0
        if step:
            X[:, 2] = on
        X[:, -1] = on * (x - fit["break"])
    return X @ fit["coef"]


def _logistic(t, ln_k, r, t0):
    return ln_k - np.logaddexp(0.0, -r * (t - t0))


def fit_logistic(t, y) -> Dict:
    """Model (c): ln K, r, t0 by non-linear least squares (scipy curve_fit, start: K at the highest count, r = 0.5, t0 = the year
    nearest half the highest count). Returns dict(sse, pred, ln K, r, t0, K)."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    p0 = [y.max() + 0.1, 0.5, float(t[np.argmin(np.abs(y - (y.max() - np.log(2))))])]
    c, _ = curve_fit(_logistic, t, y, p0=p0, maxfev=20000)
    pred = _logistic(t, *c)
    return {"sse": float(((pred - y) ** 2).sum()), "pred": pred, "ln K": float(c[0]), "r": float(c[1]), "t0": float(c[2]),
            "K": float(np.exp(c[0])), "coef": c}


def logistic_curve(fit: Dict, x) -> np.ndarray:
    return _logistic(np.asarray(x, float), *fit["coef"])


def information_criteria(sse: float, n: int, k: int) -> Dict[str, float]:
    ll = n * np.log(sse / n)
    aic = ll + 2 * k
    return {"AIC": float(aic), "BIC": float(ll + k * np.log(n)), "AICc": float(aic + 2 * k * (k + 1) / (n - k - 1))}


def fit_all(t, y) -> Dict[str, Dict]:
    """The three fits of one series, keyed 'a', 'b', 'c', each with its information criteria added."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    fits = {"a": fit_piecewise(t, y, True), "b": fit_piecewise(t, y, False), "c": fit_logistic(t, y)}
    for m, f in fits.items():
        f.update(information_criteria(f["sse"], len(y), N_PARAMS[m]))
    return fits


def winner(fits: Dict[str, Dict]) -> Dict:
    """The model lowest on AIC and the one lowest on BIC, and whether one model wins clearly (lowest on both, by CLEAR_DELTA or more
    on both against the runner-up)."""
    by_aic = sorted(fits, key=lambda m: fits[m]["AIC"])
    by_bic = sorted(fits, key=lambda m: fits[m]["BIC"])
    d_aic = fits[by_aic[1]]["AIC"] - fits[by_aic[0]]["AIC"]
    d_bic = fits[by_bic[1]]["BIC"] - fits[by_bic[0]]["BIC"]
    same = by_aic[0] == by_bic[0]
    return {"AIC": by_aic[0], "BIC": by_bic[0], "agree": same, "d AIC": float(d_aic), "d BIC": float(d_bic),
            "clear": bool(same and d_aic >= CLEAR_DELTA and d_bic >= CLEAR_DELTA)}


def bootstrap(t, y, model: str, fit: Dict, rng: np.random.Generator, draws: int = DRAWS) -> Dict[str, np.ndarray]:
    """Residual bootstrap of one fitted model: ``draws`` series pred + residuals drawn with replacement, each refitted (the break
    searched again for a and b). Returns the arrays of the resampled break, pre and post slope and step (a, b) or t0 and r (c).
    A logistic refit that fails to converge is dropped (the count of kept draws is returned as 'kept')."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    r = y - fit["pred"]
    out = {k: [] for k in (("t0", "r") if model == "c" else ("break", "pre slope", "post slope", "step"))}
    for _ in range(draws):
        ys = fit["pred"] + rng.choice(r, len(r), replace=True)
        if model == "c":
            try:
                f = fit_logistic(t, ys)
            except RuntimeError:
                continue
            out["t0"].append(f["t0"]); out["r"].append(f["r"])
        else:
            f = fit_piecewise(t, ys, model == "a")
            for k in out:
                out[k].append(f[k])
    res = {k: np.asarray(v, float) for k, v in out.items()}
    res["kept"] = len(next(iter(res.values())))
    return res


def doubling(slope: float) -> float:
    """Doubling time ln 2 / slope in years (inf when the slope is 0 or below)."""
    return float(np.log(2) / slope) if slope > 0 else float("inf")


def compare_series(series: Dict[str, pd.Series], first: int, last: int, seed: int, draws: int = DRAWS,
                   names: Optional[Dict[str, str]] = None) -> Dict[str, pd.DataFrame]:
    """The three models on every series over ``first``..``last`` (a year with a zero count would have no log: asserted absent).

    Returns two frames: ``models`` (one row per series x model: n, SSE, k, AIC, BIC, AICc, their differences to the best, the
    winner flags) and ``estimates`` (one row per series x model: break or t0 and the slopes / step / r with their bootstrap
    intervals and doubling times). Generator: np.random.default_rng([seed, i_series, i_model]) for each bootstrap, so a series'
    intervals do not depend on which other series run."""
    names = names or {}
    mrows, erows = [], []
    for i, (key, s) in enumerate(series.items()):
        yrs = np.arange(first, last + 1)
        cnt = s.reindex(yrs).astype(float)
        assert (cnt > 0).all(), f"{key}: a zero or missing count in {first}-{last}"
        t, y = yrs.astype(float), np.log(cnt.to_numpy())
        fits = fit_all(t, y)
        win = winner(fits)
        best_aic = min(f["AIC"] for f in fits.values())
        best_bic = min(f["BIC"] for f in fits.values())
        for j, m in enumerate(MODELS):
            f = fits[m]
            mrows.append({"series": names.get(key, key), "key": key, "years": f"{first}–{last}", "n": len(y), "model": f"({m}) {MODELS[m]}",
                          "parameters k": N_PARAMS[m], "SSE (log scale)": round(f["sse"], 4), "AIC": round(f["AIC"], 2),
                          "BIC": round(f["BIC"], 2), "AICc": round(f["AICc"], 2), "ΔAIC": round(f["AIC"] - best_aic, 2),
                          "ΔBIC": round(f["BIC"] - best_bic, 2), "lowest AIC": m == win["AIC"], "lowest BIC": m == win["BIC"],
                          "wins clearly": bool(win["clear"] and m == win["AIC"])})
            bs = bootstrap(t, y, m, f, np.random.default_rng([seed, i, j]), draws)
            q = lambda a: np.percentile(a, [2.5, 97.5])                                                           # noqa: E731
            row = {"series": names.get(key, key), "key": key, "years": f"{first}–{last}", "model": f"({m}) {MODELS[m]}",
                   "bootstrap draws kept": bs["kept"]}
            if m == "c":
                row.update({"inflection year t0": round(f["t0"], 1), "t0 low": round(q(bs["t0"])[0], 1), "t0 high": round(q(bs["t0"])[1], 1),
                            "early growth rate r": round(f["r"], 3), "r low": round(q(bs["r"])[0], 3), "r high": round(q(bs["r"])[1], 3),
                            "ceiling K (count)": round(f["K"], 0)})
            else:
                lo, hi = q(bs["break"])
                row.update({"break year": f["break"], "break low": int(np.floor(lo)), "break high": int(np.ceil(hi)),
                            "share of draws at the break": round(float((bs["break"] == f["break"]).mean()), 3)})
                for k in ("pre slope", "post slope"):
                    a, b_ = q(bs[k])
                    row.update({k: round(f[k], 3), f"{k} low": round(a, 3), f"{k} high": round(b_, 3),
                                f"{k.split()[0]} doubling (years)": round(doubling(f[k]), 1) if f[k] > 0 else "no doubling"})
                if m == "a":
                    a, b_ = q(bs["step"])
                    row.update({"level step (factor)": round(f["step"], 2), "step low": round(a, 2), "step high": round(b_, 2)})
            erows.append(row)
    return {"models": pd.DataFrame(mrows), "estimates": pd.DataFrame(erows)}
