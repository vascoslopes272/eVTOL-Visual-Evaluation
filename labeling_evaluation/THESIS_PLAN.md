# Thesis figures and tables — organisation and plan (revised 2026-10-01, second pass)

Input: the 45-page document titled "Labelling Analysis in brief" (LABELLING_ANALYSIS_BRIEF.pdf, rendered
2026-09-30 18:42; no later file exists on this machine, so a copy saved at 19:58 is the same render).
It is the whole analysis that goes into the thesis, not a summary of something else: five questions,
24 figures, 10 tables, and 953 numbers quoted in its Method / Results / Answer text (placeholders
resolved from ~480 computed tables).

**Scope rule (author, 2026-10-01): everything in that document that is computed — figure, table or
number in the text — is computed in a notebook cell, from a lib function, so the author can change it.**
No number in the thesis comes from a file the notebooks did not write.

## 1. Folders (revised 2026-10-01, third pass)

### Code — the old repo content in `archive/`, a fresh `labeling_evaluation/` for the thesis (author, 2026-10-01)

```
eVTOL-Visual-Evaluation/
├── archive/                        everything that was in the repo before 2026-10-01, moved as-is (git mv):
│   ├── labeling_evaluation/        the engine of the 45-page document (src/dataset_facts, scripts, config.yaml,
│   │                               notebook 10, assets/external); still runs from here, writes to the renamed Drive folder
│   ├── docs/  scripts/  README.md  the earlier reports and PDF renderers
├── requirements.txt
└── labeling_evaluation/            NEW, self-contained (imports nothing from archive/)
    ├── labelling_analysis.yaml                 every path, constant and the figure/table register for the thesis
    ├── THESIS_PLAN.md
    │
    ├── lib/                        NEW — SCIENCE ONLY (pure functions, formula in the docstring)
    │   ├── diversity.py            Hill numbers, rarefaction, Chao1 / jackknife
    │   ├── distance.py             Gower distance, proximity, Jaccard
    │   ├── dominant_design.py      conditions 1–3, permutation band, verdict
    │   ├── association.py          Cramér's V (bias-corrected), chi-square, Mann–Whitney, Spearman, BH
    │   ├── intervals.py            Wilson interval, bootstrap
    │   ├── concentration.py        HHI, firm leverage, one-vote-per-filer
    │   ├── growth.py               doubling time, turning point, B64 normalisation
    │   ├── regional.py             location quotient, lead/lag
    │   └── drivers.py              trace drift, couplings, verdict rules
    │
    ├── viz/                        NEW — VISUAL + HELPERS (name is free; "viz" proposed)
    │   ├── config.py               read labelling_analysis.yaml, resolve paths, assert every input exists
    │   ├── data.py                 load the master dataset and the external assets
    │   ├── frames.py               windows, class folding, display names (wrangling, no science)
    │   ├── style.py                SciencePlots base + thesis.mplstyle, class colour/marker/dash/hatch, sizes
    │   ├── plots.py                chart primitives
    │   ├── tables.py               DataFrame → notebook display / booktabs .tex
    │   ├── save.py                 .pdf + .png + .csv + .json per figure
    │   └── checks.py               compare with the document's tables/*.csv
    │
    ├── assets/external/            copied from archive (ARI, B64 baseline, sector events…) — read by viz/data.py
    ├── tests/
    │   └── test_lib_vs_document.py NEW: every lib function reproduces a number of the document
    │
    └── notebooks/
        ├── 39_style_proof.ipynb            draws the proof sheet (one page, one example of each chart type)
        ├── 40_q1_growth_protection_fidelity.ipynb
        ├── 41_q2_design_space.ipynb
        ├── 42_q3_evolution_dominant_design.ipynb
        ├── 43_q4_filers.ipynb
        ├── 44_q5_regions.ipynb
        └── 45_export_latex.ipynb           collects everything 40–44 saved → latex/ + captions + index
```

### Outputs — on the Drive, in a NEW folder, nothing mixed with the existing documents

