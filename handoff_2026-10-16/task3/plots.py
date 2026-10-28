"""Chart primitives for the thesis figures. Each draws on an axis it is given and returns it.

They take ready numbers (computed in the notebook with lib/) and only draw: no statistics here.

    share_bars(ax, shares)            stacked 100 % bars, one per window, classes in the fixed order
    class_lines(ax, frame)            one line per class over years, marker + dash per class
    ci_bars(ax, labels, p, lo, hi)    shares with their interval, as dots with whiskers
    heatmap(ax, matrix)               a matrix with its value in each cell
    count_bars(ax, x, y)              plain counts per year, partial years hatched
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd
import matplotlib as mpl

from .style import CLASS_ORDER, INK, MUTED, PARTIAL_HATCH, cls


def _text_on(color: str) -> str:
    """Ink or white, whichever reads better on ``color`` (relative luminance)."""
    r, g, b = mpl.colors.to_rgb(color)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return INK if lum > 0.45 else "white"


def _ordered(cols: Iterable[str]) -> list:
    cols = list(cols)
    return [c for c in CLASS_ORDER if c in cols] + [c for c in cols if c not in CLASS_ORDER]


def share_bars(ax, shares: pd.DataFrame, partial: Sequence[str] = (), labels: bool = True,
               min_label: float = 0.08, horizontal: bool = False, label_kind: str = "short"):
    """Stacked shares: rows = windows (x), columns = classes; each row sums to 1.

    A window named in ``partial`` gets a hatched outline (not complete yet). A segment of at least
    ``min_label`` carries its class code (``label_kind="short"``) or its percentage as a whole number
    (``label_kind="pct"``); smaller ones are left to the legend.
    """
    shares = shares[_ordered(shares.columns)]
    pos = np.arange(len(shares))
    bottom = np.zeros(len(shares))
    bar = ax.barh if horizontal else ax.bar
    for c in shares.columns:
        s = cls(c)
        vals = shares[c].fillna(0).to_numpy()
        kw = dict(color=s.color, hatch=s.hatch, edgecolor="white", linewidth=0.6, label=s.short)
        bars = bar(pos, vals, 0.72, **({"left": bottom} if horizontal else {"bottom": bottom}), **kw)
        if labels:
            for b, v, b0 in zip(bars, vals, bottom):
                if v >= min_label:
                    x, y = ((b0 + v / 2, b.get_y() + b.get_height() / 2) if horizontal
                            else (b.get_x() + b.get_width() / 2, b0 + v / 2))
                    ax.text(x, y, s.short if label_kind == "short" else f"{100 * v:.0f}", ha="center", va="center", color=_text_on(s.color),
                            fontsize=mpl.rcParams["xtick.labelsize"] - 1,
                            bbox=dict(boxstyle="square,pad=0.15", facecolor=s.color, edgecolor="none"))
        bottom = bottom + vals
    for i, w in enumerate(shares.index):
        if str(w) in set(map(str, partial)):        # not complete yet: a dashed frame around the bar
            box = dict(fill=False, edgecolor=INK, linewidth=0.9, linestyle=(0, (3, 2)))
            (ax.barh if horizontal else ax.bar)(i, 1, 0.80, **box)
    if horizontal:
        ax.set_yticks(pos, shares.index)
        ax.set_xlim(0, 1)
        ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    else:
        ax.set_xticks(pos, shares.index)
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    return ax


def _spread(ys: Sequence[float], gap: float) -> list:
    """Move label positions apart so neighbours are at least ``gap`` apart, keeping their order."""
    order = np.argsort(ys)
    out = np.array(ys, dtype=float)
    for k in range(1, len(order)):
        a, b = order[k - 1], order[k]
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    shift = (np.mean(ys) - np.mean(out)) if len(out) else 0     # keep the group centred
    return list(out + shift)


def class_lines(ax, frame: pd.DataFrame, pct: bool = False, end_labels: bool = True):
    """One line per class (columns) over the index (years or windows), marker + dash per class.
    ``end_labels`` writes the class code at the end of each line, pushed apart so none overlap,
    with a thin leader to its line."""
    ends = []
    for c in _ordered(frame.columns):
        s = cls(c)
        y = frame[c]
        ax.plot(frame.index, y, color=s.color, marker=s.marker, linestyle=s.dash,
                markersize=3.5, markeredgecolor="white", markeredgewidth=0.4, label=s.short)
        last = y.last_valid_index()
        if last is not None:
            ends.append((s.short, last, float(y[last])))
    if pct:
        ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    if end_labels and ends:
        ax.figure.canvas.draw()
        lo, hi = ax.get_ylim()
        h_in = ax.get_window_extent().height / ax.figure.dpi            # axis height in inches
        gap = (hi - lo) * (mpl.rcParams["xtick.labelsize"] * 1.15 / 72) / h_in
        placed = _spread([e[2] for e in ends], gap)
        for (txt, x, y), yl in zip(ends, placed):
            moved = abs(yl - y) > 1e-9
            ax.annotate(txt, xy=(x, y), xytext=(8, yl), textcoords=("offset points", "data"),
                        va="center", fontsize=mpl.rcParams["xtick.labelsize"] - 1, color=INK,
                        annotation_clip=False,
                        arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.4, shrinkA=0,
                                        shrinkB=2) if moved else None)
    return ax


def ci_bars(ax, labels: Sequence[str], p: Sequence[float], lo: Sequence[float], hi: Sequence[float],
            codes: Optional[Sequence[str]] = None, pct: bool = True):
    """Shares with their interval: a dot and a whisker per row (rows top to bottom)."""
    y = np.arange(len(labels))[::-1]
    for i, (yy, pp, l, h) in enumerate(zip(y, p, lo, hi)):
        s = cls(codes[i]) if codes is not None else None
        col = s.color if s else INK
        ax.plot([l, h], [yy, yy], color=MUTED, linewidth=1)
        ax.plot(pp, yy, marker=s.marker if s else "o", color=col, markeredgecolor=INK,
                markeredgewidth=0.4, markersize=5, linestyle="none")
    ax.set_yticks(y, labels)
    if pct:
        ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    return ax


def heatmap(ax, matrix: pd.DataFrame, fmt: str = "{:.0%}", cmap: str = "Blues",
            vmin: Optional[float] = None, vmax: Optional[float] = None, box=None):
    """A matrix with its value printed in each cell; one hue, light to dark (sequential).
    ``box`` = list of (row, col) cells to outline (e.g. the diagonal 'stays in class')."""
    m = matrix.to_numpy(dtype=float)
    im = ax.imshow(m, cmap=cmap, vmin=vmin if vmin is not None else np.nanmin(m),
                   vmax=vmax if vmax is not None else np.nanmax(m), aspect="auto")
    norm = im.norm
    for (r, c), val in np.ndenumerate(m):
        if np.isnan(val):
            continue
        dark = norm(val) > 0.55
        ax.text(c, r, fmt.format(val), ha="center", va="center",
                color="white" if dark else INK, fontsize=mpl.rcParams["xtick.labelsize"] - 1)
    for r, c in (box or []):
        ax.add_patch(mpl.patches.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False, edgecolor=INK, linewidth=1.2))
    ax.set_xticks(range(m.shape[1]), matrix.columns)
    ax.set_yticks(range(m.shape[0]), matrix.index)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return ax


def count_bars(ax, x: Sequence, y: Sequence[float], partial_from: Optional[int] = None,
               color: str = "#0072B2"):
    """Counts per year; years from ``partial_from`` on are hatched (not complete yet)."""
    x = list(x)
    for xi, yi in zip(x, y):
        part = partial_from is not None and xi >= partial_from
        ax.bar(xi, yi, 0.8, color="white" if part else color, edgecolor=color,
               hatch=PARTIAL_HATCH if part else "", linewidth=0.6)
    return ax


# =====================================================================================================
# Question 1 primitives (notebook 40). Same rules: ready numbers in, drawing only.
# =====================================================================================================
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib.lines import Line2D                                 # noqa: E402
from matplotlib.patches import Patch                                # noqa: E402

from .style import GRID, REGIONS as REGION_STYLE, OTHER             # noqa: E402

#: region -> hatch, so the stack survives black-and-white print (colours come from style.REGIONS)
REGION_HATCH = {"North America": "", "Europe": "////", "Asia-Pacific": "....", "Other regions": "xxxx"}


def region_stack(ax, tab: pd.DataFrame, line: Optional[pd.Series] = None, line_label: str = "",
                 incomplete: Sequence[int] = (), pooled_first: str = ""):
    """Stacked bars per year (rows = years) by applicant region, with an optional line on top of them.

    ``tab`` columns: the regions in the order they stack (colour, hatch: style.REGIONS / REGION_HATCH; any
    other column is grey). A year in ``incomplete`` is faded with a dashed outline and carries its bar total
    above it (it will still grow). ``pooled_first`` is a note written beside the first bar (a pooled bucket).
    """
    x = np.arange(len(tab))
    bottom = np.zeros(len(tab))
    for col in tab.columns:
        colour = REGION_STYLE[col][0] if col in REGION_STYLE else OTHER.color
        ax.bar(x, tab[col], 0.78, bottom=bottom, color=colour, hatch=REGION_HATCH.get(col, "xxxx"),
               edgecolor="white", linewidth=0.5, label=col)
        bottom = bottom + tab[col].to_numpy()
    inc = [i for i, y in enumerate(tab.index) if y in set(incomplete)]
    for i in inc:
        ax.bar(i, bottom[i], 0.78, color=(1, 1, 1, 0.55), edgecolor=INK, linewidth=0.8, linestyle=(0, (3, 2)))
    if line is not None:
        ax.plot(x, line.to_numpy(), color=INK, linewidth=1.3, marker="o", markersize=3, zorder=5, label=line_label)
    top = np.maximum(bottom, line.to_numpy() if line is not None else 0)
    for i in inc:       # the bar total of a year still filling: inside a bar tall enough, else just above it
        inside = bottom[i] >= 12
        ax.text(i, bottom[i] / 2 if inside else bottom[i] + 2.5, f"{int(bottom[i])}", ha="center",
                va="center" if inside else "bottom", fontsize=mpl.rcParams["xtick.labelsize"] - 0.5, color=INK,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8) if inside else None)
    if pooled_first:
        ax.annotate(pooled_first, (0, top[0]), xytext=(4, 8), textcoords="offset points", fontsize=7, color=MUTED,
                    va="bottom")
    ax.set_xlim(-0.7, len(tab) - 0.3)
    return ax


def event_strip(ax, events: pd.DataFrame, years: Sequence, parent=None, label_max: int = 28, side_step: float = 0.55):
    """A strip of dated events under a year axis: each event a short tick on its calendar year with its label
    reading upward from the tick (two events of one year stand side by side, in date order); a faint dotted guide
    runs from the tick up through ``parent``'s bars. ``events`` columns: event, year; ``years``: the axis years
    (an event before the first year stands on the first bar, the pooled one)."""
    pos = {y: i for i, y in enumerate(years)}
    xs = np.array([pos[min(max(y, years[0]), years[-1])] for y in events["year"]], dtype=float)
    for y in np.unique(xs):
        k = np.flatnonzero(xs == y)
        if len(k) > 1:
            xs[k] = y + (np.arange(len(k)) - (len(k) - 1) / 2) * side_step
    labels = [s if len(s) <= label_max else s[:label_max - 1].rstrip() + "…" for s in events["event"].astype(str)]
    ax.set_ylim(0, 1)
    tick = 0.045
    for x, lab in zip(xs, labels):
        ax.plot([x, x], [0, tick], color=INK, linewidth=0.8, solid_capstyle="butt")
        ax.text(x, tick + 0.02, lab, rotation=90, ha="center", va="bottom", fontsize=7, color=INK)
        if parent is not None:
            parent.axvline(x, color=MUTED, linewidth=0.5, linestyle=(0, (1, 2.2)), zorder=0.6)
    ax.set_yticks([])
    for side in ("top", "left", "right"):
        ax.spines[side].set_visible(False)
    ax.set_ylabel("sector events", fontsize=mpl.rcParams["xtick.labelsize"])
    return ax


#: the series of a growth panel: colour, dash, marker, line width (greys + black: none of these is a class)
GROWTH_STYLE = {"evtol_families": (INK, "-", "o", 1.8), "b64": ("#555555", "--", "s", 1.2),
                "secb": ("#808080", "-.", "^", 1.2), "all": ("#a6a6a6", ":", "v", 1.4)}


def growth_fits(ax, yearly: dict, fits: dict, names: dict, first: int, last: int, base_years=(2005, 2009)):
    """Each series divided by its own base-window mean, on a log axis: yearly points and the fitted line (log count
    on year); the legend names every series with its doubling time. ``yearly``: key -> year-indexed counts;
    ``fits``: key -> dict(doubling time (years), slope (log count per year)); ``names``: key -> printed name."""
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    yrs = np.arange(first, last + 1)
    top = 1.0
    for key, s in yearly.items():
        col, ls, mk, lw = GROWTH_STYLE[key]
        cnt = s.reindex(yrs, fill_value=0).astype(float)
        base = float(cnt.loc[base_years[0]:base_years[1]].mean())
        ok = cnt.to_numpy() > 0
        b, a = np.polyfit(yrs[ok], np.log(cnt.to_numpy()[ok]), 1)
        ax.plot(yrs[ok], cnt.to_numpy()[ok] / base, ls="none", marker=mk, ms=3, color=col, alpha=0.6)
        line = np.exp(a + b * yrs) / base
        ax.plot(yrs, line, ls=ls, lw=lw, color=col,
                label=f"{names[key]}: doubles every {fits[key]['doubling time (years)']:.1f} years")
        top = max(top, float((cnt.to_numpy()[ok] / base).max()), float(line.max()))
    ax.set_yscale("log")
    ticks = [t for t in (0.25, 0.5, 1, 2, 4, 8, 16, 32) if t <= top * 1.6]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"×{x:g}"))
    ax.set_ylim(min(ticks) * 0.8, top * 1.5)
    ax.axhline(1, color=MUTED, linewidth=0.7, linestyle=":")
    ax.set_xlim(first - 0.6, last + 0.6)
    ax.set_ylabel(f"count ÷ its {base_years[0]}-{str(base_years[1])[2:]} mean\n(log scale)")
    return ax


def folded_bars(ax, shares: pd.DataFrame, spec: dict, totals: Optional[Sequence[int]] = None, min_label: float = 0.08):
    """Stacked 100 % bars (rows = windows) of the evtol.news five classes. ``spec``: folded code -> (class code of
    style.cls whose colour and hatch it borrows, printed short code); the segment prints its percentage.
    ``totals`` (aircraft per bar) go under the window name."""
    pos = np.arange(len(shares))
    bottom = np.zeros(len(shares))
    for code, (cls_code, short) in spec.items():
        s = cls(cls_code)
        vals = shares[code].fillna(0).to_numpy()
        bars = ax.bar(pos, vals, 0.72, bottom=bottom, color=s.color, hatch=s.hatch, edgecolor="white", linewidth=0.6,
                      label=short)
        for x, b0, val in zip(pos, bottom, vals):
            if val >= min_label:
                ax.text(x, b0 + val / 2, f"{100 * val:.0f}", ha="center", va="center", color=_text_on(s.color),
                        fontsize=mpl.rcParams["xtick.labelsize"] - 0.5,
                        bbox=dict(boxstyle="square,pad=0.15", facecolor=s.color, edgecolor="none"))
        bottom = bottom + vals
    names = [str(w) for w in shares.index]
    ax.set_xticks(pos, [f"{n}\n{t}" if totals is not None else n for n, t in zip(names, totals if totals is not None else names)])
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    return ax


def clock_rows(ax, tl: pd.DataFrame, today: float, planned_after: int):
    """One row per firm: a bar from its first to its last patent (priority years), a tick at its peak filing year,
    a square at the first flight and a triangle at the entry into service the index states. A marker after
    ``planned_after`` is a plan and is drawn open. ``today``: x of the dotted line."""
    y = np.arange(len(tl))
    for yi, (_, r) in zip(y, tl.iterrows()):
        ax.plot([r["first patent"], r["last patent"] + 0.0], [yi, yi], color="#9a9a9a", linewidth=4.5, solid_capstyle="butt",
                zorder=2)
        ax.plot(r["peak filing year"], yi, marker="|", markersize=9, markeredgewidth=1.6, color=INK, zorder=4)
        for col, mk in (("first flight (ARI)", "s"), ("entry into service (ARI)", "^")):
            if pd.notna(r[col]):
                plan = r[col] > planned_after
                ax.plot(r[col], yi, marker=mk, markersize=5.5, markerfacecolor="white" if plan else INK,
                        markeredgecolor=INK, markeredgewidth=0.9, linestyle="none", zorder=5)
    ax.set_yticks(y, [f"{c} ({int(n)})" for c, n in zip(tl["company"], tl["unique aircraft"])])
    ax.invert_yaxis()
    ax.axvline(today, color=MUTED, linewidth=0.8, linestyle=":")
    ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(2))
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def clock_legend(target, **kw):
    """The key of :func:`clock_rows`; ``target`` is an axes or a figure."""
    h = [Line2D([], [], color="#9a9a9a", linewidth=4.5, label="first to last patent"),
         Line2D([], [], color=INK, marker="|", markersize=9, markeredgewidth=1.6, linestyle="none", label="peak filing year"),
         Line2D([], [], color=INK, marker="s", markersize=5.5, linestyle="none", label="first flight"),
         Line2D([], [], color="white", marker="s", markeredgecolor=INK, markersize=5.5, linestyle="none", label="first flight, planned"),
         Line2D([], [], color=INK, marker="^", markersize=5.5, linestyle="none", label="entry into service"),
         Line2D([], [], color="white", marker="^", markeredgecolor=INK, markersize=5.5, linestyle="none", label="entry into service, planned")]
    return target.legend(handles=h, **kw)


def class_value_bars(ax, codes: Sequence[str], values: Sequence[float], ns: Sequence[int], marks: Optional[Sequence[float]] = None,
                     mark_label: str = "", overall: Optional[float] = None, overall_label: str = ""):
    """One bar per class (colour and hatch from style.cls), the value printed inside its top, the class's n under its
    code; ``marks`` = a second reading of the same share, drawn as a dash across the bar; ``overall`` =
    a dashed reference line."""
    x = np.arange(len(codes))
    for xi, c, val in zip(x, codes, values):
        s = cls(c)
        ax.bar(xi, val, 0.62, color=s.color, hatch=s.hatch, edgecolor="white", linewidth=0.6, zorder=3)
        ax.text(xi, val - 0.012, f"{val:.0%}", ha="center", va="top", fontsize=mpl.rcParams["xtick.labelsize"], color=INK,
                bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"), zorder=7)
    if marks is not None:       # a second reading of the share: a black dash across the bar on a white ground
        ax.plot(x, marks, linestyle="none", marker="_", markersize=22, markeredgewidth=3.6, color="white", zorder=5)
        ax.plot(x, marks, linestyle="none", marker="_", markersize=20, markeredgewidth=1.6, color=INK, zorder=6,
                label=mark_label)
    if overall is not None:
        ax.axhline(overall, color=INK, linewidth=1, linestyle="--", zorder=4)
        ax.text(len(codes) - 0.35, overall + 0.012, overall_label, ha="right", va="bottom",
                fontsize=mpl.rcParams["xtick.labelsize"], color=MUTED, linespacing=1.15)
    ax.set_xticks(x, [f"{cls(c).short}\nn {n}" for c, n in zip(codes, ns)])
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlim(-0.6, len(codes) - 0.3)
    return ax


def split_hbars(ax, labels: Sequence[str], matched: Sequence[int], unmatched: Sequence[int], matched_label: str,
                unmatched_label: str):
    """Horizontal bars split into two counts (dark hatched = matched, light = not matched), the counts printed in
    the segments; rows top to bottom."""
    y = np.arange(len(labels))[::-1]
    ax.barh(y, matched, 0.6, color="#4d4d4d", hatch="....", edgecolor="white", linewidth=0.6, label=matched_label)
    ax.barh(y, unmatched, 0.6, left=matched, color="#dcdcdc", edgecolor="white", linewidth=0.6, label=unmatched_label)
    for yi, m, u in zip(y, matched, unmatched):
        if m:
            ax.text(m / 2, yi, f"{m}", ha="center", va="center", color="white", fontsize=mpl.rcParams["xtick.labelsize"],
                    bbox=dict(boxstyle="square,pad=0.15", fc="#4d4d4d", ec="none"))
        if u:
            ax.text(m + u / 2, yi, f"{u}", ha="center", va="center", color=INK, fontsize=mpl.rcParams["xtick.labelsize"])
    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(np.add(matched, unmatched)) * 1.04)
    return ax


# =====================================================================================================
# Question 2 primitives (notebook 41). Same rules: ready numbers in, drawing only.
# =====================================================================================================
from matplotlib.transforms import Bbox                              # noqa: E402

#: the three greys of a ducting bar, darkest first (a share of an aircraft's units, not a class)
DUCT_GREYS = ("#3d3d3d", "#9a9a9a", "#dcdcdc")


def class_ticks(ax, codes: Sequence[str], second: Sequence[str]):
    """x ticks at 0..k-1: the class's printed code, then ``second`` (its aircraft) underneath."""
    ax.set_xticks(range(len(codes)), [f"{cls(c).short}\n{s}" for c, s in zip(codes, second)])
    ax.set_xlim(-0.6, len(codes) - 0.4)
    return ax


