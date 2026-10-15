# NUMBERS_I — Analysis I (evidence base)

Generated 2026-10-13 by notebook 48 (`viz/latex_v15.py:write_numbers_I`) from the current inputs (external inputs: `script`), 627 designs, snapshot 2026-06-08. Every value is computed when this file is written; the source column names the CSV or the code that holds it. A value marked **new** is a number the earlier text did not quote.

## 1. Growth

### Doubling times, 2005-2023 (years, 95 % interval)

| number | value | source |
|---|---|---|
| eVTOL architecture patents (families) | 3.6 (3.0 to 4.4) | csv/q1_growth_rates.csv; csv/numbers_I_growth.csv; q1.numbers()['dbl_fam'] |
| eVTOL unique designs | 3.7 (2.9 to 5.0) | csv/numbers_I_growth.csv; q1.numbers()['dbl_ac'] |
| aeronautics (CPC B64) | 4.7 (4.1 to 5.6) | csv/numbers_I_growth.csv; q1.numbers()['dbl_b64'] |
| transport and operations (CPC section B) | 6.4 (5.4 to 7.9) | csv/numbers_I_growth.csv; q1.numbers()['dbl_secb'] |
| all patenting | 10.7 (9.6 to 12.2) | csv/numbers_I_growth.csv; q1.numbers()['dbl_all'] |
| growth per year, eVTOL architecture patents | 21 % | csv/numbers_I_growth.csv |

### Growth-rate ratio of eVTOL architecture patents (times as fast, 95 % interval)

| number | value | source |
|---|---|---|
| against aeronautics (CPC B64) | 1.32 (1.20 to 1.46) | csv/numbers_I_growth.csv; q1.numbers()['gr_fam_b64'], ['gr_fam_b64_ci'] |
| against transport and operations | 1.79 (1.61 to 1.94) | csv/numbers_I_growth.csv; q1.numbers()['gr_fam_secb'] |
| against all patents | 3.0 (2.71 to 3.35) | csv/numbers_I_growth.csv; q1.numbers()['gr_fam_all'] |
| against aeronautics with the fit ended at 2019 (sensitivity) | 1.26 (1.07 to 1.41) | q1.numbers()['gr_fam_b64_19'], ['gr_fam_b64_19_ci'] |

### Turning point (two-segment log fit, residual bootstrap, 5 000 draws as set in lib/growth.py)

| number | value | source |
|---|---|---|
| representative patents | 2016 (jump x3.38; chosen by 90 % of the resampled fits; 95 % range of the resampled year 2015 to 2018) | csv/numbers_I_turning_points.csv; lib/growth.py:turning_point |
| unique aircraft | 2017 (jump x1.79; chosen by 23 % of the resampled fits; 95 % range of the resampled year 2010 to 2020) | csv/numbers_I_turning_points.csv; lib/growth.py:turning_point |
| aircraft per 1 000 B64 | 2013 (jump x0.50; chosen by 18 % of the resampled fits; 95 % range of the resampled year 2009 to 2020) | csv/numbers_I_turning_points.csv; lib/growth.py:turning_point |

## 2. Active protection (every priority year; actively protected = any patent that shows the design is in force at the snapshot)

### The 604 designs of the nine architectures of ten designs or more (the designs plotted in `q1_in_force_status`)

| number | value | source |
|---|---|---|
| designs plotted | 604 | csv/q1_in_force_status.csv (sum of n) |
| not actively protected, all 604 | 184 of 604 = 30.5 % | csv/q1_in_force_status.csv; csv/numbers_I_active_protection_by_architecture.csv |
| US office: designs, share not actively protected | 353 designs, 81 = 22.9 % | csv/q1_in_force_status.csv |
| other offices: designs, share not actively protected | 251 designs, 103 = 41.0 % | csv/q1_in_force_status.csv |
| test of the architecture (nine architectures x not actively protected) | chi-square 13.21, df 8, p 0.105 | lib/association.chi2_test on the 604 designs; q1.numbers()['fa_p'] |
| test of the office (US against other offices x not actively protected), on the 604 | chi-square 21.82, df 1 (Yates correction, 2 x 2), p 3.0e-06 | lib/association.chi2_test on the 604 designs; **new** |
| the same office test on all 625 designs with an architecture (the earlier text) | chi-square 24.79, df 1, p 6.4e-07; US 22.8 % of 364, other offices 41.8 % of 261 | q1.numbers()['fo_us'], ['fo_else'], ['fo_n_us'], ['fo_n_else'], ['fo_p'] |

Share not actively protected per architecture (the nine plotted):

| architecture | code | designs | not actively protected | share |
|---|---|---|---|---|
| Lift + Cruise | SLC | 165 | 53 | 32 % |
| Tilt Propulsor | TP | 151 | 40 | 26 % |
| Combined Vectored Thrust | CVT | 106 | 31 | 29 % |
| Tilt Wing | TW | 56 | 17 | 30 % |
| Multicopter | MR | 48 | 16 | 33 % |
| Pitch-to-Cruise | PTC | 25 | 3 | 12 % |
| Tilt Frame | TF | 24 | 13 | 54 % |
| Hoverbike | HB | 19 | 8 | 42 % |
| Personal Flying Vehicle | PFV | 10 | 3 | 30 % |

### Designs not plotted in `q1_in_force_status`

| number | value | source |
|---|---|---|
| DS (Deflected Slipstream) | 4 designs, 25 % not actively protected | csv/numbers_I_active_protection_by_architecture.csv |
| RC (Rotorcraft) | 9 designs, 44 % not actively protected | csv/numbers_I_active_protection_by_architecture.csv |
| SRW (Stopped/Slowed Rotor Wing) | 8 designs, 38 % not actively protected | csv/numbers_I_active_protection_by_architecture.csv |
| no architecture read | 2 designs (read for legal status, see the 627 line) | viz/frames.py:force_frame drops a design without an architecture |
| designs not plotted, total | 23 of 627 (604 plotted) |  |

### The share if every one of the 627 designs is read

| number | value | source |
|---|---|---|
| designs with a legal status read | 627 | frames.aircraft_patents, every design has at least one patent with a status |
| not actively protected | 194 of 627 = 30.9 % | **new** |
| (for comparison) the 625 designs with an architecture | 192 of 625 = 30.7 % | q1.numbers()['fa_share'], ['fa_n'] |

Share not actively protected per priority-year cohort (the age effect):

| cohort | designs (625 read) | share not actively protected (625) | designs (604 plotted) | share not actively protected (604) |
|---|---|---|---|---|
| <= 2011 | 63 | 71.4 % | 61 | 72.1 % |
| 2012-15 | 58 | 43.1 % | 57 | 42.1 % |
| 2016-19 | 211 | 34.6 % | 203 | 34.5 % |
| 2020-23 | 237 | 19.0 % | 230 | 18.3 % |
| 2024-26 (partial) | 56 | 7.1 % | 53 | 7.5 % |

## 3. The acquisition funnel of section 4.1

