# NUMBERS_II — Analysis II (design space)

Written by notebook 50 (`viz/thesis_latex_part2.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`. Levels are A (architecture), A·W·T (architecture, wings, tilt), A·U (architecture, propulsors); the propulsor bands are 1–3, 4, 5–6, 7–8 and 9+. The one design recorded with 0 propulsors (GB202302720D0_ua1, its count never entered under an M2 override) is left out of U (rerun of 2026-10-15).

## Configurations that hold half of each cohort's designs, at A·U (`q6_half_of_cohort`, which leaves the text)

Source: `q6_half_of_cohort.csv`. The figure ranks the configurations by size within the cohort (first column); the old heatmap used the overall-size order (second), which gives 10 for 2016–19 where the text says 10. 2024–26 is incomplete and not read.

| cohort               |   designs |   designs in the 32 A·U configurations of five or more |   configurations that hold half (ranked by size within the cohort) |   same, columns in overall-size order (the old heatmap) |
|:---------------------|----------:|-------------------------------------------------------:|-------------------------------------------------------------------:|--------------------------------------------------------:|
| ≤2011                |        63 |                                                     61 |                                                                  5 |                                                       5 |
| 2012–15              |        58 |                                                     57 |                                                                  5 |                                                       8 |
| 2016–19              |       213 |                                                    201 |                                                                  9 |                                                      10 |
| 2020–23              |       237 |                                                    224 |                                                                  7 |                                                       7 |
| 2024–26 (incomplete) |        56 |                                                     54 |                                                                  6 |                                                       9 |

## Table: dimensions that vary

Source: `q6_selected_fields.csv` (notebook 50, group II1).

| dimension                                  |   designs answering |   options | top share   | most common options                                                          |
|:-------------------------------------------|--------------------:|----------:|:------------|:-----------------------------------------------------------------------------|
| propulsors per design (band)          |                 595 |         5 | 23 %        | 1–3: 136 · 4: 125 · 5–6: 117 · 9+: 117 · 7–8: 100                            |
| tail type                                  |                 600 |        13 | 29 %        | Tailless: 176 · Conventional: 74 · V-tail: 69 · Single fin: 60               |
| places carrying propulsors per design |                 595 |         4 | 48 %        | 2: 286 · 1: 246 · 3: 60 · 4 or more: 3                                       |
| number of wings (winged designs)           |                 547 |         3 | 66 %        | 1: 359 · 2: 172 · 3: 16                                                      |
| landing-gear type                          |                 602 |         3 | 68 %        | Unknown: 411 · Wheeled: 101 · Skids: 90                                      |
| fuselage motion hover to cruise            |                 602 |         4 | 85 %        | Fixed: 511 · Whole-body pitch: 62 · Tail-sitter: 17 · Variable incidence: 12 |
| wing configuration                         |                 541 |         5 | 87 %        | Standard: 471 · Other: 49 · Blended wing body: 16 · Lifting body: 4          |

## Which dimensions the architecture fixes (`q6_fixed_by_architecture`)

Source: `q6_fixed_by_architecture.csv` and `q6_fixed_by_architecture_detail.csv` (notebook 50, group II1, appendix; `viz/thesis_q6.py` fixed_by_architecture).

For each dimension of the table above, on the designs that answer it and have an architecture, the bias-corrected Cramér's V (Bergsma 2013) of dimension × architecture is read with a permutation p (1000 shuffles of the architecture column, one generator seeded 42, dimensions in the table's order; p = share of shuffles at or above the observed V). Per architecture the leading option of the dimension and its share of that architecture's answering designs are read (the detail csv); an architecture with fewer than 10 answering designs is too few to read, and the dimension is fixed in an architecture when the leading option holds 80 % or more of them.