def unit_strips(ax, codes: Sequence[str], units: Sequence, cap: int = 30, seed: int = 42, empty_label: str = "no record"):
    """One column per class: a dot per aircraft (propulsor units, capped at ``cap``, jittered with ``seed``), a bar over
    the middle half (25th to 75th percentile) and a ring at the median. A class without units reads ``empty_label``.
    ``units``: one array of unit counts per class."""
    rng = np.random.default_rng(seed)
    for i, (c, u) in enumerate(zip(codes, units)):
        s = cls(c)
        u = np.asarray(u, dtype=float)
        u = u[~np.isnan(u)]
        if not len(u):
            ax.text(i, cap / 2, empty_label, rotation=90, ha="center", va="center", fontsize=mpl.rcParams["xtick.labelsize"],
                    color=MUTED)
            continue
        ax.scatter(i + rng.uniform(-0.28, 0.28, len(u)), np.clip(u, 0, cap) + rng.uniform(-0.25, 0.25, len(u)), s=6,
                   color=s.color, edgecolor="white", linewidth=0.25, alpha=0.8, zorder=2)
        q1, md, q3 = np.percentile(u, [25, 50, 75])
        ax.plot([i, i], [q1, q3], color=INK, linewidth=2.6, solid_capstyle="butt", zorder=4)
        ax.plot(i, md, marker="o", markersize=6, markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.5, zorder=5)
    ax.set_ylim(-1, cap + 1)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def feature_heat(ax, mat: pd.DataFrame, cmap: str = "Blues"):
    """A features x classes matrix of shares: the percentage in each cell on a one-hue scale; a cell with no value (the
    class has no propulsor record) is hatched grey. Rows top to bottom, columns left to right."""
    m = mat.to_numpy(dtype=float)
    ax.imshow(np.ma.masked_invalid(m), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for (r, c), val in np.ndenumerate(m):
        if np.isnan(val):
            ax.add_patch(mpl.patches.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor="#ececec", hatch="////", edgecolor="white",
                                               linewidth=0))
            continue
        ax.text(c, r, f"{100 * val:.0f}%", ha="center", va="center", color="white" if val > 0.55 else INK,
                fontsize=mpl.rcParams["xtick.labelsize"] - 0.5)
    ax.set_yticks(range(m.shape[0]), list(mat.index))
    ax.set_xticks(range(m.shape[1]), [])
    ax.set_xticks(np.arange(-0.5, m.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, m.shape[0]), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(length=0, which="both")
    for sp in ax.spines.values():
        sp.set_visible(False)
    return ax


def duct_bands(ax, dc: pd.DataFrame, cd: pd.DataFrame, band_col: str = "propulsive units"):
    """Ducting per propulsor-unit band and for all bands together. Bar height = the share of the band's aircraft with at
    least one ducted propulsor, split by how much of each such aircraft is ducted (every propulsor; half or more, not all;
    under half), the share that duct every propulsor of the ducting aircraft printed in the dark block; the diamond is the
    share of the band's propulsor UNITS that sit in a duct. Under each tick: aircraft in the band, aircraft that duct, and
    the median ducted propulsors of those. ``dc`` = frames.duct_count_by_units, ``cd`` = frames.duct_conditional."""
    dc, cd = dc.set_index(band_col), cd.set_index(band_col)
    order = [g for g in dc.index if g != "all bands"] + ["all bands"]
    f = lambda t, c: pd.to_numeric(t.loc[order, c], errors="coerce").to_numpy(dtype=float)
    n, any_n, any_s, unit_s = f(dc, "aircraft"), f(dc, "with any ducted unit"), f(dc, "share with any"), f(dc, "share of units ducted")
    every_s, med, cond_every = f(dc, "share ducting every unit"), f(dc, "median ducted units (ducted aircraft)"), f(cd, "share that duct every unit")
    half = (f(cd, "half to three quarters") + f(cd, "three quarters, not all")) / n
    under = (f(cd, "under a quarter") + f(cd, "a quarter to half")) / n
    x = np.arange(len(order), dtype=float)
    x[-1] += 0.55                                       # the all-bands bar stands apart
    w = 0.5
    tick_fs = mpl.rcParams["xtick.labelsize"]
    parts = [("ducts every propulsor", every_s, DUCT_GREYS[0], ""), ("half or more, not all", half, DUCT_GREYS[1], "...."),
             ("under half", under, DUCT_GREYS[2], "")]
    bottom = np.zeros(len(x))
    for lab, h, colour, hatch in parts:
        ax.bar(x, h, w, bottom=bottom, color=colour, hatch=hatch, edgecolor="white", linewidth=0.6, zorder=3, label=lab)
        bottom = bottom + h
    for xi, e_, c_ in zip(x, every_s, cond_every):
        ax.text(xi, e_ / 2, f"{100 * c_:.0f}%", ha="center", va="center", color="white", fontsize=tick_fs - 0.5, zorder=6)
    for xi, s_ in zip(x, any_s):
        ax.text(xi, s_ + 0.018, f"{100 * s_:.0f}%", ha="center", va="bottom", fontweight="bold", fontsize=tick_fs, zorder=6)
    ax.plot(x + w / 2, unit_s, linestyle="none", marker="D", markersize=5.2, markerfacecolor="white", markeredgecolor=INK,
            markeredgewidth=1.2, zorder=7, label="share of the band's propulsor units in a duct")
    for xi, u_ in zip(x, unit_s):
        ax.text(xi + w / 2 + 0.09, u_, f"{100 * u_:.0f}%", ha="left", va="center", fontsize=tick_fs - 0.5, color=INK, zorder=7,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))
    ax.set_xticks(x, [f"{g}\n{int(a)} · {int(b)}\nmed {m:g}" for g, a, b, m in zip(order, n, any_n, med)])
    ax.set_xlim(-0.6, x[-1] + 0.95)
    ax.set_ylim(0, 0.9)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.axvline((x[-2] + x[-1]) / 2, color=GRID, linewidth=0.8, linestyle=":")
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def filer_bars(ax, tab: pd.DataFrame, marked: Sequence[str], bold: str, note: str, class_of=None):
    """Horizontal bars of distinct filers per aircraft, one per archetype, the lowest at the bottom: colour and hatch of
    the archetype's class (style.cls), the ratio and "(filers / aircraft)" printed after the bar. The archetypes in
    ``marked`` are outlined in ink; ``bold`` is printed in bold with ``note`` on a second line. ``tab`` columns: archetype,
    code (class), label (short), aircraft, filers, filers per aircraft; rows in the order top to bottom."""
    y = np.arange(len(tab))[::-1]
    for yi, (_, r) in zip(y, tab.iterrows()):
        s = cls(r["code"])
        mk = r["archetype"] in marked
        ax.barh(yi, r["filers per aircraft"], 0.66, color=s.color, hatch=s.hatch, edgecolor=INK if mk else "white",
                linewidth=1.4 if mk else 0.6, zorder=3)
        lead = r["archetype"] == bold
        ax.text(r["filers per aircraft"] + 0.015, yi + (0.2 if lead else 0),
                f"{r['filers per aircraft']:.2f}   ({int(r['filers'])} filers / {int(r['aircraft'])} aircraft)",
                va="center", ha="left", fontsize=mpl.rcParams["xtick.labelsize"], fontweight="bold" if lead else "normal")
        if lead:
            ax.text(r["filers per aircraft"] + 0.015, yi - 0.24, note, va="center", ha="left",
                    fontsize=mpl.rcParams["xtick.labelsize"] - 0.5, color=INK)
    ax.set_yticks(y, list(tab["label"]))
    ax.set_ylim(-0.95, len(tab) - 0.3)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def hull_ring(ax, xs, ys, radii_pt, pad_pt: float = 4.0, **kw):
    """A smooth outline round a group of bubbles: the convex hull of a circle of (bubble radius + ``pad_pt``) round each
    one, computed in display space so it is round on paper and mapped back to data. Call after the axis limits are
    final and the layout is drawn. Returns the outline's vertices in display pixels."""
    from scipy.spatial import ConvexHull
    fig = ax.figure
    k = fig.dpi / 72
    ang = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    cloud = []
    for x_, y_, r_ in zip(xs, ys, radii_pt):
        cx, cy = ax.transData.transform((x_, y_))
        rr = (r_ + pad_pt) * k
        cloud += list(zip(cx + rr * np.cos(ang), cy + rr * np.sin(ang)))
    cloud = np.array(cloud)
    hull = cloud[ConvexHull(cloud).vertices]
    data = ax.transData.inverted().transform(hull)
    style = {"linewidth": 1.4, "edgecolor": INK, "linestyle": "-", **kw}
    ax.add_patch(mpl.patches.Polygon(data, closed=True, fill=False, joinstyle="round", zorder=2, **style))
    return hull


