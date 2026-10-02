"""Chapter 4 of the brief — "Who files" (2026-09-26, the chapter-4 review).

Written to BRIEF_REVISION_RULES.md from the author's Word comments D1-D26
(REVIEW_2026-09-26_ch4_docx_comments.txt; his copy still numbers this chapter 3, so his
"Figure 17-20 / Table 17-20" are, in order: ``coverage``, ``la_filer_mix``,
``la_filers_by_window``, ``filer_weight``, ``firm_influence``, ``la_class_filer_weight``,
``sm_entry_all``, ``la_tw_successions``). Loaded by ``sm_index`` through ``CHAPTER_MODULES``; the
interface is the CHAPTER MODULES block at the end of ``sm_index.py``.

Layout: sub-question 4.q1 heads node 4.1 (old "Who files"), into which node 4.2 (old "Whether
one firm carries the reading") is merged (``MERGE``), so it has one Results and discussion;
sub-question 4.q2 heads node 4.3 (old "entrants"). The wording of the two sub-questions is the
coordinator's (``sm_index.SUBQ``); this module proposes new wording in :data:`PROPOSED_TITLES`.

Data: ``sm_open.ch4_tables`` (registered in ``sm_open.build_all``) — la_class_concentration_brief,
la_entry_split, la_entry_split_test, la_tw_entry, la_succession_matrix, la_ari_funding,
la_ari_funding_tests — plus la_filer_mix, la_filers_by_window, la_coverage_segments and
la_firm_leverage of ``la_tables``. Figures: ``sm_figures.panel_who_files`` / ``panel_one_firm``
/ ``panel_ari_funding`` / ``panel_entry_split`` / ``panel_successions``. Every number is a
placeholder computed in :func:`_ch4_numbers` from those tables, never typed.

Comment map
-----------
D1, D14, D15  new sub-question wording proposed (PROPOSED_TITLES): "space", not "mix".
D2, D11, D16  Method and Results separated; the old observation prose became Method or a
              takeaway, never both; itemised.
D3            the filer types, and how each is recognised, in the 4.q1 Method (a table).
D4, D5, D8    the filer figure keeps its panel (i); panels (ii)/(iii) (index firms against the
              others; index score against aircraft) are cut. The index firms' representativeness
              is chapter 1's table (``{sm_here_la_ari_representativeness}``).
D4, D6, D26   what the index carries and the corpus does not — disclosed funding, $M — read on the
              9 firms that have it, against aircraft, first patent and the patent-to-flight lead
              of chapter 1 (``{sm_here_ari_clock}``). Headcount and capitalisation: not in the
              index, said so.
D9, D10       the filer-mix and filers-per-window tables are panels (ii) and (iii) of one figure.
D12, D13      the two filer-weight figures and the concentration table are one figure.
D17-D19, D22, D25  "arrival", "conversion", "crowd", "capitalisation" replaced by what is measured
              (first-time / returning filers; organisations holding one aircraft; funding $M).
D18           why Tilt Wing keeps drawing new firms: the record cannot say; who they are is
              counted, and the "after the share peaked" premise is not supported (Fisher p).
D20           the successions table is a heat map.
D21           the Answer ties "open" to the crowded core / empty rim of chapter 2.
D23           the effective number of filers is defined (1 / sum of squared shares) with an example.
D24           one claim instead of two: first-time and returning firms choose alike; a firm's
              next aircraft stays in the large classes and leaves the small ones, Tilt Wing most.

OVERTURNED by the new readings (report to the author):
* "Arrival, not conversion, moves the mix" — first-time and returning filers differ only in
  2016-19 (p 0.015), and not once Bell / Textron is left out (p 0.61); 2020-23 no difference.
* "Tilt Wing: firms keep arriving after the share has peaked" — the fall of the Tilt Wing share
  from 2016-19 to 2020-23 is not detected (Fisher p 0.27); what holds is that its share of
  entering firms is the same in both windows.
"""
from __future__ import annotations

from typing import Dict, Optional

CHAPTER = "4"

#: the coordinator applies these to ``sm_index.SUBQ`` (D1; D14, D15: "space" not "mix")
PROPOSED_TITLES = {
    "4.1": "Who files eVTOL patents, and does any filer hold enough of an architecture class to "
           "decide its share?",
    "4.2": "Is the eVTOL design space reshaped by firms filing their first aircraft or by firms "
           "filing again, and where does a firm's next design land?",
}

#: old 4.2 ("Whether one firm carries the reading") joins 4.1: one Results and discussion per
#: sub-question
MERGE = {"4.2": "4.1"}

# ---------------------------------------------------------------------------------------------
# the chapter opener
# ---------------------------------------------------------------------------------------------
CHAPTER_TEXT = (
    "Chapters 2 and 3 read the designs; this chapter reads the filers behind them, in two steps.\n\n"
    "- **4.1 — who files, and how concentrated filing is.** The filers are sorted by type and "
    "ranked by the aircraft they hold; each architecture class is asked whether one filer holds "
    "enough of it to decide its share; and the firms the AAM Reality Index rates are read against "
    "the one thing the index holds and the patents do not — the money they have raised.\n"
    "- **4.2 — who reshapes the design space.** The classes of the aircraft filed by firms filing "
    "for the first time are set against those of firms that filed before, and each firm's next "
    "aircraft is followed to the class it lands in.\n"
)

