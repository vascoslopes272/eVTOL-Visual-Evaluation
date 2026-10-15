# Assignee rule change, Analysis V (2026-10-15)

**Rule.** A design goes to the co-assignee of its representative patent that files the most patent families in the whole dataset (1 639 patents);
every co-assignee is resolved with the existing grouper (an organisation it does not list keeps the name read from the string); a tie keeps the first listed;
an individual inventor counts only when no organisation is on the patent. The design's region follows the chosen assignee's country where the string prints one.
Code: `viz/frames.py: design_assignees()` used by `base()`.

**Reach.** 16 of the 1 639 patents change assignee (122 patents have co-assignees). No design changes region.

## Numbers that moved (old -> new), NUMBERS_V.md
| number | old | new |
|---|---|---|
| named companies, designs (`co_n`) / share (`co_share`) | 397 / 63 % | 399 / 64 % |
| universities and institutes (`uni_n`) | 44 | 43 |
| individual inventors (`ind_n`) | 186 | 185 |
| designs of named assignees (`org_aircraft`) | 441 (70.3 %) | 442 (70.5 %) |
| 4 largest assignees' share of named assignees' designs | 23.1 % | 23.1 % (102 of 442 vs 441) |
| assignees with exactly one design (`single_n`, share of assignees) | 130, 65 % | 131, 66 % |
| assignees with 2-4 designs | 53 | 52 |
| new assignees 2016-19 (`new_1619`) / 2020-23 (`new_2023`) | 57 / 82 | 58 / 81 |
| named assignees active 2016-19 / 2020-23 | 64 / 101 | 65 / 100 |
| first-time designs 2016-19 (`first_1619`) / 2020-23 (`first_2023`) | 98 / 120 | 99 / 117 |
| returning designs 2020-23 | 61 | 64 |
| first-time share of the named designs 2020-23 (`first_share_2023`) | 66 % | 65 % |
| chi-square p, first-time vs returning, 2016-19 (`p_1619`) | 0.017 | 0.014 |
| chi-square p, 2020-23 (`p_2023`) | 0.07 | **0.010** (flips from not significant to significant at 0.05) |
| same without Bell / Textron, 2020-23 (`p_wo_2023`) | 0.38 | 0.17 |
| Tilt Wing entrants 2016-19 (`tw_ent_1619`) / share | 7 of 57, 12 % | 8 of 58, 14 % |
| Tilt Wing entrants 2012-15 | 2 (10.5 %) | 1 (5.3 %) |
| entrants 2020-23 that are universities (`ent_uni_share_2023`) / single-design (`ent_single_share_2023`) | 18 % / 68 % | 19 % / 69 % |
| Tilt Wing successions (`tw_succ`) / assignees (`tw_firms`) | 23 / 13 | 24 / 14 |
| Tilt Wing successions that go to Tilt Propulsor (`tw_to_tr`) / to Lift + Cruise (`tw_to_slc`) | 44 % / 22 % | 42 % / 21 % |
| all successions (`succ_n`) / assignees with one (`succ_firms`) | 240 / 69 | 241 / 68 |
| assignees in CVT (largest-assignee-per-architecture table) | 67 | 66 |
| representative patents, named companies / universities / individuals | 658 / 42 / 179 | 660 / 41 / 178 |
| 2020-23 CVT among first-time designs | 15.0 % | 12.8 % |
| largest-assignee share table (`q2_largest_filers_share`) | ranks 18 to 199 reorder (Supernal, Safran, NASA, Karem move) | Bell / Textron 60, Airbus 21, Kitty Hawk 11, Shenfeng 10 unchanged |

Unchanged: the regions (every region number, the entry lag, the NA tilting share without its largest assignee), Bell / Textron's 60 designs, effective number, Parts II, III, IV.

