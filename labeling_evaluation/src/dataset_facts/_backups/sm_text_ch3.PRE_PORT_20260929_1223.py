"""Chapter 3 of the brief, sections 3.1 and 3.2 — "Evolution and dominant design" (2026-09-26).

Written to BRIEF_REVISION_RULES.md from the author's Word comments C41-C46 and C51-C61
(REVIEW_2026-09-26_ch2_docx_comments.txt). Sections 3.3 and 3.4 are ``sm_text_ch3b``; this module
owns the chapter opener, 3.1, 3.2 and the chapter Answer (whose last bullet is left for 3.3-3.4).
Loaded by ``sm_index`` through ``CHAPTER_MODULES``; the interface is the CHAPTER MODULES block at
the end of ``sm_index.py``. Every number is a placeholder read from a table (rule 1); the numbers
the spec grammar cannot say are computed in :func:`_ch3_numbers`, from the tables only.

Comment map
-----------
C41/C55      the three conditions in the Method, each with what moves it, so a reader can
             predict it; what grouping classes does to the test.
C43          3.1 has no prose under Results: the takeaways carry it.
C44-C46      the external check is the dated evtol.news directory, said plainly: what agrees
             (the Lift + Cruise / Vectored Thrust balance), what does not (Wingless, Hover Bikes),
             what cannot be checked (the Tilt Rotor crossover); the 63 unruled conflicts left out.
C51          the era frame (ferment / incremental change) in the Method, no results in it.
C52/C56      family F = definition (b) only, chosen on morphological similarity after the first
             readings; the alternatives in one line.
C53          condition 1 read per priority year; main base the aircraft with a patent in force,
             second base all aircraft; ``la_family_yearly`` + ``sm_family_yearly``.
C54          F is one more level of the test, beside C, C·W·T and C·U (``la_dd_levels``,
             ``sm_dd_conditions``).
C57          every met level-window drawn in red (``sm_dd_conditions``, ``sm_family_yearly``) and
             named in the verdict table (``la_dd_levels``).
C58/C59      no generated how-to-read; ``la_family_dd`` and its takeaway dropped.
C60          the reading of the verdict itemised (AFTER).
C61          (superseded by K26: ``la_top_archetypes`` no longer printed.)

2026-09-28, K comments (sm_text_ch3 / sm_text_methods / sm_figures)
K11 3.1 retitled neutrally (title itself lives in sm_index.SUBQ), victory words swept.
K12/K13 3.1 Method in five parts, outside check compacted, the directory's missing domain
             refinement stated and used in the takeaway (K14/K15, representativeness sentence).
K16-K21 3.2 Method in five parts; the Procedure walks the graphs in print order; "post hoc" ->
             "chosen after the first readings of the data"; the in-force base justified; the
             rarefaction reason in place; the Gower fields named; why C, C·U and F share a panel.
K23/K24 caveat on the 2022-23 fall; condition 2 compared across archetype sets.
K25/K26 ✓ / ✗ flags in the verdict table (``_flag``); la_top_archetypes dropped.
Author addition: morphology against functional allocation, in the Method, verdict and Answer.

2026-09-28, L comments (round 2 on chapter 3)
L1  sm_evtolnews_check shorter, with panel (iii): the balance per window, record beside
    directory, 95 % Wilson intervals and p (sm_figures); Method, caption and takeaway point to it.
N2  (2026-09-28) panel (iii) and the pooled balance test deleted; the takeaway reads the
    two mixes qualitatively and points to 1.3 for the class-level agreement.
L2  condition 2 says in place what the band is: the middle 95 % of the shuffled results.
L3  how the rarefaction sample is drawn ({sm_rare_draws}, read from the code).
L4  Gower's distance and Rao's Q defined in the box of 2.2 (sm_text_methods.DIVERSITY_BOX).
L5  condition 3 with the same bold lead and short sentences as conditions 1 and 2.
L6  the technological discontinuity is the literature's candidate (sm_text_methods).
L7  the two weightings said in the Method; the takeaway says why "main weighting only" matters.
L8  sm_dd_conditions: every tick label upright and centred on its own window (sm_figures).
"""
from __future__ import annotations

from typing import Dict, Optional

from . import sm_text_methods as _tm

CHAPTER = "3"

# ---------------------------------------------------------------------------------------------
# the chapter opener (C62 pattern: say what each section does; the units are chapter 2's)
# ---------------------------------------------------------------------------------------------
CHAPTER_TEXT = (
    "Chapter 2 described the design space as it stands. This chapter asks how it has moved over "
    "twenty years of filing, and whether it has settled on one design. Its units are the "
    "archetypes of chapter 2: every share, count and test below is a statement about archetypes "
    "in a named archetype set, **C** (class), **C·W·T** (class + wings + tilt), **C·U** (class + "
    "units) or **F**, the Lift + Cruise family.\n\n"
    "- **3.1: how the class mix moves across the windows.** The class mix per priority window, "
    "set against the one outside series that dates eVTOL aircraft by class: the evtol.news "
    "directory.\n"
    "- **3.2: whether there is a dominant design.** Three conditions of different kinds, in the "
    "four archetype sets, and the era of a technology cycle they place the sector in.\n"
    "- **3.3: whether designs converge inside each class.** Each class read on the labels that "
    "tell its own designs apart.\n"
    "- **3.4: what drives the changes inside the classes.** The propulsion traces over the "
    "priority years, read class by class.\n"
)

