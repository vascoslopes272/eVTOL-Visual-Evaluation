"""Tables of the Labelling Analysis that the Preliminary Analysis does not have.

Every function takes the live :class:`Dataset` (and the atlas variant frame where
it helps) and returns a DataFrame; nothing is typed. The frames the figures of
``la_figures`` draw come from here too, so a table and its figure can never
disagree. External inputs: the AAM Reality Index CSVs under
``assets/external/aam_reality_index`` and the evtol.news links of ``EVTOLNEWS_DS``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import a2, a3, la_baseline, metrics
from .loaders import Dataset

ASSETS = Path(__file__).resolve().parents[2] / "assets"
ARI_DIR = ASSETS / "external" / "aam_reality_index"
EVTOLNEWS = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/EVTOLNEWS_DS")

WINDOWS = a2.WINDOWS
WINDOW_NAMES = [w[0] for w in WINDOWS]
REGIONS = ["North America", "Europe", "Asia-Pacific"]
#: G1 classes folded to the five evtol.news directory classes (user ruling 2026-09-22:
#: Lift + Cruise = fixed thrust, every tilting class = vectored thrust, the rest to the rest)
FOLD5: Dict[str, str] = {
    "SLC": "LC", "TR": "VT", "TW": "VT", "CVT": "VT", "TB": "VT", "PTC": "VT", "DS": "VT",
    "MR": "WM", "RC": "ER", "SRW": "ER", "HB": "HB", "PFV": "HB",
}
FOLD5_NAMES = {"VT": "Vectored Thrust", "LC": "Lift + Cruise", "WM": "Wingless (Multicopter)",
               "ER": "Electric Rotorcraft", "HB": "Hover Bikes / Personal Flying Devices"}
FIRM_MIN = 5          # firms with this many unique aircraft carry a profile
#: named filers that are universities, institutes or agencies rather than companies
INSTITUTE_RE = r"(?i)univ|institute|college|kaist|\bkari\b|\bnasa\b|\bjaxa\b|casic|nuaa|nudt|chrdi|comac research|polytech|academy|research"
BIG4 = ["SLC", "TR", "CVT", "TW"]
LAST_COMPLETE = 2023  # every trend claim ends here (ruling 2026-09-10)

#: Propulsive units per aircraft, banded. The cuts are those of :data:`a2.ROTOR_BINS` (the
#: A0c archetype level), but the bottom band is labelled by what it actually holds: no
#: aircraft flies on nothing, so "0-3" is written "1-3" (user ruling 2026-09-22). The two
#: cases that would otherwise hide inside a band are named in full instead of being counted
#: as zero -- the Hoverbike and Personal Flying Vehicle aircraft, which the codebook gives no
#: propulsor card at all, and the single aircraft whose record carries a literal 0.
#: a2.ROTOR_BINS itself is untouched: it feeds the Preliminary Analysis, which must render
#: unchanged. Defined here, before its first use, because :data:`_BINS` reads it at import.
UNIT_BANDS = ([0, 3, 4, 6, 8, 10 ** 6], ["1-3", "4", "5-6", "7-8", "9+"])
NO_UNIT_CARD = "no propulsor card"
UNIT_ZERO = "0 recorded"


# ------------------------------------------------------------------ frames --
def base(ds: Dataset) -> pd.DataFrame:
    """One row per unique aircraft with year, window, region, filer, company, class and
    the derived propulsion fields; the frame every table and figure here starts from."""
    af = a2.archetype_frame(ds)[["aircraft_id", "rotorBin", "anyTilt", "nBooms"]]
    v = ds.variants.merge(
        ds.identity[["patent_id", "priority_year", "region", "assignee_country", "company_canonical",
                     "legal_status_raw", "pub_office", "industry_primary", "claim_count", "forward_citations",
                     "backward_citations", "forward_citations_in_corpus", "self_citations_in_corpus", "family_size",
                     "kind_code"]],
        on="patent_id", how="left", suffixes=("", "_id"))
    v = v.merge(af, on="aircraft_id", how="left")
    ps = a2.propulsion_states(ds.variants)
    for c in ("any_tilting", "any_ducted", "any_fixed"):
        v[c] = ps[c].to_numpy()
    v["units"] = a2.propulsor_units(ds.variants)["units"].to_numpy()
    v["year"] = pd.to_numeric(v["priority_year"], errors="coerce")
    v["window"] = v["year"].map(a2.window_of)
    v["region3"] = v["region"].where(v["region"].isin(REGIONS), "Other regions")
    cc = v["company_canonical"]
    inst = cc.fillna("").str.contains(INSTITUTE_RE, regex=True)
    v["filer"] = np.select([cc.eq(a2.CATCH_ALL[0]), cc.eq(a2.CATCH_ALL[1]) | cc.isna(), inst],
                           ["Individual inventor", "Unattributed / independent", "University / institute"], "Named company")
    v["named"] = v["filer"].isin(["Named company", "University / institute"])
    # a filer id: the firm for a named company, the patent for everyone else
    v["filer_id"] = np.where(v["named"], cc.fillna(""), "patent:" + v["patent_id"].astype(str))
    v["class5"] = v["topType"].map(FOLD5)
    # Display-only, Labelling Analysis side: a2's bottom propulsor bin prints "0-3" although no
    # aircraft flies on nothing (user ruling 2026-09-22). Relabelled here, once, before the
    # archetype key is built, so every rendered A0c key follows -- 4.1.3, 4.1.8, 4.1.9 and the
    # specialisation table -- without any table builder changing. It is a 1:1 rename of one
    # category: no archetype count, top share, Hill number or permutation band can move, and
    # a2.ROTOR_BINS is untouched so the Preliminary Analysis renders exactly as before.
    # The corpus holds one aircraft recorded with 0 units; it stays inside this band (splitting
    # it out would change the A0c counts) and is named instead in :func:`flags`.
    v["rotorBin"] = v["rotorBin"].replace(a2.ROTOR_BINS[1][0], UNIT_BANDS[1][0])
    v["archetype"] = np.where(v["topType"].notna() & v["rotorBin"].notna(),
                              v["topType"].astype(str) + " · " + v["rotorBin"].astype(str), None)
    # The honest exception: one aircraft in the corpus really is recorded with 0 propulsive
    # units (a labelling gap, not a design), and its class would otherwise be printed as
    # "1-3" -- a false statement. That class keeps the original label in the printed key.
    # It is a 1:1 rename inside ``archetype``, which is itself the group key, so no count,
    # share or diversity number moves; only the row's name changes.
    zero = set(v.loc[pd.to_numeric(v["units"], errors="coerce").eq(0), "topType"].dropna().astype(str))
    if zero:
        tail = " · " + UNIT_BANDS[1][0]
        mask = v["topType"].astype(str).isin(zero) & v["archetype"].astype(str).str.endswith(tail)
        v.loc[mask, "archetype"] = (v.loc[mask, "archetype"].astype(str)
                                    .str.slice(stop=-len(tail)) + " · " + a2.ROTOR_BINS[1][0])
    status = v["legal_status_raw"].fillna("").astype(str)
    v["lapsed"] = status.str.startswith("INACTIVE")
    v["granted"] = status.str.contains("GRANTED")
    return v


def firm_sizes(v: pd.DataFrame) -> pd.Series:
    """Unique aircraft per named company, largest first."""
    return v.loc[v["named"], "company_canonical"].value_counts()


# ------------------------------------------------------- 4.1 convergence ----
def firm_weighted_shares(v: pd.DataFrame, types: Optional[List[str]] = None) -> pd.DataFrame:
    """Class share per window counted two ways: by aircraft, and one vote per filer.

    A named firm votes once per window, for the class it filed most in that window; an
    individual or unattributed patent is its own filer and votes once per aircraft.
    """
    types = types or ["TR", "SLC", "CVT", "MR", "TW"]
    w = v.dropna(subset=["window", "topType"])
    rows = []
    for name in WINDOW_NAMES:
        sub = w[w["window"].eq(name)]
        votes = (sub.groupby("filer_id")["topType"]
                 .agg(lambda s: s.value_counts().index[0]))
        by_air = sub["topType"].value_counts(normalize=True)
        by_filer = votes.value_counts(normalize=True)
        for t in types:
            rows.append({"window": name, "class": metrics.ARCH_NAMES.get(t, t),
                         "aircraft": int(len(sub)), "filers": int(len(votes)),
                         "share by aircraft": round(float(by_air.get(t, 0)), 3),
                         "share by filer": round(float(by_filer.get(t, 0)), 3)})
    return pd.DataFrame(rows)


def lead_lag(v: pd.DataFrame, by: str = "region3", top: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cumulative share of each group's own aircraft by priority year (complete years only)
    and the year each group reached 25, 50 and 75 % of its output.

    Returns (curves, quartiles). ``by`` is ``region3`` or ``topType``.
    """
    w = v.dropna(subset=["year"])
    w = w[w["year"] <= LAST_COMPLETE]
    years = np.arange(int(w["year"].min()), LAST_COMPLETE + 1)
    groups = w[by].value_counts()
    if by == "region3":
        groups = groups.reindex([g for g in REGIONS if g in groups.index])
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
        rows.append({by: g if by == "region3" else metrics.ARCH_NAMES.get(g, g), "aircraft": int(n),
                     "first year": int(sub["year"].min()), "25 %": q[0.25], "50 %": q[0.5],
                     "75 %": q[0.75], "last year counted": LAST_COMPLETE})
    curves = pd.DataFrame(curves, index=years)
    quart = pd.DataFrame(rows).sort_values("50 %").reset_index(drop=True)
    return curves, quart


def class_cycles(v: pd.DataFrame) -> pd.DataFrame:
    """Each class over the windows as a share of its own total (row %), with n."""
    w = v.dropna(subset=["window", "topType"])
    tab = pd.crosstab(w["topType"], w["window"]).reindex(columns=WINDOW_NAMES, fill_value=0)
    order = tab.sum(axis=1).sort_values(ascending=False).index
    tab = tab.loc[order]
    share = tab.div(tab.sum(axis=1), axis=0)
    # median window: the window in which the class passes half its aircraft
    med = []
    for c in tab.index:
        cum = tab.loc[c].cumsum() / tab.loc[c].sum()
        med.append(WINDOW_NAMES[int(np.searchsorted(cum.to_numpy(), 0.5))])
    out = share.round(3)
    out.insert(0, "aircraft", tab.sum(axis=1))
    out["median window"] = med
    out.index = [metrics.ARCH_NAMES.get(c, c) for c in out.index]
    out.index.name = "class"
    return out.reset_index()


def hill_numbers(labels: pd.Series, n: int = 40, draws: int = 1000, seed: int = 42) -> Dict[str, float]:
    """Rarefied Hill numbers of orders 0, 1, 2 at sample size n (mean and 95 % band)."""
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


def hill_by_window(v: pd.DataFrame, n: int = 40) -> pd.DataFrame:
    """Rarefied Hill numbers per window at A0 (class) and A0c (class × propulsive-unit bin)."""
    rows = []
    for level, col in (("A0 class", "topType"), ("A0c class × propulsive-unit bin", "archetype")):
        w = v.dropna(subset=["window", col])
        for name in WINDOW_NAMES:
            sub = w[w["window"].eq(name)]
            if len(sub) < 10:
                continue
            r = hill_numbers(sub[col], n=n)
            rows.append({"level": level, "window": name, **r})
    return pd.DataFrame(rows)


def zones(v: pd.DataFrame, min_aircraft: int = 5) -> pd.DataFrame:
    """A0c archetypes with ``min_aircraft`` or more: aircraft, distinct filers, first and last
    window, share of the complete windows 2016-23, and a zone label.

    Zone: *new* = first seen in 2016-19 or later; *fading* = not seen after 2016-19;
    *persistent* otherwise. Filers = named firms plus one per individual/unattributed patent.
    """
    w = v.dropna(subset=["archetype", "window"])
    g = w.groupby("archetype")
    tab = pd.crosstab(w["archetype"], w["window"]).reindex(columns=WINDOW_NAMES, fill_value=0)
    recent = w[w["window"].isin(["2016-19", "2020-23"])]
    share_recent = recent["archetype"].value_counts(normalize=True)
    filers_recent = recent.groupby("archetype")["filer_id"].nunique()
    rows = []
    for a, sub in g:
        if len(sub) < min_aircraft:
            continue
        present = [wn for wn in WINDOW_NAMES if tab.loc[a, wn] > 0]
        first, last = present[0], present[-1]
        if WINDOW_NAMES.index(first) >= 2:
            zone = "new"
        elif WINDOW_NAMES.index(last) <= 2:
            zone = "fading"
        else:
            zone = "persistent"
        cls = sub["topType"].iloc[0]
        rows.append({"archetype": a, "class": metrics.ARCH_NAMES.get(cls, cls), "code": cls,
                     "aircraft": int(len(sub)), "filers": int(sub["filer_id"].nunique()),
                     "named firms": int(sub.loc[sub["named"], "company_canonical"].nunique()),
                     "filers per aircraft": round(float(sub["filer_id"].nunique() / len(sub)), 2),
                     "share 2016-23": round(float(share_recent.get(a, 0)), 3),
                     "filers 2016-23": int(filers_recent.get(a, 0)),
                     "first window": first, "last window": last, "zone": zone,
                     **{wn: int(tab.loc[a, wn]) for wn in WINDOW_NAMES}})
    out = pd.DataFrame(rows).sort_values(["aircraft"], ascending=False).reset_index(drop=True)
    return out


