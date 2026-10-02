"""Chapter 2 of the brief — "Design space" (2026-09-26, the chapter-2 review).

Written to BRIEF_REVISION_RULES.md from the author's Word comments C47-C50, C60, C62, C67-C78
and C83 (REVIEW_2026-09-26_ch2_docx_comments.txt). Loaded by ``sm_index`` through
``CHAPTER_MODULES``; the interface is the CHAPTER MODULES block at the end of ``sm_index.py``.

What the chapter does, and why it comes before chapter 3 (C67): it defines what a design is
made of (2.1, the label fields and the propulsion), how designs are grouped into archetypes and
at which level of detail every later count is made, including the post-hoc Lift + Cruise family
F (2.2, C47-C50, C54), and where the recent designs concentrate and whether new ones still
appear (2.3, C70-C74). Every number is a placeholder read from a table (rule 1); the numbers no
spec can say are computed in :func:`_ch2_numbers` from the tables, never from the dataset.

Comment map
-----------
C47/C49/C61  readable archetype names and level codes (``sm_text_methods.archetype_label`` /
             ``level_name``), in every table (PRINT hooks) and every takeaway.
C48/C50/C54  the level table shows only C, C·U, C·W·T and F (``la_archetype_levels_brief``,
             built in ``sm_open``); finer levels get one line in the Method.
C60/C83      Method itemised, one takeaway per item, no prose under Results.
C62          the chapter opener tells the reader what each section does.
C67          chapter 2 = the design space, before the evolution chapter.
C68/C69      Method and Results separated; the eight stations are named (glossary).
C70          the discovery-curve lead is the finding itself, and says why it matters.
C71          filer figure before the zones figure; zones takeaway names the rings, the shift
             2016-19 -> 2020-23 and the CVT · 5-6 split (Bell / Textron), all from tables.
C72/C73      the unit of the zones figure (C·U archetype) and why; the 2016-23 axis explained.
C75/C76/C78  five propulsion graphs -> one compact figure; the ducting table dropped.
C77          the label-field table comes before the archetypes (2.1 before 2.2).
"""
from __future__ import annotations

from typing import Dict, Optional

from . import sm_text_methods as _tm

CHAPTER = "2"

# ---------------------------------------------------------------------------------------------
# method constants mirrored from the code that runs, printed in the screens table
# ---------------------------------------------------------------------------------------------
#: "an archetype of five or more" and "5 % or more" — the two literals of
#: ``la_tables.archetype_levels`` behind the population and readable-shares screens
SCREEN_BIG = 5
SCREEN_SHARE = 0.05

# ---------------------------------------------------------------------------------------------
# the chapter opener (C62: say what the section will do; C67: why it comes first)
# ---------------------------------------------------------------------------------------------
CHAPTER_TEXT = (
    "Chapter 3 asks whether eVTOL designs converge. That question needs two things first: what a "
    "design is, and where the designs sit today. This chapter supplies both, in three steps.\n\n"
    "- **2.1 — what a design is made of.** The label fields are read one at a time, to find the "
    "few that tell one aircraft from another; the propulsion, where most of the variety lies, is "
    "read per architecture class.\n"
    "- **2.2 — how designs are grouped.** The fields that vary are combined into **archetypes**, "
    "and the levels of detail at which every later count is made are fixed — among them the "
    "Lift + Cruise family that the dominant-design test of chapter 3 reads.\n"
    "- **2.3 — where designs concentrate.** The archetypes are placed on a map of where the "
    "recent aircraft sit and how many firms file them, and the record is asked whether new "
    "archetypes are still appearing.\n\n"
    "Every result of chapter 3 — a share that grows, a design that dominates or does not, a "
    "class that settles — is a statement about archetypes at a named level, so it cannot be read "
    "before this chapter. The propulsion vocabulary the chapter uses comes first.\n"
)

# ---------------------------------------------------------------------------------------------
# Method blocks
# ---------------------------------------------------------------------------------------------
#: the propulsion vocabulary, without the paragraph about the retired word: in this document
#: "group" is used for boom groups only, and the history of the word is not the reader's concern
_GLOSSARY = (_tm.GLOSSARY_TABLE.split("*Retired word:*")[0].rstrip()
             + "\n\n*Group* is used only for a boom group.\n")

#: the chapter head: the opener, the vocabulary 2.1 needs and the box 2.2 needs. A chapter opens
#: a fresh page, so the two long definitions cost no blank space here, where inside a Method
#: block they pushed the block to the next page and left half a page empty before it.
CHAPTER_TEXT = CHAPTER_TEXT + "\n" + _GLOSSARY