# ---------------------------------------------------------------------------------------------
# Method blocks
# ---------------------------------------------------------------------------------------------
_FILER_TYPES = (
    "**Who a filer is.** Every patent names its owners, the assignees; the first one named is "
    "the **filer**. Its type is read from that name as the patent office prints it:\n\n"
    "| filer type | recognised by | example |\n"
    "|---|---|---|\n"
    "| **Named company** | a legal form (Inc, GmbH, Ltd, 株式会社, 公司 …), an activity word "
    "(aviation, technology, systems …), a digit, a single brand word, or more than five words | "
    "Bell Textron Inc |\n"
    "| **University / institute** | a university, institute, academy, college, polytechnic or "
    "public research centre | Beihang University |\n"
    "| **Individual inventor** | a personal name — two to five words, or one name in Chinese, "
    "Japanese or Korean script | a private inventor filing in his or her own name |\n\n"
    "A fourth type, *no assignee named*, is empty in this corpus. Companies, universities and "
    "institutes are the **named organisations**, called *firms* below; the spellings of one firm "
    "are merged into one name (Airbus Urban Mobility into Airbus). An individual inventor cannot "
    "be followed reliably from patent to patent — one name can be transliterated two ways — so "
    "where filers are counted each individual's patent is its own filer, and wherever a firm is "
    "followed over time the individuals are left out.\n\n"
)

