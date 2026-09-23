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
    "la_class_region_timing": (
        "Median priority year of each class inside each applicant region, with the aircraft each cell "
        "rests on. Complete priority years only (to 2023); a cell of fewer than five aircraft is left "
        "unread and printed “–”. A region that simply files later shows as a whole column shifted; a "
        "class one region took up before the others shows as one cell out of line with its own row"),
    "la_hill_by_window": "Rarefied Hill numbers per window (40 aircraft, 1 000 draws): richness ⁰D, ¹D and ²D with 95 % bands",
    "la_zones": "A0c archetypes with five or more aircraft: size, distinct filers, span of windows and zone",
    "la_class_filer_weight": (
        "How much of each class is one filer repeating itself. `its share` is the fraction of the class "
        "held by its single largest filer — the direct answer to how much weight one company carries. "
        "`effective filers` is 1 / Σ(share²) over filers: the number of equally sized filers that would "
        "give the same concentration, so it falls towards 1 as one filer takes a class over and equals "
        "the filer count when every filer holds one aircraft. The last three columns count the class's "
        "share of the corpus twice, once per aircraft and once with every filer casting one vote for "
        "the class it filed most; their ratio is how much of the class's apparent size is repetition"),
    "la_abandonment_by_class": "Primary patents no longer in force per class, priority year 2019 or earlier",
    "la_country_class": "Class share per applicant country, eight largest countries",
    "la_firm_tiers": "Firm tiers: how many firms and aircraft each threshold keeps",
    "la_coverage_segments": "The firm-size ranking cut into disjoint segments: firms, aircraft and share per segment "
                            "(these add up; the nested rows of the tier table do not)",
    "la_market_vs_patents": "Market standing against patenting: the named firms the AAM Reality Index rates against "
                            "the named firms it does not, and the two correlations taken inside the index itself",
    "la_filer_mix": "Who filed, in both units: primary patents and the share per primary patent, unique aircraft and "
                    "the share of the analysis set, and the aircraft a filer type gets out of one patent",
    "la_firm_leverage": "Firm leverage: how far the class shares move when one firm is dropped from the analysis set, "
                        "over the whole set and inside its busiest window",
    "la_class_concentration": "Class concentration: named firms filing in each class, and the share of the class held "
                              "by its largest filer and by its three largest",
    "la_cohort_mix": "Entrants against the field: per window and class, the share of the entering FIRMS that enter "
                     "with the class beside the share of the window's AIRCRAFT in it",
    "la_filers_by_window": "Named firms per window: active, new, continuing, last seen, and the individuals' share",
    "la_proximity_region": (
        "Mean technological proximity by pair of regions. Every pair of the firms in Figure 4.2.6 is put in "
        "one of six boxes by the two regions it joins, and the table gives the number of pairs in the box "
        "and the mean, median, lowest and highest proximity in it. The three `within` rows are a region against itself and are "
        "the diagonal boxes of the figure; the three `across` rows are the rest of it. Read down the mean "
        "column: a high `within` row is a region whose firms design alike, a low one a region that is "
        "internally split. The question the table settles is whether firms resemble their own region more "
        "than another, and the Source line of Figure 4.2.6 carries the permutation test that answers it"),
    "la_ari_firms": "AAM Reality Index firms that file in the corpus: score, funding, patented aircraft and class mix",
    "la_ari_correlation": (
        "Spearman rank correlation between the index side and the patent side, firm by firm. Every pair of "
        "one index quantity and one patent-side measure is tested and the whole family is corrected: `q` is "
        "the Benjamini-Hochberg adjustment of `p` over all the rows, and `holds?` reads it — `yes` at q below "
        "0.10, `chance-level` where p alone is under 0.05 but the correction does not survive, `no` "
        "otherwise. With at most 18 firms this table is not where the answer is; Table 4.2.7c is"),
    "la_ari_gap": (
        "What actually separates the index firms from the rest of the corpus — one row per labelled or "
        "bibliographic variable, comparing the unique aircraft of the AAM Reality Index firms with every "
        "other unique aircraft in the analysis set. The two value columns are medians for a number and "
        "shares for a yes/no field; for a category the level the two sides differ most on is named with both "
        "shares. `q` corrects `p` over the whole table. The last two columns are the honest check: the index "
        "firms are far more US-published than the rest, so every test is run again on the US-published "
        "patents alone — `holds?` says `yes` only when the difference survives that, `office effect` when it "
        "does not, and `yes, by selection` for the applicant region, which is what the index selects on"),
    "la_trl_placeholder": "TRL-ranked firms: planned figures, pending the TRL work",
    "la_class_fold": "The twelve G1 classes folded to the five evtol.news directory classes",
    "la_mission_capacity": "Capacity stated on the evtol.news page, by folded class (linked aircraft, counts)",
    "la_mission_piloting": "Piloting stated on the page, by folded class",
    "la_mission_power source": "Power source stated on the page, by folded class",
    "la_mission_status": "Development status of the page, by folded class",
    "la_mission_agreement": "Folded patent class against the directory's own class of the same aircraft",
    "la_filings_per_year": "Representative unique aircraft and acquired patents per priority year, and the same counts against all aeronautics (B64) patents of the same priority years and publication offices; every year has its own row here, while the first bar of Figure 4.1.1 pools 1999-2005; a year is incomplete while the snapshot is within the 90th-percentile publication lag of it",
    "la_flags": "Items flagged as candidates to leave out of the high-level document — the author decides. Already removed and therefore no longer listed: the two 4.1.2 robustness figures and Table 4.1.2 (2026-09-22), and Tables 4.1.6, 4.3.3, 4.3.4, 5.1 and 5.5g (2026-09-23). A removed table's builder is kept, so its CSV is still written to tables/",
    "la_archetype_levels": "Every archetype level the codebook can form: the dimensions it combines, its largest archetype, how many archetypes it yields, how many aircraft end up alone in one, the effective number of archetypes (Hill ¹D) and where this document reads the level. The counting columns reproduce table 3.3.6 of the Preliminary Analysis",
    "la_archetype_choice": "Which of those levels can carry a design species: four screens applied to the numbers of the previous table, each cell printing the level's value and whether it clears the line. A level that clears all four can still be set aside on a codebook ruling, and the reason is printed",
    "la_dd_conditions": "The three conditions of the dominant-design test as they were fixed in the Preliminary Analysis (5.7), before any curve of this corpus was drawn: what each one tests, the threshold, and where the threshold comes from. No number of this corpus enters this table",
    "la_dd_q": "Condition 3 per window at both levels: Rao's quadratic entropy Q of the Gower distance fixed in Preliminary Analysis 5.3, the level of the two earliest windows it is measured against, and the permutation band of the difference. Reported under the subsystem weighting 5.3 fixes as the main one, and under uniform weighting as the robustness check 5.3 requires",
    "la_dd_result": "What the corpus answers, one generated sentence per condition. Every figure in the sentences is read out of the per-window tables that follow; none of them is typed",
    "la_dominant_design": "The dominant-design test per window: top archetype share (condition 1) and rarefied ²D against the permutation band (condition 2)",
    "la_class_configs": "Within-class convergence per class and window: the configuration most of the class's unique "
                        "aircraft share, how many of them hold it, and how many distinct configurations the class holds. "
                        "A configuration is one aircraft's combination of four label fields — propulsive units banded "
                        "(1-3 / 4 / 5-6 / 7-8 / 9+), ducted or open, booms or no booms, and tail type",
    "la_dimension_drift": "Dimension drift per class and window: median propulsive units, and the share of the class's "
                          "own unique aircraft in that window with a ducted unit, with no tail surface, with booms and "
                          "electric-only. The denominator is the `aircraft` column, never a count of rotors — except for "
                          "the powertrain share, which divides by `powertrain stated`, the aircraft whose patent states "
                          "one. The tilting column is kept but not drawn: it is flat by definition of the classes, and "
                          "its two points off 100 % are an internal check on the labelling",
    "la_transitions": "Within-firm successions: class of the earlier aircraft against the class of the next one",
    "la_ip_strategy": (
        "IP strategy per firm (5+ aircraft): patents per aircraft, family size, claims, citations. Two "
        "citation columns are printed on purpose. `mean forward citations` is the raw count and is what the "
        "bubbles of Figure 4.2.5a are sized by; it rewards age, because a patent from 2013 has had thirteen "
        "years to be cited. `median cohort citation rank` takes the age out — each of the firm's patents is "
        "ranked against every corpus patent of its own priority year and the firm's median rank is printed, "
        "so 0.50 is a firm cited like the median patent of its years and 0.90 a firm in the top tenth of "
        "them. Where the two columns disagree, the firm is old rather than influential. `median claims` sits "
        "beside `main office` because claim counts are an office convention before they are a strategy: the "
        "corpus median is 20 claims at the USPTO and 10 at the CNIPA"),
    "la_ip_by_class": (
        "Claims, citations and family size per class, primary patents. Every column is a median except "
        "`mean forward citations`, and each choice is deliberate: claims and family size are small skewed "
        "counts where one very long application would drag a mean, so the median is the value a reader can "
        "check against a typical patent of the class; citations are given as both a mean (the total "
        "attention the class has drawn, and the bubble size of Figure 4.2.5a) and a median (what a typical "
        "patent of the class draws), because their distribution is so skewed that the two say different "
        "things — where they are far apart the class rests on one or two patents. Both are raw and therefore "
        "reward age, which is why `median priority year` is printed beside them and why the column to "
        "compare classes on is `median cohort citation rank`, each patent ranked inside its own priority "
        "year. `US share` is printed next to the claims because a class's median claim count mostly reflects "
        "where it files"),
    "la_cohorts": "Entry cohorts: firms by first-filing window and the class they entered with",
    "la_ari_timeline": (
        "Patent clock against market clock, firm by firm: first, peak and last patent in this corpus, "
        "against the first flight and the entry into service the index states, and the two gaps between "
        "them. Both market dates come from the `first_flight` and `eis` fields of "
        "`assets/external/aam_reality_index/ari_may2026.csv`; they are the index's own statements, not a "
        "flight register, and an entry into service is a plan. `years to first flight` and `years to entry "
        "into service` count from the firm's earliest priority year *in this corpus*, which is the first "
        "eVTOL patent the labelling reached and not the firm's first patent ever, so a firm that flew before "
        "it appears here prints a negative number and every figure in the two columns is a floor"),
    "la_ari_clock_region": (
        "Which regions and authorities move from patent to flight fastest: the medians of Table 4.2.7d, "
        "grouped first by the certifying authority the index names and then by the applicant region of the "
        "firm's patents. The firms behind each row are listed, because no row rests on more than five of "
        "them — the table ranks jurisdictions, it does not measure them, and the two truncations of Table "
        "4.2.7d carry over"),
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
    "atlas_units": "propulsive units and their arrangement",
    "atlas_design_heatmaps": "the design space as heatmaps of paired fields",
    # parked 2026-09-22: built on request only, not placed in NODES — the caption is kept so putting the
    # name back in a node is the only edit needed to bring the figure back.
    "firm_weighted": "class share per window, every aircraft against one vote per filer",
    "spans_by_firm": "re-filing of the same aircraft, by firm",
    "two_counts": "class share per window, aircraft counted once or in every window it was filed in",  # parked, see above
    "lead_lag": "lead and lag: the quarter, the median and the three quarters year of each region and "
                "each class on one axis, and the median year of each class inside each region",
    "class_cycles": "where in time each class lives: one bar per class, its aircraft per window as a "
                    "percentage of its own total, with the band that percentage carries",
    "hill": "how many kinds of aircraft a window holds, every window cut to the same 40 aircraft",
    "zones": "archetypes with five or more aircraft: crowded against open, and activity per window",
    "filer_weight": "how much of a class is one filer repeating itself: the three largest filers of "
                    "each class, and the largest filer of each class inside each window",
    "abandonment": "primary patents no longer in force, per class",
    "region_grid": "three variables per region and window",
    "region_grid_b": "three more variables per region and window",
    "country_class": "class share per applicant country",
    "coverage": "how much of the analysis set the top N firms cover, and whether market standing tracks patenting",
    "filers_over_time": "the body of filers over time, and what the firms entering each window enter with",
    "firm_tiles": "firms with five or more aircraft per window: aircraft and the class filed most",
    "firm_influence": "which firms could move the reading, and how much of a class one firm holds",
    "proximity_region": "technological proximity between firms, grouped in region blocks",
    "ari": "AAM Reality Index firms that file in the corpus: score, history, funding and class mix",
    "mission": "mission of the linked aircraft by folded class, and the agreement with the directory's class",
    "linked_check": "whether the aircraft linked to an evtol.news page stand for the whole analysis set",
    "ari_history": "how each index firm's score moved, and disclosed funding against patented aircraft",
    "ari_clock": "the patent clock against the market clock for the index firms, one row per firm",
    "filings_per_year": "unique aircraft per priority year by applicant region, acquired patents as a line, and the same filings indexed against all aeronautics (B64) patenting of the same offices; hatched years are still incomplete at the snapshot (90th-percentile publication lag)",
    "dominant_design_q": "condition 3 of the dominant-design test: Q per window against the level of the earliest windows and the permutation band",
    "dominant_design": "the dominant-design test per window: top archetype share against the 50 % line, and ²D against the permutation band",
    "class_configs": "within-class convergence: how far each architecture class settles on a single configuration. "
                     "A line is a class, not an archetype, and the unit is the unique aircraft; a configuration is one "
                     "aircraft's combination of propulsive units (banded), ducted or open, booms or no booms, and tail "
                     "type. Every class with at least 5 aircraft in at least 3 of the 5 windows is drawn — the Source "
                     "line under the figure gives the classes and the share of the corpus they cover",
    "dimension_drift": "dimension drift inside each architecture class, per window: panels (i)–(iv) are the four label "
                       "fields the configuration of Figure 4.1.4 is made of, read one at a time, then powertrain. A line "
                       "is a class, not an archetype; every percentage is a share of that class's own unique aircraft in "
                       "that window, not of rotors — except the powertrain panel, which divides by the aircraft whose "
                       "patent states a powertrain and says so in its own title",
    "transitions": "within-firm successions: what class a firm's next aircraft takes",
    "ip_strategy": "IP strategy: depth and breadth per firm, then claims and citations per class read with and without the age of the patent",
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
    "dominant_design_q": [("Q per window, both weightings", 1), ("condition 3: ΔQ at A0c against the band", 1),
                          ("condition 3: ΔQ at A1t against the band", 1)],
    "dominant_design": [("condition 1: top archetype share", 1), ("condition 2: ²D at A0c against the band", 1),
                        ("condition 2: ²D at A1t against the band", 1)],
    "class_configs": [("share of the class in its single most common configuration", 1),
                      ("distinct configurations per aircraft", 1)],
    "dimension_drift": [("median propulsive units per aircraft", 1), ("% of aircraft with a ducted unit", 1),
                        ("% of aircraft with no tail surface", 1), ("% of aircraft with booms", 1),
                        ("% electric-only, of the aircraft whose powertrain is stated", 1)],
    "hill": [("A0, the architecture class", 1), ("A0c, class × propulsive-unit count", 1)],
    "lead_lag": [("25 %, median and 75 % year of each region and each class", 1),
                 ("median year of each class inside each region", 1)],
    "zones": [("crowded against open", 1), ("aircraft per window for each archetype", 1)],
    "filer_weight": [("the three largest filers of each class", 1),
                     ("the largest filer of each class inside each window", 1)],
    # --- 4.2 who designs it
    "coverage": [("cumulative share of the analysis set by firm rank, with the segment counts", 1),
                 ("rated by the AAM Reality Index against not rated, per firm", 1),
                 ("position on the index against unique aircraft", 1)],
    "filers_over_time": [("filers per window: entries, returners, exits", 1),
                         ("class mix of the entering firms beside the class mix of the window's aircraft", 1)],
    "firm_influence": [("how far the class shares move if one firm is dropped", 1),
                       ("share of each class held by its largest filers", 1)],
    "transitions": [("every pair of aircraft one firm filed one after the other", 1),
                    ("share of each class's pairs that stay in the class", 1)],
    "atlas_filers": [("top companies by unique aircraft", 1), ("architecture mix by filer type", 1),
                     ("concentration of filing (Lorenz)", 1)],
    "ip_strategy": [("depth against breadth, per firm — bubble area = mean forward citations", 1),
                    ("median claims per class, with the class's US share", 1),
                    ("citations per class with age taken out (cohort rank)", 1)],
    "spans_by_firm": [("aircraft filed again over several years", 1), ("share of a firm's aircraft filed more than once", 1)],
    "ari_history": [("score per release", 1), ("funding against patented aircraft", 1)],
    # --- 4.3 where
    # the last row of each grid is the region's share of the window, added 2026-09-23 so the figure
    # can answer "did this region grow or shrink", not only "did its internal mix change"
    "region_grid": [("class", 3), ("propulsive units", 3), ("tilting unit", 3),
                    ("share of the window", 3)],
    "region_grid_b": [("ducted unit", 3), ("powertrain", 3), ("filer type", 3),
                      ("share of the window", 3)],
    # --- 5 low level
    "atlas_powertrain": [("by architecture", 1), ("by priority window", 1)],
    "atlas_units": [("propulsive units per class", 1), ("arrangement features per class", 1)],
    "atlas_design_heatmaps": [("wings", 1), ("fuselage motion", 1), ("booms", 1), ("any propulsor tilts", 1),
                              ("tail type", 1), ("landing gear", 1)],
    "atlas_region": [("applicant country", 1), ("architecture mix by region", 1)],
    "mission": [("capacity", 1), ("piloting", 1), ("power source", 1), ("status", 1),
                ("patent class against the directory's class", 1)],
    "examination": [("by publication office", 1), ("by class", 1)],
    # --- one graph drawn over several axes: no numerals
    # one graph on one axes since 2026-09-23 (the two log-ratio strips became a dot chart)
    "specialisation": [("regional specialisation by archetype", 1)],
    # 2026-09-23: class_cycles is one graph now (one stacked bar per class on one axes), so it takes
    # no numerals and is deliberately absent from this map — see the note at the top of it.
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
    "class_cycles": "100%", "hill": "100%", "zones": "100%", "abandonment": "92%", "filer_weight": "100%",
    "country_class": "92%", "coverage": "96%", "filers_over_time": "96%", "firm_tiles": "96%", "firm_influence": "100%",
    "proximity_region": "96%", "ari": "100%", "dominant_design": "100%", "dominant_design_q": "100%", "class_configs": "100%",
    "dimension_drift": "100%", "ip_strategy": "100%",
    "industry_by_class": "96%", "examination": "100%", "filings_per_year": "100%",
    "linked_check": "100%",
}

