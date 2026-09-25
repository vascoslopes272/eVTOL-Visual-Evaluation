"""Render a methodology-style .md to a monochrome print PDF (python-markdown + headless Chrome).

    python3 scripts/build_styled_md_pdf.py <source.md> <dest.pdf>

Two document shapes are understood:

* the annotated framework (H1 "Title — Subtitle", then a date line, a reading
  guide with **Part A**..**Part H** cards and a corrections line, then ``---``);
* a plain report such as the generated Preliminary Analysis (H1, a few intro
  paragraphs, ``---``, numbered ``##`` / ``###`` headings, tables and images).

The first shape renders exactly as before; the second skips the guide cards and
the Part-name mapping. Images are resolved relative to the source file.
"""
import re, subprocess, sys, tempfile
from pathlib import Path
import markdown

SRC = Path(sys.argv[1]); DEST = Path(sys.argv[2])
# a compact document (file name carries "compact", or --compact on the command line) gets
# a tighter print style: same faces and rules, less air around headings, tables and figures
COMPACT = "--compact" in sys.argv[3:] or "compact" in SRC.stem.lower()

CSS_TEMPLATE = """
/* ---- monochrome print stylesheet (A4, black and white) ---- */
@page { size: A4; margin: 19mm 17mm 20mm 17mm;
  @bottom-left { content: "__FOOTER__"; font: 7.6pt Inter, sans-serif; color: #555; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.6pt Inter, sans-serif; color: #555; } }
/* a figure on its own A4-landscape page at full width (<div class="landscape">) */
@page landscape { size: A4 landscape; margin: 11mm 13mm 14mm 13mm; }
div.landscape { page: landscape; }
div.landscape img { width: 100% !important; max-height: 168mm; object-fit: contain; margin: 0 auto 0.3em auto; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Noto Serif", "Liberation Serif", Georgia, serif; font-size: 9.3pt; line-height: 1.52;
       color: #111111; margin: 0; orphans: 2; widows: 2; }
p { margin: 0.5em 0; text-align: justify; hyphens: auto; }
strong { font-weight: 700; color: #000; }
em { color: #111111; }
a { color: inherit; text-decoration: none; }
code { font-family: "DejaVu Sans Mono", "JetBrains Mono", Menlo, monospace; font-size: 0.82em;
       background: #f1f1f1; color: #111111; padding: 0.05em 0.32em; border-radius: 2px; }
hr { border: none; margin: 0; }
sup, sub { line-height: 0; }

/* ---- title block ---- */
.title { border-bottom: 2.4pt solid #000; padding: 0 0 8px 0; margin: 0 0 12px 0; }
.title h1 { font-family: "Inter Display", Inter, sans-serif; font-size: 21pt; font-weight: 700; margin: 0;
            line-height: 1.12; color: #000; letter-spacing: -0.01em; }
.title .sub { font-family: Inter, sans-serif; font-size: 10pt; color: #3f3f3f; font-weight: 500; margin-top: 4px;
              letter-spacing: 0.02em; }
.meta { font-family: Inter, sans-serif; font-size: 8.2pt; color: #3f3f3f; border-bottom: 0.5pt solid #c8c8c8;
        padding: 0 0 9px 0; margin: 0 0 11px 0; text-align: left; }
.meta p { margin: 0.25em 0; text-align: left; }

/* ---- margin stickers: open items flagged beside their heading (no-op elsewhere) ---- */
div.sticker { float: right; width: 26mm; margin: 2px 0 6px 9px; padding: 3px 5px 4px 5px; transform: rotate(1.5deg);
              box-shadow: 1px 1px 0 #9a8a3a;
              background: #fff1a8; border: 0.6pt solid #a88a00; border-left: 3pt solid #c9a400;
              font-family: Inter, sans-serif; font-size: 6.4pt; line-height: 1.25; font-weight: 500;
              color: #2e2500; text-align: left; hyphens: auto; break-inside: avoid; page-break-inside: avoid; }
div.sticker b { display: block; font-size: 7.6pt; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 2px; }

/* ---- front-page index (a no-op on any document that does not emit div.toc) ---- */
div.toc { margin: 2px 0 0 0; }
div.toc .toc-h { font-family: Inter, sans-serif; font-size: 11pt; font-weight: 700; color: #000;
                 border-bottom: 0.5pt solid #b8b8b8; padding-bottom: 5px; margin: 0 0 10px 0; }
div.toc-row { display: flex; align-items: baseline; margin: 4px 0; break-inside: avoid; page-break-inside: avoid; }
div.toc-row.toc-l0 { font-family: Inter, sans-serif; font-weight: 700; font-size: 8.8pt; color: #000; margin-top: 11px; }
div.toc-row.toc-l1 { font-family: "Noto Serif", serif; font-weight: 400; font-size: 8.2pt; color: #262626;
                      margin-left: 16px; }
div.toc-row .toc-t { flex: 0 1 auto; }
div.toc-row .toc-d { flex: 1 1 auto; border-bottom: 0.5pt dotted #a0a0a0; margin: 0 5px 2px 5px; }
div.toc-row .toc-p { flex: 0 0 auto; font-variant-numeric: tabular-nums; }

/* ---- reading guide ---- */
.guide { display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; margin: 10px 0 8px 0; }
.guide div { font-family: Inter, sans-serif; background: #fff; border: 0.5pt solid #b8b8b8; border-top: 2pt solid #000;
             padding: 6px 8px; font-size: 7.9pt; line-height: 1.35; color: #2b2b2b; text-align: left; }
.guide div b { display: block; color: #000; font-size: 8.6pt; font-weight: 700; margin-bottom: 3px;
               letter-spacing: 0.02em; }
.fixes { font-family: Inter, sans-serif; font-size: 8pt; color: #4d4d4d; margin: 8px 0 0 0; text-align: left; }

/* ---- section headings ---- */
h2 { font-family: "Inter Display", Inter, sans-serif; font-size: 14.5pt; font-weight: 700; color: #000;
     border-top: 2.4pt solid #000; margin: 1.7em 0 0.75em 0; padding: 9px 0 0 0; break-after: avoid; line-height: 1.2; }
h2 .part { display: block; font-family: Inter, sans-serif; font-size: 7.8pt; font-weight: 700; color: #4d4d4d;
     letter-spacing: 0.16em; margin-bottom: 4px; }
h3 { font-family: Inter, sans-serif; font-size: 11pt; font-weight: 600; color: #000; margin: 1.35em 0 0.45em 0;
     padding-bottom: 3px; border-bottom: 0.5pt solid #b8b8b8; break-after: avoid; }
h2 + h3 { margin-top: 0.75em; }
h4 { font-family: Inter, sans-serif; font-size: 9.8pt; font-weight: 700; color: #000; margin: 1.1em 0 0.3em 0;
     break-after: avoid; }
h3 + h4 { margin-top: 0.5em; }
h5 { font-family: Inter, sans-serif; font-size: 9pt; font-weight: 700; color: #262626; margin: 0.9em 0 0.25em 0;
     break-after: avoid; }
h4 + h5 { margin-top: 0.4em; }
h1, h2, h3, h4, h5 { break-inside: avoid; }
p.level { font-family: Inter, sans-serif; font-size: 8pt; color: #4d4d4d; margin: 0 0 0.45em 0; text-align: left; }
p.tcaption { font-family: Inter, sans-serif; font-size: 8pt; color: #000; margin: 0.7em 0 0 0; text-align: left;
             break-after: avoid; }
p.tcaption + table { margin-top: 0.25em; }

/* ---- tables: horizontal rules only (booktabs) ---- */
table { border-collapse: collapse; width: 100%; margin: 0.7em 0 1em 0; font-family: Inter, sans-serif;
        font-size: 8.2pt; line-height: 1.38; border-top: 1.2pt solid #000; border-bottom: 1.2pt solid #000; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border: none; border-bottom: 0.4pt solid #dcdcdc; padding: 5px 8px 5px 0; text-align: left; vertical-align: top; }
th:last-child, td:last-child { padding-right: 0; }
th { background: #fff; color: #000; font-weight: 700; border-bottom: 0.9pt solid #000; padding-bottom: 5px; }
tbody tr:last-child td { border-bottom: none; }
td:first-child { font-weight: 600; color: #000; }
table.plan { font-size: 7.9pt; }
table.narrow2 { width: 58%; }
table.narrow3 { width: 74%; }
table.plan td:first-child, table.state td:first-child { color: #000; }
td.v-ready, td.v-prio, td.v-park, td.v-warn { background: none; }
td.v-park { color: #4d4d4d; }

/* ---- figures ---- */
img { max-width: 100%; height: auto; display: block; margin: 0.8em auto 0.3em auto; }
/* 2026-09-22: a wide table or a long code span must wrap, never widen the page — Chrome otherwise
   shrinks the WHOLE document to fit, which made every letter and the landscape drawings small */
table { max-width: 100%; }
/* break-word, never anywhere: `anywhere` lets Chrome squeeze a narrow column to one letter
   per line ("l/e/v/e/l"), because it drops the min-content width to a single character. */
td, th { overflow-wrap: break-word; hyphens: none; }
code { overflow-wrap: anywhere; }
/* a heading never splits across pages, and never ends a page on its own */
h1, h2, h3, h4 { break-inside: avoid; page-break-inside: avoid; break-after: avoid; page-break-after: avoid; }
/* a heading and the first figure or table under it stay on one page; a chapter opens a new page */
div.keep { break-inside: avoid; page-break-inside: avoid; }
div.chapter-start { break-before: page; page-break-before: always; }
p > img + em, p.caption { font-family: Inter, sans-serif; font-size: 8pt; color: #4d4d4d; text-align: center; }
/* the provenance line under a figure or a table: unit of analysis, base, transform.
   Same grey and size as the Source line drawn inside a figure, so the two read as one note. */
p.prov { font-family: Inter, sans-serif; font-size: 7pt; line-height: 1.32; color: #5a5a5a;
         text-align: left; margin: 0.1em 0 0.7em 0; break-inside: avoid; page-break-inside: avoid; }
p.prov em { color: inherit; font-style: italic; }
p.caption + p.prov { margin-top: 0.05em; }
/* the takeaway sits directly under the provenance line: same grey, one hair of air between them */
p.prov + p.prov.take { margin-top: 0.22em; }
/* the question line sits last, under the takeaway: same grey again */
p.prov + p.prov.quest { margin-top: 0.22em; }
p.prov.quest em { font-style: italic; }
/* the four short lines (2026-09-23): Source · Unit · How to read · Why this way. They are one
   block under the caption — tight between themselves, with the air kept under the last of them. */
p.prov.src, p.prov.read, p.prov.why { margin-bottom: 0; }
p.prov.src + p.prov, p.prov + p.prov.read, p.prov + p.prov.why { margin-top: 0.12em; }
p.prov.why { margin-bottom: 0.75em; }
p.prov.src em { font-style: normal; letter-spacing: 0.01em; }
/* the Answer that closes a question: the one place in the document where a finding is stated */
div.answer { break-inside: avoid; page-break-inside: avoid; margin: 0.9em 0 0.4em 0;
             padding: 0.55em 0.75em; border-left: 2.5pt solid #2a2a2a; background: #f4f4f4; }
div.answer p { margin: 0; text-align: justify; font-size: 9.5pt; line-height: 1.45; }

/* ---- the chapter Answer panel (<div class="answer-box">) ----
   The most important thing on its page, and it has to survive a greyscale printer: the emphasis is
   carried by a heavy black rule top and bottom plus a light tint, never by a hue. It stays whole on
   one page. A no-op in any document that does not emit the wrapper. */
div.answer-box { break-inside: avoid; page-break-inside: avoid; margin: 1.15em 0 1.05em 0;
                 padding: 8px 12px 9px 12px; background: #eeeeee;
                 border: 0.6pt solid #000; border-top: 3pt solid #000; border-bottom: 1.6pt solid #000;
                 box-shadow: none; }
div.answer-box > *:first-child { margin-top: 0; }
div.answer-box > *:last-child { margin-bottom: 0; }
div.answer-box p { margin: 0.34em 0; text-align: justify; font-size: 9.6pt; line-height: 1.42; color: #000; }
div.answer-box strong { font-weight: 800; }
/* an "Answer" label, written as the box's first heading or a leading bold run on its own line */
div.answer-box > h3, div.answer-box > h4, div.answer-box > h5 {
    font-family: Inter, sans-serif; font-size: 8pt; font-weight: 800; letter-spacing: 0.16em;
    text-transform: uppercase; color: #000; border: none; padding: 0; margin: 0 0 5px 0; }
div.answer-box ul, div.answer-box ol { margin: 0.25em 0 0.25em 0; padding-left: 1.15em; }
div.answer-box li { margin: 0.12em 0; line-height: 1.36; font-size: 9.4pt; text-align: left; }
div.answer-box li > ul, div.answer-box li > ol { margin: 0.08em 0; }
div.answer-box ul > li::marker { color: #000; }
div.answer-box table { margin: 0.4em 0; background: #fff; }
div.answer-box p.prov, div.answer-box p.caption { color: #3a3a3a; }

/* ---- the quieter reference panel (<div class="methods-box">) ----
   Smaller type, a hairline rule, no fill; it may break across pages. */
div.methods-box { margin: 0.85em 0 0.95em 0; padding: 6px 10px 6px 10px; background: #fbfbfb;
                  border: 0.4pt solid #c0c0c0; border-left: 1.6pt solid #808080;
                  break-inside: auto; page-break-inside: auto; }
div.methods-box > *:first-child { margin-top: 0; }
div.methods-box > *:last-child { margin-bottom: 0; }
div.methods-box p { margin: 0.3em 0; font-size: 8.2pt; line-height: 1.4; color: #333333; text-align: justify; }
div.methods-box strong { color: #000; font-weight: 700; }
div.methods-box > h3, div.methods-box > h4, div.methods-box > h5 {
    font-family: Inter, sans-serif; font-size: 7.4pt; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #4d4d4d; border: none; padding: 0; margin: 0 0 4px 0; }
div.methods-box ul, div.methods-box ol { margin: 0.2em 0; padding-left: 1.1em; }
div.methods-box li { margin: 0.1em 0; font-size: 8.2pt; line-height: 1.38; color: #333333; text-align: left; }
div.methods-box table { font-size: 7.4pt; margin: 0.35em 0; }
div.methods-box code { font-size: 0.8em; }

/* ---- lists ---- */
ul, ol { margin: 0.35em 0 0.65em 0; padding-left: 1.35em; }
li { margin: 0.3em 0; text-align: justify; }
li > ul { margin-top: 0.18em; }
ol > li::marker { font-weight: 700; color: #000; }
ul > li::marker { color: #6e6e6e; }

/* ---- badges and callouts ---- */
.decide { display: inline-block; border: 0.8pt solid #000; background: #fff; color: #000; font-family: Inter, sans-serif;
          font-size: 7pt; font-weight: 700; padding: 0.5px 5px; letter-spacing: 0.08em; vertical-align: middle; }
.formula { background: #f4f4f4; border-left: 2.2pt solid #000; padding: 7px 11px; margin: 0.6em 0;
           font-size: 9pt; text-align: left; }
.hl { background: #f7f7f7; border: 0.5pt solid #c8c8c8; padding: 9px 12px; margin: 0.8em 0; }
pre { background: #f4f4f4; border-left: 2.2pt solid #000; padding: 6px 11px; margin: 0.5em 0 0.6em 0;
      font-size: 8.4pt; line-height: 1.4; white-space: pre-wrap; }
pre code { background: none; padding: 0; font-size: 1em; }
.hl p { margin: 0.32em 0; }
.pill { display: inline-block; font-size: 7.4pt; font-weight: 700; padding: 0 6px; border: 0.6pt solid #000;
        border-radius: 8px; margin-right: 3px; }
"""

