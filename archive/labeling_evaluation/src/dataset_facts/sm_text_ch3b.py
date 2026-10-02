"""Chapter 3 of the brief, sections 3.3 and 3.4 (2026-09-26, the chapter-2/3 review).

Written to BRIEF_REVISION_RULES.md from the author's Word comments C62-C66 (inside a class) and
C79-C95 (drivers) of REVIEW_2026-09-26_ch2_docx_comments.txt. Loaded by ``sm_index`` through
``CHAPTER_MODULES`` after ``sm_text_ch3`` (which owns CHAPTER = "3", the opener, 3.1, 3.2 and the
Answer); this module sets neither CHAPTER nor ANSWER and hands the coordinator
:data:`ANSWER_BULLET` to splice into the chapter Answer.

The data are ``sm_open.ch3b_tables`` (registered in ``sm_open.build_all``):
``la_class_configs_brief`` / ``la_class_config_mix`` (both rule sets; ``sm_open.CLASS_RULES_SET``
chooses the printed one), ``la_driver_windows``, ``la_sets_per_unit_brief`` and
``la_driver_links``. Every number below is a placeholder computed in :func:`_ch3b_numbers` from
those tables (or from ``la_trace_trends`` / ``a2_d9_windows``), never typed.

SWITCHING THE RULES. ``sm_open.CLASS_RULES_SET = "current"`` redraws the figure and re-reads
every share, but the 3.3 takeaway names the configurations of the PROPOSED rules (lift units on
booms, tilting sets on two stations, rotors tilting with the fixed units on booms); under the
current rules those placeholders print "–" and the takeaway must be rewritten.

Comment map
-----------
C62      3.3 opens on what the section compares (Method, first paragraph).
C63      the rules as a table in the Method (class | configuration = | why | possible), chosen
         after the shares under earlier rules were seen, justified by what physically separates
         two designs of the class, not by the share.
C64      3.3 is not a dominant-design condition (neither 1 nor 3): said in the Method.
C65      "configurations per aircraft" explained, and why panel (ii) now draws the composition.
C66      ``la_class_configs_own`` is no longer printed.
C79/C84  the verdict table reworded: where each trace moved (ρ, p), the drivers it goes WITH and
         AGAINST in plain words, and what that means (print hook ``_print_verdicts``).
C80/C81  mean against median, and "never pooled", in the Method.
C82      "tilting set" everywhere; the tilting-set panel folded into the trajectory; early windows
         faded behind a line and labelled "few aircraft".
C83/C86/C87/C94  3.4 compacted: no observation prose, one itemised takeaway per item.
C85      no how-to-read line (chapter 3 is a Method/Results chapter).
C88      the duct leaving CVT is told with the tilting-set move, as one story (trajectory iii).
C89      the drivers are named (Method table; verdict table; takeaways).
C90      "type" defined in the Method.
C91      the unclear correlation panel replaced: units by tilting sets and ducting by boom layout
         are panels (ii) and (iii) of the trajectory figure, each with its test.
C92      the trajectory figure (``sm_driver_trajectory``).
C93      booms as a small trace (``sm_driver_traces`` (i)).
C95      "so the cost drivers win" withdrawn: the per-unit fall fits cost, distributed propulsion
         and redundancy alike.

2026-09-28, L comments (round 2 on chapter 3)
L9   "never pooled": one concrete example on the record's own shares (Tilt Rotor falls, Lift +
     Cruise rises, the pooled tilting-set curve stays flat).
L10  trajectory panel (iii) split into (iii) the boom share and (iv) the ducted share per boom
     layout, lines named at their ends, no filled/hollow code; old (iv) is now (v).
L11  la_sets_per_unit_brief deleted from 3.4 (items, caption, columns, print hook, takeaway);
     its per-unit fall and per-aircraft trend are in the sm_driver_trajectory takeaway.
L12  the author's CVT sentence kept on the boom evidence, backed with the trace numbers and
     tied to F; the duct part corrected (CVT falls below Lift + Cruise, not toward it).
"""
from __future__ import annotations

import re
from typing import Dict, Optional

# ---------------------------------------------------------------------------------------------
# fold the two children of 3.4 into it (the interface block of sm_index: "fold or empty them as
# the compaction needs"). Their items move to 3.4 (ITEMS below) and their headings — "Four
# observations …", "Do tilting joints fall (cost) …" — go, because a Method/Results chapter
# prints no observation headings (rules §2) and the second title states the claim C95 withdrew.
# sm_index renumbers the items after every chapter module has loaded.
# ---------------------------------------------------------------------------------------------
FOLD_CHILDREN = ("3.4.obs", "3.4.answer")


def _fold_children() -> None:
    import sys
    sm = sys.modules.get(f"{__package__}.sm_index")
    if sm is None or not hasattr(sm, "NODES"):
        return
    sm.NODES[:] = [n for n in sm.NODES if n["id"] not in FOLD_CHILDREN]


_fold_children()


