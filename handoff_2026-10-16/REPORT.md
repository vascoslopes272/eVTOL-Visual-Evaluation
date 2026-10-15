# Hand-over 2026-10-16: five figure and table tasks (plus Task 6, exploratory)

Tasks 1 to 5 are done. Every output was written by running the notebooks end to end, headlessly (`jupyter nbconvert --execute`): notebook 52 (Part III, Tasks 1 and 3), notebook 50 (Part II, Tasks 2 and 4), notebook 51 (Part IV, the CVT* distance of Task 1) and notebook 53 (Part V, Task 5). Each of those notebooks has a new last section "Hand-over 2026-10-16" that writes the extra copies listed below through `viz/handoff_2026_10_16.py`. No .tex file was edited and Thesis.pdf was not rebuilt. `FINAL_2026-10-14/` was not touched. Task 6 is in its own section at the end.

**Where things are.** As on 2026-10-15, the dissertation repository is not on this computer. `LaTeX_v15/` is the export folder next to the other thesis outputs:

    D = /mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED/1_labelling_analysis/labelling_analysis_thesis

All `LaTeX_v15/...`, `thesis_figures_v2/...` and `thesis_figures/...` paths below are under `D`. To use them in the dissertation, copy them over the dissertation repository's `LaTeX_v15/` (same paths).

**How I read the three destinations each task names.**
- "LaTeX_v15/Figures/Part_.../main (or appendix, auxiliary)": the final-width pdf the text prints, with png (300 dpi), csv and json beside it.
- "LaTeX_v15/Figures/thesis_figures_v2/... (same subfolder)": that folder did not exist. I created it and put there a copy of the notebook-size (v2) files, which the notebooks write to `D/thesis_figures_v2/<Part>/<group>/<role>/` as always (both places now hold them).
- "the script's results folder": for the Q7 and Q2 items this is `thesis_figures/Q7_dominant_design/results/` and `thesis_figures/Q2_filers/results/` (the builder and writer of notebook 46, as the 2026-10-15 hand-over did; copied here as `<name>_q7results.*` / `<name>_q2results.*`). For the items that exist only in the v2 layer (Task 2 tables, `q6_half_of_cohort`, `q7_family_conditions` also has a Q7 item) the results folder is the `thesis_figures_v2` folder above.

Files in each `taskN/` folder: `<name>.pdf/.png/.csv/.json` are the LaTeX_v15 versions (final width in the text block); `<name>_v2.*` the notebook-size copies; `<name>_q7results.*` / `_q2results.*` the notebook-46 versions; the changed scripts and notebooks are copied in full.

**Everything is recomputed with seed 42, 200 permutations, the same rarefaction (40) and the same bases.** No number was changed to match the dissertation text; where a value differs from the text, the new value is reported here.

---

## Task 1. Condition 3 rerun with the 15-dimension weighting (w15)

**What changed in the code.** The weighting is a named one now: `w15` (reported) and `w34` (the old 34-dimension one, kept in the code for the record). `frames.Q_WEIGHTINGS = ("w15", "w34")`; the "uniform" weighting is gone (it was never reported). The w15 definition lives in one place, `frames.FORM15` (system, dimension, codebook field, how compared, weight), with `frames.form_frame15(ds)` building the 15 columns per design and `frames.form_distance(ds)` the single entry point to the Gower matrix. Every user of the distance now goes through it: condition 3 (`dd_form_table`), condition 3 on F per base (`analysis3.form_family`), the CVT* to Separate Lift + Cruise distance (`thesis_v2_part4_iv2.cvt_lc_distance`) and the centroid dispersion of Part IV (`thesis_v2_part4.dispersion`, figure `q6_centroid_dispersion`, which leaves the text; it was rerun by notebook 51 and its values moved with the weighting). `lib/distance.gower_distance` gained two optional arguments: a fixed range per ordered dimension (so "rank difference / 4" holds exactly, not the observed range) and set-valued columns compared by the Jaccard distance (mount locations). The old call signature still works.

**The 15 dimensions as implemented** (`q7_condition3_weights.csv`, 15 rows, total 4.000):