md_text = SRC.read_text(encoding="utf-8")

# ---- title block: pull the H1 and the intro paragraphs out of the markdown
lines = md_text.split("\n")
h1 = lines[0].lstrip("# ").strip()
title_main, _, title_sub = h1.partition(" — ")
body_md = "\n".join(lines[1:])
intro, _, rest = body_md.partition("\n---\n")
paras = [p.strip() for p in intro.strip().split("\n\n") if p.strip()]

def inline(md): return markdown.markdown(md, extensions=["attr_list"]).replace("<p>", "").replace("</p>", "")

# the framework shape: date line, reading guide with Part cards, corrections line
NAMES = {"Part A": "The labelled dataset", "Part B": "Info-gathering plan", "Part C": "Phase 1 checklist", "Part D": "Methods", "Part E": "Additions", "Part F": "Order of work", "Part G": "Thesis outline", "Part H": "Glossary"}
framework_shape = len(paras) >= 3 and "**Part A**" in paras[1]
if framework_shape:
    date_p, guide_p, fix_p = paras[0], paras[1], paras[2]
    guide_cards = re.findall(r"\*\*(Part [A-H])\*\* (.*?)(?=\s\*\*Part|\sItems marked)", guide_p)
    guide_html = "".join(f"<div><b>{k} · {NAMES[k]}</b>{v.lstrip('is ').rstrip('.')}.</div>" for k, v in guide_cards)
    decide_note = "Items marked <span class='decide'>DECIDE</span> are open rulings for the author."
    head_html = (f"<div class='meta'>{inline(date_p)}</div>\n<div class='guide'>{guide_html}</div>\n"
                 f"<p class='fixes'>{decide_note} {inline(fix_p)}</p>")
