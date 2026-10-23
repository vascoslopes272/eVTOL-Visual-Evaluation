# Rerun notes, supervisor's second review (October 2026)

Every seed stays at 42. Each step was rerun with notebooks 48 → 50 → 52 → 51 → 53 → 54 → 55, in that order, before the next step began.
Old values come from a rerun of the unchanged code (HEAD 3cc1252, 2026-10-21). That rerun matched the outputs already on disk except
for one label rename (Lift + Cruise → Separate Lift + Cruise in `q2_largest_filer_per_class.csv`), so every difference below comes from the step it is listed under.
Outputs live in `…/labelling_analysis_thesis/LaTeX_v15/` and `thesis_figures_v2/`. The copies made before this work are in
`_BACKUPS/PRE_SUPREV2_*_20261021`.

## Step 1. Resampling counts set to 1000

What changed in the code:

| count | where | old → new |
|---|---|---|
| permutations behind the cohort bands of conditions 2 and 3 (and the form families of notebook 55) | `viz/thesis_q7.py: PERMS` | 200 → 1000 |
| defaults of `balance_band` and `cohesion_band` | `lib/dominant_design.py` | perms 200 → 1000 |
| rarefaction draws of the observed ²D | `lib/dominant_design.py: balance_band(obs_draws)` | 300 → 1000 |
| permutations of the centroid / dispersion band (Part IV) | `viz/thesis_v2_part4.py: dispersion` | 200 → 1000 |
| permutations of the CVT / Lift + Cruise distance (Part IV) | `viz/thesis_v2_part4_iv2.py: cvt_lc_distance` | 200 → 1000 |
| tie orderings of the discovery curve | `lib/diversity.py: ORDERS`, `labelling_analysis.yaml: discovery_orders` | 400 → 1000 |

Corrections to the brief:
- `viz/thesis_v2_part2.py`, around line 150, holds no rarefaction count. The 300 there (line 217, `for trial in range(300)`) and the 200 in `ts_spread` (line 66) are retry loops of the label placement, and so is the `range(300)` in `thesis_latex_part4.py:892`. They resample nothing and were left alone. The rarefaction 300 was `obs_draws` in `lib/dominant_design.py`.
- Left alone, because they are not 200/300/400: `perm_draws = 40` (the rarefaction draws inside each permutation of condition 2), the bootstrap counts of `lib/growth.py` (2000) and `lib/regional.py` (2000, 5000), and `lib/association.py` (as asked).
- The printed descriptions that named the old counts now say 1000 (`thesis_latex_part3.py`, `thesis_latex_part4.py`, `thesis_q7.py` units, `thesis_form_families.py`, notebook 51 header). The premise band of notebook 55 (random subsets of the cohort) also runs `PERMS` times, so it went from 200 to 1000 as well; its text line ("200 random subsets") was corrected after the step-1 run and reads right from step 2 on.

### Verdicts that change (main reading untouched)

| table | cell | old → new |
|---|---|---|
| `q7_verdict_table.csv`, condition 2, base **actively protected**, level A | ≤ 2011 cohort, 18 designs: ²D 3.00 against a band lower edge of 2.89 → 3.06 | "✓ met in 2020-23" → "✓ met in ≤ 2011, 2020-23" |
| `q8_families_verdict.csv` (notebook 55, exploratory), P4, actively protected, condition 2 | ≤ 2011 | "✓ met in 2020-23" → "✓ met in ≤ 2011, 2020-23" |
| `q8_families_premise.csv` / verdict, P5, all designs | 2012-15 cohesion below band: False → True | premise "holds in ≤ 2011, 2016-19, 2020-23" → "holds in ≤ 2011, 2012-15, 2016-19, 2020-23" |

No conclusion changes. All designs, the main reading, is unchanged at every level. The cell that moves is in the earliest cohort of
the sensitivity base, has 18 designs, and sits on the edge of its band (3.00 against 3.06). It says nothing about convergence in 2020-23. Its two neighbours at A·W·T and A·U were already below the band.
No discovery verdict ("filling up" / "slowing, not closed" / "still opening") changes.

### Numbers that move (rounded as printed)

- **Condition 2, ²D rarefied to 40, all designs** (`q7_condition2_balance.csv`; the values move by at most 0.05, the band edges by up to 0.4):
  - A, 2020-23: ²D 4.53 → 4.55, band 4.74–5.80 → 4.73–5.79, still below.
  - A·W·T, 2020-23: ²D 8.34 → 8.36, band 8.24–10.34 → 8.30–10.37.
  - A·U, 2020-23: ²D 14.46 → 14.49, band low 13.93 → 13.85.
  - A·W·T 2012-15: band high 12.31 → 11.91. A·U ≤ 2011: band 12.39–18.48 → 12.15–18.53.
