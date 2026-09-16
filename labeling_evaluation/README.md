# eVTOL Visual Evaluation — Labeling Evaluation

**Pillar:** labeling methodology, taxonomy structure, spatial design characteristics and evolutionary/convergence studies.
**Companion pillar:** [Embedding Evaluation](../embedding_evaluation/README.md) (embedding QC, structure tests, clustering and alignment metrics).

**Prepared for:** Phase Supervisor
**Pipeline stage:** [`21_structure_clustering.ipynb`](../embedding_evaluation/archive/notebooks/21_structure_clustering.ipynb) (Batches 01 + 05, 1639-patent dataset)

*Split from `docs/Supervisor_Report_Taxonomy_Structure_Analysis_summary.md` (the summary edition of the original combined supervisor report, with Section 5 restored). This file carries the review-data, duplicate, taxonomy and design-characteristic sections; the embedding-side sections live in the companion file. All figure and output paths below are relative to this repository.*

---

## 1. Batches & Review Summary

> **What this stage checks:** whether the review spreadsheets and processed manifests agree end-to-end.

*Sourced from `Review_postprocess_Batch_01/05.xlsx`, `processing_manifest_Batch_01/05.csv`, and the notebook's Stage 0 outputs.*

### 1.1 Individual and Combined Batch High-Level Summary

**Table 1.** Individual and combined batch high-level summary.

| Metric | Batch_01 | Batch_05 | **Global / Combined** |
|---|---:|---:|---:|
| Total patents reviewed (patent-level, `T1`) | 352 | 211 | **563** |
| Patents disapproved (`isApproved=False`) | 60 | 87[^1] | **147** |
| Patents approved (`isApproved=True`) | 292 | 123 | **415** |
| Total unique Patent IDs reviewed *and approved into the architecture stage* (`T2`)[^2] | 125 | 95 | **220** |
| Total architecture instances (approved, `T2` "arch" rows) | 301[^3] | 230[^3] | **531** |
| `is_main == True` images | 150 | 114 | **264** |

[^1]: One patent in Batch_05 has an unresolved review value; excluded from both counts (123 + 87 + 1 = 211).
[^2]: Lower than "approved" because approved-but-duplicate patents fold into an existing architecture record.
[^3]: Exceeds unique Patent IDs because one patent can disclose multiple aircraft configurations (14 multi-arch patents in Batch_01, 12 in Batch_05) — expected, not a data-quality issue.

**Cross-check:** 264 main images = 268 architectures − 4 with no approved main image. Reconciles exactly. *Source: `qc_issues.csv`.*

### 1.2 Review Tiers

The review record is tiered, and each tier is the unit for a different count above:

- **`T1`** — patent level: one row per reviewed patent, carrying the approve/disapprove decision.
- **`T2`** — architecture level: one "arch" row per aircraft configuration disclosed by an approved patent. A patent with several configurations has several `T2` rows.
- **`is_main`** — figure level: the one approved main image per architecture that goes on to embedding.

---

## 2. Duplicate-Type Definitions

Duplicates are labelled at review time with one of three types. The type decides which taxonomy stages are shared with the original record.

**Table 2.** Duplicate-type definitions and counts.

| Type (as labelled in the data) | Batch_01 | Batch_05 | Plain-language meaning |
|---|---:|---:|---|
| **"1 — Same Aircraft"** | 5 | 6 | Same aircraft/design seen before; `G1`–`M3` equal. |
| **"2 — Images AND aircraft the same"** | 167 | 27 | True exact duplicate; `T2`–`M3` equal. |
| **"3 — Same plane, small changes"** | 10 | – (0) | Minor drawing variations; all taxonomy stages differ. |

Type 2 (true exact duplicate) is the large majority (167/182 Batch_01, 27/33 Batch_05).

---

## 3. Pipeline & Data Discrepancy Audit

*Purpose: trace where the 563 reviewed patents narrow down to the 264 embedded images.*

**Table 3.** Global batch pipeline & data discrepancy audit.

| Pipeline Metric | Value |
|---|---:|
| `is_main == True` images (manifest, both batches) | **264** |
| Total architectures labelled | **268** |
| Base patents behind those architectures | 222 |
| Taxonomy attributes (distinct fields) tracked | **256** |
| Images with a fully aligned embedding | **264** |
| Architectures missing an approved main image | 4 |

### 3.1 Reconciling the Counts

