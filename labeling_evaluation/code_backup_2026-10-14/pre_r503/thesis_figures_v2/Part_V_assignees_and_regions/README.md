# Part V: assignees and regions

Written by notebook 53 (`notebooks/_build/build_53.py`). One file per graph or table: `<group>/<role>/<name>.{pdf,png,csv,json}`.

## V1_who_files

- `q2_filer_types` (main, figure): Assignee types, all years and per cohort *(Figure 16 (ii))*
- `q2_largest_filers_share` (main, figure): Cumulative share held by the largest assignees *(Figure 16 (i))*
- `q2_largest_filer_per_class` (main, table): Largest assignee of each architecture *(Figure 17 (i))*

## V2_new_and_returning_assignees

- `q2_first_vs_returning_filers` (appendix, figure): First-time and returning assignees per cohort *(Figure 16 (iii))*
- `q2_entrant_class_mix` (appendix, figure): Architectures of first-time and returning assignees *(Figure 19 (i))*
- `q2_tilt_wing_entrants` (appendix, figure): Tilt Wing among the entering assignees *(Figure 19 (ii))*

## V3_regions_what_and_when

- `q3_region_design_all_years` (main, figure): What each region files, all years *(Figure 22 (all years bars))*
- `q3_region_mix_by_window_class` (appendix, figure): Architecture per region and cohort *(Figure 22 (i), per-cohort bars)*
- `q3_region_mix_by_window_units` (appendix, figure): Propulsor units per region and cohort *(Figure 22 (ii), per-cohort bars)*
- `q3_region_mix_by_window_tilting` (appendix, figure): Tilting share per region and cohort *(Figure 22 (iii), per-cohort bars)*
- `q3_region_entry_lag` (main, figure): Years after North America, per architecture *(Figure 23 (ii))*
- `q3_region_countries` (appendix, figure): The applicant countries behind the regions *(Figure 21)*

## V4_regions_and_family_F

- `q7_region_family_share` (main, figure): Family F share per region and cohort *(Figure 24 (i))*
- `q7_region_lean_without_largest_filer` (appendix, figure): Tilting lean with and without the largest assignee *(Figure 24 (ii))*

## Labels (relabel only; data, cohorts, builders and layout unchanged)

Multirotor → Multicopter; Tilt Body → Tilt Frame; Tilt Rotor → Tilt Propulsor; filer, firm, organisation → assignee; window → cohort; class → architecture; Q2, Q3, Part V → Analysis V. File names are unchanged, including those with filer and window in them.
The notebook prints, under each figure, the words changed in it.

## Removed marks

- The hollow AAM Reality Index diamonds and their legend in `q2_largest_filers_share`, and the AAM text in its caption and source (JSON); the CSV column 'rated by the index' is gone.

## Not in this folder, not regenerated, not deleted

- `q3_firm_successions`, `q7_region_firm_proximity` and every funding figure: cut from the dissertation; their files stay in `thesis_figures/`.
