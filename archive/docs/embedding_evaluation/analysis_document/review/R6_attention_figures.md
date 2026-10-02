# R6. Attention section (§7) and Appendix, plus a full figure/table audit, 2026-09-30

Two jobs. Part A: flags on §7 "Where the model looks" and the Appendix, checked against
registers_share.csv, dinov2-reg-large_518/ (attention arrays),
analysis_document_figs/f_attention_panel.png and f_attention_base_vs_registers.png, and
1639_LABELLED/3_embedding_evaluation/registers_check/ (attention_base_vs_registers.png,
REGISTERS_CHECK.md). Part B: every figure PNG referenced by ANALYSIS.md was opened and read
(16 figures), and every table (26) was checked against the prose around it. Severity: MUST = a
reader is actively misled or a printed value is wrong; SHOULD = clearly strengthens the
document; COULD = polish. Part A capped at 8 flags, Part B's missing-graph list capped at 10.
The full figure-by-figure / table-by-table audit is in Part B before its flags.

## Part A - §7 "Where the model looks" and the Appendix

**F6.1 [MUST]** · §7, last paragraph (line 558) · §7's own reading — "layer 18 traces the
line-work... almost everywhere" against "layer 24 is sparser... gathers in spots... on
propulsors, hubs and the fuselage" — is exactly the qualitative case for why L24 CLS, not L18
CLS, is the matrix carried forward, but the paragraph never cites the number that would close
that argument. It says only "consistent with the modest kNN scores," with no figure or table
pointer · Table 15 has L18 CLS kNN-5 at 0.118 against L24 CLS at 0.235 (roughly double), and
Table 10/Figure 5 show L24 CLS chosen in 69-79% of the split-half selections against L18 CLS at
0%; neither is named in §7, so the attention section's central claim rests on an unstated
number · Add one sentence: "L18 CLS scores 0.118 against L24 CLS's 0.235 on the same 12 classes
(Table 15), and the split-half rule never picks L18 CLS (Table 10): the layer that reads every
line is not the layer that reads the architecture." · wording only, numbers already computed.

**F6.2 [SHOULD]** · §7, first paragraph (line 548) · The register-token share (0.32 to 0.44)
quoted in §7's opening sentence has no table anywhere in ANALYSIS.md. Table 8 (§2.2) carries the
"largest single patch" share that the same sentence also quotes, but not the register/prefix
share; that number exists only in registers_share.csv (prefix_share_median column) and in the
sidecar REGISTERS_CHECK.md, neither of which the reader of ANALYSIS.md can see · A number the
text leans on ("so no single background patch dominates") is unverifiable from the document
itself · Add a "register-token share" column to Table 8, or a two-row table in §7. Data is
already in registers_share.csv · low cost, no recompute.

