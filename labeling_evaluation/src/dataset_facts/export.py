"""Write every table to CSV and markdown, so the document can be re-issued from the data.

``build_all(ds)`` returns ``{name: DataFrame}`` for every table the index and the
framework document name; ``write_all`` puts them under the output folder as
``<name>.csv`` and ``<name>.md``; ``markdown_tables`` renders a subset as pipe
tables for pasting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from . import a1, a2, a3, a4, a5, a6, index, published, roster, rules
from .loaders import Dataset


def _dict_table(d: Dict, key: str = "measure", value: str = "value") -> pd.DataFrame:
    return pd.DataFrame([{key: k, value: v} for k, v in d.items()])


def build_all(ds: Dataset, rule_decisions_glob: Optional[str] = None,
              partial_window_start: int = 2024) -> Dict[str, pd.DataFrame]:
    """Every table, keyed by the name the index uses."""
    prov = a1.provenance_tables(ds)
    slots = a2.d2_slots_per_aircraft(ds)
    ros = roster.analysis_set(ds, partial_window_start)
    windows = a2.d9_architecture_by_window(ds)

    tables: Dict[str, pd.DataFrame] = {
        # ---- index 1
        "a2_d1_funnel": a2.d1_funnel(ds),
        "a2_d1_rejection_reasons": a2.d1_rejection_reasons(ds),
        "a2_d1_approval_by_region": a2.d1_approval_by_region(ds),
        "a2_d1_rejection_by_region": a2.d1_rejection_by_region(ds),
        "a2_d1_rejection_by_filer_type": a2.d1_rejection_by_filer_type(ds),
        "a1_inclusion_gates": a1.inclusion_gates(ds),
        "a1_inclusion_gates_analysis": a1.inclusion_gates(ds, analysis_only=True),
        "a2_d7_duplicates": a2.d7_duplicates(ds),
        "a2_d7_d3_identical": _dict_table(a2.d7_d3_identical_to_root(ds)),
        "a2_d7_d3_rows": a2.d7_d3_rows(ds),
        "a2_d7_aircraft_per_patent": a2.d7_aircraft_per_patent(ds),
        "a2_d4_missingness": a2.d4_missingness(ds),
        "a2_d6_weak_labels": a2.d6_weak_labels(ds),
        "roster": ros,
        "roster_summary": roster.summary(ros),
        "roster_counts": _dict_table(roster.counts(ros)),
        "a2_d9_publication_lag_region": a2.d9_publication_lag(ds, "region"),
        "a2_d9_publication_lag_office": a2.d9_publication_lag(ds, "pub_office"),
        "a1_snapshot": _dict_table({
            "snapshot_date": str(ds.identity["snapshot_date"].dropna().iloc[0])
            if ds.identity["snapshot_date"].notna().any() else "(unknown)",
            "partial_window_start": partial_window_start,
        }),
        "a1_time_coverage": a1.time_coverage(ds),
        "a1_time_coverage_summary": a1.time_coverage_summary(ds),
        "a2_d9_windows": windows[["window", "variants"]],
        # ---- index 2
        "a2_d2_label_set": a2.d2_label_set(ds),
        "a2_d2_figure_slots": a2.d2_figure_slots(ds),
        "a2_d11_figures_per_variant": a2.d11_figures_per_variant(ds),
        "a2_d11_figure_quality": a2.d11_figure_quality(ds),
        "a2_d11_sensitivity": _dict_table(a2.d11_sensitivity_set(ds)),
        # ---- index 3
        "a1_provenance_region": prov["region"],
        "a1_provenance_country": prov["assignee_country"],
        "a1_provenance_office": prov["pub_office"],
        "a2_d8_filer_mix": a2.d8_filer_mix(ds),
        "a2_d8_concentration": a2.d8_concentration(ds),
        "a2_d8_single_patent_filers": a2.d8_single_patent_filers(ds),
        "a2_d8_split_firms": a2.d8_split_firms(ds),
        "a1_assignee_type": a1.assignee_type(ds),
        # ---- index 4
        "a2_d2_slots_quantiles": _dict_table({
            "median": int(slots.median()), "lower quartile": int(slots.quantile(0.25)),
            "upper quartile": int(slots.quantile(0.75)), "minimum": int(slots.min()),
            "maximum": int(slots.max()),
        }),
        "a2_d13_flagship_check": a2.d13_flagship_check(ds),
        # ---- index 5
        "a2_d3_selected_fields": a2.d3_selected_fields(ds),
        "a2_d2_near_constant_fields": a2.d2_near_constant_fields(ds),
        "a2_d2_informative_fields": a2.d2_informative_fields(ds),
        "a2_d2_field_inventory": a2.d2_field_inventory(ds),
        "a3_derived_layer_summary": a3.derived_layer_summary(ds),
        "a3_derived_layer": a3.derived_layer(ds),
        "a2_d5_archetype_cardinality": a2.d5_archetype_cardinality(ds),
        "a2_d3_architecture_balance": a2.d3_architecture_balance(ds),
        "a2_d9_architecture_by_window": windows,
        # ---- overview
        "index_feeds": index.feeds_table(),
        # ---- framework document (appendix)
        "a1_source_state": a1.source_state_table(ds),
        "published_check": published.check(ds),
    }
    if rule_decisions_glob:
        counts = rules.d12_rule_counts(rule_decisions_glob)
        tables["rules_d12"] = counts
        tables["rules_d12_by_rule"] = rules.d12_by_rule(counts)

    optional = {
        "a4_what_was_done": a4.what_was_done,
        "a4_agreement_by_type": a4.agreement_by_type,
        "a4_disagreements": a4.disagreements,
        "a4_confusion_matrix": a4.confusion_matrix,
        "a4_confirmation_protocol": a4.confirmation_protocol,
        "a4_citation_quality": a4.citation_quality,
        "a4_known_aircraft": a4.known_aircraft_list,
        "a4_multi_aircraft": a4.multi_aircraft_patents,
        "a5_name_proposals": a5.name_proposals,
        "a5_gazetteer_by_company": a5.gazetteer_by_company,
        "a5_sbert_name_hits": a5.sbert_name_hits,
        "a5_review_sets": a5.review_sets,
        "a6_evidence_per_variable": a6.evidence_per_variable,
        "a6_powertrain_without_evidence": a6.powertrain_without_evidence,
        "a6_reading_outcome": a6.reading_outcome,
        "a6_powertrain_vocabulary": a6.powertrain_vocabulary,
        "a6_contradictions": a6.contradictions,
        "a6_contradiction_summary": a6.contradiction_summary,
        "a6_gazetteer_ambiguous": a6.gazetteer_ambiguous_companies,
    }
    for name, fn in optional.items():
        try:
            tables[name] = fn(ds)
        except FileNotFoundError:
            continue
    return tables


def write_all(tables: Dict[str, pd.DataFrame], out_dir: Path | str) -> pd.DataFrame:
    """Write every table as CSV and markdown. Returns an index of what was written."""
    out_dir = Path(out_dir) / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, table in tables.items():
        t = table.reset_index() if table.index.name is not None or isinstance(
            table.index, pd.MultiIndex) else table
        t.to_csv(out_dir / f"{name}.csv", index=False)
        (out_dir / f"{name}.md").write_text(t.to_markdown(index=False), encoding="utf-8")
        rows.append({"table": name, "rows": len(table), "file": f"tables/{name}.csv"})
    return pd.DataFrame(rows)


def markdown_tables(tables: Dict[str, pd.DataFrame], only: str | None = None) -> str:
    """Render tables as markdown pipe tables, for pasting into a document."""
    parts = []
    for name, table in tables.items():
        if only and not name.startswith(only):
            continue
        t = table.reset_index() if table.index.name is not None else table
        parts.append(f"**{name}**\n\n{t.to_markdown(index=False)}\n")
    return "\n".join(parts)
