"""Structure of the SHORT Labelling Analysis — ``LABELLING_ANALYSIS_BRIEF.md``.

A second document over the SAME data as ``LABELLING_ANALYSIS.md``: the same built tables in
``tables/``, the same drawn figures in ``figures/``, rendered by the same
:func:`report.write_markdown`. Nothing here recomputes anything and nothing here is typed —
every number is a ``{placeholder}`` resolved at render time, either from ``numbers.live`` or,
through :data:`NUMBERS` and :data:`la_index.TAKEAWAY_NUMBERS`, out of the built tables. So no
number in this document can disagree with the one in the full document.

WHAT IS DIFFERENT FROM ``la_index``
-----------------------------------
* **Organised by question, not by chapter.** One section per sector question, and the section
  ids ARE the question ids (``Q1`` … ``Q8``, ``M``), so the wording of a question lives in
  exactly one place — :data:`la_index.QUESTIONS` — and rewriting a question renames the heading
  of this document without touching anything else. The ids are keys, not positions, and only
  :data:`NODES` decides the printed order; since the renumbering of 2026-09-23 the two agree,
  because the questions were renumbered INTO this document's reading order — Q1 as the
  introducer (what the record is worth), then Q2 … Q8, then the design drivers and M.
* **No front matter.** There is no "how to read" page, no data-set paragraph and no vocabulary
  section (cut 2026-09-23): the two-line statement of the data set and the pointer to the full
  document open the first question, and every question section states its own unit of analysis
  on its second line (:data:`UNIT`, read from ``la_index.PROVENANCE``). The taxonomy drawing is
  not printed here at all (dropped 2026-09-23, the author has it on paper); it stays Appendix D
  of the full document, and the two pointers to it — the opening paragraph of Q1 and the class
  line of Q2 — name that document through ``{sm_ref_codebook_classes}``.
* **One to three items per question**, graded ``core`` in :data:`la_index.GRADE` unless
  :data:`NOT_CORE` names the item and the reason. The answer is stated first, in prose; the
  items are the evidence under it, and the selection rule is enforced by the render script,
  not by eye. Q3 is the one question printed in four parts — unit, screens, conditions,
  result — because its answer is negative and a negative answer is a statement about a unit
  and a test, both of which have to be on the page before the verdict can be read.
* **The apparatus is lighter.** This module deliberately defines no ``provenance`` and no
  ``question`` accessor, so ``report._prov_md`` and ``report._quest_md`` return ``""`` and the
  unit·base·transform line and the per-item question line are simply not printed. The takeaway
  stays, and carries the item's number in the full document at its end, where the two dropped
  lines are printed in full. Since 2026-09-23 it carries nothing else: the grade clause
  ("Graded supporting; printed here because …") was the document explaining its own selection
  rule to a reader who cannot act on it, and the rule is still enforced in
  ``render_summary.check_selection``. The same review took out every other sentence of that
  register — how the brief was assembled, how items were graded or ordered, what the register
  does — while keeping the method behind each measurement.
* **Its own numbering.** Figures and tables are numbered in one running sequence, Figure 1,
  Figure 2, …, so a number here never collides with a number there, and a caption still starts
  with "Figure <digit>" — which is what the PDF stylesheet keys its caption rule on.

NOTHING IN THIS MODULE IS IMPORTED BY ``la_index`` OR BY ``index``. ``report.py`` carries one
guarded addition for the front-page index (below); it fires only when ``idx.index_md`` exists,
which neither ``la_index`` nor ``index`` defines, so the full Labelling Analysis and the
Preliminary Analysis still render byte-for-byte as before.
"""

from __future__ import annotations

import re as _re
from typing import Dict, List, Optional

from . import index as _pa
from . import la_index as _la
from . import sm_text_methods as _methods_text

TITLE = ("Labelling Analysis in brief: five questions about the eVTOL patent record, "
         "the evidence that answers them, and what to ask next")


# --------------------------------------------------------------------------
# 1 — the running order
# --------------------------------------------------------------------------
# The ORDER of this list is the order of the document. The ids of the eight question
# sections are the keys of ``la_index.QUESTIONS``; ``heading`` reads the wording from there,
# so a renamed question needs no edit here.
#
# SELECTION RULE, applied once and enforced by the render script rather than by hand: an item
# is printed here only if ``la_index.GRADE`` grades it **core** — the answer rests on it. No
# item graded weak is printed, on either ground, not even the eight that ``QUESTION_MAP.md``
# §2 keeps "with a fix": in a document this short the reader has no room to discount a figure
# while reading it. The items that are printed without being core are graded **supporting** or
# ungraded, never weak; each is named in :data:`NOT_CORE` with its reason, and the render
# script fails on any item outside that list that is not core.
#
# Where the core items of a question run out, the question is stated as only partly reachable
# and the grade that keeps the missing item out is quoted — see Q2, which has exactly one core
# item in the whole document.
OLD_NODES: List[Dict] = [
    # ---------------------------------------------------------------- Q1 — the introducer
    # First on the author's instruction (2026-09-23): what the record is worth as an indicator
    # is what a reader needs before any reading of it, and its opening lines carry the two-line
    # statement of the data set and the pointer to the full document that the cut front matter
    # used to carry. The taxonomy drawing USED to open its figures and took page 2 on its own;
    # on the author's instruction of 2026-09-23 ("regarding the two pages of taxonomy, put them
    # in the end, in the appendix") it is now the closing section of this document, and the
    # section opens with its own first figure instead — the lapse figure, shortest-first,
    # because ``report`` binds a portrait first figure to the heading and the filings figure is
    # 8.7 in tall. The pointer to the vocabulary stays in the opening paragraph, and now names
    # where it went.
    # 2026-09-26 (chapter-1 review): the prose that stood here moved into the Method blocks
    # (``TEXTS["1.q1"]`` and ``CHAPTER_METHOD["1"]``) and the takeaways; C6 — it repeated them.
    # The market clock figure joins it (C41: the Answer quoted a figure the chapter did not show).
    dict(id="Q1",
         figures=["filings_per_year", "ari_clock"]),
    # 2026-09-24: the lapse paragraph and its figure are their own section, under sub-question 1.2
    # 2026-09-26 (C15): out of force is read per unique aircraft — out only when EVERY patent
    # that describes it is inactive — so the primary-patent figure gives way to the brief's own
    dict(id="Q1b",
         figures=["sm_force_aircraft"]),

    # ---------------------------------------------------------------- Q2
    # Second: what is gaining and dying, read before the archetype test (Q3) and before the
    # inventory (Q4), on the author's instruction. ``dimension_drift`` (core)
    # is the figure the author asked for under Figure 2 (ii): propulsor counts inside one class
    # over the years.
    dict(id="Q2",
         text="**Lift + Cruise overtakes Tilt Rotor and keeps the lead.** Tilt Rotor falls from "
              "{tk_tr_w1} of the aircraft in the earliest window to {tk_tr_w4} in 2020-23; Lift + "
              "Cruise rises from {tk_slc_w1} to {tk_slc_w4}; CVT stands at {tk_cvt_w4}. The earliest "
              "window holds {sm_w1_n} aircraft, so its shares are coarse; the 2020-23 end rests on "
              "{sm_w4_n}. **This crossover has no external check.** No published source resolves "
              "eVTOL filings by architecture over time, and the nearest public series — the Vertical "
              "Flight Society aircraft directory — counts announced aircraft rather than patent "
              "families, as a cumulative stock rather than per filing cohort, and pools Tilt Rotor, "
              "Tilt Wing and CVT into one 'vectored thrust' category; on that pooled definition this "
              "corpus agrees with the directory that the tilting family is the largest. The movement "
              "of Tilt Rotor on its own is a finding of this record, not a confirmation of one. "
              "Shares are "
              "read per window, so a class can fall in share while its count still grows — and where "
              "the count itself falls (CVT from 2020-23 into the partial 2024-26 window) the fall is "
              "the incomplete window, not an abandonment. The shift arrives with new firms: "
              "{tk_cm_e_slc} of the firms entering in 2020-23 enter with Lift + Cruise against "
              "{tk_cm_a_slc} of that window's aircraft (Chapter 3).",
         figures=["atlas_arch_time", "sm_evtolnews_check"]),

    # ---------------------------------------------------------------- Q3
    # Third, before Q4: the archetype has to be explained before Q4's archetype figure is read.
    # The only question printed in four parts (unit, screens, conditions, result — the full
    # document's own order, 1.1.3), with the verdict still stated first. Cut to about half its
    # 2026-09-23 length on the author's review: short definitions, the tables carry the detail.
    dict(id="Q3",
         text="**No dominant design, at any level, in any complete window.** The test has three "
              "conditions — counts, balance, form — with thresholds fixed in the Preliminary "
              "Analysis (5.7) before any curve of this corpus was drawn, so a 'no' is a finding and "
              "not a description. What each condition measures, where it comes from and which "
              "published test it does and does not reproduce are set out in the methods box at the "
              "head of this chapter.",
         figures=["dominant_design", "sm_weighting", "sm_family"],
         tables=["la_dd_result", "la_top_archetypes"]),
    # 2026-09-26 (chapter-2 review, C52/C67/C77): the archetype premise moved to the new
    # chapter 2 (node "arch"); the class configurations are node "inclass" of chapter 3; the
    # dominant-design evidence is carried by Q3 itself. The era table and the family verdict
    # table are no longer printed (C51, C59).
    dict(id="arch", title="Archetypes and the level of detail",
         tables=["la_archetype_levels"]),
    dict(id="inclass", title="Inside each class",
         figures=["sm_class_configs"]),

    # ---------------------------------------------------------------- Q4
    # The answer is two or three sentences, never a page: everything else the corpus says about
    # this question is already printed on the items, in their takeaway lines.
    dict(id="Q4",
         text="**A wide space with a crowded middle; the variety is in the propulsion.** Twelve "
              "classes are occupied; {top_class} holds {sm_top_class_share} of the {unique_s} "
              "aircraft; the five propulsive-unit bands hold {bin_r03}, {bin_r4}, {bin_r56}, "
              "{bin_r78} and {bin_r9} aircraft, and {grp2} of {units_n} aircraft put their units on "
              "exactly two **stations** — a station is a place on the airframe where a group of "
              "propulsors sits: the wing, a boom, the nose, the tail. The fastest-growing archetype, CVT · 5-6, rests on "
              "{sm_cvt56_filers} filers for {sm_cvt56_air} aircraft — {sm_cvt56_fpa} per aircraft, the "
              "lowest of the {sm_zones_big_n} archetypes of {sm_zones_min}+ aircraft — so its rise is "
              "closer to one firm's line of variants than to a sector choice. Ducting is U-shaped in "
              "rotor count ({sm_duct_13} of aircraft at 1-3 units, {sm_duct_78} at 7-8, {sm_duct_9} "
              "at 9+); counted in units, the aircraft at nine and more that duct, duct nearly "
              "everything — {sm_duct9_units} of that band's units run in a duct, a median of "
              "{sm_duct9_med} per ducting aircraft — where at 1-3 units it is a single ducted fan. "
              "The two ends are two designs: a ducted-fan array, and a ducted cruise or tail unit.\n\n"
              "**Whether the space is still opening depends on how finely a design is described, "
              "and that is the finding.** At the class level it is closed: twelve classes, and not "
              "one new class in the last hundred aircraft. At class plus propulsive-unit band it is "
              "effectively closed — about {sm_disc_a0c_unseen} of an archetype is estimated to be "
              "still unseen. At the design-species level, which also records the wings and whether "
              "anything tilts, it is **still opening**: {sm_disc_a1t_obs} archetypes observed "
              "against an estimated {sm_disc_a1t_est} in the population, and "
              "{sm_disc_a1t_new100} new ones appeared in the last hundred aircraft where chance "
              "alone would give {sm_disc_a1t_exp100}. One assumption, stated because it bounds the "
              "claim: the estimator treats the record as a closed population sampled at random, so "
              "'unseen' means combinations already in the record and not yet drawn. It is a floor "
              "on what remains, never a forecast of designs nobody has invented.",
         figures=["atlas_units", "sm_duct_count"],
         tables=["a2_d3_selected_fields"]),
    dict(id="space", title="Where designs concentrate",
         figures=["sm_archetype_filers", "zones", "discovery_curve"]),

    # ---------------------------------------------------------------- Q5
    dict(id="Q5",
         text="**Most of the corpus belongs to an organisation, but to a great many small ones, "
              "and there is no top tier.** Named companies hold {tk_fm_named_air} of the "
              "{unique_s} aircraft ({tk_fm_named_share}) and individual inventors "
              "{tk_fm_ind_air}; the largest {tk_seg_top_firms} firms hold {tk_seg_top_air} "
              "between them and all {tk_firms_all} named firms together {tk_named_share} of the "
              "set. The population is still forming: the individual share falls from "
              "{tk_indshare_w1} to {tk_indshare_2023} and in every window most active firms are "
              "filing for the first time, so no statement about firm strategy holds over the "
              "corpus as a whole. Filer type is read from the assignee string the patent itself "
              "names (decision G8 of the methodology framework).",
         figures=["coverage"],
         tables=["la_filer_mix", "la_filers_by_window"]),

    # ---------------------------------------------------------------- Q6
    dict(id="Q6",
         text="**Three countries hold almost two thirds of the corpus — US {tk_us_n}, CN "
              "{tk_cn_n}, DE {tk_de_n} of {unique_s} — and one regional difference survives in "
              "every window: North America keeps the tilting architectures.** The US files "
              "{tk_us_tr} of its aircraft as Tilt Rotor while China's largest class is Lift + "
              "Cruise at {tk_cn_slc}; everything else moves together.\n\n"
              "*What region does not do is organise design at firm level.* Firms in different "
              "regions are as close in architecture profile as firms in the same one — a null "
              "result ({sm_here_proximity_region}).",
         figures=["atlas_region", "region_grid", "proximity_region"]),
    # 2026-09-24: timing is its own sub-question (4.2)
    dict(id="Q6b",
         text="**The regions do not run on one clock, and the lead is solid.** Every class is taken "
              "up first in North America, then Europe, then Asia-Pacific, with CVT the one exception "
              "({tk_crt_cvt_na} in North America, its latest cell). North America passes the middle "
              "of its own filings in 2018, Europe in 2019 and Asia-Pacific in 2020, and the regional "
              "effect on priority year is strong (p {sm_lag_p_region}).\n\n"
              "**Whether the gap is the same size in every class is not settled.** The test for it "
              "— whether the regional offset changes from class to class — gives p "
              "{sm_lag_p_inter}, which neither rejects a constant offset nor confirms one, so this "
              "document does not claim the lag is a constant. What pushes the test that way is a "
              "change of sign: Asia-Pacific sits roughly three to four years behind on Lift + "
              "Cruise, Tilt Rotor and Tilt Wing, and about a year **ahead** on Combined vectored "
              "thrust.",
         tables=["la_class_region_timing"]),
    # 2026-09-24: how a firm files — depth against breadth — is sub-question 4.3, moved here from
    # the full document's 3.4 (both items core there)
    dict(id="portfolio",
         text="**Firms deepen; they do not explore.** A firm that files again usually files in the "
              "same class, and Tilt Wing is the one class firms pass **through**: only about one "
              "succession in six stays in Tilt Wing, where Lift + Cruise and Tilt Rotor keep "
              "roughly six firms in ten. Where the leavers go answers the 'why': more of them move "
              "to Tilt Rotor than stay, and almost as many move to Lift + Cruise — the two "
              "neighbours that keep the tilting rotors and drop the tilting wing, or drop the tilt "
              "altogether. The tilting wing is a step on the way, not a destination. Among the "
              "17 firms with five or more aircraft there is no single IP strategy: patents per "
              "aircraft run from {tk_ip_min_ppa_v} ({tk_ip_min_ppa}) to {tk_ip_max_ppa_v} "
              "({tk_ip_max_ppa}), and the firms that file deepest are not the firms with the widest "
              "class mix. Re-filing one design many times moves no class share by more than 0.03, "
              "which is why every count in this document is taken on aircraft.",
         figures=["ip_strategy"],
         tables=["la_ip_strategy"]),

    # ---------------------------------------------------------------- Q7
    dict(id="Q7",
         text="**No at class level; sometimes inside a single window.** The largest single filer "
              "of a class holds {tk_fw_tr_share} of Tilt Rotor and {tk_fw_cvt_share} of CVT, the "
              "four largest classes each divide as if between twenty-five or more equally sized "
              "filers, and dropping {tk_lev_firm} — the largest filer in the corpus — moves the "
              "{tk_lev_class} share by {tk_lev_pp} points, further than any other firm moves "
              "any share. Inside one window it is different: {tk_fw_tr_largest} holds "
              "{tk_fw_tr_win} of Tilt Rotor in 2016-19 and {tk_fw_cvt_win} of CVT in 2020-23, so "
              "a single window's rise can be one firm even where the class is not.",
         figures=["filer_weight", "firm_influence"],
         tables=["la_class_filer_weight"]),

    # ---------------------------------------------------------------- Q8
    # 2026-09-26 (C21, C32): the name table opens the section — it says which aircraft CAN be
    # compared before the comparison is shown; the index-gap table (old Table 5) is cut, the
    # representativeness tables carry what the question needs.
    dict(id="Q8",
         tables=["la_name_coverage", "la_public_pairwise", "a2_d15_trl_by_class",
                 "la_trl_representativeness", "la_ari_representativeness"]),

    # ---------------------------------------------------------------- design drivers (2026-09-23)
    # Not a ninth question: the closing reading of Q2-Q4 (what is gaining, whether it converges,
    # what is being designed), placed after the last question section and before the method
    # bound. Printed because both tables are graded core in
    # la_index.GRADE; the drift figure (Figure 1.4.1 of the full document, eleven panels) is core
    # too but is not printed — the verdict table carries every one of its readings with the test
    # beside it, and the figure would cost this document a page for the same content.
    dict(id="drivers", title="What moved inside the classes, and which drivers predict it",
         text="A design driver — the technology that moved, the physics that did not, a requirement, "
              "a cost — is not observed in a patent; it leaves a trace in the morphology, and the "
              "traces are what the aircraft are labelled with. Each trace is read INSIDE each class "
              "against priority year (Spearman ρ; p < 0.05 = it moves), never pooled, because the "
              "class mix moves on its own. Counts are medians, or means where a median of 1 or 2 "
              "stands still while the distribution moves. Four traces moved; under each, the "
              "correlation the record shows and the reasons it *may* have — possible, not asserted.",
         figures=["sm_driver_traces"],
         tables=["la_driver_verdicts"]),
    # 2026-09-25 (C33): "make this easier to understand to a child of 14, I did not understand
    # at first sight". Each observation now opens with what physically changed on the aircraft,
    # in one sentence and no numbers; the numbers follow; the verdict is a PLACEHOLDER read from
    # the verdict table, never a sentence typed here, because the tilting-joint result is being
    # recomputed per propulsive unit and the cost reading may weaken or disappear.
    dict(id="drivers.obs", title="Four observations, each with the correlation behind it",
         text="**1 \u00b7 A second set of tilting rotors.** *What changed on the aircraft:* the early "
              "tilt rotor was one pair of rotors, out on the wing, that swivel from pointing up to "
              "pointing forward. The aircraft filed later carry **two** sets of tilting rotors "
              "instead of one \u2014 a forward set and a rear set, on a canard and a wing, or on a wing "
              "and a tail (Maker v1, Nexus v6, Heaviside, Lilium Jet in 2020-23). Nothing new tilts: "
              "there are simply two groups of tilting rotors where there was one.\n\n"
              "*The numbers.* Inside Tilt Rotor the mean number of tilting joint groups "
              "{sm_t_joints_tr_move} from {sm_t_joints_tr_first} to {sm_t_joints_tr_last} "
              "(\u03c1 {sm_t_joints_tr_rho}, p {sm_t_joints_tr_p}); inside CVT it "
              "{sm_t_joints_cvt_move} from {sm_t_joints_cvt_first} to {sm_t_joints_cvt_last} "
              "(\u03c1 {sm_t_joints_cvt_rho}, p {sm_t_joints_cvt_p}); Tilt Wing and Multirotor are flat, "
              "Lift + Cruise has none by definition, and pooled over the five classes the trace is "
              "{sm_t_joints_all_move} ({sm_t_joints_all_first} to {sm_t_joints_all_last}, "
              "p {sm_t_joints_all_p}). The added joint is a tilting *propulsor set*, not a tilting "
              "wing or boom: the joints that are not a propulsor set do not move in any window, and "
              "the two curves travel together in {sm_here_sm_driver_corr} (i).\n\n"
              "*What it means — and a correction this review produced.* Regime transition (A1) "
              "predicts more joints; development and certification cost and maintenance cost "
              "predict fewer, and on the raw count the verdict table above reads "
              "{sm_v_joints_full}. **That verdict does not survive normalisation, and the "
              "correction was predicted at review: a count of joint groups is not normalised by the "
              "rotors those joints have to move.** Divided by the propulsive units the aircraft "
              "carries, tilting joints **fall** inside Tilt Rotor (ρ {sm_jpu_tr_rho}, p "
              "{sm_jpu_tr_p}) and are flat inside CVT (ρ {sm_jpu_cvt_rho}, p {sm_jpu_cvt_p}); "
              "pooled, they fall. So designers are not adding tilting joints. They are adding "
              "propulsors, and the joints follow at a declining rate per propulsor — which moves "
              "**with** the cost drivers, not against them. The joints-per-unit table and its "
              "figure carry the fit. Three readings the "
              "drawings cannot tell apart: a fore-and-aft pair controls pitch in hover by "
              "differential thrust and removes the cyclic-pitch hub a single pair needs (a simpler "
              "hub, not fewer joints \u2014 hub mechanism is not labelled); an electric nacelle is small "
              "enough that one tilt actuator per set is cheap, where a turboshaft tilt rotor tilts a "
              "heavy gearbox per side; and a second set doubles the units for the same joints per "
              "set, which is the redundancy certification asks for.\n\n"
              "**2 \u00b7 More rotors, and it is the same move as 1.** *What changed on the aircraft:* "
              "the tilting classes went from a couple of large rotors to several smaller ones. "
              "*The numbers.* The median propulsive-unit count {sm_t_units_tr_move} in Tilt Rotor "
              "({sm_t_units_tr_first} to {sm_t_units_tr_last}, \u03c1 {sm_t_units_tr_rho}, "
              "p {sm_t_units_tr_p}) and {sm_t_units_cvt_move} in CVT ({sm_t_units_cvt_first} to "
              "{sm_t_units_cvt_last}, \u03c1 {sm_t_units_cvt_rho}, p {sm_t_units_cvt_p}); Lift + Cruise "
              "is flat from {sm_t_units_slc_first}. *What it means.* Verdict: **{sm_v_units}** \u2014 "
              "distributed propulsion (A1), failure tolerance (B) and community noise (B) all "
              "predict the same rise and the record cannot separate them. It is not a second event: "
              "in Tilt Rotor the unit count follows the number of tilting sets almost exactly \u2014 two "
              "units with one set, four with two, six with three ({sm_here_sm_driver_corr} ii) \u2014 so "
              "observation 1 and observation 2 are one arrival, the multi-set tilt rotor. Electric "
              "share does not explain it: inside Tilt Rotor the median is the same for electric and "
              "hybrid aircraft, and the year term survives the electric control.\n\n"
              "**3 \u00b7 The duct leaves CVT, because the airframe around it leaves.** *What changed on "
              "the aircraft:* the early CVT buried its fan inside the fuselage or the wing, and a "
              "fan buried in a body is ducted because the body **is** the duct. The late CVT looks "
              "like a Lift + Cruise: open rotors hung on booms, with one tilting set added. A rotor "
              "on a boom has no body around it, so there is nothing to duct. *The numbers.* Inside "
              "CVT the share with a ducted unit {sm_t_duct_cvt_move} from {sm_t_duct_cvt_first} to "
              "{sm_t_duct_cvt_last} (\u03c1 {sm_t_duct_cvt_rho}, p {sm_t_duct_cvt_p}); every other class "
              "is flat. Split CVT by whether it carries units on booms and the fall disappears: the "
              "aircraft **without** booms duct throughout, the aircraft **with** booms barely duct at "
              "all, and ducting against year with the boom layout held fixed is not significant "
              "({sm_here_sm_driver_corr} iii). *What it means.* Verdict: **{sm_v_duct}** \u2014 community "
              "noise predicts more ducting and the share fell. The finding is structural and the "
              "record supports it: **the duct is a property of the airframe the rotor sits in, not a "
              "separate choice.** The reading that a duct is bought to keep noise and vibration away "
              "from the cabin is a *hypothesis this record cannot test* \u2014 acoustics are not labelled "
              "and no patent states them \u2014 and it is written here as one, not as a finding. What the "
              "record can say is that the noise requirement was met another way in the same years: "
              "more, smaller rotors (observation 2).\n\n"
              "**4 \u00b7 One more kind of propulsor, and it is observation 1 again.** *What changed on "
              "the aircraft:* a propulsor type is one set of like units on one station \u2014 lift rotors "
              "on the booms are one type, a cruise propeller on the tail a second, a tilting set on "
              "the wing a third \u2014 and the tilt rotors gained a type. *The numbers.* The mean "
              "{sm_t_types_tr_move} in Tilt Rotor ({sm_t_types_tr_first} to {sm_t_types_tr_last}, "
              "\u03c1 {sm_t_types_tr_rho}, p {sm_t_types_tr_p}) and pooled {sm_t_types_all_first} to "
              "{sm_t_types_all_last}. *What it means.* **Verdict: {sm_v_types_full}.** The type the "
              "tilt rotor added is **not a fixed set** \u2014 it is the second tilting set of observation "
              "1 ({sm_here_sm_driver_corr} i), so the tilt rotor is not drifting toward CVT, it is "
              "becoming a multi-set tilt rotor and stays in class. Why it can move against cost "
              "without contradicting it: the type count is a poor proxy for cost when the added type "
              "is a copy of the first \u2014 the same motor, rotor and actuator on a second station. "
              "Production cost falls with commonality, and the codebook cannot see commonality.",
         figures=["sm_driver_corr"]),
    dict(id="drivers.answer", title="Do tilting joints fall (cost) or rise (regime transition)?",
         text="**Counted per propulsive unit they fall, so cost wins \u2014 and the earlier reading, "
              "that transition wins inside a class, does not survive the normalisation.** The raw "
              "count does rise inside the two classes that transition, Tilt Rotor and CVT, and is "
              "flat pooled over the corpus ({sm_t_joints_all_first} to {sm_t_joints_all_last}, "
              "p {sm_t_joints_all_p}). But those same aircraft are gaining propulsors, and divided "
              "by the units the joints have to move, tilting joints fall inside Tilt Rotor, are "
              "flat inside CVT and fall pooled. The mechanism is therefore one thing and not two: "
              "a firm that accepts tilting rotors adds a second set \u2014 the set buys hover pitch "
              "control without a cyclic hub, redundancy and units at once, and observations 1, 2 "
              "and 4 are that one move \u2014 while the tilting hardware per rotor gets lighter as it "
              "does. The mix points the same way: the class growing fastest, Lift + Cruise, has no "
              "tilting joint at all, and that is where the entrants of 2020-23 arrive. The record "
              "shows the levels; it does not show which one any firm weighed. Of the couplings the "
              "fixed physical drivers predict, one exists \u2014 empennage type against wing "
              "configuration (V {tk_dr_emp_wing_v}); the others are no stronger than a random "
              "pair."),

    # ---------------------------------------------------------------- M
    dict(id="M",
         text="**A bound on everything above, not a statement about the sector.** Every label was "
              "read from the drawings; against the whole-patent text reading the drawings recover the "
              "class well for the large winged classes (Tilt Rotor {tk_gt_tr}, Lift + Cruise "
              "{tk_gt_slc}) and badly for the small ones (Pitch-to-Cruise {tk_gt_ptc}, Hoverbike "
              "{tk_gt_hb}). Read every small-class number in this document as the least reliable on "
              "its page. Still owed: the labeller against himself — the relabel of 50 patents "
              "has not been run.",
         figures=["atlas_arch_gt"]),

    # ---------------------------------------------------------------- new questions
    # Each question owns ONE panel and prints it BEFORE its prose (author, 2026-09-23: "I want
    # to see the evidence by my eyes, not text"). The order comes for free: a node whose prose
    # lives in :data:`AFTER` rather than in :data:`TEXTS` renders as heading, panel, prose —
    # and because the id is NOT in :data:`NO_KEEP`, the heading and the panel travel together,
    # so a question is never printed on one page and its evidence on the next. The panels are
    # drawn by :mod:`sm_figures`, which exists for this section and is imported nowhere else;
    # the full document is untouched and still points at its own figures.
    # 2026-09-24: the six "new questions" are folded into the chapters they belong to (ducting ->
    # 2.3, the weighting -> 2.2, CVT · 5-6 -> 2.3, Tilt Wing entrants -> this section for every
    # class, TRL -> 1.2 as a representativeness test); the citation question is cut.
    dict(id="entrants", title="What every class's entrants arrive with",
         text="**Arrival, not conversion, moves the mix.** Lift + Cruise takes {tk_cm_e_slc} of the "
              "firms entering in 2020-23 against {tk_cm_a_slc} of the window's aircraft; Tilt Wing "
              "takes {sm_tw_ent_2023} of the entrants against {sm_tw_air_2023} of the aircraft — the "
              "one class where firms keep arriving after the share has peaked, and the one class "
              "the firms then leave: only about one Tilt Wing succession in six stays in Tilt Wing, "
              "against roughly six in ten for Lift + Cruise and Tilt Rotor, and more leavers go to "
              "Tilt Rotor than stay. **The tilting wing is a first design firms pass through.** The "
              "entering population is also changing shape — in 2020-23 most entering filers are "
              "named organisations rather than individuals — but this corpus carries no "
              "capitalisation, funding or headcount, so whether the newcomers are better financed "
              "than the ones before them cannot be answered from it.",
         figures=["sm_entry_all"]),

    dict(id="cannot", title="What this record will never tell you, and what it has not yet been asked"),

    # The taxonomy drawing closed this document until 2026-09-23; the author has printed it
    # already, so it is dropped here and stays Appendix D of the full document. The two
    # in-text pointers to it — the opening paragraph of Q1 and the class line of Q2 — now
    # name that document, through ``{sm_ref_codebook_classes}``, which resolves to the number
    # the full document gives the drawing at this render.
]


