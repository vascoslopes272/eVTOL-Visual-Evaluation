"""Part II (Design space) figures, v2: relabelled, simplified and regrouped versions of a subset of the Q6 / Q7
thesis figures (THESIS_CONTRACT.md). Every number and every underlying frame is read from viz/thesis_q6.py and
viz/thesis_q7.py unchanged; this module only re-draws, re-labels and re-groups them for
thesis_figures_v2/Part_II_design_space/ (see its README.md). The originals in thesis_figures/ are never touched.

Terminology (author's ruling, 2026-10-11), in every label, legend, axis and title:
    archetype -> configuration      aircraft (as a count) -> design      filer -> assignee
    window -> cohort                class -> architecture                Multirotor -> Multicopter
    Tilt Body TB -> Tilt Frame TF   Tilt Propulsor = TP                  Lift + Cruise code = SLC
    levels of description are written C, C·W·T, C·U.
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
from matplotlib.transforms import Bbox

from lib import diversity
from viz import frames, plots, style
from viz import thesis_q6 as q6
from viz import thesis_q7 as q7
from viz import thesis_v2_part1 as p1

FS = 8.0                      # the smallest text of any figure, pt at print size
TITLE_FS = 9.0
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
    """A C·U configuration key as the figures print it: 'SLC · 9+' -> 'SLC 9+', 'TB · 1-3' -> 'TF 1–3',
    'HB · n/a (no M3 card)' -> 'HB'. The suffix is the propulsor-unit band."""
    c, _, b = key.partition(" · ")
    b = _dash(b.replace("n/a (no M3 card)", ""))
    return f"{arch(c).short} {b}".strip()


def _dash(s: str) -> str:
    """En dash in number ranges; the lowest propulsor-unit band has ONE name everywhere: 0–3 (the data's own bin, frames.ROTOR_BINS)."""
    return re.sub(r"(?<=\d)-(?=\d)", "–", re.sub(r"\b1-3\b", "0-3", s))


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


def _label_size(ax, text, fs=FS):
    t = ax.text(0, 0, text, fontsize=fs)
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
    angles = np.deg2rad([0, 180, 30, 150, 330, 210, 90, 270, 60, 120, 300, 240])
    placed, fails = [], []
    for q in sorted(range(len(P)), key=lambda i: -near[i]):
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
                if any(_box_gap(bb, o) <= own + 3 * k for o in others):
                    continue
                placed.append(bb)
                ha = "left" if np.cos(th) > 0.3 else "right" if np.cos(th) < -0.3 else "center"
                va = "bottom" if np.sin(th) > 0.3 else "top" if np.sin(th) < -0.3 else "center"
                ax.annotate(labels[q], xy=tuple(xy[q]), xytext=(r * np.cos(th), r * np.sin(th)), textcoords="offset points", ha=ha,
                            va=va, fontsize=fs, color=style.INK, zorder=8,
                            arrowprops=dict(arrowstyle="-", linewidth=0.5, color=style.INK, shrinkA=0, shrinkB=r_pt) if r > r_pt + 4 else None)
                done = True
                break
            if done:
                break
        if not done:
            fails.append(labels[q])
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
}


def _short_options(s: str) -> str:
    out = []
    for item in s.split(" · "):
        name, cnt = item.rsplit(": ", 1)
        out.append(f"{_dash(OPTION_SHORT.get(name, name))}: {cnt}"
    return " · ".join(out)


def tab_selected_fields_v2(ctx):
    """II1 main: Table 6, the dimensions whose most common option holds under the cut-off. Columns renamed
    (designs answering, options, most common options); option names shortened; 'aircraft' -> 'design'."""
    df, _ = q6.tab_selected_fields(ctx)
    t = pd.DataFrame({
        "dimension": df["field"].str.replace("aircraft", "design", regex=False),
        "designs answering": df["aircraft answering"],
        "options": df["different answers"],
        "top share": df["top share"],
        "most common options": df["most common answers: aircraft"].map(_short_options),
    })
    return t, None


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
    fig, ax = plt.subplots(figsize=(ctx.W, 3.4), constrained_layout=True)
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
               loc="outside lower center", ncol=3, fontsize=FS)
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
    """II2 main: Table 7 reduced to the three levels C, C·W·T, C·U (the F row moves to III.3)."""
    b = q7._data(ctx)["brief7"]
    b = b[b["level id"].isin(["A0", "A1t", "A0c"])].set_index("level id").loc[["A0", "A1t", "A0c"]]
    t = pd.DataFrame({"level": [q6.NAMES3[i] for i in b.index], "configurations": b["archetypes"].astype(int).to_numpy(),
                      "single-design configurations": b["aircraft alone in their archetype"].astype(int).to_numpy(),
                      "¹D": b["effective number ¹D"].map(lambda x: f"{x:.1f}").to_numpy(),
                      "largest configuration": b["largest archetype"].map(_largest_configuration).to_numpy(),
                      "its share": b["its share"].map(ctx.pct).to_numpy()})
    return t, None


