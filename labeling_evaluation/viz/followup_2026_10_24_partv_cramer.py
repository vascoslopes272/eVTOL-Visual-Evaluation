"""Follow-up 2026-10-24 to NUMBERS_V (Analysis V.3, comment 74): Cramér's V of region against architecture, propulsor band, any tilting
propulsor, priority-year cohort and family F, with all assignees and without Bell / Textron. Reads the frames of viz.thesis_q3._frames(ctx)
and viz.thesis_q7._data(ctx) only; draws no figure. Writes LaTeX_v15/Data_for_writing/csv/q7_region_cramers_v.csv and appends the section
"Follow-up 2026-10-24, Cramér's V by region" to NUMBERS_V.md (once).

V as 3.4.1 defines it: V = sqrt(chi2 / (n * (min(r, k) - 1))), Pearson's chi2 (no continuity correction; region has 3 levels, so none applies).

    python -m viz.followup_2026_10_24_partv_cramer      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import numpy as np
import pandas as pd

from viz import frames, thesis_q3, thesis_q7
from viz.thesis_latex_common import root as latex_root

HEADING = "## Follow-up 2026-10-24, Cramér's V by region"
BELL = "Bell / Textron"
LAST = 2023
#: measure -> (column of the regional frame, name of the measure in q7_region_tests.csv or None)
MEASURES = {"architecture (five + other)": ("cls5", "class mix (five classes + other)"),
            "propulsor band (1-3, 4, 5-6, 7-8, 9+)": ("rb", "propulsive-unit band"),
            "any tilting propulsor (yes / no)": ("tilt", "any tilting unit"),
            "priority-year cohort (2012-15, 2016-19, 2020-23)": ("window", None),
            "family F (yes / no)": ("F", "family F")}


def cramers_v(frame: pd.DataFrame, a: str, b: str):
    """(V, chi2, df, p, n) of ``a`` against ``b`` on the rows where both are set; all-zero columns dropped, as ``chi2_p_of_columns``."""
    from scipy.stats import chi2_contingency
    f = frame.dropna(subset=[a, b])
    ct = pd.crosstab(f[a], f[b])
    ct = ct.loc[ct.sum(axis=1) > 0, ct.sum() > 0]
    chi2, p, dof, _ = chi2_contingency(ct, correction=False)
    n = int(ct.values.sum())
    return float(np.sqrt(chi2 / (n * (min(ct.shape) - 1)))), float(chi2), int(dof), float(p), n


def table(ctx) -> pd.DataFrame:
    w = thesis_q3._frames(ctx)["w"]
    assert w.index.equals(thesis_q7._data(ctx)["w"].index)
    ts = thesis_q7._data(ctx)["ts"]
    assert ts.attrs["left_out"] == BELL
    rows = []
    for base, s in ((f"all years to {LAST}", w[w["year"].le(LAST)]), ("V.3 test base (all years, 2024-26 included)", w)):
        for name, (col, tsname) in MEASURES.items():
            if col == "window":
                s_ = s[s["window"].isin(frames.CH5_WINS)]
                if base.startswith("V.3"):
                    continue
            else:
                s_ = s
            for who, sub in (("all assignees", s_), (f"without {BELL}", s_[s_["firm"].ne(BELL)])):
                v, chi2, dof, p, n = cramers_v(sub, "region3", col)
                if base.startswith("V.3"):
                    ref = ts[(ts["measure"] == tsname) & (ts["period"] == "all years")
                             & (ts["filers"] == ("all filers" if who == "all assignees" else who))].iloc[0]
                    assert ref["aircraft"] == n and abs(ref["p (chi-square, region)"] - round(p, 4)) < 1e-9, (name, who)
                rows.append({"base": base, "measure": name, "assignees": who, "n": n, "chi-square": round(chi2, 2), "df": dof,
                             "p": round(p, 3), "Cramér's V": round(v, 2), "_v": v})
    return pd.DataFrame(rows)


def _fmt(t: pd.DataFrame) -> pd.DataFrame:
    """V to 2 decimals and p to 3 as printed strings, so the trailing zeros stay (0.20, 0.120)."""
    return t.drop(columns="_v").assign(**{"p": t["p"].map("{:.3f}".format), "Cramér's V": t["Cramér's V"].map("{:.2f}".format),
                                          "chi-square": t["chi-square"].map("{:.2f}".format)})


def run(cfg, ctx):
    dfw = latex_root(cfg) / "Data_for_writing"
    t = table(ctx)
    _fmt(t).to_csv(dfw / "csv" / "q7_region_cramers_v.csv", index=False)

    nf = dfw / "NUMBERS_V.md"
    txt = nf.read_text(encoding="utf-8")
    if HEADING in txt:
        print("NUMBERS_V.md already holds", HEADING, "- not appended")
        return t
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_V.md"))
    main = t[t["base"].str.startswith("all years")]
    V = {(m.split(" (")[0], a): x for m, a, x in zip(main["measure"], main["assignees"], main["Cramér's V"])}
    alls, wo = "all assignees", f"without {BELL}"
    rank = lambda who: ", ".join(f"{m} {V[(m, who)]:.2f}" for m in sorted(  # noqa: E731
        ["architecture", "propulsor band", "any tilting propulsor", "priority-year cohort"], key=lambda m: -V[(m, who)]))
    L = [f"\n{HEADING}\n",
         "Source: `viz/followup_2026_10_24_partv_cramer.py` (frames of `viz.thesis_q3._frames(ctx)` and `viz.thesis_q7._data(ctx)`; no figure "
         "changed). CSV: `q7_region_cramers_v.csv`.\n",
         "Base: unique aircraft of North America, Europe and Asia-Pacific whose field is recorded. Cramér's V as in 3.4.1: "
         "V = sqrt(chi-square / (n x (smaller option count - 1))); region has 3 options, so the divisor is n x 1 for the yes / no measures "
         "and n x 2 for the others. Chi-square p of the same table. The cohort test counts only 2012-23 (aircraft before 2012 have no cohort).\n",
         f"### Main reading: priority years to {LAST}\n",
         _fmt(main).drop(columns="base").to_markdown(index=False, disable_numparse=True), "",
         f"Ranking of V, to {LAST}: all assignees: {rank(alls)}; {wo}: {rank(wo)}.\n",
         f"Reading: tilting has the largest V with all assignees ({V[('any tilting propulsor', alls)]:.2f}) and cohort the largest without "
         f"{BELL} ({V[('priority-year cohort', wo)]:.2f}). The claim is reversed for the propulsor band, which has the smallest V "
         f"({V[('propulsor band', alls)]:.2f}, p {main.iloc[2]['p']:.3f}, below architecture {V[('architecture', alls)]:.2f}). It holds for "
         f"the cohort, which is ahead of architecture by {V[('priority-year cohort', alls)] - V[('architecture', alls)]:.2f} with all "
         f"assignees (too close to rank) and by {V[('priority-year cohort', wo)] - V[('architecture', wo)]:.2f} without {BELL}.\n",
         "### Check: the base of the V.3 tests (`q7_region_tests.csv`, all years, 2024-26 included)\n",
         "The V.3 tests' \"all years\" counts the 2024-26 aircraft too; n and p below are asserted equal to `q7_region_tests.csv`.\n",
         _fmt(t[t["base"].str.startswith("V.3")]).drop(columns="base").to_markdown(index=False, disable_numparse=True), ""]
    nf.write_text(txt.rstrip("\n") + "\n" + "\n".join(L), encoding="utf-8")
    return t


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    ctx = thesis.context(cfg)
    print(_fmt(run(cfg, ctx)).to_string(index=False))
