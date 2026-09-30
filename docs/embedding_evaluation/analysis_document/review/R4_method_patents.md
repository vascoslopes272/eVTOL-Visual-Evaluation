# R4. Evaluation method and patent-drawing results (§3, §4), 2026-09-30

Flags on ANALYSIS.md, focused on §3 "Evaluation method" and §4 "Results: patent drawings"
(T1-T7), checked against embedding_protocol.py, view_erasure/VIEW_ERASURE.md +
view_erasure.csv, registers_check/, and PATENT_EMBEDDING_ANALYSIS_REGISTERS.md. Severity:
MUST = a jury would attack it or a claim is not supported as written; SHOULD = clearly
strengthens the document; COULD = polish. At most 15 flags, most important first.

## Robustness

**F4.1 [MUST]** · §4.4 (lines 380-397) · The view-erasure paragraph and Table 17 report the
erasure as if it cleanly removes the view ("the aircraft vectors are rebuilt", scores compared
before/after) but drop the one caveat the source explicitly names: the 3 directions are fitted
and applied on the *same* 1 541 figures, so the removal is "exact in-sample, which is where it
is applied." VIEW_ERASURE.md's own held-out check (fit on half the makers, evaluate on the
other half) shows the erasure removes only about half of the above-chance view signal
out-of-sample (linear view probe 0.823 → 0.504 base / 0.455 registers, vs. 0.79 → 0.22 in-sample
on main figures) · Without this, a reader takes "0.79 to 0.22" as the erasure's real strength;
it overstates how much view signal is actually gone from a vector the erasure was not fitted on,
which matters for the "architecture survives removing the view" claim in §8 · Add one sentence
to §4.4 (or a footnote): "The three directions are fitted on the same figures they are applied
to; fitted on one half of the makers and applied to the other, only about half of the
above-chance view signal is removed, so this is an in-sample, not a held-out, erasure." · no
compute, wording only (numbers are already in VIEW_ERASURE.md).

**F4.2 [MUST]** · §4.1, Table 16 (lines 333-344) and its prose (line 354) · Five of the twelve
G1 classes have n < 30 (DS 5, SRW 9, RC 9, PFV 10, HB 20), and DS/PTC/SRW have recall exactly
0.00. The prose states "PTC, DS, SRW are never recovered" as a finding, and only RC's small n is
flagged in-line ("scores high, but on very few aircraft"); the small-n caveat for the others is
left to §9's Limitations, one page away and not linked from the table · A reader can take "never
recovered" as a stable property of PTC/DS/SRW rather than what it is: 0/26, 0/5 and 0/9, numbers
with no real precision · Add a note under Table 16 flagging DS, SRW, RC, PFV, HB (n < 30) as
unreliable and cross-reference §9; soften "PTC, DS, SRW are never recovered" to "recall was 0 in
this sample for PTC (26), DS (5) and SRW (9)" · no compute, wording only.