def place_labels(ax, xs, ys, labels, marker_pt, obstacles: Sequence[Bbox] = (), fontsize: Optional[float] = None,
                 gap_pt: float = 1.5, max_r_pt: float = 90.0, color: str = INK, extra_avoid=()):
    """Label bubbles so that no label touches another label, a bubble or an obstacle (display-space boxes), and stays
    inside the axes. Each label tries 16 directions round its bubble at growing distance, the most crowded bubbles first;
    a label moved away from its bubble gets a thin leader line. Returns the labels that found no free place (should be none)."""
    fig = ax.figure
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    k = fig.dpi / 72
    fs = fontsize if fontsize is not None else mpl.rcParams["xtick.labelsize"] - 0.5
    pts = ax.transData.transform(np.c_[xs, ys])
    rad = np.asarray(marker_pt, dtype=float) * k
    placed = [Bbox([[p[0] - r, p[1] - r], [p[0] + r, p[1] + r]]) for p, r in zip(pts, rad)]
    n_own = len(placed)                      # the labelled bubbles come first; ``extra_avoid`` = (x, y, radius pt) of other bubbles
    for x_, y_, r_ in extra_avoid:
        cx, cy = ax.transData.transform((x_, y_))
        placed.append(Bbox([[cx - r_ * k, cy - r_ * k], [cx + r_ * k, cy + r_ * k]]))
    placed += list(obstacles)
    axbb = ax.get_window_extent(rend)
    sizes = []
    for lab in labels:
        t = ax.text(0, 0, lab, fontsize=fs)
        bb = t.get_window_extent(rend)
        sizes.append((bb.width + 4, bb.height + 3))
        t.remove()
    near = [(np.hypot(*(pts - p).T) < 45 * k).sum() for p in pts]
    angles = np.deg2rad([0, 180, 90, 270, 30, 150, 330, 210, 60, 120, 300, 240, 15, 165, 345, 195])
    fails = []
    for q in sorted(range(len(xs)), key=lambda i: -near[i]):
        w, h = sizes[q]
        done = False
        for r_pt in np.arange(rad[q] / k + gap_pt, max_r_pt, 3.0):
            for th in angles:
                px, py = pts[q][0] + r_pt * k * np.cos(th), pts[q][1] + r_pt * k * np.sin(th)
                x0 = px if np.cos(th) > 0.3 else px - w if np.cos(th) < -0.3 else px - w / 2
                y0 = py if np.sin(th) > 0.3 else py - h if np.sin(th) < -0.3 else py - h / 2
                bb = Bbox([[x0, y0], [x0 + w, y0 + h]])
                if not (axbb.x0 + 1 <= bb.x0 and bb.x1 <= axbb.x1 - 1 and axbb.y0 + 1 <= bb.y0 and bb.y1 <= axbb.y1 - 1):
                    continue
                if any(bb.overlaps(b) for b in placed):
                    continue
                seg = []
                if r_pt > rad[q] / k + 2.0:          # the leader line must not cross a label either
                    ex, ey = np.clip(pts[q][0], x0, x0 + w), np.clip(pts[q][1], y0, y0 + h)
                    seg = [Bbox([[pts[q][0] + (ex - pts[q][0]) * t - 1.5, pts[q][1] + (ey - pts[q][1]) * t - 1.5],
                                 [pts[q][0] + (ex - pts[q][0]) * t + 1.5, pts[q][1] + (ey - pts[q][1]) * t + 1.5]])
                           for t in np.linspace(0.25, 1, 9)]
                    others = [b for j, b in enumerate(placed) if j >= n_own or j != q]
                    if any(sg.overlaps(b) for sg in seg for b in others):
                        continue
                placed.append(bb)
                placed.extend(seg)
                ha = "left" if np.cos(th) > 0.3 else "right" if np.cos(th) < -0.3 else "center"
                va = "bottom" if np.sin(th) > 0.3 else "top" if np.sin(th) < -0.3 else "center"
                off = (r_pt * np.cos(th), r_pt * np.sin(th))
                ax.annotate(labels[q], xy=(xs[q], ys[q]), xytext=off, textcoords="offset points", ha=ha, va=va, fontsize=fs,
                            color=color, zorder=8, arrowprops=dict(arrowstyle="-", linewidth=0.5, color=INK, shrinkA=0,
                                                                    shrinkB=rad[q] / k) if r_pt > rad[q] / k + 2.0 else None)
                done = True
                break
            if done:
                break
        if not done:
            fails.append(labels[q])
    return fails


