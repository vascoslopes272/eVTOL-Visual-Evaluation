"""The figures of the Labelling Analysis.

Colour figures in the atlas style (one fixed hue per architecture class, blue ramp
for magnitudes, a Source and How-to-read line under every figure). Figures the
Preliminary Analysis atlas already draws are reused from :mod:`atlas`; the new
ones read their frames from :mod:`la_tables`, so a figure and its table can never
disagree. :func:`render_all` draws everything into ``<out_dir>/figures``.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import a2, atlas, figures, la_tables, metrics, numbers
from .atlas import (ARCH_COLOR, ARCH_ORDER, BLUE, CAT, GRID, INK, INK2, MUTED, OTHER, REGION_COLOR,
                    REGIONS, STYLE, SURFACE, _arch_name, _color, _fold, _heat, _hgrid, _legend_arch,
                    _stack_h)
from .la_tables import FIRM_MIN, FOLD5_NAMES, WINDOW_NAMES
from .loaders import Dataset

DPI = 200
W = 7.6                      # portrait text width, inches
PAGE = atlas.PAGE            # landscape page
SRC = "master labels (notebook 04) through labeling_evaluation/src/dataset_facts; analysis set = representative primary unique aircraft"
ARI_SRC = "AAM Reality Index, SMG Consulting (aamrealityindex.com), May 2026 release and its history, fetched 2026-09-22"
EVN_SRC = "evtol.news directory pages (EVTOLNEWS_DS/0_source/aircraft.csv) joined through patent_links.csv (use = yes)"
FIVE_COLOR = {"VT": "#2a78d6", "LC": "#4a3aa7", "WM": "#008300", "ER": "#eda100", "HB": "#e87ba4"}
#: marker and dash per class so the line charts survive black-and-white printing
CLASS_STYLE = {"SLC": ("o", "-"), "TR": ("s", "--"), "CVT": ("^", "-."), "TW": ("D", ":"), "MR": ("v", "-"),
               "TB": ("P", "--"), "PTC": ("X", "-.")}
REGION_STYLE = {"North America": ("o", "-"), "Europe": ("s", "--"), "Asia-Pacific": ("^", ":")}


def _cs(code):
    return CLASS_STYLE.get(code, ("o", "-"))


WIN_SHORT = {"<= 2011": "≤2011", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23", "2024-26 (partial)": "24–26*"}


def _stamp(fig, source: str, read: str = "") -> None:
    atlas._stamp(fig, source, read)


def _save(fig, path: Path, source: str, read: str = "") -> Path:
    with plt.rc_context(STYLE):
        _stamp(fig, source, read)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def _win_labels(names: List[str], n: Optional[pd.Series] = None) -> List[str]:
    if n is None:
        return [WIN_SHORT.get(w, w) for w in names]
    return [f"{WIN_SHORT.get(w, w)}\nn {int(n.get(w, 0))}" for w in names]


# ------------------------------------------------------- 2 taxonomy --------
def design_space_cards_svg(n: Dict, path: Path) -> Path:
    """Figure 3.3c without its bottom row: the four label cards of one unique aircraft."""
    s = figures._Svg(760, 130)
    s.text(12, 17, f"One unique aircraft: {n['questions']} slots on four label cards "
           f"({n['q_dim']} dimensions, {n['q_tick']} ticks, {n['q_num']} numbers), "
           f"filling {n['cols']} export columns", size=10.5, weight="bold")

    def kinds(card):
        parts = [(n[f"qd_{card}"], "dimension"), (n[f"qt_{card}"], "tick"), (n[f"qn_{card}"], "number")]
        return " · ".join(f"{k} {w}{'s' if k != 1 else ''}" for k, w in parts if k)

    cards = [
        ("G1 · Architecture", "G1", ["class, notPureArch"]),
        ("M1 · Structure", "M1", ["fuselage, boom group ×0..n"]),
        ("M2 · Aero", "M2", ["wing, wing panel ×1..4,", "integrated surface, empennage"]),
        ("M3 · Propulsion", "M3", ["propulsor card per host,", "propulsor type ×1..n"]),
    ]
    cards = [(title, f"{n[f'q_{c}']} slots", [kinds(c)] + body + [f"{n[f'cols_{c}']} export columns"])
             for title, c, body in cards]
    x0, w, h, y0, gap = 12, 172, 84, 30, 16
    for i, (title, slots, body) in enumerate(cards):
        x = x0 + i * (w + gap)
        s.rect(x, y0, w, h, fill="#ffffff", sw=1.1)
        s.text(x + 9, y0 + 18, title, size=10, weight="bold")
        s.text(x + w - 8, y0 + 18, slots, size=8.2, anchor="end", fill="#4d4d4d")
        s.lines(x + 9, y0 + 36, body, size=8.4, dy=12)
        if i < 3:
            s.arrow(x + w + 2, y0 + h / 2, x + w + gap - 2, y0 + h / 2, sw=1.1)
    return s.write(path)


# ------------------------------------------------------- 4.1 convergence ---
def fig_firm_weighted(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.firm_weighted_shares(v)
    fig, ax = plt.subplots(figsize=(W, 3.6))
    x = np.arange(len(WINDOW_NAMES))
    for cls, sub in t.groupby("class", sort=False):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        sub = sub.set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, sub["share by aircraft"], marker="o", lw=2, ms=5, color=_color(code), label=f"{cls} — by aircraft")
        ax.plot(x, sub["share by filer"], marker="s", lw=1.4, ms=4, ls="--", color=_color(code), label=f"{cls} — one vote per filer")
    ns = t.drop_duplicates("window").set_index("window")
    ax.set_xticks(x, [f"{WIN_SHORT[w]}\n{int(ns.loc[w, 'aircraft'])} aircraft\n{int(ns.loc[w, 'filers'])} filers" for w in WINDOW_NAMES], fontsize=8)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("share of the window")
    ax.set_title("Class share per window: every aircraft (solid) against one vote per filer (dashed)")
    ax.legend(ncol=1, fontsize=7.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    _hgrid(ax, "y")
    return _save(fig, path, SRC + "; Table 4.1.1b.",
                 "Solid: each unique aircraft counts once. Dashed: a named firm votes once per window for the class it filed "
                 "most; an individual or unattributed patent is its own filer. Where the two lines part, a few large filers "
                 "carry the class. * partial window.")


def fig_spans_by_firm(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    sp = a2.d9_aircraft_spans(ds)
    sp = sp.merge(v[["aircraft_id", "company_canonical", "named"]], on="aircraft_id", how="left")
    sizes = la_tables.firm_sizes(v)
    firms = sizes[sizes >= FIRM_MIN].index
    rep = sp[sp["span_years"] > 0].copy()
    rep["firm"] = np.where(rep["company_canonical"].isin(firms), rep["company_canonical"],
                           np.where(rep["named"], "other named firms", "individuals / unattributed"))
    order = [f for f in firms if f in rep["firm"].values] + ["other named firms", "individuals / unattributed"]
    order = [f for f in order if f in rep["firm"].values]
    rep["firm"] = pd.Categorical(rep["firm"], order)
    rep = rep.sort_values(["firm", "first"])
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 8.0), gridspec_kw={"width_ratios": [2.0, 1], "wspace": 0.55})
    y = 0
    ticks, labels = [], []
    for f, sub in rep.groupby("firm", sort=True, observed=True):
        start = y
        for _, r in sub.iterrows():
            ax.plot([r["first"], r["last"]], [y, y], color=_color(r["topType"]), lw=1.6, alpha=0.9)
            ax.plot(r["primary_year"], y, marker="o", ms=3.2, color=_color(r["topType"]))
            y += 1
        y += 0.6                                     # a gap between firms
        ticks.append((start + y - 1.6) / 2)
        labels.append(f"{f} ({len(sub)})")
        ax.axhline(y - 0.8, color=GRID, lw=0.6)
    ax.set_yticks(ticks, labels, fontsize=6.8)
    ax.invert_yaxis()
    ax.set_xlabel("priority year, first to last filing of the same aircraft")
    ax.set_title("Aircraft filed again over several years, by firm")
    _hgrid(ax, "x")
    # right: share of each firm's aircraft that were re-filed at all (any O1/O2)
    allsp = sp.copy()
    allsp["firm"] = np.where(allsp["company_canonical"].isin(firms), allsp["company_canonical"],
                             np.where(allsp["named"], "other named firms", "individuals / unattributed"))
    g = allsp.groupby("firm").agg(aircraft=("aircraft_id", "size"), refiled=("repeats", lambda s: (s > 0).sum()),
                                  span=("span_years", "max"))
    g = g.reindex(order)
    g["share"] = g["refiled"] / g["aircraft"]
    yy = np.arange(len(g))
    ax2.barh(yy, g["share"], color=BLUE(0.7), height=0.6)
    for yi, (_, r) in zip(yy, g.iterrows()):
        ax2.text(r["share"], yi, f" {int(r['refiled'])}/{int(r['aircraft'])}", va="center", fontsize=7.5)
    ax2.set_yticks(yy, list(g.index), fontsize=6.8)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 1.15)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("Share of the firm's aircraft\nfiled more than once", fontsize=9.5)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.02)
    return _save(fig, path, SRC + "; aircraft observations O1/O2 (Table 2.2.1); firms with 5 or more unique aircraft.",
                 "Left: one line per aircraft filed in more than one year, first to last filing; the dot is the primary record. "
                 "Right: of all the firm's aircraft, how many were filed again (any O1 / O2), whatever the span. Re-filing the "
                 "same aircraft for years is the only commitment signal the patents themselves carry.")


def fig_two_counts(ds: Dataset, path: Path) -> Path:
    t = a2.d9_architecture_by_window_active(ds)
    classes = [c for c in t.columns if c not in ("window", "count", "unique aircraft")]
    fig, axes = plt.subplots(1, len(classes), figsize=(W, 3.0), sharey=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, cls in zip(axes, classes):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        for mode, ls, mk in (("once, at the primary record", "-", "o"), ("while filed, first to last", "--", "s")):
            sub = t[t["count"].eq(mode)].set_index("window").reindex(WINDOW_NAMES)
            ax.plot(x, sub[cls], ls=ls, marker=mk, ms=4, lw=1.8, color=_color(code), label=mode)
        ax.set_title(f"{code}", fontsize=9.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=6.5, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
    fig.subplots_adjust(bottom=0.34, top=0.8)
    fig.suptitle("Class share per window, aircraft counted once (solid) or in every window it was filed in (dashed)",
                 x=0.01, y=0.98, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; aircraft spans (O1/O2 re-filings).",
                 "Solid: the aircraft sits in the window of its primary record. Dashed: it counts in every window from its "
                 "first to its last filing. The gap between the lines is what the dating rule can move.")


def fig_lead_lag(v: pd.DataFrame, path: Path) -> Path:
    cr, qr = la_tables.lead_lag(v, "region3")
    cc, qc = la_tables.lead_lag(v, "topType", top=7)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.6), gridspec_kw={"wspace": 0.25})
    for g in cr.columns:
        ax.plot(cr.index, cr[g], lw=2.2, ls=REGION_STYLE.get(g, ("o", "-"))[1], color=REGION_COLOR.get(g, OTHER), label=f"{g} ({int(qr.set_index('region3').loc[g, 'aircraft'])})")
    for p in (0.25, 0.5, 0.75):
        ax.axhline(p, color=GRID, lw=0.8)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("By applicant region", fontsize=9.5)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlabel("priority year (complete years, to 2023)")
    for g in cc.columns:
        ax2.plot(cc.index, cc[g], lw=2, ls=_cs(g)[1], color=_color(g), label=_arch_name(g))
    for p in (0.25, 0.5, 0.75):
        ax2.axhline(p, color=GRID, lw=0.8)
    ax2.set_ylim(0, 1)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("By class, seven largest", fontsize=9.5)
    ax2.legend(loc="upper left", fontsize=7)
    ax2.set_xlabel("priority year (complete years, to 2023)")
    fig.suptitle("Cumulative share of each group's own aircraft by priority year (lead and lag)",
                 x=0.01, y=1.0, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; complete priority years only (≤ 2023); Tables 4.1.3a/b.",
                 "Each curve is one group divided by its own total, so the axis is not volume but timing: the year a curve "
                 "crosses 50 % is the group's median year. A curve to the left leads, to the right lags.")


def fig_class_cycles(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.class_cycles(v).set_index("class")
    classes = t.index.tolist()
    ncol = 4
    nrow = int(np.ceil(len(classes) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(W, 1.75 * nrow), sharey=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, cls in zip(axes.flat, classes):
        code = next(k for k, nm in metrics.ARCH_NAMES.items() if nm == cls)
        vals = t.loc[cls, WINDOW_NAMES].astype(float).to_numpy()
        ax.bar(x, vals, color=_color(code) if code in ARCH_COLOR else OTHER, width=0.72)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        med = WINDOW_NAMES.index(t.loc[cls, "median window"])
        ax.plot(med, vals[med] + 0.05, marker="v", color=INK, ms=5)
        ax.set_title(f"{code} ({int(t.loc[cls, 'aircraft'])})", fontsize=8.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=6.3, rotation=45)
        ax.set_ylim(0, 1.0)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        _hgrid(ax, "y")
    for ax in list(axes.flat)[len(classes):]:
        ax.axis("off")
    fig.suptitle("Where in time each class lives: its aircraft per window as a share of its own total (▼ median window; codes as Figure 2.1a)",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.subplots_adjust(hspace=0.85, wspace=0.12)
    return _save(fig, path, SRC + "; Table 4.1.4.",
                 "Bars sum to 100 % across each class's own panel. A class whose bars peak early and empty later has faded; one "
                 "whose bars rise to the right is still growing. Classes ordered by size; * partial window.")


def fig_hill(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.hill_by_window(v)
    levels = t["level"].unique()
    fig, axes = plt.subplots(1, len(levels), figsize=(W, 3.0), sharex=True)
    x = np.arange(len(WINDOW_NAMES))
    for ax, lvl in zip(np.atleast_1d(axes), levels):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        for q, col, lab in ((0, CAT[0], "⁰D richness"), (1, CAT[1], "¹D exp Shannon"), (2, CAT[2], "²D inverse Simpson")):
            ax.errorbar(x, sub[f"D{q}"], yerr=[sub[f"D{q}"] - sub[f"D{q} low"], sub[f"D{q} high"] - sub[f"D{q}"]],
                        marker="o", ms=4, lw=1.8, capsize=2, color=col, label=lab)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES, sub["aircraft"]), fontsize=7.5)
        ax.set_title(lvl, fontsize=9.5)
        ax.set_ylim(0)
        _hgrid(ax, "y")
    np.atleast_1d(axes)[0].legend(fontsize=7.5, loc="upper left")
    np.atleast_1d(axes)[0].set_ylabel("effective number of archetypes")
    fig.suptitle("Diversity per window, rarefied to 40 aircraft (1 000 draws, 95 % band)", x=0.01, y=1.04, ha="left",
                 fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.5; A0 = class, A0c = class × propulsor-unit bin.",
                 "Hill numbers at equal sample size: ⁰D counts archetypes, ¹D and ²D weigh them by share, so a fall in ¹D or "
                 "²D with a flat ⁰D means the same archetypes but a more uneven mix (convergence); rising means spreading out.")


def fig_zones(v: pd.DataFrame, path: Path) -> Path:
    z = la_tables.zones(v)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 4.6), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.42})
    # heatmap archetype × window, counts, with the filers per archetype at the right
    mat = z.set_index("archetype")[WINDOW_NAMES]
    mat.columns = _win_labels(WINDOW_NAMES)
    mat = mat.astype(float)
    _heat(ax, mat.div(mat.max(axis=1), axis=0), counts=mat)
    ax.set_yticks(range(len(mat)), [f"{a}  ·  {f} filers" for a, f in zip(z["archetype"], z["filers"])], fontsize=7)
    ax.set_title("Aircraft per window", fontsize=9.5)
    # quadrant: share of 2016-23 vs filers per aircraft
    zz = z[z["filers 2016-23"] > 0]
    for _, r in zz.iterrows():
        ax2.scatter(r["share 2016-23"], r["filers per aircraft"], s=18 + 3.2 * r["aircraft"], color=_color(r["code"]),
                    alpha=0.85, edgecolor=SURFACE, lw=0.8, marker={"new": "^", "fading": "v"}.get(r["zone"], "o"))
        if r["aircraft"] >= 12 or r["share 2016-23"] >= 0.03 or r["filers per aircraft"] < 0.75:
            ax2.annotate(r["archetype"].replace(" · ", " ").replace(" n/a (no M3 card)", ""),
                         (r["share 2016-23"], r["filers per aircraft"]),
                         fontsize=6.2, xytext=(3, 2), textcoords="offset points", color=INK2)
    ax2.axvline(zz["share 2016-23"].median(), color=GRID, lw=1)
    ax2.axhline(zz["filers per aircraft"].median(), color=GRID, lw=1)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_xlabel("share of the 2016–23 aircraft")
    ax2.set_ylabel("distinct filers per aircraft")
    ax2.set_title("Crowded (right, low) vs open (left, high)", fontsize=9.5)
    ax2.text(0.99, 0.02, "▲ new (first seen 2016+)   ▼ fading (absent after 2019)   ● persistent", transform=ax2.transAxes,
             ha="right", fontsize=6.5, color=INK2)
    _hgrid(ax2, "both")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.02)
    return _save(fig, path, SRC + "; A0c archetypes (class × propulsor-unit bin) with 5 or more aircraft; Table 4.1.6.",
                 "Left: darker = the archetype's busiest window. Right: an archetype far right holds a big share of recent "
                 "aircraft; one high up is filed by many different filers per aircraft (open field), one low down by few filers "
                 "holding many aircraft (crowded by a few). Bubble size = aircraft.")


def fig_abandonment(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.abandonment_by_class(v)
    t = t[t["class"].ne("all classes")]
    t = t[t["patents"] >= 5]
    fig, ax = plt.subplots(figsize=(W, 2.9))
    y = np.arange(len(t))
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == c), c) for c in t["class"]]
    ax.barh(y, t["lapsed share"], color=[_color(c) for c in codes], height=0.66)
    for yi, (_, r) in zip(y, t.iterrows()):
        ax.text(r["lapsed share"], yi, f" {int(r['lapsed'])}/{int(r['patents'])}", va="center", fontsize=8)
    allrow = la_tables.abandonment_by_class(v).set_index("class").loc["all classes"]
    ax.axvline(allrow["lapsed share"], color=INK, lw=1, ls="--")
    ax.text(allrow["lapsed share"], len(t) - 0.3, f" all classes {allrow['lapsed share']:.0%}", fontsize=7.5, color=INK2)
    ax.set_yticks(y, t["class"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("Primary patents lapsed, withdrawn, expired or refused, per class (priority ≤ 2019)")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    return _save(fig, path, SRC + "; PatSeer legal_status_raw of the primary patent; Table 4.1.7.",
                 "Share of each class's primary patents that are no longer in force, among patents old enough to have "
                 "been granted and then kept or dropped. A high share is money withdrawn from that class.")


# ------------------------------------------------------- 4.2 provenance ----
def fig_region_grid(v: pd.DataFrame, path: Path) -> Path:
    variables = list(la_tables.GRID_VARIABLES)
    fig, axes = plt.subplots(len(variables), len(REGIONS), figsize=(W, 1.45 * len(variables) + 0.5),
                             sharex=True)
    x = np.arange(len(WINDOW_NAMES))
    palettes = {
        "class": lambda cols: {c: _color(c) for c in cols},
        "propulsor units": lambda cols: dict(zip(cols, [BLUE(t) for t in np.linspace(0.25, 0.95, len(cols))])),
        "tilting unit": lambda cols: {True: CAT[1], False: CAT[0], "blank": OTHER},
        "ducted unit": lambda cols: {True: CAT[6], False: CAT[2], "blank": OTHER},
        "powertrain": lambda cols: {"Yes": CAT[2], "Hybrid": CAT[3], "Unknown": OTHER, "No": CAT[7]},
        "filer type": lambda cols: {"Named company": CAT[0], "University / institute": CAT[6], "Individual inventor": CAT[3], "Unattributed / independent": OTHER},
    }
    names = {True: "yes", False: "no", "blank": "not determinable", "Yes": "electric", "Hybrid": "hybrid",
             "Unknown": "not stated", "No": "non-electric"}
    for i, var in enumerate(variables):
        shares, n = la_tables.region_window_shares(v, var)
        if var == "class":
            keep = [c for c in ARCH_ORDER if c in shares.columns]
            other = shares.drop(columns=keep).sum(axis=1)
            shares = shares[keep].assign(Other=other)
        pal = palettes[var](list(shares.columns))
        for j, reg in enumerate(REGIONS):
            ax = axes[i, j]
            sub = shares.loc[reg].reindex(WINDOW_NAMES) if reg in shares.index.get_level_values(0) else None
            bottom = np.zeros(len(x))
            if sub is not None:
                for col in sub.columns:
                    vals = sub[col].fillna(0).to_numpy(dtype=float)
                    ax.bar(x, vals, bottom=bottom, color=pal.get(col, OTHER), width=0.74, edgecolor=SURFACE, lw=0.8,
                           label=names.get(col, metrics.ARCH_NAMES.get(col, col) if var == "class" else col))
                    for xi, (b, val) in enumerate(zip(bottom, vals)):
                        if val >= 0.15:
                            ax.text(xi, b + val / 2, f"{val:.0%}", ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
                    bottom += vals
                blank = sub.isna().all(axis=1).to_numpy()
                for xi in x[blank]:
                    ax.text(xi, 0.5, "n < 10", ha="center", va="center", fontsize=7, color=INK2)
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            ax.spines[["left", "bottom"]].set_visible(False)
            if i == 0:
                ax.set_title(reg, fontsize=10, color=REGION_COLOR.get(reg, INK))
            if j == 0:
                ax.set_ylabel(var, fontsize=9, rotation=0, ha="right", va="center", labelpad=6)
            nn = n.loc[reg] if reg in n.index.get_level_values(0) else pd.Series(dtype=int)
            ax.set_xticks(x, [f"{WIN_SHORT[w]}\n{int(nn.get(w, 0))}" for w in WINDOW_NAMES], fontsize=6.8)
            if j == len(REGIONS) - 1:
                ax.legend(fontsize=5.8, loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1)
    fig.suptitle("Six variables per region and window, share of the region-window cell (cell count under the axis)",
                 x=0.01, ha="left", fontsize=9.5, fontweight="bold")
    fig.subplots_adjust(hspace=0.6, wspace=0.08, right=0.8)
    return _save(fig, path, SRC + "; region = applicant region (identity), not publication office; cells under 10 aircraft blanked.",
                 "Each bar is 100 % of the aircraft of one region in one window. Read down a column for how a region's "
                 "aircraft changed, across a row for how regions differ at the same time. * partial window.")


def fig_country_class(v: pd.DataFrame, path: Path) -> Path:
    shares, n = la_tables.country_class(v, top=8)
    mat = shares.copy()
    mat.index = [f"{c} (n {int(n[c])})" for c in mat.index]
    fig, ax = plt.subplots(figsize=(W, 3.4))
    _heat(ax, mat, fmt="{:.0%}", vmax=0.5)
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=0)
    ax.set_title("Class share per applicant country, eight largest countries (codes as Figure 2.1a)")
    return _save(fig, path, SRC + "; assignee_country of the primary patent's identity record.",
                 "Rows sum to 100 %. Read across a row for a country's mix; down a column for where a class is filed. "
                 "Capped at 50 % so that the middle of the range keeps contrast.")


# ------------------------------------------------------- 4.3 assignees -----
def fig_coverage(v: pd.DataFrame, path: Path) -> Path:
    sizes = la_tables.firm_sizes(v)
    ari = set(la_tables.ari_firms(v)["company"])
    total = len(v)
    cum = sizes.cumsum() / total
    rank = np.arange(1, len(sizes) + 1)
    fig, ax = plt.subplots(figsize=(W, 3.8))
    ax.step(rank, cum, where="post", color=BLUE(0.8), lw=2)
    for i, (k, lab) in enumerate(((10, "≥ 10"), (5, "≥ 5"), (4, "≥ 4"), (3, "≥ 3"), (2, "≥ 2"))):
        nf = int((sizes >= k).sum())
        if nf:
            ax.axvline(nf, color=GRID, lw=1)
            ax.text(nf, 0.92 - 0.07 * i, f" {lab} aircraft: {nf} firms, {cum.iloc[nf - 1]:.0%}", fontsize=7.5, color=INK2)
    named_share = sizes.sum() / total
    ax.axhline(named_share, color=INK, lw=1, ls="--")
    ax.text(len(sizes), named_share, f"all named companies {named_share:.0%} ", ha="right", va="bottom", fontsize=8)
    ax.axhline(1, color=GRID, lw=0.8)
    ax.text(len(sizes), 1.0, "whole analysis set (individuals and unattributed filers are the rest) ", ha="right", va="bottom", fontsize=7.5, color=INK2)
    k = 0
    for i, (f, s) in enumerate(sizes.items()):
        if f in ari:
            ax.plot(i + 1, cum.iloc[i], marker="o", ms=5, color=CAT[1], zorder=5)
            ax.annotate(f, (i + 1, cum.iloc[i]), fontsize=6.2, xytext=(4, -10 - 9 * (k % 3)), textcoords="offset points",
                        color=CAT[1], rotation=-30)
            k += 1
    ax.set_xlim(0, len(sizes) + 1)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("named companies ranked by unique aircraft (largest first)")
    ax.set_ylabel("cumulative share of the analysis set")
    ax.set_title("How much of the analysis set the top N firms cover; orange = firm on the AAM Reality Index")
    _hgrid(ax, "both")
    return _save(fig, path, SRC + "; Table 4.3.1; ARI firms from " + ARI_SRC + ".",
                 "The curve climbs steeply over the first firms and then flattens: beyond the vertical marks each extra "
                 "firm adds a few aircraft. The cut for per-firm profiles is where a firm still has enough aircraft "
                 "for a class share to mean something (5).")


def fig_filers_over_time(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.filers_by_window(v).set_index("window").reindex(WINDOW_NAMES)
    co = la_tables.cohorts(v).set_index("window").reindex(WINDOW_NAMES).fillna(0)
    fig, (ax, axc) = plt.subplots(1, 2, figsize=(W, 3.8), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.35})
    x = np.arange(len(t))
    ax.bar(x, t["continuing firms"], color=BLUE(0.75), width=0.66, label="firms already seen in an earlier window")
    ax.bar(x, t["new firms"], bottom=t["continuing firms"], color=CAT[2], width=0.66, label="firms filing for the first time")
    gone = pd.to_numeric(t["firms last seen"], errors="coerce")
    ax.bar(x, -gone.fillna(0), color=CAT[7], width=0.66, label="firms not seen again (judged up to 2016–19)")
    for xi, (_, r) in zip(x, t.iterrows()):
        ax.text(xi, r["named firms active"] + 0.5, f"{int(r['named firms active'])} firms\n{int(r['aircraft by named firms'])} aircraft",
                ha="center", va="bottom", fontsize=7)
    ax.axhline(0, color=INK, lw=0.8)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.set_xticks(x, _win_labels(WINDOW_NAMES, t["unique aircraft"]), fontsize=7.5)
    ax.set_ylim(top=float(t["named firms active"].max()) * 1.3)
    ax.set_ylabel("named firms")
    ax2 = ax.twinx()
    ax2.plot(x, t["share individual inventors"], color=CAT[3], marker="o", lw=2, label="share of the window's aircraft by individual inventors")
    ax2.plot(x, t["share unattributed"], color=OTHER, marker="s", lw=1.6, label="share unattributed / independent")
    ax2.set_ylim(0, 0.8)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.spines[["top"]].set_visible(False)
    ax.set_title("Filers per window: entries, returners, exits", fontsize=9.5)
    # cohorts: entrants by the class they entered with
    cols = [c for c in ARCH_ORDER if c in co.columns]
    other = co.drop(columns=["firms entering"] + cols).sum(axis=1)
    bottom = np.zeros(len(co))
    for c in cols + ["Other"]:
        vals = (co[c] if c != "Other" else other).to_numpy(dtype=float)
        axc.bar(x, vals, bottom=bottom, color=_color(c), width=0.66, edgecolor=SURFACE, lw=0.8)
        bottom += vals
    for xi, n in zip(x, co["firms entering"]):
        axc.text(xi, n + 0.4, f"{int(n)}", ha="center", va="bottom", fontsize=7.5)
    axc.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    axc.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7.5)
    axc.set_ylabel("firms entering")
    axc.set_title("Entry cohorts: first-window class of new firms", fontsize=9.5)
    _hgrid(axc, "y")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, fontsize=6.8, loc="lower center", bbox_to_anchor=(0.5, 0.09), ncol=2)
    fig.subplots_adjust(bottom=0.42)
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=0.0)
    return _save(fig, path, SRC + "; Tables 4.2.2a/b; named firms = companies and institutes.",
                 "Left, bars above zero: named firms with at least one aircraft in the window, first-timers and returners; "
                 "below zero, firms whose last filing is in that window (not judged in the last two windows). Lines: the "
                 "share of the window's aircraft filed by individuals. Right: the firms that enter in each window, coloured "
                 "by the class of their first aircraft.")
def fig_firm_tiles(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.firm_windows(v)
    firms = (t.drop_duplicates("firm").assign(fi=lambda d: d["first window"].map(WINDOW_NAMES.index))
             .sort_values(["fi", "aircraft total"], ascending=[True, False])["firm"].tolist())
    fig, ax = plt.subplots(figsize=(W, 0.32 * len(firms) + 1.3))
    x = np.arange(len(WINDOW_NAMES))
    for yi, f in enumerate(firms):
        sub = t[t["firm"].eq(f)].set_index("window").reindex(WINDOW_NAMES)
        for xi, (w, r) in zip(x, sub.iterrows()):
            if r["aircraft"] > 0:
                ax.scatter(xi, yi, s=28 + 22 * r["aircraft"], color=_color(r["modal class"]), alpha=0.9, edgecolor=SURFACE, lw=0.8)
                ax.text(xi, yi, f"{int(r['aircraft'])}", ha="center", va="center", fontsize=6.8, color="white", fontweight="bold")
    ax.set_yticks(range(len(firms)), [f"{f} ({int(t[t['firm'].eq(f)]['aircraft total'].iloc[0])})" for f in firms], fontsize=8)
    ax.invert_yaxis()
    ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=8)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.set_xlim(-0.5, len(x) - 0.5)
    ax.set_title("Firms with 5 or more aircraft, per window: aircraft (size, number) and the class filed most (colour)")
    ax.spines[["left", "bottom"]].set_visible(False)
    _hgrid(ax, "both")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.02)
    return _save(fig, path, SRC + "; Table 4.3.4; firms ordered by first window, then size.",
                 "One row per firm, one bubble per window it filed in. A row that changes colour is a firm that changed "
                 "its main class; a row that starts late is an entrant.")


def fig_proximity_region(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    m, summary = la_tables.proximity_by_region(ds, v)
    reg = m.attrs["region"]
    prof = a2.firm_profiles(ds, FIRM_MIN, "class")
    size = prof.sum(axis=1)
    fig = plt.figure(figsize=(W, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.045, 1], wspace=0.02)
    axr = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[0, 1])
    shown = m.to_numpy().copy()
    np.fill_diagonal(shown, np.nan)
    im = ax.imshow(shown, cmap=BLUE, vmin=0, vmax=1)
    for i in range(len(m)):
        for j in range(len(m)):
            val = float(m.iat[i, j])
            if i != j and val >= 0.5:
                ax.text(j, i, "1" if val >= 0.995 else f"{val:.2f}"[1:], ha="center", va="center", fontsize=6,
                        color="white" if val > 0.6 else INK)
    labels = [f"{f} ({int(size[f])})" for f in m.index]
    ax.set_xticks(range(len(m)), labels, rotation=60, ha="right", fontsize=7)
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    axr.imshow(np.array([[0] for _ in m.index]), cmap="Greys", vmin=0, vmax=1, aspect="auto")
    for i, f in enumerate(m.index):
        axr.add_patch(matplotlib.patches.Rectangle((-0.5, i - 0.5), 1, 1, color=REGION_COLOR.get(reg[f], OTHER)))
    axr.set_yticks(range(len(m)), labels, fontsize=7)
    axr.set_xticks([])
    for s in axr.spines.values():
        s.set_visible(False)
    txt = " · ".join(f"{r['firm pair']}: mean {r['mean']:.2f} over {int(r['pairs'])} pairs" for _, r in summary.iterrows())
    ax.set_title("Technological proximity between firms (class profile); colour strip = the firm's region\n" + txt,
                 fontsize=9.5)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("proximity: 1 = same mix of classes, 0 = none in common", fontsize=7.5)
    handles = [matplotlib.patches.Patch(color=REGION_COLOR[r], label=r) for r in REGIONS]
    fig.legend(handles=handles, loc="lower right", ncol=1, bbox_to_anchor=(0.99, 0.12), fontsize=7.5)
    return _save(fig, path, SRC + "; Jaffe (1986) cosine of firm × class vectors, firms with 5 or more aircraft; Table 4.3.5.",
                 "Firms are ordered so that similar ones sit together. Two firms score 1 when they file the same mix of "
                 "classes, 0 when they share none. The strip shows whether design neighbours share a region; the line "
                 "under the figure gives the mean proximity of same-region and different-region pairs.")


def fig_ari(v: pd.DataFrame, path: Path) -> Path:
    f = la_tables.ari_firms(v)
    hist = la_tables.ari_history_corpus(v)
    tl = la_tables.ari_timeline(v)
    fig = plt.figure(figsize=(W, 10.2))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.15, 0.9, 0.95], hspace=0.55, wspace=0.5)
    # (a) score with class mix
    ax = fig.add_subplot(gs[0, :])
    ff = f.sort_values("ARI score", ascending=False).reset_index(drop=True)
    y = np.arange(len(ff))
    current = ff["release"].eq("May 2026")
    ax.barh(y, ff["ARI score"], color=[BLUE(0.8) if c else BLUE(0.35) for c in current], height=0.62)
    for yi, (_, r) in zip(y, ff.iterrows()):
        tag = "" if r["release"] == "May 2026" else f"  (to {r['release'][:3]} {r['release'][-4:]})"
        ax.text(r["ARI score"], yi, f" {r['ARI score']:.1f}{tag}", va="center", fontsize=7.5)
    ax.set_yticks(y, [f"{r['company']}  ·  {int(r['unique aircraft'])} aircraft" for _, r in ff.iterrows()], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 10.5)
    ax.set_xlabel("AAM Reality Index score (0–10)")
    ax.set_title("Index firms that file in the corpus: score and their patent class mix", fontsize=9.5)
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax, "x")
    ax_m = ax.inset_axes([1.03, 0, 0.22, 1], sharey=ax)
    left = np.zeros(len(ff))
    for code in ARCH_ORDER + ["Other"]:
        vals = []
        for _, r in ff.iterrows():
            sub = v[v["company_canonical"].eq(r["company"])]["topType"].map(_fold)
            vals.append((sub.eq(code).sum() / max(len(sub), 1)))
        vals = np.array(vals)
        ax_m.barh(y, vals, left=left, color=_color(code), height=0.62, edgecolor=SURFACE, lw=0.6)
        left += vals
    ax_m.set_xlim(0, 1)
    ax_m.set_xticks([0, 1], ["0", "100 %"], fontsize=7)
    ax_m.tick_params(labelleft=False, left=False)
    for sp in ax_m.spines.values():
        sp.set_visible(False)
    ax_m.set_xlabel("class mix", fontsize=8)
    # (b) history
    ax2 = fig.add_subplot(gs[1, 0])
    ends = []
    for comp, sub in hist.groupby("company"):
        sub = sub.sort_values("date")
        ax2.plot(sub["date"], sub["score"], lw=1.4, marker="o", ms=2.2, alpha=0.85)
        ends.append((sub["date"].iloc[-1], float(sub["score"].iloc[-1]), comp))
    ends.sort(key=lambda e: e[1])
    last_y = -9
    xr = hist["date"].max()
    for d, sc, comp in ends:
        yv = max(sc, last_y + 0.28)
        ax2.annotate(comp, (xr, yv), xytext=(4, 0), textcoords="offset points", fontsize=6, va="center", color=INK2)
        last_y = yv
    ax2.set_ylim(3, 9.5)
    ax2.set_title("Score per release since Dec 2020", fontsize=9.5)
    ax2.set_ylabel("ARI score")
    _hgrid(ax2, "y")
    # (c) funding vs aircraft
    ax3 = fig.add_subplot(gs[1, 1])
    fc = f.copy()
    fc["funding"] = pd.to_numeric(fc["funding $M"].astype(str).str.replace(",", ""), errors="coerce")
    disclosed = fc.dropna(subset=["funding"])
    ax3.scatter(disclosed["unique aircraft"], disclosed["funding"], s=30 + 40 * disclosed["ARI score"].fillna(5) / 10,
                color=BLUE(0.8), edgecolor=SURFACE)
    for _, r in disclosed.iterrows():
        ax3.annotate(r["company"], (r["unique aircraft"], r["funding"]), fontsize=6.3, xytext=(3, 2), textcoords="offset points")
    undisclosed = ", ".join(fc[fc["funding"].isna()]["company"])
    ax3.set_yscale("log")
    ax3.set_xlabel("unique aircraft in the corpus")
    ax3.set_ylabel("disclosed funding, $M (log)")
    ax3.set_title("Funding against patented aircraft", fontsize=9.5)
    _hgrid(ax3, "both")
    # (d) patent clock against market clock
    ax4 = fig.add_subplot(gs[2, :])
    tl = tl.sort_values("first patent").reset_index(drop=True)
    yy = np.arange(len(tl))
    for yi, (_, r) in zip(yy, tl.iterrows()):
        ax4.plot([r["first patent"], r["last patent"]], [yi, yi], color=BLUE(0.7), lw=4, solid_capstyle="butt")
        ax4.plot(r["peak filing year"], yi, marker="|", ms=11, mew=2, color=INK)
        if pd.notna(r["first flight (ARI)"]):
            ax4.plot(r["first flight (ARI)"], yi, marker="^", ms=7, color=CAT[1], zorder=5)
        if pd.notna(r["entry into service (ARI)"]):
            ax4.plot(r["entry into service (ARI)"], yi, marker="D", ms=6, color=CAT[2], zorder=5)
    ax4.set_yticks(yy, [f"{r['company']} ({int(r['unique aircraft'])})" for _, r in tl.iterrows()], fontsize=7.5)
    ax4.invert_yaxis()
    ax4.axvline(2026.7, color=GRID, lw=1)
    ax4.text(2026.8, -0.6, "today", fontsize=7, color=INK2)
    handles = [matplotlib.lines.Line2D([], [], color=BLUE(0.7), lw=4, label="first to last patent (priority years)"),
               matplotlib.lines.Line2D([], [], color=INK, marker="|", ms=10, mew=2, ls="", label="peak filing year"),
               matplotlib.lines.Line2D([], [], color=CAT[1], marker="^", ms=7, ls="", label="first flight (index)"),
               matplotlib.lines.Line2D([], [], color=CAT[2], marker="D", ms=6, ls="", label="entry into service (index, planned)")]
    ax4.legend(handles=handles, fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    ax4.set_title("Patent clock against market clock, index firms listed in May 2026", fontsize=9.5)
    ax4.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    _hgrid(ax4, "x")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.01)
    return _save(fig, path, ARI_SRC + "; corpus counts from " + SRC + "; Tables 4.2.6a/b/c. Corporate-backed or "
                 "undisclosed funding, not in the scatter: " + undisclosed + ".",
                 "Top: the index score (darker = listed in May 2026, lighter = last score before the firm left the index) "
                 "beside the firm's class mix. Middle: how each score moved; disclosed funding against patented aircraft, "
                 "bubble = score. Bottom: each firm's patent span and peak year against the first flight and planned entry "
                 "into service the index states.")
def fig_mission(v: pd.DataFrame, path: Path) -> Path:
    linked = la_tables.linked_aircraft(v)
    tabs = la_tables.mission_tables(linked)
    fields = ["capacity", "piloting", "power source", "status"]
    fig = plt.figure(figsize=(W, 5.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.85], hspace=0.8, wspace=0.3)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    ax_h = fig.add_subplot(gs[0, 2])
    order5 = [c for c in ["VT", "LC", "WM", "ER", "HB"] if c in linked["class5"].values]
    ns = linked["class5"].value_counts()
    for ax, field in zip(axes, fields):
        t = tabs[field].set_index(field).drop(columns="all")
        t = t.reindex(columns=order5, fill_value=0)
        share = t.div(t.sum(axis=0), axis=1).T
        share.index = [f"{c} (n {int(ns[c])})" for c in share.index]
        cols = list(share.columns)
        pal = dict(zip(cols, [BLUE(x) for x in np.linspace(0.9, 0.25, len(cols))]))
        _stack_h(ax, share, pal, min_label=0.15)
        ax.set_title(field, fontsize=9.5)
        ax.tick_params(axis="y", labelsize=7.5)
        ax.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, handlelength=1.2, columnspacing=0.8)
    ag = tabs["agreement"].set_index("patent label")
    ag.index = [next(k for k, nm in FOLD5_NAMES.items() if i.replace("G1 folded: ", "") == nm) for i in ag.index]
    _heat(ax_h, ag.div(ag.sum(axis=1), axis=0), counts=ag)
    ax_h.set_title("patent (rows) vs\nevtol.news (cols)", fontsize=8.5)
    ax_h.set_xticks(range(ag.shape[1]), ag.columns, rotation=0, fontsize=7.5)
    ax_h.tick_params(axis="y", labelsize=7.5)
    fig.suptitle(f"Mission of the {len(linked)} aircraft linked to an evtol.news page, by the patent's class folded to the\n"
                 "directory's five classes (VT vectored thrust, LC lift + cruise, WM wingless, ER electric rotorcraft, HB hover bikes)",
                 x=0.01, y=0.99, ha="left", fontsize=9.5, fontweight="bold")
    return _save(fig, path, EVN_SRC + "; G1 class folded as Table 4.3.8a; capacity, piloting, power source and status parsed from the page text.",
                 "Four panels: each bar is 100 % of the linked aircraft of one folded class. Heatmap: how often the "
                 "folded patent class agrees with the class the directory gives the same aircraft (count in the cell).")



# ------------------------------------------------------- new 2026-09-22 (2nd round)
def fig_filings_per_year(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.filings_per_year(ds, v).set_index("priority year")
    t = t[t.index >= 2005]
    p90 = t.attrs["p90"]
    fig, ax = plt.subplots(figsize=(W, 3.8))
    bottom = np.zeros(len(t))
    colors = {**REGION_COLOR, "Other regions": OTHER}
    hatches = {"North America": "", "Europe": "..", "Asia-Pacific": "//", "Other regions": "xx"}
    for col in REGIONS + ["Other regions"]:
        bars = ax.bar(t.index, t[col], bottom=bottom, color=colors[col], width=0.8, label=col, edgecolor=SURFACE, lw=0.8,
                      hatch=hatches[col])
        bottom += t[col].to_numpy()
    for xi, (_, r) in zip(t.index, t.iterrows()):
        if not r["complete"]:
            ax.bar(xi, r["unique aircraft"], color="none", edgecolor=INK, lw=1.0, hatch="////", width=0.8, alpha=0.5)
            ax.text(xi, r["unique aircraft"] + 1.5, f"{int(r['unique aircraft'])}", ha="center", fontsize=6.5, color=INK2)
    ax.plot(t.index, t["patents acquired"], color=INK, lw=2, marker="o", ms=3.5, label="patents acquired (all 1 639)")
    first_incomplete = int(t.index[~t["complete"]].min())
    ax.axvline(first_incomplete - 0.5, color=INK, lw=0.8, ls="--")
    ax.text(first_incomplete - 0.4, ax.get_ylim()[1] * 0.97, f"incomplete: within {p90:.0f} years\n(90th-pct lag) of the snapshot",
            va="top", fontsize=7, color=INK2)
    ax.set_xticks(list(t.index), [("≤2005" if y == 2005 else str(y)) for y in t.index], rotation=45, fontsize=7.5)
    ax.set_ylabel("unique aircraft (bars) · patents acquired (line)")
    ax.legend(loc="upper left", fontsize=7.5)
    ax.set_title("Filings per priority year, by applicant region; hatched bars are years still filling")
    _hgrid(ax, "y")
    return _save(fig, path, SRC + f"; Table 4.1.1; PatSeer snapshot {t.attrs['snapshot']}; 90th-percentile priority-to-publication lag = {p90:.0f} years.",
                 "Bars: representative unique aircraft by the priority year of their primary record, stacked by applicant "
                 "region (region hatches survive black and white). Line: every acquired patent. A year is drawn hatched "
                 "while the snapshot is less than the 90th-percentile lag after its end: those bars will still grow.")


def fig_dominant_design(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.dominant_design(v)
    fig, axes = plt.subplots(1, 3, figsize=(W, 3.1), gridspec_kw={"wspace": 0.4})
    x = np.arange(len(WINDOW_NAMES))
    ax = axes[0]
    for lvl, col, mk in (("A0c", CAT[0], "o"), ("A1t", CAT[1], "s")):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, sub["top share"], marker=mk, lw=2, ms=5, color=col, label=f"{lvl}: top archetype share")
    ax.axhline(0.5, color=INK, lw=1, ls="--")
    ax.text(0.05, 0.515, "more than half, two windows running", fontsize=6.5, color=INK2)
    ax.set_ylim(0, 0.6)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("Cond. 1: top archetype share", fontsize=9)
    ax.legend(fontsize=6.5, loc="center right")
    for ax, lvl in zip(axes[1:], ("A0c", "A1t")):
        sub = t[t["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, sub["D2 permutation low"], sub["D2 permutation high"], color=GRID, alpha=0.9,
                        label="permutation band (labels shuffled across windows)")
        ax.errorbar(x, sub["D2"], yerr=[sub["D2"] - sub["D2 low"], sub["D2 high"] - sub["D2"]], marker="o", ms=4.5,
                    lw=1.8, capsize=2, color=CAT[0] if lvl == "A0c" else CAT[1], label="observed ²D, rarefied (95 %)")
        ax.set_title(f"Cond. 2: ²D at {lvl} vs band", fontsize=9)
        ax.set_ylim(0)
        if lvl == "A0c":
            h, l = ax.get_legend_handles_labels()
            fig.legend(h, l, fontsize=6.8, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2)
            fig.subplots_adjust(bottom=0.3)
    for ax in axes:
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    fig.suptitle("The dominant-design test fixed in the Preliminary Analysis (5.7), applied per window",
                 x=0.01, y=1.04, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.2; rarefied to 40 aircraft; 200 permutations; Q (condition 3) needs the Gower distance and is not yet computed.",
                 "Left: a dominant design needs the top archetype above the dashed line in two consecutive complete windows; "
                 "A0c = class × propulsor bin, A1t = class × wings × tilting. Middle and right: the window is more concentrated "
                 "than chance only where the observed ²D falls below the grey band.")


def fig_class_configs(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.class_configs(v)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.2), gridspec_kw={"wspace": 0.3})
    x = np.arange(len(WINDOW_NAMES))
    for code, sub in t.groupby("code", sort=False):
        sub = sub.set_index("window").reindex(WINDOW_NAMES)
        mk, ls = _cs(code)
        ax.plot(x, sub["modal share"], marker=mk, ls=ls, lw=2, ms=5, color=_color(code), label=f"{code}")
        ax2.plot(x, sub["configurations"] / sub["aircraft"], marker=mk, ls=ls, lw=2, ms=5, color=_color(code), label=code)
    for a in (ax, ax2):
        a.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=7.5)
        a.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        _hgrid(a, "y")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 0.5)
    ax.set_title("Share of the class's modal configuration", fontsize=9.5)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("distinct configurations per aircraft")
    ax2.set_title("How many configurations the class holds", fontsize=9.5)
    ax2.legend(fontsize=7.5, loc="lower left", ncol=2)
    fig.suptitle("Within-class convergence, four largest classes: configuration = propulsor bin × ducted × booms × tail",
                 x=0.01, y=1.03, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.3 names the modal configuration per class and window; windows with fewer than 5 aircraft of the class blank.",
                 "Left: the share of the class's aircraft in its single most common configuration; a class settling on one "
                 "design would climb. Right: distinct configurations divided by aircraft; 1.0 means every aircraft is its own "
                 "configuration, a falling line means designs repeat.")


def fig_dimension_drift(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.dimension_drift(v)
    metrics_ = [("median propulsor units", "median units", None), ("ducted share", "ducted share", 1),
                ("tilting share", "tilting share", 1), ("boom share", "boom share", 1)]
    fig, axes = plt.subplots(1, 4, figsize=(W, 2.7), gridspec_kw={"wspace": 0.45})
    x = np.arange(len(WINDOW_NAMES))
    for ax, (col, title, top) in zip(axes, metrics_):
        for code, sub in t.groupby("code", sort=False):
            sub = sub.set_index("window").reindex(WINDOW_NAMES)
            mk, ls = _cs(code)
            ax.plot(x, sub[col], marker=mk, ls=ls, lw=1.8, ms=4, color=_color(code), label=code)
        ax.set_title(title, fontsize=8.5)
        ax.set_xticks(x, _win_labels(WINDOW_NAMES), fontsize=6.3, rotation=45)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
        if top:
            ax.set_ylim(0, 1.05)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        else:
            ax.set_ylim(0)
        _hgrid(ax, "y")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Dimension drift inside the four largest classes, per window", x=0.01, y=1.06, ha="left",
                 fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; Table 4.1.4; windows with fewer than 5 aircraft of the class left out.",
                 "One line per class. Substitution shows here before a class label changes: a class whose rotor count "
                 "climbs, or whose ducted share falls, is changing what it is while keeping its name.")


def fig_transitions(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.transitions(v)
    t["from"] = t["from"].map(_fold); t["to"] = t["to"].map(_fold)
    order = [c for c in ARCH_ORDER + ["Other"]]
    mat = t.groupby(["from", "to"])["pairs"].sum().unstack(fill_value=0).reindex(index=order, columns=order, fill_value=0)
    share = mat.div(mat.sum(axis=1).replace(0, np.nan), axis=0)
    fig, ax = plt.subplots(figsize=(W * 0.72, 4.6))
    _heat(ax, share.fillna(0), counts=mat, vmax=1.0)
    ax.set_xticks(range(len(order)), order, rotation=0)
    ax.set_yticks(range(len(order)), [f"{c}  ({int(mat.loc[c].sum())})" for c in order])
    ax.set_xlabel("class of the firm's next aircraft")
    ax.set_ylabel("class of the earlier aircraft")
    ax.set_title(f"Within-firm successions: {t.attrs['pairs']} consecutive pairs in {t.attrs['firms']} named firms; "
                 f"{t.attrs['same share']:.0%} stay in class", fontsize=9)
    return _save(fig, path, SRC + "; Table 4.2.4; each named firm's aircraft in priority order, every consecutive pair counted once.",
                 "Rows are the earlier aircraft's class and sum to 100 %; the number is pairs. The diagonal is a firm "
                 "repeating its class; an off-diagonal cell is what firms move to next. Colour is the row share.")


def fig_ip_strategy(ds: Dataset, v: pd.DataFrame, path: Path) -> Path:
    f = la_tables.ip_strategy(ds, v)
    c = la_tables.ip_by_class(v)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.9), gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.45})
    for _, r in f.iterrows():
        ax.scatter(r["unique aircraft"], r["patents per aircraft"], s=25 + 3 * r["mean forward citations"],
                   color=REGION_COLOR.get(r["region"], OTHER), alpha=0.85, edgecolor=SURFACE, lw=0.8)
        ax.annotate(r["firm"], (r["unique aircraft"], r["patents per aircraft"]), fontsize=6.3, xytext=(4, 2), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xticks([5, 10, 20, 50], ["5", "10", "20", "50"])
    ax.set_xlabel("unique aircraft (log)")
    ax.set_ylabel("representative patents per aircraft")
    ax.axhline(1, color=GRID, lw=1)
    ax.set_title("Depth against breadth, firms with 5+ aircraft\n(bubble = mean forward citations; colour = region)", fontsize=8.8)
    _hgrid(ax, "both")
    handles = [matplotlib.patches.Patch(color=REGION_COLOR[r], label=r) for r in REGIONS]
    ax.legend(handles=handles, fontsize=6.5, loc="upper right")
    cc = c[c["patents"] >= 10]
    y = np.arange(len(cc))
    codes = [next((k for k, nm in metrics.ARCH_NAMES.items() if nm == n), n) for n in cc["class"]]
    ax2.barh(y - 0.2, cc["median claims"], height=0.38, color=BLUE(0.45), label="median claims")
    ax2.barh(y + 0.2, cc["mean forward citations"], height=0.38, color=BLUE(0.85), label="mean forward citations")
    ax2.set_yticks(y, [f"{code} ({int(n)})" for code, n in zip(codes, cc["patents"])], fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_title("Claims and citations per class (primary patents)", fontsize=8.8)
    ax2.legend(fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2, "x")
    return _save(fig, path, SRC + "; PatSeer claim_count, forward_citations, family_size; Tables 4.2.5a/b.",
                 "Left: above the line a firm files more than one patent per aircraft (protecting each design in depth); "
                 "far right it files many different aircraft (exploring). Right: how much each class is claimed and cited; "
                 "citations favour older patents, so read them with the median priority year in the table.")


def fig_specialisation(v: pd.DataFrame, path: Path) -> Path:
    lq, counts = la_tables.specialisation(v)
    mat = lq.copy()
    mat.index = [f"{a}  ({int(n)})" for a, n in zip(lq.index, counts.sum(axis=1))]
    fig, ax = plt.subplots(figsize=(W * 0.72, 0.22 * len(mat) + 1.4))
    im = ax.imshow(np.log2(mat.to_numpy(dtype=float).clip(0.25, 4)), cmap="RdBu_r", vmin=-2, vmax=2, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iat[i, j]; n = counts.iat[i, j]
            ax.text(j, i, f"{val:.1f}\n({int(n)})" if n else "–", ha="center", va="center", fontsize=6.3,
                    color="white" if abs(np.log2(max(val, 0.25))) > 1.1 else INK)
    ax.set_xticks(range(mat.shape[1]), mat.columns, fontsize=8)
    ax.set_yticks(range(mat.shape[0]), mat.index, fontsize=7)
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02, ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_yticklabels(["¼", "½", "1", "2", "4"], fontsize=7)
    cb.set_label("specialisation index (region share ÷ overall share)", fontsize=7.5)
    ax.set_title("Regional specialisation by archetype (A0c, 5+ aircraft): red = over-represented, blue = under", fontsize=9)
    return _save(fig, path, SRC + "; Table 4.3.3; three main regions only.",
                 "Each cell: the archetype's share of the region's aircraft divided by its share of all aircraft, count in "
                 "brackets. 1 = as everywhere; 2 = twice the overall share. Read a column for what a region leans to; a row "
                 "for where an archetype is concentrated.")


def fig_industry_by_class(v: pd.DataFrame, path: Path) -> Path:
    t = la_tables.industry_by_class(v).set_index("class")
    tab = t.drop(columns="aircraft")
    tab = tab[tab.sum().sort_values(ascending=False).index]
    share = tab.div(tab.sum(axis=1), axis=0)
    share.index = [f"{i} (n {int(n)})" for i, n in zip(t.index, t["aircraft"])]
    cols = list(share.columns)
    pal = {c: (OTHER if c == "General_Unspecified" else CAT[i % len(CAT)]) for i, c in enumerate([c for c in cols if c != "General_Unspecified"])}
    pal["General_Unspecified"] = OTHER
    fig, ax = plt.subplots(figsize=(W, 4.0))
    _stack_h(ax, share, pal, min_label=0.1)
    ax.set_title("Industry named in the patent text, by class (text model, 03a)", fontsize=9.5)
    ax.legend([c.replace("_", " / ") for c in cols], fontsize=6.5, loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1)
    return _save(fig, path, SRC + "; identity industry_primary (text classifier, one value per patent); Table 5.5.",
                 "Each bar is 100 % of the class's aircraft. Grey is 'general / unspecified', half the corpus: patents "
                 "rarely name a mission. Read the coloured part only.")


def fig_examination(v: pd.DataFrame, path: Path) -> Path:
    to = la_tables.examination(v, "pub_office").set_index("pub_office")
    tc = la_tables.examination(v, "topType").set_index("topType")
    pal = {"granted, in force": CAT[2], "pending": BLUE(0.4), "lapsed (non-payment)": CAT[3], "expired": OTHER,
           "withdrawn": CAT[1], "refused": CAT[7]}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.6), gridspec_kw={"width_ratios": [0.8, 1.2], "wspace": 0.45})
    code_of = {nm: k for k, nm in metrics.ARCH_NAMES.items()}
    for a, t, title in ((ax, to, "by publication office"), (ax2, tc, "by class")):
        tab = t.drop(columns="patents")
        share = tab.div(tab.sum(axis=1), axis=0)
        share.index = [f"{code_of.get(i, i)} (n {int(n)})" for i, n in zip(t.index, t["patents"])]
        _stack_h(a, share, pal, min_label=0.12)
        a.set_title(title, fontsize=9.5)
        a.tick_params(axis="y", labelsize=7.5)
    ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(1.3, -0.1), ncol=6)
    fig.suptitle("Legal status of the primary patents at the snapshot", x=0.01, y=1.02, ha="left", fontsize=10, fontweight="bold")
    return _save(fig, path, SRC + "; PatSeer legal_status_raw at the 2026-06 snapshot; Tables 5.6a/b.",
                 "Examination outcome as a proxy for regulatory friction on the IP side: refused and withdrawn shares "
                 "differ by office far more than by class. Pending is high where filings are recent (CN, WO).")

# ------------------------------------------------------- reuse of atlas ----
#: atlas figures reused as they are: name -> atlas function
ATLAS_REUSE: Dict[str, Callable] = {
    "atlas_removal": atlas.fig_removal,
    "atlas_duplicates": atlas.fig_duplicates,
    "atlas_figure_approval": atlas.fig_figure_approval,
    "atlas_years": atlas.fig_years,
    "atlas_region": atlas.fig_region,
    "atlas_filers": atlas.fig_filers,
    "atlas_state_by_arch": atlas.fig_state_by_arch,
    "atlas_arch_gt": atlas.fig_arch_gt,
    "atlas_arch_time": atlas.fig_arch_time,
    "atlas_powertrain": atlas.fig_powertrain,
    "atlas_fields": atlas.fig_fields,
    "atlas_fill": atlas.fig_fill,
    "atlas_flagship": atlas.fig_flagship,
    "atlas_units": atlas.fig_units,
    "atlas_design_heatmaps": atlas.fig_design_heatmaps,
}


#: portrait sizes for the reused atlas figures (they are drawn at ``atlas.PAGE``, patched per call)
ATLAS_SIZE: Dict[str, tuple] = {
    "atlas_removal": (W, 4.4), "atlas_duplicates": (W, 3.8), "atlas_figure_approval": (W, 4.4),
    "atlas_years": (W, 4.0), "atlas_region": (W, 4.8), "atlas_filers": (W, 6.2), "atlas_state_by_arch": (W, 4.4),
    "atlas_arch_gt": (W, 5.6), "atlas_arch_time": (W, 4.0), "atlas_powertrain": (W, 4.6), "atlas_fields": (W, 5.6),
    "atlas_fill": (W, 5.4), "atlas_flagship": (W, 5.0), "atlas_units": (W, 5.4), "atlas_design_heatmaps": (W, 6.2),
}


def _atlas(fn: Callable, ds: Dataset, av: pd.DataFrame, n: Dict, path: Path, size: tuple = (W, 5.0)) -> Path:
    page = atlas.PAGE
    atlas.PAGE = size
    try:
        with plt.rc_context({**STYLE, "font.size": 8.5, "axes.titlesize": 9.5, "legend.fontsize": 7.5}):
            fig, number, title = fn(ds, av, n)
            if len(fig.axes) > 1:            # side-by-side panels: wrap titles so they cannot collide
                import textwrap
                for ax in fig.axes:
                    for loc in ("left", "center"):
                        t = ax.get_title(loc=loc)
                        if t and len(t) > 34:
                            ax.set_title("\n".join(textwrap.wrap(t, 34)), fontsize=9, loc=loc)
            _atlas_save(fig, path)
    finally:
        atlas.PAGE = page
    return path


def _atlas_save(fig, path: Path) -> None:
    with plt.rc_context(STYLE):
        if getattr(fig, "_atlas_note", None):
            atlas._stamp(fig, *fig._atlas_note)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
        plt.close(fig)


def render_all(ds: Dataset, out_dir: Path, partial_window_start: int = 2024, **_) -> Dict[str, Path]:
    """Draw every figure of the Labelling Analysis into ``out_dir/figures``; returns {name: path}."""
    out = Path(out_dir) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    n = numbers.live(ds, partial_window_start)
    v = la_tables.base(ds)
    av = atlas._variants(ds)
    paths: Dict[str, Path] = {}
    # schemes reused from the Preliminary Analysis
    paths["fig_02_refinement_funnel"] = figures.refinement_funnel_svg(n, out / "fig_02_refinement_funnel.svg")
    paths["design_space_cards"] = design_space_cards_svg(n, out / "design_space_cards.svg")
    for name, src in figures.CODEBOOK_DRAWINGS.items():
        paths[name] = Path(shutil.copyfile(src, out / src.name))
    for name, fn in ATLAS_REUSE.items():
        paths[name] = _atlas(fn, ds, av, n, out / f"{name}.png", ATLAS_SIZE.get(name, (W, 5.0)))
    jobs = {
        "firm_weighted": lambda p: fig_firm_weighted(v, p),
        "spans_by_firm": lambda p: fig_spans_by_firm(ds, v, p),
        "two_counts": lambda p: fig_two_counts(ds, p),
        "lead_lag": lambda p: fig_lead_lag(v, p),
        "class_cycles": lambda p: fig_class_cycles(v, p),
        "hill": lambda p: fig_hill(v, p),
        "zones": lambda p: fig_zones(v, p),
        "abandonment": lambda p: fig_abandonment(v, p),
        "region_grid": lambda p: fig_region_grid(v, p),
        "country_class": lambda p: fig_country_class(v, p),
        "coverage": lambda p: fig_coverage(v, p),
        "filers_over_time": lambda p: fig_filers_over_time(v, p),
        "firm_tiles": lambda p: fig_firm_tiles(v, p),
        "proximity_region": lambda p: fig_proximity_region(ds, v, p),
        "ari": lambda p: fig_ari(v, p),
        "mission": lambda p: fig_mission(v, p),
        "filings_per_year": lambda p: fig_filings_per_year(ds, v, p),
        "dominant_design": lambda p: fig_dominant_design(v, p),
        "class_configs": lambda p: fig_class_configs(v, p),
        "dimension_drift": lambda p: fig_dimension_drift(v, p),
        "transitions": lambda p: fig_transitions(v, p),
        "ip_strategy": lambda p: fig_ip_strategy(ds, v, p),
        "specialisation": lambda p: fig_specialisation(v, p),
        "industry_by_class": lambda p: fig_industry_by_class(v, p),
        "examination": lambda p: fig_examination(v, p),
    }
    with plt.rc_context(STYLE):
        for name, job in jobs.items():
            paths[name] = job(out / f"{name}.png")
    return paths
