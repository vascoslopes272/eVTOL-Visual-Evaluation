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

from . import a1, a2, atlas, figures, la_baseline, la_tables, metrics, numbers
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
#: black-and-white pattern for the :data:`ATLAS_EXTRA_CLASSES` colours that are not in ``CAT``, which
#: ``_bw_table`` would otherwise leave unpatterned. Their greys are chosen for the band order in the
#: stack — PTC .29, RC .47, HB .09, PFV .38, Other .72 — so every neighbouring pair differs by at
#: least .29 of grey, well clear of the steps the seven fixed classes already rely on hatches for.
#: HB carries no hatch on purpose: at grey .09 it is by far the darkest band in the figure, which
#: identifies it on its own, and a pattern on near-black prints as a smudge. PFV takes stars rather
#: than circles so it cannot be read as RC, the other mid-grey band ("oo").
EXTRA_CLASS_BW = {"#111827": ("", (0, (6, 2, 2, 2)), "*"),        # HB, near-black slate
                  "#7a5c3e": ("**", (0, (2, 2, 6, 2)), "p")}      # PFV, mid brown


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
    _BW.update({to_hex(c): v for c, v in EXTRA_CLASS_BW.items()})
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


# ----------------------------------------------- Appendix D taxonomy -------
def design_space_cards_svg(n: Dict, path: Path) -> Path:
    """The Preliminary Analysis Figure 3.3c without its bottom row: the four label cards of one
    unique aircraft. (That number is the PA's, not this document's — here the figure is 2.1a.)"""
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


# ------------------------------------------------------- 1.1 convergence ---
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
    return _save(fig, path, SRC + "; tables/la_firm_weighted_shares.csv.",
                 "Solid: each unique aircraft counts once. Dashed: a named firm votes once per window for the class it filed "
                 "most; an individual inventor's patent is its own filer. Where the two lines part, a few large filers "
                 "carry the class. * partial window.")


def fig_spans_by_firm(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    sp = a2.d9_aircraft_spans(ds)
    sp = sp.merge(v[["aircraft_id", "company_canonical", "named"]], on="aircraft_id", how="left")
    sizes = la_tables.firm_sizes(v)
    firms = list(sizes[sizes >= FIRM_MIN].index)
    group = lambda d: np.where(d["company_canonical"].isin(firms), d["company_canonical"],
                               np.where(d["named"], "other named firms", "individual inventors"))
    sp["firm"] = group(sp)
    order = firms + ["other named firms", "individual inventors"]
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
        labels.append(f)
        x = start + slot + 0.6
        ax.axvline(x - 0.8, color=GRID, lw=0.6)
    ax.set_xticks(ticks, labels, rotation=90, fontsize=7)
    ax.set_xlim(-1, x - 0.5)
    ax.set_ylabel("priority year")
    ax.set_title("Aircraft filed again over several years", fontsize=9)
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
    return _save(fig, path, SRC + "; aircraft observations O1/O2 (Table A.2a); firms with 5 or more unique aircraft.",
                 "(i) Each vertical line is one aircraft that was filed in more than one year: the line runs from its "
                 "first filing to its last and the dot is the record the labels were read from, so a long line is a "
                 "design a firm kept coming back to. Only the aircraft filed more than once are drawn, so an empty "
                 "column means the firm never re-filed. Colour is the architecture class. (ii) The same firms with "
                 "every one of their aircraft in the denominator — the fraction over each bar is aircraft re-filed "
                 "out of aircraft held. Read (ii) first: it is the panel that compares firms, and (i) only shows how "
                 "long the re-filing went on. Re-filing the same aircraft for years is the only commitment signal the "
                 "patents themselves carry.")
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
    """Lead and lag drawn as the two tables are read, not as twelve cumulative curves.

    Author's ruling 2026-09-23: "the tables are the best now because from the graphs I can't
    see it … I would like a better way for me to correlate … class and region". So panel (i)
    *is* Tables 1.1.8a/b — one row per group, the bar running from its 25 % year to its 75 %
    year with the median marked — with regions and classes on one shared year axis so they can
    be compared against each other, which two separate line charts could not do. Panel (ii) is
    the crossing the tables cannot show at all: the median year of each class inside each
    region, which is where a class-against-region reading actually lives.
    """
    _, qr = la_tables.lead_lag(v, "region3")
    _, qc = la_tables.lead_lag(v, "topType", top=7)
    med, n_cell = la_tables.class_region_timing(v)
    fig = plt.figure(figsize=(W, 3.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.62, 1], wspace=0.10)
    ax = fig.add_subplot(gs[0])
    rows = ([(r["region3"], int(r["aircraft"]), r["25 %"], r["50 %"], r["75 %"],
              REGION_COLOR.get(r["region3"], OTHER), REGION_STYLE.get(r["region3"], ("o", "-"))[0])
             for _, r in qr.sort_values("50 %").iterrows()]
            + [(None,) * 7]
            + [(r["topType"], int(r["aircraft"]), r["25 %"], r["50 %"], r["75 %"],
                _color(next((k for k, nm in metrics.ARCH_NAMES.items() if nm == r["topType"]), r["topType"])),
                _cs(next((k for k, nm in metrics.ARCH_NAMES.items() if nm == r["topType"]), "x"))[0])
               for _, r in qc.sort_values("50 %").iterrows()])
    labels = []
    for i, (name, n, q1, q2, q3, col, mk) in enumerate(rows):
        if name is None:
            labels.append("")
            continue
        ax.hlines(i, q1, q3, color=col, lw=5.5, alpha=0.55, zorder=2)
        ax.plot([q1, q3], [i, i], ls="none", marker="|", ms=7, mew=1.4, color=col, zorder=3)
        ax.plot(q2, i, marker=mk, ms=6.5, color=col, mec=SURFACE, mew=0.8, zorder=4)
        ax.text(q3 + 0.35, i, f"{q2}", fontsize=7.6, va="center", color=INK2)
        labels.append(f"{name} ({n})")
    ax.set_yticks(range(len(rows)), labels, fontsize=8)
    ax.invert_yaxis()
    lo_x = min(r[2] for r in rows if r[0] is not None)
    ax.set_xlim(lo_x - 1.2, la_tables.LAST_COMPLETE + 1.4)   # room for the median year beside each bar
    ax.set_xlabel("priority year (complete years, to 2023)")
    ax.set_title("Each group's own aircraft:\n25 % — median — 75 %", fontsize=9)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    for i, txt in ((0, "by region"), (len(qr) + 1, "by class, seven largest")):
        ax.text(0.0, i - 0.72, txt, transform=matplotlib.transforms.blended_transform_factory(
            ax.transAxes, ax.transData), fontsize=7.5, color=INK2, style="italic")
    ax2 = fig.add_subplot(gs[1])
    grand = v.dropna(subset=["year"])
    grand = grand[grand["year"].le(la_tables.LAST_COMPLETE) & grand["region3"].isin(REGIONS)]
    allrow = grand.groupby("region3")["year"].median().reindex(med.columns)
    mat = pd.concat([med, allrow.to_frame("all classes").T])
    lo, hi = float(np.nanmin(mat.to_numpy())), float(np.nanmax(mat.to_numpy()))
    ax2.imshow(mat.to_numpy(dtype=float), cmap=BLUE, vmin=lo - 0.8, vmax=hi + 0.3, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            if pd.isna(val):
                ax2.text(j, i, "–", ha="center", va="center", fontsize=7.5, color=MUTED)
                continue
            dark = (val - lo + 0.8) / (hi - lo + 1.1) > 0.55
            ax2.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8.2,
                     color="white" if dark else INK, fontweight="bold" if i == mat.shape[0] - 1 else "normal")
    ax2.set_xticks(range(mat.shape[1]), ["N. America", "Europe", "Asia-Pac."], fontsize=7.5,
                   rotation=30, ha="right")
    # codes, not names: panel (i) spells every one of them out two inches to the left, and the
    # full names here would push the figure past the 7.09 in text width
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == c), c) for c in mat.index]
    ax2.set_yticks(range(mat.shape[0]), codes, fontsize=7.5)
    ax2.yaxis.tick_right()          # labels on the outside, clear of panel (i)
    ax2.axhline(mat.shape[0] - 1.5, color=INK, lw=1)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.set_xticks(np.arange(-.5, mat.shape[1]), minor=True)
    ax2.set_yticks(np.arange(-.5, mat.shape[0]), minor=True)
    ax2.grid(which="minor", color=SURFACE, linewidth=1.4)
    ax2.tick_params(which="minor", length=0)
    ax2.set_title("Median year per class,\ninside each region", fontsize=9)
    fig.suptitle("Lead and lag: when each region, and each class, did its filing",
                 x=0.01, y=1.0, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; complete priority years only (≤ 2023), so 2024-26 is excluded "
                 "throughout; unit = unique aircraft, each group divided by its own total, never by the "
                 "corpus; a cell of the matrix with fewer than 5 aircraft is printed “–”; Tables 1.1.8a/b/c. "
                 "NOT normalised against B64 aviation patenting, and it does not need to be: every group is "
                 "divided by its own total, and the stored baseline (1.1.1) has one series for all offices, "
                 "so it would multiply every group by the same yearly factor and could not change which "
                 "group leads — a check with each aircraft weighted by 1 / B64 of its year moves all the "
                 "crossings about two years earlier and leaves the order of the regions unchanged.",
                 "Left: a bar runs from the year a group had a quarter of its aircraft to the year it had "
                 "three quarters, and the mark is its median year, printed beside it; further left = earlier. "
                 "Regions and classes share one axis, so a class can be held against a region. Right: the "
                 "same median year taken inside each region — read a row to see whether one region took a "
                 "class up before the others, and the bottom row for the region's own median over all "
                 "classes, which is what a row must be compared against.")


def _wilson_half(k: int, n: int, z: float = 1.96) -> float:
    """Half-width of the 95 % Wilson interval on a share k/n — how far a printed percentage
    could be from the truth on that many aircraft."""
    if not n:
        return float("nan")
    p = k / n
    d = 1 + z * z / n
    return float(z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d)


def fig_class_cycles(v: pd.DataFrame, path: Path) -> Path:
    """1.1.7 as ONE longitudinal bar, the percentage printed per window (author's ruling,
    2026-09-23: "I need this 4.1.6 to be conciser … just a single longitudinal bar figure …
    don't put the number, just put the percentage"). The twelve panels and the raw counts are
    gone. The right-hand column is new and answers the other half of the same ruling — whether
    a 20-aircraft class may be read at all — by printing the 95 % band that class's largest
    percentage actually carries."""
    t = la_tables.class_cycles(v).set_index("class")
    classes = t.index.tolist()
    shade = {w: BLUE(x) for w, x in zip(WINDOW_NAMES, np.linspace(0.08, 0.78, len(WINDOW_NAMES)))}
    fig, ax = plt.subplots(figsize=(W, 0.285 * len(classes) + 1.35))
    y = np.arange(len(classes))
    left = np.zeros(len(classes))
    placed = np.full(len(classes), -1.0)     # centre of the last percentage printed on that row
    for wn in WINDOW_NAMES:
        vals = t[wn].astype(float).to_numpy()
        c = shade[wn]
        ax.barh(y, vals, left=left, height=0.74, color=c, edgecolor=SURFACE, linewidth=1.2,
                label=WIN_SHORT.get(wn, wn), zorder=2)
        pale = sum(c[:3]) > 1.95
        for yi, (l, val) in enumerate(zip(left, vals)):
            mid = l + val / 2
            # a percentage is printed only where the block is wide enough for it and far enough
            # from the one before it: two 5 % blocks side by side would print on top of each other
            if val >= 0.04 and mid - placed[yi] >= 0.055:
                ax.text(mid, yi, f"{val:.0%}", ha="center", va="center", fontsize=7,
                        color=INK if pale else "white", fontweight="bold", zorder=4)
                placed[yi] = mid
        left = left + vals
    # the median window — the one in which the class passes half its own aircraft — is outlined
    for yi, cls in enumerate(classes):
        k = WINDOW_NAMES.index(t.loc[cls, "median window"])
        x0 = float(t.loc[cls, WINDOW_NAMES[:k]].astype(float).sum())
        ax.add_patch(matplotlib.patches.Rectangle((x0, yi - 0.37), float(t.loc[cls, WINDOW_NAMES[k]]),
                                                  0.74, fill=False, edgecolor=INK, linewidth=1.4, zorder=5))
    # how wide the band on that class's biggest percentage is, printed as its own column
    ax.text(1.035, -0.95, "95 % band on\nthe largest bar", fontsize=7, color=INK2, va="bottom", ha="left")
    for yi, cls in enumerate(classes):
        n = int(t.loc[cls, "aircraft"])
        share = float(t.loc[cls, WINDOW_NAMES].astype(float).max())
        h = _wilson_half(int(round(share * n)), n)
        ax.text(1.035, yi, f"± {h * 100:.0f} pts", fontsize=7.5, va="center", ha="left",
                color=INK if h < 0.12 else INK2)
    ax.set_yticks(y, [f"{c} ({int(t.loc[c, 'aircraft'])})" for c in classes], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.30)
    ax.set_xticks(np.arange(0, 1.01, 0.25))
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("share of that class's own aircraft")
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.10), ncol=5, fontsize=8,
              title="priority window (24–26 partial)", title_fontsize=8, handlelength=1.5,
              columnspacing=1.2, handletextpad=0.5)
    fig.suptitle("Where in time each class lives: its aircraft per window, as a percentage of its own total",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; unit = unique aircraft; every bar is one class divided by its own "
                 "total, so the bars compare timing and never size; counts per class in tables/la_class_cycles.csv.",
                 "One bar per class, left to right in time; the percentage in a block is that share of the class's "
                 "own aircraft, and the five blocks of a bar add to 100 %. The outlined block is the window in "
                 "which the class passes half its aircraft. A bar whose weight sits left has faded, one whose "
                 "weight sits right is still growing. The last column is the 95 % band on that class's biggest "
                 "percentage: a class of 20 carries ± 17 points or more, so the bottom five rows say which window "
                 "a class lived in and nothing finer. Classes largest first.")


#: ⁰D / ¹D / ²D written the way the question is asked, not the way the ecology literature writes it
HILL_NAMES = [(0, CAT[0], "how many kinds exist", "-", "o"),
              (1, CAT[1], "how many are commonly used", "--", "s"),
              (2, CAT[2], "how many are the usual choice", ":", "^")]


def fig_hill(v: pd.DataFrame, path: Path) -> Path:
    """1.1.9 made self-explaining (author, 2026-09-23: "I don't really know the meaning of D1,
    D2, and how I take takeaways from these graphs"). Three changes and nothing else: the three
    quantities are named by the question each answers instead of by its symbol, the grey band
    is named on the figure, and the takeaway is stated on the figure rather than left to the
    reader — which here is a null, and the honest statement of it is that nothing in this
    figure separates.

    The build recommends cutting the section (see :func:`la_tables.flags`): none of the 60
    pairs of windows separate at 95 %, and the one signal this statistic does carry in this
    corpus is already tested against a null in 4.1.3.3. The figure is left working so the
    author can decide with it in front of him.
    """
    t = la_tables.hill_by_window(v)
    levels = t["level"].unique()
    fig, axes = plt.subplots(1, len(levels), figsize=(W, 3.2), sharex=True)
    x = np.arange(len(WINDOW_NAMES))
    sep = 0
    for ax, lvl in zip(np.atleast_1d(axes), levels):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        for q, col, lab, ls_, mk_ in HILL_NAMES:
            ax.errorbar(x, sub[f"D{q}"], yerr=[sub[f"D{q}"] - sub[f"D{q} low"], sub[f"D{q} high"] - sub[f"D{q}"]],
                        marker=mk_, ls=ls_, ms=4, lw=1.8, capsize=2, color=col, label=lab)
            lo, hi = sub[f"D{q} low"], sub[f"D{q} high"]
            sep += sum(1 for i, a in enumerate(WINDOW_NAMES) for b in WINDOW_NAMES[i + 1:]
                       if pd.notna(lo.get(a)) and pd.notna(lo.get(b))
                       and (hi[a] < lo[b] or hi[b] < lo[a]))
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES, sub["aircraft"]), fontsize=7.5)
        ax.set_title("A0: the architecture class\n(one kind = one class)" if lvl.startswith("A0 ")
                     else "A0c: class × propulsive units\n(one kind = a class at one unit count)", fontsize=9)
        ax.set_ylim(0)
        _hgrid(ax, "y")
    h, l = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3)
    fig.subplots_adjust(bottom=0.24)
    np.atleast_1d(axes)[0].set_ylabel("number of kinds in 40 aircraft")
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    fig.suptitle("How many kinds of aircraft a window holds, every window cut to the same 40 aircraft",
                 x=0.01, y=1.06, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; unit = unique aircraft; Table 1.1.9; A0 = the architecture class "
                 "alone, A0c = the class together with the number of propulsive units. Each point is the "
                 "mean of 1 000 random draws of 40 aircraft from that window, and the vertical whisker "
                 "through it is the 95 % band of those draws — how much the point would move if a "
                 "different 40 aircraft had been drawn. Cutting every window to the same 40 is what stops "
                 "a window counting as varied merely because it holds more patents. The grey hatched "
                 "column is the partial window 2024-26.",
                 "Three counts of the same thing, from the broadest to the strictest. Top line: how many "
                 "different kinds appear at all. Middle: how many are common enough to matter. Bottom: "
                 "how many are the usual choice, which is the one a dominant design would pull towards 1. "
                 "Lines apart and flat = many kinds exist but few are usual. TAKEAWAY: every whisker "
                 f"overlaps every other one — {sep} of the 60 pairs of windows separate — so at equal "
                 "sample size the corpus holds about as many kinds of aircraft in 2020-23 as it did "
                 "before 2011. Filings per year rose by an order of magnitude over the same span "
                 "(Figure 1.1.1): the field grew hard and did not widen. Whether the early windows were already narrower "
                 "than chance is a different question, and 1.1.3.3 answers it against a null.")


def _short_firm(name: str, n: int = 16) -> str:
    """A filer's name short enough for a figure cell, without inventing an abbreviation."""
    s = str(name)
    if s.startswith("patent:") or s == "one patent" or "(one patent)" in s:
        return "one patent"
    for cut in (" / ", " Aviation", " Aerospace", " Aircraft", " Technologies", " Helicopter"):
        if len(s) > n and cut in s:
            s = s.split(cut)[0]
    return s if len(s) <= n else s[:n - 1] + "…"


