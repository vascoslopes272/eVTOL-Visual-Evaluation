"""A.2 — the corpus and the labels: the first descriptive pass, checks D1-D13.

One function per check. The unit is the primary approved variant (805 aircraft)
unless the docstring says patents. The labelling batches are provenance only and
nothing is split by batch.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import metrics
from .loaders import Dataset

#: the T2 value that says a figure shows the whole aircraft
WHOLE_VEHICLE = "Whole Vehicle Layout"
#: the figure quality flags, in the wizard's own vocabulary
QUALITY_NAMES = {"clean": "Clean", "generic": "Partial quality",
                 "poor_quality": "Poor quality"}

# --------------------------------------------------------------------------
# which columns count as an answerable slot
# --------------------------------------------------------------------------
#: sections of the wizard whose columns are aircraft labels
LABEL_SECTIONS = ("G1", "M1", "M2", "M3")
#: process columns that live in those sections but describe the labelling, not the aircraft
PROCESS_PATTERNS = ("humanUncertain", "quickOverride", "quickCount")


def answerable_slots(ds: Dataset) -> List[str]:
    """The 283 answerable slots: coded G1-M3 columns, process columns removed.

    A slot is a column of ``data_dictionary.csv`` that is (a) in a label section,
    (b) of a coded kind (``id`` / ``bool`` / ``int``, so free text and Other-note
    tags are out) and (c) not a labelling-process column.
    """
    dd = ds.data_dictionary
    if dd is None:
        raise FileNotFoundError("data_dictionary.csv is required for the slot list")
    keep = (
        dd["section"].isin(LABEL_SECTIONS)
        & dd["kind"].isin(["id", "bool", "int"])
        & ~dd["column"].str.contains("|".join(PROCESS_PATTERNS), case=False)
    )
    return [c for c in dd.loc[keep, "column"] if c in ds.master.columns]


def concept_of(slot: str) -> str:
    """Collapse a slot onto the concept behind it.

    Boom groups 1-6, wing panels 1-3 and propulsor tiers 1-3 repeat the same
    questions, so ``boom3_orient`` and ``boom1_orient`` are one concept, and
    ``wing1_t2_bmech`` collapses onto ``wing_bmech``.
    """
    slot = re.sub(r"^([A-Za-z]+?)[0-9]+_", r"\1_", slot)
    slot = re.sub(r"_t[0-9]_", "_", slot)
    return slot


# --------------------------------------------------------------------------
# D1 — the funnel
# --------------------------------------------------------------------------
def d1_funnel(ds: Dataset) -> pd.DataFrame:
    """The acquisition-to-analysis funnel."""
    c = ds.counts
    figs_per_patent = ds.approved_figures.groupby("patent_id").size()
    rows = [
        ("Patents acquired (PatSeer query)", c["patents_acquired"], ""),
        ("Approved at labelling", c["patents_wizard_approved"],
         f"{c['patents_wizard_approved'] / c['patents_acquired']:.0%} of acquired: show an "
         "aircraft that can be read from the figures"),
        ("Representative patents", c["patents_approved"],
         f"{c['patents_gated_out']} approved patents leave on a Similar tag (UAV, not electric, "
         "STOL only): only electric, vertical-take-off, occupied aircraft enter"),
        ("Representative patents that are the primary record", c["patents_analysis"],
         "O1 / O2 observations removed"),
        ("Aircraft observations", c["approved_variants"], "O1, O2 and S3 included"),
        ("Unique aircraft - the analysis unit", c["primary_approved_variants"],
         "one row per aircraft"),
        ("Approved figures", c["approved_figures_all"], "show the aircraft in a readable view"),
        ("Whole-aircraft figures - the analysis image set", c["approved_figures"],
         f"{c['detail_figures']} approved detail figures set aside; on {figs_per_patent.size} "
         f"patents, median {figs_per_patent.median():.0f} per patent"),
    ]
    return pd.DataFrame(rows, columns=["stage", "count", "note"])


def d1_approval_by_region(ds: Dataset) -> pd.DataFrame:
    """Approval rate per region — the North America surplus is an acquisition effect."""
    j = ds.patents.merge(ds.identity[["patent_id", "region"]], on="patent_id", how="left")
    g = j.groupby("region").agg(
        patents=("patent_id", "size"),
        representative=("is_representative", lambda s: int(s.fillna(False).astype(bool).sum())),
    )
    g["representative share"] = (g["representative"] / g["patents"]).round(2)
    return g.sort_values("patents", ascending=False).reset_index()


def d1_rejection_reasons(ds: Dataset) -> pd.DataFrame:
    """Why a patent is not representative: the wizard's reason, or the Similar tag that removed it."""
    rejected = ds.patents[~ds.patents["is_representative"].fillna(False).astype(bool)]
    counts = rejected["reason"].value_counts(dropna=False)
    return pd.DataFrame({
        "reason": [("(no reason recorded)" if pd.isna(k) else k) for k in counts.index],
        "patents": counts.to_numpy(),
    })


def filer_type(company_canonical: pd.Series) -> pd.Series:
    """Individual inventor / unattributed / named company, from ``company_canonical``."""
    cc = company_canonical.fillna(CATCH_ALL[1])
    return cc.where(cc.isin(CATCH_ALL), "Named company").replace(
        {CATCH_ALL[0]: "Individual inventor", CATCH_ALL[1]: "Unattributed or independent"}
    )


def _rejected_with_identity(ds: Dataset) -> pd.DataFrame:
    rejected = ds.patents[~ds.patents["is_representative"].fillna(False).astype(bool)]
    j = rejected.merge(
        ds.identity[["patent_id", "region", "company_canonical"]], on="patent_id", how="left"
    )
    j["reason"] = j["reason"].fillna("(no reason recorded)")
    j["filer type"] = filer_type(j["company_canonical"])
    return j


