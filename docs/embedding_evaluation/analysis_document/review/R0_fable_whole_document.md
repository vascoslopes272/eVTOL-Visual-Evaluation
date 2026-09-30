# R0. Whole-document read (Fable, 2026-09-30)

Flags on ANALYSIS.md (outline version, 27 pp). Severity: MUST = a jury would attack it or a
claim is not supported as written; SHOULD = clearly strengthens the document; COULD = polish.

## Robustness

**F0.1 [MUST]** · §6, Table 22 · The class-mix check changes pool size AND class mix at once
(200 photo subsets of 663 at the drawings' counts). The text then says "most of the +0.12 comes
from the larger and more balanced pool", but the two effects are not separated · A jury will ask
which one it is · Add the size-only control: 200 photo subsets of 663 drawn at the PHOTOS' own
class mix. If size alone explains the drop, say so; if mix does, say so · CPU, same code
(setup_selection fairness), minutes.

**F0.2 [MUST]** · §2.2 · "The model choice was fixed in advance on the attention artifact, and
the held-out rule confirms it" is not the history: the switch to registers was decided after the
registers check showed both the attention fix AND the higher scores · The rules say a choice
made after seeing numbers is labelled post hoc; a reader who finds out otherwise loses trust ·
Reword: the registers checkpoint was motivated by the attention artifact, adopted after the
check of 2026-09-30 showed the collapse gone and the scores higher (post hoc on the scores), and
the held-out rule then confirms it · wording only.

**F0.3 [MUST]** · §5.3 · The crop test is the one base-model result; the chosen model is
untested for background sensitivity · The setup section claims robustness "without the photo
backgrounds" (§8) for a model on which it was not run · Re-embed the existing crops with the
registers model and repeat the paired test (crops already on disk) · GPU ~10 min + CPU.

**F0.4 [SHOULD]** · §2.4 · The thickening variants are also greyscaled (210 of 1 545 drawings
carry colour), so "thick1 − plain" mixes two changes · Either add a greyscale-only drawing
variant (separates the two) or state in the table note that the thick variants remove colour
too and that the 210 coloured drawings were checked separately · GPU ~10 min, or wording.

**F0.5 [SHOULD]** · §6 · The photo label is the directory's class and agrees with the codebook
parent for 83 of 99 linked aircraft (84 %). This bounds every cross-source comparison but is said
only in §1.3 and §9, not where the comparison is made · Put one sentence in §6's opening: the two
label sources agree on 84 % of the aircraft that carry both, so differences below that order are
not interpretable as medium · wording.

**F0.6 [SHOULD]** · §6.1 · The 94 matched aircraft are the named, mostly built aircraft with a
public page: a biased subset (better photos, more images) · The matching numbers may not transfer
to the corpus · State the bias in one sentence; optionally report matching restricted to concept
aircraft · already in saved results (status column).

**F0.7 [SHOULD]** · §2.1 · The decision rule pools the two sources (frequencies averaged within
a source, then over sources). For the photos, L22 CLS won 40 % of selections. Choosing ONE setup
for both sources is the author's ruling (fair comparison needs the same readout) and should be
stated as a decision, not hidden in the averaging · wording.

**F0.8 [SHOULD]** · §4.1 Table 16 · Per-class recall without intervals; the rules ask for a
Wilson interval on shares with a finite base · Add Wilson intervals (or a bar chart with them)
and grey out classes under 20 aircraft · CPU trivial.

**F0.9 [COULD]** · §2 resolution row · 224 px base embeddings exist; the author ruled no
comparison. One line "224 px was extracted for the base model and not compared, by decision"
pre-empts the question · wording.

**F0.10 [COULD]** · Table 8 says 665 drawings (attention run) while the analysis set is 663 ·
Explain the 2 (the unclassifiable aircraft were in the attention run) or recompute on 663 ·
CPU trivial.

## Missing graphs

**F0.11 [SHOULD]** · §2.2 Table 9 · Registers vs base on three label sets with paired CIs is a
picture, not a table: paired dots with interval bars · replaces the table · CPU.

**F0.12 [SHOULD]** · §4.1 Table 16 · The 12-class recall per type with n is the document's most
concrete class-level result and has no chart (the 5-class one, Figure 14, exists) · bar chart
with n under each bar and the 20-aircraft line · CPU.

**F0.13 [SHOULD]** · §4.4 Table 17 · Before/after erasure with the variance-matched control is
a paired dot chart; the table hides that the control costs the same · CPU.

**F0.14 [COULD]** · §2.6 · Optimism gap: show in-sample vs held-out as two markers per candidate
on Figure 5 rather than a separate table · CPU.

**F0.15 [COULD]** · §5.3 · The photo image rules (hero / random other / mean of all) are prose
only, while the drawings' rules get Table 18 · one small table or one figure for both · CPU.

## Organisation of ideas

**F0.16 [MUST]** · §2 before §3 · §2 uses kNN-5, maker held out, bootstrap, split-half before
§3 defines them · definitions must precede use (rules §2) · the brief format fixes it: methods
box at the head of the first results chapter, the split-half rule defined in §2's Method ·
structural.

**F0.17 [SHOULD]** · §7 · The author's own reading (layer 18 traces every line, layer 24
selects the parts that tell types apart; only layer 24 carries the architecture: 0.118 vs 0.235)
is the argument that ties the attention section to the layer choice, and it is not made ·
add two sentences and cite the L18/L24 scores; it turns §7 from a picture into evidence ·
wording.

**F0.18 [COULD]** · §0 Table 1 vs §8 first paragraph · the conclusions repeat the summary
table row by row · in the brief format the Answer boxes replace both · structural.

**F0.19 [COULD]** · §1.2 Table 5 (flight state counts) · answers nothing the text does not say
in one sentence ("state barely moves the vector choice: 26 aircraft") · drop per rules §4.

**F0.20 [COULD]** · Appendix · file paths, script names and 3-D links point out of the
document · rules §1 · the reformat drops them.

## Verdict on the organisation

The document runs setup → results → comparison → conclusion, which is right, but definitions
trail their first use, the headline claim (drawings carry the architecture, weakly, and it
survives every control) is diluted by the summary table's seven equal rows, and the strongest
new finding (the photo advantage is mostly the pool) sits in §6 without the size-only control
that would make it safe. The brief format (question chapters, Method before Results, Answer
boxes) resolves the first two; F0.1 and F0.3 resolve the third.
