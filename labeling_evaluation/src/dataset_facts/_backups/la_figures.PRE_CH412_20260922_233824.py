"""The figures of the Labelling Analysis.

Colour figures in the atlas style (one fixed hue per architecture class, blue ramp
for magnitudes, a Source and How-to-read line under every figure). Figures the
Preliminary Analysis atlas already draws are reused from :mod:`atlas`; the new
ones read their frames from :mod:`la_tables`, so a figure and its table can never
disagree. :func:`render_all` draws everything into ``<out_dir>/figures``.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import a2, atlas, figures, la_tables, metrics, numbers
from .atlas import (ARCH_COLOR, ARCH_ORDER, BLUE, CAT, GRID, INK, INK2, MUTED, OTHER, REGION_COLOR,
                    REGIONS, STYLE, SURFACE, _arch_name, _color, _fold, _heat, _hgrid, _legend_arch,
                    _stack_h)
from .la_tables import FIRM_MIN, FOLD5_NAMES, WINDOW_NAMES
from .loaders import Dataset

DPI = 200
W = 7.6                      # portrait text width, inches
PAGE = atlas.PAGE            # landscape page
SRC = "master labels (notebook 04) through labeling_evaluation/src/dataset_facts; analysis set = representative primary unique aircraft"
ARI_SRC = "AAM Reality Index, SMG Consulting (aamrealityindex.com), May 2026 release and its history, fetched 2026-09-22"
EVN_SRC = "evtol.news directory pages (EVTOLNEWS_DS/0_source/aircraft.csv) joined through patent_links.csv (use = yes)"
FIVE_COLOR = {"VT": "#2a78d6", "LC": "#4a3aa7", "WM": "#008300", "ER": "#eda100", "HB": "#e87ba4"}
#: marker and dash per class so the line charts survive black-and-white printing
CLASS_STYLE = {"SLC": ("o", "-"), "TR": ("s", "--"), "CVT": ("^", "-."), "TW": ("D", ":"), "MR": ("v", "-"),
               "TB": ("P", "--"), "PTC": ("X", "-.")}
REGION_STYLE = {"North America": ("o", "-"), "Europe": ("s", "--"), "Asia-Pacific": ("^", ":")}


def _cs(code):
    return CLASS_STYLE.get(code, ("o", "-"))


WIN_SHORT = {"<= 2011": "≤2011", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23", "2024-26 (partial)": "24–26*"}


def _fig_bottom(fig) -> tuple:
    """(left, bottom) of everything drawn, in figure fractions."""
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    return bb.x0 / fig.get_figwidth(), bb.y0 / fig.get_figheight(), bb.width


def _stamp(fig, source: str, read: str = "") -> None:
    """Source / How-to-read lines hung under the lowest drawn element, so they never overlap it."""
    import textwrap
    x0, y0, width_in = _fig_bottom(fig)
    chars = max(int(min(width_in, TEXT_W) * 15.5), 60)
    lines = textwrap.wrap("Source: " + source, chars)
    if read:
        lines += textwrap.wrap("How to read: " + read, chars)
    fig.text(max(x0, 0.0), y0 - 0.012, "\n".join(lines), fontsize=7, color=INK2, ha="left", va="top")


def _legend_arch(fig, codes, loc="lower center", ncol=4, y=0.0):
    """Class legend, at most 4 columns (8 made figures wider than the page), hung under everything."""
    _, y0, _ = _fig_bottom(fig)
    handles = [matplotlib.patches.Patch(color=_color(c), label=_arch_name(c) if c != "Other" else "Other types")
               for c in codes]
    fig.legend(handles=handles, loc="upper center", ncol=min(ncol, 4), bbox_to_anchor=(0.5, y0 - 0.01),
               fontsize=7.5, handlelength=1.4, columnspacing=1.2)


def _repel(ax, xs, ys, labels, fs=7, avoid=None, marker_pt=5.0):
    """Label points without overlap. Candidates: right then left of the dot, starting just clear of it,
    at growing vertical offsets; a moved label gets a thin leader line. A spot is free when its text touches
    no other label and no dot, and stays inside the axes. ``avoid``: every dot on the axes."""
    from matplotlib.transforms import Bbox, offset_copy
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    k = fig.dpi / 72
    placed = []
    px = marker_pt * k
    for (ax_, ay_) in (avoid if avoid is not None else list(zip(xs, ys))):
        cx, cy = ax.transData.transform((ax_, ay_))
        placed.append(Bbox([[cx - px, cy - px], [cx + px, cy + px]]))
    axbb = ax.get_window_extent(r)
    dx0 = marker_pt + 2
    dys = [0] + [s_ * d for d in range(8, 88, 8) for s_ in (1, -1)]
    fails = []
    order = sorted(range(len(xs)), key=lambda q: -ax.transData.transform((xs[q], ys[q]))[1])
    for q in order:
        done = False
        for dy in dys:
            for side, dx in ((1, dx0), (-1, dx0), (1, dx0 + 12), (-1, dx0 + 12)):
                tr = offset_copy(ax.transData, fig=fig, x=dx * side, y=dy, units="points")
                t = ax.text(xs[q], ys[q], labels[q], transform=tr, fontsize=fs, color=INK, va="center",
                            ha="left" if side > 0 else "right", zorder=6,
                            bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))
                bb = t.get_window_extent(r).expanded(1.02, 1.12)
                inside = (axbb.x0 - 1 <= bb.x0 and bb.x1 <= axbb.x1 + 1 and axbb.y0 - 1 <= bb.y0 and bb.y1 <= axbb.y1 + 1)
                if inside and not any(bb.overlaps(b) for b in placed):
                    placed.append(bb)
                    if dy or dx > dx0:
                        ax.annotate("", xy=(xs[q], ys[q]), xytext=(dx * side, dy), textcoords="offset points",
                                    arrowprops=dict(arrowstyle="-", lw=0.4, color=MUTED, shrinkA=0, shrinkB=marker_pt * 0.8))
                    done = True
                    break
                t.remove()
            if done:
                break
        if not done:
            fails.append(labels[q])
            t = ax.text(xs[q], ys[q], labels[q], fontsize=fs, color=INK, va="center",
                        transform=offset_copy(ax.transData, fig=fig, x=dx0, y=0, units="points"))
            placed.append(t.get_window_extent(r))
    if fails:
        print(f"[repel] no free spot for: {fails}")


#: printed text width of the compact A4 page (210 mm − 2 × 15 mm margins), inches
TEXT_W = 7.0


def _wrap_to(t, width_in: float, r) -> None:
    """Re-wrap a Text so its drawn width is at most ``width_in`` inches."""
    import textwrap
    txt = t.get_text()
    if not txt:
        return
    w = t.get_window_extent(r).width / t.figure.dpi
    if w <= width_in:
        return
    flat = " ".join(txt.split())
    chars = max(int(len(flat) * width_in / w * 0.96), 12)
    t.set_text("\n".join(textwrap.wrap(flat, chars)))


def _wrap_texts(fig, target: float = TEXT_W) -> None:
    """Titles, axis labels and the suptitle wrap to the space they own instead of widening the figure."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    if fig._suptitle is not None:
        _wrap_to(fig._suptitle, min(target, fig.get_figwidth()) * 0.98, r)
    boxes = {ax: ax.get_window_extent(r) for ax in fig.axes}
    fig_w = fig.get_figwidth() * fig.dpi
    for ax, bb in boxes.items():
        # room to the right: up to the next panel on the same row (its y-labels included), else the canvas edge
        right = fig_w
        for o, ob in boxes.items():
            if o is not ax and ob.x0 > bb.x0 + 5 and ob.y1 > bb.y0 and ob.y0 < bb.y1:
                ylab = o.yaxis.get_tightbbox(r)
                right = min(right, (ylab.x0 if ylab is not None else ob.x0) - 6)
        room = max((right - bb.x0) / fig.dpi, 1.0)
        for t in (ax.title, ax._left_title):
            _wrap_to(t, room, r)
        _wrap_to(ax._right_title, max(bb.width / fig.dpi, 1.0), r)
        _wrap_to(ax.xaxis.label, max(bb.width / fig.dpi, 1.0), r)
    # the suptitle sits above every panel title
    if fig._suptitle is not None and fig._suptitle.get_text():
        fig.canvas.draw()
        tops = [t.get_window_extent(r).y1 for ax in fig.axes for t in (ax.title, ax._left_title, ax._right_title)
                if t.get_text()] + [bb.y1 for bb in boxes.values()]
        sb = fig._suptitle.get_window_extent(r)
        need = max(tops) + 4 - sb.y0
        if need > 0:
            x_, y_ = fig._suptitle.get_position()
            fig._suptitle.set_y(y_ + need / (fig.get_figheight() * fig.dpi))