def fig_filer_weight(v: pd.DataFrame, path: Path) -> Path:
    """How much of a class is one filer repeating itself — the author's question of 2026-09-23:
    "if you see a filer with sixty-four patents, and twenty-four of those are CVT … how do I
    know the weight that that filer is contributing with CVT? THIS IS VERY IMPORTANT TO ANSWER".

    Nothing else in the document answers it. Table 1.1.6a counts *distinct filers* per archetype,
    which says how many there are and not how unevenly they divide it, and the one-vote-per-filer
    check of 1.1.2 was cut on 2026-09-22. So this figure carries the answer in two readings: how
    much of a whole class its three biggest filers hold, and how much of one class in one window
    its single biggest filer holds — which is what "the bar on CVT is increasing because the same
    company keeps filing" would have to look like if it were true.
    """
    t = la_tables.class_filer_weight(v)
    cw = la_tables.class_window_filer_weight(v)
    fig = plt.figure(figsize=(W, 6.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.92], hspace=0.60)

    # ---- (i) the three biggest filers of each class
    ax = fig.add_subplot(gs[0])
    y = np.arange(len(t))
    tint = [BLUE(0.72), BLUE(0.45), BLUE(0.22)]
    left = np.zeros(len(t))
    w = v.dropna(subset=["topType"])
    ranks = {c: (sub["filer_id"].value_counts() / len(sub)).head(3).tolist()
             for c, sub in w.groupby("topType")}
    for k in range(3):
        vals = np.array([(ranks[c][k] if len(ranks[c]) > k else 0.0) for c in t["code"]])
        ax.barh(y, vals, left=left, height=0.70, color=tint[k], edgecolor=SURFACE, linewidth=1.1,
                label=["largest filer", "2nd", "3rd"][k], zorder=2)
        left = left + vals
    for yi, (_, r) in zip(y, t.iterrows()):
        ax.text(left[yi] + 0.012, yi, f"{_short_firm(r['largest filer'])}  {r['its share']:.0%}",
                fontsize=7.5, va="center", ha="left", color=INK)
    ax.set_yticks(y, [f"{r['class']} ({r['aircraft']})" for _, r in t.iterrows()], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("share of the class's own aircraft")
    ax.set_title("The three largest filers of each class, and who the largest is", fontsize=9)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    ax.legend(loc="upper right", fontsize=7.5, ncol=1, handlelength=1.3, labelspacing=0.35)

    # ---- (ii) the same question inside one window
    ax2 = fig.add_subplot(gs[1])
    order = [c for c in t["code"] if c in set(cw["code"])]
    mat = cw.pivot_table(index="code", columns="window", values="its share").reindex(
        index=order, columns=WINDOW_NAMES)
    who = cw.pivot_table(index="code", columns="window", values="largest filer", aggfunc="first").reindex(
        index=order, columns=WINDOW_NAMES)
    ax2.imshow(mat.to_numpy(dtype=float), cmap=BLUE, vmin=0, vmax=0.45, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]
            if pd.isna(val):
                continue
            ax2.text(j, i, f"{_short_firm(who.iat[i, j], 11)}\n{val:.0%}", ha="center", va="center",
                     fontsize=7, color="white" if val > 0.25 else INK)
    ax2.set_xticks(range(len(WINDOW_NAMES)), _win_labels(WINDOW_NAMES), fontsize=7.5)
    ax2.set_yticks(range(mat.shape[0]), [f"{c} ({int(t.set_index('code').loc[c, 'aircraft'])})" for c in mat.index],
                   fontsize=7.5)
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.set_xticks(np.arange(-.5, len(WINDOW_NAMES)), minor=True)
    ax2.set_yticks(np.arange(-.5, mat.shape[0]), minor=True)
    ax2.grid(which="minor", color=SURFACE, linewidth=1.5)
    ax2.tick_params(which="minor", length=0)
    ax2.set_title("Inside one window: the biggest single filer of that class, and its share "
                  "(blank = under 10 aircraft)", fontsize=9)
    fig.suptitle("How much of a class is one filer repeating itself", x=0.01, ha="left",
                 fontsize=10, fontweight="bold")
    big = t[t["aircraft"] >= 20]         # the classes big enough for a share to be read at all
    return _save(fig, path, SRC + "; unit = unique aircraft, so a firm that filed four patents on one "
                 "aircraft counts once and only a firm with several different aircraft moves these "
                 "numbers; a filer is an organisation, and an individual inventor's patent is its own "
                 "filer, so no two lone inventors are merged; Table 1.1.6b, and per window "
                 "tables/la_class_window_filer_weight.csv.",
                 "Top: each class divided among its three biggest filers, the biggest named on the bar; "
                 "the rest of the bar is everyone else. Bottom: the same for one class in one window, "
                 "which is where a firm's weight actually shows — a class can be evenly held over 25 "
                 f"years and still be one firm's work in one window. TAKEAWAY: no class is one company. "
                 f"Across the {len(big)} classes with 20 or more aircraft the largest single filer holds "
                 f"at most {big['its share'].max():.0%} of its class "
                 f"({_short_firm(big.loc[big['its share'].idxmax(), 'largest filer'])}, "
                 f"{big.loc[big['its share'].idxmax(), 'class']}), and the top three of the four "
                 "big classes hold between 15 and 25 %. The one place a firm does carry a bar is inside a "
                 f"window: Bell / Textron holds {cw.set_index(['code', 'window']).loc[('TR', '2016-19'), 'its share']:.0%} "
                 f"of Tilt Rotor in 2016-19 and {cw.set_index(['code', 'window']).loc[('CVT', '2020-23'), 'its share']:.0%} "
                 "of Combined vectored thrust in 2020-23 — real, but a fifth of the bar, not the bar. "
                 "Table 1.1.6b counts the same thing a third way: give every filer one vote instead of "
                 "counting aircraft and no class changes rank.")


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
    return _save(fig, path, SRC + "; A0c archetypes (class × propulsive-unit bin) with 5 or more aircraft; Table 1.1.6a.",
                 "Top: an archetype far right holds a big share of recent aircraft; high up it is filed by many different "
                 "filers per aircraft (open field), low down by few filers holding many aircraft (crowded by a few). Bubble "
                 "size = aircraft. Bottom: the same archetypes over the windows, count in the cell.")
#: what each PatSeer legal status means, spelled out under Figure 1.1.10 (author, 2026-09-23:
#: "how do you know that the patents are no longer in force? This needs to be stated on the source")
LEGAL_STATUS_MEANING = [
    ("ACTIVE - GRANTED", "granted and in force at the snapshot"),
    ("ACTIVE - APPLIED", "still pending, neither granted nor refused"),
    ("INACTIVE - WITHDRAWN / SURRENDERED", "the applicant withdrew the application, or gave the patent up"),
    ("INACTIVE - NONPAYMENT", "lapsed because a renewal fee was not paid"),
    ("INACTIVE - EXPIRED", "the office records the right as expired"),
    ("INACTIVE - REJECTED / REFUSED / SUSPENDED", "the office refused it"),
]


def fig_abandonment(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
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
    snap = ds.identity["snapshot_date"].dropna()
    snap = str(snap.iloc[0])[:10] if len(snap) else "the snapshot"
    cohort = v.dropna(subset=["topType"]).drop_duplicates("patent_id")
    cov = (cohort[cohort["year"].le(2019)].groupby("topType").size()
           / cohort.groupby("topType").size()).dropna()
    inact = (v.drop_duplicates("patent_id")["legal_status_raw"].fillna("").astype(str)
             .str.startswith("INACTIVE").sum())
    return _save(fig, path,
                 SRC + "; unit = the primary patent of a unique aircraft, one row per patent, not per "
                 f"aircraft ({len(cohort)} primary patents carry a class, {len(cohort[cohort['year'].le(2019)])} "
                 "of them with priority 2019 or earlier and drawn here). HOW A PATENT IS KNOWN TO BE OUT "
                 "OF FORCE: the `legal_status_raw` field PatSeer returns for that patent in the corpus "
                 f"export, read as it stood at the PatSeer snapshot of {snap} — a stored field, not a "
                 "live lookup, so re-running this document does not move it. PatSeer writes one of six "
                 "values: " + "; ".join(f"{k} = {mean}" for k, mean in LEGAL_STATUS_MEANING) + ". A patent "
                 f"counts as no longer in force here when that value begins INACTIVE — {inact} of the "
                 f"{v['patent_id'].nunique()} primary patents of the analysis set, and "
                 f"{int(allrow['lapsed'])} of the {int(allrow['patents'])} of the cohort behind it. "
                 "INACTIVE pools the applicant's own decisions "
                 "(withdrawn, surrendered, unpaid renewal) with the office's (refused) and with expiry; "
                 "the split per status, over every priority year, is in tables/la_examination_class.csv. "
                 "EXPIRED is the office's own "
                 "word and is not always the end of a 20-year term: it appears on filings too recent for "
                 "that, so it is read as “the register no longer carries the right”, nothing more. "
                 "Table 1.1.10.",
                 "Share of each class's primary patents that are no longer in force, among patents filed "
                 "early enough (priority ≤ 2019) to have been granted and then kept or dropped; the label "
                 "on each bar is the raw count. A high share is money withdrawn from that class. The "
                 "denominator is deliberately that class's own patents of the same cohort, and NOT the "
                 "class's aircraft over all years: dividing by every aircraft would mostly measure how "
                 "young a class is, and Lift + Cruise — the youngest, with only "
                 f"{cov.get('SLC', float('nan')):.0%} of its patents in this cohort against "
                 f"{cov.get('TR', float('nan')):.0%} for Tilt Rotor — would then look the most durable "
                 "class for no other reason. What the cohort share does change is coverage, so read each "
                 "bar as a statement about that fraction of the class and not about all of it.")


# ------------------------------------------------------- 1.2 provenance ----
#: A percentage of a handful of aircraft is not a trend. Every cell of Figure 1.3.2a/b that holds
#: fewer than this many aircraft is blanked in the mix panels (``la_tables.region_window_shares``)
#: and drawn hollow, with its share greyed, in the share-of-window row (author, 2026-09-23:
#: "as this is in percentage, I can misstalk about some things").
GRID_THIN = 10

#: Where the four filer types come from, printed wherever the document draws them. The author asked
#: the question outright on 2026-09-23 ("WHERE DID YOU GET THAT FROM?"), so the rule is written out
#: and the audit of it is printed with it rather than being left in a commit message.
#: Rule, since 2026-09-23: the filer type is read off the RAW PatSeer assignee string
#: (:func:`la_tables.filer_from_assignee`) — first assignee, country code stripped; a university,
#: institute, academy or national research agency by :data:`la_tables.ASSIGNEE_INSTITUTE_RE`;
#: otherwise an organisation if the string carries a legal form of any office in the corpus in its
#: last two tokens (US, CN, DE, JP, KR, FR, GB, IT, RU, IL, ES, CA and the rest — ``co``, ``spa``,
#: ``kk``, ``sl``, ``as``, ``lp``, ``ooo`` …), an activity word anywhere, a digit, more than five
#: name words, or a non-Latin legal form; otherwise an individual inventor.
#: What it replaced: the type used to be read off ``company_canonical``
#: (``Patent-Labelling-Tools/src/grouper.py::_normalise_company``, stored in
#: ``0_labelling/inputs/reference/family_map.csv``), which matches the assignee against a
#: hand-written table of ~110 companies and drops everything else into "Individual Inventor" or
#: "Unknown / Independent". The type therefore measured the table's coverage: of the 138 aircraft
#: the document drew as "unattributed / independent", 118 were companies, 16 universities or
#: institutes, 2 individuals and 0 anonymous; twelve organisations went the other way and were
#: drawn as individual inventors because their legal form was missing from the keyword list.
#: Audit, 2026-09-23, against a hand reading of all 393 distinct assignee strings of the 665
#: aircraft (663 readable, 2 undeterminable): the old rule got person against organisation right
#: 643/663 = 97 % and the three-way split 509/663 = 77 %; this rule agrees with the reading on
#: every readable aircraft (663/663). ``company_canonical`` itself is untouched — it stays the
#: firm-identity field and still decides which firm a row belongs to wherever it resolved one.
FILER_RULE = ("filer type from the raw PatSeer assignee string (la_tables.filer_from_assignee: "
              "first assignee, country code stripped; institute, academy or national research "
              "agency by regex; otherwise an organisation if it carries a legal form of any office "
              "in the corpus, an activity word, a digit or more than five name words; otherwise an "
              "individual inventor). It replaced the company_canonical rule of grouper.py on "
              "2026-09-23, which made the type depend on whether the assignee had made it onto a "
              "hand-written list of ~110 companies: audited against a reading of all 393 assignee "
              "strings, that rule was right 97 % on person against organisation and 77 % on the "
              "three-way split, and its 'unattributed / independent' band held no unattributed "
              "patent at all. This rule agrees with the reading on all 663 readable aircraft. The "
              "fourth band, 'no assignee named', is empty: every aircraft in the analysis set names "
              "an assignee on its patent")


def _b64_by_window(ds: Optional[Dataset]) -> Optional[pd.Series]:
    """Corpus patents per 1 000 B64 patents of the same priority window, or ``None``.

    The one normalisation that answers "is this just the general rise in patenting?" at the level
    of the whole corpus. It is corpus-wide: the stored baseline
    (``assets/external/aviation_baseline``) has no regional split, so it cannot be taken per region
    and the region grids are **not** normalised — see the Source line each of them prints.
    """
    if ds is None or not la_baseline.available():
        return None
    try:
        b = la_baseline.series()
        pat = ds.patents.merge(ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left")
        win = pd.to_numeric(pat["priority_year"], errors="coerce").map(a2.window_of)
        # the truncated window is dropped: both sides of the ratio are still filling up there, so a
        # number read off it says more about publication lag than about filing
        names = [w for w in WINDOW_NAMES if "partial" not in w]
        per_win = pat.groupby(win).size().reindex(names)
        base = b.groupby(pd.Series(b.index, index=b.index).map(a2.window_of)).sum().reindex(names)
        return (per_win / base * 1000).round(1)
    except Exception:                       # a missing baseline costs a sentence, never the figure
        return None


def fig_region_grid(v: pd.DataFrame, path: Path, variables: Optional[List[str]] = None,
                    ds: Optional[Dataset] = None) -> Path:
    variables = variables or list(la_tables.GRID_VARIABLES)
    # one extra row under the variables: how much of the window each region holds, so the reading is
    # "did this region grow or shrink", not only "did its internal mix change" (author, 2026-09-23)
    fig, axes = plt.subplots(len(variables) + 1, len(REGIONS),
                             figsize=(W, 2.45 * len(variables) + 2.0),
                             gridspec_kw={"height_ratios": [1] * len(variables) + [0.62]})
    x = np.arange(len(WINDOW_NAMES))
    palettes = {
        "class": lambda cols: {c: _color(c) for c in cols},
        "propulsive units": lambda cols: dict(zip(cols, [BLUE(t) for t in np.linspace(0.25, 0.95, len(cols))])),
        "tilting unit": lambda cols: {True: CAT[1], False: CAT[0], "blank": OTHER},
        "ducted unit": lambda cols: {True: CAT[6], False: CAT[2], "blank": OTHER},
        "powertrain": lambda cols: {"Yes": CAT[2], "Hybrid": CAT[3], "Unknown": OTHER, "No": CAT[7]},
        "filer type": lambda cols: {"Named company": CAT[0], "University / institute": CAT[6],
                                    "Individual inventor": CAT[3], la_tables.NO_ASSIGNEE: OTHER},
    }
    # The fourth filer type was drawn "assignee not in the list" while the type was read off
    # company_canonical, because that is all the band measured. Since 2026-09-23 the type is read
    # off the raw assignee string, so the band means what it says — and it is empty: every aircraft
    # of the analysis set names an assignee on its patent. See FILER_RULE.
    names = {True: "yes", False: "no", "blank": "not determinable", "Yes": "electric", "Hybrid": "hybrid",
             "Unknown": "not stated", "No": "non-electric",
             la_tables.NO_ASSIGNEE: "no assignee named"}
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
            ax.tick_params(axis="x", labelbottom=False)     # the share row at the bottom carries them
            if j == 1:
                ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12),
                          ncol=5 if len(pal) > 4 else len(pal),
                          handlelength=1.2, columnspacing=1.0)

    # ---- bottom row: how much of the window each region holds ---------------
    # The mix panels above are shares *inside* a region-window cell, so they answer "what changed
    # inside this region" and cannot answer "did this region grow". This row answers that: the
    # region's aircraft divided by every aircraft of the same window, all regions included.
    w_ = v.dropna(subset=["window"])
    win_total = w_.groupby("window").size().reindex(WINDOW_NAMES).fillna(0)
    reg_n = (w_.groupby(["region3", "window"]).size().unstack()
             .reindex(index=REGIONS, columns=WINDOW_NAMES).fillna(0))
    reg_share = reg_n.div(win_total.replace(0, np.nan), axis=1)
    overall = (reg_n.sum(axis=1) / max(float(win_total.sum()), 1.0))
    for j, reg in enumerate(REGIONS):
        ax = axes[len(variables), j]
        vals = reg_share.loc[reg].to_numpy(dtype=float)
        cnt = reg_n.loc[reg].to_numpy(dtype=float)
        col = REGION_COLOR.get(reg, INK)
        for xi, (val, c_) in enumerate(zip(vals, cnt)):
            # a thin cell is drawn hollow and its share is labelled with its own n, so a percentage
            # of six aircraft cannot be read as a trend. No hatch: the black-and-white pass writes
            # one on the solid bars, and a second pattern here would read as a category.
            thin = c_ < GRID_THIN
            ax.bar(xi, 0 if not np.isfinite(val) else val, width=0.74,
                   color="none" if thin else col, edgecolor=col, lw=1.0)
            if np.isfinite(val):
                ax.text(xi, val + 0.02, f"{val:.0%}" + (f"\nof {int(c_)}" if thin else ""),
                        ha="center", va="bottom", fontsize=7, linespacing=0.95,
                        color=INK2 if thin else INK)
        ax.axhline(float(overall.get(reg, np.nan)), color=INK2, lw=0.8, ls=(0, (4, 2)))
        ax.set_ylim(0, max(0.75, float(np.nanmax(reg_share.to_numpy())) + 0.18))
        ax.set_yticks([])
        ax.spines[["left", "right", "top"]].set_visible(False)
        ax.set_xticks(x, [f"{WIN_SHORT[w]} ({int(reg_n.loc[reg, w])})" for w in WINDOW_NAMES],
                      fontsize=7, rotation=90)
        if j == 0:
            ax.set_ylabel("share of\nthe window", fontsize=8.5)
        ax.set_title(f"{reg}: {overall.get(reg, np.nan):.0%} overall", fontsize=8,
                     color=REGION_COLOR.get(reg, INK))

    fig.suptitle(f"{', '.join(variables).capitalize()} per region and window: share of the region-window cell "
                 "(cell count under the axis); bottom row, the region's share of the whole window",
                 x=0.01, ha="left", fontsize=9.5, fontweight="bold")
    fig.subplots_adjust(hspace=0.95, wspace=0.08)
    ratio = _b64_by_window(ds)
    norm = ("Not normalised against the general rise in patenting: the stored aviation baseline has no "
            "regional split. The mix panels are shares inside one cell, so the rise cancels there; the "
            "bottom row is a share of this corpus, so it says a region grew *relative to the others*, "
            "not in absolute terms. ")
    if ratio is not None and ratio.notna().any():
        got = ratio.dropna()
        norm += (f"The corpus as a whole went from {got.iloc[0]:.1f} patents per 1 000 B64 patents in "
                 f"{WIN_SHORT.get(got.index[0], got.index[0])} to {got.iloc[-1]:.1f} in "
                 f"{WIN_SHORT.get(got.index[-1], got.index[-1])}, the last complete window, so a part "
                 f"of every raw rise here is the general one and a part is not (Figure 1.1.1). ")
    return _save(fig, path,
                 SRC + "; region = applicant region (identity), not publication office; " + norm
                 + f"Cells under {GRID_THIN} aircraft are blanked in the mix panels and drawn hollow in the "
                   "bottom row; the count behind every bar is printed under it."
                 + (" " + FILER_RULE[0].upper() + FILER_RULE[1:] + "." if "filer type" in variables else ""),
                 "Each bar of the upper rows is 100 % of the aircraft of one region in one window — read down "
                 "a column for how a region's mix changed, across a row for how regions differ at the same "
                 "time. The bottom row is the other question: the region's aircraft as a share of every "
                 "aircraft of that window, against the dashed line of its share of the whole corpus. Above "
                 "the line the region held more of that window than it holds overall. A hollow bar rests on "
                 f"fewer than {GRID_THIN} aircraft and is not a trend. * partial window.")


def fig_country_class(v: pd.DataFrame, path: Path) -> Path:
    shares, n = la_tables.country_class(v, top=8)
    mat = shares.copy()
    mat.index = [f"{c} (n {int(n[c])})" for c in mat.index]
    fig, ax = plt.subplots(figsize=(W, 3.4))
    _heat(ax, mat, fmt="{:.0%}", vmax=0.5)
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=0)
    ax.set_title("Class share per applicant country, eight largest countries (codes as Figure D.1a)")
    return _save(fig, path, SRC + "; assignee_country of the primary patent's identity record.",
                 "Rows sum to 100 %. Read across a row for a country's mix; down a column for where a class is filed. "
                 "Capped at 50 % so that the middle of the range keeps contrast.")