# ---------------------------------------------------------------------------------------------
# Method blocks
# ---------------------------------------------------------------------------------------------
METHOD: Dict[str, str] = {
    # 2026-09-28 (K12, K13): the five labelled parts; the outside check compacted; the
    # directory's missing domain refinement stated once, used in the takeaway
    "3.q1": (
        "#### Method\n\n"
        "**Objective.** How the share of each architecture class moves across the priority "
        "windows, and whether a public list of aircraft shows the same movement.\n\n"
        "**Data and unit of analysis.** {sm_here_atlas_arch_time} counts unique aircraft, because "
        "a design filed several times is one design, per four-year priority window (human "
        "labelling for the class, PatSeer for the priority date). {sm_here_sm_evtolnews_check} "
        "sets beside it the World eVTOL Aircraft Directory of the Vertical Flight Society "
        "(evtol.news, crawled 2026-09-17): {sm_evn_list} aircraft on five class lists, "
        "{sm_evn_dated} of them ({sm_evn_dated_share}) dated.\n\n"
        "**Procedure.** {sm_here_atlas_arch_time} (i) draws each window at 100 %, split by class; "
        "(ii) follows the five largest classes. Shares are read, never counts, since a share can "
        "fall while the count grows. Each directory aircraft is dated by its **development "
        "year**, the earliest year its own page documents (a programme start, an unveiling, a "
        "first flight), the counterpart of a priority year. Two independent readers (separate "
        "language-model instances given only the page's dated sentences) each named the dating "
        "sentence, and a script checked that it states the year: the {sm_evn_agreed} aircraft "
        "on which they agree are used, {sm_evn_notstated} have no dated sentence, and the "
        "{sm_evn_conflict} on which they disagree are left out until the author rules. The "
        "labelled dataset's twelve classes are folded onto the directory's five: Lift + Cruise stays; "
        "every class whose thrust tilts or is redirected (Tilt Propulsor, Tilt Wing, CVT, Tilt "
        "Body, Pitch-to-Cruise, Deflected Slipstream) is **Vectored Thrust**; Multirotor is "
        "Wingless; Rotorcraft and Stopped/Slowed Rotor Wing are Electric Rotorcraft; Hoverbike "
        "and Personal Flying Vehicle are Hover Bikes. {sm_here_sm_evtolnews_check} draws the "
        "folded mix of each source per window, (i) the labelled dataset and (ii) the directory.\n\n"
        "**Scientific grounds.** The two mixes are compared by reading, not by a test: the "
        "direction of each class and which of the two large classes is the larger, in the windows "
        "where both sources hold {sm_evn_min_n} dated aircraft or more. Whether the labelled "
        "dataset's classes agree with the aircraft actually built is tested aircraft by aircraft "
        "in 1.3, not here.\n\n"
        "**Assumptions and limits.** Four-year windows, because before 2016 a single year holds "
        "too few aircraft to carry twelve shares; the 2024-26 window is still filling and is not "
        "read. The directory counts announced aircraft, not patented ones, so what compares is "
        "the direction of each class and which of the two large ones is the larger, not how large "
        "each class is. "
        "The directory has no domain refinement like the labelled dataset's: its class lists also carry "
        "uncrewed aircraft (UAVs) and cargo drones, so its mix is not directly comparable in the "
        "small classes. Vectored Thrust pools Tilt Propulsor with CVT and Tilt Wing, so the "
        "crossover of Lift + Cruise over Tilt Propulsor cannot be checked against it.\n"
    ),

    # 2026-09-28 (K16-K21, and the author's morphology / operating-principle addition): the
    # five labelled parts; the Procedure walks the graphs in the order they print, each with
    # what it shows, how it is computed and when the condition is met
    "3.q2": (
        "#### Method\n\n"
        "**Objective.** Whether the sector has settled on a **dominant design**, the design most "
        "new products follow after a period of competing alternatives, after which change moves "
        "from the concept to its parts (Abernathy and Utterback, 1978). A design has two sides: "
        "its **morphology**, the arrangement (the form, number, size and placement of wings, booms "
        "and propulsor units), and its **functional allocation**, which components do which duty "
        "in hover and in cruise. A Lift + Cruise and a CVT can share the same outline, a fixed "
        "wing carrying propulsor sets, and differ in the allocation: separate units for each "
        "regime against one tilting set doing both.\n\n"
        "**Data and unit of analysis.** The unique aircraft, in the four archetype sets of "
        "chapter 2: C (class), C·W·T (class + wings + tilt), C·U (class + units) and **F**, the "
        "Lift + Cruise family: every Lift + Cruise aircraft plus every CVT aircraft whose tilting "
        "propulsor set sits on a wing that does not tilt (2.2). F groups on morphology alone: "
        "both are a fixed wing carrying propulsors spread over the airframe, and they part on "
        "the functional allocation. Sources: human labelling (class, wings, tilt, units, every "
        "field of the distance), PatSeer (priority date; legal status at the snapshot, "
        "{snapshot}).\n\n"
        "**Procedure.** A patent record has no sales, so the idea is tested through three "
        "conditions of different kinds, counts, balance and form. A dominant design needs all "
        "three in the same period: condition 1's two years inside a complete window in which "
        "conditions 2 and 3 are met. The graphs follow the conditions.\n\n"
        "- **Condition 1, counts: is most of the sector proposing the same design?** "
        "{sm_here_sm_family_yearly} shows F's share of the aircraft of each priority year on two "
        "bases: the aircraft with at least one patent in force at the snapshot, granted and "
        "alive or pending (main, solid line), and every aircraft of the year (dashed). Years are "
        "read from {sm_fy_first} (in force) and {sm_fy_first_all} (all), where the base holds "
        "{sm_dd_year_min} aircraft or more, to 2023; under each year the graph prints the "
        "aircraft in force, all aircraft, and the share of the in-force aircraft with a granted "
        "patent. *Met when* one archetype holds more than 50 % in two consecutive read years "
        "(ringed in red). It moves only when one archetype's share rises while all the others "
        "fall; two designs sharing the field do not meet it. C, C·W·T and C·U are read the same "
        "way and reported in {sm_here_la_dd_levels}.\n"
        "- **Condition 2, balance: are fewer designs in play than chance gives?** "
        "{sm_here_sm_dd_conditions} (i) shows, per four-year window and archetype set, ²D (how "
        "many large designs are in play, box of 2.2) against its permutation band (grey): the "
        "middle 95 % of the ²D values obtained when the aircraft are shuffled among the windows "
        "at random (box of chapter 1). ²D is rarefied to {sm_perm_n} aircraft because it needs "
        "a sample of the same size in every window to be compared, and it is read per window "
        "because single years are too small for that sample. The {sm_perm_n} are drawn at "
        "random from the window's aircraft, and the draw is repeated {sm_rare_draws} times and "
        "averaged, so every aircraft has the same chance of entering and no single sample "
        "decides the value. *Met when* ²D falls below the band (red point): the window holds "
        "fewer designs in play than the same aircraft dealt into windows at random.\n"
        # 2026-09-28 (L4, L5, L7): the same bold lead as conditions 1 and 2, short sentences,
        # the formulas pointed to (box of 2.2), and the two weightings said in plain words
        "- **Condition 3, form: have the aircraft themselves become alike?** "
        "{sm_here_sm_dd_conditions} (ii) shows ΔQ per window against its permutation band. Q "
        "is the average Gower distance between two aircraft of the window (Rao's quadratic "
        "entropy; formulas in the box of 2.2): 0 when two aircraft answer every design field "
        "alike, 1 when they share none. ΔQ is the window's Q minus the average Q of the two "
        "earliest windows. The fields compared are the class; wing count, arrangement, vertical "
        "and lateral position and planform; empennage type and count; fuselage count, shape, "
        "body motion, symmetry and landing gear; whether the wing carries thrust and how many "
        "units it carries; propulsor units, any tilting unit, fixed and tilting units mixed, any "
        "ducted unit, all units ducted. **The main weighting** (solid) gives each of the six "
        "subsystems (class, wings, tail, body, booms, propulsion) the same total weight, shared "
        "among its fields, so a subsystem described by many fields does not outweigh one "
        "described by few. **The check** (dashed, dotted band) gives every field the same "
        "weight, so the propulsion fields, the most numerous, carry the largest part of it. "
        "*Met when* ΔQ falls below its band (red point). Q uses no archetype: C, C·U and F read "
        "the same aircraft, give identical values and share one panel; C·W·T leaves out the few "
        "aircraft whose wings or tilt are not recorded. So Q can fall when aircraft converge on "
        "one layout under different class names, while conditions 1 and 2 need not move.\n"
        "- {sm_here_la_dd_levels} marks, per condition and archetype set, whether the condition "
        "is met (✓) or not (✗), naming the years or windows.\n\n"
        "**Scientific grounds.** Condition 1 carries Anderson and Tushman (1990), more than "
        "50 % of new product sales in four consecutive years, over to a patent record; on its "
        "{sm_dd_read_years} read years, two consecutive years are asked. Its main base is the "
        "in-force set: a dominant design is the design most new products follow, a patent "
        "record has no sales, and renewal fees are the one place where a firm votes with money "
        "on the designs it still values, so the aircraft still in force are the closest "
        "substitute; all aircraft are kept beside them as the check. Conditions 2 and 3 measure "
        "what the literature states in words: variety collapses (Utterback), the core "
        "subsystems converge (Murmann and Frenken, 2006). The shakeout test of Suárez and "
        "Utterback (1995) is not run: most active firms are still filing for the first time, so "
        "there are no exits to date it by.\n\n"
        "**Assumptions and limits.** The thresholds (50 %, the bands) were fixed before any "
        "curve was drawn. Chosen after the first readings of the data: the yearly step of "
        "condition 1 (a dominant design is a claim about the latest years, which a four-year "
        "window blurs), its in-force base, and F. F was defined to test whether the general "
        "morphology could be grouped, because the boom and propulsor-unit patterns had made "
        "Lift + Cruise and the fixed-wing CVT look alike; CVT with units on booms and Tilt "
        "Propulsor with CVT were considered and not used. Merging archetypes adds their shares, "
        "so grouping alone can pass condition 1; it cannot pass conditions 2 and 3, since the "
        "band of condition 2 is rebuilt from the grouped archetypes and Q uses none. 2022 and "
        "2023 are the least complete years: only {sm_fy_gl_2022} and {sm_fy_gl_2023} of their "
        "in-force aircraft hold a granted patent, against {sm_fy_gl_2020} and {sm_fy_gl_2021} in "
        "2020 and 2021, and {sm_lapse_p2022} of the 2022 families and {sm_lapse_p2023} of the "
        "2023 ones are neither granted nor refused.\n\n"
        + _tm.ERA_FRAME_METHOD.replace("the within-class readings of chapter 3",
                                       "the within-class readings of 3.3")
    ),
}