**268 vs. 256:** different units, not a discrepancy. 268 = row count (one per architecture). 256 = column count (distinct taxonomy fields). Every row carries all 256 columns. *Source: `analysis_taxonomy/stage0/coverage_table.csv`.*

**268 vs. 264:** all architecture main images are embedded; the 4 not embedded simply have no approved main image on disk. 268 − 4 = **264**, matching Section 1.1 exactly. *Source: `config.yaml: taxonomy.main_arch_only: false`; `qc_issues.csv`; `aligned_rows.csv`.*

**Funnel:**

```text
563 reviewed patents (T1)
 └─ 415 approved
     └─ 220 unique patents entering the architecture stage (T2)
         └─ 268 labelled architectures
             └─ 264 with an approved main image → embedded
```

**Status:** RECONCILED. **Core finding:** every count reconciles exactly (563 → 415 → 268 → 264).

---

## 4. Taxonomy Schema and the Attributes Under Test

### 4.1 Schema Sections

`G1`/`M1`/`M2`/`M3` are the taxonomy schema section codes. They are used downstream as labels against the unsupervised clusters.

| Code | Section | Covers |
|---|---|---|
| `G1` | Topology | Top-level configuration type (`G1_topType`). |
| `M1` | Fuselage, gear and booms | Fuselage shape, landing-gear architecture, boom presence and geometry. |
| `M2` | Wing and empennage | Wing count, wing configuration, wing mounting position. |
| `M3` | Propulsion | Propulsor placement, orientation and count per structural group. |

The schema tracks **256 distinct attribute fields** per architecture (Table 3). Of these, **79 attributes** were testable against the clusters and the intra-/inter-class separation test (see Embedding Evaluation §5–6); many fields only apply to a subset of aircraft, so each attribute has its own labelled count.

### 4.2 Attributes Used for UMAP Colouring

The six attributes chosen to colour the UMAP projections (Embedding Evaluation Figure 6) are the coarse spatial-design descriptors: `G1_topType`, `M2_wCount`, `M2_wingConf`, `M1_boomsPresent`, `M1_fusShape`, `M1_gearArch`. No single one of them cleanly reproduces the cluster boundary, which is what motivated the quantitative alignment test.

### 4.3 Attributes That Surfaced in the Alignment Test

The table below defines the design attributes that ranked highest against the 2-cluster partition, and the label fields that act as confounds. The alignment scores themselves (NMI/ARI) are in Embedding Evaluation Table 4.

**Table 4.** Definitions of the best-aligning design attributes and the confound fields.

| Attribute | Section | Categories / N labelled | What it is | Verdict from the alignment test |
|---|---|---:|---|---|
| **M3_emp_chord** | M3 | 2 / 39 | Whether the empennage-mounted propulsor faces forward or back — puller ("Front") vs. pusher ("Back") configuration. | **Real signal** — ARI tracks NMI closely. |
| M3_emp_zone | M3 | 5 / 41 | Where on the empennage that propulsor sits — tip-mounted, stacked vertically, or stacked horizontally. | Aligns, weaker once chance-corrected. |
| M3_boom_t2_count | M3 | 9 / 94 | Number of secondary (type-2) propulsion units mounted on the boom, per boom. | **False positive** — aligns worse than chance (ARI < 0). |
| M2_wing1_posV | M2 | 4 / 211 | Vertical mounting position of the main wing on the fuselage — high/shoulder, mid, or low. | Real, modest signal. |
| M1_boom1_circSym | M1 | 2 / 111 | Whether the primary boom is circumferentially symmetric (round cross-section) or not. | Real, modest signal; strongest attribute on the separation test. |
| *assignee* | confound | 109 / 264 | Patent applicant/company — a drafting-style confound, not a design attribute. | **Mirage** — many small categories inflate NMI; real agreement ≈ 0. |
| *drawing perspective* | confound | 6 / 264 | The figure's viewpoint (front, side, top, isometric, …) — reflects how the patent was drawn, not the aircraft's design. | **Genuine confound** — strongest chance-corrected relationship of all; must be controlled for. |
| *assignee_country* | confound | 19 / 261 | Applicant's country of origin — another drafting/institutional confound. | Confound, weaker than perspective. |

### 4.4 Attributes That Separate Best in Embedding Space

From the intra- vs. inter-class distance test (Embedding Evaluation Table 5), the design characteristics with the strongest same-class cohesion are:

