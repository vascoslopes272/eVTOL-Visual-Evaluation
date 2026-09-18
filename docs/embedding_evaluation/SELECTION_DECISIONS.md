# Figure Selection — Decision Register

This register records which figures enter the embedding pipeline, and why.

- **Rule values:** the `selection:` block in `eVTOL-Embedding-Extraction/config.yaml`.
- **Applied by:** `eVTOL-Embedding-Extraction/notebooks/20_figure_selection.ipynb`, which uses only the labels and opens no image.
- **Reported in:** section 0 of [embedding_evaluation_report.md](embedding_evaluation_report.md).

When a rule changes, add a dated entry here, re-run notebooks 20 → 21 → 22, then re-run `30_embedding_evaluation`.

**Input:** Stage 04's tables, `1639_LABELLED/0_labelling/outputs/tables/` (`aircraft_table.csv`, `figure_table.csv`) and `outputs/images/<aircraft_id>/`; outputs go to `1639_LABELLED/2_embedding_extraction/` (layout of 2026-09-17; aircraft_uid = `<patent>_ua<N>`). The label source is `master_04`, in use since 2026-09-15.

**Unit of analysis:** the **aircraft**. This is a primary approved variant of a patent, identified by `aircraft_uid = <patent_id>#<variant>`. The labelling evaluation uses the same unit, so both stages analyse the same 685 aircraft.

---

## Fixed gates

Every figure set passes these gates, in this order. Each figure is counted under the first gate that removes it.

| # | Gate | Rule | Decided | Why |
|---|---|---|---|---|
| G1 | Figure approved | T2 `status = approved` | wizard review | Only figures the labeller accepted as usable. |
| G2 | Image file exists | `approved_copy_path` exists on disk | 2026-09-16 | The file has to be there to be embedded. |
| G3 | Patent / aircraft approved | T1 `isApproved` | wizard review | Rejected records carry no morphology. |
| G4 | Domain gate | Drop an aircraft with `UAVSimilar`, `ElectricSimilar` or `STOLSimilar` in `edgeTags` | 2026-09-15 | Only electric, vertical-take-off, non-UAV aircraft are in scope. This is the same gate as the Preliminary Analysis, applied per aircraft. V/STOL, Hybrid and Unknown powertrains carry no tag and stay. |
| G5 | Duplicates | Drop D1/D2 patents (`is_primary = False`). D3 stays (`exclude_dup_types: []`). | 2026-09-09 | A D1/D2 duplicate is the same aircraft as its original and inherits its labels, so embedding it again would count one design twice. A D3 is a variant with its own labels. |
| G6 | One figure per file | When two figure rows of a patent point at the same file, keep the main row, otherwise the first | 2026-09-16 | Wizard record error on CN114684361A (a `crop_1` row points at `crop_0`), found by notebook 20. The same image must not be embedded twice. Fix it in the wizard. |
| G7 | Whole aircraft only | T2 `parts` starts with `Whole Vehicle Layout` | 2026-09-15 (refinement 3) | Detail views (tilt hinge, rotor blade) do not show the architecture being compared. |
| G8 | Quality / style | `exclude_quality: []`, `exclude_styles: []` | open | Off for now. Candidates to test: drop `poor_quality`, or drop `Render`/`Draft`. |
| — | Human-uncertain | `exclude_uncertain: false` | open | Off for now. It can be turned on as a sensitivity run. |

**Result on 2026-09-16:** 5,840 figures on file → **1,584 figures of 685 aircraft**. The removals were:
- 3,927 figures not approved;
- 2 figures of patents that were not approved;
- 261 figures removed by the domain gate (189 UAV, 69 not electric, 3 STOL only);
- 46 D1/D2 duplicates;
- 1 image file listed twice;
- 19 detail views.

---

## Selection strategies (figure sets)

The fixed gates leave one pool of eligible figures, and each strategy builds one **named figure set** from it. Every set holds at most one figure per aircraft, except `all`.

When an aircraft has several matching figures, one is picked in this order:
1. the main image;
2. the perspective order `Front-Isometric, Rear-Isometric, Side, Front, Top, Back, Bottom/Down`;
3. quality `clean`;
4. figure order in the patent.

If an aircraft has no matching figure, it is **left out** of that set (there is no fallback), so each set stays pure. Table 0.3 of the report shows who is missing.

| Set | Rule | Question it answers | Aircraft (2026-09-16) |
|---|---|---|---|
| `main` | the labeller's main image | Baseline: the figure chosen as representative at labelling. | 685 |
| `all` | every eligible figure | Do several views per aircraft help, or add view noise? | 685 (1,584 figures) |
| `hover` | `acState = Hover` | Does the hover configuration show the architecture best? | 335 |
| `cruise` | `acState = Cruise` | … or the cruise configuration? | 314 |
| `hovercruise` | `acState = HoverCruise` (invariant) | Aircraft whose layout does not change between modes (mostly SLC, MR). | 278 |
| `per_front_iso` | `per = Front-Isometric` | The viewing-angle confound (ARI 0.288 in the supervisor report), one angle at a time. | 483 |
| `per_side` | `per = Side` | Same question, side view. | 197 |
| `per_top` | `per = Top` | Same question, top view. | 269 |
| `line_only` | `acSty = Line Drawing` | Removes drawing style (renders, drafts) as a confound. | 663 |
| `state_by_type` | the flight state that shows each topType's defining feature | For example, a tilt-wing (TW) with its hover configuration visible. | **pending** |

### Pending: the `state_by_type` table

This decision is open and is yours to investigate. For each topType (TW, TR, CVT, TB, SLC, MR, PTC, HB, RC, PFV, SRW, DS), decide which `acState` values (Hover / Cruise / HoverCruise / Transition) best show what defines that type. The set is skipped while the table is empty.

---

## Comparing strategies

- **Compare pairs, not all sets at once.** Only 2 aircraft appear in all 9 sets. Compare two strategies on the aircraft both of them cover (e.g. `hover` vs `cruise`), or use `metrics.aircraft_scope: common` on a smaller list of sets.
- **Select on one half, report on the other.** The eligible aircraft are split 50/50, stratified by topType (`split` in `selection/aircraft.parquet`: 345 `select`, 340 `report`, seed 42). Choose the best strategy on `select` and report its result on `report`. Choosing and reporting on the same aircraft would overstate how good the choice is.
- **Label-free metrics do not settle the choice.** Integrity, structure vs. random and clustering describe each set's geometry, but set size and coverage differ between sets. Whether a strategy's images recover the labelling better needs the comparison against the labels, which is not built yet.

## Image processing (notebook 21)

Processing runs after selection and is not part of it, but it defines what the model sees.

| Setting | Value | Why |
|---|---|---|
| Source | `approved_images/` raw crops | Every batch is present there (the older 02b 518 px set covers only B01/B05). |
| Rotation | labelled `rotation_deg`, clockwise | Same convention as the wizard and `Patent-Labelling-Tools/src/processor.py`. 59 of the 1,584 figures are rotated. |
| Resize + pad | long side = size, LANCZOS, padded to a white square | The aspect ratio is kept, and nothing is cropped away. |
| Sizes | 224 and 518 | 518 is DINOv2/14's hi-res input (37×37 patches); 224 is its default. Size is compared like a strategy. Upscaled figures: 2 at 224, 64 at 518. |