def window_heat(ax, mat: pd.DataFrame, half: dict, mark: str = "#ff5a1f"):
    """Aircraft per archetype (columns, largest first) per window (rows): the count in each cell, each column shaded by its
    own busiest window (darker = busier). ``half``: window -> zero-based column that takes the window past half of its
    aircraft; it gets a thick bar in ``mark`` and an arrow joins the bars of the first two windows named."""
    m = mat.to_numpy(dtype=float)
    norm = m / np.where(m.max(axis=0) > 0, m.max(axis=0), 1)
    ax.imshow(norm, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for (r, c), val in np.ndenumerate(m):
        if val:
            ax.text(c, r, f"{val:.0f}", ha="center", va="center", color="white" if norm[r, c] > 0.55 else INK,
                    fontsize=mpl.rcParams["xtick.labelsize"] - 0.5)
    rows = list(mat.index)
    for w, j in half.items():
        i = rows.index(w)
        ax.plot([j + 0.5, j + 0.5], [i - 0.5, i + 0.5], color=mark, linewidth=3.0, solid_capstyle="butt", zorder=6)
    names = list(half)
    if len(names) == 2 and half[names[0]] != half[names[1]]:
        i0, i1 = rows.index(names[0]), rows.index(names[1])
        ax.annotate("", xy=(half[names[1]] + 0.5, (i0 + i1) / 2), xytext=(half[names[0]] + 0.5, (i0 + i1) / 2),
                    arrowprops=dict(arrowstyle="-|>", linewidth=1.5, color=mark, mutation_scale=10), zorder=7)
    ax.set_yticks(range(m.shape[0]), rows)
    ax.set_xticks(range(m.shape[1]), list(mat.columns), rotation=90)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return ax


#: the line of each archetype set on the discovery curve: dash and width (black on white: a set is not a class)
DISCOVERY_STYLE = {"A0": ("-", 1.8), "A0c": ("--", 1.8), "A1t": ((0, (1.2, 1.4)), 2.2)}


def discovery_lines(ax, curve: pd.DataFrame, names: dict, tail: int, tail_box: Optional[Bbox] = None):
    """The discovery curve of each archetype set: distinct archetypes seen against the aircraft added in priority order (a
    black line, the grey band the spread over tie orderings inside a year) and, in light grey, the same count with the
    aircraft in a random order. The last ``tail`` aircraft are shaded. ``curve``: columns level, aircraft, archetypes (date
    order), 2.5 %, 97.5 %, archetypes (random order); ``names``: level -> printed set code."""
    n_max = int(curve["aircraft"].max())
    ax.axvspan(n_max - tail, n_max, color="#ececec", zorder=0, linewidth=0)
    for lvl, g in curve.groupby("level", sort=False):
        ls, lw = DISCOVERY_STYLE[lvl]
        x = g["aircraft"].to_numpy()
        ax.fill_between(x, g["2.5 %"], g["97.5 %"], color="#bdbdbd", alpha=0.6, linewidth=0, zorder=1)
        ax.plot(x, g["archetypes (random order)"], color="#8c8c8c", linewidth=0.9, linestyle=(0, (1, 1.8)), zorder=2)
        ax.plot(x, g["archetypes (date order)"], color=INK, linewidth=lw, linestyle=ls, zorder=4,
                label=f"{names[lvl]}: {int(g['archetypes (date order)'].iloc[-1] + 1e-9)} archetypes in {len(g)} aircraft")
    ax.set_xlim(0, n_max * 1.0 + 3)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


# ====================================================================================== chapter 3 (notebook 42)
#: the window ticks as the figures print them
WINDOW_TICKS = {"<= 2011": "≤2011", "2012-15": "2012–15", "2016-19": "2016–19", "2020-23": "2020–23", "2024-26 (partial)": "2024–26*"}
#: the fill of the windows that hold few aircraft, and the colour of a condition that is MET (a status, not a class)
FEW_FILL = "#efeeec"
MET = "#d62728"


def few_band(ax, n_few: int = 2, text: Optional[str] = "few aircraft", fontsize: float = 7.0):
    """Grey the first ``n_few`` windows (x positions 0..n_few-1) behind a dashed line and say why."""
    ax.axvspan(-0.5, n_few - 0.5, color=FEW_FILL, zorder=0, linewidth=0)
    ax.axvline(n_few - 0.5, color=MUTED, linewidth=0.8, linestyle="--", zorder=1)
    if text:
        ax.text((n_few - 1) / 2, 0.985, text, transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=fontsize, color=MUTED)


def window_lines(ax, frame: pd.DataFrame, n_few: int = 2, ticks: Optional[Sequence[str]] = None, linewidth: float = 1.4,
                 markersize: float = 4.6):
    """One line per class (columns) over the windows (rows, x = 0..k-1), the class's colour, dash and marker; the markers of the
    first ``n_few`` windows are hollow (few aircraft). A missing value breaks nothing: the line joins the drawn windows."""
    x = np.arange(len(frame))
    for c in _ordered(frame.columns):
        s = cls(c)
        y = frame[c].to_numpy(dtype=float)
        ok = np.isfinite(y)
        ax.plot(x[ok], y[ok], color=s.color, linestyle=s.dash, linewidth=linewidth, zorder=3, solid_capstyle="round")
        for xi in x[ok]:
            ax.plot(xi, y[xi], marker=s.marker, markersize=markersize, color=s.color, markeredgecolor=s.color, markeredgewidth=1.0,
                    markerfacecolor="white" if xi < n_few else s.color, linestyle="none", zorder=4)
    ax.set_xticks(x, list(ticks) if ticks is not None else [str(i) for i in frame.index])
    return ax


def end_labels(ax, x_end: float, ys: Sequence[float], texts: Sequence[str], colors: Sequence[str], gap: float, dx_pt: float = 7.0,
               fontsize: Optional[float] = None):
    """Text at the right end of lines, spread apart by at least ``gap`` (data units) in their order, with a leader where moved."""
    placed = _spread(list(ys), gap)
    fs = fontsize if fontsize is not None else mpl.rcParams["xtick.labelsize"]
    for y0, yl, t, col in zip(ys, placed, texts, colors):
        ax.annotate(t, xy=(x_end, y0), xytext=(dx_pt, yl), textcoords=("offset points", "data"), va="center", ha="left",
                    fontsize=fs, color=INK, annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.4, shrinkA=0, shrinkB=2) if abs(yl - y0) > 1e-9 else None)