def _declutter(fig) -> None:
    """Inside each axes: a percentage label that collides with another is hidden; any other colliding
    label is nudged up by its own height until it is free."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    pct = re.compile(r"^\s*\d{1,3}\s*%\s*$")
    for ax in fig.axes:
        placed = []
        for t in ax.texts:
            if not t.get_visible() or not t.get_text().strip():
                continue
            bb = t.get_window_extent(r)
            if any(bb.overlaps(b) for b in placed):
                if pct.match(t.get_text()):
                    t.set_visible(False)
                    continue
                for _ in range(6):
                    try:                       # positions in dates or categories are left alone
                        x_, y_ = (float(c) for c in t.get_position())
                    except (TypeError, ValueError):
                        break
                    tr = t.get_transform()
                    dx, dy = tr.transform((x_, y_))
                    nx, ny = tr.inverted().transform((dx, dy + bb.height * 1.05))
                    t.set_position((nx, ny))
                    bb = t.get_window_extent(r)
                    if not any(bb.overlaps(b) for b in placed):
                        break
            placed.append(bb)


def _clear_panels(fig) -> bool:
    """Widen the gap between side-by-side panels until the right panel's row labels clear the left panel's
    content (its dots and texts). Returns True when it changed anything."""
    changed = False
    for _ in range(12):
        fig.canvas.draw()
        r_ = fig.canvas.get_renderer()
        clash = None
        for a1 in fig.axes:
            for a2_ in fig.axes:
                if a2_ is a1 or not hasattr(a2_, "get_subplotspec") or a2_.get_subplotspec() is None:
                    continue
                b1, b2 = a1.get_window_extent(r_), a2_.get_window_extent(r_)
                if b2.x0 > b1.x1 - 2 and b2.y1 > b1.y0 and b2.y0 < b1.y1:
                    yl = a2_.yaxis.get_tightbbox(r_)
                    content = [t.get_window_extent(r_) for t in a1.texts if t.get_visible() and t.get_text()]
                    content += [c.get_window_extent(r_) for c in a1.collections]
                    content += [b1]
                    if yl is not None and any(yl.x0 < c.x1 + 3 and yl.y1 > c.y0 and yl.y0 < c.y1 for c in content):
                        clash = a2_
        if clash is None:
            return changed
        gs_ = clash.get_subplotspec().get_gridspec()
        gs_.update(wspace=(gs_.wspace or 0.2) + 0.12)
        changed = True
    return changed


def _fit_width(fig, target: float = TEXT_W) -> None:
    """Shrink the canvas until the drawn content (labels and legends hanging outside included) is
    ``target`` inches wide, so the page prints every letter at its set size instead of scaling it down."""
    for _ in range(6):
        _wrap_texts(fig, target)               # titles re-wrap to the current panel widths first
        fig.canvas.draw()
        bb = fig.get_tightbbox(fig.canvas.get_renderer())
        if bb.width <= target * 1.01:
            return
        over = bb.width - fig.get_figwidth()
        new_w = max(target - over, target * 0.55)
        fig.set_size_inches(new_w, fig.get_figheight(), forward=True)


#: black-and-white print: every categorical colour also carries a hatch (bars, bubbles, legend patches)
#: and a dash + marker (lines). Colours are matched by value, so the pass works on any figure.
_BW = {}


def _bw_table():
    if _BW:
        return _BW
    from matplotlib.colors import to_hex
    hatch = ["", "////", "....", "\\\\\\", "xxxx", "----", "++++", "oo"]
    dash = ["-", "--", "-.", ":", (0, (5, 1.5, 1, 1.5, 1, 1.5)), (0, (1, 1)), (0, (8, 2)), "--"]
    mark = ["o", "s", "^", "D", "v", "P", "X", "h"]
    for k, c in enumerate(CAT):
        _BW[to_hex(c)] = (hatch[k], dash[k], mark[k])
    _BW[to_hex(OTHER)] = ("||||", (0, (3, 1, 1, 1)), "h")
    return _BW


def _bw(fig) -> None:
    """Add hatches, dashes and markers keyed to the categorical colours, so no category depends on colour."""
    from matplotlib.colors import to_hex
    from matplotlib.collections import PathCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    tab = _bw_table()
    if getattr(fig, "_bw_off", False):
        return
    ink = (0, 0, 0, 0.55)
    axes_all = list(fig.axes) + [c for a_ in fig.axes for c in getattr(a_, "child_axes", [])]
    # fills outside the categorical palette (e.g. a blue ramp): patterns assigned from light to dark
    extra = ["", "....", "////", "xxxx", "\\\\\\", "----", "++++", "oo", "**"]
    unm = {}
    for ax in axes_all:
        for a in ax.patches:
            if isinstance(a, Rectangle) and not a.get_hatch():
                fc = a.get_facecolor()
                key = to_hex(fc[:3])
                if fc[3] > 0.5 and key not in tab and key not in ("#ffffff", to_hex(GRID)) and min(fc[:3]) < 0.97:
                    unm[key] = sum(fc[:3])
    ramp = {k: extra[i % len(extra)] for i, k in enumerate(sorted(unm, key=lambda k: -unm[k]))} if len(unm) > 1 else {}
    for ax in axes_all + [fig]:
        arts = ax.get_children() if ax is not fig else []
        for leg in ([ax.get_legend()] if ax is not fig else fig.legends):
            if leg is not None:
                arts += list(leg.get_patches()) + list(leg.get_lines())
        for a in arts:
            if isinstance(a, Rectangle) and a.get_width() and a.get_height():
                fc = a.get_facecolor()
                if fc[3] == 0:
                    continue
                key = to_hex(fc[:3])
                h = tab[key][0] if key in tab else ramp.get(key, "")
                if h and not a.get_hatch():
                    a.set_hatch(h)
                    a.set_edgecolor(ink)
                    a.set_linewidth(0.4)
            elif isinstance(a, PathCollection):
                fcs = a.get_facecolors()
                if len(fcs):
                    keys = {to_hex(c[:3]) for c in fcs}
                    if len(keys) == 1:
                        key = keys.pop()
                        if key in tab and tab[key][0]:
                            a.set_hatch(tab[key][0])
                            a.set_edgecolor(ink)
                            a.set_linewidth(0.4)
            elif isinstance(a, Line2D) and len(a.get_xdata()) >= 1:
                key = to_hex(a.get_color())
                if (key in tab and len(a.get_xdata()) >= 2 and a.get_linestyle() == "-"
                        and not getattr(fig, "_bw_keep_dash", False)):
                    a.set_linestyle(tab[key][1])
                if key in tab and a.get_marker() not in ("None", None, "", " ", "|") and not getattr(fig, "_bw_keep_marker", False):
                    a.set_marker(tab[key][2])
    import matplotlib as _m
    _m.rcParams["hatch.linewidth"] = 0.5


# --------------------------------------------------------------- panels ----
#: {figure name: [(mark, name), ...]} — filled while the figures are drawn, so the caption
#: in the document and the mark printed on the figure can never disagree.
PANELS: Dict[str, List] = {}


def _is_colorbar(ax) -> bool:
    return ax.get_label() == "<colorbar>" or hasattr(ax, "_colorbar")


def _drawn_axes(fig) -> List:
    """The axes that carry a graph, in drawing order; colorbars and empty axes left out."""
    out = []
    for ax in fig.axes:
        if _is_colorbar(ax):
            continue
        if ax.lines or ax.patches or ax.images or ax.collections or ax.texts or ax.tables:
            out.append(ax)
    return out


def _mark_panels(fig, path: Path) -> List:
    """Print (i), (ii), … on each graph of a figure that holds more than one, and record them.

    The names and the grouping come from :data:`la_index.FIGURE_PANELS`; a figure that is not
    listed there gets one panel per axes, named after its own title. The mark goes in front of
    the panel title, else in front of its y label, else on its own above the panel, so it
    survives wrapping, the black-and-white pass and the width fit.
    """
    from . import la_index
    name = Path(path).stem
    axes = _drawn_axes(fig)
    spec = la_index.FIGURE_PANELS.get(name)
    if spec is None:
        spec = [((ax.get_title(loc="left") or ax.get_title() or ax.get_ylabel() or "").replace("\n", " "), 1)
                for ax in axes]
    spread = sum(int(k) for _, k in spec)
    if spread != len(axes):
        print(f"  ! {name}: FIGURE_PANELS spans {spread} axes, {len(axes)} drawn — marks skipped")
        return []
    if len(spec) < 2:
        PANELS[name] = []
        return []
    marks, leaders, i = [], [], 0
    for k, (label, span) in enumerate(spec):
        mark = la_index.panel_mark(k)
        ax = axes[i]
        i += int(span)
        # a graph drawn as a row of small multiples is named by the row's y label — the title of
        # its first cell names the column (the region), not the graph
        if int(span) > 1 and ax.get_ylabel():
            ax.set_ylabel(f"{mark} {ax.get_ylabel()}")
        else:
            _mark_above(ax, mark)
        marks.append((mark, label))
        leaders.append((mark, ax))
    PANELS[name] = marks
    _lift_suptitle(fig)
    return leaders


def _mark_above(ax, mark: str) -> None:
    """The mark on its own line above the panel's title, flush with the panel's left edge, so it
    costs the figure a little height and no width at all (width is what the print size hangs on)."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    tops = [t.get_window_extent(r).y1 for t in (ax.title, ax._left_title, ax._right_title) if t.get_text()]
    box = ax.get_window_extent(r)
    y = (max(tops) if tops else box.y1) + 3
    fig.text(box.x0 / (fig.get_figwidth() * fig.dpi), y / (fig.get_figheight() * fig.dpi), mark,
             ha="left", va="bottom", fontsize=9.5, fontweight="bold", color=INK)


def _lift_suptitle(fig) -> None:
    """Keep the suptitle above the marks that were just added."""
    if fig._suptitle is None or not fig._suptitle.get_text():
        return
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    tops = [t.get_window_extent(r).y1 for ax in fig.axes
            for t in (ax.title, ax._left_title, ax._right_title) if t.get_text()]
    tops += [t.get_window_extent(r).y1 for t in fig.texts if t is not fig._suptitle]
    need = max(tops) + 4 - fig._suptitle.get_window_extent(r).y0
    if need > 0:
        x_, y_ = fig._suptitle.get_position()
        fig._suptitle.set_y(y_ + need / (fig.get_figheight() * fig.dpi))


_POS_RE = re.compile(r"(?:(?<=^)|(?<=\. ))(Left|Right|Top|Bottom)(?=[,:])")


def _read_with_marks(read: str, leaders: List) -> str:
    """"Left: … Right: …" in a How-to-read line becomes "(i) left: … (ii) right: …".

    Only where the geometry is unambiguous: exactly one panel at that edge. A figure whose
    panels sit side by side keeps any Top/Bottom wording untouched, and the other way round.
    """
    if not read or len(leaders) < 2:
        return read
    box = [(m, ax.get_position()) for m, ax in leaders]
    edges = {"Left": min(b.x0 for _, b in box), "Right": max(b.x0 for _, b in box),
             "Bottom": min(b.y1 for _, b in box), "Top": max(b.y1 for _, b in box)}
    val = {"Left": lambda b: b.x0, "Right": lambda b: b.x0, "Bottom": lambda b: b.y1, "Top": lambda b: b.y1}
    pos = {}
    for word, edge in edges.items():
        at = [m for m, b in box if abs(val[word](b) - edge) < 1e-6]
        if len(at) == 1 and len({round(val[word](b), 6) for _, b in box}) > 1:
            pos[word] = at[0]
    return _POS_RE.sub(lambda m: f"{pos[m.group(1)]} {m.group(1).lower()}" if m.group(1) in pos else m.group(0), read)


def _mark_keeping_width(fig, path: Path, read: str = "") -> str:
    """Put the panel marks on, without letting the longer titles change the figure's width.

    The marks go on after :func:`_fit_width` has settled the canvas, then the titles re-wrap
    inside the width the figure already had: a mark can add a line, never a millimetre of
    width, so a figure still prints at the size it was drawn for."""
    fig.canvas.draw()
    before = fig.get_tightbbox(fig.canvas.get_renderer()).width
    read = _read_with_marks(read, _mark_panels(fig, path))
    _wrap_texts(fig, before)
    fig.canvas.draw()
    if fig.get_tightbbox(fig.canvas.get_renderer()).width > before * 1.005:
        _fit_width(fig, before)
    return read


def _save(fig, path: Path, source: str, read: str = "") -> Path:
    with plt.rc_context(STYLE):
        _bw(fig)
        _wrap_texts(fig)
        _fit_width(fig)
        read = _mark_keeping_width(fig, path, read)
        _declutter(fig)
        _stamp(fig, source, read)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def _win_labels(names: List[str], n: Optional[pd.Series] = None) -> List[str]:
    if n is None:
        return [WIN_SHORT.get(w, w) for w in names]
    return [f"{WIN_SHORT.get(w, w)}\nn {int(n.get(w, 0))}" for w in names]


# ------------------------------------------------------- 2 taxonomy --------
def design_space_cards_svg(n: Dict, path: Path) -> Path:
    """Figure 3.3c without its bottom row: the four label cards of one unique aircraft."""
    s = figures._Svg(760, 130)
    s.text(12, 17, f"One unique aircraft: {n['questions']} slots on four label cards "
           f"({n['q_dim']} dimensions, {n['q_tick']} ticks, {n['q_num']} numbers), "
           f"filling {n['cols']} export columns", size=10.5, weight="bold")

    def kinds(card):
        parts = [(n[f"qd_{card}"], "dimension"), (n[f"qt_{card}"], "tick"), (n[f"qn_{card}"], "number")]
        return " · ".join(f"{k} {w}{'s' if k != 1 else ''}" for k, w in parts if k)

    cards = [
        ("G1 · Architecture", "G1", ["class, notPureArch"]),
        ("M1 · Structure", "M1", ["fuselage, boom group ×0..n"]),
        ("M2 · Aero", "M2", ["wing, wing panel ×1..4,", "integrated surface, empennage"]),
        ("M3 · Propulsion", "M3", ["propulsor card per host,", "propulsor type ×1..n"]),
    ]
    cards = [(title, f"{n[f'q_{c}']} slots", [kinds(c)] + body + [f"{n[f'cols_{c}']} export columns"])
             for title, c, body in cards]
    x0, w, h, y0, gap = 12, 172, 84, 30, 16
    for i, (title, slots, body) in enumerate(cards):
        x = x0 + i * (w + gap)
        s.rect(x, y0, w, h, fill="#ffffff", sw=1.1)
        s.text(x + 9, y0 + 18, title, size=10, weight="bold")
        s.text(x + w - 8, y0 + 18, slots, size=8.2, anchor="end", fill="#4d4d4d")
        s.lines(x + 9, y0 + 36, body, size=8.4, dy=12)
        if i < 3:
            s.arrow(x + w + 2, y0 + h / 2, x + w + gap - 2, y0 + h / 2, sw=1.1)
    return s.write(path)


