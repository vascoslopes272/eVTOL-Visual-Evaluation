"""Chapter 5 — the two tables of the methods chapter, built from the live numbers.

Table 5.1 reads its values from the same variables the sections of chapters 2 to 4
use (:func:`numbers.live`), so it cannot go stale. Table 5.10 lists the three
choices that rest on judgement; its wording is fixed text.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd


def settings_table(n: Dict) -> pd.DataFrame:
    """Table 5.1 — what the preliminary analysis fixes for the evolution analysis."""
    rows = [
        ("unit counted", "2.2", f"the unique aircraft, {n['unique']}, and not the patent"),
        ("years compared", "2.1.3",
         f"to {n['complete_to']} for counts; to {n['year_max']} for shares, within region"),
        ("one independent design", "2.2.1, 3.1.2",
         "the aircraft, O1 and O2 removed, S3 counted as new"),
        ("design species", "3.3.6",
         f"A1t: architecture class by wing count by any tilting unit, {n['a1t_distinct']} archetypes"),
        ("informative fields", "3.3.4",
         f"{n['informative']}, with the {n['near_constant']} near-constant ones held out of the distance"),
        ("a blank", "3.3.2",
         "absence, dropped from a comparison instead of counted as difference"),
        ("thin evidence", "3.2.4", f"{n['sens']} aircraft, marked and carried, never removed"),
        ("labels hold", "4.1",
         "they agree with the public product wherever the product is public"),
    ]
    return pd.DataFrame(rows, columns=["choice", "fixed in", "value"])


def judgement_table(n: Dict) -> pd.DataFrame:
    """Table 5.10 — the three choices that rest on the author's judgement."""
    rows = [
        ("archetype level (3.3.6)",
         "A1t, architecture class by wing count by any tilting unit, because booms are "
         "structure and allocate no function",
         "A1 or A1b, both of which keep the singleton count inside the same regime",
         "the design-species row of table 5.1, the archetype paragraph of 5.3, condition 1 "
         "of 5.7, and every curve of 5.5 that is drawn at the counting level"),
        ("field weights in the distance (5.3)",
         f"one unit per subsystem, because {n['slots_M3']} propulsion slots against "
         f"{n['slots_G1']} architecture slots records the codebook and not the aircraft",
         "uniform weights, the conventional default for Gower's coefficient",
         "which of the two weightings is the main result and which is the robustness run; "
         "the curves themselves are computed both ways regardless"),
        ("the balance condition (5.7)",
         "²D falls outside the permutation band of the earliest windows",
         "a fixed cutoff such as two designs in play, as used in parts of the "
         "dominant-design literature",
         "the wording of condition 2, and whether the convergence verdict rests on a "
         "constant or on this corpus"),
    ]
    return pd.DataFrame(rows, columns=["choice", "taken here", "the alternative",
                                       "what changes if it flips"])


REFERENCES = [
    "Abernathy, W. J. and Utterback, J. M. (1978), \"Patterns of industrial innovation\", "
    "*Technology Review* 80(7), 40–47.",
    "Gower, J. C. (1971), \"A general coefficient of similarity and some of its properties\", "
    "*Biometrics* 27(4), 857–871.",
    "Hill, M. O. (1973), \"Diversity and evenness: a unifying notation and its consequences\", "
    "*Ecology* 54(2), 427–432.",
    "Rao, C. R. (1982), \"Diversity and dissimilarity coefficients: a unified approach\", "
    "*Theoretical Population Biology* 21(1), 24–43.",
    "Stirling, A. (2007), \"A general framework for analysing diversity in science, technology "
    "and society\", *Journal of the Royal Society Interface* 4(15), 707–719.",
]