# --------------------------------------------------------------------------
# 1b — the fold to four questions (2026-09-23, author's ruling)
# --------------------------------------------------------------------------
# The eight questions became four in the full document; this one follows, and follows it as
# DATA rather than as a rewrite: every section above keeps its prose, its figures and its
# tables and becomes a subsection of the question it now belongs to. A chapter opens with the
# ANSWER written for the full document (``la_lines.ANSWER``), so the brief and the long
# document answer each question with the same words, and the evidence sections follow.

#: old section id -> (new chapter, order in it, the heading it now prints)
FOLD = {
    "Q1": ("1", 1, "The record itself: how early, how complete"),
    "Q1b": ("1", 2, "How live it is: what lapsed"),
    "Q8": ("1", 3, "The record against what the industry actually builds"),
    # 2026-09-26 (chapter-2 review): the old chapter 2 split in two — 2 the design space,
    # 3 its evolution and the dominant-design test; old 3 and 4 become 4 and 5
    "Q4": ("2", 1, "What the design space is made of"),
    "arch": ("2", 2, "Archetypes and the level of detail"),
    "space": ("2", 3, "Where designs concentrate"),
    "Q2": ("3", 1, "What is gaining, and what is fading"),
    "Q3": ("3", 2, "The dominant-design test"),
    "inclass": ("3", 3, "Inside each class"),
    "drivers": ("3", 4, "Design drivers and their traces"),
    "Q5": ("4", 1, "Who files"),
    "Q7": ("4", 2, "Whether one firm carries the reading"),
    "entrants": ("4", 3, "What every class's entrants arrive with"),
    "Q6": ("5", 1, "Where it is designed, and whether region changes the design"),
    "Q6b": ("5", 2, "Whether region changes the timing"),
    "portfolio": ("5", 3, "How a firm builds its portfolio"),
}

# --------------------------------------------------------------------------
# 1c — the questions (2026-09-24, author's ruling: "only the important ones are questions,
# the rest are observations of that section")
# --------------------------------------------------------------------------
#: the chapter question, printed whole as the chapter heading. Since 2026-09-25 the wording is
#: identical to ``la_lines.QUESTIONS4`` (the full document) — keep the two in step.
SM_QUESTIONS = {
    # 2026-09-26 (author's chapter-1 review, C1): the chapter questions are the thesis's eVTOL-
    # sector morphology questions, worded so they can head a Method section and a Results section
    "1": "How has the eVTOL patent record grown, and how well does it represent the aircraft "
         "the sector builds?",
    "2": "What does the eVTOL design space look like: what is a design made of, and where do "
         "designs concentrate?",
    "3": "Is there a dominant eVTOL design or is the field still experimenting, and how have the "
         "designs changed over twenty years of filing?",
    "4": "Which kinds of firm, institute and inventor patent eVTOL aircraft, and which designs and "
         "filing strategies do firms of different maturity follow?",
    "5": "Do North America, Europe and Asia-Pacific design different eVTOL aircraft, or the same "
         "aircraft at different times?",
}

#: the sub-questions: (chapter, printed before the FOLD member with this order, number, wording).
#: Each is a heading of its own; the FOLD sections that follow it are its observations.
SUBQ = [
    # 2026-09-26 (C12, C19): a question comes BEFORE its result, so none of them may state one
    ("1", 1, "1.1", "How fast has eVTOL patenting grown, and how early does it show a design?"),
    ("1", 2, "1.2", "What share of the patented aircraft is still protected, and does it differ "
                    "between architecture classes?"),
    ("1", 3, "1.3", "How faithfully do the patented aircraft describe the aircraft the industry "
                    "builds, and can the built ones stand for the rest?"),
    # 2026-09-26 (chapter-2 review): the new chapters 2 and 3
    ("2", 1, "2.1", "What is an eVTOL design made of: which features vary and which barely do?"),
    ("2", 2, "2.2", "How are designs grouped into archetypes, and at which level of detail is the "
                    "space read?"),
    ("2", 3, "2.3", "Where do designs concentrate, and is the design space still opening?"),
    ("3", 1, "3.1", "Which architectures gain and which fade, and does the public directory show "
                    "the same?"),
    ("3", 2, "3.2", "Is there a dominant design?"),
    ("3", 3, "3.3", "Do designs converge inside each architecture class?"),
    ("3", 4, "3.4", "What drives the changes inside the classes?"),
    # 2026-09-27: author's titles for chapters 4 and 5 (no "who", no presupposed result)
    ("4", 1, "4.1", "Which kinds of filer — companies, universities, individual inventors — file "
                    "eVTOL patents, and does any single firm hold enough of an architecture class "
                    "to decide its share?"),
    ("4", 3, "4.2", "Is the eVTOL design space reshaped by firms filing their first aircraft or by "
                    "firms filing again, and where does a firm's next design land?"),
    ("5", 1, "5.1", "Which classes, propulsive-unit counts and tilting choices does each region "
                    "file, and how has each region's mix moved since 2012?"),
    ("5", 2, "5.2", "In what order do the regions take up each architecture class, and is the "
                    "recent fall in North America's share of new aircraft real or a publication "
                    "delay?"),
    ("5", 3, "5.3", "Do the three regions converge on the same design, and does any region's lean "
                    "depend on a single firm?"),
]

#: new id of every old node, including the children of the archetype premise (Q3.1 … Q3.4)
REKEY = {}
for _old, (_ch, _k, _t) in FOLD.items():
    REKEY[_old] = f"{_ch}.{_k}"
for _n in OLD_NODES:
    _i = _n["id"]
    if "." in _i and _i.split(".")[0] in FOLD:
        _head, _tail = _i.split(".", 1)
        REKEY[_i] = f"{REKEY[_head]}.{_tail}"


def _rekey(d):
    """A register keyed by the old ids, re-keyed to the new ones; unknown keys pass through."""
    return {REKEY.get(k, k): v for k, v in d.items()}


def _build_nodes():
    out = []
    for chapter in ("1", "2", "3", "4", "5"):
        out.append(dict(id=chapter, answer=True))
        kids = sorted(((v[1], k) for k, v in FOLD.items() if v[0] == chapter))
        for order, old_id in kids:
            for ch, before, num, wording in SUBQ:
                if ch == chapter and before == order:
                    out.append(dict(id=f"{chapter}.q{num.split('.')[1]}", subq=num,
                                    title=wording))
            for n in OLD_NODES:
                i = n["id"]
                if i == old_id or i.startswith(old_id + "."):
                    n = dict(n)
                    n["id"] = REKEY[i]
                    if i == old_id:
                        n["title"] = FOLD[old_id][2]
                    out.append(n)
    for n in OLD_NODES:                      # M, the new questions and the closing section
        if n["id"].split(".")[0] not in FOLD:
            out.append(dict(n))
    return out


NODES: List[Dict] = _build_nodes()

# ---------------------------------------------------------------------------
# 2026-09-25 — the items the review rebuild added. Kept as a separate map rather than folded
# into ``OLD_NODES`` so that the FOLD/REKEY machinery above is untouched and the additions of
# one review round can be read, and reversed, in one place. Each id is a node of ``NODES``;
# the figure or table is appended to what that node already carries, never replacing it.
# ---------------------------------------------------------------------------
NEW_ITEMS: Dict[str, Dict[str, List[str]]] = {
    # the aircraft that carry a real product name against the generated ones — the table the
    # author asked for so the "90 % of the matched aircraft" sentence can state its own base
    "1.3": dict(tables=["la_name_coverage"]),
    # 2026-09-27 (F12): the AAM Reality Index timeline, next to Figure 2 (ari_clock) — first
    # patent here against first flight and planned entry into service as the index reports them
    "1.1": dict(tables=["la_ari_timeline"]),
    # 2026-09-26: keys follow the five-chapter layout (old 2.3 → 2.1, 2.4 → 3.4, 3.3 → 4.3,
    # 4.2 → 5.2); the family now sits on Q3 itself and its verdict table is cut (C59)
    # the all-or-nothing reading of ducting
    "2.1": dict(figures=["sm_duct_conditional"]),
    # the correction: tilting joints normalised by the propulsors they have to move
    "3.4": dict(figures=["sm_joints_per_unit"], tables=["la_joints_per_unit"]),
    # where the firms that leave Tilt Wing go
    "4.3": dict(tables=["la_tw_successions"]),
    # the test behind "the lead is real, the size of the gap is not settled"
    "5.2": dict(tables=["la_lag_constancy"]),
}
for _node in NODES:
    _extra = NEW_ITEMS.get(_node["id"])
    if not _extra:
        continue
    for _key, _vals in _extra.items():
        _have = list(_node.get(_key) or [])
        _node[_key] = _have + [x for x in _vals if x not in _have]
del _node, _extra, _key, _vals, _have



#: the one section that opens a fresh page. ``report.write_markdown`` treats a top-level node
#: whose id is in ``APPENDIX`` as a chapter, and ``build_styled_md_pdf`` breaks a page before a
#: ``div.chapter-start``. Everything else flows, which is what keeps the document short.
APPENDIX = ("new", "1", "2", "3", "4", "5")

#: ids that are their own page. Used by :func:`depth` — see its docstring.
_TOP = set(APPENDIX)

#: sections whose heading travels with its PROSE but not with the figure under it.
#: ``report.write_markdown`` otherwise puts heading, prose and first figure inside one
#: unbreakable block; with figures five to eight inches tall that block does not fit in what
#: is left of a page, so it moves whole and leaves the page it came from two thirds empty —
#: which is what left page 1 holding nothing but the title, and pages 15 and 17 half blank.
#: Every section that owns an item is listed — a long table costs as much as a figure: the
#: verdict table alone left two thirds of the page before it empty — so the item starts where
#: it lands and the page before it fills. The heading is still never orphaned: it sits in a
#: block with the answer paragraph, and the stylesheet forbids a break after a heading.
#: the six new-question sections are the exception: their panels are 2.2 to 2.9 in tall, a
#: heading and a panel fit in what is left of almost any page, and a question printed without
#: its evidence under it is the thing this section was rebuilt to stop.
PANEL_SECTIONS = tuple(n["id"] for n in NODES if n["id"].startswith("new."))

NO_KEEP = tuple(n["id"] for n in NODES
                if (n.get("figures") or n.get("tables")) and n["id"] not in PANEL_SECTIONS) + (
    # the chapter that opens on the methods box (2026-09-25): the box is most of a page on its
    # own, so an unbreakable block around it would empty the page before it and still overflow.
    # The box carries its own heading and its own rule, so it needs no keep.
    "2",)


# --------------------------------------------------------------------------
# 2 — prose that is not a node's own text
# --------------------------------------------------------------------------
#: the lead paragraph of each question section, printed before the answer: the question
#: itself, in full, straight out of ``la_index.QUESTIONS``. Nothing is restated here.
def _question_line(nid: str) -> str:
    q = SM_QUESTIONS.get(nid) or _la.QUESTIONS.get(nid)
    if not q or q.strip() == _question_title(nid):     # the heading already IS the question
        return ""
    return f"*The question in full: {q}.*"


#: what the section heading says. For a question section it is the first clause of the
#: question — everything before the em dash — so a rewrite of the question rewrites the
#: heading, and a question with no em dash prints whole.
def _question_title(nid: str) -> str:
    if nid in SM_QUESTIONS:                          # printed whole: the question IS the heading
        return SM_QUESTIONS[nid]
    q = _la.QUESTIONS.get(nid, nid)
    return q.split(" — ")[0].strip()


TEXTS: Dict[str, str] = {
    # ---- Q3's premise, in three parts (restored 2026-09-23; cut to the point the same day:
    # short definitions, the tables carry the detail, nothing of the full document's argument
    # is repeated).
    "Q3.1":
        "An **archetype** is a combination of label answers: fix a set of dimensions, write each "
        "aircraft as its answers on them (*{sm_a1t_top}*, *{sm_a0c_top}*), and two aircraft share "
        "an archetype when the string is the same. The count depends entirely on the level: at "
        "A0 (the class alone) {sm_a0_arch} archetypes, at A2c {sm_a2c_arch} of which "
        "{sm_a2c_single} hold one aircraft. A convergence claim has to name its level. The table "
        "keeps the three levels this document reads.",

    "Q3.2":
        "Four screens fixed in code choose the level, not the answer: *resolution* (at least twice "
        "as many archetypes as classes), *fragmentation* (how much of the corpus sits alone), "
        "*population* (how much sits in archetypes big enough to measure), *readable shares*. "
        "{sm_arch_pass} of {sm_arch_levels} levels clear all four: **A1t** ({sm_a1t_dims}), the "
        "design species, and **A0c** ({sm_a0c_dims}), reported beside it because it is the only "
        "level at which condition 2 ever fires.",

    "Q3.3":
        "The three conditions in one line each; how each is tested, and where each comes from, is "
        "the methods box at the head of this chapter.\n\n"
        "**Counts** — one archetype holds more than 50 % of a window's aircraft, in two "
        "consecutive complete windows. **Balance** — the designs in play collapse toward one or "
        "two: ²D falls below the permutation band. **Form** — the aircraft themselves become "
        "alike: the mean distance between two aircraft of the window falls below the two earliest "
        "windows' level by more than the shuffle gives. A dominant design needs all three in one "
        "complete window.\n\n"
        "*Two designs instead of one.* Condition 1 is written for one archetype; a duopoly would "
        "show as the top TWO archetypes holding more than 50 % together. The highest top-2 share "
        "in any window is {sm_top2}, at {sm_top2_level} in {sm_top2_window} — no duopoly either.\n\n"
        "*Both bands are the year-shuffling permutation test of the methods box:* condition 2 reads "
        "²D on each shuffle and condition 3 reads Q.",

    "Q3.4":
        "**Condition 1 is not close**: the largest archetype of any window reaches {tk_dd_top_share} "
        "against 50 %. **Condition 2** fires in {tk_dd_below} of {tk_dd_cells} level-windows, all at "
        "A0c and only in the two earliest windows, the ones with the least data. **Condition 3** "
        "fires in {tk_q_below} of {tk_q_cells} cells, in 2020-23 and only under the subsystem "
        "weighting — under uniform weighting the same window stays inside its band (second figure), "
        "so the one signal the test finds is a choice of weighting, not a finding.\n\n"
        "**One family, tested because the record suggested it — and it fails too.** Observation 3 "
        "of the drivers section shows the late CVT converging on a Lift + Cruise layout: open "
        "rotors on booms, with one tilting set added. If distributed electric propulsion is the "
        "real commonality, Lift + Cruise and the boom-layout CVT should be read as one family "
        "rather than as two classes. Tested on that definition — **post hoc**, after the curves "
        "were drawn, and marked as such wherever it appears — the family holds {sm_fam_c_n} "
        "aircraft and reaches {sm_fam_c_peak} of the 2020-23 window; the widest definition tried "
        "reaches {sm_fam_b_peak}. That is the closest anything in this corpus comes to the 50 % "
        "line, and it clears it in {sm_fam_windows_met} of the four complete windows, so never "
        "twice in a row. Condition 3 is met in {sm_fam_c3_cells} of {sm_fam_c3_total} "
        "level-windows. **Verdict: no, on every definition.** The result is worth printing "
        "precisely because the family is larger than any single class and still does not "
        "constitute a dominant design.",

    "Q3.4b":
        "**Three branches, not one design and not two — and they are the same three in every "
        "window.** The *design species* (A1t) is the coarsest description that still separates "
        "designs: the architecture class, plus how many wings the aircraft has, plus whether at "
        "least one of its propulsors tilts. At that level the one-wing Lift + Cruise, the one-wing Tilt "
        "Rotor and the one-wing Combined Vectored Thrust are the three largest archetypes of every "
        "complete window and hold about half of it together ({sm_top3_a1t_w1} in the earliest "
        "window, {sm_top3_a1t_w3} in 2016-19, {sm_top3_a1t_w4} in 2020-23); no one of them passes "
        "a quarter of it: no single archetype holds more than 25 % of its own window, against the "
        "50 % the first condition asks for. The leadership inside the three changed once: Tilt Rotor led until 2016-19, "
        "Lift + Cruise leads since ({sm_top1_a1t_w4} in 2020-23). At the class level (A0) the same "
        "three classes hold {sm_top3_a0_w4} of 2020-23 — the sector has a stable set of three "
        "concepts, not a winner. One level down, at the rotor count (A0c), nothing holds: the "
        "three largest archetypes together are {sm_top3_a0c_w4} of 2020-23, and the largest is a "
        "different one in almost every window. So the branches are firm and what is inside each "
        "branch is still open — which is where the next figure looks.",

    "Q3.5":
        "The old configuration key (units · ducted · booms · tail) called every class diverse "
        "because it counted fields the class does not choose. Each class is now read on the labels "
        "that tell its OWN aircraft apart. Ducting was taken out of those rules on the author's "
        "ruling — it is not what tells one Lift + Cruise from another — so the rules are: Lift + "
        "Cruise, whether the lift units retract or fold, and the propulsive-unit band; Tilt Rotor, "
        "one or more tilting types, and the band; CVT, how many types tilt against how many are "
        "fixed, and the band; Tilt Wing, one or more wings, and the band; Multirotor, booms or no "
        "booms, and the band. Dropping the duct concentrates every class, because that one field "
        "had been splitting each configuration in two, and **no class settles even so**: the most "
        "common configuration tops out at under a third of its class in 2020-23, and "
        "{top_class}'s {tk_slc_n_2023} aircraft of that window still spread over "
        "{sm_own_slc_configs} configurations.",

    "new.1":
        "**The measure.** Ducting does not follow the calendar and does not follow the map, but it "
        "follows rotor count, and not in a straight line: {sm_duct_13} of the aircraft with three "
        "or fewer propulsive units carry a ducted unit, {sm_duct_78} of those with seven or "
        "eight, and {sm_duct_9} of those with nine or more, against {sm_duct_all} over the whole "
        "corpus. It is not the class mix in disguise — the dip is there inside Lift + Cruise, "
        "Tilt Rotor and CVT taken one at a time, and the band still moves the answer with the "
        "class held fixed. The per-class rows behind that control are `tables/la_duct_units.csv`, "
        "and the same measure sits inside {sm_here_sm_propulsion_compact} with the rest of the "
        "propulsion picture.\n\n"
        "**Why it is a question.** A U-shaped curve means a duct is being bought for two "
        "different reasons at the two ends of the range and for neither reason in the middle. "
        "That is a design statement this corpus can suggest but not test, because the label "
        "records only whether *any* unit is ducted — one ducted fan among twelve open rotors "
        "counts the same as twelve ducted ones.\n\n"
        "**What would answer it.** A count of ducted units per aircraft, beside the existing "
        "yes/no, on the aircraft in the two end bands only; or the patents' own stated reason, "
        "read from the text of the {sm_duct_9_n} aircraft at nine units and above that do duct. "
        "The first is a labelling pass over one field; the second is a reading pass.",

    "new.2":
        "**The measure.** Of the three pre-registered conditions, only the third ever fires in a "
        "recent window, and it fires {sm_c3_met}. Under the uniform weighting drawn beside it, "
        "the same level-windows sit inside the permutation band and the condition does not fire "
        "at all: at 2020-23 the main weighting falls {sm_c3_gap_main} below the lower edge of "
        "its own band and the uniform one stops {sm_c3_gap_alt} above the edge of its own. It "
        "is condition 3 of {sm_here_la_dd_result}, and the two conditions that do not fire are "
        "drawn in {sm_here_dominant_design}.\n\n"
        "**Why it is a question.** The whole value of the dominant-design test is that its "
        "thresholds were fixed before the curves were drawn. A result that appears under one of "
        "two weightings and not the other is not a threshold problem — it is a signal that the "
        "answer is sensitive to a choice nobody pre-registered as carefully as the thresholds. "
        "It matters because condition 3 is the only one that is about the aircraft becoming "
        "similar, rather than about one label getting bigger.\n\n"
        "**What would answer it.** The same test over a range of weightings between the two, "
        "reported as a curve of ΔQ against the weighting rather than as a yes or no — the code "
        "already computes both endpoints, so this is a loop, not a new method. If the sign holds "
        "across the range it is a finding; if it changes sign inside it, the honest statement is "
        "that the corpus has no answer on condition 3.",

    "new.3":
        "**The measure.** CVT · 5-6 holds {sm_cvt56_air} aircraft from {sm_cvt56_filers} distinct "
        "filers — {sm_cvt56_fpa} filers per aircraft, the lowest of any archetype in the corpus "
        "with twenty aircraft or more, against {sm_cvt4_fpa} for CVT · 4 next door. It is also "
        "one of the fastest-growing: {sm_cvt56_win2023} of its aircraft are in 2020-23. CVT as a "
        "class puts {sm_cvt_own_2023} of its own aircraft in that one window. The panel ranks "
        "every archetype of that size on the one column; the archetype is also a cell of "
        "{sm_here_zones} and a row of `tables/la_zones.csv`.\n\n"
        "**Why it is a question.** At class level this is settled — CVT divides as if between "
        "{tk_fw_cvt_eff} equal filers and no firm moves its share by more than "
        "{tk_lev_pp} points. But the class is not what a reader looks at when they see a bar "
        "rise; the archetype is. A filers-per-aircraft of {sm_cvt56_fpa} means the average filer "
        "in this archetype holds about two of its aircraft, which is the pattern a firm's own "
        "line of variants makes.\n\n"
        "**What would answer it.** One column in the zones table that the class-level table "
        "already has: the share of the archetype held by its single largest filer, and the "
        "effective number of filers, per archetype rather than per class. The inputs are in "
        "`tables/la_zones.csv` already — only the largest-filer share is missing, and it is the "
        "same computation as the class column.",

    "new.4":
        "**The measure.** Tilt Wing peaks and comes back down rather than trending: it puts "
        "{sm_tw_1619} of its {sm_tw_n} aircraft in 2016-19 and {sm_tw_2023} in 2020-23, and its "
        "median window is 2016-19 while Lift + Cruise and CVT both sit in 2020-23. Yet firms keep "
        "arriving with it: {sm_tw_ent_2023} of the firms entering in 2020-23 enter with Tilt "
        "Wing, against {sm_tw_air_2023} of that window's aircraft. The panel puts the two "
        "counts side by side, window by window — five comparisons, not a trend; the class "
        "shares over time are drawn in {sm_here_atlas_arch_time}.\n\n"
        "**Why it is a question.** Everywhere else in this corpus entrants over-index on the "
        "class of their moment, and that is the mechanism behind the whole of Q2. Tilt "
        "Wing is the case where entrants over-index on a class whose share is falling. Either the "
        "entrants are late and will follow, or Tilt Wing is a first design that firms pass "
        "through — and the two have opposite implications for reading any share as a trend.\n\n"
        "**What would answer it.** The within-firm successions restricted to the firms that "
        "entered with Tilt Wing: what their next aircraft is. The succession machinery exists "
        "({sm_ref_transitions} of the full document, {tk_trans_pairs} pairs); it has never been "
        "cut by the class a firm entered with. The technology-readiness table "
        "({sm_here_a2_d15_trl_by_class}) is the second half of the answer — Tilt Wing sits at "
        "{sm_trl_tw} above TRL 2.",

    "new.5":
        "**The measure.** {trl_above_s} of the {trl_aircraft_s} aircraft ({sm_trl_share}) have "
        "reached anything above TRL 2; {sm_trl_nottracked} of them are not tracked by the public "
        "record at all, and four classes — {trl_zero_classes} — have not one aircraft above TRL 2 "
        "between them. Read over the {sm_trl_tracked_n} aircraft a public source does follow, "
        "the same {trl_above_s} are {sm_trl_tracked_share}. The per-class rows are "
        "{sm_here_a2_d15_trl_by_class}.\n\n"
        "**Why it is a question.** TRL 2 is the level assigned when nothing better is known, so "
        "the table as it stands cannot separate *this aircraft was never built* from *no public "
        "source follows this aircraft*. That distinction decides whether the tenth of the corpus "
        "above TRL 2 is the sector's real build rate or the coverage rate of one directory — and "
        "the second reading would also explain the four empty classes, which are exactly the "
        "classes an eVTOL directory has least reason to list.\n\n"
        "**What would answer it.** A second, independent public source over the same aircraft "
        "names, and a rule that distinguishes *not found* from *found and at TRL 2*. Until then "
        "every TRL statement in this document is a floor, and should be written as one.",

    "new.6":
        "**The measure.** The aircraft of the firms the AAM Reality Index rates sit at a cohort "
        "citation rank of {sm_cite_idx} against {sm_cite_rest} for every other aircraft in the "
        "corpus — a full cohort rank apart, q {sm_cite_q} after correction over the whole table, "
        "and it holds on the US-published patents alone (p {sm_cite_us}), so it is not the office "
        "effect that removes two of the other differences. The panel is the two distributions "
        "the medians come from; the row itself is in `tables/la_ari_gap.csv` (cut from chapter 1 on 2026-09-26).\n\n"
        "**Why it is a question.** The cohort rank is computed against patents of the same year, "
        "so it is not an age effect. That leaves three readings that this corpus cannot tell "
        "apart: the rated firms file better patents; the rated firms are cited more because they "
        "are visible, and the index is a proxy for that visibility; or both are caused by the "
        "funding that the index scores. The last would make the citation rank a market "
        "measurement wearing a patent measurement's clothes.\n\n"
        "**What would answer it.** The citation rank of each index firm's patents against the "
        "year it first appeared in the index. If the advantage is there before the listing, it is "
        "about the patents; if it opens after, it is about visibility. The index history back to "
        "December 2020 is already stored in `assets/external/aam_reality_index/`, and the "
        "citation ranks are already computed per patent.",

    "cannot":
        "Fourteen questions were put to this record by the industry side of the project. **Six "
        "are answered** in the chapters above: whether the sector is converging "
        "({sm_here_sm_dd_conditions}, {sm_here_la_dd_levels}), which sub-variants stay open "
        "({sm_here_zones}, {sm_here_sm_class_configs}), whether the field is concentrated "
        "({sm_here_coverage}, {sm_here_la_class_filer_weight}), whether propulsor counts settle on "
        "six to eight ({sm_here_sm_propulsion_compact}) and whether regions build differently "
        "({sm_here_atlas_region}, {sm_here_la_class_region_timing}). Some of those answer *no* to "
        "the question as it was asked, which is still an answer, and convergence gets a qualified "
        "*yes*, resting on choices made after the first readings (3.2). The other eight are printed here "
        "with the reason, because a reader is owed the boundary of the instrument.\n\n"
        "**{sm_next_table} — What this record cannot answer, question by question: the eight "
        "stakeholder questions it answers only in part or not at all, and the reason.**\n\n"
        "| Question | Verdict | Why |\n"
        "|---|---|---|\n"
        "| Do patents track substance rather than press attention? | no | The only handle is the "
        "citation rank of the index firms' patents, and a citation follows a firm's visibility as "
        "much as the quality of the patent; the record cannot tell the two apart. |\n"
        "| Do filings lead or lag commercial emergence? | partly | Holds for the five largest classes "
        "only; the commercial side rests on the {sm_pw_n} aircraft with a public counterpart and the "
        "{trl_above_s} above TRL 2. No per-class lead time for the small classes. |\n"
        "| Are there hype cycles — exotic configurations later abandoned? | partly | Legal status is a "
        "snapshot, alive or dead at the export date, with no lapse date in the labelled data, so "
        "*time* to abandonment cannot be drawn. |\n"
        "| Is convergence happening inside one mission segment while diversity persists elsewhere? | "
        "no | Mission is not a label. It exists only for the aircraft with a public page, is "
        "majority-unspecified even there, and that subset fails the representativeness test on four "
        "of six attributes. |\n"
        "| Where is the mechanical white space against already-claimed territory? | no | The labels "
        "describe what is **drawn**, never what is **claimed**. Claim scope is not a field. |\n"
        "| Is hybrid-electric a bridge or a dead end? | no | Powertrain is one yes/no field. Battery, "
        "hybrid and fuel cell are nowhere distinguished, and none of the three is reliably visible in "
        "a drawing. |\n"
        "| Which architectures are the safer certification bet; does autonomy cluster by airframe? | "
        "no | No certification data of any kind is in the corpus, there is no autonomy label and no "
        "occupancy label. Examination outcome is an office effect, not a technology effect. |\n"
        "| Are architectures specialising into mission niches, increasingly over time? | no | The "
        "mission gap again, and no size handle to substitute for it: there is no payload, mass, "
        "wingspan or size field anywhere in the labels, and patent drawings are unscaled. |\n\n"
        "**Also out of reach, and why.**\n\n"
        "- **Noise, wind and weather.** Never labelled, and not stated in the patents.\n"
        "- **Battery energy against disc loading.** Disc loading needs rotor diameter, and no "
        "size, span, area or mass field exists; patent drawings are unscaled.\n"
        "- **A shakeout of firms.** Most firms whose last filing is 2019 or earlier filed only "
        "once, so leaving the sector cannot be told apart from never having had a programme.\n"
        "- **Firm design paths as sequences.** Too few firms file three aircraft or more for a "
        "path to be a pattern and not an anecdote.\n"
        "- **Time from patent to flight, per architecture.** About a dozen firms carry a first-"
        "flight date; split over twelve classes, that is no analysis.\n\n"
        "**Questions still open, and within reach.** Each uses data already held; none has been "
        "run for this document.\n\n"
        "*From the label table alone:*\n\n"
        "- **Are the twelve classes natural groups, or a cut through a continuum?** Group the "
        "aircraft by label similarity without their class, and compare the groups with the "
        "classes. A first probe shows weak agreement, which would make the classes a useful "
        "convention and not clusters the drawings impose.\n"
        "- **Which design choices force which?** The association between every pair of label "
        "fields, and how many independent directions the design space really has. A first probe "
        "points to many nearly independent choices and not a few coupled packages.\n"
        "- **Does the average design move while the variety stays?** The centre of the whole "
        "label space per window, against a shuffled-year band. A first probe says the centre moves "
        "further than chance while the spread does not shrink.\n"
        "- **Which archetypes appear, and which disappear?** First and last year of every "
        "archetype, and the turnover per window.\n\n"
        "*From the raw PatSeer export, fields known to be in it and never opened:*\n\n"
        "- **Where is the white space?** The full CPC codes crossed with the architecture class.\n"
        "- **Battery, hybrid or fuel cell?** The B64D27 subgroups separate the three, in place of "
        "the yes/no powertrain field.\n"
        "- **How long does a design stay protected?** The dated legal events turn the "
        "alive-or-dead snapshot of {sm_here_sm_force_aircraft} into a time to abandonment per "
        "class.\n"
        "- **How broad are the claims, per architecture?** Claim count and the length of the "
        "first claim, from the claims text.\n"
        "- **Autonomy.** The G05D1 codes and the B64U unmanned family, the only autonomy proxy the "
        "record holds, and a weak one.\n\n"
        "*From the same export, if it carries the field:*\n\n"
        "- **Who learns from whom?** Citations between aircraft of the corpus, read as flows "
        "between classes and regions: whether Lift + Cruise builds on Tilt Rotor, whether "
        "Asia-Pacific builds on North America.\n"
        "- **Who files together, and who moves?** Co-applicants (firms with universities, firms "
        "with firms) and inventors who file for more than one firm.\n"
        "- **Where does each firm protect its designs?** The offices a patent family extends to, "
        "per region and class, as a map of the markets firms expect to serve.\n\n"
        "Mission, payload, size, noise and certification stay out of reach from any of these: "
        "they need an outside population and another unit of analysis, which is another study.\n\n"
        "**References**\n\n"
        "Abernathy, W. J. and Utterback, J. M. (1978). Patterns of industrial innovation. "
        "*Technology Review*, 80(7), 40-47.\n\n"
        "Anderson, P. and Tushman, M. L. (1990). Technological discontinuities and dominant "
        "designs: a cyclical model of technological change. *Administrative Science Quarterly*, "
        "35(4), 604-633.\n\n"
        "Efron, B. (1979). Bootstrap methods: another look at the jackknife. *The Annals of "
        "Statistics*, 7(1), 1-26.\n\n"
        "Fisher, R. A. (1922). On the interpretation of chi-square from contingency tables, and "
        "the calculation of P. *Journal of the Royal Statistical Society*, 85(1), 87-94.\n\n"
        "Fisher, R. A. (1925). *Statistical Methods for Research Workers*. Oliver and Boyd.\n\n"
        "Mann, H. B. and Whitney, D. R. (1947). On a test of whether one of two random variables "
        "is stochastically larger than the other. *The Annals of Mathematical Statistics*, "
        "18(1), 50-60.\n\n"
        "Murmann, J. P. and Frenken, K. (2006). Toward a systematic framework for research on "
        "dominant designs, technological innovations, and industrial change. *Research Policy*, "
        "35(7), 925-952.\n\n"
        "Pearson, K. (1900). On the criterion that a given system of deviations from the "
        "probable in the case of a correlated system of variables is such that it can be "
        "reasonably supposed to have arisen from random sampling. *Philosophical Magazine, "
        "Series 5*, 50(302), 157-175.\n\n"
        "Spearman, C. (1904). The proof and measurement of association between two things. "
        "*American Journal of Psychology*, 15(1), 72-101.\n\n"
        "Suárez, F. F. and Utterback, J. M. (1995). Dominant designs and the survival of firms. "
        "*Strategic Management Journal*, 16(6), 415-430.\n\n"
        "Wasserstein, R. L. and Lazar, N. A. (2016). The ASA statement on p-values: context, "
        "process, and purpose. *The American Statistician*, 70(2), 129-133.\n\n"
        "Wilson, E. B. (1927). Probable inference, the law of succession, and statistical "
        "inference. *Journal of the American Statistical Association*, 22(158), 209-212.",
}


