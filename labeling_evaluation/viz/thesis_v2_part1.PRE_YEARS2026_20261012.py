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

# --------------------------------------------------------------------------------------- terminology layer
ARCH_NAME_OVERRIDE = {"TB": "Tilt Frame", "MR": "Multicopter"}            # style.py has TB = "Tilt Body"; this document calls it Tilt Frame
ARCH_SHORT_OVERRIDE = {"TB": "TF", "SLC": "SLC"}      # style.py's SLC short code is "L+C"; never used here


def arch(code: str):
    """style.cls(code) with this document's TB -> Tilt Frame / TF override; everything else unchanged."""
    s = style.cls(code)
    return dataclasses.replace(s, name=ARCH_NAME_OVERRIDE.get(code, s.name), short=ARCH_SHORT_OVERRIDE.get(code, s.short))


#: at most 5 dated sector events shown on the main-slot figure (assets/external/sector_events has 14; this is a
#: curated subset spanning the series: China's founding moment, the market-framing white paper, the first
#: certification basis, the SPAC financing wave, the first type certificate)
EVENTS_MAIN = ["2016-01-06", "2016-10-27", "2019-07-02", "2021-08-11", "2023-10-13"]


def _events_above(ax, events: pd.DataFrame, years: list, dates=EVENTS_MAIN, top: float = None, side_step: float = 0.6):
    """At most 5 dated sector events, drawn as small numbered markers along the top of the plot, each with a faint
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
    """I1 main: designs filed per priority year, bars in one colour (no region stack — the regions live in
    q1_na_drop_is_real), patent families as a line on its own right-hand axis, at most 5 dated sector events
    as ticks above the bars, the incomplete years still shaded."""
    c = q1._calc(ctx)
    fpy = c["fpy"]
    regs = frames.REGIONS + ["Other regions"]
    t = fpy.loc[2005:, regs + ["patents representative", "complete"]].copy()
    t.loc[2005, regs + ["patents representative"]] = fpy.loc[:2005, regs + ["patents representative"]].sum()
    designs = t[regs].sum(axis=1)
    incomplete = set(t.index[~t["complete"].astype(bool)])
    years = list(t.index)
    x = np.arange(len(years))
    events = frames.sector_events(ctx.cfg, fpy.attrs["snapshot"])
    n_rep = int(t["patents representative"].sum())
    ymax_bars = float(designs.max())

    fig, ax = plt.subplots(figsize=(ctx.W, 3.4), constrained_layout=True)
    ax.bar(x, designs.to_numpy(), 0.78, color="#0072B2", edgecolor="white", linewidth=0.5, zorder=3)
    for i, y in enumerate(years):
        if y in incomplete:
            ax.bar(x[i], designs.loc[y], 0.78, color=(1, 1, 1, 0.55), edgecolor=style.INK, linewidth=0.8,
                   linestyle=(0, (3, 2)), zorder=4)
    first_inc = years.index(min(incomplete))
    ax.axvline(first_inc - 0.5, color=style.INK, linewidth=0.8, linestyle="--", zorder=2)
    ax.text(first_inc - 0.4, ymax_bars * 0.98, "incomplete\nyears", va="top", ha="left", fontsize=7, color=style.MUTED,
            bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_ylim(0, ymax_bars * 1.22)
    ax.set_ylabel("designs filed")
    ax.set_xticks(x, [("≤2005" if y == 2005 else str(y)) for y in years], rotation=90)
    ax.set_xlim(-0.6, len(years) - 0.4)

    ax2 = ax.twinx()
    ax2.plot(x, t["patents representative"].to_numpy(), color=style.MUTED, linewidth=1.3, marker="o", markersize=3, zorder=5)
    ax2.set_ylabel(f"patent families ({ctx.thin(n_rep)} total)", color=style.MUTED)
    ax2.tick_params(axis="y", colors=style.MUTED)
    ax2.set_ylim(0, float(t["patents representative"].max()) * 1.22)

    key = _events_above(ax, events, years, top=ymax_bars * 1.13)
    # the key as a grid: 3 columns at fixed x, each entry left-aligned in its column (no space padding)
    fig.text(0.01, -0.03, "Sector events:", ha="left", va="top", fontsize=7, color=style.INK)
    cols, row_h = [0.13, 0.42, 0.71], 0.045
    for k, entry in enumerate(key):
        fig.text(cols[k % 3], -0.03 - (k // 3) * row_h, entry, ha="left", va="top", fontsize=7, color=style.INK)
    data = t.drop(columns="complete").assign(**{"designs filed": designs.astype(int)})
    return fig, data


def fig_growth_rates_v2(ctx):
    """I1 main: each series relative to its own 2005-09 mean, log scale; no legend box — each series is named
    at the right end of its own line; the eVTOL series in colour, the three baselines in greys."""
    c = q1._calc(ctx)
    shown = ["evtol_families", "b64", "secb", "all"]
    colours = {"evtol_families": ("#0072B2", "-", "o", 1.8), "b64": ("#808080", "--", "s", 1.2),
               "secb": ("#a6a6a6", "-.", "^", 1.2), "all": ("#c9c9c9", ":", "v", 1.4)}
    first, last = 2005, 2023
    yrs = np.arange(first, last + 1)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.6), constrained_layout=True)
    top = 1.0
    for key in shown:
        col, ls, mk, lw = colours[key]
        cnt = c["ser"][key].reindex(yrs, fill_value=0).astype(float)
        base = float(cnt.loc[2005:2009].mean())
        ok = cnt.to_numpy() > 0
        b, a = np.polyfit(yrs[ok], np.log(cnt.to_numpy()[ok]), 1)
        ax.plot(yrs[ok], cnt.to_numpy()[ok] / base, ls="none", marker=mk, ms=3, color=col, alpha=0.55)
        line = np.exp(a + b * yrs) / base
        ax.plot(yrs, line, ls=ls, lw=lw, color=col)
        ax.annotate(c["names"][key], (last, line[-1]), xytext=(4, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=7, color=col, fontweight="bold" if key == "evtol_families" else "normal")
        top = max(top, float((cnt.to_numpy()[ok] / base).max()), float(line.max()))
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    ax.set_yscale("log")
    ticks = [t for t in (0.25, 0.5, 1, 2, 4, 8, 16, 32) if t <= top * 1.6]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"×{x:g}"))
    ax.set_ylim(min(ticks) * 0.8, top * 1.5)
    ax.axhline(1, color=style.MUTED, linewidth=0.7, linestyle=":")
    ax.set_xlim(first - 0.6, last + 4.6)                      # room for the end-of-line names
    ax.set_xticks(range(2005, 2024, 2))
    ax.set_xlabel("priority year")
    ax.set_ylabel("growth since 2005–09 (log scale)")
    data = pd.DataFrame({c["names"][k]: c["ser"][k] for k in shown}).loc[2005:2023]
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


def fig_patent_vs_market_clock_v2(ctx):
    """I1 auxiliary: the patent clock against the market clock, as the original, with the unused filled
    'entry into service' legend entry removed (every ARI entry-into-service date in this corpus is a plan,
    drawn open; the filled marker is never used in this figure)."""
    from viz import plots
    tl = q4.ari_timeline(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.9), constrained_layout=True)
    plots.clock_rows(ax, tl, today=2026.45, planned_after=frames.ARI_RELEASE_YEAR - 1)
    ax.set_xlim(2012, 2031)
    ax.text(2026.5, len(tl) - 0.7, "mid-2026", fontsize=7, color=style.MUTED)
    handles = [Line2D([], [], color="#9a9a9a", linewidth=4.5, label="first to last patent"),
               Line2D([], [], color=style.INK, marker="|", markersize=9, markeredgewidth=1.6, linestyle="none",
                      label="peak filing year"),
               Line2D([], [], color=style.INK, marker="s", markersize=5.5, linestyle="none", label="first flight"),
               Line2D([], [], color="white", marker="s", markeredgecolor=style.INK, markersize=5.5, linestyle="none",
                      label="first flight, planned"),
               Line2D([], [], color="white", marker="^", markeredgecolor=style.INK, markersize=5.5, linestyle="none",
                      label="entry into service, planned")]
    fig.legend(handles=handles, loc="outside lower center", ncol=3)
    return fig, tl


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
    """I2 main: share of each architecture's designs with no patent left in force, split into designs filed at
    the US office and designs filed elsewhere — the earlier reading found this is a patent-office effect, so
    the figure now shows the office directly. The original's black 'earlier reading' ticks (first-patent-only)
    are dropped: that reading is not an office split and read as a stray mark once the office is shown. Full
    architecture names on the x axis, n of each bar printed under it."""
    c = q1._calc(ctx)
    wo, force = c["wo"], c["force"]
    codes = list(force.loc[(force["unique aircraft"] >= frames.FORCE_TEST_MIN) & (force["code"] != "ALL"), "code"])
    order = force.set_index("code").loc[codes].sort_values("unique aircraft", ascending=False).index.tolist()
    wo2 = wo[wo["topType"].isin(codes)].copy()
    wo2["office_group"] = np.where(wo2["pub_office"].eq("US"), "US-filed", "other offices")
    g = wo2.groupby(["topType", "office_group"]).agg(n=("aircraft_id", "size"), out=("out", "mean")).reset_index()

    import textwrap
    overall = float(c["w"]["out"].mean())
    fig, ax = plt.subplots(figsize=(ctx.W, 4.3), constrained_layout=True)
    x = np.arange(len(order))
    bw = 0.36
    small = mpl.rcParams["xtick.labelsize"] - 1
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
            ax.text(xx, val + 0.02, f"{val:.0%}", ha="center", va="bottom", fontsize=small, color=style.INK)
            ax.annotate(f"n {n}", (xx, 0), xycoords=("data", "axes fraction"), xytext=(0, -3),
                        textcoords="offset points", ha="center", va="top", fontsize=small - 0.5, color=style.MUTED,
                        annotation_clip=False)
    ax.set_xticks(x, ["\n".join(textwrap.wrap(arch(c_).name, 11)) for c_ in order])
    ax.tick_params(axis="x", pad=14)        # n under the bars first, then the architecture name
    ax.set_ylabel("Designs not actively\nprotected (%)")
    ax.set_ylim(0, 1.18)
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlim(-0.6, len(order) - 0.3)
    ax.axhline(overall, color=style.INK, linewidth=1, linestyle="--", zorder=2)
    ax.legend(handles=[Patch(facecolor=style.INK, edgecolor=style.INK, label="US-filed"),
                       Patch(facecolor="white", edgecolor=style.INK, label="other offices"),
                       Line2D([], [], color=style.INK, linewidth=1, linestyle="--",
                              label=f"all architectures: {overall:.0%} of {len(c['w'])} designs")],
              loc="upper right", fontsize=small)
    return fig, g.rename(columns={"topType": "code"})


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
    """I4 main: the architecture mix of the patent dataset and of the evtol.news directory, as two panels side
    by side (same window order, same colours), one shared legend, instead of two separate figures."""
    from viz import plots
    mix = q4.class_mix(ctx)
    fig, axes = plt.subplots(1, 2, figsize=(ctx.W, 3.3), constrained_layout=True, sharey=True)
    for src, label, ax in [(q4.SRC_PATENT, "patent dataset", axes[0]), (q4.SRC_DIR, "evtol.news directory", axes[1])]:
        s = mix[(mix["source"] == src) & mix["window"].isin(ctx.COMPLETE)]
        share = s.pivot(index="window", columns="code", values="share").reindex(index=ctx.COMPLETE, columns=frames.CLASS5_ORDER)
        total = s.groupby("window")["window total"].first().reindex(ctx.COMPLETE)
        plots.folded_bars(ax, share.rename(index=q4.WIN_LABEL), GROUP_SPEC, totals=[int(t) for t in total])
        ax.set_title(label, fontsize=mpl.rcParams["font.size"])
    axes[0].set_ylabel("share of the window's designs")
    axes[1].set_ylabel("")
    handles = axes[0].get_legend_handles_labels()[0]
    fig.legend(handles, [f"{GROUP_SPEC[c][1]}  {GROUP_NAME[c]}" for c in frames.CLASS5_ORDER], loc="outside lower center",
              ncol=3, handlelength=1.2, columnspacing=1.0, fontsize=mpl.rcParams["legend.fontsize"] - 0.5)
    data = mix[mix["source"].isin([q4.SRC_PATENT, q4.SRC_DIR]) & mix["window"].isin(ctx.COMPLETE)]
    return fig, data


def fig_dataset_vs_directory_classes_v2(ctx):
    """I4 appendix: designs per directory architecture group in the patent dataset (filled) and the evtol.news
    directory (outline), all years together."""
    from lib import intervals
    d = q4.directory_mix(ctx)
    n_set, n_dir = d["n_set"], d["n_dir"]
    O5 = q4.O5
    fig, ax = plt.subplots(figsize=(ctx.W, 3.1), constrained_layout=True)
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
                       Patch(facecolor="white", edgecolor=style.INK, label=f"evtol.news directory ({ctx.thin(n_dir.sum())} pages; outline)")],
              loc="upper right")
    data = pd.DataFrame({"architecture group": [GROUP_NAME[c] for c in O5], "code": O5, "patent dataset": n_set.to_numpy(),
                         "evtol.news directory": n_dir.to_numpy(), "adjusted residual": d["resid"].round(1)})
    return fig, data


def fig_dataset_vs_directory_subsets_v2(ctx):
    """I4 appendix: for each architecture group, the designs in the patent dataset and in five parts of the
    directory; the original's (a)/(b)/(d) panel labels are written out in words. Each panel keeps its own x
    scale — noted here for the caption."""
    from lib import intervals
    d = q4.directory_mix(ctx)
    counts, n_set, O5 = d["counts"], d["n_set"], q4.O5
    order = list(counts)
    ylab = ["patent dataset", "directory, all", "in domain", "concept designs", "flying hardware",
            "linked to a patent", "not linked to a patent"]
    fig, axes = plt.subplots(1, len(O5), figsize=(ctx.W, 2.9), constrained_layout=True)
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
    fig.supxlabel("designs of the architecture group in each source (95 % Wilson interval); dotted line: the patent "
                  "dataset; each panel has its own x scale", fontsize=mpl.rcParams["xtick.labelsize"])
    return fig, d["why"]


# ================================================================================== items + writer
#: one row per figure/table of thesis_figures_v2/Part_I_evidence_base/, grouped and slotted as the task's layout
ITEMS = [
    dict(name="q1_filings_per_year", group="I1_patenting_rate", role="main", kind="figure", builder=fig_filings_per_year_v2,
         title="Designs filed per priority year", source_item="v2 of Figure 1 (i)"),
    dict(name="q1_growth_rates", group="I1_patenting_rate", role="main", kind="figure", builder=fig_growth_rates_v2,
         title="Growth of each series, log scale", source_item="v2 of Figure 1 (ii)"),
    dict(name="q1_na_drop_is_real_A", group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_na_drop_is_real_v2a,
         title="Designs per year and region, NA share as a line (version A)", source_item="v2 of Figure 23 (i), version A"),
    dict(name="q1_na_drop_is_real_B", group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_na_drop_is_real_v2b,
         title="North America's share of the year, bars replaced by a line (version B)", source_item="v2 of Figure 23 (i), version B"),
    dict(name="q4_patent_vs_market_clock", group="I1_patenting_rate", role="auxiliary", kind="figure", builder=fig_patent_vs_market_clock_v2,
         title="The patent clock against the market clock", source_item="v2 of Figure 3"),
    dict(name="q5_ari_timeline", group="I1_patenting_rate", role="auxiliary", kind="table", builder=tab_ari_timeline_v2,
         title="AAM Reality Index timing", source_item="v2 of q5_ari_timeline (Table 1)"),
    dict(name="q1_growth_rates_table", group="I1_patenting_rate", role="appendix", kind="table", builder=tab_growth_rates_table_v2,
         title="Doubling times against the baselines", source_item="v2 of q1_growth_rates_table"),
    dict(name="q1_in_force_status", group="I2_active_protection", role="main", kind="figure", builder=fig_in_force_status_v2,
         title="Designs not actively protected, by architecture and office (every priority year)", source_item="v2 of Figure 4"),
    dict(name="q4_coding_agreement", group="I3_construct_validity", role="main", kind="table", builder=tab_coding_agreement_v2,
         title="Three sources of an architecture, two at a time", source_item="v2 of Table 2"),
    dict(name="q4_flown_representativeness", group="I3_construct_validity", role="auxiliary", kind="table", builder=tab_trl_representativeness_v2,
         title="Flown designs against the rest", source_item="v2 of Table 4 (flown = TRL 5 or more, 2026-10-12)"),
    dict(name="q4_flown_index_firm_representativeness", group="I3_construct_validity", role="auxiliary", kind="table", builder=tab_index_firm_representativeness_v2,
         title="Flown index-firm designs against the rest", source_item="v2 of Table 5 (index firms flown before the snapshot, 2026-10-12)"),
    dict(name="q4_class_mix", group="I4_external_validity", role="main", kind="figure", builder=fig_class_mix_combined_v2,
         title="Architecture mix per window, dataset and directory side by side", source_item="v2 merging Figure 2 (i) and (ii)"),
    dict(name="q4_dataset_vs_directory_classes", group="I4_external_validity", role="appendix", kind="figure", builder=fig_dataset_vs_directory_classes_v2,
         title="Dataset against directory, all years", source_item="v2 of Figure 5b (i)"),
    dict(name="q4_dataset_vs_directory_subsets", group="I4_external_validity", role="appendix", kind="figure", builder=fig_dataset_vs_directory_subsets_v2,
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
        for ext in cfg.style.get("formats", ["pdf", "png"]):
            obj.savefig(out / f"{name}.{ext}")
        if data is not None:
            data.to_csv(out / f"{name}.csv")
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
    else:
        obj.to_csv(out / f"{name}.csv", index=False)
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return obj, data
