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
C52/C56      family F = definition (b) only, chosen on morphological similarity, post hoc; the
             alternatives in one line.
C53          condition 1 read per priority year; main base the aircraft with a patent in force,
             second base all aircraft; ``la_family_yearly`` + ``sm_family_yearly``.
C54          F is one more level of the test, beside C, C·W·T and C·U (``la_dd_levels``,
             ``sm_dd_conditions``).
C57          every met level-window drawn in red (``sm_dd_conditions``, ``sm_family_yearly``) and
             named in the verdict table (``la_dd_levels``).
C58/C59      no generated how-to-read; ``la_family_dd`` and its takeaway dropped.
C60          the reading of the verdict itemised (AFTER).
C61          ``la_top_archetypes`` printed with readable archetype names, two levels, complete
             windows (PRINT hook).
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
    "at a named level — **C** (class), **C·W·T** (class + wings + tilt), **C·U** (class + units) "
    "or **F**, the Lift + Cruise family.\n\n"
    "- **3.1 — which architectures gain and which fade.** The class mix per priority window, set "
    "against the one outside series that dates eVTOL aircraft by class: the evtol.news "
    "directory.\n"
    "- **3.2 — whether there is a dominant design.** Three conditions of different kinds, at the "
    "four levels, and the era of a technology cycle they place the sector in.\n"
    "- **3.3 — whether designs converge inside each class.** Each class read on the labels that "
    "tell its own designs apart.\n"
    "- **3.4 — what drives the changes inside the classes.** The propulsion traces over the "
    "priority years, read class by class.\n"
)

