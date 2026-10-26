# How the evtol.news and index inputs were checked (2026-10-11)

Written for: the author, to adapt into the thesis methods. Every statement below is checked against the files named.

## 1. What was checked and why

Four inputs of the Part I (Evidence base) figures were proposed by a reading step over the public evtol.news page text (or the AAM Reality Index tables), not typed by the author. The author checked them on review pages and the results below decide whether each may be used.

| input | what it feeds | how it was proposed | checked |
|---|---|---|---|
| domain flag of the evtol.news pages (in / out of the thesis domain) | class-mix and dataset-vs-directory figures (I4) | **fixed rules written as a script** (`viz/frames.py`, `directory_frame`) applied to the spec sheet and page text | random sample of the exclusions + all 10 patent-linked exclusions |
| development year per aircraft | `q4_patent_vs_market_clock`, directory age | a reading step over the page text, one sentence + a kind of date per aircraft | random sample, 90 of 1 229 |
| technology readiness level (TRL) | `q4_trl_representativeness` | a reading step; 105 rows rest on a quoted sentence | random sample, 51 of 105 |
| AAM Reality Index company -> patent-dataset company map | `q4_index_firm_representativeness`, `q5_ari_timeline` | a reading step over the index tables | all 43 rows (census) |

Only the domain flag is rule-and-script based. The year, TRL and company map were **not** produced by a script of fixed rules, so they must not be described as script-only.

## 2. Sample sizes and the interval

Sample size for a proportion with a finite population: n0 = z^2 p (1 - p) / e^2 with z = 1.96, p = 0.5, e = 10 % (n0 = 96), then n = n0 N / (n0 + N - 1). Random draw with seed 42 (`notebooks/_build/prepare_review_pages.py`). The result is the Wilson interval with the finite-population correction (`lib/intervals.wilson_fpc_interval`). A source is accepted when the **lower** bound of the 95 % interval is at or above the threshold (default 90 %).

**Acceptance bar (author's ruling, 2026-10-25).** The dissertation's bar for the rule-based scripts is **70 % on the point estimate**. It is the author's own ruling; it was not in the code or in these notes before today. The 90 % lower-bound rule above stays as the stricter reading and is reported beside it. The domain flag at review time: excluded side 89.7 % and kept side 76.1 % pass 70 % on the point estimate; on the lower bound the kept side (66.7 %) does not pass 70 %, and neither side passes 90 %.

**Domain figures, first script version (11 October sample).** Excluded 61/68 = 89.7 % (82.1-94.3 %, pool 223); kept 67/88 = 76.1 % (66.7-83.6 %, pool 1 040); both together 128/156 = 82.1 % raw, 78.5 % (71.4-85.7 %) weighted by pool size, pool 1 263. The script was corrected afterwards to follow the Section 3.1.1 rules (the rules themselves did not change); the corrected script has no independent sample (59/68 and 77/88 on the same pages, in-sample, no interval). Table note: "128/156 raw; 78.5 % weights each side by its pool".

## 3. Rules used for the domain flag (directory side only; the patent dataset's own gate is unchanged)

1. A power source that offers an electric version counts as electric; only a source with no electric option (fuel cell, turbine, hydrogen, hybrid only) is out.
2. Only unmanned pages are UAVs; autonomous or remote-controlled pages count as piloted.
3. Capacity "cargo only", status "cargo drone", or cargo / drone / delivery / spray ... in the aircraft type or name, with no person named in the capacity, type or piloting field, is out.
4. A page whose own text (not the Resources list) says the aircraft can be crewed or optionally piloted is in.
5. A "no passengers" or uncrewed demonstrator is in when the page says the aircraft (or its maker's line) is built for people (passengers, air taxi, seats, cabin, optionally piloted).
6. The author's individual rulings on the review page are kept as an explicit file (`review/domain_overrides.csv`, 11 pages) and override the rules.

## 4. Results

| input | agree | n | pool | 95 % interval | lower bound >= 90 % |
|---|---|---|---|---|---|
| TRL | 50 | 50 (1 unsure not counted) | 105 | 96.1 - 100 % | yes |
| year (kept as proposed) | 84 | 90 | 1 229 | 86.5 - 96.8 % | **no** |
| domain exclusions, at review time | 61 | 68 | 223 | 82.1 - 94.3 % | **no** |
| company map | 22 of 26 answered so far | 43 rows | 43 | census, not complete | pending |

Corrections the author made were applied: 6 year corrections (`review/year_overrides.csv`), 11 domain rulings. Rules 3 and 5 above were written or tightened after the review found the errors, so the domain interval above describes the rules **as they stood**; a fresh sample is needed to state a figure for the current rules.

## 5. Limits to state

- The evtol.news text is the public, non-member view (1 138 of 1 229 pages end with "VFS Member? Log in to read more!").
- A year is an upper bound of when an aircraft existed ("existed by" = a prototype existed, even if sub-scale). Of the 90 sampled years, 50 are only a publication date or an "existed by" bound; 8 are a first flight, 10 a development start and 15 an announcement.
- The patent priority year is likewise not the first appearance; the two clocks are compared as bounds.

## 6. Wording for the thesis (accurate options)

- Domain flag: "The domain of the directory pages was set by fixed text rules applied by script to each page's specification sheet and description (Table X); rules were refined once on a first author review, and the author's individual rulings override them."
- Year, TRL, company map: "Values were proposed by a reading step over the public page text and checked by the author on a random sample sized for a 95 % interval (z = 1.96, e = 10 %); a source is used when the lower bound of the interval is at least 90 %."
