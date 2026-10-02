"""The three analyses the Labelling Analysis printed as OPEN, now closed (rulings 2026-09-25).

Three margin stickers of the brief (``sm_index.STICKERS``) said the document had not done the
work it was pointing at. This module does it, and nothing else:

* **O1 — the doubling time** (sticker on 1.1, comment C1). "The doubling time is not fitted:
  needs the full B64 series." Fitted here for the corpus and for the aeronautics baseline, as
  ln 2 over the slope of log count on priority year, with an interval.
* **O2 — the discovery curve** (sticker on 2.2, comment C19). "The discovery curve is not built;
  the answer rests on evenness alone." Built here as an accumulation curve of distinct
  archetypes against aircraft in priority order, with a rarefaction reference and the standard
  species-richness estimators of what has not been seen.
* **O3 — is the regional lag a constant** (sticker on 4.2, comment C49). "'Is the lag a
  constant' is read off the table, not tested." Tested here as a class x region interaction on
  priority year, rank-based and by permutation, with a per-class offset and its interval.

House rules of ``la_tables`` apply: every function takes the live :class:`Dataset` (and the
analysis frame :func:`la_tables.base` builds) and returns a DataFrame; nothing prints, nothing
is written to disk, and the frames the drawing function reads are the frames the tables print,
so a figure and its table cannot disagree.

THE BASELINE IS THE NINE-OFFICE SUBSET, AND IS LABELLED AS SUCH (settled ruling, 2026-09-25).
The stored aeronautics series is CPC B64 counted at the nine publication offices of the corpus,
not worldwide; a worldwide series was asked for and has not arrived. Every row this module
prints for the baseline carries :data:`BASELINE_LABEL`, and the swap is one line:
:data:`BASELINE_COLUMN` (the alternates already sit in the same CSV, see
``la_baseline.ALTERNATES``). Nothing else in the module names a column.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from . import la_baseline, la_tables, metrics
from .loaders import Dataset

# --------------------------------------------------------------------------- O1
#: THE SWAP POINT. The stored baseline column the doubling time is fitted on. Today it is the
#: nine-office CPC B64 series; when the worldwide series arrives, change these two lines (and
#: nothing else) to ``"cpc_world"`` / "worldwide" -- ``la_baseline.ALTERNATES`` lists what the
#: CSV already holds. Ruling of 2026-09-25: fit on the nine offices now, label it everywhere.
#: 2026-09-25: swapped to the worldwide PatSeer family series the user exported — same unit
#: (simple families) and same database as the corpus, complete at the recent edge.
BASELINE_COLUMN: str = la_baseline.PATSEER_WORLD
#: how the baseline is named in every row, caption and sentence that quotes it
BASELINE_LABEL: str = "CPC B64, worldwide simple families (PatSeer)"
#: the office-controlled reading, kept as a printed comparison row; it is the baseline of
#: Figure 1 (ii), so the two stay reconcilable.
BASELINE_ALT_COLUMN: str = la_baseline.OFFICES_B64
BASELINE_ALT_LABEL: str = "CPC B64, nine corpus offices (PATENTSCOPE publications)"

#: the fitted window. The document's trend rule ends at :data:`la_tables.LAST_COMPLETE` (2023,
#: ruling 2026-09-10); 2005 is the corpus's family-level lower bound and the start of
#: ``la_baseline.BASE_YEARS``. Before 2005 the corpus counts single figures a year and a log fit
#: would be driven by them.
FIT_WINDOW: Tuple[int, int] = (2005, la_tables.LAST_COMPLETE)

#: the same fit on other windows, printed beside the primary one so the reader can see whether
#: the answer depends on where the window is cut. ``(2005, 2019)`` stops before the recent-edge
#: truncation that pulls both series down; ``(2010, 2023)`` drops the thin early corpus years.
FIT_SENSITIVITY: List[Tuple[int, int]] = [(2005, 2019), (2010, 2023), (2013, 2023)]

#: bootstrap draws behind every interval in this module, and the seed
DRAWS: int = 2000
SEED: int = 42


def baseline_series() -> pd.Series:
    """The aeronautics series the doubling time is fitted on, year-indexed.

    The single place a baseline column is read. Swap :data:`BASELINE_COLUMN` and every number,
    label and interval in this module follows.
    """
    return la_baseline.series(BASELINE_COLUMN)


def _loglin(years: np.ndarray, counts: np.ndarray) -> Dict[str, float]:
    """Least squares of ``log(count)`` on ``year``, as doubling time with a 95 % interval.

    Years with a zero count are dropped (log is not defined there) and the number dropped is
    reported, because dropping them biases the slope down. The interval is the t interval on
    the slope, mapped through ``ln 2 / slope``; the map is monotone and decreasing, so the low
    slope gives the high doubling time.
    """
    from scipy import stats as _st

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
    # Is the series exponential at all? A doubling time is only meaningful if log count really is
    # linear in year; a series that rises and then falls back has a slope, but the slope is a
    # window average and not a growth rate. The quadratic term is fitted and its p value carried,
    # so the reader is told when the straight line is being imposed on a bend (ruling 2026-09-25).
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


def _poisson_slope(years: np.ndarray, counts: np.ndarray) -> Optional[float]:
    """Doubling time from a Poisson GLM with a log link, or None if statsmodels is absent.

    A robustness check only. A count series is Poisson-shaped, and a least squares fit on
    ``log(count)`` fits the geometric mean and drops zero years; the GLM does neither. The two
    agreeing is the evidence that the printed doubling time is not an artefact of the transform.
    """
    try:
        import statsmodels.api as sm
    except Exception:
        return None
    X = sm.add_constant(years.astype(float))
    try:
        res = sm.GLM(counts.astype(float), X, family=sm.families.Poisson()).fit()
    except Exception:
        return None
    b = float(res.params[1])
    return float(math.log(2) / b) if b > 0 else np.nan


def _series_for_fit(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.Series]:
    """The three year-indexed count series the doubling time is fitted on.

    *eVTOL aircraft* is the corpus's own unit and the series the question asks about; *eVTOL
    patents* is the same corpus counted in patent documents, which is the unit the baseline is
    in, so the corpus-against-aeronautics ratio has a like-for-like reading; the baseline is
    :func:`baseline_series`.
    """
    ac = (v.dropna(subset=["year"])["year"].astype(int).value_counts().sort_index())
    pat = ds.patents.merge(ds.identity[["patent_id", "priority_year"]], on="patent_id",
                           how="left", suffixes=("", "_id"))
    pat = (pd.to_numeric(pat["priority_year"], errors="coerce").dropna().astype(int)
           .value_counts().sort_index())
    return {"eVTOL aircraft (this corpus)": ac,
            "eVTOL patents (this corpus)": pat,
            f"aeronautics — {BASELINE_LABEL}": baseline_series().dropna().astype(int),
            # the office-controlled comparison (2026-09-25): worldwide families are the primary
            # baseline since the user's PatSeer export arrived; the nine-office row stays printed
            # so the reader can see how much the choice of baseline moves the answer.
            f"aeronautics — {BASELINE_ALT_LABEL}":
                la_baseline.series(BASELINE_ALT_COLUMN).dropna().astype(int)}


def _window_frame(s: pd.Series, lo: int, hi: int) -> Tuple[np.ndarray, np.ndarray]:
    yrs = np.arange(lo, hi + 1)
    return yrs, s.reindex(yrs, fill_value=0).to_numpy()


def doubling_time(ds: Dataset, v: pd.DataFrame,
                  windows: Optional[Sequence[Tuple[int, int]]] = None) -> pd.DataFrame:
    """How many years the annual count takes to double, fitted, for the corpus and for aeronautics.

    Closes the OPEN sticker on 1.1 (comment C1, ruling 2026-09-25). The count of filings per
    priority year is fitted as an exponential -- least squares of ``log(count)`` on year -- and
    the doubling time is ``ln 2`` over the slope, with the t interval on the slope carried
    through. Complete priority years only: the window ends at :data:`la_tables.LAST_COMPLETE`.
    One row per series per window; the first :data:`FIT_WINDOW` rows are the ones the document
    quotes and the rest are the sensitivity.

    The aeronautics rows are BOTH baselines: worldwide simple families (PatSeer, the primary
    since 2026-09-25 — same unit and database as the corpus) and the nine-office PATENTSCOPE
    subset as the office-controlled comparison; each says which it is in its own ``series`` cell. Both sides are priority-year counts and both are
    truncated at the recent edge by publication lag; that is why the window stops at 2023 and
    why the 2005-2019 sensitivity row is printed beside it.
    """
    wins = list(windows) if windows else [FIT_WINDOW] + FIT_SENSITIVITY
    series = _series_for_fit(ds, v)
    rows = []
    for lo, hi in wins:
        for name, s in series.items():
            yrs, cnt = _window_frame(s, lo, hi)
            fit = _loglin(yrs, cnt)
            if not fit:
                continue
            pois = _poisson_slope(yrs, cnt)
            rows.append({
                "series": name, "window": f"{lo}–{hi}",
                "first count": int(cnt[0]), "last count": int(cnt[-1]),
                "total": int(cnt.sum()),
                "doubling time (years)": round(fit["doubling time (years)"], 2),
                "95 % low": round(fit["doubling low"], 2),
                "95 % high": round(fit["doubling high"], 2),
                "growth per year %": round(fit["growth per year %"], 1),
                "R²": round(fit["R²"], 3),
                "doubling, Poisson GLM": (round(pois, 2) if pois is not None and np.isfinite(pois)
                                          else None),
                "curvature p": (round(fit["curvature p"], 4)
                                if np.isfinite(fit.get("curvature p", np.nan)) else None),
                "shape": _fit_shape(fit),
                "years fitted": fit["years fitted"],
                "primary": (lo, hi) == FIT_WINDOW,
            })
    out = pd.DataFrame(rows)
    # 2026-09-25: the interval as one printable string, so stated prose can quote it with a
    # single placeholder instead of pairing two numbers and risking them drifting apart.
    out["95 % interval"] = [f"{lo:.1f} to {hi:.1f}" if pd.notna(lo) and pd.notna(hi) else ""
                            for lo, hi in zip(out["95 % low"], out["95 % high"])]
    out.attrs["baseline_column"] = BASELINE_COLUMN
    out.attrs["baseline_label"] = BASELINE_LABEL
    out.attrs["baseline_source"] = la_baseline.SOURCE
    out.attrs["window"] = FIT_WINDOW
    return out


def _fit_shape(fit: Dict[str, float]) -> str:
    """Whether the straight line on log count is a fair description of the series.

    ``exponential`` = no detectable bend; ``bends down`` / ``bends up`` = the quadratic term is
    significant, and the doubling time is then an average over the window rather than a rate the
    series held. Both sides of the comparison are truncated at the recent edge by publication
    lag, which bends a priority-year series down on its own, so a downward bend is expected and
    is one reason the 2005-2019 window is printed beside the primary one.
    """
    p = fit.get("curvature p", np.nan)
    if not np.isfinite(p) or p >= 0.05:
        return "exponential"
    return "bends down — doubling time is a window average" if fit["curvature"] < 0 else \
           "bends up — doubling time is a window average"


def doubling_ratio(ds: Dataset, v: pd.DataFrame,
                   windows: Optional[Sequence[Tuple[int, int]]] = None) -> pd.DataFrame:
    """The sentence the doubling time is for: eVTOL doubles X times faster than aeronautics.

    The ratio of the two doubling times is the ratio of the two slopes the other way up, so it
    is estimated and bounded together rather than by dividing two rounded numbers. The interval
    is a paired bootstrap over YEARS (:data:`DRAWS` draws, seed :data:`SEED`): a draw resamples
    the years of the window with replacement and refits both series on the same drawn years, so
    the two fits stay paired and the shared truncation at the recent edge is resampled with
    them. Ruling 2026-09-25; the aeronautics side is :data:`BASELINE_LABEL` — worldwide simple families since the user's PatSeer export of the same day.

    A bootstrap over years, not over patents: the fit has one observation per year, and it is
    the year-to-year scatter around the exponential, not the counting of documents, that the
    interval has to carry.
    """
    wins = list(windows) if windows else [FIT_WINDOW] + FIT_SENSITIVITY
    series = _series_for_fit(ds, v)
    base_name = f"aeronautics — {BASELINE_LABEL}"
    rng = np.random.default_rng(SEED)
    rows = []
    for lo, hi in wins:
        yrs, base = _window_frame(series[base_name], lo, hi)
        for name in ("eVTOL aircraft (this corpus)", "eVTOL patents (this corpus)"):
            _, top = _window_frame(series[name], lo, hi)
            f_top, f_base = _loglin(yrs, top), _loglin(yrs, base)
            if not f_top or not f_base:
                continue
            ratio = f_top["doubling time (years)"] / f_base["doubling time (years)"]
            draws = []
            n = len(yrs)
            for _ in range(DRAWS):
                ix = rng.integers(0, n, n)
                if len(np.unique(yrs[ix])) < 4:
                    continue
                a, b = _loglin(yrs[ix], top[ix]), _loglin(yrs[ix], base[ix])
                if not a or not b:
                    continue
                if a["slope (log count per year)"] <= 0 or b["slope (log count per year)"] <= 0:
                    continue
                draws.append(a["doubling time (years)"] / b["doubling time (years)"])
            d = np.array(draws)
            rows.append({
                "window": f"{lo}–{hi}", "corpus series": name,
                "baseline": base_name,
                "corpus doubling (years)": round(f_top["doubling time (years)"], 2),
                "baseline doubling (years)": round(f_base["doubling time (years)"], 2),
                "ratio (corpus / baseline)": round(ratio, 3),
                "times faster": round(1 / ratio, 2),
                "95 % low": round(float(np.percentile(d, 2.5)), 3) if len(d) > 50 else None,
                "95 % high": round(float(np.percentile(d, 97.5)), 3) if len(d) > 50 else None,
                "times faster low": (round(1 / float(np.percentile(d, 97.5)), 2)
                                     if len(d) > 50 else None),
                "times faster high": (round(1 / float(np.percentile(d, 2.5)), 2)
                                      if len(d) > 50 else None),
                "draws used": int(len(d)),
                "primary": (lo, hi) == FIT_WINDOW,
            })
    out = pd.DataFrame(rows)
    # 2026-09-25: as above — the "times faster" interval as one printable string.
    out["times faster interval"] = [
        f"{lo:.2f} to {hi:.2f}" if pd.notna(lo) and pd.notna(hi) else ""
        for lo, hi in zip(out["times faster low"], out["times faster high"])]
    out.attrs["baseline_column"] = BASELINE_COLUMN
    out.attrs["baseline_label"] = BASELINE_LABEL
    return out


# --------------------------------------------------------------------------- O2
#: the archetype levels the discovery curve is built at -- the three the document already reads
#: (``la_tables.archetype_levels``, ruling recorded there). A0 is the class, A0c the class with
#: the propulsive-unit band, A1t the class with the wing count and whether anything tilts.
DISCOVERY_LEVELS: List[str] = ["A0", "A0c", "A1t"]
#: orderings drawn to break the ties inside a priority year (only the year is recorded, so the
#: order of the aircraft filed in the same year is unknown and is averaged over)
ORDERS: int = 400
#: the tail the flattening is read on: new archetypes over the last this-many aircraft
TAIL: int = 100


def _rarefaction(counts: np.ndarray, ns: np.ndarray) -> np.ndarray:
    """Expected distinct types in a random subsample of size n, drawn without replacement.

    The classical rarefaction expectation: ``E[S_n] = S - sum_i C(N-n_i, n) / C(N, n)``. It is
    the reference the chronological curve is read against -- what the accumulation would look
    like if the same aircraft had arrived in a random order rather than in date order.
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


def _complete(v: pd.DataFrame) -> pd.DataFrame:
    """The aircraft of complete priority years — the document's rule, applied here too.

    Priority years past :data:`la_tables.LAST_COMPLETE` are truncated by publication lag, so the
    aircraft in them are the ones that happened to publish early, not the year's filings. A
    curve run through them would read a sampling artefact as a slowdown in discovery, which is
    the very thing the curve is being asked about (ruling 2026-09-25).
    """
    w = v.dropna(subset=["year"]).copy()
    return w[w["year"].le(la_tables.LAST_COMPLETE)].copy()


