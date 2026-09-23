"""The structure and prose of the Preliminary Analysis, held as data.

The document follows the rewrite spec of 2026-09-13 (``PRELIM_REWRITE_SPEC.md``):
four chapters, three numbering levels (``2.1``, ``2.1.1``), every table and
figure named by the subsection that owns it. Each node below carries the prose
of one heading as a template whose ``{placeholders}`` are filled from
:func:`numbers.live`, the tables and figures it shows, and the notebook code that
produces them. Change the wording here and the notebook, the draft and the PDF
all follow.
"""

from __future__ import annotations

from typing import Dict, List, Optional

TITLE = "Preliminary Analysis — the labelled eVTOL patent data set"

#: caption of every table the document prints, by table name
TABLE_CAPTIONS: Dict[str, str] = {
    "a2_d1_rejection_reasons": "Why a patent is not representative",
    "a2_d1_similars": "The similars: near misses of the domain, how each is caught, and what happened to it",
    "a2_d9_publication_lag_region": "Priority-to-publication lag, years, three main regions",
    "a2_d1_filing_status": "Filing status at the three patent levels",
    "a2_d7_duplicates": "The same aircraft in several patents: observations (O1, O2) and similars (S3)",
    "a2_d7_aircraft_per_patent": "Aircraft drawn per primary patent",
    "a2_d11_figure_approval": "Figure approval and what the approved figures show",
    "a2_d8_filer_mix": "Who filed the primary patents",
    "a2_d8_concentration": "Concentration of filing, raw assignee string against canonical company",
    "a2_d9_windows": "Candidate windows and the unique aircraft each holds",
    "a2_d2_figure_slots": "The figure-level (T2) slots over the approved figures",
    "a2_d11_figures_per_variant": "Approved figures behind each unique aircraft",
    "a2_d2_figure_slot_answers": "Most common answers of the T2 slots",
    "roster_summary_short": "Evidence and labelling flags on the unique aircraft",
    "a2_d2_label_set": "The label set and the slots answered per aircraft",
    "a2_d4_missingness": "Blanks where the parent field says the part exists; values an override hides are left out",
    "a2_d3_selected_fields": "Most common answers, G1 to M3 fields",
    "a2_d2_informative_fields": "Field inventory, ranked by effective number of answers",
    "a3_derived_layer_summary": "Derived per-aircraft features, each with the aircraft it is counted over",
    "a2_d5_archetype_cardinality": "Archetype cardinality at five levels",
    "a2_d9_architecture_by_window": "Class shares per window, four largest classes",
    "a2_d13_flagship_check": "Flagship check: labels of the largest filers against their public products",
    "ch5_settings": "What the preliminary analysis fixes for the evolution analysis",
    "ch5_judgement": "The three choices that rest on the author's judgement",
}

#: caption of every figure, by figure name
FIGURE_CAPTIONS: Dict[str, str] = {
    "fig_01_document_pipeline": "the document, chapter by chapter, one way",
    "fig_02_refinement_funnel": "the acquisition and refinement funnel",
    "provenance_bars": "acquired and representative patents by region and by publication office",
    "patents_per_year": "representative primary patents per priority year, with the candidate windows",
    "fig_03_design_space_order": "the four label cards of one unique aircraft, and the order of the design-space analysis",
    "fill_rate_heatmap": "fill rate of each field, conditional on the parent part being present; a value an override hides is left out",
    "archetype_levels": "the two columns that pick the archetype level",
    "class_balance_bars": "architecture class balance; the white bar is the aircraft a G1 override leaves without a type",
    "class_share_stacked_area": "class shares per window; the partial window is hatched",
    "slots_histogram": "slots answered per unique aircraft",
    "lorenz": "concentration of filing",
    "fig_05_handover": "the handover: what each result of chapters 2 to 4 gives to each step of the method",
}

#: figure width in the document, fraction of the text width
FIG_WIDTH: Dict[str, str] = {
    "fig_01_document_pipeline": "92%", "fig_02_refinement_funnel": "92%",
    "fig_03_design_space_order": "92%", "fig_05_handover": "92%", "provenance_bars": "84%",
    "patents_per_year": "78%",
    "fill_rate_heatmap": "54%", "archetype_levels": "84%", "class_balance_bars": "56%",
    "class_share_stacked_area": "66%", "slots_histogram": "56%", "lorenz": "36%",
}

#: row caps and column subsets for the document (the CSV always holds everything)
ROW_CAP: Dict[str, int] = {"a2_d13_flagship_check": 8, "a2_d9_publication_lag_region": 3,
                           "a2_d2_informative_fields": 12}
COLUMNS: Dict[str, List[str]] = {
    "a2_d2_figure_slots": ["name", "field", "answered", "answers", "top_share", "effective_answers"],
    "a2_d2_informative_fields": ["name", "card", "answered", "answers", "top_share",
                                 "effective_answers", "top2_cumulative", "top3_cumulative"],
    "a2_d5_archetype_cardinality": ["level", "fields combined", "aircraft", "left out", "distinct archetypes",
                                    "singletons", "effective number"],
}