def class_filer_weight(v: pd.DataFrame) -> pd.DataFrame:
    """How much of each class is one filer repeating itself (author's question, 2026-09-23).

    A class can look large for two different reasons: many different people chose that
    architecture, or one company filed the same architecture again and again. This table
    separates them. Per class:

    * ``aircraft`` / ``filers`` — size, and how many distinct filers hold it. A filer is a
      named firm; an individual or unattributed patent is its own filer, so no two lone
      inventors are merged.
    * ``largest filer`` and ``its share`` — the single biggest contributor and the fraction
      of the class it holds. This is the direct answer: the most one company can be worth.
    * ``top 3 share`` — the same for the three biggest together.
    * ``effective filers`` — 1 / Σ(share²) over filers: the number of *equally sized* filers
      that would give the same concentration. Equal to the filer count when every filer holds
      one aircraft, and it falls towards 1 as one filer takes the class over.
    * ``share by aircraft`` against ``share one vote per filer`` — the class's share of the
      whole corpus counted each way. A class inflated by one firm repeating itself shrinks
      when every filer votes once; the ratio of the two columns is how much of the class's
      apparent size is repetition.

    The unit is the unique aircraft throughout, so a firm that filed four patents on one
    aircraft counts once, and only a firm with several *different* aircraft moves the numbers.
    """
    w = v.dropna(subset=["topType"])
    total = len(w)
    # one vote per filer: the class that filer filed most (ties break on the class's own size)
    size = w["topType"].value_counts()
    vote = (w.groupby("filer_id")["topType"]
            .agg(lambda s: s.value_counts().sort_values(ascending=False)
                 .reindex(sorted(set(s), key=lambda c: -size.get(c, 0)), fill_value=0).idxmax()))
    votes = vote.value_counts()
    rows = []
    for c, sub in w.groupby("topType"):
        cnt = sub["filer_id"].value_counts()
        p = cnt / cnt.sum()
        top = cnt.index[0]
        name = top.split("patent:")[-1] + " (one patent)" if str(top).startswith("patent:") else top
        by_air = len(sub) / total
        by_vote = float(votes.get(c, 0)) / float(votes.sum())
        rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "aircraft": int(len(sub)),
                     "filers": int(cnt.size),
                     "named firms": int(sub.loc[sub["named"], "company_canonical"].nunique()),
                     "largest filer": name, "its aircraft": int(cnt.iloc[0]),
                     "its share": round(float(cnt.iloc[0] / len(sub)), 3),
                     "top 3 share": round(float(cnt.head(3).sum() / len(sub)), 3),
                     "effective filers": round(1.0 / float((p ** 2).sum()), 1),
                     "share by aircraft": round(by_air, 3),
                     "share one vote per filer": round(by_vote, 3),
                     "repetition factor": round(by_air / by_vote, 2) if by_vote else None})
    return pd.DataFrame(rows).sort_values("aircraft", ascending=False).reset_index(drop=True)


def class_window_filer_weight(v: pd.DataFrame, min_n: int = 10) -> pd.DataFrame:
    """The same question inside one window: for each class × window, the share held by its
    single largest filer. This is what answers "is that bar one company?" — the author's
    reading of the 2020-23 CVT bar. Cells under ``min_n`` aircraft are left out: a share taken
    on 4 aircraft says nothing."""
    w = v.dropna(subset=["topType", "window"])
    rows = []
    for (c, wn), sub in w.groupby(["topType", "window"]):
        if len(sub) < min_n:
            continue
        cnt = sub["filer_id"].value_counts()
        top = cnt.index[0]
        rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": wn,
                     "aircraft": int(len(sub)), "filers": int(cnt.size),
                     "largest filer": ("one patent" if str(top).startswith("patent:") else top),
                     "its aircraft": int(cnt.iloc[0]),
                     "its share": round(float(cnt.iloc[0] / len(sub)), 3)})
    out = pd.DataFrame(rows)
    if len(out):
        out["_w"] = out["window"].map({n: i for i, n in enumerate(WINDOW_NAMES)})
        out = out.sort_values(["aircraft", "_w"], ascending=[False, True]).drop(columns="_w")
    return out.reset_index(drop=True)


def abandonment_by_class(v: pd.DataFrame, max_year: int = 2019) -> pd.DataFrame:
    """Share of primary patents lapsed (any INACTIVE status), per class, priority ≤ max_year
    so that every patent had time to be granted and then kept or dropped."""
    w = v[v["year"].le(max_year) & v["topType"].notna()].drop_duplicates("patent_id")
    g = w.groupby("topType").agg(patents=("patent_id", "size"), lapsed=("lapsed", "sum"),
                                 granted=("granted", "sum"))
    g["lapsed share"] = (g["lapsed"] / g["patents"]).round(2)
    g["granted share"] = (g["granted"] / g["patents"]).round(2)
    g = g.sort_values("patents", ascending=False)
    g.index = [metrics.ARCH_NAMES.get(c, c) for c in g.index]
    g.index.name = "class"
    allrow = pd.DataFrame({"patents": [len(w)], "lapsed": [int(w["lapsed"].sum())],
                           "granted": [int(w["granted"].sum())],
                           "lapsed share": [round(w["lapsed"].mean(), 2)],
                           "granted share": [round(w["granted"].mean(), 2)]}, index=["all classes"])
    return pd.concat([g, allrow]).reset_index().rename(columns={"index": "class"})


# ------------------------------------------------------- 4.2 provenance ----
GRID_VARIABLES = {
    "class": ("topType", None),
    # the bin labels must match the relabelled ``rotorBin`` of :func:`base`, or the bottom
    # category silently drops out of Figure 4.3.2a
    "propulsive units": ("rotorBin", ["1-3", "4", "5-6", "7-8", "9+"]),
    "tilting unit": ("any_tilting", [True, False]),
    "ducted unit": ("any_ducted", [True, False]),
    "powertrain": ("is_electric_final", ["Yes", "Hybrid", "Unknown", "No"]),
    "filer type": ("filer", ["Named company", "University / institute", "Individual inventor", "Unattributed / independent"]),
}


