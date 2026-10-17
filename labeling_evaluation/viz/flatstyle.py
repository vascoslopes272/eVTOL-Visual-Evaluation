"""Flat figure style — an experiment for the whole dissertation (author, 2026-10-17), first tried on q2_filer_types.

One place for the palette, the fonts, the in-segment label rule and the one-line legend of the horizontal 100 % stacked bars, so
that the other bar figures of Parts III to V can be moved to the same look in a later pass without inline styling.

    from viz import flatstyle as fs
    with fs.context():                              # fonts and sizes (Helvetica / Arial family, Liberation Sans fallback)
        fig, ax = fs.figure(11, 6)                  # printed size in cm
        fs.stacked_rows(ax, parts, colours, ...)    # one row per group, 100 % wide
        fs.legend_line(fig, ax, labels, colours)    # one line above the plot, left-aligned

Rules (author, 2026-10-17):
* three flat colours, no hatching, no gradients; thin white separators between segments;
* a percentage is printed inside a segment only when the segment is at least ``MIN_LABEL`` (10 %) wide, white on the dark
  colour and black on the light ones, 8 pt; a column named in ``side`` never prints inside: its value goes in a small grey
  7 pt column to the right of the bar ("univ. 7 %");
* the n of a row is part of the row label ("2016-19 (n 213)"); an incomplete row has its BAR drawn at 50 % opacity (its texts stay at
  full opacity, author 2026-10-17) and says so in its label;
* legend as one line above the plot, left-aligned, small squares and lower-case words; all text 7 to 9 pt at the printed width.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

CM = 2.54

# ----------------------------------------------------------------------------------------------- palette
DARK = "#3b4a5a"        # companies: dark blue-grey
LIGHT = "#9aa5b1"       # individual inventors: mid grey
ACCENT = "#c8792a"      # universities and institutes: the one warm accent
INK = "#1a1a1a"
MUTED = "#6b6b6b"       # the side column, the axis
AXIS = "#b0b0b0"        # the light x axis line
SEPARATOR = "white"     # between segments
SEP_LW = 0.8
FADE = 0.5              # opacity of an incomplete row

#: colour -> colour of the text printed on it
TEXT_ON = {DARK: "white", LIGHT: INK, ACCENT: "white"}

# ----------------------------------------------------------------------------------------------- text sizes (pt)
SIZE_LABEL = 8          # row labels, percentages inside segments, legend
SIZE_SMALL = 7          # the side column, the x tick labels
MIN_LABEL = 0.10        # a segment prints its share inside only from this width

#: the dissertation body is Helvetica; the first of these that is installed is used (Liberation Sans is metric-compatible with Arial)
FONT_PREFERENCE = ["Helvetica", "Arial", "Liberation Sans", "Nimbus Sans", "TeX Gyre Heros", "DejaVu Sans"]


def font_name() -> str:
    """The first installed font of FONT_PREFERENCE (DejaVu Sans at worst)."""
    from matplotlib import font_manager as fm
    installed = {f.name for f in fm.fontManager.ttflist}
    return next((f for f in FONT_PREFERENCE if f in installed), "DejaVu Sans")


FONT = font_name()

RC = {
    "font.family": FONT,                 # the concrete name: a generic 'sans-serif' would be resolved again at draw time, outside this context
    "font.sans-serif": [FONT] + [f for f in FONT_PREFERENCE if f != FONT],
    "font.size": SIZE_LABEL, "axes.labelsize": SIZE_LABEL, "xtick.labelsize": SIZE_SMALL, "ytick.labelsize": SIZE_LABEL,
    "legend.fontsize": SIZE_LABEL, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": True,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.grid": False,
    "xtick.color": AXIS, "xtick.labelcolor": MUTED, "xtick.major.width": 0.6, "xtick.major.size": 2.5,
    "ytick.color": INK, "ytick.major.size": 0, "text.color": INK, "axes.labelcolor": INK,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "ps.fonttype": 42,
}


@contextmanager
def context():
    """The flat style as an rc context (restores the previous settings on exit)."""
    with mpl.rc_context(RC):
        yield


def figure(width_cm: float, height_cm: float):
    """A figure at its printed size, in cm; the layout is finished by ``stacked_rows`` / ``legend_line``."""
    return plt.subplots(figsize=(width_cm / CM, height_cm / CM))


def text_on(colour: str) -> str:
    """White on the dark colours, ink on the light ones (the TEXT_ON table, luminance for colours not in it)."""
    if colour in TEXT_ON:
        return TEXT_ON[colour]
    r, g, b = mpl.colors.to_rgb(colour)
    return INK if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.55 else "white"


DECIMALS = 1            # shares print with one decimal (author, 2026-10-17), so a bar reads 63.6 / 6.9 / 29.5


def pct(v: float, decimals: int = DECIMALS) -> str:
    """A share as a percent: 0.069 -> '6.9 %'."""
    return f"{100 * v:.{decimals}f} %"


# ----------------------------------------------------------------------------------------------- the bars
def stacked_rows(ax, parts: pd.DataFrame, colours: Mapping[str, str], labels: Sequence[str], *, side: Sequence[str] = (),
                 side_prefix: Mapping[str, str] | None = None, gaps_before: Sequence[int] = (), faded: Sequence[int] = (),
                 height: float = 0.72, gap: float = 0.45, min_label: float = MIN_LABEL):
    """Horizontal 100 % stacked bars, one row per row of ``parts`` (first row on top), one segment per column in column order.

    ``labels`` are the row labels on the left (the n belongs in them). A column named in ``side`` prints its share in a small grey
    column right of the bar, prefixed by ``side_prefix[col]`` ("univ."); every other segment prints its share inside when at least
    ``min_label`` wide. ``gaps_before`` lists row positions preceded by a thin gap; ``faded`` the rows whose bar is drawn at FADE opacity (texts stay full).
    Returns the y positions of the rows."""
    shares = parts.div(parts.sum(axis=1), axis=0).fillna(0)
    n = len(shares)
    y = np.zeros(n)
    for i in range(1, n):
        y[i] = y[i - 1] - 1 - (gap if i in gaps_before else 0)
    side_prefix = side_prefix or {}
    left = np.zeros(n)
    for c in shares.columns:
        vals = shares[c].to_numpy()
        colour = colours[c]
        bars = ax.barh(y, vals, height, left=left, color=colour, edgecolor=SEPARATOR, linewidth=SEP_LW, zorder=3)
        for i, (b, v, l0) in enumerate(zip(bars, vals, left)):
            a = FADE if i in faded else 1.0
            b.set_alpha(a)
            if c in side or v < min_label or v <= 0:
                continue
            ax.text(l0 + v / 2, y[i], pct(v), ha="center", va="center", fontsize=SIZE_LABEL, color=text_on(colour), zorder=5)
        left = left + vals
    for c in side:
        for i, v in enumerate(shares[c].to_numpy()):
            ax.text(1.015, y[i], f"{side_prefix.get(c, c)} {pct(v)}", ha="left", va="center", fontsize=SIZE_SMALL, color=MUTED,
                    zorder=5, clip_on=False)
    ax.set_yticks(y, labels, fontsize=SIZE_LABEL)
    ax.set_xlim(0, 1)
    ax.set_ylim(y[-1] - height / 2 - 0.15, y[0] + height / 2 + 0.15)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "25", "50", "75", "100 %"])
    ax.tick_params(axis="y", length=0, pad=4)
    ax.spines["bottom"].set_bounds(0, 1)
    return y


def legend_line(fig, ax, labels: Sequence[str], colours: Sequence[str], *, pad: float = 0.03, left: float | None = None):
    """One legend line above the plot, left-aligned: small squares and the words. It starts at the left edge of the figure (where the
    row labels start) unless ``left`` gives another figure-x; it is then as wide as the whole figure, not only the bars."""
    handles = [Patch(facecolor=c, edgecolor="none", label=l) for l, c in zip(labels, colours)]
    x0 = 0.0 if left is None else left
    y0 = ax.get_position().y1 + pad
    return fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(x0, y0), bbox_transform=fig.transFigure, ncol=len(labels),
                      frameon=False, fontsize=SIZE_LABEL, handlelength=0.9, handleheight=0.9, handletextpad=0.5, columnspacing=1.4,
                      borderaxespad=0, borderpad=0)


def save(fig, pdf_path, png_dpi: int = 300):
    """Vector PDF at the figure's size, and a PNG preview beside it (same stem)."""
    from pathlib import Path
    from matplotlib.text import Text
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    for t in fig.findobj(Text):          # texts added outside context() (a relabel pass, a caller) take the same font
        t.set_fontfamily(FONT)
    fig.savefig(pdf_path)
    fig.savefig(pdf_path.with_suffix(".png"), dpi=png_dpi)
    return pdf_path, pdf_path.with_suffix(".png")
