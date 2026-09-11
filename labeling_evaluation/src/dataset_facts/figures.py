"""The figures of the Preliminary Analysis, drawn with matplotlib only.

Monochrome and hatch-based, so they print the way the document's stylesheet
prints. Every function returns the :class:`matplotlib.figure.Figure` and, when
``path`` is given, saves a PNG there. :func:`render_all` draws every figure the
index names and returns ``{name: path}``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from . import a1, a2, index
from .loaders import Dataset

GREYS = ["#1a1a1a", "#4d4d4d", "#808080", "#b3b3b3", "#d9d9d9", "#f0f0f0"]
HATCHES = ["", "////", "....", "xxxx", "\\\\\\\\", "++++"]
DPI = 200

matplotlib.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "legend.frameon": False,
    "figure.dpi": 110,
})


def _save(fig: plt.Figure, path: Optional[Path]) -> plt.Figure:
    if path is not None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    return fig


# --------------------------------------------------------------------------
# 1.1 funnel
# --------------------------------------------------------------------------
def funnel(funnel_df: pd.DataFrame, path: Optional[Path] = None) -> plt.Figure:
    """Horizontal bars, widest at the top: acquired -> approved -> ... -> figures."""
    df = funnel_df.copy()
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    y = np.arange(len(df))[::-1]
    widths = df["count"].to_numpy()
    ax.barh(y, widths, color=[GREYS[min(i, 4)] for i in range(len(df))], edgecolor="black",
            linewidth=0.6, height=0.62)
    for yi, w, note in zip(y, widths, df["note"]):
        ax.text(w + max(widths) * 0.012, yi, f"{int(w):,}" + (f"   ({note})" if note else ""),
                va="center", ha="left", fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(df["stage"], fontsize=8.5)
    ax.set_xlim(0, max(widths) * 1.55)
    ax.set_xlabel("count")
    ax.set_title("Acquisition funnel")
    ax.tick_params(axis="x", labelsize=8)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 1.4 conditional fill-rate heatmap
# --------------------------------------------------------------------------
#: child fields (rows) and the conditions they are read under (columns)
HEATMAP_FIELDS = [
    "topType", "fusShape", "fusKin", "gearArch", "latSym", "dinoUnderstanding",
    "wCount", "wingConf", "wing1_posV", "wing1_posL", "wing1_plan", "empType",
    "boomsPresent", "boom1_orient", "boom1_attach", "boom1_count", "boom_count",
]


def fill_rate_matrix(ds: Dataset, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Fill rate of each field on all aircraft, on winged aircraft, on boomed aircraft."""
    v = ds.variants
    winged = pd.to_numeric(v["wCount"], errors="coerce").fillna(0) > 0
    boomed = v["boomsPresent"].fillna(False).astype(bool)
    conditions = {
        f"all aircraft (n={len(v)})": pd.Series(True, index=v.index),
        f"wings present (n={int(winged.sum())})": winged,
        f"booms present (n={int(boomed.sum())})": boomed,
    }
    fields = [f for f in (fields or HEATMAP_FIELDS) if f in v.columns]
    rows = {}
    for f in fields:
        rows[a2.FIELD_NAMES.get(f, f)] = {
            name: float(v.loc[mask, f].notna().mean()) for name, mask in conditions.items()
        }
    return pd.DataFrame(rows).T


def fill_rate_heatmap(ds: Dataset, path: Optional[Path] = None) -> plt.Figure:
    m = fill_rate_matrix(ds)
    fig, ax = plt.subplots(figsize=(6.0, 0.32 * len(m) + 1.2))
    im = ax.imshow(m.to_numpy(), cmap="Greys", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(m.shape[1]))
    ax.set_xticklabels(m.columns, fontsize=8)
    ax.set_yticks(range(m.shape[0]))
    ax.set_yticklabels(m.index, fontsize=8)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            val = m.iat[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7.5,
                    color="white" if val > 0.55 else "black")
    ax.set_title("Fill rate of each field, conditional on the parent part being present")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("share answered", fontsize=8)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 1.6 patents per priority year
