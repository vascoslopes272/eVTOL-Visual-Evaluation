"""Chapter 5 of the brief — geography (2026-09-27, the chapter-5 review).

Written to BRIEF_REVISION_RULES.md from the author's Word comments E1-E17
(REVIEW_2026-09-27_ch5_docx_comments.txt; his copy numbers this chapter 4, and his "Figure 20-23 /
Table 12-14" are ``atlas_region``, ``region_grid``, ``proximity_region``, ``ip_strategy``,
``la_class_region_timing``, ``la_lag_constancy``, ``la_ip_strategy``). Loaded by ``sm_index``
through ``CHAPTER_MODULES``.

Layout: 5.q1 heads node 5.1 (what each region designs), 5.q2 node 5.2 (when each region files),
5.q3 node 5.3 — the old portfolio section, replaced (E10, E11) by the question the author's E4 and
E17 raise: do the regions converge, and is North America's tilting lean one firm's.

Data: ``sm_open.ch5_tables`` (la_region_mix_change, la_region_window_mix, la_region_tests,
la_region_lean, la_region_years, la_region_lag, la_region_proximity_test) plus la_lag_offsets,
la_lead_lag_region, la_proximity_region and la_country_class. Figures: ``sm_figures.
panel_region_design`` / ``panel_region_timing`` / ``panel_region_converge``. Every number is a
placeholder computed in :func:`_ch5_numbers`.

Comment map
-----------
E1, E2, E6    new wording proposed (PROPOSED_TITLES): which regions, relative to whom, which classes.
E3, E5        Method / Results split; one takeaway per figure, the readings itemised per region.
E4a           unit: the unique aircraft in every panel (the old atlas panel (i) counted patents —
              acquired and representative — and is cut with the atlas figure).
E4b, E4c      raw readings per region, counts beside shares, and a trend column drawn beside each
              panel: shares 2012-15 → 2016-19 → 2020-23 and the Spearman trend over 2012-2023 on
              each aircraft's priority year (author's ruling 2026-09-27: read from 2012, not a
              before/after-2020 split; <= 2011 drawn faded).
E4d           publication lag checked: it explains 2025-26 only, not the fall of 2022-24.
E4e           "national mentality": one line, an interpretation the record neither confirms nor
              tests; what the record shows is the tilting lean surviving without Bell / Textron.
E7-E9         the interaction table (F on ranks) is cut; the delays are drawn in years with intervals.
E10, E11      the IP-strategy figure and the firm table are cut; the successions already sit in 4.2.
E12           the three countries are named with their counts.
E13           the regional peaks set beside dated sector events, as hypotheses.
E14-E16       every Answer claim points at the figure that shows it; "China leans to wingless
              designs" is dropped (China 10 % wingless, the United States 10 %).
E17           the shared objective: chapter 3's family F, reached by different routes.
"""
from __future__ import annotations

from typing import Dict, Optional

CHAPTER = "5"

#: the coordinator applies these to ``sm_index.SM_QUESTIONS`` / ``SUBQ`` (E1, E2, E6)
PROPOSED_TITLES = {
    "5": "Do North America, Europe and Asia-Pacific design different eVTOL aircraft, or the same "
         "aircraft at different times?",
    "5.1": "Which classes, propulsive-unit counts and tilting choices does each region file, and "
           "how has each region's mix moved since 2020?",
    "5.2": "How many years after North America do Europe and Asia-Pacific take up each class, and "
           "is North America's falling share of new aircraft real or a publication delay?",
    "5.3": "Do the three regions converge on the same design, and is North America's tilting lean "
           "the region's or one firm's?",
}

CHAPTER_TEXT = (
    "**Region** is the applicant region of the aircraft's patent — the country of its first "
    "assignee, not the office that published it: North America {c5_na_n} aircraft, Europe "
    "{c5_eu_n}, Asia-Pacific {c5_ap_n}; the {c5_oth_n} from other regions are left out. The "
    "United States ({c5_us_n}), China ({c5_cn_n}) and Germany ({c5_de_n}) hold {c5_top3_n} of the "
    "{unique_s}; China holds {c5_cn_ap} of Asia-Pacific's, so Asia-Pacific is mostly China. "
    "**Unit, in every figure: the unique aircraft**, counted once in the window of its priority "
    "year; counting the {c5_rep_n} representative patents would weigh a design by how often its "
    "firm re-filed it.\n"
)