#: C43: nothing under "Results and discussion" in 3.1 beyond its two takeaways; 3.2's reading of
#: the verdict comes after its items (AFTER), so the figures lead
RESULTS: Dict[str, str] = {"3.1": "", "3.2": ""}

# ---------------------------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------------------------
ITEMS = {
    "3.1": dict(figures=["atlas_arch_time", "sm_evtolnews_check"], tables=[]),
    # the per-window dominant_design and sm_weighting are replaced by sm_dd_conditions (the four
    # levels, met points in red, C54/C57); sm_family by sm_family_yearly (C53); la_dd_result by
    # la_dd_levels (which level-windows, C57); la_family_dd dropped (C59)
    # K26 (2026-09-28): la_top_archetypes dropped, its two shares folded into the AFTER text
    "3.2": dict(figures=["sm_family_yearly", "sm_dd_conditions"],
                tables=["la_dd_levels"]),
}

FIGURE_CAPTIONS = {
    "sm_evtolnews_check": "the class mix per window in the labelled dataset, folded to the five "
                          "classes of the evtol.news directory (i), beside the directory's own "
                          "mix per development-year window (ii)",
    "sm_family_yearly": "condition 1 on F, the Lift + Cruise family (defined after the first "
                        "readings of the data), per priority year: its share of the aircraft "
                        "with a patent in force and of all aircraft, against the 50 % line",
    "sm_dd_conditions": "conditions 2 and 3 of the dominant-design test per window in the four "
                        "archetype sets C, C·W·T, C·U and F; a red point is an archetype-set "
                        "window where the condition is met; condition 3 under the main "
                        "weighting (every subsystem equal) and the check (every field equal)",
}

