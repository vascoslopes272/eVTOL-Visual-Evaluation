#!/usr/bin/env python3
"""Render a docs/*.md report to PDF, matching the original supervisor-report layout.

    python3 scripts/build_report_pdf.py docs/Supervisor_Report_Taxonomy_Structure_Analysis_summary.md

Why this script exists rather than a plain markdown->pdf one-liner: the reports
carry raw HTML (<figure>, <div class="img-grid">, <span class="provenance">,
<div class="footnotes">) alongside their markdown, and the *layout* classes
`.img-grid`, `.img-grid3` and `.caption` are used in the markup but defined
nowhere in the .md files' own <style> blocks. Whatever produced the original
PDFs supplied them externally and that stylesheet was never committed. Without
the PRINT_CSS below, every figure panel stacks full-width and the document
balloons (36 pages instead of 14).

Pipeline: python-markdown (md_in_html passes the raw HTML through untouched)
-> standalone HTML -> headless Chrome --print-to-pdf. This is the same renderer
that produced the originals (their PDF metadata reads Skia/PDF, HeadlessChrome).

The HTML is written next to the source .md so relative `figs/...` paths resolve,
then removed. Requires: python-markdown, google-chrome.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

PRINT_CSS = """
@page { size: letter; margin: 14mm 12mm 14mm 12mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; max-width: none; margin: 0;
}
h1 { font-size: 19pt; margin: 0 0 0.25em 0; line-height: 1.25; }
h2 { font-size: 14pt; margin: 1.4em 0 0.5em 0; padding-bottom: 0.2em;
     border-bottom: 2px solid #d7dbe0; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 1.1em 0 0.4em 0; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 0.9em 0 0.35em 0; break-after: avoid; }
p { margin: 0.5em 0; }
hr { border: none; border-top: 1px solid #e3e6ea; margin: 1.5em 0; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.88em;
       background: #f2f4f6; padding: 0.1em 0.32em; border-radius: 3px; }

table { border-collapse: collapse; width: 100%; margin: 0.7em 0;
        font-size: 9pt; break-inside: avoid; }
th, td { border: 1px solid #d7dbe0; padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: #f0f2f5; font-weight: 700; }
tbody tr:nth-child(even) { background: #fafbfc; }

img { max-width: 100%; height: auto; }
figure { margin: 0.9em 0; text-align: center; break-inside: avoid; }
figure.single img { max-width: 72%; }
figcaption { font-size: 7.5pt; color: #5a6069; margin-top: 0.25em; line-height: 1.25; }

/* Side-by-side figure grids used throughout the report. These classes are in
   the markup but defined nowhere in the source .md's own <style> block, so
   without these rules every panel stacks full-width. */
.img-grid, .img-grid3 {
  display: grid; gap: 0.5em 0.8em; margin: 0.8em 0;
  align-items: end;
  /* deliberately breakable: a 2-row grid that cannot split leaves half-page
     gaps. Individual figures below stay atomic, so rows never tear. */
  break-inside: auto;
}
.img-grid  { grid-template-columns: repeat(2, 1fr); }
.img-grid3 { grid-template-columns: repeat(3, 1fr); }
.img-grid figure, .img-grid3 figure { margin: 0; }
.img-grid img, .img-grid3 img { width: 100%; }
.caption {
  display: block; text-align: center; font-size: 8pt;
  color: #5a6069; margin: 0.2em 0 0.9em 0;
}

/* keep a status badge with the text it closes */
.stage-status { break-before: avoid; }
.stage-purpose, div.footnotes, figure { break-inside: avoid; }
"""

CHROME_CANDIDATES = ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable")


def find_chrome() -> str:
    for name in CHROME_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    sys.exit(f"error: no Chrome/Chromium found (looked for: {', '.join(CHROME_CANDIDATES)})")


def build(src: Path, dest: Path | None = None) -> Path:
    if not src.is_file():
        sys.exit(f"error: no such file: {src}")
    dest = dest or src.with_suffix(".pdf")

    body = markdown.markdown(
        src.read_text(encoding="utf-8"),
        extensions=["tables", "md_in_html", "attr_list", "sane_lists", "footnotes"],
    )
    html = (
        "<!doctype html>\n<html><head><meta charset='utf-8'>\n"
        f"<style>{PRINT_CSS}</style>\n</head><body>\n{body}\n</body></html>"
    )

    # written beside the source so relative figs/ paths resolve for Chrome
    fd, tmp_name = tempfile.mkstemp(suffix=".html", prefix=".render_", dir=src.parent)
    tmp = Path(tmp_name)
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(html)
        subprocess.run(
            [
                find_chrome(), "--headless", "--disable-gpu", "--no-sandbox",
                "--no-pdf-header-footer", "--virtual-time-budget=20000",
                f"--print-to-pdf={dest}", tmp.resolve().as_uri(),
            ],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)

    if not dest.is_file():
        sys.exit("error: Chrome reported success but wrote no PDF")
    print(f"{dest}  ({dest.stat().st_size:,} bytes)")
    return dest


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__.strip().splitlines()[0] + "\n\nusage: build_report_pdf.py <report.md> [out.pdf]")
    build(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) == 3 else None)