```
3 - Images DataSets & Labelling Outputs/1639_LABELLED/1_labelling_analysis/
├── preliminary_analysis/           old Preliminary Analysis (notebook 10)
├── labelling_analysis_preliminary/ RENAMED 2026-10-01 (was labelling_analysis): the 45-page document,
│                                   its tables/ and figures/ — read-only for the new code, used only for checks
└── labelling_analysis_thesis/      NEW — everything the new notebooks write
    ├── style/
    │   └── proof_sheet.pdf         output of notebook 39
    ├── q1_growth_protection_fidelity/      output of notebook 40
    │   ├── figures/  fig_1_filings_per_year.pdf  .png  .csv  .json   (one set per figure)
    │   ├── tables/   tab_1_ari_firms.csv  .tex
    │   └── numbers.csv             every number the text of question 1 quotes: name, value, base, test
    ├── q2_design_space/                    notebook 41   (same three parts)
    ├── q3_evolution_dominant_design/       notebook 42
    ├── q4_filers/                          notebook 43
    ├── q5_regions/                         notebook 44
    └── latex/                              output of notebook 45
        ├── figures/                all .pdf, flat, named as the \includegraphics will cite them
        ├── tables/                 all .tex
        ├── captions.tex            one \caption per figure and table, from the .json sidecars
        └── FIGURE_INDEX.md         figure → question → notebook → inputs → files
```

labelling_analysis.yaml names both trees; nothing in the notebooks hard-codes a path.

## 2. What to do with the existing notebook and source files

