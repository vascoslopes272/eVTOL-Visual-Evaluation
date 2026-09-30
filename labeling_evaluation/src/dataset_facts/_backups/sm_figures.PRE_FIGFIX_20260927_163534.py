"""The six small panels of "New questions these measures raise" — the BRIEF's own figures.

One panel per question, and nothing else on it: the question names a measure, the panel draws
that measure, and the two sentences under it say why it is a question and what would settle it.
They exist because the section used to point at figures printed twenty pages earlier ("panel
(iii) of Figure 8", "a cell of Figure 7") and a reader taking the section to a supervisor cannot
flip pages while arguing.

NOTHING HERE IS A NEW ANALYSIS. Five of the six panels are drawn from the tables the full render
already wrote into ``tables/`` — ``la_duct_units``, ``la_dd_q``, ``la_zones``, ``la_cohorts`` +
``la_class_cycles`` + ``la_cohort_mix``, ``a2_d15_trl_status`` — read back from their CSVs at
render time, so a number on a panel and the same number in the full document cannot diverge. The
sixth needs the shape of a distribution rather than its median, which no table carries, and gets
it from the two functions the printed table itself is built with
(:func:`la_tables.cohort_citation_rank` and :func:`la_tables.ari_firms`), so its two medians
reproduce the ``la_ari_gap`` row exactly.

NOTHING HERE TOUCHES THE FULL DOCUMENT. This module is imported by ``scripts/render_summary.py``
alone; ``la_figures`` is imported for its helpers (the black-and-white pass, the width fit, the
declutter pass, the window labels, the palette) and is never modified, so
``LABELLING_ANALYSIS.md`` and every figure under it render byte-for-byte as before.

HOUSE RULES THAT DO APPLY: 7 pt floor, 200 dpi, 7.09 in text width, readable in black and white
(every colour also carries a hatch or a dash), and every panel prints the base it rests on — the
n is on the tick, in the axis label or beside the bar, never left to the caption. The two that do
NOT apply are the Source / How-to-read stamp and the class legend: these are plain bar and line
charts with labelled axes, which the standing rule exempts, and the brief prints the source under
each panel as the grey line ``sm_index.TAKEAWAY`` writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import la_figures as _lf
from . import la_tables as _lt
from .atlas import BLUE, CAT, GRID, INK, INK2, MUTED, STYLE, SURFACE, _hgrid
from .la_tables import WINDOW_NAMES

#: the six panels, in the order the six questions are printed.
NAMES = ["sm_duct_bands", "sm_weighting", "sm_archetype_filers",
         "sm_tw_entry", "sm_trl_tracked", "sm_cite_rank",
         "sm_duct_count", "sm_entry_all", "sm_class_configs",
         "sm_joints_per_unit", "sm_duct_conditional", "sm_family_yearly", "sm_dd_conditions",
         "sm_duct_merged", "sm_propulsion_compact"]

#: a panel is a single measure on a small canvas: one point smaller than the full document's
#: body size everywhere, still well clear of the 7 pt floor.
PANEL_STYLE = {**STYLE, "font.size": 8.0, "axes.titlesize": 9.0, "axes.titlepad": 6,
               "legend.fontsize": 7.5}

#: the light grey a "context" bar is drawn in. Deliberately NOT ``atlas.OTHER``: that colour is
#: in the black-and-white table and would put a hatch on every context bar in the document.
CONTEXT = "#c9c8c3"

W = 7.09          # the document's text width, inches


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _num(frame: pd.DataFrame, col: str) -> pd.Series:
    """One column of a table read back from CSV, as numbers.

    ``render_summary.load_tables`` reads with ``keep_default_na=False`` — several option ids in
    this corpus are literally "NA" or "None" — so a numeric column with one blank cell comes
    back as text. Everything drawn here goes through this function.
    """
    return pd.to_numeric(frame[col], errors="coerce")


def _save(fig, path: Path) -> Path:
    """The house save, minus the stamp and the panel marks.

    Reuses ``la_figures``' own passes so a panel obeys the same rules as a figure: hatches and
    dashes keyed to the colours (:func:`la_figures._bw`), titles re-wrapped to the space they
    own, the canvas shrunk until the drawn content is exactly the text width, colliding labels
    moved or hidden. What is left out is :func:`la_figures._mark_keeping_width` — a two-panel
    figure would grow an "(i)"/"(ii)" line above each title, and these panels are too short to
    spend it — and :func:`la_figures._stamp`.
    """
    with plt.rc_context(PANEL_STYLE):
        _lf._bw(fig)
        _lf._wrap_texts(fig)
        _lf._fit_width(fig)
        _lf._declutter(fig)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=_lf.DPI, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def _pct_axis(ax, top: float) -> None:
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, top)
    _hgrid(ax, "y")


def _bar_pct(ax, bars, values, size=7.5, dy=0.012, color=INK) -> None:
    for b, val in zip(bars, values):
        if np.isfinite(val):
            ax.text(b.get_x() + b.get_width() / 2, val + dy, f"{val:.0%}",
                    ha="center", va="bottom", fontsize=size, color=color)


# --------------------------------------------------------------------------
# 1 — ducting returns at nine propulsive units and more
# --------------------------------------------------------------------------
def panel_duct(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """The five propulsive-unit bands, the share of each band's aircraft carrying a ducted
    unit, and the corpus line across them. Base: the aircraft under each band.

    The same rows the full document prints as ``tables/la_duct_units.csv`` and draws as panel
    (iii) of its propulsive-units figure, cut down to the one measure the question is about.
    """
    t = tables["la_duct_units"]
    t = t[t["level"].eq("propulsive units")].copy()
    t["_n"] = _num(t, "aircraft")
    t["_s"] = _num(t, "share ducted")
    bands = t[t["group"].ne("all bands") & t["reported"].astype(str).eq("True")]
    allrow = t[t["group"].eq("all bands")]
    overall = float(allrow["_s"].iloc[0])
    total = int(allrow["_n"].iloc[0])

    fig, ax = plt.subplots(figsize=(W, 2.25))
    x = np.arange(len(bands))
    bars = ax.bar(x, bands["_s"], width=0.62, color=BLUE(0.78), zorder=3)
    _bar_pct(ax, bars, bands["_s"].tolist())
    ax.axhline(overall, color=INK, lw=1.1, ls="--", zorder=4)
    # clear of every bar, at the height of the line it names
    ax.text(len(bands) - 0.35, overall, f"every band\ntogether, {overall:.0%}",
            ha="left", va="center", fontsize=7.5, color=INK2, zorder=5, linespacing=1.2)
    ax.set_xticks(x, [f"{g}\nn {int(n)}" for g, n in zip(bands["group"], bands["_n"])], fontsize=8)
    ax.set_xlim(-0.65, len(bands) + 0.5)
    ax.set_xlabel(f"propulsive units per aircraft ({total} aircraft fall in a band)", fontsize=8)
    ax.set_ylabel("aircraft with at least\none ducted unit", fontsize=8)
    _pct_axis(ax, float(bands["_s"].max()) + 0.10)
    ax.set_title("Ducting against rotor count: commonest at the fewest units and at the most",
                 fontsize=9)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2 — condition 3 under both weightings
# --------------------------------------------------------------------------
def panel_weighting(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Condition 3's ΔQ per window against its permutation band, under BOTH weightings, at both
    archetype levels. Base: the aircraft of each window, on the tick.

    The full document draws this figure under the main (subsystem) weighting only and reports
    the uniform one in a table, which is exactly what the question objects to: the condition
    fires under one weighting and not the other, so the two have to be on one panel. A ringed
    point is a window whose ΔQ falls below the lower edge of its OWN band — the condition met.
    """
    t = tables["la_dd_q"].copy()
    for c in ("Q", "ΔQ", "ΔQ permutation low", "ΔQ permutation high", "aircraft"):
        t[c] = _num(t, c)
    main, alt = _lt.Q_WEIGHTINGS
    levels = [l for l in dict.fromkeys(t["level"])]
    x = np.arange(len(WINDOW_NAMES))
    fig, axes = plt.subplots(1, len(levels), figsize=(W, 2.1), gridspec_kw={"wspace": 0.26})
    axes = np.atleast_1d(axes)
    lo = float(min(t["ΔQ"].min(), t["ΔQ permutation low"].min()))
    hi = float(max(t["ΔQ"].max(), t["ΔQ permutation high"].max()))
    pad = (hi - lo) * 0.16

    for k, (ax, lvl) in enumerate(zip(axes, levels)):
        sub = t[t["level"].eq(lvl)]
        sm = sub[sub["weighting"].eq(main)].set_index("window").reindex(WINDOW_NAMES)
        su = sub[sub["weighting"].eq(alt)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, sm["ΔQ permutation low"], sm["ΔQ permutation high"], color=GRID,
                        alpha=0.95, zorder=1,
                        label=f"permutation band, {main} weighting")
        ax.plot(x, su["ΔQ permutation low"], color=MUTED, lw=0.9, ls=":", zorder=2,
                label=f"band edges, {alt} weighting")
        ax.plot(x, su["ΔQ permutation high"], color=MUTED, lw=0.9, ls=":", zorder=2)
        ax.axhline(0, color=MUTED, lw=0.8, ls="-", zorder=2)
        ax.plot(x, sm["ΔQ"], marker="o", ms=4.2, lw=1.7, color=INK, zorder=4,
                label=f"ΔQ, {main} weighting (main)")
        ax.plot(x, su["ΔQ"], marker="^", ms=4.2, lw=1.4, color=MUTED, ls="--", zorder=4,
                label=f"ΔQ, {alt} weighting")
        for s_, col in ((sm, INK), (su, MUTED)):
            below = s_[s_["below band"].astype(str).eq("True")]
            if len(below):
                ax.plot([WINDOW_NAMES.index(w) for w in below.index], below["ΔQ"], "o", ms=9.5,
                        mfc="none", mec=INK, mew=1.5, zorder=5,
                        label="below its own band: condition 3 fires" if col is INK else None)
        # the crossing itself, in numbers: the one window where the two weightings disagree
        w23 = WINDOW_NAMES.index("2020-23")
        minus = lambda z: f"{z:+.3f}".replace("-", "−")
        ax.annotate(f"{minus(sm['ΔQ'].iloc[w23])}\nbelow", (w23, sm["ΔQ"].iloc[w23]),
                    textcoords="offset points", xytext=(-7, -3), ha="right", va="top",
                    fontsize=7, color=INK)
        ax.annotate(f"{minus(su['ΔQ'].iloc[w23])}\ninside", (w23, su["ΔQ"].iloc[w23]),
                    textcoords="offset points", xytext=(7, 4), ha="left", va="bottom",
                    fontsize=7, color=INK2)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_xticks(x, [f"{_lf.WIN_SHORT.get(w, w)}\nn {int(sm['aircraft'].get(w, 0))}"
                          for w in WINDOW_NAMES], fontsize=7.5)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
        ax.set_title(f"at {lvl}", fontsize=8.5)
        if k == 0:
            ax.set_ylabel("ΔQ against the two\nearliest windows", fontsize=8)
            h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 0.015), ncol=3,
               handlelength=1.8, columnspacing=1.2)
    fig.suptitle("Condition 3 under both weightings: the fall below the permutation band happens "
                 "under one of them only", x=0.0, y=1.02, ha="left", fontsize=9,
                 fontweight="bold")
    fig.subplots_adjust(bottom=0.32)
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3 — CVT · 5-6 against the other archetypes of its size
# --------------------------------------------------------------------------
#: an archetype is read here only at this many aircraft or more — the cut the question names
#: ("the lowest of any archetype in the corpus with twenty aircraft or more").
ZONE_MIN = 20


def panel_archetype_filers(tables: Dict[str, pd.DataFrame], path: Path, ds=None) -> Path:
    """Distinct filers per aircraft, for every archetype holding :data:`ZONE_MIN` aircraft or
    more, CVT · 5-6 marked against the rest and CVT · 4 marked beside it. Base: the aircraft of
    each archetype, printed on its row.

    The zones table is graded weak as a table — it is a wide frame of twelve columns read for
    one of them. This is the one column, cut to the one comparison the question makes.
    """
    t = tables["la_zones"].copy()
    t["_n"] = _num(t, "aircraft")
    t["_f"] = _num(t, "filers")
    t["_fpa"] = _num(t, "filers per aircraft")
    t = t[t["_n"].ge(ZONE_MIN)].sort_values("_fpa")
    focus, neighbour = "CVT · 5-6", "CVT · 4"
    colors = [CAT[1] if a == focus else CAT[0] if a == neighbour else CONTEXT
              for a in t["archetype"]]
    fig, ax = plt.subplots(figsize=(W, 2.95))
    y = np.arange(len(t))
    bars = ax.barh(y, t["_fpa"], height=0.68, color=colors, zorder=3)
    for b, a in zip(bars, t["archetype"]):
        if a == focus:
            b.set_hatch("////")
        elif a == neighbour:
            b.set_hatch("....")
    # 2026-09-26 (author, C71): say on the bar what "few filers" is made of — many small
    # filers, or one large one. Read from the aircraft frame (the filer of each aircraft, as
    # la_tables.zones counts it), never typed.
    split = ""
    if ds is not None:
        fv = _lt.base(ds)
        held = fv[fv["archetype"].eq(focus)].groupby("filer_id").size().sort_values(ascending=False)
        if len(held):
            top = str(held.index[0])
            top = "one patent's inventor" if top.startswith("patent:") else top
            split = (f"\n{top} holds {int(held.iloc[0])} of the {int(held.sum())}; "
                     f"{int((held == 1).sum())} filers hold one each")
    for b, (a, fpa, n_, f_) in zip(bars, zip(t["archetype"], t["_fpa"], t["_n"], t["_f"])):
        lead = a == focus and split
        ax.text(b.get_width() + 0.015, b.get_y() + b.get_height() / 2 + (0.36 if lead else 0),
                f"{fpa:.2f}   ({int(f_)} filers / {int(n_)} aircraft)" + (split if lead else ""),
                va="top" if lead else "center", ha="left", fontsize=7.2, linespacing=1.25,
                color=INK if a == focus else INK2, fontweight="bold" if a == focus else "normal")
    ax.set_yticks(y, [str(a).replace(" · n/a (no M3 card)", "") for a in t["archetype"]], fontsize=7.5)
    ax.set_ylim(-1.5 if split else -0.7, len(t) - 0.3)
    ax.set_xlim(0, float(t["_fpa"].max()) * 1.42)
    ax.set_xlabel("distinct filers per aircraft (1.00 = every aircraft a different filer)",
                  fontsize=8)
    _hgrid(ax, "x")
    ax.set_title(f"How many different filers each archetype of {ZONE_MIN}+ aircraft rests on: "
                 f"{focus} is the lowest in the corpus", fontsize=9)
    _lf._panel_note(ax, ax, f"Unit: C·U archetype (class + propulsive-unit band), the {len(t)} with "
                    f"{ZONE_MIN}+ unique aircraft\nSource: human labelling (class, units) · "
                    "PatSeer (applicant → filer)")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 4 — Tilt Wing: the aircraft against the firms arriving
# --------------------------------------------------------------------------
#: a window's entrant share is printed, but marked, below this many firms entering with the
#: class: three firms is an anecdote, and the panel says so on the tick rather than in prose.
THIN_FIRMS = 5