else:
    head_html = "<div class='meta'>" + "".join(f"<p>{inline(p)}</p>" for p in paras) + "</div>"

# the running footer: title and subtitle without a trailing parenthesis
footer = title_main + (f" — {title_sub.split(' (')[0]}" if title_sub else "")
CSS = CSS_TEMPLATE.replace("__FOOTER__", footer.replace('"', "'"))

# a compact document (file name carries "compact") gets a tighter print style:
# same faces and rules, less air around headings, tables and figures
if COMPACT:
    CSS += """
@page { margin: 15mm 15mm 16mm 15mm; }
body { font-size: 8.8pt; line-height: 1.42; }
p { margin: 0.35em 0; }
h2 { font-size: 12.5pt; margin: 1.1em 0 0.45em 0; padding-top: 6px; }
h3 { font-size: 10pt; margin: 0.9em 0 0.3em 0; }
h4 { font-size: 9.2pt; margin: 0.8em 0 0.2em 0; }
h3 + h4 { margin-top: 0.35em; }
h5 { font-size: 8.6pt; margin: 0.65em 0 0.2em 0; }
h4 + h5 { margin-top: 0.3em; }
h2 + h3 { margin-top: 0.4em; }
ul, ol { margin: 0.2em 0 0.4em 0; }
li { margin: 0.15em 0; }
table { font-size: 7.5pt; line-height: 1.25; margin: 0.45em 0 0.7em 0; }
th, td { padding: 2.5px 6px 2.5px 0; }
img { margin: 0.4em auto 0.2em auto; }
.meta { font-size: 7.6pt; padding-bottom: 6px; margin-bottom: 8px; }
div.answer-box { margin: 0.85em 0 0.8em 0; padding: 6px 10px 7px 10px; }
div.answer-box p { font-size: 9pt; line-height: 1.36; margin: 0.25em 0; }
div.answer-box li { font-size: 8.9pt; line-height: 1.3; margin: 0.08em 0; }
div.methods-box { margin: 0.6em 0 0.7em 0; padding: 5px 9px; }
div.methods-box p, div.methods-box li { font-size: 7.8pt; line-height: 1.34; }
"""

