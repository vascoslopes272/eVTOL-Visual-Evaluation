"""A.1 — where each information source stands, and the time coverage.

One function per row of the source table, plus :func:`source_state_table` which
assembles them into the table the document prints. Each function returns the
counts it measured, so a changed pipeline shows up as a changed number rather
than as stale prose.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from . import metrics
from .loaders import Dataset

#: the T2 value that says a figure shows the whole aircraft. `arch` in
#: master_figures.xlsx is a count of aircraft in the figure, not a scope label.
WHOLE_VEHICLE = "Whole Vehicle Layout"


# --------------------------------------------------------------------------
# individual sources
# --------------------------------------------------------------------------
def image_labels(ds: Dataset) -> Dict:
    """Row 1: the wizard image labels — the dataset itself."""
    c = ds.counts
    approved = ds.approved_variants.groupby("patent_id").size()
    primary = ds.variants.groupby("patent_id").size()
    return {
        **c,
        "patents_rejected": c["patents_acquired"] - c["patents_approved"],
        "master_rows": int(len(ds.master)),
        "master_columns": int(ds.master.shape[1]),
        # over every approved patent, duplicates included
        "patents_with_several_variants": int((approved > 1).sum()),
        # over the analysis set only — the number A.4 works with
        "analysis_patents_with_several_variants": int((primary > 1).sum()),
    }


def electric(ds: Dataset) -> pd.DataFrame:
    """Row 2: the electric gate — verdicts and the evidence each rests on."""
    verdict = metrics.share_table(ds.identity["is_electric"])
    source = metrics.share_table(ds.identity["is_electric_source"])
    verdict["kind"] = "verdict"
    source["kind"] = "evidence"
    return pd.concat([verdict, source], ignore_index=True)[
        ["kind", "value", "count", "share"]
    ]


def takeoff(ds: Dataset) -> Dict:
    """Row 3: VTOL / V/STOL / STOL, and how many carry a quote."""
    counts = ds.identity["takeoff_mode"].value_counts(dropna=False)
    return {
        **{str(k): int(v) for k, v in counts.items()},
        "with_quote": int(ds.identity["takeoff_quote"].notna().sum()),
    }


def architecture_from_text_prelabel(ds: Dataset) -> Dict:
    """Row 4: the retired SBERT/keyword text guess, measured against the images.

    Compared on the approved patents that show a **single** architecture, which
    is the only fair comparison: the guess names one type per patent.
    """
    ident = ds.identity.set_index("patent_id")
    per_patent = (
        ds.variants.groupby("patent_id")["topType"].agg(lambda s: set(s.dropna()))
    )
    single = per_patent[per_patent.apply(len) == 1]

    image = single.apply(lambda s: next(iter(s)))
    guess = ident.reindex(image.index)["architecture_primary"]
    src = ident.reindex(image.index)["architecture_source"]

    out = dict(metrics.agreement(image, guess))
    for source in ("keyword", "sbert"):
        mask = src.eq(source)
        sub = metrics.agreement(image[mask.to_numpy()], guess[mask.to_numpy()])
        out[f"{source}_n"] = sub["n"]
        out[f"{source}_agreement"] = sub["agreement"]

    # the guess also lists every type it detects (as display labels, not ids):
    # is the image type in that list?
    id_to_label = (
        ds.identity.dropna(subset=["architecture_primary"])
        .drop_duplicates("architecture_primary")
        .set_index("architecture_primary")["architecture_primary_label"]
        .to_dict()
    )
    all_types = ident.reindex(image.index)["architecture_all"].fillna("")
    listed = [
        id_to_label.get(img, img) in {t.strip() for t in row.split(";") if t.strip()}
        for img, row in zip(image, all_types)
    ]
    out["types_listed_per_patent"] = round(
        float(ds.identity["architecture_count"].mean()), 1
    )
    out["image_type_is_listed"] = round(float(np.mean(listed)), 3)
    out["cvt_is_the_guess_for"] = int(
        (ds.identity["architecture_primary"] == "CVT").sum()
    )
    # the two types the text vocabulary cannot express at all
    out["TB_or_PTC_approved_rows"] = int(
        ds.approved_variants["topType"].isin(["TB", "PTC"]).sum()
    )
    out["TB_or_PTC_analysis_variants"] = int(
        ds.variants["topType"].isin(["TB", "PTC"]).sum()
    )
    return out


def scope(ds: Dataset) -> Dict:
    """Row 5: scope — machine only, and not derivable from the figure labels."""
    counts = ds.identity["scope"].value_counts(dropna=False)
    figs = ds.approved_figures
    whole = figs["parts"].astype(str).eq(WHOLE_VEHICLE)
    return {
        **{str(k): int(v) for k, v in counts.items()},
        "sbert_sourced": int((ds.identity["scope_source"] == "sbert").sum()),
        "approved_figures": int(len(figs)),
        "approved_figures_whole_vehicle": int(whole.sum()),
    }


def mission(ds: Dataset) -> pd.DataFrame:
    """Row 6: mission type — parked, 809 of 1,639 are General_Unspecified."""
    return metrics.share_table(ds.identity["industry_primary"])


def specs(ds: Dataset) -> pd.DataFrame:
    """Row 7: the specification columns are empty; patents do not state them."""
    cols = ["pax", "mtow_kg", "range_km", "cruise_speed_kmh", "max_speed_kmh",
            "endurance_min", "payload_kg"]
    return pd.DataFrame(
        [{"field": c, "non_empty": int(ds.identity[c].notna().sum())} for c in cols]
    )


def metadata(ds: Dataset) -> Dict:
    """Row 8: the PatSeer metadata that is ready to use."""
    ident = ds.identity
    return {
        "priority_year_present": int(ident["priority_year"].notna().sum()),
        **{f"legal_{k}": int(v) for k, v in ident["legal_stage"].value_counts().items()},
        **{f"region_{k}": int(v) for k, v in ident["region"].value_counts().items()},
    }


def assignee_type(ds: Dataset) -> pd.DataFrame:
    """Row 9: assignee type does not exist as a column — the crude suffix heuristic.

    Reproduces the "about 1,050 company / 33 university / about 580 unresolved"
    of the document. It is a placeholder for the real classification of plan
    line G8, not a variable to analyse.
    """
    UNIVERSITY = ("univ", "college", "institute of technology", "polytech", "school",
                  "academy", "universit")
    COMPANY = (" inc", " inc.", " llc", " ltd", " limited", " corp", " co.", " gmbh",
               " s.a", " sa", " ag", " bv", " b.v", " kg", " plc", " company",
               " technologies", " aviation", " aerospace", " systems", " group",
               " holdings", " industries", " aircraft", " motors", " labs")
    raw = ds.identity["assignee_raw"].fillna("").astype(str).str.lower()

    def classify(name: str) -> str:
        if not name.strip():
            return "unresolved"
        if any(k in name for k in UNIVERSITY):
            return "university"
        if any(name.endswith(k.strip()) or k in name for k in COMPANY):
            return "company"
        return "unresolved"

    return metrics.share_table(raw.map(classify))


def aircraft_names(ds: Dataset) -> Dict:
    """Row 10: name proposals per patent and per variant."""
    ident = ds.identity
    analysis = ident[ident["patent_id"].isin(ds.patents_analysis["patent_id"])]
    link = ident["aircraft_link"].value_counts()
    link_a = analysis["aircraft_link"].value_counts()
    return {
        "name_proposals": int(ident["aircraft_name"].notna().sum()),
        "link_Depicted": int(link.get("Depicted", 0)),
        "link_CompanyAttributed": int(link.get("CompanyAttributed", 0)),
        "link_empty": int(ident["aircraft_link"].isna().sum()),
        "analysis_Depicted": int(link_a.get("Depicted", 0)),
        "analysis_CompanyAttributed": int(link_a.get("CompanyAttributed", 0)),
        "analysis_empty": int(analysis["aircraft_link"].isna().sum()),
        "wizard_name_filled_on_variants": int(
            ds.variants["aircraft_name"].notna().sum()
        ),
    }


# --------------------------------------------------------------------------
# the inclusion gates (index 1.2) and the provenance tables (index 3.1)
# --------------------------------------------------------------------------
#: (gate, machine column, column after the annotator's review)
GATES = [
    ("electric", "is_electric", "is_electric_final"),
    ("take-off", "takeoff_mode", "takeoff_final"),
    ("UAV", "uav_hint", "uav_final"),
]


def inclusion_gates(ds: Dataset, analysis_only: bool = False) -> pd.DataFrame:
    """The three inclusion gates, machine verdict against the state after review.

    One row per gate and value; ``machine`` is the Stage 03a pipeline column,
    ``after review`` the ``*_final`` column that carries the annotator's decisions
    on top of it. The two UAV columns use different vocabularies (the hint says
    ``UAV`` / ``UAV-language``, the final says ``UAVSimilar``), so they are
    listed side by side rather than matched value by value.
    """
    ident = ds.identity
    if analysis_only:
        ident = ident[ident["patent_id"].isin(ds.patents_analysis["patent_id"])]
    rows = []
    for gate, machine_col, final_col in GATES:
        machine = ident[machine_col].fillna("(blank)").value_counts()
        final = ident[final_col].fillna("(blank)").value_counts()
        for value in sorted(set(machine.index) | set(final.index), key=str):
            rows.append({
                "gate": gate,
                "value": value,
                "machine": int(machine.get(value, 0)),
                "after review": int(final.get(value, 0)),
            })
    return pd.DataFrame(rows)


def provenance_tables(ds: Dataset, top_offices: int = 10) -> Dict[str, pd.DataFrame]:
    """Region, assignee country and publication office, patents and approval rate."""
    j = ds.patents.merge(
        ds.identity[["patent_id", "region", "assignee_country", "pub_office"]],
        on="patent_id", how="left",
    )
    approved = j["is_approved"].fillna(False).astype(bool)
    out = {}
    for key in ("region", "assignee_country", "pub_office"):
        g = j.assign(approved=approved).groupby(key).agg(
            patents=("patent_id", "size"), approved=("approved", "sum")
        )
        g["approval_rate"] = (g["approved"] / g["patents"]).round(2)
        g = g.sort_values("patents", ascending=False).reset_index()
        if key != "region":
            g = g.head(top_offices)
        out[key] = g
    return out


# --------------------------------------------------------------------------
# the table
# --------------------------------------------------------------------------
def source_state_table(ds: Dataset) -> pd.DataFrame:
    """The A.1 table: one row per information source, state recomputed."""
    img = image_labels(ds)
    ele = ds.identity["is_electric"].value_counts()
    tak = takeoff(ds)
    arc = architecture_from_text_prelabel(ds)
    sco = scope(ds)
    mis = ds.identity["industry_primary"].value_counts()
    spe = specs(ds).set_index("field")["non_empty"]
    met = metadata(ds)
    asg = assignee_type(ds).set_index("value")["count"]
    nam = aircraft_names(ds)

    rows = [
        ("Image labels G1-M3 (wizard, 5 batches)", "Yes",
         f"{img['patents_acquired']:,} patents; {img['patents_approved']:,} approved / "
         f"{img['patents_rejected']:,} rejected; {img['primary_approved_variants']} primary "
         f"approved variants; master {img['master_rows']:,} x {img['master_columns']}; "
         f"{img['patents_with_several_variants']} patents carry more than one variant",
         "Ready. This is the dataset."),
        ("Electric or not (03a)", "Yes, machine",
         " · ".join(f"{k} {v}" for k, v in ele.items()),
         "Priority 1 - inclusion gate."),
        ("VTOL or STOL (03a)", "Yes, machine",
         f"VTOL {tak.get('VTOL', 0)} · V/STOL {tak.get('V/STOL', 0)} · STOL {tak.get('STOL', 0)} "
         f"· blank {tak.get('nan', 0)}; quote for {tak['with_quote']}",
         "Priority 1. DECIDE what V/STOL means for inclusion."),
        ("Architecture from the TEXT (03a architecture_primary)", "Yes, but a guess",
         f"agrees with the image label on {arc['agreement']:.1%} of {arc['n']} single-type "
         f"approved patents (kappa {arc['kappa']}); keyword {arc['keyword_agreement']:.1%} "
         f"of {arc['keyword_n']}, SBERT {arc['sbert_agreement']:.1%} of {arc['sbert_n']}; "
         f"{arc['types_listed_per_patent']} types listed per patent, image type among them "
         f"{arc['image_type_is_listed']:.1%}",
         "Not a gold standard. Superseded by the reading pass of A.4."),
        ("Scope (whole aircraft / subsystem / component)", "Yes, machine",
         " · ".join(f"{k} {v}" for k, v in ds.identity["scope"].value_counts().items())
         + f"; {sco['sbert_sourced']} SBERT, none reviewed",
         "Not a gate, and not derivable from the figure labels "
         f"({sco['approved_figures_whole_vehicle']:,} of {sco['approved_figures']:,} approved "
         "figures are Whole Vehicle Layout by construction)."),
        ("Mission type (industry_primary)", "Yes, weak",
         f"{mis.get('General_Unspecified', 0)} of {img['patents_acquired']:,} are "
         f"General_Unspecified; the rest split over {mis.size - 1} industries",
         "Park it."),
        ("Specs (pax, MTOW, range, speed)", "Almost empty",
         f"pax {spe['pax']} · MTOW {spe['mtow_kg']} · range {spe['range_km']} · "
         f"cruise speed {spe['cruise_speed_kmh']} non-empty",
         "Out of scope - confirmed by the data."),
        ("Metadata (PatSeer via 03a)", "Yes",
         f"priority_year for all {met['priority_year_present']:,}; Granted "
         f"{met.get('legal_Granted', 0):,} / Application {met.get('legal_Application', 0)}; "
         f"N. America {met.get('region_North America', 0)} · Asia-Pacific "
         f"{met.get('region_Asia-Pacific', 0)} · Europe {met.get('region_Europe', 0)}",
         "Ready."),
        ("Assignee type (company / university / individual)", "No",
         f"not a column anywhere; suffix heuristic gives {asg.get('company', 0):,} company / "
         f"{asg.get('university', 0)} university / {asg.get('unresolved', 0)} unresolved",
         "Cheap to add, high value. Plan line G8."),
        ("Real aircraft name (03a)", "Yes, proposals",
         f"{nam['name_proposals']} proposals; aircraft_link Depicted {nam['link_Depicted']} · "
         f"CompanyAttributed {nam['link_CompanyAttributed']} · empty {nam['link_empty']:,}; "
         f"on the analysis patents {nam['analysis_Depicted']} / "
         f"{nam['analysis_CompanyAttributed']} / {nam['analysis_empty']}",
         "Only matters for a named-aircraft sub-analysis. Not a gate."),
    ]
    return pd.DataFrame(rows, columns=["source", "exists", "state", "verdict"])


# --------------------------------------------------------------------------
# time coverage
# --------------------------------------------------------------------------
def time_coverage(ds: Dataset) -> pd.DataFrame:
    """Approved primary patents per priority year — why pre-2016 needs windows."""
    joined = ds.patents_analysis.merge(
        ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left"
    )
    counts = joined["priority_year"].dropna().astype(int).value_counts().sort_index()
    return pd.DataFrame({"priority_year": counts.index, "patents": counts.to_numpy()})


def time_coverage_summary(ds: Dataset) -> pd.DataFrame:
    """The three sentences of the document, as a table: max per year per era."""
    cov = time_coverage(ds).set_index("priority_year")["patents"]
    eras = {"1999-2011": range(1999, 2012), "2012-2015": range(2012, 2016),
            "2016-2024": range(2016, 2025), "2025+": range(2025, 2030)}
    rows = []
    for name, years in eras.items():
        sub = cov[cov.index.isin(list(years))]
        rows.append({
            "era": name,
            "years_present": int(len(sub)),
            "patents": int(sub.sum()),
            "min_per_year": int(sub.min()) if len(sub) else 0,
            "max_per_year": int(sub.max()) if len(sub) else 0,
        })
    return pd.DataFrame(rows)