| File(s) | Role today | Action |
|---|---|---|
| everything that was in the repo (labeling_evaluation, docs, scripts, README) | the engine of the 45-page document and the earlier reports | **moved to `archive/`** 2026-10-01 (git mv, history kept); the five render scripts had their output-folder string updated to `labelling_analysis_preliminary` so they still run |
| `archive/labeling_evaluation/src/dataset_facts/*.py` (37 k lines) | loaders, ~150 table builders, figure code, document renderer | equations get **ported** into the new `lib/` (clean, tested against the document's CSV); the loader logic is **re-written** small in `viz/data.py`; figure code is **not** ported, it is replaced by `viz/plots.py` |
| `embedding_evaluation/` | the embedding pillar | moved out of this repo by another session on 2026-10-01 (now in eVTOL-Embedding-Extraction); its `docs/embedding_evaluation` went into `archive/docs/` with the rest |

## 3. Equations the lib must hold (all exist in `la_tables.py` / `sm_open.py` today, mixed with wrangling)

| lib module | Equation | Used by brief items |
|---|---|---|
| distance | Gower: d(i,j) = Σ w_k δ_k(i,j) / Σ w_k with δ = 1 − |x_i − x_j| / range for numbers, mismatch for categories; weights subsystem-equal or field-equal | 3.2 condition 3, 3.3, 5.3 proximity |
| dominant_design | C1 top archetype share of in-force aircraft ≥ threshold per priority year; C2 top archetype unchanged over consecutive windows; C3 within-archetype Gower Q below the permutation band (`perms` draws) | Fig sm_family_yearly, sm_dd_conditions, Table 8 |
| diversity | Hill numbers ^qD, rarefied to n = 40 by `draws` resamples; Chao1, jackknife-1/2 discovery curve | Fig discovery_curve, 2.3 |
| association | Cramér's V bias-corrected (Bergsma 2013), χ², Mann–Whitney, Spearman ρ vs priority year, Benjamini–Hochberg | 1.3 Tables 4–5, 3.4 traces, 4.1 ARI tests |
| intervals | Wilson interval for a share | sm_evtolnews_check, sm_force_aircraft |
| concentration | HHI; leverage = max share change when one firm is dropped; one-vote-per-filer shares | sm_one_firm, 5.3 |
| growth | two-segment log-linear fit → doubling time + turning point; share of CPC-B64 baseline | filings_per_year, 1.1 |
| regional | LQ = (class share in region) / (class share overall); lead/lag = first-year offset per class | sm_region_timing, sm_region_converge |
| drivers | per-class Spearman of a trace vs year (≤2023, n ≥ 20, p < 0.05) → verdict rules | sm_driver_traces, sm_driver_trajectory, Table 9 |

Rule: a lib function takes plain frames/arrays and returns numbers; it never reads a file or a config.
`tests/test_lib_vs_document.py` calls each one on the master dataset and asserts equality with the CSV the
brief printed (`brief_dir/tables/*.csv`). If a port disagrees with the brief, the brief wins until the
author rules.

## 4. Style

- `pip install scienceplots` (2.2.2 available) → base style `science` + `no-latex` (+ `grid` where useful),
  then `thesis.mplstyle` on top: thesis font and point sizes, figure widths from `text_width_in`.
- **Per-class scheme** (explained): every architecture class gets, once and for all, one colour AND one
  marker shape AND one line dash AND one hatch pattern (e.g. Lift+Cruise = blue, circle, solid, no hatch;
  Tilt Propulsor = orange, square, dashed, diagonal hatch …). The same class looks the same in all 24
  figures, and if a page is printed in black and white the classes can still be told apart by the
  marker/dash/hatch. This is what the brief already does; the thesis keeps it.
- **Style proof sheet** (explained): before drawing the 24 figures, `viz/style.py` draws ONE page with
  one example of each chart type (a share-bar chart, a class line chart, a CI bar chart, a heatmap, a
  small-multiples grid, a table) in the final thesis style. The author looks at that one page and asks for
  changes. Fixes go into `viz/style.py` / `viz/plots.py` once, instead of into 24 figures one by one.
- Output per figure: `.pdf` (vector, for LaTeX, drawn at final width) + `.png` 300 dpi (preview/Word)
  + `.csv` (the plotted data) + `.json` (Source · Unit · Base · Transform · How to read → caption).
  No stamp inside the image.

## 5. labelling_analysis.yaml (what it holds)

paths (labelled_root, brief_dir, output_dir, latex_dir) · inputs (every file read, by key; `viz/config.py`
asserts each exists and prints a table) · analysis constants (partial_window_start 2024, windows, class
order, thresholds n ≥ 20 / p < 0.05 / n = 40 rarefaction / perms) · style (text_width_in, font,
base_font_pt, dpi, palette, formats) · figures register (name → notebook, brief figure number, thesis
chapter, lib functions, source tables, size, panels) · tables register (same).

## 6. Steps

**Status 2026-10-01: step 1 DONE.** labelling_analysis.yaml (34 paths, 0 missing; DEV_YEAR_DECISIONS.csv optional and
absent, as it was for the document), assets copied into `labeling_evaluation/assets/`, `viz/config.py`
(`python -m viz.config` prints the path table), `viz/data.py` (ported loader: every frame identical to the
archive's, counts 1 639 patents → 627 aircraft), register of 24 figures + 10 tables in labelling_analysis.yaml, notebook
40 section 0 executed.

**Status 2026-10-01: step 2 DONE.** lib/ = 9 modules (diversity, distance, dominant_design, association, intervals,
concentration, growth, regional, drivers), ~110 pure functions, each with formula + "Ported from" + "Used in";
tests/ = 82 tests, all pass (~3.5 min), each lib function equal to the archived one (atol 1e-12) and to the document's
CSV where the table comes straight from it. Duplicates merged (one Holm, one Freedman–Lane test, one proximity test;
concentration.inverse_hhi ≠ diversity.effective_number). Findings for the author: METHOD_NOTES.md.
**Step 3 started:** scienceplots installed; viz/style.py, viz/plots.py, viz/save.py; notebook 39 → style/proof_sheet.pdf
(approved 2026-10-01).

**Status 2026-10-01 (evening): notebooks 40–43 DONE and verified** (Q1 96/96 numbers, Q2 46/46, Q3 78/78, Q4 56/56;
every table matches the document; SRW→LC differences labelled). Notebook 45 (LaTeX export) built: viz/latex.py →
<output>/latex/ (figures/*.pdf, tables/*.tex booktabs, figures.tex, tables.tex, FIGURE_INDEX.md); no LaTeX compiler on
this machine, so the notebook checks braces/environments/PDF presence instead of compiling. Notebook 44 (Q5) DONE (47/47 numbers, 14 tables, Table 10 + its 2 computed numbers).
**ALL STEPS DONE 2026-10-01:** notebooks 39–45 run end to end; 24 figures + 40 tables (10 of the document + supporting)
exported to latex/; 115 tests pass. README.md written. Open for the author: METHOD_NOTES.md decisions, the 7 ⚠ inputs in
INPUTS.md, Figure 1 caption, the thesis LaTeX text width/font (yaml `style`), then re-run 39–45.


| Step | Work | Author sees |
|---|---|---|
| 1 | labelling_analysis.yaml + viz/config.py + viz/data.py; register filled from the code | the printed path table (every input: path, exists, mtime) |
| 2 | lib/ ported, tests pass against the brief's CSV | test report: equation → brief table → match |
| 3 | scienceplots installed; viz/{style,plots,save,tables}.py; notebook 39 → proof sheet | one PDF page to approve |
| 4 | notebook 40 (Q1) end to end | 5 figures + 5 tables as in LaTeX |
| 5 | notebooks 41–44 | 19 figures + 5 tables |
| 6 | notebook 45 export; delete notebook 10 and build_notebook_10.py; propose the _backups purge | LaTeX folder + FIGURE_INDEX.md |

## 7. Open points

1. Thesis LaTeX template (text width, class, body font, caption size, colour or B&W) — **can come later**:
   labelling_analysis.yaml starts with defaults (A4, text width 6.3 in, serif, 9 pt base, colour + B&W-safe scheme);
   changing them and re-running 39–45 redraws everything. Needed before the FINAL run only.
2. Outputs: Drive, new folder `1_labelling_analysis/thesis/` — decided 2026-10-01.
3. Scope: everything in the 45-page document — decided 2026-10-01.