# ------------------------------------------------------- 1.3 assignees -----
def fig_coverage(v: pd.DataFrame, path: Path) -> Path:
    """Coverage, with the counts on the curve, and the market-standing reading beside it.

    Author's ruling 2026-09-23: the curve must carry the numbers (so many firms, so many
    aircraft, between the marked thresholds) so the tier table can go; and the correlation with
    the AAM Reality Index must be shown, not left to be inferred from a few marked dots.
    """
    sizes = la_tables.firm_sizes(v)
    listed = la_tables.ari_listed(v)
    seg = la_tables.coverage_segments(v)
    total = len(v)
    cum = sizes.cumsum() / total
    rank = np.arange(1, len(sizes) + 1)
    fig = plt.figure(figsize=(W, 6.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.28, 1], hspace=0.62, wspace=0.34,
                          left=0.115, right=0.995, top=0.94, bottom=0.10)
    ax = fig.add_subplot(gs[0, :])
    ax.step(rank, cum, where="post", color=BLUE(0.8), lw=2, zorder=3)
    # the segments between the thresholds, annotated with the firms and the aircraft they hold.
    # Legibility pass 2026-09-23: a box is about 42 firms wide at this scale, so the two narrow
    # segments (the first ~17 firms) cannot hold theirs — those stack in the empty top-left corner
    # with a leader down to the segment, and the wide segments carry their box under the curve,
    # between their own dividers, where nothing else is drawn (no leader needed).
    edges = [0] + seg["cumulative firms"].tolist()
    n_narrow = 0
    for i, (_, r) in enumerate(seg.iterrows()):
        x0, x1 = edges[i], edges[i + 1]
        if i:
            ax.axvline(x0, color=GRID, lw=1, zorder=1)
        yb = 0.055                            # the span bar sits under the curve, which never rises past 0.47
        ax.annotate("", xy=(x0 + 0.2, yb), xytext=(x1 - 0.2, yb),
                    arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7, shrinkA=0, shrinkB=0))
        mid = (x0 + x1) / 2
        txt = f"{int(r['firms'])} firms · {int(r['aircraft'])} aircraft\n({r['aircraft per firm']} aircraft each)"
        y_mid = float(cum.iloc[min(int(round(mid)), len(cum)) - 1])
        if x1 - x0 < 45:
            # narrow segment: box in the top-left corner (one row per narrow segment), leader from
            # the box down to a point just above the curve at the segment's middle; the leader
            # starts under the box (the box is drawn on top) and stays left of the box below it
            ylab = 0.99 - 0.13 * n_narrow
            xlab = 6.0
            ax.plot([xlab + 0.5 + 6.0 * n_narrow, mid], [ylab, y_mid + 0.06], color=INK2, lw=0.6, zorder=1)
            ax.text(xlab, ylab, txt, ha="left", va="top", fontsize=7, color=INK, linespacing=1.2,
                    bbox=dict(fc="white", ec=GRID, lw=0.4, pad=0.3, alpha=0.96), zorder=4)
            n_narrow += 1
        else:
            # wide segment: box under the curve, inside the segment; the curve's lowest point in the
            # segment is at its left divider, so the box top sits below that
            ax.text(mid, float(cum.iloc[x0 - 1]) - 0.06, txt, ha="center", va="top", fontsize=7, color=INK,
                    linespacing=1.2, bbox=dict(fc="white", ec=GRID, lw=0.4, pad=0.3, alpha=0.96), zorder=4)
        y1 = float(cum.iloc[x1 - 1])
        if i == 0:
            # the first threshold is too close to the y axis for a right-aligned label (it would spill
            # over the tick labels) and the rated dots crowd the curve just right of it: below-right
            ax.text(x1 + 0.6, y1 - 0.02, f"{y1:.0%}", ha="left", va="top",
                    fontsize=7, color=BLUE(0.95), fontweight="bold", zorder=5)
        else:
            ax.text(x1, y1 + 0.012, f"{y1:.0%}", ha="right", va="bottom",
                    fontsize=7, color=BLUE(0.95), fontweight="bold", zorder=5)
    named_share = sizes.sum() / total
    ax.axhline(named_share, color=INK, lw=1, ls="--")
    ax.text(len(sizes), named_share + 0.012, f"all {len(sizes)} named companies: {int(sizes.sum())} aircraft, "
            f"{named_share:.0%} ", ha="right", va="bottom", fontsize=7.5,
            bbox=dict(fc="white", ec="none", pad=0.3))
    ax.axhline(1, color=GRID, lw=0.8)
    ax.text(len(sizes), 1.0, f"whole analysis set, {total} aircraft (individual inventors are the rest) ",
            ha="right", va="bottom", fontsize=7.5, color=INK2)
    pts = [(i + 1, float(cum.iloc[i])) for i, f in enumerate(sizes.index) if f in listed]
    ax.plot([p_[0] for p_ in pts], [p_[1] for p_ in pts], ls="", marker="o", ms=5, color=CAT[1], zorder=6,
            label=f"rated by the AAM Reality Index ({len(pts)} firms, ranks "
                  f"{min(p_[0] for p_ in pts)}–{max(p_[0] for p_ in pts)})")
    ax.set_xlim(0, len(sizes) + 1)
    ax.set_ylim(0, 1.06)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("named companies ranked by unique aircraft (largest first); they are named in Figure 1.2.3a")
    ax.set_ylabel("cumulative share of the analysis set")
    ax.set_title("How much of the analysis set the top N firms cover", fontsize=9)
    ax.legend(fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.11), framealpha=0.92)
    _hgrid(ax, "both")

    # (ii) do the rated firms hold more, file earlier, file broader?
    f = la_tables.firm_frame(v)
    ax2 = fig.add_subplot(gs[1, 0])
    mvp = la_tables.market_vs_patents(v).set_index("reading")
    rows = [("unique aircraft", "aircraft", "unique aircraft per firm, median"),
            ("patents", "patents", "representative patents per firm, median"),
            ("distinct classes", "classes", "distinct classes per firm, median"),
            ("years first to last", "years\nfirst→last", "years from first to last filing, median")]
    y = np.arange(len(rows))
    for j, (col, lab, key) in enumerate(rows):
        a = f.loc[f["on the AAM index"], col].dropna()
        b = f.loc[~f["on the AAM index"], col].dropna()
        ax2.barh(y[j] - 0.19, a.median(), height=0.36, color=CAT[1], zorder=3)
        ax2.barh(y[j] + 0.19, b.median(), height=0.36, color=BLUE(0.45), hatch="///", edgecolor=SURFACE, lw=0.6, zorder=3)
        ax2.text(a.median(), y[j] - 0.19, f" {a.median():g}", va="center", fontsize=7, color=INK)
        ax2.text(b.median(), y[j] + 0.19, f" {b.median():g}", va="center", fontsize=7, color=INK)
        p = mvp["p"].get(key, np.nan)
        if pd.notna(p):
            ax2.text(0.99, y[j], ("p " + (f"{p:.3f}" if p >= 0.001 else "< 0.001")), transform=ax2.get_yaxis_transform(),
                     ha="right", va="center", fontsize=6.5, color=INK2 if p < 0.05 else MUTED)
    ax2.set_yticks(y, [r[1] for r in rows], fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_xlabel("median per firm")
    ax2.set_xlim(0, max(f["patents"].median(), 4) * 2.1)
    ax2.set_title("Rated by the market, against not rated", fontsize=8.6)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    n_l, n_r = int(f["on the AAM index"].sum()), int((~f["on the AAM index"]).sum())
    a_l = int(f.loc[f["on the AAM index"], "unique aircraft"].sum())
    a_r = int(f.loc[~f["on the AAM index"], "unique aircraft"].sum())
    ax2.legend(handles=[matplotlib.patches.Patch(fc=CAT[1], label=f"on the AAM Reality Index — {n_l} firms, {a_l} aircraft"),
                        matplotlib.patches.Patch(fc=BLUE(0.45), hatch="///", ec=SURFACE,
                                                 label=f"the other named firms — {n_r} firms, {a_r} aircraft")],
               fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.34), ncol=1, framealpha=0.9)

    # (iii) and does the POSITION on the index track the patenting?
    ax3 = fig.add_subplot(gs[1, 1])
    a = la_tables.ari_firms(v)
    a = a[pd.to_numeric(a["ARI score"], errors="coerce").notna()]
    xs = pd.to_numeric(a["ARI score"], errors="coerce").tolist()
    ys = pd.to_numeric(a["unique aircraft"], errors="coerce").tolist()
    ax3.scatter(xs, ys, s=34, color=CAT[1], edgecolor=SURFACE, lw=0.7, zorder=3)
    rho = mvp["AAM index firms"].get("within the index — index score against unique aircraft", "")
    pv = mvp["test"].get("within the index — index score against unique aircraft", "")
    ax3.set_yscale("log")
    ax3.set_yticks([1, 2, 5, 10, 25, 60], ["1", "2", "5", "10", "25", "60"])
    ax3.set_ylim(0.8, 110)
    ax3.set_xlim(min(xs) - 0.7, max(xs) + 0.5)
    ax3.set_xlabel("AAM Reality Index score\n(last release that rated the firm)")
    ax3.set_ylabel("unique aircraft (log)")
    ax3.set_title("Position on the index against patenting\n"
                  f"Spearman {rho.split(' (')[0]} ({pv.replace('Spearman ', '')}, n {len(xs)})", fontsize=8.2)
    _hgrid(ax3, "both")
    big = [i for i, yy in enumerate(ys) if yy >= 9]     # only the firms that carry weight are named
    _repel(ax3, [xs[i] for i in big], [ys[i] for i in big],
           [a["company"].iloc[i].replace(" / ", "/") for i in big], fs=6.5, marker_pt=5,
           avoid=list(zip(xs, ys)))
    return _save(fig, path, SRC + "; Table 1.2.1 and Table 1.2.7a; the segment counts of (i) are "
                 "tables/la_coverage_segments.csv and the nested tiers behind them "
                 "tables/la_firm_tiers.csv; index membership and scores from " + ARI_SRC + ".",
                 "The curve climbs steeply over the first firms and then flattens; the boxes split the ranking "
                 "into four disjoint segments, so the firms and the aircraft printed in them add up to the whole — "
                 "three firms hold as many aircraft as the next fourteen, which hold as many as the next "
                 "thirty-eight. The cut "
                 "for per-firm profiles is where a firm still has enough aircraft for a class share to mean something "
                 "(5). Being rated at all is what goes with patenting — index firms hold more aircraft and more "
                 "patents, but start no earlier; where a firm sits on the index does not track how much it patents, "
                 "and the two largest patent holders are incumbents the index rates low or has stopped rating.")


def fig_filers_over_time(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.filers_by_window(v).set_index("window").reindex(WINDOW_NAMES)
    co = la_tables.cohorts(v).set_index("window").reindex(WINDOW_NAMES).fillna(0)
    fig, (ax, axc) = plt.subplots(1, 2, figsize=(W, 4.2), gridspec_kw={"width_ratios": [1.05, 1], "wspace": 0.38})
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
    ax.set_title("Filers per window", fontsize=9.5)
    # why the exits stop: a firm can only be called "last seen" where a later window exists AND a
    # later filing of it could already have published. The last two windows fail that test, so the
    # figure says so on the figure rather than leaving a gap the reader has to explain (author, 2026-09-23).
    ax.axvspan(x[-2] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.35, zorder=0, lw=0)
    ax.text((x[-2] + x[-1]) / 2, -float(gone.max()) * 0.75, "exits not judged here:\na later filing may\nnot have "
            "published yet", ha="center", va="center", fontsize=6.6, color=INK2, linespacing=1.25)
    ax.set_ylim(bottom=-float(gone.max()) * 1.45)
    # (ii) the entry cohorts, NORMALISED (author's ruling 2026-09-23): the class mix of the firms
    # that enter, beside the class mix of the aircraft of the same window. The left bar is firms,
    # the right bar is aircraft; where they differ, entry is running ahead of the field or behind it.
    cm = la_tables.cohort_mix(v, printed=False)
    cols = [c for c in ARCH_ORDER if c in set(cm["class"])]
    ent = (cm.pivot(index="window", columns="class", values="share of entrants")
           .reindex(WINDOW_NAMES).fillna(0))
    air = (cm.pivot(index="window", columns="class", values="share of aircraft")
           .reindex(WINDOW_NAMES).fillna(0))
    wid = 0.33
    for frame, off, hatch in ((ent, -0.185, None), (air, 0.185, "....")):
        bottom = np.zeros(len(frame))
        for c in cols + ["Other"]:
            vals = (frame[c] if c != "Other" else frame.drop(columns=cols, errors="ignore").sum(axis=1)).to_numpy(dtype=float)
            axc.bar(x + off, vals, bottom=bottom, color=_color(c), width=wid, edgecolor=SURFACE, lw=0.7,
                    hatch=hatch, zorder=3)
            bottom += vals
    n_air = cm.groupby("window")["aircraft in the window"].first().reindex(WINDOW_NAMES).fillna(0)
    axc.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    axc.set_xticks(x, [f"{WIN_SHORT[w]}\n{int(e)} · {int(a)}"
                       for w, e, a in zip(WINDOW_NAMES, co["firms entering"], n_air)], fontsize=7)
    axc.set_ylim(0, 1.0)
    axc.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axc.set_ylabel("share of the window")
    axc.set_xlabel("left bar: entering firms\nright bar: the window's aircraft\n(tick: entrants · aircraft)", fontsize=7)
    axc.set_title("Entrants against the field", fontsize=9.5)
    _hgrid(axc, "y")
    h1, l1 = ax.get_legend_handles_labels()
    fig.legend(h1, l1, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2)
    _legend_arch(fig, ARCH_ORDER + ["Other"])
    return _save(fig, path, SRC + "; Tables 1.2.2a/b; named firms = companies and institutes.",
                 "Left, bars above zero: named firms with at least one aircraft in the window, first-timers and "
                 "returners; below zero, firms whose last filing is in that window. Exits are judged only up to "
                 "2016–19: to call a firm gone you need a later window in which it could have filed and did not, and "
                 "the two last windows are still inside the publication lag, so a firm that has filed may simply not "
                 "have published. Right, both bars are normalised, so the height is a mix and not a size: the left bar "
                 "counts FIRMS (the class each entrant enters with, one vote per firm) and the right bar counts "
                 "AIRCRAFT (the same window's class mix, the quantity Figure 1.1.2 draws). Where the left bar runs "
                 "ahead of the right one, the class is being carried into the field by new firms rather than by the "
                 "firms already inside it.")
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
    return _save(fig, path, SRC + "; tables/la_firm_windows.csv; firms ordered by first window, then size.",
                 "One column per firm, one bubble per window it filed in. A column that changes colour is a firm that "
                 "changed its main class; a column that starts low is an entrant.")


def fig_firm_influence(v: pd.DataFrame, path: Path) -> Path:
    """Which firms can move the reading, and which classes rest on few firms.

    Replaces the firm tiles at 1.2.3 (author, 2026-09-23: "I don't really know what to take out
    from this ... the firms are the characters that can influence anything on the analysis").
    Panel (i) is the direct test: drop one firm and see how far the class shares move. Panel (ii)
    is the same question asked of the classes: a class whose largest filer holds a tenth of it
    cannot be one firm's portfolio. Together they answer the author's 1.1.6 question — how much of
    a class is one filer.
    """
    lev = la_tables.firm_leverage(v)
    conc = la_tables.class_concentration(v)
    top = lev.head(12).iloc[::-1]
    # legibility pass 2026-09-23: 4.9 in tall (the rows breathe, and (ii)'s legend gets a row of its
    # own), every label at the 7-pt floor, the "1 pp" tag above the top bar instead of across it
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 4.9), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.52})
    y = np.arange(len(top))
    vals = top["shift if the firm is dropped (pp)"].abs().to_numpy(dtype=float)
    for yi, (_, r) in zip(y, top.iterrows()):
        c = r["modal class"]
        ax.barh(yi, abs(r["shift if the firm is dropped (pp)"]), height=0.68, color=_color(c),
                edgecolor=SURFACE, lw=0.7, zorder=3)
        ax.text(abs(r["shift if the firm is dropped (pp)"]) + 0.06, yi,
                f"{r['class most moved']} {r['shift if the firm is dropped (pp)']:+.1f}", va="center", fontsize=7,
                color=INK, zorder=5, bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.9))
    ax.axvline(1.0, color=INK, lw=1, ls="--")
    ax.set_ylim(-0.6, len(top) + 0.45)        # a clear row above the top bar for the threshold tag
    ax.text(1.05, len(top) - 0.05, "1 pp", fontsize=7, color=INK2, va="center")
    ax.set_yticks(y, [f"{r['firm'].replace(' / ', '/')} ({int(r['unique aircraft'])})" for _, r in top.iterrows()],
                  fontsize=7)
    ax.set_xlim(0, max(3.0, float(vals.max()) * 1.75))
    ax.set_xlabel("percentage points the biggest class share moves\nif this firm is dropped")
    ax.set_title("Which firms could move the reading", fontsize=9.5)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")

    cc = conc[conc["aircraft"] >= 9].sort_values("aircraft")
    y2 = np.arange(len(cc))
    ax2.barh(y2 + 0.19, cc["top 3 firms' share"], height=0.36, color=BLUE(0.35), edgecolor=SURFACE, lw=0.6,
             label="its three largest firms", zorder=3)
    ax2.barh(y2 - 0.19, cc["its share of the class"], height=0.36, color=BLUE(0.85), edgecolor=SURFACE, lw=0.6,
             label="its single largest firm", zorder=3)
    for yi, (_, r) in zip(y2, cc.iterrows()):
        ax2.text(r["its share of the class"] + 0.008, yi - 0.19, f"{r['largest firm'].replace(' / ', '/')} "
                 f"{r['its share of the class']:.0%}", va="center", fontsize=7, color=INK)
        top3 = float(r["top 3 firms' share"])
        ax2.text(top3 + 0.008, yi + 0.19, f"{top3:.0%}", va="center", fontsize=7, color=INK2)
    ax2.set_yticks(y2, [f"{r['class']} ({int(r['aircraft'])}, {int(r['named firms filing in it'])} firms)"
                        for _, r in cc.iterrows()], fontsize=7)
    # the axis runs past the longest bar and leaves an empty band under the last class, so the legend
    # (lower right) sits in that band instead of across a row's bars and names
    ax2.set_xlim(0, 0.84)
    ax2.set_ylim(-2.35, len(cc) - 0.45)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_xlabel("share of the class held by its largest filers")
    ax2.set_title("How much of a class one firm holds", fontsize=9.5)
    ax2.spines[["left"]].set_visible(False)
    ax2.legend(fontsize=7, loc="lower right", framealpha=0.9)
    _hgrid(ax2, "x")
    _legend_arch(fig, [c for c in ARCH_ORDER if c in set(top["modal class"])])
    return _save(fig, path, SRC + "; tables/la_firm_leverage.csv and tables/la_class_concentration.csv; "
                 "classes with 9 or more aircraft on the right.",
                 "(i) each bar is one firm removed from the analysis set and the class shares re-taken: the bar is the "
                 "largest share that moves and the label names the class and the direction. Only two firms move any "
                 "class share by a full percentage point, so no reading in this document rests on one portfolio; the "
                 "bar colour is the class the firm files most. (ii) the same question asked of the classes: the share "
                 "of each class held by its largest filer and by its three largest. A class whose largest filer holds "
                 "a sixth of it is a spread of firms, not one firm's programme.")


