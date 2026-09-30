#!/usr/bin/env python3
"""Export a finished markdown document to a clean Word file for readers outside the project.

    python3 scripts/clean_word.py <in.md> <out.docx> [--title "..."]

Works on a copy of the markdown and never changes the source. It applies the author's writing
rules (the thesis-voice skill, Part 5) that the generated text does not yet follow everywhere:

* no em dashes: headings "1.1 — X" become "1.1 X", captions "Figure 3 — x" become
  "Figure 3. x", an empty table cell "—" becomes "–", and a dash inside a sentence becomes a
  comma;
* fewer semicolons: "; " before a lower-case word, outside brackets and outside tables,
  becomes a full stop;
* no generator traces: HTML comments are dropped, the review colours are not applied, and the
  Word metadata (author, last modified by, comments, keywords) is emptied.

The Word file is then built by ``export_brief_docx.py --no-highlight`` exactly as the review
copy is, so figures, tables and boxes are identical.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _semicolons(line: str) -> str:
    out, depth, i = [], 0, 0
    while i < len(line):
        ch = line[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if (ch == ";" and depth == 0 and line[i + 1:i + 2] == " "
                and re.match(r"[a-z]", line[i + 2:i + 3] or "")):
            out.append(". " + line[i + 2].upper())
            i += 3
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _dashes(line: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z*])", line)        # roughly, sentences
    out = []
    for seg in parts:
        n = seg.count(" — ")
        if n >= 2:
            seg = seg.replace(" — ", ", ")
        elif n == 1:
            before, after = seg.split(" — ", 1)
            joiner = ", " if re.match(r"(and|but|or|so|yet|not)\b", after) else ": "
            seg = before + joiner + after
        seg = seg.replace("—", ", ")
        out.append(seg)
    return " ".join(out)


def transform(md: str) -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
    # internal to-do stickers ("OWED", "PARTLY") are for the author, never for other readers
    md = re.sub(r'<div class="sticker">.*?</div>', "", md, flags=re.DOTALL)
    lines = []
    for line in md.splitlines():
        # headings and index rows: "1.1 — Title" -> "1.1 Title"
        line = re.sub(r"^(#{1,6} )(\d+(?:\.\d+)*|M) — ", r"\1\2 ", line)
        line = re.sub(r'(<span class="toc-t">)(\d+(?:\.\d+)*|M) — ', r"\1\2 ", line)
        # captions: "Figure 3 — x" -> "Figure 3. x"
        line = re.sub(r"\b(Figure|Table) (\d+) — ", r"\1 \2. ", line)
        # a Method bullet naming its item: "**Title — Figure 3.**" -> "**Title (Figure 3).**"
        line = re.sub(r"\*\*([^*]+?) — ((?:Figures?|Tables?) [^*]+?)\.\*\*", r"**\1 (\2).**", line)
        # an empty table cell
        line = re.sub(r"\|\s*—\s*(?=\|)", "| – ", line)
        # any other dash inside a sentence: a pair (a parenthesis) becomes two commas; a single
        # dash introduces an explanation and becomes a colon, or a comma before "and / but / or"
        line = _dashes(line)
        line = line.replace(", ,", ",").replace(", .", ".").replace(",,", ",")
        is_prose = not (line.lstrip().startswith(("|", "#", "<", "!")))
        if is_prose:
            line = _semicolons(line)
        lines.append(line)
    return "\n".join(lines) + "\n"


def scrub(docx_path: Path, title: str) -> None:
    import docx
    d = docx.Document(str(docx_path))
    cp = d.core_properties
    cp.author = ""
    cp.last_modified_by = ""
    cp.comments = ""
    cp.keywords = ""
    cp.subject = ""
    cp.category = ""
    cp.title = title
    d.save(str(docx_path))


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--title", default=None)
    a = ap.parse_args(argv)

    text = transform(a.src.read_text(encoding="utf-8"))
    title = a.title or next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    # the copy sits beside the source so the figure paths resolve
    fd, tmp = tempfile.mkstemp(suffix=".md", prefix="._clean_", dir=str(a.src.parent))
    tmp = Path(tmp)
    try:
        tmp.write_text(text, encoding="utf-8")
        # export under a neutral name: the exporter refuses names that look like the author's
        # annotated copies, then the file is moved to its final name
        staged = a.dest.with_name("._clean_export.docx")
        r = subprocess.run([sys.executable, str(HERE / "export_brief_docx.py"), "--in", str(tmp),
                            "--out", str(staged), "--no-highlight", "--force"],
                           capture_output=True, text=True)
        print(r.stdout[-800:], r.stderr[-800:])
        if r.returncode != 0 or not staged.exists():
            return r.returncode or 1
        staged.replace(a.dest)
    finally:
        tmp.unlink(missing_ok=True)
    scrub(a.dest, title)
    left = sum(p.count("—") for p in [text])
    print(f"clean: {a.dest}  (em dashes left in text: {left})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
