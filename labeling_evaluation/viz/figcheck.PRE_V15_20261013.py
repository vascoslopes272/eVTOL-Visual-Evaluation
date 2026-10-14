"""Layout checks for a finished matplotlib figure (the author's rules, 2026-10-12):
no text on top of other text, and nothing printed smaller than the floor size.

    overlaps(fig) -> list of (text a, text b) whose drawn boxes intersect
    small_text(fig, floor_pt) -> list of (text, size) under the floor
Tick labels of the same axis are compared too (catches crowded or rotated labels running into each other).
"""
from __future__ import annotations

from matplotlib.text import Text


def _texts(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    # tick labels matplotlib keeps for ticks outside the view are never drawn: only the drawn ones count
    all_ticks, drawn = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                all_ticks.update((id(tk.label1), id(tk.label2)))
            if not axis.get_visible():          # a twin axis hides the shared axis: its labels are never drawn
                continue
            for tk in axis._update_ticks():
                if tk.label1.get_visible():
                    drawn.add(id(tk.label1))
                if tk.label2.get_visible():
                    drawn.add(id(tk.label2))
    out = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if id(t) in all_ticks and id(t) not in drawn:
            continue
        try:
            bb = t.get_window_extent(r)
        except Exception:                     # noqa: BLE001
            continue
        if bb.width > 0 and bb.height > 0:
            out.append((t, bb.shrunk(0.92, 0.80)))   # a little slack: touching glyph boxes are not an overlap
    return out


def overlaps(fig):
    tx = _texts(fig)
    hits = []
    for i in range(len(tx)):
        for j in range(i + 1, len(tx)):
            (a, ba), (b, bb) = tx[i], tx[j]
            if ba.overlaps(bb):
                hits.append((a.get_text().replace("\n", " / ")[:40], b.get_text().replace("\n", " / ")[:40]))
    return hits


def small_text(fig, floor_pt=6.5):
    return sorted({(t.get_text().replace("\n", " / ")[:40], round(t.get_fontsize(), 1)) for t, _ in _texts(fig) if t.get_fontsize() < floor_pt})


def forbidden(fig, words):
    """(text, word) for every drawn text containing one of ``words`` (case-insensitive, whole-word where the word is a plain word).
    The author's label rules for Part I: never 'evtol.news', 'aircraft' / 'unique aircraft', 'window', 'filer'."""
    import re
    out = []
    for t, _ in _texts(fig):
        s = t.get_text()
        for w in words:
            if re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])" if w.isalpha() else re.escape(w), s, re.I):
                out.append((s.replace("\n", " / ")[:60], w))
    return out


def width_check(fig, width_in, tol=0.01):
    """The figure's canvas size against the final width of the dissertation and the 55 % height rule."""
    w, h = fig.get_size_inches()
    return {"width_in": round(w, 3), "height_in": round(h, 3), "width_ok": abs(w - width_in) <= tol, "height_ok": h <= 0.55 * w + 1e-6}
