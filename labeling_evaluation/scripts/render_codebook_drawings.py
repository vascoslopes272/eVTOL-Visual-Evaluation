#!/usr/bin/env python3
"""Render the two codebook drawings (Figure 3.3a/b) from their HTML at 2x.

    python3 scripts/render_codebook_drawings.py

The HTML in ``assets/codebook/src/`` is copied from the Design artifact
"eVTOL Patent-Image Taxonomy — Scheme" (boards Classes and Map). The design
tool's own PNG export wrapped headings and badges over the lines below them;
headless Chrome lays the same page out with the real fonts (Google Fonts, so
the machine needs network) and the PNGs replace the exports. Re-run after
editing the HTML, then ``scripts/render_drafts.py``.
"""
import subprocess
from pathlib import Path

CODEBOOK = Path(__file__).resolve().parent.parent / "assets" / "codebook"
#: html source -> (png the document uses, width, height in CSS px)
DRAWINGS = {
    "every_dimension.html": ("codebook_every_dimension.png", 1900, 1080),
    "architecture_classes.html": ("codebook_architecture_classes.png", 1760, 840),
}

for html, (png, w, h) in DRAWINGS.items():
    subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=2", f"--window-size={w},{h}",
                    "--virtual-time-budget=15000", f"--screenshot={CODEBOOK / png}",
                    (CODEBOOK / "src" / html).as_uri()], check=True, capture_output=True)
    print(CODEBOOK / png)