| dimension                                  |   designs answering |   Cramér's V | p       | architectures at 80 % or more   | architectures too few to read                                                                                |
|:-------------------------------------------|--------------------:|-------------:|:--------|:--------------------------------|:-------------------------------------------------------------------------------------------------------------|
| propulsors per design (band)          |                 595 |         0.23 | < 0.001 | 0 of 7 read                     | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle              |
| tail type                                  |                 599 |         0.12 | 0.024   | 0 of 7 read                     | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle              |
| places carrying propulsors per design |                 595 |         0.27 | < 0.001 | 1 of 7 read                     | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle              |
| number of wings (winged designs)           |                 545 |         0.17 | 0.003   | 1 of 7 read                     | Multicopter, Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Personal Flying Vehicle            |
| landing-gear type                          |                 601 |         0.24 | < 0.001 | 0 of 7 read                     | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle              |
| fuselage motion hover to cruise            |                 601 |         0.72 | < 0.001 | 5 of 7 read                     | Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle              |
| wing configuration                         |                 540 |         0.31 | 0.006   | 5 of 6 read                     | Multicopter, Rotorcraft, Stopped/Slowed Rotor Wing, Deflected Slipstream, Hoverbike, Personal Flying Vehicle |

## Table: levels of description

Source: `q7_levels_of_description.csv` (notebook 50, group II2). The family F row is in Analysis III.

| level   |   configurations |   singletons |   ¹D | largest configuration                 | its share   |
|:--------|-----------------:|-------------:|-----:|:--------------------------------------|:------------|
| A       |               12 |            0 |  7.3 | SLC                                   | 26 %        |
| A·W·T   |               39 |           10 | 16.4 | SLC · one wing · no tilting propulsor | 17 %        |
| A·U     |               43 |            3 | 29.3 | TP · 1–3 propulsors              | 10 %        |

## Table: Hill numbers of each level

Source: `q7_hill_numbers_by_level.csv`; all years, 627 designs less those the level cannot name.

| level   |   designs |   ⁰D (configurations) |   ¹D |   ²D |
|:--------|----------:|----------------------:|-----:|-----:|
| A       |       625 |                    12 |  7.3 |  5.7 |
| A·W·T   |       623 |                    39 | 16.4 | 11.3 |
| A·U     |       624 |                    43 | 29.3 | 22.5 |

## Discovery (`q6_discovery_curve`): complete years (to 2023)

Source: `q6_discovery_estimators.csv`; the figure's last-100 cohort and these numbers are on the complete years.

| level   |   designs (complete years) |   configurations seen |   Chao1 |   new in the last 100 designs |   new in the last 100, random order |
|:--------|---------------------------:|----------------------:|--------:|------------------------------:|------------------------------------:|
| A       |                        569 |                    12 |      12 |                           0   |                                 0   |
| A·W·T   |                        568 |                    37 |      41 |                           4.1 |                                 1.6 |
| A·U     |                        568 |                    42 |      43 |                           1.1 |                                 0.6 |

## Core (`q6_configuration_core`)

Source: `q6_configuration_core.csv`. Core: the A·U configurations taken in order of their share of the 2016–23 designs until the cumulative share reaches 50 % (the one that crosses 50 % is included, and any tied with it, on the unrounded shares): 10 configurations holding 55.8 % of the 2016–23 designs; rim: 16 configurations holding 22.7 %. 2024–26 is not drawn. Judgement call on labels: the figure names the core and the 3 largest non-core configurations by their 2016–23 share (unrounded; ties kept); every other point is grey and unnamed.

## Numbers quoted by the Results text, Analysis II (sub-question A)

Source: `viz/thesis_q6.py` numbers(ctx), notebook cells of groups II1–II3.

- `core_n` = 10
- `core_share` = 56 %
- `cu_top_w4` = 11 %
- `cwt_chao` = 41.0
- `cwt_exp` = 1.6
- `cwt_found` = 90 %
- `cwt_new` = 4.1
- `disc_after_last_class` = 362
- `half_w3` = 10
- `half_w4` = 7
- `span_recent` = 2016-23
- `tail_top` = 29 %
- `units_median` = 5
- `units_top` = 23 %
- `w3` = 2016-19