# ================================================================================== II3. distribution and new variety
def fig_configuration_core_v2(ctx):
    """II3 main: the C·U configurations of five designs or more by share of the 2016–23 designs and distinct assignees per
    design. Label only the 7 core configurations and the 3 non-core ones with the largest 2016–23 share; every other
    point grey and unlabelled; the core outlined solid, the rim dashed, each named once."""
    d = q6._data(ctx)
    zz, core, rim = d["zz"], d["core"], d["rim"]
    extra = zz[~zz.index.isin(core.index)].sort_values("share 2016-23", ascending=False).head(3)
    lab = pd.concat([core, extra])
    s_pt2 = 46.0
    r_pt = float(np.sqrt(s_pt2 / np.pi))

    fig, ax = plt.subplots(figsize=(ctx.W, 4.7), constrained_layout=True)
    ax.scatter(zz["share 2016-23"], zz["filers per aircraft"], s=s_pt2, color=GREY, edgecolor="white", linewidth=0.6, zorder=3)
    for _, r in lab.iterrows():
        ax.scatter(r["share 2016-23"], r["filers per aircraft"], s=s_pt2, color=arch(r["code"]).color, edgecolor="white", linewidth=0.6, zorder=4)
    ax.set_xlim(-0.002, zz["share 2016-23"].max() * 1.12)
    ax.set_ylim(0.4, 1.08)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.set_xlabel("share of the 2016–23 designs\n(label: architecture and propulsor units, e.g. SLC 5–6 = Lift + Cruise with 5–6 propulsor units)")
    ax.set_ylabel("distinct assignees per design")
    codes = [c for c in style.CLASS_ORDER if c in set(lab["code"])]
    fig.legend(handles=_arch_legend(codes), loc="outside lower center", ncol=len(codes), fontsize=FS, columnspacing=1.2, handletextpad=0.3)
    fig.canvas.draw()
    ring_core = plots.hull_ring(ax, core["share 2016-23"], core["filers per aircraft"], [r_pt] * len(core), pad_pt=4, linewidth=1.4)
    ring_rim = plots.hull_ring(ax, rim["share 2016-23"], rim["filers per aircraft"], [r_pt] * len(rim), pad_pt=4, linewidth=1.2,
                               linestyle=(0, (4, 2)), edgecolor=style.MUTED)
    obstacles = _ring_boxes(ring_core) + _ring_boxes(ring_rim)
    failed = _place_point_labels(ax, lab[["share 2016-23", "filers per aircraft"]].to_numpy(), [cfg_label(a) for a in lab["archetype"]], r_pt,
                                 obstacles, zz[["share 2016-23", "filers per aircraft"]].to_numpy())
    assert not failed, failed
    for t in ax.texts:                       # a point label never shows a ring line through it
        t.set_bbox(dict(fc="white", ec="none", pad=0.3, alpha=0.9))
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = [t.get_window_extent(rend).expanded(1.04, 1.12) for t in ax.texts]
    pts = [Bbox([[x - r_pt * fig.dpi / 72, y - r_pt * fig.dpi / 72], [x + r_pt * fig.dpi / 72, y + r_pt * fig.dpi / 72]])
           for x, y in ax.transData.transform(np.c_[zz["share 2016-23"], zz["filers per aircraft"]])]
    for name, ring, colour in (("core: largest configurations", ring_core, style.INK), ("rim: smallest configurations", ring_rim, style.MUTED)):
        size = _label_size(ax, name)
        target = [tuple(ring.mean(axis=0))] if name.startswith("core") else [tuple(p) for p in ring]      # the core's name sits inside it
        spot = _free_spot(ax, size, placed + pts + _ring_boxes(ring_core) + _ring_boxes(ring_rim), target)
        assert spot is not None, name
        x_d, y_d = ax.transData.inverted().transform(spot)
        ax.text(x_d, y_d, name, fontsize=FS, color=colour, ha="left", va="bottom", fontweight="bold" if name.startswith("core") else "normal")
        placed.append(Bbox([[spot[0], spot[1]], [spot[0] + size[0], spot[1] + size[1]]]))
    cols = ["archetype", "class", "aircraft", "filers", "filers per aircraft", "share 2016-23", "zone"]
    data = zz[cols].reset_index(drop=True).rename(columns={"archetype": "configuration", "class": "architecture", "aircraft": "designs",
                                                           "filers": "assignees", "filers per aircraft": "assignees per design",
                                                           "zone": "first seen"})
    data["configuration"] = data["configuration"].map(cfg_label)
    data["architecture"] = zz["code"].map(lambda c: arch(c).name).to_numpy()
    data["group"] = ["core" if i in core.index else "rim" if i in rim.index else "" for i in zz.index]
    data["labelled"] = [i in lab.index for i in zz.index]
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