def panel_tw_entry(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Tilt Wing's share of each window's AIRCRAFT against its share of that window's ENTERING
    FIRMS. Base: the aircraft and the firms entering, both on the tick; the firms entering with
    Tilt Wing printed on the bar.

    Two units on one panel on purpose — the question is the gap between them, not the level of
    either. The aircraft share is rebuilt from the class's own window shares in
    ``la_class_cycles`` against the window totals in ``la_cohort_mix``, and reproduces the
    ``share of aircraft`` column of ``la_cohort_mix`` exactly where that table reports the
    class; the entrant share is ``la_cohorts``, which reports every window.
    """
    cyc = tables["la_class_cycles"]
    coh = tables["la_cohorts"].copy()
    mix = tables["la_cohort_mix"].copy()
    cls_name, code = "Tilt Wing", "TW"
    row = cyc[cyc["class"].eq(cls_name)].iloc[0]
    n_class = float(pd.to_numeric(row["aircraft"], errors="coerce"))
    coh = coh.set_index("window").reindex(WINDOW_NAMES)
    mix["_air"] = _num(mix, "aircraft in the window")
    win_air = mix.groupby("window")["_air"].max().reindex(WINDOW_NAMES)

    share_air, share_ent, n_ent, n_air, ent, air = [], [], [], [], [], []
    for w in WINDOW_NAMES:
        air_c = round(float(pd.to_numeric(row[w], errors="coerce")) * n_class)
        tot_a = float(win_air.get(w, np.nan))
        e = float(pd.to_numeric(coh.loc[w, code], errors="coerce"))
        tot_e = float(pd.to_numeric(coh.loc[w, "firms entering"], errors="coerce"))
        share_air.append(air_c / tot_a if tot_a else np.nan)
        share_ent.append(e / tot_e if tot_e else np.nan)
        n_air.append(int(tot_a))
        n_ent.append(int(tot_e))
        ent.append(int(e))
        air.append(int(air_c))

    fig, ax = plt.subplots(figsize=(W, 2.35))
    x = np.arange(len(WINDOW_NAMES))
    b1 = ax.bar(x - 0.19, share_air, width=0.36, color=CONTEXT, zorder=3,
                label="share of the window's aircraft")
    b2 = ax.bar(x + 0.19, share_ent, width=0.36, color=CAT[0], zorder=3,
                label="share of the window's entering firms")
    for b in b2:
        b.set_hatch("////")
    # every bar carries its own numerator; the tick under it carries the denominator
    for bars, vals, counts, word in ((b1, share_air, air, "aircraft"), (b2, share_ent, ent, "firm")):
        for b, val, c in zip(bars, vals, counts):
            if np.isfinite(val):
                ax.text(b.get_x() + b.get_width() / 2, val + 0.004,
                        f"{val:.0%}\n{c} {word}{'s' if c != 1 and word == 'firm' else ''}",
                        ha="center", va="bottom", fontsize=7, color=INK, linespacing=1.1)
    ticks = []
    for w, na, ne, e in zip(WINDOW_NAMES, n_air, n_ent, ent):
        mark = " ‡" if e < THIN_FIRMS else ""
        ticks.append(f"{_lf.WIN_SHORT.get(w, w)}\n{na} aircraft\n{ne} firms{mark}")
    ax.set_xticks(x, ticks, fontsize=7.5)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
    _pct_axis(ax, float(np.nanmax(share_air + share_ent)) + 0.085)
    ax.set_ylabel(f"{cls_name}'s share\nof the window", fontsize=8)
    ax.set_xlabel(f"‡ fewer than {THIN_FIRMS} firms entered the corpus with {cls_name} in that "
                  f"window", fontsize=7.5)
    ax.legend(fontsize=7.5, loc="upper left", ncol=1, handlelength=1.6, labelspacing=0.3)
    ax.set_title(f"{cls_name} after its peak: the aircraft fall away, the firms arriving do not",
                 fontsize=9)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 5 — technology readiness: the aircraft, or the public record?
# --------------------------------------------------------------------------
def panel_trl_tracked(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """The whole corpus by technology-readiness band with the untracked aircraft as a band of
    their own, and the same mix over the tracked aircraft alone. Base: printed at the end of
    each bar.

    The point of the question is the band the full document's TRL table cannot show: the
    aircraft no public source follows at all sit at TRL 2 in that table, indistinguishable from
    an aircraft that is followed and has got no further. Splitting them is the whole panel.
    """
    st = tables["a2_d15_trl_status"].copy()
    bands = ["TRL 2", "TRL 3-5", "TRL 6-7", "TRL 8-9"]
    for c in bands + ["unique aircraft"]:
        st[c] = _num(st, c)
    tot = st[st["programme status"].eq("Total")].iloc[0]
    untracked = st[st["programme status"].eq("not tracked")].iloc[0]
    n_all = int(tot["unique aircraft"])
    n_un = int(untracked["unique aircraft"])
    n_tr = n_all - n_un
    # the tracked aircraft: every band of the Total row, less what the untracked row holds
    tracked = [int(tot[c] - untracked[c]) for c in bands]
    rows = [("every aircraft in the corpus", [n_un] + tracked, n_all),
            ("the aircraft the public record follows", tracked, n_tr)]
    labels = ["not tracked by\nthe public record"] + bands
    colors = [CONTEXT, "#b9cfe8", BLUE(0.45), BLUE(0.72), BLUE(0.95)]

    fig, ax = plt.subplots(figsize=(W, 2.25))
    y = np.arange(len(rows))[::-1]
    for yi, (_, vals, base) in zip(y, rows):
        left = 0.0
        pad = [0.0] * len(labels) if len(vals) == len(labels) else [None]
        for k, val in enumerate(vals):
            col = colors[k] if len(vals) == len(labels) else colors[k + 1]
            lab = labels[k] if len(vals) == len(labels) else labels[k + 1]
            share = val / base if base else 0.0
            ax.barh(yi, share, left=left, height=0.52, color=col, zorder=3,
                    label=lab if yi == y[0] else None)
            if share >= 0.045:
                # ink or paper, decided by the fill's own luminance rather than by its
                # position, so the same band is labelled the same way in both bars
                from matplotlib.colors import to_rgb
                lum = sum(c * w for c, w in zip(to_rgb(col), (0.299, 0.587, 0.114)))
                ax.text(left + share / 2, yi, f"{val}", ha="center", va="center", fontsize=7.5,
                        color="#ffffff" if lum < 0.55 else INK, zorder=5)
            left += share
        ax.text(1.008, yi, f"n {base}", va="center", ha="left", fontsize=7.5, color=INK2)
    above_all = int(tot["unique aircraft"] - tot["TRL 2"])
    ax.set_yticks(y, [r[0] for r in rows], fontsize=8)
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.tick_params(axis="x", labelsize=7.5)
    _hgrid(ax, "x")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=5,
              handlelength=1.3, columnspacing=1.0)
    ax.set_title(f"Above TRL 2: {above_all} of {n_all} aircraft, or {above_all} of the {n_tr} "
                 f"any public source follows", fontsize=9)
    fig.subplots_adjust(bottom=0.30)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-24, the brief's review: three new panels
# --------------------------------------------------------------------------
def panel_duct_count(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """How much of an aircraft is ducted, per propulsive-unit band: the share of the band's UNITS
    that run in a duct (bars) beside the share of its AIRCRAFT with any duct (hollow), with the
    median ducted count of the ducting aircraft on the bar. Base: the aircraft of the band."""
    t = tables["la_duct_count"].copy()
    t = t[t["propulsive units"].ne("all bands")]
    for c in ("aircraft", "share with any", "share of units ducted", "share ducting every unit",
              "median ducted units (ducted aircraft)"):
        t[c] = _num(t, c)
    fig, ax = plt.subplots(figsize=(W, 2.35))
    x = np.arange(len(t))
    b1 = ax.bar(x - 0.2, t["share with any"], width=0.38, color="none", edgecolor=INK, lw=1.0, zorder=3,
                label="aircraft with at least one ducted unit")
    b2 = ax.bar(x + 0.2, t["share of units ducted"], width=0.38, color=BLUE(0.78), zorder=3,
                label="of the band's units, the share in a duct")
    _bar_pct(ax, b1, t["share with any"].tolist())
    _bar_pct(ax, b2, t["share of units ducted"].tolist())
    for b, med, ev in zip(b2, t["median ducted units (ducted aircraft)"], t["share ducting every unit"]):
        ax.text(b.get_x() + b.get_width() / 2, 0.012, f"med {med:.0f}\nall {ev:.0%}", ha="center",
                va="bottom", fontsize=6.5, color="#ffffff", zorder=5, linespacing=1.1)
    ax.set_xticks(x, [f"{g}\nn {int(n)}" for g, n in zip(t["propulsive units"], t["aircraft"])], fontsize=8)
    ax.set_xlabel("propulsive units per aircraft · on the bar: median ducted units of the ducting "
                  "aircraft, and the share that duct every unit", fontsize=7.5)
    _pct_axis(ax, float(max(t["share with any"].max(), t["share of units ducted"].max())) + 0.12)
    ax.legend(fontsize=7.5, loc="upper center", ncol=2, handlelength=1.4)
    ax.set_title("Ducting by rotor count, counted in units: at nine and more the aircraft that duct, "
                 "duct nearly everything", fontsize=9)
    return _save(fig, path)


ENTRY_CLASSES = ["SLC", "TR", "CVT", "TW", "MR"]


def panel_entry_all(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """What the firms entering a window arrive with, for the five largest classes: the class's
    share of the window's ENTERING FIRMS (hatched) beside its share of the window's AIRCRAFT
    (grey), one small panel per class. Base on the tick. Generalises the Tilt Wing panel."""
    mix = tables["la_cohort_mix"].copy()
    for c in ("firms entering", "entering with this class", "share of entrants",
              "aircraft in the window", "aircraft of this class", "share of aircraft"):
        mix[c] = _num(mix, c)
    fig, axes = plt.subplots(1, len(ENTRY_CLASSES), figsize=(W, 2.3), sharey=True)
    x = np.arange(len(WINDOW_NAMES))
    top = 0.0
    for ax, code in zip(axes, ENTRY_CLASSES):
        sub = mix[mix["class"].eq(code)].set_index("window").reindex(WINDOW_NAMES)
        ea, aa = sub["share of entrants"].to_numpy(), sub["share of aircraft"].to_numpy()
        top = max(top, float(np.nanmax(np.concatenate([ea, aa]))))
        ax.bar(x - 0.19, aa, width=0.36, color=CONTEXT, zorder=3, label="share of the window's aircraft")
        b2 = ax.bar(x + 0.19, ea, width=0.36, color=CAT[0], zorder=3, label="share of the entering firms")
        for b in b2:
            b.set_hatch("////")
        for xi, (e, ne) in enumerate(zip(ea, sub["entering with this class"])):
            if np.isfinite(e):
                ax.text(xi + 0.19, e + 0.01, f"{int(ne)}", ha="center", va="bottom", fontsize=6.5, color=INK)
        ax.set_xticks(x, [_lf.WIN_SHORT.get(w, w) for w in WINDOW_NAMES], fontsize=6.5, rotation=90)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        ax.set_title(_lf._arch_name(code), fontsize=8.5)
        _hgrid(ax, "y")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    axes[0].set_ylim(0, top + 0.12)
    axes[0].set_ylabel("share of the window", fontsize=8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7, loc="lower center", ncol=2, handlelength=1.4,
               bbox_to_anchor=(0.5, -0.16), frameon=False)
    fig.suptitle("What entering firms arrive with, against the window's own mix — the number on the bar "
                 "is the firms entering with the class", fontsize=9, y=1.02)
    return _save(fig, path)


def panel_class_configs(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Within-class convergence on each class's OWN differentiating labels (rules in the table):
    (i) the share of the class in its single most common configuration; (ii) distinct
    configurations per aircraft. A line is a class; a window under five aircraft is not drawn."""
    t = tables["la_class_configs_own"].copy()
    for c in ("aircraft", "distinct configurations", "share in it"):
        t[c] = _num(t, c)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.5))
    x = np.arange(len(WINDOW_NAMES))
    for code in t["code"].unique():
        sub = t[t["code"].eq(code)].set_index("window").reindex(WINDOW_NAMES)
        mk, ls = _lf._cs(code)
        ok = sub["share in it"].notna()
        a1.plot(x[ok], sub["share in it"][ok], marker=mk, ls=ls, color=_lf._color(code), lw=1.4, ms=4,
                label=_lf._arch_name(code))
        per = (sub["distinct configurations"] / sub["aircraft"]).where(ok)
        a2.plot(x[ok], per[ok], marker=mk, ls=ls, color=_lf._color(code), lw=1.4, ms=4)
    for ax, title in ((a1, "share of the class in its most common configuration"),
                      (a2, "distinct configurations per aircraft")):
        ax.set_xticks(x, [_lf.WIN_SHORT.get(w, w) for w in WINDOW_NAMES], fontsize=7.5)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        ax.set_title(title, fontsize=8.5)
        _hgrid(ax, "y")
    a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    a1.set_ylim(0, 0.7)
    a2.set_ylim(0, 1.0)
    handles, labels = a1.get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=6.5, loc="lower center", ncol=5, handlelength=1.8,
               bbox_to_anchor=(0.5, -0.12), frameon=False, columnspacing=1.0)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 6 — the citation advantage of the rated firms, as a distribution
# --------------------------------------------------------------------------
#: the rank axis in ten bins: a decile is the coarsest split that still shows a shape, and the
#: rank is a percentile, so the bins need no choosing.
CITE_BINS = np.linspace(0, 1, 11)


