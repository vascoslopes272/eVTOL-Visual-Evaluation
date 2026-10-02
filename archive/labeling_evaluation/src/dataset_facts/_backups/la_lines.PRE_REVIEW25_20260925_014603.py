"""The four short lines under every figure and table, and the Answer under every question.

Author's ruling 2026-09-23 (second reorganisation): the document is **question → graphs →
answer**. A graph carries four short lines and nothing else; the finding is not written under
the graph any more, it is written once, big, at the end of the question the graphs were drawn
to answer.

    Source: Human labelling · PatSeer
    Unit: unique aircraft (665) · priority window · % of the window
    How to read: one sentence.
    Why this way: why this level, this cut, this threshold.

Three of the four are picked from a fixed vocabulary — :data:`SOURCES`, :data:`DATASETS`,
:data:`TIMES`, :data:`NORMS` — so that an advisor reads the same words in the same order under
every item instead of a paragraph of prose. ``How to read`` and ``Why this way`` are written
per item, one sentence each.

The registers are keyed by the INTERNAL item name, never by the printed number, so a
renumbering cannot detach a line from its item. :mod:`la_index` re-exports the accessors and
:mod:`report` prints them; :func:`la_figures._save` reads ``SOURCE`` and ``READ`` from here too,
so the stamp on the PNG and the line under it can never disagree.

Nothing here is deleted when an item is cut from the document: an entry with no item is inert.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# --------------------------------------------------------------------------
# 1 — the vocabularies. Only these values may be used.
# --------------------------------------------------------------------------

#: the only values a ``SOURCE`` entry may hold. tag -> what the tag stands for, printed once
#: in the document's front matter so the tags under the figures can stay one word.
SOURCES: Dict[str, str] = {
    "Human labelling": "the drawings of the {acquired_s} patents read against the codebook in the "
                       "labelling wizard — every morphology field of this document",
    "Whole-patent reading": "the architecture read from the full patent text, independently of the "
                            "drawing — the ground truth the labels are checked against",
    "PatSeer": "the PatSeer bibliographic export (priority and filing dates, applicant and country, "
               "legal status, family, claims, citations, CPC), snapshot 2026-06",
    "CPC-B64 baseline": "all aeronautics patenting (CPC B64) of the same offices and priority years, "
                        "used as the denominator when a count has to be told apart from a trend in "
                        "patenting at large",
    "evtol.news": "the evtol.news public aircraft directory (crawl 2026-09-17), joined to the corpus "
                  "by hand through patent_links.csv",
    "AAM Reality Index": "the AAM Reality Index of SMG Consulting — one 0-10 score per manufacturer, "
                         "May 2026 release and the full history since December 2020, fetched 2026-09-22",
    "NASA TRL": "a technology readiness level per aircraft, assessed against NASA NPR 7123.1D App. E "
                "from public evidence",
    "Codebook": "the codebook itself — a definition, not a measurement",
    "This document": "computed from this document's own registers, not from the data set",
}

#: the only values the ``counts`` slot of a ``UNIT`` entry may hold — what one bar, row, dot or
#: cell IS. The three patent levels are kept apart on purpose: they are different populations.
DATASETS: Dict[str, str] = {
    "acquired patents": "every patent bought from PatSeer",
    "representative patents": "the acquired patents that survive the relevance gate",
    "primary patents": "one patent per unique aircraft — the earliest representative filing of it",
    "aircraft observations": "one labelled aircraft in one patent, before duplicates are merged",
    "unique aircraft": "the analysis set — one row per distinct aircraft design",
    "whole-aircraft figures": "the approved patent drawings that show a complete vehicle",
    "label slots": "the fields of the codebook, not the aircraft",
    "archetypes": "a combination of label answers, at the level the item names",
    "architecture classes": "the twelve classes of card G1",
    "named firms": "an organisation that filed, after the assignee strings are canonicalised",
    "firm pairs": "two firms compared with each other",
    "firm successions": "one firm's aircraft and the next aircraft the same firm filed",
    "field pairs": "two label fields crossed with each other",
    "countries": "the applicant country of the patent",
    "regions": "North America, Europe, Asia-Pacific",
    "offices": "the patent office the document was published at",
    "items of this document": "figures, tables and sections — not a measurement",
}

#: the only values the ``time`` slot may hold.
TIMES: Dict[str, str] = {
    "none": "a snapshot — the whole corpus at once, with no time axis",
    "priority year": "the year of the earliest filing of the family",
    "priority window": "the five windows ≤2011 · 2012-15 · 2016-19 · 2020-23 · 2024-26 (partial)",
    "complete priority years": "priority years to 2023 only — 2024-26 is still filling",
    "publication year": "the year the document was published, not filed",
    "index release": "the quarterly release dates of the AAM Reality Index",
}

#: the only values the ``norm`` slot may hold. An item with a percentage on it MUST say which
#: denominator the percentage is taken on; an item with no time axis must say whether it is
#: normalised at all, and against what.
NORMS: Dict[str, str] = {
    "counts": "raw counts, not normalised",
    "% of the window": "each window is its own 100 %, so the growth of the corpus is divided out",
    "% of the class": "each class is its own 100 %, so the size of the class is divided out",
    "% of the corpus": "share of the whole analysis set",
    "% of the group": "each row or group is its own 100 %",
    "% that state the field": "the denominator is the aircraft whose patent states it, not all of them",
    "against B64 patenting": "divided by all aeronautics patenting of the same years and offices",
    "rarefied": "cut to a common sample size so windows of different size can be compared",
    "against a permutation band": "compared with the range the same data give when the labels are shuffled",
    "leave-one-out (pp)": "the difference in percentage points when one firm is taken out",
    "per firm": "divided by the firm, not by the aircraft",
    "per aircraft": "divided by the aircraft, not by the patent",
}


def _u(counts: str, n: str = "", time: str = "none", norm: str = "counts") -> Dict[str, str]:
    """One UNIT entry. ``n`` is a placeholder like ``{unique_s}`` or a literal count."""
    return dict(counts=counts, n=n, time=time, norm=norm)


UA = "unique aircraft"

# --------------------------------------------------------------------------
# 2 — the four questions, and which items answer each of them
# --------------------------------------------------------------------------
# Author's ruling 2026-09-23: the eight questions fold to four. Q1+Q8 -> A, Q2+Q3+Q4 -> B,
# Q5+Q7 -> C, Q6 -> D. M (the method question, RQ4) is not a sector question and stays in the
# data-quality appendix. ORDER IS PRINTED ORDER.

QUESTIONS4: Dict[str, str] = {
    "1": "Is the patent record a usable indicator of the sector — is it early, is it live, "
         "and does it describe the aircraft the industry actually builds?",
    "2": "What is being designed, and is the sector converging on a dominant design?",
    "3": "Who designs it — is the field concentrated among incumbents, or open to entrants?",
    "4": "Where is it designed, and does the jurisdiction change what is designed?",
    "M": "Method (RQ4): does the figure alone carry the architecture the text states — "
         "not a question about the sector, and printed in Appendix B",
}

#: the proposed running order: chapter -> [(section title, [item names])]. Chapters 1-4 are the
#: four questions; the appendices keep their letters and their contents. The items listed are the
#: ones that survive; :data:`CUT` holds the rest with the reason. Nothing is deleted from
#: ``la_tables`` or ``la_figures`` — a cut item keeps its builder and its CSV.
ORDER: Dict[str, List] = {
    "1": [
        ("How much record there is, and which years can be read",
         ["filings_per_year", "la_filings_per_year", "a2_d9_publication_lag_region"]),
        ("How live it is: what lapsed and what was refused",
         ["abandonment", "examination", "la_examination_office"]),
        ("Does the patent clock lead the market clock",
         ["ari_clock", "la_ari_timeline"]),
        ("Does the record describe what is built",
         ["atlas_flagship", "ari", "la_ari_firms", "la_ari_gap",
          "la_market_vs_patents", "linked_check", "la_class_fold", "la_mission_status"]),
    ],
    "2": [
        ("The mix, and how it moves",
         ["atlas_arch_time", "class_cycles"]),
        ("The dominant-design test",
         ["la_archetype_levels", "la_archetype_choice", "la_dd_conditions",
          "dominant_design", "dominant_design_q", "la_dd_result", "la_dominant_design", "la_dd_q"]),
        ("Inside a class: does one configuration settle",
         ["class_configs", "dimension_drift"]),
        ("Crowded and open zones of the design space",
         ["zones"]),
        ("What the design space is made of",
         ["atlas_units", "atlas_design_heatmaps", "a2_d3_selected_fields", "atlas_fields"]),
        ("Design drivers and their traces",
         ["trace_drift", "trace_couplings", "la_driver_verdicts", "la_driver_questions"]),
    ],
    "3": [
        ("Coverage: who holds the corpus",
         ["coverage", "la_filer_mix", "la_filers_by_window"]),
        ("Entry, and what new firms arrive with",
         ["filers_over_time", "la_cohort_mix", "transitions"]),
        ("Can one firm move the reading",
         ["firm_influence", "filer_weight", "la_class_filer_weight", "la_firm_leverage"]),
        ("How firms build a portfolio",
         ["atlas_filers", "ip_strategy", "la_ip_strategy"]),
    ],
    "4": [
        ("Where the filings come from",
         ["atlas_region", "country_class"]),
        ("Does region change the design",
         ["region_grid", "region_grid_b", "proximity_region", "specialisation"]),
        ("Does region change the timing",
         ["lead_lag", "la_class_region_timing"]),
    ],
}

#: the appendices, unchanged in purpose and in letter. Appendix B also carries the method
#: question M, which is not a sector question and must never be counted as a sector finding.
APPENDIX_ORDER: Dict[str, List] = {
    "A": [
        ("How the data set was built",
         ["fig_02_refinement_funnel", "atlas_removal"]),
        ("Refinement 1 — representativity", ["a2_d1_similars", "a2_d1_filing_status"]),
        ("Refinement 2 — observations to unique aircraft", ["atlas_duplicates", "a2_d7_duplicates"]),
        ("Refinement 3 — figure approval", ["atlas_figure_approval", "a2_d11_figure_approval"]),
    ],
    "B": [
        ("Missingness", ["atlas_fill"]),
        ("The image label against the whole-patent reading (question M)",
         ["atlas_arch_gt", "la_mission_agreement", "atlas_state_by_arch",
          "la_name_arch_check", "la_relabel_protocol", "a2_d2_figure_slot_answers"]),
    ],
    "C": [
        ("The inventory, by question", ["la_open_questions"]),
    ],
    "D": [
        ("The codebook", ["codebook_classes", "codebook_dimensions"]),
    ],
}

#: item -> why it is not printed. Every cut item keeps its builder and its CSV in ``tables/``;
#: putting the name back in :data:`ORDER` is all it takes to print it again. The author decides
#: — this register is the list he asked for, not a removal.
CUT: Dict[str, str] = {
    # restates the figure above it, number for number
    "la_class_configs": "restates Figure B.3a; the figure carries the same shares",
    "la_dimension_drift": "restates Figure B.3b",
    "la_zones": "restates the zones figure; the CSV keeps the per-archetype counts",
    "la_trace_couplings": "restates the couplings figure",
    "la_abandonment_by_class": "the class column is a null; the base rate is in the figure",
    "a2_d13_flagship_check": "restates the flagship figure",
    "a2_d4_missingness": "restates the fill figure",
    "a2_d2_informative_fields": "restates the field-inventory figure",
    "la_lead_lag_region": "three rows, and the figure prints them",
    "la_lead_lag_class": "restates the class shares one window at a time",
    # nothing survives in it
    "la_examination_class": "a null: every class sits at the same grant rate — one sentence in the Answer",
    "la_ip_by_class": "citations follow age, not class; the cohort rank replaces it",
    "a2_d8_concentration": "a name-cleaning artefact, not a finding about the sector",
    "la_ari_correlation": "57 tests on 9-18 firms, none survives the correction — one sentence in the Answer",
    "hill": "no window separates from any other; condition 2 of the dominant-design test carries it",
    "la_hill_by_window": "every band overlaps every other",
    "spans_by_firm": "the re-filing count is a filing habit, not a design statement",
    "la_proximity_region": "136 pairs from 17 firms; the figure states the null",
    "la_ari_clock_region": "no row rests on more than five firms",
    "la_ari_history": "a segment of a segment — nine firms disclose funding",
    "ari_history": "nine firms disclose funding; the score history adds nothing the score does not",
    # the mission block: one honest paragraph in the Answer of A, and the proof kept
    "mission": "95 self-selected aircraft, half of them unspecified — Appendix C states it once",
    "industry_by_class": "345 of 665 unspecified, and the field comes from an unverified text classifier",
    "la_mission_capacity": "95 aircraft over five folded classes, cells of 0-12",
    "la_mission_piloting": "mostly unstated; cannot be used as a variable",
    "la_mission_power source": "confirms the electric gate on 95 aircraft; the gate is already stated",
    # replaced
    "la_trl_placeholder": "a promise, not a measurement — replaced by the TRL table now that the CSV exists",
    "atlas_powertrain": "the electric gate restated; Figure B.3b panel (v) carries the drift",
    "design_space_cards": "duplicates the codebook class drawing of Appendix D",
    "a2_d7_aircraft_per_patent": "one number: 1 patent = 1 aircraft almost everywhere",
    "la_flags": "superseded by this register — the cut list is here, with the reason",
}

# --------------------------------------------------------------------------
# 3 — the registers, in the order of :data:`ORDER`
# --------------------------------------------------------------------------

SOURCE: Dict[str, List[str]] = {}
UNIT: Dict[str, Dict[str, str]] = {}
READ: Dict[str, str] = {}
WHY: Dict[str, str] = {}


def _item(name: str, source: List[str], unit: Dict[str, str], read: str, why: str) -> None:
    """Register one item's four lines. One call per item; a repeated name is an error."""
    if name in SOURCE:
        raise KeyError(f"la_lines: {name} registered twice")
    SOURCE[name] = source
    UNIT[name] = unit
    READ[name] = read
    WHY[name] = why


