# eVTOL-Visual-Evaluation

Evaluation of eVTOL patent figures along two pillars, analysed separately because
the thesis compares them:

- **[`embedding_evaluation/`](embedding_evaluation/README.md)** — embedding
  extraction, visual feature analysis and visual-learning metrics: benchmarks
  vision pipelines (frozen DINOv2, DINOv2+registers, SigLIP, SAM-crops+SigLIP,
  style-normalized and fine-tuned variants) against taxonomy labels.
- **[`labeling_evaluation/`](labeling_evaluation/README.md)** — the
  human-labelled dataset on its own: labelling methodology, taxonomy structure,
  design characteristics, and the Preliminary Analysis document (below).

Each pillar is self-contained: its own `config.yaml`, `notebooks/`, `src/`,
`scripts/` and `outputs/`. Only shared material sits at the root — `docs/`
(reports and figures) and `scripts/` (document rendering).

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
    Supervisor_Report_Taxonomy_Structure_Analysis_summary.md/.pdf
  scripts/                        # document tooling only
    build_report_pdf.py           # docs/*.md or */README.md -> PDF
    build_styled_md_pdf.py        # methodology / preliminary-analysis .md -> print-style PDF

  embedding_evaluation/
    README.md                     # pillar report: embedding QC, structure, clustering, alignment
    config.yaml                   # labels_parquet, embeddings_root, taxonomy settings
    notebooks/
      20_probes.ipynb
      21_structure_clustering.ipynb
    src/
      config_loader.py
      registry.py                 # pipeline name -> embeddings folder + manifest.json
      probes.py                   # linear probes per taxonomy axis, confound tests
      structure_clustering.py     # UMAP, HDBSCAN, cluster<->taxonomy alignment
    scripts/  outputs/

  labeling_evaluation/
    README.md                     # pillar report: review data, duplicates, taxonomy, design characteristics
    config.yaml                   # labelled_root + dataset_facts settings
    notebooks/
      30_preliminary_analysis.ipynb   # the Preliminary Analysis, index order 1.1 -> 5.5 (+ appendix)
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

## The Preliminary Analysis (labelling pillar)

`labeling_evaluation/notebooks/30_preliminary_analysis.ipynb` follows the
annotated index of the Preliminary Analysis document section by section
(1.1 acquisition funnel → 5.5 class shares per window). Each section is a
markdown cell with the index's three lines — *Source*, *Tables / figures*,
*Gives →* — followed by the code that produces exactly those tables and figures.
The index itself is data (`src/dataset_facts/index.py`), so the notebook, the
block diagrams and the generated document all read one text.

```bash
cd labeling_evaluation
#   config.yaml -> paths.labelled_root = .../1639_LABELLED   (the only input)
jupyter lab notebooks/30_preliminary_analysis.ipynb
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
(`paths.labels_parquet`, `paths.embeddings_root`) or
`labeling_evaluation/config.yaml` (`paths.labelled_root`).