# --------------------------------------------------------------------------
# 2b — the methods box (2026-09-25, review comments C8, C9, C10, C12, C13, C34)
# --------------------------------------------------------------------------
# The author could not read the statistics: "across this section I don't know the way to read
# p", "what is 1D, how is it calculated", "how is the band created", "I need much more info
# about this test", "where is this from? is this a framework created?". One box, printed once,
# at the head of the chapter that uses all of it; every later mention of p, of a band or of an
# effective number points back here instead of re-explaining. Every number in it is a
# placeholder like everywhere else, and the two apparatus constants (how many shuffles, which
# seed, the rarefaction size) are READ OUT OF ``la_tables`` at render time by
# :func:`_method_numbers`, never typed, so the box cannot drift from the code that ran.
#:
#: The chapter the box opens. Printed by :func:`text` in place of that chapter's empty prose.
METHODS_CHAPTER = ""          # 2026-09-26: the box is split into the chapter modules

METHODS_BOX = (
    '<div class="methods-box">\n\n'
    "##### How to read the measures of this chapter\n\n"
    "*p and the four tests are introduced at the head of chapter 1; this box adds the "
    "measures only this chapter uses.*\n\n"
    "**¹D and ²D — the effective number of archetypes.** Counting archetypes treats a design "
    "held by one aircraft exactly like a design held by forty, so the count says nothing about "
    "how the corpus is actually divided. The effective number asks a better question: **if the "
    "window held N equally common archetypes and no more, how concentrated would it be? That N "
    "is the effective number.** ¹D weights each archetype by how common it is (the Shannon "
    "form); ²D weights the common ones harder still (the Simpson form), so a window with one "
    "large archetype and a long tail of singletons scores lower on ²D than on ¹D. Worked "
    "example, from the table below: at the class level this corpus uses {sm_a0_arch} classes, "
    "but its ¹D is {sm_a0_eff} — the twelve classes behave like about {sm_a0_eff} equally "
    "common ones, because most aircraft sit in a handful of them. Both numbers are *rarefied*: "
    "every window is cut to a random {sm_perm_n} aircraft before counting, the draw is repeated "
    "and averaged, so a large window cannot score higher merely by being large.\n\n"
    "**The permutation band.** A number on its own cannot say whether it is unusual, so the "
    "range that chance gives is built from the same data. Every aircraft keeps its labels and "
    "is given a **randomly reassigned priority year**; the statistic is recomputed on the "
    "reshuffled windows; this is repeated {sm_perms} times (seed {sm_perm_seed}, so the band "
    "is reproducible). The band drawn on the figures is the middle 95 % of those {sm_perms} "
    "results. A real value **inside** the band is what any split of this corpus into windows of "
    "these sizes would show — not a near miss, a null. A real value **outside** it is structure "
    "that the years carry, and falling outside is the condition the test asks for.\n\n"
    "**The three dominant-design conditions, and where each comes from.**\n\n"
    "- **1 — counts.** One archetype holds more than 50 % of a window's aircraft, in two "
    "consecutive complete windows. This operationalises **Anderson and Tushman (1990)**, whose "
    "test is one design holding more than 50 % of new product sales for four consecutive years, "
    "moved onto what a patent record can see: aircraft instead of sales, and two consecutive "
    "four-year windows instead of four years. The concept being tested is **Abernathy and "
    "Utterback (1978)**.\n"
    "- **2 — balance.** The designs in play collapse toward one or two: ²D falls below the "
    "permutation band.\n"
    "- **3 — form.** The aircraft themselves become alike: the mean distance between two "
    "aircraft of a window (0 identical, 1 nothing in common, over every labelled field) falls "
    "below the two earliest windows' level by more than the shuffle gives.\n"
    "- **Conditions 2 and 3 are this thesis's own measurements, and are stated as such.** The "
    "literature says in words that variety collapses (Utterback) and that the core subsystems "
    "converge (**Murmann and Frenken, 2006**, the nested-hierarchy account); neither statement "
    "has been given a threshold and tested on a patent record. No published test is reproduced "
    "by conditions 2 and 3, and no citation is claimed for their thresholds.\n"
    "- **What is deliberately not used.** **Suárez and Utterback (1995)** date a dominant design "
    "by the shakeout of firms that follows it. That test is not run here, because Chapter 3 "
    "shows this sector is still in its entry phase — in every window most active firms are "
    "filing for the first time — so there is no shakeout to date anything by. Leaving it out "
    "is a reasoned choice, not an omission.\n\n"
    "All three thresholds were fixed before any curve of this corpus was drawn, which is what "
    "makes a 'no' a finding rather than a description.\n\n"
    "</div>\n"
)


AFTER: Dict[str, str] = {
    # The Q3 note that used to stand here — "the three thresholds are Table 1.1.3.2 of the full
    # document" — was deleted on 2026-09-23 when Q3.3 began printing that table itself.
    "Q8":"*The AAM Reality Index is one index, not two: AAM for the field, ARI for the score. "
          "It is an analyst's judgement, published quarterly, not a measurement — section 1.2.7 "
          "of the full document states what it is and is not, and what it is joined to this "
          "corpus by.*",
}


# --------------------------------------------------------------------------
# 3 — captions, widths, row caps and columns
# --------------------------------------------------------------------------
# Copies, never the same object as ``la_index``'s: the render script rewrites FIG_WIDTH from
# the PNGs on disk, and it must not reach the full document's module while doing it.
FIGURE_CAPTIONS: Dict[str, str] = dict(_la.FIGURE_CAPTIONS)
TABLE_CAPTIONS: Dict[str, str] = dict(_la.TABLE_CAPTIONS)
FIG_WIDTH: Dict[str, str] = dict(_la.FIG_WIDTH)
LANDSCAPE = set(_la.LANDSCAPE)

#: shorter captions where the full document's caption is a paragraph of how-to-read. The
#: how-to-read belongs in the full document; here the caption names the object.
FIGURE_CAPTIONS.update({
    # 2026-09-24, the drivers section as observations
    "sm_driver_traces": "the four traces that moved, per class and priority window: **(i)** tilting joint groups, mean per aircraft; **(ii)** propulsive units, median per aircraft; **(iii)** propulsor types, mean per aircraft; **(iv)** share of aircraft with a ducted unit. A point needs five aircraft in the class-window; priority year ≤ 2023",
    "sm_driver_corr": "the correlation behind each observation: **(i)** Tilt Rotor, share of aircraft with two or more tilting propulsor sets against share with any fixed set, per window; **(ii)** Tilt Rotor, median propulsive units by number of tilting sets; **(iii)** CVT, share with units on booms, and share ducted among the aircraft with and without units on booms (a point needs four aircraft)",
    # the author asked how panel (ii)'s classes are ordered (2026-09-23): by class size,
    # largest first — ``atlas.ALL_ARCH``, the fixed order every class figure shares
    "atlas_units": "propulsive units and their arrangement. In every panel the classes run "
                   "left to right in the fixed order every class figure shares, which is by "
                   "size, largest first (Lift + Cruise, Tilt Rotor, CVT, …; the one departure "
                   "is Tilt Body drawn before Pitch-to-Cruise, one aircraft larger)",
    "dimension_drift": "dimension drift inside each architecture class, per window: (i)–(iv) "
                       "the four fields of a configuration read one at a time, then powertrain. "
                       "A line is a class, not an archetype; every share is of that class's own "
                       "aircraft in that window, never of rotors — except the powertrain panel, "
                       "which divides by the aircraft whose patent states one",
    "class_configs": "within-class convergence: how far each architecture class settles on a "
                     "single configuration. A configuration is one aircraft's combination of "
                     "propulsive units (banded), ducted or open, booms or no booms, and tail "
                     "type; every class with 5+ aircraft in 3+ windows is drawn",
    # ---- the six panels of the new questions. Each caption names the object and nothing else:
    # the reading is the grey line under it and the question is the heading above it.
    "sm_duct_bands": "a ducted unit against the number of propulsive units. Each bar is the "
                     "share of that band's AIRCRAFT carrying at least one ducted unit, never a "
                     "share of rotors; the dashed line is the same share over every band",
    "sm_weighting": "condition 3 of the dominant-design test — ΔQ per priority window against "
                    "the permutation band — under both weightings and at both archetype "
                    "levels. A ringed point falls below the lower edge of its own band, which "
                    "is the condition met; the hatched window is still incomplete",
    "sm_archetype_filers": "distinct filers per aircraft, for every archetype holding twenty "
                           "aircraft or more. 1.00 means no filer holds two of the archetype's "
                           "aircraft; CVT · 5-6 and the neighbouring CVT · 4 are marked",
    "sm_tw_entry": "Tilt Wing's share of each window's aircraft beside its share of that "
                   "window's entering firms — five separate comparisons, one per window, and "
                   "not a trend: the two counts have different units and different bases, both "
                   "printed on the tick",
    "sm_trl_tracked": "technology readiness over the whole corpus and over the tracked aircraft "
                      "alone, with the aircraft no public source follows as a band of their own "
                      "rather than inside TRL 2",
    "sm_cite_rank": "the cohort citation rank of the index firms' aircraft against every other "
                    "aircraft in the corpus, as two distributions. A rank is taken inside the "
                    "patent's own priority year, so age is already out of it",
    # 2026-09-24
    "sm_duct_count": "ducting counted in units, per propulsive-unit band: aircraft with any ducted "
                     "unit (hollow), the share of the band's units in a duct (filled), and on the "
                     "bar the median ducted units of the ducting aircraft and the share that duct "
                     "every unit",
    "sm_entry_all": "what the firms entering each window arrive with, for the five largest classes: "
                    "the class's share of the window's entering firms (hatched, count on the bar) "
                    "beside its share of the window's aircraft (grey)",
    "sm_class_configs": "within-class convergence on each class's own differentiating labels: (i) "
                        "share of the class in its most common configuration, (ii) distinct "
                        "configurations per aircraft; a window under five aircraft is not drawn",
})

TABLE_CAPTIONS.update({
    "la_class_configs_own": "Each class on its own labels, 2020-23: the rule, the most common "
                            "configuration, the share of the class in it, and how many "
                            "configurations the class spreads over",
    "la_duct_count": "Ducting counted in units, per propulsive-unit band",
    "la_trl_representativeness": "Do the aircraft above TRL 2 stand for the corpus? One test per "
                                 "attribute: chi-square for a category, Mann-Whitney for a number",
})

TABLE_CAPTIONS.update({
    # Q4. The brief prints only the fields that separate designs (author, 2026-09-23); the
    # rows dropped are named in the caption, and the full table stands in the full document.
    "a2_d3_selected_fields": "The label fields that separate one design from another: per "
                             "field, how many of the unique aircraft answer it, how many "
                             "distinct answers there are, the share of the most common one and "
                             "the four most common answers. Fields with one answer for nearly "
                             "every aircraft are left out as uninformative",
    # Q3's premise. The archetype-levels caption is rewritten only because this document prints
    # the table without its "used in this document" column: the full document's caption ends on
    # "and where this document reads the level", which would describe a column that is not here.
    "la_archetype_levels": "Every archetype level the codebook can form: the dimensions it "
                           "combines, its largest archetype, how many archetypes the level "
                           "yields, how many aircraft end up alone in one, the effective number "
                           "of archetypes (Hill ¹D) and the share held by the largest",
    "la_dd_result": "The dominant-design verdict, one line per condition",
    "la_ari_gap": "The aircraft of the 18 firms the AAM Reality Index has scored against the rest of "
                  "the corpus (both counts on the Unit line): the differences that survive correction for "
                  "multiple testing, ordered by p. `holds?` is `yes` only where the difference "
                  "also survives being re-run on the US-published patents alone",
    "la_public_pairwise": "Three sources of a class compared two at a time on the 98 aircraft with a "
                          "public counterpart: the drawing label, the patent text, the public aircraft",
    "la_ari_representativeness": "Do the index-firm aircraft stand for the corpus? One test per "
                                 "attribute",
    "la_era_frame": "The evolutionary eras and their measures (methodology framework), with what "
                    "this corpus shows on each",
    "la_top_archetypes": "The three largest archetypes of each window and what they hold "
                         "together, at all three levels: the class alone (A0), the design species "
                         "(A1t — class, wings, whether anything tilts) and the class with its "
                         "propulsive-unit band (A0c)",
    "la_class_region_timing": "Median priority year of each class inside each applicant region, "
                              "with the aircraft each cell rests on; a cell under five aircraft "
                              "is left unread",
    "la_class_filer_weight": "How much of each class is one filer repeating itself: the share "
                             "held by the largest filer, and the number of equally sized filers "
                             "that would give the same concentration",
    "la_ari_timeline": "The index firms that file in this corpus: first patent here, first "
                       "flight and planned entry into service as the AAM Reality Index reports "
                       "them, and the years between",
    # the drivers section: the full caption spells out the test; here the object is named and the
    # test is in the unit-base-transform line of the full document
    "la_driver_verdicts": "The verdict table: one row per trace of the drivers table — what moved "
                          "(first reportable window → 2020-23, per class where it differs, with "
                          "Spearman ρ and p), and the verdict with the drivers that predict it",
    "la_driver_questions": "Three questions put to the traces, each answered in one sentence",
    # the new questions: the ducting bands, printed under the question they raise
    "la_duct_units": "A ducted unit against the number of propulsive units: the aircraft in "
                     "each band, how many carry at least one ducted unit, and the share. Only "
                     "the bands are printed here; the same table holds the per-class rows the "
                     "question's own paragraph reads as the control, in `tables/la_duct_units.csv`",
})

#: rows to print. The full table is always in ``tables/<name>.csv`` and the renderer says so
#: whenever it cuts one.
ROW_CAP: Dict[str, int] = {
    "a2_d3_selected_fields": 8,
    "la_dd_result": 4,
    "la_filer_mix": 4,
    "la_filers_by_window": 5,
    "la_class_region_timing": 7,
    "la_class_filer_weight": 12,
    "a2_d16_public_match": 5,
    "a2_d15_trl_by_class": 14,
    "la_ari_gap": 8,
    "la_ari_timeline": 13,
    "la_driver_verdicts": 30,       # printed whole: every labelled trace and every unlabelled one
    "la_duct_units": 6,             # the five bands and the corpus line
    "la_class_configs_own": 5,
    "la_trl_representativeness": 6,
    "la_ari_representativeness": 6,
    "la_public_pairwise": 3,
    "la_era_frame": 4,
    "la_duct_count": 6,
    "la_archetype_levels": 3,
}

#: rows to leave out, per table, as a predicate over the built frame — applied by the render
#: script to the copy of the tables it hands the writer, NEVER to the tables the numbers are
#: read from, so no placeholder changes value. One entry (author, 2026-09-23): the
#: most-common-answers table drops every field whose top answer holds ``D3_DROP_SHARE`` or
#: more of its answered aircraft — wing configuration and lateral symmetry at this render —
#: because a row that says "almost all" separates no design from another.
D3_DROP_SHARE = 0.88


#: the column of the verdict table that says where to open the full document for that trace.
#: The built table carries a ``where drawn`` column with a TYPED number in it; the numbers of
#: the full document changed twice on 2026-09-23, so nothing typed is printed — the string is
#: used only to say WHICH item the trace is drawn in, and the number itself is read from
#: :data:`FULL_REF`, which ``set_full_reference`` fills from ``la_index`` at render time. A
#: trace drawn nowhere (the unlabelled ones, and those the frame reads in tables only) gets an
#: empty cell rather than an invented reference.
_DRAWN_IN = {"Figure 1.4.1": "trace_drift", "Figure 1.1.5": "dimension_drift"}


def _driver_pointer(row) -> str:
    refs = []
    drawn = _DRAWN_IN.get(str(row.get("where drawn", "")).strip())
    if drawn and FULL_REF.get(drawn):
        refs.append(FULL_REF[drawn])
    # a trace only the fixed physical drivers predict is read in the coupling test, not in the
    # drift figure; the verdict itself says so, and that is what the pointer follows
    if "coupling" in str(row.get("verdict", "")):
        refs += [r for r in (FULL_REF.get("trace_couplings"),
                             FULL_REF.get("la_trace_couplings")) if r]
    return " · ".join(refs)


def _with_driver_pointer(t):
    t = t.copy()
    t["in the full document"] = [_driver_pointer(r) for _, r in t.iterrows()]
    # 2026-09-24 (C28): "is any of these important? a column of importance should be added".
    # Read off the built ``verdict class`` column through :data:`IMPORTANCE`, so the grade is a
    # restatement of the test's own verdict and not a second opinion.
    t["importance"] = [_importance(r) for _, r in t.iterrows()]
    return t


ROW_FILTER: Dict[str, object] = {
    "a2_d3_selected_fields": lambda t: t[t["top_share"].astype(float) < D3_DROP_SHARE],
    # 2026-09-24, author's review: only the three levels the document reads
    "la_archetype_levels": lambda t: t[t["level"].astype(str).isin(["A0", "A0c", "A1t"])],
    # the per-class rules and the most recent complete window; every window is in the CSV
    "la_class_configs_own": lambda t: t[t["window"].astype(str).eq("2020-23")],
    # one row per attribute — the test, not every level
    "la_trl_representativeness": lambda t: t[t["test"].astype(str).ne("")],
    "la_ari_representativeness": lambda t: t[t["test"].astype(str).ne("")],
    # 2026-09-24 (C15, "why not A0c too?"): all three levels the document reads, so the level
    # that the text quotes is the level the reader can see
    "la_top_archetypes": lambda t: t[t["level"].astype(str).isin(["A1t", "A0", "A0c"])],
    # the author reads the verdict table with the full document open beside it (2026-09-23)
    # 2026-09-24: only the traces that move are printed; the still and unlabelled ones are in the CSV
    "la_driver_verdicts": lambda t: _with_driver_pointer(
        t[t["what moved"].astype(str).str.contains(r"\brises\b|\bfalls\b", regex=True)]),
    # the new questions print the ducting bands only — the same table's class rows are the
    # control the question's own paragraph reports, and the unreported rows carry no share
    "la_duct_units": lambda t: t[(t["level"] == "propulsive units")
                                 & (t["reported"].astype(str) == "True")],
}


def filter_rows(tables: Dict) -> Dict:
    """A copy of ``tables`` with :data:`ROW_FILTER` applied — for the writer only."""
    out = dict(tables)
    for name, fn in ROW_FILTER.items():
        if name in out:
            out[name] = fn(out[name]).reset_index(drop=True)
    return out


#: columns to print, where the built table is wider than a compact page can carry. Nothing is
#: recomputed: these are the same columns, fewer of them.
COLUMNS: Dict[str, List[str]] = {
    "a2_d3_selected_fields": ["name", "answered", "answers", "top_share", "most common answers"],
    # Q3's premise. ``la_archetype_levels`` drops only the full document's last column, a
    # paragraph of cross-references to sections that are not in this document; the four screen
    # columns of ``la_archetype_choice`` are kept in full, because the screens ARE the argument
    # that the level was chosen by a rule rather than by taste. ``la_dd_conditions`` has no
    # entry: all four of its columns print, thresholds and provenance included.
    "la_archetype_levels": ["level", "dimensions combined", "largest archetype", "archetypes",
                            "singletons", "effective number ¹D", "largest share"],
    "la_archetype_choice": ["level", "resolution", "fragmentation", "population",
                            "readable shares", "verdict"],
    "la_dd_result": ["condition", "met"],
    "la_class_filer_weight": ["class", "code", "aircraft", "filers", "largest filer",
                              "its aircraft", "its share", "effective filers",
                              "repetition factor"],
    "la_ari_gap": ["variable", "test", "index firms", "rest of the corpus", "p", "q (BH)",
                   "p, US patents only", "holds?"],
    "la_ari_timeline": ["company", "first patent", "first flight (ARI)",
                        "entry into service (ARI)", "years to first flight",
                        "years to entry into service"],
    "a2_d15_trl_by_class": ["class", "unique aircraft", "TRL 2", "TRL 3-5", "TRL 6-7", "TRL 8-9",
                            "above TRL 2", "share above TRL 2"],
    "la_filers_by_window": _la.COLUMNS.get("la_filers_by_window"),
    # the drivers that predict a trace are named inside the verdict itself, so the separate
    # column and the driver-kind and where-drawn columns are left to the full document
    "la_driver_verdicts": ["trace", "importance", "what moved", "verdict"],
    "la_duct_units": ["group", "aircraft", "with a ducted unit", "share ducted"],
    # 2026-09-24
    "la_class_configs_own": ["class", "rule", "aircraft", "distinct configurations",
                             "most common configuration", "share in it"],
    "la_trl_representativeness": ["attribute", "n above TRL 2", "n rest", "largest gap", "test", "p", "verdict"],
    "la_ari_representativeness": ["attribute", "n index firms", "n rest", "largest gap", "test", "p", "verdict"],   # header renamed in print (G7)
    "la_public_pairwise": ["comparison", "agree", "of", "share", "the disagreements"],
    "la_era_frame": ["measure", "era of ferment", "dominant design emerging", "incremental change", "this corpus"],
    "la_top_archetypes": ["level", "window", "aircraft", "top 1", "top 2", "top 3", "top 3 together", "top 5 together"],
    "la_duct_count": ["propulsive units", "aircraft", "with any ducted unit", "share with any",
                      "share of units ducted", "share ducting every unit",
                      "median ducted units (ducted aircraft)"],
}
COLUMNS = {k: v for k, v in COLUMNS.items() if v}

# 2026-09-25, the print audit: the tables added by the review printed 12-13 columns and
# 16-digit p values. The brief prints the columns a reader needs; tables/ keeps everything.
COLUMNS.update({
    "la_joints_per_unit": ["class", "measure", "≤2011", "12–15", "16–19", "20–23", "rho", "p",
                           "movement"],
    "la_family_dd": ["definition", "condition", "observed", "met"],
    "la_lag_constancy": ["effect", "F (on ranks)", "p (permutation)", "p (parametric)",
                         "p (Holm, across the two regions)", "partial η²"],
    "la_tw_successions": ["class of origin", "successions", "stays in the class",
                          "largest destination", "share to it", "second destination",
                          "share to it, second"],
})