def panel_cite_rank(tables: Dict[str, pd.DataFrame], path: Path,
                    ds=None, v: Optional[pd.DataFrame] = None) -> Optional[Path]:
    """The cohort citation rank of the index firms' aircraft against every other aircraft, as
    two distributions rather than two medians. Base: the aircraft in each group, in the legend.

    The printed table gives the two medians and a p; the question is whether the advantage is a
    property of the whole population or of a tail, and only the shape answers that. The split
    and the rank are the SAME two functions the table is built from, so the medians drawn here
    are the table's own (``la_ari_gap``, row "cohort citation rank").
    """
    if ds is None:
        return None
    frame = _lt.base(ds) if v is None else v
    rank = _lt.cohort_citation_rank(ds)
    firms = set(_lt.ari_firms(frame)["company"])
    idx = frame["company_canonical"].isin(firms)
    r = pd.to_numeric(pd.Series(rank.reindex(frame["patent_id"]).to_numpy()), errors="coerce")
    a = r[idx.to_numpy()].dropna()
    b = r[~idx.to_numpy()].dropna()
    # the two medians are read from the printed table, never from the two series drawn here —
    # they are the same number, and this way they cannot become two
    gap = tables.get("la_ari_gap")
    med_a, med_b = float(a.median()), float(b.median())
    if gap is not None and "variable" in gap.columns:
        row = gap[gap["variable"].eq("cohort citation rank")]
        if len(row):
            med_a = float(pd.to_numeric(row["index firms"].iloc[0], errors="coerce"))
            med_b = float(pd.to_numeric(row["rest of the corpus"].iloc[0], errors="coerce"))

    fig, ax = plt.subplots(figsize=(W, 2.35))
    centres = (CITE_BINS[:-1] + CITE_BINS[1:]) / 2
    ha, _ = np.histogram(a, bins=CITE_BINS)
    hb, _ = np.histogram(b, bins=CITE_BINS)
    wid = 0.042
    bars_a = ax.bar(centres - wid / 1.9, ha / ha.sum(), width=wid, color=CAT[0], zorder=3,
                    label=f"the index firms' aircraft (n {len(a)})")
    bars_b = ax.bar(centres + wid / 1.9, hb / hb.sum(), width=wid, color=CONTEXT, zorder=3,
                    label=f"every other aircraft (n {len(b)})")
    for bar in bars_a:
        bar.set_hatch("////")
    top = max((ha / ha.sum()).max(), (hb / hb.sum()).max())
    ax.set_ylim(0, top * 1.16)
    for med, col, ls, ha_ in ((med_b, INK2, "--", "right"), (med_a, CAT[0], "-", "left")):
        ax.axvline(med, color=col, lw=1.3, ls=ls, zorder=4)
        # under the legend, which owns the top of the panel
        ax.text(med + (0.008 if ha_ == "left" else -0.008), top * 0.88, f"median {med:.2f}",
                va="top", ha=ha_, fontsize=7.5, color=col, zorder=6,
                bbox=dict(fc=SURFACE, ec="none", pad=0.6))
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, 0.1), [f"{t:.1f}" for t in np.arange(0, 1.01, 0.1)],
                  fontsize=7.5)
    ax.set_xlabel("cohort citation rank (0.50 = cited like the median patent of its own "
                  "priority year)", fontsize=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("share of the group", fontsize=8)
    _hgrid(ax, "y")
    ax.legend(fontsize=7.5, loc="upper left", handlelength=1.4)
    ax.set_title("The whole distribution moves, not one tail: the rated firms' aircraft sit "
                 "above the median patent of their own year", fontsize=9)
    return _save(fig, path)


# --------------------------------------------------------------------------
# the one entry point the render script calls
# --------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# 2026-09-24, the drivers section rewritten as observations with the correlation behind each
# (author: "put this as a correlation with the possible reasons"). Both panels read the SAME
# frame the verdict table is built from (``la_tables.trace_frame``) plus the per-aircraft unit
# counts (``la_tables._per_aircraft_units``), so no number here can disagree with Table 12.
# ---------------------------------------------------------------------------------------------
_DRV_W = ["<= 2011", "2012-15", "2016-19", "2020-23"]
_DRV_WL = ["≤2011", "12–15", "16–19", "20–23"]
_DRV_CL = [("SLC", "Lift + Cruise", "o", "-", CAT[0], True),
           ("TR", "Tilt Rotor", "s", "--", CAT[7], True),
           ("CVT", "Comb. vectored thrust", "^", "-.", CAT[2], True),
           ("TW", "Tilt Wing", "D", ":", CAT[3], False),
           ("MR", "Multirotor", "v", "--", CAT[6], False)]


def _driver_frame(ds) -> pd.DataFrame:
    """One row per unique aircraft, priority year ≤ 2023: the traces of Table 12 and the
    tilting / fixed propulsor-set counts read from the M3 groups."""
    v = _lt.base(ds)
    t = _lt.trace_frame(ds, v)
    raw = ds.variants
    pu = _lt._per_aircraft_units(raw)
    pu["aircraft_id"] = raw["aircraft_id"].values
    t = t.merge(pu, on="aircraft_id", how="left")
    t = t[pd.to_numeric(t["year"], errors="coerce") <= 2023].copy()
    for c in ("joints", "n_types", "units", "ducted", "on_booms", "tilting types", "fixed types"):
        t[c] = pd.to_numeric(t[c], errors="coerce")
    return t


def _drv_series(t, cls, col, how, min_n=5):
    d = t[t["topType"] == cls]
    g = d.groupby("window")[col]
    s = (g.median() if how == "median" else g.mean()).reindex(_DRV_W)
    n = g.count().reindex(_DRV_W).fillna(0)
    return s.where(n >= min_n)


def _drv_pct(ax):
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.set_yticklabels(["0", "25", "50", "75", "100 %"])


def panel_driver_traces(ds, path: Path) -> Optional[Path]:
    """The four traces of the observations, per class and window: (i) tilting joint groups
    (mean), (ii) propulsive units (median), (iii) propulsor types (mean), (iv) share with a
    ducted unit. A point needs ≥ 5 aircraft in the class-window."""
    if ds is None:
        return None
    t = _driver_frame(ds)
    fig, axs = plt.subplots(1, 4, figsize=(W, 2.45))
    spec = [("joints", "mean", "(i) tilting joint groups\nmean per aircraft", False),
            ("units", "median", "(ii) propulsive units\nmedian per aircraft", False),
            ("n_types", "mean", "(iii) propulsor types\nmean per aircraft", False),
            ("ducted", "mean", "(iv) share with a\nducted unit", True)]
    for ax, (col, how, title, pct) in zip(axs, spec):
        for code, name, mk, ls, c, filled in _DRV_CL:
            s = _drv_series(t, code, col, how)
            ax.plot(range(4), s.values, marker=mk, ls=ls, color=c, ms=4.5, lw=1.3, label=name,
                    mfc=c if filled else "white")
        ax.set_title(title, loc="left", fontsize=8.5)
        ax.set_xticks(range(4))
        ax.set_xticklabels(_DRV_WL, rotation=35, ha="right", fontsize=7)
        ax.grid(axis="y", lw=0.4, alpha=0.5)
        if pct:
            _drv_pct(ax)
        else:
            ax.set_ylim(bottom=0)
    axs[0].set_ylim(0, 2.1)
    axs[2].set_ylim(0, 3.2)
    fig.legend(*axs[0].get_legend_handles_labels(), loc="lower center", ncol=5, frameon=False,
               fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    return _save(fig, path)


def panel_driver_correlations(ds, path: Path) -> Optional[Path]:
    """The correlation behind each observation: (i) Tilt Rotor, share with ≥ 2 tilting
    propulsor sets against share with any fixed set, per window; (ii) Tilt Rotor, median
    propulsive units by number of tilting sets; (iii) CVT, share with units on booms, and share
    ducted among the aircraft with and without units on booms (a point needs ≥ 4 aircraft)."""
    if ds is None:
        return None
    t = _driver_frame(ds)
    red = CAT[7]
    fig, axs = plt.subplots(1, 3, figsize=(W, 2.55))
    x = np.arange(4)
    d = t[t["topType"] == "TR"]
    two = (d["tilting types"] >= 2).groupby(d["window"]).mean().reindex(_DRV_W)
    fx = (d["fixed types"] >= 1).groupby(d["window"]).mean().reindex(_DRV_W)
    ax = axs[0]
    ax.bar(x - 0.19, two.values, 0.38, color=red, label="≥ 2 tilting sets")
    ax.bar(x + 0.19, fx.values, 0.38, color="white", edgecolor=red, hatch="///", label="≥ 1 fixed set")
    ax.set_xticks(x)
    ax.set_xticklabels(_DRV_WL, fontsize=7.5)
    _drv_pct(ax)
    ax.set_title("(i) Tilt Rotor: what the\nsecond propulsor type is", loc="left", fontsize=8.5)
    ax.legend(frameon=False, loc="upper left", fontsize=7)
    ax = axs[1]
    k = d.groupby("tilting types")["units"].agg(["median", "size"])
    k = k[(k.index >= 1) & (k.index <= 3)]
    ax.bar([str(int(i)) for i in k.index], k["median"].values, color=red, width=0.6)
    for i, (m, n) in enumerate(zip(k["median"], k["size"])):
        ax.text(i, m + 0.15, f"n = {int(n)}", ha="center", fontsize=7)
    ax.set_title("(ii) Tilt Rotor: median units\nby number of tilting sets", loc="left", fontsize=8.5)
    ax.set_xlabel("tilting propulsor sets on the aircraft", fontsize=7.5)
    ax.set_ylim(0, float(k["median"].max()) + 1.5)
    d = t[t["topType"] == "CVT"]
    onb = d.groupby("window")["on_booms"].mean().reindex(_DRV_W)
    nb, b = d[d["on_booms"] == 0], d[d["on_booms"] == 1]
    n_nb = nb.groupby("window").size().reindex(_DRV_W).fillna(0)
    n_b = b.groupby("window").size().reindex(_DRV_W).fillna(0)
    duct_nb = nb.groupby("window")["ducted"].mean().reindex(_DRV_W).where(n_nb >= 4)
    duct_b = b.groupby("window")["ducted"].mean().reindex(_DRV_W).where(n_b >= 4)
    ax = axs[2]
    ax.plot(x, onb.values, marker="^", ls="-.", color=CAT[2], label="units on booms (share)", lw=1.3, ms=4.5)
    ax.plot(x, duct_nb.values, marker="s", ls="-", color=INK, label="ducted · no booms", lw=1.3, ms=4.5)
    ax.plot(x, duct_b.values, marker="s", ls="--", color=INK, mfc="white", label="ducted · units on booms",
            lw=1.3, ms=4.5)
    ax.set_xticks(x)
    ax.set_xticklabels(_DRV_WL, fontsize=7.5)
    _drv_pct(ax)
    ax.set_title("(iii) CVT: ducting against\nthe boom layout", loc="left", fontsize=8.5)
    ax.legend(frameon=False, loc="upper center", fontsize=6.5, bbox_to_anchor=(0.5, -0.2), ncol=1)
    for ax in axs:
        ax.grid(axis="y", lw=0.4, alpha=0.5)
    fig.tight_layout()
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-25, the review of the brief: three panels, each for a result that a
# table alone does not carry — the normalised joint count (C29, C32), the
# conditional ducting test (C24, C36) and the post-hoc design family (C36).
# --------------------------------------------------------------------------
#: the classes drawn on the joints panel, in the order the document names them
JOINT_CLASSES = ["TR", "CVT", "TW", "MR", "SLC"]


def panel_joints_per_unit(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Tilting joint groups per window, absolute (i) and divided by the aircraft's propulsive
    units (ii), one line per class. Base: the class's aircraft in the window, five or more.

    The two panels are the whole of the point: the absolute count rises inside Tilt Rotor and CVT,
    and the ratio does not follow it, so the rise is the propulsor count and not an independent
    tilting cost. The Spearman rho and p of each line are printed in the table.
    """
    t = tables["la_joints_per_unit"].copy()
    wins = [_lf.WIN_SHORT.get(w, w) for w in WINDOW_NAMES]
    for c in wins:
        t[c] = _num(t, c)
    t["_rho"] = _num(t, "rho")
    measures = list(dict.fromkeys(t["measure"]))
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.5))
    x = np.arange(len(wins))
    for ax, measure in zip(axes, measures):
        sub_m = t[t["measure"].eq(measure)]
        for code in JOINT_CLASSES:
            r = sub_m[sub_m["code"].eq(code)]
            if not len(r):
                continue
            y = r[wins].iloc[0].to_numpy(dtype=float)
            ok = np.isfinite(y)
            mk, ls = _lf._cs(code)
            ax.plot(x[ok], y[ok], marker=mk, ls=ls, color=_lf._color(code), lw=1.4, ms=4,
                    label=_lf._arch_name(code))
        ax.set_xticks(x, wins, fontsize=7.5)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        _hgrid(ax, "y")
    axes[0].set_title("(i) median tilting joint groups", loc="left", fontsize=8.5)
    axes[1].set_title("(ii) the same, per propulsive unit", loc="left", fontsize=8.5)
    axes[0].set_ylim(bottom=0)
    axes[1].set_ylim(0, 0.62)
    # the two classes the verdict is about, with their test, written on the panel that decides it
    said = []
    for code in ("TR", "CVT"):
        a = t[t["code"].eq(code) & t["measure"].eq(measures[0])]
        b = t[t["code"].eq(code) & t["measure"].eq(measures[1])]
        if len(a) and len(b):
            said.append(f"{_lf._arch_name(code)}: count {a['movement'].iloc[0]} (ρ {a['_rho'].iloc[0]:+.2f}), "
                        f"per unit {b['movement'].iloc[0]} (ρ {b['_rho'].iloc[0]:+.2f})")
    axes[1].text(0.02, 0.03, "\n".join(said), transform=axes[1].transAxes, fontsize=6.5,
                 color=INK2, va="bottom", ha="left", linespacing=1.3)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=6.5, loc="lower center", ncol=5, handlelength=1.8,
               bbox_to_anchor=(0.5, -0.12), frameon=False, columnspacing=1.0)
    fig.suptitle("The tilting joints rose with the propulsors, not against the cost of tilting",
                 fontsize=9, y=1.02)
    return _save(fig, path)


def panel_duct_conditional(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Given that one unit is ducted, how much of the aircraft is: the conditional distribution of
    the ducted share, per propulsive-unit band. Base on the tick — the aircraft of the band with at
    least one ducted unit."""
    t = tables["la_duct_conditional"].copy()
    bins = [c for c, _lo, _hi in _lt.DUCT_SHARE_BINS] + [_lt.DUCT_EVERY]
    for c in bins + ["of them, duct at least one unit", "share that duct every unit"]:
        t[c] = _num(t, c)
    t = t[t["propulsive units"].ne("all bands")]
    allrow = tables["la_duct_conditional"]
    allrow = allrow[allrow["propulsive units"].eq("all bands")]
    every = float(_num(allrow, "share that duct every unit").iloc[0])

    fig, ax = plt.subplots(figsize=(W, 2.45))
    x = np.arange(len(t))
    n = t["of them, duct at least one unit"].to_numpy(dtype=float)
    bottom = np.zeros(len(t))
    # a light-to-dark grey ramp for the partial bins and the one colour for "every unit", so the
    # four partial bins stay apart from each other in black and white as well as in colour
    ramp = ["#ececea", "#d5d4d0", "#bebcb6", "#a7a49c"]
    for i, b in enumerate(bins):
        frac = t[b].to_numpy(dtype=float) / n
        ax.bar(x, frac, bottom=bottom, width=0.62, zorder=3, label=b,
               color=(BLUE(0.85) if b == _lt.DUCT_EVERY else ramp[i % len(ramp)]),
               edgecolor=INK, lw=0.4)
        for xi, (f, bt) in enumerate(zip(frac, bottom)):
            if f >= 0.08:
                ax.text(xi, bt + f / 2, f"{f:.0%}", ha="center", va="center", fontsize=6.5,
                        color="#ffffff" if b == _lt.DUCT_EVERY else INK)
        bottom = bottom + frac
    ax.axhline(1 - every, color=INK, lw=1.1, ls="--", zorder=5)
    ax.text(len(t) - 0.4, 1 - every, f"every band together:\nthe top block is {every:.0%}",
            ha="left", va="center", fontsize=7, color=INK2, zorder=6, linespacing=1.2)
    ax.set_xticks(x, [f"{g}\nn {int(v)}" for g, v in zip(t["propulsive units"], n)], fontsize=8)
    ax.set_xlim(-0.6, len(t) + 0.55)
    ax.set_xlabel("propulsive units per aircraft · base: the aircraft of the band with at least one "
                  "ducted unit", fontsize=7.5)
    ax.set_ylabel("share of the aircraft that\nduct at least one unit", fontsize=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 1.0)
    _hgrid(ax, "y")
    ax.legend(fontsize=6.5, loc="lower center", ncol=5, handlelength=1.4, frameon=False,
              bbox_to_anchor=(0.5, -0.46))
    ax.set_title("If one unit is ducted, are they all? Mostly — but not as a rule", fontsize=9)
    return _save(fig, path)


def panel_family(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """The post-hoc Lift + Cruise + CVT family: its share of each priority window under the three
    definitions, against the 50 % line of condition 1. Base: the aircraft of the window, on the
    tick. POST HOC — the grouping was defined after the result it came from."""
    t = tables["la_family_share"].copy()
    t["_s"] = _num(t, "family share")
    t["_n"] = _num(t, "family aircraft")
    t["_w"] = _num(t, "aircraft in the window")
    ids = [i for i in ("c", "b", "bc") if i in set(t["id"])]
    fig, ax = plt.subplots(figsize=(W, 2.5))
    x = np.arange(len(WINDOW_NAMES))
    for i, key in enumerate(ids):
        sub = t[t["id"].eq(key)].set_index("window").reindex(WINDOW_NAMES)
        ax.plot(x, sub["_s"], marker=["o", "s", "^"][i % 3], ls=["-", "--", ":"][i % 3],
                color=CAT[i % len(CAT)], lw=1.5, ms=4.5, label=str(sub["definition"].dropna().iloc[0]))
        if key == ids[0]:
            for xi, (s, nn) in enumerate(zip(sub["_s"], sub["_n"])):
                if np.isfinite(s):
                    ax.text(xi, s - 0.025, f"{int(nn)}", ha="center", va="top", fontsize=6.5, color=INK)
    ax.axhline(0.5, color=INK, lw=1.2, ls="--", zorder=4)
    ax.text(len(WINDOW_NAMES) - 0.55, 0.505,
            "condition 1: one design over half a window, twice in a row",
            transform=ax.transData, fontsize=7, color=INK2, va="bottom", ha="right")
    wins = tables["la_family_share"]
    base = wins[wins["id"].eq(ids[0])].set_index("window").reindex(WINDOW_NAMES)
    ax.set_xticks(x, [f"{_lf.WIN_SHORT.get(w, w)}\nn {int(v)}" for w, v in
                      zip(WINDOW_NAMES, _num(base.reset_index(), "aircraft in the window"))], fontsize=7.5)
    ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
    ax.set_ylabel("share of the window's aircraft", fontsize=8)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 0.62)
    _hgrid(ax, "y")
    ax.legend(fontsize=7, loc="lower right", handlelength=2.0, frameon=False)
    ax.set_title("POST HOC — Lift + Cruise and the CVT aircraft read as one design family: "
                 "larger than any class, still under the line", fontsize=9)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-26 — an aircraft is out of force only when every patent linked to it is
# --------------------------------------------------------------------------
#: a class is drawn (and tested) with this many aircraft or more; the same cut as
#: ``sm_open.FORCE_TEST_MIN``
FORCE_MIN = 10


def panel_force_aircraft(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Share of the unique aircraft (priority <= 2019) out of force per class, where an aircraft
    is out of force only when EVERY patent linked to it reads INACTIVE at the PatSeer snapshot
    (author's ruling 2026-09-26). The hollow tick is the old reading on the same aircraft — the
    primary patent alone. Base: the class's aircraft, on the tick; classes under ten are not drawn.
    """
    t = tables["la_force_aircraft"].copy()
    for c in ("unique aircraft", "out of force", "out of force share", "out of force, primary patent only"):
        t[c] = _num(t, c)
    allrow = t[t["class"].eq("all classes")]
    overall = float(allrow["out of force share"].iloc[0])
    total = int(allrow["unique aircraft"].iloc[0])
    t = t[t["class"].ne("all classes") & t["unique aircraft"].ge(FORCE_MIN)]

    fig, ax = plt.subplots(figsize=(W, 2.45))
    x = np.arange(len(t))
    bars = ax.bar(x, t["out of force share"], width=0.62, color=BLUE(0.78), zorder=3,
                  label="out of force: every linked patent INACTIVE")
    # the value on a white ground above the dashed line, so a bar that ends near it stays legible
    for b, val in zip(bars, t["out of force share"]):
        ax.text(b.get_x() + b.get_width() / 2, val + 0.012, f"{val:.0%}", ha="center", va="bottom",
                fontsize=7.5, color=INK, zorder=6, bbox=dict(fc="white", ec="none", pad=0.4))
    ax.scatter(x + 0.36, t["out of force, primary patent only"], marker="<", s=22, facecolor="white",
               edgecolor=INK, lw=0.9, zorder=5, label="old reading: the primary patent alone")
    ax.axhline(overall, color=INK, lw=1.1, ls="--", zorder=4)
    ax.text(len(t) - 0.4, overall + 0.012, f"all classes\n{overall:.0%} of {total}",
            ha="left", va="bottom", fontsize=7.5, color=INK2, zorder=5, linespacing=1.2)
    # the table prints display names; a long one goes to its code, a two-word one to two lines,
    # so eight ticks fit the text width without running into each other
    codes = {nm: k for k, nm in _lt.metrics.ARCH_NAMES.items()}
    names = [(c if len(c) <= 14 else codes.get(c, c)) for c in t["class"]]
    names = ["\n".join(nm.rsplit(" ", 1)) if len(nm) > 10 else nm for nm in names]
    ax.set_xticks(x, [f"{nm}\nn {int(n)}" for nm, n in zip(names, t["unique aircraft"])], fontsize=7.5)
    ax.set_xlim(-0.65, len(t) + 0.6)
    _pct_axis(ax, float(t["out of force share"].max()) + 0.16)
    ax.set_ylabel("share of the class's\naircraft out of force", fontsize=8)
    ax.legend(fontsize=7, loc="upper left", ncol=2, handlelength=1.4, frameon=False)
    test = tables.get("la_force_aircraft_test")
    ptxt = ""
    if test is not None and len(test):
        p = float(pd.to_numeric(test["p"], errors="coerce").iloc[0])
        k = int(pd.to_numeric(test["classes tested"], errors="coerce").iloc[0])
        ptxt = f" · class × out of force over the {k} classes drawn: χ² p = {p:.3f}"
        # 2026-09-26: the p depends on how a duplicate that names several aircraft is counted;
        # the figure prints both, as the text does, so it cannot be read as a firm difference
        sens = test[test["reading"].astype(str).str.contains("first target only")]
        if len(sens):
            ps = float(pd.to_numeric(sens["p"], errors="coerce").iloc[0])
            ptxt += f" ({ps:.3f} if a duplicate counts for its first aircraft only)"
    ax.set_xlabel(f"architecture class · unique aircraft with priority ≤ 2019, classes of {FORCE_MIN} "
                  f"or more{ptxt}", fontsize=7.5)
    ax.annotate("Source: PatSeer legal status at the snapshot (2026-06-08) · human labelling (class)",
                xy=(0, 0), xycoords="axes fraction", xytext=(0, -56), textcoords="offset points",
                ha="left", va="top", fontsize=7, color=INK2)
    ax.set_title("An aircraft is out of force only when none of its patents is: share per class",
                 fontsize=9)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-26, C44-C46 — the class mix per window against the dated evtol.news directory
# --------------------------------------------------------------------------
#: the directory's five classes, in stack order (bottom first), each in the atlas colour of the
#: corpus class that dominates it: Lift + Cruise = SLC, Vectored Thrust = TR, Wingless = MR,
#: Electric Rotorcraft = RC, Hover Bikes / PFD = HB. All five are known to the black-and-white pass.
EVN_CLASSES = [("LC", "Lift + Cruise", CAT[0]), ("VT", "Vectored Thrust", CAT[1]),
               ("WM", "Wingless (Multicopter)", CAT[4]), ("ER", "Electric Rotorcraft", CAT[7]),
               ("HB", "Hover Bikes / Personal Flying Devices", "#111827")]
EVN_PANELS = [
    ("patent corpus (unique aircraft, priority year)",
     "(i) Patent corpus · unique aircraft by priority year",
     "Source: PatSeer · human labelling, folded to five classes"),
    ("evtol.news directory (aircraft, development year)",
     "(ii) evtol.news directory · aircraft by development year",
     "Source: evtol.news directory (crawled 2026-09-17)"),
]


def panel_evtolnews_check(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """The corpus's class share per priority window, folded to the directory's five classes
    (``la_tables.FOLD5``), beside the directory's class share per development-year window: same
    windows, same classes, same colours. Base: dated, classed aircraft, n on the tick; the partial
    window is faded. Each panel carries its own source note."""
    t = tables["la_evtolnews_check"].copy()
    for c in ("aircraft", "window total", "share"):
        t[c] = _num(t, c)
    cov = tables.get("la_evtolnews_coverage")
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.6), sharey=True, gridspec_kw={"wspace": 0.12})
    x = np.arange(len(WINDOW_NAMES))
    for ax, (src, title, note) in zip(axes, EVN_PANELS):
        s = t[t["source"].eq(src)]
        bottom = np.zeros(len(x))
        ns = s.groupby("window")["window total"].first().reindex(WINDOW_NAMES).fillna(0).astype(int)
        for code, name, col in EVN_CLASSES:
            sh = s[s["code"].eq(code)].set_index("window")["share"].reindex(WINDOW_NAMES).fillna(0).to_numpy()
            bars = ax.bar(x, sh, bottom=bottom, width=0.72, color=col, edgecolor=SURFACE, lw=1.0,
                          label=name, zorder=3)
            for xi, (b, val) in enumerate(zip(bottom, sh)):
                if "partial" in WINDOW_NAMES[xi]:
                    bars[xi].set_alpha(0.45)
                if val >= 0.06:
                    ax.text(xi, b + val / 2, f"{val:.0%}", ha="center", va="center", fontsize=7.5,
                            color="white", fontweight="bold", zorder=5,
                            bbox=dict(fc=col, ec="none", pad=0.6, alpha=0.85))
            bottom += sh
        ax.set_xticks(x, [f"{_lf.WIN_SHORT.get(w, w)}\nn {ns[w]}" for w in WINDOW_NAMES], fontsize=7.5)
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.spines[["left", "bottom"]].set_visible(False)
        ax.set_title(title, fontsize=8.5)
        total = int(ns.sum())
        if src.startswith("patent"):
            base = f"n = {_thin(total)} aircraft with a class · * partial window"
        else:
            base = f"n = {_thin(total)} aircraft dated · * partial window"
            if cov is not None and len(cov):
                allrow = cov[cov["directory class"].eq("all classes")]
                if len(allrow):
                    base = (f"n = {_thin(total)} of {_thin(int(_num(allrow, 'aircraft on the list').iloc[0]))} "
                            f"dated · * partial window")
        ax.set_xlabel(base, fontsize=7.5)
        ax.annotate(note, xy=(0, 0), xycoords="axes fraction", xytext=(0, -38), textcoords="offset points",
                    ha="left", va="top", fontsize=7, color=INK2, linespacing=1.25)
    axes[0].set_ylabel("share of the window's aircraft", fontsize=8)
    handles, labels = axes[0].get_legend_handles_labels()
    # the source notes sit under each panel; the key goes below both of them
    fig.subplots_adjust(bottom=0.3)
    # 2026-09-26 (chapter-3 review): the figure is shorter now, so the key is anchored below the
    # two source notes instead of at a fixed fraction of the canvas
    fig.legend(handles, labels, fontsize=7.5, loc="upper center", ncol=3, handlelength=1.4,
               bbox_to_anchor=(0.5, -0.03), frameon=False, columnspacing=1.2)
    return _save(fig, path)


def _thin(n: int) -> str:
    """1229 -> '1 229', the document's thousands separator."""
    return f"{int(n):,}".replace(",", " ")


# --------------------------------------------------------------------------
# 2026-09-26, chapter 2 review (C75, C76, C78): ducting merged into one panel, and the five
# propulsion graphs compacted into one figure. The originals (atlas_units, sm_duct_count,
# sm_duct_conditional) are kept and still drawn.
# --------------------------------------------------------------------------
#: the four partial bins of la_duct_conditional, pooled two by two for the merged panel: the
#: middle of the distribution is thin, and four grey steps on a bar a third of the axis high
#: cannot be told apart in print
DUCT_PARTIAL = [("half or more, not all", ["half to three quarters", "three quarters, not all"], "#a7a49c"),
                ("some units, under half", ["under a quarter", "a quarter to half"], "#dddcd7")]


def _duct_merged(ax, tables: Dict[str, pd.DataFrame], legend_y: float = 1.0) -> None:
    """Draw the merged ducting panel on ``ax`` (C76/C78): per propulsive-unit band, and for all
    bands together, the share of the band's aircraft that duct (the stack's height — the U the
    yes/no line draws), split into the aircraft that duct EVERY unit (blue, with its share of
    the ducting aircraft printed inside) and the two partial bins; the share of the band's
    UNITS in a duct as a diamond; the median ducted units of the ducting aircraft under the tick.
    Everything is read from ``la_duct_count`` and ``la_duct_conditional``; nothing is typed."""
    dc = tables["la_duct_count"].copy()
    cd = tables["la_duct_conditional"].copy()
    key = "propulsive units"
    dc = dc.set_index(key)
    cd = cd.set_index(key)
    order = [g for g in dc.index if g != "all bands"] + ["all bands"]
    num = lambda f, c: pd.to_numeric(f.loc[order, c], errors="coerce").to_numpy(dtype=float)
    n = num(dc, "aircraft")
    any_n = num(dc, "with any ducted unit")
    any_s = num(dc, "share with any")
    unit_s = num(dc, "share of units ducted")
    every_s = num(dc, "share ducting every unit")
    med = num(dc, "median ducted units (ducted aircraft)")
    cond_every = num(cd, "share that duct every unit")
    parts = [(lab, sum(num(cd, c) for c in cols) / n, col) for lab, cols, col in DUCT_PARTIAL]

    x = np.arange(len(order), dtype=float)
    x[-1] += 0.6                                   # the all-bands bar stands apart
    w = 0.58
    ax.bar(x, every_s, width=w, color=BLUE(0.85), edgecolor=INK, lw=0.5, zorder=3,
           label="ducts every unit")
    bottom = every_s.copy()
    for lab, frac, col in parts:
        ax.bar(x, frac, bottom=bottom, width=w, color=col, edgecolor=INK, lw=0.5, zorder=3, label=lab)
        bottom = bottom + frac
    # the stack's top is the band's share with any duct: joined over the bands (the U), with
    # the count it rests on
    ax.plot(x[:-1], any_s[:-1], color=INK, lw=1.3, zorder=4)
    ax.plot(x, any_s, "o", color=INK, ms=4, zorder=5)
    for xi, s_, a_, n_ in zip(x, any_s, any_n, n):
        ax.text(xi, s_ + 0.03, f"{s_:.0%}", ha="center", va="bottom", fontsize=7.5,
                fontweight="bold", color=INK, zorder=6)
    for xi, e_, c_ in zip(x, every_s, cond_every):
        ax.text(xi, e_ / 2, f"{c_:.0%}", ha="center", va="center", fontsize=6.8,
                color="#ffffff", zorder=6)
    ax.plot(x + w / 2 + 0.1, unit_s, "D", color=SURFACE, mec=INK, mew=1.2, ms=5, ls="none",
            zorder=6, label="◆ share of the band's units in a duct")
    for xi, u_ in zip(x, unit_s):
        ax.text(xi + w / 2 + 0.2, u_, f"{u_:.0%}", ha="left", va="center", fontsize=6.8,
                color=INK2, zorder=6)
    ax.axvline((x[-2] + x[-1]) / 2, color=GRID, lw=1, ls=":")
    ax.set_xticks(x, [f"{g}\n{int(nn)} · {int(a_)}\nmed {m_:g}"
                      for g, nn, a_, m_ in zip(order, n, any_n, med)], fontsize=7)
    ax.set_xlim(x[0] - 0.55, x[-1] + 0.85)
    _pct_axis(ax, float(np.nanmax(np.r_[any_s, unit_s])) + 0.38)
    ax.set_ylabel("share of the band's aircraft", fontsize=8)
    ax.set_xlabel("propulsive units per aircraft · under each band: aircraft · aircraft with a "
                  "ducted unit · median ducted units of those", fontsize=7.5)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h, [lab.replace("◆ ", "") for lab in l], fontsize=7, ncol=2, loc="upper left",
              bbox_to_anchor=(0.0, legend_y), frameon=False, handlelength=1.3, columnspacing=1.0)
    ax.text(0.995, legend_y - 0.20, "white % in the blue block: of the aircraft that duct,\n"
            "the share that duct every unit", transform=ax.transAxes, ha="right", va="top",
            fontsize=6.8, color=INK2, linespacing=1.15)


def _duct_source(ax, tables) -> None:
    allrow = tables["la_duct_count"]
    base = int(pd.to_numeric(allrow.loc[allrow["propulsive units"].eq("all bands"), "aircraft"]).iloc[0])
    _lf._panel_note(ax, ax, f"Unit: unique aircraft with a propulsive-unit count ({base}), by band; the "
                    "◆ counts propulsive units\nSource: human labelling (M3 propulsor cards: unit "
                    "counts and the ducted flag per propulsor type)")


def panel_duct_merged(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """ONE ducting panel in place of sm_duct_count + sm_duct_conditional (+ la_duct_count, which
    leaves the brief): how many aircraft of each band duct, and how much of each is ducted."""
    fig, ax = plt.subplots(figsize=(W, 3.1))
    _duct_merged(ax, tables)
    ax.set_title("Ducting per propulsive-unit band: how many aircraft duct (bar height), and how "
                 "much of each aircraft is ducted (the split)", fontsize=9)
    _duct_source(ax, tables)
    return _save(fig, path)


def panel_propulsion_compact(tables: Dict[str, pd.DataFrame], path: Path, ds) -> Optional[Path]:
    """The propulsion pages in two panels instead of five graphs (C75): (i) the propulsive
    units per class with the arrangement features of the same classes directly under it on a
    shared class axis (atlas_units (i) + (ii), plus one row for the stations the takeaway names);
    (ii) the merged ducting panel (atlas_units (iii) + sm_duct_count + sm_duct_conditional).
    The frames are the ones fig_units draws from; nothing is typed."""
    if ds is None:
        return None
    from . import a2, atlas, metrics
    v = atlas._variants(ds)
    order = [c for c in atlas.ALL_ARCH if c in v["atype"].values]
    fig = plt.figure(figsize=(W, 8.4))
    outer = fig.add_gridspec(2, 1, height_ratios=[2.0, 1.25], hspace=0.62)
    gs = outer[0].subgridspec(2, 1, height_ratios=[1.15, 0.8], hspace=0.06)
    ax = fig.add_subplot(gs[0])
    rng = np.random.default_rng(42)
    units = pd.to_numeric(v["units"], errors="coerce")
    for i_, c in enumerate(order):
        u = units[v["atype"].eq(c)].dropna().to_numpy()
        if not len(u):
            ax.text(i_, 15, "no propulsor card", rotation=90, ha="center", va="center", fontsize=7,
                    color=MUTED)
            continue
        ax.scatter(i_ + rng.uniform(-0.25, 0.25, len(u)), np.clip(u, 0, 30) + rng.uniform(-0.25, 0.25, len(u)),
                   s=7, color=_lf._color(c), alpha=0.55, lw=0)
        q1, md, q3 = np.percentile(u, [25, 50, 75])
        ax.plot([i_, i_], [q1, q3], color=INK, lw=2.5)
        ax.plot(i_, md, "o", color=SURFACE, mec=INK, ms=6, mew=1.6)
    ax.set_xlim(-0.5, len(order) - 0.5)
    ax.set_ylim(-1, 31)
    ax.set_xticks(range(len(order)))
    ax.tick_params(axis="x", labelbottom=False, length=0)
    ax.set_ylabel("propulsive units\n(capped at 30)", fontsize=7.5)
    _hgrid(ax, "y")
    ax.set_title("(i) Propulsive units per class (dot = one aircraft, bar = middle half, ring = "
                 "median) and, under it, how each class arranges them", fontsize=9)
    # the arrangement rows, the same definitions as atlas_units (ii), plus the stations
    st = a2.propulsion_states(v)
    stations = a2.propulsor_groups(v).astype(float).where(units.notna())
    feat = pd.DataFrame({"atype": v["atype"].to_numpy(),
                         "tilting unit": st["any_tilting"].to_numpy(),
                         "fixed + tilting": (st["any_tilting"] & st["any_fixed"]).to_numpy(),
                         "ducted unit": st["any_ducted"].to_numpy(),
                         "more than 8 units": (units > 8).astype("boolean").where(units.notna(), pd.NA).to_numpy(),
                         "units on exactly\ntwo stations": (stations == 2).astype("boolean")
                         .where(stations.notna(), pd.NA).to_numpy()})
    g = feat.groupby("atype")
    tab = g.agg(lambda s_: float(s_.dropna().astype(float).mean()) if s_.notna().any() else np.nan)
    tab = tab.reindex(order).astype(float)
    read = g["tilting unit"].agg(lambda s_: int(s_.notna().sum())).reindex(order)
    tot = feat.groupby("atype").size().reindex(order)
    mat = tab.T
    ax2 = fig.add_subplot(gs[1])
    atlas._heat(ax2, mat, vmax=1)
    for t_ in ax2.texts:
        t_.set_fontsize(7)
    ax2.set_xticks(range(len(order)), [f"{c}\n{int(r_)}/{int(n_)}" for c, r_, n_ in zip(order, read, tot)],
                   rotation=0, ha="center", fontsize=7)
    ax2.tick_params(axis="y", labelsize=7.5)
    two = int((stations == 2).sum())
    ax2.set_xlabel(f"class · aircraft read / total — cells: share of the class with the feature\n"
                   f"(corpus: {two} of {int(stations.notna().sum())} aircraft carry their units on "
                   f"exactly two stations)", fontsize=7)
    names = [f"{c} {metrics.ARCH_NAMES.get(c, c)}" for c in order]
    key = "\n".join(" · ".join(names[k:k + 5]) for k in range(0, len(names), 5))
    _lf._panel_note(ax2, ax2, "Classes: " + key + "\nUnit: unique aircraft (" + str(len(v)) +
                    "); units and stations read where a propulsor record exists\nSource: human "
                    "labelling (G1 class, M1-M3 cards)", fontsize=6.8)
    # (ii) the merged ducting panel, with room above it for the notes of (i)
    ax3 = fig.add_subplot(outer[1])
    _duct_merged(ax3, tables)
    ax3.set_title("(ii) Ducting per propulsive-unit band: how many aircraft duct (bar height) and "
                  "how much of each is ducted (the split)", fontsize=9)
    _duct_source(ax3, tables)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-26 — chapter 3, sections 3.3 and 3.4 (sm_text_ch3b). Three figures, each read from a
# table ``sm_open.ch3b_tables`` writes, so a point on a figure and a number in the prose cannot
# disagree: the class configurations on the proposed rules (C63-C66), the one move of the
# tilting classes as a trajectory (C88, C91, C92, C95) and the boom and duct traces (C82, C93).
# Every window before 2016 is drawn faded behind a line and labelled "few aircraft" (§6).
# --------------------------------------------------------------------------
_CH3B_W = ["<= 2011", "2012-15", "2016-19", "2020-23"]
_CH3B_WL = ["≤2011", "12–15", "16–19", "20–23"]
_CH3B_FEW = 2                       # the first two windows are the faded ones


def _few_band(ax, top_text: bool = True) -> None:
    """Grey the two early windows behind a vertical line and say why (§6)."""
    ax.axvspan(-0.5, _CH3B_FEW - 0.5, color=GRID, alpha=0.55, zorder=0, lw=0)
    ax.axvline(_CH3B_FEW - 0.5, color=MUTED, lw=0.8, ls="--", zorder=1)
    if top_text:
        ax.text(0.5, 0.985, "few aircraft", transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=6.5, color=INK2)


def _note_under(host, axes, text: str, fontsize: float = 6.8) -> None:
    """A source / unit note hung under the lowest drawn element of ``axes`` (tick labels and
    legends included), starting at the left edge of ``host`` — ``la_figures._panel_note`` for a
    panel whose legend sits under its axis."""
    from matplotlib.transforms import Bbox

    def _foot(rend):
        hb = host.get_window_extent(rend)
        ys = [hb.y0]
        for a in axes:                      # not a.get_tightbbox: it would measure this note too
            tb = a.xaxis.get_tightbbox(rend)
            if tb is not None:
                ys.append(tb.y0)
            leg = a.get_legend()
            if leg is not None:
                ys.append(leg.get_window_extent(rend).y0)
        y0 = min(ys)
        return Bbox([[hb.x0, y0], [hb.x1, y0]])
    host.annotate(text, xy=(0, 0), xycoords=_foot, xytext=(0, -3), textcoords="offset points",
                  ha="left", va="top", fontsize=fontsize, color=INK2, annotation_clip=False)


def _tint(color, k: float):
    """``color`` mixed with white: k = 1 the colour itself, k = 0 white."""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(color)
    return (1 - k * (1 - r), 1 - k * (1 - g), 1 - k * (1 - b))


#: legend words for the configurations of panel (ii): the class name is the panel title, so the
#: repeated head of each configuration is dropped
_CFG_LEGEND = {
    "SLC": lambda s: s.replace("lift units ", "", 1),
    "TR": lambda s: (s.replace("two or more tilting sets", "2+ tilting sets")
                     .replace("two or more stations", "2+ stations")),
    "CVT": lambda s: s.replace("fixed units ", "fixed "),
}


def panel_class_configs_b(tables: Dict[str, pd.DataFrame], path: Path,
                          rules_set: Optional[str] = None) -> Path:
    """3.3 on the rule set ``sm_open.CLASS_RULES_SET``: (i) the share of each class in its most
    common configuration per window, with the configurations observed and possible printed at
    the last point; (ii) for Lift + Cruise, Tilt Rotor and CVT, the whole composition of the class
    per window — the bottom block is the configuration that leads in 2020-23, so the reader sees
    whether the leader holds, grows or changes hands."""
    from . import sm_open
    rs = rules_set or sm_open.CLASS_RULES_SET
    t = tables["la_class_configs_brief"]
    t = t[t["rule set"].astype(str).eq(rs)].copy()
    for c in ("aircraft", "possible configurations", "distinct configurations", "share in it"):
        t[c] = _num(t, c)
    mix = tables["la_class_config_mix"]
    mix = mix[mix["rule set"].astype(str).eq(rs)].copy()
    mix["aircraft"] = _num(mix, "aircraft")
    fig = plt.figure(figsize=(W, 5.9))
    outer = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.15], hspace=0.62)
    ax = fig.add_subplot(outer[0])
    x = np.arange(len(_CH3B_W))
    _few_band(ax)
    ends = []
    for code in sm_open.CH3B_CLASSES:
        sub = t[t["code"].eq(code)].set_index("window").reindex(_CH3B_W)
        y = sub["share in it"].to_numpy(dtype=float)
        ok = np.isfinite(y)
        mk, ls = _lf._cs(code)
        col = _lf._color(code)
        ax.plot(x[ok], y[ok], ls=ls, color=col, lw=1.4, zorder=3)
        for xi in x[ok]:
            early = xi < _CH3B_FEW
            ax.plot(xi, y[xi], marker=mk, ms=4.5, color=col, mfc="white" if early else col,
                    zorder=4, ls="none")
        last = sub.loc[_CH3B_W[-1]]
        if np.isfinite(last["share in it"]):
            k_, K_ = int(last["distinct configurations"]), last["possible configurations"]
            of = f"{k_} of {int(K_)}" if np.isfinite(K_) else f"{k_}"
            ends.append([float(last["share in it"]), f"{_lf._arch_name(code)} {last['share in it']:.0%} · "
                         f"{of} configurations", col])
    # the end labels, spread so none overlaps another
    ends.sort(key=lambda e: e[0])
    for k in range(1, len(ends)):
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + 0.075)
    for yv, lbl, col in ends:
        ax.text(x[-1] + 0.12, yv, lbl, fontsize=6.8, color=col, va="center", ha="left")
    ax.set_xlim(-0.5, x[-1] + 1.9)
    ax.set_xticks(x, _CH3B_WL, fontsize=7.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, max(0.85, ends[-1][0] + 0.05 if ends else 0.85))
    _hgrid(ax, "y")
    ax.set_title("(i) Share of each class in its most common configuration (hollow: few aircraft); "
                 "at the end, 2020-23 and the configurations observed of those the rule allows",
                 fontsize=8.5, loc="left")
    _lf._panel_note(ax, ax, "Unit: unique aircraft of the class in the window, with a complete "
                    "priority year; a window under 5 aircraft of the class is not drawn\n"
                    "Source: human labelling (G1 class; M1-M3 wing, boom and propulsor cards)",
                    fontsize=6.8)
    gs = outer[1].subgridspec(1, 3, wspace=0.28)
    axes = []
    titles = {"SLC": "(ii) Lift + Cruise: where\nthe lift units sit",
              "TR": "Tilt Rotor: how the\ntilting thrust is split",
              "CVT": "CVT: what tilts · where\nthe fixed units sit"}
    for j, code in enumerate(["SLC", "TR", "CVT"]):
        a = fig.add_subplot(gs[j])
        axes.append(a)
        m = mix[mix["code"].eq(code)]
        last = m[m["window"].eq(_CH3B_W[-1])].sort_values("aircraft", ascending=False)
        from .sm_open import _cfg_outside
        order = [c for c in last["configuration"] if not _cfg_outside(c)]
        keep = order[:3] if len(order) > 4 else order[:4]
        col = _lf._color(code)
        shades = [col, _tint(col, 0.6), _tint(col, 0.32), _tint(col, 0.14)]
        # the house black-and-white pass is switched off for this figure (it would put a dense
        # hatch on every block); the blocks carry their own light hatch instead, one per rank
        hatches = ["", "////", "....", "\\\\"]
        tot = m.groupby("window")["aircraft"].sum().reindex(_CH3B_W).fillna(0)
        bottom = np.zeros(len(_CH3B_W))
        series = [(cfg, m[m["configuration"].eq(cfg)].set_index("window")["aircraft"]
                   .reindex(_CH3B_W).fillna(0).to_numpy(dtype=float)) for cfg in keep]
        rest = m[~m["configuration"].isin(keep)].groupby("window")["aircraft"].sum()\
            .reindex(_CH3B_W).fillna(0).to_numpy(dtype=float)
        if rest.sum() > 0:
            series.append(("other configurations", rest))
        for k, (cfg, cnt) in enumerate(series):
            frac = np.divide(cnt, tot.to_numpy(), out=np.zeros_like(cnt), where=tot.to_numpy() > 0)
            other = cfg == "other configurations"
            fc = shades[k] if not other else "#e4e3df"
            lbl = _CFG_LEGEND.get(code, lambda s: s)(cfg)
            for xi in range(len(_CH3B_W)):
                a.bar(xi, frac[xi], bottom=bottom[xi], width=0.66, color=fc,
                      edgecolor=_tint(INK, 0.35) if k else INK, lw=0.35,
                      hatch="" if other else hatches[k % len(hatches)],
                      alpha=0.5 if xi < _CH3B_FEW else 1.0, zorder=3, label=lbl if xi == 0 else None)
                if frac[xi] >= 0.12:
                    a.text(xi, bottom[xi] + frac[xi] / 2, f"{frac[xi]:.0%}", ha="center", va="center",
                           fontsize=6.3, color="white" if k == 0 else INK, zorder=4,
                           bbox=None if k == 0 else dict(facecolor="white", edgecolor="none",
                                                         alpha=0.8, pad=0.6))
            bottom = bottom + frac
        a.set_xticks(range(len(_CH3B_W)), [f"{w}\nn {int(n)}" for w, n in zip(_CH3B_WL, tot)],
                     fontsize=6.5)
        a.axvline(_CH3B_FEW - 0.5, color=MUTED, lw=0.8, ls="--", zorder=5)
        a.set_ylim(0, 1.0)
        a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        a.tick_params(axis="y", labelsize=6.5)
        a.set_title(titles[code], fontsize=8, loc="left")
        a.legend(fontsize=6.3, loc="upper left", bbox_to_anchor=(-0.05, -0.2), frameon=False,
                 handlelength=1.1, labelspacing=0.3)
    fig._bw_off = True
    _note_under(axes[0], axes, "Unit: unique aircraft of the class in the window; bottom block = the "
                "configuration that leads in 2020-23; faded bars = few aircraft\nSource: human "
                "labelling (G1 class; M1-M3 wing, boom and propulsor cards)")
    return _save(fig, path)


def _drv_rows(tables, code: str) -> pd.DataFrame:
    t = tables["la_driver_windows"]
    return t[t["code"].astype(str).eq(code)].set_index("window").reindex(_CH3B_W)


def _test_text(row) -> str:
    rho = pd.to_numeric(row.get("rho"), errors="coerce")
    p = pd.to_numeric(row.get("p"), errors="coerce")
    if not np.isfinite(rho):
        return str(row.get("movement", ""))
    ps = "p < 0.001" if p < 0.001 else f"p {p:.3f}" if p < 0.01 else f"p {p:.2f}"
    return f"{row.get('movement', '')} (ρ {rho:+.2f}, {ps})"


def panel_driver_trajectory(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """3.4 — the one move of the tilting classes, in four panels (C92, with C88 and C91 folded in):
    (i) each class's centre per window — mean tilting sets against median propulsive units —
    joined by arrows; (ii) Tilt Rotor, median propulsive units by tilting sets; (iii) CVT, the
    ducted share inside each boom layout, with the share that carries units on booms; (iv)
    tilting sets per propulsive unit (mean) per window, with the trend test of every year."""
    fig = plt.figure(figsize=(W, 6.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1.0], hspace=0.72, wspace=0.3)
    # (i) the trajectory
    ax = fig.add_subplot(gs[0, 0])
    for code in ("SLC", "TR", "CVT"):
        d = _drv_rows(tables, code)
        xs = _num(d, "tilting sets (mean)").to_numpy(dtype=float)
        ys = _num(d, "propulsive units (median)").to_numpy(dtype=float)
        col = _lf._color(code)
        mk, _ls = _lf._cs(code)
        for k in range(len(_CH3B_W)):
            if not (np.isfinite(xs[k]) and np.isfinite(ys[k])):
                continue
            early = k < _CH3B_FEW
            ax.plot(xs[k], ys[k], marker=mk, ms=6, color=col, mfc="white" if early else col,
                    alpha=0.55 if early else 1.0, zorder=4, ls="none")
            dx = {"SLC": 0.07, "TR": 0.06, "CVT": -0.06}[code]
            ax.text(xs[k] + dx, ys[k] + 0.25, _CH3B_WL[k], fontsize=6.3, color=col,
                    ha="left" if dx > 0 else "right", alpha=0.6 if early else 1.0, zorder=5)
            if k + 1 < len(_CH3B_W) and np.isfinite(xs[k + 1]) and np.isfinite(ys[k + 1]):
                ax.annotate("", xy=(xs[k + 1], ys[k + 1]), xytext=(xs[k], ys[k]), zorder=3,
                            arrowprops=dict(arrowstyle="->", color=col, lw=1.3, shrinkA=4,
                                            shrinkB=4, alpha=0.4 if k + 1 < _CH3B_FEW else 1.0))
        ax.plot([], [], marker=mk, ls="-", color=col, ms=5, lw=1.3, label=_lf._arch_name(code))
    ax.legend(fontsize=6.4, loc="upper right", frameon=True, framealpha=0.9, edgecolor="none",
              handlelength=1.6)
    ax.set_xlim(-0.15, 2.15)
    ax.set_ylim(0, 10)
    ax.set_xlabel("tilting sets per aircraft (mean)", fontsize=7.5)
    ax.set_ylabel("propulsive units per aircraft (median)", fontsize=7.5)
    _hgrid(ax, "y")
    ax.grid(True, axis="x", lw=0.4, alpha=0.5)
    ax.set_title("(i) Each class's centre per window\n(hollow, faint arrow: few aircraft)",
                 fontsize=8.3, loc="left")
    _lf._panel_note(ax, ax, "Unit: unique aircraft of the class in the window (5 or more)\n"
                    "Source: human labelling (G1 class; M1-M3 cards)", fontsize=6.6)
    # (ii) Tilt Rotor: units by tilting sets
    ax = fig.add_subplot(gs[0, 1])
    lk = tables["la_driver_links"]
    k2 = lk[lk["link"].astype(str).str.startswith("Tilt Rotor")]
    med = _num(k2, "median").to_numpy(dtype=float)
    n = _num(k2, "aircraft").to_numpy(dtype=float)
    col = _lf._color("TR")
    bars = ax.bar(range(len(k2)), med, width=0.6, color=col, zorder=3)
    for i_, (m_, n_) in enumerate(zip(med, n)):
        ax.text(i_, m_ + 0.2, f"{m_:g} units\nn = {int(n_)}", ha="center", va="bottom", fontsize=6.8)
    ax.set_xticks(range(len(k2)), list(k2["group"].astype(str)), fontsize=7.5)
    ax.set_xlabel("tilting sets on the aircraft", fontsize=7.5)
    ax.set_ylabel("propulsive units (median)", fontsize=7.5)
    ax.set_ylim(0, float(np.nanmax(med)) + 2.6)
    _hgrid(ax, "y")
    ax.set_title("(ii) Tilt Rotor: propulsive units\nby number of tilting sets", fontsize=8.3,
                 loc="left")
    _lf._panel_note(ax, ax, f"Unit: Tilt Rotor aircraft with a unit count ({int(np.nansum(n))}), "
                    "all years\nSource: human labelling (M3 cards)", fontsize=6.6)
    # (iii) CVT: ducting by boom layout
    ax = fig.add_subplot(gs[1, 0])
    d = _drv_rows(tables, "CVT")
    x = np.arange(len(_CH3B_W))
    _few_band(ax)
    colc = _lf._color("CVT")
    tests = lk[lk["link"].astype(str).str.startswith("CVT")].set_index("group")
    series = [("share of CVT with units on booms", _num(d, "share with units on booms"), colc, "-", "^"),
              ("ducted, with units on booms: " + _test_text(tests.loc["units on booms"]),
               _num(d, "ducted share, units on booms"), INK, "--", "s"),
              ("ducted, without: " + _test_text(tests.loc["no units on booms"]),
               _num(d, "ducted share, no units on booms"), INK, "-", "s")]
    for lbl, s, c, ls, mk in series:
        y = s.to_numpy(dtype=float)
        ok = np.isfinite(y)
        ax.plot(x[ok], y[ok], ls=ls, color=c, lw=1.3, label=lbl, zorder=3)
        for xi in x[ok]:
            ax.plot(xi, y[xi], marker=mk, ms=4.5, color=c,
                    mfc="white" if (xi < _CH3B_FEW or ls == "--") else c, ls="none", zorder=4)
    nb = _num(d, "aircraft, units on booms").to_numpy(dtype=float)
    nn = _num(d, "aircraft, no units on booms").to_numpy(dtype=float)
    ax.set_xticks(x, [f"{w}\n{int(a)} · {int(b)}" for w, a, b in zip(_CH3B_WL, nb, nn)], fontsize=6.5)
    ax.set_xlabel("window · CVT with units on booms · without", fontsize=6.8)
    _drv_pct(ax)
    _hgrid(ax, "y")
    ax.set_title("(iii) CVT: ducted share by boom layout,\nand the share with units on booms",
                 fontsize=8.3, loc="left")
    ax.legend(fontsize=6.4, loc="upper left", bbox_to_anchor=(-0.02, -0.3), frameon=False, ncol=1)
    _note_under(ax, [ax], "Trend: ducting against the priority year, every year to 2023\n"
                "Unit: CVT aircraft; a ducted share needs 5 of the layout\nSource: human labelling "
                "(M3 cards)", fontsize=6.6)
    # (iv) tilting sets per propulsive unit
    ax = fig.add_subplot(gs[1, 1])
    su = tables["la_sets_per_unit_brief"]
    su = su[su["measure"].astype(str).eq("tilting sets per propulsive unit")]
    _few_band(ax)
    said = []
    for code, lbl, col, ls, mk in (("TR", "Tilt Rotor", _lf._color("TR"), "--", "s"),
                                   ("CVT", "CVT", _lf._color("CVT"), "-.", "^"),
                                   ("ALL5", "five classes pooled", MUTED, ":", "o")):
        r = su[su["code"].astype(str).eq(code)]
        if not len(r):
            continue
        y = r[_CH3B_WL].iloc[0].map(lambda v: pd.to_numeric(v, errors="coerce")).to_numpy(dtype=float)
        ok = np.isfinite(y)
        ax.plot(x[ok], y[ok], ls=ls, color=col, lw=1.3, label=f"{lbl}: {_test_text(r.iloc[0])}",
                zorder=3)
        for xi in x[ok]:
            ax.plot(xi, y[xi], marker=mk, ms=4.5, color=col, mfc="white" if xi < _CH3B_FEW else col,
                    ls="none", zorder=4)
        said.append(lbl)
    ax.set_xticks(x, _CH3B_WL, fontsize=7)
    ax.set_ylim(0, 0.75)
    _hgrid(ax, "y")
    ax.set_ylabel("tilting sets per propulsive unit (mean)", fontsize=7.2)
    ax.set_title("(iv) Tilting sets per propulsive unit\n(mean per aircraft)", fontsize=8.3,
                 loc="left")
    ax.legend(fontsize=6.4, loc="upper left", bbox_to_anchor=(-0.02, -0.13), frameon=False, ncol=1)
    _note_under(ax, [ax], "Trend: against the priority year, every year to 2023\n"
                "Unit: aircraft of the class with a unit count\nSource: human labelling (M3 cards)",
                fontsize=6.6)
    return _save(fig, path)


def panel_driver_traces_b(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """3.4 — two traces per class and window, early windows faded: (i) the share of aircraft that
    carry units on booms (C93, the boom trace), (ii) the share with a ducted unit."""
    from . import sm_open
    t = tables["la_driver_windows"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 2.75))
    x = np.arange(len(_CH3B_W))
    for ax, col_name, title in ((axs[0], "share with units on booms", "(i) Share of aircraft that "
                                 "carry units on booms"),
                                (axs[1], "share with a ducted unit", "(ii) Share of aircraft with "
                                 "a ducted unit")):
        _few_band(ax)
        for code in sm_open.CH3B_CLASSES:
            d = t[t["code"].astype(str).eq(code)].set_index("window").reindex(_CH3B_W)
            y = _num(d, col_name).to_numpy(dtype=float)
            ok = np.isfinite(y)
            mk, ls = _lf._cs(code)
            c = _lf._color(code)
            ax.plot(x[ok], y[ok], ls=ls, color=c, lw=1.3, zorder=3, label=_lf._arch_name(code))
            for xi in x[ok]:
                ax.plot(xi, y[xi], marker=mk, ms=4.2, color=c, mfc="white" if xi < _CH3B_FEW else c,
                        ls="none", zorder=4)
        ax.set_xticks(x, _CH3B_WL, fontsize=7.2)
        _drv_pct(ax)
        _hgrid(ax, "y")
        ax.set_title(title, fontsize=8.3, loc="left")
    axs[0].legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, -0.13), ncol=5, frameon=False,
                  handlelength=1.8, columnspacing=1.0)
    for ax, what in ((axs[0], "stations"), (axs[1], "ducted flag")):
        _note_under(ax, [axs[0]], "Unit: aircraft of the class in the window (5 or more)\n"
                    f"Source: human labelling (M3 cards: {what})", fontsize=6.6)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-26, chapter-3 review (C53, C54, C57) — the dominant-design test at the four levels
# --------------------------------------------------------------------------
#: the colour of a condition MET, on every chapter-3 panel (C57: "flag the points that are met in
#: another colour"); the red of the palette, so the black-and-white pass knows it
MET = CAT[7]
#: the four levels as the panels title them (old level id -> printed name)
DD_LEVEL_TITLES = [("A0", "C\nclass"), ("A1t", "C·W·T\nclass + wings + tilt"),
                   ("A0c", "C·U\nclass + units"), ("family_b", "F\nLift + Cruise family")]


def panel_family_yearly(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Condition 1 on the family F, per priority year 2008-2023, on the two bases of the author's
    ruling (C53): the aircraft with a patent in force (main) and every aircraft of the year.
    The years whose in-force base holds fewer than the trend minimum are greyed behind a line;
    two consecutive years above the 50 % line are ringed in the MET colour. Under each year: the
    aircraft in force · all aircraft, and the share of the in-force aircraft whose live patent is
    granted (a low share = a base still made of pending applications). POST HOC family."""
    t = tables["la_family_yearly"].copy()
    for c in ("priority year", "aircraft", "F share", "aircraft in force", "F share in force",
              "in force with a granted patent"):
        t[c] = _num(t, c)
    t = t.sort_values("priority year")
    yrs = t["priority year"].astype(int).to_numpy()
    read = t["read, in force"].astype(str).eq("True").to_numpy()
    first = int(yrs[read][0]) if read.any() else int(yrs[0])
    fig, ax = plt.subplots(figsize=(W, 2.85))
    ax.axvspan(yrs[0] - 0.5, first - 0.5, color=GRID, alpha=0.75, zorder=0, lw=0)
    ax.axvline(first - 0.5, color=MUTED, lw=0.9, zorder=1)
    ax.text((yrs[0] + first - 1) / 2, 0.955, f"few aircraft in force\n(under {_lt.TREND_MIN} a year): not read",
            ha="center", va="top", fontsize=7, color=INK2, transform=ax.get_xaxis_transform())
    fi, fa = t["F share in force"].to_numpy(), t["F share"].to_numpy()
    read_all = t["read, all"].astype(str).eq("True").to_numpy()
    # the two bases: faded where the year is not read on that base
    for y_, col, ls, mk, lab, rd in ((fi, CAT[0], "-", "o", "aircraft with a patent in force (main)", read),
                                     (fa, INK2, "--", "s", "all aircraft of the year", read_all)):
        lw = 1.7 if ls == "-" else 1.3
        ax.plot(yrs[yrs <= first], y_[yrs <= first], color=col, ls=ls, lw=lw, alpha=0.35, zorder=3)
        ax.plot(yrs[yrs >= first], y_[yrs >= first], color=col, ls=ls, lw=lw, zorder=3, label=lab)
        ax.plot(np.where(rd, yrs, np.nan), np.where(rd, y_, np.nan), ls="", marker=mk, ms=4.6,
                color=col, mfc=col if ls == "-" else SURFACE, mec=col, zorder=4)
        ax.plot(np.where(~rd, yrs, np.nan), np.where(~rd, y_, np.nan), ls="", marker=mk, ms=4.0,
                color=col, mfc=SURFACE, mec=col, alpha=0.45, zorder=4)
    ax.axhline(0.5, color=INK, lw=1.1, ls=(0, (4, 2)), zorder=2)
    ax.text(yrs[-1] + 0.45, 0.505, "50 %", ha="right", va="bottom", fontsize=7.5, color=INK)
    # two consecutive read years above the line, on the main base: the condition met
    over = [int(y) for y, s, r in zip(yrs, fi, read) if r and s > 0.5]
    pairs = [(a, b) for a, b in zip(over[:-1], over[1:]) if b == a + 1]
    met = sorted({x for p in pairs for x in p})
    if met:
        ax.axvspan(met[0] - 0.5, met[-1] + 0.5, color=MET, alpha=0.10, zorder=0, lw=0)
        mi = [list(yrs).index(y) for y in met]
        ax.plot(yrs[mi], fi[mi], "o", ms=11, mfc="none", mec=MET, mew=1.8, zorder=5,
                label="two consecutive years above 50 %: met")
        ax.text((met[0] + met[-1]) / 2, 0.97, f"condition 1 met,\nin force: {met[0]}–{str(met[-1])[-2:]}",
                ha="center", va="top", fontsize=7.5, color=MET, fontweight="bold",
                transform=ax.get_xaxis_transform())
        for k, y in enumerate(met):
            i = list(yrs).index(y)
            side = -1 if k == 0 else 1
            ax.annotate(f"{100 * fi[i]:.1f} %", (y, fi[i]), textcoords="offset points",
                        xytext=(side * 8, 7), ha="right" if side < 0 else "left", va="bottom",
                        fontsize=7, color=CAT[0], fontweight="bold")
            ax.annotate(f"{100 * fa[i]:.1f} %", (y, fa[i]), textcoords="offset points",
                        xytext=(side * 11, -9), ha="right" if side < 0 else "left", va="top",
                        fontsize=7, color=INK2, zorder=6, bbox=dict(fc="white", ec="none", pad=0.4))
    ax.set_ylim(0, 0.85)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("share of the year's aircraft\nin the family F", fontsize=8)
    _hgrid(ax, "y")
    ni = t["aircraft in force"].astype(int).to_numpy()
    na = t["aircraft"].astype(int).to_numpy()
    gr = t["in force with a granted patent"].to_numpy()
    ax.set_xticks(yrs, [f"{y}\n{a}·{b}\n{g:.0%}" if np.isfinite(g) else f"{y}\n{a}·{b}\n–"
                        for y, a, b, g in zip(yrs, ni, na, gr)], fontsize=7)
    for lab, r in zip(ax.get_xticklabels(), read):
        if not r:
            lab.set_color(MUTED)
    ax.set_xlim(yrs[0] - 0.6, yrs[-1] + 0.6)
    ax.text(-0.01, -0.105, "aircraft in force · all", transform=ax.transAxes, ha="right", va="top",
            fontsize=7, color=INK2)
    ax.text(-0.01, -0.165, "in force with a grant", transform=ax.transAxes, ha="right", va="top",
            fontsize=7, color=INK2)
    ax.set_xlabel("priority year", fontsize=8)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.30), frameon=False,
              handlelength=2.0, ncol=3, columnspacing=1.2)
    ax.annotate("Source: human labelling (class; family F, post hoc) · PatSeer priority year and\n"
                "legal status at the snapshot (2026-06-08)", xy=(0, 0), xycoords="axes fraction",
                xytext=(0, -78), textcoords="offset points", ha="left", va="top", fontsize=7,
                color=INK2)
    ax.set_title("Condition 1 on the Lift + Cruise family F, per priority year, on two bases",
                 fontsize=9)
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    return _save(fig, path)


def panel_dd_conditions(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Conditions 2 and 3 of the dominant-design test at the four levels, complete windows read,
    the partial window hatched. Top: ²D per window against its permutation band (condition 2).
    Bottom: ΔQ per window against its band under both weightings (condition 3); Q uses no
    archetype, so C, C·U and F share one panel (the same aircraft) and C·W·T has its own (two
    aircraft fewer). Every level-window where a condition is met is drawn in the MET colour."""
    b = tables["la_dd_balance"].copy()
    q = tables["la_dd_form"].copy()
    for c in ("D2", "D2 low", "D2 high", "D2 permutation low", "D2 permutation high", "aircraft"):
        b[c] = _num(b, c)
    for c in ("ΔQ", "ΔQ permutation low", "ΔQ permutation high", "aircraft"):
        q[c] = _num(q, c)
    x = np.arange(len(WINDOW_NAMES))
    fig = plt.figure(figsize=(W, 4.7))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.0], hspace=1.15, wspace=0.45)
    top = [fig.add_subplot(gs[0, k]) for k in range(4)]
    bot = [fig.add_subplot(gs[1, 0:2]), fig.add_subplot(gs[1, 2:4])]
    for ax, (lvl, title) in zip(top, DD_LEVEL_TITLES):
        s = b[b["level"].eq(lvl)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, s["D2 permutation low"], s["D2 permutation high"], color=GRID, alpha=0.95,
                        zorder=1, label="permutation band (95 %)")
        ax.errorbar(x, s["D2"], yerr=[s["D2"] - s["D2 low"], s["D2 high"] - s["D2"]], marker="o",
                    ms=3.8, lw=1.4, capsize=1.8, color=INK, zorder=3, label="²D, rarefied to 40 (95 %)")
        hit = [i for i, w in enumerate(WINDOW_NAMES)
               if str(s["below band"].get(w, "")) == "True" and "partial" not in w]
        if hit:
            ax.plot(x[hit], s["D2"].to_numpy()[hit], "o", ms=7.5, color=MET, mec=INK, mew=0.8,
                    zorder=5, label="below the band: condition met")
        ax.set_title(title, fontsize=7.5, loc="left")
        ax.set_xticks(x, [_lf.WIN_SHORT.get(w, w) for w in WINDOW_NAMES], fontsize=7, rotation=50,
                      ha="right", rotation_mode="anchor")
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        ax.set_ylim(0, float(np.nanmax(s[["D2 high", "D2 permutation high"]].to_numpy())) * 1.15)
        _hgrid(ax, "y")
    top[0].set_ylabel("²D: large designs\nin play", fontsize=8)
    h2, l2 = [], []
    for ax in top:
        h, l = ax.get_legend_handles_labels()
        for hh, ll in zip(h, l):
            if ll not in l2:
                h2.append(hh)
                l2.append(ll)
    main, alt = _lt.Q_WEIGHTINGS
    for ax, (lvl, title) in zip(bot, (("A0", "C, C·U and F (the same aircraft)"),
                                      ("A1t", "C·W·T"))):
        s = q[q["level"].eq(lvl)]
        sm = s[s["weighting"].eq(main)].set_index("window").reindex(WINDOW_NAMES)
        su = s[s["weighting"].eq(alt)].set_index("window").reindex(WINDOW_NAMES)
        ax.fill_between(x, sm["ΔQ permutation low"], sm["ΔQ permutation high"], color=GRID,
                        alpha=0.95, zorder=1, label=f"permutation band, {main} weighting (main)")
        ax.plot(x, su["ΔQ permutation low"], color=MUTED, lw=0.9, ls=":", zorder=2,
                label=f"band edges, {alt} weighting")
        ax.plot(x, su["ΔQ permutation high"], color=MUTED, lw=0.9, ls=":", zorder=2)
        ax.axhline(0, color=MUTED, lw=0.8, zorder=2)
        ax.plot(x, sm["ΔQ"], marker="o", ms=3.8, lw=1.5, color=INK, zorder=4,
                label=f"ΔQ, {main} weighting (main)")
        ax.plot(x, su["ΔQ"], marker="^", ms=3.8, lw=1.2, color=MUTED, ls="--", zorder=4,
                label=f"ΔQ, {alt} weighting")
        hit = [i for i, w in enumerate(WINDOW_NAMES)
               if str(sm["below band"].get(w, "")) == "True" and "partial" not in w]
        if hit:
            ax.plot(x[hit], sm["ΔQ"].to_numpy()[hit], "o", ms=7.5, color=MET, mec=INK, mew=0.8,
                    zorder=5, label="below the band: condition met")
        n = sm["aircraft"]
        ax.set_xticks(x, [f"{_lf.WIN_SHORT.get(w, w)}\nn {int(n.get(w, 0))}" for w in WINDOW_NAMES],
                      fontsize=7)
        ax.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.55, zorder=0, hatch="//", lw=0)
        ax.set_title(title, fontsize=8)
        _hgrid(ax, "y")
    lo = float(np.nanmin(q[["ΔQ", "ΔQ permutation low"]].to_numpy()))
    hi = float(np.nanmax(q[["ΔQ", "ΔQ permutation high"]].to_numpy()))
    for ax in bot:
        ax.set_ylim(lo - 0.012, hi + 0.012)
    bot[0].set_ylabel("ΔQ: change in how unlike\ntwo aircraft are, against\nthe two earliest windows",
                      fontsize=7.5)
    h3, l3 = bot[0].get_legend_handles_labels()
    top[0].text(0.0, 1.42, "(i) Condition 2 — balance: ²D per window against its band",
                transform=top[0].transAxes, ha="left", va="bottom", fontsize=9, fontweight="bold")
    bot[0].text(0.0, 1.22, "(ii) Condition 3 — form: ΔQ per window against its band, both weightings",
                transform=bot[0].transAxes, ha="left", va="bottom", fontsize=9, fontweight="bold")
    top[0].legend(h2, l2, fontsize=7, loc="upper left", bbox_to_anchor=(0.0, -0.36), ncol=3,
                  frameon=False, handlelength=1.6, columnspacing=1.2)
    keep = [i for i, l in enumerate(l3) if "condition met" not in l]
    bot[0].legend([h3[i] for i in keep], [l3[i] for i in keep], fontsize=7, loc="upper left",
                  bbox_to_anchor=(0.0, -0.24), ncol=2, frameon=False, handlelength=1.8,
                  columnspacing=1.2)
    bot[0].annotate("Source: human labelling (class, wings, tilt, units, every field of the distance; family F "
                    "post hoc) · PatSeer priority year ·\n200 permutations, seed 42 · hatched: the partial "
                    "window, not read", xy=(0, 0), xycoords="axes fraction", xytext=(0, -66),
                    textcoords="offset points", ha="left", va="top", fontsize=7, color=INK2)
    fig._bw_keep_dash = True
    fig._bw_keep_marker = True
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-26 — chapter 4 of the brief (sm_text_ch4, comments D4-D20): who files, how
# concentrated a class is, first-time against returning filers, successions, the index's money
# --------------------------------------------------------------------------
_CH4_FILER = [("Named company", "named companies", CAT[0]),
              ("University / institute", "universities / institutes", CAT[3]),
              ("Individual inventor", "individual inventors", CAT[1])]