METHOD: Dict[str, str] = {
    "5.q1": (
        "#### Method\n\n"
        "- **What each region files — {sm_here_sm_region_design}.** Per region and window: (i) "
        "the class, (ii) the propulsive-unit band, (iii) whether any propulsor tilts. Each bar is "
        "100 % of the region-window's aircraft with the answer recorded (under {c5_thin} aircraft: "
        "blank) — a share of the region's own aircraft, not a count.\n"
        "- **What moved, from 2012.** Beside each panel, the shares of 2012-15, 2016-19 and "
        "2020-23 and the **trend over 2012-2023**: Spearman ρ between each aircraft's priority "
        "year and the answer (1/0), as for chapter 3's driver traces. The two answers with the "
        "smallest p are listed; p < 0.05 is a trend detected. Before 2012 the regions hold too few "
        "aircraft (Europe {c5_eu_w1_clas_base}, Asia-Pacific {c5_ap_w1_clas_base}): drawn faded. "
        "The start year was set by the author after a first reading (**post hoc**).\n"
    ),
    "5.q2": (
        "#### Method\n\n"
        "- **Aircraft per year — {sm_here_sm_region_timing} (i).** North America's share of each "
        "priority year is printed on its segment.\n"
        "- **Publication lag.** A patent enters the record only once published, and the delay "
        "differs by office: priority to publication took a median of {c5_na_lag} years for North "
        "America's aircraft of 2016-21 ({c5_na_off_share} published in the {c5_na_off}) and "
        "{c5_ap_lag} for Asia-Pacific's ({c5_ap_off_share} in {c5_ap_off}). Recent years therefore "
        "show Asia-Pacific more fully. To test whether lag alone moves the regional shares of "
        "recent years, each region's count of a year is divided by the part of its aircraft the June 2026 "
        "snapshot can already see (read from its own 2016-21 lags) and the shares recomputed.\n"
        "- **When each region takes up a class — (ii).** A region's median priority year in a "
        "class minus that of North America, the region with the most aircraft, taken as the "
        "reference; with a 95 % bootstrap interval, on complete years (to "
        "{c5_last}) and the five classes with 10 aircraft or more in every region. The median, "
        "not the mean, because priority years are bounded and skewed to recent years. An interval "
        "that excludes 0 is a difference detected.\n"
        "- **Sector events** (dotted) are dated company and regulator notices, set beside the "
        "regional peaks as hypotheses, never tested as causes.\n"
    ),
    "5.q3": (
        "#### Method\n\n"
        "- **Convergence — {sm_here_sm_region_converge} (i).** Each region's share of aircraft in "
        "the family F of chapter 3 (Lift + Cruise, plus the CVT whose tilting part is a rotor set "
        "on a fixed wing: the dominant design of 3.2), in 2012-15, 2016-19 and 2020-23. A "
        "chi-square test of region against F asks whether the regions differ in each window; the "
        "same test is run on the unit band of {sm_here_sm_region_design}.\n"
        "- **One firm or the region — (ii).** The record's largest filer, {c5_big}, holds "
        "{c5_big_n} of North America's {c5_na_n} aircraft and {c5_big_tr} of its {c5_na_tr_n} Tilt "
        "Rotors. Each region's share with a tilting propulsor and its Tilt Rotor share are "
        "compared (chi-square, all years), with and without that firm.\n"
        "- **Firms of one region — (iii).** For the {c5_px_firms} firms with 5 aircraft or more, "
        "the **proximity** of two firms is the cosine of their class-share profiles: 1 = the same "
        "mix, 0 = no class in common. Pairs from the same region are set against pairs from "
        "different regions; p is a permutation test shuffling the region labels over the firms. "
        "*Unit:* the firm pair, because the question is whether a firm resembles its neighbours.\n"
    ),
}