METHOD: Dict[str, str] = {
    "2.q1": (
        "#### Method\n\n"
        "Two measurements answer this question; the terms are those of the propulsion "
        "vocabulary above.\n\n"
        "- **Which label fields tell designs apart — {sm_here_a2_d3_selected_fields}.** For each "
        "field of the codebook: how many of the unique aircraft answer it, how many different "
        "answers it takes, and the **top share** — the share of the aircraft that give its most "
        "common answer. A field whose top answer covers nearly every aircraft cannot tell two "
        "designs apart; fields with a top share of {sm_d3_drop_share} or more are left out of the "
        "table and named under it. Two fields are derived: the propulsive units per aircraft, in "
        "the five unit bands, and the **stations carrying units** — how many of the eight stations "
        "hold at least one propulsive unit, read from each station's own unit count. Both are read "
        "on the {units_n} aircraft with a propulsion record. Source: human labelling.\n"
        "- **How the propulsion varies — {sm_here_sm_propulsion_compact}.** The propulsion is where "
        "the variety lies, so it is drawn per architecture class, because the class fixes much of "
        "it (every Tilt Rotor tilts) and a count over all classes would describe the class mix "
        "rather than the designs.\n"
        "  - *(i), top:* the propulsive units of every aircraft of each class — one dot per "
        "aircraft, the bar the middle half, the ring the **median**, which is not pulled by the "
        "few aircraft with very many units.\n"
        "  - *(i), bottom:* the share of each class's aircraft that carries each arrangement "
        "feature — a tilting unit, fixed and tilting units together, a ducted unit, more than "
        "eight units, units on exactly two stations.\n"
        "  - *(ii):* ducting per unit band. The bar is the share of the band's aircraft with at "
        "least one ducted unit; its split says how much of each of those aircraft is ducted "
        "(every unit, half or more, under half); the diamond counts **units** instead of "
        "aircraft — the share of all the band's units that sit in a duct.\n"
        "  - *Unit:* the unique aircraft, because an arrangement belongs to a design and a design "
        "filed several times is still one design. Source: human labelling (the propulsion record "
        "of each station: units, tilt and duct per propulsor type).\n"
    ),

    "2.q2": (
        # 2026-09-26 follow-up (author): shortened from sm_text_methods.ARCHETYPE_METHOD — the
        # screens table became two sentences, the band definition and "the T of C·W·T" went (the
        # glossary and 2.3 carry them); the definition, the level names and F's rationale stay
        "#### Method\n\n"
        "**What an archetype is.** A design described by a few chosen labels: write each "
        "aircraft as its answers on those labels, and two aircraft share an archetype when every "
        "answer is the same. The set of labels chosen is the **level**; each aircraft has exactly "
        "one archetype at each level.\n\n"
        "**How it is written.** A level is named by letters for the labels it combines — **C** "
        "class, **W** wings, **T** tilt, **U** propulsive-unit band — and an archetype is written "
        "in words, one label after another:\n\n"
        "- *Lift + Cruise · one wing · no tilting propulsor* — level **C·W·T**: the class is Lift "
        "+ Cruise, the aircraft has one wing, and none of its propulsors tilts.\n"
        "- *Tilt Rotor · 1-3 units* — level **C·U**: the class is Tilt Rotor and the aircraft has "
        "one to three propulsive units.\n\n"
        "**Why these levels.** {sm_arch_levels} levels were built, combining the class with wings, "
        "booms, tail, tilt and the unit band; the finer ones run to {sm_arch_max} archetypes, "
        "most holding one or two aircraft, where no share can be read. Four screens, fixed before "
        "the levels were compared, keep a level only if it adds to the class (at least twice as "
        "many archetypes as classes), leaves few aircraft alone (at most {sm_screen_frag}), puts "
        "most aircraft in archetypes of {sm_screen_big} or more (at least {sm_screen_pop}) and has "
        "at least {sm_screen_readable} archetypes of {sm_screen_share} or more. {sm_arch_pass} "
        "levels pass: C·W·T, C·U and class + wings + booms, which is set aside because booms carry "
        "rotors but do not decide how the aircraft lifts or cruises. The class alone fails only "
        "the first screen, because it *is* the class, and is kept as the reference.\n\n"
        "| level | combines | why it is read |\n"
        "|---|---|---|\n"
        "| **C** — Class | the architecture class | the reference: how the aircraft passes from "
        "hover to cruise |\n"
        "| **C·W·T** — Class + wings + tilt | class · number of wings · whether any propulsor "
        "tilts | the two further decisions that change how the aircraft flies; the level the "
        "dominant-design test was written at |\n"
        "| **C·U** — Class + units | class · propulsive-unit band | the decision distributed "
        "electric propulsion moves: a four-rotor Lift + Cruise against a twelve-rotor one |\n"
        "| **F** — Lift + Cruise family | the class, with the family below as one archetype | "
        "one design across two classes; **post hoc** |\n\n"
        "**The Lift + Cruise family (F)** holds every Lift + Cruise aircraft **plus every CVT "
        "aircraft whose tilting part is a rotor set and which has no tilting wing** — "
        "{sm_fam_b_n} aircraft; every other aircraft keeps its class.\n\n"
        "- *Why these two:* both are a fixed wing that never tilts, carrying rotors spread over "
        "the airframe; they differ only in whether cruise thrust comes from dedicated propellers "
        "(Lift + Cruise) or from tilting some of the rotors forward (this CVT). The criterion is "
        "morphological similarity of the airframe.\n"
        "- *Not used:* CVT with units on booms grouped with Lift + Cruise (a structural and "
        "redundancy criterion), and Tilt Rotor with CVT (grouped because something tilts).\n"
        "- *Post hoc:* defined after the class and archetype readings had been seen; no result on "
        "it is a pre-registered test, and it is marked post hoc wherever it appears.\n\n"
        "**What is measured — {sm_here_la_archetype_levels_brief}.** Per level: the archetypes, "
        "the aircraft alone in theirs, ¹D (box below) and the largest "
        "archetype with its share. *Unit:* the unique aircraft, each written once per level, "
        "over the **whole corpus and all years** (no time windows), because the question is what "
        "the level does to the count; ¹D is therefore not rarefied. Shares per priority window "
        "are chapter 3. Source: human labelling.\n\n"
        + _tm.DIVERSITY_BOX
    ),

    "2.q3": (
        "#### Method\n\n"
        "**The archetype read here is C·U**, the class with its propulsive-unit band: it splits "
        "every class by the field that varies most (2.1), and yields the most archetypes large "
        "enough to read — {sm_lv_cu_big} of five aircraft or more, against {sm_lv_cwt_big} at "
        "C·W·T, whose tilt answer inside the large classes is fixed by the class. The figures "
        "write an archetype short (*SLC 9+* = Lift + Cruise with nine units or more; class "
        "abbreviations in the legend of {sm_here_zones}).\n\n"
        "- **Who files each large archetype — {sm_here_sm_archetype_filers}.** **Distinct filers "
        "per aircraft** = the archetype's filers divided by its aircraft; a filer is a firm, and "
        "an individual inventor's patent is its own filer. 1.00 means every aircraft has a "
        "different filer; a low value is the trace of one firm's line of variants. Read first, "
        "because it says whether a large archetype on the map is many designers' choice or one "
        "firm filing again. *Unit:* the C·U archetype with {sm_zones_min} aircraft or more "
        "({sm_zones_big_n}); on fewer, one filer moves the ratio by a large step. Sources: human "
        "labelling, PatSeer (applicant).\n"
        "- **Where the recent aircraft concentrate — {sm_here_zones}.** *Unit:* the C·U archetype "
        "with five aircraft or more ({sm_zones_n}).\n"
        "  - *(i)* Left to right: the archetype's share of the aircraft with a priority year from "
        "2016 to 2023 — from the take-off of filing (chapter 1) to the last year whose "
        "publication lag has run; these two windows hold {sm_win_active_n} aircraft "
        "({sm_win_active_share}) against {sm_ch2_w1_n} and {sm_ch2_w2_n} in the two before, so "
        "the axis says where today's designers are. Bottom to top: distinct filers per aircraft. "
        "▲ first seen in 2016 or later, ▼ not seen after 2019, ● throughout. The **crowded core** "
        "(solid ring: above the median share, below the median filers per aircraft) and the "
        "**empty rim** (dashed: at or below the median share) are set by the two medians, the "
        "grey crosshairs, not by eye.\n"
        "  - *(ii)* Each archetype's aircraft per window, largest first; the orange bar marks the "
        "column by which half the window's aircraft are reached. As the order is the total over "
        "all windows, the count is repeated with each window in its own order. Sources: human "
        "labelling, PatSeer (applicant; priority date).\n"
        "- **Whether the space is still opening — {sm_here_discovery_curve}.** *Why it matters:* "
        "a space that no longer produces new kinds of design can only converge among those it "
        "holds. The distinct archetypes seen are counted as the aircraft accumulate in priority "
        "order, at C, C·U and C·W·T (shaded: the spread over orderings inside a year; dotted: a "
        "fully random order). Read are the new archetypes of the last 100 aircraft against what "
        "a random 100 brings, and the Chao1 estimate of what is still unseen, from the archetypes "
        "seen once and twice — combinations of existing labels not yet drawn, a floor and never "
        "a forecast. *Unit:* the unique aircraft with a priority year up to 2023, whose "
        "publication lag has run. Sources: human labelling, PatSeer (priority date).\n"
    ),
}

