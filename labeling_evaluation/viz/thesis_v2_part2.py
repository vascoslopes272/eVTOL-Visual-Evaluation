"""Part II (Design space) figures, v2: relabelled, simplified and regrouped versions of a subset of the Q6 / Q7
thesis figures (THESIS_CONTRACT.md). Every number and every underlying frame is read from viz/thesis_q6.py and
viz/thesis_q7.py unchanged; this module only re-draws, re-labels and re-groups them for
thesis_figures_v2/Part_II_design_space/ (see its README.md). The originals in thesis_figures/ are never touched.

Terminology (author's ruling, 2026-10-11), in every label, legend, axis and title:
    archetype -> configuration      aircraft (as a count) -> design      filer -> assignee
    window -> cohort                class -> architecture                Multirotor -> Multicopter
    Tilt Body TB -> Tilt Frame TF   Tilt Propulsor = TP                  Lift + Cruise code = SLC
    levels of description are written A, A·W·T, A·U (A = architecture; was C before 2026-10-13).
Style: the Part I v2 style, 6.3 in wide, no text under 8 pt at print size, no in-plot text boxes, no label that
overlaps a mark or another label, a legend only for what is drawn, at most ~6 colours per figure (the rest grey).
"""
from __future__ import annotations

import dataclasses
import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text
from matplotlib.transforms import Bbox

from lib import diversity
from viz import frames, plots, style
from viz import thesis_q6 as q6
from viz import thesis_q7 as q7
from viz import thesis_v2_part1 as p1

# ================================================================================== thesis style (2026-10-20 restyle of Figs 4.6-4.8)
import sys as _sys
import pathlib as _pathlib
_NB = _pathlib.Path(__file__).resolve().parents[1] / "notebooks"
if str(_NB) not in _sys.path:
    _sys.path.insert(0, str(_NB))
import thesis_style as ts                                     # noqa: E402

#: the figures of this module drawn in the thesis style (notebooks/thesis_style.py): full text width, ts.save, no bbox crop
TS_FIGS = {"q6_configuration_core", "q6_half_of_cohort", "q6_discovery_curve"}
TS_H = {"q6_configuration_core": 2.45, "q6_half_of_cohort": 2.4, "q6_discovery_curve": 2.3}
NOTE = "#555555"                                              # dark grey of the 8 pt notes (local; candidate for thesis_style)


def ts_tint(color, k: float):
    """``color`` mixed with white (k = 1 the colour, k = 0 white). Local helper; candidate for thesis_style."""
    r, g, b = mpl.colors.to_rgb(color)
    return (1 - k * (1 - r), 1 - k * (1 - g), 1 - k * (1 - b))


def ts_ink_on(color) -> str:
    """White or near-black text, whichever reads on ``color`` (relative luminance). Local helper; candidate for thesis_style."""
    r, g, b = mpl.colors.to_rgb(color)
    return "#1a1a1a" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else "white"


def ts_spread(ys, gap: float, lo: float = -np.inf, hi: float = np.inf) -> np.ndarray:
    """Positions as near as possible to ``ys`` with at least ``gap`` between neighbours, kept inside [lo, hi] (end-label de-overlap)."""
    ys = np.asarray(ys, dtype=float)
    order = np.argsort(ys)
    y = ys[order].copy()
    for _ in range(200):
        moved = False
        for i in range(1, len(y)):
            d = y[i] - y[i - 1]
            if d < gap - 1e-9:
                push = (gap - d) / 2
                y[i - 1] -= push
                y[i] += push
                moved = True
        if len(y):
            if y[0] < lo:
                y += lo - y[0]
                moved = True
            if y[-1] > hi:
                y -= y[-1] - hi
                moved = True
        if not moved:
            break
    out = np.empty_like(y)
    out[order] = y
    return out


def ts_pt_to_data(ax, pt: float) -> float:
    """``pt`` points as a distance along the y axis of ``ax`` (data units), at the drawn size."""
    ax.figure.canvas.draw()
    h_px = ax.get_window_extent().height
    y0, y1 = ax.get_ylim()
    return pt * ax.figure.dpi / 72 / h_px * (y1 - y0)


def ts_rc():
    """The thesis rc as a context (so a figure drawn inside a part1.mplstyle caller still gets the thesis style and no bbox crop)."""
    return mpl.rc_context(ts.RC)

FS = 8.0                      # the smallest text of any figure, pt at print size
TITLE_FS = 9.0
LEVEL = {"A0": "A", "A1t": "A·W·T", "A0c": "A·U"}      # printed names of the levels of description
GREY = "#9a9a9a"              # the unlabelled marks
SHADE = "#c9c9c9"
TAIL_FILL = "#dce9f5"         # the last-100-designs window

# --------------------------------------------------------------------------------------- terminology layer
ARCH_NAME_OVERRIDE = {**p1.ARCH_NAME_OVERRIDE, "MR": "Multicopter"}      # style.py: TB "Tilt Body", MR "Multirotor"
ARCH_SHORT_OVERRIDE = {**p1.ARCH_SHORT_OVERRIDE}                          # TB -> TF, SLC -> SLC (style.py: "L+C")
#: style.py's printed architecture names -> this document's short code (to read names inside the frames' strings)
_STYLE_NAME_TO_SHORT = {style.cls(c).name: ARCH_SHORT_OVERRIDE.get(c, style.cls(c).short) for c in style.CLASS_ORDER}


def arch(code: str):
    """style.cls(code) with this document's names and short codes."""
    s = style.cls(code)
    return dataclasses.replace(s, name=ARCH_NAME_OVERRIDE.get(code, s.name), short=ARCH_SHORT_OVERRIDE.get(code, s.short))


def cfg_label(key: str) -> str:
    """An A·U configuration key as the figures print it: 'SLC · 9+' -> 'SLC 9+', 'TB · 1-3' -> 'TF 1–3',
    'HB · n/a (no M3 card)' -> 'HB'. The suffix is the propulsor-unit band."""
    c, _, b = key.partition(" · ")
    b = _dash(b.replace("n/a (no M3 card)", ""))
    return f"{arch(c).short} {b}".strip()


def _dash(s: str) -> str:
    """En dash in number ranges; the lowest propulsor band has ONE name everywhere: 1–3 (rerun of 2026-10-15: the one design recorded
    with 0 propulsors is left out, frames.propulsor_units)."""
    return re.sub(r"(?<=\d)-(?=\d)", "–", s)


def code_key(codes) -> str:
    """'SLC Separate Lift + Cruise · TP Tilt Propulsor · …': the full name of every architecture code a figure prints on its points or columns."""
    return " · ".join(f"{arch(c).short} {arch(c).name}" for c in codes)


def code_key_lines(fig, codes, fs: float = 7.0, share: float = 0.95) -> str:
    """:func:`code_key` broken into lines that fit ``share`` of the figure's width at ``fs`` pt (measured with the figure's renderer)."""
    rend = fig.canvas.get_renderer()
    width_px = fig.get_figwidth() * fig.dpi * share

    def w(t):
        tt = fig.text(0, 0, t, fontsize=fs)
        out = tt.get_window_extent(rend).width
        tt.remove()
        return out
    lines, cur = [], ""
    for item in (f"{arch(c).short} {arch(c).name}" for c in codes):
        cand = item if not cur else cur + " · " + item
        if cur and w(cand) > width_px:
            lines.append(cur + " ·")
            cur = item
        else:
            cur = cand
    return "\n".join(lines + [cur])


