"""Every number Part A states, as it was printed, and a check against the live data.

The document is
``Drive_files_to_syncronize/eVTOL_Methodology_Framework_v2_ANNOTATED_20260909.md``
(issue of 2026-09-10). This module is the only place in the package that holds a
hard-coded value: everything else is measured. :func:`check` recomputes each one
and says whether the document still matches the dataset, which is what makes the
document re-issuable after the labels change.

A ``drift`` row is not a bug. It means the dataset moved after the document was
written and the sentence has to be updated — or, where the note says so, that the
document's definition was wrong and this package uses the corrected one.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from . import a1, a2, a3, a4, a5, a6
from .loaders import Dataset

#: (section, what the document says, published value, how to recompute it, note)
PUBLISHED: List[Dict[str, Any]] = [
    # ---- A.1 ------------------------------------------------------------
    dict(section="A.1", fact="patents acquired", value=1639,
         fn=lambda ds: ds.counts["patents_acquired"]),
    dict(section="A.1", fact="patents approved", value=1110,
         fn=lambda ds: ds.counts["patents_wizard_approved"],
         note="the wizard's approval; since 2026-09-15 the Similar tags gate the analysis set further"),
    dict(section="A.1", fact="primary approved variants", value=805,
         fn=lambda ds: ds.counts["primary_approved_variants"]),
    dict(section="A.1", fact="master sheet rows", value=1797,
         fn=lambda ds: len(ds.master)),
    dict(section="A.1", fact="master sheet columns", value=435,
         fn=lambda ds: ds.master.shape[1],
         note="435 is the 04 master; the batch reader carries no *_otherTag columns (415)"),
    dict(section="A.1", fact="patents with more than one variant", value=98,
         fn=lambda ds: a1.image_labels(ds)["patents_with_several_variants"],
         note="over every approved patent; over the 695 analysis patents it is 68 (A.4)"),
    dict(section="A.1", fact="electric: Yes", value=902,
         fn=lambda ds: int((ds.identity["is_electric"] == "Yes").sum()),
         note="measured before the burden-of-proof rewrite of the electric rule"),
    dict(section="A.1", fact="electric: Hybrid", value=167,
         fn=lambda ds: int((ds.identity["is_electric"] == "Hybrid").sum()),
         note="same rewrite"),
    dict(section="A.1", fact="electric: No", value=74,
         fn=lambda ds: int((ds.identity["is_electric"] == "No").sum()),
         note="same rewrite"),
    dict(section="A.1", fact="take-off: VTOL", value=1381,
         fn=lambda ds: a1.takeoff(ds).get("VTOL", 0)),
    dict(section="A.1", fact="take-off: V/STOL", value=195,
         fn=lambda ds: a1.takeoff(ds).get("V/STOL", 0)),
    dict(section="A.1", fact="text pre-label agreement with the images", value=0.257,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["agreement"]),
    dict(section="A.1", fact="text pre-label kappa", value=0.13,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["kappa"]),
    dict(section="A.1", fact="text pre-label: keyword agreement", value=0.396,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["keyword_agreement"]),
    dict(section="A.1", fact="text pre-label: SBERT agreement", value=0.178,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["sbert_agreement"]),
    dict(section="A.1", fact="image type appears in the text's list", value=0.488,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["image_type_is_listed"]),
    dict(section="A.1", fact="CVT is the text guess for", value=437,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["cvt_is_the_guess_for"]),
    dict(section="A.1", fact="TB + PTC rows the text vocabulary cannot express", value=107,
         fn=lambda ds: a1.architecture_from_text_prelabel(ds)["TB_or_PTC_approved_rows"],
         note="all approved rows; the document says 'approved primary rows', where it is 66"),
    dict(section="A.1", fact="scope: subsystem enabler", value=1371,
         fn=lambda ds: int((ds.identity["scope"] == "Architectural Subsystem Enabler").sum())),
    dict(section="A.1", fact="approved figures that are Whole Vehicle Layout", value=1891,
         fn=lambda ds: a1.scope(ds)["approved_figures_whole_vehicle"]),
    dict(section="A.1", fact="mission: General_Unspecified", value=809,
         fn=lambda ds: int((ds.identity["industry_primary"] == "General_Unspecified").sum())),
    dict(section="A.1", fact="specs: pax non-empty", value=10,
         fn=lambda ds: int(ds.identity["pax"].notna().sum())),
    dict(section="A.1", fact="legal stage: Granted", value=1110,
         fn=lambda ds: int((ds.identity["legal_stage"] == "Granted").sum())),
    dict(section="A.1", fact="region: North America", value=719,
         fn=lambda ds: int((ds.identity["region"] == "North America").sum())),
    dict(section="A.1", fact="name proposals", value=387,
         fn=lambda ds: a1.aircraft_names(ds)["name_proposals"]),
    dict(section="A.1", fact="aircraft_link Depicted", value=41,
         fn=lambda ds: a1.aircraft_names(ds)["link_Depicted"]),
    dict(section="A.1", fact="wizard name filled on variants", value=728,
         fn=lambda ds: a1.aircraft_names(ds)["wizard_name_filled_on_variants"]),

    # ---- A.2 D1 ---------------------------------------------------------
    dict(section="A.2 D1", fact="approved patents that are the primary record", value=695,
         fn=lambda ds: ds.counts["patents_analysis"]),
    dict(section="A.2 D1", fact="approved aircraft variants", value=1268,
         fn=lambda ds: ds.counts["approved_variants"]),
    dict(section="A.2 D1", fact="approved figures", value=1913,
         fn=lambda ds: ds.counts["approved_figures"]),
    dict(section="A.2 D1", fact="North America approval rate", value=0.78,
         fn=lambda ds: _region(ds, "North America")),
    dict(section="A.2 D1", fact="Asia-Pacific approval rate", value=0.59,
         fn=lambda ds: _region(ds, "Asia-Pacific")),
    dict(section="A.2 D1", fact="Europe approval rate", value=0.61,
         fn=lambda ds: _region(ds, "Europe")),
    dict(section="A.2 D1", fact="rejected: no aircraft image", value=173,
         fn=lambda ds: _reason(ds, "No Aircraft Image")),
    dict(section="A.2 D1", fact="rejected: pure UAV", value=161,
         fn=lambda ds: _reason(ds, "Pure UAV")),
    dict(section="A.2 D1", fact="rejected: out of domain", value=159,
         fn=lambda ds: _reason(ds, "Out of Domain"),
         note="one rejected patent carries no reason at all (CN106494614A)"),

    # ---- A.2 D2 ---------------------------------------------------------
    dict(section="A.2 D2", fact="answerable slots", value=283,
         fn=lambda ds: len(a2.answerable_slots(ds))),
    dict(section="A.2 D2", fact="distinct concepts", value=73,
         fn=lambda ds: a3.concept_count(ds)["concepts"],
         note="the document's collapsing rule was not recorded; a2.concept_of is stated in code"),
    dict(section="A.2 D2", fact="slots answered per aircraft, median", value=37,
         fn=lambda ds: _label_set(ds, "Slots answered per aircraft, median")),
    dict(section="A.2 D2", fact="slots answered on more than 90 %", value=15,
         fn=lambda ds: _label_set(ds, "Slots answered on more than 90 % of aircraft")),
    dict(section="A.2 D2", fact="slots answered on fewer than 5 %", value=184,
         fn=lambda ds: _label_set(ds, "Slots answered on fewer than 5 % of aircraft"),
         note="the document read master_labels.xlsx with pandas defaults, which turn the option ids 'NA' and 'None' into missing; counted as the answers they are, the value differs"),
    dict(section="A.2 D2", fact="near-constant fields", value=15,
         fn=lambda ds: len(a2.d2_near_constant_fields(ds)), note="the document read master_labels.xlsx with pandas defaults, which turn the option ids 'NA' and 'None' into missing; counted as the answers they are, the value differs"),
    dict(section="A.2 D2", fact="fields that carry the information", value=21,
         fn=lambda ds: len(a2.d2_informative_fields(ds)), note="the document read master_labels.xlsx with pandas defaults, which turn the option ids 'NA' and 'None' into missing; counted as the answers they are, the value differs"),
    dict(section="A.2 D2", fact="empType effective answers", value=8.8,
         fn=lambda ds: _eff(ds, "empType")),
    dict(section="A.2 D2", fact="topType effective answers", value=7.1,
         fn=lambda ds: _eff(ds, "topType")),

    # ---- A.2 D3 ---------------------------------------------------------
    dict(section="A.2 D3", fact="Lift + Cruise aircraft", value=222,
         fn=lambda ds: _arch(ds, "SLC")),
    dict(section="A.2 D3", fact="Tilt Rotor aircraft", value=206,
         fn=lambda ds: _arch(ds, "TR")),
    dict(section="A.2 D3", fact="Combined vectored thrust aircraft", value=117,
         fn=lambda ds: _arch(ds, "CVT")),
    dict(section="A.2 D3", fact="largest architecture class share", value=0.28,
         fn=lambda ds: float(a2.d3_architecture_balance(ds)["share"].iloc[0])),
    dict(section="A.2 D3", fact="propulsor groups that are fixed", value=891,
         fn=lambda ds: a2.d3_propulsor_units(ds)["groups_fixed"]),
    dict(section="A.2 D3", fact="propulsor groups that tilt", value=460,
         fn=lambda ds: a2.d3_propulsor_units(ds)["groups_tilting"]),
    dict(section="A.2 D3", fact="aircraft with a ducted unit", value=250,
         fn=lambda ds: a2.d3_propulsor_units(ds)["aircraft_with_a_ducted_unit"]),
    dict(section="A.2 D3", fact="laterally symmetric aircraft", value=769,
         fn=lambda ds: int(ds.variants["latSym"].fillna(False).astype(bool).sum())),

    # ---- A.2 D4 / D5 / D6 / D7 -----------------------------------------
    dict(section="A.2 D4", fact="wings present but wing height blank", value=86,
         fn=lambda ds: _d4(ds, "Wings present but wing height blank")),
    dict(section="A.2 D4", fact="wings present but tail type blank", value=30,
         fn=lambda ds: _d4(ds, "Wings present but tail type blank")),
    dict(section="A.2 D4", fact="architecture type blank", value=3,
         fn=lambda ds: _d4(ds, "Architecture type blank")),
    dict(section="A.2 D5", fact="A1 distinct archetypes", value=63,
         fn=lambda ds: _d5(ds, "A1", "distinct archetypes")),
    dict(section="A.2 D5", fact="A1 singletons", value=14,
         fn=lambda ds: _d5(ds, "A1", "singletons")),
    dict(section="A.2 D5", fact="A2 distinct archetypes", value=223,
         fn=lambda ds: _d5(ds, "A2", "distinct archetypes")),
    dict(section="A.2 D5", fact="A2 singletons", value=92,
         fn=lambda ds: _d5(ds, "A2", "singletons")),
    dict(section="A.2 D6", fact="mixed architecture flag", value=39,
         fn=lambda ds: _d6(ds, "Mixed architecture")),
    dict(section="A.2 D6", fact="annotator unsure at G1", value=35,
         fn=lambda ds: _d6(ds, "Annotator unsure at G1")),
    dict(section="A.2 D6", fact='figure readability "Impossible"', value=38,
         fn=lambda ds: _d6(ds, 'Figure readability "Impossible"')),
    dict(section="A.2 D7", fact="D1 rows", value=38,
         fn=lambda ds: int(ds.master["dup_type"].eq(1).sum())),
    dict(section="A.2 D7", fact="D2 rows", value=425,
         fn=lambda ds: int(ds.master["dup_type"].eq(2).sum())),
    dict(section="A.2 D7", fact="D3 rows, inside the analysis set", value=27,
         fn=lambda ds: int(ds.variants["dup_type"].eq(3).sum())),
    dict(section="A.2 D7", fact="D3 identical to their root on all archetype fields", value=15,
         fn=lambda ds: a2.d7_d3_identical_to_root(ds)["identical_on_all_archetype_fields"]),

    # ---- A.2 D8 ---------------------------------------------------------
    dict(section="A.2 D8", fact="individual inventors", value=211,
         fn=lambda ds: int(a2.d8_filer_mix(ds)["patents"].iloc[0])),
    dict(section="A.2 D8", fact="unattributed or independent", value=152,
         fn=lambda ds: int(a2.d8_filer_mix(ds)["patents"].iloc[1])),
    dict(section="A.2 D8", fact="named-company patents", value=332,
         fn=lambda ds: int(a2.d8_filer_mix(ds)["patents"].iloc[2])),
    dict(section="A.2 D8", fact="distinct raw filers", value=445,
         fn=lambda ds: int(a2.d8_concentration(ds).iloc[0, 1]),
         note="03a was rebuilt after the document was written"),
    dict(section="A.2 D8", fact="raw filers with exactly one patent", value=359,
         fn=lambda ds: int(a2.d8_concentration(ds).iloc[1, 1]), note="same rebuild"),
    dict(section="A.2 D8", fact="top-10 share, raw", value=0.18,
         fn=lambda ds: a2.d8_concentration(ds).iloc[2, 1]),
    dict(section="A.2 D8", fact="HHI, raw", value=0.007,
         fn=lambda ds: a2.d8_concentration(ds).iloc[3, 1]),
    dict(section="A.2 D8", fact="Bell / Textron patents (canonical)", value=66,
         fn=lambda ds: _canonical(ds, "Bell / Textron")),

    # ---- A.2 D9 / D11 ---------------------------------------------------
    dict(section="A.2 D9", fact="Tilt Rotor share, <= 2011", value=0.34,
         fn=lambda ds: _window(ds, "<= 2011", "Tilt Rotor")),
    dict(section="A.2 D9", fact="Lift + Cruise share, 2020-23", value=0.33,
         fn=lambda ds: _window(ds, "2020-23", "Lift + Cruise")),
    dict(section="A.2 D9", fact="North America median publication lag", value=2.0,
         fn=lambda ds: _lag(ds, "North America")),
    dict(section="A.2 D11", fact="variants resting on a single approved figure", value=226,
         fn=lambda ds: a2.d11_sensitivity_set(ds)["single_figure_variants"]),
    dict(section="A.2 D11", fact="median approved figure share per patent", value=0.38,
         fn=lambda ds: a2.d11_sensitivity_set(ds)["median_approved_share_per_patent"]),
    dict(section="A.2 D11", fact="approved figures flagged partial quality", value=8,
         fn=lambda ds: _quality(ds, "Partial quality")),
    dict(section="A.2 D11", fact="approved figures flagged poor quality", value=7,
         fn=lambda ds: _quality(ds, "Poor quality")),
    dict(section="A.2 D11", fact="analysis patents with no whole-aircraft figure", value=0,
         fn=lambda ds: a2.d11_sensitivity_set(ds)["patents_without_a_whole_vehicle_figure"],
         note="refutes the text classifier's claim of 262"),

    # ---- A.3 ------------------------------------------------------------
    dict(section="A.3", fact="total propulsor units, median", value=4,
         fn=lambda ds: a2.d3_propulsor_units(ds)["units_median"]),
    dict(section="A.3", fact="aircraft with more than 8 propulsor units", value=121,
         fn=lambda ds: a2.d3_propulsor_units(ds)["aircraft_with_more_than_8_units"],
         note="the document summed only the four main carriers; this counts every carrier"),
    dict(section="A.3", fact="aircraft with any tilting unit", value=296,
         fn=lambda ds: a2.d3_propulsor_units(ds)["aircraft_with_a_tilting_unit"]),
    dict(section="A.3", fact="aircraft mixing fixed and tilting units", value=111,
         fn=lambda ds: a2.d3_propulsor_units(ds)["aircraft_mixing_fixed_and_tilting"]),
    dict(section="A.3", fact="aircraft whose units are all ducted", value=148,
         fn=lambda ds: a2.d3_propulsor_units(ds)["aircraft_all_units_ducted"]),

    # ---- A.4 ------------------------------------------------------------
    dict(section="A.4", fact="patents whose text states an architecture", value=632,
         fn=lambda ds: int(a4.what_was_done(ds)["patents"].iloc[1])),
    dict(section="A.4", fact="patents whose text does not", value=63,
         fn=lambda ds: int(a4.what_was_done(ds)["patents"].iloc[2])),
    dict(section="A.4", fact="single-type patents stating a type", value=614,
         fn=lambda ds: a4.agreement_with_images(ds)["single_type_patents_stating_a_type"]),
    dict(section="A.4", fact="text-image agreement", value=0.681,
         fn=lambda ds: a4.agreement_with_images(ds)["agreement"],
         note="0.684 over the 611 pairs; 3 quick-override rows carry no image label"),
    dict(section="A.4", fact="text-image kappa", value=0.61,
         fn=lambda ds: a4.agreement_with_images(ds)["kappa"]),
    dict(section="A.4", fact="high-confidence agreement", value=0.79,
         fn=lambda ds: a4.agreement_with_images(ds)["high_agreement"]),
    dict(section="A.4", fact="medium-confidence agreement", value=0.54,
         fn=lambda ds: a4.agreement_with_images(ds)["medium_agreement"]),
    dict(section="A.4", fact="low-confidence agreement", value=0.33,
         fn=lambda ds: a4.agreement_with_images(ds)["low_agreement"]),
    dict(section="A.4", fact="exempted by the known-aircraft rule", value=27,
         fn=lambda ds: int(a4.confirmation_protocol(ds)["rows"].iloc[0])),
    dict(section="A.4", fact="agree, citation to confirm", value=399,
         fn=lambda ds: int(a4.confirmation_protocol(ds)["rows"].iloc[1])),
    dict(section="A.4", fact="text != image, to adjudicate", value=201,
         fn=lambda ds: int(a4.confirmation_protocol(ds)["rows"].iloc[3])),
    dict(section="A.4", fact="screen work", value=608,
         fn=lambda ds: a4.confirmation_protocol(ds).attrs["screen_work"]),
    dict(section="A.4", fact="citations that are verbatim", value=553,
         fn=lambda ds: _citation(ds, "verbatim")),
    dict(section="A.4", fact="citations that are partly verbatim", value=74,
         fn=lambda ds: _citation(ds, "partial")),
    dict(section="A.4", fact="citations not found in the text", value=5,
         fn=lambda ds: _citation(ds, "not_found")),
    dict(section="A.4", fact="patents drawing several aircraft", value=68,
         fn=lambda ds: a4.multi_aircraft_patents(ds).attrs["patents_with_several_aircraft"]),
    dict(section="A.4", fact="variants they contribute", value=178,
         fn=lambda ds: a4.multi_aircraft_patents(ds).attrs["variants_they_contribute"]),
    dict(section="A.4", fact="several aircraft, one architecture", value=50,
         fn=lambda ds: int(a4.multi_aircraft_patents(ds)["patents"].iloc[0])),
    dict(section="A.4", fact="known-aircraft models listed", value=33,
         fn=lambda ds: int(len(ds.known_aircraft))),

    # ---- A.5 ------------------------------------------------------------
    dict(section="A.5", fact="company-attributed names", value=351,
         fn=lambda ds: int((ds.identity["aircraft_name_source"] == "gazetteer").sum())),
    dict(section="A.5", fact="SBERT text hits", value=36,
         fn=lambda ds: int((ds.identity["aircraft_name_source"] == "sbert").sum())),
    dict(section="A.5", fact="companies the gazetteer stamps", value=29,
         fn=lambda ds: a5.gazetteer_by_company(ds).attrs["companies"]),
    dict(section="A.5", fact="Depicted rows that are gazetteer", value=36,
         fn=lambda ds: _link(ds, "Depicted", "gazetteer")),
    dict(section="A.5", fact="03a name queue", value=93,
         fn=lambda ds: int(a5.review_sets(ds)["rows"].iloc[2])),

    # ---- A.6 ------------------------------------------------------------
    dict(section="A.6", fact="take-off carries a citation", value=677,
         fn=lambda ds: _evidence(ds, "take-off mode")),
    dict(section="A.6", fact="powertrain carries a citation", value=477,
         fn=lambda ds: _evidence(ds, "powertrain")),
    dict(section="A.6", fact="powertrain without a citation", value=218,
         fn=lambda ds: int(a6.powertrain_without_evidence(ds)["count"].sum())),
    dict(section="A.6", fact="of those, gazetteer", value=114,
         fn=lambda ds: _no_evidence(ds, "gazetteer")),
    dict(section="A.6", fact="of those, presumed", value=101,
         fn=lambda ds: _no_evidence(ds, "presumed")),
    dict(section="A.6", fact="patents read from text", value=237,
         fn=lambda ds: a6.reading_outcome(ds).attrs["patents_read"]),
    dict(section="A.6", fact="the text settles the powertrain", value=100,
         fn=lambda ds: int(a6.reading_outcome(ds)["patents"].iloc[0])),
    dict(section="A.6", fact="confirms the 03a verdict", value=63,
         fn=lambda ds: int(a6.reading_outcome(ds)["patents"].iloc[1])),
    dict(section="A.6", fact="contradicts the 03a verdict", value=37,
         fn=lambda ds: int(a6.reading_outcome(ds)["patents"].iloc[2])),
    dict(section="A.6", fact="the text never says", value=137,
         fn=lambda ds: int(a6.reading_outcome(ds)["patents"].iloc[3])),
    dict(section="A.6", fact="of those, Alternatives", value=26,
         fn=lambda ds: int(a6.reading_outcome(ds)["patents"].iloc[4])),
    dict(section="A.6", fact="counted electric, by their own words not electric", value=5,
         fn=lambda ds: _contradiction(ds, "No")),
    dict(section="A.6", fact="gazetteer rows that read as hybrid-electric", value=8,
         fn=lambda ds: _contradiction(ds, "Hybrid")),
]


# --------------------------------------------------------------------------
# the small accessors the table above uses
# --------------------------------------------------------------------------
def _region(ds, name):
    t = a2.d1_approval_by_region(ds)
    return float(t.loc[t["region"] == name, "approval_rate"].iloc[0])


def _reason(ds, name):
    t = a2.d1_rejection_reasons(ds)
    hit = t.loc[t["reason"] == name, "patents"]
    return int(hit.iloc[0]) if len(hit) else 0


def _label_set(ds, name):
    return a2.d2_column_stats(ds)[name]


def _eff(ds, field):
    t = a2.d2_informative_fields(ds)
    return float(t.loc[t["field"] == field, "effective_answers"].iloc[0])


def _arch(ds, code):
    t = a2.d3_architecture_balance(ds)
    return int(t.loc[t["value"] == code, "count"].iloc[0])


def _d4(ds, name):
    t = a2.d4_missingness(ds)
    return int(t.loc[t["check"] == name, "affected"].iloc[0])


def _d5(ds, level, col):
    t = a2.d5_archetype_cardinality(ds)
    return int(t.loc[t["level"] == level, col].iloc[0])


def _d6(ds, name):
    t = a2.d6_weak_labels(ds)
    return int(t.loc[t["flag"] == name, "aircraft"].iloc[0])


def _canonical(ds, name):
    j = ds.patents_analysis.merge(
        ds.identity[["patent_id", "company_canonical"]], on="patent_id", how="left"
    )
    return int((j["company_canonical"] == name).sum())


def _window(ds, window, column):
    t = a2.d9_architecture_by_window(ds)
    return float(t.loc[t["window"] == window, column].iloc[0])


def _lag(ds, region):
    t = a2.d9_publication_lag(ds)
    return float(t.loc[t["region"] == region, "median lag"].iloc[0])


def _quality(ds, name):
    t = a2.d11_figure_quality(ds)
    return int(t.loc[t["approved figures"] == name, "count"].iloc[0])


def _citation(ds, name):
    t = a4.citation_quality(ds)
    hit = t.loc[t["value"] == name, "count"]
    return int(hit.iloc[0]) if len(hit) else 0


def _link(ds, link, source):
    t = a5.link_flag(ds)
    hit = t[(t["aircraft_link"] == link) & (t["aircraft_name_source"] == source)]
    return int(hit["patents"].iloc[0]) if len(hit) else 0


def _evidence(ds, name):
    t = a6.evidence_per_variable(ds)
    return int(t.loc[t["variable"] == name, "with a citation"].iloc[0])


def _no_evidence(ds, source):
    t = a6.powertrain_without_evidence(ds)
    hit = t.loc[t["value"] == source, "count"]
    return int(hit.iloc[0]) if len(hit) else 0


def _contradiction(ds, says):
    t = a6.contradiction_summary(ds)
    return int(t.loc[t["the text says"] == says, "patents"].sum())


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------
def check(ds: Dataset, tolerance: float = 0.006) -> pd.DataFrame:
    """Recompute every published number and report match, drift or error.

    ``tolerance`` applies to the rates and shares, which the document rounds.
    """
    rows = []
    for entry in PUBLISHED:
        try:
            live = entry["fn"](ds)
        except Exception as exc:  # a missing input file, not a wrong number
            rows.append({**_row(entry), "live": None, "status": f"error: {exc}"})
            continue
        published = entry["value"]
        if isinstance(published, float):
            ok = live is not None and abs(float(live) - published) <= tolerance
        else:
            ok = live == published
        rows.append({**_row(entry), "live": live, "status": "match" if ok else "drift"})
    out = pd.DataFrame(rows)
    return out[["section", "fact", "published", "live", "status", "note"]]


def _row(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {"section": entry["section"], "fact": entry["fact"],
            "published": entry["value"], "note": entry.get("note", "")}


def summary(ds: Dataset) -> pd.DataFrame:
    """Match / drift / error counts per section."""
    c = check(ds)
    c["state"] = c["status"].str.split(":").str[0]
    return (
        c.groupby(["section", "state"]).size().unstack(fill_value=0).reset_index()
    )