def tint(color: str, k: float):
    """``color`` mixed with white: k = 1 the colour itself, k = 0 white."""
    r, g, b = mpl.colors.to_rgb(color)
    return (1 - k * (1 - r), 1 - k * (1 - g), 1 - k * (1 - b))


def config_stack(ax, comp: pd.DataFrame, color: str, n_few: int = 2, min_label: float = 0.12, shades: Sequence[float] = (1.0, 0.62, 0.36, 0.17),
                 other_color: str = "#e4e3df", other_name: str = "other configurations"):
    """The composition of one class per window: rows = windows, columns = configurations (the first column is the bottom block,
    the leader of the last window), each a share of the class; the blocks are tints of the class colour, the last column
    (``other_name``) grey. The first ``n_few`` windows are faded. A block of ``min_label`` or more prints its percentage."""
    x = np.arange(len(comp))
    bottom = np.zeros(len(comp))
    for k, c in enumerate(comp.columns):
        vals = comp[c].fillna(0).to_numpy(dtype=float)
        other = c == other_name
        fc = other_color if other else tint(color, shades[min(k, len(shades) - 1)])
        for xi in x:
            ax.bar(xi, vals[xi], bottom=bottom[xi], width=0.68, color=fc, edgecolor="white" if k == 0 else tint(INK, 0.55), linewidth=0.5,
                   alpha=0.55 if xi < n_few else 1.0, zorder=3, label=c if xi == 0 else None)
            if vals[xi] >= min_label:
                dark = k == 0
                ax.text(xi, bottom[xi] + vals[xi] / 2, f"{100 * vals[xi]:.0f}", ha="center", va="center", zorder=5,
                        fontsize=mpl.rcParams["xtick.labelsize"] - 0.5, color=_text_on(color) if dark else INK,
                        bbox=None if dark else dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.7))
        bottom = bottom + vals
    ax.axvline(n_few - 0.5, color=MUTED, linewidth=0.8, linestyle="--", zorder=5)
    ax.set_ylim(0, 1.0)
    ax.set_xlim(-0.5, len(comp) - 0.5)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    return ax


