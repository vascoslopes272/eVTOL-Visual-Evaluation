# Inputs of the thesis notebooks — what the author reviewed, what is still open (2026-10-07)

Scope: every file listed under `inputs:` in `labelling_analysis.yaml`, traced to the thesis items
(`viz/thesis_q1..q7.py`) that use it. Slot = results / appendix as the items declare it.

## A. Made or reviewed by the author — nothing to do

| Input | Made by | Used by |
|---|---|---|
| aircraft_table.csv, figure_table.csv, data_dictionary.csv | author's labels + review pages, joined by notebook 04 (build 2026-10-01 16:38, 627 aircraft) | everything |
| aircraft_identity_ALL.xlsx (dates, office, assignee, country, legal status, canonical firm) | PatSeer export + identity build; name / electric / take-off / UAV reviewed by the author | every per-patent fact; `industry_primary` (SBERT) is loaded but no item uses it |
| patent_links.csv | author, on proposals | Q4 linked aircraft, Fig 5b (ii), TRL evidence |
| aircraft.csv (evtol.news directory, 1 229 pages) | script crawl 2026-09-17 | Fig 2 (ii), Fig 5b |
| aviation baseline (PatSeer B64 / section B / world) | PatSeer exports | Q1 growth ratios (Fig 1 ii, growth table) |
| status_by_priority_year.csv | author's script on the PatSeer export | Q7 numbers |
| 627 aircraft, Unknown powertrain kept | author 2026-10-07: reviewed, they are electric | the funnel |

## B. The three the author will review (flag = verify in the thesis contract)

| Item | Slot | Input behind it | What to check |
|---|---|---|---|
| Table 4 `q4_trl_representativeness` | results | `inputs/trl/aircraft_trl_evidence.csv` — 105 TRL rulings by Claude (77 high, 28 medium), quote + link each | the 105 rulings (28 medium first); 693 others are TRL 2 "patent only" by rule |
| Table 5 `q4_index_firm_representativeness` | results | `ari_company_map.csv` (43 OEM → firm rows, hand-made by Claude) + the ARI CSVs | the 43 mappings (one marked "check": Volant Aerotech → Wollant Aviation) |
| Fig 18 (ii) `q5_patent_lead_to_flight` | appendix | ARI first-flight / EIS dates (`ari_may2026.csv`) | the dates of the 24 OEMs against the site |

## C. Unreviewed inputs that reach a RESULTS item and carry no flag — necessary

| Input | Made by | Reaches | Size of the review |
|---|---|---|---|
| `assets/external/sector_events/sector_events.csv` | Claude, 2026-09-23, "first pass, meant to be edited" | **Fig 1 (i)** results: the dotted event lines | 14 rows, each with a source URL |
| `EVTOLNEWS_DS/0_source/years/aircraft_dev_year.csv` | Claude, two LLM readers (1 000 agreed, 63 conflict, 166 not stated), rule `year_rule` | **Fig 2 (ii)** results (directory class mix per window), Fig 5b | the 63 conflicts + a sample of the agreed; page `years/dev_year_review.html` exists |
| `ari_company_map.csv` | Claude | **Fig 18 (i)** results, Fig 3 (decide), Table 1, Fig 17 (i) (decide), Q7 numbers | same 43 rows as Table 5 — one review covers all |
| `ari_may2026.csv`, `ari_history.csv`, `ari_funding_may2026.csv` | transcribed from the Infogram embeds on 2026-09-22; no fetch script | Fig 18 (i), Fig 3, Table 1, Table 5 | spot-check 24 OEM rows against aamrealityindex.com |
| `aircraft_trl_evidence.csv` | Claude | also **Q7 number** `trl_above` (aircraft above TRL 2) and Table 3 (drop) | covered by the Table 4 review |

## D. Unreviewed, appendix only, author decides whether to keep

| Input | Made by | Reaches |
|---|---|---|
| `assets/external/investment/aam_funding_by_period.csv` (4 rows) | Claude from publisher pages, 2026-09-27 | `q5_patenting_vs_investment` (new figure, flag decide) — if kept, check the 4 rows |

## E. Listed in the yaml but used by no thesis item — no review needed

`market_forecasts` (evtol_market_forecasts.csv), `grant_lag` (grant_lag_summary.csv), `baseline_wipo`
(b64_by_priority_year.csv; the PatSeer baselines are used instead), `codebook_dimensions`, and the SBERT
`industry_primary` column. They can be dropped from the yaml or marked `unused`.

## Items flagged decide / drop (author's choice, not a data review)

decide: Fig 17 (i), Fig 22 (i–iii) per window, Fig 21, Fig 3, Table 1, new funding figure, Table 6, Fig 6 (i).
drop: Table 3, Fig 5, Fig 7, Table 10.