| step | count | source |
|---|---|---|
| patent query hits (PatSeer, snapshot 2026-06-08) | 1639 | ds.counts['patents_acquired'] |
| disapproved at labelling (no usable image, pure UAV, out of the domain, other) | 530 | difference |
| after the patent triage T1: patents approved at labelling | 1109 | ds.counts['patents_wizard_approved'] |
| approved patents whose every aircraft is 'but similar' (UAV or not electric), set aside | 230 | ds.counts['patents_gated_out'] |
| representative patents (patent families) | 879 | ds.counts['patents_approved'] |
| aircraft observations (a patent can show several aircraft) | 963 | ds.counts['approved_variants'] |
| the 627 designs (unique aircraft), on primary patents | 627 | len(ctx.v); primary patents 543 |
| after the image triage T2: whole-aircraft figures approved | 1538 | ds.counts['approved_figures']; on 578 patents |

*Mapping of T1 and T2:* the repository names the stages above; **T1 = the patent triage at labelling (1 109 approved, then the domain gate to 879)** and **T2 = the figure approval (1 538 whole-aircraft figures on 578 patents)** is my reading of your two names. The 627 designs sit between them (a design needs approved figures). Tell me if your T1 or T2 is another step.

### The VFS eVTOL directory and the company map

| number | value | source |
|---|---|---|
| directory aircraft pages | 1229 | frames.directory_frame; csv/numbers_I_funnel.csv |
| kept by the corrected domain rules | 871 | frames.directory_frame()['in_domain'] (rules of Section 3.1.1 and the author's single-page rulings) |
| matched to a design (pages linked to a patent design, use = yes) | 97 pages, 99 designs | evtolnews_patent_links.csv, use = yes |
| of those pages, kept in the domain | 83 | frames.directory_frame() |
| index companies read in full (AAM Reality Index company map rows) | 43 | ari_firm_map / review/script_outputs/COMPANY_MAP.csv |
| companies the script matches to a company of the dataset (non-blank match) | 18 | notebooks/_build/yearscript/ari_rule.py |
| companies where the script's match equals the author's name | 35 of 43 | notebook 60, review/script_outputs/COMPANY_MAP.csv |
| index companies that file in the dataset | 22 | frames.ari_firms; csv/numbers_I_funnel.csv |
| of them, in the current index release with a first flight and entry date (the clock figure) | 14 | frames.ari_timeline; csv/q4_patent_vs_market_clock.csv |

*If any count differs from the ones you listed:* one reading differs. The directory's 1 229 pages, the 871 kept, the 97 matched pages, the 43 companies read and the 22 that file all match. The **35** is the number of the 43 companies on which the script's answer equals the author's, counting the companies both leave blank; the script returns a non-blank match for **18** of them. Say which of the two the text should print.

## 4. Checks requested on 2026-10-12 (no figure or text changed by them)

### Flown designs (TRL 5 or more)

- **Definition in the code** (`viz/thesis_q4.py:representativeness`): flown = `trl >= 5`, where `trl` is `frames.trl_frame(ds)`: the NASA TRL of each design from `0_labelling/inputs/trl/aircraft_trl.csv`, overridden, design by design, by the TRL of the rule-based scripts (the author's own reading where he reviewed the design) when `analysis.external_inputs` is `script` (`viz/script_inputs.py`, `review/script_outputs/TRL.csv`). A design without a TRL is TRL 2. TRL 3-4 (ground and wind-tunnel tests) is not flown; no design of the 627 sits at TRL 3 or 4 under the script inputs.
- **Sizes:** the earlier group (TRL above 2 on the earlier inputs) has 63 designs, of which 1 sit at TRL 3 or 4 and 62 at TRL 5 or more. The new group (TRL 5 or more on the script inputs) has 68 designs, none at TRL 3 or 4.
- **Why 68 against 63:** the TRL values differ between the two input sets, and the definition moves the TRL 3-4 design out. 10 designs are in the new group and were not in the old one, 5 were in the old one and are not in the new (63 + 10 - 5 = 68). A design moves from the old group to the rest when the script finds no flight sentence on its linked directory pages where the earlier reading had found one (and the reverse). They are listed below and in `csv/numbers_I_flown_group_difference.csv`.

| aircraft_id | company | architecture | TRL, earlier inputs | TRL, script inputs | in the old group (TRL above 2, earlier inputs) | in the new group (TRL 5 or more, script inputs) |
|---|---|---|---|---|---|---|
| US2018208305A1_ua1 | Bell / Textron | TR | 2 | 6 | False | True |
| US2020239134A1_ua1 | Bell / Textron | CVT | 2 | 6 | False | True |
| US2020391879A1_ua1 | Bell / Textron | TR | 2 | 6 | False | True |
| US2023118750A1_ua1 | Bell / Textron | TR | 2 | 6 | False | True |
| US2014158816A1_ua1 | DeLorean Aerospace | TR | 3 | 2 | True | False |
| US2020354048A1_ua1 | Embraer / Eve | SLC | 6 | 2 | True | False |
| US2021354816A1_ua1 | Embraer / Eve | TR | 2 | 6 | False | True |
| KR20230089903A_ua1 | KARI | CVT | 7 | 2 | True | False |
| US2025304249A1_ua1 | Leonardo | CVT | 2 | 6 | False | True |
| US2019135413A1_ua1 | Uber Elevate | CVT | 2 | 6 | False | True |
| GB201801766D0_ua1 | None | SLC | 5 | 2 | True | False |
| US2011042510A1_ua1 | None | TW | 2 | 6 | False | True |
| CN117985223A_ua1 | Changsha Huayu Xianxiang Aviation Technology | TR | 6 | 2 | True | False |
| US2024051687A1_ua1 | Katla Aero | SLC | 2 | 6 | False | True |
| WO2025109312A1_ua1 | Sora Aviation | TR | 2 | 6 | False | True |

### Flown index-firm group

- **Definition:** the designs of the index firms of the current AAM Reality Index release whose first flight, as the index prints it, is a year before 2026 (the index prints years only; a 2026 year is read as a plan, as in the clock figure). The other index firms, and the 22 - 14 firms with no row in the current release, go to the rest. The group has 42 designs of 12 firms.

Architecture groups behind "LC +21.5 pp, p 0.047" (flown index-firm designs against the rest, the five directory categories):

| directory category | flown index-firm designs | % of the flown index-firm designs | the rest | % of the rest | gap pp |
|---|---|---|---|---|---|
| VT | 17 | 40.5 | 349 | 59.7 | -19.2 |
| LC | 20 | 47.6 | 153 | 26.2 | 21.5 |
| WM | 3 | 7.1 | 45 | 7.7 | -0.5 |
| HB | 2 | 4.8 | 27 | 4.6 | 0.1 |
| ER | 0 | 0.0 | 9 | 1.5 | -1.5 |

chi-square on this 2 x 5 table: p 0.047. The two designs without an architecture group are in the rest of the other attributes but not in this table (the five rows add to 42 and 583, not 42 and 585).

Index firms and whether their first flight counts as flown:

| company | designs | first flight in the index (earliest year) | counts as flown before the snapshot | reason if not |
|---|---|---|---|---|
| Joby Aviation | 8 | 2018 | True |  |
| Guangzhou Ehang Intelligent Technology | 1 | 2018 | True |  |
| Embraer / Eve | 4 | 2025 | True |  |
| Honda | 9 | 2024 | True |  |
| AutoFlight | 2 | 2022 | True |  |
| Volocopter | 4 | 2021 | True |  |
| Wisk Aero | 4 | 2025 | True |  |
| Archer Aviation | 4 | 2023 | True |  |
| Beta Technologies | 1 | 2020 | True |  |
| Wollant Aviation | 2 | 2023 | True |  |
| Supernal | 4 |  | False | no first flight in the index |
| Ascendance Flight Technologies | 1 | 2027 | False | a planned first flight (after the index release of 2026) |
| Vertical Aerospace | 1 | 2023 | True |  |
| Wofei / Geely Aviation | 2 | 2023 | True |  |

### I.1 turning points and the lead from the first patent to the first flight

| series | turning point | 95 % range of the resampled year | share of the fits choosing it | jump factor |
|---|---|---|---|---|
| representative patents | 2016 | 2015 to 2018 | 90 % | x3.38 |
| unique aircraft | 2017 | 2010 to 2020 | 23 % | x1.79 |
| aircraft per 1 000 B64 | 2013 | 2009 to 2020 | 18 % | x0.50 |

(`unique aircraft` = the designs series; `representative patents` = the patent-families series.)

| company | first patent | first flight | years from the first patent to the first flight |
|---|---|---|---|
| Joby Aviation | 2013 | 2018 | 5 |
| Guangzhou Ehang Intelligent Technology | 2015 | 2018 | 3 |
| Embraer / Eve | 2018 | 2025 | 7 |
| Honda | 2018 | 2024 | 6 |
| AutoFlight | 2019 | 2022 | 3 |
| Volocopter | 2019 | 2021 | 2 |
| Wisk Aero | 2020 | 2025 | 5 |
| Archer Aviation | 2020 | 2023 | 3 |
| Beta Technologies | 2021 | 2020 | -1 |
| Wollant Aviation | 2022 | 2023 | 1 |
| Vertical Aerospace | 2024 | 2023 | -1 |
| Wofei / Geely Aviation | 2024 | 2023 | -1 |

- firms with a first flight on record (year 2026 or before): n = 12; with the first patent before the flight: n = 9; median lead among those 3 years (range 1 to 7); median over all 12: 3.0 years.
- 90th-percentile publication lag: 3 years (the largest of the three regions, `frames.publication_lag`). Median lead minus that lag: 0 years (`q5.numbers()['ff_visible']`), the "about 1 year" figure, on the same n = 9 firms. The lag is subtracted as one number, from the median, not firm by firm.

## 5. What each figure plots

| figure | what is plotted |
|---|---|
| q1_filings_per_year | 627 designs over the priority years 2005 (pooled with the earlier ones) to 2026; 625 have an architecture, 2 do not (grey segment); 879 patent families; cohort 2024-26 faded |
| q1_growth_rates | eVTOL architecture patents, aeronautics, transport and operations, all patents; 2005-2023 fitted, 2024-26 shown and never fitted |
| q4_patent_vs_market_clock | 14 index firms with a first patent here; first flight 13 firms, entry into service 10 firms |
| q1_in_force_status | 604 designs of the nine architectures, by office; 23 not plotted (see section 2) |
| q4_class_mix | patent dataset: <= 2011 63, 2012-15 58, 2016-19 211, 2020-23 237, 2024-26 (partial) 56; directory: <= 2011 70, 2012-15 126, 2016-19 393, 2020-23 387, 2024-26 (partial) 117 |
| q5_funding_vs_aircraft | 10 firms with a disclosed amount; Spearman rho +0.58, p 0.08 (not printed in the figure) |
| q5_patenting_vs_investment | four published periods of disclosed sector investment (2010-20, 2021, 2023, 2024 to August); no test |

## 6. Every number the Results text of Analysis I quotes

Placeholders of `viz/thesis_text_q1.py`, `thesis_text_q4.py` and `thesis_text_q5.py` (results, answer and appendix lines) with the value they take now. A value that differs from the old Results text is marked (was X); section 7 lists them one line each.

### Q1 growth and active protection

| key | value now | where used | sentence | source |
|---|---|---|---|---|
| `ac_2015` | 21 | results A (Growth of the field) | In 2015 the dataset gains {ac_2015} unique aircraft. | viz/thesis_q1.py:numbers() |
| `ac_2018` | 68 | results A (Growth of the field) | In 2018 it gains {ac_2018}, and the count holds near that level to the last complete year. | viz/thesis_q1.py:numbers() |
| `ap_2526` | 18 | results B (Entry by region) | Lag explains only the two latest years, whose {ap_2526} aircraft are all Asia-Pacific's. | viz/thesis_q1.py:numbers() |
| `ap_delay_cvt` | −1 | results B (Entry by region) | On Combined Vectored Thrust (CVT) no delay is detected, {ap_delay_cvt} years with an interval of {ap_delay_cvt_ci} that takes in zero, because North A… | viz/thesis_q1.py:numbers() |
| `ap_delay_cvt_ci` | −3 to +1 | results B (Entry by region) | On Combined Vectored Thrust (CVT) no delay is detected, {ap_delay_cvt} years with an interval of {ap_delay_cvt_ci} that takes in zero, because North A… | viz/thesis_q1.py:numbers() |
| `ap_delay_range` | 2 to 4 | results B (Entry by region) | Asia-Pacific files Lift + Cruise, Tilt Propulsor and Tilt Wing {ap_delay_range} years after North America. | viz/thesis_q1.py:numbers() |
| `dbl_ac` | 3.7 | appendix q1_growth_rates_table | Against all patenting they grow {gr_fam_all} times as fast, and the unique aircraft double every {dbl_ac} years. | viz/thesis_q1.py:numbers() |
| `dbl_all` | 10.7 | results A (Growth of the field) | Transport doubles every {dbl_secb} years and all patenting every {dbl_all} (). | viz/thesis_q1.py:numbers() |
| `dbl_b64` | 4.7 | results A (Growth of the field) | eVTOL is the fastest-growing series (), its architecture patents doubling every {dbl_fam} years against {dbl_b64} for aeronautics. | viz/thesis_q1.py:numbers() |
| `dbl_fam` | 3.6 | results A (Growth of the field) | eVTOL is the fastest-growing series (), its architecture patents doubling every {dbl_fam} years against {dbl_b64} for aeronautics. | viz/thesis_q1.py:numbers() |
| `dbl_secb` | 6.4 | results A (Growth of the field) | Transport doubles every {dbl_secb} years and all patenting every {dbl_all} (). | viz/thesis_q1.py:numbers() |
| `fa_c_2023` | 19 % | results B (Entry by region) | It is {fa_c_2023} in the youngest complete cohort. | viz/thesis_q1.py:numbers() |
| `fa_c_le2011` | 71 % | results B (Entry by region) | It is {fa_c_le2011} in the oldest. | viz/thesis_q1.py:numbers() |
| `fa_cvt` | 29 % (was 53 %) | results B (Entry by region) | By architecture it runs from {fa_mr} for Multicopter to {fa_cvt} for CVT. | viz/thesis_q1.py:numbers() |
| `fa_mr` | 33 % (was 31 %) | results B (Entry by region) | By architecture it runs from {fa_mr} for Multicopter to {fa_cvt} for CVT. | viz/thesis_q1.py:numbers() |
| `fa_n` | 625 (was 332) | results B (Entry by region) | Of the {fa_n} designs, {fa_share} are not actively protected at the snapshot (). | viz/thesis_q1.py:numbers() |
| `fa_p` | 0.105 (was 0.043) | results B (Entry by region) | The architectures differ with p {fa_p}. | viz/thesis_q1.py:numbers() |
| `fa_share` | 31 % (was 43 %) | results B (Entry by region) | Of the {fa_n} designs, {fa_share} are not actively protected at the snapshot (). | viz/thesis_q1.py:numbers() |
| `fo_else` | 42 % (was 69 %) | results B (Entry by region) | At the other offices it is {fo_else}, over {fo_n_else} designs. | viz/thesis_q1.py:numbers() |
| `fo_n_else` | 261 | results B (Entry by region) | At the other offices it is {fo_else}, over {fo_n_else} designs. | viz/thesis_q1.py:numbers() |
| `fo_n_us` | 364 (was 209) | results B (Entry by region) | At the US office the share is {fo_us}, over {fo_n_us} designs. | viz/thesis_q1.py:numbers() |
| `fo_p` | < 0.001 | results B (Entry by region) | The two differ with p {fo_p}. | viz/thesis_q1.py:numbers() |
| `fo_us` | 23 % (was 31 %) | results B (Entry by region) | At the US office the share is {fo_us}, over {fo_n_us} designs. | viz/thesis_q1.py:numbers() |
| `gr_fam_all` | 3.00 | appendix q1_growth_rates_table | Against all patenting they grow {gr_fam_all} times as fast, and the unique aircraft double every {dbl_ac} years. | viz/thesis_q1.py:numbers() |
| `gr_fam_b64` | 1.32 | results A (Growth of the field) | Counted in families, eVTOL grows {gr_fam_b64} times as fast as aeronautics ({gr_fam_b64_ci}). | viz/thesis_q1.py:numbers() |
| `gr_fam_b64_19` | 1.26 | results A (Growth of the field) | The lead rests partly on the latest years, and with the fit ended at 2019 the ratio falls to {gr_fam_b64_19}. | viz/thesis_q1.py:numbers() |
| `gr_fam_b64_19_ci` | 1.07 to 1.41 | results A (Growth of the field) | Its interval, {gr_fam_b64_19_ci}, still leaves eVTOL the faster series. | viz/thesis_q1.py:numbers() |
| `gr_fam_b64_ci` | 1.20 to 1.46 | results A (Growth of the field) | Counted in families, eVTOL grows {gr_fam_b64} times as fast as aeronautics ({gr_fam_b64_ci}). | viz/thesis_q1.py:numbers() |
| `na_2021` | 32 | results B (Entry by region) | North America's count falls from {na_2021} to {na_2023} aircraft over the same two years. | viz/thesis_q1.py:numbers() |
| `na_2023` | 10 | results B (Entry by region) | North America's count falls from {na_2021} to {na_2023} aircraft over the same two years. | viz/thesis_q1.py:numbers() |
| `na_share_2021` | 44 % | results B (Entry by region) | Its share falls from {na_share_2021} to {na_share_2023} over those two years (). | viz/thesis_q1.py:numbers() |
| `na_share_2023` | 22 % | results B (Entry by region) | Its share falls from {na_share_2021} to {na_share_2023} over those two years (). | viz/thesis_q1.py:numbers() |
| `na_share_2023_corr` | 22 % | results B (Entry by region) | Corrected for lag, the share of 2023 stays at {na_share_2023_corr}. | viz/thesis_q1.py:numbers() |
| `turn_ac_hi` | 2020 | results A (Growth of the field) | The resamples place that year anywhere from {turn_ac_lo} to {turn_ac_hi}. | viz/thesis_q1.py:numbers() |
| `turn_ac_lo` | 2010 | results A (Growth of the field) | The resamples place that year anywhere from {turn_ac_lo} to {turn_ac_hi}. | viz/thesis_q1.py:numbers() |
| `turn_ac_year` | 2017 | results A (Growth of the field) | The unique aircraft turn in {turn_ac_year}. | viz/thesis_q1.py:numbers() |
| `turn_pat_boot` | 90 % | results A (Growth of the field) | Filing takes off in {turn_pat_year}, the year chosen by {turn_pat_boot} of the resampled fits (). | viz/thesis_q1.py:numbers() |
| `turn_pat_year` | 2016 | results A (Growth of the field) | Filing takes off in {turn_pat_year}, the year chosen by {turn_pat_boot} of the resampled fits (). | viz/thesis_q1.py:numbers() |
| `vis_2023_hi` | 92 % | results B (Entry by region) | The snapshot already sees {vis_2023_lo} to {vis_2023_hi} of every region's aircraft of that year. | viz/thesis_q1.py:numbers() |
| `vis_2023_lo` | 87 % | results B (Entry by region) | The snapshot already sees {vis_2023_lo} to {vis_2023_hi} of every region's aircraft of that year. | viz/thesis_q1.py:numbers() |

### Q4 representativeness and the market clock

| key | value now | where used | sentence | source |
|---|---|---|---|---|
| `ari_n` | 152 (was 147) | answer | The aircraft public sources cover, the {trl_n} that got built and the {ari_n} of the index firms, are company-backed and carry more propulsor units, s… | viz/thesis_q4.py:numbers() |
| `closest_p` | 0.208 | results B (Is the mix representative) | Only the directory pages linked to a patent of this dataset match the dataset's mix (p {closest_p}, ). | viz/thesis_q4.py:numbers() |
| `eis_lead` | 7 | results B (Is the mix representative) | The lead is a median of {ff_lead} years, and planned entry into service sits a median of {eis_lead} years after the first patent. | viz/thesis_q4.py:numbers() |
| `fari_class_p` | 0.047 | results B (Is the mix representative) | By architecture group the flown designs give p {flown_class_p}, the flown index-firm designs p {fari_class_p}. | viz/thesis_q4.py:numbers() |
| `fari_differs` | 5 | results B (Is the mix representative) | The {fari_n} designs of the index firms that have flown differ on {fari_differs} of the six (). | viz/thesis_q4.py:numbers() |
| `fari_n` | 42 | results B (Is the mix representative) | The {fari_n} designs of the index firms that have flown differ on {fari_differs} of the six (). | viz/thesis_q4.py:numbers() |
| `ff_before` | 9 (was 8) | results B (Is the mix representative) | {ff_before} of the {ff_flown} firms with a first flight on record filed their first patent in this corpus before flying. | viz/thesis_q4.py:numbers() |
| `ff_flown` | 12 (was 11) | results B (Is the mix representative) | {ff_before} of the {ff_flown} firms with a first flight on record filed their first patent in this corpus before flying. | viz/thesis_q4.py:numbers() |
| `ff_lead` | 3 (was 4) | results B (Is the mix representative) | The lead is a median of {ff_lead} years, and planned entry into service sits a median of {eis_lead} years after the first patent. | viz/thesis_q4.py:numbers() |
| `flown_class_p` | 0.17 | results B (Is the mix representative) | By architecture group the flown designs give p {flown_class_p}, the flown index-firm designs p {fari_class_p}. | viz/thesis_q4.py:numbers() |
| `flown_differs` | 3 | results B (Is the mix representative) | They differ from the rest on {flown_differs} of the six attributes (). | viz/thesis_q4.py:numbers() |
| `flown_n` | 68 | results B (Is the mix representative) | Of the {unique} designs, {flown_n} have flown. | viz/thesis_q4.py:numbers() |
| `lc_dir_first` | 9 % (was 13 %) | results B (Is the mix representative) | In the directory it goes from {lc_dir_first} to {lc_dir_last}. | viz/thesis_q4.py:numbers() |
| `lc_dir_last` | 20 % | results B (Is the mix representative) | In the directory it goes from {lc_dir_first} to {lc_dir_last}. | viz/thesis_q4.py:numbers() |
| `lc_ds_first` | 27 % | results B (Is the mix representative) | Lift + Cruise rises in both, from {lc_ds_first} to {lc_ds_last} of the dataset's aircraft. | viz/thesis_q4.py:numbers() |
| `lc_ds_last` | 33 % | results B (Is the mix representative) | Lift + Cruise rises in both, from {lc_ds_first} to {lc_ds_last} of the dataset's aircraft. | viz/thesis_q4.py:numbers() |
| `mix_p` | < 0.001 | appendix q4_dataset_vs_directory_classes | All years together the two mixes differ (chi-square p {mix_p}), and Wingless carries the gap with an adjusted residual of {resid_low}. | viz/thesis_q4.py:numbers() |
| `nc_gen` | 530 | appendix q4_name_coverage | {nc_named} aircraft carry a real product name and {nc_gen} a generated identifier; none of the generated ones could be matched to a public aircraft. | viz/thesis_q4.py:numbers() |
| `nc_named` | 97 | results A (Is the coding right) | Only a named aircraft can be checked at all, {nc_named} of {unique}, so these shares speak for the company-backed part of the dataset. | viz/thesis_q4.py:numbers() |
| `pw_ci` | 0.83–0.94 | results A (Is the coding right) | That share, {pw_share}, has an interval of {pw_ci}. | viz/thesis_q4.py:numbers() |
| `pw_img_pub` | 87 | results A (Is the coding right) | The drawing label gives the built aircraft's architecture class for {pw_img_pub} of the {pw_n} matched aircraft (). | viz/thesis_q4.py:numbers() |
| `pw_img_txt` | 93 | results A (Is the coding right) | The patent text agrees with the public aircraft on {pw_txt_pub} of them, and the drawing agrees with the text on {pw_img_txt}. | viz/thesis_q4.py:numbers() |
| `pw_n` | 97 | results A (Is the coding right) | The drawing label gives the built aircraft's architecture class for {pw_img_pub} of the {pw_n} matched aircraft (). | viz/thesis_q4.py:numbers() |
| `pw_share` | 90 % | results A (Is the coding right) | That share, {pw_share}, has an interval of {pw_ci}. | viz/thesis_q4.py:numbers() |
| `pw_txt_pub` | 89 | results A (Is the coding right) | The patent text agrees with the public aircraft on {pw_txt_pub} of them, and the drawing agrees with the text on {pw_img_txt}. | viz/thesis_q4.py:numbers() |
| `resid_low` | −10.8 | results B (Is the mix representative) | All years together Wingless carries the gap between the two mixes (adjusted residual {resid_low}, ). | viz/thesis_q4.py:numbers() |
| `trl_n` | 68 (was 63) | answer | The aircraft public sources cover, the {trl_n} that got built and the {ari_n} of the index firms, are company-backed and carry more propulsor units, s… | viz/thesis_q4.py:numbers() |
| `trl_share` | 11 % (was 10 %) | appendix q4_trl_by_class | Only {trl_share} of the aircraft, {trl_n}, got past the paper stage of NASA TRL, and they come from the classes patented most, Lift + Cruise and Tilt … | viz/thesis_q4.py:numbers() |
| `unique` | 627 | results A (Is the coding right) | Only a named aircraft can be checked at all, {nc_named} of {unique}, so these shares speak for the company-backed part of the dataset. | viz/thesis_q4.py:numbers() |
| `wm_domain` | 30 % | results B (Is the mix representative) | Restricting the directory to electric crewed pages leaves Wingless at {wm_domain}, so the domain gate does not explain the gap. | viz/thesis_q4.py:numbers() |

### Q5 funding and investment

| key | value now | where used | sentence | source |
|---|---|---|---|---|
| `air_level_year` | 2018 | answer | Sector investment multiplied only in {fund_peak_period}, after filings had held their level since {air_level_year}. | viz/thesis_q5.py:numbers() |
| `ari_timeline_n` | 14 (was 13) | results A (Timing) | Of the {ari_timeline_n} index firms that file here, {ff_record_n} have a first flight on record up to the release year. | viz/thesis_q5.py:numbers() |
| `best_air` | 8 | results B (Funding vs filing and output) | {best_firm}, the best funded, holds {best_air} aircraft. | viz/thesis_q5.py:numbers() |
| `best_firm` | Joby Aviation | results B (Funding vs filing and output) | {best_firm}, the best funded, holds {best_air} aircraft. | viz/thesis_q5.py:numbers() |
| `eis_lead` | 7 | results A (Timing) | Planned entry into service sits a median of {eis_lead} years after the first patent on the {eis_n} firms that state one, firm by firm in . | viz/thesis_q5.py:numbers() |
| `eis_n` | 10 (was 9) | results A (Timing) | Planned entry into service sits a median of {eis_lead} years after the first patent on the {eis_n} firms that state one, firm by firm in . | viz/thesis_q5.py:numbers() |
| `ext_fund_1020` | 4.5 | results C (Concentration of funding) | Disclosed eVTOL investment totalled about US$ {ext_fund_1020} billion over the whole decade to {ext_fund_1020_end} (Vertical Flight Society), after th… | viz/thesis_q5.py:numbers() |
| `ext_fund_1020_end` | 2020 | results C (Concentration of funding) | Disclosed eVTOL investment totalled about US$ {ext_fund_1020} billion over the whole decade to {ext_fund_1020_end} (Vertical Flight Society), after th… | viz/thesis_q5.py:numbers() |
| `ext_fund_2021` | 6.8 | results C (Concentration of funding) | The year {fund_peak_period} alone then brought about {ext_fund_2021} billion (McKinsey), so the sector's money came later than its patents. | viz/thesis_q5.py:numbers() |
| `ff_before_n` | 9 (was 8) | results A (Timing) | Of those, {ff_before_n} filed their first patent in this corpus before flying, a median of {ff_lead} years earlier. | viz/thesis_q5.py:numbers() |
| `ff_lead` | 3 (was 4) | results A (Timing) | Of those, {ff_before_n} filed their first patent in this corpus before flying, a median of {ff_lead} years earlier. | viz/thesis_q5.py:numbers() |
| `ff_record_n` | 12 (was 11) | results A (Timing) | Of the {ari_timeline_n} index firms that file here, {ff_record_n} have a first flight on record up to the release year. | viz/thesis_q5.py:numbers() |
| `ff_visible` | 0 (was 1) | results A (Timing) | Once that lag is paid, about {ff_visible} year of the median lead is left. | viz/thesis_q5.py:numbers() |
| `fund_peak_period` | 2021 | results C (Concentration of funding) | The year {fund_peak_period} alone then brought about {ext_fund_2021} billion (McKinsey), so the sector's money came later than its patents. | viz/thesis_q5.py:numbers() |
| `lag_p90` | 3 | results A (Timing) | The lead a reader of published patents can use is shorter, because a patent is published up to {lag_p90} years after its priority date and a priority … | viz/thesis_q5.py:numbers() |
| `p_air` | 0.08 (was 0.11) | results B (Funding vs filing and output) | sets the disclosed funding of the firms with an amount against their unique aircraft in the corpus, ρ {rho_air} with p {p_air}, no relation detected. | viz/thesis_q5.py:numbers() |
| `p_fp` | 0.13 (was 0.031) | results B (Funding vs filing and output) | Money does go with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}, and the best-funded firm filed first. | viz/thesis_q5.py:numbers() |
| `p_lead` | 0.29 (was 0.23) | results B (Funding vs filing and output) | The lead from first patent to first flight does not shorten with money either, ρ {rho_lead} with p {p_lead} on the firms whose first flight has happen… | viz/thesis_q5.py:numbers() |
| `rho_air` | +0.58 (was +0.56) | results B (Funding vs filing and output) | sets the disclosed funding of the firms with an amount against their unique aircraft in the corpus, ρ {rho_air} with p {p_air}, no relation detected. | viz/thesis_q5.py:numbers() |
| `rho_fp` | −0.51 (was −0.71) | results B (Funding vs filing and output) | Money does go with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}, and the best-funded firm filed first. | viz/thesis_q5.py:numbers() |
| `rho_lead` | +0.40 (was +0.48) | results B (Funding vs filing and output) | The lead from first patent to first flight does not shorten with money either, ρ {rho_lead} with p {p_lead} on the firms whose first flight has happen… | viz/thesis_q5.py:numbers() |
| `top1` | Joby Aviation | results C (Concentration of funding) | The money is concentrated in {top1} and {top2}, where the patents are not. | viz/thesis_q5.py:numbers() |
| `top2` | Beta Technologies | results C (Concentration of funding) | The money is concentrated in {top1} and {top2}, where the patents are not. | viz/thesis_q5.py:numbers() |
| `top2_airshare` | 1.4 % | results C (Concentration of funding) | These two firms hold {top2_fundshare} of the funding the index firms disclose and {top2_airshare} of the aircraft of this labelled dataset. | viz/thesis_q5.py:numbers() |
| `top2_fundshare` | 56 % (was 57 %) | results C (Concentration of funding) | These two firms hold {top2_fundshare} of the funding the index firms disclose and {top2_airshare} of the aircraft of this labelled dataset. | viz/thesis_q5.py:numbers() |

