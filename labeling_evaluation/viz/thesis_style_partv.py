"""Part V (assignees and regions): the five dissertation figures 4.17-4.21 redrawn in the one thesis style (notebooks/thesis_style.py).

Same data and the same CSV as the builders they replace; only the drawing changes. The data come from the shared modules
(thesis_q2 / thesis_q3 / thesis_q7 / analysis5), never recomputed here:

    4.17 q2_filer_types                  fig_filer_types           (thesis_q2._filer_types_parts)
    4.18 q2_largest_filers_share         fig_largest_filers_share  (thesis_q2._frames: sizes, cov)
    4.19 q3_region_design_all_years      fig_region_design_all_years   (data of thesis_q3.fig_region_design_all_years; NA w/o its largest
                                                                        assignee from thesis_q7._data)
    4.20 q3_region_mix_by_window_class   fig_region_mix_by_window_class (data of thesis_q3.fig_region_mix_by_window_class; trends from
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
ATYPE_COL = {"Named company": ts.ATYPE["Company"], "Individual inventor": ts.ATYPE["Individual inventor"],
             "University / institute": ts.ATYPE["University / institute"]}
ATYPE_WORD = {"Named company": "company", "Individual inventor": "individual inventor", "University / institute": "univ. / inst."}


def fig_filer_types(ctx):
    """4.17: horizontal 100 % rows, all designs, all patents, then each cohort; company and individual shares inside, university in a column
    on the right; 2024-26* at alpha 0.6. Data and CSV as thesis_q2.fig_filer_types_flat."""
    parts, parts_n, bars = q2._filer_types_parts(ctx)
    order = ["Named company", "Individual inventor", "University / institute"]
    sh = parts[order].div(parts[order].sum(axis=1), axis=0)
    # rows top to bottom: all designs (bar 1), all patents (bar 0), a gap, the cohorts
    rows = [1, 0] + list(range(2, len(bars)))
    labels = ["all designs", "all patents"] + [COHORT[b] for b in bars[2:]]
    ypos = [0, 1] + [2.45 + k for k in range(len(bars) - 2)]
    with _rc():
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, 2.45), layout="constrained")
        for y, r in zip(ypos, rows):
            faded = bars[r] == INCOMPLETE
            left = 0.0
            for k in order:
                v = float(sh.loc[r, k])
                ax.barh(y, v, 0.72, left=left, color=ATYPE_COL[k], alpha=ts.INCOMPLETE_ALPHA if faded else 1.0,
                        edgecolor="white", linewidth=0.6)
                if k != "University / institute" and v >= 0.08:
                    col = "white" if (k == "Named company" and not faded) else INK
                    ax.text(left + v / 2, y, f"{100 * v:.1f} %", ha="center", va="center", fontsize=TS, color=col)
                left += v
            ax.text(1.025, y, f"{100 * float(sh.loc[r, 'University / institute']):.1f} %", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=TS, color=ATYPE_COL["University / institute"])
        # the key as direct labels over the first row
        s0 = sh.loc[rows[0]]
        cx = {"Named company": s0["Named company"] / 2, "Individual inventor": s0["Named company"] + s0["Individual inventor"] / 2}
        for k, x in cx.items():
            ax.text(x, -0.62, ATYPE_WORD[k], ha="center", va="bottom", fontsize=TS, color=ATYPE_COL[k] if k == "Named company" else MUTED)
        ax.text(1.025, -0.62, ATYPE_WORD["University / institute"], transform=ax.get_yaxis_transform(), ha="left", va="bottom",
                fontsize=TS, color=ATYPE_COL["University / institute"])
        ax.set_yticks(ypos, labels)
        ax.set_ylim(ypos[-1] + 0.55, -0.62)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1], ["0", "25", "50", "75", "100"])
        ax.set_xlabel("share of designs, or of patents for all patents (%)")
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    data = parts.assign(bar=bars, n=parts_n)
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.18 concentration
BAND_DESC = ["≥10 designs", "5–9 designs", "2–4 designs", "1 design"]


def fig_largest_filers_share(ctx):
    """4.18: the cumulative share of all designs held by the named assignees ranked largest first, coloured by size group A-D
    (ts.BLUES dark to light), the group brackets under the axis, the group ends marked, the share of all named assignees dashed."""
    d = q2._frames(ctx)
    sizes, cov, v = d["sizes"], d["cov"], ctx.v
    n_air, n_named = len(v), len(sizes)
    cum = (sizes.cumsum() / n_air).to_numpy()
    rank = np.arange(1, n_named + 1)
    xs, ys = np.r_[0, rank], np.r_[0, cum]
    edges = [0] + cov["cumulative firms"].astype(int).tolist()
    cols = [ts.BLUES[4], ts.BLUES[3], ts.BLUES[2], ts.BLUES[1]]
    letters = "ABCD"
    with _rc():
        fig, (ax, axb) = plt.subplots(2, 1, figsize=(ts.TEXTWIDTH, 2.6), layout="constrained", height_ratios=[1, 0.13])
        for k in range(len(edges) - 1):
            sl = slice(edges[k], edges[k + 1] + 1)
            ax.step(xs[sl], ys[sl], where="post", color=cols[k], linewidth=1.6, zorder=3, solid_capstyle="butt")
        share_named = float(sizes.sum() / n_air)
        ax.axhline(share_named, color=MUTED, linewidth=0.7, linestyle="--", zorder=1)
        ax.text(n_named, share_named + 0.03, f"all {n_named} named assignees: {int(sizes.sum())} designs, {_pct(share_named)}",
                ha="right", va="bottom", fontsize=TS, color=MUTED)
        ends = [edges[k + 1] for k in range(len(edges) - 1)]
        ax.plot(ends, [cum[e - 1] for e in ends], "o", color=INK, markersize=4, zorder=5)
        for e in ends[:-1]:
            ax.annotate(_pct(cum[e - 1]), (e, cum[e - 1]), xytext=(5, -3), textcoords="offset points", ha="left", va="top", fontsize=TS, color=INK)
        # group descriptions: A and B are short stretches, labelled above with leader lines; C and D beside their stretch
        desc = [f"{letters[k]}  {BAND_DESC[k]}: {int(r['firms'])} assignees" for k, r in cov.reset_index(drop=True).iterrows()]
        for k, ytxt, xtxt in ((0, 0.93, 18), (1, 0.82, 28)):
            x0, x1 = edges[k], edges[k + 1]
            xm = (x0 + x1) / 2
            ym = float(np.interp(xm, xs, ys)) + 0.02
            ax.text(xtxt, ytxt, desc[k], ha="left", va="center", fontsize=TS, color=INK)
            ax.plot([xm, xtxt - 0.8], [ym, ytxt - 0.035], color=MUTED, linewidth=0.5, zorder=2)        # leader line (a Line2D, not an arrow)
        xc = (edges[2] + edges[3]) / 2
        ax.text(xc + 4, float(np.interp(xc, xs, ys)) - 0.05, desc[2], ha="left", va="top", fontsize=TS, color=INK)
        xd = (edges[3] + edges[4]) / 2
        ax.text(xd, float(np.interp(xd, xs, ys)) - 0.07, desc[3], ha="center", va="top", fontsize=TS, color=INK)
        ax.set_xlim(0, n_named + 2)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, .2, .4, .6, .8, 1], ["0", "20", "40", "60", "80", "100"])
        ax.set_xticks([0, 50, 100, 150, n_named])
        ax.set_ylabel(f"cumulative share of\nthe {n_air} designs (%)")
        # brackets A-D under the x axis
        for k in range(len(edges) - 1):
            a, b = edges[k] + 0.4, edges[k + 1] - 0.4
            axb.plot([a, a, b, b], [1, 0.55, 0.55, 1], color=cols[k], linewidth=1.6, solid_capstyle="butt", clip_on=False)
            axb.text((edges[k] + edges[k + 1]) / 2, 0.3, letters[k], ha="center", va="top", fontsize=TS, fontweight="bold", color=INK)
        axb.set_xlim(ax.get_xlim())
        axb.set_ylim(-0.6, 1)
        axb.set_xticks([]); axb.set_yticks([])
        for sp in axb.spines.values():
            sp.set_visible(False)
        axb.set_xlabel("named assignees ranked by designs, largest first")
    data = pd.DataFrame({"rank": rank, "firm": sizes.index, "unique aircraft": sizes.to_numpy(), "cumulative share": np.round(cum, 4)})
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.19 regional profile
def _region_handles(ns=None):
    hs, ls = [], []
    for r in REGIONS:
        hs.append((Patch(facecolor=ts.REGION[r], edgecolor="none"),
                   Line2D([], [], ls="none", marker=ts.REGION_MARKER[r], mfc="white", mec=ts.REGION[r], ms=3.5, mew=0.8)))
        ls.append(f"{r} (n {ns[r]})" if ns else r)
    return hs, ls


def fig_region_design_all_years(ctx):
    """4.19: three panels, one shared y axis: (a) architecture, (b) propulsors per aircraft, (c) any propulsor tilts; three bars per
    category (region colours, the region marker on each bar top); (c) also North America without its largest assignee (hollow marker)."""
    fig0, data = q3.fig_region_design_all_years(ctx)
    plt.close(fig0)
    big = q7._data(ctx)["ts"].attrs["left_out"]
    na_wo = float(q7._data(ctx)["ln"].set_index("region").loc["North America", "tilting share without it"])
    panels = [("class", "(a) architecture", q3.CLASSES5, ["SLC", "TP", "CVT", "TW", "MR", "other"]),
              ("propulsive units", "(b) propulsors per aircraft", q3.UNIT_ANS, [a.replace("-", "–") for a in q3.UNIT_ANS]),
              ("tilting unit", "(c) any propulsor tilts", [True], ["any tilt"])]
    ns = {r: int(data[(data["variable"] == "class") & (data["region"] == r)]["n"].iloc[0]) for r in REGIONS}
    with _rc():
        fig, axs = plt.subplots(1, 3, figsize=(ts.TEXTWIDTH, 2.45), layout="constrained", sharey=True,
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
                ax.plot(xx, vals, ls="none", marker=ts.REGION_MARKER[r], mfc="white", mec=ts.REGION[r], ms=3.2, mew=0.8, zorder=4)
                if var == "tilting unit":
                    ax.text(xx[0], vals[0] / 2, f"{100 * vals[0]:.0f}", ha="center", va="center", fontsize=TS, color="white", zorder=5)
            if var == "tilting unit":
                xna = x[0] - bw
                ax.plot([xna], [na_wo], ls="none", marker=ts.REGION_MARKER["North America"], mfc="white", mec=ts.REGION["North America"],
                        ms=4.2, mew=1.0, zorder=5)
                short = big.split(" /")[0] + "/" + big.split("/ ")[-1] if "/" in big else big
                xt, yt = x[0] + 0.6, 0.60
                ax.text(xt, yt, f"NA without\n{short}: {100 * na_wo:.0f} %", ha="left", va="center", fontsize=TS,
                        color=ts.REGION["North America"])
                ax.plot([xna + 0.07, xt - 0.03], [na_wo, yt], color=ts.REGION["North America"], linewidth=0.5, zorder=5)
                ax.set_xlim(-0.65, 1.75)
            else:
                ax.set_xlim(-0.55, len(answers) - 0.45)
            ax.set_xticks(x, ticks)
            ax.tick_params(axis="x", length=0)
            ax.set_title(title)
        axs[0].set_ylim(0, 0.7)
        axs[0].set_yticks(np.arange(0, 0.71, 0.1), [f"{v}" for v in range(0, 71, 10)])
        axs[0].set_ylabel("share of the region's\ndesigns, all years (%)")
        for ax in axs[1:]:
            ax.tick_params(axis="y", left=False)
            ax.spines["left"].set_visible(False)
        h, l = _region_handles(ns)
        ts.bottom_legend(fig, h, l)
    return fig, data


# ---------------------------------------------------------------------------------------------- 4.20 architecture per region and cohort
def fig_region_mix_by_window_class(ctx):
    """4.20: 2 x 3 small line charts, one per architecture; x = cohort from 2012-15, a line per region (colour and marker); a cell under
    frames.CH5_THIN designs is not drawn; 2024-26* hollow and never joined. Each significant 2012-2023 trend (p < 0.05) printed in its panel."""
    fig0, data = q3.fig_region_mix_by_window_class(ctx)
    plt.close(fig0)
    mc = q3._frames(ctx)["mc"]
    wins = frames.CH5_WINS + [INCOMPLETE]
    x = np.arange(len(wins), dtype=float)
    with _rc():
        fig, axs = plt.subplots(2, 3, figsize=(ts.TEXTWIDTH, ts.H_TWO_ROWS), layout="constrained", sharex=True, sharey=True)
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
            ax.set_title(f"({'abcdef'[k]}) {ARCH_TITLE[c]}")
            sig = mc[(mc["variable"] == "class") & (mc["answer"] == c) & (mc["p"] < 0.05)]
            for i, (_, t) in enumerate(sig.iterrows()):
                p = "p < 0.001" if t["p"] < 0.001 else f"p {t['p']:.3f}"
                ax.text(0.03, 0.97 - 0.13 * i, f"{ABBR[t['region']]} ρ {t['rho']:+.2f}, {p}".replace("ρ -", "ρ −"), transform=ax.transAxes,
                        ha="left", va="top", fontsize=TS, color=ts.REGION[t["region"]])
        axs[0, 0].set_ylim(0, 0.6)
        axs[0, 0].set_yticks([0, .2, .4], ["0", "20", "40"])
        axs[0, 0].set_xlim(-0.35, len(wins) - 0.65)
        for ax in axs[1]:
            ax.set_xticks(x, [COHORT_2L[w] for w in wins])
        fig.supylabel("share of the region's designs (%)", fontsize=9)
        h = [Line2D([], [], color=ts.REGION[r], marker=ts.REGION_MARKER[r], ms=3.5, lw=1.2) for r in REGIONS]
        h.append(Line2D([], [], ls="none", marker="o", mfc="white", mec=MUTED, mew=0.8, ms=3.5, alpha=ts.INCOMPLETE_ALPHA))
        ts.bottom_legend(fig, h, list(REGIONS) + ["2024–26* (incomplete)"])
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
        for reg, i, n in notes:
            ax.text(xw[i], 0.42, f"{reg}:\nn {n}, not plotted", ha="center", va="center", fontsize=8, color=ts.REGION[reg])
        ax.set_xticks(xw, [f"{COHORT[w]}\nχ² p {q7.pval5(q7._tp(d, 'family F', w))}" for w in wins])
        ax.set_xlim(-0.3, len(wins) - 0.45)
        ax.set_ylim(0, 0.65)
        ax.set_yticks([0, .2, .4, .6], ["0", "20", "40", "60"])
        ax.set_xlabel("priority cohort")
        ax.set_ylabel("share in family F (%)")
    cols = ["region"] + [c for c in ln.columns if c.startswith("F ")]
    return fig, ln[cols]


#: the five restyled figures by file name (used by viz/latex_v15_partv.py and viz/thesis_v2_part5.py)
BUILDERS = {"q2_filer_types": fig_filer_types, "q2_largest_filers_share": fig_largest_filers_share,
            "q3_region_design_all_years": fig_region_design_all_years, "q3_region_mix_by_window_class": fig_region_mix_by_window_class,
            "q7_region_family_share": fig_region_family_share}