def _fmt_p_cell(x):
    """A p value as a reader wants it: below a thousandth as an inequality, else 2-3 places."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return x
    if v != v:                                            # NaN
        return ""
    if v < 0.001:
        return "< 0.001"
    return f"{v:.3f}" if v < 0.01 else f"{v:.2f}"


def _is_p_col(c: str) -> bool:
    c = str(c).strip()
    return c in ("p", "q (BH)") or c.startswith(("p (", "p,", "q ("))


def print_format(name: str, t):
    """Print-only formatting for every table of the brief (read by ``report._table_md``).

    Every p or q column is printed as a reader reads it; any other float with more than three
    decimals is rounded to three. Only rows change for one table: the post-hoc family is
    printed for its ruling definition (c) in full, and for the two sensitivity definitions by
    their verdict line alone — the three definitions give the same answer, and fifteen rows of
    the same conditions would say it three times.
    """
    t = t.copy()
    if name == "la_family_dd" and "definition" in t.columns and "condition" in t.columns:
        keep = t["definition"].astype(str).str.startswith("(c)") | \
            t["condition"].astype(str).str.strip().eq("verdict")
        t = t[keep]
    for c in t.columns:
        if _is_p_col(c):
            t[c] = t[c].map(_fmt_p_cell)
            continue
        if t[c].dtype.kind == "f":
            t[c] = t[c].map(lambda x: "" if x != x else (f"{x:.3f}".rstrip("0").rstrip(".")
                                                          if abs(x - round(x, 3)) > 1e-12 else x))
    return t


# --------------------------------------------------------------------------
# 4 — numbers this document needs that ``la_index`` does not have
# --------------------------------------------------------------------------
#: Same spec grammar as :data:`la_index.TAKEAWAY_NUMBERS` and resolved by the same
#: :func:`la_index._tk_number`, against the same built tables. Two kinds of entry live here:
#: numbers no takeaway of the full document needed, and — marked `FIXES` — numbers whose
#: ``la_index`` spec names a column the built table does not have, so that the full document
#: prints an ellipsis where a number belongs. The entries below are NOT a correction of
#: ``la_index``: that module is left exactly as it is, and the broken specs are reported to
#: the author instead of edited, because editing them would change what the full document
#: renders.
NUMBERS: Dict[str, Dict] = {
    # The two configuration numbers this document used to define for itself — the
    # ``la_index`` specs named columns ``la_tables`` does not build — were corrected in
    # ``la_index`` itself on 2026-09-23, so they are gone from here: one definition per
    # number, and the prose below uses ``{tk_slc_modal_1619}`` and ``{tk_slc_configs_2023}``.
    # ---- Q3: the archetype levels and the choice among them (the premise of the test).
    # Every one of these is read out of the two built tables the section prints, so a number in
    # the prose and the same number in the table cannot diverge. ``numbers.live`` carries most
    # of them too (``a1t_distinct`` and its siblings), and they are deliberately NOT taken from
    # there: the tables are what the reader has in front of him.
    "sm_arch_levels": dict(table="la_archetype_levels", how="rows", fmt="int"),
    "sm_arch_pass": dict(table="la_archetype_choice", how="count",
                         where=("screens passed", "4 of 4"), fmt="int"),
    "sm_a0_arch": dict(table="la_archetype_levels", where=("level", "A0"),
                       col="archetypes", fmt="int"),
    "sm_a0_eff": dict(table="la_archetype_levels", where=("level", "A0"),
                      col="effective number ¹D", fmt="1f"),
    "sm_a2c_arch": dict(table="la_archetype_levels", where=("level", "A2c"),
                        col="archetypes", fmt="int"),
    "sm_a2c_single": dict(table="la_archetype_levels", where=("level", "A2c"),
                          col="singletons", fmt="int"),
    "sm_a1t_dims": dict(table="la_archetype_levels", where=("level", "A1t"),
                        col="dimensions combined"),
    "sm_a1t_n": dict(table="la_archetype_levels", where=("level", "A1t"),
                     col="aircraft", fmt="int"),
    "sm_a1t_arch": dict(table="la_archetype_levels", where=("level", "A1t"),
                        col="archetypes", fmt="int"),
    "sm_a1t_top": dict(table="la_archetype_levels", where=("level", "A1t"),
                       col="largest archetype"),
    "sm_a1t_top_share": dict(table="la_archetype_levels", where=("level", "A1t"),
                             col="largest share", fmt="pct"),
    "sm_a0c_dims": dict(table="la_archetype_levels", where=("level", "A0c"),
                        col="dimensions combined"),
    "sm_a0c_n": dict(table="la_archetype_levels", where=("level", "A0c"),
                     col="aircraft", fmt="int"),
    "sm_a0c_single": dict(table="la_archetype_levels", where=("level", "A0c"),
                          col="singletons", fmt="int"),
    "sm_a0c_top": dict(table="la_archetype_levels", where=("level", "A0c"),
                       col="largest archetype"),
    # ---- Q8: the public match (gap G2) and the class fold
    "sm_pub_n": dict(table="a2_d16_public_match",
                     where=("patent label against the public aircraft", "Total"),
                     col="unique aircraft", fmt="int"),
    "sm_pub_same": dict(table="a2_d16_public_match",
                        where=("patent label against the public aircraft",
                               "same class as the public aircraft"),
                        col="unique aircraft", fmt="int"),
    "sm_pub_share": dict(table="a2_d16_public_match",
                         where=("patent label against the public aircraft",
                                "same class as the public aircraft"),
                         col="share", fmt="pct"),
    "sm_pub_other": dict(table="a2_d16_public_match",
                         where=("patent label against the public aircraft",
                                "the patent describes another configuration "
                                "(drawing and text agree)"),
                         col="unique aircraft", fmt="int"),
    "sm_pub_draw": dict(table="a2_d16_public_match",
                        where=("patent label against the public aircraft",
                               "drawing label differs from the patent text; "
                               "the text matches the public aircraft"),
                        col="unique aircraft", fmt="int"),
    "sm_fold_vt": dict(table="la_class_fold", how="sum",
                       where=("evtol.news class", "Vectored Thrust (VT)"),
                       col="unique aircraft", fmt="int"),
    "sm_trl_nottracked": dict(table="a2_d15_trl_status",
                              where=("programme status", "not tracked"),
                              col="unique aircraft", fmt="int"),
    "sm_trl_tw": dict(table="a2_d15_trl_by_class", where=("class", "Tilt Wing"),
                      col="share above TRL 2", fmt="pct"),
    # ---- new question 1: ducting against rotor count
    "sm_duct_13": dict(table="la_duct_units",
                       where=[("level", "propulsive units"), ("group", "1-3")],
                       col="share ducted", fmt="pct"),
    "sm_duct_78": dict(table="la_duct_units",
                       where=[("level", "propulsive units"), ("group", "7-8")],
                       col="share ducted", fmt="pct"),
    "sm_duct_9": dict(table="la_duct_units",
                      where=[("level", "propulsive units"), ("group", "9+")],
                      col="share ducted", fmt="pct"),
    "sm_duct_all": dict(table="la_duct_units",
                        where=[("level", "propulsive units"), ("group", "all bands")],
                        col="share ducted", fmt="pct"),
    # ---- new question 2: the weighting
    "sm_c3_met": dict(table="la_dd_result", where=("condition", "3 — form"), col="met"),
    # ---- new question 3: the CVT · 5-6 archetype
    "sm_cvt56_air": dict(table="la_zones", where=("archetype", "CVT · 5-6"),
                         col="aircraft", fmt="int"),
    "sm_cvt56_filers": dict(table="la_zones", where=("archetype", "CVT · 5-6"),
                            col="filers", fmt="int"),
    "sm_cvt56_fpa": dict(table="la_zones", where=("archetype", "CVT · 5-6"),
                         col="filers per aircraft", fmt="2f"),
    "sm_cvt56_win2023": dict(table="la_zones", where=("archetype", "CVT · 5-6"),
                             col="2020-23", fmt="int"),
    "sm_cvt4_fpa": dict(table="la_zones", where=("archetype", "CVT · 4"),
                        col="filers per aircraft", fmt="2f"),
    "sm_cvt_own_2023": dict(table="la_class_cycles",
                            where=("class", "Combined vectored thrust"),
                            col="2020-23", fmt="pct"),
    # ---- new question 4: Tilt Wing
    "sm_tw_n": dict(table="la_class_cycles", where=("class", "Tilt Wing"),
                    col="aircraft", fmt="int"),
    "sm_tw_1619": dict(table="la_class_cycles", where=("class", "Tilt Wing"),
                       col="2016-19", fmt="pct"),
    "sm_tw_2023": dict(table="la_class_cycles", where=("class", "Tilt Wing"),
                       col="2020-23", fmt="pct"),
    "sm_tw_ent_2023": dict(table="la_cohort_mix",
                           where=[("window", "2020-23"), ("class", "TW")],
                           col="share of entrants", fmt="pct"),
    "sm_tw_air_2023": dict(table="la_cohort_mix",
                           where=[("window", "2020-23"), ("class", "TW")],
                           col="share of aircraft", fmt="pct"),
    # ---- new question 6: citations
    "sm_cite_idx": dict(table="la_ari_gap", where=("variable", "cohort citation rank"),
                        col="index firms"),
    "sm_cite_rest": dict(table="la_ari_gap", where=("variable", "cohort citation rank"),
                         col="rest of the corpus"),
    "sm_cite_q": dict(table="la_ari_gap", where=("variable", "cohort citation rank"),
                      col="q (BH)"),
    "sm_cite_us": dict(table="la_ari_gap", where=("variable", "cohort citation rank"),
                       col="p, US patents only"),
    # ---- Q2: the base of the one window that is read
    "sm_ent_2023": dict(table="la_cohort_mix",
                        where=[("window", "2020-23"), ("class", "SLC")],
                        col="firms entering", fmt="int"),
    # ---- shares that ``numbers.live`` carries as a raw fraction (0.28), read here as 28 %
    "sm_top_class_share": dict(table="la_class_filer_weight", how="max",
                               col="share by aircraft", fmt="pct"),
    "sm_trl_share": dict(table="a2_d15_trl_by_class", where=("class", "Total"),
                         col="share above TRL 2", fmt="pct"),
    "sm_duct_9_n": dict(table="la_duct_units",
                        where=[("level", "propulsive units"), ("group", "9+")],
                        col="with a ducted unit", fmt="int"),
    # ---- the bases the six panels rest on, for the grey line under each of them
    "sm_duct_total": dict(table="la_duct_units",
                          where=[("level", "propulsive units"), ("group", "all bands")],
                          col="aircraft", fmt="int"),
    "sm_tw_ent_n_2023": dict(table="la_cohort_mix",
                             where=[("window", "2020-23"), ("class", "TW")],
                             col="entering with this class", fmt="int"),
    "sm_tw_ent_base_2023": dict(table="la_cohort_mix",
                                where=[("window", "2020-23"), ("class", "TW")],
                                col="firms entering", fmt="int"),
    "sm_tw_air_n_2023": dict(table="la_cohort_mix",
                             where=[("window", "2020-23"), ("class", "TW")],
                             col="aircraft of this class", fmt="int"),
    "sm_tw_air_base_2023": dict(table="la_cohort_mix",
                                where=[("window", "2020-23"), ("class", "TW")],
                                col="aircraft in the window", fmt="int"),
    # ---- 2026-09-24, the brief's review
    "sm_pat_2018": dict(_la.TAKEAWAY_NUMBERS["tk_y2018"], col="patents acquired", fmt="int"),
    "sm_top2": dict(table="la_dominant_design", how="max", col="top-2 share", fmt="pct"),
    "sm_top2_level": dict(table="la_dominant_design", how="max", col="top-2 share", out="level"),
    "sm_top2_window": dict(table="la_dominant_design", how="max", col="top-2 share", out="window"),
    "sm_duct9_units": dict(table="la_duct_count", where=("propulsive units", "9+"),
                           col="share of units ducted", fmt="pct"),
    "sm_duct9_med": dict(table="la_duct_count", where=("propulsive units", "9+"),
                         col="median ducted units (ducted aircraft)", fmt="1f"),
    "sm_dr_cvt_duct_first": dict(table="la_trace_trends", where=[("trace", "a ducted unit"), ("code", "CVT")],
                                 col="first value", fmt="pct"),
    "sm_dr_cvt_duct_last": dict(table="la_trace_trends", where=[("trace", "a ducted unit"), ("code", "CVT")],
                                col="2020-23 value", fmt="pct"),
    "sm_dr_tr_types_first": dict(table="la_trace_trends", where=[("trace", "propulsor types"), ("code", "TR")],
                                 col="first value", fmt="int"),
    "sm_dr_tr_types_last": dict(table="la_trace_trends", where=[("trace", "propulsor types"), ("code", "TR")],
                                col="2020-23 value", fmt="int"),
    # the drift figure, one number per panel
    "sm_dd_slc_duct_w1": dict(table="la_dimension_drift", where=[("code", "SLC"), ("window", "<= 2011")],
                              col="share with a ducted unit", fmt="pct"),
    "sm_dd_slc_duct_w4": dict(table="la_dimension_drift", where=[("code", "SLC"), ("window", "2020-23")],
                              col="share with a ducted unit", fmt="pct"),
    "sm_dd_cvt_duct_w1": dict(table="la_dimension_drift", where=[("code", "CVT"), ("window", "<= 2011")],
                              col="share with a ducted unit", fmt="pct"),
    "sm_dd_cvt_duct_w4": dict(table="la_dimension_drift", where=[("code", "CVT"), ("window", "2020-23")],
                              col="share with a ducted unit", fmt="pct"),
    "sm_dd_slc_tail_w4": dict(table="la_dimension_drift", where=[("code", "SLC"), ("window", "2020-23")],
                              col="share with no tail surface", fmt="pct"),
    "sm_dd_tr_tail_w4": dict(table="la_dimension_drift", where=[("code", "TR"), ("window", "2020-23")],
                             col="share with no tail surface", fmt="pct"),
    "sm_dd_slc_boom_w4": dict(table="la_dimension_drift", where=[("code", "SLC"), ("window", "2020-23")],
                              col="share with booms", fmt="pct"),
    "sm_dd_slc_el_w4": dict(table="la_dimension_drift", where=[("code", "SLC"), ("window", "2020-23")],
                            col="share electric only", fmt="pct"),
    "sm_dd_tr_el_w4": dict(table="la_dimension_drift", where=[("code", "TR"), ("window", "2020-23")],
                           col="share electric only", fmt="pct"),
    "sm_top3_a1t_w1": dict(table="la_top_archetypes", where=[("level", "A1t"), ("window", "<= 2011")],
                           col="top 3 together", fmt="pct"),
    "sm_top3_a1t_w3": dict(table="la_top_archetypes", where=[("level", "A1t"), ("window", "2016-19")],
                           col="top 3 together", fmt="pct"),
    "sm_top3_a1t_w4": dict(table="la_top_archetypes", where=[("level", "A1t"), ("window", "2020-23")],
                           col="top 3 together", fmt="pct"),
    "sm_top1_a1t_w4": dict(table="la_top_archetypes", where=[("level", "A1t"), ("window", "2020-23")],
                           col="top 1"),
    "sm_top3_a0_w4": dict(table="la_top_archetypes", where=[("level", "A0"), ("window", "2020-23")],
                          col="top 3 together", fmt="pct"),
    "sm_top3_a0c_w4": dict(table="la_top_archetypes", where=[("level", "A0c"), ("window", "2020-23")],
                           col="top 3 together", fmt="pct"),
    "sm_ari_repr_fail": dict(table="la_ari_representativeness", how="count",
                             where=("verdict", "does NOT match the rest"), fmt="int"),
    "sm_pw_n": dict(table="la_public_pairwise", where=("comparison", "drawing label against the public aircraft"),
                    col="of", fmt="int"),
    "sm_pw_img_pub": dict(table="la_public_pairwise", where=("comparison", "drawing label against the public aircraft"),
                          col="agree", fmt="int"),
    "sm_pw_txt_pub": dict(table="la_public_pairwise", where=("comparison", "patent text against the public aircraft"),
                          col="agree", fmt="int"),
    "sm_pw_img_txt": dict(table="la_public_pairwise", where=("comparison", "drawing label against the patent text"),
                          col="agree", fmt="int"),
    "sm_pw_gt_n": dict(table="la_public_pairwise", where=("comparison", "drawing label against the patent text"),
                       col="of", fmt="int"),
    "sm_own_slc_configs": dict(table="la_class_configs_own", where=[("code", "SLC"), ("window", "2020-23")],
                               col="distinct configurations", fmt="int"),
    "sm_trl_repr_fail": dict(table="la_trl_representativeness", how="count",
                             where=("verdict", "does NOT match the rest"), fmt="int"),
    "sm_trl_repr_n": dict(table="la_trl_representativeness", how="count",
                          where=("test", "chi-square"), fmt="int"),
    # ---- 2026-09-25, the docx review
    # the two ends of the class crossover, so the thin early window can be named (C7)
    "sm_w1_n": dict(table="la_top_archetypes", where=[("level", "A0"), ("window", "<= 2011")],
                    col="aircraft", fmt="int"),
    "sm_w4_n": dict(table="la_top_archetypes", where=[("level", "A0"), ("window", "2020-23")],
                    col="aircraft", fmt="int"),
    # the verdict of each of the four moving traces, so no observation asserts a direction the
    # verdict table does not print (the tilting-joint verdict is being recomputed per unit)
    "sm_v_joints": dict(table="la_driver_verdicts",
                        where=("trace", "tilting joint groups (median)"), col="verdict class"),
    "sm_v_joints_full": dict(table="la_driver_verdicts",
                             where=("trace", "tilting joint groups (median)"), col="verdict"),
    "sm_v_units": dict(table="la_driver_verdicts",
                       where=("trace", "propulsive units (median)"), col="verdict class"),
    "sm_v_duct": dict(table="la_driver_verdicts",
                      where=("trace", "a ducted unit"), col="verdict class"),
    "sm_v_types": dict(table="la_driver_verdicts",
                       where=("trace", "propulsor types (median)"), col="verdict class"),
    "sm_v_types_full": dict(table="la_driver_verdicts",
                            where=("trace", "propulsor types (median)"), col="verdict"),
    # the most common configuration of each class, named on the page (C16)
    "sm_modal_slc": dict(table="la_class_configs_own",
                         where=[("code", "SLC"), ("window", "2020-23")],
                         col="most common configuration"),
    "sm_modal_slc_share": dict(table="la_class_configs_own",
                               where=[("code", "SLC"), ("window", "2020-23")],
                               col="share in it", fmt="pct"),
    "sm_modal_tr": dict(table="la_class_configs_own",
                        where=[("code", "TR"), ("window", "2020-23")],
                        col="most common configuration"),
    "sm_modal_cvt": dict(table="la_class_configs_own",
                         where=[("code", "CVT"), ("window", "2020-23")],
                         col="most common configuration"),
    # what the three markers of the zones panel hold (C21)
    "sm_zones_new": dict(table="la_zones", how="count", where=("zone", "new"), fmt="int"),
    "sm_zones_fading": dict(table="la_zones", how="count", where=("zone", "fading"), fmt="int"),
    "sm_zones_persist": dict(table="la_zones", how="count", where=("zone", "persistent"),
                             fmt="int"),
    "sm_zones_n": dict(table="la_zones", how="rows", fmt="int"),
    "sm_zones_top": dict(table="la_zones", how="max", col="aircraft", out="archetype"),
    "sm_zones_top_air": dict(table="la_zones", how="max", col="aircraft", fmt="int"),
    "sm_zones_top_filers": dict(table="la_zones", how="max", col="aircraft", out="filers",
                                fmt="int"),
    # all-or-nothing ducting (C24)
    "sm_duct9_every": dict(table="la_duct_count", where=("propulsive units", "9+"),
                           col="share ducting every unit", fmt="pct"),
    "sm_duct13_every": dict(table="la_duct_count", where=("propulsive units", "1-3"),
                            col="share ducting every unit", fmt="pct"),
}

#: The items printed here that ``la_index.GRADE`` does not grade **core**, each with the
#: reason it is printed anyway. The render script refuses any item outside this list that is
#: not core, so the selection rule cannot quietly slip. None of them is graded *weak*: the
#: three added on 2026-09-23 are graded **supporting**, which that register defines as
#: "apparatus the answer needs but is not — a premise, a caveat, or a description of the data
#: set". Q3's answer is negative, and a negative answer is unreadable without its premise.
NOT_CORE: Dict[str, str] = {
    "codebook_classes": "it is the vocabulary every finding is stated in, and a reader without "
                        "the twelve classes cannot read any other page",
    "la_archetype_levels": "the whole of Q3 is a statement about archetypes, and a reader who "
                           "has not seen what an archetype is, or how much the level changes "
                           "the count, cannot judge the answer",
    "la_archetype_choice": "it is the evidence that the level the test is run at was chosen by "
                           "four stated screens and a recorded ruling, and not by which level "
                           "gave the better answer",
    "la_dd_conditions": "the three thresholds were fixed before the curves were drawn, and that "
                        "is the only thing that makes a negative result a finding rather than a "
                        "description",
    "a2_d15_trl_by_class": "gap G1 of the question map, and the strongest evidence Q8 has",
    "a2_d16_public_match": "gap G2 of the question map, and the headline agreement number of "
                           "the whole labelling effort",
    "la_duct_units": "it is the measure the first of the new questions is about, and the "
                     "question cannot be read without the five bands in front of it",
    # the six panels of the new questions. They carry no grade because the question map grades
    # the ITEMS of the eight answered questions, and these are not evidence for an answer —
    # each is the measure a question is about, printed so the question can be read without
    # turning back twenty pages to the figure it was cut from.
    **{name: "a panel of the new questions: it is the measure the question names, cut to that "
             "measure alone from a table the full render already wrote"
       for name in ("sm_duct_bands", "sm_weighting", "sm_archetype_filers", "sm_tw_entry",
                    "sm_trl_tracked", "sm_cite_rank")},
    # 2026-09-24, the brief's review
    "sm_duct_count": "the ducted-unit count the author asked for; not in the full document yet",
    "sm_driver_traces": "the four moving traces of Table 12 redrawn alone, so the observations can be read on the page (2026-09-24)",
    "sm_driver_corr": "the correlation behind each observation, asked for on 2026-09-24; not in the full document",
    "sm_entry_all": "the Tilt Wing entrants panel generalised to every large class, on his ruling",
    "sm_class_configs": "within-class convergence on each class's own labels, on his ruling of 2026-09-24",
    "la_class_configs_own": "the rules of the figure above, printed so they can be attacked",
    "la_duct_count": "the ducted-unit count behind its panel",
    "la_trl_representativeness": "whether the 64 aircraft above TRL 2 stand for the corpus — asked for",
    "la_ari_representativeness": "whether the 150 index-firm aircraft stand for the corpus — asked for",
    "la_public_pairwise": "the three-source comparison the author asked for, replacing the match table",
    "la_era_frame": "the author's own era frame with this corpus read into it — asked for",
    "la_top_archetypes": "what holds the corpus once no single design does — asked for 2026-09-24",
}


def _window_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    """The study window, read from ``tables/a2_d9_windows.csv`` at render time (author's
    question, 2026-09-23): the first and last window labels, and how many of the unique
    aircraft the two complete recent windows (2016-19 and 2020-23) hold between them."""
    frame = (tables or {}).get("a2_d9_windows")
    if frame is None or "window" not in frame.columns or "unique aircraft" not in frame.columns:
        return {}
    win = [str(w).strip() for w in frame["window"]]
    cnt = [int(float(c)) for c in frame["unique aircraft"]]
    out = {"sm_win_first": win[0].replace("<=", "≤"), "sm_win_last": win[-1]}
    active = sum(c for w, c in zip(win, cnt) if w in ("2016-19", "2020-23"))
    total = values.get("unique") or sum(cnt)
    if active and total:
        out["sm_win_active_n"] = _la._tk_fmt(active, "int")
        out["sm_win_active_share"] = _la._tk_fmt(active / float(total), "pct")
    return out


def _d3_numbers(tables: Optional[Dict]) -> Dict:
    """What :data:`ROW_FILTER` leaves out of the most-common-answers table, for its caption:
    the names of the dropped fields and the cut, both read at render time."""
    frame = (tables or {}).get("a2_d3_selected_fields")
    if frame is None or "top_share" not in frame.columns:
        return {}
    gone = frame[frame["top_share"].astype(float) >= D3_DROP_SHARE]
    names = [str(n) for n in gone.get("name", [])]
    return {"sm_d3_dropped": ", ".join(names) if names else "none at this render",
            "sm_d3_drop_share": _la._tk_fmt(D3_DROP_SHARE, "pct")}


def _panel_numbers(tables: Optional[Dict]) -> Dict:
    """The four numbers the new-question panels put on the page that no single cell of a built
    table holds — each one a difference between two cells of the same row, computed here rather
    than typed, so it cannot drift from the panel drawn beside it.

    ``sm_c3_gap_main`` / ``sm_c3_gap_alt``: how far 2020-23's ΔQ falls below, or stops above,
    the lower edge of its OWN permutation band, under each of the two weightings. That distance
    is the whole of the second question and it is what the panel draws.
    ``sm_trl_tracked_n`` / ``sm_trl_tracked_share``: the aircraft a public source follows at
    all, and the share of THOSE above TRL 2 — the denominator the fifth question asks for.
    """
    from . import sm_figures as _sf          # lazy: keeps matplotlib out of a plain import
    out: Dict = {}
    q = (tables or {}).get("la_dd_q")
    if q is not None and {"level", "weighting", "window"} <= set(q.columns):
        import pandas as _pd
        for key, wt in (("sm_c3_gap_main", _la_q_weighting(0)), ("sm_c3_gap_alt", _la_q_weighting(1))):
            row = q[q["level"].eq("A0c") & q["weighting"].eq(wt) & q["window"].eq("2020-23")]
            if len(row):
                dq = float(_pd.to_numeric(row["ΔQ"], errors="coerce").iloc[0])
                lo = float(_pd.to_numeric(row["ΔQ permutation low"], errors="coerce").iloc[0])
                out[key] = f"{abs(dq - lo):.4f}"
    z = (tables or {}).get("la_zones")
    if z is not None and "aircraft" in z.columns:
        import pandas as _pd
        big = _pd.to_numeric(z["aircraft"], errors="coerce").ge(_sf.ZONE_MIN).sum()
        out["sm_zones_big_n"] = _la._tk_fmt(int(big), "int")
        out["sm_zones_min"] = _la._tk_fmt(_sf.ZONE_MIN, "int")
    co = (tables or {}).get("la_cohorts")
    if co is not None and "TW" in co.columns:
        import pandas as _pd
        thin = _pd.to_numeric(co["TW"], errors="coerce").lt(_sf.THIN_FIRMS).sum()
        out["sm_tw_thin_n"] = _la._tk_fmt(int(thin), "int")
        out["sm_tw_thin_cut"] = _la._tk_fmt(_sf.THIN_FIRMS, "int")
    st = (tables or {}).get("a2_d15_trl_status")
    if st is not None and "programme status" in st.columns:
        import pandas as _pd
        col = lambda r, c: float(_pd.to_numeric(
            st.loc[st["programme status"].eq(r), c], errors="coerce").iloc[0])
        try:
            tracked = col("Total", "unique aircraft") - col("not tracked", "unique aircraft")
            above = col("Total", "unique aircraft") - col("Total", "TRL 2")
            out["sm_trl_tracked_n"] = _la._tk_fmt(tracked, "int")
            out["sm_trl_tracked_share"] = _la._tk_fmt(above / tracked, "pct") if tracked else ""
        except (IndexError, KeyError, ValueError):
            pass
    return out


#: verdict class (the built column of ``la_driver_verdicts``) -> how much of this chapter's
#: argument the trace carries. Author's ruling of 2026-09-24: "I am bolding what is important
#: and I expect that to continue and to be a rule." **central** = one of the four observations
#: the chapter is built on; **supporting** = a clean reading that the four already fold in;
#: **null** = the trace separates nothing, which is stated as a finding and not hidden.
IMPORTANCE = {
    "opposed drivers": "**central**",
    "overdetermined": "**central**",
    "moved against every driver that predicts a direction": "**central**",
    "single driver": "supporting",
    "moves, but only fixed physical drivers predict this trace": "supporting",
    "mixed by class": "null",
    "trace does not move": "null",
    "not labelled": "null",
}


def _importance(row) -> str:
    return IMPORTANCE.get(str(row.get("verdict class", "")).strip(), "supporting")


def _importance_numbers(tables: Optional[Dict]) -> Dict:
    """How many of the PRINTED verdict rows are central, supporting and null — so the table's
    takeaway can state the split without a typed number. The rows counted are the rows
    :data:`ROW_FILTER` keeps, which is what the reader has in front of him."""
    frame = (tables or {}).get("la_driver_verdicts")
    if frame is None or "verdict class" not in frame.columns:
        return {}
    try:
        kept = ROW_FILTER["la_driver_verdicts"](frame)
    except Exception:
        return {}
    marks = [_importance(r).strip("*") for _, r in kept.iterrows()]
    return {"sm_imp_central": _la._tk_fmt(marks.count("central"), "int"),
            "sm_imp_support": _la._tk_fmt(marks.count("supporting"), "int"),
            "sm_imp_null": _la._tk_fmt(marks.count("null"), "int"),
            "sm_imp_rows": _la._tk_fmt(len(marks), "int")}


#: the trace readings the four driver observations quote, as (key, trace, class code, which pair
#: of columns, format). Every number in those four paragraphs comes from here rather than from
#: the keyboard, so a recomputation of the traces rewrites the prose.
_TRACE_POINTS = [
    ("joints_tr", "tilting joint groups", "TR", "mean", "1f"),
    ("joints_cvt", "tilting joint groups", "CVT", "mean", "1f"),
    ("joints_all", "tilting joint groups", "ALL5", "mean", "1f"),
    ("units_tr", "propulsive units", "TR", "value", "1f"),
    ("units_cvt", "propulsive units", "CVT", "value", "1f"),
    ("units_slc", "propulsive units", "SLC", "value", "1f"),
    ("duct_cvt", "a ducted unit", "CVT", "value", "pct"),
    ("types_tr", "propulsor types", "TR", "mean", "1f"),
    ("types_all", "propulsor types", "ALL5", "mean", "1f"),
    # 2026-09-26: the rewritten statistics box (sm_text_methods.STATS_BOX)
    ("units_mr", "propulsive units", "MR", "value", "1f"),
    ("joints_cvt_med", "tilting joint groups", "CVT", "value", "1f"),
]


def _driver_numbers(tables: Optional[Dict]) -> Dict:
    """The four observations' own numbers, out of ``la_trace_trends``.

    ``la_index._tk_number`` has no format for a p-value — 0.0093 would print as 0.01 and
    4.6e-07 as 0.00 — so the three fields a driver sentence needs (the two ends, Spearman rho
    and p) are formatted here: rho always signed, p as "< 0.001" or to three decimals, and the
    movement word ("rises", "falls", "flat") so that no sentence asserts a direction the table
    does not.
    """
    frame = (tables or {}).get("la_trace_trends")
    if frame is None or "trace" not in frame.columns:
        return {}
    import pandas as _pd
    out: Dict = {}
    for key, trace, code, which, fmt in _TRACE_POINTS:
        sel = frame[frame["trace"].astype(str).str.strip().eq(trace)
                    & frame["code"].astype(str).str.strip().eq(code)]
        if not len(sel):
            continue
        r = sel.iloc[0]
        c1, c2 = (("first mean", "2020-23 mean") if which == "mean"
                  else ("first value", "2020-23 value"))
        for slot, col in (("first", c1), ("last", c2)):
            got = _la._tk_fmt(r.get(col), fmt)
            if got is not None:
                out[f"sm_t_{key}_{slot}"] = got
        rho = _la._tk_float(r.get("rho"))
        if rho is not None:
            out[f"sm_t_{key}_rho"] = f"{rho:+.2f}"
        pv = _la._tk_float(r.get("p"))
        if pv is not None:
            out[f"sm_t_{key}_p"] = "< 0.001" if pv < 0.001 else f"{pv:.3f}"
        mv = str(r.get("movement", "")).strip()
        if mv:
            out[f"sm_t_{key}_move"] = mv
    return out


def _duct_conditional_numbers(tables: Optional[Dict]) -> Dict:
    """Ducting read CONDITIONALLY on ducting at all (author, C24: "if one is ducted, are they
    all ducted?"). Both numbers are ratios of two cells of the ``all bands`` row of
    ``la_duct_count`` — computed here rather than typed, exactly as :func:`_panel_numbers`
    computes the two band gaps, so they cannot drift from the table printed beside them."""
    frame = (tables or {}).get("la_duct_count")
    if frame is None or "propulsive units" not in frame.columns:
        return {}
    try:
        row = frame[frame["propulsive units"].astype(str).str.strip().eq("all bands")].iloc[0]
        every = _la._tk_float(row.get("share ducting every unit"))
        anyd = _la._tk_float(row.get("share with any"))
    except (IndexError, KeyError, ValueError):
        return {}
    if not every or not anyd:
        return {}
    return {"sm_ductc_all": _la._tk_fmt(every / anyd, "pct")}


def _method_numbers() -> Dict:
    """The three apparatus constants the methods box states, read from the code that runs.

    ``perms`` and ``seed`` are the defaults of :func:`la_tables.dominant_design` (the same two
    the Q test uses) and ``n`` the rarefaction size of :func:`la_tables.hill_numbers`. Reading
    them from the signatures rather than typing them is the same rule the numbers obey: a
    changed default rewrites the box instead of silently disagreeing with it.
    """
    import inspect
    try:
        from . import la_tables as _ltb
        dd = inspect.signature(_ltb.dominant_design).parameters
        hn = inspect.signature(_ltb.hill_numbers).parameters
        return {"sm_perms": str(dd["perms"].default),
                "sm_perm_seed": str(dd["seed"].default),
                "sm_perm_n": str(hn["n"].default)}
    except Exception:
        return {}


def _la_q_weighting(k: int) -> str:
    """The k-th of the two weightings the dominant-design test is run under, named where the
    test names them (``la_tables.Q_WEIGHTINGS``) rather than spelled out here."""
    from . import la_tables as _ltb
    return _ltb.Q_WEIGHTINGS[k]


# ---------------------------------------------------------------------------
# 2026-09-25 — the numbers of the review rebuild. Five groups, all read out of tables
# built on the same run, so a number in the stated prose and the same number in the table
# it sits under cannot diverge. Written by the coordinator after the four review agents
# landed; the prose that asks for them was written first, against these names.
# ---------------------------------------------------------------------------
NUMBERS.update({
    # ---- 1.1 doubling time (sm_open.la_doubling_time / la_doubling_ratio). The baseline is
    # CPC B64 WORLDWIDE simple families (PatSeer) since 2026-09-25 — the nine-office series is
    # now the comparison row; the label travels in the table's
    # own ``series`` cell and the prose states it.
    "sm_dbl_evtol": dict(table="la_doubling_time", fmt="1f", col="doubling time (years)",
                         where=[("series", "eVTOL aircraft (this corpus)"), ("primary", "True")]),
    "sm_dbl_evtol_ci": dict(table="la_doubling_time", col="95 % interval",
                            where=[("series", "eVTOL aircraft (this corpus)"), ("primary", "True")]),
    "sm_dbl_b64": dict(table="la_doubling_time", fmt="1f", col="doubling time (years)",
                       where=[("series", "aeronautics — CPC B64, worldwide simple families (PatSeer)"),
                              ("primary", "True")]),
    "sm_dbl_b64_ci": dict(table="la_doubling_time", col="95 % interval",
                          where=[("series", "aeronautics — CPC B64, worldwide simple families (PatSeer)"),
                                 ("primary", "True")]),
    "sm_dbl_b64_offices": dict(table="la_doubling_time", fmt="1f", col="doubling time (years)",
                               where=[("series", "aeronautics — CPC B64, nine corpus offices "
                                                 "(PATENTSCOPE publications)"),
                                      ("primary", "True")]),
    "sm_dbl_ratio": dict(table="la_doubling_ratio", fmt="2f", col="times faster",
                         where=[("corpus series", "eVTOL aircraft (this corpus)"),
                                ("primary", "True")]),
    "sm_dbl_ratio_ci": dict(table="la_doubling_ratio", col="times faster interval",
                            where=[("corpus series", "eVTOL aircraft (this corpus)"),
                                   ("primary", "True")]),
    "sm_dbl_ratio_sens": dict(table="la_doubling_ratio", fmt="2f", col="times faster",
                              where=[("corpus series", "eVTOL aircraft (this corpus)"),
                                     ("window", "2005–2019")]),

    # ---- 2.2 the discovery curve (sm_open.la_discovery_estimators). The level-dependent
    # answer: closed at the coarse levels, still opening at the design species.
    "sm_disc_a0c_unseen": dict(table="la_discovery_estimators", where=("level", "A0c"),
                               col="estimated unseen", fmt="1f"),
    "sm_disc_a1t_obs": dict(table="la_discovery_estimators", where=("level", "A1t"),
                            col="archetypes observed", fmt="int"),
    "sm_disc_a1t_est": dict(table="la_discovery_estimators", where=("level", "A1t"),
                            col="Chao1", fmt="1f"),
    "sm_disc_a1t_new100": dict(table="la_discovery_estimators", where=("level", "A1t"),
                               col="new in the last 100 aircraft", fmt="1f"),
    "sm_disc_a1t_exp100": dict(table="la_discovery_estimators", where=("level", "A1t"),
                               col="new in the last 100, random order", fmt="1f"),

    # ---- 4.2 is the regional lag a constant (sm_open.la_lag_constancy). The lead is solid,
    # the constancy of the offset is not established — the prose must not claim it.
    "sm_lag_p_region": dict(table="la_lag_constancy", col="p (parametric)", fmt="p",
                            where=("effect", "region (the lead itself)")),
    "sm_lag_p_inter": dict(table="la_lag_constancy", col="p (permutation)", fmt="3f",
                           where=("effect", "class × region (the lag is not a constant)")),

    # ---- driver observation 1: the tilting-joint rise does not survive normalisation
    # (la_tables.la_joints_per_unit). This is the correction the 2026-09-24 review produced.
    "sm_jpu_tr_rho": dict(table="la_joints_per_unit", col="rho", fmt="2f",
                          where=[("measure", "tilting joint groups per propulsive unit"),
                                 ("code", "TR")]),
    "sm_jpu_tr_p": dict(table="la_joints_per_unit", col="p", fmt="p",
                        where=[("measure", "tilting joint groups per propulsive unit"),
                               ("code", "TR")]),
    "sm_jpu_cvt_rho": dict(table="la_joints_per_unit", col="rho", fmt="2f",
                           where=[("measure", "tilting joint groups per propulsive unit"),
                                  ("code", "CVT")]),
    "sm_jpu_cvt_p": dict(table="la_joints_per_unit", col="p", fmt="2f",
                         where=[("measure", "tilting joint groups per propulsive unit"),
                                ("code", "CVT")]),

    # ---- the post-hoc Lift + Cruise + CVT family (la_tables.la_family_share / la_family_dd).
    # Definition (c) is the ruling one; (b) is the sensitivity that comes closest to the line.
    "sm_fam_c_n": dict(table="la_family_dd", where=("id", "c"), col="aircraft", fmt="int"),
    "sm_fam_c_peak": dict(table="la_family_share", where=("id", "c"), how="max",
                          col="family share", fmt="pct"),
    "sm_fam_b_peak": dict(table="la_family_share", where=("id", "b"), how="max",
                          col="family share", fmt="pct"),
    "sm_fam_windows_met": dict(table="la_family_share", how="count",
                               where=[("id", "c"), ("over the 50 % line", "True")], fmt="int"),
    # condition 3's own cell counts, read off the condition-3 row itself. Counting rows of the
    # table instead gave "0 of 5" for a 0-of-8 result, because the table has five condition rows
    # per definition and eight complete level-windows.
    "sm_fam_c3_cells": dict(table="la_family_dd", col="cells met", fmt="int",
                            where=[("id", "c"),
                                   ("condition", "3 form — Rao's Q below the family's earliest windows")]),
    "sm_fam_c3_total": dict(table="la_family_dd", col="cells total", fmt="int",
                            where=[("id", "c"),
                                   ("condition", "3 form — Rao's Q below the family's earliest windows")]),
})

#: the new items carry no grade in ``la_index.GRADE`` — they did not exist when the question
#: map was graded — so each states here why the brief prints it. ``render_summary.check_selection``
#: accepts an item that is graded ``core`` OR named in :data:`NOT_CORE`.
NOT_CORE.update({
    "la_name_coverage": "the base of the public-aircraft comparison: without it the 90 % cannot "
                        "be read (author's review, 2026-09-24)",
    "sm_family": "the post-hoc family test — the closest this corpus comes to the 50 % line",
    "la_family_dd": "the three conditions applied to the post-hoc family, and its verdict",
    "discovery_curve": "closes the question of whether the space is still opening, which the "
                       "document previously printed as OPEN",
    "sm_duct_conditional": "answers whether ducting is a property of the aircraft or of the unit",
    "sm_joints_per_unit": "the correction the review produced: the joint rise does not survive "
                          "normalisation by propulsive units",
    "la_joints_per_unit": "the fit behind that correction",
    "la_tw_successions": "where the firms that leave Tilt Wing go — the one class firms leave",
    "la_lag_constancy": "the test that replaced 'read off the table, not tested'",
})

TABLE_CAPTIONS.update({
    "la_name_coverage": "Unique aircraft by name: the ones that carry a real product name, the "
                        "ones that carry a generated one, and what a name buys — every aircraft "
                        "matched to a public product is a named one",
    "la_family_dd": "The post-hoc Lift + Cruise and CVT family against the three dominant-design "
                    "conditions, one row per condition and per definition of the family. The "
                    "grouping was defined after the result that suggested it and is not a "
                    "pre-registered test",
    "la_joints_per_unit": "Tilting joint groups per class and window, counted per aircraft and "
                          "again per propulsive unit, with the same rank correlation against the "
                          "priority year that every other trace is tested with",
    "la_tw_successions": "Where a firm's next aircraft lands, by the class it started in: the "
                         "share that stays and the classes the leavers go to",
    "la_lag_constancy": "Is the regional lead the same size in every class? The class-by-region "
                        "interaction on the priority-year ranks, against a permutation null that "
                        "holds both main effects",
})


#: the release of the AAM Reality Index the market dates come from (ari_may2026.csv)
ARI_RELEASE_YEAR = 2026


def _ari_clock_numbers(tables: Optional[Dict]) -> Dict:
    """The patent-clock-against-market-clock numbers of the chapter 1 answer, from
    ``la_ari_timeline`` (settled 2026-09-25, ``CLOSING_TAKEAWAYS_2026-09-25.md``; the author
    approved all three takeaways). Medians over a filtered column, which the ``NUMBERS`` spec
    language cannot say, hence a function. Every gap in that table is a floor — the clock
    starts at the firm's first patent IN THIS CORPUS — and the prose states it."""
    frame = (tables or {}).get("la_ari_timeline")
    if frame is None:
        return {}
    import pandas as pd    # the module deliberately imports no dataframe machinery; only this
    try:                   # function needs it, and a missing pandas must cost the numbers, not the build
        ff = pd.to_numeric(frame["years to first flight"], errors="coerce").dropna()
        eis = pd.to_numeric(frame["years to entry into service"], errors="coerce").dropna()
    except Exception:
        return {}
    if not len(ff):
        return {}
    # 2026-09-26 (chapter-1 review): a first flight the index dates after its own release is a
    # PLAN, not a flight — Ascendance's 2027 was being counted as "filed before they flew".
    # Only flights on or before the release year count; the planned ones are named apart.
    flown_year = pd.to_numeric(frame["first flight (ARI)"], errors="coerce")
    planned = int((flown_year > ARI_RELEASE_YEAR).sum())
    ff = pd.to_numeric(frame.loc[flown_year.le(ARI_RELEASE_YEAR), "years to first flight"],
                       errors="coerce").dropna()
    pos = ff[ff > 0]
    return {"sm_ff_dated": f"{len(ff):d}",
            "sm_ff_flown": f"{len(ff):d}",
            "sm_ff_planned": f"{planned:d}",
            "sm_ff_before": f"{int((ff > 0).sum()):d}",
            "sm_ff_neg": f"{int((ff <= 0).sum()):d}",
            "sm_ff_lead": f"{pos.median():.0f}" if len(pos) else "",
            "sm_ff_eis": f"{eis.median():.0f}" if len(eis) else ""}

NUMBERS.update({
    # 2026-09-25: the seven-year rule of 1.2, measured on the corpus (author-supplied check,
    # sm_open.la_lapse_check) — the lapse-cohort rule is now confirmed, not argued.
    "sm_lapse_grants": dict(table="la_lapse_check", col="value",
                            where=("measure", "dated grants in the corpus")),
    "sm_lapse_7y": dict(table="la_lapse_check", col="value",
                        where=("measure", "grants arriving within 7 years of priority")),
    "sm_lapse_median": dict(table="la_lapse_check", col="value",
                            where=("measure", "median priority-to-grant lag (years)")),
    "sm_lapse_p2019": dict(table="la_lapse_check", col="value",
                           where=("measure", "families still pending, 2019 cohort")),
    "sm_lapse_p2022": dict(table="la_lapse_check", col="value",
                           where=("measure", "families still pending, 2022 cohort")),
    "sm_lapse_p2023": dict(table="la_lapse_check", col="value",
                           where=("measure", "families still pending, 2023 cohort")),
})

NUMBERS.update({
    # 2026-09-25, the takeaways of the items the review added
    "sm_nc_named": dict(table="la_name_coverage", col="unique aircraft", fmt="int",
                        where=("aircraft", "carry a real product name")),
    "sm_nc_gen": dict(table="la_name_coverage", col="unique aircraft", fmt="int",
                      where=("aircraft", "carry a generated identifier")),
    "sm_nc_gen_matched": dict(table="la_name_coverage", col="compared with the public aircraft",
                              fmt="int", where=("aircraft", "carry a generated identifier")),
    "sm_tw_stay": dict(table="la_tw_successions", col="stays in the class", fmt="pct",
                       where=("code", "TW")),
    "sm_tw_to_tr": dict(table="la_tw_successions", col="share to it", fmt="pct",
                        where=("code", "TW")),
    "sm_tw_n": dict(table="la_tw_successions", col="successions", fmt="int", where=("code", "TW")),
    "sm_slc_stay": dict(table="la_tw_successions", col="stays in the class", fmt="pct",
                        where=("code", "SLC")),
    "sm_tr_stay": dict(table="la_tw_successions", col="stays in the class", fmt="pct",
                       where=("code", "TR")),
})

def resolve(values: Optional[Dict], tables: Optional[Dict]) -> Dict:
    """``values`` extended with every number this document's prose can ask for.

    Called by the render script BEFORE :func:`report.write_markdown`, because that function
    fills a node's prose from ``values`` alone and never sees the tables. The result is the
    same mechanism the grey lines use — :data:`la_index.TAKEAWAY_NUMBERS` and
    :data:`NUMBERS`, both read through :func:`la_index._tk_number` — so a number in the prose
    and the same number in a takeaway cannot diverge.

    A spec that cannot be resolved is simply absent, and :func:`_pa._fill` then leaves its
    ``{placeholder}`` standing. The render script fails on a standing placeholder rather than
    shipping one, which is the opposite of the grey lines' behaviour on purpose: a grey line
    degrades to an ellipsis, a stated answer must not.
    """
    out = dict(values or {})
    out.update(_window_numbers(tables, out))
    out.update(_d3_numbers(tables))
    out.update(_panel_numbers(tables))
    out.update(_duct_conditional_numbers(tables))
    out.update(_ari_clock_numbers(tables))
    out.update(_ch1_numbers(tables, out))          # 2026-09-26: needs sm_ff_lead and lag_p90
    out.update(_method_numbers())
    out.update(_driver_numbers(tables))
    out.update(_importance_numbers(tables))
    for _fn in NUMBER_FUNCS:                 # 2026-09-26: chapter modules' own numbers
        try:
            out.update(_fn(tables, out) or {})
        except Exception:
            pass
    # cross-references, never typed: ``{sm_ref_<name>}`` is the item's number in the FULL
    # document at this render (``set_full_reference`` has already run), ``{sm_here_<name>}``
    # its number in this one. The full document was renumbered twice on 2026-09-23; a typed
    # number would already be wrong.
    for name, ref in FULL_REF.items():
        out[f"sm_ref_{name}"] = ref
    for name, ref in HERE_REF.items():
        out[f"sm_here_{name}"] = ref
    _nums = [int(r.split()[1]) for r in HERE_REF.values()
             if r.startswith("Table ") and r.split()[1].isdigit()]
    out["sm_next_table"] = f"Table {max(_nums) + 1}" if _nums else "Table"
    for key, tname in _la.N_FROM_TABLE.items():
        frame = (tables or {}).get(tname)
        if frame is not None:
            out[key] = len(frame)
    for register in (_la.TAKEAWAY_NUMBERS, NUMBERS):
        for key, spec in register.items():
            got = _la._tk_number(spec, tables)
            if got is not None:
                out[key] = got
    # every item's importance grade, as ``{sm_grade_<internal name>}``, straight out of the
    # shared register — so a section that has to explain why an item is NOT printed quotes the
    # map's own reason rather than a copy of it, and a regrade rewrites this document too.
    gfn = getattr(_la, "grade", None)
    if gfn is not None:
        for name in set(_la.QUESTION) | set(_la.TAKEAWAY) | set(NOT_CORE):
            try:
                got = gfn(name, None, "figure", tables)
            except Exception:
                continue
            if got:
                out[f"sm_grade_{name}"] = got
    _VALUES.clear()
    _VALUES.update(out)
    _TABLES.clear()                        # the chapter Answers resolve their own numbers
    _TABLES.update(tables or {})
    return out


# --------------------------------------------------------------------------
# 5 — accessors (the API ``report.write_markdown`` calls)
# --------------------------------------------------------------------------
def node(node_id: str) -> Dict:
    for n in NODES:
        if n["id"] == node_id:
            return n
    raise KeyError(node_id)


def depth(node_id: str) -> int:
    """0 only for the sections that open their own page.

    ``report.write_markdown`` decides a page break with ``depth(nid) == 0 and nid in
    APPENDIX``. Returning 1 everywhere else is what makes this document flow instead of
    spending a page on every heading — which is the difference between 25 pages and 40.
    """
    return 0 if node_id in _TOP else 1


def heading(node_id: str, values: Optional[Dict] = None) -> str:
    n = node(node_id)
    if node_id in SM_QUESTIONS or node_id in _la.QUESTIONS:   # chapters 1-5 and M
        return f"## {node_id} — {_question_title(node_id)}"
    title = _pa._fill(n.get("title", node_id), values)
    if n.get("subq"):                                # a sub-question: its own heading level
        return f"### {n['subq']} — {title}"
    if "." not in node_id:
        return f"## {title}"
    if node_id.count(".") == 1 and node_id.split(".")[0] in SM_QUESTIONS:
        if node_id.split(".")[0] in METHOD_RESULTS:   # 2026-09-26 (C14): no "Observation" heading
            return "#### Results and discussion"   # 2026-09-26: the thesis merges the two
        return f"#### Observation — {title}"        # a section under a sub-question; its parts flow
    return f"#### {title}"


#: the unit of analysis of each question section, printed as the section's second line
#: (author, 2026-09-23: "state the unit in every question section"). Each entry is read from
#: the ``unit`` field of ``la_index.PROVENANCE`` for the items the section prints — the
#: shortest true statement that covers all of them — and names the second unit where a
#: section has one (patents for lapse, firms for Q5 and Q7). Q8's two tables have no
#: provenance entry; their unit is the ``unique aircraft`` column of the tables themselves.
UNIT: Dict[str, str] = {
    "Q1": "primary patents (n {primary_s}) for legal status — the {tk_lapsed_n} with a "
          "2019-or-earlier priority — and unique aircraft (n {unique_s}) for filing per year; "
          "the market clock counts the {tk_ari_timeline_n} index firms that file in the corpus",
    "Q2": "unique aircraft (n {unique_s}), as shares of each priority window; the drift figure "
          "reads one architecture class per line, in the windows where it holds 5 or more",
    "Q3": "unique aircraft (n {unique_s}) grouped into archetypes, per priority window; the "
          "screens and conditions tables have no corpus unit — one row is a level or a "
          "condition",
    "Q4": "unique aircraft (n {unique_s}); the first figure counts A0c archetypes of five or "
          "more aircraft (n {n_zones})",
    "Q5": "named firms (n {tk_firms_all}) and the unique aircraft (n {unique_s}) they hold; the "
          "filer-mix table counts the same population twice, as primary patents "
          "(n {primary_s}) and as aircraft",
    "Q6": "unique aircraft (n {unique_s}) by applicant region; panel (i) of the first figure "
          "counts patents per country (acquired {acquired_s}, representative "
          "{representative_s})",
    "Q7": "unique aircraft (n {unique_s}) attributed to filers — a named firm is one filer, a "
          "lone inventor's patent its own; the leave-one-out panel counts named firms holding "
          "three or more aircraft",
    "Q8": "unique aircraft (n {unique_s}) — all of them for technology readiness, the "
          "{sm_pub_n} with a matched public aircraft for the agreement table, and the aircraft "
          "of the index firms against everyone else's for the gap table",
    "M":  "unique aircraft (n {unique_s}) carrying both a figure label and a whole-patent "
          "class; rows of the matrix are the whole-patent class",
}


UNIT = _rekey(UNIT)
TEXTS = _rekey(TEXTS)
AFTER = _rekey(AFTER)


# ---------------------------------------------------------------------------
# 2026-09-26 — the chapter-1 review (38 comments on "Labelling Analysis in brief — 2026-09-25
# revised.docx"), written toward the thesis split into Methodology and Results. Every
# sub-question of a chapter in METHOD_RESULTS opens on a **Method** block — what is measured,
# in which figure or table, on which unit and why, from which sources, with which test — and
# its evidence follows under a **Results** heading. The Source · Unit · How-to-read lines move
# up into the Method block, so an item there keeps only its takeaway. Chapters not yet reviewed
# keep the earlier layout until their own round.
# ---------------------------------------------------------------------------
METHOD_RESULTS = {"1"}

#: the method every chapter shares, printed at the head of chapter 1 (C14, C29: the unit, the
#: time axis and the four tests are introduced before the first item that uses them)
CHAPTER_METHOD: Dict[str, str] = {
    "1": (
    "#### Method common to every chapter\n\n"
    "**Unit of analysis.** {acquired_s} patents were acquired (PatSeer, snapshot {snapshot}); "
    "{representative_s} describe an electric VTOL aircraft readable from its drawings; those "
    "describe **{unique_s} unique aircraft**. A unique aircraft is not the patent, because a "
    "firm that files the same design five times has one design, and the questions here are "
    "about designs. It is not the {observations_s} aircraft observations either, because an "
    "observation is one aircraft in one patent — drawn in one of its figures or in several — "
    "and the same aircraft recurs across filings. The unique aircraft is the unit most figures "
    "and tables count, but not all: a growth rate compared with worldwide baselines is counted "
    "in patent families, because that is the baselines' own unit, and a market-clock comparison "
    "is counted in firms, because a first flight is a firm's event, not a design's. Each Method "
    "below names the unit of analysis it uses.\n\n"
    "**Time analysis is based on the priority year:** the earliest filing date of the patent "
    "family, which is when the design existed. A patent is published a median of "
    "{lag_median_lo} to {lag_median_hi} years after its priority date, depending on the region, "
    "and {lag_p90} years after at the 90th percentile. Priority years from {partial_start} on "
    "are still filling at the snapshot, are hatched in every figure, and no trend is read past "
    "2023. How much of a recent year the snapshot already sees is read from the corpus's own "
    "publication lag: the years 2016-21, whose publications are complete, give the distribution "
    "of that lag per region, and applying it to priority year 2023 says the snapshot already "
    "sees from {sm_vis2023_lo} to {sm_vis2023_hi} of each region's 2023 aircraft, depending on "
    "the region, so the last hatched years are a large majority of what they will become, not a "
    "small fraction of it.\n\n"
    + _methods_text.STATS_BOX.strip() + "\n"),     # the box carries its own div and heading
}

# 2026-09-27 (author's review, A2): how much of priority year 2023 the snapshot already sees,
# per region, read off la_region_years ("visible at the snapshot"; sm_open.region_years) rather
# than typed. The row is filtered on the int column "priority year" == 2023.
NUMBERS.update({
    "sm_vis2023_lo": dict(table="la_region_years", where=[("priority year", 2023)],
                          how="min", col="visible at the snapshot", fmt="pct"),
    "sm_vis2023_hi": dict(table="la_region_years", where=[("priority year", 2023)],
                          how="max", col="visible at the snapshot", fmt="pct"),
})

TEXTS.update({
    "1.q1": (
    "#### Method\n\n"
    "**Objective.** The question is how fast eVTOL patenting has grown, and how early the "
    "record shows a design that later flies. An answer places eVTOL's growth against patenting "
    "at large and states, in years, how far ahead of its first flight a design becomes visible "
    "in the patent record.\n\n"
    "**Data and unit of analysis.** Two units are drawn side by side in "
    "{sm_here_filings_per_year} (i), because they answer different questions and the gap "
    "between them is itself informative: the gap is repeated filing. In 2018, {sm_pat_2018} "
    "acquired patents describe only {tk_y2018} unique aircraft, so a count of patents alone "
    "would overstate the number of designs filed that year. The unique aircraft, counted once "
    "by the priority year of its first patent (later patents on the same aircraft are not "
    "counted again), is the unit of the filings count; the acquired-patent count is drawn "
    "beside it only to show the size of that gap. For the growth-rate comparison in "
    "{sm_here_filings_per_year} (ii) the unit changes, because the three worldwide baselines "
    "are counted in patent families: eVTOL's own series is counted the same way for that "
    "comparison, as the {representative_s} patents that describe an electric VTOL aircraft, "
    "each one family, so the comparison is like for like. eVTOL's doubling time counted as "
    "unique aircraft, the unit used everywhere else in this document, is also fitted and "
    "reported alongside it. For how long before first flight, in {sm_here_ari_clock} and "
    "{sm_here_la_ari_timeline}, the unit changes again, to the firm, because a first flight is "
    "a firm's event and not a design's: it is read for the {tk_ari_timeline_n} firms the AAM "
    "Reality Index lists in May 2026 that file in this corpus. Sources: PatSeer (the corpus and "
    "the worldwide baselines), WIPO patent families by origin (all patents), the AAM Reality "
    "Index (May 2026) and human labelling.\n\n"
    "**Procedure.** {sm_here_filings_per_year} (i) plots unique aircraft per priority year, "
    "split by applicant region, with the acquired patents drawn as a line beside the bars and "
    "the dated sector events marked under them. {sm_here_filings_per_year} (ii) then asks how "
    "fast eVTOL grows against the patenting around it, against three worldwide baselines: "
    "aeronautics (CPC B64), transport and operations (CPC section B) and every patent family of "
    "any kind. {sm_here_ari_clock} reads, for each of the {tk_ari_timeline_n} index firms, the "
    "span from its first to its last patent and its peak filing year, against the first flight "
    "and planned entry into service the index reports; {sm_here_la_ari_timeline} lists these "
    "dates firm by firm. The **AAM Reality Index** (AAM = Advanced Air Mobility, the field; ARI "
    "= the index's score) is an analyst's quarterly judgement of how far each manufacturer has "
    "got, not a measurement.\n\n"
    "**Scientific grounds.** To compare how fast each series grows, the number of years each "
    "takes to double is computed. Each series is first divided by its own 2005-09 average, so "
    "all four start at the same point and can be read on the same log axis, where a steeper "
    "line is faster growth and two parallel lines grow at the same rate. On that scale the "
    "yearly count is fitted as log(count_t) = a + b·t by least squares over the priority years "
    "2005-2023, and the doubling time is ln 2 / b, with its own 95 % interval from the fit. Two "
    "series are compared as the ratio of their doubling times, read as times as fast. That "
    "ratio's own interval comes from a paired bootstrap over the years: the complete years are "
    "resampled with replacement, both series are refitted on the same drawn years, this is "
    "repeated 2 000 times, and the interval is the middle 95 % of the resulting ratios (Efron, "
    "1979). Resampling years, rather than refitting once, carries the year-to-year scatter that "
    "a single fitted line hides. An interval that takes in 1 means the two rates cannot be told "
    "apart. The fit is repeated ending at 2019, to check whether the answer rests on the most "
    "recent years alone. The lead over first flight is the number of years from a firm's first "
    "patent in this corpus to its first flight, counted only for the flights that have already "
    "happened.\n\n"
    "**Assumptions and limits.** The lead over first flight is a floor, because a firm may have "
    "filed earlier outside this corpus, and the AAM Reality Index itself is a judgement, not a "
    "measurement. The dated sector events marked on {sm_here_filings_per_year} (i) are context "
    "for reading the curve, not evidence that any one of them caused a change in filing: "
    "patenting responds to many things at once, and a coincidence in time is not a proven "
    "cause.\n"),

    "1.q2": (
    "#### Method\n\n"
    "**Objective.** The question is what share of the patented aircraft is still protected, and "
    "whether that share differs between architecture classes. An answer would show whether some "
    "classes have been let lapse more than others, or whether the record's own age already "
    "explains the difference.\n\n"
    "**Data and unit of analysis.** The unit is the unique aircraft, counted **out of force** "
    "when every patent that describes it reads INACTIVE in PatSeer's legal status at the "
    "snapshot: lapsed for non-payment, withdrawn, refused or expired. One patent that is "
    "pending or in force keeps the aircraft in force, because a design stays protected as long "
    "as any of its patents does, so the aircraft's first patent alone cannot decide it. Only "
    "aircraft with a priority year of 2019 or earlier are read, because an application takes up "
    "to about seven years from its priority date to be granted or refused: in this corpus "
    "{sm_lapse_7y} of the {sm_lapse_grants} dated grants arrive within seven years of priority, "
    "a median of {sm_lapse_median} years, and the share of families still under examination, "
    "neither granted nor refused, is {sm_lapse_p2019} for priority year 2019, {sm_lapse_p2022} "
    "for 2022 and {sm_lapse_p2023} for 2023. A younger application that reads active is mostly "
    "still under examination, and counting it would inflate the share in force. Sources: "
    "PatSeer legal status (snapshot {snapshot}), human labelling for the class.\n\n"
    "**Procedure.** {sm_here_sm_force_aircraft} reads the share out of force per architecture "
    "class, for aircraft with a priority year of 2019 or earlier.\n\n"
    "**Scientific grounds.** Whether the classes differ is asked with a chi-square test, "
    "χ² = Σ (O − E)² / E, comparing the observed count of out-of-force aircraft in each class "
    "against the count expected if every class lapsed at the same rate (statistics box). "
    "Because one duplicate patent family can name more than one aircraft, the test is run "
    "twice, once counting a duplicate for every aircraft it names and once counting it for the "
    "first aircraft only, and both p values are reported.\n\n"
    "**Assumptions and limits.** Legal status here is a single snapshot, not a lapse date, so "
    "this Method states only whether an aircraft is out of force at the export date, not when "
    "it became so.\n"),

    "1.q3": (
    "#### Method\n\n"
    "**Objective.** The question is how faithfully the patented aircraft describe the aircraft "
    "the industry actually builds, and whether the aircraft that can be checked stand for the "
    "rest of the record. An answer states how often the patent drawing's architecture class "
    "matches the built aircraft's own class, and whether the aircraft public sources cover are "
    "a fair sample of the corpus or a distinct slice of it.\n\n"
    "**Data and unit of analysis.** The unit is the unique aircraft, but only the aircraft that "
    "can be linked to a source outside the patents enter each comparison. An aircraft can be "
    "compared with a public aircraft only when it carries a real product name, recognised by "
    "the labeller and recorded in the name decisions, and that product has an evtol.news page; "
    "every other aircraft carries a name generated for this study and cannot be checked this "
    "way. {sm_here_la_name_coverage} splits the {unique_s} aircraft by kind of name and states "
    "how many of each could be matched. TRL, NASA's Technology Readiness Level, is read for "
    "every aircraft, matched or not: 1-2 is an idea on paper, 3-5 a component or a subscale rig "
    "tested, 6-7 a full-size prototype flown, 8-9 certified or in service. It was assessed per "
    "aircraft by the author from public evidence, evtol.news pages and company statements; an "
    "aircraft no public source follows is TRL 2 by construction, so every share above TRL 2 "
    "stated here is a floor. Sources: human labelling, whole-patent reading, evtol.news, the "
    "NASA TRL scale, company statements, AAM Reality Index (May 2026).\n\n"
    "**Procedure.** On the matched aircraft, {sm_here_la_public_pairwise} compares the "
    "architecture class alone, not the other labels, taken from three sources: the drawing "
    "label (the class assigned from the patent's figures), the whole-patent reading (the class "
    "the patent text states) and the public aircraft (the class of its evtol.news page). The "
    "three are compared two at a time, each agreement share with its 95 % interval (statistics "
    "box). {sm_here_a2_d15_trl_by_class} reads TRL per architecture class. "
    "{sm_here_la_trl_representativeness} and {sm_here_la_ari_representativeness} then ask "
    "whether the aircraft public information covers, the aircraft above TRL 2 and the aircraft "
    "of the {tk_ari_firms_n} firms the AAM Reality Index has ever scored, differ from the rest "
    "of the corpus on six attributes: architecture class, applicant region, priority window and "
    "filer type, and priority year and propulsive units.\n\n"
    "**Scientific grounds.** The agreement share's 95 % interval is the Wilson interval, "
    "finite-population corrected (statistics box); the matched aircraft are not a random draw, "
    "they over-represent firms with a public product, so the interval is read as the precision "
    "of the count and not as a statement about the whole record. The six-attribute comparison "
    "uses chi-square, χ² = Σ (O − E)² / E, for the four categorical attributes (architecture "
    "class, applicant region, priority window, filer type) and Mann-Whitney U, "
    "U = n₁n₂ + n₁(n₁ + 1)/2 − R₁, for the two numeric ones (priority year, propulsive units), "
    "the same tests and the same 0.05 line set out in the statistics box. p below 0.05 on an "
    "attribute means the group differs from the rest of the corpus on it and cannot stand for "
    "the corpus on that attribute.\n\n"
    "**Assumptions and limits.** A TRL above 2 is a floor, not a count of every aircraft that "
    "has flown or been built, because an aircraft with no public trace could still exist "
    "without one. The AAM Reality Index is an analyst's judgement, not a measurement, and it "
    "covers only the firms it has chosen to rate.\n"),
})

# C37: the note on the index's name moved into the Method block of 1.3, where the index is
# first used; nothing is printed under the section any more
AFTER.pop("1.3", None)

#: items printed without a takeaway (C25: "the table is enough")
NO_TAKEAWAY = {"la_public_pairwise"}


def _item_chapter() -> Dict[str, str]:
    """The chapter each item is printed in — the first segment of the node that carries it."""
    out: Dict[str, str] = {}
    for n in NODES:
        ch = n["id"].split(".")[0]
        for name in list(n.get("figures") or []) + list(n.get("tables") or []):
            out.setdefault(name, ch)
    return out


ITEM_CHAPTER = _item_chapter()


# ---- 2026-09-26, chapter-1 review: tables as printed -------------------------------------
# C36: the named-organisation column answered nothing the section asks
COLUMNS["la_name_coverage"] = ["aircraft", "unique aircraft", "share of the analysis set",
                               "linked to an evtol.news page", "compared with the public aircraft",
                               "why"]
COLUMNS["la_public_pairwise"] = ["comparison", "agree", "of", "share", "95 % interval",
                                 "the disagreements"]

#: C23: the comparison is of the architecture class only, and the row says so
_PAIRWISE_LABEL = {
    "drawing label against the public aircraft":
        "architecture class: drawing label against the public aircraft",
    "patent text against the public aircraft":
        "architecture class: patent text against the public aircraft",
    "drawing label against the patent text":
        "architecture class: drawing label against the patent text",
}
#: C28, C30: a p above 0.05 is "no difference detected", never "matches"
_VERDICT_LABEL = {"matches the rest": "no difference detected",
                  "does NOT match the rest": "differs"}


def _population_n() -> Optional[int]:
    """N of the finite-population correction: the unique aircraft of the analysis set."""
    raw = str(_VALUES.get("unique_s", "") or _VALUES.get("unique", ""))
    digits = "".join(ch for ch in raw if ch.isdigit())
    return int(digits) if digits else None


def wilson_fpc(x: float, n: float, N: Optional[int], z: float = 1.96):
    """95 % Wilson score interval of x/n, with the finite-population correction applied as an
    effective sample size n·(N − 1)/(N − n). Returns (low, high) or None."""
    import math
    if not n or n <= 0:
        return None
    ph = x / n
    ne = n
    if N and N > n:
        ne = n * (N - 1) / (N - n)
    elif N and N <= n:                     # a census: no sampling error at all
        return (ph, ph)
    den = 1 + z * z / ne
    ctr = (ph + z * z / (2 * ne)) / den
    half = z * math.sqrt(ph * (1 - ph) / ne + z * z / (4 * ne * ne)) / den
    return (max(0.0, ctr - half), min(1.0, ctr + half))


def _fmt_ci(ci) -> str:
    return "" if ci is None else f"{ci[0]:.2f}–{ci[1]:.2f}"


#: 2026-09-27 audit fix (AUDIT_ch1-2_comments.md): la_tables prints a file name into a cell of
#: la_name_coverage's "why" column, which is shared with the full document and cannot be edited
#: there. The brief alone rewrites that one cell so no file name reaches printed text.
def _no_filename_in_why(t):
    if "why" in t.columns:
        t = t.copy()
        t["why"] = t["why"].astype(str).str.replace(
            "the labeller recognised the aircraft and NAME_DECISIONS.csv records the product name",
            "the labeller recognised the aircraft, and the product name was confirmed in the name review",
            regex=False)
    return t


#: 2026-09-27 (F12): la_ari_timeline's year and year-count columns are float in the CSV
#: (NaN where a firm has no planned entry into service), so the generic float rule above prints
#: whole years as "2018.0" — it only strips trailing zeros when rounding actually changes the
#: value. Printed here as a bare integer, or blank where the index states none.
_ARI_TIMELINE_INT_COLS = ("first flight (ARI)", "entry into service (ARI)",
                          "years to first flight", "years to entry into service")


def _ari_timeline_int_cell(x):
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return x
    return "" if xf != xf else f"{xf:.0f}"


def _ari_timeline_ints(t):
    t = t.copy()
    for c in _ARI_TIMELINE_INT_COLS:
        if c in t.columns:
            t[c] = t[c].map(_ari_timeline_int_cell)
    return t


_print_format_base = print_format


def print_format(name: str, t):          # noqa: F811 — wraps the formatter above
    t = _print_format_base(name, t)
    if name == "la_name_coverage":
        t = _no_filename_in_why(t)
    if name == "la_ari_timeline":
        t = _ari_timeline_ints(t)
    hook = PRINT_HOOKS.get(name)
    if hook is not None:                   # 2026-09-26: a chapter module's print hook
        t = hook(t)
    if name == "la_public_pairwise" and {"agree", "of"} <= set(t.columns):
        N = _population_n()
        ci = [_fmt_ci(wilson_fpc(float(a), float(o), N)) for a, o in zip(t["agree"], t["of"])]
        pos = list(t.columns).index("share") + 1 if "share" in t.columns else len(t.columns)
        t.insert(pos, "95 % interval", ci)
        t["comparison"] = t["comparison"].map(lambda v: _PAIRWISE_LABEL.get(str(v), v))
    if name in ("la_trl_representativeness", "la_ari_representativeness") and "verdict" in t.columns:
        t["verdict"] = t["verdict"].map(lambda v: _VERDICT_LABEL.get(str(v), v))
    return t


def _ch1_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    """Chapter-1 numbers the spec grammar cannot say: the class-agreement interval, and the
    lead over first flight that is left once the publication lag is paid."""
    out: Dict[str, str] = {}
    pw = (tables or {}).get("la_public_pairwise")
    if pw is not None:
        try:
            row = pw[pw["comparison"].astype(str).eq("drawing label against the public aircraft")].iloc[0]
            N = _population_n()
            if N is None:
                digits = "".join(ch for ch in str(values.get("unique_s", "")) if ch.isdigit())
                N = int(digits) if digits else None
            out["sm_pw_ci"] = _fmt_ci(wilson_fpc(float(row["agree"]), float(row["of"]), N))
        except Exception:
            pass
    try:
        lead = float(values.get("sm_ff_lead", ""))
        lag = float(values.get("lag_p90", ""))
        out["sm_ff_visible"] = f"{lead - lag:.0f}"
    except (TypeError, ValueError):
        pass
    # 2026-09-27 review (F1): the statistics box names the Multirotor worked example's own n
    # and states its p as "about k in 100" rather than a bare decimal, straight off the same
    # row of la_trace_trends that _driver_numbers already reads for sm_t_units_mr_first/_last/_p
    try:
        tt = (tables or {}).get("la_trace_trends")
        if tt is not None and "trace" in tt.columns:
            sel = tt[tt["trace"].astype(str).str.strip().eq("propulsive units")
                     & tt["code"].astype(str).str.strip().eq("MR")]
            if len(sel):
                r = sel.iloc[0]
                n = _la._tk_float(r.get("aircraft"))
                if n is not None:
                    out["sm_t_units_mr_n"] = f"{round(n):d}"
                p = _la._tk_float(r.get("p"))
                if p is not None:
                    out["sm_t_units_mr_p100"] = f"{round(p * 100):d}"
    except Exception:
        pass
    return out


NUMBERS.update({
    # 2026-09-26, chapter-1 review
    "tk_ari_firms_n": dict(table="la_ari_firms", how="rows", fmt="int"),
    "sm_trl_lc_n": dict(table="a2_d15_trl_by_class", where=("class", "Lift + Cruise"),
                        col="above TRL 2", fmt="int"),
    "sm_trl_tr_n": dict(table="a2_d15_trl_by_class", where=("class", "Tilt Rotor"),
                        col="above TRL 2", fmt="int"),
    "sm_trl_rest_n": dict(table="la_trl_representativeness", where=("test", "chi-square"),
                          col="n rest", fmt="int"),
})


def _in_method_chapter(name: str) -> bool:
    return ITEM_CHAPTER.get(name) in METHOD_RESULTS


def level_line(node_id: str, values: Optional[Dict] = None) -> str:
    """The question in full, then the unit of analysis, printed where the full document
    prints the level of analysis. ``report`` calls this with the node id alone, so the unit
    line's numbers are filled from :data:`_VALUES`, set by :func:`resolve`."""
    # 2026-09-24: the unit is printed under every item (the Unit line of la_lines), so the
    # section-level unit paragraph is gone; a chapter prints its question in full and nothing else
    line = _question_line(node_id) if node_id in _la.QUESTIONS else ""
    tag = STICKERS.get(node_id)
    if tag:
        label, why = tag
        line = (f'<div class="sticker"><b>{label}</b>{why}</div>' + ("\n\n" + line if line else ""))
    return line


#: the margin stickers (2026-09-24, "flag those with a visible sticker on the margin"): the
#: sub-questions whose answer is still open, and what closes each. Keyed by node id; printed by
#: :func:`level_line` right under the heading, floated into the right margin by the stylesheet's
#: ``div.sticker`` rule (a no-op on any document that never emits it). Remove an entry when the
#: work is done.
STICKERS: Dict[str, tuple] = {
    # 2026-09-25: the doubling time is fitted and the discovery curve is built, so those two
    # stickers are closed. The lag is now tested and the test does not settle it, which is a
    # different sticker and not a closed one.
    "M":    ("OWED", "the relabel of 50 patents has not been run"),
}


# --------------------------------------------------------------------------
# the four lines under every item (2026-09-24, the brief's review)
# --------------------------------------------------------------------------
# Author's rule: "tell the sources, explain the metrics that are not evident, state the results,
# then the takeaways". Under an item that is Source · Unit · How to read · Takeaway. The first
# three are the full document's lines (``la_lines``, through ``la_index``), so the two documents
# cannot disagree; the fourth is this document's own takeaway.
FOUR_LINES = (("source", "Source"), ("unit", "Unit"), ("read", "How to read"), ("why", "Takeaway"))


# 2026-09-26: in a chapter of METHOD_RESULTS the first three lines are stated in the Method
# block of the sub-question instead, so under the item they print nothing.
def source(name, values=None, kind="figure", tables=None):
    if _in_method_chapter(name):
        return ""
    return _la.source(name, values, kind, tables)


def unit(name, values=None, kind="figure", tables=None):
    if _in_method_chapter(name):
        return ""
    return _la.unit(name, values or _VALUES, kind, tables or _TABLES)


def read(name, values=None, kind="figure", tables=None):
    if _in_method_chapter(name):
        return ""
    return _la.read(name, values or _VALUES, kind, tables or _TABLES)


def why(name, values=None, kind="figure", tables=None):
    """Printed as ``Takeaway:`` — the slot the renderer calls ``why``."""
    if name in NO_TAKEAWAY:
        return ""
    return takeaway(name, values, kind, tables)


#: The chapter Answers, itemised (author, 2026-09-24, C5: "this is the answer to the big
#: question, so if you put a box around it or another colour it will have more importance. And
#: if you could put it itemised it would be easier to read — this goes for all Answers!!").
#:
#: The full document keeps the prose Answers of ``la_lines.ANSWER``; this register overrides
#: them for the brief alone, as lead sentence plus three to five bullets, inside
#: ``div.answer-box`` — the class the stylesheet holds to one page. Nothing is typed: every
#: number is the same placeholder the prose Answer used, resolved through the same registers.
SM_ANSWER: Dict[str, str] = {
    # 2026-09-26: chapter 2 is new (the design space); its Answer is written in the chapter-2 round
    "2":
        "**[The design-space Answer is written in the chapter-2 round.]**",
    "1":
        "**Yes as a census of what is being designed — no as a ranking of what will fly.**\n\n"
        "- **It is early.** Of the {sm_ff_dated} index firms here with a dated first flight, "
        "{sm_ff_before} filed before they flew, a median of {sm_ff_lead} years earlier — so a "
        "class is visible in the filings before the aircraft exists. Entry into service sits a "
        "median of {sm_ff_eis} years after the first patent, and every gap is a floor: the "
        "clock starts at the firm's first patent in this corpus, which is why "
        "{sm_ff_neg} firms print a negative year and none of them flew before they "
        "patented.\n"
        "- **It is incomplete by construction.** A priority year cannot be read until its "
        "publication lag has run, which is why every trend in this document stops at 2023.\n"
        "- **It is not permanent.** {tk_lapsed_all} of the {tk_lapsed_n} primary patents with "
        "priority 2019 or earlier are out of force, and the classes lapse at the same rate: lapse "
        "measures age and office, never architecture. Examination says the same — the offices "
        "differ sharply from each other, the classes not at all.\n"
        "- **Where it can be checked it holds, for the aircraft that can be checked.** The drawing "
        "label and the firm's public aircraft agree for {tk_pw_share} of the {tk_pw_n} that can be "
        "matched — but only an aircraft with a real product name can be matched, so that set "
        "over-represents publicly documented firms.\n"
        "- **It is not a leaderboard.** The firms the market rates hold aircraft that differ from "
        "everyone else's in citation rank and in survival, and not in architecture class.",

    "3":
        "**Nothing is converging, and what moves is one event wearing four disguises.**\n\n"
        "- **No dominant design, on any of the three conditions.** The largest archetype anywhere "
        "reaches {tk_dd_top_share} against a 50 % line; evenness stays inside the permutation "
        "band; the spread of the space falls below its early level in {tk_q_below} of "
        "{tk_q_cells} cells and only under one of the two weightings.\n"
        "- **Not even read as one family.** Lift + Cruise together with the boom-layout CVT — "
        "tested post hoc, because the record suggested it — peaks at {sm_fam_c_peak} of 2020-23 "
        "and clears 50 % in no complete window.\n"
        "- **Not inside a class either.** No class settles on a single configuration: the most "
        "common one tops out at under a third of its class, and the configurations per aircraft do "
        "not fall.\n"
        "- **What moves is one move.** The twin tilt-rotor becomes a fore-and-aft pair of tilting "
        "sets; the unit count and the propulsor-type count follow it; CVT's ducting falls because "
        "the body that was the duct went away, not because a duct stopped being wanted.\n"
        "- **Per propulsive unit, tilting joints fall** — so the cost drivers win, and the class "
        "growing fastest, Lift + Cruise, has no tilting joint at all.",

    "4":
        "**Open, and more open than the sector's account of itself.**\n\n"
        "- **A crowd, not a top tier.** {tk_firms_all} named firms file here and "
        "{tk_seg_one_firms} of them hold a single aircraft; named companies hold "
        "{tk_fm_named_share} of the analysis set and individual inventors most of the rest.\n"
        "- **No class is one company's programme.** Dropping the firm that moves the reading most "
        "({tk_lev_firm}) shifts no class share by more than {tk_lev_pp} percentage points, and the "
        "largest classes each divide as if between twenty-five equally sized filers.\n"
        "- **Arrival moves the mix, not conversion.** Entry dominates every window — most of the "
        "firms active in one are filing for the first time, so the population cannot be read "
        "for firm strategy. The firms entering a window bring a different class mix than the "
        "window holds, while a firm that files again usually files in the same class.\n"
        "- **Tilt Wing is the exception and the diagnostic.** Firms keep arriving with it after its "
        "share has peaked, and only about one succession in six stays: it is a step on the way.\n"
        "- **What this record cannot say.** It holds no funding, capitalisation or headcount, so "
        "nothing here supports or refutes a claim about better-capitalised newcomers.",

    "5":
        "**Region changes how much is filed and when — not what is designed.**\n\n"
        "- **Three countries hold two thirds of the corpus**, and the regions do not run on one "
        "clock: North America passes the middle of its own filings in {tk_na_50}, Europe in "
        "{tk_eu_50}, Asia-Pacific in {tk_ap_50}.\n"
        "- **There are no regional design blocs.** Two firms from the same region are no more alike "
        "in class profile than two firms from different regions ({tk_prox_same} against "
        "{tk_prox_diff} over {tk_prox_pairs} pairs), and Europe is the least alike internally.\n"
        "- **The lead is solid; the size of the gap is not settled.** Whether the regional offset "
        "is the same in every class is borderline, and the reason is a change of sign: "
        "Asia-Pacific is years behind on Lift + Cruise, Tilt Rotor and Tilt Wing, and slightly "
        "ahead on Combined vectored thrust.\n"
        "- **What survives is smaller than a regional strategy** and is worth stating as such: "
        "North America keeps a higher share of tilting architectures throughout, and China's "
        "filings lean to lift-plus-cruise and to wingless designs.\n"
        "- **A reader who expected Europe, China and the United States to be building different "
        "aircraft should take the null as the finding.**",

    "M":
        "**The drawing alone carries the architecture for the large winged classes and fails for "
        "the small ones.**\n\n"
        "- Agreement with the whole-patent reading is {tk_gt_tr} for tilt rotor and {tk_gt_slc} "
        "for lift-plus-cruise.\n"
        "- It falls to {tk_gt_ptc} for the powered-tail class and {tk_gt_hb} for hybrids, so every "
        "small-class number in this document is the least reliable on its page.\n"
        "- Where the sources disagree the cases are listed by name rather than counted, so every "
        "one of them can be checked.\n"
        "- **Still owed:** every agreement number here is against another source, never the "
        "labeller against himself. The relabel of 50 patents is what closes that.",
}


def _fill_block(text_: str, values: Optional[Dict], tables: Optional[Dict]) -> str:
    """:func:`la_index._clean` collapses every run of whitespace, which would fold a bulleted
    block into one line, so an itemised Answer resolves its numbers here instead: the same
    registers through ``la_index._vals``, the same honest ellipsis for an unresolved
    placeholder, and the line breaks left alone."""
    out = _pa._fill(text_, _la._vals(values, tables, text_))
    out = _re.sub(r"\s*\(n \{[^{}]*\}\)", "", out)
    # 2026-09-25: an unresolved placeholder in a STATED ANSWER fails the build instead of
    # degrading. The ellipsis is the grey lines' honest fallback; here it shipped "… index
    # firms" into the document's headline answer without any guard noticing, because the
    # render's own check looks for surviving braces and the braces were already gone.
    left = _re.findall(r"\{[^{}]*\}", out)
    if left:
        raise KeyError(f"unresolved in a stated answer: {', '.join(sorted(set(left)))}")
    return out


def answer(question, values=None, tables=None):
    """The block that closes a chapter.

    Boxed and itemised for this document (:data:`SM_ANSWER`); a chapter with no entry falls
    back on the full document's prose Answer, so the two can never silently diverge on a
    chapter nobody rewrote. ``report._answer_md`` prints its own ``**Answer.**`` label and its
    own ``div.answer`` wrapper around whatever comes back, so the box opens on a blank line of
    its own and the stylesheet's ``div.answer-box`` rule takes it from there.
    """
    own = SM_ANSWER.get(question)
    if own is None:
        return _la.answer(question, values or _VALUES, tables or _TABLES)
    body = _fill_block(own, values or _VALUES, tables or _TABLES)
    return ('\n\n<div class="answer-box" markdown="1">\n\n'
            "#### Answer\n\n" + body + '\n\n</div>\n')


#: the resolved numbers of the last :func:`resolve` call — the only route by which
#: :func:`level_line`, which ``report`` calls without ``values``, can fill its unit line.
_VALUES: Dict = {}

#: the built tables of the last :func:`resolve` call — the chapter Answers are read through
#: ``la_index.answer``, which resolves its numbers against them.
_TABLES: Dict = {}


def text(node_id: str, values: Optional[Dict] = None) -> str:
    """The prose printed between a heading and the items under it — empty for the six
    new-question sections, whose panel comes first and whose prose is printed by
    :func:`after`. ``report.write_markdown`` prints heading, this, then the items, so a node
    that wants its figure ahead of its words simply leaves this empty."""
    n = node(node_id)
    if node_id in PANEL_SECTIONS:
        return ""
    if n.get("answer"):                    # a chapter opens on its question; the Answer closes it
        # one chapter opens on the methods box as well (2026-09-25): the chapter that uses p,
        # the permutation band, the Hill numbers and the three conditions is the only place the
        # explanation can be read where it is needed.
        parts = []
        if node_id in CHAPTER_METHOD:              # 2026-09-26: the shared method opens chapter 1
            parts.append(_pa._fill(CHAPTER_METHOD[node_id], values))
        if node_id == METHODS_CHAPTER:
            parts.append(_pa._fill(METHODS_BOX, values))
        return "\n\n".join(parts)
    return _pa._fill(n.get("text") or TEXTS.get(node_id, ""), values)


def after(node_id: str, values: Optional[Dict] = None) -> str:
    """The prose printed under the items. For the six new-question sections it is the whole
    section — the measure, why it is a question and what would answer it — kept in
    :data:`TEXTS` beside every other section's prose rather than in a register of its own."""
    own = node(node_id).get("after") or AFTER.get(node_id, "")
    if not own and node_id in PANEL_SECTIONS:
        own = TEXTS.get(node_id, "")
    return _pa._fill(own, values)


# --------------------------------------------------------------------------
# 6 — numbering: one running sequence over the whole document
# --------------------------------------------------------------------------
# Built once, at import, by walking NODES in order. ``report.write_markdown`` asks for
# ``figure_number(node_id, k, total)``, so the map is keyed by (node id, position).
_FIG_NUM: Dict = {}
_TAB_NUM: Dict = {}


def _number_items() -> None:
    _FIG_NUM.clear()
    _TAB_NUM.clear()
    f = t = 0
    for n in NODES:
        for k, _ in enumerate(n.get("figures", [])):
            f += 1
            _FIG_NUM[(n["id"], k)] = str(f)
        for k, _ in enumerate(n.get("tables", [])):
            t += 1
            _TAB_NUM[(n["id"], k)] = str(t)


_number_items()


#: internal name -> "Figure 3" / "Table 12", the item's number IN THIS DOCUMENT. Built from
#: the same two maps the renderer numbers with, so a section that points at an item printed
#: earlier quotes the number the reader sees, and reordering :data:`NODES` moves the pointer.
HERE_REF: Dict[str, str] = {}


def _here_refs() -> None:
    HERE_REF.clear()
    for n in NODES:
        for k, name in enumerate(n.get("figures", [])):
            HERE_REF[name] = f"Figure {_FIG_NUM[(n['id'], k)]}"
        for k, name in enumerate(n.get("tables", [])):
            HERE_REF[name] = f"Table {_TAB_NUM[(n['id'], k)]}"


_here_refs()


def figure_number(node_id: str, k: int, total: int) -> str:
    return _FIG_NUM.get((node_id, k), f"{node_id}.{k + 1}")


def table_number(node_id: str, k: int, total: int) -> str:
    return _TAB_NUM.get((node_id, k), f"{node_id}.{k + 1}")


# --------------------------------------------------------------------------
# 7 — the grey line: the takeaway, and where the item lives in the full document
# --------------------------------------------------------------------------
#: internal name -> "Figure 1.1.6a" / "Table 1.2.3c", the item's number in the full
#: LABELLING_ANALYSIS. Filled by :func:`set_full_reference` at render time from
#: ``la_index.NODES`` and the figures and tables that actually exist, which is exactly how
#: ``report.write_markdown`` numbers that document.
FULL_REF: Dict[str, str] = {}

#: items printed here that the full document does not print. They are named rather than
#: silently left without a reference.
NOT_IN_FULL: Dict[str, str] = {
    "a2_d15_trl_by_class": "Full table: `tables/a2_d15_trl_by_class.csv`",
    "a2_d16_public_match": "Full table: `tables/a2_d16_public_match.csv`",
    "la_duct_units": "Full table: `tables/la_duct_units.csv`",
    # the six panels: drawn for this document, so what closes their grey line is where the
    # numbers on them come from
    "sm_duct_bands": "Drawn from `tables/la_duct_units.csv`",
    "sm_weighting": "Drawn from `tables/la_dd_q.csv`",
    "sm_archetype_filers": "Drawn from `tables/la_zones.csv`",
    "sm_tw_entry": "Drawn from `tables/la_cohorts.csv`, `tables/la_cohort_mix.csv` and "
                   "`tables/la_class_cycles.csv`",
    "sm_trl_tracked": "Drawn from `tables/a2_d15_trl_status.csv`",
    "sm_cite_rank": "The two medians are the `la_ari_gap` row; the distributions behind them "
                    "are the same rank and the same split that table is built from",
}


def set_full_reference(figures, tables) -> Dict[str, str]:
    """Number every item as the FULL document numbers it, from ``la_index.NODES``.

    ``figures`` and ``tables`` are the names that exist — the same filter
    ``report.write_markdown`` applies when it walks that module — so the numbers computed here
    are the numbers printed there. Returns the map, and stores it in :data:`FULL_REF`.
    """
    FULL_REF.clear()
    for n in _la.NODES:
        nid = n["id"]
        figs = [f for f in n.get("figures", []) if f in figures]
        tabs = [t for t in n.get("tables", []) if t in tables]
        for k, name in enumerate(figs):
            FULL_REF[name] = f"Figure {_la.figure_number(nid, k, len(figs))}"
        for k, name in enumerate(tabs):
            FULL_REF[name] = f"Table {_la.table_number(nid, k, len(tabs))}"
    return FULL_REF


#: Takeaways written for this document. Two reasons only, both recorded per entry: the item
#: has NO takeaway in ``la_index`` (it is printed in no document, or its line was never
#: written), or its takeaway is a paragraph that would cost this document a third of a page.
#: A takeaway here is resolved through the same registers as every other number.
TAKEAWAY: Dict[str, str] = {
    # ---- 2026-09-25, the nine items the review added (printed "not written yet" until the
    # print audit caught it)
    "la_name_coverage":
        "{sm_nc_named} aircraft carry a real product name and {sm_nc_gen} a generated one; "
        "{sm_nc_gen_matched} of the generated ones could be matched to a public aircraft. So every "
        "public comparison in this document speaks for the named aircraft, which over-represent "
        "publicly documented firms — not for the record as a whole",
    "sm_family":
        "**Even read as one family, Lift + Cruise and the boom-layout CVT stay below the 50 % line "
        "in every window** — {sm_fam_c_peak} at their peak, {sm_fam_b_peak} on the widest "
        "definition. The closest this record comes to a dominant design is still not one",
    "la_family_dd":
        "Condition 1 fails for the family in every window and condition 3 in {sm_fam_c3_cells} of "
        "{sm_fam_c3_total}; the verdict is no on all three definitions",
    "discovery_curve":
        "**Closed at the coarse levels, still opening at the finest.** Classes stopped appearing "
        "long ago; at the design-species level {sm_disc_a1t_new100} new archetypes appeared in the "
        "last hundred aircraft against {sm_disc_a1t_exp100} expected by chance",
    "sm_duct_conditional":
        "**Once a designer ducts one unit, they usually duct them all**: {sm_ductc_all} of the "
        "aircraft with any ducted unit duct every one. Ducting is mostly a choice for the whole "
        "aircraft, not for a single unit",
    "sm_joints_per_unit":
        "**Counted per aircraft the tilting joints rise; counted per propulsive unit they fall** "
        "(Tilt Rotor ρ {sm_jpu_tr_rho}, p {sm_jpu_tr_p}). Designers added rotors, and the joints "
        "only followed them",
    "la_joints_per_unit":
        "Inside CVT the per-unit trace is flat (ρ {sm_jpu_cvt_rho}, p {sm_jpu_cvt_p}); inside Tilt "
        "Rotor it falls. Neither supports the earlier reading that joints rose against the cost "
        "drivers",
    "la_tw_successions":
        "**Tilt Wing is a first stop, not a destination**: only {sm_tw_stay} of its {sm_tw_n} "
        "successions stay in it, and {sm_tw_to_tr} go on to Tilt Rotor — against {sm_slc_stay} "
        "that stay in Lift + Cruise and {sm_tr_stay} in Tilt Rotor",
    "la_lag_constancy":
        "The regional lead is solid (p {sm_lag_p_region}); whether it is the same size in every "
        "class is not settled (p {sm_lag_p_inter}). Read North America first, Europe second, "
        "Asia-Pacific third, but not as a fixed number of years",
    # ---- 2026-09-25, the docx review
    "atlas_arch_time":
        "Lift + Cruise overtakes Tilt Rotor and keeps the lead: TR falls from {tk_tr_w1} of the "
        "earliest window's aircraft to {tk_tr_w4} in 2020-23 while SLC rises from {tk_slc_w1} to "
        "{tk_slc_w4}; with CVT ({tk_cvt_w4}) the three hold about three quarters of the recent "
        "corpus. Two limits on that reading: the earliest window rests on {sm_w1_n} aircraft "
        "against {sm_w4_n} at the recent end, so the early shares are coarse; and **no published "
        "source resolves eVTOL filings by architecture over time**, so the crossover is stated on "
        "this corpus alone. The nearest public series counts announced aircraft as a cumulative "
        "stock and pools Tilt Rotor, Tilt Wing and CVT into one category, which neither confirms "
        "nor refutes it.",
    "zones":
        "**A crowded core and an empty rim, and the plot says which is which.** Right on the top "
        "panel means the archetype holds a large share of the recent aircraft; low down means few "
        "distinct filers per aircraft, so one firm holds several of them. The crowded core is "
        "therefore the lower right, and the empty rim is the left-hand edge, where most archetypes "
        "sit with a handful of aircraft each. The largest is {sm_zones_top}, with "
        "{sm_zones_top_air} aircraft from {sm_zones_top_filers} filers — a large share AND a high "
        "filer count, so **the crowding is a crowd and not one "
        "company**. Of the {sm_zones_n} archetypes drawn, {sm_zones_persist} are persistent, "
        "{sm_zones_new} are new since 2016 and {sm_zones_fading} have gone absent: nothing in this "
        "record has been abandoned. Blank cells in the lower panel are windows with no aircraft of "
        "that archetype, and an archetype under five aircraft is not drawn at all — neither is an "
        "'absent' category.",
    "firm_influence":
        "**No single firm decides a class share, so the class reading of this document stands as "
        "written.** Dropping {tk_lev_firm}, the largest filer in the corpus, moves the "
        "{tk_lev_class} share by {tk_lev_pp} percentage points and no other firm moves any share "
        "further. A shift of that size changes no ranking and no verdict, so the answer to 'should "
        "the analysis change because of one firm' is no.",
    "la_filers_by_window":
        "**Entry dominates every window: most active firms are filing for the first time, and a "
        "population that is mostly first-time filers cannot be read for firm strategy.** The "
        "individual share falls from {tk_indshare_w1} to {tk_indshare_2023} as organisations "
        "arrive. What the corpus cannot say is whether the arriving organisations are better "
        "capitalised: it holds no funding, capitalisation or headcount of any kind.",
    # ---- 2026-09-24, the brief's review
    "dimension_drift":
        "(i) Propulsive units: the median rises in Tilt Rotor ({tk_tr_units_w1} → {tk_tr_units_w4}) "
        "and stays at {tk_slc_units_w1} in Lift + Cruise — the tilting classes catch up on "
        "distributed propulsion. (ii) Ducting falls inside CVT ({sm_dd_cvt_duct_w1} → "
        "{sm_dd_cvt_duct_w4}) and drifts in Lift + Cruise ({sm_dd_slc_duct_w1} → {sm_dd_slc_duct_w4}): "
        "no class is adopting the duct. (iii) No tail surface: Lift + Cruise {sm_dd_slc_tail_w4} "
        "against Tilt Rotor {sm_dd_tr_tail_w4} in 2020-23 — the tail is a class property, not a "
        "trend. (iv) Booms: CVT goes from {tk_cvt_boom_w1} to {tk_cvt_boom_w4}; Lift + Cruise sits "
        "at {sm_dd_slc_boom_w4} — units move onto booms where the class has to carry both lift and "
        "cruise sets. (v) Electric-only: Lift + Cruise {sm_dd_slc_el_w4}, Tilt Rotor {sm_dd_tr_el_w4} "
        "of the aircraft that state a powertrain — the tilt-rotor is where hybrid survives.",
    "atlas_units":
        "No standard rotor count: the five bands hold {bin_r03}, {bin_r4}, {bin_r56}, {bin_r78} and "
        "{bin_r9} aircraft. (iii) Ducting is U-shaped in rotor count — {sm_duct_13} at 1-3 units, "
        "{sm_duct_78} at 7-8, {sm_duct_9} at 9+ — because it is two designs: at the low end one "
        "ducted cruise or tail fan, at the high end a whole ducted-fan array (next figure).",
    "sm_driver_traces":
        "Joints, units and propulsor types rise together inside Tilt Rotor and CVT and nowhere else; "
        "ducting falls in CVT alone. Lift + Cruise, the class that grows, moves on none of the four.",
    "sm_driver_corr":
        "**Three of the four traces are one move: the twin tilt-rotor becoming a fore-and-aft pair "
        "of tilting sets** — the share with two or more tilting sets rises, and the unit count "
        "follows the set count almost exactly (panels i and ii). **The fourth is not a design "
        "choice at all but a composition effect: CVT without booms ducts throughout, and the "
        "boom-layout CVT that arrives after 2016 barely ducts** (panel iii). Four moving traces, "
        "two events.",
    "sm_duct_count":
        "**An aircraft that ducts anything usually ducts everything**: {sm_ductc_all} of the "
        "corpus's ducting aircraft duct every unit they carry. At nine units and more that becomes "
        "an array — {sm_duct9_units} of the band's units in a duct, a median of {sm_duct9_med} "
        "ducted units per ducting aircraft; at 1-3 units the same rule produces one fan (median "
        "two). The U-shape of the yes/no line is two different designs at its two ends, not one "
        "design more or less common.",
    "sm_entry_all":
        "Lift + Cruise takes {tk_cm_e_slc} of the firms entering in 2020-23 against {tk_cm_a_slc} of "
        "the window's aircraft; Tilt Wing {sm_tw_ent_2023} against {sm_tw_air_2023}. Entrants "
        "over-index on their moment's class in every window that has enough of them; Tilt Wing is "
        "the one class where they keep arriving after the share has peaked.",
    "sm_class_configs":
        "**(i)** The most common configuration of each class in 2020-23, named: Lift + Cruise "
        "*{sm_modal_slc}* ({sm_modal_slc_share} of the class), Tilt Rotor *{sm_modal_tr}*, CVT "
        "*{sm_modal_cvt}* — each holding well under a third of its class. **(ii)** The y value is "
        "the number of distinct configurations divided by the aircraft in that class-window: 1.0 "
        "would mean every aircraft is its own configuration, 0.2 that five aircraft share one. It "
        "does not fall over time in any class. **No class settles**, and the diversity is real "
        "rather than an artefact of counting fields the class does not choose.",
    "la_class_configs_own":
        "The rules are printed so they can be attacked; on them, {top_class}'s {tk_slc_n_2023} "
        "aircraft of 2020-23 still spread over {sm_own_slc_configs} configurations.",
    "la_duct_count":
        "**Ducting is usually a property of the aircraft, not of one unit on it.** Across the "
        "corpus {sm_ductc_all} of the aircraft that duct anything duct **every** unit they carry; "
        "it is not strictly all-or-nothing, but the middle is thin. The two ends of the band scale are two designs: at "
        "nine units and more {sm_duct9_every} of the whole band duct everything and "
        "{sm_duct9_units} of the band's units run in a duct — an array; at 1-3 units a ducting "
        "aircraft carries a median of two ducted units — one fan. Why an aircraft commits either "
        "way is not in the record: noise and certification are nowhere labelled.",
    "la_trl_representativeness":
        "The {trl_above_s} aircraft above TRL 2 fail {sm_trl_repr_fail} of the six attributes: they "
        "match the corpus on class and region and not on filer type, priority year or propulsive "
        "units. They can answer 'which classes get built' and cannot stand for the corpus on "
        "anything else.",
    "la_ari_representativeness":
        "The {tk_ari_in} index-firm aircraft fail {sm_ari_repr_fail} of the six attributes, so a difference "
        "in Table 4 is a difference between two populations that already differ in who files and "
        "when. What the index carries that the corpus does not: the score itself, disclosed "
        "funding, first-flight date, entry-into-service target, certifying authority and programme "
        "status (the TRL work). Firm-level correlations of the corpus counts with score, funding and "
        "first flight were run (18 firms): none survives correction. The aircraft-level "
        "comparison of Table 4 is the one with power.",
    "la_public_pairwise":
        "{sm_pw_img_pub} of {sm_pw_n} drawing labels carry the public aircraft's class; the text "
        "carries it for {sm_pw_txt_pub}; drawing and text agree with each other on {sm_pw_img_txt} "
        "of {sm_pw_gt_n}. Where the sources disagree, it is mostly the patent describing a different "
        "configuration from the one the firm built — not a misread drawing.",
    "la_top_archetypes":
        "Three branches, the same three in every complete window: one-wing Lift + Cruise, one-wing Tilt "
        "Rotor, one-wing CVT hold {sm_top3_a1t_w4} of 2020-23 together, and **not one of them holds "
        "more than a quarter of its own window** — against the 50 % the first condition of the "
        "dominant-design test asks for; "
        "the leader changed once, Tilt Rotor to Lift + Cruise, at 2016-19. At the rotor-count level "
        "the top three hold {sm_top3_a0c_w4}: the branches are settled, their insides are not.",
    "la_era_frame":
        "On the two measures the test computes the corpus sits in the era of ferment: Q shows no "
        "drop that survives both weightings and ²D never collapses toward one or two designs. The "
        "two measures not computed here were probed on the label space and point the same way.",
    # no takeaway exists in la_index for these three
    "a2_d16_public_match":
        "Where a public aircraft exists, the figure label describes it: {sm_pub_same} of the "
        "{sm_pub_n} matched aircraft carry the same class ({sm_pub_share}). {sm_pub_other} "
        "describe another configuration, drawing and text agreeing that they do; only "
        "{sm_pub_draw} are a drawing that misreads its own patent.",
    "a2_d15_trl_by_class":
        "The patent record is a record of concepts: {trl_above_s} of {trl_aircraft_s} aircraft "
        "({sm_trl_share}) are above TRL 2, and the classes that get patented most are not the "
        "classes that get built — {trl_best_class} leads the large classes, {trl_zero_classes} "
        "have none. TRL 2 is also what an aircraft gets when nothing public is known, so read "
        "every figure here as a floor.",
    "la_ari_gap":
        "The firms the market rates are a different population, and not by where they publish: "
        "eight differences survive the correction over the whole table and six survive being "
        "re-run on the US-published patents alone. The largest is the cohort citation rank, "
        "{sm_cite_idx} against {sm_cite_rest}. Applicant region is marked `yes, by selection` "
        "because that is what the index selects on, and family size `office effect` because it "
        "does not survive the US check.",
    # the new questions' own item; ungraded in the question map, so no line exists for it
    "la_duct_units":
        "Ducting is U-shaped in rotor count, not flat: {sm_duct_13} of the aircraft at three "
        "units or fewer carry a ducted unit, {sm_duct_78} at seven or eight, {sm_duct_9} at nine "
        "or more, against {sm_duct_all} over the corpus. The dip survives holding the class "
        "fixed, so it is not the class mix.",
    # ---- the six panels of the new questions: one reading each, and the base it rests on
    "sm_duct_bands":
        "Ducting is U-shaped in rotor count, not flat: {sm_duct_13} at three units or fewer, "
        "{sm_duct_78} at seven or eight, {sm_duct_9} at nine or more, against {sm_duct_all} of "
        "the {sm_duct_total} aircraft that fall in a band at all. The dip survives holding the "
        "class fixed, so it is not the class mix — and one ducted fan among twelve open rotors "
        "counts here exactly like twelve ducted ones, which is what the question is about.",
    "sm_weighting":
        "The same window, the same test, two answers: at 2020-23 the main weighting falls "
        "{sm_c3_gap_main} below the lower edge of its own permutation band — the condition met "
        "— and the uniform weighting stops {sm_c3_gap_alt} above the edge of its own. The two "
        "levels agree with each other and disagree on nothing; the weighting is the whole of "
        "the difference. Bases on the tick; the last window is incomplete.",
    "sm_archetype_filers":
        "CVT · 5-6 rests on {sm_cvt56_filers} filers for its {sm_cvt56_air} aircraft — "
        "{sm_cvt56_fpa} per aircraft, the lowest of the {sm_zones_big_n} archetypes with "
        "{sm_zones_min} aircraft or more, against {sm_cvt4_fpa} for CVT · 4 next door. A low "
        "value is the shape a firm's own line of variants leaves; it is not proof of one.",
    "sm_tw_entry":
        "In 2020-23 Tilt Wing takes {sm_tw_ent_2023} of the entering firms "
        "({sm_tw_ent_n_2023} of {sm_tw_ent_base_2023}) against {sm_tw_air_2023} of the "
        "window's aircraft ({sm_tw_air_n_2023} of {sm_tw_air_base_2023}) — the one window "
        "where the firms arriving and the aircraft filed point opposite ways. Five windows "
        "compared one at a time and not a trend: {sm_tw_thin_n} of them rest on fewer than "
        "{sm_tw_thin_cut} firms entering with the class and are marked ‡.",
    "sm_trl_tracked":
        "The tenth is a coverage rate before it is a build rate: {trl_above_s} of "
        "{trl_aircraft_s} aircraft are above TRL 2 ({sm_trl_share}), but {sm_trl_nottracked} of "
        "the {trl_aircraft_s} are followed by no public source at all and sit at TRL 2 for that "
        "reason alone. Over the {sm_trl_tracked_n} that are followed, the same {trl_above_s} "
        "are {sm_trl_tracked_share}.",
    "sm_cite_rank":
        "The gap is the whole distribution and not one heavily cited patent: the rated firms' "
        "aircraft are thin below the median of their year and pile up in the top decile, median "
        "{sm_cite_idx} against {sm_cite_rest}, q {sm_cite_q} over the whole table and p "
        "{sm_cite_us} on the US-published patents alone. Bases in the legend.",
    # Q5. The full document's line runs to 149 words; the numbers are the same
    "coverage":
        "There is no top tier: {tk_seg_top_firms} firms hold {tk_seg_top_air} aircraft, the next "
        "{tk_seg_59_firms} hold {tk_seg_59_air}, and all {tk_firms_all} named firms together "
        "{tk_named_share} of the set. Market standing does pick the filers out — the index firms "
        "hold {tk_mkt_held} against {tk_mkt_held_rest} for every other named firm, a median of "
        "{tk_mkt_air_l} aircraft each against {tk_mkt_air_r} ({tk_mkt_air_p}) — but earliness "
        "does not follow ({tk_mkt_year_p}), and the index position does not track the patent "
        "side at all ({tk_mkt_rho}, p {tk_mkt_rho_p}): the two largest patent holders are "
        "incumbents the index rates low or no longer rates.",
    "la_filer_mix":
        "**Which unit is counted does not change the answer — worth settling before any other "
        "table in this chapter is read.** Named companies hold {tk_fm_named_air} of the "
        "{unique_s} aircraft ({tk_fm_named_share}) and {tk_fm_named_pat} of the primary patents; "
        "individual inventors {tk_fm_ind_air} aircraft. No filer type gets appreciably more "
        "aircraft out of one patent than another, so no one can inflate a footprint here by "
        "re-filing one design. Most of the corpus belongs to an organisation — but to a great many "
        "small ones.",
    # Q7
    "la_class_filer_weight":
        "The four largest classes each divide as if between 25 or more equally sized filers, so "
        "their size is a shared choice and not one firm repeating itself. Giving every filer one "
        "vote instead of counting aircraft changes no class's rank.",
    # Q6
    "la_class_region_timing":
        "Every class is taken up first in North America, then Europe, then Asia-Pacific — with "
        "one exception, CVT, whose North American median is {tk_crt_cvt_na}, the latest cell of "
        "that column. The Asia-Pacific lag is widest on the oldest classes and closes on CVT.",
    # the drivers section; the full document's line runs to 169 words
    "la_driver_verdicts":
        "Read the **importance** column first: of the {sm_imp_rows} traces that move, "
        "{sm_imp_central} are **central** — the observations this chapter is built on — "
        "{sm_imp_support} are supporting and {sm_imp_null} is a null: a trace whose classes move in "
        "opposite directions, which therefore separates nothing. "
        "{tk_dr_n_rows} traces in all, and {tk_dr_n_single} sharp statements about a moving driver: "
        "units carried on booms and the stations carrying them rise with distributed propulsion "
        "alone. {tk_dr_n_over} traces are overdetermined (propulsive units and ground contact, "
        "three drivers each), {tk_dr_n_opposed} have opposed drivers and went with regime "
        "transition or occupancy rather than with cost, {tk_dr_n_against} moved against the only "
        "direction a driver gave, {tk_dr_n_still} do not move, {tk_dr_n_fixed} move with only "
        "fixed drivers behind them, {tk_dr_n_mixed} moves both ways by class and "
        "{tk_dr_n_unlab} are not labelled.",
    "la_driver_questions":
        "The propulsor-count rise is a tilting-class rise (TR, CVT), not a Multirotor one and "
        "not general; retraction inside Lift + Cruise is {tk_dr_slc_retract_last} and "
        "{tk_dr_slc_retract_mov}; the tilting-joint COUNT rises inside TR "
        "({tk_dr_tr_joints_mov}) and CVT ({tk_dr_cvt_joints_mov}) while the pooled row is "
        "{tk_dr_all_joints_mov}. **Read per propulsive unit, though, the joints fall**: the "
        "aircraft are gaining propulsors faster than they gain joints, so the cost drivers win at "
        "both levels and the class that grows fastest has no tilting joint at all.",
    # the full document's line names the two rows this document drops (symmetry, standard
    # wings); this one reads only what is printed
    "a2_d3_selected_fields":
        "**Most label fields separate nothing, and that is what this table is for**: a field whose "
        "top answer covers nearly every aircraft tells no two designs apart, and the fields that do "
        "are few. The variety of this corpus lives in two of them: tail type (top answer {tk_emptype}) "
        "and the number of propulsive units (top bin {tk_units_top}); the fixed fuselage "
        "({tk_fuskin}) and the unknown landing gear ({tk_gear_unknown}) are the modal design "
        "and the modal blank. Left out, because their top answer holds {sm_d3_drop_share} or "
        "more of the aircraft: {sm_d3_dropped}.",
    # the la_index line prints the top share as the raw fraction ``0.28``; the same sentence
    # with the share read as a share, so this document is consistent with its own Q4
    "codebook_classes":
        "The twelve classes split on what tilts and what lifts in cruise, never on size or "
        "mission, and they are very unequal: the largest holds {sm_top_class_share} of the "
        "corpus ({top_class}) and {small_classes} classes stay under a dozen aircraft. Only "
        "the five largest can carry a share over time.",
    # shortened: the full line is a 250-word design argument and belongs in the full document
    "atlas_units":
        "There is no standard number of propulsors — the median is {units_median} and the five "
        "bands hold {bin_r03}, {bin_r4}, {bin_r56}, {bin_r78} and {bin_r9} aircraft, the "
        "flattest distribution in the label set. The convergence is in the arrangement: {grp2} "
        "of {units_n} aircraft put their units on exactly two stations. Panel (iii): ducting "
        "falls from {sm_duct_13} at three units or fewer to {sm_duct_78} at seven or eight and "
        "returns to {sm_duct_9} at nine or more, against {sm_duct_all} over the corpus",
}


def takeaway(name: str, values: Optional[Dict] = None, kind: str = "figure",
             tables: Optional[Dict] = None) -> str:
    """The one grey line this document prints under a figure or a table.

    The takeaway itself, then the item's number in the full LABELLING_ANALYSIS, where the unit
    of analysis, the base, the transform and the question line are printed in full. An item of
    :data:`TAKEAWAY` is written for this document; every other item delegates to
    :func:`la_index.takeaway`, so the two documents say the same thing in the same words.
    """
    if name in NO_TAKEAWAY:            # 2026-09-26: with every line empty, report falls back here
        return ""
    own = TAKEAWAY.get(name)
    if own is not None:
        vals = dict(values or {})                      # already carries every resolved number
        line = _la._clean(_pa._fill(str(own), vals))
        line = line if line[-1:] in ".!?" else line + "."
    else:
        line = _la.takeaway(name, values, kind, tables)
    # The grade clause that used to close this line — "Graded supporting; printed here because
    # …" — was dropped on 2026-09-23: it is the document describing its own selection rule to a
    # reader who cannot act on it, and the register still enforces the rule in
    # ``render_summary.check_selection``. The pointer into the full document stays.
    # 2026-09-26 (author): nothing in this document points out of it — no "Full document: …",
    # no "Full table: tables/….csv". The brief now stands alone.
    return line
    tail = []
    ref = FULL_REF.get(name)
    if ref:
        tail.append(f"Full document: {ref}")
    elif NOT_IN_FULL.get(name):
        tail.append(NOT_IN_FULL[name])
    if not tail:
        return line
    return line + " · " + " · ".join(tail) + "."


# --------------------------------------------------------------------------
# 7 — the front-page index (2026-09-24, on request: "put an index in the first page")
# --------------------------------------------------------------------------
# Chapter 1 forces a page break (``div.chapter-start``), so page 1 today holds only the title
# and the meta line — this is where the index goes. The PDF is built by headless Chrome
# printing static HTML, which has no cross-reference primitive for "the page this heading
# landed on", so the page numbers are filled in a second pass: ``render_summary.py`` renders
# once with every number blank, scans the resulting PDF for each entry's own heading text, and
# renders again with the numbers it found. A heading that is not found (search text not matched,
# a font substitution, …) simply keeps its em dash — the index degrades one row, never the build.

#: every chapter and sub-question, in document order — the two kinds of node this index lists.
#: Built from ``NODES`` rather than hand-kept, so a reordering of the chapters cannot desync it.
def _toc_ids() -> List[tuple]:
    ids = []
    for n in NODES:
        nid = n["id"]
        if nid in SM_QUESTIONS or n.get("subq") or nid in ("M", "cannot"):
            ids.append((nid, 1 if n.get("subq") else 0))
    return ids


#: id -> page number (string), set by :func:`set_toc_pages` between the two render passes.
#: Empty on the first pass, which is exactly when every row should print its placeholder.
_TOC_PAGES: Dict[str, str] = {}


def set_toc_pages(pages: Dict[str, str]) -> None:
    """Called between the two passes of ``render_summary.py`` with what the first pass's PDF
    showed. Never called at all on a single-pass run, which is why :func:`index_md` defaults
    every row to an em dash rather than raising on a missing id."""
    _TOC_PAGES.clear()
    _TOC_PAGES.update(pages)


def toc_search_text(nid: str) -> str:
    """The snippet :func:`toc_page_map`-style code searches a rendered page for, to find which
    page ``nid``'s heading landed on. Stylesheet rule ``h1,h2,h3,h4 { break-inside: avoid }``
    guarantees a heading never spans two pages, so any substring of it is safe to search for —
    this one is the heading's own text, capped so it cannot run past the sentence a very long
    chapter question opens with."""
    h = heading(nid).lstrip("#").strip()
    if len(h) <= 70:
        return h
    cut = h[:70].rsplit(" ", 1)[0]
    return cut


def index_md() -> str:
    """The front-page index: one row per chapter (bold) and per sub-question (indented),
    each with a right-aligned page number filled from :data:`_TOC_PAGES` where a second pass
    has run, an em dash otherwise. Raw HTML, not a markdown list — ``build_styled_md_pdf.py``
    loads ``md_in_html`` but a hand-built two-column row is simpler to get right than fighting
    the list parser for a dotted leader, and the CSS that styles ``div.toc`` is a no-op on
    every document that never emits it."""
    rows = []
    for nid, level in _toc_ids():
        title = heading(nid).lstrip("#").strip()
        pg = _TOC_PAGES.get(nid, "—")
        cls = "toc-l0" if level == 0 else "toc-l1"
        rows.append(f'<div class="toc-row {cls}"><span class="toc-t">{title}</span>'
                    f'<span class="toc-d"></span><span class="toc-p">{pg}</span></div>')
    return ('<!-- TOC -->\n<div class="toc">\n<div class="toc-h">Contents</div>\n'
            + "\n".join(rows) + "\n</div>\n<!-- /TOC -->")


NUMBERS.update({
    # 2026-09-26 (C15): out of force per unique aircraft, sm_open.force_aircraft
    "sm_fa_n": dict(table="la_force_aircraft", where=("class", "all classes"),
                    col="unique aircraft", fmt="int"),
    "sm_fa_out": dict(table="la_force_aircraft", where=("class", "all classes"),
                      col="out of force", fmt="int"),
    "sm_fa_share": dict(table="la_force_aircraft", where=("class", "all classes"),
                        col="out of force share", fmt="pct"),
    "sm_fa_old": dict(table="la_force_aircraft", where=("class", "all classes"),
                      col="out of force, primary patent only", fmt="pct"),
    "sm_fa_tr": dict(table="la_force_aircraft", where=("class", "Tilt Rotor"),
                     col="out of force share", fmt="pct"),
    "sm_fa_slc": dict(table="la_force_aircraft", where=("class", "Lift + Cruise"),
                      col="out of force share", fmt="pct"),
    "sm_fa_cvt": dict(table="la_force_aircraft", where=("class", "Combined vectored thrust"),
                      col="out of force share", fmt="pct"),
    "sm_fa_mr": dict(table="la_force_aircraft", where=("class", "Multirotor"),
                     col="out of force share", fmt="pct"),
    "sm_fa_p": dict(table="la_force_aircraft_test",
                    where=("reading", "every linked patent INACTIVE (this reading)"),
                    col="p", fmt="3f"),
    "sm_fa_classes": dict(table="la_force_aircraft_test",
                          where=("reading", "every linked patent INACTIVE (this reading)"),
                          col="classes tested", fmt="int"),
    "sm_fa_p_sens": dict(table="la_force_aircraft_test",
                         where=("reading", "every linked patent INACTIVE, multi-target "
                                           "duplicates to first target only"),
                         col="p", fmt="3f"),
    # C8/C10: the multiples of Figure 1 (ii), sm_open.la_baseline_multiples
    "sm_mult_b64_2018": dict(table="la_baseline_multiples", where=("priority year", "2018"),
                             col="vs aeronautics (B64)", fmt="1f"),
    "sm_mult_secb_2018": dict(table="la_baseline_multiples", where=("priority year", "2018"),
                              col="vs section B", fmt="1f"),
    "sm_mult_all_2018": dict(table="la_baseline_multiples", where=("priority year", "2018"),
                             col="vs all patents", fmt="1f"),
})

FIGURE_CAPTIONS.update({
    "sm_force_aircraft": "unique aircraft with no patent left in force, per architecture class, "
                         "priority year 2019 or earlier",
})

NOT_CORE.update({
    "ari_clock": "the evidence behind the chapter's lead over first flight; the Answer quoted it "
                 "without showing it (author's review, 2026-09-26)",
    "la_ari_timeline": "the firm-by-firm dates the ari_clock takeaway rests on, printed at the "
                       "author's request (2026-09-27, F12)",
    "sm_force_aircraft": "the per-aircraft reading of out of force the author ruled on "
                         "2026-09-26; it replaces the primary-patent figure",
})

TAKEAWAY.update({
    # 2026-09-26, chapter-1 review — every one of these says what its item shows and nothing
    # the Method block already said
    "filings_per_year":
        "(i) Filing takes off in 2016 and then holds: unique aircraft per priority year rise from "
        "{tk_y2015} in 2015 to {tk_y2018} in 2018, against {sm_pat_2018} acquired patents that "
        "year, because the large filers filed several patents on the same unique aircraft, and stay near "
        "that level to 2022. The fall at the right edge is the publication lag, not a decline. "
        "The steep rise of 2017-18 follows the Uber Elevate white paper of late 2016, a "
        "coincidence in time, not a proven cause. "
        "(ii) eVTOL is the fastest-growing series: its patent families double every "
        "{sm_g_fam_dbl} years, against {sm_g_b64_dbl} "
        "for aeronautics, {sm_g_secb_dbl} for transport and {sm_g_all_dbl} for all patenting. "
        "Counted in families, the baselines' own unit, eVTOL grows {sm_gr_fam_b64} times as fast "
        "as aeronautics ({sm_gr_fam_b64_ci}), {sm_gr_fam_secb} times as fast as transport and "
        "{sm_gr_fam_all} times as fast as all patenting. The lead over aeronautics is small and "
        "rests partly on the latest years: ending the fit at 2019 gives {sm_gr_fam_b64_19} "
        "({sm_gr_fam_b64_19_ci}), an interval that takes in 1. Counted as unique aircraft, eVTOL "
        "doubles every {sm_g_ac_dbl} years — almost the same rate as its families",
    "ari_clock":
        "{sm_ff_before} of the {sm_ff_flown} firms with a first flight on record filed their first "
        "patent in this corpus before flying, a median of {sm_ff_lead} years earlier; for the other "
        "{sm_ff_neg} the first flight comes first, which only means their earliest filing is not "
        "in this corpus. {sm_ff_planned} firm's first flight is still a plan and is not counted. "
        "Planned entry into service sits a median of {sm_ff_eis} years after the first patent. "
        "The dates behind these figures, firm by firm, are in {sm_here_la_ari_timeline}",
    "sm_force_aircraft":
        "{sm_fa_share} of the {sm_fa_n} aircraft with a priority year of 2019 or earlier have no "
        "patent left in force ({sm_fa_out} aircraft); reading each aircraft's first patent alone "
        "gave {sm_fa_old}. CVT ({sm_fa_cvt}) and Lift + Cruise ({sm_fa_slc}) have lost more of "
        "their aircraft than Tilt Rotor ({sm_fa_tr}) and Multirotor ({sm_fa_mr}), but whether the "
        "classes really differ depends on one counting choice: chi-square p {sm_fa_p} over the "
        "{sm_fa_classes} classes with ten or more aircraft when a duplicate patent counts for "
        "every aircraft it names, p {sm_fa_p_sens} when it counts for the first only (one 2004 "
        "family names four Multirotor aircraft). No class difference is claimed, then",
    "la_name_coverage":
        "{sm_nc_named} aircraft carry a real product name and {sm_nc_gen} a name generated for "
        "this study; {sm_nc_gen_matched} of the generated ones could be matched to a public "
        "aircraft. Every comparison with the public aircraft that follows therefore speaks for "
        "the named aircraft, which over-represent publicly documented firms, and not for the "
        "record as a whole",
    "a2_d15_trl_by_class":
        "{trl_above_s} of {trl_aircraft_s} aircraft ({sm_trl_share}) are above TRL 2 — the record "
        "is overwhelmingly aircraft that exist only on paper. The aircraft that did get built "
        "come from the classes that are patented most: Lift + Cruise ({sm_trl_lc_n}) and Tilt "
        "Rotor ({sm_trl_tr_n}) hold most of them. Among the classes with twenty or more aircraft, "
        "{trl_best_class} has the largest share built ({trl_best_share}); no aircraft of "
        "{trl_zero_classes} in this dataset is above TRL 2",
    "la_trl_representativeness":
        "The {trl_above_s} aircraft above TRL 2 differ from the other {sm_trl_rest_n} on "
        "{sm_trl_repr_fail} of the six attributes — filer type, priority window, priority year "
        "and propulsive units: they are company-backed, more recent and carry more propulsive "
        "units. No difference is detected on architecture class or region, so they can say "
        "which classes get built and cannot stand for the corpus on anything else",
    "la_ari_representativeness":
        "The {tk_ari_in} aircraft of the index firms differ from the other {tk_ari_rest} on "
        "{sm_ari_repr_fail} of the six attributes — applicant region, priority window, filer type "
        "and propulsive units: more North American, more company-backed, more often filed in "
        "2016-19 and with more propulsive units. No difference is detected on architecture class "
        "or priority year. The firms the market rates are a distinct group of the record, not a "
        "sample of it",
})

SM_ANSWER["1"] = (
    "**The record grows faster than patenting at large and a little faster than aeronautics, "
    "and shows a design before it flies; it can be checked against the aircraft the sector "
    "builds only for its {sm_nc_named} named aircraft, and those are not a sample of it.**\n\n"
    "- **eVTOL patenting grows faster than patenting at large, and a little faster than "
    "aeronautics.** Its patent families double every {sm_g_fam_dbl} years, against "
    "{sm_g_b64_dbl} for aeronautics, {sm_g_secb_dbl} for transport and {sm_g_all_dbl} for all "
    "patents: {sm_gr_fam_b64} times as fast as aeronautics ({sm_gr_fam_b64_ci}) and "
    "{sm_gr_fam_all} times as fast as all patenting. The edge over aeronautics is small: ending "
    "the fit at 2019, it can no longer be told apart from 1.\n"
    "- **A design becomes public about {sm_ff_visible} year before it flies.** A patent is "
    "published up to {lag_p90} years after its priority date (90th percentile), so a priority "
    "year can only be read {lag_p90} years later — which is why every trend here stops at 2023. "
    "Firms file a median of {sm_ff_lead} years before their first flight ({sm_ff_before} of "
    "{sm_ff_flown} index firms with a flight on record); once publication is paid, about "
    "{sm_ff_visible} year of that lead is left.\n"
    "- **{sm_fa_share} of the aircraft filed in 2019 or earlier have no patent left in force.** "
    "An aircraft counts as out of force only when every patent that describes it is inactive. "
    "CVT and Lift + Cruise have lost more of their aircraft than Tilt Rotor and Multirotor, but "
    "the difference passes the 0.05 line under one way of counting duplicate patents "
    "(p {sm_fa_p}) and not under the other (p {sm_fa_p_sens}), so no class difference is "
    "claimed.\n"
    "- **Where an aircraft can be checked, the drawing gives the built aircraft's architecture "
    "class {tk_pw_share} of the time** ({sm_pw_img_pub} of {sm_pw_n}; 95 % interval "
    "{sm_pw_ci}); most disagreements are a patent that describes another configuration than "
    "the one the firm built. Only an aircraft with a real product name can be checked — "
    "{sm_nc_named} of {unique_s}, none of the {sm_nc_gen} with a generated name.\n"
    "- **The aircraft that public sources cover do not stand for the record.** Only "
    "{sm_trl_share} of the aircraft are above TRL 2, and they come from the classes patented "
    "most. Both they and the aircraft of the firms the AAM Reality Index rates differ from the "
    "rest in filer type, priority window and propulsive units, and neither differs detectably "
    "in architecture class. A comparison with the built sector therefore speaks for "
    "company-backed, recent aircraft with many propulsive units, not for the whole record.\n"
    "- **External comparison.** Filings (unique aircraft per priority year) climb sharply from "
    "2016, reach their high range by 2018 and stay there, with a dip in 2019, until 2021. "
    "Disclosed eVTOL investment was only about "
    "{sm_ext_fund_1020} billion US dollars over the whole of 2010-2020 (Vertical Flight "
    "Society), rising to about {sm_ext_fund_2021} billion in 2021 alone (McKinsey) and falling "
    "back to {sm_ext_fund_2023} billion in 2023: filing ran ahead of the money by a few years, "
    "and after 2021 both fall, though part of the filing drop is the publication lag already "
    "described above, not a real slowdown. This is a reading of a few points on two short "
    "series, not a test. For scale only: {sm_ext_fc_n} published reports put the eVTOL aircraft "
    "market between {sm_ext_fc_min} and {sm_ext_fc_max} billion US dollars by 2034, at growth "
    "rates between {sm_ext_fc_cagr_min} % and {sm_ext_fc_cagr_max} % a year; the spread is too "
    "wide to validate anything, and the reports forecast revenue, not design."
)

NOT_CORE.update({
    "proximity_region": "the evidence for the chapter-4 null on firm-level design proximity, "
                        "brought in so the brief no longer points out of itself (2026-09-26)",
})

# 2026-09-27: the chapter-1 "External comparison" (author's request) -- disclosed investment
# by period and the published market-size forecasts, both collected in
# assets/external/investment/ and built into tables by sm_open.external_tables.
NUMBERS.update({
    "sm_ext_fund_1020": dict(table="la_ext_funding", where=("period", "2010-2020"),
                             col="funding_usd_bn", fmt="1f"),
    "sm_ext_fund_2021": dict(table="la_ext_funding", where=("period", "2021"),
                             col="funding_usd_bn", fmt="1f"),
    "sm_ext_fund_2023": dict(table="la_ext_funding", where=("period", "2023"),
                             col="funding_usd_bn", fmt="1f"),
    "sm_ext_fc_n": dict(table="la_ext_forecast_range", col="reports", fmt="int"),
    "sm_ext_fc_min": dict(table="la_ext_forecast_range", col="min value 2034 (US$ bn)", fmt="1f"),
    "sm_ext_fc_max": dict(table="la_ext_forecast_range", col="max value 2034 (US$ bn)", fmt="1f"),
    "sm_ext_fc_cagr_min": dict(table="la_ext_forecast_range", col="min CAGR (%)", fmt="1f"),
    "sm_ext_fc_cagr_max": dict(table="la_ext_forecast_range", col="max CAGR (%)", fmt="1f"),
})

#: read by ``report._table_md``: a truncated table says so without pointing to a file
ROW_NOTE_POINTS_OUT = False

#: the firm table fits whole (17 rows), so it is printed whole
ROW_CAP["la_ip_strategy"] = 20

NUMBERS.update({
    # 2026-09-26: Figure 1 (ii) as growth rates (sm_open.growth_rates / growth_ratios)
    "sm_g_fam_dbl": dict(table="la_growth_rates", where=[("key", "evtol_families"), ("window", "2005–2023")], col="doubling time (years)", fmt="1f"),
    "sm_g_ac_dbl": dict(table="la_growth_rates", where=[("key", "evtol_aircraft"), ("window", "2005–2023")], col="doubling time (years)", fmt="1f"),
    "sm_g_b64_dbl": dict(table="la_growth_rates", where=[("key", "b64"), ("window", "2005–2023")], col="doubling time (years)", fmt="1f"),
    "sm_g_secb_dbl": dict(table="la_growth_rates", where=[("key", "secb"), ("window", "2005–2023")], col="doubling time (years)", fmt="1f"),
    "sm_g_all_dbl": dict(table="la_growth_rates", where=[("key", "all"), ("window", "2005–2023")], col="doubling time (years)", fmt="1f"),
    "sm_gr_fam_b64": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2023")], col="times as fast", fmt="2f"),
    "sm_gr_fam_b64_ci": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2023")], col="95 % interval", fmt="raw"),
    "sm_gr_fam_secb": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "transport and operations (CPC section B)"), ("window", "2005–2023")], col="times as fast", fmt="2f"),
    "sm_gr_fam_all": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "all patents"), ("window", "2005–2023")], col="times as fast", fmt="2f"),
    "sm_gr_fam_b64_19": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2019")], col="times as fast", fmt="2f"),
    "sm_gr_fam_b64_19_ci": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL patent families"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2019")], col="95 % interval", fmt="raw"),
    "sm_gr_ac_b64": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL unique aircraft"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2023")], col="times as fast", fmt="2f"),
    "sm_gr_ac_b64_ci": dict(table="la_growth_ratios", where=[("eVTOL counted as", "eVTOL unique aircraft"), ("against", "aeronautics (CPC B64)"), ("window", "2005–2023")], col="95 % interval", fmt="raw"),
})

