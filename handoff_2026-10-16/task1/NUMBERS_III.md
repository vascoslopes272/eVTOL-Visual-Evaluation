# NUMBERS_III — Analysis III (dominant design)

Written by notebook 52 (`viz/thesis_latex_part3.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`.

## (a) III.1, cohort shares of Tilt Propulsor and Separate Lift + Cruise

Source: `q6_architecture_shares_by_cohort.csv` (share of the cohort's designs).

| cohort   |   designs | Tilt Propulsor   | Separate Lift + Cruise   |
|:---------|----------:|:-----------------|:----------------|
| <= 2011  |        63 | 31.7 %           | 27.0 %          |
| 2012-15  |        58 | 34.5 %           | 15.5 %          |
| 2016-19  |       213 | 23.5 %           | 22.5 %          |
| 2020-23  |       237 | 20.7 %           | 31.6 %          |
| 2024–26* |        56 | 21.4 %           | 28.6 %          |

## III.1, Spearman rho of share on priority year (2008–2023)

Source: `q6_share_trend_spearman.csv`.

| architecture code   | architecture             |   designs |   years |    rho |     p |   p (Holm) |   rho, 2016-23 |   p, 2016-23 |   p, 2016-23 (Holm) |
|:--------------------|:-------------------------|----------:|--------:|-------:|------:|-----------:|---------------:|-------------:|--------------------:|
| SLC                 | Separate Lift + Cruise            |       142 |      16 |  0.443 | 0.09  |      0.43  |          0.515 |         0.19 |                   1 |
| TP                  | Tilt Propulsor           |       132 |      16 | -0.675 | 0.004 |      0.029 |         -0.357 |         0.39 |                   1 |
| CVT                 | Combined Vectored Thrust |        93 |      16 |  0.255 | 0.34  |      1     |          0.548 |         0.16 |                   1 |
| TW                  | Tilt Wing                |        51 |      16 | -0.169 | 0.53  |      1     |         -0.548 |         0.16 |                   1 |
| MR                  | Multicopter              |        37 |      16 |  0.074 | 0.78  |      1     |         -0.476 |         0.23 |                   1 |
| PTC                 | Pitch-to-Cruise          |        22 |      16 |  0.472 | 0.07  |      0.39  |          0.204 |         0.63 |                   1 |
| TF                  | Tilt Frame               |        22 |      16 | -0.003 | 0.99  |      1     |         -0.286 |         0.49 |                   1 |

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

Balance (²D rarefied to 40, all designs, 1000 permutations) with the band, per cohort; 2024–26* is incomplete and not read:

| cohort            |   aircraft |   D2 |   D2 permutation low |   D2 permutation high | below band   |
|:------------------|-----------:|-----:|---------------------:|----------------------:|:-------------|
| <= 2011           |         63 | 2.91 |                 1.86 |                  2.83 | False        |
| 2012-15           |         58 | 1.97 |                 1.84 |                  2.82 | False        |
| 2016-19           |        211 | 2.34 |                 2.08 |                  2.56 | False        |
| 2020-23           |        237 | 2.18 |                 2.09 |                  2.53 | False        |
| 2024-26 (partial) |         56 | 2.4  |                 1.81 |                  2.83 | False        |

## Verdict table (each base read alone: all designs is the main reading, actively protected the sensitivity; condition 3 under the w15 weighting)

Source: `q7_verdict_table.csv`.

| base               | condition                                                                             | A                                | A·W·T                            | A·U                                | F                                       |
|:-------------------|:--------------------------------------------------------------------------------------|:---------------------------------|:---------------------------------|:-----------------------------------|:----------------------------------------|
| all designs        | 1, counts: one architecture above 50 % of the designs, two consecutive priority years | ✗ not met, at most 36.2 % (2020) | ✗ not met, at most 27.3 % (2018) | ✗ not met, at most 19.4 % (2021)   | ✗ not met, at most 56.9 % (2021)        |
| all designs        | 2, balance: ²D below the permutation band                                             | ✓ met in 2020-23                 | ✗ not met                        | ✓ met in <= 2011, 2012-15          | ✓ met in 2020-23                        |
| all designs        | 3, form: Q below the two earliest cohorts by more than the band                       | ✓ met in 2020-23                 | ✓ met in 2020-23                 | ✓ met in 2020-23                   | ✓ met in 2020-23                        |
| all designs        | all three in the same period                                                          | ✗ not met                        | ✗ not met                        | ✗ not met                          | ✗ not met                               |
| actively protected | 1, counts: one architecture above 50 % of the designs, two consecutive priority years | ✗ not met, at most 39.0 % (2021) | ✗ not met, at most 27.1 % (2021) | ✗ not met, at most 23.7 % (2021)   | ✓ met in 2020 and 2021 (51.8 %, 59.3 %) |
| actively protected | 2, balance: ²D below the permutation band                                             | ✓ met in <= 2011, 2020-23        | ✓ met in <= 2011, 2020-23        | ✓ met in <= 2011, 2012-15, 2020-23 | ✓ met in 2020-23                        |
| actively protected | 3, form: Q below the two earliest cohorts by more than the band                       | ✗ not met                        | ✗ not met                        | ✗ not met                          | ✗ not met                               |
| actively protected | all three in the same period                                                          | ✗ not met                        | ✗ not met                        | ✗ not met                          | ✗ not met                               |

## The numbers behind the verdict

Source: `q7_verdict_detail.csv`. Condition 1: the largest share of a read year (20 designs or more) and the years met; condition 2: ²D rarefied to 40 and the lower edge of its band; condition 3: ΔQ 2020-23 of the form distance under w15 (15 dimensions, each of the four systems weighing 1) and the lower edge of its band (1000 permutations, seed 42).

| base               | level   | condition 1: largest share   |   condition 1: its year | condition 1: years met   | condition 1: share 2020 (n of N)   | condition 1: share 2021 (n of N)   |   ²D <= 2011 |   ²D lower band edge <= 2011 |   ²D 2012-15 |   ²D lower band edge 2012-15 |   ²D 2016-19 |   ²D lower band edge 2016-19 |   ²D 2020-23 |   ²D lower band edge 2020-23 |   ΔQ 2020-23 |   ΔQ lower band edge 2020-23 |
|:-------------------|:--------|:-----------------------------|------------------------:|:-------------------------|:-----------------------------------|:-----------------------------------|-------------:|-----------------------------:|-------------:|-----------------------------:|-------------:|-----------------------------:|-------------:|-----------------------------:|-------------:|-----------------------------:|
| all designs        | A       | 36.2 %                       |                    2020 | none                     | 36.2 % (25 of 69)                  | 33.3 % (24 of 72)                  |         4.66 |                         4.18 |         5.01 |                         4.12 |         5.96 |                         4.68 |         4.55 |                         4.73 |      -0.0279 |                      -0.0196 |
| all designs        | A·W·T   | 27.3 %                       |                    2018 | none                     | 24.6 % (17 of 69)                  | 23.6 % (17 of 72)                  |         8.25 |                         7.03 |         8.12 |                         6.97 |        10.58 |                         8.25 |         8.36 |                         8.3  |      -0.0299 |                      -0.0206 |
| all designs        | A·U     | 19.4 %                       |                    2021 | none                     | 14.5 % (10 of 69)                  | 19.4 % (14 of 72)                  |        10.61 |                        12.15 |        10.12 |                        11.89 |        16.21 |                        13.86 |        14.49 |                        13.85 |      -0.0299 |                      -0.0234 |
| all designs        | F       | 56.9 %                       |                    2021 | none                     | 49.3 % (34 of 69)                  | 56.9 % (41 of 72)                  |         3.9  |                         3.11 |         4.84 |                         3.03 |         4.84 |                         3.58 |         3.25 |                         3.62 |      -0.0279 |                      -0.0196 |
| actively protected | A       | 39.0 %                       |                    2021 | none                     | 38.9 % (21 of 54)                  | 39.0 % (23 of 59)                  |         3    |                         3.06 |         4.02 |                         3.72 |         6.05 |                         4.48 |         4.4  |                         4.63 |       0.0091 |                      -0.0227 |
| actively protected | A·W·T   | 27.1 %                       |                    2021 | none                     | 24.1 % (13 of 54)                  | 27.1 % (16 of 59)                  |         4.15 |                         4.91 |         6.68 |                         6.29 |        11.35 |                         8.18 |         8.27 |                         8.5  |       0.0064 |                      -0.0223 |
| actively protected | A·U     | 23.7 %                       |                    2021 | none                     | 16.7 % (9 of 54)                   | 23.7 % (14 of 59)                  |         5.59 |                         7.04 |         7.72 |                         9.99 |        16.35 |                        13.52 |        13.84 |                        13.89 |       0.0064 |                      -0.0203 |
| actively protected | F       | 59.3 %                       |                    2021 | 2020, 2021               | 51.8 % (28 of 54)                  | 59.3 % (35 of 59)                  |         2.84 |                         2.28 |         3.93 |                         2.76 |         5.14 |                         3.38 |         3.14 |                         3.5  |       0.0091 |                      -0.0227 |

## Weights table (condition 3, the reported weighting w15: 15 dimensions of the codebook, each of the four systems weighing 1, 4 in all)

Source: `q7_condition3_weights.csv`; 15 dimensions, 625 designs (two designs have no architecture recorded). Eleven dimensions are compared as options (0 same, 1 different); three are ordered and compared by rank difference over a fixed range: boom count (0 when no boom, 1, 2, 3 to 4, 5 or more; / 4), wing count (0 when no wing, 1, 2, 3; / 3) and the band of propulsors (1 to 3, 4, 5 to 6, 7 to 8, 9 or more; / 4, the bands of A·U); the tilt share is the share 0 to 1 of the design's propulsors whose thrust turns between hover and cruise (a propulsor that pivots on its mount, sits on a tilting wing, a tilting empennage or a tilting boom, or a Tilt Body design, which turns whole), compared by absolute difference; the mount locations are the set of stations carrying propulsors among fuselage, wing, boom and empennage, compared by Jaccard distance (the share of the stations used by either design that only one of them uses). The three wing dimensions read wing 1 (the primary wing of codebook R5-03, which is wing 1 in every design: the author checked the 4 designs whose role reading pointed to wing 2 on 2026-10-16); enclosure and tractor/pusher arrangement read the set with the most propulsors (first listed on a tie); a dimension that does not apply or that an override hides is blank and left out of the pair's average, and the propulsion dimensions are blank for designs with no propulsor card (Hoverbike, Personal Flying Vehicle). The 34-dimension weighting of 2026-10-14 (w34) stays in the code for the record and is no longer reported.

| system          | dimension                  | codebook field                                                           | compared as                                                                                     |   weight |
|:----------------|:---------------------------|:-------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|---------:|
| G1 architecture | Architecture               | topType                                                                  | 0 same option, 1 different                                                                      |    1     |
| M1 structure    | Fuselage Shape             | fusShape                                                                 | 0 same option, 1 different                                                                      |    0.5   |
| M1 structure    | Boom count                 | boomsPresent, boom1..6_count                                             | ordered 0, 1, 2, 3 to 4, 5 or more; rank difference / 4                                         |    0.3   |
| M1 structure    | Fuselage Kinematics        | fusKin                                                                   | 0 same option, 1 different                                                                      |    0.2   |
| M2 aerodynamics | Wing count                 | wCount                                                                   | ordered 0, 1, 2, 3; difference / 3                                                              |    0.3   |
| M2 aerodynamics | Wing Architecture          | wingConf                                                                 | 0 same option, 1 different                                                                      |    0.3   |
| M2 aerodynamics | Vertical Position          | wing1_posV                                                               | 0 same option, 1 different                                                                      |    0.022 |
| M2 aerodynamics | Longitudinal Position      | wing1_posL                                                               | 0 same option, 1 different                                                                      |    0.022 |
| M2 aerodynamics | Planform                   | wing1_plan                                                               | 0 same option, 1 different                                                                      |    0.022 |
| M2 aerodynamics | Empennage Type             | empType                                                                  | 0 same option, 1 different                                                                      |    0.333 |
| M3 propulsion   | Propulsor band             | propulsor_units                                                          | ordered 1 to 3, 4, 5 to 6, 7 to 8, 9 or more; rank difference / 4                               |    0.35  |
| M3 propulsion   | Tilt share                 | <station>_count, propKin, wing tilt, empTilts, boom_thrust_state, fusKin | share 0 to 1 of the propulsors whose thrust turns between hover and cruise; absolute difference |    0.3   |
| M3 propulsion   | Propulsor Enclosure        | <set>_bmech                                                              | 0 same option, 1 different (the set with the most propulsors)                                   |    0.15  |
| M3 propulsion   | Tractor/Pusher Arrangement | <set>_chord                                                              | 0 same option, 1 different (the set with the most propulsors)                                   |    0.1   |
| M3 propulsion   | Mount locations            | <station>_count                                                          | stations carrying propulsors among fuselage, wing, boom, empennage; Jaccard distance            |    0.1   |
| total           | 15 dimensions              |                                                                          |                                                                                                 |    4     |

## Condition 3 on F (the same w15 weights; Q on the designs of F's base, per cohort)

Source: `q7_condition3_family.csv`. Q uses no architecture, so F on all designs is the same set as A.

| base               | cohort            |   designs |      Q |   Q of the earliest cohorts |      ΔQ |   ΔQ permutation low |   ΔQ permutation high | below band   | partial   |
|:-------------------|:------------------|----------:|-------:|----------------------------:|--------:|---------------------:|----------------------:|:-------------|:----------|
| actively protected | <= 2011           |        18 | 0.5107 |                      0.5064 |  0.0043 |              -0.0472 |                0.0345 | False        | False     |
| actively protected | 2012-15           |        33 | 0.5021 |                      0.5064 | -0.0043 |              -0.0345 |                0.0472 | False        | False     |
| actively protected | 2016-19           |       138 | 0.5727 |                      0.5064 |  0.0663 |              -0.0244 |                0.0692 | False        | False     |
| actively protected | 2020-23           |       192 | 0.5154 |                      0.5064 |  0.0091 |              -0.0227 |                0.0666 | False        | False     |
| actively protected | 2024-26 (partial) |        52 | 0.5413 |                      0.5064 |  0.0349 |              -0.0429 |                0.0712 | False        | True      |
| all designs        | <= 2011           |        63 | 0.5583 |                      0.5463 |  0.012  |              -0.0213 |                0.0213 | False        | False     |
| all designs        | 2012-15           |        58 | 0.5343 |                      0.5463 | -0.012  |              -0.0213 |                0.0213 | False        | False     |
| all designs        | 2016-19           |       211 | 0.5679 |                      0.5463 |  0.0215 |              -0.0205 |                0.0361 | False        | False     |
| all designs        | 2020-23           |       237 | 0.5185 |                      0.5463 | -0.0279 |              -0.0196 |                0.0351 | True         | False     |
| all designs        | 2024-26 (partial) |        56 | 0.549  |                      0.5463 |  0.0027 |              -0.0437 |                0.0401 | False        | True      |
| granted and live   | <= 2011           |        18 | 0.5107 |                      0.5071 |  0.0036 |              -0.0489 |                0.0335 | False        | False     |
| granted and live   | 2012-15           |        32 | 0.5034 |                      0.5071 | -0.0036 |              -0.0335 |                0.0489 | False        | False     |
| granted and live   | 2016-19           |       135 | 0.5748 |                      0.5071 |  0.0677 |              -0.0262 |                0.0656 | False        | False     |
| granted and live   | 2020-23           |       148 | 0.5046 |                      0.5071 | -0.0025 |              -0.0241 |                0.066  | False        | False     |
| granted and live   | 2024-26 (partial) |        10 | 0.5488 |                      0.5071 |  0.0418 |              -0.1301 |                0.0515 | False        | True      |

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
| <= 2011           |        18 | 2.84 |               2.31 |               5.79 | False        |
| 2012-15           |        32 | 4.1  |               2.69 |               5.69 | False        |
| 2016-19           |       135 | 5.14 |               3.51 |               4.7  | False        |
| 2020-23           |       148 | 2.98 |               3.53 |               4.65 | True         |
| 2024-26 (partial) |        10 | 3.33 |               1.92 |               5.56 | False        |

## III.4, which VT share the figure draws

`q7_iii4_directory_categories` draws VT's share per priority YEAR (left panel, condition 1: all designs solid, actively protected dashed, years under 20 designs hollow grey; the met years of each base as red bars), and ²D per COHORT against its band (right panel, condition 2, all designs). The per-cohort VT share above is not drawn; it is listed here for the text. Per-year values: the table 'VT share per priority year' above, also written to `Data_for_writing/csv/q7_iii4_vt_share_per_year.csv`.

## Designs per cohort: III.1 against the form distance of condition 3

Source: `q6_architecture_shares_by_cohort.csv` (`designs`), `q7_condition3_cohesion.csv` (`aircraft`, w15 weighting).

| cohort   |   designs in III.1 (denominator of the shares) |   designs in the form distance, A and F |   designs in the form distance, A·U |   designs in the form distance, A·W·T |   difference to A |
|:---------|-----------------------------------------------:|----------------------------------------:|------------------------------------:|--------------------------------------:|------------------:|
| <= 2011  |                                             63 |                                      63 |                                  63 |                                    63 |                 0 |
| 2012-15  |                                             58 |                                      58 |                                  58 |                                    58 |                 0 |
| 2016-19  |                                            213 |                                     211 |                                 211 |                                   211 |                 2 |
| 2020-23  |                                            237 |                                     237 |                                 236 |                                   236 |                 0 |
| 2024–26* |                                             56 |                                      56 |                                  56 |                                    55 |                 0 |

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
- `t7_cu_d1` = 29.3
- `t7_f_d1` = 6.2
- `t7_f_share` = 39 %
- `t7_slc_share` = 26 %
- `t7_cu_share` = 10 %
- `t7_cwt_share` = 17 %
- `t7_f_n` = 246
- `t7_cwt_largest` = Separate Lift + Cruise · one wing · no tilting propulsor
- `t7_cu_largest` = Tilt Propulsor · 1-3 propulsors
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
- `f_d2_last` = 3.25
- `f_d2_edge` = 3.62
- `c_d2_last` = 4.55
- `c_d2_edge` = 4.73
- `cu_d2_w1` = 10.61
- `cu_d2_w1_edge` = 12.15
- `cu_d2_w2` = 10.12
- `cu_d2_w2_edge` = 11.89
- `dq_main` = −0.028
- `dq_main_edge` = −0.020
- `top3_cwt` = 47 %
- `top3_cu` = 26 %
- `rarefy_n` = 40
- `perms` = 1000
- `seed` = 42
- `f_ap_d2` = 3.14
- `f_ap_d2_edge` = 3.50
- `dq_ap` = +0.009
- `dq_ap_edge` = −0.023
- `f_all_short` = 1
- `max_c_all` = 36.2 %
- `dq_f_all` = −0.028
- `dq_f_all_edge` = −0.020
