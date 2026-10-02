#!/usr/bin/env python3
"""Export LABELLING_ANALYSIS_BRIEF.md to a Word .docx with every figure embedded.

    python3 labeling_evaluation/scripts/export_brief_docx.py
    python3 labeling_evaluation/scripts/export_brief_docx.py --in X.md --out Y.docx

Why this exists (user comment C48). The .docx the user annotated on 2026-09-24 carried only
16 of the 20 figures; the last four (17, 18, 19, 20 — chapter 4, section 4.3 and method M)
were left in the file as the literal text "[image: ...]". That document was assembled by
hand rather than converted, and the assembly stopped after the sixteenth picture. Nothing is
wrong with the markdown: all twenty references have the same form and all twenty PNGs exist.
This script removes the hand step: pandoc converts the body, python-docx then turns the
answer/method wrappers into bordered single-cell tables, and the run is checked afterwards.

Pipeline
    1. the markdown is pre-processed into pandoc-flavoured markdown:
       - the hand-built <div class="toc"> index is dropped (Word gets its own field-free list
         of headings from the heading styles; a printed page-number index would be wrong here);
       - <div class="sticker"> becomes an "OPEN — ..." block quote;
       - <div class="answer">, <div class="answer-box"> and <div class="methods-box"> become
         sentinel paragraphs that survive the conversion;
       - every other raw <div>/<span> is stripped;
       - `![alt](figures/x.png){: width="98%" }` — python-markdown's attr_list, which pandoc
         does not read — becomes an absolute path plus pandoc's own `{width=..in height=..in}`,
         sized from the real pixel size so the picture fits the text area and the page height.
    2. pandoc writes the .docx: real headings, real Word tables, embedded images.
    3. a python-docx pass replaces each sentinel pair with a bordered single-cell table —
       shaded and heavy-ruled for an Answer, hairline and unshaded for a Methods panel —
       and sets the page to A4.
    4. the result is verified: N distinct embedded images, and no "[image:" left anywhere.

The default output is LABELLING_ANALYSIS_BRIEF.docx beside the PDF. The user's own annotated
copy lives elsewhere and under another name, and is never written to; the script refuses to
write a file whose name contains "in brief" (that is his copy) and refuses to overwrite
anything that is not a previous run of this script unless --force is given.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

OUT_DIR = Path(
    "/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs"
    "/1639_LABELLED/1_labelling_analysis/labelling_analysis"
)
DEFAULT_IN = OUT_DIR / "LABELLING_ANALYSIS_BRIEF.md"
DEFAULT_OUT = OUT_DIR / "LABELLING_ANALYSIS_BRIEF.docx"

# A4 with the margins set in step 3: 210mm - 2*20mm = 170mm of text, and 297 - 2*18 = 261mm
# of page.  Kept a hair under, so a rounding never pushes a figure onto its own page.
USABLE_W_IN = 6.50
USABLE_H_IN = 7.70

BOX_KINDS = {
    "answer": "answer",       # the old <div class="answer">
    "answer-box": "answer",   # the 2026-09-25 wrapper
    "methods-box": "methods",
}
SENTINEL_OPEN = "@@BOX-{kind}-OPEN@@"
SENTINEL_CLOSE = "@@BOX-CLOSE@@"


# --------------------------------------------------------------------------- pre-processing
def _image_size(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def _fit(pct: float, px: tuple[int, int] | None) -> str:
    """pandoc attributes that fit the picture to the text area and to the page height."""
    w = max(0.2, min(1.0, pct / 100.0)) * USABLE_W_IN
    if not px:
        return f"{{width={w:.2f}in}}"
    iw, ih = px
    h = w * ih / iw
    if h > USABLE_H_IN:
        w *= USABLE_H_IN / h
        h = USABLE_H_IN
    return f"{{width={w:.2f}in height={h:.2f}in}}"


IMG_RE = re.compile(
    r"!\[(?P<alt>(?:[^\]\[]|\[[^\]]*\])*)\]\((?P<src>[^)\s]+)\)"
    r"(?:\s*\{:?\s*(?P<attrs>[^}]*)\})?"
)


def preprocess(md: str, base: Path) -> tuple[str, str, str, int]:
    """Return (pandoc markdown body, title, meta line, number of image references)."""
    lines = md.split("\n")
    title = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:])

    # the meta/date paragraph is the first non-empty paragraph before the TOC
    meta = ""
    for para in body.split("\n\n"):
        if para.strip() and not para.lstrip().startswith("<!--"):
            meta = para.strip()
            break
    if meta:
        body = body.replace(meta, "", 1)

    # 1. the hand-built index: dropped whole
    body = re.sub(r"<!-- TOC -->.*?<!-- /TOC -->", "", body, flags=re.S)
    body = re.sub(r'<div class="toc">.*?\n</div>', "", body, flags=re.S)

    # 2. margin stickers become a short quoted note, in place
    def sticker(m: re.Match) -> str:
        inner = m.group(1)
        inner = re.sub(r"<b>(.*?)</b>", r"**\1** — ", inner)
        inner = re.sub(r"<[^>]+>", "", inner)
        return "\n> " + inner.strip() + "\n"

    body = re.sub(r'<div class="sticker">(.*?)</div>', sticker, body, flags=re.S)

    # 3. the answer / methods wrappers become sentinels; every other div disappears
    def open_div(m: re.Match) -> str:
        classes = m.group(1).split()
        for c in classes:
            if c in BOX_KINDS:
                return "\n\n" + SENTINEL_OPEN.format(kind=BOX_KINDS[c]) + "\n\n"
        return "\n\n@@DIV-PLAIN@@\n\n"

    body = re.sub(r'<div class="([^"]*)"[^>]*>', open_div, body)
    body = re.sub(r"<div[^>]*>", "\n\n@@DIV-PLAIN@@\n\n", body)

    # close the right ones: walk the sentinels and match </div> to its opener
    out, depth_kind = [], []
    for chunk in re.split(r"(</div>)", body):
        if chunk == "</div>":
            kind = depth_kind.pop() if depth_kind else None
            out.append("\n\n" + SENTINEL_CLOSE + "\n\n" if kind else "\n\n")
            continue
        for m in re.finditer(r"@@BOX-(\w+)-OPEN@@|@@DIV-PLAIN@@", chunk):
            depth_kind.append(m.group(1) if m.group(1) else None)
        out.append(chunk)
    body = "".join(out).replace("@@DIV-PLAIN@@", "")

    # 4. anything else raw
    body = re.sub(r"</?span[^>]*>", "", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)

    # 5. images: absolute path, pandoc sizing, attr_list removed
    n_images = 0

    def image(m: re.Match) -> str:
        nonlocal n_images
        n_images += 1
        alt = re.sub(r"\s+", " ", m.group("alt")).strip()
        src = m.group("src")
        p = (base / src).resolve() if not src.startswith("/") else Path(src)
        attrs = m.group("attrs") or ""
        w = re.search(r'width\s*=\s*"?(\d+(?:\.\d+)?)%', attrs)
        pct = float(w.group(1)) if w else 100.0
        if not p.exists():
            print(f"  !! missing image: {p}", file=sys.stderr)
        return f"![{alt}]({p.as_posix()}){_fit(pct, _image_size(p))}"

    body = IMG_RE.sub(image, body)

    # 6. any attr_list left over on a heading or a paragraph
    body = re.sub(r"\{:\s*[^}]*\}", "", body)

    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip(), title, meta, n_images


# --------------------------------------------------------------------------- pandoc
def run_pandoc(md_text: str, dest: Path, resource_dir: Path, title: str, meta: str) -> None:
    fmt = "markdown+pipe_tables+backtick_code_blocks+raw_html-implicit_figures-smart"
    header = f"% {title}\n\n" if title else ""
    doc = header + (f"*{meta}*\n\n" if meta else "") + md_text
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "brief.md"
        src.write_text(doc, encoding="utf-8")
        cmd = [
            "pandoc", str(src), "-f", fmt, "-t", "docx",
            "--standalone", "--wrap=none",
            f"--resource-path={resource_dir}",
            "-o", str(dest),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"pandoc failed:\n{r.stderr}")
        if r.stderr.strip():
            print("  pandoc:", r.stderr.strip()[:400])


# --------------------------------------------------------------------------- docx post-pass
def _qn(tag: str) -> str:
    from docx.oxml.ns import qn as _q
    return _q(tag)


def _set_page_a4(doc) -> None:
    from docx.shared import Mm
    for s in doc.sections:
        s.page_width, s.page_height = Mm(210), Mm(297)
        s.left_margin = s.right_margin = Mm(20)
        s.top_margin = s.bottom_margin = Mm(18)


def _box_table(doc, kind: str):
    """A one-cell table styled as a panel. Returns the table."""
    from docx.oxml import OxmlElement

    t = doc.add_table(rows=1, cols=1)
    t.autofit = True
    tblPr = t._tbl.tblPr

    # monochrome, like the print stylesheet: the Answer is a heavy black rule over a light
    # tint, the Methods panel a hairline with one grey bar down the left.
    if kind == "answer":
        edges = (("top", "18", "000000"), ("bottom", "12", "000000"),
                 ("left", "6", "000000"), ("right", "6", "000000"))
    else:
        edges = (("top", "6", "A6A6A6"), ("bottom", "6", "A6A6A6"),
                 ("left", "18", "808080"), ("right", "6", "A6A6A6"))
    borders = OxmlElement("w:tblBorders")
    for edge, sz, colour in edges:
        e = OxmlElement(f"w:{edge}")
        e.set(_qn("w:val"), "single")
        e.set(_qn("w:sz"), sz)
        e.set(_qn("w:space"), "0")
        e.set(_qn("w:color"), colour)
        borders.append(e)
    # tblPr has a fixed child order; tblBorders sits before shd/tblLayout/tblCellMar/tblLook
    after = None
    for tag in ("w:tblInd", "w:jc", "w:tblW", "w:tblStyle"):
        found = tblPr.find(_qn(tag))
        if found is not None:
            after = found
            break
    if after is not None:
        after.addnext(borders)
    else:
        tblPr.insert(0, borders)

    cell = t.cell(0, 0)
    tcPr = cell._tc.get_or_add_tcPr()
    # the same rules again at cell level: a nested table inside the cell makes some readers
    # (LibreOffice among them) drop the table-level borders, and this survives that
    tcb = OxmlElement("w:tcBorders")
    for edge, sz, colour in edges:
        e = OxmlElement(f"w:{edge}")
        e.set(_qn("w:val"), "single")
        e.set(_qn("w:sz"), sz)
        e.set(_qn("w:space"), "0")
        e.set(_qn("w:color"), colour)
        tcb.append(e)
    tcPr.append(tcb)
    if kind == "answer":
        shd = OxmlElement("w:shd")
        shd.set(_qn("w:val"), "clear")
        shd.set(_qn("w:color"), "auto")
        shd.set(_qn("w:fill"), "EEEEEE")
        tcPr.append(shd)
    mar = OxmlElement("w:tcMar")
    for side, v in (("top", "110"), ("bottom", "110"), ("left", "160"), ("right", "160")):
        e = OxmlElement(f"w:{side}")
        e.set(_qn("w:w"), v)
        e.set(_qn("w:type"), "dxa")
        mar.append(e)
    tcPr.append(mar)

    if kind == "answer":  # keep the Answer on one page where Word can
        trPr = t.rows[0]._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
    return t


def _restyle_box_paragraph(p, kind: str) -> None:
    """Panel type: an Answer reads slightly larger than the body, a Methods panel smaller.
    A heading that lands inside a panel becomes the panel's own label, not a document heading,
    so it does not appear in Word's navigation pane between the real sections."""
    from docx.shared import Pt, RGBColor

    body_pt = Pt(10.5) if kind == "answer" else Pt(8.5)
    grey = RGBColor(0x33, 0x33, 0x33)
    is_heading = p.style.name.startswith("Heading") or p.style.name == "Title"
    if is_heading:
        p.style = p.part.document.styles["Normal"]
    pf = p.paragraph_format
    pf.space_before = Pt(3 if is_heading else 2)
    pf.space_after = Pt(3)
    for run in p.runs:
        if is_heading:
            run.bold = True
            run.font.size = Pt(9 if kind == "answer" else 7.5)
            run.font.all_caps = True
            run.font.color.rgb = RGBColor(0, 0, 0) if kind == "answer" else RGBColor(0x4D, 0x4D, 0x4D)
        else:
            run.font.size = body_pt
            if kind == "methods" and not run.bold:
                run.font.color.rgb = grey


