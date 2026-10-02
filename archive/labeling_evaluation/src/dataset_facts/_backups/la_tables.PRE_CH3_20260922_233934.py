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

from . import a2, metrics
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
    v["archetype"] = np.where(v["topType"].notna() & v["rotorBin"].notna(),
                              v["topType"].astype(str) + " · " + v["rotorBin"].astype(str), None)
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
    """Rarefied Hill numbers per window at A0 (class) and A0c (class × propulsor bin)."""
    rows = []
    for level, col in (("A0 class", "topType"), ("A0c class × propulsor bin", "archetype")):
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
    "propulsor units": ("rotorBin", ["0-3", "4", "5-6", "7-8", "9+"]),
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
                     "median propulsor units": (float(sub["units"].median()) if "units" in sub and sub["units"].notna().any() else np.nan),
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
        for y in ("unique aircraft", "classes", "median propulsor units", "first priority year"):
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


def class_configs(v: pd.DataFrame, classes: Optional[List[str]] = None) -> pd.DataFrame:
    """Within-class convergence: for each big class and window, the share of the modal
    configuration (propulsor bin × ducted × booms × tail) and the number of configurations."""
    classes = classes or BIG4
    w = v.dropna(subset=["window", "topType"]).copy()
    w["ducted"] = w["any_ducted"].map({True: "ducted", False: "open"}).fillna("duct n/d")
    w["booms"] = np.where(w["nBooms"].fillna(0) > 0, "booms", "no booms")
    w["tail"] = w["empType"].fillna("tail n/d").astype(str)
    w["config"] = (w["rotorBin"].astype(str) + " units · " + w["ducted"] + " · " + w["booms"] + " · " + w["tail"])
    rows = []
    for c in classes:
        sub_c = w[w["topType"].eq(c) & w["rotorBin"].notna()]
        for name in WINDOW_NAMES:
            sub = sub_c[sub_c["window"].eq(name)]
            if len(sub) < 5:
                rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name, "aircraft": int(len(sub)),
                             "configurations": int(sub["config"].nunique()), "modal share": np.nan, "modal configuration": ""})
                continue
            vc = sub["config"].value_counts(normalize=True)
            rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name, "aircraft": int(len(sub)),
                         "configurations": int(vc.size), "modal share": round(float(vc.iloc[0]), 3),
                         "modal configuration": vc.index[0]})
    return pd.DataFrame(rows)


def dimension_drift(v: pd.DataFrame, classes: Optional[List[str]] = None) -> pd.DataFrame:
    """Per class and window: median propulsor units, ducted share, tilting share, boom share, median wings."""
    classes = classes or BIG4
    w = v.dropna(subset=["window", "topType"])
    rows = []
    for c in classes:
        for name in WINDOW_NAMES:
            sub = w[w["topType"].eq(c) & w["window"].eq(name)]
            if len(sub) < 5:
                continue
            rows.append({"class": metrics.ARCH_NAMES.get(c, c), "code": c, "window": name, "aircraft": int(len(sub)),
                         "median propulsor units": float(pd.to_numeric(sub["units"], errors="coerce").median()),
                         "ducted share": round(float(sub["any_ducted"].map({True: 1, False: 0}).mean()), 2),
                         "tilting share": round(float(sub["any_tilting"].map({True: 1, False: 0}).mean()), 2),
                         "boom share": round(float((sub["nBooms"].fillna(0) > 0).mean()), 2),
                         "median wings": float(pd.to_numeric(sub["wCount"], errors="coerce").median())})
    return pd.DataFrame(rows)


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
    return tab.reset_index()


def flags() -> pd.DataFrame:
    """Items the author of the build would cut for a 16-page version — the user decides."""
    rows = [
        ("Table 1.1b publication lag", "1.1", "a data-quality fact, already in the PA"),
        ("Table 1.2b aircraft per patent", "1.2", "one number (627 / 44) the funnel already gives"),
        ("Figure 1.3 evidence per aircraft", "1.3", "refinement detail; the table beside it carries the counts"),
        ("Figure 2.1c the four cards", "2", "repeats Figure 2.1b"),
        ("Table 3.1 missingness", "3.1", "the figure shows the same shares"),
        ("Table 3.3 flagship", "3.3", "the figure shows the same matches"),
        ("Table 3.5 field inventory", "3.5", "the figure shows the same ranking"),
        ("Figure 4.1.2b one vote per filer", "4.1.2", "robustness check; the lines barely part"),
        ("Figure 4.1.2c two counts", "4.1.2", "robustness check; no share moves more than 0.03"),
        ("4.1.7 lead and lag, figure and tables", "4.1.7", "timing question rated less important"),
        ("Table 4.1.8 Hill numbers", "4.1.8", "the figure shows the same values"),
        ("Table 4.1.9 zones", "4.1.9", "20 rows; the figure carries it"),
        ("Figure 4.2.5b re-filing spans", "4.2.5", "its one useful number is in the IP figure"),
        ("Table 4.2.6a firm proximity", "4.2.6", "17 rows; the heatmap carries it"),
        ("4.3.4 country × class, figure and table", "4.3.4", "the specialisation index (4.3.3) answers it at archetype level"),
        ("5.4 image-level answers", "5.4", "T2 detail; keep only if the image chapter needs it here"),
        ("Tables 5.5b–g mission crosstabs", "5.5", "six small tables the mission figure already shows"),
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
        ("planned figure b", "TRL band against class mix, propulsor units and number of classes per firm"),
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
    tables["la_firm_tiers"] = firm_tiers(v)
    tables["la_filers_by_window"] = filers_by_window(v)
    tables["la_firm_windows"] = firm_windows(v)
    _, tables["la_proximity_region"] = proximity_by_region(ds, v)
    firms = ari_firms(v)
    tables["la_ari_firms"] = firms
    tables["la_ari_correlation"] = ari_correlation(firms, v)
    tables["la_class_fold"] = class_fold_table(v)
    linked = linked_aircraft(v)
    tables["la_linked_aircraft"] = linked
    for k, t in mission_tables(linked).items():
        tables[f"la_mission_{k}"] = t
    tables["la_relabel_protocol"] = relabel_protocol()
    tables["la_trl_placeholder"] = trl_placeholder()
    tables["la_dominant_design"] = dominant_design(v)
    tables["la_class_configs"] = class_configs(v)
    tables["la_dimension_drift"] = dimension_drift(v)
    tables["la_transitions"] = transitions(v)
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