TABLE_CAPTIONS = {
    "la_dd_levels": "The dominant-design verdict per condition and archetype set, naming the "
                    "priority years (condition 1) or windows (conditions 2 and 3) where each "
                    "condition is met (✓) or not (✗). Condition 1 on the aircraft with a patent "
                    "in force (main) and on all aircraft; condition 3 under the main weighting. "
                    "F was defined after the first readings of the data",
}

NOT_CORE = {
    "sm_family_yearly": "condition 1 per priority year on the in-force and all-aircraft bases, "
                        "the author's ruling (C53, 2026-09-26)",
    "sm_dd_conditions": "conditions 2 and 3 at the four levels with the met level-windows "
                        "marked (C54, C57)",
    "la_dd_levels": "the verdict per condition and level, naming where each is met (C54, C57)",
}

# ---------------------------------------------------------------------------------------------
# print hooks: readable names (C61), short level headers
# ---------------------------------------------------------------------------------------------
def _flag(cell: str) -> str:
    """K25 (2026-09-28): a met / not-met flag in every verdict cell. Bold ✓ / ✗ rather than a
    coloured span, because export_brief_docx strips every <span> and the brief is monochrome:
    bold and the two signs survive both the PDF and the Word export."""
    import re
    c = str(cell).replace("(subsystem weighting only)", "(main weighting only)")
    if c.strip() == "no":
        return "**✗ not met**"
    c = re.sub(r"\bmet in\b", "**✓ met** in", c)
    c = re.sub(r"\bno — ", "**✗ not met**, ", c)
    return c.replace(" — ", ", ")


def _print_levels(t):
    t = t.copy()
    t[t.columns[0]] = t[t.columns[0]].astype(str).str.replace(" — ", ", ", regex=False)
    for c in t.columns[1:]:
        t[c] = t[c].astype(str).map(_flag)
    ren = {}
    for c in t.columns:
        if " — " in c:
            code = c.split(" — ")[0]
            ren[c] = f"{code} (defined after the first readings)" if code == "F" else code
    return t.rename(columns=ren)


PRINT = {
    "la_dd_levels": _print_levels,
}

# ---------------------------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------------------------
_EC = "la_evtolnews_compare"
_EV = "la_evtolnews_class_verdict"
_EK = "la_evtolnews_check"
_EG = "la_evtolnews_coverage"
_D = "directory class"
_PAT = "patent corpus (unique aircraft, priority year)"
_DIR = "evtol.news directory (aircraft, development year)"