#: figures printed on their own A4-landscape page
LANDSCAPE = {"codebook_classes", "codebook_dimensions"}

ROW_CAP: Dict[str, int] = {
    **_pa.ROW_CAP,
    "la_zones": 20, "la_ari_firms": 20, "la_firm_weighted_shares": 25, "la_country_class": 8,
    "la_hill_by_window": 10, "la_class_cycles": 12, "la_abandonment_by_class": 13, "la_class_fold": 12,
    "la_class_filer_weight": 12, "la_class_region_timing": 7,
    "la_name_arch_check": 24,   # 1 summary + the 3 aircraft no comparison reaches + 20 disagreements
    "la_flags": 20, "la_class_configs": 25, "la_dimension_drift": 25, "la_ip_strategy": 20, "la_ari_timeline": 20,
    "la_ari_gap": 14, "la_ari_clock_region": 12, "la_ari_correlation": 14, "la_proximity_region": 8,
    "la_specialisation": 20, "la_dominant_design": 10, "la_transitions": 12,
    "la_archetype_levels": 12, "la_archetype_choice": 12, "la_dd_conditions": 4, "la_dd_result": 4,
    "la_dd_q": 20,
    "la_market_vs_patents": 12, "la_coverage_segments": 6, "la_filer_mix": 6, "la_class_concentration": 12,
    "la_firm_leverage": 12,     # the firms below the twelfth move no share by a tenth of a point
    "la_cohort_mix": 24,
}
COLUMNS: Dict[str, List[str]] = {
    **_pa.COLUMNS,
    "la_class_filer_weight": ["class", "aircraft", "filers", "named firms", "largest filer", "its aircraft",
                              "its share", "top 3 share", "effective filers", "share by aircraft",
                              "share one vote per filer", "repetition factor"],
    # the `p` column is the sort key the figure reads; the printed `test` column carries it in words
    "la_market_vs_patents": ["reading", "AAM index firms", "other named firms", "test"],
    "la_firm_leverage": ["firm", "unique aircraft", "share of the analysis set", "class most moved",
                         "shift if the firm is dropped (pp)", "largest shift inside one window (pp)",
                         "that window", "that class"],
    "la_cohort_mix": ["window", "class", "firms entering", "entering with this class", "share of entrants",
                      "aircraft of this class", "share of aircraft", "entrants ahead of the field (pp)"],
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
    "la_dd_q": ["level", "weighting", "window", "aircraft", "Q", "ΔQ", "ΔQ permutation low",
                "ΔQ permutation high", "below band"],
    "la_dominant_design": ["level", "window", "aircraft", "top archetype", "top share", "D2", "D2 permutation low",
                           "D2 permutation high", "below band"],
    "la_class_configs": ["class", "window", "aircraft", "most common configuration", "share in it",
                         "distinct configurations"],
    "la_dimension_drift": ["class", "window", "aircraft", "median propulsive units", "share with a ducted unit",
                           "share with no tail surface", "share with booms", "powertrain stated",
                           "share electric only", "share with a tilting unit"],
    "la_ip_strategy": ["firm", "unique aircraft", "patents", "patents per aircraft", "median family size", "median claims",
                       "main office", "mean forward citations", "median cohort citation rank",
                       "self-citation share (in corpus)", "region"],
    "la_ip_by_class": ["class", "patents", "median claims", "US share", "mean forward citations",
                       "median forward citations", "median cohort citation rank", "median family size",
                       "median priority year"],
    "la_ari_timeline": ["company", "ARI score", "first patent", "peak filing year", "last patent", "unique aircraft",
                        "first flight (ARI)", "entry into service (ARI)", "years to first flight",
                        "years to entry into service", "regulator (ARI)", "region"],
    "la_ari_clock_region": ["grouped by", "group", "firms", "median first flight",
                            "median years, first patent to first flight",
                            "median years, first patent to entry into service", "firms listed"],
    "la_ari_gap": ["variable", "test", "index firms", "rest of the corpus", "p", "q (BH)",
                   "p, US patents only", "holds?"],
    "la_ari_correlation": ["x", "y", "n firms", "Spearman rho", "p", "q (BH)", "holds?"],
    "la_proximity_region": ["region pair", "within a region?", "pairs", "mean", "median", "lowest", "highest"],
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
                "**The two levels this section reads (ruled 2026-09-23).** Two levels clear the four "
                "screens, A1t and A0c, and both are carried through the whole test. **A1t is the "
                "design species**: the criterion of Preliminary Analysis 5.7 is written at A1t and "
                "table 5.1 fixes it there, its three dimensions are direct codebook answers with no "
                "binning choice for a reader to attack, and it concentrates the corpus enough for a "
                "share to carry meaning — its largest archetype is the same one in the three most "
                "recent windows, with a rising share. **A0c is reported beside it at every step, and "
                "not as a check on it.** It is the level at which condition 2 fires at all, so the "
                "only balance signal the test finds anywhere is an A0c signal and would be invisible "
                "without it; it splits the corpus by the number of propulsive units, which is the "
                "dimension the eVTOL taxonomy turns on; it leaves almost no aircraft alone in its own "
                "archetype; and it is the level on which 4.1.8, 4.1.9 and 4.3.3 are built, so it is "
                "already load-bearing for the rest of this chapter. Every condition below is stated "
                "at both levels, and where the two disagree the section says so rather than choosing "
                "for the reader.")),
    dict(id="4.1.3.2", title="The conditions, fixed in advance", tables=["la_dd_conditions"]),
    dict(id="4.1.3.3", title="The result", figures=["dominant_design", "dominant_design_q"],
         tables=["la_dd_result", "la_dominant_design", "la_dd_q"]),
    dict(id="4.1.4", title="Within-class convergence", figures=["class_configs"], tables=["la_class_configs"]),
    dict(id="4.1.5", title="Dimension drift inside the classes", figures=["dimension_drift"], tables=["la_dimension_drift"]),
    # 2026-09-23, author's ruling: Table 4.1.6 is cut ("basically the same thing as the figure"), and
    # the figure is now one longitudinal bar with the percentage per window instead of twelve panels.
    # la_tables still builds la_class_cycles, so the CSV keeps every number the table printed; putting
    # the name back in ``tables`` here is all it takes to print it again.
    dict(id="4.1.6", title="Where each class lives in time", figures=["class_cycles"]),
    dict(id="4.1.7", title="Lead and lag by region and by class", figures=["lead_lag"],
         tables=["la_lead_lag_region", "la_lead_lag_class", "la_class_region_timing"]),
    dict(id="4.1.8", title="Diversity per window", figures=["hill"], tables=["la_hill_by_window"]),
    # 2026-09-23: 4.1.9 gains the filer-weight figure and table. They answer the author's question
    # of the same day — how much of a class is one company repeating itself — which Table 4.1.9a
    # cannot, because a count of distinct filers says how many there are and not how unevenly they
    # divide the class. Placement: this section reads better straight after 4.1.5 (see the report of
    # 2026-09-23); the move is a reorder of these dicts plus the ids, left for one pass.
    dict(id="4.1.9", title="Crowded and open zones of the design space, and the weight of each filer",
         figures=["zones", "filer_weight"], tables=["la_zones", "la_class_filer_weight"]),
    dict(id="4.1.10", title="Abandonment: patents no longer in force", figures=["abandonment"],
         tables=["la_abandonment_by_class"]),
    dict(id="4.2", title="Who designs it, and how they compete", level="firm"),
    # 4.2.1: the tier table (la_firm_tiers) was removed on the author's ruling of 2026-09-23 — the
    # curve now prints the firms and the aircraft of each segment, so the table only repeated it.
    # It is still built into tables/la_firm_tiers.csv; put the name back here to print it again.
    # The table that took its place answers the question the author says is the important one at
    # this section: does market standing track patenting.
    dict(id="4.2.1", title="Coverage, and whether market standing tracks patenting",
         figures=["coverage"], tables=["la_market_vs_patents"]),
    dict(id="4.2.2", title="The body of filers over time, and what new firms enter with",
         figures=["filers_over_time"], tables=["la_filers_by_window", "la_cohort_mix"]),
    dict(id="4.2.3", title="Who filed, and which firms can move the reading",
         figures=["atlas_filers", "firm_influence"],
         tables=["la_filer_mix", "a2_d8_concentration", "la_firm_leverage"]),
    dict(id="4.2.4", title="Within-firm successions", figures=["transitions"],
         after=("*How to read this section.* A **succession** is one firm's aircraft and the next "
                "aircraft the same firm filed, ordered by priority year. A firm holding k aircraft "
                "makes k − 1 successions, so the unit of Figure 4.2.4 is the pair — not the "
                "aircraft, not the patent, and the count of pairs is therefore smaller than the "
                "count of aircraft. The pairs come from the named firms that hold two or more "
                "aircraft, the same firms as the “2 aircraft or more” segment of Figure 4.2.1; a "
                "firm with a single aircraft makes no pair and is absent by construction, which is "
                "why the firm count under this figure is lower than the one under Figure 4.2.1. "
                "“Stays in class” counts the pairs whose two aircraft carry the same G1 class, and "
                "the share over every class together is the dashed line in panel (ii). "
                "*Why it is worth a section.* Section 4.1 shows the class mix of the corpus moving, "
                "and that movement has two causes which the aircraft counts alone cannot separate: "
                "the firms already filing change course, or different firms arrive. Panel (ii) here "
                "measures the first and Figure 4.2.2 (ii) the second. A class whose bar sits above "
                "the dashed line holds on to its firms, so a fall in its share is firms arriving "
                "elsewhere rather than firms leaving it; a class far below the line is one the firms "
                "themselves pass through, and the label on the bar names where they go next.")),
    dict(id="4.2.5", title="IP strategy: depth, breadth, claims and citations", figures=["ip_strategy", "spans_by_firm"],
         tables=["la_ip_strategy", "la_ip_by_class"]),
    # 2026-09-23, author's ruling: the per-firm proximity table (a2_d14_firm_proximity, printed here as
    # Table 4.2.6a) is cut — "take that out, it is not necessary, it is already all that I need in the heat
    # map". The figure now groups the firms by region, which is what the table's ordering was for. The
    # table is still built by the Preliminary Analysis and still written to tables/; only this node drops
    # it. To bring it back, put "a2_d14_firm_proximity" first in ``tables`` again.
    dict(id="4.2.6", title="Technological proximity between firms, and region", figures=["proximity_region"],
         tables=["la_proximity_region"]),
    # 2026-09-23, author's review: "if we introduce ARI score we need to explain it really well" and "I need
    # to know how the Spearman rho is calculated and why it is important, and why am I doing that only for
    # the ARI index and not for AAM too". Both are answered here, once, before any figure. This is the
    # node's ``text`` (printed under the heading); the ``after`` slot is left free on purpose.
    dict(id="4.2.7", title="The AAM Reality Index firms: score, funding, and the patent clock against the market clock",
         level="the firm, and its unique aircraft in this corpus",
         text=("**ARI and AAM are one index, not two.** The AAM Reality Index — AAM for Advanced Air "
               "Mobility, ARI for the index itself — is a single quarterly ranking published by SMG "
               "Consulting at aamrealityindex.com. Where this document writes ARI score and where it "
               "writes AAM Reality Index it means the same number. The one thing on that page that is "
               "*not* the index is the funding table beside it, which lists disclosed capital raised per "
               "manufacturer and is a separate quantity; both are used below and both are named.\n\n"
               "**What the index measures.** One score per aircraft manufacturer, from 0 to 10, combining "
               "the publisher's assessment of funding, team, technology readiness, certification progress "
               "and production readiness. It is an analyst's judgement about how close a company is to "
               "flying a certified aircraft commercially, published since December 2020 and re-issued every "
               "few months; a firm can be added, re-scored or dropped at any release. The stored copy is "
               "the May 2026 release plus the full score history, scraped on 2026-09-22 and kept verbatim "
               "in `assets/external/aam_reality_index/`, and every number in this section is traceable to "
               "those four files.\n\n"
               "**What it is not.** It is not a measurement, it is not audited, its weights are not "
               "published, and it covers only the manufacturers the publisher chose to list: 24 in the May 2026 "
               "release, and 43 listings in the stored history since December 2020. Eighteen of the firms "
               "the index has listed at some point file in this corpus, and 13 of those 18 are still in "
               "the May 2026 release — the other five (Airbus, Bell / Textron, Kitty Hawk, Lilium, Overair) "
               "carry their last score and no dates. Those 18 firms are a segment and are treated as one "
               "throughout: they are the commercial end of the eVTOL industry, they hold 150 of the "
               "corpus's unique aircraft, and Table 4.2.7c shows how they differ from the other 515 "
               "rather than assuming they represent them.\n\n"
               "**How the two sides were joined.** By hand, in `ari_company_map.csv`: each index OEM name "
               "was matched to the canonical company of the patent corpus, including the three cases where "
               "the names differ (Volant Aerotech is Wollant Aviation, Aerofugia is Wofei / Geely, Eve Air "
               "Mobility is Embraer / Eve). Firms the index lists but that file nothing here, and firms "
               "that file here but the index has never listed, are simply absent from this section.\n\n"
               "**Why Spearman, and why only on the index side.** Spearman's rho is Pearson's correlation "
               "computed on ranks: each column is replaced by its order, 1st, 2nd, 3rd, and the two orders "
               "are correlated. +1 means the firm ranked highest on one column is ranked highest on the "
               "other and so on down; -1 is the exact reverse; 0 is no relation between the orders. It is "
               "the right statistic here because the index score is an ordinal judgement on a 0-10 scale "
               "rather than a measured quantity, because the patent-side columns are small skewed counts "
               "in which Bell's 60 aircraft or Joby's $5.2 bn would dominate an ordinary correlation, and "
               "because 18 firms support nothing stronger than a statement about order. It is run on the "
               "index side only because that is the only side that arrives as a score: everything else in "
               "this chapter is a count or a label, and counts and labels are compared with the tests of "
               "Table 4.2.7c instead. Table 4.2.7b is nevertheless the weaker of the two — with 18 firms "
               "and dozens of pairs, nothing in it survives the correction for multiple testing, which is "
               "the honest reading and is printed in its own `holds?` column."),
         figures=["ari", "ari_history", "ari_clock"],
         tables=["la_ari_firms", "la_ari_correlation", "la_ari_gap", "la_ari_timeline", "la_ari_clock_region"]),
    dict(id="4.2.8", title="TRL-ranked firms", tables=["la_trl_placeholder"]),
    dict(id="4.3", title="Where", level="patent → unique aircraft"),
    dict(id="4.3.1", title="Region, country and publication office", figures=["atlas_region"]),
    dict(id="4.3.2", title="Region over time, six variables", figures=["region_grid", "region_grid_b"]),
    # 2026-09-23, author's ruling: Table 4.3.3 cut ("not needed, I already have the info on other
    # graphs"). The figure was rebuilt to carry the reading on its own. The builder still writes
    # tables/la_specialisation.csv, which the figure's Source line points at for the per-cell counts.
    dict(id="4.3.3", title="Regional specialisation by archetype", figures=["specialisation"]),
    # 2026-09-23, author's ruling: Table 4.3.4 cut, the figure stays.
    dict(id="4.3.4", title="Country and class", figures=["country_class"]),
    # ================================================================ 5
    dict(id="5", title="Low-level Analysis", level="unique aircraft and image"),
    # 2026-09-23, author's ruling: Table 5.1 cut ("take it off"); the figure carries the same shares.
    dict(id="5.1", title="Hybrid against electric, not-stated included", figures=["atlas_powertrain"]),
    dict(id="5.2", title="Propulsive units and their arrangement", figures=["atlas_units"]),
    dict(id="5.3", title="The design space as paired fields", figures=["atlas_design_heatmaps"]),
    dict(id="5.4", title="Image-level answers", figures=["atlas_state_by_arch"], tables=["a2_d2_figure_slot_answers"]),
    dict(id="5.5", title="Mission of the aircraft linked to evtol.news, and the industry named in the text",
         # Figure 5.5c added 2026-09-23: the section describes a subset, so the first thing it owes
         # the reader is whether that subset stands for the rest. It is placed last so that the
         # numbers of 5.5a and 5.5b do not move under the author's own review notes.
         figures=["mission", "industry_by_class", "linked_check"],
         # 2026-09-23, author's ruling: Table 5.5g (industry by class) cut — the industry field comes
         # from a text classifier he has no way of verifying, and he does not want to. Figure 5.5b
         # keeps it, with the classifier named in its Source line.
         tables=["la_class_fold", "la_mission_capacity", "la_mission_piloting", "la_mission_power source",
                 "la_mission_status", "la_mission_agreement"]),
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
    # one graph in this document: la_figures.ATLAS_DROP cuts the column dot cloud (ruling 2026-09-22)
    "atlas_fields": dict(
        unit="unique aircraft (n {unique_s}), one box per architecture class",
        base="each class's own aircraft; a class with no propulsor card is still counted, on the "
             "slots it does answer",
        transform="box plot (median, quartiles, whiskers, single aircraft beyond them) of the slots "
                  "each aircraft answers, of {questions}; no shares"),
    "a2_d2_informative_fields": dict(
        unit="label fields (n {n_informative}), profiled over unique aircraft (n {unique_s})",
        base="only the fields at least 300 aircraft answer with an effective number of answers of "
             "1.5 or more; the other coded columns are left out of the table, not of the data",
        transform="counts and shares of the aircraft that answer the field; effective answers = exp "
                  "of the Shannon entropy, the number of answers the field behaves as if it had"),
    # one graph in this document: la_figures.ATLAS_DROP cuts the class bars (ruling 2026-09-22)
    "atlas_arch_gt": dict(
        unit="unique aircraft (n {unique_s}), of which the matrix holds the 662 carrying a class on "
             "both sides — a figure label and a whole-patent reading",
        base="each row is one ground-truth class. The 3 aircraft left out are named in the table of "
             "section 3.3: one whose patent states no class, and two the wizard left unlabelled, one "
             "of them read as a convertiplane, outside the twelve classes",
        transform="share of the ground-truth row (rows sum to 100 %) with the aircraft count in the "
                  "cell; agreement and κ are over the matrix, so they are computed on the 662"),

    # ================================================================ 4.1 what is designed
    "filings_per_year": dict(
        unit="three units across the two graphs — unique aircraft (n {unique_s}) in the bars of (i), "
             "acquired patents (n {acquired_s}) in its line, and all B64 patent publications in (ii)",
        base="(i) each priority year on its own, except the first bar, which pools 1999-2005 so those "
             "years are counted somewhere; an aircraft sits in the year of its primary record. "
             "(ii) single years only, never the pooled bucket, each divided by every aeronautics (B64) "
             "patent of that priority year in the nine publication offices the corpus draws on "
             "(WIPO PATENTSCOPE, fetched 2026-09-22)",
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
        base="the aircraft of each priority window, n printed under each bar; each class is drawn on "
             "its own except SRW and DS, the only two left inside Other types",
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
        unit="unique aircraft (n {unique_s}) as archetypes — A0c = class × propulsive-unit bin, "
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
    "la_dd_q": dict(
        unit="unique aircraft (n {unique_s}) of one window, compared pairwise",
        base="the aircraft each level can name, carrying a value on the distance shortlist; windows under 10 left out",
        transform="the Gower distance imported from the Preliminary Analysis code (5.3: one unit of weight per "
                  "subsystem divided among its fields, blanks dropped from the pair, the pooled wing-borne field of "
                  "rule 4); Q = Rao's quadratic entropy over the window (5.5); the band is 200 shuffles of which "
                  "window each aircraft belongs to"),
    "la_dd_result": dict(
        unit="condition",
        base="the per-window tables that follow (conditions 1 and 2, and condition 3)",
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
        transform="median propulsive units (an order statistic, not a mean); panels (i)–(iv) are the four "
                  "fields of the 4.1.4 configuration and divide by the class's own aircraft in that window, "
                  "all of which answer them, so those four sit on one base. Panel (v), powertrain, divides "
                  "by the aircraft whose patent states one — a smaller base, named in its title, blank "
                  "under 5. No share is a share of rotors"),
    "la_dimension_drift": dict(
        unit="unique aircraft, one architecture class per row — not an archetype",
        base="the aircraft of one class in one window; windows under 5 are left out. Classes drawn by rule: "
             "5+ aircraft in 3+ of the 5 windows (SLC, TR, CVT, TW, MR)",
        transform="medians for propulsive units and wings; the ducted, tail and boom shares divide by the "
                  "aircraft of that class-window (all of them answer those fields), the powertrain share by "
                  "the `powertrain stated` column beside it. Never by a count of rotors. The tilting column "
                  "is reported but not drawn: flat by definition of the classes"),
    "class_cycles": dict(
        unit="unique aircraft (n {unique_s}), one bar per architecture class",
        base="each class's own total — the bar, never the window",
        transform="share of the class's own total per window, printed in each block, so every bar sums "
                  "to 100 %. This deliberately divides out the growth of the corpus: it says when a "
                  "class lived and says nothing about how big the class is. The outlined block is the "
                  "class's median window; the last column is the 95 % Wilson half-width on that class's "
                  "largest percentage, which is how far it could sit from the truth on that many "
                  "aircraft. No raw count is printed on the figure (author's ruling 2026-09-23); they "
                  "are all in tables/la_class_cycles.csv"),
    "la_class_cycles": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own total (the `aircraft` column)",
        transform="row shares summing to 100 % per class; the median window is the window in which "
                  "the class passes half its own aircraft"),
    "lead_lag": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="panel (i) each group's own aircraft — the region's, or the class's; panel (ii) the "
             "aircraft of one class inside one region, and a cell under 5 of them is left unread",
        transform="panel (i) the year each group's cumulative share of its own total crosses 25, 50 and "
                  "75 %, drawn as a bar with the median marked, so the axis is timing and never volume; "
                  "panel (ii) the median priority year of each class inside each region, with the "
                  "region's own median over all classes on the bottom row as the line a cell is read "
                  "against. NOT normalised against B64 aviation patenting: every group is already "
                  "divided by its own total, and the stored baseline is one series for all offices, so "
                  "it would apply the same yearly factor to every group — a check weighting each "
                  "aircraft by 1 / B64 of its year moves every crossing about two years earlier and "
                  "leaves the order of the regions unchanged"),
    "la_class_region_timing": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023), the seven "
             "largest classes against the three regions",
        base="the aircraft of one class inside one region (the `(n)` column beside each region); a "
             "cell under 5 aircraft is printed “–” rather than read",
        transform="the median priority year of each cell — an order statistic, so one very early or "
                  "very late filing cannot move it; the column reads a region's own lateness, the row "
                  "reads whether one region took a class up before the others"),
    "la_lead_lag_region": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="each region's own aircraft (the `aircraft` column)",
        transform="the year each region's cumulative share crosses 25, 50 and 75 % of its own total"),
    "la_lead_lag_class": dict(
        unit="unique aircraft (n {unique_s}) of complete priority years only (to 2023)",
        base="each class's own aircraft, seven largest classes",
        transform="the year each class's cumulative share crosses 25, 50 and 75 % of its own total"),
    "hill": dict(
        unit="unique aircraft (n {unique_s}), labelled at A0 (class) and A0c (class × propulsive-unit bin)",
        base="the aircraft of each window, cut to a common sample of 40 so the windows are "
             "comparable; a window under 10 aircraft is left out",
        transform="rarefied Hill numbers ⁰D, ¹D and ²D — printed on the figure as the question each "
                  "answers: how many kinds exist at all (⁰D), how many are commonly used (¹D, the "
                  "exponential of the Shannon entropy) and how many are the usual choice (²D, the "
                  "inverse Simpson index, the one a dominant design pulls towards 1). Each point is the "
                  "mean of 1 000 draws of 40 aircraft and the whisker is the 2.5th-to-97.5th percentile "
                  "of those draws; cutting every window to 40 is what removes the effect of a window "
                  "simply holding more patents than another"),
    "la_hill_by_window": dict(
        unit="unique aircraft (n {unique_s}) at A0 and A0c",
        base="the aircraft of each window, rarefied to 40; windows under 10 are left out",
        transform="mean of 1 000 draws of 40 aircraft with the 2.5th and 97.5th percentiles as the band"),
    "zones": dict(
        unit="A0c archetypes (class × propulsive-unit bin) with five or more aircraft (n {n_zones}); "
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
    "filer_weight": dict(
        unit="unique aircraft (n {unique_s}), attributed to a filer — a named firm is one filer, an "
             "individual or unattributed patent is its own filer, so no two lone inventors are merged "
             "and a firm with four patents on one aircraft counts once",
        base="panel (i) each class's own aircraft; panel (ii) the aircraft of one class in one window, "
             "and a cell under 10 of them is left blank because a share on four aircraft says nothing",
        transform="the share of the class (or of the class-window) held by its largest filer, and by "
                  "its three largest together. This is a concentration reading, not a count: Table "
                  "4.1.9a's `filers` column says how many filers an archetype has and cannot say how "
                  "unevenly they divide it, which is the question this figure answers"),
    "la_class_filer_weight": dict(
        unit="unique aircraft (n {unique_s}) per architecture class, and the filers holding them",
        base="each class's own aircraft for the share columns; the whole analysis set for the last "
             "three, which are the class's share of the corpus counted two ways",
        transform="`its share` and `top 3 share` divide the largest filer's (or largest three filers') "
                  "aircraft by the class's; `effective filers` is 1 / Σ(share²) over filers, the number "
                  "of equally sized filers that would give the same concentration; `share one vote per "
                  "filer` re-counts the corpus with each filer casting a single vote for the class it "
                  "filed most, and `repetition factor` is the aircraft share divided by that vote share"),
    "abandonment": dict(
        unit="the PRIMARY patent of a unique aircraft, one row per patent and not per aircraft, with "
             "priority year 2019 or earlier (of the {primary_s}) so every one of them was filed early "
             "enough to have been granted and then kept or dropped",
        base="the patents of each class, of that same cohort — never the class's aircraft over all "
             "years, which would mostly measure how young the class is",
        transform="share of the class's patents whose stored PatSeer `legal_status_raw` begins "
                  "INACTIVE at the snapshot, with the raw patent count beside it. INACTIVE covers "
                  "WITHDRAWN / SURRENDERED, NONPAYMENT, EXPIRED and REJECTED / REFUSED / SUSPENDED, so "
                  "it pools the applicant's own decisions with the office's; the four are separated in "
                  "tables/la_examination_class.csv. A patent-level fact, not an aircraft-level one"),
    "la_abandonment_by_class": dict(
        unit="the primary patent of a unique aircraft, priority year 2019 or earlier (of the "
             "{primary_s}), one row per patent",
        base="the patents of each class of that cohort; the last row is all classes together",
        transform="lapsed share = patents whose stored PatSeer `legal_status_raw` begins INACTIVE at "
                  "the snapshot ÷ the class's patents, raw counts beside it; granted share is the same "
                  "denominator against statuses containing GRANTED, so the two shares need not sum to "
                  "1 (a patent can be inactive and never have been granted)"),

    # ================================================================ 4.2 who designs it
    "coverage": dict(
        unit="(i) named companies ranked by unique aircraft, against the analysis set (n {unique_s}); "
             "(ii) and (iii) the named firm, one per bar group or dot",
        base="(i) the whole analysis set: every share is taken on {unique_s} aircraft, not on the "
             "corporate subset. (ii) the named firms split in two by one flag — listed on the AAM "
             "Reality Index in any release, or not listed. (iii) only the firms the index rates",
        transform="(i) cumulative share of the analysis set covered by the top N firms, with the "
                  "ranking cut into four disjoint segments whose firms and aircraft are printed and "
                  "do add up; the dashed line is the share held by all named companies together. "
                  "(ii) the median of each group, with a two-sided Mann-Whitney U between them — a "
                  "difference in rank, not a model, and every n is printed. (iii) raw score against "
                  "raw aircraft count on a log axis, with the Spearman rho over the rated firms. "
                  "Index membership is not random: a firm is on the index because it has a vehicle "
                  "programme the market follows, so the comparison describes rated against unrated "
                  "filers and is not evidence that rating causes patenting"),
    "la_market_vs_patents": dict(
        unit="named firms — {named_companies} of them, split by whether the AAM Reality Index rates "
             "the firm (in the May 2026 release or any earlier one)",
        base="the two groups of firms; the first row is instead the unique aircraft each group holds, "
             "on the whole analysis set (n {unique_s})",
        transform="medians per firm with a two-sided Mann-Whitney U between the groups, and, in the "
                  "last rows, Spearman rho taken inside the index alone. Descriptive: n is small, "
                  "every n is printed, no correction is made for multiple comparisons, and index "
                  "membership is a market judgement about vehicle programmes, not a random sample"),
    "la_coverage_segments": dict(
        unit="named companies grouped by how many unique aircraft each holds",
        base="the whole analysis set (n {unique_s})",
        transform="raw counts per disjoint segment — unlike the nested tiers of la_firm_tiers, these "
                  "rows do add up to the {named_companies} named companies and their aircraft"),
    "la_firm_tiers": dict(
        unit="named companies, and the unique aircraft they hold (analysis set n {unique_s})",
        base="two different denominators in two columns — the whole analysis set, and the "
             "named-company aircraft only",
        transform="raw counts of firms and aircraft per threshold; the thresholds are nested, so the "
                  "rows are cumulative and must not be added"),
    "filers_over_time": dict(
        unit="(i) named firms (companies and institutes) per window; (ii) two units side by side — "
             "the left bar is firms (each entrant counted once, in the window of its first filing) "
             "and the right bar is the unique aircraft of the same window (analysis set n {unique_s})",
        base="(i) the firms active in each window. (ii) each bar is its own 100 % — the entrants of "
             "the window, and the aircraft of the window",
        transform="(i) raw counts of firms; entries are firms whose first filing is in the window, and "
                  "the bars below zero are firms whose last filing is in it. An exit can only be "
                  "counted where a later window exists in which the firm could have filed and a "
                  "filing of that window could already have published — the 90th-percentile "
                  "priority-to-publication lag is {lag_p90} years, so a firm that filed in 2024 or "
                  "later may not be visible at the snapshot and the last two windows are left blank "
                  "rather than counted as zero. (ii) shares, so a taller band is a larger "
                  "part of the mix and never a larger count; the class of an entrant is the class of "
                  "its first aircraft"),
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
    "firm_influence": dict(
        unit="(i) named firms holding three or more unique aircraft, one bar each; (ii) the "
             "architecture class, one pair of bars each (classes with nine or more aircraft)",
        base="(i) the whole analysis set (n {unique_s}), re-counted once per firm with that firm's "
             "aircraft taken out. (ii) each class's own aircraft",
        transform="(i) a leave-one-firm-out difference: the class shares of the analysis set minus the "
                  "class shares of the set without that firm, reported as the largest single class "
                  "share that moves, in percentage points. (ii) plain shares of the class held by its "
                  "largest filer and by its three largest — the individual and unattributed filings "
                  "of the class are in the denominator, so the bars do not reach 100 %"),
    "la_firm_leverage": dict(
        unit="named firms holding three or more unique aircraft",
        base="the whole analysis set (n {unique_s}) for the first shift column; the aircraft of one "
             "window for the second",
        transform="leave-one-firm-out differences in percentage points, taken on the class shares; a "
                  "positive sign means dropping the firm raises that class's share. The per-window "
                  "column is the worst case over the four complete windows and names the window it "
                  "comes from; windows with fewer than 30 aircraft are skipped"),
    "la_class_concentration": dict(
        unit="architecture classes, all twelve",
        base="each class's own unique aircraft",
        transform="raw counts of the named firms filing in the class, and the share of the class held "
                  "by its largest filer and by its three largest; the last column is the share held "
                  "by named firms at all, the rest being individual and unattributed filings"),
    "la_cohort_mix": dict(
        unit="two units in the same row — the named firms entering a window (each counted once, in "
             "the window of its first filing) and the unique aircraft of the same window",
        base="two denominators, one per share: the entrants of the window, and the aircraft of the "
             "window (analysis set n {unique_s})",
        transform="shares of each denominator and their difference in percentage points. Only the "
                  "rows where a class holds a tenth of the entrants or a tenth of the aircraft are "
                  "printed; every row is in tables/la_cohort_mix.csv"),
    "la_filer_mix": dict(
        unit="two units in the same row — primary patents (n {primary_s}) and unique aircraft "
             "(n {unique_s}), by filer type",
        base="all the primary patents in one share column, all the analysis set in the other, so the "
             "two are the same population counted twice",
        transform="raw counts and the share on each denominator; the last column divides the two — "
                  "aircraft per patent, which is above 1 where one patent carries more than one "
                  "aircraft. The distinct-filer count exists only for the named rows: individual and "
                  "unattributed filings are not resolved to a person"),
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
        unit="consecutive pairs of aircraft filed by the same named firm, ordered by priority year — "
             "not aircraft and not patents. A firm holding k aircraft contributes k − 1 pairs, so "
             "only the named firms with two or more aircraft appear and the firms with one are "
             "absent by construction",
        base="the class of the earlier aircraft of the pair: each row of (i) and each bar of (ii) is "
             "taken on that class's own pairs",
        transform="(i) raw pair counts in the cell, coloured as the share of the earlier class's row, "
                  "so the rows sum to 100 % and the diagonal is a firm repeating its class. (ii) the "
                  "diagonal alone as a share, for the classes with five or more pairs, with the class "
                  "most of the leavers go to; the dashed line is the same share over every pair"),
    "la_transitions": dict(
        unit="consecutive pairs of aircraft filed by the same named firm",
        base="all such pairs over the named firms",
        transform="raw counts per (from, to) pair; no shares"),
    "ip_strategy": dict(
        unit="(i) named firms with five or more unique aircraft (n {n_firms5}); (ii) and (iii) primary "
             "patents (n {primary_s}) grouped by class",
        base="(i) each firm's own representative patents and its unique aircraft; (ii) and (iii) the "
             "patents of each class holding 10 or more",
        transform="(i) patents per aircraft against unique aircraft, x on a log scale; the BUBBLE AREA is "
                  "the firm's mean forward citations and the panel carries its own size key. (ii) median "
                  "claims per class, with the share of the class's patents published in the United States "
                  "printed beside each bar, because claim counts are an office convention (corpus median "
                  "20 claims at the USPTO against 10 at the CNIPA). (iii) the same classes on the median "
                  "cohort citation rank — each patent ranked against every corpus patent of its own "
                  "priority year, so age is taken out — with the raw mean printed beside it for comparison"),
    "la_ip_strategy": dict(
        unit="named firms with five or more unique aircraft (n {n_firms5})",
        base="each firm's own representative patents (primary plus the O1/O2 re-filings); the cohort "
             "citation rank is taken against all 1 639 acquired patents of the same priority year, not "
             "against the firm's own",
        transform="ratios and order statistics — patents per aircraft, median family size, median claims, "
                  "mean forward citations (raw, not age-normalised, and the bubble size of Figure 4.2.5a) "
                  "and the median cohort citation rank, which is age-normalised and is the column to "
                  "compare firms on"),
    "la_ip_by_class": dict(
        unit="primary patents (n {primary_s})",
        base="the patents of each class; the cohort citation rank is taken against all 1 639 acquired "
             "patents of the same priority year",
        transform="medians per class, plus one mean (forward citations) kept because the citation "
                  "distribution is skewed and the mean and the median say different things. The raw "
                  "citation columns accumulate with age — over the corpus they fall with the priority year "
                  "at Spearman rho -0.53 — so the median priority year is printed beside them and the "
                  "age-normalised median cohort citation rank (rho -0.02) is the one to rank classes on. "
                  "`US share` is a share of the class's own patents"),
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
                  "(no class in common) and 1 (identical mix), never a share or a distance in any unit. "
                  "The firms are ordered in region blocks (user ruling 2026-09-23) and clustered inside "
                  "each block, so the boxed square on the diagonal of a block is that region against "
                  "itself; the region labels and the blocks are a re-ordering only and change no value"),
    "a2_d14_firm_proximity": dict(
        unit="named firms with five or more unique aircraft (n {n_prox_firms})",
        base="each firm's own aircraft, spread over the classes",
        transform="Jaffe (1986) uncentred cosine, computed twice — on the class alone, and on the "
                  "class crossed with the propulsive-unit count bin"),
    "la_proximity_region": dict(
        unit="pairs of firms (over the {n_prox_firms} firms with five or more aircraft)",
        base="every firm pair, put in one box by the two regions it joins; the six boxes are the six "
             "region pairs and together they hold all the pairs exactly once",
        transform="mean, median and range of the proximities in each box; the pair count is printed "
                  "because the boxes are very different sizes (6 pairs to 42). The permutation test of "
                  "same-region against different-region proximity is printed in the Source line of "
                  "Figure 4.2.6, on 10 000 shuffles of the region labels over the firms"),
    "ari": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="the index side is the index's own release; the patent side is this corpus's aircraft of "
             "the same firm",
        transform="raw index scores, disclosed funding and raw corpus counts — nothing is normalised; "
                  "with n = {n_ari} firms this is descriptive only"),
    "ari_history": dict(
        unit="(i) AAM Reality Index firms that also file in the corpus (n {n_ari}); (ii) only the nine of "
             "them that publish a funding figure — a segment of a segment, declared on the panel",
        base="(i) each firm's first and last score in the index history, whichever releases those are; "
             "(ii) each disclosing firm once, its disclosed funding against its unique aircraft here",
        transform="raw scores and raw counts, nothing normalised and no trend fitted; (ii) has a log "
                  "funding axis, so equal steps up the axis are ten times the money, and its horizontal "
                  "axis runs from 1 to 8 single aircraft"),
    "ari_clock": dict(
        unit="the 13 index firms listed in the May 2026 release that also file in the corpus — the five "
             "firms the index has dropped carry no dates and are not drawn",
        base="each firm's own first, peak and last priority year in the corpus, against the dates the "
             "index states in `assets/external/aam_reality_index/ari_may2026.csv`",
        transform="raw years, no shares; the two clocks come from different sources and are only set side "
                  "by side. An entry into service is what the index reports as planned, not an event"),
    "la_ari_firms": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari})",
        base="each firm's own aircraft in the corpus, beside its index entry",
        transform="raw counts and the index's own score and funding; nothing is normalised"),
    "la_ari_correlation": dict(
        unit="AAM Reality Index firms that also file in the corpus (n {n_ari}); n per row is printed "
             "because funding and the two market dates are stated for only some of them",
        base="the firms for which both sides of the pair have a value",
        transform="Spearman rank correlation — Pearson's correlation on the ranks, so the size of a value "
                  "never enters, only its order. Descriptive at this n: `q` is the Benjamini-Hochberg "
                  "adjustment of `p` over every row of the table, and no row is read as a finding without "
                  "it"),
    "la_ari_gap": dict(
        unit="unique aircraft (n {unique_s}), split in two — the 150 held by the AAM Reality Index firms "
             "against the 515 held by everyone else",
        base="for a number, the aircraft that carry a value on that variable; for a category, the whole "
             "split. The `p, US patents only` column re-runs each test on the US-published patents alone",
        transform="one distribution-free test per row — Mann-Whitney U for a number, Fisher exact for a "
                  "yes/no field, chi-square for a category — with `q` the Benjamini-Hochberg adjustment "
                  "over the whole table. The printed values are medians for a number and shares for a "
                  "yes/no field, never means. This is a comparison of two groups, not a correlation "
                  "coefficient, and it carries no causal claim: the index firms are also the best-funded "
                  "and the most US-published in the corpus"),
    "la_ari_timeline": dict(
        unit="the 13 index firms listed in the May 2026 release that also file in the corpus",
        base="each firm's own priority years in the corpus, beside the index's stated dates",
        transform="raw years, no shares; the two gap columns are subtractions from the firm's earliest "
                  "priority year in this corpus, which is left-truncated at the first eVTOL patent the "
                  "labelling reached, so a negative value means the firm flew before it enters this "
                  "corpus and every gap is a floor"),
    "la_ari_clock_region": dict(
        unit="the 12 index firms with a stated first flight, grouped twice — by certifying authority and "
             "by the applicant region of their patents",
        base="each group's own firms; the firm count and the firm names are printed on every row because "
             "no group holds more than five",
        transform="medians of the columns of Table 4.2.7d; no test is run and none would be supportable "
                  "at this n, so the table ranks jurisdictions rather than measuring them"),
    "la_trl_placeholder": dict(
        unit="no data yet — the TRL work is not installed",
        base="nothing is computed",
        transform="none"),

    # ================================================================ 4.3 where
    "atlas_region": dict(
        unit="(i) patents — acquired (n {acquired_s}) and representative (n {representative_s}) of "
             "each applicant country, the twelve largest; (ii) unique aircraft (n {unique_s})",
        base="(i) each country's own patents, and the whole representative set for the share; "
             "(ii) each region's own aircraft, n printed on the row",
        transform="(i) raw counts, then two percentages: how much of that country's own filing "
                  "survived, and — the one that answers representativeness — how much of the whole "
                  "analysis set the country holds. Country codes are spelled out; (ii) share of the "
                  "region, each row 100 %"),
    "region_grid": dict(
        unit="unique aircraft (n {unique_s}); rows (i)–(iii) use the three main applicant regions "
             "only, and the bottom row divides by every aircraft of the window, 'Other regions' "
             "included",
        base="(i)–(iii) each region × window cell on its own; (iv) the whole window",
        transform="(i)–(iii) share of the cell, each region × window row summing to 100 %; (iv) the "
                  "region's share of the window, against the dashed line of its share of the whole "
                  "corpus. Region is the applicant's region, not the publication office. NOT "
                  "normalised against the general rise in patenting — the stored B64 baseline has no "
                  "regional split, so the mix rows cancel the rise only because they are shares "
                  "inside one cell, and the bottom row is relative to the other regions, not "
                  "absolute; Figure 4.1.1 carries the corpus-wide normalisation. A cell under 10 "
                  "aircraft is blanked in the mix rows and drawn hollow with its n in the bottom row"),
    "region_grid_b": dict(
        unit="unique aircraft (n {unique_s}); the three main applicant regions in rows (i)–(iii), "
             "every region in the bottom row",
        base="(i)–(iii) each region × window cell on its own; (iv) the whole window",
        transform="shares as in Figure 4.3.2a, with the same n < 10 guard and the same absence of any "
                  "B64 normalisation. Filer type comes from company_canonical (grouper.py: first "
                  "assignee, exact then fuzzy ≥ 85 against a hand-written list of ~110 companies; "
                  "unmatched 2–5-word strings become individual inventors, everything else "
                  "'unattributed'), split into company and university by a regex over the canonical "
                  "name. Audited 2026-09-23 against the raw assignee strings: person against "
                  "organisation right 98 %, the three-way split 75 %. The band drawn 'assignee not in "
                  "the list' is the stored category 'unattributed / independent' and is not "
                  "unattributed — all of its aircraft name an assignee, most of them a company the "
                  "list does not hold — so it measures the list's coverage, not independent filing"),
    "specialisation": dict(
        unit="A0c archetypes with five or more aircraft (n {n_special}), over the three main regions",
        base="the archetype's share inside one region, divided by its share over all three regions "
             "together",
        transform="location quotient — 1 = the same share as everywhere, 2 = twice it. It is a ratio, "
                  "not a share, and it is already normalised for how much each region files, so a big "
                  "region cannot score high merely by being big. One dot per region, rows grouped by "
                  "the region that leads them; an archetype of fewer than 10 aircraft is drawn hollow "
                  "because at that size the index moves a full point on chance alone"),
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
        transform="(top) one dot per aircraft, the bar spanning the middle half of the class (25th to "
                  "75th percentile) and the ring the median, units capped at 30 for the drawing only. "
                  "Quartiles and a median rather than a mean because the count is a whole number with "
                  "a long tail, so a mean falls between two real machines and names none of them; the "
                  "figure's own How-to-read line prints the corpus mean, median and longest count as "
                  "they stand at render time; (bottom) share of that readable base carrying the "
                  "feature"),
    "atlas_design_heatmaps": dict(
        unit="unique aircraft (n {unique_s})",
        base="each class's own aircraft — every row of every panel sums to 100 % of its class",
        transform="share of the class; a value an override hides is shown as 'not determinable' "
                  "rather than blank, and the answers outside the seven most common are pooled as "
                  "'other'. Every class is drawn, the small ones included: Pitch-to-Cruise and "
                  "Hoverbike answer several of these panels almost trivially (a hoverbike has no "
                  "wing, no tail and no boom), so their rows carry no information on those panels and "
                  "the author has said he will drop them in the thesis; they are kept here so the "
                  "denominators of the figure and of the corpus are the same"),
    "atlas_state_by_arch": dict(
        unit="whole-aircraft figures (n {figures_approved_s}) — an image-level item, not an "
             "aircraft-level one, so an aircraft with many figures weighs more",
        base="each architecture's own approved figures, n printed on the row",
        transform="share of the row; the number under each column name is that flight state's figure "
                  "total across all classes. This is a labelling-process fact, not a design fact: it "
                  "says which configuration the draughtsman chose to draw, which is why it sits at the "
                  "end of the document and not beside the architecture figures"),
    "a2_d2_figure_slot_answers": dict(
        unit="the {figures_approved_s} approved whole-aircraft figures of the representative patents "
             "— the analysis image set, not every figure on file. Figures rejected at labelling and "
             "approved detail figures (a tilt mechanism, a rotor hub) are both out, so the counts are "
             "the answers of the images this document actually reads",
        base="per slot, the figures that answer it",
        transform="raw counts of the four most common answers; the flight-state row lists every state "
                  "of the codebook, zeros included"),
    "mission": dict(
        unit="the unique aircraft linked to an evtol.news page — a subset of the {unique_s}, never "
             "the whole analysis set",
        base="each folded class's own linked aircraft, n printed on the bar",
        transform="(i)–(iv) share of the folded class, each bar 100 %; the bottom panel is the share "
                  "of the patent-class row with the aircraft count in the cell. The mission fields are "
                  "parsed from the directory page text, not from the patent, and not by any model: "
                  "each one is a keyword rule over one field of the page (capacity from the first "
                  "number before 'passenger / seat / pax', piloting from 'autonomous / remote / "
                  "unmanned' against 'pilot / manned', power from 'hydrogen / fuel cell', 'hybrid', "
                  "'batter / electric', status from the words in the page's own status line), with "
                  "'not stated' kept as an answer. The link itself is the reviewed patent_links.csv: "
                  "candidates found by aircraft name plus company against the directory index, plus "
                  "the URLs the author pasted into NAME_DECISIONS.csv, every row checked by hand. "
                  "Whether these aircraft stand for the whole analysis set is tested in Figure 5.5c, "
                  "and the short answer is that their class mix and their geography do carry back "
                  "while their filer mix, their dates and the size of their aircraft do not"),
    "linked_check": dict(
        unit="all {unique_s} unique aircraft, split into the ones linked to an evtol.news page and "
             "the ones with no page — the test behind every other item of 5.5",
        base="each side's own aircraft: a share is of the linked set or of the rest, never of the "
             "two together",
        transform="share per level, with a chi-square over the whole attribute (categorical) or a "
                  "Mann-Whitney over the two medians (priority year, propulsive units); p ≥ 0.05 is "
                  "printed as 'same mix'. The link is not a random draw — an aircraft can be linked "
                  "only when the labelling gave it a real name and the directory carries that name — "
                  "so this figure states the bias rather than removing it"),
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


