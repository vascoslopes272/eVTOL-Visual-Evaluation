#!/usr/bin/env python3
"""Build the short document for the advisors from the finished brief.

    python3 scripts/render_advisor.py

Writes ``LABELLING_ANALYSIS_FOR_REVIEW.md`` next to the brief. It holds, in order: a short
note on how to read it, the chapter answers in one page, a decision table with one row per
sub-question (what the record shows, where the evidence sits in the brief, and an empty column
for the advisor's mark), then each chapter's Answer and its key figure.

The chapter Answers and the figures are lifted from ``LABELLING_ANALYSIS_BRIEF.md`` through the
digest's own functions, so they cannot drift from the brief. The one-line findings of the
decision table are written here (``ROWS``) and must be revised when a result in the brief
changes; the figure and table numbers in them are resolved from the brief at build time.
Chapter M is left out on the author's ruling (2026-09-26: "a different thing for later").
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_digest as rd  # noqa: E402

OUT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/"
           "1639_LABELLED/1_labelling_analysis/labelling_analysis")

TITLE = "Labelling Analysis: the findings, for review"

INTRO = (
    "This document gathers the answers of the Labelling Analysis of the eVTOL patent record, "
    "one chapter per page, each with the figure its answer rests on. The method, the full "
    "evidence and every table sit in the accompanying *Labelling Analysis in brief*, and the "
    "figure and table numbers below refer to it.\n\n"
    "The table in section 2 lists the fifteen questions the analysis answers. For each one, a "
    "mark in the last column is enough: whether the result belongs in the thesis as it stands, "
    "in a shorter form, or not at all. Reading takes about fifteen minutes."
)

#: the chapters the advisors see, with the short title each gets (chapter M is left out)
CHAPTERS = [c for c in rd.CHAPTERS if c[0] != "M"]

#: one row per sub-question: number, short question, what the record shows, evidence.
#: Evidence entries are figure stems ("fig:<stem>") or table caption openings ("tab:<text>").
ROWS = [
    ("1.1", "How fast has eVTOL patenting grown, and how early does it show a design?",
     "eVTOL patent families double every 3.8 years, against 4.7 for aeronautics and 10.7 for all "
     "patents. Firms file a median of 4 years before their first flight.",
     ["fig:filings_per_year", "fig:ari_clock"]),
    ("1.2", "What share of the patented aircraft is still protected?",
     "44 % of the aircraft filed up to 2019 have no patent left in force. No difference between "
     "classes is claimed, because it depends on how duplicate patents are counted.",
     ["fig:sm_force_aircraft"]),
    ("1.3", "How faithfully do the patented aircraft describe the aircraft that get built?",
     "Where a public aircraft exists, the drawing gives its architecture class for 88 of 98. "
     "The aircraft public sources cover are company-backed, recent and carry more propulsors, "
     "so they cannot stand for the whole record.",
     ["tab:Three sources of a class", "tab:Do the aircraft above TRL 2"]),
    ("2.1", "What is an eVTOL design made of?",
     "The variety sits in the propulsion. The median aircraft carries 5 propulsive units, and "
     "306 of 633 place them on exactly two stations.",
     ["tab:The label fields", "fig:sm_propulsion_compact"]),
    ("2.2", "How are designs grouped into archetypes?",
     "Four levels of detail are read: the class, the class with its unit count, the class with "
     "wings and tilt, and the family F. Finer levels split the record into too many "
     "one-aircraft designs to be read.",
     ["tab:The four archetype levels"]),
    ("2.3", "Where do designs concentrate, and is the design space still opening?",
     "Half of the 2020-23 aircraft sit in 7 archetypes, yet the largest holds only 10 %. No new "
     "class has appeared in the last 376 aircraft, while new combinations of wings and tilt "
     "still appear.",
     ["fig:zones", "fig:discovery_curve"]),
    ("3.1", "Which architectures gain and which fade?",
     "Lift + Cruise overtakes Tilt Rotor, from 26 % to 32 % of the aircraft against Tilt "
     "Rotor's fall from 32 % to 21 %. The evtol.news directory shows the same balance between "
     "Lift + Cruise and the tilting classes.",
     ["fig:atlas_arch_time", "fig:sm_evtolnews_check"]),
    ("3.2", "Is there a dominant design?",
     "Yes, and it is a branch across two classes: Lift + Cruise together with the CVT that tilt "
     "a rotor set on a fixed wing. It meets all three conditions in 2020-23 on the aircraft "
     "still in force. The grouping was chosen after the first readings.",
     ["fig:sm_family_yearly", "fig:sm_dd_conditions", "tab:The dominant-design verdict"]),
    ("3.3", "Do designs converge inside each class?",
     "No class converges on one layout. Lift + Cruise keeps lift rotors on booms as its leading "
     "layout, and the leading Tilt Rotor layout moves from one tilting set to two sets on two "
     "stations.",
     ["fig:sm_class_configs"]),
    ("3.4", "What drives the changes inside the classes?",
     "Tilt Rotor adds a second tilting set and its median units go from 2 to 4. CVT moves its "
     "fixed rotors onto booms and loses its ducts. Per propulsive unit, tilting sets fall.",
     ["fig:sm_driver_trajectory", "tab:The traces that move"]),
    ("4.1", "Which kinds of filer file, and does any firm hold enough of a class to decide it?",
     "Organisations file 70 % of the aircraft, spread over 208 firms, 134 of them with a single "
     "aircraft. No firm holds more than 20 % of any class. Among the index firms, the "
     "better-funded filed earlier (9 firms).",
     ["fig:sm_who_files", "fig:sm_one_firm", "fig:sm_ari_funding"]),
    ("4.2", "Do first-time or returning firms reshape the design space?",
     "Once Bell / Textron is set aside, first-time and returning firms choose the same classes. "
     "A firm that files again stays in the large classes and leaves the small ones.",
     ["fig:sm_entry_split", "fig:sm_successions"]),
    ("5.1", "What does each region file, and how has its mix moved since 2012?",
     "Only North America's mix moved clearly: CVT rose to 35 % of its aircraft. After 2020 each "
     "region settled on a different number of propulsive units.",
     ["fig:sm_region_design"]),
    ("5.2", "In what order do the regions take up each class?",
     "North America files first (median 2018), Europe in 2019 and Asia-Pacific in 2020. North "
     "America's recent fall in share is real, and publication delay does not explain it.",
     ["fig:sm_region_timing"]),
    ("5.3", "Do the regions converge on the same design?",
     "By 2020-23 the three regions hold the family F in similar measure, 46 % to 57 %. North "
     "America's lean to tilting aircraft survives without Bell / Textron.",
     ["fig:sm_region_converge"]),
]

MARK = "yes · shorter · no"


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


def build() -> Path:
    md = rd.read_brief(OUT / "LABELLING_ANALYSIS_BRIEF.md")
    ans = rd.answers(md)
    figs, tabs = numbering(md)

    doc = [f"# {TITLE}", "", "## 1. How to read this document", "", INTRO, "",
           "### The answers in one page", ""]
    for cid, short in CHAPTERS:
        if cid in ans:
            doc += [f"**{short}** {rd.lead(ans[cid])}", ""]

    doc += ['<div class="keep" markdown="1">', "",
            "## 2. The fifteen questions, for a decision", "", "</div>", "",
            "| | Question | What the record shows | Evidence in the brief | Keep in the thesis? |",
            "|---|---|---|---|---|"]
    for num, q, finding, refs in ROWS:
        doc.append(f"| {num} | {q} | {finding} | {evidence(refs, figs, tabs)} | {MARK} |")
    doc.append("")

    for k, (cid, short) in enumerate(CHAPTERS, start=3):
        if cid not in ans:
            continue
        doc += ['<div class="keep" markdown="1">', "",
                f"## {k}. {short}", "", "</div>", "",
                '<div class="answer-box" markdown="1">', "", ans[cid], "", "</div>", ""]
        for stem, caption in rd.FIGURES.get(cid, [])[:1]:      # one figure per chapter
            fig = rd.figure_line(md, stem, caption)
            if fig:
                doc += [fig, ""]

    doc += ['<div class="keep" markdown="1">', "",
            f"## {len(CHAPTERS) + 3}. What this record cannot tell", "", "</div>", "",
            "- **Noise, weather, payload, mass and size** are neither labelled nor stated in the "
            "patents.",
            "- **Mission** is stated only for the aircraft with a public page, is mostly "
            "unspecified even there, and that subset does not stand for the record.",
            "- **Certification and autonomy** have no field in this record.",
            "- **Commercial outcome** is not in a patent. The record shows what was designed, "
            "never what will sell.", ""]

    path = OUT / "LABELLING_ANALYSIS_FOR_REVIEW.md"
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(build())