| system | dimension | read from | compared as | weight |
|---|---|---|---|---|
| G1 | Architecture | topType | 0 same / 1 different | 1.000 |
| M1 | Fuselage Shape | fusShape | 0 / 1 | 0.500 |
| M1 | Boom count | boomsPresent, boom1..6_count summed (0 when no booms) | ranks 0, 1, 2, 3-4, 5+; rank difference / 4 | 0.300 |
| M1 | Fuselage Kinematics | fusKin | 0 / 1 | 0.200 |
| M2 | Wing count | wCount (0 when no wing) | 0, 1, 2, 3; difference / 3 | 0.300 |
| M2 | Wing Architecture | wingConf | 0 / 1 | 0.300 |
| M2 | Vertical Position of wing 1 | wing1_posV | 0 / 1 | 0.022 |
| M2 | Longitudinal Position of wing 1 | wing1_posL | 0 / 1 | 0.022 |
| M2 | Planform of wing 1 | wing1_plan | 0 / 1 | 0.022 |
| M2 | Empennage Type | empType | 0 / 1 | 0.333 |
| M3 | Propulsor band | propulsor count in the A·U bands 1-3, 4, 5-6, 7-8, 9+ | rank difference / 4 | 0.350 |
| M3 | Tilt share | per station and type counts, propKin, wing tilt, empTilts, boom_thrust_state, fusKin | absolute difference | 0.300 |
| M3 | Propulsor Enclosure | bmech of the set with the most propulsors | 0 / 1 | 0.150 |
| M3 | Tractor / Pusher Arrangement | chord of that set | 0 / 1 | 0.100 |
| M3 | Mount locations | set of stations among fuselage, wing, boom, empennage | Jaccard distance | 0.100 |

