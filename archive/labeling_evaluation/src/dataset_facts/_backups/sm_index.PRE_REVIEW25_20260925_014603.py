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
              "what counting aircraft removes.",
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
              "Cruise rises from {tk_slc_w1} to {tk_slc_w4}; CVT stands at {tk_cvt_w4}. Shares are "
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
              "conditions with thresholds fixed in the Preliminary Analysis (5.7) before any curve of "
              "this corpus was drawn — so a 'no' is a finding and not a description. Their origin: "
              "the dominant-design literature (Abernathy and Utterback, 1978) asks whether one design "
              "takes most of a sector and keeps it; condition 1 is that question with a number on it, "
              "and conditions 2 and 3 are this thesis's own additions, because a sector can crowd "
              "under one archetype name without its aircraft becoming alike."),
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
              "exactly two stations. The fastest-growing archetype, CVT · 5-6, rests on "
              "{sm_cvt56_filers} filers for {sm_cvt56_air} aircraft — {sm_cvt56_fpa} per aircraft, the "
              "lowest of the {sm_zones_big_n} archetypes of {sm_zones_min}+ aircraft — so its rise is "
              "closer to one firm's line of variants than to a sector choice. Ducting is U-shaped in "
              "rotor count ({sm_duct_13} of aircraft at 1-3 units, {sm_duct_78} at 7-8, {sm_duct_9} "
              "at 9+); counted in units, the aircraft at nine and more that duct, duct nearly "
              "everything — {sm_duct9_units} of that band's units run in a duct, a median of "
              "{sm_duct9_med} per ducting aircraft — where at 1-3 units it is a single ducted fan. "
              "The two ends are two designs: a ducted-fan array, and a ducted cruise or tail unit.",
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
         text="**The regions do not run on one clock.** Every class is taken up first in North "
              "America, then Europe, then Asia-Pacific, with CVT the one exception "
              "({tk_crt_cvt_na} in North America, its latest cell). North America passes the middle "
              "of its own filings in 2018, Europe in 2019 and Asia-Pacific in 2020. Whether the lag "
              "is the same on every class, or closes on the newest ones, is read from the table.",
         tables=["la_class_region_timing"]),
    # 2026-09-24: how a firm files — depth against breadth — is sub-question 4.3, moved here from
    # the full document's 3.4 (both items core there)
    dict(id="portfolio",
         text="**Firms deepen; they do not explore.** A firm that files again usually files in the "
              "same class — 46 % of within-firm successions stay in class, and Tilt Wing is the one "
              "class firms pass through (16 % retention against 48-59 % for the others). Among the "
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
              "coarser vocabulary, not a different aircraft). {trl_above_s} of {trl_aircraft_s} "
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
    dict(id="drivers.obs", title="Four observations, each with the correlation behind it",
         text="**1 · Tilting joint groups — opposed drivers; the trace went with transition.** "
              "Inside Tilt Rotor the count rises (mean 1.4 → 1.8, ρ +0.22, p 0.009) and inside CVT it "
              "rises (1.0 → 1.4, ρ +0.27, p 0.006); Tilt Wing and Multirotor are flat, Lift + Cruise "
              "has none by definition. Regime transition (A1) predicts more joints, the two cost "
              "drivers (development and certification, maintenance) predict fewer. *Correlation:* the "
              "extra joint is almost never a tilting wing or boom — in Tilt Rotor the joints that are "
              "not a tilting propulsor set stay at 0.1–0.2 per aircraft in every window, and joints "
              "move with tilting sets (ρ 0.80). The rise is a **second tilting propulsor set** "
              "({sm_here_sm_driver_corr} i): the twin tilt-rotor (one wing, two proprotors) gives "
              "way to a fore-and-aft pair of tilting sets (canard + wing, or wing + tail: Maker v1, "
              "Nexus v6, Heaviside, Lilium Jet in 2020-23). *Possible reasons, in the order the record "
              "supports them:* (a) a fore-and-aft pair controls pitch in hover by differential thrust "
              "and removes the cyclic-pitch hub a twin tilt-rotor needs — the maintenance driver is "
              "answered by a simpler hub, not by fewer joints (hub mechanism is not labelled); (b) an "
              "electric nacelle is small enough that a tilt actuator per set is cheap, where a "
              "turboshaft tilt-rotor tilts one heavy gearbox per side; (c) a second set doubles the "
              "units for the same joints per set — the redundancy certification asks for. The "
              "drawings cannot tell the three apart.\n\n"
              "**2 · Propulsive units — overdetermined (three drivers), and the same move as 1.** The "
              "median rises in Tilt Rotor ({tk_dr_tr_units_first} → {tk_dr_tr_units_last}, ρ +0.40, "
              "p < 0.001) and CVT ({tk_dr_cvt_units_first} → {tk_dr_cvt_units_last}, ρ +0.32, "
              "p 0.001); Lift + Cruise is flat from {tk_dr_slc_units_first}, Tilt Wing flat at 4, "
              "Multirotor 4 → 6 does not reach p 0.05. Distributed propulsion (A1), failure tolerance "
              "(B) and community noise (B) all predict the rise. *Correlation:* in Tilt Rotor the unit "
              "count follows the number of tilting sets almost exactly — median 2 units with one set, "
              "4 with two, 6 with three ({sm_here_sm_driver_corr} ii; ρ 0.67) — so the unit rise "
              "and the joint rise are one event, the arrival of the multi-set tilt-rotor. In CVT the "
              "units travel with the boom layout (units on booms 25 % → 62 %). *Why the three drivers "
              "cannot be separated:* they predict the same sign, and the designs that would separate "
              "them are not in the corpus — a noise-driven design adds units at the same joint count "
              "and lowers tip speed (rotor diameter is not labelled), a redundancy-driven design adds "
              "units on the same station, distributed propulsion adds stations; the drawings show "
              "stations and sets added together. Electric share does not explain it: inside Tilt "
              "Rotor the median is 4 units for electric and hybrid aircraft alike, and the year term "
              "survives the electric control.\n\n"
              "**3 · A ducted unit — moved against its only driver, and the correlation explains it.** "
              "Inside CVT the share with a ducted unit falls {sm_dr_cvt_duct_first} → "
              "{sm_dr_cvt_duct_last} (ρ −0.22, p 0.03); community noise (B) predicts more ducting; "
              "every other class is flat. *Correlation ({sm_here_sm_driver_corr} iii):* split CVT by "
              "whether it carries units on booms and the fall disappears — CVT aircraft **without** "
              "booms duct 67 % → 75 %; those **with** booms duct 19 % over all years and 6 % in "
              "2020-23. Ducting against year with the boom layout held fixed is not significant "
              "(logit: booms p < 0.001, year p 0.21). The early CVT is a ducted fan buried in the "
              "fuselage or wing (6 of the 8 aircraft before 2012 duct a fuselage set); the late CVT is "
              "a Lift + Cruise-like layout of open rotors on booms with one tilting set added (Maker, "
              "Midnight). *Possible reasons:* a duct pays where the fan is short of diameter and "
              "buried in a body (static thrust augmentation, a guarded fan beside the cabin) and costs "
              "weight and cruise drag where the rotor sits free on a boom; and the noise requirement "
              "was met another way in the same years — more, smaller rotors (observation 2) — so the "
              "driver is not contradicted, it is served by a different trace. A regional composition "
              "effect is possible but weak (Europe ducts 56 % of its CVT, North America 33 %, "
              "Asia-Pacific 29 %).\n\n"
              "**4 · Propulsor types — moved against both cost drivers; what the types are.** A "
              "propulsor type is one set of like units on one station of the M3 record: lift rotors on "
              "the booms are one type, a cruise propeller on the tail a second, a tilting set on the "
              "wing a third. Development-and-certification and production cost (C) both predict fewer "
              "types. The mean rises in Tilt Rotor (1.4 → 1.8, ρ +0.23, p 0.006) and, pooled, "
              "1.9 → 2.3; Lift + Cruise sits at 2.6–2.7 (lift set + cruise set, often a third), CVT at "
              "2.2–2.8, Tilt Wing 1.5, Multirotor 1.8–1.9. *Correlation:* the type Tilt Rotor added is "
              "**not a fixed set** — tilt-rotors with any fixed set move only 9 % → 16 %, all of them "
              "on booms — it is the second tilting set of observation 1 (share with ≥ 2 tilting sets "
              "23 % → 59 %, {sm_here_sm_driver_corr} i). The tilt-rotor is not drifting toward CVT; "
              "it is becoming a multi-set tilt-rotor and stays in class. *Possible reason it moved "
              "against cost:* the type count is a poor proxy for cost when the added type is a copy of "
              "the first (same motor, rotor and actuator on a second station) — production cost falls "
              "with commonality, not with the type count, and the codebook cannot see commonality.",
         figures=["sm_driver_corr"]),
    dict(id="drivers.answer", title="Do tilting joints fall (cost) or rise (regime transition)?",
         text="They rise inside the "
              "classes that transition — Tilt Rotor and CVT, both p < 0.01 — and are flat in the corpus "
              "as a whole (pooled mean 0.8 → 0.9, p 0.58). The two readings sit at different levels, "
              "not in conflict. Inside a class, a firm that has accepted one tilting joint adds a "
              "second, because the second set buys hover pitch control without a cyclic hub, "
              "redundancy and units at once — observations 1, 2 and 4 are one move. Across classes, "
              "cost wins in the mix: the class that grows fastest, Lift + Cruise, has no joint at all, "
              "and that is where the entrants of 2020-23 arrive. The likely mechanism is selection, "
              "not conversion — the cost driver acts when a firm chooses its class, the transition "
              "driver acts once the class is chosen — and the record shows the two levels but not "
              "which one any firm weighed. Of the couplings the fixed physical drivers predict, one "
              "exists — empennage type against wing configuration (V {tk_dr_emp_wing_v}); the others "
              "are no stronger than a random pair."),

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
              "one class where firms keep arriving after the share has peaked, and the one class the "
              "firms then leave: within-firm successions stay in Tilt Wing 16 % of the time against "
              "48-59 % for the others.",
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
    "1": "Do patents see the eVTOL sector before it exists — or are they a graveyard of "
         "concepts that never flew?",
    "2": "Twenty years in, is there an eVTOL the way there is an airliner — or three rival "
         "answers and no winner?",
    "3": "Is eVTOL held by a few large firms, or open to anyone — and does the newcomer change "
         "what gets built?",
    "4": "Does geography shape the design — or only its timing and its filing strategy?",
}

