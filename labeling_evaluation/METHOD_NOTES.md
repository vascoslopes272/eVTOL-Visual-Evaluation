# Method notes — what the port of the equations found (2026-10-01)

The equations of the 45-page document are now in `lib/`. Each one reproduces the document exactly; 82 tests prove it
(`python3 -m pytest -q tests/`). While porting, the following were found in the ORIGINAL method. Nothing was changed:
the lib reproduces the document as it was. Each line needs your decision: **keep** (and state it in the method), or
**change** (the number in the thesis then moves).

## Could change a result

| # | Where | What | Effect |
|---|---|---|---|
| 1 | Dominant design, condition 3 (cohesion Q) | Q is the mean distance over all pairs of a window **including each aircraft with itself** (distance 0) | Q is too low by about 1/n; more in small windows. The fix is to leave the diagonal out |
| 2 | Gower distance, subsystem weighting | A field not assigned to a subsystem **silently counts as propulsion** (all derived fields, wing-borne units) | Propulsion weighs more than one subsystem's share. Already noted 2026-09-28 (fuselage_count, emp_count, fuselage_sym) |
| 3 | Gower distance | The range of a count is taken over the rows passed in | The same pair can get a different distance in a sub-sample |
| 4 | Firm leverage (Figure 17) | Firms are ranked on the `firm` column but dropped on `company_canonical` | Differs only for firms outside the hand-written name list |
| 5 | One vote per filer | Two different tie rules in two tables (first seen vs. class size) | Small; only on tied firms |
| 6 | Named-company HHI / top-10 share | Divided by all patents, not by the named ones | The two concentration numbers are not on the same base as the others |
| 8 | Class shares per window (3.1) | The table divides by the classed aircraft (211 in 2016-19), Figure 10 by all aircraft incl. 2 with no class recorded (213) | Tilt Propulsor 2016-19 prints 24 % in the table, 23 % in the figure and text ("equal to Lift + Cruise"). Pick one base for both |
| 7 | Archetype names (C·U) | When a class holds one aircraft recorded with 0 propulsor units, EVERY aircraft of that class in the lowest band is printed "0-3" instead of "1-3" | Names only; no count, share or test changes |

## Choices with no stated reason (state them in the method, or change them)

- Turning point searched only in 2009–2020; 2 000 residual resamples.
- Growth base window 2005–2009.
- Regional lag window fixed at 2016–21.
- Lag verdict cuts at p 0.05 and 0.10.
- Rarefaction to n = 40 aircraft.
- Benjamini–Hochberg q-values are not capped at 1 (one q can print above 1).
- The proximity permutation test has no +1 correction, and draws with all-same or no-same pairs are counted as non-hits.

## Reproducibility notes (no decision needed)

- Every resampling uses seed 42, but several tests share one random stream across levels, windows or series. Changing the
  ORDER of levels or windows changes those numbers slightly (dominant design C·U then C·W·T; discovery curve A0, A0c, A1t;
  doubling ratio; lag offsets; turning point). The lib keeps the document's order.
- Ties for the largest archetype are broken by first appearance; the document marks them "tied".
- The "priority year reached" column of the discovery curve is the sorted years, not an average, though a comment says averaged.

## Not ported (not used by the 45-page document)

The logistic likelihood-ratio test of ducting by propulsor band (`la_duct_units`, full document only), and every
sentence-writing function (wording, not science).

## Text to fix (found while rebuilding the figures)

- **Figure 1 caption** (from the 45-page document) describes panel (ii) twice, and the second description is stale:
  "(ii) eVTOL's share of aeronautics, of section B and of all patenting worldwide, relative to its 2005-09 share".
  The panel now shows each series' growth relative to its own 2005-09 mean, on a log axis. Keep only the first
  description. The notebook copies the caption as the document has it, so fix it once in build_40.py (or in the thesis).
- **Figure 16 (ii)**: the document printed the named-company share as 71 % (2016-19) and 69 % (2024-26), computed as
  1 − the rounded shares of the other two filer types. The exact values are 150/213 = 70 % and 39/56 = 70 %; the thesis
  figure prints 70 %.
- **Figure 9 label**: the document's figure printed "C·U: 1.0 new" while its text and table say 1.1 (stored 1.05);
  the thesis figure prints 1.1.