FIGURE_CAPTIONS["filings_per_year"] = (
    "unique aircraft, counted once, by the priority year of their first patent (later patents "
    "on the same aircraft are not counted again), per year and applicant region, with the "
    "acquired patents as a line and the dated sector events under the bars. Then how fast each "
    "series grows: eVTOL patent families, eVTOL unique aircraft and three worldwide baselines, "
    "each relative to its own 2005-09 average on a log axis, with its fitted line over "
    "2005-2023")

NOT_CORE.update({
    "sm_evtolnews_check": "the external check of the class shares against the evtol.news "
                          "directory the author built (2026-09-26, C44)",
})


# ---------------------------------------------------------------------------
# 2026-09-26 — chapter modules. Each reviewed chapter keeps its prose in its own module,
# ``sm_text_ch<N>.py``, so several helpers can write chapters at once without touching this
# file (BRIEF_REVISION_RULES.md §5). A module may define any of these, all optional:
#   CHAPTER    "2"                              the chapter it owns (added to METHOD_RESULTS)
#   METHOD     {"2.q1": md, …}                  the Method block of each sub-question
#   RESULTS    {"2.1": md, …}                   prose under "Results and discussion" ("" = none)
#   ITEMS      {"2.1": dict(figures=[…], tables=[…]), …}   replaces the node's items, in order
#   CHAPTER_TEXT  md                            printed under the chapter heading
#   ANSWER     md                               the chapter's Answer box
#   TAKEAWAY, NUMBERS, FIGURE_CAPTIONS, TABLE_CAPTIONS, COLUMNS, NOT_CORE   dict updates
#   NO_TAKEAWAY  set
#   AFTER      {node id: md}                    printed under a node's items
# Node ids of the five-chapter layout: 2.1 (Q4) · 2.2 (arch) · 2.3 (space) · 3.1 (Q2) ·
# 3.2 (Q3) · 3.3 (inclass) · 3.4 (drivers; children 3.4.obs, 3.4.answer).
# ---------------------------------------------------------------------------
EXCLUDE_NODES = {"M"}
CHAPTER_MODULES = ("sm_text_ch2", "sm_text_ch3", "sm_text_ch3b",   # ch3: 3.1-3.2 | 3.3-3.4
                   "sm_text_ch4", "sm_text_ch5")
