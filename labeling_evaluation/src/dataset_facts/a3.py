"""A.3 — what the fine labels are for: the derived layer (step D2b of the checklist).

The 283 columns are slots, not concepts. Collapsing the repeats leaves the
concepts of :func:`a2.concept_of`, and about twenty of those vary enough to
separate designs on their own. The rest fall into three groups:

1. **structurally sparse slots** — absent because most aircraft do not have the
   part. Used aggregated per aircraft, which is what :func:`derived_layer`
   builds; those columns enter the Gower distance exactly like a wizard field.
2. **near-constant fields** — findings, not waste (:func:`a2.d2_near_constant_fields`).
3. **the three-field archetype** — limits only the counting metrics.

Rulings of 2026-09-19 applied here: rule 1 (a value an override hides is not
determinable; it is left out and the number left out is reported), rule 3 (the boom
state comes from ``boom_thrust_state``) and rule 4 (where the analysis asks whether
the wing carries thrust, rotors on the wing card and on wing-attached booms both count
as wing-borne: the Gower distance uses the pooled pair ``wing_borne_thrust`` /
``wing_borne_units`` in place of the fields that depend on the boom-or-wing choice,
and :func:`boom_wing_sensitivity` reports what that changes).
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import metrics
from .a2 import (LEFT_OUT_HBPFV, LEFT_OUT_NONE, NO_M3_CARD, PROPULSOR_UNIT_COLUMNS,
                 answerable_slots, concept_of, left_out_summary, propulsion_states,
                 propulsor_units)
from .loaders import Dataset, override_sets


def slot_groups(ds: Dataset) -> pd.DataFrame:
    """Slots per concept — the repeats that make 283 columns out of ~73 questions."""
    slots = answerable_slots(ds)
    frame = pd.DataFrame({"slot": slots, "concept": [concept_of(s) for s in slots]})
    grouped = frame.groupby("concept").agg(
        slots=("slot", "size"), examples=("slot", lambda s: " · ".join(sorted(s)[:3]))
    )
    return grouped.sort_values("slots", ascending=False).reset_index()


#: wing_thrust_carrier values that count as wing-borne (rule 4)
WING_BORNE = ("wing", "wing_boom", "both")


def wing_borne_thrust(v: pd.DataFrame) -> pd.Series:
    """Rule 4, pooled: does the wing carry thrust? ``wing-borne`` (wing card, wing-attached
    boom, or both) / ``not wing-borne``. Blank on a wingless aircraft (the question does not
    arise), where an override leaves it not determinable, and on HB/PFV (no propulsor card)."""
    if "wing_thrust_carrier" not in v.columns:
        return pd.Series(pd.NA, index=v.index, dtype=object)
    c = v["wing_thrust_carrier"].astype(object)
    out = c.map(lambda x: "wing-borne" if x in WING_BORNE else "not wing-borne" if x == "none" else pd.NA)
    out[v["topType"].isin(["HB", "PFV"])] = pd.NA
    return out


def derived_layer(ds: Dataset) -> pd.DataFrame:
    """One row per aircraft: the sparse slots aggregated into design variables.

    These are the columns the distance and the coupling analysis use in place of
    the per-slot detail. Every one is a fact about the aircraft, not about a slot.
    Rule 1 (2026-09-19): a value that is not determinable is <NA>, never 0 or False —
    the units are notebook 04's ``propulsor_units`` (quick counts on count-only
    stations, blank for HB/PFV), the tilt and duct answers come from
    :func:`a2.propulsion_states`.
    """
    v = ds.variants
    orient = [c for c in v.columns if c.endswith("_orient") and not c.startswith("boom")]
    counts = [c for c in PROPULSOR_UNIT_COLUMNS if c in v.columns]
    st = propulsion_states(v)
    pu = propulsor_units(v)
    no_record = st["left_out"].isin([LEFT_OUT_HBPFV, LEFT_OUT_NONE])
    hidden_station = override_sets(v).map(lambda s: any(t.startswith("M3:") for t in s)).astype(bool)
    axis_mix = (v[orient].notna().sum(axis=1) > 1).astype("boolean")
    axis_mix = axis_mix.mask(no_record | (hidden_station & ~axis_mix.fillna(False)), pd.NA)

    out = pd.DataFrame({
        "patent_id": v["patent_id"].to_numpy(),
        "variant": v["variant"].to_numpy(),
        "propulsor_units": pu["units"].to_numpy(),
        "any_tilting_unit": st["any_tilting"].to_numpy(),
        "mixes_fixed_and_tilting": (st["any_tilting"] & st["any_fixed"]).to_numpy(),
        "any_ducted_unit": st["any_ducted"].to_numpy(),
        "all_units_ducted": st["all_ducted"].to_numpy(),
        "thrust_axis_mix": axis_mix.to_numpy(),
        "propulsor_carriers": v[counts].apply(pd.to_numeric, errors="coerce")
                               .gt(0).sum(axis=1).where(pu["units"].notna()).to_numpy(),
        "units_on_the_wing_span": v.get("wing1_zoneSpan", pd.Series(index=v.index)).to_numpy(),
        "units_on_the_wing_chord": v.get("wing1_zoneChord", pd.Series(index=v.index)).to_numpy(),
        "boom_thrust_state": v.get("boom_thrust_state", pd.Series(index=v.index)).to_numpy(),
        "wing_borne_thrust": wing_borne_thrust(v).to_numpy(),
        "wing_borne_units": pd.to_numeric(v.get("wing_borne_units", pd.Series(index=v.index)),
                                          errors="coerce").to_numpy(),
    })
    for c in ("any_tilting_unit", "mixes_fixed_and_tilting", "any_ducted_unit", "all_units_ducted",
              "thrust_axis_mix"):
        out[c] = out[c].astype("boolean")
    out.attrs["left_out"] = st["left_out"].to_numpy()
    out.attrs["units_left_out"] = pu["left_out"].to_numpy()
    return out


def derived_layer_summary(ds: Dataset) -> pd.DataFrame:
    """The derived variables as the document states them, each with the aircraft it is
    counted over (``of``) and the number left out as not determinable (rule 1)."""
    d = derived_layer(ds)
    n = len(d)
    units = d["propulsor_units"].dropna()
    left_units = n - len(units)

    def row(name, series, value=None):
        s = series.dropna()
        return (name, int(s.sum()) if value is None else value, int(len(s)), int(n - len(s)))

    wc = pd.to_numeric(ds.variants["wCount"], errors="coerce").to_numpy()
    winged = d["wing_borne_thrust"].notna()
    wing_left = int((((wc > 0) | np.isnan(wc)) & ~winged.to_numpy()).sum())   # winged, or wing count hidden
    rows = [
        ("Total propulsor units, median", f"{units.median():.0f}", len(units), left_units),
        ("Total propulsor units, quartiles",
         f"{units.quantile(0.25):.0f}-{units.quantile(0.75):.0f}", len(units), left_units),
        ("Aircraft with more than 8 propulsor units", int((units > 8).sum()), len(units), left_units),
        row("Aircraft with any tilting unit", d["any_tilting_unit"]),
        row("Aircraft mixing fixed and tilting units", d["mixes_fixed_and_tilting"]),
        row("Aircraft with any ducted unit", d["any_ducted_unit"]),
        row("Aircraft whose units are all ducted", d["all_units_ducted"]),
        ("Winged aircraft whose wing carries thrust (wing card or wing-attached boom)",
         int(d["wing_borne_thrust"].eq("wing-borne").sum()), int(winged.sum()), wing_left),
    ]
    out = pd.DataFrame(rows, columns=["derived variable", "value", "of", "left out"])
    out["left out"] = out["left out"].astype("Int64")
    out.attrs["units_left_out"] = left_out_summary(pd.Series(d.attrs["units_left_out"]))
    out.attrs["left_out"] = left_out_summary(pd.Series(d.attrs["left_out"]))
    return out


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


# --------------------------------------------------------------------------
# rule 4 — the Gower distance with the wing-borne pair, and its sensitivity
# --------------------------------------------------------------------------
#: shortlist fields whose value depends on whether a member on a wing is recorded as a boom
#: or as a propulsor on the wing card (the 2026-09-19 boom/nacelle rule). The pooled
#: distance replaces every one of them present in the shortlist with :data:`POOLED_FIELDS`.
BOOM_WING_FIELDS = ["boomsPresent", "boom1_count", "boom1_attach", "boom1_orient", "boom_count",
                    "boom_ntypes", "wing1_count", "wing1_zoneSpan", "wing1_zoneChord", "wing1_orient",
                    "wing1_propKin", "wing1_bmech", "wing1_chord"]
#: rule 4: rotors on the wing card and on wing-attached booms both count as wing-borne
POOLED_FIELDS = ["wing_borne_thrust", "wing_borne_units"]
#: aircraft-level propulsion variables, the same whichever card a member is recorded on
DERIVED_FIELDS = ["propulsor_units", "any_tilting_unit", "mixes_fixed_and_tilting", "any_ducted_unit",
                  "all_units_ducted"]
#: shortlist fields that describe the drawing, not the design (no distance uses them)
NOT_DESIGN = ["dinoUnderstanding"]
#: count fields compared by range (all others by match)
NUMERIC = {"propulsor_units", "wing_borne_units"}
#: chapter 5.3: one unit of weight per subsystem, divided among its fields. The pooled
#: ``wing_borne_thrust`` takes the booms slot, so both runs keep six subsystems.
SUBSYSTEM_OF = {
    "topType": "architecture",
    "fusShape": "fuselage", "fusKin": "fuselage", "gearArch": "fuselage", "latSym": "fuselage",
    "wCount": "wings", "wingConf": "wings", "wing1_posV": "wings", "wing1_posL": "wings",
    "wing1_plan": "wings",
    "empType": "empennage",
    "boomsPresent": "booms", "boom1_count": "booms", "boom1_attach": "booms", "boom1_orient": "booms",
    "wing_borne_thrust": "booms",
}


def gower_fields(ds: Dataset, pooled: bool = True, min_answered: int = 300,
                 min_effk: float = 1.5) -> List[str]:
    """The distance shortlist: the informative fields of 3.3.4 (drawing fields out) plus the
    derived propulsion variables; ``pooled`` swaps the boom-or-wing fields for the wing-borne pair."""
    from .a2 import d2_informative_fields

    inf = [f for f in d2_informative_fields(ds, min_answered, min_effk)["field"] if f not in NOT_DESIGN]
    if pooled:
        inf = [f for f in inf if f not in BOOM_WING_FIELDS] + POOLED_FIELDS
    return inf + DERIVED_FIELDS


def gower_frame(ds: Dataset) -> pd.DataFrame:
    """The typed aircraft with every field either run can use (wizard fields + derived)."""
    f = ds.variants.copy()
    d = derived_layer(ds)
    d.index = f.index
    for c in DERIVED_FIELDS + POOLED_FIELDS:
        f[c] = d[c]
    return f[f["topType"].notna()]


def _is_numeric(ds: Dataset, field: str) -> bool:
    if field in NUMERIC:
        return True
    dd = ds.data_dictionary
    kind = dict(zip(dd["column"], dd["kind"])).get(field) if dd is not None else None
    return kind == "int" or field.endswith("_count") or field.endswith("_ntypes") or field == "wCount"


def gower_distance(ds: Dataset, frame: pd.DataFrame, fields: List[str],
                   weighting: str = "subsystem") -> np.ndarray:
    """d(i,j) = Σ w δ (1 − s) / Σ w δ over ``fields`` (Gower, 1971; chapter 5.3).

    s is 1 for a shared category, 1 − |xi − xj| / range for a count; δ is 1 only when both
    aircraft carry a value, so a blank (absence, or a value an override hides) leaves the
    pair's average instead of registering as a difference. ``weighting``: ``subsystem``
    (one unit per subsystem, divided among its fields) or ``uniform``.
    """
    n = len(frame)
    if weighting == "subsystem":
        subs = {f: SUBSYSTEM_OF.get(f, "propulsion") for f in fields}
        size = pd.Series(subs).value_counts()
        w = {f: 1.0 / size[s] for f, s in subs.items()}
    else:
        w = {f: 1.0 for f in fields}
    num = np.zeros((n, n))
    den = np.zeros((n, n))
    for f in fields:
        x = frame[f]
        present = x.notna().to_numpy()
        both = present[:, None] & present[None, :]
        if _is_numeric(ds, f):
            a = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
            rng = np.nanmax(a) - np.nanmin(a) if present.any() else 0.0
            diff = np.abs(a[:, None] - a[None, :]) / rng if rng > 0 else np.zeros((n, n))
        else:
            codes = pd.factorize(x.astype(object).where(x.notna(), None), use_na_sentinel=True)[0]
            diff = (codes[:, None] != codes[None, :]).astype(float)
        diff = np.where(both, diff, 0.0)
        num += w[f] * diff
        den += w[f] * both
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def nearest_neighbours(D: np.ndarray, ids: np.ndarray) -> Dict[str, frozenset]:
    """Each aircraft's nearest neighbours: every aircraft at the minimum distance (ties kept)."""
    D = np.where(np.isnan(D), np.inf, D.copy())
    np.fill_diagonal(D, np.inf)
    m = D.min(axis=1, keepdims=True)
    near = D <= m + 1e-12
    return {ids[i]: frozenset(ids[np.flatnonzero(near[i])]) for i in range(len(ids))}


