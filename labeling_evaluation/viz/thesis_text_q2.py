"""Thesis question Q2, the text: who fills the field, and does anyone control it? (see THESIS_CONTRACT.md)"""

METHOD = """- **Objective:** Who fills the field with aircraft, and whether any filer controls a class.
- **Data and unit:** The {n_aircraft} unique aircraft, each counted once under the first assignee of its first patent.
- **Procedure:** Filer type from the name; per class of {class_min} or more, largest share, effective filers, shift on removal.
- **Test:** Chi-square of class against first-time and returning firms per window; Fisher's exact test on Tilt Wing between windows.
- **Limit:** Classes under {class_min} aircraft are not read; a subsidiary outside the name table is its own firm."""

RESULTS = [
    dict(sub="A", title="Who files", text="""Named companies hold {co_share} of the aircraft and individual inventors {ind_share}; universities and institutes hold the rest ([fig:q2_filer_types]). Counted over representative patents instead, companies hold {co_share_rep} and individuals {ind_share_rep}, so companies file the same aircraft on more patents. The individual inventors' share of the aircraft falls from {ind_w1} in the first window to {ind_w4} in the last complete one.

The {top_n} largest firms hold {top_share} of the aircraft ([fig:q2_largest_filers_share]). The named organisations together hold {org_share}, and {single_n} of them filed exactly one aircraft. In every window most of the filing organisations therefore file for the first time ([fig:q2_first_vs_returning_filers]). The design space read in Q6 is many designers' choice."""),
    dict(sub="B", title="Does anyone control it", text="""[hl]No filer holds more than {max_top_share} of any class of {class_min} aircraft or more over all years ([tab:q2_largest_filer_per_class]).[/hl] Every such class behaves as if split between {min_eff} or more equal filers, Lift + Cruise between {slc_eff}. The largest holdings are all Bell / Textron's, {tb_share} of Tilt Body and {tr_share} of Tilt Propulsor. Inside a single window one firm weighs more, Bell / Textron holding {tr_win_share} of Tilt Propulsor in {w1619}.

Removing Bell / Textron, the firm with the most aircraft, moves the Lift + Cruise share by {lev1_pp} points over all years, because its tilting-class aircraft leave at once. No other firm moves any class share by more than {lev2_pp} points. The class shares read in Q6 and Q7 therefore rest on many filers; the share of a single window can rest on one firm.

The class mix moves with the firms arriving, which bring most of the aircraft of named organisations in every window, {first_share_2023} in {w2023} ([fig:q2_entrant_class_mix]). In that window their classes do not differ detectably from those of returning firms (χ² p {p_2023}). In {w1619} the two groups differ (p {p_1619}), on the returning firms' Tilt Propulsor, most of it Bell / Textron's.

Tilt Wing is the first aircraft of {tw_ent_share_1619} and {tw_ent_share_2023} of the entering firms in the two windows ([fig:q2_tilt_wing_entrants]). Its share of the aircraft goes from {tw_air_1619} to {tw_air_2023}. Fisher's exact test does not detect the fall (p {tw_fisher_p})."""),
]

ANSWER = """Named organisations, {org_n} in all, file {org_share} of the aircraft, and most of them hold a single aircraft. No filer holds more than {max_top_share} of a class of {class_min} aircraft or more. Every such class behaves as if split between {min_eff} or more equal filers. Removing even the largest filer, Bell / Textron, moves a class share over all years by at most {lev1_pp} points, so no single firm decides the readings of Q6 and Q7. The class mix moves with the firms arriving in each window, which bring most of its aircraft, and not with returning firms changing class."""

APPENDIX = {
    "q2_first_vs_returning_filers": "Most filing organisations in every window are first-time ones; in the last complete window {new_2023} against {cont_2023} filing again.",
    "q2_entrant_class_mix": "In {w2023} first-time and returning firms do not differ detectably in class (χ² p {p_2023}); in the window before they do, on Bell / Textron's Tilt Propulsor.",
    "q2_tilt_wing_entrants": "Tilt Wing is the first aircraft of {tw_ent_share_2023} of the firms entering in the last complete window. Its share of all the aircraft falls a little, a fall Fisher's test does not detect (p {tw_fisher_p}).",
}
