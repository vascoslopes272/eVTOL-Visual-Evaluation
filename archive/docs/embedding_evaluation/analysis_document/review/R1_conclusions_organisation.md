# R1. Conclusions, robustness and organisation of ideas

Review of `ANALYSIS.md` (build of 2026-09-30), read-only. Focus: §0 Summary, §8 Conclusions, §9 Limitations, §10 Open questions, and the order of ideas across the document. Numbers checked against `embedding_protocol_registers/`, `registers_check/`, `view_erasure/`, `setup_selection/`, the photo registers report and `src/analysis_document.py`.

---

**F1.1 [MUST]** · §0 Table 1 row 1, §2.2 last paragraph, §8 first paragraph
- **What is wrong.** The headline 0.23 is a full-sample score of a setup chosen on the same labels, and the model choice was made after the full-sample scores were seen. §2.2 says "The model choice was fixed in advance on the attention artifact". `registers_check/REGISTERS_CHECK.md` ends on "Open decision (author's): keep dinov2-large ... or switch", written after the 0.178 to 0.235 gain was known, and CHAPTER_PLAN N2 says "Model decision deferred ... Decide by comparison". The only planned model, base, scores 0.178. When both models compete, the optimism gap is 0.027 (12 classes) and 0.038 (5 classes) (SETUP_SELECTION S1a). Table 12 shows only the smaller registers-only gap, and neither §0 nor §8 mentions any of this.
- **Why it matters.** A jury will ask whether the headline number was picked because it was the best one. The honest answer exists and is favourable (base is still above chance, and the optimism is small), but the document states the opposite of the record.
- **What to do.** Rewrite the §2.2 sentence: "The attention artifact motivated the check; the switch was decided after both models had been scored, and the held-out rule confirms it." Add the "all 12 compete" rows (gap 0.027 / 0.038 / 0.018) to Table 12. In §0 and §8 quote the headline as "0.23 [0.19, 0.28]; about 0.21 after the selection optimism; 0.18 with the model planned before any score". Add a bullet to §9 "Post hoc model choice". This also closes the §10 question "Which registers number is the headline?".
- **Cost.** Already in saved results (`setup_selection/s1a_*.csv`).

**F1.2 [MUST]** · §0 Table 1 row 3, §6 Table 22 text, §8 first sentence, §10 bullet 5
- **What is wrong.** "The gap is mostly the pool" (§0) and "shrinks to nothing measurable" (§8) rest on the drawings' 0.445 falling inside the 2.5 to 97.5 % range of 200 photo subsamples (0.367 to 0.557). That range is subsample-to-subsample variation only (`class_mix_matched()` draws without replacement). It leaves out the drawings' own sampling error ([0.36, 0.53]), so it is not an interval on the difference. The test can exclude only gaps larger than about ±0.1, so "nothing measurable" says more about its power than about the media. Size and class mix also change together, so "the pool" is not split into its two parts. Finally, §10 lists this as an open ruling while §0 and §8 already rule on it.
- **Why it matters.** This is the secondary claim of the chapter. As written, a jury can read "not shown to differ" as "shown equal".
- **What to do.** (a) For each of the 200 draws, subtract a bootstrap draw of the drawings' score, and report the matched difference with a 95 % interval (expected to be around +0.02 [−0.1, +0.14]). (b) Report the share of the +0.119 gap that matching removes (0.100) with its interval. (c) Add a size-only control (663 random photos with the photos' own mix) to separate size from mix. (d) In §8 write: "Matched in size and class mix, the photos are not shown to read the architecture better (difference +0.02 [x, y]); the test cannot exclude a difference of about 0.1 either way." Settle §10 bullet 5 before §0 takes a side.
- **Cost.** CPU recompute (minutes; embeddings are saved).