- **F (III.4 directory categories, `q7_iii4_directory_categories.csv`), all designs:** 2020-23 ²D 2.16 → 2.18, band 2.09–2.52 → 2.09–2.53. ≤ 2011 band 1.87–2.91 → 1.86–2.83. 2012-15 band 1.85–2.84 → 1.84–2.82.
- **F, granted and live** (`q7_granted_live_condition2.csv`): 2020-23 ²D 3.03 → 2.98, band 3.55–4.64 → 3.53–4.65.
- **Condition 3, ΔQ band (w15)** (`q7_condition3_cohesion.csv`; ΔQ itself does not move): A 2020-23 −0.0190 to 0.0390 → −0.0196 to 0.0351, A 2016-19 −0.0168 to 0.0407 → −0.0205 to 0.0361, A·U 2020-23 −0.0168 to 0.0374 → −0.0234 to 0.0369, A·W·T 2020-23 −0.0204 to 0.0340 → −0.0206 to 0.0369.
- **Centroid dispersion** (`q6_centroid_dispersion.csv`): between-cohort distance band 2012-15 0.0044–0.0172 → 0.0042–0.0176, 2016-19 high 0.0106 → 0.0102, 2020-23 low 0.0028 → 0.0027.
- **CVT / Lift + Cruise distance** (`q6_iv2_merge_cvt_lc_distance.csv`): CVT* band −0.0529 to 0.0561 → −0.0550 to 0.0580, CVT band high 0.0520 → 0.0504.
- **Discovery curve** (`q6_discovery_estimators.csv`): A·U new in the last 100 designs 1.07 → 1.09 (before that 0.93 → 0.91). A·W·T new in the 100 before the last 2.36 → 2.31. The last 100 at A·W·T stay 4.14 against 1.61 by chance. The curve's mean and 95 % band move in the second decimal (`q6_discovery_curve.csv`).
- `NUMBERS_III.md`, `NUMBERS_IV.md` and `NUMBERS_VI_form_families.md` carry the same numbers, plus the new count in their method lines.

## Step 2. Holm correction

`lib/multiple.py` (new) wraps `statsmodels.stats.multitest.multipletests(method="holm")`. A test that could not run (NaN) stays
out of its family. Every raw p stays in its column and the Holm p sits beside it as `… (Holm)`. No raw value moved: the
existing columns are byte-identical to step 1. The register of every test in the four families, with p, Holm p and the verdict at
0.05 before and after, is `Data_for_writing/csv/holm_register.csv` (written by notebook 56).

| family | where (CSV) | family = | tests | below 0.05 raw → Holm |
|---|---|---|---|---|
| I.2 dataset against the in-domain directory and its parts, chi-square | `q4_dataset_vs_directory_subsets.csv`, `numbers_I_in_domain_directory_parts.csv` | the 5 directory readings tested against the dataset | 5 | 4 → 4 |
| II.1 dimension × architecture | `q6_fixed_by_architecture.csv` | the 10 dimensions of Table 4.3 | 10 | 10 → 10 |
| III.1 architecture share × priority year, Spearman | `q6_share_trend_spearman.csv` | the 7 architectures, separately for 2008-2023 and for 2016-2023 | 7 + 7 | 1 → 1 and 0 → 0 |
| V region × measure, chi-square | `q7_region_tests.csv` (**new**, was only quoted in NUMBERS_V) | each assignee reading (all assignees; without Bell / Textron), 5 measures × 4 periods | 20 + 20 | 9 → 5 and 7 → 0 |
| V trend of a regional answer, Spearman 2012-2023 | `q3_region_mix_change.csv` (**new**) | every region × variable × answer with a defined p | 42 | 8 → 3 |

Corrections to the brief:
- II.1 uses no chi-square. Its per-dimension test is the bias-corrected Cramér's V with a permutation p (1000 shuffles, from `viz/thesis_q6.py`). Holm is applied to those permutation p values. Seven of the ten are p = 0 (no shuffle reached the observed V), and their Holm values stay 0, printed "< 0.001".
- III's "architecture-by-cohort" tests in the code are Spearman trends of each architecture's yearly share on the priority year (III.1). No chi-square of architecture × cohort is computed.
- Stale copies: `thesis_figures_v2/…/II1_varying_attributes/appendix/q6_fixed_by_architecture*.csv` (and its copy under `LaTeX_v15/Figures/thesis_figures_v2/`) date from 2026-10-16. Notebook 50 no longer writes them, so they lack the Holm column. The live tables are `LaTeX_v15/Data_for_writing/csv/` and `LaTeX_v15/Figures/Part_II_design_space/II1_varying_attributes/appendix/`. The stale copies were left in place.

### Tests whose verdict at 0.05 changes after Holm (all lose significance; none gains it)

No test of I.2, II.1 or III.1 changes. The largest Holm p among the II.1 dimensions is tail type, 0.024. Tilt Propulsor's III.1 trend (2008-2023)
goes from 0.004 to 0.029, still below 0.05.

Analysis V, region × measure (chi-square), all assignees:

| measure · period | p → Holm p | quoted as |
|---|---|---|
| class mix · 2016-19 | 0.0057 → 0.080 | |
| propulsor-unit band · 2020-23 | 0.0036 → 0.054 | `p_units_2023` (0.004) |
| any tilting unit · 2016-19 | 0.036 → 0.43 | |
| family F · all years | 0.018 → 0.24 | |

Analysis V, region × measure (chi-square), without Bell / Textron (every test of this family loses significance):

| measure · period | p → Holm p | quoted as |
|---|---|---|
| class mix · 2016-19 | 0.012 → 0.24 | |
| class mix · 2020-23 | 0.013 → 0.25 | |
| propulsor-unit band · 2020-23 | 0.039 → 0.59 | |
| any tilting unit · all years | 0.023 → 0.42 | NUMBERS_V "chi-square p … 0.023 without" (North America tilting share without its largest assignee) |
| any tilting unit · 2020-23 | 0.030 → 0.50 | |
| Tilt Rotor · all years | 0.035 → 0.57 | |
| Tilt Rotor · 2020-23 | 0.042 → 0.59 | |

Analysis V, trend of a regional answer, 2012-2023 (Spearman):