# ------------------------------------------------------- 4.1 convergence ---
def fig_firm_weighted(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.firm_weighted_shares(v)
    fig, ax = plt.subplots(figsize=(W, 3.6))
    x = np.arange(len(WINDOW_NAMES))
    for cls, sub in t.groupby("class", sort=False):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        sub = sub.set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, sub["share by aircraft"], marker="o", lw=2, ms=5, color=_color(code), label=f"{cls} — by aircraft")
        ax.plot(x, sub["share by filer"], marker="s", lw=1.4, ms=4, ls="--", color=_color(code), label=f"{cls} — one vote per filer")
    ns = t.drop_duplicates("window").set_index("window")
    ax.set_xticks(x, [f"{WIN_SHORT[w]}\n{int(ns.loc[w, 'aircraft'])} / {int(ns.loc[w, 'filers'])}" for w in WINDOW_NAMES], fontsize=7)
    ax.set_xlabel("window, and its aircraft / filers", fontsize=7.5)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("share of the window")
    fig._bw_keep_dash = True
    for cls, sub_ in t.groupby("class", sort=False):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        last = sub_.set_index("window").reindex(WINDOW_NAMES).iloc[-2]
        ax.annotate(code, (x[-2], last["share by aircraft"]), xytext=(4, 0), textcoords="offset points", fontsize=7,
                    va="center", color=INK, bbox=dict(fc="white", ec="none", pad=0.2))
    ax.set_title("Class share per window: every aircraft (solid) against one vote per filer (dashed)", fontsize=9)
    ax.legend(ncol=1, fontsize=7.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    _hgrid(ax, "y")
    return _save(fig, path, SRC + "; Table 4.1.1b.",
                 "Solid: each unique aircraft counts once. Dashed: a named firm votes once per window for the class it filed "
                 "most; an individual or unattributed patent is its own filer. Where the two lines part, a few large filers "
                 "carry the class. * partial window.")


def fig_spans_by_firm(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    sp = a2.d9_aircraft_spans(ds)
    sp = sp.merge(v[["aircraft_id", "company_canonical", "named"]], on="aircraft_id", how="left")
    sizes = la_tables.firm_sizes(v)
    firms = list(sizes[sizes >= FIRM_MIN].index)
    group = lambda d: np.where(d["company_canonical"].isin(firms), d["company_canonical"],
                               np.where(d["named"], "other named firms", "individuals / unattributed"))
    sp["firm"] = group(sp)
    order = firms + ["other named firms", "individuals / unattributed"]
    rep = sp[sp["span_years"] > 0].copy()
    order_rep = [f for f in order if f in rep["firm"].values]
    fig = plt.figure(figsize=(W, 6.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.5, 1], hspace=1.45)
    ax = fig.add_subplot(gs[0])
    x = 0.0
    ticks, labels = [], []
    for f in order_rep:
        sub = rep[rep["firm"].eq(f)].sort_values("first")
        slot = max(len(sub), 2.6)
        start = x
        xs = start + (slot - len(sub)) / 2 + np.arange(len(sub))
        for xi, (_, r) in zip(xs, sub.iterrows()):
            ax.plot([xi, xi], [r["first"], r["last"]], color=_color(r["topType"]), lw=2.2, solid_capstyle="butt")
            ax.plot(xi, r["primary_year"], marker="o", ms=3.4, color=_color(r["topType"]))
        ticks.append(start + (slot - 1) / 2)
        labels.append(f"{f} ({len(sub)})")
        x = start + slot + 0.6
        ax.axvline(x - 0.8, color=GRID, lw=0.6)
    ax.set_xticks(ticks, labels, rotation=90, fontsize=7)
    ax.set_xlim(-1, x - 0.5)
    ax.set_ylabel("priority year")
    ax.set_title("Aircraft filed again over several years: one line per aircraft, first to last filing (dot = primary record)",
                 fontsize=9)
    _hgrid(ax, "y")
    # share of each firm's aircraft filed more than once, same order along x
    ax2 = fig.add_subplot(gs[1])
    g = sp.groupby("firm").agg(aircraft=("aircraft_id", "size"), refiled=("repeats", lambda s_: (s_ > 0).sum()))
    g = g.reindex([f for f in order if f in g.index])
    g["share"] = g["refiled"] / g["aircraft"]
    xx = np.arange(len(g))
    ax2.bar(xx, g["share"], color=BLUE(0.7), width=0.62)
    for xi, (_, r) in zip(xx, g.iterrows()):
        ax2.text(xi, r["share"] + 0.03, f"{int(r['refiled'])}/{int(r['aircraft'])}", ha="center", va="bottom", fontsize=7,
                 rotation=90)
    ax2.set_xticks(xx, list(g.index), rotation=90, fontsize=7)
    ax2.set_ylim(0, 1.35)
    ax2.set_yticks([0, 0.5, 1.0])
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("Share of each firm's aircraft filed more than once (any O1 / O2)", fontsize=9)
    _hgrid(ax2, "y")
    _legend_arch(fig, ARCH_ORDER + ["Other"])
    return _save(fig, path, SRC + "; aircraft observations O1/O2 (Table 1.2a); firms with 5 or more unique aircraft.",
                 "Top: each vertical line is one aircraft filed in more than one year. Bottom: of all the firm's aircraft, "
                 "how many were filed again, whatever the span. Re-filing the same aircraft for years is the only "
                 "commitment signal the patents themselves carry.")
def fig_two_counts(ds: Dataset, path: Path) -> Path:
    t = a2.d9_architecture_by_window_active(ds)
    classes = [c for c in t.columns if c not in ("window", "count", "unique aircraft")]
    fig, axes = plt.subplots(1, len(classes), figsize=(W, 3.0), sharey=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, cls in zip(axes, classes):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        for mode, ls, mk in (("once, at the primary record", "-", "o"), ("while filed, first to last", "--", "s")):
            sub = t[t["count"].eq(mode)].set_index("window").reindex(WINDOW_NAMES)
            ax.plot(x, sub[cls], ls=ls, marker=mk, ms=4, lw=1.8, color=_color(code), label=mode)
        ax.set_title(f"{code}", fontsize=9.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
    fig.subplots_adjust(bottom=0.34, top=0.8)
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    fig.suptitle("Class share per window, aircraft counted once (solid) or in every window it was filed in (dashed)",
                 x=0.01, y=0.98, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; aircraft spans (O1/O2 re-filings).",
                 "Solid: the aircraft sits in the window of its primary record. Dashed: it counts in every window from its "
                 "first to its last filing. The gap between the lines is what the dating rule can move.")


def fig_lead_lag(v: pd.DataFrame, path: Path) -> Path:
    cr, qr = la_tables.lead_lag(v, "region3")
    cc, qc = la_tables.lead_lag(v, "topType", top=7)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.6), gridspec_kw={"wspace": 0.25})
    for g in cr.columns:
        ax.plot(cr.index, cr[g], lw=2.2, ls=REGION_STYLE.get(g, ("o", "-"))[1], color=REGION_COLOR.get(g, OTHER), label=f"{g} ({int(qr.set_index('region3').loc[g, 'aircraft'])})")
    for p in (0.25, 0.5, 0.75):
        ax.axhline(p, color=GRID, lw=0.8)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("By applicant region", fontsize=9.5)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlabel("priority year (complete years, to 2023)")
    for g in cc.columns:
        ax2.plot(cc.index, cc[g], lw=1.8, ls=_cs(g)[1], color=_color(g), label=g, marker=_cs(g)[0], markevery=3, ms=4)
    for p in (0.25, 0.5, 0.75):
        ax2.axhline(p, color=GRID, lw=0.8)
    ax2.set_ylim(0, 1)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("By class, seven largest", fontsize=9.5)
    ax2.legend(loc="upper left", fontsize=7)
    ax2.set_xlabel("priority year (complete years, to 2023)")
    fig.suptitle("Cumulative share of each group's own aircraft by priority year (lead and lag)",
                 x=0.01, y=1.0, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; complete priority years only (≤ 2023); Tables 4.1.3a/b.",
                 "Each curve is one group divided by its own total, so the axis is not volume but timing: the year a curve "
                 "crosses 50 % is the group's median year. A curve to the left leads, to the right lags.")


def fig_class_cycles(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.class_cycles(v).set_index("class")
    classes = t.index.tolist()
    ncol = 3
    nrow = int(np.ceil(len(classes) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(W, 2.25 * nrow), sharey=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, cls in zip(axes.flat, classes):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        vals = t.loc[cls, WINDOW_NAMES].astype(float).to_numpy()
        ax.bar(x, vals, color=_color(code) if code in ARCH_COLOR else OTHER, width=0.72)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        med = WINDOW_NAMES.index(t.loc[cls, "median window"])
        ax.plot(med, vals[med] + 0.05, marker="v", color=INK, ms=5)
        ax.set_title(f"{code} ({int(t.loc[cls, 'aircraft'])})", fontsize=8.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7)
        ax.set_ylim(0, 1.0)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        _hgrid(ax, "y")
    for ax in list(axes.flat)[len(classes):]:
        ax.axis("off")
    fig.suptitle("Where in time each class lives: its aircraft per window as a share of its own total (▼ median window; codes as Figure 2.1a)",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.subplots_adjust(hspace=0.85, wspace=0.12)
    return _save(fig, path, SRC + "; Table 4.1.4.",
                 "Bars sum to 100 % across each class's own panel. A class whose bars peak early and empty later has faded; one "
                 "whose bars rise to the right is still growing. Classes ordered by size; * partial window.")


def fig_hill(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.hill_by_window(v)
    levels = t["level"].unique()
    fig, axes = plt.subplots(1, len(levels), figsize=(W, 3.0), sharex=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, lvl in zip(np.atleast_1d(axes), levels):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        for q, col, lab, ls_, mk_ in ((0, CAT[0], "⁰D richness", "-", "o"), (1, CAT[1], "¹D exp Shannon", "--", "s"),
                                      (2, CAT[2], "²D inverse Simpson", ":", "^")):
            ax.errorbar(x, sub[f"D{q}"], yerr=[sub[f"D{q}"] - sub[f"D{q} low"], sub[f"D{q} high"] - sub[f"D{q}"]],
                        marker=mk_, ls=ls_, ms=4, lw=1.8, capsize=2, color=col, label=lab)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES, sub["aircraft"]), fontsize=7.5)
        ax.set_title(lvl, fontsize=9.5)
        ax.set_ylim(0)
        _hgrid(ax, "y")
    h, l = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3)
    fig.subplots_adjust(bottom=0.28)
    np.atleast_1d(axes)[0].set_ylabel("effective number of archetypes")
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    fig.suptitle("Diversity per window, rarefied to 40 aircraft (1 000 draws, 95 % band)", x=0.01, y=1.04, ha="left",
                 fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.5; A0 = class, A0c = class × propulsor-unit bin.",
                 "Hill numbers at equal sample size: ⁰D counts archetypes, ¹D and ²D weigh them by share, so a fall in ¹D or "
                 "²D with a flat ⁰D means the same archetypes but a more uneven mix (convergence); rising means spreading out.")


def fig_zones(v: pd.DataFrame, path: Path) -> Path:
    z = la_tables.zones(v)
    fig = plt.figure(figsize=(W, 6.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1], hspace=0.62)
    ax2 = fig.add_subplot(gs[0])
    zz = z[z["filers 2016-23"] > 0]
    for _, r in zz.iterrows():
        ax2.scatter(r["share 2016-23"], r["filers per aircraft"], s=18 + 3.2 * r["aircraft"], color=_color(r["code"]),
                    alpha=0.85, edgecolor=SURFACE, lw=0.8, marker={"new": "^", "fading": "v"}.get(r["zone"], "o"), zorder=3)
    ax2.set_xlim(-0.002, zz["share 2016-23"].max() * 1.16)
    ax2.axvline(zz["share 2016-23"].median(), color=GRID, lw=1)
    ax2.axhline(zz["filers per aircraft"].median(), color=GRID, lw=1)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_xlabel("share of the 2016–23 aircraft")
    ax2.set_ylabel("distinct filers per aircraft")
    ax2.set_title("Crowded (right, low) against open (left, high); ▲ new since 2016, ▼ absent after 2019, ● persistent",
                  fontsize=9)
    _hgrid(ax2, "both")
    lab = zz[(zz["aircraft"] >= 12) | (zz["share 2016-23"] >= 0.03) | (zz["filers per aircraft"] < 0.75)]
    _repel(ax2, lab["share 2016-23"].tolist(), lab["filers per aircraft"].tolist(),
           [a.replace(" · ", " ").replace(" n/a (no M3 card)", "") for a in lab["archetype"]],
           avoid=list(zip(zz["share 2016-23"], zz["filers per aircraft"])), marker_pt=7)
    # archetypes as columns, windows as rows
    ax = fig.add_subplot(gs[1])
    mat = z.set_index("archetype")[WINDOW_NAMES].astype(float).T
    norm = mat.div(mat.max(axis=0), axis=1)
    ax.imshow(norm.to_numpy(), cmap=BLUE, vmin=0, vmax=1, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            if val:
                ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if norm.iat[i, j] > 0.55 else INK)
    ax.set_yticks(range(len(WINDOW_NAMES)), _win_labels(WINDOW_NAMES), fontsize=7.5)
    ax.set_xticks(range(mat.shape[1]), [a.replace(" · ", " ").replace(" n/a (no M3 card)", "") for a in mat.columns],
                  rotation=90, fontsize=7)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Aircraft per window for each archetype (darker = the archetype's busiest window)", fontsize=9)
    _legend_arch(fig, ARCH_ORDER + ["Other"])
    return _save(fig, path, SRC + "; A0c archetypes (class × propulsor-unit bin) with 5 or more aircraft; Table 4.1.9.",
                 "Top: an archetype far right holds a big share of recent aircraft; high up it is filed by many different "
                 "filers per aircraft (open field), low down by few filers holding many aircraft (crowded by a few). Bubble "
                 "size = aircraft. Bottom: the same archetypes over the windows, count in the cell.")
def fig_abandonment(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.abandonment_by_class(v)
    t = t[t["class"].ne("all classes")]
    t = t[t["patents"] >= 5]
    fig, ax = plt.subplots(figsize=(W, 2.9))
    y = np.arange(len(t))
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == c), c) for c in t["class"]]
    ax.barh(y, t["lapsed share"], color=[_color(c) for c in codes], height=0.66)
    for yi, (_, r) in zip(y, t.iterrows()):
        ax.text(r["lapsed share"], yi, f" {int(r['lapsed'])}/{int(r['patents'])}", va="center", fontsize=7.5,
                bbox=dict(fc="white", ec="none", pad=0.2), zorder=3)
    allrow = la_tables.abandonment_by_class(v).set_index("class").loc["all classes"]
    ax.axvline(allrow["lapsed share"], color=INK, lw=1, ls="--", zorder=0)

    ax.set_yticks(y, t["class"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title(f"Primary patents no longer in force, per class (priority ≤ 2019); dashed = all classes "
                 f"{allrow['lapsed share']:.0%}", fontsize=9)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    return _save(fig, path, SRC + "; PatSeer legal_status_raw of the primary patent; Table 4.1.7.",
                 "Share of each class's primary patents that are no longer in force, among patents old enough to have "
                 "been granted and then kept or dropped. A high share is money withdrawn from that class.")


# ------------------------------------------------------- 4.2 provenance ----
def fig_region_grid(v: pd.DataFrame, path: Path, variables: Optional[List[str]] = None) -> Path:
    variables = variables or list(la_tables.GRID_VARIABLES)
    fig, axes = plt.subplots(len(variables), len(REGIONS), figsize=(W, 2.45 * len(variables) + 0.4))
    x = np.arange(len(WINDOW_NAMES))
    palettes = {
        "class": lambda cols: {c: _color(c) for c in cols},
        "propulsor units": lambda cols: dict(zip(cols, [BLUE(t) for t in np.linspace(0.25, 0.95, len(cols))])),
        "tilting unit": lambda cols: {True: CAT[1], False: CAT[0], "blank": OTHER},
        "ducted unit": lambda cols: {True: CAT[6], False: CAT[2], "blank": OTHER},
        "powertrain": lambda cols: {"Yes": CAT[2], "Hybrid": CAT[3], "Unknown": OTHER, "No": CAT[7]},
        "filer type": lambda cols: {"Named company": CAT[0], "University / institute": CAT[6], "Individual inventor": CAT[3], "Unattributed / independent": OTHER},
    }
    names = {True: "yes", False: "no", "blank": "not determinable", "Yes": "electric", "Hybrid": "hybrid",
             "Unknown": "not stated", "No": "non-electric"}
    for i, var in enumerate(variables):
        shares, n = la_tables.region_window_shares(v, var)
        if var == "class":
            keep = [c for c in ARCH_ORDER if c in shares.columns]
            other = shares.drop(columns=keep).sum(axis=1)
            shares = shares[keep].assign(Other=other)
        pal = palettes[var](list(shares.columns))
        for j, reg in enumerate(REGIONS):
            ax = axes[i, j]
            sub = shares.loc[reg].reindex(WINDOW_NAMES) if reg in shares.index.get_level_values(0) else None
            bottom = np.zeros(len(x))
            if sub is not None:
                for col in sub.columns:
                    vals = sub[col].fillna(0).to_numpy(dtype=float)
                    ax.bar(x, vals, bottom=bottom, color=pal.get(col, OTHER), width=0.74, edgecolor=SURFACE, lw=0.8,
                           label=names.get(col, metrics.ARCH_NAMES.get(col, col) if var == "class" else col))
                    for xi, (b, val) in enumerate(zip(bottom, vals)):
                        if val >= 0.3:
                            ax.text(xi, b + val / 2, f"{val:.0%}", ha="center", va="center", fontsize=7, color=INK,
                                    rotation=90, bbox=dict(fc="white", ec="none", pad=0.15, alpha=0.85))
                    bottom += vals
                blank = sub.isna().all(axis=1).to_numpy()
                for xi in x[blank]:
                    ax.text(xi, 0.5, "n < 10", ha="center", va="center", fontsize=7, color=INK2, rotation=90)
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            ax.spines[["left", "bottom"]].set_visible(False)
            if i == 0:
                ax.set_title(reg, fontsize=10, color=REGION_COLOR.get(reg, INK))
            if j == 0:
                ax.set_ylabel(var, fontsize=8.5)
            nn = n.loc[reg] if reg in n.index.get_level_values(0) else pd.Series(dtype=int)
            ax.set_xticks(x, [f"{WIN_SHORT[w]} ({int(nn.get(w, 0))})" for w in WINDOW_NAMES], fontsize=7, rotation=90)
            if i < len(variables) - 1:
                ax.tick_params(axis="x", labelbottom=False)
            if j == 1:
                ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12 if i < len(variables) - 1 else -0.62),
                          ncol=5 if len(pal) > 4 else len(pal),
                          handlelength=1.2, columnspacing=1.0)
    fig.suptitle(f"{', '.join(variables).capitalize()} per region and window: share of the region-window cell "
                 "(cell count under the axis)",
                 x=0.01, ha="left", fontsize=9.5, fontweight="bold")
    fig.subplots_adjust(hspace=0.95, wspace=0.08)
    return _save(fig, path, SRC + "; region = applicant region (identity), not publication office; cells under 10 aircraft blanked.",
                 "Each bar is 100 % of the aircraft of one region in one window. Read down a column for how a region's "
                 "aircraft changed, across a row for how regions differ at the same time. * partial window.")


def fig_country_class(v: pd.DataFrame, path: Path) -> Path:
    shares, n = la_tables.country_class(v, top=8)
    mat = shares.copy()
    mat.index = [f"{c} (n {int(n[c])})" for c in mat.index]
    fig, ax = plt.subplots(figsize=(W, 3.4))
    _heat(ax, mat, fmt="{:.0%}", vmax=0.5)
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=0)
    ax.set_title("Class share per applicant country, eight largest countries (codes as Figure 2.1a)")
    return _save(fig, path, SRC + "; assignee_country of the primary patent's identity record.",
                 "Rows sum to 100 %. Read across a row for a country's mix; down a column for where a class is filed. "
                 "Capped at 50 % so that the middle of the range keeps contrast.")


# ------------------------------------------------------- 4.3 assignees -----
def fig_coverage(v: pd.DataFrame, path: Path) -> Path:
    sizes = la_tables.firm_sizes(v)
    ari = set(la_tables.ari_firms(v)["company"])
    total = len(v)
    cum = sizes.cumsum() / total
    rank = np.arange(1, len(sizes) + 1)
    fig, ax = plt.subplots(figsize=(W, 3.8))
    ax.step(rank, cum, where="post", color=BLUE(0.8), lw=2)
    for i, (k, lab) in enumerate(((10, "≥ 10"), (5, "≥ 5"), (4, "≥ 4"), (3, "≥ 3"), (2, "≥ 2"))):
        nf = int((sizes >= k).sum())
        if nf:
            ax.axvline(nf, color=GRID, lw=1)
            ax.text(nf, 0.92 - 0.07 * i, f" {lab} aircraft: {nf} firms, {cum.iloc[nf - 1]:.0%}", fontsize=7.5, color=INK2,
                    bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.9), zorder=4)
    named_share = sizes.sum() / total
    ax.axhline(named_share, color=INK, lw=1, ls="--")
    ax.text(len(sizes), named_share + 0.012, f"all named companies {named_share:.0%} ", ha="right", va="bottom",
            fontsize=7.5, bbox=dict(fc="white", ec="none", pad=0.3))
    ax.axhline(1, color=GRID, lw=0.8)
    ax.text(len(sizes), 1.0, "whole analysis set (individuals and unattributed filers are the rest) ", ha="right", va="bottom", fontsize=7.5, color=INK2)
    pts = [(i + 1, float(cum.iloc[i]), f) for i, f in enumerate(sizes.index) if f in ari]
    for x_, y_, _ in pts:
        ax.plot(x_, y_, marker="o", ms=5, color=CAT[1], zorder=5)
    ax.set_xlim(0, len(sizes) + 1)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("named companies ranked by unique aircraft (largest first)")
    ax.set_ylabel("cumulative share of the analysis set")
    ax.set_title("How much of the analysis set the top N firms cover; labelled dots = firms on the AAM Reality Index",
                 fontsize=9)
    _hgrid(ax, "both")
    _repel(ax, [p_[0] for p_ in pts], [p_[1] for p_ in pts], [p_[2] for p_ in pts], marker_pt=5)
    return _save(fig, path, SRC + "; Table 4.3.1; ARI firms from " + ARI_SRC + ".",
                 "The curve climbs steeply over the first firms and then flattens: beyond the vertical marks each extra "
                 "firm adds a few aircraft. The cut for per-firm profiles is where a firm still has enough aircraft "
                 "for a class share to mean something (5).")


def fig_filers_over_time(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.filers_by_window(v).set_index("window").reindex(WINDOW_NAMES)
    co = la_tables.cohorts(v).set_index("window").reindex(WINDOW_NAMES).fillna(0)
    fig, (ax, axc) = plt.subplots(1, 2, figsize=(W, 3.8), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.35})
    x = np.arange(len(t))
    ax.bar(x, t["continuing firms"], color=BLUE(0.75), width=0.66, label="firms already seen in an earlier window")
    ax.bar(x, t["new firms"], bottom=t["continuing firms"], color=CAT[2], width=0.66, label="firms filing for the first time")
    gone = pd.to_numeric(t["firms last seen"], errors="coerce")
    ax.bar(x, -gone.fillna(0), color=CAT[7], width=0.66, label="firms not seen again (judged up to 2016–19)")
    for xi, (_, r) in zip(x, t.iterrows()):
        ax.text(xi, r["named firms active"] + 0.5, f"{int(r['named firms active'])} firms\n{int(r['aircraft by named firms'])} aircraft",
                ha="center", va="bottom", fontsize=7)
    ax.axhline(0, color=INK, lw=0.8)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.set_ylim(top=float(t["named firms active"].max()) * 1.3)
    ax.set_ylabel("named firms")
    ax.set_xticks(x, [f"{WIN_SHORT[w]}\nn {int(r['unique aircraft'])}" for w, (_, r) in zip(WINDOW_NAMES, t.iterrows())],
                  fontsize=7)
    ax.set_title("Filers per window: entries, returners, exits", fontsize=9.5)
    # cohorts: entrants by the class they entered with
    cols = [c for c in ARCH_ORDER if c in co.columns]
    other = co.drop(columns=["firms entering"] + cols).sum(axis=1)
    bottom = np.zeros(len(co))
    for c in cols + ["Other"]:
        vals = (co[c] if c != "Other" else other).to_numpy(dtype=float)
        axc.bar(x, vals, bottom=bottom, color=_color(c), width=0.66, edgecolor=SURFACE, lw=0.8)
        bottom += vals
    for xi, n in zip(x, co["firms entering"]):
        axc.text(xi, n + 0.4, f"{int(n)}", ha="center", va="bottom", fontsize=7.5)
    axc.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    axc.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7.5)
    axc.set_ylabel("firms entering")
    axc.set_title("Entry cohorts: first-window class of new firms", fontsize=9.5)
    _hgrid(axc, "y")
    h1, l1 = ax.get_legend_handles_labels()
    fig.legend(h1, l1, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2)
    _legend_arch(fig, ARCH_ORDER + ["Other"])
    return _save(fig, path, SRC + "; Tables 4.2.2a/b; named firms = companies and institutes.",
                 "Left, bars above zero: named firms with at least one aircraft in the window, first-timers and returners; "
                 "below zero, firms whose last filing is in that window (not judged in the last two windows). Under each "
                 "window: its aircraft (the individual-inventor and unattributed shares are in Table 4.2.2a). Right: the "
                 "firms that enter in each window, by the class of their first aircraft.")
def fig_firm_tiles(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.firm_windows(v)
    firms = (t.drop_duplicates("firm").assign(fi=lambda d: d["first window"].map(WINDOW_NAMES.index))
             .sort_values(["fi", "aircraft total"], ascending=[True, False])["firm"].tolist())
    fig, ax = plt.subplots(figsize=(W, 3.3))
    y = np.arange(len(WINDOW_NAMES))
    for xi, f in enumerate(firms):
        sub = t[t["firm"].eq(f)].set_index("window").reindex(WINDOW_NAMES)
        for yi, (w, r) in zip(y, sub.iterrows()):
            if r["aircraft"] > 0:
                ax.scatter(xi, yi, s=85 + 24 * r["aircraft"], color=_color(r["modal class"]), alpha=0.9,
                           marker=_bw_table().get(matplotlib.colors.to_hex(_color(r["modal class"])), ("", "", "o"))[2],
                           edgecolor=SURFACE, lw=0.8, zorder=3)
                ax.text(xi, yi, f"{int(r['aircraft'])}", ha="center", va="center", fontsize=7, color="white",
                        fontweight="bold", zorder=4)
    tot = t.drop_duplicates("firm").set_index("firm")["aircraft total"]
    ax.set_xticks(range(len(firms)), [f"{f} ({int(tot[f])})" for f in firms], rotation=55, ha="right", fontsize=7.5)
    ax.set_yticks(y, _win_labels(WINDOW_NAMES), fontsize=8)
    ax.invert_yaxis()
    ax.axhspan(y[-1] - 0.5, y[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.set_ylim(len(y) - 0.4, -0.6)
    ax.set_xlim(-0.6, len(firms) - 0.4)
    ax.set_title("Firms with 5 or more aircraft: aircraft per window (size, number) and the class filed most (shape)",
                 fontsize=9)
    fig._bw_off = True
    ax.spines[["left", "bottom"]].set_visible(False)
    _hgrid(ax, "both")
    tab_ = _bw_table()
    handles = [matplotlib.lines.Line2D([], [], ls="", marker=tab_.get(matplotlib.colors.to_hex(_color(c)), ("", "", "o"))[2],
                                       ms=7, color=_color(c), label=_arch_name(c) if c != "Other" else "Other types")
               for c in ARCH_ORDER + ["Other"]]
    _, y0, _ = _fig_bottom(fig)
    fig.legend(handles=handles, loc="upper center", ncol=4, bbox_to_anchor=(0.5, y0 - 0.01), fontsize=7.5)
    return _save(fig, path, SRC + "; Table 4.3.4; firms ordered by first window, then size.",
                 "One column per firm, one bubble per window it filed in. A column that changes colour is a firm that "
                 "changed its main class; a column that starts low is an entrant.")
def fig_proximity_region(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    m, summary = la_tables.proximity_by_region(ds, v)
    reg = m.attrs["region"]
    prof = a2.firm_profiles(ds, FIRM_MIN, "class")
    size = prof.sum(axis=1)
    n = len(m)
    fig, ax = plt.subplots(figsize=(W, W * 1.02))
    shown = m.to_numpy().copy()
    np.fill_diagonal(shown, np.nan)
    im = ax.imshow(shown, cmap=BLUE, vmin=0, vmax=1, extent=(-0.5, n - 0.5, n - 0.5, -0.5))
    for i_ in range(n):
        for j_ in range(n):
            val = float(m.iat[i_, j_])
            if i_ != j_ and val >= 0.75:
                ax.text(j_, i_, "1" if val >= 0.95 else f"{val:.1f}"[1:], ha="center", va="center", fontsize=7,
                        color="white" if val > 0.6 else INK)
    # the region strip: one hatched cell per row, left of the matrix, in the same axes
    hatch_reg = {"North America": "", "Europe": "////", "Asia-Pacific": "...."}
    for i_, f in enumerate(m.index):
        ax.add_patch(matplotlib.patches.Rectangle((-1.6, i_ - 0.5), 0.9, 1, facecolor=REGION_COLOR.get(reg[f], OTHER),
                                                  hatch=hatch_reg.get(reg[f], "xx"), edgecolor=(0, 0, 0, 0.55),
                                                  lw=0.4, clip_on=False))
    ax.set_xlim(-1.7, n - 0.5)
    ax.set_ylim(n - 0.5, -0.5)
    labels = [f"{f} ({int(size[f])})" for f in m.index]
    ax.set_yticks(range(n), labels, fontsize=7.5)
    ax.set_xticks(range(n), labels, rotation=90, fontsize=7.5)
    ax.tick_params(axis="y", pad=26)
    for sp_ in ax.spines.values():
        sp_.set_visible(False)
    txt = " · ".join(f"{r['firm pair']}: mean {r['mean']:.2f} over {int(r['pairs'])} pairs" for _, r in summary.iterrows())
    ax.set_title("Technological proximity between firms (class profile); strip = the firm's region", fontsize=9, pad=22)
    handles = [matplotlib.patches.Patch(facecolor=REGION_COLOR[r_], hatch=hatch_reg[r_], edgecolor=(0, 0, 0, 0.55), label=r_)
               for r_ in REGIONS]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, fontsize=7.5, frameon=False,
              borderaxespad=0.2)
    fig.canvas.draw()
    lab_bottom = ax.xaxis.get_tightbbox(fig.canvas.get_renderer()).y0 / (fig.get_figheight() * fig.dpi)
    cax = fig.add_axes([0.3, lab_bottom - 0.035, 0.4, 0.014])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("proximity: 1 = same mix of classes, 0 = none in common", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    fig._bw_off = True
    return _save(fig, path, SRC + "; Jaffe (1986) cosine of firm × class vectors, firms with 5 or more aircraft; "
                 "Table 4.2.6a. " + txt + ".",
                 "Firms are ordered so that similar ones sit together. Two firms score 1 when they file the same mix of "
                 "classes, 0 when they share none; values of 0.75 and above are printed. The strip left of each row "
                 "gives the firm's region, to see whether design neighbours share a region.")


def fig_ari(v: pd.DataFrame, path: Path) -> Path:
    """4.2.7a — score and class mix."""
    f = la_tables.ari_firms(v)
    fig, ax = plt.subplots(figsize=(W, 3.9))
    ff = f.sort_values("ARI score", ascending=False).reset_index(drop=True)
    y = np.arange(len(ff))
    current = ff["release"].eq("May 2026")
    ax.barh(y, ff["ARI score"], color=[BLUE(0.8) if c else BLUE(0.35) for c in current], height=0.62)
    for yi, (_, r) in zip(y, ff.iterrows()):
        tag = "" if r["release"] == "May 2026" else f"  (to {r['release'][:3]} {r['release'][-4:]})"
        ax.text(r["ARI score"], yi, f" {r['ARI score']:.1f}{tag}", va="center", fontsize=7.5)
    ax.set_yticks(y, [f"{r['company']}  ·  {int(r['unique aircraft'])} aircraft" for _, r in ff.iterrows()], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 11.5)
    ax.set_xlabel("AAM Reality Index score (0–10)")
    ax.set_title("Index firms that file in the corpus: score and patent class mix", fontsize=9)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    ax_m = ax.inset_axes([1.03, 0, 0.24, 1], sharey=ax)
    left = np.zeros(len(ff))
    for code in ARCH_ORDER + ["Other"]:
        vals = np.array([(v[v["company_canonical"].eq(r["company"])]["topType"].map(_fold).eq(code).sum()
                          / max(int(v["company_canonical"].eq(r["company"]).sum()), 1)) for _, r in ff.iterrows()])
        ax_m.barh(y, vals, left=left, color=_color(code), height=0.62, edgecolor=SURFACE, lw=0.6)
        left += vals
    ax_m.set_xlim(0, 1)
    ax_m.set_xticks([0, 1], ["0", "100 %"], fontsize=7)
    ax_m.tick_params(labelleft=False, left=False)
    for sp_ in ax_m.spines.values():
        sp_.set_visible(False)
    ax_m.set_xlabel("class mix", fontsize=7.5)
    _legend_arch(fig, ARCH_ORDER + ["Other"])
    return _save(fig, path, ARI_SRC + "; corpus counts from " + SRC + "; Table 4.2.7a.",
                 "Bars: the index score; light bars are firms no longer listed, with the last score they had. Right: the "
                 "firm's patented aircraft by class.")


def fig_ari_history(v: pd.DataFrame, path: Path) -> Path:
    """4.2.7b — score history and funding against patented aircraft."""
    f = la_tables.ari_firms(v)
    hist = la_tables.ari_history_corpus(v)
    fig, (ax2, ax3) = plt.subplots(1, 2, figsize=(W, 5.2), gridspec_kw={"wspace": 1.3, "width_ratios": [1.0, 0.9]})
    ends = []
    for comp, sub in hist.groupby("company"):
        sub = sub.sort_values("date")
        ax2.plot(sub["date"], sub["score"], lw=1.4, marker="o", ms=2.2, alpha=0.85)
        ends.append((float(sub["score"].iloc[-1]), comp, ax2.get_lines()[-1].get_color()))
    ends.sort()
    xr = hist["date"].max()
    lo, hi = 3.0, 9.5
    ax2.set_ylim(lo, hi)
    ax2.figure.canvas.draw()
    bb = ax2.get_window_extent()
    step = (hi - lo) * (7 * 1.5 * ax2.figure.dpi / 72) / bb.height     # one 7-pt line and air, in score units
    ys = []
    for sc, _, _ in ends:                               # push up from the bottom ...
        ys.append(max(sc, (ys[-1] + step) if ys else lo + step / 2))
    top = hi - step / 2
    for k in range(len(ys) - 1, -1, -1):                # ... then down from the top
        ys[k] = min(ys[k], top if k == len(ys) - 1 else ys[k + 1] - step)
    lab_x = xr + pd.Timedelta(days=150)
    for (sc, comp, col), yv in zip(ends, ys):
        ax2.annotate(comp, (xr, sc), xytext=(lab_x, yv), textcoords="data", fontsize=7, va="center", color=col,
                     annotation_clip=False,
                     arrowprops=dict(arrowstyle="-", lw=0.4, color=col, relpos=(0, 0.5), shrinkA=1, shrinkB=0))
    ax2.set_title("Score per release since Dec 2020", fontsize=9)
    ax2.set_ylabel("ARI score")
    ax2.xaxis.set_major_locator(matplotlib.dates.YearLocator(2))
    ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
    _hgrid(ax2, "y")
    fc = f.copy()
    fc["funding"] = pd.to_numeric(fc["funding $M"].astype(str).str.replace(",", ""), errors="coerce")
    disclosed = fc.dropna(subset=["funding"])
    ax3.scatter(disclosed["unique aircraft"], disclosed["funding"], s=30 + 40 * disclosed["ARI score"].fillna(5) / 10,
                color=BLUE(0.8), edgecolor=SURFACE, zorder=3)
    ax3.set_yscale("log")
    ax3.set_xlim(0, disclosed["unique aircraft"].max() + 7)
    ax3.set_xlabel("unique aircraft in the corpus")
    ax3.set_ylabel("disclosed funding, $M (log)")
    ax3.set_title("Funding against patented aircraft", fontsize=9)
    _hgrid(ax3, "both")
    _repel(ax3, disclosed["unique aircraft"].tolist(), disclosed["funding"].tolist(),
           [c.replace(" Flight Technologies", "").replace(" / Geely Aviation", " / Geely") for c in disclosed["company"]],
           marker_pt=6)
    undisclosed = ", ".join(fc[fc["funding"].isna()]["company"])
    return _save(fig, path, ARI_SRC + "; Table 4.2.7a. Corporate-backed or undisclosed funding, not in the scatter: "
                 + undisclosed + ".",
                 "Left: how each firm's score moved; the names sit at the last score, spread apart where scores tie. "
                 "Right: disclosed funding against the number of patented aircraft, bubble = score.")


def fig_ari_clock(v: pd.DataFrame, path: Path) -> Path:
    """4.2.7c — the patent clock against the market clock."""
    tl = la_tables.ari_timeline(v).sort_values("first patent").reset_index(drop=True)
    fig, ax4 = plt.subplots(figsize=(W, 3.4))
    yy = np.arange(len(tl))
    for yi, (_, r) in zip(yy, tl.iterrows()):
        ax4.plot([r["first patent"], r["last patent"] + 0.02], [yi, yi], color=BLUE(0.7), lw=5, solid_capstyle="butt")
        ax4.plot(r["peak filing year"], yi, marker="|", ms=12, mew=2, color=INK)
        if pd.notna(r["first flight (ARI)"]):
            ax4.plot(r["first flight (ARI)"], yi, marker="^", ms=7, color=CAT[1], zorder=5)
        if pd.notna(r["entry into service (ARI)"]):
            ax4.plot(r["entry into service (ARI)"], yi, marker="D", ms=6, color=CAT[2], zorder=5)
    ax4.set_yticks(yy, [f"{r['company']} ({int(r['unique aircraft'])})" for _, r in tl.iterrows()], fontsize=7.5)
    ax4.invert_yaxis()
    ax4.axvline(2026.7, color=MUTED, lw=1, ls=":")
    ax4.text(2026.8, len(tl) - 0.4, "today", fontsize=7, color=INK2)
    ax4.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
    ax4.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))
    handles = [matplotlib.lines.Line2D([], [], color=BLUE(0.7), lw=5, label="first to last patent (priority years)"),
               matplotlib.lines.Line2D([], [], color=INK, marker="|", ms=10, mew=2, ls="", label="peak filing year"),
               matplotlib.lines.Line2D([], [], color=CAT[1], marker="^", ms=7, ls="", label="first flight (index)"),
               matplotlib.lines.Line2D([], [], color=CAT[2], marker="D", ms=6, ls="", label="entry into service (index, planned)")]
    ax4.legend(handles=handles, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax4.set_title("Patent clock against market clock, index firms listed in May 2026", fontsize=9)
    _hgrid(ax4, "x")
    return _save(fig, path, ARI_SRC + "; corpus priority years; Table 4.2.7c.",
                 "Each row: the firm's patent span and its peak filing year, against the first flight and the planned "
                 "entry into service the index states. Patents lead the market clock by several years.")
def fig_mission(v: pd.DataFrame, path: Path) -> Path:
    linked = la_tables.linked_aircraft(v)
    tabs = la_tables.mission_tables(linked)
    fields = ["capacity", "piloting", "power source", "status"]
    fig = plt.figure(figsize=(W, 8.2))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.05], hspace=1.35, wspace=0.55)
    order5 = [c for c in ["VT", "LC", "WM", "ER", "HB"] if c in linked["class5"].values]
    ns = linked["class5"].value_counts()
    for k, field in enumerate(fields):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        t = tabs[field].set_index(field).drop(columns="all").reindex(columns=order5, fill_value=0)
        share = t.div(t.sum(axis=0), axis=1).T
        share.index = [f"{c} (n {int(ns[c])})" for c in share.index]
        cols = list(share.columns)
        pal = dict(zip(cols, [BLUE(x) for x in np.linspace(0.9, 0.25, len(cols))]))
        _stack_h(ax, share, pal, min_label=0.2)
        for t_ in ax.texts:
            t_.set_fontsize(7)
        ax.set_title(field, fontsize=9)
        ax.tick_params(axis="both", labelsize=7.5)
        ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, handlelength=1.2, columnspacing=0.8)
    ax_h = fig.add_subplot(gs[2, :])
    ag = tabs["agreement"].set_index("patent label")
    ag.index = [next(k for k, nm in FOLD5_NAMES.items() if i_.replace("G1 folded: ", "") == nm) for i_ in ag.index]
    _heat(ax_h, ag.div(ag.sum(axis=1), axis=0), counts=ag)
    ax_h.set_aspect("equal")
    ax_h.set_title("Folded patent class (rows) against the class evtol.news gives the same aircraft (columns)", fontsize=9)
    ax_h.set_xticks(range(ag.shape[1]), ag.columns, rotation=0, fontsize=7.5)
    ax_h.tick_params(axis="y", labelsize=7.5)
    fig.suptitle(f"Mission of the {len(linked)} aircraft linked to an evtol.news page, by the patent's class folded to the "
                 "directory's five classes", x=0.01, y=0.995, ha="left", fontsize=9.5, fontweight="bold")
    return _save(fig, path, EVN_SRC + "; G1 class folded as Table 5.5a (VT vectored thrust, LC lift + cruise, WM wingless, "
                 "ER electric rotorcraft, HB hover bikes); capacity, piloting, power source and status parsed from the page text.",
                 "(i) to (iv): each bar is 100 % of the linked aircraft of one folded class. Bottom: how often the folded "
                 "patent class agrees with the directory's class of the same aircraft (count in the cell).")


def fig_filings_per_year(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.filings_per_year(ds, v).set_index("priority year")
    t = t[t.index >= 2005]
    p90 = t.attrs["p90"]
    fig, ax = plt.subplots(figsize=(W, 3.8))
    bottom = np.zeros(len(t))
    colors = {**REGION_COLOR, "Other regions": OTHER}
    hatches = {"North America": "", "Europe": "", "Asia-Pacific": "", "Other regions": ""}
    for col in REGIONS + ["Other regions"]:
        bars = ax.bar(t.index, t[col], bottom=bottom, color=colors[col], width=0.8, label=col, edgecolor=SURFACE, lw=0.8,
                      hatch=hatches[col])
        bottom += t[col].to_numpy()
    for xi, (_, r) in zip(t.index, t.iterrows()):
        if not r["complete"]:
            ax.bar(xi, r["unique aircraft"], color=(1, 1, 1, 0.45), edgecolor=INK, lw=1.0, ls="--", width=0.8)
            top = max(r["unique aircraft"], r["patents acquired"])
            ax.text(xi, top + 5, f"{int(r['unique aircraft'])}", ha="center", fontsize=7, color=INK2,
                    bbox=dict(fc="white", ec="none", pad=0.2))
    ax.plot(t.index, t["patents acquired"], color=INK, lw=2, marker="o", ms=3.5, label="patents acquired (all 1 639)")
    first_incomplete = int(t.index[~t["complete"]].min())
    ax.axvline(first_incomplete - 0.5, color=INK, lw=0.8, ls="--")
    ax.text(first_incomplete - 0.4, ax.get_ylim()[1] * 0.97, f"incomplete: within {p90:.0f} years\n(90th-pct lag) of the snapshot",
            va="top", fontsize=7, color=INK2)
    ax.set_xticks(list(t.index), [("≤2005" if y == 2005 else str(y)) for y in t.index], rotation=45, fontsize=7.5)
    ax.set_ylabel("unique aircraft (bars) · patents acquired (line)")
    ax.legend(loc="upper left", fontsize=7.5)
    ax.set_title("Filings per priority year, by applicant region; dashed, faded bars are years still filling")
    _hgrid(ax, "y")
    return _save(fig, path, SRC + f"; Table 4.1.1; PatSeer snapshot {t.attrs['snapshot']}; 90th-percentile priority-to-publication lag = {p90:.0f} years.",
                 "Bars: representative unique aircraft by the priority year of their primary record, stacked by applicant "
                 "region (region hatches survive black and white). Line: every acquired patent. A year is drawn faded with a dashed outline "
                 "while the snapshot is less than the 90th-percentile lag after its end: those bars will still grow.")


def fig_dominant_design(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.dominant_design(v)
    fig, axes = plt.subplots(1, 3, figsize=(W, 3.3), gridspec_kw={"wspace": 0.45})
    x = np.arange(len(WINDOW_NAMES))
    ax = axes[0]
    for lvl, col, mk in (("A0c", CAT[0], "o"), ("A1t", CAT[1], "s")):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, sub["top share"], marker=mk, lw=2, ms=5, color=col, label=f"{lvl}: top archetype share")
    ax.axhline(0.5, color=INK, lw=1, ls="--")
    ax.text(0.0, 0.52, "> 50 %, two windows", fontsize=7, color=INK2)
    ax.set_ylim(0, 0.6)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("Condition 1:\ntop archetype share", fontsize=8.5)
    h1, l1 = ax.get_legend_handles_labels()
    for ax, lvl in zip(axes[1:], ("A0c", "A1t")):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, sub["D2 permutation low"], sub["D2 permutation high"], color=GRID, alpha=0.9,
                        label="permutation band (labels shuffled across windows)")
        ax.errorbar(x, sub["D2"], yerr=[sub["D2"] - sub["D2 low"], sub["D2 high"] - sub["D2"]], marker="o", ms=4.5,
                    lw=1.8, capsize=2, color=CAT[0] if lvl == "A0c" else CAT[1], label="observed ²D, rarefied (95 %)")
        ax.set_title(f"Condition 2:\n²D at {lvl} against the band", fontsize=8.5)
        ax.set_ylim(0)
        if lvl == "A0c":
            h, l = ax.get_legend_handles_labels()
            fig.legend(h1 + h, l1 + l, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
            fig.subplots_adjust(bottom=0.34)
    for ax in axes:
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    fig.suptitle("The dominant-design test fixed in the Preliminary Analysis (5.7), applied per window",
                 x=0.01, y=1.04, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.2; rarefied to 40 aircraft; 200 permutations; Q (condition 3) needs the Gower distance and is not yet computed.",
                 "Left: a dominant design needs the top archetype above the dashed line in two consecutive complete windows; "
                 "A0c = class × propulsor bin, A1t = class × wings × tilting. (ii) and (iii): the window is more concentrated "
                 "than chance only where the observed ²D falls below the grey band.")


def fig_class_configs(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.class_configs(v)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.2), gridspec_kw={"wspace": 0.3})
    x = np.arange(len(WINDOW_NAMES))
    for code, sub in t.groupby("code", sort=False):
        sub = sub.set_index("window").reindex(WINDOW_NAMES)
        mk, ls = _cs(code)
        ax.plot(x, sub["modal share"], marker=mk, ls=ls, lw=2, ms=5, color=_color(code), label=f"{code}")
        ax2.plot(x, sub["configurations"] / sub["aircraft"], marker=mk, ls=ls, lw=2, ms=5, color=_color(code), label=code)
    for a in (ax, ax2):
        a.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7.5)
        a.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(a, "y")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 0.5)
    ax.set_title("Share of the class's modal configuration", fontsize=9.5)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("distinct configurations per aircraft")
    ax2.set_title("How many configurations the class holds", fontsize=9.5)
    ax2.legend(fontsize=7.5, loc="lower left", ncol=2)
    fig.suptitle("Within-class convergence, four largest classes: configuration = propulsor bin × ducted × booms × tail",
                 x=0.01, y=1.03, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.3 names the modal configuration per class and window; windows with fewer than 5 aircraft of the class blank.",
                 "Left: the share of the class's aircraft in its single most common configuration; a class settling on one "
                 "design would climb. Right: distinct configurations divided by aircraft; 1.0 means every aircraft is its own "
                 "configuration, a falling line means designs repeat.")