#: nothing under "Results and discussion" beyond the items: every point is a takeaway (C60, C83)
RESULTS: Dict[str, str] = {"2.1": "", "2.2": "", "2.3": ""}

# ---------------------------------------------------------------------------------------------
# items (decided by the coordinator, 2026-09-26)
# ---------------------------------------------------------------------------------------------
ITEMS = {
    "2.1": dict(figures=["sm_propulsion_compact"], tables=["a2_d3_selected_fields"]),
    "2.2": dict(figures=[], tables=["la_archetype_levels_brief"]),
    "2.3": dict(figures=["sm_archetype_filers", "zones", "discovery_curve"], tables=[]),
}

FIGURE_CAPTIONS = {
    "sm_propulsion_compact": "propulsive units and how each architecture class arranges them, "
                             "and ducting per propulsive-unit band",
    "sm_archetype_filers": "distinct filers per aircraft for the largest C·U archetypes (class + "
                           "propulsive-unit band); Combined Vectored Thrust with 5-6 units "
                           "(CVT · 5-6) is marked, and CVT · 4 beside it",
    "zones": "the C·U archetypes with five aircraft or more: where the recent aircraft "
             "concentrate and how many filers stand behind them, then the aircraft of each "
             "archetype per priority window",
    "discovery_curve": "distinct archetypes seen as the aircraft accumulate in priority order, "
                       "at three levels of detail, against a random order",
}