#   MERGE      {node id: into node id}          the node's items join the target's, the node goes
#   TABLES_FIRST  {node id, …}                  nodes whose tables print before their figures
TABLES_FIRST: set = set()
#   PRINT      {table name: fn(frame) -> frame}  print-only formatting, applied after print_format
#   NUMBER_FUNCS  [fn(tables, values) -> dict]    numbers the spec grammar cannot say
PRINT_HOOKS: Dict = {}
NUMBER_FUNCS: List = []


def _apply_chapter_module(mod) -> None:
    ch = getattr(mod, "CHAPTER", None)
    if ch:
        METHOD_RESULTS.add(ch)
    TEXTS.update(getattr(mod, "METHOD", {}) or {})
    for nid, md in (getattr(mod, "RESULTS", {}) or {}).items():
        node(nid)["text"] = md
    for src, dst in (getattr(mod, "MERGE", {}) or {}).items():   # 2026-09-26
        s_node, d_node = node(src), node(dst)
        for key in ("figures", "tables"):
            d_node[key] = list(d_node.get(key) or []) + [x for x in (s_node.get(key) or [])
                                                          if x not in (d_node.get(key) or [])]
        NODES[:] = [n for n in NODES if n["id"] != src and not n["id"].startswith(src + ".")]
    for nid, items in (getattr(mod, "ITEMS", {}) or {}).items():
        n = node(nid)
        for key in ("figures", "tables"):
            if key in items:
                n[key] = list(items[key])
    if getattr(mod, "CHAPTER_TEXT", None) and ch:
        CHAPTER_METHOD[ch] = mod.CHAPTER_TEXT
    if getattr(mod, "ANSWER", None) and ch:
        SM_ANSWER[ch] = mod.ANSWER
    for reg, name in ((TAKEAWAY, "TAKEAWAY"), (NUMBERS, "NUMBERS"),
                      (FIGURE_CAPTIONS, "FIGURE_CAPTIONS"), (TABLE_CAPTIONS, "TABLE_CAPTIONS"),
                      (COLUMNS, "COLUMNS"), (NOT_CORE, "NOT_CORE"), (AFTER, "AFTER")):
        reg.update(getattr(mod, name, {}) or {})
    NO_TAKEAWAY.update(getattr(mod, "NO_TAKEAWAY", set()) or set())
    PRINT_HOOKS.update(getattr(mod, "PRINT", {}) or {})
    TABLES_FIRST.update(getattr(mod, "TABLES_FIRST", set()) or set())
    NUMBER_FUNCS.extend(getattr(mod, "NUMBER_FUNCS", []) or [])


