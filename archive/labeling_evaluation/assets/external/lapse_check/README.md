# The seven-year rule, checked on the corpus itself (user, 2026-09-25)

`seven_year_check.py` run by the user on the full PatSeer record export (1 639 simple
families, snapshot 8 Jun 2026); outputs copied verbatim from
`1639_LABELLED/baselines_patenting_2.zip`.

- `grant_lag_summary.csv` — priority-to-grant lag of the 781 dated grants: median 3.06 y,
  p90 5.28 y, **97.7 % of eventual grants arrive within 7 years of priority**.
- `status_by_priority_year.csv` — per cohort: dead / granted / pending. Pending share:
  2019 cohort 4.0 %, 2021 10 %, 2022 23.8 %, 2023 56.5 %.

This is the empirical confirmation of the ≤2019 lapse-cohort rule the brief states in 1.2
(read into `la_lapse_check` by `sm_open.lapse_check`).
