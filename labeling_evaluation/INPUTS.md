# Inputs of the Labelling Analysis — the pipeline and the history of label changes

## What the thesis notebooks read

⚠ = not made by you: to review.

| Info | Made by | File |
|---|---|---|
| All aircraft labels (class, propulsor units, wings, booms, ducts, tilting…), approval, duplicates, powertrain ruling, ground truth | You (wizard + review pages), joined by notebook 04 | aircraft_table.csv |
| Figure verdicts (approved, whole vehicle) | You (wizard), joined by notebook 04 | figure_table.csv |
| Option names of each label column | Notebook 04 (script) | data_dictionary.csv |
| Dates, office, assignee, country, region, legal status, claims, citations | PatSeer | aircraft_identity_ALL.xlsx |
| Company name (canonical) | Script (name list + fuzzy match) | aircraft_identity_ALL.xlsx |
| ⚠ Industry (not used in the 45-page document) | SBERT | aircraft_identity_ALL.xlsx |
| ⚠ TRL per aircraft | Claude (LLM) | aircraft_trl.csv |
| Public aircraft: class, status, capacity, piloting, power source | evtol.news (script crawl) | aircraft.csv |
| Which patent is which public aircraft | You, on Claude's proposals | patent_links.csv |
| ⚠ Development year of public aircraft | Claude (LLM), two readers | aircraft_dev_year.csv |
| Index score, funding, first flight, entry into service | AAM Reality Index (SMG Consulting) | ari_may2026.csv, ari_history.csv, ari_funding_may2026.csv |
| ⚠ Index firm → corpus firm | Claude (LLM) | ari_company_map.csv |
| Aviation patents per year (growth baseline) | WIPO PATENTSCOPE, PatSeer | b64_by_priority_year.csv, patseer_*_worldwide_by_priority_year.csv, baselines_2000_2023.csv |
| Granted / pending / dead per year, grant lag | You (script on the PatSeer export) | status_by_priority_year.csv, grant_lag_summary.csv |
| ⚠ Sector funding | Claude (LLM), from publisher pages | aam_funding_by_period.csv |
| ⚠ Market forecasts | Claude (LLM), from publisher pages | evtol_market_forecasts.csv |
| ⚠ Dated sector events (strip under Figure 1) | Claude (LLM) | sector_events.csv |
| Codebook dimensions | You (codebook) | dimension_register.csv |

Full paths: `labelling_analysis.yaml`, or run `python -m viz.config`.

## The labelling pipeline (notebook 04) — not read by the thesis notebooks

### What enters notebook 04 (all confirmed)

| Input | File (under 1639_LABELLED/0_labelling/inputs/) | Made by |
|---|---|---|
| Wizard record | record/reviewed_patents_Batch_ALL.xlsx | **author**, the wizard labels |
| PatSeer export | reference/patseer_1639_08_06_26.xlsx | **external**, PatSeer, exported by the author 2026-06-08 |
| Company map | reference/family_map.csv | **script** grouper.py: hand-written list of ~110 company names + fuzzy match ≥ 85 |
| Identity workbooks | labels/Batch_NN/aircraft_identity_Batch_NN.xlsx | **author** on the identity page (name, electric, take-off, UAV), over **script + SBERT** machine columns of stage 03a |
| Identity corrections | review_decisions/CORRECTIONS_identity.csv | **author's** rulings, typed in by Claude |
| Name decisions | review_decisions/NAME_DECISIONS.csv | **author**, name review pages |
| Duplicate answers | review_decisions/duplicate_root_variant.csv | **author**, duplicate worksheet page |
| Powertrain decisions | review_decisions/POWERTRAIN_DECISIONS.csv | **author**, on Claude's proposals, 2026-09-30 |
| Architecture ground truth | text_architecture/architecture_text_final_variants.csv | **author**, whole-patent reading on the architecture page |
| ML pre-labels | labels/Batch_NN/ml_predict_labels_Batch_NN.xlsx | **SigLIP + SBERT** models; kept as ml_ columns, NOT used by the analysis |
| Note tags | Patent-Labelling-Tools/notebooks/04_other_note_tags.csv | **author**, free-text notes mapped to tags |

### What notebook 04 does

1. Backs up the previous build to `1639_LABELLED/_archive/backups/NB04_<time>/`.
2. Reads the wizard record; turns "ID — Label" answers into plain option ids; one row per aircraft.
3. Resolves duplicates: a D1/D2 carries no labels and points at the aircraft it repeats.
4. Applies the override rule (2026-09-19): a value an override hides is left blank.
5. Joins the patent facts (identity build: PatSeer + names + electric/take-off/UAV + powertrain ruling).
6. Joins the architecture ground truth (arch_gt) and the company map.
7. Derives the rule columns (propulsor units, boom thrust state, wing-borne thrust).
8. Checks the record against what the wizard shows; writes the outputs and BUILD_LOG.md.

### What notebook 04 writes

`0_labelling/outputs/`: tables/aircraft_table.csv, tables/figure_table.csv, tables/data_dictionary.csv (read by the
thesis notebooks), 1639_LABELS.xlsx (sheet aircraft_final = aircraft_table.csv), BUILD_LOG.md. The thesis code stops
with a message if the wizard record or any decision file is newer than aircraft_table.csv.

### The chain, with dates

**Your last labelling is the source of everything below.** The chain is:

