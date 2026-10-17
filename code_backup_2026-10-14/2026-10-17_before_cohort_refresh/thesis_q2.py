"""Thesis question Q2 — the filers: who fills the field, and does anyone control it? (build_43 §4.1, §4.2)

One graph per file. Every panel of Figure 16 / 17 / 19 of the 45-page document becomes its own item; the numbers of
chapter 4 that the text quotes are recomputed here from the same frames (``viz.frames``) as notebook 43 uses.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from viz import flow, frames, plots, style

FT = ["Named company", "University / institute", "Individual inventor"]
FT_NAME = {"Named company": "named companies", "University / institute": "universities / institutes",
           "Individual inventor": "individual inventors"}
DOCCLS = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT", "TW": "Tilt Wing", "MR": "Multirotor", "other": "other classes"}
CODES19 = ["SLC", "TR", "CVT", "TW", "MR", "other"]
BAND = "ABCD"
BAND_TEXT = ["10 or more aircraft each", "5-9 aircraft each", "2-4 aircraft each", "1 aircraft each"]
#: the colours of the other Analysis V figures (q3_region_design_all_years, q7_region_family_share): the Okabe-Ito entries of
#: viz/style.py in their order there (style._CLASSES SLC, TR, CVT, TW = style.REGIONS NA, EU, AP + the fourth), given in that same order to
#: the assignee types of q2_filer_types and to the bands A-D of q2_largest_filers_share (2026-10-15; the greys of plots.FILER_STYLE
#: are kept for the other figures). The hatches are the ones of plots.FILER_STYLE, as the q3 figure keeps hatches beside its colours.
PALETTE = [style.cls(c).color for c in ("SLC", "TR", "CVT", "TW")]       # #0072B2, #E69F00, #009E73, #D55E00
FILER_STYLE = {"Named company": (PALETTE[0], ""), "University / institute": (PALETTE[1], "////"), "Individual inventor": (PALETTE[2], "....")}


# ------------------------------------------------------------------------------------------ shared frames (cached per ctx)
def _frames(ctx) -> dict:
    """The chapter-4 frames every builder and numbers() read, computed once per context."""
    if getattr(ctx, "_q2", None) is None:
        v = ctx.v
        d = {}
        d["fm"] = frames.filer_mix(v)
        d["fmr"] = frames.filer_mix_representative(ctx.ds)
        d["cov"] = frames.coverage_table(v)
        d["fw"] = frames.filers_by_window(v, ctx.WIN_NAMES)
        d["sizes"] = frames.firm_sizes(v)
        d["rated"] = set(frames.ari_firms(v, ctx.cfg)["company"])
        d["cb"] = frames.class_concentration_brief(v, ctx.COMPLETE)
        d["lev"] = frames.firm_leverage_table(v, ctx.WIN_NAMES)
        d["levc"] = frames.firm_leverage_classes(v, ctx.WIN_NAMES, lev=d["lev"])
        ent = frames.named_entries(v, ctx.WIN_NAMES)
        d["es"] = frames.entry_split(ent, ctx.COMPLETE, DOCCLS)
        d["et"] = frames.entry_split_test(ent, ctx.COMPLETE)
        d["twe"] = frames.tw_entry(v, ctx.COMPLETE)
        ctx._q2 = d
    return ctx._q2


def _who_short(s) -> str:
    return str(s).replace("an individual inventor's patent", "one inventor")


def _winlab(w: str) -> str:
    return "before 2012" if w == "<= 2011" else f"in {w}"


def _pval(p: float) -> str:
    """The document's form of a p value: three decimals under 0.05, two above."""
    return "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.05 else f"{p:.2f}"


