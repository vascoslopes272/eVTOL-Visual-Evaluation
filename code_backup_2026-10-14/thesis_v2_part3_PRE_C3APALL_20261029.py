"""Part III (Dominant design) figures and tables, v2: the Q6 (shares) and Q7 (conditions) thesis figures redrawn under the Part I/II
style and terms, plus the Analysis III additions (Spearman table, weights of condition 3, three-year check, granted-and-live base of F,
III.4 on the five directory categories). Every number is read from viz/thesis_q6.py, thesis_q7.py and viz/analysis3.py; this module only
draws, relabels and groups them for thesis_figures_v2/Part_III_dominant_design/ (notebook 52).

Terms (author's ruling 2026-10-13): architecture (never class), design or aircraft, cohort (never window), assignee; the levels of
description are A (architecture alone), A·W·T, A·U; the family stays F.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text

from viz.relabel import directory_builder           # the VFS directory's own category (rerun of 2026-10-15)
from viz import analysis3, frames, plots, style
from viz import thesis_q6 as q6
from viz import thesis_q7 as q7
from viz import thesis_v2_part2 as p2

FS = p2.FS
arch = p2.arch


def _bump(fig, fs: float = FS):
    """No text of the figure under ``fs`` pt: the original builders print 7 to 7.5 pt, the thesis style 8."""
    for t in fig.findobj(Text):
        if t.get_text() and t.get_fontsize() < fs:
            t.set_fontsize(fs)
    return fig


def _cohort(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: c.replace("windows", "cohorts").replace("window", "cohort") for c in df.columns})


#: the levels of description as the CSV/JSON beside Figure 12 print them (author's ruling 2026-10-13); F is Lift + Cruise and CVT on a fixed wing
LEVEL_CODE = {"A0": "A", "A1t": "A·W·T", "A0c": "A·U", "family_b": "F"}
LEVEL_NAME = {"A": "A — architecture", "A·W·T": "A·W·T — architecture, wings, tilt", "A·U": "A·U — architecture, propulsor units",
              "F": "F — Separate Lift + Cruise and Combined Vectored Thrust on a fixed wing"}


def _levels(df: pd.DataFrame) -> pd.DataFrame:
    """The level columns of a condition table in the new codes; ``top archetype`` is ``top configuration``. No value changes."""
    df = df.copy()
    df["level"] = df["level"].map(LEVEL_CODE)
    df["level name"] = df["level"].map(LEVEL_NAME)
    return df.rename(columns={"top archetype": "top configuration"})


# ===================================================================================== III1 shares
#: the smallest categories joined into "Other" (handoff 2026-10-15): the JOIN_N smallest by designs over the four complete cohorts, the
#: existing "Other" (no architecture recorded) among them; HB (18) stays apart, nearer TF and PTC (22 each) than PFV (9)
JOIN_N = 5


def joined_shares(ctx):
    """The cohort shares with the JOIN_N smallest categories summed into "Other"; returns (share, codes joined, totals over the complete cohorts)."""
    d = q6._data(ctx)
    cnt, share = d["cnt"], d["share"]
    complete = [w for w in ctx.WIN_NAMES if "partial" not in w]
    total = cnt.loc[complete].sum().sort_values(kind="stable")
    joined = list(total.index[:JOIN_N])
    keep = [c for c in style.CLASS_ORDER if c in cnt.columns and c not in joined]
    out = share[keep].copy()
    out["Other"] = share[joined].sum(axis=1)
    return out, joined, total



def fig_largest_architectures_over_time(ctx):
    """III1 main: the five largest architectures' share of each cohort's designs, one line each."""
    d = q6._data(ctx)
    share = d["share"]
    five = q6.CLASSES5
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    lines = share[five].copy()
    lines.index = list(range(len(lines)))
    plots.window_lines(ax, lines, n_few=0, ticks=list(ts.COHORTS))     # one-line cohort ticks (author 2026-10-23)
    n = len(ctx.WIN_NAMES)
    ax.axvspan(n - 1.5, n - 0.5, facecolor=plots.FEW_FILL, hatch=style.PARTIAL_HATCH, edgecolor=style.GRID, linewidth=0, zorder=0)
    ax.set_xlim(-0.3, n + 0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(0.04, 0.37)
    last = lines.iloc[-1]
    plots.end_labels(ax, n - 1, [last[c] for c in five], [arch(c).short for c in five], [style.cls(c).color for c in five], gap=0.03, fontsize=FS)
    ax.set_ylabel("share of all designs")                  # base: every design of the cohort (frames.class_counts_by_window)
    ax.set_xlabel(ts.COHORT_X)                             # the asterisk is named in the legend (author 2026-10-23)
    fig.legend(handles=[Line2D([], [], color=style.cls(c).color, linestyle=style.cls(c).dash, marker=style.cls(c).marker, markersize=4.6,
                               linewidth=1.4, label=f"{arch(c).short} {arch(c).name}") for c in five]
                       + [mpl.patches.Patch(facecolor=plots.FEW_FILL, hatch=style.PARTIAL_HATCH, edgecolor=style.GRID, linewidth=0,
                                            label=ts.INCOMPLETE_LABEL)],     # the incomplete cohort's band, as drawn
               loc="outside lower center", ncol=3, fontsize=FS, handlelength=2.0, columnspacing=1.0)
    return _bump(fig), share[five].round(4)


def tab_share_trend(ctx):
    """III1 main: Spearman rho of each architecture's yearly share on the priority year (architectures of 20 designs or more), over
    2008-2023 and over 2016-2023 alone (the same yearly shares, one point per year)."""
    t = analysis3.rho_table(ctx)
    t["architecture"] = [arch(c).name for c in t["code"]]
    t["code"] = [arch(c).short for c in t["code"]]
    t = t.rename(columns={"code": "architecture code", "aircraft": "designs", "years": "years"})
    t = t.drop(columns=["rho, years with 20+ aircraft", "p, years with 20+ aircraft", "p, years with 20+ aircraft (Holm)",
                        "years with 20+ aircraft"])   # handoff 2026-10-15: 2016-23 instead
    for col in ("p", "p (Holm)", "p, 2016-23", "p, 2016-23 (Holm)"):        # Holm within each span (supervisor review 2, 2026-10)
        t[col] = t[col].map(q7.pval5)
    return t, None


# ===================================================================================== III3 dominant design
def fig_condition1_f(ctx):
    fig, d = q7.fig_condition1_family(ctx)
    from matplotlib.text import Annotation
    notes = sorted([a for a in fig.findobj(Annotation) if a.get_text().startswith("all:")], key=lambda a: a.xy[0])
    for k, a in enumerate(notes):                      # at 8 pt the two "all" notes collide: one to the left, one to the right
        a.set_ha("right" if k == 0 else "left")
        a.set_position((a.xy[0] + (-0.1 if k == 0 else 0.4), a.get_position()[1]))
    return _bump(fig), d


#: shorter panel titles for Figure 12 (i) and (ii): at 8 pt the long ones run into each other (F has its own figure since 2026-10-15)
SHORT_TITLES = {"A0": "A\narchitecture", "A1t": "A·W·T\n+ wings, tilt", "A0c": "A·U\n+ propulsor units"}


def _with_short_titles(builder, ctx):
    keep = dict(q7.SET_TITLE)
    q7.SET_TITLE.update(SHORT_TITLES)
    try:
        return builder(ctx)
    finally:
        q7.SET_TITLE.update(keep)





def tab_levels_verdict(ctx):
    """The verdict on each base, never mixed: all designs (main) and actively protected (sensitivity)."""
    t, _ = analysis3.verdict_two_bases(ctx)
    return t, None


def tab_verdict_detail(ctx):
    _, t = analysis3.verdict_two_bases(ctx)
    return t, None


def tab_condition3_weights(ctx):
    return analysis3.weights_report(ctx)["table"], None


def tab_condition3_family(ctx):
    return analysis3.form_family(ctx), None


def tab_three_year_check(ctx):
    t3 = analysis3.three_year(q7._data(ctx))
    return pd.DataFrame([{"level": k, "years above 50 % in three consecutive years, actively protected designs": ", ".join(map(str, v)) or "none"}
                         for k, v in t3.items()]), None


def tab_granted_live_condition1(ctx):
    y = analysis3.granted_live(ctx, q7._data(ctx))["yearly"]
    t = y[y["priority year"] >= 2016].rename(columns={"aircraft": "designs", "F aircraft": "F designs", "F share": "share of F", "read": "read (20 designs or more)"})
    t["share of F"] = t["share of F"].round(4)
    return t, None


def tab_granted_live_condition2(ctx):
    b = analysis3.granted_live(ctx, q7._data(ctx))["balance"]
    t = b.rename(columns={"window": "cohort", "aircraft": "designs", "top archetype": "largest configuration"})
    return t[["cohort", "designs", "D2", "D2 permutation low", "D2 permutation high", "below band"]].rename(
        columns={"D2": "²D", "D2 permutation low": "band, lower edge", "D2 permutation high": "band, upper edge"}), None


# ===================================================================================== III4 directory categories

def tab_directory_fold(ctx):
    """The twelve architectures folded to the five directory categories (analysis.class_fold), with the designs behind each."""
    v = ctx.v[ctx.v["topType"].notna()]
    t = v.groupby(["class5", "topType"]).size().rename("designs").reset_index()
    t["architecture"] = [arch(c).name for c in t["topType"]]
    t["architecture code"] = [arch(c).short for c in t["topType"]]
    return t.rename(columns={"class5": "directory category"})[["directory category", "architecture code", "architecture", "designs"]], None



# ===================================================================================== thesis style (2026-10-20 restyle, Figs 4.9 to 4.13)
#: The five Part III figures of the dissertation are drawn here under notebooks/thesis_style.py (6.3 in wide, 8 pt floor, one bottom
#: legend, 2024-26 hollow and never joined). Every number comes from the same frames as before (thesis_q6, thesis_q7, analysis3).
import sys as _sys
import pathlib as _pathlib

import matplotlib as mpl

_NB = _pathlib.Path(__file__).resolve().parents[1] / "notebooks"
if str(_NB) not in _sys.path:
    _sys.path.insert(0, str(_NB))
import thesis_style as ts                                     # noqa: E402

#: the items drawn under the thesis style: written with ts.save (pdf + 300 dpi png), never resized afterwards
RESTYLED = ("q6_architecture_shares_by_cohort", "q7_condition2_balance", "q7_condition3_cohesion", "q7_family_conditions",
            "q7_iii4_directory_categories")
#: data code -> key of ts.ARCH (the data says TR and TB; the thesis prints Tilt Propulsor and Tilt Frame)
TS_CODE = {"TR": "TP", "TB": "TF"}
#: Figs 4.10 and 4.11 are a matched pair, stacked on one page: the same size and the SAME fixed panel geometry (layout=None)
PAIR_SIZE = (ts.TEXTWIDTH, 2.6)   # batch 2 (2026-10-23): + an x label per panel
#: Fig 4.9: sideways step between coincident 2024-26* markers (cohort units)
DODGE = 0.08
#: 2026-10-23: the panel labels moved under the panels; the axes keep their size (0.54 of the height) and move up into the freed title room
PAIR_ADJUST = dict(left=0.115, right=0.99, bottom=0.435, top=0.975, wspace=0.27)
PAIR_TITLES = ("(a) A, architecture", "(b) A·W·T, + wings, tilt", "(c) A·U, + propulsors")
#: helpers that belong in thesis_style (local until the coordinator moves them): a faint y grid, the grey of a year that is not read,
#: the reference-line grey
GRID_COLOR = "#EBEBEB"
UNREAD = "#9E9E9E"
REF = "#555555"
CI_LW = 0.8


def _exact(fig):
    """Every later savefig of ``fig`` keeps the exact page size: thesis.context applies viz.style, whose savefig.bbox is "tight", and a
    tight crop would change the 6.3 in width (and LaTeX would rescale the text). Belongs in thesis_style.save."""
    orig = fig.savefig

    def savefig(*a, **k):
        if k.get("bbox_inches") is None:
            with mpl.rc_context({"savefig.bbox": "standard"}):
                return orig(*a, **k)
        return orig(*a, **k)
    fig.savefig = savefig
    return fig


def _grid(ax):
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.5)
    ax.set_axisbelow(True)


def _legend_fixed(fig, handles, labels):
    """ts.bottom_legend for a figure with layout=None (fixed geometry): one row, no frame, at the bottom edge of the figure."""
    return fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=len(labels), frameon=False,
                      handlelength=1.6, columnspacing=1.2, borderaxespad=0.3)


def _band_series(ax, val, band_lo, band_hi, color, wlo=None, whi=None, met=None, dashed=False, dx=0.0, band=True):
    """One condition-2/3 series per cohort (x = 0..4, the last cohort incomplete): the permutation band as a ts.BAND fill (main
    series only), the four complete cohorts joined (solid filled, or dashed hollow for the actively protected base), the 95 % whiskers
    when given, 2024-26 hollow at alpha 0.6 and never joined, the cohorts where the condition is met in ts.HIGHLIGHT."""
    val = np.asarray(val, dtype=float)
    n = len(val)
    x = np.arange(n) + dx
    c = slice(0, n - 1)
    if band:
        ax.fill_between(np.arange(n), np.asarray(band_lo, float), np.asarray(band_hi, float), color=ts.BAND, linewidth=0, zorder=1)
    if wlo is not None:
        lo, hi = np.asarray(wlo, float), np.asarray(whi, float)
        ax.errorbar(x[c], val[c], yerr=[val[c] - lo[c], hi[c] - val[c]], fmt="none", ecolor=color, elinewidth=CI_LW, capsize=1.8, capthick=CI_LW, zorder=3)
        ax.errorbar(x[-1:], val[-1:], yerr=[val[-1:] - lo[-1:], hi[-1:] - val[-1:]], fmt="none", ecolor=color, elinewidth=CI_LW, capsize=1.8,
                    capthick=CI_LW, alpha=ts.INCOMPLETE_ALPHA, zorder=3)
    look = dict(linestyle="--", markerfacecolor="white", markeredgewidth=0.9) if dashed else dict(linestyle="-")
    ax.plot(x[c], val[c], marker="o", color=color, markeredgecolor=color, zorder=4, **look)
    ts.incomplete_point(ax, x[-1], val[-1], color, zorder=4)
    hit = [i for i, m in enumerate(met if met is not None else []) if m and i < n - 1]
    if hit:
        if dashed:
            ax.plot(x[hit], val[hit], "o", markersize=5.2, markerfacecolor="white", markeredgecolor=ts.HIGHLIGHT, markeredgewidth=1.2, zorder=6)
        else:
            ax.plot(x[hit], val[hit], "o", markersize=5.2, color=ts.HIGHLIGHT, markeredgecolor=ts.HIGHLIGHT, zorder=6)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_xticks(np.arange(n), ts.COHORTS_2L)
    _grid(ax)


def _pair_figure(ctx, panels, ylabel, sharey=False):
    """Fig 4.10: three panels, black series; under each panel its own x label, then its title PAIR_TITLES (batch 2, 2026-10-23: a shared
    x label under (b) read as part of (b)'s title); one unframed legend row under the panels. Constrained layout."""
    fig, axs = plt.subplots(1, 3, figsize=PAIR_SIZE, layout="constrained", sharey=sharey)
    for ax, ttl, p in zip(axs, PAIR_TITLES, panels):
        _band_series(ax, **p, color="black")
        ax.set_xlabel(ts.COHORT_X)
        ts.panel_label(ax, ttl)
    axs[0].set_ylabel(ylabel)
    ts.bottom_legend(fig, [mpl.patches.Patch(facecolor=ts.BAND, edgecolor="none"),
                           Line2D([], [], marker="o", color=ts.HIGHLIGHT, linestyle="none", markersize=5.2), ts.incomplete_handle("black")],
                     ["permutation band (95 %)", "below the band: condition met", ts.INCOMPLETE_LABEL])   # 2024-26* (author 2026-10-23)
    ts.fit_cohort_ticks(fig)
    ts.place_panel_labels(fig)
    return fig, axs


def fig_condition2_balance(ctx):
    """Fig 4.10: ²D per cohort with its 95 % interval over the rarefaction draws against the permutation band, levels A, A·W·T, A·U."""
    d = q7._data(ctx)
    bal, win = d["bal"], ctx.WIN_NAMES
    with mpl.rc_context(ts.RC):
        panels, tops = [], []
        for lvl in q7.MAIN_LEVELS:
            s = bal[bal["level"] == lvl].set_index("window").reindex(win)
            met = [bool(s.loc[w, "below band"]) and "partial" not in w for w in win]
            panels.append(dict(val=s["D2"], band_lo=s["D2 permutation low"], band_hi=s["D2 permutation high"], wlo=s["D2 low"], whi=s["D2 high"], met=met))
            tops.append(float(np.nanmax(s[["D2 high", "D2 permutation high"]].to_numpy())))
        fig, axs = _pair_figure(ctx, panels, "²D of all designs:\nlarge designs in play")   # base: frames.dd_balance_table, no protection filter
        for ax, t in zip(axs, tops):
            ax.set_ylim(0, t * 1.12)
        ts.fit_cohort_ticks(fig)                         # one-line cohort ticks, rotated where a panel is too narrow (as ts.save does)
        fig.canvas.draw()
    _exact(fig)
    return fig, _levels(_cohort(bal[bal["level"].isin(q7.MAIN_LEVELS)].reset_index(drop=True)))


#: Fig 4.11 alone: Q is computed on the aircraft, not the level, so A·W·T and A·U repeat panel (a); full width, one low row
COHESION_SIZE = (ts.TEXTWIDTH, 1.8)   # batch 2 (2026-10-23): compact, constrained layout
COHESION_ADJUST = dict(left=0.135, right=0.99, bottom=0.41, top=0.89)


def fig_condition3_form(ctx):
    """Fig 4.11: ΔQ per cohort (main weighting) against its permutation band, level A alone (panel (a) of the old three; Rao's Q does not
    depend on the level). The csv keeps the three levels' rows."""
    d = q7._data(ctx)
    form, win = d["form"], ctx.WIN_NAMES
    main = frames.Q_WEIGHTINGS[0]
    with mpl.rc_context(ts.RC):
        s = form[(form["level"] == "A0") & (form["weighting"] == main)].set_index("window").reindex(win)
        met = [bool(q < lo) and "partial" not in w for q, lo, w in zip(s["ΔQ"], s["ΔQ permutation low"], win)]
        fig, ax = plt.subplots(figsize=COHESION_SIZE, layout="constrained")
        fig.get_layout_engine().set(h_pad=0.02)
        _band_series(ax, s["ΔQ"], s["ΔQ permutation low"], s["ΔQ permutation high"], color="black", met=met)
        # base: frames.dd_form_table, no protection filter; "against the two earliest cohorts" (the ΔQ reference) goes to the caption
        ax.set_ylabel("ΔQ of all designs")
        ax.set_xlabel(ts.COHORT_X)
        ts.panel_label(ax, PAIR_TITLES[0].removeprefix("(a) "))
        ax.axhline(0, color=REF, linewidth=0.5, zorder=2)
        ts.bottom_legend(fig, [mpl.patches.Patch(facecolor=ts.BAND, edgecolor="none"),
                               Line2D([], [], marker="o", color=ts.HIGHLIGHT, linestyle="none", markersize=5.2), ts.incomplete_handle("black")],
                         ["permutation band (95 %)", "below the band: condition met", ts.INCOMPLETE_LABEL])   # 2024-26* (author 2026-10-23)
        ts.place_panel_labels(fig)
        fig.canvas.draw()
    _exact(fig)
    out = form[form["weighting"].eq(main) & form["level"].isin(q7.MAIN_LEVELS)].reset_index(drop=True)
    return fig, _levels(_cohort(out).drop(columns=["weighting"]))


def _spread(ys, gap, lo, hi):
    """Label positions: each label as near its value as possible, at least ``gap`` apart, inside [lo, hi]."""
    ys = np.asarray(ys, dtype=float)
    o = np.argsort(ys, kind="stable")
    p = ys[o].copy()
    p[0] = max(p[0], lo)
    for i in range(1, len(p)):
        p[i] = max(p[i], p[i - 1] + gap)
    if p[-1] > hi:
        p[-1] = hi
        for i in range(len(p) - 2, -1, -1):
            p[i] = min(p[i], p[i + 1] - gap)
    out = np.empty_like(p)
    out[o] = p
    return out


def _tick_n(ax, ns) -> None:
    """Fig 4.9 (author 2026-10-24): under each cohort tick a second, grey line "n 63" = every design of the cohort (the base of the shares),
    as in Fig 4.14, at the tick font size; placed one line under the tick label's own anchor, and the axis title moved down by that line."""
    import matplotlib.transforms as mtrans
    tick = ax.xaxis.get_major_ticks()[0]
    trans, va, _ = ax.get_xaxis_text1_transform(tick.get_pad() + tick.get_tick_padding())
    fs = ax.get_xticklabels()[0].get_fontsize()
    line = 1.25 * fs
    trans = trans + mtrans.ScaledTranslation(0, -line / 72, ax.figure.dpi_scale_trans)
    for xi, n in enumerate(ns):
        ax.text(xi, 0, f"n {int(n)}", transform=trans, ha="center", va=va, fontsize=fs, color=p2.NOTE, clip_on=False)
    ax.xaxis.labelpad += line


def fig_architecture_shares_by_cohort(ctx):
    """Fig 4.9: each architecture's share of the cohort's designs, one line per architecture in its ts.ARCH colour (SLC, TP, CVT thick,
    the rest thin and lighter); the JOIN_N smallest categories joined into "Other"; 2024-26 hollow, not joined; direct labels at the right."""
    d = q6._data(ctx)
    n_win = d["n_win"]
    share, joined, _ = joined_shares(ctx)
    codes = list(share.columns)
    big = ("SLC", "TR", "CVT")
    with mpl.rc_context(ts.RC):
        fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, 2.5), layout="constrained")
        n = len(share)
        x = np.arange(n)
        # 2024-26* markers that coincide (within 0.6 percentage points) are dodged sideways by DODGE cohort units, so each is visible
        last_v = share.iloc[-1].to_numpy(dtype=float) * 100
        groups = {}
        for c, yv in zip(codes, last_v):
            key = next((g for g in groups if abs(g - yv) < 0.6), yv)
            groups.setdefault(key, []).append(c)
        dodge = {}
        for members in groups.values():
            k = len(members)
            for i, c in enumerate(members):
                dodge[c] = ((k - 1) / 2 - i) * DODGE        # the first in code order takes the lowest label (_spread is stable): leftmost marker -> highest label, so the leaders never cross
        for c in codes[::-1]:                                   # the large architectures drawn last, on top
            col = ts.ARCH[TS_CODE.get(c, c)]
            y = share[c].to_numpy(dtype=float) * 100
            main = c in big
            ax.plot(x[:-1], y[:-1], marker="o", color=col, linewidth=2.0 if main else 0.9, markersize=4.0 if main else 2.6,
                    alpha=1.0 if main else 0.6, zorder=4 if main else 3)
            ts.incomplete_point(ax, x[-1] + dodge[c], y[-1], col, markersize=4.0 if main else 2.8, zorder=4)
        top = float(np.ceil(share.to_numpy().max() * 100 / 5) * 5 + 2)
        ax.set_ylim(0, top)
        ax.set_xlim(-0.3, n + 1.55)
        ax.spines["bottom"].set_bounds(-0.3, n - 1 + 0.3)
        ax.set_xticks(x, ts.COHORTS)
        _tick_n(ax, n_win)
        ax.set_ylabel("share of all designs (%)")          # base: every design of the cohort (frames.class_counts_by_window)
        ax.set_xlabel(ts.COHORT_X)
        _grid(ax)
        n_none = int(ctx.v["topType"].isna().sum())
        note = "n counts every design of the cohort" + (f", including {n_none} in 2016–19 with no architecture recorded" if n_none else "")
        assert ctx.v.loc[ctx.v["topType"].isna(), "window"].eq("2016-19").all(), "the base note names 2016-19 only"
        leg = ts.bottom_legend(fig, [ts.incomplete_handle(), Line2D([], [], linestyle="none")], [ts.INCOMPLETE_LABEL, note], ncol=1)
        leg.get_texts()[1].set_color(p2.NOTE)               # base of the shares, one grey line under the entry (author 2026-10-24)
        fig.canvas.draw()
        gap = abs(ax.transData.inverted().transform((0, 0))[1] - ax.transData.inverted().transform((0, 10.2 * fig.dpi / 72))[1])
        last = share.iloc[-1].to_numpy(dtype=float) * 100
        pos = _spread(last, gap, 0.6, top - 1.0)
        xl = n - 1 + 0.42
        for c, yv, yp in zip(codes, last, pos):
            k = TS_CODE.get(c, c)
            col = ts.ARCH[k]
            main = c in big
            ax.plot([n - 1 + dodge[c] + 0.07, xl - 0.06], [yv, yp], color=col, linewidth=0.5, alpha=1.0 if main else 0.7, zorder=2)
            ax.text(xl, yp, ts.ARCH_NAME[k] if k != "Other" else "Other", color=col, ha="left", va="center", fontsize=8.4,
                    fontweight="bold" if main else "normal")
        fig.canvas.draw()
    _exact(fig)
    return fig, share.round(4).assign(designs=n_win)