RESULTS: Dict[str, str] = {"5.1": "", "5.2": "", "5.3": ""}

#: printed under each node's figure (sm_index AFTER): the per-region readings the author asked
#: for (E4b), the hypotheses beside the dated events (E13), the one line on mentality (E4e)
AFTER: Dict[str, str] = {
    "5.1": (
        "**Region by region, 2012-15 → 2016-19 → 2020-23.**\n\n"
        "- **North America.** CVT {c5_na_cvt_s1215} → {c5_na_cvt_s1619} → {c5_na_cvt_s2023} "
        "(ρ {c5_na_cvt_rho}, p {c5_na_cvt_p}), the one class trend detected in any region. Tilt "
        "Rotor {c5_na_tr_s1215} → {c5_na_tr_s1619} → {c5_na_tr_s2023}, no trend detected (p "
        "{c5_na_tr_p}); its larger share before 2012 ({c5_na_tr_w1}) rests on "
        "{c5_na_w1_clas_base} aircraft. One to three units fall ({c5_na_u13_s1215} → "
        "{c5_na_u13_s2023}, p {c5_na_u13_p}) and five to six rise ({c5_na_u56_s1215} → "
        "{c5_na_u56_s2023}, p {c5_na_u56_p}). The tilting share stays at "
        "{c5_na_tilt_s1619}-{c5_na_tilt_s2023}, the highest of the three regions.\n"
        "- **Europe.** Lift + Cruise {c5_eu_slc_s1215} → {c5_eu_slc_s1619} → {c5_eu_slc_s2023} "
        "and CVT {c5_eu_cvt_s1215} → {c5_eu_cvt_s1619} → {c5_eu_cvt_s2023}, no trend detected "
        "(p {c5_eu_slc_p}, {c5_eu_cvt_p}); CVT is {c5_eu_cvt_w5} of the partial 2024-26 window, on "
        "{c5_eu_w5_clas_base} aircraft. Seven to eight units rise ({c5_eu_u78_s1215} → "
        "{c5_eu_u78_s1619} → {c5_eu_u78_s2023}, p {c5_eu_u78_p}).\n"
        "- **Asia-Pacific.** 2012-15 holds {c5_ap_w2_clas_base} aircraft and is not read. From "
        "2016-19 to 2020-23: Lift + Cruise {c5_ap_slc_s1619} → {c5_ap_slc_s2023}, nine units or "
        "more {c5_ap_u9_s1619} → {c5_ap_u9_s2023}, the tilting share {c5_ap_tilt_s1619} → "
        "{c5_ap_tilt_s2023} — none a trend detected.\n"
    ),
    "5.2": (
        "**Why North America, then Europe, then Asia-Pacific — hypotheses the record cannot "
        "test.**\n\n"
        "- North America files most in {c5_na_peak} ({c5_na_peak_n} aircraft), the year after the "
        "Uber Elevate white paper and of the first Elevate Summit, both in the United States.\n"
        "- Europe files most in {c5_eu_peak} ({c5_eu_peak_n}), the year EASA published its special "
        "condition for VTOL aircraft and Lilium flew its five-seat prototype.\n"
        "- Asia-Pacific files most in {c5_ap_peak} ({c5_ap_peak_n}); the event list holds no Asian "
        "event before the EHang type certificate of 2023, so no dated event stands beside it. A "
        "follower reading — Asian firms entering once North American and European designs were "
        "public — fits the delays of (ii) but is not tested.\n"
    ),
    "5.3": (
        "A national design mentality — Asian caution and redundancy, American boldness with "
        "tilting mechanisms — is an interpretation the record neither confirms nor tests: it holds "
        "designs, not the reasons behind them.\n"
    ),
}

ITEMS = {
    "5.1": dict(figures=["sm_region_design"], tables=[]),
    "5.2": dict(figures=["sm_region_timing"], tables=[]),
    "5.3": dict(figures=["sm_region_converge"], tables=[]),
}