`thesis_figures/Q1_growth/numbers.json`, `Q4_representativeness/numbers.json` and `Q5_money/numbers.json` were rewritten on 2026-10-13 from the current inputs (the corrected company map with EHang, the script TRL, the script years); the previous Q4 and Q5 files are kept beside them as `numbers.PRE_20261013.json`, and the values of the old Results text are in `review/numbers_old/`.

## 7. What changed since the old Results text (old -> new)

Old = the values the old Results text printed (the `numbers.json` files before the changes of 2026-10-12: the all-years protection method, the flown definition, the script inputs and the corrected company map with EHang). New = the values now. A key that the new text no longer quotes reads "(no longer quoted)".

### The statistics you listed, one line each

- **Index firms that file here** (rows of the clock figure, the firms of the current index release with a first patent in the dataset): 13 -> 14 (Q5 `ari_timeline_n`)
- **Index companies that file in the dataset** (whole company map): 18 -> 22 (Q4 `ari_firms_n`); their designs 147 -> 152 (Q4 `ari_n`)
- **Firms with a first flight on record** (year 2026 or before): 11 -> 12 (Q5 `ff_record_n`; Q4 `ff_flown` 11 -> 12)
- **Firms that filed their first patent before flying**: 8 -> 9 (Q5 `ff_before_n`; Q4 `ff_before` 8 -> 9); firms with a first flight at or before the first patent: 3 -> 3 (`ff_after_n`)
- **Median lead from the first patent to the first flight**, years: 4 -> 3 (Q5 `ff_lead`; Q4 4 -> 3), on the 9 firms with the patent before the flight (was 8); range 1 to 7 -> 1 to 7
- **The lead left after the 90th-percentile publication lag** (3 years, unchanged): 1 -> 0 years (Q5 `ff_visible`)
- **Median years from the first patent to the planned entry into service**: 7 -> 7 (Q5 `eis_lead`), on 9 -> 10 firms that state one (`eis_n`)
- **Firms behind each statistic (now)**: first flights 12; the lead median 9; planned entry into service 10; clock rows 14; funding tests 10 firms with a disclosed amount, 10 for the first-patent year, 9 for the lead (before 9, 9, 8)
- **Size of the flown group**: 63 (designs above TRL 2, earlier inputs) -> 68 (designs at TRL 5 or more, script inputs); the rest 564 -> 559 (Q4 `trl_n` -> `flown_n`); 10 designs entered and 5 left (section 4)
- **Turning point, patent families**: 2016 -> 2016 (unchanged), chosen by 90 % -> 90 % of the resampled fits, 95 % range of the resampled year 2015 to 2018 (not quoted before)
- **Turning point, designs**: 2017 -> 2017 (unchanged), chosen by 23 % of the resampled fits (not quoted before), 95 % range 2010 to 2020 -> 2010 to 2020 (unchanged)