NUMBERS = {
    # 3.1 — the directory's dating (sm_open.evtolnews_coverage)
    "sm_evn_dated_share": dict(table=_EG, where=(_D, "all classes"), col="dated share", fmt="pct"),
    # 3.1 — the balance of the two large classes (sm_open.evtolnews_compare)
    "sm_evn_lc2_p_2023": dict(table=_EC, where=("window", "2020-23"),
                              col="Lift + Cruise of (LC + VT), patent", fmt="pct"),
    "sm_evn_lc2_d_2023": dict(table=_EC, where=("window", "2020-23"),
                              col="Lift + Cruise of (LC + VT), directory", fmt="pct"),
    "sm_evn_p_bal_2023": dict(table=_EC, where=("window", "2020-23"), col="p (LC vs VT balance)",
                              fmt="p"),
    "sm_evn_p_bal_min": dict(table=_EC, how="min", col="p (LC vs VT balance)", fmt="p"),
    # 3.1 — the classes that differ (sm_open.evtolnews_class_verdict / evtolnews_check)
    "sm_evn_wm_p_2023": dict(table=_EV, where=("code", "WM"), col="patent 2020-23", fmt="pct"),
    "sm_evn_wm_d_2023": dict(table=_EV, where=("code", "WM"), col="directory 2020-23", fmt="pct"),
    "sm_evn_wm_p_w1": dict(table=_EV, where=("code", "WM"), col="patent <= 2011", fmt="pct"),
    "sm_evn_wm_d_w1": dict(table=_EV, where=("code", "WM"), col="directory <= 2011", fmt="pct"),
    "sm_evn_p_wm_2023": dict(table=_EV, where=("code", "WM"),
                             col="p level 2020-23, patent vs directory", fmt="p"),
    "sm_evn_hb_p_w1": dict(table=_EV, where=("code", "HB"), col="patent <= 2011", fmt="pct"),
    "sm_evn_hb_d_w1": dict(table=_EV, where=("code", "HB"), col="directory <= 2011", fmt="pct"),
    "sm_evn_lc_p_w1": dict(table=_EV, where=("code", "LC"), col="patent <= 2011", fmt="pct"),
    "sm_evn_lc_p_2023": dict(table=_EV, where=("code", "LC"), col="patent 2020-23", fmt="pct"),
    "sm_evn_lc_d_w1": dict(table=_EV, where=("code", "LC"), col="directory <= 2011", fmt="pct"),
    "sm_evn_lc_d_2023": dict(table=_EV, where=("code", "LC"), col="directory 2020-23", fmt="pct"),
    "sm_evn_n_p_2023": dict(table=_EC, where=("window", "2020-23"), col="patent aircraft",
                            fmt="int"),
    "sm_evn_n_d_2023": dict(table=_EC, where=("window", "2020-23"), col="directory aircraft",
                            fmt="int"),
}


def _num(x) -> Optional[float]:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if v != v else v


def _pct(x: float) -> str:
    from . import la_index as _la
    return _la._tk_fmt(x, "pct")


def _thin(n: int) -> str:
    """1229 -> '1 229', the document's thousands separator."""
    return f"{int(n):,}".replace(",", " ")


def _pct1(x: float) -> str:
    """One decimal, because condition 1 turns on whether 50.0 % is more than half."""
    return f"{100 * x:.1f} %"