# ---------------------------------------------------------------------------------------------
# Method blocks
# ---------------------------------------------------------------------------------------------
METHOD: Dict[str, str] = {
    "3.q3": (
        "#### Method\n\n"
        "**What is compared.** 3.2 asked whether one design takes over the whole field. This "
        "section asks the same question one class at a time: inside Lift + Cruise, Tilt Rotor, "
        "CVT, Tilt Wing and Multirotor, do the aircraft settle on one layout?\n\n"
        "**Configuration.** An aircraft written on the few labels that tell two aircraft of the "
        "*same* class apart; the labels the class already fixes are left out (every Tilt Rotor "
        "tilts; no Lift + Cruise does). The rules were **chosen after the shares under earlier "
        "rules had been seen, after those shares were seen, not before**. Each is fixed by what physically separates two "
        "designs of the class, not by the share it produces:\n\n"
        "| class | configuration = | why these labels tell its designs apart | possible |\n"
        "|---|---|---|---|\n"
        "| Lift + Cruise | where the lift propulsor units sit (on booms, on the wing, on the body) and "
        "whether they are stowed in cruise (retract or fold) | the lift set is dead weight and "
        "drag in cruise: what carries it, and whether it is hidden, are the class's two layout "
        "decisions | {sm3b_cc_slc_K} |\n"
        "| Tilt Rotor | one tilting set · two or more in one place · two or more in two or more "
        "places | how the tilting thrust is split: one set, several sets in one place (front "
        "and rear rotors on the same booms), or sets fore and aft (canard and wing, wing and "
        "tail) | {sm3b_cc_tr_K} |\n"
        "| CVT | what tilts (rotors, a wing, or both) and where the fixed propulsor units sit: on booms, "
        "elsewhere, none | the class mixes tilting and fixed thrust; what tilts and what carries "
        "the fixed part is its layout | {sm3b_cc_cvt_K} |\n"
        "| Tilt Wing | one wing, or two or more · propulsive-unit band | unchanged | "
        "{sm3b_cc_tw_K} |\n"
        "| Multirotor | booms or none · propulsive-unit band | unchanged | {sm3b_cc_mr_K} |\n\n"
        "- *The unit band* is left out of the three rewritten rules: it is read on its own (C·U "
        "in chapter 2, the drivers in 3.4), and inside a rule it multiplied each layout by up to "
        "five for a reason that is not the layout.\n"
        "- *Possible* is the number of configurations the rule allows. An aircraft whose record "
        "leaves the rule unanswered (a tilt that was not recorded) is kept as a configuration of "
        "its own and is not counted among them: {sm3b_cc_gaps} aircraft.\n\n"
        "**What is measured: {sm_here_sm_class_configs}.** Per class and complete priority "
        "window:\n\n"
        "- *(i)* the **share of the class in its most common configuration**, with, at its "
        "2020-23 end, how many of the possible configurations are observed;\n"
        "- *(ii)* for the three rewritten classes, the whole **composition**: every "
        "configuration's share of the class, stacked, the configuration that leads in 2020-23 at "
        "the bottom. The number of blocks is the number of distinct configurations; the bottom "
        "block is what (i) reads whenever the 2020-23 leader also leads the window.\n"
        "- *Why not configurations per aircraft.* The earlier panel (ii) drew distinct "
        "configurations divided by aircraft: 1.0 when every aircraft is its own configuration, "
        "low when many aircraft share a few. It can never exceed possible configurations divided "
        "by aircraft, so under a rule with three to nine configurations it falls as a window "
        "grows whether or not the designs converge. Tilt Rotor uses {sm3b_cc_tr_11_k} "
        "configurations among {sm3b_cc_tr_11_n} aircraft up to 2011 ({sm3b_cc_tr_11_cpa} per "
        "aircraft) and {sm3b_cc_tr_23_k} among {sm3b_cc_tr_23_n} in 2020-23 "
        "({sm3b_cc_tr_23_cpa}): the ratio halves with no change in how many layouts are in use. "
        "The composition shows the configurations without that artefact.\n\n"
        "**How it is read.**\n\n"
        "- *Convergence is a change across windows under one rule*: a share that rises toward "
        "the whole class. The level of a share is not compared between classes or rule sets, "
        "because a rule with fewer possible configurations gives a larger leading share by "
        "construction (Tilt Rotor's rule allows {sm3b_cc_tr_K}, CVT's {sm3b_cc_cvt_K}).\n"
        "- *Robustness:* the reading is repeated on the earlier rules, which carried the unit "
        "band in every class.\n"
        "- *Not a dominant-design condition.* Condition 1 asks whether one archetype holds more "
        "than half of **all** the aircraft of a period; a layout that holds half of one class is "
        "a concentration inside the class, not condition 1. Condition 3 measures how alike all "
        "the aircraft are on every labelled field; this measures one class on its own few "
        "labels. What the reading adds to the test is where change happens: in the era frame of "
        "3.2, change inside a class that is settling is incremental.\n\n"
        "*Unit:* the unique aircraft of the class with a complete priority year, because a "
        "layout belongs to a design and a design filed several times is still one design; a "
        "window with fewer than {sm3b_min_cell} aircraft of the class is not drawn, and the two "
        "early windows, which hold {sm3b_win_11_n} and {sm3b_win_15_n} aircraft of all classes "
        "against {sm3b_win_19_n} and {sm3b_win_23_n}, are drawn faded. Source: human labelling "
        "(class; wing, boom and propulsor cards).\n"
    ),

    "3.q4": (
        "#### Method\n\n"
        "**Driver and trace.** A *design driver* is a cause of design change: a technology that "
        "moved, a physical limit that did not, a requirement, a cost. A driver is never written "
        "in a patent. If it acts, it leaves a **trace**: a labelled feature that moves over the "
        "years in the direction the driver predicts. The drivers considered:\n\n"
        "| kind | drivers |\n"
        "|---|---|\n"
        "| A1 technological | regime transition (from hover to wing-borne flight); distributed "
        "propulsion and rotor control |\n"
        "| A2 physical | hover load path; wing structural and aeroelastic limits; cruise "
        "stability and control; flow interference and drag |\n"
        "| B requirement | mission range and speed; payload; occupant presence; failure "
        "tolerance; community noise; operating environment |\n"
        "| C life-cycle cost | development and certification; production; maintenance |\n\n"
        "A physical limit (A2) does not move with the years; it predicts that two labels go "
        "together, not a trend, so an A2 driver never makes a trace rise or fall.\n\n"
        "**What a trace is.** One label read against the priority year: a **share** of the "
        "aircraft (units on booms, a ducted unit) or a **count per aircraft**. Three counts carry "
        "this section; all are defined in the propulsion vocabulary at the head of chapter 2:\n\n"
        "- *propulsive units*: the rotors, propellers and fans that give lift or thrust;\n"
        "- *propulsor types*: sets of like propulsor units in one place: a Lift + Cruise with lift "
        "rotors on booms and a pusher on the fuselage has two; a tilt rotor that adds a tilting "
        "set on its tail goes from one to two;\n"
        "- *tilting sets*: the parts that swivel their units between hover and cruise as one: a "
        "tilting propulsor type, a tilting wing panel, a tilting boom group or a tilting tail each "
        "count one.\n\n"
        # 2026-09-28 (L9): one concrete example of what pooling does, on the record's own shares
        "**Read inside each class, never pooled.** *Pooled* means every class thrown into one "
        "curve. A pooled curve mixes two movements: change *inside* designs, and change in "
        "*which* designs are filed. Tilting sets show the difference. Inside Tilt Rotor they "
        "rise, from {sm_t_joints_tr_first} to {sm_t_joints_tr_last} per aircraft on average (p "
        "{sm_t_joints_tr_p}), and they rise inside CVT too. Over the same windows Tilt Rotor "
        "falls from {tk_tr_w1} to {tk_tr_w4} of all aircraft, while Lift + Cruise, which has no "
        "tilting set, rises from {tk_slc_w1} to {tk_slc_w4}. Pooled, the aircraft with many "
        "tilting sets become fewer and those with none become more, so the pooled curve stays "
        "flat ({sm_t_joints_all_first} to {sm_t_joints_all_last}, p {sm_t_joints_all_p}) although "
        "the sets rose inside both tilting classes. Reading each class on its own removes that mixing: a "
        "class's curve moves only when its own aircraft change. A driver acts on how an aircraft "
        "is built, so it is looked for one class at a time; a pooled row is printed only as "
        "this contrast.\n\n"
        "**The test.** Spearman ρ between each aircraft's own priority year and the trace, over "
        "every aircraft of the class with a value and a priority year up to 2023: *rises* or "
        "*falls* at p < 0.05, *flat* (no trend detected) otherwise; read on {sm3b_trend_min} "
        "aircraft or more (statistics box).\n\n"
        "**The years read.** The figures group the years in four-year windows; the two early "
        "windows hold {sm3b_win_11_n} and {sm3b_win_15_n} aircraft against {sm3b_win_19_n} and "
        "{sm3b_win_23_n} in the two after, so they are drawn faded behind a vertical line and "
        "labelled *few aircraft*, and no figure is read on them. The test does not use windows: "
        "it runs on every year, so an early aircraft counts once, like any other. A window is "
        "drawn only with {sm3b_min_cell} aircraft of the class or more.\n\n"
        "**The centre: mean or median.** The median is used where a few extreme aircraft would "
        "carry a mean: propulsive units, where a handful of hull arrays carry tens of units. The "
        "mean is used for small whole-number counts (tilting sets, propulsor types) and for "
        "tilting sets per unit, because a median of 1 or 2 (or of ½) stands still while the mix "
        "of aircraft moves under it. A share is a share of the aircraft that answer the label.\n\n"
        "**What is shown.**\n\n"
        "- **{sm_here_sm_driver_trajectory}**: the move of the tilting classes. *(i)* each "
        "class's centre per window, mean tilting sets against median propulsive units, joined by "
        "arrows (Lift + Cruise, Tilt Rotor, CVT: the three largest classes, and the two that "
        "tilt); *(ii)* Tilt Rotor, median units by the number of tilting sets, all years; "
        "*(iii)* CVT, the share of its aircraft with units on booms; *(iv)* CVT, the share with "
        "a ducted unit inside each boom layout, one line for the aircraft with units on booms "
        "and one for those without, each with its own trend test; each point is labelled with "
        "the layout's aircraft over all CVT of the window (layout / all), and a share is drawn only "
        "when the layout holds 5 aircraft or more of that window; *(v)* tilting sets per "
        "propulsive unit, with its test.\n"
        "- **{sm_here_sm_driver_traces}**: two traces in every class: units carried on booms, "
        "and a ducted unit.\n"

        "- **{sm_here_la_driver_verdicts}**: every trace that moves in at least one class: "
        "where it moved, with ρ and p, and the drivers it goes **with** (it moved the way they "
        "predict) and **against** (it moved the other way). *Overdetermined:* several drivers "
        "predict the same move, and the labelled dataset cannot say which. ●: the traces this section "
        "reads.\n\n"
        "*Unit:* the unique aircraft, because a trace is a property of a design, and a design "
        "filed five times is still one design. *What a trace can say:* a move in the predicted "
        "direction is *consistent* with its driver; it does not prove it. Source: human "
        "labelling (class; wing, boom and propulsor cards).\n"
    ),
}

