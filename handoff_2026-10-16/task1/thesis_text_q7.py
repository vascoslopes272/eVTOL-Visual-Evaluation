"""Thesis question Q7 — Is there a dominant design? The text of chapter 4 (Methodology, Results and discussion, Appendix).

Numbers are never typed: every ``{key}`` is resolved from ``viz.thesis_q7.numbers(ctx)``. Sub-question titles follow the index.
"""

METHOD = """- **Objective:** Whether a dominant design exists, one layout most new designs copy after competing alternatives (Abernathy and Utterback, 1978).
- **Data and unit:** Unique designs by priority year or four-year cohort, in four configuration sets, A, A·W·T, A·U and F. The main base is all designs; the actively protected designs are a sensitivity base, read alone and never mixed with the main one.
- **Procedure:** Three conditions asked in the same period on one base, the largest configuration's share, the balance ²D and the form ΔQ. ΔQ uses one declared weighting (w15): 15 dimensions of the codebook, each of its four systems weighing 1 (the table of method III.2).
- **Test:** Share above half in two consecutive read years; ²D and ΔQ below their {perms}-permutation bands.
- **Limit:** Patent records have no sales, so renewal fees stand in; the latest years are still filling."""

RESULTS = [
    dict(sub="A", title="Defining the candidates", text="""[tab:q7_archetype_sets] gives the four configuration sets the test is run in. At A the same designs are {t7_c_arch} architectures that behave like {t7_c_d1} equally common ones. A·W·T and A·U cut them finer, into {t7_cwt_arch} and {t7_cu_arch} configurations. The largest single design in any set is F, with {t7_f_share} of the whole corpus against {t7_slc_share} for Lift + Cruise alone. At A·U the largest configuration holds {t7_cu_share}.

The configuration set, not the corpus, sets how many designs there are, so every claim below names its set. F was defined after the architecture and configuration readings had been seen, and no result on it is a pre-registered test."""),
    dict(sub="B", title="The test", text="""On all designs, the main base, F meets two of the three conditions in {w_last} and misses the third by one design. [fig:q7_condition2_balance] shows the balance condition met, F's ²D {f_d2_last} against a band edge of {f_d2_edge}. [fig:q7_condition3_cohesion] shows the form condition met, ΔQ {dq_f_all} against a band edge of {dq_f_all_edge}. [fig:q7_condition1_family] shows the counts condition missed: F holds {f_all_2021} of the designs of {met_last} but {f_all_2020} of {met_first} ({f_all_2020_k}), {f_all_short} design short of half, so no two consecutive years are above half.

The form condition uses one weighting only, w15: 15 dimensions of the codebook with each of its four systems weighing 1 (the table of method III.2). For A, A·U and F, which read the same designs, ΔQ is {dq_main} against a band edge of {dq_main_edge}.

No set meets the three conditions in the same period on all designs ([tab:q7_verdict_table]). A, A·W·T and A·U fail the counts condition, their largest configuration reaching at most {max_c_all} of a year's designs."""),
    dict(sub="C", title="Robustness", text="""Read alone on the actively protected designs, the sensitivity base, the result moves rather than holds. F meets the counts condition there, {f_in_2020} and {f_in_2021} in {met_first} and {met_last} ({f_in_2020_k} and {f_in_2021_k}), and the balance condition, ²D {f_ap_d2} against {f_ap_d2_edge}. It misses the form condition, ΔQ {dq_ap} against a band edge of {dq_ap_edge}. The two bases are never combined, so neither gives F the three conditions in one period.

On granted and live patents alone F holds {f_gl_2020} and {f_gl_2021} of the same two years. Only {gl_2022} and {gl_2023} of the actively protected designs of the two last years hold a granted patent, so whether the family held after them cannot be said. What holds on every base is a shared morphology, a fixed wing carrying many propulsors, and not a shared functional allocation."""),
    dict(sub="D", title="By region", text="""[fig:q7_region_family_share] shows the three regions reaching F in like measure. In {w_last} F holds {r_na_f_last} of North America's aircraft. Europe holds {r_eu_f_last} and Asia-Pacific {r_ap_f_last}. No regional difference in F is detected in any window from {w_first}, the smallest p being {r_p_f_mid}. North America is the one region whose F share rises detectably, ρ {r_na_rho} with p {r_na_rho_p}.

The tilting lean is North America's and not only its largest assignee's. Without Bell / Textron {r_na_tilt_wo} of North America's aircraft still tilt (p {r_p_tilt_wo}), more than in Europe or Asia-Pacific ([fig:q7_region_lean_without_largest_filer]). Two assignees of one region are no more alike than two of different regions, {px_same} against {px_diff} ([fig:q7_region_firm_proximity]).

Among the index assignees that disclose funding, {ext_f_weighted} of the aircraft sit in F when each assignee is weighted by its funding, against {ext_f_corpus} of the whole corpus. With {ext_firms} assignees behind it this is an indication only."""),
]

ANSWER = """The sector shows a shared morphology that cuts across two architectures, Lift + Cruise together with the CVT designs that tilt a propulsor set on a fixed wing, in simple words a fixed wing carrying many propulsors. On all designs that family F meets balance and form in {w_last} and misses the counts condition by one design ({met_first}: {f_all_2020_k}, {f_all_2020}). On the actively protected designs, read alone, it meets counts and balance and misses form (ΔQ {dq_ap} against {dq_ap_edge}). No single architecture or configuration comes close, the largest reaching {max_c_all} of a year's designs. The members of F part on the functional allocation of thrust, so a dominant design in the full sense is not found. The three regions hold F in like measure by {w_last}."""

APPENDIX = {
    "q7_verdict_table": "On all designs no set meets the three conditions in one period: F meets balance and form in {w_last} and misses counts by one design; on the actively protected designs, read alone, F meets counts and balance and misses form. At A·W·T the three largest configurations hold {top3_cwt} of {w_last}, an era of ferment.",
    "q7_region_lean_without_largest_filer": "North America's tilting lean outlives Bell / Textron, with {r_na_tilt_wo} of its aircraft still tilting without the assignee (p {r_p_tilt_wo}).",
    "q7_region_firm_proximity": "Two assignees of one region are no more alike than two of different regions, {px_same} against {px_diff}. Europe's assignees are the least alike.",
    "q7_cannot_answer": "[hl]The labelled dataset answers eight stakeholder questions only in part or not at all. Mission, size, certification and claim scope are not labels, so they need another study.[/hl]",
}