HL = "Human labelling"
PS = "PatSeer"
WPR = "Whole-patent reading"
EVN = "evtol.news"
ARI = "AAM Reality Index"
B64 = "CPC-B64 baseline"
TRL = "NASA TRL"
CB = "Codebook"
DOC = "This document"

# ============================================================ A — the record as an indicator
_item("filings_per_year", [PS, HL, B64],
      _u(UA, "{unique_s}", "priority year", "against B64 patenting"),
      "(i) bars: unique aircraft per priority year; line: the acquired patents. (ii) three lines, one "
      "per baseline, each built in three steps — aeronautics for example: (1) for each priority year, "
      "this corpus's eVTOL patents divided by ALL aeronautics patents (CPC B64) filed at the same nine "
      "offices with that year: 2018, 193 of about 10 400, 18.6 per 1 000; (2) the same fraction averaged "
      "over 2005-09, 5.6 per 1 000, is the starting level; (3) each year's fraction divided by the "
      "starting level is the point drawn, so every line starts at 1 and 2018 reads \u00d73.3. The other "
      "two lines repeat the recipe with all CPC section-B patents (transport and operations) and with "
      "all patents of any kind as the denominator; the starting level is only what lets three fractions "
      "of very different size share one axis. Complete years only. Source of the three baselines: WIPO "
      "PATENTSCOPE, counted by priority year at the corpus's nine offices; CPC B64* includes B64U, "
      "the UAV class created in 2022.",
      "Years are used, not windows, because the question is when the record starts; 1999-2005 is "
      "pooled into one bar because no single year in it reaches five aircraft, and the last years "
      "are hatched because the snapshot is inside their publication lag.")

