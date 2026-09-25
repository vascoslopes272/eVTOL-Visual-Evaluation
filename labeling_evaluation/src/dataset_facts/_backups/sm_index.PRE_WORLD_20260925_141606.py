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

TITLE = ("Labelling Analysis in brief — four questions about the eVTOL patent record, "
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
    dict(id="Q1",
         text="**The unit, stated once for the whole document.** {acquired_s} patents were acquired "
              "(PatSeer, snapshot {snapshot}); {representative_s} describe an electric VTOL aircraft "
              "readable from its drawings; those describe **{unique_s} unique aircraft**, and the "
              "unique aircraft is the row everywhere below. Not the patent, because a firm that files "
              "the same design five times has one design, and the questions here are about designs; "
              "the patents are drawn as a line beside the bars so the difference is visible. Not the "
              "{observations_s} aircraft observations, because an observation is one drawing in one "
              "patent and the same aircraft recurs across filings. The classes are those of Appendix D "
              "of `LABELLING_ANALYSIS.pdf`.\n\n"
              "**Time is the priority year** — the earliest filing date of the family, which is when "
              "the design existed. Publication follows {lag_p90} years later at the 90th percentile, "
              "so priority years from {partial_start} on are still filling at the snapshot, are "
              "hatched in every figure, and no trend claim reaches past 2023.\n\n"
              "**2018** holds {tk_y2018} aircraft against {sm_pat_2018} patents: the large filers of "
              "that year filed several patents on each design — the gap between the two is exactly "
              "what counting aircraft removes.\n\n"
              "**The record is growing about twice as fast as the aeronautics it sits inside.** "
              "Fitted on the complete years, eVTOL aircraft double every {sm_dbl_evtol} years "
              "({sm_dbl_evtol_ci}); the aeronautics baseline — CPC B64 filings **at the same nine "
              "offices this corpus is drawn from**, never aeronautics worldwide — doubles every "
              "{sm_dbl_b64} years ({sm_dbl_b64_ci}). The ratio is {sm_dbl_ratio} "
              "({sm_dbl_ratio_ci}). Read the baseline figure with one caveat: the B64 series bends "
              "downward across the window while the eVTOL series does not, so {sm_dbl_b64} years is "
              "an average over the window and not a rate aeronautics held throughout. Cutting the "
              "fit at 2019 leaves eVTOL {sm_dbl_ratio_sens} times faster, so the conclusion does not "
              "rest on the last four years.",
         figures=["filings_per_year"]),
    # 2026-09-24: the lapse paragraph and its figure are their own section, under sub-question 1.2
    dict(id="Q1b",
         text="**Out of force** = the PatSeer legal status of the aircraft's primary patent reads "
              "INACTIVE at the snapshot — lapsed for non-payment, withdrawn, refused or expired. It "
              "is read on the {tk_lapsed_n} primary patents with priority **2019 or earlier**, and "
              "on no younger cohort, because a lapse needs about seven years from priority to show: "
              "18 months to publication, two to four years of examination, then the first renewal "
              "decisions. A 2022 patent that is 'alive' is alive because it is young. "
              "{tk_lapsed_all} of the cohort is out of force and the classes sit around that line "
              "(Tilt Rotor {tk_lapsed_tr}, Lift + Cruise {tk_lapsed_slc}, CVT {tk_lapsed_cvt}).",
         figures=["abandonment"]),

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
         figures=["atlas_arch_time"]),

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
              "head of this chapter."),
    dict(id="Q3.1", title="What a design is here: the archetype",
         tables=["la_archetype_levels"]),
    # 2026-09-24: the screens table and the conditions table are no longer printed — the two
    # paragraphs carry them, and the two tables cost a page each. Both stay in tables/.
    dict(id="Q3.2", title="Which level the test is run at"),
    dict(id="Q3.3", title="The three conditions, and the era they place the sector in",
         tables=["la_era_frame"]),
    dict(id="Q3.4", title="The result",
         figures=["dominant_design", "sm_weighting"],
         tables=["la_dd_result"]),
    dict(id="Q3.4b", title="Not one design, then: how many, and which",
         tables=["la_top_archetypes"]),
    dict(id="Q3.5", title="Inside a class, on the class's own labels",
         figures=["sm_class_configs"],
         tables=["la_class_configs_own"]),

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
         figures=["zones", "sm_archetype_filers", "atlas_units", "sm_duct_count"],
         tables=["a2_d3_selected_fields", "la_duct_count"]),

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
              "result, carried by {sm_ref_proximity_region} of the full document.",
         figures=["atlas_region", "region_grid"]),
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
    dict(id="Q8",
         text="**Where a public aircraft exists the label describes it; the record itself is a "
              "record of concepts.** {sm_pw_img_pub} of the {sm_pw_n} aircraft that can be matched to "
              "a public product carry its class ({tk_pw_share}; six of the rest are the directory's "
              "coarser vocabulary, not a different aircraft). **Read that agreement as a statement "
              "about those aircraft and not about the record.** The aircraft that can be matched "
              "are exactly the aircraft that carry a real product name; the rest carry a name "
              "generated for this study, and none of those could be matched, because matching "
              "required recognising the aircraft in the first place. The matched set is therefore "
              "not a sample of the corpus — it over-represents publicly documented firms. "
              "**TRL** is NASA's Technology "
              "Readiness Level, a 1-to-9 scale for how far a technology has got: 1-2 is an idea on "
              "paper, 3-5 is a component or a subscale rig tested, 6-7 is a full-size prototype "
              "flown, 8-9 is certified or in service. *Above TRL 2* therefore means the aircraft "
              "exists as more than a drawing. {trl_above_s} of {trl_aircraft_s} "
              "aircraft ({sm_trl_share}) are above TRL 2; {trl_zero_classes} have none. Those "
              "{trl_above_s} match the corpus on class and on region and NOT on filer type, priority "
              "year or propulsive units (table below), so every TRL statement describes the "
              "company-backed, recent, many-rotor part of the record and is a floor for the rest. "
              "The aircraft of the firms the market rates differ from everyone else's in citation "
              "rank and in survival, not in architecture class.",
         tables=["la_public_pairwise", "a2_d15_trl_by_class", "la_trl_representativeness",
                 "la_ari_representativeness", "la_ari_gap"]),

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
              "(Appendix B.2 of the full document) has not been run.",
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
    "Q2": ("2", 1, "What is gaining, and what is fading"),
    "Q3": ("2", 2, "The dominant-design test"),
    "Q4": ("2", 3, "What the design space is made of"),
    "drivers": ("2", 4, "Design drivers and their traces"),
    "Q5": ("3", 1, "Who files"),
    "Q7": ("3", 2, "Whether one firm carries the reading"),
    "entrants": ("3", 3, "What every class's entrants arrive with"),
    "Q6": ("4", 1, "Where it is designed, and whether region changes the design"),
    "Q6b": ("4", 2, "Whether region changes the timing"),
    "portfolio": ("4", 3, "How a firm builds its portfolio"),
}

