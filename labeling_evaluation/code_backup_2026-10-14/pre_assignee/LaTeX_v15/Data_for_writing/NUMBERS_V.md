# NUMBERS_V: Analysis V (assignees and regions)

Source tags: `CSV` = Data_for_writing/csv/<name>.csv; `nb53` = notebooks/53_thesis_figures_v2_part5.ipynb (`viz/analysis5.py:numbers_for_text`); `q2.numbers`, `q3.numbers`, `q7.numbers` = `viz/thesis_q2.py`, `thesis_q3.py`, `thesis_q7.py` numbers(ctx). Every value was recomputed from the frames when this file was written.

## (a) The largest assignees

Source: `viz.thesis_q2._frames(ctx)['sizes']` and `['cov']` (the data of `q2_largest_filers_share`, CSV `q2_largest_filers_share.csv`).

- The 4 largest assignees (Bell / Textron 60, Airbus 21, Kitty Hawk 11, Shenfeng Aviation 10 designs) hold 102 designs: 16.3 % of the 627 designs and 23.1 % of the 441 designs of named assignees.
- Named assignees: 199 ("named organisations"); together 441 designs, 70.3 % of the 627; individual inventors hold the rest (186 designs).
- Assignees with exactly one design: 130 of 199 (65.3 %), 130 designs (20.7 % of all designs).
- Bands:

| aircraft per assignee | assignees | aircraft | share of the analysis set | cumulative assignees | cumulative aircraft |
|---|---|---|---|---|---|
| 10 or more | 4 | 102 | 0.163 | 4 | 102 |
| 5-9 | 12 | 80 | 0.128 | 16 | 182 |
| 2-4 | 53 | 129 | 0.206 | 69 | 311 |
| 1 | 130 | 130 | 0.207 | 199 | 441 |

## (b) Entry lag: Europe and Asia-Pacific against North America

Source: `viz.thesis_q3._frames(ctx)['off']` (all years to the last complete year) and `['off16']` (priority years 2016 onward); CSV `q3_region_entry_lag.csv` holds the five drawn architectures. Offset = median priority year of the region minus North America's; positive = later. Interval = 95 % bootstrap, 2000 draws, seed 42 (`lib/regional.py`), rounded to 1 decimal. 'Excludes zero' means the rounded interval is entirely above or below 0; a rounded bound of +0.0 is marked.