# --------------------------------------------------------------------------
# the nodes, in document order. depth = number of dots in the id.
# --------------------------------------------------------------------------
NODES: List[Dict] = [
    # ================================================================ 1
    dict(id="1", title="Introduction",
         figures=["fig_01_document_pipeline"],
         text=(
             "This document is the first pass over the labelled eVTOL patent data set: what was "
             "acquired, what survived each refinement, and how the labels spread. Every number in "
             "it is computed from the consolidated master sheet (Stage 04), which joins the five "
             "batch exports with the identity review. A review of several labelling decisions is "
             "still open, so some counts will move; the structure of the analysis does not depend "
             "on which way they move.\n\n"
             "Chapter 2 settles what enters and at which level. Three refinements take "
             "{acquired_s} acquired patents to {representative_s} representative patents, "
             "{unique} unique aircraft and {figures_approved_s} whole-aircraft figures. It comes first "
             "because every later count is a count of something it defines.\n\n"
             "Chapter 3 describes the data set one level at a time: provenance at the patent "
             "level, the drawing labels at the image level and the design space at the "
             "unique-aircraft level. It comes second because its tables are the spread the next "
             "chapter judges.\n\n"
             "Chapter 4 asks whether the labels can be trusted. For now it compares what is "
             "already known publicly with what the methodology recovered. Validity can only be "
             "judged once the spread of the labels is known, which is why it follows chapter 3.\n\n"
             "Chapter 5 specifies the design space and evolution analysis. It comes last because "
             "every setting it fixes is a value read from a table of chapters 2 to 4.\n\n"
             "**Levels of analysis.** The document works at three levels and every section states "
             "which one it uses before its first table: the patent ({acquired_s} acquired, "
             "{representative_s} representative), the unique aircraft ({unique}) and the image "
             "({figures_approved_s} approved whole-aircraft figures). A statistic computed at one "
             "level does not "
             "transfer to another.\n\n"
             "**Terms.** A *representative patent* shows an eVTOL aircraft **and** that aircraft "
             "can be read from its figures, where eVTOL means electric, vertical take-off and "
             "occupied: an aircraft the review tagged as UAV-similar, not electric or STOL-only "
             "is near the boundary but outside it, and leaves. *Granted* and *pending "
             "application* are the office's words and never describe representativity. A *unique "
             "aircraft* is one design, however many patents draw it. The same aircraft seen again "
             "is an *observation* (O1 with new figures, O2 with the same figures); a *similar* "
             "(S3) is a different aircraft and is counted as one new unique aircraft."),
         code=[]),
    # ================================================================ 2
    dict(id="2", title="eVTOL Data Sets: Acquisition and Refinement",
         figures=["fig_02_refinement_funnel"],
         text=("Three refinements, each at its own level, take the acquired patents to the "
               "analysis set. Refinement 1 decides which patents represent the domain, "
               "refinement 2 turns patents into unique aircraft, refinement 3 decides which "
               "figures the labels rest on."),
         code=[]),
    dict(id="2.1", title="Refinement 1 — representativity", level="patent",
         text=("A patent is representative when it shows an eVTOL aircraft and the aircraft can "
               "be read from its figures. The test is applied in two steps. At labelling, "
               "{disapproved_wizard} of the {acquired_s} acquired patents are disapproved: no "
               "aircraft image, or an aircraft plainly outside the domain; {wizard_approved_s} "
               "({wizard_share}) are approved. The identity review then reads the text of every "
               "approved patent for what a drawing cannot show, occupancy, powertrain and take-off "
               "mode, and marks the near misses with a tag: UAV-similar, electric-similar, "
               "STOL-similar. A tagged aircraft leaves the analysis set. {gated_patents} approved "
               "patents lose every aircraft this way, so {representative_s} ({rep_share}) are "
               "representative."),
         code=[]),
    dict(id="2.1.1", title="Disapproval reasons",
         text=("The two largest reasons at labelling are the two conditions themselves: no "
               "aircraft image ({r_noimg}) and a domain miss (pure UAV {r_uav}, out of domain "
               "{r_ood}); the remaining {r_other} are marginal. The review adds the tagged "
               "near misses: UAV-similar {r_sim_uav}, not electric {r_sim_el}, STOL-only "
               "{r_sim_stol}."),
         tables=["a2_d1_rejection_reasons"],
         code=["display(a2.d1_funnel(ds))", "display(a2.d1_approval_by_region(ds))",
               "a2.d1_rejection_reasons(ds)"]),
    dict(id="2.1.2", title="The similars: UAV-similar, STOL-similar, electric-similar",
         text=("Three kinds of near miss sit next to the boundary and each is caught by a "
               "different mechanism, all of them from the text, because neither occupancy nor "
               "powertrain nor take-off mode can be read from a drawing. Each tag names an "
               "aircraft, not a patent: a patent that draws several aircraft keeps the ones "
               "without a tag. The tags remove {gated_aircraft} unique aircraft "
               "({uav_primary} UAV-similar, {notel_primary} electric-similar, "
               "{stol_rep} STOL-only; an aircraft can carry two tags). What stays is "
               "deliberate: V/STOL, where the text claims "
               "both modes, is a vertical take-off aircraft ({vstol_n} patents); a hybrid "
               "powertrain has electric motors ({hybrid_el}); and where the text gives no "
               "powertrain evidence either way ({unknown_el} patents) the aircraft stays, because "
               "silence is not a turbine."),
         tables=["a2_d1_similars"],
         code=["a2.d1_similars(ds)"]),
    dict(id="2.1.3", title="Publication lag",
         text=("A patent enters the corpus only when it publishes. The median lag from priority "
               "to publication is {lag_median_lo} to {lag_median_hi} years and the 90th percentile "
               "{lag_p90} in the three main regions, so priority years to {complete_to} are "
               "complete, the year after nearly, and {partial_start} onwards is truncated. Every "
               "trend statement ends at {complete_to} and the last window is drawn as partial. "
               "Priority year is the time axis because it is the date closest to the design "
               "decision."),
         tables=["a2_d9_publication_lag_region"],
         code=["display(a2.d9_publication_lag(ds, 'region'))", "a2.d9_publication_lag(ds, 'pub_office')"]),
    dict(id="2.1.4", title="Filing status",
         text=("Granted and pending are the office's decision on the claims, not on the drawing, "
               "so they do not touch representativity. The analysis runs on every representative "
               "patent; filing status is carried as a stratum. Of the {primary} primary patents, "
               "{granted_pri} were granted, {pending_pri} are pending applications and "
               "{withdrawn_pri} were withdrawn, refused or suspended."),
         tables=["a2_d1_filing_status"],
         after=("Refusal and withdrawal are legal or procedural outcomes (novelty, inventive "
                "step, clarity, unpaid fees), not a verdict on the aircraft drawn. Hence:\n\n"
                "- **Pool everything, carry status as a stratum.**\n"
                "- **Do not filter to granted.** Status is confounded with filing year.\n"
                "- **Use it as a robustness check, not a filter.** Filing status against "
                "top-level architecture.\n"
                "- **Sensitivity line.** Headline counts repeated on the {granted_pri} granted "
                "primaries.\n"
                "- **Status is a snapshot** at the acquisition date."),
         code=["a2.d1_filing_status(ds)"]),
    dict(id="2.2", title="Refinement 2 — observations to unique aircraft",
         level="patent → unique aircraft",
         text=("The {representative_s} representative patents hold {observations_s} aircraft "
               "observations. Observations of an aircraft already in the set are removed, and a "
               "patent that draws several aircraft contributes one row per aircraft. The result "
               "is {unique} unique aircraft on {primary} primary patents."),
         code=[]),
    dict(id="2.2.1", title="Same unique aircraft in different patents: O1, O2, S3",
         text=("O1 and O2 are the same aircraft seen again; their labels are inherited from the "
               "original and they add no unique aircraft. S3 is a similar aircraft, relabelled in "
               "full, and counts as one new unique aircraft. {s3_identical} of the {s3} S3 rows "
               "are identical to their original on all seven archetype fields; that double-count "
               "is kept as a sensitivity run."),
         tables=["a2_d7_duplicates"],
         code=["display(a2.d7_duplicates(ds))", "pd.Series(a2.d7_d3_identical_to_root(ds)).to_frame('value')"]),
    dict(id="2.2.2", title="Different unique aircraft in the same patent",
         text=("{multi_patents} of the {primary} primary patents draw more than one aircraft, up "
               "to {max_aircraft}; each is a row of its own."),
         tables=["a2_d7_aircraft_per_patent"],
         code=["a2.d7_aircraft_per_patent(ds)"]),
    dict(id="2.3", title="Refinement 3 — figure approval", level="unique aircraft → image",
         text=("Each figure of a representative patent is approved or not on its own, and of "
               "the approved figures only those that show the whole aircraft are analysed. "
               "{figures_approved_all_s} figures are approved; {figures_approved_s} show the "
               "whole aircraft and form the image set; the other {detail_figs} are detail figures "
               "approved on purpose (tilt mechanism, rotor), kept on record and not analysed. "
               "Every image-level count in this document, and the number of figures behind each "
               "aircraft, is taken on the whole-aircraft figures."),
         code=[]),
    dict(id="2.3.1", title="Reasons to approve a figure, and the resulting count",
         text=("A figure is approved when it shows the aircraft in a view the architecture can be "
               "read from. The {representative_s} representative patents hold {figures_total_s} "
               "figures with an image file; {figures_approved_all_s} pass; {whole_vehicle_s} of "
               "them show the whole vehicle and "
               "enter the analysis, the other {detail_figs} are detail figures approved on purpose "
               "(tilt mechanism, rotor) and are set aside."),
         tables=["a2_d11_figure_approval"],
         code=["display(a2.d11_figure_approval(ds))", "a2.d11_figure_quality(ds)"]),
    dict(id="2.3.2", title="Why {fig_patents} patents carry figures and only {primary} are primary records",
         text=("{fig_patents} patents carry approved figures but only {primary} are primary "
               "records. {o1_fig_patents} are O1 observations, which bring new figures of an "
               "aircraft already in the set{odd_note}. The counts are in "
               "`tables/a2_d11_figure_patents.csv`."),
         code=["a2.d11_figure_patents(ds)"]),
    # ================================================================ 3
    dict(id="3", title="Data Set Analysis by Level",
         text=("One level at a time: the patent for provenance, the image for the drawing "
               "labels, the unique aircraft for the design space."),
         code=[]),
    dict(id="3.1", title="Provenance", level="patent", code=[]),
    dict(id="3.1.1", title="Region, assignee country, publication office",
         text=("North America supplies {na_share} of the acquired patents and has the highest "
               "representative share ({na_rep_share}); Asia-Pacific and Europe are acquired in "
               "similar numbers but less often show a whole aircraft ({ap_rep_share}, "
               "{eu_rep_share}). The query behaves differently by office, so region is reported "
               "next to later statistics as a stratum and never used as a filter."),
         figures=["provenance_bars"],
         code=["prov = a1.provenance_tables(ds)", "display(prov['region'])",
               "display(prov['assignee_country'])", "prov['pub_office']"]),
    dict(id="3.1.2", title="Who filed, and how concentrated it is",
         text=("The three rows of the first table are read as follows. *Individual inventors* "
               "are patents whose assignee is a person rather than an organisation, as the "
               "identity stage resolved it ({individual}). *Unattributed or independent* holds "
               "the patents with no assignee string, or one that resolves to no known company "
               "({unattributed}). *Named companies* are the {named_companies} firms of the "
               "canonical company column; a firm is counted once across every assignee string it "
               "files under, which is why Bell / Textron is {bell} patents on the canonical "
               "column and {bell_raw} on its largest raw string. {non_corporate_share} of the "
               "corpus is not corporate, and concentration is mild (HHI {hhi_raw} on the raw "
               "string), so pseudo-replication matters mainly where one firm dominates a class. "
               "Name proposals exist for {names} patents ({gazetteer} from a company gazetteer, "
               "{sbert} from the text); none is verified, and a company-attributed name is a "
               "statement about the assignee, not about the drawing."),
         tables=["a2_d8_filer_mix", "a2_d8_concentration"],
         code=["display(a2.d8_filer_mix(ds))", "display(a2.d8_concentration(ds))",
               "display(a2.d8_split_firms(ds, 'Bell / Textron'))", "a5.name_proposals(ds)"]),
    dict(id="3.1.3", title="Publication timeline, overall and per region",
         text=("Per-year counts before 2016 are too small for per-year statistics, so the "
               "analysis uses windows of three to five years, rarefied to about 40 aircraft each; "
               "the smallest complete window holds {min_window}. The {partial_start}–26 window is "
               "partial: it is drawn hatched and labelled, never dropped."),
         figures=["patents_per_year"], tables=["a2_d9_windows"],
         code=["display(a1.time_coverage_summary(ds))",
               "a2.d9_architecture_by_window(ds)[['window', 'unique aircraft']]"]),
    dict(id="3.2", title="Image analysis", level="image, T2 labels", code=[]),
    dict(id="3.2.1", title="Answerable slots at image level",
         text=("Every approved figure carries {t2_slots} T2 slots. They describe the drawing, not "
               "the design (perspective, style, colour, background, what is shown, flight state), "
               "and they are the confounds the embedding pillar has to control for. Only "
               "perspective and flight state vary; the rest are near-constant."),
         tables=["a2_d2_figure_slots"],
         code=["a2.d2_figure_slots(ds)"]),
    dict(id="3.2.2", title="Figure basis of each label",
         text=("The labels of a unique aircraft rest on a median of {median_figs} approved "
               "figures; {single_fig} ({single_share}) rest on one, which defines the "
               "single-figure flag. Every primary patent shows at least one whole aircraft, the "
               "inclusion criterion the labelling enforced."),
         tables=["a2_d11_figures_per_variant"],
         code=["display(a2.d11_figures_per_variant(ds))", "pd.Series(a2.d11_sensitivity_set(ds)).to_frame('value')"]),
    dict(id="3.2.3", title="Most common answers, T2 labels",
         text=("Most figures are monochrome line drawings on a plain background, seen from the "
               "front-isometric, and drawn Invariant or in hover."),
         tables=["a2_d2_figure_slot_answers"],
         after=("How to read the flight state: Hover, Transition and Cruise are read from the angle of "
                "the moving part. Invariant means nothing in the drawing depends on the configuration. "
                "Both means the moving part is drawn in two positions with equal weight. Other means no "
                "configuration can be read. A part drawn solid in one position and dashed in the other "
                "is recorded as the solid one. The six states are counted apart and never pooled."),
         code=["from src.dataset_facts.atlas import table_caption", "display(a2.d2_figure_slot_answers(ds))", "display(Markdown(table_caption(ds, 't2_answers')))"]),
    dict(id="3.2.4", title="Evidence flags",
         text=("Every flag is about evidence or labelling; nothing in this document is about what "
               "a model can read, which first appears in the DINOv2 chapter. The flagged aircraft "
               "stay in, marked, and every later analysis runs with and without them: {sens} "
               "unique aircraft ({sens_share}) form the thin-evidence set, {noflag} carry no flag "
               "at all. The full roster, one row per unique aircraft with every flag, is "
               "`tables/roster.csv`."),
         tables=["roster_summary_short"],
         code=["ROSTER = roster.analysis_set(ds, PARTIAL)", "print(roster.counts(ROSTER))",
               "roster.summary(ROSTER)"]),
    dict(id="3.3", title="Design space analysis", level="unique aircraft, G1 to M3",
         figures=["fig_03_design_space_order"],
         text=("The design space is read from the four label cards of one unique aircraft, in "
               "the order the figure shows: from completeness to the level at which aircraft are "
               "counted, and on to the first look at movement over time."),
         code=[]),
    dict(id="3.3.1", title="Slots answered per aircraft",
         text=("The {slots} columns of the four label cards G1 to M3 (the coded answers only: option "
               "ids, booleans and counts; free-text notes and the labelling-process flags are not "
               "slots) are slots, not concepts: {concepts} questions repeated over "
               "boom groups, wing panels and propulsor tiers. Sparsity is structural, a slot is "
               "blank when the part does not exist, so an aircraft answers a median of "
               "{median_slots} slots and {slots_lt5} slots are answered on fewer than 5 % of "
               "aircraft. {informative} fields carry the information; {near_constant} are "
               "near-constant."),
         tables=["a2_d2_label_set"],
         code=["display(a2.d2_label_set(ds, near_constant_min_answered=F.get('near_constant_min_answered', 100),",
               "    near_constant_share=F.get('near_constant_share', 0.95),",
               "    informative_min_answered=F.get('informative_min_answered', 300),",
               "    informative_min_effk=F.get('informative_min_effective', 1.5)))",
               "_ = figures.slots_histogram(a2.d2_slots_per_aircraft(ds))"]),
    dict(id="3.3.2", title="Missingness",
         text=("A blank is a labelling gap only where the parent field says the part exists. On "
               "that test nearly every blank is design absence; the three real gaps are wing "
               "height, wing planform and tail type on winged aircraft. No aircraft is dropped "
               "for blanks, and landing gear \"Unknown\" means not drawn, never absent. An override "
               "keeps only what it records: {override_aircraft} aircraft carry a stage override, and "
               "where it hides the parent or the field the value is not determinable, so the aircraft "
               "is left out of that check (at most {d4_left} per check) instead of counted as a gap."),
         tables=["a2_d4_missingness"], figures=["fill_rate_heatmap"],
         code=["from src.dataset_facts.atlas import table_caption", "display(a2.d4_missingness(ds))", "display(Markdown(table_caption(ds, 'd4')))", "display(a2.d6_weak_labels(ds))", "display(Markdown(table_caption(ds, 'd6')))"]),
    dict(id="3.3.3", title="Most common answers, G1 to M3 labels",
         text=("The table covers the aircraft-level labels G1 to M3 only. Which answers dominate "
               "says where the design space has boundaries: one wing, a fixed fuselage, standard "
               "wings, left-right symmetry. Near-constant fields are reported as findings and "
               "then excluded from distances."),
         tables=["a2_d3_selected_fields"],
         code=["display(a2.d3_selected_fields(ds))",
               "a2.d2_near_constant_fields(ds, min_answered=F.get('near_constant_min_answered', 100), min_share=F.get('near_constant_share', 0.95))"]),
    dict(id="3.3.4", title="Field inventory",
         text=("Fields answered on at least 300 aircraft, ranked by effective number of answers; "
               "tail type and architecture class spread widest. The cumulative columns say how "
               "much of a field its two and three most common answers already cover. This is the "
               "shortlist for the distances and the coupling analysis."),
         tables=["a2_d2_informative_fields"],
         code=["a2.d2_informative_fields(ds, min_answered=F.get('informative_min_answered', 300), min_effk=F.get('informative_min_effective', 1.5))"]),
    dict(id="3.3.5", title="Derived per-aircraft features",
         text=("The sparse boom and tier slots become variables every aircraft has: total "
               "propulsor units, any tilting unit, mixed fixed and tilting units, any ducted "
               "unit, all units ducted, and whether the wing carries thrust (rotors on the wing card "
               "and on a wing-attached boom both count). A value that cannot be read is left out, "
               "never read as zero, none or Fixed: the unit total covers {units_n} aircraft and leaves "
               "out {units_left} (hoverbikes and personal flying vehicles have no propulsor card, a G1 "
               "override leaves no type, an overridden station may lack its count); the tilt answer "
               "covers {tilt_base} and leaves out {tilt_left}. A tilting boom is read from the boom "
               "tick."),
         tables=["a3_derived_layer_summary"],
         code=["from src.dataset_facts.atlas import table_caption", "DLS = a3.derived_layer_summary(ds)", "display(DLS)", "display(Markdown(table_caption(ds, 'derived') + f\"  \\nLeft out of the unit total: {DLS.attrs['units_left_out']}. Left out of the tilt answer: {DLS.attrs['left_out']}.\"))", "a3.derived_layer(ds).head()"]),
    dict(id="3.3.6", title="Archetype cardinality",
         text=("An archetype is the string formed by joining the chosen fields; *distinct "
               "archetypes* counts those strings, and the *effective number* is the exponential "
               "of the Shannon entropy of their shares. Two columns decide the level. *Singletons* "
               "counts archetypes holding exactly one aircraft; above roughly five per cent of the "
               "corpus ({five_pct} aircraft) the level has stopped naming kinds of aircraft and "
               "started naming individual ones. The effective number against the distinct count "
               "is the same test from the other side: close together means every archetype is "
               "about equally rare, well apart means a few archetypes carry most of the aircraft, "
               "which is what a design space looks like. The finest level that holds both is "
               "taken. On the current numbers A0 is safe but too coarse to show movement, A1 "
               "holds at {a1_single} singletons in {n_arch}, and A2 fails on both counts. A1b "
               "bins the number of booms because the raw count has {booms_answers} answers and "
               "reads as a measurement rather than a design decision; A1t tests whether the same "
               "resolution is reached through tilt, the feature the architecture classes actually "
               "turn on ({tilt_n} aircraft tilt a unit)."),
         figures=["archetype_levels"], tables=["a2_d5_archetype_cardinality"],
         code=["from src.dataset_facts.atlas import table_caption", "display(a2.d5_archetype_cardinality(ds))", "display(Markdown(table_caption(ds, 'd5')))", "# rule 4 (2026-09-19): raw boom / wing-card fields against the pooled wing-borne pair", "SENS = a3.boom_wing_sensitivity(ds)", "display(SENS['fields'])", "display(SENS['archetypes'])", "display(SENS['neighbours'])", "display(Markdown(table_caption(ds, 'sensitivity')))"]),
    dict(id="3.3.7", title="Architecture class balance",
         text=("{n_classes} classes, the largest ({top_class}) at {top_class_share}: balanced "
               "enough for windows of about 40 aircraft. The {small_classes} classes below twelve "
               "aircraft are the candidates for merging or dropping in the frozen-model chapter. "
               "{unclassifiable} unique aircraft are unclassifiable (G1 override): they carry no type "
               "and are counted beside the classes, never in one."),
         figures=["class_balance_bars"],
         code=["from src.dataset_facts.atlas import table_caption", "display(a2.d3_architecture_balance(ds))", "display(Markdown(table_caption(ds, 'balance')))"]),
    dict(id="3.3.8", title="Class shares per window",
         text=("A first look at a shift from tilt rotor to lift plus cruise, and no class above "
               "{max_window_share} in any window, so raw shares show no dominant design. This is "
               "the pattern the evolution chapter tests, not assumes."),
         tables=["a2_d9_architecture_by_window"], figures=["class_share_stacked_area"],
         code=["windows = a2.d9_architecture_by_window(ds)",
               "print('largest share of any class in any window:', round(windows.attrs['max_share_any_class_any_window'], 2))",
               "windows"]),
    # ================================================================ 4
    dict(id="4", title="Data Quality and Validity",
         text=("For now this chapter compares what is already known publicly against what the "
               "methodology recovered. In the thesis it is done differently."),
         code=[]),
    dict(id="4.1", title="Flagship check",
         text=("Where a company's product is public, the top label agrees with it; the "
               "disagreements are alternative embodiments filed by the same firm, which is itself "
               "a finding. {flagship_companies} companies with two or more aircraft are checked; "
               "the first eight are shown."),
         tables=["a2_d13_flagship_check"],
         after=("An intra-rater re-label, kappa per field on 60 to 100 patents at least four weeks "
                "after the last labelling, is later work and not a result of this document."),
         code=["a2.d13_flagship_check(ds).head(20)"]),
    # ================================================================ 5
    dict(id="5", title="Method for the Design Space and Evolution Analysis",
         figures=["fig_05_handover"],
         text=("The class shares of section 3.3.8 move in one direction across {year_span} "
               "years, from tilt rotor toward lift plus cruise, and at the same time no class "
               "holds more than about a third of any window. Read on their own those two "
               "observations point opposite ways, the first toward a sector settling on an answer "
               "and the second toward one still exploring. Separating them is the work of the "
               "evolution analysis. This chapter specifies that analysis, and names the result in "
               "the preceding chapters that makes each step available."),
         code=[]),
    dict(id="5.1", title="What this document settles",
         text=("An evolution study makes a handful of choices before it computes anything. Which "
               "unit is counted. Which years can be compared. How fine a design species is. Which "
               "fields carry information. What a blank means. Which aircraft rest on thin "
               "evidence. Taken in isolation each is a matter of taste. Taken from the tables of "
               "chapters 2 to 4, each is a matter of record."),
         tables=["ch5_settings"],
         code=["ch5.settings_table(N)"]),
    dict(id="5.2", title="Unit, time axis and windows",
         text=("The unit is the primary representative unique aircraft. Each aircraft enters once. "
               "Metadata belonging to a filing and not to a design, such as citations and legal "
               "status, is counted at the patent.\n\n"
               "The time axis is the priority year, the date closest to the design decision. The "
               "application and publication years lag it by amounts that differ by office "
               "(2.1.3).\n\n"
               "Windows are 2011 and earlier, 2012 to 2015, 2016 to 2019, 2020 to 2023, and "
               "{partial_start} to {year_max}, holding {window_counts} aircraft. The last is "
               "partial and is drawn hatched. Counts stop at {complete_to} and shares run to "
               "{year_max} within region, under the rule of 2.1.3."),
         code=["a2.d9_architecture_by_window(ds)[['window', 'unique aircraft']]"]),
    dict(id="5.3", title="The archetype and the distance",
         text=("The same aircraft is represented two ways, because the measures need different "
               "things. One representation is discrete, so kinds can be counted. The other is "
               "continuous, so degrees of difference can be measured without naming kinds at "
               "all.\n\n"
               "**The archetype.** An archetype is a name for a kind of design, formed by joining a "
               "few label fields into one string. A1t, defined in 3.3.6, joins architecture class, "
               "number of wings, and whether any propulsor tilts. It gives {a1t_distinct} "
               "archetypes over {n_arch} aircraft. A1 and A1b are computed alongside as "
               "robustness, and every curve below is drawn at all three.\n\n"
               "**The distance.** Gower's coefficient measures how different two aircraft are "
               "across the mixed categorical and count fields of the shortlist (Gower, 1971). For "
               "aircraft *i* and *j*,\n\n"
               "```\nd(i,j) = Σ w δ (1 − s)  /  Σ w δ\n```\n\n"
               "over fields *k*, where *s* is 1 when the two aircraft share a category and 0 when "
               "they do not, and *δ* is 1 only when both aircraft carry a value for that field. "
               "The *δ* term is what implements 3.3.2. A boom field does not exist for a wingless "
               "multirotor, so it leaves that pair's average instead of registering as a "
               "difference between them. Whether the wing carries the thrust enters as one pooled "
               "field: rotors on the wing card and on a wing-attached boom count the same, so the "
               "boom-or-wing reading of an ambiguous member does not move the distance.\n\n"
               "The weights *w* decide how much each field contributes, and the question they "
               "answer is concrete. The codebook spends {slots_M3} slots on propulsion and "
               "{slots_G1} on architecture class. That ratio records how much detail the "
               "labelling tool collects, and not how much each subsystem matters to a design. "
               "Weighting every field equally would carry that ratio into the measurement, and "
               "two aircraft would come out similar mainly because their propulsor slots match. "
               "The weights are therefore set by subsystem: each of architecture, wings, "
               "empennage, fuselage, booms and propulsion receives one unit of weight, divided "
               "among its own fields. A subsystem then counts once whatever number of columns "
               "the codebook spends on it.\n\n"
               "Uniform weighting is computed as well, and reported as a robustness check. When "
               "the two produce the same shape, the finding is about the corpus. When they "
               "disagree, the finding is about the weighting, and the chapter says which. A "
               "third scheme, weighting each field by how strongly it constrains the others, was "
               "considered and dropped: the weights would come from an analysis of the same "
               "labels the distance is afterwards used to analyse.\n\n"
               "The matrix is {unique} by {unique} and is computed once. Every measure below "
               "reads from it."),
         code=["a2.d5_archetype_cardinality(ds).set_index('level').loc[['A1', 'A1b', 'A1t']]"]),
    dict(id="5.4", title="Structure of the design space",
         text=("For each pair of shortlist fields, the strength of association is measured by "
               "Cramér's V over their contingency table, computed only on aircraft to which both "
               "fields apply. Cramér's V runs from 0 to 1 and states how far knowing one field's "
               "answer tells you the other's. The output is a fields by fields heatmap, and it "
               "answers which design decisions travel together. The row sums rank the fields by "
               "how much each constrains the rest. A field that constrains many others is core "
               "to the design, and one that constrains none is peripheral.\n\n"
               "Strongly associated fields are not double-counted in the distance, because two "
               "fields carrying the same information twice would weight that information twice."),
         code=[]),
    dict(id="5.5", title="The three diversity measures",
         text=("No single number expresses how diverse a technology is, so variety, balance and "
               "disparity are reported separately (Stirling, 2007). The three answer different "
               "questions about the same window, and they can move independently.\n\n"
               "Within a window, *p* is the share of aircraft belonging to each archetype, and the "
               "shares sum to one.\n\n"
               "**Variety and balance.** The Hill numbers are a family of three counts that differ "
               "in how much weight they give to rare archetypes (Hill, 1973).\n\n"
               "```\n⁰D = the number of archetypes present\n"
               "¹D = exp(−Σ p ln p)          the exponential of Shannon entropy\n"
               "²D = 1 / Σ p²                 the inverse Simpson index\n```\n\n"
               "⁰D counts kinds and ignores how common each one is, so a single unusual design "
               "raises it as much as a mainstream one. ¹D and ²D rescale instead. Each states how "
               "many equally common archetypes would produce the spread actually observed, which "
               "is why both are read as a number of designs in play rather than a number of "
               "designs present. A window holding twelve archetypes where three quarters of its "
               "aircraft sit in two of them behaves like about three, and the distance between "
               "twelve and three is the message. ²D discounts rare archetypes more sharply than "
               "¹D, so ⁰D ≥ ¹D ≥ ²D always, with equality only when every archetype is equally "
               "common.\n\n"
               "⁰D is comparable across windows only at equal sample size, because the windows "
               "differ by a factor of four and a larger window finds more kinds for that reason "
               "alone. Forty aircraft are drawn without replacement from each window, the count "
               "is taken, and the draw is repeated a thousand times. The mean and the fifth to "
               "ninety-fifth percentile band are reported. This is rarefaction, and it is "
               "mandatory here and not optional: the raw counts rise and fall with window size "
               "in a way that has nothing to do with the design space.\n\n"
               "**Disparity.** Rao's quadratic entropy is the expected distance between two "
               "aircraft drawn at random from the window (Rao, 1982). Read plainly, it answers "
               "how different two eVTOL concepts from that period would be if they were picked "
               "blind.\n\n"
               "```\nQ = Σᵢ Σⱼ pᵢ pⱼ d(i,j)\n```\n\n"
               "Q needs no archetype, which makes it the independent check on the other two, and "
               "it carries the fine labels the archetype leaves behind. It can move while the "
               "Hill numbers are still, and the reverse.\n\n"
               "The three read as a set. Balance falling with disparity holding means the field "
               "is concentrating on fewer designs that nonetheless remain far apart. Both falling "
               "is convergence.\n\n"
               "**Turnover.** Per window, the archetypes appearing for the first time, those last "
               "seen, and the Jaccard overlap with the previous window, which is the share of "
               "archetypes the two windows hold in common. It shows branches opening and closing "
               "directly."),
         code=[]),
    dict(id="5.6", title="Significance and uncertainty",
         text=("Any curve moves a little even when design and date are unrelated, because each "
               "window holds a different number of aircraft and a different draw of designs. Two "
               "guards separate real movement from that noise, and chapter 3 licenses both.\n\n"
               "**Year shuffling.** The claim under test is that which architecture an aircraft "
               "has depends on when it was filed. The test builds corpora in which that "
               "dependence is removed and nothing else is changed. Every aircraft keeps its "
               "labels exactly as they are, and only the priority years are dealt out again at "
               "random. The same aircraft and the same window sizes survive, and design and date "
               "are now unrelated by construction. The measure is recomputed there, a thousand "
               "times, and the spread of those thousand values is how much movement the window "
               "structure produces on its own. Drawn as a shaded band behind the real curve, it "
               "shows at a glance how much of the curve is signal. A fall matched by a third of "
               "the shuffles is evidence of nothing. A fall matched by twelve of them is a "
               "finding.\n\n"
               "**Company bootstrap.** Confidence bands are built by resampling companies and not "
               "patents. A bootstrap builds an error bar by drawing a corpus of the same size at "
               "random with replacement, recomputing the measure, and repeating. Resampling "
               "companies is what makes the band answer the right question, which is how much "
               "the curve would move if a different set of firms had happened to file. Bell and "
               "Textron file under {bell_strings} assignee strings and stand behind {bell_tr_share} "
               "of the tilt-rotor aircraft of named companies ({bell_tr} of {tr_named}, 3.1.2). "
               "One firm filing thirty patents on one aircraft is one design decision, and a "
               "band built on patents would treat it as thirty and report the field as more "
               "certain than it is. The year shuffling is run within company for the same "
               "reason.\n\n"
               "Effect sizes are reported with their bands. The permutation probability is the "
               "guard and not the result."),
         code=["a2.d8_split_firms(ds, 'Bell / Textron')"]),
    dict(id="5.7", title="The dominant-design criterion, fixed in advance",
         text=("A dominant design is the configuration an industry settles on after a period of "
               "competing alternatives, and its arrival changes what firms compete over. The "
               "automobile industry is the standard case (Abernathy and Utterback, 1978). Steam, "
               "electric and petrol propulsion competed for three decades, the front-engine "
               "petrol layout became the shape every manufacturer built, and competition moved "
               "from the arrangement of the vehicle to its cost and refinement. Whether the eVTOL "
               "sector has reached that point is the question this analysis exists to "
               "answer.\n\n"
               "The criterion is written here, before any curve is drawn. The reason is that a "
               "measure of convergence can be read as supporting almost any account once the "
               "curves are in front of the reader, and a criterion stated afterwards carries no "
               "weight. A dominant design is recorded when all three conditions hold in the same "
               "window, and the window is complete.\n\n"
               "1. One A1t archetype holds more than half the aircraft, in two consecutive "
               "windows. More than half means most of the sector is proposing the same design. "
               "Two windows means the share is not a single unusual period.\n"
               "2. ²D falls below the permutation band of the earliest windows. The window then "
               "holds fewer designs in play than the shuffled corpora produce by chance, so the "
               "concentration is in the corpus and not in the window structure. A fixed cutoff "
               "was considered and set aside: a threshold such as two designs in play cannot be "
               "justified against 2.5, while the band is computed from this corpus and moves "
               "with it.\n"
               "3. Q falls below the level of the earliest windows by more than the permutation "
               "band. The aircraft have become similar to one another, and not only concentrated "
               "in one name.\n\n"
               "The three conditions are deliberately different in kind. The first is about "
               "counts, the second about balance, the third about form. A sector can satisfy one "
               "and not the others, and each of those cases is a different state of the "
               "technology.\n\n"
               "The corpus already indicates the first condition will not be met. No architecture "
               "class exceeds {max_window_share} of any window in table 3.3.8, and A1t subdivides "
               "those classes further, so the largest archetype share is smaller still. That "
               "result stands on its own: {year_span} years of eVTOL patents, and the sector has "
               "not converged on a single architecture.\n\n"
               "The measurement that matters is therefore the second reading, and it is specified "
               "with the same care. ²D can fall while Q holds. Fewer designs would then be in "
               "play, while the designs that remain stay far apart in form. That is a field "
               "narrowing without having chosen a shape, and it is a more precise claim about the "
               "state of eVTOL development than a plain absence of convergence. Both readings are "
               "fixed before either is observed, and whichever the corpus supports is reported "
               "with the same weight."),
         code=[]),
    dict(id="5.8", title="Strata",
         text=("{non_corporate_share} of the corpus is not corporate. {individual} primary patents "
               "belong to individual inventors and {unattributed} to filers that resolve to no "
               "known company, against {named} from {named_companies} named firms (3.1.2). "
               "Assignee type is therefore a stratum the corpus can support, and the "
               "ferment-to-dominance account makes a prediction about it: individuals and "
               "universities are expected to keep exploring after companies have converged. "
               "Every curve of 5.5 is repeated by assignee type.\n\n"
               "Region is reported next to every curve and is never used as a filter, for the "
               "reason given in 3.1.1. It becomes a split and not an annotation in the "
               "{partial_start}–{year_max} window, under the rule of 2.1.3."),
         code=[]),
    dict(id="5.9", title="Scope",
         text=("Two boundaries are set by decision.\n\n"
               "The {partial_start}–{year_max} window carries shares and not counts, and within "
               "region and not pooled.\n\n"
               "The frozen-model comparison receives the {n_classes} architecture classes of "
               "3.3.7 and the whole-aircraft figures of 3.2.2. What a frozen vision model "
               "recovers from them is the subject of its own chapter, and no result in this "
               "chapter depends on it. Every number above is computed from the labels alone, so "
               "no measurement of the design space can be disturbed by a model's errors."),
         code=[]),
    dict(id="5.10", title="Choices that rest on the author's judgement",
         text=("Most of the settings in table 5.1 are read from a measurement in chapters 2 to 4. "
               "Three are not. Each of the three is argued in the section that makes it, and each "
               "has a defensible alternative, so they are collected here with what would change "
               "if the alternative were taken. They are open until the analysis is run and are "
               "recorded so that a reader can disagree with a specific sentence and not with the "
               "document as a whole."),
         tables=["ch5_judgement"],
         after=("The first two are the substantive ones, because they change what is computed. "
                "The third changes only what the result is compared against."),
         code=["ch5.judgement_table(N)"]),
    dict(id="references", title="References",
         text="",
         code=[]),
]


