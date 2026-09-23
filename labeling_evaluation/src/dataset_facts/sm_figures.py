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
         "sm_tw_entry", "sm_trl_tracked", "sm_cite_rank"]

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


def panel_archetype_filers(tables: Dict[str, pd.DataFrame], path: Path) -> Path:
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
    fig, ax = plt.subplots(figsize=(W, 2.7))
    y = np.arange(len(t))
    bars = ax.barh(y, t["_fpa"], height=0.68, color=colors, zorder=3)
    for b, a in zip(bars, t["archetype"]):
        if a == focus:
            b.set_hatch("////")
        elif a == neighbour:
            b.set_hatch("....")
    for b, (fpa, n_, f_) in zip(bars, zip(t["_fpa"], t["_n"], t["_f"])):
        ax.text(b.get_width() + 0.015, b.get_y() + b.get_height() / 2,
                f"{fpa:.2f}   ({int(f_)} filers / {int(n_)} aircraft)",
                va="center", ha="left", fontsize=7.2, color=INK2)
    ax.set_yticks(y, t["archetype"], fontsize=7.5)
    ax.set_ylim(-0.7, len(t) - 0.3)
    ax.set_xlim(0, float(t["_fpa"].max()) * 1.42)
    ax.set_xlabel("distinct filers per aircraft (1.00 = every aircraft a different filer)",
                  fontsize=8)
    _hgrid(ax, "x")
    ax.set_title(f"How many different filers each archetype of {ZONE_MIN}+ aircraft rests on: "
                 f"{focus} is the lowest in the corpus", fontsize=9)
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
        "sm_archetype_filers": (["la_zones"], lambda p: panel_archetype_filers(tables, p)),
        "sm_tw_entry": (["la_class_cycles", "la_cohorts", "la_cohort_mix"],
                        lambda p: panel_tw_entry(tables, p)),
        "sm_trl_tracked": (["a2_d15_trl_status"], lambda p: panel_trl_tracked(tables, p)),
        "sm_cite_rank": (["la_ari_gap"], lambda p: panel_cite_rank(tables, p, ds, frame)),
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
