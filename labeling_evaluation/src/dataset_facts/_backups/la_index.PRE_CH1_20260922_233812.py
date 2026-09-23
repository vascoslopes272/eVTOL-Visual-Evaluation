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
    "la_filings_per_year": "Representative unique aircraft and acquired patents per priority year; a year is incomplete while the snapshot is within the 90th-percentile publication lag of it",
    "la_flags": "Items flagged as candidates to leave out of the high-level document — the author decides; nothing has been removed",
    "la_dominant_design": "The dominant-design test per window: top archetype share (condition 1) and rarefied ²D against the permutation band (condition 2)",
    "la_class_configs": "Within-class convergence: modal configuration per class and window, its share and the number of configurations",
    "la_dimension_drift": "Dimension drift per class and window: propulsor units, ducted, tilting, booms, wings",
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
    "atlas_arch_gt": "image label against the whole-patent reading: agreement and confusion",
    "atlas_arch_time": "architecture mix per priority window",
    "atlas_powertrain": "powertrain stated in the patent",
    "atlas_fields": "field informativeness and label depth",
    "atlas_fill": "fill rate of each field where its part exists",
    "atlas_flagship": "flagship check: labels of the largest filers against their public products",
    "atlas_units": "propulsor units and their arrangement",
    "atlas_design_heatmaps": "the design space as heatmaps of paired fields",
    "firm_weighted": "class share per window, every aircraft against one vote per filer",
    "spans_by_firm": "re-filing of the same aircraft, by firm",
    "two_counts": "class share per window, aircraft counted once or in every window it was filed in",
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
    "filings_per_year": "unique aircraft per priority year by applicant region, acquired patents as a line; hatched years are still incomplete at the snapshot (90th-percentile publication lag)",
    "dominant_design": "the dominant-design test per window: top archetype share against the 50 % line, and ²D against the permutation band",
    "class_configs": "within-class convergence, four largest classes",
    "dimension_drift": "dimension drift inside the four largest classes per window",
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
    "atlas_fields": [("every coded column, by kind", 1), ("label depth by architecture", 1)],
    "atlas_arch_gt": [("the classes of the analysis set", 1), ("agreement and confusion matrix", 1)],
    # --- 4.1 what is designed
    "atlas_arch_time": [("architecture share per window", 1), ("the five largest classes over time", 1)],
    "dominant_design": [("condition 1: top archetype share", 1), ("condition 2: ²D at A0c against the band", 1),
                        ("condition 2: ²D at A1t against the band", 1)],
    "class_configs": [("share of the modal configuration", 1), ("configurations the class holds", 1)],
    "dimension_drift": [("median propulsor units", 1), ("ducted share", 1), ("tilting share", 1), ("boom share", 1)],
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
    "two_counts": [("one panel per class", 4)],
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
    "la_flags": 20, "la_class_configs": 20, "la_dimension_drift": 20, "la_ip_strategy": 20, "la_ari_timeline": 20,
    "la_specialisation": 20, "la_dominant_design": 10, "la_transitions": 12,
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
    "la_dominant_design": ["level", "window", "aircraft", "top archetype", "top share", "D2", "D2 permutation low",
                           "D2 permutation high", "below band"],
    "la_class_configs": ["class", "window", "aircraft", "configurations", "modal share", "modal configuration"],
    "la_dimension_drift": ["class", "window", "aircraft", "median propulsor units", "ducted share", "tilting share",
                           "boom share", "median wings"],
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
    dict(id="3.3", title="Flagship check", figures=["atlas_flagship"], tables=["a2_d13_flagship_check"]),
    dict(id="3.4", title="Most common answers", tables=["a2_d3_selected_fields"]),
    dict(id="3.5", title="Field inventory", figures=["atlas_fields"], tables=["a2_d2_informative_fields"]),
    dict(id="3.6", title="Image label against the whole-patent reading", figures=["atlas_arch_gt"]),
    # ================================================================ 4
    dict(id="4", title="Preliminary Analysis", level="unique aircraft"),
    dict(id="4.1", title="What is being designed, and whether it converges", level="unique aircraft"),
    dict(id="4.1.1", title="Filings per year", figures=["filings_per_year"], tables=["la_filings_per_year"]),
    dict(id="4.1.2", title="Class shares per window", figures=["atlas_arch_time", "firm_weighted", "two_counts"],
         tables=["a2_d9_architecture_by_window"]),
    dict(id="4.1.3", title="The dominant-design test", figures=["dominant_design"], tables=["la_dominant_design"]),
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