_item("la_filings_per_year", [PS, HL, B64],
      _u(UA, "{unique_s}", "priority year", "against B64 patenting"),
      "Every year has its own row, with the B64 count of that year beside it and the two ratio columns.",
      "The table keeps the years the figure pools, so the pooling cannot hide a year.")

_item("a2_d9_publication_lag_region", [PS],
      _u("representative patents", "{representative_s}", "priority year", "counts"),
      "The months between priority and publication, by region; the 90th percentile is the line the "
      "document treats a year as incomplete below.",
      "It is here and not in the appendix because it fixes the 2023 cut-off every trend in this "
      "chapter is read to.")

_item("abandonment", [PS, HL],
      _u("primary patents", "{primary_s}", "priority year", "% of the class"),
      "The share of each class's patents whose legal status starts INACTIVE at the snapshot; the "
      "cohort is priority 2019 or earlier so every patent has had the same time to lapse.",
      "The cohort is fixed at 2019 because a lapse takes years: comparing all years would measure "
      "how old each class is, not whether it is abandoned.")

_item("examination", [PS, HL],
      _u("primary patents", "{primary_s}", "none", "% of the group"),
      "Grant, refusal and withdrawal shares, by office and by class.",
      "Office and class are shown side by side because the office difference is large and the class "
      "difference is not — showing only the class panel would invite a technology reading of an "
      "administrative fact.")

_item("la_examination_office", [PS],
      _u("primary patents", "{primary_s}", "none", "% of the group"),
      "One row per office, with the number of patents it examined.",
      "Offices with fewer than 20 patents are pooled: a grant rate on five patents is noise.")

_item("ari_clock", [ARI, PS, HL],
      _u("named firms", "13", "priority year", "counts"),
      "Each firm's first, peak and last patent year against the dates the index states for it — "
      "first flight, certification target, entry into service.",
      "Only the 13 firms in the current release are drawn: the five the index has dropped carry no "
      "dates, so a bar for them would be half empty and would read as a late programme.")

_item("la_ari_timeline", [ARI, PS, HL],
      _u("named firms", "13", "priority year", "counts"),
      "Years from the firm's earliest patent in this corpus to the dates the index states.",
      "The gap columns are subtractions from the firm's earliest priority year here, which is a "
      "lower bound: a firm may have filed before it entered this corpus.")

_item("atlas_flagship", [HL, EVN, PS],
      _u("named firms", "19", "none", "% of the group"),
      "For each firm with a publicly known flagship aircraft, whether the class in the corpus "
      "matches the class of that aircraft.",
      "Firms are the unit, not aircraft: the check asks whether the record finds the aircraft the "
      "firm is known for, which is a statement about the firm.")

_item("la_name_arch_check", [HL, WPR, EVN],
      _u(UA, "51", "none", "counts"),
      "The 51 aircraft where the drawing label, the text reading and the public source do not all "
      "agree, named one by one.",
      "Listed by name rather than counted, because the value of a disagreement is that a reader can "
      "check it.")

_item("ari", [ARI, PS, HL],
      _u("named firms", "{n_ari}", "none", "counts"),
      "The index score and the disclosed funding of each rated firm, against the aircraft it holds here.",
      "Nothing is normalised and no line is fitted: 18 firms support a description, not a model.")

_item("la_ari_firms", [ARI, PS, HL],
      _u("named firms", "{n_ari}", "none", "counts"),
      "One row per rated firm: its score, its funding and its aircraft in this corpus.",
      "The whole segment is printed rather than a top slice, so a reader can see the firms the index "
      "covers and the ones it does not.")

_item("la_ari_gap", [ARI, HL, PS],
      _u(UA, "{tk_ari_in} against {tk_ari_rest}", "none", "% of the group"),
      "Index firms = the 18 manufacturers the AAM Reality Index has ever scored that file in this "
      "corpus; their {tk_ari_in} aircraft against the other {tk_ari_rest}. One test per row: Mann-Whitney for a "
      "number (do the two groups have the same median), Fisher exact for a yes/no field, chi-square "
      "for a category. p = the chance of a gap this large if the groups were the same; q = the same "
      "p corrected for running many tests at once (Benjamini-Hochberg), read below 0.05. The last "
      "column re-runs the test on US-published patents only, so an office effect cannot pass as a "
      "firm effect.",
      "The unit is the aircraft and not the firm because the firm-level correlations do not survive "
      "the correction for multiple testing and the aircraft-level differences do.")