def fix_lists(md):
    out=[]; prev=""
    for ln in md.split("\n"):
        import re as _re
        m=_re.match(r"^( {2,3})(- |\d+\. )", ln)
        if m: ln="    "+ln[len(m.group(1)):]
        if _re.match(r"^\s*(- |\d+\. )", ln) and prev.strip() and not _re.match(r"^\s*(- |\d+\. )", prev) and not prev.startswith("|"):
            out.append("")
        out.append(ln); prev=ln
    return "\n".join(out)
rest = fix_lists(rest)

# the two styled blocks of 2026-09-25 (<div class="answer-box"> / <div class="methods-box">): the
# generator writes the wrapper, this adds the markdown="1" that md_in_html needs to parse the
# contents. Harmless where the attribute is already there, a no-op where the wrapper is absent.
def arm_boxes(md):
    def add(m):
        tag = m.group(0)
        return tag if "markdown=" in tag else tag[:-1] + ' markdown="1">'
    return re.sub(r'<div class="(?:answer-box|methods-box)(?:[^"]*)"[^>]*>', add, md)
rest = arm_boxes(rest)

html_body = markdown.markdown(rest, extensions=["tables", "attr_list", "sane_lists", "md_in_html", "fenced_code"])

# ---- post-processing
def scripts(h):
    parts = re.split(r"(<code>.*?</code>)", h)
    for i in range(0, len(parts), 2):
        t = parts[i]
        t = re.sub(r"\^([0-2q])D", r"<sup>\1</sup>D", t)
        t = re.sub(r"(?<![\w/])([A-Za-zδΣ])_([A-Za-z0-9]{1,5})(?![A-Za-z0-9_])", r"\1<sub>\2</sub>", t)
        parts[i] = t
    return "".join(parts)