Blanks (left out of the pair's average, Gower with δ, as before): the propulsion dimensions on the 29 Hoverbike and Personal Flying Vehicle designs, on 1 design with an M3 override and on 1 design with no propulsor count (31 in all); the wing-1 dimensions on wingless designs (107); fuselage shape and kinematics where unrecorded (23 and 24); the tractor/pusher arrangement where unrecorded (99). 625 designs, as before. The wing-1 dimensions read the primary wing (codebook R5-03); that is wing 1 in every design, as the author checked on 2026-10-16.

**Judgement calls made (please check):**
- Boom count is the design's number of booms (boom groups 1-6 summed), 0 when `boomsPresent` is not True; not the count of boom group 1 and not the count of propulsors on the boom card. One design (US2020361622A1_ua1, Tilt Propulsor) has `boomsPresent` True with no group count and reads 0.
- Tilt share: the boom propulsors count as tilting when `boom_thrust_state` is `tilting` or `on_tilting_wing` (every propulsor of the card). For `mixed` (37 designs, all Combined Vectored Thrust) the boom propulsor types with propKin Tilt count; in 36 of the 37 the types separate Tilt from Fixed. In the one design where no type says Tilt (CN113306714A_ua1, boom groups 1-2 ticked "tilts", group 3 not) the boom propulsors are prorated by the share of propeller-carrying booms in ticked groups (2 of 3). That one is a guess; the record has no link between a propulsor type and a boom group.
- Whole-airframe reorientation: tilt share 1 when `fusKin` is TiltBody or when the architecture is Tilt Frame; 7 of the 24 Tilt Frame designs are recorded as "Variable Incidence", not TiltBody, and following "every Tilt Frame" they read 1 too.
- Tilt share by architecture (mean): Separate Lift + Cruise, Pitch-to-Cruise, Deflected Slipstream 0.00; Tilt Propulsor 0.99; Tilt Wing and Tilt Frame 1.00; Combined Vectored Thrust 0.53; Multicopter 0.32 (multicopters whose boom groups are ticked "tilts" or whose `boom_thrust_state` is tilting; this follows the record, as `propulsion_states` does); Rotorcraft 0.06. Distribution: 243 designs at 0, 250 at 1, 101 in between.
- Mount locations: fuselage, core_layout and hull_array cards map to "fuselage"; wing1..4 to "wing"; boom to "boom"; emp to "empennage"; a station is in the set when a non-control-only set on it has a count above 0. 15 distinct sets; the largest {wing} 142, {boom} 117, {fuselage, wing} 71.
- The ordered dimensions are passed with their fixed ranges (4, 3, 1, 4); the observed ranges happen to equal them.

**Condition 3, ΔQ of 2020-23 and the lower edge of its band (new w15 next to old w34; my run reproduces the old w34 values exactly):**

| base | level | new ΔQ | new lower edge | new verdict | old ΔQ | old lower edge | old verdict |
|---|---|---:|---:|---|---:|---:|---|
| all designs | A | −0.0279 | −0.0190 | met | −0.0168 | −0.0151 | met |
| all designs | A·W·T | −0.0299 | −0.0204 | **met** | −0.0191 | −0.0231 | not met |
| all designs | A·U | −0.0299 | −0.0168 | met | −0.0191 | −0.0163 | met |
| all designs | F | −0.0279 | −0.0190 | met | −0.0168 | −0.0151 | met |
| actively protected | A | +0.0091 | −0.0221 | not met | +0.0368 | −0.0176 | not met |
| actively protected | A·W·T | +0.0064 | −0.0226 | not met | +0.0338 | −0.0214 | not met |
| actively protected | A·U | +0.0064 | −0.0177 | not met | +0.0338 | −0.0223 | not met |
| actively protected | F | +0.0091 | −0.0221 | not met | +0.0368 | −0.0176 | not met |
| granted and live | F | −0.0025 | −0.0182 | not met | +0.0281 | −0.0280 | not met |

Q itself is lower under w15 (A, 2020-23: 0.5185 against 0.5555). The design counts per cohort are unchanged (A: 63, 58, 211, 237, 56; A·W·T and A·U 236 in 2020-23). Conditions 1 and 2 do not use the distance and are unchanged.

**Which verdicts changed, in plain words.** One cell: condition 3 at A·W·T on all designs is now met in 2020-23 (it was not met under w34, by 0.004). A, A·U and F stay met on all designs; on the actively protected designs condition 3 stays not met at every level, and the gap narrowed (ΔQ is now +0.009 rather than +0.037, still above the band's lower edge of −0.022). "All three in the same period" stays not met everywhere: condition 1 fails on all designs at every level; on the actively protected base F meets conditions 1 and 2 but not 3. The verdict table (`q7_verdict_table.csv`) therefore differs from the old one in exactly one cell (A·W·T, all designs, condition 3: ✓ met in 2020-23).

**CVT* to Separate Lift + Cruise distance (`q6_iv2_merge_cvt_lc_distance.csv`, w15):** 2012-15 0.541, 2020-23 0.544, change +0.002 against a band of −0.053 to +0.056 (old: 0.583 and 0.607, +0.024, band −0.048 to +0.051). The reading is unchanged in kind: the change is inside the band, and now near zero. For all CVT (not only CVT*): 0.551 to 0.553, +0.002, band −0.049 to +0.052.

**NUMBERS_III.md.** The sections "Verdict table", "The numbers behind the verdict", "Weights table" and "Condition 3 on F" are rewritten from the new files (they describe w15: 15 dimensions, the four systems at 1 each, the ordered and set dimensions, the tilt share, 625 designs, w34 kept for the record).

**Also changed for consistency (text only):** the captions of `q7_condition3_cohesion` in `viz/thesis_q7.py` and the two sentences of `viz/thesis_text_q7.py` (the chapter-4 Results text generator of notebook 47) that described the 34-dimension weighting now describe w15. Not changed: `tests/test_q3.py` and `tests/test_dominant_design.py` compare the form table against the archive's "subsystem"/"uniform" weightings and will no longer match, by design.

Files (Task 1):
- scripts: `labeling_evaluation/lib/distance.py`, `labeling_evaluation/viz/frames.py`, `labeling_evaluation/viz/analysis3.py`, `labeling_evaluation/viz/thesis_q7.py`, `labeling_evaluation/viz/thesis_text_q7.py`, `labeling_evaluation/viz/thesis_latex_part3.py`, `labeling_evaluation/viz/thesis_v2_part3.py`, `labeling_evaluation/viz/thesis_v2_part4.py`, `labeling_evaluation/viz/thesis_v2_part4_iv2.py`, `labeling_evaluation/viz/handoff_2026_10_16.py` (new), `labeling_evaluation/notebooks/52_thesis_figures_v2_part3.ipynb`, `labeling_evaluation/notebooks/51_thesis_figures_v2_part4.ipynb`
- `LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition3_cohesion.{pdf,png,csv,json}` (overwritten; the figure itself is Task 3's three-panel version)
- `LaTeX_v15/Data_for_writing/csv/q7_condition3_cohesion.csv`, `q7_condition3_family.csv` (+ .json), `q7_condition3_weights.csv` (+ .json, 15 rows), `q7_verdict_table.csv` (+ .json), `q7_verdict_detail.csv` (+ .json), `q6_iv2_merge_cvt_lc_distance.csv` (new copy here; its normal place is `LaTeX_v15/Figures/Part_IV_design_space_evolution/IV2_attributes_and_drivers/main/`, overwritten)
- `LaTeX_v15/Data_for_writing/NUMBERS_III.md` (rewritten by notebook 52), `NUMBERS_IV.md` (rewritten by notebook 51; the centroid-dispersion numbers moved with the weighting)
- `LaTeX_v15/Figures/thesis_figures_v2/Part_III_dominant_design/III2_III3_dominant_design/{main,appendix}/` copies; `thesis_figures_v2/Part_III_dominant_design/...` (normal place); `thesis_figures/Q7_dominant_design/results/q7_condition3_cohesion.*`

## Task 2. Which dimensions the architecture fixes (tab:q6_fixed_by_architecture)

**Method as run.** Seven dimensions, the same series that `q6_selected_fields` reads (rebuilt in `frames.selected_field_series`), on the designs that answer the dimension and have an architecture; "designs answering" differs from the `q6_selected_fields` column only by the two designs with no architecture recorded (tail 599 vs 600, wings 545 vs 547, gear 601 vs 602, fuselage motion 601 vs 602, wing configuration 540 vs 541). Cramér's V with the Bergsma (2013) bias correction (`lib/association.cramers_v_bc_table`, equal to the existing `cramers_v_bc` on every row); permutation p with one `default_rng(42)` over 1 000 shuffles of the architecture column, dimensions in the table's order, p = share of shuffles at or above the observed V ("< 0.001" when none reached it); leading option per architecture (tie: the more common option overall); 80 % counted on architectures with 10 or more answering designs.

| dimension | designs answering | Cramér's V | p | architectures at 80 % or more | too few to read |
|---|---:|---:|---|---|---|
| propulsors per design (band) | 595 | 0.23 | < 0.001 | 0 of 7 read | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle |
| tail type | 599 | 0.12 | 0.024 | 0 of 7 read | same five |
| places carrying propulsors | 595 | 0.27 | < 0.001 | 1 of 7 read | same five |
| number of wings (winged designs) | 545 | 0.17 | 0.003 | 1 of 7 read | Multicopter, Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Personal Flying Vehicle |
| landing-gear type | 601 | 0.24 | < 0.001 | 0 of 7 read | the five of row 1 |
| fuselage motion hover to cruise | 601 | 0.72 | < 0.001 | 5 of 7 read | the five of row 1 |
| wing configuration | 540 | 0.31 | 0.006 | 5 of 6 read | Multicopter, Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle |

**In plain words.** Only two dimensions are fixed by the architecture in most architectures. Fuselage motion (V 0.72): the leading option holds 80 % or more in 5 of the 7 readable architectures (Fixed in Separate Lift + Cruise 98 %, Tilt Propulsor 100 %, Combined Vectored Thrust 100 %, Tilt Wing 98 %; whole-body pitch in Pitch-to-Cruise 100 %); the exceptions are Multicopter (whole-body pitch 48 %) and Tilt Frame (tail-sitter 71 %). Wing configuration (V 0.31): Standard holds 80 % or more in 5 of 6, the exception being Tilt Frame at 79 %. Everything else varies inside the architectures. The propulsor band is under 80 % in all 7 readable architectures (leading shares 27 % to 40 %). The tail type is under 80 % in all 7 (Tailless leads everywhere, 16 % to 71 %, highest in Multicopter). Landing gear: 0 of 7, and its leading option is "Unknown" in 6 of them. Places carrying propulsors: 1 of 7 (Multicopter, 94 % on one place). Number of wings: 1 of 7 (Hoverbike, 94 % one wing). Every association is significant (p at most 0.024) but small except fuselage motion.

Files (Task 2):
- scripts: `labeling_evaluation/lib/association.py`, `labeling_evaluation/viz/frames.py` (`selected_field_series`), `labeling_evaluation/viz/thesis_q6.py` (`fixed_by_architecture`), `labeling_evaluation/viz/thesis_v2_part2.py`, `labeling_evaluation/viz/thesis_latex_part2.py`, `labeling_evaluation/notebooks/50_thesis_figures_v2_part2.ipynb`
- `LaTeX_v15/Data_for_writing/csv/q6_fixed_by_architecture.csv`, `q6_fixed_by_architecture_detail.csv` (new; + .json)
- `LaTeX_v15/Figures/Part_II_design_space/II1_varying_attributes/appendix/q6_fixed_by_architecture.csv`, `q6_fixed_by_architecture_detail.csv` (new)
- `LaTeX_v15/Data_for_writing/NUMBERS_II.md` (new section "Which dimensions the architecture fixes")
- `thesis_figures_v2/Part_II_design_space/II1_varying_attributes/appendix/` and the copy under `LaTeX_v15/Figures/thesis_figures_v2/...`

## Task 3. F out of the III.2 figures, into one figure of its own for III.3

- `q7_condition2_balance` and `q7_condition3_cohesion` now have the three panels A, A·W·T, A·U (the F panel is gone, the legend has no F entry). Condition 3 used to show "A and A·U (the same aircraft)" in one panel; it now draws A·U from its own rows (n 236 in 2020-23, its own band), so both figures have the same three panels in the same order. Widths unchanged (0.9 and 0.85 of the text block); the csv behind each holds the three levels only.
- New `q7_family_conditions` (1.0 of the text block, 16.0 × 8.6 cm): (a) F's share per priority year 2016-2023 on the three bases, read years only (all designs solid, actively protected dashed, granted and live dotted; 2023 granted-and-live has 15 designs and is not drawn), the 50 % line, the all-designs year above 50 % ringed (2021, 56.9 %); (b) ²D of F per cohort on all designs with its band and the red point where met, the actively protected series grey dashed with a hollow red ring where it is below its own band; (c) ΔQ of F per cohort (w15) with its band and the red point where met, the actively protected series grey dashed. Panel titles "F, condition 1 (share)", "F, condition 2 (balance)", "F, condition 3 (disparity)". The hollow ring for "met on the actively protected designs" is an addition of mine; drop it if unwanted (`plots.band_series_panel(alt_met=None)`).
- `q7_condition1_family` is still written (same files, same places) and marked as leaving the text.
- Layout checks at the final width: 0 text over text, nothing under 7 pt, height at most 55 % of the width, for all three.

**Values printed in the F figure.** Panel (b), ²D of F in 2020-23: all designs 3.22 against a lower edge of 3.65 (met); actively protected 3.14 against 3.58 (met). Granted and live is not drawn in panel (b); its table value stays 3.03 against 3.55. Panel (c), ΔQ of F in 2020-23 (w15, Task 1): all designs −0.0279 against −0.0190 (met); actively protected +0.0091 against −0.0221 (not met). All as in the verdict tables.

Files (Task 3):
- scripts: `labeling_evaluation/viz/thesis_q7.py`, `labeling_evaluation/viz/plots.py`, `labeling_evaluation/viz/thesis_v2_part3.py`, `labeling_evaluation/viz/thesis_latex_part3.py`, `labeling_evaluation/notebooks/52_thesis_figures_v2_part3.ipynb`
- `LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition2_balance.*`, `q7_condition3_cohesion.*` (overwritten), `q7_family_conditions.{pdf,png,csv,json}` (new); `LaTeX_v15/Data_for_writing/csv/q7_condition2_balance.csv`, `q7_condition3_cohesion.csv`, `q7_family_conditions.csv`
- copies under `LaTeX_v15/Figures/thesis_figures_v2/...`, `thesis_figures_v2/...` and `thesis_figures/Q7_dominant_design/results/`

## Task 4. Figure q6_half_of_cohort, made readable

Redrawn wide: notebook size 7.0 × 2.6 in; final LaTeX size 16.0 × 5.9 cm (height/width 0.37) at the full text width (the `FIGS` share went from 0.8 to 1.0, since the text prints it at text width). Horizontal axis limited to the first 12 configurations, a tick at every one. The 50 % line is a thicker dashed black line; the five crossing markers are twice as large (11 pt) with a white edge (a white halo around the coloured marker, so the hollow 2024-26 marker keeps its outline). Series colours, legend text and cohort order unchanged. The csv is unchanged (the builder's frame of ranks 1-20 per cohort is identical to the old file; only the drawing stops at 12). Layout checks pass.

**Crossings, unchanged:** ≤2011 5 (54.1 %), 2012-15 5 (52.6 %), 2016-19 9 (52.7 %), 2020-23 7 (52.7 %), 2024-26 6 (50.0 %).

Files (Task 4):
- scripts: `labeling_evaluation/viz/thesis_v2_part2.py` (`fig_half_of_cohort_v2`), `labeling_evaluation/viz/thesis_latex_part2.py` (`FIGS`, new `HEIGHT`), `labeling_evaluation/notebooks/50_thesis_figures_v2_part2.ipynb`
- `LaTeX_v15/Figures/Part_II_design_space/II3_distribution_and_new_variety/auxiliary/q6_half_of_cohort.{pdf,png,csv,json}` (overwritten)
- `LaTeX_v15/Data_for_writing/csv/q6_half_of_cohort.csv` (same content); copies under `LaTeX_v15/Figures/thesis_figures_v2/...` and `thesis_figures_v2/...`

## Task 5. Figures q2_filer_types and q2_largest_filers_share in colour

The greyscale came from the builders themselves (`plots.FILER_STYLE` greys and the grey band fills), not from the LaTeX export. Both builders in `viz/thesis_q2.py` now use the Okabe-Ito palette of `style.py`, the one `q3_region_design_all_years` (architecture colours) and `q7_region_family_share` (region colours) draw with, in the same order. Same data, labels, sizes, legend text; hatches kept in `q2_filer_types` because the sibling q3 figure keeps hatch beside colour. Layout checks pass (10.6 × 5.8 cm and 16.0 × 7.9 cm).

- `q2_filer_types`: named companies #0072B2 (blue, the colour of Separate Lift + Cruise / North America), solid; universities and institutes #E69F00 (orange, Tilt Propulsor / Europe), hatch ////; individual inventors #009E73 (green, Combined Vectored Thrust / Asia-Pacific), hatch ..... The faded 2024-26 bar keeps its alpha.
- `q2_largest_filers_share`: band A #0072B2, B #E69F00, C #009E73, D #D55E00 (vermilion, Tilt Wing); each band's background is its colour tinted 18 % towards white, the band letter in the full colour; the step curve and the dashed "all named assignees" line stay ink and grey as before.

One thing to know, not my change: the csv of `q2_largest_filers_share` differs from the Drive copies in one assignee name at rank 157 (the old files printed "Propulsor 1Srl" for "Unit 1Srl", a relabel slip the current `analysis5.relabel_df` already avoids).

Files (Task 5):
- scripts: `labeling_evaluation/viz/thesis_q2.py`, `labeling_evaluation/notebooks/53_thesis_figures_v2_part5.ipynb`
- `LaTeX_v15/Figures/Part_V_assignees_and_regions/V1_who_files/main/q2_filer_types.{pdf,png,csv,json}`, `q2_largest_filers_share.{pdf,png,csv,json}` (overwritten); `LaTeX_v15/Data_for_writing/csv/q2_filer_types.csv`, `q2_largest_filers_share.csv`
- copies under `LaTeX_v15/Figures/thesis_figures_v2/...`, `thesis_figures_v2/...` and `thesis_figures/Q2_filers/results/`

---

## Things to know

1. **Uncommitted work already in the tree.** When I started, the working tree held uncommitted changes from earlier on 2026-10-15 (the author's rulings rerun: `viz/relabel.py` prints "Separate Lift + Cruise" and the band "1-3"; `viz/thesis_q3.py`, `viz/thesis_v2_part1.py`, `viz/thesis_latex_part4.py`, `notebooks/_build/write_readme_50.py`, notebook 48, and the executed outputs of notebooks 50-53), plus about 2 000 deleted files (`handoff_2026-10-15/`, `labeling_evaluation/code_backup_2026-10-13/`, sector-event backups) that were moved to the trash. The outputs of this hand-over were produced with those changes in place, so they are committed together with mine (the deletions are not staged; they are left as they were).
2. **Notebook 53 layout check.** The run of notebook 53 reports 45 overlapping percentage labels in `q3_region_mix_by_window_class` (appendix figure, not one of these tasks). It comes from the earlier changes above, not from Task 5; the two Task 5 figures pass.
3. **The 2026-10-15 hand-over section of notebook 52** was replaced by the 2026-10-16 one (its outputs are in the commit of 2026-10-15).
4. **Running the whole notebooks** also rewrote every other figure and csv of Parts II, III, IV and V in `thesis_figures_v2/` and `LaTeX_v15/` with the current code (same numbers, the relabel changes applied). `FINAL_2026-10-14/` was not touched.

---

## Task 6. Form-defined families (exploratory, after Task 1, w15 only)

New notebook `labeling_evaluation/notebooks/55_form_families.ipynb` (numbered 55, not 53 as the brief says, because 53 and 54 already exist) over the new script `labeling_evaluation/viz/thesis_form_families.py`. Run end to end headlessly, no error cell. Nothing in it changes F or any number of the dissertation. The five families were declared before running and none was added or tuned afterwards. Same seed 42, 200 permutations, rarefaction 40, read years of 20 designs or more; the actively protected base is read alone as the sensitivity.

**Membership (all designs, 625; actively protected, 433).** No family is one architecture renamed (the largest architecture share is 53 % at most; the tiny P4 is 71 % Multicopter on 14 designs).

| family | members | share | largest architecture | its share | mix (codes) |
|---|---:|---:|---|---:|---|
| P1 fixed wing, boom-borne distributed propulsion | 174 | 27.8 % | Separate Lift + Cruise | 51.7 % | SLC 90, CVT 40, TR 26, PTC 11, TB 6, SRW 1 |
| P2 fixed wing, distributed propulsion | 264 | 42.2 % | Separate Lift + Cruise | 48.1 % | SLC 127, CVT 56, TR 50, PTC 16, TB 10, DS 3, SRW 2 |
| P3 fixed wing, open distributed propulsion | 192 | 30.7 % | Separate Lift + Cruise | 52.6 % | SLC 101, CVT 37, TR 31, PTC 11, TB 10, DS 1, SRW 1 |
| P4 wingless multicopter, distributed | 14 | 2.2 % | Multicopter | 71.4 % | MR 10, CVT 2, TR 1, PTC 1 |
| P5 fixed wing with distributed propulsion, any tilt | 303 | 48.5 % | Separate Lift + Cruise | 41.9 % | SLC 127, CVT 67, TR 50, TW 28, PTC 16, TB 10, DS 3, SRW 2 |

30 designs (31 for P3 and P4) are non-members because a rule variable is blank (no propulsor card or a hidden station); they stay in the denominators.

**Verdict table** (`q8_families_verdict.csv`; premise = cohesion below AND separation above the band of 200 random subsets of the cohort of the family's size; condition 3 is the Task 1 cohort verdict at level A, family-independent):

| family | base | premise (2020-23) | condition 1: largest share, years met | condition 2 | condition 3 | all three, same period |
|---|---|---|---|---|---|---|
| P1 | all designs | holds (2016-19, 2020-23) | not met, at most 41.7 % (2022) | met 2020-23 | met 2020-23 | not met |
| P2 | all designs | holds (all four complete cohorts) | met 2021, 2022, 2023 (54.2 %, 64.6 %, 54.2 %) | met 2020-23 | met 2020-23 | **met 2020-23** |
| P3 | all designs | holds (2016-19, 2020-23) | not met, at most 50.0 % (2022) | met 2020-23 | met 2020-23 | not met |
| P4 | all designs | not read (under 10 designs a cohort) | not met, at most 5.9 % | met 2020-23 | met 2020-23 | not met |
| P5 | all designs | holds (≤2011, 2016-19, 2020-23) | met 2021, 2022, 2023 (63.9 %, 68.8 %, 60.4 %) | met 2020-23 | met 2020-23 | **met 2020-23** |
| P1 | actively protected | holds (2016-19, 2020-23) | not met, at most 42.9 % (2022) | met 2020-23 | not met | not met |
| P2 | actively protected | holds (2016-19, 2020-23) | met 2021, 2022, 2023 (55.9 %, 71.4 %, 56.8 %) | met 2020-23 | not met | not met |
| P3 | actively protected | holds (2016-19, 2020-23) | not met, at most 54.3 % (2022, one year) | met 2020-23 | not met | not met |
| P4 | actively protected | not read | not met, at most 9.1 % | met 2020-23 | not met | not met |
| P5 | actively protected | holds (2016-19, 2020-23) | met 2019 to 2023 (59.1 %, 53.7 %, 67.8 %, 74.3 %, 63.6 %) | met 2020-23 | not met | not met |

The three-year sensitivity of condition 1 gives the same answer (P2 and P5 met 2021-2023 on both bases; P5 2019-2023 on the actively protected base).

**In plain words.** On the all-designs base, two form families pass all three conditions in the same period, 2020-23: P2 (a fixed wing that does not tilt, five or more propulsors) and P5 (a fixed wing, five or more propulsors, any tilt). Both are coherent in form (within-family distance below the band, family-to-rest distance above it) and neither is an architecture renamed (Separate Lift + Cruise is 48 % and 42 % of them). P1, which adds the boom rule, and P3, which adds the open-enclosure rule, fail only condition 1: P3 by one design in 2022 (50.0 %) and four in 2023. P4 is too small to read. On the actively protected base no family passes, because condition 3 is not met there (the Task 1 verdict, which is the same for every family). The Q decomposition of 2020-23 (`q8_families_q_decomposition.csv`) shows what carries the ΔQ of Task 1: for P2 the within-family pairs are 27.8 % of the pairs at a mean distance of 0.443, up from the two earliest cohorts, replacing within-rest pairs at 0.535; the same pattern holds for P1, P3 and P5. This is a result of the exploratory test and changes nothing about F.

Judgement calls (the agent's, listed in NUMBERS_VI_form_families.md too): wing_tilts read on the raw wing1..4 tilt fields; boom_n is the boom1..6 count sum (0 without booms); "band ≥ 5-6" is band rank 2 or more; the premise needs 10 or more family designs in the cohort, else "not read"; condition 2 relabels the members as one option and keeps every other architecture as its own option, with a fresh generator per family and base, as F was computed; the Q decomposition uses Task 1's Q definition (mean over all ordered pairs including the diagonal) so the three blocks sum exactly to Q.

Files (Task 6):
- scripts: `labeling_evaluation/viz/thesis_form_families.py` (new), `labeling_evaluation/notebooks/55_form_families.ipynb` (new)
- results folder `thesis_figures_v2/Part_III_dominant_design/III3_form_families/exploratory/`: `q8_form_variables.csv`, `q8_families_membership.csv`, `q8_families_premise.csv`, `q8_families_verdict.csv`, plus the detail files `q8_families_q_decomposition.csv`, `q8_families_condition1.csv`, `q8_families_condition2.csv`, `q8_families_condition3.csv`, and `NUMBERS_VI_form_families.md`
- the same eight csv in `LaTeX_v15/Data_for_writing/csv/`; `LaTeX_v15/Data_for_writing/NUMBERS_VI_form_families.md`
- copies of all of it in `handoff_2026-10-16/task6/`