# ---------------------------------------------------------------------------------------------
# Method blocks
# ---------------------------------------------------------------------------------------------
METHOD: Dict[str, str] = {
    "3.q1": (
        "#### Method\n\n"
        "Two readings: the class mix inside the record, and the same mix in a public list of "
        "aircraft.\n\n"
        "- **The class mix per priority window — {sm_here_atlas_arch_time}.** (i) Each bar is one "
        "window at 100 %: the share of its unique aircraft in each architecture class; (ii) the "
        "five largest classes over the windows. *Unit:* the unique aircraft, because a design "
        "filed several times is one design. *Window:* four priority years, because before 2016 a "
        "single year holds too few aircraft to carry twelve shares; the 2024-26 window is still "
        "filling and is not read. A share can fall while the count still grows, so shares are "
        "read, never counts. Sources: human labelling (class), PatSeer (priority date).\n"
        "- **The outside check — {sm_here_sm_evtolnews_check}.** The World eVTOL Aircraft "
        "Directory of the Vertical Flight Society (evtol.news, crawled 2026-09-17) lists "
        "{sm_evn_list} aircraft, each on one of five class lists.\n"
        "  - *Dating.* The directory has no year field, so each aircraft gets a **development "
        "year**: the earliest year its own page documents for its development (a programme start, "
        "an unveiling, a first flight, a dated source), the counterpart of a patent's priority "
        "year. Two independent readers — separate instances of a language model, given only the "
        "page's dated sentences — each named the sentence that dates the aircraft, and a script "
        "checked that it states the year. Where both gave the same year it is used "
        "({sm_evn_agreed} aircraft); where neither found one the aircraft is undated "
        "({sm_evn_notstated}); the {sm_evn_conflict} on which they disagree await the author's "
        "ruling and are **left out until ruled**. The panel rests on {sm_evn_dated} dated "
        "aircraft ({sm_evn_dated_share} of the list).\n"
        "  - *Classes.* The record's twelve classes are folded onto the directory's five: Lift + "
        "Cruise stays Lift + Cruise; every class whose thrust tilts or is redirected (Tilt Rotor, "
        "Tilt Wing, CVT, Tilt Body, Pitch-to-Cruise, Deflected Slipstream) is **Vectored "
        "Thrust**; Multirotor is Wingless; Rotorcraft and Stopped/Slowed Rotor Wing are Electric "
        "Rotorcraft; Hoverbike and Personal Flying Vehicle are Hover Bikes.\n"
        "  - *Tests.* Per window, a Fisher exact test on the balance between Lift + Cruise and "
        "Vectored Thrust (their aircraft only) and a chi-square on the whole five-class mix; per "
        "class, a Fisher test of the change from the earliest window to 2020-23 in each source. "
        "A window is compared where both sources hold {sm_evn_min_n} dated aircraft or more.\n"
        "  - *What it can check.* The directory counts announced aircraft, not patented ones, so "
        "the two need not hold the same levels; what can be compared is the direction of each "
        "class and the balance between the two large ones. Vectored Thrust pools Tilt Rotor with "
        "CVT and Tilt Wing, so the crossover of Lift + Cruise over Tilt Rotor cannot be checked "
        "against it.\n"
    ),

    "3.q2": (
        "#### Method\n\n"
        "A **dominant design** is the design a sector settles on after a period of competing "
        "alternatives: most new products follow it, and change moves from the concept to its "
        "parts (Abernathy and Utterback, 1978). A patent record cannot see sales, so the idea is "
        "tested through three conditions of different kinds — **counts, balance, form** — at the "
        "four levels of chapter 2: C, C·W·T, C·U and the family F. **A dominant design needs all "
        "three in the same period.** The thresholds (50 %, the permutation bands) were fixed "
        "before any curve of this corpus was drawn; the base and the time step of condition 1 "
        "were chosen after the first readings, and are marked post hoc below.\n\n"
        "**Condition 1 — counts. Is most of the sector proposing the same design?**\n\n"
        "- *Measure:* the share of the largest archetype among the aircraft of each priority "
        "year. *Met when* one archetype holds more than 50 % in two consecutive years. Anderson "
        "and Tushman (1990) ask for more than 50 % of new product sales in four consecutive "
        "years; the per-window reading this replaces asked for two consecutive windows, and on "
        "the {sm_dd_read_years} readable years of this record two consecutive years are asked.\n"
        "- *Which aircraft — two bases, both shown.*\n"
        "  - **Main: the aircraft with at least one patent in force** at the snapshot, granted "
        "and alive or still pending (chapter 1). A patent stays in force only while its renewal "
        "fees are paid, and a firm pays them only for a design it still values; this base is what "
        "the sector still holds rights to, not everything it ever tried.\n"
        "  - **Second: every aircraft of the year**, as filed.\n"
        "  - *Post hoc.* The first reading ran per four-year window on all aircraft. The in-force "
        "base and the yearly step were chosen after it: the yearly step because a dominant design "
        "is a claim about the latest years, which a four-year window blurs; the in-force base for "
        "the renewal-fee reason above, and because the recent years are mostly still under "
        "examination — {sm_lapse_p2022} of the 2022 families and {sm_lapse_p2023} of the 2023 "
        "ones are neither granted nor refused.\n"
        "- *Years read:* those whose base holds {sm_dd_year_min} aircraft or more — from "
        "{sm_fy_first} on the in-force base and from {sm_fy_first_all} on all aircraft — to 2023, "
        "the last year whose publication lag has run. 2022 and 2023 are the "
        "least complete years: of their in-force aircraft only {sm_fy_gl_2022} and "
        "{sm_fy_gl_2023} hold a granted patent, against {sm_fy_gl_2020} and {sm_fy_gl_2021} in "
        "2020 and 2021; the rest are applications not yet decided.\n"
        "- *What moves it:* one archetype gaining at the expense of all the others. Two designs "
        "sharing the field do not meet it.\n\n"
        "**Condition 2 — balance. Are fewer designs in play than chance gives?**\n\n"
        "- *Measure:* ²D of each four-year window (how many large designs are in play; box of "
        "2.2), rarefied to 40 aircraft, against its permutation band. Read per window because ²D "
        "needs a sample of 40, more than most single years hold.\n"
        "- *Met when* ²D falls below the band: the window holds fewer designs in play than the "
        "same aircraft, dealt into windows at random, would give it.\n"
        "- *What moves it:* a window crowding into two or three archetypes while the rest of the "
        "record is spread. A window only as concentrated as the record as a whole does not meet "
        "it.\n\n"
        "**Condition 3 — form. Have the aircraft themselves become alike?**\n\n"
        "- *The distance between two aircraft* (Gower's): every labelled field is compared — a "
        "shared answer counts 0, a different one 1, a count by how far apart the two values are, "
        "and a field blank on either aircraft is skipped. Each of the six subsystems (class, "
        "wings, tail, fuselage, booms, propulsion) weighs the same, shared among its fields, so a "
        "card with many questions does not outweigh one with few. 0 is identical, 1 nothing in "
        "common.\n"
        "- *Measure:* **Q**, the average distance between two aircraft drawn at random from the "
        "window (Rao's quadratic entropy). *Met when* **ΔQ** — the window's Q minus the average "
        "Q of the two earliest windows — falls below the band built by the same shuffle as "
        "condition 2: the window's aircraft are more alike than any random split makes them.\n"
        "- *What moves it — and what does not:* Q uses no archetype. If aircraft converge on one "
        "layout under different class names, Q falls while conditions 1 and 2 need not move; if "
        "one class grows while its own aircraft stay varied, condition 1 can climb while Q does "
        "not fall. The level therefore changes Q only through the aircraft it can name: C, C·U "
        "and F read the same aircraft; C·W·T leaves out the few whose wings or tilt are not "
        "recorded.\n"
        "- *Weighting:* the subsystem weighting above is the main one; equal weight for every "
        "field (the *uniform* weighting) is shown beside it. A result under one weighting only is a result about the "
        "weighting.\n\n"
        "**All three in the same period:** condition 1's two years inside a complete window in "
        "which conditions 2 and 3 are both met — the matching rule that follows from reading "
        "condition 1 per year.\n\n"
        "**The Lift + Cruise family F** (defined in 2.2) is every Lift + Cruise aircraft plus "
        "every CVT aircraft whose tilting part is a rotor set on a wing that does not tilt. It is "
        "chosen on **morphological similarity**: both are a fixed wing carrying rotors spread over "
        "the airframe, and differ only in whether cruise thrust comes from dedicated propellers or "
        "from some of the rotors tilted forward. It was chosen after the class readings had been "
        "seen and is **post hoc**. *Not used:* CVT with units on booms (a redundancy criterion) "
        "and Tilt Rotor with CVT (grouped because something tilts).\n\n"
        "**What grouping does to the test.** Merging archetypes adds their shares, so any "
        "grouping raises the largest share: condition 1 can be passed by grouping alone, which is "
        "why a grouping must rest on a criterion other than its share. Conditions 2 and 3 cannot: "
        "the band of condition 2 is rebuilt from the grouped archetypes, so grouping lowers the "
        "observed ²D and its band together, and Q uses no archetype at all.\n\n"
        "**What is shown.** Condition 1 on the family, year by year on both bases — "
        "{sm_here_sm_family_yearly}; conditions 2 and 3 at the four levels, every level-window "
        "where a condition is met in red — {sm_here_sm_dd_conditions}; the verdict per condition "
        "and level, naming the years or windows where each is met — {sm_here_la_dd_levels}; and "
        "what holds the recent aircraft below the family: the three largest archetypes of each "
        "window at C·W·T and C·U — {sm_here_la_top_archetypes}. *Unit:* the unique aircraft. "
        "Sources: human labelling (class, wings, tilt, units, every field of the distance), "
        "PatSeer (priority date; legal status at the snapshot, {snapshot}).\n\n"
        "**Where the conditions come from.** Condition 1 carries Anderson and Tushman (1990) over "
        "to a patent record. Conditions 2 and 3 are this thesis's own measurements of what the "
        "literature states only in words: variety collapses (Utterback), the core subsystems "
        "converge (Murmann and Frenken, 2006). The shakeout test of Suárez and Utterback (1995) is "
        "not run: most active firms are still filing for the first time, so there are no exits "
        "to date it by.\n\n"
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
    "3.2": dict(figures=["sm_family_yearly", "sm_dd_conditions"],
                tables=["la_dd_levels", "la_top_archetypes"]),
}

FIGURE_CAPTIONS = {
    "sm_evtolnews_check": "the class mix per window in the patent record, folded to the five "
                          "classes of the evtol.news directory, beside the directory's own mix "
                          "per development-year window",
    "sm_family_yearly": "condition 1 on the Lift + Cruise family F (post hoc), per priority year: "
                        "its share of the aircraft with a patent in force and of all aircraft, "
                        "against the 50 % line",
    "sm_dd_conditions": "conditions 2 and 3 of the dominant-design test per window at the four "
                        "levels C, C·W·T, C·U and F; a red point is a level-window where the "
                        "condition is met",
}

TABLE_CAPTIONS = {
    "la_dd_levels": "The dominant-design verdict per condition and level, naming the priority "
                    "years (condition 1) or windows (conditions 2 and 3) where each condition is "
                    "met. Condition 1 on the aircraft with a patent in force (main) and on all "
                    "aircraft; condition 3 under the main weighting. F was defined post hoc",
    "la_top_archetypes": "The three largest archetypes of each complete window at C·W·T (class + "
                         "wings + tilt) and C·U (class + units), with their share of the window, "
                         "and what the three hold together",
}

COLUMNS = {
    "la_top_archetypes": ["level", "window", "aircraft", "top 1", "top 2", "top 3",
                          "top 3 together"],
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
_LEVEL_SHORT = {"A0": "C", "A1t": "C·W·T", "A0c": "C·U"}


def _print_top(t):
    t = t.copy()
    t = t[t["level"].astype(str).isin(["A1t", "A0c"])
          & ~t["window"].astype(str).str.contains("partial")]
    import re
    for c in ("top 1", "top 2", "top 3"):
        if c in t.columns:
            t[c] = [re.sub(r" (\d+)%$", r" (\1 %)", _tm.archetype_label(a, str(l)))
                    for a, l in zip(t[c], t["level"])]
    if "top 3 together" in t.columns:
        t["top 3 together"] = [f"{float(x):.0%}".replace("%", " %") for x in t["top 3 together"]]
    t["level"] = t["level"].astype(str).map(lambda v: _LEVEL_SHORT.get(v, v))
    return t.rename(columns={"top 1": "largest", "top 2": "second", "top 3": "third",
                             "top 3 together": "the three together"})


def _print_levels(t):
    t = t.copy()
    for c in t.columns[1:]:
        t[c] = t[c].astype(str).str.replace("(subsystem weighting only)", "(main weighting only)",
                                            regex=False)
    ren = {}
    for c in t.columns:
        if " — " in c:
            code = c.split(" — ")[0]
            ren[c] = f"{code} (post hoc)" if code == "F" else code
    return t.rename(columns=ren)


PRINT = {
    "la_top_archetypes": _print_top,
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
        for lvl, key in (("family_b", "f"), ("A0", "c")):
            r = b[b["level"].astype(str).eq(lvl) & b["window"].astype(str).eq("2020-23")]
            if len(r):
                out[f"sm_bal_{key}_2023"] = f"{float(r['D2'].iloc[0]):.2f}"
                out[f"sm_bal_{key}_2023_lo"] = f"{float(r['D2 permutation low'].iloc[0]):.2f}"

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
        "**Lift + Cruise draws level with Tilt Rotor in 2016-19 and leads in 2020-23.** Tilt "
        "Rotor falls from {tk_tr_w1} of the earliest window's aircraft to {tk_tr_w4} in 2020-23 "
        "while Lift + Cruise rises from {tk_slc_w1} to {tk_slc_w4}; with CVT ({tk_cvt_w4}) the "
        "three hold {sm_top3_a0_w4} of the recent aircraft. The earliest window rests on "
        "{sm_w1_n} aircraft against {sm_w4_n} at the recent end, so its shares are coarse",

    "sm_evtolnews_check":
        "**In the balance of Lift + Cruise against the tilting classes no difference from the "
        "directory is detected, in any window; the two part on the small classes.** Lift + "
        "Cruise is {sm_evn_lc2_p_2023} of the two classes' 2020-23 aircraft in the record and "
        "{sm_evn_lc2_d_2023} in the directory (p {sm_evn_p_bal_2023}; p {sm_evn_p_bal_lo} or more "
        "in every window); Vectored Thrust is the larger in every window of both, and Lift + "
        "Cruise rises in both, from {sm_evn_lc_p_w1} to {sm_evn_lc_p_2023} and from "
        "{sm_evn_lc_d_w1} to {sm_evn_lc_d_2023} (neither rise detected alone, p "
        "{sm_evn_p_change_lo} or more). Wingless multicopters ({sm_evn_wm_d_2023} of the "
        "directory's 2020-23 aircraft against {sm_evn_wm_p_2023}, p {sm_evn_p_wm_2023}) and, "
        "early on, Hover Bikes ({sm_evn_hb_d_w1} against {sm_evn_hb_p_w1}) are far more common in "
        "the directory, and Wingless falls in the record while it rises there. The Tilt Rotor "
        "crossover is not checked: the directory pools Tilt Rotor with CVT and Tilt Wing",

    "sm_family_yearly":
        "**On the aircraft still in force the family holds more than half of 2020 and of 2021 — "
        "{sm_fy_fi_2020} and {sm_fy_fi_2021} — and so meets condition 1; on all aircraft it does "
        "not, because 2020 stops at exactly half ({sm_fy_fa_2020}).** The margin is small: "
        "{sm_fy_fik_2020} of {sm_fy_ni_2020} and {sm_fy_fik_2021} of {sm_fy_ni_2021} aircraft. "
        "In 2022 and 2023 the family falls back to {sm_fy_fi_2022} and {sm_fy_fi_2023} of the "
        "in-force aircraft, in the two years whose in-force base is least complete, so the record "
        "cannot yet say whether the fall is real",

    "sm_dd_conditions":
        "**Condition 2 is met by F and by the class level in 2020-23, and by C·U only in the two "
        "earliest windows; condition 3 is met at every level in 2020-23, under the main weighting "
        "only.** (i) F's ²D in 2020-23 is {sm_bal_f_2023} against a band from {sm_bal_f_2023_lo}: "
        "fewer large designs in play than chance gives that window. The class level sits just "
        "under its band ({sm_bal_c_2023} against {sm_bal_c_2023_lo}). (ii) In 2020-23 ΔQ is "
        "{sm_q_main_2023}, past the lower edge of its band at {sm_q_main_2023_lo}; under equal "
        "field weights it is {sm_q_alt_2023}, inside its band (edge {sm_q_alt_2023_lo})",

    "la_dd_levels":
        "**Only the family F meets the three conditions in the same period: 2020-23, with "
        "condition 1 met in {sm_fy_met} on the aircraft in force.** At C, C·W·T and C·U condition "
        "1 fails in every read year — the largest archetype reaches at most {sm_dd_max_rest} of a "
        "year's in-force aircraft ({sm_dd_max_rest_name}, {sm_dd_max_rest_year}), {sm_dd_max_cwt} "
        "at C·W·T and {sm_dd_max_cu} at C·U — so no class and no archetype is a dominant design",

    "la_top_archetypes":
        "**Below the family, the recent aircraft are three branches: one-wing Lift + Cruise, "
        "one-wing Tilt Rotor and one-wing CVT hold {sm_top3_a1t_w4} of 2020-23 together.** The "
        "same three lead every complete window, and the lead passed once, from Tilt Rotor to Lift "
        "+ Cruise, in 2016-19. At C·U the three largest hold {sm_top3_a0c_w4} of 2020-23: the "
        "branches are settled, their insides are not",
}

# ---------------------------------------------------------------------------------------------
# the reading of the verdict, after the items (C60: itemised; no takeaway repeated)
# ---------------------------------------------------------------------------------------------
AFTER = {
    "3.2": (
        "**Reading the verdict.**\n\n"
        "- **The pass rests on three choices, and each is shown both ways.** The family F and the "
        "in-force base were chosen after the first readings, and condition 3 holds under the "
        "main weighting only. Keep F but count every aircraft of the year, or weight every field "
        "equally, and the family fails a condition.\n"
        "- **What holds under every choice: the dominant design is a layout, not a class.** It is the layout two classes share — a fixed wing carrying many "
        "rotors, with cruise thrust from dedicated propellers or from some of the rotors tilted "
        "forward.\n"
        "- **The era, on the frame of the Method.** At C·W·T and C·U the recent windows read as an "
        "era of ferment: no archetype holds more than {sm_dd_max_fine} of a year, and ²D is "
        "inside its band or above it. At the class level the recent window concentrates — ²D just under its "
        "band, Q falling — with no class near half. The family F shows the pattern of a dominant "
        "design emerging in 2020-21: past half, fewer designs in play, aircraft more alike; the "
        "years after it are too incomplete to say whether it held.\n"
    ),
}

# ---------------------------------------------------------------------------------------------
# the Answer box (the last bullet is left for 3.3-3.4, written in sm_text_ch3b)
# ---------------------------------------------------------------------------------------------
ANSWER = (
    # 2026-09-27, author: lead with the dominant design and say exactly what it is — a branch
    # that cuts across the usual eVTOL classes — never "there is no dominant design"
    "**eVTOL has a dominant design, but it is not one of the classes the sector is usually "
    "sorted into: it is a branch that cuts across two of them — Lift + Cruise together with the "
    "CVT aircraft that tilt a rotor set on a fixed wing, the layout of a fixed wing carrying many "
    "rotors. That family meets all three dominant-design conditions in 2020-23 on the aircraft "
    "still in force; no single class or archetype does.**\n\n"
    "- **Lift + Cruise has overtaken Tilt Rotor.** Tilt Rotor falls from {tk_tr_w1} to "
    "{tk_tr_w4} of the aircraft between the earliest window and 2020-23, Lift + Cruise rises "
    "from {tk_slc_w1} to {tk_slc_w4}. Against the evtol.news directory no difference is "
    "detected in the balance between Lift + Cruise and the tilting classes, in any window; the "
    "directory pools Tilt Rotor with CVT, so the crossover itself has no outside check.\n"
    "- **Condition 1: the family holds more than half of 2020 and 2021 on the aircraft in "
    "force** ({sm_fy_fi_2020}, {sm_fy_fi_2021}); on all aircraft 2020 stops at "
    "{sm_fy_fa_2020}. In 2022-23, years still largely under examination, it falls to "
    "{sm_fy_fi_2022} and {sm_fy_fi_2023}.\n"
    "- **Conditions 2 and 3 are met by the family in 2020-23**, condition 3 under the main "
    "weighting only. At C, C·W·T and C·U no period meets all three, and no archetype passes "
    "{sm_dd_max_rest} of a year's in-force aircraft.\n"
    "- **What the result rests on.** The family and the in-force base were chosen after the "
    "first readings. Counted on all aircraft, 2020 stops at exactly half, one aircraft short of "
    "a majority; with equal field weights, condition 3 is not met. Counted only on aircraft "
    "with a granted patent still in force — none of them still under examination — the family "
    "holds {sm3_f_gl_2020} of 2020 and {sm3_f_gl_2021} of 2021, so the majority is not an "
    "artefact of pending applications.\n"
    "- [3.3–3.4 bullet: to be added]"
)

NUMBERS.update({
    # 2026-09-27: the family on granted-and-live aircraft only (no pending applications)
    "sm3_f_gl_2020": dict(table="la_family_yearly", where=("priority year", "2020"),
                          col="F share, granted and live", fmt="pct"),
    "sm3_f_gl_2021": dict(table="la_family_yearly", where=("priority year", "2021"),
                          col="F share, granted and live", fmt="pct"),
})
