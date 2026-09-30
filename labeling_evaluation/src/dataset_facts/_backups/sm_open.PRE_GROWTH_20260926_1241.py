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

    lv = list(levels) if levels else DISCOVERY_LEVELS
    with plt.rc_context({**STYLE, "font.size": 8.0}):
        fig, ax = plt.subplots(figsize=(7.09, 3.4), dpi=200)
        for i, level in enumerate(lv):
            c = curve[curve["level"].eq(level)].sort_values("aircraft")
            x = c["aircraft"].to_numpy()
            colour = CAT[i % len(CAT)]
            ax.fill_between(x, c["2.5 %"], c["97.5 %"], color=colour, alpha=0.18, linewidth=0)
            ax.plot(x, c["archetypes (date order)"], color=colour, lw=1.6,
                    dashes=[(None, None), (5, 2), (1.5, 1.5)][i % 3],
                    label=f"{level} — {int(c['archetypes (date order)'].iloc[-1])} archetypes "
                          f"in {len(c)} aircraft")
            ax.plot(x, c["archetypes (random order)"], color=colour, lw=0.9, alpha=0.55,
                    dashes=(1, 2))
        _hgrid(ax)
        ax.set_xlabel("aircraft, in priority order")
        ax.set_ylabel("distinct archetypes seen")
        ax.set_title("Discovery curve: date order (solid) against random order (dotted)",
                     color=INK, loc="left")
        ax.legend(frameon=False, loc="lower right")
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
    }