def _arch_legend(codes):
    return [Line2D([], [], marker="o", markersize=6, linestyle="none", markerfacecolor=arch(c).color, markeredgecolor="white",
                   label=f"{arch(c).short} {arch(c).name}") for c in codes]


# --------------------------------------------------------------------------------------- small drawing helpers
def _free_spot(ax, size, avoid, targets, step=0.01):
    """Display-space box origin for a label of ``size`` (w, h px): the free position (inside the axes, clear of every
    box in ``avoid``) nearest to one of the display points ``targets``. Returns the origin or None."""
    axbb = ax.get_window_extent()
    best, best_d = None, np.inf
    for fx in np.arange(0.01, 0.99, step):
        for fy in np.arange(0.01, 0.99, step):
            x0, y0 = axbb.x0 + fx * axbb.width, axbb.y0 + fy * axbb.height
            bb = Bbox([[x0, y0], [x0 + size[0], y0 + size[1]]])
            if bb.x1 > axbb.x1 - 2 or bb.y1 > axbb.y1 - 2 or any(bb.overlaps(b) for b in avoid):
                continue
            cx, cy = x0 + size[0] / 2, y0 + size[1] / 2
            dist = min(np.hypot(cx - tx, cy - ty) for tx, ty in targets)
            if dist < best_d:
                best, best_d = (x0, y0), dist
    return best


def _label_size(ax, text, fs=FS, weight="normal"):
    t = ax.text(0, 0, text, fontsize=fs, fontweight=weight)
    bb = t.get_window_extent(ax.figure.canvas.get_renderer())
    t.remove()
    return bb.width + 4, bb.height + 3


def _box_gap(bb: Bbox, p) -> float:
    """Distance in px from the display point ``p`` to the box ``bb`` (0 inside)."""
    return float(np.hypot(max(bb.x0 - p[0], 0, p[0] - bb.x1), max(bb.y0 - p[1], 0, p[1] - bb.y1)))


def _place_point_labels(ax, xy, labels, r_pt, avoid, all_xy, fs=FS, max_r_pt=30.0):
    """Label points so that no label touches another label, a mark, an ``avoid`` box or the axes edge, and so that each label
    is nearer to its own point than to any other. A label that cannot sit next to its point gets a short leader (≤ ``max_r_pt``).
    ``xy``: data positions of the labelled points; ``all_xy``: every mark of the axes (the labelled ones included).
    Returns the labels that found no place."""
    fig = ax.figure
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    k = fig.dpi / 72
    P = ax.transData.transform(np.asarray(xy, dtype=float))
    A = ax.transData.transform(np.asarray(all_xy, dtype=float))
    rad = r_pt * k
    marks = [Bbox([[x - rad, y - rad], [x + rad, y + rad]]) for x, y in A]
    axbb = ax.get_window_extent(rend)
    sizes = [_label_size(ax, t, fs) for t in labels]
    near = [(np.hypot(*(P - p).T) < 45 * k).sum() for p in P]
    angles = np.deg2rad([0, 180, 30, 150, 330, 210, 90, 270, 60, 120, 300, 240, 15, 165, 345, 195, 45, 135, 315, 225, 75, 105, 285, 255])
    base = sorted(range(len(P)), key=lambda i: -near[i])
    rng = np.random.default_rng(0)
    best = None
    for trial in range(300):                 # the crowded-first order first, then shuffled orders until every label has a place
        order = base if trial == 0 else list(rng.permutation(len(P)))
        placed, fails, plan = [], [], []
        for q in order:
            w, h = sizes[q]
            others = [a for a in A if np.hypot(*(a - P[q])) > 1e-6]
            done = False
            for r in np.arange(r_pt + 2.0, max_r_pt, 2.0):
                for th in angles:
                    px, py = P[q][0] + r * k * np.cos(th), P[q][1] + r * k * np.sin(th)
                    x0 = px if np.cos(th) > 0.3 else px - w if np.cos(th) < -0.3 else px - w / 2
                    y0 = py if np.sin(th) > 0.3 else py - h if np.sin(th) < -0.3 else py - h / 2
                    bb = Bbox([[x0, y0], [x0 + w, y0 + h]])
                    if not (axbb.x0 + 1 <= bb.x0 and bb.x1 <= axbb.x1 - 1 and axbb.y0 + 1 <= bb.y0 and bb.y1 <= axbb.y1 - 1):
                        continue
                    if any(bb.overlaps(b) for b in marks + list(avoid) + placed):
                        continue
                    own = _box_gap(bb, P[q])
                    if r <= r_pt + 4 and any(_box_gap(bb, o) <= own + 3 * k for o in others):      # a label with a leader is tied to its point by the line
                        continue
                    if r > r_pt + 4:                    # a leader never runs through another mark
                        end = np.array([min(max(P[q][0], bb.x0), bb.x1), min(max(P[q][1], bb.y0), bb.y1)])
                        seg = P[q] + (end - P[q]) * np.linspace(0, 1, 40)[:, None]
                        if any(np.hypot(*(seg - o).T).min() < rad + 1 for o in others):
                            continue
                        bb = Bbox.union([bb, Bbox([seg.min(axis=0) - 1, seg.max(axis=0) + 1])])      # the label's extent counts its leader
                        if any(bb.overlaps(b) for b in placed):
                            continue
                    placed.append(bb)
                    plan.append((q, r, th))
                    done = True
                    break
                if done:
                    break
            if not done:
                fails.append(labels[q])
        if best is None or len(fails) < len(best[0]):
            best = (fails, plan)
        if not fails:
            break
    fails, plan = best
    for q, r, th in plan:
        ha = "left" if np.cos(th) > 0.3 else "right" if np.cos(th) < -0.3 else "center"
        va = "bottom" if np.sin(th) > 0.3 else "top" if np.sin(th) < -0.3 else "center"
        ax.annotate(labels[q], xy=tuple(xy[q]), xytext=(r * np.cos(th), r * np.sin(th)), textcoords="offset points", ha=ha,
                    va=va, fontsize=fs, color=style.INK, zorder=8,
                    arrowprops=dict(arrowstyle="-", linewidth=0.5, color=style.INK, shrinkA=0, shrinkB=r_pt) if r > r_pt + 4 else None)
    return fails


def _ring_boxes(h, pad=3.0):
    pts = [a + (b - a) * t for a, b in zip(h, np.roll(h, -1, axis=0)) for t in np.linspace(0, 1, 14)]
    return [Bbox([[x - pad, y - pad], [x + pad, y + pad]]) for x, y in pts]


# ================================================================================== II1. varying attributes
#: option names of Table 6 as the thesis table prints them -> short forms
OPTION_SHORT = {
    "Tailless (None)": "Tailless", "Conventional (Horizontal at base)": "Conventional", "V-Tail": "V-tail",
    "Single Vertical Fin Only (No Horizontal Stabilizer)": "Single fin", "Fixed / Conventional": "Fixed",
    "Whole-Body Pitch": "Whole-body pitch", "Variable Incidence": "Variable incidence", "Standard Wings": "Standard",
    "Blended Wing Body": "Blended wing body", "Lifting Body": "Lifting body", "Wheeled Gear": "Wheeled",
    "Skids / Fixed Skids": "Skids", "Tail-sitter": "Tail-sitter",
    # fuselage shape (2026-10-16): the codebook's base names
    "Circular / Tubular": "Circular", "Oval / Elliptical": "Oval", "Rectangular / Box": "Rectangular", "Blended / Lifting Body": "Blended",
    "Pod and Boom (legacy — re-pick the base shape)": "Pod and boom (legacy)",
}


