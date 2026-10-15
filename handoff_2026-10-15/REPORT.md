# Hand-over 2026-10-15: three figure and table tasks

All three tasks are done. Every output was written by running notebook 52 (`labeling_evaluation/notebooks/52_thesis_figures_v2_part3.ipynb`) end to end. A new last section of that notebook, "Hand-over 2026-10-15", writes the extra copies listed below. No .tex file was edited and Thesis.pdf was not rebuilt.

**Where things are.** The dissertation repository (the one with Thesis.pdf and the .tex files) is not on this computer. Here, `LaTeX_v15/` is the export folder next to the other thesis outputs:

    D = /mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED/1_labelling_analysis/labelling_analysis_thesis

All `LaTeX_v15/...` paths below are under `D`. To use them in the dissertation, copy them over the dissertation repository's `LaTeX_v15/`. The paths are the same. `FINAL_2026-10-14/` and the old folders were not touched.

Files in each `taskN/` folder:
- `<name>.pdf/.png/.csv/.json` are the LaTeX_v15 versions (final width in the text block).
- `<name>_v2.*` are the copies in `thesis_figures_v2`.
- `<name>_q7results.*` are the copies in `thesis_figures/Q7_dominant_design/results`.
- The changed scripts are copied in full.

---

## Task 1. Architecture shares per cohort, smallest joined into "Other"

**Which categories were joined.** These are the totals over the four complete cohorts (≤2011, 2012-15, 2016-19, 2020-23), counted from the data:

| category | aircraft |
|---|---:|
| no architecture recorded (the old "Other") | 2 |
| Deflected Slipstream | 4 |
| Stopped/Slowed Rotor Wing | 6 |
| Rotorcraft | 8 |
| Personal Flying Vehicle | 9 |
| *Hoverbike (kept)* | *18* |
| *Tilt Frame / Pitch-to-Cruise (kept)* | *22 each* |

The five smallest went into "Other". I kept Hoverbike separate: with 18 aircraft it sits much closer to Tilt Frame and Pitch-to-Cruise (22 each) than to Personal Flying Vehicle (9), so it is not clearly in the same range.

**Judgement call.** The brief also said "keep the 6 to 7 largest". With five joined, the figure keeps **8** architectures (Separate Lift + Cruise, Tilt Propulsor, Combined Vectored Thrust, Tilt Wing, Multicopter, Tilt Frame, Pitch-to-Cruise, Hoverbike) plus "Other", so 9 categories in all instead of 13. Only 7 architectures would remain if Hoverbike were joined too. That is a one-line change: `JOIN_N = 6` in `viz/thesis_v2_part3.py`, then rerun notebook 52.

**New share of "Other" per cohort:**

| cohort | designs | "Other" share |
|---|---:|---:|
| ≤2011 | 63 | 7.9 % (5 aircraft) |
| 2012-15 | 58 | 1.7 % (1) |
| 2016-19 | 213 | 5.6 % (12) |
| 2020-23 | 237 | 4.6 % (11) |
| 2024-26 (partial) | 56 | 7.1 % (4) |

Every cohort's shares still add up to 1. The cohort sizes are unchanged (63, 58, 213, 237, 56).