# --------------------------------------------------------------------------
# takeaway — the second grey line under every figure and every table
# --------------------------------------------------------------------------
# User ruling 2026-09-23 (review round 2, cross-cutting instruction 2): "create under each
# table the outcome — the takeaway that I take from those graphs". Over and over in that
# review: "I don't know what to take from this". So every item prints a second grey line
# under the provenance line:
#
#     Takeaway: <what the reader should conclude, with the number that supports it>
#
# The rules this register is written to, and that any new entry must keep:
#
# 1. A FINDING, NOT A DESCRIPTION. "shows class share per window" is not a takeaway;
#    "Lift + Cruise overtakes Tilt Rotor in 2020-23 and holds the lead" is.
# 2. ONE OR TWO SENTENCES. It is read in one glance, under a figure, at 7 pt.
# 3. EVERY NUMBER IS A PLACEHOLDER. ``{unique_s}`` and the rest resolve against
#    ``numbers.live`` exactly as the provenance line does; a number that comes out of a
#    built table is declared in :data:`TAKEAWAY_NUMBERS` and resolved at render time. A
#    typed number goes stale the first time the corpus changes and is never used here.
# 4. AN HONEST NEGATIVE IS A TAKEAWAY. Where the item does not support a conclusion, the
#    line says so — that is the answer to "what do I take from this", not a failure.
# 5. NEVER REPEAT THE HOW-TO-READ LINE baked into the figure. That says how to read the
#    graph; this says what it means.
# 6. WHAT IS NOT WRITTEN IS VISIBLE. An item with no entry, or with the :data:`NOT_YET`
#    sentinel, prints "takeaway not written yet" rather than an invented sentence.
#
# Keyed by the internal figure or table name, never by the printed number, so the line
# survives a renumbering. ONE ENTRY PER KEY — a repeated key is not an error in Python:
# the last one silently wins and the first is lost. Search for the name before adding.

