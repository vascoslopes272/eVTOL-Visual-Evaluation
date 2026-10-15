# NUMBERS_II — Analysis II (design space)

Written by notebook 50 (`viz/thesis_latex_part2.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`. Levels are A (architecture), A·W·T (architecture, wings, tilt), A·U (architecture, propulsor units); the lowest propulsor-unit band is named 0–3.

## Configurations that hold half of each cohort's designs, at A·U (`q6_half_of_cohort`, which leaves the text)

Source: `q6_half_of_cohort.csv`. The figure ranks the configurations by size within the cohort (first column); the old heatmap used the overall-size order (second), which gives 10 for 2016–19 where the text says 10. 2024–26 is incomplete and not read.

| cohort               |   designs |   designs in the 33 A·U configurations of five or more |   configurations that hold half (ranked by size within the cohort) |   same, columns in overall-size order (the old heatmap) |
|:---------------------|----------:|-------------------------------------------------------:|-------------------------------------------------------------------:|--------------------------------------------------------:|
| ≤2011                |        63 |                                                     61 |                                                                  5 |                                                       5 |
| 2012–15              |        58 |                                                     57 |                                                                  5 |                                                       8 |
| 2016–19              |       213 |                                                    203 |                                                                  9 |                                                      10 |
| 2020–23              |       237 |                                                    227 |                                                                  7 |                                                       7 |
| 2024–26 (incomplete) |        56 |                                                     54 |                                                                  6 |                                                       9 |

## Table: dimensions that vary

Source: `q6_selected_fields.csv` (notebook 50, group II1).

| dimension                                  |   designs answering |   options | top share   | most common options                                                          |
|:-------------------------------------------|--------------------:|----------:|:------------|:-----------------------------------------------------------------------------|
| number of wings                            |                 626 |         4 | 57 %        | 1: 359 · 2: 172 · 0: 79 · 3: 16                                              |
| tail type                                  |                 600 |        13 | 29 %        | Tailless: 176 · Conventional: 74 · V-tail: 69 · Single fin: 60               |
| fuselage motion hover to cruise            |                 602 |         4 | 85 %        | Fixed: 511 · Whole-body pitch: 62 · Tail-sitter: 17 · Variable incidence: 12 |
| wing configuration                         |                 541 |         5 | 87 %        | Standard: 471 · Other: 49 · Blended wing body: 16 · Lifting body: 4          |
| landing-gear type                          |                 602 |         3 | 68 %        | Unknown: 411 · Wheeled: 101 · Skids: 90                                      |
| propulsor units per design (band)          |                 596 |         5 | 23 %        | 0–3: 137 · 4: 125 · 5–6: 117 · 9+: 117 · 7–8: 100                            |
| places carrying propulsor units per design |                 596 |         5 | 48 %        | 2: 286 · 1: 246 · 3: 60 · 4 or more: 3 · 0: 1                                |

## Table: levels of description

Source: `q7_levels_of_description.csv` (notebook 50, group II2). The family F row is in Analysis III.

| level   |   configurations |   single-design configurations |   ¹D | largest configuration                 | its share   |
|:--------|-----------------:|-------------------------------:|-----:|:--------------------------------------|:------------|
| A       |               12 |                              0 |  7.3 | SLC                                   | 26 %        |
| A·W·T   |               39 |                             10 | 16.4 | SLC · one wing · no tilting propulsor | 17 %        |
| A·U     |               43 |                              3 | 29.4 | TP · 0–3 propulsor units              | 10 %        |

## Table: Hill numbers of each level

Source: `q7_hill_numbers_by_level.csv`; all years, 627 designs less those the level cannot name.

| level   |   designs |   ⁰D (configurations) |   ¹D |   ²D |
|:--------|----------:|----------------------:|-----:|-----:|
| A       |       625 |                    12 |  7.3 |  5.7 |
| A·W·T   |       623 |                    39 | 16.4 | 11.3 |
| A·U     |       625 |                    43 | 29.4 | 22.6 |

## Discovery (`q6_discovery_curve`): complete years (to 2023)

Source: `q6_discovery_estimators.csv`; the figure's last-100 window and these numbers are on the complete years.

| level   |   designs (complete years) |   configurations seen |   Chao1 |   new in the last 100 designs |   new in the last 100, random order |
|:--------|---------------------------:|----------------------:|--------:|------------------------------:|------------------------------------:|
| A       |                        569 |                    12 |      12 |                           0   |                                 0   |
| A·W·T   |                        568 |                    37 |      41 |                           4.1 |                                 1.6 |
| A·U     |                        569 |                    42 |      43 |                           1.1 |                                 0.6 |

## Core (`q6_configuration_core`)

Source: `q6_configuration_core.csv`. Core: 7 A·U configurations holding 45.4 % of the 2016–23 designs; rim: 17 configurations holding 23.8 %. 2024–26 is not drawn.

## Numbers quoted by the Results text, Analysis II (sub-question A)

Source: `viz/thesis_q6.py` numbers(ctx), notebook cells of groups II1–II3.

- `core_n` = 7
- `core_share` = 45 %
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