#: nothing under "Results and discussion" beyond the items: every point is a takeaway (C83, C86)
RESULTS: Dict[str, str] = {"3.3": "", "3.4": ""}

# ---------------------------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------------------------
ITEMS = {
    "3.3": dict(figures=["sm_class_configs"], tables=[]),
    # 2026-09-28 (L11): la_sets_per_unit_brief no longer printed; its per-unit fall and its
    # per-aircraft trend are in the sm_driver_trajectory takeaway (panel v draws the same rows)
    "3.4": dict(figures=["sm_driver_trajectory", "sm_driver_traces"],
                tables=["la_driver_verdicts"]),
}

FIGURE_CAPTIONS = {
    "sm_class_configs": "how each architecture class spreads over its own configurations, per "
                        "priority window: (i) the share of the class in its most common "
                        "configuration; (ii) the composition of Lift + Cruise, Tilt Rotor and CVT, "
                        "the configuration that leads in 2020-23 at the bottom. Rules chosen after the shares were seen; "
                        "windows before 2016 hold few aircraft",
    "sm_driver_trajectory": "the move of the tilting classes: (i) each class's centre per window "
                            "in tilting sets and propulsive units; (ii) Tilt Rotor units by "
                            "tilting sets; (iii) the share of CVT with units on booms; (iv) the "
                            "share of CVT with a ducted unit, one line per boom layout, each "
                            "named at its end; (v) tilting sets per propulsive unit",
    "sm_driver_traces": "two traces per architecture class and priority window: (i) the share "
                        "of aircraft that carry units on booms; (ii) the share with a ducted "
                        "unit",
}

