"""The aviation-patenting baseline of the Labelling Analysis.

2.1.1 counts eVTOL filings per priority year. That count on its own cannot say whether the
sector became more active: if patenting rose everywhere, eVTOL filings would rise with it
and the graph would look the same. This module divides the corpus by a baseline of all
aeronautics patenting -- classification B64 (aircraft, aviation, cosmonautics), counted by
the same priority year -- so the document can report eVTOL as a share of aviation patenting
and not only as a raw count (user, 2026-09-22).

The series is stored, never fetched at render time:
``assets/external/aviation_baseline/b64_by_priority_year.csv`` holds one row per year and
one column per query, and the README beside it gives the exact WIPO PATENTSCOPE query, the
date fetched and the limits. ``scripts/fetch_aviation_baseline.py`` rebuilds the CSV.

Three traps this module does not hide, and how each is handled:

* **Unit.** The corpus counts *unique aircraft* by priority year; the baseline counts
  *patent publications* by priority year. Those are not the same unit, so the module also
  carries the corpus's own patent count (all 1 639 acquired patents by priority year). The
  patents-per-B64 ratio is the like-for-like one and is the series the document reads; the
  aircraft ratio is printed beside it and is a mix of two units.
* **Incomplete years.** Both sides are priority-year counts truncated by publication lag,
  so both fall away at the right edge. The truncation partly cancels in the ratio, but only
  as far as eVTOL and aviation share a lag distribution, which is not established. Every
  year inside the 90th-percentile lag stays marked incomplete and the ratio is not read there.
* **Office coverage.** The corpus is a multi-office PatSeer set. The baseline the document
  reads is restricted to the same nine publication offices (:data:`CORPUS_OFFICES`); the
  worldwide series is kept in the CSV as a robustness check.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ASSETS = Path(__file__).resolve().parents[2] / "assets"
BASE_DIR = ASSETS / "external" / "aviation_baseline"
BASE_FILE = BASE_DIR / "b64_by_priority_year.csv"

#: publication offices of the corpus (Table A.1 provenance), used to restrict the baseline
CORPUS_OFFICES: List[str] = ["US", "CN", "DE", "WO", "EP", "KR", "FR", "GB", "IT"]

#: the stored column the document reads. ``cpc_offices`` = CPC B64, the nine corpus offices.
PRIMARY = "cpc_offices"
#: the same query worldwide, and the IPC readings of both, kept as robustness checks
ALTERNATES: List[str] = ["cpc_world", "ipc_offices", "ipc_world"]

#: index base. A single year is too small a denominator (2005 holds 9 aircraft), so the
#: index is taken against the mean of a five-year base window.
BASE_YEARS: Tuple[int, int] = (2005, 2009)

#: printed under Figure 2.1.1 and in the README
SOURCE = ("aviation baseline: WIPO PATENTSCOPE, query CPC:B64* AND PD:<year> restricted to the "
          "nine publication offices of the corpus (US, CN, DE, WO, EP, KR, FR, GB, IT), fetched "
          "2026-09-22; stored in assets/external/aviation_baseline")

COLS = {
    "base": "B64 patents (same offices)",
    "air_ratio": "aircraft per 1 000 B64",
    "pat_ratio": "patents per 1 000 B64",
    "evtol_ix": "eVTOL index (2005-09 = 100)",
    "avia_ix": "aviation index (2005-09 = 100)",
}


def available() -> bool:
    """True when the stored baseline exists, so a render can fall back to the raw counts."""
    return BASE_FILE.exists()


def load() -> pd.DataFrame:
    """The stored baseline, one row per year, indexed by year."""
    if not available():
        raise FileNotFoundError(
            f"aviation baseline not installed: {BASE_FILE}. Run scripts/fetch_aviation_baseline.py, "
            f"or drop a PatSeer export there with the columns the README names.")
    b = pd.read_csv(BASE_FILE)
    b["year"] = pd.to_numeric(b["year"], errors="coerce").astype("Int64")
    return b.dropna(subset=["year"]).set_index(b["year"].astype(int)).drop(columns=["year"])


def series(column: str = PRIMARY) -> pd.Series:
    """One baseline column as a year-indexed integer series."""
    return pd.to_numeric(load()[column], errors="coerce")


def _index(s: pd.Series, base_years: Tuple[int, int] = BASE_YEARS) -> pd.Series:
    """``s`` rescaled so the mean of the base window is 100."""
    lo, hi = base_years
    base = s.reindex(range(lo, hi + 1)).mean()
    if not base or not np.isfinite(base):
        return pd.Series(np.nan, index=s.index, dtype=float)
    return s / base * 100.0


def attach(tab: pd.DataFrame, column: str = PRIMARY,
           base_years: Tuple[int, int] = BASE_YEARS) -> pd.DataFrame:
    """Add the baseline and the normalised readings to the 2.1.1 table.

    ``tab`` is :func:`la_tables.filings_per_year` before ``reset_index``: indexed by priority
    year, carrying ``unique aircraft`` and ``patents acquired``. Returns the same frame with
    :data:`COLS` appended. If the baseline is not installed the frame comes back untouched,
    so the document still renders its raw counts.
    """
    if not available():
        tab.attrs["baseline"] = None
        return tab
    b = series(column).reindex(tab.index)
    out = tab.copy()
    out[COLS["base"]] = b.astype("Int64")
    with np.errstate(divide="ignore", invalid="ignore"):
        out[COLS["air_ratio"]] = (out["unique aircraft"] / b * 1000).round(2)
        out[COLS["pat_ratio"]] = (out["patents acquired"] / b * 1000).round(2)
    out[COLS["evtol_ix"]] = _index(out["patents acquired"].astype(float), base_years).round(0)
    out[COLS["avia_ix"]] = _index(b.astype(float), base_years).round(0)
    out.attrs.update(tab.attrs)
    out.attrs["baseline"] = column
    out.attrs["baseline_source"] = SOURCE
    out.attrs["base_years"] = base_years
    return out


#: columns of the 2.1.1 table that are flags or elapsed time, never counts
_NOT_COUNTS = ("years since year end", "complete")


def pool_to_first(tab: pd.DataFrame, first: int) -> pd.DataFrame:
    """Everything before ``first`` summed into the ``first`` row, for a chart of totals.

    Figure 2.1.1's bars are totals, so they can pool the thin early years into one "≤ first"
    bar and stop hiding them: before this, the figure filtered those years away while its tick
    still said "≤2005" (author's ruling 2026-09-23). Table 2.1.1 keeps every year as its own row.

    A **per-year index cannot pool** -- a seven-year bucket is not a year, and the two sides do
    not pool by the same factor, so an index built on a pooled bucket would compare a multi-year
    total on one side with a multi-year total on the other and call the result a rate. The index
    columns are therefore dropped here and the normalised panel is drawn from the unpooled frame.

    Counts are summed, **the baseline among them**, so a ratio taken on the pooled row still
    divides a pooled numerator by a pooled denominator. The two ratio columns are recomputed
    from those sums rather than averaged over the rows.
    """
    rate_cols = (COLS["air_ratio"], COLS["pat_ratio"], COLS["evtol_ix"], COLS["avia_ix"])
    out = tab[tab.index >= first].copy()
    pre = tab[tab.index < first]
    out.attrs.update(tab.attrs)
    out.attrs["pooled_years"] = (int(pre.index.min()), int(pre.index.max())) if len(pre) else None
    if len(pre):
        counts = [c for c in out.columns
                  if c not in _NOT_COUNTS and c not in rate_cols and pd.api.types.is_numeric_dtype(out[c])]
        for c in counts:
            out.loc[first, c] = out.loc[first, c] + pd.to_numeric(pre[c], errors="coerce").sum()
    if COLS["base"] in out.columns:
        b = pd.to_numeric(out[COLS["base"]], errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            out[COLS["air_ratio"]] = (out["unique aircraft"] / b * 1000).round(2)
            out[COLS["pat_ratio"]] = (out["patents acquired"] / b * 1000).round(2)
    return out.drop(columns=[c for c in (COLS["evtol_ix"], COLS["avia_ix"]) if c in out.columns])


def readings(tab: pd.DataFrame) -> Dict[str, object]:
    """The facts 2.1.1 states in prose, all recomputed from ``tab``.

    Keys: ``first_above`` (first complete year from which eVTOL stays above the aviation
    index), ``ratio_start`` / ``ratio_end`` (patents per 1 000 B64 in the base window and in
    the last complete year), ``growth`` (how many times faster eVTOL grew), ``last_complete``.
    """
    if COLS["pat_ratio"] not in tab.columns:
        return {}
    t = tab[tab.index >= BASE_YEARS[0]]
    comp = t[t["complete"].astype(bool)]
    if not len(comp):
        return {}
    last = int(comp.index.max())
    lo, hi = BASE_YEARS
    base_ratio = float(t.reindex(range(lo, hi + 1))[COLS["pat_ratio"]].mean())
    end_ratio = float(comp.loc[last, COLS["pat_ratio"]])
    gap = comp[COLS["evtol_ix"]] - comp[COLS["avia_ix"]]
    above = gap[gap > 0]
    first_above = None
    if len(above):
        # the first year from which the eVTOL index never falls back to the aviation index
        for y in above.index:
            if bool((gap.loc[y:] > 0).all()):
                first_above = int(y)
                break
    return {
        "first_above": first_above,
        "ratio_start": round(base_ratio, 2),
        "ratio_end": round(end_ratio, 2),
        "ratio_multiple": round(end_ratio / base_ratio, 1) if base_ratio else None,
        "evtol_index_end": float(comp.loc[last, COLS["evtol_ix"]]),
        "aviation_index_end": float(comp.loc[last, COLS["avia_ix"]]),
        "growth": (round(float(comp.loc[last, COLS["evtol_ix"]]) / float(comp.loc[last, COLS["avia_ix"]]), 1)
                   if comp.loc[last, COLS["avia_ix"]] else None),
        "last_complete": last,
        "base_years": BASE_YEARS,
    }


def check(tab: pd.DataFrame) -> pd.DataFrame:
    """The same normalisation under each stored baseline column, so the choice can be shown
    not to drive the answer. One row per column: its index in the last complete year and the
    eVTOL-to-aviation growth multiple."""
    rows = []
    for col in [PRIMARY] + ALTERNATES:
        try:
            r = readings(attach(tab, col))
        except Exception:
            continue
        if r:
            rows.append({"baseline": col, "first year eVTOL pulls ahead": r["first_above"],
                         "aviation index, last complete year": r["aviation_index_end"],
                         "eVTOL index, last complete year": r["evtol_index_end"],
                         "eVTOL grows this many times faster": r["growth"]})
    return pd.DataFrame(rows)