def _short_options(s: str) -> str:
    out = []
    for item in s.split(" · "):
        name, cnt = item.rsplit(": ", 1)
        out.append(f"{_dash(OPTION_SHORT.get(name, name))}: {cnt}")
    return " · ".join(out)


def tab_selected_fields_v2(ctx):
    """II1 main: Table 6, the dimensions whose most common option holds under the cut-off. Columns renamed
    (designs answering, options, top share, most common options); option names shortened; 'aircraft' -> 'design'.
    Rows sorted by top share, lowest first (rerun of 2026-10-15), on the top share before rounding to whole percent."""
    df, _ = q6.tab_selected_fields(ctx)
    t6 = q6._data(ctx)["t6"]
    share = t6.loc[t6["top_share"] < q6._data(ctx)["cut"], "top_share"].to_numpy()
    df = df.iloc[np.argsort(share, kind="stable")].reset_index(drop=True)
    t = pd.DataFrame({
        "dimension": df["field"].str.replace("aircraft", "design", regex=False),
        "designs answering": df["aircraft answering"],
        "options": df["different answers"],
        "top share": df["top share"],
        "most common options": df["most common answers: aircraft"].map(_short_options),
    })
    return t, None


def _fixed_tables(ctx):
    summary, detail = q6.fixed_by_architecture(ctx)
    dim = lambda s: s.str.replace("aircraft", "design", regex=False)             # noqa: E731
    name = lambda c: arch(c).name                                                # noqa: E731
    pval = lambda p: f"{p:.3f}" if p > 0 else f"< {1 / q6.FIXED_PERMS:.3f}"       # noqa: E731  0 hits in 1 000 shuffles: below the resolution
    t1 = pd.DataFrame({
        "dimension": dim(summary["dimension"]),
        "designs answering": summary["designs answering"],
        "Cramér's V": summary["cramers_v"].map(lambda x: f"{x:.2f}"),
        "p": summary["p"].map(pval),
        "architectures at 80 % or more": [f"{f} of {r} read" for f, r in zip(summary["fixed"], summary["read"])],
        "architectures too few to read": summary["too few codes"].map(lambda cs: ", ".join(name(c) for c in cs) or "none"),
    })
    t2 = pd.DataFrame({
        "dimension": dim(detail["dimension"]),
        "architecture": detail["code"].map(name),
        "designs": detail["designs"],
        "leading option": detail["leading option"].map(lambda o: _dash(OPTION_SHORT.get(o, o)) if o else ""),
        "share": [ctx.pct(x) if n > 0 else "" for x, n in zip(detail["share"], detail["designs"])],
    })
    return t1, t2


def tab_fixed_by_architecture_v2(ctx):
    """II1 appendix: for each dimension of q6_selected_fields, on the designs that answer it and have an architecture, the bias-corrected
    Cramér's V of dimension x architecture, its permutation p (1 000 shuffles of the architecture column, seed ctx.SEED), and in how many
    of the architectures with 10 or more answering designs the leading option holds 80 % or more (viz.thesis_q6.fixed_by_architecture)."""
    return _fixed_tables(ctx)[0], None


def tab_fixed_by_architecture_detail_v2(ctx):
    """II1 appendix: the per-architecture reading behind q6_fixed_by_architecture: designs answering, leading option and its share,
    one row per dimension x architecture (all 12 architectures; an empty share = no answering design)."""
    return _fixed_tables(ctx)[1], None


def fig_propulsor_units_per_architecture_v2(ctx):
    """II1 auxiliary: the original strip design (a dot per design, a bar over the middle half, a ring at the median).
    x labels: architecture code and the designs drawn; architectures with no propulsor record are left out and
    named once under the axis."""
    d = q6._data(ctx)
    codes, units, empty = [], [], []
    for c, u, n_all in zip(d["codes"], d["units_by_class"], d["total"]):
        u = np.asarray(u, dtype=float)
        if np.isfinite(u).any():
            codes.append(c), units.append(u)
        else:
            empty.append((c, int(n_all)))
    n_drawn = [int(np.isfinite(u).sum()) for u in units]
    fig, ax = plt.subplots(figsize=(ctx.W, getattr(ctx, 'fig_h', 3.4)), constrained_layout=True)
    plots.unit_strips(ax, codes, units, cap=30, seed=ctx.SEED)
    ax.set_xticks(range(len(codes)), [f"{arch(c).short}\n{n}" for c, n in zip(codes, n_drawn)])
    ax.set_xlim(-0.6, len(codes) - 0.4)
    ax.set_ylabel("propulsor units per design\n(capped at 30)")
    note = "; ".join(f"{arch(c).short} ({n} designs)" for c, n in empty)
    ax.set_xlabel("architecture, with its designs that have a propulsor record" + (f"\nno propulsor record: {note}" if empty else ""))
    fig.legend(handles=[Line2D([], [], marker="o", markersize=3.5, color=GREY, linestyle="none", label="one design"),
                        Line2D([], [], color=style.INK, linewidth=2.6, solid_capstyle="butt", label="middle half of the designs"),
                        Line2D([], [], marker="o", markersize=6, markerfacecolor="white", markeredgecolor=style.INK,
                               markeredgewidth=1.5, linestyle="none", label="median")],
               loc="outside lower center", ncol=3, fontsize=FS, title=code_key_lines(fig, codes + [c for c, _ in empty]), title_fontsize=7.0)
    data = pd.concat([pd.DataFrame({"architecture": arch(c).short, "propulsor units": u}) for c, u in zip(codes, units)], ignore_index=True)
    return fig, data


def _feature_heat(ax, mat: pd.DataFrame):
    """plots.feature_heat with 8 pt cell text (same one-hue scale, same hatched cell where an architecture has no record)."""
    m = mat.to_numpy(dtype=float)
    ax.imshow(np.ma.masked_invalid(m), cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for (r, c), val in np.ndenumerate(m):
        if np.isnan(val):
            ax.add_patch(mpl.patches.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor="#ececec", hatch="////", edgecolor="white", linewidth=0))
            continue
        ax.text(c, r, f"{100 * val:.0f}%", ha="center", va="center", color="white" if val > 0.55 else style.INK, fontsize=FS)
    ax.set_yticks(range(m.shape[0]), list(mat.index))
    ax.set_xticks(np.arange(-0.5, m.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, m.shape[0]), minor=True)
    ax.grid(False, which="major")                 # the thesis style's y grid would cross the cell numbers
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(length=0, which="both")
    for sp in ax.spines.values():
        sp.set_visible(False)


