"""The text common to every question of the thesis chapter (notebook 47): the dataset paragraph of the Methodology,
the one statistics table, the Limitations and the organisation of chapter 4, all as itemised blocks.

Markup as THESIS_CONTRACT.md §1: ``{key}`` is a number from ``thesis_common.numbers(ctx)`` (never typed),
``[tab:name]`` a table reference, paragraphs separated by a blank line; a line starting with ``- `` is a list item.
Wording follows the author's rules (contract §2): his voice, British English, no em dashes, no explanatory colons.
"""
from __future__ import annotations

from viz.thesis import QUESTIONS

# ------------------------------------------------------------------------------------------ the dataset (≤ 8 lines)
METHOD_COMMON = """- **Patents:** {acquired_s} acquired from PatSeer, snapshot {snapshot}; {representative_s} show an electric VTOL aircraft in their drawings.
- **Aircraft:** {unique_s} unique aircraft, an aircraft drawn in several patents counting once; [fig:common_data_flow] shows the four ground files joined into the one table every question reads.
- **Unit of analysis:** the unique aircraft, dated by the priority year of its first patent.
- **Labels:** the wizard labels of chapter 3, read under its codebook; class, propulsors, wings, booms, tilting.
- **Windows:** trends run over the complete windows {sm_windows}; years from {partial_start} are still filling and are hatched in the figures.
- **Publication lag:** median {lag_median_lo} to {lag_median_hi} years, 90th percentile {lag_p90} years. No trend is read past {last_complete}.
- **Regions:** {sm_region_n}, by the applicant's address; North America, Europe and Asia-Pacific.
- **Classes:** {sm_class_n} codebook classes, folded to {sm_class5_n} for the comparisons between classes."""

# ------------------------------------------------------------------------------------------ the statistics table
#: one row per test: what it answers, its formula in plain unicode, and the questions that use it.
STATS = [
    dict(test="Wilson interval",
         answers="the range of the true share read on n aircraft; n becomes n(N − 1)/(N − n) when drawn from "
                 "the N = {unique_s} aircraft",
         formula_unicode="(p̂ + z²/2n ± z·√(p̂(1 − p̂)/n + z²/4n²)) / (1 + z²/n), z = {sm_wilson_z}",
         used_in="Q4 (drawing against public aircraft, {sm_pw_img_pub} of {sm_pw_n}; the TRL and index-firm subsets)"),
    dict(test="Chi-square, Fisher exact",
         answers="whether two categories are related; Fisher for a small 2 × 2 table; detected below p {sm_alpha}; "
                 "a residual past ±2 names the cell",
         formula_unicode="χ² = Σ (O − E)² / E; Fisher, the hypergeometric p; residual (O − E) / √(E (1 − rᵢ/N)(1 − cⱼ/N))",
         used_in="Q1, Q2, Q3, Q4 (residuals), Q7"),
    dict(test="Mann-Whitney U",
         answers="whether a number, for example propulsor units, runs higher in one group than in another, over "
                 "every pair drawn one from each",
         formula_unicode="U = the number of pairs (i, j) with xᵢ above yⱼ; p from the rank sum",
         used_in="Q4"),
    dict(test="Spearman ρ",
         answers="the trend of a number with another, usually the priority year; +1 always rises, −1 always falls; "
                 "{sm_trend_min} aircraft or more, detected below p {sm_alpha}",
         formula_unicode="ρ = 1 − 6 Σ dᵢ² / (n (n² − 1)), dᵢ the rank difference of aircraft i",
         used_in="Q3, Q5 (funding of the index firms), Q6, Q7"),
    dict(test="Permutation band and test",
         answers="what chance alone gives; aircraft dealt into the windows at random {sm_perms} times (seed "
                 "{sm_perm_seed}), middle 95 % kept; p the share of shuffles as extreme as the real value",
         formula_unicode="band = the 2.5th to the 97.5th percentile over {sm_perms} shuffles; ²D rarefied to {sm_perm_n} "
                         "aircraft per window; p = #(shuffle ≥ real) / shuffles",
         used_in="Q7 (conditions 2 and 3), Q6 (discovery curve, {sm_discovery_orders} random orders), Q3 (entry lag "
                 "the same in every class)"),
    dict(test="Gower cohesion, Rao's Q",
         answers="how alike the aircraft of a window are; d is 0 for the same answer, 1 otherwise; ΔQ the "
                 "fall against the two earliest windows",
         formula_unicode="d(i,j) = Σₖ wₖ δₖ dₖ / Σₖ wₖ δₖ over the labels k; Q = (1/N²) Σᵢ Σⱼ d(i,j)",
         used_in="Q7 (condition 3)"),
    dict(test="Log-linear doubling time",
         answers="how fast a yearly count grows; the ratio of two doubling times compares eVTOL with a baseline, "
                 "an interval taking in 1 meaning no difference",
         formula_unicode="ln(countₜ) = a + b·t over {sm_fit_lo} to {sm_fit_hi}; doubling time = ln 2 / b",
         used_in="Q1"),
    dict(test="Hill numbers ¹D, ²D and Chao1",
         answers="how many designs are in play; ¹D weighs each archetype by its share, ²D the large ones more, "
                 "both read at {sm_perm_n} aircraft; Chao1 a floor on the unseen",
         formula_unicode="¹D = exp(−Σ pᵢ ln pᵢ); ²D = 1 / Σ pᵢ²; Chao1 = S + f₁(f₁ − 1) / (2(f₂ + 1))",
         used_in="Q6 (archetype sets, discovery curve), Q7 (condition 2), Q2 (²D as the effective number of filers)"),
    dict(test="Bootstrap interval",
         answers="the range of a fitted value when the aircraft are a sample; rows redrawn with replacement "
                 "{sm_boot_draws} times (seed {sm_perm_seed}), the middle 95 % kept",
         formula_unicode="interval = the 2.5th to the 97.5th percentile of the statistic over {sm_boot_draws} resamples",
         used_in="Q1 (ratio of doubling times, turning point with {sm_turn_draws} residual resamples), Q3 (entry lag "
                 "per class and region)"),
]