FIGURE_CAPTIONS = {
    "sm_region_design": "what each region files, per priority window — class, propulsive units "
                        "and tilting — with the trend from 2012 beside each panel",
    "sm_region_timing": "when each region files: aircraft per priority year and region against "
                        "dated sector events, and how many years after North America Europe and "
                        "Asia-Pacific file each class",
    "sm_region_converge": "whether the regions converge on chapter 3's family F, whether North "
                          "America's tilting lean survives without its largest filer, and whether "
                          "firms of one region are alike",
}

NOT_CORE = {
    "sm_region_design": "the regional grid redrawn on the unique aircraft with a trend column; "
                        "replaces atlas_region and region_grid (author, E3-E5, E12)",
    "sm_region_timing": "filing per year against publication lag and the per-class delays in "
                        "years; replaces la_class_region_timing and la_lag_constancy (E4d, E7-E9, "
                        "E13)",
    "sm_region_converge": "convergence on F, the tilting lean without Bell / Textron, firm "
                          "proximity; replaces proximity_region, ip_strategy and la_ip_strategy "
                          "(E4e, E10, E11, E14-E17)",
}


# ---------------------------------------------------------------------------------------------
# numbers — every one read from a table
# ---------------------------------------------------------------------------------------------
def _f(x) -> Optional[float]:
    try:
        v = float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return None if v != v else v


def _pct(x) -> str:
    v = _f(x)
    return "–" if v is None else f"{v * 100:.0f} %"


def _p(x) -> str:
    v = _f(x)
    if v is None:
        return "–"
    return "< 0.001" if v < 0.001 else f"{v:.3f}" if v < 0.05 else f"{v:.2f}"


def _int(x) -> str:
    v = _f(x)
    return "–" if v is None else f"{round(v):d}"


def _yrs(x) -> str:
    v = _f(x)
    if v is None:
        return "–"
    return f"{v:+.1f}".replace(".0", "") if abs(v) > 0 else "0"


_R = {"North America": "na", "Europe": "eu", "Asia-Pacific": "ap"}
_A = {"SLC": "slc", "TR": "tr", "CVT": "cvt", "TW": "tw", "MR": "mr", "other": "oth",
      "1-3": "u13", "4": "u4", "5-6": "u56", "7-8": "u78", "9+": "u9", "True": "tilt",
      "False": "notilt"}
_W = {"<= 2011": "w1", "2012-15": "w2", "2016-19": "w3", "2020-23": "w4", "2024-26 (partial)": "w5"}