- `M1_boom1_circSym` — boom cross-section symmetry (defined in Table 4); top of the table at every layer tested.
- `M3_core_layout_zone` — propulsion-section field for the core layout; not defined in the source report.
- `M3_wing1_chord` — propulsion-section field for the first wing; not defined in the source report (by name, the wing analogue of `M3_emp_chord`).

Across 79 attributes, **174 attribute × layer rows separate significantly at p < 0.05**, so a large share of the taxonomy is at least weakly visible in the embeddings.

---

## 5. Design-Family Reading of the Dendrogram Branches

*Purpose: check by eye whether same-branch images look like the same design family, i.e. whether the clusters carry spatial design characteristics or only drawing style.*

The Ward-linkage dendrogram over the 264 embedded architectures (Embedding Evaluation Figure 4) was cut at Ward distance 0.60, giving **14 branches** (a strict 0.47 cut gives 21 instead). Each labeled branch has a folder of its actual main images for auditing:

```text
docs/dendrogram_clusters/cluster_01/ … cluster_14/   (1–43 images each; cluster_sizes.json)
```

**Visual spot-check:** genuine consistency is confirmed, but the common thread differs by branch.

| Branch | Common thread | Nature |
|---|---|---|
| 1 and 2 | Share drawing perspective more than design. | Style |
| 7 | Shares a "cruise" configuration — similar fuselage/wing, mostly 2 tilting propulsors. | Design |
| 14 | The same cruise style as branch 7, with more propulsors. | Design |
| 13 | Shares rendering style (grayscale/shaded CAD) rather than design. | Style |

The style-driven branches are the same effect as the drawing-perspective confound quantified in Embedding Evaluation §5 (ARI 0.288). A full branch-by-branch audit of whether same-branch images look like the same design family is still open (Section 6).

---

## 6. Phase Progress & Next Steps (Labeling Side)

> **What this section is for:** not a new test — it rolls up the review-data and taxonomy results into an overall phase status and lists the concrete data-side next steps still open. The embedding-side roll-up is in [Embedding Evaluation §7](../embedding_evaluation/README.md#7-phase-progress--next-steps-embedding-side).

**Data preprocessing & taxonomy checks — robust.** Two batches (531 approved patents combined), full review/duplicate tracking, zero embedding QC failures. The taxonomy schema (G1/M1/M2/M3 attribute groups, 256 attributes) is wired end-to-end from Excel review sheets through to cluster-alignment testing. Embedding every architecture (not just each patent's main one) improved the downstream result: the clearest 2-way partition now aligns with a genuine design attribute (`M3_emp_chord`) more strongly than with any confound on the pipeline's NMI gate.

**Immediate next steps:**

1. **Integrate missing data breakdowns.** Add the architecture-type breakdown table: formally generate and embed the table, using the data from `analysis_taxonomy/stage0/coverage_table.csv`.
2. **Audit the 14 dendrogram branches.** Each branch now has its own image folder (Section 5) — a visual check of whether same-branch images actually look like the same design family would validate (or challenge) the quantitative clustering results. Worth doing while this is fresh.

**Status:** IN PROGRESS.

---

## 7. Evolutionary / Convergence Studies

This pillar's forward scope covers evolutionary and convergence analysis of eVTOL spatial design over the patent record, using the taxonomy labels together with the embeddings. **The source report contains no results for this study yet.** What it does establish as prerequisites:

- A reconciled, duplicate-tracked review record (Sections 1–3) so that repeated designs are counted once.
- A 256-field taxonomy with a known subset of attributes that carry visual signal (Section 4).
- Evidence that clusters currently mix design signal with drawing style (Section 5), so convergence claims must wait for the perspective confound to be controlled (Embedding Evaluation §7).

---

*All tables sourced from [`notebooks/21_structure_clustering.ipynb`](../embedding_evaluation/archive/notebooks/21_structure_clustering.ipynb) (formerly `DINOv2_eVTOL_frozen_Analysis/notebooks/11_taxonomy_structure_separation.ipynb`). Stage outputs live outside the repo on the sync drive under `4 - Intelligence Models & Post Process Outputs/Preliminary_analysis/outputs/`: Stage-0 QC in `analysis_1639_518/`, Stage 1–5 tables and figures in `analysis_taxonomy/`. Branch image folders are vendored copies in [`docs/dendrogram_clusters/`](../docs/dendrogram_clusters/); see [ANALYSIS_GUIDE.md](../docs/ANALYSIS_GUIDE.md) for metric definitions.*
