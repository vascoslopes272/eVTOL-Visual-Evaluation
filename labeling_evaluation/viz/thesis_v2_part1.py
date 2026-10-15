"""Part I (Evidence base) figures, v2: reorganised, relabelled and simplified versions of a subset of the
Q1 / Q4 / Q5 thesis figures (THESIS_CONTRACT.md). Every number and every underlying computation is read
from viz/thesis_q1.py, thesis_q4.py, thesis_q5.py unchanged; this module only re-draws, re-labels and
re-groups them for thesis_figures_v2/Part_I_evidence_base/ (see its README.md). The originals in
thesis_figures/ are never touched.

Terminology (author's ruling, 2026-10-10): "unique aircraft" -> designs; "labelled dataset" -> patent
dataset; never "labelled / coded / coding / corpus"; class -> architecture; a combination of attributes ->
archetype; patents counted as patent families. Architecture short codes: TR already displays as TP (Tilt
Propulsor) in style.py; TB displays as TF (Tilt Frame) via the override below; SLC's short code is "SLC"
everywhere (never "L+C" / "LC").
"""
from __future__ import annotations

import dataclasses

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from viz import frames, style
from viz import thesis_q1 as q1
from viz import thesis_q4 as q4
from viz import thesis_q5 as q5

# --------------------------------------------------------------------------------------- terminology layer
ARCH_NAME_OVERRIDE = {"TB": "Tilt Frame", "MR": "Multicopter"}            # style.py has TB = "Tilt Body"; this document calls it Tilt Frame
ARCH_SHORT_OVERRIDE = {"TB": "TF", "SLC": "SLC"}      # style.py's SLC short code is "L+C"; never used here


def arch(code: str):
    """style.cls(code) with this document's TB -> Tilt Frame / TF override; everything else unchanged."""
    s = style.cls(code)
    return dataclasses.replace(s, name=ARCH_NAME_OVERRIDE.get(code, s.name), short=ARCH_SHORT_OVERRIDE.get(code, s.short))


#: the dissertation's text block is 16 cm wide; every Part I figure of the LaTeX is drawn at its final width and is at most 55 % as high
TEXT_W_IN = 16 / 2.54
MIN_PT = 7.0


def final_size(frac: float, height_frac: float = 0.55):
    """(width, height) in inches of a figure printed at ``frac`` of the text width; the height is ``height_frac`` of the width at most."""
    import math
    w = frac * TEXT_W_IN
    return w, math.floor(height_frac * w * 1000) / 1000


#: the dated sector events shown on the main-slot figure (assets/external/sector_events has 15; this is a
#: curated subset spanning the series: China's founding moment, the market-framing white paper, the first
#: certification basis, the pandemic, the SPAC financing wave, the first type certificate)
EVENTS_MAIN = ["2016-01-06", "2016-10-27", "2019-07-02", "2020-03-11", "2021-08-11", "2023-10-13"]


def _events_above(ax, events: pd.DataFrame, years: list, dates=EVENTS_MAIN, top: float = None, side_step: float = 0.6):
    """The dated sector events of ``dates``, drawn as small numbered markers along the top of the plot, each with a faint
    dotted line down to its year; the event names go in a numbered key under the figure (no rotated text).
    Events on the same year stand side by side. ``top``: the data y-value of the markers (defaults to 92 % of
    the y-limit). Returns the key text."""
    ev = events[events["date"].dt.strftime("%Y-%m-%d").isin(dates)].sort_values("date").reset_index(drop=True)
    lo, hi = ax.get_ylim()
    top = lo + (hi - lo) * 0.92 if top is None else top
    pos = {y: i for i, y in enumerate(years)}
    xs = np.array([pos[min(max(int(y), years[0]), years[-1])] for y in ev["year"]], dtype=float)
    for y in np.unique(xs):
        k = np.flatnonzero(xs == y)
        if len(k) > 1:
            xs[k] = y + (np.arange(len(k)) - (len(k) - 1) / 2) * side_step
    key = []
    for i, (x, label, yr) in enumerate(zip(xs, ev["event"], ev["year"]), 1):
        ax.plot([x, x], [lo, top], color=style.INK, linewidth=0.6, linestyle=(0, (1, 2)), zorder=1)
        ax.text(x, top, str(i), ha="center", va="center", fontsize=7, color="white", fontweight="bold", zorder=7,
                bbox=dict(boxstyle="circle,pad=0.25", fc=style.INK, ec="none"))
        key.append(f"{i}  {label} ({int(yr)})")
    return key