#: Fig 4.11 (c) note (batch 5, author 2026-10-28): one line; "(vs. two earliest cohorts)" left out because it ran past the page; the y
#: label already says "against the two earliest cohorts"
C3_NOTE = "met below the band"          # the longer form ran past the page edge (measured, batch 5)


def fig_family_conditions(ctx):
    """Fig 4.11: the three conditions on F, all designs (solid, filled) and actively protected (dashed, hollow), colour ts.ARCH['F']:
    (a) share per priority year from 2016 against 50 %, (b) ²D per cohort with its band, (c) ΔQ per cohort with its band. The values are
    the tidy table of thesis_q7.fig_family_conditions; its "granted and live" series is not drawn (and left out of the table).
    Legends pass (author 2026-10-28): the test of each panel in words under its label, five legend entries in two rows, the footnote."""
    import matplotlib.pyplot as _plt
    from lib import dominant_design as _dd
    f0, data = q7.fig_family_conditions(ctx)
    _plt.close(f0)
    data = data[data["base"] != "granted and live"].reset_index(drop=True)
    win = ctx.WIN_NAMES
    col = ts.ARCH["F"]
    bases = (("all designs", False, 0.0), ("actively protected", True, 0.14))
    with mpl.rc_context(ts.RC):
        fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(ts.TEXTWIDTH, 2.94), layout="constrained")   # 2.5 + labels under the panels (2026-10-23); 3.35: + notes, footnote (2026-10-28); 3.23: legend in rows (batch 4); 2.94: one-line notes, one entry fewer (batch 5)
        # (a) condition 1, read years only
        p1 = data[data["panel"] == "(a) condition 1"]
        top_at = {}
        for base, dashed, _ in bases:
            s = p1[(p1["base"] == base) & p1["drawn"]]
            yrs, y = s["year / cohort"].astype(int).to_numpy(), s["value"].to_numpy(float) * 100
            look = dict(linestyle="--", markerfacecolor="white", markeredgewidth=0.9) if dashed else dict(linestyle="-")
            a1.plot(yrs, y, marker="o", color=col, markeredgecolor=col, zorder=4 if not dashed else 3, **look)
            met = sorted(_dd.condition1_years(pd.DataFrame({"priority year": yrs, "read": True, "above 50 %": y > 50})))
            for yr in met:
                yy = y[list(yrs).index(yr)]
                if dashed:
                    a1.plot(yr, yy, "o", markersize=5.2, markerfacecolor="white", markeredgecolor=ts.HIGHLIGHT, markeredgewidth=1.2, zorder=6)
                else:
                    a1.plot(yr, yy, "o", markersize=5.2, color=ts.HIGHLIGHT, zorder=6)
            for yr, yy in zip(yrs, y):
                top_at[yr] = max(top_at.get(yr, 0), yy)
        s_all = p1[(p1["base"] == "all designs") & p1["drawn"]]
        for yr, sh in zip(s_all["year / cohort"].astype(int), s_all["value"].astype(float)):
            if sh > 0.5:
                a1.annotate(f"{100 * sh:.1f}{ts.THIN}%", (yr, top_at[yr]), textcoords="offset points", xytext=(0, 4), ha="center", va="bottom", fontsize=8.4, color=col)
        a1.axhline(50, color=REF, linewidth=0.8, linestyle=(0, (4, 2)), zorder=2)
        yrs_all = sorted(p1["year / cohort"].astype(int).unique())
        a1.text(yrs_all[0] - 0.4, 51, f"50{ts.THIN}% threshold", ha="left", va="bottom", fontsize=8.4, color=REF)
        a1.set_xlim(yrs_all[0] - 0.5, yrs_all[-1] + 0.5)
        a1.set_xticks(yrs_all, [str(y) if (y - yrs_all[0]) % 2 == 0 else "" for y in yrs_all])
        a1.set_ylim(0, 75)
        a1.set_yticks([0, 20, 40, 60])
        a1.set_ylabel("share of designs in F (%)")
        a1.set_xlabel("priority year")
        ts.panel_label(a1, "(a) share", note=f"met above 50{ts.THIN}% in two consecutive years")     # one line each (batch 5)
        _grid(a1)
        # (b) condition 2 and (c) condition 3, per cohort
        for ax, panel, whisk in ((a2, "(b) condition 2", True), (a3, "(c) condition 3", False)):
            p = data[data["panel"] == panel]
            for base, dashed, dx in bases:
                s = p[p["base"] == base].set_index("year / cohort").reindex(win)
                _band_series(ax, s["value"], s["band low"], s["band high"], col, wlo=s["whisker low"] if whisk and not dashed else None,
                             whi=s["whisker high"] if whisk and not dashed else None, met=s["met"].astype(bool).tolist(), dashed=dashed, dx=dx,
                             band=not dashed)
            ax.set_xlabel(ts.COHORT_X)
        a2.set_ylim(0, float(np.nanmax(data.loc[data["panel"] == "(b) condition 2", ["value", "band high", "whisker high"]].to_numpy(float))) * 1.12)
        a2.set_ylabel("²D of F")
        ts.panel_label(a2, "(b) balance", note="met below the band")
        a3.axhline(0, color=REF, linewidth=0.5, zorder=2)
        a3.set_ylabel("ΔQ of F against the\ntwo earliest cohorts")
        ts.panel_label(a3, "(c) disparity", note=C3_NOTE)
        # batch 4 (author 2026-10-28): the five entries in rows across the page width, the footnote at the end of the last row
        ts.compact_legend(fig, [Line2D([], [], color=col, marker="o"),
                               Line2D([], [], color=col, marker="o", linestyle="--", markerfacecolor="white", markeredgewidth=0.9),
                               mpl.patches.Patch(facecolor=ts.BAND, edgecolor="none"),
                               Line2D([], [], marker="o", color=ts.HIGHLIGHT, linestyle="none", markersize=5.2)],
                         ["all designs", "actively protected designs", f"95{ts.THIN}% permutation band", "condition met"],
                         footnote=ts.INCOMPLETE_FOOTNOTE)            # batch 5: the 2024-26* entry dropped, the footnote says it
        ts.fit_cohort_ticks(fig)
        ts.place_panel_labels(fig)
        fig.canvas.draw()
    _exact(fig)
    return fig, data