#: the sub-questions: (chapter, printed before the FOLD member with this order, number, wording).
#: Each is a heading of its own; the FOLD sections that follow it are its observations.
SUBQ = [
    ("1", 1, "1.1", "How many years ahead of the runway is the drawing board, and is the gap "
                    "still widening?"),
    ("1", 2, "1.2", "Half the record is dead. Does dying tell us anything about the design?"),
    ("1", 3, "1.3", "Do the aircraft that fly look like the aircraft that were patented?"),
    ("2", 1, "2.1", "One winner, or three branches that refuse to merge?"),
    ("2", 3, "2.2", "Is the design space filling up, or still opening?"),
    ("2", 4, "2.3", "What forces a design to change — and is it one move dressed as four?"),
    ("3", 1, "3.1", "Is there a top tier, or a crowd of one-aircraft firms?"),
    ("3", 3, "3.2", "Do newcomers bring the shift, or do the firms already there change their "
                    "minds?"),
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
                if (n.get("figures") or n.get("tables")) and n["id"] not in PANEL_SECTIONS)


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
        "**Counts** — one archetype holds more than 50 % of a window's aircraft, in two "
        "consecutive complete windows. **Balance** — the window holds fewer designs in play than "
        "chance would give it: ²D is the number of equally common archetypes that would give the "
        "window's concentration (12 aircraft spread evenly over 4 archetypes = 4; the same 12 "
        "with 9 in one archetype ≈ 1.7); it is compared with the ²D obtained when the archetype "
        "labels are shuffled across windows, and the condition fires when the real value is below "
        "that band — more concentrated than the window's size alone explains. **Form** — the "
        "aircraft have become alike: the mean Gower distance between two aircraft of the window "
        "(0 identical, 1 nothing in common, over every labelled field) falls below the two earliest "
        "windows' level by more than the same shuffle gives. A dominant design needs all three in "
        "one complete window.\n\n"
        "*Two designs instead of one.* Condition 1 is written for one archetype; a duopoly would "
        "show as the top TWO archetypes holding more than 50 % together. The highest top-2 share "
        "in any window is {sm_top2}, at {sm_top2_level} in {sm_top2_window} — no duopoly either.\n\n"
        "*Both bands are year-shuffling permutation tests.* The labels of every aircraft are held "
        "fixed and its window (priority year) is reassigned at random, 200 times; condition 2 "
        "reads ²D and condition 3 reads Q on each shuffle, and the band is the middle 95 % of what "
        "the shuffles give. A real value outside the band is structure the years carry; a value "
        "inside it is what any split of this corpus into windows of these sizes would show.",

    "Q3.4":
        "**Condition 1 is not close**: the largest archetype of any window reaches {tk_dd_top_share} "
        "against 50 %. **Condition 2** fires in {tk_dd_below} of {tk_dd_cells} level-windows, all at "
        "A0c and only in the two earliest windows, the ones with the least data. **Condition 3** "
        "fires in {tk_q_below} of {tk_q_cells} cells, in 2020-23 and only under the subsystem "
        "weighting — under uniform weighting the same window stays inside its band (second figure), "
        "so the one signal the test finds is a choice of weighting, not a finding.",

    "Q3.4b":
        "**Three branches, not one design and not two — and they are the same three in every "
        "window.** At the design-species level (A1t) the one-wing Lift + Cruise, the one-wing Tilt "
        "Rotor and the one-wing Combined Vectored Thrust are the three largest archetypes of every "
        "complete window and hold about half of it together ({sm_top3_a1t_w1} in the earliest "
        "window, {sm_top3_a1t_w3} in 2016-19, {sm_top3_a1t_w4} in 2020-23); no one of them passes "
        "a quarter. The leadership inside the three changed once: Tilt Rotor led until 2016-19, "
        "Lift + Cruise leads since ({sm_top1_a1t_w4} in 2020-23). At the class level (A0) the same "
        "three classes hold {sm_top3_a0_w4} of 2020-23 — the sector has a stable set of three "
        "concepts, not a winner. One level down, at the rotor count (A0c), nothing holds: the "
        "three largest archetypes together are {sm_top3_a0c_w4} of 2020-23, and the largest is a "
        "different one in almost every window. So the branches are firm and what is inside each "
        "branch is still open — which is where the next figure looks.",

    "Q3.5":
        "The old configuration key (units · ducted · booms · tail) called every class diverse "
        "because it counted fields the class does not choose. Each class is now read on the labels "
        "that tell its OWN aircraft apart — the rules: Lift + Cruise, whether the lift units retract "
        "or fold, ducting, unit band; Tilt Rotor, one or more tilting types, ducting, unit band; "
        "CVT, how many types tilt against how many are fixed, unit band; Tilt Wing, one or more "
        "wings, ducting, unit band; Multirotor, booms, ducting, unit band. On those labels no class "
        "settles either: the most common configuration holds a fifth to a third of its class in "
        "2020-23, and a class of 50 aircraft still spreads over 14-20 configurations.",

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
        "**Noise** and **wind or weather**: not labelled, not stated in the patents. **Mission**: "
        "stated only for the 95 aircraft with an evtol.news page (14 %), majority-unspecified even "
        "there, and that subset fails the representativeness test on four of six attributes. "
        "**Battery specific energy**: external to the corpus; a Wh/kg series against the filing "
        "curve would be context, never a finding. **Regulation**: reaches the corpus only through "
        "examination outcome, which is an office effect (Chapter 1). What the corpus does carry on "
        "these themes is the number of propulsive units, the ducting count and the tail type, all "
        "in Chapter 2.\n\n"
        "**Not yet asked**, and answerable from the raw PatSeer export the analysis has not opened: "
        "the white space — full CPC codes crossed with architecture class; battery, hybrid and "
        "fuel cell from the B64D27 family, in place of the yes/no powertrain field; autonomy through "
        "G05D1 as the only proxy the record has; and the age at which a patent lapses, from the "
        "dated register status.",
}

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
    "la_top_archetypes": "The three largest archetypes of each window and what they hold together, "
                         "at the species level (A1t) and the class level (A0)",
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
    # the species level and the class level; the rotor-count level is in the CSV and in the text
    "la_top_archetypes": lambda t: t[t["level"].astype(str).isin(["A1t", "A0"])],
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
    "la_driver_verdicts": ["trace", "what moved", "verdict", "in the full document"],
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