def _ch5_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    import pandas as pd
    t = tables or {}
    out: Dict[str, str] = {}
    try:
        from . import la_tables as _lt, sm_figures as _sf
        out["c5_last"] = str(_lt.LAST_COMPLETE)
        out["c5_thin"] = str(_sf.CH5_THIN)
    except Exception:
        pass

    # --- the base ------------------------------------------------------------------------------
    ln = t.get("la_region_lean")
    if ln is not None:
        tot = 0
        for _, r in ln.iterrows():
            k = _R[r["region"]]
            out[f"c5_{k}_n"] = _int(r["aircraft"])
            tot += _f(r["aircraft"])
            out[f"c5_{k}_tilt"] = _pct(r["tilting share"])
            out[f"c5_{k}_tilt_wo"] = _pct(r["tilting share without it"])
            out[f"c5_{k}_tr"] = _pct(r["Tilt Rotor share"])
            out[f"c5_{k}_tr_wo"] = _pct(r["Tilt Rotor share without it"])
            out[f"c5_{k}_tr_n"] = _int(r["Tilt Rotor aircraft"])
            for per in ("2012-15", "2016-19", "2020-23"):
                sk = per.replace("-", "")[2:]
                out[f"c5_{k}_f{sk}"] = _pct(r[f"F share {per}"]) if (_f(r[f"F base {per}"]) or 0) >= 10 else "–"
                out[f"c5_{k}_f{sk}_n"] = _int(r[f"F base {per}"])
        na = ln[ln["region"].eq("North America")].iloc[0]
        out["c5_big"] = str(na["largest filer"])
        out["c5_big_n"] = _int(na["its aircraft"])
        out["c5_big_tr"] = _int(na["its Tilt Rotor aircraft"])
        fm = t.get("la_filer_mix")
        if fm is not None:
            n_all = _f(fm[fm["filer"].astype(str).eq("all filers")]["unique aircraft"].iloc[0])
            out["c5_oth_n"] = _int(n_all - tot)
    cc = t.get("la_country_class")
    if cc is not None:
        g = {str(r["country"]): _f(r["aircraft"]) for _, r in cc.iterrows()}
        out["c5_us_n"], out["c5_cn_n"], out["c5_de_n"] = (_int(g["US"]), _int(g["CN"]), _int(g["DE"]))
        out["c5_top3_n"] = _int(g["US"] + g["CN"] + g["DE"])
        if ln is not None:
            ap = _f(ln[ln["region"].eq("Asia-Pacific")]["aircraft"].iloc[0])
            out["c5_cn_ap"] = f"{g['CN']:.0f} of {ap:.0f}"
    prov = t.get("a1_provenance_region")
    if prov is not None:
        out["c5_rep_n"] = _int(pd.to_numeric(prov["representative"], errors="coerce").sum())

    # --- the regional mix and what moved -------------------------------------------------------
    mc = t.get("la_region_mix_change")
    if mc is not None:
        for _, r in mc.iterrows():
            a = "fam" if r["variable"] == "family F" else _A.get(str(r["answer"]), str(r["answer"]).lower())
            k = f"c5_{_R[r['region']]}_{a}"
            for wn in ("2012-15", "2016-19", "2020-23"):
                base = _f(r[f"base {wn}"]) or 0
                out[k + "_s" + wn.replace("-", "")[2:]] = _pct(r[f"share {wn}"]) if base >= 10 else "–"
            out[k + "_n2023"] = _int(r["aircraft 2020-23"])
            out[k + "_rho"] = "–" if _f(r["rho"]) is None else f"{_f(r['rho']):+.2f}"
            out[k + "_p"] = _p(r["p"])
        cls = mc[mc["variable"].eq("class")]
        for code in ("SLC", "TR", "CVT"):
            n = pd.to_numeric(cls[cls["answer"].eq(code)]["aircraft 2020-23"], errors="coerce").sum()
            out[f"c5_{_A[code]}_late_n"] = _int(n)
    wm = t.get("la_region_window_mix")
    if wm is not None:
        for _, r in wm.iterrows():
            k = (f"c5_{_R[r['region']]}_{_A.get(str(r['answer']), str(r['answer']).lower())}_"
                 f"{_W[str(r['window'])]}")
            out[k] = _pct(r["share"])
            out[k + "_n"] = _int(r["aircraft"])
            out[f"c5_{_R[r['region']]}_{_W[str(r['window'])]}_{r['variable'][:4]}_base"] = _int(r["base"])
        ap = wm[wm["region"].eq("Asia-Pacific") & wm["variable"].eq("class")]
        pre16 = ap[ap["window"].isin(["<= 2011", "2012-15"])].drop_duplicates("window")
        out["c5_ap_pre16"] = _int(pd.to_numeric(pre16["base"], errors="coerce").sum())

    # --- the tests -----------------------------------------------------------------------------
    ts = t.get("la_region_tests")
    if ts is not None:
        mk = {"class mix (five classes + other)": "class", "propulsive-unit band": "units",
              "any tilting unit": "tilt", "Tilt Rotor": "tr", "family F": "f"}
        pk = {"all years": "all", "2012-15": "1215", "2016-19": "1619", "2020-23": "2023"}
        for _, r in ts.iterrows():
            k = f"c5_p_{mk[r['measure']]}_{pk[r['period']]}" + ("" if r["filers"] == "all filers" else "_wo")
            out[k] = _p(r["p (chi-square, region)"])

    # --- when: per year, and the lag ------------------------------------------------------------
    yr = t.get("la_region_years")
    if yr is not None:
        y = yr.copy()
        for c in ("priority year", "aircraft", "share of the year", "share corrected for publication lag",
                  "visible at the snapshot"):
            y[c] = pd.to_numeric(y[c], errors="coerce")
        for _, r in y.iterrows():
            k = f"c5_{_R[r['region']]}_{int(r['priority year'])}"
            out[k] = _pct(r["share of the year"])
            out[k + "_n"] = _int(r["aircraft"])
            out[k + "_c"] = _pct(r["share corrected for publication lag"])
            out[k + "_vis"] = _pct(r["visible at the snapshot"])
        last = int(out.get("c5_last", "2023"))
        for reg, k in _R.items():
            s = y[y["region"].eq(reg) & y["priority year"].le(last)]
            top = s.loc[s["aircraft"].idxmax()]
            out[f"c5_{k}_peak"] = _int(top["priority year"])
            out[f"c5_{k}_peak_n"] = _int(top["aircraft"])
        late = y[y["priority year"].gt(last)]
        w5 = late.groupby("region")["aircraft"].sum()
        out["c5_na_w5_share"] = _pct(w5.get("North America", 0) / w5.sum()) if w5.sum() else "–"
        after = y[y["priority year"].gt(last + 1)]
        out["c5_ap_2526_n"] = _int(after[after["region"].eq("Asia-Pacific")]["aircraft"].sum())
        out["c5_other_2526_n"] = _int(after[~after["region"].eq("Asia-Pacific")]["aircraft"].sum())
        v23 = y[y["priority year"].eq(last)]["visible at the snapshot"]
        out["c5_vis_last_lo"] = _pct(v23.min())
        out["c5_vis_last_hi"] = _pct(v23.max())
        ap_mid = y[y["region"].eq("Asia-Pacific") & y["priority year"].between(last - 2, last)]["aircraft"]
        out["c5_ap_mid_lo"], out["c5_ap_mid_hi"] = _int(ap_mid.min()), _int(ap_mid.max())
    lg = t.get("la_region_lag")
    if lg is not None:
        names = {"US": "United States", "CN": "China", "EP": "European Patent Office", "DE": "Germany"}
        for _, r in lg.iterrows():
            k = _R[r["region"]]
            out[f"c5_{k}_lag"] = _int(r["median lag (years)"])
            out[f"c5_{k}_off"] = names.get(str(r["main office"]), str(r["main office"]))
            out[f"c5_{k}_off_share"] = _pct(r["its share"])
            out[f"c5_{k}_pub1"] = _pct(r["published within 1 y"])
    off = t.get("la_lag_offsets")
    if off is not None:
        ck = {"Lift + Cruise": "slc", "Tilt Rotor": "tr", "Combined vectored thrust": "cvt",
              "Tilt Wing": "tw", "Multirotor": "mr"}
        for _, r in off.iterrows():
            c = ck.get(str(r["class"]))
            if not c or r["region"] not in _R:
                continue
            k = f"c5_off_{_R[r['region']]}_{c}"
            out[k] = _yrs(r["offset vs North America (years)"])
            out[k + "_lo"] = _yrs(r["95 % low"])
            out[k + "_hi"] = _yrs(r["95 % high"])
            out[f"c5_med_{_R[r['region']]}_{c}"] = _int(r["median priority year"])
    ll = t.get("la_lead_lag_region")
    if ll is not None:
        for _, r in ll.iterrows():
            if r["region3"] in _R:
                out[f"c5_{_R[r['region3']]}_median"] = _int(r["50 %"])
    lc = t.get("la_lag_constancy")
    if lc is not None and len(lc):
        out["c5_p_lag_inter"] = _p(lc.iloc[0]["p (permutation)"])

    # --- proximity -----------------------------------------------------------------------------
    pt = t.get("la_region_proximity_test")
    if pt is not None:
        r = pt.iloc[0]
        out["c5_px_firms"] = _int(r["firms"])
        out["c5_px_same"] = f"{_f(r['same-region mean']):.2f}"
        out["c5_px_diff"] = f"{_f(r['different-region mean']):.2f}"
        out["c5_px_p"] = _p(r["p (permutation)"])
    pr = t.get("la_proximity_region")
    if pr is not None:
        for _, r in pr.iterrows():
            a = [x.strip() for x in str(r["region pair"]).split("/")]
            if len(a) == 2 and a[0] == a[1] and a[0] in _R:
                out[f"c5_px_{_R[a[0]]}"] = f"{_f(r['mean']):.2f}"
                out[f"c5_px_{_R[a[0]]}_pairs"] = _int(r["pairs"])

    # the closing section points at the old regional items; they are now this chapter's figures
    try:
        from . import sm_index as _sm
        for old, new in (("atlas_region", "sm_region_design"),
                         ("la_class_region_timing", "sm_region_timing"),
                         ("proximity_region", "sm_region_converge")):
            if old not in _sm.HERE_REF and new in _sm.HERE_REF:
                out[f"sm_here_{old}"] = _sm.HERE_REF[new]
    except Exception:
        pass
    return out