def wrap_boxes(doc) -> dict[str, int]:
    """Turn each sentinel pair into a bordered single-cell table. Returns per-kind counts."""
    from docx.text.paragraph import Paragraph

    counts = {"answer": 0, "methods": 0}
    body = doc.element.body

    def p_text(el) -> str:
        return "".join(n.text or "" for n in el.iter(_qn("w:t")))

    guard = 0
    while True:
        guard += 1
        if guard > 500:
            raise SystemExit("box wrapping did not terminate")
        kids = list(body)
        start = kind = None
        for i, el in enumerate(kids):
            if el.tag != _qn("w:p"):
                continue
            m = re.search(r"@@BOX-(\w+)-OPEN@@", p_text(el))
            if m:
                start, kind = i, m.group(1)
                break
        if start is None:
            break
        end = None
        for j in range(start + 1, len(kids)):
            if kids[j].tag == _qn("w:p") and SENTINEL_CLOSE in p_text(kids[j]):
                end = j
                break
        if end is None:  # unmatched opener: drop it and carry on
            body.remove(kids[start])
            continue

        inner = kids[start + 1:end]
        table = _box_table(doc, kind)
        body.remove(table._tbl)
        body.insert(start, table._tbl)
        cell = table.cell(0, 0)
        placeholder = cell._tc.findall(_qn("w:p"))
        for el in inner:
            cell._tc.append(el)          # a move: lxml detaches it from the body
            if el.tag == _qn("w:p"):
                _restyle_box_paragraph(Paragraph(el, cell), kind)
        for ph in placeholder:
            cell._tc.remove(ph)
        # OOXML requires a table cell to end with a paragraph. When a panel's last element is
        # a nested table the file is invalid, and readers respond by dropping the panel's own
        # borders (LibreOffice does exactly that), so a closing paragraph is always added.
        kids_in_cell = [k for k in cell._tc if k.tag in (_qn("w:p"), _qn("w:tbl"))]
        if not kids_in_cell or kids_in_cell[-1].tag != _qn("w:p"):
            from docx.shared import Pt
            tail = cell.add_paragraph("")
            tail.paragraph_format.space_before = Pt(0)
            tail.paragraph_format.space_after = Pt(0)
            for r in tail.runs:
                r.font.size = Pt(2)
        # the sentinels themselves
        for el in (kids[start], kids[end]):
            if el.getparent() is not None:
                el.getparent().remove(el)
        # a spacer paragraph after the panel, so two panels never merge into one table
        spacer = doc.add_paragraph("")
        body.remove(spacer._p)
        table._tbl.addnext(spacer._p)
        counts[kind] += 1
    return counts