html_body = scripts(html_body)
html_body = html_body.replace("▶ DECIDE", "<span class='decide'>DECIDE</span>")
html_body = re.sub(r"<h2>Part ([A-H]) — (.*?)</h2>", r"<h2><span class='part'>PART \1</span>\2</h2>", html_body)
html_body = re.sub(r"<h2>Chapter (\d+) — (.*?)</h2>", r"<h2><span class='part'>CHAPTER \1</span>\2</h2>", html_body)
# an appendix carries the same eyebrow; no document that has none is changed by this line
html_body = re.sub(r"<h2>Appendix ([A-Z]) — (.*?)</h2>", r"<h2><span class='part'>APPENDIX \1</span>\2</h2>", html_body)
# the level-of-analysis line under a section heading, and the table captions above a table
html_body = re.sub(r"<p><em>(Level of analysis: .*?)</em></p>", r"<p class='level'><em>\1</em></p>", html_body)
html_body = re.sub(r"<p><strong>(Table [0-9][^<]*?)</strong></p>", r"<p class='tcaption'><strong>\1</strong></p>", html_body)
# verdict-cell colouring in the Part A table (4th cell of each row)
def colour_row(m):
    row = m.group(0)
    cells = re.findall(r"<td>(.*?)</td>", row, flags=re.S)
    if len(cells) != 4: return row
    v = cells[3]
    cls = ("v-ready" if v.startswith("<strong>Ready") or "Priority 1" in v else
           "v-prio" if "Cheap" in v else
           "v-warn" if v.startswith("<strong>Not a gold") else
           "v-park" if any(k in v for k in ("Park", "Out of scope", "Not needed", "Only matters")) else "")
    if cls:
        idx = [mm.start() for mm in re.finditer(r"<td>", row)][3]
        row = row[:idx] + f"<td class='{cls}'>" + row[idx+4:]
    return row
