"""Association, agreement, trend and significance tests (science only: arrays in, numbers out).

Every function is a pure statistical core lifted from the archived analysis code
(archive/labeling_evaluation/src/dataset_facts). Frame building, rounding and wording stay out;
defaults are those the document used.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd

# defaults the document used (la_tables.py:44, 2486-2487, 2814 area)
LAST_COMPLETE = 2023     # every trend claim ends here
TREND_MIN = 20           # a trend is read on at least this many aircraft
TREND_ALPHA = 0.05       # "rises"/"falls" at p < this
COUPLING_MIN_N = 30      # a Cramér's V pair is measured on at least this many rows
PERMS = 5000             # permutations of the class x region interaction test
SEED = 42                # seed of every permutation / bootstrap of the document


# ------------------------------------------------------------------ Cramér's V
def cramers_v_bc(x: pd.Series, y: pd.Series, min_n: int = COUPLING_MIN_N) -> Tuple[float, int]:
    """Bias-corrected Cramér's V (Bergsma 2013) on the rows where both fields carry a value.

    Formula: phi2 = max(0, chi2/n - (k-1)(r-1)/(n-1)); k~ = k - (k-1)^2/(n-1); r~ = r - (r-1)^2/(n-1);
             V = sqrt(phi2 / min(k~ - 1, r~ - 1)); chi2 is Pearson's, WITHOUT continuity correction.
    Rows with a missing value or the strings "<NA>", "nan", "" are dropped. NaN if n < min_n (30),
    if either field has fewer than 2 levels, or if the denominator is not positive. Returns (V, n).

    Ported from: la_tables.py:cramers_v_bc
    Used in: la_trace_couplings / la_trace_couplings_all
    """
    from scipy.stats import chi2_contingency
    d = pd.DataFrame({"x": x.astype(object), "y": y.astype(object)}).dropna()
    d = d[~d["x"].astype(str).isin(["<NA>", "nan", ""]) & ~d["y"].astype(str).isin(["<NA>", "nan", ""])]
    n = len(d)
    if n < min_n:
        return np.nan, n
    ct = pd.crosstab(d["x"].astype(str), d["y"].astype(str))
    r, k = ct.shape
    if r < 2 or k < 2:
        return np.nan, n
    chi2 = chi2_contingency(ct.values, correction=False)[0]
    phi2 = max(0.0, chi2 / n - (k - 1) * (r - 1) / (n - 1))
    kc, rc = k - (k - 1) ** 2 / (n - 1), r - (r - 1) ** 2 / (n - 1)
    den = min(kc - 1, rc - 1)
    return (float(np.sqrt(phi2 / den)) if den > 0 else np.nan), n


# ------------------------------------------------------------------ chi-square
def chi2_test(table) -> Dict[str, float]:
    """Pearson chi-square test of independence on a contingency table (scipy defaults, so Yates
    correction applies on 2x2 tables).

    Formula: chi2 = sum (O - E)^2 / E, E = row_total * col_total / n; p from chi2 with (r-1)(c-1) dof.

    Ported from: la_tables.py:duct_by_units inner _chi (~2244), sm_open.py:force_aircraft_test (~1024),
                 sm_open.py:evtolnews window test (~1326)
    Used in: la_duct_by_units (chi2/dof/p attrs), la_force_aircraft_test, la_evtolnews_* (5-class p)
    """
    from scipy.stats import chi2_contingency
    chi2, p, dof, _ = chi2_contingency(np.asarray(table))
    return {"chi2": float(chi2), "dof": int(dof), "p": float(p)}


def chi2_p_of_crosstab(labels: pd.Series, groups: pd.Series, drop_empty: str = "rows") -> Optional[float]:
    """p of the chi-square test of two label columns after dropping empty rows ("rows") of the
    crosstab; None when the table is smaller than 2x2.

    Formula: as chi2_test on pd.crosstab(labels, groups).
    Ported from: sm_open.py:_chi_p (rows dropped, 'None' if < 2x2)
    Used in: la_entry_split_test (columns of 'p' and 'p without it')
    """
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(labels, groups)
    if drop_empty == "rows":
        ct = ct.loc[ct.sum(axis=1) > 0]
    if ct.shape[1] < 2 or ct.shape[0] < 2:
        return None
    return float(chi2_contingency(ct)[1])


def chi2_p_of_columns(frame: pd.DataFrame, a: str, b: str) -> Tuple[float, int]:
    """p of the chi-square test of column ``a`` against ``b`` on the rows where both are set;
    all-zero columns of the crosstab are dropped; (NaN, n) when smaller than 2x2. Returns (p, n).

    Ported from: sm_open.py:_chi
    Used in: la_region_tests
    """
    from scipy.stats import chi2_contingency
    f = frame.dropna(subset=[a, b])
    ct = pd.crosstab(f[a], f[b])
    ct = ct.loc[:, ct.sum() > 0]
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan, int(len(f))
    return float(chi2_contingency(ct)[1]), int(len(f))


def chi2_p_two_groups(counts_a: Iterable[float], counts_b: Iterable[float]) -> float:
    """p of the chi-square test of two count vectors over the same levels (levels empty in both
    groups dropped); NaN if scipy cannot run it (e.g. a single level left).

    Formula: as chi2_test on the 2 x L table.
    Ported from: la_tables.py:linked_representativeness (~1580), la_tables.py:_representativeness (~3652),
                 la_tables.py:ari_gap (~1311, categorical branch, which passes the 2xL crosstab)
    Used in: la_linked_representativeness, la_trl_representativeness, la_ari_representativeness
    """
    from scipy.stats import chi2_contingency
    obs = np.vstack([np.asarray(counts_a, dtype=float), np.asarray(counts_b, dtype=float)])
    obs = obs[:, obs.sum(axis=0) > 0]
    try:
        return float(chi2_contingency(obs)[1])
    except Exception:
        return float("nan")


def total_variation_distance(counts_a: Iterable[float], counts_b: Iterable[float],
                             n_a: int, n_b: int) -> float:
    """Total variation distance between the level shares of two groups.

    Formula: TVD = sum_i | a_i / max(n_a,1) - b_i / max(n_b,1) | / 2
    Ported from: la_tables.py:linked_representativeness (variable ``gap``)
    Used in: la_linked_representativeness ('total variation distance')
    """
    ca, cb = np.asarray(counts_a, dtype=float), np.asarray(counts_b, dtype=float)
    return float(np.abs(ca / max(n_a, 1) - cb / max(n_b, 1)).sum() / 2)


# ------------------------------------------------------------------ rank / exact tests
def mann_whitney_p(a, b, alternative: Optional[str] = None) -> float:
    """p of the Mann-Whitney U test between two samples (scipy defaults; the document either
    passed alternative="two-sided" or nothing, which is the same).

    Formula: U = sum of ranks of a - n_a(n_a+1)/2; p from scipy.stats.mannwhitneyu.
    Ported from: la_tables.py:market_vs_patents (~746), :linked_representativeness (~1598),
                 :_representativeness (~3666), :ari_gap (~1297)
    Used in: la_market_vs_patents, la_linked/trl/ari_representativeness, la_ari_gap
    """
    from scipy.stats import mannwhitneyu
    if alternative is None:
        return float(mannwhitneyu(a, b).pvalue)
    return float(mannwhitneyu(a, b, alternative=alternative).pvalue)


def fisher_exact_p(table) -> float:
    """Two-sided Fisher exact p of a 2x2 table (scipy default).

    Ported from: la_tables.py:ari_gap (~1305), sm_open.py:tw_entry (~2273),
                 sm_open.py:evtolnews_* (~1328, 1366, 1372)
    Used in: la_ari_gap, la_tw_entry ('Fisher p against the window before'), la_evtolnews_*
    """
    from scipy.stats import fisher_exact
    return float(fisher_exact(table)[1])


def spearman_rho_p(x, y, min_n: int = 0, require_variation: bool = False) -> Tuple[float, float]:
    """Spearman rank correlation and its p on paired values (NaN, NaN if fewer than min_n pairs,
    or, with require_variation, if y is constant).

    Formula: rho = Pearson correlation of the mid-ranks of x and y; p from scipy.stats.spearmanr.
    Ported from: la_tables.py:market_vs_patents (~776, min 4 pairs), la_tables.py:ari_correlation (~1228,
                 own n/uniqueness gate left to the caller), sm_open.py:ari_funding_tests (~2363, min 3),
                 sm_open.py:region_mix_change (~2589, y must vary)
    Used in: la_market_vs_patents, la_ari_correlation, la_ari_funding_tests, la_region_mix_change
    """
    from scipy.stats import spearmanr
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < min_n or (require_variation and len(np.unique(y)) <= 1):
        return np.nan, np.nan
    r = spearmanr(x, y)
    return float(r.statistic), float(r.pvalue)


def spearman_trend(year, x, last_complete: int = LAST_COMPLETE, min_n: int = TREND_MIN,
                   alpha: float = TREND_ALPHA) -> Dict[str, object]:
    """The trend test every trace uses: Spearman's rho between each aircraft's own priority year
    and the value, complete years only, at least ``min_n`` aircraft.

    Formula: rho = Pearson correlation of mid-ranks of (year, x); movement = "rises" if rho>0 and
             p < alpha, "falls" if rho<0 and p < alpha, else "flat"; "too thin" if n < min_n,
             "constant" if x has a single value. Defaults: last_complete 2023, min_n 20, alpha 0.05.
    Returns {aircraft, rho, p, movement}; rho and p are NOT rounded (the archive rounds rho to 2).

    Ported from: sm_open.py:_spearman (same body as la_tables.py:trace_trends ~2637 and :joints_per_unit ~3881)
    Used in: la_trace_trends, la_joints_per_unit (rho / p / movement columns)
    """
    from scipy import stats as _st
    s = pd.DataFrame({"y": pd.to_numeric(year, errors="coerce"),
                      "x": pd.to_numeric(x, errors="coerce")}).dropna()
    s = s[s["y"].le(last_complete)]
    out: Dict[str, object] = {"aircraft": int(len(s)), "rho": np.nan, "p": np.nan}
    if len(s) < min_n:
        out["movement"] = "too thin"
    elif s["x"].nunique() < 2:
        out["movement"] = "constant"
    else:
        rho, p = _st.spearmanr(s["y"], s["x"])
        out.update(rho=float(rho), p=float(p),
                   movement=("rises" if rho > 0 else "falls") if p < alpha else "flat")
    return out


# ------------------------------------------------------------------ agreement
def cohen_kappa(a: Iterable, b: Iterable) -> float:
    """Cohen's kappa between two label vectors, over the rows where both are set.

    Formula: kappa = (p_o - p_e) / (1 - p_e); p_o = share of equal pairs;
             p_e = sum_k pa_k * pb_k over the union of labels. NaN if no pair or p_e == 1.
    Ported from: metrics.py:cohen_kappa
    Used in: label-agreement kappa (atlas, la_*_agreement tables)
    """
    pairs = pd.DataFrame({"a": list(a), "b": list(b)}).dropna()
    if pairs.empty:
        return float("nan")
    observed = float((pairs["a"] == pairs["b"]).mean())
    pa = pairs["a"].value_counts(normalize=True)
    pb = pairs["b"].value_counts(normalize=True)
    expected = float(sum(pa.get(k, 0.0) * pb.get(k, 0.0) for k in set(pa.index) | set(pb.index)))
    if expected == 1.0:
        return float("nan")
    return (observed - expected) / (1.0 - expected)


def raw_agreement(a: Iterable, b: Iterable) -> Tuple[int, float]:
    """(n, share of equal pairs) over the rows where both labels are set.

    Ported from: metrics.py:agreement (unrounded)
    """
    pairs = pd.DataFrame({"a": list(a), "b": list(b)}).dropna()
    return int(len(pairs)), (float((pairs["a"] == pairs["b"]).mean()) if len(pairs) else float("nan"))


# ------------------------------------------------------------------ multiple testing
def bh_qvalues(p) -> np.ndarray:
    """Benjamini-Hochberg q-values, in the input order. NOT clipped at 1 (as the archive).

    Formula: sort p ascending; q_(i) = min_{j >= i} p_(j) * m / j  (m = number of tests, j = rank).
    The archive applied it to a frame already sorted by p; the result is identical for any order.
    Ported from: la_tables.py:ari_correlation (~1235, 'q (BH)'; unrounded here)
    Used in: la_ari_correlation ('q (BH)', 'holds?' uses q < 0.10)
    """
    p = np.asarray(p, dtype=float)
    order = np.argsort(p, kind="stable")
    m = len(p)
    q_sorted = (p[order] * m / (np.arange(m) + 1))[::-1]
    q_sorted = np.minimum.accumulate(q_sorted)[::-1]
    out = np.empty(m)
    out[order] = q_sorted
    return out


def holm_adjust(p) -> np.ndarray:
    """Holm step-down adjusted p-values, in the input order.

    Formula: sort p ascending; adj_(i) = max_{j <= i} min(1, p_(j) * (m - j + 1)) (0-based: m - i).
    Ported from: sm_open.py:lag_constancy (~736-741; unrounded here)
    Used in: la_lag_constancy ('p (Holm, across the two regions)')
    """
    p = np.asarray(p, dtype=float)
    order = np.argsort(p, kind="stable")
    m = len(p)
    run, out = 0.0, np.empty(m)
    for i, ix in enumerate(order):
        run = max(run, min(1.0, float(p[ix]) * (m - i)))
        out[ix] = run
    return out


# ------------------------------------------------------------------ permutation tests
def design_matrix(cls: pd.Series, reg: pd.Series, interaction: bool) -> np.ndarray:
    """Reference-coded dummy design matrix for class + region (+ their interaction), with an
    intercept column; first level (in get_dummies order) of each factor is the reference.

    Ported from: sm_open.py:_design
    """
    c = pd.get_dummies(cls, drop_first=True, dtype=float)
    r = pd.get_dummies(reg, drop_first=True, dtype=float)
    parts = [np.ones((len(cls), 1)), c.to_numpy(), r.to_numpy()]
    if interaction:
        parts.append(np.column_stack([c[a].to_numpy() * r[b].to_numpy()
                                      for a in c.columns for b in r.columns]))
    return np.column_stack(parts)


def ols_rss(X: np.ndarray, y: np.ndarray) -> Tuple[float, int]:
    """Residual sum of squares and rank of the least-squares fit of y on X.

    Ported from: sm_open.py:_rss
    """
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid), int(rank)


def ols_fit_resid(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Fitted values and residuals of the least-squares fit of y on X.

    Ported from: sm_open.py:_fit_resid
    """
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    return fit, y - fit