_CH4_SRC = "Sources: PatSeer (assignee, priority date) · human labelling"


def _ch4_note(ax, text: str) -> None:
    _lf._panel_note(ax, ax, text, fontsize=6.8)


def panel_who_files(tables: Dict[str, pd.DataFrame], path: Path, ds) -> Optional[Path]:
    """(i) cumulative share of the analysis set held by the named organisations ranked by aircraft,
    cut at 10 / 5 / 2 aircraft per firm, index firms marked; (ii) aircraft (and, for all years,
    primary patents) by filer type, all years and per window; (iii) named organisations active per
    window: filing their first eVTOL aircraft there, or returning. Replaces the three-panel
    ``coverage`` figure, ``la_filer_mix`` and ``la_filers_by_window`` (D4, D5, D8-D10)."""
    if ds is None:
        return None
    v = _lt.base(ds)
    sizes = _lt.firm_sizes(v)
    listed = _lt.ari_listed(v)
    seg = tables["la_coverage_segments"].copy()
    for c in ("firms", "aircraft", "cumulative firms"):
        seg[c] = _num(seg, c)
    fm = tables["la_filer_mix"].copy()
    fw = tables["la_filers_by_window"].copy()
    total = len(v)
    cum = sizes.cumsum() / total
    rank = np.arange(1, len(sizes) + 1)

    fig = plt.figure(figsize=(W, 6.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1], width_ratios=[1.45, 1], hspace=0.72,
                          wspace=0.28, left=0.1, right=0.99, top=0.95, bottom=0.12)
    ax = fig.add_subplot(gs[0, :])
    ax.step(rank, cum, where="post", color=BLUE(0.8), lw=2, zorder=3)
    edges = [0] + seg["cumulative firms"].astype(int).tolist()
    n_narrow = 0
    for i, (_, r) in enumerate(seg.iterrows()):
        x0, x1 = edges[i], edges[i + 1]
        if i:
            ax.axvline(x0, color=GRID, lw=1, zorder=1)
        ax.annotate("", xy=(x0 + 0.2, 0.05), xytext=(x1 - 0.2, 0.05),
                    arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7, shrinkA=0, shrinkB=0))
        mid = (x0 + x1) / 2
        txt = f"{int(r['firms'])} firms · {int(r['aircraft'])} aircraft\n({r['aircraft per firm']} aircraft each)"
        y_mid = float(cum.iloc[min(int(round(mid)), len(cum)) - 1])
        if x1 - x0 < 45:
            ylab = 0.99 - 0.16 * n_narrow
            ax.plot([6.5 + 6.0 * n_narrow, mid], [ylab, y_mid + 0.05], color=INK2, lw=0.6, zorder=1)
            ax.text(6.0, ylab, txt, ha="left", va="top", fontsize=7, color=INK, linespacing=1.2,
                    bbox=dict(fc="white", ec=GRID, lw=0.4, pad=0.3, alpha=0.96), zorder=4)
            n_narrow += 1
        else:
            ax.text(mid, float(cum.iloc[x0 - 1]) - 0.07, txt, ha="center", va="top", fontsize=7,
                    color=INK, linespacing=1.2,
                    bbox=dict(fc="white", ec=GRID, lw=0.4, pad=0.3, alpha=0.96), zorder=4)
        y1 = float(cum.iloc[x1 - 1])
        ax.text(x1 + (0.6 if i == 0 else 0), y1 + (-0.02 if i == 0 else 0.012), f"{y1:.0%}",
                ha="left" if i == 0 else "right", va="top" if i == 0 else "bottom", fontsize=7,
                color=BLUE(0.95), fontweight="bold", zorder=5)
    share = sizes.sum() / total
    ax.axhline(share, color=INK, lw=1, ls="--")
    ax.text(len(sizes), share + 0.012, f"all {len(sizes)} named organisations: {int(sizes.sum())} "
            f"aircraft, {share:.0%} ", ha="right", va="bottom", fontsize=7.5,
            bbox=dict(fc="white", ec="none", pad=0.3))
    ax.axhline(1, color=GRID, lw=0.8)
    ax.text(len(sizes), 1.0, f"all {total} aircraft (individual inventors hold the rest) ",
            ha="right", va="bottom", fontsize=7.5, color=INK2)
    pts = [(i + 1, float(cum.iloc[i])) for i, f in enumerate(sizes.index) if f in listed]
    if pts:
        ax.plot([p_[0] for p_ in pts], [p_[1] for p_ in pts], ls="", marker="o", ms=4.5,
                color=CAT[1], zorder=6,
                label=f"rated by the AAM Reality Index ({len(pts)} firms)")
        ax.legend(fontsize=7, loc="lower right", bbox_to_anchor=(1.0, 0.13), framealpha=0.92)
    ax.set_xlim(0, len(sizes) + 1)
    ax.set_ylim(0, 1.07)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("named organisations (companies, universities, institutes) ranked by unique "
                  "aircraft, largest first", fontsize=7.5)
    ax.set_ylabel("cumulative share of\nthe 665 aircraft", fontsize=8)
    ax.set_title("(i) How much of the record the largest filers hold", fontsize=8.8)
    _hgrid(ax, "both")
    _ch4_note(ax, _CH4_SRC + " · AAM Reality Index (the firms it has rated) · unit: unique aircraft")

    # (ii) filer type: all years in patents and in aircraft, then per window
    ax2 = fig.add_subplot(gs[1, 0])
    names = {"Named company": "Named companies", "University / institute": "Universities and institutes",
             "Individual inventor": "Individual inventors"}
    fmi = fm.set_index("filer")
    cols = [("all,\npatents", {k: float(_num(fm, "primary patents")[fm["filer"].eq(v_)].iloc[0])
                                     for k, v_ in names.items()}),
            ("all,\naircraft", {k: float(_num(fm, "unique aircraft")[fm["filer"].eq(v_)].iloc[0])
                                      for k, v_ in names.items()})]
    fw_n = _num(fw, "unique aircraft")
    for _, r in fw.iterrows():
        n = float(_num(pd.DataFrame([r]), "unique aircraft").iloc[0])
        ind = float(pd.to_numeric(r["share individual inventors"], errors="coerce"))
        uni = float(pd.to_numeric(r["share universities / institutes"], errors="coerce"))
        cols.append((f"{_lf.WIN_SHORT.get(r['window'], r['window'])}",
                     {"Named company": (1 - ind - uni) * n, "University / institute": uni * n,
                      "Individual inventor": ind * n}))
    x = np.arange(len(cols))
    bottom = np.zeros(len(cols))
    tot = np.array([sum(c[1].values()) for c in cols])
    for key, lab, col in _CH4_FILER:
        vals = np.array([c[1][key] for c in cols]) / tot
        bars = ax2.bar(x, vals, bottom=bottom, width=0.72, color=col, edgecolor=SURFACE, lw=1.0,
                       label=lab, zorder=3)
        for xi, (b0, val) in enumerate(zip(bottom, vals)):
            if "24" in cols[xi][0] and "*" in cols[xi][0]:
                bars[xi].set_alpha(0.45)
            if val >= 0.08:
                ax2.text(xi, b0 + val / 2, f"{val:.0%}", ha="center", va="center", fontsize=6.8,
                         color="white", fontweight="bold", zorder=5,
                         bbox=dict(fc=col, ec="none", pad=0.4, alpha=0.85))
        bottom += vals
    ax2.axvline(1.5, color=INK2, lw=0.8, ls=":")
    ax2.set_xticks(x, [f"{c[0]}\nn {int(round(t_))}" for c, t_ in zip(cols, tot)], fontsize=6.5)
    ax2.set_ylim(0, 1)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.spines[["left", "bottom"]].set_visible(False)
    ax2.set_ylabel("share", fontsize=8)
    ax2.set_title("(ii) Who files, all years and per priority window", fontsize=8.8)
    ax2.legend(fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.36), ncol=3,
               handlelength=1.2, columnspacing=0.8, frameon=False)
    ax2.annotate(_CH4_SRC + " · unit: unique aircraft\n(first two bars: primary patents, then "
                 "aircraft) · * partial window", xy=(0, 0), xycoords="axes fraction",
                 xytext=(0, -62), textcoords="offset points", ha="left", va="top", fontsize=6.8,
                 color=INK2)

    # (iii) named organisations active per window: first eVTOL aircraft here, or returning
    ax3 = fig.add_subplot(gs[1, 1])
    xw = np.arange(len(fw))
    new = _num(fw, "new firms").to_numpy()
    cont = _num(fw, "continuing firms").to_numpy()
    b1 = ax3.bar(xw, new, width=0.66, color=BLUE(0.75), zorder=3, edgecolor=SURFACE, lw=1.0,
                 label="first eVTOL aircraft in the window")
    b2 = ax3.bar(xw, cont, bottom=new, width=0.66, color=BLUE(0.35), zorder=3, edgecolor=SURFACE,
                 lw=1.0, label="filed in an earlier window")
    for xi, (a_, c_) in enumerate(zip(new, cont)):
        if "partial" in str(fw["window"].iloc[xi]):
            b1[xi].set_alpha(0.45)
            b2[xi].set_alpha(0.45)
        ax3.text(xi, a_ + c_ + 1.5, f"{int(a_)} + {int(c_)}", ha="center", va="bottom",
                 fontsize=6.8, color=INK)
    ax3.set_xticks(xw, [_lf.WIN_SHORT.get(w_, w_) for w_ in fw["window"]], fontsize=6.8)
    ax3.set_ylim(0, float((new + cont).max()) * 1.45)
    ax3.set_ylabel("named organisations filing", fontsize=8)
    ax3.set_title("(iii) Filing for the first time,\nor filed before", fontsize=8.8)
    _hgrid(ax3, "y")
    ax3.legend(fontsize=6.8, loc="upper left", handlelength=1.2, frameon=False)
    ax3.annotate(_CH4_SRC + "\nunit: named organisation · * partial window", xy=(0, 0),
                 xycoords="axes fraction", xytext=(0, -30), textcoords="offset points", ha="left",
                 va="top", fontsize=6.8, color=INK2)
    return _save(fig, path)