| region · variable · answer | rho, p → Holm p | quoted as |
|---|---|---|
| North America · family F · yes | +0.20, 0.0030 → 0.117 | `r_na_rho_p` (V.4) |
| Europe · propulsor units · 7-8 | +0.21, 0.012 → 0.44 | `eu_u78_p` (0.012) |
| Europe · propulsor units · 1-3 | −0.19, 0.026 → 0.94 | |
| Europe · propulsor units · 4 | −0.18, 0.032 → 1.00 | |
| Europe · family F · yes | +0.18, 0.025 → 0.93 | |

These survive Holm: region × class mix (all years 0.006, 2020-23 0.012), any tilting unit (all years < 0.001, 2020-23 0.006),
Tilt Rotor all years (0.012), and the North American trends in CVT (0.016), 1-3 propulsors (0.004) and 5-6 propulsors (< 0.001).

**Does a conclusion change?** One does. Analysis V's claim that the regions still differ once Bell / Textron is left out does not survive:
none of the 20 tests without Bell / Textron stays below 0.05. So the regional difference in tilting and Tilt Rotor rests on the
largest North American assignee. The overall regional difference in architecture and tilting (all assignees) stands. So do North America's own trends towards
CVT and 5-6 propulsors, but not its family F trend, and none of Europe's trends.

How much this depends on the family: the families above are deliberately wide. With one family per region for the trends, North America
family F stays significant (Holm 0.033) and every Europe trend still fails. With one family per measure for the chi-squares
(5 measures, each with 4 periods and 2 assignee readings), class mix without Bell / Textron in 2016-19 and in 2020-23 stays at 0.049. Every other change in the
tables above stands. The definition is a choice for the text. The code applies the wide one (`viz/frames.py: region_tests,
region_mix_change`).

## Step 3. Threshold sensitivity

Written by the new notebook `labeling_evaluation/notebooks/56_supervisor_review_2.ipynb` (module `viz/review2.py`, generated by
`notebooks/_build/build_56.py`), after step 2. All counts are those of step 1 (1000 permutations / draws), seed 42.

### 3a. The 80 % share rule (`q6_fixed_by_architecture`) at 70 % and 90 %

Tables: `csv/q6_fixed_by_architecture_share70.csv`, `_share90.csv` and their `_detail_` files, beside `q6_fixed_by_architecture.csv`
(and in `thesis_figures_v2/Part_II_design_space/II1_varying_attributes/appendix/`). Cramér's V and p do not depend on the rule.

| dimension | architectures fixed at 70 % | 80 % (main) | 90 % |
|---|---|---|---|
| propulsors per design (band) | 0 of 7 | 0 of 7 | 0 of 7 |
| tail type | 1 of 7 | 0 of 7 | 0 of 7 |
| places carrying propulsors | 1 of 7 | 1 of 7 | 1 of 7 |
| booms present | 3 of 9 | 2 of 9 | 2 of 9 |
| propulsor enclosure (any ducted) | 2 of 7 | 1 of 7 | 0 of 7 |
| fuselage shape | 2 of 7 | 1 of 7 | 0 of 7 |
| number of wings | 2 of 7 | 1 of 7 | 1 of 7 |
| landing-gear type | 3 of 7 | 0 of 7 | 0 of 7 |
| fuselage motion hover to cruise | 6 of 7 | 5 of 7 | 5 of 7 |
| wing configuration | 6 of 6 | 5 of 6 | **1 of 6** |

**Does a conclusion change?** Partly. "The architecture fixes the fuselage motion" holds at every threshold: 5 of 7, with
Lift + Cruise, Tilt Propulsor, CVT, Tilt Wing and Pitch-to-Cruise at 98–100 %. "The architecture fixes the wing configuration" holds at 70 %
and 80 % only. Standard wings lead with 87 % (Separate Lift + Cruise), 92 % (Tilt Propulsor), 88 % (CVT), 80 % (Tilt Wing),
79 % (Tilt Frame) and 88 % (Pitch-to-Cruise), so at 90 % only Tilt Propulsor stays fixed. Write the wing claim as "standard wings in roughly 80–90 % of each winged architecture's designs", not as fixed. At 70 %, landing gear (3 of 7) becomes "fixed", but its leading option is "Unknown" in each case: an artefact of unrecorded answers, not a design rule. None of the other dimensions supports a claim at any threshold.

### 3b. Rarefied to 30 and 50 instead of 40

Tables: `csv/q7_hill_by_cohort_rarefied30.csv`, `…40.csv`, `…50.csv`. Each holds, per level (A, A·W·T, A·U, F) and cohort, the rarefied ⁰D, ¹D, ²D
(1000 draws) and the condition-2 band at that size (1000 permutations). The 40 table reproduces `q7_condition2_balance.csv`.

Correction to the brief: the code rarefies to `rarefy_n = 40` (`labelling_analysis.yaml`), not to the smallest cohort. 58 is the size of the smallest
complete cohort (2012-15). So both 30 and 50 draw without replacement from every complete cohort.

Condition 2 (²D below the band), all designs:

| level, 2020-23 | n = 30 | n = 40 (main) | n = 50 |
|---|---|---|---|
| A | 4.49 < 4.64 ✓ | 4.55 < 4.73 ✓ | 4.63 < 4.81 ✓ |
| A·W·T | 7.89 < 7.91 **✓** | 8.36 ≥ 8.30 ✗ | 8.62 < 8.63 **✓** |
| A·U | 13.03 ≥ 12.58 ✗ | 14.49 ≥ 13.85 ✗ | 15.59 ≥ 14.74 ✗ |
| F | 3.25 < 3.55 ✓ | 3.25 < 3.62 ✓ | 3.27 < 3.63 ✓ |