**F1.3 [MUST]** · §8 "What DINOv2 contributes", §4.1 Table 16
- **What is wrong.** "The types it never recovers (PTC, DS, SRW) are defined by how the propulsion moves or acts, which a single silhouette need not show" is a hypothesis that is never tested. It is confounded with class size, because DS has 5 aircraft, SRW 9 and PTC 26, and §4.1 itself says a neighbour vote fails thin classes. The document's own numbers cut against it: RC (9 aircraft) reaches 0.67, and TB (25, a shape-defined type) only 0.08. "The types recovered best are the large ones" is what kNN produces by construction, so it cannot count as a test of the taxonomy. The per-class recalls carry no interval (0/5, 6/9).
- **Why it matters.** This paragraph is the chapter's claim to say something about the codebook itself, and it rests on the least robust numbers in the document.
- **What to do.** Run a size-neutral per-class reading. One option is per-class recall of the maker-grouped probe with balanced class weights. Another is kNN on repeated equal-size class subsamples (for example 20 per class for the 8 classes with 20 or more aircraft). Report per-class recall with Wilson or bootstrap intervals. If PTC, TW and CVT stay low while RC and HB stay high at equal size, keep the sentence and cite that result. If not, rewrite it as a hypothesis for future work and move it to the Discussion.
- **Cost.** CPU recompute.

**F1.4 [MUST]** · §8 first paragraph, last sentence; §0 Table 1 rows 4 and 6
- **What is wrong.** "The result holds with the maker held out, under every image rule, without the photo backgrounds, in greyscale, and after the view of the drawing is linearly removed" merges checks of different kinds and different models:
  - The crop test ran on the base model only (§5.3 says so, but §0 and §8 do not).
  - "Holds" means "stays above chance", yet exp4 loses 0.07 of the 0.235.
  - The view erasure is linear and exact only on the figures it was fitted on. Fitted on half the makers, it removes about half of the view signal on the other half (VIEW_ERASURE limit (a), not in the document).
  - Its variance-matched control appears to be a single random draw (VIEW_ERASURE method step 4).
- **Why it matters.** This is the sentence a jury will read as the robustness claim, and three of its five clauses lose their caveat.
- **What to do.** Rewrite it as a short list, each item with model, effect and interval, for example "cropping the photos (base model): +0.017 [−0.008, +0.043]". Either re-embed the saved OWLv2 crops with the registers model, or write "(base model)" in §0, §8 and §9. Repeat the variance-matched control over 50 to 100 random draws and report the spread. Add "erasure exact in-sample only" to the §9 bullet on the linear erasure.
- **Cost.** Re-embedding the crops needs a short GPU run (about 1 157 images, crops already saved). The erasure control repeats are CPU.

**F1.5 [MUST]** · Order of §1.4, §2 and §3; §0
- **What is wrong.** Terms are used before they are defined:
  - §3 defines the kNN-5 balanced accuracy, the maker hold-out, shuffled chance, the probe and the paired bootstrap. Table 6 (§1.4) and all of §2 use them first, and §0 uses "shuffled level", "probe", "d ratio" and "ARI" with no definition at all.
  - Figure 2's source line uses "rule exp3" before Table 4 defines it.
  - §1.1 uses internal jargon: G1, D1/D2 duplicate, domain gate, UAV-similar, wizard, and "TP is the wizard's TR".
- **Why it matters.** A reader meets the numbers before the ruler, and §2 is the densest statistics in the document.
- **What to do.** Reorder to question (§0) → data (§1.1 to §1.3) → evaluation protocol (current §3) → setup selection (§2) → results. Move Table 6 (selection sensitivity) out of §1.4 into a "Robustness" subsection after §5, where it sits beside T7 and the crop test. Put a five-line "how to read the numbers" box under Table 1 that defines balanced accuracy, shuffled chance, probe, d and ARI. Replace the jargon in §1.1 with one plain clause each, or point to the Methodology chapter.
- **Cost.** None (text only).

