"""Follow-up 2026-10-23 to NUMBERS_V (Analysis V): universities by region (professor comment 66), North America's yearly counts, and the
adjusted residuals of the V.2 entrant / incumbent chi-squares. Reads the frames of viz.thesis_q2._frames(ctx) and viz.thesis_q3._frames(ctx)
only; draws no figure. Writes LaTeX_v15/Data_for_writing/csv/{q2_universities_by_region, q3_na_yearly, q2_entry_residuals}.csv and appends the
section "Follow-up 2026-10-23" to NUMBERS_V.md (once).

    python -m viz.followup_2026_10_23_partv      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import numpy as np
import pandas as pd

from lib import association as _assoc
from viz import thesis_q2, thesis_q3
from viz.thesis_latex_common import root as latex_root, tables_md

HEADING = "## Follow-up 2026-10-23"
UNI = "University / institute"
NA = "North America"
REG = ["North America", "Europe", "Asia-Pacific", "Other regions"]
COHORTS = ["2016-19", "2020-23", "2024-26 (partial)"]
CLS = {"SLC": "Separate Lift + Cruise", "TR": "Tilt Propulsor", "CVT": "Combined Vectored Thrust", "TW": "Tilt Wing", "MR": "Multicopter",
       "other": "other architectures"}


def universities_by_region(ctx):
    """Cohort x region of the university / institute aircraft: count, share of the cohort's university aircraft, share of the region's aircraft."""
    v = ctx.v
    rows = []
    for c in COHORTS:
        w = v[v["window"].eq(c)]
        u = w[w["filer"].eq(UNI)]
        for r in REG:
            n, nr = int(u["region3"].eq(r).sum()), int(w["region3"].eq(r).sum())
            rows.append({"cohort": c, "region": r, "university aircraft": n, "share of the cohort's university aircraft (%)": round(100 * n / len(u), 1),
                         "region's aircraft": nr, "universities' share of the region's aircraft (%)": round(100 * n / nr, 1) if nr else np.nan})
        rows.append({"cohort": c, "region": "all regions", "university aircraft": len(u), "share of the cohort's university aircraft (%)": 100.0,
                     "region's aircraft": len(w), "universities' share of the region's aircraft (%)": round(100 * len(u) / len(w), 1)})
    return pd.DataFrame(rows)


def top_universities(ctx):
    """University / institute assignees by aircraft in 2020-23 and 2024-26 together (assignee = ``firm``, the grouper's canonical name)."""
    v = ctx.v
    u = v[v["filer"].eq(UNI) & v["window"].isin(COHORTS[1:])]
    t = u.groupby("firm").agg(**{"aircraft 2020-26": ("aircraft_id", "size"), "2020-23": ("window", lambda s: int(s.eq("2020-23").sum())),
                                 "2024-26": ("window", lambda s: int(s.eq("2024-26 (partial)").sum())),
                                 "region": ("region3", lambda s: "/".join(sorted(set(s)))),
                                 "country": ("assignee_country", lambda s: "/".join(sorted(set(map(str, s))))) })
    return t.sort_values(["aircraft 2020-26", "2020-23"], ascending=False).rename_axis("assignee").reset_index()


def na_yearly(ctx):
    """North America per priority year 2016-23: count, share of all the year's aircraft, and the share of the three regions' aircraft raw and
    corrected for publication lag (``frames.region_years``, the frame behind na_share_2023_corr)."""
    v, ry = ctx.v, thesis_q3._frames(ctx)["ry"]
    ry = ry[ry["region"].eq(NA) & ry["priority year"].between(2016, 2023)].set_index("priority year")
    rows = []
    for y in range(2016, 2024):
        w = v[v["year"].eq(y)]
        rows.append({"priority year": y, "North America aircraft": int(ry.loc[y, "aircraft"]), "all aircraft": len(w),
                     "share of all aircraft (%)": round(100 * ry.loc[y, "aircraft"] / len(w), 1),
                     "aircraft of the three regions": int(w["region3"].isin(REG[:3]).sum()),
                     "share of the three regions, raw (%)": round(100 * ry.loc[y, "share of the year"], 1),
                     "visible at the snapshot": ry.loc[y, "visible at the snapshot"],
                     "share of the three regions, corrected for lag (%)": round(100 * ry.loc[y, "share corrected for publication lag"], 1)})
    out = pd.DataFrame(rows)
    assert out["North America aircraft"].tolist() == [int(w["region3"].eq(NA).sum()) for _, w in v[v["year"].between(2016, 2023)].groupby("year")]
    return out


def entry_residuals(ctx):
    """Adjusted residuals (``lib.association.adjusted_residuals``) of architecture x new / returning assignee, per cohort of the V.2 test."""
    from scipy.stats import chi2_contingency
    d = thesis_q2._frames(ctx)
    et = d["et"].set_index("window")
    ent = thesis_q2.frames.named_entries(ctx.v, ctx.WIN_NAMES)
    rows, tests = [], []
    for wn in ["2016-19", "2020-23"]:
        s = ent[ent["window"].eq(wn)]
        ct = pd.crosstab(s["_c"], s["first_time"]).reindex(list(CLS)).fillna(0).astype(int)
        ct = ct.loc[ct.sum(axis=1) > 0]
        chi2, p, dof, _ = chi2_contingency(ct)
        assert abs(p - et.loc[wn, "p"]) < 1e-12
        res = _assoc.adjusted_residuals(ct)
        j_new, j_ret = list(ct.columns).index(True), list(ct.columns).index(False)
        for i, c in enumerate(ct.index):
            rows.append({"cohort": wn, "architecture": CLS[c], "new assignees (entrants)": int(ct.iloc[i, j_new]),
                         "returning assignees (incumbents)": int(ct.iloc[i, j_ret]),
                         "adjusted residual, entrants": round(float(res[i, j_new]), 2), "adjusted residual, incumbents": round(float(res[i, j_ret]), 2)})
        tests.append({"cohort": wn, "chi-square": round(float(chi2), 2), "df": int(dof), "p": round(float(p), 3), "n": int(ct.values.sum())})
    return pd.DataFrame(rows), pd.DataFrame(tests)


def run(cfg, ctx):
    dfw = latex_root(cfg) / "Data_for_writing"
    ub, tu, ny = universities_by_region(ctx), top_universities(ctx), na_yearly(ctx)
    er, et = entry_residuals(ctx)
    tot = ub[ub["region"].eq("all regions")].set_index("cohort")["university aircraft"].to_dict()
    assert tot == {"2016-19": 4, "2020-23": 24, "2024-26 (partial)": 11}, tot
    ub.to_csv(dfw / "csv" / "q2_universities_by_region.csv", index=False)
    ny.to_csv(dfw / "csv" / "q3_na_yearly.csv", index=False)
    er.to_csv(dfw / "csv" / "q2_entry_residuals.csv", index=False)

    nf = dfw / "NUMBERS_V.md"
    txt = nf.read_text(encoding="utf-8")
    if HEADING in txt:
        print("NUMBERS_V.md already holds", HEADING, "- not appended")
        return ub, tu, ny, er, et
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_V.md"))
    n3 = tu[tu["aircraft 2020-26"].ge(2)]
    ny23 = ny.set_index("priority year")
    L = [f"\n{HEADING}\n",
         "Source: `viz/followup_2026_10_23_partv.py` (frames of `viz.thesis_q2._frames(ctx)` and `viz.thesis_q3._frames(ctx)`; no figure changed). "
         "Shares rounded to 1 decimal, p values to 3.\n",
         "### 1. University / institute assignees by region (professor comment 66)\n",
         "Totals checked against `q2_filer_types.csv`: 4 in 2016-19, 24 in 2020-23, 11 in 2024-26. CSV: `q2_universities_by_region.csv`.\n",
         tables_md(ub), "",
         "Largest university / institute assignees, 2020-23 and 2024-26 together (assignees with 2 aircraft or more). Two hold 3 aircraft and "
         f"seven hold 2, so a top five is not defined without a tie-break; all {len(n3)} are listed.\n",
         tables_md(n3), "",
         "### 2. North America per priority year, 2016-2023\n",
         "'Share of the three regions' is the share the text and `na_share_2023_corr` use (North America, Europe and Asia-Pacific; `frames.region_years`); "
         "the lag correction divides each region's count by the part of its aircraft the snapshot already sees. CSV: `q3_na_yearly.csv`.\n",
         tables_md(ny), "",
         f"Check of the text: share {ny23.loc[2021, 'share of the three regions, raw (%)']:.1f} % (2021) to "
         f"{ny23.loc[2023, 'share of the three regions, raw (%)']:.1f} % (2023), corrected "
         f"{ny23.loc[2023, 'share of the three regions, corrected for lag (%)']:.1f} % in 2023; count {ny23.loc[2021, 'North America aircraft']} (2021) "
         f"to {ny23.loc[2023, 'North America aircraft']} (2023). The text's 44 %, 22 % and 'from 32 to 10' are confirmed.\n",
         "### 3. V.2 adjusted residuals: architecture x new / returning assignees\n",
         "Named assignees' aircraft (companies and universities / institutes), per cohort; entrant = the assignee's first cohort in the corpus "
         "(`frames.named_entries`). Test = chi-square of `frames.entry_split_test`, p asserted equal. Adjusted residual after Haberman (1973), "
         "`lib.association.adjusted_residuals`; |r| > 1.96 marks a cell at about the 5 % level, cell by cell. CSV: `q2_entry_residuals.csv`.\n",
         tables_md(et), "", tables_md(er), "",
         "Check of the text (2020-23): Combined Vectored Thrust -3.22 and Multicopter +2.14 for the entrants are confirmed; no other cell passes 1.96. "
         "In 2016-19 the cells past 1.96 are Tilt Propulsor (-3.23 for the entrants, +3.23 for the incumbents) and Separate Lift + Cruise (+2.52 for the entrants).\n"]
    nf.write_text(txt.rstrip("\n") + "\n" + "\n".join(L), encoding="utf-8")
    return ub, tu, ny, er, et


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    ctx = thesis.context(cfg)
    for t in run(cfg, ctx):
        print(t.to_string(index=False), "\n")
