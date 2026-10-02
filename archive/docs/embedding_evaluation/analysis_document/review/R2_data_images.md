# R2. Data and images (§1), 2026-09-30

Flags on ANALYSIS.md §0 (context) and §1 "Data and images", checked against
1639_LABELLED/2_embedding_extraction/{selection,view_state_experiments}/,
EVTOLNEWS_DS/1_filter/, EVTOLNEWS_DS/2_embedding_extraction/selection/,
PATENT_EMBEDDING_ANALYSIS_REGISTERS.md and EVTOLNEWS_EMBEDDING_ANALYSIS_REGISTERS.md.
Severity: MUST = a jury would attack it or a claim is not supported as written; SHOULD =
clearly strengthens the section; COULD = polish. 11 flags, most important first.

Overall: the numbers in §1 check out. Every count I re-derived from source (funnel.csv,
VIEW_STATE_REPORT.md, image_decisions.csv, both registers reports) matches ANALYSIS.md
exactly (663 aircraft/572 patents/1541 figures; 157/109/59/25/26/5/184/9/50/9/20/10 by G1
type, summing to 663; the 339/212/220/169/76 convertible-state numbers; the 96/100, 3/40,
18/40 audit numbers; 410/218/332/83/114 photo classes, summing to 1157). The problems are
what the section leaves out or leaves unexplained, not arithmetic.

## Robustness

