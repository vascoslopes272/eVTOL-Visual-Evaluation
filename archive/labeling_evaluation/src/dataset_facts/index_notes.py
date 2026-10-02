"""The notes of the annotated index (v1.1, 2026-09-09) — kept verbatim in the notebook.

These are the 43 markdown cells of the notebook as committed before the 2026-09-13
rewrite (``git show <old commit>:...30_preliminary_analysis.ipynb``, renamed 10_ on 2026-09-16): one cell per section of
the old index with its three lines **Source**, **Tables / figures**, **Gives →**, plus
the assumption notes. The user asked (2026-09-15) that they stay in the notebook no
matter what, so ``scripts/build_notebook_10.py`` inserts them under the section of the
NEW document that took over the same content. Keys are node ids of ``index.NODES``
(plus ``export`` and ``appendix``); the text is never edited here — the old section
numbers (1.1 … 5.5) are the old index's and are left as they were.
"""

from __future__ import annotations

from typing import Dict, List

#: one line printed above every note so the old numbering is not mistaken for the new
PROVENANCE = "*Note from the annotated index v1.1 (2026-09-09), kept verbatim — section numbers are the old index's:*"

NOTES: Dict[str, List[str]] = {
  "1": [
    "# Preliminary Analysis — the labelled dataset, index order\n\nThis notebook follows the annotated index of the *Preliminary Analysis* document section by\nsection (1.1 → 5.5, then the additions). Each section is a markdown cell with the index's three\nlines — **Source**, **Tables / figures**, **Gives →** — followed by the code that produces exactly\nthose tables and figures. The index text lives in `src/dataset_facts/index.py`; the notebook, the\nblock diagrams and the generated draft all read it from there.\n\nThe document states numbers; this notebook is where they come from. Change the labels, re-run\n`Patent-Labelling-Tools/notebooks/04_master_labels.ipynb`, re-run this, and every table, figure and\nthe draft `PRELIMINARY_ANALYSIS.md` move with the data.\n\nThin notebook: it only **imports**, **calls** `src/dataset_facts/`, and **displays**.\n\n> Unit of analysis, stated once at first use (1.3): the primary approved aircraft variant (805) for design statistics; the patent (695 approved primary) for metadata and citation statistics.",
    "The analysis unit is the **primary approved variant** (`ds.variants`, one row per aircraft, D1/D2\nduplicates excluded). Patent-level facts use `ds.patents` (all 1,639) or `ds.patents_analysis` (the\napproved primary 695). The labelling batches are provenance only — nothing is split by batch.",
    "---\n## Overview — what each section gives, and which chapter it feeds\n\nThe block diagram is drawn from `index.py`: one box per section with its short *Gives* line,\narrows to the chapters it feeds."
  ],
  "2": [
    "---\n## 1. Patent dataset construction (→ Ch. 3)"
  ],
  "2.1.1": [
    "### 1.1 Acquisition funnel\n\n- **Source**: D1 (funnel table); supervisor's pipeline figure with Table 1.\n- **Tables / figures**: funnel figure 1,639 acquired → 1,110 approved → 695 primary patents → 1,268 variants → 805 primary variants → 1,913 approved figures. Rejection-reason table. Approval rate by region table. Rejection reasons by region and by filer type (addition 2).\n- **Gives →** the size of the analysis set at each level and why two thirds survived; the regional approval gap shows the query behaves differently by office, so region is reported next to every later statistic. Feeds: Ch. 3 sample description; Ch. 4 Provenance (region as a possible confounder).",
    "Rejection reasons by region and by filer type (addition 2): whether the labelling filter behaves\nthe same across offices and applicants."
  ],
  "2.1.2": [
    "### 1.2 Filing reasons and inclusion gates\n\n- **Source**: A.1 (electric / VTOL / UAV columns), Part B lines G1–G3, rejection reasons of D1.\n- **Tables / figures**: one table with the three gates (electric, take-off, UAV) as the machine left them and the state after review (`*_final` columns).\n- **Gives →** which patents are eVTOL by rule and which were excluded, so the domain boundary is explicit. Feeds: Ch. 3 technological domain definition; the V/STOL ruling.",
    "`machine` is what Stage 03a decided; `after review` is the `*_final` column that carries the\nannotator's decisions on top of it. The UAV hint and the UAV final use different vocabularies, so\nthey are listed side by side. First over all 1,639 patents, then over the 695 analysis patents."
  ],
  "2.2.1": [
    "### 1.3 Unit of analysis: unique aircraft, repeated observations, several aircraft per patent\n\n- **Source**: D7 (duplicate types), aircraft-per-patent table, Part E.1.\n- **Tables / figures**: duplicate table (D1 same aircraft new figures · D2 same aircraft same figures · D3 same invention modified, with the count identical to root at A1). Aircraft drawn per patent.\n- **Gives →** how many independent aircraft there are and how the unit choice changes N; the double-count at A1 is stated with a number and kept as a sensitivity run. Feeds: every count in Ch. 4 and Ch. 5; the unit decision (G.4 #1)."
  ],
  "3.3.2": [
    "### 1.4 Missingness and weak labels: which aircraft enter the analysis\n\n- **Source**: D4 (structural missingness), D6 (uncertainty flags), D3 note on gearArch = Unknown.\n- **Tables / figures**: conditional-fill table; one heatmap of fill rate conditional on parent. Flag table. Output of this section: the list of unique aircraft that enter, with their sensitivity flags (the roster).\n- **Gives →** a blank is a labelling gap only where the parent says the part exists; on that test nearly every blank is design absence, so no aircraft is dropped for blanks. The three real gaps (wing height, planform, tail) are fixed or declared \"not visible\". Landing gear Unknown means not drawn, never absent. The flagged rows stay in, marked, and every analysis is run with and without them. Feeds: 1.5 and 1.6 operate on this list; Ch. 4 quality reads the numbers back; Gower δ treatment in Ch. 5."
  ],
  "3.2.4": [
    "**The roster** — the output of this section: every aircraft that enters, one row each, with every\nsensitivity flag as a column. Nothing is dropped; each later analysis runs with and without the\nflagged rows. Written to `outputs/preliminary_analysis/tables/roster.csv` by the export cell."
  ],
  "2.1.3": [
    "### 1.5 Filing-to-publication lag and the right-censoring cut\n\n- **Source**: D9 (lag table), Part E.2.\n- **Tables / figures**: median and 90th-percentile lag by region and by office. Snapshot date.\n- **Gives →** priority years to 2022 are complete, 2023 nearly, 2024–2026 truncated; every trend claim ends at 2023 and the last window is drawn as partial. This is what selects the patents that enter the G1–M3 analysis. Priority year is the time axis because it is the date closest to the design decision; application and publication years lag it by office-dependent amounts. Feeds: Ch. 3 corpus boundary; Ch. 5 window definition inherits the cut, does not re-derive it."
  ],
  "3.1.3": [
    "### 1.6 Publication timeline\n\n- **Source**: A.1 time coverage, D9 counts.\n- **Tables / figures**: patents per priority year, one bar chart; candidate windows with the variants each holds.\n- **Gives →** per-year statistics before 2016 are noise, so windows of 3–5 years rarefied to n ≈ 40 are needed. Feeds: Ch. 5 window width and rarefaction n. Priority year is the time axis (closest to the design decision)."
  ],
  "3.2": [
    "---\n## 2. Image and labelling statistics (→ Ch. 3 labelling results; input to Ch. 6)"
  ],
  "3.2.1": [
    "### 2.1 Answerable slots at patent and image level\n\n- **Source**: D2 (label-set properties).\n- **Tables / figures**: aircraft-level slot properties (slots, concepts, slots answered per aircraft, coverage, near-constant and informative counts); figure-level (T2) slots profiled over the approved figures.\n- **Gives →** the 283 columns are slots, not concepts; sparsity is structural (boom groups, propulsor tiers), so absence is a design fact carried by the parent field. Feeds: the field shortlist for Ch. 4 and Ch. 5; the derived per-aircraft layer (D2b, see additions).",
    "Aircraft level first (the cut-offs come from `config.yaml`), then the figure-level (T2) slots the\nwizard answers on every approved figure — these describe the drawing, not the design, and are the\nconfounds the embedding pillar has to control for. *Assumption for \"image level\" in the index:*\nthe T2 slots; say so if another reading was meant."
  ],
  "3.2.2": [
    "### 2.2 Figure basis of each label\n\n- **Source**: D11.\n- **Tables / figures**: approved figures per variant; figure quality; Whole Vehicle Layout share; median approved share per patent.\n- **Gives →** every approved primary patent shows at least one whole aircraft (the inclusion criterion the labelling enforced); the variants that rest on one figure define the single-figure sensitivity flag. Feeds: Ch. 4 quality sensitivity runs; Ch. 6 dataset (whole-aircraft figures available to the frozen model)."
  ],
  "3.1": [
    "---\n## 3. Provenance (→ Ch. 4 Provenance)"
  ],
  "3.1.1": [
    "### 3.1 Region, assignee country, publication office\n\n- **Source**: A.1 metadata (region, assignee_country, pub_office), D1 by region.\n- **Tables / figures**: region table; assignee-country table; publication-office table; one bar chart.\n- **Gives →** where the corpus comes from and where the acquisition surplus sits (US whole-aircraft filings vs drone and component filings elsewhere). Feeds: Ch. 4 region as a stratum, never as a filter (G.4 #6)."
  ],
  "3.1.2": [
    "### 3.2 Who filed and how concentrated it is\n\n- **Source**: D8, plan line G8 (assignee type).\n- **Tables / figures**: filer-type table; concentration table on raw string vs canonical company; single-patent filers; the strings one firm files under; Lorenz curve.\n- **Gives →** half the corpus is not corporate, which is what makes the assignee-type stratum worth building; concentration is mild, so pseudo-replication matters mainly in the tilt-rotor class. Feeds: Ch. 4 Provenance (assignee type); Ch. 5 company bootstrap and within-company permutation. Still to produce: the `assignee_type` column (G8).",
    "The `assignee_type` column (G8) does not exist yet; the suffix heuristic below only shows the size\nof the prize and is not a variable to analyse."
  ],
  "4": [
    "---\n## 4. Label quality (→ Ch. 4 Quality of data and methods of certifying it)",
    "### 4.1 Missingness and uncertainty, read back\n\n- **Source**: sections 1.4 (D4, D6). No new table.\n- **Tables / figures**: none; one paragraph pointing to 1.4.\n- **Gives →** the quality verdict on the labels that entered: which fields carry declared gaps, how many rows are flagged, and the size of the sensitivity set. Feeds: reliability paragraph.",
    "No new table: the D4 conditional-fill table, the D6 flag table and the roster summary of 1.4 are\nthe quality verdict on the labels that entered.",
    "### 4.3 Consistency rules\n\n- **Source**: D12 (02a rule-violation counts before and after correction). Partial: only the batches 02a has been run on.\n- **Tables / figures**: one table of rule applications and skips per batch.\n- **Gives →** internal coherence of the labelling; reliability evidence that does not need a second annotator. Feeds: reliability paragraph.",
    "Partial until 02a has been run on every batch: the table reads whatever `rule_decisions_*.json`\nfiles the configured glob finds."
  ],
  "3.3.1": [
    "### 4.2 Slots answered per aircraft\n\n- **Source**: D2.\n- **Tables / figures**: median, quartiles, maximum; histogram.\n- **Gives →** completeness of one label as a distribution, not a single number. Feeds: reliability paragraph."
  ],
  "4.1": [
    "### 4.4 Flagship check\n\n- **Source**: D13.\n- **Tables / figures**: company × labels × public product × verdict.\n- **Gives →** the labels agree with what the world knows where the answer is public; the disagreements are alternative embodiments, which is itself a sentence in the thesis. Feeds: external validation in Ch. 4; a short re-read list. Open: whether the intra-rater re-label (κ per field, 60–100 patents, 4 weeks after last labelling) enters as 4.5 or is a stated scope decision.",
    "---\n## Additions worth considering",
    "### A.6 Named-aircraft state (A.5)\n\n- **Source**: A.5 (addition 6).\n- **Tables / figures**: name proposals by source; what is reviewed and where.\n- **Gives →** proposals exist but none is verified; company-attributed names are statements about the assignee, not the drawing. One short table if the named-aircraft stratum stays in RQ3; otherwise a sentence in 3.2.",
    "### Not in the preliminary analysis (by design)\n\nImage-vs-text agreement (κ 0.61), Hill numbers, Rao's Q, MCA, permutation tests, kNN communities. These are results of Ch. 4–7, and the preliminary analysis only has to hand them a fixed dataset, a field shortlist, an archetype level, a window definition and a sensitivity-flag list."
  ],
  "3.3": [
    "---\n## 5. Design-space descriptives (→ Ch. 4 Variety and Diversity; 5.5 → Ch. 5)",
    "Opening figure: purpose of each subsection and the analysis it feeds."
  ],
  "3.3.3": [
    "### 5.1 Most common answers per field, and near-constant fields\n\n- **Source**: D3 second table, D2 (near-constant fields), A.3 group 2.\n- **Tables / figures**: field × answered × answers × top share × most common answers. Separate list of the near-constant fields.\n- **Gives →** which answers dominate and which fields cannot separate designs. Near-constant fields are reported as findings about the boundaries of the design space, then excluded from distances. Feeds: field shortlist; Ch. 4 descriptive statements."
  ],
  "3.3.4": [
    "### 5.2 Field inventory: effective number of answers, top share, cumulative\n\n- **Source**: D2 ranked table (`phase1_field_inventory.csv`).\n- **Tables / figures**: ranked table of the informative fields with card, answered, answers, top share, effective number, and the cumulative share of the top-2 and top-3 answers.\n- **Gives →** which fields carry information; the shortlist for Gower, Cramér's V and archetypes chosen from evidence. Feeds: Ch. 4 Variety; Ch. 5 methods (Gower field list, weights).",
    "*Assumption for \"cumulative\" in the index:* the cumulative share of the two and three most\ncommon answers (`top2_cumulative`, `top3_cumulative`); say so if another reading was meant."
  ],
  "3.3.5": [
    "### 5.2b Derived per-aircraft features (D2b)\n\n- **Source**: A.3 group 1 (addition 1).\n- **Tables / figures**: total propulsor units, any tilting, mixed fixed and tilting, any ducted, all ducted, thrust-axis mix, units per carrier. One table.\n- **Gives →** the sparse boom and tier slots as variables every aircraft has. Feeds: Gower, Cramér's V, MCA."
  ],
  "3.3.6": [
    "### 5.3 Archetype cardinality\n\n- **Source**: D5.\n- **Tables / figures**: level × fields × distinct × singletons × effective number.\n- **Gives →** how fine a design species can be before every patent is its own kind; A1 (three fields) is the counting archetype, finer levels enter only through distances. Feeds: G.4 #3; Ch. 5 Hill numbers."
  ],
  "3.3.7": [
    "### 5.4 Architecture class balance\n\n- **Source**: D3 first table.\n- **Tables / figures**: architecture type × aircraft × share; bar chart.\n- **Gives →** the class variable is balanced for twelve classes, so classes are large enough for windows of ~40. Feeds: Ch. 4 Variety; Ch. 6 class list for the frozen model; merging or dropping of small classes."
  ],
  "3.3.8": [
    "### 5.5 Class shares per window\n\n- **Source**: D9 window table.\n- **Tables / figures**: window × variants × share of TR / SLC / CVT / MR; stacked-area figure with the partial window hatched.\n- **Gives →** a first look at a shift from tilt rotor to lift plus cruise, and no class above about a third in any window, so raw shares show no dominant design. This is the pattern Ch. 5 tests, not assumes. Feeds: Ch. 5 window definition and hypotheses."
  ],
  "export": [
    "---\n## Export — tables, figures, the roster and the draft document\n\n`outputs/preliminary_analysis/` gets every table as CSV and markdown (`tables/`), every figure as\nPNG (`figs/`), and `PRELIMINARY_ANALYSIS.md`: the index text with the live tables and figures in\nplace. Edit the prose there; never the numbers. Render with\n`python3 scripts/build_styled_md_pdf.py <md> <pdf>` from the repo root."
  ],
  "appendix": [
    "---\n## Appendix — the framework-document sections the index excludes\n\nKept here because they are measured on the same data and because `published.check` (the drift\ncheck of every number the framework document prints) depends on them. They are results of\nCh. 4–7, not of the preliminary analysis.",
    "### Does the framework document still match the data?\n\n`published.py` holds every number Part A of the framework document prints, next to the call that\nrecomputes it. A **drift** row means the dataset moved after the document was written, or that the\ndocument's definition was wrong and the package uses the corrected one — read the note column."
  ]
}