_item("a2_d16_public_match", [HL, WPR, EVN],
      _u(UA, "98", "none", "% of the group"),
      "For the 98 aircraft whose firm has a public product of the same name (evtol.news, matched by "
      "hand), whether the drawing label, the whole-patent text reading and the public aircraft carry "
      "the same class. 'Drawing label differs from the text' = the labeller read the figure one way "
      "and the patent's own description says another; 'text matches the public aircraft' = the "
      "description agrees with what the firm built.",
      "Counted on the aircraft that CAN be matched: a patent with no public product cannot be checked "
      "and is not a disagreement.")

_item("a2_d15_trl_by_class", [TRL, HL, EVN],
      _u(UA, "{unique_s}", "none", "% of the class"),
      "TRL per aircraft on NASA's 1-9 scale, assessed by the author from public evidence (evtol.news "
      "pages, company statements): TRL 2 = patent only, nothing built; 3-5 = component or subscale "
      "tests; 6-7 = full-scale prototype flown; 8-9 = certified or in service. An aircraft no public "
      "source follows is TRL 2 by construction.",
      "Banded rather than per level because the evidence rarely supports a one-level distinction.")

_item("la_trl_representativeness", [TRL, HL, PS],
      _u(UA, "64 against 601", "none", "% of the group"),
      "The 64 aircraft above TRL 2 against the other 601 (665 − 64), one attribute at a time and never "
      "jointly: how the 64 spread over the attribute's levels (the classes, the regions, the windows…) "
      "against how the 601 spread; chi-square for a category, Mann-Whitney on the median for a "
      "number. p below 0.05 = the two spreads differ, and the 64 cannot stand for the corpus on that "
      "attribute. 'largest gap' names the level the two groups differ most on.",
      "Same test as the evtol.news and index-firm checks, so every subset is judged by one rule.")

_item("la_ari_representativeness", [ARI, HL, PS],
      _u(UA, "{tk_ari_in} against {tk_ari_rest}", "none", "% of the group"),
      "The {tk_ari_in} aircraft of the 18 index firms against the other {tk_ari_rest}, one attribute at a time, the "
      "same test as the TRL check.",
      "Before anything is correlated with the index, the reader sees on which attributes the index "
      "firms' aircraft are and are not like the rest.")

_item("la_public_pairwise", [HL, WPR, EVN],
      _u(UA, "98", "none", "% of the group"),
      "Three sources of a class — the drawing label (wizard), the patent text (whole-patent "
      "reading), the public aircraft (evtol.news, matched by name) — compared two at a time on the "
      "98 aircraft that have a public counterpart.",
      "Two at a time, because each pair fails for a different reason and one agreement number hides "
      "which.")

_item("la_top_archetypes", [HL],
      _u("archetypes", "", "priority window", "% of the window"),
      "Per level and window: the three largest archetypes with their share of the window's "
      "aircraft, and what the top 3 and top 5 hold together. A0 = the class; A1t = class · wings · "
      "tilting or not (the design species); A0c = class · propulsive-unit band.",
      "Printed because 'no archetype above 50 %' says what is absent; this says what is there — "
      "how many designs share the corpus, and whether the same ones do so window after window.")

_item("la_era_frame", [CB, HL],
      _u("items of this document", "4", "none", "counts"),
      "The interpretive frame: what each measure does in an era of ferment, while a dominant design "
      "emerges, and under incremental change — and, in the last column, what this corpus shows. "
      "Rao's Q and ²D are conditions 3 and 2 of the test; the centroid shift and the locus of "
      "innovation are not computed in this document.",
      "The four measures are the author's own framework (methodology, Part C); printing the frame "
      "beside the test says which era the verdict places the sector in.")

_item("la_class_configs_own", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "Each class read on its OWN differentiating labels — the rule is printed per row — never on "
      "the wing, boom or tail the class already fixes. The share is a mode, not a mean: a "
      "configuration is a combination of categories and has no average.",
      "A class-window under five aircraft is left blank; the rules were fixed on 2026-09-24 before the "
      "table was read.")

_item("la_duct_count", [HL],
      _u(UA, "632", "none", "% of the group"),
      "Per propulsive-unit band: the aircraft with any ducted unit, the share of the band's UNITS that "
      "are ducted, the share of aircraft that duct every unit, and the median ducted units among the "
      "ducting aircraft — read from the M3 propulsor groups, each of which carries a count and a "
      "ducted/open answer.",
      "Counted in units as well as in aircraft, because one ducted fan among twelve open rotors is "
      "not the same design as twelve ducted fans.")

_item("sm_class_configs", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "(i) share of the class in its most common configuration, on the class's own labels; (ii) "
      "distinct configurations per aircraft — 1.0 would mean every aircraft is different.",
      "Per-class labels (rules in the table above), so a class is not called diverse merely because "
      "the codebook has fifty fields.")

_item("sm_duct_count", [HL],
      _u(UA, "632", "none", "% of the group"),
      "Hollow bar: aircraft with at least one ducted unit. Filled bar: of all the band's units, the "
      "share in a duct. On the bar: the median ducted units of the ducting aircraft, and the share "
      "that duct every unit.",
      "Units and aircraft side by side: the two diverge exactly where ducting is a whole-array choice.")

_item("sm_entry_all", [PS, HL],
      _u("named firms", "", "priority window", "% of the group"),
      "Per class: the class's share of the firms ENTERING in that window (hatched, count on the bar) "
      "beside its share of the window's AIRCRAFT (grey). An entrant is counted once, in the window "
      "of its first filing.",
      "The five largest classes only; a class with three entrants in a window cannot carry a share.")

_item("sm_weighting", [HL, CB],
      _u(UA, "{unique_s}", "priority window", "against a permutation band"),
      "Condition 3 (the aircraft becoming alike) per window, under the two weightings of the Gower "
      "distance: subsystem (each subsystem one unit of weight, the Preliminary Analysis's main "
      "choice) and uniform (every field one unit). A ringed point is below its band = the condition "
      "met.",
      "Both weightings are drawn because the condition fires under one and not the other, and a "
      "reader has to see that rather than be told it.")

_item("sm_archetype_filers", [PS, HL],
      _u("archetypes", "", "none", "per aircraft"),
      "Distinct filers per aircraft for every archetype of twenty aircraft or more: 1.0 = no filer "
      "holds two of its aircraft; the lower, the more one firm's line of variants.",
      "Twenty aircraft or more, because a ratio on five aircraft moves a full step on one firm.")

