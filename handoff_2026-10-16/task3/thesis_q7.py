"""Thesis question Q7 — Is there a dominant design? (chapter 4, part Convergence analysis).

Items: Table 7 (the archetype sets), Figure 11 (condition 1 on F), Figure 12 (i) and (ii) as two single graphs
(conditions 2 and 3), Table 8 (the verdict, appendix), Figure 24 (i), (ii), (iii) as three single graphs (the regions)
and Table 10 (what the labelled dataset cannot answer, printed in the Limitations chapter).

Ported from notebooks/_build/build_42.py (§3.2 and the Table 7 cell of build_41.py), build_44.py (§5.3, the closing
section) and build_43.py (the funding-weighted F share). Every frame is computed once per context and cached.
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import offset_copy

from lib import dominant_design, regional
from viz import flow, frames, plots, style

PERMS = 1000                                  # permutations behind the bands of conditions 2 and 3 (200 until supervisor review 2, 2026-10)
SET_LABEL = {"A0": "A (architecture)", "A1t": "A·W·T (architecture + wings + tilt)", "A0c": "A·U (architecture + propulsor units)",
             "family_b": "F (Lift + Cruise + CVT* family)"}
SET_TITLE = {"A0": "A\narchitecture", "A1t": "A·W·T\narchitecture + wings + tilt", "A0c": "A·U\narchitecture + propulsor units",
             "family_b": "F (exploratory, III.3)\nLift + Cruise + CVT*"}
MAIN_LEVELS = ("A0", "A1t", "A0c")                # the pre-specified sets drawn in Figure 12 (i) and (ii); F has its own figure
C1_FIRST_YEAR = 2016                              # the first priority year of the F conditions figure (condition 1 panel)
ABBR = {"North America": "NA", "Europe": "EU", "Asia-Pacific": "AP"}
NA, EU, AP = frames.REGIONS
REG_COL = {r: style.REGIONS[r][0] for r in frames.REGIONS}
WSH = {"<= 2011": "≤11", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23", "2024-26 (partial)": "24–26"}

pct1 = lambda x: f"{100 * x:.1f} %"                                        # noqa: E731  0.518 -> '51.8 %'
pval5 = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.05 else f"{p:.2f}"   # noqa: E731  the document's p
_signed = lambda x: f"{x:+.3f}".replace("-", "−")                            # noqa: E731  −0.047


# ------------------------------------------------------------------------------------------ the frames, once per context
_CACHE: dict = {}


def _data(ctx) -> dict:
    """Every frame the items and the numbers read, computed once per context (the permutations take a while)."""
    key = id(ctx)
    if key in _CACHE:
        return _CACHE[key]
    cfg, ds, v = ctx.cfg, ctx.ds, ctx.v
    frames.set_window_bounds(cfg)
    last = cfg.analysis["last_complete_year"]
    d = {}
    d["levels"] = frames.archetype_levels_table(ds, v, cfg)
    d["brief7"] = frames.archetype_levels_brief(ds, v, d["levels"])
    d["fy"] = frames.family_yearly(ds, v, last)
    d["dy"] = frames.dd_yearly(ds, v, last)
    d["bal"] = frames.dd_balance_table(ds, v, ctx.WIN_NAMES, cfg.analysis["rarefy_n"], PERMS, ctx.SEED)
    d["form"] = frames.dd_form_table(ds, v, ctx.WIN_NAMES, PERMS, ctx.SEED)
    d["lv"] = frames.dd_levels(d["dy"], d["bal"], d["form"], ctx.WIN_NAMES)
    d["ext"] = frames.ari_f_funding(ds, v, cfg)
    w = frames.regional_frame(ds, v)
    d["w"] = w
    d["ln"] = frames.region_lean(w)
    d["ts"] = frames.region_tests(w)
    d["mc"] = frames.region_mix_change(w)
    mprox, preg = frames.region_firm_proximity(v)
    d["preg"] = preg
    d["pairs"] = regional.region_pair_summary(mprox.to_numpy(), preg.to_numpy())
    d["px"] = regional.region_proximity_test(mprox.to_numpy(), preg.to_numpy())
    d["pub_n"] = len(frames.public_arch_frame(ds))
    d["trl_above"] = int(frames.trl_frame(ds)["trl"].gt(2).sum())
    _CACHE[key] = d
    return d


def _tp(d, measure: str, period: str, filers: str = "all filers") -> float:
    ts = d["ts"]
    return float(ts[(ts["measure"] == measure) & (ts["period"] == period) & (ts["filers"] == filers)]["p (chi-square, region)"].iloc[0])


# ------------------------------------------------------------------------------------------ A — the candidates
def tab_archetype_sets(ctx):
    """Table 7: the four archetype sets, over the whole corpus and all years."""
    b = _data(ctx)["brief7"]
    t = pd.DataFrame({"archetype set": b["level id"].map(SET_LABEL), "archetypes": b["archetypes"].astype(int),
                      "singletons": b["aircraft alone in their archetype"].astype(int),
                      "¹D": b["effective number ¹D"].map(lambda x: f"{x:.1f}"),
                      "largest archetype": b["largest archetype"], "its share": b["its share"].map(ctx.pct)})
    return t, None


# ------------------------------------------------------------------------------------------ B — the test
def fig_condition1_family(ctx):
    """Figure 11: F's share of the year's designs against the 50 % line; ALL designs is the main curve (rings on its years above 50 %),
    the actively protected designs a thin second curve (results freeze 2026-10-14: Analysis III reads all designs)."""
    d = _data(ctx)
    fy, cfg = d["fy"], ctx.cfg
    yrs = fy["priority year"].to_numpy()
    rd_all = fy["read, all"].to_numpy(bool)
    above = [int(y) for y, s_, r_ in zip(yrs, fy["F share"], rd_all) if r_ and s_ > 0.5]
    met = sorted(dominant_design.condition1_years(pd.DataFrame({"priority year": yrs, "read": fy["read, all"], "above 50 %": fy["F share"] > 0.5})))
    first_read = int(yrs[rd_all][0])
    fig, ax = plt.subplots(figsize=(ctx.W, 3.6), constrained_layout=True)
    plots.condition1_years(ax, yrs, fy["F share"], fy["F share in force"], fy["read, all"], fy["read, in force"], [], first_read,
                           f"few designs\n(under {cfg.analysis['trend_min_n']} a year): not tested")
    fa = fy.set_index("priority year")["F share"]
    for y in above:
        ax.plot(y, fa[y], "o", markersize=10.5, markerfacecolor="none", markeredgecolor=plots.MET, markeredgewidth=1.7, zorder=5)
        ax.annotate(pct1(fa[y]), (y, fa[y]), textcoords="offset points", xytext=(0, 10), ha="center", va="bottom", fontsize=7.5,
                    fontweight="bold", color=style.INK)
    if met:
        ax.text((met[0] + met[-1]) / 2, 0.975, f"condition 1 met: {met[0]}–{str(met[-1])[-2:]}", ha="center", va="top",
                fontsize=7.5, color=plots.MET, fontweight="bold", transform=ax.get_xaxis_transform())
    ax.text(yrs[-1] + 0.5, 0.505, "50 %", ha="right", va="bottom", fontsize=7.5)
    ax.set_ylabel("share of the year's designs in F\n(Separate Lift + Cruise +\nCombined Vectored Thrust*)")
    ax.set_xticks(yrs, [str(y) for y in yrs], fontsize=7)
    rows3 = [("all designs", fy["aircraft"]), ("actively protected", fy["aircraft in force"])]
    for r, (name, vals) in enumerate(rows3):
        tr_ = offset_copy(ax.get_xaxis_transform(), fig=fig, y=-(20 + 10 * r), units="points")
        ax.text(-0.012, 0, name, transform=offset_copy(ax.transAxes, fig=fig, y=-(20 + 10 * r), units="points"), ha="right", va="top",
                fontsize=7, color=style.MUTED)
        for y_, t_, rd in zip(yrs, vals, rd_all):
            ax.text(y_, 0, str(t_), transform=tr_, ha="center", va="top", fontsize=7, color=style.INK if rd else style.MUTED)
    for lab, rd in zip(ax.get_xticklabels(), rd_all):
        if not rd:
            lab.set_color(style.MUTED)
    ax.set_xlabel("priority year", labelpad=33)
    h = [Line2D([], [], color=style.INK, linewidth=1.7, marker="o", markersize=4.4, label="all designs of the year (main)"),
         Line2D([], [], color=style.MUTED, linewidth=1.2, linestyle="--", marker="s", markersize=4.2, markerfacecolor="white", label="actively protected designs"),
         Line2D([], [], marker="o", markersize=10, markerfacecolor="none", markeredgecolor=plots.MET, markeredgewidth=1.7, linestyle="none",
                label="year above 50 %")]
    fig.legend(handles=h, loc="outside lower center", ncol=3, fontsize=7.5, handlelength=2.2, columnspacing=1.2)
    return fig, fy


def fig_condition2_balance(ctx):
    """Figure 12 (i): ²D against its permutation band, one small multiple per pre-specified archetype set (A, A·W·T, A·U); F has its
    own figure (:func:`fig_family_conditions`, handoff 2026-10-15 Task 3)."""
    d = _data(ctx)
    bal, win = d["bal"], ctx.WIN_NAMES
    partial = [("partial" in w) for w in win]
    tk = [plots.WINDOW_TICKS[w] for w in win]
    fig, axs = plt.subplots(1, 3, figsize=(ctx.W, 3.0), constrained_layout=True)
    for ax, lvl in zip(axs, MAIN_LEVELS):
        s = bal[bal["level"] == lvl].set_index("window").reindex(win)
        metw = [bool(s.loc[w, "below band"]) and "partial" not in w for w in win]
        plots.balance_panel(ax, s.reset_index(), partial, metw, tk)
        ax.set_title(SET_TITLE[lvl], fontsize=7.5, loc="left")
    axs[0].set_ylabel("²D: large designs in play")
    for ax in axs:
        ax.set_xlabel("priority cohort", fontsize=7.5)
    fig.legend(handles=[Patch(facecolor="#dedcd8", label="permutation band (95 %)"),
                        Line2D([], [], color=style.INK, marker="o", markersize=3.6, linewidth=1.3, label=f"²D rarefied to {ctx.cfg.analysis['rarefy_n']} (95 % of the draws)"),
                        Line2D([], [], marker="o", markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle="none", label="below the band: condition met")],
               loc="outside lower center", ncol=2, fontsize=7.5, handlelength=1.6, columnspacing=1.2)
    return fig, bal[bal["level"].isin(MAIN_LEVELS)].reset_index(drop=True)


def fig_condition3_cohesion(ctx):
    """Figure 12 (ii): ΔQ against its permutation band under the main weighting (``frames.Q_WEIGHTINGS[0]``), one panel per pre-specified
    archetype set in the order of condition 2 (A, A·W·T, A·U; each drawn from its own rows of the form table); F has its own figure
    (:func:`fig_family_conditions`, handoff 2026-10-15 Task 3)."""
    d = _data(ctx)
    form, win = d["form"], ctx.WIN_NAMES
    partial = [("partial" in w) for w in win]
    main = frames.Q_WEIGHTINGS[0]
    fig, axb = plt.subplots(1, 3, figsize=(ctx.W, 3.4), constrained_layout=True, sharey=True)
    for ax, lvl in zip(axb, MAIN_LEVELS):
        s = form[form["level"] == lvl]
        sm = s[s["weighting"] == main].set_index("window").reindex(win).reset_index()
        plots.cohesion_panel(ax, sm, None, partial, [f"{ctx.WSHORT.get(w, '24–26*')}, n {int(n)}" for w, n in zip(win, sm["aircraft"])])
        ax.tick_params(axis="x", labelrotation=90)          # three panels: upright ticks ran into each other (as condition 2)
        ax.set_title(SET_TITLE[lvl], fontsize=7.5, loc="left")
    axb[0].set_ylabel("ΔQ: change in how unlike two aircraft\nare, against the two earliest cohorts")
    for ax in axb:
        ax.set_xlabel("priority cohort", fontsize=7.5)
    fig.legend(handles=[Patch(facecolor="#dedcd8", label="permutation band (95 %)"),
                        Line2D([], [], color=style.INK, marker="o", markersize=3.6, linewidth=1.5, label="ΔQ"),
                        Line2D([], [], marker="o", markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle="none", label="below the band: condition met")],
               loc="outside lower center", ncol=3, fontsize=7.5, handlelength=1.8, columnspacing=1.2)
    return fig, form[form["weighting"].eq(main) & form["level"].isin(MAIN_LEVELS)].reset_index(drop=True)


def _family_bases(ctx) -> dict:
    """The frames behind :func:`fig_family_conditions`: condition 2 of F on the actively protected designs (analysis3._base_frames, the
    numbers the verdict tables print), condition 3 of F on its three bases (analysis3.form_family, the table q7_condition3_family) and
    condition 1 on the granted-and-live designs (analysis3.granted_live). Cached on the context: the bands take a while."""
    if getattr(ctx, "_q7_family_bases", None) is not None:
        return ctx._q7_family_bases
    from viz import analysis3                                   # late import: analysis3 imports this module
    d = _data(ctx)
    out = {"bal_ap": analysis3._base_frames(ctx)["actively protected"][0], "ff": analysis3.form_family(ctx),
           "gl": analysis3.granted_live(ctx, d)["yearly"]}
    ctx._q7_family_bases = out
    return out


def fig_family_conditions(ctx):
    """The three conditions on F alone (handoff 2026-10-15 Task 3), one panel each: (a) condition 1, F's share per priority year from 2016
    on three bases (all designs solid, actively protected dashed, granted and live dotted; only the read years, 20 designs or more) against
    the 50 % line, the years above 50 % ringed on the main base; (b) condition 2, ²D of F per cohort on all designs against its
    permutation band (red where met) with the actively protected series in grey dashed (a hollow ring where met on that base);
    (c) condition 3, ΔQ of F under the main weighting, the same way. Returns the figure and a tidy table of every value drawn."""
    d, fb = _data(ctx), _family_bases(ctx)
    fy, bal, form, win = d["fy"], d["bal"], d["form"], ctx.WIN_NAMES
    main = frames.Q_WEIGHTINGS[0]
    partial = [("partial" in w) for w in win]
    tk = [plots.WINDOW_TICKS[w] for w in win]
    rows = []
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(ctx.W, 3.4), constrained_layout=True)
    # (a) condition 1: three bases, read years only
    f1 = fy[fy["priority year"] >= C1_FIRST_YEAR].reset_index(drop=True)
    gl = fb["gl"].set_index("priority year").reindex(f1["priority year"])
    yrs = f1["priority year"].astype(int).to_numpy()
    bases = [dict(base="all designs", share=f1["F share"], read=f1["read, all"], n=f1["aircraft"], k=f1["F aircraft"],
                  look=dict(color=style.INK, linestyle="-", markerfacecolor=style.INK), marker="o"),
             dict(base="actively protected", share=f1["F share in force"], read=f1["read, in force"], n=f1["aircraft in force"], k=f1["F aircraft in force"],
                  look=dict(plots.EXPLORE), marker="s"),
             dict(base="granted and live", share=gl["F share"].to_numpy(), read=gl["read"].to_numpy(bool), n=gl["aircraft"].to_numpy(), k=gl["F aircraft"].to_numpy(),
                  look=dict(plots.GRANTED), marker="^")]
    ring = [int(y) for y, sh, rd in zip(yrs, bases[0]["share"], bases[0]["read"]) if rd and sh > 0.5]
    plots.condition1_bases(ax1, yrs, bases, ring)
    fa = dict(zip(yrs, np.asarray(bases[0]["share"], dtype=float)))
    for y in ring:
        ax1.annotate(pct1(fa[y]), (y, fa[y]), textcoords="offset points", xytext=(0, 9), ha="center", va="bottom", fontsize=7.5,
                     fontweight="bold", color=style.INK)
    ax1.text(yrs[0] - 0.5, 0.505, "50 %", ha="left", va="bottom", fontsize=7.5)        # left end: the series are far below 50 % there
    ax1.set_xticks(yrs, [str(y) for y in yrs], rotation=90)
    ax1.set_ylabel("share of the year's designs in F")
    ax1.set_xlabel("priority year", fontsize=7.5)
    for b in bases:
        for y, sh, rd, n, k in zip(yrs, b["share"], b["read"], b["n"], b["k"]):
            rows.append(dict(panel="(a) condition 1", base=b["base"], x=str(int(y)), value=round(float(sh), 4), low=np.nan, high=np.nan,
                             whisker_low=np.nan, whisker_high=np.nan, drawn=bool(rd), met=bool(rd and sh > 0.5 and b["base"] == "all designs"),
                             n=int(n), F=int(k)))
    # (b) condition 2: all designs with its band, the actively protected designs dashed
    b_all = bal[bal["level"] == "family_b"].set_index("window").reindex(win).reset_index()
    b_ap = fb["bal_ap"][fb["bal_ap"]["level"] == "family_b"].set_index("window").reindex(win).reset_index()
    met_all = [bool(m) and not p for m, p in zip(b_all["below band"], partial)]
    met_ap = [bool(m) and not p for m, p in zip(b_ap["below band"], partial)]
    plots.band_series_panel(ax2, b_all, b_ap, partial, tk, "D2", "D2 permutation low", "D2 permutation high", whisk=("D2 low", "D2 high"),
                            main_met=met_all, alt_met=met_ap)
    ax2.set_ylim(0, float(np.nanmax(b_all[["D2 high", "D2 permutation high"]].to_numpy())) * 1.15)
    ax2.set_ylabel(f"²D of F, rarefied to {ctx.cfg.analysis['rarefy_n']}")
    ax2.set_xlabel("priority cohort", fontsize=7.5)
    for name, t, met in (("all designs", b_all, met_all), ("actively protected", b_ap, met_ap)):
        for i, w in enumerate(win):
            r = t.iloc[i]
            rows.append(dict(panel="(b) condition 2", base=name, x=w, value=round(float(r["D2"]), 4), low=round(float(r["D2 permutation low"]), 4),
                             high=round(float(r["D2 permutation high"]), 4), whisker_low=round(float(r["D2 low"]), 4), whisker_high=round(float(r["D2 high"]), 4),
                             drawn=True, met=met[i], n=int(r["aircraft"]), F=np.nan))
    # (c) condition 3: all designs (the F rows of the form table, main weighting) with its band, the actively protected designs dashed
    q_all = form[form["level"].eq("family_b") & form["weighting"].eq(main)].set_index("window").reindex(win).reset_index()
    ff = fb["ff"]
    q_ap = ff[ff["base"] == "actively protected"].set_index("cohort").reindex(win).reset_index()
    q_chk = ff[ff["base"] == "all designs"].set_index("cohort").reindex(win)
    if not np.allclose(q_chk["ΔQ"].to_numpy(float), q_all["ΔQ"].to_numpy(float), atol=5e-4):
        import warnings
        warnings.warn("fig_family_conditions: ΔQ of F on all designs differs between the form table and analysis3.form_family")
    met3_all = [bool(q < lo) and not p for q, lo, p in zip(q_all["ΔQ"], q_all["ΔQ permutation low"], partial)]
    met3_ap = [bool(q < lo) and not p for q, lo, p in zip(q_ap["ΔQ"], q_ap["ΔQ permutation low"], partial)]
    plots.band_series_panel(ax3, q_all, q_ap, partial, tk, "ΔQ", "ΔQ permutation low", "ΔQ permutation high", main_met=met3_all, alt_met=met3_ap,
                            zero_line=True)
    ax3.set_ylabel("ΔQ of F against the\ntwo earliest cohorts")
    ax3.set_xlabel("priority cohort", fontsize=7.5)
    for name, t, met, ncol in (("all designs", q_all, met3_all, "aircraft"), ("actively protected", q_ap, met3_ap, "designs")):
        for i, w in enumerate(win):
            r = t.iloc[i]
            rows.append(dict(panel="(c) condition 3", base=name, x=w, value=round(float(r["ΔQ"]), 4), low=round(float(r["ΔQ permutation low"]), 4),
                             high=round(float(r["ΔQ permutation high"]), 4), whisker_low=np.nan, whisker_high=np.nan, drawn=True, met=met[i],
                             n=int(r[ncol]), F=np.nan))
    for ax, ttl in zip((ax1, ax2, ax3), ("F, condition 1 (share)", "F, condition 2 (balance)", "F, condition 3 (disparity)")):
        ax.set_title(ttl, fontsize=7.5, loc="left")
    h = [Line2D([], [], color=style.INK, linewidth=1.7, marker="o", markersize=4.4, label="all designs (main base)"),
         Line2D([], [], linewidth=1.2, marker="s", markersize=4.2, **plots.EXPLORE, label="actively protected designs"),
         Line2D([], [], linewidth=1.2, marker="^", markersize=4.2, **plots.GRANTED, label="granted and live designs (condition 1)"),
         Patch(facecolor="#dedcd8", label="permutation band (95 %), all designs"),
         Line2D([], [], marker="o", markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle="none", label="condition met on all designs"),
         Line2D([], [], marker="o", markersize=8.5, markerfacecolor="none", markeredgecolor=plots.MET, markeredgewidth=1.4, linestyle="none",
                label="met on the actively protected designs")]
    fig.legend(handles=h, loc="outside lower center", ncol=3, fontsize=7.5, handlelength=2.0, columnspacing=1.2)
    data = pd.DataFrame(rows).rename(columns={"low": "band low", "high": "band high", "whisker_low": "whisker low", "whisker_high": "whisker high",
                                              "x": "year / cohort", "F": "F designs"})
    data["F designs"] = data["F designs"].astype("Int64")
    return fig, data


def _printed(cell: str) -> str:
    c = re.sub(r"(in force|all): no — ", r"\1: ✗ not met, ", cell)
    c = re.sub(r"(in force|all): met in", r"\1: ✓ met in", c)
    c = re.sub(r"^met in", "✓ met in", c)
    return "✗ not met" if c == "no" else c


def tab_verdict(ctx):
    """Table 8: the verdict per condition and archetype set (✓ met, ✗ not met, with the years or windows)."""
    lv = _data(ctx)["lv"].copy()
    lv["condition"] = lv["condition"].str.replace(" — ", ", ", n=1)
    lv["condition"] = (lv["condition"].str.replace("archetype", "architecture").str.replace("windows", "cohorts")
                       .str.replace("window", "cohort").str.replace("priority years", "priority years"))
    for c in lv.columns[1:]:
        lv[c] = lv[c].map(_printed)
    lv.columns = ["condition", "A", "A·W·T", "A·U", "F"]
    return lv, None


# ------------------------------------------------------------------------------------------ D — by region
def fig_region_family_share(ctx):
    """Figure 24 (i): each region's share of aircraft in F per window from 2012, with the chi-square p of the regional difference."""
    d = _data(ctx)
    ln = d["ln"]
    xw = np.arange(len(frames.CH5_WINS))
    fig, ax = plt.subplots(figsize=(ctx.HALF, 3.0), constrained_layout=True)
    ends = []
    for _, r in ln.iterrows():
        reg = r["region"]
        sty = style.REGIONS[reg]
        ys = np.array([r[f"F share {x}"] for x in frames.CH5_WINS])
        okw = np.array([r[f"F base {x}"] >= frames.CH5_THIN for x in frames.CH5_WINS])
        ax.plot(xw[okw], ys[okw], color=sty[0], linestyle=sty[2], marker=sty[1], markersize=4.6, linewidth=1.4, markeredgecolor="white",
                markeredgewidth=0.5, zorder=3)
        ends.append((ys[-1], reg))
    ends.sort()
    plots.end_labels(ax, xw[-1], [e[0] for e in ends], [f"{ABBR[e[1]]} {ctx.pct(e[0])}" for e in ends], [REG_COL[e[1]] for e in ends],
                     gap=0.05, dx_pt=6, fontsize=7.5)
    ax.set_xticks(xw, [f"{WSH[x]}\np {pval5(_tp(d, 'family F', x))}" for x in frames.CH5_WINS], fontsize=7)
    ax.set_xlim(-0.3, len(xw) - 0.3)
    ax.set_ylim(0, 0.7)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.set_xlabel("priority window\nχ² p: do the regions differ?", fontsize=7.5)
    ax.set_ylabel("share of aircraft in family F")
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    fig.legend(handles=[Line2D([], [], color=REG_COL[r], marker=style.REGIONS[r][1], linestyle=style.REGIONS[r][2], markersize=5,
                               label=f"{r} ({ABBR[r]})") for r in frames.REGIONS],
               loc="outside lower center", ncol=2, fontsize=7.5, handlelength=1.8, columnspacing=1.0)
    cols = ["region"] + [c for c in ln.columns if c.startswith("F ")]
    return fig, ln[cols]