# --------------------------------------------------------------------------
def patents_per_year(time_coverage: pd.DataFrame, windows=None, partial_start: int = 2024,
                     path: Optional[Path] = None) -> plt.Figure:
    """Bars per priority year; the candidate windows alternate shaded / unshaded."""
    df = time_coverage
    fig, ax = plt.subplots(figsize=(8.0, 2.9))
    years = df["priority_year"].to_numpy()
    counts = df["patents"].to_numpy()
    partial = years >= partial_start
    ax.bar(years[~partial], counts[~partial], color=GREYS[1], edgecolor="black", linewidth=0.4)
    ax.bar(years[partial], counts[partial], color="white", edgecolor="black", linewidth=0.6,
           hatch="////", label=f"{partial_start}+ (partial: still publishing)")
    top = counts.max() * 1.22
    for k, (name, lo, hi) in enumerate(windows or a2.WINDOWS):
        lo_ = max(lo, years.min())
        hi_ = min(hi, years.max())
        if k % 2 == 1:
            ax.axvspan(lo_ - 0.5, hi_ + 0.5, color=GREYS[5], zorder=0)
        ax.axvline(hi_ + 0.5, color=GREYS[3], linewidth=0.6, zorder=0)
        ax.text((lo_ + hi_) / 2, top * 0.97, name, ha="center", va="top", fontsize=7.5,
                color=GREYS[1])
    ax.set_xlabel("priority year")
    ax.set_ylabel("approved primary patents")
    ax.set_ylim(0, top)
    ax.set_title("Patents per priority year, with the candidate windows")
    ax.legend(loc="center left", fontsize=8)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.1 provenance bars
# --------------------------------------------------------------------------
def provenance_bars(region: pd.DataFrame, office: pd.DataFrame,
                    path: Optional[Path] = None) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.0), gridspec_kw={"width_ratios": [1, 1.4]})
    for ax, df, key, title in ((axes[0], region, "region", "By region"),
                               (axes[1], office, "pub_office", "By publication office")):
        df = df.copy()
        y = np.arange(len(df))[::-1]
        ax.barh(y, df["patents"], color=GREYS[4], edgecolor="black", linewidth=0.5,
                label="acquired")
        ax.barh(y, df["approved"], color=GREYS[1], edgecolor="black", linewidth=0.5,
                label="approved")
        for yi, p, r in zip(y, df["patents"], df["approval_rate"]):
            ax.text(p + df["patents"].max() * 0.02, yi, f"{r:.2f}", va="center", fontsize=7.5)
        ax.set_yticks(y)
        ax.set_yticklabels(df[key], fontsize=8)
        ax.set_xlim(0, df["patents"].max() * 1.18)
        ax.set_title(title)
        ax.tick_params(axis="x", labelsize=8)
    axes[0].legend(loc="lower right", fontsize=8)
    axes[0].set_xlabel("patents (approval rate at the bar end)")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.2 Lorenz curve
# --------------------------------------------------------------------------
def lorenz(raw_counts: pd.Series, canonical_counts: pd.Series,
           path: Optional[Path] = None) -> plt.Figure:
    """Cumulative share of patents against cumulative share of filers, both filer columns."""
    fig, ax = plt.subplots(figsize=(4.2, 4.0))
    for counts, label, style in ((raw_counts, "raw assignee string", "-"),
                                 (canonical_counts, "canonical company (named only)", "--")):
        c = np.sort(counts.to_numpy())[::-1]
        x = np.arange(1, len(c) + 1) / len(c)
        y = np.cumsum(c) / c.sum()
        ax.plot(np.r_[0, x], np.r_[0, y], style, color="black", linewidth=1.2,
                label=f"{label} (n={len(c)})")
    ax.plot([0, 1], [0, 1], ":", color=GREYS[2], linewidth=0.8, label="equal shares")
    ax.set_xlabel("share of filers, largest first")
    ax.set_ylabel("cumulative share of patents")
    ax.set_title("Concentration of filing")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=7.5, loc="lower right")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 4.2 slots answered per aircraft