def d1_rejection_by_region(ds: Dataset) -> pd.DataFrame:
    """Rejection reason x region — does the labelling filter behave the same by office?"""
    j = _rejected_with_identity(ds)
    return pd.crosstab(j["reason"], j["region"], margins=True, margins_name="all")


def d1_rejection_by_filer_type(ds: Dataset) -> pd.DataFrame:
    """Rejection reason x filer type — and the same by applicant."""
    j = _rejected_with_identity(ds)
    return pd.crosstab(j["reason"], j["filer type"], margins=True, margins_name="all")


# --------------------------------------------------------------------------
# 2.1.2 the similars — the near misses of the domain
# --------------------------------------------------------------------------
def _levels(ds: Dataset) -> pd.DataFrame:
    """The identity sheet with membership columns: wizard-approved, representative, primary."""
    ident = ds.identity.copy()
    appr_ids = set(ds.patents.loc[ds.patents["is_approved"].fillna(False).astype(bool), "patent_id"])
    rep_ids = set(ds.patents.loc[ds.patents["is_representative"].fillna(False).astype(bool), "patent_id"])
    ident["_approved"] = ident["patent_id"].isin(appr_ids)
    ident["_representative"] = ident["patent_id"].isin(rep_ids)
    ident["_primary"] = ident["patent_id"].isin(set(ds.patents_analysis["patent_id"]))
    return ident


def d1_similars(ds: Dataset) -> pd.DataFrame:
    """UAV-similar, STOL-similar, electric-similar: how each is caught, and what it removes.

    Three different things sit next to the domain boundary and each is caught by a
    different reading of the text: occupancy (``UAVSimilar``), the take-off mode
    confirmed at review (``STOLSimilar`` for STOL only) and the powertrain
    (``ElectricSimilar``: turbine or piston named, no electric motor). Since
    2026-09-15 the tag is a gate: an aircraft carrying it leaves the analysis
    (``Dataset.gated_out``). Every count here is taken on the master's tags, at the
    aircraft level (an aircraft can carry two tags) and at the patent level.
    """
    ident = ds.identity
    reasons = ds.patents.set_index("patent_id")["reason"]
    gated = ds.gated_out
    tags = gated["edgeTags"].fillna("").astype(str).map(lambda v: set(v.split("|")) - {""})
    primary = gated["is_primary"].fillna(False).astype(bool)
    dropped_patents = set(ds.patents.loc[
        ds.patents["is_approved"].fillna(False).astype(bool) & ~ds.patents["is_representative"], "patent_id"])
    n_pure_uav = int(reasons.eq("Pure UAV").sum())
    n_not_vtol = int(reasons.eq("Not VTOL").sum())
    n_unknown = int(ident["is_electric_final"].eq("Unknown").sum())
    vstol = ident["takeoff_final"].eq("V/STOL")
    vs_n = int(vstol.sum())
    vs_p = int(ident.loc[vstol, "patent_id"].isin(set(ds.patents_analysis["patent_id"])).sum())
    rows = []
    for name, tag, rule in [
        ("UAV-similar", "UAVSimilar",
         "tag UAVSimilar: drawn unoccupied, the text does not declare a UAV (a declared UAV "
         f"is disapproved at labelling as Pure UAV: {n_pure_uav})"),
        ("STOL-similar", "STOLSimilar",
         "take-off mode read from the text, confirmed at review: STOL only (a patent that "
         f"claims no vertical take-off is disapproved at labelling as Not VTOL: {n_not_vtol}). "
         f"V/STOL, where the text claims both, is kept ({vs_n} patents, {vs_p} primary)"),
        ("Electric-similar", "ElectricSimilar",
         "powertrain read from the text names a turbine or piston engine and no electric motor "
         "(is_electric_final = No), or the review tag ElectricSimilar; hybrid stays, and "
         f"{n_unknown} patents give no evidence either way and stay"),
    ]:
        has = tags.map(lambda t, tag=tag: tag in t)
        pats = set(gated.loc[has, "patent_id"])
        rows.append({"similar": name, "caught by": rule,
                     "aircraft observations tagged": int(has.sum()),
                     "unique aircraft removed": int((has & primary).sum()),
                     "patents tagged": len(pats),
                     "patents losing every aircraft": len(pats & dropped_patents),
                     "outcome": "leaves the analysis set at refinement 1"})
    out = pd.DataFrame(rows)
    out.attrs.update({"vstol": (vs_n, vs_p), "gated_patents": len(dropped_patents),
                      "gated_aircraft": int(primary.sum())})
    return out


# --------------------------------------------------------------------------
# 2.1.4 filing status — granted, pending, withdrawn — at each level
# --------------------------------------------------------------------------
#: PatSeer legal status -> the filing-status row of the document
FILING_STATUS = {
    "ACTIVE - GRANTED": "Granted, in force",
    "INACTIVE - EXPIRED": "Granted, since lapsed",
    "INACTIVE - NONPAYMENT": "Granted, since lapsed",
    "ACTIVE - APPLIED": "Pending application",
    "INACTIVE - WITHDRAWN / SURRENDERED": "Withdrawn, refused or suspended",
    "INACTIVE - REJECTED / REFUSED / SUSPENDED": "Withdrawn, refused or suspended",
}
FILING_ORDER = ["Granted, in force", "Granted, since lapsed", "Pending application",
                "Withdrawn, refused or suspended", "Unknown"]


