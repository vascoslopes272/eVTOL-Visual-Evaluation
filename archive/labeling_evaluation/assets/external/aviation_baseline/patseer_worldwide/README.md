# Worldwide patenting baselines (user export, 2026-09-25) — the PRIMARY baseline since that date

| file | what | unit | read as |
|---|---|---|---|
| `patseer_B64_worldwide_by_priority_year.csv` | PatSeer `CPC:(B64*)`, no country filter | simple families by earliest priority year, 2000-2026 | `la_baseline.PATSEER_WORLD` (= `PRIMARY`) |
| `patseer_sectionB_worldwide_by_priority_year.csv` | PatSeer, all CPC section-B classes | same | `la_baseline.PATSEER_WORLD_B` |
| `baselines_2000_2023.csv` (`world` column) | WIPO IP Statistics, indicator 6a, patent families by origin, all origins | families, 2000-2023 | `la_baseline.WIPO_WORLD_ALL` |

`README_user_export.md` is the user's own note with the exact queries; the WIPO saved search
is in the source zip `1639_LABELLED/baselines_patenting_2.zip`.

## Why these replaced the nine-office PATENTSCOPE series (2026-09-25)

1. **Same unit and same database as the corpus.** The corpus is 1 639 PatSeer simple
   families; these are PatSeer simple families. PATENTSCOPE counted publications.
2. **The PATENTSCOPE series undercounts recent years.** Its own worldwide B64 count falls
   from 13 344 (2018) to 8 533 (2023) while PatSeer's worldwide family count holds at
   ~14 000-15 500 — in years already past the publication lag, so the fall is the database,
   not the filings (most likely CPC not yet assigned to recent documents). A shrinking
   denominator inflated every eVTOL ratio: Figure 1 (ii) read ×3.3 against aeronautics in
   2018 on that series and reads ×1.6 on this one.

The nine-office PATENTSCOPE columns stay in `../b64_by_priority_year.csv` and are printed as
a comparison row of `la_doubling_time`, so the effect of the choice stays visible.

Caveat that travels with these series: China holds 65 % of world patent families in 2018 and
72 % in 2023 (WIPO), far above its share of this corpus, so the "all patents" line in
particular is a China-weighted denominator.
