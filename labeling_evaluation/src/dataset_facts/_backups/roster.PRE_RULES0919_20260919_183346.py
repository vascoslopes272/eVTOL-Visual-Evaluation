"""The roster: every aircraft that enters the analysis, with its sensitivity flags.

This is the output of index section 1.4 — the "fixed dataset" every later chapter
works on. One row per primary approved variant; nothing is dropped, every flag is
a column, and each downstream analysis is run with and without the flagged rows.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from . import a2
from .loaders import Dataset

#: the flags, in the order the summary prints them
#: readability ("Impossible") is deliberately NOT a flag here: every flag in the
#: preliminary analysis is about evidence and labelling, not about what a model
#: can read. The column stays in the roster for the DINOv2 chapter.
FLAGS = {
    "single_figure": "rests on one approved figure",
    "quality_flagged": "a figure of the patent is flagged partial or poor",
    "in_sensitivity_set": "either of the two above (the thin-evidence flag)",
    "notPureArch": "mixed architecture",
    "g1_uncertain": "annotator unsure at G1",
    "m1_uncertain": "annotator unsure at M1",
    "m2_uncertain": "annotator unsure at M2",
    "t1_uncertain": "annotator unsure at T1",
    "quickOverride": "quick count override (no architecture type by design)",
    "d3_duplicate": "S3 - a similar aircraft, relabelled in full",
    "d3_identical_to_root": "S3 identical to its original on all seven archetype fields",
    "window_partial": "priority year in the truncated window",
    "any_flag": "any flag at all",
}


def analysis_set(ds: Dataset, partial_window_start: int = 2024) -> pd.DataFrame:
    """One row per aircraft in the analysis set, with identity columns and every flag."""
    v = ds.variants
    ident = ds.identity.set_index("patent_id")
    n_fig = pd.to_numeric(v["n_approved_this_variant"], errors="coerce").fillna(0)

    flagged = ds.approved_figures["qualityFlag"].fillna("clean").ne("clean")
    flagged_patents = set(ds.approved_figures.loc[flagged, "patent_id"])
    d3 = a2.d7_d3_rows(ds)
    d3_identical = set(
        zip(d3.loc[d3["identical_on_archetype_fields"].fillna(False), "patent_id"],
            d3.loc[d3["identical_on_archetype_fields"].fillna(False), "variant"])
    )
    year = pd.to_numeric(ident.reindex(v["patent_id"])["priority_year"], errors="coerce")

    def flag(col: str) -> pd.Series:
        if col not in v.columns:
            return pd.Series(False, index=v.index)
        return v[col].map(lambda x: str(x) == "True").astype(bool)

    out = pd.DataFrame({
        "patent_id": v["patent_id"].to_numpy(),
        "variant": v["variant"].to_numpy(),
        "topType": v["topType"].to_numpy(),
        "dup_type": v["dup_type"].to_numpy(),
        "priority_year": year.to_numpy(),
        "region": ident.reindex(v["patent_id"])["region"].to_numpy(),
        "company_canonical": ident.reindex(v["patent_id"])["company_canonical"].to_numpy(),
        "approved_figures": n_fig.astype(int).to_numpy(),
        "single_figure": n_fig.eq(1).to_numpy(dtype=bool),
        "quality_flagged": v["patent_id"].isin(flagged_patents).to_numpy(),
        "readability_impossible": v["dinoUnderstanding"].astype(str).eq("Impossible").to_numpy(),
        "notPureArch": flag("notPureArch").to_numpy(),
        "g1_uncertain": flag("g1_humanUncertain").to_numpy(),
        "m1_uncertain": flag("m1_humanUncertain").to_numpy(),
        "m2_uncertain": flag("m2_humanUncertain").to_numpy(),
        "t1_uncertain": flag("t1_humanUncertain").to_numpy(),
        "quickOverride": flag("g1_quickOverride").to_numpy(),
        "d3_duplicate": v["dup_type"].eq(3).fillna(False).to_numpy(dtype=bool),
        "d3_identical_to_root": [
            (p, s) in d3_identical for p, s in zip(v["patent_id"], v["variant"])
        ],
        "window_partial": (year >= partial_window_start).fillna(False).to_numpy(),
    })
    out["in_sensitivity_set"] = out["single_figure"] | out["quality_flagged"]
    flag_cols = [c for c in FLAGS if c not in ("any_flag",)]
    for c in flag_cols:
        out[c] = out[c].astype(bool)
    out["any_flag"] = out[flag_cols].any(axis=1)
    return out


def summary(roster: pd.DataFrame) -> pd.DataFrame:
    """Rows carrying each flag, with the plain-English meaning."""
    rows = [{"flag": col, "meaning": meaning, "unique aircraft": int(roster[col].sum()),
             "share": round(float(roster[col].mean()), 3)}
            for col, meaning in FLAGS.items()]
    return pd.DataFrame(rows)


def counts(roster: pd.DataFrame) -> Dict[str, int]:
    """The headline: how many enter, how many are clean of every flag."""
    return {
        "aircraft_entering": int(len(roster)),
        "patents": int(roster["patent_id"].nunique()),
        "without_any_flag": int((~roster["any_flag"]).sum()),
        "in_sensitivity_set": int(roster["in_sensitivity_set"].sum()),
    }