NUMBER_FUNCS = [_ch5_numbers]

# ---------------------------------------------------------------------------------------------
# takeaways
# ---------------------------------------------------------------------------------------------
TAKEAWAY = {
    "sm_region_design":
        "**From 2012 to 2023 only North America changes its class mix — toward CVT — while North "
        "America and Europe add propulsive units, each into its own band: five to six in North "
        "America, seven to eight in Europe; in Asia-Pacific no trend is detected.** A bar is a share of one region's aircraft, not a count: in 2020-23 Lift + "
        "Cruise is the largest class in number across the three regions ({c5_slc_late_n} "
        "aircraft, against {c5_cvt_late_n} CVT and {c5_tr_late_n} Tilt Rotor), yet the smallest of "
        "the three in North America ({c5_na_slc_s2023}); its weight is Europe's and "
        "Asia-Pacific's",

    "sm_region_timing":
        "**North America's share of new aircraft falls from {c5_na_2021} in 2021 to {c5_na_2023} "
        "in 2023, and publication lag does not explain it; lag explains only the all-Asia-Pacific "
        "years 2025-26.** "
        "**(i) The fall is in the record.** Corrected for lag, North America holds {c5_na_2023_c} "
        "of 2023 and {c5_na_2024_c} of 2024 — the same as observed, because the snapshot already "
        "sees {c5_vis_last_lo}-{c5_vis_last_hi} of every region's 2023 aircraft. Its count falls "
        "too, from {c5_na_2021_n} in 2021 to {c5_na_2023_n} in 2023, while Asia-Pacific holds at "
        "{c5_ap_mid_lo}-{c5_ap_mid_hi} a year. The partial 2024-26 window's low North American "
        "share ({c5_na_w5_share}) is mostly the lag: its {c5_ap_2526_n} aircraft of 2025-26 are all "
        "Asia-Pacific's, and of 2025 the snapshot can have seen {c5_ap_2025_vis} of Asia-Pacific's "
        "aircraft but only {c5_na_2025_vis} of North America's. "
        "**(ii) Asia-Pacific is 3-4 years late on the older classes, not on CVT.** It files Lift + "
        "Cruise {c5_off_ap_slc} years after North America ({c5_off_ap_slc_lo} to "
        "{c5_off_ap_slc_hi}), Tilt Rotor {c5_off_ap_tr} ({c5_off_ap_tr_lo} to {c5_off_ap_tr_hi}) "
        "and Tilt Wing {c5_off_ap_tw} ({c5_off_ap_tw_lo} to {c5_off_ap_tw_hi}); on CVT no delay is "
        "detected ({c5_off_ap_cvt}, {c5_off_ap_cvt_lo} to {c5_off_ap_cvt_hi}), because North "
        "America itself came late to CVT (median {c5_med_na_cvt}). No European delay is detected: "
        "every European interval reaches zero. Whether the delay differs from class to class is "
        "not settled (p {c5_p_lag_inter})",

    "sm_region_converge":
        "**By 2020-23 the three regions hold chapter 3's dominant design in like measure, and "
        "differ in how many propulsors they put on their aircraft.** "
        "**(i) One destination.** No regional difference in F is detected in any window from "
        "2012 (p {c5_p_f_1215}, {c5_p_f_1619}, {c5_p_f_2023}); in 2020-23 F holds {c5_na_f2023} "
        "of North America's aircraft, {c5_eu_f2023} of Europe's and {c5_ap_f2023} of "
        "Asia-Pacific's. North America, the lowest in 2012-19 ({c5_na_f1215}, {c5_na_f1619}), is "
        "the one region whose F share rises detectably (ρ {c5_na_fam_rho}, p {c5_na_fam_p}). The "
        "unit band does the opposite: the regions differ only in 2020-23 (p {c5_p_units_1215}, "
        "{c5_p_units_1619}, then {c5_p_units_2023}). "
        "**(ii) The tilting lean is North America's, not only {c5_big}'s.** Without that firm "
        "{c5_na_tilt_wo} of North America's aircraft still tilt, against {c5_eu_tilt} in Europe "
        "and {c5_ap_tilt} in Asia-Pacific (p {c5_p_tilt_all_wo}), and {c5_na_tr_wo} are Tilt "
        "Rotors, against {c5_eu_tr} and {c5_ap_tr} (p {c5_p_tr_all_wo}). {c5_big}, the firm "
        "behind the XV-15 and V-22 tilt rotors, carries {c5_big_tr} of the region's "
        "{c5_na_tr_n} Tilt Rotors. "
        "**(iii) No regional blocs among firms.** Two firms of one region are no more alike than "
        "two of different regions ({c5_px_same} against {c5_px_diff}, p {c5_px_p}). Europe's "
        "firms are the least alike ({c5_px_eu}, against {c5_px_na} and {c5_px_ap}; not tested)",
}