def panel_one_firm(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """(i) per class of twenty aircraft or more: the largest filer's share over all years (bar),
    the largest share one filer holds inside a single complete window (diamond), and the
    effective number of filers on the tick; (ii) the firms whose removal moves a class share
    most, over all years (bar) and inside one window (diamond). Replaces ``filer_weight``,
    ``firm_influence`` and ``la_class_filer_weight`` (D12, D13, D23)."""
    t = tables["la_class_concentration_brief"].copy()
    for c in ("aircraft", "filers", "effective filers", "its share", "largest share inside one window"):
        t[c] = _num(t, c)
    lev = tables["la_firm_leverage"].copy()
    for c in ("shift if the firm is dropped (pp)", "largest shift inside one window (pp)", "unique aircraft"):
        lev[c] = _num(lev, c)
    lev["mag"] = lev["shift if the firm is dropped (pp)"].abs()
    lev = lev.sort_values("mag", ascending=False).head(8)
    word = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT", "TW": "Tilt Wing",
            "MR": "Multirotor", "PTC": "Pitch-to-Cruise", "TB": "Tilt Body", "HB": "Hoverbike",
            "DS": "Defl. Slipstream", "PFV": "Personal FV"}

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 4.1), gridspec_kw={"width_ratios": [1.25, 1],
                                                                        "wspace": 0.72})
    y = np.arange(len(t))
    hb = a1.barh(y + 0.13, t["its share"], height=0.34, color=BLUE(0.7), zorder=3,
                 label="all years")
    dm = a1.scatter(t["largest share inside one window"], y - 0.24, marker="D", s=22, color=CAT[1],
                    zorder=5, edgecolor="white", lw=0.6, label="inside one priority window")
    for yi, (_, r) in enumerate(t.iterrows()):
        who = str(r["largest filer"]).replace("an individual inventor's patent", "one inventor")
        a1.text(r["its share"] + 0.01, yi + 0.13, f"{who} {r['its share']:.0%}", va="center",
                fontsize=6.4, color=INK)
        if pd.notna(r["largest share inside one window"]):
            hw = str(r["held by"]).replace("an individual inventor's patent", "one inventor")
            a1.text(r["largest share inside one window"] + 0.014, yi - 0.24,
                    f"{r['largest share inside one window']:.0%}, {hw}, "
                    f"{_lf.WIN_SHORT.get(r['in window'], r['in window'])}",
                    va="center", fontsize=6.0, color=INK2)
    a1.set_yticks(y, [f"{word.get(c, c)} · {int(n)} aircraft\n{int(f)} filers ≈ {e:.0f} equal"
                      for c, n, f, e in zip(t["code"], t["aircraft"], t["filers"],
                                            t["effective filers"])], fontsize=6.6)
    a1.invert_yaxis()
    a1.set_xlim(0, 0.78)
    a1.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    a1.set_xlabel("share of the class's aircraft held by one filer", fontsize=7.5)
    a1.set_title("(i) The largest filer of each class", fontsize=8.8)
    _hgrid(a1, "x")
    _ch4_note(a1, _CH4_SRC + "\nunit: unique aircraft · classes of 20 aircraft or more ·\n"
              "windows of 10 aircraft or more; 2024-26 left out")

    y2 = np.arange(len(lev))
    a2.barh(y2 + 0.13, lev["mag"], height=0.34, color=BLUE(0.7), zorder=3)
    a2.scatter(lev["largest shift inside one window (pp)"], y2 - 0.24, marker="D", s=22,
               color=CAT[1], edgecolor="white", lw=0.6, zorder=5)
    for yi, (_, r) in enumerate(lev.iterrows()):
        a2.text(r["mag"] + 0.15, yi + 0.13,
                f"{word.get(r['class most moved'], r['class most moved'])} "
                f"{r['shift if the firm is dropped (pp)']:+.1f}", va="center", fontsize=6.2, color=INK)
        if pd.notna(r["largest shift inside one window (pp)"]) and r["largest shift inside one window (pp)"] > 0:
            a2.text(r["largest shift inside one window (pp)"] + 0.2, yi - 0.24,
                    f"{r['largest shift inside one window (pp)']:.1f}, "
                    f"{_lf.WIN_SHORT.get(r['that window'], r['that window'])}",
                    va="center", fontsize=6.0, color=INK2)
    a2.set_yticks(y2, [f"{f}\n{int(n)} aircraft" for f, n in zip(lev["firm"], lev["unique aircraft"])],
                  fontsize=6.6)
    a2.invert_yaxis()
    a2.set_xlim(0, max(float(lev["largest shift inside one window (pp)"].max()),
                       float(lev["mag"].max())) * 1.35)
    a2.set_xlabel("largest change of a class share\nwhen the firm is left out\n(percentage points)",
                  fontsize=7.5)
    a2.set_title("(ii) Leaving one firm out", fontsize=8.8)
    _hgrid(a2, "x")
    _ch4_note(a2, _CH4_SRC.replace(" · ", "\n", 1) + "\nunit: unique aircraft · the 8 firms\n"
              "that move a class share most")
    fig.legend([hb, dm], ["all years", "inside one priority window"], fontsize=7,
               loc="upper center", bbox_to_anchor=(0.5, 1.04), ncol=2, frameon=False,
               handlelength=1.2)
    return _save(fig, path)