def _vt_yearly(ctx) -> dict:
    """Vectored Thrust's share of each priority year's designs (2008 to the last complete year) on the two bases of analysis3.directory
    (all designs with a directory category; actively protected), with read = 20 designs or more (frames.DD_YEAR_MIN)."""
    v = ctx.v
    state = frames.patent_state(ctx.ds, v)
    k = v["class5"].where(v["topType"].notna())
    live = v["aircraft_id"].map(state["in_force"]).astype(bool)
    yrs = list(range(frames.DD_YEAR_FIRST, ctx.cfg.analysis["last_complete_year"] + 1))
    out = {}
    for base, mask in (("all", k.notna()), ("in force", live & k.notna())):
        n = np.array([int((mask & v["year"].eq(y)).sum()) for y in yrs])
        vt = np.array([int((mask & v["year"].eq(y) & k.eq("VT")).sum()) for y in yrs])
        out[base] = pd.DataFrame({"priority year": yrs, "designs": n, "VT designs": vt, "VT share": np.where(n > 0, vt / np.maximum(n, 1), np.nan),
                                  "read": n >= frames.DD_YEAR_MIN})
    return out


def _runs(years):
    """Consecutive runs of the sorted years: [2016, 2017, 2021] -> [(2016, 2017), (2021, 2021)]."""
    runs = []
    for y in sorted(years):
        if runs and y == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], y)
        else:
            runs.append((y, y))
    return runs


