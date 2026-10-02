"""The dimension register: the codebook drawing (Figure 3.3b) as a table.

User ruling 2026-09-21: the list of questions is the one on the drawing
"Every dimension, at a glance" (the wizard's cards G1 to M3), not the export
columns. ``assets/codebook/dimension_register.csv`` holds one row per question
of the drawing:

* ``card`` / ``box`` / ``repeat`` / ``question``: as printed on the drawing;
* ``kind``: Dimension (one answer from a list), Tick (a box ticked or not),
  Number (a count), Tag, Escape (humanUncertain, overrides) or Process;
* ``on_list``: yes for what the drawing shows; the few coded columns it does not
  show carry ``no`` and are left out of every count;
* ``columns``: a regular expression matched in full against the coded G1-M3
  export columns (the repeats per boom group, wing panel, propulsor host and
  propulsor type all fall under one question);
* ``when``: optional ``<field> in A|B`` / ``<field> not in A|B`` that narrows the
  aircraft (the integrated-surface planform shares ``wing1_plan`` with the wing
  panel planform).

Only Dimension, Tick and Number rows that are on the list count as questions.
Rows sharing card + box + question count as one question, so renaming two rows
alike merges them. Edit the CSV to rename or re-kind a question and re-run: no
count in section 3.3 is typed anywhere else.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .loaders import Dataset

REGISTER_PATH = Path(__file__).resolve().parents[2] / "assets" / "codebook" / "dimension_register.csv"
CARDS = ("G1", "M1", "M2", "M3")
#: the kinds that make a question; the rest sit beside the questions
COUNTED_KINDS = ("Dimension", "Tick", "Number")
KIND_ORDER = ["Dimension", "Tick", "Number", "Tag", "Escape", "Process"]
KEY = ["card", "box", "question"]


def load(path: Path = REGISTER_PATH) -> pd.DataFrame:
    """The register as edited, with ``on_list`` and ``counted`` as booleans."""
    reg = pd.read_csv(path, keep_default_na=False, dtype=str)
    reg["kind"] = reg["kind"].str.strip()
    reg["on_list"] = reg["on_list"].str.strip().str.lower().isin(["yes", "y", "true", "1"])
    reg["counted"] = reg["on_list"] & reg["kind"].isin(COUNTED_KINDS)
    return reg


def coded_columns(ds: Dataset) -> List[str]:
    """Every coded G1-M3 export column (option id, boolean or count) the data carries."""
    dd = ds.data_dictionary
    keep = dd["section"].isin(CARDS) & dd["kind"].isin(["id", "bool", "int"])
    return [c for c in dd.loc[keep, "column"] if c in ds.variants.columns]


def mapping(ds: Dataset, reg: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """One row per (register row, export column) it claims; warns on unclaimed columns."""
    reg = load() if reg is None else reg
    cols = coded_columns(ds)
    rows = []
    for i, r in reg.iterrows():
        pat = re.compile(r["columns"])
        rows += [(i, c) for c in cols if pat.fullmatch(c)]
    m = pd.DataFrame(rows, columns=["row", "column"]).merge(
        reg.drop(columns="columns"), left_on="row", right_index=True)
    free = sorted(set(cols) - set(m["column"]))
    if free:
        warnings.warn(f"coded columns no register row claims: {free}")
    m.attrs["unclaimed"] = free
    return m


def _when(v: pd.DataFrame, when: str) -> pd.Series:
    if not when.strip():
        return pd.Series(True, index=v.index)
    hit = re.fullmatch(r"\s*(\w+)\s+(not\s+in|in)\s+(.+?)\s*", when)
    if not hit:
        raise ValueError(f"register 'when' not understood: {when!r}")
    field, op, values = hit.groups()
    inside = v[field].astype(str).isin(values.split("|"))
    return ~inside if op.startswith("not") else inside


def questions(ds: Dataset, reg: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """One row per question (card + box + question) with its kind, columns and answer rate."""
    reg = load() if reg is None else reg
    m = mapping(ds, reg)
    ans = answered(ds, reg, m)
    out = []
    for key, g in reg.groupby(KEY, sort=False):
        cols = sorted(set(m.loc[m["row"].isin(g.index), "column"]))
        out.append(dict(zip(KEY, key), repeat=g["repeat"].iloc[0], kind=g["kind"].iloc[0],
                        answers=g["answers"].iloc[0], on_list=bool(g["on_list"].any()),
                        counted=bool(g["counted"].iloc[0] and g["on_list"].any()),
                        columns=len(cols), column_names=" ".join(cols),
                        aircraft_answering=int(ans[key].sum()) if key in ans else 0,
                        share_answering=float(ans[key].mean()) if key in ans else 0.0))
    return pd.DataFrame(out)


def answered(ds: Dataset, reg: Optional[pd.DataFrame] = None,
             m: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Aircraft x question: True where any column of the question holds a value."""
    reg = load() if reg is None else reg
    m = mapping(ds, reg) if m is None else m
    v = ds.variants
    out = {}
    for key, g in reg.groupby(KEY, sort=False):
        hit = pd.Series(False, index=v.index)
        for i, r in g.iterrows():
            cols = list(m.loc[m["row"].eq(i), "column"])
            if cols:
                hit |= v[cols].notna().any(axis=1) & _when(v, r["when"])
        out[key] = hit
    return pd.DataFrame(out)


def counted_keys(reg: Optional[pd.DataFrame] = None) -> List[tuple]:
    reg = load() if reg is None else reg
    g = reg.groupby(KEY, sort=False).agg(kind=("kind", "first"), on_list=("on_list", "any"))
    return [k for k, r in g.iterrows() if r["on_list"] and r["kind"] in COUNTED_KINDS]


def per_aircraft(ds: Dataset, reg: Optional[pd.DataFrame] = None) -> pd.Series:
    """How many of the counted questions each aircraft answers (one value per variant)."""
    reg = load() if reg is None else reg
    return answered(ds, reg)[counted_keys(reg)].sum(axis=1)


def column_kind(ds: Dataset, reg: Optional[pd.DataFrame] = None) -> pd.Series:
    """The kind of question each coded export column answers; 'off the cards' when not on the list."""
    m = mapping(ds, reg)
    m = m.assign(label=m["kind"].where(m["on_list"], "off the cards"),
                 rank=(~m["counted"]).astype(int))
    return m.sort_values("rank").drop_duplicates("column").set_index("column")["label"]


def by_card(ds: Dataset, reg: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Questions per card and kind, and the export columns the questions fill."""
    reg = load() if reg is None else reg
    q = questions(ds, reg)
    m = mapping(ds, reg)
    counted_rows = reg.index[reg["counted"]]
    rows = []
    for card in CARDS + ("all",):
        qc = q[q["counted"] & (q["card"].eq(card) if card != "all" else True)]
        kinds = qc["kind"].value_counts()
        mc = m[m["row"].isin(counted_rows) & (m["card"].eq(card) if card != "all" else True)]
        beside = q[q["on_list"] & ~q["counted"] & (q["card"].eq(card) if card != "all" else True)]
        rows.append({"card": card, "dimensions": int(kinds.get("Dimension", 0)),
                     "ticks": int(kinds.get("Tick", 0)), "numbers": int(kinds.get("Number", 0)),
                     "questions": len(qc), "export columns": mc["column"].nunique(),
                     "tags and escapes beside them": len(beside)})
    return pd.DataFrame(rows)
