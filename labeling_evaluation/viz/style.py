"""The thesis figure style: one place for fonts, sizes and the look of every architecture class.

    from viz import config, style
    cfg = config.load()
    style.apply(cfg)                         # SciencePlots base + the thesis settings from the yaml
    fig, ax = style.figure("full", 0.45)     # drawn at the final printed width
    s = style.cls("SLC")                     # colour, marker, dash, hatch, name of a class

Rules (2026-10-01):
* figures are drawn at their FINAL width (text width or half of it), so a 9 pt font prints at 9 pt;
* each architecture class looks the same in every figure: one colour + one marker + one dash + one
  hatch. The colour order was checked with the palette validator (all checks pass; worst colour-blind
  separation ΔE 11). Three colours are light on white (orange, sky, pink), so a class is never told by
  colour alone: the marker / dash / hatch carry it in black-and-white print;
* the five small classes share greys and are told apart by marker and hatch.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt

try:                                    # registers the 'science' styles
    import scienceplots  # noqa: F401
except ImportError as e:                # pragma: no cover
    raise ImportError("pip install scienceplots") from e

INK = "#1a1a1a"          # text and axes
MUTED = "#6b6b6b"        # secondary text, reference lines
GRID = "#d9d9d9"
PARTIAL_HATCH = "////"   # a window or year that is not complete yet


@dataclass(frozen=True)
class ClassStyle:
    code: str
    name: str
    short: str
    color: str
    marker: str
    dash: object
    hatch: str


# order = the document's class order; colours validated in this order (adjacent pairs)
_CLASSES = [
    # code, printed name, printed code, colour, marker, dash, hatch
    ("SLC", "Lift + Cruise",               "L+C", "#0072B2", "o", "-",                 ""),
    ("TR",  "Tilt Propulsor",              "TP",  "#E69F00", "s", "--",                "////"),
    ("CVT", "Combined Vectored Thrust",    "CVT", "#009E73", "^", "-.",                "...."),
    ("TW",  "Tilt Wing",                   "TW",  "#D55E00", "D", ":",                 "\\\\\\\\"),
    ("MR",  "Multirotor",                  "MR",  "#56B4E9", "v", (0, (5, 1.5, 1, 1.5)), "xxxx"),
    ("TB",  "Tilt Body",                   "TB",  "#882255", "P", (0, (1, 1)),         "----"),
    ("PTC", "Pitch-to-Cruise",             "PTC", "#CC79A7", "X", (0, (8, 2)),         "++++"),
    # small classes: greys, told apart by marker and hatch
    ("RC",  "Rotorcraft",                  "RC",  "#4d4d4d", "h", "-",                 ""),
    ("SRW", "Stopped/Slowed Rotor Wing",   "SRW", "#7a7a7a", "<", "--",                "oo"),
    ("DS",  "Deflected Slipstream",        "DS",  "#a6a6a6", ">", ":",                 ".."),
    ("HB",  "Hoverbike",                   "HB",  "#262626", "*", "-.",                ""),
    ("PFV", "Personal Flying Vehicle",     "PFV", "#bfbfbf", "p", (0, (1, 1)),         "**"),
]
CLASSES: Dict[str, ClassStyle] = {c[0]: ClassStyle(*c) for c in _CLASSES}
CLASS_ORDER = [c[0] for c in _CLASSES]
OTHER = ClassStyle("Other", "Other", "Other", "#d0d0d0", ".", "-", "")

REGIONS: Dict[str, Tuple[str, str, object]] = {     # colour, marker, dash
    "North America": ("#0072B2", "o", "-"),
    "Europe":        ("#E69F00", "s", "--"),
    "Asia-Pacific":  ("#009E73", "^", ":"),
}


def cls(code: str) -> ClassStyle:
    """The style of one class (unknown codes get the neutral 'Other' style)."""
    return CLASSES.get(code, OTHER)


# ---------------------------------------------------------------------------------------------
def apply(cfg) -> None:
    """Set matplotlib for the thesis: SciencePlots base, then the yaml's fonts and sizes."""
    st = cfg.style
    plt.style.use(list(st.get("base", ["science", "no-latex"])))
    base, small = float(st["base_font_pt"]), float(st["small_font_pt"])
    mpl.rcParams.update({
        "font.family": st.get("font_family", "serif"),
        "font.serif": [st.get("font", "DejaVu Serif"), "DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "font.size": base,
        "axes.titlesize": base,
        "axes.labelsize": base,
        "xtick.labelsize": small,
        "ytick.labelsize": small,
        "legend.fontsize": small,
        "legend.frameon": False,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "xtick.top": False,
        "ytick.right": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "hatch.linewidth": 0.5,
        "hatch.color": INK,
        "savefig.dpi": int(st.get("dpi_png", 300)),
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,             # fonts embedded as text, editable and searchable
        "figure.dpi": 110,              # screen only; files use savefig.dpi
    })


def size(cfg, width: str = "full", aspect: float = 0.5) -> Tuple[float, float]:
    """(width, height) in inches. width: 'full' = text width, 'half' = half minus the gap."""
    st = cfg.style
    w = float(st["text_width_in"])
    if width == "half":
        w = (w - float(st.get("column_gap_in", 0.25))) / 2
    return w, w * aspect


def figure(cfg, width: str = "full", aspect: float = 0.5, **kw):
    """A figure drawn at its printed size. kw goes to plt.subplots (nrows, ncols, sharey, …)."""
    return plt.subplots(figsize=size(cfg, width, aspect), constrained_layout=True, **kw)


def mark(ax, label: str, lines_up: float = 0) -> None:
    """The panel mark (i), (ii)… above the top-left corner, so the caption can name the graph.
    ``lines_up`` lifts it by that many text lines (when the panel also has a title)."""
    from matplotlib.transforms import offset_copy
    tr = offset_copy(ax.transAxes, fig=ax.figure, y=lines_up * mpl.rcParams["font.size"] * 1.3, units="points")
    ax.text(0.0, 1.02, label, transform=tr, ha="left", va="bottom",
            fontsize=mpl.rcParams["font.size"], fontweight="bold")