# ================================================================================== I1. patenting rate
def fig_filings_per_year_v2(ctx):
    """I1 main (final size, width 1.0): designs filed per priority year, stacked by the five architecture groups (the colours and
    hatches of q4_class_mix), the incomplete cohort 2024-26 faded, patent families as a grey line on its own right-hand axis, the
    dated sector events as numbered markers with an aligned key."""
    c = q1._calc(ctx)
    fpy = c["fpy"]
    regs = frames.REGIONS + ["Other regions"]
    t = fpy.loc[2005:, regs + ["patents representative", "complete"]].copy()
    t.loc[2005, regs + ["patents representative"]] = fpy.loc[:2005, regs + ["patents representative"]].sum()
    designs = t[regs].sum(axis=1)
    years = list(t.index)
    x = np.arange(len(years))
    partial = int(ctx.cfg.analysis["partial_window_start"])                     # 2024: the cohort 2024-26 is the incomplete one
    faded = [y >= partial for y in years]
    v = ctx.v.assign(_y=ctx.v["year"].clip(lower=2005).astype(int))
    stack = pd.crosstab(v["_y"], v["class5"]).reindex(index=years, columns=frames.CLASS5_ORDER, fill_value=0)
    stack["no architecture"] = designs.to_numpy() - stack.sum(axis=1).to_numpy()      # 2 designs have no architecture: kept so the bar equals the count
    events = frames.sector_events(ctx.cfg, fpy.attrs["snapshot"])
    n_rep = int(t["patents representative"].sum())
    ymax = float(designs.max())
    W, H = final_size(1.0, 0.54)

    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    bottom = np.zeros(len(years))
    for code in frames.CLASS5_ORDER + ["no architecture"]:
        vals = stack[code].to_numpy(dtype=float)
        if code == "no architecture":
            col, hatch = "#d9d9d9", ""
        else:
            sp = arch(GROUP_SPEC[code][0])
            col, hatch = sp.color, sp.hatch
        for i in range(len(years)):
            ax.bar(x[i], vals[i], 0.8, bottom=bottom[i], color=col, hatch=hatch, edgecolor="white", linewidth=0.3,
                   alpha=0.4 if faded[i] else 1.0, zorder=3)
        bottom = bottom + vals
    first_f = years.index(partial)
    ax.axvline(first_f - 0.5, color=style.INK, linewidth=0.8, linestyle="--", zorder=2)
    ax.text(first_f - 0.3, ymax * 0.97, "2024–26\nincomplete", va="top", ha="left", fontsize=MIN_PT, color=style.MUTED)
    ax.set_ylim(0, ymax * 1.3)
    ax.set_ylabel("designs filed")
    ax.set_xticks(x, [("≤2005" if y == 2005 else str(y)) for y in years], rotation=90)
    ax.set_xlim(-0.6, len(years) - 0.4)

    ax2 = ax.twinx()
    ax2.grid(False)
    ax2.plot(x, t["patents representative"].to_numpy(), color=style.MUTED, linewidth=1.3, marker="o", markersize=3, zorder=5)
    ax2.set_ylabel(f"patent families ({ctx.thin(n_rep)} total)", color=style.MUTED)
    ax2.tick_params(axis="y", colors=style.MUTED)
    ax2.set_ylim(0, float(t["patents representative"].max()) * 1.3)

    ev_key = _events_above(ax, events, years, top=ymax * 1.2)
    arch_h = [Patch(facecolor=arch(GROUP_SPEC[c_][0]).color, hatch=arch(GROUP_SPEC[c_][0]).hatch, edgecolor="white",
                    label=f"{GROUP_SPEC[c_][1]}  {GROUP_NAME[c_]}") for c_ in frames.CLASS5_ORDER]
    n_none = int(stack["no architecture"].sum())
    if n_none:
        arch_h.append(Patch(facecolor="#d9d9d9", edgecolor="white", label=f"no architecture read ({n_none} designs)"))
    ax.legend(handles=arch_h, loc="upper left", fontsize=MIN_PT, handlelength=1.3, borderaxespad=0.2, labelspacing=0.25)
    blank = [Line2D([], [], linestyle="none")] * len(ev_key)
    fig.legend(blank, ev_key, loc="outside lower center", ncol=3, fontsize=MIN_PT, handlelength=0, handletextpad=0,
               columnspacing=1.2, title="Sector events", title_fontsize=MIN_PT, alignment="left")
    data = stack.assign(**{"designs filed": designs.astype(int).to_numpy(), "patent families": t["patents representative"].astype(int).to_numpy(),
                           "cohort 2024-26 (faded)": faded})
    data.index.name = "priority year"
    return fig, data


