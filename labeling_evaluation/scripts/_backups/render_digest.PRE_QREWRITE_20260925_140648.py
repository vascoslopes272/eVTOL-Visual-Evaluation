#!/usr/bin/env python3
"""Generate LABELLING_ANALYSIS_DIGEST.md — the brief of the brief.

    python3 scripts/render_digest.py [--pdf] [--docx]

A THIRD view of the same data, and the shortest one: the four questions, the answer to each,
and one figure per answer. Nothing here is written and nothing here is computed. Every word of
every answer is LIFTED VERBATIM out of ``LABELLING_ANALYSIS_BRIEF.md`` — the ``div.answer-box``
blocks the brief already prints — so the digest cannot state a number the brief does not, and
re-running it after the brief changes is the only way to update it. That is the whole design:
a summary that is a copy has nothing of its own to drift.

It therefore CANNOT be run before ``render_summary.py`` has produced the brief, and it never
runs it. It writes one new set of files into the same folder and touches nothing else.

What is dropped, on purpose: the methods box, the Source/Unit/How-to-read lines, every table,
and all but one figure per chapter. A reader who wants the evidence has the brief; a reader who
wants the findings has this.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

PILLAR = Path(__file__).resolve().parent.parent
REPO = PILLAR.parent

#: the figure each chapter keeps, by the stem of its PNG, with the caption the digest prints.
#: One per chapter, two for chapter 2 because its answer rests on two separate results — the
#: test that fires nowhere, and the one move behind the drift. A stem that is not in the brief
#: is skipped with a warning rather than failing the build.
FIGURES = {
    "1": [("filings_per_year",
           "Unique aircraft per priority year, and how much faster this corpus grew than the "
           "patenting around it.")],
    "2": [("dominant_design",
           "The dominant-design test: the largest archetype of each window against the 50 % "
           "line, and evenness against the permutation band."),
          ("sm_driver_corr",
           "The one move behind the drift: a second tilting set arrives, and the units come "
           "with it.")],
    "3": [("coverage",
           "How much of the record the largest firms hold, and whether market standing tracks "
           "patenting.")],
    "4": [("atlas_region",
           "Where the aircraft come from, and the architecture mix of each region.")],
    "M": [("atlas_arch_gt",
           "Where the label read from the drawings and the whole-patent reading agree, and what "
           "they confuse.")],
}

#: the chapter order of the digest, and the short title each one is given. The brief's own
#: chapter headings are long two-clause questions; at one chapter per page the question is the
#: heading and the long form would wrap three times.
CHAPTERS = [
    ("1", "Does the patent record see the sector before it exists?"),
    ("2", "Is there one eVTOL design, or several?"),
    ("3", "Who is designing it?"),
    ("4", "Does geography shape the design?"),
    ("M", "Can the drawing alone carry the architecture?"),
]

TITLE = "Labelling Analysis — the findings"
SUBTITLE = ("The four questions and their answers, one page each. Every answer below is the "
            "answer printed in *Labelling Analysis in brief*, word for word; the evidence, the "
            "method and the tables are there, not here.")


def read_brief(path: Path) -> str:
    if not path.exists():
        sys.exit(f"the brief is not built: {path}\nrun scripts/render_summary.py first")
    return path.read_text(encoding="utf-8")


def chapter_of(line: str) -> str:
    """The chapter id a ``## `` heading opens, or ``""``."""
    m = re.match(r"^## ([\dM]) — ", line)
    return m.group(1) if m else ""


def answers(md: str) -> dict:
    """Every ``answer-box`` block of the brief, keyed by the chapter it closes.

    The blocks are lifted with their markdown intact — the lead sentence and the bullets — and
    only the ``#### Answer`` heading is dropped, because the digest supplies its own.
    """
    out, chapter, buf, inside = {}, "", [], False
    for line in md.splitlines():
        ch = chapter_of(line)
        if ch:
            chapter = ch
        if 'class="answer-box"' in line:
            inside, buf = True, []
            continue
        if inside and line.strip() == "</div>":
            inside = False
            body = [b for b in buf if not b.strip().startswith("#### ")]
            while body and not body[0].strip():
                body.pop(0)
            while body and not body[-1].strip():
                body.pop()
            if chapter and body:
                out[chapter] = "\n".join(body)
            continue
        if inside:
            buf.append(line)
    return out


