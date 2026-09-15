#!/usr/bin/env python3
"""Regenerate PRELIMINARY_ANALYSIS.md and its PDF without the notebook.

    python3 scripts/render_drafts.py [--no-rules] [--pdf]

Loads the dataset as config.yaml says, builds every table and figure, writes
``PRELIMINARY_ANALYSIS.md`` under the output folder and, with ``--pdf``, renders
it with ``scripts/build_styled_md_pdf.py --compact`` at the repo root and prints
the page count (the document must stay at ten pages or fewer). ``--no-rules``
skips the one-minute codebook-rule run, whose tables go to ``tables/`` only.
"""
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

PILLAR = Path(__file__).resolve().parent.parent
REPO = PILLAR.parent
sys.path.insert(0, str(PILLAR))
from src.config_loader import load_config  # noqa: E402
from src.dataset_facts import export, figures, load_dataset, numbers, report  # noqa: E402


def main(argv):
    cfg = load_config()
    facts = dict(cfg["dataset_facts"])
    if "--no-rules" in argv:
        facts.pop("conformance_dir", None)
    ds = load_dataset(cfg)
    out = PILLAR / facts["output_dir"]
    partial = facts.get("partial_window_start", 2024)
    values = numbers.live(ds, partial)
    tables = export.build_all(ds, facts)
    figs = figures.render_all(ds, out, partial)
    export.write_all(tables, out)
    md = report.write_markdown(ds, tables, figs, out, values=values, partial_window_start=partial)
    print(f"source={ds.source}  tables={len(tables)}  figures={len(figs)}")
    print(f"document: {md}  ({md.stat().st_size / 1024:.0f} KB)")
    if "--pdf" in argv:
        pdf = md.with_suffix(".pdf")
        subprocess.run([sys.executable, str(REPO / "scripts" / "build_styled_md_pdf.py"),
                        str(md), str(pdf), "--compact"], check=True)
        pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        print(pdf.name, [l for l in pages.splitlines() if l.startswith("Pages")])


if __name__ == "__main__":
    main(sys.argv[1:])