def condition1_years(ax, years: Sequence[int], in_force: Sequence[float], every: Sequence[float], read_force: Sequence[bool],
                     read_all: Sequence[bool], met: Sequence[int], first_read: int, few_text: str):
    """Condition 1 on one archetype, per priority year: its share of the aircraft with a patent in force (solid, dots) and of
    all aircraft (dashed, squares) against the 50 % line; years under the read minimum are faded behind a vertical line; two
    consecutive years above 50 % are ringed in the MET colour (``met``)."""
    yrs = np.asarray(years)
    fi, fa = np.asarray(in_force, dtype=float), np.asarray(every, dtype=float)
    ax.axvspan(yrs[0] - 0.5, first_read - 0.5, color=FEW_FILL, zorder=0, linewidth=0)
    ax.axvline(first_read - 0.5, color=MUTED, linewidth=0.8, zorder=1)
    ax.text((yrs[0] + first_read - 1) / 2, 0.97, few_text, ha="center", va="top", fontsize=7, color=MUTED, transform=ax.get_xaxis_transform())
    for y_, ls, mk, lw, fill, rd in ((fi, "-", "o", 1.7, INK, np.asarray(read_force)), (fa, "--", "s", 1.2, MUTED, np.asarray(read_all))):
        ax.plot(yrs[yrs <= first_read], y_[yrs <= first_read], color=fill, linestyle=ls, linewidth=lw, alpha=0.35, zorder=3)
        ax.plot(yrs[yrs >= first_read], y_[yrs >= first_read], color=fill, linestyle=ls, linewidth=lw, zorder=3)
        ax.plot(yrs[rd], y_[rd], linestyle="", marker=mk, markersize=4.4, color=fill, markerfacecolor=fill if ls == "-" else "white",
                markeredgecolor=fill, zorder=4)
        ax.plot(yrs[~rd], y_[~rd], linestyle="", marker=mk, markersize=4.0, color=fill, markerfacecolor="white", markeredgecolor=fill,
                alpha=0.45, zorder=4)
    ax.axhline(0.5, color=INK, linewidth=1.0, linestyle=(0, (4, 2)), zorder=2)
    if met:
        ax.axvspan(min(met) - 0.5, max(met) + 0.5, color=MET, alpha=0.09, zorder=0, linewidth=0)
        idx = [list(yrs).index(m) for m in met]
        ax.plot(yrs[idx], fi[idx], "o", markersize=10.5, markerfacecolor="none", markeredgecolor=MET, markeredgewidth=1.7, zorder=5)
    ax.set_ylim(0, 0.85)
    ax.set_xlim(yrs[0] - 0.6, yrs[-1] + 0.6)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


