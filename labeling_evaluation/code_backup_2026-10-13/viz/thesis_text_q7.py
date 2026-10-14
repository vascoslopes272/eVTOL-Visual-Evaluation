"""Thesis question Q7 — Is there a dominant design? The text of chapter 4 (Methodology, Results and discussion, Appendix).

Numbers are never typed: every ``{key}`` is resolved from ``viz.thesis_q7.numbers(ctx)``. Sub-question titles follow the index.
"""

METHOD = """- **Objective:** Whether a dominant design exists, one layout most new aircraft copy after competing alternatives (Abernathy and Utterback, 1978).
- **Data and unit:** Unique aircraft by priority year or four-year window, in four archetype sets, C, C·W·T, C·U and F.
- **Procedure:** Three conditions asked in the same period, the largest archetype's share, the balance ²D and the form ΔQ.
- **Test:** Share above half in two consecutive years on the in-force aircraft; ²D and ΔQ below their {perms}-permutation bands.
- **Limit:** Patent records have no sales, so renewal fees stand in; the years after {met_last} are still filling."""

RESULTS = [
    dict(sub="A", title="Defining the candidates", text="""[tab:q7_archetype_sets] gives the four archetype sets the test is run in. At C the same aircraft are {t7_c_arch} classes that behave like {t7_c_d1} equally common ones. C·W·T and C·U cut them finer, into {t7_cwt_arch} and {t7_cu_arch} archetypes. The largest single design in any set is F, with {t7_f_share} of the whole corpus against {t7_slc_share} for Lift + Cruise alone. At C·U the largest archetype holds {t7_cu_share}.

The archetype set, not the corpus, sets how many designs there are, so every claim below names its set. F was defined after the class and archetype readings had been seen, and no result on it is a pre-registered test."""),
    dict(sub="B", title="The test", text="""[fig:q7_condition1_family] reads the counts condition on F, met on the aircraft still in force with more than half in two consecutive years, {f_in_2020} and then {f_in_2021}. The margin is small. In the first met year F holds {f_in_2020_k} aircraft, in the second {f_in_2021_k}. On all aircraft the condition fails, because {met_first} stops at {f_all_2020}. In the two years after, whose base is the least complete, F falls to {f_in_2022} and {f_in_2023}.

[fig:q7_condition2_balance] shows the balance condition met by F and by C in {w_last}, and by C·U in the two earliest windows only. F's ²D is {f_d2_last} against a band edge of {f_d2_edge}.

[fig:q7_condition3_cohesion] shows the form condition met in every archetype set in {w_last}, under the main weighting only. For C, C·U and F, which read the same aircraft, ΔQ is {dq_main}, past a band edge of {dq_main_edge}. With every field weighted equally it is {dq_alt}, inside its band.

Only F meets the three conditions in the same period, {w_last} ([tab:q7_verdict_table]). C, C·W·T and C·U each meet at most two and fail on the counts condition, where their largest archetype reaches at most {max_c} of a year's in-force aircraft. The pass rests on the in-force base and on the weighting, and the next sub-question shows each the other way."""),
    dict(sub="C", title="Robustness", text="""The pass rests on three choices, F, the in-force base and the subsystem weighting, and each is shown both ways. Counted subsystem by subsystem the aircraft of {w_last} are more alike than chance gives, counted field by field they are not. The convergence therefore sits in the subsystems described by few fields and not in the propulsion fields.

Counted on all aircraft, F holds {f_all_2020_k} aircraft of the first met year, and one more would have crossed half. The in-force base includes applications still under examination. On granted and live patents alone F holds {f_gl_2020} and {f_gl_2021} of the two met years, so the pass does not rest on pending applications. Only {gl_2022} and {gl_2023} of the in-force aircraft of the two last years hold a granted patent, so whether the family held after the met years cannot be said. What holds under every choice is a shared morphology, a fixed wing carrying many propulsors, and not a shared functional allocation."""),
    dict(sub="D", title="By region", text="""[fig:q7_region_family_share] shows the three regions reaching F in like measure. In {w_last} F holds {r_na_f_last} of North America's aircraft. Europe holds {r_eu_f_last} and Asia-Pacific {r_ap_f_last}. No regional difference in F is detected in any window from {w_first}, the smallest p being {r_p_f_mid}. North America is the one region whose F share rises detectably, ρ {r_na_rho} with p {r_na_rho_p}.

The tilting lean is North America's and not only its largest filer's. Without Bell / Textron {r_na_tilt_wo} of North America's aircraft still tilt (p {r_p_tilt_wo}), more than in Europe or Asia-Pacific ([fig:q7_region_lean_without_largest_filer]). Two firms of one region are no more alike than two of different regions, {px_same} against {px_diff} ([fig:q7_region_firm_proximity]).

Among the index firms that disclose funding, {ext_f_weighted} of the aircraft sit in F when each firm is weighted by its funding, against {ext_f_corpus} of the whole corpus. With {ext_firms} firms behind it this is an indication only."""),
]

ANSWER = """The sector has converged on a dominant morphology that cuts across two classes, Lift + Cruise together with the CVT aircraft that tilt a propulsor set on a fixed wing, in simple words a fixed wing carrying many propulsors. That family F meets the three conditions in {w_last} on the aircraft still in force, with more than half of two consecutive years. No single class or archetype does so, the largest reaching {max_c} of a year's in-force aircraft. The pass rests on F, on the in-force base and on the subsystem weighting, each chosen after the first readings or shown both ways. The members of F part on the functional allocation of thrust, so a dominant design in the full sense, morphology and functional allocation both shared, is not found. The three regions hold F in like measure by {w_last}."""

APPENDIX = {
    "q7_verdict_table": "Only F meets the three conditions in one period, {w_last}. C, C·W·T and C·U each meet at most two and fail on the counts condition. At C·W·T the three largest archetypes hold {top3_cwt} of that window, an era of ferment.",
    "q7_region_lean_without_largest_filer": "North America's tilting lean outlives Bell / Textron, with {r_na_tilt_wo} of its aircraft still tilting without the firm (p {r_p_tilt_wo}).",
    "q7_region_firm_proximity": "Two firms of one region are no more alike than two of different regions, {px_same} against {px_diff}. Europe's firms are the least alike.",
    "q7_cannot_answer": "[hl]The labelled dataset answers eight stakeholder questions only in part or not at all. Mission, size, certification and claim scope are not labels, so they need another study.[/hl]",
}
