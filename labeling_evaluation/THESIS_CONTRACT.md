# Thesis layer contract (notebooks 46 and 47) — read before touching viz/thesis_q*.py

Goal. The thesis chapter 4 "Analysis" follows the author's index (seven questions, Q1–Q7). Notebook 46 draws **one
file per graph** (never two graphs (i)/(ii) in one figure) into folders per question and slot; notebook 47 writes the
LaTeX document (Methodology → Results and discussion → Appendix → Limitations) and compiles it to PDF with tectonic.
Numbers in the text are **never typed**: they are `{placeholders}` resolved from `numbers(ctx)`.

## 1. Files per question (N = 1…7)

`viz/thesis_qN.py`
```python
from viz import thesis            # ctx fields: cfg ds v WIN WIN_NAMES COMPLETE W HALF WSHORT SEED thin pct pval np
ITEMS = [dict(name="q1_filings_per_year", slot="results", kind="figure", sub="A",
              title="Unique aircraft per priority year", caption="…≤ 2 lines…",
              source_item="Figure 1 (i)", flag=None, flag_note="", builder=fig_filings_per_year,
              source="labelled dataset, 627 unique aircraft", unit="unique aircraft", read=""), …]
def numbers(ctx) -> dict[str, str]: …     # every number the text quotes, AS PRINTED ('1 639', '53 %', '0.031', '< 0.001')
```
Builders: `def fig_x(ctx) -> (matplotlib Figure, DataFrame | None)` or `def tab_x(ctx) -> (DataFrame, None)`.
Reuse `viz.frames` and `viz.plots` exactly as notebooks 40–44 do (read the cell in `notebooks/_build/build_4N.py`
that draws the source figure and keep only the panel asked for; keep its style calls: `style.cls`, `plots.few_band`,
`plots.end_labels`, percent formatters, grid). Width: `ctx.W` (text width) or `ctx.HALF`; one axes per figure
(small multiples of ONE variable, e.g. the three class panels of Figure 13 (ii), stay one figure). Do not call
`style.mark(ax, '(i)')` — there are no panel marks any more. Use `constrained_layout=True`. Port the number
computations from the same build_4N cells (they live in notebook cells, not modules); add helpers to the module.

`viz/thesis_text_qN.py`
```python
METHOD = """≤ 250 words of prose: Objective · Data and unit · Procedure · Grounds (test names) · Limits, as 1–2 sentences each."""
RESULTS = [dict(sub="A", title="Growth of the field",            # the index's sub-question titles, in order
               text="""Results then discussion for this sub-question: 3–6 sentences, cites [fig:q1_filings_per_year] …""")]
ANSWER = """The question's answer in 3–5 sentences, specific claims (with {placeholders}), no slogans."""
APPENDIX = {"q1_growth_rates_table": "one line: the finding this appendix item carries, with its number."}
```
Markup inside text: `{key}` number · `[fig:name]` / `[tab:name]` → Figure/Table reference (the item is placed
after the paragraph that first cites it) · `[hl]…[/hl]` → yellow highlight for the author (use with flags) ·
`**bold**` allowed, sparingly · paragraphs separated by a blank line. Plain unicode (≤ · ² ρ χ −) is fine.
Every `results` item must be cited in RESULTS; every `appendix` item needs an APPENDIX line (one short takeaway).
Main text lives ONLY in Methodology / Results; the Appendix prints items + caption + the one takeaway line.

## 2. Writing rules (the author's)
- Less dense than the 45-page document: only what answers the sub-question; no Source/Unit/How-to-read in prose
  (they go to the item's `source`/`unit`/`read` fields); never explain the same idea twice; no "cohort"; no I/we/you.
- At most two numbers per sentence; a comparison with more numbers becomes a table or two sentences.
- Questions are neutral titles; results stated as claims with their number; discussion = what it rests on, one or two sentences.
- Voice and layout, THE authority: read `/mnt/storage_11tb/Drive_files_to_syncronize/thesis-review-human/thesis-review-human/references/his-writing.md`
  (the author's habits: definition then plain words, the case not the abstraction, decisions stated with their reason, uneven
  rhythm; no additive openers, no "it is important", no triads, no closing summaries, no register words, no em dashes, no
  explanatory colons, no adjectives on the thesis) and `.../references/layout.md` (paragraphs of 3–6 sentences, first
  sentence names the job, lists for 3+ parallel items, tables for two axes, map sentence + hand-over per subsection).
  Also `/home/vasco/.claude/skills/synced/*/thesis-voice/SKILL.md`. British English. Results paragraphs: short, flat, the number carries it.
- Flags (yellow in the document): `decide` = author decides (e.g. main text or appendix), `verify` = author
  re-verifies these values (Q4 Tables 4/5 and the evtol.news class mapping), `drop` = kept in the appendix but
  proposed to be dropped. Put the same note in `flag_note` and wrap the sentence that depends on it in `[hl]…[/hl]`.

## 3. Items per question (from the index image; "Fig n" = the 45-page document's numbering, built by build_4N.py)

**Q1 growth (build_40 §1.1, §1.2; build_44 Fig 23)** — A Growth of the field: results `q1_filings_per_year` (Fig 1 i),
`q1_growth_rates` (Fig 1 ii, log axis, each series ÷ its 2005-09 mean); appendix `q1_growth_rates_table`
(table: doubling times vs baselines, from la_growth_rates/la_growth_ratios). B Entry by region: text only, citing
Q3's `q3_region_entry_lag`; appendix `q1_na_drop_is_real` (Fig 23 i: aircraft per priority year and region with the
publication-lag reading), `q1_in_force_status` (Fig 4). Numbers: growth rates, doubling times, turning point, NA share drop, out-of-force shares.

