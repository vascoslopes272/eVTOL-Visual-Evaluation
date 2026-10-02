"""Assemble PRELIMINARY_ANALYSIS.md from the index, the live numbers and the tables.

``write_markdown`` walks :data:`index.NODES` in order, prints each heading, its
level line and its prose (placeholders filled from :func:`numbers.live`), then
the figures and tables the node owns, each captioned with the node's number.
The prose lives in ``index.py``; the numbers are regenerated on every run and
are never typed by hand.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from . import index, numbers
from .export import md_safe
from .loaders import Dataset

MAX_ROWS = 16


def _prov_md(name: str, idx, values: Optional[Dict], kind: str,
             tables: Optional[Dict] = None) -> str:
    """The provenance line of one item — unit of analysis, base and transform — as a
    markdown paragraph, or ``""``.

    The line is optional by design: an index module that does not define ``provenance``
    (the Preliminary Analysis) renders exactly as before, and an item whose entry is
    missing or broken costs a line, never the build.
    """
    fn = getattr(idx, "provenance", None)
    if fn is None:
        return ""
    try:
        line = fn(name, values, kind, tables)
    except Exception:                                  # a bad entry never breaks the document
        return ""
    return f"\n*{line}*\n" if line else ""


def _take_md(name: str, idx, values: Optional[Dict], kind: str,
             tables: Optional[Dict] = None) -> str:
    """The takeaway line of one item — what the reader should conclude — as a markdown
    paragraph, or ``""``.

    Optional in exactly the same way as :func:`_prov_md`: an index module that does not define
    ``takeaway`` (the Preliminary Analysis) renders byte-for-byte as before, and a broken entry
    costs a line, never the build. It prints under the provenance line and in the same grey —
    the renderer styles any paragraph opening with "Takeaway: " like the "Unit: " one.
    """
    fn = getattr(idx, "takeaway", None)
    if fn is None:
        return ""
    try:
        line = fn(name, values, kind, tables)
    except Exception:                                  # a bad entry never breaks the document
        return ""
    return f"\n*Takeaway: {line}*\n" if line else ""


def _quest_md(name: str, idx, values: Optional[Dict], kind: str,
              tables: Optional[Dict] = None) -> str:
    """The question line of one item — which of the eight sector questions it answers, and
    in what way — as a markdown paragraph, or ``""``.

    Optional in exactly the same way as :func:`_prov_md` and :func:`_take_md`: an index
    module that does not define ``question`` (the Preliminary Analysis) renders
    byte-for-byte as before, and a broken entry costs a line, never the build. It prints
    last of the three grey lines and in the same grey — the renderer styles any paragraph
    opening with "Question: " like the "Unit: " one.

    The line also carries the item's DEGREE OF IMPORTANCE when the index module offers a
    ``grade`` register — ``… — direct · core``, ``… — describes · weak, low
    representativeness (9 aircraft)`` — rather than opening a fourth grey line under an
    already heavily annotated figure. That register is optional in its own right: an index
    module with ``question`` but no ``grade`` prints the question line exactly as before,
    and a grade that raises costs the tail of one line, never the build.
    """
    fn = getattr(idx, "question", None)
    if fn is None:
        return ""
    try:
        line = fn(name, values, kind, tables)
    except Exception:                                  # a bad entry never breaks the document
        return ""
    if not line:
        return ""
    gfn = getattr(idx, "grade", None)                   # the fourth register; absent in the PA
    if gfn is not None:
        try:
            deg = gfn(name, values, kind, tables)
        except Exception:                              # a bad grade never breaks the document
            deg = ""
        if deg:
            line = f"{line} · {deg}"
    return f"\n*Question: {line}*\n"


#: the four short lines of the second reorganisation (2026-09-23), in printed order. An index
#: module that offers ``source`` prints these INSTEAD of the older Unit/Takeaway/Question trio,
#: so the Preliminary Analysis — which offers none of them — renders byte-for-byte as before.
FOUR_LINES = (("source", "Source"), ("unit", "Unit"),
              ("read", "How to read"), ("why", "Why this way"))


def _four_md(name: str, idx, values: Optional[Dict], kind: str,
             tables: Optional[Dict] = None) -> str:
    """Source / Unit / How to read / Why this way, one grey paragraph each, or ``""``.

    A graph carries these four and nothing else: the finding is written once, at the end of the
    question the graphs answer (:func:`_answer_md`). A missing register costs its line, never the
    build.
    """
    if getattr(idx, "source", None) is None:
        return ""
    out = []
    for attr, label in getattr(idx, "FOUR_LINES", FOUR_LINES):   # the brief prints its own set
        fn = getattr(idx, attr, None)
        if fn is None:
            continue
        try:
            line = fn(name, values, kind, tables)
        except Exception:                                  # a bad entry never breaks the document
            continue
        if line:
            out.append(f"\n*{label}: {line}*\n")
    return "".join(out)


def _answer_md(question: str, idx, values: Optional[Dict],
               tables: Optional[Dict] = None) -> str:
    """The block that closes a question — the finding, big, once, under the graphs that earned it."""
    fn = getattr(idx, "answer", None)
    if fn is None:
        return ""
    try:
        text = fn(question, values, tables)
    except Exception:                                      # a bad Answer never breaks the document
        return ""
    return f'<div class="answer" markdown="1">\n\n**Answer.** {text}\n\n</div>\n' if text else ""


def _table_md(name: str, table: pd.DataFrame, number: str, idx=index,
              values: Optional[Dict] = None, tables: Optional[Dict] = None) -> str:
    t = md_safe(table)
    cols = idx.COLUMNS.get(name)
    if cols:
        t = t[[c for c in cols if c in t.columns]]
    cap = idx.ROW_CAP.get(name, MAX_ROWS)
    note = ""
    if len(t) > cap:
        note = f"\n\n*First {cap} of {len(t)} rows; the full table is `tables/{name}.csv`.*"
        t = t.head(cap)
    caption = idx.TABLE_CAPTIONS.get(name, name)
    four = _four_md(name, idx, values, "table", tables)
    if four:                                               # the four lines replace the old trio
        return (f"**Table {number} — {caption}.**\n\n{t.to_markdown(index=False)}{note}\n{four}")
    prov = _prov_md(name, idx, values, "table", tables)
    take = _take_md(name, idx, values, "table", tables)
    quest = _quest_md(name, idx, values, "table", tables)
    return (f"**Table {number} — {caption}.**\n\n{t.to_markdown(index=False)}{note}\n"
            f"{prov}{take}{quest}")


def _figure_md(name: str, path: Path, out_dir: Path, number: str, idx=index,
               panels: Optional[Dict] = None, values: Optional[Dict] = None,
               tables: Optional[Dict] = None) -> str:
    rel = Path(path).relative_to(out_dir) if Path(path).is_relative_to(out_dir) else Path(path)
    width = idx.FIG_WIDTH.get(name, "80%")
    caption = idx.FIGURE_CAPTIONS.get(name, name)
    # a figure that holds more than one graph names each of them, with the mark printed on it
    marks = (panels or {}).get(name) or []
    sub = ""
    if len(marks) > 1:
        sub = " " + " ".join(f"**{m}** {lbl};" for m, lbl in marks).rstrip(";") + "."
    four = _four_md(name, idx, values, "figure", tables)
    lines_ = four or (f"{_prov_md(name, idx, values, 'figure', tables)}"
                      f"{_take_md(name, idx, values, 'figure', tables)}"
                      f"{_quest_md(name, idx, values, 'figure', tables)}")
    md = (f"![Figure {number} — {caption}.{sub}]({rel.as_posix()}){{: width=\"{width}\" }}\n\n"
          f"*Figure {number} — {caption}.{sub}*\n{lines_}")
    if name in idx.LANDSCAPE:   # its own landscape page (the renderer's div.landscape)
        md = f'<div class="landscape" markdown="1">\n\n{md}\n</div>\n'
    return md


def write_markdown(ds: Dataset, tables: Dict[str, pd.DataFrame], figures: Dict[str, Path],
                   out_dir: Path, filename: str = "PRELIMINARY_ANALYSIS.md",
                   values: Optional[Dict] = None, partial_window_start: int = 2024,
                   idx=index, generated_by: Optional[str] = None, keep_with_next: bool = False,
                   panels: Optional[Dict] = None) -> Path:
    """Write the document; returns its path. ``idx`` is the index module (the Preliminary
    Analysis by default, ``la_index`` for the Labelling Analysis)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    values = values or numbers.live(ds, partial_window_start)
    today = _dt.date.today().isoformat()
    lines = [
        f"# {idx.TITLE}",
        "",
        generated_by or (
            f"Date: {today} · Generated by `labeling_evaluation/notebooks/10_preliminary_analysis.ipynb` "
            f"from the batch exports in `{ds.root.name}/labels` (PatSeer snapshot {values['snapshot']}) · "
            "Every number comes from the tables in `tables/`; the prose is edited in "
            "`src/dataset_facts/index.py`."),
        "",
    ]
    # the front-page index (2026-09-24): present only on a module that defines it (sm_index),
    # so index.py and la_index.py render exactly as before
    toc = getattr(idx, "index_md", None)
    if toc:
        lines += [toc(), ""]
    lines += [
        "---",
        "",
    ]
    prev_chapter: Optional[str] = None
    for n in idx.NODES:
        nid = n["id"]
        # a chapter IS a question since the second reorganisation, so it closes with its Answer —
        # printed when the walk leaves the chapter, and after the loop for the last one. An index
        # module with no ``answer`` (the Preliminary Analysis) prints nothing here.
        top = nid.split(".")[0]
        if top != prev_chapter:
            if prev_chapter is not None:
                ans = _answer_md(prev_chapter, idx, values, tables)
                if ans:
                    lines += [ans, ""]
            prev_chapter = top
        # an appendix opens a page like a chapter; ``APPENDIX`` is optional, so an index module
        # without it (the Preliminary Analysis) renders byte-for-byte as before
        chapter = idx.depth(nid) == 0 and (nid[0].isdigit()
                                           or nid in getattr(idx, "APPENDIX", ()))
        if chapter and nid != "1" and not keep_with_next:
            lines += ["---", ""]
        head = [idx.heading(nid, values), ""]
        lvl = idx.level_line(nid)
        if lvl:
            head += [lvl, ""]
        body = idx.text(nid, values)
        if body:
            head += [body, ""]
        figs = [f for f in n.get("figures", []) if f in figures]
        tabs_ = [t for t in n.get("tables", []) if t in tables]
        first_fig = figs[0] if figs and figs[0] not in getattr(idx, "LANDSCAPE", set()) else None
        if keep_with_next:
            # the heading travels with the first block under it; a chapter opens a new page
            cls = "keep chapter-start" if chapter else "keep"
            first = []
            # a node named in the index module's optional ``NO_KEEP`` binds its heading to its
            # prose only: the item under it flows, instead of dragging a tall figure onto the
            # next page and leaving the rest of this one blank. Absent in ``index`` and in
            # ``la_index``, so both of those documents render exactly as before.
            if nid in getattr(idx, "NO_KEEP", ()):
                first = []
            elif first_fig:
                first = [_figure_md(first_fig, figures[first_fig], out_dir,
                                    idx.figure_number(nid, 0, len(figs)), idx, panels,
                                    values, tables), ""]
            elif not figs and tabs_:
                first = [_table_md(tabs_[0], tables[tabs_[0]], idx.table_number(nid, 0, len(tabs_)),
                                   idx, values, tables), ""]
            lines += [f'<div class="{cls}" markdown="1">', ""] + head + first + ["</div>", ""]
            done_fig = {first_fig} if (first_fig and first) else set()
            done_tab = {tabs_[0]} if (not figs and tabs_ and first) else set()
        else:
            lines += head
            done_fig, done_tab = set(), set()
        for k, name in enumerate(figs):
            if name in done_fig:
                continue
            lines += [_figure_md(name, figures[name], out_dir,
                                 idx.figure_number(nid, k, len(figs)), idx, panels,
                                 values, tables), ""]
        tabs = [t for t in n.get("tables", []) if t in tables]
        for k, name in enumerate(tabs):
            if name in done_tab:
                continue
            lines += [_table_md(name, tables[name], idx.table_number(nid, k, len(tabs)),
                                idx, values, tables), ""]
        tail = idx.after(nid, values)
        if tail:
            lines += [tail, ""]
    if prev_chapter is not None:                           # the Answer of the last chapter
        ans = _answer_md(prev_chapter, idx, values, tables)
        if ans:
            lines += [ans, ""]
    path = out_dir / filename
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