# --------------------------------------------------------------------------
# accessors
# --------------------------------------------------------------------------
def node(node_id: str) -> Dict:
    for n in NODES:
        if n["id"] == node_id:
            return n
    raise KeyError(node_id)


def depth(node_id: str) -> int:
    return node_id.count(".")


def children(node_id: str) -> List[Dict]:
    return [n for n in NODES if n["id"].startswith(node_id + ".") and depth(n["id"]) == depth(node_id) + 1]


def _fill(template: str, values: Optional[Dict]) -> str:
    if not values:
        return template
    class _Safe(dict):
        def __missing__(self, key):
            return "{" + key + "}"
    return template.format_map(_Safe(values))


def heading(node_id: str, values: Optional[Dict] = None) -> str:
    n = node(node_id)
    title = _fill(n["title"], values)
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
    """The prose of a node, placeholders filled from :func:`numbers.live`."""
    if node_id == "references":
        from .ch5 import REFERENCES
        return "\n".join(f"- {r}" for r in REFERENCES)
    return _fill(node(node_id).get("text", ""), values)


def after(node_id: str, values: Optional[Dict] = None) -> str:
    return _fill(node(node_id).get("after", ""), values)


def figure_number(node_id: str, k: int, total: int) -> str:
    """Chapter-head figures are numbered N.1; others take the owning subsection's id."""
    base = f"{node_id}.1" if depth(node_id) == 0 else node_id
    return base + ("" if total == 1 else "abcdef"[k])


def table_number(node_id: str, k: int, total: int) -> str:
    return node_id + ("" if total == 1 else "abcdef"[k])