**F1.6 [SHOULD]** · Missing figure for §8 paragraph 1 and §0 rows 4 and 6
- **What is missing.** Every robustness result is a separate table (Tables 9, 11, 17, 18, 20, 22, and the §2.5 text). No single figure shows them side by side.
- **Why it matters.** The §8 claim "the result holds under ..." reads fastest as one picture. It also shows the jury at a glance which checks move the score (registers, thick2, erasure) and which do not (grey, crop, image rule).
- **What to do.** Draw one forest plot of paired differences with 95 % intervals and a zero line. Rows: registers − base, thick1, thick2, grey, crop (marked "base"), view erasure, variance-matched removal, Perspective-only erasure, exp1/exp2/exp4 − exp3, and matched photos − drawings. Reference it from §8 and from Table 1.
- **Cost.** Already in saved results, apart from the exp-rule paired differences (F1.11, CPU).

**F1.7 [SHOULD]** · Missing figure for §6 last paragraph and §8 "types recovered best are the large ones"
- **What is missing.** The pool argument ("a class is read well largely when it dominates the pool") is carried by two tables (16 and 22). No figure plots recall against class share.
- **Why it matters.** The pool effect is the key to both the secondary answer and the taxonomy paragraph, and it is visual by nature.
- **What to do.** Plot recall against the class's share of the neighbour pool. Points: the 12 G1 types, the 5 drawing parents, the 5 photo classes and the 5 matched-photo classes, with an interval on each and labels. If F1.3 is run, add its size-neutral recalls as a second marker. Reference the figure in §4.1, §6 and §8.
- **Cost.** Already in saved results (`t_recall.csv`, class counts, matched recall), plus CPU for intervals.

**F1.8 [SHOULD]** · §0 Table 1 row 4, §4 T3 against §4.3, §5 against §5.2, §8 paragraph 2
- **What is wrong.**
  - "Organised first by how the aircraft is drawn" rests on the d ratio of 1.70, which has no interval.
  - The architecture d appears as 0.28 in §4 (T3, 663 aircraft) and as 0.21 in §4.3 (T6, 1 541 figures), with no word on the change of unit. The photos have the same issue (0.44 in §5, 0.46 in §5.2).
  - The strongest simple evidence for view dominance is never quoted in §0 or §8: view kNN 0.73 against a chance of 0.27, and the view probe at 0.79.
  - Only the viewpoint was tested. "How it is drawn" (shading, reference numerals, office style) is wider than what was measured.
  - §4.4 shows the view directions carry no more architecture than random high-variance directions, which fits badly with "first by how, second by what" unless this is spelled out.
- **Why it matters.** This is the second conclusion of §8. It needs an interval and a consistent unit.
- **What to do.**
  - Bootstrap the ratio over aircraft and give its interval.
  - Name the unit each time d is quoted (figures or aircraft).
  - Replace "how it is drawn" with "from which viewpoint it is drawn".
  - Add one sentence to §8 tying the ratio to §4.4: "the view dominates the geometry, yet the architecture signal does not ride on it".
  - Add a UMAP of the drawings coloured by view group beside Figure 9, and reference Figure 10 from §8.
- **Cost.** Ratio interval: CPU. View-coloured UMAP: already in saved results (`_umap_exp3_main_figure_24_cls.npy` plus the view labels).

**F1.9 [SHOULD]** · §0 rows 1 and 2, §4.1, §8 paragraph 2
- **What is wrong.** "The probe reads more than the neighbours, so the architecture is in the vector but does not decide which aircraft are nearest" is a §8 conclusion. It rests on probe values (0.36, 0.61, 0.66) that have no interval and no shuffled-label chance. `t_main.csv` has neither. The probe's regularisation choice is not stated.
- **Why it matters.** The kNN numbers come with an interval and a chance level. The probe numbers carry a conclusion but not the same controls.
- **What to do.** For L24 CLS on both sources, compute a grouped-fold bootstrap interval and a 200-shuffle chance level for the probe, and state how the regularisation was set. Add both to Tables 15 and 19.
- **Cost.** CPU recompute.