def fig_directory_categories(ctx):
    """Fig 4.13: (a) Vectored Thrust's share per priority year, all designs solid and actively protected dashed (years under 20 designs
    hollow grey), the 50 % line, and the years where condition 1 is met (a read year above 50 % next to another one) as red bars, one row
    per base; (b) ²D per cohort with its 95 % interval against the permutation band. Colour ts.VFS['Vectored Thrust'].
    Restored 2026-10-23 (author) from the pre-batch-2 version: the direct labels kept; one legend row for the incomplete cohort."""
    r = analysis3.directory(ctx, q7._data(ctx))
    vy = _vt_yearly(ctx)
    for base in ("all", "in force"):                         # VT is the largest category in every read year: the share drawn is condition 1's
        t = r["yearly"][base].set_index("priority year")
        rd = vy[base][vy[base]["read"]].set_index("priority year")
        if not (t.loc[rd.index, "largest archetype"].eq("VT").all() and np.allclose(t.loc[rd.index, "its share"], rd["VT share"], atol=1e-4)):
            import warnings
            warnings.warn(f"fig_directory_categories: VT is not the largest category in every read year ({base})")
    col = ts.VFS["Vectored Thrust"]
    win = ctx.WIN_NAMES
    bal = r["balance"].set_index("window").reindex(win)
    with mpl.rc_context(ts.RC):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(ts.TEXTWIDTH, 2.7), layout="constrained", gridspec_kw=dict(width_ratios=[1.6, 1]))   # 2.5 + labels under the panels (2026-10-23)
        for base, dashed in (("all", False), ("in force", True)):
            t = vy[base]
            yrs, y, rd = t["priority year"].to_numpy(), t["VT share"].to_numpy(float) * 100, t["read"].to_numpy(bool)
            ls = "--" if dashed else "-"
            first = int(np.argmax(rd))
            a1.plot(yrs[:first + 1], y[:first + 1], linestyle=ls, color=UNREAD, linewidth=0.9, zorder=2)
            mk = "^" if dashed else "o"                  # round 5: shape tells the base (all designs circle, actively protected triangle)
            a1.plot(yrs[~rd], y[~rd], mk, markerfacecolor="white", markeredgecolor=UNREAD, markeredgewidth=0.8, linestyle="none", zorder=3)
            a1.plot(yrs[rd], y[rd], marker=mk, linestyle=ls, color=col, markeredgecolor=col, zorder=4)   # filled: hollow = incomplete cohort only
        a1.axhline(50, color=REF, linewidth=0.8, linestyle=(0, (4, 2)), zorder=1)
        y0, y1 = int(vy["all"]["priority year"].iloc[0]), int(vy["all"]["priority year"].iloc[-1])
        a1.text(y1 + 0.5, 48, "50 %", ha="right", va="top", fontsize=8.4, color=REF)
        a1.text(2011.5, 24, f"under {frames.DD_YEAR_MIN} designs: not tested", ha="center", va="bottom", fontsize=8.4, color=UNREAD)
        for row, (yy, met, lab) in enumerate(((17, r["met_all"], "met, all designs"), (6, r["met"], "met, actively protected"))):
            runs = _runs(met)
            for a, b in runs:
                a1.plot([a - 0.4, b + 0.4], [yy, yy], color=ts.HIGHLIGHT, linewidth=3.2, solid_capstyle="butt", zorder=4)
            if runs:
                a1.text(runs[0][0] - 0.65, yy, lab, ha="right", va="center", fontsize=8.4, color=ts.HIGHLIGHT)
        a1.text(2018.6, 78, "actively protected", ha="center", va="bottom", fontsize=8.4, color=col)
        a1.text(2020.0, 34, "all designs", ha="center", va="top", fontsize=8.4, color=col)
        a1.set_xlim(y0 - 0.5, y1 + 0.5)
        a1.set_xticks(range(y0, y1 + 1), [str(y) if (y - y0) % 2 == 0 else "" for y in range(y0, y1 + 1)])
        a1.set_ylim(0, 105)
        a1.set_yticks([0, 20, 40, 60, 80, 100])
        a1.set_ylabel("share of designs in\nVectored Thrust (%)")
        a1.set_xlabel("priority year")
        ts.panel_label(a1, "(a) condition 1, Vectored Thrust share")
        _grid(a1)
        metw = [bool(bal.loc[w, "below band"]) and "partial" not in w for w in win]
        _band_series(a2, bal["D2"], bal["D2 permutation low"], bal["D2 permutation high"], col, wlo=bal["D2 low"], whi=bal["D2 high"], met=metw)
        a2.set_ylim(0, float(np.nanmax(bal[["D2 high", "D2 permutation high"]].to_numpy(float))) * 1.15)
        a2.set_ylabel("²D of all designs with a\ndirectory category: large\ndesigns in play")   # base: analysis3.directory, every design with a directory category (625 of 627)
        a2.set_xlabel(ts.COHORT_X)
        ts.panel_label(a2, "(b) condition 2, balance")
        ts.bottom_legend(fig, [ts.incomplete_handle(col)], [ts.INCOMPLETE_LABEL])    # (b) draws 2024-26* (author 2026-10-23)
        ts.fit_cohort_ticks(fig)
        ts.place_panel_labels(fig)
        fig.canvas.draw()
    _exact(fig)
    return fig, r["balance"].rename(columns={"window": "cohort", "top archetype": "top category"})


