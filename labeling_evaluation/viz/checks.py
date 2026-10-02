"""Compare a notebook with the 45-page document: its quoted numbers and its tables.

    from viz import checks
    checks.numbers({"acquired_s": "1 639", ...}, "1")           # one row per number: notebook | document | match
    checks.table(frame, "la_ari_timeline", cfg, key=["company"])   # one row per table: cells compared | matched

Both are tolerant of FORMATTING only: a number is written the way the document prints it, so the two strings
must be equal once whitespace, minus signs and dashes are normalised; a table cell is compared at the number of
decimals the document printed (a notebook value of 0.4286 matches a document 0.43, never 0.44). A difference of
value is never absorbed. A row that differs because of a ruling made after the document (``expected`` maps a row
key to the ruling's name) is labelled with the ruling and counted apart from the failures.

``numbers`` reads ``tests/reference/document_numbers.csv`` (every number the document's text quotes, as printed);
``table`` reads ``<roots.reference>/tables/<ref_name>.csv`` of ``labelling_analysis.yaml``.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union

import numpy as np
import pandas as pd

PILLAR = Path(__file__).resolve().parent.parent
NUMBERS_FILE = PILLAR / "tests" / "reference" / "document_numbers.csv"

#: label of the one ruling made after the document that is allowed to move numbers
SRW_RULING = "expected: SRW→LC ruling 2026-10-01"


def _norm(s) -> str:
    """Formatting-only normalisation of a printed value: spaces (thin, no-break) collapsed, minus and dash
    variants unified."""
    s = "" if s is None else str(s)
    s = re.sub(r"[   \s]+", " ", s).strip()
    return s.replace("−", "-").replace("–", "-").replace("—", "-")


# ------------------------------------------------------------------------------------------ numbers
def reference_numbers(chapter: str) -> pd.DataFrame:
    """The document's quoted numbers of one chapter: name, value as printed."""
    d = pd.read_csv(NUMBERS_FILE, keep_default_na=False, dtype=str)
    d = d[d["chapters"].str.split().map(lambda c: chapter in c)]
    return d[["name", "value"]].reset_index(drop=True)