def fig_proximity_region(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    """1.2.6 — the proximity matrix with the firms grouped in region blocks (user ruling 2026-09-23)."""
    m, summary = la_tables.proximity_by_region(ds, v)
    reg = m.attrs["region"]
    blocks = m.attrs["blocks"]
    prof = a2.firm_profiles(ds, FIRM_MIN, "class")
    size = prof.sum(axis=1)
    n = len(m)
    fig, ax = plt.subplots(figsize=(W * 0.84, W * 0.96))
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
    # region blocks: the firms are ordered region by region, so the blocks are contiguous. A rule is
    # drawn on both axes at every block edge and the region is named over its own block of columns.
    edges, at = [], 0
    for b in blocks:
        k = int((reg == b).sum())
        edges.append((b, at, at + k))
        at += k
    for _, s, e in edges[1:]:
        ax.axhline(s - 0.5, color=INK, lw=1.4, zorder=6)
        ax.axvline(s - 0.5, color=INK, lw=1.4, zorder=6)
    for b, s, e in edges:
        ax.add_patch(matplotlib.patches.Rectangle((s - 0.5, s - 0.5), e - s, e - s, fill=False,
                                                  edgecolor=INK, lw=1.6, zorder=7, clip_on=False))
        ax.text((s + e - 1) / 2, -0.95, b, ha="center", va="bottom", fontsize=8, fontweight="bold",
                color=INK, clip_on=False)
    ax.set_xlim(-1.7, n - 0.5)
    ax.set_ylim(n - 0.5, -1.05)
    labels = [f"{f} ({int(size[f])})" for f in m.index]
    ax.set_yticks(range(n), labels, fontsize=7.5)
    ax.set_xticks(range(n), labels, rotation=90, fontsize=7.5)
    ax.tick_params(axis="y", pad=26)
    ax.xaxis.set_ticks_position("bottom")
    for sp_ in ax.spines.values():
        sp_.set_visible(False)
    txt = " · ".join(f"{r['region pair']}: mean {r['mean']:.2f} over {int(r['pairs'])} pairs"
                     for _, r in summary.iterrows())
    a_ = summary.attrs
    txt += (f". Over all pairs, same region {a_['same mean']:.2f} ({a_['same pairs']} pairs) against different "
            f"region {a_['different mean']:.2f} ({a_['different pairs']} pairs); permutation p = {a_['p']:.2f} "
            f"on {a_['draws']:,} label shuffles, so the regions are not design blocs")
    ax.set_title("Technological proximity between firms, grouped by region (class profile)", fontsize=9, pad=26)
    handles = [matplotlib.patches.Patch(facecolor=REGION_COLOR[r_], hatch=hatch_reg[r_], edgecolor=(0, 0, 0, 0.55), label=r_)
               for r_ in REGIONS]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.03), ncol=3, fontsize=7.5, frameon=False,
              borderaxespad=0.2)
    fig.canvas.draw()
    lab_bottom = ax.xaxis.get_tightbbox(fig.canvas.get_renderer()).y0 / (fig.get_figheight() * fig.dpi)
    cax = fig.add_axes([0.3, lab_bottom - 0.022, 0.4, 0.014])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("proximity: 1 = same mix of classes, 0 = none in common", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    fig._bw_off = True
    return _save(fig, path, SRC + "; Jaffe (1986) cosine of firm × class vectors, firms with 5 or more aircraft; "
                 "Table 1.2.6. " + txt + ".",
                 "Two firms score 1 when they file the same mix of architecture classes and 0 when they share none; "
                 "values of 0.75 and above are printed in the cell. The firms are grouped by region and the boxed "
                 "square on the diagonal of each block is that region on its own, so a region whose firms all design "
                 "alike shows as a dark box: Asia-Pacific is the darkest (mean 0.64), Europe the lightest (0.39). "
                 "Outside the boxes are the cross-region pairs. If regions were design blocs the boxes would be "
                 "darker than everything around them; they are not, which is what the permutation test in the Source "
                 "line says. The number after a firm is its unique aircraft; the strip left of each row repeats the "
                 "region so a single row can be read on its own.")


def fig_ari(v: pd.DataFrame, path: Path) -> Path:
    """1.2.7a — score and class mix."""
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
    return _save(fig, path, ARI_SRC + "; corpus counts from " + SRC + "; Table 1.2.7a.",
                 "Bars: the index score; light bars are firms no longer listed, with the last score they had. Right: the "
                 "firm's patented aircraft by class.")


def fig_ari_history(v: pd.DataFrame, path: Path) -> Path:
    """1.2.7b — how each firm's score moved, and funding against patented aircraft.

    Rebuilt 2026-09-23 on the author's review ("on the left I don't know how to read this"). The left
    panel was eighteen overlapping score lines over thirty-four releases, which no reader can follow.
    It is now one row per firm: the score at its first listing, the score at its last, and the move
    between them — the same data, read as a ranking with a direction instead of a tangle. The right
    panel keeps every firm that discloses a funding figure and says on the panel how many of the
    eighteen that is, because it is a segment of a segment.
    """
    f = la_tables.ari_firms(v)
    hist = la_tables.ari_history_corpus(v)
    fig, (ax2, ax3) = plt.subplots(1, 2, figsize=(W * 0.91, 4.6), gridspec_kw={"wspace": 0.62, "width_ratios": [1.0, 0.8]})
    rows = []
    for comp, sub in hist.groupby("company"):
        sub = sub.sort_values("date")
        rows.append(dict(company=comp, first=float(sub["score"].iloc[0]), last=float(sub["score"].iloc[-1]),
                         t0=sub["release"].iloc[0], t1=sub["release"].iloc[-1], n=len(sub)))
    d = pd.DataFrame(rows).sort_values("last").reset_index(drop=True)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        up = r.last >= r.first
        ax2.plot([r.first, r.last], [yi, yi], color=INK2, lw=1.0, zorder=2, solid_capstyle="butt")
        ax2.plot(r.first, yi, marker="o", ms=4.5, color=SURFACE, mec=INK2, mew=1.1, zorder=3)
        ax2.plot(r.last, yi, marker="o", ms=5.5, color=BLUE(0.85) if up else CAT[1], mec=SURFACE, mew=0.7, zorder=4)
        ax2.text(r.last + 0.18, yi, f"{r.last:.1f}", va="center", fontsize=7, color=INK2)
    short = lambda c: c.replace(" Flight Technologies", "").replace(" / Geely Aviation", " / Geely")
    ax2.set_yticks(y, [f"{short(r.company)}  ({r.t1[:3]} {r.t1[-4:]})" for r in d.itertuples()], fontsize=7.5)
    ax2.set_xlim(2.8, 10.2)
    ax2.set_ylim(-0.8, len(d) + 1.5)          # an empty band at the top, for the key
    ax2.set_xlabel("AAM Reality Index score (0–10)", fontsize=8)
    ax2.set_title("First listing against latest score", fontsize=9)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    key = [matplotlib.lines.Line2D([], [], ls="", marker="o", ms=4.5, color=SURFACE, mec=INK2, mew=1.1,
                                   label="first listing"),
           matplotlib.lines.Line2D([], [], ls="", marker="o", ms=5.5, color=BLUE(0.85), label="latest score, higher"),
           matplotlib.lines.Line2D([], [], ls="", marker="o", ms=5.5, color=CAT[1], label="latest score, lower")]
    ax2.legend(handles=key, fontsize=7, loc="upper center", ncol=3, frameon=False, columnspacing=1.0,
               handletextpad=0.35, borderpad=0.2)
    fc = f.copy()
    fc["funding"] = pd.to_numeric(fc["funding $M"].astype(str).str.replace(",", ""), errors="coerce")
    disclosed = fc.dropna(subset=["funding"])
    ax3.scatter(disclosed["unique aircraft"], disclosed["funding"], s=30 + 40 * disclosed["ARI score"].fillna(5) / 10,
                color=BLUE(0.8), edgecolor=SURFACE, zorder=3)
    hi = int(disclosed["unique aircraft"].max())
    ax3.set_yscale("log")
    ax3.set_xlim(0.3, hi + 0.9)
    ax3.set_xticks(range(1, hi + 1), [str(k) for k in range(1, hi + 1)])
    ax3.set_xlabel("unique aircraft in the corpus", fontsize=8)
    ax3.text(0.98, 0.02, f"only {len(disclosed)} of the {len(fc)}\nindex firms disclose\na funding figure",
             transform=ax3.transAxes, ha="right", va="bottom", fontsize=7, color=INK2)
    ax3.set_ylabel("disclosed funding, $M (log)", fontsize=8)
    ax3.set_title("Funding against aircraft", fontsize=9)
    _hgrid(ax3, "both")
    _repel(ax3, disclosed["unique aircraft"].tolist(), disclosed["funding"].tolist(),
           [c.replace(" Flight Technologies", "").replace(" / Geely Aviation", " / Geely") for c in disclosed["company"]],
           marker_pt=6)
    undisclosed = ", ".join(fc[fc["funding"].isna()]["company"])
    return _save(fig, path, ARI_SRC + "; Table 1.2.7a. " + str(len(disclosed)) + " of the " + str(len(fc))
                 + " index firms that file in this corpus publish a funding figure; the other "
                 + str(len(fc) - len(disclosed)) + " are corporate-backed or were dropped from the index before it "
                 "carried funding, and are not in (ii): " + undisclosed + ".",
                 "(i) One row per firm, ordered by where it stands today: the hollow dot is the score at its first "
                 "listing, the filled dot the score at its last, and the date after the name is that last listing — "
                 "a firm still in the index reads 'May 2026'. The line between them is the whole move, so a long line "
                 "is a firm the index changed its mind about. (ii) is a segment of a segment and must be read as one: "
                 "of the " + str(len(fc)) + " index firms that file in this corpus, only " + str(len(disclosed))
                 + " publish a funding figure, and those " + str(len(disclosed)) + " hold between 1 and "
                 + str(hi) + " aircraft here, so the horizontal axis runs over single aircraft and not over the "
                 "corpus. Nothing on (ii) can be read as a statement about the corpus as a whole.")


def fig_ari_clock(v: pd.DataFrame, path: Path) -> Path:
    """1.2.7c — the patent clock against the market clock.

    Every date on the market side comes from one stored file and the Source line now says which
    (``la_tables.ARI_DATE_SRC``, user review 2026-09-23): the first-flight and entry-into-service
    fields of the May 2026 release, kept in ``assets/external/aam_reality_index/ari_may2026.csv``.
    """
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
    ax4.set_title(f"Patent clock against market clock, the {len(tl)} index firms listed in May 2026 that file here",
                  fontsize=9)
    _hgrid(ax4, "x")
    flew = int(tl["first flight (ARI)"].notna().sum())
    return _save(fig, path, ARI_SRC + "; corpus priority years; Tables 1.2.7d and 1.2.7e. "
                 + la_tables.ARI_DATE_SRC + ".",
                 "Each row is one firm: the bar is its patent span in this corpus, from its earliest to its latest "
                 "priority year, and the vertical tick is the year it filed most. The two coloured markers, named in "
                 "the key under the figure, are the market clock — the first flight the index reports and the entry "
                 "into service it reports as planned. "
                 f"{flew} of the {len(tl)} firms have a first flight on record; a marker to the right of the dotted "
                 "'today' line has not happened yet and is a plan. The gap between the bar and the first-flight marker "
                 "is the years from a firm's first patent here to its first flight, and Table 1.2.7e groups that gap by "
                 "region and by certifying authority. The number after a firm is its unique aircraft in this corpus. "
                 "Nothing on this figure is a flight record: both market dates are the index's own statements.")
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
    return _save(fig, path, EVN_SRC + "; G1 class folded as Table 2.5a (VT vectored thrust, LC lift + cruise, WM wingless, "
                 "ER electric rotorcraft, HB hover bikes); capacity, piloting, power source and status read off the "
                 "directory page by keyword rules over one field each — no model is involved and nothing comes from the "
                 "patent; the links are the hand-reviewed patent_links.csv (aircraft name + company against the directory "
                 "index, plus the URLs recorded in NAME_DECISIONS.csv).",
                 "(i) to (iv): each bar is 100 % of the linked aircraft of one folded class. Bottom: how often the folded "
                 "patent class agrees with the directory's class of the same aircraft (count in the cell). These are the "
                 "publicly announced aircraft of the corpus, not a sample of it — Figure 2.5c tests how far they stand "
                 "for the rest, and the answer is that the class mix and the geography carry back while the filer mix, "
                 "the dates and the size of the aircraft do not.")


def fig_linked_check(v: pd.DataFrame, path: Path) -> Path:
    """Figure 2.5c: whether the aircraft linked to an evtol.news page stand for the whole set.

    Section 2.5 is a description of the linked aircraft; the author's ruling of 2026-09-23 is that
    it is only worth reading if those aircraft are representative, and that the answer has to be
    stated. So the test is drawn, not asserted: for every level of four attributes, the share inside
    the linked set against the share in everything else, with the per-attribute test printed beside
    the group.
    """
    t = la_tables.linked_representativeness(v)
    n_in, n_out = t.attrs.get("linked", 0), t.attrs.get("rest", 0)
    cat = t[t["level"].ne("median")].reset_index(drop=True)
    con = t[t["level"].eq("median")]
    fig, ax = plt.subplots(figsize=(W, 0.205 * len(cat) + 1.9))
    y = np.arange(len(cat))
    ax.hlines(y, cat["rest %"], cat["linked %"], color=GRID, lw=2.6, zorder=1)
    ax.scatter(cat["rest %"], y, marker="s", s=26, facecolor="none", edgecolor=INK2, lw=1.0,
               zorder=3, label=f"the other {n_out} aircraft")
    ax.scatter(cat["linked %"], y, marker="o", s=30, color=CAT[0], edgecolor=SURFACE, lw=0.5,
               zorder=3, label=f"the {n_in} linked aircraft")
    for yi, r in cat.iterrows():
        if abs(r["gap pp"]) >= 5:
            x_ = max(r["rest %"], r["linked %"])
            ax.text(x_ + 1.5, yi, f"{r['gap pp']:+.0f} pp", va="center", fontsize=6.5, color=INK2)
    def _p(value: float) -> str:
        return "p < 0.001" if value < 0.001 else f"p = {value:.3f}"

    x_lab = 118.0
    for name in cat["attribute"].unique():
        idx = cat.index[cat["attribute"].eq(name)]
        a_, b_ = int(idx.min()), int(idx.max())
        pv = float(cat.loc[a_, "p"])
        same = pv >= 0.05
        if a_:
            ax.axhline(a_ - 0.5, color=GRID, lw=0.8)
        ax.text(x_lab, (a_ + b_) / 2,
                f"{name}\n{'no difference detected' if same else 'differs'}\n{_p(pv)}",
                fontsize=7, ha="right", va="center", color=CAT[5] if same else CAT[7],
                fontweight="bold", linespacing=1.3)
    lev_names = [FOLD5_NAMES.get(s, s).replace("<= ", "≤ ") for s in cat["level"]]
    ax.set_yticks(y, lev_names, fontsize=7.5)
    ax.set_ylim(len(cat) - 0.5, -0.5)
    ax.set_xlim(-2, x_lab + 2)
    ax.set_xticks([0, 20, 40, 60, 80], ["0", "20", "40", "60", "80 %"], fontsize=7.5)
    ax.set_xlabel("share of the set it belongs to", fontsize=8)
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.42, -0.07), ncol=2,
              handlelength=1.0, columnspacing=1.6, frameon=False)
    ax.set_title(f"Are the {n_in} aircraft linked to an evtol.news page a fair picture of the "
                 f"{n_in + n_out}?", fontsize=9)
    fig._bw_off = True                     # shape and position carry it; nothing here is a filled category

    med = "; ".join(f"{r['attribute']} median {r['linked %']:.0f} against {r['rest %']:.0f} "
                    f"({_p(float(r['p']))})" for _, r in con.iterrows())
    same = [a for a in cat["attribute"].unique()
            if float(cat.loc[cat["attribute"].eq(a), "p"].dropna().iloc[0]) >= 0.05]
    diff = [a for a in cat["attribute"].unique() if a not in same]
    return _save(
        fig, path,
        EVN_SRC + f"; the {n_in} linked aircraft against the other {n_out} of the analysis set; "
                  "chi-square per attribute for the categorical ones, Mann-Whitney for the two "
                  "medians; the full frame is tables/la_linked_representativeness.csv.",
        "One row per level of an attribute: the open square is the share among the aircraft with no "
        "evtol.news page, the filled circle the share among the linked ones, and the line between "
        "them is the gap. A test that finds no difference at this n is not proof of sameness; a test "
        "that finds one is. Answer: no difference is detectable on "
        + (" or ".join(same) if same else "nothing")
        + ", and there is a clear one on " + (" and ".join(diff) if diff else "nothing")
        + f" — {med}. The reason is in how a link is made: an aircraft can only be linked when the "
          "labelling gave it a real name and a public directory of announced programmes carries that "
          "name, so the linked set is the publicly announced, company-backed part of the corpus. "
          "Section 2.5 therefore describes announced eVTOL programmes, and its class mix and its "
          "geography can be carried back to the whole corpus; its filer mix, its dates and the size "
          "of its aircraft cannot.")


#: Figure 1.1.1 opens here. (i) pools everything earlier into this bar; (ii) starts here as a single year.
FILINGS_FIRST_YEAR = 2005

#: Dated sector events on the timeline of Figure 1.1.1 — the author's ruling of 2026-09-23: the
#: overall rise in eVTOL patenting is read against what happened outside the patent record (the
#: Uber Elevate paper, first flights, certification rules, listings, insolvencies), and is not
#: tested against morphology. The figure reads the CSV at render time, so the list is edited in
#: the file, never here; its README says how. A missing or empty file draws the figure as it was.
EVENTS_FILE = la_baseline.ASSETS / "external" / "sector_events" / "sector_events.csv"
EVENTS_SRC = ("sector events: assets/external/sector_events/sector_events.csv (the author's first pass, "
              "one source URL per event, dates checked 2026-09-23)")
#: a label longer than this is cut with an ellipsis: the strip is exactly as tall as its longest label
EVENT_LABEL_MAX = 28
#: geometry of the strip, inches: the tick an event stands on, the gap to its label, the clearance
#: between the tallest label and the bars; and how far apart, in years, two events of one year stand
EVENT_TICK_IN, EVENT_PAD_IN, EVENT_CLEAR_IN, EVENT_SIDE_STEP = 0.08, 0.04, 0.10, 0.5


def sector_events(snapshot: Optional[str] = None) -> pd.DataFrame:
    """The stored event list, one row per event in date order, with its calendar ``year``.

    Rows without a readable date and events dated after the snapshot are dropped with a printed
    line; a missing file gives an empty frame, so the figure still renders without the list."""
    cols = ["date", "event", "source_url", "note"]
    if not EVENTS_FILE.exists():
        return pd.DataFrame(columns=cols + ["year"])
    e = pd.read_csv(EVENTS_FILE, dtype=str, keep_default_na=False)
    missing = [c for c in cols if c not in e.columns]
    if missing:
        raise ValueError(f"{EVENTS_FILE} lacks the column(s) {missing}; its README names them")
    e["date"] = pd.to_datetime(e["date"].str.strip(), errors="coerce")
    bad = e["date"].isna()
    if bad.any():
        print(f"  ! sector events without a readable date, skipped: {e.loc[bad, 'event'].tolist()}")
        e = e[~bad]
    if snapshot:
        late = e["date"] > pd.Timestamp(snapshot)
        if late.any():
            print(f"  ! sector events after the snapshot {snapshot}, not drawn: {e.loc[late, 'event'].tolist()}")
        e = e[~late]
    e = e.sort_values("date", kind="stable").reset_index(drop=True)
    e["year"] = e["date"].dt.year.astype(int)
    return e


def _event_labels(ev: pd.DataFrame) -> List[str]:
    out = []
    for s in ev["event"].astype(str).str.strip():
        if len(s) > EVENT_LABEL_MAX:
            print(f"  ! sector event label cut to {EVENT_LABEL_MAX} characters: {s!r}")
            s = s[:EVENT_LABEL_MAX - 1].rstrip() + "…"
        out.append(s)
    return out


def _event_x(ev: pd.DataFrame, xmin: int, xmax: int) -> np.ndarray:
    """Where each event stands: on its calendar year — the axis is the priority year of the
    filings, and an event dated by calendar date sits at its year, never between two — clipped
    to the drawn years, so an event before ``xmin`` stands on the pooled bar. Two or more events
    in one year stand side by side, in date order."""
    early = ev["year"] < xmin
    if early.any():
        print(f"  ! sector events before {xmin} stand on the pooled ≤{xmin} bar: {ev.loc[early, 'event'].tolist()}")
    xs = ev["year"].clip(lower=xmin, upper=xmax).to_numpy(dtype=float)
    for y in np.unique(xs):
        k = np.flatnonzero(xs == y)
        if len(k) > 1:
            xs[k] = y + (np.arange(len(k)) - (len(k) - 1) / 2) * EVENT_SIDE_STEP
    return xs


def _event_strip_height(ev: pd.DataFrame) -> float:
    """Height in inches the strip needs: its longest label drawn as it will be (7 pt, upright),
    plus the tick under it and the clearance above it. Measured on a throwaway canvas, so the
    figure can be laid out before it is drawn."""
    if not len(ev):
        return 0.0
    with plt.rc_context(STYLE):
        f = plt.figure(figsize=(2, 2))
        f.canvas.draw()
        r = f.canvas.get_renderer()
        tall = max(f.text(0.5, 0.5, lb, rotation=90, fontsize=7).get_window_extent(r).height
                   for lb in _event_labels(ev)) / f.dpi
        plt.close(f)
    return EVENT_TICK_IN + EVENT_PAD_IN + tall + EVENT_CLEAR_IN


def _event_strip(fig, ax, ev: pd.DataFrame, xmin: int, xmax: int, strip_in: float,
                 ticks: List, tick_labels: List[str]) -> None:
    """The timeline strip hung directly under the bars of (i).

    It is an inset of (i) — the same x range, and no axes of its own in ``fig.axes`` — so the
    figure still holds two graphs and the marks stay (i) and (ii). The year labels move from
    the bars to the foot of the strip; every event stands on its year as a short tick with its
    label reading upward, and a faint dotted guide runs up through the bars from it. Chosen
    over markers inside (i) on 2026-09-23: there the labels crossed the patents line, the
    legend and the incomplete-years note; here nothing is covered."""
    xs = _event_x(ev, xmin, xmax)
    labels = _event_labels(ev)
    ax_in = ax.get_position().height * fig.get_figheight()
    h = strip_in / ax_in
    s = ax.inset_axes([0.0, -h, 1.0, h])
    s.set_xlim(ax.get_xlim())
    s.set_ylim(0, strip_in)
    s.patch.set_alpha(0.0)
    s.set_xticks(ticks, tick_labels, rotation=45, fontsize=7.5)
    s.set_yticks([])
    for side in ("top", "left", "right"):
        s.spines[side].set_visible(False)
    s.set_ylabel("sector events", fontsize=7.5)
    ax.tick_params(axis="x", labelbottom=False)
    for x, lab in zip(xs, labels):
        s.plot([x, x], [0, EVENT_TICK_IN], color=INK, lw=0.9, solid_capstyle="butt", zorder=3)
        s.text(x, EVENT_TICK_IN + EVENT_PAD_IN, lab, rotation=90, ha="center", va="bottom",
               fontsize=7, color=INK, zorder=4)
        ax.axvline(x, color=INK2, lw=0.6, ls=(0, (1, 2.2)), zorder=0.6)


