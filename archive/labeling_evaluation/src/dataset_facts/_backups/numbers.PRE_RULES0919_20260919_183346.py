"""Every number the document's prose and diagrams quote, measured once.

:func:`live` returns a flat ``{name: value}`` dict. The prose templates in
:mod:`index` and the SVG figures in :mod:`figures` read from it, so a count can
never be typed by hand and the funnel diagram cannot disagree with the tables
beside it. Integers above 999 are also provided as ``<name>_s`` strings with a
space as thousands separator ("1 639"), the way the document prints them.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from . import a1, a2, a3, a5, roster
from .loaders import Dataset


def fmt(n) -> str:
    """1639 -> '1 639'; floats untouched."""
    if isinstance(n, (int,)) or (isinstance(n, float) and float(n).is_integer() and abs(n) >= 1000):
        return f"{int(n):,}".replace(",", " ")
    return str(n)


def live(ds: Dataset, partial_window_start: int = 2024) -> Dict:
    c = ds.counts
    n: Dict = {}
    # ---- the funnel
    n["acquired"] = c["patents_acquired"]
    n["representative"] = c["patents_approved"]
    n["primary"] = c["patents_analysis"]
    n["observations"] = c["approved_variants"]
    n["unique"] = c["primary_approved_variants"]
    n["figures_approved"] = c["approved_figures"]            # whole-aircraft figures: the image set analysed
    n["figures_approved_all"] = c["approved_figures_all"]    # every approved figure, detail figures included
    n["figures_total"] = int(len(ds.figures_rep))            # figures on file of the representative patents
    n["figures_total_all"] = int(len(ds.figures))            # ... of every acquired patent
    n["figures_not_approved"] = n["figures_total"] - n["figures_approved_all"]
    n["wizard_approved"] = c["patents_wizard_approved"]
    n["gated_patents"] = c["patents_gated_out"]
    n["gated_aircraft"] = c["primary_variants_gated_out"]
    n["disapproved"] = n["acquired"] - n["representative"]
    n["disapproved_wizard"] = n["acquired"] - n["wizard_approved"]
    n["rep_share"] = f"{n['representative'] / n['acquired']:.0%}"
    n["wizard_share"] = f"{n['wizard_approved'] / n['acquired']:.0%}"
    reasons = a2.d1_rejection_reasons(ds).set_index("reason")["patents"]
    n["r_noimg"] = int(reasons.get("No Aircraft Image", 0))
    n["r_uav"] = int(reasons.get("Pure UAV", 0))
    n["r_ood"] = int(reasons.get("Out of Domain", 0))
    n["r_sim_uav"] = int(reasons.get("Similar: UAV", 0))
    n["r_sim_el"] = int(reasons.get("Similar: not electric", 0))
    n["r_sim_stol"] = int(reasons.get("Similar: STOL only", 0))
    n["r_sim"] = n["r_sim_uav"] + n["r_sim_el"] + n["r_sim_stol"]
    n["r_other"] = int(reasons.sum() - n["r_noimg"] - n["r_uav"] - n["r_ood"] - n["r_sim"])
    snap = ds.identity["snapshot_date"].dropna()
    n["snapshot"] = str(snap.iloc[0])[:10] if len(snap) else "unknown"
    # ---- similars
    sim = a2.d1_similars(ds).set_index("similar")
    n["uav_n"] = int(sim.loc["UAV-similar", "patents tagged"])
    n["uav_primary"] = int(sim.loc["UAV-similar", "unique aircraft removed"])
    n["stol_n"] = int(sim.loc["STOL-similar", "patents tagged"])
    n["stol_rep"] = int(sim.loc["STOL-similar", "unique aircraft removed"])
    n["vstol_n"], n["vstol_primary"] = sim.attrs["vstol"]
    n["notel_n"] = int(sim.loc["Electric-similar", "patents tagged"])
    n["notel_primary"] = int(sim.loc["Electric-similar", "unique aircraft removed"])
    n["unknown_el"] = int(ds.identity["is_electric_final"].eq("Unknown").sum())
    n["hybrid_el"] = int(ds.identity["is_electric_final"].eq("Hybrid").sum())
    n["stol_note"] = ""
    # ---- filing status
    fs = a2.d1_filing_status(ds).set_index("filing status")
    n["granted_acq"], n["granted_rep"], n["granted_pri"] = fs.attrs["granted"]
    n["pending_acq"] = int(fs.loc["Pending application", "acquired"])
    n["pending_pri"] = int(fs.loc["Pending application", "primary"])
    n["withdrawn_pri"] = int(fs.loc["Withdrawn, refused or suspended", "primary"])
    n["withdrawn_acq"] = int(fs.loc["Withdrawn, refused or suspended", "acquired"])
    # ---- lag
    lag = a2.d9_publication_lag(ds, "region").set_index("region")
    main = lag.loc[["North America", "Asia-Pacific", "Europe"]]
    n["lag_median_lo"], n["lag_median_hi"] = int(main["median lag"].min()), int(main["median lag"].max())
    n["lag_p90"] = int(main["90th percentile"].max())
    n["partial_start"] = partial_window_start
    n["complete_to"] = partial_window_start - 2
    # ---- observations and similars
    dup = a2.d7_duplicates(ds).set_index("type")
    n["o1_obs"] = int(dup.iloc[0]["observations"])
    n["o2_obs"] = int(dup.iloc[1]["observations"])
    n["s3"] = int(dup.iloc[2]["observations"])
    n["s3_identical"] = a2.d7_d3_identical_to_root(ds)["identical_on_all_archetype_fields"]
    pat = ds.patents
    n["o12_patents"] = int((pat["is_representative"].fillna(False).astype(bool) & pat["dup_type"].isin([1, 2])).sum())
    per = a2.d7_aircraft_per_patent(ds)
    n["multi_patents"] = int(per.loc[per["aircraft drawn in the patent"] > 1, "patents"].sum())
    n["max_aircraft"] = int(per["aircraft drawn in the patent"].max())
    # ---- figures
    fp = a2.d11_figure_patents(ds).set_index("patents")
    n["fig_patents"] = int(fp.iloc[0]["count"])
    n["o1_fig_patents"] = int(fp.iloc[2]["count"])
    n["odd_fig_patents"] = int(fp.iloc[4]["count"])
    n["odd_fig_ids"] = str(fp.iloc[4]["note"]).replace(" - to review", "")
    if n["odd_fig_patents"]:
        n["odd_note"] = (f" and {n['odd_fig_patents']} {'is a' if n['odd_fig_patents'] == 1 else 'are'} "
                         f"disapproved patent{'s' if n['odd_fig_patents'] > 1 else ''} ({n['odd_fig_ids']}) "
                         "that still hold" + ("s" if n["odd_fig_patents"] == 1 else "") +
                         " an approved figure, a contradiction to review")
    else:
        n["odd_note"] = ""
    fa = a2.d11_figure_approval(ds).set_index("figures")["count"]
    n["whole_vehicle"] = int(fa.get("  approved, shows: Whole Vehicle Layout", 0))
    n["detail_figs"] = n["figures_approved_all"] - n["whole_vehicle"]
    figs_per = a2.d11_figures_per_variant(ds).set_index("approved figures behind the aircraft")["unique aircraft"]
    n["single_fig"] = int(figs_per.get("1 figure", 0))
    n["single_share"] = f"{n['single_fig'] / n['unique']:.0%}"
    n["median_figs"] = int(pd.to_numeric(ds.variants["n_approved_this_variant"], errors="coerce").median())
    n["t2_slots"] = int(len(a2.d2_figure_slots(ds)))
    # ---- flags
    ros = roster.analysis_set(ds, partial_window_start)
    rc = roster.counts(ros)
    n["sens"] = rc["in_sensitivity_set"]
    n["sens_share"] = f"{rc['in_sensitivity_set'] / rc['aircraft_entering']:.0%}"
    n["noflag"] = rc["without_any_flag"]
    n["any_flag"] = rc["aircraft_entering"] - rc["without_any_flag"]
    n["quality_flagged"] = int(ros["quality_flagged"].sum())
    n["readability"] = int(ros["readability_impossible"].sum())
    # ---- provenance and filers
    reg = a2.d1_approval_by_region(ds).set_index("region")
    n["na_share"] = f"{reg.loc['North America', 'patents'] / n['acquired']:.0%}"
    n["na_rep_share"] = f"{reg.loc['North America', 'representative share']:.2f}"
    n["ap_rep_share"] = f"{reg.loc['Asia-Pacific', 'representative share']:.2f}"
    n["eu_rep_share"] = f"{reg.loc['Europe', 'representative share']:.2f}"
    mix = a2.d8_filer_mix(ds)
    n["individual"] = int(mix.iloc[0]["patents"])
    n["unattributed"] = int(mix.iloc[1]["patents"])
    n["named"] = int(mix.iloc[2]["patents"])
    n["named_companies"] = int(mix.iloc[2]["filer"].split("(")[1].split(" ")[0])
    n["non_corporate_share"] = f"{(n['individual'] + n['unattributed']) / n['primary']:.0%}"
    conc = a2.d8_concentration(ds).set_index("concentration measure")
    n["hhi_raw"] = conc.loc["HHI", "on the raw assignee string"]
    n["bell"] = str(conc.loc["Largest filer", "on the canonical company"]).split(", ")[-1]
    n["bell_raw"] = str(conc.loc["Largest filer", "on the raw assignee string"]).split(", ")[-1]
    names = a1.aircraft_names(ds)
    n["names"] = names["name_proposals"]
    try:
        prop = a5.name_proposals(ds).set_index("value")["count"]
        n["gazetteer"], n["sbert"] = int(prop.get("gazetteer", 0)), int(prop.get("sbert", 0))
    except Exception:
        n["gazetteer"], n["sbert"] = 0, 0
    # ---- label set
    ls = a2.d2_label_set(ds).set_index("property of the label set")["value"]
    n["slots"] = int(ls.iloc[0]); n["concepts"] = int(ls.iloc[1])
    n["median_slots"] = int(ls["Slots answered per aircraft, median"])
    n["slots_gt90"] = int(ls["Slots answered on more than 90 % of aircraft"])
    n["slots_lt5"] = int(ls["Slots answered on fewer than 5 % of aircraft"])
    n["informative"] = int(ls["Fields that carry the information"])
    n["near_constant"] = int(ls.iloc[-2])
    dd = ds.data_dictionary.set_index("column")["section"]
    slots = a2.answerable_slots(ds)
    for card in ("G1", "M1", "M2", "M3"):
        n[f"slots_{card}"] = sum(1 for s in slots if dd.get(s) == card)
    # ---- archetypes
    arch = a2.d5_archetype_cardinality(ds).set_index("level")
    n["n_arch"] = int(arch.iloc[0]["aircraft"])
    n["five_pct"] = int(round(0.05 * n["n_arch"]))
    for lvl in arch.index:
        key = lvl.lower()
        n[f"{key}_single"] = int(arch.loc[lvl, "singletons"])
        n[f"{key}_distinct"] = int(arch.loc[lvl, "distinct archetypes"])
        n[f"{key}_eff"] = float(arch.loc[lvl, "effective number"])
    af = a2.archetype_frame(ds)
    n["booms_answers"] = int(af["nBooms"].nunique())
    n["booms_top_share"] = f"{af['nBooms'].value_counts(normalize=True).iloc[0]:.2f}"
    n["tilt_n"] = int(af["anyTilt"].sum())
    bal = a2.d3_architecture_balance(ds)
    n["n_classes"] = int(len(bal))
    n["top_class"] = str(bal.iloc[0]["name"])
    n["top_class_share"] = f"{bal.iloc[0]['share']:.2f}"
    n["small_classes"] = int((bal["count"] < 12).sum())
    win = a2.d9_architecture_by_window(ds)
    n["max_window_share"] = f"{win.attrs['max_share_any_class_any_window']:.2f}"
    n["min_window"] = int(win["unique aircraft"].iloc[:-1].min())
    n["window_counts"] = ", ".join(str(int(x)) for x in win["unique aircraft"].iloc[:-1]) + \
        f" and {int(win['unique aircraft'].iloc[-1])}"
    years = pd.to_numeric(ds.identity.loc[ds.identity["patent_id"].isin(
        set(ds.patents_analysis["patent_id"])), "priority_year"], errors="coerce")
    n["year_min"], n["year_max"] = int(years.min()), int(years.max())
    n["year_span"] = n["year_max"] - n["year_min"]
    # Bell / Textron behind the tilt-rotor company subset (5.6)
    jj = ds.variants.merge(ds.identity[["patent_id", "company_canonical"]], on="patent_id", how="left")
    tr_named = jj[jj["topType"].eq("TR") & ~jj["company_canonical"].isin(a2.CATCH_ALL)
                  & jj["company_canonical"].notna()]
    n["bell_tr"] = int(tr_named["company_canonical"].eq("Bell / Textron").sum())
    n["tr_named"] = int(len(tr_named))
    n["bell_tr_share"] = f"{n['bell_tr'] / n['tr_named']:.0%}" if n["tr_named"] else "0%"
    n["bell_strings"] = int(len(a2.d8_split_firms(ds, "Bell / Textron")))
    der = a3.derived_layer_summary(ds).set_index("derived variable")["value"]
    n["units_median"] = der.iloc[0]
    fl = a2.d13_flagship_check(ds)
    n["flagship_companies"] = int(len(fl))
    if "public products" in fl:
        pub = fl[fl["public products"].astype(str).str.len() > 0]
        n["flagship_public"] = int(len(pub))
        n["flagship_match"] = int(pub["top label matches a public type"].fillna(False).astype(bool).sum())
    # ---- string forms with the thousands space
    for k, v in list(n.items()):
        if isinstance(v, (int,)) and not isinstance(v, bool):
            n[f"{k}_s"] = fmt(v)
    return n