def fig_region_lean_without_largest_filer(ctx):
    """Figure 24 (ii): the tilting and Tilt Propulsor share per region, North America also without its largest filer."""
    d = _data(ctx)
    ln, big = d["ln"], d["ts"].attrs["left_out"]
    groups = [("a propulsor\ntilts", "tilting share", "tilting share without it", "any tilting unit"),
              ("Tilt Propulsor", "Tilt Rotor share", "Tilt Rotor share without it", "Tilt Rotor")]
    bars = [(NA, False), (NA, True), (EU, False), (AP, False)]
    wbar = 0.21
    fig, ax = plt.subplots(figsize=(ctx.HALF, 3.1), constrained_layout=True)
    for g, (gname, c, c2, meas) in enumerate(groups):
        for b, (reg, wo) in enumerate(bars):
            r = ln[ln["region"] == reg].iloc[0]
            val = float(r[c2] if wo else r[c])
            xx = g + (b - 1.5) * wbar
            ax.bar(xx, val, wbar * 0.92, color="white" if wo else REG_COL[reg], hatch="////" if wo else plots.REGION_HATCH[reg],
                   edgecolor=REG_COL[reg], linewidth=1.0, zorder=3)
            ax.text(xx, val + 0.012, ctx.pct(val), ha="center", va="bottom", fontsize=7, rotation=90)
    short = big.split(" /")[0]
    ax.set_xticks(range(len(groups)), [f"{g[0]}\nχ² p {pval5(_tp(d, g[3], 'all years'))}\nw/o {short} {pval5(_tp(d, g[3], 'all years', f'without {big}'))}"
                                       for g in groups], fontsize=7)
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylim(0, 0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("share of the region's aircraft")
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    fig.legend(handles=[Patch(facecolor=REG_COL[r], hatch=plots.REGION_HATCH[r], edgecolor="white", label=f"{r} ({ABBR[r]})") for r in frames.REGIONS] +
               [Patch(facecolor="white", edgecolor=REG_COL[NA], hatch="////", label=f"North America without {big}")],
               loc="outside lower center", ncol=2, fontsize=7.5, handlelength=1.3, columnspacing=1.0)
    cols = ["region", "aircraft", "largest filer", "its aircraft", "its Tilt Rotor aircraft", "Tilt Rotor aircraft", "tilting share",
            "tilting share without it", "Tilt Rotor share", "Tilt Rotor share without it"]
    return fig, ln[cols]


def fig_region_firm_proximity(ctx):
    """Figure 24 (iii): the proximity of the firms' class profiles, within and across regions."""
    d = _data(ctx)
    pairs_, px = d["pairs"], d["px"]
    pr = pairs_.assign(_w=pairs_["within a region?"].eq("within")).sort_values(["_w", "mean"], ascending=[False, False]).reset_index(drop=True)
    ab = lambda s: " / ".join(ABBR.get(t.strip(), t.strip()) for t in str(s).split("/"))      # noqa: E731
    fig, ax = plt.subplots(figsize=(ctx.HALF, 3.1), constrained_layout=True)
    for k, r in pr.iterrows():
        colr = style.INK if r["_w"] else style.MUTED
        ax.hlines(k, r["lowest"], r["highest"], color=style.GRID, linewidth=2.6, zorder=2)
        ax.plot([r["mean"]], [k], marker="D" if r["_w"] else "o", markersize=5.5, color=colr, linestyle="none", zorder=3)
        ax.annotate(f"{r['mean']:.2f}", (r["mean"], k), xytext=(7, 0), textcoords="offset points", ha="left", va="center", fontsize=7.5, color=colr)
    ax.set_yticks(range(len(pr)), [f"{ab(p_)}\n{int(n_)} pairs" for p_, n_ in zip(pr["region pair"], pr["pairs"])], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15)
    ax.grid(axis="x", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    # base (2026-10-23): frames.region_firm_proximity, the named assignees with FIRM_MIN designs or more, every pair of them
    ax.set_xlabel(f"proximity of two assignees' architecture mixes\n(1 = same mix), assignees with {frames.FIRM_MIN}+ designs\n"
                  f"same region {px['same_mean']:.2f} · different {px['different_mean']:.2f} · p {pval5(px['p'])}",
                  fontsize=7.5)
    fig.legend(handles=[Line2D([], [], color=style.INK, marker="D", linestyle="none", markersize=5, label="firm pair within a region (mean)"),
                        Line2D([], [], color=style.MUTED, marker="o", linestyle="none", markersize=5, label="firm pair across regions (mean)")],
               loc="outside lower center", ncol=1, fontsize=7.5, handlelength=1.3, columnspacing=1.0)
    return fig, pairs_.drop(columns=[c for c in pairs_.columns if c.startswith("_")])


# ------------------------------------------------------------------------------------------ Limitations — Table 10
def _brief_table10(cfg) -> tuple:
    """The header and rows of the document's Table 10 (written text, the author's), as build_44 reads them."""
    lines = (Path(cfg.roots["reference"]) / "LABELLING_ANALYSIS_BRIEF.md").read_text(encoding="utf-8").splitlines()
    i1 = next(k for k, l in enumerate(lines) if l.startswith("**Table 10 —"))
    i2 = next(k for k, l in enumerate(lines) if k > i1 and l.startswith("**Also out of reach"))
    rows = []
    for l in lines[i1 + 1:i2]:
        if l.startswith("|"):
            rows.append([c.strip().replace("**", "") for c in l.strip().strip("|").split("|")])
    head, body = rows[0], [r for r in rows[1:] if not all(set(c) <= set(":-") for c in r)]
    return head, body


def tab_cannot_answer(ctx):
    """Table 10: the eight stakeholder questions the labelled dataset answers only in part or not at all, with the reason."""
    d = _data(ctx)
    head, body = _brief_table10(ctx.cfg)
    out = []
    for r in body:
        r = list(r)
        if r[0].startswith("Do filings lead or lag"):
            r[2] = r[2].replace("97", str(d["pub_n"])).replace("63", str(d["trl_above"]))
        out.append(r)
    t = pd.DataFrame(out, columns=head)
    assert len(t) == 8, len(t)
    return t, None


# ------------------------------------------------------------------------------------------ the items
def fig_method_flow(ctx):
    """How Q7 is answered: the aircraft in four archetype sets, the three conditions and the regional check, the figures, the answer."""
    nodes = [
        dict(id="data", kind="data", col=0, text="Unique aircraft in\nfour archetype sets"),
        dict(id="t_counts", kind="test", col=1, text="Share above half,\ntwo consecutive years"),
        dict(id="t_bands", kind="test", col=1, text="²D and ΔQ\nbelow shuffled bands"),
        dict(id="t_region", kind="test", col=1, text="Chi-square, region\nagainst F"),
        dict(id="f_cond", kind="figure", col=2, text="Condition 1 on F\nConditions 2 and 3"),
        dict(id="f_region", kind="figure", col=2, text="Family F share\nper region and window"),
        dict(id="ans", kind="answer", col=3, text="Answer to Q7"),
    ]
    edges = [("data", "t_counts"), ("data", "t_bands"), ("data", "t_region"), ("t_counts", "f_cond"),
             ("t_bands", "f_cond"), ("t_region", "f_region"), ("f_cond", "ans"), ("f_region", "ans")]
    return flow.chart(ctx.cfg, nodes, edges, aspect=0.55), None


ITEMS = [
    dict(name="q7_method_flow", slot="method", kind="figure", sub="",
         title="How Q7 is answered", caption="How Q7 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source="human labelling · PatSeer (priority date, legal status)", unit="", read=""),
    dict(name="q7_archetype_sets", slot="results", kind="table", sub="A", title="The four archetype sets",
         caption="The four archetype sets the test is run in: archetypes, singletons, the effective number ¹D and the largest archetype with its share, whole corpus, all years. F was defined after the first readings of the data.",
         source_item="Table 7", flag=None, flag_note="", builder=tab_archetype_sets,
         source="human labelling", unit="unique aircraft (627), each written once per archetype set, all years together", read=""),
    dict(name="q7_condition1_family", slot="results", kind="figure", sub="B", title="Condition 1 on F per priority year",
         caption="Condition 1 on F per priority year, as its share of the aircraft with a patent in force and of all aircraft against the 50 % line. The ringed years meet it.",
         source_item="Figure 11", flag=None, flag_note="", builder=fig_condition1_family,
         source="human labelling (class; the family F, defined after the first readings of the data) · PatSeer (priority date; legal status at the snapshot, 2026-06-08)",
         unit="unique aircraft by priority year, 2008-2023; F = every Lift + Cruise aircraft plus every CVT aircraft whose tilting propulsor set sits on a wing that does not tilt (CVT*); a year is read when its base holds 20 aircraft or more",
         read="Solid line, dots: F's share of the aircraft with at least one patent in force, the main base; dashed line, squares: F's share of every aircraft of the year. Condition 1 is met when the share is above 50 % in two consecutive read years (ringed, red band). Faded years hold fewer than 20 in-force aircraft and are not read. Under each year: the aircraft in force, all aircraft, and the share of the in-force aircraft whose patent is granted."),
    dict(name="q7_condition2_balance", slot="results", kind="figure", sub="B", title="Condition 2: ²D against its band",
         caption="Condition 2 per window in the three pre-specified archetype sets A, A·W·T and A·U (F is drawn in q7_family_conditions), ²D rarefied to 40 aircraft against the band of the same archetypes shuffled among the windows. A red point is below the band.",
         source_item="Figure 12 (i)", flag=None, flag_note="", builder=fig_condition2_balance,
         source="human labelling (class, wings, tilt, propulsor units) · PatSeer (priority date)",
         unit="unique aircraft per four-year priority window; 1000 permutations, seed 42; ²D rarefied to 40 aircraft (1000 draws); the partial window 2024-26 is hatched and not read",
         read="Dot: the window's ²D (how many large designs are in play) averaged over the rarefaction draws, whisker: the middle 95 % of the draws. Grey band: the middle 95 % of the ²D of the same archetypes shuffled among the windows at random, window sizes kept. A red dot is below the band: fewer designs in play than chance gives, condition 2 met."),
    dict(name="q7_condition3_cohesion", slot="results", kind="figure", sub="B", title="Condition 3: ΔQ against its band",
         caption="Condition 3 per window. ΔQ is the change in the average Gower distance between two aircraft against the two earliest windows, drawn under the one weighting of the form distance (w15): 15 dimensions of the codebook, each of its four systems weighing 1.",
         source_item="Figure 12 (ii)", flag=None, flag_note="", builder=fig_condition3_cohesion,
         source="human labelling (every field of the distance) · PatSeer (priority date)",
         unit="unique aircraft per four-year priority window; 1000 permutations, seed 42; A, A·U and F read the same aircraft, A·W·T leaves out the aircraft whose wings or tilt are not recorded",
         read="Q is the average Gower distance between two aircraft of the window (0 = alike on every design field, 1 = no field shared); ΔQ is the window's Q minus the average Q of the two earliest windows. Grey band: the middle 95 % of ΔQ when the aircraft are shuffled among the windows; a red dot is below it (condition 3 met). Weights (w15): 15 dimensions of the codebook, each of its four systems (G1, M1, M2, M3) weighing 1."),
    dict(name="q7_family_conditions", slot="results", kind="figure", sub="B", title="The three conditions on F",
         caption="The three conditions on F alone. (a) Condition 1: F's share of the year's designs from 2016 on all designs, the actively protected designs and the granted-and-live designs, read years only, against the 50 % line; the ringed years are above it on all designs. (b) Condition 2: ²D of F per cohort on all designs against its permutation band, the actively protected designs dashed. (c) Condition 3: ΔQ of F per cohort under the main weighting, the same way. A red point is below the band; a red ring marks the actively protected designs below their own band.",
         source_item="new (handoff 2026-10-15, Task 3)", flag=None, flag_note="", builder=fig_family_conditions,
         source="human labelling (class; the family F; every field of the form distance) · PatSeer (priority date; legal status at the snapshot, 2026-06-08)",
         unit="unique aircraft by priority year 2016-2023 (condition 1; a base is read when it holds 20 aircraft or more) and per four-year priority cohort (conditions 2 and 3; 1000 permutations, seed 42; the partial cohort 2024-26 is hatched and not read)",
         read="(a) Solid line, dots: F's share of all designs of the year; dashed, squares: of the actively protected designs; dotted, triangles: of the granted-and-live designs; a ring marks a year above 50 % on all designs. (b) Dot and whisker: ²D of F rarefied to 40 (middle 95 % of the draws) on all designs, grey band: the middle 95 % of ²D with the designs shuffled among the cohorts; dashed: the same on the actively protected designs (its band in the appendix table). (c) ΔQ: the cohort's mean form distance minus that of the two earliest cohorts, all designs with its band, the actively protected designs dashed. A red point is below the band (condition met); a red ring marks the actively protected designs below their own band."),
    dict(name="q7_verdict_table", slot="appendix", kind="table", sub="B", title="The dominant-design verdict",
         caption="The verdict per condition and archetype set, naming the priority years (condition 1) or windows (conditions 2 and 3) where each condition is met (✓) or not (✗); condition 1 on both bases, condition 3 under the main weighting.",
         source_item="Table 8", flag=None, flag_note="", builder=tab_verdict,
         source="human labelling · PatSeer (priority date; legal status at the snapshot, 2026-06-08)", unit="unique aircraft; the year (condition 1) or the complete four-year window (conditions 2 and 3)", read=""),
    dict(name="q7_region_family_share", slot="results", kind="figure", sub="D", title="Family F share per region and window",
         caption="Each region's share of aircraft in F per priority window from 2012, with the chi-square p of the regional difference under each window.",
         source_item="Figure 24 (i)", flag=None, flag_note="", builder=fig_region_family_share,
         source="PatSeer (applicant country, priority date) · human labelling",
         unit="unique aircraft of the three regions per priority window from 2012; a window under 10 aircraft of the region is not drawn",
         read="One line per region: its share of aircraft in the family F; under each window, the p of the chi-square test of region against F (a small p = the regions differ)."),
    dict(name="q7_region_lean_without_largest_filer", slot="appendix", kind="figure", sub="D", title="Tilting lean with and without the largest filer",
         caption="The share of each region's aircraft with a tilting propulsor and its Tilt Propulsor share, all years. The hatched bar is North America without its largest filer, Bell / Textron.",
         source_item="Figure 24 (ii)", flag=None, flag_note="", builder=fig_region_lean_without_largest_filer,
         source="PatSeer (applicant country, assignee) · human labelling", unit="unique aircraft of the three regions, all years",
         read="Per measure, the share of each region's aircraft; under each group the p of the chi-square test of region against the measure, with all filers and without Bell / Textron."),
    dict(name="q7_region_firm_proximity", slot="appendix", kind="figure", sub="D", title="Proximity of firms within and across regions",
         caption="The proximity of the class-share profiles of the 16 firms with 5 aircraft or more, by region pair, with the mean of the firm pairs (marker) and the lowest to the highest pair (bar).",
         source_item="Figure 24 (iii)", flag=None, flag_note="", builder=fig_region_firm_proximity,
         source="PatSeer (applicant country, assignee) · human labelling", unit="the firm pair; the 16 firms with 5 aircraft or more",
         read="One row per pair of regions (NA North America, EU Europe, AP Asia-Pacific); 1 = the two firms hold the same class mix, 0 = no class in common. Under the axis: the mean of same-region and of different-region pairs and the permutation p that the first is higher."),
    dict(name="q7_cannot_answer", slot="appendix", kind="table", sub="", title="What the labelled dataset cannot answer",
         caption="The eight stakeholder questions the labelled dataset answers only in part or not at all, with the reason. Printed in the Limitations chapter.",
         source_item="Table 10", flag="drop", flag_note="limitations table", builder=tab_cannot_answer,
         source="written by the author · the aircraft with a public counterpart (evtol.news) and above TRL 2 (NASA TRL table) computed here", unit="", read=""),
]


# ------------------------------------------------------------------------------------------ the numbers the text quotes
def numbers(ctx) -> dict:
    d = _data(ctx)
    cfg, pct, thin = ctx.cfg, ctx.pct, ctx.thin
    b7 = d["brief7"].set_index("level id")
    fy, dy, bal, form, ln, ext, px = d["fy"], d["dy"], d["bal"], d["form"], d["ln"], d["ext"], d["px"]
    fyi = fy.set_index("priority year")
    yrs = fy["priority year"].to_numpy()
    words = {6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    rest = dy[dy["read"] & dy["base"].eq("in force") & ~dy["level id"].eq("family_b")]
    topshare = lambda lvl: float(dy[(dy["level id"] == lvl) & (dy["base"] == "in force") & dy["read"]]["its share"].max())   # noqa: E731
    top3 = lambda sid: frames.archetype_key(ctx.v[ctx.v["window"] == "2020-23"], sid).value_counts(normalize=True).head(3).sum()  # noqa: E731
    b = bal.set_index(["level", "window"])
    q = form.set_index(["level", "weighting", "window"])
    main = frames.Q_WEIGHTINGS[0]
    status = pd.read_csv(cfg.path("grant_status_by_year"))
    pending = lambda y: f"{float(status.loc[status['priority_year'] == y, 'pending_pct'].iloc[0]):.1f} %"   # noqa: E731
    lni = ln.set_index("region")
    nar = lni.loc[NA]
    big = d["ts"].attrs["left_out"]
    mci = d["mc"].set_index(["region", "variable", "answer"])
    pri = d["pairs"].set_index("region pair")
    flags = frames.family_flags(ctx.ds, ctx.v)
    met = sorted(dominant_design.condition1_years(pd.DataFrame({"priority year": yrs, "read": fy["read, in force"], "above 50 %": fy["F share in force"] > 0.5})))
    n = {
        # windows and labels (so no typed window appears in the text)
        "w_last": "2020-23", "w_early": "2012-15", "w_mid": "2016-19", "w_first": "2012",
        "met_years": " and ".join(str(y) for y in met), "met_span": f"{met[0]}-{str(met[-1])[-2:]}" if met else "",
        "met_first": str(met[0]) if met else "", "met_last": str(met[-1]) if met else "",
        # A — Table 7
        "t7_c_arch": str(int(b7.loc["A0", "archetypes"])), "t7_cwt_arch": str(int(b7.loc["A1t", "archetypes"])),
        "t7_cu_arch": str(int(b7.loc["A0c", "archetypes"])), "t7_f_arch": str(int(b7.loc["family_b", "archetypes"])),
        "t7_c_d1": f"{b7.loc['A0', 'effective number ¹D']:.1f}", "t7_cwt_d1": f"{b7.loc['A1t', 'effective number ¹D']:.1f}",
        "t7_cu_d1": f"{b7.loc['A0c', 'effective number ¹D']:.1f}", "t7_f_d1": f"{b7.loc['family_b', 'effective number ¹D']:.1f}",
        "t7_f_share": pct(b7.loc["family_b", "its share"]), "t7_slc_share": pct(b7.loc["A0", "its share"]),
        "t7_cu_share": pct(b7.loc["A0c", "its share"]), "t7_cwt_share": pct(b7.loc["A1t", "its share"]),   # as Table 7 prints them
        "t7_f_n": thin(int(frames.family_mask(flags[flags["topType"].notna()]).sum())),
        "t7_cwt_largest": str(b7.loc["A1t", "largest archetype"]), "t7_cu_largest": str(b7.loc["A0c", "largest archetype"]),
        # B — condition 1
        "dd_year_min": str(cfg.analysis["trend_min_n"]), "dd_read_years": words[int(fy["read, in force"].sum())],
        "dd_first_read": str(int(yrs[fy["read, in force"].to_numpy()][0])), "dd_first_read_all": str(int(yrs[fy["read, all"].to_numpy()][0])),
        "dd_last_year": str(int(yrs[-1])), "dd_first_year": str(int(yrs[0])),
        "f_in_2020": pct1(fyi.loc[2020, "F share in force"]), "f_in_2021": pct1(fyi.loc[2021, "F share in force"]),
        "f_in_2022": pct1(fyi.loc[2022, "F share in force"]), "f_in_2023": pct1(fyi.loc[2023, "F share in force"]),
        "f_all_2020": pct1(fyi.loc[2020, "F share"]), "f_all_2021": pct1(fyi.loc[2021, "F share"]), "f_all_2022": pct1(fyi.loc[2022, "F share"]),
        "f_in_2020_k": f"{int(fyi.loc[2020, 'F aircraft in force'])} of {int(fyi.loc[2020, 'aircraft in force'])}",
        "f_in_2021_k": f"{int(fyi.loc[2021, 'F aircraft in force'])} of {int(fyi.loc[2021, 'aircraft in force'])}",
        "f_all_2020_k": f"{int(fyi.loc[2020, 'F aircraft'])} of {int(fyi.loc[2020, 'aircraft'])}",
        "gl_2020": pct(fyi.loc[2020, "in force with a granted patent"]), "gl_2021": pct(fyi.loc[2021, "in force with a granted patent"]),
        "gl_2022": pct(fyi.loc[2022, "in force with a granted patent"]), "gl_2023": pct(fyi.loc[2023, "in force with a granted patent"]),
        "f_gl_2020": pct(fyi.loc[2020, "F share, granted and live"]), "f_gl_2021": pct(fyi.loc[2021, "F share, granted and live"]),
        "lapse_2022": pending(2022), "lapse_2023": pending(2023),
        "max_rest": pct1(float(rest["its share"].max())), "max_c": pct1(topshare("A0")), "max_cwt": pct1(topshare("A1t")), "max_cu": pct1(topshare("A0c")),
        "max_c_year": str(int(rest[rest["level id"].eq("A0")].sort_values("its share").iloc[-1]["priority year"])),
        "max_c_arch": str(rest[rest["level id"].eq("A0")].sort_values("its share").iloc[-1]["largest archetype"]),
        # B — conditions 2 and 3
        "f_d2_last": f"{b.loc[('family_b', '2020-23'), 'D2']:.2f}", "f_d2_edge": f"{b.loc[('family_b', '2020-23'), 'D2 permutation low']:.2f}",
        "c_d2_last": f"{b.loc[('A0', '2020-23'), 'D2']:.2f}", "c_d2_edge": f"{b.loc[('A0', '2020-23'), 'D2 permutation low']:.2f}",
        "cu_d2_w1": f"{b.loc[('A0c', '<= 2011'), 'D2']:.2f}", "cu_d2_w1_edge": f"{b.loc[('A0c', '<= 2011'), 'D2 permutation low']:.2f}",
        "cu_d2_w2": f"{b.loc[('A0c', '2012-15'), 'D2']:.2f}", "cu_d2_w2_edge": f"{b.loc[('A0c', '2012-15'), 'D2 permutation low']:.2f}",
        "dq_main": _signed(q.loc[("A0", main, "2020-23"), "ΔQ"]), "dq_main_edge": _signed(q.loc[("A0", main, "2020-23"), "ΔQ permutation low"]),
        "top3_cwt": pct(top3("A1t")), "top3_cu": pct(top3("A0c")),
        "rarefy_n": str(cfg.analysis["rarefy_n"]), "perms": str(PERMS), "seed": str(ctx.SEED),
        # C — external comparison
        "ext_f_weighted": pct(ext.iloc[-1]["funding-weighted F share"]), "ext_f_corpus": pct(b7.loc["family_b", "its share"]),
        "ext_firms": str(int((ext["kind"] == "firm").sum())),
        # D — the regions
        "r_na_f_last": pct(lni.loc[NA, "F share 2020-23"]), "r_eu_f_last": pct(lni.loc[EU, "F share 2020-23"]), "r_ap_f_last": pct(lni.loc[AP, "F share 2020-23"]),
        "r_na_f_early": pct(lni.loc[NA, "F share 2012-15"]), "r_na_f_mid": pct(lni.loc[NA, "F share 2016-19"]),
        "r_p_f_early": pval5(_tp(d, "family F", "2012-15")), "r_p_f_mid": pval5(_tp(d, "family F", "2016-19")), "r_p_f_last": pval5(_tp(d, "family F", "2020-23")),
        "r_na_rho": f"{mci.loc[(NA, 'family F', 'True'), 'rho']:+.2f}", "r_na_rho_p": pval5(mci.loc[(NA, "family F", "True"), "p"]),
        "r_p_units_last": pval5(_tp(d, "propulsive-unit band", "2020-23")),
        "r_big": big, "r_big_n": str(int(nar["its aircraft"])), "r_na_n": str(int(nar["aircraft"])),
        "r_big_tr": str(int(nar["its Tilt Rotor aircraft"])), "r_na_tr": str(int(nar["Tilt Rotor aircraft"])),
        "r_na_tilt": pct(lni.loc[NA, "tilting share"]), "r_eu_tilt": pct(lni.loc[EU, "tilting share"]), "r_ap_tilt": pct(lni.loc[AP, "tilting share"]),
        "r_na_tilt_wo": pct(lni.loc[NA, "tilting share without it"]), "r_p_tilt_wo": pval5(_tp(d, "any tilting unit", "all years", f"without {big}")),
        "r_na_tp_wo": pct(lni.loc[NA, "Tilt Rotor share without it"]), "r_eu_tp": pct(lni.loc[EU, "Tilt Rotor share"]), "r_ap_tp": pct(lni.loc[AP, "Tilt Rotor share"]),
        "r_p_tp_wo": pval5(_tp(d, "Tilt Rotor", "all years", f"without {big}")),
        "r_p_tilt_all": pval5(_tp(d, "any tilting unit", "all years")), "r_p_tp_all": pval5(_tp(d, "Tilt Rotor", "all years")),
        "px_firms": str(len(d["preg"])), "px_firm_min": str(frames.FIRM_MIN), "px_same": f"{px['same_mean']:.2f}", "px_diff": f"{px['different_mean']:.2f}",
        "px_p": pval5(px["p"]), "px_eu": f"{pri.loc['Europe / Europe', 'mean']:.2f}",
        "px_na": f"{pri.loc['North America / North America', 'mean']:.2f}", "px_ap": f"{pri.loc['Asia-Pacific / Asia-Pacific', 'mean']:.2f}",
        # Limitations — Table 10
        "pub_n": str(d["pub_n"]), "trl_above": str(d["trl_above"]),
    }
    # the actively protected base read alone (sensitivity), and the all-designs maxima (results freeze 2026-10-14)
    from viz import analysis3                                   # late import: analysis3 imports this module
    det = analysis3.verdict_two_bases(ctx)[1].set_index(["base", "level"])
    ap, al = ("actively protected", "F"), ("all designs", "F")
    top_all = lambda lvl: float(dy[(dy["level id"] == lvl) & (dy["base"] == "all") & dy["read"]]["its share"].max())      # noqa: E731
    k20, n20 = int(fyi.loc[2020, "F aircraft"]), int(fyi.loc[2020, "aircraft"])
    n.update({
        "f_ap_d2": f"{det.loc[ap, '²D 2020-23']:.2f}", "f_ap_d2_edge": f"{det.loc[ap, '²D lower band edge 2020-23']:.2f}",
        "dq_ap": _signed(det.loc[ap, "ΔQ 2020-23"]), "dq_ap_edge": _signed(det.loc[ap, "ΔQ lower band edge 2020-23"]),
        "f_all_short": str(n20 // 2 + 1 - k20), "max_c_all": pct1(top_all("A0")),
        "dq_f_all": _signed(det.loc[al, "ΔQ 2020-23"]), "dq_f_all_edge": _signed(det.loc[al, "ΔQ lower band edge 2020-23"]),
    })
    return n