def fig_discovery_curve_v2(ctx):
    """II3 main: configurations seen as the designs accumulate in priority order, to 2026, three small panels (C | C·W·T | C·U):
    the real curve, the random-order expectation as a thin dashed grey line, the 2024–26 designs shaded as not yet all published,
    and the last 100 designs of the complete years (to 2023) shaded; the last-100 numbers are those of the complete years."""
    d = q6._data(ctx)
    full, est, tail = curve_to_2026(ctx), d["est"], ctx.cfg.analysis["discovery_tail"]
    n_done = d["curve"].groupby("level")["aircraft"].max()
    levels = [("A0", "C"), ("A1t", "C·W·T"), ("A0c", "C·U")]
    fig, axs = plt.subplots(1, 3, figsize=(ctx.W, 3.5), constrained_layout=True)
    for ax, (lvl, name) in zip(axs, levels):
        g = full[full["level"] == lvl]
        x = g["aircraft"].to_numpy()
        real, rnd = g["archetypes (date order)"].to_numpy(), g["archetypes (random order)"].to_numpy()
        n_c, n_max = int(n_done[lvl]), int(x.max())
        ax.axvspan(n_c - tail, n_c, color=TAIL_FILL, zorder=0, linewidth=0)
        ax.axvspan(n_c, n_max, facecolor="white", edgecolor=GREY, hatch="////", linewidth=0, alpha=0.9, zorder=0)
        ax.plot(x, rnd, color="#8c8c8c", linewidth=0.8, linestyle=(0, (3, 2)), zorder=2)
        ax.plot(x, real, color=style.INK, linewidth=1.7, zorder=4)
        ax.set_xlim(0, n_max + 3)
        ax.set_ylim(0, max(real.max(), rnd.max()) * 1.1)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(200))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(5, integer=True))
        ax.grid(axis="y", color=style.GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        top = ax.secondary_xaxis("top")
        top.set_xticks([_year_start(g, 2016), _year_start(g, 2020)], ["2016", "2020"])
        top.tick_params(length=4, labelsize=FS)
        ax.set_title(name, loc="left", fontsize=TITLE_FS, fontweight="bold", pad=18)
        ax.set_xlabel(f"last {tail} to 2023: {est.loc[lvl, 'new in the last 100 aircraft']:.1f} new\n"
                      f"vs {est.loc[lvl, 'new in the last 100, random order']:.1f} by chance", fontsize=FS)
    axs[0].set_ylabel("distinct configurations seen")
    fig.supxlabel("designs, in priority order, to 2026 (top ticks: the first design of 2016 and of 2020)", fontsize=FS)
    fig.legend(handles=[Line2D([], [], color=style.INK, linewidth=1.7, label="real order (priority year)"),
                        Line2D([], [], color="#8c8c8c", linewidth=0.8, linestyle=(0, (3, 2)), label="same designs in random order"),
                        Patch(facecolor=TAIL_FILL, label=f"last {tail} designs to 2023"),
                        Patch(facecolor="white", edgecolor=GREY, hatch="////", label="2024–26: not yet all published")],
               loc="outside upper center", ncol=2, fontsize=FS)
    data = full[["level", "aircraft", "priority year reached", "archetypes (date order)", "archetypes (random order)"]].rename(
        columns={"aircraft": "designs", "archetypes (date order)": "configurations (real order)", "archetypes (random order)": "configurations (random order)"})
    data["level"] = data["level"].map(q6.NAMES3)
    data["complete years"] = [bool(a <= n_done[l]) for l, a in zip(full["level"], full["aircraft"])]
    return fig, data


def fig_half_of_cohort_v2(ctx):
    """II3 auxiliary: replaces the configuration × cohort heatmap. One line per cohort (2024–26 dashed and faded, incomplete): the cumulative share of the
    cohort's designs held by its k largest configurations (ranked by size within the cohort, among the C·U configurations
    of five designs or more), the 50 % line, and where each cohort crosses it."""
    d = q6._data(ctx)
    z = d["zones"]
    cohorts = ctx.WIN_NAMES                      # the four complete cohorts and 2024–26, which is incomplete
    style_of = {"<= 2011": ("#b0b0b0", (0, (4, 2)), "s"), "2012-15": ("#6b6b6b", (0, (1, 1.6)), "D"),
                "2016-19": ("#0072B2", "-", "o"), "2020-23": ("#D55E00", "-", "o"),
                "2024-26 (partial)": ("#8fb8d6", (0, (5, 2)), "o")}
    K = 20
    ranks = np.arange(1, K + 1)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.5), constrained_layout=True)
    ax.axhline(0.5, color=style.INK, linewidth=0.8, linestyle="--", zorder=1)
    rows, ends = [], []
    for w in cohorts:
        c = np.sort(z[w].astype(float).to_numpy())[::-1]
        cs = np.cumsum(c) / c.sum()
        k = int(np.searchsorted(cs, 0.5)) + 1
        col, ls, mk = style_of[w]
        part = "partial" in w
        ax.plot(ranks, cs[:K], color=col, linestyle=ls, linewidth=1.3 if part else 1.6, zorder=3)
        nudge = {"<= 2011": -0.18, "2012-15": 0.18}.get(w, 0.0)      # ≤2011 and 2012-15 both cross at 5: keep both visible
        ax.plot(k + nudge, cs[k - 1], marker=mk, markersize=8, markerfacecolor="white" if part else col, markeredgecolor=col, markeredgewidth=1.8, linestyle="none", zorder=5)
        ends.append((cs[K - 1], f"2024–26 (incomplete): half in {k}" if part else f"{plots.WINDOW_TICKS[w]}: half in {k}", col))
        rows += [{"cohort": "2024–26 (incomplete)" if part else plots.WINDOW_TICKS[w], "rank": int(r), "designs in the configuration": int(c[r - 1]),
                  "cumulative share": round(float(cs[r - 1]), 4), "crosses 50 % here": bool(r == k)} for r in ranks]
    ax.set_xlim(0.5, K + 11)
    ax.set_ylim(0, 1.12)
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.spines["bottom"].set_bounds(1, K)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_xlabel("configurations, ranked by size within the cohort")
    ax.set_ylabel("cumulative share of the cohort's designs")
    ax.text(0.7, 0.505, "50 %", ha="left", va="bottom", fontsize=FS)
    ys = [e[0] for e in ends]
    placed = plots._spread(ys, 0.09)
    for (y0, text, col), yl in zip(ends, placed):
        ax.annotate(text, xy=(K, y0), xytext=(K + 0.9, yl), textcoords="data", ha="left", va="center", fontsize=FS,
                    color=style.INK, annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=col, linewidth=0.8, shrinkA=0, shrinkB=2) if abs(yl - y0) > 0.02 else None)
    return fig, pd.DataFrame(rows)


# ================================================================================== items + writer
ITEMS = [
    dict(name="q6_selected_fields", group="II1_varying_attributes", role="main", kind="table", builder=tab_selected_fields_v2,
         title="Dimensions that tell designs apart", source_item="v2 of q6_selected_fields (Table 6)"),
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
