"""Render the same Part I figures under each style of viz/style_options/*.mplstyle, for the author to choose a look.

    python3 notebooks/_build/style_options.py
Writes thesis_figures_v2/_style_options/<style>/<figure>.{png,pdf} and one comparison sheet per figure
(_style_options/COMPARE_<figure>.png). Nothing in Part_I_evidence_base is touched.
"""
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PILLAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PILLAR))
from viz import config, thesis
from viz import thesis_v2_part1 as v2

FIGS = ["q1_filings_per_year", "q1_growth_rates", "q4_class_mix"]
STYLES = sorted((PILLAR / "viz" / "style_options").glob("*.mplstyle"))

cfg = config.load()
ctx = thesis.context(cfg)
OUT = v2.out_root(cfg).parent / "_style_options"
items = {it["name"]: it for it in v2.ITEMS}
warnings.filterwarnings("ignore")
for st in STYLES:
    d = OUT / st.stem
    d.mkdir(parents=True, exist_ok=True)
    for name in FIGS:
        with plt.style.context(str(st)):
            fig, _ = items[name]["builder"](ctx)
            for a in fig.axes:
                if a.yaxis.get_label_position() == "right":
                    a.grid(False)
            fig.savefig(d / f"{name}.png", dpi=200)
            fig.savefig(d / f"{name}.pdf")
            plt.close(fig)
    print("written", d)

from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 46)
for name in FIGS:
    ims = [(st.stem, Image.open(OUT / st.stem / f"{name}.png").convert("RGB")) for st in STYLES]
    W = max(i.width for _, i in ims)
    H = sum(i.height + 90 for _, i in ims)
    sheet = Image.new("RGB", (W, H), "white")
    y = 0
    for label, im in ims:
        ImageDraw.Draw(sheet).text((12, y + 20), label.replace("_", " ", 1).replace("_", " "), fill="black", font=font)
        sheet.paste(im, (0, y + 90))
        y += im.height + 90
    sheet.save(OUT / f"COMPARE_{name}.png")
    print("written", OUT / f"COMPARE_{name}.png")
