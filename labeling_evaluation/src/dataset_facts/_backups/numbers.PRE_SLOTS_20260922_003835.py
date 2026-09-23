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

from . import a1, a2, a3, a5, register, roster
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
    st = ds.figures_rep["status"].astype(str).str.lower()
    n["figures_disapproved"] = int(st.eq("disapproved").sum())
    n["figures_nostatus"] = n["figures_not_approved"] - n["figures_disapproved"]
    n["nostatus_note"] = ""
    if n["figures_nostatus"]:
        odd = ds.figures_rep.loc[~st.isin(["approved", "disapproved"])]
        ids = ", ".join(odd["patent_id"].astype(str) + " " + odd["fig_key"].astype(str))
        n["nostatus_note"] = (f" {n['figures_nostatus']} figure{'s were' if n['figures_nostatus'] > 1 else ' was'} "
                              f"never approved or disapproved in the wizard ({ids}) and "
                              f"{'are' if n['figures_nostatus'] > 1 else 'is'} counted apart.")
    n["wizard_approved"] = c["patents_wizard_approved"]
    n["gated_patents"] = c["patents_gated_out"]
    n["gated_aircraft"] = c["primary_variants_gated_out"]
    n["disapproved"] = n["acquired"] - n["representative"]
    n["disapproved_wizard"] = n["acquired"] - n["wizard_approved"]
    n["rep_share"] = f"{n['representative'] / n['acquired']:.0%}"
    n["wizard_share"] = f"{n['wizard_approved'] / n['acquired']:.0%}"
    reasons = a2.d1_rejection_reasons(ds).set_index("code")["patents"]
    n["r_noimg"] = int(reasons.get("No Aircraft Image", 0))
    n["r_uav"] = int(reasons.get("Pure UAV", 0))
    n["r_ood"] = int(reasons.get("Out of Domain", 0))
    n["r_nocontent"] = int(reasons.get("No Content", 0))
    n["r_notvtol"] = int(reasons.get("Not VTOL", 0))
    n["r_otherreason"] = int(reasons.get("Other", 0))
    n["r_sim_uav"] = int(reasons.get("Similar: UAV", 0))
    n["r_sim_el"] = int(reasons.get("Similar: not electric", 0))
    n["r_sim_stol"] = int(reasons.get("Similar: STOL only", 0))
    n["r_sim"] = int(reasons.get("subtotal_similar", 0))
    n["r_wiz"] = int(reasons.get("subtotal_wizard", 0))
    n["r_other"] = n["r_wiz"] - n["r_noimg"] - n["r_uav"] - n["r_ood"]
    n["not_rep"] = int(reasons.get("total", 0))
    snap = ds.identity["snapshot_date"].dropna()
    n["snapshot"] = str(snap.iloc[0])[:10] if len(snap) else "unknown"
    # ---- similars
    sim = a2.d1_similars(ds).set_index("similar")
    n["uav_n"] = int(sim.loc["UAV but similar", "patents tagged"])
    n["uav_primary"] = int(sim.loc["UAV but similar", "unique aircraft removed"])
    has_stol = "STOL but similar" in sim.index
    n["stol_n"] = int(sim.loc["STOL but similar", "patents tagged"]) if has_stol else 0
    n["stol_rep"] = int(sim.loc["STOL but similar", "unique aircraft removed"]) if has_stol else 0
    n["stol_also_uav"], n["stol_ids"] = sim.attrs["stol_also_uav"], sim.attrs["stol_ids"]
    n["vstol_n"], n["vstol_primary"] = sim.attrs["vstol"]
    n["notel_n"] = int(sim.loc["Not electric but similar", "patents tagged"])
    n["notel_primary"] = int(sim.loc["Not electric but similar", "unique aircraft removed"])
    n["two_tags"] = n["uav_primary"] + n["notel_primary"] + n["stol_rep"] - n["gated_aircraft"]
    n["unknown_el"] = int(ds.identity["is_electric_final"].eq("Unknown").sum())
    n["hybrid_el"] = int(ds.identity["is_electric_final"].eq("Hybrid").sum())
    n["stol_note"] = ""
    if n["stol_rep"] == 0 and n["stol_also_uav"]:
        n["stol_note"] = (" STOL but similar no longer removes an aircraft on its own: the last "
                          "STOL-only aircraft was disapproved at labelling as Not VTOL, and the one "
                          f"aircraft still carrying the tag ({n['stol_ids']}) is also UAV but similar "
                          "and leaves on that tag, so the table has no STOL row.")
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
    dup = a2.d7_duplicates(ds)
    dup.index = dup["type"].astype(str).str[:2]
    n["orig_obs"] = int(dup.loc["Or", "observations"])
    n["o1_obs"] = int(dup.loc["O1", "observations"])
    n["o2_obs"] = int(dup.loc["O2", "observations"])
    n["s3"] = int(dup.loc["S3", "observations"])
    n["o12_removed"] = n["o1_obs"] + n["o2_obs"]
    n["o1_all"], n["o2_all"], n["s3_all"] = (int(dup.loc[k, "all approved (before the gate)"])
                                             for k in ("O1", "O2", "S3"))
    n["s3_identical"] = a2.d7_d3_identical_to_root(ds)["identical_on_all_archetype_fields"]
    # patents -> observations: how many aircraft each representative patent draws
    obs_per = ds.approved_variants.groupby("patent_id").size()
    n["rep_one"] = int((obs_per == 1).sum())
    n["rep_multi"] = int((obs_per > 1).sum())
    n["rep_extra"] = int(obs_per.sum() - len(obs_per))
    n["o12_patents"] = n["representative"] - n["primary"]     # patents holding only an O1 / O2
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
    # ---- label set: questions from the dimension register (Figure 3.3b), columns from the export
    lab = a2.d2_label_set(ds)
    ls = lab.set_index("property of the label set")["value"]
    n["questions"] = int(ls.iloc[0])
    n["q_dim"], n["q_tick"], n["q_num"] = (int(ls.iloc[k]) for k in (1, 2, 3))
    n["q_beside"] = int(ls["Tags and escapes beside them, not counted"])
    n["cols"] = int(ls.iloc[5]); n["cols_off"] = int(ls["Coded export columns not on the cards, left out"])
    n["off_names"] = ", ".join(lab.attrs["off_cards"])
    n["median_q"] = int(ls.iloc[7])
    n["q_gt90"] = int(ls["Questions answered on more than 90 % of aircraft"])
    n["q_lt5"] = int(ls["Questions answered on fewer than 5 % of aircraft"])
    n["q_lt5_phrase"] = f"{n['q_lt5']} question is" if n["q_lt5"] == 1 else f"{n['q_lt5']} questions are"
    n["informative"] = int(ls["Export columns that carry the information (3.3.4)"])
    n["near_constant"] = int(ls.iloc[-2])
    cards = register.by_card(ds).set_index("card")
    for card in register.CARDS:
        r = cards.loc[card]
        n[f"q_{card}"], n[f"cols_{card}"] = int(r["questions"]), int(r["export columns"])
        n[f"qd_{card}"], n[f"qt_{card}"], n[f"qn_{card}"] = (int(r[k]) for k in ("dimensions", "ticks", "numbers"))
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
    n["tilt_n"] = int(af["anyTilt"].eq(True).sum())          # <NA> / n/a never counted (rule 1)
    n["a1t_left"] = int(arch.loc["A1t", "left out"]) if "left out" in arch.columns else 0
    bal = a2.d3_architecture_balance(ds, with_unclassifiable=False)
    n["unclassifiable"] = int(bal.attrs.get("unclassifiable", 0))
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
    dls = a3.derived_layer_summary(ds).set_index("derived variable")
    der = dls["value"]
    n["units_median"] = der.iloc[0]
    # rule 1 (2026-09-19): the bases and what is left out
    n["units_n"] = int(dls["of"].iloc[0])
    n["units_left"] = int(dls["left out"].iloc[0])
    n["tilt_base"] = int(dls.loc["Aircraft with any tilting unit", "of"])
    n["tilt_left"] = int(dls.loc["Aircraft with any tilting unit", "left out"])
    n["override_aircraft"] = int(a2.override_sets(ds.variants).map(bool).sum())
    d4 = a2.d4_missingness(ds)
    n["d4_left"] = int(d4["left out (override)"].max()) if len(d4) else 0
    n["wing_boom_candidates"] = int(ds.variants["wing_boom_candidate"].fillna(False).astype(bool).sum()) \
        if "wing_boom_candidate" in ds.variants.columns else 0
    fl = a2.d13_flagship_check(ds)
    n["flagship_companies"] = int(len(fl))
    if "public products" in fl:
        pub = fl[fl["public products"].astype(str).str.len() > 0]
        n["flagship_public"] = int(len(pub))
        n["flagship_match"] = int(pub["top label matches a public type"].fillna(False).astype(bool).sum())
        miss = pub[~pub["top label matches a public type"].fillna(False).astype(bool)]
        n["flagship_mismatch"] = int(len(miss))
        n["flagship_mismatch_names"] = ", ".join(miss["company"].astype(str))
    # ---- propulsor count (2026-09-22): the bins and what they hold
    units = a2.propulsor_units(ds.variants)["units"]
    bins = a2.rotor_bin(units).value_counts()
    n["units_counted"] = int(units.notna().sum())
    n["units_left_c"] = int(units.isna().sum())      # same count as units_left (3.3.5)
    for b, k in zip(a2.ROTOR_BINS[1], ("r03", "r4", "r56", "r78", "r9")):
        n[f"bin_{k}"] = int(bins.get(b, 0))
    u = pd.to_numeric(units, errors="coerce")
    n["u5"], n["u7"] = int((u == 5).sum()), int((u == 7).sum())
    j5 = ds.variants.loc[u.eq(5).reindex(ds.variants.index, fill_value=False), "topType"]
    n["u5_slc"] = int(j5.eq("SLC").sum())
    j7 = ds.variants.loc[u.eq(7).reindex(ds.variants.index, fill_value=False), "topType"]
    n["u7_slc"] = int(j7.eq("SLC").sum())
    grp = a2.propulsor_groups(ds.variants).where(units.notna())
    n["grp1"], n["grp2"], n["grp3"] = (int((grp == k).sum()) for k in (1, 2, 3))
    n["grp4"] = int((grp >= 4).sum())
    # ---- technological proximity between firms (3.3.9)
    px = a2.d14_firm_proximity(ds)
    for k in ("firms", "min_aircraft", "aircraft", "mean_class", "mean_rotors", "pairs_high_class",
              "pairs_zero_class", "pairs"):
        n[f"px_{k}"] = px.attrs[k]
    top = px.sort_values("proximity (class)", ascending=False).iloc[0]
    n["px_top_pair"] = f"{top['firm']} and {top['closest firm (class)']}"
    n["px_top_val"] = f"{top['proximity (class)']:.2f}"
    pc = a2.firm_profiles(ds, n["px_min_aircraft"], "class")
    xr = a2.proximity_matrix(a2.firm_profiles(ds, n["px_min_aircraft"], "class_rotors")
                             .reindex(pc.index).fillna(0))
    n["px_top_rot"] = f"{xr.loc[top['firm'], top['closest firm (class)']]:.2f}"
    # ---- repeat filings over time (3.3.8)
    sp = a2.d9_aircraft_spans(ds)
    n["sp_repeat"] = int((sp["repeats"] > 0).sum())
    n["sp_single"] = int((sp["repeats"] == 0).sum())
    n["sp_span"] = int((sp["span_years"] > 0).sum())
    n["sp_sameyear"] = n["sp_repeat"] - n["sp_span"]
    n["sp_multiwin"] = int((sp["window_first"] != sp["window_last"]).sum())
    n["sp_earlier"] = int((sp["first"] < sp["primary_year"]).sum())
    n["sp_move"] = int((sp["window_first"] != sp["window_primary"]).sum())
    n["sp_max"] = int(sp["span_years"].max())
    act = a2.d9_architecture_by_window_active(ds)
    once = act[act["count"].str.startswith("once")].set_index("window")
    whil = act[act["count"].str.startswith("while")].set_index("window")
    diff = (whil.drop(columns=["count", "unique aircraft"]) - once.drop(columns=["count", "unique aircraft"])).abs()
    n["sp_maxdiff"] = f"{diff.to_numpy().max():.2f}"
    # ---- string forms with the thousands space
    for k, v in list(n.items()):
        if isinstance(v, (int,)) and not isinstance(v, bool):
            n[f"{k}_s"] = fmt(v)
    return n