TABLE_CAPTIONS = {
    "la_driver_verdicts": "The traces that move inside at least one class: where each moved, "
                          "and the drivers it goes with and against",
}

COLUMNS = {
    # the hook rebuilds the printed columns from these (``_print_verdicts``)
    "la_driver_verdicts": ["trace", "importance", "what moved", "drivers that predict it",
                           "verdict class"],
}

NOT_CORE = {
    "sm_driver_trajectory": "the trajectory the author asked for (C92), with the two links of the "
                            "one move folded in (C88, C91)",
    "sm_driver_traces": "the boom and duct traces per class, the boom trace asked for (C93)",
    "sm_class_configs": "within-class convergence on the proposed per-class rules, chosen after the shares were seen (C63)",
}

# ---------------------------------------------------------------------------------------------
# print hooks
# ---------------------------------------------------------------------------------------------
_CLASS_WORD = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT", "TW": "Tilt Wing",
               "MR": "Multirotor"}

#: the trace names as the text uses them (the vocabulary of chapter 2)
_TRACE_WORD = {
    "tilting joint groups (median)": "tilting sets per aircraft",
    "propulsive units (median)": "propulsive units per aircraft",
    "propulsor types (median)": "propulsor types per aircraft",
    "stations carrying units (median)": "stations carrying units per aircraft",
    "fuselage kinematics not fixed": "a body that tilts or rotates",
    "units carried on booms": "units carried on booms",
    "booms present": "booms present",
    "wing units at the leading edge": "wing units at the leading edge",
    "a pusher unit": "a pusher unit",
    "no tail surface": "no tail surface",
    "a ducted unit": "a ducted unit",
    "ground contact drawn": "landing gear drawn",
}

#: the traces 3.4 reads, printed bold in the verdict table (the Method says so)
_READ_HERE = {"tilting joint groups (median)", "propulsive units (median)", "units carried on booms",
              "a ducted unit", "propulsor types (median)"}

#: what a trace's verdict means, in plain words (C84). ``{n}`` is the number of drivers.
_READING = {
    "opposed drivers": "drivers disagree; it moved with those under *goes with*",
    "overdetermined": "{n} drivers predict it; the labelled dataset cannot say which acts",
    "single driver": "one driver predicts it, and it moved that way",
    "moved against every driver that predicts a direction":
        "moved against the only direction any driver predicts",
    "moves, but only fixed physical drivers predict this trace":
        "no driver predicts a direction; only physical limits bear on it",
    "mixed by class": "classes move in opposite directions; no driver reading",
}

#: the readings this section adds to the built verdict, per trace
_READING_EXTRA = {
    "tilting joint groups (median)": "; per propulsive unit it falls (trajectory figure, v)",
    "a ducted unit": "; in CVT it follows the boom layout (trajectory figure, iv)",
    "propulsor types (median)": "; in Tilt Rotor the added type is a second tilting set",
}

_MOVE = re.compile(r"(rises|falls) in (\w+) \([^()]*?ρ ([+-]\d\.\d\d), (p [^)]*)\)")
_DRIVER = re.compile(r"\s*(.+?) \((A1|A2|B|C)\)\s*([+-])?\s*$")


def _where_moved(text: str) -> str:
    parts = [f"{mv} in {_CLASS_WORD.get(c, c)} (ρ {rho}, {p})" for mv, c, rho, p in _MOVE.findall(text)]
    m = re.search(r"pooled over the five classes: (\w+)", text)
    head = "; ".join(parts) if parts else "no trend detected in any class"
    return head + (f"; pooled: {m.group(1)}" if m else "")


def _direction(text: str) -> str:
    moves = {mv for mv, _c, _r, _p in _MOVE.findall(text)}
    if moves == {"rises"}:
        return "+"
    if moves == {"falls"}:
        return "-"
    return "mixed"


def _drivers(cell: str):
    out = []
    for item in str(cell).split(","):
        m = _DRIVER.match(item)
        if m:
            out.append((m.group(1).strip(), m.group(2), m.group(3) or ""))
    return out


def _print_verdicts(t):
    t = t.copy()
    rows = []
    for _, r in t.iterrows():
        raw_trace = str(r.get("trace", "")).strip()
        name = _TRACE_WORD.get(raw_trace, raw_trace)
        if raw_trace in _READ_HERE:        # the first column prints bold anyway: mark with ●
            name = f"● {name}"
        moved = str(r.get("what moved", ""))
        d = _direction(moved)
        drv = _drivers(r.get("drivers that predict it", ""))
        with_, against = [], []
        for dname, kind, sign in drv:
            if not sign or d == "mixed":
                continue
            word = f"{dname} ({'more' if sign == '+' else 'fewer'})"
            (with_ if sign == d else against).append(word)
        vc = str(r.get("verdict class", "")).strip()
        reading = _READING.get(vc, vc).format(n=len(drv)) + _READING_EXTRA.get(raw_trace, "")
        if vc.startswith("moves, but only fixed"):
            reading += " (" + ", ".join(n for n, _k, _s in drv) + ")"
        rows.append({"trace": name, "where it moved (every year to 2023)": _where_moved(moved),
                     "goes with (driver: what it predicts)": "; ".join(with_) or "—",
                     "goes against (driver: what it predicts)": "; ".join(against) or "—",
                     "what it means": reading})
    import pandas as pd
    return pd.DataFrame(rows)


def _print_sets(t):
    t = t.copy()
    if "measure" in t.columns:
        t["measure"] = t["measure"].map(lambda v: {"tilting sets per aircraft": "per aircraft",
                                                   "tilting sets per propulsive unit":
                                                       "per propulsive unit"}.get(str(v), v))
    return t.rename(columns={"rho": "ρ", "measure": "tilting sets"})


PRINT = {"la_driver_verdicts": _print_verdicts}