In the earlier cohorts every cell keeps its reading at all three sizes (A·U ≤ 2011 and 2012-15 below the band; all others not).

**Does a conclusion change?** Not the verdict. A·W·T condition 2 in 2020-23 flips from "not met" (40) to "met" (30 and 50).
Its ²D sits on the edge of the band at every size: 0.02, 0.06 and 0.01 from the lower edge. So the A·W·T reading of condition 2 should be
written as "at the edge of the band", not as a clear "not met". Condition 1 fails at every level, so "all three conditions in the same period" stays not
met everywhere, and the dominant-design verdict is unchanged. ²D grows with n, as expected (A·U 2016-19: 14.5 / 16.2 / 17.6), and the bands
grow with it. The comparison against the band, not the raw ²D, is what the text should rest on.

### 3c. Acceptance threshold of the TRL and date scripts

Table: `csv/script_acceptance_thresholds.csv` (also `review/decisions/ACCURACY_THRESHOLD_SENSITIVITY.csv`), from
`review/decisions/ACCURACY_TABLE.csv` (notebook 60).

Correction to the brief: no 70 % threshold exists in the code or the review notes. The documented rule
(`review/HOW_THE_REVIEWS_WERE_DONE.md`, `notebooks/_build/review_confidence.py`) accepts a source when the **lower bound** of its 95 %
Wilson interval (finite-population corrected) is at or above **90 %**. Notebook 60 applies that to the reading-step inputs. Both readings are given here: the point share, and the lower bound.

| input, method | share (95 % interval) | accepted on the share at 60 / 70 / 80 / 90 % | on the lower bound at 60 / 70 / 80 / 90 % |
|---|---|---|---|
| year, script, exact | 60.5 % (50.0–70.1) | ✓ / ✗ / ✗ / ✗ | ✗ / ✗ / ✗ / ✗ |
| year, script, within 1 year | 75.3 % (65.3–83.2) | ✓ / ✓ / ✗ / ✗ | ✓ / ✗ / ✗ / ✗ |
| year, script, same cohort (the unit the figures use) | 71.6 % (61.4–80.0) | ✓ / ✓ / ✗ / ✗ | ✓ / ✗ / ✗ / ✗ |
| TRL, script, exact | 46.0 % (36.3–56.0) | ✗ / ✗ / ✗ / ✗ | ✗ / ✗ / ✗ / ✗ |
| TRL, script, same side of TRL 2 (the unit the figures use) | 74.0 % (64.3–81.8) | ✓ / ✓ / ✗ / ✗ | ✓ / ✗ / ✗ / ✗ |
| TRL, script, within 1 level | 74.0 % (64.3–81.8) | ✓ / ✓ / ✗ / ✗ | ✓ / ✗ / ✗ / ✗ |
| year, reading step (author-checked) | 93.3 % (86.5–96.8) | ✓ / ✓ / ✓ / ✓ | ✓ / ✓ / ✓ / ✗ |
| TRL, reading step (author-checked) | 100 % (96.1–100) | ✓ / ✓ / ✓ / ✓ | ✓ / ✓ / ✓ / ✓ |

**Does a conclusion change?** No figure changes. The acceptance decision gates nothing in the code: `external_inputs: script` feeds the script
values to every Part I figure whatever the threshold. What changes is the status the text may give the scripts:
- At 80 % (either reading) no script output is accepted, and the scripts can only be reported as transparent baselines. That is also the case at 90 %, the documented rule.
- At 70 % they pass only on the point share, in the units the figures use (same cohort, same side of TRL 2). On the lower bound they fail.
- At 60 % they pass on the lower bound too, except the exact year and the exact TRL.

So "the scripts are acceptable stand-ins" is true only below 70 % on the lower bound. Above that the text has to call them baselines.

## Step 4. Figure 4.2, the growth comparison (`q1_growth_rates`)

New module `lib/growth_models.py`. Called by `viz/thesis_q1.py: growth_models`, drawn by `viz/thesis_v2_part1.py: fig_growth_rates_ts`
and `fig_growth_baselines_ts`, exported by notebook 48. Every series is fitted alone on ln(count) by priority year, 2005–2022, by least squares:
(a) two lines with a free level step at the break, (b) two lines that meet at the break (slope change only), (c) a logistic S-curve.
The break is each series' own: every year that leaves at least 3 years on each side (2008–2020) is tried. Aeronautics is not forced to 2016.
The break and the error variance count as parameters (k = 6 / 5 / 4). Intervals: residual bootstrap, 1000 resamples per series and
model, the break searched again in every resample, seeds [42, series, model]. "Wins clearly" = lowest AIC and lowest BIC by 10 or more on both
(Burnham & Anderson). Tables: `csv/numbers_I_growth_models.csv` (AIC / BIC / AICc), `csv/numbers_I_growth_breakpoints.csv` (breaks, slopes,
step, logistic t0 and r, all with intervals), and the section "I.1 growth models" of `NUMBERS_I.md`.

### The figure