#: printed where a defensible takeaway needs an analysis that has not been done
NOT_YET = "takeaway not written yet"

#: Numbers a takeaway needs that are not in ``numbers.live``, read out of the built tables
#: at render time. ``{key}`` in a takeaway -> the spec here -> the value. A spec that cannot
#: be resolved (table not built, column renamed, row gone) drops its placeholder instead of
#: printing it, exactly as the provenance register does, so a takeaway degrades to a
#: sentence with an ellipsis and never to a wrong number.
#:
#: Spec keys: ``table`` (required), ``how`` (see below), ``where`` (one (column, value) pair
#: or a list of them — matched on the printed string), ``col`` (the column read), ``out``
#: (the column returned by max/min, default ``col``), ``over`` (the denominator's filter for
#: ``share``, default: no filter), ``at_least`` (the threshold of ``count_ge``), ``fmt``.
#: ``how``: ``value`` (default, first matching row) · ``rows`` (row count) · ``count``
#: (matching rows) · ``count_ge`` (rows whose ``col`` is >= ``at_least``) · ``sum`` · ``max``
#: · ``min`` · ``share`` (sum of ``col`` over ``where`` / sum over ``over``).
#: ``fmt``: ``raw`` (default) · ``int`` · ``pct`` (0.424 -> "42 %") · ``1f`` · ``2f``.
TAKEAWAY_NUMBERS: Dict[str, Dict] = {
    "tk_flags_n": dict(table="la_flags", how="rows", fmt="int"),
    # ---------------------------------------------------------------- chapter 1
    "tk_one_aircraft": dict(table="a2_d7_aircraft_per_patent",
                            where=("aircraft drawn in the patent", "1"), col="patents", fmt="int"),
    # ---------------------------------------------------------------- chapter 3
    "tk_fill_worst": dict(table="a2_d4_missingness", how="max", col="share", out="check"),
    "tk_fill_worst_sh": dict(table="a2_d4_missingness", how="max", col="share", fmt="pct"),
    "tk_fill_worst_n": dict(table="a2_d4_missingness", how="max", col="share", out="affected", fmt="int"),
    "tk_flag_types": dict(table="a2_d13_flagship_check", how="max", col="distinct types", fmt="int"),
    "tk_flag_multi": dict(table="a2_d13_flagship_check", how="count_ge", col="distinct types",
                          at_least=3, fmt="int"),
    "tk_latsym": dict(table="a2_d3_selected_fields", where=("name", "left-right symmetry"),
                      col="top_share", fmt="pct"),
    "tk_fuskin": dict(table="a2_d3_selected_fields", where=("name", "fuselage motion hover to cruise"),
                      col="top_share", fmt="pct"),
    "tk_wingconf": dict(table="a2_d3_selected_fields", where=("name", "wing configuration"),
                        col="top_share", fmt="pct"),
    "tk_emptype": dict(table="a2_d3_selected_fields", where=("name", "tail type"),
                       col="top_share", fmt="pct"),
    "tk_units_top": dict(table="a2_d3_selected_fields", where=("name", "propulsor units per aircraft"),
                         col="top_share", fmt="pct"),
    "tk_gear_unknown": dict(table="a2_d3_selected_fields", where=("name", "landing-gear type"),
                            col="top_share", fmt="pct"),
    "tk_inf_emp": dict(table="a2_d2_informative_fields", where=("name", "tail type"),
                       col="effective_answers", fmt="1f"),
    "tk_inf_top": dict(table="a2_d2_informative_fields", where=("name", "architecture type"),
                       col="effective_answers", fmt="1f"),
    "tk_gt_tr": dict(table="a4_agreement_by_type", where=("image_label", "TR"), col="recovered", fmt="pct"),
    "tk_gt_slc": dict(table="a4_agreement_by_type", where=("image_label", "SLC"), col="recovered", fmt="pct"),
    "tk_gt_ptc": dict(table="a4_agreement_by_type", where=("image_label", "PTC"), col="recovered", fmt="pct"),
    "tk_gt_hb": dict(table="a4_agreement_by_type", where=("image_label", "HB"), col="recovered", fmt="pct"),
    # ---------------------------------------------------------------- 4.1
    "tk_y2015": dict(table="la_filings_per_year", where=("priority year", "2015"),
                     col="unique aircraft", fmt="int"),
    "tk_y2018": dict(table="la_filings_per_year", where=("priority year", "2018"),
                     col="unique aircraft", fmt="int"),
    "tk_y2021": dict(table="la_filings_per_year", where=("priority year", "2021"),
                     col="unique aircraft", fmt="int"),
    "tk_incomplete_years": dict(table="la_filings_per_year", how="count", where=("complete", "False"),
                                fmt="int"),
    "tk_tr_w1": dict(table="a2_d9_architecture_by_window", where=("window", "<= 2011"),
                     col="Tilt Rotor", fmt="pct"),
    "tk_tr_w4": dict(table="a2_d9_architecture_by_window", where=("window", "2020-23"),
                     col="Tilt Rotor", fmt="pct"),
    "tk_slc_w1": dict(table="a2_d9_architecture_by_window", where=("window", "<= 2011"),
                      col="Lift + Cruise", fmt="pct"),
    "tk_slc_w4": dict(table="a2_d9_architecture_by_window", where=("window", "2020-23"),
                      col="Lift + Cruise", fmt="pct"),
    "tk_cvt_w4": dict(table="a2_d9_architecture_by_window", where=("window", "2020-23"),
                      col="Combined vectored thrust", fmt="pct"),
    "tk_dd_top_share": dict(table="la_dominant_design", how="max", col="top share", fmt="pct"),
    "tk_dd_top_arch": dict(table="la_dominant_design", how="max", col="top share", out="top archetype"),
    "tk_dd_cells": dict(table="la_dominant_design", how="rows", fmt="int"),
    "tk_dd_below": dict(table="la_dominant_design", how="count", where=("below band", "True"), fmt="int"),
    "tk_q_below": dict(table="la_dd_q", how="count", where=("below band", "True"), fmt="int"),
    "tk_q_cells": dict(table="la_dd_q", how="rows", fmt="int"),
    "tk_slc_modal_1619": dict(table="la_class_configs",
                              where=[("code", "SLC"), ("window", "2016-19")], col="modal share", fmt="pct"),
    "tk_slc_configs_2023": dict(table="la_class_configs",
                                where=[("code", "SLC"), ("window", "2020-23")], col="configurations", fmt="int"),
    "tk_slc_n_2023": dict(table="la_class_configs",
                          where=[("code", "SLC"), ("window", "2020-23")], col="aircraft", fmt="int"),
    "tk_slc_units_w1": dict(table="la_dimension_drift",
                            where=[("code", "SLC"), ("window", "<= 2011")], col="median propulsor units", fmt="1f"),
    "tk_tr_units_w1": dict(table="la_dimension_drift",
                           where=[("code", "TR"), ("window", "<= 2011")], col="median propulsor units", fmt="1f"),
    "tk_tr_units_w4": dict(table="la_dimension_drift",
                           where=[("code", "TR"), ("window", "2020-23")], col="median propulsor units", fmt="1f"),
    "tk_cvt_boom_w4": dict(table="la_dimension_drift",
                           where=[("code", "CVT"), ("window", "2020-23")], col="boom share", fmt="pct"),
    "tk_cvt_boom_w1": dict(table="la_dimension_drift",
                           where=[("code", "CVT"), ("window", "<= 2011")], col="boom share", fmt="pct"),
    "tk_hb_n": dict(table="la_class_cycles", where=("class", "Hoverbike"), col="aircraft", fmt="int"),
    "tk_hb_1619": dict(table="la_class_cycles", where=("class", "Hoverbike"), col="2016-19", fmt="pct"),
    "tk_pfv_n": dict(table="la_class_cycles", where=("class", "Personal Flying Vehicle"),
                     col="aircraft", fmt="int"),
    "tk_srw_n": dict(table="la_class_cycles", where=("class", "Stopped/Slowed Rotor Wing"),
                     col="aircraft", fmt="int"),
    "tk_slc_own_2023": dict(table="la_class_cycles", where=("class", "Lift + Cruise"),
                            col="2020-23", fmt="pct"),
    "tk_tr_own_1619": dict(table="la_class_cycles", where=("class", "Tilt Rotor"), col="2016-19", fmt="pct"),
    "tk_na_50": dict(table="la_lead_lag_region", where=("region3", "North America"), col="50 %", fmt="int"),
    "tk_ap_50": dict(table="la_lead_lag_region", where=("region3", "Asia-Pacific"), col="50 %", fmt="int"),
    "tk_eu_50": dict(table="la_lead_lag_region", where=("region3", "Europe"), col="50 %", fmt="int"),
    "tk_tr_50": dict(table="la_lead_lag_class", where=("topType", "Tilt Rotor"), col="50 %", fmt="int"),
    "tk_cvt_50": dict(table="la_lead_lag_class", where=("topType", "Combined vectored thrust"),
                      col="50 %", fmt="int"),
    "tk_d1_1619": dict(table="la_hill_by_window",
                       where=[("level", "A0c class × propulsive-unit bin"), ("window", "2016-19")],
                       col="D1", fmt="1f"),
    "tk_d1_2023": dict(table="la_hill_by_window",
                       where=[("level", "A0c class × propulsive-unit bin"), ("window", "2020-23")],
                       col="D1", fmt="1f"),
    "tk_d1_w1": dict(table="la_hill_by_window",
                     where=[("level", "A0c class × propulsive-unit bin"), ("window", "<= 2011")],
                     col="D1", fmt="1f"),
    "tk_zone_top": dict(table="la_zones", how="max", col="aircraft", out="archetype"),
    "tk_zone_top_n": dict(table="la_zones", how="max", col="aircraft", fmt="int"),
    "tk_zone_top_filers": dict(table="la_zones", how="max", col="aircraft", out="filers", fmt="int"),
    "tk_zone_crowded": dict(table="la_zones", how="count", where=("zone", "persistent"), fmt="int"),
    # 4.1.9b, the filer-weight figure and table (2026-09-23)
    "tk_fw_tr_largest": dict(table="la_class_filer_weight", where=("class", "Tilt Rotor"),
                             col="largest filer"),
    "tk_fw_tr_share": dict(table="la_class_filer_weight", where=("class", "Tilt Rotor"),
                           col="its share", fmt="pct"),
    "tk_fw_cvt_share": dict(table="la_class_filer_weight", where=("class", "Combined vectored thrust"),
                            col="its share", fmt="pct"),
    "tk_fw_cvt_eff": dict(table="la_class_filer_weight", where=("class", "Combined vectored thrust"),
                          col="effective filers", fmt="1f"),
    "tk_fw_tr_win": dict(table="la_class_window_filer_weight",
                         where=[("class", "Tilt Rotor"), ("window", "2016-19")], col="its share", fmt="pct"),
    "tk_fw_cvt_win": dict(table="la_class_window_filer_weight",
                          where=[("class", "Combined vectored thrust"), ("window", "2020-23")],
                          col="its share", fmt="pct"),
    "tk_crt_cvt_na": dict(table="la_class_region_timing", where=("class", "Combined vectored thrust"),
                          col="North America"),
    "tk_lapsed_all": dict(table="la_abandonment_by_class", where=("class", "all classes"),
                          col="lapsed share", fmt="pct"),
    "tk_lapsed_n": dict(table="la_abandonment_by_class", where=("class", "all classes"),
                        col="patents", fmt="int"),
    "tk_lapsed_tr": dict(table="la_abandonment_by_class", where=("class", "Tilt Rotor"),
                         col="lapsed share", fmt="pct"),
    "tk_lapsed_slc": dict(table="la_abandonment_by_class", where=("class", "Lift + Cruise"),
                          col="lapsed share", fmt="pct"),
    "tk_lapsed_cvt": dict(table="la_abandonment_by_class", where=("class", "Combined vectored thrust"),
                          col="lapsed share", fmt="pct"),
    # ---------------------------------------------------------------- 4.2
    "tk_tier10_firms": dict(table="la_firm_tiers", where=("rule", "10 or more aircraft"),
                            col="firms", fmt="int"),
    "tk_tier10_air": dict(table="la_firm_tiers", where=("rule", "10 or more aircraft"),
                          col="aircraft", fmt="int"),
    "tk_tier5_firms": dict(table="la_firm_tiers", where=("rule", "5 or more aircraft"),
                           col="firms", fmt="int"),
    "tk_tier5_share": dict(table="la_firm_tiers", where=("rule", "5 or more aircraft"),
                           col="share of the analysis set", fmt="pct"),
    "tk_named_share": dict(table="la_firm_tiers", where=("rule", "all named companies"),
                           col="share of the analysis set", fmt="pct"),
    "tk_ind_air": dict(table="la_firm_tiers", where=("rule", "individual inventors"),
                       col="aircraft", fmt="int"),
    "tk_firms_2023": dict(table="la_filers_by_window", where=("window", "2020-23"),
                          col="named firms active", fmt="int"),
    "tk_new_2023": dict(table="la_filers_by_window", where=("window", "2020-23"),
                        col="new firms", fmt="int"),
    "tk_firms_w1": dict(table="la_filers_by_window", where=("window", "<= 2011"),
                        col="named firms active", fmt="int"),
    "tk_indshare_w1": dict(table="la_filers_by_window", where=("window", "<= 2011"),
                           col="share individual inventors", fmt="pct"),
    "tk_indshare_2023": dict(table="la_filers_by_window", where=("window", "2020-23"),
                             col="share individual inventors", fmt="pct"),
    "tk_coh_2023_n": dict(table="la_cohorts", where=("window", "2020-23"), col="firms entering", fmt="int"),
    "tk_coh_2023_slc": dict(table="la_cohorts", where=("window", "2020-23"), col="SLC", fmt="int"),
    "tk_coh_w1_tr": dict(table="la_cohorts", where=("window", "<= 2011"), col="TR", fmt="int"),
    "tk_coh_w1_n": dict(table="la_cohorts", where=("window", "<= 2011"), col="firms entering", fmt="int"),
    # --- 4.2.1 market standing against patenting (author's ruling 2026-09-23)
    "tk_mkt_held": dict(table="la_market_vs_patents",
                        where=("reading", "aircraft held, and their share of the analysis set"),
                        col="AAM index firms", fmt="raw"),
    "tk_mkt_held_rest": dict(table="la_market_vs_patents",
                             where=("reading", "aircraft held, and their share of the analysis set"),
                             col="other named firms", fmt="raw"),
    "tk_mkt_air_l": dict(table="la_market_vs_patents", where=("reading", "unique aircraft per firm, median"),
                         col="AAM index firms", fmt="raw"),
    "tk_mkt_air_r": dict(table="la_market_vs_patents", where=("reading", "unique aircraft per firm, median"),
                         col="other named firms", fmt="raw"),
    "tk_mkt_air_p": dict(table="la_market_vs_patents", where=("reading", "unique aircraft per firm, median"),
                         col="test", fmt="raw"),
    "tk_mkt_year_p": dict(table="la_market_vs_patents", where=("reading", "first priority year, median"),
                          col="test", fmt="raw"),
    "tk_mkt_rho": dict(table="la_market_vs_patents",
                       where=("reading", "within the index — index score against unique aircraft"),
                       col="AAM index firms", fmt="raw"),
    "tk_mkt_rho_p": dict(table="la_market_vs_patents",
                         where=("reading", "within the index — index score against unique aircraft"),
                         col="p", fmt="2f"),
    "tk_seg_top_firms": dict(table="la_coverage_segments", where=("aircraft per firm", "10 or more"),
                             col="firms", fmt="int"),
    "tk_seg_top_air": dict(table="la_coverage_segments", where=("aircraft per firm", "10 or more"),
                           col="aircraft", fmt="int"),
    "tk_seg_59_firms": dict(table="la_coverage_segments", where=("aircraft per firm", "5-9"), col="firms", fmt="int"),
    "tk_seg_59_air": dict(table="la_coverage_segments", where=("aircraft per firm", "5-9"), col="aircraft", fmt="int"),
    "tk_seg_one_firms": dict(table="la_coverage_segments", where=("aircraft per firm", "1"), col="firms", fmt="int"),
    # --- 4.2.3 firm leverage. tk_lev_firm / tk_lev_pp / tk_conc_max are defined once, further down
    # with the rest of the takeaway register; only the keys nothing else defines are added here.
    "tk_lev_air": dict(table="la_firm_leverage", col="unique aircraft", fmt="int"),
    "tk_lev_ge1": dict(table="la_firm_leverage", how="count_ge", col="shift magnitude (pp)",
                       at_least=1.0, fmt="int"),
    "tk_conc_cvt": dict(table="la_class_concentration", where=("class", "CVT"),
                        col="its share of the class", fmt="pct"),
    "tk_conc_cvt3": dict(table="la_class_concentration", where=("class", "CVT"),
                         col="top 3 firms' share", fmt="pct"),
    "tk_mix_ap": dict(table="la_filer_mix", where=("filer", "Named companies"), col="aircraft per patent", fmt="2f"),
    "tk_mix_ind_ap": dict(table="la_filer_mix", where=("filer", "Individual inventors"),
                          col="aircraft per patent", fmt="2f"),
    # --- 4.2.2 entrants against the field
    "tk_ent_slc_2023": dict(table="la_cohort_mix", where=[("window", "2020-23"), ("class", "SLC")],
                            col="share of entrants", fmt="pct"),
    "tk_air_slc_2023": dict(table="la_cohort_mix", where=[("window", "2020-23"), ("class", "SLC")],
                            col="share of aircraft", fmt="pct"),
    "tk_ent_tr_w1": dict(table="la_cohort_mix", where=[("window", "<= 2011"), ("class", "TR")],
                         col="share of entrants", fmt="pct"),
    "tk_air_tr_w1": dict(table="la_cohort_mix", where=[("window", "<= 2011"), ("class", "TR")],
                         col="share of aircraft", fmt="pct"),
    "tk_trans_pairs": dict(table="la_transitions", how="sum", col="pairs", fmt="int"),
    "tk_trans_same": dict(table="la_transitions", how="sum", where=("same class", "True"),
                          col="pairs", fmt="int"),
    "tk_trans_share": dict(table="la_transitions", how="share", where=("same class", "True"),
                           col="pairs", fmt="pct"),
    "tk_ip_max_ppa": dict(table="la_ip_strategy", how="max", col="patents per aircraft", out="firm"),
    "tk_ip_max_ppa_v": dict(table="la_ip_strategy", how="max", col="patents per aircraft", fmt="1f"),
    "tk_ip_min_ppa": dict(table="la_ip_strategy", how="min", col="patents per aircraft", out="firm"),
    "tk_ip_min_ppa_v": dict(table="la_ip_strategy", how="min", col="patents per aircraft", fmt="1f"),
    "tk_ipc_slc_cit": dict(table="la_ip_by_class", where=("class", "Lift + Cruise"),
                           col="median forward citations", fmt="int"),
    "tk_ipc_tr_cit": dict(table="la_ip_by_class", where=("class", "Tilt Rotor"),
                          col="median forward citations", fmt="int"),
    "tk_ipc_slc_claims": dict(table="la_ip_by_class", where=("class", "Lift + Cruise"),
                              col="median claims", fmt="int"),
    "tk_ipc_tr_claims": dict(table="la_ip_by_class", where=("class", "Tilt Rotor"),
                             col="median claims", fmt="int"),
    "tk_prox_diff": dict(table="la_proximity_region", where=("firm pair", "different regions"),
                         col="mean", fmt="2f"),
    "tk_prox_same": dict(table="la_proximity_region", where=("firm pair", "same region"),
                         col="mean", fmt="2f"),
    "tk_prox_pairs": dict(table="la_proximity_region", how="sum", col="pairs", fmt="int"),
    "tk_ari_rho_air": dict(table="la_ari_correlation", where=[("x", "ARI score"), ("y", "unique aircraft")],
                           col="Spearman rho", fmt="2f"),
    "tk_ari_p_air": dict(table="la_ari_correlation", where=[("x", "ARI score"), ("y", "unique aircraft")],
                         col="p", fmt="2f"),
    "tk_ari_rho_cls": dict(table="la_ari_correlation", where=[("x", "funding"), ("y", "classes")],
                           col="Spearman rho", fmt="2f"),
    "tk_ari_n_fund": dict(table="la_ari_correlation", where=[("x", "funding"), ("y", "classes")],
                          col="n firms", fmt="int"),
    "tk_ari_rho_year": dict(table="la_ari_correlation", where=[("x", "funding"), ("y", "first priority year")],
                            col="Spearman rho", fmt="2f"),
    "tk_ari_timeline_n": dict(table="la_ari_timeline", how="rows", fmt="int"),
    # ---------------------------------------------------------------- 4.3
    "tk_spec_tr03_na": dict(table="la_specialisation", where=("archetype", "TR · 0-3"),
                            col="North America", fmt="1f"),
    "tk_spec_ptc_eu": dict(table="la_specialisation", where=("archetype", "PTC · 7-8"),
                           col="Europe", fmt="1f"),
    "tk_spec_ptc_na": dict(table="la_specialisation", where=("archetype", "PTC · 7-8"),
                           col="North America", fmt="1f"),
    "tk_us_n": dict(table="la_country_class", where=("country", "US"), col="aircraft", fmt="int"),
    "tk_cn_n": dict(table="la_country_class", where=("country", "CN"), col="aircraft", fmt="int"),
    "tk_de_n": dict(table="la_country_class", where=("country", "DE"), col="aircraft", fmt="int"),
    "tk_us_tr": dict(table="la_country_class", where=("country", "US"), col="Tilt Rotor", fmt="pct"),
    "tk_us_slc": dict(table="la_country_class", where=("country", "US"), col="Lift + Cruise", fmt="pct"),
    "tk_cn_slc": dict(table="la_country_class", where=("country", "CN"), col="Lift + Cruise", fmt="pct"),
    "tk_cn_tr": dict(table="la_country_class", where=("country", "CN"), col="Tilt Rotor", fmt="pct"),
    "tk_jp_slc": dict(table="la_country_class", where=("country", "JP"), col="Lift + Cruise", fmt="pct"),
    # ---------------------------------------------------------------- chapter 5
    "tk_pw_slc_el": dict(table="la_powertrain_by_class", where=("class", "Lift + Cruise"),
                         col="electric", fmt="int"),
    "tk_pw_slc_n": dict(table="la_powertrain_by_class", where=("class", "Lift + Cruise"),
                        col="aircraft", fmt="int"),
    "tk_pw_tw_hy": dict(table="la_powertrain_by_class", where=("class", "Tilt Wing"),
                        col="hybrid", fmt="int"),
    "tk_pw_tw_n": dict(table="la_powertrain_by_class", where=("class", "Tilt Wing"),
                       col="aircraft", fmt="int"),
    "tk_pw_tr_ns": dict(table="la_powertrain_by_class", where=("class", "Tilt Rotor"),
                        col="not stated", fmt="int"),
    "tk_pw_el": dict(table="la_powertrain_by_class", how="sum", col="electric", fmt="int"),
    "tk_pw_ns": dict(table="la_powertrain_by_class", how="sum", col="not stated", fmt="int"),
    "tk_state_n": dict(table="a2_d2_figure_slot_answers", where=("slot", "flight state drawn"),
                       col="answered", fmt="int"),
    "tk_fold_vt": dict(table="la_class_fold", how="sum", where=("evtol.news class", "Vectored Thrust (VT)"),
                       col="unique aircraft", fmt="int"),
    "tk_fold_lc": dict(table="la_class_fold", how="sum", where=("evtol.news class", "Lift + Cruise (LC)"),
                       col="unique aircraft", fmt="int"),
    "tk_cap_ns": dict(table="la_mission_capacity", where=("capacity", "not stated"), col="all", fmt="int"),
    "tk_cap_34": dict(table="la_mission_capacity", where=("capacity", "3-4"), col="all", fmt="int"),
    "tk_cap_tot": dict(table="la_mission_capacity", how="sum", col="all", fmt="int"),
    "tk_pil_ns": dict(table="la_mission_piloting", where=("piloting", "not stated"), col="all", fmt="int"),
    "tk_pil_either": dict(table="la_mission_piloting", where=("piloting", "either"), col="all", fmt="int"),
    "tk_pow_batt": dict(table="la_mission_power source", where=("power source", "battery electric"),
                        col="all", fmt="int"),
    "tk_pow_h2": dict(table="la_mission_power source", where=("power source", "hydrogen"),
                      col="all", fmt="int"),
    "tk_st_concept": dict(table="la_mission_status", where=("status", "concept design"), col="all", fmt="int"),
    "tk_st_prod": dict(table="la_mission_status", where=("status", "production"), col="all", fmt="int"),
    "tk_st_defunct": dict(table="la_mission_status", where=("status", "defunct"), col="all", fmt="int"),
    "tk_agree_vt": dict(table="la_mission_agreement", where=("patent label", "G1 folded: Vectored Thrust"),
                        col="VT", fmt="int"),
    "tk_agree_lc": dict(table="la_mission_agreement", where=("patent label", "G1 folded: Lift + Cruise"),
                        col="LC", fmt="int"),
    "tk_agree_lc_vt": dict(table="la_mission_agreement", where=("patent label", "G1 folded: Lift + Cruise"),
                           col="VT", fmt="int"),
    "tk_ind_slc_gen": dict(table="la_industry_by_class", where=("class", "Lift + Cruise"),
                           col="General_Unspecified", fmt="int"),
    "tk_ind_slc_n": dict(table="la_industry_by_class", where=("class", "Lift + Cruise"),
                         col="aircraft", fmt="int"),
    "tk_ind_gen": dict(table="la_industry_by_class", how="sum", col="General_Unspecified", fmt="int"),
    "tk_ind_uam": dict(table="la_industry_by_class", how="sum", col="UAM_Passenger", fmt="int"),
    "tk_ind_rec": dict(table="la_industry_by_class", how="sum", col="Recreation_Sport", fmt="int"),
    "tk_ex_us_n": dict(table="la_examination_office", where=("pub_office", "US"), col="patents", fmt="int"),
    "tk_ex_us_gr": dict(table="la_examination_office", where=("pub_office", "US"),
                        col="granted, in force", fmt="int"),
    "tk_ex_cn_n": dict(table="la_examination_office", where=("pub_office", "CN"), col="patents", fmt="int"),
    "tk_ex_cn_gr": dict(table="la_examination_office", where=("pub_office", "CN"),
                        col="granted, in force", fmt="int"),
    "tk_ex_cn_ref": dict(table="la_examination_office", where=("pub_office", "CN"), col="refused", fmt="int"),
    "tk_exc_slc_gr": dict(table="la_examination_class", where=("topType", "Lift + Cruise"),
                          col="granted, in force", fmt="int"),
    "tk_exc_slc_n": dict(table="la_examination_class", where=("topType", "Lift + Cruise"),
                         col="patents", fmt="int"),
    "tk_exc_tr_gr": dict(table="la_examination_class", where=("topType", "Tilt Rotor"),
                         col="granted, in force", fmt="int"),
    "tk_exc_tr_n": dict(table="la_examination_class", where=("topType", "Tilt Rotor"),
                        col="patents", fmt="int"),
    # ---------------------------------------------------------------- new items (4.2/4.3 rework)
    "tk_name_arch_n": dict(table="la_name_arch_check", how="rows", fmt="int"),
    "tk_lev_max": dict(table="la_firm_leverage", how="max", col="points moved", out="firm"),
    "tk_conc_max": dict(table="la_class_concentration", how="max", col="its share of the class",
                        out="class"),
    "tk_conc_max_v": dict(table="la_class_concentration", how="max", col="its share of the class",
                          fmt="pct"),
    "tk_lev_firm": dict(table="la_firm_leverage", how="max", col="shift if the firm is dropped (pp)",
                        out="firm"),
    "tk_lev_pp": dict(table="la_firm_leverage", how="max", col="shift if the firm is dropped (pp)",
                      fmt="1f"),
    "tk_lev_class": dict(table="la_firm_leverage", how="max", col="shift if the firm is dropped (pp)",
                         out="class most moved"),
    "tk_cfw_max": dict(table="la_class_filer_weight", how="max", col="its share", fmt="pct"),
    "tk_cfw_class": dict(table="la_class_filer_weight", how="max", col="its share", out="class"),
    "tk_cfw_slc_filers": dict(table="la_class_filer_weight", where=("code", "SLC"),
                              col="filers", fmt="int"),
    "tk_cfw_slc_rep": dict(table="la_class_filer_weight", where=("code", "SLC"),
                           col="repetition factor", fmt="2f"),
    "tk_fm_named_air": dict(table="la_filer_mix", where=("filer", "Named companies"),
                            col="unique aircraft", fmt="int"),
    "tk_fm_named_share": dict(table="la_filer_mix", where=("filer", "Named companies"),
                              col="share of the analysis set", fmt="pct"),
    "tk_fm_named_pat": dict(table="la_filer_mix", where=("filer", "Named companies"),
                            col="share per primary patent", fmt="pct"),
    "tk_fm_ind_air": dict(table="la_filer_mix", where=("filer", "Individual inventors"),
                          col="unique aircraft", fmt="int"),
    "tk_cm_e_slc": dict(table="la_cohort_mix", where=[("window", "2020-23"), ("class", "SLC")],
                        col="share of entrants", fmt="pct"),
    "tk_cm_a_slc": dict(table="la_cohort_mix", where=[("window", "2020-23"), ("class", "SLC")],
                        col="share of aircraft", fmt="pct"),
}

