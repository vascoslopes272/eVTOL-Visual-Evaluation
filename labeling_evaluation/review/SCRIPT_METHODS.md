# The rule-based scripts, in plain words

Written for: the author, to adapt into the thesis methods. No model is used by any script below; each one reads text that is already on disk and applies fixed keyword rules. Code: `notebooks/_build/yearscript/` (`year_rule.py`, `trl_rule.py`, `ari_rule.py`) and `viz/frames.py` (`directory_frame`, domain flag). Scored in `notebooks/60_review_scripts_vs_author.ipynb`.

## Where the text comes from
The public evtol.news aircraft pages (non-member view, crawled 17 September 2026). A first script splits every page into sentences and keeps the sentences that contain a year (14 148 of them), each with a fixed id and a flag for "this sentence is a Resources / source-list entry". The patent side is not used by these scripts.

## 1. Domain flag (is this directory page in the thesis domain?)
Reads the page's specification lines (Power source, Capacity, Aircraft type, Piloting) and the page text. A page is OUT when:
- its power source has a combustion element (hybrid, fuel cell, turbine, engine, gas, hydrogen) and **no electric alternative**. "Hybrid-electric" does not count as an electric alternative; "batteries or hybrid-electric" does;
- it is a cargo / unmanned aircraft: capacity says "cargo only", status is "cargo drone", or the aircraft type or name says cargo / drone / delivery / spray / ... and no person (passenger, pilot, seat) is named in capacity, type or piloting;
- except that a "no passengers" demonstrator stays IN when the page says the aircraft is built for people (passenger, air taxi, seat, cabin, optionally piloted), and a page saying it can be crewed stays IN.
The author's individual rulings (`review/domain_overrides.csv`) override these rules.

## 2. Development year
For each page, take the dated sentences and:
1. **drop** company-history sentences (founded, incorporated, established, headquarters ...), future statements (will, plans to, expected ...), "as of / no information / has not been released" statements, and years after 2026;
2. **keep** every Resources entry (its year = the publication year of the source), and every text sentence that contains an **event word** (announced, unveiled, revealed, first flight, flew, test flight, built, prototype, began, started, completed, demonstrated, launched, patent filed ...) **and** names the aircraft's model or says "the aircraft / prototype / demonstrator / vehicle";
3. the year is the **earliest** year among the kept sentences. No kept sentence = no year.
Same definition as the thesis: the earliest year the page documents for the aircraft. The rule was built on the pages the author did not review, then scored once on the author's sample.

## 3. TRL
Reads the quoted evidence sentence(s) of each design and applies the first rule that matches:
- certification granted -> TRL 8
- piloted / crewed flight (and not "unmanned") -> TRL 7
- any flight, hover or test campaign of a sub-scale or scaled model -> TRL 5
- any other flight (full-scale, prototype, demonstrator, unmanned, tethered, or no scale given) -> TRL 6
- wind tunnel, simulation, bench or ground tests only -> TRL 4
- nothing above (concept, plan, announcement) -> TRL 2
Designs with no page evidence (patent only) are TRL 2 by rule, as before.

## 4. AAM Reality Index company map
Lower-cases both names, drops legal and generic words (aviation, aerospace, technologies, group, inc ...), and accepts a patent-dataset company whose remaining words are identical or whose first word is identical. No match = blank (not in the dataset).

## How good are they (against the author's review)
| input | script | the earlier reading step (LLM) |
|---|---|---|
| domain, deleted pages really out | 89.7 % (82.1-94.3), rules as at review time | n/a (rules only) |
| domain, kept pages really in | 76.1 % (66.7-83.6), rules as at review time | n/a |
| development year | exact 60.5 % (50.0-70.1); within 1 year 75.3 % (65.3-83.2) | 93.3 % (86.5-96.8) |
| TRL | exact 68 % (58-77); within 1 level 84 % (75-90) | 100 % (96-100) |
| company map (43 rows) | 81.4 % | 88.4 % |

The scripts are **not equal** to the reading step: they are the same task done with fixed keywords, and they agree with the author less often. Say so in the thesis; do not call them equivalent.

## Files written by running the scripts on everything
`review/decisions/SCRIPT_YEAR_ALL.csv` (a year and its sentence for 1 094 of 1 229 pages), `SCRIPT_TRL_ALL.csv`.