def _nn_changed(a: Dict[str, frozenset], b: Dict[str, frozenset], among: List[str]) -> List[str]:
    """Aircraft whose nearest neighbours in ``a`` and ``b`` share no aircraft (tie-robust)."""
    return [i for i in among if not (a[i] & b[i])]


def _archetype_keys(f: pd.DataFrame, fields: List[str]) -> pd.Series:
    return f[fields].astype(object).where(f[fields].notna(), None).astype(str).agg(" | ".join, axis=1)


def _split_from_raw(ka: pd.Series, kb: pd.Series) -> int:
    """Aircraft split away from their raw archetype: for each raw archetype, the aircraft
    outside the pooled archetype that holds most of it. Two raw archetypes merging into one
    pooled archetype move nobody (the drop in distinct archetypes shows the merges)."""
    if not len(ka):
        return 0
    ct = pd.crosstab(ka.to_numpy(), kb.to_numpy())
    return int(len(ka) - ct.max(axis=1).sum())


#: the archetype levels that read the boom-or-wing choice, and their pooled form (rule 4)
ARCHETYPE_POOLED = {
    "A1": (["topType", "wCount", "boomsPresent"], ["topType", "wCount", "wingBorne"]),
    "A1b": (["topType", "wCount", "boomBin"], ["topType", "wCount", "wingBorne"]),
    "A2": (["topType", "wCount", "boomsPresent", "empType"], ["topType", "wCount", "wingBorne", "empType"]),
}