def discovery_curve(ds: Dataset, v: pd.DataFrame,
                    levels: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """Distinct archetypes seen against aircraft seen, in priority order — the discovery curve.

    Closes the OPEN sticker on 2.2 (comment C19, ruling 2026-09-25). The question is whether the
    design space is filling up or still opening. Aircraft are put in priority order and the
    running number of DISTINCT archetypes is counted; a curve that bends over means the space is
    filling, a curve still climbing at the right edge means it is still opening.

    Only the priority YEAR is recorded, so the order inside a year is unknown: every year's
    aircraft are shuffled and the curve is averaged over :data:`ORDERS` draws (seed
    :data:`SEED`), with the 2.5-97.5 band of those draws printed beside it. The rarefaction
    column is the same aircraft in random order (:func:`_rarefaction`) -- the reference that
    says whether date order discovers archetypes faster or slower than chance.

    One row per level per aircraft-count step; ``la_discovery_estimators`` holds the numbers the
    prose quotes.
    """
    lv = list(levels) if levels else DISCOVERY_LEVELS
    w = _complete(v)
    rng = np.random.default_rng(SEED)
    rows = []
    for level in lv:
        key = la_tables._archetype_key(w, level)
        sub = w[key.notna()].copy()
        sub["key"] = key[key.notna()]
        years = sub["year"].to_numpy()
        codes = pd.factorize(sub["key"])[0]
        N, S = len(codes), int(codes.max() + 1)
        curves = np.zeros((ORDERS, N), dtype=float)
        for d in range(ORDERS):
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
        rar = _rarefaction(counts, ns)
        # the year reached at each step, averaged the same way as the curve
        ysort = np.sort(years)
        for i in range(N):
            rows.append({"level": level, "aircraft": int(ns[i]),
                         "priority year reached": int(ysort[i]),
                         "archetypes (date order)": round(float(mean[i]), 2),
                         "2.5 %": round(float(lo[i]), 2), "97.5 %": round(float(hi[i]), 2),
                         "archetypes (random order)": round(float(rar[i]), 2)})
    out = pd.DataFrame(rows)
    out.attrs["orders"] = ORDERS
    out.attrs["seed"] = SEED
    return out


def _chao1(counts: np.ndarray) -> Dict[str, float]:
    """Bias-corrected Chao1 and its log-normal 95 % interval, plus the two jackknives.

    Chao1 reads the number of types seen ONCE (``f1``) against the number seen TWICE (``f2``):
    many singletons mean the sample is still turning up new types. The bias-corrected form
    ``S + f1(f1-1) / (2(f2+1))`` is used because it is defined when ``f2 = 0``, which happens at
    the finer levels. The interval is Chao's standard log-normal one, which is asymmetric by
    construction: a richness estimate cannot fall below what has already been seen.
    """
    S = int(len(counts))
    N = int(counts.sum())
    f1 = int((counts == 1).sum())
    f2 = int((counts == 2).sum())
    chao = S + f1 * (f1 - 1) / (2.0 * (f2 + 1))
    unseen = chao - S
    # variance of the bias-corrected estimator (Chao 1987; Colwell & Coddington 1994)
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


def discovery_estimators(ds: Dataset, v: pd.DataFrame, curve: Optional[pd.DataFrame] = None,
                         levels: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """How many archetypes the record has not yet turned up, and whether the curve has flattened.

    The companion of :func:`discovery_curve` (ruling 2026-09-25). Chao1 and the two jackknives
    estimate the richness the corpus would reach if it kept sampling the SAME population; the
    difference from what has been seen is the estimate of the unseen. Sample coverage is the
    Good-Turing reading, the share of the next aircraft expected to carry an archetype already
    seen. The flattening is read on the curve itself: how many new archetypes appeared over the
    last :data:`TAIL` aircraft in date order, against how many appeared over the :data:`TAIL`
    before them.

    THE ASSUMPTION, stated because it decides what the number means: these estimators assume a
    CLOSED population -- a fixed set of archetypes with fixed relative frequencies, sampled at
    random. A design space is not closed: an archetype nobody has drawn yet cannot be estimated
    from singletons, and date order is not random sampling (that is exactly what the rarefaction
    column tests). The unseen count is therefore a floor on the archetypes already in the record's
    population but not yet drawn, NOT a forecast of what engineers will invent. Read it as "the
    sample is/is not still turning up new combinations", never as "the design space contains N".
    """
    lv = list(levels) if levels else DISCOVERY_LEVELS
    cur = curve if curve is not None else discovery_curve(ds, v, lv)
    w = _complete(v)
    rows = []
    for level in lv:
        key = la_tables._archetype_key(w, level)
        counts = key.dropna().value_counts().to_numpy()
        est = _chao1(counts)
        c = cur[cur["level"].eq(level)].sort_values("aircraft")
        y = c["archetypes (date order)"].to_numpy()
        n = len(y)
        last = float(y[-1] - y[max(0, n - 1 - TAIL)])
        prev = float(y[max(0, n - 1 - TAIL)] - y[max(0, n - 1 - 2 * TAIL)])
        # the same tail under random order: how many new archetypes the last TAIL aircraft would
        # have brought if they had been a random draw rather than the most recent filings. This
        # is the reference the flattening is read against -- an accumulation curve flattens
        # simply because the sample grows, and only a tail BELOW the random-order tail is
        # evidence that discovery itself has slowed.
        r = c["archetypes (random order)"].to_numpy()
        rar_last = float(r[-1] - r[max(0, n - 1 - TAIL)])
        half = int(n // 2)
        rows.append({
            "level": level,
            "aircraft": est["aircraft"], "archetypes observed": est["observed"],
            "seen once (f1)": est["singletons f1"], "seen twice (f2)": est["doubletons f2"],
            "Chao1": round(est["Chao1"], 1),
            "Chao1 95 % low": round(est["Chao1 low"], 1),
            "Chao1 95 % high": round(est["Chao1 high"], 1),
            "estimated unseen": round(est["Chao1"] - est["observed"], 1),
            "jackknife 1": round(est["jackknife 1"], 1),
            "jackknife 2": round(est["jackknife 2"], 1),
            "coverage": round(est["coverage (Good–Turing)"], 4),
            "share of richness found": round(est["observed"] / est["Chao1"], 3),
            "archetypes by half the corpus": round(float(y[half - 1]), 1),
            f"new in the last {TAIL} aircraft": round(last, 2),
            f"new in the {TAIL} before that": round(prev, 2),
            f"new in the last {TAIL}, random order": round(rar_last, 2),
            "date order vs random, last tail": round(last - rar_last, 2),
            "verdict": _discovery_verdict(est, last, prev, rar_last),
        })
    out = pd.DataFrame(rows)
    out.attrs["assumption"] = ("Chao1 and the jackknives assume a closed population sampled at "
                              "random; the estimate is of archetypes present but not yet drawn, "
                              "not of designs not yet invented")
    out.attrs["tail"] = TAIL
    return out


def _discovery_verdict(est: Dict[str, float], last: float, prev: float, rar_last: float) -> str:
    """One sentence per level: filling up, still opening, or too close to call.

    Three readings have to agree before the word "filling" is used: coverage (the share of the
    next aircraft expected to be an archetype already seen), the share of the estimated richness
    already found, and the tail of the curve read against the same tail in random order. A tail
    at or above the random-order tail is not a flattening -- it is the curve doing what any
    accumulation curve does as n grows.
    """
    found = est["observed"] / est["Chao1"]
    cov = est["coverage (Good–Turing)"]
    tail = (f"{last:g} new in the last {TAIL} aircraft against {rar_last:.1f} expected in a random "
            f"{TAIL}, and {prev:g} in the {TAIL} before")
    if found >= 0.95 and cov >= 0.99 and last <= max(1.0, rar_last):
        return f"filling up — {cov:.1%} coverage, {found:.0%} of the estimated richness found; {tail}"
    if last >= rar_last and found < 0.95:
        return f"still opening — {found:.0%} of the estimated richness found; {tail}"
    return f"slowing, not closed — {found:.0%} of the estimated richness found; {tail}"


# --------------------------------------------------------------------------- O3
#: the smallest cell a regional offset is estimated on -- the rule of
#: :func:`la_tables.class_region_timing`, kept so the test is run on the table it tests
MIN_CELL: int = 5
#: the region every offset is measured from: the claim under test is that North America leads
REFERENCE_REGION: str = "North America"
#: permutations behind the interaction test
PERMS: int = 5000


def _design(frame: pd.DataFrame, interaction: bool) -> np.ndarray:
    """Dummy design matrix for ``class + region`` (+ their interaction), reference-coded."""
    cls = pd.get_dummies(frame["class"], drop_first=True, dtype=float)
    reg = pd.get_dummies(frame["region"], drop_first=True, dtype=float)
    parts = [np.ones((len(frame), 1)), cls.to_numpy(), reg.to_numpy()]
    if interaction:
        inter = np.column_stack([cls[c].to_numpy() * reg[r].to_numpy()
                                 for c in cls.columns for r in reg.columns])
        parts.append(inter)
    return np.column_stack(parts)


def _rss(X: np.ndarray, y: np.ndarray) -> Tuple[float, int]:
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid), int(rank)


def _fit_resid(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    return fit, y - fit


def lag_frame(v: pd.DataFrame, min_cell: int = MIN_CELL) -> pd.DataFrame:
    """The aircraft the lag test is run on: class, region, priority year, complete years only.

    Same base as :func:`la_tables.class_region_timing` -- the table the claim is read off -- so
    the test and the table cannot be run on different aircraft. A class is kept only when all
    three regions hold ``min_cell`` aircraft: an interaction is a comparison of offsets, and a
    class with an empty cell has no offset to compare.
    """
    w = v.dropna(subset=["year", "topType"]).copy()
    w = w[w["year"].le(la_tables.LAST_COMPLETE) & w["region3"].isin(la_tables.REGIONS)]
    n = w.pivot_table(index="topType", columns="region3", values="year", aggfunc="size")
    n = n.reindex(columns=la_tables.REGIONS).fillna(0)
    keep = n[(n >= min_cell).all(axis=1)].index
    w = w[w["topType"].isin(keep)].copy()
    w["class"] = [metrics.ARCH_NAMES.get(c, c) for c in w["topType"]]
    w["region"] = pd.Categorical(w["region3"], categories=la_tables.REGIONS, ordered=True)
    return w[["aircraft_id", "class", "region", "year"]].reset_index(drop=True)


def lag_offsets(v: pd.DataFrame, min_cell: int = MIN_CELL) -> pd.DataFrame:
    """Each class's regional offset in priority year, against North America, with an interval.

    Route (ii) of the question (comment C49, ruling 2026-09-25): estimate the offset class by
    class and then ask whether the offsets are the same everywhere. The offset is the difference
    of MEDIAN priority years, because priority year is a bounded, left-skewed, tied count and a
    mean of it is pulled by the thin early tail. The interval is a percentile bootstrap
    (:data:`DRAWS` draws, seed :data:`SEED`) resampling aircraft inside each class-region cell,
    so it carries the small cells honestly -- several are a dozen aircraft and come back with an
    interval three years wide, which is the point.

    An offset above zero means the region filed LATER than North America in that class.
    """
    w = lag_frame(v, min_cell)
    rng = np.random.default_rng(SEED)
    rows = []
    for cls, sub in w.groupby("class", observed=True):
        ref = sub.loc[sub["region"].eq(REFERENCE_REGION), "year"].to_numpy()
        for reg in la_tables.REGIONS:
            arr = sub.loc[sub["region"].eq(reg), "year"].to_numpy()
            if not len(arr) or not len(ref):
                continue
            obs = float(np.median(arr) - np.median(ref))
            d = np.array([np.median(rng.choice(arr, len(arr), replace=True))
                          - np.median(rng.choice(ref, len(ref), replace=True))
                          for _ in range(DRAWS)])
            rows.append({"class": cls, "region": reg, "aircraft": int(len(arr)),
                         "median priority year": float(np.median(arr)),
                         "offset vs North America (years)": round(obs, 1),
                         "95 % low": round(float(np.percentile(d, 2.5)), 1),
                         "95 % high": round(float(np.percentile(d, 97.5)), 1)})
    out = pd.DataFrame(rows)
    out.attrs["reference"] = REFERENCE_REGION
    out.attrs["min_cell"] = min_cell
    return out


def lag_constancy(v: pd.DataFrame, min_cell: int = MIN_CELL, perms: int = PERMS) -> pd.DataFrame:
    """Is the regional lag the same in every class? The interaction test behind the claim.

    Closes the OPEN sticker on 4.2 (comment C49, ruling 2026-09-25). "North America leads, then
    Europe, then Asia-Pacific" is a statement about the MAIN effect of region; "the lag is a
    constant" is the statement that this offset does not change from class to class, which is
    exactly a class x region INTERACTION being absent.

    Route taken and why. Priority year is bounded above (nothing past 2023), skewed and heavily
    tied, so the parametric two-way ANOVA is not safe on it. The test is therefore run on the
    MID-RANKS of priority year, and its p value comes from a permutation rather than from the F
    distribution: the reduced (additive) model is fitted, its residuals are permuted and added
    back to the additive fit, and the interaction F is recomputed on each of :data:`perms` draws
    (Freedman-Lane, seed :data:`SEED`). That null keeps both main effects -- the regional lead
    and the class's own date -- and destroys only the interaction, which is the hypothesis under
    test. The parametric p is printed beside it as a cross-check, never as the answer.

    Rows: the interaction test, the two main effects on the same ranks, and the spread of the
    per-class offsets that :func:`lag_offsets` prints. ``verdict`` is the plain reading.
    """
    from scipy import stats as _st

    w = lag_frame(v, min_cell)
    y = _st.rankdata(w["year"].to_numpy())
    Xfull = _design(w, True)
    Xadd = _design(w, False)
    Xcls = np.column_stack([np.ones(len(w)),
                            pd.get_dummies(w["class"], drop_first=True, dtype=float).to_numpy()])
    Xreg = np.column_stack([np.ones(len(w)),
                            pd.get_dummies(w["region"], drop_first=True, dtype=float).to_numpy()])
    rss_full, k_full = _rss(Xfull, y)
    rss_add, k_add = _rss(Xadd, y)
    n = len(w)
    df_int, df_res = k_full - k_add, n - k_full
    F_int = ((rss_add - rss_full) / df_int) / (rss_full / df_res)
    p_param = float(_st.f.sf(F_int, df_int, df_res))

    fit_add, resid_add = _fit_resid(Xadd, y)
    rng = np.random.default_rng(SEED)
    null = np.empty(perms)
    for i in range(perms):
        ystar = fit_add + rng.permutation(resid_add)
        rf, _ = _rss(Xfull, ystar)
        ra, _ = _rss(Xadd, ystar)
        null[i] = ((ra - rf) / df_int) / (rf / df_res)
    p_perm = float((1 + (null >= F_int).sum()) / (perms + 1))

    # main effects on the same ranks, each against the model without it
    rows = []
    def _main(Xsmall: np.ndarray, label: str) -> Dict:
        rss_s, k_s = _rss(Xsmall, y)
        df = k_add - k_s
        F = ((rss_s - rss_add) / df) / (rss_add / (n - k_add))
        return {"effect": label, "df": df, "F (on ranks)": round(float(F), 2),
                "p (parametric)": float(_st.f.sf(F, df, n - k_add)),
                "partial η²": round(float((rss_s - rss_add) / rss_s), 4)}

    off = lag_offsets(v, min_cell)
    non_ref = off[off["region"].ne(REFERENCE_REGION)]
    spread = (non_ref.groupby("region", observed=True)["offset vs North America (years)"]
              .agg(["min", "max", "median"]))

    rows.append({"effect": "class × region (the lag is not a constant)",
                 "df": df_int, "F (on ranks)": round(float(F_int), 2),
                 "p (parametric)": p_param, "p (permutation)": p_perm,
                 "partial η²": round(float((rss_add - rss_full) / rss_add), 4),
                 "permutations": perms})
    rows.append(_main(Xcls, "region (the lead itself)"))
    rows.append(_main(Xreg, "class (each class has its own date)"))
    # The homogeneity test, one region at a time. The full interaction spends 12 degrees of
    # freedom on two regions at once; a reader who wants to know whether EUROPE's offset is the
    # same in every class is asking a 6-degree-of-freedom question, and asking it on its own is
    # the more powerful test. Same rank response, same Freedman-Lane null, restricted to that
    # region and the reference (ruling 2026-09-25).
    for reg in la_tables.REGIONS:
        if reg == REFERENCE_REGION:
            continue
        sub = w[w["region"].isin([REFERENCE_REGION, reg])].copy()
        sub["region"] = sub["region"].astype(str)
        ysub = _st.rankdata(sub["year"].to_numpy())
        Xf, Xa = _design(sub, True), _design(sub, False)
        rf, kf = _rss(Xf, ysub)
        ra, ka = _rss(Xa, ysub)
        dfi, dfr = kf - ka, len(sub) - kf
        Fi = ((ra - rf) / dfi) / (rf / dfr)
        fa, resa = _fit_resid(Xa, ysub)
        rg = np.random.default_rng(SEED)
        nul = np.empty(perms)
        for i in range(perms):
            ys = fa + rg.permutation(resa)
            r1, _ = _rss(Xf, ys)
            r0, _ = _rss(Xa, ys)
            nul[i] = ((r0 - r1) / dfi) / (r1 / dfr)
        rows.append({"effect": f"class × region, {reg} against {REFERENCE_REGION} "
                               f"(is this region's offset the same in every class)",
                     "region tested": reg, "aircraft": int(len(sub)), "df": dfi, "F (on ranks)": round(float(Fi), 2),
                     "p (parametric)": float(_st.f.sf(Fi, dfi, dfr)),
                     "p (permutation)": float((1 + (nul >= Fi).sum()) / (perms + 1)),
                     "partial η²": round(float((ra - rf) / ra), 4),
                     "permutations": perms})
    out = pd.DataFrame(rows)
    out["aircraft"] = out.get("aircraft", pd.Series(np.nan, index=out.index)).fillna(n).astype(int)
    out["classes"] = w["class"].nunique()
    # two regional homogeneity tests are run, so the smaller of the two p values is the smaller of
    # two chances to be surprised; Holm's correction is printed beside them and the verdict quotes
    # the corrected value, not the raw one (ruling 2026-09-25).
    reg_rows = out[out["effect"].str.startswith("class × region,")].copy()
    holm = {}
    if len(reg_rows):
        srt = reg_rows.sort_values("p (permutation)")
        m = len(srt)
        run = 0.0
        for i, (ix, r) in enumerate(srt.iterrows()):
            run = max(run, min(1.0, float(r["p (permutation)"]) * (m - i)))
            holm[ix] = round(run, 4)
    out["p (Holm, across the two regions)"] = pd.Series(holm)
    verdict = _lag_verdict(p_perm, spread, w, reg_rows.assign(
        holm=[holm.get(i) for i in reg_rows.index]))
    out.attrs["verdict"] = verdict
    out.attrs["offset_spread"] = spread
    out["verdict"] = [verdict] + [""] * (len(out) - 1)
    return out


def _lag_verdict(p_perm: float, spread: pd.DataFrame, w: pd.DataFrame,
                 reg: Optional[pd.DataFrame] = None) -> str:
    """The plain answer: constant lag, or not.

    The joint interaction and the two one-region homogeneity tests are read together, because
    they answer different questions: the joint test asks whether ANY regional offset moves with
    the class, the one-region tests ask which one does.
    """
    eur = spread.loc["Europe"] if "Europe" in spread.index else None
    asia = spread.loc["Asia-Pacific"] if "Asia-Pacific" in spread.index else None
    span = ""
    if eur is not None and asia is not None:
        span = (f"; across the {w['class'].nunique()} classes tested the Europe offset runs "
                f"{eur['min']:g} to {eur['max']:g} years and the Asia-Pacific offset "
                f"{asia['min']:g} to {asia['max']:g}")
    if p_perm < 0.05:
        return ("not a constant — the regional offset changes from class to class "
                f"(permutation p = {p_perm:.3f}){span}")
    named = ""
    if reg is not None and len(reg):
        hits = reg[reg["holm"].astype(float) < 0.05] if "holm" in reg else reg.iloc[:0]
        raw = reg[reg["p (permutation)"].astype(float) < 0.05]
        if len(hits):
            named = ("; the offset that moves is " +
                     ", ".join(f"{r['region tested']} (Holm p = {float(r['holm']):.3f})"
                               for _, r in hits.iterrows()))
        elif len(raw):
            named = ("; taken one region at a time only " +
                     ", ".join(f"{r['region tested']} moves with the class "
                               f"(p = {float(r['p (permutation)']):.3f}, Holm "
                               f"{float(r['holm']):.3f} across the two regions)"
                               for _, r in raw.iterrows()))
    if p_perm < 0.10:
        return ("borderline — a constant lag is not rejected, and not confirmed: the joint "
                f"class × region interaction falls short of the 5 % line (permutation "
                f"p = {p_perm:.3f}){named}{span}")
    return ("consistent with a constant — no class × region interaction is detected "
            f"(permutation p = {p_perm:.3f}), so the same regional offset fits every class "
            f"tested{span}. Absence of evidence on cells this small is not evidence of absence")


# --------------------------------------------------------------------------- the figure
def fig_discovery_curve(curve: pd.DataFrame, path, levels: Optional[Sequence[str]] = None):
    """The discovery curve: distinct archetypes against aircraft, in priority order.

    Written here rather than in ``sm_figures`` (another author owns that module, 2026-09-25) and
    following its house rules: 7 pt floor, 200 dpi, the document's text width, every colour also
    carrying a dash so the panel survives black and white, and the base printed on the panel.
    Draws NOTHING it does not read from :func:`discovery_curve`, so the curve and the table
    cannot disagree. One line per level, the shaded band the 2.5-97.5 % of the tie orderings,
    the dashed line the random-order rarefaction reference.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from .atlas import CAT, INK, STYLE, _hgrid
    from . import sm_text_methods as _tm        # 2026-09-26 (C47/C49): readable level names

    lv = list(levels) if levels else DISCOVERY_LEVELS
    with plt.rc_context({**STYLE, "font.size": 8.0}):
        fig, ax = plt.subplots(figsize=(7.09, 3.6), dpi=200)
        tail_lines = []
        for i, level in enumerate(lv):
            c = curve[curve["level"].eq(level)].sort_values("aircraft")
            x = c["aircraft"].to_numpy()
            colour = CAT[i % len(CAT)]
            ax.fill_between(x, c["2.5 %"], c["97.5 %"], color=colour, alpha=0.18, linewidth=0)
            ax.plot(x, c["archetypes (date order)"], color=colour, lw=1.6,
                    dashes=[(None, None), (5, 2), (1.5, 1.5)][i % 3],
                    label=f"{_tm.level_name(level)} — {int(c['archetypes (date order)'].iloc[-1])} "
                          f"archetypes in {len(c)} aircraft")
            ax.plot(x, c["archetypes (random order)"], color=colour, lw=0.9, alpha=0.55,
                    dashes=(1, 2))
            # 2026-09-26 (C70): the reading the takeaway makes, drawn — the new archetypes of the
            # last hundred aircraft in date order against a random order, read off the same curve
            if len(c) > 100:
                d = c["archetypes (date order)"].to_numpy()
                r = c["archetypes (random order)"].to_numpy()
                tail_lines.append(f"{_tm.LEVEL_CODES.get(level, (level,))[0]}: "
                                  f"{d[-1] - d[-101]:.1f} new, {r[-1] - r[-101]:.1f} by chance")
        if tail_lines:
            n_max = float(curve["aircraft"].max())
            ax.axvspan(n_max - 100, n_max, color=INK, alpha=0.06, lw=0, zorder=0)
            top = float(curve["archetypes (date order)"].max())
            ax.set_ylim(-0.42 * top, top * 1.08)          # room under the curves for the legend
            ax.text(n_max - 104, 0.52 * top, "the last 100 aircraft (grey band):\n"
                    + "\n".join(tail_lines), ha="right", va="center", fontsize=6.8, color=INK,
                    linespacing=1.2, bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.9))
        _hgrid(ax)
        ax.set_xlabel("aircraft, in priority order")
        ax.set_ylabel("distinct archetypes seen")
        ax.set_title("Discovery curve: date order (solid) against random order (dotted)",
                     color=INK, loc="left")
        ax.legend(frameon=False, loc="lower right", fontsize=7.2)
        ax.set_yticks([t for t in ax.get_yticks() if 0 <= t <= ax.get_ylim()[1]])
        ax.annotate("Unit: unique aircraft of the complete windows (priority ≤ 2023), in priority "
                    "order\nSource: human labelling (class, wings, tilt, units) · PatSeer "
                    "(priority date)", xy=(0, 0), xycoords="axes fraction", xytext=(0, -34),
                    textcoords="offset points", ha="left", va="top", fontsize=6.8, color=INK)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
    return path


# --------------------------------------------------------------------------- entry point

# --------------------------------------------------------------------------- lapse check
LAPSE_DIR = la_baseline.ASSETS / "external" / "lapse_check"


def lapse_check() -> pd.DataFrame:
    """The seven-year rule of 1.2, measured on the corpus instead of argued (user, 2026-09-25).

    The user ran ``seven_year_check.py`` on the full PatSeer record export (1 639 simple
    families) and supplied the outputs; this reads them verbatim from
    ``assets/external/lapse_check`` into one table so the brief's prose can quote them as
    placeholders. Two facts carry the rule: 97.7 % of the corpus's own grants arrive within
    seven years of priority (781 dated grants, median 3.06 y, p90 5.28 y), and the pending
    share per cohort collapses exactly at the rule's boundary — 4 % at 2019 against 24 % at
    2022 and 57 % at 2023. A cohort younger than the rule is undecided, not alive.
    """
    lag = pd.read_csv(LAPSE_DIR / "grant_lag_summary.csv", index_col=0)["value"]
    st = pd.read_csv(LAPSE_DIR / "status_by_priority_year.csv")
    rows = [
        {"measure": "dated grants in the corpus", "value": f"{int(lag['with_grant_date']):d}"},
        {"measure": "median priority-to-grant lag (years)", "value": f"{lag['median_lag_years']:.1f}"},
        {"measure": "90th percentile lag (years)", "value": f"{lag['p90_lag_years']:.1f}"},
        {"measure": "grants arriving within 7 years of priority", "value": f"{lag['pct_granted_within_7y']:.1f} %"},
    ]
    for y in (2019, 2021, 2022, 2023):
        r = st[st["priority_year"].eq(y)]
        if len(r):
            rows.append({"measure": f"families still pending, {y} cohort",
                         "value": f"{float(r['pending_pct'].iloc[0]):.1f} %"})
    out = pd.DataFrame(rows)
    out.attrs["source"] = ("seven_year_check.py on the PatSeer record export (snapshot 2026-06-08), "
                           "run by the author 2026-09-25; assets/external/lapse_check")
    return out


# --------------------------------------------------------------------------- aircraft in force
# Author's ruling, 2026-09-26: "it is not because of the first patent being out of force that
# the aircraft is out of force — it is the last one being out of force, i.e. NO patent regarding
# one aircraft being in force." A unique aircraft is OUT OF FORCE only when EVERY patent linked
# to it reads INACTIVE at the PatSeer snapshot; one patent that does not (granted, applied)
# keeps it in force. la_tables.abandonment_by_class (1.1.10) reads the primary patent alone and
# is left as it is; this is the brief's reading, with the old one printed beside it.

#: the priority-year cut, the seven-year rule of 1.2 measured in :func:`lapse_check`: an aircraft
#: whose primary patent has priority after this year may simply not have been decided yet
FORCE_MAX_YEAR: int = 2019
#: a class enters the chi-square test of class x out-of-force with this many aircraft or more
FORCE_TEST_MIN: int = 10


def aircraft_patents(ds: Dataset, v: pd.DataFrame, first_only: bool = False) -> pd.DataFrame:
    """Every patent linked to each unique aircraft of ``v``, one row per (aircraft, patent).

    ``first_only=True`` is the SENSITIVITY reading: a duplicate naming several aircraft is linked
    to its FIRST target alone — the rule the loader's domain gate uses for a D1/D2 row.

    The links: the aircraft's own PRIMARY patent (``v.patent_id``), plus every patent of the
    master whose row points at the aircraft through ``same_aircraft_as`` — the D1/D2 duplicates,
    which is how an aircraft recurs on a second patent in this record. A duplicate that names
    several aircraft ("…_ua1; …_ua2") is linked to each of them, since it repeats all of them.
    The whole master is read, not only the representative rows, so an unapproved duplicate of a
    representative aircraft would still count; on the current record the two readings give the
    same links. D3 filings are NOT linked: a D3 is a new version and is its own aircraft.

    ``status_known`` is False where PatSeer has no ``legal_status_raw`` for the patent; such a
    patent cannot keep an aircraft in force (it is not known to be alive).
    """
    prim = v[["aircraft_id", "patent_id"]].assign(link="primary")
    m = ds.master
    d = m.loc[m["same_aircraft_as"].notna(), ["patent_id", "same_aircraft_as"]].copy()
    d["aircraft_id"] = d["same_aircraft_as"].astype(str).str.split(";")
    if first_only:
        d["aircraft_id"] = d["aircraft_id"].str[:1]
    d = d.explode("aircraft_id")
    d["aircraft_id"] = d["aircraft_id"].str.strip()
    d = d[d["aircraft_id"].isin(set(prim["aircraft_id"]))][["aircraft_id", "patent_id"]]
    out = pd.concat([prim, d.assign(link="duplicate")]).drop_duplicates(["aircraft_id", "patent_id"])
    status = ds.identity.drop_duplicates("patent_id").set_index("patent_id")["legal_status_raw"]
    s = out["patent_id"].map(status)
    out["legal_status_raw"] = s
    out["status_known"] = s.notna() & s.fillna("").astype(str).str.strip().ne("")
    out["inactive"] = s.fillna("").astype(str).str.startswith("INACTIVE")
    return out.reset_index(drop=True)


def _force_frame(ds: Dataset, v: pd.DataFrame, max_year: int = FORCE_MAX_YEAR,
                 first_only: bool = False) -> pd.DataFrame:
    """One row per unique aircraft with a class and priority year <= ``max_year``: how many
    patents it links, whether any of them is in force (``out`` = none is), and the old reading
    (``lapsed`` = the primary patent alone). An aircraft none of whose linked patents has a
    status is dropped (it cannot be read either way); the count is in ``attrs``."""
    links = aircraft_patents(ds, v, first_only=first_only)
    links["_live"] = links["status_known"] & ~links["inactive"]
    per = links.groupby("aircraft_id").agg(linked=("patent_id", "size"),
                                           known=("status_known", "sum"), live=("_live", "any"))
    w = v[v["year"].le(max_year) & v["topType"].notna()][["aircraft_id", "topType", "lapsed"]]
    w = w.join(per, on="aircraft_id")
    unread = int(w["known"].fillna(0).eq(0).sum())
    w = w[w["known"].fillna(0).gt(0)].copy()
    w["out"] = ~w["live"].astype(bool)
    w["lapsed"] = w["lapsed"].astype(bool)
    w.attrs.update(unread=unread, links=links)
    return w


def force_aircraft(ds: Dataset, v: pd.DataFrame, max_year: int = FORCE_MAX_YEAR) -> pd.DataFrame:
    """Unique aircraft out of force per class: priority <= 2019, and EVERY linked patent INACTIVE
    at the PatSeer snapshot (author's ruling 2026-09-26). The last column is the old reading on
    the same aircraft — the primary patent alone — so the two can be read side by side."""
    w = _force_frame(ds, v, max_year)
    g = w.groupby("topType").agg(**{"unique aircraft": ("aircraft_id", "size"),
                                    "out of force": ("out", "sum"), "_old": ("lapsed", "mean")})
    g["out of force share"] = (g["out of force"] / g["unique aircraft"]).round(2)
    g["out of force, primary patent only"] = g["_old"].round(2)
    g.index = [metrics.ARCH_NAMES.get(c, c) for c in g.index]
    g.index.name = "class"
    g = g.reset_index().sort_values(["unique aircraft", "class"], ascending=[False, True])
    allrow = pd.DataFrame({"class": ["all classes"], "unique aircraft": [len(w)],
                           "out of force": [int(w["out"].sum())],
                           "out of force share": [round(float(w["out"].mean()), 2)],
                           "out of force, primary patent only": [round(float(w["lapsed"].mean()), 2)]})
    cols = ["class", "unique aircraft", "out of force", "out of force share",
            "out of force, primary patent only"]
    out = pd.concat([g[cols], allrow], ignore_index=True)
    out["out of force"] = out["out of force"].astype(int)
    links = w.attrs["links"]
    linked = links[links["aircraft_id"].isin(set(w["aircraft_id"]))]
    out.attrs.update(
        max_year=max_year, unread=w.attrs["unread"],
        flipped_to_in_force=int((w["lapsed"] & ~w["out"]).sum()),
        flipped_to_out=int((~w["lapsed"] & w["out"]).sum()),
        patents_per_aircraft=w["linked"].astype(int).value_counts().sort_index().to_dict(),
        linked_patents=int(linked["patent_id"].nunique()),
        linked_without_status=int((~linked["status_known"]).sum()),
        source="PatSeer legal_status_raw at the snapshot (2026-06-08) · human labelling (class, duplicates)")
    return out


def force_aircraft_test(ds: Dataset, v: pd.DataFrame, max_year: int = FORCE_MAX_YEAR,
                        min_n: int = FORCE_TEST_MIN) -> pd.DataFrame:
    """Chi-square test of class x out-of-force over the classes with ``min_n`` aircraft or more,
    under the new reading (every linked patent), the old one (primary patent only), and a
    SENSITIVITY row: the new reading with a multi-target duplicate linked to its first target only
    (the loader's domain-gate rule) — all on the same aircraft. ``attrs["mr_first_only"]`` holds
    the Multirotor share under that sensitivity reading."""
    from scipy.stats import chi2_contingency
    w = _force_frame(ds, v, max_year)
    w1 = _force_frame(ds, v, max_year, first_only=True).set_index("aircraft_id")["out"]
    w["out_first"] = w["aircraft_id"].map(w1).astype(bool)
    size = w.groupby("topType").size()
    keep = w[w["topType"].isin(size[size.ge(min_n)].index)]
    rows = []
    for reading, col in (("every linked patent INACTIVE (this reading)", "out"),
                         ("primary patent INACTIVE (the 1.1.10 reading)", "lapsed"),
                         ("every linked patent INACTIVE, multi-target duplicates to first target only",
                          "out_first")):
        tab = pd.crosstab(keep["topType"], keep[col])
        chi2, p, dof, _ = chi2_contingency(tab.values)
        rows.append({"reading": reading, "classes tested": int(tab.shape[0]),
                     "aircraft": int(len(keep)), "out of force": int(keep[col].sum()),
                     "out of force share": round(float(keep[col].mean()), 2),
                     "chi2": round(float(chi2), 2), "dof": int(dof), "p": float(p)})
    out = pd.DataFrame(rows)
    mr = w[w["topType"].eq("MR")]
    out.attrs.update(mr_first_only=(round(float(mr["out_first"].mean()), 2) if len(mr) else float("nan")),
                     flipped_first_only=int((w["lapsed"] & ~w["out_first"]).sum()))
    out.attrs.update(min_n=min_n, classes=[metrics.ARCH_NAMES.get(c, c) for c in
                                           size[size.ge(min_n)].sort_values(ascending=False).index])
    return out


# --------------------------------------------------------------------------- Figure 1 (ii) values
def baseline_multiples(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """The values drawn in Figure 1 (ii), one row per complete priority year (2026-09-26).

    eVTOL's SHARE of each baseline relative to its own 2005-09 share (= 1): the corpus's acquired
    patents (all 1 639 PatSeer simple families) over PatSeer CPC B64 and CPC section B worldwide
    simple families and over WIPO patent families by origin (all patents). Computed by
    :func:`la_baseline.multiples`, the function the figure itself draws from, so the brief can
    quote the figure's numbers as placeholders. A share multiple is not a growth-rate ratio: the
    latter is ``la_doubling_ratio``.
    """
    full = la_tables.filings_per_year(ds, v).set_index("priority year")
    m = la_baseline.multiples(full)
    out = m.rename(columns=la_baseline.MULTIPLE_LABELS).round(1)
    out.index.name = "priority year"
    out = out.reset_index()
    out.attrs["source"] = la_baseline.SOURCE
    out.attrs["base_years"] = la_baseline.BASE_YEARS
    return out


# --------------------------------------------------------------------------- growth rates
# 2026-09-26, author's ruling on Figure 1 (ii): the panel shows GROWTH RATES, not eVTOL's share
# of each baseline — a share multiple of one year against a base period is a level, and it was
# being read as a speed. eVTOL is counted twice: as patent families (the representative patents,
# the same unit as the three baselines, so the comparison is like for like) and as unique
# aircraft (the brief's own unit: distinct designs).
GROWTH_WINDOW: Tuple[int, int] = FIT_WINDOW
GROWTH_SENSITIVITY: Tuple[int, int] = (2005, 2019)

#: (key, printed name) in the order the table and the figure print them
GROWTH_SERIES: List[Tuple[str, str]] = [
    ("evtol_families", "eVTOL patent families"),
    ("evtol_aircraft", "eVTOL unique aircraft"),
    ("b64", "aeronautics (CPC B64)"),
    ("secb", "transport and operations (CPC section B)"),
    ("all", "all patents"),
]


def growth_series(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.Series]:
    """Count per priority year of every series the growth comparison reads, keyed as
    :data:`GROWTH_SERIES`. The eVTOL families are the patents that describe an electric VTOL
    aircraft (the representative patents), each one PatSeer simple family."""
    pid = set(ds.approved_variants["patent_id"].astype(str))
    rep = ds.identity[ds.identity["patent_id"].astype(str).isin(pid)]
    fam = (pd.to_numeric(rep["priority_year"], errors="coerce").dropna().astype(int)
           .value_counts().sort_index())
    ac = v.dropna(subset=["year"])["year"].astype(int).value_counts().sort_index()
    return {"evtol_families": fam, "evtol_aircraft": ac,
            "b64": la_baseline.series(la_baseline.PATSEER_WORLD).dropna().astype(int),
            "secb": la_baseline.series(la_baseline.PATSEER_WORLD_B).dropna().astype(int),
            "all": la_baseline.series(la_baseline.WIPO_WORLD_ALL).dropna().astype(int)}


def growth_rates(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Doubling time and yearly growth of every series, fitted on the complete priority years."""
    ser = growth_series(ds, v)
    names = dict(GROWTH_SERIES)
    rows = []
    for lo, hi in (GROWTH_WINDOW, GROWTH_SENSITIVITY):
        for key, _ in GROWTH_SERIES:
            yrs, cnt = _window_frame(ser[key], lo, hi)
            fit = _loglin(yrs, cnt)
            if not fit:
                continue
            rows.append({"series": names[key], "key": key, "window": f"{lo}–{hi}",
                         "total": int(cnt.sum()),
                         "doubling time (years)": round(fit["doubling time (years)"], 1),
                         "95 % interval": f"{fit['doubling low']:.1f} to {fit['doubling high']:.1f}",
                         "growth per year": f"{fit['growth per year %']:.0f} %",
                         "shape": _fit_shape(fit),
                         "primary": (lo, hi) == GROWTH_WINDOW})
    return pd.DataFrame(rows)


def growth_ratios(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """How many times faster each eVTOL count grows than each baseline, with the paired
    bootstrap over years of :func:`doubling_ratio` (same draws, same seed)."""
    ser = growth_series(ds, v)
    names = dict(GROWTH_SERIES)
    rng = np.random.default_rng(SEED)
    rows = []
    for lo, hi in (GROWTH_WINDOW, GROWTH_SENSITIVITY):
        for top_key in ("evtol_families", "evtol_aircraft"):
            yrs, top = _window_frame(ser[top_key], lo, hi)
            for base_key in ("b64", "secb", "all"):
                _, base = _window_frame(ser[base_key], lo, hi)
                ft, fb = _loglin(yrs, top), _loglin(yrs, base)
                if not ft or not fb:
                    continue
                ratio = fb["doubling time (years)"] / ft["doubling time (years)"]
                d = []
                for _ in range(DRAWS):
                    ix = rng.integers(0, len(yrs), len(yrs))
                    if len(np.unique(yrs[ix])) < 4:
                        continue
                    a, b = _loglin(yrs[ix], top[ix]), _loglin(yrs[ix], base[ix])
                    if not a or not b or a["slope (log count per year)"] <= 0 \
                            or b["slope (log count per year)"] <= 0:
                        continue
                    d.append(b["doubling time (years)"] / a["doubling time (years)"])
                d = np.array(d)
                lo_ci, hi_ci = (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))) \
                    if len(d) > 50 else (np.nan, np.nan)
                rows.append({"eVTOL counted as": names[top_key], "against": names[base_key],
                             "window": f"{lo}–{hi}",
                             "times as fast": round(ratio, 2),
                             "95 % interval": f"{lo_ci:.2f} to {hi_ci:.2f}",
                             "reading": ("faster" if lo_ci > 1 else
                                         "cannot be told apart" if hi_ci >= 1 else "slower"),
                             "primary": (lo, hi) == GROWTH_WINDOW})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- evtol.news check
# 2026-09-26, comments C44-C46: the class mix per window checked against an outside series. The
# author's dated evtol.news set (World eVTOL Aircraft Directory, crawled 2026-09-17; development
# year read by two independent LLM readers, disagreements ruled by the author) gives the directory
# a time axis, so the corpus's class shares per priority window can be set beside the directory's
# shares per development-year window, both on the directory's five classes. The corpus's twelve
# classes are folded with ``la_tables.FOLD5`` (ruling 2026-09-22), the same fold every other
# evtol.news comparison of the document uses.
EVN_YEARS = la_tables.EVTOLNEWS / "0_source" / "years" / "aircraft_dev_year.csv"
#: the author's rulings on the readers' disagreements, exported by ``dev_year_review.html``
#: (columns slug_key, year, evidence_id). Read from the first place it is found; absent = none yet.
EVN_DECISIONS = [la_tables.EVTOLNEWS / "0_source" / "years" / "DEV_YEAR_DECISIONS.csv",
                 la_tables.EVTOLNEWS.parent / "1639_LABELLED" / "review_decisions" / "DEV_YEAR_DECISIONS.csv"]
EVN_SOURCES: List[Tuple[str, str]] = [
    ("patent", "patent corpus (unique aircraft, priority year)"),
    ("directory", "evtol.news directory (aircraft, development year)"),
]
#: class order of every table and panel: the two classes the crossover is about first
CLASS5_ORDER: List[str] = ["LC", "VT", "WM", "ER", "HB"]
#: a window is compared only when both sources hold this many dated aircraft in it
EVN_MIN_N: int = 30


def evtolnews_years() -> pd.DataFrame:
    """The directory's 1 229 aircraft with their FINAL development year.

    The final year (THESIS_METHOD_TEXT.md, step 4): the readers' common year when both gave the
    same one (``dev_year_status`` "agreed", ``dev_year`` filled), none when both found none
    ("not_stated"), and the author's ruling where they disagreed ("conflict"). A conflict without a
    ruling has no final year and is counted apart (``year_basis`` "conflict, not yet ruled"); an
    author's ruling that is not a year ("not stated", "none") makes the aircraft undated.
    """
    d = pd.read_csv(EVN_YEARS)
    d["year"] = pd.to_numeric(d["dev_year"], errors="coerce")
    d["year_basis"] = np.where(d["year"].notna(), "agreed by both readers",
                               np.where(d["dev_year_status"].eq("conflict"), "conflict, not yet ruled",
                                        "not stated on the page"))
    ruled = next((p for p in EVN_DECISIONS if p.exists()), None)
    if ruled is not None:
        r = pd.read_csv(ruled, dtype=str, keep_default_na=False)
        r = r[r["slug_key"].isin(set(d.loc[d["dev_year_status"].eq("conflict"), "slug_key"]))]
        r = r[r["year"].str.strip().ne("")].set_index("slug_key")["year"]
        hit = d["slug_key"].isin(r.index)
        d.loc[hit, "year"] = pd.to_numeric(d.loc[hit, "slug_key"].map(r), errors="coerce")
        d.loc[hit, "year_basis"] = np.where(d.loc[hit, "year"].notna(), "ruled by the author",
                                            "ruled by the author: not stated")
    d["window"] = d["year"].map(la_tables.a2.window_of)
    d.attrs["decisions"] = str(ruled) if ruled is not None else None
    return d


def _evn_long(v: pd.DataFrame) -> pd.DataFrame:
    """Both sources stacked: one row per dated, classed aircraft with ``source`` / ``window`` /
    ``class5``. The corpus side is every unique aircraft with a class and a priority window."""
    p = v.dropna(subset=["window", "class5"])[["window", "class5"]].assign(source="patent")
    d = evtolnews_years().dropna(subset=["window"])
    d = d[["window", "evtol_class"]].rename(columns={"evtol_class": "class5"}).assign(source="directory")
    return pd.concat([p, d], ignore_index=True)


def evtolnews_check(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Count and share of each of the five directory classes per window, for the corpus (unique
    aircraft by priority year, twelve classes folded by ``la_tables.FOLD5``) and for the
    directory (aircraft by development year). One row per (source, window, class)."""
    long = _evn_long(v)
    names = dict(EVN_SOURCES)
    rows = []
    for src, _ in EVN_SOURCES:
        s = long[long["source"].eq(src)]
        for w in la_tables.WINDOW_NAMES:
            sw = s[s["window"].eq(w)]
            n = len(sw)
            for c in CLASS5_ORDER:
                k = int(sw["class5"].eq(c).sum())
                rows.append({"source": names[src], "window": w, "class": la_tables.FOLD5_NAMES[c],
                             "code": c, "aircraft": k, "window total": n,
                             "share": round(k / n, 3) if n else float("nan")})
    out = pd.DataFrame(rows)
    out.attrs["fold"] = dict(la_tables.FOLD5)
    return out


def evtolnews_compare(ds: Dataset, v: pd.DataFrame, min_n: int = EVN_MIN_N) -> pd.DataFrame:
    """One row per window: the two sources side by side on the two classes of the crossover,
    and two tests where both hold ``min_n`` dated aircraft or more.

    * χ² of source x five classes: are the two class mixes told apart at all;
    * Fisher's exact test on source x (Lift + Cruise, Vectored Thrust), the aircraft of those two
      classes only: is the BALANCE between the two classes of the crossover told apart;
    * the larger of the two classes in each source, and whether it is the same one.
    """
    from scipy.stats import chi2_contingency, fisher_exact
    long = _evn_long(v)
    rows = []
    for w in la_tables.WINDOW_NAMES:
        lw = long[long["window"].eq(w)]
        tab = pd.crosstab(lw["source"], lw["class5"]).reindex(
            index=[s for s, _ in EVN_SOURCES], columns=CLASS5_ORDER, fill_value=0)
        n_p, n_d = int(tab.loc["patent"].sum()), int(tab.loc["directory"].sum())
        row = {"window": w, "patent aircraft": n_p, "directory aircraft": n_d}
        for src, lab in (("patent", "patent"), ("directory", "directory")):
            n = tab.loc[src].sum()
            for c in ("LC", "VT"):
                row[f"{la_tables.FOLD5_NAMES[c]} share, {lab}"] = round(tab.loc[src, c] / n, 3) if n else np.nan
            lcvt = tab.loc[src, "LC"] + tab.loc[src, "VT"]
            row[f"Lift + Cruise of (LC + VT), {lab}"] = round(tab.loc[src, "LC"] / lcvt, 3) if lcvt else np.nan
            row[f"larger of LC / VT, {lab}"] = ("Lift + Cruise" if tab.loc[src, "LC"] > tab.loc[src, "VT"]
                                                else "Vectored Thrust" if tab.loc[src, "VT"] > tab.loc[src, "LC"]
                                                else "tie")
        row["same order"] = "yes" if row["larger of LC / VT, patent"] == row["larger of LC / VT, directory"] else "no"
        tested = n_p >= min_n and n_d >= min_n
        if tested:
            t = tab.loc[:, tab.sum(axis=0).gt(0)]
            chi2, p, dof, _ = chi2_contingency(t.values)
            row.update({"chi2 (5 classes)": round(float(chi2), 1), "dof": int(dof), "p (5 classes)": float(p)})
            _, pf = fisher_exact(tab[["LC", "VT"]].values)
            row["p (LC vs VT balance)"] = float(pf)
        else:
            row.update({"chi2 (5 classes)": np.nan, "dof": np.nan, "p (5 classes)": np.nan,
                        "p (LC vs VT balance)": np.nan})
        row["tested"] = tested
        row["partial"] = "partial" in w
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs["min_n"] = min_n
    return out


#: the two ends the brief reads the crossover between (earliest window -> last complete window)
EVN_ENDS: Tuple[str, str] = (la_tables.WINDOW_NAMES[0], "2020-23")


def evtolnews_class_verdict(ds: Dataset, v: pd.DataFrame, ends: Tuple[str, str] = EVN_ENDS) -> pd.DataFrame:
    """One row per directory class: its share at the two ends the brief reads (the earliest window
    and 2020-23) in each source, the direction of the change in each, whether the directions
    agree, and two Fisher tests — the change inside each source (class vs rest x first vs last
    window) and the level of the two sources in the last window (class vs rest x source)."""
    from scipy.stats import fisher_exact
    long = _evn_long(v)
    a, b = ends
    rows = []
    for c in CLASS5_ORDER:
        row = {"class": la_tables.FOLD5_NAMES[c], "code": c}
        dirs = {}
        for src, lab in (("patent", "patent"), ("directory", "directory")):
            s = long[long["source"].eq(src)]
            k = [int(s[s["window"].eq(w)]["class5"].eq(c).sum()) for w in (a, b)]
            n = [int(s["window"].eq(w).sum()) for w in (a, b)]
            sh = [k[i] / n[i] if n[i] else np.nan for i in range(2)]
            row[f"{lab} {a}"] = round(sh[0], 3)
            row[f"{lab} {b}"] = round(sh[1], 3)
            dirs[src] = "up" if sh[1] > sh[0] else "down" if sh[1] < sh[0] else "flat"
            row[f"{lab} change"] = dirs[src]
            row[f"p change, {lab}"] = float(fisher_exact([[k[0], n[0] - k[0]], [k[1], n[1] - k[1]]])[1])
        row["same direction"] = "yes" if dirs["patent"] == dirs["directory"] else "no"
        s = long[long["window"].eq(b)]
        kp = int(((s["source"] == "patent") & s["class5"].eq(c)).sum())
        kd = int(((s["source"] == "directory") & s["class5"].eq(c)).sum())
        np_, nd = int(s["source"].eq("patent").sum()), int(s["source"].eq("directory").sum())
        row[f"p level {b}, patent vs directory"] = float(fisher_exact([[kp, np_ - kp], [kd, nd - kd]])[1])
        rows.append(row)
    return pd.DataFrame(rows)


def evtolnews_coverage() -> pd.DataFrame:
    """How many directory aircraft carry a final development year, per class: the base of the
    directory panel and what it leaves out."""
    d = evtolnews_years()
    bases = ["agreed by both readers", "ruled by the author", "conflict, not yet ruled",
             "not stated on the page", "ruled by the author: not stated"]
    t = pd.crosstab(d["evtol_class"], d["year_basis"]).reindex(index=CLASS5_ORDER, columns=bases, fill_value=0)
    t = t.loc[:, t.sum(axis=0).gt(0) | t.columns.isin(bases[:4])]
    t.index = [la_tables.FOLD5_NAMES[c] for c in t.index]
    t.loc["all classes"] = t.sum(axis=0)
    t.insert(0, "aircraft on the list", t.sum(axis=1))
    dated = t[[c for c in ("agreed by both readers", "ruled by the author") if c in t.columns]].sum(axis=1)
    t["dated (in the panel)"] = dated
    t["undated (left out)"] = t["aircraft on the list"] - dated
    t["dated share"] = (dated / t["aircraft on the list"]).round(3)
    t.index.name = "directory class"
    out = t.reset_index()
    out.attrs["decisions"] = d.attrs.get("decisions")
    return out


# --------------------------------------------------------------------------- chapter 2
#: the archetype levels the brief reads (2026-09-26, chapter-2 review C48/C49/C54): the three
#: levels that pass or anchor the screens, plus the post-hoc Lift + Cruise family (definition
#: (b)) as one more level. Old level id -> the words the brief prints for what it combines.
BRIEF_LEVELS: Tuple[Tuple[str, str], ...] = (
    ("A0", "architecture class"),
    ("A1t", "class · number of wings · whether any propulsor tilts"),
    ("A0c", "class · propulsive-unit band (1-3 / 4 / 5-6 / 7-8 / 9 or more)"),
    ("family_b", "class, with Lift + Cruise and the CVT whose tilting part is a rotor set "
                 "(no tilting wing) merged into one family"),
)
FAMILY_LABEL = "Lift + Cruise family"


def archetype_levels_brief(ds: Dataset, v: pd.DataFrame,
                           levels: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """The archetype levels the brief reads, one row each, with readable names (C47, C49).

    The rows C, C·U and C·W·T are :func:`la_tables.archetype_levels` as it is — the same counts,
    the same unrarefied ¹D over the whole corpus — and the fourth row is the family level F:
    every aircraft keeps its class, except that Lift + Cruise and the CVT aircraft of family
    definition (b) (:func:`la_tables.family_mask`) share one archetype. Post hoc, like every
    family result (:data:`la_tables.FAMILY_POSTHOC`).
    """
    from . import sm_text_methods as _tm
    lv = levels if levels is not None else la_tables.archetype_levels(ds, v)
    lv = lv.set_index("level")
    rows = []
    for level, combines in BRIEF_LEVELS:
        code, name = _tm.LEVEL_CODES[level]
        if level in lv.index:
            r = lv.loc[level]
            n = int(r["aircraft"])
            rows.append({"level id": level, "level": f"{code} — {name}", "combines": combines,
                         "aircraft": n, "archetypes": int(r["archetypes"]),
                         "aircraft alone in their archetype": int(r["singletons"]),
                         "effective number ¹D": float(r["effective number ¹D"]),
                         "largest archetype": _tm.archetype_label(r["largest archetype"], level),
                         "its share": float(r["largest share"]),
                         "archetypes of five or more": int(r["archetypes of five or more"])})
            continue
        flags = la_tables.family_flags(ds, v)
        flags = flags[flags["topType"].notna()].copy()
        fam = la_tables.family_mask(flags, "b")
        key = flags["topType"].astype(str).where(~fam, FAMILY_LABEL)
        counts = key.value_counts()
        shares = counts / counts.sum()
        top = str(counts.index[0])
        rows.append({"level id": level, "level": f"{code} — {name}", "combines": combines,
                     "aircraft": int(counts.sum()), "archetypes": int(len(counts)),
                     "aircraft alone in their archetype": int((counts == 1).sum()),
                     "effective number ¹D": round(float(np.exp(-(shares * np.log(shares)).sum())), 1),
                     "largest archetype": top if top == FAMILY_LABEL else _tm.archetype_label(top, "A0"),
                     "its share": round(float(shares.iloc[0]), 3),
                     "archetypes of five or more": int((counts >= 5).sum())})
    return pd.DataFrame(rows)


def archetype_filer_split(v: pd.DataFrame, min_aircraft: int = 20) -> pd.DataFrame:
    """What "few filers per aircraft" is made of, per class · propulsive-unit archetype (C·U)
    holding ``min_aircraft`` or more (C71): the largest filer and how many of the archetype's
    aircraft it holds, and how many filers hold a single one. Filers counted as
    :func:`la_tables.zones` counts them (``filer_id``: a firm, or an individual inventor's
    patent as its own filer), so the aircraft and filer columns reproduce ``la_zones``."""
    w = v.dropna(subset=["archetype"])
    rows = []
    for a, sub in w.groupby("archetype"):
        if len(sub) < min_aircraft:
            continue
        held = sub.groupby("filer_id").size().sort_values(ascending=False)
        top = str(held.index[0])
        rows.append({"archetype": a, "aircraft": int(len(sub)), "filers": int(len(held)),
                     "filers per aircraft": round(float(len(held) / len(sub)), 2),
                     "largest filer": ("one patent's inventor" if top.startswith("patent:") else top),
                     "its aircraft": int(held.iloc[0]),
                     "filers holding one aircraft": int((held == 1).sum())})
    return (pd.DataFrame(rows).sort_values("filers per aircraft").reset_index(drop=True))


# --------------------------------------------------------------------------- chapter 3 (3.2)
# 2026-09-26, chapter-3 review (C53, C54, C57): the dominant-design test read at the four levels
# the brief uses (C, C·W·T, C·U and the post-hoc family F), with condition 1 read PER PRIORITY
# YEAR on the author's ruling — two consecutive years above 50 %, main base the aircraft with at
# least one patent in force, second base every aircraft of the year. Conditions 2 and 3 keep
# their windows. Nothing in ``la_tables`` is modified: the pre-registered numbers at C·U and
# C·W·T are ``la_tables.dominant_design`` / ``dominant_design_q`` as they are, and the two added
# levels run the same routine on the same seed.
#: the four levels, in the order the brief prints them (old level id; ``family_b`` = F)
DD_LEVELS: Tuple[str, ...] = ("A0", "A1t", "A0c", "family_b")
#: the years drawn in the yearly figure, and the last one read (the publication lag, chapter 1)
DD_YEAR_FIRST: int = 2008
DD_YEAR_LAST: int = la_tables.LAST_COMPLETE
#: a year is read for condition 1 when its base holds this many aircraft (the trend minimum
#: every per-year reading of the document uses)
DD_YEAR_MIN: int = la_tables.TREND_MIN
#: the two bases of condition 1, main first
DD_BASES: Tuple[Tuple[str, str], ...] = (("in force", "aircraft with a patent in force"),
                                          ("all", "all aircraft of the year"))


def _patent_state(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Per unique aircraft: ``in_force`` — at least one linked patent (primary or duplicate,
    :func:`aircraft_patents`) whose PatSeer status is known and not INACTIVE, i.e. granted and
    alive or still pending (the chapter-1 reading); ``granted_live`` — at least one linked patent
    granted and alive (``ACTIVE - GRANTED``)."""
    links = aircraft_patents(ds, v)
    links["_live"] = links["status_known"] & ~links["inactive"]
    links["_gl"] = links["legal_status_raw"].fillna("").astype(str).str.strip().eq("ACTIVE - GRANTED")
    per = links.groupby("aircraft_id").agg(in_force=("_live", "any"), granted_live=("_gl", "any"))
    out = v[["aircraft_id"]].join(per, on="aircraft_id")
    return out.fillna({"in_force": False, "granted_live": False}).set_index("aircraft_id")


def _level_keys(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.Series]:
    """The archetype of every aircraft at each of :data:`DD_LEVELS` (index = ``v``'s), blank
    where the level cannot name it. F: every aircraft keeps its class, except that the aircraft
    of family definition (b) share one archetype (:func:`archetype_levels_brief`)."""
    keys = {lvl: la_tables._archetype_key(v, lvl) for lvl in DD_LEVELS if lvl != "family_b"}
    flags = la_tables.family_flags(ds, v)
    fam_ids = set(flags.loc[la_tables.family_mask(flags, "b"), "aircraft_id"])
    f = v["topType"].astype(object).where(~v["aircraft_id"].isin(fam_ids), FAMILY_LABEL)
    keys["family_b"] = f.where(v["topType"].notna())
    return keys


def _level_word(level: str) -> str:
    from . import sm_text_methods as _tm
    code, name = _tm.LEVEL_CODES[level]
    return f"{code} — {name}"


def _key_word(key, level: str) -> str:
    from . import sm_text_methods as _tm
    if key == FAMILY_LABEL or level == "family_b":
        return str(key) if key == FAMILY_LABEL else _tm.archetype_label(key, "A0")
    return _tm.archetype_label(key, level)


def dd_yearly(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Condition 1 per priority year: the largest archetype's share of the year, at each level
    and on both bases. One row per (level, base, year), 2008-2023; ``read`` marks the years with
    :data:`DD_YEAR_MIN` aircraft or more on that base."""
    state = _patent_state(ds, v)
    keys = _level_keys(ds, v)
    rows = []
    for level in DD_LEVELS:
        k = keys[level]
        w = v.assign(_k=k)[k.notna()]
        w = w.assign(_live=w["aircraft_id"].map(state["in_force"]).astype(bool))
        for base, _desc in DD_BASES:
            b = w[w["_live"]] if base == "in force" else w
            for y in range(DD_YEAR_FIRST, DD_YEAR_LAST + 1):
                sub = b[b["year"].eq(y)]
                n = int(len(sub))
                if n:
                    vc = sub["_k"].value_counts()
                    top, k1 = str(vc.index[0]), int(vc.iloc[0])
                    tied = int((vc == k1).sum()) > 1
                else:
                    top, k1, tied = "", 0, False
                rows.append({"level id": level, "level": _level_word(level), "base": base,
                             "priority year": y, "aircraft": n,
                             "largest archetype": _key_word(top, level) if n else "",
                             "its aircraft": k1, "its share": round(k1 / n, 4) if n else np.nan,
                             "tied": tied, "read": n >= DD_YEAR_MIN,
                             "above 50 %": bool(n >= DD_YEAR_MIN and k1 / n > 0.5)})
    return pd.DataFrame(rows)


def family_yearly(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """The family F's share of each priority year, 2008-2023, on both bases of condition 1, with
    the share of the in-force aircraft that hold a GRANTED live patent — the measure of how far a
    year's in-force base is still a base of pending applications (C53)."""
    state = _patent_state(ds, v)
    f = _level_keys(ds, v)["family_b"]
    w = v.assign(_f=f.eq(FAMILY_LABEL))[f.notna()]
    w = w.assign(_live=w["aircraft_id"].map(state["in_force"]).astype(bool),
                 _gl=w["aircraft_id"].map(state["granted_live"]).astype(bool))
    rows = []
    for y in range(DD_YEAR_FIRST, DD_YEAR_LAST + 1):
        s = w[w["year"].eq(y)]
        live = s[s["_live"]]
        gl = s[s["_gl"]]
        n, nl, ng = len(s), len(live), len(gl)
        rows.append({"priority year": y, "aircraft": n, "F aircraft": int(s["_f"].sum()),
                     "F share": round(float(s["_f"].mean()), 4) if n else np.nan,
                     "aircraft in force": nl, "F aircraft in force": int(live["_f"].sum()),
                     "F share in force": round(float(live["_f"].mean()), 4) if nl else np.nan,
                     "in force with a granted patent": round(ng / nl, 4) if nl else np.nan,
                     "F share, granted and live": round(float(gl["_f"].mean()), 4) if ng else np.nan,
                     "read, in force": nl >= DD_YEAR_MIN, "read, all": n >= DD_YEAR_MIN})
    out = pd.DataFrame(rows)
    out.attrs.update(note=la_tables.FAMILY_POSTHOC, year_min=DD_YEAR_MIN)
    return out


def dd_balance(ds: Dataset, v: pd.DataFrame, n: int = 40, perms: int = 200,
               seed: int = 42) -> pd.DataFrame:
    """Condition 2 at the four levels: rarefied ²D per window against the permutation band.

    C·U and C·W·T are :func:`la_tables.dominant_design` as it is (the pre-registered test, same
    numbers as ``la_dominant_design``); C and F run the same routine — archetypes shuffled across
    the windows, window sizes kept, ``perms`` shuffles, ²D rarefied to ``n`` aircraft — on their
    own archetypes, each level on a generator seeded afresh with ``seed``."""
    pre = la_tables.dominant_design(v, n=n, perms=perms, seed=seed)
    keys = _level_keys(ds, v)
    w0 = v.dropna(subset=["window"])
    rows = []
    for level in DD_LEVELS:
        if level in set(pre["level"]):
            for r in pre[pre["level"].eq(level)].to_dict("records"):
                rows.append(r)
            continue
        rng = np.random.default_rng(seed)
        k = keys[level].loc[w0.index]
        ww = w0[k.notna()].assign(key=k[k.notna()])
        obs = {}
        for name in la_tables.WINDOW_NAMES:
            sub = ww[ww["window"].eq(name)]
            if len(sub) < 10:
                continue
            h = la_tables.hill_numbers(sub["key"], n=n, draws=300)
            top = sub["key"].value_counts(normalize=True)
            obs[name] = {"level": level, "window": name, "aircraft": int(len(sub)),
                         "top archetype": top.index[0], "top share": round(float(top.iloc[0]), 3),
                         "top-2 share": round(float(top.iloc[:2].sum()), 3),
                         "D2": h["D2"], "D2 low": h["D2 low"], "D2 high": h["D2 high"]}
        band = {name: [] for name in obs}
        pool = ww["key"].to_numpy()
        for _ in range(perms):
            shuffled = rng.permutation(pool)
            for name in obs:
                mask = ww["window"].eq(name).to_numpy()
                band[name].append(la_tables.hill_numbers(pd.Series(shuffled[mask]), n=n, draws=40,
                                                         seed=int(rng.integers(1e9)))["D2"])
        for name, r in obs.items():
            b = np.array(band[name])
            r["D2 permutation low"] = round(float(np.percentile(b, 2.5)), 2)
            r["D2 permutation high"] = round(float(np.percentile(b, 97.5)), 2)
            r["below band"] = bool(r["D2"] < r["D2 permutation low"])
            r["condition 1 (> 50 %)"] = bool(r["top share"] > 0.5)
            rows.append(r)
    out = pd.DataFrame(rows)
    out.insert(1, "level name", out["level"].map(_level_word))
    out["top archetype"] = [_key_word(a, l) for a, l in zip(out["top archetype"], out["level"])]
    out["partial"] = out["window"].astype(str).str.contains("partial")
    return out


def dd_form(ds: Dataset, v: pd.DataFrame, perms: int = 200, seed: int = 42) -> pd.DataFrame:
    """Condition 3 at the four levels. Q uses no archetype, so a level changes it only through
    the aircraft it can name: C and F name every aircraft with a class (F only regroups them),
    C·U the same aircraft, C·W·T two fewer in 2020-23. :func:`la_tables.dominant_design_q` is run
    at C, C·U and C·W·T (the last two are the pre-registered rows, same numbers as ``la_dd_q``)
    and F is C's row, relabelled — the identical computation on the identical aircraft."""
    q = la_tables.dominant_design_q(ds, v, levels=("A0", "A1t", "A0c"), perms=perms, seed=seed)
    f = q[q["level"].eq("A0")].assign(level="family_b")
    out = pd.concat([q, f], ignore_index=True)
    out.insert(1, "level name", out["level"].map(_level_word))
    out["partial"] = out["window"].astype(str).str.contains("partial")
    order = {lvl: i for i, lvl in enumerate(DD_LEVELS)}
    out = out.sort_values(["weighting", "level", "window"], key=lambda s: s.map(order) if s.name == "level"
                          else (s.map({w: i for i, w in enumerate(la_tables.WINDOW_NAMES)})
                                if s.name == "window" else s))
    return out.reset_index(drop=True)


def _pct1(x: float) -> str:
    return f"{100 * x:.1f} %"


def _consecutive(years: List[int]) -> List[Tuple[int, int]]:
    ys = sorted(years)
    return [(a, b) for a, b in zip(ys[:-1], ys[1:]) if b == a + 1]


def dd_levels(yearly: pd.DataFrame, balance: pd.DataFrame, form: pd.DataFrame) -> pd.DataFrame:
    """The verdict, one row per condition and one column per level, each cell naming WHERE the
    condition is met (C54, C57): the years for condition 1, the windows for conditions 2 and 3,
    complete windows only. The last row asks the three in the same period: condition 1's two
    years inside a window where conditions 2 and 3 are both met."""
    complete = [w for w in la_tables.WINDOW_NAMES if "partial" not in w]
    main = la_tables.Q_WEIGHTINGS[0]
    alt = la_tables.Q_WEIGHTINGS[1]
    cells: Dict[str, Dict[str, str]] = {}
    met_where: Dict[str, Dict[str, set]] = {}
    for level in DD_LEVELS:
        c: Dict[str, str] = {}
        m: Dict[str, set] = {}
        # condition 1, per year, on both bases
        y = yearly[yearly["level id"].eq(level)]
        parts, years_met = [], set()
        for base, _d in DD_BASES:
            b = y[y["base"].eq(base) & y["read"].astype(bool)]
            over = b[b["above 50 %"].astype(bool)]
            pairs = _consecutive(over["priority year"].astype(int).tolist())
            if pairs:
                ys = sorted({x for p in pairs for x in p})
                shares = [float(b.loc[b["priority year"].eq(yy), "its share"].iloc[0]) for yy in ys]
                parts.append(f"{base}: met in " + " and ".join(str(x) for x in ys)
                             + " (" + ", ".join(_pct1(s) for s in shares) + ")")
                if base == DD_BASES[0][0]:
                    years_met = set(ys)
            elif len(over):
                # above half in single years only: name them, and the read years beside them
                sh = dict(zip(b["priority year"].astype(int), b["its share"].astype(float)))
                txt = []
                for yy in over["priority year"].astype(int):
                    nb = [f"{x} ({_pct1(sh[x])})" for x in (yy - 1, yy + 1) if x in sh]
                    txt.append(f"{yy} ({_pct1(sh[yy])})" + (", not " + " or ".join(nb) if nb else ""))
                parts.append(f"{base}: no — above half only in " + "; ".join(txt))
            else:
                top = b.loc[b["its share"].astype(float).idxmax()]
                parts.append(f"{base}: no — at most {_pct1(float(top['its share']))} "
                             f"({int(top['priority year'])})")
        c["1"] = "; ".join(parts)
        m["1"] = years_met
        # condition 2, per complete window
        bl = balance[balance["level"].eq(level) & balance["window"].isin(complete)]
        below = bl[bl["below band"].astype(str).eq("True")]["window"].tolist()
        c["2"] = ("met in " + ", ".join(below)) if below else "no"
        m["2"] = set(below)
        # condition 3, per complete window, main weighting; the uniform one beside it
        fm = form[form["level"].eq(level) & form["window"].isin(complete)]
        hit = fm[fm["weighting"].eq(main) & fm["below band"].astype(str).eq("True")]["window"].tolist()
        hit_alt = fm[fm["weighting"].eq(alt) & fm["below band"].astype(str).eq("True")]["window"].tolist()
        if hit:
            only = [w for w in hit if w not in hit_alt]
            c["3"] = "met in " + ", ".join(hit) + (f" ({main} weighting only)" if only else "")
        else:
            c["3"] = "no"
        m["3"] = set(hit)
        # all three: condition 1's years inside a window where 2 and 3 are met
        both = m["2"] & m["3"]
        inside = [w for w in both if m["1"] and all(la_tables.a2.window_of(yy) == w for yy in m["1"])]
        c["all"] = ("met in " + ", ".join(inside)) if inside else "no"
        cells[level] = c
    rows = []
    for cond, label in (("1", "1 — counts: one archetype above 50 % of the aircraft, two consecutive "
                               "priority years"),
                        ("2", "2 — balance: ²D below the permutation band"),
                        ("3", "3 — form: Q below the two earliest windows by more than the band"),
                        ("all", "all three in the same period")):
        row = {"condition": label}
        for level in DD_LEVELS:
            row[_level_word(level)] = cells[level][cond]
        rows.append(row)
    return pd.DataFrame(rows)


def ch3_tables(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """The chapter-3 frames, built together because the verdict reads the other three."""
    yearly, balance, form = dd_yearly(ds, v), dd_balance(ds, v), dd_form(ds, v)
    return {"la_family_yearly": family_yearly(ds, v), "la_dd_yearly": yearly,
            "la_dd_balance": balance, "la_dd_form": form,
            "la_dd_levels": dd_levels(yearly, balance, form)}


# ---------------------------------------------------------------------------------------------
# 2026-09-26 — chapter 3, sections 3.3 and 3.4 (``sm_text_ch3b``): the configurations inside each
# class on the PROPOSED per-class rules (BRIEF_REVISION_RULES §6, C63-C66), and the frames the
# driver figures and sentences read (C79-C95). Every frame reads ``ds.variants`` by the rules of
# :func:`la_tables.trace_frame` — the same M3 override skip, control-only types left out — so a
# tilting set here is the tilting set the driver traces count.
# ---------------------------------------------------------------------------------------------
#: which rule set the brief's figure and prose read. The PROPOSED rules are pending the author's
#: confirmation (§6), so both sets are built into ``la_class_configs_brief`` on every run and this
#: constant only chooses the one printed: "proposed" or "current".
CLASS_RULES_SET: str = "proposed"

#: the windows every chapter-3b frame reports: the four complete ones (no trend past 2023)
CH3B_WINDOWS: List[str] = [w for w in la_tables.WINDOW_NAMES if "partial" not in w]
#: the two early windows, drawn faded and labelled "few aircraft" (§6, driver traces)
CH3B_FEW: List[str] = CH3B_WINDOWS[:2]
#: the classes the drivers read, largest first (the 5-in-3-windows rule of la_tables)
CH3B_CLASSES: List[str] = ["SLC", "TR", "CVT", "TW", "MR"]

#: the station of a propulsor card, in the words a configuration is written in
_CFG_STATION = {"fuselage": "body", "core_layout": "body", "hull_array": "body", "emp": "tail",
                "boom": "booms", "wing1": "wing 1", "wing2": "wing 2", "wing3": "wing 3"}

#: the rules, per rule set and class: (rule as printed, the configuration's categories). The
#: categories are the configurations the rule can produce; an aircraft whose labels fall outside
#: them (a gap in its propulsion record) is kept, as a configuration of its own, but is not
#: counted among the possible ones.
CLASS_RULES_BRIEF: Dict[str, Dict[str, Tuple[str, int]]] = {
    "proposed": {
        "SLC": ("where the lift units sit (booms, wing, body) · stowed in cruise or not", 6),
        "TR": ("tilting sets: one · two or more on one station · two or more on two or more "
               "stations", 3),
        "CVT": ("what tilts (rotors, a wing, both) · where the fixed units sit (booms, "
                "elsewhere, none)", 9),
        "TW": ("wings: one or two or more · propulsive-unit band", 10),
        "MR": ("booms or none · propulsive-unit band", 10),
    },
    "current": {
        "SLC": ("lift units fixed or retracting/folding · propulsive-unit band", 10),
        "TR": ("tilting types: one or two or more · propulsive-unit band", 10),
        "CVT": ("tilting types × fixed types · propulsive-unit band", 0),
        "TW": ("wings: one or two or more · propulsive-unit band", 10),
        "MR": ("booms or none · propulsive-unit band", 10),
    },
}


def config_frame(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Per unique aircraft, the facts the proposed class rules and the driver links are written in.

    * ``sets`` — tilting sets, the ``joints`` trace of :func:`la_tables.trace_frame` itself;
    * ``tilt_stations`` — how many stations carry a tilting type (wing 1 and wing 2 are two);
    * ``what_tilts`` — *rotors tilt* (on their own mounts or on a tilting boom), *a wing tilts*
      (the units ride a tilting wing panel, or a tilting tail surface), both, or nothing recorded;
    * ``fixed_where`` — where the non-tilting units sit: on booms (any), elsewhere, or none;
    * ``lift_where`` — where the fixed lift units sit (a non-tilting type whose thrust axis is
      recorded vertical): on booms, else on the wing, else on the body, else elsewhere;
    * ``stowed`` — a unit retracts or folds its blades in cruise.
    """
    from . import a2
    raw = ds.variants
    ovs = a2.override_sets(raw)
    _s, _n = a2._s, a2._n
    rows = []
    for (_, r), ov in zip(raw.iterrows(), ovs):
        g = lambda c: r[c] if c in r.index else None                       # noqa: E731
        hidden = any(t.startswith("M3:") for t in ov)
        tw = {k for k in range(1, 5) if _s(g(f"wing{k}_tilt")) == "Tilt"}
        bstate = _s(g("boom_thrust_state"))
        boom_tilts = any(_s(g(f"boom{k}_tilts")) == "True" and _s(g(f"boom{k}_hasProps")) != "False"
                         for k in range(1, 7))
        types = []
        for card in la_tables._TRACE_CARDS:
            if f"M3:{card}" in ov:
                continue
            nt = _n(g(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                if _n(g(pre + "count")) <= 0 or _s(g(pre + "ctrlOnly")) == "True":
                    continue
                k = _s(g(pre + "propKin"))
                if card == "boom":
                    how = ("wing" if bstate == "on_tilting_wing" else
                           "rotor" if (boom_tilts or k == "Tilt" or bstate == "tilting") else None)
                elif card.startswith("wing") and int(card[-1]) in tw:
                    how = "wing"
                elif card == "emp" and _s(g("empTilts")) == "True":
                    how = "wing"                    # a tilting tail surface: a surface tilts
                else:
                    how = "rotor" if k == "Tilt" else None
                types.append(dict(st=_CFG_STATION.get(card, card), how=how,
                                  vertical=_s(g(pre + "orient")) in ("Vertical", "Vert"),
                                  stow=_s(g(pre + "rmech")) in ("Retracting", "BladeFold")))
        rec = bool(types) and not hidden
        hows = {t["how"] for t in types if t["how"]}
        lift = {t["st"] for t in types if t["how"] is None and t["vertical"]}
        fixed = {t["st"] for t in types if t["how"] is None}
        rows.append(dict(
            aircraft_id=r["aircraft_id"], recorded=rec,
            tilt_stations=len({t["st"] for t in types if t["how"]}),
            what_tilts=("rotors and a wing tilt" if hows == {"rotor", "wing"} else
                        "rotors tilt" if hows == {"rotor"} else
                        "a wing tilts" if hows == {"wing"} else "tilt not recorded"),
            fixed_where=("fixed units on booms" if "booms" in fixed else
                         "fixed units elsewhere" if fixed else "no fixed unit"),
            any_fixed=bool(fixed),
            lift_where=("on booms" if "booms" in lift else
                        "on the wing" if any(s.startswith("wing") for s in lift) else
                        "on the body" if "body" in lift else
                        "elsewhere" if lift else "not recorded"),
            stowed=any(t["stow"] for t in types)))
    f = pd.DataFrame(rows)
    t = la_tables.trace_frame(ds, v)[["aircraft_id", "joints", "units", "n_types", "on_booms",
                                      "ducted"]]
    out = v[["aircraft_id", "topType", "window", "year"]].merge(t, on="aircraft_id", how="left")
    out = out.merge(f, on="aircraft_id", how="left").rename(columns={"joints": "sets"})
    for c in ("sets", "units", "n_types"):
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def _cfg_key_proposed(r: pd.Series, code: str, band: str) -> str:
    """One aircraft's configuration under the proposed rule of its class, in words."""
    if code == "SLC":
        where = r["lift_where"]
        key = f"lift units {where}" if where != "not recorded" else "lift units not recorded"
        return key + (", stowed in cruise" if r["stowed"] else "")
    if code == "TR":
        s = r["sets"]
        if pd.isna(s) or s < 1:
            return "no tilting set recorded"
        if s < 2:
            return "one tilting set"
        return ("two or more tilting sets, on two or more stations" if r["tilt_stations"] >= 2
                else "two or more tilting sets, on one station")
    if code == "CVT":
        return f"{r['what_tilts']} · {r['fixed_where']}"
    return ""


#: the configurations a proposed rule does not provide for: a gap in the aircraft's propulsion
#: record, kept as a configuration of its own but not counted among the distinct ones
_CFG_GAPS = ("no tilting set recorded", "tilt not recorded", "lift units not recorded",
             "lift units elsewhere")


def _cfg_outside(key: str) -> bool:
    return str(key).startswith(_CFG_GAPS)


def _class_config_keys(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Long frame: one row per (rule set, aircraft of a drawn class with a complete window) and
    its configuration. The current rules are those of :func:`la_tables.class_configs_own`,
    rebuilt field for field so both sets rest on the same aircraft."""
    cf = config_frame(ds, v)
    w = v.dropna(subset=["window", "topType"]).copy()
    w = w[w["topType"].isin(CH3B_CLASSES) & w["window"].isin(CH3B_WINDOWS)]
    u = la_tables._per_aircraft_units(w)
    w["band"] = la_tables.unit_band(w).astype(str)
    w["lift kinematics"] = np.where(u["retracting units"] > 0, "lift units retract/fold", "lift units fixed")
    w["tilting types"] = np.where(u["tilting types"] >= 2, "2+ tilting types", "1 tilting type")
    w["tilt mix"] = (u["tilting types"].astype(int).astype(str) + " tilting × "
                     + u["fixed types"].astype(int).astype(str) + " fixed")
    w["wings"] = np.where(pd.to_numeric(w["wCount"], errors="coerce").fillna(0) >= 2, "2+ wings", "1 wing")
    w["booms"] = np.where(w["nBooms"].fillna(0) > 0, "booms", "no booms")
    cur_fields = {code: fields for code, (_r, fields) in la_tables.CLASS_CONFIG_RULES.items()}
    w = w.merge(cf.drop(columns=["topType", "window", "year"]), on="aircraft_id", how="left")
    rows = []
    for _, r in w.iterrows():
        code = r["topType"]
        cur = " · ".join(str(r[f]) for f in cur_fields[code])
        prop = _cfg_key_proposed(r, code, r["band"]) if code in ("SLC", "TR", "CVT") else cur
        for rs, key in (("proposed", prop), ("current", cur)):
            rows.append({"rule set": rs, "code": code, "window": r["window"],
                         "aircraft_id": r["aircraft_id"], "configuration": key})
    return pd.DataFrame(rows)


def class_configs_brief(ds: Dataset, v: pd.DataFrame,
                        keys: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Section 3.3, per rule set, class and complete window: the rule, the aircraft, the
    configurations the rule allows and those observed, configurations per aircraft, and the most
    common configuration (in words) with the share of the class in it. A window under
    :data:`la_tables.MIN_CELL` aircraft of the class keeps its row with blank measures.

    *Configurations per aircraft* is observed configurations divided by aircraft: 1.0 when every
    aircraft is its own configuration. It cannot exceed ``possible / aircraft``, so under a rule
    that allows few configurations it falls as a window grows even when nothing converges — which
    is why the brief draws the composition (:func:`class_config_mix`) instead of it.
    """
    k = keys if keys is not None else _class_config_keys(ds, v)
    rows = []
    for rs, rules in CLASS_RULES_BRIEF.items():
        for code in CH3B_CLASSES:
            rule, possible = rules[code]
            sub_c = k[k["rule set"].eq(rs) & k["code"].eq(code)]
            for wn in CH3B_WINDOWS:
                sub = sub_c[sub_c["window"].eq(wn)]
                n = int(len(sub))
                gap = sub["configuration"].map(_cfg_outside)
                inside = int(sub.loc[~gap, "configuration"].nunique())
                row = {"rule set": rs, "class": metrics.ARCH_NAMES.get(code, code), "code": code,
                       "window": wn, "rule": rule, "aircraft": n,
                       "possible configurations": possible if possible else np.nan,
                       "distinct configurations": inside,
                       "aircraft outside the rule": int(gap.sum()),
                       "configurations per aircraft": np.nan, "most common configuration": "",
                       "aircraft in it": np.nan, "share in it": np.nan,
                       "few aircraft": wn in CH3B_FEW}
                if n >= la_tables.MIN_CELL:
                    vc = sub["configuration"].value_counts()
                    row.update({"configurations per aircraft": round(inside / n, 3),
                                "most common configuration": str(vc.index[0]),
                                "aircraft in it": int(vc.iloc[0]),
                                "share in it": round(float(vc.iloc[0] / n), 3)})
                rows.append(row)
    return pd.DataFrame(rows)


def class_config_mix(ds: Dataset, v: pd.DataFrame,
                     keys: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """The composition behind :func:`class_configs_brief`: per rule set, class, window and
    configuration, the aircraft and the share of the class-window — what panel (ii) of the
    configuration figure stacks."""
    k = keys if keys is not None else _class_config_keys(ds, v)
    g = k.groupby(["rule set", "code", "window", "configuration"]).size().rename("aircraft").reset_index()
    tot = k.groupby(["rule set", "code", "window"]).size().rename("class aircraft").reset_index()
    g = g.merge(tot, on=["rule set", "code", "window"])
    g["share"] = (g["aircraft"] / g["class aircraft"]).round(3)
    g["class"] = g["code"].map(lambda c: metrics.ARCH_NAMES.get(c, c))
    return g[["rule set", "class", "code", "window", "configuration", "aircraft", "class aircraft", "share"]]


def driver_windows(ds: Dataset, v: pd.DataFrame, cf: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Section 3.4, per class and complete window: the centre of each trace the figures draw.

    Centres follow the rule of the Method (C80): propulsive units as a MEDIAN (a few hull arrays
    with tens of units would carry a mean); tilting sets, propulsor types and tilting sets per
    propulsive unit as a MEAN, because a median of 1 or 2 stands still while the mix moves (the
    median is kept beside the mean for the two counts). A share is a share of the aircraft that
    answer the label. Blank under :data:`la_tables.MIN_CELL` aircraft with a value. For CVT the
    ducted share is split by whether the aircraft carries units on booms (C88)."""
    cf = cf if cf is not None else config_frame(ds, v)
    mc = la_tables.MIN_CELL
    rows = []

    def _c(s: pd.Series, how: str):
        s = pd.to_numeric(s, errors="coerce").dropna()
        if len(s) < mc:
            return np.nan
        return round(float(s.median() if how == "median" else s.mean()), 3)

    for code in CH3B_CLASSES:
        for wn in CH3B_WINDOWS:
            d = cf[cf["topType"].eq(code) & cf["window"].eq(wn)]
            u = d["units"].where(d["units"] > 0)
            spu = d["sets"] / u
            onb = d["on_booms"].map({True: 1.0, False: 0.0})
            duc = d["ducted"].map({True: 1.0, False: 0.0})
            row = {"class": metrics.ARCH_NAMES.get(code, code), "code": code, "window": wn,
                   "aircraft": int(len(d)), "few aircraft": wn in CH3B_FEW,
                   "tilting sets (mean)": _c(d["sets"], "mean"),
                   "tilting sets (median)": _c(d["sets"], "median"),
                   "propulsive units (median)": _c(d["units"], "median"),
                   "propulsor types (mean)": _c(d["n_types"], "mean"),
                   "propulsor types (median)": _c(d["n_types"], "median"),
                   "tilting sets per propulsive unit (mean)": _c(spu, "mean"),
                   "share with two or more tilting sets": _c((d["sets"] >= 2).astype(float).where(d["sets"].notna()), "mean"),
                   "share with a fixed unit": _c(d["any_fixed"].map({True: 1.0, False: 0.0}).where(d["recorded"].fillna(False)), "mean"),
                   "share with units on booms": _c(onb, "mean"),
                   "share with a ducted unit": _c(duc, "mean")}
            for tag, m in (("units on booms", onb.eq(1.0)), ("no units on booms", onb.eq(0.0))):
                row[f"aircraft, {tag}"] = int(m.sum())
                row[f"ducted share, {tag}"] = _c(duc[m], "mean") if code == "CVT" else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def _spearman(year: pd.Series, x: pd.Series) -> Dict[str, object]:
    """The trend test every trace uses (:func:`la_tables.trace_trends`): Spearman's rho between
    each aircraft's own priority year and the value, every complete year, at least
    :data:`la_tables.TREND_MIN` aircraft."""
    from scipy import stats as _st
    s = pd.DataFrame({"y": pd.to_numeric(year, errors="coerce"),
                      "x": pd.to_numeric(x, errors="coerce")}).dropna()
    s = s[s["y"].le(la_tables.LAST_COMPLETE)]
    out = {"aircraft": int(len(s)), "rho": np.nan, "p": np.nan}
    if len(s) < la_tables.TREND_MIN:
        out["movement"] = "too thin"
    elif s["x"].nunique() < 2:
        out["movement"] = "constant"
    else:
        rho, p = _st.spearmanr(s["y"], s["x"])
        out.update(rho=round(float(rho), 2), p=float(p),
                   movement=("rises" if rho > 0 else "falls") if p < la_tables.TREND_ALPHA else "flat")
    return out


def sets_per_unit_brief(ds: Dataset, v: pd.DataFrame, cf: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """The joints-per-unit correction (``la_tables.joints_per_unit``), compacted for the brief:
    tilting sets per aircraft and per propulsive unit, for Tilt Rotor, CVT and the five drawn
    classes pooled, with the MEAN per complete window — the median of a ratio of two small counts
    (1/2, 2/4) stands still while the mix moves — and the same Spearman test on every year. The
    base is the aircraft with a propulsive-unit count, for both rows of a class, as in the
    full-document table, so rho and p reproduce ``la_joints_per_unit``."""
    cf = cf if cf is not None else config_frame(ds, v)
    d = cf[cf["topType"].isin(CH3B_CLASSES) & cf["units"].gt(0)].copy()
    d["per unit"] = d["sets"] / d["units"]
    rows = []
    for code, label in (("TR", "Tilt Rotor"), ("CVT", "Combined vectored thrust"),
                        ("ALL5", "five classes pooled")):
        sub = d if code == "ALL5" else d[d["topType"].eq(code)]
        for measure, col in (("tilting sets per aircraft", "sets"),
                             ("tilting sets per propulsive unit", "per unit")):
            row = {"class": label, "code": code, "measure": measure}
            for wn in CH3B_WINDOWS:
                vals = sub.loc[sub["window"].eq(wn), col].dropna()
                row[la_tables.WIN_SHORT.get(wn, wn)] = (round(float(vals.mean()), 2)
                                                        if len(vals) >= la_tables.MIN_CELL else np.nan)
            row.update(_spearman(sub["year"], sub[col]))
            rows.append(row)
    return pd.DataFrame(rows)


def driver_links(ds: Dataset, v: pd.DataFrame, cf: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """The two links the chapter-3 story rests on, each as a small test (C88, C91):

    * **Tilt Rotor: the units follow the tilting sets** — median (and mean) propulsive units of
      the Tilt Rotor aircraft with one, two, and three or more tilting sets, all years;
    * **CVT: the duct follows the boom layout** — the share of CVT aircraft with a ducted unit,
      and its Spearman trend against the priority year, inside each boom layout (units on booms /
      none) and over all CVT aircraft. A trend that holds over all CVT and disappears inside both
      layouts is a change of layout, not of ducting within a layout.
    """
    cf = cf if cf is not None else config_frame(ds, v)
    rows = []
    tr = cf[cf["topType"].eq("TR") & cf["units"].gt(0) & cf["sets"].ge(1)]
    for label, m in (("1", tr["sets"].eq(1)), ("2", tr["sets"].eq(2)), ("3 or more", tr["sets"].ge(3))):
        s = tr.loc[m, "units"]
        rows.append({"link": "Tilt Rotor: propulsive units by tilting sets", "group": label,
                     "aircraft": int(len(s)), "median": float(s.median()) if len(s) else np.nan,
                     "mean": round(float(s.mean()), 2) if len(s) else np.nan,
                     "rho": np.nan, "p": np.nan, "movement": ""})
    cvt = cf[cf["topType"].eq("CVT")]
    duc = cvt["ducted"].map({True: 1.0, False: 0.0})
    onb = cvt["on_booms"].map({True: 1.0, False: 0.0})
    for label, m in (("units on booms", onb.eq(1.0)), ("no units on booms", onb.eq(0.0)),
                     ("all CVT", duc.notna())):
        t = _spearman(cvt.loc[m, "year"], duc[m])
        rows.append({"link": "CVT: ducted share by boom layout", "group": label,
                     "aircraft": t["aircraft"], "median": np.nan,
                     "mean": round(float(duc[m].dropna().mean()), 3) if m.any() else np.nan,
                     "rho": t["rho"], "p": t["p"], "movement": t["movement"]})
    return pd.DataFrame(rows)


def ch3b_tables(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Every frame of sections 3.3 and 3.4, keyed by table id (registered in :func:`build_all`)."""
    keys = _class_config_keys(ds, v)
    cf = config_frame(ds, v)
    return {"la_class_configs_brief": class_configs_brief(ds, v, keys),
            "la_class_config_mix": class_config_mix(ds, v, keys),
            "la_driver_windows": driver_windows(ds, v, cf),
            "la_sets_per_unit_brief": sets_per_unit_brief(ds, v, cf),
            "la_driver_links": driver_links(ds, v, cf)}


# ---------------------------------------------------------------------------------------------
# 2026-09-26 — chapter 4 of the brief (sm_text_ch4; the author's comments D1-D26)
# ---------------------------------------------------------------------------------------------
#: the classes chapter 4 reads one by one; every other class is pooled as "other classes"
CH4_CLASSES: List[str] = ["SLC", "TR", "CVT", "TW", "MR"]
CH4_WORD: Dict[str, str] = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT",
                            "TW": "Tilt Wing", "MR": "Multirotor", "other": "other classes"}
#: a class is read for concentration with this many aircraft or more
CH4_CLASS_MIN: int = 20
#: a class x window cell is read for its largest filer with this many aircraft or more
CH4_CELL_MIN: int = 10
#: the complete windows: the partial 2024-26 window is never read for a trend
CH4_WINDOWS: List[str] = [w for w in la_tables.WINDOW_NAMES if not str(w).startswith("2024")]
#: a window's two groups are tested only when the returning group holds this many aircraft
CH4_TEST_MIN: int = 20
#: an origin class is drawn in the succession matrix with this many successions or more
CH4_SUCC_MIN: int = 10
#: the release of the AAM Reality Index the market dates come from; mirrors
#: ``sm_index.ARI_RELEASE_YEAR`` (a first flight dated after it is a plan, not a flight)
CH4_ARI_RELEASE: int = 2026


def _ch4_class(code) -> str:
    return code if code in CH4_CLASSES else "other"


def _named_frame(v: pd.DataFrame) -> pd.DataFrame:
    """The aircraft of named organisations with a window, each flagged first-time or returning:
    first-time = the firm's earliest window in the corpus is this window."""
    order = list(la_tables.WINDOW_NAMES)
    w = v[v["named"]].dropna(subset=["window", "year"]).copy()
    first = w.groupby("firm")["window"].agg(lambda s: min(s, key=order.index))
    w["first_time"] = w["firm"].map(first).eq(w["window"])
    w["_c"] = w["topType"].map(_ch4_class)
    return w


def class_concentration_brief(v: pd.DataFrame) -> pd.DataFrame:
    """Per class of :data:`CH4_CLASS_MIN` aircraft or more: its filers, the effective number of
    filers (1 / sum of squared filer shares, the 2D of the diversity box applied to filers), the
    largest filer over all years, and the largest share one filer holds inside a single complete
    window (cells of :data:`CH4_CELL_MIN` aircraft or more). A filer is a firm; an individual
    inventor's patent is its own filer (``la_tables.class_filer_weight``)."""
    fw = la_tables.class_filer_weight(v)
    cw = la_tables.class_window_filer_weight(v, min_n=CH4_CELL_MIN)
    cw = cw[cw["window"].isin(CH4_WINDOWS)]
    rows = []
    for _, r in fw[fw["aircraft"] >= CH4_CLASS_MIN].iterrows():
        top_name = str(r["largest filer"])
        row = {"class": r["class"], "code": r["code"], "aircraft": int(r["aircraft"]),
               "filers": int(r["filers"]), "effective filers": float(r["effective filers"]),
               "largest filer": ("an individual inventor's patent" if "(one patent)" in top_name
                                 else top_name),
               "its aircraft": int(r["its aircraft"]), "its share": float(r["its share"]),
               "top 3 share": float(r["top 3 share"])}
        cells = cw[cw["code"].eq(r["code"])]
        if len(cells):
            top = cells.sort_values(["its share", "aircraft"], ascending=False).iloc[0]
            who = str(top["largest filer"])
            row.update({"largest share inside one window": float(top["its share"]),
                        "held by": ("an individual inventor's patent" if who == "one patent" else who),
                        "in window": top["window"], "window aircraft": int(top["aircraft"]),
                        "its aircraft in the window": int(top["its aircraft"])})
        rows.append(row)
    return pd.DataFrame(rows)


def entry_split(v: pd.DataFrame) -> pd.DataFrame:
    """Per complete window, the class mix of the named organisations' aircraft in two groups:
    firms filing their first eVTOL aircraft in the window (first-time) and firms that filed in an
    earlier window (returning). Unit: the unique aircraft."""
    w = _named_frame(v)
    rows = []
    for wn in CH4_WINDOWS:
        sub = w[w["window"].eq(wn)]
        for grp, mask in (("first-time filers", sub["first_time"]),
                          ("returning filers", ~sub["first_time"])):
            g = sub[mask]
            row = {"window": wn, "group": grp, "aircraft": int(len(g)),
                   "firms": int(g["firm"].nunique())}
            for c in CH4_CLASSES + ["other"]:
                row[CH4_WORD[c]] = round(float(g["_c"].eq(c).mean()), 3) if len(g) else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def _chi_p(frame: pd.DataFrame) -> Optional[float]:
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(frame["_c"], frame["first_time"])
    ct = ct.loc[ct.sum(axis=1) > 0]
    if ct.shape[1] < 2 or ct.shape[0] < 2:
        return None
    return float(chi2_contingency(ct)[1])


def entry_split_test(v: pd.DataFrame) -> pd.DataFrame:
    """Per complete window whose returning group holds :data:`CH4_TEST_MIN` aircraft or more: a
    chi-square test of class (the five classes and "other") against first-time / returning, and
    the same test again without the returning firm that holds most of the window's returning
    aircraft. The second test was added after the first result was seen (post hoc): one firm
    held most of the returning aircraft."""
    w = _named_frame(v)
    rows = []
    for wn in CH4_WINDOWS:
        sub = w[w["window"].eq(wn)]
        ret = sub[~sub["first_time"]]
        row = {"window": wn, "first-time aircraft": int(sub["first_time"].sum()),
               "returning aircraft": int(len(ret)),
               "returning firms": int(ret["firm"].nunique())}
        if len(ret) >= CH4_TEST_MIN:
            big = ret["firm"].value_counts()
            row.update({"p": _chi_p(sub), "largest returning firm": big.index[0],
                        "its aircraft": int(big.iloc[0]),
                        "p without it": _chi_p(sub[sub["firm"].ne(big.index[0])])})
        rows.append(row)
    return pd.DataFrame(rows)


def tw_entry(v: pd.DataFrame) -> pd.DataFrame:
    """Per complete window: the named firms entering (first aircraft in the window), those whose
    first aircraft is a Tilt Wing, what kind of entrant they are, and the Tilt Wing share of the
    window's aircraft. The first aircraft is chosen as in ``la_tables.cohorts``, so the counts are
    those of ``la_cohorts`` / ``la_cohort_mix``."""
    w = v[v["named"]].dropna(subset=["window", "year"]).sort_values("year")
    first = w.groupby("company_canonical").first()
    sizes = la_tables.firm_sizes(v)
    first["n_aircraft"] = sizes.reindex(first.index).fillna(0).astype(int).to_numpy()
    rows = []
    for wn in CH4_WINDOWS:
        ent = first[first["window"].eq(wn)]
        tw = ent[ent["topType"].eq("TW")]
        allw = v[v["window"].eq(wn)]
        rows.append({
            "window": wn, "firms entering": int(len(ent)), "entering with Tilt Wing": int(len(tw)),
            "Tilt Wing share of entrants": round(len(tw) / len(ent), 3) if len(ent) else np.nan,
            "Tilt Wing entrants: universities / institutes": int(tw["filer"].eq("University / institute").sum()),
            "Tilt Wing entrants: no other aircraft": int(tw["n_aircraft"].eq(1).sum()),
            "all entrants: universities / institutes": int(ent["filer"].eq("University / institute").sum()),
            "all entrants: no other aircraft": int(ent["n_aircraft"].eq(1).sum()),
            "aircraft in the window": int(len(allw)),
            "Tilt Wing aircraft": int(allw["topType"].eq("TW").sum()),
            "Tilt Wing share of the aircraft": round(float(allw["topType"].eq("TW").mean()), 3)
            if len(allw) else np.nan})
    out = pd.DataFrame(rows)
    # is the change of the Tilt Wing share from the window before more than chance? (Fisher)
    from scipy.stats import fisher_exact
    ps = [np.nan]
    for i in range(1, len(out)):
        a, b = out.iloc[i - 1], out.iloc[i]
        tab = [[int(a["Tilt Wing aircraft"]), int(a["aircraft in the window"] - a["Tilt Wing aircraft"])],
               [int(b["Tilt Wing aircraft"]), int(b["aircraft in the window"] - b["Tilt Wing aircraft"])]]
        ps.append(round(float(fisher_exact(tab)[1]), 3))
    out["Tilt Wing share, Fisher p against the window before"] = ps
    return out


def _succession_pairs(v: pd.DataFrame) -> pd.DataFrame:
    """Every consecutive pair of a named firm's aircraft in priority order — the pairs of
    ``la_tables.transitions``, kept per firm."""
    w = (v[v["named"] & v["topType"].notna()].dropna(subset=["year"])
         .sort_values(["company_canonical", "year", "aircraft_id"]))
    pairs = []
    for f, sub in w.groupby("company_canonical"):
        t = sub["topType"].tolist()
        pairs += [{"firm": f, "from": a, "to": b} for a, b in zip(t[:-1], t[1:])]
    return pd.DataFrame(pairs)


def succession_matrix(v: pd.DataFrame) -> pd.DataFrame:
    """Where a firm's next aircraft lands, by the class of the one before: one row per class of
    origin with :data:`CH4_SUCC_MIN` successions or more, the shares of each destination (a row
    sums to 1), and the share that stays once the firm with the most successions is left out."""
    p = _succession_pairs(v)
    top_firm = p["firm"].value_counts().index[0]
    q = p[p["firm"].ne(top_firm)]
    dests = CH4_CLASSES + ["PTC"]
    rows = []
    for code, sub in p.groupby("from"):
        if len(sub) < CH4_SUCC_MIN:
            continue
        row = {"class of origin": metrics.ARCH_NAMES.get(code, code), "code": code,
               "successions": int(len(sub)), "firms": int(sub["firm"].nunique()),
               "stays in the class": round(float(sub["to"].eq(code).mean()), 3)}
        for d in dests:
            row[f"→ {d}"] = round(float(sub["to"].eq(d).mean()), 3)
        row["→ other"] = round(float((~sub["to"].isin(dests)).mean()), 3)
        qs = q[q["from"].eq(code)]
        row["firm left out"] = top_firm
        row["its successions, all classes"] = int(p["firm"].eq(top_firm).sum())
        row["successions, all classes"] = int(len(p))
        row["firms with a succession"] = int(p["firm"].nunique())
        row["successions without it"] = int(len(qs))
        row["stays without it"] = round(float(qs["to"].eq(code).mean()), 3) if len(qs) else np.nan
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("successions", ascending=False).reset_index(drop=True)
    out.attrs["pairs"] = int(len(p))
    out.attrs["same share"] = round(float(p["from"].eq(p["to"]).mean()), 3)
    return out


def ari_funding(v: pd.DataFrame) -> pd.DataFrame:
    """The index firms that file in the corpus, with what the AAM Reality Index says about their
    money: disclosed funding ($M, May 2026 release), "corporate backed" where the index gives no
    amount, and nothing for the firms only earlier releases list. The index carries no headcount
    and no market capitalisation. Beside it: unique aircraft, first patent (priority year), first
    flight and the lead from first patent to first flight (flights up to the release year)."""
    f = la_tables.ari_firms(v)
    t = la_tables.ari_timeline(v).set_index("company")
    rows = []
    for _, r in f.iterrows():
        raw = str(r["funding $M"]).strip()
        amt = pd.to_numeric(raw.replace(",", ""), errors="coerce")
        status = ("disclosed" if pd.notna(amt) else
                  "corporate backed, no amount" if raw.lower().startswith("corporate") else
                  "not in the May 2026 release")
        ff = t["first flight (ARI)"].get(r["company"]) if r["company"] in t.index else None
        ff = pd.to_numeric(ff, errors="coerce")
        flown = pd.notna(ff) and ff <= CH4_ARI_RELEASE
        fp = pd.to_numeric(r["first priority year"], errors="coerce")
        rows.append({"company": r["company"], "ARI score": r["ARI score"], "release": r["release"],
                     "funding $M": float(amt) if pd.notna(amt) else np.nan,
                     "funding status": status, "unique aircraft": int(r["unique aircraft"]),
                     "first patent": int(fp) if pd.notna(fp) else np.nan,
                     "first flight": float(ff) if pd.notna(ff) else np.nan,
                     "first flight flown": bool(flown),
                     "years first patent to first flight": (float(ff - fp) if flown and pd.notna(fp)
                                                            else np.nan)})
    return pd.DataFrame(rows)


def ari_funding_tests(v: pd.DataFrame, fr: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Spearman rho of disclosed funding against three patent-side quantities, on the index firms
    with a disclosed amount (the lead only on those whose first flight has happened)."""
    from scipy.stats import spearmanr
    fr = ari_funding(v) if fr is None else fr
    d = fr[fr["funding $M"].notna()]
    rows = []
    for y, label in (("unique aircraft", "unique aircraft in the corpus"),
                     ("first patent", "priority year of the first patent"),
                     ("years first patent to first flight", "years from first patent to first flight")):
        s = d[["funding $M", y]].dropna()
        r = spearmanr(s["funding $M"], s[y]) if len(s) >= 3 else None
        rows.append({"against": label, "column": y, "firms": int(len(s)),
                     "rho": round(float(r.statistic), 2) if r is not None else np.nan,
                     "p": round(float(r.pvalue), 3) if r is not None else np.nan})
    return pd.DataFrame(rows)


def ch4_tables(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Every frame of chapter 4 of the brief, keyed by table id (registered in :func:`build_all`)."""
    fr = ari_funding(v)
    return {"la_class_concentration_brief": class_concentration_brief(v),
            "la_entry_split": entry_split(v),
            "la_entry_split_test": entry_split_test(v),
            "la_tw_entry": tw_entry(v),
            "la_succession_matrix": succession_matrix(v),
            "la_ari_funding": fr,
            "la_ari_funding_tests": ari_funding_tests(v, fr)}


# ---------------------------------------------------------------------------------------------
# 2026-09-27 — chapter 5 of the brief (sm_text_ch5, comments E1-E17): what each region designs
# and how its mix moves, when each region files, and whether the regions converge
# ---------------------------------------------------------------------------------------------
#: 2026-09-27, author's ruling on chapter 5: the regional mix is read FROM 2012 — the windows
#: 2012-15, 2016-19 and 2020-23 (<= 2011 is drawn faded, too few aircraft) — and a change is a
#: trend over those twelve priority years, each aircraft at its own year (Spearman, as the driver
#: traces of chapter 3), not a before/after-2020 split
CH5_WINS: List[str] = ["2012-15", "2016-19", "2020-23"]
CH5_TREND: Tuple[int, int] = (2012, 2023)
#: the categories the regional figure draws, per variable (column of ``la_tables.base``)
CH5_VARS: Dict[str, Tuple[str, List]] = {
    "class": ("topType", ["SLC", "TR", "CVT", "TW", "MR", "other"]),
    "propulsive units": ("rotorBin", ["1-3", "4", "5-6", "7-8", "9+"]),
    "tilting unit": ("any_tilting", [True, False]),
}
CH5_CLASS_WORD: Dict[str, str] = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT",
                                  "TW": "Tilt Wing", "MR": "Multirotor", "other": "other classes"}


def _ch5_frame(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """The aircraft of the three regions, with their class folded to the five largest + other,
    and whether they belong to chapter 3's family F (definition b)."""
    keys = _level_keys(ds, v)["family_b"]
    w = v.assign(F=keys.eq(FAMILY_LABEL).where(keys.notna()))
    w = w[w["region3"].isin(la_tables.REGIONS)].copy()
    w["cls5"] = w["topType"].where(w["topType"].isin(CH5_VARS["class"][1][:-1]), "other")
    w.loc[w["topType"].isna(), "cls5"] = np.nan
    w["rb"] = w["rotorBin"].where(w["rotorBin"].isin(CH5_VARS["propulsive units"][1]))
    w["tilt"] = w["any_tilting"].map({True: True, False: False})
    return w


def _ch5_col(var: str) -> str:
    return {"class": "cls5", "propulsive units": "rb", "tilting unit": "tilt", "family F": "F"}[var]


def region_mix_change(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Per region, variable and answer: aircraft and share in 2012-15, 2016-19 and 2020-23, and
    the trend over 2012-2023 — Spearman rho of the answer (1/0) against each aircraft's own
    priority year, with its p. The share is taken over the region-window's aircraft whose field
    is recorded. Drives the trend column of the regional figure (E4c) and the family-F trend of
    5.3."""
    from scipy.stats import spearmanr
    w = _ch5_frame(ds, v)
    lo, hi = CH5_TREND
    rows = []
    specs = list(CH5_VARS.items()) + [("family F", ("F", [True]))]
    for reg in la_tables.REGIONS:
        for var, (_, cats) in specs:
            col = _ch5_col(var)
            s = w[w["region3"].eq(reg) & w[col].notna()]
            tr = s[s["year"].between(lo, hi)]
            for c in cats:
                row = {"region": reg, "variable": var, "answer": str(c),
                       "label": CH5_CLASS_WORD.get(c, "yes" if c is True else "no" if c is False else c)}
                for wn in CH5_WINS:
                    x = s[s["window"].eq(wn)]
                    k = int(x[col].eq(c).sum())
                    row[f"aircraft {wn}"] = k
                    row[f"base {wn}"] = int(len(x))
                    row[f"share {wn}"] = round(k / len(x), 4) if len(x) else np.nan
                y = tr[col].eq(c).astype(int)
                r = spearmanr(tr["year"], y) if y.nunique() > 1 else None
                row["aircraft 2012-23"] = int(len(tr))
                row["rho"] = round(float(r.statistic), 3) if r is not None else np.nan
                row["p"] = round(float(r.pvalue), 4) if r is not None else np.nan
                rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs["trend"] = f"{lo}-{hi}"
    return out


def region_window_mix(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """The bars of the regional figure as numbers: per region, variable, answer and window, the
    aircraft and the share of the region-window's aircraft whose field is recorded."""
    w = _ch5_frame(ds, v)
    rows = []
    for reg in la_tables.REGIONS:
        for var, (_, cats) in CH5_VARS.items():
            col = _ch5_col(var)
            s = w[w["region3"].eq(reg) & w[col].notna()]
            for wn in la_tables.WINDOW_NAMES:
                c = s[s["window"].eq(wn)]
                for a in cats:
                    k = int(c[col].eq(a).sum())
                    rows.append({"region": reg, "variable": var, "answer": str(a), "window": wn,
                                 "aircraft": k, "base": int(len(c)),
                                 "share": round(k / len(c), 4) if len(c) else np.nan})
    return pd.DataFrame(rows)


def _chi(frame: pd.DataFrame, a: str, b: str) -> Tuple[float, int]:
    from scipy.stats import chi2_contingency
    f = frame.dropna(subset=[a, b])
    ct = pd.crosstab(f[a], f[b])
    ct = ct.loc[:, ct.sum() > 0]
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan, int(len(f))
    return float(chi2_contingency(ct)[1]), int(len(f))


def region_tests(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Do the three regions differ? One chi-square of region against each measure, over all years
    and in each window from 2012, and, where one firm could carry it, again without the largest filer of North America
    (Bell / Textron, 60 aircraft). Base: the aircraft whose field is recorded."""
    w = _ch5_frame(ds, v)
    big = w[w["region3"].eq("North America")]["firm"].value_counts().index[0]
    w["tr"] = w["topType"].eq("TR").where(w["topType"].notna())
    rows = []
    specs = [("class mix (five classes + other)", "cls5"), ("propulsive-unit band", "rb"),
             ("any tilting unit", "tilt"), ("Tilt Rotor", "tr"), ("family F", "F")]
    for name, col in specs:
        for per in ["all years"] + CH5_WINS:
            s = w if per == "all years" else w[w["window"].eq(per)]
            for who, sub in (("all filers", s), (f"without {big}", s[s["firm"].ne(big)])):
                p, n = _chi(sub, "region3", col)
                rows.append({"measure": name, "period": per, "filers": who, "aircraft": n,
                             "p (chi-square, region)": round(p, 4)})
    out = pd.DataFrame(rows)
    out.attrs["left_out"] = big
    return out


def region_lean(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Per region, all years: its aircraft, its largest filer, and the share with a tilting unit,
    the Tilt Rotor share (all years) and the family-F share per window from 2012 — the first two also without the
    region's largest filer, so a regional lean can be told from one firm's line (E4e)."""
    w = _ch5_frame(ds, v)
    rows = []
    for reg in la_tables.REGIONS:
        s = w[w["region3"].eq(reg)]
        big = s["firm"].value_counts()
        firm, fn = str(big.index[0]), int(big.iloc[0])
        wo = s[s["firm"].ne(firm)]
        t, t2 = s["tilt"].dropna(), wo["tilt"].dropna()
        tt = s[s["topType"].notna()]
        tt2 = wo[wo["topType"].notna()]
        row = {"region": reg, "aircraft": int(len(s)), "largest filer": firm,
               "its aircraft": fn,
               "its Tilt Rotor aircraft": int(s[s["firm"].eq(firm)]["topType"].eq("TR").sum()),
               "Tilt Rotor aircraft": int(tt["topType"].eq("TR").sum()),
               "its tilting aircraft": int(s[s["firm"].eq(firm)]["tilt"].eq(True).sum()),
               "tilting aircraft": int(t.eq(True).sum()),
               "tilting share": round(float(t.mean()), 4),
               "tilting share without it": round(float(t2.mean()), 4),
               "Tilt Rotor share": round(float(tt["topType"].eq("TR").mean()), 4),
               "Tilt Rotor share without it": round(float(tt2["topType"].eq("TR").mean()), 4)}
        for per in CH5_WINS:
            f = s[s["window"].eq(per)]["F"].dropna()
            row[f"F aircraft {per}"] = int(f.sum())
            row[f"F base {per}"] = int(len(f))
            row[f"F share {per}"] = round(float(f.mean()), 4) if len(f) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


#: the share of a year a snapshot has seen (2026-06-08: 159 of 365 days) — the part of the
#: snapshot's own calendar year in which a patent can already have published
def _snapshot_frac(ds: Dataset) -> Tuple[int, float]:
    snap = pd.to_datetime(ds.identity["snapshot_date"].dropna().iloc[0])
    return int(snap.year), float(snap.dayofyear / 365.0)


def region_years(ds: Dataset, v: pd.DataFrame, first: int = 2012) -> pd.DataFrame:
    """Aircraft per priority year and region, each region's share of the three regions' aircraft
    of that year, and the share corrected for publication lag (E4d).

    The correction: an aircraft enters the corpus only once its patent is published. For each
    region, the lag from priority to publication is read on its aircraft of 2016-21, whose
    publications are complete; the part of a region's aircraft of year Y that the snapshot can
    already see is P(lag <= S-Y-1) + f * P(lag = S-Y), S the snapshot year and f the part of it
    elapsed. Each count is divided by that visibility and the shares recomputed. Lag is in whole
    years (publication year minus priority year), so the correction is approximate."""
    S, frac = _snapshot_frac(ds)
    j = v.merge(ds.identity[["patent_id", "pub_year"]], on="patent_id", how="left",
                suffixes=("", "_pub"))
    pub = pd.to_numeric(j["pub_year_pub"] if "pub_year_pub" in j else j["pub_year"], errors="coerce")
    j = j.assign(lag=pub - j["year"])
    j = j[j["region3"].isin(la_tables.REGIONS)]
    ref = j[j["year"].between(2016, 2021)]
    lagd = {r: ref.loc[ref["region3"].eq(r), "lag"].dropna().to_numpy() for r in la_tables.REGIONS}

    def vis(r, y):
        k = S - y
        arr = lagd[r]
        return float(np.mean(arr <= k - 1) + frac * np.mean(arr == k)) if len(arr) else np.nan

    rows = []
    for y in range(first, S + 1):
        s = j[j["year"].eq(y)]
        n = {r: int(s["region3"].eq(r).sum()) for r in la_tables.REGIONS}
        tot = sum(n.values())
        vv = {r: vis(r, y) for r in la_tables.REGIONS}
        corr = {r: (n[r] / vv[r] if vv[r] and vv[r] > 0 else np.nan) for r in la_tables.REGIONS}
        ctot = np.nansum(list(corr.values()))
        for r in la_tables.REGIONS:
            rows.append({"priority year": y, "region": r, "aircraft": n[r],
                         "share of the year": round(n[r] / tot, 4) if tot else np.nan,
                         "visible at the snapshot": round(vv[r], 3),
                         "share corrected for publication lag":
                             round(corr[r] / ctot, 4) if ctot and np.isfinite(corr[r]) else np.nan,
                         "complete": bool(y <= la_tables.LAST_COMPLETE)})
    out = pd.DataFrame(rows)
    med = {r: float(np.median(lagd[r])) for r in la_tables.REGIONS}
    out.attrs.update(snapshot_year=S, snapshot_frac=round(frac, 2), median_lag=med)
    return out


def region_lag(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Per region: the lag from priority to publication of its aircraft of 2016-21 (median, and the
    share published within 0-3 years) and the publication office most of them publish at."""
    j = v.merge(ds.identity[["patent_id", "pub_year"]], on="patent_id", how="left",
                suffixes=("", "_pub"))
    pub = pd.to_numeric(j["pub_year_pub"] if "pub_year_pub" in j else j["pub_year"], errors="coerce")
    j = j.assign(lag=pub - j["year"])
    rows = []
    for r in la_tables.REGIONS:
        s = j[j["region3"].eq(r) & j["year"].between(2016, 2021)]
        lag = s["lag"].dropna()
        off = s["pub_office"].value_counts()
        row = {"region": r, "aircraft 2016-21": int(len(lag)), "median lag (years)": float(lag.median()),
               "main office": str(off.index[0]), "its share": round(float(off.iloc[0] / len(s)), 3)}
        for k in range(4):
            row[f"published within {k} y"] = round(float((lag <= k).mean()), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def ch5_tables(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Every frame of chapter 5 of the brief, keyed by table id (registered in :func:`build_all`)."""
    return {"la_region_mix_change": region_mix_change(ds, v),
            "la_region_window_mix": region_window_mix(ds, v),
            "la_region_tests": region_tests(ds, v),
            "la_region_lean": region_lean(ds, v),
            "la_region_years": region_years(ds, v),
            "la_region_lag": region_lag(ds, v),
            "la_region_proximity_test": region_proximity_test(ds, v)}


def region_proximity_test(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """The one-row summary behind ``la_proximity_region``: mean proximity of same-region and of
    different-region firm pairs and the permutation p that the first is higher (region labels
    shuffled over the firms). Stored so the brief can quote the p, which the CSV of the pair
    table does not carry."""
    _, summ = la_tables.proximity_by_region(ds, v)
    a = summ.attrs
    pairs = int(a["same pairs"]) + int(a["different pairs"])
    firms = int(round((1 + math.sqrt(1 + 8 * pairs)) / 2))          # pairs = n (n - 1) / 2
    return pd.DataFrame([{"firms": firms, "minimum aircraft per firm": la_tables.FIRM_MIN,
                          "same-region pairs": a["same pairs"], "same-region mean": a["same mean"],
                          "different-region pairs": a["different pairs"],
                          "different-region mean": a["different mean"], "p (permutation)": a["p"],
                          "draws": a["draws"]}])


def build_all(ds: Dataset, v: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Every frame this module owns, keyed by table id — the module's single entry point.

    ``la_doubling_time`` / ``la_doubling_ratio`` close the 1.1 sticker, ``la_discovery_curve`` /
    ``la_discovery_estimators`` the 2.2 sticker, ``la_lag_offsets`` / ``la_lag_constancy`` the
    4.2 sticker (rulings 2026-09-25). ``v`` is :func:`la_tables.base`, passed in rather than
    rebuilt so this module reads the same 665 aircraft as every other table.
    """
    curve = discovery_curve(ds, v)
    return {
        "la_doubling_time": doubling_time(ds, v),
        "la_doubling_ratio": doubling_ratio(ds, v),
        "la_discovery_curve": curve,
        "la_discovery_estimators": discovery_estimators(ds, v, curve),
        "la_lag_offsets": lag_offsets(v),
        "la_lag_constancy": lag_constancy(v),
        # 2026-09-25: the seven-year rule measured on the corpus (user-supplied check)
        "la_lapse_check": lapse_check(),
        # 2026-09-26: an aircraft is out of force only when every patent linked to it is
        # (author's ruling); the primary-patent reading is printed beside it
        "la_force_aircraft": force_aircraft(ds, v),
        "la_force_aircraft_test": force_aircraft_test(ds, v),
        # 2026-09-26: the multiples drawn in Figure 1 (ii), so the brief quotes them as placeholders
        "la_baseline_multiples": baseline_multiples(ds, v),
        # 2026-09-26: Figure 1 (ii) is a growth-rate panel (author's ruling)
        "la_growth_rates": growth_rates(ds, v),
        "la_growth_ratios": growth_ratios(ds, v),
        # 2026-09-26, C44-C46: class shares per window against the dated evtol.news directory
        "la_evtolnews_check": evtolnews_check(ds, v),
        "la_evtolnews_compare": evtolnews_compare(ds, v),
        "la_evtolnews_class_verdict": evtolnews_class_verdict(ds, v),
        "la_evtolnews_coverage": evtolnews_coverage(),
        # 2026-09-26, chapter-2 review: the levels the brief reads, with the family F as one
        # more level (C48/C49/C54), and what CVT · 5-6's few filers are made of (C71)
        "la_archetype_levels_brief": archetype_levels_brief(ds, v),
        "la_archetype_filer_split": archetype_filer_split(v),
        # 2026-09-26, chapter-3 review (C53, C54, C57): the dominant-design test at the four
        # levels, condition 1 per priority year on the in-force and all-aircraft bases
        **ch3_tables(ds, v),
        # 2026-09-26, chapter 3 (3.3-3.4, sm_text_ch3b): class configurations on the proposed
        # rules (both rule sets, CLASS_RULES_SET chooses) and the driver frames
        **ch3b_tables(ds, v),
        # 2026-09-26, chapter 4 (sm_text_ch4): concentration per class, first-time against
        # returning filers, Tilt Wing entry, successions, and the index firms' funding
        **ch4_tables(ds, v),
        # 2026-09-27, chapter 5 (sm_text_ch5, E1-E17): regional mix and its change, the region
        # tests, the regional lean without the largest filer, filing per year against lag
        **ch5_tables(ds, v),
    }