def _ch3_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    """The chapter-3 numbers the spec grammar cannot say, each read from a built table:

    * condition 1 on F per year (``la_family_yearly``): the shares with one decimal, the counts,
      the granted share of the in-force base, the first year read and the years met;
    * the largest archetype of any read year at C, C·W·T and C·U (``la_dd_yearly``);
    * the ²D and ΔQ values of the met level-windows (``la_dd_balance``, ``la_dd_form``);
    * the p range of the balance test (``la_evtolnews_compare``);
    * the apparatus constants (``sm_open``);
    * pointers of the items this chapter no longer prints, re-aimed at their successors.
    """
    import pandas as pd
    out: Dict[str, str] = {}
    t = tables or {}

    try:
        from . import sm_open as _so
        out["sm_dd_year_min"] = str(int(_so.DD_YEAR_MIN))
        out["sm_evn_min_n"] = str(int(_so.EVN_MIN_N))
    except Exception:
        pass
    # 2026-09-28 (L3): how many random draws of the rarefaction sample the observed ²D averages,
    # read from the code that runs (la_tables.dominant_design and sm_open.dd_balance pass the
    # same ``draws``); left unset, so the render fails loudly, if the two ever disagree
    try:
        import inspect
        import re as _re
        from . import la_tables as _ltb
        from . import sm_open as _so2
        d1 = _re.findall(r'hill_numbers\(sub\["key"\], n=n, draws=(\d+)\)',
                         inspect.getsource(_ltb.dominant_design))
        d2 = _re.findall(r'hill_numbers\(sub\["key"\], n=n, draws=(\d+)\)',
                         inspect.getsource(_so2.dd_balance))
        if d1 and set(d1) == set(d2):
            out["sm_rare_draws"] = d1[0]
    except Exception:
        pass

    fy = t.get("la_family_yearly")
    if fy is not None and "priority year" in fy.columns:
        f = fy.copy()
        f["_y"] = pd.to_numeric(f["priority year"], errors="coerce").astype("Int64")
        f = f.set_index("_y")
        read = f[f["read, in force"].astype(str).eq("True")]
        if len(read):
            out["sm_fy_first"] = str(int(read.index.min()))
        read_all = f[f["read, all"].astype(str).eq("True")]
        if len(read_all):
            out["sm_fy_first_all"] = str(int(read_all.index.min()))
            out["sm_dd_read_years"] = {6: "six", 7: "seven", 8: "eight", 9: "nine",
                                       10: "ten"}.get(len(read), str(len(read)))
        for y in (2020, 2021, 2022, 2023):
            if y not in f.index:
                continue
            r = f.loc[y]
            fi, fa = _num(r["F share in force"]), _num(r["F share"])
            gl = _num(r["in force with a granted patent"])
            if fi is not None:
                out[f"sm_fy_fi_{y}"] = _pct1(fi)
            if fa is not None:
                out[f"sm_fy_fa_{y}"] = _pct1(fa)
            if gl is not None:
                out[f"sm_fy_gl_{y}"] = _pct(gl)
            out[f"sm_fy_fik_{y}"] = str(int(float(r["F aircraft in force"])))
            out[f"sm_fy_ni_{y}"] = str(int(float(r["aircraft in force"])))
            out[f"sm_fy_fak_{y}"] = str(int(float(r["F aircraft"])))
            out[f"sm_fy_na_{y}"] = str(int(float(r["aircraft"])))
        # the consecutive read years above half, on the main base
        over = [int(y) for y, s in zip(read.index, read["F share in force"])
                if (_num(s) or 0) > 0.5]
        met = sorted({x for a, b in zip(over[:-1], over[1:]) if b == a + 1 for x in (a, b)})
        if met:
            out["sm_fy_met"] = " and ".join(str(x) for x in met)

    yy = t.get("la_dd_yearly")
    if yy is not None and "level id" in yy.columns:
        y = yy[yy["read"].astype(str).eq("True") & yy["base"].astype(str).eq("in force")].copy()
        y["_s"] = pd.to_numeric(y["its share"], errors="coerce")
        rest = y[~y["level id"].astype(str).eq("family_b")]
        if len(rest):
            top = rest.loc[rest["_s"].idxmax()]
            out["sm_dd_max_rest"] = _pct1(float(top["_s"]))
            out["sm_dd_max_rest_year"] = str(int(float(top["priority year"])))
            out["sm_dd_max_rest_name"] = str(top["largest archetype"])
        for lvl, key in (("A1t", "cwt"), ("A0c", "cu")):
            s = y[y["level id"].astype(str).eq(lvl)]
            if len(s):
                out[f"sm_dd_max_{key}"] = _pct1(float(s["_s"].max()))
        fine = y[y["level id"].astype(str).isin(["A1t", "A0c"])]
        if len(fine):
            out["sm_dd_max_fine"] = _pct1(float(fine["_s"].max()))

    b = t.get("la_dd_balance")
    if b is not None and "level" in b.columns:
        for lvl, key, win, tag in (("family_b", "f", "2020-23", "2023"), ("A0", "c", "2020-23", "2023"),
                                   ("A0c", "cu", "<= 2011", "w1"), ("A0c", "cu", "2012-15", "w2")):
            r = b[b["level"].astype(str).eq(lvl) & b["window"].astype(str).eq(win)]
            if len(r):
                out[f"sm_bal_{key}_{tag}"] = f"{float(r['D2'].iloc[0]):.2f}"
                out[f"sm_bal_{key}_{tag}_lo"] = f"{float(r['D2 permutation low'].iloc[0]):.2f}"
        # the smallest complete window read (the stats box's reason for the rarefaction size)
        c = b[b["level"].astype(str).eq("A0") & ~b["window"].astype(str).str.contains("partial")]
        if len(c):
            out["sm_win_min_n"] = str(int(pd.to_numeric(c["aircraft"], errors="coerce").min()))

    q = t.get("la_dd_form")
    if q is not None and "level" in q.columns:
        for wt, key in (("subsystem", "main"), ("uniform", "alt")):
            r = q[q["level"].astype(str).eq("A0") & q["window"].astype(str).eq("2020-23")
                  & q["weighting"].astype(str).eq(wt)]
            if len(r):
                minus = lambda z: f"{z:+.3f}".replace("-", "−")
                out[f"sm_q_{key}_2023"] = minus(float(r["ΔQ"].iloc[0]))
                out[f"sm_q_{key}_2023_lo"] = minus(float(r["ΔQ permutation low"].iloc[0]))

    ec = t.get("la_evtolnews_compare")
    if ec is not None and "p (LC vs VT balance)" in ec.columns:
        p = pd.to_numeric(ec["p (LC vs VT balance)"], errors="coerce").dropna()
        if len(p):
            out["sm_evn_p_bal_lo"] = f"{p.min():.2f}"
    eg = t.get("la_evtolnews_coverage")
    if eg is not None and "directory class" in eg.columns:
        r = eg[eg["directory class"].astype(str).eq("all classes")]
        if len(r):
            for key, col in (("list", "aircraft on the list"), ("agreed", "agreed by both readers"),
                             ("notstated", "not stated on the page"),
                             ("conflict", "conflict, not yet ruled"), ("dated", "dated (in the panel)")):
                if col in r.columns and _num(r[col].iloc[0]) is not None:
                    out[f"sm_evn_{key}"] = _thin(int(float(r[col].iloc[0])))
    ev = t.get("la_evtolnews_class_verdict")
    if ev is not None and "p change, patent" in ev.columns:
        r = ev[ev["code"].astype(str).isin(["LC", "VT"])]
        ps = pd.concat([pd.to_numeric(r["p change, patent"], errors="coerce"),
                        pd.to_numeric(r["p change, directory"], errors="coerce")]).dropna()
        if len(ps):
            out["sm_evn_p_change_lo"] = f"{ps.min():.2f}"

    # the closing section of the brief points at the old dominant-design items by name; they are
    # now sm_dd_conditions and la_dd_levels
    try:
        from . import sm_index as _sm
        for old, new in (("dominant_design", "sm_dd_conditions"), ("la_dd_result", "la_dd_levels")):
            if old not in _sm.HERE_REF and new in _sm.HERE_REF:
                out[f"sm_here_{old}"] = _sm.HERE_REF[new]
    except Exception:
        pass
    return out


