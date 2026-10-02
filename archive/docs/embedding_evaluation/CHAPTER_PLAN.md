# DINOv2 Chapter — Plan and Decision Register

2026-09-30. Working plan for the thesis chapter on the DINOv2 embedding analysis, fixed with the
author's rulings of 2026-09-29/30. The two source reports are `PATENT_EMBEDDING_ANALYSIS.md` (this
folder) and `EVTOLNEWS_EMBEDDING_ANALYSIS.md` (EVTOLNEWS_DS, private). This file is the register:
what the chapter claims, what is already computed, what still gets computed, and in which order.

## 1. What the chapter claims

- **Headline (a):** can a frozen, general-purpose vision model (DINOv2) recover the eVTOL
  architecture taxonomy from patent drawings? The answer is quantified, whichever way it points.
- **Secondary (c):** the same protocol on real-world photographs (evtol.news), and the comparison:
  where does the visual architecture signal actually live?
- (b) the labelled image benchmark itself is a by-product, mentioned, not the headline.
- This chapter fills the reserved slot (chapter M / RQ4). **Reword approved (author,
  2026-09-30):** "Method (RQ4): does the figure alone carry the architecture — read by a frozen
  vision model on patent drawings and real photographs, judged against the human labels."
  (Old wording: "does the figure alone carry the architecture the text states.")
- Well-supported negative results are findings and stay in (author ruling: "good" means
  well-supported, not positive). Weak or uninteresting side results are compared briefly, not
  developed (e.g. matching, if it stays unconvincing).

## 2. Chapter skeleton (fixed)

Classic Method → Results → Discussion, not the per-sub-question format of the Labelling Analysis.
**Title (author, 2026-09-30): "Visual Learning: DINOv2 embeddings of patent drawings and
photographs".**

- **X.1 Method**
  - X.1.1 The tool: frozen DINOv2 (model choice; layer/token chosen by a stated rule, L24 CLS;
    why frozen, no fine-tuning).
  - X.1.2 From approved figures to model inputs. Patents: label-driven figure selection funnel
    (nb20), rotation / resize / white-pad to 518 px (nb21), the monochrome question. Photos: the
    post-filter processing and the crop question. (The PatSeer→wizard import, the labelling wizard
    and the evtol.news crawl+filter live in the Methodology chapter, not here.)
  - X.1.3 One vector per aircraft: the four rules (exp1 view-first, exp2 state-first, exp3 main
    figure, exp4 view average), the canonical state, and the role of the acState "Both" label.
  - X.1.4 Evaluation protocol: T1–T7, kNN-5 balanced accuracy with the maker held out, bootstrap
    CIs, shuffled chance, probes, k-means ARI, permutation tests.
- **X.2 Results: patent drawings** (soundness; 12-class separation; view dominates architecture;
  what else is encoded; does the image choice matter, incl. the exp4 slots sub-question — kept for
  now, dropped later if it stays a null).
- **X.3 Results: photographs** (same protocol; crop check result).
- **X.4 Drawings vs photographs** (the shared 5-class bridge; same-aircraft matching if it earns
  its place).
- **X.5 What the model attends to** (L18 attention maps on a chosen subset; the register-token
  artifact; dinov2-with-registers check).
- **X.6 Discussion and limitations.**

## 3. Already computed (reuse, do not redo)

- Shared protocol T1–T7 + layer rule, both sources, 518 px: the two reports of 2026-09-22.
  Key numbers: L24 CLS wins both; patents G1 12-class kNN 0.18 (chance 0.10 shuffled), probe 0.32;
  view d / G1 d = 2.2; same 5 classes patents 0.33 vs photos 0.53 (probes 0.57 vs 0.65);
  photos mean-of-all-images 0.55; k-means ARI photos 0.145 vs patents 0.03.
- Matching patents↔photos: R@10 20 %, R@50 37–38 % (no line drawings), vs random 1.5 / 7.5 %.
- 3-D pages (2026-09-30): `PATENT_UMAP_3D.html` (new, 12-class G1 + 5-class parent + exp4) beside
  `EVTOLNEWS_UMAP_3D.html`; links docx in "Embedding Analysis brief/current/".