# ------------------------------------------------------------------------------------------ limitations (≤ 6 lines)
LIMITATIONS = """- **Drawn, not claimed:** the labels record what a drawing shows; claim scope and white space stay out of reach.
- **Mission:** not a label; known only for the {sm_pw_n} aircraft with a public page. Those differ from the rest on {sm_linked_fail_n} of {sm_rep_attr_n} attributes.
- **Legal status:** a snapshot, alive or dead at the export date; time to abandonment cannot be drawn.
- **Not in the dataset:** hybrid aircraft, certification, autonomy, occupancy, noise, size, mass and battery energy; [tab:q7_cannot_answer] lists the stakeholder questions these gaps leave open.
- **Too few:** most firms file once, so a shakeout and firm design paths cannot be read; the patent-to-flight lag per class rests on {sm_ff_firms_n} firms spread over {sm_class_n} classes.
- **Not run:** the centre of the label space per window against a shuffled-year band, and citations between the aircraft of the corpus."""

# ------------------------------------------------------------------------------------------ chapter organisation (≤ 5 lines)
#: the three parts in the order of thesis.QUESTIONS, each with its question ids; built from QUESTIONS so the map cannot
#: drift from the index.
_PARTS = []
for _qid, _slug, _part, _question in QUESTIONS:
    if not _PARTS or _PARTS[-1][0] != _part:
        _PARTS.append((_part, []))
    _PARTS[-1][1].append(_qid)
_WORDS = {3: "three", 7: "seven"}
_SUBS = "A to D"


def _ids(ids: list) -> str:
    return f"{ids[0]} to {ids[-1]}" if len(ids) > 2 else " and ".join(ids)


CHAPTER_MAP = "\n".join([
    "The chapter answers the seven questions of the index on the {unique_s} unique aircraft of chapter 3, "
    "in three parts, and closes with the limits of the dataset.",
    "",
    "- **Methodology:** first; the dataset, the statistics table and, per question, a five-line Method with its flowchart ([fig:common_chapter_flow]).",
    f"- **Parts:** {_WORDS[len(_PARTS)]}, in the order of the index; "
    + "; ".join(f"{p[0].lower()}{p[1:]} ({_ids(ids)})" for p, ids in _PARTS) + ".",
    f"- **Questions:** {_WORDS[len(QUESTIONS)]}, one section each, Q1 to Q{len(QUESTIONS)}; sub-questions lettered {_SUBS} within a question, each stating its results, then what they rest on.",
    "- **Answer box:** one per question, the answer in a few sentences with its numbers; the box closes the section.",
    "- **Appendix:** one block per question with the supporting figures and tables, a caption and one takeaway line each.",
])

__all__ = ["METHOD_COMMON", "STATS", "LIMITATIONS", "CHAPTER_MAP"]