def d1_filing_status(ds: Dataset) -> pd.DataFrame:
    """Granted / pending / withdrawn at the acquired, representative and primary levels.

    The office sense of "approved" (granted) and the domain sense (representative)
    are kept apart: this table is the office sense only.
    """
    ident = _levels(ds)
    status = ident["legal_status_raw"].map(FILING_STATUS)
    # a status the map does not know falls back on the coarse legal_stage column
    fallback = ident["legal_stage"].map({"Granted": "Granted, in force",
                                         "Application": "Pending application"}).fillna("Unknown")
    status = status.fillna(fallback)
    rows = []
    for name in FILING_ORDER:
        m = status.eq(name)
        rows.append({"filing status": name, "acquired": int(m.sum()),
                     "representative": int((m & ident["_representative"]).sum()),
                     "primary": int((m & ident["_primary"]).sum())})
    granted = status.str.startswith("Granted")
    out = pd.DataFrame(rows)
    out = out[out["acquired"] > 0].reset_index(drop=True)
    out.attrs["granted"] = (int(granted.sum()), int((granted & ident["_representative"]).sum()),
                            int((granted & ident["_primary"]).sum()))
    return out


# --------------------------------------------------------------------------
# D2 — what the label set contains
# --------------------------------------------------------------------------
def d2_slots_per_aircraft(ds: Dataset) -> pd.Series:
    """How many of the answerable slots each aircraft answers (one value per variant)."""
    return ds.variants[answerable_slots(ds)].notna().sum(axis=1)


def d2_label_set(
    ds: Dataset, near_constant_min_answered: int = 100, near_constant_share: float = 0.95,
    informative_min_answered: int = 300, informative_min_effk: float = 1.5,
) -> pd.DataFrame:
    """The properties of the label set: slots, concepts, coverage, informative fields."""
    slots = answerable_slots(ds)
    sub = ds.variants[slots]
    answered_per_aircraft = d2_slots_per_aircraft(ds)
    coverage = sub.notna().mean()
    inv = d2_field_inventory(ds)

    near_constant = inv[
        (inv["answered"] >= near_constant_min_answered)
        & (inv["top_share"] >= near_constant_share)
    ]
    informative = inv[
        (inv["answered"] >= informative_min_answered)
        & (inv["effective_answers"] >= informative_min_effk)
    ]
    q1, q3 = answered_per_aircraft.quantile([0.25, 0.75])
    rows = [
        ("Answerable slots (G1 to M3, coded columns; free text and process flags excluded)", len(slots)),
        ("Distinct concepts behind them (repeats collapsed)",
         len({concept_of(s) for s in slots})),
        ("Slots answered per aircraft, median", int(answered_per_aircraft.median())),
        ("Slots answered per aircraft, lower quartile", int(q1)),
        ("Slots answered per aircraft, upper quartile", int(q3)),
        ("Slots answered per aircraft, minimum", int(answered_per_aircraft.min())),
        ("Slots answered per aircraft, maximum", int(answered_per_aircraft.max())),
        ("Slots answered on more than 90 % of aircraft", int((coverage > 0.90).sum())),
        ("Slots answered on fewer than 5 % of aircraft", int((coverage < 0.05).sum())),
        (f"Fields with the same answer on {near_constant_share:.0%} or more "
         f"(answered on at least {near_constant_min_answered})", len(near_constant)),
        ("Fields that carry the information", len(informative)),
    ]
    return pd.DataFrame(rows, columns=["property of the label set", "value"])


def d2_field_inventory(ds: Dataset) -> pd.DataFrame:
    """Per-slot profile: answered, distinct answers, top share, effective answers.

    This is the frame behind ``joined/phase1_field_inventory.csv``; recomputing it
    here is what makes the ranking below reproducible.
    """
    dd = ds.data_dictionary.set_index("column")["section"]
    rows = [
        metrics.field_profile(ds.variants, slot, section=str(dd.get(slot, "")))
        for slot in answerable_slots(ds)
    ]
    return pd.DataFrame(rows)


#: the plain-English name of each informative field, as the document prints it
FIELD_NAMES: Dict[str, str] = {
    "empType": "tail type",
    "topType": "architecture type",
    # boom_count is an M3 (propulsion) field: it counts the propulsor units
    # carried on the booms, not the booms themselves (boom1_count..boom6_count,
    # section M1, count those). The document's D2 table names it "number of
    # booms"; that wording is wrong and is corrected here.
    "boom_count": "propulsor units on the booms",
    "wing1_zoneSpan": "propulsors along the wing span",
    "boom1_orient": "direction of boom group 1",
    "boom1_count": "number of booms in group 1",
    "wing1_posV": "wing height on the fuselage",
    "fusShape": "fuselage cross-section",
    "wing1_plan": "wing planform",
    "wing1_zoneChord": "propulsors along the wing chord",
    "wCount": "number of wings",
    "gearArch": "landing-gear type",
    "dinoUnderstanding": "figure readability",
    "wing1_posL": "wing fore/aft position",
    "wing1_orient": "thrust axis of the wing propulsors",
    "boom1_attach": "what the booms attach to",
    "boom_ntypes": "number of distinct boom groups",
    "wing1_propKin": "whether the wing propulsors tilt",
    "boomsPresent": "booms present",
    "wing1_bmech": "open or ducted wing propulsors",
    "fusKin": "fuselage motion hover to cruise",
    "wingConf": "wing configuration",
    "latSym": "left-right symmetry",
}


def d2_informative_fields(
    ds: Dataset, min_answered: int = 300, min_effk: float = 1.5
) -> pd.DataFrame:
    """The ranking by effective number of answers — the fields that carry information.

    The two cumulative columns say how much of a field the two and three most
    common answers already cover; a field whose top-3 share is close to 1 has a
    long tail of rare answers that the distance will treat as one-offs.
    """
    inv = d2_field_inventory(ds)
    keep = inv[(inv["answered"] >= min_answered) & (inv["effective_answers"] >= min_effk)]
    out = keep.sort_values("effective_answers", ascending=False).copy()
    out["effective_answers"] = out["effective_answers"].round(1)
    out["top2_cumulative"] = [
        round(metrics.top_k_share(ds.variants[f], 2), 2) for f in out["field"]
    ]
    out["top3_cumulative"] = [
        round(metrics.top_k_share(ds.variants[f], 3), 2) for f in out["field"]
    ]
    out.insert(0, "name", out["field"].map(FIELD_NAMES).fillna(""))
    return out.reset_index(drop=True)