**F6.3 [MUST]** · Figure 16's Figure-Source note (line 553) · Every attention map in Figure 16
is independently rescaled to its own 99th percentile ("each map scaled to its own 99th
percentile"), which is disclosed only in the technical Source line, not in the "How to read"
line that actually instructs the reader how to look at the figure. §7's prose then reads the
panel for *relative* intensity across layers and sources ("layer 24 is sparser," "a scatter of
weak spots") — a legitimate use of a per-image-normalised map for spread/shape, but the
qualification that brightness is not comparable in absolute terms between panels or aircraft is
easy to miss on a skim, and the whole section is explicitly "read by eye" · Move or repeat the
normalisation caveat into "How to read": "each map is scaled to its own brightest patch, so
compare where the light falls, not how bright it is, between panels." · one sentence.

**F6.4 [SHOULD]** · §7, last paragraph (line 558) · "Layer 24... gathers in spots... often on
propulsors, hubs and the fuselage" is followed two sentences later by "On neither source does the
attention settle on one part that names the architecture." Propulsors and hubs are exactly the
parts that would name the architecture (arrangement of lift and thrust), so the two clauses pull
against each other and the tension is never resolved · A reader can reasonably ask "then why
doesn't the model read the architecture from those spots" and the section does not answer it ·
Add a clause connecting the two, e.g. "...but the same spots light up for aircraft the model
gets wrong as often as for aircraft it gets right (Figure 8), so landing on a propulsor is not
the same as reading its arrangement." Requires checking whether high-propulsor-attention cases
overlap with the confusion-matrix off-diagonal, or soften the propulsor/hub claim if that check
is not done · low-to-moderate: one sentence if softened, a small check if the causal claim is
kept.

**F6.5 [SHOULD]** · Appendix (lines 588-629), Tables 24-26 · Confirmed by grep: no
"Appendix," "Table 24," "Table 25" or "Table 26" occurs anywhere in the document outside the
Appendix heading itself. The registers columns of Tables 24-26 exactly reproduce numbers already
printed in Table 15 (drawings, 12 classes), and Table 19 (photos, 5 classes) — e.g. Table 24's
"L24 CLS, kNN registers 0.235, probe registers 0.362" is Table 15's L24 CLS row verbatim. The
only new information is the base-model column at layers other than L24 CLS (L24 CLS base/registers
is already in Table 9) · As written, the Appendix is mostly a restatement, and the one part of it
that is new (the full base-vs-registers grid, which is the direct evidence for §2.2's model
choice) is never pointed to from §2.2 · Add "(full grid across all layers: Appendix Tables
24-26)" to §2.2 or §2.6 where the model choice is argued; consider dropping the registers columns
from Tables 24-26 since they duplicate Tables 15/19 exactly · low cost either way.

**F6.6 [SHOULD]** · Figure 9's caption (line 365) against Figure 13's caption (line 460) ·
Figure 9 (patent UMAP) ends its "How to read" with "The rotatable 3-D version is linked in the
appendix." Figure 13 (photo UMAP) has no such line, even though the Appendix's second 3-D link
("evtol.news photos with the patents in one joint map") does cover the photos · A reader of §5
alone (skipping §4) has no way to know a rotatable counterpart to Figure 13 exists · Add the same
sentence to Figure 13's caption, naming it as the joint map since there is no photos-only 3-D
page · one sentence.

**F6.7 [COULD]** · Appendix, "Rotatable 3-D maps" (lines 631-636) · Both links are plain
`file:///mnt/storage_11tb/...` paths to the author's own machine; they will not resolve for any
other reader, and a PDF/Word export of this document will carry two dead links with no warning ·
Not a correctness problem for the author's own review pass, but worth flagging before this
document goes to a supervisor or committee, since a dead local-file link reads as a broken
document rather than an intentional author-only convenience · Add "(author's machine only)" next
to the links, or export/host the two HTML files before distribution · none needed now, a few
minutes before hand-off.

**F6.8 [COULD]** · §7, first paragraph (line 548) · "Two aircraft per class and source were
drawn at random" is stated in the body text without the seed; the seed (42) is given only in
Figure 16's Figure-Source line. A reader working from the prose alone cannot tell the sample is
reproducible · Add "(seed 42)" to the body sentence, matching how §2.1 and the UMAP figures state
their seeds inline · trivial.

## Part B - Figure and table audit

### Counts per section

| section | figures | tables | note |
|---|---:|---:|---|
| 0 Summary | 0 | 2 | all-table (expected: it is the answer table) |
| 1 Data and images | 3 | 4 | |
| 2 Setup selection | 3 | 7 | table-heavy (7:3) |
| 3 Evaluation method | 0 | 1 | all-table (a method listing, not a result) |
| 4 Results: patent drawings | 4 | 4 | |
| 5 Results: photographs | 3 | 2 | §5.3 subsection is all-table (Table 20, 0 figures) |
| 6 Drawings vs photographs | 2 | 3 | |
| 7 Where the model looks | 1 | 0 | all-figure (fits a qualitative section) |
| 8-10 Conclusions/Limitations/Open Qs | 0 | 0 | prose only |
| Appendix | 0 | 3 | all-table; see F6.5 |
| **Total** | **16** | **26** | |

### Figures

| id | section | verdict | fix |
|---|---|---|---|
| Fig 1 funnels | §1 | OK | none; clear axes, counts labelled, source in caption |
| Fig 2 patent examples | §1.1 | OK | G1 codes correctly printed (incl. PFV); fine reference numerals may be small at A4 print, inherent to source drawings |
| Fig 3 photo examples | §1.3 | FIX | "HB: Hover Bikes / PFD" should read PFV (B1); HB panel caption text is cut off mid-word (B2) |
| Fig 4 base vs registers attention | §2.2 | MINOR | row headers mix G1-type codes (TP, MR) and parent-class codes (VT, WM) with no note on the switch of granularity |
| Fig 5 layer/token selection | §2.3 | OK | none |
| Fig 6 thickening | §2.4 | OK | detail crops mitigate small-scale risk |
| Fig 7 pat prediction | §4.1 | OK | none |
| Fig 8 pat confusion | §4.1 | MINOR | no colour-scale bar in-image, relies on caption text (B10) |
| Fig 9 pat UMAP | §4.2 | FIX | legend "PFD" should read "PFV" (B1); caption could name the joint 3-D link (F6.6) |
| Fig 10 view vs architecture d | §4.3 | OK | none |
| Fig 11 pho prediction | §5.1 | OK | none |
| Fig 12 pho confusion | §5.1 | MINOR | same colour-scale-bar note as Fig 8 |
| Fig 13 pho UMAP | §5.2 | FIX | legend "PFD" should read "PFV" (B1); missing 3-D-link sentence (F6.6) |
| Fig 14 five-class comparison | §6 | OK | none |
| Fig 15 matching curve | §6.1 | OK | none |
| Fig 16 attention panel | §7 | MINOR | see Part A F6.1, F6.3; cells are small (~226 px wide at 8 columns) for dense line drawings at A4 |

### Tables

Tables are graded on three questions: could it be a figure instead, is it referenced by number
in the prose, does it duplicate a figure. Most tables in this document are deliberately paired
with a figure (exact numbers in the table, the same numbers charted next to it) — that pairing is
a consistent, useful house style here, not sloppy duplication, and is marked "paired" below
rather than flagged.

| id | section | referenced in prose | duplicates a figure | verdict |
|---|---|---|---|---|
| Table 1 questions/answers | §0 | is the summary itself | no | OK, summary table |
| Table 2 chosen setup | §0 | is the summary itself | no | OK |
| Table 3 G1 types | §1.1 | yes ("Table 3") | no | OK, defines codes used everywhere after |
| Table 4 image rules | §1.2 | yes | no | OK |
| Table 5 flight state | §1.2 | yes | no | OK, but see B9 (Perspective-only subtotal not checkable against it) |
| Table 6 selection sensitivity | §1.4 | yes | no | OK; could be a small dumbbell/forest plot but table is precise and small enough as-is (COULD) |
| Table 7 candidate grid | §2 | yes | no | OK |
| Table 8 attention collapse | §2.2 | yes (Table 8) | paired with Fig 4 | OK; missing prefix-share column, see F6.2 |
| Table 9 registers vs base | §2.2 | yes | no | OK |
| Table 10 layer/token decision | §2.3 | yes | paired with Fig 5 | OK |
| Table 11 thickening | §2.4 | yes | paired with Fig 6 (qualitatively) | OK |
| Table 12 optimism gap | §2.6 | yes | no | OK |
| Table 13 chosen setup (final) | §2.6 | is the section's conclusion | no | OK |
| Table 14 seven tests | §3 | yes | no | OK; reference table, fine without a figure |
| Table 15 drawings prediction | §4.1 | yes | paired with Fig 7 (partial: Fig 7 omits the 5-class columns) | OK |
| Table 16 recall per G1 type | §4.1 | yes | paired with Fig 8 | OK |
| Table 17 view erasure | §4.4 | yes | no | OK |
| Table 18 image-rule sensitivity | §4.5 | yes | no | OK; no photo-side counterpart, see B7 |
| Table 19 photos prediction | §5.1 | yes | duplicates Fig 11 almost completely | OK by house style, but this is the one pair with near-total overlap; no action needed |
| Table 20 cropping | §5.3 | yes | no | OK; §5.3 is the one all-table subsection, fine at this size |
| Table 21 photos vs drawings | §6 | yes | paired with Fig 14 | OK |
| Table 22 recall, matched mix | §6 | yes | paired with Fig 14 | OK |
| Table 23 same-aircraft matching | §6.1 | yes | paired with Fig 15 | OK; base-model matching (37%) cited in §2.2 has no row here, see B6 |
| Table 24 appendix, drawings 12-class | Appendix | no | duplicates Table 15's registers column | see F6.5 |
| Table 25 appendix, drawings 5-class | Appendix | no | duplicates numbers scattered in §4.4/Table 17 | see F6.5 |
| Table 26 appendix, photos 5-class | Appendix | no | duplicates Table 19 / Fig 11 almost completely | see F6.5 |

### Claims with no figure or table behind them (missing-graph flags, max 10)

**F6.9 [MUST]** · §1.3 (line 109) vs §6.1 (line 525) · §1.3 says "On the 99 patent aircraft that
have a directory page..."; §6.1 says "For the 94 patent aircraft that have a directory page...".
Both describe what reads as the same overlap set (patent aircraft with an evtol.news page), with
no stated reason for the 5-aircraft gap · A reviewer who reads both sections will hit a
contradiction with no resolution in the text · Reconcile the two counts, or add one clause
explaining the difference (e.g. a join or dedup step between §1 and §6) · needs a data check
first, then a one-sentence fix.

**F6.10 [SHOULD]** · §1.1 (line 49) · The headline "κ 0.94" (627 of 662 aircraft agree with the
independent whole-patent reading) has no table or figure anywhere in the document, including the
Appendix, and is not revisited even though §4.1's near-zero recall for PTC/DS/SRW makes "where do
the 35 disagreements fall" a natural follow-up question · Add a small table (disagreements by G1
type) reusing the existing whole-patent-reading comparison · moderate: data likely already
computed for the κ figure elsewhere in the pipeline.