#: what the reader should conclude from each figure and each table. ONE ENTRY PER KEY.
TAKEAWAY: Dict[str, str] = {
    # ---------------------------------------------------------------- front matter
    "la_flags": (
        "Nothing here has been removed: the list is what one reader would cut and why, so the "
        "decision stays with the author. {tk_flags_n} items are on it, and no measurement put "
        "them there."),

    # ================================================================ 1 data sets
    "fig_02_refinement_funnel": (
        "The corpus is set by what counts as an eVTOL, not by duplicate handling: {disapproved} of "
        "the {acquired_s} acquired patents leave at refinement 1, while only {o12_removed} "
        "observations are merged away as repeats, leaving {unique_s} unique aircraft. Every count "
        "in this document is on those {unique_s}."),
    "atlas_removal": (
        "Three reasons carry the removals — no usable image ({r_noimg}), a declared UAV ({r_uav}) "
        "and out of domain ({r_ood}) — and the domain gate then takes {gated_aircraft} aircraft "
        "that had already been labelled. The boundary of the study is a reading decision, not a "
        "search decision."),
    "a2_d1_similars": (
        "The two near-miss tags remove aircraft that the search could not have excluded: "
        "{r_sim_uav} patents lose every aircraft to UAV-but-similar and {r_sim_el} to "
        "not-electric-but-similar. Both are judgements on the text, so both are places a reviewer "
        "can push."),
    "a2_d9_publication_lag_region": (
        "The lag is the same everywhere — a median of {lag_median_lo} to {lag_median_hi} years and "
        "a 90th percentile of {lag_p90} in all three main regions — so one cut-off serves the whole "
        "corpus and no region's recent years are penalised more than another's."),
    "a2_d1_filing_status": (
        "Office status is not evidence of quality at this stage: {granted_pri} of the {primary_s} "
        "primary patents are granted and in force, {withdrawn_pri} ended without a grant, and the "
        "three columns are nested subsets of the same patents. Read this as the state of the "
        "paperwork, never as a filter on the designs."),
    "atlas_duplicates": (
        "Repetition is re-publication, not new drawing: {o2_obs} of the {observations_s} "
        "observations repeat an aircraft with the same figures and only {o1_obs} bring new ones. "
        "Almost every patent draws one aircraft ({tk_one_aircraft} of {primary_s})."),
    "a2_d7_duplicates": (
        "The de-duplication is arithmetic, not judgement: {observations_s} observations minus "
        "{o12_removed} repeats gives the {unique_s} unique aircraft, and the {s3} similar aircraft "
        "were relabelled in full rather than inherited."),
    "a2_d7_aircraft_per_patent": (
        "One patent means one aircraft: {tk_one_aircraft} of the {primary_s} primary patents draw a "
        "single aircraft, so patent counts and aircraft counts differ by a few per cent, not by a "
        "factor."),
    "atlas_figure_approval": (
        "The evidence behind an aircraft is thin: the median aircraft rests on {median_figs} "
        "approved whole-aircraft figures and {single_fig} of them ({single_share}) on one. A single "
        "view can hide a tilting mechanism, so single-figure aircraft are the ones a class error "
        "would come from."),
    "a2_d11_figure_approval": (
        "The label set is a whole-vehicle set by construction: {whole_vehicle} of the "
        "{figures_approved_s} approved figures show the whole vehicle and only {detail_figs} a "
        "mechanism. Nothing in this document can speak about detail design."),

    # ================================================================ 2 taxonomy
    "design_space_cards": (
        "The questionnaire is deeper than any one aircraft: {questions} slots exist and an aircraft "
        "answers a median of {median_q}. A blank is usually a design absence — no wing panel on a "
        "wingless aircraft — not a missing label."),
    "codebook_classes": (
        "The twelve classes split on what tilts and what lifts in cruise, never on size or mission, "
        "and they are very unequal: the largest holds a share of {top_class_share} of the corpus "
        "({top_class}) and {small_classes} classes stay under a dozen aircraft. Only the five "
        "largest can carry a share over time."),
    "codebook_dimensions": (
        "Almost the whole card set earns its place: {q_gt90} of the {questions} slots are answered "
        "for more than 90 % of the aircraft and {q_lt5_phrase} answered for fewer than 5 %. The "
        "unused depth is in the repeated M3 panels, not in dead questions."),

    # ================================================================ 3 data quality
    "atlas_fill": (
        "Where a part exists it is described: the worst field in the whole card set is blank in "
        "{tk_fill_worst_sh} of the aircraft that have that part ({tk_fill_worst}). Missingness "
        "cannot move any result in this document, and nothing is imputed anywhere."),
    "a2_d4_missingness": (
        "The largest single gap is {tk_fill_worst_n} aircraft on {tk_fill_worst} "
        "({tk_fill_worst_sh}); no field is blank often enough to change a class share, which is why "
        "no imputation is used."),
    "la_relabel_protocol": (
        "This document carries no measured intra-rater reliability: the relabel of 50 patents is "
        "designed but not run. Until it is, every agreement number here is against an outside "
        "source, never between the labeller and himself, and that is the one reliability claim the "
        "thesis still owes."),
    "atlas_flagship": (
        "The labels agree with the public aircraft for {flagship_match} of the {flagship_public} "
        "firms that have one. In the {flagship_mismatch} that miss ({flagship_mismatch_names}) the "
        "public type is still inside the firm's patent mix — what fails is the assumption that a "
        "firm's most-filed class is its product, not the label."),
    "a2_d13_flagship_check": (
        "A firm's portfolio is wider than its product line: the largest filer carries "
        "{tk_flag_types} distinct classes and {tk_flag_multi} of the {n_flagship_firms} firms "
        "listed hold three or more. Every firm-level class statement in Chapter 4 is a mix, never "
        "a firm's architecture."),
    "la_name_arch_check": (
        "{tk_name_arch_n} aircraft have sources that disagree on the architecture. That is the size "
        "of the correction a full adjudication would apply to the {unique_s} of the analysis set, "
        "and each row is a case to settle by hand rather than a rule to apply."),
    "a2_d3_selected_fields": (
        "Most fields have one answer that dominates — symmetry {tk_latsym}, a fixed fuselage "
        "{tk_fuskin}, standard wings {tk_wingconf} — so the variety of this corpus lives in the two "
        "that are spread: tail type (top answer {tk_emptype}) and the number of propulsive units "
        "(top bin {tk_units_top})."),
    "atlas_fields": (
        "Label depth is a property of the design, not of the labelling: an aircraft answers a median "
        "of {median_q} of the {questions} slots, and the classes that answer fewest are the ones "
        "with no wing and no boom to describe. A low count is never a weaker record."),
    "a2_d2_informative_fields": (
        "Only {informative} of the coded fields carry real information and {near_constant} are "
        "near-constant; the two that separate designs best are tail type and the architecture class "
        "itself ({tk_inf_emp} and {tk_inf_top} effective answers). Any clustering on the raw label "
        "set is driven by a handful of columns."),
    "atlas_arch_gt": (
        "The figures recover the whole-patent architecture well for the large winged classes (Tilt "
        "Rotor {tk_gt_tr}, Lift + Cruise {tk_gt_slc}) and badly for the small ones (Pitch-to-Cruise "
        "{tk_gt_ptc}, Hoverbike {tk_gt_hb}). Read every small-class number in this document as the "
        "least reliable one on its page."),

    # ================================================================ 4.1
    "filings_per_year": (
        "Filing takes off in 2016 and then plateaus: unique aircraft per year rise from {tk_y2015} "
        "in 2015 to {tk_y2018} in 2018 and stay near that level to 2022. The fall at the right edge "
        "is the {lag_p90}-year publication lag, not a decline in the sector."),
    "la_filings_per_year": (
        "The right edge is not readable: {tk_incomplete_years} priority years are still inside the "
        "{lag_p90}-year publication lag and are marked incomplete, so no trend statement in this "
        "document runs past the last complete year."),
    "atlas_arch_time": (
        "Lift + Cruise overtakes Tilt Rotor and keeps the lead: TR falls from {tk_tr_w1} of the "
        "aircraft in the earliest window to {tk_tr_w4} in 2020-23 while SLC rises from {tk_slc_w1} "
        "to {tk_slc_w4}. Together with CVT ({tk_cvt_w4}) the three hold about three quarters of the "
        "recent corpus."),
    "la_archetype_levels": (
        "The level decides the answer, not the corpus: at A0 the aircraft fall into {a0_distinct} "
        "archetypes with {a0_eff} effective ones, at A2c into {a2c_distinct} of which {a2c_single} "
        "hold a single aircraft. Any convergence claim is a claim about a level and must name it."),
    "la_archetype_choice": (
        "Two levels survive the four screens: A1t ({a1t_distinct} archetypes, {a1t_single} of them "
        "alone) and A0c ({a0c_distinct}, {a0c_single} alone). The finer levels fail because most of "
        "their archetypes hold one aircraft ({a2c_single} of {a2c_distinct} at A2c), which no "
        "diversity measure can use."),
    "la_dd_conditions": (
        "Nothing is measured here: the three thresholds were fixed in the Preliminary Analysis "
        "before this corpus was read. That is what makes 4.1.3.3 a test whose answer could have "
        "been yes, rather than a description written after the fact."),
    "la_dd_result": (
        "No dominant design. Condition 1 is not close — the largest archetype share anywhere is "
        "{tk_dd_top_share} ({tk_dd_top_arch}) against a 50 % line — and the balance condition fires "
        "in only {tk_dd_below} of the {tk_dd_cells} level-windows, in the earliest ones. The corpus "
        "is still in the era of ferment on its own pre-stated criterion."),
    "dominant_design": (
        "The top-share line never approaches 50 %: the largest archetype of any window is "
        "{tk_dd_top_share} ({tk_dd_top_arch}). Where ²D leaves the permutation band it does so in "
        "the two earliest windows, where the corpus is thinnest — so the only balance signal in the "
        "test is the one with the least data behind it."),
    "dominant_design_q": (
        "Condition 3 changes with the weighting rather than with the corpus: Q falls below the band "
        "in {tk_q_below} of the {tk_q_cells} cells measured. Treat it as evidence that the answer "
        "depends on how the dimensions are weighted, not as evidence of convergence."),
    "la_dominant_design": (
        "Read the two levels together: A1t concentrates the corpus more than A0c but neither "
        "reaches half, and the top archetype changes identity between the early windows (Tilt Rotor) "
        "and the late ones (Lift + Cruise). The leader turns over; the concentration does not rise."),
    "la_dd_q": (
        "Q is stable across the windows and its excursions are inside or near the permutation band "
        "({tk_q_below} of {tk_q_cells} cells below it), so the spread of the design space is not "
        "narrowing even where the shares move."),
    "class_configs": (
        "Inside a class the designs do not settle: the modal configuration of Lift + Cruise is only "
        "{tk_slc_modal_1619} of the class in 2016-19, and in 2020-23 its {tk_slc_n_2023} aircraft "
        "take {tk_slc_configs_2023} different configurations. Convergence on the class label is not "
        "convergence on a design."),
    "la_class_configs": (
        "The number of configurations grows with the number of aircraft in almost every cell, so the "
        "modal share falls as a class grows ({tk_slc_modal_1619} for Lift + Cruise in 2016-19). "
        "This table is the direct answer to 'has anything converged': inside the classes, no."),
    "dimension_drift": (
        "The one dimension that moves in the same direction in every class is the number of "
        "propulsive units: Tilt Rotor goes from a median of {tk_tr_units_w1} units in the earliest "
        "window to {tk_tr_units_w4} in 2020-23, and booms follow it (CVT {tk_cvt_boom_w1} to "
        "{tk_cvt_boom_w4}). Ducting does not trend."),
    "la_dimension_drift": (
        "Units and booms rise together across the classes while ducting stays flat, so the drift is "
        "towards distributed thrust on structure, not towards a quieter or more integrated "
        "installation — the ducted share is the one number that does not move."),
    "class_cycles": (
        "Each class has a lifetime: Hoverbike is concentrated in 2016-19 ({tk_hb_1619} of its "
        "{tk_hb_n} aircraft) and is nearly gone afterwards, while Lift + Cruise puts "
        "{tk_slc_own_2023} of its own aircraft in 2020-23. The classes under about twenty aircraft "
        "({tk_pfv_n} for Personal Flying Vehicle, {tk_srw_n} for the slowed rotor wing) cannot "
        "carry a shape at all — their peaks are a handful of patents."),
    "la_class_cycles": (
        "The median window separates the classes into an early group (Tilt Rotor, Tilt Wing, "
        "Multirotor, Hoverbike — all 2016-19) and a late one (Lift + Cruise, CVT, Deflected "
        "Slipstream — 2020-23). For a class with under twenty aircraft the median window is one or "
        "two patents wide and should not be read."),
    "lead_lag": (
        "Asia-Pacific is the late entrant and the fast one: it reaches half its aircraft in "
        "{tk_ap_50} against {tk_na_50} for North America and {tk_eu_50} for Europe, and covers the "
        "same ground in fewer years. By class, CVT is the latest ({tk_cvt_50}) and Tilt Rotor the "
        "earliest ({tk_tr_50})."),
    "la_lead_lag_region": (
        "The regional gap is about two years at the median ({tk_na_50} against {tk_ap_50}), which "
        "is the same size as the publication lag — so this is a real ordering but a small one, and "
        "it should not be read as a technology gap."),
    "la_lead_lag_class": (
        "The class order matches the class shares: the classes that reach half their aircraft last "
        "(CVT {tk_cvt_50}) are the ones still growing in 4.1.2, and the earliest (Tilt Rotor "
        "{tk_tr_50}) is the one losing share. Timing and share tell the same story here, which is "
        "why one of the two can go."),
    "hill": (
        "Diversity does not fall: richness and the effective numbers are flat or slightly up across "
        "the windows (A0c ¹D {tk_d1_w1} in the earliest window against {tk_d1_2023} in 2020-23) and "
        "every band overlaps every other. A field converging on a dominant design would show this "
        "curve falling; it does not."),
    "la_hill_by_window": (
        "Every window's confidence band overlaps every other window's at both levels, so the "
        "honest reading is no change in diversity, not a trend — the rarefaction to 40 aircraft is "
        "what makes the windows comparable at all."),
    "zones": (
        "The design space has a crowded core and an empty rim: the largest archetype is "
        "{tk_zone_top} with {tk_zone_top_n} aircraft from {tk_zone_top_filers} distinct filers, and "
        "{tk_zone_crowded} of the archetypes are persistent rather than new. High aircraft counts "
        "come with high filer counts, so the crowding is a crowd, not one company."),
    "la_zones": (
        "Read the filers-per-aircraft column before the size column: an archetype held by many "
        "filers is a shared choice, one held by few is a portfolio. The largest archetype "
        "({tk_zone_top}, {tk_zone_top_n} aircraft) is spread over {tk_zone_top_filers} filers, so "
        "it is the first kind."),
    # added 2026-09-23 with Figure 4.1.9b and Table 4.1.9b
    "filer_weight": (
        "No class is one company's portfolio: the largest single filer holds {tk_fw_tr_share} of "
        "Tilt Rotor and {tk_fw_cvt_share} of CVT, and CVT divides as if between "
        "{tk_fw_cvt_eff} equally sized filers. One firm's weight does show inside a window — "
        "{tk_fw_tr_largest} holds {tk_fw_tr_win} of Tilt Rotor in 2016-19 and {tk_fw_cvt_win} of "
        "CVT in 2020-23 — so a single window's rise can be one firm, a class cannot."),
    "la_class_filer_weight": (
        "Read `its share` against `effective filers`: the four largest classes each divide as if "
        "between 25 or more equally sized filers, so their size is a shared choice and not one firm "
        "repeating itself. The last three columns check it a second way — give every filer one vote "
        "instead of counting aircraft and no class changes rank."),
    "la_class_region_timing": (
        "Every class is taken up first in North America, then Europe, then Asia-Pacific — with one "
        "exception, CVT, whose North American median is {tk_crt_cvt_na} and is the latest cell of "
        "that column. The Asia-Pacific lag is widest on the oldest classes and closes on CVT, which "
        "is what entering a field whose design menu is already set looks like."),
    "abandonment": (
        "Abandonment does not separate the classes: {tk_lapsed_all} of the {tk_lapsed_n} primary "
        "patents with a 2019-or-earlier priority are no longer in force, and the classes sit around "
        "that line (Tilt Rotor {tk_lapsed_tr}, Lift + Cruise {tk_lapsed_slc}, CVT {tk_lapsed_cvt}). "
        "The differences are within what a class of this size can show by chance."),
    "la_abandonment_by_class": (
        "The class column is not the finding; the base rate is: {tk_lapsed_all} of these patents "
        "lapsed, expired or were withdrawn. Nearly half of what is counted as a design in this "
        "corpus is no longer a live right, which is worth stating before any claim about industrial "
        "intent."),

    # ================================================================ 4.2
    "coverage": (
        "There is no top tier to speak of — {tk_seg_top_firms} firms hold {tk_seg_top_air} aircraft, "
        "the next {tk_seg_59_firms} hold {tk_seg_59_air}, and all {named_companies} named companies "
        "together only {tk_named_share} of the set — but market standing does pick the filers out: "
        "the firms the AAM Reality Index rates hold {tk_mkt_held} of the analysis set against "
        "{tk_mkt_held_rest} for every other named firm together, with a median of {tk_mkt_air_l} "
        "aircraft each against {tk_mkt_air_r} ({tk_mkt_air_p}). What does NOT follow is earliness — "
        "the two groups start in the same year ({tk_mkt_year_p}) — nor the position on the index, "
        "which does not track the patent side at all ({tk_mkt_rho}, p {tk_mkt_rho_p}), the two "
        "largest patent holders being incumbents the index rates low or no longer rates."),
    "la_market_vs_patents": (
        "Being rated is what goes with patenting, not where the rating sits: the index firms hold "
        "more aircraft and more patents than the other named firms, start no earlier, and are "
        "narrower per aircraft, while inside the index the score correlates with nothing on the "
        "patent side and only disclosed funding does. Read it as a description of who gets rated — "
        "a firm is on the index because it has a vehicle programme the market follows — not as "
        "evidence that either side causes the other."),
    "la_coverage_segments": (
        "The segments are the concentration: {tk_seg_top_firms} firms hold {tk_seg_top_air} aircraft "
        "and the next {tk_seg_59_firms} hold {tk_seg_59_air}, so the three largest filers are worth "
        "as much as the fourteen behind them; {tk_seg_one_firms} firms appear once and never again."),
    "la_firm_tiers": (
        "Every threshold is arbitrary because the curve has no elbow: cutting at ten firms keeps "
        "{tk_tier10_air} aircraft, at five keeps {tk_tier5_share} of the set. The ≥5 rule is used "
        "for firm profiles because it is the smallest cut that still leaves a comparable group, not "
        "because the data suggests it."),
    "filers_over_time": (
        "The field industrialises and the class shift arrives with the new firms: individual "
        "inventors fall from {tk_indshare_w1} of the aircraft in the earliest window to "
        "{tk_indshare_2023} in 2020-23, the named firms active rise from {tk_firms_w1} to "
        "{tk_firms_2023}, and {tk_new_2023} of those {tk_firms_2023} are filing for the first time. "
        "Normalised, panel (ii) says what the aircraft counts of 4.1.2 cannot: in 2020-23 "
        "{tk_ent_slc_2023} of the entering firms enter with Lift + Cruise against "
        "{tk_air_slc_2023} of the window's aircraft, exactly as {tk_ent_tr_w1} of the earliest "
        "entrants came in with Tilt Rotor against {tk_air_tr_w1} of its aircraft — entrants run "
        "ahead of the field, so the mix moves by arrival rather than by conversion."),
    "la_filers_by_window": (
        "Entry dominates: in every window most active firms are new arrivals, and the individual "
        "share falls from {tk_indshare_w1} to {tk_indshare_2023}. A population that is mostly "
        "first-time filers cannot be read for firm strategy — it is a population still forming."),
    "la_cohorts": (
        "Entrants arrive with the class of their moment: {tk_coh_2023_slc} of the {tk_coh_2023_n} "
        "firms entering in 2020-23 enter with Lift + Cruise, against {tk_coh_w1_tr} of "
        "{tk_coh_w1_n} entering with Tilt Rotor before 2011. The class shift is carried by new "
        "firms, not by firms changing their minds."),
    "atlas_filers": (
        "Filing is spread, not concentrated: the top ten filers hold under a quarter of the "
        "aircraft and the Lorenz curve stays close to the diagonal. {named_companies} named "
        "companies hold {tk_named_share} of the set and the rest is individuals and unattributed "
        "filings, which is why no firm-level result here can stand for the field."),
    "la_class_concentration": (
        "Every class is filed by many firms: the most concentrated ({tk_conc_max}) has its largest "
        "filer holding {tk_conc_max_v}, CVT — the class the author asked about — has its largest "
        "filer on {tk_conc_cvt} and its three largest on {tk_conc_cvt3}, and the named firms "
        "together hold about half of each class, the rest being individual and unattributed "
        "filings. No class in this corpus is one company's product line."),
    "firm_tiles": (
        "A firm appears in one or two windows and leaves: very few firms hold five or more aircraft "
        "in more than one window, so the tiles read as a turnover of firms rather than a race "
        "between them. The class a firm files most is its portfolio's centre, not its product."),
    "a2_d8_filer_mix": (
        "Named companies file {named} of the {primary_s} primary patents — under half. The "
        "non-corporate majority ({non_corporate_share}) is the reason this document reports "
        "individuals and unattributed filings beside firms everywhere instead of dropping them."),
    "a2_d8_concentration": (
        "Concentration is an artefact of name cleaning, not a fact about the field: an HHI of "
        "{hhi_raw} on the raw assignee strings is near-zero, and canonicalising the names moves the "
        "largest filer from {bell_raw} to {bell} patents. Always read the canonical column."),
    "transitions": (
        "Firms repeat themselves: a firm's next aircraft is in the same class in {tk_trans_same} of "
        "the {tk_trans_pairs} consecutive pairs ({tk_trans_share}), far more than the twelve class "
        "shares would give by chance. Firms are not exploring the design space — they are deepening "
        "one part of it."),
    "ip_strategy": (
        "Depth and breadth do not go together: the firms with the most patents per aircraft "
        "({tk_ip_max_ppa}, {tk_ip_max_ppa_v}) are not the firms with the widest class mix, and the "
        "range runs down to {tk_ip_min_ppa_v} for {tk_ip_min_ppa}. There is no single IP strategy "
        "in this corpus to describe."),
    "la_ip_strategy": (
        "Patents per aircraft spans {tk_ip_min_ppa_v} to {tk_ip_max_ppa_v} across the same set of "
        "firms, and self-citation varies just as widely. The column to read is self-citation: a high "
        "value means the firm's forward citations are its own filings, so its apparent influence is "
        "internal."),
    "spans_by_firm": (
        "Re-filing is small enough to ignore in the window counts: {sp_repeat} of the {unique_s} "
        "aircraft are filed more than once, {sp_multiwin} of them across a window boundary. The "
        "two-count check moved no class share by more than {sp_maxdiff}."),
    "la_ip_by_class": (
        "Citations follow age, not class: the older classes (Tilt Rotor {tk_ipc_tr_cit} median "
        "forward citations) sit above the newer ones (Lift + Cruise {tk_ipc_slc_cit}) while median "
        "claims barely differ ({tk_ipc_tr_claims} against {tk_ipc_slc_claims}). Do not read this "
        "table as impact per architecture."),
    "proximity_region": (
        "Region does not organise the design choices: firms in different regions are as close in "
        "architecture profile as firms in the same region ({tk_prox_diff} against {tk_prox_same} "
        "mean proximity over {tk_prox_pairs} pairs). Whatever drives a firm's class mix, it is not "
        "where the firm is."),
    "a2_d14_firm_proximity": (
        "The closest pairs are firms with the same two-class portfolio ({px_top_pair}, "
        "{px_top_val}), and the closeness collapses when the propulsor count is added "
        "({px_top_rot}). Similarity at class level is mostly the coarseness of the class."),
    "la_proximity_region": (
        "The same-region and different-region means are {tk_prox_same} and {tk_prox_diff} over "
        "{tk_prox_pairs} pairs — a difference far smaller than the spread within either group, so "
        "this table is a null result and should be reported as one."),
    "ari": (
        "The firms the market rates are not the firms that patent most: the index firms in the "
        "corpus hold a handful of aircraft each while the largest filer is not on the index at all. "
        "Market standing and patent volume are close to independent here ({tk_ari_rho_air}, "
        "p {tk_ari_p_air})."),
    "la_ari_firms": (
        "Index score does not track anything on the patent side: Spearman rho against unique "
        "aircraft is {tk_ari_rho_air} (p {tk_ari_p_air}) over the listed firms. Funding is the "
        "column that does correlate — with the breadth of the class mix ({tk_ari_rho_cls} on "
        "{tk_ari_n_fund} firms) — which is the finding worth carrying forward."),
    "ari_history": (
        "The index moves with funding rounds and announcements, not with filings, and the corpus "
        "side of the panel is a handful of aircraft per firm. Read the right-hand panel as a "
        "sample of {tk_ari_timeline_n} firms, not as the field."),
    "ari_clock": (
        "The patent clock runs years ahead of the market clock: the index firms file first and fly "
        "later, and several have stopped filing before their stated entry into service. Patenting "
        "marks the start of a programme, not its maturity."),
    "la_ari_correlation": (
        "Only one correlation in this table survives its own p value — funding against the breadth "
        "of a firm's class mix ({tk_ari_rho_cls} on {tk_ari_n_fund} firms) — and funding against "
        "first priority year ({tk_ari_rho_year}) says the better-funded firms started earlier. The "
        "score itself explains nothing."),
    "la_ari_timeline": (
        "First flight comes four to six years after the first patent for most of the "
        "{tk_ari_timeline_n} firms, and the last patent usually precedes it. The patent record is a "
        "leading indicator with a multi-year lead, which is the argument for using it at all."),
    "la_trl_placeholder": (
        "Nothing is measured here yet: the TRL ranking is the author's separate work and is not "
        "installed. Until it is, this document cannot say whether the architectures that patent "
        "most are the architectures that fly."),
    "la_filer_mix": (
        "The two units agree, and both say the same uncomfortable thing: named companies hold "
        "{tk_fm_named_air} of the {unique_s} aircraft ({tk_fm_named_share}) and "
        "{tk_fm_named_pat} of the primary patents, while individual inventors hold "
        "{tk_fm_ind_air} aircraft. It does not matter whether a statement is made per patent or "
        "per aircraft — either way, under half the corpus belongs to a firm."),
    "la_cohort_mix": (
        "The class shift is led by who enters, not by who changes: {tk_cm_e_slc} of the firms "
        "entering in 2020-23 arrive with Lift + Cruise against {tk_cm_a_slc} of that window's "
        "aircraft. Entrants over-index on the class of their moment, which is what makes 4.1.2 a "
        "population effect rather than a set of firms redesigning."),
    # ``filer_weight`` and ``la_class_filer_weight`` are entered above, with Figure 4.1.9b
    "la_firm_leverage": (
        "Every class share in this document survives the loss of any one firm: the largest effect "
        "is {tk_lev_firm}, whose removal moves the {tk_lev_class} share by {tk_lev_pp} points, and "
        "every other firm moves it less. This is the direct answer to 'is that bar one company' — "
        "it is not."),
    "firm_influence": (
        "No single firm decides a class share: dropping {tk_lev_firm}, the largest filer in the "
        "corpus, moves the {tk_lev_class} share by {tk_lev_pp} points and no other firm moves any "
        "share further. Read the within-window column before concluding the same of one bar."),

    # ================================================================ 4.3
    "atlas_region": (
        "Three countries hold almost two thirds of the corpus (US {tk_us_n}, CN {tk_cn_n}, DE "
        "{tk_de_n} of {unique_s} aircraft), so every regional statement in this document is really "
        "a statement about those three. Every other country stays under 25 aircraft and cannot "
        "carry a class share."),
    "region_grid": (
        "One regional difference survives: North America keeps tilting architectures in every "
        "window while Europe and Asia-Pacific sit well below it, and the US files {tk_us_tr} Tilt "
        "Rotor against China's {tk_cn_tr}. Propulsor counts rise in all three regions together, so "
        "that is a field-wide drift and not a regional choice."),
    "region_grid_b": (
        "Powertrain and ducting say nothing by region — the shares move without direction and the "
        "cells are small — but filer type does: North America is the region of named companies "
        "while Asia-Pacific carries the universities. If one panel of this pair is kept, keep the "
        "filer-type one."),
    "specialisation": (
        "Specialisation is real but modest: most archetypes sit between 0.6 and 1.5 in every region, "
        "with two clear exceptions — the small tilt rotor is North American ({tk_spec_tr03_na}) and "
        "the winged multirotor is European ({tk_spec_ptc_eu} against {tk_spec_ptc_na} in North "
        "America). Everything else is close to proportional."),
    "la_specialisation": (
        "An index near 1.0 means the region files that archetype in proportion to its size, and "
        "most cells are near 1.0. Read only the rows built on twenty or more aircraft; below that "
        "the index swings on two or three patents."),
    "country_class": (
        "The two largest countries build different things: the US is the tilt-rotor country "
        "({tk_us_tr} of its {tk_us_n} aircraft, against {tk_us_slc} lift + cruise) and China the "
        "lift + cruise one ({tk_cn_slc} of {tk_cn_n}). Japan is the most one-sided of the mid-size "
        "countries ({tk_jp_slc})."),
    "la_country_class": (
        "Below the top three countries every row rests on twenty to thirty aircraft, so a share of "
        "0.1 is two or three patents. The table is readable for US, CN and DE and is illustrative "
        "for the rest."),

    # ================================================================ 5
    "atlas_powertrain": (
        "Powertrain is not a discriminator in this corpus: {tk_pw_el} of the aircraft are electric "
        "and the class differences are small, with hybrid concentrated in the classes that carry a "
        "wing (Tilt Wing {tk_pw_tw_hy} of {tk_pw_tw_n}). {tk_pw_ns} aircraft state nothing at all."),
    "la_powertrain_by_class": (
        "The not-stated column is the finding: {tk_pw_ns} aircraft ({tk_pw_tr_ns} of them Tilt "
        "Rotor) never say what drives them. Hybrid is a wing-class choice — Tilt Wing declares it "
        "for {tk_pw_tw_hy} of {tk_pw_tw_n} aircraft, Lift + Cruise for a far smaller share of "
        "{tk_pw_slc_n}."),
    "atlas_units": (
        "There is no standard number of propulsors: the median is {units_median} and the five bins "
        "hold {bin_r03}, {bin_r4}, {bin_r56}, {bin_r78} and {bin_r9} aircraft — the flattest "
        "distribution in the label set. The convergence is in the arrangement instead: {grp2} of "
        "{units_n} aircraft put their units on exactly two stations."),
    "atlas_design_heatmaps": (
        "The pairs are not free choices: one wing is the default and {tk_gear_unknown} of the "
        "aircraft do not draw a landing gear at all, so most cells are empty by construction. Only "
        "class against tail type carries information here; the rest repeats the class."),
    "atlas_state_by_arch": (
        "The figures draw end states, not the transition: of {tk_state_n} approved figures the "
        "transition is drawn in a small minority and the largest group is invariant geometry. "
        "Nothing in this corpus is evidence about how a transition is flown."),
    "a2_d2_figure_slot_answers": (
        "The image set is visually uniform — monochrome line drawings on a solid ground, every "
        "approved figure a whole-vehicle view, {tk_state_n} of them. A model trained on these sees "
        "geometry and nothing else, which is a strength for comparison and a limit for anything "
        "about scale, material or finish."),
    "la_class_fold": (
        "The fold is lossy in one direction only: {tk_fold_vt} aircraft from six G1 classes collapse "
        "into the directory's single Vectored Thrust class, while Lift + Cruise maps one-to-one "
        "({tk_fold_lc}). Any comparison with evtol.news is therefore blind to the distinctions this "
        "codebook was built to make."),
    "la_mission_capacity": (
        "Capacity is not recoverable at corpus scale: {tk_cap_ns} of the {tk_cap_tot} linked "
        "aircraft state none, and the largest stated group is {tk_cap_34} at three to four seats. "
        "This is a description of the linked sample, not of the corpus."),
    "la_mission_piloting": (
        "Piloting is mostly unstated or optional — {tk_pil_ns} not stated and {tk_pil_either} "
        "explicitly either — so autonomy cannot be used as a variable anywhere in this document."),
    "la_mission_power source": (
        "The directory's power source agrees with the patent reading: battery electric dominates "
        "({tk_pow_batt} of the linked aircraft) and hydrogen is marginal ({tk_pow_h2}). It confirms "
        "the electric gate rather than adding to it."),
    "la_mission_status": (
        "The linked aircraft are early-stage: {tk_st_concept} are concept designs against "
        "{tk_st_prod} in production, and {tk_st_defunct} are already defunct. A patent in this "
        "corpus is far more likely to describe a concept than a product."),
    "la_mission_agreement": (
        "Where both sides name a class they agree: the folded patent label matches the directory's "
        "own class for {tk_agree_vt} vectored-thrust and {tk_agree_lc} lift + cruise aircraft, with "
        "{tk_agree_lc_vt} lift + cruise aircraft the directory calls vectored thrust. The figures "
        "and the public record describe the same aircraft."),
    "mission": (
        "The linked aircraft are a small, early-stage and self-selected sample — those with a public "
        "page — so its mission answers describe that sample, not the corpus. What it does establish "
        "is that the figure-based class agrees with the directory's class where both exist."),
    "industry_by_class": (
        "The named application does not separate the classes: {tk_ind_gen} aircraft are unspecified "
        "and the rest spread the same way in every class. Patents do not commit to a mission, which "
        "is the finding — not the small differences between the bars."),
    "la_industry_by_class": (
        "{tk_ind_gen} of the aircraft name no application at all, {tk_ind_slc_gen} of them in Lift + "
        "Cruise alone ({tk_ind_slc_n} aircraft). Recreation ({tk_ind_rec}) outweighs urban air "
        "mobility ({tk_ind_uam}) in the text, which is a property of what patents say, not of what "
        "firms build."),
    "examination": (
        "Examination outcome is an office effect, not a technology effect: {tk_ex_us_gr} of the "
        "{tk_ex_us_n} US patents are granted and in force against {tk_ex_cn_gr} of {tk_ex_cn_n} at "
        "the CNIPA, with {tk_ex_cn_ref} refusals there and none in the US set. The class panel shows "
        "no such split."),
    "la_examination_office": (
        "The offices behave differently on the same corpus: {tk_ex_us_gr} of {tk_ex_us_n} in force "
        "in the US against {tk_ex_cn_gr} of {tk_ex_cn_n} in China, where most filings are still "
        "pending, withdrawn or refused. Use office status to compare offices, never designs."),
    "la_examination_class": (
        "The classes sit at the same grant rate ({tk_exc_slc_gr} of {tk_exc_slc_n} for Lift + "
        "Cruise, {tk_exc_tr_gr} of {tk_exc_tr_n} for Tilt Rotor), so examination gives no signal "
        "about which architecture an office finds novel."),
}


