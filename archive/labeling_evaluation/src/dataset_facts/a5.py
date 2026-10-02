"""A.5 — aircraft names as they stand.

No name in the corpus was verified programmatically against the patent's own
content: the gazetteer names are an attribution rule, the SBERT names are a text
hit. The name is a stratum variable and the basis of the flagship check; it is
never a design variable.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from . import metrics
from .loaders import Dataset


def name_proposals(ds: Dataset) -> pd.DataFrame:
    """Where the name proposals come from, and whether the patent's text says it."""
    i = ds.identity
    out = metrics.share_table(i["aircraft_name_source"])
    in_text = i.groupby("aircraft_name_source")["aircraft_name_in_text"].value_counts()
    out["name appears in the patent's own text"] = out["value"].map(
        lambda src: " · ".join(f"{k} {v}" for k, v in in_text.get(src, {}).items())
    )
    out.attrs["proposals"] = int(i["aircraft_name"].notna().sum())
    out.attrs["no_proposal"] = int(i["aircraft_name"].isna().sum())
    return out


def gazetteer_by_company(ds: Dataset, top: int = 12) -> pd.DataFrame:
    """The companies the gazetteer stamps, biggest first.

    A company-attributed name says nothing about which embodiment a patent shows
    (A.4: the Bell "APT" patents carry six image types), so accepting a company's
    attribution is a statement about the assignee, not about the drawing.
    """
    i = ds.identity
    gaz = i[i["aircraft_name_source"] == "gazetteer"]
    g = gaz.groupby(["company_canonical", "aircraft_name"]).size()
    out = g.reset_index(name="patents").sort_values("patents", ascending=False)
    out.attrs["companies"] = int(gaz["company_canonical"].nunique())
    out.attrs["patents"] = int(len(gaz))
    return out.head(top).reset_index(drop=True)


def sbert_name_hits(ds: Dataset, top: int = 15) -> pd.DataFrame:
    """The name-like tokens SBERT picked out of the text.

    These are prior-art aircraft mentioned in the description (V-22, XV-3, CL-84,
    Yak-38 ...), not the aircraft depicted; the recommendation is to clear all of
    them.
    """
    i = ds.identity
    hits = i[i["aircraft_name_source"] == "sbert"]
    counts = hits["aircraft_name"].value_counts()
    out = pd.DataFrame({"token": counts.index, "patents": counts.to_numpy()})
    out.attrs["rows"] = int(len(hits))
    return out.head(top)


def link_flag(ds: Dataset) -> pd.DataFrame:
    """``aircraft_link`` crossed with the source of the name.

    The guardrail of Part D, 8 rests on the 36 gazetteer rows: the five SBERT
    "Depicted" rows are prior-art mentions.
    """
    i = ds.identity
    return (
        i.groupby(["aircraft_link", "aircraft_name_source"])
        .size()
        .reset_index(name="patents")
    )


def review_sets(ds: Dataset) -> pd.DataFrame:
    """What the NAME_REVIEW workbook asks the annotator to decide."""
    i = ds.identity
    gaz = i[i["aircraft_name_source"] == "gazetteer"]
    queue = i[i["name_review"].fillna(False).astype(bool)] if "name_review" in i else i.iloc[0:0]
    queue_src = queue["aircraft_name_source"].fillna("(no name)").value_counts()
    rows = [
        ("SBERT text hits", int((i["aircraft_name_source"] == "sbert").sum()),
         "keep / clear; recommendation: clear all of them"),
        ("Company-attributed, per company", int(gaz["company_canonical"].nunique()),
         f"accept the attribution rule for the company, review its "
         f"{len(gaz)} patents one by one, or clear"),
        ("03a name queue", int(len(queue)),
         " · ".join(f"{k} {v}" for k, v in queue_src.items())),
    ]
    return pd.DataFrame(rows, columns=["set", "rows", "decision"])