METHOD: Dict[str, str] = {
    "4.q1": (
        "#### Method\n\n"
        + _FILER_TYPES +
        "Three measurements answer this question.\n\n"
        "- **Who files and how much each holds — {sm_here_sm_who_files}.**\n"
        "  - *(i)* The named organisations ranked by their unique aircraft, largest first, and "
        "the cumulative share of the {unique_s} aircraft they hold, cut where firms hold 10 or "
        "more, 5-9, 2-4 and 1 aircraft each; the firms the AAM Reality Index has rated are "
        "marked.\n"
        "  - *(ii)* The share of each filer type, over all years counted twice — in patents (the "
        "{c4_patents} distinct patents the aircraft are recorded on) and in unique aircraft — then "
        "per priority window, in aircraft. The two all-years bars show whether the unit changes "
        "the answer.\n"
        "  - *(iii)* The named organisations filing in each window, split into **first-time "
        "filers** — firms whose earliest eVTOL aircraft in the corpus falls in that window — and "
        "**returning filers**, firms that filed in an earlier window.\n"
        "  - *Unit:* the unique aircraft in (i) and (ii), because holding the record means "
        "holding designs, and a design filed five times is one design; the organisation in (iii), "
        "because a first filing is an event of the firm.\n"
        "- **Whether one filer holds enough of a class to decide its share — "
        "{sm_here_sm_one_firm}.** Read on the {c4_conc_n} classes with {c4_class_min} aircraft or "
        "more; in a smaller class one filer's aircraft move the share by large steps.\n"
        "  - *(i)* Per class: the share of its aircraft held by its largest filer over all years "
        "(bar), and the largest share one filer holds inside a single priority window (diamond; "
        "windows with {c4_cell_min} or more of the class's aircraft, the partial 2024-26 window "
        "left out). On the tick: the class's filers and its effective number of filers.\n"
        "  - **Effective number of filers = 1 / Σ sᵢ²**, where sᵢ is filer i's share of the "
        "class's aircraft — the ²D of the diversity box in chapter 2, computed over filers instead "
        "of archetypes. It says how many *equally sized* filers would give the same concentration. "
        "*Example, invented numbers:* a class of 10 aircraft, 5 from one firm and 1 each from five "
        "others, has Σ sᵢ² = 0.5² + 5 × 0.1² = 0.30 and so behaves as if split between 3.3 equal "
        "filers, although it has 6. When every filer holds one aircraft the number equals the "
        "filer count; when one filer holds everything it is 1.\n"
        "  - *(ii)* **Leaving one firm out.** For each firm with three aircraft or more, its "
        "aircraft are removed, every class's share of the remaining aircraft is recomputed, and "
        "the largest change is kept, in percentage points — over all years (bar) and inside a "
        "single window of 30 aircraft or more (diamond). The eight firms that move a share most "
        "are drawn.\n"
        "  - *Unit:* the unique aircraft; a firm that files one design several times moves "
        "nothing.\n"
        "- **What the AAM Reality Index adds about the firms it rates — "
        "{sm_here_sm_ari_funding}.** The index (1.1) rates {c4_ari_n} firms that file here; they "
        "hold {c4_ari_air} of the aircraft ({c4_ari_share}). Chapter 1 has already tested whether "
        "their aircraft stand for the corpus ({sm_here_la_ari_representativeness}): they do not — "
        "they differ from the rest in region, priority window, filer type and propulsive units — "
        "so what follows describes these firms, not the record.\n"
        "  - *What the index holds that the patents do not:* a disclosed funding amount, in "
        "US$ million, for {c4_fund_n} of the firms (May 2026 release); {c4_corp_n} are marked "
        "*corporate backed* with no amount, and {c4_hist_n} appear only in earlier releases, "
        "without funding. The index holds **no headcount and no market capitalisation**, so "
        "neither is read.\n"
        "  - *What is tested:* on the {c4_fund_n} firms with an amount, funding against (i) their "
        "unique aircraft in the corpus, (ii) the priority year of their first patent and (iii) "
        "the lead from first patent to first flight of {sm_here_ari_clock}, on the {c4_lead_n} "
        "firms whose first flight has happened. Each is a **Spearman ρ** — whether one quantity "
        "rises as the other does, reading only the order of the values — with its p, as set out "
        "in the statistics box at the head of chapter 1.\n"
        "  - *Unit:* the firm, because funding belongs to the firm. On {c4_fund_n} firms only a "
        "strong relation can be detected; a lead below zero only means that the firm's earliest "
        "filing is not in this corpus. Sources: AAM Reality Index (May 2026), PatSeer, human "
        "labelling.\n"
    ),

    "4.q2": (
        "#### Method\n\n"
        "The design space moves when the classes of the new aircraft change. Two things can move "
        "it: the firms filing for the first time may choose other classes than the firms already "
        "filing, and a firm that files again may change class. Both are read on the named "
        "organisations only, because an individual inventor cannot be followed from one patent to "
        "the next (4.1).\n\n"
        "- **First-time against returning filers — {sm_here_sm_entry_split} (i).** In each "
        "window the named organisations' aircraft are split into those of first-time filers and "
        "those of returning filers (defined in 4.1), and the class mix of the two groups is "
        "compared by a chi-square test over Lift + Cruise, Tilt Rotor, CVT, Tilt Wing, Multirotor "
        "and the other classes together. Tested where the returning group holds {c4_test_min} "
        "aircraft or more: 2016-19 and 2020-23. *Unit:* the unique aircraft. The test is repeated "
        "without the returning firm that holds most of the window's returning aircraft; that "
        "second reading was added after the first result showed one firm holding "
        "{c4_big_ret_1619} of the {c4_ret_1619} returning aircraft of 2016-19.\n"
        "- **Tilt Wing's entering firms — {sm_here_sm_entry_split} (ii).** Tilt Wing is read on "
        "its own because it is the class a firm's next aircraft leaves most often "
        "({sm_here_sm_successions}). Per window: the share of the firms entering the record in "
        "that window whose first aircraft is a Tilt Wing (a firm enters once, in the window of its "
        "first aircraft; *unit:* the firm), beside Tilt Wing's share of all the window's aircraft "
        "(*unit:* the aircraft, individuals included). The change of that aircraft share from "
        "2016-19 to 2020-23 is tested with Fisher's exact test. For the firms entering with Tilt "
        "Wing in 2020-23, the filer type and whether the firm filed any other aircraft are "
        "counted, against all the window's entering firms.\n"
        "- **Where a firm's next aircraft lands — {sm_here_sm_successions}.** A **succession** "
        "is a named organisation's aircraft followed by the same firm's next aircraft in priority "
        "order; aircraft of the same year are taken in record order, which is arbitrary. Each "
        "class of origin with {c4_succ_min} successions or more is one row, giving the share of "
        "the next aircraft that stay in the class and where the others go (the row sums to "
        "100 %). *Unit:* the succession — {c4_pairs} of them, from the {c4_pair_firms} firms with "
        "two aircraft or more. A firm with many aircraft contributes many successions — "
        "{c4_bell} {c4_bell_pairs} of them — so the share that stays is repeated without it, in "
        "the right-hand column. Sources: PatSeer (assignee, priority date), human labelling.\n"
    ),
}

#: every point is a takeaway (rule 2); the chapter's one joined reading is its Answer
RESULTS: Dict[str, str] = {"4.1": "", "4.3": ""}

# ---------------------------------------------------------------------------------------------
# items: 4.2 is merged into 4.1, so 4.1 carries the three items of 4.q1, in Method order
# ---------------------------------------------------------------------------------------------
ITEMS = {
    "4.1": dict(figures=["sm_who_files", "sm_one_firm", "sm_ari_funding"], tables=[]),
    "4.3": dict(figures=["sm_entry_split", "sm_successions"], tables=[]),
}

FIGURE_CAPTIONS = {
    "sm_who_files": "who files the eVTOL patents: how much of the record the largest named "
                    "organisations hold, the filer types over all years and per priority window, "
                    "and the organisations filing for the first time or again",
    "sm_one_firm": "whether one filer holds enough of a class to decide its share: the largest "
                   "filer of each class over all years and inside one window, with the effective "
                   "number of filers; and how far leaving one firm out moves a class share",
    "sm_ari_funding": "the AAM Reality Index firms with a disclosed funding amount: funding "
                      "against the aircraft they filed, the year of their first patent and the "
                      "lead from first patent to first flight",
    "sm_entry_split": "who moves the class mix: the classes of the aircraft of first-time and "
                      "returning filers in the two windows that can be tested, and Tilt Wing's "
                      "share of the entering firms against its share of the aircraft",
    "sm_successions": "where a firm's next aircraft lands, by the class of the one before; the "
                      "boxed cell is the share that stays in the class",
}