# ---------------------------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------------------------
_W = {"<= 2011": "11", "2012-15": "15", "2016-19": "19", "2020-23": "23"}

#: configurations the 3.3 takeaway names, per class: (slug, configuration) — proposed rules
_MIX_NAMED = {
    "SLC": [("booms", "lift units on booms")],
    "TR": [("one", "one tilting set"), ("onest", "two or more tilting sets, on one station"),
           ("twost", "two or more tilting sets, on two or more stations")],
    "CVT": [("rb", "rotors tilt · fixed units on booms"),
            ("re", "rotors tilt · fixed units elsewhere")],
}

#: the trace readings the takeaways quote that ``sm_index._TRACE_POINTS`` does not carry
_TRACES_EXTRA = [("onb_slc", "units carried on booms", "SLC", "pct"),
                 ("onb_tr", "units carried on booms", "TR", "pct"),
                 ("onb_cvt", "units carried on booms", "CVT", "pct"),
                 ("onb_tw", "units carried on booms", "TW", "pct"),
                 ("onb_mr", "units carried on booms", "MR", "pct"),
                 ("duct_slc", "a ducted unit", "SLC", "pct")]


def _f(x) -> Optional[float]:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if v != v else v


def _pct(x) -> str:
    from . import la_index as _la
    v = _f(x)
    return "–" if v is None else _la._tk_fmt(v, "pct")


def _p(x) -> str:
    v = _f(x)
    if v is None:
        return "–"
    return "< 0.001" if v < 0.001 else f"{v:.3f}" if v < 0.01 else f"{v:.2f}"


def _rho(x) -> str:
    v = _f(x)
    return "–" if v is None else f"{v:+.2f}"


def _num_g(x, nd: int = 1) -> str:
    v = _f(x)
    if v is None:
        return "–"
    return f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.{nd}f}"


_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _frac_words(v: float, long: bool = False) -> str:
    """A ratio said as the nearest simple fraction, for the reader of a per-propulsor-unit rate:
    0.50 -> "one for every two", 0.39 -> "two for every five" (denominators up to five). The
    long form names what is counted: "one tilting set for every two propulsor units"."""
    from fractions import Fraction
    f = Fraction(v).limit_denominator(5)
    a, b = _WORDS.get(f.numerator, str(f.numerator)), _WORDS.get(f.denominator, str(f.denominator))
    if long:
        sets = "tilting set" if f.numerator == 1 else "tilting sets"
        return f"{a} {sets} for every {b} propulsor units"
    return f"{a} for every {b}"


