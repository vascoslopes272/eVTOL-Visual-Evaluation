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
