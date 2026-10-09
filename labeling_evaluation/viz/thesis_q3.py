"""Thesis question Q3 — the regions: do the regions, and the firms within them, take different routes?

Items (one graph per file) ported from notebook 44 (build_44.py: Figures 21, 22, 23 (ii)) and notebook 43 (build_43.py: Figure 20);
the numbers the text quotes come from the same cells. See THESIS_CONTRACT.md §3 "Q3 regions".
"""
from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from lib import regional
from viz import flow, frames, plots, style

REGIONS = frames.REGIONS
NA, EU, AP = REGIONS
ABBR = {"North America": "NA", "Europe": "EU", "Asia-Pacific": "AP"}
WSH = {"<= 2011": "≤11", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23", "2024-26 (partial)": "24–26"}
CLASSES5 = list(frames.CH5_VARS["class"][1])                                    # SLC TR CVT TW MR other
CLS_WORD = {c: ("other classes" if c == "other" else "CVT" if c == "CVT" else style.cls(c).name) for c in CLASSES5}
CLS_STYLE = {c: (style.cls(c) if c != "other" else ("#e3e3e3", "||||")) for c in CLASSES5}
UNIT_ANS = list(frames.CH5_VARS["propulsive units"][1])
UNIT_STYLE = dict(zip(UNIT_ANS, [("#eeeeee", ""), ("#cfcfcf", "////"), ("#a8a8a8", "xxxx"), ("#7d7d7d", "\\\\\\\\"), ("#4a4a4a", "----")]))
TILT_STYLE = {True: ("#595959", ""), False: ("#e3e3e3", "....")}
#: the three variables of Figure 22: (frame variable, printed title, answers, styles, answer words)
VARS = [("class", "Architecture class", CLASSES5, CLS_STYLE, CLS_WORD),
        ("propulsive units", "Propulsor units", UNIT_ANS, UNIT_STYLE, {a: f"{a} units" for a in UNIT_ANS}),
        ("tilting unit", "Any propulsor that tilts", [True, False], TILT_STYLE, {True: "tilts", False: "none tilts"})]
SOURCE = "PatSeer (applicant country, priority date) · human labelling"

# the document's form of p (build_44): 3 decimals under 0.05, else 2
pval = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.05 else f"{p:.2f}"          # noqa: E731
yrs = lambda x: "0" if abs(x) == 0 else f"{x:+.1f}".replace(".0", "")                          # noqa: E731  +2, -1, +4.5
pct = lambda x: f"{x:.0%}".replace("%", " %")                                                  # noqa: E731


# ------------------------------------------------------------------------------------------ the frames, built once per ctx
_CACHE: dict = {}


def _frames(ctx) -> dict:
    """Every frame the Q3 items and numbers read, computed once per context (the bootstrap and the permutation test are slow)."""
    key = id(ctx)
    if key in _CACHE:
        return _CACHE[key]
    ds, v = ctx.ds, ctx.v
    w = frames.regional_frame(ds, v)
    region_n = v["region3"].value_counts().reindex(REGIONS + ["Other regions"]).fillna(0).astype(int)
    f = dict(w=w, region_n=region_n, rep_n=int(ds.patents["is_representative"].fillna(False).astype(bool).sum()),
             rc=frames.region_countries(ds, v), wm=frames.region_window_mix(w, ctx.WIN_NAMES), mc=frames.region_mix_change(w),
             ts=frames.region_tests(w), ry=frames.region_years(ds, v), rl=regional.region_lag(frames.with_publication(ds, v)))
    _, f["ll"] = regional.lead_lag(v, "region3")
    lf = regional.lag_frame(v, class_names=frames.LAG_CLASS_NAMES)
    f["off"] = regional.lag_offsets(lf)
    f["off16"] = regional.lag_offsets_since(v, class_names=frames.LAG_CLASS_NAMES)
    f["lc"] = regional.lag_constancy(lf, f["off"])
    f["pairs"] = frames.succession_pairs(v)
    f["succ"] = frames.succession_matrix(f["pairs"])
    _CACHE[key] = f
    return f


def _join(words: list) -> str:
    """'a', 'a and b', 'a, b and c'."""
    return "" if not words else words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def _lag_classes(off: pd.DataFrame) -> list:
    """The classes Figure 23 (ii) draws: 10 aircraft or more in every region, in the class order."""
    return [c for c in style.CLASS_ORDER if frames.LAG_CLASS_NAMES[c] in set(off["class"])
            and all(off[off["class"] == frames.LAG_CLASS_NAMES[c]]["aircraft"] >= 10)]


def _legend_handles(answers, sty, word) -> list:
    return [Patch(facecolor=(sty[a].color if hasattr(sty[a], "color") else sty[a][0]),
                  hatch=(sty[a].hatch if hasattr(sty[a], "hatch") else sty[a][1]), edgecolor="white", label=word[a]) for a in answers]


# ------------------------------------------------------------------------------------------ A: what each region files (Figure 22, all years)
def fig_region_design_all_years(ctx):
    """One axes: nine 100 % bars, a block per variable (class, propulsor units, tilting) and a bar per region, all years together."""
    f = _frames(ctx)
    w = f["w"]
    fig, ax = plt.subplots(figsize=(ctx.W, 4.3), constrained_layout=True)
    rows, pos, ticks, data = [], [], [], []
    y = 0.0
    blocks = []
    for var, title, answers, sty, word in VARS:
        col = frames.CH5_VARS[var][0]
        y0 = y
        for reg in REGIONS:
            s = w[w["region3"].eq(reg) & w[col].notna()]
            counts = pd.Series({a: int(s[col].eq(a).sum()) for a in answers})
            parts = counts.to_frame().T
            parts.columns = answers
            plots.stack_bars(ax, parts, sty, positions=[y], width=0.74, horizontal=True, min_label=0.10, fontsize=7)
            data.append(parts.assign(region=reg, variable=var, n=len(s)))
            pos.append(y); ticks.append(f"{reg} · {len(s)}"); y += 1.0
        blocks.append((title, y0, y - 1.0, answers, sty, word))
        y += 0.9
    for (title, ya, yb, answers, sty, word), loc in zip(blocks, ("outside right upper", "outside right center", "outside right lower")):
        ax.text(0.0, ya - 0.62, title, ha="left", va="bottom", fontsize=8.5, fontweight="bold", color=style.INK)
        fig.legend(handles=_legend_handles(answers, sty, word), loc=loc, title=title, title_fontsize=7.5, alignment="left",
                   fontsize=7.5, handlelength=1.3, frameon=False, ncol=1, labelspacing=0.35)
    ax.set_yticks(pos, ticks, fontsize=7.5)
    ax.invert_yaxis(); ax.set_ylim(pos[-1] + 0.6, -0.9)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.spines[["left", "top", "right"]].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("share of the region's aircraft, all years")
    ax.grid(axis="x", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    return fig, pd.concat(data, ignore_index=True)


# ------------------------------------------------------------------------------------------ B: when each region enters (Figure 23 ii)
def fig_region_entry_lag(ctx):
    """Years after North America, per class: the median priority-year difference with its 95 % bootstrap interval, Europe and Asia-Pacific."""
    f = _frames(ctx)
    off = f["off"]
    classes = _lag_classes(off)
    XMAX = 9.0
    fig, ax = plt.subplots(figsize=(ctx.W * 0.72, 3.1), constrained_layout=True)
    ypos = np.arange(len(classes))
    for dy, reg, side in ((-0.2, EU, 1), (0.2, AP, -1)):
        s = off[off["region"].eq(reg)].set_index("class").reindex([frames.LAG_CLASS_NAMES[c] for c in classes])
        o, lo, hi = s["offset vs North America (years)"].to_numpy(), s["95 % low"].to_numpy(), s["95 % high"].to_numpy()
        sty = style.REGIONS[reg]
        ax.hlines(ypos + dy, lo, np.minimum(hi, XMAX), color=sty[0], linewidth=1.4, zorder=3)
        ax.plot(o, ypos + dy, linestyle="none", marker=sty[1], markersize=5, color=sty[0], markeredgecolor="white", markeredgewidth=0.5,
                zorder=4, label=reg)
        for yy, oo, hh in zip(ypos + dy, o, hi):
            ax.annotate(yrs(oo), (oo, yy), xytext=(4 if abs(oo) < 1 else 0, 5 * side), textcoords="offset points", ha="center",
                        va="bottom" if side == 1 else "top", fontsize=7, color=style.INK,
                        bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85), zorder=6)
            if hh > XMAX:
                ax.annotate(f"to {yrs(hh)} →", (XMAX, yy), xytext=(-2, 2), textcoords="offset points", ha="right", va="bottom",
                            fontsize=7, color=sty[0])
    ax.axvline(0, color=style.REGIONS[NA][0], linewidth=1.2, zorder=2)
    na_med = off[off["region"].eq(NA)].set_index("class")["median priority year"]
    ax.set_yticks(ypos, [f"{CLS_WORD[c]}\nNA median {int(na_med[frames.LAG_CLASS_NAMES[c]])}" for c in classes], fontsize=7.5)
    ax.set_ylim(len(classes) - 0.3, -0.65); ax.set_xlim(-5, XMAX)
    ax.set_xlabel("years after North America, median difference")
    ax.grid(axis="x", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=7.5, handlelength=1.0)
    return fig, off[off["class"].isin([frames.LAG_CLASS_NAMES[c] for c in classes])].reset_index(drop=True)


# ------------------------------------------------------------------------------------------ appendix: Figure 22 per window, one variable per file
def _fig_mix_by_window(ctx, var: str):
    """The three region panels of one row of Figure 22: a 100 % bar per priority window (blank under CH5_THIN aircraft), the two
    answers with the smallest trend p over 2012-2023 above each panel (bold when detected)."""
    f = _frames(ctx)
    w, mc = f["w"], f["mc"]
    _, title, answers, sty, word = next(r for r in VARS if r[0] == var)
    col = frames.CH5_VARS[var][0]
    WIN_NAMES = ctx.WIN_NAMES
    pos = np.arange(len(WIN_NAMES), dtype=float)
    fig, axs = plt.subplots(1, 3, figsize=(ctx.W, 3.0), constrained_layout=True, sharey=True)
    data = []
    for ax, reg in zip(axs, REGIONS):
        s = w[w["region3"].eq(reg) & w[col].notna()]
        ns = [int(s["window"].eq(wn).sum()) for wn in WIN_NAMES]
        counts = [[int(s.loc[s["window"].eq(wn), col].eq(a).sum()) if n >= frames.CH5_THIN else 0 for a in answers] for wn, n in zip(WIN_NAMES, ns)]
        parts = pd.DataFrame(counts, columns=answers)
        data.append(parts.assign(region=reg, variable=var, window=WIN_NAMES, n=ns))
        plots.stack_bars(ax, parts, sty, positions=pos, width=0.8, partial=[0, len(pos) - 1], min_label=0.12, fontsize=7, no_label=[0, len(pos) - 1])
        ax.axvline((pos[0] + pos[1]) / 2, color=style.MUTED, linewidth=0.6, linestyle=":", zorder=4)
        for p_, n in zip(pos, ns):
            if n < frames.CH5_THIN:
                ax.text(p_, 0.5, f"n {n}", ha="center", va="center", fontsize=7, color=style.MUTED, rotation=90)
        ax.set_xticks(pos, [f"{WSH[wn]}\n{n}" for wn, n in zip(WIN_NAMES, ns)], fontsize=7)
        ax.set_ylim(0, 1); ax.set_xlim(-0.55, pos[-1] + 0.55); ax.set_yticks([])
        ax.spines[["left", "bottom"]].set_visible(False); ax.tick_params(length=0, pad=1.5)
        cand = mc[mc["region"].eq(reg) & mc["variable"].eq(var) & mc["answer"].ne("other")]
        cand = cand[cand["answer"].eq("True")] if var == "tilting unit" else cand
        cand = cand.dropna(subset=["p"]).sort_values("p").head(2)
        ax.annotate(reg, xy=(0, 1), xycoords="axes fraction", xytext=(0, 3 + len(cand) * 9.2), textcoords="offset points", ha="left", va="bottom",
                    fontsize=8.5, fontweight="bold", color=style.REGIONS[reg][0])
        for k, (_, r) in enumerate(cand.iloc[::-1].iterrows()):
            lab = "tilts" if var == "tilting unit" else (CLS_WORD[r["answer"]] if var == "class" else f"{r['answer']} units")
            sig = r["p"] < 0.05
            ax.annotate(f"{'▲' if r['rho'] > 0 else '▼'} {lab}: ρ {r['rho']:+.2f}, p {pval(r['p'])}".replace("ρ -", "ρ −"), xy=(0, 1),
                        xycoords="axes fraction", xytext=(0, 3 + 9.2 * k), textcoords="offset points", ha="left", va="bottom", fontsize=7,
                        fontweight="bold" if sig else None, color=style.INK if sig else style.MUTED)
    fig.legend(handles=_legend_handles(answers, sty, word), loc="outside lower center", ncol=min(len(answers), 6), fontsize=7.5,
               handlelength=1.3, columnspacing=1.0)
    return fig, pd.concat(data, ignore_index=True)


def fig_region_mix_by_window_class(ctx):
    return _fig_mix_by_window(ctx, "class")


def fig_region_mix_by_window_units(ctx):
    return _fig_mix_by_window(ctx, "propulsive units")


def fig_region_mix_by_window_tilting(ctx):
    return _fig_mix_by_window(ctx, "tilting unit")


# ------------------------------------------------------------------------------------------ appendix: Figure 21, the applicant countries
def fig_region_countries(ctx):
    """Patents acquired (pale) and representative patents (dark) per applicant country, the ten largest, with each country's unique aircraft."""
    f = _frames(ctx)
    rc = f["rc"]
    t = rc.iloc[::-1].reset_index(drop=True)
    REG_COL = {r: style.REGIONS[r][0] for r in REGIONS}
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    for i, r in t.iterrows():
        col = REG_COL.get(r["region"], style.OTHER.color if r["region"] == "" else "#8c8c8c")
        ax.barh(i, r["patents acquired"], 0.72, color=plots.tint(col, 0.3), edgecolor="white", linewidth=0.5, zorder=2)
        ax.barh(i, r["representative patents"], 0.72, color=col, hatch=plots.REGION_HATCH.get(r["region"], "xxxx"), edgecolor="white",
                linewidth=0.5, zorder=3)
        ax.text(r["patents acquired"] + 8, i,
                f"{int(r['representative patents'])} of {int(r['patents acquired'])} patents ({pct(r['share of representative patents'])}) · {int(r['unique aircraft'])} aircraft",
                va="center", ha="left", fontsize=7)
    labs = ["other countries or\nnot recorded" if c.startswith("other") else f"{frames.country_name(c)} · {ABBR.get(rg, 'other')}"
            for c, rg in zip(t["country"], t["region"])]
    ax.set_yticks(range(len(t)), labs, fontsize=7.5)
    ax.set_xlim(0, float(t["patents acquired"].max()) * 1.6)
    ax.set_xlabel("patents"); ax.tick_params(axis="y", length=0); ax.spines[["left"]].set_visible(False)
    ax.grid(axis="x", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(handles=[Patch(facecolor=REG_COL[r], hatch=plots.REGION_HATCH[r], edgecolor="white", label=f"{r} ({ABBR[r]})") for r in REGIONS] +
              [Patch(facecolor=plots.tint("#595959", 0.3), label="patents acquired (pale)"), Patch(facecolor="#595959", label="representative patents (dark)")],
              loc="center right", fontsize=7.5, handlelength=1.4)
    return fig, rc


# ------------------------------------------------------------------------------------------ appendix: Figure 20, within-firm successions
def fig_firm_successions(ctx):
    """Where a named firm's next aircraft lands, by the class of the one before; the boxed cell is the share that stays."""
    f = _frames(ctx)
    succ = f["succ"]
    dest = [("SLC", "Lift +\nCruise"), ("TR", "Tilt\nPropulsor"), ("CVT", "CVT"), ("TW", "Tilt\nWing"), ("MR", "Multi-\nrotor"),
            ("PTC", "Pitch-to-\nCruise"), ("other", "other")]
    M = succ[[f"→ {c}" for c, _ in dest]].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.4), constrained_layout=True)
    ax.imshow(M, cmap="Greys", vmin=0, vmax=0.8, aspect="auto")
    for i, r in succ.reset_index(drop=True).iterrows():
        for j, (c, _) in enumerate(dest):
            val = M[i, j]
            ax.text(j, i, f"{100 * val:.0f} %" if val > 0 else "–", ha="center", va="center", fontsize=7.5,
                    color="white" if val >= 0.4 else style.INK, fontweight="bold" if c == r["code"] else None)
            if c == r["code"]:
                ax.add_patch(matplotlib.patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=style.INK, linewidth=1.8, zorder=5,
                                                          clip_on=False))
    ax.set_xticks(range(len(dest)), [d[1] for d in dest], fontsize=7.5); ax.xaxis.tick_top()
    ax.set_yticks(range(len(succ)), [f"{'CVT' if c == 'CVT' else style.cls(c).name}\n{int(n)} successions · {int(k)} firms"
                                     for c, n, k in zip(succ["code"], succ["successions"], succ["firms"])], fontsize=7.5)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_ylabel("class of the firm's aircraft")
    ax.set_xlabel("class of the same firm's next aircraft"); ax.xaxis.set_label_position("top"); ax.xaxis.labelpad = 8
    return fig, succ


