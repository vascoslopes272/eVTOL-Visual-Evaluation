#!/usr/bin/env python3
"""Build the short document for the advisors from the finished brief.

    python3 scripts/render_advisor.py

Writes ``LABELLING_ANALYSIS_FOR_REVIEW.md`` next to the brief. It holds, in order:

1. how to read it;
2. the map: the five chapters and why the analysis divides this way;
3. the decision table, one row per sub-question (what the labelled dataset shows, where the
   evidence sits in the brief, and a mark column for the advisor);
4. each chapter's Answer, lifted verbatim from the brief, with its one key figure;
5. what the labelled dataset cannot tell;
6. the author's proposal of what to keep, in three tiers, for the advisors to react to.

The chapter Answers and the figures are lifted from ``LABELLING_ANALYSIS_BRIEF.md`` through the
digest's own functions, so they cannot drift from the brief. The one-line findings of the
decision table (``ROWS``) and the proposal (``PROPOSAL``) are written here and must be revised
when a result in the brief changes; the figure and table numbers are resolved from the brief at
build time. Rebuilt 2026-09-28 against the five-chapter brief (Tilt Propulsor, archetype sets,
"labelled dataset"). Chapter M is left out on the author's ruling (2026-09-26).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_digest as rd  # noqa: E402

OUT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/"
           "1639_LABELLED/1_labelling_analysis/labelling_analysis")

TITLE = "Labelling Analysis: the questions, the findings, and what to keep"

INTRO = (
    "This document summarises the Labelling Analysis of the eVTOL patent corpus so that a "
    "decision can be taken on what enters the thesis. The full method and evidence are in the "
    "accompanying *Labelling Analysis in brief*; every figure and table number below is that "
    "document's.\n\n"
    "Section 2 sets out the five chapters and why the analysis divides this way. Section 3 is "
    "the decision table: one row per question, fifteen in all, each with what the labelled "
    "dataset shows and where the evidence sits. For each question a mark in the last column is "
    "enough: **core** (in the thesis as it stands), **shorter** (in a reduced form) or "
    "**drop**. Section 4 gives each chapter's answer as the brief prints it, with the one "
    "figure it rests on most, and section 5 what the labelled dataset cannot tell. Section 6 "
    "gives the author's own proposal of what to keep, to react to rather than to accept.\n\n"
    "Reading time is about fifteen minutes."
)

MAP = [
    ("1. The material.",
     "Before anything is read from the patents, the material has to be established: how much "
     "of it there is and how fast it has grown, how much of it is still protected, and whether "
     "the aircraft drawn in patents resemble the aircraft that get built. The first chapter "
     "answers those three points, so that the later chapters know what their counts stand "
     "for."),
    ("2. The design space.",
     "A design has to be defined before its movement can be followed. The second chapter reads "
     "what an eVTOL design is made of, groups the aircraft into archetypes within a few "
     "chosen archetype sets, and shows where the designs concentrate and "
     "whether new kinds still appear."),
    ("3. The movement and the dominant-design test.",
     "With the design space fixed, the third chapter follows it over twenty years of filing: "
     "which classes gain and which fade, whether one design has come to dominate, whether "
     "designs settle inside each class, and which traces of design drivers move."),
    ("4. The filers.",
     "The designs are filed by someone. The fourth chapter asks who files, whether any single "
     "firm is large enough to steer a class, and whether the mix moves with new firms "
     "arriving or with firms already filing that change course."),
    ("5. The regions.",
     "The last chapter reads the same variables by applicant region, North America, Europe "
     "and Asia-Pacific: what each files, in what order the regions take up each class, and "
     "whether they end on the same design."),
]

#: the chapters of section 4: brief chapter id, heading, key figure stem, caption
#: ({n} is replaced by the figure's number in the brief)
CHAPTERS = [
    ("1", "Chapter 1: growth, protection and how faithful the drawings are",
     "filings_per_year",
     "Unique aircraft per priority year by applicant region (i), and how fast eVTOL patenting "
     "grows against three worldwide baselines, each fitted over 2005-2023 (ii). Brief, "
     "Figure {n}."),
    ("2", "Chapter 2: the design space",
     "zones",
     "The class + units archetypes with five aircraft or more: where the 2016-23 aircraft "
     "concentrate and how many filers stand behind them, with the crowded core ringed (i), and "
     "each archetype's aircraft per priority window (ii). Brief, Figure {n}."),
    ("3", "Chapter 3: the movement and the dominant design",
     "sm_family_yearly",
     "The Lift + Cruise + CVT\\* family F per priority year: its share of the aircraft with a "
     "patent in force (solid) and of all aircraft (dashed), against the 50 % line. F was "
     "defined after the first readings of the data. Brief, Figure {n}."),
    ("4", "Chapter 4: the filers",
     "sm_who_files",
     "Who files: how much of the labelled dataset the largest organisations hold (i), the "
     "filer types in patents and in aircraft (ii), and first-time against returning filers per "
     "window (iii). Brief, Figure {n}."),
    ("5", "Chapter 5: the regions",
     "sm_region_design",
     "What each region files, all years together and per priority window: class, propulsor "
     "units and tilting, with the trend from 2012 above each region's chart. Brief, "
     "Figure {n}."),
]

#: one row per sub-question: number, short question, what the labelled dataset shows, evidence.
#: Evidence entries are figure stems ("fig:<stem>") or table caption openings ("tab:<text>").
ROWS = [
    ("1.1", "How fast has eVTOL patenting grown, and how early does it show a design?",
     "Architecture patents double every 3.8 years, against 4.7 for aeronautics and 10.7 for "
     "all patenting; counted in families, 1.26 times as fast as aeronautics (1.14 to 1.39), an "
     "edge that can no longer be told from 1 when the fit ends at 2019. Firms file a median of "
     "4 years before their first flight (8 of the 11 index firms that have flown).",
     ["fig:filings_per_year", "fig:ari_clock", "tab:The index firms that file"]),
    ("1.2", "What share of the patented aircraft is still protected, and does it differ "
     "between classes?",
     "44 % of the 356 aircraft filed up to 2019 have no patent left in force. The classes "
     "differ narrowly (chi-square p 0.035; CVT 57 %, Lift + Cruise 52 %, Tilt Propulsor 35 %, "
     "Multirotor 30 %), and part of the difference comes from one patent that describes four "
     "Multirotor aircraft.",
     ["fig:sm_force_aircraft"]),
    ("1.3", "How faithfully do the patented aircraft describe the aircraft that get built?",
     "Where a public aircraft exists, the drawing gives its architecture class for 88 of 98 "
     "(95 % interval 0.83 to 0.94). The aircraft above TRL 2 and those of the index firms are "
     "company-backed, recent and carry more propulsor units, so they cannot stand for the rest.",
     ["tab:Three sources of a class", "tab:Do the aircraft above TRL 2",
      "tab:Do the index-firm aircraft"]),
    ("2.1", "What is an eVTOL design made of: which features vary?",
     "The tail and the propulsor-unit count vary most: their most common answers hold only "
     "30 % and 23 % of the aircraft. The median aircraft carries 5 propulsor units, and 306 "
     "of 633 place them on two stations.",
     ["tab:The label fields", "fig:sm_propulsion_compact"]),
    ("2.2", "How are designs grouped into archetypes, and in which archetype set is the "
     "space read?",
     "Four archetype sets are read: the class, class + wings + tilt, class + units, and the "
     "Lift + Cruise + CVT\\* family F, chosen after the first readings. The same aircraft are 12 "
     "classes, 40 archetypes at C·W·T and 43 at C·U, and F is the largest single design, with "
     "40 % of all aircraft.",
     ["tab:The four archetype sets"]),
    ("2.3", "Where do designs concentrate, and is the design space still opening?",
     "Half of the 2020-23 aircraft sit in 7 class + units archetypes (10 in 2016-19), yet the "
     "largest holds only 10 %. No new class has appeared in the last 376 aircraft, while at "
     "C·W·T the last 100 aircraft brought 4.0 new archetypes against 1.5 by chance.",
     ["fig:sm_archetype_filers", "fig:zones", "fig:discovery_curve"]),
    ("3.1", "How do the class shares change over time, and does the public directory agree?",
     "Lift + Cruise rises from 26 % to 32 % of the aircraft between the earliest window and "
     "2020-23 while Tilt Propulsor falls from 32 % to 21 %. The evtol.news directory shows a "
     "similar mix, but it pools Tilt Propulsor with CVT and Tilt Wing, so the crossover has no "
     "outside check.",
     ["fig:atlas_arch_time", "fig:sm_evtolnews_check"]),
    ("3.2", "Is there a dominant design?",
     "Only the family F, Lift + Cruise with the fixed-wing CVT, meets all three conditions in "
     "2020-23 (52.6 % and 58.3 % of the in-force aircraft of 2020 and 2021); no class or "
     "archetype passes 40.4 % of a year. F, the in-force base and the yearly step were chosen "
     "after the first readings, and on all aircraft 2020 stops at 50.0 %.",
     ["fig:sm_family_yearly", "fig:sm_dd_conditions", "tab:The dominant-design verdict"]),
    ("3.3", "Do designs converge inside each class?",
     "No class converges on one layout; what changes is which layout leads. Lift + Cruise "
     "keeps lift units on booms (47 % in 2020-23), CVT's leader becomes tilting propulsors "
     "with the fixed units on booms (53 %), and Tilt Propulsor spreads from one tilting set "
     "(73 % up to 2011) over three layouts.",
     ["fig:sm_class_configs"]),
    ("3.4", "What drives the changes inside the classes?",
     "Tilt Propulsor adds a second tilting set and its median units go from 2 to 4; CVT moves "
     "its fixed units onto booms (25 % to 62 %, p 0.02) and sheds its ducts (75 % to 32 %). "
     "Of the 12 traces that move, only the boom and station traces point to a single driver, "
     "distributed propulsion.",
     ["fig:sm_driver_trajectory", "fig:sm_driver_traces", "tab:The traces that move"]),
    ("4.1", "Which kinds of filer file, and does any single firm hold enough of a class to "
     "decide its share?",
     "Organisations file 70 % of the aircraft, spread over 208 of them, 134 with a single "
     "aircraft, and no filer holds more than 20 % of any class. On the 9 index firms with a "
     "disclosed amount, the better-funded filed their first patent earlier (p 0.031), with no "
     "relation detected to aircraft held or to the lead to first flight.",
     ["fig:sm_who_files", "fig:sm_one_firm", "fig:sm_ari_funding"]),
    ("4.2", "Do first-time or returning firms reshape the design space, and where does a "
     "firm's next design land?",
     "First-time firms bring most of each window's aircraft, and their classes differ from "
     "those of returning firms only in 2016-19 (p 0.015), where 33 of the 58 returning "
     "aircraft are Bell / Textron's. A firm's next aircraft stays in Lift + Cruise (62 %) or "
     "Tilt Propulsor (57 %) and mostly leaves Tilt Wing (15 % stay).",
     ["fig:sm_entry_split", "fig:sm_successions"]),
    ("5.1", "What does each region file, and how has its mix moved since 2012?",
     "All years together, North America leads with Tilt Propulsor (32 %) and files the most "
     "tilting aircraft (66 %); Europe and Asia-Pacific lead with Lift + Cruise (32 % and 34 %). "
     "From 2012 only North America's class mix moves, CVT 23 % to 9 % to 35 %, while North "
     "America adds units in the five-to-six band and Europe in the seven-to-eight band.",
     ["fig:sm_region_countries", "fig:sm_region_design"]),
    ("5.2", "In what order do the regions take up each class, and is North America's recent "
     "fall real?",
     "Median priority year: North America 2018, Europe 2019, Asia-Pacific 2020, with "
     "Asia-Pacific 3-4 years late on the older classes; from 2016 onward only its delay on "
     "Tilt Propulsor stays detected. North America's fall from 44 % of 2021 to 22 % of 2023 "
     "is not a publication delay.",
     ["fig:sm_region_timing"]),
    ("5.3", "Do the regions converge on the same design, and does any lean rest on one firm?",
     "In 2020-23 the family F holds 47 % of North American, 57 % of European and 46 % of "
     "Asia-Pacific aircraft, with no regional difference detected in any window. North "
     "America's lean to tilting aircraft survives without Bell / Textron (59 %, p 0.019).",
     ["fig:sm_region_converge"]),
]

MARK = "core · shorter · drop"

LIMITS = [
    "- **Noise, weather, payload, mass and size** are neither labelled nor stated in the "
    "patents, and the drawings are unscaled.",
    "- **Mission** is stated only for the aircraft with a public page, is mostly unspecified "
    "even there, and that subset does not stand for the labelled dataset.",
    "- **Certification and autonomy** have no field in the labels.",
    "- **Powertrain** is one yes/no field: battery, hybrid and fuel cell are not told apart.",
    "- **Commercial outcome** is not in a patent. The labelled dataset shows what was "
    "designed, never what will sell.",
]

#: the author's proposal. Each entry: question, one line on its two axes (method, sector).
PROPOSAL = [
    ("Core", "the thesis rests on these", [
        ("1.1", "*Method:* a doubling time fitted over 2005-2023 with a bootstrap interval; the "
         "brief itself notes that the edge over aeronautics can no longer be told from 1 when "
         "the fit ends at 2019. *Sector:* how fast eVTOL patenting grows against patenting "
         "at large is the sector's headline figure."),
        ("2.1", "*Method:* plain counts over the label fields, with no modelling choice to "
         "defend. *Sector:* it defines what an eVTOL design is made of, the foundation of the "
         "taxonomy every later result uses."),
        ("2.3", "*Method:* the crowded core and empty rim are set by rule, not by eye, and the "
         "discovery curve is read against a random-order reference. *Sector:* where designers "
         "concentrate today and whether new kinds still appear is the map of the field."),
        ("3.1", "*Method:* shares per window, checked in direction against an outside "
         "directory of 1 000 dated aircraft. *Sector:* which classes gain and which fade is "
         "the most direct question the sector puts to the patents."),
        ("3.2", "*Method:* three conditions of different kinds, with the thresholds fixed "
         "before any curve was drawn; F, the in-force base and the yearly step were chosen "
         "after the first readings, and this is stated wherever they appear. *Sector:* the "
         "centrepiece, a dominant morphology across Lift + Cruise and the fixed-wing CVT."),
        ("3.3-3.4", "*Method:* per-class configurations (rules chosen after the shares "
         "were seen) and Spearman trends on every year, with the pooled contrast shown; CVT moving its fixed units onto booms is detected "
         "(p 0.02). *Sector:* the drivers of change, and the move that motivated defining F."),
    ]),
    ("Shorter", "kept in a reduced form", [
        ("1.2", "*Method:* the 44 % out-of-force share is robust; the class difference is "
         "narrow (p 0.035) and rests partly on one patent that describes four Multirotor "
         "aircraft. *Sector:* useful context, not a result to build on."),
        ("1.3", "*Method:* 88 of 98 agree, with a 95 % interval of 0.83 to 0.94, but the "
         "matched aircraft are company-backed and recent and cannot stand for the rest. "
         "*Sector:* it supports the use of drawings, stated in a paragraph."),
        ("2.2", "*Method:* necessary, since every later count names its archetype set, and the "
         "four screens were fixed before the sets were compared. *Sector:* it reads as "
         "methodology, so it belongs in the method chapter."),
        ("4.1", "*Method:* the crowd structure of filers (208 organisations, no filer above "
         "20 % of a class) is robust; the funding read rests on 9 firms and detects one "
         "relation of three, an earlier first patent. *Sector:* who files is relevant; the "
         "funding read is kept to a sentence."),
        ("5.1", "*Method:* one robust regional difference: North America keeps the tilting "
         "architectures (66 % of its aircraft, still 59 % without Bell / Textron). *Sector:* "
         "the regional lean worth reporting, with the median order North America, Europe, "
         "Asia-Pacific added in one sentence from 5.2."),
        ("5.3", "*Method:* no regional difference in F is detected in any window. *Sector:* "
         "the regions hold the family in similar measure (46 % to 57 %), which corroborates "
         "3.2."),
    ]),
    ("Drop", "not carried into the thesis", [
        ("4.2", "*Method:* the order of a firm's aircraft rests on this dataset's architecture "
         "filings alone, and no outside source could corroborate it. *Sector:* a firm's next "
         "design is a relevant question that this material cannot answer firmly."),
        ("5.2", "*Method:* read on the aircraft of 2016 onward, the regional delays shrink and "
         "only Asia-Pacific's on Tilt Propulsor stays detected. *Sector:* the median order "
         "North America, Europe, Asia-Pacific survives as one sentence in 5.1."),
    ]),
]


def numbering(md: str):
    figs = {m.group(2): m.group(1)
            for m in re.finditer(r"^!\[Figure (\d+) — [^\]]*\]\(figures/([a-z0-9_]+)\.png\)",
                                 md, re.MULTILINE)}
    tabs = [(m.group(1), m.group(2))
            for m in re.finditer(r"^\*\*Table (\d+) — (.*)$", md, re.MULTILINE)]
    return figs, tabs


def evidence(refs, figs, tabs) -> str:
    out = []
    for ref in refs:
        kind, key = ref.split(":", 1)
        if kind == "fig":
            n = figs.get(key)
            if n is None:
                print(f"  ! figure not in the brief: {key}")
                continue
            out.append(f"Figure {n}")
        else:
            hit = next((n for n, cap in tabs if cap.startswith(key)), None)
            if hit is None:
                print(f"  ! table not in the brief: {key}")
                continue
            out.append(f"Table {hit}")
    return ", ".join(out)


def keep(heading: str) -> list:
    return ['<div class="keep" markdown="1">', "", heading, "", "</div>", ""]


def build() -> Path:
    md = rd.read_brief(OUT / "LABELLING_ANALYSIS_BRIEF.md")
    ans = rd.answers(md)
    figs, tabs = numbering(md)

    doc = [f"# {TITLE}", "", "## 1. How to read this document", "", INTRO, ""]

    doc += keep("## 2. The map: five chapters and why they divide this way")
    for head, text in MAP:
        doc += [f"**{head}** {text}", ""]

    doc += keep("## 3. The fifteen questions, for a decision")
    doc += ["| | Question | What the labelled dataset shows | Evidence in the brief | Keep? |",
            "|---|---|---|---|---|"]
    for num, q, finding, refs in ROWS:
        doc.append(f"| {num} | {q} | {finding} | {evidence(refs, figs, tabs)} | {MARK} |")
    doc.append("")

    doc += keep("## 4. The five answers, each with its key figure")
    doc += ["Each answer below is the one the brief prints, word for word.", ""]
    for cid, heading, stem, caption in CHAPTERS:
        if cid not in ans:
            print(f"  ! no answer block for chapter {cid}")
            continue
        doc += ['<div class="keep" markdown="1">', "", f"### {heading}", "", "</div>", "",
                '<div class="answer-box" markdown="1">', "", ans[cid], "", "</div>", ""]
        n = figs.get(stem)
        if n is None:
            print(f"  ! key figure not in the brief: {stem}")
            continue
        fig = rd.figure_line(md, stem, caption.replace("{n}", n))
        if fig:
            doc += [fig, ""]

    doc += keep("## 5. What this labelled dataset cannot tell")
    doc += LIMITS + [""]

    doc += keep("## 6. The author's proposal: what to keep")
    doc += ["What follows is the author's own position, set out for the professors to react "
            "to. Each question is placed in one of three tiers and justified on two axes: how "
            "robust the method behind it is, and how relevant the result is to the sector.", ""]
    for tier, gloss, entries in PROPOSAL:
        doc += [f"**{tier}** ({gloss})", ""]
        doc += [f"- **{num}.** {line}" for num, line in entries]
        doc.append("")
    doc += ["Where you disagree with a tier, a different mark in the last column of the table "
            "in section 3 is all that is needed.", ""]

    path = OUT / "LABELLING_ANALYSIS_FOR_REVIEW.md"
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(build())