def _tk_float(value) -> Optional[float]:
    """A number out of a printed cell, or ``None`` — thousands spaces and commas included."""
    try:
        return float(str(value).replace(",", "").replace(" ", "").replace(" ", "").rstrip("%"))
    except (TypeError, ValueError):
        return None


def _tk_fmt(value, fmt: str) -> Optional[str]:
    """One cell as the takeaway prints it. ``None`` when the value cannot carry the format,
    so the placeholder is dropped rather than printed wrong."""
    if value is None or str(value).strip().lower() in ("", "nan", "none", "<na>"):
        return None
    if fmt == "raw":
        return str(value).strip()
    x = _tk_float(value)
    if x is None:
        return None
    if fmt == "int":
        return f"{round(x):d}"
    if fmt == "1f":
        return f"{x:.1f}"
    if fmt == "2f":
        return f"{x:.2f}"
    if fmt == "pct":
        p = x * 100.0
        if abs(p) >= 10:
            s = f"{p:.0f}"
        elif abs(p) >= 1:
            s = f"{p:.1f}".rstrip("0").rstrip(".")
        else:
            s = f"{p:.2f}".rstrip("0").rstrip(".")
        return f"{s} %"
    return str(value).strip()


def _tk_number(spec: Dict, tables: Optional[Dict]) -> Optional[str]:
    """One :data:`TAKEAWAY_NUMBERS` spec against the built tables. Any failure returns
    ``None`` and the placeholder is dropped — a takeaway never prints a guessed number."""
    frame = (tables or {}).get(spec.get("table"))
    if frame is None:
        return None
    try:
        recs = frame.to_dict("records")
    except Exception:
        return None
    if not recs:
        return None
    how = spec.get("how", "value")
    fmt = spec.get("fmt", "raw")
    if how == "rows":
        return _tk_fmt(len(recs), fmt)

    def _sel(rows, where):
        if not where:
            return rows
        pairs = [where] if isinstance(where, tuple) else list(where)
        for col, val in pairs:
            rows = [r for r in rows if str(r.get(col, "")).strip() == str(val).strip()]
        return rows

    sel = _sel(recs, spec.get("where"))
    col = spec.get("col")
    try:
        if how == "count":
            return _tk_fmt(len(sel), fmt)
        if how == "count_ge":
            n = sum(1 for r in sel
                    if (_tk_float(r.get(col)) or float("-inf")) >= float(spec["at_least"]))
            return _tk_fmt(n, fmt)
        if not sel:
            return None
        if how == "sum":
            vals = [x for x in (_tk_float(r.get(col)) for r in sel) if x is not None]
            return _tk_fmt(sum(vals), fmt) if vals else None
        if how == "share":
            num = [x for x in (_tk_float(r.get(col)) for r in sel) if x is not None]
            den = [x for x in (_tk_float(r.get(col)) for r in _sel(recs, spec.get("over"))) if x is not None]
            return _tk_fmt(sum(num) / sum(den), fmt) if num and sum(den) else None
        if how in ("max", "min"):
            pairs = [(x, r) for r in sel for x in [_tk_float(r.get(col))] if x is not None]
            if not pairs:
                return None
            row = (max if how == "max" else min)(pairs, key=lambda p: p[0])[1]
            return _tk_fmt(row.get(spec.get("out", col)), fmt)
        return _tk_fmt(sel[0].get(col), fmt)                     # how == "value"
    except Exception:
        return None


def takeaway(name: str, values: Optional[Dict] = None, kind: str = "figure",
             tables: Optional[Dict] = None) -> str:
    """The second grey line under figure or table ``name``: what the reader should conclude.

    ``name`` is the internal key, so the line follows the item through a renumbering. An item
    with no :data:`TAKEAWAY` entry, or one still set to :data:`NOT_YET`, prints the marker so
    the gap is visible to the author instead of being filled with an invented sentence.
    """
    text_ = TAKEAWAY.get(name)
    if not text_ or text_ == NOT_YET:
        return NOT_YET
    vals = dict(values or {})
    for key, tname in N_FROM_TABLE.items():                      # shared with the provenance line
        frame = (tables or {}).get(tname)
        if frame is not None:
            vals[key] = len(frame)
    for key, spec in TAKEAWAY_NUMBERS.items():
        if ("{" + key + "}") not in text_:                       # only what this line asks for
            continue
        got = _tk_number(spec, tables)
        if got is not None:
            vals[key] = got
    line = _clean(_pa._fill(str(text_), vals))
    if not line:
        return NOT_YET
    return line if line[-1:] in ".!?" else line + "."


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