- Removed: the black level-shift arrows, the "jump at 2016" text, the "split at 2016" panel and their legend entries.
- (a) eVTOL architecture patents and aeronautics (CPC B64), relative to 2005–09 (log 2), each drawn with the model that wins for it. The two segments of the step model are separate lines: nothing joins them and there is no arrow. 2023–26 are hollow and not fitted.
- (b) one line: eVTOL families per 1 000 B64 families per priority year. Both are PatSeer simple families, so the ratio is like for like.
- Section B and all patents: new appendix figure `q1_growth_rates_baselines` (same reading, one panel each), exported to `Figures/Part_I_evidence_base/I1_patenting_rate/appendix/`.
- 6.3 in (full text width), nothing under 8 pt (`ts.save` asserts both), no text over text (`figcheck.overlaps`: none).
- `q1_growth_rates.csv` gains the column `eVTOL per 1 000 B64 families`. The old turning-point and segment-slope sections of `NUMBERS_I.md` stay for the record, marked as no longer drawn.

### Model comparison, 2005–2022 (Δ = distance to the best model)

| series | (a) step: ΔAIC / ΔBIC | (b) hinge | (c) logistic | winner |
|---|---|---|---|---|
| eVTOL architecture patents | 0 / 0 | 12.2 / 11.3 | 15.1 / 13.3 | (a), clearly |
| aeronautics (CPC B64) | 0 / 0 | 19.7 / 18.8 | 24.4 / 22.6 | (a), clearly |
| transport and operations (CPC B) | 0 / 0 | 13.6 / 12.7 | 19.7 / 17.9 | (a), clearly |
| all patents | 0 / 0 | 4.3 / 3.4 | 8.0 / 6.2 | (a), not clearly |

### Breaks and slopes of the winning model (a), 95 % bootstrap intervals

| series | break | share of resamples at it | slope before (per year, log) | slope after | level step |
|---|---|---|---|---|---|
| eVTOL | 2016 (2016–2017) | 97 % | 0.130 (0.083–0.177), ×2 in 5.3 y | 0.061 (−0.026–0.144) | ×3.35 (2.12–5.05) |
| aeronautics (B64) | 2016 (2016–2016) | 100 % | 0.130 (0.111–0.148), ×2 in 5.3 y | 0.013 (−0.026–0.054) | ×2.10 (1.77–2.57) |
| transport (CPC B) | 2016 (2016–2016) | 100 % | 0.069 (0.049–0.088) | 0.025 (−0.012–0.066) | ×2.05 (1.67–2.48) |
| all patents | 2016 (2015–2019) | 85 % | 0.062 (0.051–0.074) | 0.027 (0.001–0.053) | ×1.20 (1.06–1.33) |

Ratio (panel b): eVTOL families per 1 000 B64 families average 3.2 a year over 2005–2015 and 5.8 over 2016–2022 (4.7, 5.3, 6.2, 5.7, 5.5, 6.6, 6.6).

### With 2023 included

Nothing changes. Every winner is the same (eVTOL (a): ΔAIC 15.2, ΔBIC 14.3), every break stays at 2016, and the eVTOL step is ×3.57 (2.38–5.42) against
×3.35. The eVTOL slope after the break drops from 0.061 to 0.030 (−0.039–0.093), still indistinguishable from zero. B64 gives ×2.11, slope after 0.011.

### Old → new

- Old figure: eVTOL level shift ×3.38 at 2016 from `lib/growth.turning_point` (2006–2023, break searched over 2009–2020, residual bootstrap of 2000 draws (`TURNING_DRAWS`; the NUMBERS_I heading says 5 000, which is wrong), 90 % of resamples at 2016, range 2015–2018), drawn as arrows. New: ×3.35 (2.12–5.05) at 2016, 97 % of resamples, range 2016–2017, on 2005–2022.
- The old figure drew aeronautics at the eVTOL break. Its own break, searched freely, is also 2016, so that part of the old drawing was right, but it was not shown to be.
- Doubling times before the break: 5.3 y for both (unchanged; this is the slope of the step model, which is the same as the separate 2005–15 fits). The 2005–2023 single-line doubling times (3.6 y and 4.7 y, `q1_growth_rates_table`) are untouched.

### What the result means (read before writing)

The supervisor's point holds in one direction and not the other. The step is in the data, not only in the model: a free level step beats a continuous
slope change and a logistic curve by more than 10 in AIC and BIC for eVTOL, and the break lands in 2016 when each series chooses its own. But the
same step, in the same year, appears in aeronautics (×2.1), in all of section B (×2.05) and, weakly, in all patents (×1.2). Something at priority
year 2016 lifts every PatSeer series, possibly a change in coverage or a surge in national filings. The text should not present the 2016 step as an eVTOL event. What is specific to eVTOL is the size of its step relative to aeronautics: ×3.35 against ×2.10, so the ratio
roughly doubles, from about 3 to about 6 eVTOL families per 1 000 B64 families. That is the quantity panel (b) shows.

### Three sentences for the text

1. For eVTOL architecture patents, a model of two lines with a free level step fits the 2005–2022 priority-year counts clearly better than a continuous change of slope or a logistic S-curve (ΔAIC 12.2, ΔBIC 11.3): filing grew about 14 % a year before 2016 (doubling every 5.3 years), rose by a factor of 3.4 (95 % bootstrap interval 2.1 to 5.1) in 2016, and grew at a rate indistinguishable from zero thereafter (0.06 per year, −0.03 to 0.14).
2. Aeronautics (CPC B64), with its breakpoint estimated independently, shows the same structure: the step model again wins clearly (ΔAIC 19.7, ΔBIC 18.8), the break falls in 2016 in every bootstrap resample, growth before it matches eVTOL's (doubling every 5.3 years), the step is smaller (×2.1, 1.8 to 2.6) and the series is flat afterwards (0.01 per year, −0.03 to 0.05).
3. Because a step of similar timing appears in every PatSeer baseline, the 2016 jump is not specific to eVTOL; what distinguishes eVTOL is its larger step, which raised its share of aeronautics patenting from about 3 to about 6 families per 1 000 (Figure 4.2b), and including 2023 changes none of these results.

