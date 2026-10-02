"""The figures of the Preliminary Analysis: matplotlib charts and three SVG schemes.

Monochrome and hatch-based, so they print the way the document's stylesheet
prints. Every chart function returns the :class:`matplotlib.figure.Figure` and,
when ``path`` is given, saves a PNG there. The three schemes (document pipeline,
refinement funnel, design-space order) are written as SVG with every number a
plain ``<text>`` interpolated from :func:`numbers.live`, so the diagrams can
never disagree with the tables beside them. :func:`render_all` draws everything
into ``<out_dir>/figures`` and returns ``{name: path}``.
"""

from __future__ import annotations

import shutil
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import a1, a2, numbers, register
from .loaders import Dataset

#: the two codebook drawings (Figure 3.3a/b), kept in labeling_evaluation/assets/codebook/
CODEBOOK_DIR = Path(__file__).resolve().parents[2] / "assets" / "codebook"
CODEBOOK_DRAWINGS: Dict[str, Path] = {
    "codebook_classes": CODEBOOK_DIR / "codebook_architecture_classes.png",
    "codebook_dimensions": CODEBOOK_DIR / "codebook_every_dimension.png",
}

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
# 3.3.2 conditional fill-rate heatmap
# --------------------------------------------------------------------------
#: child fields (rows) and the conditions they are read under (columns)
HEATMAP_FIELDS = [
    "topType", "fusShape", "fusKin", "gearArch", "latSym",
    "wCount", "wingConf", "wing1_posV", "wing1_posL", "wing1_plan", "empType",
    "boomsPresent", "boom1_orient", "boom1_attach", "boom1_count", "boom_count",
]