def d2_near_constant_fields(
    ds: Dataset, min_answered: int = 100, min_share: float = 0.95
) -> pd.DataFrame:
    """The near-constant fields — reported as findings, never dropped in silence (A.3)."""
    inv = d2_field_inventory(ds)
    keep = inv[(inv["answered"] >= min_answered) & (inv["top_share"] >= min_share)].copy()
    keep["effective_answers"] = keep["effective_answers"].round(2)
    keep.insert(0, "name", keep["field"].map(FIELD_NAMES).fillna(""))
    return keep.sort_values("top_share", ascending=False).reset_index(drop=True)


#: the T2 (figure-level) slots the wizard answers on every approved figure
FIGURE_SLOTS = {
    "per": "perspective",
    "acSty": "drawing style",
    "acCol": "aircraft colour",
    "bgSty": "background style",
    "parts": "what the figure shows",
    "qualityFlag": "quality flag",
    "acState": "flight state drawn",
    "hasLegends": "legends present",
}


def d2_figure_slots(ds: Dataset) -> pd.DataFrame:
    """The figure-level (T2) slots, profiled over the approved figures.

    The aircraft-level slots of :func:`d2_label_set` describe the design; these
    describe the drawing, and they are the confounds the embedding pillar has to
    control for (perspective, style, colour, background).
    """
    figs = ds.approved_figures
    rows = []
    for col, name in FIGURE_SLOTS.items():
        if col not in figs.columns:
            continue
        p = metrics.field_profile(figs, col, section="T2")
        top = figs[col].dropna().value_counts().head(3)
        rows.append({
            "name": name, "field": col, "answered": p["answered"],
            "answers": p["answers"], "top_share": p["top_share"],
            "effective_answers": round(p["effective_answers"], 1),
            "most common answers": " · ".join(f"{k} {v}" for k, v in top.items()),
        })
    return pd.DataFrame(rows)


