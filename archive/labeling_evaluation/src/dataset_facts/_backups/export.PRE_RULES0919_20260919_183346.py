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

from . import a1, a2, a3, a4, a5, a6, ch5, numbers, published, roster, rules
from .loaders import Dataset


def _dict_table(d: Dict, key: str = "measure", value: str = "value") -> pd.DataFrame:
    return pd.DataFrame([{key: k, value: v} for k, v in d.items()])


def md_safe(table: pd.DataFrame) -> pd.DataFrame:
    """A copy fit for ``to_markdown``: index reset, nullable ``<NA>`` shown as blank."""
    t = table
    if isinstance(t.index, pd.MultiIndex) or t.index.name is not None:
        t = t.reset_index()
    return t.astype(object).where(t.notna(), "")


def build_all(ds: Dataset, facts: Optional[Dict] = None,
              partial_window_start: Optional[int] = None) -> Dict[str, pd.DataFrame]:
    """Every table, keyed by the name the index uses.

    ``facts`` is the ``dataset_facts`` block of config.yaml (paths of the
    conformance harness and of the before/after exports, the partial-window
    start, the legacy 02a glob). Missing keys just leave those tables out.
    """
    facts = facts or {}
    partial_window_start = partial_window_start or facts.get("partial_window_start", 2024)
    prov = a1.provenance_tables(ds)
    slots = a2.d2_slots_per_aircraft(ds)
    ros = roster.analysis_set(ds, partial_window_start)
    windows = a2.d9_architecture_by_window(ds)
    live = numbers.live(ds, partial_window_start)

    tables: Dict[str, pd.DataFrame] = {
        # ---- index 1
        "a2_d1_funnel": a2.d1_funnel(ds),
        "a2_d1_rejection_reasons": a2.d1_rejection_reasons(ds),
        "a2_d1_approval_by_region": a2.d1_approval_by_region(ds),
        "a2_d1_rejection_by_region": a2.d1_rejection_by_region(ds),
        "a2_d1_rejection_by_filer_type": a2.d1_rejection_by_filer_type(ds),
        "a1_inclusion_gates": a1.inclusion_gates(ds),
        "a1_inclusion_gates_analysis": a1.inclusion_gates(ds, analysis_only=True),
        "a2_d1_similars": a2.d1_similars(ds),
        "a2_d1_filing_status": a2.d1_filing_status(ds),
        "a2_d7_duplicates": a2.d7_duplicates(ds),
        "a2_d7_d3_identical": _dict_table(a2.d7_d3_identical_to_root(ds)),
        "a2_d7_d3_rows": a2.d7_d3_rows(ds),
        "a2_d7_aircraft_per_patent": a2.d7_aircraft_per_patent(ds),
        "a2_d4_missingness": a2.d4_missingness(ds),
        "a2_d6_weak_labels": a2.d6_weak_labels(ds),
        "roster": ros,
        "roster_summary": roster.summary(ros),
        "roster_summary_short": roster.summary(ros).set_index("flag").loc[
            ["single_figure", "quality_flagged", "in_sensitivity_set", "notPureArch",
             "g1_uncertain", "any_flag"]].reset_index(),
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
        "a2_d9_windows": windows[["window", "unique aircraft"]],
        # ---- index 2
        "a2_d2_label_set": a2.d2_label_set(ds),
        "a2_d2_figure_slots": a2.d2_figure_slots(ds),
        "a2_d2_figure_slot_answers": a2.d2_figure_slot_answers(ds),
        "a2_d11_figures_per_variant": a2.d11_figures_per_variant(ds),
        "a2_d11_figure_quality": a2.d11_figure_quality(ds),
        "a2_d11_figure_approval": a2.d11_figure_approval(ds),
        "a2_d11_figure_patents": a2.d11_figure_patents(ds),
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
        # ---- chapter 5 and every number the prose and the diagrams quote
        "ch5_settings": ch5.settings_table(live),
        "ch5_judgement": ch5.judgement_table(live),
        "numbers": _dict_table({k: v for k, v in live.items() if not k.endswith("_s")}, key="name"),
        # ---- framework document (appendix)
        "a1_source_state": a1.source_state_table(ds),
        "published_check": published.check(ds),
    }
    # ---- index 4.3: the codebook's own rules, before and after correction
    if facts.get("conformance_dir") and facts.get("rules_stages"):
        counts = rules.codebook_rule_counts(
            facts["conformance_dir"], facts["rules_stages"],
            facts.get("batches", ["Batch_01", "Batch_02", "Batch_03", "Batch_04", "Batch_05"]))
        tables["rules_codebook"] = counts
        tables["rules_codebook_by_rule"] = rules.codebook_by_rule(counts)
        tables["rules_codebook_by_batch"] = rules.codebook_by_batch(counts)
    # the legacy 02a sidecars, for the record only
    if facts.get("rule_decisions_glob"):
        counts = rules.d12_rule_counts(facts["rule_decisions_glob"])
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
        (out_dir / f"{name}.md").write_text(md_safe(table).to_markdown(index=False), encoding="utf-8")
        rows.append({"table": name, "rows": len(table), "file": f"tables/{name}.csv"})
    return pd.DataFrame(rows)


def markdown_tables(tables: Dict[str, pd.DataFrame], only: str | None = None) -> str:
    """Render tables as markdown pipe tables, for pasting into a document."""
    parts = []
    for name, table in tables.items():
        if only and not name.startswith(only):
            continue
        parts.append(f"**{name}**\n\n{md_safe(table).to_markdown(index=False)}\n")
    return "\n".join(parts)