def region_window_shares(v: pd.DataFrame, variable: str, min_n: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Share of each answer per region × window (rows) for one variable; cells with fewer
    than ``min_n`` aircraft are blanked. Returns (shares, n)."""
    col, order = GRID_VARIABLES[variable]
    w = v.dropna(subset=["window"])
    w = w[w["region3"].isin(REGIONS)]
    key = w[col]
    if col in ("any_tilting", "any_ducted"):
        key = key.map({True: True, False: False})
    tab = pd.crosstab([w["region3"], w["window"]], key.fillna("blank") if col != "topType" else key)
    if order:
        tab = tab.reindex(columns=[o for o in order if o in tab.columns], fill_value=0)
    n = w.groupby(["region3", "window"]).size()
    shares = tab.div(tab.sum(axis=1), axis=0)
    shares[n.reindex(shares.index).lt(min_n)] = np.nan
    return shares, n


def country_class(v: pd.DataFrame, top: int = 8) -> Tuple[pd.DataFrame, pd.Series]:
    """Class share per assignee country (top ``top`` countries), row-normalised, with n."""
    w = v.dropna(subset=["topType", "assignee_country"])
    n = w["assignee_country"].value_counts().head(top)
    tab = pd.crosstab(w["assignee_country"], w["topType"]).reindex(n.index)
    cols = tab.sum().sort_values(ascending=False).index
    return tab[cols].div(tab.sum(axis=1), axis=0), n


# ------------------------------------------------------- 4.3 assignees -----
def firm_tiers(v: pd.DataFrame) -> pd.DataFrame:
    sizes = firm_sizes(v)
    total = len(v)
    rows = []
    for rule, k in (("10 or more aircraft", 10), ("5 or more aircraft", 5), ("4 or more aircraft", 4),
                    ("3 or more aircraft", 3), ("2 or more aircraft", 2), ("all named companies", 1)):
        sel = sizes[sizes >= k]
        rows.append({"rule": rule, "firms": int(len(sel)), "aircraft": int(sel.sum()),
                     "share of the analysis set": round(float(sel.sum() / total), 2),
                     "share of named-company aircraft": round(float(sel.sum() / sizes.sum()), 2)})
    for name, key in (("of which universities / institutes", "University / institute"),
                      ("individual inventors", "Individual inventor"),
                      ("unattributed or independent", "Unattributed / independent")):
        k = int(v["filer"].eq(key).sum())
        rows.append({"rule": name, "firms": "", "aircraft": k,
                     "share of the analysis set": round(k / total, 2), "share of named-company aircraft": ""})
    return pd.DataFrame(rows)


def firm_frame(v: pd.DataFrame) -> pd.DataFrame:
    """One row per named firm: aircraft, representative patents, distinct classes, first and last
    priority year, windows active, region — the frame the coverage and market-standing readings
    of 4.2.1 are taken on. Index is the canonical company."""
    w = v[v["named"]]
    yrs = w.groupby("company_canonical")["year"]
    f = pd.DataFrame({
        "unique aircraft": firm_sizes(v),
        "patents": w.groupby("company_canonical")["patent_id"].nunique(),
        "distinct classes": w.groupby("company_canonical")["topType"].nunique(),
        "first priority year": yrs.min(),
        "last priority year": yrs.max(),
        "windows active": w.dropna(subset=["window"]).groupby("company_canonical")["window"].nunique(),
    })
    f["years first to last"] = f["last priority year"] - f["first priority year"]
    f["classes per aircraft"] = (f["distinct classes"] / f["unique aircraft"]).round(3)
    f["region"] = firm_region(v).reindex(f.index)
    f["on the AAM index"] = f.index.isin(ari_listed(v))
    return f.sort_values("unique aircraft", ascending=False)


def market_vs_patents(v: pd.DataFrame) -> pd.DataFrame:
    """Does market standing track patenting? The named firms the AAM Reality Index rates against
    the named firms it does not, measure by measure, plus the two correlations taken inside the
    index itself. Mann-Whitney U between the two groups (two-sided, the only test used), Spearman
    rho within the index. Descriptive: every n is printed beside the number.

    The first block answers "do the firms the market rates hold more, file earlier, file broader";
    the second answers "does WHERE a firm sits on the index track any of that".
    """
    from scipy.stats import mannwhitneyu, spearmanr
    f = firm_frame(v)
    listed, rest = f[f["on the AAM index"]], f[~f["on the AAM index"]]
    n_l, n_r = len(listed), len(rest)
    rows: List[Dict] = []

    def med(s):
        return f"{s.median():.4g}"

    def block(col, label, sub=None, fmt=med):
        a, b = (sub if sub is not None else f).pipe(
            lambda d: (d.loc[d["on the AAM index"], col].dropna(), d.loc[~d["on the AAM index"], col].dropna()))
        u, p = mannwhitneyu(a, b, alternative="two-sided")
        rows.append({"reading": label,
                     "AAM index firms": f"{fmt(a)}  (n {len(a)})",
                     "other named firms": f"{fmt(b)}  (n {len(b)})",
                     "test": f"Mann-Whitney p = {p:.3f}",
                     "p": round(float(p), 3)})

    tot = len(v)
    rows.append({"reading": "aircraft held, and their share of the analysis set",
                 "AAM index firms": f"{int(listed['unique aircraft'].sum())}  ({listed['unique aircraft'].sum() / tot:.0%})",
                 "other named firms": f"{int(rest['unique aircraft'].sum())}  ({rest['unique aircraft'].sum() / tot:.0%})",
                 "test": f"{n_l} firms against {n_r}", "p": np.nan})
    block("unique aircraft", "unique aircraft per firm, median")
    block("patents", "representative patents per firm, median")
    block("first priority year", "first priority year, median")
    block("distinct classes", "distinct classes per firm, median")
    block("classes per aircraft", "distinct classes per aircraft, median (firms with 2+ aircraft only)",
          sub=f[f["unique aircraft"] >= 2], fmt=lambda s: f"{s.median():.2f}")
    block("years first to last", "years from first to last filing, median")

    # inside the index: does the position on it track anything?
    a = ari_firms(v).set_index("company")
    a["funding"] = pd.to_numeric(a["funding $M"].astype(str).str.replace(",", ""), errors="coerce")
    join = f.join(a[["ARI score", "funding"]], how="inner")
    for x, y, label in (("ARI score", "unique aircraft", "index score against unique aircraft"),
                        ("ARI score", "distinct classes", "index score against distinct classes"),
                        ("funding", "unique aircraft", "disclosed funding against unique aircraft"),
                        ("funding", "first priority year", "disclosed funding against first priority year")):
        d = join[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(d) >= 4:
            rho, p = spearmanr(d[x], d[y])
            rows.append({"reading": f"within the index — {label}",
                         "AAM index firms": f"rho {rho:+.2f}  (n {len(d)})", "other named firms": "not listed",
                         "test": f"Spearman p = {p:.3f}", "p": round(float(p), 3)})
    return pd.DataFrame(rows)


def coverage_segments(v: pd.DataFrame) -> pd.DataFrame:
    """The firm-size ranking cut into the segments the coverage curve marks: between two
    thresholds, how many firms sit there and how many aircraft they hold. The segments are
    disjoint, so they add up — unlike the nested rows of :func:`firm_tiers`."""
    sizes = firm_sizes(v)
    total = len(v)
    cuts = [10, 5, 4, 3, 2, 1]
    rows = []
    for hi, lo in zip([None] + cuts[:-1], cuts):
        sel = sizes[(sizes >= lo) & ((sizes < hi) if hi else True)]
        if not len(sel):
            continue
        band = f"{lo} or more" if hi is None else (f"{lo}" if lo == hi - 1 else f"{lo}-{hi - 1}")
        rows.append({"aircraft per firm": band, "firms": int(len(sel)), "aircraft": int(sel.sum()),
                     "share of the analysis set": round(float(sel.sum() / total), 3),
                     "cumulative firms": int((sizes >= lo).sum()),
                     "cumulative aircraft": int(sizes[sizes >= lo].sum())})
    return pd.DataFrame(rows)


def filer_mix(v: pd.DataFrame) -> pd.DataFrame:
    """Who filed, counted in both units at once: primary patents and the share of them, unique
    aircraft and the share of them, and the aircraft a filer type gets out of one patent. The
    patent columns reproduce the Preliminary Analysis table; the aircraft columns are what makes
    the two denominators of this chapter comparable (author's request, 2026-09-23)."""
    pat = v.drop_duplicates("patent_id")
    order = ["Named company", "University / institute", "Individual inventor", "Unattributed / independent"]
    names = {"Named company": "Named companies", "University / institute": "Universities and institutes",
             "Individual inventor": "Individual inventors", "Unattributed / independent": "Unattributed or independent"}
    rows = []
    for k in order:
        p, a = int(pat["filer"].eq(k).sum()), int(v["filer"].eq(k).sum())
        if not (p or a):
            continue
        rows.append({"filer": names[k],
                     "distinct filers": (int(v.loc[v["filer"].eq(k), "company_canonical"].nunique())
                                         if k in ("Named company", "University / institute") else "not identified"),
                     "primary patents": p, "share per primary patent": round(p / len(pat), 2),
                     "unique aircraft": a, "share of the analysis set": round(a / len(v), 2),
                     "aircraft per patent": round(a / p, 2) if p else np.nan})
    out = pd.DataFrame(rows)
    out.loc[len(out)] = {"filer": "all filers", "distinct filers": "",
                         "primary patents": int(len(pat)), "share per primary patent": 1.0,
                         "unique aircraft": int(len(v)), "share of the analysis set": 1.0,
                         "aircraft per patent": round(len(v) / len(pat), 2)}
    return out


def firm_leverage(v: pd.DataFrame, min_aircraft: int = 3) -> pd.DataFrame:
    """How much any one firm can move the class reading of this document.

    For each named firm: drop it from the analysis set and re-take the class shares; the answer is
    the largest share that moves and by how many percentage points. It is the direct test of "is
    this class share a real spread of firms or one firm's portfolio" — the author's question at
    4.1.9 and 4.2.3. Done on the whole set and again inside the two windows that carry most of the
    corpus, because a firm can be negligible overall and dominant in one window.
    """
    base_all = v["topType"].value_counts(normalize=True)
    sizes = firm_sizes(v)
    keep = sizes[sizes >= min_aircraft].index
    rows = []
    for f in keep:
        d = (v[~v["company_canonical"].eq(f)]["topType"].value_counts(normalize=True)
             .reindex(base_all.index).fillna(0) - base_all)
        moved = d.abs().idxmax()
        worst_w, worst_pp, worst_c = "", 0.0, ""
        for wn in WINDOW_NAMES[:-1]:
            sub = v[v["window"].eq(wn)]
            if len(sub) < 30 or not sub["company_canonical"].eq(f).any():
                continue
            b = sub["topType"].value_counts(normalize=True)
            dw = (sub[~sub["company_canonical"].eq(f)]["topType"].value_counts(normalize=True)
                  .reindex(b.index).fillna(0) - b)
            if float(dw.abs().max()) > worst_pp:
                worst_w, worst_pp, worst_c = wn, float(dw.abs().max()), dw.abs().idxmax()
        rows.append({"firm": f, "unique aircraft": int(sizes[f]),
                     "share of the analysis set": round(float(sizes[f] / len(v)), 3),
                     "class most moved": moved,
                     "shift if the firm is dropped (pp)": round(float(d[moved]) * 100, 2),
                     "largest shift inside one window (pp)": round(worst_pp * 100, 1),
                     "that window": worst_w, "that class": worst_c,
                     "modal class": (v[v["company_canonical"].eq(f)]["topType"].mode().iloc[0]
                                     if v[v["company_canonical"].eq(f)]["topType"].notna().any() else "")})
    out = pd.DataFrame(rows)
    return out.reindex(out["shift if the firm is dropped (pp)"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def class_concentration(v: pd.DataFrame) -> pd.DataFrame:
    """Per class: how many named firms file in it, and how much of it the largest one and the
    largest three hold. The companion of :func:`firm_leverage` — a class whose top firm holds a
    small share cannot be one firm's portfolio."""
    tot = v["topType"].value_counts()
    rows = []
    for c, n in tot.items():
        named = v[v["topType"].eq(c) & v["named"]]["company_canonical"].value_counts()
        rows.append({"class": c, "aircraft": int(n), "named firms filing in it": int(len(named)),
                     "largest firm": (named.index[0] if len(named) else ""),
                     "its share of the class": round(float(named.iloc[0] / n), 2) if len(named) else 0.0,
                     "top 3 firms' share": round(float(named.head(3).sum() / n), 2) if len(named) else 0.0,
                     "share held by named firms": round(float(named.sum() / n), 2)})
    return pd.DataFrame(rows)


def cohort_mix(v: pd.DataFrame) -> pd.DataFrame:
    """The normalised form of the entry cohorts (author's ruling 2026-09-23: 4.2.2 must be
    normalised by the number of firms). Per window and class: the share of that window's ENTRANTS
    who enter with the class, beside the share of that window's AIRCRAFT in the same class.

    The two shares are what makes the section say something 4.1.2 does not: 4.1.2 counts aircraft,
    this counts firms, and the gap between them is whether the class shift is carried by new firms
    or by the firms already inside.
    """
    co = cohorts(v).set_index("window").reindex(WINDOW_NAMES).fillna(0)
    rows = []
    for wn in WINDOW_NAMES:
        n_ent = int(co.loc[wn, "firms entering"])
        air = v[v["window"].eq(wn)]["topType"].value_counts()
        n_air = int(air.sum())
        for c in [c for c in co.columns if c != "firms entering"]:
            e = int(co.loc[wn, c])
            if not e and not air.get(c, 0):
                continue
            rows.append({"window": wn, "class": c, "firms entering": n_ent, "entering with this class": e,
                         "share of entrants": round(e / n_ent, 3) if n_ent else np.nan,
                         "aircraft in the window": n_air, "aircraft of this class": int(air.get(c, 0)),
                         "share of aircraft": round(float(air.get(c, 0)) / n_air, 3) if n_air else np.nan})
    return pd.DataFrame(rows)


def filers_by_window(v: pd.DataFrame) -> pd.DataFrame:
    """Named firms active per window: new (first window), continuing, last seen (no later
    filing; not judged in the partial window); plus the individual-inventor share."""
    w = v.dropna(subset=["window"])
    named = w[w["named"]]
    first = named.groupby("company_canonical")["window"].agg(lambda s: min(s, key=WINDOW_NAMES.index))
    last = named.groupby("company_canonical")["window"].agg(lambda s: max(s, key=WINDOW_NAMES.index))
    rows = []
    for i, name in enumerate(WINDOW_NAMES):
        sub = named[named["window"].eq(name)]
        firms = sub["company_canonical"].unique()
        new = sum(first[f] == name for f in firms)
        gone = sum(last[f] == name for f in firms) if i < len(WINDOW_NAMES) - 2 else np.nan
        allw = w[w["window"].eq(name)]
        rows.append({"window": name, "unique aircraft": int(len(allw)),
                     "named firms active": int(len(firms)), "new firms": int(new),
                     "continuing firms": int(len(firms) - new),
                     "firms last seen": (int(gone) if not np.isnan(gone) else ""),
                     "aircraft by named firms": int(len(sub)),
                     "share individual inventors": round(float(allw["filer"].eq("Individual inventor").mean()), 2),
                     "share unattributed": round(float(allw["filer"].eq("Unattributed / independent").mean()), 2)})
    return pd.DataFrame(rows)


def firm_windows(v: pd.DataFrame, min_aircraft: int = FIRM_MIN) -> pd.DataFrame:
    """Firm × window: aircraft count and modal class, firms with ``min_aircraft`` or more."""
    sizes = firm_sizes(v)
    firms = sizes[sizes >= min_aircraft].index
    w = v[v["company_canonical"].isin(firms)].dropna(subset=["window"])
    rows = []
    for f in firms:
        sub = w[w["company_canonical"].eq(f)]
        first = min(sub["window"], key=WINDOW_NAMES.index)
        for name in WINDOW_NAMES:
            s = sub[sub["window"].eq(name)]
            modal = s["topType"].value_counts().index[0] if len(s) and s["topType"].notna().any() else None
            rows.append({"firm": f, "aircraft total": int(sizes[f]), "first window": first,
                         "window": name, "aircraft": int(len(s)), "modal class": modal,
                         "classes": int(s["topType"].nunique())})
    return pd.DataFrame(rows)


def firm_region(v: pd.DataFrame) -> pd.Series:
    """Modal region of each named firm's patents."""
    w = v[v["named"]]
    return w.groupby("company_canonical")["region3"].agg(lambda s: s.value_counts().index[0])


def proximity_by_region(ds: Dataset, v: pd.DataFrame, min_aircraft: int = FIRM_MIN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Jaffe proximity of the firm profiles (class) with the firms' regions; mean proximity
    within and between regions. Returns (matrix in clustered order, summary)."""
    prof = a2.firm_profiles(ds, min_aircraft, "class")
    prox = a2.proximity_matrix(prof)
    order = a2.proximity_order(prox)
    m = prox.loc[order, order]
    reg = firm_region(v).reindex(order)
    pairs = []
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            pairs.append({"a": a, "b": b, "proximity": float(prox.loc[a, b]),
                          "same region": reg[a] == reg[b]})
    p = pd.DataFrame(pairs)
    summary = p.groupby("same region")["proximity"].agg(pairs="size", mean="mean", median="median").round(2)
    summary.index = ["different regions", "same region"]
    summary.index.name = "firm pair"
    m.attrs["region"] = reg
    return m, summary.reset_index()


# ------------------------------------------------------- ARI ---------------
def _load_ari() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cur = pd.read_csv(ARI_DIR / "ari_may2026.csv", keep_default_na=False)
    hist = pd.read_csv(ARI_DIR / "ari_history.csv")
    cmap = pd.read_csv(ARI_DIR / "ari_company_map.csv", keep_default_na=False)
    return cur, hist, cmap


def _oem_key(s: str) -> str:
    s = re.sub(r"\(.*?\)", "", str(s)).strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def ari_listed(v: pd.DataFrame) -> set:
    """The canonical companies of the corpus that the AAM Reality Index rates — in the May 2026
    release or in any earlier one. Membership, not score: it is the "the market rates this firm"
    flag that 4.2.1 compares the other named firms against."""
    _, _, cmap = _load_ari()
    return set(cmap.loc[cmap["company_canonical"].ne(""), "company_canonical"]) & set(firm_sizes(v).index)


def ari_firms(v: pd.DataFrame) -> pd.DataFrame:
    """Every AAM Reality Index OEM that files in the corpus: score (May 2026 or the last release
    that listed it), disclosed funding, unique aircraft, classes and re-filings."""
    cur, hist, cmap = _load_ari()
    cmap = cmap[cmap["company_canonical"].ne("")]
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows()}
    cur["key"] = cur["oem"].map(_oem_key)
    cur["company_canonical"] = cur["key"].map(key_to_canon)
    hist["key"] = hist["oem"].map(_oem_key)
    hist["company_canonical"] = hist["key"].map(key_to_canon)
    dates = [c for c in hist.columns if c not in ("oem", "key", "company_canonical")]
    sizes = firm_sizes(v)
    rows = []
    for canon in sorted(set(cmap["company_canonical"])):
        c = cur[cur["company_canonical"].eq(canon)]
        h = hist[hist["company_canonical"].eq(canon)]
        score = last = funding = vtype = None
        if len(c):
            score = float(c["ari"].iloc[0]); last = "May 2026"
            funding = c["funding_musd"].iloc[0]; vtype = c["vehicle_type"].iloc[0]
        elif len(h):
            s = h[dates].apply(pd.to_numeric, errors="coerce").iloc[0]
            valid = s.dropna()
            if len(valid):
                score, last = float(valid.iloc[-1]), valid.index[-1]
        sub = v[v["company_canonical"].eq(canon)]
        mix = sub["topType"].value_counts()
        rows.append({"company": canon, "ARI score": score, "release": last,
                     "funding $M": funding if funding not in (None, "") else "",
                     "ARI vehicle type": vtype or "",
                     "unique aircraft": int(sizes.get(canon, 0)),
                     "classes": int(mix.size),
                     "class mix": " · ".join(f"{metrics.ARCH_NAMES.get(k, k)} {n}" for k, n in mix.items()),
                     "median propulsive units": (float(sub["units"].median()) if "units" in sub and sub["units"].notna().any() else np.nan),
                     "first priority year": (int(sub["year"].min()) if sub["year"].notna().any() else ""),
                     "in the corpus": int(sizes.get(canon, 0)) > 0})
    out = pd.DataFrame(rows)
    return out[out["in the corpus"]].sort_values("ARI score", ascending=False).reset_index(drop=True)


def ari_history_corpus(v: pd.DataFrame) -> pd.DataFrame:
    """Score per release for the ARI OEMs that file in the corpus (long form)."""
    cur, hist, cmap = _load_ari()
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows() if r["company_canonical"]}
    hist["company"] = hist["oem"].map(_oem_key).map(key_to_canon)
    sizes = firm_sizes(v)
    hist = hist[hist["company"].isin(sizes.index)]
    dates = [c for c in hist.columns if c not in ("oem", "key", "company")]
    long = hist.melt(id_vars=["company", "oem"], value_vars=dates, var_name="release", value_name="score")
    long["score"] = pd.to_numeric(long["score"], errors="coerce")
    long["date"] = pd.to_datetime(long["release"], format="%B %Y")
    return long.dropna(subset=["score"]).sort_values(["company", "date"]).reset_index(drop=True)


def ari_correlation(firms: pd.DataFrame, v: pd.DataFrame) -> pd.DataFrame:
    """Spearman correlations between the ARI score / funding and the patent-side measures,
    over the ARI firms in the corpus. Descriptive: n is small and printed."""
    from scipy.stats import spearmanr
    f = firms.copy()
    f["funding"] = pd.to_numeric(f["funding $M"].astype(str).str.replace(",", ""), errors="coerce")
    # re-filings per firm
    sp = None
    rows = []
    for x in ("ARI score", "funding"):
        for y in ("unique aircraft", "classes", "median propulsive units", "first priority year"):
            d = f[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(d) >= 4:
                rho, p = spearmanr(d[x], d[y])
                rows.append({"x": x, "y": y, "n firms": int(len(d)), "Spearman rho": round(float(rho), 2),
                             "p": round(float(p), 2)})
    return pd.DataFrame(rows)


# ------------------------------------------------------- mission (evtol.news)
def _parse_capacity(text: str) -> str:
    t = str(text).lower()
    if not t.strip():
        return "not stated"
    m = re.search(r"(\d+)\s*(?:passengers?|people|persons?|pax|seats?|occupants?)", t)
    if m:
        k = int(m.group(1))
        return "1" if k == 1 else "2" if k == 2 else "3-4" if k <= 4 else "5+"
    if "cargo" in t or "payload" in t or "package" in t:
        return "cargo only"
    m = re.search(r"\b(\d+)\b", t)
    if m:
        k = int(m.group(1))
        return "1" if k == 1 else "2" if k == 2 else "3-4" if k <= 4 else "5+"
    if "pilot" in t or "passenger" in t or "person" in t:
        return "1"
    return "not stated"


def _parse_piloting(text: str) -> str:
    t = str(text).lower()
    if not t.strip():
        return "not stated"
    auto = any(k in t for k in ("autonom", "remote", "unmanned", "optionally"))
    pil = "pilot" in t or "manual" in t or "manned" in t
    return "either" if auto and pil else "autonomous / remote" if auto else "piloted" if pil else "not stated"


def _parse_power(text: str) -> str:
    t = str(text).lower()
    if not t.strip():
        return "not stated"
    if "hydrogen" in t or "fuel cell" in t:
        return "hydrogen"
    if "hybrid" in t:
        return "hybrid"
    if "batter" in t or "electric" in t:
        return "battery electric"
    return "other"


def _parse_status(text: str) -> str:
    t = str(text).lower()
    if "production" in t:
        return "production"
    if "prototype" in t or "demonstrator" in t or "testbed" in t or "proof" in t:
        return "prototype / demonstrator"
    if "mock" in t or "subscale" in t or "sub-scale" in t:
        return "mock-up / subscale"
    if "concept" in t or "design" in t:
        return "concept design"
    if "defunct" in t or "dormant" in t:
        return "defunct"
    return "other / blank"


MISSION_ORDER = {
    "capacity": ["1", "2", "3-4", "5+", "cargo only", "not stated"],
    "piloting": ["piloted", "autonomous / remote", "either", "not stated"],
    "power source": ["battery electric", "hybrid", "hydrogen", "other", "not stated"],
    "status": ["concept design", "mock-up / subscale", "prototype / demonstrator", "production", "defunct", "other / blank"],
}


def linked_aircraft(v: pd.DataFrame) -> pd.DataFrame:
    """The patent aircraft linked to an evtol.news page (patent_links.csv, use = yes), with the
    page's class, status and parsed mission fields, and the G1 class folded to five."""
    links = pd.read_csv(EVTOLNEWS / "3_embedding_evaluation" / "patent_links.csv", keep_default_na=False)
    links = links[links["use"].eq("yes")]
    pages = pd.read_csv(EVTOLNEWS / "0_source" / "aircraft.csv", keep_default_na=False).set_index("slug_key")
    rows = []
    for _, r in links.iterrows():
        slug = str(r["slug_keys"]).split("|")[0]
        if slug not in pages.index:
            continue
        p = pages.loc[slug]
        rows.append({"aircraft_id": r["aircraft_uid"], "patent_id": r["patent_id"], "name": r["aircraft_name"],
                     "company": r["company"], "slug": slug, "evtol class": p["evtol_class_main"] or p["evtol_class"],
                     "status": _parse_status(p["list_status"]), "capacity": _parse_capacity(p["spec_capacity"]),
                     "piloting": _parse_piloting(p["spec_piloting"]), "power source": _parse_power(p["spec_power_source"]),
                     "list_status raw": p["list_status"]})
    l = pd.DataFrame(rows)
    l = l.merge(v[["aircraft_id", "topType", "class5", "units", "year"]], on="aircraft_id", how="inner")
    return l


#: the three sources the architecture of one aircraft can come from, in the order they are compared
NAME_ARCH_SOURCES = ("G1", "whole patent", "public")


def name_arch_check(v: pd.DataFrame) -> pd.DataFrame:
    """One row per aircraft whose architecture the sources do not agree on; the agreeing ones
    collapse into the first row (user ruling 2026-09-22).

    The three sources are the G1 class of the figures (``topType``, the label this document uses
    everywhere), the whole-patent reading (``arch_gt``, ``architecture_ground_truth.csv``) and the
    class the evtol.news directory gives the same aircraft, for the ~95 aircraft a page is linked
    to. The directory works in five classes, so G1 and the whole-patent reading are folded with
    :data:`FOLD5` before either is compared with it; between themselves they are compared at the
    twelve G1 classes. An aircraft with no real name is identified by its patent id.
    """
    codes = set(metrics.ARCH_NAMES) | set(FOLD5)
    pub = linked_aircraft(v).set_index("aircraft_id")["evtol class"]
    w = v.copy()
    w["pub"] = w["aircraft_id"].map(pub)
    g1, gt = w["topType"].where(w["topType"].isin(codes)), w["arch_gt"].where(w["arch_gt"].isin(codes))
    w["_g1"], w["_gt"] = g1, gt
    d_g1_gt = g1.notna() & gt.notna() & g1.ne(gt)
    d_g1_pub = w["pub"].notna() & g1.notna() & g1.map(FOLD5).ne(w["pub"])
    d_gt_pub = w["pub"].notna() & gt.notna() & gt.map(FOLD5).ne(w["pub"])
    hit = d_g1_gt | d_g1_pub | d_gt_pub
    size = firm_sizes(v)

    def _cell(code, folded: bool) -> str:
        if not isinstance(code, str) or code not in metrics.ARCH_NAMES:
            # a value outside the twelve codes is printed as it stands, never silently blanked
            return f"{code} (not a class)" if isinstance(code, str) and code else "—"
        name = f"{metrics.ARCH_NAMES.get(code, code)} ({code}"
        return name + (f" → {FOLD5.get(code, '?')})" if folded else ")")

    rows = []
    for _, r in w[hit].iterrows():
        pairs = [n for n, f in zip(("G1 vs whole patent", "G1 vs public", "whole patent vs public"),
                                   (d_g1_gt[r.name], d_g1_pub[r.name], d_gt_pub[r.name])) if f]
        if len(pairs) == 2 and "G1 vs public" in pairs and "whole patent vs public" in pairs:
            pairs = ["G1 and whole patent vs public"]
        has_pub = pd.notna(r["pub"])
        named = bool(r.get("name_is_real"))
        rows.append({
            "aircraft": str(r["aircraft_name"]) if named else str(r["patent_id"]),
            "company": str(r["company_canonical"]) if pd.notna(r["company_canonical"]) else "—",
            "G1 class": _cell(r["_g1"], has_pub),
            "whole-patent class": _cell(r["_gt"], has_pub),
            # HB's directory name runs to 37 characters and would set the column width on its own
            "public class": (f"{'Hover Bike / PFV' if r['pub'] == 'HB' else FOLD5_NAMES.get(r['pub'], r['pub'])}"
                             f" ({r['pub']})") if has_pub else "—",
            "sources that disagree": "; ".join(pairs),
            # two sources against one first, then anything a public class can be held against
            "_rank": 3 if len(pairs) > 1 else (2 if has_pub else 1),
            "_firm": int(size.get(r["company_canonical"], 0)),
            "_named": int(named),
        })
    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values(["_rank", "_firm", "_named", "aircraft"],
                              ascending=[False, False, False, True]).reset_index(drop=True)
        out = out.drop(columns=["_rank", "_firm", "_named"])
    agree = int((~hit).sum())
    # What no comparison can reach: a source missing, or a value outside the twelve classes. The
    # author's ruling of 2026-09-23 keeps these aircraft out of every comparison but off no page:
    # they are named here, with the reason, instead of only being counted. Nothing was relabelled
    # and architecture_ground_truth.csv is untouched, so "Convertiplane" prints as it stands.
    blind_m = g1.isna() | gt.isna()
    blind = int(blind_m.sum())
    blind_rows = []
    for _, r in w[blind_m].iterrows():
        raw_gt = r["arch_gt"] if isinstance(r["arch_gt"], str) else ""
        why = []
        if pd.isna(r["_g1"]):
            why.append("no G1 label")
        if not raw_gt:
            why.append("the patent states no class")
        elif pd.isna(r["_gt"]):
            why.append("GT outside the twelve")
        blind_rows.append({
            "aircraft": str(r["patent_id"]),
            "company": str(r["company_canonical"]) if pd.notna(r["company_canonical"]) else "—",
            "G1 class": _cell(r["_g1"], False) if pd.notna(r["_g1"]) else "none recorded",
            "whole-patent class": _cell(raw_gt, False) if raw_gt else "blank in the GT file",
            "public class": "—",
            "sources that disagree": "not compared: " + "; ".join(why),
        })
    head = pd.DataFrame([{
        "aircraft": f"{agree} of {len(w)} agree — not listed",
        "company": "every filer", "G1 class": "—", "whole-patent class": "—",
        "public class": f"{int(w['pub'].notna().sum())} carry one",
        "sources that disagree": f"none; {blind} not compared, named below",
    }] + blind_rows)
    out = pd.concat([head, out], ignore_index=True)
    out.attrs.update({"agree": agree, "disagree": int(hit.sum()), "linked": int(w["pub"].notna().sum()),
                      "g1_vs_gt": int(d_g1_gt.sum()), "g1_vs_pub": int(d_g1_pub.sum()),
                      "gt_vs_pub": int(d_gt_pub.sum()), "unclassified": blind, "aircraft": int(len(w))})
    return out


def class_fold_table(v: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for code, five in FOLD5.items():
        rows.append({"G1 class": f"{metrics.ARCH_NAMES.get(code, code)} ({code})", "evtol.news class": f"{FOLD5_NAMES[five]} ({five})",
                     "unique aircraft": int(v["topType"].eq(code).sum())})
    return pd.DataFrame(rows).sort_values(["evtol.news class", "unique aircraft"], ascending=[True, False]).reset_index(drop=True)


def mission_tables(linked: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Crosstabs of each mission field against the folded class, counts, on the linked aircraft."""
    out = {}
    order5 = ["VT", "LC", "WM", "ER", "HB"]
    for field, order in MISSION_ORDER.items():
        t = pd.crosstab(linked[field], linked["class5"]).reindex(index=[o for o in order if o in linked[field].values],
                                                                  columns=[c for c in order5 if c in linked["class5"].values], fill_value=0)
        t["all"] = t.sum(axis=1)
        out[field] = t.reset_index()
    agree = pd.crosstab(linked["class5"], linked["evtol class"]).reindex(index=[c for c in order5 if c in linked["class5"].values])
    agree.index = [f"G1 folded: {FOLD5_NAMES[c]}" for c in agree.index]
    out["agreement"] = agree.reset_index().rename(columns={"index": "patent label"})
    return out



# ------------------------------------------------------- 4.1 new: dominant design, configs, drift
def _archetype_key(v: pd.DataFrame, level: str) -> pd.Series:
    cols = a2.ARCHETYPE_LEVELS[level][0]
    frame = v.copy()
    if "anyTilt" in cols and "anyTilt" not in frame:
        frame["anyTilt"] = None
    ok = frame[cols].notna().all(axis=1)
    key = frame[cols].astype(str).agg(" · ".join, axis=1)
    return key.where(ok)


def dominant_design(v: pd.DataFrame, n: int = 40, perms: int = 200, seed: int = 42) -> pd.DataFrame:
    """The pre-registered test (PA 5.7) per window: top archetype share at A0c and A1t against the
    50 % line, and rarefied ²D against the band of ²D obtained when archetype labels are shuffled
    across windows (window structure kept, corpus concentration destroyed)."""
    w = v.dropna(subset=["window"]).copy()
    rng = np.random.default_rng(seed)
    rows = []
    for level in ("A0c", "A1t"):
        key = _archetype_key(w, level)
        ww = w[key.notna()].copy()
        ww["key"] = key[key.notna()]
        obs = {}
        for name in WINDOW_NAMES:
            sub = ww[ww["window"].eq(name)]
            if len(sub) < 10:
                continue
            h = hill_numbers(sub["key"], n=n, draws=300)
            top = sub["key"].value_counts(normalize=True)
            obs[name] = {"level": level, "window": name, "aircraft": int(len(sub)), "top archetype": top.index[0],
                         "top share": round(float(top.iloc[0]), 3), "D2": h["D2"], "D2 low": h["D2 low"], "D2 high": h["D2 high"]}
        # permutation band: shuffle keys across all windows
        band = {name: [] for name in obs}
        keys = ww["key"].to_numpy()
        for _ in range(perms):
            shuffled = rng.permutation(keys)
            for name in obs:
                mask = ww["window"].eq(name).to_numpy()
                band[name].append(hill_numbers(pd.Series(shuffled[mask]), n=n, draws=40, seed=int(rng.integers(1e9)))["D2"])
        for name, r in obs.items():
            b = np.array(band[name])
            r["D2 permutation low"] = round(float(np.percentile(b, 2.5)), 2)
            r["D2 permutation high"] = round(float(np.percentile(b, 97.5)), 2)
            r["below band"] = bool(r["D2"] < r["D2 permutation low"])
            r["condition 1 (> 50 %)"] = bool(r["top share"] > 0.5)
            rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------- 4.1.3.1 what the test evaluates: the archetypes
#: The dimensions of each archetype level, written out. Same order as the values of
#: ``a2.ARCHETYPE_LEVELS[level][0]``, so a reader can decode an archetype string such as
#: ``TR · 1 · True`` position by position. Words, never column names.
#: the propulsive-unit bins as this document prints them: the cuts of :data:`a2.ROTOR_BINS`
#: with the bottom band relabelled by :data:`UNIT_BANDS` (see :func:`base`), so the wording
#: follows the bins and matches every rendered archetype key
_BINS = " / ".join(str(b) for b in UNIT_BANDS[1])
ARCHETYPE_DIMENSIONS: Dict[str, str] = {
    "A0": "architecture class",
    "A0c": f"architecture class · propulsive units, binned {_BINS}",
    "A1": "architecture class · number of wings · booms present",
    "A1c": "architecture class · number of wings · booms present · propulsive units",
    "A1b": "architecture class · number of wings · number of booms, binned none / 1-2 / 3 / 4 or more",
    "A1t": "architecture class · number of wings · at least one tilting propulsor",
    "A1tc": "architecture class · number of wings · at least one tilting propulsor · propulsive units",
    "A2": "architecture class · number of wings · booms present · tail type",
    "A2c": "architecture class · number of wings · booms present · tail type · propulsive units",
}
#: Where each level is read. A level with no reading in this document says so.
ARCHETYPE_ROLE: Dict[str, str] = {
    "A0": "the reference level: every per-class reading (4.1.2, 4.1.4 to 4.1.7, 4.1.8 (i), 4.1.10, 4.3.4, 5.1)",
    "A0c": "co-reported second level of 4.1.3.3, conditions 1 to 3, and the only level at which condition 2 fires; 4.1.8 (ii) diversity; 4.1.9 zones; 4.3.3 regional specialisation",
    "A1": "not read here; the alternative to A1t recorded in Preliminary Analysis 5.10",
    "A1c": "not read here",
    "A1b": "not read here; the alternative to A1t recorded in Preliminary Analysis 5.10",
    "A1t": "the design species: 4.1.3.3 conditions 1 to 3, and the level Preliminary Analysis 5.1 and 5.7 are written at",
    "A1tc": "not read here",
    "A2": "not read here; 4.1.4 reads the same fields inside one class, as a configuration",
    "A2c": "not read here; 4.1.4 reads the same fields inside one class, as a configuration",
}
#: The screens a level must pass to be usable as a design species, as
#: ``(name, printed column, line, direction)``. Resolution: the level must separate designs the
#: class alone merges, so it needs at least twice as many archetypes as there are classes — the
#: line is computed from the corpus, not typed. Fragmentation and population: a level whose
#: aircraft are mostly alone cannot carry a share, and the five-aircraft line is the one 4.1.9
#: already uses. Readable shares: a test written on shares needs several archetypes large enough
#: to hold one.
ARCHETYPE_SCREENS: List[Tuple[str, str, str, Optional[float], str]] = [
    ("resolution", "archetypes", "needs at least {line}, twice the number of classes", None, "min"),
    ("fragmentation", "of the aircraft alone in their archetype", "needs at most {line}", 0.05, "max"),
    ("population", "of the aircraft in an archetype of five or more", "needs at least {line}", 0.90, "min"),
    ("readable shares", "archetypes hold 5 % or more of the aircraft", "needs at least {line}", 3, "min"),
]
#: The author's ruling of 2026-09-23 on the levels that clear the screens: A1t is the design
#: species, A0c is reported beside it at every step of 4.1.3 and is not a robustness run.
ARCHETYPE_RULED: Dict[str, str] = {
    "A1t": "the design species (ruled 2026-09-23)",
    "A0c": "co-reported beside A1t at every step (ruled 2026-09-23)",
}
#: A level that clears every screen but is still not read: the codebook reason it is set aside.
ARCHETYPE_SET_ASIDE: Dict[str, str] = {
    "A0": "the architecture class itself, not a species",
    "A1": "booms are structure and allocate no function (Preliminary Analysis 5.10)",
    "A1b": "booms are structure and allocate no function (Preliminary Analysis 5.10)",
}


def _level_key(frame: pd.DataFrame, level: str, ds: Dataset) -> pd.Series:
    """The archetype string of every aircraft at ``level``, blank where the level is not
    determinable. Same rule as :func:`a2.d5_archetype_cardinality` (rule 1, 2026-09-19): a field
    hidden by a stage override, or a derived field that is not determinable, leaves the aircraft
    out of that level; any other blank stays a design absence and is a value of its own."""
    fields = a2.ARCHETYPE_LEVELS[level][0]
    left = pd.Series(False, index=frame.index)
    for f in fields:
        left |= (frame[f].isna() if f in ("anyTilt", "boomBin", "rotorBin")
                 else a2.hidden_by_override(frame, f, ds.data_dictionary))
    shown = frame[fields].astype(str).replace({"nan": "blank", "None": "blank", "<NA>": "blank"})
    return shown.agg(" · ".join, axis=1).where(~left)


def archetype_levels(ds: Dataset, v: pd.DataFrame) -> pd.DataFrame:
    """Every archetype level the codebook can form, with how many archetypes it yields, how
    many aircraft end up alone, how even it is and where this document reads it.

    An archetype is the combination of the level's dimensions: each aircraft is written as its
    answers on those dimensions joined by ``·``, and two aircraft share an archetype when that
    string is the same. Each aircraft belongs to exactly one archetype per level. The effective
    number is Hill ¹D, the exponential of the Shannon entropy of the archetype shares — the
    number of equally common archetypes that would give the same entropy; ²D repeats it for the
    inverse Simpson index, which weights the large archetypes more and is the quantity condition 2
    of the test reads. The counting columns reproduce table 3.3.6 of the Preliminary Analysis.
    """
    w = v[v["topType"].notna()].copy()
    if "boomBin" not in w.columns:
        w = w.merge(a2.archetype_frame(ds)[["aircraft_id", "boomBin"]], on="aircraft_id", how="left")
    rows = []
    for level in a2.ARCHETYPE_LEVELS:
        key = _level_key(w, level, ds)
        sub = w[key.notna()].copy()
        sub["key"] = key[key.notna()]
        n = len(sub)
        counts = sub["key"].value_counts()
        shares = counts / n
        big = counts[counts >= 5]
        tops = [sub[sub["window"].eq(wn)]["key"].value_counts().index[0]
                for wn in WINDOW_NAMES if sub["window"].eq(wn).sum() >= 10]
        rows.append({
            "level": level,
            "dimensions combined": ARCHETYPE_DIMENSIONS[level],
            "largest archetype": counts.index[0],
            "aircraft": int(n),
            "left out": int(key.isna().sum()),
            "archetypes": int(len(counts)),
            "singletons": int((counts == 1).sum()),
            "singleton share": round(float((counts == 1).sum() / n), 3),
            "effective number ¹D": round(metrics.effective_number(sub["key"]), 1),
            "effective number ²D": round(float(1 / (shares ** 2).sum()), 1),
            "largest share": round(float(shares.iloc[0]), 3),
            "top three share": round(float(shares.iloc[:3].sum()), 3),
            "archetypes of five or more": int(len(big)),
            "share in archetypes of five or more": round(float(big.sum() / n), 3),
            "archetypes holding 5 % or more": int((shares >= 0.05).sum()),
            "distinct largest archetypes over the windows": int(len(set(tops))),
            "used in this document": ARCHETYPE_ROLE[level],
        })
    return pd.DataFrame(rows)


def archetype_level_choice(levels: pd.DataFrame) -> pd.DataFrame:
    """Which levels this document can read as a design species, screen by screen.

    The four screens are fixed in :data:`ARCHETYPE_SCREENS` and applied to the numbers of the
    previous table; each cell prints the level's value and whether it clears the line. A level
    that clears all four is usable; what it is then used for is the author's ruling, recorded
    in the note under this table and in table 5.10 of the Preliminary Analysis.
    """
    src = {"resolution": "archetypes", "fragmentation": "singleton share",
           "population": "share in archetypes of five or more",
           "readable shares": "archetypes holding 5 % or more"}
    classes = int(levels.loc[levels["level"].eq("A0"), "archetypes"].iloc[0])
    lines = {"resolution": 2 * classes}
    rows = []
    for _, r in levels.iterrows():
        row = {"level": r["level"]}
        passed = []
        for name, unit, rule, line, direction in ARCHETYPE_SCREENS:
            val, line = r[src[name]], lines.get(name, line)
            ok = bool(val >= line) if direction == "min" else bool(val <= line)
            passed.append(ok)
            fmt = _pct if isinstance(val, float) else (lambda x: f"{x:g}")
            said = f"{fmt(val)} {unit}"
            if not isinstance(val, float) and val == 1:      # "1 archetype", never "1 archetypes"
                said = said.replace("archetypes hold", "archetype holds").replace("archetypes", "archetype")
            row[name] = f"{said} — {rule.format(line=fmt(line))} — {'pass' if ok else 'fail'}"
        failed = [n for (n, _, _, _, _), ok in zip(ARCHETYPE_SCREENS, passed) if not ok]
        row["screens passed"] = f"{sum(passed)} of {len(passed)}"
        aside = ARCHETYPE_SET_ASIDE.get(r["level"])
        if not all(passed):
            row["verdict"] = "set aside — fails " + ", ".join(failed)
        elif aside:
            row["verdict"] = "clears the screens, set aside — " + aside
        else:
            ruled = ARCHETYPE_RULED.get(r["level"])
            row["verdict"] = ("usable as a design species — " + ruled if ruled
                              else "usable as a design species")
        if r["level"] == "A0":
            row["verdict"] = "the reference level — " + ARCHETYPE_SET_ASIDE["A0"]
        row["used in this document"] = r["used in this document"]
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------- 4.1.3.2 / 4.1.3.3 the conditions and the result
#: The three conditions of the test, as fixed in Preliminary Analysis 5.7 before any curve was
#: drawn: what each one tests, the threshold, and where the threshold comes from. The wording is
#: fixed text; every number that answers them is computed in :func:`dominant_design_result`.
DD_CONDITIONS: List[Tuple[str, str, str, str]] = [
    ("1 — counts",
     "whether one archetype holds most of the sector, so that most filers are proposing the same design",
     "the largest archetype holds more than 50 % of the aircraft of a window, in two consecutive "
     "complete windows",
     "Preliminary Analysis 5.7, condition 1. More than half means most of the sector is proposing "
     "the same design; two windows means the share is not a single unusual period. The condition is "
     "written at A1t there; it is run at A0c as well, so the verdict does not rest on the level."),
    ("2 — balance",
     "whether a window holds fewer designs in play than chance would give it, so that the "
     "concentration is in the corpus and not in the window structure",
     "rarefied ²D falls below the permutation band: the 2.5th percentile of the ²D obtained when "
     "archetype labels are shuffled across windows (40 aircraft per draw, 200 permutations)",
     "Preliminary Analysis 5.7, condition 2. A fixed cutoff such as two designs in play was "
     "considered and set aside (5.10): it cannot be justified against 2.5, while the band is "
     "computed from this corpus and moves with it."),
    ("3 — form",
     "whether the aircraft have become similar to one another, and not only concentrated under one "
     "archetype name",
     "Q, the mean Gower distance between two aircraft of the window drawn at random, falls below the "
     "mean Q of the two earliest windows by more than the permutation band: the 2.5th percentile of "
     "the same difference when the window labels are shuffled across the aircraft, window sizes kept "
     "(200 permutations)",
     "Preliminary Analysis 5.7, condition 3, on the distance fixed in 5.3 and the disparity measure of "
     "5.5. Gower's coefficient (Gower, 1971) is d(i,j) = Σ w δ (1 − s) / Σ w δ over the informative "
     "shortlist of 3.3.4: s is 1 for a shared category and 1 − |xi − xj| / range for a count, and δ is "
     "1 only where both aircraft carry a value, so a blank leaves the pair's average instead of "
     "counting as a difference (3.3.2). One unit of weight per subsystem — architecture, wings, "
     "empennage, fuselage, booms, propulsion — divided among that subsystem's fields, so the number of "
     "columns the codebook spends on a card does not become importance; uniform weighting is reported "
     "beside it as 5.3 requires. Q is Rao's quadratic entropy, Σᵢ Σⱼ pᵢ pⱼ d(i,j) (Rao, 1982). The "
     "distance is imported from the Preliminary Analysis code, not redefined here."),
    ("all three",
     "whether the sector has settled on a dominant design",
     "conditions 1, 2 and 3 hold in the same window, and the window is complete",
     "Preliminary Analysis 5.7. The conditions are deliberately different in kind — counts, "
     "balance, form — and a sector can satisfy one without the others."),
]


def dominant_design_conditions() -> pd.DataFrame:
    """Table of the three conditions as they were fixed in advance: what each tests, the
    threshold, and where the threshold comes from. No number of this corpus enters it."""
    return pd.DataFrame(DD_CONDITIONS,
                        columns=["condition", "what it tests", "the threshold",
                                 "where the threshold comes from"])


def _pct(x: float) -> str:
    """A share as the document prints one: one decimal, dropped when it is zero, thin space."""
    s = f"{float(x):.1%}"
    return (s[:-3] if s.endswith(".0%") else s[:-1]) + " %"


#: how many of the earliest windows set the reference level of condition 3 ("the level of the
#: earliest windows", Preliminary Analysis 5.7)
Q_BASELINE_WINDOWS = 2
#: the weighting Preliminary Analysis 5.3 fixes as the main one, and the robustness weighting
#: reported beside it (5.3: "Uniform weighting is computed as well, and reported as a robustness
#: check. When the two produce the same shape, the finding is about the corpus. When they
#: disagree, the finding is about the weighting, and the chapter says which.")
Q_WEIGHTINGS = ("subsystem", "uniform")


def dominant_design_q(ds: Dataset, v: pd.DataFrame, levels: Tuple[str, ...] = ("A0c", "A1t"),
                      perms: int = 200, seed: int = 42, baseline: int = Q_BASELINE_WINDOWS) -> pd.DataFrame:
    """Condition 3 per window: Rao's quadratic entropy Q of the Gower distance, against the level
    of the earliest windows and a permutation band.

    The distance is the one fixed in Preliminary Analysis 5.3 and is **imported** from
    :mod:`a3` — the shortlist (:func:`a3.gower_fields`), the pooled wing-borne pair of rule 4,
    the subsystem weighting and the δ treatment of blanks all come from there, and nothing in
    the Preliminary Analysis is modified. Q is the mean distance over the ordered pairs of a
    window (Rao, 1982; 5.5), which is the expected distance between two aircraft of that window
    drawn at random.

    Q needs no archetype, which is what makes it the independent check of the three conditions.
    It is still reported per level, because the two levels admit slightly different aircraft: a
    level leaves out the aircraft whose fields an override hides, so ``A1t`` is measured on the
    aircraft it can name and ``A0c`` on its own. The window labels are shuffled across the
    aircraft (window sizes kept, every aircraft keeping its labels) to build the band, which is
    the same guard condition 2 uses, applied to the difference from the earliest windows.
    """
    frame = a3.gower_frame(ds)
    fields = a3.gower_fields(ds, pooled=True)
    ids = frame["aircraft_id"].to_numpy()
    at = {a: i for i, a in enumerate(ids)}
    base_windows = WINDOW_NAMES[:baseline]
    rows = []
    for weighting in Q_WEIGHTINGS:
        D = a3.gower_distance(ds, frame, fields, weighting=weighting)

        def q(idx: np.ndarray) -> float:
            return float(np.nanmean(D[np.ix_(idx, idx)])) if len(idx) else float("nan")

        for level in levels:
            key = _archetype_key(v, level)
            sub = v[key.notna()].dropna(subset=["window"]).copy()
            sub["row"] = sub["aircraft_id"].map(at)
            sub = sub[sub["row"].notna()]
            per = {w: sub[sub["window"].eq(w)]["row"].astype(int).to_numpy() for w in WINDOW_NAMES}
            obs = {w: q(r) for w, r in per.items() if len(r) >= 10}
            ref = float(np.mean([obs[w] for w in base_windows if w in obs]))
            rng = np.random.default_rng(seed)
            pool = sub["row"].astype(int).to_numpy()
            band = {w: [] for w in obs}
            for _ in range(perms):
                shuffled = rng.permutation(pool)
                cut, drawn = 0, {}
                for w in WINDOW_NAMES:
                    take = len(per[w])
                    drawn[w] = q(shuffled[cut:cut + take]) if take >= 10 else float("nan")
                    cut += take
                r0 = float(np.mean([drawn[w] for w in base_windows if w in obs]))
                for w in obs:
                    band[w].append(drawn[w] - r0)
            for w in WINDOW_NAMES:
                if w not in obs:
                    continue
                arr = np.array(band[w])
                lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
                rows.append({
                    "level": level, "weighting": weighting, "window": w,
                    "aircraft": int(len(per[w])), "Q": round(obs[w], 4),
                    "Q of the earliest windows": round(ref, 4),
                    "ΔQ": round(obs[w] - ref, 4),
                    "ΔQ permutation low": round(lo, 4), "ΔQ permutation high": round(hi, 4),
                    "below band": bool(obs[w] - ref < lo),
                })
    return pd.DataFrame(rows)


def dominant_design_result(dd: pd.DataFrame, complete: Optional[List[str]] = None,
                           q: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """One generated sentence per condition, built from :func:`dominant_design`.

    Every figure in the sentences is read out of ``dd``; nothing is typed. ``complete`` is the
    list of windows that are complete (the partial window is named as partial in the sentence),
    because conditions 1 and the verdict are only recorded on complete windows.
    """
    complete = complete or [w for w in WINDOW_NAMES if "partial" not in w]
    levels = list(dict.fromkeys(dd["level"]))
    rows = []

    # ---- condition 1: the top share against the 50 % line
    parts, fails, total, peak = [], 0, 0, 0.0
    for lvl in levels:
        s = dd[dd["level"].eq(lvl)]
        total += len(s)
        fails += int((~s["condition 1 (> 50 %)"]).sum())
        best = s.loc[s["top share"].idxmax()]
        bc = s[s["window"].isin(complete)]
        bestc = bc.loc[bc["top share"].idxmax()]
        peak = max(peak, float(best["top share"]))
        same = best["window"] == bestc["window"]
        parts.append(f"At {lvl} the largest share of any window is {_pct(best['top share'])} "
                     f"({best['top archetype']}, {best['window']})"
                     + ("" if same else f", and of any complete window {_pct(bestc['top share'])} "
                                        f"({bestc['top archetype']}, {bestc['window']})")
                     + (", and that window is complete" if same and best["window"] in complete else ""))
    c1 = (f"Condition 1 fails in {fails} of the {total} level-windows measured: no window at either "
          f"level reaches the {_pct(0.5)} line, so no two consecutive windows can clear it either. "
          + ". ".join(parts) + f". The largest share anywhere in the corpus is {_pct(peak)}: the "
          f"{_pct(0.5)} line is {0.5 / peak:.1f} times it.")
    rows.append({"condition": DD_CONDITIONS[0][0], "observed result": c1,
                 "met": f"no, in {fails} of {total} level-windows"})

    # ---- condition 2: ²D against the permutation band
    parts, any_below = [], 0
    for lvl in levels:
        s = dd[dd["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES).dropna(subset=["D2"])
        below = s[s["below band"].astype(bool)]
        above = s[s["D2"] > s["D2 permutation high"]]
        any_below += len(below)
        if len(below):
            named = "; ".join(f"{w}, ²D {r['D2']:.2f} against a band of {r['D2 permutation low']:.2f} "
                              f"to {r['D2 permutation high']:.2f}" for w, r in below.iterrows())
            parts.append(f"at {lvl}, ²D falls below the band in {len(below)} of the {len(s)} windows "
                         f"({named}), and lies inside it in the rest")
        else:
            extra = (f", and in {len(above)} of them above it ("
                     + "; ".join(f"{w}, ²D {r['D2']:.2f} against {r['D2 permutation low']:.2f} to "
                                 f"{r['D2 permutation high']:.2f}" for w, r in above.iterrows()) + ")") if len(above) else ""
            parts.append(f"at {lvl}, ²D falls below the band in none of the {len(s)} windows{extra}")
    below_lvls = sorted({lvl for lvl in levels
                         if bool(dd[dd["level"].eq(lvl)]["below band"].astype(bool).any())})
    c2 = ((f"Condition 2 is met in {any_below} of the {total} level-windows, all of them at "
           f"{' and '.join(below_lvls)}: " if any_below
           else "Condition 2 is met in no window: ") + "; ".join(parts) + ".")
    rows.append({"condition": DD_CONDITIONS[1][0], "observed result": c2,
                 "met": (f"in {any_below} of {total} level-windows, at {' and '.join(below_lvls)} only"
                         if any_below else "no, in every window")})

    # ---- condition 3: Q against the level of the earliest windows
    if q is None or not len(q):
        rows.append({"condition": DD_CONDITIONS[2][0],
                     "observed result": "Condition 3 is not answered in this document: Q needs the Gower "
                                        "distance fixed in Preliminary Analysis 5.3, which is not computed here.",
                     "met": "not computed"})
        q_fired = {}
    else:
        main = q[q["weighting"].eq(Q_WEIGHTINGS[0])]
        alt = q[q["weighting"].eq(Q_WEIGHTINGS[1])]
        q_fired = {(r["level"], r["window"]) for _, r in main.iterrows() if r["below band"]}
        parts = []
        for lvl in levels:
            s3 = main[main["level"].eq(lvl)]
            if not len(s3):
                continue
            hit = s3[s3["below band"].astype(bool)]
            ref = float(s3["Q of the earliest windows"].iloc[0])
            if len(hit):
                named = "; ".join(f"{r['window']}, Q {r['Q']:.4f}, ΔQ {r['ΔQ']:+.4f} against a band of "
                                  f"{r['ΔQ permutation low']:+.4f} to {r['ΔQ permutation high']:+.4f}"
                                  for _, r in hit.iterrows())
                parts.append(f"at {lvl}, where the two earliest windows sit at Q {ref:.4f}, Q falls below "
                             f"that level by more than the band in {len(hit)} of the {len(s3)} windows "
                             f"({named}), and stays inside the band in the rest")
            else:
                parts.append(f"at {lvl}, where the two earliest windows sit at Q {ref:.4f}, Q stays inside "
                             f"the band in all {len(s3)} windows")
        n_hit = len(q_fired)
        robust = []
        for lvl, win in sorted(q_fired):
            a = alt[alt["level"].eq(lvl) & alt["window"].eq(win)]
            if len(a):
                r = a.iloc[0]
                robust.append(f"{lvl} {win}: ΔQ {r['ΔQ']:+.4f} against {r['ΔQ permutation low']:+.4f} to "
                              f"{r['ΔQ permutation high']:+.4f}, {'below the band' if r['below band'] else 'inside the band'}")
        same = bool(len(alt)) and set(q_fired) == {(r["level"], r["window"]) for _, r in alt.iterrows() if r["below band"]}
        c3 = (f"Condition 3 is met in {n_hit} of the {len(main)} level-windows under the subsystem weighting "
              f"fixed in 5.3: " + "; ".join(parts) + ". "
              + (f"Under the uniform weighting reported beside it the same level-windows "
                 f"{'also fall below the band' if same else 'do not all fall below the band'} "
                 f"({'; '.join(robust)}), so the reading "
                 f"{'is about the corpus and not the weighting' if same else 'depends on the weighting, and 5.3 fixes the subsystem weighting as the main one'}."
                 if robust else "")).strip()
        rows.append({"condition": DD_CONDITIONS[2][0], "observed result": c3,
                     "met": (f"in {n_hit} of {len(main)} level-windows, under the main weighting only"
                             if n_hit and not same else
                             f"in {n_hit} of {len(main)} level-windows" if n_hit else "no, in every window")})

    # ---- the verdict, and what the corpus does instead
    lvlN = levels[-1]
    sN = dd[dd["level"].eq(lvlN)].set_index("window").reindex(WINDOW_NAMES).dropna(subset=["top share"])
    last3 = sN["top share"].iloc[-3:]
    rising = list(last3) == sorted(last3)
    # where each condition fired, as (level, window) — the verdict names both levels throughout
    fired2 = {(r["level"], r["window"]) for _, r in dd.iterrows() if bool(r["below band"])}
    both = sorted(fired2 & q_fired)
    def _say(pairs):
        """`at A0c in <= 2011 and 2012-15`, or `at A0c and A1t in 2020-23` when both fire alike."""
        if not pairs:
            return "in no window at either level"
        by = {}
        for lv in levels:
            wins = tuple(w for w in WINDOW_NAMES if (lv, w) in pairs)
            if wins:
                by.setdefault(wins, []).append(lv)
        return "; ".join(f"at {' and '.join(lvs)} in {' and '.join(wins)}" for wins, lvs in by.items())
    d2_line = "; ".join(
        f"at {lv}, ²D is lowest in {d.D2.idxmin()} ({d.D2.min():.2f}) and highest in "
        f"{d.D2.idxmax()} ({d.D2.max():.2f})"
        for lv, d in ((l, dd[dd["level"].eq(l)].set_index("window").reindex(WINDOW_NAMES).dropna(subset=["D2"]))
                      for l in levels))
    verdict = (f"No window satisfies the three conditions together, at either level, so the corpus records "
               f"no dominant design over the period it covers. The three fail in different places: "
               f"condition 1 fails in all {len(dd)} level-windows, at {' and '.join(levels)} alike; "
               f"condition 2 is met {_say(fired2)}; condition 3 is met {_say(q_fired)}"
               + (f", and no level-window meets more than one of them"
                  if not both else f", and the two meet in {len(both)} level-window(s): {_say(both)}")
               + f". Diversity does not fall over the period: {d2_line}. The one movement towards a "
               f"dominant design is at {lvlN}, where the share of its largest archetype "
               f"({sN['top archetype'].iloc[-1]}) "
               f"{'rises' if rising else 'moves'} over the last three windows, "
               + " then ".join(_pct(x) for x in last3)
               + f", which is {_pct(float(last3.iloc[-1]))} of that window and still short of the "
                 f"{_pct(0.5)} line.")
    rows.append({"condition": DD_CONDITIONS[3][0], "observed result": verdict,
                 "met": "no"})
    return pd.DataFrame(rows)


# ---------------------------------------- 4.1.4 / 4.1.5: which classes can be drawn ----
#: A class earns a line in 4.1.4 and 4.1.5 when it can carry one: at least ``MIN_CELL``
#: unique aircraft in at least ``MIN_WINDOWS`` of the five windows, so no line is a trend
#: drawn through two points. This replaces the earlier "four largest classes", which was a
#: size ranking and not a rule and which nothing in the document justified (user, 2026-09-22).
MIN_CELL = 5
MIN_WINDOWS = 3


def class_selection(v: pd.DataFrame, min_cell: int = MIN_CELL,
                    min_windows: int = MIN_WINDOWS) -> Dict[str, object]:
    """The classes 4.1.4 and 4.1.5 draw, and the numbers that justify the selection.

    Keys: ``classes`` (codes, largest first), ``names``, ``aircraft`` they hold,
    ``classified`` (every aircraft with a class), ``share`` of it, ``dropped`` (the classes
    left out, with their size), ``suppressed`` (windows a drawn class does reach but with
    too few aircraft to report -- the class is present there, the cell is not reportable),
    ``min_cell`` and ``min_windows``.

    ``suppressed`` exists so a blank can never be read as "the class did not exist yet":
    every cell the threshold removes is named, with its count, wherever the rule is printed.
    """
    w = v.dropna(subset=["window", "topType"])
    ct = pd.crosstab(w["topType"], w["window"]).reindex(columns=WINDOW_NAMES, fill_value=0)
    windows_ok = (ct >= min_cell).sum(axis=1)
    sizes = ct.sum(axis=1).sort_values(ascending=False)
    keep = [c for c in sizes.index if windows_ok[c] >= min_windows]
    held = int(sizes[keep].sum())
    return {"classes": keep, "names": [metrics.ARCH_NAMES.get(c, c) for c in keep],
            "aircraft": held, "classified": int(sizes.sum()),
            "share": round(held / max(int(sizes.sum()), 1), 3),
            "windows_drawn": {c: int(windows_ok[c]) for c in keep},
            "dropped": {c: int(sizes[c]) for c in sizes.index if c not in keep},
            "suppressed": {c: [(wn, int(ct.loc[c, wn])) for wn in WINDOW_NAMES
                               if 0 < ct.loc[c, wn] < min_cell] for c in keep
                           if any(0 < ct.loc[c, wn] < min_cell for wn in WINDOW_NAMES)},
            "min_cell": min_cell, "min_windows": min_windows}


def drawn_classes(v: pd.DataFrame, min_cell: int = MIN_CELL, min_windows: int = MIN_WINDOWS) -> List[str]:
    """The class codes 4.1.4 and 4.1.5 draw, largest first (see :func:`class_selection`)."""
    return list(class_selection(v, min_cell, min_windows)["classes"])


def unit_band(v: pd.DataFrame) -> pd.Series:
    """Propulsive units per aircraft -> 1-3 / 4 / 5-6 / 7-8 / 9+, with the two honest
    exceptions spelled out rather than binned (see :data:`UNIT_BANDS`)."""
    u = pd.to_numeric(v["units"], errors="coerce")
    band = pd.cut(u, bins=UNIT_BANDS[0], labels=UNIT_BANDS[1]).astype(object).where(u.notna())
    band = band.mask(u.eq(0), UNIT_ZERO)
    return band.mask(v["rotorBin"].astype(str).eq(a2.NO_M3_CARD), NO_UNIT_CARD)


def class_configs(v: pd.DataFrame, classes: Optional[List[str]] = None) -> pd.DataFrame:
    """Within-class convergence per class and window.

    A *configuration* is one aircraft's combination of four label fields: propulsive units
    banded (M3), ducted or open (M3), booms or no booms (M1) and tail type (M2/empType). The
    table gives the class's single most common configuration, the share of its aircraft that
    hold it, and how many distinct configurations the class holds in the window. The unit is
    the unique aircraft throughout; a row is a class, not an archetype. The share is a mode
    and not a mean because a configuration is a combination of categories -- it has no
    arithmetic and therefore no average. Windows with fewer than :data:`MIN_CELL` aircraft
    of the class are kept as a row but left blank rather than reported.
    """
    classes = classes or drawn_classes(v)
    w = v.dropna(subset=["window", "topType"]).copy()
    w["band"] = unit_band(w)
    w["ducted"] = w["any_ducted"].map({True: "ducted", False: "open"}).fillna("duct n/d")
    w["booms"] = np.where(w["nBooms"].fillna(0) > 0, "booms", "no booms")
    w["tail"] = w["empType"].fillna("tail n/d").astype(str)
    w["config"] = (w["band"].astype(str) + " propulsive units · " + w["ducted"] + " · "
                   + w["booms"] + " · " + w["tail"])
    rows = []
    for c in classes:
        sub_c = w[w["topType"].eq(c) & w["band"].notna()]
        for name in WINDOW_NAMES:
            sub = sub_c[sub_c["window"].eq(name)]
            row = {"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name,
                   "aircraft": int(len(sub)), "distinct configurations": int(sub["config"].nunique()),
                   "most common configuration": "", "share in it": np.nan}
            if len(sub) >= MIN_CELL:
                vc = sub["config"].value_counts(normalize=True)
                row["most common configuration"] = vc.index[0]
                row["share in it"] = round(float(vc.iloc[0]), 3)
            rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs.update(class_selection(v))
    return out


def dimension_drift(v: pd.DataFrame, classes: Optional[List[str]] = None) -> pd.DataFrame:
    """Per class and window, one row per class x window of every drawn class.

    Every ``share`` is a share of *aircraft*, never of rotors. For propulsive units, ducted,
    tail and booms the denominator is the ``aircraft`` column of the same row: in the classes
    drawn here every one of those fields is answered for every aircraft. ``share electric
    only`` is the one exception -- a patent that never states a powertrain is excluded, so it
    divides by ``powertrain stated``, which is smaller, and the cell is left blank when fewer
    than :data:`MIN_CELL` aircraft state one (user ruling, five panels, 2026-09-22).

    ``share with a tilting unit`` is kept as a column but no longer drawn: it is flat by
    construction -- a Tilt Rotor, Combined vectored thrust or Tilt Wing carries tilting units
    by definition of the class and Lift + Cruise carries none -- so its only information is
    the handful of points off 0 % and 100 %, which are an internal check on the labelling.
    Its panel was replaced by tail type, which makes the figure the exact decomposition of the
    configuration defined in 4.1.4, and by powertrain.

    A window holding fewer than :data:`MIN_CELL` aircraft of the class keeps its row, with the
    count and blank measures, rather than being dropped: the class is present in that window
    and only the cell is too thin to report, so an absent row must never be read as an absent
    class (2026-09-22).
    """
    classes = classes or drawn_classes(v)
    w = v.dropna(subset=["window", "topType"])
    rows = []
    for c in classes:
        for name in WINDOW_NAMES:
            sub = w[w["topType"].eq(c) & w["window"].eq(name)]
            if len(sub) < MIN_CELL:
                rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name,
                             "aircraft": int(len(sub)), "median propulsive units": np.nan,
                             "share with a ducted unit": np.nan, "share with no tail surface": np.nan,
                             "share with booms": np.nan, "share electric only": np.nan,
                             "share with a tilting unit": np.nan, "median wings": np.nan,
                             "propulsive units answered": 0, "ducted answered": 0, "tail answered": 0,
                             "booms answered": 0, "powertrain stated": 0, "tilting answered": 0})
                continue
            power = sub["is_electric_final"].astype(str)
            stated = power.ne("Unknown")
            rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name, "aircraft": int(len(sub)),
                         "median propulsive units": float(pd.to_numeric(sub["units"], errors="coerce").median()),
                         "share with a ducted unit": round(float(sub["any_ducted"].map({True: 1, False: 0}).mean()), 2),
                         "share with no tail surface": round(float(sub["empType"].astype(str).eq("Tailless").mean()), 2),
                         "share with booms": round(float((pd.to_numeric(sub["nBooms"], errors="coerce")
                                                          .dropna() > 0).mean()), 2),
                         # the one narrower base: "not stated" is excluded, and a cell resting on
                         # fewer than MIN_CELL stated powertrains is blank rather than reported
                         "share electric only": (round(float(power[stated].eq("Yes").mean()), 2)
                                                 if int(stated.sum()) >= MIN_CELL else np.nan),
                         "share with a tilting unit": round(float(sub["any_tilting"].map({True: 1, False: 0}).mean()), 2),
                         "median wings": float(pd.to_numeric(sub["wCount"], errors="coerce").median()),
                         "propulsive units answered": int(pd.to_numeric(sub["units"], errors="coerce").notna().sum()),
                         "ducted answered": int(sub["any_ducted"].notna().sum()),
                         "tail answered": int(sub["empType"].notna().sum()),
                         "booms answered": int(pd.to_numeric(sub["nBooms"], errors="coerce").notna().sum()),
                         "powertrain stated": int(stated.sum()),
                         "tilting answered": int(sub["any_tilting"].notna().sum())})
    out = pd.DataFrame(rows)
    out.attrs.update(class_selection(v))
    return out


# ------------------------------------------------------- 4.2 new: transitions, IP, cohorts, timeline
def transitions(v: pd.DataFrame) -> pd.DataFrame:
    """Within-firm successions: each named firm's aircraft in priority order, every consecutive pair
    (earlier class → later class). Rows: from, to, count."""
    w = v[v["named"] & v["topType"].notna()].dropna(subset=["year"]).sort_values(["company_canonical", "year", "aircraft_id"])
    pairs = []
    for f, sub in w.groupby("company_canonical"):
        t = sub["topType"].tolist()
        for a, b in zip(t[:-1], t[1:]):
            pairs.append({"firm": f, "from": a, "to": b})
    p = pd.DataFrame(pairs)
    out = p.groupby(["from", "to"]).size().reset_index(name="pairs")
    out["same class"] = out["from"].eq(out["to"])
    out.attrs["firms"] = int(p["firm"].nunique())
    out.attrs["pairs"] = int(len(p))
    out.attrs["same share"] = round(float(p["from"].eq(p["to"]).mean()), 2)
    return out


def ip_strategy(ds: Dataset, v: pd.DataFrame, min_aircraft: int = FIRM_MIN) -> pd.DataFrame:
    """Per firm with ``min_aircraft`` or more: unique aircraft, representative patents (primary + O1/O2),
    patents per aircraft, median family size, median claims, mean forward citations, in-corpus
    self-citation share."""
    av = ds.approved_variants.merge(ds.identity[["patent_id", "company_canonical", "family_size", "claim_count",
                                                 "forward_citations", "forward_citations_in_corpus",
                                                 "self_citations_in_corpus"]], on="patent_id", how="left",
                                    suffixes=("", "_id"))
    sizes = firm_sizes(v)
    rows = []
    for f, n_air in sizes[sizes >= min_aircraft].items():
        sub = av[av["company_canonical"].eq(f)].drop_duplicates("patent_id")
        fwd_corpus = pd.to_numeric(sub["forward_citations_in_corpus"], errors="coerce").sum()
        self_c = pd.to_numeric(sub["self_citations_in_corpus"], errors="coerce").sum()
        rows.append({"firm": f, "unique aircraft": int(n_air), "patents": int(len(sub)),
                     "patents per aircraft": round(len(sub) / n_air, 2),
                     "median family size": float(pd.to_numeric(sub["family_size"], errors="coerce").median()),
                     "median claims": float(pd.to_numeric(sub["claim_count"], errors="coerce").median()),
                     "mean forward citations": round(float(pd.to_numeric(sub["forward_citations"], errors="coerce").mean()), 1),
                     "in-corpus forward citations": int(fwd_corpus),
                     "self-citation share (in corpus)": (round(float(self_c / fwd_corpus), 2) if fwd_corpus else np.nan),
                     "region": v[v["company_canonical"].eq(f)]["region3"].mode().iloc[0]})
    return pd.DataFrame(rows).sort_values("unique aircraft", ascending=False).reset_index(drop=True)


def ip_by_class(v: pd.DataFrame) -> pd.DataFrame:
    """Per class: median claims, mean and median forward citations, median family size (primary patents)."""
    w = v.dropna(subset=["topType"]).drop_duplicates("patent_id")
    g = w.groupby("topType").agg(patents=("patent_id", "size"),
                                 **{"median claims": ("claim_count", lambda s: pd.to_numeric(s, errors="coerce").median()),
                                    "mean forward citations": ("forward_citations", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                                    "median forward citations": ("forward_citations", lambda s: pd.to_numeric(s, errors="coerce").median()),
                                    "median family size": ("family_size", lambda s: pd.to_numeric(s, errors="coerce").median()),
                                    "median priority year": ("year", "median")})
    g = g.sort_values("patents", ascending=False).round(1)
    g.index = [metrics.ARCH_NAMES.get(c, c) for c in g.index]
    g.index.name = "class"
    return g.reset_index()


def cohorts(v: pd.DataFrame) -> pd.DataFrame:
    """Named firms by the window of their first filing and the class they entered with."""
    w = v[v["named"]].dropna(subset=["window", "year"]).sort_values("year")
    first = w.groupby("company_canonical").first()
    tab = pd.crosstab(first["window"], first["topType"]).reindex(index=WINDOW_NAMES, fill_value=0)
    tab.insert(0, "firms entering", tab.sum(axis=1))
    return tab.reset_index()


def _first_year(text) -> Optional[int]:
    m = re.search(r"(19|20)\d{2}", str(text))
    return int(m.group(0)) if m else None


def ari_timeline(v: pd.DataFrame) -> pd.DataFrame:
    """For the index firms in the corpus: first patent, peak filing year, first flight and entry into
    service as the index states them."""
    cur, hist, cmap = _load_ari()
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows() if r["company_canonical"]}
    cur["company"] = cur["oem"].map(_oem_key).map(key_to_canon)
    rows = []
    for _, r in cur.dropna(subset=["company"]).iterrows():
        sub = v[v["company_canonical"].eq(r["company"])].dropna(subset=["year"])
        if not len(sub):
            continue
        yrs = sub["year"].astype(int)
        rows.append({"company": r["company"], "ARI score": float(r["ari"]), "first patent": int(yrs.min()),
                     "peak filing year": int(yrs.value_counts().sort_index().idxmax()), "last patent": int(yrs.max()),
                     "unique aircraft": int(len(sub)), "first flight (ARI)": _first_year(r["first_flight"]),
                     "entry into service (ARI)": _first_year(r["eis"]), "regulator (ARI)": r["cert_regulator"],
                     "ARI vehicle type": r["vehicle_type"]})
    return pd.DataFrame(rows).sort_values("first patent").reset_index(drop=True)


# ------------------------------------------------------- 4.3 new: specialisation index
def specialisation(v: pd.DataFrame, min_aircraft: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Location quotient of each A0c archetype per region: its share in the region divided by its
    share overall. 1 = as everywhere, 2 = twice the overall share. Returns (LQ, counts)."""
    w = v.dropna(subset=["archetype"])
    w = w[w["region3"].isin(REGIONS)]
    keep = w["archetype"].value_counts()
    keep = keep[keep >= min_aircraft].index
    w = w[w["archetype"].isin(keep)]
    counts = pd.crosstab(w["archetype"], w["region3"]).reindex(columns=REGIONS, fill_value=0)
    counts = counts.loc[counts.sum(axis=1).sort_values(ascending=False).index]
    share_region = counts.div(counts.sum(axis=0), axis=1)
    share_all = counts.sum(axis=1) / counts.values.sum()
    lq = share_region.div(share_all, axis=0)
    return lq.round(2), counts


# ------------------------------------------------------- 5 low level
def industry_by_class(v: pd.DataFrame) -> pd.DataFrame:
    w = v.dropna(subset=["topType"])
    tab = pd.crosstab(w["topType"], w["industry_primary"].fillna("General_Unspecified"))
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]
    tab.insert(0, "aircraft", tab.sum(axis=1))
    tab.index = [metrics.ARCH_NAMES.get(c, c) for c in tab.index]
    tab.index.name = "class"
    return tab.reset_index()


STATUS_SHORT = {"ACTIVE - GRANTED": "granted, in force", "ACTIVE - APPLIED": "pending",
                "INACTIVE - WITHDRAWN / SURRENDERED": "withdrawn", "INACTIVE - NONPAYMENT": "lapsed (non-payment)",
                "INACTIVE - EXPIRED": "expired", "INACTIVE - REJECTED / REFUSED / SUSPENDED": "refused"}
STATUS_ORDER = ["granted, in force", "pending", "lapsed (non-payment)", "expired", "withdrawn", "refused"]


def examination(v: pd.DataFrame, by: str = "pub_office", top: int = 6) -> pd.DataFrame:
    """Legal status of the primary patents by publication office (top offices) or by class."""
    w = v.drop_duplicates("patent_id").copy()
    w["status"] = w["legal_status_raw"].map(STATUS_SHORT).fillna("unknown")
    if by == "pub_office":
        keep = w["pub_office"].value_counts().head(top).index
        w = w[w["pub_office"].isin(keep)]
        key = w["pub_office"]
    else:
        w = w.dropna(subset=["topType"])
        key = w["topType"].map(lambda c: metrics.ARCH_NAMES.get(c, c))
    tab = pd.crosstab(key, w["status"]).reindex(columns=[s for s in STATUS_ORDER if s in w["status"].values], fill_value=0)
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]
    tab.insert(0, "patents", tab.sum(axis=1))
    tab.index.name = by
    return tab.reset_index()


def powertrain_by_class(v: pd.DataFrame) -> pd.DataFrame:
    w = v.dropna(subset=["topType"])
    tab = pd.crosstab(w["topType"], w["is_electric_final"].fillna("Unknown")).reindex(
        columns=[c for c in ["Yes", "Hybrid", "Unknown", "No"] if c in w["is_electric_final"].fillna("Unknown").values], fill_value=0)
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]
    tab.columns = [{"Yes": "electric", "Hybrid": "hybrid", "Unknown": "not stated", "No": "non-electric"}[c] for c in tab.columns]
    tab.insert(0, "aircraft", tab.sum(axis=1))
    tab.index = [metrics.ARCH_NAMES.get(c, c) for c in tab.index]
    tab.index.name = "class"
    return tab.reset_index()


def lag_p90(ds: Dataset) -> float:
    """90th percentile of the priority-to-publication lag, years, representative primary patents."""
    j = ds.patents_analysis.merge(ds.identity[["patent_id", "priority_year", "pub_year"]], on="patent_id", how="left",
                                  suffixes=("", "_id"))
    lag = pd.to_numeric(j["pub_year"], errors="coerce") - pd.to_numeric(j["priority_year"], errors="coerce")
    return float(lag.dropna().quantile(0.9))


def filings_per_year(ds: Dataset, v: pd.DataFrame, snapshot: str = "2026-06-08") -> pd.DataFrame:
    """Unique aircraft per priority year by region, patents acquired per priority year, and whether
    the year is complete: complete when the snapshot lies at least the 90th-percentile lag after the
    end of the year."""
    p90 = lag_p90(ds)
    snap = pd.Timestamp(snapshot)
    w = v.dropna(subset=["year"]).copy()
    w["year"] = w["year"].astype(int)
    tab = pd.crosstab(w["year"], w["region3"]).reindex(columns=REGIONS + ["Other regions"], fill_value=0)
    acq = ds.patents.merge(ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left", suffixes=("", "_id"))
    acq_y = pd.to_numeric(acq["priority_year"], errors="coerce").dropna().astype(int).value_counts()
    years = range(int(tab.index.min()), int(tab.index.max()) + 1)
    tab = tab.reindex(years, fill_value=0)
    tab["unique aircraft"] = tab[REGIONS + ["Other regions"]].sum(axis=1)
    tab["patents acquired"] = acq_y.reindex(years, fill_value=0).to_numpy()
    elapsed = (snap - pd.to_datetime([f"{y}-12-31" for y in years])).days / 365.25
    tab["years since year end"] = np.round(elapsed, 1)
    tab["complete"] = elapsed >= p90
    tab.attrs["p90"] = p90
    tab.attrs["snapshot"] = snapshot
    tab.index.name = "priority year"
    # the raw counts stay the primary reading; the aviation baseline is appended beside them so
    # the year-on-year rise can be read against aeronautics patenting as a whole (user, 2026-09-22).
    # Falls through untouched when the stored baseline is not installed -- see la_baseline.
    tab = la_baseline.attach(tab)
    return tab.reset_index()


def flags() -> pd.DataFrame:
    """Items the author of the build would cut for a 16-page version — the user decides."""
    rows = [
        ("Table 1.1b publication lag", "1.1", "a data-quality fact, already in the PA"),
        ("Table 1.2b aircraft per patent", "1.2", "one number (627 / 44) the funnel already gives"),
        ("Figure 1.3 evidence per aircraft", "1.3", "refinement detail; the table beside it carries the counts"),
        ("Figure 2.1a the four cards", "2", "repeats Figure 2.1b"),
        ("Table 3.1 missingness", "3.1", "the figure shows the same shares"),
        ("Table 3.3a flagship", "3.3", "the figure shows the same matches"),
        ("Table 3.5 field inventory", "3.5", "the figure shows the same ranking"),
        # 2026-09-22: the two 4.1.2 robustness figures and Table 4.1.2 were cut on the author's ruling,
        # so they are no longer candidates. Their builders are kept (fig_firm_weighted, fig_two_counts).
        ("4.1.7 lead and lag, figure and tables", "4.1.7", "timing question rated less important"),
        ("Table 4.1.8 Hill numbers", "4.1.8", "the figure shows the same values"),
        ("Table 4.1.9 zones", "4.1.9", "20 rows; the figure carries it"),
        ("Figure 4.2.5b re-filing spans", "4.2.5", "its one useful number is in the IP figure"),
        ("Table 4.2.6a firm proximity", "4.2.6", "17 rows; the heatmap carries it"),
        ("4.3.4 country × class, figure and table", "4.3.4", "the specialisation index (4.3.3) answers it at archetype level"),
        ("5.4 image-level answers", "5.4", "T2 detail; keep only if the image chapter needs it here"),
        ("Tables 5.5b–f mission crosstabs", "5.5", "five small tables the mission figure already shows"),
    ]
    return pd.DataFrame(rows, columns=["item", "section", "why it could go"])

# ------------------------------------------------------- placeholders -------
def relabel_protocol() -> pd.DataFrame:
    return pd.DataFrame([
        ("status", "pending — the wizard export of the relabel batch is not yet installed"),
        ("sample", "50 primary patents, stratified by architecture class"),
        ("timing", "relabelled at least four weeks after labelling closed (2026-09-19)"),
        ("measure", "per field: agreement and Cohen's kappa, first label against second"),
        ("output", "table of kappa per field; figure of agreement per class"),
    ], columns=["item", "value"])


def trl_placeholder() -> pd.DataFrame:
    return pd.DataFrame([
        ("status", "pending — TRL per firm comes from the user's separate work"),
        ("planned figure a", "firms ranked by TRL, with the share of the analysis set the top 20 / 40 / 100 cover"),
        ("planned figure b", "TRL band against class mix, propulsive units and number of classes per firm"),
    ], columns=["item", "value"])


# ------------------------------------------------------- everything ---------
def build_all(ds: Dataset) -> Dict[str, pd.DataFrame]:
    v = base(ds)
    tables: Dict[str, pd.DataFrame] = {}
    tables["la_firm_weighted_shares"] = firm_weighted_shares(v)
    _, tables["la_lead_lag_region"] = lead_lag(v, "region3")
    _, tables["la_lead_lag_class"] = lead_lag(v, "topType", top=7)
    tables["la_class_cycles"] = class_cycles(v)
    tables["la_hill_by_window"] = hill_by_window(v)
    tables["la_zones"] = zones(v)
    tables["la_abandonment_by_class"] = abandonment_by_class(v)
    shares, n = country_class(v)
    cc = shares.round(2).copy()
    cc.insert(0, "aircraft", n)
    cc.columns = [metrics.ARCH_NAMES.get(c, c) if c != "aircraft" else c for c in cc.columns]
    tables["la_country_class"] = cc.reset_index().rename(columns={"assignee_country": "country"})
    # parked 2026-09-23 (author's ruling on 4.2.1: the curve now carries the counts, so the tier
    # table is not printed). Still built, so the numbers behind the curve stay checkable in
    # tables/la_firm_tiers.csv; put the name back in node 4.2.1 of la_index.NODES to print it.
    tables["la_firm_tiers"] = firm_tiers(v)
    tables["la_coverage_segments"] = coverage_segments(v)
    tables["la_market_vs_patents"] = market_vs_patents(v)
    tables["la_filer_mix"] = filer_mix(v)
    tables["la_firm_leverage"] = firm_leverage(v)
    tables["la_class_concentration"] = class_concentration(v)
    tables["la_cohort_mix"] = cohort_mix(v)
    tables["la_filers_by_window"] = filers_by_window(v)
    tables["la_firm_windows"] = firm_windows(v)
    _, tables["la_proximity_region"] = proximity_by_region(ds, v)
    firms = ari_firms(v)
    tables["la_ari_firms"] = firms
    tables["la_ari_correlation"] = ari_correlation(firms, v)
    tables["la_class_fold"] = class_fold_table(v)
    tables["la_name_arch_check"] = name_arch_check(v)
    linked = linked_aircraft(v)
    tables["la_linked_aircraft"] = linked
    for k, t in mission_tables(linked).items():
        tables[f"la_mission_{k}"] = t
    tables["la_relabel_protocol"] = relabel_protocol()
    tables["la_trl_placeholder"] = trl_placeholder()
    lv = archetype_levels(ds, v)
    tables["la_archetype_levels"] = lv
    tables["la_archetype_choice"] = archetype_level_choice(lv)
    tables["la_dd_conditions"] = dominant_design_conditions()
    tables["la_dominant_design"] = dominant_design(v)
    tables["la_dd_q"] = dominant_design_q(ds, v)
    tables["la_dd_result"] = dominant_design_result(tables["la_dominant_design"], q=tables["la_dd_q"])
    tables["la_class_configs"] = class_configs(v)
    tables["la_dimension_drift"] = dimension_drift(v)
    # parked 2026-09-22: placed in no node, so it was computed and written on every run but never printed.
    # Figure 4.2.4 builds its own matrix from transitions(v), so nothing depends on this line. To print the
    # table, un-comment it and add "la_transitions" to node 4.2.4 in la_index.NODES.
    # tables["la_transitions"] = transitions(v)
    tables["la_ip_strategy"] = ip_strategy(ds, v)
    tables["la_ip_by_class"] = ip_by_class(v)
    tables["la_cohorts"] = cohorts(v)
    tables["la_ari_timeline"] = ari_timeline(v)
    lq, counts = specialisation(v)
    t = lq.copy(); t.insert(0, "aircraft", counts.sum(axis=1))
    tables["la_specialisation"] = t.reset_index()
    tables["la_industry_by_class"] = industry_by_class(v)
    tables["la_examination_office"] = examination(v, "pub_office")
    tables["la_examination_class"] = examination(v, "topType")
    tables["la_powertrain_by_class"] = powertrain_by_class(v)
    tables["la_flags"] = flags()
    tables["la_filings_per_year"] = filings_per_year(ds, v)
    return tables