# --------------------------------------------------------------------------
def slots_histogram(slots: pd.Series, path: Optional[Path] = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    ax.hist(slots, bins=range(int(slots.min()), int(slots.max()) + 3, 2), color=GREYS[3],
            edgecolor="black", linewidth=0.5)
    q1, med, q3 = (slots.quantile(q) for q in (0.25, 0.5, 0.75))
    for val, style in ((q1, ":"), (med, "-"), (q3, ":")):
        ax.axvline(val, color="black", linestyle=style, linewidth=1)
    ax.text(0.98, 0.95,
            f"lower quartile {int(q1)}\nmedian {int(med)}\nupper quartile {int(q3)}\n"
            f"maximum {int(slots.max())}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=GREYS[1],
            linespacing=1.4)
    ax.set_xlabel("answerable slots answered per aircraft")
    ax.set_ylabel("aircraft")
    ax.set_title("Completeness of one label, as a distribution")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 5.4 class balance
# --------------------------------------------------------------------------
def class_balance_bars(balance: pd.DataFrame, path: Optional[Path] = None) -> plt.Figure:
    df = balance
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    y = np.arange(len(df))[::-1]
    ax.barh(y, df["count"], color=GREYS[2], edgecolor="black", linewidth=0.5)
    for yi, c, s in zip(y, df["count"], df["share"]):
        ax.text(c + df["count"].max() * 0.015, yi, f"{int(c)}  ({s:.2f})", va="center",
                fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(df["name"], fontsize=8.5)
    ax.set_xlim(0, df["count"].max() * 1.25)
    ax.set_xlabel("aircraft (share in brackets)")
    ax.set_title("Architecture class balance, primary approved variants")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 5.5 class shares per window
# --------------------------------------------------------------------------
def class_share_stacked_area(windows: pd.DataFrame, partial_label: str = "partial",
                             path: Optional[Path] = None) -> plt.Figure:
    df = windows.copy()
    classes = [c for c in df.columns if c not in ("window", "variants")]
    other = (1 - df[classes].sum(axis=1)).clip(lower=0)
    stack = df[classes].assign(**{"other classes": other})
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    bottom = np.zeros(len(df))
    for i, col in enumerate(stack.columns):
        ax.bar(x, stack[col], bottom=bottom, color=GREYS[min(i, 4)] if col != "other classes"
               else "white", edgecolor="black", linewidth=0.5, hatch=HATCHES[i % len(HATCHES)]
               if col == "other classes" else "", label=col, width=0.72)
        for xi, b, h in zip(x, bottom, stack[col]):
            if h >= 0.08:
                ax.text(xi, b + h / 2, f"{h:.2f}", ha="center", va="center", fontsize=7.5,
                        color="white" if i < 2 and col != "other classes" else "black")
        bottom += stack[col].to_numpy()
    partial = df["window"].astype(str).str.contains(partial_label, case=False)
    for xi in x[partial.to_numpy()]:
        ax.bar(xi, 1, color="none", edgecolor="black", linewidth=1.2, hatch="////",
               width=0.72, alpha=0.35)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{w}\n(n={n})" for w, n in zip(df["window"], df["variants"])],
                       fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of variants")
    ax.set_title("Architecture class shares per window (hatched = partial window)")
    ax.legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    return _save(fig, path)


# --------------------------------------------------------------------------
# block diagrams: section -> gives -> chapter
# --------------------------------------------------------------------------
def block_diagram(section_ids: List[str], title: str, path: Optional[Path] = None,
                  chapters: Optional[List[str]] = None, wrap: int = 46) -> plt.Figure:
    """Boxes on the left (sections, with their short Gives line), chapters on the right.

    Titles are wrapped to the box width; the chapter boxes are spread over the
    whole height so the arrows fan out instead of crossing the text.
    """
    import textwrap

    secs = [index.section(s) for s in section_ids]
    chaps = chapters or [c for c in index.CHAPTERS if any(c in s["feeds"] for s in secs)]
    n_l, n_r = len(secs), len(chaps)

    # each section box holds the wrapped title plus the short Gives line
    title_lines = [textwrap.wrap(f"{s['id']}  {s['title']}", wrap) for s in secs]
    gives_lines = [s["gives_short"].split("\n") for s in secs]
    box_h = [0.30 * len(t) + 0.26 * len(g) + 0.30 for t, g in zip(title_lines, gives_lines)]
    gap = 0.22
    height = sum(box_h) + gap * (n_l - 1) + 1.2
    fig, ax = plt.subplots(figsize=(9.6, 0.56 * height + 0.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, height)
    ax.axis("off")

    left_x, left_w = 0.15, 5.3
    right_x, right_w = 7.6, 2.25
    pos_l, pos_r = {}, {}
    y_top = height - 0.7
    for s, tl, gl, h in zip(secs, title_lines, gives_lines, box_h):
        y0 = y_top - h
        ax.add_patch(FancyBboxPatch((left_x, y0), left_w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="white", edgecolor="black", linewidth=0.9))
        y_text = y_top - 0.2
        for line in tl:
            ax.text(left_x + 0.15, y_text, line, fontsize=8, weight="bold", va="center", ha="left")
            y_text -= 0.30
        for line in gl:
            ax.text(left_x + 0.15, y_text - 0.02, line, fontsize=7.2, va="center", ha="left",
                    color=GREYS[1])
            y_text -= 0.26
        pos_l[s["id"]] = (left_x + left_w, y0 + h / 2)
        y_top = y0 - gap

    # chapters spread evenly over the same vertical extent as the section boxes
    top_y = height - 0.7
    bottom_y = y_top + gap
    for j, c in enumerate(chaps):
        y = top_y - (j + 0.5) * (top_y - bottom_y) / n_r if n_r > 1 else (top_y + bottom_y) / 2
        ax.add_patch(FancyBboxPatch((right_x, y - 0.3), right_w, 0.6,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=GREYS[5], edgecolor="black", linewidth=0.9))
        ax.text(right_x + right_w / 2, y, c, fontsize=8.5, weight="bold", va="center", ha="center")
        pos_r[c] = (right_x, y)
    for s in secs:
        for c in s["feeds"]:
            if c not in pos_r:
                continue
            (x0, y0), (x1, y1) = pos_l[s["id"]], pos_r[c]
            ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9,
                                         linewidth=0.7, color=GREYS[1],
                                         connectionstyle="arc3,rad=0.0"))
    ax.set_title(title, fontsize=10, weight="bold", loc="left")
    return _save(fig, path)


# --------------------------------------------------------------------------
# everything the index names
# --------------------------------------------------------------------------
def render_all(ds: Dataset, out_dir: Path, partial_window_start: int = 2024) -> Dict[str, Path]:
    """Draw every figure of the index into ``out_dir/figs`` and return ``{name: path}``."""
    out_dir = Path(out_dir) / "figs"
    out_dir.mkdir(parents=True, exist_ok=True)
    prov = a1.provenance_tables(ds)
    raw, canonical = a2.d8_filer_counts(ds)

    paths = {}
    jobs = {
        "funnel": lambda p: funnel(a2.d1_funnel(ds), p),
        "fill_rate_heatmap": lambda p: fill_rate_heatmap(ds, p),
        "patents_per_year": lambda p: patents_per_year(
            a1.time_coverage(ds), partial_start=partial_window_start, path=p),
        "provenance_bars": lambda p: provenance_bars(prov["region"], prov["pub_office"], p),
        "lorenz": lambda p: lorenz(raw, canonical, p),
        "slots_histogram": lambda p: slots_histogram(a2.d2_slots_per_aircraft(ds), p),
        "class_balance_bars": lambda p: class_balance_bars(a2.d3_architecture_balance(ds), p),
        "class_share_stacked_area": lambda p: class_share_stacked_area(
            a2.d9_architecture_by_window(ds), path=p),
        "block_diagram_all": lambda p: block_diagram(
            [s["id"] for s in index.SECTIONS], "What each section gives, and which chapter it feeds", p),
        "block_diagram_5": lambda p: block_diagram(
            [s["id"] for s in index.sections_of("5")],
            "Section 5 — purpose of each subsection and the analysis it feeds", p),
    }
    for name, job in jobs.items():
        path = out_dir / f"{name}.png"
        fig = job(path)
        plt.close(fig)
        paths[name] = path
    return paths