def _ch3b_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    import pandas as pd
    from . import la_tables as _lt
    from . import sm_open as _so
    out: Dict[str, str] = {}
    t = tables or {}
    rs = _so.CLASS_RULES_SET
    other = "current" if rs == "proposed" else "proposed"

    out["sm3b_trend_min"] = str(_lt.TREND_MIN)
    out["sm3b_min_cell"] = str(_lt.MIN_CELL)
    win = t.get("a2_d9_windows")
    if win is not None:
        for w, k in _W.items():
            r = win[win["window"].astype(str).eq(w)]
            if len(r):
                out[f"sm3b_win_{k}_n"] = _num_g(r["unique aircraft"].iloc[0])

    cc = t.get("la_class_configs_brief")
    if cc is not None:
        for code in _so.CH3B_CLASSES:
            c = code.lower()
            for set_, pre in ((rs, "sm3b_cc"), (other, "sm3b_ccx")):
                sub = cc[cc["rule set"].astype(str).eq(set_) & cc["code"].astype(str).eq(code)]
                if not len(sub):
                    continue
                if pre == "sm3b_cc":
                    K = _f(sub["possible configurations"].iloc[0])
                    out[f"{pre}_{c}_K"] = "—" if K is None else _num_g(K)
                for w, k in _W.items():
                    r = sub[sub["window"].astype(str).eq(w)]
                    if not len(r):
                        continue
                    r = r.iloc[0]
                    out[f"{pre}_{c}_{k}"] = _pct(r["share in it"])
                    if pre == "sm3b_cc":
                        out[f"{pre}_{c}_{k}_top"] = str(r["most common configuration"]) or "–"
                        out[f"{pre}_{c}_{k}_k"] = _num_g(r["distinct configurations"])
                        out[f"{pre}_{c}_{k}_n"] = _num_g(r["aircraft"])
                        v = _f(r["configurations per aircraft"])
                        out[f"{pre}_{c}_{k}_cpa"] = "–" if v is None else f"{v:.2f}"
        act = cc[cc["rule set"].astype(str).eq(rs)]
        out["sm3b_cc_gaps"] = _num_g(pd.to_numeric(act["aircraft outside the rule"],
                                                   errors="coerce").sum())

    mix = t.get("la_class_config_mix")
    if mix is not None:
        m = mix[mix["rule set"].astype(str).eq(rs)]
        for code, named in _MIX_NAMED.items():
            for slug, cfg in named:
                for w, k in _W.items():
                    r = m[m["code"].astype(str).eq(code) & m["window"].astype(str).eq(w)
                          & m["configuration"].astype(str).eq(cfg)]
                    key = f"sm3b_mix_{code.lower()}_{slug}_{k}"
                    out[key] = _pct(r["share"].iloc[0]) if len(r) else "0 %"
                    out[key + "_n"] = _num_g(r["aircraft"].iloc[0]) if len(r) else "0"

    dw = t.get("la_driver_windows")
    if dw is not None:
        fields = {"n": ("aircraft", "g"),
                  "sets": ("tilting sets (mean)", "1f"), "units": ("propulsive units (median)", "g"),
                  "onb": ("share with units on booms", "pct"), "duct": ("share with a ducted unit", "pct"),
                  "two": ("share with two or more tilting sets", "pct"),
                  "fixed": ("share with a fixed unit", "pct"),
                  "ductb": ("ducted share, units on booms", "pct"),
                  "ductnb": ("ducted share, no units on booms", "pct"),
                  "nb": ("aircraft, units on booms", "g"), "nnb": ("aircraft, no units on booms", "g")}
        for code in _so.CH3B_CLASSES:
            for w, k in _W.items():
                r = dw[dw["code"].astype(str).eq(code) & dw["window"].astype(str).eq(w)]
                if not len(r):
                    continue
                r = r.iloc[0]
                for slug, (col, fmt) in fields.items():
                    x = r.get(col)
                    out[f"sm3b_dw_{code.lower()}_{k}_{slug}"] = (
                        _pct(x) if fmt == "pct" else _num_g(x) if fmt == "g"
                        else ("–" if _f(x) is None else f"{_f(x):.1f}"))

    su = t.get("la_sets_per_unit_brief")
    if su is not None:
        for _, r in su.iterrows():
            c = str(r["code"]).lower()
            m = "unit" if "unit" in str(r["measure"]) else "ac"
            for w, k in _W.items():
                col = _lt.WIN_SHORT.get(w, w)
                v = _f(r.get(col))
                out[f"sm3b_spu_{c}_{m}_{k}"] = "–" if v is None else f"{v:.2f}"
                if v is not None and m == "unit":      # 2026-09-29 (T6): "about two for every five"
                    out[f"sm3b_spu_{c}_{m}_{k}_frac"] = _frac_words(v)
                    out[f"sm3b_spu_{c}_{m}_{k}_frac_long"] = _frac_words(v, long=True)
            out[f"sm3b_spu_{c}_{m}_rho"] = _rho(r["rho"])
            out[f"sm3b_spu_{c}_{m}_p"] = _p(r["p"])
            out[f"sm3b_spu_{c}_{m}_move"] = str(r["movement"])

    lk = t.get("la_driver_links")
    if lk is not None:
        for _, r in lk.iterrows():
            g = str(r["group"])
            if str(r["link"]).startswith("Tilt Rotor"):
                s = {"1": "1", "2": "2"}.get(g, "3")
                out[f"sm3b_lk_tr_{s}_med"] = _num_g(r["median"])
                out[f"sm3b_lk_tr_{s}_n"] = _num_g(r["aircraft"])
            else:
                s = {"units on booms": "b", "no units on booms": "nb"}.get(g, "all")
                out[f"sm3b_lk_cvt_{s}_rho"] = _rho(r["rho"])
                out[f"sm3b_lk_cvt_{s}_p"] = _p(r["p"])
                out[f"sm3b_lk_cvt_{s}_move"] = str(r["movement"])
                out[f"sm3b_lk_cvt_{s}_share"] = _pct(r["mean"])
                out[f"sm3b_lk_cvt_{s}_n"] = _num_g(r["aircraft"])

    tt = t.get("la_trace_trends")
    if tt is not None:
        for key, trace, code, fmt in _TRACES_EXTRA:
            r = tt[tt["trace"].astype(str).str.strip().eq(trace) & tt["code"].astype(str).eq(code)]
            if not len(r):
                continue
            r = r.iloc[0]
            out[f"sm3b_t_{key}_first"] = _pct(r["first value"])
            out[f"sm3b_t_{key}_last"] = _pct(r["2020-23 value"])
            out[f"sm3b_t_{key}_rho"] = _rho(r["rho"])
            out[f"sm3b_t_{key}_p"] = _p(r["p"])
            out[f"sm3b_t_{key}_move"] = str(r["movement"])
            out[f"sm3b_t_{key}_fw"] = _lt.WIN_SHORT.get(str(r["first window"]), str(r["first window"]))

    vd = t.get("la_driver_verdicts")
    if vd is not None and "what moved" in vd.columns:
        moving = vd[vd["what moved"].astype(str).str.contains(r"\brises\b|\bfalls\b", regex=True)]
        out["sm3b_v_moving"] = str(len(moving))
        out["sm3b_v_all"] = str(len(vd))
    return out


NUMBER_FUNCS = [_ch3b_numbers]

# 2026-09-27: the chapter-3 "External comparison" bullet (author's request) -- whether the AAM
# Reality Index firms' disclosed funding follows family F more than the corpus does. Data from
# sm_open.external_tables (la_ext_f_funding: the "total" row over the disclosed-funding firms)
# and from the family level of sm_open.archetype_levels_brief (la_archetype_levels_brief,
# level_id "family_b"), which already carries F's share of the whole corpus.
NUMBERS = {
    "sm_ext_f_weighted": dict(table="la_ext_f_funding", where=("kind", "total"),
                              col="funding-weighted F share", fmt="pct"),
    "sm_ext_f_plain": dict(table="la_ext_f_funding", where=("kind", "total"),
                           col="share in family F", fmt="pct"),
    "sm_ext_f_corpus": dict(table="la_archetype_levels_brief", where=("level id", "family_b"),
                            col="its share", fmt="pct"),
}