NUMBER_FUNCS = [_ch3_numbers]

# ---------------------------------------------------------------------------------------------
# takeaways (rule 3: specific bold leads; no repeat of the Method; no prose repeats them)
# ---------------------------------------------------------------------------------------------
TAKEAWAY = {
    "atlas_arch_time":
        "**Tilt Propulsor falls from {tk_tr_w1} of the earliest window's aircraft to {tk_tr_w4} "
        "in 2020-23 while Lift + Cruise rises from {tk_slc_w1} to {tk_slc_w4}; the two hold equal "
        "shares in 2016-19.** With CVT ({tk_cvt_w4}) the three hold {sm_top3_a0_w4} of the "
        "recent aircraft. The earliest window rests on {sm_w1_n} aircraft against {sm_w4_n} at "
        "the recent end, so its shares are coarse",

    # K14, K15 (2026-09-28): agreement of two independent sources, not chance; the parting on
    # the small classes has a stated cause (K13); one sentence answers "is it representative?"
    "sm_evtolnews_check":
        # 2026-09-28 (N2): the pooled balance test is gone with panel (iii); the reading is
        # qualitative, and the class-level agreement is 1.3's
        "**The directory shows a similar mix: Vectored Thrust is the larger of the two large "
        "classes in every window of both sources, and Lift + Cruise rises in both, from "
        "{sm_evn_lc_p_w1} to {sm_evn_lc_p_2023} in the labelled dataset and from "
        "{sm_evn_lc_d_w1} to {sm_evn_lc_d_2023} in the directory.** Where the small classes "
        "differ, the directory's unfiltered listings explain it: Wingless is {sm_evn_wm_d_2023} "
        "of the directory's 2020-23 aircraft against {sm_evn_wm_p_2023} in the labelled dataset, "
        "and early on Hover Bikes are {sm_evn_hb_d_w1} against {sm_evn_hb_p_w1}, because the "
        "directory's lists also carry UAV and cargo designs that the labelled dataset's domain "
        "refinement removes. This parting does not put the labelled dataset in question. The "
        "Tilt Propulsor crossover has no outside check, since the directory pools Tilt Propulsor "
        "with CVT and Tilt Wing. The figure compares mixes only: that the labelled dataset's "
        "classes agree with the aircraft actually built is shown aircraft by aircraft in 1.3",

    # K23: the recent fall carries the publication-lag caveat
    "sm_family_yearly":
        "**On the aircraft still in force the family holds more than half of 2020 and of 2021, "
        "{sm_fy_fi_2020} and {sm_fy_fi_2021}, and so meets condition 1; on all aircraft it does "
        "not, because 2020 stops at exactly half ({sm_fy_fa_2020}).** The margin is small: "
        "{sm_fy_fik_2020} of {sm_fy_ni_2020} and {sm_fy_fik_2021} of {sm_fy_ni_2021} aircraft. "
        "In 2022 and 2023 the family falls to {sm_fy_fi_2022} and {sm_fy_fi_2023} of the "
        "in-force aircraft, in the two years whose base is least complete. A caveat, not a "
        "finding: these years are still filling because of the priority-to-publication lag, and "
        "if Lift + Cruise and CVT filings surface later than others, the fall could be partly "
        "that lag",

    # K24: the archetype sets compared explicitly
    "sm_dd_conditions":
        "**Condition 2 is met by F and by C in 2020-23 and by C·U in the two earliest windows; "
        "condition 3 is met in every archetype set in 2020-23, under the main weighting only.** "
        "(i) F's ²D in 2020-23 is {sm_bal_f_2023}, below its band (lower edge "
        "{sm_bal_f_2023_lo}), and C's is {sm_bal_c_2023}, just below its band (edge "
        "{sm_bal_c_2023_lo}). C·U sat below its band in the same way in the two earliest windows "
        "({sm_bal_cu_w1} against an edge of {sm_bal_cu_w1_lo}, {sm_bal_cu_w2} against "
        "{sm_bal_cu_w2_lo}) and is inside it since; C·W·T is inside its band in every window. "
        "(ii) In 2020-23 ΔQ is {sm_q_main_2023}, past the lower edge of its band at "
        "{sm_q_main_2023_lo}; with every field weighted equally it is {sm_q_alt_2023}, inside "
        "its band (edge {sm_q_alt_2023_lo}). Why this matters: counted subsystem by subsystem, "
        "the aircraft of 2020-23 are more alike than chance gives; counted field by field, they "
        "are not. The convergence therefore sits in the subsystems described by few fields "
        "rather than in the propulsion fields, which carry the largest part of the equal "
        "weighting, and condition 3 rests on the choice to count each subsystem once",

    # K25b + the author's morphology / operating-principle reading
    "la_dd_levels":
        "**Only F meets the three conditions in the same period, 2020-23, with condition 1 met "
        "in {sm_fy_met} on the aircraft in force; C, C·W·T and C·U each meet at most two.** "
        "Condition 1 is where they part: the largest archetype reaches at most "
        "{sm_dd_max_rest} of a year's in-force aircraft at C ({sm_dd_max_rest_name}, "
        "{sm_dd_max_rest_year}), {sm_dd_max_cwt} at C·W·T and {sm_dd_max_cu} at C·U, against "
        "F's {sm_fy_fi_2021} in 2021. F was defined after the first readings of the data, to "
        "test whether the general morphology could be grouped, because the boom and "
        "propulsor-unit patterns had made Lift + Cruise and the fixed-wing CVT look alike. It is "
        "the only grouping that meets all conditions, and it rests on morphology alone: its "
        "members part on the functional allocation. The convergence the labelled dataset shows is therefore "
        "morphological, and a dominant design in the full sense, with morphology and functional "
        "allocation both shared, is not found",
}

