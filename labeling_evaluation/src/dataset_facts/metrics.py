"""The statistics Part A quotes, and the codebook id -> display name map.

Every count in the document is a plain frequency; the two derived numbers are

* **effective number of answers** — Hill number of order 1, ``exp(Shannon)``:
  how many equally common answers would produce the same spread. A field with
  12 answers whose largest holds 28 % has an effective number of 7.1, a field
  with 6 answers whose largest holds 88 % has 1.6.
* **Cohen's kappa** — agreement corrected for the agreement two independent
  readings would reach by chance alone.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd

# The short architecture names used in the document's tables. The full codebook
# strings ("Independent Thrust - Lift + Cruise (SLC)") come from
# data_dictionary.csv via :func:`option_names`.
ARCH_NAMES: Dict[str, str] = {
    "SLC": "Lift + Cruise",
    "TR": "Tilt Rotor",
    "CVT": "Combined vectored thrust",
    "TW": "Tilt Wing",
    "MR": "Multirotor",
    "TB": "Tilt Body",
    "PTC": "Pitch-to-Cruise",
    "HB": "Hoverbike",
    "DS": "Deflected Slipstream",
    "PFV": "Personal Flying Vehicle",
    "SRW": "Stopped/Slowed Rotor Wing",
    "RC": "Rotorcraft",
}


# --------------------------------------------------------------------------
# spread
# --------------------------------------------------------------------------
def effective_number(series: pd.Series) -> float:
    """Hill number of order 1 (``exp`` of the Shannon entropy) over non-null values."""
    p = series.dropna().value_counts(normalize=True)
    if p.empty:
        return float("nan")
    return float(np.exp(-(p * np.log(p)).sum()))


def top_share(series: pd.Series) -> float:
    """Share of the most common non-null answer."""
    p = series.dropna().value_counts(normalize=True)
    return float(p.iloc[0]) if len(p) else float("nan")


def field_profile(frame: pd.DataFrame, column: str, section: str = "") -> Dict:
    """One row of the A.2 D2 ranking: answered, distinct answers, top share, effK."""
    s = frame[column]
    return {
        "field": column,
        "card": section,
        "answered": int(s.notna().sum()),
        "answers": int(s.nunique(dropna=True)),
        "top_share": round(top_share(s), 2),
        # kept unrounded: the informative/near-constant cut-offs are applied to it
        "effective_answers": effective_number(s),
    }


def share_table(
    series: pd.Series, names: Optional[Dict[str, str]] = None, total: Optional[int] = None
) -> pd.DataFrame:
    """Counts and shares of a categorical column, most common first."""
    counts = series.dropna().value_counts()
    denom = total if total is not None else counts.sum()
    out = pd.DataFrame(
        {
            "value": counts.index,
            "count": counts.to_numpy(),
            "share": (counts.to_numpy() / denom).round(2),
        }
    )
    if names:
        out.insert(0, "name", out["value"].map(names).fillna(out["value"]))
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------
# agreement
# --------------------------------------------------------------------------
def cohen_kappa(a: Iterable, b: Iterable) -> float:
    """Cohen's kappa between two label vectors, over the rows where both are set."""
    pairs = pd.DataFrame({"a": list(a), "b": list(b)}).dropna()
    if pairs.empty:
        return float("nan")
    n = len(pairs)
    observed = float((pairs["a"] == pairs["b"]).mean())
    pa = pairs["a"].value_counts(normalize=True)
    pb = pairs["b"].value_counts(normalize=True)
    expected = float(sum(pa.get(k, 0.0) * pb.get(k, 0.0) for k in set(pa.index) | set(pb.index)))
    if expected == 1.0:
        return float("nan")
    return (observed - expected) / (1.0 - expected)


def agreement(a: Iterable, b: Iterable) -> Dict[str, float]:
    """Raw agreement, kappa and n for two label vectors."""
    pairs = pd.DataFrame({"a": list(a), "b": list(b)}).dropna()
    return {
        "n": int(len(pairs)),
        "agreement": round(float((pairs["a"] == pairs["b"]).mean()), 3) if len(pairs) else float("nan"),
        "kappa": round(cohen_kappa(pairs["a"], pairs["b"]), 2) if len(pairs) else float("nan"),
    }


# --------------------------------------------------------------------------
# concentration
# --------------------------------------------------------------------------
def hhi(series: pd.Series) -> float:
    """Herfindahl-Hirschman index of a filer column: sum of squared shares."""
    p = series.dropna().value_counts(normalize=True)
    return float((p**2).sum())


def concentration(series: pd.Series, top_n: int = 10) -> Dict:
    """Distinct filers, singletons, top-n share, HHI and the largest filer."""
    counts = series.dropna().value_counts()
    total = int(counts.sum())
    return {
        "distinct": int(len(counts)),
        "singletons": int((counts == 1).sum()),
        f"top{top_n}_share": round(float(counts.head(top_n).sum() / total), 2) if total else float("nan"),
        "hhi": round(hhi(series), 3),
        "largest": f"{counts.index[0]}, {int(counts.iloc[0])}" if len(counts) else "",
    }


# --------------------------------------------------------------------------
# codebook display names
# --------------------------------------------------------------------------
def option_names(data_dictionary: pd.DataFrame, column: str) -> Dict[str, str]:
    """``{option id: display name}`` for one coded column, from data_dictionary.csv."""
    row = data_dictionary.loc[data_dictionary["column"] == column, "options"]
    if row.empty or not isinstance(row.iloc[0], str):
        return {}
    out = {}
    for part in row.iloc[0].split("|"):
        if "=" in part:
            key, name = part.split("=", 1)
            out[key.strip()] = name.strip()
    return out


def top_k_share(series: pd.Series, k: int) -> float:
    """Cumulative share of the ``k`` most common non-null answers."""
    p = series.dropna().value_counts(normalize=True)
    return float(p.head(k).sum()) if len(p) else float("nan")