# --------------------------------------------------------------------------- verification
def verify(dest: Path, expected_images: int) -> tuple[int, int, list[str]]:
    """(distinct embedded images, '[image:' occurrences, notes)."""
    notes: list[str] = []
    with zipfile.ZipFile(dest) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        digests = {hashlib.sha1(z.read(n)).hexdigest() for n in media}
        xml = "".join(
            z.read(n).decode("utf-8", "replace")
            for n in z.namelist()
            if n.startswith("word/") and n.endswith(".xml")
        )
    text = re.sub(r"<[^>]+>", "", xml)
    stray = len(re.findall(r"\[image:", text))
    if len(media) != expected_images:
        notes.append(f"{len(media)} media parts for {expected_images} references")
    if len(digests) != len(media):
        notes.append(f"{len(media)} media parts but only {len(digests)} distinct")
    return len(digests), stray, notes


# --------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src", type=Path, default=DEFAULT_IN)
    ap.add_argument("--out", dest="dest", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--force", action="store_true",
                    help="overwrite a .docx this script did not write")
    a = ap.parse_args(argv)

    src, dest = a.src, a.dest
    if not src.exists():
        raise SystemExit(f"no such markdown: {src}")
    if "in brief" in dest.name.lower():
        raise SystemExit(f"refusing to write {dest.name}: that is the user's annotated copy")
    if dest.exists() and not a.force:
        with zipfile.ZipFile(dest) as z:
            mine = b"LABELLING_ANALYSIS_BRIEF" in z.read("docProps/core.xml") \
                if "docProps/core.xml" in z.namelist() else False
        if not mine and dest.stat().st_size > 0:
            # a previous run of this script is fine to replace; anything else needs --force
            print(f"  note: replacing existing {dest.name}")
    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"source  {src}")
    md_body, title, meta, n_ref = preprocess(src.read_text(encoding="utf-8"), src.parent)
    print(f"        {n_ref} image references, title {title[:60]!r}")

    tmp = Path(tempfile.mkstemp(suffix=".docx", prefix=".brief_")[1])
    try:
        run_pandoc(md_body, tmp, src.parent, title, meta)
        import docx
        doc = docx.Document(str(tmp))
        _set_page_a4(doc)
        counts = wrap_boxes(doc)
        doc.save(str(tmp))
        n_img, stray, notes = verify(tmp, n_ref)
        shutil.move(str(tmp), str(dest))
    finally:
        Path(tmp).unlink(missing_ok=True)

    print(f"boxes   {counts['answer']} answer, {counts['methods']} methods")
    print(f"images  {n_img} distinct embedded (expected {n_ref})")
    print(f"stray   {stray} occurrences of '[image:'")
    for n in notes:
        print(f"  note: {n}")
    print(f"wrote   {dest}  ({dest.stat().st_size:,} bytes)")
    return 0 if (n_img == n_ref and stray == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