# ---------------------------------------------------------------------------------------------
# the reading of the verdict, after the items (C60: itemised; no takeaway repeated)
# ---------------------------------------------------------------------------------------------
AFTER = {
    "3.2": (
        "**Reading the verdict.**\n\n"
        "- **The pass rests on three choices, and each is shown both ways.** F and the in-force "
        "base were chosen after the first readings of the data, and condition 3 holds under the "
        "main weighting only. Keep F but count every aircraft of the year, or weight every field "
        "equally, and F does not meet a condition.\n"
        "- **What holds under every choice is a shared morphology, not a shared functional "
        "allocation.** F's members share a fixed wing carrying many propulsors and part on which "
        "components do the cruise duty: dedicated propellers in Lift + Cruise, some of the lift "
        "propulsors tilted forward in CVT. This is the reading F was built to test.\n"
        "- **The era, on the frame of the Method.** At C·W·T and C·U the recent windows read as "
        "an era of ferment: no archetype holds more than {sm_dd_max_fine} of a year, ²D is "
        "inside its band, and the three largest archetypes hold {sm_top3_a1t_w4} of 2020-23 at "
        "C·W·T (one-wing Lift + Cruise, Tilt Propulsor and CVT) and {sm_top3_a0c_w4} at C·U. At "
        "C the recent window concentrates, with ²D just under its band and Q falling, while no "
        "class passes {sm_dd_max_rest} of a year. F shows the pattern of a dominant morphology "
        "emerging in 2020-21: past half, fewer designs in play, aircraft more alike; the years "
        "after it are too incomplete to say whether it held.\n"
    ),
}

# ---------------------------------------------------------------------------------------------
# the Answer box (the last bullet is left for 3.3-3.4, written in sm_text_ch3b)
# ---------------------------------------------------------------------------------------------
ANSWER = (
    # 2026-09-27, author: lead with the dominant design and say exactly what it is, a branch
    # that cuts across the usual eVTOL classes. 2026-09-28, author: the convergence is one of
    # morphology, not of functional allocation
    "**eVTOL has converged on a dominant morphology that cuts across two of the classes the "
    "sector is usually sorted into: Lift + Cruise together with the CVT aircraft that tilt a "
    "propulsor set on a fixed wing, a fixed wing carrying many propulsors. That family meets all "
    "three dominant-design conditions in 2020-23 on the aircraft still in force; no single class "
    "or archetype does. Its members differ in functional allocation, which components do which "
    "duty in hover and in cruise, so a dominant design in the full sense, morphology and "
    "functional allocation both shared, is not found.**\n\n"
    "- **Lift + Cruise rises from {tk_slc_w1} to {tk_slc_w4} of the aircraft between the "
    "earliest window and 2020-23, while Tilt Propulsor falls from {tk_tr_w1} to {tk_tr_w4}.** "
    "The evtol.news directory shows a similar mix, with the tilting classes the larger in every "
    "window and Lift + Cruise rising; it pools Tilt Propulsor with CVT, so the crossover itself "
    "has no outside check.\n"
    "- **Condition 1: the family holds more than half of 2020 and 2021 on the aircraft in "
    "force** ({sm_fy_fi_2020}, {sm_fy_fi_2021}); on all aircraft 2020 stops at "
    "{sm_fy_fa_2020}. In 2022-23, years still largely under examination and still filling, it "
    "falls to {sm_fy_fi_2022} and {sm_fy_fi_2023}.\n"
    "- **Conditions 2 and 3 are met by the family in 2020-23**, condition 3 under the main "
    "weighting only. In C, C·W·T and C·U no period meets all three, and no archetype passes "
    "{sm_dd_max_rest} of a year's in-force aircraft.\n"
    "- **What the result rests on.** The family and the in-force base were chosen after the "
    "first readings of the data. Counted on all aircraft, 2020 stops at exactly half, one "
    "aircraft short of a majority; with equal field weights, condition 3 is not met. Counted "
    "only on aircraft with a granted patent still in force (none of them still under "
    "examination), the family holds {sm3_f_gl_2020} of 2020 and {sm3_f_gl_2021} of 2021, so "
    "the majority is not an artefact of pending applications.\n"
    "- [3.3–3.4 bullet: to be added]"
)

NUMBERS.update({
    # 2026-09-27: the family on granted-and-live aircraft only (no pending applications)
    "sm3_f_gl_2020": dict(table="la_family_yearly", where=("priority year", "2020"),
                          col="F share, granted and live", fmt="pct"),
    "sm3_f_gl_2021": dict(table="la_family_yearly", where=("priority year", "2021"),
                          col="F share, granted and live", fmt="pct"),
})