NOT_CORE = {
    "sm_who_files": "the filer figure with the filer-mix and filers-per-window tables as panels "
                    "(author, D4, D5, D8-D10, 2026-09-26)",
    "sm_one_firm": "the two filer-weight figures and the concentration table as one figure "
                   "(author, D12, D13, D23)",
    "sm_ari_funding": "the index firms' disclosed funding against the patent side (author, D4, "
                      "D6, D26)",
    "sm_entry_split": "first-time against returning filers, and Tilt Wing's entering firms "
                      "(author, D16-D18, D24)",
    "sm_successions": "the successions table as a heat map (author, D20)",
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
    from . import la_index as _la
    v = _f(x)
    return "–" if v is None else _la._tk_fmt(v, "pct")


def _p(x) -> str:
    v = _f(x)
    if v is None:
        return "–"
    return "< 0.001" if v < 0.001 else f"{v:.3f}" if v < 0.05 else f"{v:.2f}"


def _int(x) -> str:
    v = _f(x)
    return "–" if v is None else f"{round(v):d}"


def _row(t, col, val):
    m = t[t[col].astype(str).eq(val)]
    return m.iloc[0] if len(m) else None


def _ch4_numbers(tables: Optional[Dict], values: Dict) -> Dict:
    import pandas as pd
    t = tables or {}
    out: Dict[str, str] = {}
    try:
        from . import sm_open as _so
        out["c4_class_min"] = str(_so.CH4_CLASS_MIN)
        out["c4_cell_min"] = str(_so.CH4_CELL_MIN)
        out["c4_test_min"] = str(_so.CH4_TEST_MIN)
        out["c4_succ_min"] = str(_so.CH4_SUCC_MIN)
    except Exception:
        pass

    # --- who files (la_filer_mix, la_coverage_segments, la_filers_by_window) ------------------
    fm = t.get("la_filer_mix")
    if fm is not None:
        allr = _row(fm, "filer", "all filers")
        out["c4_patents"] = _int(allr["primary patents"])
        gaps = []
        for key, name in (("co", "Named companies"), ("uni", "Universities and institutes"),
                          ("ind", "Individual inventors")):
            r = _row(fm, "filer", name)
            out[f"c4_{key}_air"] = _int(r["unique aircraft"])
            out[f"c4_{key}_share"] = _pct(r["share of the analysis set"])
            out[f"c4_{key}_pat_share"] = _pct(r["share per primary patent"])
            gaps.append(abs(_f(r["share of the analysis set"]) - _f(r["share per primary patent"])))
        out["c4_unit_gap"] = f"{max(gaps) * 100:.0f}"
    seg = t.get("la_coverage_segments")
    if seg is not None:
        s = seg.reset_index(drop=True)
        out["c4_top4_n"] = _int(s.loc[0, "firms"])
        out["c4_top4_air"] = _int(s.loc[0, "aircraft"])
        out["c4_top4_share"] = _pct(s.loc[0, "share of the analysis set"])
        out["c4_seg2_n"] = _int(s.loc[1, "firms"])
        out["c4_seg2_air"] = _int(s.loc[1, "aircraft"])
        last = s.iloc[-1]
        out["c4_single_n"] = _int(last["firms"])
        out["c4_org_n"] = _int(last["cumulative firms"])
        cum_air = _f(last["cumulative aircraft"])
        if fm is not None:
            n_all = _f(_row(fm, "filer", "all filers")["unique aircraft"])
            out["c4_org_share"] = _pct(cum_air / n_all)
    fw = t.get("la_filers_by_window")
    if fw is not None:
        for w, k in (("<= 2011", "1"), ("2016-19", "1619"), ("2020-23", "2023")):
            r = _row(fw, "window", w)
            out[f"c4_ind_w{k}"] = _pct(r["share individual inventors"])
            out[f"c4_new_{k}"] = _int(r["new firms"])
            out[f"c4_act_{k}"] = _int(r["named firms active"])
        out["c4_ind_w4"] = out.get("c4_ind_w2023", "–")

    # --- concentration (la_class_concentration_brief, la_firm_leverage) -----------------------
    cc = t.get("la_class_concentration_brief")
    if cc is not None:
        c = cc.copy()
        for col in ("its share", "effective filers", "largest share inside one window", "aircraft"):
            c[col] = pd.to_numeric(c[col], errors="coerce")
        out["c4_conc_n"] = str(len(c))
        top = c.loc[c["its share"].idxmax()]
        out["c4_max_top_share"] = _pct(top["its share"])
        out["c4_max_top_class"] = str(top["class"])
        out["c4_max_top_firm"] = str(top["largest filer"])
        out["c4_min_eff"] = f"{c['effective filers'].min():.0f}"
        big4 = c.sort_values("aircraft", ascending=False).head(4)
        out["c4_big4_min_eff"] = f"{big4['effective filers'].min():.0f}"
        tr_ = c[c["code"].eq("TR")].iloc[0]
        cvt_ = c[c["code"].eq("CVT")].iloc[0]
        if str(top["largest filer"]) == str(tr_["largest filer"]) == str(cvt_["largest filer"]):
            out["c4_top_holdings"] = (f"all {top['largest filer']}'s: {_pct(top['its share'])} of "
                                      f"{top['class']}, {_pct(tr_['its share'])} of Tilt Rotor and "
                                      f"{_pct(cvt_['its share'])} of CVT")
        else:
            out["c4_top_holdings"] = (f"{top['largest filer']}'s {_pct(top['its share'])} of "
                                      f"{top['class']}, {tr_['largest filer']}'s "
                                      f"{_pct(tr_['its share'])} of Tilt Rotor and "
                                      f"{cvt_['largest filer']}'s {_pct(cvt_['its share'])} of CVT")
        for code in ("SLC", "TR", "CVT", "TW"):
            r = c[c["code"].eq(code)].iloc[0]
            k = code.lower()
            out[f"c4_{k}_top"] = str(r["largest filer"])
            out[f"c4_{k}_top_share"] = _pct(r["its share"])
            out[f"c4_{k}_eff"] = f"{r['effective filers']:.0f}"
            out[f"c4_{k}_win_share"] = _pct(r["largest share inside one window"])
            out[f"c4_{k}_win_firm"] = str(r["held by"])
            out[f"c4_{k}_win"] = str(r["in window"])
            out[f"c4_{k}_win_n"] = _int(r["window aircraft"])
    lev = t.get("la_firm_leverage")
    if lev is not None:
        lv = lev.copy()
        lv["mag"] = pd.to_numeric(lv["shift if the firm is dropped (pp)"], errors="coerce").abs()
        lv["win"] = pd.to_numeric(lv["largest shift inside one window (pp)"], errors="coerce")
        lv = lv.sort_values("mag", ascending=False)
        out["c4_lev1"] = str(lv.iloc[0]["firm"])
        out["c4_lev1_pp"] = f"{lv.iloc[0]['mag']:.1f}"
        out["c4_lev1_class"] = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT",
                                "TW": "Tilt Wing", "MR": "Multirotor"}.get(
            str(lv.iloc[0]["class most moved"]), str(lv.iloc[0]["class most moved"]))
        out["c4_lev2_pp"] = f"{lv.iloc[1]['mag']:.1f}"
        w = lv.loc[lv["win"].idxmax()]
        out["c4_levw_pp"] = f"{w['win']:.1f}"
        out["c4_levw_firm"] = str(w["firm"])
        out["c4_levw_win"] = str(w["that window"])

    # --- the index firms and their money (la_ari_funding, la_ari_funding_tests) ---------------
    fr = t.get("la_ari_funding")
    if fr is not None:
        f = fr.copy()
        f["_fund"] = pd.to_numeric(f["funding $M"], errors="coerce")
        f["_air"] = pd.to_numeric(f["unique aircraft"], errors="coerce")
        out["c4_ari_n"] = str(len(f))
        out["c4_ari_air"] = _int(f["_air"].sum())
        if fm is not None:
            out["c4_ari_share"] = _pct(f["_air"].sum() / _f(_row(fm, "filer", "all filers")["unique aircraft"]))
        st = f["funding status"].astype(str)
        out["c4_fund_n"] = str(int(st.eq("disclosed").sum()))
        out["c4_corp_n"] = str(int(st.str.startswith("corporate").sum()))
        out["c4_hist_n"] = str(int(st.str.startswith("not in").sum()))
        d = f[f["_fund"].notna()].sort_values("_fund", ascending=False)
        out["c4_top_fund_firm"] = str(d.iloc[0]["company"])
        out["c4_top_fund_fp"] = _int(d.iloc[0]["first patent"])
        out["c4_top_fund_m"] = f"{d.iloc[0]['_fund']:,.0f}".replace(",", " ")
        out["c4_low_fund_m"] = f"{d.iloc[-1]['_fund']:,.0f}".replace(",", " ")
    ft = t.get("la_ari_funding_tests")
    if ft is not None:
        for col, k in (("unique aircraft", "air"), ("first patent", "fp"),
                       ("years first patent to first flight", "lead")):
            r = _row(ft, "column", col)
            out[f"c4_rho_{k}"] = f"{_f(r['rho']):+.2f}"
            out[f"c4_p_{k}"] = _p(r["p"])
            out[f"c4_n_{k}"] = _int(r["firms"])
        out["c4_lead_n"] = out["c4_n_lead"]

    # --- first-time against returning (la_entry_split, la_entry_split_test) -------------------
    es, et = t.get("la_entry_split"), t.get("la_entry_split_test")
    if es is not None and et is not None:
        for w, k in (("2016-19", "1619"), ("2020-23", "2023")):
            r = _row(et, "window", w)
            out[f"c4_p_{k}"] = _p(r["p"])
            out[f"c4_p_{k}_wo"] = _p(r["p without it"])
            out[f"c4_big_{k}"] = str(r["largest returning firm"])
            out[f"c4_big_ret_{k}"] = _int(r["its aircraft"])
            out[f"c4_ret_{k}"] = _int(r["returning aircraft"])
            out[f"c4_new_air_{k}"] = _int(r["first-time aircraft"])
            out[f"c4_all_air_{k}"] = _int(_f(r["first-time aircraft"]) + _f(r["returning aircraft"]))
            sub = es[es["window"].astype(str).eq(w)]
            new = sub[sub["group"].eq("first-time filers")].iloc[0]
            ret = sub[sub["group"].eq("returning filers")].iloc[0]
            for cls, ck in (("Lift + Cruise", "slc"), ("Tilt Rotor", "tr"), ("CVT", "cvt")):
                out[f"c4_new_{ck}_{k}"] = _pct(new[cls])
                out[f"c4_ret_{ck}_{k}"] = _pct(ret[cls])
    tw = t.get("la_tw_entry")
    if tw is not None:
        for w, k in (("2016-19", "1619"), ("2020-23", "2023")):
            r = _row(tw, "window", w)
            out[f"c4_tw_ent_{k}"] = _pct(r["Tilt Wing share of entrants"])
            out[f"c4_tw_n_{k}"] = _int(r["entering with Tilt Wing"])
            out[f"c4_ent_{k}"] = _int(r["firms entering"])
            out[f"c4_tw_air_{k}"] = _pct(r["Tilt Wing share of the aircraft"])
        r = _row(tw, "window", "2020-23")
        out["c4_tw_p"] = _p(r["Tilt Wing share, Fisher p against the window before"])
        a, b = out["c4_tw_ent_1619"], out["c4_tw_ent_2023"]
        out["c4_tw_ent_both"] = (f"{a} in both windows" if a == b else f"{a} and {b}")
        n_tw, n_all = _f(r["entering with Tilt Wing"]), _f(r["firms entering"])
        for col, k in (("universities / institutes", "uni"), ("no other aircraft", "one")):
            a, b = _f(r[f"Tilt Wing entrants: {col}"]), _f(r[f"all entrants: {col}"])
            out[f"c4_tw_{k}"] = f"{round(a):d} ({_pct(a / n_tw)})"
            out[f"c4_all_{k}"] = f"{round(b):d} ({_pct(b / n_all)})"

    # --- successions (la_succession_matrix) ---------------------------------------------------
    sm = t.get("la_succession_matrix")
    if sm is not None:
        r0 = sm.iloc[0]
        out["c4_pairs"] = _int(r0["successions, all classes"])
        out["c4_pair_firms"] = _int(r0["firms with a succession"])
        out["c4_bell"] = str(r0["firm left out"])
        out["c4_bell_pairs"] = _int(r0["its successions, all classes"])
        for code in ("SLC", "TR", "CVT", "TW", "MR"):
            r = _row(sm, "code", code)
            if r is None:
                continue
            k = code.lower()
            out[f"c4_{k}_stay"] = _pct(r["stays in the class"])
            out[f"c4_{k}_succ"] = _int(r["successions"])
            out[f"c4_{k}_firms"] = _int(r["firms"])
            out[f"c4_{k}_stay_wo"] = _pct(r["stays without it"])
            out[f"c4_{k}_succ_wo"] = _int(r["successions without it"])
        r = _row(sm, "code", "TW")
        out["c4_tw_to_tr"] = _pct(r["→ TR"])
        out["c4_tw_to_slc"] = _pct(r["→ SLC"])

    # chapter 2's rings (la_zones), by the rule the zones figure draws them with: the core is
    # above the median 2016-23 share and below the median filers per aircraft, the rim at or
    # below the median share
    z = t.get("la_zones")
    if z is not None and "share 2016-23" in z.columns:
        zz = z[pd.to_numeric(z["filers 2016-23"], errors="coerce") > 0]
        sh = pd.to_numeric(zz["share 2016-23"], errors="coerce")
        fp = pd.to_numeric(zz["filers per aircraft"], errors="coerce")
        core = fp[(sh > sh.median()) & (fp < fp.median())]
        rim = fp[sh <= sh.median()]
        out["c4_core_fpa"] = f"{core.median():.2f}"
        out["c4_rim_fpa"] = f"{rim.median():.2f}"

    # the closing section of the brief points at the filer figure and the concentration table by
    # their old names; both are now panels of this chapter's figures
    try:
        from . import sm_index as _sm
        for old, new in (("coverage", "sm_who_files"), ("la_class_filer_weight", "sm_one_firm")):
            if old not in _sm.HERE_REF and new in _sm.HERE_REF:
                out[f"sm_here_{old}"] = _sm.HERE_REF[new]
    except Exception:
        pass
    return out