None of the turning-point numbers depends on the company map, the TRL or the years of the directory: they come from the patent counts per priority year.

### Every number the old Results text quoted that changed

- Q1 `fa_cvt`: 53 % -> 29 %   (The classes appear to differ, CVT and Lift + Cruise at {fa_cvt} against Multirotor at {fa_mr}, but the differe…)
- Q1 `fa_mr`: 31 % -> 33 %   (The classes appear to differ, CVT and Lift + Cruise at {fa_cvt} against Multirotor at {fa_mr}, but the differe…)
- Q1 `fa_mr_first`: 41 % -> (no longer quoted)   (Counting a patent that names several aircraft for its first aircraft only, Multirotor rises to {fa_mr_first} a…)
- Q1 `fa_p`: 0.043 -> 0.105   (The class difference (p {fa_p}) does not survive the filing office.)
- Q1 `fa_p_first`: 0.079 -> (no longer quoted)   (Counting a patent that names several aircraft for its first aircraft only, Multirotor rises to {fa_mr_first} a…)
- Q1 `fa_share`: 43 % -> 31 %   (Of the aircraft with a priority year of 2019 or earlier, {fa_share} have no patent left in force ().)
- Q1 `fo_else`: 69 % -> 42 %   (Aircraft filed at the US office are out of force {fo_us} of the time, against {fo_else} elsewhere.)
- Q1 `fo_n_us`: 209 -> 364   (Within the US office no class difference is detected (p {fo_p_us}, {fo_n_us} aircraft).)
- Q1 `fo_p_us`: 0.43 -> (no longer quoted)   (Within the US office no class difference is detected (p {fo_p_us}, {fo_n_us} aircraft).)
- Q1 `fo_us`: 31 % -> 23 %   (Aircraft filed at the US office are out of force {fo_us} of the time, against {fo_else} elsewhere.)
- Q4 `ari_class_p`: 0.15 -> (no longer quoted)   (Neither group differs detectably in architecture class (p {trl_class_p} and {ari_class_p}).)
- Q4 `ari_n`: 147 -> 152   (The {ari_n} aircraft of the index firms differ on four of the six attributes (): region, priority window, file…)
- Q4 `ff_before`: 8 -> 9   ({ff_before} of the {ff_flown} firms with a first flight on record filed their first patent in this corpus befo…)
- Q4 `ff_flown`: 11 -> 12   ({ff_before} of the {ff_flown} firms with a first flight on record filed their first patent in this corpus befo…)
- Q4 `ff_lead`: 4 -> 3   (The lead is a median of {ff_lead} years, and planned entry into service sits a median of {eis_lead} years afte…)
- Q4 `lc_dir_first`: 13 % -> 9 %   (In the directory it goes from {lc_dir_first} to {lc_dir_last}.)
- Q4 `trl_class_p`: 0.11 -> (no longer quoted)   (Neither group differs detectably in architecture class (p {trl_class_p} and {ari_class_p}).)
- Q4 `trl_n`: 63 -> 68   (The aircraft that got built, {trl_n} of {unique}, differ from the rest on filer type and propulsor units and o…)
- Q4 `trl_share`: 10 % -> 11 %   (Only {trl_share} of the aircraft, {trl_n}, got past the paper stage of NASA TRL, and they come from the classe…)
- Q5 `ari_timeline_n`: 13 -> 14   (Of the {ari_timeline_n} index firms that file here, {ff_record_n} have a first flight on record up to the rele…)
- Q5 `eis_n`: 9 -> 10   (Planned entry into service sits a median of {eis_lead} years after the first patent on the {eis_n} firms that …)
- Q5 `ff_before_n`: 8 -> 9   (Of those, {ff_before_n} filed their first patent in this corpus before flying, a median of {ff_lead} years ear…)
- Q5 `ff_lead`: 4 -> 3   (Of those, {ff_before_n} filed their first patent in this corpus before flying, a median of {ff_lead} years ear…)
- Q5 `ff_record_n`: 11 -> 12   (Of the {ari_timeline_n} index firms that file here, {ff_record_n} have a first flight on record up to the rele…)
- Q5 `ff_visible`: 1 -> 0   (Once that lag is paid, about {ff_visible} year of the median lead is left.)
- Q5 `p_air`: 0.11 -> 0.08   (sets the disclosed funding of the firms with an amount against their unique aircraft in the corpus, ρ {rho_air…)
- Q5 `p_fp`: 0.031 -> 0.13   (Money does go with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}, and t…)
- Q5 `p_lead`: 0.23 -> 0.29   (The lead from first patent to first flight does not shorten with money either, ρ {rho_lead} with p {p_lead} on…)
- Q5 `rho_air`: +0.56 -> +0.58   (sets the disclosed funding of the firms with an amount against their unique aircraft in the corpus, ρ {rho_air…)
- Q5 `rho_fp`: −0.71 -> −0.51   (Money does go with filing early, ρ {rho_fp} against the priority year of the first patent with p {p_fp}, and t…)
- Q5 `rho_lead`: +0.48 -> +0.40   (The lead from first patent to first flight does not shorten with money either, ρ {rho_lead} with p {p_lead} on…)
- Q5 `top2_fundshare`: 57 % -> 56 %   (These two firms hold {top2_fundshare} of the funding the index firms disclose and {top2_airshare} of the aircr…)

### Numbers that did NOT change (57)

| question | key | value (old = new) | used in the sentence |
|---|---|---|---|
| Q1 | `ac_2015` | 21 | In 2015 the dataset gains {ac_2015} unique aircraft. |
| Q1 | `ac_2018` | 68 | In 2018 it gains {ac_2018}, and the count holds near that level to the last complete year. |
| Q1 | `ap_2526` | 18 | Lag explains only the two latest years, whose {ap_2526} aircraft are all Asia-Pacific's. |
| Q1 | `ap_delay_cvt` | −1 | On Combined Vectored Thrust (CVT) no delay is detected, {ap_delay_cvt} years with an interval of {ap_delay_cvt… |
| Q1 | `ap_delay_cvt_ci` | −3 to +1 | On Combined Vectored Thrust (CVT) no delay is detected, {ap_delay_cvt} years with an interval of {ap_delay_cvt… |
| Q1 | `ap_delay_range` | 2 to 4 | Asia-Pacific files Lift + Cruise, Tilt Propulsor and Tilt Wing {ap_delay_range} years after North America. |
| Q1 | `dbl_ac` | 3.7 | Against all patenting they grow {gr_fam_all} times as fast, and the unique aircraft double every {dbl_ac} year… |
| Q1 | `dbl_all` | 10.7 | Transport doubles every {dbl_secb} years and all patenting every {dbl_all} (). |
| Q1 | `dbl_b64` | 4.7 | eVTOL is the fastest-growing series (), its architecture patents doubling every {dbl_fam} years against {dbl_b… |
| Q1 | `dbl_fam` | 3.6 | eVTOL is the fastest-growing series (), its architecture patents doubling every {dbl_fam} years against {dbl_b… |
| Q1 | `dbl_secb` | 6.4 | Transport doubles every {dbl_secb} years and all patenting every {dbl_all} (). |
| Q1 | `gr_fam_all` | 3.00 | Against all patenting they grow {gr_fam_all} times as fast, and the unique aircraft double every {dbl_ac} year… |
| Q1 | `gr_fam_b64` | 1.32 | Counted in families, eVTOL grows {gr_fam_b64} times as fast as aeronautics ({gr_fam_b64_ci}). |
| Q1 | `gr_fam_b64_19` | 1.26 | The lead rests partly on the latest years, and with the fit ended at 2019 the ratio falls to {gr_fam_b64_19}. |
| Q1 | `gr_fam_b64_19_ci` | 1.07 to 1.41 | Its interval, {gr_fam_b64_19_ci}, still leaves eVTOL the faster series. |
| Q1 | `gr_fam_b64_ci` | 1.20 to 1.46 | Counted in families, eVTOL grows {gr_fam_b64} times as fast as aeronautics ({gr_fam_b64_ci}). |
| Q1 | `na_2021` | 32 | North America's count falls from {na_2021} to {na_2023} aircraft over the same two years. |
| Q1 | `na_2023` | 10 | North America's count falls from {na_2021} to {na_2023} aircraft over the same two years. |
| Q1 | `na_share_2021` | 44 % | Its share falls from {na_share_2021} to {na_share_2023} over those two years (). |
| Q1 | `na_share_2023` | 22 % | Its share falls from {na_share_2021} to {na_share_2023} over those two years (). |
| Q1 | `na_share_2023_corr` | 22 % | Corrected for lag, the share of 2023 stays at {na_share_2023_corr}. |
| Q1 | `turn_ac_hi` | 2020 | The resamples place that year anywhere from {turn_ac_lo} to {turn_ac_hi}. |
| Q1 | `turn_ac_lo` | 2010 | The resamples place that year anywhere from {turn_ac_lo} to {turn_ac_hi}. |
| Q1 | `turn_ac_year` | 2017 | The unique aircraft turn in {turn_ac_year}. |
| Q1 | `turn_pat_boot` | 90 % | Filing takes off in {turn_pat_year}, the year chosen by {turn_pat_boot} of the resampled fits (). |
| Q1 | `turn_pat_year` | 2016 | Filing takes off in {turn_pat_year}, the year chosen by {turn_pat_boot} of the resampled fits (). |
| Q1 | `vis_2023_hi` | 92 % | The snapshot already sees {vis_2023_lo} to {vis_2023_hi} of every region's aircraft of that year. |
| Q1 | `vis_2023_lo` | 87 % | The snapshot already sees {vis_2023_lo} to {vis_2023_hi} of every region's aircraft of that year. |
| Q4 | `closest_p` | 0.208 | Only the directory pages linked to a patent of this dataset match the dataset's mix (p {closest_p}, ). |
| Q4 | `eis_lead` | 7 | The lead is a median of {ff_lead} years, and planned entry into service sits a median of {eis_lead} years afte… |
| Q4 | `lc_dir_last` | 20 % | In the directory it goes from {lc_dir_first} to {lc_dir_last}. |
| Q4 | `lc_ds_first` | 27 % | Lift + Cruise rises in both, from {lc_ds_first} to {lc_ds_last} of the dataset's aircraft. |
| Q4 | `lc_ds_last` | 33 % | Lift + Cruise rises in both, from {lc_ds_first} to {lc_ds_last} of the dataset's aircraft. |
| Q4 | `mix_p` | < 0.001 | All years together the two mixes differ (chi-square p {mix_p}), and Wingless carries the gap with an adjusted … |
| Q4 | `nc_gen` | 530 | {nc_named} aircraft carry a real product name and {nc_gen} a generated identifier; none of the generated ones … |
| Q4 | `nc_named` | 97 | Only a named aircraft can be checked at all, {nc_named} of {unique}, so these shares speak for the company-bac… |
| Q4 | `pw_ci` | 0.83–0.94 | That share, {pw_share}, has an interval of {pw_ci}. |
| Q4 | `pw_img_pub` | 87 | The drawing label gives the built aircraft's architecture class for {pw_img_pub} of the {pw_n} matched aircraf… |
| Q4 | `pw_img_txt` | 93 | The patent text agrees with the public aircraft on {pw_txt_pub} of them, and the drawing agrees with the text … |
| Q4 | `pw_n` | 97 | The drawing label gives the built aircraft's architecture class for {pw_img_pub} of the {pw_n} matched aircraf… |
| Q4 | `pw_share` | 90 % | That share, {pw_share}, has an interval of {pw_ci}. |
| Q4 | `pw_txt_pub` | 89 | The patent text agrees with the public aircraft on {pw_txt_pub} of them, and the drawing agrees with the text … |
| Q4 | `resid_low` | −10.8 | All years together Wingless carries the gap between the two mixes (adjusted residual {resid_low}, ). |
| Q4 | `unique` | 627 | Only a named aircraft can be checked at all, {nc_named} of {unique}, so these shares speak for the company-bac… |
| Q4 | `wm_domain` | 30 % | Restricting the directory to electric crewed pages leaves Wingless at {wm_domain}, so the domain gate does not… |
| Q5 | `air_level_year` | 2018 | Sector investment multiplied only in {fund_peak_period}, after filings had held their level since {air_level_y… |
| Q5 | `best_air` | 8 | {best_firm}, the best funded, holds {best_air} aircraft. |
| Q5 | `best_firm` | Joby Aviation | {best_firm}, the best funded, holds {best_air} aircraft. |
| Q5 | `eis_lead` | 7 | Planned entry into service sits a median of {eis_lead} years after the first patent on the {eis_n} firms that … |
| Q5 | `ext_fund_1020` | 4.5 | Disclosed eVTOL investment totalled about US$ {ext_fund_1020} billion over the whole decade to {ext_fund_1020_… |
| Q5 | `ext_fund_1020_end` | 2020 | Disclosed eVTOL investment totalled about US$ {ext_fund_1020} billion over the whole decade to {ext_fund_1020_… |
| Q5 | `ext_fund_2021` | 6.8 | The year {fund_peak_period} alone then brought about {ext_fund_2021} billion (McKinsey), so the sector's money… |
| Q5 | `fund_peak_period` | 2021 | The year {fund_peak_period} alone then brought about {ext_fund_2021} billion (McKinsey), so the sector's money… |
| Q5 | `lag_p90` | 3 | The lead a reader of published patents can use is shorter, because a patent is published up to {lag_p90} years… |
| Q5 | `top1` | Joby Aviation | The money is concentrated in {top1} and {top2}, where the patents are not. |
| Q5 | `top2` | Beta Technologies | The money is concentrated in {top1} and {top2}, where the patents are not. |
| Q5 | `top2_airshare` | 1.4 % | These two firms hold {top2_fundshare} of the funding the index firms disclose and {top2_airshare} of the aircr… |

## 8. The funnel of section 4.1 in one table

| step | count |
|---|---|
| patent query hits (PatSeer, snapshot 2026-06-08) | 1 639 |
| T1: patents approved at labelling (patent triage) | 1 109 (879 after the domain gate) |
| T2: whole-aircraft figures approved (image triage), and the patents they sit on | 1 538 figures on 578 patents |
| designs characterised | 627 (on 543 primary patents) |
| directory pages (VFS eVTOL directory) | 1 229 |
| kept by the corrected domain rules | 871 |
| pages matched to a design (and the designs they give) | 97 pages, 99 designs |
| companies read in full (index company map) | 43 |
| companies where the script and the author agree (counting the companies both leave blank) | 35 of 43 |
| companies where the script returns a match | 18 |
| index companies that file in the dataset | 22 |