# ------------------------------------------------------------------------------------------ A. who files
def fig_largest_filers_share(ctx):
    """Figure 16 (i): the named organisations ranked by unique aircraft and the cumulative share of the aircraft they hold."""
    d = _frames(ctx)
    sizes, cov, v = d["sizes"], d["cov"], ctx.v
    n_air = len(v)
    cum = (sizes.cumsum() / n_air).to_numpy()
    rank = np.arange(1, len(sizes) + 1)
    rated_rank = [i + 1 for i, f in enumerate(sizes.index) if f in d["rated"]]
    edges = [0] + cov["cumulative firms"].astype(int).tolist()
    fig, ax = plt.subplots(figsize=(ctx.W, 3.1), constrained_layout=True)
    for k in range(len(edges) - 1):                       # one pale band per size band A-D, in the palette order
        ax.axvspan(edges[k] + 0.5, edges[k + 1] + 0.5, color=plots.tint(PALETTE[k], 0.18), linewidth=0, zorder=0)
    ax.step(rank, cum, where="post", color=style.INK, linewidth=1.5, zorder=3)
    ax.plot(rated_rank, cum[np.array(rated_rank) - 1], linestyle="none", marker="D", markersize=4.6, markerfacecolor="white",
            markeredgecolor=style.INK, markeredgewidth=1.0, zorder=5)
    for k, (x0, x1) in enumerate(zip(edges[:-1], edges[1:])):
        ax.text((x0 + x1) / 2 + 0.5, 0.025, BAND[k], ha="center", va="bottom", fontsize=8, fontweight="bold", color=PALETTE[k])
        y1 = float(cum[x1 - 1])
        dx, dy, ha, va = [(4, -8, "left", "top"), (4, -8, "left", "top"), (-4, 6, "right", "bottom"), (-3, -8, "right", "top")][k]
        ax.annotate(ctx.pct(y1), (x1, y1), textcoords="offset points", xytext=(dx, dy), ha=ha, va=va, fontsize=8, fontweight="bold")
    share_named = float(sizes.sum() / n_air)
    ax.axhline(share_named, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=2)
    ax.text(len(sizes), share_named + 0.015, f"all {len(sizes)} named organisations: {int(sizes.sum())} aircraft, {ctx.pct(share_named)}",
            ha="right", va="bottom", fontsize=7.5)
    ax.axhline(1, color=style.GRID, linewidth=0.8, zorder=1)
    ax.text(len(sizes), 1.012, f"all {n_air} aircraft (individual inventors hold the rest)", ha="right", va="bottom", fontsize=7.5, color=style.MUTED)
    for k, r in cov.reset_index(drop=True).iterrows():
        ax.text(0.985, 0.40 - 0.085 * k, f"{BAND[k]}  {BAND_TEXT[k]}: {int(r['firms'])} firms · {int(r['aircraft'])} aircraft",
                transform=ax.transAxes, ha="right", va="top", fontsize=7.5, bbox=dict(fc="white", ec="none", pad=1.2))
    ax.legend(handles=[Line2D([], [], linestyle="none", marker="D", markersize=4.6, markerfacecolor="white", markeredgecolor=style.INK,
                              label=f"rated by the AAM Reality Index ({len(rated_rank)} firms)")],
              loc="upper left", fontsize=7.5, handletextpad=0.4, borderaxespad=0.3)
    ax.set_xlim(0, len(sizes) + 1); ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax.grid(axis="y", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.set_xlabel("named organisations ranked by unique aircraft, largest first")
    ax.set_ylabel(f"cumulative share of\nthe {n_air} aircraft")
    data = pd.DataFrame({"rank": rank, "firm": sizes.index, "unique aircraft": sizes.to_numpy(), "cumulative share": np.round(cum, 4),
                         "rated by the index": [f in d["rated"] for f in sizes.index]})
    return fig, data


def fig_filer_types(ctx):
    """Figure 16 (ii): the share of each filer type, all years (representative patents, then aircraft) and per priority window."""
    d = _frames(ctx)
    v, fmr = ctx.v, d["fmr"]
    win_counts = [v[v["window"] == w]["filer"].value_counts().reindex(FT).fillna(0) for w in ctx.WIN_NAMES]
    rep = fmr.set_index("filer")["representative patents"]
    parts = pd.DataFrame([[rep["Named companies"], rep["Universities and institutes"], rep["Individual inventors"]],
                          list(v["filer"].value_counts().reindex(FT).fillna(0))] + [list(c) for c in win_counts], columns=FT)
    pos = [0, 1] + [2.4 + k for k in range(len(ctx.WIN_NAMES))]
    parts_n = parts.sum(axis=1).astype(int).to_numpy()
    fig, ax = plt.subplots(figsize=(ctx.W * 0.66, 2.9), constrained_layout=True)
    plots.stack_bars(ax, parts, FILER_STYLE, positions=pos, width=0.72, partial=[len(parts) - 1], min_label=0.06)
    ax.axvline(1.7, color=style.MUTED, linewidth=0.8, linestyle=":")
    ax.set_xticks(pos, [f"{t}\nn {n}" for t, n in zip(["all, repr.\npatents", "all,\naircraft"] + [ctx.WSHORT[w] for w in ctx.WIN_NAMES], parts_n)], fontsize=7)
    ax.set_ylim(0, 1); ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax.set_ylabel("share")
    ax.spines[["bottom"]].set_visible(False); ax.tick_params(axis="x", length=0)
    fig.legend(handles=[Patch(facecolor=FILER_STYLE[k][0], hatch=FILER_STYLE[k][1], edgecolor="white", label=FT_NAME[k]) for k in FT],
               loc="outside lower center", ncol=3, fontsize=7.5, handlelength=1.4, columnspacing=1.0)
    data = parts.assign(bar=["all, repr. patents", "all, aircraft"] + ctx.WIN_NAMES, n=parts_n)
    return fig, data


def fig_first_vs_returning_filers(ctx):
    """Figure 16 (iii): the named organisations filing in each window, first-time and filing again."""
    d = _frames(ctx)
    fw = d["fw"]
    new, cont = fw["new firms"].to_numpy(), fw["continuing firms"].to_numpy()
    x = np.arange(len(fw))
    fig, ax = plt.subplots(figsize=(ctx.HALF, 2.7), constrained_layout=True)
    b1 = ax.bar(x, new, 0.66, color=plots.ENTRY_COLORS[0], edgecolor="white", linewidth=0.6, zorder=3)
    b2 = ax.bar(x, cont, 0.66, bottom=new, color=plots.ENTRY_COLORS[1], edgecolor="white", linewidth=0.6, zorder=3)
    for i, (p1, p2) in enumerate(zip(b1, b2)):
        if i == len(fw) - 1:
            for b in (p1, p2):
                b.set_alpha(0.5); b.set_hatch(style.PARTIAL_HATCH)
        ax.text(i, new[i] / 2, f"{new[i]}", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold", zorder=5)
        ax.text(i, new[i] + cont[i] + 2, f"+{cont[i]} again", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x, [ctx.WSHORT[w] for w in ctx.WIN_NAMES], fontsize=7)
    ax.set_xlim(-0.75, len(fw) - 0.3); ax.set_ylim(0, float((new + cont).max()) * 1.45); ax.set_ylabel("named organisations filing")
    ax.grid(axis="y", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(handles=[Patch(facecolor=plots.ENTRY_COLORS[0], label="first-time (number in the bar)"),
                       Patch(facecolor=plots.ENTRY_COLORS[1], label="filing again (above the bar)")],
              loc="upper left", fontsize=7.5, handlelength=1.2)
    return fig, fw[["window", "named firms active", "new firms", "continuing firms"]]


# ------------------------------------------------------------------------------------------ B. does anyone control it
def tab_largest_filer_per_class(ctx):
    """Figure 17 (i) as a table: per class of 20 aircraft or more, its largest filer over all years, the highest share one filer
    holds inside a single complete window, and the effective number of filers."""
    cb = _frames(ctx)["cb"]
    out = pd.DataFrame({
        "class": cb["class"],
        "aircraft": cb["aircraft"].astype(int),
        "filers": cb["filers"].astype(int),
        "effective filers": cb["effective filers"].map(lambda e: f"{e:.0f}"),
        "largest filer, all years": cb["largest filer"].map(_who_short),
        "its share": cb["its share"].map(ctx.pct),
        "highest share in one window": [f"{ctx.pct(s)} ({_who_short(h)}, {_winlab(w)})" for s, h, w in
                                         zip(cb["largest share inside one window"], cb["held by"], cb["in window"])],
    })
    return out, None


def fig_entrant_class_mix(ctx):
    """Figure 19 (i): the classes of the aircraft of first-time and returning filers in the two windows that can be tested."""
    d = _frames(ctx)
    es, et = d["es"], d["et"]
    tested = et[et["p"].notna()]
    style19 = {c: (style.cls(c) if c != "other" else ("#e3e3e3", "||||")) for c in CODES19}
    rows, labels, pos, notes = [], [], [], []
    y0 = 0.0
    for _, t in tested.iterrows():
        sub = es[es["window"] == t["window"]].set_index("group")
        for g, lab in (("first-time filers", "first-time"), ("returning filers", "returning")):
            rows.append(sub.loc[g, [DOCCLS[c] for c in CODES19]].astype(float).to_numpy())
            labels.append(f"{ctx.WSHORT[t['window']]} {lab}\n{int(sub.loc[g, 'aircraft'])} aircraft"); pos.append(y0); y0 += 1.0
        notes.append((y0 - 0.5 + 0.12, f"χ² p {_pval(t['p'])} · {t['largest returning firm']}: {int(t['its aircraft'])} of the {int(t['returning aircraft'])} returning aircraft"))
        y0 += 0.95
    parts = pd.DataFrame(rows, columns=CODES19)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.2), constrained_layout=True)
    plots.stack_bars(ax, parts, style19, positions=pos, width=0.8, horizontal=True, min_label=0.07, fontsize=7.5)
    for y, t in notes:
        ax.text(0.0, y, t, ha="left", va="top", fontsize=7.5, color=style.MUTED)
    ax.set_yticks(pos, labels, fontsize=7.5); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.set_ylim(pos[-1] + 1.05, -0.55)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax.spines[["left"]].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("share of the group's aircraft")
    fig.legend(handles=[Patch(facecolor=style19[c].color if hasattr(style19[c], "color") else style19[c][0],
                              hatch=style19[c].hatch if hasattr(style19[c], "hatch") else style19[c][1], edgecolor="white",
                              label=DOCCLS[c].replace("Tilt Rotor", "Tilt Propulsor")) for c in CODES19],
               loc="outside lower center", ncol=6, fontsize=7.5, handlelength=1.3, columnspacing=1.0)
    data = pd.concat([es.assign(panel="mix"), et.assign(panel="test")], ignore_index=True)
    return fig, data


def fig_tilt_wing_entrants(ctx):
    """Figure 19 (ii): Tilt Wing's share of the firms entering in each window beside its share of all the window's aircraft."""
    twe = _frames(ctx)["twe"]
    x = np.arange(len(twe))
    ea, aa = twe["Tilt Wing share of entrants"].to_numpy(), twe["Tilt Wing share of the aircraft"].to_numpy()
    tws = style.cls("TW")
    fig, ax = plt.subplots(figsize=(ctx.HALF, 2.9), constrained_layout=True)
    ax.bar(x - 0.19, aa, 0.36, color="#bdbdbd", edgecolor="white", linewidth=0.6, zorder=3)
    ax.bar(x + 0.19, ea, 0.36, color=tws.color, hatch=tws.hatch, edgecolor="white", linewidth=0.6, zorder=3)
    for i in range(len(x)):
        ax.text(x[i] + 0.19, ea[i] + 0.004, f"{100 * ea[i]:.0f} %\n{int(twe['entering with Tilt Wing'][i])} of\n{int(twe['firms entering'][i])}",
                ha="center", va="bottom", fontsize=7, linespacing=1.0)
        ax.text(x[i] - 0.19, aa[i] - 0.004, f"{100 * aa[i]:.0f} %", ha="center", va="top", fontsize=7, rotation=90)
    ax.set_xticks(x, [f"{ctx.WSHORT[w]}\n{int(a)}/{int(n)}" for w, a, n in zip(twe["window"], twe["Tilt Wing aircraft"], twe["aircraft in the window"])], fontsize=7)
    ax.set_ylim(0, float(max(ea.max(), aa.max())) + 0.07); ax.yaxis.set_major_locator(mticker.MultipleLocator(0.04))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.set_ylabel("Tilt Wing share")
    fig.legend(handles=[Patch(facecolor="#bdbdbd", label="share of all the window's aircraft"),
                        Patch(facecolor=tws.color, hatch=tws.hatch, edgecolor="white", label="share of the firms entering")],
               loc="outside lower center", ncol=1, fontsize=7.5, handlelength=1.3)
    return fig, twe


# ------------------------------------------------------------------------------------------ method flowchart
def fig_method_flow(ctx):
    """How Q2 is answered: the aircraft and their first assignee, the filer reading, the two tests, the figures, the answer."""
    n = len(ctx.v)
    nodes = [
        dict(id="data", text=f"{ctx.thin(n)} unique aircraft\nfirst assignee each", kind="data", col=0),
        dict(id="type", text="Type and fold\nthe filer names", kind="step", col=1),
        dict(id="cls", text="Largest share and\nremoval shift per class", kind="step", col=1),
        dict(id="test", text="Chi-square and\nFisher's exact", kind="test", col=2),
        dict(id="figA", text="Cumulative share ·\nFiler types", kind="figure", col=3),
        dict(id="figB", text="Largest filer per class ·\nFirst-time filer classes", kind="figure", col=3),
        dict(id="ans", text="Answer to Q2", kind="answer", col=4),
    ]
    edges = [("data", "type"), ("type", "cls"), ("type", "figA"), ("cls", "test"), ("cls", "figB"), ("test", "figB"),
             ("figA", "ans"), ("figB", "ans")]
    return flow.chart(ctx.cfg, nodes, edges), None


# ------------------------------------------------------------------------------------------ items
ITEMS = [
    dict(name="q2_method_flow", slot="method", kind="figure", sub="",
         title="How Q2 is answered",
         caption="How Q2 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source="", unit="", read=""),
    dict(name="q2_largest_filers_share", slot="results", kind="figure", sub="A",
         title="Cumulative share held by the largest filers",
         caption="The named organisations ranked by unique aircraft, largest first, and the cumulative share of the aircraft they hold, "
                 "cut into four bands; hollow diamonds are the firms the AAM Reality Index rates.",
         source_item="Figure 16 (i)", flag=None, flag_note="", builder=fig_largest_filers_share,
         source="PatSeer (assignee) · human labelling · AAM Reality Index (the firms it has rated)", unit="unique aircraft",
         read="The curve climbs by one firm at a time; the bands A to D cut it where firms hold 10 or more, 5-9, 2-4 and 1 aircraft each; "
              "the dashed line is the share all named organisations hold."),
    dict(name="q2_filer_types", slot="results", kind="figure", sub="A",
         title="Filer types, all years and per window",
         caption="The share of each filer type over all years, in representative patents and in aircraft, then per priority window in aircraft; "
                 "the window 2024-26 is still filling (faded).",
         source_item="Figure 16 (ii)", flag=None, flag_note="", builder=fig_filer_types,
         source="PatSeer (assignee, priority date) · human labelling", unit="unique aircraft; the first bar the representative patents",
         read="Each bar is 100 %; a segment of 6 % or more prints its share."),
    dict(name="q2_largest_filer_per_class", slot="results", kind="table", sub="B",
         title="Largest filer of each class",
         caption="The classes of 20 aircraft or more: filers, effective number of filers (1 / Σ sᵢ²), the largest filer over all years "
                 "and the highest share one filer holds inside a single priority window of 10 or more of the class's aircraft.",
         source_item="Figure 17 (i)", flag="decide",
         flag_note="Author decides: the table may be redundant with the text of B; keep one of the two in the main text.",
         builder=tab_largest_filer_per_class,
         source="PatSeer (assignee, priority date) · human labelling", unit="unique aircraft",
         read="The effective number of filers is how many equally sized filers would give the same concentration."),
    dict(name="q2_first_vs_returning_filers", slot="appendix", kind="figure", sub="B",
         title="First-time and returning organisations per window",
         caption="The named organisations filing in each priority window: filing for the first time (number inside the dark bar) "
                 "and filing again (above the bar); the window 2024-26 is still filling (faded).",
         source_item="Figure 16 (iii)", flag=None, flag_note="", builder=fig_first_vs_returning_filers,
         source="PatSeer (assignee, priority date) · human labelling", unit="the named organisation",
         read="Dark: organisations whose earliest aircraft in the corpus falls in the window; light: organisations that filed in an earlier window."),
    dict(name="q2_entrant_class_mix", slot="appendix", kind="figure", sub="B",
         title="Classes of first-time and returning filers",
         caption="The classes of the aircraft of first-time and returning named organisations in the two windows that can be tested, "
                 "with the chi-square p and the returning firm that holds most of the returning aircraft.",
         source_item="Figure 19 (i)", flag=None, flag_note="", builder=fig_entrant_class_mix,
         source="PatSeer (assignee, priority date) · human labelling",
         unit="unique aircraft of named organisations, in the windows where the returning group holds 20 aircraft or more",
         read="Each bar is 100 % of one group of aircraft; a segment of 7 % or more prints its share."),
    dict(name="q2_tilt_wing_entrants", slot="appendix", kind="figure", sub="B",
         title="Tilt Wing among the entering firms",
         caption="Tilt Wing's share of the firms entering in each window (hatched) beside its share of all the window's aircraft "
                 "(grey); the fraction under each window counts the Tilt Wing aircraft over all aircraft.",
         source_item="Figure 19 (ii)", flag=None, flag_note="", builder=fig_tilt_wing_entrants,
         source="PatSeer (assignee, priority date) · human labelling",
         unit="the named organisation (hatched), the unique aircraft (grey, individuals included)",
         read="A firm enters once, in the window of its first aircraft."),
]


# ------------------------------------------------------------------------------------------ numbers
def numbers(ctx) -> dict:
    """Every number the Q2 text quotes, as printed."""
    d = _frames(ctx)
    v, thin, pct = ctx.v, ctx.thin, ctx.pct
    fm, fmr, cov, fw, cb, lev, levc, es, et, twe = (d[k] for k in ("fm", "fmr", "cov", "fw", "cb", "lev", "levc", "es", "et", "twe"))
    fmi, fmri, fwi, cbi, eti, twi = (x.set_index(k) for x, k in ((fm, "filer"), (fmr, "filer"), (fw, "window"), (cb, "code"), (et, "window"), (twe, "window")))
    n = len(v)
    bell = lev.iloc[0]["firm"]
    bell_cls = levc[levc["firm"] == bell].set_index("class")
    second = lev.iloc[1]
    second_cls = levc[levc["firm"] == second["firm"]].set_index("class")
    second_cls_code = second["class most moved"]
    iw = lev["largest shift inside one window (pp)"].idxmax()
    big4 = cb.sort_values("aircraft", ascending=False).head(4)
    e16 = es[es["window"] == "2016-19"].set_index("group")
    tw23 = twi.loc["2020-23"]
    N = {
        # the dataset
        "n_aircraft": thin(n), "n_rep": thin(fmri.loc["all filers", "representative patents"]),
        "w1619": "2016-19", "w2023": "2020-23", "w1215": "2012-15",
        # who files
        "co_share": pct(fmi.loc["Named companies", "unique aircraft"] / n), "co_n": thin(fmi.loc["Named companies", "unique aircraft"]),
        "uni_share": pct(fmi.loc["Universities and institutes", "unique aircraft"] / n), "uni_n": thin(fmi.loc["Universities and institutes", "unique aircraft"]),
        "ind_share": pct(fmi.loc["Individual inventors", "unique aircraft"] / n), "ind_n": thin(fmi.loc["Individual inventors", "unique aircraft"]),
        "co_share_rep": pct(fmri.loc["Named companies", "share per representative patent"]),
        "ind_share_rep": pct(fmri.loc["Individual inventors", "share per representative patent"]),
        "ind_w1": pct(fwi.loc["<= 2011", "share individual inventors"]), "ind_w4": pct(fwi.loc["2020-23", "share individual inventors"]),
        "org_n": thin(cov.iloc[-1]["cumulative firms"]), "org_share": pct(cov.iloc[-1]["cumulative aircraft"] / n),
        "org_aircraft": thin(cov.iloc[-1]["cumulative aircraft"]),
        "top_n": thin(cov.iloc[0]["firms"]), "top_aircraft": thin(cov.iloc[0]["aircraft"]), "top_share": pct(cov.iloc[0]["aircraft"] / n),
        "next_n": thin(cov.iloc[1]["firms"]), "next_aircraft": thin(cov.iloc[1]["aircraft"]),
        "single_n": thin(cov.iloc[-1]["firms"]), "single_share_of_orgs": pct(cov.iloc[-1]["firms"] / cov.iloc[-1]["cumulative firms"]),
        "rated_n": thin(len(d["rated"] & set(d["sizes"].index))),
        "new_1619": thin(fwi.loc["2016-19", "new firms"]), "cont_1619": thin(fwi.loc["2016-19", "continuing firms"]),
        "new_2023": thin(fwi.loc["2020-23", "new firms"]), "cont_2023": thin(fwi.loc["2020-23", "continuing firms"]),
        # does anyone control it
        "class_min": str(frames.CH4_CLASS_MIN), "cell_min": str(frames.CH4_CELL_MIN), "conc_n": thin(len(cb)),
        "max_top_share": pct(cb["its share"].max()), "min_eff": f"{cb['effective filers'].min():.0f}",
        "big4_min_eff": f"{big4['effective filers'].min():.0f}", "slc_eff": f"{cbi.loc['SLC', 'effective filers']:.0f}",
        "tb_share": pct(cbi.loc["TB", "its share"]), "tr_share": pct(cbi.loc["TR", "its share"]), "cvt_share": pct(cbi.loc["CVT", "its share"]),
        "top_firm": bell, "top_firm_aircraft": thin(lev.iloc[0]["unique aircraft"]),
        "tr_win_share": pct(cbi.loc["TR", "largest share inside one window"]), "tr_win": cbi.loc["TR", "in window"],
        "slc_win_share": pct(cbi.loc["SLC", "largest share inside one window"]), "slc_win_n": thin(cbi.loc["SLC", "window aircraft"]),
        "lev_min_firm": str(frames.LEVERAGE_MIN_FIRM), "lev_min_window": str(frames.LEVERAGE_MIN_WINDOW),
        "lev1_pp": f"{lev.iloc[0]['shift magnitude (pp)']:.1f}", "lev1_class": frames.cls_name(lev.iloc[0]["class most moved"]),
        "lev2_pp": f"{second['shift magnitude (pp)']:.1f}", "lev2_firm": second["firm"], "lev2_class": frames.cls_name(second_cls_code),
        "lev_win_pp": f"{lev.loc[iw, 'largest shift inside one window (pp)']:.1f}", "lev_win_firm": lev.loc[iw, "firm"], "lev_win_window": lev.loc[iw, "that window"],
        "bell_tr_pp": f"{abs(bell_cls.loc['TR', 'shift all years (pp)']):.1f}", "bell_cvt_pp": f"{abs(bell_cls.loc['CVT', 'shift all years (pp)']):.1f}",
        "bell_tw_pp": f"{abs(bell_cls.loc['TW', 'shift all years (pp)']):.1f}", "bell_slc_n": thin(bell_cls.loc["SLC", "firm aircraft in the class"]),
        "lev2_in_class": thin(second_cls.loc[second_cls_code, "firm aircraft in the class"]), "lev2_aircraft": thin(second["unique aircraft"]),
        "lev2_win_pp": f"{second['largest shift inside one window (pp)']:.1f}", "lev2_win": second["that window"],
        "lev2_win_n": thin(second_cls.loc[second_cls_code, f"window aircraft {second['that window']}"]),
        # first-time against returning
        "test_min": str(frames.CH4_TEST_MIN),
        "first_1619": thin(eti.loc["2016-19", "first-time aircraft"]), "named_1619": thin(eti.loc["2016-19", "first-time aircraft"] + eti.loc["2016-19", "returning aircraft"]),
        "first_2023": thin(eti.loc["2020-23", "first-time aircraft"]), "named_2023": thin(eti.loc["2020-23", "first-time aircraft"] + eti.loc["2020-23", "returning aircraft"]),
        "first_share_1619": pct(eti.loc["2016-19", "first-time aircraft"] / (eti.loc["2016-19", "first-time aircraft"] + eti.loc["2016-19", "returning aircraft"])),
        "first_share_2023": pct(eti.loc["2020-23", "first-time aircraft"] / (eti.loc["2020-23", "first-time aircraft"] + eti.loc["2020-23", "returning aircraft"])),
        "p_1619": _pval(eti.loc["2016-19", "p"]), "p_2023": _pval(eti.loc["2020-23", "p"]),
        "p_wo_1619": _pval(eti.loc["2016-19", "p without it"]), "p_wo_2023": _pval(eti.loc["2020-23", "p without it"]),
        "big_1619": eti.loc["2016-19", "largest returning firm"], "big_ret_1619": thin(eti.loc["2016-19", "its aircraft"]), "ret_1619": thin(eti.loc["2016-19", "returning aircraft"]),
        "ret_tr_1619": pct(e16.loc["returning filers", "Tilt Rotor"]), "new_tr_1619": pct(e16.loc["first-time filers", "Tilt Rotor"]),
        "new_slc_1619": pct(e16.loc["first-time filers", "Lift + Cruise"]), "ret_slc_1619": pct(e16.loc["returning filers", "Lift + Cruise"]),
        # Tilt Wing entrants
        "tw_ent_1619": thin(twi.loc["2016-19", "entering with Tilt Wing"]), "ent_1619": thin(twi.loc["2016-19", "firms entering"]),
        "tw_ent_2023": thin(twi.loc["2020-23", "entering with Tilt Wing"]), "ent_2023": thin(twi.loc["2020-23", "firms entering"]),
        "tw_ent_share_1619": pct(twi.loc["2016-19", "Tilt Wing share of entrants"]), "tw_ent_share_2023": pct(twi.loc["2020-23", "Tilt Wing share of entrants"]),
        "tw_air_1619": pct(twi.loc["2016-19", "Tilt Wing share of the aircraft"]), "tw_air_2023": pct(twi.loc["2020-23", "Tilt Wing share of the aircraft"]),
        "tw_fisher_p": f"{tw23['Tilt Wing share, Fisher p against the window before']:.2f}",
        "tw_uni_2023": thin(tw23["Tilt Wing entrants: universities / institutes"]), "tw_single_2023": thin(tw23["Tilt Wing entrants: no other aircraft"]),
        "ent_uni_share_2023": pct(tw23["all entrants: universities / institutes"] / tw23["firms entering"]),
        "ent_single_share_2023": pct(tw23["all entrants: no other aircraft"] / tw23["firms entering"]),
        "tw_uni_share_2023": pct(tw23["Tilt Wing entrants: universities / institutes"] / tw23["entering with Tilt Wing"]),
        "tw_single_share_2023": pct(tw23["Tilt Wing entrants: no other aircraft"] / tw23["entering with Tilt Wing"]),
    }
    return {k: str(x) for k, x in N.items()}