def fig_arrangement_by_architecture_v2(ctx):
    """II1 appendix: share of each architecture's designs with each arrangement feature; relabelled only."""
    d = q6._data(ctx)
    rows = {"at least one tilting propulsor": "≥ 1 tilting", "both fixed and tilting propulsors": "fixed and tilting",
            "a ducted propulsor": "≥ 1 ducted", "more than 8 propulsors": "more than 8"}
    fig, ax = plt.subplots(figsize=(ctx.W, 2.3), constrained_layout=True)
    _feature_heat(ax, d["feat"].rename(index=rows))
    ax.set_xticks(range(len(d["codes"])), [f"{arch(c).short}\n" + (f"{n}" if r == n else f"{r}/{n}")
                                           for c, r, n in zip(d["codes"], d["read"], d["total"])])
    ax.set_xlabel("architecture, with its designs\n(where fewer have a propulsor record: designs with a record / all designs)")
    data = d["feat"].round(3).reset_index().rename(columns={"index": "feature", "topType": "feature"})
    data.columns = [arch(c).short if c in style.CLASSES else c for c in data.columns]
    return fig, data


def _duct_bands(ax, dc: pd.DataFrame, cd: pd.DataFrame, band_col: str = "propulsive units"):
    """plots.duct_bands redrawn at 8 pt, without the white boxes behind the diamond labels, 'aircraft' -> 'design'."""
    dc, cd = dc.set_index(band_col), cd.set_index(band_col)
    order = [g for g in dc.index if g != "all bands"] + ["all bands"]
    f = lambda t, c: pd.to_numeric(t.loc[order, c], errors="coerce").to_numpy(dtype=float)       # noqa: E731
    n, any_n, any_s, unit_s = f(dc, "aircraft"), f(dc, "with any ducted unit"), f(dc, "share with any"), f(dc, "share of units ducted")
    every_s, med, cond_every = f(dc, "share ducting every unit"), f(dc, "median ducted units (ducted aircraft)"), f(cd, "share that duct every unit")
    half = (f(cd, "half to three quarters") + f(cd, "three quarters, not all")) / n
    under = (f(cd, "under a quarter") + f(cd, "a quarter to half")) / n
    x = np.arange(len(order), dtype=float)
    x[-1] += 0.55
    w = 0.5
    parts = [("ducts every propulsor", every_s, plots.DUCT_GREYS[0], ""), ("half or more, not all", half, plots.DUCT_GREYS[1], "...."),
             ("under half", under, plots.DUCT_GREYS[2], "")]
    bottom = np.zeros(len(x))
    for lab, h, colour, hatch in parts:
        ax.bar(x, h, w, bottom=bottom, color=colour, hatch=hatch, edgecolor="white", linewidth=0.6, zorder=3, label=lab)
        bottom = bottom + h
    for xi, e_, c_ in zip(x, every_s, cond_every):
        ax.text(xi, e_ / 2, f"{100 * c_:.0f}%", ha="center", va="center", color="white", fontsize=FS, zorder=6)
    for xi, s_ in zip(x, any_s):
        ax.text(xi, s_ + 0.018, f"{100 * s_:.0f}%", ha="center", va="bottom", fontweight="bold", fontsize=FS, zorder=6)
    ax.plot(x + w / 2, unit_s, linestyle="none", marker="D", markersize=5.2, markerfacecolor="white", markeredgecolor=style.INK,
            markeredgewidth=1.2, zorder=7, label="share of the band's propulsor units in a duct")
    for xi, u_ in zip(x, unit_s):
        ax.text(xi + w / 2 + 0.09, u_, f"{100 * u_:.0f}%", ha="left", va="center", fontsize=FS, color=style.INK, zorder=7)
    ax.set_xticks(x, [f"{_dash(g)}\n{int(a)} designs\n{int(b)} duct\nmedian {m:g}" for g, a, b, m in zip(order, n, any_n, med)])
    ax.set_xlim(-0.6, x[-1] + 0.95)
    ax.set_ylim(0, 0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.axvline((x[-2] + x[-1]) / 2, color=style.GRID, linewidth=0.8, linestyle=":")
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def fig_ducting_by_units_v2(ctx):
    """II1 appendix: ducting per propulsor-unit band; relabelled only (designs, 8 pt, legend below the plot)."""
    d = q6._data(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.6), constrained_layout=True)
    _duct_bands(ax, d["dcount"], d["dcond"])
    ax.set_ylabel("share of the band's designs")
    ax.set_xlabel("propulsor units per design (band); under each band: its designs, the designs with a duct,\nand the median number of ducted propulsors among those")
    h, l = ax.get_legend_handles_labels()
    h, l = h[1:] + h[:1], l[1:] + l[:1]
    fig.legend(h, l, loc="outside lower center", ncol=2, fontsize=FS)
    return fig, d["dcount"].merge(d["dcond"], on="propulsive units")


# ================================================================================== II2. levels of description
def _largest_configuration(s: str) -> str:
    first, *rest = s.split(" · ")
    return " · ".join([_STYLE_NAME_TO_SHORT.get(first, first)] + [_dash(r) for r in rest])


def tab_levels_of_description_v2(ctx):
    """II2 main: Table 7 reduced to the three levels A, A·W·T, A·U (the F row moves to III.3)."""
    b = q7._data(ctx)["brief7"]
    b = b[b["level id"].isin(["A0", "A1t", "A0c"])].set_index("level id").loc[["A0", "A1t", "A0c"]]
    t = pd.DataFrame({"level": [LEVEL[i] for i in b.index], "configurations": b["archetypes"].astype(int).to_numpy(),
                      "singletons": b["aircraft alone in their archetype"].astype(int).to_numpy(),
                      "¹D": b["effective number ¹D"].map(lambda x: f"{x:.1f}").to_numpy(),
                      "largest configuration": b["largest archetype"].map(_largest_configuration).to_numpy(),
                      "its share": b["its share"].map(ctx.pct).to_numpy()})
    return t, None


# ================================================================================== II3. distribution and new variety
#: the hollow marker of q6_configuration_core: the configuration's largest assignee holds MORE than this share of its designs (author's line, 2026-10-15)
SOLO_ASSIGNEE = 0.40


def largest_assignee(v: pd.DataFrame, keys) -> pd.DataFrame:
    """Per A·U configuration: its largest assignee, the designs it holds and its share of the configuration's designs. Read on ALL the
    configuration's designs (all years), the designs the figure's y (distinct assignees per design, frames.zones) is counted on; an
    individual inventor is one assignee per patent (``filer_id``), as in frames.zones. Ties: the first in the data's order."""
    rows = []
    for a in keys:
        sub = v[v["archetype"] == a]
        held = sub.groupby("filer_id").size().sort_values(ascending=False, kind="stable")
        top = str(held.index[0])
        rows.append({"archetype": a, "largest assignee": "one patent's inventor" if top.startswith("patent:") else top,
                     "its designs": int(held.iloc[0]), "its share": round(float(held.iloc[0] / len(sub)), 3)})
    return pd.DataFrame(rows).set_index("archetype")