def fig_growth_rates_v2(ctx):
    """I1 main (final size, width 1.0): each series relative to its own 2005-09 mean, log scale; no legend box, each series is named
    at the right end of its own line; the eVTOL series in colour, the three baselines in greys; 2024-26 shaded, never fitted."""
    import textwrap
    c = q1._calc(ctx)
    shown = ["evtol_families", "b64", "secb", "all"]
    colours = {"evtol_families": ("#0072B2", "-", "o", 1.8), "b64": ("#808080", "--", "s", 1.2),
               "secb": ("#a6a6a6", "-.", "^", 1.2), "all": ("#c9c9c9", ":", "v", 1.4)}
    first, last = 2005, 2023
    yrs = np.arange(first, last + 1)
    late_yrs = np.arange(last + 1, 2027)
    last_drawn = int(late_yrs[-1])
    W, H = final_size(1.0, 0.54)
    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    from viz import plots as _plots
    ax.axvspan(last + 0.5, last_drawn + 0.5, color=_plots.FEW_FILL, zorder=0, linewidth=0)
    ax.text((last + last_drawn + 1) / 2, 0.99, "2024–26\nincomplete", transform=ax.get_xaxis_transform(), ha="center", va="top",
            fontsize=MIN_PT, color=style.MUTED)
    top = 1.0
    ends = []
    legend_h, legend_l = [], []                                        # the six lines of the two series with segment fits
    for key in shown:
        col, ls, mk, lw = colours[key]
        cnt = c["ser"][key].reindex(yrs, fill_value=0).astype(float)
        base = float(cnt.loc[2005:2009].mean())
        ok = cnt.to_numpy() > 0
        b, a = np.polyfit(yrs[ok], np.log(cnt.to_numpy()[ok]), 1)
        ax.plot(yrs[ok], cnt.to_numpy()[ok] / base, ls="none", marker=mk, ms=3, color=col, alpha=0.55)
        line = np.exp(a + b * yrs) / base
        seg = c["seg"].get(key)                                        # eVTOL and B64: whole-period line thin, one thick line per segment
        hw, = ax.plot(yrs, line, ls=ls, lw=0.8 if seg else lw, color=col)
        if seg:
            tb = int(seg["turn"]["break"])
            short = "eVTOL" if key == "evtol_families" else "aeronautics (B64)"
            parts, ends_ = [], []
            for (name, (lo, hi, f)) in list(seg["lines"].items())[1:]:
                m = (yrs >= lo) & (yrs <= hi) & ok
                bb, aa = np.polyfit(yrs[m], np.log(cnt.to_numpy()[m]), 1)
                xs = np.arange(lo, hi + 1)
                h, = ax.plot(xs, np.exp(aa + bb * xs) / base, ls="-", lw=3.0 if key == "evtol_families" else 1.8, color=col, solid_capstyle="butt",
                             zorder=4 if key == "evtol_families" else 5)       # the two series share a slope before the break: eVTOL wide underneath, B64 narrow on top
                parts.append(h)
                ends_.append((xs[0], xs[-1], aa, bb))
            (_, x_end, a1, b1), (x_start, _, a2, b2) = ends_                         # the jump at the turning point: last fitted point of the first
            ax.plot([x_end, x_start], [np.exp(a1 + b1 * x_end) / base, np.exp(a2 + b2 * x_start) / base],      # segment to the first of the second, in black
                    ls="-", lw=1.3, color="black", zorder=7)
            legend_h += parts + [hw]
            legend_l += [f"{short}, before {tb}", f"{short}, after {tb}", f"{short}, 2005–23"]
        late = c["ser"][key].reindex(late_yrs).astype(float)          # 2024-26: drawn faded, never fitted or read
        okl = (late > 0).to_numpy()
        ax.plot(late_yrs[okl], late.to_numpy()[okl] / base, ls="none", marker=mk, ms=3, markerfacecolor="white", markeredgecolor=col, alpha=0.5)
        ends.append((float(line[-1]), "\n".join(textwrap.wrap(c["names"][key].replace(" (", "\n("), 24, break_long_words=False)).replace("\n\n", "\n"), col, key == "evtol_families"))
        top = max(top, float((cnt.to_numpy()[ok] / base).max()), float(line.max()))
    text_col = {"evtol_families": "#0072B2", "b64": "#5f5f5f", "secb": "#767676", "all": "#8a8a8a"}      # darker than the lines: legible in print
    for (y_end, label, col, bold), key in zip(ends, shown):
        ax.annotate(label, (last_drawn, y_end), xytext=(10, 0), textcoords="offset points", ha="left", va="center",
                    fontsize=MIN_PT, color=text_col[key], fontweight="bold" if bold else "normal", linespacing=1.05)
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    ax.set_yscale("log")
    ticks = [t for t in (0.25, 0.5, 1, 2, 4, 8, 16, 32) if t <= top * 1.6]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"×{x:g}"))
    ax.set_ylim(min(ticks) * 0.8, top * 1.5)
    ax.axhline(1, color=style.MUTED, linewidth=0.7, linestyle=":")
    legend_h.append(Line2D([], [], ls="-", lw=1.3, color="black"))
    legend_l.append("jump at the turning point")
    ax.legend(legend_h, legend_l, loc="upper left", fontsize=MIN_PT, ncol=2, frameon=False, handlelength=2.2, columnspacing=1.2, labelspacing=0.3,
              borderaxespad=0.2)
    ax.set_xlim(first - 0.6, last_drawn + 6.2)                      # room for the end-of-line names
    ax.set_xticks(range(2005, 2027, 3))
    ax.set_xlabel("priority year")
    ax.set_ylabel("growth since 2005–09 (log scale)")
    data = pd.DataFrame({c["names"][k]: c["ser"][k] for k in shown}).loc[2005:2026]
    data.index.name = "priority year"
    return fig, data


def _na_drop_common(ctx):
    c = q1._calc(ctx)
    ry, ll = c["ry"], c["ll"]
    REGIONS = frames.REGIONS
    tab = ry.pivot(index="priority year", columns="region", values="aircraft")[REGIONS]
    share = ry.pivot(index="priority year", columns="region", values="share of the year")[REGIONS]
    years = list(tab.index)
    from lib import regional
    incomplete = [y for y in years if y > regional.LAST_COMPLETE]
    ev_all = frames.sector_events(ctx.cfg, frames.snapshot_date(ctx.ds))
    events = ev_all[ev_all["date"].dt.strftime("%Y-%m-%d").isin(
        ["2016-10-27", "2019-07-02", "2021-08-11", "2023-10-13"])].reset_index(drop=True)
    return tab, share, years, incomplete, events, ll


def fig_na_drop_is_real_v2a(ctx):
    """I1 auxiliary, version A: same stacked bars as the original, but the rotated in-bar percentage labels are
    removed and North America's share is drawn as one line on its own right-hand axis instead."""
    from viz import plots
    tab, share, years, incomplete, events, ll = _na_drop_common(ctx)
    REGIONS = frames.REGIONS
    NA = REGIONS[0]
    med = ll.set_index("region3")["50 %"]
    fig, (a1, strip) = plt.subplots(2, 1, figsize=(ctx.W, 4.3), gridspec_kw=dict(height_ratios=[3.0, 1.35]),
                                     constrained_layout=True)
    plots.region_stack(a1, tab, incomplete=incomplete)
    first_inc = years.index(incomplete[0])
    a1.axvspan(first_inc - 0.5, len(years) - 0.3, color=plots.FEW_FILL, zorder=0, linewidth=0)
    a1.text(first_inc - 0.4, a1.get_ylim()[1] * 0.99, "not yet all\npublished", va="top", fontsize=7, color=style.MUTED)
    a1.set_xticks([])
    a1.set_ylabel("designs")
    h, _ = a1.get_legend_handles_labels()
    a1.legend(h, [f"{r} (median year {int(med[r])})" for r in REGIONS], loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3,
              fontsize=7, handlelength=1.2, columnspacing=1.0, borderaxespad=0.2)   # above the plot: the share line no longer crosses it
    a2 = a1.twinx()
    x = np.arange(len(years))
    reliable = [i for i, y in enumerate(years) if y not in incomplete]       # share is only read where n >= 8 (as the original)
    a2.plot([x[i] for i in reliable], [share[NA].iloc[i] for i in reliable], color=style.INK, linewidth=1.4,
            marker="o", markersize=3, zorder=6)
    a2.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    a2.set_ylabel(f"{NA} share\n(line, through {years[reliable[-1]]})", fontsize=mpl.rcParams["xtick.labelsize"])
    plots.event_strip(strip, events.assign(year=events["year"]), years, parent=a1)
    strip.set_xlim(a1.get_xlim())
    strip.set_xticks(range(len(years)), [str(y) for y in years], rotation=90, fontsize=7)
    return fig, tab.assign(**{f"{NA} share": share[NA]})