_CH4_CLS = [("Lift + Cruise", "SLC"), ("Tilt Rotor", "TR"), ("CVT", "CVT"), ("Tilt Wing", "TW"),
            ("Multirotor", "MR"), ("other classes", "Other")]


def panel_entry_split(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """(i) class mix of the named organisations' aircraft: firms filing their first eVTOL aircraft
    in the window against firms that filed before, in the two windows with twenty returning
    aircraft or more, with the chi-square p and the p without the largest returning firm;
    (ii) Tilt Wing: its share of the entering firms against its share of the window's aircraft.
    Replaces ``sm_entry_all`` (D16-D18, D24)."""
    from .atlas import OTHER, ARCH_COLOR
    es = tables["la_entry_split"].copy()
    te = tables["la_entry_split_test"].copy()
    tw = tables["la_tw_entry"].copy()
    tested = te[_num(te, "p").notna()]
    wins = tested["window"].tolist()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.1), gridspec_kw={"width_ratios": [1.7, 1],
                                                                       "wspace": 0.3})
    rows, labels = [], []
    for wn in wins:
        for grp, lab in (("first-time filers", "first-time"), ("returning filers", "returning")):
            r = es[es["window"].eq(wn) & es["group"].eq(grp)].iloc[0]
            rows.append(r)
            labels.append(f"{_lf.WIN_SHORT.get(wn, wn)} {lab}\n{int(_num(pd.DataFrame([r]), 'aircraft').iloc[0])} aircraft")
    ypos = np.array([0, 1, 2.6, 3.6])[:len(rows)]
    left = np.zeros(len(rows))
    for name, code in _CH4_CLS:
        vals = np.array([float(pd.to_numeric(r[name], errors="coerce")) for r in rows])
        col = ARCH_COLOR.get(code, OTHER)
        a1.barh(ypos, vals, left=left, height=0.78, color=col, edgecolor=SURFACE, lw=1.0,
                label=name, zorder=3)
        for yi, (l0, val) in zip(ypos, zip(left, vals)):
            if val >= 0.09:
                a1.text(l0 + val / 2, yi, f"{val:.0%}", ha="center", va="center", fontsize=6.8,
                        color="white", fontweight="bold", zorder=5,
                        bbox=dict(fc=col, ec="none", pad=0.4, alpha=0.85))
        left += vals
    a1.set_yticks(ypos, labels, fontsize=6.8)
    a1.invert_yaxis()
    a1.set_xlim(0, 1)
    a1.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    a1.spines[["left", "bottom"]].set_visible(False)
    for k, (_, r) in enumerate(tested.iterrows()):
        p, p2 = float(_num(pd.DataFrame([r]), "p").iloc[0]), float(_num(pd.DataFrame([r]), "p without it").iloc[0])
        n_big = int(_num(pd.DataFrame([r]), "its aircraft").iloc[0])
        a1.text(1.0, ypos[2 * k] + 0.5 + 0.02, f"χ² p {p:.3f} · without {r['largest returning firm']} "
                f"({n_big} of the returning aircraft) p {p2:.2f}", ha="right", va="center",
                fontsize=6.5, color=INK2, transform=a1.get_yaxis_transform() if False else a1.transData)
    a1.set_title("(i) Class of the aircraft: first-time against returning filers", fontsize=8.8)
    a1.legend(fontsize=6.6, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3,
              handlelength=1.0, columnspacing=0.9, frameon=False)
    a1.annotate(_CH4_SRC + "\nunit: unique aircraft of named organisations · windows with 20\n"
                "or more returning aircraft", xy=(0, 0), xycoords="axes fraction", xytext=(0, -52),
                textcoords="offset points", ha="left", va="top", fontsize=6.8, color=INK2)

    x = np.arange(len(tw))
    ea = _num(tw, "Tilt Wing share of entrants").to_numpy()
    aa = _num(tw, "Tilt Wing share of the aircraft").to_numpy()
    ne = _num(tw, "entering with Tilt Wing").to_numpy()
    nf = _num(tw, "firms entering").to_numpy()
    a2.bar(x - 0.19, aa, width=0.36, color=CONTEXT, zorder=3, label="share of the window's aircraft")
    b2 = a2.bar(x + 0.19, ea, width=0.36, color=CAT[3], zorder=3, label="share of the entering firms")
    for b in b2:
        b.set_hatch("////")
    for xi in range(len(x)):
        a2.text(xi + 0.19, ea[xi] + 0.006, f"{int(ne[xi])}/{int(nf[xi])}", ha="center", va="bottom",
                fontsize=6.3, color=INK)
        a2.text(xi - 0.19, aa[xi] + 0.006, f"{aa[xi]:.0%}", ha="center", va="bottom", fontsize=6.3,
                color=INK2)
    a2.set_xticks(x, [_lf.WIN_SHORT.get(w_, w_) for w_ in tw["window"]], fontsize=7)
    a2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    a2.set_ylim(0, float(np.nanmax(np.concatenate([ea, aa]))) + 0.06)
    _hgrid(a2, "y")
    a2.set_title("(ii) Tilt Wing: entering firms\nagainst aircraft", fontsize=8.8)
    a2.legend(fontsize=6.6, loc="upper left", frameon=False, handlelength=1.2)
    a2.annotate("Sources: PatSeer (assignee, priority\ndate) · human labelling · unit: named\n"
                "organisation (hatched), unique aircraft\n(grey) · on the hatched bar: firms "
                "entering\nwith Tilt Wing / all firms entering",
                xy=(0, 0), xycoords="axes fraction", xytext=(0, -22), textcoords="offset points",
                ha="left", va="top", fontsize=6.8, color=INK2)
    return _save(fig, path)


