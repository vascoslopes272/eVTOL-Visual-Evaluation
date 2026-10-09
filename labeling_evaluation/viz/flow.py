"""Flowcharts for the Methodology: boxes and arrows drawn with matplotlib at the printed width (notebook 46, slot "method").

    from viz import flow
    fig = flow.chart(cfg, nodes, edges, width="full", rows=None)

nodes: list of dicts {id, text, kind} — kind in {"data", "step", "test", "figure", "answer"} picks the box style;
       text may hold "\\n" for a second line. Nodes are laid out left→right in columns by `col` (default: order given);
       several nodes in one column stack vertically.
edges: list of (from_id, to_id) or (from_id, to_id, label).
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from viz import style

KIND = {                       # face, edge, box style
    "data":   dict(fc="#f2f2f2", ec="#555555", box="round,pad=0.35"),
    "step":   dict(fc="#ffffff", ec="#333333", box="round,pad=0.35"),
    "test":   dict(fc="#e8f1fa", ec="#2b6ca3", box="round,pad=0.35"),
    "figure": dict(fc="#fff6e0", ec="#b8860b", box="round,pad=0.35"),
    "answer": dict(fc="#e9f5ea", ec="#2e7d32", box="round,pad=0.35"),
}
Edge = Union[Tuple[str, str], Tuple[str, str, str]]


def _layout(nodes: List[dict]) -> Dict[str, Tuple[float, float]]:
    cols: Dict[int, List[str]] = {}
    for i, n in enumerate(nodes):
        cols.setdefault(int(n.get("col", i)), []).append(n["id"])
    ncol = max(cols) + 1
    pos = {}
    for c, ids in cols.items():
        k = len(ids)
        for j, nid in enumerate(ids):
            y = 0.5 if k == 1 else 1 - (j + 0.5) / k
            pos[nid] = ((c + 0.5) / ncol, y)
    return pos


def chart(cfg, nodes: List[dict], edges: Sequence[Edge], width: str = "full", aspect: float = None,
          fontsize: float = None):
    cols: Dict[int, int] = {}
    for i, n in enumerate(nodes):
        cols[int(n.get("col", i))] = cols.get(int(n.get("col", i)), 0) + 1
    rows = max(cols.values()) if cols else 1
    if aspect is None:
        aspect = 0.10 + 0.11 * rows                       # one row of boxes ≈ 0.21 × width
    w, h = style.size(cfg, width, aspect)
    fig, ax = plt.subplots(figsize=(w, h), constrained_layout=True)
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fs = fontsize or max(float(cfg.style.get("min_font_pt", 7)), float(cfg.style.get("small_font_pt", 8)) - 0.5)
    pos = _layout(nodes)
    boxes = {}
    for n in nodes:
        x, y = pos[n["id"]]
        k = KIND[n.get("kind", "step")]
        t = ax.text(x, y, n["text"], ha="center", va="center", fontsize=fs, wrap=False, zorder=3,
                    bbox=dict(boxstyle=k["box"], fc=k["fc"], ec=k["ec"], lw=0.8))
        boxes[n["id"]] = t
    fig.canvas.draw()
    for e in edges:
        a, b = e[0], e[1]
        (xa, ya), (xb, yb) = pos[a], pos[b]
        arrow = FancyArrowPatch((xa, ya), (xb, yb), arrowstyle="-|>", mutation_scale=9, lw=0.8, color="#333333",
                                shrinkA=22, shrinkB=22, connectionstyle="arc3,rad=0.0" if abs(ya - yb) < 1e-6 else "arc3,rad=0.15",
                                zorder=2)
        ax.add_patch(arrow)
        if len(e) > 2 and e[2]:
            ax.text((xa + xb) / 2, (ya + yb) / 2 + 0.07, e[2], ha="center", va="bottom", fontsize=fs - 1, color="#333333",
                    bbox=dict(fc="white", ec="none", pad=0.5), zorder=4)
    fit_arrows(fig)
    return fig


def fit_arrows(fig) -> None:
    """Trim every arrow to the edge of the boxes it joins (+2 pt), whatever the box width."""
    ax = fig.axes[0]
    fig.canvas.draw()
    pt = 72.0 / fig.dpi
    boxes = {}
    for t in ax.texts:
        if t.get_bbox_patch() is None:
            continue
        ext = t.get_bbox_patch().get_window_extent()
        cx, cy = ax.transData.transform(t.get_position())
        boxes[(round(cx), round(cy))] = (ext.width / 2, ext.height / 2)
    for a in ax.patches:
        if not isinstance(a, FancyArrowPatch):
            continue
        (xa, ya), (xb, yb) = a._posA_posB
        pa, pb = ax.transData.transform((xa, ya)), ax.transData.transform((xb, yb))
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        norm = max((dx ** 2 + dy ** 2) ** 0.5, 1e-9)
        ux, uy = abs(dx) / norm, abs(dy) / norm
        for key, attr in ((pa, "shrinkA"), (pb, "shrinkB")):
            hw, hh = boxes.get((round(key[0]), round(key[1])), (22 / pt, 22 / pt))
            reach = min(hw / ux if ux > 1e-9 else float("inf"), hh / uy if uy > 1e-9 else float("inf"))
            setattr(a, attr, reach * pt + 2.0)