def fill_rate_matrix(ds: Dataset, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Fill rate of each field on all aircraft, on winged aircraft, on boomed aircraft.

    Rule 1 (2026-09-19): a value an override hides is not determinable, so that aircraft
    leaves the cell's base instead of counting as unanswered (``attrs['left_out']``).
    """
    v = ds.variants
    dd = ds.data_dictionary
    winged = pd.to_numeric(v["wCount"], errors="coerce").fillna(0) > 0
    boomed = v["boomsPresent"].fillna(False).astype(bool)
    conditions = {
        f"all aircraft (n={len(v)})": pd.Series(True, index=v.index),
        f"wings present (n={int(winged.sum())})": winged,
        f"booms present (n={int(boomed.sum())})": boomed,
    }
    fields = [f for f in (fields or HEATMAP_FIELDS) if f in v.columns]
    rows, left = {}, {}
    for f in fields:
        hidden = a2.hidden_by_override(v, f, dd)
        if hidden.any():
            left[a2.FIELD_NAMES.get(f, f)] = int(hidden.sum())
        rows[a2.FIELD_NAMES.get(f, f)] = {
            name: float(v.loc[mask & ~hidden, f].notna().mean()) for name, mask in conditions.items()
        }
    out = pd.DataFrame(rows).T
    out.attrs["left_out"] = left
    return out


def fill_rate_heatmap(ds: Dataset, path: Optional[Path] = None) -> plt.Figure:
    m = fill_rate_matrix(ds)
    fig, ax = plt.subplots(figsize=(6.0, 0.30 * len(m) + 1.1))
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
# 3.1.3 patents per priority year
# --------------------------------------------------------------------------
def patents_per_year(time_coverage: pd.DataFrame, windows=None, partial_start: int = 2024,
                     path: Optional[Path] = None) -> plt.Figure:
    """Bars per priority year; the candidate windows alternate shaded / unshaded."""
    df = time_coverage
    fig, ax = plt.subplots(figsize=(8.0, 2.7))
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
    ax.set_ylabel("representative primary patents")
    ax.set_ylim(0, top)
    ax.set_title("Patents per priority year, with the candidate windows")
    ax.legend(loc="center left", fontsize=8)
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.1.1 provenance bars
# --------------------------------------------------------------------------
def provenance_bars(region: pd.DataFrame, office: pd.DataFrame,
                    path: Optional[Path] = None) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 2.8), gridspec_kw={"width_ratios": [1, 1.4]})
    for ax, df, key, title in ((axes[0], region, "region", "By region"),
                               (axes[1], office, "pub_office", "By publication office")):
        df = df.copy()
        y = np.arange(len(df))[::-1]
        ax.barh(y, df["patents"], color=GREYS[4], edgecolor="black", linewidth=0.5,
                label="acquired")
        ax.barh(y, df["representative"], color=GREYS[1], edgecolor="black", linewidth=0.5,
                label="representative")
        for yi, p, r in zip(y, df["patents"], df["representative share"]):
            ax.text(p + df["patents"].max() * 0.02, yi, f"{r:.2f}", va="center", fontsize=7.5)
        ax.set_yticks(y)
        ax.set_yticklabels(df[key], fontsize=8)
        ax.set_xlim(0, df["patents"].max() * 1.18)
        ax.set_title(title)
        ax.tick_params(axis="x", labelsize=8)
    axes[0].legend(loc="lower right", fontsize=8)
    axes[0].set_xlabel("patents (representative share at the bar end)")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.1.2 Lorenz curve (kept for the notebook; the document carries the table)
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
# 3.3.1 questions answered per aircraft (the dimension register)
# --------------------------------------------------------------------------
def slots_histogram(slots: pd.Series, path: Optional[Path] = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    ax.hist(slots, bins=np.arange(slots.min() - 0.5, slots.max() + 1.5, 1), color=GREYS[3],
            edgecolor="black", linewidth=0.5)
    q1, med, q3 = (slots.quantile(q) for q in (0.25, 0.5, 0.75))
    for val, style in ((q1, ":"), (med, "-"), (q3, ":")):
        ax.axvline(val, color="black", linestyle=style, linewidth=1)
    ax.text(0.98, 0.95,
            f"lower quartile {int(q1)}\nmedian {int(med)}\nupper quartile {int(q3)}\n"
            f"maximum {int(slots.max())}",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=GREYS[1],
            linespacing=1.4)
    ax.set_xlabel("questions of Figure 3.3b answered per unique aircraft")
    ax.set_ylabel("aircraft")
    ax.set_title("Completeness of one label, as a distribution")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.3.6 archetype levels: the two columns that pick the level
# --------------------------------------------------------------------------
def archetype_levels(card: pd.DataFrame, path: Optional[Path] = None) -> plt.Figure:
    """Singletons per level against the 5 % line; distinct against effective number."""
    df = card
    x = np.arange(len(df))
    n = int(df["aircraft"].iloc[0])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 2.7), gridspec_kw={"wspace": 0.3})
    ax1.bar(x, df["singletons"], color=GREYS[2], edgecolor="black", linewidth=0.5, width=0.6)
    ax1.axhline(0.05 * n, color="black", linestyle="--", linewidth=1)
    ax1.text(-0.4, 0.05 * n, f"5 % of {n}", ha="left", va="bottom", fontsize=7.5)
    for xi, s in zip(x, df["singletons"]):
        ax1.text(xi, s + n * 0.006, str(int(s)), ha="center", va="bottom", fontsize=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["level"])
    ax1.set_ylabel("archetypes holding one aircraft")
    ax1.set_title("Singletons per level")
    ax2.plot(x, df["distinct archetypes"], "-o", color="black", linewidth=1.2, markersize=4,
             label="distinct archetypes")
    ax2.plot(x, df["effective number"], "--s", color=GREYS[1], linewidth=1.2, markersize=4,
             label="effective number")
    for xi, d, e in zip(x, df["distinct archetypes"], df["effective number"]):
        ax2.text(xi, d + 5, str(int(d)), ha="center", va="bottom", fontsize=7.5)
        ax2.text(xi, e - 5, f"{e:.0f}", ha="center", va="top", fontsize=7.5, color=GREYS[1])
    ax2.set_xticks(x)
    ax2.set_xticklabels(df["level"])
    ax2.set_ylim(0, df["distinct archetypes"].max() * 1.18)
    ax2.set_title("Distinct against effective number")
    ax2.legend(fontsize=7.5, loc="upper left")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.3.7 class balance
# --------------------------------------------------------------------------
def class_balance_bars(balance: pd.DataFrame, path: Optional[Path] = None) -> plt.Figure:
    df = balance
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    y = np.arange(len(df))[::-1]
    # the unclassifiable row (G1 override, rule 1) is drawn white: beside the classes, not one of them
    ax.barh(y, df["count"], color=[GREYS[2] if pd.notna(s) else "white" for s in df["share"]],
            edgecolor="black", linewidth=0.5)
    for yi, c, s in zip(y, df["count"], df["share"]):
        ax.text(c + df["count"].max() * 0.015, yi,
                f"{int(c)}  ({s:.2f})" if pd.notna(s) else f"{int(c)}  (no type)", va="center",
                fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(df["name"], fontsize=8.5)
    ax.set_xlim(0, df["count"].max() * 1.25)
    ax.set_xlabel("unique aircraft (share in brackets)")
    ax.set_title("Architecture class balance, unique aircraft")
    return _save(fig, path)


# --------------------------------------------------------------------------
# 3.3.8 class shares per window
# --------------------------------------------------------------------------
def class_share_stacked_area(windows: pd.DataFrame, partial_label: str = "partial",
                             path: Optional[Path] = None) -> plt.Figure:
    df = windows.copy()
    count_col = "unique aircraft" if "unique aircraft" in df else "variants"
    classes = [c for c in df.columns if c not in ("window", count_col)]
    other = (1 - df[classes].sum(axis=1)).clip(lower=0)
    stack = df[classes].assign(**{"other classes": other})
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
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
    ax.set_xticklabels([f"{w}\n(n={n})" for w, n in zip(df["window"], df[count_col])],
                       fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of unique aircraft")
    ax.set_title("Architecture class shares per window (hatched = partial window)")
    ax.legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    return _save(fig, path)


# --------------------------------------------------------------------------
# the three SVG schemes
# --------------------------------------------------------------------------
FONT = "Inter, Helvetica, Arial, sans-serif"


class _Svg:
    """A tiny SVG writer: boxes, text, arrows, all monochrome."""

    def __init__(self, width: int, height: int):
        self.w, self.h = width, height
        self.parts: List[str] = []

    def rect(self, x, y, w, h, fill="#ffffff", stroke="#000000", sw=1.0, rx=4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=9, weight="normal", anchor="start", fill="#111111",
             style="normal"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
                          f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}" '
                          f'fill="{fill}">{escape(str(s))}</text>')

    def lines(self, x, y, lines, size=8.5, dy=None, **kw):
        dy = dy or size * 1.35
        for i, s in enumerate(lines):
            self.text(x, y + i * dy, s, size=size, **kw)

    def arrow(self, x1, y1, x2, y2, sw=1.1, dash=None, color="#000000"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                          f'stroke-width="{sw}" marker-end="url(#ah)"{d}/>')

    def line(self, x1, y1, x2, y2, sw=0.8, dash=None, color="#666666"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                          f'stroke-width="{sw}"{d}/>')

    def write(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n<defs><marker id="ah" viewBox="0 0 10 10" '
                'refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path d="M 0 0 L 10 5 L 0 10 z" fill="#000000"/></marker></defs>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n')
        path.write_text(head + "\n".join(self.parts) + "\n</svg>\n", encoding="utf-8")
        return path


def document_pipeline_svg(n: Dict, path: Path) -> Path:
    """Figure 1.1 — chapters 2 -> 3 -> 4, one way, with what each settles."""
    s = _Svg(760, 196)
    boxes = [
        ("Chapter 2", "Acquisition, refinement",
         [f"{n['acquired_s']} acquired → {n['representative_s']} repr.",
          f"{n['observations_s']} obs. → {n['unique']} unique aircraft",
          f"{n['figures_total_s']} figures → {n['figures_approved_s']} whole-aircraft"],
         "what enters, at which level"),
        ("Chapter 3", "Analysis by level",
         [f"patent: {n['primary']} primary patents",
          f"image: {n['figures_approved_s']} T2-labelled figures",
          f"unique aircraft: {n['unique']}, G1 to M3"],
         "the spread of the labels"),
        ("Chapter 4", "Quality and validity",
         ["flagship check against",
          "public products;",
          "intra-rater re-label later"],
         "whether the labels hold"),
        ("Chapter 5", "Method for evolution",
         ["unit, windows, archetype,",
          "distance, three measures,",
          "criterion fixed in advance"],
         "what the next chapters compute"),
    ]
    x0, w, h, y0, gap = 8, 172, 140, 12, 20
    for i, (chap, title, body, foot) in enumerate(boxes):
        x = x0 + i * (w + gap)
        s.rect(x, y0, w, h, fill="#f0f0f0" if i == 3 else "#ffffff", sw=1.1)
        s.rect(x, y0, w, 28, fill="#e4e4e4" if i == 3 else "#f0f0f0", sw=1.1, rx=4)
        s.text(x + 9, y0 + 19, chap, size=12, weight="bold")
        s.text(x + 9, y0 + 47, title, size=10, weight="bold")
        s.lines(x + 9, y0 + 67, body, size=8.4, dy=13)
        s.text(x + 9, y0 + h - 10, foot, size=8, style="italic", fill="#4d4d4d")
        if i < 3:
            s.arrow(x + w + 2, y0 + h / 2, x + w + gap - 2, y0 + h / 2, sw=1.3)
    s.text(380, 182, "one way: each chapter is read before the next can be", size=8.6,
           anchor="middle", style="italic", fill="#4d4d4d")
    return s.write(path)


def handover_svg(n: Dict, path: Path) -> Path:
    """Figure 5.1 — what each result of chapters 2 to 4 hands to each step of the method."""
    s = _Svg(760, 392)
    left = [
        ("2.2 · 2.2.1", f"{n['unique']} unique aircraft; O1, O2 removed, S3 new"),
        ("2.1.3", f"counts to {n['complete_to']}; shares to {n['year_max']} within region"),
        ("3.3.6", f"A1t: {n['a1t_distinct']} archetypes over {n['n_arch']} aircraft"),
        ("3.3.4 · 3.3.2", f"{n['informative']} informative fields; a blank is absence"),
        ("3.1.2", f"{n['named_companies']} named firms; {n['non_corporate_share']} not corporate"),
        ("3.2.4 · 4.1", f"{n['sens']} thin-evidence aircraft, carried; top label = public product {n['flagship_match']}/{n['flagship_public']}"),
        ("3.3.8", f"no class above {n['max_window_share']} in any window"),
    ]
    right = [
        ("5.2", "unit, time axis, windows"),
        ("5.3", "archetype and Gower distance"),
        ("5.4", "structure: Cramér's V"),
        ("5.5", "variety, balance, disparity"),
        ("5.6", "year shuffling, company bootstrap"),
        ("5.7", "dominant-design criterion"),
        ("5.8 · 5.9", "strata and scope"),
    ]
    # which left rows feed which right rows (indices)
    edges = [(0, 0), (1, 0), (0, 1), (2, 1), (3, 1), (3, 2), (2, 3), (4, 4), (5, 4), (6, 5),
             (2, 5), (4, 6), (1, 6)]
    s.text(12, 18, "Read from chapters 2 to 4", size=11, weight="bold")
    s.text(748, 18, "Used in chapter 5", size=11, weight="bold", anchor="end")
    lx, lw, rx, rw, h, y0, step = 12, 352, 486, 262, 42, 32, 50
    for i, (sec, txt) in enumerate(left):
        y = y0 + i * step
        s.rect(lx, y, lw, h, fill="#ffffff", sw=1.0)
        s.text(lx + 9, y + 17, sec, size=10, weight="bold", fill="#4d4d4d")
        s.text(lx + 9, y + 33, txt, size=9.6)
    for j, (sec, txt) in enumerate(right):
        y = y0 + j * step
        s.rect(rx, y, rw, h, fill="#f0f0f0", sw=1.0)
        s.text(rx + 9, y + 17, sec, size=10, weight="bold", fill="#4d4d4d")
        s.text(rx + 9, y + 33, txt, size=9.6)
    for i, j in edges:
        s.arrow(lx + lw + 3, y0 + i * step + h / 2, rx - 3, y0 + j * step + h / 2, sw=0.8,
                color="#555555")
    s.text(380, 386, "every setting of the method is a value read from a table above, not a choice",
           size=9.4, anchor="middle", style="italic", fill="#4d4d4d")
    return s.write(path)


def refinement_funnel_svg(n: Dict, path: Path) -> Path:
    """Figure 2.1 — the acquisition and refinement funnel, three refinements, three levels."""
    s = _Svg(760, 372)
    stages = [
        (f"{n['acquired_s']} patents acquired", f"PatSeer query, snapshot {n['snapshot']}",
         "patent level", 430),
        (f"{n['representative_s']} representative patents",
         f"of {n['wizard_approved_s']} approved at labelling: electric, vertical take-off, "
         "occupied, readable from the figures", "patent level", 400),
        (f"{n['unique']} unique aircraft",
         f"{n['primary']} primary patents · {n['observations_s']} aircraft observations · "
         f"{n['s3']} S3 similars counted as new", "unique-aircraft level", 370),
        (f"{n['figures_approved_s']} whole-aircraft figures",
         f"of {n['figures_approved_all_s']} approved; on {n['fig_patents']} patents, "
         f"median {n['median_figs']} per aircraft", "image level", 340),
    ]
    refinements = [
        ("Refinement 1 — representativity",
         [f"{n['disapproved_wizard']} disapproved at labelling: no aircraft image {n['r_noimg']},",
          f"pure UAV {n['r_uav']}, out of domain {n['r_ood']}, other {n['r_other']};",
          f"{n['gated_patents']} more leave on a Similar tag (UAV {n['r_sim_uav']}, "
          f"not electric {n['r_sim_el']}, STOL {n['r_sim_stol']})"]),
        ("Refinement 2 — observations → unique aircraft",
         [f"{n['o12_patents']} patents are O1 / O2 observations of an",
          f"aircraft already in the set; {n['multi_patents']} patents draw several"]),
        ("Refinement 3 — figure approval",
         [f"{n['figures_total_s']} figures examined, {n['figures_not_approved_s']} not approved;",
          f"{n['detail_figs']} approved detail figures set aside:",
          "only figures of the whole aircraft are analysed"]),
    ]
    x0, h, y0, step = 12, 50, 12, 104
    for i, (title, sub, level, w) in enumerate(stages):
        y = y0 + i * step
        fill = "#f0f0f0" if i in (1, 3) else "#ffffff"
        s.rect(x0, y, w, h, fill=fill, sw=1.1)
        s.text(x0 + 12, y + 21, title, size=12.5, weight="bold")
        s.text(x0 + 12, y + 39, sub, size=8.6, fill="#333333")
        s.text(x0 + w - 8, y + 13, level, size=8, anchor="end", style="italic", fill="#4d4d4d")
        if i < 3:
            s.arrow(x0 + 40, y + h + 2, x0 + 40, y + step - 3, sw=1.3)
    for i, (title, body) in enumerate(refinements):
        y = y0 + i * step + h + 3
        x = 456
        s.rect(x, y, 294, 50, fill="#ffffff", sw=0.8, dash="3,2")
        s.text(x + 9, y + 13, title, size=9.2, weight="bold")
        s.lines(x + 9, y + 24, body, size=7.6, dy=10)
        s.line(x0 + 44, y + 25, x - 2, y + 25, sw=0.7, dash="2,2", color="#888888")
    return s.write(path)


def design_space_order_svg(n: Dict, path: Path) -> Path:
    """Figure 3.3c — the four label cards of one unique aircraft, and the order of the analysis."""
    s = _Svg(760, 278)
    s.text(12, 17, f"One unique aircraft: {n['questions']} questions on four label cards "
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
    cards = [(title, f"{n[f'q_{c}']} questions", [kinds(c)] + body + [f"{n[f'cols_{c}']} export columns"])
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
    # the bridge: what the reading of the four cards together gives
    s.arrow(380, y0 + h + 4, 380, y0 + h + 42, sw=1.3)
    s.text(392, y0 + h + 21, f"read together: an aircraft answers a median of {n['median_q']} of the "
           f"{n['questions']} questions;", size=8.6, fill="#333333")
    s.text(392, y0 + h + 34, f"{n['informative']} export columns carry the information, "
           f"{n['near_constant']} are near-constant", size=8.6, fill="#333333")
    steps = [
        ("3.3.1", "completeness", "questions answered"),
        ("3.3.2", "missingness", "gap or absence"),
        ("3.3.3", "common answers", "the boundaries"),
        ("3.3.4", "field inventory", "the shortlist"),
        ("3.3.5", "derived features", "sparse → per aircraft"),
        ("3.3.6", "archetype levels", "the counting level"),
        ("3.3.7", "class balance", f"{n['n_classes']} classes"),
        ("3.3.8", "shares by window", "the shift to test"),
    ]
    y1, bw, bh, bgap = y0 + h + 54, 88, 62, 6
    x0 = 8
    for i, (num, title, gives) in enumerate(steps):
        x = x0 + i * (bw + bgap)
        s.rect(x, y1, bw, bh, fill="#f0f0f0" if i == 5 else "#ffffff", sw=1.0)
        s.text(x + 6, y1 + 15, num, size=8.2, weight="bold", fill="#4d4d4d")
        s.text(x + 6, y1 + 31, title, size=8.4, weight="bold")
        s.text(x + 6, y1 + 50, gives, size=7.8, style="italic", fill="#4d4d4d")
        if i < len(steps) - 1:
            s.arrow(x + bw + 1, y1 + bh / 2, x + bw + bgap - 1, y1 + bh / 2, sw=0.9)
    s.text(380, y1 + bh + 22, "the analysis walks left to right; the shaded step fixes the level "
           "every later count uses", size=8.6, anchor="middle", style="italic", fill="#4d4d4d")
    return s.write(path)


# --------------------------------------------------------------------------
# everything the index names
# --------------------------------------------------------------------------
def render_all(ds: Dataset, out_dir: Path, partial_window_start: int = 2024, **_) -> Dict[str, Path]:
    """Draw every figure of the document into ``out_dir/figures`` and return ``{name: path}``."""
    out_dir = Path(out_dir) / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    prov = a1.provenance_tables(ds)
    raw, canonical = a2.d8_filer_counts(ds)
    n = numbers.live(ds, partial_window_start)

    paths: Dict[str, Path] = {}
    svgs = {
        "fig_01_document_pipeline": document_pipeline_svg,
        "fig_02_refinement_funnel": refinement_funnel_svg,
        "fig_03_design_space_order": design_space_order_svg,
        "fig_05_handover": handover_svg,
    }
    for name, fn in svgs.items():
        paths[name] = fn(n, out_dir / f"{name}.svg")
    jobs = {
        "fill_rate_heatmap": lambda p: fill_rate_heatmap(ds, p),
        "patents_per_year": lambda p: patents_per_year(
            a1.time_coverage(ds), partial_start=partial_window_start, path=p),
        "provenance_bars": lambda p: provenance_bars(prov["region"], prov["pub_office"], p),
        "lorenz": lambda p: lorenz(raw, canonical, p),
        "slots_histogram": lambda p: slots_histogram(register.per_aircraft(ds), p),
        "archetype_levels": lambda p: archetype_levels(a2.d5_archetype_cardinality(ds), p),
        "class_balance_bars": lambda p: class_balance_bars(a2.d3_architecture_balance(ds), p),
        "class_share_stacked_area": lambda p: class_share_stacked_area(
            a2.d9_architecture_by_window(ds), path=p),
    }
    for name, job in jobs.items():
        path = out_dir / f"{name}.png"
        fig = job(path)
        plt.close(fig)
        paths[name] = path
    # the codebook drawings are static (drawn by the author, not from data): copied, not drawn
    for name, src in CODEBOOK_DRAWINGS.items():
        paths[name] = Path(shutil.copyfile(src, out_dir / src.name))
    return paths