def fig_dimension_drift(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.dimension_drift(v)
    metrics_ = [("median propulsor units", "median units", None), ("ducted share", "ducted share", 1),
                ("tilting share", "tilting share", 1), ("boom share", "boom share", 1)]
    fig, axes = plt.subplots(1, 4, figsize=(W, 2.7), gridspec_kw={"wspace": 0.45})
    x = np.arange(len(WINDOW_NAMES))
    for ax, (col, title, top) in zip(axes, metrics_):
        for code, sub in t.groupby("code", sort=False):
            sub = sub.set_index("window").reindex(WINDOW_NAMES)
            mk, ls = _cs(code)
            ax.plot(x, sub[col], marker=mk, ls=ls, lw=1.8, ms=4, color=_color(code), label=code)
        ax.set_title(title, fontsize=8.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        if top:
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        else:
            ax.set_ylim(0)
        _hgrid(ax, "y")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=4)
    fig.subplots_adjust(bottom=0.3)
    fig.suptitle("Dimension drift inside the four largest classes, per window", x=0.01, y=1.06, ha="left",
                 fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.4; windows with fewer than 5 aircraft of the class left out.",
                 "One line per class. Substitution shows here before a class label changes: a class whose rotor count "
                 "climbs, or whose ducted share falls, is changing what it is while keeping its name.")


def fig_transitions(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.transitions(v)
    t["from"] = t["from"].map(_fold); t["to"] = t["to"].map(_fold)
    order = [c for c in ARCH_ORDER + ["Other"]]
    mat = t.groupby(["from", "to"])["pairs"].sum().unstack(fill_value=0).reindex(index=order, columns=order, fill_value=0)
    share = mat.div(mat.sum(axis=1).replace(0, np.nan), axis=0)
    fig, ax = plt.subplots(figsize=(W * 0.72, 4.6))
    _heat(ax, share.fillna(0), counts=mat, vmax=1.0)
    ax.set_xticks(range(len(order)), order, rotation=0)
    ax.set_yticks(range(len(order)), [f"{c}  ({int(mat.loc[c].sum())})" for c in order])
    ax.set_xlabel("class of the firm's next aircraft")
    ax.set_ylabel("class of the earlier aircraft")
    ax.set_title(f"Within-firm successions: {t.attrs['pairs']} consecutive pairs in {t.attrs['firms']} named firms; "
                 f"{t.attrs['same share']:.0%} stay in class", fontsize=9)
    return _save(fig, path, SRC + "; Table 4.2.4; each named firm's aircraft in priority order, every consecutive pair counted once.",
                 "Rows are the earlier aircraft's class and sum to 100 %; the number is pairs. The diagonal is a firm "
                 "repeating its class; an off-diagonal cell is what firms move to next. Colour is the row share.")


def fig_ip_strategy(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    f = la_tables.ip_strategy(ds, v)
    c = la_tables.ip_by_class(v)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(W, 7.4), gridspec_kw={"height_ratios": [1.5, 1], "hspace": 0.55})
    for _, r in f.iterrows():
        ax.scatter(r["unique aircraft"], r["patents per aircraft"], s=25 + 3 * r["mean forward citations"],
                   color=REGION_COLOR.get(r["region"], OTHER), alpha=0.85, edgecolor=SURFACE, lw=0.8, zorder=3,
                   marker={"North America": "o", "Europe": "s", "Asia-Pacific": "^"}.get(r["region"], "o"))
    ax.set_xscale("log")
    ax.set_xticks([5, 10, 20, 50], ["5", "10", "20", "50"])
    ax.set_xlabel("unique aircraft (log)")
    ax.set_ylabel("representative patents per aircraft")
    ax.axhline(1, color=GRID, lw=1)
    ax.set_title("Depth against breadth, firms with 5+ aircraft (bubble = mean forward citations; shape = region)", fontsize=9)
    _hgrid(ax, "both")
    handles = [matplotlib.lines.Line2D([], [], ls="", marker=m_, ms=7, color=REGION_COLOR[r_], label=r_)
               for r_, m_ in zip(REGIONS, ("o", "s", "^"))]
    ax.legend(handles=handles, fontsize=7.5, loc="upper right", ncol=1)
    ax.set_xlim(4, 160)
    _repel(ax, f["unique aircraft"].tolist(), f["patents per aircraft"].tolist(), f["firm"].tolist(), marker_pt=8)
    cc = c[c["patents"] >= 10]
    y = np.arange(len(cc))
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == n), n) for n in cc["class"]]
    ax2.barh(y - 0.2, cc["median claims"], height=0.38, color=BLUE(0.45), label="median claims")
    ax2.barh(y + 0.2, cc["mean forward citations"], height=0.38, color=BLUE(0.85), label="mean forward citations")
    ax2.set_yticks(y, [f"{code} ({int(n)})" for code, n in zip(codes, cc["patents"])], fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_title("Claims and citations per class (primary patents)", fontsize=8.8)
    ax2.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    return _save(fig, path, SRC + "; PatSeer claim_count, forward_citations, family_size; Tables 4.2.5a/b.",
                 "(i): above the line a firm files more than one patent per aircraft (protecting each design in depth); "
                 "far right it files many different aircraft (exploring). (ii): how much each class is claimed and cited; "
                 "citations favour older patents, so read them with the median priority year in the table.")


def fig_specialisation(v: pd.DataFrame, path: Path) -> Path:
    lq, counts = la_tables.specialisation(v)
    mat_all, tot = lq.T, counts.sum(axis=1)
    halves = np.array_split(np.arange(mat_all.shape[1]), 2)
    fig, axes = plt.subplots(2, 1, figsize=(W, 4.4), gridspec_kw={"hspace": 1.05})
    for ax, idx in zip(axes, halves):
        mat = mat_all.iloc[:, idx]
        n = counts.T.iloc[:, idx]
        im = ax.imshow(np.log2(mat.to_numpy(dtype=float).clip(0.25, 4)), cmap="RdBu_r", vmin=-2, vmax=2, aspect="auto")
        for a in range(mat.shape[0]):
            for b in range(mat.shape[1]):
                val = mat.iat[a, b]
                ax.text(b, a, f"{val:.1f}" if n.iat[a, b] else "–", ha="center", va="center", fontsize=7,
                        color="white" if abs(np.log2(max(val, 0.25))) > 1.1 else INK)
        ax.set_yticks(range(mat.shape[0]), mat.index, fontsize=7.5)
        ax.set_xticks(range(mat.shape[1]), [f"{c.replace(' · ', ' ').replace(' n/a (no M3 card)', '')} ({int(tot[c])})"
                                            for c in mat.columns], rotation=90, fontsize=7)
        for sp_ in ax.spines.values():
            sp_.set_visible(False)
    cb = fig.colorbar(im, ax=list(axes), fraction=0.02, pad=0.01, ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_yticklabels(["¼", "½", "1", "2", "4"], fontsize=7)
    cb.set_label("region share ÷ overall share", fontsize=7)
    axes[0].set_title("Regional specialisation by archetype (A0c); the number in each cell is the index", fontsize=9)
    return _save(fig, path, SRC + "; Table 4.3.3 (with the counts per cell); three main regions only.",
                 "Each cell: the archetype's share of the region's aircraft divided by its share of all aircraft. 1 = as "
                 "everywhere, 2 = twice the overall share, – = none. Read a row for what a region leans to, a column for "
                 "where an archetype is concentrated. Archetypes ordered by size, split over two strips.")

def fig_industry_by_class(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.industry_by_class(v).set_index("class")
    tab = t.drop(columns="aircraft")
    tab = tab[tab.sum().sort_values(ascending=False).index]
    share = tab.div(tab.sum(axis=1), axis=0)
    share.index = [f"{i} (n {int(n)})" for i, n in zip(t.index, t["aircraft"])]
    cols = list(share.columns)
    pal = {c: (OTHER if c == "General_Unspecified" else CAT[i % len(CAT)]) for i, c in enumerate([c for c in cols if c != "General_Unspecified"])}
    pal["General_Unspecified"] = OTHER
    fig, ax = plt.subplots(figsize=(W, 4.0))
    _stack_h(ax, share, pal, min_label=0.1)
    pats = ["", "////", "....", "\\\\\\", "xxxx", "----", "++++", "oo", "**", "||||", "//..", "xx.."]
    per = len(share)
    for c_i, patch_group in enumerate([ax.patches[k:k + per] for k in range(0, len(ax.patches), per)]):
        for pa in patch_group:
            pa.set_hatch(pats[c_i % len(pats)])
            pa.set_edgecolor((0, 0, 0, 0.55))
            pa.set_linewidth(0.4)
    fig._bw_off = True
    ax.set_title("Industry named in the patent text, by class (text model, 03a)", fontsize=9.5)
    ax.legend([c.replace("_", " / ") for c in cols], fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1)
    return _save(fig, path, SRC + "; identity industry_primary (text classifier, one value per patent); Table 5.5.",
                 "Each bar is 100 % of the class's aircraft. Grey is 'general / unspecified', half the corpus: patents "
                 "rarely name a mission. Read the coloured part only.")


def fig_examination(v: pd.DataFrame, path: Path) -> Path:
    to = la_tables.examination(v, "pub_office").set_index("pub_office")
    tc = la_tables.examination(v, "topType").set_index("topType")
    pal = {"granted, in force": CAT[2], "pending": BLUE(0.4), "lapsed (non-payment)": CAT[3], "expired": OTHER,
           "withdrawn": CAT[1], "refused": CAT[7]}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.6), gridspec_kw={"width_ratios": [0.8, 1.2], "wspace": 0.45})
    code_of = {nm: k for k, nm in metrics.ARCH_NAMES.items()}
    for a, t, title in ((ax, to, "by publication office"), (ax2, tc, "by class")):
        tab = t.drop(columns="patents")
        share = tab.div(tab.sum(axis=1), axis=0)
        share.index = [f"{code_of.get(i, i)} (n {int(n)})" for i, n in zip(t.index, t["patents"])]
        _stack_h(a, share, pal, min_label=0.12)
        a.set_title(title, fontsize=9.5)
        a.tick_params(axis="y", labelsize=7.5)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(1.3, -0.1), ncol=6)
    fig.suptitle("Legal status of the primary patents at the snapshot", x=0.01, y=1.02, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; PatSeer legal_status_raw at the 2026-06 snapshot; Tables 5.6a/b.",
                 "Examination outcome as a proxy for regulatory friction on the IP side: refused and withdrawn shares "
                 "differ by office far more than by class. Pending is high where filings are recent (CN, WO).")