# ---------------------------------------------------------------------------------------------
# takeaways (rule 3: specific bold leads; itemised; no repeat of the Method)
# ---------------------------------------------------------------------------------------------
TAKEAWAY = {
    # one paragraph each: the renderer prints a takeaway as one italic line, so a markdown list
    # inside it would break; the items are keyed by a bold class name or a panel mark instead
    "sm_class_configs":
        # 2026-09-29 (decision document, T6): the year CVT's leading layout changes, said plainly
        "**No class converges on one layout; what changes is which layout leads.** "
        "In **Lift + Cruise** the same layout leads in every window, lift propulsor units on "
        "booms, at {sm3b_cc_slc_11}, {sm3b_cc_slc_15}, {sm3b_cc_slc_19} and {sm3b_cc_slc_23} of "
        "the class, with {sm3b_cc_slc_23_k} of its {sm3b_cc_slc_K} configurations in use in "
        "2020-23: a stable layout just under half the class, there from the first window. "
        "**CVT** keeps about half of its aircraft in its leading layout, but the leader changes: "
        "up to 2016-19 it is tilting propulsors with the fixed propulsor units elsewhere on the "
        "airframe ({sm3b_mix_cvt_re_11}, {sm3b_mix_cvt_re_15} and {sm3b_mix_cvt_re_19} of the "
        "class), and in 2020-23 tilting propulsors with the fixed propulsor units on booms "
        "({sm3b_mix_cvt_rb_23}; {sm3b_mix_cvt_rb_11_n} and {sm3b_mix_cvt_rb_15_n} aircraft in "
        "the two early windows): the boom layout of Lift + Cruise with a tilting set added. "
        "**Tilt Rotor** spreads out: one tilting set falls from {sm3b_mix_tr_one_11} of the class "
        "to {sm3b_mix_tr_one_23}; the three layouts are almost even in 2016-19 "
        "({sm3b_mix_tr_onest_19_n}, {sm3b_mix_tr_one_19_n} and {sm3b_mix_tr_twost_19_n} "
        "aircraft), and tilting sets in two or more places lead in 2020-23 with "
        "{sm3b_mix_tr_twost_23}. **Tilt Wing** and **Multirotor** fall to {sm3b_cc_tw_23} and "
        "{sm3b_cc_mr_23}. On the earlier rules every share also falls or stays flat: Lift + "
        "Cruise {sm3b_ccx_slc_11} to {sm3b_ccx_slc_23}, Tilt Rotor {sm3b_ccx_tr_11} to "
        "{sm3b_ccx_tr_23}, CVT {sm3b_ccx_cvt_11} to {sm3b_ccx_cvt_23}",

    "sm_driver_trajectory":
        "**Inside the two tilting classes the change is one move toward more rotors: Tilt Rotor "
        "adds a second tilting set, CVT moves its fixed units onto booms, and in both the "
        "propulsive units follow; Lift + Cruise, the class that grows, moves on neither axis.** "
        "(i) Tilt Rotor's centre goes from {sm3b_dw_tr_11_sets} tilting sets and "
        "{sm3b_dw_tr_11_units} units up to 2011 to {sm3b_dw_tr_23_sets} and "
        "{sm3b_dw_tr_23_units} in 2020-23, CVT's from {sm3b_dw_cvt_11_sets} and "
        "{sm3b_dw_cvt_11_units} to {sm3b_dw_cvt_23_sets} and {sm3b_dw_cvt_23_units}; over every "
        "year the units rise in both (ρ {sm_t_units_tr_rho} and {sm_t_units_cvt_rho}, p "
        "{sm_t_units_tr_p} and {sm_t_units_cvt_p}), and so do the sets (ρ {sm_t_joints_tr_rho} "
        "and {sm_t_joints_cvt_rho}). (ii) In Tilt Rotor the units come with the sets (a "
        "median of {sm3b_lk_tr_1_med} units with one tilting set, {sm3b_lk_tr_2_med} with two, "
        "{sm3b_lk_tr_3_med} with three or more), and what is added is a tilting set, not a fixed "
        "one: in 2020-23 {sm3b_dw_tr_23_two} of the tilt rotors carry two or more tilting sets "
        "and {sm3b_dw_tr_23_fixed} any fixed unit, so the tilt rotor stays a tilt rotor. "
        "(iii, iv) The duct leaves CVT in two steps: the layout moves onto booms (the share "
        "with units on booms rises from {sm3b_dw_cvt_11_onb} to {sm3b_dw_cvt_23_onb}) while the "
        "CVT without them keep their ducts ({sm3b_dw_cvt_19_ductnb} and {sm3b_dw_cvt_23_ductnb} "
        "since 2016, trend {sm3b_lk_cvt_nb_move}); then the boom layout sheds its own, from "
        "{sm3b_dw_cvt_19_ductb} in 2016-19 to {sm3b_dw_cvt_23_ductb} in 2020-23 (ρ "
        "{sm3b_lk_cvt_b_rho}, p {sm3b_lk_cvt_b_p}). This corrects the earlier reading that the "
        "layout alone explains the fall of CVT ducting ({sm_t_duct_cvt_first} to "
        "{sm_t_duct_cvt_last}). (v) Per aircraft the tilting sets rise in Tilt Rotor (ρ "
        "{sm3b_spu_tr_ac_rho}, p {sm3b_spu_tr_ac_p}), but per propulsive unit they fall, from "
        "{sm3b_spu_tr_unit_11} up to 2011, about {sm3b_spu_tr_unit_11_frac_long}, to "
        "{sm3b_spu_tr_unit_23} in 2020-23, about {sm3b_spu_tr_unit_23_frac} (ρ "
        "{sm3b_spu_tr_unit_rho}, p {sm3b_spu_tr_unit_p}): the propulsor units grow faster than "
        "the tilting sets; in CVT the per-unit ratio has no trend (p {sm3b_spu_cvt_unit_p}). "
        "The aircraft carry more tilting sets only as they carry more propulsors, so the rise "
        "per aircraft does not show tilting growing against the cost drivers. The fall per unit "
        "fits lower cost per propulsor, distributed propulsion and failure tolerance alike, and "
        "the labelled dataset cannot say which of the three a firm weighed",

    "sm_driver_traces":
        "**Units moved onto booms in CVT, Tilt Wing and Multirotor; ducting fell in CVT alone.** "
        "(i) Units on booms rise in CVT ({sm3b_t_onb_cvt_first} to {sm3b_t_onb_cvt_last}, "
        "p {sm3b_t_onb_cvt_p}: {sm3b_dw_cvt_11_nb} of its {sm3b_dw_cvt_11_n} aircraft up to "
        "2011, {sm3b_dw_cvt_23_nb} of {sm3b_dw_cvt_23_n} in 2020-23), Tilt Wing ({sm3b_t_onb_tw_first} in {sm3b_t_onb_tw_fw} to "
        "{sm3b_t_onb_tw_last}, p {sm3b_t_onb_tw_p}) and Multirotor ({sm3b_t_onb_mr_first} to "
        "{sm3b_t_onb_mr_last}, p {sm3b_t_onb_mr_p}); in Lift + Cruise ({sm3b_t_onb_slc_first} to "
        "{sm3b_t_onb_slc_last}, p {sm3b_t_onb_slc_p}) and Tilt Rotor ({sm3b_t_onb_tr_first} to "
        "{sm3b_t_onb_tr_last}, p {sm3b_t_onb_tr_p}) no trend is detected. The boom is the one "
        "airframe feature that spreads across classes, as distributed propulsion (A1) predicts; "
        "the wing does not move (two or more wing panels: no trend detected in any class). "
        "(ii) Ducting falls in CVT ({sm_t_duct_cvt_first} to {sm_t_duct_cvt_last}); in every "
        "other class no trend is detected",

    "la_driver_verdicts":
        "**Of the {sm3b_v_moving} traces that move inside a class, only the boom and place "
        "traces point to a single driver, distributed propulsion; the other moves this section "
        "reads do not single one out.** The unit count is overdetermined: distributed "
        "propulsion, failure tolerance and community noise all predict the rise; tilting sets "
        "went with regime transition and against the cost drivers on the raw count, a reading "
        "reversed per unit ({sm_here_sm_driver_trajectory}, v); ducting and the propulsor-type "
        "count moved against the only direction a driver gives (community noise predicts more "
        "ducting; development, certification and production cost predict fewer types)",
}