The word "jump" appears in sentence 3 only. Model (a) wins clearly for eVTOL, and the sentence uses the word for what is shared across the series, not for an eVTOL-only event.

## Fixes after the handover (2026-10-22)

Rerun: notebooks 48 and 50 (side by side), then 54 and 56. Seeds unchanged. Outside the items below, no number moved: the CSVs other than those
named here are identical to the 2026-10-21 run, and MANIFEST.md lost no line.

### 1. `q6_configuration_core`: "rim" → "periphery"

- Figure: the label left of the dashed line reads "periphery". "core (10 configurations, half of the designs)" is unchanged.
- CSV: values of `group` are `core` / `periphery`, and the column `core / rim threshold (share 2016-23, drawn)` is now `core / periphery threshold (share 2016-23, drawn)`.
- JSON title: "Crowded core and empty rim" → "Core and periphery of the configurations".
- MANIFEST and NUMBERS_II describe the grey points as the periphery.
- Checked: the words "rim", "crowded" and "empty" appear in none of the figure's PDF, CSV or JSON files. The figure has no legend; the two labels at the top are its key.
- Not changed: the older Q6 document layer (`viz/thesis_q6.py` figure `q6_archetype_core`, `viz/thesis_text_q6.py`, notebooks 41/46/47) still says "crowded core" / "empty rim". It is not part of LaTeX_v15. Internal variable names (`rim`) are unchanged.

### 2. `q6_fixed_by_architecture`: one architecture set across 70 / 80 / 90 %

The brief's premise did not hold. The three files of 2026-10-21 already used the same architecture set: identical rows and design counts, with booms present "of 9" in all three (80 % read "2 of 9"). The "0 of 7" in the dissertation's table comes from a different readability rule. The code reads an architecture from **10** answering designs (`thesis_q6.FIXED_MIN_DESIGNS`, stated in NUMBERS_II). Under that rule booms present also reads Hoverbike (19) and Personal Flying Vehicle (10), and both have no booms in ≥ 90 % of their designs, hence "2 of 9". The dissertation's table reads an architecture from **20** designs. With 20, booms present has 7 architectures and none reaches 80 %, so "0 of 7".

So the comparable trio at your rule (20 designs) is now written beside the others: `csv/q6_fixed_by_architecture_min20_share70.csv`, `_share80.csv`, `_share90.csv` (plus `_detail_`, also in `thesis_figures_v2/…/II1_varying_attributes/appendix/`). The main file `q6_fixed_by_architecture.csv` stays on the documented rule of 10. If the dissertation keeps 20, cite the `min20` files, and change the rule in NUMBERS_II's text, or set `FIXED_MIN_DESIGNS = 20`.

| dimension | 70 % | 80 % | 90 % | (main file, rule of 10: 70 / 80 / 90 %) |
|---|---|---|---|---|
| propulsors per design (band) | 0 of 7 | 0 of 7 | 0 of 7 | 0 / 0 / 0 of 7 |
| tail type | 1 of 7 | 0 of 7 | 0 of 7 | 1 / 0 / 0 of 7 |
| places carrying propulsors | 1 of 7 | 1 of 7 | 1 of 7 | 1 / 1 / 1 of 7 |
| booms present | 1 of 7 | **0 of 7** | 0 of 7 | 3 / 2 / 2 of 9 |
| propulsor enclosure (any ducted) | 2 of 7 | 1 of 7 | 0 of 7 | 2 / 1 / 0 of 7 |
| fuselage shape | 2 of 7 | 1 of 7 | 0 of 7 | 2 / 1 / 0 of 7 |
| number of wings (winged designs) | 1 of 6 | 0 of 6 | 0 of 6 | 2 / 1 / 1 of 7 |
| landing-gear type | 3 of 7 | 0 of 7 | 0 of 7 | 3 / 0 / 0 of 7 |
| fuselage motion hover to cruise | 6 of 7 | 5 of 7 | 5 of 7 | same |
| wing configuration | 6 of 6 | 5 of 6 | 1 of 6 | same |

At 20 designs the two rows that differ from the main file are booms present and number of wings. In both, the architectures that dropped out (Hoverbike, Personal Flying Vehicle) were the ones counted as fixed. The step-3a reading is unchanged: fuselage motion is fixed at every share, and wing configuration only up to 80 %.

Readable architectures per dimension (`csv/q6_fixed_by_architecture_readable.csv`; answering designs in brackets):

- **20 designs or more**, every dimension except the two below: Separate Lift + Cruise (165), Tilt Propulsor (151), Combined Vectored Thrust (106), Tilt Wing (56), Multicopter (48), Tilt Frame (24), Pitch-to-Cruise (25). Seven architectures.
- **number of wings (winged designs)**: Separate Lift + Cruise (158), Tilt Propulsor (145), Combined Vectored Thrust (103), Tilt Wing (56), Tilt Frame (23), Pitch-to-Cruise (23). Six (Multicopter has no wing; Hoverbike has 17).
- **wing configuration**: the same six as number of wings, with 165, 151, 106, 56, 24, 25.
- Under the rule of 10, booms present adds Hoverbike (19) and Personal Flying Vehicle (10), and number of wings adds Hoverbike (17). Nothing else changes.
- Never readable: Rotorcraft, Stopped/Slowed Rotor Wing and Deflected Slipstream (under 10 designs everywhere). Hoverbike and Personal Flying Vehicle have no propulsor card, so they are not read in the propulsor rows.