TABLE_CAPTIONS = {
    "a2_d3_selected_fields": "The label fields that tell one design from another: per field, "
                             "the unique aircraft that answer it, the number of different "
                             "answers, the share of the most common answer and the most common "
                             "answers with their aircraft",
    "la_archetype_levels_brief": "The four archetype levels this document reads (what each "
                                 "combines is in the Method): how many archetypes it yields, how "
                                 "many aircraft stand alone, the effective number of archetypes ¹D and the largest "
                                 "archetype with its share over the whole corpus, all years together. F, the Lift + "
                                 "Cruise family, was defined post hoc",
}

COLUMNS = {
    "la_archetype_levels_brief": ["level", "archetypes",
                                  "aircraft alone in their archetype", "effective number ¹D",
                                  "largest archetype", "its share"],
}

NOT_CORE = {
    "sm_propulsion_compact": "the propulsion pages compacted into one figure on the author's "
                             "ruling (C75, C76, C78, 2026-09-26)",
    "la_archetype_levels_brief": "the archetype levels the document reads, with the family F as "
                                 "one more level and readable names (C48, C49, C54)",
}

# ---------------------------------------------------------------------------------------------
# print hooks: readable labels in every chapter-2 table (C47, C49, C61)
# ---------------------------------------------------------------------------------------------
_FIELD_NAMES = {
    "propulsor units per aircraft": "propulsive units per aircraft (band)",
    "propulsor groups per aircraft": "stations carrying units per aircraft",
}


def _answers(cell) -> str:
    """``"1 380 · 2 185"`` -> ``"1: 380 · 2: 185"`` — an answer and its aircraft kept apart."""
    parts = []
    for item in str(cell).split(" · "):
        head, _, n = item.rpartition(" ")
        parts.append(f"{head}: {n}" if head and n.isdigit() else item)
    return " · ".join(parts)


def _print_fields(t):
    t = t.copy()
    if "name" in t.columns:
        t["name"] = t["name"].map(lambda v: _FIELD_NAMES.get(str(v), v))
    if "most common answers" in t.columns:
        t["most common answers"] = t["most common answers"].map(_answers)
    return t.rename(columns={"name": "field", "answered": "aircraft answering",
                             "answers": "different answers", "top_share": "top share",
                             "most common answers": "most common answers: aircraft"})


def _print_levels(t):
    return t.rename(columns={"aircraft alone in their archetype": "aircraft alone",
                             "effective number ¹D": "¹D"})


PRINT = {
    "a2_d3_selected_fields": _print_fields,
    "la_archetype_levels_brief": _print_levels,
}

# ---------------------------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------------------------
_LV = "la_archetype_levels_brief"
_FS = "la_archetype_filer_split"