NUMBER_FUNCS = [_ch4_numbers]

# 2026-09-27: the chapter-4 "External comparison" bullet (author's request) -- the two
# best-funded AAM Reality Index firms' share of the disclosed funding against their share of
# the corpus aircraft. Data from sm_open.external_tables (la_ext_concentration).
NUMBERS = {
    "sm_ext_top1": dict(table="la_ext_concentration", col="firm 1", fmt="raw"),
    "sm_ext_top2": dict(table="la_ext_concentration", col="firm 2", fmt="raw"),
    "sm_ext_top2_fundshare": dict(table="la_ext_concentration",
                                  col="their share of disclosed funding", fmt="pct"),
    "sm_ext_top2_airshare": dict(table="la_ext_concentration",
                                 col="their share of corpus aircraft", fmt="pct"),
}

# ---------------------------------------------------------------------------------------------
# takeaways (rule 3: specific bold leads; nothing the Method already says)
# ---------------------------------------------------------------------------------------------
TAKEAWAY = {
    "sm_who_files":
        "**Organisations file most of the record, but no small group of them holds it: the "
        "{c4_top4_n} largest firms hold {c4_top4_share} of the aircraft, and {c4_single_n} of the "
        "{c4_org_n} named organisations hold one aircraft each.** (i) The {c4_top4_n} firms with "
        "ten aircraft or more hold {c4_top4_air} aircraft, the next {c4_seg2_n} another "
        "{c4_seg2_air}, and all {c4_org_n} together {c4_org_share}. (ii) Named companies hold "
        "{c4_co_air} of the {unique_s} aircraft ({c4_co_share}), individual inventors "
        "{c4_ind_air} ({c4_ind_share}), universities and institutes {c4_uni_air} "
        "({c4_uni_share}); counted in patents instead, no share moves by more than {c4_unit_gap} "
        "point. The individual inventors' share of the aircraft falls from {c4_ind_w1} before "
        "2012 to {c4_ind_w4} in 2020-23. (iii) In every window most filing organisations file "
        "for the first time: {c4_new_1619} of {c4_act_1619} in 2016-19 and {c4_new_2023} of "
        "{c4_act_2023} in 2020-23",

    "sm_one_firm":
        "**No class is one filer's portfolio: no filer holds more than {c4_max_top_share} of a "
        "class over all years, and every class of {c4_class_min} aircraft or more behaves as if "
        "split between {c4_min_eff} or more equal filers.** (i) The largest holdings are "
        "{c4_top_holdings}; the four largest classes "
        "behave as if split between {c4_big4_min_eff} or more equal filers, Lift + Cruise between "
        "{c4_slc_eff}. Inside one window a single firm can weigh far more: {c4_tr_win_firm} holds "
        "{c4_tr_win_share} of Tilt Rotor in {c4_tr_win}, and {c4_slc_win_firm} {c4_slc_win_share} "
        "of Lift + Cruise in {c4_slc_win}, a window of {c4_slc_win_n} such aircraft. (ii) Leaving "
        "out {c4_lev1}, the firm with the most aircraft, moves the {c4_lev1_class} share by "
        "{c4_lev1_pp} points; no other firm moves any class share over all years by more than "
        "{c4_lev2_pp}, and the largest move inside one window is {c4_levw_pp} points "
        "({c4_levw_firm}, {c4_levw_win}). The class shares read in chapter 3 therefore rest on "
        "many filers; the share of a single window can rest on one",

    "sm_ari_funding":
        "**The better-funded index firms filed their first eVTOL patent earlier, but hold no "
        "detectably more aircraft and reach first flight no detectably sooner after it.** (i) "
        "Funding against the aircraft in the corpus: ρ {c4_rho_air}, p {c4_p_air}, no relation "
        "detected. (ii) Against the year of the first patent: ρ {c4_rho_fp}, p {c4_p_fp} on "
        "{c4_n_fp} firms; the best funded, {c4_top_fund_firm} (US$ {c4_top_fund_m} million), "
        "filed first, in {c4_top_fund_fp}. (iii) Against the lead to first "
        "flight: ρ {c4_rho_lead}, p {c4_p_lead} on {c4_n_lead} firms, no relation detected. On so "
        "few firms the one relation detected, one of three tested, is a lead to follow rather "
        "than a settled result",

    "sm_entry_split":
        "**First-time and returning filers choose the same classes once {c4_big_1619} is left "
        "out; the one difference detected is that firm's Tilt Rotor line.** (i) In 2016-19 the "
        "two groups differ (χ² p {c4_p_1619}): returning filers put {c4_ret_tr_1619} of their "
        "aircraft in Tilt Rotor against {c4_new_tr_1619} for first-time filers, who put "
        "{c4_new_slc_1619} in Lift + Cruise against {c4_ret_slc_1619}. {c4_big_1619} holds "
        "{c4_big_ret_1619} of the {c4_ret_1619} returning aircraft, and without it no difference "
        "is detected (p {c4_p_1619_wo}). In 2020-23 none is detected with it (p {c4_p_2023}) or "
        "without it (p {c4_p_2023_wo}). First-time filers hold most of each window's aircraft "
        "({c4_new_air_1619} of {c4_all_air_1619} in 2016-19, {c4_new_air_2023} of "
        "{c4_all_air_2023} in 2020-23), so the class mix moves with the whole population of "
        "filers, not with one group of it. (ii) Tilt Wing draws the same share of the entering "
        "firms in 2016-19 and 2020-23 ({c4_tw_ent_both}: {c4_tw_n_1619} "
        "and {c4_tw_n_2023} firms), while its share of the aircraft goes from {c4_tw_air_1619} "
        "to {c4_tw_air_2023}, a fall not detected (Fisher p {c4_tw_p}). Why firms start with "
        "Tilt Wing the record cannot say, and who they are does not single them out: of the "
        "{c4_tw_n_2023} entering with it in 2020-23, {c4_tw_uni} are universities or institutes "
        "and {c4_tw_one} filed no other aircraft, against {c4_all_uni} and {c4_all_one} of all "
        "{c4_ent_2023} entering firms",

    "sm_successions":
        "**A firm's next aircraft usually stays in Lift + Cruise or Tilt Rotor, and usually leaves "
        "every smaller class — Tilt Wing most of all.** {c4_slc_stay} of the successions from "
        "Lift + Cruise and {c4_tr_stay} from Tilt Rotor stay in the class; CVT keeps "
        "{c4_cvt_stay}. From Tilt Wing only {c4_tw_stay} of {c4_tw_succ} successions, from "
        "{c4_tw_firms} firms, stay: {c4_tw_to_tr} go on to Tilt Rotor and {c4_tw_to_slc} to Lift "
        "+ Cruise. Without {c4_bell}, Tilt Wing still keeps only {c4_tw_stay_wo} of "
        "{c4_tw_succ_wo}, while CVT falls to {c4_cvt_stay_wo}: much of CVT's apparent loyalty is "
        "that one firm's",
}