def panel_successions(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Where a firm's next aircraft lands, by the class of the one before: one row per class of
    origin (ten successions or more), each row summing to 100 %; the diagonal (stays in the class)
    is boxed. Replaces ``la_tw_successions`` (D20)."""
    t = tables["la_succession_matrix"].copy()
    dest = [("→ SLC", "Lift +\nCruise"), ("→ TR", "Tilt\nRotor"), ("→ CVT", "CVT"),
            ("→ TW", "Tilt\nWing"), ("→ MR", "Multi-\nrotor"), ("→ PTC", "Pitch-to-\nCruise"),
            ("→ other", "other")]
    codes = ["SLC", "TR", "CVT", "TW", "MR", "PTC", None]
    M = np.array([[float(pd.to_numeric(r[c], errors="coerce")) for c, _ in dest] for _, r in t.iterrows()])
    fig, ax = plt.subplots(figsize=(W, 2.9))
    fig._bw_off = True
    ax.imshow(M, cmap=BLUE, vmin=0, vmax=0.75, aspect="auto")
    for i, (_, r) in enumerate(t.iterrows()):
        for j, (c, _) in enumerate(dest):
            val = M[i, j]
            ax.text(j, i, f"{val:.0%}" if val > 0 else "–", ha="center", va="center", fontsize=7.2,
                    color="white" if val >= 0.4 else INK, fontweight="bold" if codes[j] == r["code"] else None)
            if codes[j] == r["code"]:
                ax.add_patch(matplotlib.patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                                          ec=INK, lw=1.6, zorder=5))
        stay_wo = float(pd.to_numeric(r["stays without it"], errors="coerce"))
        ax.text(len(dest) - 0.35, i, f"{stay_wo:.0%} of {int(pd.to_numeric(r['successions without it']))}",
                ha="left", va="center", fontsize=7, color=INK2)
    ax.text(len(dest) - 0.35, -0.75, f"stays, without\n{t['firm left out'].iloc[0]}", ha="left",
            va="bottom", fontsize=6.6, color=INK2, linespacing=1.1)
    ax.set_xticks(range(len(dest)), [d[1] for d in dest], fontsize=7)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(t)), [f"{c.replace('Combined vectored thrust', 'CVT')}\n"
                                  f"{int(n)} successions · {int(f)} firms"
                                  for c, n, f in zip(t["class of origin"], _num(t, "successions"),
                                                     _num(t, "firms"))], fontsize=7)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel("class of the firm's\naircraft", fontsize=8)
    ax.set_xlabel("class of the same firm's next aircraft · the boxed cell: the next aircraft stays "
                  "in the class", fontsize=7.5)
    ax.annotate(_CH4_SRC + " · unit: succession = a named organisation's aircraft and its next "
                "one, in priority order", xy=(0, 0), xycoords="axes fraction", xytext=(0, -30),
                textcoords="offset points", ha="left", va="top", fontsize=6.8, color=INK2)
    return _save(fig, path)


_ARI_SHORT = {"Ascendance Flight Technologies": "Ascendance", "Wofei / Geely Aviation": "Wofei / Geely",
              "Embraer / Eve": "Eve", "Beta Technologies": "Beta", "Vertical Aerospace": "Vertical",
              "Wollant Aviation": "Wollant", "Archer Aviation": "Archer", "Joby Aviation": "Joby",
              "AutoFlight": "AutoFlight"}


def panel_ari_funding(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """The index firms with a disclosed funding amount: funding against (i) unique aircraft in the
    corpus, (ii) the priority year of the first patent, (iii) the years from first patent to
    first flight (flights up to the release year). Spearman rho, p and n on each panel (D4, D6,
    D26)."""
    fr = tables["la_ari_funding"].copy()
    for c in ("funding $M", "unique aircraft", "first patent", "years first patent to first flight"):
        fr[c] = _num(fr, c)
    tests = tables["la_ari_funding_tests"].copy()
    d = fr[fr["funding $M"].notna()]
    fig, axes = plt.subplots(1, 3, figsize=(W, 2.7), gridspec_kw={"wspace": 0.42})
    spec = [("unique aircraft", "unique aircraft in the corpus", "(i) Aircraft filed"),
            ("first patent", "priority year of the first patent", "(ii) First patent"),
            ("years first patent to first flight", "years, first patent → first flight",
             "(iii) Patent-to-flight lead")]
    for ax, (col, ylab, title) in zip(axes, spec):
        s = d[["company", "funding $M", col]].dropna()
        ax.scatter(s["funding $M"], s[col], s=22, color=CAT[0], edgecolor="white", lw=0.6, zorder=4)
        for _, r in s.iterrows():
            ax.annotate(_ARI_SHORT.get(r["company"], r["company"]), (r["funding $M"], r[col]),
                        xytext=(3, 2), textcoords="offset points", fontsize=5.8, color=INK2)
        ax.set_xscale("log")
        ax.set_xlim(35, 12000)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x_, _p: f"{x_:,.0f}"))
        ax.set_xlabel("disclosed funding, $M (log)", fontsize=7)
        ax.set_ylabel(ylab, fontsize=7)
        ax.tick_params(labelsize=6.5)
        if col == "years first patent to first flight":
            ax.axhline(0, color=MUTED, lw=0.8, ls="--")
        tr = tests[tests["column"].eq(col)]
        if len(tr):
            rho = float(_num(tr, "rho").iloc[0]); p = float(_num(tr, "p").iloc[0])
            n = int(_num(tr, "firms").iloc[0])
            ax.set_title(f"{title}\nρ {rho:+.2f} · p {p:.3f} · n {n}", fontsize=8)
        _hgrid(ax, "both")
        _ch4_note(ax, "Sources: AAM Reality Index\n(May 2026) · PatSeer ·\nhuman labelling · unit: firm")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 2026-09-27 — chapter 5 (sm_text_ch5, comments E1-E17)
# --------------------------------------------------------------------------
_CH5_SRC = "Sources: PatSeer (applicant country, priority date) · human labelling"
_CH5_ABBR = {"North America": "NA", "Europe": "EU", "Asia-Pacific": "AP"}
#: a region-window cell under this many aircraft is left blank, as in the full document's grid
CH5_THIN = 10


def _ch5_p(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p {p:.3f}" if p < 0.05 else f"p {p:.2f}"


def panel_region_design(tables: Dict[str, pd.DataFrame], path: Path, ds) -> Optional[Path]:
    """What each region designs and how its mix moves (E4): per region (column) and priority
    window, (i) the class, (ii) the propulsive-unit band, (iii) whether any propulsor tilts —
    each bar 100 % of the region-window's aircraft — and beside each panel the answers whose
    share trends over 2012-2023 (Spearman on each aircraft's priority year; bold = detected),
    with the shares of the three windows from 2012 (author's ruling, 2026-09-27). Replaces ``atlas_region`` and ``region_grid`` in the brief."""
    if ds is None:
        return None
    from .atlas import ARCH_COLOR, OTHER, REGION_COLOR
    from . import sm_open as _so
    v = _lt.base(ds)
    w = _so._ch5_frame(ds, v)
    mc = tables["la_region_mix_change"].copy()
    for c in ["rho", "p"] + [f"share {w_}" for w_ in _so.CH5_WINS] + [f"base {w_}" for w_ in _so.CH5_WINS]:
        mc[c] = _num(mc, c)
    regions = _lt.REGIONS
    wins = list(WINDOW_NAMES)
    unit_cols = dict(zip(_so.CH5_VARS["propulsive units"][1],
                         [BLUE(t) for t in np.linspace(0.22, 0.95, 5)]))
    specs = [
        ("class", "(i) Architecture class",
         {c: ARCH_COLOR.get(c, OTHER) for c in _so.CH5_VARS["class"][1]},
         lambda c: _so.CH5_CLASS_WORD[c]),
        ("propulsive units", "(ii) Propulsive units", unit_cols, lambda c: f"{c} units"),
        ("tilting unit", "(iii) Any propulsor that tilts",
         {True: CAT[7], False: CONTEXT}, lambda c: "tilts" if c is True else "none tilts"),
    ]
    fig = plt.figure(figsize=(W, 5.3))
    gs = fig.add_gridspec(3, 6, width_ratios=[1.55, 1.0] * 3, hspace=1.25, wspace=0.12,
                          left=0.03, right=0.995, top=0.84, bottom=0.08)
    x = np.arange(len(wins))
    for i, (var, title, pal, word) in enumerate(specs):
        col = _so._ch5_col(var)
        cats = _so.CH5_VARS[var][1]
        for j, reg in enumerate(regions):
            ax = fig.add_subplot(gs[i, 2 * j])
            tx = fig.add_subplot(gs[i, 2 * j + 1])
            tx.axis("off")
            tx.set_zorder(5)
            s = w[w["region3"].eq(reg) & w[col].notna()]
            bottom = np.zeros(len(wins))
            ns = np.array([int(s["window"].eq(wn).sum()) for wn in wins])
            for c in cats:
                vals = np.array([float(s.loc[s["window"].eq(wn), col].eq(c).mean())
                                 if ns[k] >= CH5_THIN else 0.0 for k, wn in enumerate(wins)])
                bars = ax.bar(x, vals, bottom=bottom, width=0.76, color=pal[c], edgecolor=SURFACE,
                              lw=0.7, label=word(c), zorder=3)
                for k, b in enumerate(bars):
                    if str(wins[k]).startswith("2024") or wins[k] == "<= 2011":
                        b.set_alpha(0.4)
                    if vals[k] >= 0.2 and wins[k] != "<= 2011":
                        ax.text(k, bottom[k] + vals[k] / 2, f"{vals[k]:.0%}", ha="center",
                                va="center", fontsize=6.2, color=INK, zorder=5,
                                bbox=dict(fc="white", ec="none", pad=0.12, alpha=0.8))
                bottom += vals
            for k in range(len(wins)):
                if ns[k] < CH5_THIN:
                    ax.text(k, 0.5, f"n {ns[k]}", ha="center", va="center", fontsize=6.2,
                            color=INK2, rotation=90)
            ax.axvline(0.5, color=INK2, lw=0.6, ls=":", zorder=4)
            ax.set_ylim(0, 1)
            ax.set_xlim(-0.6, len(wins) - 0.4)
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_xticks(x, [f"{_lf.WIN_SHORT[wn].replace('≤2011', '≤11')}\n{ns[k]}"
                              for k, wn in enumerate(wins)], fontsize=5.6)
            ax.tick_params(length=0, pad=1.5)
            from matplotlib.transforms import offset_copy
            if i == 0:
                ax.annotate(reg, xy=(0, 1), xycoords="axes fraction", xytext=(0, 17),
                            textcoords="offset points", fontsize=9.5, ha="left", va="bottom",
                            color=REGION_COLOR.get(reg, INK), fontweight="bold")
            if j == 0:
                ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(-2, 4),
                            textcoords="offset points", ha="left", va="bottom", fontsize=8.4,
                            fontweight="bold", color=INK)
            # the trend column: the two answers with the smallest trend p over 2012-2023 (Spearman,
            # each aircraft at its own priority year); "other classes" is not a class, not listed
            sub = mc[mc["region"].eq(reg) & mc["variable"].eq(var) & mc["answer"].ne("other")].copy()
            if var == "tilting unit":
                sub = sub[sub["answer"].eq("True")]
            sub = sub.dropna(subset=["p"]).sort_values("p").head(2)

            def put(dy, txt, **kw):
                tx.annotate(txt, xy=(0, 1), xycoords="axes fraction", xytext=(0, dy),
                            textcoords="offset points", ha="left", va="top", **kw)
            put(0, "12–15→16–19→20–23", fontsize=6.0, color=INK2, style="italic")
            dy = -11
            for _, r in sub.iterrows():
                up = r["rho"] > 0
                sig = r["p"] < 0.05
                lab = r["label"] if var != "tilting unit" else "tilts"
                lab = lab if var != "propulsive units" else f"{lab} units"
                put(dy, f"{'▲' if up else '▼'} {lab}", fontsize=6.4, color=INK if sig else INK2,
                    fontweight="bold" if sig else None)
                sh = ["–" if (not np.isfinite(r[f"share {w_}"]) or r[f"base {w_}"] < CH5_THIN)
                      else f"{r[f'share {w_}'] * 100:.0f}" for w_ in _so.CH5_WINS]
                put(dy - 8, "→".join(sh) + " %", fontsize=6.2, color=INK if sig else INK2)
                put(dy - 16, f"ρ {r['rho']:+.2f} · {_ch5_p(float(r['p']))}", fontsize=6.0,
                    color=INK2)
                dy -= 27
            if j == 1:
                leg = ax.legend(fontsize=6.6, loc="upper center", bbox_to_anchor=(0.8, 0.0),
                                bbox_transform=offset_copy(ax.transAxes, fig=fig, y=-19, units="points"),
                                ncol=len(cats), handlelength=1.1, columnspacing=0.8, frameon=False)
                for h_ in leg.legend_handles:
                    h_.set_alpha(1)
            if j == 0:
                base = (f"unit: unique aircraft ({len(v)}), each in the window of its priority year "
                        "and the region of its applicant;\nbar = 100 % of the region-window's "
                        f"aircraft whose answer is recorded; n under each bar; cells under "
                        f"{CH5_THIN} left blank; * partial window")
                note = _CH5_SRC + " · " + base if i == 0 else _CH5_SRC + " · unit: unique aircraft"
                ax.annotate(note, xy=(0, 0), xycoords="axes fraction", xytext=(0, -33),
                            textcoords="offset points", ha="left", va="top", fontsize=6.0,
                            color=INK2)
    fig.text(0.03, 0.995, "Beside each panel: share in 2012-15 → 2016-19 → 2020-23 (– = under "
             f"{CH5_THIN} aircraft); trend 2012-2023: Spearman ρ of the answer against\neach "
             "aircraft's priority year; the two answers with the smallest p; bold = trend detected "
             "(p < 0.05)\n≤2011 drawn faded, left of the dotted line: few aircraft", ha="left",
             va="top", fontsize=6.4, color=INK2)
    return _save(fig, path)


_CH5_EVENTS = [(2016.8, "Uber Elevate paper"), (2019.5, "EASA SC-VTOL"),
               (2021.6, "Joby, Archer listed"), (2023.8, "EHang type cert.")]


def panel_region_timing(tables: Dict[str, pd.DataFrame], path: Path, ds=None) -> Path:
    """When each region files (E4d, E6-E9, E13): (i) the unique aircraft per priority year and
    region, with North America's share of the year printed on its segment, the years the snapshot
    has not fully seen shaded, the dated sector events and each region's median year; (ii) how
    many years after North America Europe and Asia-Pacific file each class (difference of median
    priority years, 95 % bootstrap interval). Replaces ``la_class_region_timing`` and
    ``la_lag_constancy`` in the brief."""
    from .atlas import REGION_COLOR
    yr = tables["la_region_years"].copy()
    for c in ("priority year", "aircraft", "share of the year", "share corrected for publication lag",
              "visible at the snapshot"):
        yr[c] = _num(yr, c)
    off = tables["la_lag_offsets"].copy()
    for c in ("median priority year", "offset vs North America (years)", "95 % low", "95 % high",
              "aircraft"):
        off[c] = _num(off, c)
    ll = tables.get("la_lead_lag_region")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.25),
                                 gridspec_kw={"width_ratios": [1.55, 1], "wspace": 0.34})
    years = sorted(yr["priority year"].dropna().astype(int).unique())
    bottom = np.zeros(len(years))
    for reg in _lt.REGIONS:
        s = yr[yr["region"].eq(reg)].set_index("priority year").reindex(years)
        vals = s["aircraft"].fillna(0).to_numpy()
        bars = a1.bar(years, vals, bottom=bottom, width=0.78, color=REGION_COLOR[reg],
                      edgecolor=SURFACE, lw=0.6, label=reg, zorder=3)
        for k, b in enumerate(bars):
            if years[k] > _lt.LAST_COMPLETE:
                b.set_alpha(0.45)
            if reg == "North America" and years[k] >= 2016 and vals[k] >= 8:
                sh = s["share of the year"].iloc[k]
                a1.text(years[k], bottom[k] + vals[k] / 2, f"{sh:.0%}", ha="center", va="center",
                        fontsize=5.8, color=INK, rotation=90, zorder=5,
                        bbox=dict(fc="white", ec="none", pad=0.1, alpha=0.85))
        bottom += vals
    top = float(bottom.max())
    a1.axvspan(_lt.LAST_COMPLETE + 0.5, years[-1] + 0.6, color="#ecebe6", zorder=0)
    a1.text(_lt.LAST_COMPLETE + 0.6, top * 1.02, "not yet\nall\npublished", ha="left",
            va="bottom", fontsize=5.8, color=INK2)
    for xe, lab in _CH5_EVENTS:
        a1.axvline(xe, color=MUTED, lw=0.7, ls=":", zorder=1)
        a1.text(xe - 0.12, top * 1.62, lab, rotation=90, ha="right", va="top", fontsize=5.8,
                color=INK2)
    if ll is not None:
        meds = []
        for _, r in ll.iterrows():
            if r.get("region3") in REGION_COLOR:
                meds.append(f"{_CH5_ABBR[r['region3']]} {int(float(r['50 %']))}")
        med_txt = " · ".join(meds)
    else:
        med_txt = ""
    a1.set_ylim(0, top * 1.64)
    a1.set_xlim(years[0] - 0.6, years[-1] + 0.6)
    a1.set_xticks(years, [str(y_)[2:] if y_ % 2 == 0 else "" for y_ in years], fontsize=6.6)
    a1.set_ylabel("unique aircraft", fontsize=7.5)
    a1.set_xlabel(f"priority year (20‥) · median year to {_lt.LAST_COMPLETE}: {med_txt}\n"
                  "on the North America segment: its share of the year", fontsize=6.6)
    _hgrid(a1, "y")
    a1.set_title("(i) Aircraft per priority year and applicant region", fontsize=8.6)
    a1.legend(fontsize=6.4, loc="upper left", bbox_to_anchor=(0.0, 0.8), frameon=False,
              handlelength=1.1)
    _lf._panel_note(a1, a1, _CH5_SRC + "\nunit: unique aircraft · dotted: dated sector events "
                    "(company and\nregulator notices) · shaded: years the snapshot of June 2026 "
                    "has not\nfully seen", fontsize=6.0)

    # (ii) years after North America
    order = ["Lift + Cruise", "Tilt Rotor", "Combined vectored thrust", "Tilt Wing", "Multirotor"]
    na = off[off["region"].eq("North America")].set_index("class")
    ypos = np.arange(len(order))
    for dy, reg in ((-0.14, "Europe"), (0.14, "Asia-Pacific")):
        s = off[off["region"].eq(reg)].set_index("class").reindex(order)
        o = s["offset vs North America (years)"].to_numpy()
        lo, hi = s["95 % low"].to_numpy(), s["95 % high"].to_numpy()
        a2.hlines(ypos + dy, lo, hi, color=REGION_COLOR[reg], lw=1.4, zorder=3)
        a2.plot(o, ypos + dy, ls="", marker="o", ms=5, color=REGION_COLOR[reg], zorder=4,
                label=f"{reg}")
        for yy, oo in zip(ypos + dy, o):
            above = reg == "Europe"
            a2.text(oo, yy + (-0.12 if above else 0.12), f"{oo:+.1f}".replace("+0.0", "0"),
                    ha="center", va="bottom" if above else "top", fontsize=5.8, color=INK)
    a2.axvline(0, color=REGION_COLOR["North America"], lw=1.2)
    lab = [f"{c.replace('Combined vectored thrust', 'CVT')}\nNA median "
           f"{int(na.loc[c, 'median priority year']) if c in na.index else '–'}" for c in order]
    a2.set_yticks(ypos, lab, fontsize=6.6)
    a2.invert_yaxis()
    a2.set_xlim(-5, 9)
    a2.set_xlabel("years after North America (difference of median priority years)",
                  fontsize=6.6)
    _hgrid(a2, "x")
    a2.set_title("(ii) Years after North America,\nper class", fontsize=8.6)
    a2.legend(fontsize=6.4, loc="center right", frameon=False, handlelength=1.0)
    _lf._panel_note(a2, a2, "Sources: PatSeer (applicant country,\npriority date) · human labelling\nunit: unique aircraft, priority years to "
                    f"{_lt.LAST_COMPLETE}\nbar: 95 % bootstrap interval", fontsize=6.0)
    return _save(fig, path)