# --------------------------------------------------------------------------
# 1c — the questions (2026-09-24, author's ruling: "only the important ones are questions,
# the rest are observations of that section")
# --------------------------------------------------------------------------
#: the chapter question, printed whole as the chapter heading. Overrides the wording of
#: ``la_index.QUESTIONS`` for THIS document only; the full document keeps its own.
SM_QUESTIONS = {
    "1": "How far ahead of the sector does the patent record run?",
    "2": "Is there a dominant eVTOL design or is the field still experimenting, and where has "
         "twenty years of filing moved the design space?",
    "3": "Who is patenting eVTOL aircraft, and which designs and filing strategies do firms of "
         "different maturity follow?",
    "4": "Does geography shape the design, or only its timing and its filing strategy?",
}

#: the sub-questions: (chapter, printed before the FOLD member with this order, number, wording).
#: Each is a heading of its own; the FOLD sections that follow it are its observations.
SUBQ = [
    ("1", 1, "1.1", "Do the patents come before the aircraft fly, and is that head start "
                    "getting longer?"),
    ("1", 2, "1.2", "Half the record is dead. Does dying tell us anything about the design?"),
    ("1", 3, "1.3", "Do the aircraft that fly look like the aircraft that were patented?"),
    ("2", 1, "2.1", "One winner, or three branches that refuse to merge?"),
    ("2", 3, "2.2", "Is the design space filling up, or still opening?"),
    ("2", 4, "2.3", "What forces a design to change — and is it one move dressed as four?"),
    ("3", 1, "3.1", "Does anyone hold enough of the record to steer it?"),
    ("3", 3, "3.2", "When the design mix moves, who moves it?"),
    ("4", 1, "4.1", "Regional design blocs — or a null the sector should hear?"),
    ("4", 2, "4.2", "Who moves first, who follows, and is the lag a constant?"),
    ("4", 3, "4.3", "Go deep or go wide: does a firm re-file one design, spread across classes, "
                    "or pass through one on the way to another?"),
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
    for chapter in ("1", "2", "3", "4"):
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
    # the post-hoc Lift + Cruise + CVT family, printed with the verdict table it fails
    "2.2.4": dict(figures=["sm_family"], tables=["la_family_dd"]),
    # the design space: the discovery curve that replaced the OPEN sticker, and the
    # all-or-nothing reading of ducting
    "2.3": dict(figures=["discovery_curve", "sm_duct_conditional"]),
    # the correction: tilting joints normalised by the propulsors they have to move
    "2.4": dict(figures=["sm_joints_per_unit"], tables=["la_joints_per_unit"]),
    # where the firms that leave Tilt Wing go
    "3.3": dict(tables=["la_tw_successions"]),
    # the test behind "the lead is real, the size of the gap is not settled"
    "4.2": dict(tables=["la_lag_constancy"]),
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
APPENDIX = ("new", "1", "2", "3", "4")

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
        "and the same measure sits inside {sm_here_atlas_units} with the rest of the "
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
        "the medians come from; the row itself is in {sm_here_la_ari_gap}.\n\n"
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
        "Fourteen questions were put to this record by the industry side of the project. **Seven "
        "are answered** in the chapters above: whether the sector is converging "
        "({sm_here_dominant_design}, {sm_here_la_dd_result}), which sub-variants stay open "
        "({sm_here_zones}, {sm_here_la_class_configs_own}), whether the field is concentrated "
        "({sm_here_coverage}, {sm_here_la_class_filer_weight}), whether propulsor counts settle on "
        "six to eight ({sm_here_atlas_units}), whether regions build differently "
        "({sm_here_atlas_region}, {sm_here_la_class_region_timing}) and whether patents track "
        "substance rather than press attention ({sm_here_la_ari_gap}). Two of those answer *no* to "
        "the question as it was asked, which is still an answer. The other seven are printed here "
        "with the reason, because a reader is owed the boundary of the instrument.\n\n"
        "| Question | Verdict | Why |\n"
        "|---|---|---|\n"
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
        "**Noise** and **wind or weather** were never labelled and are not stated in the patents; "
        "**battery specific energy** is external to the corpus and can only ever be context.\n\n"
        "**Not yet asked**, and reachable from the raw PatSeer export the analysis has never opened. "
        "Full CPC codes crossed with architecture class give the white-space map; the B64D27 family "
        "separates battery, hybrid and fuel cell in place of the yes/no powertrain field; the dated "
        "register status turns the alive/dead snapshot of Figure 2 into time-to-abandonment by class; "
        "the claims text gives claim breadth per architecture; and G05D1 with the B64U unmanned "
        "family is the only autonomy proxy this record will ever have — a weak one. Nothing on disk "
        "closes mission, payload, size, noise or certification: those need an external population and "
        "a different unit of analysis, which is another study, not an extension of this one.",
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
METHODS_CHAPTER = "2"

METHODS_BOX = (
    '<div class="methods-box">\n\n'
    "##### How to read the statistics\n\n"
    "*Written once, for the whole document; every later p, band or effective number points "
    "back here.*\n\n"
    "**p, and what it does not say.** Every test below asks one question: *if there were really "
    "no difference, how often would numbers like these turn up by chance alone?* That frequency "
    "is p. **p 0.03** means three times in a hundred — rare enough to say the pattern is real. "
    "**p 0.58** means fifty-eight times in a hundred — exactly what chance produces, so there is "
    "nothing there. The line used throughout this document is 0.05. A small p never says *why* "
    "something moved and never proves that one thing caused another; it says only that the "
    "pattern is larger than the noise around it.\n\n"
    "**The four tests, and the question each one answers.**\n\n"
    "- **Mann-Whitney U** — do two groups have the same middle value? (Do the aircraft above "
    "TRL 2 carry as many propulsors as the rest?)\n"
    "- **Fisher exact** — do two groups have the same share of a yes/no answer, when the counts "
    "are too small for anything coarser? (Is a ducted unit as common in one group as in the "
    "other?)\n"
    "- **Chi-square** — do two groups spread the same way over several categories at once? (Do "
    "the aircraft above TRL 2 spread over the twelve classes the way the rest of the corpus "
    "does?)\n"
    "- **Spearman ρ (rho)** — does a value rise or fall as the year advances? It runs from "
    "−1 (falls steadily) through 0 (no trend) to +1 (rises steadily), and it reads the ORDER of "
    "the values rather than their size, so one extreme aircraft cannot manufacture a trend.\n\n"
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
    "and averaged, so a large window cannot score higher merely by being large. The exact "
    "formula is `hill_numbers` in `la_tables.py`.\n\n"
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
                             "every aircraft are left out as uninformative; the full table is "
                             "Table B.4 of the full document",
    # Q3's premise. The archetype-levels caption is rewritten only because this document prints
    # the table without its "used in this document" column: the full document's caption ends on
    # "and where this document reads the level", which would describe a column that is not here.
    "la_archetype_levels": "Every archetype level the codebook can form: the dimensions it "
                           "combines, its largest archetype, how many archetypes the level "
                           "yields, how many aircraft end up alone in one, the effective number "
                           "of archetypes (Hill ¹D) and the share held by the largest. The "
                           "counting columns reproduce table 3.3.6 of the Preliminary Analysis; "
                           "which section reads which level is the last column of Table 1.1.3.1a "
                           "of the full document",
    "la_dd_result": "The dominant-design verdict, one line per condition (the observed result "
                    "behind each line is Table 1.1.3.3a of the full document)",
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
    "la_ari_timeline": "The patent clock against the market clock, firm by firm. Both market "
                       "dates are the index's own statements, and the years count from the "
                       "firm's first patent IN THIS CORPUS, so every figure is a floor",
    # the drivers section: the full caption spells out the test; here the object is named and the
    # test is in the unit-base-transform line of the full document
    "la_driver_verdicts": "The verdict table: one row per trace of the drivers table — what moved "
                          "(first reportable window → 2020-23, per class where it differs, with "
                          "Spearman ρ and p), and the verdict with the drivers that predict it. "
                          "Generated from the same frame as Figure 1.4.1 of the full document",
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
    "la_ari_timeline": ["company", "ARI score", "first patent", "last patent", "unique aircraft",
                        "first flight (ARI)", "years to first flight",
                        "years to entry into service", "region"],
    "a2_d15_trl_by_class": ["class", "unique aircraft", "TRL 2", "TRL 3-5", "TRL 6-7", "TRL 8-9",
                            "above TRL 2", "share above TRL 2"],
    "la_filers_by_window": _la.COLUMNS.get("la_filers_by_window"),
    # the drivers that predict a trace are named inside the verdict itself, so the separate
    # column and the driver-kind and where-drawn columns are left to the full document
    "la_driver_verdicts": ["trace", "importance", "what moved", "verdict",
                           "in the full document"],
    "la_duct_units": ["group", "aircraft", "with a ducted unit", "share ducted"],
    # 2026-09-24
    "la_class_configs_own": ["class", "rule", "aircraft", "distinct configurations",
                             "most common configuration", "share in it"],
    "la_trl_representativeness": ["attribute", "n above TRL 2", "n rest", "largest gap", "test", "p", "verdict"],
    "la_ari_representativeness": ["attribute", "n index firms", "n rest", "largest gap", "test", "p", "verdict"],
    "la_public_pairwise": ["comparison", "agree", "of", "share", "the disagreements"],
    "la_era_frame": ["measure", "era of ferment", "dominant design emerging", "incremental change", "this corpus"],
    "la_top_archetypes": ["level", "window", "aircraft", "top 1", "top 2", "top 3", "top 3 together", "top 5 together"],
    "la_duct_count": ["propulsive units", "aircraft", "with any ducted unit", "share with any",
                      "share of units ducted", "share ducting every unit",
                      "median ducted units (ducted aircraft)"],
}
COLUMNS = {k: v for k, v in COLUMNS.items() if v}


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
    # CPC B64 at the NINE CORPUS OFFICES, never worldwide; the label travels in the table's
    # own ``series`` cell and the prose states it.
    "sm_dbl_evtol": dict(table="la_doubling_time", fmt="1f", col="doubling time (years)",
                         where=[("series", "eVTOL aircraft (this corpus)"), ("primary", "True")]),
    "sm_dbl_evtol_ci": dict(table="la_doubling_time", col="95 % interval",
                            where=[("series", "eVTOL aircraft (this corpus)"), ("primary", "True")]),
    "sm_dbl_b64": dict(table="la_doubling_time", fmt="1f", col="doubling time (years)",
                       where=[("series", "aeronautics — CPC B64, nine corpus offices"),
                              ("primary", "True")]),
    "sm_dbl_b64_ci": dict(table="la_doubling_time", col="95 % interval",
                          where=[("series", "aeronautics — CPC B64, nine corpus offices"),
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
    pos = ff[ff > 0]
    return {"sm_ff_dated": f"{len(ff):d}",
            "sm_ff_before": f"{int((ff > 0).sum()):d}",
            "sm_ff_neg": f"{int((ff <= 0).sum()):d}",
            "sm_ff_lead": f"{pos.median():.0f}" if len(pos) else "",
            "sm_ff_eis": f"{eis.median():.0f}" if len(eis) else ""}

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
    out.update(_method_numbers())
    out.update(_driver_numbers(tables))
    out.update(_importance_numbers(tables))
    # cross-references, never typed: ``{sm_ref_<name>}`` is the item's number in the FULL
    # document at this render (``set_full_reference`` has already run), ``{sm_here_<name>}``
    # its number in this one. The full document was renumbered twice on 2026-09-23; a typed
    # number would already be wrong.
    for name, ref in FULL_REF.items():
        out[f"sm_ref_{name}"] = ref
    for name, ref in HERE_REF.items():
        out[f"sm_here_{name}"] = ref
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
    if node_id in _la.QUESTIONS:                     # Q1 … Q8, M — the wording comes from there
        return f"## {node_id} — {_question_title(node_id)}"
    title = _pa._fill(n.get("title", node_id), values)
    if n.get("subq"):                                # a sub-question: its own heading level
        return f"### {n['subq']} — {title}"
    if "." not in node_id:
        return f"## {title}"
    if node_id.count(".") == 1 and node_id.split(".")[0] in SM_QUESTIONS:
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
    "4.q2": ("PARTLY", "the regional lead is solid; whether the gap is the same size in every "
                       "class is not settled"),
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


def source(name, values=None, kind="figure", tables=None):
    return _la.source(name, values, kind, tables)


def unit(name, values=None, kind="figure", tables=None):
    return _la.unit(name, values or _VALUES, kind, tables or _TABLES)


def read(name, values=None, kind="figure", tables=None):
    return _la.read(name, values or _VALUES, kind, tables or _TABLES)


def why(name, values=None, kind="figure", tables=None):
    """Printed as ``Takeaway:`` — the slot the renderer calls ``why``."""
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

    "2":
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

    "3":
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

    "4":
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
        return _pa._fill(METHODS_BOX, values) if node_id == METHODS_CHAPTER else ""
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