def interaction_permutation_test(X_full: np.ndarray, X_add: np.ndarray, y: np.ndarray,
                                 perms: int = PERMS, seed: int = SEED) -> Dict[str, float]:
    """Interaction F test with a Freedman-Lane permutation p.

    Formula: F = ((RSS_add - RSS_full)/df_int) / (RSS_full/df_res), df_int = rank_full - rank_add,
             df_res = n - rank_full. The additive model is fitted, its residuals permuted and added
             back to the additive fit; F is recomputed on each of ``perms`` draws;
             p_perm = (1 + #{F* >= F}) / (perms + 1). p_param is the F-distribution p.
             partial eta2 = (RSS_add - RSS_full) / RSS_add. Defaults: perms 5000, seed 42, and a
             fresh default_rng(seed) per call (as the archive).
    The caller supplies y (the document used mid-ranks of priority year).

    Ported from: sm_open.py:lag_constancy (interaction block and the per-region loop)
    Used in: la_lag_constancy
    """
    from scipy import stats as _st
    rss_full, k_full = ols_rss(X_full, y)
    rss_add, k_add = ols_rss(X_add, y)
    n = len(y)
    df_int, df_res = k_full - k_add, n - k_full
    F = ((rss_add - rss_full) / df_int) / (rss_full / df_res)
    fit_add, resid_add = ols_fit_resid(X_add, y)
    rng = np.random.default_rng(seed)
    null = np.empty(perms)
    for i in range(perms):
        ystar = fit_add + rng.permutation(resid_add)
        rf, _ = ols_rss(X_full, ystar)
        ra, _ = ols_rss(X_add, ystar)
        null[i] = ((ra - rf) / df_int) / (rf / df_res)
    return {"F": float(F), "df": int(df_int), "df_res": int(df_res),
            "p_param": float(_st.f.sf(F, df_int, df_res)),
            "p_perm": float((1 + (null >= F).sum()) / (perms + 1)),
            "partial_eta2": float((rss_add - rss_full) / rss_add),
            "rss_full": float(rss_full), "rss_add": float(rss_add), "k_full": int(k_full), "k_add": int(k_add)}


