"""Aircraft changes made in the wizard AFTER the image labels were frozen (2026-09-15), shared by
build_architecture_review_page.py and apply_architecture_review.py so both see the same aircraft list.

- DROPPED      aircraft that no longer exist (merged away)
- RENAMED_IN   aircraft renumbered in the wizard: old id -> new id, applied to the frozen labels and the readings
- RENAMED_OUT  id written to the final file (a patent reduced to one aircraft is keyed by the bare patent id)
- REPLACED     patents whose single frozen row is replaced by per-aircraft rows
- ADDED        text readings of aircraft that did not exist at the freeze
- POSTFREEZE   the wizard label of those aircraft (made after the freeze; never part of the frozen comparison)
"""
from pathlib import Path
import pandas as pd

TA = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED/text_architecture")
DROPPED = {"US2023257132A1_arch2": "merged into one aircraft in the wizard 2026-09-16"}
RENAMED_IN = {"US2024002048A1_arch2": "US2024002048A1_arch3", "US2024002048A1_arch3": "US2024002048A1_arch4"}
RENAMED_OUT = {"US2023257132A1_arch1": "US2023257132A1", "US11787551B1_arch1": "US11787551B1"}
REPLACED = {"US2022388648A1"}
ADDED = TA / "variant_reading" / "architecture_text_variants_added_20260916.csv"
POSTFREEZE = TA / "image_labels_postfreeze_20260916.csv"
# patents that were not among the 695 read on 2026-09-09 (page metadata)
NEW_PATENTS = {"US11787551B1": dict(bucket="0_added", image_label="CVT", text_label="CVT", confidence="H", quote="", note="",
                                    company_canonical="Archer Aviation", aircraft_name_final="Midnight", priority_year=2022,
                                    title="Vertical takeoff and landing aircraft electric engine configuration",
                                    assignee="ARCHER AVIATION INC (US)", n_var=1, main_figure="", your_decision="", comment="")}


def frozen_labels() -> pd.DataFrame:
    """variant_id, patent_id, image_label_frozen (+ post_freeze flag) for the aircraft that exist now."""
    p = pd.read_csv(TA / "image_labels_frozen_20260915.csv", dtype=str, keep_default_na=False)
    p = p[~p.variant_id.isin(DROPPED) & ~(p.variant_id.isin(REPLACED))].copy()
    p["variant_id"] = p["variant_id"].replace(RENAMED_IN)
    p["post_freeze"] = False
    a = pd.read_csv(POSTFREEZE, dtype=str, keep_default_na=False)[["variant_id", "patent_id", "image_label_frozen"]]
    a["post_freeze"] = True
    out = pd.concat([p, a], ignore_index=True)
    assert not out.variant_id.duplicated().any(), out[out.variant_id.duplicated()].variant_id.tolist()
    return out


def readings(frames) -> pd.DataFrame:
    """Per-aircraft readings with the renumbering applied and the added aircraft appended."""
    v = pd.concat(list(frames), ignore_index=True)
    v = v[~v.variant_id.isin(DROPPED)].copy()
    v["variant_id"] = v["variant_id"].replace(RENAMED_IN)
    v = pd.concat([v, pd.read_csv(ADDED)], ignore_index=True)
    if "basis" in v.columns:
        v["basis"] = v["basis"].fillna("aircraft")
    assert not v.variant_id.duplicated().any(), v[v.variant_id.duplicated()].variant_id.tolist()
    return v