# ------------------------------------------------------- Chapter 1 and 3.1, compact (2026-09-22, 4th round)
def _vbar_labels(ax, bars, fmt="{:.0f}", fs=7):
    for b in bars:
        h = b.get_height()
        if h:
            ax.text(b.get_x() + b.get_width() / 2, h, fmt.format(h), ha="center", va="bottom", fontsize=fs)


def fig_c1_removal(ds: Dataset, path: Path) -> Path:
    r = a2.d1_rejection_reasons(ds)
    r = r[~r["code"].str.startswith(("subtotal", "total"))].sort_values("patents", ascending=False)
    gate = r["code"].str.startswith("Similar").to_numpy()
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.9), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.25})
    x = np.arange(len(r))
    bars = ax.bar(x, r["patents"], color=np.where(gate, CAT[1], CAT[0]), width=0.66)
    _vbar_labels(ax, bars)
    short = {"No Usable, Sufficient, or Legible Aircraft Image": "No usable aircraft image",
             "No content available on the patent": "No content on the patent",
             "Not VTOL (STOL / CTOL)": "Not VTOL"}
    ax.set_xticks(x, [short.get(t, t) for t in r["reason"]], fontsize=7, rotation=35, ha="right")
    ax.set_title("Why patents left the analysis (patents)", fontsize=9)
    ax.legend(handles=[matplotlib.patches.Patch(color=CAT[0], label="rejected at labelling"),
                       matplotlib.patches.Patch(color=CAT[1], label="domain gate (Similar tag)")],
              loc="upper right", fontsize=7)
    ax.set_ylim(0, r["patents"].max() * 1.15)
    _hgrid(ax, "y")
    g = ds.gated_out[ds.gated_out["is_primary"].fillna(False).astype(bool)]
    tab = pd.crosstab(g["topType"].map(_fold), g["similar_tag"]).reindex(ARCH_ORDER + ["Other"]).fillna(0)
    tab = tab.loc[tab.sum(axis=1) > 0]
    bottom = np.zeros(len(tab))
    tagc = {"UAVSimilar": CAT[1], "ElectricSimilar": CAT[6], "STOLSimilar": CAT[3]}
    xx = np.arange(len(tab))
    for col in tab.columns:
        ax2.bar(xx, tab[col], bottom=bottom, color=tagc.get(col, OTHER), width=0.66, edgecolor=SURFACE, lw=0.8,
                label=col.replace("Similar", "-similar"))
        bottom += tab[col].to_numpy()
    for xi, t in zip(xx, bottom):
        ax2.text(xi, t, f"{t:.0f}", ha="center", va="bottom", fontsize=7)
    ax2.set_xticks(xx, [("Oth." if c == "Other" else c) for c in tab.index], fontsize=7)
    ax2.set_ylim(0, bottom.max() * 1.18)
    ax2.set_title(f"Aircraft removed by the gate ({int(tab.values.sum())}), by class", fontsize=9)
    ax2.legend(fontsize=7, loc="upper right")
    _hgrid(ax2, "y")
    return _save(fig, path, SRC + "; wizard disapproval reasons and the Similar tags (Table 1.1a); class codes as Figure 2.1a.",
                 "Left: patents by the reason they left, plain at labelling, hatched by the domain gate. Right: the unique "
                 "aircraft the gate removed, by the class they were labelled with.")