**F1.10 [SHOULD]** · §1.1 (κ 0.94), §9 bullet "Labels", §10 bullet 6, §6 and §8
- **What is wrong.** The whole-patent reading is called "independent", yet it is the author's own reading. Per the project record of 2026-09-17, several dozen wizard labels were corrected after that comparison. The frozen figure labels agreed with it at κ 0.866 (n 803); the 0.94 is measured after the corrections. That the labels come from one labeller is known, so §10 bullet 6 is answerable now. Separately, the two sources are labelled by different schemes: the codebook parent for drawings, the directory class for photos, which agree on 83 of 99 linked aircraft. §9 lists this, but §6 and §8 compare the two sources as if the labels were the same.
- **Why it matters.** Inter-rater reliability is a standard jury question. Different label noise in the two sources is a second explanation for the photo gap, beside the pool.
- **What to do.** In §1.1 write "one labeller (the author); agreement with the author's own whole-patent reading κ 0.87 before and 0.94 after correction (a consistency check, not inter-rater reliability)". Remove §10 bullet 6. Add one sentence to §6 and to §8: "the photo labels are the directory's classes, not the codebook's; they agree for 83 of 99 linked aircraft."
- **Cost.** None (in the records).

**F1.11 [SHOULD]** · §0 Table 1 row 6, §4.5 Table 18
- **What is wrong.** "Does the choice of image matter? Little" rests on overlapping intervals, which is not a test. exp3 − exp1 is +0.04, and exp3 − exp4 is +0.07. That is the same size as the view-erasure loss that §4.4 treats as a real cost (−0.043, interval below zero), so the document applies two standards. exp3 is also the labeller's chosen main figure, so part of the headline score may come from human curation.
- **Why it matters.** A jury will notice that 0.04 counts as "little" in one section and as "a cost" in another.
- **What to do.** Compute paired bootstrap differences exp3 − exp1, exp3 − exp2 and exp3 − exp4 on the same aircraft, and add them to Table 18 and to the forest plot (F1.6). Reword §0 as "the labeller's main figure scores highest (+0.04 over view-first, [x, y]); every rule stays above chance". Note in §4.5 that the main figure is a human choice.
- **Cost.** CPU recompute.

**F1.12 [SHOULD]** · §8 structure, §7, §0 Table 2 against Table 13
- **What is wrong.**
  - §8 answers the headline in its first sentence and then gives two of its four paragraphs to contributions and a "recipe".
  - The secondary question of the chapter plan ("where does the visual architecture signal actually live?") gets one subordinate clause.
  - The recipe recommends registers on a mechanism that was never tested (the collapse lowering the score). The recipe's own §4.4 finds the registers advantage gone once the view is erased, and the recipe is generalised from one corpus.
  - §7 answers a question that is not in Table 1 and is not used in §8. Its sentence "the late CLS token summarises the whole shape and the way it is drawn" is untested.
  - Table 2 duplicates Table 13, and Table 7 repeats both.
- **Why it matters.** The closing section should mirror the opening one. As written, it does for the headline, only weakly for the secondary answer, and adds claims the opening never raised.
- **What to do.**
  - Rebuild §8 in the order of Table 1: (1) headline answer with the corrected number (F1.1); (2) drawings against photos with the matched difference (F1.2); (3) the view dominates the geometry but carries no more architecture than random high-variance directions; (4) what this means for the codebook; (5) the recipe, framed "for this corpus and model family", with the registers line hedged by §4.4.
  - Either add a Table 1 row "Where does the model look? Spread over the airframe, no part names the architecture (qualitative, 20 aircraft)", or move §7 to the Discussion.
  - Drop Table 2 and point §0 to Table 13.
- **Cost.** None (text only).