**F6.11 [SHOULD]** · §1.3 (line 111) · The photo-filter audit ("96 of 100 hero images show the
whole aircraft, 3 of 40 dropped images were a whole vehicle, 18 of 40 review-band images would
have been usable") is three numbers in one sentence with no table · This is the evidence behind
a limitation the document itself flags in §9 ("not blind... not yet re-checked"), so it deserves
to be checked easily, not read off prose · Add a 3-row table (sample, n, correct/usable count) ·
low cost, numbers already stated.

**F6.12 [SHOULD]** · §2.2 (line 198) · "Patent-to-photo matching improves too (own page in the
top 50: 37% base, 48% registers)" cites a base-model matching result that appears nowhere else;
Table 23 and Figure 15 report the registers model only · Fix: add a base-model row to Table 23,
or a footnote saying where the 37% comes from · low cost if the base-model matching run is
already saved.

**F6.13 [SHOULD]** · §5.3 (line 478) · "hero image 0.563, one random other image 0.521, the mean
of all kept images 0.578, against an interval about 0.06 wide for one rule" is the photo-side
counterpart to Table 18 (image-rule sensitivity for drawings) but has no table of its own · Add
a photos block to Table 18, or a Table 18b · low cost, values already computed.

**F6.14 [SHOULD]** · §4.1 (line 331) · "The reports' own layer rule, run in-sample on 200 random
80% subsets, picks L24 CLS in 96% of them, in line with the split-half rule" names a second,
separate layer-selection procedure and result that is never tabulated, unlike the split-half
rule's own Table 10/Figure 5 · Either drop this corroborating aside or add it as a column/footnote
to Table 10 so the 96% is checkable · low cost to drop, moderate to tabulate.