NUMBERS = {
    # 2.2 — the levels read (sm_open.archetype_levels_brief)
    "sm_lv_n": dict(table=_LV, where=("level id", "A0"), col="aircraft", fmt="int"),
    "sm_lv_c_arch": dict(table=_LV, where=("level id", "A0"), col="archetypes", fmt="int"),
    "sm_lv_c_eff": dict(table=_LV, where=("level id", "A0"), col="effective number ¹D", fmt="1f"),
    "sm_lv_c_top_share": dict(table=_LV, where=("level id", "A0"), col="its share", fmt="pct"),
    "sm_lv_cu_arch": dict(table=_LV, where=("level id", "A0c"), col="archetypes", fmt="int"),
    "sm_lv_cu_eff": dict(table=_LV, where=("level id", "A0c"), col="effective number ¹D", fmt="1f"),
    "sm_lv_cu_big": dict(table=_LV, where=("level id", "A0c"), col="archetypes of five or more",
                         fmt="int"),
    "sm_lv_cu_top_share": dict(table=_LV, where=("level id", "A0c"), col="its share", fmt="pct"),
    "sm_lv_cwt_arch": dict(table=_LV, where=("level id", "A1t"), col="archetypes", fmt="int"),
    "sm_lv_cwt_eff": dict(table=_LV, where=("level id", "A1t"), col="effective number ¹D",
                          fmt="1f"),
    "sm_lv_cwt_big": dict(table=_LV, where=("level id", "A1t"), col="archetypes of five or more",
                          fmt="int"),
    "sm_lv_cwt_top": dict(table=_LV, where=("level id", "A1t"), col="largest archetype", fmt="raw"),
    "sm_lv_cwt_top_share": dict(table=_LV, where=("level id", "A1t"), col="its share", fmt="pct"),
    "sm_lv_f_eff": dict(table=_LV, where=("level id", "family_b"), col="effective number ¹D",
                        fmt="1f"),
    "sm_lv_f_share": dict(table=_LV, where=("level id", "family_b"), col="its share", fmt="pct"),
    # the finest levels built, for the one line the Method gives them (C48)
    "sm_arch_max": dict(table="la_archetype_levels", how="max", col="archetypes", fmt="int"),
    "sm_eff_max": dict(table="la_archetype_levels", how="max", col="effective number ¹D",
                       fmt="int"),
    "sm_fam_b_n": dict(table="la_family_dd", where=("id", "b"), col="aircraft", fmt="int"),
    # 2.3 — who files the large archetypes (sm_open.archetype_filer_split)
    "sm_cvt56_top": dict(table=_FS, where=("archetype", "CVT · 5-6"), col="largest filer",
                         fmt="raw"),
    "sm_cvt56_top_n": dict(table=_FS, where=("archetype", "CVT · 5-6"), col="its aircraft",
                           fmt="int"),
    "sm_cvt56_ones": dict(table=_FS, where=("archetype", "CVT · 5-6"),
                          col="filers holding one aircraft", fmt="int"),
    "sm_tr13_fpa": dict(table=_FS, where=("archetype", "TR · 1-3"), col="filers per aircraft",
                        fmt="2f"),
    "sm_tr13_top": dict(table=_FS, where=("archetype", "TR · 1-3"), col="largest filer",
                        fmt="raw"),
    "sm_tr13_top_n": dict(table=_FS, where=("archetype", "TR · 1-3"), col="its aircraft",
                          fmt="int"),
    "sm_tr13_air": dict(table=_FS, where=("archetype", "TR · 1-3"), col="aircraft", fmt="int"),
    # 2.3 — the two early windows, against which the 2016-23 axis is read (C73)
    "sm_ch2_w1_n": dict(table="a2_d9_windows", where=("window", "<= 2011"),
                        col="unique aircraft", fmt="int"),
    "sm_ch2_w2_n": dict(table="a2_d9_windows", where=("window", "2012-15"),
                        col="unique aircraft", fmt="int"),
    # 2.3 — the discovery curve at C·U (the C·W·T numbers are sm_index's own)
    "sm_disc_a0c_new100": dict(table="la_discovery_estimators", where=("level", "A0c"),
                               col="new in the last 100 aircraft", fmt="1f"),
    "sm_disc_a0c_exp100": dict(table="la_discovery_estimators", where=("level", "A0c"),
                               col="new in the last 100, random order", fmt="1f"),
    "sm_disc_a1t_found": dict(table="la_discovery_estimators", where=("level", "A1t"),
                              col="share of richness found", fmt="pct"),
    # 2.1 — the median ducted units of the ducting aircraft at 1-3 units
    "sm_duct13_med": dict(table="la_duct_count", where=("propulsive units", "1-3"),
                          col="median ducted units (ducted aircraft)", fmt="int"),
    "sm_d3_wings_top": dict(table="a2_d3_selected_fields", where=("name", "number of wings"),
                            col="top_share", fmt="pct"),
    "sm_d3_stations_top": dict(table="a2_d3_selected_fields",
                               where=("name", "propulsor groups per aircraft"),
                               col="top_share", fmt="pct"),
}