def fig_configuration_core_v2(ctx):
    """II3 main (Fig 4.6, thesis style 2026-10-20): the A·U configurations of five designs or more by share of the 2016–23 designs and
    distinct assignees per design. The core configurations (thesis_q6: taken by share until half of the 2016–23 designs) coloured by
    architecture and labelled; every other configuration a small grey dot; a thin dashed line at the share threshold between core and
    rim, "rim" / "core (…)" at the top; a ring round the configuration whose largest assignee holds more than 40 % (``SOLO_ASSIGNEE``),
    with an 8 pt note on a short leader. No hulls. Data and CSV as before (the three largest non-core configurations are no longer named)."""
    d = q6._data(ctx)
    zz, core, rim = d["zz"], d["core"], d["rim"]
    lab = core
    big = largest_assignee(ctx.v, zz["archetype"])
    solo = zz["archetype"].map(big["its share"]).gt(SOLO_ASSIGNEE)
    X, Y = "share 2016-23", "filers per aircraft"
    s_core, s_grey = 30.0, 9.0
    r_pt = float(np.sqrt(s_core / np.pi))
    with ts_rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, TS_H["q6_configuration_core"]), layout="constrained")
        grey = zz[~zz.index.isin(lab.index)]
        ax.scatter(grey[X], grey[Y], s=s_grey, color=ts.NEUTRAL, edgecolor="none", zorder=3)
        cols = [ts.ARCH.get(arch(c).short, ts.ARCH["Other"]) for c in lab["code"]]
        ax.scatter(lab[X], lab[Y], s=s_core, color=cols, edgecolor="white", linewidth=0.4, zorder=4)
        thr = (lab[X].min() + grey[X].max()) / 2                     # between the smallest core share and the largest other share
        xmax = zz[X].max() * 1.08
        ax.set_xlim(0, xmax)
        ax.set_ylim(0.34, 1.13)
        ax.set_yticks([0.4, 0.6, 0.8, 1.0])
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
        ax.xaxis.set_major_locator(mticker.MultipleLocator(0.02))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{100 * v:.0f}"))
        ax.grid(axis="y", color="#e6e6e6", linewidth=0.5)
        ax.set_axisbelow(True)
        ax.axvline(thr, color=NOTE, linewidth=0.7, linestyle=(0, (3, 2)), zorder=2)
        ax.set_xlabel("share of the 2016–23 designs (%)")
        ax.set_ylabel("distinct assignees\nper design")
        ytop = 1.105
        t_rim = ax.text(thr - 0.0012, ytop, "rim", ha="right", va="center", fontsize=8.4, color=NOTE)
        t_core = ax.text(thr + 0.0012, ytop, f"core ({len(core)} configurations, half of the designs)", ha="left", va="center", fontsize=8.4, color=NOTE)
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        avoid = [t.get_window_extent(rend).expanded(1.02, 1.3) for t in (t_rim, t_core)]
        sel = zz.index[solo.to_numpy()]
        for i in sel:                                                 # the ring (drawn first, so the labels keep clear of it)
            ax.scatter(zz.loc[i, X], zz.loc[i, Y], s=s_core * 4.2, facecolor="none", edgecolor="#1a1a1a", linewidth=0.7, zorder=5)
        ring_r = r_pt * np.sqrt(4.2)
        ring_xy = ax.transData.transform(zz.loc[sel, [X, Y]].to_numpy(dtype=float)) if len(sel) else np.zeros((0, 2))
        k = fig.dpi / 72
        avoid += [Bbox([[x - ring_r * k, y - ring_r * k], [x + ring_r * k, y + ring_r * k]]) for x, y in ring_xy]
        tx_ = ax.transData.transform([[thr, 0.34], [thr, 1.13]])
        thr_box = Bbox([[tx_[0][0] - 2, tx_[0][1]], [tx_[1][0] + 2, tx_[1][1]]])        # the threshold line: no label crosses it
        avoid.append(thr_box)
        names = [cfg_label(a) for a in lab["archetype"]]
        failed = _place_point_labels(ax, lab[[X, Y]].to_numpy(dtype=float), names, r_pt, avoid, zz[[X, Y]].to_numpy(dtype=float),
                                     fs=8.4, max_r_pt=40.0)
        assert not failed, failed
        colour_of = dict(zip(names, cols))
        for t in ax.texts:
            if t.get_text() in colour_of:
                t.set_color(colour_of[t.get_text()])
                if t.arrow_patch is not None:
                    t.arrow_patch.set_color(colour_of[t.get_text()])
        # the note of the ringed point: 8 pt dark grey, on a short leader, at the first free spot
        fig.canvas.draw()
        boxes = [Text.get_window_extent(t, rend).expanded(1.05, 1.15) for t in ax.texts]
        A = ax.transData.transform(zz[[X, Y]].to_numpy(dtype=float))
        marks = [Bbox([[x - 3 * k, y - 3 * k], [x + 3 * k, y + 3 * k]]) for x, y in A]
        axbb = ax.get_window_extent(rend)
        note = "largest assignee > 40 %"
        for i, (px, py) in zip(sel, ring_xy):
            placed = False
            for dx, dy in [(14, -24), (24, -24), (34, -22), (44, -18), (24, 18), (-14, -24), (-24, -24), (-34, -22), (-24, 18)]:
                t = ax.annotate(note, (zz.loc[i, X], zz.loc[i, Y]), xytext=(dx, dy), textcoords="offset points", fontsize=8, color=NOTE,
                                ha="left" if dx > 0 else "right", va="center", zorder=6,
                                arrowprops=dict(arrowstyle="-", color=NOTE, linewidth=0.5, shrinkA=0, shrinkB=ring_r + 0.5))
                fig.canvas.draw()
                bb = Text.get_window_extent(t, rend)                 # the text alone (an annotation's extent includes its leader)
                inside = axbb.x0 <= bb.x0 and bb.x1 <= axbb.x1 and axbb.y0 <= bb.y0 and bb.y1 <= axbb.y1
                end = np.array([bb.x0 if dx > 0 else bb.x1, (bb.y0 + bb.y1) / 2])
                seg = np.array([px, py]) + (end - np.array([px, py])) * np.linspace(0.25, 1, 30)[:, None]
                hit_line = any(b.contains(*q) for q in seg for b in boxes + [thr_box])
                if inside and not hit_line and not any(bb.overlaps(b) for b in boxes + marks + avoid + [thr_box]):
                    placed = True
                    boxes.append(bb)
                    break
                t.remove()
            assert placed, "no place for the note of the ringed configuration"
    cols_ = ["archetype", "class", "aircraft", "filers", "filers per aircraft", "share 2016-23", "zone"]
    data = zz[cols_].reset_index(drop=True).rename(columns={"archetype": "configuration", "class": "architecture", "aircraft": "designs",
                                                            "filers": "assignees", "filers per aircraft": "assignees per design",
                                                            "zone": "first seen"})
    data["configuration"] = data["configuration"].map(cfg_label)
    data["architecture"] = zz["code"].map(lambda c: arch(c).name).to_numpy()
    data["group"] = ["core" if i in core.index else "rim" if i in rim.index else "" for i in zz.index]
    data["labelled"] = [i in lab.index for i in zz.index]
    bb_ = big.loc[zz["archetype"]]
    data["largest assignee"] = bb_["largest assignee"].to_numpy()
    data["its designs"] = bb_["its designs"].to_numpy()
    data["its share"] = bb_["its share"].to_numpy()
    data["largest assignee above 40 %"] = solo.to_numpy()
    data["core / rim threshold (share 2016-23, drawn)"] = round(float(thr), 4)
    return fig, data


def _year_start(g: pd.DataFrame, year: int) -> int:
    return int(g.loc[g["priority year reached"] == year, "aircraft"].min())


