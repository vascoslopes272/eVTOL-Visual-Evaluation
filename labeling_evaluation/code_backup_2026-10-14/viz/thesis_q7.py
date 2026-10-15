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

PERMS = 200                                   # permutations behind the bands of conditions 2 and 3 (as the document)
SET_LABEL = {"A0": "A (architecture)", "A1t": "A·W·T (architecture + wings + tilt)", "A0c": "A·U (architecture + propulsor units)",
             "family_b": "F (Lift + Cruise + CVT* family)"}
SET_TITLE = {"A0": "A\narchitecture", "A1t": "A·W·T\narchitecture + wings + tilt", "A0c": "A·U\narchitecture + propulsor units",
             "family_b": "F\nLift + Cruise + CVT*"}
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
    """Figure 11: F's share of the year's aircraft on the two bases against the 50 % line."""
    d = _data(ctx)
    fy, cfg = d["fy"], ctx.cfg
    yrs = fy["priority year"].to_numpy()
    met = sorted(dominant_design.condition1_years(pd.DataFrame({"priority year": yrs, "read": fy["read, in force"],
                                                                "above 50 %": fy["F share in force"] > 0.5})))
    first_read = int(yrs[fy["read, in force"].to_numpy()][0])
    fig, ax = plt.subplots(figsize=(ctx.W, 3.6), constrained_layout=True)
    plots.condition1_years(ax, yrs, fy["F share in force"], fy["F share"], fy["read, in force"], fy["read, all"], met, first_read,
                           f"few aircraft in force\n(under {cfg.analysis['trend_min_n']} a year): not read")
    fi, fa = fy.set_index("priority year")["F share in force"], fy.set_index("priority year")["F share"]
    for k, y in enumerate(met):
        side = -1 if k == 0 else 1
        ax.annotate(pct1(fi[y]), (y, fi[y]), textcoords="offset points", xytext=(side * 9, 10), ha="right" if side < 0 else "left",
                    va="bottom", fontsize=7.5, fontweight="bold", color=style.INK)
        ax.annotate(f"all: {pct1(fa[y])}", (y, fa[y]), xytext=(y + 0.15, 0.33 if k == 0 else 0.24), textcoords="data", ha="center",
                    va="top", fontsize=7.5, color=style.MUTED,
                    arrowprops=dict(arrowstyle="-", color=style.MUTED, linewidth=0.5, shrinkA=1, shrinkB=4))
    if met:
        ax.text((met[0] + met[-1]) / 2, 0.975, f"condition 1 met,\nin force: {met[0]}–{str(met[-1])[-2:]}", ha="center", va="top",
                fontsize=7.5, color=plots.MET, fontweight="bold", transform=ax.get_xaxis_transform())
    ax.text(yrs[-1] + 0.5, 0.505, "50 %", ha="right", va="bottom", fontsize=7.5)
    ax.set_ylabel("share of the year's aircraft\nin F (Lift + Cruise + CVT*)")
    ax.set_xticks(yrs, [str(y) for y in yrs], fontsize=7)
    rows3 = [("aircraft in force", fy["aircraft in force"]), ("all aircraft", fy["aircraft"]),
             ("in force with a grant", fy["in force with a granted patent"].map(lambda g: "–" if not np.isfinite(g) else f"{100 * g:.0f}%"))]
    for r, (name, vals) in enumerate(rows3):
        tr_ = offset_copy(ax.get_xaxis_transform(), fig=fig, y=-(20 + 10 * r), units="points")
        ax.text(-0.012, 0, name, transform=offset_copy(ax.transAxes, fig=fig, y=-(20 + 10 * r), units="points"), ha="right", va="top",
                fontsize=7, color=style.MUTED)
        for y_, t_, rd in zip(yrs, vals, fy["read, in force"]):
            ax.text(y_, 0, str(t_), transform=tr_, ha="center", va="top", fontsize=7, color=style.INK if rd else style.MUTED)
    for lab, rd in zip(ax.get_xticklabels(), fy["read, in force"]):
        if not rd:
            lab.set_color(style.MUTED)
    ax.set_xlabel("priority year", labelpad=43)
    h = [Line2D([], [], color=style.INK, linewidth=1.7, marker="o", markersize=4.4, label="aircraft with a patent in force (main)"),
         Line2D([], [], color=style.MUTED, linewidth=1.2, linestyle="--", marker="s", markersize=4.2, markerfacecolor="white", label="all aircraft of the year"),
         Line2D([], [], marker="o", markersize=10, markerfacecolor="none", markeredgecolor=plots.MET, markeredgewidth=1.7, linestyle="none",
                label="two consecutive years above 50 %: met")]
    fig.legend(handles=h, loc="outside lower center", ncol=3, fontsize=7.5, handlelength=2.2, columnspacing=1.2)
    return fig, fy


