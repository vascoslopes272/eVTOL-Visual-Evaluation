# Patenting baselines (collected 2026-09-25)

## raw/
- patseer_B64_worldwide_by_priority_year.csv — PatSeer, query `CPC:(B64*)`, no country filter, families by Earliest Priority Year, 2000–2026
- patseer_sectionB_worldwide_by_priority_year.csv — PatSeer, query `CPC:(B01* OR ... OR B99*)` (all CPC section B classes), same settings
- wipo_6a_patent_family_by_origin_2000_2024.csv — WIPO IP Statistics Data Center, indicator 6a "Patent family by origin", total count by applicant's origin, all origins (data updated May 2026)
- wipo_saved_search.json — WIPO saved search parameters (to reproduce the export)

## processed/baselines_2000_2023.csv
Columns: y (year) | world (WIPO, sum of all origins) | CN (China origin) | exCN (world minus China) | b64 | B | CNshare% | b64_per10k (B64 per 10k world families) | B_share% (section B as % of world)

## Notes
- Use windows ending 2023 at the latest; 2024–2026 are incomplete (publication lag).
- PatSeer series (B64 and B) jump in 2015–2016 (+66%, +59%); WIPO world shows only +13%. Treat the jump as a database coverage effect (likely Chinese utility models, which WIPO's patent family indicator excludes).
- WIPO unit = families by applicant origin and first filing year; PatSeer unit = families by earliest priority year. Use WIPO as context only.
- Doubling times (log-linear fit, 2000–2023): B64 5.5 yr, section B 7.8 yr, WIPO world 12.3 yr; world excluding China is flat/declining.

## seven_year_check/
Check of the seven-years-from-priority rule on the eVTOL corpus (1,639 simple families, PatSeer export 8 Jun 2026).
Run `python seven_year_check.py` → status_by_priority_year.csv, grant_lag_summary.csv.
- Pending share (ACTIVE - APPLIED) is <=5% for every cohort aged >=6 years (priority <=2020); 10% at 5 y, 24% at 4 y, 57% at 3 y.
- Priority-to-first-grant lag (781 granted families with a dated grant event): median 3.1 y, 90th percentile 5.3 y; 97.7% granted within 7 y.
- Conclusion: seven years from priority is a conservative cut-off; status is effectively settled by 6 years.
