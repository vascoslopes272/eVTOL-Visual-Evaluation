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
# and the grade that keeps the missing item out is quoted — see Q2, which has exactly one core
# item in the whole document.
NODES: List[Dict] = [
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
         text="*The data set, in two lines.* {acquired_s} patents were acquired, {representative_s} "
              "of them describe an electric VTOL aircraft readable from its figures and are not a "
              "duplicate filing, and those describe **{unique_s} unique aircraft**. The twelve "
              "architecture classes every finding is stated in are drawn in "
              "{sm_ref_codebook_classes} of `LABELLING_ANALYSIS.pdf`, in this folder, which "
              "carries each item's unit, base and transform.\n\n"
              "**An early, partly live record with a multi-year lead over the market.** "
              "{tk_lapsed_all} of the {tk_lapsed_n} primary patents with a 2019-or-earlier "
              "priority are already no longer in force, and the classes sit around that line "
              "rather than apart from it. Filing itself rises from {tk_y2015} unique aircraft in "
              "2015 to {tk_y2018} in 2018 and then plateaus, and indexed against all aeronautics "
              "(B64) patenting of the same offices the rise is the sector's own rather than the "
              "general rise in patenting; first flight then comes four to six years after the "
              "first patent for most of the {tk_ari_timeline_n} index firms, which is the "
              "argument for using the record at all.\n\n"
              "*The study window.* The record is read in five priority windows, from "
              "{sm_win_first} to {sm_win_last}, and the two complete windows 2016-23 hold "
              "{sm_win_active_n} of the {unique_s} aircraft ({sm_win_active_share}). Every "
              "trend claim stops at 2023: priority years from {partial_start} on are incomplete "
              "at the snapshot ({snapshot}), behind a {lag_p90}-year publication lag, and the "
              "last bar of every time figure is hatched.\n\n"
              "*One bound on any use of it.* Legal status compares offices, never designs — "
              "{tk_ex_us_gr} of {tk_ex_us_n} primaries are in force at the USPTO against "
              "{tk_ex_cn_gr} of {tk_ex_cn_n} at the CNIPA, and no class differs from another at "
              "either office.",
         figures=["abandonment", "filings_per_year"],
         tables=["la_ari_timeline"]),

    # ---------------------------------------------------------------- Q2
    # Second: what is gaining and dying, read before the archetype test (Q3) and before the
    # inventory (Q4), on the author's instruction. ``dimension_drift`` (core)
    # is the figure the author asked for under Figure 2 (ii): propulsor counts inside one class
    # over the years.
    dict(id="Q2",
         text="**Lift + Cruise overtakes Tilt Rotor and keeps the lead, and nothing is abandoned "
              "outright — what falls, falls in share and not in count.** Tilt Rotor goes from "
              "{tk_tr_w1} of the aircraft in the earliest window to {tk_tr_w4} in 2020-23 while "
              "Lift + Cruise rises from {tk_slc_w1} to {tk_slc_w4}; with CVT at {tk_cvt_w4} the "
              "three hold about three quarters of the recent corpus. Inside the classes (the "
              "twelve of {sm_ref_codebook_classes} of the full document) the one dimension that "
              "moves the same way everywhere is the number of propulsive units — Tilt Rotor's "
              "median goes from {tk_tr_units_w1} units in the earliest window to "
              "{tk_tr_units_w4} in 2020-23 — and ducting does not move "
              "({sm_here_dimension_drift}).\n\n"
              "*Only the most recent window carries the mechanism.* On {sm_ent_2023} entering "
              "firms, the shift arrives with the population rather than with firms changing "
              "course: {tk_cm_e_slc} of the firms entering in 2020-23 enter with Lift + Cruise "
              "against {tk_cm_a_slc} of that window's aircraft. The earlier windows are too thin "
              "to extend it, so this stays an indication.",
         figures=["atlas_arch_time", "dimension_drift"]),

    # ---------------------------------------------------------------- Q3
    # Third, before Q4: the archetype has to be explained before Q4's archetype figure is read.
    # The only question printed in four parts (unit, screens, conditions, result — the full
    # document's own order, 1.1.3), with the verdict still stated first. Cut to about half its
    # 2026-09-23 length on the author's review: short definitions, the tables carry the detail.
    dict(id="Q3",
         text="**No — and the test could have said yes.** No window of this corpus meets more "
              "than one of three conditions fixed in the Preliminary Analysis (5.7) before any "
              "curve of it was drawn, and inside the classes the designs do not settle either."),
    dict(id="Q3.1", title="What a design is here: the archetype",
         tables=["la_archetype_levels"]),
    dict(id="Q3.2", title="Which level the test is run at: four screens, then a ruling",
         tables=["la_archetype_choice"]),
    dict(id="Q3.3", title="The three conditions, fixed in advance",
         tables=["la_dd_conditions"]),
    dict(id="Q3.4", title="The result",
         figures=["dominant_design", "class_configs"],
         tables=["la_dd_result"]),

    # ---------------------------------------------------------------- Q4
    # The answer is two or three sentences, never a page: everything else the corpus says about
    # this question is already printed on the items, in their takeaway lines.
    dict(id="Q4",
         text="**A wide space with a crowded middle, and the variety is in the propulsion, not "
              "in what tilts.** Twelve architecture classes are occupied (the archetypes of the first "
              "figure are the A0c level of Q3), the largest — "
              "{top_class} — holds {sm_top_class_share} of the {unique_s} aircraft, and only two "
              "label fields are really spread: the tail, and the number of propulsive units, "
              "whose five bands hold {bin_r03}, {bin_r4}, {bin_r56}, {bin_r78} and {bin_r9} "
              "aircraft. Where the corpus does converge is on arrangement — {grp2} of {units_n} "
              "aircraft put their units on exactly two stations.",
         figures=["zones", "atlas_units"],
         tables=["a2_d3_selected_fields"]),

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
              "Cruise at {tk_cn_slc}; everything else moves together, and every class is taken "
              "up first in North America, then Europe, then Asia-Pacific, with CVT the one "
              "exception ({tk_crt_cvt_na} in North America, its latest cell).\n\n"
              "*What region does not do is organise design at firm level.* Firms in different "
              "regions are as close in architecture profile as firms in the same one — a null "
              "result, carried by {sm_ref_proximity_region} of the full document.",
         figures=["atlas_region", "region_grid"],
         tables=["la_class_region_timing"]),

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
              "match its public product — is {sm_ref_atlas_flagship} of the full document: "
              "{flagship_match} of the {flagship_public} firms that have one.",
         tables=["a2_d16_public_match", "a2_d15_trl_by_class", "la_ari_gap"]),

    # ---------------------------------------------------------------- design drivers (2026-09-23)
    # Not a ninth question: the closing reading of Q2-Q4 (what is gaining, whether it converges,
    # what is being designed), placed after the last question section and before the method
    # bound. Printed because both tables are graded core in
    # la_index.GRADE; the drift figure (Figure 1.4.1 of the full document, eleven panels) is core
    # too but is not printed — the verdict table carries every one of its readings with the test
    # beside it, and the figure would cost this document a page for the same content.
    dict(id="drivers", title="Design drivers and their traces",
         text="**What moved, moved inside the tilting classes, and almost nothing that moved points at "
              "one driver.** The design drivers — the technology that moved over the window, the "
              "physics that did not, the requirements, the life-cycle costs — are not observed in a "
              "patent; each leaves a trace in the morphology, and the traces are what the aircraft "
              "are labelled with. Tilt Rotor goes from a median "
              "of {tk_dr_tr_units_first} propulsive units to {tk_dr_tr_units_last} and CVT from "
              "{tk_dr_cvt_units_first} to {tk_dr_cvt_units_last}, while Lift + Cruise, which started "
              "at {tk_dr_slc_units_first}, stays where it was — and three drivers predict that rise "
              "(distributed control, failure tolerance, community noise), so the record cannot say "
              "which. Units move onto booms across the five classes ({tk_dr_all_booms_first} to "
              "{tk_dr_all_booms_last}), which one moving driver alone predicts. The opposed pair — "
              "tilting joints, which regime transition pushes up and cost pushes down — splits by "
              "level: the joint count rises inside Tilt Rotor and CVT (TR {tk_dr_tr_joints_mov}, CVT "
              "{tk_dr_cvt_joints_mov}) and the pooled row is {tk_dr_all_joints_mov}, because the "
              "class that grows has no joints at all. Retraction of lift units, the one-driver trace "
              "of drag reduction, is in the record at {tk_dr_slc_retract_last} of Lift + Cruise and "
              "{tk_dr_slc_retract_mov}.\n\n"
              "*Of the four couplings the fixed physical drivers predict, one is there:* empennage "
              "type against the wing configuration (V {tk_dr_emp_wing_v}, in the strongest tenth of "
              "all pairs of label fields); boom presence against the wing, units on the wing against "
              "its planform, and the position of the wing units against retraction are no stronger "
              "than a random pair. These are facts about the traces, not answers about the "
              "drivers. Five traces the drivers predict carry no label at all — rotor diameter, "
              "hub mechanism, cabin dimensions, aircraft size, the joint count — and close the "
              "table.",
         tables=["la_driver_verdicts", "la_driver_questions"]),

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
    # Each question owns ONE panel and prints it BEFORE its prose (author, 2026-09-23: "I want
    # to see the evidence by my eyes, not text"). The order comes for free: a node whose prose
    # lives in :data:`AFTER` rather than in :data:`TEXTS` renders as heading, panel, prose —
    # and because the id is NOT in :data:`NO_KEEP`, the heading and the panel travel together,
    # so a question is never printed on one page and its evidence on the next. The panels are
    # drawn by :mod:`sm_figures`, which exists for this section and is imported nowhere else;
    # the full document is untouched and still points at its own figures.
    dict(id="new", title="New questions these measures raise",
         text="Six questions the corpus raises and does not answer. Each is printed with the "
              "one measure it is about."),
    dict(id="new.1", title="Why does ducting come back at nine rotors and more?",
         figures=["sm_duct_bands"]),
    dict(id="new.2", title="Is the one condition that fires a finding, or a choice of weighting?",
         figures=["sm_weighting"]),
    dict(id="new.3", title="Is CVT · 5-6 a design many firms chose, or one firm's line?",
         figures=["sm_archetype_filers"]),
    dict(id="new.4", title="Why do firms keep entering with Tilt Wing after it has peaked?",
         figures=["sm_tw_entry"]),
    dict(id="new.5", title="Is TRL 2 a fact about the aircraft or about the public record?",
         figures=["sm_trl_tracked"]),
    dict(id="new.6", title="Do the rated firms get cited more because they are rated?",
         figures=["sm_cite_rank"]),

    dict(id="cannot", title="What this corpus cannot answer"),

    # The taxonomy drawing closed this document until 2026-09-23; the author has printed it
    # already, so it is dropped here and stays Appendix D of the full document. The two
    # in-text pointers to it — the opening paragraph of Q1 and the class line of Q2 — now
    # name that document, through ``{sm_ref_codebook_classes}``, which resolves to the number
    # the full document gives the drawing at this render.
]

