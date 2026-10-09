"""Thesis question Q3 — the regions: the text (Methodology, Results and discussion, Answer, Appendix lines).

Every number is a {placeholder} resolved from viz.thesis_q3.numbers(ctx). See THESIS_CONTRACT.md.
"""

METHOD = """- **Objective:** Whether the three regions file different designs, and whether they enter each class at different times.
- **Data and unit:** {three_n} of {all_n} unique aircraft, in North America, Europe and Asia-Pacific, by first-assignee country and priority year.
- **Procedure:** Class, propulsor-unit band and tilting share per region and window; median priority year per class and region.
- **Test:** Chi-square across regions, Spearman trend per region over {trend_from}-{trend_to}, bootstrap interval on each class's entry lag.
- **Limit:** Years before {trend_from} are too thin to read, and publication delay shows Asia-Pacific more fully in recent years."""

RESULTS = [
    dict(sub="A", title="What each region files", text="""The regions are compared first on what they file, then on when they file it. All years together North America leads with Tilt Propulsor, {na_tr_all} of its aircraft against {na_slc_all} in Lift + Cruise ([fig:q3_region_design_all_years]). Europe and Asia-Pacific lead with Lift + Cruise, {eu_slc_all} and {ap_slc_all}. North America also has the most aircraft with a tilting propulsor, {na_tilt_all}, where the other two regions stay under half (p {p_tilt_all}).

[hl]Per window only North America changes its class mix, toward CVT, which reaches {na_cvt_2023} of its aircraft in the latest complete window, the one class trend detected in any region (p {na_cvt_p}, [fig:q3_region_mix_by_window_class]).[/hl] [hl]Propulsor units grow in a different band in each region, five to six in North America (p {na_u56_p}) and seven to eight in Europe (p {eu_u78_p}, [fig:q3_region_mix_by_window_units]).[/hl] The regions therefore differ in their propulsor-unit band only in the latest window (p {p_units_2023}, against {p_units_1619} in the window before). In that window Lift + Cruise is the largest class in number across the three regions, {slc_2023_n} aircraft, yet the smallest of the three large classes in North America ({na_slc_2023}). Its weight is Europe's and Asia-Pacific's."""),
    dict(sub="B", title="When each region enters", text="""North America's median priority year is {na_median}; Europe's and Asia-Pacific's follow it by {follow_years}. Asia-Pacific files Lift + Cruise, Tilt Propulsor and Tilt Wing {ap_delay_range} years after North America, a delay detected in each of the three ([fig:q3_region_entry_lag]). On CVT no delay is detected, Asia-Pacific's offset is {ap_cvt_off} years, because North America itself came to CVT late, median year {na_cvt_median}. No European delay is detected, {eu_all_reach_zero} European interval reaches zero. Whether the delay differs from class to class is not settled (p {lag_constancy_p}).

Read on the aircraft of {lag_since} onward only, the order holds but the delays shrink. [hl]Asia-Pacific's delay on {ap_16_reach_zero} is no longer detected, the Tilt Propulsor one falling to {ap_tr_off16} years.[/hl] Part of Asia-Pacific's delay therefore rests on the few aircraft filed before {lag_since}. A follower reading, Asian firms entering once North American and European designs were public, fits the delays but is not tested.

North America files most in {na_peak_year}, the year after the Uber Elevate white paper, and Europe in {eu_peak_year}, the year of EASA's special condition for VTOL aircraft. Both are coincidences in time that the dataset cannot test as causes. Within firms the route is read in the appendix ([fig:q3_firm_successions]). A firm's next aircraft stays in Lift + Cruise or Tilt Propulsor and leaves Tilt Wing. Whether the patented aircraft stand for the ones that get built is read next, in Q4."""),
]

ANSWER = """Region has more influence on when a design is filed and how many propulsors it carries than on which architecture it is. North America's route runs through CVT, the one class trend detected in any region, and through tilting propulsors, {na_tilt_all} of its aircraft all years together. Europe and Asia-Pacific lead with Lift + Cruise, {eu_slc_all} and {ap_slc_all}, and each region adds propulsor units in its own band, five to six in North America and seven to eight in Europe. Asia-Pacific files the older classes {ap_delay_range} years after North America and shows no delay on CVT, the class North America came to late; no European delay is detected. Within a firm the next aircraft stays in Lift + Cruise in {slc_stay} of the successions and in Tilt Wing in only {tw_stay}, so the smaller classes are left by the firms that filed them."""

APPENDIX = {
    "q3_region_mix_by_window_class": "[hl]Only North America moves its class mix from {trend_from}, toward CVT, {na_cvt_2023} of its aircraft in the latest complete window; Europe's and Asia-Pacific's changes are not detected[/hl]",
    "q3_region_mix_by_window_units": "[hl]Five to six units rise in North America (p {na_u56_p}) and seven to eight in Europe (p {eu_u78_p}); nine or more in Asia-Pacific is not detected[/hl]",
    "q3_region_mix_by_window_tilting": "[hl]North America's tilting share stays between {na_tilt_lo} and {na_tilt_hi} in the windows read, the highest of the three regions all years together[/hl]",
    "q3_region_countries": "[hl]The United States, China and Germany hold {top3_rep_share} of the representative patents, the United States alone {us_rep_share}; a country with a few dozen patents weighs little in its region's shares[/hl]",
    "q3_firm_successions": "A firm's next aircraft usually stays in Lift + Cruise ({slc_stay} of the successions) and usually leaves Tilt Wing (only {tw_stay} stay, most going to Tilt Propulsor).",
}