**Figure changes:**
- "Other" is drawn in neutral grey (#d0d0d0, the existing style for Other). The other architectures keep their colours and hatches.
- The legend uses full names only (e.g. "Separate Lift + Cruise", "Tilt Propulsor", "Multicopter"), without the short codes.
- There is no title or caption inside the figure.
- The figure keeps its file name, and the LaTeX label `fig:q6_class_shares_by_window` needs no change.
- The csv now has the columns SLC, TR, CVT, TW, MR, TB, PTC, HB, Other, designs. These are internal codes, as before.

## Task 2. Spearman test over 2016-2023 added to tab:q6_share_trend

The 2016-23 test uses the same yearly shares as the all-years test: each architecture's share of the priority year's aircraft that have an architecture recorded. It is computed in the same function (`analysis3.rho_table`), restricted to the eight years 2016 to 2023, one point per year. The "years of 20+" columns were dropped. The all-years columns are unchanged.

| architecture | aircraft | rho, 2008-23 | p, 2008-23 | rho, 2016-23 | p, 2016-23 |
|---|---:|---:|---:|---:|---:|
| Separate Lift + Cruise | 142 | 0.443 | 0.09 | 0.515 | 0.19 |
| Tilt Propulsor | 132 | −0.675 | 0.004 | −0.357 | 0.39 |
| Combined Vectored Thrust | 93 | 0.255 | 0.34 | 0.548 | 0.16 |
| Tilt Wing | 51 | −0.169 | 0.53 | −0.548 | 0.16 |
| Multicopter | 37 | 0.074 | 0.78 | −0.476 | 0.23 |
| Pitch-to-Cruise | 22 | 0.472 | 0.07 | 0.204 | 0.63 |
| Tilt Frame | 22 | −0.003 | 0.99 | −0.286 | 0.49 |

Aircraft per priority year (those with an architecture recorded): 2016: 34, 2017: 52, 2018: 66, 2019: 59, 2020: 69, 2021: 72, 2022: 48, 2023: 48.

**What it shows:**
- No trend is detected on 2016-2023: every p is 0.16 or above.
- The Tilt Propulsor fall does not remain. It is detected over 2008-2023 (rho −0.675, p 0.004), but on 2016-2023 alone rho is −0.357 with p 0.39. The fall happened mostly before 2016.
- With only eight points, a test can detect only a strong monotonic trend: |rho| needs to be about 0.74 or more for p below 0.05.

**Note.** The four years 2016-19 hold 211 aircraft, while the 2016-19 cohort holds 213. This is the same difference that already existed between the yearly and cohort counts. I did not change it.

## Task 3. F set apart as exploratory in q7_condition2_balance and q7_condition3_cohesion

**How F is drawn now:**
- Neutral grey (#8c8c8c), dashed line, hollow markers.
- F's "condition met" point is a hollow red ring instead of the filled red dot.
- It is labelled "F (exploratory, III.3)" in the panel title and in the legend.
- Condition 2: F was already the last of the four panels (A, A·W·T, A·U, F). Only its style and title changed.
- Condition 3: F used to share the left panel ("A, A·U and F, the same aircraft"). It now has its own third panel, drawn last. The left panel is now titled "A and A·U (the same aircraft)".
- With three panels, the cohort tick labels would overlap, so they are rotated 90° in all three panels (as in condition 2) and read "20–23, n 237".
- Colours, order, bands and red points of A, A·W·T and A·U are unchanged.
- No computation, band, rarefaction (40), weighting or base was touched. The csv files of both figures are byte-identical to the ones before the change.

**Printed values, checked against the csv:**

| check | expected | csv |
|---|---|---|
| F ²D 2020-23 vs band lower edge | 3.22 vs 3.65 | **3.22 vs 3.65** ✓ |
| ΔQ 2020-23, A | −0.017 vs −0.015 | **−0.0168 vs −0.0151** ✓ |
| ΔQ 2020-23, F | −0.017 vs −0.015 | **−0.0168 vs −0.0151** ✓ |
| ΔQ 2020-23, A·W·T | −0.019 vs −0.023 | **−0.0191 vs −0.0231** ✓ |
| ΔQ 2020-23, A·U | −0.017 vs −0.015 | **−0.0191 vs −0.0163** ✗ differs |

**To check: A·U in condition 3.** The csv row for A·U does not match the "A, A·U and F" grouping:
- It holds 236 aircraft in 2020-23 (A has 237).
- ΔQ is −0.0191 against a lower edge of −0.0163, and the row is marked below the band.
- This was already in the csv before today, so it is not caused by this change. I did not "fix" it.
- The figure draws the A row in the "A and A·U" panel, as before.
- Please check whether the text and the panel title ("the same aircraft") should treat A·U as identical to A.

---

## Every file changed or overwritten

**Scripts (repository `eVTOL-Visual-Evaluation`):**
- `labeling_evaluation/viz/thesis_v2_part3.py`: Task 1 (`JOIN_N`, `joined_shares`, the figure) and Task 2 (the table columns), plus the F panel title (Task 3).
- `labeling_evaluation/viz/analysis3.py`: Task 2 (`RHO_LATE_FIRST`, the 2016-23 rho and p in `rho_table`).
- `labeling_evaluation/viz/thesis_q7.py`: Task 3 (F's style, the third condition-3 panel, legend, titles).
- `labeling_evaluation/viz/plots.py`: Task 3 (`EXPLORE`; an `exploratory` option in `balance_panel` and `cohesion_panel`, off by default).
- `labeling_evaluation/notebooks/52_thesis_figures_v2_part3.ipynb`: the new "Hand-over 2026-10-15" section; rerun end to end. The backup before the change is `52_thesis_figures_v2_part3.PRE_HANDOFF_20261015.ipynb`.
- `handoff_2026-10-15/` (this folder).

**Outputs (under `D`). Overwritten:**
- `LaTeX_v15/Figures/Part_III_dominant_design/III1_architecture_shares/main/q6_architecture_shares_by_cohort.pdf`
- `LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition2_balance.pdf`
- `LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition3_cohesion.pdf`
- `LaTeX_v15/Data_for_writing/csv/q6_architecture_shares_by_cohort.csv`
- `LaTeX_v15/Data_for_writing/csv/q6_share_trend_spearman.csv`
- `LaTeX_v15/Data_for_writing/NUMBERS_III.md` (the Spearman table now shows the 2016-23 columns)
- `thesis_figures_v2/Part_III_dominant_design/III1_architecture_shares/main/q6_architecture_shares_by_cohort.{pdf,png,csv,json}`
- `thesis_figures_v2/Part_III_dominant_design/III1_architecture_shares/main/q6_share_trend_spearman.{csv,json}`
- `thesis_figures_v2/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition2_balance.{pdf,png,csv,json}`
- `thesis_figures_v2/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition3_cohesion.{pdf,png,csv,json}`

**Outputs (under `D`). New:**
- `LaTeX_v15/Figures/Part_III_dominant_design/III1_architecture_shares/main/q6_architecture_shares_by_cohort.{png,csv,json}`
- `LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/q7_condition2_balance.{png,csv,json}` and `q7_condition3_cohesion.{png,csv,json}`
- `LaTeX_v15/Data_for_writing/csv/q6_share_trend_spearman.json`
- `LaTeX_v15/Figures/analysis/q7_condition2_balance.pdf` and `q7_condition3_cohesion.pdf`. This folder did not exist here; in the dissertation repository it already does, so copy them over.
- `thesis_figures/Q7_dominant_design/results/q7_condition2_balance.{pdf,png,csv,json}` and `q7_condition3_cohesion.{pdf,png,csv,json}`. This folder was empty here, because the old Q7 folder had been moved to `_superseded_2026-10-16/`. The files are written by the builder and writer that notebook 46 uses.

**Rewritten by the notebook run with identical content:** the rest of Part III (the other figures and tables of notebook 52). Their csv and json files are byte-identical to before.

**Not caused by this run.** While notebook 52 was running, something else wrote these files:
- `LaTeX_v15/Figures/Part_IV_design_space_evolution/IV1_layout_convergence/main/q6_leading_layout_by_architecture.pdf`
- six Part IV lines appended to `LaTeX_v15/Data_for_writing/MANIFEST.md`

At the same time, notebooks 50, 51 and 53 changed in the repository. Notebook 52 has no Part IV code, so this was probably another session running notebook 51.

## What was committed

- `handoff_2026-10-15/`
- `viz/analysis3.py`, `viz/plots.py`, `viz/thesis_q7.py`, `notebooks/52_thesis_figures_v2_part3.ipynb`. Each was committed as a whole file. `thesis_q7.py` also carries one earlier uncommitted label change of yours (the condition-1 y-axis label).
- `viz/thesis_v2_part3.py`: only this hand-over's edits, applied to the committed version. The file on disk also holds uncommitted edits from the 2026-10-15 rerun, and they depend on an uncommitted `viz/relabel.py` (`directory_builder`). Committing the whole file would break the committed code, so those edits stay uncommitted. The full working version is in `task1/` to `task3/`.
- The output folders are outside the repository (`*/outputs/**` is also git-ignored), so only the copies in this folder are in git.