def curve_to_2026(ctx) -> pd.DataFrame:
    """The discovery curve to 2026 WITHOUT touching any complete-year value: the rows up to the last complete year are thesis_q6's own
    curve; the 2024–26 rows continue it, step by step, from the same functions run over all designs with a priority year
    (frames.discovery_inputs without the complete-year cut), shifted so that the curve is continuous at the join. Cached on ctx."""
    if getattr(ctx, "_v2p2_curve", None) is None:
        orig = q6._data(ctx)["curve"]
        inputs = frames.discovery_inputs(ctx.v, q6.SETS3, 2100)
        full = diversity.discovery_curve_levels(inputs, orders=ctx.cfg.analysis["discovery_orders"], seed=ctx.SEED)
        parts = []
        for lvl, g0 in orig.groupby("level", sort=False):
            g1 = full[full["level"] == lvl].reset_index(drop=True)
            n = len(g0)
            ext = g1.iloc[n:].copy()
            for col in ("archetypes (date order)", "archetypes (random order)"):
                ext[col] = (ext[col] - g1[col].iloc[n - 1] + g0[col].iloc[-1]).round(2)
            ext["2.5 %"] = ext["97.5 %"] = np.nan
            parts += [g0[["level", "aircraft", "priority year reached", "archetypes (date order)", "archetypes (random order)", "2.5 %", "97.5 %"]], ext]
        ctx._v2p2_curve = pd.concat(parts, ignore_index=True)
    return ctx._v2p2_curve


#: the last-100-designs band of q6_discovery_curve: light grey (rerun of 2026-10-15; was light blue)
TAIL_BAND = "#e3e3e3"


def fig_discovery_curve_v2(ctx):
    """II3 main (Fig 4.8, thesis style 2026-10-20): configurations seen as the designs accumulate in priority order, to 2026, panels
    (a) A, (b) A·W·T, (c) A·U: real order solid black, random-order expectation dashed grey, the 2024–26* part thin dotted and faded;
    the last 100 designs to 2023 marked by a thin bracket (no shaded zone); the first design of 2016 and of 2020 as short ticks at the
    foot. (d): the new configurations among the last 100 designs to 2023 as a dot plot, real (filled) against random (hollow), one row per
    level, values printed. Every number as before."""
    d = q6._data(ctx)
    full, est, tail = curve_to_2026(ctx), d["est"], ctx.cfg.analysis["discovery_tail"]
    n_done = d["curve"].groupby("level")["aircraft"].max()
    levels = [(k, LEVEL[k]) for k in ("A0", "A1t", "A0c")]
    RND = "#7a7a7a"
    starts = {}
    with ts_rc():
        fig, axs4 = plt.subplots(1, 4, figsize=(ts.TEXTWIDTH, TS_H["q6_discovery_curve"]), layout="constrained",
                                 gridspec_kw=dict(width_ratios=[1, 1, 1, 1.12]))
        axs, axd = axs4[:3], axs4[3]
        for j, (ax, (lvl, nm)) in enumerate(zip(axs, levels)):
            g = full[full["level"] == lvl]
            x = g["aircraft"].to_numpy()
            real, rnd = g["archetypes (date order)"].to_numpy(), g["archetypes (random order)"].to_numpy()
            n_c, n_max = int(n_done[lvl]), int(x.max())
            done, inc = x <= n_c, x > n_c                             # 2024-26*: from the first 2024 design, never joined to 2023
            ax.plot(x[done], rnd[done], color=RND, linewidth=1.0, linestyle=(0, (3.5, 2)), zorder=2)
            ax.plot(x[done], real[done], color="#000000", linewidth=1.3, solid_capstyle="butt", zorder=4)
            gap_ls = (1.0, (1, 2.2))                                  # the dotted part opens with a gap: visibly apart from the solid curve
            ax.plot(x[inc], rnd[inc], color=RND, linewidth=0.8, linestyle=gap_ls, dash_capstyle="butt", alpha=ts.INCOMPLETE_ALPHA, zorder=2)
            ax.plot(x[inc], real[inc], color="#000000", linewidth=0.8, linestyle=gap_ls, dash_capstyle="butt", alpha=ts.INCOMPLETE_ALPHA, zorder=4)
            hi = max(real.max(), rnd.max())
            top = hi * 1.32
            ax.set_xlim(0, n_max + 5)
            ax.set_ylim(0, top)
            ax.xaxis.set_major_locator(mticker.MultipleLocator(300))
            ax.yaxis.set_major_locator(mticker.MaxNLocator(4, integer=True))
            yb = hi * 1.12                                            # the last-100 bracket, above the curves
            ax.plot([n_c - tail, n_c - tail, n_c, n_c], [yb - hi * 0.05, yb, yb, yb - hi * 0.05], color=NOTE, linewidth=0.7, zorder=5)
            ax.text(n_c - tail / 2, yb + hi * 0.02, f"last {tail}", ha="center", va="bottom", fontsize=8, color=NOTE)
            for yr in (2016, 2020):
                xs = _year_start(g, yr)
                starts[(nm, yr)] = xs
                ax.plot([xs, xs], [0, hi * 0.06], color=NOTE, linewidth=0.7, zorder=5)
                ax.text(xs, hi * 0.08, str(yr), ha="center", va="bottom", fontsize=8, color=NOTE)
            ax.set_title(f"({'abc'[j]}) {nm}", loc="left")
            if j == 1:                                                # the two curves named once, in (b)
                xi = int(np.searchsorted(x, n_c * 0.8))
                ax.text(x[xi], rnd[xi] + hi * 0.08, "random order", ha="right", va="bottom", fontsize=8.4, color=RND)
                xi = int(np.searchsorted(x, n_c * 0.72))
                ax.text(x[xi], real[xi] - hi * 0.08, "real order", ha="center", va="top", fontsize=8.4, color="#000000")
        axs[0].set_ylabel("distinct\nconfigurations seen")
        axs[1].set_xlabel("designs, in priority order (dotted: 2024–26*, incomplete)")
        # (d) the last-100 numbers as a dot plot
        obs = [float(est.loc[lvl, "new in the last 100 aircraft"]) for lvl, _ in levels]
        rnd_ = [float(est.loc[lvl, "new in the last 100, random order"]) for lvl, _ in levels]
        yy = np.arange(len(levels))[::-1]
        xm = max(obs + rnd_)
        for y, o, r in zip(yy, obs, rnd_):
            axd.plot([min(o, r), max(o, r)], [y, y], color="#cfcfcf", linewidth=1.2, zorder=2)
            axd.plot(r, y, "o", ms=5, mfc="white", mec=RND, mew=1.0, ls="none", zorder=3)
            axd.plot(o, y, "o", ms=5, color="#000000", ls="none", zorder=4)
            if abs(o - r) < 0.05:
                axd.text(max(o, r) + xm * 0.11, y, f"{o:.1f} (both)", ha="left", va="center", fontsize=8.4)
            else:
                lo_, hi_ = (r, o) if r < o else (o, r)
                axd.text(hi_ + xm * 0.07, y, f"{hi_:.1f}", ha="left", va="center", fontsize=8.4, color="#000000" if hi_ == o else RND)
                axd.text(lo_ - xm * 0.07, y, f"{lo_:.1f}", ha="right", va="center", fontsize=8.4, color="#000000" if lo_ == o else RND)
        key = next((i for i, (o, r) in enumerate(zip(obs, rnd_)) if abs(o - r) >= 0.5), 1)       # the words on the widest-apart row
        axd.text(obs[key], yy[key] + 0.3, "real", ha="center", va="bottom", fontsize=8.4, color="#000000")
        axd.text(rnd_[key], yy[key] + 0.3, "random", ha="center", va="bottom", fontsize=8.4, color=RND)
        axd.set_yticks(yy, [nm for _, nm in levels])
        axd.set_ylim(-0.6, len(levels) - 0.3)
        axd.set_xlim(-xm * 0.32, xm * 1.35)
        axd.xaxis.set_major_locator(mticker.MultipleLocator(2))
        axd.spines["left"].set_visible(False)
        axd.tick_params(axis="y", length=0)
        axd.set_xlabel("new configurations")
        axd.set_title(f"(d) last {tail} designs to 2023", loc="left", x=-0.42)
    data = full[["level", "aircraft", "priority year reached", "archetypes (date order)", "archetypes (random order)"]].rename(
        columns={"aircraft": "designs", "archetypes (date order)": "configurations (real order)", "archetypes (random order)": "configurations (random order)"})
    data["level"] = data["level"].map(LEVEL)
    data["complete years"] = [bool(a <= n_done[l]) for l, a in zip(full["level"], full["aircraft"])]
    data["first design of 2016 or 2020"] = [bool(a in (starts[(LEVEL[l], 2016)], starts[(LEVEL[l], 2020)])) for l, a in zip(full["level"], full["aircraft"])]
    data[f"new in the last {tail} designs to 2023, real order"] = [obs[[k for k, _ in levels].index(l)] for l in full["level"]]
    data[f"new in the last {tail} designs to 2023, random order"] = [rnd_[[k for k, _ in levels].index(l)] for l in full["level"]]
    return fig, data


