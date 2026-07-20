# eVTOL-Embedding-Evaluation

Characterization of embedding spaces for eVTOL patent figures: benchmarks
multiple vision pipelines (frozen DINOv2, DINOv2+registers, SigLIP,
SAM-crops+SigLIP, style-normalized and fine-tuned variants) against taxonomy
labels (lift architecture, wing type, rotor count, propulsion).

This repo only **consumes**:
- labels from `Patent-Labelling-Tools` → `eVTOL-Embedding-Extraction`'s
  `labels_v1.parquet`
- embeddings from `eVTOL-Embedding-Extraction`'s
  `outputs/embeddings/<pipeline_name>/` folders

It never re-derives labels from raw wizard exports and never runs a vision
model — both of those live in the sibling repos.

## Layout

```
eVTOL-Embedding-Evaluation/
  README.md
  config.yaml
  src/
    __init__.py
    config_loader.py
    registry.py                 # pipeline name -> embeddings folder + manifest.json
    probes.py                   # linear probes per taxonomy axis, confound tests
    structure_clustering.py     # UMAP, HDBSCAN, cluster<->taxonomy alignment
  notebooks/
    20_probes.ipynb
    21_structure_clustering.ipynb
    22_benchmark_table.ipynb    # final cross-pipeline csv/latex
  docs/
    ANALYSIS_GUIDE.md           # metric reference (probes, structure)
    21_structure_clustering_report.md
    MEETING_SUMMARY_2026-06-30.md
    figs/, dendrogram_clusters/
  outputs/
```

## Known follow-up

`src/structure_clustering.py::stage0_prepare` (moved as-is from the previous
combined repo) still directly calls embedding computation
(`emb.compute_embeddings`) rather than reading finished embeddings through
`registry.py`. That coupling needs to be untangled in a follow-up pass —
extraction should happen only in `eVTOL-Embedding-Extraction`'s `12x`
notebooks, and this repo's `stage0_prepare` should be rewritten to *only* join
already-extracted embeddings (via `registry.py`) with
`labels_v1.parquet` (via `paths.labels_parquet`).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Edit `config.yaml`: `paths.labels_parquet` and `paths.embeddings_root`.