```
wizard export (Downloads, last 2026-09-21 23:41)
  → installed as 0_labelling/inputs/record/reviewed_patents_Batch_ALL.xlsx (2026-09-22 14:34)
  → notebook 04 (Patent-Labelling-Tools), last run 2026-09-30 16:46, writes in ONE run:
       outputs/1639_LABELS.xlsx          the same labels in the wizard's format (one row per answer,
                                         131 205 rows), for resuming in the wizard and for reading by eye
       outputs/tables/aircraft_table.csv the same labels reshaped for analysis: one row per aircraft,
                                         plain option ids, duplicates resolved, override rule applied
       outputs/tables/figure_table.csv   one row per figure
```

The analysis reads the CSV, not the xlsx, because the xlsx is one row per answer in "ID — Label" text and
cannot be counted per aircraft without redoing notebook 04's work. BUILD_LOG.md records the sha256 of the
record it read. `python -m viz.config` warns if the record is ever newer than aircraft_table.csv.

| File | Who made it | What is in it |
|---|---|---|
| aircraft_table.csv | **Author's labels**, joined by notebook 04 (a script) | One row per patent × aircraft (1 750 rows, 504 columns): every wizard answer (class, propulsor units, wings, booms, ducts, tilting…), approval verdict, duplicate links, edge tags, and the author's whole-patent architecture ground truth (`arch_gt`). The core of every figure. |
| figure_table.csv | **Author's figure verdicts** in the wizard, joined by notebook 04 | One row per patent figure (4 628 on file): approved or not, which parts it shows. Used only to keep whole-aircraft drawings. |
| data_dictionary.csv | Script (notebook 04) | Column name → wizard section and type. No content, only definitions. |
| aircraft_identity_ALL.xlsx | **PatSeer export** (dates, assignee, country, legal status) + stage 03a script; name, electric and VTOL **reviewed by the author**; scope and powertrain pre-filled by **SBERT** where no sentence was found | One row per patent (1 639): priority year, region, assignee country, raw assignee, canonical firm (hand list + fuzzy match), in force or not. The document reads only the PatSeer-origin columns and the canonical firm. |
| aircraft_trl.csv | Script, from **105 TRL rulings written by Claude** from evtol.news pages and web sources (quote + link each), under rules set with the author; 28 marked medium confidence | NASA TRL per aircraft (798). No ruling = TRL 2 "patent only". |

## Every change made after the labelling, and where it lives (checked 2026-10-01)

Two kinds of change exist. **Kind 1** was written INTO the wizard record, so it is in
`reviewed_patents_Batch_ALL.xlsx`, in the Review sheet of `1639_LABELS.xlsx` (byte-identical to the record) and in
`aircraft_table.csv`. **Kind 2** lives in a decision CSV in `0_labelling/inputs/review_decisions/` and is applied every
time the identity workbook and notebook 04 are rebuilt: it reaches `aircraft_table.csv`, but **not** the wizard record
and **not** the Review sheet of `1639_LABELS.xlsx`.

| Change | Date | File that holds it | Kind | In aircraft_table.csv |
|---|---|---|---|---|
| All wizard edits and scripted fixes to the record (names, booms, wCount, edge tags…) | to 2026-09-22 | labels/CORRECTIONS_LOG.csv (15 335 logged edits) | 1 | yes |
| Flight-state (acState) page | 2026-09-19 | ACSTATE_DECISIONS.csv (57) | 1 | yes, 57/57 checked in the record |
| Damaged-figure restore page | 2026-09-18 | DAMAGE_RESTORE_DECISIONS.csv + _EXTRA | 1 | yes |
| Identity edge tags (UAV / Electric Similar) | 2026-09-22 | CORRECTIONS_identity.csv (24 tags + 1 count) | 1 | yes, 24/24 (12 on duplicates, carried by their original) |
| Aircraft names | 2026-09-17 | NAME_DECISIONS.csv | 1 + 2 | yes |
| Architecture ground truth (whole-patent reading) | 2026-09-17/21 | text_architecture/architecture_text_final_variants.csv | 2 | yes, column arch_gt (also in the ground_truth sheet of 1639_LABELS.xlsx) |
| Which aircraft a duplicate repeats | 2026-09-16 | duplicate_root_variant.csv (27) | 2 | yes |
| **Powertrain ruling (no Hybrid)** | **2026-09-30** | **POWERTRAIN_DECISIONS.csv (83 patents)** | **2** | **yes: 31 patents / 38 aircraft No + ElectricSimilar. NOT in the record, NOT in 1639_LABELS.xlsx** |

Not applied to anything (lists only): PENDING_WIZARD_REVIEW.csv (things to check in the wizard), REVIEWED_IN_WIZARD.csv,
the NAME_EVTOLNEWS_* page exports, scope_sample_decisions.csv (scope parked), the HYBRID_* review files (superseded by
POWERTRAIN_DECISIONS.csv).

**Rule for the thesis:** the analysis reads `aircraft_table.csv`. Since 2026-10-01 the sheet `aircraft_final` of
`1639_LABELS.xlsx` holds the same values (both kinds); the Review sheet and the record show the labels before the
Kind 2 decisions. Notebook 04 backs up the previous build to `1639_LABELLED/_archive/backups/NB04_<time>/`.

## Read by the old code but NOT used by the 45-page document (removed from the yaml)

Claude's text architecture reading (architecture_text_Claude_20260909.csv, architecture_text_final.csv, quote_check.csv),
the text identity reading (results.csv, comparison_237.csv), known_aircraft_architecture.csv, phase1_field_inventory.csv,
family_map.csv, the legacy rule_decisions JSON. They fed the old Preliminary Analysis only.