def fig_c1_duplicates(ds: Dataset, path: Path) -> Path:
    d = a2.d7_duplicates(ds)
    d = d[d["type"].astype(str).str[:2].isin(["O1", "O2", "S3"])].reset_index(drop=True)
    app = a2.d7_aircraft_per_patent(ds)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.4), gridspec_kw={"wspace": 0.3})
    lab = ["O1\nsame aircraft,\nnew figures", "O2\nsame aircraft,\nsame figures", "S3\nsimilar aircraft,\nnew unique"]
    bars = ax.bar(range(3), d["observations"], color=[CAT[0], BLUE(0.45), CAT[2]], width=0.6)
    _vbar_labels(ax, bars)
    ax.set_xticks(range(3), lab, fontsize=7)
    ax.set_ylim(0, d["observations"].max() * 1.15)
    ax.set_title("Repeated observations (patents)", fontsize=9)
    _hgrid(ax, "y")
    xs = app.iloc[:, 0].astype(str)
    bars = ax2.bar(xs, app["patents"], color=BLUE(0.7), width=0.6)
    _vbar_labels(ax2, bars)
    ax2.set_yscale("log")
    ax2.set_ylim(top=app["patents"].max() * 2.5)
    ax2.set_xlabel("aircraft drawn in one patent", fontsize=7.5)
    ax2.set_title("Aircraft per primary patent (log scale)", fontsize=9)
    _hgrid(ax2, "y")
    return _save(fig, path, SRC + "; Tables 1.2a/b.",
                 "Left: patents that repeat an aircraft already counted (O1, O2) or add a similar one (S3). Right: most "
                 "primary patents draw one aircraft.")