# ---------------------------------------------------------------------------------------------
# the Answer box (D21: "open" read against chapter 2's crowded core and empty rim; D24: one claim)
# ---------------------------------------------------------------------------------------------
ANSWER = (
    "**Organisations, mostly companies, file {c4_org_share} of the eVTOL aircraft — but "
    "{c4_org_n} of them, {c4_single_n} with a single aircraft. No filer holds enough of any class to decide its share, first-time "
    "and returning firms choose the same classes, and the one firm whose weight shows is "
    "{c4_lev1}.**\n\n"
    "- **Who files.** Named companies hold {c4_co_share} of the aircraft, individual inventors "
    "{c4_ind_share} and universities and institutes {c4_uni_share}; the individuals' share falls "
    "from {c4_ind_w1} before 2012 to {c4_ind_w4} in 2020-23. Of {c4_org_n} organisations, the "
    "{c4_top4_n} largest hold {c4_top4_share} of the aircraft and {c4_single_n} hold one each.\n"
    "- **The crowded core of chapter 2 is crowded by many filers.** No class of {c4_class_min} aircraft or more has a "
    "filer holding more than {c4_max_top_share} of it, and each behaves as if split between "
    "{c4_min_eff} or more equal filers, so the core of {sm_here_zones} — the archetypes "
    "that hold most recent aircraft — is many designers' choice, not one firm's variants, and "
    "the record is open in that sense. The empty rim is more dispersed still — a median of "
    "{c4_rim_fpa} filers per aircraft against {c4_core_fpa} in the core: designs each tried by "
    "a different filer. The core's one exception, CVT with 5-6 units "
    "({sm_cvt56_top_n} of {sm_cvt56_air} aircraft from {sm_cvt56_top}), is the line of the firm whose "
    "removal moves a class share most — by {c4_lev1_pp} points.\n"
    "- **Money goes with filing early, not with filing more.** Of the {c4_ari_n} index firms, "
    "{c4_fund_n} disclose their funding: the better-funded filed their first patent earlier "
    "(ρ {c4_rho_fp}, p {c4_p_fp}) but hold no detectably more aircraft and fly no detectably "
    "sooner after filing. The index firms are not a sample of the record "
    "({sm_here_la_ari_representativeness}).\n"
    "- **The class mix moves with the whole population of filers.** First-time filers hold most "
    "of every window's aircraft, and their classes do not differ detectably from those of "
    "returning firms once {c4_big_1619} is left out (p {c4_p_1619_wo} in 2016-19, "
    "{c4_p_2023_wo} in 2020-23).\n"
    "- **A firm that files again stays in the large classes and leaves the small ones.** "
    "{c4_slc_stay} of the next aircraft stay in Lift + Cruise and {c4_tr_stay} in Tilt Rotor, "
    "only {c4_tw_stay} in Tilt Wing. Tilt Wing is the far end of that pattern, not an exception "
    "to it: it keeps its place in the record through the firms that start with it — "
    "{c4_tw_ent_both} of the entering firms, 2016-19 and 2020-23 — not through firms that "
    "stay. Why firms start "
    "there, the record cannot say.\n"
    "- **External comparison.** Money is far more concentrated than patents. The two "
    "best-funded index firms, {sm_ext_top1} and {sm_ext_top2}, hold {sm_ext_top2_fundshare} of "
    "the disclosed funding between them, yet their aircraft come to only "
    "{sm_ext_top2_airshare} of the whole corpus: the patents behind the record are spread far "
    "more widely than the money in front of it."
)