## Cell-level list (thesis_figures_v2 CSVs)
```
q4_flown_index_firm_representativeness.csv | assignee type | largest gap: Named company (+39.3 pp) -> Named company (+39.0 pp)
q4_flown_representativeness.csv | assignee type | largest gap: Named company (+37.8 pp) -> Named company (+37.5 pp)
q2_filer_types.csv | 658 | Named company: 658 -> 660
q2_filer_types.csv | 658 | University / institute: 42 -> 41
q2_filer_types.csv | 658 | Individual inventor: 179 -> 178
q2_filer_types.csv | 397 | Named company: 397 -> 399
q2_filer_types.csv | 397 | University / institute: 44 -> 43
q2_filer_types.csv | 397 | Individual inventor: 186 -> 185
q2_filer_types.csv | 150 | Named company: 150 -> 152
q2_filer_types.csv | 150 | University / institute: 5 -> 4
q2_filer_types.csv | 150 | Individual inventor: 58 -> 57
q2_largest_filer_per_class.csv | Combined Vectored Thrust | assignees: 67 -> 66
q2_entrant_class_mix.csv | 2016-19 | aircraft: 98.0 -> 99.0
q2_entrant_class_mix.csv | 2016-19 | assignees: 57.0 -> 58.0
q2_entrant_class_mix.csv | 2016-19 | Lift + Cruise: 0.316 -> 0.323
q2_entrant_class_mix.csv | 2016-19 | Tilt Propulsor: 0.133 -> 0.131
q2_entrant_class_mix.csv | 2016-19 | CVT: 0.122 -> 0.121
q2_entrant_class_mix.csv | 2016-19 | Tilt Wing: 0.112 -> 0.111
q2_entrant_class_mix.csv | 2016-19 | Multicopter: 0.082 -> 0.081
q2_entrant_class_mix.csv | 2016-19 | other architectures: 0.235 -> 0.232
q2_entrant_class_mix.csv | 2020-23 | aircraft: 120.0 -> 117.0
q2_entrant_class_mix.csv | 2020-23 | assignees: 82.0 -> 81.0
q2_entrant_class_mix.csv | 2020-23 | Lift + Cruise: 0.342 -> 0.35
q2_entrant_class_mix.csv | 2020-23 | Tilt Propulsor: 0.217 -> 0.222
q2_entrant_class_mix.csv | 2020-23 | CVT: 0.15 -> 0.128
q2_entrant_class_mix.csv | 2020-23 | Tilt Wing: 0.092 -> 0.094
q2_entrant_class_mix.csv | 2020-23 | Multicopter: 0.067 -> 0.068
q2_entrant_class_mix.csv | 2020-23 | other architectures: 0.133 -> 0.137
q2_entrant_class_mix.csv | 2020-23 | aircraft: 61.0 -> 64.0
q2_entrant_class_mix.csv | 2020-23 | Lift + Cruise: 0.311 -> 0.297
q2_entrant_class_mix.csv | 2020-23 | Tilt Propulsor: 0.23 -> 0.219
q2_entrant_class_mix.csv | 2020-23 | CVT: 0.295 -> 0.328
q2_entrant_class_mix.csv | 2020-23 | Tilt Wing: 0.098 -> 0.094
q2_entrant_class_mix.csv | 2020-23 | other architectures: 0.066 -> 0.062
q2_entrant_class_mix.csv | 2016-19 | first-time aircraft: 98.0 -> 99.0
q2_entrant_class_mix.csv | 2016-19 | p: 0.016560733008724814 -> 0.013842461879235138
q2_entrant_class_mix.csv | 2016-19 | p without it: 0.5871527706008085 -> 0.5862107168300825
q2_entrant_class_mix.csv | 2020-23 | first-time aircraft: 120.0 -> 117.0
q2_entrant_class_mix.csv | 2020-23 | returning aircraft: 61.0 -> 64.0
q2_entrant_class_mix.csv | 2020-23 | p: 0.07008826800245227 -> 0.009886959129515285
q2_entrant_class_mix.csv | 2020-23 | p without it: 0.38036398187951415 -> 0.17476113273080032
q2_first_vs_returning_filers.csv | 2016-19 | named assignees active: 64 -> 65
q2_first_vs_returning_filers.csv | 2016-19 | new assignees: 57 -> 58
q2_first_vs_returning_filers.csv | 2020-23 | named assignees active: 101 -> 100
q2_first_vs_returning_filers.csv | 2020-23 | new assignees: 82 -> 81
q2_tilt_wing_entrants.csv | 2012-15 | entering with Tilt Wing: 2 -> 1
q2_tilt_wing_entrants.csv | 2012-15 | Tilt Wing share of entrants: 0.105 -> 0.053
q2_tilt_wing_entrants.csv | 2016-19 | assignees entering: 57 -> 58
q2_tilt_wing_entrants.csv | 2016-19 | entering with Tilt Wing: 7 -> 8
q2_tilt_wing_entrants.csv | 2016-19 | Tilt Wing share of entrants: 0.123 -> 0.138
q2_tilt_wing_entrants.csv | 2016-19 | all entrants: universities / institutes: 5 -> 4
q2_tilt_wing_entrants.csv | 2016-19 | all entrants: no other aircraft: 34 -> 35
q2_tilt_wing_entrants.csv | 2020-23 | assignees entering: 82 -> 81
q2_tilt_wing_entrants.csv | 2020-23 | Tilt Wing share of entrants: 0.11 -> 0.111
```