NO_TAKEAWAY: set = set()

# ---------------------------------------------------------------------------------------------
# the bullets for the chapter Answer (spliced in by the coordinator, into sm_text_ch3.ANSWER)
# ---------------------------------------------------------------------------------------------
ANSWER_BULLET = (
    # 2026-09-29 (decision document, S3, T6, T8): organised by sub-question; the year CVT's
    # leading layout changes and the layout definitions (3.3); the CVT boom counts and the
    # tilting-sets-per-propulsor-unit example (3.4); the closing interpretation, chapter-wide
    "[[3.3]]\n\n"
    "- **No class converges on one layout. What changes is which layout leads.** Lift + Cruise "
    "keeps its lift propulsor units on booms as the leading layout in every window, at just "
    "under half the class ({sm3b_cc_slc_23} in 2020-23); CVT keeps about half of its aircraft "
    "in its leading layout, but the leader changes: up to 2016-19 it is tilting propulsors with "
    "the fixed propulsor units elsewhere on the airframe ({sm3b_mix_cvt_re_11}, "
    "{sm3b_mix_cvt_re_15} and {sm3b_mix_cvt_re_19} of the class), and in 2020-23 tilting "
    "propulsors with the fixed propulsor units on booms ({sm3b_mix_cvt_rb_23}); Tilt Propulsor "
    "spreads from one tilting set ({sm3b_mix_tr_one_11} up to 2011) over three layouts, led in "
    "2020-23 by tilting sets in two or more places ({sm3b_mix_tr_twost_23}). Each layout is "
    "defined on fixed label fields, the same in every window: for Lift + Cruise, where the lift "
    "propulsor units sit and whether they stow in cruise; for CVT, what tilts and where the "
    "fixed propulsor units sit; for Tilt Propulsor, how many tilting sets there are and whether "
    "they sit in one place or several. These definitions were set after a first reading of the "
    "data, as F was.\n\n"
    "[[3.4]]\n\n"
    # 2026-09-28 (L12): the author's sentence, checked against la_driver_windows and
    # la_trace_trends. Booms: CVT's share rises to about Lift + Cruise's level, which has no
    # trend, so on booms CVT comes to look like Lift + Cruise (and its leading 2020-23 layout,
    # 3.3, is Lift + Cruise's boom layout with a tilting set added). Ducts: CVT's share falls
    # below Lift + Cruise's, so the duct is told as CVT's own change, not as a move toward it.
    "- **What moves inside the classes is one move toward more propulsors.** Tilt Propulsor "
    "adds a second tilting set and its median propulsor units go from {sm3b_dw_tr_11_units} to "
    "{sm3b_dw_tr_23_units}. CVT moves its fixed propulsor units onto booms, from "
    "{sm3b_t_onb_cvt_first} of its aircraft to {sm3b_t_onb_cvt_last} (p {sm3b_t_onb_cvt_p}), "
    "close to the {sm3b_t_onb_slc_last} of Lift + Cruise in 2020-23: of the "
    "{sm3b_dw_cvt_11_n} CVT aircraft up to 2011, {sm3b_dw_cvt_11_nb} carried propulsor units on "
    "booms; of the {sm3b_dw_cvt_23_n} in 2020-23, {sm3b_dw_cvt_23_nb} do. In morphology it "
    "becomes more like the Lift + Cruise aircraft, and this likeness is what motivated defining "
    "the family F (chapter 2 and 3.2). CVT also sheds its ducts ({sm_t_duct_cvt_first} to "
    "{sm_t_duct_cvt_last}), to below Lift + Cruise's {sm3b_t_duct_slc_last}. Lift + Cruise "
    "itself moves on neither booms nor ducts. Per propulsor unit the tilting sets fall (in Tilt "
    "Propulsor, from {sm3b_spu_tr_unit_11} up to 2011, about {sm3b_spu_tr_unit_11_frac_long}, "
    "to {sm3b_spu_tr_unit_23} in 2020-23, about {sm3b_spu_tr_unit_23_frac}: the propulsor units "
    "grow faster than the tilting sets), consistent with lower cost per propulsor, with "
    "distributed propulsion and with redundancy alike, which the labelled dataset cannot "
    "separate.\n\n"
    "**Why this can matter for the sector (an interpretation, not a finding).** The shared "
    "layout, a fixed wing with its propulsor units spread over the airframe, mostly on booms, "
    "is the airframe of distributed electric propulsion. Many propulsor units can carry "
    "redundancy, so that losing one need not end a flight, and that tolerance to failure weighs "
    "on safety and certification today. If the sector consolidates, it may consolidate on this "
    "layout while the functional allocation of thrust still differs between its members. The "
    "labelled dataset shows the layout, not these reasons."
)