html_body = re.sub(r"<tr>.*?</tr>", colour_row, html_body, flags=re.S)
# column widths for the plan table (header starts with '#', 'Information')
html_body = html_body.replace("<table>\n<thead>\n<tr>\n<th>#</th>\n<th>Information",
    "<table class='plan'><colgroup><col style='width:4%'><col style='width:16%'><col style='width:33%'><col style='width:11%'><col style='width:17%'><col style='width:19%'></colgroup>\n<thead>\n<tr>\n<th>#</th>\n<th>Information")
html_body = html_body.replace("<table>\n<thead>\n<tr>\n<th>Source</th>\n<th>Exists?</th>",
    "<table class='state'><colgroup><col style='width:17%'><col style='width:9%'><col style='width:44%'><col style='width:30%'></colgroup>\n<thead>\n<tr>\n<th>Source</th>\n<th>Exists?</th>")
# formula lines (start with a variable and an "=" ) get a box
html_body = re.sub(r"<p>((?:d\(i,j\)|κ|Q|P_o|\^0D|V) = .*?)</p>", r"<p class='formula'>\1</p>", html_body)
# the worked example paragraph in 3.1
html_body = html_body.replace("<p>Worked example with two classes.", "<div class='hl'><p>Worked example with two classes.")
html_body = html_body.replace("because κ is dragged down by rare classes.</p>", "because κ is dragged down by rare classes.</p></div>")
# figure captions: the *Figure `name`.* line after an image
html_body = re.sub(r"<p><em>(Figure <code>.*?</code>\.)</em></p>", r"<p class='caption'><em>\1</em></p>", html_body)
html_body = re.sub(r"<p><em>(Figure [0-9][^<]*?)</em></p>", r"<p class='caption'><em>\1</em></p>", html_body)