def lead(block: str) -> str:
    """The bold verdict sentence a block opens on, for the one-page summary."""
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("**") and not s.startswith("- "):
            return s.strip("*").strip()
    return ""


def figure_line(md: str, stem: str, caption: str) -> str:
    """The figure as the digest prints it: the brief's own image path and width, the digest's
    own short caption. The width is reused so a figure keeps the size it was drawn for."""
    m = re.search(r"^!\[[^\]]*\]\(figures/" + re.escape(stem) + r"\.png\)(\{[^}]*\})?\s*$",
                  md, re.MULTILINE)
    if not m:
        print(f"  ! figure not in the brief, skipped: {stem}")
        return ""
    attrs = m.group(1) or '{: width="100%" }'
    return f"![{caption}](figures/{stem}.png){attrs}\n\n*{caption}*\n"


def build(brief: Path, out: Path) -> Path:
    md = read_brief(brief)
    ans = answers(md)
    missing = [c for c, _ in CHAPTERS if c not in ans]
    if missing:
        print(f"  ! no answer block found for chapter(s): {', '.join(missing)}")

    doc = [f"# {TITLE}", "", SUBTITLE, "",
           f"*{dt.date.today().isoformat()} · generated by "
           "`labeling_evaluation/scripts/render_digest.py` from "
           "`LABELLING_ANALYSIS_BRIEF.md`; every answer is that document's, verbatim.*", "",
           "## In one page", ""]
    for cid, short in CHAPTERS:
        if cid in ans:
            doc.append(f"**{short}** {lead(ans[cid])}")
            doc.append("")
    doc += ["*Each of these is expanded overleaf, with the figure that carries it.*", ""]

    for cid, short in CHAPTERS:
        if cid not in ans:
            continue
        doc += ['<div class="keep chapter-start" markdown="1">', "",
                f"## {short}", "", "</div>", "",
                '<div class="answer-box" markdown="1">', "", "#### Answer", "",
                ans[cid], "", "</div>", ""]
        for stem, caption in FIGURES.get(cid, []):
            fig = figure_line(md, stem, caption)
            if fig:
                doc += [fig, ""]

    # the limits, kept because a findings-only document without them invites over-reading
    doc += ['<div class="keep chapter-start" markdown="1">', "",
            "## What this record cannot tell you", "", "</div>", "",
            "- **Noise, weather, payload, mass and size** are not labelled and not stated in the "
            "patents. No amount of analysis reaches them.",
            "- **Mission** is stated only for the aircraft with a public page, is mostly "
            "unspecified even there, and that subset does not stand for the corpus.",
            "- **Certification and autonomy** have no field in this record at all.",
            "- **Commercial outcome** is not in a patent. The record says what was designed, "
            "never what will sell.", "",
            "*The full list, question by question, is `CANNOT_ANSWER_TABLE.md`; the evidence for "
            "every answer above is `LABELLING_ANALYSIS_BRIEF.pdf`.*", ""]

    path = out / "LABELLING_ANALYSIS_DIGEST.md"
    path.write_text("\n".join(doc) + "\n", encoding="utf-8")
    return path


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--docx", action="store_true")
    ap.add_argument("--folder", default=None, help="the labelling_analysis output folder")
    a = ap.parse_args(argv)

    if a.folder:
        out = Path(a.folder)
    else:
        sys.path.insert(0, str(PILLAR))
        from src.config_loader import load_config
        cfg = load_config()
        out = Path(cfg["dataset_facts"]["output_dir"]).parent / "labelling_analysis"

    brief = out / "LABELLING_ANALYSIS_BRIEF.md"
    md = build(brief, out)
    print(f"digest: {md}  ({md.stat().st_size / 1024:.0f} KB)")

    if a.pdf:
        pdf = md.with_suffix(".pdf")
        subprocess.run([sys.executable, str(REPO / "scripts" / "build_styled_md_pdf.py"),
                        str(md), str(pdf), "--compact"], check=True)
        pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        print(pdf.name, [l for l in pages.splitlines() if l.startswith("Pages")])
    if a.docx:
        subprocess.run([sys.executable, str(PILLAR / "scripts" / "export_brief_docx.py"),
                        "--in", str(md),
                        "--out", str(md.with_suffix(".docx"))], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
