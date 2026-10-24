"""Follow-up 2026-10-24 to NUMBERS_V (Analysis V.2): the 2020-23 table entrants x incumbents by architecture that the chi-square p 0.010 is
computed on, and the incumbents' Combined Vectored Thrust aircraft with the Bell / Textron part, 2016-19 and 2020-23. Reads the frames of
viz.thesis_q2._frames(ctx) only; draws no figure. Writes LaTeX_v15/Data_for_writing/csv/q2_entry_table_2020_23.csv and appends the section
"Follow-up 2026-10-24" to NUMBERS_V.md (once).

    python -m viz.followup_2026_10_24_partv      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import pandas as pd

from viz import thesis_q2
from viz.followup_2026_10_23_partv import CLS
from viz.thesis_latex_common import root as latex_root, tables_md

HEADING = "## Follow-up 2026-10-24"
BELL = "Bell / Textron"


def _cohort(ctx, wn):
    return thesis_q2.frames.named_entries(ctx.v, ctx.WIN_NAMES).pipe(lambda e: e[e["window"].eq(wn)])


def entry_table(ctx, wn="2020-23"):
    """Architecture x entrants / incumbents (aircraft of named assignees) for one cohort, with the incumbents' Bell / Textron part; the
    chi-square p of the table is asserted equal to the one of ``frames.entry_split_test``."""
    from scipy.stats import chi2_contingency
    s = _cohort(ctx, wn)
    ret = s[~s["first_time"]]
    rows = []
    for c in CLS:
        rows.append({"cohort": wn, "architecture": CLS[c], "entrants (aircraft)": int((s["first_time"] & s["_c"].eq(c)).sum()),
                     "incumbents (aircraft)": int(ret["_c"].eq(c).sum()),
                     f"of which {BELL}": int((ret["_c"].eq(c) & ret["firm"].eq(BELL)).sum())})
    t = pd.DataFrame(rows)
    t["all named assignees (aircraft)"] = t["entrants (aircraft)"] + t["incumbents (aircraft)"]
    ct = t.set_index("architecture")[["entrants (aircraft)", "incumbents (aircraft)"]]
    ct = ct.loc[ct.sum(axis=1) > 0]
    chi2, p, dof, _ = chi2_contingency(ct)
    et = thesis_q2._frames(ctx)["et"].set_index("window")
    assert abs(p - et.loc[wn, "p"]) < 1e-12
    tot = {"cohort": wn, "architecture": "all architectures", **{k: int(t[k].sum()) for k in t.columns[2:]}}
    t = pd.concat([t, pd.DataFrame([tot])], ignore_index=True)
    test = {"cohort": wn, "chi-square": round(float(chi2), 2), "df": int(dof), "p": round(float(p), 3), "n": int(ct.values.sum()),
            "entrant assignees": int(s.loc[s["first_time"], "firm"].nunique()), "incumbent assignees": int(ret["firm"].nunique())}
    return t, test


def cvt_incumbents(ctx):
    """Per cohort: the incumbents' Combined Vectored Thrust aircraft and how many are Bell / Textron's."""
    rows = []
    for wn in ["2016-19", "2020-23"]:
        ret = _cohort(ctx, wn).pipe(lambda s: s[~s["first_time"] & s["_c"].eq("CVT")])
        rows.append({"cohort": wn, "incumbents' Combined Vectored Thrust aircraft": len(ret), f"of which {BELL}": int(ret["firm"].eq(BELL).sum()),
                     "incumbent assignees holding them": int(ret["firm"].nunique())})
    return pd.DataFrame(rows)


def run(cfg, ctx):
    dfw = latex_root(cfg) / "Data_for_writing"
    t, test = entry_table(ctx)
    cv = cvt_incumbents(ctx)
    t.to_csv(dfw / "csv" / "q2_entry_table_2020_23.csv", index=False)

    nf = dfw / "NUMBERS_V.md"
    txt = nf.read_text(encoding="utf-8")
    if HEADING in txt:
        print("NUMBERS_V.md already holds", HEADING, "- not appended")
        return t, test, cv
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_V.md"))
    c = cv.set_index("cohort")
    L = [f"\n{HEADING}\n",
         "Source: `viz/followup_2026_10_24_partv.py` (frames of `viz.thesis_q2._frames(ctx)`, `frames.named_entries`; no figure changed).\n",
         "### V.2: entrants x incumbents by architecture, 2020-23\n",
         "Unit: aircraft of named assignees (companies and universities / institutes; individual inventors not counted). Entrant = an assignee "
         "whose first design falls in 2020-23; all its 2020-23 aircraft count as entrant aircraft. Incumbent = an assignee with a design in an "
         "earlier cohort. This is the table of the chi-square p 0.010 (`p_2023`), p asserted equal to `frames.entry_split_test`. "
         f"CSV: `q2_entry_table_2020_23.csv`.\n",
         tables_md(pd.DataFrame([test])), "", tables_md(t), "",
         "### Incumbents' Combined Vectored Thrust aircraft and the Bell / Textron part\n",
         tables_md(cv), "",
         f"Check of the text: in 2020-23 the incumbents hold {c.loc['2020-23', cv.columns[1]]} Combined Vectored Thrust aircraft (text: 21), "
         f"{c.loc['2020-23', cv.columns[2]]} of them Bell / Textron's (text: 11). In 2016-19: {c.loc['2016-19', cv.columns[1]]} and "
         f"{c.loc['2016-19', cv.columns[2]]}.\n"]
    nf.write_text(txt.rstrip("\n") + "\n" + "\n".join(L), encoding="utf-8")
    return t, test, cv


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    ctx = thesis.context(cfg)
    for x in run(cfg, ctx):
        print(x.to_string(index=False) if isinstance(x, pd.DataFrame) else x, "\n")