def _num(x) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _pct(x: float) -> str:
    from . import la_index as _la
    return _la._tk_fmt(x, "pct")


def _split_share(cell: str):
    """``"SLC · 9+ 10%"`` -> (``"SLC · 9+"``, 0.10)."""
    head, _, tail = str(cell).strip().rpartition(" ")
    if tail.endswith("%"):
        try:
            return head, float(tail[:-1]) / 100.0
        except ValueError:
            pass
    return str(cell).strip(), None


def _ch2_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    """The chapter-2 numbers the spec grammar cannot say, each read from a built table:

    * the rings and the half-marks of the zones figure, by the rules ``la_figures.fig_zones``
      draws them with (the medians of the two axes; the column past which half a window's
      aircraft are reached), plus the same half-mark with each window in its own order;
    * the largest C·U archetype of 2020-23 and its share, from ``la_top_archetypes``;
    * when the twelfth class appeared on the discovery curve;
    * the screens' lines, from ``la_tables.ARCHETYPE_SCREENS``;
    * the readable name of the largest archetype on the map.
    """
    import numpy as np
    import pandas as pd
    out: Dict[str, str] = {}
    t = tables or {}

    z = t.get("la_zones")
    if z is not None and "share 2016-23" in z.columns:
        zz = z[pd.to_numeric(z["filers 2016-23"], errors="coerce") > 0]
        sh = pd.to_numeric(zz["share 2016-23"], errors="coerce")
        fp = pd.to_numeric(zz["filers per aircraft"], errors="coerce")
        mx, my = sh.median(), fp.median()
        core = zz[(sh > mx) & (fp < my)]
        rim = zz[sh <= mx]
        out["sm_z_core_n"] = str(len(core))
        out["sm_z_rim_n"] = str(len(rim))
        out["sm_z_core_share"] = _pct(float(pd.to_numeric(core["share 2016-23"]).sum()))
        out["sm_z_rim_share"] = _pct(float(pd.to_numeric(rim["share 2016-23"]).sum()))
        lead = core.assign(_s=pd.to_numeric(core["share 2016-23"])).sort_values("_s", ascending=False)
        names = [_tm.archetype_label(a, "A0c") for a in lead["archetype"].head(3)]
        if len(names) == 3:
            out["sm_z_core_lead"] = f"{names[0]}, {names[1]} and {names[2]}"
        for w, k in (("2016-19", "1619"), ("2020-23", "2023")):
            c = pd.to_numeric(z[w], errors="coerce").fillna(0).to_numpy(dtype=float)
            out[f"sm_z_half_{k}"] = str(int(np.searchsorted(np.cumsum(c) / c.sum(), 0.5)) + 1)
            s = np.sort(c)[::-1]
            out[f"sm_z_half_own_{k}"] = str(int(np.searchsorted(np.cumsum(s) / s.sum(), 0.5)) + 1)
        top = z.loc[pd.to_numeric(z["aircraft"], errors="coerce").idxmax(), "archetype"]
        out["sm_zones_top_label"] = _tm.archetype_label(top, "A0c")

    ta = t.get("la_top_archetypes")
    if ta is not None and "top 1" in ta.columns:
        row = ta[ta["level"].astype(str).eq("A0c") & ta["window"].astype(str).eq("2020-23")]
        if len(row):
            key, share = _split_share(row["top 1"].iloc[0])
            out["sm_cu_top_2023"] = _tm.archetype_label(key, "A0c")
            if share is not None:
                out["sm_cu_top_2023_share"] = _pct(share)

    cv = t.get("la_discovery_curve")
    if cv is not None and "archetypes (date order)" in cv.columns:
        a0 = cv[cv["level"].astype(str).eq("A0")].copy()
        a0["_n"] = pd.to_numeric(a0["aircraft"], errors="coerce")
        a0["_d"] = pd.to_numeric(a0["archetypes (date order)"], errors="coerce")
        a0 = a0.sort_values("_n")
        final = a0["_d"].max()
        hit = a0[a0["_d"] >= final - 1e-9].iloc[0]
        out["sm_disc_a0_full_n"] = str(int(hit["_n"]))
        out["sm_disc_a0_full_year"] = str(hit["priority year reached"]).split(".")[0]
        out["sm_disc_a0_after"] = str(int(a0["_n"].max() - hit["_n"]))

    try:
        from . import la_tables as _ltb
        lines = {name: line for name, _u, _r, line, _d in _ltb.ARCHETYPE_SCREENS}
        out["sm_screen_frag"] = _pct(lines["fragmentation"])
        out["sm_screen_pop"] = _pct(lines["population"])
        out["sm_screen_readable"] = f"{int(lines['readable shares'])}"
        out["sm_screen_big"] = f"{SCREEN_BIG}"
        out["sm_screen_share"] = _pct(SCREEN_SHARE)
    except Exception:
        pass

    # the closing section of the brief points at the propulsion figure by its old name
    # (``{sm_here_atlas_units}``); that figure is now the compact one of 2.1 (C75)
    try:
        from . import sm_index as _sm
        if "atlas_units" not in _sm.HERE_REF and "sm_propulsion_compact" in _sm.HERE_REF:
            out["sm_here_atlas_units"] = _sm.HERE_REF["sm_propulsion_compact"]
    except Exception:
        pass
    return out


