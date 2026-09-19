"""The figure atlas of the Preliminary Analysis — the document as pictures only.

User ruling 2026-09-17: "from that document I just want to see the images — not
the text". :func:`render` draws every figure from the live :class:`Dataset`
(no number is typed), saves each one as PNG under ``<out_dir>/atlas/`` and
assembles ``PRELIMINARY_ANALYSIS_FIGURES.pdf`` (one figure per A4-landscape
page, numbered by the chapter it illustrates). The prose document
(``report.write_markdown``) is untouched and still generated beside it.

Colour: one fixed hue per architecture class (the seven largest; the rest fold
into "Other", grey), a single blue ramp for magnitudes, and value labels on
every bar so no reading depends on colour alone.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

from . import a1, a2, metrics
from .loaders import Dataset

# ---------------------------------------------------------------- style ----
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#ffffff"
OTHER = "#b8b7b1"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE = LinearSegmentedColormap.from_list(
    "blue", ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
#: fixed hue per architecture class (largest seven), never re-assigned by rank
ARCH_ORDER = ["SLC", "TR", "CVT", "TW", "MR", "TB", "PTC"]
ARCH_COLOR = dict(zip(ARCH_ORDER, CAT))
ALL_ARCH = ["SLC", "TR", "CVT", "TW", "MR", "TB", "PTC", "HB", "RC", "PFV", "SRW", "DS"]
REGIONS = ["North America", "Europe", "Asia-Pacific"]
REGION_COLOR = dict(zip(REGIONS, CAT[:3]))
PAGE = (11.69, 8.27)
DPI = 200

STYLE = {
    "font.family": "sans-serif", "font.size": 9.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.6,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.major.size": 0, "ytick.major.size": 0,
    "legend.frameon": False, "legend.fontsize": 9, "figure.facecolor": SURFACE,
}


def _arch_name(code) -> str:
    return f"{metrics.ARCH_NAMES.get(code, code)} ({code})" if isinstance(code, str) else "blank"


def _fold(code) -> str:
    return code if code in ARCH_COLOR else "Other"


def _color(code) -> str:
    return ARCH_COLOR.get(code, OTHER)


def _hgrid(ax, axis="x"):
    ax.grid(True, axis=axis)
    ax.set_axisbelow(True)


def _bar_labels(ax, bars, fmt="{:,.0f}", inside=False, color=INK, size=8.5):
    for b in bars:
        w = b.get_width()
        if not w:
            continue
        y = b.get_y() + b.get_height() / 2
        if inside:
            ax.text(b.get_x() + w / 2, y, fmt.format(w), ha="center", va="center", color="white",
                    fontsize=size, fontweight="bold")
        else:
            ax.text(b.get_x() + w, y, " " + fmt.format(w).replace(",", " "), ha="left", va="center",
                    color=color, fontsize=size)


def _stack_h(ax, frame: pd.DataFrame, colors: Dict[str, str], min_label=0.06, pct=True):
    """100 % horizontal stacked bars, rows = bars, columns = segments (shares)."""
    left = np.zeros(len(frame))
    y = np.arange(len(frame))
    for col in frame.columns:
        vals = frame[col].to_numpy(dtype=float)
        ax.barh(y, vals, left=left, color=colors.get(col, OTHER), edgecolor=SURFACE,
                linewidth=1.5, height=0.72, label=str(col))
        for yi, (l, v) in enumerate(zip(left, vals)):
            if v >= min_label:
                ax.text(l + v / 2, yi, f"{v:.0%}" if pct else f"{v:.0f}", ha="center", va="center",
                        fontsize=8, color="white", fontweight="bold")
        left += vals
    ax.set_yticks(y, frame.index)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.spines[["left", "bottom"]].set_visible(False)


def _heat(ax, mat: pd.DataFrame, fmt="{:.0%}", vmax=None, counts: pd.DataFrame = None, cbar=False):
    vmax = vmax if vmax is not None else float(np.nanmax(mat.to_numpy())) or 1
    im = ax.imshow(mat.to_numpy(dtype=float), cmap=BLUE, vmin=0, vmax=vmax, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.iat[i, j]
            if pd.isna(v) or v == 0:
                continue
            txt = fmt.format(v) if counts is None else f"{counts.iat[i, j]:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                    color="white" if v > 0.55 * vmax else INK)
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=35, ha="right")
    ax.set_yticks(range(mat.shape[0]), mat.index)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-.5, mat.shape[1]), minor=True)
    ax.set_yticks(np.arange(-.5, mat.shape[0]), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    if cbar:
        plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02).outline.set_visible(False)
    return im


def _legend_arch(fig, codes: List[str], loc="lower center", ncol=8, y=0.0):
    handles = [matplotlib.patches.Patch(color=_color(c), label=_arch_name(c) if c != "Other" else "Other types")
               for c in codes]
    fig.legend(handles=handles, loc=loc, ncol=ncol, bbox_to_anchor=(0.5, y))


# ------------------------------------------------------------ frames -------
def _variants(ds: Dataset) -> pd.DataFrame:
    v = ds.variants.merge(
        ds.identity[["patent_id", "priority_year", "region", "company_canonical"]],
        on="patent_id", how="left", suffixes=("", "_id"))
    v["year"] = pd.to_numeric(v["priority_year"], errors="coerce")
    v["window"] = pd.cut(v["year"], [0, 2011, 2015, 2019, 2023, 2100],
                         labels=["≤ 2011", "2012–15", "2016–19", "2020–23", "2024–26*"])
    v["atype"] = v["topType"]
    v["region3"] = v["region"].where(v["region"].isin(REGIONS), "Other regions")
    cc = v["company_canonical"]
    v["filer"] = np.select(
        [cc.eq(a2.CATCH_ALL[0]), cc.eq(a2.CATCH_ALL[1]) | cc.isna()],
        ["Individual inventor", "Unattributed / independent"], "Named company")
    units = [c for c in a2.PROPULSOR_UNIT_COLUMNS if c in v.columns]
    v["units"] = v[units].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
    return v


def _ground_truth(ds: Dataset) -> pd.DataFrame:
    p = ds.root / "0_labelling/inputs/text_architecture/architecture_ground_truth.csv"
    gt = pd.read_csv(p, keep_default_na=False, dtype=str)
    # the GT file keeps the pre-2026-09-17 ids (<pid> / <pid>_archN); the aircraft table uses _uaN
    gt["variant"] = gt["aircraft_id"].str.extract(r"_arch(\d+)$")[0].fillna("1").astype(int)
    keys = ds.variants[["patent_id", "variant"]].assign(variant=lambda d: d["variant"].astype(int))
    return gt.merge(keys, on=["patent_id", "variant"], how="inner")


# ================================================================ figures ===
# Chapter 2 — the three refinements
def fig_funnel(ds, v, n):
    fig, axes = plt.subplots(1, 3, figsize=PAGE, gridspec_kw={"wspace": 0.95})
    stages = [
        ("Patents", [("acquired", n["acquired"]), ("approved at labelling", n["wizard_approved"]),
                     ("representative\n(domain gate)", n["representative"]),
                     ("carrying a unique aircraft", n["primary"])]),
        ("Aircraft", [("observations", n["observations"]), ("unique aircraft", n["unique"])]),
        ("Figures", [("on file (representative patents)", n["figures_total"]),
                     ("approved", n["figures_approved_all"]),
                     ("whole-aircraft (analysed)", n["figures_approved"])]),
    ]
    for ax, (title, rows) in zip(axes, stages):
        labels, vals = zip(*rows)
        cols = [BLUE(0.35 + 0.6 * i / max(len(vals) - 1, 1)) for i in range(len(vals))]
        bars = ax.barh(range(len(vals)), vals, color=cols, height=0.62)
        _bar_labels(ax, bars)
        ax.set_yticks(range(len(vals)), labels)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.set_xlim(0, max(vals) * 1.25)
        ax.spines[["left"]].set_visible(False)
        _hgrid(ax)
    return fig, "2.0", "From 1 639 patents to the analysed aircraft and figures"


def fig_removal(ds, v, n):
    r = a2.d1_rejection_reasons(ds).sort_values("patents")
    gate = r["reason"].str.startswith("Similar")
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.6})
    bars = ax.barh(r["reason"], r["patents"], color=np.where(gate, CAT[1], CAT[0]), height=0.62)
    _bar_labels(ax, bars)
    ax.set_title("Why patents left the analysis (patents)")
    ax.legend(handles=[matplotlib.patches.Patch(color=CAT[0], label="rejected at labelling"),
                       matplotlib.patches.Patch(color=CAT[1], label="domain gate (Similar tag)")],
              loc="lower right")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    # gated aircraft by the architecture they were labelled with
    g = ds.gated_out[ds.gated_out["is_primary"].fillna(False).astype(bool)]
    tab = pd.crosstab(g["topType"].map(_fold), g["similar_tag"]).reindex(ARCH_ORDER + ["Other"]).fillna(0)
    tab = tab.loc[tab.sum(axis=1) > 0]
    left = np.zeros(len(tab))
    tagc = {"UAVSimilar": CAT[1], "ElectricSimilar": CAT[6], "STOLSimilar": CAT[3]}
    for col in tab.columns:
        b = ax2.barh(range(len(tab)), tab[col], left=left, color=tagc.get(col, OTHER), height=0.62,
                     edgecolor=SURFACE, linewidth=1.5, label=col.replace("Similar", "-similar"))
        for i, (l, val) in enumerate(zip(left, tab[col])):
            if val >= 3:
                ax2.text(l + val / 2, i, f"{val:.0f}", ha="center", va="center", color="white", fontsize=8,
                         fontweight="bold")
        left += tab[col].to_numpy()
    ax2.set_yticks(range(len(tab)), [_arch_name(c) if c != "Other" else "Other types" for c in tab.index])
    ax2.invert_yaxis()
    ax2.set_title(f"Unique aircraft removed by the gate ({int(tab.values.sum())})")
    ax2.legend(loc="lower right")
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2)
    return fig, "2.1", "Refinement 1 — what was removed, and why"


def fig_duplicates(ds, v, n):
    d = a2.d7_duplicates(ds)
    app = a2.d7_aircraft_per_patent(ds)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"wspace": 0.5})
    lab = ["O1 — same aircraft,\nnew figures", "O2 — same aircraft,\nsame figures", "S3 — similar aircraft\n(new unique)"]
    bars = ax.barh(lab, d["observations"], color=[CAT[0], BLUE(0.45), CAT[2]], height=0.6)
    _bar_labels(ax, bars)
    ax.invert_yaxis()
    ax.set_title("Repeated observations (duplicate patents)")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    x = app.iloc[:, 0].astype(str)
    bars = ax2.bar(x, app["patents"], color=BLUE(0.7), width=0.6)
    for b in bars:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.0f}", ha="center",
                 va="bottom", fontsize=9)
    ax2.set_yscale("log")
    ax2.set_xlabel("aircraft drawn in one patent")
    ax2.set_title("Aircraft per primary patent (log scale)")
    _hgrid(ax2, "y")
    return fig, "2.2", "Refinement 2 — observations to unique aircraft"


def fig_figure_approval(ds, v, n):
    f = ds.figures_rep.copy()
    st = f["status"].astype(str).str.lower()
    f["outcome"] = np.select([st.eq("approved") & f["parts"].astype(str).str.startswith("Whole Vehicle"),
                              st.eq("approved")], ["whole aircraft", "detail (set aside)"], "not approved")
    per = ds.approved_figures.groupby("aircraft_id").size()
    vv = v.set_index("aircraft_id")
    nfig = vv["n_approved_this_variant"].astype(float)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.35})
    cnt = nfig.clip(upper=8).value_counts().sort_index()
    bars = ax.bar(cnt.index.astype(int).astype(str).str.replace("8", "8+"), cnt.values,
                  color=[CAT[1] if i == 1 else BLUE(0.6) for i in cnt.index], width=0.65)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.0f}", ha="center",
                va="bottom", fontsize=9)
    ax.set_xlabel("whole-aircraft figures per unique aircraft")
    ax.set_title(f"Visual evidence per aircraft (median {nfig.median():.0f})")
    _hgrid(ax, "y")
    # single-figure share by architecture
    g = vv.assign(single=nfig.eq(1), a=vv["topType"]).groupby("a").agg(
        n=("single", "size"), single=("single", "mean"), med=("n_approved_this_variant", "median"))
    g = g.reindex([c for c in ALL_ARCH if c in g.index])
    bars = ax2.barh([_arch_name(c) for c in g.index], g["single"], color=[_color(c) for c in g.index], height=0.65)
    for b, (_, r) in zip(bars, g.iterrows()):
        ax2.text(b.get_width(), b.get_y() + b.get_height() / 2,
                 f" {r['single']:.0%}  (n {r['n']:.0f}, median {r['med']:.0f})", va="center", fontsize=8.5)
    ax2.axvline(nfig.eq(1).mean(), color=INK2, lw=1, ls="--")
    ax2.set_xlim(0, 0.9)
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.invert_yaxis()
    ax2.set_title("Aircraft resting on a single figure, by architecture")
    ax2.spines[["left"]].set_visible(False)
    _hgrid(ax2)
    return fig, "2.3", "Refinement 3 — figure approval and the evidence behind each aircraft"


# Chapter 3.1 — provenance
def fig_years(ds, v, n):
    y = v.dropna(subset=["year"]).copy()
    y["year"] = y["year"].astype(int).clip(lower=2005)
    tab = pd.crosstab(y["year"], y["region3"]).reindex(columns=REGIONS + ["Other regions"]).fillna(0)
    tab = tab.reindex(range(tab.index.min(), tab.index.max() + 1), fill_value=0)
    acq = ds.patents.merge(ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left")
    acq_y = pd.to_numeric(acq["priority_year"], errors="coerce").dropna().astype(int).clip(lower=2005)
    acq_y = acq_y.value_counts().reindex(tab.index, fill_value=0)
    fig, ax = plt.subplots(figsize=PAGE)
    bottom = np.zeros(len(tab))
    colors = {**REGION_COLOR, "Other regions": OTHER}
    for col in tab.columns:
        ax.bar(tab.index, tab[col], bottom=bottom, color=colors[col], width=0.8, label=col,
               edgecolor=SURFACE, linewidth=0.8)
        bottom += tab[col].to_numpy()
    ax.plot(acq_y.index, acq_y.values, color=INK, lw=2, marker="o", ms=4, label="patents acquired (all)")
    partial = n["partial_start"]
    ax.axvspan(partial - 0.5, tab.index.max() + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax.text(partial, ax.get_ylim()[1] * 0.97, " partial\n window", va="top", fontsize=9, color=INK2)
    ax.set_xticks(tab.index, [("≤2005" if t == 2005 else str(t)) for t in tab.index], rotation=45)
    ax.set_ylabel("unique aircraft (bars)  ·  patents acquired (line)")
    ax.legend(loc="upper left")
    ax.set_title("Unique aircraft per priority year, by applicant region")
    _hgrid(ax, "y")
    return fig, "3.1.1", "When the aircraft were filed"


def fig_region(ds, v, n):
    prov = a1.provenance_tables(ds, top_offices=12)
    c = prov["assignee_country"].sort_values("patents")
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"wspace": 0.45})
    y = np.arange(len(c))
    ax.barh(y, c["patents"], color=BLUE(0.25), height=0.7, label="acquired")
    b = ax.barh(y, c["representative"], color=BLUE(0.75), height=0.7, label="representative")
    for yi, (_, r) in zip(y, c.iterrows()):
        ax.text(r["patents"], yi, f" {r['representative']:.0f} / {r['patents']:.0f}  ({r['representative share']:.0%})",
                va="center", fontsize=8.5)
    ax.set_yticks(y, c["assignee_country"].fillna("?"))
    ax.set_xlim(0, c["patents"].max() * 1.35)
    ax.legend(loc="lower right")
    ax.set_title("Applicant country — patents kept")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    # architecture mix by region
    tab = pd.crosstab(v["region3"], v["atype"].map(_fold), normalize="index")
    tab = tab.reindex(index=REGIONS + ["Other regions"], columns=ARCH_ORDER + ["Other"]).fillna(0)
    ns = v["region3"].value_counts()
    tab.index = [f"{r}\n(n {ns.get(r, 0)})" for r in tab.index]
    _stack_h(ax2, tab, {**ARCH_COLOR, "Other": OTHER})
    ax2.set_title("Architecture mix by applicant region")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=4, y=-0.02)
    return fig, "3.1.2", "Where the aircraft come from"


def fig_filers(ds, v, n):
    fig = plt.figure(figsize=PAGE)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.1, 1], hspace=0.55, wspace=0.75)
    ax = fig.add_subplot(gs[:, 0])
    named = v[v["filer"].eq("Named company")]
    top = named["company_canonical"].value_counts().head(18)
    mix = pd.crosstab(named["company_canonical"], named["atype"].map(_fold)).reindex(top.index)
    mix = mix.reindex(columns=ARCH_ORDER + ["Other"]).fillna(0)
    left = np.zeros(len(mix))
    for col in mix.columns:
        ax.barh(range(len(mix)), mix[col], left=left, color=_color(col), height=0.7,
                edgecolor=SURFACE, linewidth=1)
        left += mix[col].to_numpy()
    for i, t in enumerate(top.values):
        ax.text(t, i, f" {t}", va="center", fontsize=8.5)
    ax.set_xlim(0, top.max() * 1.12)
    ax.set_yticks(range(len(mix)), mix.index)
    ax.invert_yaxis()
    ax.set_title("Top 18 companies — unique aircraft by architecture")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    # filer type x architecture
    ax2 = fig.add_subplot(gs[0, 1])
    tab = pd.crosstab(v["filer"], v["atype"].map(_fold), normalize="index").reindex(
        columns=ARCH_ORDER + ["Other"]).fillna(0)
    ns = v["filer"].value_counts()
    tab.index = [f"{r} (n {ns[r]})" for r in tab.index]
    _stack_h(ax2, tab, {**ARCH_COLOR, "Other": OTHER}, min_label=0.08)
    ax2.set_title("Architecture mix by filer type")
    # Lorenz
    ax3 = fig.add_subplot(gs[1, 1])
    raw, canonical = a2.d8_filer_counts(ds)
    for s, lab, col in ((raw, "raw assignee string", BLUE(0.45)), (canonical, "canonical company", CAT[1])):
        x = np.sort(s.to_numpy())
        cum = np.concatenate([[0], np.cumsum(x) / x.sum()])
        ax3.plot(np.linspace(0, 1, len(cum)), cum, lw=2, color=col, label=lab)
    ax3.plot([0, 1], [0, 1], color=MUTED, lw=1, ls="--")
    ax3.set_xlabel("share of filers (smallest first)")
    ax3.set_ylabel("share of patents")
    ax3.legend(loc="upper left")
    ax3.set_title("Concentration of filing (Lorenz)")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.02)
    return fig, "3.1.3", "Who files the aircraft"


def fig_status(ds, v, n):
    fs = a2.d1_filing_status(ds).set_index("filing status")
    lag = a2.d9_publication_lag(ds)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.4, 1], "wspace": 0.4})
    share = (fs / fs.sum()).T
    share.index = [f"{i} (n {fs[i].sum():,})".replace(",", " ") for i in share.index]
    _stack_h(ax, share, dict(zip(fs.index, [CAT[2], BLUE(0.45), CAT[3], CAT[7]])))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
    ax.set_title("Legal status at each refinement level")
    lg = lag[lag["patents"] >= 10]
    y = np.arange(len(lg))
    ax2.hlines(y, 0, lg["90th percentile"], color=GRID, lw=6)
    ax2.plot(lg["median lag"], y, "o", ms=10, color=CAT[0], label="median")
    ax2.plot(lg["90th percentile"], y, "|", ms=18, mew=2.5, color=INK2, label="90th percentile")
    ax2.set_yticks(y, [f"{r} (n {p})" for r, p in zip(lg["region"], lg["patents"])])
    ax2.invert_yaxis()
    ax2.set_xlim(0, 4.5)
    ax2.set_xlabel("years from priority to publication")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax2.set_title("Publication lag — why the last window is partial")
    ax2.spines[["left"]].set_visible(False)
    return fig, "3.1.4", "Filing status and publication lag"


# Chapter 3.2 — images
def fig_image_slots(ds, v, n):
    f = ds.approved_figures
    slots = [("per", "Perspective"), ("acSty", "Drawing style"), ("acCol", "Aircraft colour"),
             ("acState", "Flight state drawn")]
    fig, axes = plt.subplots(len(slots), 1, figsize=PAGE, gridspec_kw={"hspace": 1.1})
    for ax, (col, title) in zip(axes, slots):
        s = f[col].replace("", np.nan).dropna().astype(str)
        vc = s.value_counts(normalize=True)
        top = vc.head(6)
        if len(vc) > 6:
            top["other"] = vc.iloc[6:].sum()
        frame = pd.DataFrame([top.to_numpy()], columns=top.index, index=[""])
        _stack_h(ax, frame, dict(zip(top.index, CAT[:len(top) - 1] + [OTHER] if "other" in top.index
                                    else CAT[:len(top)])), min_label=0.04)
        ax.set_title(f"{title}  (n {len(s):,})".replace(",", " "), fontsize=10)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=7, fontsize=8.5)
        ax.set_yticks([])
    return fig, "3.2.1", "What the approved whole-aircraft figures look like"


def fig_state_by_arch(ds, v, n):
    f = ds.approved_figures.merge(v[["aircraft_id", "atype"]], on="aircraft_id", how="inner")
    f = f[f["acState"].astype(str).ne("") & f["acState"].notna()]
    states = f["acState"].value_counts().index.tolist()
    tab = pd.crosstab(f["atype"], f["acState"]).reindex(columns=states).fillna(0)
    tab = tab.reindex([c for c in ALL_ARCH if c in tab.index])
    share = tab.div(tab.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=PAGE)
    share.index = [f"{_arch_name(c)}  n {int(tab.loc[c].sum())}" for c in tab.index]
    _heat(ax, share, vmax=1)
    ax.set_title("Flight state drawn, per architecture (row share of whole-aircraft figures)")
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    return fig, "3.2.2", "Which flight state each architecture is drawn in"


# Chapter 3.3 — design space
def fig_arch_gt(ds, v, n):
    gt = _ground_truth(ds)
    gt = gt[gt["ground_truth"].isin(ALL_ARCH) & gt["figure_label_frozen"].isin(ALL_ARCH)]
    fig = plt.figure(figsize=PAGE)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.15], wspace=0.45)
    ax = fig.add_subplot(gs[0])
    lab = v["atype"].value_counts()
    gtc = v["arch_gt"].value_counts()
    order = [c for c in ALL_ARCH if c in lab.index or c in gtc.index]
    y = np.arange(len(order))
    b1 = ax.barh(y - 0.2, [lab.get(c, 0) for c in order], height=0.38, color=[_color(c) for c in order],
                 label="figure label (wizard)")
    b2 = ax.barh(y + 0.2, [gtc.get(c, 0) for c in order], height=0.38, color="none",
                 edgecolor=[_color(c) if c in ARCH_COLOR else MUTED for c in order], hatch="////", lw=1.2,
                 label="whole-patent ground truth")
    _bar_labels(ax, b1, size=8)
    _bar_labels(ax, b2, size=8, color=INK2)
    ax.set_yticks(y, [_arch_name(c) for c in order])
    ax.invert_yaxis()
    ax.legend(loc="lower right")
    ax.set_title(f"Architecture classes — {len(v)} unique aircraft")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    # confusion: frozen figure label vs ground truth
    ax2 = fig.add_subplot(gs[1])
    cm = pd.crosstab(gt["ground_truth"], gt["figure_label_frozen"])
    keys = [c for c in ALL_ARCH if c in cm.index or c in cm.columns]
    cm = cm.reindex(index=keys, columns=keys).fillna(0)
    share = cm.div(cm.sum(axis=1).replace(0, np.nan), axis=0)
    _heat(ax2, share, vmax=1, counts=cm)
    ax2.set_xticklabels(keys, rotation=0, ha="center")
    ax2.set_yticklabels([f"{k}  ({int(cm.loc[k].sum())})" for k in keys])
    ax2.set_xlabel("label read from the figures alone (frozen)")
    ax2.set_ylabel("ground truth (whole patent)")
    agree = float(np.trace(cm.to_numpy()) / cm.to_numpy().sum())
    kappa = metrics.cohen_kappa(gt["ground_truth"], gt["figure_label_frozen"])
    ax2.set_title(f"Figure label vs ground truth — agreement {agree:.0%}, κ {kappa:.2f}")
    return fig, "3.3.1", "Architecture classes and how far the image alone gets"


def fig_gt_visibility(ds, v, n):
    gt = _ground_truth(ds)
    gt = gt[gt["ground_truth"].isin(ALL_ARCH)]
    g = gt.assign(vis=gt["visible_in_image"].eq("yes"), same=gt["ground_truth"].eq(gt["figure_label_frozen"]))
    t = g.groupby("ground_truth").agg(n=("vis", "size"), vis=("vis", "mean"), same=("same", "mean"))
    t = t.reindex([c for c in ALL_ARCH if c in t.index])
    fig, ax = plt.subplots(figsize=PAGE)
    y = np.arange(len(t))
    ax.hlines(y, t["same"], 1, color=GRID, lw=8)
    ax.plot(t["same"], y, "o", ms=11, color=CAT[1], label="figure label equals ground truth")
    ax.plot(t["vis"], y, "D", ms=8, color=CAT[0], label="type visible in the image")
    for yi, (_, r) in zip(y, t.iterrows()):
        ax.text(1.01, yi, f"n {r['n']:.0f}  ·  {1 - r['vis']:.0%} not visible", va="center", fontsize=8.5)
    ax.set_yticks(y, [_arch_name(c) for c in t.index])
    ax.invert_yaxis()
    ax.set_xlim(0.4, 1.0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.legend(loc="lower left")
    ax.set_title("Per ground-truth class: how often the drawing shows the type")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    return fig, "3.3.2", "Where the drawing is not enough"


def fig_arch_time(ds, v, n):
    w = v.dropna(subset=["window"])
    tab = pd.crosstab(w["window"], w["atype"].map(_fold)).reindex(columns=ARCH_ORDER + ["Other"]).fillna(0)
    share = tab.div(tab.sum(axis=1), axis=0)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.3})
    x = np.arange(len(share))
    bottom = np.zeros(len(share))
    for col in share.columns:
        ax.bar(x, share[col], bottom=bottom, color=_color(col), width=0.72, edgecolor=SURFACE, lw=1.5)
        for xi, (b, val) in enumerate(zip(bottom, share[col])):
            if val >= 0.05:
                ax.text(xi, b + val / 2, f"{val:.0%}", ha="center", va="center", fontsize=8,
                        color="white", fontweight="bold")
        bottom += share[col].to_numpy()
    ax.set_xticks(x, [f"{i}\nn {tab.loc[i].sum():.0f}" for i in share.index])
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(0, 1)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.set_title("Architecture share per priority window  (* partial)")
    ends = []
    for col in ARCH_ORDER[:5]:
        ax2.plot(x, share[col], marker="o", lw=2, ms=6, color=_color(col))
        yv = float(share[col].iloc[-1])
        while any(abs(yv - e) < 0.012 for e in ends):
            yv += 0.012
        ends.append(yv)
        ax2.text(x[-1] + 0.12, yv, col, va="center", fontsize=9, color=INK)
    ax2.set_xticks(x, share.index)
    ax2.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=GRID, alpha=0.6, zorder=0, hatch="//", lw=0)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title("The five largest classes over time")
    _hgrid(ax2, "y")
    _legend_arch(fig, ARCH_ORDER + ["Other"], ncol=8, y=-0.03)
    return fig, "3.3.3", "How the architecture mix moves over time"


def fig_powertrain(ds, v, n):
    order = ["Yes", "Hybrid", "Unknown", "No"]
    colors = {"Yes": CAT[2], "Hybrid": CAT[3], "Unknown": OTHER, "No": CAT[7]}
    tab = pd.crosstab(v["atype"], v["is_electric_final"].fillna("Unknown"), normalize="index")
    tab = tab.reindex(index=[c for c in ALL_ARCH if c in v["atype"].values],
                      columns=[o for o in order if o in v["is_electric_final"].fillna("Unknown").values]).fillna(0)
    ns = v["atype"].value_counts()
    tab.index = [f"{_arch_name(c)}  n {ns[c]}" for c in tab.index]
    w = v.dropna(subset=["window"])
    tw = pd.crosstab(w["window"], w["is_electric_final"].fillna("Unknown"), normalize="index").reindex(
        columns=tab.columns).fillna(0)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.4, 1], "wspace": 0.45})
    _stack_h(ax, tab, colors)
    ax.set_title("Powertrain stated in the patent, by architecture")
    _stack_h(ax2, tw, colors)
    ax2.set_title("… and by priority window")
    ax.legend(["electric", "hybrid", "not stated", "stated non-electric"][:len(tab.columns)],
              loc="upper center", bbox_to_anchor=(0.8, -0.05), ncol=4)
    return fig, "3.3.4", "Powertrain"


def fig_fields(ds, v, n):
    inv = a2.d2_field_inventory(ds)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.3})
    card = inv["card"].fillna("?").astype(str).str[:1]
    cards = sorted(card.unique())
    cc = dict(zip(cards, CAT))
    for c in cards:
        s = inv[card.eq(c)]
        ax.scatter(s["answered"], s["effective_answers"], s=26, color=cc[c], alpha=0.8,
                   edgecolor=SURFACE, lw=0.6, label=f"card {c}")
    ax.axvline(n.get("informative_min_answered", 300), color=MUTED, ls="--", lw=1)
    ax.axhline(1.5, color=MUTED, ls="--", lw=1)
    for _, r in inv[(inv["answered"] >= 300) & (inv["effective_answers"] >= 3)].iterrows():
        ax.annotate(r["field"], (r["answered"], r["effective_answers"]), fontsize=7.5, color=INK2,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("unique aircraft answering the field")
    ax.set_ylabel("effective number of answers")
    ax.text(ax.get_xlim()[1], 1.55, "informative →", ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax.legend(loc="upper left", ncol=2)
    ax.set_title(f"Every answerable field ({len(inv)})")
    _hgrid(ax, "both")
    slots = a2.d2_slots_per_aircraft(ds)
    sv = v.assign(slots=v["aircraft_id"].map(dict(zip(ds.variants["aircraft_id"], slots))))
    order = [c for c in ALL_ARCH if c in sv["atype"].values]
    data = [sv.loc[sv["atype"].eq(c), "slots"].to_numpy() for c in order]
    bp = ax2.boxplot(data, vert=False, patch_artist=True, widths=0.6, medianprops={"color": INK},
                     flierprops={"markersize": 3, "markeredgecolor": MUTED})
    for patch, c in zip(bp["boxes"], order):
        patch.set_facecolor(_color(c))
        patch.set_edgecolor(SURFACE)
    ax2.set_yticks(range(1, len(order) + 1), order)
    ax2.invert_yaxis()
    ax2.set_xlabel("fields answered per aircraft")
    ax2.set_title("Label depth by architecture")
    _hgrid(ax2)
    return fig, "3.3.5", "Which fields carry information, and how deep each aircraft is labelled"


def fig_fill(ds, v, n):
    from .figures import fill_rate_matrix
    mat = fill_rate_matrix(ds)
    fig, ax = plt.subplots(figsize=PAGE)
    _heat(ax, mat, vmax=1, cbar=True)
    ax.set_title("Conditional fill rate — share answered where the parent condition holds")
    return fig, "3.3.6", "Where the labels are complete"


def _profile(v, col, top=8, labels=None):
    s = v[col]
    if s.dropna().isin([True, False]).all():
        s = s.map({True: "yes", False: "no"})
    if s.dtype == bool or str(s.dtype) == "boolean":
        s = s.map({True: "yes", False: "no"})
    s = s.astype("object").where(s.notna(), "blank").astype(str)
    keep = s.value_counts().head(top).index
    if col == "boomBin":
        keep = pd.Index([k for k in ("none", "1-2", "3", "4+") if k in keep])
    s = s.where(s.isin(keep), "other")
    tab = pd.crosstab(v["atype"], s, normalize="index")
    cols = [c for c in keep if c != "blank"] + [c for c in ("other", "blank") if c in tab.columns]
    tab = tab.reindex(index=[c for c in ALL_ARCH if c in tab.index], columns=cols).fillna(0)
    if labels:
        tab.columns = [labels.get(c, c) for c in tab.columns]
    return tab


def fig_design_heatmaps(ds, v, n):
    af = a2.archetype_frame(ds)
    v2 = v.merge(af[["aircraft_id", "boomBin", "anyTilt"]], on="aircraft_id", how="left")
    panels = [("wCount", "Wings", {"0": "none", "1": "1 wing", "2": "2 wings", "3": "3 wings"}),
              ("fusKin", "Fuselage motion", None), ("boomBin", "Booms", None),
              ("anyTilt", "Any propulsor tilts", None), ("empType", "Tail type", None),
              ("gearArch", "Landing gear", None)]
    fig, axes = plt.subplots(2, 3, figsize=PAGE, gridspec_kw={"hspace": 0.6, "wspace": 0.25})
    for k, (ax, (col, title, labels)) in enumerate(zip(axes.flat, panels)):
        tab = _profile(v2, col, top=7, labels=labels)
        _heat(ax, tab, vmax=1)
        ax.set_title(title, fontsize=10)
        if k % 3:
            ax.set_yticklabels([])
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8.5)
    return fig, "3.3.7", "The design space — each architecture's answer profile (row shares)"


def fig_units(ds, v, n):
    order = [c for c in ALL_ARCH if c in v["atype"].values]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=PAGE, gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.35})
    rng = np.random.default_rng(42)
    for i, c in enumerate(order):
        u = v.loc[v["atype"].eq(c), "units"].dropna()
        u = u[u > 0].to_numpy()
        if not len(u):
            ax.text(0.3, i, "no propulsor count recorded", va="center", fontsize=8.5, color=MUTED)
            continue
        ax.scatter(np.clip(u, 0, 30) + rng.uniform(-0.25, 0.25, len(u)), i + rng.uniform(-0.25, 0.25, len(u)),
                   s=9, color=_color(c), alpha=0.55, lw=0)
        if len(u):
            q1, med, q3 = np.percentile(u, [25, 50, 75])
            ax.plot([q1, q3], [i, i], color=INK, lw=2.5)
            ax.plot(med, i, "o", color=SURFACE, mec=INK, ms=7, mew=1.8)
    ax.set_yticks(range(len(order)), [_arch_name(c) for c in order])
    ax.invert_yaxis()
    ax.set_xlabel("propulsor units on the aircraft (capped at 30; aircraft with 0 counted left out)")
    ax.set_title("Propulsor units — dot = aircraft, bar = quartiles, ring = median")
    ax.spines[["left"]].set_visible(False)
    _hgrid(ax)
    kin = a2._group_columns(ds, "_propKin")
    bm = a2._group_columns(ds, "_bmech")
    feat = pd.DataFrame({
        "atype": v["atype"],
        "tilting unit": v[kin].eq("Tilt").any(axis=1),
        "fixed + tilting": v[kin].eq("Tilt").any(axis=1) & v[kin].eq("Fixed").any(axis=1),
        "ducted unit": v[bm].eq("Ducted").any(axis=1),
        "more than 8 units": v["units"] > 8,
    })
    tab = feat.groupby("atype").mean().reindex([c for c in ALL_ARCH if c in feat["atype"].values])
    _heat(ax2, tab, vmax=1)
    ax2.set_title("Share of aircraft with …")
    return fig, "3.3.8", "Propulsion"


def fig_archetypes(ds, v, n):
    card = a2.d5_archetype_cardinality(ds)
    from .figures import archetype_levels
    fig = archetype_levels(card)
    fig.set_size_inches(*PAGE)
    for ax in fig.axes:
        for p in ax.patches:
            p.set_facecolor(BLUE(0.6))
            p.set_hatch("")
        ax.set_title("")
    return fig, "3.3.9", "Archetype levels — how many distinct designs each level of detail finds"


# Chapter 4 — flagship check
def fig_flagship(ds, v, n):
    named = v[v["filer"].eq("Named company")]
    top = named["company_canonical"].value_counts()
    top = top[top >= 5].index
    tab = pd.crosstab(named["company_canonical"], named["atype"]).reindex(index=top)
    tab = tab.reindex(columns=[c for c in ALL_ARCH if c in tab.columns]).fillna(0)
    share = tab.div(tab.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=PAGE)
    share.index = [f"{c}  ({int(tab.loc[c].sum())})" for c in tab.index]
    _heat(ax, share, vmax=1, counts=tab)
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    ax.set_title("Companies with ≥ 5 unique aircraft — aircraft per architecture (colour = row share)", pad=24)
    return fig, "4.1", "Flagship check — do companies stick to one architecture?"


FIGURES: List[Callable] = [
    fig_funnel, fig_removal, fig_duplicates, fig_figure_approval,
    fig_years, fig_region, fig_filers, fig_status,
    fig_image_slots, fig_state_by_arch,
    fig_arch_gt, fig_gt_visibility, fig_arch_time, fig_powertrain,
    fig_fields, fig_fill, fig_design_heatmaps, fig_units, fig_archetypes,
    fig_flagship,
]


def render(ds: Dataset, out_dir: Path, values: Dict, filename: str = "PRELIMINARY_ANALYSIS_FIGURES.pdf"
           ) -> Tuple[Path, List[Path]]:
    """Draw every atlas figure; returns (pdf path, png paths)."""
    out_dir = Path(out_dir)
    png_dir = out_dir / "atlas"
    png_dir.mkdir(parents=True, exist_ok=True)
    v = _variants(ds)
    pdf_path = out_dir / filename
    pngs = []
    with plt.rc_context(STYLE), PdfPages(pdf_path) as pdf:
        for fn in FIGURES:
            fig, number, title = fn(ds, v, values)
            fig.suptitle(f"Figure {number} — {title}", x=0.02, y=0.995, ha="left",
                         fontsize=13, fontweight="bold", color=INK)
            slug = re.sub(r"[^a-z0-9]+", "_", fn.__name__[4:])
            png = png_dir / f"fig_{number.replace('.', '_')}_{slug}.png"
            fig.savefig(png, dpi=DPI, bbox_inches="tight", facecolor=SURFACE)
            fig.savefig(pdf, format="pdf", bbox_inches="tight", facecolor=SURFACE)
            plt.close(fig)
            pngs.append(png)
    return pdf_path, pngs