def _load_chapter_modules() -> None:
    import importlib
    for name in CHAPTER_MODULES:
        try:
            mod = importlib.import_module(f"{__package__}.{name}")
        except ModuleNotFoundError as e:
            if e.name and e.name.endswith(name):
                continue                     # that chapter has not been written yet
            raise
        _apply_chapter_module(mod)
        # 2026-09-26: a module may hand the chapter Answer one more bullet (3.3-3.4 → chapter 3)
        bullet = getattr(mod, "ANSWER_BULLET", None)
        if bullet:
            for ch, ans in list(SM_ANSWER.items()):
                if "bullet: to be added]" in ans:
                    lines = [ln for ln in ans.split("\n") if "bullet: to be added]" not in ln]
                    SM_ANSWER[ch] = "\n".join(lines).rstrip() + "\n" + bullet.strip()
    # 2026-09-27, author: chapter M (the figure against the text) is left for later
    NODES[:] = [n for n in NODES if n["id"] not in EXCLUDE_NODES
                and n["id"].split(".")[0] not in EXCLUDE_NODES]
    # items may have moved: renumber, and recompute which chapter each item sits in
    _number_items()
    _here_refs()
    ITEM_CHAPTER.clear()
    ITEM_CHAPTER.update(_item_chapter())


_load_chapter_modules()

