# labeling_evaluation — the thesis figures, tables and numbers of the Labelling Analysis

Every figure, table and number of the 45-page Labelling Analysis (2026-09-30), rebuilt from notebooks you can edit.

## Run it

Run the notebooks in order (each also runs alone):

| Notebook | What it makes | Output folder (Drive, `1639_LABELLED/1_labelling_analysis/labelling_analysis_thesis/`) |
|---|---|---|
| 39_style_proof | the one-page style sample | `style/` |
| 40_q1_growth_protection_fidelity | Figures 1–5, Tables 1–5, 96 numbers | `q1_growth_protection_fidelity/` |
| 41_q2_design_space | Figures 6–9, Tables 6–7, 46 numbers | `q2_design_space/` |
| 42_q3_evolution_dominant_design | Figures 10–15, Tables 8–9, 78 numbers | `q3_evolution_dominant_design/` |
| 43_q4_filers | Figures 16–20, 56 numbers | `q4_filers/` |
| 44_q5_regions | Figures 21–24, Table 10, 47 numbers | `q5_regions/` |
| 45_export_latex | everything above, ready for LaTeX | `latex/` |

Each question notebook ends with a check: every number and table against the 45-page document. A difference is either
labelled with its cause (e.g. your SRW → LC ruling) or the notebook stops.

To change a notebook's structure, edit its generator in `notebooks/_build/build_4N.py` and run it with `--run`
(the notebooks are generated, so a hand edit is overwritten the next time the generator runs).

## Where things are

- `labelling_analysis.yaml` — every path and constant. `python -m viz.config` prints and checks the paths.
- `INPUTS.md` — what each input gives and who made it (⚠ = to review); the notebook 04 pipeline behind the labels.
- `METHOD_NOTES.md` — what the rebuild found in the method and in the document's text: your decisions.
- `lib/` — the equations (statistics only), each with its formula in the docstring.
- `viz/` — data loading, data wrangling, style, charts, saving, checks, LaTeX export.
- `tests/` — 115 tests: every equation and helper equals the code that produced the document (`python3 -m pytest -q tests/`).
- `assets/` — the outside data (AAM Reality Index, baselines, sector events, …).
- `THESIS_PLAN.md` — how this folder was planned and built.

In LaTeX: copy `latex/` next to the thesis, add `\usepackage{graphicx,booktabs,amssymb}`, then `\input{latex/figures.tex}`
or copy single blocks from it. `latex/FIGURE_INDEX.md` lists every item with its label and source. `tables.tex` includes
the document's 10 tables plus the supporting tables (the plotted data of some figures); keep the ones you need.


## Final rebuild 2026-10-15: printed wording (CONVENTIONS.md term rules)

Labels only: no number, computation or layout choice changed. Every figure, table and number file of Parts I-V was rebuilt by re-running notebooks 48, 50, 52, 51 and 53 (51 has a new last cell for `q6_iv2_merge_cvt_lc` and `q6_iv2_split_tp`); file names and folders are unchanged. Before the rebuild the outputs were copied to `code_backup_2026-10-14/final_rebuild/`.

**Files changed (code).** New `viz/relabel.py`; `viz/__init__.py` installs it (one line); notebook 51 (one cell added). No other source file was edited. The term rules are applied where text leaves the code: every matplotlib text (titles, axis, tick, legend, annotation), the headers and text cells of every CSV written under the output folders, and every .json and .md written there. Rules: propulsor unit(s) -> propulsor(s); units on booms -> propulsors on booms; fixed units -> fixed propulsors; lift units -> lift propulsors; any other "unit(s)" -> propulsor(s); the lowest band 1-3 -> 0-3; C·W·T -> A·W·T; C·U -> A·U; class -> architecture; firm and filer -> assignee (index firms stays; first-time firm -> new assignee); out of force -> not actively protected; Multirotor -> Multicopter; evtol.news -> VFS eVTOL directory; window -> cohort; archetype -> configuration; aircraft -> design(s) in figures. "lift/thrust unit" (EASA) is untouched. Where a renamed CSV header would repeat another column the header keeps its name (none occurred).

**Check that no number changed.** All 124 CSV files of `LaTeX_v15` and `thesis_figures_v2`: the previous build with the rules applied to it equals the new build cell for cell and header for header. The .md and .json files differ only by the generation date of NUMBERS_I and the MANIFEST lines for the new files.

**Grep result.** Over every exported .csv, .json, .md and the text of every PDF (289 files): no hit for "propulsor unit", "propulsor-unit", "propulsive unit", "units on booms", "fixed units", "1-3" (band), "C·W·T", "C·U", "class", "firm" (except index firm), "filer", "out of force", "Multirotor", "evtol.news", "window", "archetype", "unit(s)", and no "aircraft" in any figure text. The only hits are the READMEs themselves, which name the old terms to say they are banned, and "aircraft" as a count column header in CSV and .md tables (the rule covers axes). Over the code (`viz/`, `lib/`, excluding PRE_ backups) the grep is NOT empty: the old words remain in docstrings, comments, internal data keys and printed-string literals (for example "propulsive units (median)" is a column key of the driver frame, and `frames.UNIT_BANDS` still builds "1-3"); they are relabelled on the way out, so they never reach a file. Renaming them at source would change data keys read by other code, which this labels-only pass did not do.

**Layout.** Every figure passes the layout check of its notebook (no text over text, nothing under 7 pt, inside the canvas). The shorter wording moved the automatic label placement in three figures (`q6_configuration_core`, `q6_iv2_merge_cvt_lc`, `q6_half_of_cohort`): the labels sit in slightly different places, none overlaps. No tick spacing changed. Cohort tick labels in Part V still use the short forms 12-15 / 16-19 / 20-23 (an earlier layout choice, left as it was).

**625 against 627.** The dataset has 627 unique designs (funnel and text). The form-distance figures (condition 3, the centre and disparity figure) draw 625: Rao's Q needs an architecture to place a design in a level, and two designs have none recorded (`CN109263914A_ua1`, `CN109263949A_ua1`, both priority year 2018), so they drop out of the form distance; 2016-19 shows 211 there against 213 in the architecture shares.