| priority years | architecture | region | aircraft | offset vs North America (years) | interval | excludes zero | note |
|---|---|---|---|---|---|---|---|
| all years to 2023 | Combined vectored thrust | Europe | 25 | -2.0 | -3.0 to +1.0 | no |  |
| all years to 2023 | Combined vectored thrust | Asia-Pacific | 24 | -1.0 | -3.0 to +1.0 | no |  |
| all years to 2023 | Hoverbike | Europe | 7 | 0.0 | -2.0 to +2.0 | no |  |
| all years to 2023 | Hoverbike | Asia-Pacific | 5 | -2.0 | -6.0 to +2.0 | no |  |
| all years to 2023 | Lift + Cruise | Europe | 51 | 1.0 | +0.0 to +4.0 | no | lower bound +0.0 (rounded to 1 decimal) |
| all years to 2023 | Lift + Cruise | Asia-Pacific | 49 | 2.0 | +1.0 to +4.0 | yes |  |
| all years to 2023 | Multicopter | Europe | 14 | 1.5 | -1.5 to +14.5 | no |  |
| all years to 2023 | Multicopter | Asia-Pacific | 14 | 4.0 | +1.5 to +16.0 | yes |  |
| all years to 2023 | Tilt Frame | Europe | 8 | 1.0 | -3.0 to +4.0 | no |  |
| all years to 2023 | Tilt Frame | Asia-Pacific | 5 | 2.0 | -7.0 to +6.0 | no |  |
| all years to 2023 | Tilt Propulsor | Europe | 30 | 0.5 | -2.0 to +2.0 | no |  |
| all years to 2023 | Tilt Propulsor | Asia-Pacific | 28 | 3.0 | +1.0 to +4.5 | yes |  |
| all years to 2023 | Tilt Wing | Europe | 11 | 4.0 | -2.5 to +5.0 | no |  |
| all years to 2023 | Tilt Wing | Asia-Pacific | 11 | 4.0 | +1.0 to +5.0 | yes |  |
| 2016 to 2023 | Combined vectored thrust | Europe | 20 | -1.0 | -2.0 to +0.0 | no |  |
| 2016 to 2023 | Combined vectored thrust | Asia-Pacific | 23 | -1.0 | -3.0 to +0.0 | no |  |
| 2016 to 2023 | Lift + Cruise | Europe | 42 | 1.0 | -0.5 to +3.0 | no |  |
| 2016 to 2023 | Lift + Cruise | Asia-Pacific | 44 | 1.0 | +0.0 to +3.0 | no | lower bound +0.0 (rounded to 1 decimal) |
| 2016 to 2023 | Multicopter | Europe | 10 | 1.0 | -2.0 to +3.0 | no |  |
| 2016 to 2023 | Multicopter | Asia-Pacific | 12 | 2.0 | -1.0 to +4.0 | no |  |
| 2016 to 2023 | Tilt Propulsor | Europe | 19 | 0.0 | -1.0 to +3.0 | no |  |
| 2016 to 2023 | Tilt Propulsor | Asia-Pacific | 24 | 2.0 | +0.0 to +4.0 | no | lower bound +0.0 (rounded to 1 decimal) |
| 2016 to 2023 | Tilt Wing | Europe | 8 | 3.5 | +1.0 to +5.0 | yes |  |
| 2016 to 2023 | Tilt Wing | Asia-Pacific | 11 | 3.0 | +0.0 to +4.0 | no | lower bound +0.0 (rounded to 1 decimal) |
| 2016 to 2023 | all architectures | Europe | 127 | 0.0 | none (all-architecture row) | no interval |  |
| 2016 to 2023 | all architectures | Asia-Pacific | 130 | 1.0 | none (all-architecture row) | no interval |  |

**Check of your expectation.** Over all years only Asia-Pacific excludes zero: Lift + Cruise (+1.0 to +4.0), Tilt Propulsor (+1.0 to +4.5), Tilt Wing (+1.0 to +5.0) and Multicopter (+1.5 to +16.0). Confirmed. No Europe interval excludes zero over all years; Lift + Cruise Europe (+0.0 to +4.0) only touches it. Combined vectored thrust, Hoverbike and Tilt Frame include zero in both regions (Hoverbike and Tilt Frame have 5 to 8 designs in a region and are not drawn). **On 2016 onward the picture changes**: only Tilt Wing in Europe excludes zero (+1.0 to +5.0). Lift + Cruise, Tilt Propulsor and Tilt Wing in Asia-Pacific have a lower bound of +0.0, so they touch zero; Multicopter and combined vectored thrust include it. The all-architectures rows (2016 onward) carry no interval.

## Other numbers quoted by the Results text of Analysis V

### Region shares of designs (nb53)

| cohort | designs | North America | Europe | Asia-Pacific | others | sum of the three |
|---|---|---|---|---|---|---|
| all years | 627 | 39.9 % | 28.2 % | 29.7 % | 2.2 % | 97.8 % |
| 2012-15 | 58 | 50.0 % | 39.7 % | 10.3 % | 0.0 % | 100.0 % |
| 2016-19 | 213 | 48.8 % | 30.0 % | 17.8 % | 3.3 % | 96.7 % |
| 2020-23 | 237 | 32.5 % | 26.6 % | 38.8 % | 2.1 % | 97.9 % |
| 2024-26 (partial) | 56 | 8.9 % | 21.4 % | 69.6 % | 0.0 % | 100.0 % |

### Entrants and incumbents per cohort (nb53; `viz.thesis_q2._frames(ctx)['fw']`)