def fig_na_drop_is_real_v2b(ctx):
    """I1 auxiliary, version B: the bars are replaced entirely by North America's share of the year as one line."""
    from viz import plots
    tab, share, years, incomplete, events, ll = _na_drop_common(ctx)
    REGIONS = frames.REGIONS
    NA = REGIONS[0]
    fig, (a1, strip) = plt.subplots(2, 1, figsize=(ctx.W, 3.5), gridspec_kw=dict(height_ratios=[3.0, 1.35]),
                                     constrained_layout=True)
    x = np.arange(len(years))
    a1.plot(x, share[NA].to_numpy(), color=style.INK, linewidth=1.6, marker="o", markersize=3.5, zorder=6)
    a1.set_ylim(0, 1)
    first_inc = years.index(incomplete[0])
    a1.axvspan(first_inc - 0.5, len(years) - 0.3, color=plots.FEW_FILL, zorder=0, linewidth=0)
    a1.text(first_inc - 0.4, 0.98, "not yet all\npublished", va="top", fontsize=7, color=style.MUTED)
    a1.set_xticks([])
    a1.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    a1.set_ylabel(f"{NA} share\nof the year's designs")
    plots.event_strip(strip, events.assign(year=events["year"]), years, parent=a1)
    strip.set_xlim(a1.get_xlim())
    strip.set_xticks(range(len(years)), [str(y) for y in years], rotation=90, fontsize=7)
    return fig, tab.assign(**{f"{NA} share": share[NA]})


#: the firm names of the clock figure as printed (short, so the rows fit the 0.8 width); the full canonical names stay in the CSV
CLOCK_SHORT = {"Guangzhou Ehang Intelligent Technology": "EHang", "Ascendance Flight Technologies": "Ascendance",
               "Wofei / Geely Aviation": "Wofei / Geely"}


def fig_patent_vs_market_clock_v2(ctx):
    """I1 auxiliary (final size, width 0.8): the patent clock against the market clock, one row per index firm that files here: a bar
    from its first to its last patent, a tick at its peak filing year, a square at the first flight, a triangle at the entry into
    service the index states (open = a plan after the index release)."""
    tl = q4.ari_timeline(ctx)
    W, H = final_size(0.8, 0.55)
    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    y = np.arange(len(tl))
    planned_after = frames.ARI_RELEASE_YEAR - 1
    for yi, (_, r) in zip(y, tl.iterrows()):
        ax.plot([r["first patent"], r["last patent"]], [yi, yi], color="#9a9a9a", linewidth=4.0, solid_capstyle="butt", zorder=2)
        ax.plot(r["peak filing year"], yi, marker="|", markersize=8, markeredgewidth=1.5, color=style.INK, zorder=4)
        for col, mk in (("first flight (ARI)", "s"), ("entry into service (ARI)", "^")):
            if pd.notna(r[col]):
                plan = r[col] > planned_after
                ax.plot(r[col], yi, marker=mk, markersize=5, markerfacecolor="white" if plan else style.INK, markeredgecolor=style.INK,
                        markeredgewidth=0.9, linestyle="none", zorder=5)
    ax.set_yticks(y, [f"{CLOCK_SHORT.get(c, c)} ({int(n)})" for c, n in zip(tl["company"], tl["unique aircraft"])])
    ax.invert_yaxis()
    ax.axvline(2026.45, color=style.MUTED, linewidth=0.8, linestyle=":")
    ax.text(2026.6, len(tl) - 0.65, "mid-2026", fontsize=MIN_PT, color=style.MUTED, ha="left", va="center")
    ax.set_xlim(2012, 2031)
    ax.set_xticks(range(2012, 2031, 4))
    ax.grid(axis="x", color=style.GRID, linewidth=0.5)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    handles = [Line2D([], [], color="#9a9a9a", linewidth=4.0, label="first to last patent"),
               Line2D([], [], color=style.INK, marker="|", markersize=8, markeredgewidth=1.5, linestyle="none", label="peak filing year"),
               Line2D([], [], color=style.INK, marker="s", markersize=5, linestyle="none", label="first flight"),
               Line2D([], [], color="white", marker="s", markeredgecolor=style.INK, markersize=5, linestyle="none", label="first flight, planned"),
               Line2D([], [], color=style.INK, marker="^", markersize=5, linestyle="none", label="entry into service"),
               Line2D([], [], color="white", marker="^", markeredgecolor=style.INK, markersize=5, linestyle="none", label="entry into service, planned")]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, fontsize=MIN_PT, columnspacing=1.0, handlelength=1.4)
    return fig, tl.rename(columns={"unique aircraft": "designs"})