ITEMS = [
    dict(name="q6_architecture_shares_by_cohort", group="III1_architecture_shares", role="main", kind="figure", builder=fig_architecture_shares_by_cohort,
         title="Architecture share per priority cohort", source_item="v2 of q6_class_shares_by_window (Figure 10 (i))"),
    dict(name="q6_largest_architectures_over_time", group="III1_architecture_shares", role="main", kind="figure", builder=fig_largest_architectures_over_time,
         title="Five largest architectures over time", source_item="v2 of q6_largest_classes_over_time (Figure 10 (ii))"),
    dict(name="q6_share_trend_spearman", group="III1_architecture_shares", role="main", kind="table", builder=tab_share_trend,
         title="Spearman rho of each architecture's share on priority year", source_item="new (Analysis III item 1)"),
    dict(name="q7_condition1_family", group="III2_III3_dominant_design", role="main", kind="figure", builder=fig_condition1_f,
         title="Condition 1 on F per priority year", source_item="v2 of q7_condition1_family (Figure 11)"),
    dict(name="q7_condition2_balance", group="III2_III3_dominant_design", role="main", kind="figure", builder=fig_condition2_balance,
         title="Condition 2: ²D against its band", source_item="v2 of q7_condition2_balance (Figure 12 (i))"),
    dict(name="q7_condition3_cohesion", group="III2_III3_dominant_design", role="main", kind="figure", builder=fig_condition3_form,
         title="Condition 3: ΔQ against its band", source_item="v2 of q7_condition3_cohesion (Figure 12 (ii))"),
    dict(name="q7_family_conditions", group="III2_III3_dominant_design", role="main", kind="figure", builder=fig_family_conditions,
         title="The three conditions on F: all designs and actively protected", source_item="new (handoff 2026-10-15, Task 3)"),
    dict(name="q7_verdict_table", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_levels_verdict,
         title="The dominant-design verdict, levels A, A·W·T, A·U and F", source_item="v2 of q7_verdict_table (Table 8)"),
    dict(name="q7_verdict_detail", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_verdict_detail,
         title="The numbers behind the verdict, each base", source_item="new (results freeze 2026-10-14)"),
    dict(name="q7_condition3_weights", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_condition3_weights,
         title="Weights of the form distance", source_item="new (Analysis III item 2)"),
    dict(name="q7_condition3_family", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_condition3_family,
         title="Condition 3 on F: actively protected, all designs, granted and live", source_item="new (weights of 2026-10-14)"),
    dict(name="q7_three_year_check", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_three_year_check,
         title="Condition 1 with three consecutive years", source_item="new (Analysis III item 4)"),
    dict(name="q7_granted_live_condition1", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_granted_live_condition1,
         title="F's share on granted and live patents alone", source_item="new (Analysis III item 5)"),
    dict(name="q7_granted_live_condition2", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_granted_live_condition2,
         title="²D of F on granted and live patents alone", source_item="new (Analysis III item 5)"),
    dict(name="q7_iii4_directory_categories", group="III4_directory_categories", role="main", kind="figure", builder=directory_builder(fig_directory_categories),
         title="Conditions 1 and 2 on the five directory categories", source_item="new (Analysis III item 6)"),
    dict(name="q7_iii4_directory_fold", group="III4_directory_categories", role="appendix", kind="table", builder=tab_directory_fold,
         title="Architectures folded to the directory categories", source_item="analysis.class_fold"),
]


def out_root(cfg):
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_III_dominant_design"


def save_v2_item(item: dict, cfg, ctx):
    """Built and saved under the Part I/II style, through Part II's writer pointed at this part's folder; the items in RESTYLED are drawn
    under notebooks/thesis_style.py and written with ts.save (pdf + 300 dpi png, width and 8 pt floor checked), csv and json beside."""
    if item["name"] in RESTYLED:
        import json
        fig, data = item["builder"](ctx)
        out = out_root(cfg) / item["group"] / item["role"]
        ts.save(fig, item["name"], out)
        if data is not None:
            data.to_csv(out / f"{item['name']}.csv", index=False)
        meta = {k: item[k] for k in ("name", "group", "role", "kind", "title", "source_item")}
        meta.update(width_in=round(fig.get_figwidth(), 3), height_in=round(fig.get_figheight(), 3), style="notebooks/thesis_style.py")
        (out / f"{item['name']}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
        return fig, data
    p2.out_root, saved = out_root, p2.out_root
    try:
        return p2.save_v2_item(item, cfg, ctx)
    finally:
        p2.out_root = saved