#: the one section that opens a fresh page. ``report.write_markdown`` treats a top-level node
#: whose id is in ``APPENDIX`` as a chapter, and ``build_styled_md_pdf`` breaks a page before a
#: ``div.chapter-start``. Everything else flows, which is what keeps the document short.
APPENDIX = ("new",)

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
    # ---- Q3's premise, in three parts (restored 2026-09-23; cut to the point the same day:
    # short definitions, the tables carry the detail, nothing of the full document's argument
    # is repeated).
    "Q3.1":
        "**An archetype is a combination of label answers, and nothing more.** Fix a set of "
        "dimensions and write each aircraft as its answers on them, joined by middle dots — "
        "*{sm_a1t_top}* is one, *{sm_a0c_top}* another; two aircraft share an archetype when "
        "the string is the same. A blank is a design absence and stays an answer (*no wing* is "
        "an answer, not a missing value); an aircraft whose field is hidden by a stage override "
        "is left out of that level, which is why the base moves by a few aircraft between "
        "levels.\n\n"
        "**The level is the question.** The codebook forms {sm_arch_levels} levels and they do "
        "not agree: at A0 — the class alone — the corpus falls into {sm_a0_arch} archetypes with "
        "{sm_a0_eff} effective ones (¹D, the exponential of the Shannon entropy of the shares); "
        "at A2c into {sm_a2c_arch}, of which {sm_a2c_single} hold one aircraft. A convergence "
        "claim is a claim about a level and has to name it.",

    "Q3.2":
        "**Four screens, fixed in code (`la_tables.ARCHETYPE_SCREENS`), choose the level — not "
        "which level gives the more interesting answer.** *Resolution*: enough archetypes to "
        "tell designs apart (at least twice the number of classes). *Fragmentation*: how much "
        "of the corpus sits alone in an archetype of one. *Population*: how much sits in "
        "archetypes large enough to measure. *Readable shares*: how many archetypes are big "
        "enough for a share to mean anything. {sm_arch_pass} of the {sm_arch_levels} levels "
        "clear all four.\n\n"
        "**A1t is the design species; A0c is reported beside it** (ruled 2026-09-23). A1t is "
        "{sm_a1t_dims} — the level Preliminary Analysis 5.7 is written at, three direct "
        "codebook answers with no binning; {sm_a1t_n} aircraft in {sm_a1t_arch} archetypes, "
        "the largest {sm_a1t_top} at {sm_a1t_top_share}. A0c is {sm_a0c_dims}: the dimension "
        "the taxonomy turns on, and the only level at which condition 2 fires anywhere. Every "
        "condition is stated at both levels.",

    "Q3.3":
        "**Written in the Preliminary Analysis (5.7) before any curve of this corpus was drawn; "
        "no number of this corpus enters them.** They differ in kind, because a sector can "
        "crowd onto one archetype name without its aircraft becoming alike: **counts** (one "
        "archetype holds most of two consecutive complete windows), **balance** (a window "
        "holds fewer designs in play than shuffling the labels across windows would give it), "
        "**form** (the aircraft themselves have become similar — mean Gower distance within "
        "the window, against the two earliest windows and the same shuffle). A dominant "
        "design needs all three in one complete window; the table gives each threshold and "
        "its paragraph.",

    "Q3.4":
        "**No window meets more than one of the three, and condition 1 is not close.** The "
        "largest archetype of any window, at either level, reaches {tk_dd_top_share} against a "
        "50 % line. Condition 2 fires in {tk_dd_below} of {tk_dd_cells} level-windows, all at "
        "A0c and only in the two earliest — the windows with the least data. Condition 3 fires "
        "in {tk_q_below} of {tk_q_cells} cells, under one of the two required weightings only "
        "(the second of the new questions at the end). On its own pre-stated criterion the "
        "corpus is still in the era of ferment, and the classes do not settle internally "
        "either: {top_class}'s {tk_slc_n_2023} aircraft of 2020-23 take {tk_slc_configs_2023} "
        "different configurations.",

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
        "effect that removes two of the other differences. It is the cohort-citation-rank row of "
        "{sm_here_la_ari_gap}.\n\n"
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
        "Four things a design account would want — noise, wind or weather, mission, and battery "
        "specific energy — are not in this record: none of the four is a labelled dimension and "
        "none is stated in the patents, so no figure in either document can carry them.\n\n"
        "**Noise** and **wind or weather** are not recorded anywhere in the codebook and are "
        "not stated in the patent texts. **Mission** exists only for the 95 aircraft with an "
        "evtol.news page — 14 % of the corpus — and that subset fails the representativeness "
        "test against the other 570 on four of six attributes, so it cannot stand for the rest; "
        "the field is majority-unspecified even inside it. **Battery specific energy** is "
        "external to this corpus entirely: a published Wh/kg series against the filing curve "
        "would be legitimate context and would prove nothing about these aircraft, and it must "
        "be labelled as context if it is used. **Regulation** reaches the corpus only through "
        "examination outcome, and Q1 shows that outcome is an office effect and "
        "not a technology effect.\n\n"
        "What the corpus does carry on the same theme is the number of propulsive units, the "
        "ducting share and the tail type — the three fields that a noise or a gust argument "
        "would have to work through — and all three are in Q4.",
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
    # the author reads the verdict table with the full document open beside it (2026-09-23)
    "la_driver_verdicts": _with_driver_pointer,
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