- No 224-vs-518 or pad-vs-crop ablation for the drawings: preprocessing choices are stated and
  cited, not re-derived (author ruling, 2026-09-29).

## 4. New work items (the only new computation)

| # | Item | Objective | Status |
|---|------|-----------|--------|
| N1 | Photo crop test (subagent) | does background removal change the 5-class signal? detector + re-embed + kNN vs CI | DONE 2026-09-30: NO — full main set (1 157), OWLv2 crops (3.7 % fallback), L24 CLS 0.534→0.550, paired diff +0.017 [−0.008, +0.043] inside CI; only L24 patch-mean clears zero (+0.034). Uncropped photos are representative; becomes a robustness paragraph in X.3. `EVTOLNEWS_DS/3_embedding_evaluation/crop_experiment/RESULTS.md` |
| N2 | dinov2-with-registers check | fixes the L22/L24 attention collapse? does the taxonomy score move? | DONE 2026-09-30: YES twice — collapse gone (median max-patch share L24 0.30→0.01, mass absorbed by the register tokens) AND the drawings' scores rise significantly (G1 12-class 0.178→0.235 [+0.008,+0.103]; parent 5-class 0.333→0.445; photos +0.030 borderline). L24 CLS stays the best matrix under both models. Model decision deferred (author 2026-09-30): BOTH report versions now exist — registers twins built overnight (PATENT_EMBEDDING_ANALYSIS_REGISTERS.md/.pdf, EVTOLNEWS twin in embedding_analysis_registers/, PATENT_UMAP_3D_REGISTERS.html; base outputs verified untouched; twins carry a base-vs-registers comparison table after the Summary). Registers matching also better: R@10 22 %, R@50 48 % (base 20/37). Decide by comparison, then N4. `registers_check/REGISTERS_CHECK.md` |
| N3 | Monochrome preprocessing check | drawings: does a preprocessing variant (contrast / fill) move the score? small, only if cheap | open, may drop |
| N4 | Attention-map figure set | L18 maps on ~2 aircraft per class, both sources, for X.5 | open |
| N5 | Same-aircraft matching, final read | keep in X.4 or reduce to one paragraph | decide after triage |
| N6 | View-erasure test | does architecture survive removing the viewpoint? | DONE 2026-09-30: YES — base model unchanged (+0.005/+0.010, CIs include 0); registers drops −0.043/−0.079 but stays far above chance, and a variance-matched random removal costs the same, so the loss is high-variance removal, not view specifically. View probe 0.78–0.79 → chance on the scored figures. NOTE for the model decision: after erasure base ≈ registers — the registers advantage sits in dominant, view-shared directions. Caveats: linear erasure only (view kNN stays ~0.55–0.62), exact only on the fitted figures. `1639_LABELLED/3_embedding_evaluation/view_erasure/VIEW_ERASURE.md` |

### 4b. Setup selection (author rulings 2026-09-30 midday)

- **Model: registers** (dinov2-with-registers-large). **Resolution: 518 px**, the model's largest
  training size; no 224 check (author: compute allows 518, so 518).
- Two kinds of choices. **Image-type choices** (model, resolution, view handling, drawing
  preparation) are justified by what patent drawings are, so they transfer to other
  patent-drawing studies. **Label-selected choices** (layer, token) are chosen on half the makers
  and confirmed on the other half.
- **One model and readout for both sources** (registers, 518, layer and token from the held-out
  rule). Each source's **image preparation** may differ, chosen by the same held-out rule from a
  candidate set fixed in advance: drawings {plain, lines +1 px, lines +2 px at the 518 px input};
  photos {colour, greyscale} (greyscale doubles as the fairness check: is the photo advantage
  colour?). Crop already tested (no effect).
- Thesis: one short setup section (option table, rule, result) and one short comparison section.