_item("la_market_vs_patents", [ARI, PS, HL],
      _u("named firms", "", "none", "per firm"),
      "Medians per firm for the rated and the unrated group, with a rank test between them.",
      "Medians, not means: one firm with 60 aircraft would otherwise carry the comparison.")

_item("linked_check", [EVN, HL, PS],
      _u(UA, "95", "none", "% of the group"),
      "The 95 aircraft with a public page against the rest of the corpus, one attribute per panel.",
      "It is printed before anything that uses the linked set, because that set is the only part of "
      "the corpus a public source can check and it is not representative on four of six attributes.")

_item("la_class_fold", [HL, EVN, CB],
      _u("architecture classes", "12 into 5", "none", "counts"),
      "Which of the twelve codebook classes falls into each of the five public-directory classes.",
      "The fold is printed rather than assumed, because it is lossy: it is the only way the two "
      "vocabularies can be compared at all.")

_item("la_mission_status", [EVN, HL],
      _u(UA, "95", "none", "% of the group"),
      "The development status of the linked aircraft, by folded class.",
      "Kept from the mission block because status is stated for almost every linked aircraft, while "
      "mission, capacity and piloting are not.")

# ============================================================ B — what is designed, and convergence
_item("atlas_arch_time", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the window"),
      "Each bar is one window at 100 %; the n of the window is printed under it.",
      "Windows, not years, because a single year holds too few aircraft of a small class for a share "
      "to mean anything; the two rarest classes are pooled for the same reason.")

_item("class_cycles", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "Each bar is one class at 100 %, split by window: where in time that class's own filings sit.",
      "Deliberately divided by the class and not by the window — the question here is the lifetime of "
      "a class, which the window view cannot show for a small class.")

_item("la_archetype_levels", [HL, CB],
      _u("archetypes", "", "none", "counts"),
      "Every archetype level the codebook can form, with how many archetypes it yields and how "
      "concentrated they are.",
      "Printed before the test because the answer to the convergence question depends on the level "
      "it is asked at, and the level must be chosen in the open.")

_item("la_archetype_choice", [HL, CB],
      _u("archetypes", "", "none", "counts"),
      "The four screens applied to the previous table, and which levels clear them.",
      "The screens are fixed in code (`la_tables.ARCHETYPE_SCREENS`) so the level is not chosen after "
      "seeing the result.")

_item("la_dd_conditions", [CB],
      _u("items of this document", "3", "none", "counts"),
      "The three conditions, their thresholds, and where each threshold comes from.",
      "No number of this corpus enters this table: the thresholds were fixed in the Preliminary "
      "Analysis before any curve here was drawn.")

_item("dominant_design", [HL],
      _u("archetypes", "", "priority window", "against a permutation band"),
      "(i) the largest archetype's share of its window against the 50 % line; (ii) and (iii) the "
      "evenness ²D against the band the same data give with the labels shuffled.",
      "Both levels are drawn, A1t as the design species and A0c beside it, because condition 2 fires "
      "only at A0c and hiding that would hide the only balance signal the test finds.")

_item("dominant_design_q", [HL],
      _u(UA, "{unique_s}", "priority window", "against a permutation band"),
      "How spread out the space is per window, against the level of the two earliest windows and the "
      "permutation band.",
      "Reported under the subsystem weighting the Preliminary Analysis fixes, with uniform weighting "
      "beside it as the robustness check that ruling requires.")

_item("la_dd_result", [HL, DOC],
      _u("items of this document", "3", "priority window", "counts"),
      "One generated sentence per condition; every number in it is read from the tables below.",
      "Generated rather than typed, so the verdict cannot drift away from the numbers it rests on.")

_item("la_dominant_design", [HL],
      _u("archetypes", "", "priority window", "rarefied"),
      "Top share and rarefied ²D per window, with the permutation band beside them.",
      "²D is rarefied to 40 aircraft because the windows differ in size and evenness falls with "
      "sample size on its own.")

_item("la_dd_q", [HL, CB],
      _u(UA, "{unique_s}", "priority window", "against a permutation band"),
      "Rao's quadratic entropy of the Gower distance per window, at both levels, under both weightings.",
      "The distance is imported from the Preliminary Analysis rather than redefined here, so the "
      "convergence test and the embedding work measure the same space.")

_item("class_configs", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "(i) how much of a class sits in its single most common configuration; (ii) how many distinct "
      "configurations that class holds per aircraft.",
      "A configuration is four fields only — units banded, ducted, booms, tail — because a finer key "
      "makes almost every aircraft unique and the question unanswerable; a class-window under five "
      "aircraft is left blank rather than drawn.")