NUMBER_FUNCS = [_ch2_numbers]

# ---------------------------------------------------------------------------------------------
# takeaways (rule 3: specific bold leads; no repeat of the Method)
# ---------------------------------------------------------------------------------------------
TAKEAWAY = {
    "sm_propulsion_compact":
        "**No number of propulsive units is standard, but the arrangement nearly is.** The median "
        "aircraft carries {units_median} units and the five bands hold {bin_r03}, {bin_r4}, "
        "{bin_r56}, {bin_r78} and {bin_r9} aircraft, while {grp2} of the {units_n} aircraft with "
        "a propulsion record put their units on exactly two stations. (ii) **Ducting is two "
        "designs, not one more or less common design**: {sm_duct_13} of the aircraft at 1-3 "
        "units duct, {sm_duct_78} at 7-8 and {sm_duct_9} at 9 or more. At nine units or more a "
        "ducting aircraft ducts a median of {sm_duct9_med} units and {sm_duct9_units} of the "
        "band's units sit in a duct — an array of ducted fans; at 1-3 units it ducts a median "
        "of {sm_duct13_med}, a small ducted set rather than an array. Across the bands {sm_ductc_all} of "
        "the ducting aircraft duct every unit they carry: a duct is chosen for the whole "
        "aircraft, not for one rotor",

    "a2_d3_selected_fields":
        "**Two fields carry most of the variety — the tail and the number of propulsive units: "
        "their most common answers hold only {tk_emptype} and {tk_units_top} of the aircraft.** "
        "The other fields each have a clear leading answer: a fuselage that does not move between "
        "hover and cruise ({tk_fuskin}), one wing ({sm_d3_wings_top}), units on two stations "
        "({sm_d3_stations_top}); the landing gear's top answer, *unknown* "
        "({tk_gear_unknown}), is a gap of the drawings, not a design. Left out because their top "
        "answer holds {sm_d3_drop_share} or more: {sm_d3_dropped}. The archetypes of 2.2 are "
        "built from the class and these varying fields",

    "la_archetype_levels_brief":
        "**The level of detail, not the corpus, sets how many designs there are.** The same "
        "aircraft are {sm_lv_c_arch} classes that behave like {sm_lv_c_eff} equally common ones, "
        "{sm_lv_cwt_arch} archetypes at C·W·T (¹D {sm_lv_cwt_eff}) and {sm_lv_cu_arch} at C·U "
        "(¹D {sm_lv_cu_eff}). The largest single design at any level is the Lift + Cruise family "
        "F, with {sm_lv_f_share} of the whole corpus (all years) against {sm_lv_c_top_share} for Lift + Cruise "
        "alone; at C·U the largest archetype holds {sm_lv_cu_top_share}. Any statement about "
        "convergence is therefore a statement about a level, and chapter 3 names it every time",

    "sm_archetype_filers":
        "**Combined Vectored Thrust with 5-6 units is the one large archetype that leans on one "
        "firm: {sm_cvt56_top} holds {sm_cvt56_top_n} of its {sm_cvt56_air} aircraft, and "
        "{sm_cvt56_ones} other filers hold one each.** That split gives it {sm_cvt56_filers} "
        "filers, {sm_cvt56_fpa} per aircraft, the lowest of the {sm_zones_big_n} archetypes with "
        "{sm_zones_min} aircraft or more, against {sm_cvt4_fpa} for Combined Vectored Thrust · 4 "
        "units. So its "
        "growth is partly one firm's line of variants on top of an ordinary spread of single "
        "filers. The same firm is the largest filer of Tilt Rotor with 1-3 units too, with "
        "{sm_tr13_top_n} of {sm_tr13_air}, yet that archetype still rests on {sm_tr13_fpa} filers "
        "per aircraft: every other large archetype is held by a crowd",

    "zones":
        "**The recent aircraft sit in a crowded core of {sm_z_core_n} archetypes, most archetypes "
        "sit in an empty rim, and from 2016-19 to 2020-23 the aircraft moved toward the core.** "
        "(i) The core — {sm_z_core_lead} in the lead — holds {sm_z_core_share} of the 2016-23 "
        "aircraft; the {sm_z_rim_n} archetypes of the rim hold {sm_z_rim_share} between them. "
        "Below the median filers per aircraft does not mean one firm's: the largest archetype, "
        "{sm_zones_top_label}, has {sm_zones_top_air} aircraft from {sm_zones_top_filers} filers, "
        "and the one archetype of the core that leans on a single firm is Combined Vectored "
        "Thrust · 5-6 units ({sm_here_sm_archetype_filers}). (ii) Half of the 2016-19 aircraft "
        "sit in the {sm_z_half_1619} largest archetypes, half of the 2020-23 aircraft in the "
        "{sm_z_half_2023} largest; with each window in its own order it is {sm_z_half_own_1619} "
        "against {sm_z_half_own_2023}, so the shift is not an effect of the column order. It is "
        "a concentration, not a winner: the largest archetype of 2020-23, "
        "{sm_cu_top_2023}, holds {sm_cu_top_2023_share} of that window. Of the {sm_zones_n} "
        "archetypes, {sm_zones_persist} are present throughout, {sm_zones_new} are new since 2016 "
        "and {sm_zones_fading} have disappeared after 2019",

    "discovery_curve":
        "**The kinds of eVTOL are settled while their detailed designs are not: no new class has "
        "appeared in the last {sm_disc_a0_after} aircraft, yet new wing-and-tilt combinations still "
        "appear faster than chance.** The twelfth class had arrived by aircraft number "
        "{sm_disc_a0_full_n} (priority {sm_disc_a0_full_year}). At C·U the last 100 aircraft brought "
        "{sm_disc_a0c_new100} new archetype against {sm_disc_a0c_exp100} by chance, and "
        "{sm_disc_a0c_unseen} is estimated still unseen: complete for practical purposes. At "
        "C·W·T they brought {sm_disc_a1t_new100} against {sm_disc_a1t_exp100}, and the "
        "{sm_disc_a1t_obs} archetypes seen are {sm_disc_a1t_found} of the {sm_disc_a1t_est} "
        "estimated. For chapter 3 this means the classes compete as a closed set, while at the "
        "level of wings and tilt the space is still being explored",
}

