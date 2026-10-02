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
  of this document without touching anything else.
* **One to three items per question**, graded ``core`` in :data:`la_index.GRADE` unless
  :data:`NOT_CORE` names the item and the reason. The answer is stated first, in prose; the
  items are the evidence under it, and the selection rule is enforced by the render script,
  not by eye. Q2 is the one question printed in four parts — unit, screens, conditions,
  result — because its answer is negative and a negative answer is a statement about a unit
  and a test, both of which have to be on the page before the verdict can be read.
* **The apparatus is lighter.** This module deliberately defines no ``provenance`` and no
  ``question`` accessor, so ``report._prov_md`` and ``report._quest_md`` return ``""`` and the
  unit·base·transform line and the per-item question line are simply not printed. The takeaway
  stays, and carries the item's number in the full document at its end, where the two dropped
  lines are printed in full.
* **Its own numbering.** Figures and tables are numbered in one running sequence, Figure 1,
  Figure 2, …, so a number here never collides with a number there, and a caption still starts
  with "Figure <digit>" — which is what the PDF stylesheet keys its caption rule on.

NOTHING IN THIS MODULE IS IMPORTED BY ``la_index`` OR BY ``index``, and ``report.py`` is not
changed by it: both existing documents render byte-for-byte as before.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import index as _pa
from . import la_index as _la