_item("dimension_drift", [HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "The four fields of the configuration read one at a time, then powertrain, per class.",
      "Every share is of the class's own aircraft in that window, so a class growing does not move "
      "its own line; the powertrain panel divides by the aircraft whose patent states a powertrain "
      "and says so on the panel.")

_item("zones", [HL, PS],
      _u("archetypes", "{n_zones}", "priority window", "% of the window"),
      "(top) how crowded each archetype is against how many filers it has; (bottom) its activity per "
      "window.",
      "Only archetypes with five or more aircraft are drawn, and the crowding is read on the two "
      "complete windows 2016-23 — an archetype with three aircraft cannot be called crowded or open.")

_item("atlas_units", [HL],
      _u(UA, "{unique_s}", "none", "% of the corpus"),
      "How many propulsive units an aircraft has, how they are arranged, and how ducting varies with "
      "the count.",
      "The ducting panel is cut by rotor count rather than by year or region because that is the cut "
      "the relation actually follows (U-shaped, p 0.0001).")

_item("atlas_design_heatmaps", [HL],
      _u("field pairs", "", "none", "% of the class"),
      "Two label fields crossed; the colour is the share of the row.",
      "Definitional pairs are excluded — a pair that the codebook forces to agree would print as a "
      "perfect association and mean nothing.")

_item("a2_d3_selected_fields", [HL],
      _u("label slots", "", "none", "% that state the field"),
      "The most common answer of each field, and how much of the corpus holds it.",
      "The denominator is the aircraft that carry an answer, not all of them, so a sparsely answered "
      "field is not made to look rare.")

_item("atlas_fields", [HL, CB],
      _u("label slots", "42", "none", "counts"),
      "How much of the corpus each of the 42 slots is answered for, and which slots carry information.",
      "A field answered the same way for almost every aircraft is marked uninformative rather than "
      "dropped, because its constancy is itself a finding about the design space.")

_item("trace_drift", [HL],
      _u(UA, "{unique_s}", "complete priority years", "% of the class"),
      "Each labelled trace against priority year, inside each class, with the trend test on it.",
      "Inside a class, never pooled: the class mix moves on its own, and a pooled line would credit "
      "that movement to a design driver.")

_item("trace_couplings", [HL],
      _u("field pairs", "435", "none", "counts"),
      "Bias-corrected Cramér's V for every pair of fields, with the pairs the drivers predict marked.",
      "31 definitional pairs are excluded and named; without that exclusion the strongest associations "
      "in the figure would be the codebook talking to itself.")

_item("la_driver_verdicts", [HL, CB],
      _u("items of this document", "22", "complete priority years", "counts"),
      "One row per trace: what moved, which drivers predict it, and the verdict.",
      "A trace with several plausible drivers is called overdetermined rather than assigned to one — "
      "the patents cannot separate them.")

_item("la_driver_questions", [HL, DOC],
      _u("items of this document", "", "none", "counts"),
      "The three answers the verdict table supports, generated from it.",
      "Generated from the verdicts so the wording cannot drift from the table above it.")

# ============================================================ C — who designs it
_item("coverage", [PS, HL],
      _u("named firms", "", "none", "% of the corpus"),
      "The cumulative share of the corpus covered by the top N firms, cut into four segments.",
      "Every share is taken on the whole analysis set, not on the corporate part of it, so the "
      "curve says what one firm is worth against the sector and not against other firms.")

_item("la_filer_mix", [PS, HL],
      _u("primary patents", "{primary_s}", "none", "% of the corpus"),
      "Patents and aircraft per filer type, with the aircraft-per-patent ratio beside them.",
      "Both units are printed because a filer type can hold many patents on few aircraft, which is a "
      "different statement about the sector.")

_item("la_filers_by_window", [PS, HL],
      _u("named firms", "", "priority window", "counts"),
      "How many firms are active in each window, and the aircraft they hold.",
      "Firms and aircraft are counted separately in the same table: the two grow at different rates, "
      "which is the finding.")

_item("filers_over_time", [PS, HL],
      _u("named firms", "", "priority window", "counts"),
      "(i) firms entering and last seen per window; (ii) what the entrants of a window arrive with, "
      "against the mix of that window.",
      "An entrant is counted once, in the window of its first filing, so a firm that files for a "
      "decade cannot be counted as an entrant twice.")

_item("la_cohort_mix", [PS, HL],
      _u("named firms", "", "priority window", "% of the group"),
      "The class mix the entrants of a window arrive with, against the mix of the window itself.",
      "Two denominators in one row — the entrants, and the window's aircraft — because the difference "
      "between them is the quantity of interest.")

_item("transitions", [PS, HL],
      _u("firm successions", "", "priority year", "% of the class"),
      "Where a firm's next aircraft goes, given the class of its previous one.",
      "The unit is the pair, not the aircraft: a firm with one aircraft makes no pair and is absent by "
      "construction, which is why the firm count here is lower than in the coverage figure.")

_item("firm_influence", [PS, HL],
      _u("named firms", "", "none", "leave-one-out (pp)"),
      "How far each class share moves when one firm is taken out of the corpus.",
      "Taken on the whole analysis set re-counted without the firm, which is the only version of this "
      "number a reader can check against the class shares printed elsewhere.")

_item("filer_weight", [PS, HL],
      _u(UA, "{unique_s}", "priority window", "% of the class"),
      "How much of a class its largest filer holds, and the same inside each window.",
      "An individual inventor's patent counts as its own filer, so two lone inventors are never merged "
      "into one; a class-window under ten aircraft is not drawn.")

_item("la_class_filer_weight", [PS, HL],
      _u(UA, "{unique_s}", "none", "% of the class"),
      "Per class: the largest filer's share, and the effective number of filers.",
      "Effective filers (1/Σ share²) is printed beside the count because a count says how many filers "
      "there are and not how unevenly they divide the class.")

_item("la_firm_leverage", [PS, HL],
      _u("named firms", "", "priority window", "leave-one-out (pp)"),
      "The same leave-one-out shift, per firm, in the corpus and in the firm's strongest window.",
      "Both are given because a firm too small to move the corpus can still carry a single window.")

_item("atlas_filers", [PS, HL],
      _u("primary patents", "{primary_s}", "none", "% of the corpus"),
      "(i) the largest companies; (ii) the aircraft of each filer type; (iii) the Lorenz curve of "
      "patents over filers.",
      "The Lorenz curve is on patents and the bars on aircraft, and each says so: the corpus is more "
      "concentrated in patents than in designs.")

_item("ip_strategy", [PS, HL],
      _u("named firms", "{n_firms5}", "none", "per aircraft"),
      "Patents per aircraft against aircraft held; the bubble is the firm's mean forward citations.",
      "Only firms with five or more aircraft are drawn: a ratio on two aircraft is not a strategy.")

_item("la_ip_strategy", [PS, HL],
      _u("named firms", "{n_firms5}", "none", "per firm"),
      "Depth, breadth, claims and citations per firm, with the citation rank taken inside the "
      "priority-year cohort.",
      "Citations are ranked inside the cohort because an older patent has had longer to be cited — "
      "the raw count ranks classes by age.")

# ============================================================ D — where
_item("atlas_region", [PS, HL],
      _u("countries", "", "none", "% of the corpus"),
      "(i) the twelve largest applicant countries; (ii) the aircraft of each region; (iii) the office "
      "the document was published at.",
      "Applicant country and publication office are kept apart: where a firm is and where it files are "
      "different facts, and the second is a filing strategy.")

_item("country_class", [PS, HL],
      _u("countries", "", "none", "% of the group"),
      "The class mix of each of the largest countries.",
      "Only countries above 25 aircraft are drawn; below that a class share moves by more than ten "
      "points on one filing.")

_item("region_grid", [PS, HL],
      _u("regions", "3", "priority window", "% of the group"),
      "Three design variables per region over time, each region its own 100 %.",
      "Three regions only, because every other region is under 25 aircraft and would print a line "
      "that jumps between 0 and 100 %.")

_item("region_grid_b", [PS, HL],
      _u("regions", "3", "priority window", "% of the group"),
      "Filer type per region over time.",
      "Kept as a figure of its own rather than a fourth row of the grid: four rows do not fit an A4 "
      "text block, and the figure would have had to be shrunk to fit.")

_item("proximity_region", [PS, HL],
      _u("firm pairs", "{n_prox_firms} firms", "none", "counts"),
      "How alike two firms' class profiles are, firms grouped by region.",
      "A firm's profile is its own aircraft spread over the classes, so a firm with 60 aircraft and a "
      "firm with 5 can be compared at all.")

_item("specialisation", [PS, HL],
      _u("archetypes", "{n_special}", "none", "% of the corpus"),
      "Which archetypes a region holds more of than its size would give it.",
      "Readable only above roughly ten aircraft per archetype-region cell, and the cells below that "
      "are left grey rather than coloured.")

_item("lead_lag", [PS, HL],
      _u(UA, "{unique_s}", "complete priority years", "% of the group"),
      "The year each region, and each class, passes 25, 50 and 75 % of its own filings.",
      "Each group is measured against its own total, so a large region does not automatically look "
      "early; complete years only, because the incomplete tail would pull every group late.")

_item("la_class_region_timing", [PS, HL],
      _u(UA, "{unique_s}", "complete priority years", "counts"),
      "The median priority year of each class inside each region.",
      "A median, so one very early filing cannot move a cell; a cell under five aircraft prints a dash "
      "instead of a year.")

# ============================================================ M — method
_item("atlas_arch_gt", [HL, WPR],
      _u(UA, "{unique_s}", "none", "% of the class"),
      "The drawing label against the whole-patent reading, class by class.",
      "Read per class rather than as one agreement number, because the agreement is good for the large "
      "winged classes and poor for the small ones, and one number would hide both.")

_item("la_mission_agreement", [EVN, HL],
      _u(UA, "95", "none", "% of the group"),
      "The folded label against the class the public directory gives the same aircraft.",
      "On the folded five-class vocabulary, the only level at which the two sources can be compared.")

_item("atlas_state_by_arch", [HL],
      _u("whole-aircraft figures", "{figures_approved_s}", "none", "% of the class"),
      "Which flight state the approved drawings show, per class.",
      "A property of the drawings, not of the aircraft: a patent draws the state it claims, which is "
      "why this bounds the labelling and is not a finding about design.")

_item("la_relabel_protocol", [HL],
      _u(UA, "50", "none", "counts"),
      "The protocol for the intra-rater relabel — what is drawn, when, and what would count as "
      "agreement.",
      "Printed before the result exists so the protocol cannot be written to fit the number.")

_item("a2_d2_figure_slot_answers", [HL],
      _u("whole-aircraft figures", "{figures_approved_s}", "none", "% that state the field"),
      "How many of the 42 slots a single drawing can answer.",
      "A property of the drawings, not of the aircraft — it bounds what the image side of the "
      "thesis can be asked to recover.")

# ---------------------------------------------------------------- Appendix A — construction
_item("fig_02_refinement_funnel", [PS, HL],
      _u("acquired patents", "{acquired_s}", "none", "counts"),
      "Each level of the funnel and what left it, so the arithmetic closes on the figure.",
      "Every stage is counted on the stage above it, so no level can be quoted against the wrong "
      "denominator later.")

_item("atlas_removal", [HL, WPR],
      _u("acquired patents", "{acquired_s}", "none", "% of the group"),
      "What the domain gate removed, and which class those records had been given.",
      "The removed records are shown rather than summarised: the gate is a reading, and a reader "
      "who disagrees with it can see exactly what it cost.")

_item("a2_d1_similars", [HL, WPR],
      _u("aircraft observations", "", "none", "counts"),
      "The tags that put a record outside the domain, one row each.",
      "Kept as its own table because these tags are the single place a reviewer can push on the "
      "boundary of the corpus.")

_item("a2_d1_filing_status", [PS],
      _u("acquired patents", "{acquired_s}", "none", "counts"),
      "The three patent levels — acquired, representative, primary — and what separates them.",
      "Printed once, early, because almost every count in the document is on one of these three "
      "and mixing them is the easiest mistake to make.")

_item("atlas_duplicates", [HL, PS],
      _u("aircraft observations", "", "none", "counts"),
      "How the repeated filings of one aircraft were merged into a single record.",
      "De-duplication is shown rather than assumed, because every concentration number in Chapter 3 "
      "depends on it: an unmerged corpus would make repetition look like breadth.")

_item("a2_d7_duplicates", [HL, PS],
      _u("aircraft observations", "", "none", "counts"),
      "The duplicate types and how many records each accounts for.",
      "The types are kept apart because only one of them legitimately carries no labels of its own.")

_item("atlas_figure_approval", [HL],
      _u("whole-aircraft figures", "{figures_approved_s}", "none", "% of the corpus"),
      "How many approved whole-aircraft drawings each aircraft rests on.",
      "It bounds every image-side claim: 29 % of the aircraft rest on a single drawing.")

_item("a2_d11_figure_approval", [HL],
      _u("whole-aircraft figures", "{figures_approved_s}", "none", "counts"),
      "Approval and rejection counts for the drawings.",
      "A whole-vehicle set by construction: a drawing of a detail is rejected, which is why the "
      "image set is smaller than the figure count of the patents.")

_item("atlas_fill", [HL],
      _u("label slots", "42", "none", "% that state the field"),
      "How much of the corpus each slot is answered for.",
      "A value hidden by a stage override is left out of the base rather than counted as missing, "
      "so the figure measures what the codebook asked, not what the wizard displayed.")

_item("la_open_questions", [DOC],
      _u("items of this document", "", "none", "counts"),
      "Every question the corpus was asked and could not answer, with the item that tried and the "
      "number that stops it.",
      "One row per question rather than per item, so a weak item is not mistaken for a weak "
      "question; item numbers are resolved at build time and cannot go stale.")

_item("codebook_classes", [CB],
      _u("architecture classes", "12", "none", "counts"),
      "The twelve classes of card G1, drawn.",
      "A reference, not a result — it sits at the end because a reader consults it while reading "
      "the chapters rather than before them.")

_item("codebook_dimensions", [CB],
      _u("label slots", "42", "none", "counts"),
      "The 42 slots of the codebook, drawn.",
      "Same reason as the class drawing: it is the vocabulary the findings are stated in.")

# --------------------------------------------------------------------------
# 4 — the Answer under each question
# --------------------------------------------------------------------------
# Author's ruling 2026-09-23: "the takeaways can be bigger, still direct to the point, but not
# related to the graphs itself either to the questions, answering the fucking question, nothing
# more". So the per-item takeaway line is no longer printed, and each question closes with one
# block that answers it. Numbers in braces resolve from the built tables through
# ``la_index.TAKEAWAY_NUMBERS`` exactly as the takeaway lines did, so nothing here is typed.

ANSWER: Dict[str, str] = {
    "1": "**Yes as a census, no as a leaderboard.** The record is early: a firm's first patent here "
         "comes years before its first flight, so a class is visible in the filings before the "
         "aircraft exists. It is not complete — a priority year cannot be read until its publication "
         "lag has run, which is why every trend in this document stops at 2023 — and it is not "
         "permanent: {tk_lapsed_all} of the {tk_lapsed_n} primary patents with priority 2019 or "
         "earlier are no longer in force, and the classes lapse at the same rate, so what lapse "
         "measures is age and office, not architecture. The same holds for examination: the offices "
         "differ sharply from each other — {tk_ex_us_gr} of the {tk_ex_us_n} US patents are granted "
         "and in force against {tk_ex_cn_gr} of {tk_ex_cn_n} at the Chinese office — while the "
         "classes do not differ from each other at all, which makes examination an administrative "
         "fact and never a technology signal. Where the record can be checked against the world: "
         "the patent class and the class of the firm's publicly known aircraft agree for most "
         "flagship firms, and for {tk_pw_share} of the {tk_pw_n} aircraft that can be matched to a public product. "
         "What the record cannot do is rank architectures commercially. The firms the market rates "
         "highest hold aircraft that differ from everyone else's in citation rank and in survival "
         "and NOT in architecture class — the index is reading patent quality, not configuration. "
         "Read this corpus as an early and honest census of what is being designed; do not read it "
         "as a ranking of what will fly.",

    "2": "**Nothing is converging, and the classes are drifting apart.** On the three conditions "
         "fixed before any curve of this corpus was drawn, none fires: the largest archetype "
         "anywhere reaches {tk_dd_top_share} against a 50 % line, evenness stays inside the "
         "permutation band, and the spread of the space falls below its early level in only "
         "{tk_q_below} of {tk_q_cells} cells. Inside a class it is the same — no class settles on a "
         "single configuration, and the count of distinct configurations per aircraft does not fall. "
         "What does move is the opposite of convergence. Propulsive units rise inside tilt rotor "
         "({tk_dr_tr_units_first} to {tk_dr_tr_units_last}) and inside combined vectored thrust "
         "({tk_dr_cvt_units_first} to {tk_dr_cvt_units_last}) while lift-plus-cruise stays flat from "
         "{tk_dr_slc_units_first}; tilting joints rise inside the classes that transition, and the "
         "pooled line is flat only because lift-plus-cruise has none of them — transition wins inside "
         "a class, cost wins in the mix. Two traces move against the only driver that predicts them: "
         "ducting falls where noise predicts more of it, and distinct propulsor types rise where both "
         "cost drivers predict fewer. Of the couplings the fixed physical drivers predict, one "
         "survives (empennage type against wing count, V {tk_dr_emp_wing_v}); the rest are near zero. "
         "That is the mechanism, not a separate finding: the architecture class is the one choice "
         "that constrains the others, everything below it is close to free, and a design space that "
         "loose does not produce a dominant design.",

    "3": "**Open, and more open than the sector's account of itself.** {tk_firms_all} named firms "
         "file here and {tk_seg_one_firms} of them hold a single aircraft; named companies hold "
         "{tk_fm_named_share} of the analysis set and individual inventors most of the rest. No "
         "class is one company's programme: dropping the firm that moves the reading most "
         "({tk_lev_firm}) shifts no class share by more than {tk_lev_pp} percentage points, and the "
         "largest classes each divide as if between twenty-five equally sized filers. What moves "
         "the mix is arrival, not conversion — the firms entering a window bring a different class "
         "mix than the window itself holds, while a firm that files again usually files in the same "
         "class. The exception names itself: tilt wing keeps only 16 % of its firms across "
         "successions against 48-59 % for the others, so it is the one class the firms themselves "
         "pass through on the way somewhere else. One caution on the unit: named companies hold "
         "{tk_fm_named_share} of the aircraft and {tk_fm_named_pat} of the primary patents, so the "
         "concentration reads the same whichever is counted — but every count in this document is "
         "taken on aircraft, because a firm that re-files one design would otherwise read as breadth.",

    "4": "**Region changes how much is filed and when, not what is designed.** Three countries hold "
         "two thirds of the corpus and the regions do not run on one clock — North America passes "
         "the middle of its own filings in {tk_na_50}, Europe in {tk_eu_50} and Asia-Pacific in "
         "{tk_ap_50}. The designs themselves do not separate. Two firms from the same region are no "
         "more alike in their class profile than two firms from different regions "
         "({tk_prox_same} against {tk_prox_diff} over {tk_prox_pairs} pairs), and Europe is the least "
         "alike internally of the three. What survives is smaller than a regional strategy and is "
         "worth stating as such: North America keeps a higher share of tilting architectures "
         "throughout, China's filings lean to lift-plus-cruise and to wingless designs, and a handful "
         "of archetype-region cells are over-represented enough to name. There are no regional design "
         "blocs in this record, and a reader who expected Europe, China and the United States to be "
         "building different aircraft should take that as the finding.",

    "M": "**The drawing alone carries the architecture for the large winged classes and fails for the "
         "small ones.** Agreement with the whole-patent reading is {tk_gt_tr} for tilt rotor and "
         "{tk_gt_slc} for lift-plus-cruise, against {tk_gt_ptc} for the powered-tail class and "
         "{tk_gt_hb} for hybrids; where the sources disagree the cases are listed by name rather than "
         "counted, so every one of them can be checked. One reliability claim is still owed: every "
         "agreement number in this document is against another source, never between the labeller and "
         "himself, and that is what the relabel of 50 closes.",
}

# --------------------------------------------------------------------------
# 5 — accessors, all optional from the renderer's point of view
# --------------------------------------------------------------------------

_MISSING = "not recorded for this item yet — add it to la_lines.py"


def source_line(name: str) -> str:
    tags = SOURCE.get(name)
    return " · ".join(tags) if tags else ""


def unit_line(name: str) -> str:
    """``unique aircraft (665) · priority window · % of the window`` — three slots, always in
    this order, always from the vocabularies."""
    e = UNIT.get(name)
    if not e:
        return ""
    head = e.get("counts", "")
    if e.get("n"):
        head = f"{head} ({e['n']})"
    parts = [head]
    if e.get("time") and e["time"] != "none":
        parts.append(e["time"])
    else:
        parts.append("no time axis")
    parts.append(e.get("norm") or "counts")
    return " · ".join(p for p in parts if p)


def read_line(name: str) -> str:
    return READ.get(name, "")


def why_line(name: str) -> str:
    return WHY.get(name, "")


def answer(question: str) -> str:
    return ANSWER.get(question, "")


def unregistered(names) -> List[str]:
    """The items of the document that have no entry here — printed by the render script so a
    new figure cannot reach the page with three of its four lines missing."""
    return [n for n in names if n not in SOURCE and n not in CUT]