def boom_wing_sensitivity(ds: Dataset) -> Dict[str, pd.DataFrame]:
    """Rule 4 sensitivity: raw fields against the pooled wing-borne pair, with and without the
    ``wing_boom_candidate`` aircraft (a member whose boom-or-wing reading is visually ambiguous).

    ``archetypes``: distinct archetypes and singletons at A1, A1b and A2 under the raw field
    (booms present / booms binned) and the pooled one (does the wing carry thrust: wing-borne,
    not wing-borne, wingless, or n/a for HB/PFV), and how many aircraft the pooled field splits
    away from their raw archetype.
    ``neighbours``: how many aircraft change nearest neighbour (no neighbour in common, ties
    kept) between the raw and the pooled Gower distance, under both weightings.
    ``fields``: which shortlist fields the pooled run replaces.
    """
    from .a2 import archetype_frame, hidden_by_override

    f = gower_frame(ds)
    ids = f["aircraft_id"].to_numpy()
    cand = f["wing_boom_candidate"].fillna(False).astype(bool).to_numpy() if "wing_boom_candidate" in f.columns \
        else np.zeros(len(f), dtype=bool)
    keep_ids = ids[~cand]

    # ---- archetypes
    af = archetype_frame(ds).set_index("aircraft_id").reindex(ids)
    wc = pd.to_numeric(af["wCount"], errors="coerce")
    wb = pd.Series(wing_borne_thrust(ds.variants).to_numpy(), index=ds.variants["aircraft_id"]).reindex(ids)
    wb = wb.where(~(wc == 0), "wingless")
    wb = wb.where(~af["topType"].isin(["HB", "PFV"]).to_numpy(), NO_M3_CARD)
    af["wingBorne"] = wb.to_numpy()
    arows = []
    for level, (raw_f, pool_f) in ARCHETYPE_POOLED.items():
        left = pd.Series(False, index=af.index)
        for fld in set(raw_f + pool_f):
            if fld in ("boomBin", "wingBorne"):
                left |= af[fld].isna()
            else:
                left |= hidden_by_override(af, fld, ds.data_dictionary)
        for subset, mask in (("all", np.ones(len(af), dtype=bool)), ("without the candidates", ~cand)):
            sub = af[mask & ~left.to_numpy()]
            kr, kp = _archetype_keys(sub, raw_f), _archetype_keys(sub, pool_f)
            changes = _split_from_raw(kr, kp)
            for run, key, flds in (("raw", kr, raw_f), ("pooled", kp, pool_f)):
                counts = key.value_counts()
                arows.append({"level": level, "aircraft set": subset, "run": run, "fields": " × ".join(flds),
                              "aircraft": int(len(sub)), "left out": int((mask & left.to_numpy()).sum()),
                              "distinct archetypes": int(len(counts)), "singletons": int((counts == 1).sum()),
                              "effective number": round(metrics.effective_number(key), 1),
                              "aircraft split from their raw archetype": changes if run == "pooled" else pd.NA})
    archetypes = pd.DataFrame(arows)
    archetypes["aircraft split from their raw archetype"] = archetypes["aircraft split from their raw archetype"].astype("Int64")

    # ---- nearest neighbours under the Gower distance
    raw_fields, pooled_fields = gower_fields(ds, pooled=False), gower_fields(ds, pooled=True)
    nrows = []
    for weighting in ("subsystem", "uniform"):
        nn = {}
        for run, flds in (("raw", raw_fields), ("pooled", pooled_fields)):
            nn[(run, "all")] = nearest_neighbours(gower_distance(ds, f, flds, weighting), ids)
            sub = f[~cand]
            nn[(run, "without")] = nearest_neighbours(gower_distance(ds, sub, flds, weighting), keep_ids)
        ch = _nn_changed(nn[("raw", "all")], nn[("pooled", "all")], list(ids))
        nrows.append({"weighting": weighting, "comparison": "raw against pooled, all aircraft",
                      "aircraft compared": len(ids), "nearest neighbour changes": len(ch),
                      "share": round(len(ch) / len(ids), 3),
                      "of which wing-boom candidates": int(np.isin(ch, ids[cand]).sum())})
        ch = _nn_changed(nn[("raw", "without")], nn[("pooled", "without")], list(keep_ids))
        nrows.append({"weighting": weighting, "comparison": "raw against pooled, candidates out",
                      "aircraft compared": len(keep_ids), "nearest neighbour changes": len(ch),
                      "share": round(len(ch) / len(keep_ids), 3), "of which wing-boom candidates": 0})
        ch = _nn_changed(nn[("pooled", "all")], nn[("pooled", "without")], list(keep_ids))
        nrows.append({"weighting": weighting, "comparison": "pooled, with against without the candidates",
                      "aircraft compared": len(keep_ids), "nearest neighbour changes": len(ch),
                      "share": round(len(ch) / len(keep_ids), 3), "of which wing-boom candidates": 0})
    neighbours = pd.DataFrame(nrows)

    replaced = [x for x in raw_fields if x not in pooled_fields]
    fields = pd.DataFrame({
        "run": ["raw", "pooled"],
        "fields": [len(raw_fields), len(pooled_fields)],
        "boom-or-wing fields": [", ".join(replaced), ", ".join(POOLED_FIELDS)],
    })
    out = {"archetypes": archetypes, "neighbours": neighbours, "fields": fields}
    for t in out.values():
        t.attrs.update({"candidates": int(cand.sum()), "aircraft": int(len(ids))})
    return out