TITLE = ("Labelling Analysis in brief — eight questions about the eVTOL patent record, "
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
# and the grade that keeps the missing item out is quoted — see Q3, which has exactly one core
# item in the whole document.
NODES: List[Dict] = [
    dict(id="how", title="How to read this brief"),
    dict(id="data", title="The data set, in one paragraph"),
    dict(id="vocab", title="The vocabulary", figures=["codebook_classes"]),

    # ---------------------------------------------------------------- Q1
    # The answer is two or three sentences, never a page: everything else the corpus says about
    # this question is already printed on the items, in their takeaway lines.
    dict(id="Q1",
         text="**A wide space with a crowded middle, and the variety is in the propulsion, not "
              "in what tilts.** Twelve architecture classes are occupied, the largest — "
              "{top_class} — holds {sm_top_class_share} of the {unique_s} aircraft, and only two "
              "label fields are really spread: the tail, and the number of propulsive units, "
              "whose five bands hold {bin_r03}, {bin_r4}, {bin_r56}, {bin_r78} and {bin_r9} "
              "aircraft. Where the corpus does converge is on arrangement — {grp2} of {units_n} "
              "aircraft put their units on exactly two stations.",
         figures=["zones", "atlas_units"],
         tables=["a2_d3_selected_fields"]),

    # ---------------------------------------------------------------- Q2
    # The only question printed in four parts. Restored on the author's instruction of
    # 2026-09-23: this brief had kept the RESULT of the dominant-design test and dropped
    # everything the result is a statement about, so a reader was told there is no dominant
    # design without being told what a design IS in this corpus or what test it survived. The
    # order is the full document's own — section 2.1.3 reads unit, then conditions, then result
    # (user, 2026-09-22) — with the verdict still stated first, as every other section here
    # states its answer first. Nothing is recomputed for it: the four sub-sections print the
    # same four built tables the full document's 2.1.3.1 and 2.1.3.2 print.
    dict(id="Q2",
         text="**No — and the test could have said yes.** Not one window of this corpus meets "
              "more than one of the three conditions that were fixed in the Preliminary Analysis "
              "(5.7) before any curve of it was drawn, and inside the classes the designs do not "
              "settle either. A negative answer is worth only as much as the unit it is about "
              "and the test it survived, so this section states both before it states the result: "
              "what an archetype is and at which level it is counted, then the three conditions "
              "with their thresholds and where each came from, then the verdict."),
    dict(id="Q2.1", title="What a design is here: the archetype",
         tables=["la_archetype_levels"]),
    dict(id="Q2.2", title="Which level the test is run at: four screens, then a ruling",
         tables=["la_archetype_choice"]),
    dict(id="Q2.3", title="The three conditions, fixed in advance",
         tables=["la_dd_conditions"]),
    dict(id="Q2.4", title="The result",
         figures=["dominant_design", "class_configs"],
         tables=["la_dd_result"]),

    # ---------------------------------------------------------------- Q3
    # The only question with a single core item in the whole document. Rather than print one of
    # the weak ones and ask the reader to discount it, the section says how far the corpus
    # reaches and quotes the grade that keeps the rest out.
    dict(id="Q3",
         text="**Lift + Cruise overtakes Tilt Rotor and keeps the lead, and nothing is abandoned "
              "outright — what falls, falls in share and not in count.** Tilt Rotor goes from "
              "{tk_tr_w1} of the aircraft in the earliest window to {tk_tr_w4} in 2020-23 while "
              "Lift + Cruise rises from {tk_slc_w1} to {tk_slc_w4}; with CVT at {tk_cvt_w4} the "
              "three hold about three quarters of the recent corpus.\n\n"
              "*This is the one question the corpus only partly reaches.* Two items would extend "
              "it and both are graded weak — the class-lifetime figure "
              "(*{sm_grade_class_cycles}*) and the entrant-mix table "
              "(*{sm_grade_la_cohort_mix}*) — so neither is printed. What the most recent window "
              "alone supports, on {sm_ent_2023} entering firms, is that the shift arrives with "
              "the population and not with firms changing course: {tk_cm_e_slc} of the firms "
              "entering in 2020-23 enter with Lift + Cruise against {tk_cm_a_slc} of that "
              "window's aircraft. That is an indication; the finding would need the earlier "
              "windows, and they are too thin to give it.",
         figures=["atlas_arch_time"]),

    # ---------------------------------------------------------------- Q4
    dict(id="Q4",
         text="**Most of the corpus belongs to an organisation, but to a great many small ones, "
              "and there is no top tier.** Named companies hold {tk_fm_named_air} of the "
              "{unique_s} aircraft ({tk_fm_named_share}) and individual inventors "
              "{tk_fm_ind_air}; the largest {tk_seg_top_firms} firms hold {tk_seg_top_air} "
              "between them and all {tk_firms_all} named firms together {tk_named_share} of the "
              "set. The population is still forming: the individual share falls from "
              "{tk_indshare_w1} to {tk_indshare_2023} and in every window most active firms are "
              "filing for the first time, which is why no statement about firm strategy can be "
              "made over the corpus as a whole.\n\n"
              "*One provenance note, because every filer-type statement rests on it:* the filer "
              "type is read from the assignee string the patent itself names (decision G8 of the "
              "methodology framework), and the rule was corrected on 2026-09-23 — figures quoted "
              "from an earlier render, or from `QUESTION_MAP.md`, are from before it and are "
              "lower.",
         figures=["coverage"],
         tables=["la_filer_mix", "la_filers_by_window"]),

    # ---------------------------------------------------------------- Q5
    dict(id="Q5",
         text="**Three countries hold almost two thirds of the corpus — US {tk_us_n}, CN "
              "{tk_cn_n}, DE {tk_de_n} of {unique_s} — and one regional difference survives in "
              "every window: North America keeps the tilting architectures.** The US files "
              "{tk_us_tr} of its aircraft as Tilt Rotor while China's largest class is Lift + "
              "Cruise at {tk_cn_slc}; everything else moves together, and every class is taken "
              "up first in North America, then Europe, then Asia-Pacific, with CVT the one "
              "exception ({tk_crt_cvt_na} in North America, its latest cell).\n\n"
              "*What region does not do is organise design at firm level.* Firms in different "
              "regions are as close in architecture profile as firms in the same one — a null "
              "result, graded core, carried by Figure 2.2.6 of the full document and not "
              "repeated here, because a null needs no picture.",
         figures=["atlas_region", "region_grid"],
         tables=["la_class_region_timing"]),

    # ---------------------------------------------------------------- Q6
    dict(id="Q6",
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

    # ---------------------------------------------------------------- Q7
    dict(id="Q7",
         text="**Where a public aircraft exists the label describes it; but the record is a "
              "record of concepts, not of built machines.** {sm_pub_same} of the {sm_pub_n} "
              "matched aircraft carry the same class as the public product ({sm_pub_share}), "
              "while only {trl_above_s} of the {trl_aircraft_s} ({sm_trl_share}) have reached "
              "anything above TRL 2, {trl_zero_classes} have none at all, and "
              "{sm_trl_nottracked} are not tracked by the public record in any form. The firms "
              "the market rates are a different population in six ways that survive both "
              "correction for multiple testing and the check that they are not an artefact of "
              "publishing in the US.\n\n"
              "*One caveat on the agreement number.* The public directory works in five classes "
              "where this codebook works in twelve, and {sm_fold_vt} of the {unique_s} aircraft "
              "fold into its Vectored Thrust alone, so agreement measured in five classes is a "
              "weaker test than it looks. The per-firm version — does a firm's most-filed class "
              "match its public product — is Figure B.3 of the full document: {flagship_match} "
              "of the {flagship_public} firms that have one.",
         tables=["a2_d16_public_match", "a2_d15_trl_by_class", "la_ari_gap"]),

    # ---------------------------------------------------------------- Q8
    # The figures are ordered shortest-first here for a mechanical reason: ``report`` binds the
    # heading and the FIRST figure into one unbreakable block, and the filings figure is 8.7 in
    # tall — heading, answer and that figure do not fit on one A4 page together, so leading with
    # it would leave the answer alone on a page. The answer's sentences follow the same order.
    dict(id="Q8",
         text="**An early, partly live record with a multi-year lead over the market.** "
              "{tk_lapsed_all} of the {tk_lapsed_n} primary patents with a 2019-or-earlier "
              "priority are already no longer in force, and the classes sit around that line "
              "rather than apart from it. Filing itself rises from {tk_y2015} unique aircraft in "
              "2015 to {tk_y2018} in 2018 and then plateaus, and indexed against all aeronautics "
              "(B64) patenting of the same offices the rise is the sector's own rather than the "
              "general rise in patenting; first flight then comes four to six years after the "
              "first patent for most of the {tk_ari_timeline_n} index firms, which is the "
              "argument for using the record at all.\n\n"
              "*Two bounds on any use of it.* Legal status compares offices, never designs — "
              "{tk_ex_us_gr} of {tk_ex_us_n} primaries are in force at the USPTO against "
              "{tk_ex_cn_gr} of {tk_ex_cn_n} at the CNIPA, and no class differs from another at "
              "either office. And priority years from {partial_start} on are incomplete at the "
              "snapshot ({snapshot}), behind a {lag_p90}-year publication lag, which is why "
              "every window reading here stops at 2023 and the last bar of every time figure is "
              "hatched.",
         figures=["abandonment", "filings_per_year"],
         tables=["la_ari_timeline"]),

    # ---------------------------------------------------------------- M
    dict(id="M",
         text="**Not a statement about the sector — a bound on everything above.** Every label in "
              "this document was read from the patent figures, and against the whole-patent "
              "reading the figures recover the architecture well for the large winged classes "
              "(Tilt Rotor {tk_gt_tr}, Lift + Cruise {tk_gt_slc}) and badly for the small ones "
              "(Pitch-to-Cruise {tk_gt_ptc}, Hoverbike {tk_gt_hb}). Read every small-class number "
              "in this document as the least reliable one on its page.\n\n"
              "*The debt.* Every agreement number here is between the labeller and an outside "
              "source; there is none yet for the labeller against himself. The intra-rater "
              "relabel of 50 patents is designed, is written down as Appendix B.2 of the full "
              "document, and has not been run.",
         figures=["atlas_arch_gt"]),

    # ---------------------------------------------------------------- new questions
    dict(id="new", title="New questions these measures raise",
         text="Six questions that did not exist before these measures did. Each one is a question "
              "the corpus RAISES and does not answer: the measure behind it is named, it is "
              "printed in this document or in the full one, and the last sentence of each says "
              "what would settle it. They are ordered by how far the existing measure already "
              "carries them, not by importance."),
    dict(id="new.1", title="Why does ducting come back at nine rotors and more?"),
    dict(id="new.2", title="Is the one condition that fires a finding, or a choice of weighting?"),
    dict(id="new.3", title="Is CVT · 5-6 a design many firms chose, or one firm's line?"),
    dict(id="new.4", title="Why do firms keep entering with Tilt Wing after it has peaked?"),
    dict(id="new.5", title="Is TRL 2 a fact about the aircraft or about the public record?"),
    dict(id="new.6", title="Do the rated firms get cited more because they are rated?"),

    dict(id="cannot", title="What this corpus cannot answer"),
]

#: the one section that opens a fresh page. ``report.write_markdown`` treats a top-level node
#: whose id is in ``APPENDIX`` as a chapter, and ``build_styled_md_pdf`` breaks a page before a
#: ``div.chapter-start``. Everything else flows, which is what keeps the document short.
APPENDIX = ("new",)

#: ids that are their own page. Used by :func:`depth` — see its docstring.
_TOP = set(APPENDIX)


# --------------------------------------------------------------------------
# 2 — prose that is not a node's own text
# --------------------------------------------------------------------------
#: the lead paragraph of each question section, printed before the answer: the question
#: itself, in full, straight out of ``la_index.QUESTIONS``. Nothing is restated here.
def _question_line(nid: str) -> str:
    q = _la.QUESTIONS.get(nid)
    if not q or q.strip() == _question_title(nid):     # the heading already IS the question
        return ""
    return f"*The question in full: {q}.*"


#: what the section heading says. For a question section it is the first clause of the
#: question — everything before the em dash — so a rewrite of the question rewrites the
#: heading, and a question with no em dash prints whole.
def _question_title(nid: str) -> str:
    q = _la.QUESTIONS.get(nid, nid)
    return q.split(" — ")[0].strip()


TEXTS: Dict[str, str] = {
    "how":
        "This is the Labelling Analysis in short. It is generated from the same tables and the "
        "same figures as the full document, `LABELLING_ANALYSIS.pdf` in this folder: both read "
        "the CSV files in `tables/`, and no number in either is typed by hand, so no number here "
        "can disagree with one there.\n\n"
        "**It is organised by question.** The eight questions are a proposal written on "
        "2026-09-23 and **the author has not confirmed them**; their wording lives in one place "
        "in the code and is printed here from there, so rewriting a question renames a heading "
        "and breaks nothing else. Each section states the answer in a paragraph and then prints "
        "only the items that carry it — one to three of them.\n\n"
        "**What is printed here is what the question map grades core**, meaning the answer rests "
        "on it. That grade is a register in the same code that draws the figures, one entry per "
        "item, and the rule is checked at render time rather than by eye: nothing graded weak "
        "appears in this document, on either ground — low representativeness or low insight — "
        "not even the eight items the map keeps with a stated fix, because a document this short "
        "gives a reader no room to discount a figure while reading it. Where an item here is not "
        "graded core — the vocabulary drawing, the three premise tables of the dominant-design "
        "test, and the two tables the map never reached — its "
        "own grey line prints the grade it does carry and why it is here anyway. Where a "
        "question has too few core items to answer it, and there is one, the third, that "
        "section says so and quotes the grade that keeps the rest out.\n\n"
        "**The apparatus is lighter here.** In the full document every figure and table carries "
        "three grey lines: the unit of analysis with its base and its transform, the takeaway, "
        "and the question it answers. This document keeps the takeaway and drops the other two — "
        "the question line because the heading of the section is the question, and the "
        "unit·base·transform line because it is long and its place is the document you check "
        "against. **Every grey line here ends with the item's number in the full document**, "
        "where both dropped lines are printed in full, together with the source of every column. "
        "Figures and tables are numbered afresh here, in one running sequence, so a number in "
        "this document is never mistaken for a number in that one.\n\n"
        "Two of the tables here — the technology-readiness table and the public-aircraft match "
        "— are gaps G1 and G2 of `QUESTION_MAP.md` §4.1: both are built into `tables/` and, when "
        "this document was written, printed in no document at all. They are the strongest "
        "evidence the seventh question has, so this one prints them.",

    "data":
        "{acquired_s} patents were acquired and {wizard_approved_s} of them show an aircraft that can "
        "be read from the figures. {gated_patents_s} of those leave on a domain tag — a UAV, a "
        "non-electric aircraft, a short-take-off-only aircraft — which leaves {representative_s} "
        "representative patents, of which {primary_s} are the primary record of an aircraft "
        "rather than a duplicate filing. Those describe **{unique_s} unique aircraft**, and the "
        "unique aircraft is the unit of every number in this document unless a line says "
        "otherwise. {figures_approved_s} whole-aircraft figures stand behind them. How each of "
        "those steps was decided is Appendix A of the full document; what the labels are worth is "
        "Appendix B and the method section at the end of this one.",

    "vocab":
        "Every finding below is stated in the twelve architecture classes of card G1. They split "
        "on what tilts and what carries the weight in cruise — never on size, mission or "
        "occupancy — and they are very unequal.",

    # ---- Q2's premise, in three parts. Restored 2026-09-23; see the comment on the node.
    "Q2.1":
        "**An archetype is a combination of label answers, and nothing more.** Fix a set of "
        "dimensions; write each aircraft as its answers on those dimensions, joined by middle "
        "dots — *{sm_a1t_top}* is one such string and *{sm_a0c_top}* another — and two "
        "aircraft share an archetype when the string is the same. Every aircraft belongs to "
        "exactly one archetype at a given level, and every level refines the twelve architecture "
        "classes of card G1 rather than cutting across them. A blank is a design absence and "
        "stays an answer of its own — an aircraft with no wing is not a missing value, it is an "
        "aircraft whose answer is *none*. The single exclusion is an answer hidden by a stage "
        "override: that aircraft is left out of the level instead of being given a blank, which "
        "is why the base moves by a few aircraft from one level to the next.\n\n"
        "**The level is not a detail; it is the question.** The codebook can form "
        "{sm_arch_levels} levels, and they do not agree. At A0 — the architecture class on its "
        "own — the corpus falls into {sm_a0_arch} archetypes with {sm_a0_eff} effective ones; at "
        "A2c it falls into {sm_a2c_arch}, of which {sm_a2c_single} hold one aircraft each. "
        "Convergence measured at the first is a different question from convergence measured at "
        "the last, so any claim that the space is or is not converging is a claim about a level "
        "and has to name it. The effective number ¹D in the table is the exponential of the "
        "Shannon entropy of the archetype shares — the number of equally common archetypes that "
        "would produce the same spread — so the distance between it and the archetype count is "
        "how uneven a level is.",

    "Q2.2":
        "**The level was chosen by four screens, applied to the counts of the previous table and "
        "fixed in code** (`la_tables.ARCHETYPE_SCREENS`), not by which level gives the more "
        "interesting answer. *Resolution* asks whether the level yields enough archetypes to "
        "tell designs apart at all, against a line set at twice the number of architecture "
        "classes. *Fragmentation* asks how much of the corpus ends up alone in an archetype of "
        "one. *Population* asks how much of it sits inside archetypes large enough to measure. "
        "*Readable shares* asks how many archetypes are big enough for a share to mean anything. "
        "Each cell below prints the level's own value, the line it is held to and whether it "
        "clears it; {sm_arch_pass} of the {sm_arch_levels} levels clear all four, and a level "
        "that clears them can still be set aside on a codebook ruling, which the table prints "
        "with its reason.\n\n"
        "**A1t is the design species, and A0c is reported beside it at every step — not as a "
        "check on it** (ruled 2026-09-23). A1t combines {sm_a1t_dims}. It is the level at which "
        "the criterion of Preliminary Analysis 5.7 is written, its three dimensions are direct "
        "codebook answers with no binning choice for a reader to attack, and it concentrates the "
        "corpus far enough for a share to carry meaning — {sm_a1t_n} aircraft in {sm_a1t_arch} "
        "archetypes, the largest of them {sm_a1t_top} at {sm_a1t_top_share} — read against that "
        "dimension list, *Lift + Cruise, one wing, nothing that tilts*. A0c combines "
        "{sm_a0c_dims}. It is not a robustness run on A1t, and it earns the second place three "
        "times over: it is the only level at which condition 2 fires anywhere in the whole test, "
        "so the one balance signal the corpus gives would be invisible without it; it divides "
        "the corpus by the number of propulsive units, the dimension the eVTOL taxonomy turns "
        "on; and it leaves almost no aircraft alone in an archetype of one, {sm_a0c_single} of "
        "{sm_a0c_n}. Every condition below is stated at both levels, and where the two disagree "
        "this document says so rather than choosing for the reader.",

    "Q2.3":
        "**The three conditions are not this document's, and no number of this corpus enters "
        "them.** They were written in the Preliminary Analysis (5.7) — with the distance of 5.3 "
        "and the disparity measure of 5.5 — before any curve of this corpus was drawn, and they "
        "are deliberately different in kind, because a sector can crowd onto one archetype name "
        "without its aircraft becoming alike. Condition 1 is about **counts**: does one "
        "archetype hold most of the sector, in two consecutive complete windows. Condition 2 is "
        "about **balance**: does a window hold fewer designs in play than shuffling the same "
        "labels across windows would give it. Condition 3 is about **form**: have the aircraft "
        "themselves become similar, measured as the mean Gower distance between two aircraft of "
        "the window drawn at random, against the two earliest windows and against the same "
        "shuffle. A dominant design requires all three in the same complete window; the table "
        "gives each threshold and the paragraph of the Preliminary Analysis it comes from. That "
        "the thresholds were set first is the whole reason the next section is a test whose "
        "answer could have been yes, rather than a description written after the curves.",

    "Q2.4":
        "**No window meets more than one of the three, and condition 1 is not close.** The "
        "largest archetype of any window, at either level, reaches {tk_dd_top_share} against a "
        "50 % line. Condition 2 fires in {tk_dd_below} of {tk_dd_cells} level-windows, all of "
        "them at A0c and only in the two earliest — the windows with the least data behind them. "
        "Condition 3 fires in {tk_q_below} of {tk_q_cells} cells, and only under one of the two "
        "weightings the Preliminary Analysis requires to be reported together; under the other "
        "it does not fire at all, which is the second of the new questions at the end of this "
        "document. On its own pre-stated criterion the corpus is still in the era of ferment. "
        "Nor do the classes settle internally: {top_class}'s {tk_slc_n_2023} aircraft of 2020-23 "
        "take {tk_slc_configs_2023} different configurations between them.",

    "new.1":
        "**The measure.** Ducting does not follow the calendar and does not follow the map, but it "
        "follows rotor count, and not in a straight line: {sm_duct_13} of the aircraft with three "
        "or fewer propulsive units carry a ducted unit, {sm_duct_78} of those with seven or "
        "eight, and {sm_duct_9} of those with nine or more, against {sm_duct_all} over the whole "
        "corpus. It is not the class mix in disguise — the dip is there inside Lift + Cruise, "
        "Tilt Rotor and CVT taken one at a time, and the figure prints the test with the class "
        "held fixed. The measure is panel (iii) of the propulsion figure in Q1 and "
        "`tables/la_duct_units.csv`.\n\n"
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
        "recent window, and it fires {sm_c3_met}. Under the uniform weighting reported beside it, "
        "the same level-windows sit inside the permutation band and the condition does not fire "
        "at all.\n\n"
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
        "class puts {sm_cvt_own_2023} of its own aircraft in that one window.\n\n"
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
        "Wing, against {sm_tw_air_2023} of that window's aircraft.\n\n"
        "**Why it is a question.** Everywhere else in this corpus entrants over-index on the "
        "class of their moment, and that is the mechanism behind the whole third question. Tilt "
        "Wing is the case where entrants over-index on a class whose share is falling. Either the "
        "entrants are late and will follow, or Tilt Wing is a first design that firms pass "
        "through — and the two have opposite implications for reading any share as a trend.\n\n"
        "**What would answer it.** The within-firm successions restricted to the firms that "
        "entered with Tilt Wing: what their next aircraft is. The succession machinery exists "
        "(Figure 2.2.4 of the full document, {tk_trans_pairs} pairs); it has never been cut by "
        "the class a firm entered with. The technology-readiness table is the second half of the "
        "answer — Tilt Wing sits at {sm_trl_tw} above TRL 2.",

    "new.5":
        "**The measure.** {trl_above_s} of the {trl_aircraft_s} aircraft ({sm_trl_share}) have "
        "reached anything above TRL 2; {sm_trl_nottracked} of them are not tracked by the public "
        "record at all, and four classes — {trl_zero_classes} — have not one aircraft above TRL 2 "
        "between them.\n\n"
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
        "effect that removes two of the other differences.\n\n"
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
        "The review asked for noise, wind, mission and battery specific energy as drivers of "
        "design choice. None of the four is a labelled dimension and none is stated in the "
        "patents, so no figure in either document can carry them, and one honest paragraph is "
        "the right answer rather than four weak figures.\n\n"
        "**Noise** and **wind or weather** are not recorded anywhere in the codebook and are "
        "not stated in the patent texts. **Mission** exists only for the 95 aircraft with an "
        "evtol.news page — 14 % of the corpus — and that subset fails the representativeness "
        "test against the other 570 on four of six attributes, so it cannot stand for the rest; "
        "the field is majority-unspecified even inside it. **Battery specific energy** is "
        "external to this corpus entirely: a published Wh/kg series against the filing curve "
        "would be legitimate context and would prove nothing about these aircraft, and it must "
        "be labelled as context if it is used. **Regulation** reaches the corpus only through "
        "examination outcome, and the eighth question shows that outcome is an office effect and "
        "not a technology effect.\n\n"
        "What the corpus does carry on the same theme is the number of propulsive units, the "
        "ducting share and the tail type — the three fields that a noise or a gust argument "
        "would have to work through — and all three are in the first question.",
}

AFTER: Dict[str, str] = {
    # The Q2 note that used to stand here — "the three thresholds are Table 2.1.3.2 of the full
    # document" — was deleted on 2026-09-23 when Q2.3 began printing that table itself.
    "Q7":"*The AAM Reality Index is one index, not two: AAM for the field, ARI for the score. "
          "It is an analyst's judgement, published quarterly, not a measurement — section 2.2.7 "
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
    "class_configs": "within-class convergence: how far each architecture class settles on a "
                     "single configuration. A configuration is one aircraft's combination of "
                     "propulsive units (banded), ducted or open, booms or no booms, and tail "
                     "type; every class with 5+ aircraft in 3+ windows is drawn",
})

TABLE_CAPTIONS.update({
    # Q2's premise. The archetype-levels caption is rewritten only because this document prints
    # the table without its "used in this document" column: the full document's caption ends on
    # "and where this document reads the level", which would describe a column that is not here.
    "la_archetype_levels": "Every archetype level the codebook can form: the dimensions it "
                           "combines, its largest archetype, how many archetypes the level "
                           "yields, how many aircraft end up alone in one, the effective number "
                           "of archetypes (Hill ¹D) and the share held by the largest. The "
                           "counting columns reproduce table 3.3.6 of the Preliminary Analysis; "
                           "which section reads which level is the last column of Table 2.1.3.1a "
                           "of the full document",
    "la_dd_result": "The dominant-design verdict, one line per condition (the observed result "
                    "behind each line is Table 2.1.3.3a of the full document)",
    "la_ari_gap": "What separates the aircraft of the AAM Reality Index firms from the rest of "
                  "the corpus: the eight differences that survive correction for multiple "
                  "testing, ordered by p. `holds?` is `yes` only where the difference also "
                  "survives being re-run on the US-published patents alone",
    "la_class_region_timing": "Median priority year of each class inside each applicant region, "
                              "with the aircraft each cell rests on; a cell under five aircraft "
                              "is left unread",
    "la_class_filer_weight": "How much of each class is one filer repeating itself: the share "
                             "held by the largest filer, and the number of equally sized filers "
                             "that would give the same concentration",
    "la_ari_timeline": "The patent clock against the market clock, firm by firm. Both market "
                       "dates are the index's own statements, and the years count from the "
                       "firm's first patent IN THIS CORPUS, so every figure is a floor",
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
}

#: columns to print, where the built table is wider than a compact page can carry. Nothing is
#: recomputed: these are the same columns, fewer of them.
COLUMNS: Dict[str, List[str]] = {
    "a2_d3_selected_fields": ["name", "answered", "answers", "top_share", "most common answers"],
    # Q2's premise. ``la_archetype_levels`` drops only the full document's last column, a
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
    # ---- Q2: the archetype levels and the choice among them (the premise of the test).
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
    # ---- Q7: the public match (gap G2) and the class fold
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
    # ---- Q3: the base of the one window that is read
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
}

#: The items printed here that ``la_index.GRADE`` does not grade **core**, each with the
#: reason it is printed anyway. The render script refuses any item outside this list that is
#: not core, so the selection rule cannot quietly slip. None of them is graded *weak*: the
#: three added on 2026-09-23 are graded **supporting**, which that register defines as
#: "apparatus the answer needs but is not — a premise, a caveat, or a description of the data
#: set". Q2's answer is negative, and a negative answer is unreadable without its premise.
NOT_CORE: Dict[str, str] = {
    "codebook_classes": "it is the vocabulary every finding is stated in, and a reader without "
                        "the twelve classes cannot read any other page",
    "la_archetype_levels": "the whole of Q2 is a statement about archetypes, and a reader who "
                           "has not seen what an archetype is, or how much the level changes "
                           "the count, cannot judge the answer",
    "la_archetype_choice": "it is the evidence that the level the test is run at was chosen by "
                           "four stated screens and a recorded ruling, and not by which level "
                           "gave the better answer",
    "la_dd_conditions": "the three thresholds were fixed before the curves were drawn, and that "
                        "is the only thing that makes a negative result a finding rather than a "
                        "description",
    "a2_d15_trl_by_class": "gap G1 of the question map, and the strongest evidence Q7 has",
    "a2_d16_public_match": "gap G2 of the question map, and the headline agreement number of "
                           "the whole labelling effort",
}


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
    return f"## {title}" if "." not in node_id else f"#### {title}"


def level_line(node_id: str) -> str:
    """The question in full, printed where the full document prints the level of analysis.

    The level of analysis of this document is one sentence and is stated once, in "How to read
    this brief": every number is per unique aircraft unless its own line says otherwise.
    """
    return _question_line(node_id) if node_id in _la.QUESTIONS else ""


def text(node_id: str, values: Optional[Dict] = None) -> str:
    n = node(node_id)
    return _pa._fill(n.get("text") or TEXTS.get(node_id, ""), values)


def after(node_id: str, values: Optional[Dict] = None) -> str:
    return _pa._fill(node(node_id).get("after") or AFTER.get(node_id, ""), values)


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


def figure_number(node_id: str, k: int, total: int) -> str:
    return _FIG_NUM.get((node_id, k), f"{node_id}.{k + 1}")


def table_number(node_id: str, k: int, total: int) -> str:
    return _TAB_NUM.get((node_id, k), f"{node_id}.{k + 1}")


# --------------------------------------------------------------------------
# 7 — the grey line: the takeaway, and where the item lives in the full document
# --------------------------------------------------------------------------
#: internal name -> "Figure 2.1.6a" / "Table 2.2.3c", the item's number in the full
#: LABELLING_ANALYSIS. Filled by :func:`set_full_reference` at render time from
#: ``la_index.NODES`` and the figures and tables that actually exist, which is exactly how
#: ``report.write_markdown`` numbers that document.
FULL_REF: Dict[str, str] = {}

#: items printed here that the full document does not print. They are named rather than
#: silently left without a reference.
NOT_IN_FULL: Dict[str, str] = {
    "a2_d15_trl_by_class": "Built into `tables/a2_d15_trl_by_class.csv`; not in the full "
                           "document's running order at this render",
    "a2_d16_public_match": "Built into `tables/a2_d16_public_match.csv`; not in the full "
                           "document's running order at this render",
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
    # no takeaway exists in la_index for these three
    "a2_d16_public_match":
        "Where a public aircraft exists, the figure label describes it: {sm_pub_same} of the "
        "{sm_pub_n} matched aircraft carry the same class ({sm_pub_share}). {sm_pub_other} "
        "describe another configuration and drawing and text agree that they do; only "
        "{sm_pub_draw} are a drawing that misreads its own patent. This is the headline "
        "agreement number of the labelling effort and it is stated nowhere else.",
    "a2_d15_trl_by_class":
        "The patent record is a record of concepts: {trl_above_s} of {trl_aircraft_s} aircraft "
        "({sm_trl_share}) are above TRL 2, and the classes that get patented most are not the "
        "classes that get built — {trl_best_class} leads the large classes while "
        "{trl_zero_classes} have none at all. Read every figure here as a floor: TRL 2 is also "
        "what an aircraft gets when nothing public is known about it.",
    "la_ari_gap":
        "The firms the market rates are a different population, and it is not an artefact of "
        "where they publish: eight differences survive the correction over the whole table and "
        "six of them survive being re-run on the US-published patents alone. The largest is the "
        "cohort citation rank, {sm_cite_idx} against {sm_cite_rest}. The applicant region is "
        "marked `yes, by selection` because that is what the index selects on, and family size "
        "is marked `office effect` because it does not survive the US check.",
    # the la_index line prints the top share as the raw fraction ``0.28``; the same sentence
    # with the share read as a share, so this document is consistent with its own Q1
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
        "of {units_n} aircraft put their units on exactly two stations. Panel (iii) is why "
        "ducting is drawn against rotor count and not against region or year: it falls from "
        "{sm_duct_13} at three units or fewer to {sm_duct_78} at seven or eight and returns to "
        "{sm_duct_9} at nine or more, against {sm_duct_all} over the corpus, and the dip survives "
        "holding the class fixed. The design argument behind that U is written out in full in the "
        "full document",
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
    tail = []
    ref = FULL_REF.get(name)
    if ref:
        tail.append(f"Full document: {ref}, with its unit, base and transform")
    elif NOT_IN_FULL.get(name):
        tail.append(NOT_IN_FULL[name])
    # the grade is read live rather than stored, so an item that is regraded — or wired into
    # the full document and graded core — loses this clause on the next render instead of
    # carrying a stale one
    grade = ""
    gfn = getattr(_la, "grade", None)
    if gfn is not None:
        try:
            grade = gfn(name, None, kind, tables)
        except Exception:
            grade = ""
    if grade and not grade.startswith("core") and name in NOT_CORE:
        # an item the map has not reached says so plainly rather than repeating the register's
        # own "add it to GRADE" marker at a reader who cannot act on it
        if grade == getattr(_la, "NO_GRADE", None):
            grade = "not yet graded by the question map"
        tail.append(f"{grade[0].upper()}{grade[1:]}; printed here because {NOT_CORE[name]}"
                    if grade.startswith("not yet")
                    else f"Graded {grade}; printed here because {NOT_CORE[name]}")
    if not tail:
        return line
    return line + " · " + " · ".join(tail) + "."