#: read by ``report.write_markdown`` (2026-09-26): a sub-question whose Method is long binds only
#: its heading and the first block of the Method to the page, so a one-page Method no longer
#: pushes itself whole to the next page and leaves the one before it empty
KEEP_HEAD_ONLY = {n["id"] for n in NODES
                  if n.get("subq") and n["id"].split(".")[0] in METHOD_RESULTS}


# ---------------------------------------------------------------------------
# 2026-09-27, author: "you just added a lot of text, no one wants to read that". Chapter 1's
# Methods keep the five labelled parts (BRIEF_REVISION_RULES §7) at one or two sentences each;
# the statistics box is the short one. Everything the author asked for stays, said once.
# ---------------------------------------------------------------------------
CHAPTER_METHOD["1"] = (
    "#### Method common to every chapter\n\n"
    "**Unit of analysis.** {acquired_s} patents were acquired (PatSeer, snapshot {snapshot}); "
    "{representative_s} describe an electric VTOL aircraft readable from its drawings, and "
    "those describe **{unique_s} unique aircraft**. A unique aircraft is one design: a firm "
    "that files it five times has one aircraft, and an aircraft shown in several patents "
    "({observations_s} such observations) is counted once. Most analyses count unique "
    "aircraft; each Method names its own unit.\n\n"
    "**Time is the priority year**, the earliest filing date of the family, when the design "
    "existed. Publication follows a median of {lag_median_lo} to {lag_median_hi} years later, "
    "and {lag_p90} years at the 90th percentile, so priority years from {partial_start} on are "
    "still filling, are hatched in every figure, and no trend is read past 2023. From the "
    "corpus's own publication delays, the snapshot already sees {sm_vis2023_lo} to "
    "{sm_vis2023_hi} of each region's 2023 aircraft.\n\n"
    + _methods_text.STATS_BOX_SHORT.strip() + "\n")

TEXTS["1.q1"] = (
    "#### Method\n\n"
    "**Objective.** How fast eVTOL patenting has grown against patenting at large, and how "
    "many years before its first flight a design appears in the record.\n\n"
    "**Data and unit of analysis.** {sm_here_filings_per_year} (i) counts unique aircraft, "
    "each once, by the priority year of its first patent. The acquired patents are drawn "
    "beside them because the gap is repeated filing: {sm_pat_2018} patents for {tk_y2018} "
    "aircraft in 2018. {sm_here_filings_per_year} (ii) counts patent families "
    "({representative_s}), the unit of the three worldwide baselines. {sm_here_ari_clock} and "
    "{sm_here_la_ari_timeline} count firms: the {tk_ari_timeline_n} firms that the AAM Reality "
    "Index, an analyst's quarterly rating of eVTOL makers (May 2026), lists and that file "
    "here. Sources: PatSeer, WIPO, the AAM Reality Index, human labelling.\n\n"
    "**Procedure.** Each growth series is divided by its own 2005-09 average and drawn on a "
    "log axis, where a steeper line means faster growth. The lead is the years from a firm's "
    "first patent here to its first flight.\n\n"
    "**Scientific grounds.** log(count_t) = a + b·t is fitted by least squares over 2005-2023, "
    "and the doubling time is ln 2 / b. Two series are compared by the ratio of their "
    "doubling times; its interval comes from resampling the years 2 000 times and refitting "
    "(bootstrap, Efron 1979). An interval that takes in 1 means the two rates cannot be told "
    "apart.\n\n"
    "**Assumptions and limits.** The lead is a floor, since a firm may have filed earlier "
    "elsewhere. The sector events marked on {sm_here_filings_per_year} (i) are context, not "
    "causes.\n")

TEXTS["1.q2"] = (
    "#### Method\n\n"
    "**Objective.** What share of the aircraft is still protected, and whether it differs "
    "between architecture classes. It matters because a class whose patents lapse faster may "
    "be a class firms are giving up, which bears on the dominant-design question of chapter "
    "3.\n\n"
    "**Data and unit of analysis.** Unique aircraft with a priority year of 2019 or earlier. "
    "An aircraft is out of force when every one of its patents reads INACTIVE in PatSeer "
    "(lapsed, withdrawn, refused or expired); one live patent keeps it in force. The cut is "
    "2019 because {sm_lapse_7y} of the {sm_lapse_grants} dated grants arrive within seven "
    "years of priority, while {sm_lapse_p2023} of 2023 families are still under examination "
    "(published, but neither granted nor refused). Aircraft filed after 2019 are left out "
    "because most have not yet been decided, so they would count as protected only because no "
    "decision exists yet.\n\n"
    "**Procedure.** {sm_here_sm_force_aircraft} gives the share out of force per class.\n\n"
    "**Scientific grounds.** A chi-square test of class against out of force (statistics "
    "box), run twice because one duplicate patent can name several aircraft: counting it for "
    "all of them, and for the first only.\n\n"
    "**Assumptions and limits.** Legal status is a snapshot: it says whether an aircraft has "
    "lapsed, not when. Out of force refers only to the patents in this dataset: a design could "
    "still be protected by a patent outside it, although that is not expected, and for the "
    "question asked here, whether the record's own patents are let go, this is the relevant "
    "reading.\n")

TEXTS["1.q3"] = (
    "#### Method\n\n"
    "**Objective.** Whether the patent drawings describe the aircraft that get built, and "
    "whether the aircraft public sources cover stand for the rest of the record.\n\n"
    "**Data and unit of analysis.** Unique aircraft that can be linked to an outside source. "
    "Only an aircraft with a real product name can be matched to its evtol.news page "
    "({sm_here_la_name_coverage}); the others carry a name generated for this study. TRL, "
    "NASA's Technology Readiness Level (1-2 on paper, 3-5 components tested, 6-7 full-size "
    "prototype flown, 8-9 certified), was assessed per aircraft from public evidence "
    "(evtolindex.org, evtol.news, company statements); an aircraft no public source follows is "
    "set at TRL 2, since its patent is itself an idea on paper.\n\n"
    "**Procedure.** {sm_here_la_public_pairwise} compares the label's architecture class with "
    "the public aircraft's class and with the class the patent text states, two at a time. "
    "{sm_here_a2_d15_trl_by_class} reads TRL per class. {sm_here_la_trl_representativeness} "
    "and {sm_here_la_ari_representativeness} compare the aircraft above TRL 2, and those of "
    "the {tk_ari_firms_n} index firms, with the rest on six attributes.\n\n"
    "**Scientific grounds.** {sm_pw_img_pub} of {sm_pw_n} is a sample, not the whole record; "
    "each agreement share therefore comes with a 95 % interval, which says how sure that share "
    "is of holding for the aircraft not matched (Wilson interval, statistics box). The six "
    "attributes use "
    "chi-square for the categories (class, region, window, filer type) and Mann-Whitney for "
    "the numbers (priority year, propulsive units); see the statistics box.\n\n"
    "**Assumptions and limits.** The matched aircraft are not a random sample: most come from "
    "firms with a public product. Their interval therefore says how precise the count is, not "
    "how well the whole record matches the built aircraft. TRL above 2 is a floor. The TRL "
    "values and the development years of the evtol.news aircraft were extracted by a language "
    "model from public pages and have not yet been checked by hand; they will be checked if "
    "the results that rest on them are kept.\n")


# 2026-09-27 (author, G5, G7): Table 1 without its total row; Table 5 says where its firms come from
def _no_total_row(t):
    if "aircraft" in t.columns:
        t = t[~t["aircraft"].astype(str).str.startswith("all unique aircraft")]
    return t


def _ari_repr_header(t):
    return t.rename(columns={"n index firms": "n aircraft of AAM Reality Index firms"})


PRINT_HOOKS["la_name_coverage"] = _no_total_row
PRINT_HOOKS["la_ari_representativeness"] = _ari_repr_header