# ---------------------------------------------------------------------------------------------
# the Answer box
# ---------------------------------------------------------------------------------------------
ANSWER = (
    "**An eVTOL design is an architecture class plus a propulsion layout. The twelve classes are "
    "settled; inside them the number of propulsive units varies freely, the recent aircraft "
    "crowd into a small core of archetypes filed by many firms, and new combinations of wings "
    "and tilt still appear.**\n\n"
    "- **The variety is in the propulsion.** The tail and the propulsive-unit count have the "
    "weakest leading answers ({tk_emptype} and {tk_units_top} of the aircraft); the median aircraft carries "
    "{units_median} units, spread almost evenly over the five bands, while {grp2} of {units_n} "
    "aircraft put their units on exactly two stations.\n"
    "- **Ducting is two designs.** At 1-3 units a ducting aircraft ducts a median of "
    "{sm_duct13_med} units — a small ducted set; at nine or more it ducts {sm_duct9_med} and "
    "{sm_duct9_units} of the band's units sit in a duct — a fan array.\n"
    "- **How many designs there are depends on the level read.** {sm_lv_c_arch} classes "
    "(¹D {sm_lv_c_eff}), {sm_lv_cwt_arch} archetypes at C·W·T, {sm_lv_cu_arch} at C·U; the "
    "post-hoc Lift + Cruise family F is the largest single design at any level, with "
    "{sm_lv_f_share} of the whole corpus, all years together.\n"
    "- **The recent aircraft concentrate, without a winner.** A core of {sm_z_core_n} C·U "
    "archetypes holds {sm_z_core_share} of the 2016-23 aircraft; half of 2020-23 sits in "
    "{sm_z_half_2023} archetypes against {sm_z_half_1619} for 2016-19, yet the largest holds "
    "{sm_cu_top_2023_share}. The core is filed by crowds of firms, except Combined Vectored "
    "Thrust with 5-6 units, where {sm_cvt56_top} holds {sm_cvt56_top_n} of {sm_cvt56_air}.\n"
    "- **Closed at the class, open below it.** No new class in the last {sm_disc_a0_after} "
    "aircraft; at C·W·T the last 100 aircraft brought {sm_disc_a1t_new100} new archetypes "
    "against {sm_disc_a1t_exp100} by chance."
)

#: C77: the label fields are read before the figure built on them (coordinator, 2026-09-26)
TABLES_FIRST = {"2.1"}
