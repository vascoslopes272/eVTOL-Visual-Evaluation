"""The structure of the Labelling Analysis, held as data — tables and figures only.

Same node shape as :mod:`index` (the Preliminary Analysis) so :func:`report.write_markdown`
can render either. User ruling 2026-09-22: no explaining prose, just the tables and figures,
each with its Source and How-to-read line. Sections follow the user's outline: 1 data sets
construction, 2 taxonomy, 3 data quality and facts, 4 preliminary analysis (convergence,
provenance, assignees). Change wording here and the document follows.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import index as _pa

TITLE = "Labelling Analysis — the labelled eVTOL patent data set in tables and figures"

TABLE_CAPTIONS: Dict[str, str] = {
    **_pa.TABLE_CAPTIONS,
    "a2_d7_duplicates": (
        "From aircraft observations to unique aircraft: originals, observations (O1, O2) and similars (S3). "
        "The three middle columns count the representative set, after the domain gate; the last column counts "
        "the same types one step earlier — every aircraft observation on all the patents approved at labelling, "
        "before the “but similar” gate removed any"),
    "a2_d13_flagship_check": (
        "Flagship check: the classes the largest filers patent, beside the aircraft they have made public. "
        "The last two columns read the public side alone — whether the company's own public aircraft sit in "
        "more than one class, and whether the class it files most is the class of one of them"),
    "la_name_arch_check": (
        "Aircraft where the sources disagree on the architecture: the G1 label of the figures, the whole-patent "
        "reading, and the evtol.news directory. The first row counts the aircraft where every available source "
        "agrees; under it are the three no comparison can reach, each with the reason; then the disagreements. "
        "Nothing was relabelled to make a comparison possible — a whole-patent value outside the twelve classes "
        "prints as it stands. The directory works in five classes, so the G1 and whole-patent codes carry their "
        "fold where a public class exists"),
    "la_relabel_protocol": "Intra-rater relabel of 50 patents: protocol and status",
    "la_firm_weighted_shares": "Class share per window, by aircraft and one vote per filer",
    "la_lead_lag_region": "Year each region reached a quarter, half and three quarters of its aircraft (complete years, to 2023)",
    "la_lead_lag_class": "Year each of the seven largest classes reached a quarter, half and three quarters of its aircraft",
    "la_class_cycles": "Each class over the windows as a share of its own total, and its median window",
    "la_hill_by_window": "Rarefied Hill numbers per window (40 aircraft, 1 000 draws): richness ⁰D, ¹D and ²D with 95 % bands",
    "la_zones": "A0c archetypes with five or more aircraft: size, distinct filers, span of windows and zone",
    "la_abandonment_by_class": "Primary patents no longer in force per class, priority year 2019 or earlier",
    "la_country_class": "Class share per applicant country, eight largest countries",
    "la_firm_tiers": "Firm tiers: how many firms and aircraft each threshold keeps",
    "la_filers_by_window": "Named firms per window: active, new, continuing, last seen, and the individuals' share",
    "la_proximity_region": "Mean technological proximity of firm pairs in the same and in different regions",
    "la_ari_firms": "AAM Reality Index firms that file in the corpus: score, funding, patented aircraft and class mix",
    "la_ari_correlation": "Spearman correlation between the index side and the patent side, over the listed firms",
    "la_trl_placeholder": "TRL-ranked firms: planned figures, pending the TRL work",
    "la_class_fold": "The twelve G1 classes folded to the five evtol.news directory classes",
    "la_mission_capacity": "Capacity stated on the evtol.news page, by folded class (linked aircraft, counts)",
    "la_mission_piloting": "Piloting stated on the page, by folded class",
    "la_mission_power source": "Power source stated on the page, by folded class",
    "la_mission_status": "Development status of the page, by folded class",
    "la_mission_agreement": "Folded patent class against the directory's own class of the same aircraft",
    "la_filings_per_year": "Representative unique aircraft and acquired patents per priority year, and the same counts against all aeronautics (B64) patents of the same priority years and publication offices; a year is incomplete while the snapshot is within the 90th-percentile publication lag of it",
    "la_flags": "Items flagged as candidates to leave out of the high-level document — the author decides; so far only the two 4.1.2 robustness figures and Table 4.1.2 have been removed (2026-09-22)",
    "la_archetype_levels": "Every archetype level the codebook can form: the dimensions it combines, its largest archetype, how many archetypes it yields, how many aircraft end up alone in one, the effective number of archetypes (Hill ¹D) and where this document reads the level. The counting columns reproduce table 3.3.6 of the Preliminary Analysis",
    "la_archetype_choice": "Which of those levels can carry a design species: four screens applied to the numbers of the previous table, each cell printing the level's value and whether it clears the line. A level that clears all four can still be set aside on a codebook ruling, and the reason is printed",
    "la_dd_conditions": "The three conditions of the dominant-design test as they were fixed in the Preliminary Analysis (5.7), before any curve of this corpus was drawn: what each one tests, the threshold, and where the threshold comes from. No number of this corpus enters this table",
    "la_dd_result": "What the corpus answers, one generated sentence per condition. Every figure in the sentences is read out of the per-window table that follows; none of them is typed",
    "la_dominant_design": "The dominant-design test per window: top archetype share (condition 1) and rarefied ²D against the permutation band (condition 2)",
    "la_class_configs": "Within-class convergence per class and window: the configuration most of the class's unique "
                        "aircraft share, how many of them hold it, and how many distinct configurations the class holds. "
                        "A configuration is one aircraft's combination of four label fields — propulsive units banded "
                        "(1-3 / 4 / 5-6 / 7-8 / 9+), ducted or open, booms or no booms, and tail type",
    "la_dimension_drift": "Dimension drift per class and window: median propulsive units, and the share of the class's "
                          "own unique aircraft in that window with a ducted unit, with a tilting unit and with booms "
                          "(the denominator is the `aircraft` column, never a count of rotors)",
    "la_transitions": "Within-firm successions: class of the earlier aircraft against the class of the next one",
    "la_ip_strategy": "IP strategy per firm (5+ aircraft): patents per aircraft, family size, claims, citations",
    "la_ip_by_class": "Claims, citations and family size per class, primary patents",
    "la_cohorts": "Entry cohorts: firms by first-filing window and the class they entered with",
    "la_ari_timeline": "Patent clock against market clock for the index firms: first, peak and last patent, first flight, entry into service, regulator",
    "la_specialisation": "Regional specialisation index per archetype (A0c, 5+ aircraft)",
    "la_industry_by_class": "Industry named in the patent text, by class (counts)",
    "la_examination_office": "Legal status of the primary patents by publication office",
    "la_examination_class": "Legal status of the primary patents by class",
    "la_powertrain_by_class": "Powertrain stated in the patent, by class (counts)",
}

FIGURE_CAPTIONS: Dict[str, str] = {
    **_pa.FIGURE_CAPTIONS,
    "design_space_cards": "the four label cards of one unique aircraft",
    "atlas_removal": "what refinement 1 removed, and the gated aircraft by type",
    "atlas_duplicates": "observations to unique aircraft: O1, O2 and S3",
    "atlas_figure_approval": "figure approval and the evidence behind each aircraft",
    "atlas_years": "unique aircraft per priority year, by applicant region",
    "atlas_region": "provenance of the aircraft: country and region",
    "atlas_filers": "who files the aircraft",
    "atlas_state_by_arch": "flight state of the approved figures by architecture",
    "atlas_arch_gt": "where the label read from the figures alone and the whole-patent reading agree, and what they confuse",
    "atlas_arch_time": "architecture mix per priority window, counted in unique aircraft (not patents)",
    "atlas_powertrain": "powertrain stated in the patent",
    "atlas_fields": "label depth: slots answered per aircraft, by architecture class",
    "atlas_fill": "fill rate of each field where its part exists",
    "atlas_flagship": "flagship check: labels of the largest filers against their public products",
    "atlas_units": "propulsor units and their arrangement",
    "atlas_design_heatmaps": "the design space as heatmaps of paired fields",
    # parked 2026-09-22: built on request only, not placed in NODES — the caption is kept so putting the
    # name back in a node is the only edit needed to bring the figure back.
    "firm_weighted": "class share per window, every aircraft against one vote per filer",
    "spans_by_firm": "re-filing of the same aircraft, by firm",
    "two_counts": "class share per window, aircraft counted once or in every window it was filed in",  # parked, see above
    "lead_lag": "cumulative share of the aircraft by priority year: who is early, who is late",
    "class_cycles": "where in time each class lives: its aircraft per window as a share of its own total",
    "hill": "diversity per window, rarefied to 40 aircraft",
    "zones": "archetypes with five or more aircraft: crowded against open, and activity per window",
    "abandonment": "primary patents no longer in force, per class",
    "region_grid": "three variables per region and window",
    "region_grid_b": "three more variables per region and window",
    "country_class": "class share per applicant country",
    "coverage": "share of the analysis set the top N firms cover, AAM Reality Index firms marked",
    "filers_over_time": "the body of filers over time",
    "firm_tiles": "firms with five or more aircraft per window: aircraft and the class filed most",
    "proximity_region": "technological proximity between firms, with each firm's region",
    "ari": "AAM Reality Index firms that file in the corpus: score, history, funding and class mix",
    "mission": "mission of the linked aircraft by folded class, and the agreement with the directory's class",
    "ari_history": "the index over time, and against the corpus",
    "ari_clock": "the patent clock against the market clock for the index firms",
    "filings_per_year": "unique aircraft per priority year by applicant region, acquired patents as a line, and the same filings indexed against all aeronautics (B64) patenting of the same offices; hatched years are still incomplete at the snapshot (90th-percentile publication lag)",
    "dominant_design": "the dominant-design test per window: top archetype share against the 50 % line, and ²D against the permutation band",
    "class_configs": "within-class convergence: how far each architecture class settles on a single configuration. "
                     "A line is a class, not an archetype, and the unit is the unique aircraft; a configuration is one "
                     "aircraft's combination of propulsive units (banded), ducted or open, booms or no booms, and tail "
                     "type. Every class with at least 5 aircraft in at least 3 of the 5 windows is drawn — the Source "
                     "line under the figure gives the classes and the share of the corpus they cover",
    "dimension_drift": "dimension drift inside each architecture class, per window: the four label dimensions that make "
                       "up the configuration of Figure 4.1.4, read one at a time. A line is a class, not an archetype; "
                       "every percentage is a share of that class's own unique aircraft in that window, not of rotors",
    "transitions": "within-firm successions: what class a firm's next aircraft takes",
    "ip_strategy": "IP strategy: depth, breadth, claims and citations",
    "specialisation": "regional specialisation index per archetype",
    "industry_by_class": "industry named in the patent text, by class",
    "examination": "legal status of the primary patents",
}

#: The graphs inside one figure, in the order they are drawn: ``(name, axes it spans)``.
#: A figure that is one graph is absent here or has a single entry; everything else gets a
#: numeral — (i), (ii), … — printed on the panel and repeated in the caption, so a single
#: graph can be named and commented on. ``axes it spans`` is more than 1 when one graph is
#: drawn as a row of small multiples (Figures 4.3.2a/b) or split over two strips.
#: Small multiples of one variable (one panel per class) stay a single graph: the panel
#: titles already name them.
FIGURE_PANELS: Dict[str, List] = {
    # --- 1 data sets
    "atlas_removal": [("why patents left the analysis", 1), ("aircraft removed by the domain gate, by class", 1)],
    "atlas_duplicates": [("repeated observations per patent", 1), ("aircraft per primary patent", 1)],
    "atlas_figure_approval": [("approved figures per aircraft", 1), ("aircraft resting on a single figure, by class", 1)],
    # --- 3 data quality
    # atlas_fields and atlas_arch_gt are one graph each here (la_figures.ATLAS_DROP cuts the left
    # panel of both, user ruling 2026-09-22), so they carry no panel marks and are not listed.
    # --- 4.1 what is designed
    # 4.1.1 gains (ii) only when the stored aviation baseline is installed; without it the figure
    # holds one graph and the marks are skipped (see la_baseline, user ruling 2026-09-22).
    "filings_per_year": [("filings per priority year, by applicant region", 1),
                         ("the same filings against all aeronautics (B64) patenting, both indexed", 1)],
    "atlas_arch_time": [("architecture share per window", 1), ("the five largest classes over time", 1)],
    "dominant_design": [("condition 1: top archetype share", 1), ("condition 2: ²D at A0c against the band", 1),
                        ("condition 2: ²D at A1t against the band", 1)],
    "class_configs": [("share of the class in its single most common configuration", 1),
                      ("distinct configurations per aircraft", 1)],
    "dimension_drift": [("median propulsive units per aircraft", 1), ("% of aircraft with a ducted unit", 1),
                        ("% of aircraft with a tilting unit", 1), ("% of aircraft with booms", 1)],
    "hill": [("A0, class", 1), ("A0c, class × propulsor bin", 1)],
    "lead_lag": [("by applicant region", 1), ("by class, seven largest", 1)],
    "zones": [("crowded against open", 1), ("aircraft per window for each archetype", 1)],
    # --- 4.2 who designs it
    "filers_over_time": [("filers per window: entries, returners, exits", 1), ("entry cohorts by class", 1)],
    "atlas_filers": [("top companies by unique aircraft", 1), ("architecture mix by filer type", 1),
                     ("concentration of filing (Lorenz)", 1)],
    "ip_strategy": [("depth against breadth, per firm", 1), ("claims and citations per class", 1)],
    "spans_by_firm": [("aircraft filed again over several years", 1), ("share of a firm's aircraft filed more than once", 1)],
    "ari_history": [("score per release", 1), ("funding against patented aircraft", 1)],
    # --- 4.3 where
    "region_grid": [("class", 3), ("propulsor units", 3), ("tilting unit", 3)],
    "region_grid_b": [("ducted unit", 3), ("powertrain", 3), ("filer type", 3)],
    # --- 5 low level
    "atlas_powertrain": [("by architecture", 1), ("by priority window", 1)],
    "atlas_units": [("propulsor units per class", 1), ("arrangement features per class", 1)],
    "atlas_design_heatmaps": [("wings", 1), ("fuselage motion", 1), ("booms", 1), ("any propulsor tilts", 1),
                              ("tail type", 1), ("landing gear", 1)],
    "atlas_region": [("applicant country", 1), ("architecture mix by region", 1)],
    "mission": [("capacity", 1), ("piloting", 1), ("power source", 1), ("status", 1),
                ("patent class against the directory's class", 1)],
    "examination": [("by publication office", 1), ("by class", 1)],
    # --- one graph drawn over several axes: no numerals
    "specialisation": [("regional specialisation by archetype", 2)],
    "class_cycles": [("one panel per class", 12)],
    "two_counts": [("one panel per class", 4)],   # parked 2026-09-22, not placed in NODES
}

#: numerals for the graphs inside a figure
PANEL_NUMERALS = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii",
                  "xiii", "xiv", "xv", "xvi"]


def panel_mark(k: int) -> str:
    """The mark printed on the k-th graph of a figure, e.g. ``(ii)``."""
    return f"({PANEL_NUMERALS[k]})"


FIG_WIDTH: Dict[str, str] = {
    **_pa.FIG_WIDTH,
    "design_space_cards": "92%", "region_grid": "100%", "mission": "100%",
    **{k: "100%" for k in FIGURE_CAPTIONS if k.startswith("atlas_")},
    "firm_weighted": "96%", "fig_02_refinement_funnel": "74%", "ari_history": "100%", "ari_clock": "100%",
    "specialisation": "100%", "transitions": "70%", "spans_by_firm": "100%", "two_counts": "100%", "lead_lag": "100%",
    "class_cycles": "100%", "hill": "100%", "zones": "100%", "abandonment": "92%",
    "country_class": "92%", "coverage": "96%", "filers_over_time": "96%", "firm_tiles": "96%",
    "proximity_region": "96%", "ari": "100%", "dominant_design": "100%", "class_configs": "100%",
    "dimension_drift": "100%", "ip_strategy": "100%",
    "industry_by_class": "96%", "examination": "100%", "filers_over_time": "100%", "filings_per_year": "100%",
}

#: figures printed on their own A4-landscape page
LANDSCAPE = {"codebook_classes", "codebook_dimensions"}

ROW_CAP: Dict[str, int] = {
    **_pa.ROW_CAP,
    "la_zones": 20, "la_ari_firms": 20, "la_firm_weighted_shares": 25, "la_country_class": 8,
    "la_hill_by_window": 10, "la_class_cycles": 12, "la_abandonment_by_class": 13, "la_class_fold": 12,
    "la_name_arch_check": 24,   # 1 summary + the 3 aircraft no comparison reaches + 20 disagreements
    "la_flags": 20, "la_class_configs": 25, "la_dimension_drift": 25, "la_ip_strategy": 20, "la_ari_timeline": 20,
    "la_specialisation": 20, "la_dominant_design": 10, "la_transitions": 12,
    "la_archetype_levels": 12, "la_archetype_choice": 12, "la_dd_conditions": 4, "la_dd_result": 4,
}
COLUMNS: Dict[str, List[str]] = {
    **_pa.COLUMNS,
    "la_zones": ["archetype", "aircraft", "filers", "named firms", "filers per aircraft", "share 2016-23",
                 "first window", "last window", "zone"],
    "la_ari_firms": ["company", "ARI score", "release", "funding $M", "ARI vehicle type", "unique aircraft",
                     "classes", "class mix", "first priority year"],
    "la_hill_by_window": ["level", "window", "aircraft", "D0", "D0 low", "D0 high", "D1", "D1 low", "D1 high",
                          "D2", "D2 low", "D2 high"],
    "la_filers_by_window": ["window", "unique aircraft", "named firms active", "new firms", "continuing firms",
                            "firms last seen", "aircraft by named firms", "share individual inventors",
                            "share unattributed"],
    "la_archetype_levels": ["level", "dimensions combined", "largest archetype", "archetypes", "singletons",
                            "effective number ¹D", "largest share", "used in this document"],
    "la_archetype_choice": ["level", "resolution", "fragmentation", "population", "readable shares", "verdict"],
    "la_dd_result": ["condition", "observed result", "met"],
    "la_dominant_design": ["level", "window", "aircraft", "top archetype", "top share", "D2", "D2 permutation low",
                           "D2 permutation high", "below band"],
    "la_class_configs": ["class", "window", "aircraft", "most common configuration", "share in it",
                         "distinct configurations"],
    "la_dimension_drift": ["class", "window", "aircraft", "median propulsive units", "share with a ducted unit",
                           "share with a tilting unit", "share with booms", "median wings"],
    "la_ip_strategy": ["firm", "unique aircraft", "patents", "patents per aircraft", "median family size", "median claims",
                       "mean forward citations", "in-corpus forward citations", "region"],
    "la_ari_timeline": ["company", "ARI score", "first patent", "peak filing year", "last patent", "unique aircraft",
                        "first flight (ARI)", "entry into service (ARI)", "regulator (ARI)"],
}

NODES: List[Dict] = [
    dict(id="flags", title="Items flagged for the author's decision", tables=["la_flags"]),
    # ================================================================ 1
    dict(id="1", title="Data Sets Construction",
         figures=["fig_02_refinement_funnel", "atlas_removal"]),
    dict(id="1.1", title="Refinement 1 — representativity", level="patent",
         tables=["a2_d1_similars", "a2_d9_publication_lag_region", "a2_d1_filing_status"]),
    dict(id="1.2", title="Refinement 2 — observations to unique aircraft", level="unique aircraft",
         figures=["atlas_duplicates"], tables=["a2_d7_duplicates", "a2_d7_aircraft_per_patent"]),
    dict(id="1.3", title="Refinement 3 — figure approval", level="unique aircraft → image",
         figures=["atlas_figure_approval"], tables=["a2_d11_figure_approval"]),
    # ================================================================ 2
    dict(id="2", title="Taxonomy",
         figures=["design_space_cards", "codebook_classes", "codebook_dimensions"]),
    # ================================================================ 3
    dict(id="3", title="Data Quality and Facts", level="unique aircraft, G1 to M3"),
    dict(id="3.1", title="Missingness", figures=["atlas_fill"], tables=["a2_d4_missingness"]),
    dict(id="3.2", title="Intra-rater relabel of 50 patents", tables=["la_relabel_protocol"]),
    dict(id="3.3", title="Flagship check", figures=["atlas_flagship"],
         tables=["a2_d13_flagship_check", "la_name_arch_check"]),
    dict(id="3.4", title="Most common answers", tables=["a2_d3_selected_fields"]),
    dict(id="3.5", title="Field inventory", figures=["atlas_fields"], tables=["a2_d2_informative_fields"]),
    dict(id="3.6", title="Image label against the whole-patent reading", figures=["atlas_arch_gt"]),
    # ================================================================ 4
    dict(id="4", title="Preliminary Analysis", level="unique aircraft"),
    dict(id="4.1", title="What is being designed, and whether it converges", level="unique aircraft"),
    dict(id="4.1.1", title="Filings per year", figures=["filings_per_year"], tables=["la_filings_per_year"]),
    # user ruling 2026-09-22: one figure only. The one-vote-per-filer panel (``firm_weighted``) said the
    # same as the left graph, the two-count check (``two_counts``) and the table added nothing. Their code
    # is kept: put a name back in ``figures``/``tables`` here and re-arm it in ``la_figures.render_all``.
    dict(id="4.1.2", title="Class shares per window", figures=["atlas_arch_time"]),
    # 4.1.3 reads in three steps (user, 2026-09-22): what is evaluated and why, then the
    # conditions each stated in full, then the result. The archetype tables come before the test.
    dict(id="4.1.3", title="The dominant-design test", level="unique aircraft"),
    dict(id="4.1.3.1", title="What is evaluated: the archetype levels",
         tables=["la_archetype_levels", "la_archetype_choice"],
         after=("*How to read the two tables.* An archetype is a combination of label answers. At a "
                "given level an aircraft is written as its answers on that level's dimensions, joined "
                "by ·, and two aircraft share an archetype when that string is the same; every "
                "aircraft belongs to exactly one archetype per level, and every level refines the "
                "architecture class of card G1. A blank is a design absence and stays an answer of its "
                "own, printed as \"blank\"; an aircraft whose answer is hidden by a stage override is "
                "not given a blank but left out of that level, and counted under \"left out\" in the "
                "full table. The effective number ¹D is the exponential of the Shannon entropy of the "
                "archetype shares: the number of equally common archetypes that would give the same "
                "entropy. It is at most the number of archetypes and equal to it only when every "
                "archetype is the same size, so the gap between the two columns is how uneven the "
                "level is. The four screens of the second table are fixed in code, in "
                "`la_tables.ARCHETYPE_SCREENS`.\n\n"
                "**Note for the author — the design species is still open (2026-09-22).** Two levels "
                "clear the four screens, A0c and A1t, and the test below is run at both so that the "
                "verdict does not rest on the choice. The recommendation is A1t. The criterion of "
                "Preliminary Analysis 5.7 is written at A1t and table 5.1 already fixes A1t as the "
                "design species; its three dimensions are direct codebook answers with no binning "
                "choice for a reader to attack; it concentrates the corpus enough for a share to mean "
                "something, and its largest archetype is the same one in the three most recent "
                "windows, with a rising share. A0c spreads the aircraft more evenly and leaves almost "
                "nobody alone, but its largest archetype changes with the propulsor bin rather than "
                "with the shape of the aircraft, and its bin edges are a judgement. The recommendation "
                "is therefore to keep A1t as the design species and to carry A0c as the robustness "
                "level — which is what 4.1.3.3 does, and the level 4.1.8, 4.1.9 and 4.3.3 already "
                "read. Nothing has been switched; the ruling is the author's.")),
    dict(id="4.1.3.2", title="The conditions, fixed in advance", tables=["la_dd_conditions"]),
    dict(id="4.1.3.3", title="The result", figures=["dominant_design"],
         tables=["la_dd_result", "la_dominant_design"]),
    dict(id="4.1.4", title="Within-class convergence", figures=["class_configs"], tables=["la_class_configs"]),
    dict(id="4.1.5", title="Dimension drift inside the classes", figures=["dimension_drift"], tables=["la_dimension_drift"]),
    dict(id="4.1.6", title="Where each class lives in time", figures=["class_cycles"], tables=["la_class_cycles"]),
    dict(id="4.1.7", title="Lead and lag by region and by class", figures=["lead_lag"],
         tables=["la_lead_lag_region", "la_lead_lag_class"]),
    dict(id="4.1.8", title="Diversity per window", figures=["hill"], tables=["la_hill_by_window"]),
    dict(id="4.1.9", title="Crowded and open zones of the design space", figures=["zones"], tables=["la_zones"]),
    dict(id="4.1.10", title="Abandonment: patents no longer in force", figures=["abandonment"],
         tables=["la_abandonment_by_class"]),
    dict(id="4.2", title="Who designs it, and how they compete", level="firm"),
    dict(id="4.2.1", title="Coverage: which firms count as the top", figures=["coverage"], tables=["la_firm_tiers"]),
    dict(id="4.2.2", title="The body of filers over time, and entry cohorts", figures=["filers_over_time"],
         tables=["la_filers_by_window", "la_cohorts"]),
    dict(id="4.2.3", title="Who filed, and firm portfolios per window", figures=["atlas_filers", "firm_tiles"],
         tables=["a2_d8_filer_mix", "a2_d8_concentration"]),
    dict(id="4.2.4", title="Within-firm successions", figures=["transitions"]),
    dict(id="4.2.5", title="IP strategy: depth, breadth, claims and citations", figures=["ip_strategy", "spans_by_firm"],
         tables=["la_ip_strategy", "la_ip_by_class"]),
    dict(id="4.2.6", title="Technological proximity between firms, and region", figures=["proximity_region"],
         tables=["a2_d14_firm_proximity", "la_proximity_region"]),
    dict(id="4.2.7", title="The AAM Reality Index firms: score, funding, and the patent clock against the market clock",
         figures=["ari", "ari_history", "ari_clock"], tables=["la_ari_firms", "la_ari_correlation", "la_ari_timeline"]),
    dict(id="4.2.8", title="TRL-ranked firms", tables=["la_trl_placeholder"]),
    dict(id="4.3", title="Where", level="patent → unique aircraft"),
    dict(id="4.3.1", title="Region, country and publication office", figures=["atlas_region"]),
    dict(id="4.3.2", title="Region over time, six variables", figures=["region_grid", "region_grid_b"]),
    dict(id="4.3.3", title="Regional specialisation by archetype", figures=["specialisation"], tables=["la_specialisation"]),
    dict(id="4.3.4", title="Country and class", figures=["country_class"], tables=["la_country_class"]),
    # ================================================================ 5
    dict(id="5", title="Low-level Analysis", level="unique aircraft and image"),
    dict(id="5.1", title="Hybrid against electric, not-stated included", figures=["atlas_powertrain"],
         tables=["la_powertrain_by_class"]),
    dict(id="5.2", title="Propulsor units and their arrangement", figures=["atlas_units"]),
    dict(id="5.3", title="The design space as paired fields", figures=["atlas_design_heatmaps"]),
    dict(id="5.4", title="Image-level answers", figures=["atlas_state_by_arch"], tables=["a2_d2_figure_slot_answers"]),
    dict(id="5.5", title="Mission of the aircraft linked to evtol.news, and the industry named in the text",
         figures=["mission", "industry_by_class"],
         tables=["la_class_fold", "la_mission_capacity", "la_mission_piloting", "la_mission_power source",
                 "la_mission_status", "la_mission_agreement", "la_industry_by_class"]),
    dict(id="5.6", title="Examination outcome as a regulatory signal", figures=["examination"],
         tables=["la_examination_office", "la_examination_class"]),
]


# --------------------------------------------------------------------------
# accessors (same API as index.py, bound to this module's NODES)
# --------------------------------------------------------------------------
def node(node_id: str) -> Dict:
    for n in NODES:
        if n["id"] == node_id:
            return n
    raise KeyError(node_id)


def depth(node_id: str) -> int:
    return node_id.count(".")


def heading(node_id: str, values: Optional[Dict] = None) -> str:
    n = node(node_id)
    title = _pa._fill(n["title"], values)
    d = depth(node_id)
    if not node_id[0].isdigit():
        return f"## {title}"
    if d == 0:
        return f"## Chapter {node_id} — {title}"
    return f"{'#' * (2 + d)} {node_id} {title}"


def level_line(node_id: str) -> str:
    n = node(node_id)
    return f"*Level of analysis: {n['level']}.*" if n.get("level") else ""


def text(node_id: str, values: Optional[Dict] = None) -> str:
    return _pa._fill(node(node_id).get("text", ""), values)


def after(node_id: str, values: Optional[Dict] = None) -> str:
    return _pa._fill(node(node_id).get("after", ""), values)


LETTERS = "abcdefghijklmnop"


def figure_number(node_id: str, k: int, total: int) -> str:
    base = f"{node_id}.1" if depth(node_id) == 0 else node_id
    return base + ("" if total == 1 else LETTERS[k])


def table_number(node_id: str, k: int, total: int) -> str:
    return node_id + ("" if total == 1 else LETTERS[k])


# --------------------------------------------------------------------------
# provenance — the grey line under every figure and every table
# --------------------------------------------------------------------------
# User ruling 2026-09-22: "I need to know how the data was transferred to the image or
# graph or whatever ... and I need to know what you are analysing: if it's patenting, if
# it is unique aircraft, if it is whatever." So every item prints one line in a fixed
# order:
#
#     Unit: <what one row / dot / bar is, and how many there are>
#     Base: <the denominator a share is taken on>
#     Transform: <raw counts / share of a row / rarefied / median / blanked below n ...>
#
# Keyed by the internal figure or table name, never by the printed number, so the line
# survives a section being renumbered, moved or split. Counts are written as ``{key}``
# placeholders resolved against ``numbers.live`` at render time (``{unique_s}`` = 665,
# ``{acquired_s}`` = 1 639, ...) so no number here can go stale; ``{n_*}`` placeholders
# are resolved from the built tables through :data:`N_FROM_TABLE`. A count that cannot be
# resolved is dropped rather than printed as a placeholder.
import re as _re  # noqa: E402

#: what an item under a section says when it has no entry of its own: the unit comes from
#: the section's ``level``, the rest says plainly that it is not recorded. A figure or a
#: table added later therefore still prints a true unit line, and the missing half is
#: visible to the author instead of being guessed.
LEVEL_UNIT: Dict[str, str] = {
    "patent": "patents — the column or axis says which of the three levels "
              "(acquired {acquired_s}, representative {representative_s}, primary {primary_s})",
    "unique aircraft": "unique aircraft (n {unique_s})",
    "unique aircraft → image": "unique aircraft (n {unique_s}) and the whole-aircraft figures "
                               "behind them (n {figures_approved_s})",
    "unique aircraft, G1 to M3": "unique aircraft (n {unique_s})",
    "firm": "named firms, and the unique aircraft they hold (analysis set n {unique_s})",
    "patent → unique aircraft": "unique aircraft (n {unique_s}), grouped by the applicant of the patent",
    "unique aircraft and image": "unique aircraft (n {unique_s}) and whole-aircraft figures "
                                 "(n {figures_approved_s})",
}

#: honest filler, never a guess: it names the item as unfinished so the author can see it
MISSING = "not recorded for this item yet — add it to PROVENANCE in la_index.py"

#: ``{n_key}`` -> the built table whose row count answers it. Resolved at render time, so a
#: table that grows or shrinks moves the number with it. A name that is not built is dropped.
N_FROM_TABLE: Dict[str, str] = {
    "n_flagship_firms": "a2_d13_flagship_check",
    "n_firms5": "la_ip_strategy",
    "n_prox_firms": "a2_d14_firm_proximity",
    "n_ari": "la_ari_firms",
    "n_zones": "la_zones",
    "n_special": "la_specialisation",
    "n_informative": "a2_d2_informative_fields",
}

#: The unit / base / transform of each figure and table, hand-checked against its builder
#: in ``la_tables.py``, ``a2.py``, ``la_figures.py`` or ``atlas.py`` — never inferred from
#: the title. An item that mixes units says so in ``unit``.
#:
#: ONE ENTRY PER KEY. A repeated key is not an error in Python: the last one silently wins
#: and the first is lost. Search for the name before adding an entry, and edit the entry
#: that is there rather than appending a second.
PROVENANCE: Dict[str, Dict[str, str]] = {
    # ---------------------------------------------------------------- front matter
    "la_flags": dict(
        unit="items of this document (figures, tables and whole sections)",
        base="not a measurement — a hand-written list for the author",
        transform="none; nothing has been computed and nothing has been removed"),

    # ================================================================ 1 data sets
    "fig_02_refinement_funnel": dict(
        unit="every level of the funnel in turn — acquired patents (n {acquired_s}), representative "
             "patents (n {representative_s}), primary patents (n {primary_s}), aircraft observations "
             "(n {observations_s}), unique aircraft (n {unique_s}), whole-aircraft figures "
             "(n {figures_approved_s})",
        base="each stage is counted on the stage above it",
        transform="raw counts only; every number on the figure is the line above minus what left, "
                  "so the arithmetic closes on the figure itself"),
    "atlas_removal": dict(
        unit="(i) acquired patents (n {acquired_s}); (ii) the unique-aircraft records the domain gate "
             "removed (n {gated_aircraft_s})",
        base="(i) all the acquired patents; (ii) the removed aircraft, split by the class they had "
             "been labelled with",
        transform="raw counts; the one percentage on a bar in (ii) is the share of that bar carrying "
                  "the UAV-similar tag, so the complement is the other tag"),
    "a2_d1_similars": dict(
        unit="two units in the same table — aircraft observations and patents, in their own columns",
        base="the wizard-approved set before the domain gate, so the removals are visible",
        transform="raw counts; an aircraft can carry two Similar tags, so the rows do not add up to "
                  "the gate total"),
    "a2_d9_publication_lag_region": dict(
        unit="primary patents (n {primary_s}) that carry both a priority and a publication year",
        base="the patents of each applicant region, one row each",
        transform="median and 90th percentile of the priority-to-publication lag in years — order "
                  "statistics, not a share; this is what decides which priority years are complete"),
    "a2_d1_filing_status": dict(
        unit="patents read at all three levels side by side — acquired (n {acquired_s}), "
             "representative (n {representative_s}) and primary (n {primary_s})",
        base="each column is its own total; a row is the same office status read at the three levels",
        transform="raw counts; the three columns are nested subsets, never three independent samples, "
                  "so they must not be compared as if they were"),
    "atlas_duplicates": dict(
        unit="(i) aircraft observations of the representative patents (n {observations_s}); "
             "(ii) primary patents (n {primary_s})",
        base="(i) all the observations; (ii) all the primary patents",
        transform="raw counts; (ii) is drawn on a log scale, so a bar twice as tall is ten times as many"),
    "a2_d7_duplicates": dict(
        unit="aircraft observations of the representative patents (n {observations_s}), resolved to "
             "unique aircraft (n {unique_s})",
        base="every observation of the representative set, by duplicate type",
        transform="raw counts; observations − O1 − O2 = unique aircraft, and the table closes on that"),
    "a2_d7_aircraft_per_patent": dict(
        unit="primary patents (n {primary_s})",
        base="all the primary patents, grouped by how many unique aircraft each one draws",
        transform="raw counts"),
    "atlas_figure_approval": dict(
        unit="unique aircraft (n {unique_s}) and the whole-aircraft figures behind them "
             "(n {figures_approved_s})",
        base="(i) all the aircraft; (ii) each class's own aircraft, n printed under the class code",
        transform="(i) raw counts of aircraft by number of approved figures; (ii) share of the class "
                  "resting on a single figure, with the overall share as a dashed line"),
    "a2_d11_figure_approval": dict(
        unit="figures on file of the representative patents (n {figures_total_s})",
        base="every figure of a representative patent; the indented rows split the approved ones by "
             "what the figure shows",
        transform="raw counts; the rows add up to the figures on file"),

    # ================================================================ 2 taxonomy
    "design_space_cards": dict(
        unit="the codebook itself — the four label cards one unique aircraft fills",
        base="the dimension register (assets/codebook/dimension_register.csv), not the labelled corpus",
        transform="none; the numbers are the size of the questionnaire ({questions} slots), never a "
                  "count of aircraft"),
    "codebook_classes": dict(
        unit="the codebook itself — the twelve architecture classes of card G1",
        base="the class definitions, drawn by the author",
        transform="none; no corpus data enters this drawing"),
    "codebook_dimensions": dict(
        unit="the codebook itself — every dimension of the label cards G1 to M3",
        base="the dimension register, drawn by the author",
        transform="none; no corpus data enters this drawing"),

    # ================================================================ 3 data quality
    "atlas_fill": dict(
        unit="unique aircraft (n {unique_s})",
        base="per field, only the aircraft whose parent field says the part exists; a value an "
             "override hides is left out of the base, never counted as a blank",
        transform="fill rate — the share of that base which carries a value"),
    "a2_d4_missingness": dict(
        unit="unique aircraft (n {unique_s})",
        base="the column `of`: the aircraft whose parent field says the part exists and that no "
             "override hides — not all {unique_s}",
        transform="share = blanks ÷ `of`; the aircraft an override hides are counted apart in "
                  "`left out (override)` and are in no base"),
    "la_relabel_protocol": dict(
        unit="no data yet — the protocol of a planned intra-rater relabel of 50 primary patents",
        base="nothing is computed; the wizard export of the relabel batch is not installed",
        transform="none"),
    "atlas_flagship": dict(
        unit="named companies with two or more unique aircraft (n {n_flagship_firms})",
        base="each company's own aircraft, set beside the aircraft it has made public "
             "(VFS World eVTOL Aircraft Directory)",
        transform="raw counts of labels per class; the two yes/no columns read the public side alone "
                  "and never compare a label with it"),
    "a2_d13_flagship_check": dict(
        unit="named companies with two or more unique aircraft (n {n_flagship_firms})",
        base="each company's own aircraft, set beside the aircraft it has made public",
        transform="raw counts of labels per class; the last two columns are reads of the public side "
                  "alone — whether the company's own public aircraft span more than one class, and "
                  "whether the class it files most is the class of one of them"),
    "la_name_arch_check": dict(
        unit="unique aircraft (n {unique_s}); a public class exists for the aircraft linked to an "
             "evtol.news page only",
        base="the aircraft where at least two of the three sources give a class; the first row "
             "collapses every aircraft whose sources agree, the three rows under it are the aircraft "
             "no comparison can reach (named, with the reason — none was relabelled to make one "
             "possible), and the rest are the disagreements",
        transform="raw counts, no shares; G1 and the whole-patent reading are compared at the twelve "
                  "classes, and both are folded to the directory's five before either meets the "
                  "public class"),
    "a2_d3_selected_fields": dict(
        unit="unique aircraft (n {unique_s}), one row per label field",
        base="per field, the aircraft that answer it (the `answered` column) — not all {unique_s}",
        transform="raw counts of the four most common answers; `top_share` is the share of the "
                  "answered aircraft, so fields with different `answered` are not directly comparable"),
    "atlas_fields": dict(
        unit="(i) coded export columns of the label set, one dot each; (ii) unique aircraft "
             "(n {unique_s})",
        base="(i) all coded columns, whatever they answer; (ii) each class's own aircraft",
        transform="(i) raw counts — aircraft answering the column against its effective number of "
                  "answers (exp of the Shannon entropy of its answers); (ii) box plot (median, "
                  "quartiles, whiskers) of slots answered per aircraft, of {questions}"),
    "a2_d2_informative_fields": dict(
        unit="label fields (n {n_informative}), profiled over unique aircraft (n {unique_s})",
        base="only the fields at least 300 aircraft answer with an effective number of answers of "
             "1.5 or more; the other coded columns are left out of the table, not of the data",
        transform="counts and shares of the aircraft that answer the field; effective answers = exp "
                  "of the Shannon entropy, the number of answers the field behaves as if it had"),
    "atlas_arch_gt": dict(
        unit="unique aircraft (n {unique_s}); the matrix uses only those carrying both a figure label "
             "and a whole-patent reading",
        base="(i) all the aircraft, twice over — labelled from the figures, and read from the whole "
             "patent; (ii) each row is one ground-truth class",
        transform="(i) raw counts, two bars per class; (ii) share of the ground-truth row (rows sum to "
                  "100 %) with the aircraft count in the cell; agreement and κ are over the matrix"),

    # ================================================================ 4.1 what is designed
    "filings_per_year": dict(
        unit="three units across the two graphs — unique aircraft (n {unique_s}) in the bars of (i), "
             "acquired patents (n {acquired_s}) in its line, and all B64 patent publications in (ii)",
        base="(i) each priority year on its own; an aircraft sits in the year of its primary record. "
             "(ii) the same years, divided by every aeronautics (B64) patent of that priority year in "
             "the nine publication offices the corpus draws on (WIPO PATENTSCOPE, fetched 2026-09-22)",
        transform="(i) raw counts per year, not normalised — a rise here may be a rise in patenting at "
                  "large, which is what (ii) answers. (ii) the corpus's patent count and the B64 count "
                  "each indexed to its own 2005-2009 mean = 100, so the two growth rates can be read "
                  "against each other; patents are compared with patents, never aircraft with patents. "
                  "Hatched years are still incomplete on both sides and the ratio is not read there"),
    "la_filings_per_year": dict(
        unit="three units in the same table — unique aircraft (n {unique_s}) by region, acquired "
             "patents (n {acquired_s}), and all B64 patent publications of the same priority years "
             "and publication offices",
        base="each priority year on its own, and the B64 count of that year as the denominator of the "
             "two ratio columns",
        transform="raw counts per year, then the same counts per 1 000 B64 patents and indexed to the "
                  "2005-2009 mean = 100; the patents-per-1 000 column is the like-for-like one, the "
                  "aircraft-per-1 000 column mixes two units and is printed for reference only. "
                  "`complete` is true when the snapshot lies at least the 90th-percentile publication "
                  "lag after the end of the year"),
    "atlas_arch_time": dict(
        unit="unique aircraft (n {unique_s})",
        base="the aircraft of each priority window, n printed under each bar",
        transform="share of the window — each bar is 100 % of that window's aircraft, so the growth of "
                  "the corpus is divided out and only the mix is shown; the underlying counts are raw "
                  "and are not normalised against overall patenting"),
    "a2_d9_architecture_by_window": dict(
        unit="unique aircraft (n {unique_s})",
        base="the aircraft of each priority window (`unique aircraft` column)",
        transform="share of the window; only the four largest classes are printed, so the rows do not "
                  "sum to 1"),
    "firm_weighted": dict(
        unit="two units on the same axes — unique aircraft (n {unique_s}), and filers (a named firm is "
             "one filer, an individual or unattributed patent is its own filer)",
        base="the aircraft, and then the filers, of each window",
        transform="share of the window computed twice; in the filer count each firm casts one vote per "
                  "window, for the class it filed most in that window, which removes the weight of a "
                  "firm that files many aircraft"),
    "la_firm_weighted_shares": dict(
        unit="two units in the same table — unique aircraft (n {unique_s}) and filers",
        base="the aircraft, and then the filers, of each window",
        transform="share of the window under each counting rule; one vote per filer per window, for "
                  "the class it filed most"),
    "two_counts": dict(
        unit="unique aircraft (n {unique_s}), dated two ways",
        base="the aircraft of each window under each dating rule",
        transform="share of the window; solid = the aircraft sits in the window of its primary record, "
                  "dashed = it counts in every window from its first to its last filing, so the dashed "
                  "base is larger than {unique_s}"),
    # 4.1.3's own tables (la_archetype_levels, la_archetype_choice, la_dd_conditions,
    # la_dd_result) carry their entries further down, written by the section's author.
    "dominant_design": dict(
        unit="unique aircraft (n {unique_s}) as archetypes — A0c = class × propulsor-unit bin, "
             "A1t = class × wings × any tilting unit",
        base="the aircraft of each window with a complete archetype key; a window under 10 is left out",
        transform="condition 1 = share of the window held by its largest archetype, against the 50 % "
                  "line; condition 2 = ²D rarefied to 40 aircraft (300 draws) against a 95 % band from "
                  "200 label permutations — rarefaction is what stops a window counting as diverse "
                  "merely for holding more patents"),
    "la_archetype_levels": dict(
        unit="unique aircraft (n {unique_s}) grouped into archetypes, one level per row",
        base="the aircraft carrying an architecture class; an aircraft whose field is hidden by a stage "
             "override is left out of that level and counted under `left out`",
        transform="the level's fields joined into one string per aircraft; counts, singletons, Hill ¹D and "
                  "²D of the archetype shares, and the share of the largest archetype"),
    "la_archetype_choice": dict(
        unit="archetype level",
        base="the numbers of the previous table",
        transform="four screens with the lines fixed in `la_tables.ARCHETYPE_SCREENS`; the resolution line is "
                  "twice the number of architecture classes, computed from the corpus"),
    "la_dd_conditions": dict(
        unit="condition",
        base="Preliminary Analysis 5.7 and 5.10, fixed before any curve of this corpus was drawn",
        transform="none — fixed text; no number of this corpus enters this table"),
    "la_dd_result": dict(
        unit="condition",
        base="the per-window table that follows",
        transform="one sentence per condition, generated from that table; every figure in it is read out of "
                  "the table and none is typed"),
    "la_dominant_design": dict(
        unit="unique aircraft (n {unique_s}) grouped into archetypes (A0c and A1t)",
        base="the aircraft of each window carrying a complete archetype key; windows under 10 left out",
        transform="top share = share of the window; ²D rarefied to 40 aircraft (300 draws) with the "
                  "95 % band of 200 label permutations; `below band` is the test's verdict"),
    "class_configs": dict(
        unit="unique aircraft, one architecture class per line — not an archetype",
        base="the aircraft of one class in one window; a window holding fewer than 5 of them is blanked. "
             "Classes drawn by rule, not by size ranking: every class with 5+ aircraft in 3+ of the 5 "
             "windows (SLC, TR, CVT, TW, MR — 84 % of the classified aircraft; the figure prints the count)",
        transform="share of that class-window holding its single most common configuration — configuration "
                  "= propulsive units banded (1-3 / 4 / 5-6 / 7-8 / 9+) × ducted or open × booms or none × "
                  "tail type. The mode, because a configuration is a combination of categories and has no "
                  "mean. Beside it, the number of distinct configurations — a within-class share, never a "
                  "share of the corpus"),
    "la_class_configs": dict(
        unit="unique aircraft, one architecture class per row — not an archetype",
        base="the aircraft of one class in one window; fewer than 5 leaves the share blank. Classes drawn "
             "by rule: 5+ aircraft in 3+ of the 5 windows (SLC, TR, CVT, TW, MR)",
        transform="`share in it` = share of that class-window holding the most common configuration (a mode, "
                  "not a mean: a configuration is a combination of categories); `distinct configurations` "
                  "is a raw count"),
    "dimension_drift": dict(
        unit="unique aircraft, one architecture class per line — not an archetype",
        base="the aircraft of one class in one window; a window under 5 of them is left out. Classes drawn "
             "by rule: 5+ aircraft in 3+ of the 5 windows (SLC, TR, CVT, TW, MR)",
        transform="median propulsive units (an order statistic, not a mean); every share divides by the "
                  "class's own aircraft in that window that answer the field — in these five classes that "
                  "is all of them, so all four panels sit on one base. No share is a share of rotors"),
    "la_dimension_drift": dict(
        unit="unique aircraft, one architecture class per row — not an archetype",
        base="the aircraft of one class in one window; windows under 5 are left out. Classes drawn by rule: "
             "5+ aircraft in 3+ of the 5 windows (SLC, TR, CVT, TW, MR)",
        transform="medians for propulsive units and wings; every share divides by the aircraft of that "
                  "class-window that answer the field (all of them here), never by a count of rotors"),
    "class_cycles": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own total — the row, never the window",
        transform="share of the class's own total per window, so every row sums to 100 %. This "
                  "deliberately divides out the growth of the corpus: it says when a class lived, "
                  "and says nothing about how big the class is"),
    "la_class_cycles": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own total (the `aircraft` column)",
        transform="row shares summing to 100 % per class; the median window is the window in which "
                  "the class passes half its own aircraft"),
    "lead_lag": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="each group's own aircraft — the region's, or the class's",
        transform="cumulative share of the group's own total by priority year, so every curve ends at "
                  "100 % whatever the group's size; it compares timing, never volume"),
    "la_lead_lag_region": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="each region's own aircraft (the `aircraft` column)",
        transform="the year each region's cumulative share crosses 25, 50 and 75 % of its own total"),
    "la_lead_lag_class": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="each class's own aircraft, seven largest classes",
        transform="the year each class's cumulative share crosses 25, 50 and 75 % of its own total"),
    "hill": dict(
        unit="unique aircraft (n {unique_s}), labelled at A0 (class) and A0c (class × propulsor-unit bin)",
        base="the aircraft of each window, rarefied to a common sample of 40 so the windows are "
             "comparable; a window under 10 aircraft is left out",
        transform="rarefied Hill numbers ⁰D, ¹D and ²D — mean of 1 000 draws of 40 aircraft with a "
                  "95 % band; rarefaction is exactly what removes the effect of a window simply "
                  "holding more patents than another"),
    "la_hill_by_window": dict(
        unit="unique aircraft (n {unique_s}) at A0 and A0c",
        base="the aircraft of each window, rarefied to 40; windows under 10 are left out",
        transform="mean of 1 000 draws of 40 aircraft with the 2.5th and 97.5th percentiles as the band"),
    "zones": dict(
        unit="A0c archetypes (class × propulsor-unit bin) with five or more aircraft (n {n_zones}); "
             "the archetypes below that cut are left out",
        base="(top) the aircraft of the two complete recent windows 2016–23; (bottom) each archetype's "
             "own windows",
        transform="(top) share of those two windows' aircraft against filers per aircraft, bubble area "
                  "= aircraft. (bottom) raw counts in the cell, shaded against the archetype's OWN "
                  "busiest window, so colour compares windows within an archetype, never between them"),
    "la_zones": dict(
        unit="A0c archetypes with five or more aircraft (n {n_zones})",
        base="each archetype's own aircraft and filers; `share 2016-23` is its share of the aircraft "
             "of those two complete windows",
        transform="raw counts per archetype and window, with that one share; the zone label "
                  "(new / persistent / fading) is read from the first and last window the archetype "
                  "appears in"),
    "abandonment": dict(
        unit="primary patents with priority year 2019 or earlier (of the {primary_s}), old enough to "
             "have been granted and then kept or dropped",
        base="the patents of each class",
        transform="share of the class's patents carrying any INACTIVE legal status at the snapshot, "
                  "with the raw patent count beside it; this is a patent-level fact, not an "
                  "aircraft-level one"),
    "la_abandonment_by_class": dict(
        unit="primary patents with priority year 2019 or earlier (of the {primary_s})",
        base="the patents of each class; the last row is all classes together",
        transform="lapsed share = patents with any INACTIVE status ÷ the class's patents, raw counts "
                  "beside it"),

    # ================================================================ 4.2 who designs it
    "coverage": dict(
        unit="named companies ranked by unique aircraft, against the analysis set (n {unique_s})",
        base="the whole analysis set: every share on this figure is taken on {unique_s} aircraft, not "
             "on the corporate subset",
        transform="cumulative share of the analysis set covered by the top N firms; the dashed line is "
                  "the share held by all named companies together, the rest being individuals and "
                  "unattributed filers"),
    "la_firm_tiers": dict(
        unit="named companies, and the unique aircraft they hold (analysis set n {unique_s})",
        base="two different denominators in two columns — the whole analysis set, and the "
             "named-company aircraft only",
        transform="raw counts of firms and aircraft per threshold; the thresholds are nested, so the "
                  "rows are cumulative and must not be added"),
    "filers_over_time": dict(
        unit="named firms (companies and institutes) per window, against the unique aircraft of the "
             "window (analysis set n {unique_s})",
        base="(i) the firms active in each window; (ii) the firms of each entry cohort — a firm is "
             "counted once, in the window of its first filing",
        transform="raw counts of firms; entries and exits are differences between windows, not shares"),
    "la_filers_by_window": dict(
        unit="two units in the same table — named firms, and the unique aircraft of the window "
             "(analysis set n {unique_s})",
        base="the firms and the aircraft of each window",
        transform="raw counts; the two individual/unattributed columns are shares of the window's "
                  "aircraft. `firms last seen` is left blank in the last two windows, because a later "
                  "filing may simply not have published yet"),
    "la_cohorts": dict(
        unit="named firms (each counted once, in the window of its first filing)",
        base="all named firms with a dated filing",
        transform="raw counts; the class is the class of the firm's first aircraft, so a row says what "
                  "a cohort entered with, never what it does now"),
    "atlas_filers": dict(
        unit="(i) and (ii) unique aircraft (n {unique_s}); (iii) primary patents (n {primary_s})",
        base="(i) the aircraft of the 18 largest named companies; (ii) each filer type's own aircraft; "
             "(iii) all the primary patents",
        transform="(i) raw counts; (ii) share of the filer type, each row 100 %; (iii) Lorenz curve — "
                  "cumulative share of patents against cumulative share of filers, the diagonal being "
                  "perfect equality"),
    "firm_tiles": dict(
        unit="named firms with five or more unique aircraft (n {n_firms5})",
        base="each firm's own aircraft in each window",
        transform="raw counts (aircraft of that firm in that window); the tile colour is the class the "
                  "firm filed most in that window, not a share"),
    "a2_d8_filer_mix": dict(
        unit="primary patents (n {primary_s})",
        base="all the primary patents",
        transform="raw counts, with each row's share of the {primary_s}"),
    "a2_d8_concentration": dict(
        unit="primary patents (n {primary_s}), counted once on the raw assignee string and once on "
             "the canonical company",
        base="all {primary_s} patents in both columns, so the two are comparable; the named-company "
             "shares are deliberately taken on all patents, not on the corporate subset",
        transform="concentration measures — distinct filers, one-patent filers, top-10 share and HHI "
                  "(sum of squared shares)"),
    "transitions": dict(
        unit="consecutive pairs of aircraft filed by the same named firm, ordered by priority year "
             "(not aircraft, and not patents)",
        base="each row is the class of the earlier aircraft",
        transform="raw pair counts in the cell, coloured as the share of the earlier class's row; the "
                  "diagonal is a firm repeating its class"),
    "la_transitions": dict(
        unit="consecutive pairs of aircraft filed by the same named firm",
        base="all such pairs over the named firms",
        transform="raw counts per (from, to) pair; no shares"),
    "ip_strategy": dict(
        unit="(i) named firms with five or more unique aircraft (n {n_firms5}); (ii) primary patents "
             "(n {primary_s}) grouped by class",
        base="(i) each firm's own patents and aircraft; (ii) the patents of each class holding 10+",
        transform="(i) patents per aircraft against unique aircraft, x on a log scale, bubble area = "
                  "mean forward citations. (ii) median claims and mean forward citations — citations "
                  "accumulate with age and are NOT age-normalised, so read them against the median "
                  "priority year in the table"),
    "la_ip_strategy": dict(
        unit="named firms with five or more unique aircraft (n {n_firms5})",
        base="each firm's own representative patents (primary plus the O1/O2 re-filings)",
        transform="ratios and order statistics — patents per aircraft, median family size, median "
                  "claims, mean forward citations; forward citations are raw and not age-normalised"),
    "la_ip_by_class": dict(
        unit="primary patents (n {primary_s})",
        base="the patents of each class",
        transform="medians and one mean per class; citations are raw counts that accumulate with age, "
                  "hence the median priority year printed beside them"),
    "spans_by_firm": dict(
        unit="unique aircraft (n {unique_s}) and their re-filings (the O1 / O2 observations), for "
             "firms with five or more aircraft (n {n_firms5})",
        base="(top) only the aircraft filed in more than one year; (bottom) all of the firm's aircraft",
        transform="(top) raw first-to-last year spans, one line per aircraft. (bottom) share of the "
                  "firm's aircraft that were filed again, whatever the span"),
    "proximity_region": dict(
        unit="named firms with five or more unique aircraft (n {n_prox_firms})",
        base="each firm's profile is its own aircraft spread over the classes, so the profile is "
             "independent of how many aircraft the firm has",
        transform="Jaffe (1986) uncentred cosine between firm × class vectors — a proximity between 0 "
                  "(no class in common) and 1 (identical mix), never a share or a distance in any unit"),
    "a2_d14_firm_proximity": dict(
        unit="named firms with five or more unique aircraft (n {n_prox_firms})",
        base="each firm's own aircraft, spread over the classes",
        transform="Jaffe (1986) uncentred cosine, computed twice — on the class alone, and on the "
                  "class crossed with the propulsor-count bin"),
    "la_proximity_region": dict(
        unit="pairs of firms (over the {n_prox_firms} firms with five or more aircraft)",
        base="all firm pairs, split into same-region and different-region",
        transform="mean and median proximity per group; the pair count is printed because the two "
                  "groups are very different sizes"),
    "ari": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="the index side is the index's own release; the patent side is this corpus's aircraft of "
             "the same firm",
        transform="raw index scores, disclosed funding and raw corpus counts — nothing is normalised; "
                  "with n = {n_ari} firms this is descriptive only"),
    "ari_history": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="(i) each firm's score per index release; (ii) each firm once",
        transform="raw scores over time and raw funding against raw aircraft counts; no trend is fitted"),
    "ari_clock": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="each firm's own first, peak and last priority year in the corpus, against the dates the "
             "index states",
        transform="raw years; the two clocks come from different sources and are only set side by side"),
    "la_ari_firms": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="each firm's own aircraft in the corpus, beside its index entry",
        transform="raw counts and the index's own score and funding; nothing is normalised"),
    "la_ari_correlation": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari}); n per row is printed",
        base="the firms for which both sides of the pair have a value",
        transform="Spearman rank correlation — descriptive only at this n; no inference is drawn and "
                  "no correction for multiple comparisons is applied"),
    "la_ari_timeline": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="each firm's own priority years in the corpus, beside the index's stated dates",
        transform="raw years, no shares"),
    "la_trl_placeholder": dict(
        unit="no data yet — the TRL work is not installed",
        base="nothing is computed",
        transform="none"),

    # ================================================================ 4.3 where
    "atlas_region": dict(
        unit="(i) patents — acquired (n {acquired_s}) and representative (n {representative_s}) of "
             "each applicant country; (ii) unique aircraft (n {unique_s})",
        base="(i) each country's own patents; (ii) each region's own aircraft, n printed on the row",
        transform="(i) raw counts, with the representative share of that country printed; (ii) share "
                  "of the region, each row 100 %"),
    "region_grid": dict(
        unit="unique aircraft (n {unique_s}); the three main applicant regions only, "
             "'Other regions' is left out",
        base="each region × window cell on its own; a cell holding fewer than 10 aircraft is blanked",
        transform="share of the cell, each region × window row summing to 100 %; region is the "
                  "applicant's region, not the publication office"),
    "region_grid_b": dict(
        unit="unique aircraft (n {unique_s}); the three main applicant regions only",
        base="each region × window cell on its own; cells under 10 aircraft are blanked",
        transform="share of the cell, each region × window row summing to 100 %"),
    "specialisation": dict(
        unit="A0c archetypes with five or more aircraft (n {n_special}), over the three main regions",
        base="the archetype's share inside one region, divided by its share over all three regions "
             "together",
        transform="location quotient — 1 = the same share as everywhere, 2 = twice it. It is a ratio, "
                  "not a share, and it is already normalised for how much each region files, so a big "
                  "region cannot score high merely by being big"),
    "la_specialisation": dict(
        unit="A0c archetypes with five or more aircraft (n {n_special})",
        base="the archetype's share in the region ÷ its share over the three regions",
        transform="location quotient (1 = as everywhere); the `aircraft` column is the raw count "
                  "behind the row"),
    "country_class": dict(
        unit="unique aircraft (n {unique_s}) of the eight largest applicant countries",
        base="each country's own aircraft, n printed per row",
        transform="share of the country, each row 100 %; the countries below the top eight are left out"),
    "la_country_class": dict(
        unit="unique aircraft (n {unique_s}) of the eight largest applicant countries",
        base="each country's own aircraft (the `aircraft` column)",
        transform="row shares summing to 100 % per country"),

    # ================================================================ 5 low level
    "atlas_powertrain": dict(
        unit="unique aircraft (n {unique_s})",
        base="(i) each class's own aircraft, n on the row; (ii) each window's own aircraft",
        transform="share of the row; 'not stated' is kept as its own answer and never dropped, so "
                  "these are shares of all aircraft, not of the ones with a stated powertrain"),
    "la_powertrain_by_class": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own aircraft (the `aircraft` column)",
        transform="raw counts; 'not stated' is its own column and is never folded into the others"),
    "atlas_units": dict(
        unit="unique aircraft (n {unique_s}) carrying a propulsor record — HB and PFV have no "
             "propulsor card and are left out, never counted as zero",
        base="(top) each class's own aircraft; (bottom) only those where the feature can be read, "
             "printed as read / total under the class code",
        transform="(top) one dot per aircraft, bar = quartiles, ring = median, units capped at 30 for "
                  "the drawing only; (bottom) share of that readable base carrying the feature"),
    "atlas_design_heatmaps": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own aircraft — every row of every panel sums to 100 % of its class",
        transform="share of the class; a value an override hides is shown as 'not determinable' "
                  "rather than blank, and the answers outside the seven most common are pooled as "
                  "'other'"),
    "atlas_state_by_arch": dict(
        unit="whole-aircraft figures (n {figures_approved_s}) — an image-level item, not an "
             "aircraft-level one, so an aircraft with many figures weighs more",
        base="each architecture's own approved figures, n printed on the row",
        transform="share of the row; the number under each column name is that flight state's figure "
                  "total across all classes"),
    "a2_d2_figure_slot_answers": dict(
        unit="whole-aircraft figures (n {figures_approved_s}) — image level, not aircraft level",
        base="per slot, the figures that answer it",
        transform="raw counts of the four most common answers; the flight-state row lists every state "
                  "of the codebook, zeros included"),
    "mission": dict(
        unit="the unique aircraft linked to an evtol.news page — a subset of the {unique_s}, never "
             "the whole analysis set",
        base="each folded class's own linked aircraft, n printed on the bar",
        transform="(i)–(iv) share of the folded class, each bar 100 %; the bottom panel is the share "
                  "of the patent-class row with the aircraft count in the cell. The mission fields are "
                  "parsed from the directory page text, not from the patent"),
    "la_class_fold": dict(
        unit="unique aircraft (n {unique_s})",
        base="all the aircraft, by G1 class",
        transform="raw counts; the table is the fold rule itself, not a measurement"),
    "la_mission_capacity": dict(
        unit="the unique aircraft linked to an evtol.news page (a subset of the {unique_s})",
        base="all the linked aircraft; the `all` column is the row total",
        transform="raw counts, parsed from the page text; 'not stated' is kept as its own row"),
    "la_mission_piloting": dict(
        unit="the unique aircraft linked to an evtol.news page (a subset of the {unique_s})",
        base="all the linked aircraft; the `all` column is the row total",
        transform="raw counts, parsed from the page text; 'not stated' is kept as its own row"),
    "la_mission_power source": dict(
        unit="the unique aircraft linked to an evtol.news page (a subset of the {unique_s})",
        base="all the linked aircraft; the `all` column is the row total",
        transform="raw counts, parsed from the page text — the directory's word, not the patent's"),
    "la_mission_status": dict(
        unit="the unique aircraft linked to an evtol.news page (a subset of the {unique_s})",
        base="all the linked aircraft; the `all` column is the row total",
        transform="raw counts, parsed from the page's status text"),
    "la_mission_agreement": dict(
        unit="the unique aircraft linked to an evtol.news page (a subset of the {unique_s})",
        base="each row is one folded patent class",
        transform="raw counts of the same aircraft under the two classifications; no shares"),
    "industry_by_class": dict(
        unit="unique aircraft (n {unique_s}); the industry is one value per patent from the identity "
             "text classifier, not from the label cards",
        base="each class's own aircraft, n printed on the row",
        transform="share of the class, each bar 100 %; 'general / unspecified' is about half the "
                  "corpus and is kept in the base"),
    "la_industry_by_class": dict(
        unit="unique aircraft (n {unique_s}); industry from the identity text classifier",
        base="each class's own aircraft (the `aircraft` column)",
        transform="raw counts; 'General_Unspecified' is kept as its own column"),
    "examination": dict(
        unit="primary patents (n {primary_s}) — a patent-level item, not an aircraft-level one",
        base="(i) each of the six largest publication offices; (ii) each class",
        transform="share of the row with the raw patent count beside it; the legal status is PatSeer's "
                  "at the snapshot, so a pending application may still change"),
    "la_examination_office": dict(
        unit="primary patents (n {primary_s})",
        base="the patents of each of the six largest publication offices (the `patents` column)",
        transform="raw counts per status; the offices below the top six are left out"),
    "la_examination_class": dict(
        unit="primary patents (n {primary_s})",
        base="the patents of each class (the `patents` column)",
        transform="raw counts per status"),
}


def _owner_level(name: str) -> str:
    """The ``level`` of the section that owns a figure or table, inherited from its parents."""
    owner = next((n["id"] for n in NODES
                  if name in n.get("figures", []) or name in n.get("tables", [])), None)
    if owner is None:
        return ""
    ids = [owner]
    while "." in ids[-1]:
        ids.append(ids[-1].rsplit(".", 1)[0])
    for i in ids:
        try:
            lvl = node(i).get("level")
        except KeyError:
            continue
        if lvl:
            return lvl
    return ""


def _clean(text_: str) -> str:
    """Drop what could not be resolved rather than printing a placeholder at the reader."""
    text_ = _re.sub(r"\s*\(n \{[^{}]*\}\)", "", text_)      # an unresolved count: drop the "(n …)"
    text_ = _re.sub(r"\{[^{}]*\}", "…", text_)              # anything else: an honest ellipsis
    return _re.sub(r"\s{2,}", " ", text_).strip().rstrip(".")


def provenance(name: str, values: Optional[Dict] = None, kind: str = "figure",
               tables: Optional[Dict] = None) -> str:
    """The one grey line printed under figure or table ``name``.

    ``Unit`` says what is being counted and how many there are, ``Base`` the denominator any
    share is taken on, ``Transform`` what was done to the numbers. ``name`` is the internal
    key, so the line follows the item through a renumbering. An item with no
    :data:`PROVENANCE` entry falls back on the unit of the section that owns it and says the
    rest is not recorded — an honest gap, never a guess.
    """
    entry = PROVENANCE.get(name)
    if entry is None:
        entry = {"unit": LEVEL_UNIT.get(_owner_level(name), ""), "base": MISSING, "transform": MISSING}
    vals = dict(values or {})
    for key, tname in N_FROM_TABLE.items():
        frame = (tables or {}).get(tname)
        if frame is not None:
            vals[key] = len(frame)
    parts = []
    for label in ("unit", "base", "transform"):
        txt = _clean(_pa._fill(str(entry.get(label) or ""), vals))
        if txt:
            parts.append(f"{label.capitalize()}: {txt}")
    return " · ".join(parts)
