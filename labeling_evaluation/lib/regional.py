"""Regional specialisation, lead / lag between regions, the permutation test of lag constancy, the region proximity test.

Science only: pure functions of DataFrames / arrays and parameters; no file reading, no config, no text.
Frames use the archive's column names (`region3`, `year`, `topType`, `archetype`, ...) so the caller passes the
analysis frame as it is. Distances / proximities are passed in precomputed.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats as _st

from .association import holm_adjust as _holm, interaction_permutation_test

#: the three regions, in the order every table prints them (la_tables.py:28)
REGIONS: Tuple[str, ...] = ("North America", "Europe", "Asia-Pacific")
#: last complete priority year (la_tables.py:44, ruling 2026-09-10)
LAST_COMPLETE: int = 2023
#: smallest cell of a class x region for the lag test (sm_open.py:MIN_CELL)
MIN_CELL: int = 5
#: the region every offset is measured from (sm_open.py:REFERENCE_REGION)
REFERENCE_REGION: str = "North America"
#: permutations / bootstrap draws / seed of the lag analysis (sm_open.py:PERMS, DRAWS, SEED)
PERMS: int = 5000
DRAWS: int = 2000
SEED: int = 42
#: first priority year of the "recent aircraft only" reading (sm_open.py:LAG_SINCE)
LAG_SINCE: int = 2016


# ----------------------------------------------------------------------------- specialisation
def location_quotient(counts: pd.DataFrame) -> pd.DataFrame:
    """Location quotient of each row category in each column region from a category x region count table.

    FORMULA: LQ_rc = (n_rc / n_c) / (n_r / n)  -- the category's share inside the region divided by its share overall
    (n_rc = cell, n_c = column total, n_r = row total, n = grand total). Rounded to 2 decimals.
    1 = as everywhere, 2 = twice the overall share.

    Ported from: archive la_tables.py:specialisation (arithmetic)
    Used in: la_specialisation
    """
    share_region = counts.div(counts.sum(axis=0), axis=1)
    share_all = counts.sum(axis=1) / counts.values.sum()
    return share_region.div(share_all, axis=0).round(2)


def specialisation(frame: pd.DataFrame, regions: Sequence[str] = REGIONS,
                   min_aircraft: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Location quotient of each archetype per region, keeping archetypes with at least `min_aircraft` aircraft.

    RULE: drop rows with no archetype, keep aircraft of the listed regions, keep archetypes with >= min_aircraft
    such aircraft (default 5), cross-tabulate archetype x region, order archetypes by total (descending), then
    LQ_rc = (n_rc / n_c) / (n_r / n). Returns (LQ rounded to 2 dp, counts).
    `frame` has columns `archetype`, `region3`.

    Ported from: archive la_tables.py:specialisation
    Used in: la_specialisation
    """
    regions = list(regions)
    w = frame.dropna(subset=["archetype"])
    w = w[w["region3"].isin(regions)]
    keep = w["archetype"].value_counts()
    keep = keep[keep >= min_aircraft].index
    w = w[w["archetype"].isin(keep)]
    counts = pd.crosstab(w["archetype"], w["region3"]).reindex(columns=regions, fill_value=0)
    counts = counts.loc[counts.sum(axis=1).sort_values(ascending=False).index]
    return location_quotient(counts), counts


