"""Supervisor review 2 (2026-10): the threshold-sensitivity runs of step 3 and the register of the Holm-adjusted families of step 2.
Called by notebook 56; nothing here changes a figure or a number of the main reading. Every table is written beside the table it
varies (LaTeX_v15/Data_for_writing/csv/ and the thesis_figures_v2 folder of the main table).

    3a  fixed_share_tables      q6_fixed_by_architecture at a leading-option share of 70 % and 90 % (80 % is the main table)
    3b  rarefied_hill_table     Hill numbers per cohort and level rarefied to 30, 40 and 50 designs, with the condition-2 band
    3c  acceptance_table        which script inputs a 60 / 70 / 80 / 90 % acceptance threshold accepts
    2   holm_register           every test of the four Holm families: raw p, Holm p, the verdict at 0.05 before and after
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import diversity, intervals
from viz import frames, style, thesis_q7 as q7
from viz.thesis_latex_common import root

ALPHA = 0.05
SHARES = (0.70, 0.90)
RAREFY = (30, 40, 50)
ACCEPT = (0.60, 0.70, 0.80, 0.90)
REVIEW = Path(__file__).resolve().parents[1] / "review"
#: the levels as the dissertation names them (as viz/analysis3._LVL)
LEVEL = {"A0": "A", "A1t": "A·W·T", "A0c": "A·U", "family_b": "F"}


def csv_dir(cfg) -> Path:
    p = root(cfg) / "Data_for_writing" / "csv"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------------------------------------------- 3a
def fixed_share_tables(ctx, shares=SHARES, min_designs: int = None) -> dict:
    """The printed q6_fixed_by_architecture tables (summary, detail) with the leading-option share rule at each of ``shares`` and an
    architecture read from ``min_designs`` answering designs (thesis_q6.FIXED_MIN_DESIGNS, 10, unless given). The Cramér's V and its p
    depend on neither (same shuffles, same seed); only the 'architectures at x % or more' column moves."""
    from viz import thesis_v2_part2 as p2
    return {s: p2._fixed_tables(ctx, share=s, min_designs=min_designs) for s in shares}


#: the readability minimum of the dissertation's 80 % table (2026-10-22): an architecture is read from 20 answering designs
MIN_READ_THESIS = 20


def readable_architectures(ctx) -> pd.DataFrame:
    """Per dimension of q6_fixed_by_architecture: the architectures read at 10 answering designs (the code's rule) and at 20 (the
    dissertation's), each with its answering designs."""
    from viz import thesis_q6 as q6
    _, d = q6.fixed_by_architecture(ctx)
    rows = []
    for dim, g in d.groupby("dimension", sort=False):
        name = lambda r: f"{arch_name(r['code'])} ({int(r['designs'])})"                                       # noqa: E731
        for mn in (q6.FIXED_MIN_DESIGNS, MIN_READ_THESIS):
            r = g[g["designs"] >= mn]
            rows.append({"dimension": dim.replace("aircraft", "design"), "read from (designs)": mn, "architectures read": len(r),
                         "which (answering designs)": ", ".join(name(x) for _, x in r.iterrows())})
    return pd.DataFrame(rows)


def arch_name(code: str) -> str:
    from viz.thesis_v2_part2 import arch
    return arch(code).name


def edge_cell(ctx, level: str = "A·W·T", cohort: str = "2020-23", h: pd.DataFrame = None) -> pd.DataFrame:
    """One condition-2 cell at each rarefaction size: observed ²D (with the middle 95 % of its rarefaction draws), the permutation band and
    the distance of ²D to the lower edge (negative = below the band, condition met)."""
    h = rarefied_hill_table(ctx) if h is None else h
    c = h[(h["level"] == level) & (h["cohort"] == cohort)]
    out = c[["rarefied to n", "designs", "²D (condition 2, 1000 permutations)", "²D low", "²D high", "band low", "band high",
             "below band (condition 2 met)"]].copy()
    out.insert(0, "cell", f"{level}, {cohort}, all designs")
    out["²D minus band low"] = (out["²D (condition 2, 1000 permutations)"] - out["band low"]).round(2)
    out["as a share of the band width"] = (out["²D minus band low"] / (out["band high"] - out["band low"])).round(3)
    return out.reset_index(drop=True)


# ---------------------------------------------------------------------------------------------------- 3b
def rarefied_hill_table(ctx, ns=RAREFY) -> pd.DataFrame:
    """Per rarefaction size n, level (A, A·W·T, A·U, F) and cohort: the rarefied Hill numbers ⁰D, ¹D, ²D (lib.diversity.hill_numbers,
    1000 draws, seed 42) and the condition-2 reading at that n (frames.dd_balance_table: ²D against its permutation band, thesis_q7.PERMS
    permutations, the generators of the main reading)."""
    v = ctx.v
    w0 = v.dropna(subset=["window"])
    keys = frames.dd_level_keys(ctx.ds, v)
    rows = []
    for n in ns:
        bal = frames.dd_balance_table(ctx.ds, v, ctx.WIN_NAMES, n, q7.PERMS, ctx.SEED).set_index(["level", "window"])
        for level in frames.DD_LEVELS:
            k = keys[level].loc[w0.index]
            ww = w0[k.notna()].assign(key=k[k.notna()])
            for win in ctx.WIN_NAMES:
                sub = ww[ww["window"].eq(win)]
                if len(sub) < 10:
                    continue
                h = diversity.hill_numbers(sub["key"], n=n)
                b = bal.loc[(level, win)] if (level, win) in bal.index else None
                rows.append({"rarefied to n": n, "level": LEVEL[level], "cohort": win, "designs": int(len(sub)),
                             "sample": h["sample"], "⁰D": h["D0"], "¹D": h["D1"], "²D": h["D2"], "²D low": h["D2 low"], "²D high": h["D2 high"],
                             "²D (condition 2, 1000 permutations)": b["D2"] if b is not None else np.nan,
                             "band low": b["D2 permutation low"] if b is not None else np.nan,
                             "band high": b["D2 permutation high"] if b is not None else np.nan,
                             "below band (condition 2 met)": bool(b["below band"]) if b is not None else np.nan,
                             "partial cohort (not read)": "partial" in win})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------- 3c
#: (input, method, the population N of the Wilson finite-population correction; None = census) as review/decisions/ACCURACY_TABLE.csv
_POP = {"Development year": 1229, "TRL": 105}


def acceptance_table(thresholds=ACCEPT) -> pd.DataFrame:
    """Which rows of review/decisions/ACCURACY_TABLE.csv (notebook 60) a threshold accepts, read two ways: the point share at or above the
    threshold, and the lower bound of the 95 % Wilson interval (finite-population corrected, the rule of
    review/HOW_THE_REVIEWS_WERE_DONE.md, default 90 %) at or above it. Development year and TRL rows only (the script inputs the brief names)."""
    acc = pd.read_csv(REVIEW / "decisions" / "ACCURACY_TABLE.csv", keep_default_na=False)
    acc = acc[acc["input"].isin(_POP)].copy()
    rows = []
    for _, r in acc.iterrows():
        k, n, N = int(r["agree"]), int(r["of"]), _POP[r["input"]]
        lo, hi = intervals.wilson_fpc_interval(k, n, N)
        row = {"input": r["input"], "method": r["method"], "agree": k, "of": n, "share %": round(100 * k / n, 1),
               "95 % low %": round(100 * lo, 1), "95 % high %": round(100 * hi, 1)}
        for t in thresholds:
            row[f"accepted at {t:.0%}, share"] = k / n >= t
            row[f"accepted at {t:.0%}, lower bound"] = lo >= t
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------- Section 4.2.3 (2026-10-22)
def funnel_populations(ctx) -> dict:
    """The populations of the funnel of Section 4.2.3, each as a boolean mask over ctx.v (one row per design):
    all designs; the named designs (a public counterpart, thesis_q4.public_frame: the 97 of Table 2); flown (TRL 5 or more,
    frames.trl_frame, as thesis_q4.representativeness); the designs of the AAM Reality Index assignees that have flown by the release
    (first flight on or before ARI_RELEASE_YEAR - 1, as the flown index-assignee group of thesis_q4); the designs of every index assignee
    that files here (frames.ari_timeline, the firms of the patent-vs-market clock)."""
    from viz import thesis_q4 as q4
    v = ctx.v
    named = set(q4.public_frame(ctx)["aircraft_id"])
    trl = v["aircraft_id"].map(frames.trl_frame(ctx.ds).set_index("aircraft_id")["trl"])
    tl = q4.ari_timeline(ctx)
    ff = pd.to_numeric(tl["first flight (ARI)"], errors="coerce")
    flown_firms = set(tl.loc[ff.notna() & ff.le(frames.ARI_RELEASE_YEAR - 1), "company"])
    all_firms = set(tl["company"])
    return {"all designs": pd.Series(True, index=v.index),
            "named designs (public counterpart, Table 2)": v["aircraft_id"].isin(named),
            "flown designs (TRL 5 or more)": pd.to_numeric(trl, errors="coerce").fillna(2).ge(5),
            f"designs of the {len(flown_firms)} index assignees that have flown": v["company_canonical"].isin(flown_firms),
            f"designs of the {len(all_firms)} index assignees": v["company_canonical"].isin(all_firms)}


def funnel_steps(ctx) -> pd.DataFrame:
    """q4_funnel_steps: one row per population of :func:`funnel_populations`: designs; the share of each architecture (over the designs
    with an architecture recorded) and the largest; the median number of propulsors (frames.propulsor_units, designs with a count;
    a blank is never 0); the share with priority year 2020-2023 (over the designs with a priority year)."""
    from viz.thesis_v2_part2 import arch
    v = ctx.v
    units = frames.propulsor_units(v)["units"]
    codes = [c for c in style.CLASS_ORDER if c in set(v["topType"].dropna())]
    rows = []
    for name, m in funnel_populations(ctx).items():
        sub = v[m.to_numpy()]
        a = sub["topType"].dropna()
        share = a.value_counts(normalize=True).reindex(codes, fill_value=0.0)
        u = units[m.to_numpy()].dropna()
        y = pd.to_numeric(sub["year"], errors="coerce").dropna()
        row = {"population": name, "designs": int(len(sub)), "designs with an architecture": int(len(a)),
               "largest architecture": arch(share.idxmax()).name, "its share": round(float(share.max()), 3),
               "median propulsors per design": float(u.median()), "designs with a propulsor count": int(len(u)),
               "share with priority year 2020-2023": round(float(y.between(2020, 2023).mean()), 3), "designs with a priority year": int(len(y))}
        for c in codes:
            row[f"share {arch(c).name}"] = round(float(share[c]), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def publication_lead(ctx) -> pd.DataFrame:
    """Patent-to-flight lead of each AAM Reality Index assignee that files here, from its first PRIORITY year (frames.ari_timeline, as the
    clock figure) and from its first PUBLICATION year (the earliest pub_year of its designs' patents, frames.with_publication). Years only,
    as the index prints them."""
    from viz import thesis_q4 as q4
    tl = q4.ari_timeline(ctx).copy()
    pub = frames.with_publication(ctx.ds, ctx.v).groupby("company_canonical")["pub_year"].min()
    tl["first publication"] = tl["company"].map(pub).astype("Int64")
    ff = pd.to_numeric(tl["first flight (ARI)"], errors="coerce")
    tl["flown by the release"] = ff.notna() & ff.le(frames.ARI_RELEASE_YEAR - 1)
    tl["lead from first priority (years)"] = ff - tl["first patent"]
    tl["lead from first publication (years)"] = ff - tl["first publication"].astype(float)
    return tl[["company", "first patent", "first publication", "first flight (ARI)", "flown by the release",
               "lead from first priority (years)", "lead from first publication (years)"]].rename(columns={"first patent": "first priority"})


def publication_lead_summary(ctx) -> pd.DataFrame:
    """Median and range of both leads, over the assignees that have flown by the release and over every assignee with a first-flight year."""
    t = publication_lead(ctx)
    rows = []
    for name, m in (("index assignees that have flown by the release", t["flown by the release"]),
                    ("every index assignee with a first-flight year (a planned year included)", t["first flight (ARI)"].notna())):
        g = t[m]
        pr, pu = g["lead from first priority (years)"], g["lead from first publication (years)"]
        rows.append({"assignees": name, "n": int(len(g)), "median lead from priority": float(pr.median()),
                     "range from priority": f"{int(pr.min())} to {int(pr.max())}", "median lead from publication": float(pu.median()),
                     "range from publication": f"{int(pu.min())} to {int(pu.max())}",
                     "difference of the medians (publication - priority)": float(pu.median() - pr.median())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------- 2
def holm_register(ctx) -> pd.DataFrame:
    """Every test of the four Holm families in one frame: family, test, raw p, Holm p, significant at 0.05 before / after, changed."""
    from viz import analysis3, thesis_q4 as q4, thesis_q6 as q6
    parts = []

    def add(family, test, p, ph):
        parts.append(pd.DataFrame({"family": family, "test": list(test), "p": list(p), "p (Holm)": list(ph)}))

    s, _ = q6.fixed_by_architecture(ctx)
    add("II.1 dimension × architecture (Cramér's V, permutation p)", s["dimension"], s["p"], s["p (Holm)"])
    r = analysis3.rho_table(ctx)
    for col in ("p", "p, 2016-23"):
        span = "2008-2023" if col == "p" else "2016-2023"
        add(f"III.1 share × priority year, Spearman, {span}", r["code"], r[col], r[f"{col} (Holm)"])
    d = q4.directory_mix(ctx)
    add("I.2 dataset against the in-domain directory and its parts (chi-square)", d["p_raw"].index, d["p_raw"], d["p_holm"])
    t = q7._data(ctx)["ts"]
    for who, g in t.groupby("filers", sort=False):
        add(f"V region × measure (chi-square), {who}", g["measure"] + " · " + g["period"], g["p (chi-square, region)"], g["p (Holm)"])
    m = q7._data(ctx)["mc"].dropna(subset=["p"])
    add("V trend of a regional answer 2012-2023 (Spearman)", m["region"] + " · " + m["variable"] + " · " + m["label"].astype(str), m["p"], m["p (Holm)"])
    out = pd.concat(parts, ignore_index=True)
    out["below 0.05, raw"] = out["p"] < ALPHA
    out["below 0.05, Holm"] = out["p (Holm)"] < ALPHA
    out["verdict changes"] = out["below 0.05, raw"] != out["below 0.05, Holm"]
    return out


def write_all(cfg, ctx) -> list:
    """Write every table of this module; returns the paths written."""
    from viz import thesis_v2_part2 as p2
    D = csv_dir(cfg)
    out = []
    v2dir = p2.out_root(cfg) / "II1_varying_attributes" / "appendix"
    for s, (t1, t2) in fixed_share_tables(ctx).items():
        tag = f"share{int(round(100 * s))}"
        for d in (D, v2dir):
            t1.to_csv(d / f"q6_fixed_by_architecture_{tag}.csv", index=False)
            t2.to_csv(d / f"q6_fixed_by_architecture_detail_{tag}.csv", index=False)
            out += [d / f"q6_fixed_by_architecture_{tag}.csv", d / f"q6_fixed_by_architecture_detail_{tag}.csv"]
    # 2026-10-22: the three shares again with an architecture read from 20 designs (the dissertation's 80 % table), so the trio compares
    for s, (t1, t2) in fixed_share_tables(ctx, (0.70, 0.80, 0.90), min_designs=MIN_READ_THESIS).items():
        tag = f"min{MIN_READ_THESIS}_share{int(round(100 * s))}"
        for d in (D, v2dir):
            t1.to_csv(d / f"q6_fixed_by_architecture_{tag}.csv", index=False)
            t2.to_csv(d / f"q6_fixed_by_architecture_detail_{tag}.csv", index=False)
            out += [d / f"q6_fixed_by_architecture_{tag}.csv", d / f"q6_fixed_by_architecture_detail_{tag}.csv"]
    ra = readable_architectures(ctx)
    ra.to_csv(D / "q6_fixed_by_architecture_readable.csv", index=False)
    out.append(D / "q6_fixed_by_architecture_readable.csv")
    h = rarefied_hill_table(ctx)
    for n, g in h.groupby("rarefied to n"):
        g.to_csv(D / f"q7_hill_by_cohort_rarefied{n}.csv", index=False)
        out.append(D / f"q7_hill_by_cohort_rarefied{n}.csv")
    e = edge_cell(ctx, h=h)
    e.to_csv(D / "q7_condition2_awt_2020_23_by_rarefaction.csv", index=False)
    out.append(D / "q7_condition2_awt_2020_23_by_rarefaction.csv")
    a = acceptance_table()
    for p in (D / "script_acceptance_thresholds.csv", REVIEW / "decisions" / "ACCURACY_THRESHOLD_SENSITIVITY.csv"):
        a.to_csv(p, index=False)
        out.append(p)
    from viz import thesis_v2_part1 as v1
    for name, t in (("q4_coding_agreement", v1.tab_coding_agreement_v2(ctx)[0]), ("q4_funnel_steps", funnel_steps(ctx)), ("q4_publication_lead", publication_lead(ctx)),
                    ("q4_publication_lead_summary", publication_lead_summary(ctx))):
        t.to_csv(D / f"{name}.csv", index=False)
        out.append(D / f"{name}.csv")
    hr = holm_register(ctx)
    hr.to_csv(D / "holm_register.csv", index=False)
    out.append(D / "holm_register.csv")
    return out