**F1.13 [COULD]** · §0 Table 1 row 7, §1.3, §6.1 Table 23
- **What is wrong.**
  - The 48 % top-50 rate rests on 94 queries and has no interval (a binomial interval is about ±10 points).
  - §1.3 says 99 patent aircraft have a directory page, but §6.1 uses 94, with no reason given.
  - The random baseline (7.6 % for a top 50 of 1 141) assumes several own pages per query, which only the figure caption explains.
  - "The medium separates the sources more than the aircraft joins them" is not tested.
- **Why it matters.** This is a minor section, but the unexplained drop from 99 to 94 and the missing interval invite questions.
- **What to do.**
  - Add Wilson intervals to Table 23.
  - Explain the 5 aircraft that drop out.
  - State the mean number of own pages per query in the text.
  - Either test the medium sentence or cut it. A test: compare the median cosine to the nearest cross-source aircraft against the nearest same-source aircraft of a different maker.
  - This also answers §10 bullet 1 (N5): one paragraph is enough.
- **Cost.** CPU recompute (`matching_ranks.csv` is saved).

**F1.14 [COULD]** · Numeric consistency across sections
- **What is wrong.**
  - (a) §5.2 says the photos' ARI of 0.141 is "5 times the drawings' 0.026". That compares 5 clusters with 12. The like-for-like drawings figure at 5 classes is 0.031 (`t_main_5classes.csv`), so the ratio is about 4.5.
  - (b) Table 8 has 665 drawings and the Table 23 gallery has 665, against 663 aircraft everywhere else.
  - (c) §2.4 has 1 545 source drawings against 1 541 figures elsewhere.
  - (d) §7 puts the register tokens' share at 0.32 to 0.44; REGISTERS_CHECK gives 0.26 to 0.44.
  - (e) §2.6 quotes "0.018 to 0.038 when both models compete", but no table in the document shows it (see F1.1).
  - (f) Table 17 gives no interval on the erased scores and no chance column.
- **Why it matters.** Each is small, but a jury that finds one starts checking every number.
- **What to do.** Fix (a) with the 5-class drawings ARI. Explain the extra 2 aircraft in (b) (probably the 2 unclassifiable ones) and the extra 4 drawings in (c) in a footnote. Align (d) to one source and say which layers it covers. Add (e) to Table 12. Add to Table 17 the erased-score intervals and the shuffled chance, both in VIEW_ERASURE.md.
- **Cost.** Already in saved results.

**F1.15 [COULD]** · §8 paragraph 2 ("a second, independent and label-free view")
- **What is wrong.** The sentence is not tested, and it is not accurate as written:
  - The setup was chosen on labels, so the view is not label-free.
  - The document never shows that this view adds anything to the human reading.
- **Why it matters.** It is the one practical use the conclusion offers for the thesis, and there is no evidence for it.
- **What to do.** Either cut the sentence, or test it. A test: are the 35 aircraft whose drawing label disagrees with the whole-patent reading (the "not visible in the figure" cases) more often misread by kNN, or further from their class centre, than the other 627? If yes, the embedding can flag hard or ambiguous drawings, and that is a supported claim.
- **Cost.** CPU recompute.

---

## Overall verdict on the organisation of ideas

1. The document opens on its question and closes on an answer to it. Table 1 is a good spine, and results then comparison is the right order.
2. The ruler comes after the measurements: §3 (protocol) follows §1.4 and §2, which already use it. Moving §3 forward and Table 6 back fixes most of the reading friction.
3. The headline is respected in §0 and §8. The secondary question (drawings against photos) is settled too early in §0 and §8, though §10 still lists it as open and its test is underpowered.
4. Caveats are carried in the results sections but lost on the way to §8. The lost ones are: the post hoc model choice, the crop test run on base only, the in-sample-only erasure, the single labeller, and the different label schemes. §9 misses the first three.
5. §8 spends more space on contributions and a recipe than on the secondary answer, and it adds two untested explanations (PTC/DS/SRW, "label-free second view"). Trim these, or back them with the CPU analyses above.