#: q6_half_of_cohort: cohort -> (colour, line style, marker, line width). Five line styles and five marker shapes; the colours step in
#: lightness (about 16, 38, 54, 69 and 84 % grey) so greyscale keeps them apart; 2024–26 (incomplete) lightest and thinnest, hollow marker.
COHORT_LOOK = {"<= 2011": ("#b0b0b0", (0, (1, 1.2)), "^", 1.3), "2012-15": ("#8a8a8a", (0, (5, 1.5, 1, 1.5)), "D", 1.3),
               "2016-19": ("#08306b", "-", "o", 1.6), "2020-23": ("#c2410c", (0, (5, 2)), "s", 1.6),
               "2024-26 (partial)": ("#c6dbef", (0, (2.5, 1.5)), "v", 0.9)}


def fig_half_of_cohort_v2(ctx):
    """II3 auxiliary (Fig 4.7, thesis style 2026-10-20): one curve per cohort, the cumulative share of the cohort's designs held by its k
    largest A·U configurations (ranked within the cohort, among the configurations of five designs or more: ``frames.zones``); cohorts in
    ts.GREYS (≤2011 lightest, 2020–23 black), 2024–26* hollow, faded and dotted; a dashed 50 % line; the crossing of each cohort a larger
    marker; direct labels at the right end ("2016–19: half in 9"), no legend. The frame keeps all 20 ranks; 12 are drawn."""
    d = q6._data(ctx)
    z = d["zones"]
    K, K_DRAW = 20, 12
    ranks = np.arange(1, K + 1)
    look = {"<= 2011": ts.GREYS[0], "2012-15": ts.GREYS[1], "2016-19": ts.GREYS[2], "2020-23": ts.GREYS[4], "2024-26 (partial)": ts.GREYS[3]}
    name = dict(zip(ctx.WIN_NAMES, ts.COHORTS))
    rows, ends = [], []
    with ts_rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, TS_H["q6_half_of_cohort"]), layout="constrained")
        room = 3.6                                                    # x units right of rank 12 for the end labels
        ax.plot([0.5, K_DRAW + 0.5], [0.5, 0.5], color="#1a1a1a", linewidth=0.8, linestyle=(0, (4, 3)), zorder=1)
        ax.text(0.6, 0.515, "50 %", ha="left", va="bottom", fontsize=8.4, color=NOTE)
        for w in ctx.WIN_NAMES:
            c = np.sort(z[w].astype(float).to_numpy())[::-1]
            cs = np.cumsum(c) / c.sum()
            k = int(np.searchsorted(cs, 0.5)) + 1
            col, part = look[w], "partial" in w
            al = ts.INCOMPLETE_ALPHA if part else 1.0
            ax.plot(ranks[:K_DRAW], cs[:K_DRAW], color=col, linewidth=0.9 if part else 1.2, linestyle=(0, (1, 1.5)) if part else "-",
                    alpha=al, zorder=4 if w == "2020-23" else 3)
            ax.plot(ranks[:K_DRAW], cs[:K_DRAW], "o", ms=3.0, mfc="white" if part else col, mec=col, mew=0.8, alpha=al, ls="none",
                    zorder=4 if w == "2020-23" else 3)
            ax.plot(k, cs[k - 1], "o", ms=6.5, mfc="white" if part else col, mec=col, mew=1.2, alpha=al, ls="none", zorder=5)
            ends.append((cs[K_DRAW - 1], f"{name[w]}: half in {k}", col, al))
            rows += [{"cohort": "2024-26 (incomplete)" if part else plots.WINDOW_TICKS[w], "rank": int(r), "designs in the configuration": int(c[r - 1]),
                      "cumulative share": round(float(cs[r - 1]), 4), "crosses 50 % here": bool(r == k)} for r in ranks]
        ax.set_xlim(0.5, K_DRAW + 0.5 + room)
        ax.set_ylim(0, 1.0)
        ax.spines["bottom"].set_bounds(0.5, K_DRAW + 0.5)
        ax.set_xticks(list(range(1, K_DRAW + 1)))
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{100 * v:.0f}"))
        ax.set_xlabel("A·U configurations, ranked by size within the cohort")
        ax.set_ylabel("cumulative share of\nthe cohort's designs (%)")
        gap = ts_pt_to_data(ax, 10.5)
        ys = ts_spread([e[0] for e in ends], gap, hi=1.0 - gap / 2)
        x_lab = K_DRAW + 0.5 + 0.55
        for (y0, txt, col, al), y in zip(ends, ys):
            ax.text(x_lab + 0.15, y, txt, ha="left", va="center", fontsize=8.4, color="#1a1a1a" if col in (ts.GREYS[3], ts.GREYS[4]) else NOTE)
            ax.plot([K_DRAW + 0.15, x_lab], [y0, y], color=col, linewidth=0.5, alpha=max(al, 0.8), zorder=2)
        ax.xaxis.label.set_x((K_DRAW / 2) / (K_DRAW + room))
    return fig, pd.DataFrame(rows)


