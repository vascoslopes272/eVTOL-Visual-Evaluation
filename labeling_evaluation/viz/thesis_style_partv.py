"""Part V (assignees and regions): the five dissertation figures 4.17-4.21 redrawn in the one thesis style (notebooks/thesis_style.py).

Same data and the same CSV as the builders they replace; only the drawing changes. The data come from the shared modules
(thesis_q2 / thesis_q3 / thesis_q7 / analysis5), never recomputed here:

    4.17 q2_filer_types                  fig_filer_types           (thesis_q2._filer_types_parts)
    4.18 q2_largest_filers_share         fig_largest_filers_share  (thesis_q2._frames: sizes, cov)
    4.17 q3_region_design_all_years      fig_region_design_all_years   (data of thesis_q3.fig_region_design_all_years; NA w/o its largest
                                                                        assignee from thesis_q7._data)
    4.18 q3_region_mix_by_window_class   fig_region_mix_by_window_class (data of thesis_q3.fig_region_mix_by_window_class; trends from
                                                                        thesis_q3._frames['mc'])
    4.21 q7_region_family_share          fig_region_family_share   (thesis_q7._data: ln, ts)

Every builder returns (fig, data) at 6.3 in wide with layout='constrained'; save with thesis_style.save (no bbox_inches='tight').
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

_NB = pathlib.Path(__file__).resolve().parents[1] / "notebooks"
if str(_NB) not in sys.path:
    sys.path.insert(0, str(_NB))
import thesis_style as ts  # noqa: E402

from viz import frames  # noqa: E402
from viz import thesis_q2 as q2  # noqa: E402
from viz import thesis_q3 as q3  # noqa: E402
from viz import thesis_q7 as q7  # noqa: E402

REGIONS = frames.REGIONS
ABBR = {"North America": "NA", "Europe": "EU", "Asia-Pacific": "AP"}
INK = "#222222"            # local: dark text (should move into thesis_style as ts.INK)
MUTED = "#555555"          # local: secondary text and reference lines (should move into thesis_style as ts.MUTED)
TS = 8.4                   # tick-size text used for direct labels
#: the cohort keys of the frames -> the printed cohort labels of the style
COHORT = dict(zip(["<= 2011", "2012-15", "2016-19", "2020-23", "2024-26 (partial)"], ts.COHORTS))
COHORT_2L = dict(zip(["<= 2011", "2012-15", "2016-19", "2020-23", "2024-26 (partial)"], ts.COHORTS_2L))
INCOMPLETE = "2024-26 (partial)"
#: ts.ARCH key of each class code of the regional frames
DODGE = {"North America": -0.13, "Europe": 0.0, "Asia-Pacific": 0.13}     # x offset of the 2024-26* hollow markers in 4.20
ARCH_KEY = {"SLC": "SLC", "TR": "TP", "CVT": "CVT", "TW": "TW", "MR": "MR", "other": "Other"}
ARCH_TITLE = {"SLC": "Separate Lift + Cruise", "TR": "Tilt Propulsor", "CVT": "Combined Vectored Thrust", "TW": "Tilt Wing",
              "MR": "Multicopter", "other": "other"}


def _rc():
    return mpl.rc_context(ts.RC)


def _pct(x: float, d: int = 0) -> str:
    return f"{100 * x:.{d}f} %"


def _spread(ys, gap):
    """Positions for direct labels: the values moved apart until neighbours are at least ``gap`` apart (order kept)."""
    order = np.argsort(ys)
    out = np.array(ys, dtype=float)[order]
    for _ in range(50):
        moved = False
        for i in range(1, len(out)):
            if out[i] - out[i - 1] < gap - 1e-9:
                push = (gap - (out[i] - out[i - 1])) / 2
                out[i - 1] -= push
                out[i] += push
                moved = True
        if not moved:
            break
    res = np.empty_like(out)
    res[order] = out
    return res


# ---------------------------------------------------------------------------------------------- 4.17 assignee types
#: Fig 4.18 (round 5, 2026-10-23): one blue, dark -> light (company, individual inventors, universities and institutes); the text in the
#: segment's colour, darkened where the fill is too light to read on white
ATYPE_COL = {"Named company": ts.ATYPE["Company"], "Individual inventor": ts.BLUES[2], "University / institute": ts.BLUES[0]}
ATYPE_TEXT = {"Named company": ts.ATYPE["Company"], "Individual inventor": ts.BLUES[3], "University / institute": "#4A8CC2"}
ATYPE_INK = {"Named company": "white", "Individual inventor": INK, "University / institute": INK}   # value labels inside the segment
INC_ROW_ALPHA = 0.45                                                                                # the 2024-26* row
ATYPE_WORD = {"Named company": "company", "Individual inventor": "individual inventor", "University / institute": "universities\nand institutes"}   # two lines: one runs to the page edge


def fig_filer_types(ctx):
    """Fig 4.18 (restored 2026-10-23 from the pre-batch-2 version at the author's request): horizontal 100 % rows, all designs, all
    patents, then each cohort; company and individual shares inside, university in a column on the right, the type names above the
    bars. The 2024-26* row in the same colours as the others, marked only by the asterisk on its label; the asterisk rule as one line
    under the axis (ts.INCOMPLETE_LABEL). Data and CSV as thesis_q2.fig_filer_types_flat."""
    parts, parts_n, bars = q2._filer_types_parts(ctx)
    order = ["Named company", "Individual inventor", "University / institute"]
    sh = parts[order].div(parts[order].sum(axis=1), axis=0)
    # rows top to bottom: all designs (bar 1), all patents (bar 0), a gap, the cohorts
    rows = [1, 0] + list(range(2, len(bars)))
    labels = ["all designs", "all patents"] + [COHORT[b] for b in bars[2:]]
    ypos = [0, 1] + [2.45 + k for k in range(len(bars) - 2)]
    with _rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, 2.6), layout="constrained")
        for y, r in zip(ypos, rows):
            left = 0.0
            inc = bars[r] == INCOMPLETE
            for k in order:
                v = float(sh.loc[r, k])
                ax.barh(y, v, 0.72, left=left, color=ATYPE_COL[k], alpha=INC_ROW_ALPHA if inc else 1.0, edgecolor="white", linewidth=0.6)
                if k != "University / institute" and v >= 0.08:
                    col = INK if inc else ATYPE_INK[k]          # the faded dark blue is too light for white text
                    ax.text(left + v / 2, y, f"{100 * v:.1f} %", ha="center", va="center", fontsize=TS, color=col)
                left += v
            ax.text(1.025, y, f"{100 * float(sh.loc[r, 'University / institute']):.1f} %", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=TS, color=ATYPE_TEXT["University / institute"])
        # the key as direct labels over the first row
        s0 = sh.loc[rows[0]]
        cx = {"Named company": s0["Named company"] / 2, "Individual inventor": s0["Named company"] + s0["Individual inventor"] / 2}
        for k, x in cx.items():
            ax.text(x, -0.62, ATYPE_WORD[k], ha="center", va="bottom", fontsize=TS, color=ATYPE_TEXT[k])
        ax.text(1.025, -0.62, ATYPE_WORD["University / institute"], transform=ax.get_yaxis_transform(), ha="left", va="bottom",
                fontsize=TS, color=ATYPE_TEXT["University / institute"])
        ax.set_yticks(ypos, labels)
        ax.set_ylabel("priority-year cohort")      # author 2026-10-23
        ax.set_ylim(ypos[-1] + 0.55, -0.62)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1], ["0", "25", "50", "75", "100"])
        ax.set_xlabel("share of all designs (%)")      # the "all patents" row's base is in the caption (author 2026-10-23)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        fig.legend(handles=[Line2D([], [], linestyle="none", label=ts.INCOMPLETE_LABEL)], loc="outside lower center", frameon=False,
                   handlelength=0, handletextpad=0)      # the asterisk rule, one line (author 2026-10-23)
    data = parts.assign(bar=bars, n=parts_n)
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.19 concentration
BAND_DESC = ["≥ 10 designs", "5–9 designs", "2–4 designs", "1 design"]
#: Fig 4.19 (round 5, 2026-10-23): the area under the curve shaded by size group in the blue scale of Fig 4.18, darkest for the largest
BAND_FILL = [ts.ATYPE["Company"], ts.BLUES[3], ts.BLUES[2], ts.BLUES[0]]


def fig_largest_filers_share(ctx):
    """Fig 4.19: the cumulative share of all designs held by the companies and universities (named assignees; individual inventors are
    excluded, hence the curve stops at 70 %) ranked largest first. Round 5 (2026-10-23): the area under the curve shaded by size group
    (dark blue for the largest), each group named "<n> assignees with <k> designs each" in a small key with its shade, a dot at the end
    of each group labelled with its cumulative share; the dashed line of all named assignees kept."""
    d = q2._frames(ctx)
    sizes, cov, v = d["sizes"], d["cov"], ctx.v
    n_air, n_named = len(v), len(sizes)
    cum = (sizes.cumsum() / n_air).to_numpy()
    rank = np.arange(1, n_named + 1)
    xs, ys = np.r_[0, rank], np.r_[0, cum]
    edges = [0] + cov["cumulative firms"].astype(int).tolist()
    with _rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, 2.4), layout="constrained")
        for k in range(len(edges) - 1):                                 # the area of each group, under its stretch of the curve
            sl = slice(edges[k], edges[k + 1] + 1)
            ax.fill_between(xs[sl], 0, ys[sl], step="post", color=BAND_FILL[k], linewidth=0, zorder=1)
        ax.step(xs, ys, where="post", color=ts.ATYPE["Company"], linewidth=1.2, zorder=3, solid_capstyle="butt")
        share_named = float(sizes.sum() / n_air)
        ax.axhline(share_named, color=MUTED, linewidth=0.7, linestyle="--", zorder=2)
        ax.text(n_named - 16, share_named + 0.03, f"all {n_named} companies and universities: {int(sizes.sum())} designs, {_pct(share_named)}",
                ha="right", va="bottom", fontsize=TS, color=MUTED)      # ends short of the last dot, whose share is printed above it
        ends = edges[1:]
        for k, e in enumerate(ends):                                    # a dot at the end of each group, its cumulative share above-left
            ax.plot(e, cum[e - 1], "o", color=INK, markersize=4, zorder=5)   # (on white, above the curve; the first one centred)
            first = k == 0
            ax.annotate(_pct(cum[e - 1]), (e, cum[e - 1]), xytext=(3, 9) if first else (-3, 4), textcoords="offset points",
                        ha="center" if first else "right", va="bottom", fontsize=TS, color=INK, zorder=6)
        names = [f"{int(r['firms'])} assignees with {BAND_DESC[k].replace('designs', 'designs each').replace('1 design', '1 design each')}"
                 for k, r in cov.reset_index(drop=True).iterrows()]
        ax.legend(handles=[Patch(facecolor=BAND_FILL[k], edgecolor="none", label=names[k]) for k in range(len(names))],
                  loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False, fontsize=TS, handlelength=1.2, handleheight=0.9,
                  columnspacing=1.2, labelspacing=0.3, borderaxespad=0.2)
        ax.set_xlim(0, n_named + 2)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, .2, .4, .6, .8, 1], ["0", "20", "40", "60", "80", "100"])
        ax.set_xticks([0, 50, 100, 150, n_named])
        ax.set_ylabel(f"cumulative share of\nall {n_air} designs (%)")
        ax.set_xlabel("companies and universities ranked by designs, largest first")
    data = pd.DataFrame({"rank": rank, "firm": sizes.index, "unique aircraft": sizes.to_numpy(), "cumulative share": np.round(cum, 4)})
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.19 regional profile
def _region_handles(ns=None):
    hs, ls = [], []
    for r in REGIONS:
        hs.append(Patch(facecolor=ts.REGION[r], edgecolor="none"))       # colour only (sweep 3: no markers on the bars)
        ls.append(f"{r} (n {ns[r]})" if ns else r)
    return hs, ls


def fig_region_design_all_years(ctx):
    """4.17: three panels, one shared y axis: (a) architecture, (b) propulsors per aircraft, (c) any propulsor tilts; three bars per
    category (region colours, the region marker on each bar top); (c) also North America without its largest assignee (hollow marker).
    Legends pass (author 2026-10-28): what each panel counts under its label, the architecture key on the line under the legend, and
    "NA without <largest assignee>" a legend entry instead of a label with a leader in (c)."""
    fig0, data = q3.fig_region_design_all_years(ctx)
    plt.close(fig0)
    big = q7._data(ctx)["ts"].attrs["left_out"]
    na_wo = float(q7._data(ctx)["ln"].set_index("region").loc["North America", "tilting share without it"])
    panels = [("class", "(a) architecture", q3.CLASSES5, ["SLC", "TP", "CVT", "TW", "MR", "other"]),
              ("propulsive units", "(b) propulsors per aircraft", q3.UNIT_ANS, [a.replace("-", "–") for a in q3.UNIT_ANS]),
              ("tilting unit", "(c) any propulsor tilts", [True], ["any tilt"])]
    notes = {"class": "architecture of the region's designs", "propulsive units": "propulsors per design",
             "tilting unit": "share with any\ntilting propulsor"}
    ns = {r: int(data[(data["variable"] == "class") & (data["region"] == r)]["n"].iloc[0]) for r in REGIONS}
    with _rc():
        fig, axs = plt.subplots(1, 3, figsize=(ts.TEXTWIDTH, 3.18), layout="constrained", sharey=True,   # 2.45 + labels under the panels (2026-10-23); 3.18 (batch 4, legend in one row), 3.36: + notes, legend row, key line, bar height kept (2026-10-28)
                                gridspec_kw=dict(width_ratios=[6, 5, 3.2]))
        for ax, (var, title, answers, ticks) in zip(axs, panels):
            sub = data[data["variable"] == var].set_index("region")
            x = np.arange(len(answers), dtype=float)
            bw = 0.36 if var == "tilting unit" else 0.27                     # wider bars in (c) so its white values have room
            for j, r in enumerate(REGIONS):
                n = float(sub.loc[r, "n"])
                vals = np.array([float(sub.loc[r, a]) / n for a in answers])
                xx = x + (j - 1) * bw
                ax.bar(xx, vals, bw, color=ts.REGION[r], edgecolor="white", linewidth=0.4, zorder=2)
                if var == "tilting unit":
                    ax.text(xx[0], vals[0] / 2, f"{100 * vals[0]:.0f}", ha="center", va="center", fontsize=TS, color="white", zorder=5)
            if var == "tilting unit":
                xna = x[0] - bw
                na_mark = dict(ls="none", marker=ts.REGION_MARKER["North America"], mfc="white", mec=ts.REGION["North America"], ms=4.2, mew=1.0)
                ax.plot([xna], [na_wo], zorder=5, **na_mark)
                short = big.split(" /")[0] + "/" + big.split("/ ")[-1] if "/" in big else big
                ax.set_xlim(-0.65, 1.75)
            else:
                ax.set_xlim(-0.55, len(answers) - 0.45)
            ax.set_xticks(x, ticks)
            ax.tick_params(axis="x", length=0)
            ts.panel_label(ax, title, note=notes[var])
        axs[0].set_ylim(0, 0.7)
        axs[0].set_yticks(np.arange(0, 0.71, 0.1), [f"{v}" for v in range(0, 71, 10)])
        axs[0].set_ylabel("share of the region's\ndesigns, all years (%)")
        # the base of each panel (q3.fig_region_design_all_years: the region's designs with that field recorded, 2026-10-23)
        axs[0].text(0.02, 0.98, "base: the region's designs with the\npanel's field recorded", transform=axs[0].transAxes, ha="left", va="top",
                    fontsize=TS, color=MUTED)
        for ax in axs[1:]:
            ax.tick_params(axis="y", left=False)
            ax.spines["left"].set_visible(False)
        h, l = _region_handles(ns)
        # (c)'s small dot named in the legend, its value kept (author 2026-10-28); the architecture key on the line under the legend
        h.append(Line2D([], [], **na_mark))
        l.append(f"NA without {short}, {100 * na_wo:.0f}{ts.THIN}%")
        ts.compact_legend(fig, h, l,          # batch 4 (2026-10-28): the four entries in one row where they fit, the key line under them
                          keyline="SLC Separate Lift + Cruise, TP Tilt Propulsor, CVT Combined Vectored Thrust, TW Tilt Wing, MR Multicopter")
        ts.place_panel_labels(fig)
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.20 architecture per region and cohort
#: Fig 4.18 page height: 3.4 in before the legends pass; 3.93 keeps the plot height with the two-column legend and the footnote (above the
#: 3.6 in ceiling; accepted by the author 2026-10-28)
C_HEIGHT = 3.76   # batch 4 (2026-10-28): legend in three rows instead of four
def fig_region_mix_by_window_class(ctx):
    """4.18: 2 x 3 small line charts, one per architecture; x = cohort from 2012-15, a line per region (colour and marker); a cell under
    frames.CH5_THIN designs is not drawn; 2024-26* hollow and never joined. The significant trend (NA in CVT) is in the caption, not the
    figure (author 2026-10-23, kept 2026-10-28). Legends pass (2026-10-28): the n per cohort of each region, the two marks, the footnote."""
    fig0, data = q3.fig_region_mix_by_window_class(ctx)
    plt.close(fig0)
    mc = q3._frames(ctx)["mc"]
    wins = frames.CH5_WINS + [INCOMPLETE]
    x = np.arange(len(wins), dtype=float)
    with _rc():
        fig, axs = plt.subplots(2, 3, figsize=(ts.TEXTWIDTH, C_HEIGHT), layout="constrained", sharex=True, sharey=True)   # 3.4 + labels under the panels (2026-10-23); C_HEIGHT: + legend rows (2026-10-28)
        for k, (ax, c) in enumerate(zip(axs.flat, q3.CLASSES5)):
            for r in REGIONS:
                s = data[data["region"] == r].set_index("window")
                n = s.loc[wins, "n"].to_numpy(float)
                y = s.loc[wins, c].to_numpy(float) / np.where(n > 0, n, np.nan)
                ok = n >= frames.CH5_THIN
                yc = np.where(ok[:-1], y[:-1], np.nan)                       # complete cohorts: joined where consecutive
                ax.plot(x[:-1], yc, color=ts.REGION[r], marker=ts.REGION_MARKER[r], ms=3.5, lw=1.2, zorder=3)
                if ok[-1]:                                                       # dodged by region so coincident points stay visible
                    ts.incomplete_point(ax, x[-1] + DODGE[r], y[-1], ts.REGION[r], marker=ts.REGION_MARKER[r], ms=3.5, zorder=3)
            ts.panel_label(ax, f"({'abcdef'[k]}) {ARCH_TITLE[c]}")
            # the significant trends (NA in CVT: rho +0.24, p < 0.001) are in the caption (sweep 3, 2026-10-23), not in the panel
        axs[0, 0].set_ylim(0, 0.6)
        axs[0, 0].set_yticks([0, .2, .4], ["0", "20", "40"])
        axs[0, 0].set_xlim(-0.35, len(wins) - 0.65)
        for ax in axs[1]:
            ax.set_xticks(x, [COHORT_2L[w] for w in wins], rotation=30, ha="right", rotation_mode="anchor")   # 30 degrees: flat, "2020–23" and "2024–26" touch (author 2026-10-23)
            ax.set_xlabel(ts.COHORT_X)                  # own label on each bottom panel, above its panel label (batch 2: no shared label)
        ylab = fig.supylabel("share of the region's designs\nwith an architecture (%)", fontsize=9)   # two lines: it must fit the plots' height
        h = [Line2D([], [], color=ts.REGION[r], marker=ts.REGION_MARKER[r], ms=3.5, lw=1.2) for r in REGIONS]
        h.append(ts.incomplete_handle(MUTED))            # 2024-26*: hollow light markers, named in the legend (author 2026-10-23)
        h.append(Line2D([], [], linestyle="none"))
        # legends pass (author 2026-10-28): each region's n per cohort in cohort order, the two marks in words, the footnote line
        ns = {r: ", ".join(str(int(v)) for v in data[data["region"] == r].set_index("window").loc[wins, "n"]) for r in REGIONS}
        # batch 4 (2026-10-28): the three regions on the first row (closer spacing, so they fit); the two marks and the footnote do not
        # fit one row, so "missing point" comes first and "open marker" shares the last row with the footnote, both about 2024-26
        ts.compact_legend(fig, [h[0], h[1], h[2], h[4], h[3]], [f"{r} ({ABBR[r]}, n {ns[r]})" for r in REGIONS]
                          + [f"missing point = cohort under {frames.CH5_THIN} designs, not plotted", "open marker = 2024–26*, incomplete cohort"],
                          footnote=ts.INCOMPLETE_FOOTNOTE, breaks=[3, 4], bare=[3], colsep=0.8, borderaxespad=0.2, handlelength=1.4)
        ts.place_panel_labels(fig)
        fig.canvas.draw()                                # the y label centred on the plots, not on the page with its legend (2026-10-28)
        top, bot = axs[0, 0].get_position().y1, axs[1, 0].get_position().y0
        ylab.set_y((top + bot) / 2)
        ylab.set_va("center")
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.21 family F per region
def fig_region_family_share(ctx):
    """4.21: each region's share of designs in F per cohort from 2012 (a cell under frames.CH5_THIN designs not drawn), direct end labels,
    the chi-square p of the regional difference as a second tick line."""
    d = q7._data(ctx)
    ln = d["ln"]
    wins = frames.CH5_WINS
    xw = np.arange(len(wins), dtype=float)
    with _rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, 2.3), layout="constrained")
        ends, notes = [], []
        for _, r in ln.iterrows():
            reg = r["region"]
            ys = np.array([r[f"F share {w}"] for w in wins], dtype=float)
            ok = np.array([r[f"F base {w}"] >= frames.CH5_THIN for w in wins])
            ax.plot(xw, np.where(ok, ys, np.nan), color=ts.REGION[reg], marker=ts.REGION_MARKER[reg], ms=4, lw=1.4, zorder=3)
            ends.append((reg, ys[-1]))
            for i in np.where(~ok)[0]:
                notes.append((reg, i, int(r[f"F base {wins[i]}"])))
        pos = _spread([e[1] for e in ends], 0.06)
        for (reg, yv), yp in zip(ends, pos):
            ax.text(xw[-1] + 0.08, yp, f"{ABBR[reg]} {_pct(yv)}", ha="left", va="center", fontsize=TS, color=ts.REGION[reg])
        # a cohort under frames.CH5_THIN designs is not drawn; its n is in the caption (sweep 3, 2026-10-23)
        ax.set_xticks(xw, [f"{COHORT[w]}\nχ² p {q7.pval5(q7._tp(d, 'family F', w))}" for w in wins])
        ax.set_xlim(-0.3, len(wins) - 0.45)
        ax.set_ylim(0.10, 0.65)                                         # from 10 %: the lowest value drawn is 22 % (sweep 3)
        ax.set_yticks([.2, .4, .6], ["20", "40", "60"])
        ax.set_xlabel(ts.COHORT_X)
        ax.set_ylabel("share of the region's\ndesigns in family F (%)")
        # base: frames.region_lean, F base = the region's designs of the cohort with an architecture (2026-10-23)
        ax.text(0.01, 0.98, "base: the region's designs with an architecture, per cohort", transform=ax.transAxes, ha="left", va="top",
                fontsize=TS, color=MUTED)
    cols = ["region"] + [c for c in ln.columns if c.startswith("F ")]
    return fig, ln[cols]


#: the five restyled figures by file name (used by viz/latex_v15_partv.py and viz/thesis_v2_part5.py)
BUILDERS = {"q2_filer_types": fig_filer_types, "q2_largest_filers_share": fig_largest_filers_share,
            "q3_region_design_all_years": fig_region_design_all_years, "q3_region_mix_by_window_class": fig_region_mix_by_window_class,
            "q7_region_family_share": fig_region_family_share}