def _funding_panel_v2(ctx, col: str, ylab: str, ylim, frac: float = 0.6):
    """q5 Figure 18 redrawn at its final size (width 0.6), no title: funding (log) against ``col``; the Spearman statistics are in the
    CSV and the numbers file. Dot labels placed free of each other (placement is asserted)."""
    from viz import plots
    fund, tests = q5.funding(ctx)
    d = fund[fund["funding $M"].notna()]
    s_ = d[["company", "funding $M", col]].dropna()
    W, H = final_size(frac, 0.55)
    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    ax.scatter(s_["funding $M"], s_[col], s=16, color=style.INK, edgecolor="white", linewidth=0.4, zorder=4)
    ax.set_xscale("log")
    ax.set_xlim(35, 14000)
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x_, _p: f"{x_:,.0f}".replace(",", " ")))
    ax.set_xlabel("disclosed funding, US$ M (log)")
    ax.set_ylabel(ylab)
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.grid(axis="x", visible=True)
    ax.set_axisbelow(True)
    ax.set_ylim(*ylim)
    if col.startswith("years"):
        ax.axhline(0, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=2)
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(2))
    fig.canvas.draw()
    failed = plots.place_labels(ax, s_["funding $M"].to_numpy(), s_[col].to_numpy(), [{**q5.ARI_SHORT, **CLOCK_SHORT}.get(c_, c_) for c_ in s_["company"]],
                                [2.4] * len(s_), fontsize=MIN_PT)
    assert not failed, failed
    t = tests[tests["column"] == col].iloc[0]
    out = s_.reset_index(drop=True).rename(columns={"unique aircraft": "designs", "company": "firm"})
    out["spearman rho (all firms)"], out["p"], out["firms"] = round(float(t["rho"]), 3), round(float(t["p"]), 4), int(t["firms"])
    return fig, out


def fig_funding_vs_aircraft_v2(ctx):
    """I1 appendix (final size, width 0.6; leaves the dissertation text): disclosed funding against the firm's designs in the patent dataset."""
    return _funding_panel_v2(ctx, "unique aircraft", "designs in the\npatent dataset", (0.2, 9.3))


def fig_patenting_vs_investment_v2(ctx):
    """I1 appendix (final size, width 0.6; leaves the dissertation text): designs per priority year against disclosed sector investment
    per year, one dot per published period; read by eye, no test (the two trackers differ in scope)."""
    from viz import plots
    inv = q5.investment_by_period(ctx)
    W, H = final_size(0.6, 0.55)
    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    for _, r in inv.iterrows():
        ax.scatter(r["funding US$ bn per year"], r["unique aircraft per year"], s=26, zorder=4,
                   color=style.INK if r["complete"] else "white", edgecolor=style.INK, linewidth=0.9)
    ax.set_xscale("log")
    ax.set_xlim(0.2, 12)
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x_, _p: f"{x_:g}"))
    ax.xaxis.set_major_locator(mpl.ticker.FixedLocator([0.25, 0.5, 1, 2, 4, 8]))
    ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax.set_ylim(0, 85)
    ax.set_xlabel("disclosed sector investment, US$ bn per year (log)")
    ax.set_ylabel("designs per\npriority year")
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.grid(axis="x", visible=True)
    ax.set_axisbelow(True)
    ax.text(0.99, 0.03, "open dot: year still filling\n* January to August, not annualised", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=MIN_PT, color=style.MUTED)
    fig.canvas.draw()
    failed = plots.place_labels(ax, inv["funding US$ bn per year"].to_numpy(), inv["unique aircraft per year"].to_numpy(),
                                [q5.FUND_SHORT[p_] for p_ in inv["period"]], [3.2] * len(inv), fontsize=MIN_PT)
    assert not failed, failed
    return fig, inv.rename(columns={"unique aircraft": "designs", "unique aircraft per year": "designs per year"})


def tab_growth_rates_table_v2(ctx):
    """I1 appendix: doubling times against the baselines; series renamed to 'designs' (never 'aircraft' as a
    counted unit). The count column stays neutral ('count'): every row counts patent families except the
    eVTOL unique-designs row, which counts designs (as the original table's unit note already said)."""
    df, _ = q1.tab_growth_rates(ctx)
    df = df.rename(columns={"families 2005-2023": "count 2005-2023"})
    df["series"] = df["series"].replace({"eVTOL unique aircraft": "eVTOL unique designs"})
    return df, None


def tab_ari_timeline_v2(ctx):
    """I1 auxiliary: the AAM Reality Index timing table, unchanged other than terminology."""
    from viz import thesis_q5 as q5
    df, _ = q5.tab_ari_timeline(ctx)
    return df, None


