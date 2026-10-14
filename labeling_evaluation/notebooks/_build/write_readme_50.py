"""Write thesis_figures_v2/Part_II_design_space/README.md from viz/thesis_v2_part2.ITEMS, with the number checks
recomputed from the frames (nothing typed). Run standalone (python3 notebooks/_build/write_readme_50.py) or from
notebook 50, after the items are written.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PILLAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PILLAR))

from viz import config, frames, style, thesis
from viz import thesis_q6 as q6
from viz import thesis_q7 as q7
from viz import thesis_v2_part2 as v2

cfg = config.load()
ctx = thesis.context(cfg)
OUT = v2.out_root(cfg)
d6, d7 = q6._data(ctx), q7._data(ctx)

# ------------------------------------------------------------------------------------------ number checks, recomputed
b7 = d7["brief7"].set_index("level id")
est, z = d6["est"], d6["zones"]
a0, hit = d6["a0"], d6["hit"]
core, tail = d6["core"], ctx.cfg.analysis["discovery_tail"]
half_orig = {w: frames.half_column(z[w]) + 1 for w in ("2016-19", "2020-23")}


def half_ranked(w):
    c = np.sort(z[w].astype(float).to_numpy())[::-1]
    return int(np.searchsorted(np.cumsum(c) / c.sum(), 0.5)) + 1


half_rk = {w: half_ranked(w) for w in ("2016-19", "2020-23")}
last_wt = est.loc["A1t"]
n_conf = {k: int(b7.loc[i, "archetypes"]) for k, i in (("C", "A0"), ("C·W·T", "A1t"), ("C·U", "A0c"))}
d1 = {k: float(b7.loc[i, "effective number ¹D"]) for k, i in (("C", "A0"), ("C·W·T", "A1t"), ("C·U", "A0c"))}
since_12th = int(a0["aircraft"].max() - hit["aircraft"])

ok = lambda cond: "matches" if cond else "**DOES NOT MATCH**"      # noqa: E731
checks = [
    f"- configurations at C / C·W·T / C·U: **{n_conf['C']} / {n_conf['C·W·T']} / {n_conf['C·U']}** — thesis 12 / 39 / 43: "
    f"{ok((n_conf['C'], n_conf['C·W·T'], n_conf['C·U']) == (12, 39, 43))}",
    f"- ¹D at C / C·W·T / C·U: **{d1['C']:.1f} / {d1['C·W·T']:.1f} / {d1['C·U']:.1f}** — thesis 7.3 / 16.4 / 29.4: "
    f"{ok((round(d1['C'], 1), round(d1['C·W·T'], 1), round(d1['C·U'], 1)) == (7.3, 16.4, 29.4))}",
    f"- core: **{len(core)}** configurations holding **{100 * core['share 2016-23'].sum():.1f} %** of the 2016–23 designs — thesis 7 and 45 %: "
    f"{ok(len(core) == 7 and round(100 * core['share 2016-23'].sum()) == 45)}",
    f"- configurations that hold half of a cohort, **ranked by size within the cohort** (the new figure): 2016–19 **{half_rk['2016-19']}**, "
    f"2020–23 **{half_rk['2020-23']}**; read in the thesis's column order (the C·U configurations ranked by their size over all years, "
    f"as the original heatmap and `frames.half_column` do): 2016–19 **{half_orig['2016-19']}**, 2020–23 **{half_orig['2020-23']}** — thesis 10 and 7: "
    f"2016–19 {ok(half_orig['2016-19'] == 10)} in the thesis's ordering but "
    f"{'also ' if half_rk['2016-19'] == 10 else 'is '}**{half_rk['2016-19']}** when ranked within the cohort "
    f"({'no change' if half_rk['2016-19'] == 10 else 'the text and the figure differ by one'}); 2020–23 {ok(half_orig['2020-23'] == 7 and half_rk['2020-23'] == 7)} in both",
    f"- last {tail} designs at C·W·T: **{last_wt['new in the last 100 aircraft']:.1f} new** against **{last_wt['new in the last 100, random order']:.1f}** by chance — "
    f"thesis 4.1 vs 1.6: {ok((round(last_wt['new in the last 100 aircraft'], 1), round(last_wt['new in the last 100, random order'], 1)) == (4.1, 1.6))}",
    f"- Chao1 at C·W·T: **{last_wt['Chao1']:.1f}** — thesis 41.0: {ok(round(last_wt['Chao1'], 1) == 41.0)}",
    f"- no new architecture in the last **{since_12th}** designs (the 12th architecture appears at design {int(hit['aircraft'])} of {int(a0['aircraft'].max())}, "
    f"priority year {int(hit['priority year reached'])}) — thesis 362: {ok(since_12th == 362)}",
]

# ------------------------------------------------------------------------------------------ 2024–26 drawn: counts and changes
full = v2.curve_to_2026(ctx)
n_win, conf_n = d6["n_win"], {w: int(z[w].sum()) for w in ctx.WIN_NAMES}
cohort_rows = ["| cohort | designs (all) | designs in the 33 configurations of five or more | configurations that hold half |", "|---|---|---|---|"]
for w in ctx.WIN_NAMES:
    c = np.sort(z[w].astype(float).to_numpy())[::-1]
    k = int(np.searchsorted(np.cumsum(c) / c.sum(), 0.5)) + 1
    nm = "2024–26 (incomplete)" if "partial" in w else q6.WLAB[w].replace("-", "–")
    cohort_rows.append(f"| {nm} | {int(n_win[w])} | {conf_n[w]} | {k} |")
disc_rows = ["| level | designs, complete years | configurations seen | designs, to 2026 | configurations seen | new in 2024–26 |", "|---|---|---|---|---|---|"]
for lvl, nm in (("A0", "C"), ("A1t", "C·W·T"), ("A0c", "C·U")):
    g0, g1 = d6["curve"][d6["curve"]["level"] == lvl], full[full["level"] == lvl]
    s0, s1 = g0["archetypes (date order)"].iloc[-1], g1["archetypes (date order)"].iloc[-1]
    disc_rows.append(f"| {nm} | {len(g0)} | {s0:.0f} | {len(g1)} | {s1:.0f} | {s1 - s0:.0f} |")
changed = ["- **No number changes.** The checks below are the same before and after the 2024–26 pass.",
           "- `q6_half_of_cohort`: a fifth line, 2024–26 (incomplete), dashed and faded, hollow 50 % marker (half in 6). The four complete cohorts and their crossings are untouched.",
           "- `q6_discovery_curve`: runs to 2026. Every value up to 2023 is thesis_q6's own curve (not recomputed); the 2024–26 stretch continues it from the same "
           "functions run over all designs, shifted to join at the last complete year. The last-100 window and its numbers (4.1 vs 1.6 at C·W·T), Chao1 and "
           "the 362 designs without a new architecture stay on the complete years, and the panel label says \"to 2023\". The configurations seen at the end of the "
           "curve (table above) equal the all-years counts of the levels table (12 / 39 / 43), so nothing in the text moves.",
           "- `q6_configuration_core`: 2024–26 not drawn, to keep every number (see judgement calls).",
           "- Random-order curve: thin dashed grey line, no fill. `q6_propulsor_units_per_class`: no title. Lowest band named 0–3 everywhere."]
why40 = ["## Why the rarefaction size is 40 (and the 300 draws)\n",
         "**40 is a default with no stated reason.** It first appears as `n: int = 40` in `hill_numbers` / `hill_by_window` of `archive/.../dataset_facts/la_tables.py` "
         "(already there in the 2026-09-22 backups), was carried into `dominant_design` / `dd_balance` and then into `analysis.rarefy_n` of `labelling_analysis.yaml`, "
         "whose comment (\"a good number … a reasonable balance between statistical power and computational efficiency\") gives no cohort-size rule. "
         f"The cohorts it rarefies are {', '.join(f'{k} {int(v)}' for k, v in d7['bal'][d7['bal']['level'] == 'A0'].set_index('window')['aircraft'].items())} designs at C "
         f"(C·W·T: {', '.join(str(int(v)) for v in d7['bal'][d7['bal']['level'] == 'A1t']['aircraft'])}); 40 is under all of them, the smallest being 2024–26 (partial, 55 at C·W·T, which is not read) and 2012–15 (58) among the complete cohorts. "
         "The 300 is likewise a hard-coded `obs_draws=300` of `lib/dominant_design.balance_band` (the permutation draws are `perm_draws=40`, permutations 200); no rule fixed it either.\n",
         "If `rarefy_n` were set to the smallest cohort read (58, the 2012–15 cohort), every ²D in the figures and the verdicts that use it (condition 2) would be "
         "recomputed on larger samples, so their values would change a little, and the cohorts of 2012–15 would be read on all their designs. Nothing was changed.\n"]

lines = ["# Part II (Design space) figures, v2\n",
         "Relabelled, simplified and regrouped versions of a subset of the Q6 / Q7 thesis figures (`viz/thesis_v2_part2.py`). No number or "
         "computation is changed from `thesis_figures/`, a sibling folder this one never writes into; every builder reads its frame from "
         "`viz/thesis_q6.py` or `thesis_q7.py` unchanged and only re-draws, relabels or regroups it. Generated by "
         "`notebooks/50_thesis_figures_v2_part2.ipynb` (notebook 49 was already taken by the LLM-input review). Each figure is written as "
         ".pdf + .png + .csv + .json; each table as .csv + .json, as in Part I.\n",
         "## Terminology\n",
         "- **configuration** (never archetype); **design** (never *aircraft* as a count; \"designs\" on axes); **assignee** (never filer); "
         "**cohort** (never window); **architecture** (never class / architecture class)",
         "- **Multicopter** (never Multirotor; the data code stays MR); **Tilt Frame TF** (never Tilt Body TB); **Tilt Propulsor TP**; **SLC** is "
         "the code of Lift + Cruise",
         "- levels of description: **C**, **C·W·T**, **C·U** (C = architecture; C·W·T = architecture · number of wings · whether any propulsor "
         "tilts; C·U = architecture · propulsor-unit band 0–3 / 4 / 5–6 / 7–8 / 9+)",
         "- a C·U configuration is printed as architecture code + propulsor-unit band, e.g. `SLC 9+`, `TP 0–3`, `TF 4`\n",
         "## Style\n",
         "Part I v2 style; 6.3 in wide; smallest text 8 pt at print size; no in-plot text boxes; no label overlapping a mark or another label "
         "(checked on the rendered figures); a legend only for what is drawn; at most six colours, the rest grey.\n",
         "## Files\n"]
titles = {"II1_varying_attributes": "II1. Varying attributes", "II2_levels_of_description": "II2. Levels of description",
          "II3_distribution_and_new_variety": "II3. Distribution and new variety"}
for g, gt in titles.items():
    lines.append(f"### {gt}\n")
    for role in ("main", "auxiliary", "appendix"):
        its = [it for it in v2.ITEMS if it["group"] == g and it["role"] == role]
        if not its:
            continue
        lines.append(f"**{role}**")
        for it in its:
            lines.append(f"- `{it['name']}` ({it['kind']}) — {it['title']} *({it['source_item']})*")
        lines.append("")
lines += ["## Not copied\n",
          "- `q7_archetype_sets`' F row (Lift + Cruise + CVT* family) — moves to III.3, as asked",
          "- `q6_archetype_filers` — dropped, redundant with `q6_configuration_core`\n",
          "## Counts per cohort, 2024–26 included\n"] + cohort_rows + ["", "## Discovery curve, complete years against 2026\n"] + disc_rows + [
          "", "## What changes when 2024–26 is drawn\n"] + changed + [""] + why40 + ["## Number checks (no numbers changed; recomputed from the frames when this README is written)\n"] + checks + [""]
lines += [
    "## Judgement calls\n",
    "- **Notebook number**: the request said 49; `49_review_llm_inputs.ipynb` already exists, so this is notebook **50** (`build_50.py`, "
    "`write_readme_50.py`). Rename if 49 should be this one.",
    "- **Output folder**: `thesis_figures_v2/Part_II_design_space/`, beside `Part_I_evidence_base/` (read from \"Figures/\").",
    "- **File names** that the request did not rename keep the originals' words (`q6_propulsor_units_per_class`, `q6_arrangement_by_class`); "
    "the words *class* and *archetype* appear only in those file names, never in a label.",
    "- **Discovery curve, random-order band**: the frame holds the random-order expectation as ONE curve (analytic rarefaction, no spread), so "
    "a band is not available without a new computation. It is drawn as a thin dashed grey line, no fill; "
    "a true band would need the rarefaction variance. The \"spread inside a year\" band is dropped, as asked.",
    "- **Discovery curve, per-panel y axis**: the three levels end at 12, 37 and 42 configurations, so each panel has its own y scale "
    "(the curve covers the designs of complete years, 37 at C·W·T, 42 at C·U, against 39 and 43 in the all-years table). "
    "The first design of 2016 and of 2020 are design numbers 122 and 333 at every level.",
    "- **Core figure**: markers are one size and one shape (the original's bubble area = designs and triangle = first seen 2016 or later "
    "are dropped, since the legend is limited to architectures). The 3 labelled non-core configurations are the three with the largest "
    "2016–23 share outside the core (TP 9+, CVT 4, SLC 0–3). The median guide lines are dropped; the rim is the configurations at or "
    "under the median share.",
    "- **Core figure, 2024–26**: not added. The y axis (assignees per design) is computed on 2016–23 only, so a hollow 2024–26 marker would need "
    "either a new y or a different y on the same row; the 54 designs of 2024–26 also spread over 33 configurations (1–5 each). Left out.",
    "- **One name for the lowest propulsor-unit band: 0–3**, in every table and figure label (Table 6, the levels table, the core figure's point labels, "
    "the ducting ticks). The data's own bin is 0–3 (`frames.ROTOR_BINS`); `frames.UNIT_BANDS` prints 1–3 for display, which is why the figures and the levels "
    "table said 1–3. One design is recorded with 0 units and sits in this band.",
    "- **`q6_half_of_cohort`**: the denominator is the cohort's designs in the 33 C·U configurations of five or more designs (as the original "
    "heatmap); ranks 1–20 of 33 are drawn. All four complete cohorts are drawn, and 2024–26 (dashed, faded, hollow marker, labelled incomplete) (≤2011 and 2012–15 hold 61 and 57 designs there). The "
    "≤2011 and 2012–15 lines cross 50 % at the same rank (5), so their two markers sit on top of each other.",
    "- **`q6_propulsor_units_per_class`**: HB and PFV have no propulsor record and are left out and named once under the axis; x labels "
    "count the designs drawn.",
    "- **II1 tables and appendix**: the heatmap's HB and PFV columns stay (hatched = no record), as in the original.",
    "- **Fonts**: `plots.feature_heat` and `plots.duct_bands` printed 7.5 pt text, so the appendix figures use local copies at 8 pt "
    "(`_feature_heat`, `_duct_bands`), identical otherwise; the white boxes behind the duct diamond labels are removed.",
]
(OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", OUT / "README.md")
print("\n".join(checks))