**F2.1 [MUST]** · §1.1 (line 49, κ 0.94) and §9/§10 · The section never says whether the 663
aircraft's G1 labels come from one labeller or several. §10 lists this as an open question
("The reports do not say whether the G1 labels come from one labeller... is a second-labeller
check planned?") rather than answering it, and §9's Limitations only notes "the embedding
reports record no second-labeller agreement" · This is the first question a jury asks about a
human-labelled dataset that everything else (T3-T7, the whole chapter) is built on; leaving it
as an open question to the author, still present in the document, reads as unresolved at
submission · State the fact plainly in §1.1 next to the κ 0.94 figure ("one labeller" or "N
labellers, reconciled how"); if a second-labeller check is not planned, say so and say why the
κ-vs-whole-patent-reading check (627/662) is offered as the substitute; then remove or resolve
the §10 open item · Cost: stating the fact is free (it is pipeline/labelling-process knowledge
already held); a real second-labeller pass would be new manual labelling work, not compute.

**F2.2 [MUST]** · §1.4/§5.3 (lines 121-142, 463-478) vs. EVTOLNEWS_EMBEDDING_ANALYSIS_REGISTERS.md
Section 7 (Tables 10-11, Figure 8, "f05_rules.png") · ANALYSIS.md's Table 6 (§1.4) gives the
drawings a proper "does selection decide the result" table with 95% intervals for 4 variants,
and §4.5's Table 18 gives the drawings' image-choice test (exp1-exp4) the same treatment. The
photo side of exactly this question (does the choice of image change the score: hero vs. a
random other image vs. the mean of all kept images) is reduced to one sentence in §5.3 with
three bare point estimates and no interval ("hero image 0.563, one random other image 0.521,
the mean of all kept images 0.578, against an interval about 0.06 wide for one rule"). The
source register report already has this fully worked: Table 11 (all 6 matrices × 3 rules) and
Figure 8, a chart with a 95% bootstrap interval marked per rule · Priority-1 robustness demands
that "no step decides the outcome" be shown, not asserted, for both sources equally; right now
the photo image-choice check is the one place in the document where the reader is asked to
trust a summary sentence instead of seeing the numbers · Pull Table 11 (or its L24 CLS row with
its own interval) and Figure 8 into §5.3 (or a new §1.4b for photos, mirroring Table 6/18's
treatment) · Cost: already in saved results (EVTOLNEWS_DS/3_embedding_evaluation/
embedding_analysis_registers/tables/ and figs/f05_rules.png) — copy/reformat only, no
recompute.

**F2.3 [SHOULD]** · §1.3 (line 111) vs. EVTOLNEWS_EMBEDDING_ANALYSIS_REGISTERS.md Table 2 ·
The audit numbers are quoted as bare counts ("96 of 100 hero images", "3 of 40", "18 of 40")
with no interval, even though every other estimate in the document (kNN-5, probe, ARI, d) is
given with a 95% interval, and the source register report already computes one for the
headline row: "96% usable (95% interval 90 to 98%)" · With n = 100/40/40, a reader has no way
to judge how much "96%" or "18/40 usable" could move on a different sample; omitting the one
interval that is already computed, on the section that is explicitly least trustworthy of the
document's inputs (the only non-blind, non-re-checked judgement), understates the uncertainty
exactly where it matters most · Quote the [90, 98] interval already in Table 2 next to "96 of
100"; add a Wilson or bootstrap interval for the 3/40 and 18/40 rows too · Cost: the kept-row
interval is already in saved results; the other two rows are a CPU recompute (one Wilson-score
calculation each, seconds).

**F2.4 [SHOULD]** · §1.1, Table 3 (lines 51-68) and §1.3 (line 109) · The 12 drawing classes
and the 5 photo classes are each listed as counts, but the small classes are not called out in
§1 itself — that framing appears only in §9 Limitations ("DS 5, SRW 9, RC 9, PFV 10 aircraft").
A reader of §1 alone (the data-description section) has to notice the imbalance unaided, then
wait three sections to be told which classes are thin, by which point §4's Table 16 has already
shown DS/PTC/SRW at 0.00 recall without the reader having been primed for it · Framing the
imbalance where the classes are first introduced is more honest: it shows the small classes were
known and named before results were read, not retrofitted as an excuse in Limitations · Add one
sentence after Table 3 naming the smallest types (DS 5, SRW 9, RC 9, PFV 10) and, in §1.3, name
the smallest photo class (ER, 83, against 410 for VT) · Cost: free (the counts are already in
Table 3/the §1.3 prose; this is a sentence, not new data).

**F2.5 [SHOULD]** · §1.3 (line 109) vs. §6.1 (line 523) · §1.3 says "On the 99 patent aircraft
that have a directory page..."; §6.1 says "For the 94 patent aircraft that have a directory
page..." for what reads as the same population. Neither ANALYSIS.md nor the underlying
EVTOLNEWS registers report (Section 9, "94 patent aircraft with a linked page") explains the
gap. The likely reason (some of the 99 aircraft's own hero image is itself a line drawing of the
patent figure and gets removed from the matching gallery in §6.1, so those aircraft cannot be
scored as queries) is never stated anywhere · A careful reader — or a jury member cross-checking
numbers, which is exactly what this review is doing — will flag 99 vs. 94 as an unreconciled
inconsistency, which erodes trust in the rest of the counting even though the underlying reason
is probably benign · Add one clause at the first use of "94" in §6.1 (or a footnote in §1.3)
explaining the drop from 99 · Cost: confirming the exact mechanism is a CPU check (compare the
99-aircraft link list against matching.csv's 94 queries); stating it once confirmed is free.

## Missing graphs

**F2.6 [SHOULD]** · §1.1, Table 3 · Twelve rows of counts (157 down to 5) is the kind of table
the dataviz guidance in this project explicitly flags as a candidate for a bar chart, and this
one doubles as the reader's first look at class imbalance, which recurs as the main limiting
factor in §4 and §6. No chart is given; Figure 2 right after it shows one example drawing per
type but not the counts · Add a bar chart of aircraft per G1 type (663 aircraft), grouped or
coloured by the 5-class parent, placed between Table 3 and Figure 2 · Cost: CPU only (the counts
are already in Table 3 / selection outputs; this is a plotting job, same pipeline as the
existing f_funnels.png).

**F2.7 [SHOULD]** · §1.3 · The photo label counts (VT 410, LC 218, WM 332, ER 83, HB 114) are
given only in prose, with no table or chart at all — the one dense-number spot in §1.3 that
gets less treatment than the equivalent drawing table (Table 3). For parity with the drawings
side (and because these same 5 counts get reused, recomputed as recall, in §6 Table 22), a small
table or bar chart here would let the reader see the class balance of the photos before §5 and
§6 use it · Add a table (mirroring Table 3's structure but for 5 classes) or a small bar chart
in §1.3 · Cost: CPU only (counts already known, stated in prose; a table costs nothing, a chart
is a small plotting job).

**F2.8 [SHOULD]** · §1.2, Table 5 (lines 93-103) · A 5×4 table of raw figure counts (Cruise/
Hover/Both/Other per convertible G1 type) is exactly the kind of dense table the review brief
flags as a chart candidate, and it sits directly under the claim that Cruise (220) narrowly beats
Hover (212) among Perspective figures — a claim that is easier to see on a grouped bar chart than
by mentally summing table cells. A stacked or grouped bar chart (5 types × 4 states) would also
make "the flight state barely moves the vector choice" (the sentence right after the table)
visually obvious rather than asserted · Add a grouped bar chart under Table 5, keep the table for
exact figures · Cost: CPU only (the counts come straight from VIEW_STATE_REPORT.md /
view_state_experiments/, already computed; plotting only).

## Organisation

**F2.9 [SHOULD]** · Throughout, first at §0 line 5 and §1.1 Table 3 · "G1" is used from the
first paragraph of the document onward as if self-explanatory (the codebook's 12 "G1 architecture
types") and is never expanded or glossed anywhere in ANALYSIS.md. A reader without the codebook
chapter open (a jury member reading this chapter on its own, as this review was asked to do) has
no way to know what "G1" refers to versus, say, a "G2" or a parent class · Add a one-clause gloss
at first use ("G1, the wizard's primary architecture-type field") in §0 or the opening of §1.1 ·
Cost: free.

**F2.10 [SHOULD]** · §1.1 end (Figure 2, lines 70-76) vs. §1.2 (Table 4, line 90) · Figure 2's
caption and source line name "rule exp3 main figure" before "main figure" has been defined — the
definition ("the figure the labeller marked as main (primary rule)") only appears in Table 4,
one subsection later. This is a plain definitions-before-use violation: the reader meets the term
in a figure caption first, in a table second · Either move Figure 2 after Table 4, or add one
clause in §1.1's prose introducing "main figure" before Figure 2 · Cost: free (reorder or one
sentence).

**F2.11 [COULD]** · §1.1, Table 3 caption/column (line 52) · The "parent (5-class)" column is
introduced with no explanation of why a second, coarser class scheme exists; the reason (it is
the same 5 classes the evtol.news photos are labelled with, which is what makes §6's drawings-
vs-photos comparison possible) is only made explicit much later, in §6's opening paragraph. A
reader hitting "parent (5-class)" in §1.1 has to either guess or hold the question until §6 ·
Add one sentence after Table 3: the parent column folds each G1 type into the same 5 classes
used for the photos, so the two sources can be compared on shared ground in §6 · Cost: free.
