"""The annotated index of the Preliminary Analysis, held as data.

The document is *Preliminary Analysis — annotated index v1.1* (2026-09-11). Every
section carries three lines — **Source**, **Tables / figures**, **Gives →** — and
those lines are stored here verbatim, so the notebook's markdown cells, the
generated draft (:mod:`report`) and the block diagrams (:func:`figures.block_diagram`)
all read from one place. Change the wording here and everything follows.

``tables`` and ``figures`` name the entries of :func:`export.build_all` and
:func:`figures.render_all` that each section shows.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

TITLE = "Preliminary Analysis — annotated index v1.1"

UNIT_NOTE = (
    "Unit of analysis, stated once at first use (1.3): the primary approved aircraft "
    "variant (805) for design statistics; the patent (695 approved primary) for "
    "metadata and citation statistics."
)

#: the chapters the sections feed, in the order the diagrams draw them
CHAPTERS = [
    "Ch. 3 Dataset",
    "Ch. 4 Provenance",
    "Ch. 4 Quality",
    "Ch. 4 Variety",
    "Ch. 5 Evolution",
    "Ch. 6 Model",
]

GROUPS = [
    dict(id="1", title="Patent dataset construction", chapter="→ Ch. 3"),
    dict(id="2", title="Image and labelling statistics",
         chapter="→ Ch. 3 labelling results; input to Ch. 6"),
    dict(id="3", title="Provenance", chapter="→ Ch. 4 Provenance"),
    dict(id="4", title="Label quality",
         chapter="→ Ch. 4 Quality of data and methods of certifying it"),
    dict(id="5", title="Design-space descriptives",
         chapter="→ Ch. 4 Variety and Diversity; 5.5 → Ch. 5"),
    dict(id="A", title="Additions worth considering", chapter=""),
]

SECTIONS: List[Dict] = [
    # ------------------------------------------------------------------ 1
    dict(id="1.1", group="1", title="Acquisition funnel",
         source="D1 (funnel table); supervisor's pipeline figure with Table 1.",
         tables_text="funnel figure 1,639 acquired → 1,110 approved → 695 primary patents → "
                     "1,268 variants → 805 primary variants → 1,913 approved figures. "
                     "Rejection-reason table. Approval rate by region table. Rejection reasons "
                     "by region and by filer type (addition 2).",
         gives="the size of the analysis set at each level and why two thirds survived; the "
               "regional approval gap shows the query behaves differently by office, so region "
               "is reported next to every later statistic. Feeds: Ch. 3 sample description; "
               "Ch. 4 Provenance (region as a possible confounder).",
         gives_short="size of the set at each level;\nregion reported everywhere",
         feeds=["Ch. 3 Dataset", "Ch. 4 Provenance"],
         tables=["a2_d1_funnel", "a2_d1_rejection_reasons", "a2_d1_approval_by_region",
                 "a2_d1_rejection_by_region", "a2_d1_rejection_by_filer_type"],
         figures=["funnel"]),
    dict(id="1.2", group="1", title="Filing reasons and inclusion gates",
         source="A.1 (electric / VTOL / UAV columns), Part B lines G1–G3, rejection reasons of D1.",
         tables_text="one table with the three gates (electric, take-off, UAV) as the machine "
                     "left them and the state after review (`*_final` columns).",
         gives="which patents are eVTOL by rule and which were excluded, so the domain boundary "
               "is explicit. Feeds: Ch. 3 technological domain definition; the V/STOL ruling.",
         gives_short="the domain boundary, by rule",
         feeds=["Ch. 3 Dataset"],
         tables=["a1_inclusion_gates", "a1_inclusion_gates_analysis"],
         figures=[]),
    dict(id="1.3", group="1",
         title="Unit of analysis: unique aircraft, repeated observations, several aircraft per patent",
         source="D7 (duplicate types), aircraft-per-patent table, Part E.1.",
         tables_text="duplicate table (D1 same aircraft new figures · D2 same aircraft same "
                     "figures · D3 same invention modified, with the count identical to root at "
                     "A1). Aircraft drawn per patent.",
         gives="how many independent aircraft there are and how the unit choice changes N; the "
               "double-count at A1 is stated with a number and kept as a sensitivity run. Feeds: "
               "every count in Ch. 4 and Ch. 5; the unit decision (G.4 #1).",
         gives_short="how many independent aircraft;\nthe unit decision",
         feeds=["Ch. 4 Variety", "Ch. 5 Evolution"],
         tables=["a2_d7_duplicates", "a2_d7_d3_identical", "a2_d7_aircraft_per_patent"],
         figures=[]),
    dict(id="1.4", group="1",
         title="Missingness and weak labels: which aircraft enter the analysis",
         source="D4 (structural missingness), D6 (uncertainty flags), D3 note on gearArch = Unknown.",
         tables_text="conditional-fill table; one heatmap of fill rate conditional on parent. "
                     "Flag table. Output of this section: the list of unique aircraft that enter, "
                     "with their sensitivity flags (the roster).",
         gives="a blank is a labelling gap only where the parent says the part exists; on that "
               "test nearly every blank is design absence, so no aircraft is dropped for blanks. "
               "The three real gaps (wing height, planform, tail) are fixed or declared \"not "
               "visible\". Landing gear Unknown means not drawn, never absent. The flagged rows "
               "stay in, marked, and every analysis is run with and without them. Feeds: 1.5 and "
               "1.6 operate on this list; Ch. 4 quality reads the numbers back; Gower δ treatment "
               "in Ch. 5.",
         gives_short="the roster: every aircraft that enters,\nwith its sensitivity flags",
         feeds=["Ch. 4 Quality", "Ch. 5 Evolution"],
         tables=["a2_d4_missingness", "a2_d6_weak_labels", "roster_summary"],
         figures=["fill_rate_heatmap"]),
    dict(id="1.5", group="1", title="Filing-to-publication lag and the right-censoring cut",
         source="D9 (lag table), Part E.2.",
         tables_text="median and 90th-percentile lag by region and by office. Snapshot date.",
         gives="priority years to 2022 are complete, 2023 nearly, 2024–2026 truncated; every "
               "trend claim ends at 2023 and the last window is drawn as partial. This is what "
               "selects the patents that enter the G1–M3 analysis. Priority year is the time axis "
               "because it is the date closest to the design decision; application and "
               "publication years lag it by office-dependent amounts. Feeds: Ch. 3 corpus "
               "boundary; Ch. 5 window definition inherits the cut, does not re-derive it.",
         gives_short="trends end at 2023;\n2024–26 drawn as partial",
         feeds=["Ch. 3 Dataset", "Ch. 5 Evolution"],
         tables=["a2_d9_publication_lag_region", "a2_d9_publication_lag_office", "a1_snapshot"],
         figures=[]),
    dict(id="1.6", group="1", title="Publication timeline",
         source="A.1 time coverage, D9 counts.",
         tables_text="patents per priority year, one bar chart; candidate windows with the "
                     "variants each holds.",
         gives="per-year statistics before 2016 are noise, so windows of 3–5 years rarefied to "
               "n ≈ 40 are needed. Feeds: Ch. 5 window width and rarefaction n. Priority year is "
               "the time axis (closest to the design decision).",
         gives_short="windows of 3–5 years,\nrarefied to n ≈ 40",
         feeds=["Ch. 5 Evolution"],
         tables=["a1_time_coverage_summary", "a1_time_coverage", "a2_d9_windows"],
         figures=["patents_per_year"]),
    # ------------------------------------------------------------------ 2
    dict(id="2.1", group="2", title="Answerable slots at patent and image level",
         source="D2 (label-set properties).",
         tables_text="aircraft-level slot properties (slots, concepts, slots answered per "
                     "aircraft, coverage, near-constant and informative counts); figure-level "
                     "(T2) slots profiled over the approved figures.",
         gives="the 283 columns are slots, not concepts; sparsity is structural (boom groups, "
               "propulsor tiers), so absence is a design fact carried by the parent field. "
               "Feeds: the field shortlist for Ch. 4 and Ch. 5; the derived per-aircraft layer "
               "(D2b, see additions).",
         gives_short="slots ≠ concepts;\nsparsity is structural",
         feeds=["Ch. 4 Variety", "Ch. 5 Evolution"],
         tables=["a2_d2_label_set", "a2_d2_figure_slots"],
         figures=[]),
    dict(id="2.2", group="2", title="Figure basis of each label",
         source="D11.",
         tables_text="approved figures per variant; figure quality; Whole Vehicle Layout share; "
                     "median approved share per patent.",
         gives="every approved primary patent shows at least one whole aircraft (the inclusion "
               "criterion the labelling enforced); the variants that rest on one figure define "
               "the single-figure sensitivity flag. Feeds: Ch. 4 quality sensitivity runs; Ch. 6 "
               "dataset (whole-aircraft figures available to the frozen model).",
         gives_short="one whole-aircraft figure per patent;\nthe single-figure flag",
         feeds=["Ch. 4 Quality", "Ch. 6 Model"],
         tables=["a2_d11_figures_per_variant", "a2_d11_figure_quality", "a2_d11_sensitivity"],
         figures=[]),
    # ------------------------------------------------------------------ 3
    dict(id="3.1", group="3", title="Region, assignee country, publication office",
         source="A.1 metadata (region, assignee_country, pub_office), D1 by region.",
         tables_text="region table; assignee-country table; publication-office table; one bar chart.",
         gives="where the corpus comes from and where the acquisition surplus sits (US "
               "whole-aircraft filings vs drone and component filings elsewhere). Feeds: Ch. 4 "
               "region as a stratum, never as a filter (G.4 #6).",
         gives_short="where the corpus comes from;\nregion as a stratum",
         feeds=["Ch. 4 Provenance"],
         tables=["a1_provenance_region", "a1_provenance_country", "a1_provenance_office"],
         figures=["provenance_bars"]),
    dict(id="3.2", group="3", title="Who filed and how concentrated it is",
         source="D8, plan line G8 (assignee type).",
         tables_text="filer-type table; concentration table on raw string vs canonical company; "
                     "single-patent filers; the strings one firm files under; Lorenz curve.",
         gives="half the corpus is not corporate, which is what makes the assignee-type stratum "
               "worth building; concentration is mild, so pseudo-replication matters mainly in "
               "the tilt-rotor class. Feeds: Ch. 4 Provenance (assignee type); Ch. 5 company "
               "bootstrap and within-company permutation. Still to produce: the `assignee_type` "
               "column (G8).",
         gives_short="half the corpus is not corporate;\nconcentration is mild",
         feeds=["Ch. 4 Provenance", "Ch. 5 Evolution"],
         tables=["a2_d8_filer_mix", "a2_d8_concentration", "a2_d8_single_patent_filers",
                 "a2_d8_split_firms", "a1_assignee_type"],
         figures=["lorenz"]),
    # ------------------------------------------------------------------ 4
    dict(id="4.1", group="4", title="Missingness and uncertainty, read back",
         source="sections 1.4 (D4, D6). No new table.",
         tables_text="none; one paragraph pointing to 1.4.",
         gives="the quality verdict on the labels that entered: which fields carry declared "
               "gaps, how many rows are flagged, and the size of the sensitivity set. Feeds: "
               "reliability paragraph.",
         gives_short="the quality verdict, read back",
         feeds=["Ch. 4 Quality"],
         tables=[], figures=[]),
    dict(id="4.2", group="4", title="Slots answered per aircraft",
         source="D2.",
         tables_text="median, quartiles, maximum; histogram.",
         gives="completeness of one label as a distribution, not a single number. Feeds: "
               "reliability paragraph.",
         gives_short="completeness as a distribution",
         feeds=["Ch. 4 Quality"],
         tables=["a2_d2_slots_quantiles"],
         figures=["slots_histogram"]),
    dict(id="4.3", group="4", title="Consistency rules",
         source="D12 (02a rule-violation counts before and after correction). Partial: only the "
                "batches 02a has been run on.",
         tables_text="one table of rule applications and skips per batch.",
         gives="internal coherence of the labelling; reliability evidence that does not need a "
               "second annotator. Feeds: reliability paragraph.",
         gives_short="internal coherence of the labels",
         feeds=["Ch. 4 Quality"],
         tables=["rules_d12"],
         figures=[]),
    dict(id="4.4", group="4", title="Flagship check",
         source="D13.",
         tables_text="company × labels × public product × verdict.",
         gives="the labels agree with what the world knows where the answer is public; the "
               "disagreements are alternative embodiments, which is itself a sentence in the "
               "thesis. Feeds: external validation in Ch. 4; a short re-read list. Open: whether "
               "the intra-rater re-label (κ per field, 60–100 patents, 4 weeks after last "
               "labelling) enters as 4.5 or is a stated scope decision.",
         gives_short="labels vs public products:\nexternal validation",
         feeds=["Ch. 4 Quality"],
         tables=["a2_d13_flagship_check"],
         figures=[]),
    # ------------------------------------------------------------------ 5
    dict(id="5.1", group="5", title="Most common answers per field, and near-constant fields",
         source="D3 second table, D2 (near-constant fields), A.3 group 2.",
         tables_text="field × answered × answers × top share × most common answers. Separate "
                     "list of the near-constant fields.",
         gives="which answers dominate and which fields cannot separate designs. Near-constant "
               "fields are reported as findings about the boundaries of the design space, then "
               "excluded from distances. Feeds: field shortlist; Ch. 4 descriptive statements.",
         gives_short="which answers dominate;\nwhich fields cannot separate",
         feeds=["Ch. 4 Variety"],
         tables=["a2_d3_selected_fields", "a2_d2_near_constant_fields"],
         figures=[]),
    dict(id="5.2", group="5",
         title="Field inventory: effective number of answers, top share, cumulative",
         source="D2 ranked table (`phase1_field_inventory.csv`).",
         tables_text="ranked table of the informative fields with card, answered, answers, top "
                     "share, effective number, and the cumulative share of the top-2 and top-3 "
                     "answers.",
         gives="which fields carry information; the shortlist for Gower, Cramér's V and "
               "archetypes chosen from evidence. Feeds: Ch. 4 Variety; Ch. 5 methods (Gower field "
               "list, weights).",
         gives_short="the informative-field shortlist",
         feeds=["Ch. 4 Variety", "Ch. 5 Evolution"],
         tables=["a2_d2_informative_fields"],
         figures=[]),
    dict(id="5.2b", group="5", title="Derived per-aircraft features (D2b)",
         source="A.3 group 1 (addition 1).",
         tables_text="total propulsor units, any tilting, mixed fixed and tilting, any ducted, "
                     "all ducted, thrust-axis mix, units per carrier. One table.",
         gives="the sparse boom and tier slots as variables every aircraft has. Feeds: Gower, "
               "Cramér's V, MCA.",
         gives_short="sparse slots → variables\nevery aircraft has",
         feeds=["Ch. 4 Variety", "Ch. 5 Evolution"],
         tables=["a3_derived_layer_summary"],
         figures=[]),
    dict(id="5.3", group="5", title="Archetype cardinality",
         source="D5.",
         tables_text="level × fields × distinct × singletons × effective number.",
         gives="how fine a design species can be before every patent is its own kind; A1 (three "
               "fields) is the counting archetype, finer levels enter only through distances. "
               "Feeds: G.4 #3; Ch. 5 Hill numbers.",
         gives_short="A1 is the counting archetype",
         feeds=["Ch. 5 Evolution"],
         tables=["a2_d5_archetype_cardinality"],
         figures=[]),
    dict(id="5.4", group="5", title="Architecture class balance",
         source="D3 first table.",
         tables_text="architecture type × aircraft × share; bar chart.",
         gives="the class variable is balanced for twelve classes, so classes are large enough "
               "for windows of ~40. Feeds: Ch. 4 Variety; Ch. 6 class list for the frozen model; "
               "merging or dropping of small classes.",
         gives_short="twelve balanced classes",
         feeds=["Ch. 4 Variety", "Ch. 6 Model"],
         tables=["a2_d3_architecture_balance"],
         figures=["class_balance_bars"]),
    dict(id="5.5", group="5", title="Class shares per window",
         source="D9 window table.",
         tables_text="window × variants × share of TR / SLC / CVT / MR; stacked-area figure with "
                     "the partial window hatched.",
         gives="a first look at a shift from tilt rotor to lift plus cruise, and no class above "
               "about a third in any window, so raw shares show no dominant design. This is the "
               "pattern Ch. 5 tests, not assumes. Feeds: Ch. 5 window definition and hypotheses.",
         gives_short="TR → SLC shift to test;\nno dominant design in raw shares",
         feeds=["Ch. 5 Evolution"],
         tables=["a2_d9_architecture_by_window"],
         figures=["class_share_stacked_area"]),
    # ------------------------------------------------------------------ additions
    dict(id="A.6", group="A", title="Named-aircraft state (A.5)",
         source="A.5 (addition 6).",
         tables_text="name proposals by source; what is reviewed and where.",
         gives="proposals exist but none is verified; company-attributed names are statements "
               "about the assignee, not the drawing. One short table if the named-aircraft "
               "stratum stays in RQ3; otherwise a sentence in 3.2.",
         gives_short="names: attributions, not verifications",
         feeds=["Ch. 4 Provenance"],
         tables=["a5_name_proposals", "a5_review_sets"],
         figures=[]),
]

NOT_IN_SCOPE = (
    "Image-vs-text agreement (κ 0.61), Hill numbers, Rao's Q, MCA, permutation tests, kNN "
    "communities. These are results of Ch. 4–7, and the preliminary analysis only has to hand "
    "them a fixed dataset, a field shortlist, an archetype level, a window definition and a "
    "sensitivity-flag list."
)


# --------------------------------------------------------------------------
# accessors
# --------------------------------------------------------------------------
def section(section_id: str) -> Dict:
    for s in SECTIONS:
        if s["id"] == section_id:
            return s
    raise KeyError(section_id)


def sections_of(group_id: str) -> List[Dict]:
    return [s for s in SECTIONS if s["group"] == group_id]


def group(group_id: str) -> Dict:
    for g in GROUPS:
        if g["id"] == group_id:
            return g
    raise KeyError(group_id)


def heading(section_id: str, level: int = 3) -> str:
    s = section(section_id)
    return f"{'#' * level} {s['id']} {s['title']}"


def text(section_id: str) -> str:
    """The three lines of a section, as the markdown the document prints."""
    s = section(section_id)
    return "\n".join([
        f"- **Source**: {s['source']}",
        f"- **Tables / figures**: {s['tables_text']}",
        f"- **Gives →** {s['gives']}",
    ])


def cell(section_id: str) -> str:
    """Heading + three lines, for a notebook markdown cell."""
    return heading(section_id) + "\n\n" + text(section_id)


def feeds_table(section_ids: Optional[List[str]] = None) -> pd.DataFrame:
    """One row per section: what it gives and which chapters it feeds."""
    rows = []
    for s in SECTIONS:
        if section_ids and s["id"] not in section_ids:
            continue
        rows.append({
            "section": s["id"],
            "title": s["title"],
            "gives": s["gives_short"].replace("\n", " "),
            "feeds": " · ".join(s["feeds"]),
        })
    return pd.DataFrame(rows)
