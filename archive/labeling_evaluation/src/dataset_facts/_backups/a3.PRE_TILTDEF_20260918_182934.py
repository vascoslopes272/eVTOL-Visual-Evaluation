"""A.3 — what the fine labels are for: the derived layer (step D2b of the checklist).

The 283 columns are slots, not concepts. Collapsing the repeats leaves the
concepts of :func:`a2.concept_of`, and about twenty of those vary enough to
separate designs on their own. The rest fall into three groups:

1. **structurally sparse slots** — absent because most aircraft do not have the
   part. Used aggregated per aircraft, which is what :func:`derived_layer`
   builds; those columns enter the Gower distance exactly like a wizard field.
2. **near-constant fields** — findings, not waste (:func:`a2.d2_near_constant_fields`).
3. **the three-field archetype** — limits only the counting metrics.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from . import metrics
from .a2 import PROPULSOR_UNIT_COLUMNS, answerable_slots, concept_of
from .loaders import Dataset


def slot_groups(ds: Dataset) -> pd.DataFrame:
    """Slots per concept — the repeats that make 283 columns out of ~73 questions."""
    slots = answerable_slots(ds)
    frame = pd.DataFrame({"slot": slots, "concept": [concept_of(s) for s in slots]})
    grouped = frame.groupby("concept").agg(
        slots=("slot", "size"), examples=("slot", lambda s: " · ".join(sorted(s)[:3]))
    )
    return grouped.sort_values("slots", ascending=False).reset_index()


def derived_layer(ds: Dataset) -> pd.DataFrame:
    """One row per aircraft: the sparse slots aggregated into design variables.

    These are the columns the distance and the coupling analysis use in place of
    the per-slot detail. Every one is a fact about the aircraft, not about a slot.
    """
    v = ds.variants
    kin = [c for c in v.columns if c.endswith("_propKin")]
    bmech = [c for c in v.columns if c.endswith("_bmech")]
    orient = [c for c in v.columns if c.endswith("_orient") and not c.startswith("boom")]
    counts = [c for c in PROPULSOR_UNIT_COLUMNS if c in v.columns]

    ducted = v[bmech].eq("Ducted").any(axis=1)
    open_ = v[bmech].eq("Open").any(axis=1)
    tilting = v[kin].eq("Tilt").any(axis=1)
    fixed = v[kin].eq("Fixed").any(axis=1)

    out = pd.DataFrame({
        "patent_id": v["patent_id"].to_numpy(),
        "variant": v["variant"].to_numpy(),
        "propulsor_units": v[counts].apply(pd.to_numeric, errors="coerce")
                            .fillna(0).sum(axis=1).to_numpy(),
        "any_tilting_unit": tilting.to_numpy(),
        "mixes_fixed_and_tilting": (tilting & fixed).to_numpy(),
        "any_ducted_unit": ducted.to_numpy(),
        "all_units_ducted": (ducted & ~open_).to_numpy(),
        "thrust_axis_mix": (v[orient].notna().sum(axis=1) > 1).to_numpy(),
        "propulsor_carriers": v[counts].apply(pd.to_numeric, errors="coerce")
                               .gt(0).sum(axis=1).to_numpy(),
        "units_on_the_wing_span": v.get("wing1_zoneSpan", pd.Series(index=v.index)).to_numpy(),
        "units_on_the_wing_chord": v.get("wing1_zoneChord", pd.Series(index=v.index)).to_numpy(),
    })
    return out


def derived_layer_summary(ds: Dataset) -> pd.DataFrame:
    """The derived variables as the document states them."""
    d = derived_layer(ds)
    units = d["propulsor_units"]
    rows = [
        ("Total propulsor units, median", f"{units.median():.0f}"),
        ("Total propulsor units, quartiles",
         f"{units.quantile(0.25):.0f}-{units.quantile(0.75):.0f}"),
        ("Aircraft with more than 8 propulsor units", int((units > 8).sum())),
        ("Aircraft with any tilting unit", int(d["any_tilting_unit"].sum())),
        ("Aircraft mixing fixed and tilting units", int(d["mixes_fixed_and_tilting"].sum())),
        ("Aircraft with any ducted unit", int(d["any_ducted_unit"].sum())),
        ("Aircraft whose units are all ducted", int(d["all_units_ducted"].sum())),
    ]
    return pd.DataFrame(rows, columns=["derived variable", "value"])


def concept_count(ds: Dataset) -> Dict[str, int]:
    """Slots, concepts and the informative subset, in one dict."""
    from .a2 import d2_informative_fields

    slots = answerable_slots(ds)
    return {
        "slots": len(slots),
        "concepts": len({concept_of(s) for s in slots}),
        "informative_fields": int(len(d2_informative_fields(ds))),
        "derived_variables": int(derived_layer(ds).shape[1] - 2),
    }
