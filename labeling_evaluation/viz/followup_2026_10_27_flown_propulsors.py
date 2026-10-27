"""Follow-up 2026-10-27 to NUMBERS_I (Analysis I.3, funnel tests of section 4.1): the propulsor count of the flown designs (TRL 5 or more,
the definition of ``viz.thesis_q4.representativeness``) against the other designs, Mann-Whitney U two-sided, and its Holm p inside the
funnel family (the six tests of ``viz.thesis_q4.funnel_family`` plus this one, one Holm correction over the seven raw p). Reads ctx only;
changes no figure, table or other number. Writes LaTeX_v15/Data_for_writing/csv/numbers_I_flown_propulsors_mw.csv and inserts the section
"I.3, propulsors of the flown designs (Mann-Whitney)" into NUMBERS_I.md after the funnel family (once). Run by notebook 48 after
``latex_v15.write_numbers_I``.

    python -m viz.followup_2026_10_27_flown_propulsors      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from lib.multiple import holm
from viz import frames, thesis_q4
from viz.thesis_latex_common import root as latex_root, tables_md

HEADING = "### I.3, propulsors of the flown designs (Mann-Whitney)"
AFTER = "## 4. Checks requested on 2026-10-12"            # the section is inserted just before this heading (the end of section 3)


def flown_propulsors(ctx) -> dict:
    """Median propulsor count of the flown designs and of the rest (designs with a count above zero; ``units`` of ctx.v, as in
    frames.representativeness), Mann-Whitney U two-sided, and the Holm p over the six funnel tests plus this one."""
    v = ctx.v
    wt = v.merge(frames.trl_frame(ctx.ds)[["aircraft_id", "trl"]], on="aircraft_id", how="left")
    flown = pd.to_numeric(wt["trl"], errors="coerce").fillna(2).ge(5)
    u = pd.to_numeric(wt["units"], errors="coerce")
    a, b = u[flown & u.gt(0)], u[~flown & u.gt(0)]
    r = mannwhitneyu(a, b, alternative="two-sided")
    fam = thesis_q4.funnel_family(ctx)
    p7 = holm(np.append(fam["p raw"].to_numpy(), r.pvalue))
    six_same = bool(np.allclose(p7[:-1], fam["p Holm"].to_numpy()))
    t = pd.DataFrame([{"group": "flown designs (TRL 5 or more)", "designs": int(flown.sum()), "with a propulsor count": len(a),
                       "median propulsors": float(a.median())},
                      {"group": "the other designs", "designs": int((~flown).sum()), "with a propulsor count": len(b),
                       "median propulsors": float(b.median())}])
    return {"table": t, "U": float(r.statistic), "p": float(r.pvalue), "p_holm": float(p7[-1]), "six_same": six_same,
            "fam7": fam[["key", "p raw"]].assign(**{"p Holm, seven tests": p7[:-1]})}


def run(cfg, ctx):
    dfw = latex_root(cfg) / "Data_for_writing"
    res = flown_propulsors(ctx)
    t = res["table"]
    t.assign(U=res["U"], p=res["p"], **{"p Holm (funnel family, seven tests)": res["p_holm"]}).to_csv(
        dfw / "csv" / "numbers_I_flown_propulsors_mw.csv", index=False)

    nf = dfw / "NUMBERS_I.md"
    txt = nf.read_text(encoding="utf-8")
    if HEADING in txt:
        print("NUMBERS_I.md already holds", HEADING, "- not inserted")
        return res
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_I.md"))
    pv = lambda p: f"{p:.1e}" if p < 0.001 else f"{p:.3f}"          # noqa: E731
    gap = t["median propulsors"].iloc[0] - t["median propulsors"].iloc[1]
    L = [f"{HEADING}\n",
         "Source: `viz/followup_2026_10_27_flown_propulsors.py` (follow-up 2026-10-27; no figure, table or other number changed). "
         "Flown = TRL 5 or more (`viz/thesis_q4.py:representativeness`); the rest = the other designs of the 627. Propulsor count = `units` "
         "of the analysis set, designs with a count above zero, as in `frames.representativeness`. Mann-Whitney U, two-sided "
         "(`scipy.stats.mannwhitneyu`; U of the flown designs). Holm: one correction over the six funnel tests above plus this one (seven raw p); "
         + ("the six Holm p above do not change with the seventh test. " if res["six_same"] else "NOTE: the six Holm p above change with the seventh test. ")
         + "CSV: `numbers_I_flown_propulsors_mw.csv`.\n",
         tables_md(t), "",
         f"- median difference: {gap:+.0f} propulsors (flown minus the rest)",
         f"- U = {res['U']:.0f}",
         f"- p = {pv(res['p'])} (raw {res['p']:.3e})",
         f"- p Holm (funnel family, seven tests) = {pv(res['p_holm'])} (raw {res['p_holm']:.3e})", "", ""]
    i = txt.index(AFTER)
    nf.write_text(txt[:i] + "\n".join(L) + txt[i:], encoding="utf-8")
    return res


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    r = run(cfg, thesis.context(cfg))
    print(r["table"].to_string(index=False), "\nU", r["U"], "p", r["p"], "p Holm", r["p_holm"])