def fig_c1_evidence(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    vv = v.set_index("aircraft_id")
    nfig = vv["n_approved_this_variant"].astype(float)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw={"width_ratios": [0.8, 1.2], "wspace": 0.3})
    cnt = nfig.clip(upper=8).value_counts().sort_index()
    bars = ax.bar([("8+" if i >= 8 else str(int(i))) for i in cnt.index], cnt.values,
                  color=[CAT[1] if i == 1 else BLUE(0.6) for i in cnt.index], width=0.66)
    _vbar_labels(ax, bars)
    ax.set_ylim(0, cnt.max() * 1.15)
    ax.set_xlabel("whole-aircraft figures per aircraft", fontsize=7.5)
    ax.set_title(f"Figures per aircraft (median {nfig.median():.0f})", fontsize=9)
    _hgrid(ax, "y")
    g = vv.assign(single=nfig.eq(1), a=vv["topType"]).groupby("a").agg(n=("single", "size"), single=("single", "mean"))
    g = g.reindex([c for c in atlas.ALL_ARCH if c in g.index])
    xx = np.arange(len(g))
    ax2.bar(xx, g["single"], color=[_color(c) for c in g.index], width=0.66)
    for xi, (_, r) in zip(xx, g.iterrows()):
        ax2.text(xi, r["single"] + 0.01, f"{r['single']:.0%}", ha="center", va="bottom", fontsize=7)
    ax2.axhline(nfig.eq(1).mean(), color=INK2, lw=1, ls="--")
    ax2.set_xticks(xx, [f"{c}\n{int(n)}" for c, n in zip(g.index, g["n"])], fontsize=7)
    ax2.set_ylim(0, 0.85)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("Share resting on one figure, by class (n under code)", fontsize=9)
    _hgrid(ax2, "y")
    return _save(fig, path, SRC + "; Table 1.3; whole-aircraft figures only.",
                 "Left: how many approved whole-aircraft figures each aircraft rests on; the hatched bar = one only. Right: the "
                 "share of each class resting on one figure; the dashed line is the overall share.")


def fig_c3_fill(ds: Dataset, path: Path) -> Path:
    t = figures.fill_rate_by_parent(ds)
    part_color = {"every aircraft": BLUE(0.8), "wings present": CAT[2], "booms present": CAT[1]}
    fig, ax = plt.subplots(figsize=(W, 2.7))
    x = np.arange(len(t))
    ax.bar(x, t["share"], color=[part_color[p] for p in t["part"]], width=0.66)
    for xi, (_, r) in zip(x, t.iterrows()):
        ax.text(xi, r["share"] + 0.003, f"{r['share']:.0%}", ha="center", va="bottom", fontsize=7, rotation=90)
    ax.axhline(0.95, color=INK, lw=0.8, ls="--")
    ax.set_ylim(0.8, 1.1)
    ax.set_yticks([0.8, 0.85, 0.9, 0.95, 1.0])
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xticks(x, t["field"], rotation=55, ha="right", fontsize=7)
    ax.legend(handles=[matplotlib.patches.Patch(color=c, label=f"measured on {p}") for p, c in part_color.items()],
              fontsize=7, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0), frameon=False)
    ax.set_title("Share answered of each field, measured only on the aircraft that have its part", fontsize=9)
    _hgrid(ax, "y")
    return _save(fig, path, SRC + "; Table 3.1; a value an override hides is left out of the base.",
                 "One bar per field. A wing field is measured on the winged aircraft, a boom field on the aircraft with "
                 "booms, so a blank means a missing answer, not a missing part. Every field is at or above the dashed "
                 "95 % line. The axis starts at 80 %.")


# ------------------------------------------------------- reuse of atlas ----
#: atlas figures reused as they are: name -> atlas function
ATLAS_REUSE: Dict[str, Callable] = {
    "atlas_years": atlas.fig_years,
    "atlas_region": atlas.fig_region,
    "atlas_filers": atlas.fig_filers,
    "atlas_state_by_arch": atlas.fig_state_by_arch,
    "atlas_arch_gt": atlas.fig_arch_gt,
    "atlas_arch_time": atlas.fig_arch_time,
    "atlas_powertrain": atlas.fig_powertrain,
    "atlas_fields": atlas.fig_fields,
    "atlas_flagship": atlas.fig_flagship,
}