# ================================================================================== I2. active protection
def fig_in_force_status_v2(ctx):
    """I2 main (final size, width 1.0): share of each architecture's designs that no patent in force protects at the snapshot, split into
    designs filed at the US office and designs filed at the other offices. The nine architectures of ten designs or more (604 of the
    627 designs; the 23 others are in the CSV and the numbers file). n under each bar, the share of the plotted designs as a dashed line."""
    import textwrap
    c = q1._calc(ctx)
    wo, force = c["wo"], c["force"]
    codes = list(force.loc[(force["unique aircraft"] >= frames.FORCE_TEST_MIN) & (force["code"] != "ALL"), "code"])
    order = force.set_index("code").loc[codes].sort_values("unique aircraft", ascending=False).index.tolist()
    wo2 = wo[wo["topType"].isin(codes)].copy()
    wo2["office_group"] = np.where(wo2["pub_office"].eq("US"), "US-filed", "other offices")
    g = wo2.groupby(["topType", "office_group"]).agg(n=("aircraft_id", "size"), out=("out", "mean")).reset_index()
    overall = float(wo2["out"].mean())                     # the share over the designs actually plotted
    W, H = final_size(1.0, 0.54)
    fig, ax = plt.subplots(figsize=(W, H), constrained_layout=True)
    x = np.arange(len(order))
    bw = 0.38
    for i, code in enumerate(order):
        s = arch(code)
        for j, grp in enumerate(["US-filed", "other offices"]):
            row = g[(g["topType"] == code) & (g["office_group"] == grp)]
            if row.empty:
                continue
            val, n = float(row["out"].iloc[0]), int(row["n"].iloc[0])
            xx = x[i] + (j - 0.5) * bw
            face = s.color if j == 0 else "white"
            ax.bar(xx, val, bw * 0.92, color=face, hatch=s.hatch if j == 0 else "", edgecolor=s.color,
                   linewidth=1.0 if j == 0 else 1.3, zorder=3)
            ax.text(xx, val + 0.02, f"{val:.0%}", ha="center", va="bottom", fontsize=MIN_PT, color=style.INK)
            ax.annotate(f"n {n}", (xx, 0), xycoords=("data", "axes fraction"), xytext=(0, -3),
                        textcoords="offset points", ha="center", va="top", fontsize=MIN_PT, color=style.MUTED, annotation_clip=False)
    ax.set_xticks(x, ["\n".join(textwrap.wrap(arch(c_).name, 10, break_long_words=False)) for c_ in order], fontsize=MIN_PT + 0.5)
    ax.tick_params(axis="x", pad=13)        # n under the bars first, then the architecture name
    ax.set_ylabel("Designs not actively\nprotected (%)")
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlim(-0.6, len(order) - 0.3)
    ax.axhline(overall, color=style.INK, linewidth=1, linestyle="--", zorder=2)
    ax.legend(handles=[Patch(facecolor=style.INK, edgecolor=style.INK, label="US-filed"),
                       Patch(facecolor="white", edgecolor=style.INK, label="other offices"),
                       Line2D([], [], color=style.INK, linewidth=1, linestyle="--",
                              label=f"all nine architectures: {overall:.0%} of {len(wo2)} designs")],
              loc="upper right", fontsize=MIN_PT, ncol=1)
    data = g.rename(columns={"topType": "code", "out": "share not actively protected"})
    data.insert(1, "architecture", [arch(c_).name for c_ in data["code"]])
    return fig, data


# ================================================================================== I3. construct validity
def tab_coding_agreement_v2(ctx):
    """I3 main: agreement between the three sources of an architecture, terminology only ('configuration' and
    'class' -> 'architecture' in the disagreement notes, since they name the architecture read, not an
    attribute archetype)."""
    df, _ = q4.tab_coding_agreement(ctx)
    df["the disagreements"] = (df["the disagreements"].str.replace("configuration", "architecture", regex=False)
                               .str.replace("one class", "one architecture", regex=False))
    return df, None


def tab_trl_representativeness_v2(ctx):
    """I3 auxiliary: flown designs (TRL 5 or more) against the rest; terminology is set in thesis_q4."""
    df, _ = q4.tab_trl_representativeness(ctx)
    df["attribute"] = df["attribute"].replace({"folded class": "architecture group"})
    return df, None


def tab_index_firm_representativeness_v2(ctx):
    """I3 auxiliary: flown index-firm designs against the rest; terminology is set in thesis_q4."""
    df, _ = q4.tab_index_firm_representativeness(ctx)
    df["attribute"] = df["attribute"].replace({"folded class": "architecture group"})
    return df, None


# ================================================================================== I4. external validity
#: this document's printed names for the five folded groups (kept as the code already had them; TB/TF plays
#: no part here — the fold is defined on the 12 architectures, and TB folds into VT, not its own group)
GROUP_NAME = {"VT": "Vectored Thrust", "LC": "Lift + Cruise", "WM": "Wingless (Multicopter)",
             "ER": "Electric Rotorcraft", "HB": "Hover Bikes / Personal Flying Devices"}
#: folded group -> (style.cls code it borrows, printed short code); SLC replaces the old "L+C" short code everywhere
GROUP_SPEC = {"LC": ("SLC", "SLC"), "VT": ("TR", "VT"), "WM": ("MR", "WM"), "ER": ("RC", "ER"), "HB": ("HB", "HB")}


def fig_class_mix_combined_v2(ctx):
    """I4 main (final size, width 1.0): the architecture distribution of the patent dataset and of the VFS eVTOL directory, as two panels side
    by side (same cohort order, same colours), one shared legend."""
    from viz import plots
    mix = q4.class_mix(ctx)
    W, H = final_size(1.0, 0.54)
    fig, axes = plt.subplots(1, 2, figsize=(W, H), constrained_layout=True, sharey=True)
    for src, label, ax in [(q4.SRC_PATENT, "patent dataset", axes[0]), (q4.SRC_DIR, "VFS eVTOL directory, in domain", axes[1])]:
        s = mix[(mix["source"] == src) & mix["window"].isin(ctx.WIN_NAMES)]
        share = s.pivot(index="window", columns="code", values="share").reindex(index=ctx.WIN_NAMES, columns=frames.CLASS5_ORDER)
        total = s.groupby("window")["window total"].first().reindex(ctx.WIN_NAMES)
        n_bars = len(ctx.WIN_NAMES)
        plots.folded_bars(ax, share.rename(index={**q4.WIN_LABEL, ctx.WIN_NAMES[-1]: "2024–26\nincomplete"}), GROUP_SPEC, totals=[int(t) for t in total])
        for patch in ax.patches[-n_bars * len(GROUP_SPEC):]:             # the incomplete cohort: drawn faded, dashed edge, never read
            if abs(patch.get_x() + patch.get_width() / 2 - (n_bars - 1)) < 1e-6:
                patch.set_alpha(0.45)
                patch.set_linestyle((0, (3, 2)))
                patch.set_edgecolor(style.INK)
        ax.set_title(label, fontsize=mpl.rcParams["font.size"])
    axes[0].set_ylabel("share of the cohort's designs")
    axes[1].set_ylabel("")
    handles = axes[0].get_legend_handles_labels()[0]
    fig.legend(handles, [f"{GROUP_SPEC[c][1]}  {GROUP_NAME[c]}" for c in frames.CLASS5_ORDER], loc="outside lower center",
              ncol=3, handlelength=1.2, columnspacing=1.0, fontsize=MIN_PT)
    data = mix[mix["source"].isin([q4.SRC_PATENT, q4.SRC_DIR]) & mix["window"].isin(ctx.WIN_NAMES)].copy()
    data["source"] = data["source"].replace({q4.SRC_DIR: "VFS eVTOL directory, pages in the domain (development year)", q4.SRC_PATENT: "patent dataset (designs, priority year)"})
    data = data.rename(columns={"window": "cohort", "window total": "cohort total", "aircraft": "designs"})
    return fig, data


