# eVTOL-Visual-Evaluation

Evaluation of eVTOL patent figures along two pillars, analysed separately because
the thesis compares them:

- **[`embedding_evaluation/`](embedding_evaluation/README.md)** — evaluation of
  the embeddings produced by `eVTOL-Embedding-Extraction`: which figures went in,
  integrity, structure vs. random noise, clustering, layer × pooling choice
  (one notebook, `30_embedding_evaluation`).
- **[`labeling_evaluation/`](labeling_evaluation/README.md)** — the
  human-labelled dataset on its own: labelling methodology, taxonomy structure,
  design characteristics, and the Preliminary Analysis document (below).

Each pillar is self-contained: its own `config.yaml`, `notebooks/`, `src/`,
`scripts/` and `outputs/`. Only shared material sits at the root — `docs/`
(reports and figures) and `scripts/` (document rendering).

## Pipeline stages across the three repos

| Stage | Where | Notebooks |
|---|---|---|
| 0 — Labelling | `Patent-Labelling-Tools` | wizard, 01a → 02a → 03a/03b → 04 |
| 1 — Labelling evaluation | `labeling_evaluation/` (this repo) | `10_preliminary_analysis` |
| 2 — Extraction | `eVTOL-Embedding-Extraction` | `20_figure_selection` → `21_image_processing` → `22_embedding_extraction` |
| 3 — Embedding evaluation | `embedding_evaluation/` (this repo) | `30_embedding_evaluation` |

This repo only **consumes**: labels from `Patent-Labelling-Tools`
(`1639_LABELLED/`, `labels_v1.parquet`) and embeddings from
`eVTOL-Embedding-Extraction`. It never re-derives labels from raw wizard exports
and never runs a vision model.

## Layout

```
eVTOL-Visual-Evaluation/
  README.md  requirements.txt
  docs/                           # reports, figures, meeting notes (shared)
    ANALYSIS_GUIDE.md             # metric reference (probes, structure)
    embedding_evaluation/         # generated report + figs (notebook 30) + SELECTION_DECISIONS.md
    Supervisor_Report_Taxonomy_Structure_Analysis_summary.md/.pdf
  scripts/                        # document tooling only
    build_report_pdf.py           # docs/*.md or */README.md -> PDF
    build_styled_md_pdf.py        # methodology / preliminary-analysis .md -> print-style PDF

  embedding_evaluation/
    README.md                     # pillar report: embedding QC, structure, clustering, alignment
    config.yaml                   # pipeline_root, metrics_dir, metrics + report settings
    notebooks/
      30_embedding_evaluation.ipynb   # metrics -> figures -> report (the only notebook)
    src/
      config_loader.py
      embedding_metrics.py        # label-free metrics per embedding run x figure set
      embedding_report.py         # figures + docs/embedding_evaluation/embedding_evaluation_report.md
      registry.py                 # (legacy) pipeline name -> embeddings folder + manifest.json
      probes.py                   # (legacy) linear probes per taxonomy axis, confound tests
      structure_clustering.py     # (legacy) UMAP, HDBSCAN, cluster<->taxonomy alignment
    archive/notebooks/            # 20_probes, 21_structure_clustering (do not run; kept for reference)
    scripts/  outputs/

  labeling_evaluation/
    README.md                     # pillar report: review data, duplicates, taxonomy, design characteristics
    config.yaml                   # labelled_root + dataset_facts settings
    notebooks/
      10_preliminary_analysis.ipynb   # the Preliminary Analysis, index order 1.1 -> 5.5 (+ appendix)
    src/
      config_loader.py
      dataset_facts/              # every measured fact about the labelled dataset
        loaders.py  metrics.py    # 1639_LABELLED -> Dataset; effective number, kappa, HHI
        a1.py .. a6.py            # framework Part A sections A.1-A.6
        roster.py                 # the aircraft that enter, with every sensitivity flag
        rules.py                  # D12: 02a consistency-rule counts
        index.py                  # the Preliminary Analysis index as data
        figures.py  report.py     # matplotlib figures; the generated draft .md
        published.py  export.py   # framework-number drift check; tables -> CSV + md
    scripts/
      build_architecture_review_page.py   # 03b citation-confirmation page
      apply_architecture_review.py        # merges its decisions into architecture_text_final.csv
    outputs/
      preliminary_analysis/       # tables/, figs/, PRELIMINARY_ANALYSIS.md (generated, gitignored)
```

## The embedding evaluation (embedding pillar)

`embedding_evaluation/notebooks/30_embedding_evaluation.ipynb` reads the figure
sets and embeddings the extraction repo wrote (`paths.pipeline_root`), computes
the label-free metrics for every embedding run × figure set
(`outputs/embedding_metrics/`), draws the figures and writes
`docs/embedding_evaluation/embedding_evaluation_report.md`. Why each figure was
selected is registered in `docs/embedding_evaluation/SELECTION_DECISIONS.md`.

## The Preliminary Analysis (labelling pillar)

`labeling_evaluation/notebooks/10_preliminary_analysis.ipynb` follows the
annotated index of the Preliminary Analysis document section by section
(1.1 acquisition funnel → 5.5 class shares per window). Each section is a
markdown cell with the index's three lines — *Source*, *Tables / figures*,
*Gives →* — followed by the code that produces exactly those tables and figures.
The index itself is data (`src/dataset_facts/index.py`), so the notebook, the
block diagrams and the generated document all read one text.

```bash
cd labeling_evaluation
#   config.yaml -> paths.labelled_root = .../1639_LABELLED   (the only input)
jupyter lab notebooks/10_preliminary_analysis.ipynb
```

The last cells write `outputs/preliminary_analysis/`: every table as CSV and
markdown, every figure as PNG, the roster of aircraft that enter the analysis
with their sensitivity flags, and `PRELIMINARY_ANALYSIS.md` — the draft document
with the live numbers in place. Edit the prose there; never the numbers. Render
it with `python3 scripts/build_styled_md_pdf.py <md> <pdf>` from the repo root.

The appendix keeps the framework-document sections the index excludes (text-side
architecture reading, identity variables) and `published.check(ds)`, which
compares every number the framework document printed with the live data and
reports match or drift. As of 2026-09-10, 117 of 125 reproduce exactly; the
eight that drift carry a note saying why.

Read-only: the package never writes to `1639_LABELLED`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then edit the pillar you work on: `embedding_evaluation/config.yaml`
(`paths.pipeline_root` = the extraction repo's `paths.pipeline_root`) or
`labeling_evaluation/config.yaml` (`paths.labelled_root`).
