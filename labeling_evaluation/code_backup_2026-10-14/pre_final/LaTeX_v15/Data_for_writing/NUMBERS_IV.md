# NUMBERS_IV — Analysis IV (evolution of the design space)

Written by notebook 51 (`viz/thesis_latex_part4.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`.

## IV.1 Layout shares per cohort (share of the architecture's designs; count/architecture total)

Source: `q6_leading_layout_by_architecture.csv`. The first two cohorts hold few designs.

| architecture   | layout                                      | <= 2011        | 2012-15        | 2016-19        | 2020-23        |
|:---------------|:--------------------------------------------|:---------------|:---------------|:---------------|:---------------|
| Lift + Cruise  | on booms                                    | 47.1 % (8/17)  | 55.6 % (5/9)   | 43.8 % (21/48) | 48.0 % (36/75) |
| Lift + Cruise  | on the body                                 | 23.5 % (4/17)  | 11.1 % (1/9)   | 20.8 % (10/48) | 20.0 % (15/75) |
| Lift + Cruise  | on the body, stowed in cruise               | 0.0 % (0/17)   | 11.1 % (1/9)   | 2.1 % (1/48)   | 1.3 % (1/75)   |
| Lift + Cruise  | on the wing                                 | 29.4 % (5/17)  | 22.2 % (2/9)   | 22.9 % (11/48) | 25.3 % (19/75) |
| Lift + Cruise  | on booms, stowed in cruise                  | 0.0 % (0/17)   | 0.0 % (0/9)    | 6.2 % (3/48)   | 4.0 % (3/75)   |
| Lift + Cruise  | on the wing, stowed in cruise               | 0.0 % (0/17)   | 0.0 % (0/9)    | 4.2 % (2/48)   | 1.3 % (1/75)   |
| Tilt Propulsor | one tilting set                             | 75.0 % (15/20) | 50.0 % (10/20) | 34.0 % (17/50) | 30.6 % (15/49) |
| Tilt Propulsor | 2+ tilting sets, in one place               | 5.0 % (1/20)   | 20.0 % (4/20)  | 36.0 % (18/50) | 28.6 % (14/49) |
| Tilt Propulsor | 2+ tilting sets, in 2+ places               | 20.0 % (4/20)  | 30.0 % (6/20)  | 30.0 % (15/50) | 38.8 % (19/49) |
| Tilt Propulsor | no tilting set recorded                     | 0.0 % (0/20)   | 0.0 % (0/20)   | 0.0 % (0/50)   | 2.0 % (1/49)   |
| CVT            | a wing tilts · fixed elsewhere              | 0.0 % (0/5)    | 30.0 % (3/10)  | 3.6 % (1/28)   | 7.5 % (4/53)   |
| CVT            | a wing tilts · fixed on booms               | 0.0 % (0/5)    | 10.0 % (1/10)  | 0.0 % (0/28)   | 3.8 % (2/53)   |
| CVT            | propulsors and a wing tilt · no fixed propulsor  | 0.0 % (0/5)    | 10.0 % (1/10)  | 3.6 % (1/28)   | 3.8 % (2/53)   |
| CVT            | propulsors tilt · fixed elsewhere           | 80.0 % (4/5)   | 50.0 % (5/10)  | 46.4 % (13/28) | 28.3 % (15/53) |
| CVT            | propulsors tilt · fixed on booms            | 20.0 % (1/5)   | 0.0 % (0/10)   | 39.3 % (11/28) | 52.8 % (28/53) |
| CVT            | tilt not recorded · fixed elsewhere         | 0.0 % (0/5)    | 0.0 % (0/10)   | 7.1 % (2/28)   | 0.0 % (0/53)   |
| CVT            | propulsors and a wing tilt · fixed on booms | 0.0 % (0/5)    | 0.0 % (0/10)   | 0.0 % (0/28)   | 1.9 % (1/53)   |
| CVT            | propulsors tilt · no fixed propulsor             | 0.0 % (0/5)    | 0.0 % (0/10)   | 0.0 % (0/28)   | 1.9 % (1/53)   |

## IV.1 and IV.2 Traces per architecture and cohort

Source: `q6_architecture_traces_by_cohort.csv` (frame `dw` of `viz/thesis_q6.py`).

| architecture             | cohort   |   aircraft |   tilting sets (mean) |   propulsors (median) |   share with propulsors on booms |   share with a ducted propulsor |   ducted share, propulsors on booms |   ducted share, no propulsors on booms |
|:-------------------------|:---------|-----------:|----------------------:|----------------------------:|----------------------------:|---------------------------:|-------------------------------:|----------------------------------:|
| Lift + Cruise            | <= 2011  |         17 |                 0     |                        10   |                       0.471 |                      0.529 |                        nan     |                           nan     |
| Lift + Cruise            | 2012-15  |          9 |                 0     |                         5   |                       0.667 |                      0.222 |                        nan     |                           nan     |
| Lift + Cruise            | 2016-19  |         48 |                 0     |                         6.5 |                       0.521 |                      0.292 |                        nan     |                           nan     |
| Lift + Cruise            | 2020-23  |         75 |                 0     |                         7   |                       0.56  |                      0.48  |                        nan     |                           nan     |
| Tilt Propulsor           | <= 2011  |         20 |                 1.35  |                         2   |                       0.2   |                      0.15  |                        nan     |                           nan     |
| Tilt Propulsor           | 2012-15  |         20 |                 1.65  |                         2   |                       0.3   |                      0.45  |                        nan     |                           nan     |
| Tilt Propulsor           | 2016-19  |         50 |                 1.8   |                         4   |                       0.4   |                      0.42  |                        nan     |                           nan     |
| Tilt Propulsor           | 2020-23  |         49 |                 1.755 |                         4   |                       0.388 |                      0.306 |                        nan     |                           nan     |
| Combined Vectored Thrust | <= 2011  |          5 |                 1     |                         4   |                       0.2   |                      0.8   |                        nan     |                           nan     |
| Combined Vectored Thrust | 2012-15  |         10 |                 1.1   |                         4   |                       0.2   |                      0.4   |                        nan     |                             0.5   |
| Combined Vectored Thrust | 2016-19  |         28 |                 1.357 |                         5   |                       0.607 |                      0.464 |                          0.353 |                             0.636 |
| Combined Vectored Thrust | 2020-23  |         53 |                 1.434 |                         6   |                       0.623 |                      0.321 |                          0.061 |                             0.75  |
| Tilt Wing                | <= 2011  |          4 |               nan     |                       nan   |                     nan     |                    nan     |                        nan     |                           nan     |
| Tilt Wing                | 2012-15  |          6 |                 1.333 |                         4   |                       0     |                      0     |                        nan     |                           nan     |
| Tilt Wing                | 2016-19  |         23 |                 1.696 |                         8   |                       0.261 |                      0.348 |                        nan     |                           nan     |
| Tilt Wing                | 2020-23  |         19 |                 1.421 |                         4   |                       0.263 |                      0.158 |                        nan     |                           nan     |
| Multicopter               | <= 2011  |          9 |                 0.222 |                         4   |                       0.111 |                      0.778 |                        nan     |                           nan     |
| Multicopter               | 2012-15  |          4 |               nan     |                       nan   |                     nan     |                    nan     |                        nan     |                           nan     |
| Multicopter               | 2016-19  |         16 |                 0.688 |                         5.5 |                       0.812 |                      0.438 |                        nan     |                           nan     |
| Multicopter               | 2020-23  |         15 |                 0.4   |                         6   |                       0.6   |                      0.733 |                        nan     |                           nan     |

## IV.2 Median propulsors per architecture and cohort

Source: `q6_propulsor_units_median_by_cohort.csv` (the aircraft of the architecture with a propulsor count above zero, as the traces frame; 2024–26 is incomplete and not read). The median of Tilt Propulsor goes 2, 2, 4, 4: 2 to 4 is right. The 6 is the median of one layout inside Tilt Propulsor (tilting sets in 2+ places), see below.

| architecture   | <= 2011   | 2012-15   | 2016-19    | 2020-23   | 2024-26 (incomplete)   |
|:---------------|:----------|:----------|:-----------|:----------|:-----------------------|
| Tilt Propulsor | 2 (n 20)  | 2 (n 20)  | 4 (n 50)   | 4 (n 49)  | 7 (n 12)               |
| CVT            | 4 (n 5)   | 4 (n 10)  | 5 (n 28)   | 6 (n 53)  | 6 (n 10)               |
| Lift + Cruise  | 10 (n 17) | 5 (n 9)   | 6.5 (n 48) | 7 (n 75)  | 6.5 (n 16)             |

Median propulsors of the leading layouts, per cohort:

| architecture   | cohort   | leading layout                  |   designs |   median propulsors |
|:---------------|:---------|:--------------------------------|----------:|-------------------------:|
| Lift + Cruise  | <= 2011  | lift propulsors on booms             |         8 |                      8.5 |
| Lift + Cruise  | 2020-23  | lift propulsors on booms             |        36 |                      8   |
| Tilt Propulsor | <= 2011  | one tilting set                 |        15 |                      2   |
| Tilt Propulsor | 2020-23  | tilting sets in 2+ places       |        19 |                      6   |
| CVT            | <= 2011  | tilting rotors, fixed elsewhere |         4 |                      3.5 |
| CVT            | 2020-23  | tilting rotors, fixed on booms  |        28 |                      6   |

## IV.2 Spearman rho and p of every trace (every year to 2023; too thin / constant where not tested)

Source: `q6_driver_trends.csv`.

| trace                                     | driver kind   | architecture                    | code   |   aircraft | first cohort   |   first value |   2020-23 value |   first mean |   2020-23 mean |    rho |             p | movement   |
|:------------------------------------------|:--------------|:--------------------------------|:-------|-----------:|:---------------|--------------:|----------------:|-------------:|---------------:|-------:|--------------:|:-----------|
| tilting joint groups                      | A1            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0    |            0    |         0    |           0    | nan    | nan           | constant   |
| tilting joint groups                      | A1            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          1    |            2    |         1.35 |           1.76 |   0.22 |   0.0103336   | rises      |
| tilting joint groups                      | A1            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          1    |            1    |         1    |           1.43 |   0.25 |   0.0134655   | rises      |
| tilting joint groups                      | A1            | Tilt Wing                       | TW     |         52 | 2012-15        |          1    |            1    |         1.33 |           1.42 |  -0.13 |   0.375686    | flat       |
| tilting joint groups                      | A1            | Multicopter                      | MR     |         44 | <= 2011        |          0    |            0    |         0.22 |           0.4  |   0.11 |   0.459303    | flat       |
| tilting joint groups                      | A1            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          1    |            1    |         0.73 |           0.92 |   0.01 |   0.821981    | flat       |
| tilting joint groups                      | A1            | all classed aircraft            | ALL    |        541 | <= 2011        |          1    |            1    |         0.69 |           0.84 |  -0    |   0.970293    | flat       |
| fuselage kinematics not fixed             | A1            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0    |            0    |       nan    |         nan    |  -0.08 |   0.309115    | flat       |
| fuselage kinematics not fixed             | A1            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0    |            0    |       nan    |         nan    | nan    | nan           | constant   |
| fuselage kinematics not fixed             | A1            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0    |            0    |       nan    |         nan    | nan    | nan           | constant   |
| fuselage kinematics not fixed             | A1            | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0    |       nan    |         nan    |  -0.22 |   0.116098    | flat       |
| fuselage kinematics not fixed             | A1            | Multicopter                      | MR     |         44 | <= 2011        |          0.67 |            0.33 |       nan    |         nan    |  -0.37 |   0.0148405   | falls      |
| fuselage kinematics not fixed             | A1            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.13 |            0.02 |       nan    |         nan    |  -0.15 |   0.000769457 | falls      |
| fuselage kinematics not fixed             | A1            | all classed aircraft            | ALL    |        547 | <= 2011        |          0.19 |            0.09 |       nan    |         nan    |  -0.1  |   0.0185241   | falls      |
| a propulsor retracts or folds its blades  | A2            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0    |            0.07 |       nan    |         nan    |  -0.01 |   0.877824    | flat       |
| a propulsor retracts or folds its blades  | A2            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0    |            0    |       nan    |         nan    |  -0.08 |   0.363372    | flat       |
| a propulsor retracts or folds its blades  | A2            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.2  |            0.13 |       nan    |         nan    |  -0.15 |   0.155901    | flat       |
| a propulsor retracts or folds its blades  | A2            | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0.05 |       nan    |         nan    |   0.2  |   0.151381    | flat       |
| a propulsor retracts or folds its blades  | A2            | Multicopter                      | MR     |         44 | <= 2011        |          0    |            0.13 |       nan    |         nan    |   0.22 |   0.156994    | flat       |
| a propulsor retracts or folds its blades  | A2            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.02 |            0.07 |       nan    |         nan    |   0.01 |   0.774574    | flat       |
| a propulsor retracts or folds its blades  | A2            | all classed aircraft            | ALL    |        541 | <= 2011        |          0.02 |            0.06 |       nan    |         nan    |   0.01 |   0.863805    | flat       |
| booms stow                                | B             | Lift + Cruise                   | SLC    |         81 | <= 2011        |          0    |            0.05 |       nan    |         nan    |   0.04 |   0.745846    | flat       |
| booms stow                                | B             | Tilt Propulsor                  | TR     |         52 | 2012-15        |          0    |            0    |       nan    |         nan    | nan    | nan           | constant   |
| booms stow                                | B             | Combined Vectored Thrust        | CVT    |         55 | 2016-19        |          0.06 |            0.06 |       nan    |         nan    |  -0.08 |   0.580149    | flat       |
| booms stow                                | B             | Tilt Wing                       | TW     |         15 | 2016-19        |          0    |            0    |       nan    |         nan    | nan    | nan           | too thin   |
| booms stow                                | B             | Multicopter                      | MR     |         25 | 2016-19        |          0    |            0.11 |       nan    |         nan    |   0.2  |   0.332409    | flat       |
| booms stow                                | B             | five drawn architectures pooled | ALL5   |        228 | <= 2011        |          0    |            0.05 |       nan    |         nan    |   0.03 |   0.673537    | flat       |
| booms stow                                | B             | all classed aircraft            | ALL    |        257 | <= 2011        |          0    |            0.04 |       nan    |         nan    |   0.04 |   0.547882    | flat       |
| propulsors                          | A1            | Lift + Cruise                   | SLC    |        149 | <= 2011        |         10    |            7    |       nan    |         nan    |  -0.01 |   0.86721     | flat       |
| propulsors                          | A1            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          2    |            4    |       nan    |         nan    |   0.41 |   6.49124e-07 | rises      |
| propulsors                          | A1            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          4    |            6    |       nan    |         nan    |   0.31 |   0.00211034  | rises      |
| propulsors                          | A1            | Tilt Wing                       | TW     |         52 | 2012-15        |          4    |            4    |       nan    |         nan    |   0.09 |   0.521187    | flat       |
| propulsors                          | A1            | Multicopter                      | MR     |         44 | <= 2011        |          4    |            6    |       nan    |         nan    |   0.27 |   0.0751994   | flat       |
| propulsors                          | A1            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          4    |            6    |       nan    |         nan    |   0.25 |   3.57415e-08 | rises      |
| propulsors                          | A1            | all classed aircraft            | ALL    |        542 | <= 2011        |          4    |            6    |       nan    |         nan    |   0.25 |   5.31179e-09 | rises      |
| propulsors carried on booms                    | A1            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.47 |            0.56 |       nan    |         nan    |   0.1  |   0.233259    | flat       |
| propulsors carried on booms                    | A1            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.2  |            0.39 |       nan    |         nan    |   0.11 |   0.19078     | flat       |
| propulsors carried on booms                    | A1            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.2  |            0.62 |       nan    |         nan    |   0.22 |   0.0329559   | rises      |
| propulsors carried on booms                    | A1            | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0.26 |       nan    |         nan    |   0.29 |   0.0389577   | rises      |
| propulsors carried on booms                    | A1            | Multicopter                      | MR     |         44 | <= 2011        |          0.11 |            0.6  |       nan    |         nan    |   0.29 |   0.0543699   | flat       |
| propulsors carried on booms                    | A1            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.25 |            0.51 |       nan    |         nan    |   0.17 |   0.00016226  | rises      |
| propulsors carried on booms                    | A1            | all classed aircraft            | ALL    |        541 | <= 2011        |          0.25 |            0.49 |       nan    |         nan    |   0.15 |   0.000590223 | rises      |
| stations carrying propulsors                   | A1            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          2    |            2    |         1.94 |           2.01 |   0.02 |   0.84224     | flat       |
| stations carrying propulsors                   | A1            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          1    |            1    |         1.3  |           1.45 |   0.19 |   0.0280304   | rises      |
| stations carrying propulsors                   | A1            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          2    |            2    |         1.8  |           1.91 |  -0.03 |   0.774039    | flat       |
| stations carrying propulsors                   | A1            | Tilt Wing                       | TW     |         52 | 2012-15        |          1    |            1    |         1.33 |           1.47 |  -0.01 |   0.941461    | flat       |
| stations carrying propulsors                   | A1            | Multicopter                      | MR     |         44 | <= 2011        |          1    |            1    |         1    |           1.13 |   0.25 |   0.105669    | flat       |
| stations carrying propulsors                   | A1            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          1    |            2    |         1.49 |           1.74 |   0.15 |   0.000807054 | rises      |
| stations carrying propulsors                   | A1            | all classed aircraft            | ALL    |        541 | <= 2011        |          1    |            2    |         1.46 |           1.72 |   0.14 |   0.00119977  | rises      |
| booms present                             | A2            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.47 |            0.56 |       nan    |         nan    |   0.1  |   0.233259    | flat       |
| booms present                             | A2            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.2  |            0.41 |       nan    |         nan    |   0.13 |   0.140145    | flat       |
| booms present                             | A2            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.4  |            0.62 |       nan    |         nan    |   0.18 |   0.0842121   | flat       |
| booms present                             | A2            | Tilt Wing                       | TW     |         52 | 2012-15        |          0.17 |            0.26 |       nan    |         nan    |   0.1  |   0.495078    | flat       |
| booms present                             | A2            | Multicopter                      | MR     |         44 | <= 2011        |          0.11 |            0.6  |       nan    |         nan    |   0.29 |   0.0543699   | flat       |
| booms present                             | A2            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.29 |            0.52 |       nan    |         nan    |   0.15 |   0.000866961 | rises      |
| booms present                             | A2            | all classed aircraft            | ALL    |        569 | <= 2011        |          0.29 |            0.49 |       nan    |         nan    |   0.13 |   0.00250651  | rises      |
| wing propulsors at the leading edge            | A2            | Lift + Cruise                   | SLC    |         70 | <= 2011        |          0    |            0.46 |       nan    |         nan    |   0.16 |   0.172791    | flat       |
| wing propulsors at the leading edge            | A2            | Tilt Propulsor                  | TR     |         82 | <= 2011        |          1    |            0.82 |       nan    |         nan    |  -0.12 |   0.295449    | flat       |
| wing propulsors at the leading edge            | A2            | Combined Vectored Thrust        | CVT    |         65 | 2012-15        |          0.88 |            0.73 |       nan    |         nan    |   0.03 |   0.783067    | flat       |
| wing propulsors at the leading edge            | A2            | Tilt Wing                       | TW     |         46 | 2012-15        |          1    |            0.87 |       nan    |         nan    |  -0.27 |   0.0730318   | flat       |
| wing propulsors at the leading edge            | A2            | Multicopter                      | MR     |          0 |                |        nan    |          nan    |       nan    |         nan    | nan    | nan           | too thin   |
| wing propulsors at the leading edge            | A2            | five drawn architectures pooled | ALL5   |        263 | <= 2011        |          0.66 |            0.69 |       nan    |         nan    |  -0.05 |   0.428835    | flat       |
| wing propulsors at the leading edge            | A2            | all classed aircraft            | ALL    |        291 | <= 2011        |          0.63 |            0.71 |       nan    |         nan    |  -0.02 |   0.680941    | flat       |
| a pusher propulsor                             | A2            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.41 |            0.49 |       nan    |         nan    |   0.11 |   0.165596    | flat       |
| a pusher propulsor                             | A2            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0    |            0.12 |       nan    |         nan    |   0.14 |   0.0954059   | flat       |
| a pusher propulsor                             | A2            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.2  |            0.11 |       nan    |         nan    |  -0.12 |   0.257299    | flat       |
| a pusher propulsor                             | A2            | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0.05 |       nan    |         nan    |  -0.07 |   0.603419    | flat       |
| a pusher propulsor                             | A2            | Multicopter                      | MR     |         44 | <= 2011        |          0    |            0.07 |       nan    |         nan    |   0.22 |   0.142915    | flat       |
| a pusher propulsor                             | A2            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.16 |            0.24 |       nan    |         nan    |   0.11 |   0.0120554   | rises      |
| a pusher propulsor                             | A2            | all classed aircraft            | ALL    |        541 | <= 2011        |          0.15 |            0.23 |       nan    |         nan    |   0.11 |   0.00838591  | rises      |
| two or more wing panels                   | A2            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.35 |            0.37 |       nan    |         nan    |   0.12 |   0.133695    | flat       |
| two or more wing panels                   | A2            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.2  |            0.35 |       nan    |         nan    |   0.12 |   0.143134    | flat       |
| two or more wing panels                   | A2            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.2  |            0.36 |       nan    |         nan    |   0.11 |   0.27168     | flat       |
| two or more wing panels                   | A2            | Tilt Wing                       | TW     |         52 | 2012-15        |          0.33 |            0.37 |       nan    |         nan    |  -0.16 |   0.248543    | flat       |
| two or more wing panels                   | A2            | Multicopter                      | MR     |         44 | <= 2011        |          0    |            0    |       nan    |         nan    | nan    | nan           | constant   |
| two or more wing panels                   | A2            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.24 |            0.34 |       nan    |         nan    |   0.1  |   0.0285433   | rises      |
| two or more wing panels                   | A2            | all classed aircraft            | ALL    |        568 | <= 2011        |          0.22 |            0.34 |       nan    |         nan    |   0.1  |   0.0182089   | rises      |
| swept or delta main wing                  | B             | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.82 |            0.43 |       nan    |         nan    |  -0.14 |   0.0941387   | flat       |
| swept or delta main wing                  | B             | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.15 |            0.31 |       nan    |         nan    |   0.05 |   0.577974    | flat       |
| swept or delta main wing                  | B             | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.2  |            0.26 |       nan    |         nan    |  -0.03 |   0.757834    | flat       |
| swept or delta main wing                  | B             | Tilt Wing                       | TW     |         52 | 2012-15        |          0.17 |            0    |       nan    |         nan    |  -0.11 |   0.421178    | flat       |
| swept or delta main wing                  | B             | Multicopter                      | MR     |          0 |                |        nan    |          nan    |       nan    |         nan    | nan    | nan           | too thin   |
| swept or delta main wing                  | B             | five drawn architectures pooled | ALL5   |        436 | <= 2011        |          0.39 |            0.31 |       nan    |         nan    |  -0.03 |   0.602244    | flat       |
| swept or delta main wing                  | B             | all classed aircraft            | ALL    |        489 | <= 2011        |          0.42 |            0.31 |       nan    |         nan    |  -0.02 |   0.691262    | flat       |
| no tail surface                           | A2            | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.53 |            0.23 |       nan    |         nan    |  -0.1  |   0.207683    | flat       |
| no tail surface                           | A2            | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.05 |            0.27 |       nan    |         nan    |   0.12 |   0.163557    | flat       |
| no tail surface                           | A2            | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.4  |            0.08 |       nan    |         nan    |  -0.3  |   0.00303835  | falls      |
| no tail surface                           | A2            | Tilt Wing                       | TW     |         52 | 2012-15        |          0.33 |            0.32 |       nan    |         nan    |   0.01 |   0.953745    | flat       |
| no tail surface                           | A2            | Multicopter                      | MR     |         44 | <= 2011        |          0.44 |            0.87 |       nan    |         nan    |   0.3  |   0.0507187   | flat       |
| no tail surface                           | A2            | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.31 |            0.25 |       nan    |         nan    |  -0.06 |   0.168334    | flat       |
| no tail surface                           | A2            | all classed aircraft            | ALL    |        545 | <= 2011        |          0.32 |            0.27 |       nan    |         nan    |  -0.05 |   0.286438    | flat       |
| a ducted propulsor                             | B             | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0.53 |            0.48 |       nan    |         nan    |   0.05 |   0.547395    | flat       |
| a ducted propulsor                             | B             | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.15 |            0.31 |       nan    |         nan    |   0.04 |   0.652007    | flat       |
| a ducted propulsor                             | B             | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0.8  |            0.32 |       nan    |         nan    |  -0.2  |   0.0519001   | flat       |
| a ducted propulsor                             | B             | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0.16 |       nan    |         nan    |  -0    |   0.982826    | flat       |
| a ducted propulsor                             | B             | Multicopter                      | MR     |         44 | <= 2011        |          0.78 |            0.73 |       nan    |         nan    |   0.04 |   0.817968    | flat       |
| a ducted propulsor                             | B             | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.44 |            0.39 |       nan    |         nan    |  -0.02 |   0.616614    | flat       |
| a ducted propulsor                             | B             | all classed aircraft            | ALL    |        541 | <= 2011        |          0.41 |            0.37 |       nan    |         nan    |  -0.03 |   0.488923    | flat       |
| ground contact drawn                      | B             | Lift + Cruise                   | SLC    |        149 | <= 2011        |          0    |            0.27 |       nan    |         nan    |   0.11 |   0.168335    | flat       |
| ground contact drawn                      | B             | Tilt Propulsor                  | TR     |        139 | <= 2011        |          0.35 |            0.39 |       nan    |         nan    |   0.09 |   0.28989     | flat       |
| ground contact drawn                      | B             | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          0    |            0.32 |       nan    |         nan    |   0.18 |   0.0742997   | flat       |
| ground contact drawn                      | B             | Tilt Wing                       | TW     |         52 | 2012-15        |          0    |            0.21 |       nan    |         nan    |  -0.01 |   0.939941    | flat       |
| ground contact drawn                      | B             | Multicopter                      | MR     |         44 | <= 2011        |          0.11 |            0.6  |       nan    |         nan    |   0.38 |   0.0101934   | rises      |
| ground contact drawn                      | B             | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          0.16 |            0.33 |       nan    |         nan    |   0.11 |   0.0176006   | rises      |
| ground contact drawn                      | B             | all classed aircraft            | ALL    |        547 | <= 2011        |          0.2  |            0.35 |       nan    |         nan    |   0.09 |   0.0300221   | rises      |
| wheeled gear, of the ground contact drawn | B             | Lift + Cruise                   | SLC    |         37 | 2016-19        |          0.53 |            0.55 |       nan    |         nan    |   0.04 |   0.796529    | flat       |
| wheeled gear, of the ground contact drawn | B             | Tilt Propulsor                  | TR     |         46 | <= 2011        |          0.71 |            0.53 |       nan    |         nan    |  -0.17 |   0.245932    | flat       |
| wheeled gear, of the ground contact drawn | B             | Combined Vectored Thrust        | CVT    |         21 | 2020-23        |          0.71 |            0.71 |       nan    |         nan    |   0.16 |   0.487083    | flat       |
| wheeled gear, of the ground contact drawn | B             | Tilt Wing                       | TW     |         12 | 2016-19        |          0.29 |          nan    |       nan    |         nan    | nan    | nan           | too thin   |
| wheeled gear, of the ground contact drawn | B             | Multicopter                      | MR     |         15 | 2020-23        |          0.22 |            0.22 |       nan    |         nan    | nan    | nan           | too thin   |
| wheeled gear, of the ground contact drawn | B             | five drawn architectures pooled | ALL5   |        131 | <= 2011        |          0.78 |            0.52 |       nan    |         nan    |  -0.07 |   0.398823    | flat       |
| wheeled gear, of the ground contact drawn | B             | all classed aircraft            | ALL    |        170 | <= 2011        |          0.75 |            0.49 |       nan    |         nan    |  -0.08 |   0.294571    | flat       |
| propulsor types                           | C             | Lift + Cruise                   | SLC    |        149 | <= 2011        |          3    |            3    |         2.59 |           2.71 |  -0.03 |   0.680579    | flat       |
| propulsor types                           | C             | Tilt Propulsor                  | TR     |        139 | <= 2011        |          1    |            2    |         1.35 |           1.8  |   0.23 |   0.0060762   | rises      |
| propulsor types                           | C             | Combined Vectored Thrust        | CVT    |         96 | <= 2011        |          2    |            3    |         2.4  |           2.75 |   0.14 |   0.165697    | flat       |
| propulsor types                           | C             | Tilt Wing                       | TW     |         52 | 2012-15        |          1.5  |            1    |         1.5  |           1.58 |  -0.06 |   0.686244    | flat       |
| propulsor types                           | C             | Multicopter                      | MR     |         44 | <= 2011        |          2    |            2    |         1.89 |           1.8  |   0.07 |   0.642792    | flat       |
| propulsor types                           | C             | five drawn architectures pooled | ALL5   |        480 | <= 2011        |          2    |            2    |         1.91 |           2.34 |   0.18 |   0.000100198 | rises      |
| propulsor types                           | C             | all classed aircraft            | ALL    |        541 | <= 2011        |          2    |            2    |         1.85 |           2.31 |   0.17 |   4.53935e-05 | rises      |

## IV.2 The driver table

Source: `q6_driver_verdicts.csv`.

| trace                                        | where it moved (every year to 2023)                                                          | goes with (driver: what it predicts)                                                                  | goes against (driver: what it predicts)                              | what it means                                                                                                  |
|:---------------------------------------------|:---------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------|
| ● tilting sets per aircraft                  | rises in Tilt Propulsor (ρ +0.22, p 0.01); rises in CVT (ρ +0.25, p 0.01); pooled: flat      | regime transition (more)                                                                              | development and certification cost (fewer); maintenance cost (fewer) | drivers disagree; it moved with those under 'goes with'; per propulsor it falls                           |
| a body that tilts or rotates                 | falls in Multicopter (ρ -0.37, p 0.01); pooled: falls                                         | occupant presence (fewer)                                                                             | regime transition (more)                                             | drivers disagree; it moved with those under 'goes with'                                                        |
| ● propulsors per aircraft               | rises in Tilt Propulsor (ρ +0.41, p < 0.001); rises in CVT (ρ +0.31, p 0.002); pooled: rises | distributed propulsion and propulsor control (more); failure tolerance (more); community noise (more) | —                                                                    | 3 drivers predict it; the labelled dataset cannot say which acts                                               |
| ● propulsors carried on booms           | rises in CVT (ρ +0.22, p 0.03); rises in Tilt Wing (ρ +0.29, p 0.04); pooled: rises          | distributed propulsion and propulsor control (more)                                                   | —                                                                    | one driver predicts it, and it moved that way                                                                  |
| places carrying propulsors per aircraft | rises in Tilt Propulsor (ρ +0.19, p 0.03); pooled: rises                                     | distributed propulsion and propulsor control (more)                                                   | —                                                                    | one driver predicts it, and it moved that way                                                                  |
| booms present                                | no trend detected in any architecture; pooled: rises                                         | —                                                                                                     | —                                                                    | no driver predicts a direction; only physical limits bear on it (hover load path, flow interference and drag)  |
| a pusher propulsor                                | no trend detected in any architecture; pooled: rises                                         | —                                                                                                     | —                                                                    | no driver predicts a direction; only physical limits bear on it (flow interference and drag)                   |
| two or more wing panels                      | no trend detected in any architecture; pooled: rises                                         | mission range and speed (either way)                                                                  | —                                                                    | one driver predicts it, and it moved that way                                                                  |
| no tail surface                              | falls in CVT (ρ -0.30, p 0.003); pooled: flat                                                | —                                                                                                     | —                                                                    | no driver predicts a direction; only physical limits bear on it (cruise stability and control)                 |
| landing gear drawn                           | rises in Multicopter (ρ +0.38, p 0.01); pooled: rises                                         | payload (either way); operating environment (either way); maintenance cost (either way)               | —                                                                    | 3 drivers predict it; the labelled dataset cannot say which acts                                               |
| ● propulsor types per aircraft               | rises in Tilt Propulsor (ρ +0.23, p 0.006); pooled: rises                                    | —                                                                                                     | development and certification cost (fewer); production cost (fewer)  | moved against the only direction any driver predicts; in Tilt Propulsor the added type is a second tilting set |

## IV.2 Links: Tilt Propulsors by tilting sets, CVT ducting by boom layout

Source: frame `links` of `viz/thesis_q6.py`.

| link                                         | group             |   aircraft |   median |   mean |    rho |           p | movement   |
|:---------------------------------------------|:------------------|-----------:|---------:|-------:|-------:|------------:|:-----------|
| Tilt Rotor: propulsors by tilting sets | 1                 |         57 |        2 |  3.42  | nan    | nan         |            |
| Tilt Rotor: propulsors by tilting sets | 2                 |         73 |        4 |  6.9   | nan    | nan         |            |
| Tilt Rotor: propulsors by tilting sets | 3 or more         |         20 |        6 |  7     | nan    | nan         |            |
| CVT: ducted share by boom layout             | propulsors on booms    |         53 |      nan |  0.186 |  -0.31 |   0.0249761 | falls      |
| CVT: ducted share by boom layout             | no propulsors on booms |         43 |      nan |  0.638 |   0.12 |   0.455621  | flat       |
| CVT: ducted share by boom layout             | all CVT           |         96 |      nan |  0.387 |  -0.2  |   0.0519001 | flat       |

## IV.2 Tilt mechanisms per propulsor, per architecture and cohort

Source: `q6_tilt_mechanisms_per_propulsor.csv` (tilting sets / propulsors, mean per cohort, cohorts of 5 designs or more).

| architecture   | cohort   |   aircraft |   mean_per_unit |   rho |      p |   aircraft_in_test |
|:---------------|:---------|-----------:|----------------:|------:|-------:|-------------------:|
| Tilt Propulsor | <= 2011  |         20 |          0.5042 | -0.32 | 0.0001 |                139 |
| Tilt Propulsor | 2012-15  |         20 |          0.5925 | -0.32 | 0.0001 |                139 |
| Tilt Propulsor | 2016-19  |         50 |          0.4683 | -0.32 | 0.0001 |                139 |
| Tilt Propulsor | 2020-23  |         49 |          0.3886 | -0.32 | 0.0001 |                139 |
| CVT            | <= 2011  |          5 |          0.2258 | -0.09 | 0.4063 |                 96 |
| CVT            | 2012-15  |         10 |          0.2479 | -0.09 | 0.4063 |                 96 |
| CVT            | 2016-19  |         28 |          0.2453 | -0.09 | 0.4063 |                 96 |
| CVT            | 2020-23  |         53 |          0.2247 | -0.09 | 0.4063 |                 96 |
| Tilt Wing      | <= 2011  |          4 |        nan      | -0.2  | 0.1586 |                 52 |
| Tilt Wing      | 2012-15  |          6 |          0.4167 | -0.2  | 0.1586 |                 52 |
| Tilt Wing      | 2016-19  |         23 |          0.2683 | -0.2  | 0.1586 |                 52 |
| Tilt Wing      | 2020-23  |         19 |          0.3202 | -0.2  | 0.1586 |                 52 |

Pooled over Tilt Propulsor, CVT and Tilt Wing (mean per cohort): <= 2011 0.467, 2012-15 0.467, 2016-19 0.361, 2020-23 0.306

## Future work: distance of each cohort from the first, and Rao's Q (`q6_centroid_dispersion`; leaves the dissertation)

Source: `q6_centroid_dispersion.csv`. Gower distance over 34 dimensions (four systems, each weighing 1), 625 designs; 200 permutations, seed 42, cohort sizes kept; band = 2.5th to 97.5th percentile. Distance of a cohort = mean Gower distance between its designs and those of ≤2011 minus the mean of the two Rao's Q.

| cohort   |   aircraft |   d_between |   d_between_low |   d_between_high |      Q |   Q of the earliest cohorts |      ΔQ |   ΔQ permutation low |   ΔQ permutation high | below band   |
|:---------|-----------:|------------:|----------------:|-----------------:|-------:|----------------------------:|--------:|---------------------:|----------------------:|:-------------|
| <= 2011  |         63 |      0      |          0      |           0      | 0.5772 |                      0.5723 |  0.0049 |              -0.0209 |                0.0209 | False        |
| 2012-15  |         58 |      0.0141 |          0.0048 |           0.0189 | 0.5675 |                      0.5723 | -0.0049 |              -0.0209 |                0.0209 | False        |
| 2016-19  |        211 |      0.0101 |          0.0028 |           0.0119 | 0.5958 |                      0.5723 |  0.0234 |              -0.018  |                0.0435 | False        |
| 2020-23  |        237 |      0.0155 |          0.0025 |           0.0115 | 0.5555 |                      0.5723 | -0.0168 |              -0.0149 |                0.0398 | True         |

## Numbers quoted by the Results text, IV.1 (sub-question C)

Source: `viz/thesis_q6.py` numbers(ctx).

- `cvt_rb_w4` = 53 %
- `cvt_re_w3` = 46 %
- `slc_lead_w4` = 48 %
- `slc_poss` = 6
- `tr_one_w1` = 75 %
- `tr_one_w4` = 31 %
- `tr_twost_w4` = 39 %
- `w3` = 2016-19

## Numbers quoted by the Results text, IV.2 (sub-question D)

Source: `viz/thesis_q6.py` numbers(ctx).

- `cvt_duct_booms_w3` = 35 %
- `cvt_duct_booms_w4` = 6.1 %
- `cvt_onb_w1` = 20 %
- `cvt_onb_w4` = 62 %
- `slc_onb_w4` = 56 %
- `tr_units_w1` = 2
- `tr_units_w4` = 4
- `traces_moving` = 8

## IV.2 Representative aircraft (`q6_iv2_representative_aircraft`)

Source: `q6_iv2_representative_aircraft.csv`; shares are those of the layout figure.

| architecture   | cohort   | layout                          |   share of the architecture |   designs in the layout |   designs in the architecture | patent number   | design identifier   |   propulsors |   median propulsors of the layout in the cohort | view            | figure key   |
|:---------------|:---------|:--------------------------------|----------------------------:|------------------------:|------------------------------:|:----------------|:--------------------|------------------:|-------------------------------------------:|:----------------|:-------------|
| Lift + Cruise  | <= 2011  | lift propulsors on booms             |                      0.4706 |                       8 |                            17 | US2013020429A1  | US2013020429A1_ua1  |                10 |                                        8.5 | Top             | 1            |
| Lift + Cruise  | 2020-23  | lift propulsors on booms             |                      0.48   |                      36 |                            75 | US2022281593A1  | US2022281593A1_ua1  |                 8 |                                        8   | Top             | 1            |
| Tilt Propulsor | <= 2011  | one tilting set                 |                      0.75   |                      15 |                            20 | US2013026303A1  | US2013026303A1_ua1  |                 2 |                                        2   | Top             | 13           |
| Tilt Propulsor | 2020-23  | tilting sets in 2+ places       |                      0.3878 |                      19 |                            49 | US2023331379A1  | US2023331379A1_ua1  |                 4 |                                        6   | Top             | 5            |
| CVT            | <= 2011  | tilting rotors, fixed elsewhere |                      0.8    |                       4 |                             5 | US2012091257A1  | US2012091257A1_ua1  |                 3 |                                        3.5 | Top             | 3            |
| CVT            | 2020-23  | tilting rotors, fixed on booms  |                      0.5283 |                      28 |                            53 | US2022306292A1  | US2022306292A1_ua1  |                 6 |                                        6   | Front-Isometric | Fu_D00000    |

## IV.2 Representative aircraft, alternatives (`q6_iv2_representative_aircraft_alt`)

Source: `q6_iv2_representative_aircraft_alt.csv`; shares are those of the layout figure.

| architecture   | cohort   | layout                          |   share of the architecture |   designs in the layout |   designs in the architecture | patent number   | design identifier   |   propulsors |   median propulsors of the layout in the cohort | view   |   figure key |
|:---------------|:---------|:--------------------------------|----------------------------:|------------------------:|------------------------------:|:----------------|:--------------------|------------------:|-------------------------------------------:|:-------|-------------:|
| Lift + Cruise  | <= 2011  | lift propulsors on booms             |                      0.4706 |                       8 |                            17 | US2013020429A1  | US2013020429A1_ua1  |                10 |                                        8.5 | Top    |            1 |
| Lift + Cruise  | 2020-23  | lift propulsors on booms             |                      0.48   |                      36 |                            75 | US2022281593A1  | US2022281593A1_ua1  |                 8 |                                        8   | Top    |            1 |
| Tilt Propulsor | <= 2011  | one tilting set                 |                      0.75   |                      15 |                            20 | US2013026303A1  | US2013026303A1_ua1  |                 2 |                                        2   | Top    |           13 |
| Tilt Propulsor | 2020-23  | tilting sets in 2+ places       |                      0.3878 |                      19 |                            49 | US2021229802A1  | US2021229802A1_ua2  |                 4 |                                        6   | Top    |           18 |
| CVT            | <= 2011  | tilting rotors, fixed elsewhere |                      0.8    |                       4 |                             5 | US2012091257A1  | US2012091257A1_ua1  |                 3 |                                        3.5 | Top    |            3 |
| CVT            | 2020-23  | tilting rotors, fixed on booms  |                      0.5283 |                      28 |                            53 | US2022388648A1  | US2022388648A1_ua1  |                 6 |                                        6   | Top    |            3 |