#: the second base of a condition figure (handoff 2026-10-15, Task 3: the actively protected designs beside all designs) and, before
#: that, the exploratory level F: neutral grey, dashed, hollow markers, outside the scheme of the pre-specified levels
EXPLORE = dict(color="#8c8c8c", linestyle="--", markerfacecolor="white")
#: the third base of condition 1 (granted and live): the same grey, dotted, hollow triangles
GRANTED = dict(color="#8c8c8c", linestyle=":", markerfacecolor="white")


def balance_panel(ax, s: pd.DataFrame, partial: Sequence[bool], met: Sequence[bool], ticks: Sequence[str], exploratory: bool = False):
    """Condition 2 for one archetype set: ²D per window (a dot with its 95 % whisker over the rarefaction draws) against the
    grey permutation band (``D2 permutation low`` / ``high``); a window below its band (``met``) is a MET-coloured dot; a
    partial window is hatched and not read. ``s`` has columns D2, D2 low, D2 high, D2 permutation low, D2 permutation high."""
    x = np.arange(len(s))
    ax.fill_between(x, s["D2 permutation low"], s["D2 permutation high"], color="#dedcd8", zorder=1, linewidth=0)
    look = dict(EXPLORE) if exploratory else dict(color=INK)
    eb = ax.errorbar(x, s["D2"], yerr=[s["D2"] - s["D2 low"], s["D2 high"] - s["D2"]], marker="o", markersize=3.6, linewidth=1.3, capsize=1.8,
                     zorder=3, **look)
    if exploratory:
        for b in eb[2]:
            b.set_linestyle("-")                    # the whiskers stay solid; the line between the cohorts is dashed
    hit = [i for i, m in enumerate(met) if m]
    if hit:
        if exploratory:                             # a hollow red ring: met, but on an exploratory level
            ax.plot(x[hit], s["D2"].to_numpy()[hit], "o", markersize=7.2, markerfacecolor="none", markeredgecolor=MET, markeredgewidth=1.4, zorder=5)
        else:
            ax.plot(x[hit], s["D2"].to_numpy()[hit], "o", markersize=7.2, color=MET, markeredgecolor=INK, markeredgewidth=0.8, zorder=5)
    for i, p in enumerate(partial):
        if p:
            ax.axvspan(i - 0.5, i + 0.5, facecolor=FEW_FILL, zorder=0, linewidth=0, hatch=PARTIAL_HATCH, edgecolor=GRID)
    ax.set_xticks(x, ticks, rotation=90, ha="center", va="top")
    ax.set_xlim(-0.5, len(s) - 0.5)
    ax.set_ylim(0, float(np.nanmax(s[["D2 high", "D2 permutation high"]].to_numpy())) * 1.15)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def cohesion_panel(ax, main: pd.DataFrame, alt: pd.DataFrame, partial: Sequence[bool], ticks: Sequence[str], exploratory: bool = False):
    """Condition 3: ΔQ per window against its permutation band under the main weighting (solid line, grey band) and under the
    check (dashed line, dotted band edges); a window below the main band is a MET-coloured dot; partial windows hatched."""
    x = np.arange(len(main))
    ax.fill_between(x, main["ΔQ permutation low"], main["ΔQ permutation high"], color="#dedcd8", zorder=1, linewidth=0)
    if alt is not None:
        ax.plot(x, alt["ΔQ permutation low"], color=MUTED, linewidth=0.9, linestyle=":", zorder=2)
        ax.plot(x, alt["ΔQ permutation high"], color=MUTED, linewidth=0.9, linestyle=":", zorder=2)
    ax.axhline(0, color=MUTED, linewidth=0.8, zorder=2)
    ax.plot(x, main["ΔQ"], marker="o", markersize=3.6, linewidth=1.5, zorder=4, **(dict(EXPLORE) if exploratory else dict(color=INK)))
    if alt is not None:
        ax.plot(x, alt["ΔQ"], marker="^", markersize=3.8, linewidth=1.2, color=MUTED, linestyle="--", zorder=4)
    hit = [i for i, (q, lo) in enumerate(zip(main["ΔQ"], main["ΔQ permutation low"])) if q < lo and not partial[i]]
    if hit and exploratory:                         # a hollow red ring: met, but on an exploratory level
        ax.plot(x[hit], main["ΔQ"].to_numpy()[hit], "o", markersize=7.2, markerfacecolor="none", markeredgecolor=MET, markeredgewidth=1.4, zorder=5)
    elif hit:
        ax.plot(x[hit], main["ΔQ"].to_numpy()[hit], "o", markersize=7.2, color=MET, markeredgecolor=INK, markeredgewidth=0.8, zorder=5)
    for i, p in enumerate(partial):
        if p:
            ax.axvspan(i - 0.5, i + 0.5, facecolor=FEW_FILL, zorder=0, linewidth=0, hatch=PARTIAL_HATCH, edgecolor=GRID)
    ax.set_xticks(x, ticks)
    ax.set_xlim(-0.5, len(main) - 0.5)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def band_series_panel(ax, main: pd.DataFrame, alt: Optional[pd.DataFrame], partial: Sequence[bool], ticks: Sequence[str], value: str,
                      low: str, high: str, whisk: Optional[Sequence[str]] = None, main_met: Optional[Sequence[bool]] = None,
                      alt_met: Optional[Sequence[bool]] = None, zero_line: bool = False):
    """One condition (2 or 3) of one archetype set on two bases: the main series (all designs, INK, solid; a whisker per window
    when ``whisk`` names its low/high columns) against its grey permutation band (``low`` / ``high`` of ``main``), and the second
    base (``alt``: the actively protected designs) as a grey dashed line with hollow markers and no band. A window where the
    condition is met is a MET-coloured dot on the main series (``main_met``) and a hollow MET ring on the second (``alt_met``);
    a partial window is hatched. Rows of ``main`` and ``alt`` are the windows in order (x = 0..k-1)."""
    x = np.arange(len(main))
    ax.fill_between(x, main[low], main[high], color="#dedcd8", zorder=1, linewidth=0)
    if zero_line:
        ax.axhline(0, color=MUTED, linewidth=0.8, zorder=2)
    if alt is not None:
        ax.plot(x, alt[value].to_numpy(dtype=float), marker="o", markersize=3.6, linewidth=1.3, zorder=3, **EXPLORE)
        hit = [i for i, m in enumerate(alt_met or []) if m]
        if hit:
            ax.plot(x[hit], alt[value].to_numpy(dtype=float)[hit], "o", markersize=9.6, markerfacecolor="none", markeredgecolor=MET,
                    markeredgewidth=1.4, zorder=5)         # wider than the main base's dot: the two bases can meet at nearly the same value
    y = main[value].to_numpy(dtype=float)
    if whisk is not None:
        ax.errorbar(x, y, yerr=[y - main[whisk[0]], main[whisk[1]] - y], marker="o", markersize=3.6, linewidth=1.4, capsize=1.8, color=INK, zorder=4)
    else:
        ax.plot(x, y, marker="o", markersize=3.6, linewidth=1.5, color=INK, zorder=4)
    hit = [i for i, m in enumerate(main_met or []) if m]
    if hit:
        ax.plot(x[hit], y[hit], "o", markersize=7.2, color=MET, markeredgecolor=INK, markeredgewidth=0.8, zorder=6)
    for i, p in enumerate(partial):
        if p:
            ax.axvspan(i - 0.5, i + 0.5, facecolor=FEW_FILL, zorder=0, linewidth=0, hatch=PARTIAL_HATCH, edgecolor=GRID)
    ax.set_xticks(x, ticks, rotation=90, ha="center", va="top")
    ax.set_xlim(-0.5, len(main) - 0.5)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def condition1_bases(ax, years: Sequence[int], bases: Sequence[dict], ring: Optional[Sequence[int]] = None):
    """Condition 1 on one archetype set per priority year on several bases against the 50 % line. Each base is a dict with
    ``share`` (per year), ``read`` (per year: drawn only where True), ``look`` (line kwargs: color, linestyle, markerfacecolor) and
    ``marker``; the first base is the main one. The years in ``ring`` are ringed in the MET colour on the main base."""
    yrs = np.asarray(years)
    for k, b in enumerate(bases):
        sh, rd = np.asarray(b["share"], dtype=float), np.asarray(b["read"], dtype=bool)
        look = dict(b["look"])
        col = look.pop("color")
        ax.plot(yrs[rd], sh[rd], marker=b["marker"], markersize=4.4 if k == 0 else 4.0, linewidth=1.7 if k == 0 else 1.2, color=col,
                markeredgecolor=col, zorder=4 if k == 0 else 3, **look)
    ax.axhline(0.5, color=INK, linewidth=1.0, linestyle=(0, (4, 2)), zorder=2)
    if ring:
        main = bases[0]
        idx = [list(yrs).index(y) for y in ring]
        ax.plot(yrs[idx], np.asarray(main["share"], dtype=float)[idx], "o", markersize=10.5, markerfacecolor="none", markeredgecolor=MET,
                markeredgewidth=1.7, zorder=5)
    ax.set_ylim(0, 0.85)
    ax.set_xlim(yrs[0] - 0.6, yrs[-1] + 0.6)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def centre_trajectory(ax, centres: dict, n_few: int = 2, markersize: float = 6.0):
    """Each class's centre per window as a point (x = ``x``, y = ``y`` of its frame, rows = windows), joined by arrows in time order;
    the first ``n_few`` windows hollow and faint. Returns the points as (x, y, window index, class code) for labelling."""
    pts = []
    for code, d in centres.items():
        s = cls(code)
        xs, ys = d["x"].to_numpy(dtype=float), d["y"].to_numpy(dtype=float)
        for k in range(len(d)):
            if not (np.isfinite(xs[k]) and np.isfinite(ys[k])):
                continue
            early = k < n_few
            ax.plot(xs[k], ys[k], marker=s.marker, markersize=markersize, color=s.color, markeredgecolor=s.color,
                    markerfacecolor="white" if early else s.color, alpha=0.6 if early else 1.0, linestyle="none", zorder=4)
            pts.append((xs[k], ys[k], k, code))
            if k + 1 < len(d) and np.isfinite(xs[k + 1]) and np.isfinite(ys[k + 1]):
                ax.annotate("", xy=(xs[k + 1], ys[k + 1]), xytext=(xs[k], ys[k]), zorder=3,
                            arrowprops=dict(arrowstyle="->", color=s.color, linewidth=1.3, shrinkA=4, shrinkB=4, alpha=0.4 if k + 1 < n_few else 1.0))
    return pts