# ------------------------------------------------------------------------------------------ items
_WINDOW_NOTE = ("the index wrote 'Figure 21' here; the per-window panels of Figure 22 are these three (one variable each): "
                "decide whether they stay in the appendix")
def fig_method_flow(ctx):
    """How Q3 is answered: the data, the two paths (what each region files; when each region enters), the figures, the answer."""
    nodes = [
        dict(id="data", kind="data", col=0, text="Unique aircraft,\nthree regions"),
        dict(id="mix", kind="step", col=1, text="Class, units, tilting\nper region, window"),
        dict(id="lag", kind="step", col=1, text="Median priority year\nper class and region"),
        dict(id="t_mix", kind="test", col=2, text="Chi-square by region\nSpearman by window"),
        dict(id="t_lag", kind="test", col=2, text="Bootstrap interval\non each lag"),
        dict(id="figs", kind="figure", col=3, text="What each region files\nYears after North America"),
        dict(id="ans", kind="answer", col=4, text="Answer to Q3"),
    ]
    edges = [("data", "mix"), ("data", "lag"), ("mix", "t_mix"), ("lag", "t_lag"), ("t_mix", "figs"), ("t_lag", "figs"),
             ("figs", "ans")]
    return flow.chart(ctx.cfg, nodes, edges), None