def numbers(values: Mapping[str, str], chapter: str, expected: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """Compare the notebook's numbers with the document's: one row per name in ``values``.

    ``values`` maps a placeholder name to the value formatted as the document prints it. ``expected`` maps a
    name to the ruling that makes it differ from the document (its row is then ``expected``, not a failure).
    A name the document does not quote in this chapter is reported as ``not in the document``.
    Columns: name, notebook, document, match (``yes`` / ``NO`` / ``expected: ...`` / ``not in the document``).
    """
    ref = dict(zip(*[reference_numbers(chapter)[c] for c in ("name", "value")]))
    expected = expected or {}
    rows = []
    for name, val in values.items():
        doc = ref.get(name)
        if doc is None:
            m = "not in the document"
        elif _norm(val) == _norm(doc):
            m = "yes"
        else:
            m = expected.get(name, "NO")
        rows.append({"name": name, "notebook": str(val), "document": "" if doc is None else doc, "match": m})
    return pd.DataFrame(rows)


def missing_numbers(values: Mapping[str, str], chapter: str, names: Optional[Iterable[str]] = None) -> List[str]:
    """Names the document quotes in ``chapter`` (restricted to ``names`` if given) that ``values`` lacks."""
    ref = set(reference_numbers(chapter)["name"])
    if names is not None:
        ref &= set(names)
    return sorted(ref - set(values))


# ------------------------------------------------------------------------------------------ tables
def reference_table(ref_name: str, cfg) -> pd.DataFrame:
    """The document's CSV of a table, read as text (so a printed '0.90' stays '0.90')."""
    path = Path(cfg.roots["reference"]) / "tables" / f"{ref_name}.csv"
    return pd.read_csv(path, keep_default_na=False, dtype=str)


def _decimals(s: str) -> Optional[int]:
    """Decimals printed in a numeric string (None if it is not a plain number)."""
    s = _norm(s)
    if re.fullmatch(r"[+-]?\d+(\.\d+)?", s):
        return len(s.split(".")[1]) if "." in s else 0
    return None


def _same_cell(a, b, rename: Mapping[str, str]) -> bool:
    """Is notebook cell ``a`` the document's ``b``, up to the formatting the document printed?"""
    sa, sb = _norm(a), _norm(b)
    if sa in ("nan", "None", "<NA>", "NaT"):
        sa = ""
    if sb in ("nan", "None", "<NA>", "NaT"):
        sb = ""
    if sa == sb:
        return True
    d = _decimals(sb)
    if d is not None:
        try:
            fa, fb = float(sa), float(sb)
        except ValueError:
            return False
        da = _decimals(sa)
        if da is not None and da <= d:                  # printed at the document's precision (or coarser): equal as printed
            return round(fa, d) == round(fb, d)
        # more precise than the document: it must round to the document's value, and the document's value is read
        # at no coarser than two decimals (a trailing zero may have been dropped when it printed 0.90 as 0.9)
        return abs(fa - fb) < 0.5 * 10 ** (-max(d, 2)) + 1e-12
    ca = rename.get(sa, sa).casefold()
    cb = rename.get(sb, sb).casefold()
    return ca == cb


def table(frame: pd.DataFrame, ref_name: str, cfg, key: Optional[Sequence[str]] = None,
          rename: Optional[Mapping[str, str]] = None, expected: Optional[Callable] = None,
          columns: Optional[Sequence[str]] = None, name: Optional[str] = None,
          ref_frame: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Compare a notebook table with the document's CSV, cell by cell on the document's columns.

    ``key``: columns that identify a row (default: the row position). ``rename``: display names that differ
    only in the label the thesis prints (e.g. ``{"Tilt Rotor": "Tilt Propulsor"}``, the display rename of
    2026-09-28), applied to text cells and compared case-insensitively. ``columns``: restrict to these
    document columns. ``expected(row_key, column) -> str | None``: the ruling that explains a difference in that
    cell (labelled, not counted as a failure).

    Returns a one-row summary: table, rows (notebook | document), cells compared, matched, expected (differences
    owed to a ruling), differences (failures), status. The cell differences are in ``result.attrs["detail"]``;
    columns the notebook lacks in ``result.attrs["missing_columns"]``.
    """
    rename = dict(rename or {})
    ref = ref_frame if ref_frame is not None else reference_table(ref_name, cfg)
    cols = [c for c in (columns or ref.columns) if c in ref.columns]
    miss = [c for c in cols if c not in frame.columns]
    cols = [c for c in cols if c in frame.columns]
    f = frame.reset_index(drop=True).copy()
    if key:
        f_i = f.assign(**{k: f[k].astype(str).map(lambda x: rename.get(_norm(x), _norm(x)).casefold()) for k in key})
        r_i = ref.assign(**{k: ref[k].astype(str).map(lambda x: rename.get(_norm(x), _norm(x)).casefold()) for k in key})
        fi = f_i.set_index(list(key))
        ri = r_i.set_index(list(key))
        keys = list(ri.index)
        fi_idx = set(fi.index)
    else:
        fi, ri = f, ref
        keys = list(range(len(ref)))
        fi_idx = set(range(len(f)))
    detail, n_cells, n_ok, n_exp = [], 0, 0, 0
    for k in keys:
        if k not in fi_idx:
            detail.append({"row": k, "column": "(row)", "notebook": "missing", "document": "present",
                           "label": "NO"})
            continue
        for c in cols:
            if key and c in key:
                continue
            n_cells += 1
            a, b = fi.loc[k, c], ri.loc[k, c]
            if isinstance(a, pd.Series):          # duplicate key: take the first row
                a, b = a.iloc[0], b.iloc[0]
            if _same_cell(a, b, rename):
                n_ok += 1
            else:
                why = expected(k, c) if expected else None
                n_exp += bool(why)
                detail.append({"row": k, "column": c, "notebook": a, "document": b, "label": why or "NO"})
    extra = [k for k in fi_idx if k not in set(keys)]
    for k in extra:
        detail.append({"row": k, "column": "(row)", "notebook": "present", "document": "missing", "label": "NO"})
    fails = sum(1 for d in detail if d["label"] == "NO")
    out = pd.DataFrame([{"table": name or ref_name, "rows (notebook | document)": f"{len(f)} | {len(ref)}",
                         "cells compared": n_cells, "matched": n_ok, "expected differences": n_exp,
                         "differences": fails,
                         "status": ("match" if fails == 0 and n_exp == 0 else
                                    "match except expected" if fails == 0 else "DIFFERS")}])
    out.attrs["detail"] = pd.DataFrame(detail, columns=["row", "column", "notebook", "document", "label"])
    out.attrs["missing_columns"] = miss
    return out


def detail(result: pd.DataFrame) -> pd.DataFrame:
    """The cell differences of a ``table`` result (empty when it matches)."""
    return result.attrs.get("detail", pd.DataFrame())


def changed_cells(new: pd.DataFrame, old: pd.DataFrame, key: Optional[Sequence[str]] = None,
                  ruling: str = SRW_RULING, rename: Optional[Mapping[str, str]] = None) -> Callable:
    """The ``expected`` argument of :func:`table`, built from two versions of the SAME table: ``new`` (under the
    current rulings) and ``old`` (recomputed with the document's own rulings, e.g. the class fold SRW -> ER).
    A cell is owed to the ruling exactly when it differs between the two, so a difference anywhere the ruling
    does not reach is still reported as a failure.

    Row keys are those of :func:`table`: a scalar for one key column, a tuple for several, the position for none
    (pass the same ``key`` and ``rename``).
    """
    rename = dict(rename or {})

    def _k(frame):
        f = frame.reset_index(drop=True)
        if not key:
            return f
        norm = f[list(key)].astype(str).map(lambda x: rename.get(_norm(x), _norm(x)).casefold())
        f = f.set_index(pd.MultiIndex.from_frame(norm) if len(key) > 1 else pd.Index(norm[key[0]]))
        return f

    n, o = _k(new), _k(old)

    def expected(row_key, column):
        try:
            a, b = n.loc[row_key, column], o.loc[row_key, column]
        except KeyError:
            return None
        if isinstance(a, pd.Series):
            a, b = a.iloc[0], b.iloc[0]
        return None if _same_cell(a, b, {}) else ruling
    return expected


#: the display renames of 2026-09-28 (thesis wording -> the document's), applied inside a cell
DISPLAY_RENAMES = (("Tilt Propulsor", "Tilt Rotor"), ("propulsor units", "units"), ("propulsor unit", "unit"),
                   ("Tilt Propulsor's", "Tilt Rotor's"))


def doc_wording(text: str) -> str:
    """A cell written in the thesis names (Tilt Propulsor, propulsor units) in the 45-page document's words."""
    for new, old in DISPLAY_RENAMES:
        text = text.replace(new, old)
    return text


def rename_map(frame: pd.DataFrame, columns: Optional[Sequence[str]] = None) -> Dict[str, str]:
    """``rename`` argument of :func:`table` for cells that differ only by the display renames: every text cell of ``columns``
    mapped to its wording in the document (substring renames, which ``rename`` alone cannot do)."""
    cols = list(columns) if columns is not None else [c for c in frame.columns if frame[c].dtype == object]
    out = {}
    for c in cols:
        for s in frame[c].dropna().astype(str).unique():
            d = doc_wording(s)
            if d != s:
                out[_norm(s)] = d
    return out


def brief_table(cfg, number: int, filename: str = "LABELLING_ANALYSIS_BRIEF.md") -> pd.DataFrame:
    """The markdown table that follows ``**Table <number> —`` in the 45-page document's text, as a frame of strings (the bold
    markers removed): the printed table, to compare a printed notebook table with.
    """
    lines = (Path(cfg.roots["reference"]) / filename).read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(f"**Table {number} —"))
    rows = []
    for l in lines[i + 1:]:
        if l.startswith("|"):
            rows.append([c.strip().replace("**", "") for c in l.strip().strip("|").split("|")])
        elif rows:
            break
    header, body = rows[0], [r for r in rows[1:] if not all(set(c) <= set(":-") for c in r)]
    return pd.DataFrame(body, columns=header)