# =====================================================================================================
# Question 4 (the filers): primitives of notebook 43
# =====================================================================================================
#: the three filer types are not classes: greys told apart by lightness and hatch (colour, hatch). Print-safe.
FILER_STYLE = {"Named company": ("#595959", ""), "University / institute": ("#a6a6a6", "////"), "Individual inventor": ("#e3e3e3", "....")}
#: first-time and returning filers (dark, light grey)
ENTRY_COLORS = ("#595959", "#c9c9c9")


def stack_bars(ax, parts: pd.DataFrame, styles: dict, positions: Optional[Sequence[float]] = None, width: float = 0.72,
               horizontal: bool = False, partial: Sequence[int] = (), min_label: float = 0.08, label_fmt: str = "{:.0f} %",
               fontsize: Optional[float] = None, label_pad: float = 0.12, no_label: Sequence[int] = ()):
    """Stacked 100 % bars, one per row of ``parts``, one segment per column, in the column order. ``styles`` maps a column to
    (colour, hatch) or to a ``viz.style.ClassStyle``. A bar whose row position is in ``partial`` is faded (a window not complete);
    a segment of at least ``min_label`` prints its percentage on a box of its own colour (not on a bar whose row position is in ``no_label``).
    Rows are normalised to sum to 1 here (a row that sums to 0 draws nothing).
    Returns the artists in column order (for a legend)."""
    shares = parts.div(parts.sum(axis=1), axis=0).fillna(0)
    pos = np.arange(len(shares), dtype=float) if positions is None else np.asarray(positions, dtype=float)
    bottom = np.zeros(len(shares))
    bar = ax.barh if horizontal else ax.bar
    fs = fontsize if fontsize is not None else mpl.rcParams["xtick.labelsize"] - 0.5
    arts = []
    for c in shares.columns:
        st = styles[c]
        color, hatch = (st.color, st.hatch) if hasattr(st, "color") else st
        vals = shares[c].to_numpy()
        bars = bar(pos, vals, width, **({"left": bottom} if horizontal else {"bottom": bottom}), color=color, hatch=hatch,
                   edgecolor="white", linewidth=0.6, label=c, zorder=3)
        arts.append(bars)
        for i, (b, v_, b0) in enumerate(zip(bars, vals, bottom)):
            if i in partial:
                b.set_alpha(0.5)
            if v_ >= min_label and i not in no_label:
                x, y = ((b0 + v_ / 2, pos[i]) if horizontal else (pos[i], b0 + v_ / 2))
                ax.text(x, y, label_fmt.format(100 * v_), ha="center", va="center", fontsize=fs, color=_text_on(color), zorder=5,
                        bbox=dict(boxstyle="square,pad=0.15", facecolor=color, edgecolor="none", alpha=0.9))
        bottom = bottom + vals
    return arts
