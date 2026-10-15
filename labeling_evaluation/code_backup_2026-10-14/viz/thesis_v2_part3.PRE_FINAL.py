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
              "F": "F — Lift + Cruise and CVT on a fixed wing"}


def _levels(df: pd.DataFrame) -> pd.DataFrame:
    """The level columns of a condition table in the new codes; ``top archetype`` is ``top configuration``. No value changes."""
    df = df.copy()
    df["level"] = df["level"].map(LEVEL_CODE)
    df["level name"] = df["level"].map(LEVEL_NAME)
    return df.rename(columns={"top archetype": "top configuration"})


# ===================================================================================== III1 shares
def fig_architecture_shares_by_cohort(ctx):
    """III1 main: the architectures' share of each cohort's designs (100 % bars; a segment of 5 % or more prints its share)."""
    d = q6._data(ctx)
    cnt, share, n_win = d["cnt"], d["share"], d["n_win"]
    codes = [c for c in style.CLASS_ORDER if c in cnt.columns] + ["Other"]
    ticks = [f"{ctx.WSHORT.get(w, '24–26*')}\nn {int(n)}" for w, n in zip(ctx.WIN_NAMES, n_win)]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.6), constrained_layout=True)
    sh = share[codes].copy()
    sh.index = list(range(len(sh)))
    plots.share_bars(ax, sh, partial=[len(sh) - 1], min_label=0.05, label_kind="pct")
    ax.set_xticks(range(len(ctx.WIN_NAMES)), ticks)
    ax.set_ylabel("share of the cohort's designs")
    ax.set_xlabel("priority cohort (* still filling)")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    fig.legend(handles=[Patch(facecolor=arch(c).color if c != "Other" else style.cls(c).color, hatch=style.cls(c).hatch, edgecolor="white",
                              label=f"{arch(c).short} {arch(c).name}" if c != "Other" else "no architecture recorded") for c in codes],
               loc="outside lower center", ncol=4, fontsize=FS, handlelength=1.2, columnspacing=1.0)
    return _bump(fig), share.round(4).assign(designs=n_win)


def fig_largest_architectures_over_time(ctx):
    """III1 main: the five largest architectures' share of each cohort's designs, one line each."""
    d = q6._data(ctx)
    share = d["share"]
    five = q6.CLASSES5
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    lines = share[five].copy()
    lines.index = list(range(len(lines)))
    plots.window_lines(ax, lines, n_few=0, ticks=[ctx.WSHORT.get(w, "24–26*") for w in ctx.WIN_NAMES])
    n = len(ctx.WIN_NAMES)
    ax.axvspan(n - 1.5, n - 0.5, facecolor=plots.FEW_FILL, hatch=style.PARTIAL_HATCH, edgecolor=style.GRID, linewidth=0, zorder=0)
    ax.set_xlim(-0.3, n + 0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(0.04, 0.37)
    last = lines.iloc[-1]
    plots.end_labels(ax, n - 1, [last[c] for c in five], [arch(c).short for c in five], [style.cls(c).color for c in five], gap=0.03, fontsize=FS)
    ax.set_ylabel("share of the cohort's designs")
    ax.set_xlabel("priority cohort (* still filling)")
    fig.legend(handles=[Line2D([], [], color=style.cls(c).color, linestyle=style.cls(c).dash, marker=style.cls(c).marker, markersize=4.6,
                               linewidth=1.4, label=f"{arch(c).short} {arch(c).name}") for c in five],
               loc="outside lower center", ncol=3, fontsize=FS, handlelength=2.0, columnspacing=1.0)
    return _bump(fig), share[five].round(4)


def tab_share_trend(ctx):
    """III1 main: Spearman rho of each architecture's yearly share on the priority year (architectures of 20 designs or more)."""
    t = analysis3.rho_table(ctx)
    t["architecture"] = [arch(c).name for c in t["code"]]
    t["code"] = [arch(c).short for c in t["code"]]
    t = t.rename(columns={"code": "architecture code", "aircraft": "designs", "years": "years",
                          "rho, years with 20+ aircraft": "rho, years of 20+ designs", "p, years with 20+ aircraft": "p, years of 20+ designs",
                          "years with 20+ aircraft": "years of 20+ designs"})
    t["p"] = t["p"].map(q7.pval5)
    t["p, years of 20+ designs"] = t["p, years of 20+ designs"].map(q7.pval5)
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


def fig_condition2_balance(ctx):
    keep = dict(q7.SET_TITLE)                           # shorter panel titles: at 8 pt the long ones run into each other
    q7.SET_TITLE.update({"A0": "A\narchitecture", "A1t": "A·W·T\n+ wings, tilt", "A0c": "A·U\n+ propulsor units", "family_b": "F\nLift + Cruise and CVT\non a fixed wing"})
    try:
        fig, d = q7.fig_condition2_balance(ctx)
    finally:
        q7.SET_TITLE.update(keep)
    return _bump(fig), _levels(_cohort(d))


def fig_condition3_form(ctx):
    fig, d = q7.fig_condition3_cohesion(ctx)
    fig.axes[0].set_ylabel("ΔQ against the two\nearliest cohorts")
    return _bump(fig), _levels(_cohort(d).drop(columns=["weighting"]))


def tab_levels_verdict(ctx):
    t, _ = q7.tab_verdict(ctx)
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
def fig_directory_categories(ctx):
    r = analysis3.directory(ctx, q7._data(ctx))
    fig = analysis3.fig_directory(ctx, r)
    return _bump(fig), r["balance"].rename(columns={"window": "cohort", "top archetype": "top category"})


def tab_directory_fold(ctx):
    """The twelve architectures folded to the five directory categories (analysis.class_fold), with the designs behind each."""
    v = ctx.v[ctx.v["topType"].notna()]
    t = v.groupby(["class5", "topType"]).size().rename("designs").reset_index()
    t["architecture"] = [arch(c).name for c in t["topType"]]
    t["architecture code"] = [arch(c).short for c in t["topType"]]
    return t.rename(columns={"class5": "directory category"})[["directory category", "architecture code", "architecture", "designs"]], None


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
    dict(name="q7_verdict_table", group="III2_III3_dominant_design", role="appendix", kind="table", builder=tab_levels_verdict,
         title="The dominant-design verdict, levels A, A·W·T, A·U and F", source_item="v2 of q7_verdict_table (Table 8)"),
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
    dict(name="q7_iii4_directory_categories", group="III4_directory_categories", role="main", kind="figure", builder=fig_directory_categories,
         title="Conditions 1 and 2 on the five directory categories", source_item="new (Analysis III item 6)"),
    dict(name="q7_iii4_directory_fold", group="III4_directory_categories", role="appendix", kind="table", builder=tab_directory_fold,
         title="Architectures folded to the directory categories", source_item="analysis.class_fold"),
]


def out_root(cfg):
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_III_dominant_design"


def save_v2_item(item: dict, cfg, ctx):
    """Built and saved under the Part I/II style, through Part II's writer pointed at this part's folder."""
    p2.out_root, saved = out_root, p2.out_root
    try:
        return p2.save_v2_item(item, cfg, ctx)
    finally:
        p2.out_root = saved