ITEMS = [
    dict(name="q3_method_flow", slot="method", kind="figure", sub="",
         title="How Q3 is answered", caption="How Q3 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source=SOURCE, unit="", read=""),
    dict(name="q3_region_design_all_years", slot="results", kind="figure", sub="A",
         title="What each region files, all years", caption="The class, the propulsor-unit band and the tilting share of each region's aircraft, all years together; each bar is 100 % of the region's aircraft with the field recorded.",
         source_item="Figure 22 (all years bars)", flag=None, flag_note="", builder=fig_region_design_all_years,
         source=SOURCE, unit="unique aircraft of the three regions (n beside the region)",
         read="A bar is a share of one region's aircraft, not a count; a segment of 10 % or more prints its share."),
    dict(name="q3_region_entry_lag", slot="results", kind="figure", sub="B",
         title="Years after North America, per class", caption="The years by which Europe and Asia-Pacific file each class after North America, as the median priority-year difference with its 95 % bootstrap interval.",
         source_item="Figure 23 (ii)", flag="verify", builder=fig_region_entry_lag,
         flag_note=("verify: an interval touching 0 is read here as not detected (the 2016-onward Tilt Propulsor delay, 0 to +4); "
                    "the 45-page document calls that same interval detected"),
         source="PatSeer (applicant country, priority date) · human labelling",
         unit="unique aircraft of priority year 2023 or earlier; the five classes with 10 aircraft or more in every region",
         read="Dot: the region's median priority year minus North America's (+ = later); bar: its 95 % interval, one that excludes 0 is a difference detected; under the class, North America's median year."),
    dict(name="q3_region_mix_by_window_class", slot="appendix", kind="figure", sub="A",
         title="Class per region and window", caption="The class mix of each region's aircraft per priority window, with the two strongest trends over 2012-2023 above each panel.",
         source_item="Figure 22 (i), per-window bars", flag="decide", flag_note=_WINDOW_NOTE, builder=fig_region_mix_by_window_class,
         source=SOURCE, unit="unique aircraft per region and window (n under the bar); a window under 10 aircraft is blank",
         read="Each bar is 100 % of the window's aircraft; the first and last windows are faded (few aircraft, or not yet filled); bold above the panel = trend detected (p < 0.05)."),
    dict(name="q3_region_mix_by_window_units", slot="appendix", kind="figure", sub="A",
         title="Propulsor units per region and window", caption="The propulsor-unit band of each region's aircraft per priority window, with the two strongest trends over 2012-2023 above each panel.",
         source_item="Figure 22 (ii), per-window bars", flag="decide", flag_note=_WINDOW_NOTE, builder=fig_region_mix_by_window_units,
         source=SOURCE, unit="unique aircraft per region and window (n under the bar); a window under 10 aircraft is blank",
         read="Each bar is 100 % of the window's aircraft; the first and last windows are faded; bold above the panel = trend detected (p < 0.05)."),
    dict(name="q3_region_mix_by_window_tilting", slot="appendix", kind="figure", sub="A",
         title="Tilting share per region and window", caption="The share of each region's aircraft with a tilting propulsor per priority window, with the trend over 2012-2023 above each panel.",
         source_item="Figure 22 (iii), per-window bars", flag="decide", flag_note=_WINDOW_NOTE, builder=fig_region_mix_by_window_tilting,
         source=SOURCE, unit="unique aircraft per region and window (n under the bar); a window under 10 aircraft is blank",
         read="Each bar is 100 % of the window's aircraft; the first and last windows are faded; bold above the panel = trend detected (p < 0.05)."),
    dict(name="q3_region_countries", slot="appendix", kind="figure", sub="A",
         title="The applicant countries behind the regions", caption="Patents acquired (pale) and representative patents (dark) per applicant country, the ten largest, with each country's unique aircraft.",
         source_item="Figure 21", flag="decide", flag_note="appendix or drop: the base of the regions, not an answer to the question",
         builder=fig_region_countries, source="PatSeer (applicant country, priority date) · human labelling",
         unit="patents (acquired and representative) and unique aircraft; the ten countries with most representative patents, the rest in one row",
         read="One row per country of the first assignee, in the colour and hatch of its region; the label reads representative of acquired patents, the country's share of all representative patents, then its unique aircraft."),
    dict(name="q3_firm_successions", slot="appendix", kind="figure", sub="B",
         title="Where a firm's next aircraft lands", caption="Where a named firm's next aircraft lands, by the class of the one before; each row sums to 100 % and the boxed cell is the share that stays in the class.",
         source_item="Figure 20", flag=None, flag_note="", builder=fig_firm_successions,
         source="PatSeer (assignee, priority date) · human labelling",
         unit="the succession: a named firm's aircraft and the same firm's next aircraft in priority order; classes of origin with 10 successions or more",
         read="Darker is a larger share; – is none; under each class, its successions and the firms making them (a firm with many aircraft contributes many successions)."),
]


# ------------------------------------------------------------------------------------------ numbers
def numbers(ctx) -> dict:
    """Every number the Q3 text quotes, as printed."""
    f = _frames(ctx)
    thin, np_ = ctx.thin, ctx.np
    w, region_n, rc, wm, mc, ts, ry, rl, ll, off, off16, lc, succ, pairs = (f[k] for k in
        ("w", "region_n", "rc", "wm", "mc", "ts", "ry", "rl", "ll", "off", "off16", "lc", "succ", "pairs"))
    v = ctx.v
    wmi = wm.set_index(["region", "variable", "answer", "window"])
    mci = mc.set_index(["region", "variable", "answer"])
    sh = lambda reg, var, ans, win: wmi.loc[(reg, var, str(ans), win), "share"]                                     # noqa: E731
    allsh = lambda reg, var, ans: (wm[(wm["region"] == reg) & (wm["variable"] == var) & (wm["answer"] == str(ans))]["aircraft"].sum()
                                   / wm[(wm["region"] == reg) & (wm["variable"] == var) & (wm["answer"] == str(ans))]["base"].sum())  # noqa: E731
    pp = lambda reg, var, ans: pval(mci.loc[(reg, var, str(ans)), "p"])                                            # noqa: E731
    rho = lambda reg, var, ans: f"{mci.loc[(reg, var, str(ans)), 'rho']:+.2f}".replace("-", "−")                    # noqa: E731
    tp = lambda measure, period, filers="all filers": float(ts[(ts["measure"] == measure) & (ts["period"] == period)
                                                               & (ts["filers"] == filers)]["p (chi-square, region)"].iloc[0])  # noqa: E731
    OLD = ctx.WIN_NAMES[0]
    late = mc[mc["variable"] == "class"].groupby("answer")["aircraft 2020-23"].sum()
    rci = rc.set_index("country")
    rli, lli = rl.set_index("region"), ll.set_index("region3")
    offi, off16i = off.set_index(["class", "region"]), off16.set_index(["class", "region"])
    med16 = off16[off16["class"] == "all classes"].set_index("region")["median priority year"]
    mnames = {"US": "United States", "CN": "China", "DE": "Germany", "EP": "European Patent Office"}
    interval = lambda tab, c, reg: (f"{yrs(tab.loc[(frames.LAG_CLASS_NAMES[c], reg), 'offset vs North America (years)'])} "            # noqa: E731
                                    f"({yrs(tab.loc[(frames.LAG_CLASS_NAMES[c], reg), '95 % low'])} to {yrs(tab.loc[(frames.LAG_CLASS_NAMES[c], reg), '95 % high'])})")
    offset = lambda tab, c, reg: yrs(tab.loc[(frames.LAG_CLASS_NAMES[c], reg), "offset vs North America (years)"])                   # noqa: E731
    offp = lambda tab, c, reg: offset(tab, c, reg).lstrip("+")      # the offset in prose ("2 years after"); a lead keeps its sign  # noqa: E731
    detected = lambda tab, c, reg: not (tab.loc[(frames.LAG_CLASS_NAMES[c], reg), "95 % low"] <= 0 <= tab.loc[(frames.LAG_CLASS_NAMES[c], reg), "95 % high"])  # noqa: E731
    classes = _lag_classes(off)
    eu_zero = all(not detected(offi, c, EU) for c in classes)
    ap_old = [offi.loc[(frames.LAG_CLASS_NAMES[c], AP), "offset vs North America (years)"] for c in ("SLC", "TR", "TW")]
    ryi = ry.set_index(["priority year", "region"])
    peak = lambda reg: ry[(ry["region"] == reg) & (ry["priority year"] <= regional.LAST_COMPLETE)].sort_values("aircraft", ascending=False, kind="stable").iloc[0]  # noqa: E731
    si = succ.set_index("code")
    numw = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four"}
    a_, b_ = sorted((int(lli.loc[EU, "50 %"] - lli.loc[NA, "50 %"]), int(lli.loc[AP, "50 %"] - lli.loc[NA, "50 %"])))
    tilt_sh = [sh(NA, "tilting unit", "True", x) for x in frames.CH5_WINS]
    by_region = lambda reg: [frames.COUNTRY_NAMES[c] for c in rc[rc["region"] == reg].sort_values("unique aircraft", ascending=False)["country"] if c in frames.COUNTRY_NAMES]  # noqa: E731
    return {
        # the base of the chapter
        "all_n": thin(len(v)), "three_n": thin(len(w)), "three_share": pct(len(w) / len(v)), "other_n": str(int(region_n["Other regions"])),
        "na_n": str(int(region_n[NA])), "eu_n": str(int(region_n[EU])), "ap_n": str(int(region_n[AP])), "rep_n": thin(f["rep_n"]),
        "thin_n": str(frames.CH5_THIN), "trend_from": str(frames.CH5_TREND[0]), "trend_to": str(frames.CH5_TREND[1]),
        "last_complete": str(regional.LAST_COMPLETE), "lag_min_cell": str(regional.MIN_CELL), "lag_draws": thin(regional.DRAWS),
        "lag_since": str(regional.LAG_SINCE),
        "lag_perms": thin(lc.iloc[0]["permutations"]) if "permutations" in lc.columns else "5 000",
        "top3_rep_share": pct(rc["share of representative patents"].head(3).sum()), "us_rep_share": pct(rci.loc["US", "share of representative patents"]),
        "ap_top2": " and ".join(by_region(AP)[:2]), "eu_top3": ", ".join(by_region(EU)[:2]) + " and " + by_region(EU)[2],
        # A: all years together
        "na_tr_all": pct(allsh(NA, "class", "TR")), "na_slc_all": pct(allsh(NA, "class", "SLC")),
        "eu_slc_all": pct(allsh(EU, "class", "SLC")), "ap_slc_all": pct(allsh(AP, "class", "SLC")),
        "na_tilt_all": pct(allsh(NA, "tilting unit", True)), "eu_tilt_all": pct(allsh(EU, "tilting unit", True)), "ap_tilt_all": pct(allsh(AP, "tilting unit", True)),
        "p_class_all": pval(tp("class mix (five classes + other)", "all years")), "p_tilt_all": pval(tp("any tilting unit", "all years")),
        "p_units_all": pval(tp("propulsive-unit band", "all years")),
        "slc_2023_n": str(int(late["SLC"])), "cvt_2023_n": str(int(late["CVT"])), "tr_2023_n": str(int(late["TR"])),
        "na_slc_2023": pct(sh(NA, "class", "SLC", "2020-23")),
        # A: the trends from 2012
        "na_cvt_1215": pct(sh(NA, "class", "CVT", "2012-15")), "na_cvt_1619": pct(sh(NA, "class", "CVT", "2016-19")), "na_cvt_2023": pct(sh(NA, "class", "CVT", "2020-23")),
        "na_cvt_rho": rho(NA, "class", "CVT"), "na_cvt_p": pp(NA, "class", "CVT"),
        "na_tr_1215": pct(sh(NA, "class", "TR", "2012-15")), "na_tr_2023": pct(sh(NA, "class", "TR", "2020-23")), "na_tr_p": pp(NA, "class", "TR"),
        "na_tr_old": pct(sh(NA, "class", "TR", OLD)), "na_old_n": str(int(wmi.loc[(NA, "class", "TR", OLD), "base"])),
        "na_u13_1215": pct(sh(NA, "propulsive units", "1-3", "2012-15")), "na_u13_2023": pct(sh(NA, "propulsive units", "1-3", "2020-23")), "na_u13_p": pp(NA, "propulsive units", "1-3"),
        "na_u56_1215": pct(sh(NA, "propulsive units", "5-6", "2012-15")), "na_u56_2023": pct(sh(NA, "propulsive units", "5-6", "2020-23")), "na_u56_p": pp(NA, "propulsive units", "5-6"),
        "na_tilt_lo": pct(min(tilt_sh)), "na_tilt_hi": pct(max(tilt_sh)),
        "eu_slc_1215": pct(sh(EU, "class", "SLC", "2012-15")), "eu_slc_2023": pct(sh(EU, "class", "SLC", "2020-23")), "eu_slc_p": pp(EU, "class", "SLC"),
        "eu_cvt_2023": pct(sh(EU, "class", "CVT", "2020-23")), "eu_cvt_p": pp(EU, "class", "CVT"),
        "eu_u78_1215": pct(sh(EU, "propulsive units", "7-8", "2012-15")), "eu_u78_2023": pct(sh(EU, "propulsive units", "7-8", "2020-23")), "eu_u78_p": pp(EU, "propulsive units", "7-8"),
        "ap_1215_n": str(int(wmi.loc[(AP, "class", "SLC", "2012-15"), "base"])),
        "ap_slc_1619": pct(sh(AP, "class", "SLC", "2016-19")), "ap_slc_2023": pct(sh(AP, "class", "SLC", "2020-23")),
        "ap_u9_1619": pct(sh(AP, "propulsive units", "9+", "2016-19")), "ap_u9_2023": pct(sh(AP, "propulsive units", "9+", "2020-23")), "ap_u9_p": pp(AP, "propulsive units", "9+"),
        "ap_tilt_1619": pct(sh(AP, "tilting unit", "True", "2016-19")), "ap_tilt_2023": pct(sh(AP, "tilting unit", "True", "2020-23")),
        "p_units_1215": pval(tp("propulsive-unit band", "2012-15")), "p_units_1619": pval(tp("propulsive-unit band", "2016-19")), "p_units_2023": pval(tp("propulsive-unit band", "2020-23")),
        "p_class_2023": pval(tp("class mix (five classes + other)", "2020-23")),
        # B: medians, publication lag, lags per class
        "na_median": str(int(lli.loc[NA, "50 %"])), "eu_median": str(int(lli.loc[EU, "50 %"])), "ap_median": str(int(lli.loc[AP, "50 %"])),
        "follow_years": f"{numw.get(a_, a_)} and {numw.get(b_, b_)} years" if a_ != b_ else f"{numw.get(a_, a_)} years",
        "na_lag": str(int(rli.loc[NA, "median lag (years)"])), "ap_lag": str(int(rli.loc[AP, "median lag (years)"])),
        "na_office": mnames.get(rli.loc[NA, "main office"], rli.loc[NA, "main office"]), "ap_office": mnames.get(rli.loc[AP, "main office"], rli.loc[AP, "main office"]),
        "na_office_share": pct(rli.loc[NA, "its share"]), "ap_office_share": pct(rli.loc[AP, "its share"]),
        "lag_classes_n": str(len(classes)), "lag_classes_all": str(off["class"].nunique()),
        "ap_delay_range": f"{int(min(ap_old))}-{int(max(ap_old))}" if min(ap_old) != max(ap_old) else f"{int(min(ap_old))}",
        "ap_slc_lag": interval(offi, "SLC", AP), "ap_tr_lag": interval(offi, "TR", AP), "ap_tw_lag": interval(offi, "TW", AP), "ap_cvt_lag": interval(offi, "CVT", AP),
        "ap_slc_off": offp(offi, "SLC", AP), "ap_tr_off": offp(offi, "TR", AP), "ap_tw_off": offp(offi, "TW", AP), "ap_cvt_off": offp(offi, "CVT", AP),
        "na_cvt_median": str(int(offi.loc[(frames.LAG_CLASS_NAMES["CVT"], NA), "median priority year"])),
        "eu_cvt_lag": interval(offi, "CVT", EU), "eu_all_reach_zero": "every" if eu_zero else "not every",
        "lag_constancy_p": pval(lc.iloc[0]["p (permutation)"]),
        "na_median16": str(int(med16[NA])), "eu_median16": str(int(med16[EU])), "ap_median16": str(int(med16[AP])),
        "ap_tr_lag16": interval(off16i, "TR", AP), "ap_slc_lag16": interval(off16i, "SLC", AP), "ap_tw_lag16": interval(off16i, "TW", AP),
        "ap_tr_off16": offp(off16i, "TR", AP), "ap_slc_off16": offp(off16i, "SLC", AP), "ap_tw_off16": offp(off16i, "TW", AP),
        "ap_16_reach_zero": _join([CLS_WORD[c] for c in ("SLC", "TR", "TW") if not detected(off16i, c, AP)]) or "no class",
        "eu_cvt_off": offset(offi, "CVT", EU), "eu_cvt_off16": offset(off16i, "CVT", EU),
        "na_peak_year": str(int(peak(NA)["priority year"])), "na_peak_n": str(int(peak(NA)["aircraft"])),
        "eu_peak_year": str(int(peak(EU)["priority year"])), "eu_peak_n": str(int(peak(EU)["aircraft"])),
        "ap_peak_year": str(int(peak(AP)["priority year"])), "ap_peak_n": str(int(peak(AP)["aircraft"])),
        "na_share_2021": pct(ryi.loc[(2021, NA), "share of the year"]), "na_share_2023": pct(ryi.loc[(2023, NA), "share of the year"]),
        "na_share_2023_corr": pct(ryi.loc[(2023, NA), "share corrected for publication lag"]),
        # appendix: successions
        "succ_n": str(len(pairs)), "succ_firms": str(pairs["firm"].nunique()), "succ_min": str(frames.CH4_SUCC_MIN),
        "slc_stay": pct(si.loc["SLC", "stays in the class"]), "tr_stay": pct(si.loc["TR", "stays in the class"]), "cvt_stay": pct(si.loc["CVT", "stays in the class"]),
        "tw_stay": pct(si.loc["TW", "stays in the class"]), "tw_succ": str(int(si.loc["TW", "successions"])), "tw_firms": str(int(si.loc["TW", "firms"])),
        "tw_to_tr": pct(si.loc["TW", "→ TR"]), "tw_to_slc": pct(si.loc["TW", "→ SLC"]),
        "big_firm": str(succ.iloc[0]["firm left out"]), "big_succ": str(int(succ.iloc[0]["its successions, all classes"])),
    }
