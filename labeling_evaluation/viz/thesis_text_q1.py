"""Thesis question 1, growth: the text (THESIS_CONTRACT.md §1, §2). Numbers are {placeholders} from thesis_q1.numbers."""

METHOD = """- **Objective:** How fast eVTOL patenting grows against aeronautics, transport and all patenting, when it turned, and where it grows.
- **Data and unit:** {unique_s} unique aircraft by priority year and applicant region, {representative_s} patents and three baselines in families.
- **Procedure:** Series scaled to their 2005 to 2009 mean; regional counts corrected for publication lag.
- **Test:** Log-linear fit over 2005 to 2023; doubling-time ratio with bootstrap interval; turning point by two-segment fit.
- **Limit:** Only architecture patents are counted, and the two latest years are not yet fully published."""

RESULTS = [
    dict(sub="A", title="Growth of the field", text="""Filing takes off in {turn_pat_year}, the year chosen by {turn_pat_boot} of the resampled fits ([fig:q1_filings_per_year]). In 2015 the dataset gains {ac_2015} unique aircraft. In 2018 it gains {ac_2018}, and the count holds near that level to the last complete year. The unique aircraft turn in {turn_ac_year}. The resamples place that year anywhere from {turn_ac_lo} to {turn_ac_hi}. The fall at the right edge is the publication lag, not a decline. The Uber Elevate paper of late 2016 stands beside the rise as a coincidence in time, never tested as a cause.

eVTOL is the fastest-growing series ([fig:q1_growth_rates]), its architecture patents doubling every {dbl_fam} years against {dbl_b64} for aeronautics. Transport doubles every {dbl_secb} years and all patenting every {dbl_all} ([tab:q1_growth_rates_table]). Counted in families, eVTOL grows {gr_fam_b64} times as fast as aeronautics ({gr_fam_b64_ci}). The lead rests partly on the latest years, and with the fit ended at 2019 the ratio falls to {gr_fam_b64_19}. Its interval, {gr_fam_b64_19_ci}, still leaves eVTOL the faster series. The comparison is conservative, because aeronautics counts the component patents and cargo drones that the labelled dataset screens out."""),
    dict(sub="B", title="Entry by region", text="""North America's share of new aircraft halves between 2021 and 2023, and publication lag does not explain it. Its share falls from {na_share_2021} to {na_share_2023} over those two years ([fig:q1_na_drop_is_real]). Corrected for lag, the share of 2023 stays at {na_share_2023_corr}. The snapshot already sees {vis_2023_lo} to {vis_2023_hi} of every region's aircraft of that year. North America's count falls from {na_2021} to {na_2023} aircraft over the same two years. Lag explains only the two latest years, whose {ap_2526} aircraft are all Asia-Pacific's.

The order of entry by class is read in Q3 ([fig:q3_region_entry_lag]). Asia-Pacific files Lift + Cruise, Tilt Propulsor and Tilt Wing {ap_delay_range} years after North America. On Combined Vectored Thrust (CVT) no delay is detected, {ap_delay_cvt} years with an interval of {ap_delay_cvt_ci} that takes in zero, because North America itself came late to that class. No European delay is detected on any class.

Of the {fa_n} designs, {fa_share} are not actively protected at the snapshot ([fig:q1_in_force_status]). No patent that shows them is in force. The share grows with age. It is {fa_c_2023} in the youngest complete cohort. It is {fa_c_le2011} in the oldest. By architecture it runs from {fa_mr} for Multicopter to {fa_cvt} for CVT. The architectures differ with p {fa_p}. At the US office the share is {fo_us}, over {fo_n_us} designs. At the other offices it is {fo_else}, over {fo_n_else} designs. The two differ with p {fo_p}."""),
]

ANSWER = """eVTOL patenting grows faster than patenting at large and a little faster than aeronautics, with its architecture patents doubling every {dbl_fam} years against {dbl_b64} for aeronautics. The turning point is {turn_pat_year} for the patents and {turn_ac_year} for the unique aircraft. North America's share of new aircraft halves between 2021 and 2023, a fall the publication lag does not explain. Asia-Pacific holds its yearly count and enters the older classes {ap_delay_range} years after North America. Of all designs, {fa_share} are no longer actively protected, more the older the design."""

APPENDIX = {
    "q1_growth_rates_table": "eVTOL architecture patents double every {dbl_fam} years, against {dbl_b64} for aeronautics. Against all patenting they grow {gr_fam_all} times as fast, and the unique aircraft double every {dbl_ac} years.",
    "q1_na_drop_is_real": "North America's share of the year falls from {na_share_2021} to {na_share_2023} in two years, and its count falls with it.",
    "q1_in_force_status": "Of the {fa_n} designs, {fa_share} are not actively protected. The architectures differ with p {fa_p}.",
}