def fig_condition2_balance(ctx):
    """Figure 12 (i): ²D against its permutation band, one small multiple per archetype set (one variable)."""
    d = _data(ctx)
    bal, win = d["bal"], ctx.WIN_NAMES
    partial = [("partial" in w) for w in win]
    tk = [plots.WINDOW_TICKS[w] for w in win]
    fig, axs = plt.subplots(1, 4, figsize=(ctx.W, 3.0), constrained_layout=True)
    for ax, lvl in zip(axs, frames.DD_LEVELS):
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
               loc="outside lower center", ncol=3, fontsize=7.5, handlelength=1.6, columnspacing=1.2)
    return fig, bal


def fig_condition3_cohesion(ctx):
    """Figure 12 (ii): ΔQ against its permutation band under the one weighting (every subsystem weighs the same)."""
    d = _data(ctx)
    form, win = d["form"], ctx.WIN_NAMES
    partial = [("partial" in w) for w in win]
    main = frames.Q_WEIGHTINGS[0]
    fig, axb = plt.subplots(1, 2, figsize=(ctx.W, 3.4), constrained_layout=True, sharey=True)
    for ax, lvl, ttl in zip(axb, ("A0", "A1t"), ("A, A·U and F (the same aircraft)", "A·W·T")):
        s = form[form["level"] == lvl]
        sm = s[s["weighting"] == main].set_index("window").reindex(win).reset_index()
        plots.cohesion_panel(ax, sm, None, partial, [f"{ctx.WSHORT.get(w, '24–26*')}\nn {int(n)}" for w, n in zip(win, sm["aircraft"])])
        ax.set_title(ttl, fontsize=7.5, loc="left")
    axb[0].set_ylabel("ΔQ: change in how unlike two aircraft\nare, against the two earliest cohorts")
    for ax in axb:
        ax.set_xlabel("priority cohort", fontsize=7.5)
    fig.legend(handles=[Patch(facecolor="#dedcd8", label="permutation band (95 %)"),
                        Line2D([], [], color=style.INK, marker="o", markersize=3.6, linewidth=1.5, label="ΔQ"),
                        Line2D([], [], marker="o", markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle="none", label="below the band: condition met")],
               loc="outside lower center", ncol=3, fontsize=7.5, handlelength=1.8, columnspacing=1.2)
    return fig, form[form["weighting"] == main]


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
    ax.set_xlabel(f"proximity (1 = same class mix)\nsame region {px['same_mean']:.2f} · different {px['different_mean']:.2f} · p {pval5(px['p'])}",
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
         caption="Condition 2 per window in the four archetype sets, ²D rarefied to 40 aircraft against the band of the same archetypes shuffled among the windows. A red point is below the band.",
         source_item="Figure 12 (i)", flag=None, flag_note="", builder=fig_condition2_balance,
         source="human labelling (class, wings, tilt, propulsor units) · PatSeer (priority date)",
         unit="unique aircraft per four-year priority window; 200 permutations, seed 42; ²D rarefied to 40 aircraft (300 draws); the partial window 2024-26 is hatched and not read",
         read="Dot: the window's ²D (how many large designs are in play) averaged over the rarefaction draws, whisker: the middle 95 % of the draws. Grey band: the middle 95 % of the ²D of the same archetypes shuffled among the windows at random, window sizes kept. A red dot is below the band: fewer designs in play than chance gives, condition 2 met."),
    dict(name="q7_condition3_cohesion", slot="results", kind="figure", sub="B", title="Condition 3: ΔQ against its band",
         caption="Condition 3 per window. ΔQ is the change in the average Gower distance between two aircraft against the two earliest windows, drawn under the main weighting (solid, grey band) and the check (dashed, dotted edges).",
         source_item="Figure 12 (ii)", flag=None, flag_note="", builder=fig_condition3_cohesion,
         source="human labelling (every field of the distance) · PatSeer (priority date)",
         unit="unique aircraft per four-year priority window; 200 permutations, seed 42; C, C·U and F read the same aircraft, C·W·T leaves out the aircraft whose wings or tilt are not recorded",
         read="Q is the average Gower distance between two aircraft of the window (0 = alike on every design field, 1 = no field shared); ΔQ is the window's Q minus the average Q of the two earliest windows. Grey band: the middle 95 % of ΔQ when the aircraft are shuffled among the windows; a red dot is below it (condition 3 met). Solid line and band: every subsystem weighs the same (the main weighting); dashed line and dotted edges: every field weighs the same (the check)."),
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
    return n