def d2_figure_slot_answers(ds: Dataset, top: int = 4) -> pd.DataFrame:
    """The most common answers of each figure-level (T2) slot, with counts."""
    figs = ds.approved_figures
    rows = []
    for col, name in FIGURE_SLOTS.items():
        if col not in figs.columns:
            continue
        counts = figs[col].dropna().astype(str).value_counts()
        rows.append({
            "slot": name, "answered": int(counts.sum()),
            "most common answers": " · ".join(f"{k} {v}" for k, v in counts.head(top).items()),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# D3 — class balance
# --------------------------------------------------------------------------
def d3_architecture_balance(ds: Dataset) -> pd.DataFrame:
    """The architecture type is well balanced for a twelve-class variable."""
    return metrics.share_table(ds.variants["topType"], names=metrics.ARCH_NAMES)


#: the fields the document prints in full under D3
D3_FIELDS = ["wCount", "empType", "fusKin", "wingConf", "gearArch", "latSym"]


def d3_selected_fields(ds: Dataset, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Answered / distinct / top share and the most common answers, per field."""
    rows = []
    for f in fields or D3_FIELDS:
        s = ds.variants[f]
        names = metrics.option_names(ds.data_dictionary, f)
        top = s.dropna().value_counts().head(4)
        rows.append({
            "name": FIELD_NAMES.get(f, f),
            "field": f,
            "answered": int(s.notna().sum()),
            "answers": int(s.nunique(dropna=True)),
            "top_share": round(metrics.top_share(s), 2),
            "most common answers": " · ".join(
                f"{names.get(str(k), k)} {v}" for k, v in top.items()
            ),
        })
    return pd.DataFrame(rows)


def _group_columns(ds: Dataset, suffix: str) -> List[str]:
    return [s for s in answerable_slots(ds) if s.endswith(suffix)]


#: How many propulsor units each carrier holds. One column per carrier, all in
#: section M3. ``boom_count`` is the units carried on the booms; the number of
#: booms is ``boom1_count``..``boom6_count`` in M1. The ``_t<N>_`` columns split
#: a carrier's units by type and are already inside the carrier total, so adding
#: them would double-count.
PROPULSOR_UNIT_COLUMNS = [
    "boom_count", "wing1_count", "wing2_count", "wing3_count",
    "emp_count", "fuselage_count", "hull_array_count", "core_layout_count",
]


def d3_propulsor_units(ds: Dataset) -> Dict:
    """The propulsor groups, read across every carrier and tier.

    A "group" is one row of one propulsor card: a wing panel, a boom group, the
    empennage, the fuselage or a hull array, at one of its up-to-three tiers.
    """
    v = ds.variants
    kin = _group_columns(ds, "_propKin")
    bmech = _group_columns(ds, "_bmech")
    counts = [c for c in PROPULSOR_UNIT_COLUMNS if c in v.columns]

    kin_all = pd.concat([v[c] for c in kin]).value_counts()
    ducted_per_aircraft = v[bmech].eq("Ducted").any(axis=1)
    open_per_aircraft = v[bmech].eq("Open").any(axis=1)
    tilt = v[kin].eq("Tilt").any(axis=1)
    fixed = v[kin].eq("Fixed").any(axis=1)
    units = v[counts].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    return {
        "groups_fixed": int(kin_all.get("Fixed", 0)),
        "groups_tilting": int(kin_all.get("Tilt", 0)),
        "groups_other": int(kin_all.get("Other", 0)),
        "aircraft_with_a_ducted_unit": int(ducted_per_aircraft.sum()),
        "aircraft_all_units_ducted": int((ducted_per_aircraft & ~open_per_aircraft).sum()),
        "aircraft_with_a_tilting_unit": int(tilt.sum()),
        "aircraft_mixing_fixed_and_tilting": int((tilt & fixed).sum()),
        "units_median": float(units.median()),
        "units_q1": float(units.quantile(0.25)),
        "units_q3": float(units.quantile(0.75)),
        "aircraft_with_more_than_8_units": int((units > 8).sum()),
    }


# --------------------------------------------------------------------------
# D4 — missingness
# --------------------------------------------------------------------------
#: each check is (label, parent test, child field)
D4_CHECKS = [
    ("Booms present but boom direction blank", ("boomsPresent", True), "boom1_orient"),
    ("Architecture type blank", None, "topType"),
    ("Wings present but wing height blank", ("wCount", "winged"), "wing1_posV"),
    ("Wings present but wing planform blank", ("wCount", "winged"), "wing1_plan"),
    ("Wings present but tail type blank", ("wCount", "winged"), "empType"),
    ("Fuselage cross-section blank", None, "fusShape"),
]


def d4_missingness(ds: Dataset) -> pd.DataFrame:
    """A blank is a labelling gap only where the parent field says the part exists."""
    v = ds.variants
    winged = pd.to_numeric(v["wCount"], errors="coerce").fillna(0) > 0
    rows = []
    for label, parent, child in D4_CHECKS:
        if parent is None:
            mask = pd.Series(True, index=v.index)
        elif parent[1] == "winged":
            mask = winged
        else:
            mask = v[parent[0]].fillna(False).astype(bool)
        blank = v.loc[mask, child].isna()
        rows.append({
            "check": label,
            "affected": int(blank.sum()),
            "of": int(mask.sum()),
            "share": round(float(blank.mean()) if mask.sum() else 0.0, 3),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# D5 — archetype cardinality
# --------------------------------------------------------------------------
#: the archetype levels of the document: (fields, what the row says), each level
#: named by what it adds to the architecture class. ``boomBin`` and ``anyTilt``
#: are derived in :func:`archetype_frame`.
ARCHETYPE_LEVELS = {
    "A0": (["topType"], "architecture class"),
    "A1": (["topType", "wCount", "boomsPresent"], "+ number of wings, booms present"),
    "A1b": (["topType", "wCount", "boomBin"],
            "+ number of wings, booms binned none / 1-2 / 3 / 4 or more"),
    "A1t": (["topType", "wCount", "anyTilt"], "+ number of wings, any tilting unit"),
    "A2": (["topType", "wCount", "boomsPresent", "empType"],
           "+ number of wings, booms present, tail type"),
}
#: the seven fields the S3 identical-to-root check compares (the old A3 level)
ARCHETYPE_FIELDS_FULL = ["topType", "wCount", "boomsPresent", "empType", "fusKin", "gearArch",
                         "wingConf"]


def boom_bin(n_booms: pd.Series) -> pd.Series:
    """Number of booms -> none / 1-2 / 3 / 4+ (the design decision behind the count)."""
    n = pd.to_numeric(n_booms, errors="coerce").fillna(0)
    return pd.cut(n, bins=[-1, 0, 2, 3, 10 ** 6], labels=["none", "1-2", "3", "4+"]).astype(str)


def archetype_frame(ds: Dataset) -> pd.DataFrame:
    """The variants with the two derived archetype fields added.

    ``boomBin`` bins the number of booms (``boom1_count`` .. ``boom6_count``, the
    M1 structural count — not ``boom_count``, which is the propulsor units the
    booms carry); ``anyTilt`` is true when any propulsor group tilts.
    """
    v = ds.variants[ds.variants["topType"].notna()].copy()
    boom_cols = [c for c in v.columns if re.match(r"boom\d_count$", c)]
    v["nBooms"] = v[boom_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1).astype(int)
    v["boomBin"] = boom_bin(v["nBooms"])
    kin = _group_columns(ds, "_propKin")
    v["anyTilt"] = v[kin].eq("Tilt").any(axis=1)
    return v


def d5_archetype_cardinality(ds: Dataset, levels: Optional[Dict] = None) -> pd.DataFrame:
    """How fine a design species can be defined before the corpus turns into singletons.

    An archetype is the string formed by joining the chosen fields; *distinct
    archetypes* counts those strings, *singletons* the strings holding exactly one
    aircraft, and the *effective number* is exp of the Shannon entropy of their
    shares.
    """
    v = archetype_frame(ds)
    rows = []
    for name, spec in (levels or ARCHETYPE_LEVELS).items():
        fields, label = spec if isinstance(spec, tuple) else (spec, ", ".join(spec))
        key = v[fields].astype(str).agg(" | ".join, axis=1)
        counts = key.value_counts()
        rows.append({
            "level": name,
            "fields combined": label,
            "aircraft": int(len(v)),
            "distinct archetypes": int(len(counts)),
            "singletons": int((counts == 1).sum()),
            "singleton share": round(float((counts == 1).sum() / len(v)), 3),
            "effective number": round(metrics.effective_number(key), 1),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# D6 — where the labels say they are weak
# --------------------------------------------------------------------------
D6_FLAGS = {
    "Mixed architecture": "notPureArch",
    "Annotator unsure at G1": "g1_humanUncertain",
    "Annotator unsure at M2": "m2_humanUncertain",
    "Annotator unsure at T1": "t1_humanUncertain",
    "Annotator unsure at M1": "m1_humanUncertain",
    "Quick count override": "g1_quickOverride",
}


def d6_weak_labels(ds: Dataset) -> pd.DataFrame:
    """The annotator's own uncertainty flags, plus the unreadable figures."""
    v = ds.variants
    rows = []
    for label, col in D6_FLAGS.items():
        if col not in v.columns:
            continue
        rows.append({
            "flag": label,
            "column": col,
            "aircraft": int(v[col].fillna(False).astype(bool).sum()),
        })
    rows.append({
        "flag": 'Figure readability "Impossible"',
        "column": "dinoUnderstanding",
        "aircraft": int((v["dinoUnderstanding"].astype(str) == "Impossible").sum()),
    })
    return pd.DataFrame(rows).sort_values("aircraft", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------
# D7 — duplicates and variants
# --------------------------------------------------------------------------
#: wizard duplicate code -> (name, what it is, counts as a new unique aircraft?)
#: O1 / O2 are the same aircraft seen again (observations); S3 is a similar
#: aircraft, fully relabelled, and a source of new unique aircraft.
DUP_TYPES = {
    1: ("O1 - same aircraft seen again, new figures", "labels inherited from the original", "no"),
    2: ("O2 - same aircraft, same figures", "nothing relabelled", "no"),
    3: ("S3 - a similar aircraft", "fully relabelled; one new unique aircraft", "yes"),
}


def d7_duplicates(ds: Dataset) -> pd.DataFrame:
    """Observations (O1, O2) against similars (S3): only S3 adds unique aircraft."""
    all_rows = ds.master["dup_type"].value_counts()
    in_set = ds.variants["dup_type"].value_counts()
    rows = []
    for code, (name, what, new) in DUP_TYPES.items():
        rows.append({
            "type": name,
            "what it is": what,
            "observations": int(all_rows.get(code, 0)),
            "unique aircraft added": int(in_set.get(code, 0)),
            "new unique aircraft": new,
        })
    return pd.DataFrame(rows)


def d7_d3_rows(ds: Dataset, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Every D3 row against its root: same architecture? identical on the archetype fields?"""
    fields = fields or ARCHETYPE_FIELDS_FULL
    d3 = ds.variants[ds.variants["dup_type"] == 3]
    rows = []
    for _, row in d3.iterrows():
        root = ds.master[ds.master["patent_id"] == row.get("dup_root")]
        root = root[root["is_primary"].fillna(False).astype(bool)]
        entry = {"patent_id": row["patent_id"], "variant": row["variant"],
                 "root": row.get("dup_root"), "root_found": not root.empty,
                 "same_architecture": None, "identical_on_archetype_fields": None}
        if not root.empty:
            root = root.iloc[0]
            entry["same_architecture"] = str(root["topType"]) == str(row["topType"])
            entry["identical_on_archetype_fields"] = all(
                str(root[f]) == str(row[f]) for f in fields
            )
        rows.append(entry)
    return pd.DataFrame(rows)


def d7_d3_identical_to_root(ds: Dataset, fields: Optional[List[str]] = None) -> Dict:
    """How many D3 rows are identical to their root on the archetype fields.

    A D3 is a modified re-filing of the same invention. Where it is identical on
    all seven archetype fields it is a near-replicate in the counting metrics.
    """
    t = d7_d3_rows(ds, fields)
    identical = int(t["identical_on_archetype_fields"].fillna(False).sum())
    return {
        "d3_rows": int(len(t)),
        "same_architecture_as_root": int(t["same_architecture"].fillna(False).sum()),
        "identical_on_all_archetype_fields": identical,
        "share_of_analysis_set": round(identical / len(ds.variants), 3) if len(ds.variants) else 0.0,
    }


def d7_aircraft_per_patent(ds: Dataset) -> pd.DataFrame:
    """How many aircraft each approved primary patent draws."""
    counts = ds.variants.groupby("patent_id").size().value_counts().sort_index()
    return pd.DataFrame({"aircraft drawn in the patent": counts.index,
                         "patents": counts.to_numpy()})


# --------------------------------------------------------------------------
# D8 — who filed, and how concentrated it is
# --------------------------------------------------------------------------
#: the two catch-all buckets of company_canonical, which are not companies
CATCH_ALL = ("Individual Inventor", "Unknown / Independent")


def normalise_assignee(series: pd.Series) -> pd.Series:
    """Strip the trailing country code PatSeer appends to the raw assignee string."""
    return (
        series.dropna().astype(str)
        .str.replace(r"\s*\([A-Z]{2}\)\s*$", "", regex=True)
        .str.strip()
    )


def _filers(ds: Dataset) -> pd.DataFrame:
    return ds.patents_analysis.merge(
        ds.identity[["patent_id", "company_canonical", "assignee_raw"]],
        on="patent_id", how="left",
    )


def d8_filer_mix(ds: Dataset) -> pd.DataFrame:
    """Half the corpus is not corporate at all."""
    j = _filers(ds)
    cc = j["company_canonical"]
    named = ~cc.isin(CATCH_ALL) & cc.notna()
    rows = [
        ("Individual inventors", int((cc == CATCH_ALL[0]).sum())),
        ("Unattributed or independent", int((cc == CATCH_ALL[1]).sum())),
        (f"Named companies ({cc[named].nunique()} of them)", int(named.sum())),
    ]
    out = pd.DataFrame(rows, columns=["filer", "patents"])
    out["share"] = (out["patents"] / len(j)).round(2)
    return out


def d8_concentration(ds: Dataset) -> pd.DataFrame:
    """The same question asked of the raw assignee string and of the canonical company.

    The two columns count different things: the raw string is the honest answer to
    "how dispersed is the corpus", the canonical column is the one to resample in
    the company bootstrap, because one firm files under several strings.
    """
    j = _filers(ds)
    raw = normalise_assignee(j["assignee_raw"])
    cc = j["company_canonical"]
    named = cc[~cc.isin(CATCH_ALL) & cc.notna()]

    raw_stats = metrics.concentration(raw)
    # the named-company shares are shares of ALL the analysis patents, not of the
    # corporate subset, so the two columns are comparable
    cc_stats = metrics.concentration(named)
    named_counts = named.value_counts()
    cc_stats["top10_share"] = round(float(named_counts.head(10).sum() / len(j)), 2)
    cc_stats["hhi"] = round(float(((named_counts / len(j)) ** 2).sum()), 3)
    cc_counts = cc.dropna().value_counts()
    rows = [
        ("Distinct filers", raw_stats["distinct"],
         f"{cc_counts.size} values: {named.nunique()} named companies plus the two catch-all buckets"),
        ("Filers with exactly one patent", raw_stats["singletons"],
         f"{metrics.concentration(named)['singletons']} of the {named.nunique()} named companies"),
        (f"Top-10 share of all {len(j)} patents", raw_stats["top10_share"],
         f"{cc_stats['top10_share']} (named companies only)"),
        ("HHI", raw_stats["hhi"], f"{cc_stats['hhi']} (named companies only)"),
        ("Largest filer", raw_stats["largest"], cc_stats["largest"]),
    ]
    return pd.DataFrame(rows, columns=["concentration measure",
                                       "on the raw assignee string",
                                       "on the canonical company"])


def d8_single_patent_filers(ds: Dataset) -> pd.DataFrame:
    """Where the single-patent filers sit: inside the catch-all buckets, or named.

    The canonical column cannot show them, because the bucket that holds most of
    them counts as one value.
    """
    j = _filers(ds)
    raw = normalise_assignee(j["assignee_raw"])
    counts = raw.value_counts()
    singles = j.loc[raw.index[raw.isin(counts[counts == 1].index)]]
    canonical = singles["company_canonical"].fillna("(no canonical company)")
    bucket = canonical.where(canonical.isin(CATCH_ALL), "named company")
    out = metrics.share_table(bucket)
    out.attrs["distinct_named_companies"] = int(
        canonical[~canonical.isin(CATCH_ALL)].nunique()
    )
    out.attrs["examples"] = sorted(
        canonical[~canonical.isin(CATCH_ALL)].unique()
    )[:6]
    return out


def d8_filer_counts(ds: Dataset):
    """Patents per filer, twice: raw assignee string, and named canonical company.

    The pair the Lorenz curve of index 3.2 is drawn from.
    """
    j = _filers(ds)
    raw = normalise_assignee(j["assignee_raw"]).value_counts()
    cc = j["company_canonical"]
    canonical = cc[~cc.isin(CATCH_ALL) & cc.notna()].value_counts()
    return raw, canonical


def d8_split_firms(ds: Dataset, company: str = "Bell / Textron") -> pd.DataFrame:
    """The raw assignee strings one canonical firm files under (the Bell case)."""
    j = _filers(ds)
    sub = j[j["company_canonical"] == company]
    counts = normalise_assignee(sub["assignee_raw"]).value_counts()
    return pd.DataFrame({"assignee string": counts.index, "patents": counts.to_numpy()})


# --------------------------------------------------------------------------
# D9 — time coverage and where the corpus stops being complete
# --------------------------------------------------------------------------
def d9_publication_lag(ds: Dataset, by: str = "region") -> pd.DataFrame:
    """Median and 90th-percentile lag from priority to publication.

    A patent enters the corpus only when it publishes, so this is what says which
    priority years are complete.
    """
    j = ds.patents_analysis.merge(
        ds.identity[["patent_id", "priority_year", "pub_year", "region", "pub_office"]],
        on="patent_id", how="left", suffixes=("", "_id"),
    )
    year = j["pub_year"] if "pub_year" in j else j["pub_year_id"]
    j = j.assign(lag=pd.to_numeric(year, errors="coerce")
                 - pd.to_numeric(j["priority_year"], errors="coerce"))
    g = j.dropna(subset=["lag"]).groupby(by)["lag"]
    out = pd.DataFrame({
        "patents": g.size(),
        "median lag": g.median().round(0),
        "90th percentile": g.quantile(0.90).round(0),
    })
    return out.sort_values("patents", ascending=False).reset_index()


#: the windows the document reports architecture shares over
WINDOWS = [("<= 2011", 0, 2011), ("2012-15", 2012, 2015), ("2016-19", 2016, 2019),
           ("2020-23", 2020, 2023), ("2024-26 (partial)", 2024, 2100)]


def d9_architecture_by_window(
    ds: Dataset, types: Optional[List[str]] = None, windows: Optional[List] = None
) -> pd.DataFrame:
    """Architecture shares per time window — the shift the methods have to test."""
    j = ds.variants.merge(
        ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left"
    )
    year = pd.to_numeric(j["priority_year"], errors="coerce")
    types = types or ["TR", "SLC", "CVT", "MR"]
    rows = []
    for name, lo, hi in (windows or WINDOWS):
        sub = j[(year >= lo) & (year <= hi)]
        row = {"window": name, "unique aircraft": int(len(sub))}
        shares = sub["topType"].value_counts(normalize=True)
        for t in types:
            row[metrics.ARCH_NAMES.get(t, t)] = round(float(shares.get(t, 0.0)), 2)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs["max_share_any_class_any_window"] = float(
        max(
            j[(year >= lo) & (year <= hi)]["topType"].value_counts(normalize=True).max()
            for _, lo, hi in (windows or WINDOWS)
        )
    )
    return out


# --------------------------------------------------------------------------
# D11 — how much visual evidence each label rests on
# --------------------------------------------------------------------------
def d11_figures_per_variant(ds: Dataset) -> pd.DataFrame:
    """Approved figures behind each aircraft — 28 % rest on a single figure."""
    n = pd.to_numeric(ds.variants["n_approved_this_variant"], errors="coerce").fillna(0)
    binned = n.clip(upper=5).astype(int).map(
        {1: "1 figure", 2: "2 figures", 3: "3 figures", 4: "4 figures", 5: "5 or more"}
    )
    counts = binned.value_counts().reindex(
        ["1 figure", "2 figures", "3 figures", "4 figures", "5 or more"]
    ).dropna()
    return pd.DataFrame({"approved figures behind the aircraft": counts.index,
                         "unique aircraft": counts.astype(int).to_numpy()})


def d11_figure_quality(ds: Dataset) -> pd.DataFrame:
    """The quality flags and the scope label on the approved figures."""
    figs = ds.approved_figures
    quality = figs["qualityFlag"].fillna("clean").astype(str).map(
        lambda k: QUALITY_NAMES.get(k, k)
    )
    whole = figs["parts"].astype(str).eq(WHOLE_VEHICLE)
    rows = [(str(k), int(v)) for k, v in quality.value_counts().items()]
    rows.append(("Labelled Whole Vehicle Layout", int(whole.sum())))
    rows.append(("Total approved figures", int(len(figs))))
    return pd.DataFrame(rows, columns=["approved figures", "count"])


def d11_figure_approval(ds: Dataset) -> pd.DataFrame:
    """Why a figure is approved, and the resulting count.

    A figure is approved when it shows the whole aircraft in a view the
    architecture can be read from; the T2 ``parts`` value records what the
    approved figure shows, so the detail figures approved on purpose are listed.
    """
    figs = ds.figures_rep
    status = figs["status"].astype(str).str.lower()
    appr = ds.approved_figures_all
    parts = appr["parts"].astype(str).str.split("|").str[0].replace({"nan": "(blank)"})
    rows = [("Figures with an image file", int(len(figs))),
            ("Not approved", int(status.eq("disapproved").sum())),
            ("Approved", int(len(appr)))]
    counts = parts.value_counts()
    minor = counts[counts < 5]
    for k, v in counts[counts >= 5].items():
        rows.append((f"  approved, shows: {k}", int(v)))
    if len(minor):
        rows.append((f"  approved, shows: other part or blank ({len(minor)} values)", int(minor.sum())))
    return pd.DataFrame(rows, columns=["figures", "count"])


def d11_figure_patents(ds: Dataset) -> pd.DataFrame:
    """The patents that carry approved figures, split by what they are.

    More patents carry figures than there are primary records: an O1 observation
    brings new figures of an aircraft already in the set, and a disapproved
    patent may still hold an approved figure (a contradiction to review).
    """
    fig_patents = set(ds.approved_figures["patent_id"])
    primary = set(ds.patents_analysis["patent_id"])
    pat = ds.patents.set_index("patent_id")
    rest = pat.reindex(sorted(fig_patents - primary))
    approved = rest["is_representative"].fillna(False).astype(bool)
    o1 = approved & rest["dup_type"].eq(1)
    other_dup = approved & ~rest["dup_type"].eq(1)
    rows = [
        ("Patents carrying approved figures", len(fig_patents), ""),
        ("  primary representative patents", len(fig_patents & primary), "the analysis set"),
        ("  O1 observations with new figures", int(o1.sum()),
         "same aircraft as a primary record; labels inherited"),
        ("  other representative, not primary", int(other_dup.sum()), ""),
        ("  disapproved patents with an approved figure", int((~approved).sum()),
         ", ".join(rest.index[~approved]) + " - to review" if (~approved).any() else ""),
    ]
    return pd.DataFrame(rows, columns=["patents", "count", "note"])


def d11_sensitivity_set(ds: Dataset) -> Dict:
    """The thin-evidence flag: one approved figure, or a figure flagged for quality.

    Readability ("Impossible") is not part of it: nothing in the preliminary
    analysis depends on what a model can read, and readability first appears in
    the DINOv2 chapter.
    """
    v = ds.variants
    n = pd.to_numeric(v["n_approved_this_variant"], errors="coerce").fillna(0)
    flagged = ds.approved_figures["qualityFlag"].fillna("clean").ne("clean")
    flagged_patents = set(ds.approved_figures.loc[flagged, "patent_id"])
    thin = n.eq(1) | v["patent_id"].isin(flagged_patents)
    approved_share = pd.to_numeric(v["n_approved"], errors="coerce") / pd.to_numeric(
        v["n_figures"], errors="coerce"
    )
    return {
        "single_figure_variants": int(n.eq(1).sum()),
        "single_figure_share": round(float(n.eq(1).mean()), 2),
        "median_approved_share_per_patent": round(float(approved_share.median()), 2),
        "sensitivity_set": int(thin.sum()),
        "patents_without_a_whole_vehicle_figure": int(
            len(set(ds.patents_analysis["patent_id"]) - set(
                ds.approved_figures.loc[
                    ds.approved_figures["parts"].astype(str).eq(WHOLE_VEHICLE),
                    "patent_id",
                ]
            ))
        ),
    }


# --------------------------------------------------------------------------
# D13 — flagship check
# --------------------------------------------------------------------------
def d13_flagship_check(ds: Dataset, min_patents: int = 2) -> pd.DataFrame:
    """The labels of the well-known companies against their public products.

    The public side comes from ``known_aircraft_architecture.csv`` (the VFS World
    eVTOL Aircraft Directory); the label side is recomputed. A company whose
    documented aircraft do not all share one architecture is marked, because that
    is exactly the case the automatic exemption of A.4 refuses to decide.
    """
    j = ds.variants.merge(
        ds.identity[["patent_id", "company_canonical"]], on="patent_id", how="left"
    )
    known = ds.known_aircraft
    rows = []
    for company, sub in j.groupby("company_canonical"):
        if company in CATCH_ALL or len(sub) < min_patents:
            continue
        counts = sub["topType"].value_counts()
        entry = {
            "company": company,
            "aircraft": int(len(sub)),
            "labels": " · ".join(
                f"{metrics.ARCH_NAMES.get(k, k)} {v}" for k, v in counts.head(5).items()
            ),
            "distinct types": int(len(counts)),
        }
        if known is not None:
            models = known[known["company"] == company]
            entry["public products"] = " · ".join(
                f"{r.aircraft_name} ({r.known_type})" for r in models.itertuples()
            )
            types = set(models["known_type"])
            entry["public types differ"] = len(types) > 1
            entry["top label matches a public type"] = (
                bool(counts.index[0] in types) if len(counts) and types else None
            )
        rows.append(entry)
    out = pd.DataFrame(rows)
    return out.sort_values("aircraft", ascending=False).reset_index(drop=True)