**Q2 filers (build_43 §4.1, §4.2)** — A Who files: results `q2_largest_filers_share` (Fig 16 i), `q2_filer_types`
(Fig 16 ii). B Does anyone control it: results `q2_largest_filer_per_class` (kind=table, from Fig 17 (i) data:
class, largest filer, share all years, highest share in one window, effective filers) — text may be enough,
flag=decide; appendix `q2_first_vs_returning_filers` (Fig 16 iii), `q2_entrant_class_mix` (Fig 19 i),
`q2_tilt_wing_entrants` (Fig 19 ii). Numbers: named-company share, firm counts, largest-filer shares, leverage (Bell/Textron ≤ 2.6 pp), entrants test p.

**Q3 regions (build_44 §5.1, §5.2; build_43 Fig 20)** — A What each region files: results `q3_region_design_all_years`
(Fig 22, the "all years together" panel only: class / propulsor units / tilting per region). B When each region
enters: results `q3_region_entry_lag` (Fig 23 ii: order of entry by class and lag per region). Appendix:
`q3_region_mix_by_window` (Fig 22's per-window panels; the index wrote "Figure 21" here — flag=decide, note it),
`q3_region_countries` (Fig 21 applicant countries, flag=decide), `q3_firm_successions` (Fig 20 within-firm
persistence vs switching). Numbers: regional shares, NA CVT trend, unit-band test p, lags per class.

**Q4 representativeness (build_40 §1.3 and Fig 2, Fig 3, Fig 5b)** — A Is the coding right: results
`q4_coding_agreement` (Table 2, three sources two at a time, agreement with 95 % CI). B Is the mix representative:
results `q4_class_mix_dataset` (Fig 2 i) and `q4_class_mix_directory` (Fig 2 ii) as two single graphs with the SAME
y-axis and class order; `q4_patent_vs_market_clock` (Fig 3, flag=decide "main text or appendix");
`q4_trl_representativeness` (Table 4) and `q4_index_firm_representativeness` (Table 5), both flag=verify
("author re-verifies these values and the evtol.news class mapping"). Appendix: `q4_dataset_vs_directory_classes`
(Fig 5b i), `q4_dataset_vs_directory_subsets` (Fig 5b ii), `q4_trl_by_class` (Table 3, flag=drop),
`q4_name_coverage` (Fig 5, flag=drop). Numbers: agreements, chi² p, residuals, subgroup test p's.

**Q5 money (build_43 Fig 18 + §4.1 ARI; build_40 Table 1 + external investment)** — A Timing: text only (first
filing → first flight lag, corrected for publication lag; numbers from Table 1 / ari timeline); appendix
`q5_ari_timeline` (Table 1, flag=decide). B Funding vs filing and output: results `q5_funding_vs_aircraft`
(the Fig 18 panel carrying ρ: funding against aircraft filed, Spearman); appendix `q5_patent_lead_to_flight`
(the other Fig 18 panel; flag=verify "check caption/image: the document showed no caption or image for it").
C Concentration of funding: text only (Joby + Beta share of disclosed funding vs share of aircraft); appendix
`q5_patenting_vs_investment` (new: patents/aircraft per period against disclosed sector investment per period,
`sector_funding` input; flag=decide); the VFS / McKinsey comparison is one sentence, no figure. Numbers: ρ and p (n 9), lags, funding shares.

**Q6 design space (build_41 §2.1–2.3; build_42 §3.1, §3.3, §3.4)** — A The design space: results `q6_selected_fields`
(Table 6) and `q6_propulsor_units_per_class` (Fig 6 i) — flag=decide on which of the two stays in the main text;
`q6_archetype_core` (Fig 8 i), `q6_archetype_windows` (Fig 8 ii), `q6_discovery_curve` (Fig 9). Appendix
`q6_arrangement_by_class` (Fig 6 ii), `q6_ducting_by_units` (Fig 6 iii), `q6_archetype_filers` (Fig 7, note
"redundant with Fig 8"). B Between classes: results `q6_class_shares_by_window` (Fig 10 i), `q6_largest_classes_over_time`
(Fig 10 ii). C Inside each class: results `q6_leading_layout_by_class` (Fig 13 ii, the three class panels = one
figure); appendix `q6_leading_configuration_share` (Fig 13 i). D Across classes: text reads Fig 13 (ii) across
classes and hands over to Q7 in one line; appendix `q6_class_centres_tilting_units` (Fig 14 i), `q6_tp_units_by_tilting_sets`
(Fig 14 ii), `q6_cvt_units_on_booms` (Fig 14 iii), `q6_cvt_ducted_by_boom_layout` (Fig 14 iv), `q6_boom_share_by_class`
(Fig 15 i), `q6_ducted_share_by_class` (Fig 15 ii), `q6_driver_verdicts` (Table 9). Numbers: fields that vary, archetype counts, core share, class shares, leading-layout shares, trace trends.

**Q7 dominant design (build_42 §3.2; build_44 §5.3; build_43 funding)** — A Defining the candidates: results
`q7_archetype_sets` (Table 7). B The test: results `q7_condition1_family` (Fig 11), `q7_condition2_balance` (Fig 12 i),
`q7_condition3_cohesion` (Fig 12 ii); appendix `q7_verdict_table` (Table 8). C Robustness: text only (in force vs
all aircraft, subsystem weighting; numbers from Table 8). D By region: results `q7_region_family_share` (Fig 24 i);
appendix `q7_region_lean_without_largest_filer` (Fig 24 ii), `q7_region_firm_proximity` (Fig 24 iii); the
funding-weighted F share among index firms = one sentence with its number. Also appendix `q7_cannot_answer`
(Table 10, sub="", flag=drop, note "limitations table") — printed in the Limitations chapter.

**Common (no question)** — `viz/thesis_common.py` with `numbers(ctx)` and `viz/thesis_text_common.py` with
`METHOD_COMMON` (the dataset in ≤ 120 words: 1 639 patents → 627 unique aircraft, the unit of analysis, priority-year windows,
publication lag, class labels = the author's wizard labels; from the 45-page document's "Method common to every chapter"),
`STATS` = list of dicts (test, answers, formula_unicode, used_in) for the one statistics table (Wilson, Fisher/chi², Spearman,
permutation band, Gower cohesion, log-linear doubling time, Chao1/Hill), `LIMITATIONS` (≤ 300 words from the closing section
"What this labelled dataset will never tell you", as prose + one short list), and `CHAPTER_MAP` (3 sentences opening chapter 4:
the three parts and seven questions). Same markup and placeholder rules.

## 4. Check before handing over
`python3 -m viz.thesis_run QN` must end with `0 text problems`; open every PNG written under
`<output>/thesis_figures/QN_*/` and look at it: one graph, legible at the printed width (≥ 7 pt), nothing clipped,
legend inside or right, class colours/markers from `style.cls`. Do not edit notebooks 40–44, viz/frames.py or
viz/plots.py except to ADD a function (never change existing behaviour: 117 tests must still pass: `python3 -m pytest -q tests/`).

## 5. Methodology v2 (author's ruling 2026-10-07) — the Methodology is topics + flowcharts, not prose

- `METHOD` of each `viz/thesis_text_qN.py` becomes ONE itemised block (lines starting with `- `), five lines, ≤ 18 words each:
  `- **Objective:** …` `- **Data and unit:** …` `- **Procedure:** …` `- **Test:** …` `- **Limit:** …`
  (placeholders and [fig:]/[tab:] allowed; nothing that the Results repeat). No prose paragraph before or after.
- Each question gets ONE flowchart item in ITEMS: `slot="method"`, `kind="figure"`, name `qN_method_flow`, sub="",
  built with `viz.flow.chart(ctx.cfg, nodes, edges)` (kinds: data / step / test / figure / answer; ≤ 7 boxes, ≤ 4 words
  per line, 2 lines max per box; columns = the order data → subset/transform → test → figures → answer). Caption: "How
  QN is answered." The figure boxes name the thesis figures by their item title, not by the old document numbers.
- `viz/thesis_common.py` gets `METHOD_ITEMS` (same item dicts, names `common_chapter_flow` and, if useful,
  `common_data_flow`) drawn with `viz.flow.chart`: ground files → 1 639 patents → wizard labels → 627 unique aircraft →
  the three parts / seven questions → figures and tables → Answer boxes; notebook 46 saves them to `thesis_figures/common/`.
- `METHOD_COMMON` becomes an itemised block (≤ 8 lines: patents, aircraft, unit, labels, windows, lag, regions, classes)
  and `CHAPTER_MAP` states the organisation (parts → questions → sub-questions → Answer box → appendix) in ≤ 5 lines.
- `STATS` stays (the one table). `LIMITATIONS` stays but as ≤ 6 itemised lines.
