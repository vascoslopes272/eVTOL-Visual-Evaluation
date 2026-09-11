"""A.6 — the identity variables: what the patents themselves say.

A.4 established the principle that a label is defensible when it rests on a
sentence of the patent, confirmed by the annotator. Applied to the identity
variables it found a real hole in the electric gate: the powertrain of 218 of the
695 analysis patents rested on a company gazetteer or on a corpus-wide
presumption rather than on the patent's own words.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from . import metrics
from .loaders import Dataset

#: the powertrain category the reading added, which the keyword pass cannot
#: express: the patent offers several powertrains as interchangeable options and
#: commits to none. A keyword classifier reads such a sentence as evidence of
#: "electric"; it is evidence of nothing.
ALTERNATIVES = "Alternatives"
NOT_STATED = "NotStated"


def _analysis_identity(ds: Dataset) -> pd.DataFrame:
    return ds.identity[ds.identity["patent_id"].isin(ds.patents_analysis["patent_id"])]


def evidence_per_variable(ds: Dataset) -> pd.DataFrame:
    """How many of the analysis patents carry a citation for each identity variable."""
    a = _analysis_identity(ds)
    rows = []
    for name, col in [("take-off mode", "takeoff_quote"),
                      ("powertrain", "powertrain_quote"),
                      ("UAV hint", "uav_quote"),
                      ("aircraft name", "aircraft_name_quote")]:
        if col not in a.columns:
            continue
        rows.append({
            "variable": name,
            "with a citation": int(a[col].notna().sum()),
            "of": int(len(a)),
            "without": int(a[col].isna().sum()),
        })
    return pd.DataFrame(rows)


def powertrain_without_evidence(ds: Dataset) -> pd.DataFrame:
    """What the patents with no powertrain citation rest on instead.

    Since electric is an *inclusion gate*, these are the weakest point in the
    dataset.
    """
    a = _analysis_identity(ds)
    missing = a[a["powertrain_quote"].isna()]
    return metrics.share_table(missing["is_electric_source"].fillna("(none)"))


def reading_outcome(ds: Dataset) -> pd.DataFrame:
    """The result on the patents read from text only."""
    if ds.text_identity is None:
        raise FileNotFoundError("text_identity/results.csv is missing")
    r = ds.text_identity
    settles = ~r["powertrain"].isin([NOT_STATED, ALTERNATIVES])
    cmp_ = ds.text_identity_cmp
    confirms = contradicts = None
    if cmp_ is not None:
        decided = cmp_[cmp_["text_electric"].ne("Unknown")]
        same = decided["text_electric"].eq(decided["is_electric"])
        confirms, contradicts = int(same.sum()), int((~same).sum())
    rows = [
        ("The text settles the powertrain", int(settles.sum()),
         "a citation now exists where none did"),
        ("- of which it confirms the 03a verdict", confirms, "the verdict was right"),
        ("- of which it contradicts the 03a verdict", contradicts,
         "listed by :func:`contradictions`"),
        ("The text never says what powers the aircraft", int((~settles).sum()),
         "a finding, not a gap"),
        (f"- of which {ALTERNATIVES} (several powertrains offered)",
         int(r["powertrain"].eq(ALTERNATIVES).sum()),
         "the patent commits to none"),
        ("- of which nothing at all", int(r["powertrain"].eq(NOT_STATED).sum()), ""),
    ]
    out = pd.DataFrame(rows, columns=["outcome", "patents", "meaning"])
    out.attrs["patents_read"] = int(len(r))
    return out


def powertrain_vocabulary(ds: Dataset) -> pd.DataFrame:
    """What the reading found, in the 03a powertrain vocabulary."""
    return metrics.share_table(ds.text_identity["powertrain"])


def contradictions(ds: Dataset) -> pd.DataFrame:
    """The patents counted as electric that are, by their own words, not electric.

    These are the rows that matter: electric is an inclusion gate, so a wrong
    value here decides whether a patent belongs in the corpus at all.
    """
    cmp_ = ds.text_identity_cmp
    if cmp_ is None:
        raise FileNotFoundError("text_identity/comparison_237.csv is missing")
    decided = cmp_[cmp_["text_electric"].ne("Unknown")]
    wrong = decided[decided["text_electric"].ne(decided["is_electric"])]
    cols = ["patent_id", "company_canonical", "is_electric", "is_electric_source",
            "text_electric", "powertrain_y", "pw_quote"]
    out = wrong[[c for c in cols if c in wrong.columns]].copy()
    out = out.rename(columns={"is_electric": "03a says", "text_electric": "the text says",
                              "powertrain_y": "powertrain read", "pw_quote": "citation"})
    return out.sort_values(["the text says", "03a says"]).reset_index(drop=True)


def contradiction_summary(ds: Dataset) -> pd.DataFrame:
    """The contradictions grouped: what 03a said against what the text says."""
    cmp_ = ds.text_identity_cmp
    decided = cmp_[cmp_["text_electric"].ne("Unknown")]
    wrong = decided[decided["text_electric"].ne(decided["is_electric"])]
    return (
        wrong.groupby(["is_electric", "text_electric"])
        .size()
        .reset_index(name="patents")
        .rename(columns={"is_electric": "03a says", "text_electric": "the text says"})
        .sort_values("patents", ascending=False)
        .reset_index(drop=True)
    )


def gazetteer_ambiguous_companies(ds: Dataset) -> pd.DataFrame:
    """Companies whose documented aircraft differ in powertrain.

    For their patents the filing-year window decides the powertrain of an
    inclusion gate. This is the same year-window problem as A.4, and it is the
    rule the pipeline should adopt: where a company's documented aircraft differ
    in a field, the gazetteer must not settle that field.
    """
    cmp_ = ds.text_identity_cmp
    if cmp_ is None:
        raise FileNotFoundError("text_identity/comparison_237.csv is missing")
    gaz = cmp_[cmp_["is_electric_source"] == "gazetteer"]
    g = gaz.groupby("company_canonical").agg(
        patents_read=("patent_id", "size"),
        readings=("powertrain_y", lambda s: " · ".join(
            f"{k} {v}" for k, v in s.value_counts().items()
        )),
        distinct_readings=("powertrain_y", "nunique"),
    )
    return g.sort_values("patents_read", ascending=False).reset_index()