# ----------------------------------------------------------------------------- lead / lag
def lead_lag(frame: pd.DataFrame, by: str = "region3", top: Optional[int] = None,
             regions: Sequence[str] = REGIONS, last_complete: int = LAST_COMPLETE,
             names: Optional[Mapping[str, str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cumulative share of each group's aircraft by priority year and the year it reached 25, 50, 75 %.

    RULE: aircraft with a priority year <= last_complete; years first..last_complete; per group
    cum_t = cumulative count / group total; quartile year for p = first year with cum >= p
    (np.searchsorted, left). Groups: the regions in order (by='region3') or the group sizes in descending
    order, optionally the `top` largest (otherwise). Quartile rows are sorted by the 50 % year (default
    quicksort, as the archive). `names` maps group codes to printed names for the non-region case.
    Returns (curves, quartiles); quartile columns: <by>, aircraft, first year, 25 %, 50 %, 75 %, last year counted.

    Ported from: archive la_tables.py:lead_lag
    Used in: la_lead_lag_region, la_lead_lag_class
    """
    names = names or {}
    w = frame.dropna(subset=["year"])
    w = w[w["year"] <= last_complete]
    years = np.arange(int(w["year"].min()), last_complete + 1)
    groups = w[by].value_counts()
    if by == "region3":
        groups = groups.reindex([g for g in regions if g in groups.index])
    elif top:
        groups = groups.head(top)
    curves = {}
    rows = []
    for g, n in groups.items():
        sub = w[w[by].eq(g)]
        counts = sub["year"].astype(int).value_counts().reindex(years, fill_value=0)
        cum = counts.cumsum() / counts.sum()
        curves[g] = cum
        q = {p: int(years[np.searchsorted(cum.to_numpy(), p)]) for p in (0.25, 0.5, 0.75)}
        rows.append({by: g if by == "region3" else names.get(g, g), "aircraft": int(n),
                     "first year": int(sub["year"].min()), "25 %": q[0.25], "50 %": q[0.5],
                     "75 %": q[0.75], "last year counted": last_complete})
    curves = pd.DataFrame(curves, index=years)
    quart = pd.DataFrame(rows).sort_values("50 %").reset_index(drop=True)
    return curves, quart


# ----------------------------------------------------------------------------- lag test
def lag_frame(frame: pd.DataFrame, min_cell: int = MIN_CELL, regions: Sequence[str] = REGIONS,
              last_complete: int = LAST_COMPLETE, class_names: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """The aircraft the lag test runs on: class, region, priority year; complete years; classes with all cells filled.

    RULE: rows with a year and a class (topType); year <= last_complete; region in `regions`; keep a class only
    when EVERY region holds >= min_cell aircraft of it (an interaction compares offsets; an empty cell has none).
    Output columns aircraft_id, class (class_names maps code -> printed name; unmapped codes stay), region
    (ordered Categorical over `regions`), year.

    Ported from: archive sm_open.py:lag_frame
    Used in: la_lag_offsets, la_lag_constancy
    """
    regions = list(regions)
    class_names = class_names or {}
    w = frame.dropna(subset=["year", "topType"]).copy()
    w = w[w["year"].le(last_complete) & w["region3"].isin(regions)]
    n = w.pivot_table(index="topType", columns="region3", values="year", aggfunc="size")
    n = n.reindex(columns=regions).fillna(0)
    keep = n[(n >= min_cell).all(axis=1)].index
    w = w[w["topType"].isin(keep)].copy()
    w["class"] = [class_names.get(c, c) for c in w["topType"]]
    w["region"] = pd.Categorical(w["region3"], categories=regions, ordered=True)
    return w[["aircraft_id", "class", "region", "year"]].reset_index(drop=True)


def lag_offsets(w: pd.DataFrame, regions: Sequence[str] = REGIONS, reference: str = REFERENCE_REGION,
                draws: int = DRAWS, seed: int = SEED) -> pd.DataFrame:
    """Each class's regional offset in priority year against a reference region, with a bootstrap interval.

    FORMULA: offset = median(year | class, region) - median(year | class, reference); interval = 2.5 / 97.5
    percentiles of `draws` bootstrap offsets, each resampling aircraft with replacement INSIDE the class-region cell
    and inside the class-reference cell (one default_rng(seed) consumed over classes in group order, regions in
    order, per draw: region cell first, then reference cell). Offset and bounds rounded to 1 decimal.
    > 0 means the region filed LATER than the reference. `w` is the output of lag_frame.

    Ported from: archive sm_open.py:lag_offsets
    Used in: la_lag_offsets
    """
    rng = np.random.default_rng(seed)
    rows = []
    for cls, sub in w.groupby("class", observed=True):
        ref = sub.loc[sub["region"].eq(reference), "year"].to_numpy()
        for reg in regions:
            arr = sub.loc[sub["region"].eq(reg), "year"].to_numpy()
            if not len(arr) or not len(ref):
                continue
            obs = float(np.median(arr) - np.median(ref))
            d = np.array([np.median(rng.choice(arr, len(arr), replace=True))
                          - np.median(rng.choice(ref, len(ref), replace=True))
                          for _ in range(draws)])
            rows.append({"class": cls, "region": reg, "aircraft": int(len(arr)),
                         "median priority year": float(np.median(arr)),
                         "offset vs North America (years)": round(obs, 1),
                         "95 % low": round(float(np.percentile(d, 2.5)), 1),
                         "95 % high": round(float(np.percentile(d, 97.5)), 1)})
    return pd.DataFrame(rows)


def lag_design(w: pd.DataFrame, interaction: bool) -> np.ndarray:
    """Reference-coded dummy design for class + region (+ class x region) with an intercept.

    Ported from: archive sm_open.py:_design
    """
    cls = pd.get_dummies(w["class"], drop_first=True, dtype=float)
    reg = pd.get_dummies(w["region"], drop_first=True, dtype=float)
    parts = [np.ones((len(w), 1)), cls.to_numpy(), reg.to_numpy()]
    if interaction:
        inter = np.column_stack([cls[c].to_numpy() * reg[r].to_numpy()
                                 for c in cls.columns for r in reg.columns])
        parts.append(inter)
    return np.column_stack(parts)


def rss_rank(X: np.ndarray, y: np.ndarray) -> Tuple[float, int]:
    """Residual sum of squares of the least-squares fit of y on X and the rank of X.

    Ported from: archive sm_open.py:_rss
    """
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid), int(rank)


def fit_resid(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Fitted values and residuals of the least-squares fit of y on X.

    Ported from: archive sm_open.py:_fit_resid
    """
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    return fit, y - fit




def lag_constancy(w: pd.DataFrame, offsets: pd.DataFrame, regions: Sequence[str] = REGIONS,
                  reference: str = REFERENCE_REGION, perms: int = PERMS, seed: int = SEED) -> pd.DataFrame:
    """Is the regional lag the same in every class? Interaction test on mid-ranks of priority year.

    RULE: y = mid-ranks of year (scipy rankdata average). Rows: the joint class x region interaction (full vs
    additive model, permutation p, see interaction_permutation_test), the region main effect and the class main
    effect (each model without it against the additive, parametric F only, F rounded 2 dp, partial eta² 4 dp), then
    one interaction test per non-reference region on the aircraft of that region and the reference (own
    default_rng(seed) each), permutation p, plus Holm-adjusted p across those region rows. F rounded 2 dp,
    partial eta² 4 dp, p unrounded.
    `w` = lag_frame output; `offsets` = lag_offsets output, used for the per-region min / max / median of the
    offsets (the 'spread') carried in attrs['offset_spread'] for the verdict.
    The output has the archive's columns except `verdict` (text); attrs['verdict_code'] / ['verdict_regions'] hold the
    coded verdict from lag_verdict.

    Ported from: archive sm_open.py:lag_constancy
    Used in: la_lag_constancy
    """
    y = _st.rankdata(w["year"].to_numpy())
    Xfull = lag_design(w, True)
    Xadd = lag_design(w, False)
    Xcls = np.column_stack([np.ones(len(w)),
                            pd.get_dummies(w["class"], drop_first=True, dtype=float).to_numpy()])
    Xreg = np.column_stack([np.ones(len(w)),
                            pd.get_dummies(w["region"], drop_first=True, dtype=float).to_numpy()])
    joint = interaction_permutation_test(Xfull, Xadd, y, perms, seed)
    rss_add, k_add = joint["rss_add"], joint["k_add"]
    n = len(w)

    def _main(Xsmall, label):
        rss_s, k_s = rss_rank(Xsmall, y)
        df = k_add - k_s
        F = ((rss_s - rss_add) / df) / (rss_add / (n - k_add))
        return {"effect": label, "df": df, "F (on ranks)": round(float(F), 2),
                "p (parametric)": float(_st.f.sf(F, df, n - k_add)),
                "partial η²": round(float((rss_s - rss_add) / rss_s), 4)}

    non_ref = offsets[offsets["region"].ne(reference)]
    spread = (non_ref.groupby("region", observed=True)["offset vs North America (years)"]
              .agg(["min", "max", "median"]))
    rows = [{"effect": "joint", "df": joint["df"], "F (on ranks)": round(joint["F"], 2),
             "p (parametric)": joint["p_param"], "p (permutation)": joint["p_perm"],
             "partial η²": round(joint["partial_eta2"], 4), "permutations": perms}]
    rows.append(_main(Xcls, "region"))
    rows.append(_main(Xreg, "class"))
    for reg in regions:
        if reg == reference:
            continue
        sub = w[w["region"].isin([reference, reg])].copy()
        sub["region"] = sub["region"].astype(str)
        ysub = _st.rankdata(sub["year"].to_numpy())
        r = interaction_permutation_test(lag_design(sub, True), lag_design(sub, False), ysub, perms, seed)
        rows.append({"effect": f"region {reg}", "region tested": reg, "aircraft": int(len(sub)),
                     "df": r["df"], "F (on ranks)": round(r["F"], 2), "p (parametric)": r["p_param"],
                     "p (permutation)": r["p_perm"], "partial η²": round(r["partial_eta2"], 4),
                     "permutations": perms})
    out = pd.DataFrame(rows)
    out["aircraft"] = out.get("aircraft", pd.Series(np.nan, index=out.index)).fillna(n).astype(int)
    out["classes"] = w["class"].nunique()
    reg_rows = out[out["effect"].str.startswith("region ")].copy()
    _p = reg_rows["p (permutation)"].to_dict()
    holm = dict(zip(_p, (round(float(x), 4) for x in _holm(list(_p.values()))))) if len(reg_rows) else {}
    out["p (Holm, across the two regions)"] = pd.Series(holm)
    code, named = lag_verdict(joint["p_perm"], spread, reg_rows.assign(
        holm=[holm.get(i) for i in reg_rows.index]))
    out.attrs["verdict_code"] = code
    out.attrs["verdict_regions"] = named
    out.attrs["offset_spread"] = spread
    return out


def lag_verdict(p_perm: float, spread: pd.DataFrame, reg: Optional[pd.DataFrame] = None) -> Tuple[str, List]:
    """Coded verdict on the constancy of the lag from the joint permutation p and the one-region tests.

    RULE: p_perm < 0.05 -> 'not_constant' (no region named); else p_perm < 0.10 -> 'borderline'; else 'consistent'.
    Regions that move are listed for both of the last two codes (the archive prints them only in the 'borderline'
    sentence): regions with Holm p < 0.05 -> ('holm', region, holm p); if there are none, regions with raw permutation
    p < 0.05 -> ('raw', region, p, holm p). `reg` needs columns 'region tested', 'p (permutation)', 'holm'.
    `spread` (per-region min / max / median of the offsets) only feeds the offset-range clause of the archive's
    sentence and does not change the code; it is kept in the signature.

    Returns (code, named) with named = list of tuples.

    Ported from: archive sm_open.py:_lag_verdict (logic only; the sentence is not built)
    Used in: la_lag_constancy (column 'verdict')
    """
    if p_perm < 0.05:
        return "not_constant", []
    named: List = []
    if reg is not None and len(reg):
        hits = reg[reg["holm"].astype(float) < 0.05] if "holm" in reg else reg.iloc[:0]
        raw = reg[reg["p (permutation)"].astype(float) < 0.05]
        if len(hits):
            named = [("holm", r["region tested"], float(r["holm"])) for _, r in hits.iterrows()]
        elif len(raw):
            named = [("raw", r["region tested"], float(r["p (permutation)"]), float(r["holm"]))
                     for _, r in raw.iterrows()]
    if p_perm < 0.10:
        return "borderline", named
    return "consistent", named


def lag_offsets_since(frame: pd.DataFrame, since: int = LAG_SINCE, regions: Sequence[str] = REGIONS,
                      reference: str = REFERENCE_REGION, last_complete: int = LAST_COMPLETE,
                      min_cell: int = MIN_CELL, class_names: Optional[Mapping[str, str]] = None,
                      draws: int = DRAWS, seed: int = SEED) -> pd.DataFrame:
    """The regional offsets of lag_offsets on aircraft with a priority year >= `since` only, plus an all-classes row per region.

    RULE: keep rows with year >= since; run lag_frame + lag_offsets on them; then for each region one row with
    class 'all classes': aircraft with year <= last_complete in that region, their median priority year, and its
    offset from the reference region's median (rounded 1 dp), interval NaN. Column 'priority years' =
    '<since>-<last_complete>'.

    Ported from: archive sm_open.py:lag_offsets_since
    Used in: la_lag_offsets_2016
    """
    vv = frame[pd.to_numeric(frame["year"], errors="coerce").ge(since)]
    out = lag_offsets(lag_frame(vv, min_cell, regions, last_complete, class_names), regions, reference, draws, seed)
    w = vv[vv["year"].le(last_complete) & vv["region3"].isin(list(regions))]
    med = w.groupby("region3")["year"].median()
    rows = [{"class": "all classes", "region": r, "aircraft": int(w["region3"].eq(r).sum()),
             "median priority year": float(med.get(r, np.nan)),
             "offset vs North America (years)": round(float(med.get(r, np.nan) - med.get(reference, np.nan)), 1),
             "95 % low": np.nan, "95 % high": np.nan} for r in regions]
    out = pd.concat([out, pd.DataFrame(rows)], ignore_index=True)
    out["priority years"] = f"{since}-{last_complete}"
    return out


def region_lag(frame: pd.DataFrame, regions: Sequence[str] = REGIONS,
               lo: int = 2016, hi: int = 2021) -> pd.DataFrame:
    """Per region: publication lag of its aircraft of priority years lo..hi (median, share published within 0-3 years), main office.

    FORMULA: lag = pub_year - year; per region the aircraft with year in [lo, hi] (inclusive);
    median lag over those with a lag; 'its share' = (aircraft at the most frequent publication office) / (all aircraft
    of the region in the window), rounded 3 dp; published within k y = mean(lag <= k) over aircraft with a lag,
    k = 0..3, rounded 3 dp. `frame` has columns region3, year, pub_year (numeric or coercible), pub_office.

    Ported from: archive sm_open.py:region_lag
    Used in: la_region_lag
    """
    j = frame.assign(lag=pd.to_numeric(frame["pub_year"], errors="coerce") - frame["year"])
    rows = []
    for r in regions:
        s = j[j["region3"].eq(r) & j["year"].between(lo, hi)]
        lag = s["lag"].dropna()
        off = s["pub_office"].value_counts()
        row = {"region": r, "aircraft 2016-21": int(len(lag)), "median lag (years)": float(lag.median()),
               "main office": str(off.index[0]), "its share": round(float(off.iloc[0] / len(s)), 3)}
        for k in range(4):
            row[f"published within {k} y"] = round(float((lag <= k).mean()), 3)
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- region proximity
def region_pair_table(prox, labels) -> pd.DataFrame:
    """Every firm pair of a proximity matrix with its value and the two regions it joins.

    The pair order is the upper triangle of the matrix in ROW-MAJOR order (i < j), as the archive builds it from
    the firm order. `prox` is a square matrix (array or DataFrame) in the firm order, `labels` the region of each
    firm in that same order.

    Ported from: archive la_tables.py:proximity_by_region (pair list)
    """
    P = np.asarray(prox, dtype=float)
    lab = np.asarray(labels, dtype=object)
    ia, ib = np.triu_indices(len(lab), k=1)
    return pd.DataFrame({"a": ia, "b": ib, "proximity": P[ia, ib],
                         "region a": lab[ia], "region b": lab[ib],
                         "pair": [" / ".join(sorted([str(x), str(y)])) for x, y in zip(lab[ia], lab[ib])],
                         "same region": lab[ia] == lab[ib]})


def region_proximity_test(prox, labels, draws: int = 10000, seed: int = 42) -> Dict:
    """Is a firm closer to the firms of its own region than to firms of another? Permutation test on region labels.

    FORMULA: obs = mean(proximity of same-region pairs) - mean(proximity of different-region pairs);
    null: shuffle the region labels over the firms (rng = default_rng(seed), rng.permutation of the label array in
    the given firm order, one call per draw), recompute the same difference; a draw with all pairs same-region or
    none same-region is SKIPPED (counted as a non-hit but still a draw); p = (#draws with diff >= obs) / draws
    (one-sided, no +1 correction), rounded to 3 dp.
    `prox` is the precomputed square proximity matrix in the firm order, `labels` the firms' regions in that order.
    NOTE: the order of the labels determines the RNG stream, so the caller must pass the firm order the archive uses
    (region blocks, clustered order inside a block).
    Returns dict(same_mean, same_pairs, different_mean, different_pairs, gap, p, draws), rounded as printed (means and gap 3 dp).

    Ported from: archive la_tables.py:proximity_by_region (permutation part); sm_open.py:region_proximity_test
    Used in: la_region_proximity_test, la_proximity_region
    """
    p = region_pair_table(prox, labels)
    same = p.loc[p["same region"], "proximity"]
    diff = p.loc[~p["same region"], "proximity"]
    obs = float(same.mean() - diff.mean())
    rng = np.random.default_rng(seed)
    ia = p["a"].to_numpy()
    ib = p["b"].to_numpy()
    val = p["proximity"].to_numpy()
    lab = np.asarray(labels)
    hits = 0
    for _ in range(draws):
        perm = rng.permutation(lab)
        s = perm[ia] == perm[ib]
        if s.all() or not s.any():
            continue
        if val[s].mean() - val[~s].mean() >= obs:
            hits += 1
    return {"same_mean": round(float(same.mean()), 3), "same_pairs": int(len(same)),
            "different_mean": round(float(diff.mean()), 3), "different_pairs": int(len(diff)),
            "gap": round(obs, 3), "p": round(hits / draws, 3), "draws": int(draws)}


def region_pair_summary(prox, labels) -> pd.DataFrame:
    """Mean / median / min / max proximity of the firm pairs, per region pair, rounded to 2 dp.

    Columns: region pair, pairs, mean, median, lowest, highest, 'within' flag ('within' when both regions are the
    same, else 'across'). Row order is the sorted region-pair name (groupby).

    Ported from: archive la_tables.py:proximity_by_region (summary table)
    Used in: la_proximity_region
    """
    p = region_pair_table(prox, labels)
    summary = (p.groupby("pair")["proximity"]
               .agg(**{"pairs": "size", "mean": "mean", "median": "median",
                       "lowest": "min", "highest": "max"}).round(2))
    summary.index.name = "region pair"
    summary = summary.reset_index()
    summary["within a region?"] = np.where(
        summary["region pair"].str.split(" / ").map(lambda t: t[0] == t[-1]), "within", "across")
    return summary