def fig_filings_per_year(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    full = la_tables.filings_per_year(ds, v).set_index("priority year")
    # (i) is a chart of totals, so it pools 1999-2004 into its "≤2005" bar: before the author's
    # ruling of 2026-09-23 those years were filtered away while the tick still said "≤2005", which
    # hid 17 aircraft and 47 patents. (ii) is a per-year index and cannot pool -- a seven-year
    # bucket is not a year -- so it is drawn from the unpooled frame and opens on 2005 alone.
    # Table 1.1.1 keeps every year as its own row; the How-to-read line says so.
    t = la_baseline.pool_to_first(full, FILINGS_FIRST_YEAR)
    ti = full[full.index >= FILINGS_FIRST_YEAR]
    p90 = t.attrs["p90"]
    pooled = t.attrs.get("pooled_years")
    # the dated sector events of the strip under (i); events after the snapshot are not drawn
    ev = sector_events(t.attrs["snapshot"])
    strip_in = _event_strip_height(ev)
    # (ii) is drawn only when the stored aviation baseline is installed; without it the figure
    # is exactly the raw-count graph it was before (user, 2026-09-22).
    ix_e, ix_a = la_baseline.COLS["evtol_ix"], la_baseline.COLS["avia_ix"]
    normalised = ix_e in ti.columns and ti[ix_e].notna().any() and ti[ix_a].notna().any()
    # panel heights in inches. Without events the figure is the 6.9 in it was (2.40 / 1.85, with
    # a 1.06 in gap for the year labels and the title of (ii)); with the strip the gap grows by
    # the strip and the panels give up some height, so the figure, its Source and How-to-read
    # lines included, still fits a page with its caption. Margins stay matplotlib's 0.11 / 0.88.
    if normalised:
        a1, a2 = (2.05, 1.45) if strip_in else (2.40, 1.85)
        gap = 1.06 + strip_in
        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(W, (a1 + a2 + gap) / 0.77),
                                      gridspec_kw={"hspace": gap / ((a1 + a2) / 2), "height_ratios": [a1, a2]})
    else:
        fig, ax = plt.subplots(figsize=(W, 3.8 + strip_in))
        if strip_in:                       # the panel keeps its 2.93 in; the strip takes the rest
            fig.subplots_adjust(bottom=(0.42 + strip_in) / (3.8 + strip_in), top=1 - 0.46 / (3.8 + strip_in))
        ax2 = None
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
    if pooled:
        # the pooled bar is taller than its neighbours because it is seven years, not a big year
        ax.annotate(f"{pooled[0]}-{FILINGS_FIRST_YEAR}\npooled", (FILINGS_FIRST_YEAR, t.loc[FILINGS_FIRST_YEAR, "patents acquired"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=7, color=INK2, va="bottom")
    ticks = list(t.index)
    tick_labels = [(f"≤{FILINGS_FIRST_YEAR}" if y == FILINGS_FIRST_YEAR and pooled else str(y)) for y in t.index]
    ax.set_xticks(ticks, tick_labels, rotation=45, fontsize=7.5)
    ax.set_ylabel("unique aircraft (bars) · patents acquired (line)")
    ax.legend(loc="upper left", fontsize=7.5)
    ax.set_title("Filings per priority year, by applicant region; dashed, faded bars are years still filling")
    _hgrid(ax, "y")
    if strip_in:
        _event_strip(fig, ax, ev, FILINGS_FIRST_YEAR, int(t.index.max()), strip_in, ticks, tick_labels)

    src = (SRC + f"; Table 1.1.1; PatSeer snapshot {t.attrs['snapshot']}; "
                 f"90th-percentile priority-to-publication lag = {p90:.0f} years.")
    if strip_in:
        src += " " + EVENTS_SRC[0].upper() + EVENTS_SRC[1:] + "."
    read = ("Bars: representative unique aircraft by the priority year of their primary record, stacked by applicant "
            "region (region hatches survive black and white); line: every acquired patent. A year is drawn faded with a "
            "dashed outline while the snapshot is less than the 90th-percentile lag after its end: those bars will still grow.")
    if pooled:
        first_row = t.loc[FILINGS_FIRST_YEAR]
        read += (f" The first bar is the only pooled one: it holds {pooled[0]}-{FILINGS_FIRST_YEAR} together "
                 f"({int(first_row['unique aircraft'])} aircraft, {int(first_row['patents acquired'])} patents), "
                 f"hence its tick ≤{FILINGS_FIRST_YEAR}; Table 1.1.1 keeps those years as separate rows.")
    if strip_in:
        read += (" Strip under the bars: dated sector events from the CSV, the author's first pass. The axis is the "
                 "priority year of the filings, so an event stands on its calendar year even when most of that year's "
                 "priority filings precede it (an event of October, say); two events in one year stand side by side "
                 "in date order, and events after the snapshot are not drawn.")

    if normalised:
        # ti, not t: a per-year index must be built on single years (see la_baseline.pool_to_first)
        r = la_baseline.readings(ti)
        lo, hi = la_baseline.BASE_YEARS
        ax2.plot(ti.index, ti[ix_e], color=INK, lw=2, marker="o", ms=3.5,
                 label="eVTOL: patents acquired, this corpus")
        ax2.plot(ti.index, ti[ix_a], color=MUTED, lw=2, ls="--", marker="s", ms=3.5,
                 label="aviation: all B64 patents, same offices")
        ax2.axhline(100, color=INK2, lw=0.8, ls=":")
        first_incomplete = int(ti.index[~ti["complete"]].min())
        ax2.axvspan(first_incomplete - 0.5, ti.index.max() + 0.5, color=GRID, alpha=0.75, zorder=0, hatch="//", lw=0)
        ax2.text(first_incomplete - 0.35, ax2.get_ylim()[1] * 0.97,
                 "both sides still filling:\nthe ratio is not read here", va="top", fontsize=7, color=INK2)
        # the last complete year carries the answer, so it is the only point labelled
        last = r.get("last_complete")
        if last in ti.index:
            for col, val in ((ix_e, ti.loc[last, ix_e]), (ix_a, ti.loc[last, ix_a])):
                ax2.annotate(f"{val:.0f}", (last, val), textcoords="offset points", xytext=(4, 4),
                             fontsize=7, color=INK2)
        # (i) pools into its first tick, (ii) does not, so only (i) carries the "≤"
        ax2.set_xticks(list(ti.index), [str(y) for y in ti.index], rotation=45, fontsize=7.5)
        ax2.set_ylabel(f"index, mean of {lo}-{hi} = 100")
        ax2.legend(loc="upper left", fontsize=7.5)
        ax2.set_title("The same filings against aeronautics patenting as a whole: both sides "
                      f"indexed to their own {lo}-{hi} mean", fontsize=9.5)
        _hgrid(ax2, "y")
        # str.capitalize() would lower-case CPC, B64 and the office codes, so only the first letter moves
        src += (" " + la_baseline.SOURCE[0].upper() + la_baseline.SOURCE[1:] + ". Both sides of (ii) are counted by "
                "priority year; the baseline counts patent publications, so (ii) is drawn from the corpus's own "
                "patent count and not from the aircraft of the bars.")
        mult = r.get("growth")
        gained = r.get("first_above")
        # shortened 2026-09-23 to make room for the event strip: the same facts, fewer lines
        read += (f" (ii) asks whether the rise is the sector's own: aviation patenting also grew, so the corpus's "
                 f"patents and all B64 patents are each indexed to their {lo}-{hi} mean = 100. eVTOL is above "
                 f"aviation from {gained} onwards and by {last} stands {mult:g}× higher, so the rise is not the "
                 f"tide: the corpus then holds {r.get('ratio_end')} eVTOL patents per 1 000 B64 patents against "
                 f"{r.get('ratio_start')} in the base window (Table 1.1.1). The hatched years are incomplete on "
                 f"both sides and the ratio there is unstable; the baseline covers only the nine publication "
                 f"offices the corpus draws on. (ii) does not pool: its first point is {FILINGS_FIRST_YEAR} alone, "
                 f"because an index of single years cannot take a seven-year bucket as a point and the two sides "
                 f"would not pool by the same factor.")

    return _save(fig, path, src, read)


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
    return _save(fig, path, SRC + "; levels defined in Table 1.1.3.1a, conditions in Table 1.1.3.2, numbers in Table 1.1.3.3b; "
                 "rarefied to 40 aircraft; 200 permutations; Q (condition 3) needs the Gower distance and is "
                 "not computed here.",
                 "(i) condition 1: a dominant design needs the top archetype above the dashed line in two consecutive complete windows; "
                 "A0c = class × propulsive-unit bin, A1t = class × wings × tilting. (ii) and (iii) condition 2: the window is more concentrated "
                 "than chance only where the observed ²D falls below the grey band, and holds more designs in play than chance "
                 "where it sits above the band. The hatched window is still incomplete.")


#: a window resting on fewer than this many aircraft of the class is drawn with a hollow
#: marker, so a thin point can never be read as a solid one (user, 2026-09-22)
THIN_CELL = 10


def _class_line(ax, x, y, n, code, label=None, lw=2.0, ms=5.0):
    """One class line. Points resting on fewer than :data:`THIN_CELL` aircraft are drawn
    hollow; a window the class does not reach at all is a gap, never an interpolation."""
    mk, ls = _cs(code)
    col = _color(code)
    y = np.asarray(pd.to_numeric(pd.Series(y), errors="coerce"), dtype=float)
    n = np.asarray(pd.to_numeric(pd.Series(n), errors="coerce").fillna(0), dtype=float)
    ax.plot(x, y, ls=ls, lw=lw, color=col, marker="", label=label, zorder=3)
    solid = n >= THIN_CELL
    ax.plot(np.where(solid, x, np.nan), np.where(solid, y, np.nan), ls="", marker=mk, ms=ms,
            color=col, zorder=4)
    ax.plot(np.where(~solid, x, np.nan), np.where(~solid, y, np.nan), ls="", marker=mk, ms=ms,
            mfc=SURFACE, mec=col, mew=1.1, zorder=4)


def _class_legend(fig, t, ncol=3, y=-0.02):
    """One legend entry per class, by name and code, in the order the classes are drawn."""
    names = dict(zip(t["code"], t["class"]))
    handles = [matplotlib.lines.Line2D([], [], color=_color(c), ls=_cs(c)[1], marker=_cs(c)[0],
                                       ms=5, lw=2, label=f"{names[c]} ({c})")
               for c in dict.fromkeys(t["code"])]
    fig.legend(handles=handles, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol)


def _selection_line(t) -> str:
    """The sentence that justifies which classes are drawn, from the frame's own numbers.

    It names the classes left out and the individual windows left blank, with their counts, so
    neither a missing line nor a gap in one can be read as "that design did not exist then"."""
    a = t.attrs
    out = (f"Classes drawn — the rule, not a size ranking: every class holding at least {a['min_cell']} unique "
           f"aircraft in at least {a['min_windows']} of the five windows, which is {', '.join(a['names'])}, "
           f"{a['aircraft']} of the {a['classified']} classified aircraft ({a['share']:.0%}). ")
    if a.get("dropped"):
        out += ("Left out as too thin to carry a line, not as absent from the corpus: "
                + ", ".join(f"{c} {n}" for c, n in a["dropped"].items()) + " aircraft. ")
    out += f"A hollow marker rests on {a['min_cell']}–{THIN_CELL - 1} aircraft. "
    if a.get("suppressed"):
        cells = "; ".join(f"{c} " + " and ".join(f"{WIN_SHORT.get(wn, wn)} ({n})" for wn, n in v_)
                          for c, v_ in a["suppressed"].items())
        out += (f"A gap is a window the class does reach but with fewer than {a['min_cell']} aircraft, so the cell is "
                f"suppressed and never joined up — {cells}. The class exists in those windows.")
    return out


def fig_dominant_design_q(ds: Dataset, v: pd.DataFrame, path: Path,
                          q: Optional[pd.DataFrame] = None) -> Path:
    """Condition 3: Rao's Q per window against the level of the earliest windows and its band."""
    t = la_tables.dominant_design_q(ds, v) if q is None else q
    main, alt = la_tables.Q_WEIGHTINGS
    levels = list(dict.fromkeys(t["level"]))
    fig, axes = plt.subplots(1, 3, figsize=(W, 3.3), gridspec_kw={"wspace": 0.45})
    x = np.arange(len(WINDOW_NAMES))
    # (i) the level of Q itself, under both weightings
    ax = axes[0]
    for wt, col, ls, mk in ((main, INK, "-", "o"), (alt, MUTED, "--", "^")):
        s = t[t["level"].eq(levels[0]) & t["weighting"].eq(wt)].set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, s["Q"], marker=mk, ls=ls, lw=2, ms=5, color=col,
                label=f"Q, {wt} weighting" + (" (5.3, main)" if wt == main else " (robustness)"))
        ax.axhline(float(s["Q of the earliest windows"].dropna().iloc[0]), color=col, lw=0.9, ls=":")
    ax.set_title("Q: distance between two\naircraft of the window", fontsize=8.5)
    ax.set_ylim(0)
    h1, l1 = ax.get_legend_handles_labels()
    # (ii) and (iii) the fall from the earliest windows, against the permutation band, per level
    for ax, lvl in zip(axes[1:], levels[:2]):
        s = t[t["level"].eq(lvl) & t["weighting"].eq(main)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, s["ΔQ permutation low"], s["ΔQ permutation high"], color=GRID, alpha=0.9,
                        label="permutation band (windows shuffled across aircraft)")
        ax.axhline(0, color=INK, lw=1, ls="--")
        ax.plot(x, s["ΔQ"], marker="o", ms=4.5, lw=1.8,
                color=CAT[0] if lvl == levels[0] else CAT[1], label="observed ΔQ")
        below = s[s["below band"].astype(bool)]
        if len(below):
            ax.plot([WINDOW_NAMES.index(w) for w in below.index], below["ΔQ"], "o", ms=9, mfc="none",
                    mec=INK, mew=1.4, label="below the band: condition 3 met")
        ax.set_title(f"Condition 3:\nΔQ at {lvl} against the band", fontsize=8.5)
        if lvl == levels[0]:
            h, l = ax.get_legend_handles_labels()
            fig.legend(h1 + h, l1 + l, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
            fig.subplots_adjust(bottom=0.34)
    for ax in axes:
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    fig.suptitle("Condition 3 of the same test: have the aircraft themselves become more alike?",
                 x=0.01, y=1.04, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; the Gower distance fixed in Preliminary Analysis 5.3, imported from "
                 "its code; Q is Rao's quadratic entropy (5.5); numbers in Table 1.1.3.3c; 200 permutations.",
                 "(i) Q is the distance between two aircraft of the window picked blind: high means the "
                 "window holds aircraft far apart in form. The dotted line is the level of the two earliest "
                 "windows, which is what condition 3 asks a later window to fall below. (ii) and (iii): the "
                 "fall itself, against the band produced by shuffling which window each aircraft belongs to; "
                 "a ringed point is a window whose aircraft are more alike than that shuffling ever makes "
                 "them. The hatched window is still incomplete.")


def fig_class_configs(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.class_configs(v)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.4), gridspec_kw={"wspace": 0.3})
    x = np.arange(len(WINDOW_NAMES))
    for code, sub in t.groupby("code", sort=False):
        sub = sub.set_index("window").reindex(WINDOW_NAMES)
        _class_line(ax, x, sub["share in it"], sub["aircraft"], code)
        _class_line(ax2, x, sub["distinct configurations"] / sub["aircraft"], sub["aircraft"], code)
    for a in (ax, ax2):
        a.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7.5)
        a.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(a, "y")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 0.5)
    ax.set_ylabel("% of the class's aircraft")
    ax.set_title("Share of the class in its single most\ncommon configuration", fontsize=9)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("per aircraft of the class")
    ax2.set_title("Distinct configurations\nper aircraft", fontsize=9)
    _class_legend(fig, t, ncol=3, y=-0.02)
    fig.subplots_adjust(bottom=0.24)
    # every line must stay under TEXT_W * 0.98 or _wrap_to flattens the whole suptitle and re-wraps it wider
    fig.suptitle("Within-class convergence: does a class settle on one configuration?\n"
                 "a configuration = propulsive units (banded) · ducted or open · booms or none · tail type",
                 x=0.01, y=1.06, ha="left", fontsize=9.5, fontweight="bold")
    return _save(fig, path, SRC + "; Table 1.1.4 names the most common configuration per class and window; "
                 "windows with fewer than 5 aircraft of the class are left blank.",
                 "A line is an architecture class (the G1 top type), not an archetype; every point counts unique aircraft. "
                 "A configuration is one aircraft's combination of four label fields: propulsive units banded "
                 "(1-3 / 4 / 5-6 / 7-8 / 9+), ducted or open, booms or no booms, tail type. (i) the share of the class's "
                 "aircraft holding the one configuration most of them share — the most common, not an average, because a "
                 "configuration is a combination of categories and so has no mean; a class settling on one design climbs. "
                 "(ii) distinct configurations divided by aircraft: 1.0 means every aircraft is its own configuration, a "
                 "falling line means designs repeat. " + _selection_line(t))


def fig_dimension_drift(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.dimension_drift(v)
    # a panel title line wider than its own panel overflows into the neighbour (the house
    # wrapper measures the room to the right, but a title is centred), so keep the lines short
    # the four fields of the 1.1.4 configuration, one per panel, then powertrain. The last one
    # counts on its own base ("not stated" excluded), so it names that base in its own title.
    metrics_ = [("median propulsive units", "median\npropulsive units", None, "aircraft"),
                ("share with a ducted unit", "% with\nducted units", 1, "aircraft"),
                ("share with no tail surface", "% with no\ntail surface", 1, "aircraft"),
                ("share with booms", "% with booms", 1, "aircraft"),
                ("share electric only", "% electric-only,\nof those stated", 1, "powertrain stated")]
    # five panels do not hold across a 7 in page: the titles crowd and (v) runs off the edge.
    # Two rows of three, with the class key in the free sixth cell.
    fig, axgrid = plt.subplots(2, 3, figsize=(W * 0.92, 4.6), gridspec_kw={"wspace": 0.34, "hspace": 0.75})
    axes = list(axgrid.flat)
    key_ax = axes[5]
    key_ax.axis("off")
    x = np.arange(len(WINDOW_NAMES))
    for ax, (col, title, top, base) in zip(axes, metrics_):
        for code, sub in t.groupby("code", sort=False):
            sub = sub.set_index("window").reindex(WINDOW_NAMES)
            _class_line(ax, x, sub[col], sub[base], code, lw=1.8, ms=4)
        ax.set_title(title, fontsize=7.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        if top:
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        else:
            ax.set_ylim(0)
            # a count of units: whole numbers only, never 2.5 propulsive units
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=5))
        _hgrid(ax, "y")
    # the class key sits in the free sixth cell instead of under the figure
    names = dict(zip(t["code"], t["class"]))
    key_ax.legend(handles=[matplotlib.lines.Line2D([], [], color=_color(c), ls=_cs(c)[1], marker=_cs(c)[0],
                                                   ms=5, lw=2, label=f"{names[c]} ({c})")
                           for c in dict.fromkeys(t["code"])],
                  fontsize=7.5, loc="center left", frameon=False, handlelength=2.2, labelspacing=0.9,
                  borderaxespad=0.0)
    # every line must stay under TEXT_W * 0.98 or _wrap_to flattens the whole suptitle and re-wraps it wider
    stated, total = int(t["powertrain stated"].sum()), int(t["aircraft"].sum())
    fig.suptitle("Dimension drift inside each class: panels (i)–(iv) are the four fields the configuration\n"
                 "of Figure 1.1.4 is made of, read one at a time, then powertrain",
                 x=0.01, y=1.10, ha="left", fontsize=9.5, fontweight="bold")
    return _save(fig, path, SRC + "; Table 1.1.5, where a window with fewer than 5 aircraft of the class keeps its "
                 "row and its count and only its measures are blank.",
                 "A line is an architecture class (the G1 top type), not an archetype; every point counts unique aircraft. "
                 "Panels (i)–(iv) take the configuration of Figure 1.1.4 apart, one field per panel, so the two figures "
                 "read together. Their percentages divide by the class's own aircraft in that window (the `aircraft` "
                 "column of Table 1.1.5, every one of them answered) — never by a count of rotors. Panel (v) is the one "
                 f"exception and does not share that base: a patent that never states a powertrain is excluded, so it "
                 f"divides by the smaller `powertrain stated` column ({stated} of the {total} aircraft drawn here), and a "
                 "cell resting on fewer than 5 stated powertrains is left blank. Substitution shows here before a class "
                 "label changes: a class "
                 "whose propulsive-unit count climbs, or whose ducted share falls, is changing what it is while keeping "
                 "its name. Tilting is not drawn because it is flat by construction — Tilt Rotor, Combined vectored thrust "
                 "and Tilt Wing carry tilting units by definition of the class and Lift + Cruise carries none; its column "
                 "stays in Table 1.1.5, where the two points off 100 % (CVT 0.93 in 2016-19, TR 0.98 in 2020-23) are an "
                 "internal check on the labelling. " + _selection_line(t))