def nested_f_test(X_small: np.ndarray, X_big: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    """F test of a main effect: model without it (X_small) against the additive model (X_big).

    Formula: F = ((RSS_s - RSS_b)/df) / (RSS_b/(n - k_b)), df = k_b - k_s; partial eta2 = (RSS_s - RSS_b)/RSS_s.
    Ported from: sm_open.py:lag_constancy inner _main
    Used in: la_lag_constancy (main-effect rows)
    """
    from scipy import stats as _st
    rss_s, k_s = ols_rss(X_small, y)
    rss_b, k_b = ols_rss(X_big, y)
    n = len(y)
    df = k_b - k_s
    F = ((rss_s - rss_b) / df) / (rss_b / (n - k_b))
    return {"F": float(F), "df": int(df), "p_param": float(_st.f.sf(F, df, n - k_b)),
            "partial_eta2": float((rss_s - rss_b) / rss_s)}





def adjusted_residuals(table) -> np.ndarray:
    """Adjusted standardized residual of every cell of a contingency table (Haberman 1973).

    Formula: r_ij = (O_ij - E_ij) / sqrt(E_ij * (1 - row_i/n) * (1 - col_j/n)), E_ij = row_i * col_j / n.
    Under independence each r_ij is approximately standard normal, so |r| > 1.96 marks a cell that departs from
    independence at about the 5 % level (cell by cell, no correction for the number of cells).
    New 2026-10-02 (not in the archive): used to say WHICH class makes two class mixes differ.
    Used in: notebook 40, 1.3.5 (labelled dataset against the evtol.news directory)
    """
    O = np.asarray(table, dtype=float)
    n = O.sum()
    row, col = O.sum(axis=1, keepdims=True), O.sum(axis=0, keepdims=True)
    E = row * col / n
    return (O - E) / np.sqrt(E * (1 - row / n) * (1 - col / n))