def fig_dataset_vs_directory_classes_v2(ctx):
    """I4 appendix: designs per directory architecture group in the patent dataset (filled) and the evtol.news
    directory (outline), all years together."""
    from lib import intervals
    d = q4.directory_mix(ctx)
    n_set, n_dir = d["n_set"], d["n_dir"]
    O5 = q4.O5
    fig, ax = plt.subplots(figsize=final_size(1.0, 0.54), constrained_layout=True)        # final width since 2026-10-15
    x = np.arange(len(O5))
    bw = 0.38
    small = mpl.rcParams["xtick.labelsize"] - 1
    for i, c in enumerate(O5):
        s = arch(GROUP_SPEC[c][0])
        for j, (k, n, face, hatch) in enumerate([(n_set[c], n_set.sum(), s.color, s.hatch), (n_dir[c], n_dir.sum(), "white", "")]):
            xx = x[i] + (j - 0.5) * bw
            ax.bar(xx, k, bw * 0.92, color=face, hatch=hatch, edgecolor=s.color if j else "white", linewidth=1.0 if j else 0.5)
            lo, hi = intervals.wilson_interval(k, n)
            ax.plot([xx, xx], [lo * n, hi * n], color=style.INK, linewidth=0.8)
            ax.text(xx, hi * n + 6, f"{ctx.thin(k)}\n({k / n:.0%})".replace("%", " %"), ha="center", va="bottom", fontsize=small)
    ax.set_xticks(x, [f"{c}\n{GROUP_NAME[c].split(' (')[0].split(' /')[0]}" for c in O5])
    ax.set_ylim(0, max(n_set.max(), n_dir.max()) * 1.55)
    ax.set_ylabel("designs")
    ax.legend(handles=[Patch(facecolor=style.INK, label=f"patent dataset ({ctx.thin(n_set.sum())} designs; filled)"),
                       Patch(facecolor="white", edgecolor=style.INK, label=f"VFS eVTOL directory, in domain ({ctx.thin(n_dir.sum())} pages; outline)")],
              loc="upper right")
    data = pd.DataFrame({"architecture group": [GROUP_NAME[c] for c in O5], "code": O5, "patent dataset": n_set.to_numpy(),
                         "VFS eVTOL directory, in domain": n_dir.to_numpy(), "adjusted residual": d["resid"].round(1)})
    return fig, data


def fig_dataset_vs_directory_subsets_v2(ctx):
    """I4 appendix: for each architecture group, the designs in the patent dataset and in five parts of the
    directory; the original's (a)/(b)/(d) panel labels are written out in words. Each panel keeps its own x
    scale — noted here for the caption."""
    from lib import intervals
    d = q4.directory_mix(ctx)
    counts, n_set, O5 = d["counts"], d["n_set"], q4.O5
    order = list(counts)
    ylab = ["patent dataset", "directory, in domain", "concept designs", "flying hardware",
            "linked to a patent", "not linked to a patent"]       # the parts are subsets of the in-domain pages (2026-10-15)
    fig, axes = plt.subplots(1, len(O5), figsize=final_size(1.0, 0.54), constrained_layout=True)
    for i, (c, a) in enumerate(zip(O5, axes)):
        s = arch(GROUP_SPEC[c][0])
        for r, name in enumerate(order):
            k = counts[name]
            lo, hi = intervals.wilson_interval(k[c], k.sum())
            y = len(order) - 1 - r
            own = name == order[0]
            a.plot([lo * k.sum(), hi * k.sum()], [y, y], color=style.MUTED, linewidth=1)
            a.plot(k[c], y, marker=s.marker, markersize=5, linestyle="none", color=s.color if own else "white",
                   markeredgecolor=s.color if own else style.INK, markeredgewidth=0.8)
            a.annotate(ctx.thin(k[c]), (k[c], y), xytext=(0, 5.5), textcoords="offset points", ha="center", va="bottom",
                       fontsize=mpl.rcParams["xtick.labelsize"] - 1, color=style.INK, clip_on=False, zorder=6,
                       bbox=dict(fc="white", ec="none", pad=0.6))       # clear of the marker and of the dotted reference line
        a.axvline(n_set[c], color=s.color, linewidth=0.8, linestyle=":", zorder=0)
        a.set_yticks(range(len(order)), ylab[::-1] if i == 0 else [""] * len(order))
        top = max(max(k[c], intervals.wilson_interval(k[c], k.sum())[1] * k.sum()) for k in counts.values())
        a.set_xlim(-top * 0.06, top * 1.15)
        a.set_ylim(-0.6, len(order) - 0.3)
        a.set_title(c, fontsize=mpl.rcParams["font.size"])
        a.tick_params(axis="x", labelsize=mpl.rcParams["xtick.labelsize"] - 1)
        a.xaxis.set_major_locator(mpl.ticker.MaxNLocator(3, integer=True))
    fig.supxlabel("designs of the group in each source (95 % Wilson interval); parts are subsets of the in-domain pages;\n"
                  "dotted line: the patent dataset; own x scale per panel", fontsize=mpl.rcParams["xtick.labelsize"])
    return fig, d["why"]