**F4.3 [SHOULD]** · §3 (line 284) and Table 15 (lines 314-321) · Every kNN-5 score carries a
bootstrap interval and a shuffled-label chance level; the probe column next to it (0.21-0.36 on
12 classes) has neither. §3 does not say why the probe gets no interval, and the probe is used
in §4.1 to argue "the architecture is in the vector" (0.36 against the neighbours' 0.23) without
any uncertainty on that 0.36 · An unqualified point estimate is being used to support a
comparison to an interval-qualified one · Either report a probe interval (e.g. across the 5
maker-grouped folds, or a paired bootstrap like the kNN CI) or state explicitly in §3 that the
probe is reported as a point estimate and why (e.g. cost, or that it only needs to bound the
kNN score from above) · CPU recompute (rerun probe() with resampled folds/bootstrap; small, the
embeddings are already extracted).

**F4.4 [SHOULD]** · §3 (Table 14, line 297) and embedding_protocol.py (`K = 5`, line 46) · k=5
is used throughout as the primary neighbour count but is never defended or even explicitly
flagged as fixed in advance in the text, unlike the model, resolution and thickening choices,
which Table 7 (§2) explicitly labels "candidates, fixed in advance." No sensitivity check for k
(e.g. k=3, k=10) exists anywhere in the saved results (checked embedding_protocol.py and all
_results.pkl/csv outputs) · A reviewer's first question on a kNN result is usually "why 5,
would another k change the answer" · Add one clause to §3: "k=5, fixed in advance and not
tuned on this corpus" (matching the language already used for the other fixed choices), and
ideally a one-line k-sensitivity check (k=3, k=10) in an appendix table · CPU recompute (the
`knn()` function already takes k as a parameter; rerun on saved embeddings, no GPU needed).

**F4.5 [SHOULD]** · §3 and throughout §4 · No sentence in §3 or §4 addresses multiple
comparisons, though the document reads many intervals/p-values off the same 663 aircraft: T3
across 6 matrices (p ≤ 0.027, worst case), T6 across 6 matrices, T7 across 4 image rules, line
thickening across 4 rows (Table 11), erasure across 4 label sets x 2 controls (Table 17). None
of these p-values or "interval excludes zero" claims are corrected for the number of times the
same test is repeated · Reading 6 uncorrected p-values and picking the ones under 0.05 inflates
the chance of a false positive; a jury may ask about this directly given how many tables report
per-matrix or per-rule significance · Add one sentence to §3 stating the tests are read as
converging patterns across matrices/rules rather than as independent hypothesis tests, or apply
a correction (Bonferroni/FDR) where a single p-value is used to support a claim (e.g. T3's
p ≤ 0.027) · no compute, wording, or CPU if a correction is applied.

## Missing graphs

**F4.6 [SHOULD]** · §4.4, Table 17 (lines 384-393) · The view-erasure result (original vs.
erased vs. variance-matched control, 4 label sets, with 95 % CIs) is only tabulated. This is the
document's central robustness test for §4's headline claim and would read far faster as a
paired bar/slope chart with whiskers than as an 8-column table · Add a chart: one panel per
label set (G1-12, parent-5, Perspective-only G1, Perspective-only parent), bars for
original/erased/variance-matched with 95 % CI whiskers · already in saved results
(view_erasure/view_erasure.csv has value, ci_lo, ci_hi per row) — plotting only, no recompute.

**F4.7 [SHOULD]** · §4.1, Table 16 (lines 333-344) · Per-class recall (the table underlying
"TP and SLC are read best," "PTC, DS, SRW never recovered") is only tabulated, with no visual
indication of how thin some classes are. A bar chart with n printed under each bar (as Figure 2
already does for the taxonomy examples) would make the small-class caveat (F4.2) visible instead
of buried in prose · Add a bar chart of recall per G1 type, sorted by n or grouped by parent
class, with n labelled on or under each bar · already in saved results
(embedding_protocol_registers/t_recall.csv) — plotting only.

**F4.8 [COULD]** · §4.5, Table 18 (lines 401-410) · "The rules span 0.17 to 0.23, and every
interval overlaps the others" is a visual claim (overlapping intervals) made from a table of
4 rows; a small forest/dot plot with the 4 kNN-5 points and their 95 % CIs would let the reader
see the overlap directly instead of computing it from the table · Add a compact dot-and-whisker
plot of the 4 image rules · already in saved results (embedding_protocol_registers/t_by_rule.csv
has knn_bal_acc, ci_lo, ci_hi per rule) — plotting only.

## Organisation

**F4.9 [SHOULD]** · §3 Table 14 (lines 288-300) vs. §4.1 and §4.4 · Table 14 defines exactly
T1-T7 (matching embedding_protocol.py's docstring) as "the seven tests of the protocol," but §4
also relies on two methods that are neither T-numbered nor introduced in §3: the "reports' own
layer rule, run in-sample on 200 random 80 % subsets" (§4.1, a separate function
`layer_choice()`, distinct from the split-half rule of §2.1) and the linear view erasure (§4.4,
implemented in a separate script `view_erasure.py`, not in embedding_protocol.py at all). Both
appear in §4 cold, without forward reference · A reader who just read §3 expecting "everything
§4 needs" will not know these two are supplementary, differently-controlled analyses rather than
part of the T1-T7 protocol · Add one or two sentences to §3 (or a short "beyond the protocol"
note) naming the layer-stability check and the view-erasure test as separate methods, with a
pointer to where each is defined (or define them inline at first use with the same rigor as T1-T7)
· no compute, wording only.

**F4.10 [COULD]** · §4 opening (lines 304-306) · T1 ("Soundness") and T3 ("Separation") are
reported as two unlabelled prose paragraphs before "## 4.1 Reading the architecture (T4)," while
T4 through T7 each get their own "## 4.x" header naming the T-number. This breaks the pattern a
reader has just learned from Table 14 and makes T3 (which carries a real number, d = 0.28, used
later in §6) harder to find and cite · Give T1/T2 and T3 the same "## 4.0 Soundness and
separation (T1-T3)" treatment as T4-T7, or at least name "(T1, T2)" / "(T3)" as bold lead-ins
consistently with the T4-T7 subsection titles (already partly done for T1/T2 but not as a
heading) · no compute, wording/formatting only.

**F4.11 [COULD]** · §3 (line 296) and Table 14 · T3's effect size (Cohen's d) is reported with a
permutation p-value but no confidence interval, while T4's kNN score gets both a bootstrap CI
and a shuffled-chance level. d = 0.28 (§4, line 306) is later reused as the basis for the T6
view/architecture ratio (§4.3) and cited in the erasure discussion (§4.4), so its own precision
matters to more than one downstream claim · Add a bootstrap CI on d alongside the permutation p,
for consistency with how every other primary number in §4 is treated · CPU recompute (bootstrap
resample of the pairwise distances feeding `separation()`; embeddings already extracted).