def level_line(node_id: str, values: Optional[Dict] = None) -> str:
    """The question in full, then the unit of analysis, printed where the full document
    prints the level of analysis. ``report`` calls this with the node id alone, so the unit
    line's numbers are filled from :data:`_VALUES`, set by :func:`resolve`."""
    if node_id not in _la.QUESTIONS:
        return ""
    parts = [_question_line(node_id)]
    unit = UNIT.get(node_id)
    if unit:
        parts.append("*Unit of analysis: " + _pa._fill(unit, values or _VALUES) + ".*")
    return "\n\n".join(p for p in parts if p)


#: the resolved numbers of the last :func:`resolve` call — the only route by which
#: :func:`level_line`, which ``report`` calls without ``values``, can fill its unit line.
_VALUES: Dict = {}


def text(node_id: str, values: Optional[Dict] = None) -> str:
    """The prose printed between a heading and the items under it — empty for the six
    new-question sections, whose panel comes first and whose prose is printed by
    :func:`after`. ``report.write_markdown`` prints heading, this, then the items, so a node
    that wants its figure ahead of its words simply leaves this empty."""
    n = node(node_id)
    if node_id in PANEL_SECTIONS:
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
        tail.append(f"Full document: {ref}, with its unit, base and transform")
    elif NOT_IN_FULL.get(name):
        tail.append(NOT_IN_FULL[name])
    if not tail:
        return line
    return line + " · " + " · ".join(tail) + "."