### 3. The A·W·T 2020-23 balance cell at the three rarefaction sizes

`csv/q7_condition2_awt_2020_23_by_rarefaction.csv` (all designs, 236 designs in the cohort, 1000 permutations, seed 42):

| rarefied to | observed ²D (middle 95 % of its draws) | band (2.5–97.5 %) | ²D − band low | as a share of the band width | condition 2 |
|---|---|---|---|---|---|
| 30 | 7.89 (5.36–11.25) | 7.91–9.72 | −0.02 | −1.1 % | met |
| 40 (main) | 8.36 (6.06–11.27) | 8.30–10.37 | +0.06 | +2.9 % | not met |
| 50 | 8.62 (6.48–11.26) | 8.63–10.82 | −0.01 | −0.5 % | met |

At every size ²D sits within 0.06 of the band's lower edge, which is 3 % of the band's width or less. The rarefaction draws of ²D itself spread over about 6 units. The cell is on the edge at all three sizes, and the verdict at any one size should not be read as a result.
One sentence for the text: "At A·W·T the 2020-23 cohort sits on the lower edge of the band at every rarefaction size (²D 7.89, 8.36 and 8.62 against lower edges of 7.91, 8.30 and 8.63 at 30, 40 and 50 designs), so condition 2 is neither clearly met nor clearly failed at that level."

### 4. Figure 4.2: unchanged; the comparison table as a CSV

- `csv/numbers_I_growth_model_comparison.csv`: one row per series and model (4 × 3 = 12 rows), fit 2005–2022, with n, k, SSE, AIC, BIC, AICc, ΔAIC, ΔBIC, the lowest-AIC and lowest-BIC flags and "wins clearly". Written by notebook 48 (`viz/latex_v15.py:_growth_models`). The 2023 check rows stay in `csv/numbers_I_growth_models.csv`.
- The three sentences for the text were already in these notes ("Step 4 → Three sentences for the text"). They are unchanged.

### 5. Two numbers for Section 3.4.1 (2026-10-22, no code changed)

(a) **Resampling interval of the median lag between regions:** still **2 000** bootstrap redraws with replacement (`lib/regional.py: DRAWS = 2000`, the default of `lag_offsets` and `lag_offsets_since`; seed 42). Step 1 did not touch it (it was not a 200/300/400 count). Left as it is.

(b) **Permutation-band example, cohort 2020-23, rarefied to 40, all designs, 1000 permutations:**

| level | old (200 permutations): ²D against band lower edge | new (1000 permutations) | source |
|---|---|---|---|
| F (Lift + Cruise + CVT* family): the pair the text quotes (3.22 / 3.65) | 3.22 / 3.65 | **3.25 / 3.62** | `csv/q7_family_conditions.csv`, panel (b), all designs, 2020-23 |
| A (architecture) | 4.53 / 4.74 | **4.55 / 4.73** | `csv/q7_condition2_balance.csv`, level A, 2020-23 |

The 3.22 / 3.65 in the text belongs to family F, not to the architecture level. Either keep the F example and update it to 3.25 / 3.62, or call it the architecture level and use 4.55 / 4.73. Both stay below the band (condition 2 met).

## Section 4.2.3 outputs (2026-10-22, no new reading of any patent)

Run: notebooks 48 and 56 side by side. Seeds unchanged. No existing number moved; only columns and files were added.

### 1. Cohen's kappa, architecture level, the 97 named designs

New column `Cohen's kappa` in `q4_coding_agreement.csv` (`thesis_figures_v2/Part_I_evidence_base/I3_construct_validity/main/`, and now also
`LaTeX_v15/Data_for_writing/csv/`). Computed by `lib.association.cohen_kappa` in `viz/thesis_q4.py: pairwise`.

| pair | agree | share | Cohen's kappa |
|---|---|---|---|
| drawing label against the public aircraft | 87 of 97 | 0.90 | **0.87** |
| patent text against the public aircraft | 89 of 97 | 0.92 | **0.90** |
| drawing label against the patent text | 93 of 97 | 0.96 | **0.95** |

How the public aircraft's label was obtained (no new reading; `thesis_q4.public_labels`): the record stores the public architecture as
free text only where it disagrees, so the label is rebuilt from the existing match field. Rows counted as agreeing ("yes", "taxonomy")
take the label of the source they are compared with, and "image" rows take the text's label in the drawing pair. The 8 "no" rows take the architecture their
free text names: "tilt rotor" → Tilt Propulsor (S4 v1, AE200), "lift + cruise" → Separate Lift + Cruise (Cora v1). Otherwise they keep the free text as a label
that matches no source: Wisk Z-P1 "conventional take-off", Porsche-Boeing concept ×3 and S-A1 v1 "vectored thrust". The public label is set per pair
because the table counts one "taxonomy" row, GyroBike (drawing Multicopter, text Stopped/Slowed Rotor Wing), as agreement in both public pairs.
The code asserts that the rebuilt labels give back Table 2's agreement counts exactly.

### 2. The funnel, `q4_funnel_steps.csv` (`LaTeX_v15/Data_for_writing/csv/`)

One row per population, with the share of every architecture as its own column.

