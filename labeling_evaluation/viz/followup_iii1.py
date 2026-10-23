"""Follow-up 2026-10-23 (supervisor comment 67): III.1 rerun without Bell / Textron.

Bell / Textron holds about a third of Tilt Propulsor in 2016-19, so the decrease of Tilt Propulsor into 2020-23 may partly be one
assignee's patenting cycle. Every frame and rule is III.1's (viz/analysis3.rho_table, frames.class_counts_by_window): cohort shares
over every design of the cohort; Spearman rho of each architecture's yearly share on the priority year, 2008-2023 and 2016-2023; the
same architectures and the same Holm family (one per span) as III.1. The assignee's designs leave numerator and denominator.
Spearman uses no random draw, so the seed (ctx.SEED) plays no part. No figure is touched.

Called by notebook 57; writes Data_for_writing/csv/q7_iii1_without_bell.csv and the section SECTION of Data_for_writing/NUMBERS_III.md
(notebook 52 rewrites NUMBERS_III.md, so run 57 after 52).
"""
from __future__ import annotations

import pandas as pd

from viz import analysis3, frames
from viz import thesis_v2_part2 as p2
from viz.thesis_latex_common import root

ASSIGNEE = "Bell / Textron"
SECTION = "## Follow-up 2026-10-23, III.1 without Bell / Textron"
NONE = "no architecture recorded"
#: the III.1 text quotes this, 2016-2023: the "all assignees" run must reproduce it
III1_TP_LATE = (-0.357, 0.39)


def tables_md(df: pd.DataFrame) -> str:
    """As viz.thesis_latex_common.tables_md, but the cells are printed as given (1.000 stays 1.000)."""
    return df.to_markdown(index=False, disable_numparse=True)