def fig_half_of_cohort_heatmap_v2(ctx):
    """II3 auxiliary: designs per A·U configuration (columns, largest first over all cohorts) and cohort (rows); the outlined cells (black on white since 2026-10-15; orange before) of each of the two
    complete cohorts sits after the k configurations that hold half of its designs, k read on the ranking WITHIN the cohort (as q6_half_of_cohort),
    so k reads 5, 5, 9 and 7. 2024-26 is drawn faded (incomplete)."""
    d = q6._data(ctx)
    z = d["zones"]
    cohorts = list(ctx.WIN_NAMES)
    lab = {w: ("2024-26 (incomplete)" if "partial" in w else plots.WINDOW_TICKS[w]) for w in cohorts}
    mat = z.set_index("archetype")[cohorts].astype(float).T
    mat.columns = [cfg_label(a) for a in mat.columns]
    k = {w: int(np.searchsorted(np.cumsum(np.sort(z[w].astype(float).to_numpy())[::-1]) / z[w].astype(float).sum(), 0.5)) + 1 for w in cohorts}
    m2 = mat.rename(index=lab)
    fig, ax = plt.subplots(figsize=(ctx.W, getattr(ctx, "fig_h", 3.0)), constrained_layout=True)
    plots.window_heat(ax, m2, {})
    top = {}                                                  # each complete cohort's own top-k cells (ranking within the cohort, columns in overall order)
    for i, w in enumerate(cohorts):
        if "partial" in w:
            continue
        c = z[w].astype(float).to_numpy()
        cols = np.argsort(-c, kind="stable")[:k[w]]
        top[w] = sorted(int(j) for j in cols)
        for j in cols:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="white", linewidth=3.4, zorder=6))     # black on white:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=style.INK, linewidth=1.6, zorder=7))   # reads on dark and light cells, in greyscale too
    ax.add_patch(plt.Rectangle((-0.5, len(cohorts) - 1.5), m2.shape[1], 1, facecolor="white", alpha=0.55, linewidth=0, zorder=5))
    ax.tick_params(axis="x", labelsize=FS)
    ax.tick_params(axis="y", labelsize=FS)
    ax.set_xlabel("A·U configuration, largest first over all cohorts", fontsize=FS)
    ax.set_ylabel("cohort", fontsize=FS)
    shown = [c for c in style.CLASS_ORDER if c in set(z["code"])]
    fig.legend(handles=[Patch(facecolor="none", edgecolor=style.INK, linewidth=1.6,
                              label="the cohort's own largest configurations that together hold half of its designs (k = " + ", ".join(str(k[w]) for w in cohorts if "partial" not in w) + ")")],
               loc="outside lower center", ncol=1, fontsize=FS, title=code_key_lines(fig, shown), title_fontsize=7.0)
    data = (mat.rename(index=lab).rename_axis("cohort").reset_index().melt(id_vars="cohort", var_name="configuration", value_name="designs"))
    data["configurations that hold half (ranked within the cohort)"] = data["cohort"].map({lab[w]: k[w] for w in cohorts})
    cfgs = list(mat.columns)
    data["in the cohort's top k (outlined)"] = [bool(cfgs.index(cf) in top.get(w0, [])) for cf, w0 in zip(data["configuration"], data["cohort"].map({lab[w]: w for w in cohorts}))]
    return fig, data


# ================================================================================== items + writer
ITEMS = [
    dict(name="q6_selected_fields", group="II1_varying_attributes", role="main", kind="table", builder=tab_selected_fields_v2,
         title="Dimensions that tell designs apart", source_item="v2 of q6_selected_fields (Table 6)"),
    dict(name="q6_fixed_by_architecture", group="II1_varying_attributes", role="appendix", kind="table", builder=tab_fixed_by_architecture_v2,
         title="Which dimensions the architecture fixes", source_item="new (2026-10-15): Cramér's V and leading-option shares per architecture, on the rows of q6_selected_fields"),
    dict(name="q6_fixed_by_architecture_detail", group="II1_varying_attributes", role="appendix", kind="table", builder=tab_fixed_by_architecture_detail_v2,
         title="Leading option per dimension and architecture", source_item="new (2026-10-15): the per-architecture reading behind q6_fixed_by_architecture"),
    dict(name="q6_propulsor_units_per_class", group="II1_varying_attributes", role="auxiliary", kind="figure",
         builder=fig_propulsor_units_per_architecture_v2, title="Propulsor units per design, by architecture",
         source_item="v2 of q6_propulsor_units_per_class (Figure 6 (i))"),
    dict(name="q6_arrangement_by_class", group="II1_varying_attributes", role="appendix", kind="figure",
         builder=fig_arrangement_by_architecture_v2, title="Arrangement features per architecture",
         source_item="v2 of q6_arrangement_by_class"),
    dict(name="q6_ducting_by_units", group="II1_varying_attributes", role="appendix", kind="figure", builder=fig_ducting_by_units_v2,
         title="Ducting per propulsor-unit band", source_item="v2 of q6_ducting_by_units"),
    dict(name="q7_levels_of_description", group="II2_levels_of_description", role="main", kind="table", builder=tab_levels_of_description_v2,
         title="The three levels of description", source_item="v2 of q7_archetype_sets (Table 7), F row removed"),
    dict(name="q6_configuration_core", group="II3_distribution_and_new_variety", role="main", kind="figure", builder=fig_configuration_core_v2,
         title="Crowded core and empty rim", source_item="v2 of q6_archetype_core (Figure 8 (i))"),
    dict(name="q6_discovery_curve", group="II3_distribution_and_new_variety", role="main", kind="figure", builder=fig_discovery_curve_v2,
         title="Is the design space still opening", source_item="v2 of q6_discovery_curve (Figure 9)"),
    dict(name="q6_half_of_cohort_heatmap", group="II3_distribution_and_new_variety", role="auxiliary", kind="figure", builder=fig_half_of_cohort_heatmap_v2,
         title="Designs per configuration and cohort; where each cohort reaches half", source_item="replaces q6_archetype_windows (Figure 8 (ii))"),
    dict(name="q6_half_of_cohort", group="II3_distribution_and_new_variety", role="auxiliary", kind="figure", builder=fig_half_of_cohort_v2,
         title="Configurations that hold half of a cohort's designs", source_item="replaces q6_archetype_windows (Figure 8 (ii))"),
]


def out_root(cfg):
    """thesis_figures_v2/Part_II_design_space/, a sibling of Part_I_evidence_base/ and of thesis_figures/ (never written into)."""
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_II_design_space"


def save_v2_item(item: dict, cfg, ctx) -> None:
    """Same as before, built and saved under the author's thesis figure style (viz/part1.mplstyle, style 1), as Part I."""
    import matplotlib.pyplot as plt
    from pathlib import Path
    if item["name"] in TS_FIGS:              # restyled 2026-10-20: the thesis style (notebooks/thesis_style.py), no bbox crop
        with ts_rc():
            return _save_v2_item(item, cfg, ctx)
    with plt.style.context(str(Path(__file__).with_name("part1.mplstyle"))):
        return _save_v2_item(item, cfg, ctx)


def _save_v2_item(item: dict, cfg, ctx) -> None:
    """Build one item and write it to <out_root>/<group>/<role>/<name>.{pdf,png,csv,json}."""
    import json
    obj, data = item["builder"](ctx)
    if item.get("kind", "figure") == "figure" and hasattr(obj, "axes"):
        for a in obj.axes:                   # one grid per plot: a right-hand twin axis draws none
            if a.yaxis.get_label_position() == "right":
                a.grid(False)
    out = out_root(cfg) / item["group"] / item["role"]
    out.mkdir(parents=True, exist_ok=True)
    name = item["name"]
    meta = {k: item[k] for k in ("name", "group", "role", "kind", "title", "source_item")}
    if item["kind"] == "figure":
        for ext in cfg.style.get("formats", ["pdf", "png"]):
            obj.savefig(out / f"{name}.{ext}")
        if data is not None:
            data.to_csv(out / f"{name}.csv", index=False)
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
    else:
        obj.to_csv(out / f"{name}.csv", index=False)
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return obj, data