# the provenance line the Labelling Analysis prints under every figure and every table
# (la_index.provenance): unit of analysis, base, transform. Absent from a document that
# does not emit it, and this rule is then a no-op.
html_body = re.sub(r"<p><em>(Unit: [^<]*)</em></p>", r"<p class='prov'><em>\1</em></p>", html_body)

# the takeaway line printed under the provenance line (la_index.takeaway): what the reader
# should conclude. Same grey, same size; a no-op in a document that does not emit it.
html_body = re.sub(r"<p><em>(Takeaway: [^<]*)</em></p>", r"<p class='prov take'><em>\1</em></p>", html_body)

# the question line printed last of the three grey lines (la_index.question): which of the
# eight sector questions the item answers, and in what way. Same grey; a no-op in a
# document that does not emit it.
html_body = re.sub(r"<p><em>(Question: [^<]*)</em></p>", r"<p class='prov quest'><em>\1</em></p>", html_body)

# the four short lines of the second reorganisation (2026-09-23): Source / Unit / How to read /
# Why this way, printed under every figure and table INSTEAD of the older trio. "Unit:" is already
# styled above. Each rule is a no-op in a document that does not emit its line.
for _label, _cls in (("Source", "prov src"), ("How to read", "prov read"), ("Why this way", "prov why")):
    html_body = re.sub(rf"<p><em>({_label}: [^<]*)</em></p>",
                       rf"<p class='{_cls}'><em>\1</em></p>", html_body)

# narrow tables (2-3 columns) do not need the full text width
def narrow(m):
    block = m.group(0)
    head = re.search(r"<thead>.*?</tr>", block, flags=re.S)
    if not head: return block
    ncol = len(re.findall(r"<th[ >]", head.group(0)))
    if ncol > 3 or "class=" in block[:20]: return block
    cls = "narrow2" if ncol == 2 else "narrow3"
    return block.replace("<table>", f"<table class='{cls}'>", 1)
html_body = re.sub(r"<table.*?</table>", narrow, html_body, flags=re.S)

html = f"""<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='title'><h1>{title_main}</h1><div class='sub'>{title_sub}</div></div>
{head_html}
{html_body}
</body></html>"""

# the temp HTML sits next to the source so relative image links resolve
tmp = Path(tempfile.mkstemp(suffix=".html", prefix=".render_", dir=SRC.parent)[1])
tmp.write_text(html, encoding="utf-8")
try:
    subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", f"--print-to-pdf={DEST}", tmp.resolve().as_uri()],
                   check=True, capture_output=True)
finally:
    tmp.unlink(missing_ok=True)
print(DEST, DEST.stat().st_size)