# ---------------------------------------------------------------------------------------------
# the Answer (E14-E17: every claim points at its figure)
# ---------------------------------------------------------------------------------------------
ANSWER = (
    "**Region changes when a design is filed and how many propulsors it carries more than which "
    "architecture it is: the three regions converge on chapter 3's dominant design, each by its "
    "own route.**\n\n"
    "- **One destination.** In 2020-23 the family F holds {c5_na_f2023} of North American, "
    "{c5_eu_f2023} of European and {c5_ap_f2023} of Asia-Pacific aircraft; no regional "
    "difference is detected in any window from 2012, and North America, the lowest in 2012-19, "
    "rose to meet the others (ρ {c5_na_fam_rho}, p {c5_na_fam_p}) "
    "({sm_here_sm_region_converge} (i)).\n"
    "- **Different routes.** North America's route runs through CVT ({c5_na_cvt_s1215} → "
    "{c5_na_cvt_s1619} → {c5_na_cvt_s2023} of its aircraft), the one class trend detected in "
    "any region. Propulsors grow in a different band in each region — five to six units in "
    "North America, seven to eight in Europe (both detected), nine or more in Asia-Pacific (p "
    "{c5_ap_u9_p}, not detected) ({sm_here_sm_region_design}) — and the regions' unit bands "
    "differ only in 2020-23 (p {c5_p_units_2023}).\n"
    "- **One lean outlives its largest firm.** North America files the most tilting aircraft "
    "({c5_na_tilt}, against {c5_eu_tilt} and {c5_ap_tilt}) and still does without {c5_big} "
    "({c5_na_tilt_wo}, p {c5_p_tilt_all_wo}) ({sm_here_sm_region_converge} (ii)).\n"
    "- **A clock, not a bloc.** Median priority year: North America {c5_na_median}, Europe "
    "{c5_eu_median}, Asia-Pacific {c5_ap_median}. Asia-Pacific files Lift + Cruise, Tilt Rotor "
    "and Tilt Wing 3-4 years after North America and shows no delay on CVT, the class North "
    "America came to late ({sm_here_sm_region_timing} (ii)). North America's falling share since "
    "2021 is in the record, not a publication delay ({sm_here_sm_region_timing} (i)).\n"
    "- **No regional design blocs among firms.** Two firms of one region are no more alike than "
    "two of different regions ({c5_px_same} against {c5_px_diff}, p {c5_px_p}); Europe's are the "
    "least alike ({c5_px_eu}) ({sm_here_sm_region_converge} (iii))."
)