def _p3(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def _without(ctx) -> pd.DataFrame:
    return ctx.v[ctx.v["firm"].ne(ASSIGNEE)]


def assignee_designs(ctx) -> pd.DataFrame:
    """The assignee's designs per cohort (rows) and architecture (columns), with the total."""
    b = ctx.v[ctx.v["firm"].eq(ASSIGNEE)]
    t = pd.crosstab(b["window"], b["topType"].fillna(NONE)).reindex(ctx.WIN_NAMES).fillna(0).astype(int)
    t = t[[c for c in t.columns if t[c].sum()]]
    t.columns = [NONE if c == NONE else p2.arch(c).name for c in t.columns]
    t["all architectures"] = t.sum(axis=1)
    t.loc["all cohorts"] = t.sum()
    return t.rename_axis("cohort").reset_index()


def tp_shares(ctx, code: str = "TR") -> pd.DataFrame:
    """Tilt Propulsor's share of every design of the cohort, all assignees and without the assignee."""
    rows = []
    for who, v in (("all assignees", ctx.v), (f"without {ASSIGNEE}", _without(ctx))):
        cnt = frames.class_counts_by_window(v, ctx.WIN_NAMES)
        for w in ctx.WIN_NAMES:
            n, N = int(cnt.loc[w].get(code, 0)), int(cnt.loc[w].sum())
            rows.append({"assignees": who, "cohort": w, "Tilt Propulsor": n, "designs": N, "share %": round(100 * n / N, 1)})
    t = pd.DataFrame(rows)
    t["reading"] = [f"{r['Tilt Propulsor']} of {r['designs']} ({r['share %']:.1f} %)" for _, r in t.iterrows()]
    return t


def rho_both(ctx) -> pd.DataFrame:
    """III.1's Spearman table twice: all assignees (the III.1 table) and without the assignee, on III.1's architectures."""
    base = analysis3.rho_table(ctx)
    codes = list(base["code"])
    out = []
    for who, t in (("all assignees", base), (f"without {ASSIGNEE}", analysis3.rho_table(ctx, v=_without(ctx), codes=codes))):
        out.append(pd.DataFrame({"assignees": who, "architecture": [p2.arch(c).name for c in t["code"]], "designs 2008-2023": t["aircraft"],
                                 "rho 2008-2023": t["rho"], "p 2008-2023": t["p"], "p 2008-2023 (Holm)": t["p (Holm)"],
                                 "rho 2016-2023": t["rho, 2016-23"], "p 2016-2023": t["p, 2016-23"], "p 2016-2023 (Holm)": t["p, 2016-23 (Holm)"]}))
    t = pd.concat(out, ignore_index=True)
    tp = t[(t["assignees"] == "all assignees") & (t["architecture"] == p2.arch("TR").name)].iloc[0]
    assert (round(tp["rho 2016-2023"], 3), round(tp["p 2016-2023"], 2)) == III1_TP_LATE, "the all-assignees run does not reproduce III.1"
    for c in ("p 2008-2023", "p 2008-2023 (Holm)", "p 2016-2023", "p 2016-2023 (Holm)"):
        t[c] = t[c].astype(float).round(3)
    return t


def _fmt(t: pd.DataFrame) -> pd.DataFrame:
    t = t.copy()
    for c in [c for c in t.columns if c.startswith("p ")]:
        t[c] = t[c].map(_p3)
    for c in [c for c in t.columns if c.startswith("rho ")]:
        t[c] = t[c].map(lambda x: f"{x:.3f}")
    return t


def run(cfg, ctx) -> dict:
    a, s, r = assignee_designs(ctx), tp_shares(ctx), rho_both(ctx)
    tp = p2.arch("TR").name
    sh = s.set_index(["assignees", "cohort"])["share %"]
    wo = f"without {ASSIGNEE}"
    d_all = sh[("all assignees", "2020-23")] - sh[("all assignees", "2016-19")]
    d_wo = sh[(wo, "2020-23")] - sh[(wo, "2016-19")]
    held = r[r["assignees"] == wo]
    sig = {span: list(held.loc[held[f"p {span} (Holm)"] < 0.05, "architecture"]) for span in ("2008-2023", "2016-2023")}
    tp_wo = held[held["architecture"] == tp].iloc[0]
    bell_tp = int(a.loc[a["cohort"] == "2016-19", tp].iloc[0])
    tp_1619 = int(s[(s["assignees"] == "all assignees") & (s["cohort"] == "2016-19")]["Tilt Propulsor"].iloc[0])

    csv = pd.concat([a.assign(table="1 Bell / Textron designs per cohort and architecture"),
                     s.assign(table="2 Tilt Propulsor share per cohort"),
                     r.assign(table="3-4 Spearman rho of share on priority year")], ignore_index=True)
    csv = csv[["table"] + [c for c in csv.columns if c != "table"]]
    for c in list(a.columns[1:]) + ["Tilt Propulsor", "designs", "designs 2008-2023"]:     # counts stay whole numbers beside the blanks
        csv[c] = csv[c].astype("Int64")
    R = root(cfg) / "Data_for_writing"
    csv.to_csv(R / "csv" / "q7_iii1_without_bell.csv", index=False)

    pv = s.pivot(index="cohort", columns="assignees", values="reading").reindex(ctx.WIN_NAMES)[["all assignees", wo]].reset_index()
    sentence = (f"The decrease of Tilt Propulsor from the 2016-19 cohort to 2020-23 holds without {ASSIGNEE}: its share still goes down, by "
                f"{-d_wo:.1f} points ({sh[(wo, '2016-19')]:.1f} % to {sh[(wo, '2020-23')]:.1f} %; {-d_all:.1f} points with all assignees). "
                if d_wo < 0 else
                f"The decrease of Tilt Propulsor from the 2016-19 cohort to 2020-23 does not hold without {ASSIGNEE}: its share goes up by "
                f"{d_wo:.1f} points ({sh[(wo, '2016-19')]:.1f} % to {sh[(wo, '2020-23')]:.1f} %), against a decrease of {-d_all:.1f} points "
                f"with all assignees. ")
    sentence += (f"Its trend over 2008-2023 is {'still detected' if tp_wo['p 2008-2023 (Holm)'] < 0.05 else 'no longer detected'} "
                 f"(rho {tp_wo['rho 2008-2023']:.3f}, Holm p {_p3(tp_wo['p 2008-2023 (Holm)'])}) and over 2016-2023 "
                 f"{'detected' if tp_wo['p 2016-2023 (Holm)'] < 0.05 else 'not detected'} (rho {tp_wo['rho 2016-2023']:.3f}, "
                 f"Holm p {_p3(tp_wo['p 2016-2023 (Holm)'])}); ")
    other = {k: [x for x in v if x != tp] for k, v in sig.items()}
    sentence += ("no other architecture's trend is detected after the removal, over either span."
                 if not any(other.values()) else
                 "after the removal the other trends detected are: " + "; ".join(f"{k}: {', '.join(v) or 'none'}" for k, v in other.items()) + ".")

    L = [SECTION + "\n",
         f"Written by notebook 57 (`viz/followup_iii1.py`), supervisor comment 67. The III.1 frames and rules unchanged (`viz/analysis3.rho_table`, "
         f"`frames.class_counts_by_window`): cohort shares over every design of the cohort; Spearman rho of each architecture's yearly share on the "
         f"priority year over 2008-2023 (16 years) and 2016-2023 (8 years); the same {len(held)} architectures (20 designs or more, all assignees) and "
         f"the same Holm family per span as III.1. Every design whose assignee is {ASSIGNEE} leaves numerator and denominator. Spearman draws "
         f"nothing at random, so the seed plays no part. No figure is changed. Table: `csv/q7_iii1_without_bell.csv`.\n",
         f"### 1. {ASSIGNEE}'s designs per cohort and architecture\n",
         f"{int(a.iloc[-1]['all architectures'])} designs, {int(a.iloc[-1][tp])} of them Tilt Propulsor. In 2016-19, {bell_tp} of the cohort's "
         f"{tp_1619} Tilt Propulsor designs ({100 * bell_tp / tp_1619:.1f} %) are {ASSIGNEE}'s.\n", tables_md(a), "",
         "### 2. Tilt Propulsor share per cohort (share of every design of the cohort)\n", "2024-26 is a partial cohort and is not read.\n",
         tables_md(pv.rename(columns={"all assignees": "all assignees", wo: wo})), "",
         "### 3. Tilt Propulsor, Spearman rho of share on priority year\n",
         f"Check: the all-assignees row reproduces III.1 (2016-2023: rho {III1_TP_LATE[0]}, p {III1_TP_LATE[1]}).\n",
         tables_md(_fmt(r[r["architecture"] == tp].drop(columns="architecture"))), "",
         f"### 4. The other architectures, without {ASSIGNEE}\n",
         f"`designs 2008-2023` counts the designs left; Holm over the {len(held)} architectures of III.1 in each span. "
         + " ".join(f"{n} falls under 20 designs without {ASSIGNEE} ({k}); it stays in the family as in III.1."
                    for n, k in zip(held["architecture"], held["designs 2008-2023"]) if k < 20) + "\n",
         tables_md(_fmt(held[held["architecture"] != tp].drop(columns="assignees"))), "",
         "With all assignees, for comparison:\n",
         tables_md(_fmt(r[(r["assignees"] == "all assignees") & (r["architecture"] != tp)].drop(columns="assignees"))), "",
         "### 5. Answer\n", sentence, ""]
    md = R / "NUMBERS_III.md"
    text = md.read_text(encoding="utf-8")
    if SECTION in text:                                  # rerun: replace the section, which is always the last one
        text = text[:text.index(SECTION)].rstrip() + "\n"
    md.write_text(text.rstrip() + "\n\n" + "\n".join(L), encoding="utf-8")
    return {"designs": a, "shares": s, "rho": r, "sentence": sentence, "section": "\n".join(L)}
