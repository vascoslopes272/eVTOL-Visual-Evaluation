# Aviation patenting baseline — all B64 patents per priority year

Why this exists: Figure 2.1.1 counts eVTOL filings per priority year. A raw count cannot say
whether the sector became more active, because patenting rose in general over the same period —
if aeronautics patenting doubled, eVTOL filings would double with it and the graph would look
the same. This file is the denominator that turns the count into a share (user, 2026-09-22).

- Source: **WIPO PATENTSCOPE**, https://patentscope.wipo.int/search/en/search.jsf
- Fetched: **2026-09-22**
- Rebuilt by: `scripts/fetch_aviation_baseline.py` (caches every answer, so a re-run is free)
- Read by: `src/dataset_facts/la_baseline.py`; the document reads `cpc_offices`

## What is counted

`b64_by_priority_year.csv` has one row per year 1999–2026 and four columns, each the number of
patent publications PATENTSCOPE returns for that query:

| column | PATENTSCOPE query |
|---|---|
| `cpc_world`   | `CPC:B64* AND PD:<year>` |
| `ipc_world`   | `IC:B64* AND PD:<year>` |
| `cpc_offices` | `CPC:B64* AND PD:<year> AND OF:(US OR CN OR DE OR WO OR EP OR KR OR FR OR GB OR IT)` |
| `ipc_offices` | `IC:B64* AND PD:<year> AND OF:(US OR CN OR DE OR WO OR EP OR KR OR FR OR GB OR IT)` |

- **B64** is the classification for *aircraft, aviation, cosmonautics*: `B64*` is the whole
  subclass tree (B64B airships, B64C aeroplanes, B64D equipment, B64F ground installations,
  B64G cosmonautics, B64U unmanned aerial vehicles). The truncation is used because a bare
  `B64` matches only documents classified at class level, which is a small minority.
- **`PD` is the priority date**, so the baseline is counted on the same clock as the corpus.
  This was verified before use, not assumed: for 2024, `PD` returns 5 971 and the publication
  field `DP` returns 24 294 — the collapse at the recent edge is the publication-lag signature
  a priority-date field must show, and a publication-date field must not.
- **`OF` is the publication office.** The nine offices are those of the corpus itself
  (Labelling Analysis Table A.1, provenance by office: US, CN, DE, WO, EP, KR, FR, GB, IT).

## What this is *not*

1. **It counts publications, not aircraft and not families.** The corpus counts *unique
   aircraft*; the baseline counts *patent documents*. The document therefore normalises the
   corpus's own patent count (all 1 639 acquired patents by priority year) against it, which is
   like-for-like, and prints the aircraft ratio beside it as a mixed-unit reading only.
2. **The recent years are incomplete on both sides.** A patent enters PATENTSCOPE only when it
   publishes, so priority years inside the publication lag are truncated in the baseline exactly
   as they are in the corpus. The truncation partly cancels in the ratio, but only as far as
   eVTOL and aviation share a lag distribution, which is not established here. Years inside the
   90th-percentile lag (3 years) stay marked incomplete and the ratio is not read there.
3. **Coverage is PATENTSCOPE's, not the world's.** PATENTSCOPE indexes the PCT collection and
   ~75 national collections; it is not every patent office on earth, and classification coverage
   differs between collections — several national collections carry IPC where they do not carry
   CPC. That is why both readings are stored: if the answer is the same under CPC and under IPC,
   the classification system is not driving it.
4. **It is not the same database as the corpus.** The corpus is a PatSeer export; the baseline is
   PATENTSCOPE. The two agree on what a publication office is, but not necessarily on what is
   indexed. See "If you want to replace this" below.
5. **B64 includes B64G, cosmonautics.** Spacecraft are inside the user's stated definition
   ("all aeronautics patents, CPC B64") and are left in; they are a small and slowly-growing part
   of B64 and excluding them moves the growth multiple by less than the CPC/IPC choice does.

## If you want to replace this with a PatSeer series

PatSeer is the corpus's own source, so a PatSeer baseline removes limitation 4 and matches the
corpus's indexing exactly. To swap it in, produce a CSV with the same shape — a `year` column and
at least one count column — drop it in beside this file, and point `la_baseline.PRIMARY` at the
column. The query and the fields needed are written up in the handover note that came with this
folder; in short: `CPC:(B64*)` (or `IPC:(B64*)`), priority years 1999–2026, publication offices
US, CN, DE, WO, EP, KR, FR, GB, IT, aggregated as a count of publications per priority year.