| # | Item | Status |
|---|------|--------|
| S1 | Held-out selection of model/layer/token, both sources | DONE: registers L24 CLS (69 % of selections; registers 68–90 % vs base); optimism gap 0.02–0.04 |
| S2 | Drawing line thickening (was N3) | DONE: plain kept; thick2 significantly worse (−0.05/−0.10), thick1 −0.03/−0.04 n.s.; montage shows thickening fills fine detail. Note: "thick1" = each stroke side +1 px (≈ +2 px width); a gentler variant was not in the fixed set |
| S3 | Greyscale photos | DONE: grey = colour (+0.006, n.s.); colour kept; photo advantage over drawings survives greyscale (+0.12 both) |

Result record: `1639_LABELLED/3_embedding_evaluation/setup_selection/SETUP_SELECTION.md`.
**Chosen setup: registers · 518 px · layer 24 CLS · drawings plain · photos colour.**

**Review round 2026-09-30 evening:** 7 reviews merged in `analysis_document/review/
CONSOLIDATED_FLAGS.md` (11 MUST, 16 SHOULD, 10 COULD). Author: "do all", page cap 35 (Word).
Decisions taken as recommended: three-number headline (0.23 / ~0.21 after optimism / 0.18
pre-planned model); matched comparison is the headline after the size-only control; the
"propulsion movement" explanation is tested (size-balanced per-class reading) and cut if
unsupported; one labeller stated, κ 0.866 frozen and 0.94 after the author's re-reading;
thickening grey/contrast controls run; Table 5 dropped. Document reformatted to the Labelling
Analysis brief format (question chapters, Method in five parts, Results and discussion, Answer
boxes, methods box, in-panel sources, nothing pointing out).

**Review fixes integrated 2026-09-30 evening:** all 37 flags applied to the brief-format document
(26 pp in Word, cap 35): three-number drawing headline (0.235 / about 0.21 / 0.178 base), matched
photo comparison as the chapter 5 answer, maker intervals for every paired contrast (none survives
Holm over 25), preparation verdict from the grey/contrast controls, per-class zero of PTC shown to be
class size. Base attention recomputed on the 665 main-set drawings (shares unchanged). Reproducible from
`embedding_evaluation/notebooks/32_setup_selection_and_analysis.ipynb` (`src/setup_analysis.py`).

**Analysis document built 2026-09-30** (27 pp, outline format, superseded by the brief-format rebuild): `Embedding Analysis brief/current/Embedding
Analysis — Visual Learning (private).docx`; source `docs/embedding_evaluation/analysis_document/
ANALYSIS.md`; generator `embedding_evaluation/scripts/build_analysis_document.py`. Open ruling:
the photo advantage mostly vanishes when photos are matched to the drawings' size and class mix
(0.463 [0.367, 0.557] vs 0.445).

## 5. The two documents (deliverable = results, advisor never reads method detail)

1. **Embedding Analysis** — ≤ 20 pages, tables+figures first, built by a generator (every number
   computed, nothing typed), merging the two reports around the chapter skeleton above.
2. **Summary for the advisor** — results only, takeaway-per-figure style like the Labelling
   Analysis brief; Word file into "Embedding Analysis brief/current/", same current/comments/archive
   convention as the Labelling Analysis brief folder.

## 6. Two-day order of work

- **Day 1:** N1 lands; N2 + N4 (one GPU session); triage session on the two reports → the short
  list of "big things" for the chapter; decide N3/N5/N6.
- **Day 2:** build the Embedding Analysis document from the generator; then the advisor summary;
  author review pass.

## 7. Repo placement (two-pillar rule holds)

Extraction-side code (crops, registers, attention) → `eVTOL-Embedding-Extraction/src` + `scripts`;
evaluation-side code (metrics, pages, documents) → `embedding_evaluation/src` + `scripts`; documents
in root `docs/embedding_evaluation/`; data outputs under `1639_LABELLED/…` and `EVTOLNEWS_DS/…`.
New this session: `src/patent_3d.py`, `scripts/build_patent_3d.py`,
`1639_LABELLED/3_embedding_evaluation/umap_3d/`.