def panel_region_converge(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
    """Do the regions converge, and is North America's lean one firm's (E4e, E14, E16, E17):
    (i) each region's share of family-F aircraft (chapter 3's dominant design) in each window from 2012 to
    2020-23, with the chi-square p of the regional difference in each period; (ii) the share with a
    tilting propulsor and the Tilt Rotor share per region, North America also without its largest
    filer; (iii) firm-to-firm proximity of class profiles, within and across regions."""
    from .atlas import REGION_COLOR
    ln = tables["la_region_lean"].copy()
    ts = tables["la_region_tests"].copy()
    ts["p"] = _num(ts, "p (chi-square, region)")
    pr = tables["la_proximity_region"].copy()
    pt = tables["la_region_proximity_test"].copy()
    for c in ln.columns[1:]:
        if c != "largest filer":
            ln[c] = _num(ln, c)

    def tp(measure, period, filers="all filers"):
        r = ts[ts["measure"].eq(measure) & ts["period"].eq(period) & ts["filers"].eq(filers)]
        return float(r["p"].iloc[0]) if len(r) else np.nan

    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(W, 3.0),
                                     gridspec_kw={"width_ratios": [1, 1.2, 1.1], "wspace": 0.62})
    # (i) family F per window from 2012, one line per region; a window under CH5_THIN aircraft
    # of the region is drawn hollow and not joined
    from . import sm_open as _so
    wins = _so.CH5_WINS
    xw = np.arange(len(wins))
    for _, r in ln.iterrows():
        reg = r["region"]
        ys = np.array([float(r[f"F share {w_}"]) for w_ in wins])
        ns = np.array([float(r[f"F base {w_}"]) for w_ in wins])
        ok = ns >= CH5_THIN
        a1.plot(xw[ok], ys[ok], color=REGION_COLOR[reg], lw=1.4, marker="o", ms=4.5, zorder=3,
                label=_CH5_ABBR[reg])
        a1.text(xw[-1] + 0.1, ys[-1], f"{ys[-1]:.0%}", ha="left", va="center", fontsize=6.0,
                color=INK)
    a1.set_xticks(xw, [_lf.WIN_SHORT[w_] for w_ in wins], fontsize=6.6)
    a1.set_xlim(-0.3, len(wins) - 0.4)
    _pct_axis(a1, 0.8)
    a1.set_title("(i) Share of the family F", fontsize=8.0)
    a1.legend(fontsize=6.0, loc="lower right", frameon=False, handlelength=1.2, ncol=3,
              columnspacing=0.6)
    a1.text(0.02, 0.98, "regions differ?\n" + "\n".join(
        f"{_lf.WIN_SHORT[w_]}: {_ch5_p(tp('family F', w_))}" for w_ in wins),
        transform=a1.transAxes, ha="left", va="top", fontsize=6.0, color=INK)
    _lf._panel_note(a1, a1, "Sources: PatSeer (applicant\ncountry, priority date) ·\nhuman "
                    "labelling · unit:\nunique aircraft · F: Lift +\nCruise + the CVT tilting a\n"
                    "rotor set on a fixed wing\nwindows under 10 aircraft\nnot drawn", fontsize=6.0)

    # (ii) tilting and Tilt Rotor, North America with and without its largest filer
    na = ln[ln["region"].eq("North America")].iloc[0]
    big = str(na["largest filer"])
    groups = [("a propulsor\ntilts", "tilting share", "tilting share without it", "any tilting unit"),
              ("Tilt Rotor", "Tilt Rotor share", "Tilt Rotor share without it", "Tilt Rotor")]
    bars = [("NA", lambda r, c, c2: r[c], "North America", None),
            (f"NA w/o {big.split(' /')[0]}", lambda r, c, c2: r[c2], "North America", "////"),
            ("EU", lambda r, c, c2: r[c], "Europe", None),
            ("AP", lambda r, c, c2: r[c], "Asia-Pacific", None)]
    wbar = 0.2
    for g, (gname, c, c2, meas) in enumerate(groups):
        for b, (blab, fn, reg, hatch) in enumerate(bars):
            r = ln[ln["region"].eq(reg)].iloc[0]
            val = float(fn(r, c, c2))
            xx = g + (b - 1.5) * wbar
            bb = a2.bar(xx, val, width=wbar * 0.92, color=REGION_COLOR[reg] if not hatch else "white",
                        edgecolor=REGION_COLOR[reg], lw=1.0, zorder=3,
                        label=blab if g == 0 else None)
            if hatch:
                bb[0].set_hatch(hatch)
            a2.text(xx, val + 0.012, f"{val:.0%}", ha="center", va="bottom", fontsize=5.8,
                    color=INK, rotation=90)
        a2.text(g, 0.97 if g == 0 else 0.55, f"regions: {_ch5_p(tp(meas, 'all years'))}\nw/o {big.split(' /')[0]}: "
                f"{_ch5_p(tp(meas, 'all years', f'without {big}'))}", ha="center", va="top",
                fontsize=6.0, color=INK)
    a2.set_xticks(range(len(groups)), [g_[0] for g_ in groups], fontsize=7)
    _pct_axis(a2, 1.0)
    a2.set_title(f"(ii) Tilting: North America\nwith and without {big.split(' /')[0]}", fontsize=8.0)
    a2.legend(fontsize=6.0, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
              handlelength=1.0, columnspacing=0.6, frameon=False)
    a2.annotate("Sources: PatSeer (applicant country,\npriority date) · human labelling\nunit: "
                "unique aircraft, all years\np: chi-square, region × measure", xy=(0, 0),
                xycoords="axes fraction", xytext=(0, -52), textcoords="offset points", ha="left",
                va="top", fontsize=6.0, color=INK2)

    # (iii) proximity of the firms' class profiles, within and across regions
    for c in ("mean", "lowest", "highest", "pairs"):
        pr[c] = _num(pr, c)
    ab = lambda s: " / ".join(_CH5_ABBR.get(t.strip(), t.strip()) for t in str(s).split("/"))
    pr = pr.assign(_w=pr["within a region?"].eq("within")).sort_values(["_w", "mean"],
                                                                      ascending=[False, False])
    yy = np.arange(len(pr))
    for k, (_, r) in enumerate(pr.iterrows()):
        colr = INK if r["_w"] else INK2
        a3.hlines(k, r["lowest"], r["highest"], color=GRID, lw=2.2, zorder=2)
        a3.plot([r["mean"]], [k], marker="D" if r["_w"] else "o", ms=5, color=colr, zorder=3)
        a3.text(r["mean"], k - 0.3, f"{r['mean']:.2f}", ha="center", va="bottom", fontsize=5.8,
                color=colr)
    a3.set_yticks(yy, [f"{ab(p_)}\n{int(n_)} pairs" for p_, n_ in zip(pr["region pair"], pr["pairs"])],
                  fontsize=6.3)
    a3.invert_yaxis()
    a3.set_xlim(0, 1)
    _hgrid(a3, "x")
    p0 = pt.iloc[0]
    a3.set_title("(iii) Are firms of one\nregion alike?", fontsize=8.0)
    a3.set_xlabel("proximity (1 = same class mix)", fontsize=6.4)
    _lf._panel_note(a3, a3, f"mean, same region {float(p0['same-region mean']):.2f} · "
                    f"different\n{float(p0['different-region mean']):.2f} · "
                    f"{_ch5_p(float(p0['p (permutation)']))} (permutation)\n"
                    "Sources: PatSeer (assignee) ·\nhuman labelling · unit: firm "
                    f"pair,\nthe {int(p0['firms'])} firms with {int(p0['minimum aircraft per firm'])}+ "
                    "aircraft\n◆ within a region · bar: lowest\nto highest pair", fontsize=6.0)
    return _save(fig, path)


def render(out_dir: Path, tables: Dict[str, pd.DataFrame], ds=None) -> Dict[str, Path]:
    """Draw every panel into ``out_dir/figures``; returns ``{name: path}``.

    A panel whose table is missing is skipped rather than fatal — ``render_summary`` then fails
    on it in its own selection guard, which names the item and the section, instead of a
    traceback out of a drawing routine.
    """
    out = Path(out_dir) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    frame = None
    jobs = {
        "sm_duct_bands": (["la_duct_units"], lambda p: panel_duct(tables, p)),
        "sm_weighting": (["la_dd_q"], lambda p: panel_weighting(tables, p)),
        "sm_archetype_filers": (["la_zones"], lambda p: panel_archetype_filers(tables, p, ds)),
        # 2026-09-26, chapter 2 review: ducting merged (C76/C78), propulsion compacted (C75)
        "sm_duct_merged": (["la_duct_count", "la_duct_conditional"], lambda p: panel_duct_merged(tables, p)),
        "sm_propulsion_compact": (["la_duct_count", "la_duct_conditional"],
                                  lambda p: panel_propulsion_compact(tables, p, ds)),
        "sm_tw_entry": (["la_class_cycles", "la_cohorts", "la_cohort_mix"],
                        lambda p: panel_tw_entry(tables, p)),
        "sm_trl_tracked": (["a2_d15_trl_status"], lambda p: panel_trl_tracked(tables, p)),
        "sm_cite_rank": (["la_ari_gap"], lambda p: panel_cite_rank(tables, p, ds, frame)),
        # 2026-09-24, the brief's review
        "sm_duct_count": (["la_duct_count"], lambda p: panel_duct_count(tables, p)),
        "sm_entry_all": (["la_cohort_mix"], lambda p: panel_entry_all(tables, p)),
        # 2026-09-26 (3.3, sm_text_ch3b): redrawn on the proposed rules (C63-C66); the
        # earlier drawing, panel_class_configs, stays for the full document's table
        "sm_class_configs": (["la_class_configs_brief", "la_class_config_mix"],
                             lambda p: panel_class_configs_b(tables, p)),
        # 2026-09-25, the review of the brief
        "sm_joints_per_unit": (["la_joints_per_unit"], lambda p: panel_joints_per_unit(tables, p)),
        "sm_duct_conditional": (["la_duct_conditional"], lambda p: panel_duct_conditional(tables, p)),
        # 2026-09-26, chapter-3 review (C53, C54, C57): condition 1 per priority year on the family
        # F replaces the per-window sm_family; conditions 2 and 3 at the four levels, met in red
        "sm_family_yearly": (["la_family_yearly"], lambda p: panel_family_yearly(tables, p)),
        "sm_dd_conditions": (["la_dd_balance", "la_dd_form"], lambda p: panel_dd_conditions(tables, p)),
        # 2026-09-26: aircraft out of force = every linked patent INACTIVE (author's ruling)
        "sm_force_aircraft": (["la_force_aircraft"], lambda p: panel_force_aircraft(tables, p)),
        # 2026-09-26, C44-C46: the class mix per window against the dated evtol.news directory
        "sm_evtolnews_check": (["la_evtolnews_check"], lambda p: panel_evtolnews_check(tables, p)),
        # 2026-09-24, drivers as observations: drawn from the dataset, no table needed
        # 2026-09-26 (3.4, sm_text_ch3b): booms and ducting per class (C82, C93), and the one
        # move as a trajectory with the three links folded in (C88, C91, C92, C95)
        "sm_driver_traces": (["la_driver_windows"], lambda p: panel_driver_traces_b(tables, p)),
        "sm_driver_trajectory": (["la_driver_windows", "la_driver_links", "la_sets_per_unit_brief"],
                                 lambda p: panel_driver_trajectory(tables, p)),
        "sm_driver_corr": ([], lambda p: panel_driver_correlations(ds, p)),
        # 2026-09-26, chapter 4 (sm_text_ch4, D4-D26)
        "sm_who_files": (["la_coverage_segments", "la_filer_mix", "la_filers_by_window"],
                         lambda p: panel_who_files(tables, p, ds)),
        "sm_one_firm": (["la_class_concentration_brief", "la_firm_leverage"],
                        lambda p: panel_one_firm(tables, p)),
        "sm_entry_split": (["la_entry_split", "la_entry_split_test", "la_tw_entry"],
                           lambda p: panel_entry_split(tables, p)),
        "sm_successions": (["la_succession_matrix"], lambda p: panel_successions(tables, p)),
        "sm_ari_funding": (["la_ari_funding", "la_ari_funding_tests"],
                           lambda p: panel_ari_funding(tables, p)),
        # 2026-09-27, chapter 5 (sm_text_ch5, E1-E17)
        "sm_region_design": (["la_region_mix_change"], lambda p: panel_region_design(tables, p, ds)),
        "sm_region_timing": (["la_region_years", "la_lag_offsets"],
                             lambda p: panel_region_timing(tables, p, ds)),
        "sm_region_converge": (["la_region_lean", "la_region_tests", "la_proximity_region",
                                "la_region_proximity_test"],
                               lambda p: panel_region_converge(tables, p)),
    }
    paths: Dict[str, Path] = {}
    with plt.rc_context(PANEL_STYLE):
        for name, (needs, job) in jobs.items():
            if any(n not in tables for n in needs):
                print(f"  ! {name}: missing {[n for n in needs if n not in tables]} — not drawn")
                continue
            got = job(out / f"{name}.png")
            if got is not None:
                paths[name] = Path(got)
    return paths
