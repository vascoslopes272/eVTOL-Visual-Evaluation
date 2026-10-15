# NUMBERS_III — Analysis III (dominant design)

Written by notebook 52 (`viz/thesis_latex_part3.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`.

## (a) III.1, cohort shares of Tilt Propulsor and Lift + Cruise

Source: `q6_architecture_shares_by_cohort.csv` (share of the cohort's designs).

| cohort   |   designs | Tilt Propulsor   | Lift + Cruise   |
|:---------|----------:|:-----------------|:----------------|
| <= 2011  |        63 | 31.7 %           | 27.0 %          |
| 2012-15  |        58 | 34.5 %           | 15.5 %          |
| 2016-19  |       213 | 23.5 %           | 22.5 %          |
| 2020-23  |       237 | 20.7 %           | 31.6 %          |
| 2024–26* |        56 | 21.4 %           | 28.6 %          |

## III.1, Spearman rho of share on priority year (2008–2023)

Source: `q6_share_trend_spearman.csv`.

| architecture code   | architecture             |   designs |   years |    rho |     p |   rho, years of 20+ designs |   p, years of 20+ designs |   years of 20+ designs |
|:--------------------|:-------------------------|----------:|--------:|-------:|------:|----------------------------:|--------------------------:|-----------------------:|
| SLC                 | Lift + Cruise            |       142 |      16 |  0.443 | 0.09  |                       0.142 |                      0.72 |                      9 |
| TP                  | Tilt Propulsor           |       132 |      16 | -0.675 | 0.004 |                      -0.367 |                      0.33 |                      9 |
| CVT                 | Combined Vectored Thrust |        93 |      16 |  0.255 | 0.34  |                       0.667 |                      0.05 |                      9 |
| TW                  | Tilt Wing                |        51 |      16 | -0.169 | 0.53  |                      -0.667 |                      0.05 |                      9 |
| MR                  | Multicopter              |        37 |      16 |  0.074 | 0.78  |                      -0.55  |                      0.12 |                      9 |
| PTC                 | Pitch-to-Cruise          |        22 |      16 |  0.472 | 0.07  |                       0.395 |                      0.29 |                      9 |
| TF                  | Tilt Frame               |        22 |      16 | -0.003 | 0.99  |                       0.059 |                      0.88 |                      9 |

## (b) III.4, VT on the five directory categories, actively protected designs

Source: `q7_iii4_directory_categories.csv` (balance), notebook 52 §III4. VT is the largest category in every year and cohort. Fold: `q7_iii4_directory_fold.csv`.

VT share per cohort:

| cohort   |   actively protected designs |   VT designs | VT share   |
|:---------|-----------------------------:|-------------:|:-----------|
| <= 2011  |                           18 |           10 | 55.6 %     |
| 2012-15  |                           33 |           24 | 72.7 %     |
| 2016-19  |                          138 |           83 | 60.1 %     |
| 2020-23  |                          192 |          114 | 59.4 %     |
| 2024–26* |                           52 |           30 | 57.7 %     |

VT share per priority year (read years, 20 designs or more, 2016–2023); condition 1 met in 2016, 2017, 2018, 2019, 2021, 2022, 2023 (all designs: 2016, 2017, 2021, 2022, 2023):

|   priority year |   aircraft |   its aircraft | share   | above 50 %   |
|----------------:|-----------:|---------------:|:--------|:-------------|
|            2016 |         24 |             13 | 54.2 %  | True         |
|            2017 |         33 |             24 | 72.7 %  | True         |
|            2018 |         37 |             20 | 54.0 %  | True         |
|            2019 |         44 |             26 | 59.1 %  | True         |
|            2020 |         54 |             25 | 46.3 %  | False        |
|            2021 |         59 |             40 | 67.8 %  | True         |
|            2022 |         35 |             23 | 65.7 %  | True         |
|            2023 |         44 |             26 | 59.1 %  | True         |

Balance (²D rarefied to 40, all designs, 200 permutations) with the band, per cohort; 2024–26* is incomplete and not read:

| cohort            |   aircraft |   D2 |   D2 permutation low |   D2 permutation high | below band   |
|:------------------|-----------:|-----:|---------------------:|----------------------:|:-------------|
| <= 2011           |         63 | 2.93 |                 1.87 |                  2.91 | False        |
| 2012-15           |         58 | 1.97 |                 1.85 |                  2.84 | False        |
| 2016-19           |        211 | 2.34 |                 2.06 |                  2.55 | False        |
| 2020-23           |        237 | 2.16 |                 2.09 |                  2.52 | False        |
| 2024-26 (partial) |         56 | 2.4  |                 1.77 |                  2.75 | False        |

## Verdict table

Source: `q7_verdict_table.csv`.

| condition                                                                              | A                                                                                 | A·W·T                                                                             | A·U                                                                               | F                                                                                                                                       |
|:---------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| 1, counts: one architecture above 50 % of the aircraft, two consecutive priority years | in force: ✗ not met, at most 39.0 % (2021); all: ✗ not met, at most 36.2 % (2020) | in force: ✗ not met, at most 27.1 % (2021); all: ✗ not met, at most 27.3 % (2018) | in force: ✗ not met, at most 23.7 % (2021); all: ✗ not met, at most 19.4 % (2021) | in force: ✓ met in 2020 and 2021 (51.8 %, 59.3 %); all: ✗ not met, above half only in 2021 (56.9 %), not 2020 (49.3 %) or 2022 (47.9 %) |
| 2, balance: ²D below the permutation band                                              | ✓ met in 2020-23                                                                  | ✗ not met                                                                         | ✓ met in <= 2011, 2012-15                                                         | ✓ met in 2020-23                                                                                                                        |
| 3, form: Q below the two earliest cohorts by more than the band                        | ✓ met in 2020-23                                                                  | ✗ not met                                                                         | ✓ met in 2020-23                                                                  | ✓ met in 2020-23                                                                                                                        |
| all three in the same period                                                           | ✗ not met                                                                         | ✗ not met                                                                         | ✗ not met                                                                         | ✓ met in 2020-23                                                                                                                        |

## Weights table (condition 3, the only weighting: the 34 dimensions of the codebook, each of the four systems weighing 1)

Source: `q7_condition3_weights.csv`; 34 dimensions, 625 designs (two designs have no architecture recorded). Per-wing dimensions read wing 1; per-boom dimensions boom group 1; propulsor dimensions the set with the most propulsors (first listed on a tie); a dimension that does not apply is blank and left out of the average.

| system          | dimensions                                                                                                                                                                                                                                                                                       |   count |   weight of each |   weight in all |
|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------:|-----------------:|----------------:|
| G1 architecture | Architecture                                                                                                                                                                                                                                                                                     |       1 |            1     |           1     |
| M1 structure    | Fuselage Shape; Fuselage Kinematics; Ground Contact Interface; Airframe Lateral Symmetry; Booms present; Boom count; Boom Attachment; Boom-Wing Panel Index; Boom Longitudinal Position; Boom Spanwise Position; Boom Orientation; Boom-Wing Relationship; Boom articulation; Booms retract/stow |      14 |            0.071 |           1     |
| M2 wings        | Wing Architecture; Wing count; Vertical Position; Longitudinal Position; Planform; Tip-joined; Tilt; Role                                                                                                                                                                                        |       8 |            0.083 |           0.667 |
| M2 empennage    | Empennage Type                                                                                                                                                                                                                                                                                   |       1 |            0.333 |           0.333 |
| M3 propulsion   | Propulsor count; Thrust Kinematics; Propulsor Articulation; Tractor/Pusher Arrangement; Propulsor Enclosure; Retraction Kinematics; Airframe Mounting Zone; Empennage Mounting Zone; Wing Chordwise Zone; Wing Spanwise Zone                                                                     |      10 |            0.1   |           1     |
| total           |                                                                                                                                                                                                                                                                                                  |      34 |          nan     |           4     |

## Condition 3 on F (same weights; Q on the designs of F's base, per cohort)

Source: `q7_condition3_family.csv`. Q uses no architecture, so F on all designs is the same set as A.

| base               | cohort            |   designs |      Q |   Q of the earliest cohorts |      ΔQ |   ΔQ permutation low |   ΔQ permutation high | below band   | partial   |
|:-------------------|:------------------|----------:|-------:|----------------------------:|--------:|---------------------:|----------------------:|:-------------|:----------|
| actively protected | <= 2011           |        18 | 0.4944 |                      0.5161 | -0.0216 |              -0.0449 |                0.0395 | False        | False     |
| actively protected | 2012-15           |        33 | 0.5377 |                      0.5161 |  0.0216 |              -0.0395 |                0.0449 | False        | False     |
| actively protected | 2016-19           |       138 | 0.5984 |                      0.5161 |  0.0824 |              -0.0277 |                0.0632 | False        | False     |
| actively protected | 2020-23           |       192 | 0.5528 |                      0.5161 |  0.0368 |              -0.0176 |                0.0697 | False        | False     |
| actively protected | 2024-26 (partial) |        52 | 0.5752 |                      0.5161 |  0.0591 |              -0.0414 |                0.069  | False        | True      |
| all designs        | <= 2011           |        63 | 0.5772 |                      0.5723 |  0.0049 |              -0.021  |                0.0209 | False        | False     |
| all designs        | 2012-15           |        58 | 0.5675 |                      0.5723 | -0.0049 |              -0.0209 |                0.021  | False        | False     |
| all designs        | 2016-19           |       211 | 0.596  |                      0.5723 |  0.0236 |              -0.0177 |                0.0435 | False        | False     |
| all designs        | 2020-23           |       237 | 0.5555 |                      0.5723 | -0.0168 |              -0.0151 |                0.0399 | True         | False     |
| all designs        | 2024-26 (partial) |        56 | 0.5844 |                      0.5723 |  0.0121 |              -0.0459 |                0.0434 | False        | True      |
| granted and live   | <= 2011           |        18 | 0.4944 |                      0.5174 | -0.023  |              -0.0457 |                0.0311 | False        | False     |
| granted and live   | 2012-15           |        32 | 0.5404 |                      0.5174 |  0.023  |              -0.0311 |                0.0457 | False        | False     |
| granted and live   | 2016-19           |       135 | 0.599  |                      0.5174 |  0.0816 |              -0.0247 |                0.0684 | False        | False     |
| granted and live   | 2020-23           |       148 | 0.5455 |                      0.5174 |  0.0281 |              -0.028  |                0.072  | False        | False     |
| granted and live   | 2024-26 (partial) |        10 | 0.5818 |                      0.5174 |  0.0644 |              -0.1171 |                0.06   | False        | True      |

## Three-year check (condition 1, three consecutive years, actively protected designs)

Source: `q7_three_year_check.csv`.

| level   | years above 50 % in three consecutive years, actively protected designs   |
|:--------|:--------------------------------------------------------------------------|
| A       | none                                                                      |
| A·W·T   | none                                                                      |
| A·U     | none                                                                      |
| F       | none                                                                      |

## F on granted and live patents alone

Source: `q7_granted_live_condition1.csv`, `q7_granted_live_condition2.csv`.

|   priority year |   designs |   F designs |   share of F | read (20 designs or more)   |
|----------------:|----------:|------------:|-------------:|:----------------------------|
|            2016 |        24 |           6 |       0.25   | True                        |
|            2017 |        32 |           5 |       0.1562 | True                        |
|            2018 |        35 |          11 |       0.3143 | True                        |
|            2019 |        44 |          16 |       0.3636 | True                        |
|            2020 |        51 |          27 |       0.5294 | True                        |
|            2021 |        54 |          32 |       0.5926 | True                        |
|            2022 |        28 |          11 |       0.3929 | True                        |
|            2023 |        15 |           9 |       0.6    | False                       |

| cohort            |   designs |   ²D |   band, lower edge |   band, upper edge | below band   |
|:------------------|----------:|-----:|-------------------:|-------------------:|:-------------|
| <= 2011           |        18 | 2.84 |               2.31 |               5.6  | False        |
| 2012-15           |        32 | 4.1  |               2.67 |               5.69 | False        |
| 2016-19           |       135 | 5.14 |               3.54 |               4.56 | False        |
| 2020-23           |       148 | 3.03 |               3.55 |               4.64 | True         |
| 2024-26 (partial) |        10 | 3.33 |               1.92 |               5.56 | False        |

## III.4, which VT share the figure draws

`q7_iii4_directory_categories` draws VT's share per priority YEAR (left panel, condition 1: two actively protected curves, ringed years above 50 %), and ²D per COHORT against its band (right panel, condition 2, all designs). The per-cohort VT share above is not drawn; it is listed here for the text. Per-year values: the table 'VT share per priority year' above, also written to `Data_for_writing/csv/q7_iii4_vt_share_per_year.csv`.

## Designs per cohort: III.1 against the form distance of condition 3

Source: `q6_architecture_shares_by_cohort.csv` (`designs`), `q7_condition3_cohesion.csv` (`aircraft`, subsystem weighting).

| cohort   |   designs in III.1 (denominator of the shares) |   designs in the form distance, A, A·U and F |   designs in the form distance, A·W·T |   difference to A |
|:---------|-----------------------------------------------:|---------------------------------------------:|--------------------------------------:|------------------:|
| <= 2011  |                                             63 |                                           63 |                                    63 |                 0 |
| 2012-15  |                                             58 |                                           58 |                                    58 |                 0 |
| 2016-19  |                                            213 |                                          211 |                                   211 |                 2 |
| 2020-23  |                                            237 |                                          237 |                                   236 |                 0 |
| 2024–26* |                                             56 |                                           56 |                                    55 |                 0 |

Why they differ: the shares of III.1 divide by every design of the cohort, including the designs with no architecture recorded (a bar segment 'no architecture recorded'), while the form distance needs an architecture to place a design in a level, so those designs are left out. The two designs without an architecture (`CN109263914A_ua1`, `CN109263949A_ua1`) have priority year 2018, so only 2016–19 differs (213 against 211). A·W·T drops further designs whose wings or tilt are not recorded.

## Numbers quoted by the Results text, III.1 (sub-question B)

Source: `viz/thesis_q6.py` numbers(ctx), notebook cell of the III1 group.

- `cvt_w4` = 22 %
- `lc_w1` = 27 %
- `lc_w4` = 32 %
- `three_w4` = 75 %
- `tp_w1` = 32 %
- `tp_w3` = 23 %
- `tp_w4` = 21 %
- `w1_n` = 63
- `w3` = 2016-19
- `w4_n` = 237

## Numbers quoted by the Results text, III.2 to III.4 (Q7, regions and external comparison left out)

Source: `viz/thesis_q7.py` numbers(ctx), notebook cells of the III2_III3 group.

- `w_last` = 2020-23
- `w_early` = 2012-15
- `w_mid` = 2016-19
- `w_first` = 2012
- `met_years` = 2020 and 2021
- `met_span` = 2020-21
- `met_first` = 2020
- `met_last` = 2021
- `t7_c_arch` = 12
- `t7_cwt_arch` = 39
- `t7_cu_arch` = 43
- `t7_f_arch` = 12
- `t7_c_d1` = 7.3
- `t7_cwt_d1` = 16.4
- `t7_cu_d1` = 29.4
- `t7_f_d1` = 6.2
- `t7_f_share` = 39 %
- `t7_slc_share` = 26 %
- `t7_cu_share` = 10 %
- `t7_cwt_share` = 17 %
- `t7_f_n` = 246
- `t7_cwt_largest` = Lift + Cruise · one wing · no tilting propulsor
- `t7_cu_largest` = Tilt Propulsor · 1-3 propulsor units
- `dd_year_min` = 20
- `dd_read_years` = eight
- `dd_first_read` = 2016
- `dd_first_read_all` = 2015
- `dd_last_year` = 2023
- `dd_first_year` = 2008
- `f_in_2020` = 51.8 %
- `f_in_2021` = 59.3 %
- `f_in_2022` = 42.9 %
- `f_in_2023` = 43.2 %
- `f_all_2020` = 49.3 %
- `f_all_2021` = 56.9 %
- `f_all_2022` = 47.9 %
- `f_in_2020_k` = 28 of 54
- `f_in_2021_k` = 35 of 59
- `f_all_2020_k` = 34 of 69
- `gl_2020` = 94 %
- `gl_2021` = 92 %
- `gl_2022` = 80 %
- `gl_2023` = 34 %
- `f_gl_2020` = 53 %
- `f_gl_2021` = 59 %
- `lapse_2022` = 23.8 %
- `lapse_2023` = 56.5 %
- `max_rest` = 39.0 %
- `max_c` = 39.0 %
- `max_cwt` = 27.1 %
- `max_cu` = 23.7 %
- `max_c_year` = 2021
- `max_c_arch` = Combined Vectored Thrust
- `f_d2_last` = 3.22
- `f_d2_edge` = 3.65
- `c_d2_last` = 4.53
- `c_d2_edge` = 4.74
- `cu_d2_w1` = 10.60
- `cu_d2_w1_edge` = 11.80
- `cu_d2_w2` = 10.10
- `cu_d2_w2_edge` = 11.22
- `dq_main` = −0.017
- `dq_main_edge` = −0.015
- `top3_cwt` = 47 %
- `top3_cu` = 26 %
- `rarefy_n` = 40
- `perms` = 200
- `seed` = 42