#: portrait sizes for the reused atlas figures (they are drawn at ``atlas.PAGE``, patched per call)
ATLAS_SIZE: Dict[str, tuple] = {
    "atlas_removal": (W, 4.4), "atlas_duplicates": (W, 3.8), "atlas_figure_approval": (W, 4.4),
    "atlas_years": (W, 4.0), "atlas_region": (W, 4.8), "atlas_filers": (W, 6.2), "atlas_state_by_arch": (W, 4.4),
    "atlas_arch_gt": (W, 5.6), "atlas_arch_time": (W, 4.0), "atlas_powertrain": (W, 4.6), "atlas_fields": (W, 5.6),
    "atlas_fill": (W, 5.4), "atlas_flagship": (W, 5.0), "atlas_units": (W, 5.4), "atlas_design_heatmaps": (W, 6.2),
}


def fig_design_heatmaps(ds: Dataset, av: pd.DataFrame, path: Path) -> Path:
    """The atlas design heatmaps redrawn 3 × 2 so each panel has half the page width."""
    af = a2.archetype_frame(ds)
    v2 = av.merge(af[["aircraft_id", "boomBin", "anyTilt"]], on="aircraft_id", how="left")
    nd = "not determinable"
    v2["anyTilt"] = v2["anyTilt"].map(lambda x: "yes" if x is True else "no" if x is False
                                      else x if isinstance(x, str) else nd)
    for col in ("wCount", "fusKin", "empType", "gearArch"):
        hid = a2.hidden_by_override(v2, col, ds.data_dictionary)
        if hid.any():
            v2[col] = v2[col].astype(object).where(~hid, nd)
    panels = [("wCount", "Wings", {"0": "none", "1": "1 wing", "2": "2 wings", "3": "3 wings", nd: "n/d"}),
              ("fusKin", "Fuselage motion", {"Variable Incidence": "Var. incid.", nd: "n/d"}),
              ("boomBin", "Booms", None),
              ("anyTilt", "Any propulsor tilts", {"n/a (no M3 card)": "no M3 card", nd: "n/d"}),
              ("empType", "Tail type", {"Conventional": "Conv.", nd: "n/d"}),
              ("gearArch", "Landing gear", {"Wheeled Gear": "Wheels", nd: "n/d"})]
    fig, axes = plt.subplots(3, 2, figsize=(W, 8.4), gridspec_kw={"hspace": 0.75, "wspace": 0.12})
    with plt.rc_context(STYLE):
        for k, (ax, (col, title, labels)) in enumerate(zip(axes.flat, panels)):
            tab = atlas._profile(v2, col, top=7 if col != "empType" else 6, labels=labels)
            atlas._heat(ax, tab, vmax=1)
            for t in ax.texts:
                t.set_fontsize(7)
            ax.set_title(title, fontsize=9)
            if k % 2:
                ax.set_yticklabels([])
            ax.tick_params(axis="x", labelsize=7, labelrotation=40)
            ax.tick_params(axis="y", labelsize=7.5)
    return _save(fig, path, SRC + "; archetype_frame (boom bin, any tilting unit); class codes as Figure 2.1a.",
                 "Each row is one class and sums to 100 % across a panel's columns. n/d = not determinable, a value "
                 "an override hides; 'no M3 card' marks HB and PFV, which have no propulsor card. Blank = design absence.")


def fig_units(ds: Dataset, av: pd.DataFrame, path: Path) -> Path:
    """The atlas propulsion figure stacked for a portrait page: units per class on top, shares below."""
    v = av
    order = [c for c in atlas.ALL_ARCH if c in v["atype"].values]
    fig = plt.figure(figsize=(W, 6.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1], hspace=0.55)
    ax = fig.add_subplot(gs[0])
    rng = np.random.default_rng(42)
    for i_, c in enumerate(order):
        u = v.loc[v["atype"].eq(c), "units"].dropna().to_numpy()
        if not len(u):
            ax.text(i_, 15, "no propulsor card", rotation=90, ha="center", va="center", fontsize=7, color=MUTED)
            continue
        ax.scatter(i_ + rng.uniform(-0.25, 0.25, len(u)), np.clip(u, 0, 30) + rng.uniform(-0.25, 0.25, len(u)),
                   s=8, color=_color(c), alpha=0.55, lw=0)
        q1, med, q3 = np.percentile(u, [25, 50, 75])
        ax.plot([i_, i_], [q1, q3], color=INK, lw=2.5)
        ax.plot(i_, med, "o", color=SURFACE, mec=INK, ms=6, mew=1.6)
    ax.set_xticks(range(len(order)), order, fontsize=7.5)
    ax.set_ylim(-1, 31)
    ax.set_ylabel("propulsor units (capped at 30)", fontsize=7.5)
    ax.set_title("Propulsor units per class: dot = aircraft, bar = quartiles, ring = median", fontsize=9)
    _hgrid(ax, "y")
    st = a2.propulsion_states(v)
    units = pd.Series(v["units"].to_numpy(), index=v.index)
    feat = pd.DataFrame({"atype": v["atype"], "tilting unit": st["any_tilting"],
                         "fixed + tilting": st["any_tilting"] & st["any_fixed"], "ducted unit": st["any_ducted"],
                         "more than 8 units": (units > 8).astype("boolean").where(units.notna(), pd.NA)})
    g = feat.groupby("atype")
    tab = g.agg(lambda s_: float(s_.dropna().astype(float).mean()) if s_.notna().any() else np.nan).reindex(order).astype(float)
    base = g["tilting unit"].agg(lambda s_: int(s_.notna().sum())).reindex(order)
    mat = tab.T
    mat.columns = [f"{c}\n{int(base[c])}/{int((feat['atype'] == c).sum())}" for c in order]
    ax2 = fig.add_subplot(gs[1])
    _heat(ax2, mat, vmax=1)
    for t in ax2.texts:
        t.set_fontsize(7)
    ax2.set_xticks(range(mat.shape[1]), mat.columns, rotation=0, ha="center", fontsize=7)
    ax2.tick_params(axis="y", labelsize=7.5)
    ax2.set_title("Share of each class's aircraft with the feature, where it can be read (read / total under the code)",
                  fontsize=9)
    fig._bw_off = True
    return _save(fig, path, SRC + "; propulsor_units, propulsion states (rules of 2026-09-19); class codes as Figure 2.1a.",
                 "Top: one dot per aircraft; HB and PFV have no propulsor card and are left out, never counted as 0. "
                 "Bottom: share of each class with the feature, over the aircraft where it can be read; a tilting boom "
                 "is read from the boom tick.")


def _atlas(fn: Callable, ds: Dataset, av: pd.DataFrame, n: Dict, path: Path, size: tuple = (W, 5.0)) -> Path:
    page, legend, stack = atlas.PAGE, atlas._legend_arch, atlas._stack_h
    atlas.PAGE, atlas._legend_arch = size, _legend_arch
    atlas._stack_h = lambda ax, frame, colors, min_label=0.06, pct=True: stack(ax, frame, colors, max(min_label, 0.17), pct)
    try:
        with plt.rc_context({**STYLE, "font.size": 8.5, "axes.titlesize": 9.5, "legend.fontsize": 7.5}):
            fig, number, title = fn(ds, av, n)
            for ax in fig.axes:              # a dense categorical x axis reads vertically
                labs = [t.get_text() for t in ax.get_xticklabels()]
                if len(labs) >= 9 and all(len(t) <= 14 for t in labs) and any(labs):
                    ax.tick_params(axis="x", labelrotation=90)
            seen = set()
            for ax in fig.axes:              # side-by-side panels get room for the right panel's labels
                ss = ax.get_subplotspec() if hasattr(ax, "get_subplotspec") else None
                gs_ = ss.get_gridspec() if ss is not None else None
                if gs_ is not None and id(gs_) not in seen:
                    seen.add(id(gs_))
                    if gs_.ncols > 1:
                        gs_.update(wspace=max(gs_.wspace or 0.2, 0.6))
            if len(fig.axes) > 1:            # side-by-side panels: wrap titles so they cannot collide
                import textwrap
                for ax in fig.axes:
                    for loc in ("left", "center"):
                        t = ax.get_title(loc=loc)
                        if t and len(t) > 34:
                            ax.set_title("\n".join(textwrap.wrap(t, 34)), fontsize=9, loc=loc)
            _atlas_save(fig, path)
    finally:
        atlas.PAGE, atlas._legend_arch, atlas._stack_h = page, legend, stack
    return path


def _atlas_save(fig, path: Path) -> None:
    with plt.rc_context(STYLE):
        _bw(fig)
        for ax in fig.axes:
            if ax.images:                      # heatmaps: 7-pt cell values, long column names vertical
                for t in ax.texts:
                    t.set_fontsize(7)
                if any(len(t.get_text()) > 8 for t in ax.get_xticklabels()):
                    ax.tick_params(axis="x", labelrotation=90)
            leg = ax.get_legend()
            if leg is not None:
                leg.set_loc("best")
        _wrap_texts(fig)
        _fit_width(fig)
        if _clear_panels(fig):
            _fit_width(fig)
            _clear_panels(fig)
        note = getattr(fig, "_atlas_note", None)
        read = _mark_keeping_width(fig, path, note[1] if note else "")
        if note:
            fig._atlas_note = (note[0], read)
        _declutter(fig)
        if getattr(fig, "_atlas_note", None):
            _stamp(fig, *fig._atlas_note)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
        plt.close(fig)


def render_all(ds: Dataset, out_dir: Path, partial_window_start: int = 2024, **_) -> Dict[str, Path]:
    """Draw every figure of the Labelling Analysis into ``out_dir/figures``; returns {name: path}."""
    out = Path(out_dir) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    PANELS.clear()
    n = numbers.live(ds, partial_window_start)
    v = la_tables.base(ds)
    av = atlas._variants(ds)
    av["window"] = av["window"].cat.rename_categories(["≤2011", "12–15", "16–19", "20–23", "24–26*"])
    paths: Dict[str, Path] = {}
    # schemes reused from the Preliminary Analysis
    paths["fig_02_refinement_funnel"] = figures.refinement_funnel_svg(n, out / "fig_02_refinement_funnel.svg")
    paths["design_space_cards"] = design_space_cards_svg(n, out / "design_space_cards.svg")
    for name, src in figures.CODEBOOK_DRAWINGS.items():
        paths[name] = Path(shutil.copyfile(src, out / src.name))
    for name, fn in ATLAS_REUSE.items():
        paths[name] = _atlas(fn, ds, av, n, out / f"{name}.png", ATLAS_SIZE.get(name, (W, 5.0)))
    jobs = {
        "firm_weighted": lambda p: fig_firm_weighted(v, p),
        "spans_by_firm": lambda p: fig_spans_by_firm(ds, v, p),
        "two_counts": lambda p: fig_two_counts(ds, p),
        "lead_lag": lambda p: fig_lead_lag(v, p),
        "class_cycles": lambda p: fig_class_cycles(v, p),
        "hill": lambda p: fig_hill(v, p),
        "zones": lambda p: fig_zones(v, p),
        "abandonment": lambda p: fig_abandonment(v, p),
        "region_grid": lambda p: fig_region_grid(v, p, ["class", "propulsor units", "tilting unit"]),
        "region_grid_b": lambda p: fig_region_grid(v, p, ["ducted unit", "powertrain", "filer type"]),
        "country_class": lambda p: fig_country_class(v, p),
        "coverage": lambda p: fig_coverage(v, p),
        "filers_over_time": lambda p: fig_filers_over_time(v, p),
        "firm_tiles": lambda p: fig_firm_tiles(v, p),
        "proximity_region": lambda p: fig_proximity_region(ds, v, p),
        "ari": lambda p: fig_ari(v, p),
        "mission": lambda p: fig_mission(v, p),
        "filings_per_year": lambda p: fig_filings_per_year(ds, v, p),
        "atlas_removal": lambda p: fig_c1_removal(ds, p),
        "atlas_duplicates": lambda p: fig_c1_duplicates(ds, p),
        "atlas_figure_approval": lambda p: fig_c1_evidence(ds, v, p),
        "atlas_fill": lambda p: fig_c3_fill(ds, p),
        "atlas_design_heatmaps": lambda p: fig_design_heatmaps(ds, av, p),
        "atlas_units": lambda p: fig_units(ds, av, p),
        "ari_history": lambda p: fig_ari_history(v, p),
        "ari_clock": lambda p: fig_ari_clock(v, p),
        "dominant_design": lambda p: fig_dominant_design(v, p),
        "class_configs": lambda p: fig_class_configs(v, p),
        "dimension_drift": lambda p: fig_dimension_drift(v, p),
        "transitions": lambda p: fig_transitions(v, p),
        "ip_strategy": lambda p: fig_ip_strategy(ds, v, p),
        "specialisation": lambda p: fig_specialisation(v, p),
        "industry_by_class": lambda p: fig_industry_by_class(v, p),
        "examination": lambda p: fig_examination(v, p),
    }
    with plt.rc_context(STYLE):
        for name, job in jobs.items():
            paths[name] = job(out / f"{name}.png")
    import json
    (out / "panels.json").write_text(json.dumps(PANELS, indent=1, ensure_ascii=False), encoding="utf-8")
    return paths