**F6.15 [COULD]** · §1.2 (line 80) · "more convertible aircraft have a Perspective figure in
Cruise (220) than in Hover (212) among the 339" is a Perspective-only breakdown that cannot be
checked against Table 5, which is sliced by G1 type x flight state across all views, not by view
· Add a footnote to Table 5 or a one-line note clarifying the 220/212/339 come from a different
slice · low cost.

**F6.16 [COULD]** · §4.1 (line 354) · "62% of the wrong predictions fall into SLC or TP" is
derivable from Figure 8 but not stated as a number anywhere in the figure or a table; a reader
would have to sum off-diagonal cells by hand to check it · Add the 62% as a footnote under Table
16 · low cost, arithmetic already done for the prose.

**F6.17 [COULD]** · §5.1 (line 441) · "Wingless (Multicopter) is read best (recall 0.74) and
Hover Bikes/PFD worst (0.39)" is derivable from Figure 12's diagonal but not labelled as a
recall number on the figure itself (confirmed: 247/332 = 0.744, 45/114 = 0.395, both match) ·
Low priority since the numbers check out, but a per-class recall row under Figure 12 (as Table 16
already does for drawings) would remove the need to compute it by hand · low cost.

**F6.18 [COULD]** · §6 (line 493) · "The probes point the same way (0.61 for drawings, 0.66 for
photos)" resolves to Table 25/26's L24 CLS probe-registers values (0.606, 0.662) but those tables
are in the Appendix, three sections away, with no cross-reference from §6 · Add "(Table 25/26)"
next to the sentence · trivial.