An entrant is an assignee whose earliest cohort in the dataset is this cohort: the cohort of its first design (by the priority year of the design's representative patent), not of its first patent. The assignee of a design is the FIRST assignee of its representative patent's PatSeer string (co-assignees after ';' are ignored), resolved to a canonical name by the grouper where it has one, else read from the string; not the assignee with the most patents. Individual inventors are not assignees here (they are not counted as entrants).

| cohort | assignees active | entrants | incumbents |
|---|---|---|---|
| <= 2011 | 14 | 14 | 0 |
| 2012-15 | 22 | 19 | 3 |
| 2016-19 | 64 | 57 | 7 |
| 2020-23 | 101 | 82 | 19 |
| 2024-26 (partial) | 40 | 27 | 13 |

### North America tilting share without its largest assignee (nb53; `viz.thesis_q7._data(ctx)['ln']`, `['ts']`)

- Largest assignee left out: Bell / Textron; tilting share 67.0 % with, 60.0 % without; chi-square p < 0.001 with all assignees, 0.023 without.

### Analysis V.1 and V.2 (`q2.numbers`)

| key | value |
|---|---|
| `n_aircraft` | 627 |
| `n_rep` | 879 |
| `w1619` | 2016-19 |
| `w2023` | 2020-23 |
| `w1215` | 2012-15 |
| `co_share` | 63 % |
| `co_n` | 397 |
| `uni_share` | 7 % |
| `uni_n` | 44 |
| `ind_share` | 30 % |
| `ind_n` | 186 |
| `co_share_rep` | 75 % |
| `ind_share_rep` | 20 % |
| `ind_w1` | 70 % |
| `ind_w4` | 24 % |
| `org_n` | 199 |
| `org_share` | 70 % |
| `org_aircraft` | 441 |
| `top_n` | 4 |
| `top_aircraft` | 102 |
| `top_share` | 16 % |
| `next_n` | 12 |
| `next_aircraft` | 80 |
| `single_n` | 130 |
| `single_share_of_orgs` | 65 % |
| `rated_n` | 22 |
| `new_1619` | 57 |
| `cont_1619` | 7 |
| `new_2023` | 82 |
| `cont_2023` | 19 |
| `class_min` | 20 |
| `cell_min` | 10 |
| `conc_n` | 7 |
| `max_top_share` | 21 % |
| `min_eff` | 13 |
| `big4_min_eff` | 24 |
| `slc_eff` | 57 |
| `tb_share` | 21 % |
| `tr_share` | 18 % |
| `cvt_share` | 16 % |
| `top_firm` | Bell / Textron |
| `top_firm_aircraft` | 60 |
| `tr_win_share` | 34 % |
| `tr_win` | 2016-19 |
| `slc_win_share` | 29 % |
| `slc_win_n` | 17 |
| `lev_min_firm` | 3 |
| `lev_min_window` | 30 |
| `lev1_pp` | 2.6 |
| `lev1_class` | Lift + Cruise |
| `lev2_pp` | 1.1 |
| `lev2_firm` | Airbus |
| `lev2_class` | Lift + Cruise |
| `lev_win_pp` | 5.2 |
| `lev_win_firm` | Bell / Textron |
| `lev_win_window` | 2016-19 |
| `bell_tr_pp` | 2.2 |
| `bell_cvt_pp` | 1.2 |
| `bell_tw_pp` | 0.5 |
| `bell_slc_n` | 1 |
| `lev2_in_class` | 12 |
| `lev2_aircraft` | 21 |
| `lev2_win_pp` | 3.0 |
| `lev2_win` | 2012-15 |
| `lev2_win_n` | 58 |
| `test_min` | 20 |
| `first_1619` | 98 |
| `named_1619` | 155 |
| `first_2023` | 120 |
| `named_2023` | 181 |
| `first_share_1619` | 63 % |
| `first_share_2023` | 66 % |
| `p_1619` | 0.017 |
| `p_2023` | 0.07 |
| `p_wo_1619` | 0.59 |
| `p_wo_2023` | 0.38 |
| `big_1619` | Bell / Textron |
| `big_ret_1619` | 33 |
| `ret_1619` | 57 |
| `ret_tr_1619` | 35 % |
| `new_tr_1619` | 13 % |
| `new_slc_1619` | 32 % |
| `ret_slc_1619` | 14 % |
| `tw_ent_1619` | 7 |
| `ent_1619` | 57 |
| `tw_ent_2023` | 9 |
| `ent_2023` | 82 |
| `tw_ent_share_1619` | 12 % |
| `tw_ent_share_2023` | 11 % |
| `tw_air_1619` | 11 % |
| `tw_air_2023` | 8 % |
| `tw_fisher_p` | 0.33 |
| `tw_uni_2023` | 3 |
| `tw_single_2023` | 6 |
| `ent_uni_share_2023` | 18 % |
| `ent_single_share_2023` | 68 % |
| `tw_uni_share_2023` | 33 % |
| `tw_single_share_2023` | 67 % |

### Analysis V.3 (`q3.numbers`)

| key | value |
|---|---|
| `all_n` | 627 |
| `three_n` | 613 |
| `three_share` | 98 % |
| `other_n` | 14 |
| `na_n` | 250 |
| `eu_n` | 177 |
| `ap_n` | 186 |
| `rep_n` | 879 |
| `thin_n` | 10 |
| `trend_from` | 2012 |
| `trend_to` | 2023 |
| `last_complete` | 2023 |
| `lag_min_cell` | 5 |
| `lag_draws` | 2 000 |
| `lag_since` | 2016 |
| `lag_perms` | 5 000 |
| `top3_rep_share` | 69 % |
| `us_rep_share` | 42 % |
| `ap_top2` | China and Japan |
| `eu_top3` | Germany, United Kingdom and France |
| `na_tr_all` | 32 % |
| `na_slc_all` | 18 % |
| `eu_slc_all` | 30 % |
| `ap_slc_all` | 34 % |
| `na_tilt_all` | 67 % |
| `eu_tilt_all` | 46 % |
| `ap_tilt_all` | 49 % |
| `p_class_all` | < 0.001 |
| `p_tilt_all` | < 0.001 |
| `p_units_all` | 0.07 |
| `slc_2023_n` | 73 |
| `cvt_2023_n` | 53 |
| `tr_2023_n` | 47 |
| `na_slc_2023` | 18 % |
| `na_cvt_1215` | 24 % |
| `na_cvt_1619` | 10 % |
| `na_cvt_2023` | 36 % |
| `na_cvt_rho` | +0.24 |
| `na_cvt_p` | < 0.001 |
| `na_tr_1215` | 34 % |
| `na_tr_2023` | 29 % |
| `na_tr_p` | 0.49 |
| `na_tr_old` | 43 % |
| `na_old_n` | 35 |
| `na_u13_1215` | 48 % |
| `na_u13_2023` | 15 % |
| `na_u13_p` | < 0.001 |
| `na_u56_1215` | 10 % |
| `na_u56_2023` | 35 % |
| `na_u56_p` | < 0.001 |
| `na_tilt_lo` | 63 % |
| `na_tilt_hi` | 73 % |
| `eu_slc_1215` | 17 % |
| `eu_slc_2023` | 40 % |
| `eu_slc_p` | 0.07 |
| `eu_cvt_2023` | 19 % |
| `eu_cvt_p` | 0.91 |
| `eu_u78_1215` | 5 % |
| `eu_u78_2023` | 30 % |
| `eu_u78_p` | 0.015 |
| `ap_1215_n` | 6 |
| `ap_slc_1619` | 28 % |
| `ap_slc_2023` | 37 % |
| `ap_u9_1619` | 12 % |
| `ap_u9_2023` | 31 % |
| `ap_u9_p` | 0.08 |
| `ap_tilt_1619` | 54 % |
| `ap_tilt_2023` | 46 % |
| `p_units_1215` | 0.86 |
| `p_units_1619` | 0.45 |
| `p_units_2023` | 0.003 |
| `p_class_2023` | < 0.001 |
| `na_median` | 2018 |
| `eu_median` | 2019 |
| `ap_median` | 2020 |
| `follow_years` | one and two years |
| `na_lag` | 2 |
| `ap_lag` | 1 |
| `na_office` | United States |
| `ap_office` | China |
| `na_office_share` | 96 % |
| `ap_office_share` | 50 % |
| `lag_classes_n` | 5 |
| `lag_classes_all` | 7 |
| `ap_delay_range` | 2-4 |
| `ap_slc_lag` | +2 (+1 to +4) |
| `ap_tr_lag` | +3 (+1 to +4.5) |
| `ap_tw_lag` | +4 (+1 to +5) |
| `ap_cvt_lag` | -1 (-3 to +1) |
| `ap_slc_off` | 2 |
| `ap_tr_off` | 3 |
| `ap_tw_off` | 4 |
| `ap_cvt_off` | -1 |
| `na_cvt_median` | 2021 |
| `eu_cvt_lag` | -2 (-3 to +1) |
| `eu_all_reach_zero` | every |
| `lag_constancy_p` | 0.15 |
| `na_median16` | 2019 |
| `eu_median16` | 2019 |
| `ap_median16` | 2020 |
| `ap_tr_lag16` | +2 (0 to +4) |
| `ap_slc_lag16` | +1 (0 to +3) |
| `ap_tw_lag16` | +3 (0 to +4) |
| `ap_tr_off16` | 2 |
| `ap_slc_off16` | 1 |
| `ap_tw_off16` | 3 |
| `ap_16_reach_zero` | Lift + Cruise, Tilt Propulsor and Tilt Wing |
| `eu_cvt_off` | -2 |
| `eu_cvt_off16` | -1 |
| `na_peak_year` | 2017 |
| `na_peak_n` | 32 |
| `eu_peak_year` | 2019 |
| `eu_peak_n` | 27 |
| `ap_peak_year` | 2020 |
| `ap_peak_n` | 35 |
| `na_share_2021` | 44 % |
| `na_share_2023` | 22 % |
| `na_share_2023_corr` | 22 % |
| `succ_n` | 240 |
| `succ_firms` | 69 |
| `succ_min` | 10 |
| `slc_stay` | 61 % |
| `tr_stay` | 56 % |
| `cvt_stay` | 44 % |
| `tw_stay` | 17 % |
| `tw_succ` | 23 |
| `tw_firms` | 13 |
| `tw_to_tr` | 44 % |
| `tw_to_slc` | 22 % |
| `big_firm` | Bell / Textron |
| `big_succ` | 59 |

### Analysis V.4, regional keys (`q7.numbers`)

| key | value |
|---|---|
| `r_na_f_last` | 48 % |
| `r_eu_f_last` | 57 % |
| `r_ap_f_last` | 46 % |
| `r_na_f_early` | 28 % |
| `r_na_f_mid` | 27 % |
| `r_p_f_early` | 0.34 |
| `r_p_f_mid` | 0.13 |
| `r_p_f_last` | 0.35 |
| `r_na_rho` | +0.20 |
| `r_na_rho_p` | 0.003 |
| `r_p_units_last` | 0.003 |
| `r_big` | Bell / Textron |
| `r_big_n` | 60 |
| `r_na_n` | 250 |
| `r_big_tr` | 27 |
| `r_na_tr` | 80 |
| `r_na_tilt` | 67 % |
| `r_eu_tilt` | 46 % |
| `r_ap_tilt` | 49 % |
| `r_na_tilt_wo` | 60 % |
| `r_p_tilt_wo` | 0.023 |
| `r_na_tp_wo` | 28 % |
| `r_eu_tp` | 17 % |
| `r_ap_tp` | 21 % |
| `r_p_tp_wo` | 0.035 |
| `r_p_tilt_all` | < 0.001 |
| `r_p_tp_all` | < 0.001 |
| `px_firms` | 16 |
| `px_firm_min` | 5 |
| `px_same` | 0.48 |
| `px_diff` | 0.52 |
| `px_p` | 0.69 |
| `px_eu` | 0.40 |
| `px_na` | 0.54 |
| `px_ap` | 0.52 |

## Entry lag with two decimals (follow-up)

Source: `viz/latex_v15_partv.py:lag_two_decimals`, the bootstrap of `lib/regional.lag_offsets` without the rounding (same frames, same seed 42, same draw order; **2000 draws**: the entry above, which says 200, is wrong). Asserted equal, after rounding to 1 decimal, to `viz.thesis_q3._frames(ctx)['off']` and `['off16']`, so no result moves. Offset = median priority year of the region minus that of North America; lower and upper bound = 2.5 and 97.5 percentiles of the bootstrap offsets; 'lower bound above zero' tests the two-decimal value; the marker flags every lower bound whose 1-decimal value is 0.0. CSV: `q3_region_entry_lag_two_decimals.csv`.

### 2016 to 2023: architectures drawn in `q3_region_entry_lag`

| architecture | region | designs | offset | lower bound | upper bound | lower bound above zero | marker |
|---|---|---|---|---|---|---|---|
| Combined vectored thrust | Europe | 20 | -1.00 | -2.00 | +0.00 | no |  |
| Combined vectored thrust | Asia-Pacific | 23 | -1.00 | -3.00 | +0.00 | no |  |
| Lift + Cruise | Europe | 42 | +1.00 | -0.50 | +3.00 | no |  |
| Lift + Cruise | Asia-Pacific | 44 | +1.00 | +0.00 | +3.00 | no | lower bound rounds to +0.0 |
| Multicopter | Europe | 10 | +1.00 | -2.00 | +3.00 | no |  |
| Multicopter | Asia-Pacific | 12 | +2.00 | -1.00 | +4.00 | no |  |
| Tilt Propulsor | Europe | 19 | +0.00 | -1.00 | +3.00 | no |  |
| Tilt Propulsor | Asia-Pacific | 24 | +2.00 | +0.00 | +4.00 | no | lower bound rounds to +0.0 |
| Tilt Wing | Europe | 8 | +3.50 | +1.00 | +5.00 | yes |  |
| Tilt Wing | Asia-Pacific | 11 | +3.00 | +0.00 | +4.00 | no | lower bound rounds to +0.0 |

### all years to 2023: architectures drawn in `q3_region_entry_lag`

| architecture | region | designs | offset | lower bound | upper bound | lower bound above zero | marker |
|---|---|---|---|---|---|---|---|
| Combined vectored thrust | Europe | 25 | -2.00 | -3.00 | +1.00 | no |  |
| Combined vectored thrust | Asia-Pacific | 24 | -1.00 | -3.00 | +1.00 | no |  |
| Lift + Cruise | Europe | 51 | +1.00 | +0.00 | +4.00 | no | lower bound rounds to +0.0 |
| Lift + Cruise | Asia-Pacific | 49 | +2.00 | +1.00 | +4.00 | yes |  |
| Multicopter | Europe | 14 | +1.50 | -1.50 | +14.50 | no |  |
| Multicopter | Asia-Pacific | 14 | +4.00 | +1.50 | +16.00 | yes |  |
| Tilt Propulsor | Europe | 30 | +0.50 | -2.00 | +2.00 | no |  |
| Tilt Propulsor | Asia-Pacific | 28 | +3.00 | +1.00 | +4.50 | yes |  |
| Tilt Wing | Europe | 11 | +4.00 | -2.50 | +5.00 | no |  |
| Tilt Wing | Asia-Pacific | 11 | +4.00 | +1.00 | +5.00 | yes |  |

### all years to 2023: architectures the figure does not draw (fewer than 10 designs in a region)

| architecture | region | designs | offset | lower bound | upper bound | lower bound above zero | marker |
|---|---|---|---|---|---|---|---|
| Hoverbike | Europe | 7 | +0.00 | -2.00 | +2.00 | no |  |
| Hoverbike | Asia-Pacific | 5 | -2.00 | -6.00 | +2.00 | no |  |
| Tilt Frame | Europe | 8 | +1.00 | -3.00 | +4.01 | no |  |
| Tilt Frame | Asia-Pacific | 5 | +2.00 | -7.00 | +6.00 | no |  |