def _la_q_weighting(k: int) -> str:
    """The k-th of the two weightings the dominant-design test is run under, named where the
    test names them (``la_tables.Q_WEIGHTINGS``) rather than spelled out here."""
    from . import la_tables as _ltb
    return _ltb.Q_WEIGHTINGS[k]


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
    "1.q1": ("OPEN", "the doubling time is not fitted: needs the full B64 series"),
    "2.q2": ("OPEN", "the discovery curve is not built; the answer rests on evenness alone"),
    "4.q2": ("OPEN", "\u2018is the lag a constant\u2019 is read off the table, not tested"),
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


def answer(question, values=None, tables=None):
    """The block that closes a chapter — the same words as the full document."""
    return _la.answer(question, values or _VALUES, tables or _TABLES)


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
        return ""
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
        "Three of the four are one move: the twin tilt-rotor becoming a fore-and-aft pair of tilting "
        "sets (two-set share 23 % → 59 %, units 2 → 4 → 6 with the set count). The fourth is a "
        "composition effect: CVT without booms ducts 67–75 % throughout; the boom-layout CVT that "
        "arrives after 2016 ducts 6 %.",
    "sm_duct_count":
        "At nine units and more the aircraft that duct, duct nearly everything: {sm_duct9_units} of "
        "the band's units run in a duct and the ducting aircraft carry a median of {sm_duct9_med} "
        "ducted units — a ducted-fan array, not a ducted unit. At 1-3 units the ducted aircraft "
        "carry two. The U-shape of the yes/no is two different designs at its two ends.",
    "sm_entry_all":
        "Lift + Cruise takes {tk_cm_e_slc} of the firms entering in 2020-23 against {tk_cm_a_slc} of "
        "the window's aircraft; Tilt Wing {sm_tw_ent_2023} against {sm_tw_air_2023}. Entrants "
        "over-index on their moment's class in every window that has enough of them; Tilt Wing is "
        "the one class where they keep arriving after the share has peaked.",
    "sm_class_configs":
        "On each class's own labels no class settles: the most common configuration holds a fifth "
        "to a third of its class in 2020-23, and the configurations per aircraft do not fall over "
        "time. The diversity is real, not an artefact of counting fields the class does not choose.",
    "la_class_configs_own":
        "The rules are printed so they can be attacked; on them, {top_class}'s {tk_slc_n_2023} "
        "aircraft of 2020-23 still spread over {sm_own_slc_configs} configurations.",
    "la_duct_count":
        "Share of units ducted: {sm_duct9_units} at 9+ against far less in every other band.",
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
        "Rotor, one-wing CVT hold {sm_top3_a1t_w4} of 2020-23 together and none passes a quarter; "
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
        "Both units give the same answer: named companies hold {tk_fm_named_air} of the "
        "{unique_s} aircraft ({tk_fm_named_share}) and {tk_fm_named_pat} of the primary patents, "
        "individual inventors {tk_fm_ind_air} aircraft. Per patent or per aircraft, most of the "
        "corpus belongs to an organisation — but to a great many small ones.",
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
        "{tk_dr_n_rows} traces, and {tk_dr_n_single} sharp statements about a moving driver: "
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
        "{tk_dr_slc_retract_mov}; tilting joints rise inside TR ({tk_dr_tr_joints_mov}) and CVT "
        "({tk_dr_cvt_joints_mov}) while the pooled row is {tk_dr_all_joints_mov}, because the "
        "class that grows has none — transition wins inside a class, cost wins in the mix.",
    # the full document's line names the two rows this document drops (symmetry, standard
    # wings); this one reads only what is printed
    "a2_d3_selected_fields":
        "The variety of this corpus lives in two fields: tail type (top answer {tk_emptype}) "
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