| population | designs | largest architecture (share) | median propulsors | priority 2020-2023 |
|---|---|---|---|---|
| all designs | 627 | Separate Lift + Cruise (26.4 %) | 5 (595 with a count) | 37.8 % |
| named designs (public counterpart, Table 2) | 97 | Separate Lift + Cruise (29.9 %) | 8 (95) | 45.4 % |
| flown, TRL 5 or more | 68 | **Tilt Propulsor (30.9 %)**, Separate Lift + Cruise 29.4 % | 8 (68) | 50.0 % |
| designs of the 12 index assignees that have flown | 42 | Separate Lift + Cruise (47.6 %) | 9 (40) | 47.6 % |
| designs of the 14 index assignees | 47 | Separate Lift + Cruise (51.1 %) | 8 (45) | 51.1 % |

Correction to the brief: the 14 AAM Reality Index assignees that file here hold **47** designs. The **42** designs belong to the **12** of them that
had flown by the release (first flight on or before 2025): the flown index-assignee group of NUMBERS_I. Both rows are in the CSV.
Shares of architecture are over the designs with an architecture recorded (625 of the 627; all designs in the other populations).
The median propulsor count is over the designs with a count (Hoverbike and Personal Flying Vehicle have none). The 2020-2023 share is over the designs with a priority year.

### 3. Patent-to-flight lead from the first publication instead of the first priority

`q4_publication_lead.csv` (per assignee) and `q4_publication_lead_summary.csv`. The first publication year is the earliest publication year
of the assignee's designs' patents (`frames.with_publication`). It is in years, like the index's first-flight year.

**One line for the text:** measured from the first publication instead of the first priority date, the median lead of the 12 index assignees that have flown falls from 3 to 1.5 years (range −2 to 6, against −1 to 7). Across all 13 assignees with a first-flight year, a planned 2027 included, it falls from 3 to 2 years. The difference to the priority-based median is −1.5 years (−1 year over the 13).

The brief's "same 14" does not hold: Supernal has no first-flight year in the index, so 13 of the 14 have a lead. The priority-based median of 3 years is the same over the 12 and over the 13.

## B64 refit without B64U and without B64C 29/00 (2026-10-22): NOT RUN, data missing

The only aeronautics baseline on this machine is one PatSeer export of `CPC:(B64*)` totals per priority year, with no subclass split, so the two refits cannot be computed. The code is ready:
`viz/review2.py: b64_refits` uses the same three models and bootstrap as Fig 4.2 (2005-2022), and notebook 56 runs it once these two exports exist in
`labeling_evaluation/assets/external/aviation_baseline/patseer_worldwide/`, in the same format as `patseer_B64_worldwide_by_priority_year.csv`
(families by Earliest Priority Year, no country filter):
- `patseer_B64_noB64U_worldwide_by_priority_year.csv`: query `CPC:(B64*) NOT CPC:(B64U*)`
- `patseer_B64_noB64C29_worldwide_by_priority_year.csv`: query `CPC:(B64*) NOT CPC:(B64C29*)`
Output: `csv/numbers_I_b64_parts_models.csv` and `_estimates.csv`.

### B64 refit: RUN 2026-10-22 (exports received)

The author's PatSeer exports (simple families by earliest priority year) are saved as `patseer_B64_noB64U_…csv` (`CPC:(B64*) NOT CPC:(B64U*)`)
and `patseer_B64_noB64C29_…csv` (`CPC:(B64*) NOT CPC:(B64C29*)`). Run by notebook 56, 2005-2022, with the same three models and bootstrap as Fig 4.2.
Output: `csv/numbers_I_b64_parts_models.csv`, `_estimates.csv`. In both, the free-step model (a) wins clearly and the break is 2016 in every resample.

- **Without B64U (drones):** the 2016 step remains, smaller: ×1.72 (95 % 1.51–1.99) against ×2.10 for all of B64 (ΔAIC 18.3 / ΔBIC 17.4 over the next model).
- **Without B64C 29/00 (VTOL aircraft):** the 2016 step remains, practically unchanged: ×2.08 (1.75–2.47) against ×2.10 (ΔAIC 20.1 / ΔBIC 19.2).

So drones carry about a fifth of the B64 step, the eVTOL class itself none, and most of the step is in the rest of aeronautics. That is consistent with a database-coverage
effect common to every PatSeer series. (B64's own interval reads 1.73–2.55 here, against 1.77–2.57 in Fig 4.2, because its bootstrap seed is
[42, series index, model] and B64 is the first series here, not the second; the point estimate ×2.10 is the same.)

## 2026-10-22: band of the last 100 designs (Analysis II.3, discovery curve)

`lib/diversity.discovery_tail_band` (new; `SHUFFLES = 10000`), written by notebook 50 through `viz/thesis_latex_part2.tab_discovery_last100_band` to
`Data_for_writing/csv/q6_discovery_last100_band.csv` (+ MANIFEST row, NUMBERS_II "Band of the last 100 designs"). Date order = the curve's 1000 tie orderings (same
generator stream, seed 42; reproduces 4.14 / 1.09); random = 10 000 full shuffles (seed 42), mean checked within 0.02 of the exact expectation 1.61 / 0.60.
A·W·T: 95th pct 4, 99th 5, p (share ≥ 4.14) 0.0126, p (whole counts) 0.0579. A·U: 95th 2, 99th 3, p 0.1058 / 0.4447. No .tex or figure changed.
Backup: `_BACKUPS/PRE_LAST100BAND_LaTeX_v15_20261022`.