def fig_transitions(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.transitions(v)
    t["from"] = t["from"].map(_fold); t["to"] = t["to"].map(_fold)
    order = [c for c in ARCH_ORDER + ["Other"]]
    mat = t.groupby(["from", "to"])["pairs"].sum().unstack(fill_value=0).reindex(index=order, columns=order, fill_value=0)
    share = mat.div(mat.sum(axis=1).replace(0, np.nan), axis=0)
    fig, (ax, axp) = plt.subplots(1, 2, figsize=(W, 4.6), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.45})
    _heat(ax, share.fillna(0), counts=mat, vmax=1.0)
    ax.set_xticks(range(len(order)), order, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(order)), [f"{c}  ({int(mat.loc[c].sum())})" for c in order], fontsize=8)
    ax.set_xlabel("class of the firm's NEXT aircraft")
    ax.set_ylabel("class of the EARLIER aircraft (pairs)")
    ax.set_title("Every pair of aircraft a firm filed one after the other", fontsize=8.8)
    # (ii) the same matrix read as one number per class: does a firm repeat the class or leave it?
    # The author could not read the matrix; this panel is the sentence the matrix is making
    # (author, 2026-09-23).
    rowsum = mat.sum(axis=1)
    keep = [c for c in order if rowsum[c] >= 5]
    stay = pd.Series({c: float(mat.loc[c, c]) / rowsum[c] for c in keep})
    stay = stay.sort_values()
    yq = np.arange(len(stay))
    for yi, c in zip(yq, stay.index):
        axp.barh(yi, stay[c], height=0.62, color=_color(c), edgecolor=SURFACE, lw=0.7, zorder=3)
        off = mat.loc[c].drop(labels=[c])
        dest = off.idxmax() if off.sum() else ""
        axp.text(stay[c] + 0.015, yi, f"{stay[c]:.0%}" + (f" · else mostly → {dest}" if dest else ""),
                 va="center", fontsize=6.8, color=INK)
    axp.axvline(float(t.attrs["same share"]), color=INK, lw=1, ls="--")
    axp.text(float(t.attrs["same share"]) + 0.01, len(stay) - 0.3,
             f"all classes {t.attrs['same share']:.0%}", fontsize=6.8, color=INK2, va="top")
    axp.set_yticks(yq, [f"{c} ({int(rowsum[c])})" for c in stay.index], fontsize=7.5)
    axp.set_xlim(0, 1.0)
    axp.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axp.set_xlabel("share of the pairs that stay in the class")
    axp.set_title("Does a firm repeat the class it just filed?", fontsize=8.8)
    axp.spines[["left"]].set_visible(False)
    _hgrid(axp, "x")
    return _save(fig, path, SRC + f"; each named firm's aircraft in priority order, every consecutive pair counted "
                 f"once; {t.attrs['pairs']} pairs from the {t.attrs['firms']} named firms that hold two or more "
                 f"aircraft (the 30 firms with one aircraft make no pair).",
                 "A pair is one firm's aircraft and the next aircraft the same firm filed, ordered by priority year; "
                 "a firm with k aircraft makes k − 1 pairs, so the unit here is the succession, not the aircraft and "
                 "not the patent. (i) rows are the earlier aircraft's class and sum to 100 %, the number in the cell "
                 "is pairs, and the diagonal is a firm repeating itself. (ii) the diagonal read on its own: the share "
                 "of each class's successions that stay in it, with the class most of the leavers go to. It separates "
                 "a class the field is leaving from a class the field never stays in — and read with Figure 1.2.2 it "
                 "says whether a class share moves because the firms inside it change course or because different "
                 "firms arrive.")


def fig_ip_strategy(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    """1.2.5a — depth against breadth, then claims and citations per class.

    Rebuilt 2026-09-23 on the author's review. The bubble area was unexplained: it is the mean number
    of forward citations of the firm's patents and now carries its own size legend, three reference
    bubbles with the count printed inside the panel, so the reader never has to guess. The bottom
    strip is split in two: claims (a median, printed beside the share of the class's patents published
    in the United States, because claim counts are an office convention) and citations read twice —
    the raw mean, which rewards age, and the median cohort rank, which does not.
    """
    f = la_tables.ip_strategy(ds, v)
    c = la_tables.ip_by_class(v, ds)
    fig = plt.figure(figsize=(W, 7.3))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 1], hspace=0.42, wspace=0.42)
    ax = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    bub = lambda cit: 25 + 3 * cit                     # bubble AREA in points²; used by the size legend too
    for _, r in f.iterrows():
        ax.scatter(r["unique aircraft"], r["patents per aircraft"], s=bub(r["mean forward citations"]),
                   color=REGION_COLOR.get(r["region"], OTHER), alpha=0.85, edgecolor=SURFACE, lw=0.8, zorder=3,
                   marker={"North America": "o", "Europe": "s", "Asia-Pacific": "^"}.get(r["region"], "o"))
    ax.set_xscale("log")
    ax.set_xticks([5, 10, 20, 50], ["5", "10", "20", "50"])
    ax.set_xlabel("unique aircraft (log)")
    ax.set_ylabel("representative patents per aircraft")
    ax.axhline(1, color=GRID, lw=1)
    ax.set_title("Depth against breadth, firms with 5+ aircraft", fontsize=9)
    _hgrid(ax, "both")
    handles = [matplotlib.lines.Line2D([], [], ls="", marker=m_, ms=7, color=REGION_COLOR[r_], label=r_)
               for r_, m_ in zip(REGIONS, ("o", "s", "^"))]
    ax.legend(handles=handles, fontsize=7.5, loc="upper right", ncol=1, title="shape and colour = region",
              title_fontsize=7.5)
    ax.set_xlim(4, 160)
    ax.set_ylim(0.05, 4.6)                      # head room for the size key, foot room for the biggest bubble
    _repel(ax, f["unique aircraft"].tolist(), f["patents per aircraft"].tolist(), f["firm"].tolist(), marker_pt=8)
    # the size legend: what the bubbles mean, said once, inside the panel
    sizes = [10, 40, 100]
    size_h = [matplotlib.lines.Line2D([], [], ls="", marker="o", color=INK2, alpha=0.7,
                                      markersize=float(np.sqrt(bub(s_))), label=f"{s_}") for s_ in sizes]
    lg = ax.legend(handles=size_h, fontsize=7.5, loc="upper left", ncol=3, frameon=True, framealpha=0.95,
                   handletextpad=0.4, columnspacing=1.1, borderpad=0.6, labelspacing=0.9,
                   title="BUBBLE SIZE = mean forward citations of the firm's patents", title_fontsize=7.5)
    lg.get_title().set_fontweight("bold")
    ax.add_artist(lg)
    ax.legend(handles=handles, fontsize=7.5, loc="upper right", ncol=1, title="shape and colour = region",
              title_fontsize=7.5)
    cc = c[c["patents"] >= 10]
    y = np.arange(len(cc))
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == n), n) for n in cc["class"]]
    ticks = [f"{code} ({int(n)})" for code, n in zip(codes, cc["patents"])]
    ax2.barh(y, cc["median claims"], height=0.6, color=BLUE(0.45))
    for yi, (cl, us) in zip(y, zip(cc["median claims"], cc["US share"])):
        ax2.text(cl + 0.4, yi, f"{cl:g}   ·   {us:.0%} US", va="center", fontsize=7, color=INK2)
    ax2.set_xlim(0, float(cc["median claims"].max()) * 1.9)
    ax2.set_yticks(y, ticks, fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_xlabel("median claims", fontsize=8)
    ax2.set_title("Median claims, and the class's US share", fontsize=8.8)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    ax3.axvline(0.5, color=INK2, lw=1, ls="--", zorder=2)
    ax3.barh(y, cc["median cohort citation rank"], height=0.6, color=BLUE(0.85), zorder=3)
    for yi, (rk, mn) in zip(y, zip(cc["median cohort citation rank"], cc["mean forward citations"])):
        ax3.text(rk + 0.02, yi, f"{rk:.2f}   ·   raw mean {mn:.0f}", va="center", fontsize=7, color=INK2)
    ax3.set_xlim(0, 1.5)
    ax3.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "", "0.5", "", "1"])
    ax3.set_yticks(y, ticks, fontsize=7.5)
    ax3.invert_yaxis()
    ax3.set_xlabel("median cohort citation rank (0.5 = the median patent of its own year)", fontsize=7.5)
    ax3.set_title("Citations with age taken out", fontsize=8.8)
    ax3.spines[["left"]].set_visible(False)
    _hgrid(ax3, "x")
    return _save(fig, path, SRC + "; PatSeer claim_count, forward_citations, family_size; Tables 1.2.5a/b. "
                 + la_tables.CITE_AGE_NOTE + ".",
                 "(i) The bubble is the only citation reading on this panel and its area is the firm's mean forward "
                 "citations — the key at the top left gives three reference sizes. Above the grey line a firm files "
                 "more than one patent per aircraft (protecting each design in depth); far to the right it files many "
                 "different aircraft (exploring). (ii) Median claims, with the share of the class's patents published "
                 "in the United States beside it: a class with a high median claim count is usually a class that files "
                 "in America, where the corpus median is 20 claims against 10 in China. (iii) The same classes ranked "
                 "by citations with age removed — each patent ranked against the patents of its own priority year, "
                 "then the class median. A bar past the dashed line is a class cited more than the typical patent of "
                 "its years; the raw mean is printed beside it, and where the two disagree the class is old, not "
                 "influential.")


#: Below this many aircraft an archetype's location quotient is drawn hollow and greyed: with a
#: dozen machines split three ways the index moves by a full point on chance alone, so the row is
#: shown but must not be read as a lean (author, 2026-09-23, on percentages of small cells).
SPEC_THIN = 10


def fig_specialisation(v: pd.DataFrame, path: Path) -> Path:
    """1.3.3 as a coloured dot chart, one row per archetype, one dot per region.

    It was a two-strip log-ratio heat map and the author could not read a takeaway out of it
    ("I NEED TO SEE IT WITH COLORS", 2026-09-23). The colour now carries the region — the same three
    hues the rest of the document uses for regions — and the rows are grouped by which region leads
    them, so the three blocks are visible before any number is read. Black-and-white printing is
    kept by the marker shapes (circle / square / triangle, :data:`REGION_STYLE`), which carry the
    region on their own, and by the position on the axis, which carries the value.
    """
    lq, counts = la_tables.specialisation(v)
    tot = counts.sum(axis=1)
    lead = lq.idxmax(axis=1)
    # group by the region that leads the archetype, strongest lean first inside each group
    order, groups = [], []
    for reg in REGIONS:
        rows = lq.index[lead.eq(reg)]
        rows = sorted(rows, key=lambda a: -float(lq.loc[a, reg]))
        if rows:
            groups.append((reg, len(order), len(order) + len(rows)))
            order += list(rows)
    lq, counts, tot = lq.loc[order], counts.loc[order], tot.loc[order]

    fig, ax = plt.subplots(figsize=(W, 0.168 * len(order) + 1.25))
    y = np.arange(len(order))
    lo, hi = 0.25, 4.0
    for yi, arch in enumerate(order):
        vals = lq.loc[arch].clip(lo, hi)
        ax.plot([np.log2(vals.min()), np.log2(vals.max())], [yi, yi], color=GRID, lw=3.0, zorder=1,
                solid_capstyle="round")
    for reg in REGIONS:
        mark = REGION_STYLE.get(reg, ("o", "-"))[0]
        col = REGION_COLOR[reg]
        xs = np.log2(lq[reg].clip(lo, hi).to_numpy(dtype=float))
        thin = (tot < SPEC_THIN).to_numpy()
        ax.scatter(xs[~thin], y[~thin], marker=mark, s=26, color=col, edgecolor=SURFACE, lw=0.5,
                   zorder=3, label=reg)
        ax.scatter(xs[thin], y[thin], marker=mark, s=26, facecolor="none", edgecolor=col, lw=0.9,
                   zorder=3)
    ax.axvline(0, color=INK, lw=1.0, zorder=2)
    for x_ in (-1, 1):
        ax.axvline(x_, color=GRID, lw=0.8, ls=(0, (3, 3)), zorder=0)
    for reg, a_, b_ in groups:                       # a band and a name per lead-region block
        band = tuple(1 - 0.09 * (1 - c_) for c_ in matplotlib.colors.to_rgb(REGION_COLOR[reg]))
        ax.axhspan(a_ - 0.5, b_ - 0.5, color=band, zorder=-2)
        if b_ - a_ >= 2:
            ax.text(np.log2(hi) * 0.99, (a_ + b_ - 1) / 2, f"leans {reg}", rotation=90, fontsize=7.5,
                    ha="right", va="center", color=REGION_COLOR[reg], fontweight="bold")
        if a_:
            ax.axhline(a_ - 0.5, color=INK2, lw=0.6)
    labels = [f"{a.replace(' · ', ' ').replace(' n/a (no M3 card)', ' (no card)')}  ({int(tot[a])})"
              for a in order]
    ax.set_yticks(y, labels, fontsize=7)
    for tick, arch in zip(ax.get_yticklabels(), order):
        if tot[arch] < SPEC_THIN:
            tick.set_color(INK2)
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_xlim(np.log2(lo) * 1.04, np.log2(hi) * 1.04)
    ax.set_xticks([-2, -1, 0, 1, 2], ["¼ ×", "½ ×", "1 ×", "2 ×", "4 ×"], fontsize=7.5)
    ax.set_xlabel("archetype's share of the region ÷ its share of all three regions", fontsize=8)
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.055), ncol=3,
              handlelength=1.0, columnspacing=1.6, frameon=False)
    ax.set_title("Regional specialisation by archetype (A0c): left of the line the region files this "
                 "archetype less than average, right of it more", fontsize=9)
    fig.subplots_adjust(left=0.185, right=0.985)      # the rows use the page, not two thirds of it
    # Black-and-white pass off on purpose: nothing here is a filled category. The region is carried
    # by the marker shape (circle / square / triangle) and the value by the position on the axis, so
    # the figure reads without colour; left on, the pass hatches the three lead-region bands and they
    # start to look like a fourth variable.
    fig._bw_off = True

    # the takeaway, read out of the frame rather than typed. Only archetypes big enough for the index
    # to mean something are eligible, so the sentence cannot be built on a ten-aircraft cell.
    bits = []
    for reg in REGIONS:
        for floor in (20, SPEC_THIN):
            cand = lq.loc[(tot >= floor) & lead.reindex(lq.index).eq(reg), reg]
            if len(cand):
                a_ = cand.idxmax()
                bits.append(f"{reg} to {a_.replace(' · ', ' ')} ({cand.max():.1f}×, {int(tot[a_])} aircraft)")
                break
    med = float(tot.median())
    big = tot.idxmax()
    big_txt = (f"The row that carries the most weight is the corpus's largest archetype, "
               f"{big.replace(' · ', ' ')} ({int(tot[big])} aircraft): "
               + ", ".join(f"{r} {lq.loc[big, r]:.1f}×" for r in REGIONS) + ". ")
    return _save(fig, path,
                 SRC + f"; A0c archetypes with at least 5 aircraft (n {len(order)}); three main applicant "
                       f"regions only; per-cell counts in tables/la_specialisation.csv.",
                 "One row per archetype, one dot per region; the dot's position is the location quotient — "
                 "how much of that region's output the archetype takes, against how much of all three "
                 "regions' output it takes. On the line the region files it exactly as everywhere; right of "
                 "the line more, left of it less. Rows are grouped by the region that leads them, so the "
                 "three colour blocks are the answer at a glance. "
                 + ("Takeaway: each region's strongest lean among the archetypes big enough to read is "
                    + "; ".join(bits) + ". " if bits else "")
                 + big_txt
                 + f"A hollow marker is an archetype of fewer than {SPEC_THIN} aircraft — the median "
                   f"archetype here holds {med:.0f}, and at that size the index swings by a full point on "
                   "chance alone, so only the filled rows with a clear lead carry a finding.")

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
    return _save(fig, path,
                 SRC + "; identity industry_primary — one value per patent from the Stage 03a text "
                       "classifier over the patent's own text, not from the label cards and not "
                       "checked by hand; counts in tables/la_industry_by_class.csv.",
                 "Each bar is 100 % of the class's aircraft. Grey is 'general / unspecified', half the corpus: patents "
                 "rarely name a mission. Read the coloured part only, and read it as what the classifier found in the "
                 "text rather than as what the aircraft is for: the author's ruling of 2026-09-23 is that this field "
                 "is not verified, which is why its table was cut and only the shape is kept.")


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
    return _save(fig, path, SRC + "; PatSeer legal_status_raw at the 2026-06 snapshot; Tables 2.6a/b.",
                 "Examination outcome as a proxy for regulatory friction on the IP side: refused and withdrawn shares "
                 "differ by office far more than by class. Pending is high where filings are recent (CN, WO).")