# ================================================================================== items + writer
#: one row per figure/table of thesis_figures_v2/Part_I_evidence_base/, grouped and slotted as the task's layout
ITEMS = [
    dict(name="q1_filings_per_year", width=1.0, group="I1_patenting_rate", role="main", kind="figure", builder=fig_filings_per_year_v2,
         title="Designs filed per priority year", source_item="v2 of Figure 1 (i)"),
    dict(name="q1_growth_rates", width=1.0, group="I1_patenting_rate", role="main", kind="figure", builder=fig_growth_rates_v2,
         title="Growth of each series, log scale", source_item="v2 of Figure 1 (ii)"),
    dict(name="q1_na_drop_is_real_A", group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_na_drop_is_real_v2a,
         title="Designs per year and region, NA share as a line (version A)", source_item="v2 of Figure 23 (i), version A"),
    dict(name="q1_na_drop_is_real_B", group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_na_drop_is_real_v2b,
         title="North America's share of the year, bars replaced by a line (version B)", source_item="v2 of Figure 23 (i), version B"),
    dict(name="q4_patent_vs_market_clock", width=0.8, group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_patent_vs_market_clock_v2,
         title="The patent clock against the market clock", source_item="v2 of Figure 3"),
    dict(name="q5_ari_timeline", group="I1_patenting_rate", role="auxiliary", kind="table", builder=tab_ari_timeline_v2,
         title="AAM Reality Index timing", source_item="v2 of q5_ari_timeline (Table 1)"),
    dict(name="q1_growth_rates_table", group="I1_patenting_rate", role="appendix", kind="table", builder=tab_growth_rates_table_v2,
         title="Doubling times against the baselines", source_item="v2 of q1_growth_rates_table"),
    dict(name="q5_funding_vs_aircraft", width=0.6, group="I1_patenting_rate", role="appendix", kind="figure", builder=fig_funding_vs_aircraft_v2,
         title="Disclosed funding against the designs of the firm", source_item="v2 of q5_funding_vs_aircraft (Figure 18 (i))"),
    dict(name="q5_patenting_vs_investment", width=0.6, group="I1_patenting_rate", role="appendix", kind="figure", builder=fig_patenting_vs_investment_v2,
         title="Designs per year against sector investment per year", source_item="v2 of q5_patenting_vs_investment"),
    dict(name="q1_in_force_status", width=1.0, group="I2_active_protection", role="main", kind="figure", builder=fig_in_force_status_v2,
         title="Designs not actively protected, by architecture and office (every priority year)", source_item="v2 of Figure 4"),
    dict(name="q4_coding_agreement", group="I3_construct_validity", role="main", kind="table", builder=tab_coding_agreement_v2,
         title="Three sources of an architecture, two at a time", source_item="v2 of Table 2"),
    dict(name="q4_flown_representativeness", group="I3_construct_validity", role="auxiliary", kind="table", builder=tab_trl_representativeness_v2,
         title="Flown designs against the rest", source_item="v2 of Table 4 (flown = TRL 5 or more, 2026-10-12)"),
    dict(name="q4_flown_index_firm_representativeness", group="I3_construct_validity", role="auxiliary", kind="table", builder=tab_index_firm_representativeness_v2,
         title="Flown index-firm designs against the rest", source_item="v2 of Table 5 (index firms flown before the snapshot, 2026-10-12)"),
    dict(name="q4_class_mix", width=1.0, group="I4_external_validity", role="main", kind="figure", builder=fig_class_mix_combined_v2,
         title="Architecture distribution per window, dataset and directory side by side", source_item="v2 merging Figure 2 (i) and (ii)"),
    dict(name="q4_dataset_vs_directory_classes", width=1.0, group="I4_external_validity", role="appendix", kind="figure", builder=fig_dataset_vs_directory_classes_v2,
         title="Dataset against directory, all years", source_item="v2 of Figure 5b (i)"),
    dict(name="q4_dataset_vs_directory_subsets", width=1.0, group="I4_external_validity", role="appendix", kind="figure", builder=fig_dataset_vs_directory_subsets_v2,
         title="Designs of each architecture group per part of the directory", source_item="v2 of Figure 5b (ii)"),
]


def out_root(cfg):
    """thesis_figures_v2/Part_I_evidence_base/, a sibling of thesis_figures/ (never written into)."""
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_I_evidence_base"


def save_v2_item(item: dict, cfg, ctx) -> None:
    """Build one item and write it to <out_root>/<group>/<role>/<name>.{pdf,png,csv,json}."""
    import json
    import matplotlib.pyplot as plt
    from pathlib import Path
    # the author's Part I style (viz/part1.mplstyle), on top of the thesis base style, for the build and the save
    with plt.style.context(str(Path(__file__).with_name("part1.mplstyle"))):
        return _save_v2_item(item, cfg, ctx, json)


def _save_v2_item(item, cfg, ctx, json) -> None:
    obj, data = item["builder"](ctx)
    if item["kind"] == "figure":
        for a in obj.axes:                   # a right-hand twin axis draws no grid of its own (one grid per plot)
            if a.yaxis.get_label_position() == "right":
                a.grid(False)
    out = out_root(cfg) / item["group"] / item["role"]
    out.mkdir(parents=True, exist_ok=True)
    name = item["name"]
    meta = {k: item[k] for k in ("name", "group", "role", "kind", "title", "source_item")}
    if item["kind"] == "figure":
        import matplotlib.pyplot as plt
        exact = {"savefig.bbox": "standard"} if item.get("width") else {}        # final-size figures keep their exact page size (no tight crop)
        with plt.rc_context(exact):
            for ext in cfg.style.get("formats", ["pdf", "png"]):
                obj.savefig(out / f"{name}.{ext}")
        if data is not None:
            data.to_csv(out / f"{name}.csv", index=not isinstance(data.index, pd.RangeIndex))
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
        if item.get("width"):
            meta.update(final_width_fraction=item["width"], text_block_cm=16)
    else:
        obj.to_csv(out / f"{name}.csv", index=False)
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return obj, data