# ------------------------------------------- Appendix A and B.1, compact (2026-09-22, 4th round)
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
    # 2026-09-22: one percentage per bar. Only two tags reach the gate, so printing the
    # UAV-similar share fixes the Electric-similar one as its complement (TB is 100 % UAV).
    share_tag = "UAVSimilar" if "UAVSimilar" in tab.columns else str(tab.columns[0])
    for col in tab.columns:
        lab = col.replace("Similar", "-similar") + (" (% shown)" if col == share_tag else "")
        ax2.bar(xx, tab[col], bottom=bottom, color=tagc.get(col, OTHER), width=0.66, edgecolor=SURFACE, lw=0.8,
                label=lab)
        bottom += tab[col].to_numpy()
    share = (tab[share_tag] / tab.sum(axis=1)).to_numpy()
    for xi, t, sh in zip(xx, bottom, share):
        ax2.text(xi, t, f"{t:.0f}\n{sh:.0%}", ha="center", va="bottom", fontsize=7, linespacing=1.3)
    ax2.set_xticks(xx, [("Oth." if c == "Other" else c) for c in tab.index], fontsize=7)
    ax2.set_ylim(0, bottom.max() * 1.46)   # room for the two-line bar label under the legend
    ax2.set_title(f"Aircraft removed by the gate ({int(tab.values.sum())}), by class", fontsize=9)
    ax2.legend(fontsize=7, loc="upper right")
    _hgrid(ax2, "y")
    return _save(fig, path, SRC + "; wizard disapproval reasons and the Similar tags (Table A.1a); class codes as Figure D.1a.",
                 "Left: patents by the reason they left, plain at labelling, hatched by the domain gate. Right: the unique "
                 "aircraft the gate removed, by the class they were labelled with; above each bar its total and, under the "
                 f"total, the share of that bar tagged {share_tag.replace('Similar', '-similar')}" +
                 (" — the rest of the bar is the other tag, so one share gives both."
                  if len(tab.columns) == 2 else " (the remaining share is spread over the other tags)."))


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
    return _save(fig, path, SRC + "; Tables A.2a/b.",
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
    return _save(fig, path, SRC + "; Table A.3; whole-aircraft figures only.",
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
    return _save(fig, path, SRC + "; Table B.1; a value an override hides is left out of the base.",
                 "One bar per field. A wing field is measured on the winged aircraft, a boom field on the aircraft with "
                 "booms, so a blank means a missing answer, not a missing part. Every field is at or above the dashed "
                 "95 % line. The axis starts at 80 %.")


# ------------------------------------------------------- reuse of atlas ----
#: atlas figures reused as they are: name -> atlas function
ATLAS_REUSE: Dict[str, Callable] = {
    # parked 2026-09-22: superseded by Figure 1.1.1 (filings_per_year) and placed in no node, so it was
    # drawn on every run and never printed. Un-comment to draw it again, and put it back in la_index.NODES.
    # "atlas_years": atlas.fig_years,
    "atlas_region": atlas.fig_region,
    "atlas_filers": atlas.fig_filers,
    "atlas_state_by_arch": atlas.fig_state_by_arch,
    "atlas_arch_gt": atlas.fig_arch_gt,
    "atlas_arch_time": atlas.fig_arch_time,
    "atlas_powertrain": atlas.fig_powertrain,
    "atlas_fields": atlas.fig_fields,
    "atlas_flagship": atlas.fig_flagship,
}


#: classes a reused atlas figure must show on their own instead of folding into "Other".
#: User rulings: the rotorcraft must be visible in Figure 1.1.2 (2026-09-22), and the hoverbikes and
#: the personal flying vehicles too (2026-09-23). SRW and DS stay inside "Other" by the author's choice,
#: so "Other" is now those two classes only.
#: {figure name: {class code: colour}}. Every colour must be one the black-and-white pass knows:
#: ``CAT[7]`` is the one categorical hue the seven fixed classes leave free, and the other two are
#: listed in :data:`EXTRA_CLASS_BW`. Never ``OTHER``. The order is the order of the bands in the stack,
#: chosen so that no two neighbouring bands print as the same grey (see the note on EXTRA_CLASS_BW).
ATLAS_EXTRA_CLASSES: Dict[str, Dict[str, str]] = {
    "atlas_arch_time": {"RC": CAT[7], "HB": "#111827", "PFV": "#7a5c3e"},
}

#: graphs of a reused atlas figure the Labelling Analysis does not print: {figure name: axes indices},
#: in the order the atlas function draws them. The drop happens after the shared function has returned,
#: so ``atlas.py`` is untouched and the Preliminary Analysis keeps both graphs.
#: User ruling 2026-09-22: Figure B.5 keeps only "label depth by architecture" (the dot cloud of every
#: coded column goes), Figure B.6 only the agreement / confusion heatmap (the class bars go).
ATLAS_DROP: Dict[str, List[int]] = {
    "atlas_fields": [0],       # "Every coded export column, by kind" — the scatter
    "atlas_arch_gt": [0],      # "Architecture classes: N unique aircraft" — the paired bars
}

#: Source and How-to-read lines for the figures :data:`ATLAS_DROP` cuts down: the shared atlas text
#: describes both graphs, so it cannot be reused. ``(source, read)``, the shape :func:`atlas._note` sets;
#: ``{}`` fields are filled from the live numbers when the figure is drawn.
ATLAS_NOTE: Dict[str, tuple] = {
    "atlas_fields": (
        "{src}; the slots are the rows of the dimension register "
        "(assets/codebook/dimension_register.csv, the drawing of the codebook dimensions figure); "
        "{aircraft} unique aircraft.",
        "How many of the {questions} slots each aircraft answers, one box per class. A slot is answered when "
        "any of its columns holds a value, and an unticked box on a card that exists is an answer. The box "
        "spans the quartiles, the line in it is the median, the dots beyond the whiskers are single aircraft."),
    "atlas_arch_gt": (
        "{src}; architecture_ground_truth.csv (the whole-patent reading) against the label frozen from the "
        "figures alone, over the {gt} of {aircraft} unique aircraft that carry a class on both sides. The "
        "{dropped} aircraft the matrix cannot hold are named in the table of section B.3: one whose patent "
        "states no class, and two the wizard left unlabelled, one of them read as 'Convertiplane' — outside "
        "the twelve classes. None of the three was relabelled to fit.",
        "Each row is a ground-truth class and sums to 100 %; the number in a cell is aircraft, and the count "
        "after the row name is the class total. The diagonal is agreement; everything off it is an aircraft "
        "the drawing alone reads as a different class from the whole patent."),
}

#: ISO 3166-1 alpha-2 written out. The author read the country axis of Figure 1.3.1 and did not
#: recognise "IL" (2026-09-23), so every code on that axis is spelled out; the code is kept beside
#: the name because the rest of the document indexes countries by it. Covers every code the identity
#: record holds, so a change of the top-12 cut cannot silently reintroduce a bare code.
COUNTRY_NAMES: Dict[str, str] = {
    "AT": "Austria", "AU": "Australia", "BR": "Brazil", "CA": "Canada", "CH": "Switzerland",
    "CN": "China", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "DZ": "Algeria",
    "ES": "Spain", "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece",
    "HR": "Croatia", "IL": "Israel", "IN": "India", "IR": "Iran", "IT": "Italy", "JP": "Japan",
    "KR": "South Korea", "LT": "Lithuania", "MY": "Malaysia", "NL": "Netherlands", "NO": "Norway",
    "PH": "Philippines", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "RU": "Russia",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Türkiye", "TW": "Taiwan",
    "UA": "Ukraine", "US": "United States", "VN": "Vietnam", "ZA": "South Africa",
}


def _country_name(code) -> str:
    c = "" if code is None or (isinstance(code, float) and np.isnan(code)) else str(code).strip()
    if not c or c in ("?", "nan"):
        return "not recorded"
    return f"{COUNTRY_NAMES[c]} ({c})" if c in COUNTRY_NAMES else c


def _post_region(fig, ds: Dataset) -> None:
    """Figure 1.3.1, left panel: spell the country codes out and print each country's share of the
    analysis set beside its bar.

    The atlas draws the panel with bare ISO codes and prints "kept / acquired (rate)", which answers
    "how many of this country's patents survived" but not "how much of the study is this country".
    The author asked for the second on 2026-09-23 ("that would give me the representativeness of the
    study in each region — because if there are just a few it can be not represented"), so the share
    of the representative patents is appended here. The atlas function itself is untouched and the
    Preliminary Analysis keeps the panel as it was.
    """
    c = a1.provenance_tables(ds, top_offices=12)["assignee_country"].sort_values("patents")
    rep_total = int(ds.patents["is_representative"].fillna(False).astype(bool).sum())
    ax = _drawn_axes(fig)[0]
    ax.set_yticks(np.arange(len(c)), [_country_name(x) for x in c["assignee_country"]])
    texts = sorted([t for t in ax.texts if "/" in t.get_text()], key=lambda t: t.get_position()[1])
    for t, (_, r) in zip(texts, c.iterrows()):
        share = r["representative"] / rep_total if rep_total else float("nan")
        # kept short on purpose: the legend of this panel sits in its lower-right corner and a long
        # annotation on the two smallest countries runs straight through it
        t.set_text(f"  {r['representative']:.0f}/{r['patents']:.0f} · {share:.1%}")
        t.set_fontsize(7.5)
    ax.set_xlim(0, float(c["patents"].max()) * 1.62)
    # The key goes in the figure's own Source / How-to-read stamp, which this atlas figure did not
    # carry at all: a longer title is re-flattened by the width pass and runs into the right panel's
    # title, and an x label lands under the class legend.
    covered = float(c["representative"].sum()) / rep_total if rep_total else float("nan")
    fig._atlas_note = (
        f"{atlas.TABLES_SRC}; applicant country of the patent's identity record, twelve largest by "
        f"acquired patents ({covered:.0%} of the {rep_total} representative patents; the rest are in "
        f"(ii) under 'Other regions').",
        "(i) one row per applicant country: the pale bar is every patent acquired from it, the dark "
        f"bar the representative ones, and the label reads representative / acquired, then that "
        f"country's share of the whole analysis set. That last number is the one to read for "
        f"representativeness — a country holding under about 2 % of the set cannot carry a finding of "
        f"its own. (ii) one row per region, each 100 % of its own aircraft.")


#: the three classes whose propulsors move — the split Figure 2.4 turns out to measure
TILTING_CLASSES = ("TR", "CVT", "TW")


def _post_state_by_arch(fig, ds: Dataset) -> None:
    """Figure 2.4: say what the flight state is actually evidence of.

    The author asked why the figure is needed at all (2026-09-23). The answer is not a design
    finding: it is that the state drawn is very nearly a restatement of whether the design has a
    moving part, which is a warning for anything trained on these images. The sentence is computed
    here so it cannot drift from the data.
    """
    note = getattr(fig, "_atlas_note", None)
    if not note:
        return
    try:
        f = ds.approved_figures.merge(
            ds.variants[["patent_id", "variant", "topType"]].rename(columns={"variant": "arch"}),
            on=["patent_id", "arch"], how="left")
        committed = f["acState"].isin(["Hover", "Cruise", "Transition", "Both"])
        tilt = f["topType"].isin(TILTING_CLASSES)
        a = float(committed[tilt].mean()) if tilt.any() else float("nan")
        b = float(committed[~tilt].mean()) if (~tilt).any() else float("nan")
    except Exception:
        return
    extra = (f" What this figure is evidence of: the state drawn is close to a restatement of "
             f"whether the design has a moving part. {a:.0%} of the figures of the tilting classes "
             f"({', '.join(TILTING_CLASSES)}) commit to a configuration — hover, cruise, transition "
             f"or both — against {b:.0%} of every other class, which is drawn Invariant because "
             f"nothing in the drawing depends on the configuration. Read it as a check on the "
             f"labelling and as a warning for the image side: a model can reach the "
             f"tilting / non-tilting split from the pose alone, without reading the airframe. It is "
             f"not a statement about the aircraft, which is why it sits at the end of the document.")
    fig._atlas_note = (note[0], note[1] + extra)


#: Post-processing a reused atlas figure gets only in this document: ``{figure name: fn(fig, ds)}``,
#: run after the shared function has returned and before the black-and-white pass, so ``atlas.py``
#: is untouched and the Preliminary Analysis renders exactly as before (same contract as
#: :data:`ATLAS_DROP` and :data:`ATLAS_NOTE`).
ATLAS_POST: Dict[str, Callable] = {"atlas_region": _post_region,
                                   "atlas_state_by_arch": _post_state_by_arch}


def _drop_panels(fig, idx: List[int]) -> None:
    """Remove the graphs of a shared atlas figure this document does not print, then give the canvas
    to the one that stays.

    ``idx`` indexes ``fig.axes`` in drawing order. Whatever survives is re-seated on a fresh 1 × 1
    grid, so the figure is a full-width single panel and not a half-empty page; the later
    ``_fit_width`` / ``_clear_panels`` pass then settles it as it would any one-graph figure.
    """
    axes = list(fig.axes)
    for k in sorted({i for i in idx if 0 <= i < len(axes)}, reverse=True):
        fig.delaxes(axes[k])
    left = [a for a in fig.axes if getattr(a, "get_subplotspec", None) and a.get_subplotspec() is not None]
    if len(left) == 1:
        ss = fig.add_gridspec(1, 1)[0]
        left[0].set_subplotspec(ss)
        left[0].set_position(ss.get_position(fig))
        for loc in ("left", "center"):        # a title wrapped for half the page has the whole page now
            t = left[0].get_title(loc=loc)
            if "\n" in t:                     # _wrap_texts puts the break back if it still does not fit
                left[0].set_title(t.replace("\n", " "), loc=loc)


#: portrait sizes for the reused atlas figures (they are drawn at ``atlas.PAGE``, patched per call)
ATLAS_SIZE: Dict[str, tuple] = {
    "atlas_removal": (W, 4.4), "atlas_duplicates": (W, 3.8), "atlas_figure_approval": (W, 4.4),
    "atlas_years": (W, 4.0), "atlas_region": (W, 4.8), "atlas_filers": (W, 6.2), "atlas_state_by_arch": (W, 4.4),
    "atlas_arch_gt": (W, 5.6), "atlas_arch_time": (W, 4.0), "atlas_powertrain": (W, 4.6), "atlas_fields": (W, 4.8),
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
    return _save(fig, path, SRC + "; archetype_frame (boom bin, any tilting unit); class codes as Figure D.1a.",
                 "Each row is one class and sums to 100 % across a panel's columns. n/d = not determinable, a value "
                 "an override hides; 'no M3 card' marks HB and PFV, which have no propulsor card. Blank = design "
                 "absence. Some rows are true by definition rather than by measurement: a Hoverbike has no wing, no "
                 "tail and no boom, and Pitch-to-Cruise answers several panels the same way for the same reason, so "
                 "those rows carry nothing on those panels. They are kept here so every class of the corpus is on "
                 "the page and the denominators match the rest of the document; the author's ruling of 2026-09-23 "
                 "is that they come out of the thesis version of this figure.")


def fig_units(ds: Dataset, av: pd.DataFrame, path: Path, base_v: Optional[pd.DataFrame] = None) -> Path:
    """The atlas propulsion figure stacked for a portrait page: units per class on top, shares
    below, and ducting against rotor count at the foot.

    Panel (iii) was added 2026-09-23. The author asked of Figure 1.3.2b whether ducting
    correlates with anything; it does not correlate with region or with time, which is why it
    left that figure, but it correlates strongly with the number of propulsive units — and this
    is the section that owns the number of propulsive units, so the finding is drawn here.
    """
    v = av
    order = [c for c in atlas.ALL_ARCH if c in v["atype"].values]
    fig = plt.figure(figsize=(W, 8.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.25, 1, 0.68], hspace=0.62)
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
    ax.set_ylabel("propulsive units (capped at 30)", fontsize=7.5)
    # The author asked why quartiles and a median rather than an average (2026-09-23). The answer is
    # a property of this variable, so it is stated on the panel and the numbers behind it are read
    # from the data, never typed.
    _u_all = pd.to_numeric(v["units"], errors="coerce").dropna()
    why_median = (f"Quartiles and a median, not an average: the count is a whole number and the "
                  f"distribution has a long tail — mean {_u_all.mean():.1f} against a median of "
                  f"{_u_all.median():.0f}, longest {int(_u_all.max())} — so a mean lands between two "
                  f"real machines and describes none of them.")
    ax.set_title("Propulsive units per class: dot = one aircraft, bar = middle half of the class, "
                 "ring = median", fontsize=9)
    # why_median is printed as the first sentence of the How-to-read line under the figure rather
    # than inside the panel: an in-axes note at this width collides with the panel mark and title
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

    # ---- (iii) ducting against rotor count ----------------------------------
    # The shape is the finding, so the panel is built to show one: a point per band in band order,
    # joined, against the flat line of the whole corpus. The frame comes from la_tables so the
    # figure and tables/la_duct_units.csv can never disagree. A band resting on fewer than
    # la_tables.DUCT_THIN aircraft is drawn hollow with its own n and the line is broken on both
    # sides of it — the convention of Figure 1.3.2a/b: a thin cell is suppressed visibly, never
    # dropped. Every share here is a share of AIRCRAFT: any_ducted is one answer per aircraft, so
    # one ducted fan among twelve open rotors counts exactly as much as twelve ducted ones.
    ax3 = fig.add_subplot(gs[2])
    dt = la_tables.duct_by_units(base_v if base_v is not None else la_tables.base(ds))
    bands = (dt[dt["level"].eq("propulsive units")].set_index("group")
             .reindex(la_tables.UNIT_BANDS[1]))
    all_row = dt[dt["level"].eq("propulsive units") & dt["group"].eq("all bands")]
    overall = float(all_row["share ducted"].iloc[0]) if len(all_row) else float("nan")
    xs = np.arange(len(bands))
    ys = bands["share ducted"].to_numpy(dtype=float)
    ns = bands["aircraft"].to_numpy(dtype=float)
    ok = bands["reported"].fillna(False).to_numpy(dtype=bool) & np.isfinite(ys)
    for xi, y_, n_, good in zip(xs, ys, ns, ok):
        if not np.isfinite(y_):
            continue
        ax3.bar(xi, y_, width=0.58, color=BLUE(0.30) if good else "none",
                edgecolor=INK if good else INK2, lw=0.9, zorder=2)
        ax3.text(xi, y_ + 0.025, f"{y_:.0%}" + ("" if good else f"\nof {int(n_)}"), ha="center",
                 va="bottom", fontsize=8.5 if good else 7, linespacing=0.95,
                 color=INK if good else INK2, fontweight="bold" if good else "normal", zorder=5)
    seg_x, seg_y = [], []                      # the line never crosses a band it cannot report
    for xi, y_, good in zip(xs, ys, ok):
        if good:
            seg_x.append(xi)
            seg_y.append(y_)
            continue
        if len(seg_x) > 1:
            ax3.plot(seg_x, seg_y, color=INK, lw=1.9, zorder=3)
        seg_x, seg_y = [], []
    if len(seg_x) > 1:
        ax3.plot(seg_x, seg_y, color=INK, lw=1.9, zorder=3)
    ax3.plot(xs[ok], ys[ok], "o", ls="none", ms=6.2, mfc=INK, mec=INK, zorder=4)
    thin_m = np.isfinite(ys) & ~ok
    ax3.plot(xs[thin_m], ys[thin_m], "o", ls="none", ms=6.2, mfc=SURFACE, mec=INK2, mew=1.4, zorder=4)
    if np.isfinite(overall):
        # the reference sits inside the axes: hung off the right edge it is the widest thing in the
        # figure and _fit_width would shrink every panel to make room for it
        ax3.axhline(overall, color=INK2, lw=0.9, ls=(0, (4, 2)), zorder=1)
        # over the dip, where the line has left the space free and no band label can reach it
        ax3.text(1.75, overall + 0.022, f"every band together, {overall:.0%}", ha="left",
                 va="bottom", fontsize=7, color=INK2, zorder=5)
    ax3.set_xticks(xs, [f"{b}\nn {int(n_)}" if np.isfinite(n_) and n_ else f"{b}\nno answer"
                        for b, n_ in zip(bands.index, ns)], fontsize=7.5)
    ax3.set_xlim(-0.6, len(xs) - 0.1)
    ax3.set_ylim(0, float(np.nanmax(ys)) + 0.17 if np.isfinite(ys).any() else 1)
    ax3.set_yticks([0, 0.2, 0.4, 0.6], ["0 %", "20 %", "40 %", "60 %"], fontsize=7.5)
    ax3.set_ylabel("aircraft with a\nducted unit", fontsize=7.5)
    ax3.set_xlabel("propulsive units per aircraft", fontsize=7.5)
    ax3.set_title("Ducting against rotor count: ducts sit at the smallest and the largest counts "
                  "and are rarest in between", fontsize=9)
    _hgrid(ax3, "y")

    fig._bw_off = True
    # the takeaway, read out of the frame
    med_by = {c: float(pd.to_numeric(v.loc[v["atype"].eq(c), "units"], errors="coerce").dropna().median())
              for c in order
              if pd.to_numeric(v.loc[v["atype"].eq(c), "units"], errors="coerce").notna().any()}
    big_n = {c: int(pd.to_numeric(v.loc[v["atype"].eq(c), "units"], errors="coerce").notna().sum()) for c in med_by}
    solid = {c: m for c, m in med_by.items() if big_n[c] >= 20}
    low = min(solid, key=solid.get) if solid else None
    high = max(solid, key=solid.get) if solid else None
    take = ""
    if low and high and low != high:
        take = (f"Takeaway: the classes separate on rotor count, not only on how the rotors move — "
                f"{high} sits at a median of {solid[high]:.0f} units against {solid[low]:.0f} for "
                f"{low}, and {(_u_all > 8).mean():.0%} of all aircraft carry more than eight. The "
                f"long tails are the outliers to name one by one, never to average: they are single "
                f"designs, not a band of the class. ")
    # the duct reading, read out of the same frame the panel is drawn from
    # Kept to the numbers: the design reading of this panel is the document's takeaway line
    # (la_index.TAKEAWAY["atlas_units"]), and saying it twice costs the figure a page of height.
    cls = dt[dt["level"].eq("architecture class") & dt["reported"]].dropna(subset=["share ducted"])
    duct_take = ""
    if len(bands.dropna(subset=["share ducted"])) >= 3:
        hi = bands["share ducted"].idxmax()
        lo = bands["share ducted"].idxmin()
        duct_take = (f"Ducting does not separate the regions (chi-square p = "
                     f"{dt.attrs.get('region', {}).get('p', float('nan')):.2f}) or the windows "
                     f"(p = {dt.attrs.get('window', {}).get('p', float('nan')):.2f}), which is why it "
                     f"is drawn here and not in the region-over-time figure, but it tracks rotor count "
                     f"(p = {dt.attrs.get('band', {}).get('p', float('nan')):.5f}): "
                     f"{bands.loc[lo, 'share ducted']:.0%} of the {lo}-unit aircraft against "
                     f"{bands.loc[hi, 'share ducted']:.0%} of the {hi} ones, corpus {overall:.0%}. ")
        bgc = dt.attrs.get("band_given_class")
        if bgc and np.isfinite(bgc.get("p", float("nan"))):
            duct_take += (f"The band still moves the answer with the class held fixed (likelihood "
                          f"ratio {bgc['chi2']:.1f} on {bgc['dof']} df, p = {bgc['p']:.4f}). ")
        if len(cls) >= 2:
            c_hi, c_lo = cls["share ducted"].idxmax(), cls["share ducted"].idxmin()
            duct_take += (f"By class, panel (ii): {cls.loc[c_hi, 'class']} "
                          f"{cls.loc[c_hi, 'share ducted']:.0%} of {int(cls.loc[c_hi, 'aircraft'])} "
                          f"against {cls.loc[c_lo, 'share ducted']:.0%} of "
                          f"{int(cls.loc[c_lo, 'aircraft'])} for {cls.loc[c_lo, 'class']}. ")
    return _save(fig, path, SRC + "; propulsive_units, propulsion states (rules of 2026-09-19); class codes as "
                 "Figure D.1a; the band shares of (iii) are tables/la_duct_units.csv, with the chi-square "
                 "tests behind them.",
                 why_median +
                 " Top: one dot per aircraft, jittered so equal counts do not hide each other; the bar spans the "
                 "middle half of the class (25th to 75th percentile) — the range an ordinary design of that class "
                 "sits in — and the ring is the median, an aircraft that really exists. Dots far above the bar are "
                 "the class's exceptional designs; the axis is capped at 30 for the drawing only, nothing is "
                 "dropped. HB and PFV have no propulsor card and are left out, never counted as 0. Middle: share of "
                 "each class with the feature, over the aircraft where it can be read (read / total under the code); "
                 "a tilting boom is read from the boom tick. Bottom: the shape first, then the level — each point is "
                 "the share of that band's AIRCRAFT with at least one ducted unit, never a share of rotors, so one "
                 "ducted fan among twelve open rotors counts as much as twelve ducted ones; the dashed line is the "
                 "same share over every band, and the n under a band is its base. Every banded aircraft answers the "
                 f"duct question; the {int(dt[dt['group'].eq(la_tables.NO_UNIT_CARD)]['no duct answer'].sum())} with "
                 f"no propulsor card and the one recorded with 0 units form no band. A band under "
                 f"{la_tables.DUCT_THIN} aircraft would be hollow with the line broken either side of it; none is. "
                 + take + duct_take)


def _thin_bands(fig, colors: Dict[str, str]) -> None:
    """A class kept out of "Other" can be a very thin band in a stacked bar. Thin the white separator
    between the segments so a band of one or two per cent survives its own edges, and write the share
    beside any such band, since the stack only labels a segment from 5 % up."""
    from matplotlib.colors import to_hex
    want = {to_hex(c) for c in colors.values()}
    white = to_hex(SURFACE)
    for ax in fig.axes:
        bars = [p for p in ax.patches if isinstance(p, matplotlib.patches.Rectangle) and p.get_height()]
        if len(bars) < len(want) + 4:            # not a stacked-bar axes
            continue
        for p in bars:
            ec = p.get_edgecolor()
            if len(ec) and ec[3] > 0 and to_hex(ec[:3]) == white and p.get_linewidth() > 0.6:
                p.set_linewidth(0.6)
        # the thin bands of one bar, top one first: several of them land within a per cent of each
        # other, so the labels are stacked down the gap beside the bar and joined back by a leader
        groups: Dict[float, List] = {}
        for p in bars:
            if to_hex(p.get_facecolor()[:3]) in want and p.get_height() < 0.05:
                groups.setdefault(round(p.get_x(), 6), []).append(p)   # 5 % and over labels itself
        if not groups:
            continue
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        top_px = ax.transData.transform((0, ylim[1]))[1]
        to_data = ax.transData.inverted()
        for x0, ps in groups.items():
            ps.sort(key=lambda q: q.get_y(), reverse=True)
            lab_x = x0 + ps[0].get_width() + 0.03
            prev_bottom = None
            for p in ps:
                h, yc = p.get_height(), p.get_y() + p.get_height() / 2
                t = ax.text(lab_x, yc, f"{h:.0%}" if h >= 0.01 else f"{h * 100:.1f}%",
                            rotation=90, ha="left", va="center", fontsize=6.5, color=INK,
                            clip_on=False, zorder=5)
                bb = t.get_window_extent(r)
                shift = min(0.0, top_px - bb.y1)                     # never climb past 100 %
                if prev_bottom is not None:
                    shift = min(shift, prev_bottom - 2 - bb.y1)      # 2 px clear of the one above
                if shift:
                    y_new = to_data.transform((0, ax.transData.transform((lab_x, yc))[1] + shift))[1]
                    t.set_y(y_new)
                    ax.plot([x0 + p.get_width(), lab_x], [yc, y_new], lw=0.4, color=MUTED,
                            clip_on=False, zorder=4)
                    bb = t.get_window_extent(r)
                prev_bottom = bb.y0
        ax.set_xlim(*xlim)                       # the leaders must not restretch the axes
        ax.set_ylim(*ylim)


def _atlas(fn: Callable, ds: Dataset, av: pd.DataFrame, n: Dict, path: Path, size: tuple = (W, 5.0),
           extra: Optional[Dict[str, str]] = None) -> Path:
    page, legend, stack = atlas.PAGE, atlas._legend_arch, atlas._stack_h
    order, arch_color = atlas.ARCH_ORDER, atlas.ARCH_COLOR
    atlas.PAGE, atlas._legend_arch = size, _legend_arch
    atlas._stack_h = lambda ax, frame, colors, min_label=0.06, pct=True: stack(ax, frame, colors, max(min_label, 0.17), pct)
    if extra:
        # atlas._fold sends everything outside ARCH_COLOR to "Other" and reads both names at call time,
        # so widening them here — and only here — gives this one figure a class of its own. Rebound, never
        # mutated: the lists imported into this module and the Preliminary Analysis keep the seven classes.
        atlas.ARCH_ORDER = list(order) + [c for c in extra if c not in order]
        atlas.ARCH_COLOR = {**arch_color, **extra}
    try:
        with plt.rc_context({**STYLE, "font.size": 8.5, "axes.titlesize": 9.5, "legend.fontsize": 7.5}):
            fig, number, title = fn(ds, av, n)
            if extra:                        # a class of its own can be a one-per-cent band: keep it readable
                _thin_bands(fig, extra)
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
            # graphs this document does not print (the atlas keeps them). Last, so the rules above still
            # see the panels as the atlas drew them: a half-width x axis does not pick up the rotation a
            # full-width one would, and the surviving title is wrapped for two panels before it gets one.
            stem = Path(path).stem
            if stem in ATLAS_DROP:
                _drop_panels(fig, ATLAS_DROP[stem])
                note = ATLAS_NOTE.get(stem)
                if note:                     # the shared note describes both graphs: replace it here
                    g_ = atlas._ground_truth(ds)
                    g_ = g_[g_["ground_truth"].isin(atlas.ALL_ARCH)
                            & g_["figure_label_frozen"].isin(atlas.ALL_ARCH)]
                    fig._atlas_note = tuple(s.format(src=atlas.TABLES_SRC, aircraft=len(av),
                                                     questions=n.get("questions", ""), gt=len(g_),
                                                     dropped=len(atlas._ground_truth(ds)) - len(g_))
                                            for s in note)
            if stem in ATLAS_POST:           # LA-only edits to a shared atlas figure
                ATLAS_POST[stem](fig, ds)
            _atlas_save(fig, path)
    finally:
        atlas.PAGE, atlas._legend_arch, atlas._stack_h = page, legend, stack
        atlas.ARCH_ORDER, atlas.ARCH_COLOR = order, arch_color
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


# ------------------------------------------------------- 1.4 design drivers and their traces
def fig_trace_drift(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    """Figure 1.4.1: every labelled trace of :data:`la_tables.TRACES` marked ``drawn``, one panel
    each, per class and window — the machinery of Figure 1.1.5 extended from four dimensions to
    the trace set, ordered by the kind of driver that predicts the trace (A1, A2, B, C)."""
    t = la_tables.trace_drift(ds, v)
    drawn = [tr for tr in la_tables.TRACES if tr.get("drawn")]
    codes = [c for c in dict.fromkeys(t["code"]) if c not in la_tables.POOLED]
    ncol = 4
    nrow = int(np.ceil((len(drawn) + 1) / ncol))
    fig, axgrid = plt.subplots(nrow, ncol, figsize=(W * 0.92, 2.1 * nrow),
                               gridspec_kw={"wspace": 0.38, "hspace": 0.9})
    axes = list(axgrid.flat)
    x = np.arange(len(WINDOW_NAMES))
    # the panel title must stay narrower than its own panel (a centred title wider than the
    # panel spills into the neighbour and widens the canvas), so the driver kind is a short tag
    # and the how-to-read line spells the four tags out
    for ax, tr in zip(axes, drawn):
        col, ncol_ = tr["label"], tr["label"] + " n"
        for code in codes:
            sub = t[t["code"].eq(code)].set_index("window").reindex(WINDOW_NAMES)
            _class_line(ax, x, sub[col], sub[ncol_], code, lw=1.6, ms=3.6)
        kind = la_tables.DRIVERS[next(iter(tr["drivers"]))][0]
        ax.set_title(tr["panel"] + f"\n[{kind}]", fontsize=7.2)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        if tr["kind"] == "share":
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        else:
            ax.set_ylim(0)
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=5))
        ax.tick_params(axis="y", labelsize=7)
        _hgrid(ax, "y")
    for ax in axes[len(drawn):]:
        ax.axis("off")
    # the class key runs under the figure (a legend inside the spare cell is wider than the cell
    # and would hang off the canvas, which the width fit then pays for by shrinking every panel)
    _class_legend(fig, t[t["code"].isin(codes)], ncol=3, y=-0.01)
    # every suptitle line stays under the DRAWN width * 0.98 (the panels and key span about 6.2 in
    # of the 7 in canvas), or _wrap_to flattens the block and re-wraps it wider, and the width fit
    # then shrinks every panel to pay for it
    fig.suptitle("The labelled traces inside each class, per window: one panel per trace,\n"
                 "ordered by the kind of driver that predicts it (the four of Figure 1.1.5 not redrawn)",
                 x=0.01, y=1.02, ha="left", fontsize=9.5, fontweight="bold")
    a = t.attrs
    return _save(fig, path, SRC + "; tables/la_trace_drift.csv (the frame of Table 1.4.3a), the same class rule and "
                 "window cells as Table 1.1.5.",
                 "A line is an architecture class, not an archetype; every point counts unique aircraft, and a "
                 "percentage divides by the class's own aircraft in that window that answer the trace (the `n` column "
                 "beside each trace in the CSV), never by a count of rotors. Two panels sit on a narrower base and say "
                 "so in the verdict table: wing units at the leading edge divides by the aircraft with units on a wing, "
                 "the planform panel by the aircraft with a planform. A tilting joint group is a tilting wing panel, a "
                 "tilting boom group, a tilting propulsor type or a tilting empennage, each counted once; a propulsor "
                 "type is one entry of a propulsor card. The tag under each title is the kind of driver that predicts "
                 "the trace (the author's table, 1.4): A1 technological, A2 physical, B requirement, C life-cycle cost. "
                 "A movement is consistent with a driver and never caused by it, and one trace is usually predicted by "
                 "several. The trend test behind every reading is in "
                 "tables/la_trace_trends.csv and the verdict table, not in the picture: read a slope here as a "
                 "candidate, and the table for whether it survives. " + _selection_line(t))


def fig_trace_couplings(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    """Figure 1.4.2: the couplings the fixed physical drivers (A2) predict, as bias-corrected
    Cramér's V, read against the distribution of every other pair of label fields; the
    definitional pairs are shown hollow and kept out of that distribution."""
    P = la_tables.trace_couplings(ds, v)
    T = la_tables.predicted_couplings(ds, v, P)
    a = P.attrs
    rest = P[~P["definitional"] & P["V"].notna()]
    defs = P[P["definitional"] & P["V"].notna()].sort_values("V", ascending=False).head(4)
    pred = T[T["driver"] != "(none predicted)"].sort_values("V", ascending=True)
    top = T[T["driver"] == "(none predicted)"]
    rows = []                                   # (label, V, style)
    for _, r in defs.iterrows():
        rows.append((f"{r['field a']} × {r['field b']}\ndefinitional — excluded", r["V"], "def"))
    for _, r in top.iterrows():
        rows.append((f"{r['fields']}\nstrongest pair; no driver names it", r["V"], "top"))
    for _, r in pred.iterrows():
        rows.append((f"{r['predicted pair']}\n[{r['driver'].split(' (')[0]}]", r["V"], "pred"))
    fig, ax = plt.subplots(figsize=(W * 0.92, 0.36 * len(rows) + 1.3))
    fig.subplots_adjust(left=0.47, right=0.97, top=0.9, bottom=0.11)
    y = np.arange(len(rows))
    # the distribution of the other pairs: a rug along the bottom and the three quantile lines
    rng = np.random.default_rng(7)
    ax.scatter(rest["V"], -1.1 + rng.uniform(-0.28, 0.28, len(rest)), s=5, color=INK2, alpha=0.35, lw=0, zorder=2)
    for q, lbl, ls, dy in ((a["median"], "median", ":", 0.0), (a["q75"], "upper quartile", "--", 0.55),
                           (a["q90"], "90th percentile", "-", 0.0)):
        ax.axvline(q, color=INK2, lw=0.9, ls=ls, zorder=1)
        ax.text(q, len(rows) - 0.4 + dy, lbl, fontsize=6.8, color=INK2, ha="center", va="bottom")
    for yi, (lbl, V, style) in zip(y, rows):
        if style == "def":
            ax.plot(V, yi, marker="o", ms=6, mfc=SURFACE, mec=INK, mew=1.1, ls="", zorder=4)
        elif style == "top":
            ax.plot(V, yi, marker="s", ms=5.5, color=INK2, ls="", zorder=4)
        else:
            ax.plot(V, yi, marker="D", ms=6, color=INK, ls="", zorder=5)
        ax.hlines(yi, 0, V, color=GRID, lw=0.8, zorder=1)
        ax.text(V + 0.012, yi, f"{V:.2f}", fontsize=6.8, va="center", color=INK)
    ax.set_yticks(list(y) + [-1.1], [lbl for lbl, _, _ in rows] + [f"every other pair (n {a['rest']})"], fontsize=6.8)
    ax.set_ylim(-1.7, len(rows) + 0.9)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("bias-corrected Cramér's V between the two label fields", fontsize=7.5)
    ax.tick_params(axis="x", labelsize=7)
    ax.axhspan(len(defs) - 0.5, len(defs) + len(top) - 0.5, color=GRID, alpha=0.35, lw=0, zorder=0)
    ax.axhspan(-0.5, len(defs) - 0.5, color=GRID, alpha=0.6, lw=0, zorder=0)
    _hgrid(ax, "x")
    fig.suptitle("The couplings the fixed physical drivers predict,\nagainst every other pair of label fields",
                 x=0.01, y=0.99, ha="left", fontsize=9.5, fontweight="bold")
    return _save(fig, path, SRC + f"; tables/la_trace_couplings.csv and la_trace_couplings_all.csv: {a['measured']} pairs of "
                 f"{len(a['fields'])} label fields (the Gower shortlist of Preliminary Analysis 5.3, unpooled, plus the "
                 f"retraction and propulsor-type traces), {a['definitional']} of them definitional and left out of the "
                 "distribution.",
                 "Each row is one pair of label fields and the diamond is its bias-corrected Cramér's V (Bergsma, 2013), "
                 "computed on the aircraft that answer both fields, with counts banded; 0 is independence and the "
                 "correction takes out the size of the table, so a sparse pair cannot score on its sparseness. The rug "
                 "at the bottom is every other pair of the same fields, and the three vertical lines are its median, "
                 "upper quartile and 90th percentile: a predicted pair is read against them, not against zero. The "
                 "hollow circles are the strongest pairs in the matrix and are the codebook's own "
                 "construction — the class is defined by what tilts, a boom field is only asked when booms exist — so "
                 "they are named, drawn, and excluded from the distribution; they are never findings. The grey squares "
                 "are the strongest non-definitional pairs, which no driver names, for scale. A physical driver is fixed "
                 "over the window, so its prediction is a coupling, not a trend; a diamond above the 90th-percentile "
                 "line is a pair coupled more strongly than nine in ten pairs of the same fields, and a diamond at "
                 "zero is a pair the record does not couple at all.")


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
        paths[name] = _atlas(fn, ds, av, n, out / f"{name}.png", ATLAS_SIZE.get(name, (W, 5.0)),
                             ATLAS_EXTRA_CLASSES.get(name))
    jobs = {
        # parked 2026-09-22 (author's ruling on 1.1.2): the builders stay, they are simply not drawn.
        # Un-comment the line here and put the name back in la_index.NODES to bring the figure back.
        # "firm_weighted": lambda p: fig_firm_weighted(v, p),
        # "two_counts": lambda p: fig_two_counts(ds, p),
        "spans_by_firm": lambda p: fig_spans_by_firm(ds, v, p),
        "lead_lag": lambda p: fig_lead_lag(v, p),
        "class_cycles": lambda p: fig_class_cycles(v, p),
        "hill": lambda p: fig_hill(v, p),
        "zones": lambda p: fig_zones(v, p),
        "filer_weight": lambda p: fig_filer_weight(v, p),
        "abandonment": lambda p: fig_abandonment(ds, v, p),
        "region_grid": lambda p: fig_region_grid(v, p, ["class", "propulsive units", "tilting unit"], ds),
        # 2026-09-23, author's ruling: Figure 1.3.2b keeps filer type alone. Powertrain and ducting
        # left the pair for the sections that own them (atlas_powertrain and atlas_units) — the reasons are written out
        # beside the parked entries of la_tables.GRID_VARIABLES. Kept as a figure of its own rather
        # than merged into region_grid for a mechanical reason: fig_region_grid is 2.45 in per variable
        # row, so a fourth row puts Figure 1.3.2a at roughly 13.5 in of drawn height against the
        # 10.2 in of an A4 text block, and the merged figure could not be placed on a page.
        "region_grid_b": lambda p: fig_region_grid(v, p, ["filer type"], ds),
        "country_class": lambda p: fig_country_class(v, p),
        "coverage": lambda p: fig_coverage(v, p),
        "filers_over_time": lambda p: fig_filers_over_time(v, p),
        # parked 2026-09-23 (author's ruling on 1.2.3): replaced at 1.2.3 by "firm_influence", which
        # answers the question the tiles were asked to answer. Un-comment and put "firm_tiles" back in
        # la_index.NODES to bring it back.
        # "firm_tiles": lambda p: fig_firm_tiles(v, p),
        "firm_influence": lambda p: fig_firm_influence(v, p),
        "proximity_region": lambda p: fig_proximity_region(ds, v, p),
        "ari": lambda p: fig_ari(v, p),
        "mission": lambda p: fig_mission(v, p),
        "linked_check": lambda p: fig_linked_check(v, p),
        "filings_per_year": lambda p: fig_filings_per_year(ds, v, p),
        "atlas_removal": lambda p: fig_c1_removal(ds, p),
        "atlas_duplicates": lambda p: fig_c1_duplicates(ds, p),
        "atlas_figure_approval": lambda p: fig_c1_evidence(ds, v, p),
        "atlas_fill": lambda p: fig_c3_fill(ds, p),
        "atlas_design_heatmaps": lambda p: fig_design_heatmaps(ds, av, p),
        # the base frame is passed so panel (iii) reads its shares from la_tables.duct_by_units
        # rather than recomputing them beside it
        "atlas_units": lambda p: fig_units(ds, av, p, v),
        "ari_history": lambda p: fig_ari_history(v, p),
        "ari_clock": lambda p: fig_ari_clock(v, p),
        "dominant_design": lambda p: fig_dominant_design(v, p),
        "dominant_design_q": lambda p: fig_dominant_design_q(ds, v, p),
        "class_configs": lambda p: fig_class_configs(v, p),
        "dimension_drift": lambda p: fig_dimension_drift(v, p),
        # 1.4 design drivers and their traces (2026-09-23)
        "trace_drift": lambda p: fig_trace_drift(ds, v, p),
        "trace_couplings": lambda p: fig_trace_couplings(ds, v, p),
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
