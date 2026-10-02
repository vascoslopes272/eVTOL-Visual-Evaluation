"""Method texts for the brief (chapters 1-3), drafted 2026-09-26 from the author's Word comments.

DRAFT MODULE — nothing imports it yet. The coordinator wires each constant into ``sm_index``
(``CHAPTER_METHOD`` / ``METHODS_BOX`` / ``TEXTS``) and applies :func:`archetype_label` in
``print_format``. No import of ``sm_index`` here and no data is read: every corpus number is a
``{placeholder}``. Placeholders that do not exist yet are listed in :data:`NEW_PLACEHOLDERS`
with the rule that computes them; the ones already in ``sm_index.NUMBERS``,
``la_index.TAKEAWAY_NUMBERS``, ``_driver_numbers`` or ``_method_numbers`` are used as they are.
Method constants (the 50 % line, 0.05, 95 %) are typed, as in the current texts. The only other
typed numbers are the invented, labelled illustration in :data:`DIVERSITY_BOX` and the
author-facing figures of :data:`CLASS_RULES_PROPOSAL`, which is not for printing.

README — which constant answers which comment (REVIEW_2026-09-26_ch2_docx_comments.txt)
---------------------------------------------------------------------------------------
* ``STATS_BOX``            C39 (p and the four tests "not clear for a person who doesn't understand
                           a bit of this"), C80 (mean vs median). Replaces the "How to read the
                           statistics" box inside ``CHAPTER_METHOD["1"]``.
* ``DIVERSITY_BOX``        C40, C54 (what ¹D and ²D are, how they are computed, the difference),
                           plus rarefaction and the permutation band. Replaces the ¹D/²D and
                           permutation-band paragraphs of ``METHODS_BOX``.
* ``ARCHETYPE_METHOD``     C47 (decode "SLC · 1 · False"), C48 (no A2c: "many levels were built,
                           only the low effective numbers are usable; justify these three"), C49
                           (level codes C / W / U instead of A0 / A0c / A1t), C50 (reorganise),
                           C54/C56 (the family as one more level, family (b) only).
  ``LEVEL_CODES``, ``LEVEL_FIELDS``, ``VALUE_WORDS``, :func:`archetype_label`, :func:`level_name`
                           the code/label spec for ``print_format`` (C47, C49, C61).
* ``CONDITIONS_METHOD``    C41, C55, C64 (what each condition measures, so a reader can predict it;
                           condition 3 in particular), C41/C54 (what grouping classes does to the
                           test), C53 (condition 1 base left as a marked slot).
* ``ERA_FRAME_METHOD``     C51 (era of ferment / incremental change, radical vs incremental, as a
                           methodology frame, no results).
* ``GLOSSARY_TABLE``       C63, C69, C82, C90 (units, stations — which ones —, types, groups,
                           tilting joint groups, ducted unit).
* ``CLASS_RULES_TABLE_CURRENT`` / ``CLASS_RULES_TABLE_PROPOSED``
                           C63 (the per-class rules as a table, with the reason), printable.
* ``CLASS_RULES_PROPOSAL`` C63 (better rules for SLC / TR / CVT, with the modal shares under the
                           current and the proposed rules) — AUTHOR-FACING, not for printing.
* ``DRIVERS_METHOD``       C80, C81 ("never pooled"), C82 (tilting joint groups, the years read),
                           C89 (which drivers), C90 (types).
"""

# =============================================================================================
# 1 — STATS_BOX (chapter 1, head)                                               C39, C80
# =============================================================================================
STATS_BOX = (
    '<div class="methods-box">\n\n'
    "##### How to read the statistics\n\n"
    "*Written once for the whole document. Every p, interval, mean and median later on is read "
    "as set out here.*\n\n"
    "**What p is, from zero.**\n\n"
    "- A pattern in data can be real, or it can be luck. **p measures how easily luck alone "
    "would produce it.**\n"
    "- *Worked example.* Inside Tilt Rotor, the median number of propulsive units per aircraft "
    "goes from {sm_t_units_tr_first} in the earliest window to {sm_t_units_tr_last} in 2020-23. "
    "To ask whether that could be luck, picture the priority years written on cards, shuffled, "
    "and dealt back at random to the same Tilt Rotor aircraft. After the shuffle the year says "
    "nothing about the unit count, yet a few shuffles will still show a rise, by chance. **p is "
    "the share of such shuffles that show a trend at least as strong as the real one.** Here p "
    "is {sm_t_units_tr_p}: chance almost never produces this rise, so it is read as real.\n"
    "- *The same reading, the other way.* Inside Multirotor the median goes from "
    "{sm_t_units_mr_first} to {sm_t_units_mr_last}, which looks like a rise, but p is "
    "{sm_t_units_mr_p}: on so few aircraft, shuffled years produce a trend that strong too often "
    "to tell it apart from luck.\n"
    "- The tests compute p from a formula rather than by literally shuffling; the shuffle is what "
    "the number means. The permutation bands of the dominant-design test are the one place where "
    "the shuffle is actually run.\n\n"
    "**The line at 0.05.**\n\n"
    "- **p below 0.05** — fewer than one shuffle in twenty matches the real pattern: a "
    "difference, or a trend, is *detected*.\n"
    "- **p above 0.05** is written *no difference detected*, never *the same*. A small group can "
    "only reveal a large difference; a moderate one can be real and still go unseen.\n"
    "- **A p close to 0.05 is shown with both readings.** Whether an aircraft is out of force "
    "depends on its class at p {sm_fa_p} under one counting rule and p {sm_fa_p_sens} under "
    "another; both are printed and the result is called fragile.\n"
    "- **One in twenty by luck.** Where many traces are tested, about one in twenty that does not "
    "really move is expected to cross 0.05 by chance, so a single p just under the line in a long "
    "table is read with that in mind.\n"
    "- p never says *why* something moved, nor *how much*. The size is read from the values "
    "printed beside it.\n\n"
    "**The four tests: the question each one answers, with an example from this document.** "
    "Each aircraft enters a test once.\n\n"
    "| test | the question | used for | example here |\n"
    "|---|---|---|---|\n"
    "| Mann-Whitney U | Does one group tend to have larger values than the other? | a number "
    "in two groups | Do the aircraft above TRL 2 carry more propulsive units than the rest? |\n"
    "| Fisher exact | Is the share of *yes* the same in both groups? | a yes/no answer in two "
    "groups, safe on small counts | Is Lift + Cruise as large a share of 2020-23 in the patent "
    "record as in the evtol.news directory? |\n"
    "| Chi-square | Do the groups spread over the categories the same way? | a category with "
    "several levels | Do the aircraft out of force spread over the classes the way all aircraft "
    "do? |\n"
    "| Spearman ρ (rho) | Does the value tend to rise or fall as the priority year advances? | a "
    "number against the year | Tilt Rotor propulsive units: ρ {sm_t_units_tr_rho} |\n\n"
    "- ρ runs from −1 (falls steadily) through 0 (no trend) to +1 (rises steadily).\n"
    "- Mann-Whitney and Spearman read the ORDER of the values, not their size, so one extreme "
    "aircraft cannot manufacture a result.\n\n"
    "**Mean or median — which centre, and why.**\n\n"
    "- **Median** — the value of the middle aircraft once the aircraft are sorted. It is the "
    "centre of every count per aircraft (propulsive units, stations), because a handful of "
    "aircraft with tens of units would pull a mean far from any typical aircraft.\n"
    "- **Mean** — the total divided by the number of aircraft. It is used in two places:\n"
    "  - every **share** is a mean: each aircraft counts 1 for *yes* and 0 for *no*;\n"
    "  - **beside the median** when a count takes only small whole values (tilting sets, "
    "propulsor types). A median of 1 stays at 1 while the mix of 1s and 2s shifts: inside CVT "
    "the median number of tilting sets goes from {sm_t_joints_cvt_med_first} to "
    "{sm_t_joints_cvt_med_last} while the mean goes from {sm_t_joints_cvt_first} to "
    "{sm_t_joints_cvt_last}.\n"
    "- Every figure and table names the centre it prints.\n\n"
    "**The 95 % interval of a share.**\n\n"
    "- *What it is:* the range the share would plausibly take on another draw of the same size; "
    "the procedure catches the true share 95 times in 100.\n"
    "- *Why Wilson:* the textbook interval (share ± two standard errors) breaks down near 0 % or "
    "100 % and on small groups, where it can run below zero; the Wilson interval stays inside "
    "0-100 % and stays close to its 95 % on small n.\n"
    "- *Why the finite-population correction:* the n aircraft come from a corpus of only "
    "N = {unique_s}; when n is a large part of N less is unknown, so the interval narrows "
    "(effective n = n·(N − 1)/(N − n)), and when n = N the share is a census with no sampling "
    "error at all.\n"
    "- Where the n aircraft are not a random draw from the N, the Method says so and the interval "
    "is read as the precision of the count, not as a statement about the whole record.\n\n"
    "</div>\n"
)


# =============================================================================================
# 2 — DIVERSITY_BOX (chapter 2, head)                                            C40, C54
# =============================================================================================
DIVERSITY_BOX = (
    '<div class="methods-box">\n\n'
    "##### ¹D and ²D — how many designs are really in play\n\n"
    "**Why not simply count archetypes.** A count treats an archetype held by one aircraft "
    "exactly like one held by forty, so it cannot tell a field split evenly between ten designs "
    "from a field where one design holds almost everything and nine others appear once. The "
    "**effective number** asks instead: *how many equally common archetypes would give the same "
    "spread?*\n\n"
    "**How the two are computed.** Write pᵢ for the share of the window's aircraft in archetype i "
    "(its aircraft divided by all the aircraft of the window).\n\n"
    "- **¹D = exp(H), with H = −Σ pᵢ ln pᵢ** (the Shannon entropy). In words: H measures how "
    "hard it is to guess the archetype of an aircraft drawn at random; exp turns that back into "
    "a number of archetypes. Every archetype counts in proportion to its share.\n"
    "- **²D = 1 / Σ pᵢ²** (the inverse Simpson index). In words: Σ pᵢ² is the chance that two "
    "aircraft drawn at random share an archetype; ²D is one over that chance. Squaring the "
    "shares makes the large archetypes weigh more and the rare ones almost vanish.\n"
    "- Always ²D ≤ ¹D ≤ the count of archetypes; all three are equal only when every archetype is "
    "equally common.\n\n"
    "**Worked example — invented round numbers, for illustration only, not from this corpus.** "
    "A window holds four archetypes.\n\n"
    "| shares of the four archetypes | H = −Σ pᵢ ln pᵢ | ¹D = exp(H) | Σ pᵢ² | ²D = 1 / Σ pᵢ² |\n"
    "|---|---|---|---|---|\n"
    "| 25 / 25 / 25 / 25 % | 1.39 | 4.0 | 0.25 | 4.0 |\n"
    "| 70 / 10 / 10 / 10 % | 0.94 | 2.56 | 0.49 + 3 × 0.01 = 0.52 | 1.92 |\n\n"
    "- Evenly split, four archetypes behave like four.\n"
    "- With one archetype at 70 %, the same four behave like about two and a half (¹D) — or, "
    "counting only the ones that carry weight, like about two (²D).\n"
    "- **The difference between the two:** ¹D describes how spread the whole field is, tail "
    "included; ²D describes how many *large* designs there are. A dominant design is a question "
    "about the large ones, so ²D is the number the dominant-design test reads (condition 2); ¹D "
    "describes the levels and the windows.\n\n"
    "**Rarefaction — comparing windows of different sizes.** The more aircraft a window holds, "
    "the more rare archetypes it happens to include, so a late window with several times the "
    "aircraft of an early one would look more diverse even if both were drawn from the same mix. "
    "Every window is therefore cut to a random {sm_perm_n} aircraft, ¹D and ²D are computed on "
    "that sample, the draw is repeated many times and the results are averaged. Every window is "
    "then compared at the same size.\n\n"
    "**The permutation band — what chance alone gives.** A ²D of its own cannot say whether it "
    "is low. The band is built from the same aircraft:\n\n"
    "1. every aircraft keeps its archetype, and every window keeps its number of aircraft;\n"
    "2. which aircraft sits in which window is shuffled at random, so the priority year no "
    "longer means anything;\n"
    "3. ²D is recomputed for every window of the shuffled corpus;\n"
    "4. this is repeated {sm_perms} times (seed {sm_perm_seed}, so the band is reproducible); the "
    "band is the middle 95 % of the results.\n\n"
    "- A real value **inside** the band is what any random split of the corpus into windows of "
    "these sizes would show: nothing the years explain.\n"
    "- A real value **below** the band means the window holds fewer designs in play than chance "
    "gives it: that is condition 2 of the dominant-design test (chapter 3).\n"
    "- Condition 3 of the same test (chapter 3) builds its band by the same shuffle, on a "
    "different statistic.\n\n"
    "</div>\n"
)


# =============================================================================================
# 3 — ARCHETYPE_METHOD + the level codes / label spec                    C47, C48, C49, C50
# =============================================================================================
ARCHETYPE_METHOD = (
    "#### Method\n\n"
    "**What an archetype is.** An archetype is a design described by a few chosen labels. Choose "
    "the labels; write each aircraft as its answers on them; two aircraft share an archetype "
    "when every answer is the same. Each aircraft has exactly one archetype at each level, and "
    "the **level** is the set of labels chosen.\n\n"
    "**How an archetype is written.** The codes are letters for the labels combined — "
    "**C** class, **W** wings, **T** tilt, **U** propulsive units, **B** booms, **E** tail "
    "(empennage) — and an archetype is written out in words, one label after another:\n\n"
    "- *Lift + Cruise · one wing · no tilting propulsor* — level **C·W·T**: the class is Lift + "
    "Cruise, the aircraft has one wing, and none of its propulsors tilts.\n"
    "- *Tilt Rotor · 1-3 units* — level **C·U**: the class is Tilt Rotor and the aircraft has one "
    "to three propulsive units. Units are counted in five bands, 1-3, 4, 5-6, 7-8 and 9 or more: "
    "the peaks at 4, 6 and 8 each anchor a band, and 5 or 7 is most often an even lift set plus "
    "one pusher.\n\n"
    "**Many levels were built; only the coarse ones can carry the test.** {sm_arch_levels} "
    "levels were formed, combining the class with wings, booms, tail, tilt and the unit band. "
    "The more labels a level combines, the more archetypes it has and the fewer aircraft each "
    "one holds: the finest levels run to {sm_arch_max} archetypes, with effective numbers up to "
    "{sm_eff_max}. A test written on shares cannot be read there, because almost no archetype is "
    "large enough to hold a share. Four screens, fixed in code, decide which levels are usable:\n\n"
    "| screen | the level must have | why |\n"
    "|---|---|---|\n"
    "| resolution | at least twice as many archetypes as there are classes | otherwise it adds "
    "nothing to the class |\n"
    "| fragmentation | at most {sm_screen_frag} of the aircraft alone in their archetype | an "
    "aircraft alone is a design nobody shares |\n"
    "| population | at least {sm_screen_pop} of the aircraft in archetypes of "
    "{sm_screen_big} or more | a share needs aircraft behind it |\n"
    "| readable shares | at least {sm_screen_readable} archetypes each holding {sm_screen_share} "
    "or more | a test on the largest share needs contenders |\n\n"
    "{sm_arch_pass} of the {sm_arch_levels} levels pass all four; the rest fail because they are "
    "too fine. Of those that pass, **C·W·B** (class, wings, booms present) is set aside: booms are "
    "structure — they carry rotors but do not decide how the aircraft lifts or cruises. The "
    "class alone (**C**) fails only resolution, because it *is* the class; it is kept as the "
    "reference.\n\n"
    "**The levels this document reads.**\n\n"
    "| level | combines | why it is read |\n"
    "|---|---|---|\n"
    "| **C** — Class | the architecture class | the reference: how the aircraft passes from hover "
    "to cruise; every per-class reading is at this level |\n"
    "| **C·W·T** — Class + wings + tilt | class · number of wings · whether any propulsor tilts "
    "| the *design species*: the two further decisions that change how the aircraft flies; the "
    "level the dominant-design test was written at |\n"
    "| **C·U** — Class + units | class · propulsive-unit band | the decision distributed electric "
    "propulsion moves: it tells a four-rotor Lift + Cruise from a twelve-rotor one |\n"
    "| **F** — Lift + Cruise family | the family defined below, or else the class | the grouping "
    "tested as one design across two classes; **post hoc** |\n\n"
    "*The T of C·W·T.* Inside the large classes the tilt answer is almost fixed by the class — "
    "Lift + Cruise never tilts; Tilt Rotor, CVT and Tilt Wing do — so for them C·W·T separates "
    "designs by the number of wings. The tilt answer separates designs inside Multirotor and the "
    "smaller classes.\n\n"
    "**The Lift + Cruise family (F).** One archetype at this level holds every Lift + Cruise "
    "aircraft **plus every CVT aircraft whose tilting part is a rotor set and which has no "
    "tilting wing**; every other aircraft keeps its class. It holds {sm_fam_b_n} aircraft.\n\n"
    "- *Why these two together — the airframe.* Both are a fixed wing that never tilts, carrying "
    "rotors spread over the airframe. They differ in one thing only: whether cruise thrust comes "
    "from dedicated propellers (Lift + Cruise) or from tilting some of the rotors forward (this "
    "CVT). The criterion is morphological similarity of the airframe.\n"
    "- *Other groupings considered, and not used.* CVT with its units on booms, grouped with "
    "Lift + Cruise (a structural and redundancy criterion: the rotors sit on booms); and Tilt "
    "Rotor with CVT (grouped because something tilts).\n"
    "- *Post hoc.* The family was defined after the class and archetype readings had been seen. "
    "It is not one of the pre-set classes, no result on it is a pre-registered test, and it is "
    "marked post hoc wherever it appears.\n"
)

#: old level id -> (new code, printed name). Codes: C class, W wings, T tilt (any tilting
#: propulsor), U propulsive-unit band, B booms present, B# booms binned, E tail (empennage) type.
LEVEL_CODES = {
    "A0":   ("C",         "Class"),
    "A0c":  ("C·U",       "Class + units"),
    "A1":   ("C·W·B",     "Class + wings + booms"),
    "A1c":  ("C·W·B·U",   "Class + wings + booms + units"),
    "A1b":  ("C·W·B#",    "Class + wings + number of booms"),
    "A1t":  ("C·W·T",     "Class + wings + tilt"),
    "A1tc": ("C·W·T·U",   "Class + wings + tilt + units"),
    "A2":   ("C·W·B·E",   "Class + wings + booms + tail"),
    "A2c":  ("C·W·B·E·U", "Class + wings + booms + tail + units"),
    "family_b": ("F",     "Lift + Cruise family"),
}

#: the fields of each level in key order (same order as ``a2.ARCHETYPE_LEVELS[level][0]``),
#: named by the vocabulary of :data:`VALUE_WORDS`
LEVEL_FIELDS = {
    "A0":   ["class"],
    "A0c":  ["class", "units"],
    "A1":   ["class", "wings", "booms"],
    "A1c":  ["class", "wings", "booms", "units"],
    "A1b":  ["class", "wings", "boombin"],
    "A1t":  ["class", "wings", "tilt"],
    "A1tc": ["class", "wings", "tilt", "units"],
    "A2":   ["class", "wings", "booms", "tail"],
    "A2c":  ["class", "wings", "booms", "tail", "units"],
}

#: raw key value -> printed words, per field. "blank" is how ``la_tables._level_key`` writes a
#: design absence; "n/a (no M3 card)" is a Hoverbike / PFV (no propulsion record by design).
_NO_M3 = "no propulsion record"
VALUE_WORDS = {
    "class": {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "Combined Vectored Thrust",
              "TW": "Tilt Wing", "MR": "Multirotor", "TB": "Tilt Body", "PTC": "Pitch-to-Cruise",
              "HB": "Hoverbike", "DS": "Deflected Slipstream", "PFV": "Personal Flying Vehicle",
              "SRW": "Stopped/Slowed Rotor Wing", "RC": "Rotorcraft"},
    "wings": {"0": "no wing", "1": "one wing", "True": "one wing", "2": "two wings",
              "3": "three wings", "4": "four wings", "blank": "wings not recorded"},
    "tilt": {"True": "a tilting propulsor", "False": "no tilting propulsor",
             "n/a (no M3 card)": _NO_M3},
    "units": {"0-3": "0-3 units", "1-3": "1-3 units", "4": "4 units", "5-6": "5-6 units",
              "7-8": "7-8 units", "9+": "9 or more units", "n/a (no M3 card)": _NO_M3},
    "booms": {"True": "booms", "False": "no booms", "blank": "booms not recorded"},
    "boombin": {"none": "no booms", "1-2": "1-2 booms", "3": "3 booms", "4+": "4 or more booms"},
    "tail": {"Tailless": "no tail", "Conventional": "conventional tail",
             "Cruciform": "cruciform tail", "T-Tail": "T-tail", "V-Tail": "V-tail",
             "Inv_V-Tail": "inverted V-tail", "Y-Tail": "Y-tail", "H-Tail": "H-tail / twin tail",
             "VertFin": "single fin", "HorizStab": "horizontal stabiliser only",
             "Fins": "two or more fins", "BoxTail": "box tail", "Oth": "other tail",
             "blank": "tail not recorded"},
}

#: level inferred from the number of parts when the caller does not name it (the three levels
#: the brief reads have 1, 2 and 3 parts)
_LEVEL_BY_PARTS = {1: "A0", 2: "A0c", 3: "A1t"}


def archetype_label(key, level=None, sep=" · "):
    """``"SLC · 1 · False"`` -> ``"Lift + Cruise · one wing · no tilting propulsor"``.

    ``key`` is an archetype string as ``la_tables`` writes it (parts joined by " · "; a trailing
    share such as "SLC · 1 · False 25%" from ``top_archetypes`` is kept and re-attached).
    ``level`` is the old level id (A0, A0c, A1t, ...); omitted, it is inferred from the number of
    parts. An unknown value is printed as it is, so nothing is ever dropped silently.
    """
    if key is None:
        return key
    text = str(key).strip()
    if not text or text.lower() == "nan":
        return key
    tail = ""
    last = text.rsplit(" ", 1)
    if len(last) == 2 and last[1].endswith("%") and last[1][:-1].replace(".", "", 1).isdigit():
        text, tail = last[0], " " + last[1]
    parts = [p.strip() for p in text.split("·")]
    lvl = level or _LEVEL_BY_PARTS.get(len(parts))
    fields = LEVEL_FIELDS.get(lvl)
    if not fields or len(fields) != len(parts):
        return str(key)
    words = []
    for field, val in zip(fields, parts):
        v = val[:-2] if val.endswith(".0") else val       # "1.0" wings -> "1"
        words.append(VALUE_WORDS.get(field, {}).get(v, val))
    # a Hoverbike / PFV carries "no propulsion record" once, not once per propulsion field
    out = []
    for w in words:
        if w == _NO_M3 and _NO_M3 in out:
            continue
        out.append(w)
    return sep.join(out) + tail


def level_name(level, with_code=True):
    """``"A1t"`` -> ``"C·W·T (Class + wings + tilt)"``; the plain name with ``with_code=False``."""
    code, name = LEVEL_CODES.get(str(level), (str(level), str(level)))
    return f"{code} ({name})" if with_code else name


# =============================================================================================
# 4 — CONDITIONS_METHOD and ERA_FRAME_METHOD                       C41, C51, C53, C54, C55, C64
# =============================================================================================
CONDITIONS_METHOD = (
    "#### Method\n\n"
    "A **dominant design** is the design a sector settles on after a period of competing "
    "alternatives: most new products follow it, and change moves from the concept to its parts "
    "(Abernathy and Utterback, 1978). A patent record cannot see sales, so the idea is tested "
    "through three conditions of different kinds — **counts, balance, form**. Each asks one "
    "question; the thresholds were fixed before any curve of this corpus was drawn, which is "
    "what makes a *no* a finding and not a description. **A dominant design needs all three in "
    "the same period.**\n\n"
    "**Condition 1 — counts. Is most of the sector proposing the same design?**\n\n"
    "- *Measure:* the share of the largest archetype among [BASE: per year / in force — pending "
    "author decision].\n"
    "  - *per year* — the aircraft of each complete priority year; met when one archetype holds "
    "more than 50 % in consecutive years (Anderson and Tushman, 1990, ask for more than 50 % of "
    "new product sales in four consecutive years).\n"
    "  - *in force* — the aircraft with at least one patent still in force at the snapshot; met "
    "when one archetype holds more than 50 % of them (what the sector still holds rights to).\n"
    "- *What moves it:* one archetype gaining at the expense of all the others. Two designs "
    "sharing the field do not meet it; that case is read separately as the top two archetypes "
    "holding more than 50 % together.\n\n"
    "**Condition 2 — balance. Are fewer designs in play than chance gives?**\n\n"
    "- *Measure:* ²D of the window (how many large designs are in play, box above) against its "
    "permutation band.\n"
    "- *Met when* ²D falls below the band: the window holds fewer designs in play than the same "
    "aircraft, dealt into windows at random, would give it.\n"
    "- *What moves it:* a window crowding into two or three archetypes while the rest of the "
    "corpus is spread. A window that is as concentrated as the corpus as a whole does not meet "
    "it: the condition detects a period that is *more* concentrated than the record.\n\n"
    "**Condition 3 — form. Have the aircraft themselves become alike?**\n\n"
    "- *The distance between two aircraft:* every labelled field is compared — wings, tail, "
    "fuselage, booms, propulsion, class. A shared answer counts 0, a different one 1, and a count "
    "counts by how far apart the two values are; a field blank on either aircraft is skipped "
    "rather than counted as a difference. Each of the six subsystems (architecture, wings, "
    "empennage, fuselage, booms, propulsion) carries the same weight, shared among its fields, so "
    "a card with many questions does not outweigh one with few. The result runs from 0 "
    "(identical) to 1 (nothing in common) — Gower's distance.\n"
    "- *Measure:* **Q**, the average distance between two aircraft drawn at random from the "
    "window (Rao's quadratic entropy). Q falls when the aircraft of a window resemble each other "
    "field by field.\n"
    "- *Met when* Q falls below the average Q of the two earliest windows by more than chance "
    "allows: the same shuffle as condition 2 gives the band of the difference.\n"
    "- *What moves it — and what does not:* Q uses no archetype. If aircraft converge on one "
    "layout under different class names (say a Lift + Cruise and a CVT that look almost the "
    "same), Q falls while conditions 1 and 2 need not move. If one class grows while its own "
    "aircraft stay varied, condition 1 can climb while Q does not fall. It is the one condition "
    "that does not depend on the level or on how archetypes are named or grouped.\n"
    "- *Weighting:* reported under the subsystem weighting above and, as a check, under equal "
    "weight for every field. A result that appears under one weighting only is a result about "
    "the weighting.\n\n"
    "**What grouping classes does to the test.** Merging archetypes adds their shares, so any "
    "grouping can only raise the largest share (condition 1) and lower ²D (condition 2); enough "
    "grouping would pass condition 1 by construction. A grouping is therefore fixed on a "
    "criterion that is not its share. The Lift + Cruise family (F) is fixed on the form of the "
    "airframe; it was chosen after the readings had been seen, and is read as **post hoc**. On "
    "the family, conditions 2 and 3 run unchanged on the family's own aircraft.\n\n"
    "**Where each condition comes from.** Condition 1 operationalises Anderson and Tushman (1990) "
    "on what a patent record can see. Conditions 2 and 3 are this thesis's own measurements: the "
    "literature says in words that variety collapses (Utterback) and that the core subsystems "
    "converge (Murmann and Frenken, 2006), but gives neither statement a threshold on a patent "
    "record, and no citation is claimed for theirs. Suárez and Utterback (1995) date a dominant "
    "design by the shakeout of firms that follows it; that test is not run, because a shakeout "
    "needs exits, and a record in which most active firms are still filing for the first time "
    "has none to date anything by.\n"
)

ERA_FRAME_METHOD = (
    "**The frame the result is read in: eras of a technology cycle.** Anderson and Tushman (1990) "
    "describe a technology as moving through a cycle:\n\n"
    "1. a **technological discontinuity** — a new core concept opens a new design space "
    "(for eVTOL the candidate is distributed electric propulsion, which makes vertical take-off "
    "on many small rotors possible);\n"
    "2. an **era of ferment** — rival concepts compete, variety is high, and each firm bets on its "
    "own layout;\n"
    "3. a **dominant design** is selected;\n"
    "4. an **era of incremental change** — the concept is fixed and effort moves to refining its "
    "parts, until the next discontinuity.\n\n"
    "The two kinds of innovation map onto the eras. A **radical** innovation changes the core "
    "concept — how the aircraft passes from hover to cruise, which is what the architecture "
    "class records. An **incremental** innovation refines a concept that is kept — more rotors, "
    "a duct, a folding blade, a second tilting set on the same layout. An era of ferment is "
    "dominated by the first kind; an era of incremental change by the second.\n\n"
    "What each era predicts on the measures of this chapter:\n\n"
    "| measure | era of ferment | dominant design emerging | incremental change |\n"
    "|---|---|---|---|\n"
    "| largest archetype share (condition 1) | well below half | rising toward half | above half |\n"
    "| ²D (condition 2) | high: many designs in play | falls below the band | low: one or two |\n"
    "| Q (condition 3) | high: aircraft unlike each other | clear drop | low |\n"
    "| where change happens | the class itself (radical) | from the class to its parts | the parts "
    "(incremental) |\n\n"
    "The sector is placed in an era by reading the three conditions together, and the within-class "
    "readings of chapter 3 say whether change inside each class is already incremental while the "
    "classes themselves still compete.\n"
)


# =============================================================================================
# 5 — GLOSSARY_TABLE (chapter 2, head, beside the statistics)               C63, C69, C82, C90
# =============================================================================================
GLOSSARY_TABLE = (
    "**The propulsion vocabulary.** Four words carry most of the propulsion readings, from the "
    "smallest to the largest: a **unit** is one rotor; a **type** is a set of like units in one "
    "place; a **station** is the place; a **tilting set** is whatever swivels between hover and "
    "cruise as one.\n\n"
    "| term | what it is | how it is counted | example |\n"
    "|---|---|---|---|\n"
    "| **propulsive unit** | one rotor, propeller or fan that gives lift or thrust | per aircraft, "
    "summed over every station; control-only units are not counted; Hoverbikes and personal "
    "flying vehicles have no propulsion record | a Lift + Cruise with eight lift rotors and one "
    "pusher propeller has nine |\n"
    "| **unit band** | the unit count in five bands: 1-3, 4, 5-6, 7-8, 9 or more | 4, 6 and 8 "
    "each anchor a band; 5 or 7 is most often an even lift set plus one pusher | nine units fall "
    "in 9 or more |\n"
    "| **station** | a place on the airframe that carries propulsors; the labelling records each "
    "on its own card. There are eight: **fuselage** (the body), **wing 1**, **wing 2**, **wing 3** "
    "(each wing panel separately — a main wing, a canard or tandem wing, a third surface), "
    "**empennage** (the tail), **booms** (every boom together), **hull edge array** (the edges of a "
    "blended, flying-wing or lifting body) and **body array** (a wingless body carrying every "
    "propulsor) | stations carrying units, per aircraft | the Lift + Cruise above uses two: the "
    "booms and the fuselage |\n"
    "| **propulsor type** | one set of like units on one station: the same kind of rotor, the same "
    "tilt, duct and fold. A station holds one type or several | types per aircraft, over every "
    "station; control-only types are left out | the Lift + Cruise above has two types: the lift "
    "rotors on the booms and the pusher on the fuselage |\n"
    "| **tilting unit** / **fixed unit** | a unit that changes its thrust direction between hover "
    "and cruise — on its own mount, on a tilting wing, on a tilting boom or on a tilting tail; "
    "any other unit is fixed | per aircraft: any tilting unit, any fixed unit | a tilt wing's "
    "rotors are tilting units, although they do not swivel on their own mounts |\n"
    "| **tilting set** (printed until now as *tilting joint group*) | each part of the aircraft "
    "that swivels its units as one: a tilting propulsor type, a tilting wing panel, a tilting boom "
    "group, a tilting tail | per aircraft, each counts one; 0 for an aircraft whose thrust does "
    "not tilt. The joints *inside* a set (one actuator per rotor or one for the whole wing) are "
    "not labelled | a tilt rotor whose wing rotors and tail rotors both tilt has two tilting "
    "sets; a tilt wing has one |\n"
    "| **boom group** | booms recorded together because they are alike: the same attachment and "
    "the same tilt | a boom group that tilts is one tilting set | four identical booms under the "
    "wing are one boom group |\n"
    "| **ducted unit** | a unit recorded as a ducted fan or shrouded rotor rather than an open "
    "rotor | per aircraft: any ducted unit, or the count of ducted units | a single ducted tail "
    "fan makes an aircraft *with a ducted unit* |\n"
    "| **retracting or blade-folding unit** | a unit that withdraws into the structure, or whose "
    "blades fold, once it stops working in cruise | per aircraft: any | a Lift + Cruise whose lift "
    "rotors fold flat for cruise |\n"
    "| **control-only unit** | a small unit that gives attitude or yaw authority, not lift or "
    "cruise thrust (a pitch-trim fan, an anti-torque rotor) | left out of units, types and "
    "tilting sets | the trim fan on the tail of a tilt wing |\n\n"
    "*Retired word:* **propulsor group**. Earlier tables used it for a station carrying units, and "
    "the drivers used *joint group* for a tilting set; both are replaced by the two words above, "
    "so that *group* means only a boom group.\n"
)


# =============================================================================================
# 6 — class configuration rules                                                       C63
# =============================================================================================
#: printable: the rules as they run now (``la_tables.CLASS_CONFIG_RULES``), with the reason
CLASS_RULES_TABLE_CURRENT = (
    "A **configuration** is an aircraft written on the labels that tell two aircraft of the "
    "*same* class apart; the labels the class itself already fixes are left out. The rules per "
    "class:\n\n"
    "| class | configuration = | why these labels |\n"
    "|---|---|---|\n"
    "| Lift + Cruise | lift units fixed, or retracting / blade-folding · unit band | the lift set "
    "is dead weight and drag in cruise; whether it is stowed is the class's own answer to that |\n"
    "| Tilt Rotor | one tilting type, or two or more · unit band | how many sets of rotors tilt |\n"
    "| Combined Vectored Thrust | tilting types × fixed types · unit band | the class is defined by "
    "mixing tilting and fixed thrust; the mix is its decision |\n"
    "| Tilt Wing | one wing, or two or more · unit band | a single tilting wing or a tandem pair |\n"
    "| Multirotor | booms, or no booms · unit band | what carries the rotors |\n\n"
    "Ducting is not in any rule: inside a class a duct is an installation choice, and it is read "
    "on its own elsewhere.\n"
)

#: printable IF the author rules for the proposal below (no numbers; the shares come from a new
#: table, see NEW_PLACEHOLDERS)
CLASS_RULES_TABLE_PROPOSED = (
    "A **configuration** is an aircraft written on the labels that tell two aircraft of the "
    "*same* class apart; the labels the class itself already fixes are left out. The rules per "
    "class — **chosen after the modal shares under the earlier rules had been seen, and read as "
    "post hoc**:\n\n"
    "| class | configuration = | why these labels |\n"
    "|---|---|---|\n"
    "| Lift + Cruise | lift units stowed (retracting or blade-folding) or not · where the lift "
    "units sit: on booms, on the wing, on the body | the two layout decisions of the class: what "
    "carries the lift set, and whether it is hidden in cruise |\n"
    "| Tilt Rotor | one tilting set · two or more tilting sets on one station · two or more "
    "tilting sets on two or more stations | the class's own decision is how the tilting thrust is "
    "split: one set, several sets in one place, or sets fore and aft |\n"
    "| Combined Vectored Thrust | what tilts: rotors, a wing, or both · whether the fixed units "
    "sit on booms | the class mixes tilting and fixed thrust; what tilts and where the fixed part "
    "sits is the layout |\n"
    "| Tilt Wing | one wing, or two or more · unit band | unchanged |\n"
    "| Multirotor | booms, or no booms · unit band | unchanged |\n\n"
    "The unit band is left out of the three largest classes because it is read on its own (level "
    "C·U and the drivers); inside a rule it multiplied every configuration by five for a reason "
    "that is not the class's layout.\n"
)

#: AUTHOR-FACING — not for printing. Numbers typed from the scratch run of 2026-09-26
#: (scratchpad rules.py / rules2.py, same base frame as la_tables.base); once a rule is ruled,
#: the shares move into a table and are printed through placeholders.
CLASS_RULES_PROPOSAL = (
    "### Proposal for the author — per-class configuration rules (C63)\n\n"
    "**What is wrong with the current rules.**\n\n"
    "- *The unit band is in every rule.* It multiplies each class's configurations by up to five, "
    "so the most common configuration is small for a reason that is rotor count, not layout — and "
    "rotor count is already read on its own (C·U, drivers).\n"
    "- *CVT counts only rotors that swivel on their own mount.* A CVT whose tilt comes from a "
    "tilting wing reads \"0 tilting types\" (the 2012-15 modal CVT configuration is \"0 tilting × "
    "2 fixed\"). What tilts, and where, is invisible.\n"
    "- *Tilt Rotor \"2+ tilting types\" merges two designs:* two tilting types on one station "
    "(e.g. front and rear rotors on the same booms) and tilting sets on two stations (canard + "
    "wing, wing + tail).\n\n"
    "**Proposed rules** (tilt read as in the traces and the family: on its own mount, on a "
    "tilting wing, on a tilting boom, on a tilting tail; control-only units excluded):\n\n"
    "- **Lift + Cruise** — lift units stowed or not · where the fixed units sit: on booms (any), "
    "else on the wing, else on the body.\n"
    "- **Tilt Rotor** — one tilting set / 2+ tilting sets on one station / 2+ tilting sets on "
    "2+ stations (wing 1 and wing 2 count as different stations).\n"
    "- **CVT** — what tilts (rotors / a wing / rotors and a wing) · fixed units on booms or not.\n"
    "- **Tilt Wing, Multirotor** — unchanged (without the band they collapse to two "
    "configurations each).\n\n"
    "**Share of the class in its most common configuration** (configurations / aircraft of the "
    "class-window in brackets; windows under 5 aircraft blank):\n\n"
    "| class | rule | ≤2011 | 2012-15 | 2016-19 | 2020-23 | most common in 2020-23 |\n"
    "|---|---|---|---|---|---|---|\n"
    "| Lift + Cruise | current: stowed · band | 50 % (4/18) | 53 % (6/17) | 31 % (9/51) | "
    "31 % (9/78) | lift units fixed · 9+ |\n"
    "| Lift + Cruise | **proposed: stowed · where lift units sit** | 56 % (2/18) | 47 % (4/17) | "
    "43 % (6/51) | **51 % (5/78)** | lift units fixed · on booms |\n"
    "| Lift + Cruise | alt.: where lift units sit only | 56 % (2/18) | 53 % (2/17) | 49 % (3/51) "
    "| 56 % (3/78) | on booms |\n"
    "| Lift + Cruise | alt.: stowed · coarse band (1-4 / 5-8 / 9+) | 50 % (3/18) | 59 % (4/17) "
    "| 33 % (6/51) | 45 % (6/78) | lift units fixed · 5-8 |\n"
    "| Tilt Rotor | current: tilting types · band | 64 % (5/22) | 48 % (5/21) | 31 % (8/51) | "
    "24 % (10/51) | 2+ tilting types · 9+ |\n"
    "| Tilt Rotor | **proposed: tilting sets and stations** | 73 % (3/22) | 52 % (3/21) | "
    "35 % (3/51) | **39 % (3/51)** | 2+ tilting sets on 2+ stations |\n"
    "| Tilt Rotor | alt.: tilting types 1 / 2+ only | 73 % (2/22) | 52 % (2/21) | 67 % (2/51) | "
    "67 % (2/51) | 2+ tilting types |\n"
    "| CVT | current: tilting × fixed types · band | 25 % (6/8) | 20 % (8/10) | 14 % (18/28) | "
    "17 % (20/53) | 2 tilting × 1 fixed · 5-6 |\n"
    "| CVT | **proposed: what tilts · fixed on booms?** | 62 % (3/8) | 50 % (5/10) | 46 % (5/28) "
    "| **53 % (8/53)** | rotors tilt · fixed units on booms |\n"
    "| CVT | alt.: what tilts · station of the fixed units | 38 % (5/8) | 20 % (7/10) | "
    "39 % (10/28) | 40 % (19/53) | rotors tilt · fixed on booms |\n"
    "| Tilt Wing | current: wings · band | — | 33 % (3/6) | 24 % (8/25) | 20 % (8/20) | "
    "1 wing · 4 |\n"
    "| Multirotor | current: booms · band | 44 % (5/9) | — | 35 % (7/17) | 31 % (8/16) | "
    "booms · 4 |\n\n"
    "**Reading and cautions.**\n\n"
    "- The Tilt Rotor modal configuration *moves*: one tilting set until 2012-15, two sets on one "
    "station in 2016-19, sets on two stations in 2020-23 — the same movement as drivers "
    "observation 1, now visible in the configuration figure.\n"
    "- The proposed CVT modal (rotors tilt, fixed units on booms) is the layout that motivates "
    "the family; at 53 % of CVT in 2020-23 it crosses half the class. That is concentration "
    "*inside one class*, not condition 1 — the text must say so.\n"
    "- These rules were chosen after seeing the shares: they must be printed as post hoc "
    "(rule 3). The honest reading is the change across windows under a fixed rule, not the level.\n"
    "- The scratch run reproduces the current rules exactly (same shares as "
    "``la_class_configs_own``). The proposed columns need new per-aircraft fields in "
    "``la_tables`` (where the fixed units sit; tilting sets and their stations; what tilts), read "
    "by the rules of ``trace_frame`` / ``family_flags``, not by ``_per_aircraft_units`` (which "
    "counts only own-mount tilt and includes control-only types).\n\n"
    "**For the author to rule:** (1) adopt the three proposed rules, an alternative, or keep the "
    "current ones; (2) drop the band from Tilt Wing and Multirotor too, for consistency, or keep "
    "it; (3) accept the post-hoc label on the configuration figure.\n"
)


# =============================================================================================
# 7 — DRIVERS_METHOD                                                  C80, C81, C82, C89, C90
# =============================================================================================
DRIVERS_METHOD = (
    "#### Method\n\n"
    "**Driver and trace.** A *design driver* is a cause of design change: a technology that "
    "moved, a physical limit that did not, a requirement, a cost. A driver is never written in a "
    "patent. What a patent does show is the aircraft, and if a driver acts it should leave a "
    "**trace** — a labelled feature that moves over the years in the direction the driver "
    "predicts. The drivers considered:\n\n"
    "| kind | drivers |\n"
    "|---|---|\n"
    "| A1 technological | regime transition (from hover to wing-borne flight); distributed "
    "propulsion and rotor control |\n"
    "| A2 physical | hover load path; wing structural and aeroelastic limits; cruise stability and "
    "control; flow interference and drag |\n"
    "| B requirement | mission range and speed; payload; occupant presence; failure tolerance; "
    "community noise; operating environment |\n"
    "| C life-cycle cost | development and certification; production; maintenance |\n\n"
    "**What a trace is.** One label, read against the priority year: either a **share** of the "
    "aircraft (units on booms, a pusher unit, two or more wing panels) or a **count per "
    "aircraft** (propulsive units, propulsor types, tilting sets — each defined in the "
    "propulsion vocabulary of chapter 2). Two counts are easy to misread:\n\n"
    "- *propulsor types* — how many different sets of like units the aircraft carries: a Lift + "
    "Cruise with lift rotors on booms and a pusher on the fuselage has two; a tilt rotor that "
    "adds a second tilting set on its tail goes from one to two.\n"
    "- *tilting sets* — how many parts of the aircraft swivel between hover and cruise; each "
    "tilting wing, tilting boom group, tilting tail or tilting propulsor type counts one.\n\n"
    "**Read inside each class, never pooled.** *Pooled* means every class thrown together into "
    "one curve. A pooled curve mixes two different movements: change *inside* designs, and change "
    "in *which* designs are filed. Tilting sets show why that matters: they rise inside Tilt Rotor "
    "({sm_t_joints_tr_first} to {sm_t_joints_tr_last} on average, p {sm_t_joints_tr_p}) and inside "
    "CVT, yet pooled over the classes they stay flat ({sm_t_joints_all_first} to "
    "{sm_t_joints_all_last}, p {sm_t_joints_all_p}) — because over the same years Lift + Cruise, "
    "which has no tilting set at all, takes a larger part of the record. A driver acts on how an "
    "aircraft is built, so it is looked for inside one class at a time; the pooled row is printed "
    "only as that contrast.\n\n"
    "**The test.** Spearman ρ between the priority year and the trace, over the aircraft of the "
    "class that carry a value, in the years read (below): *rises* or *falls* at p < 0.05, *flat* "
    "otherwise (statistics box). A trend is read only on {sm_trend_min} aircraft or more; a window "
    "is drawn only with {sm_min_cell} aircraft or more; the classes drawn are those with "
    "{sm_min_cell} aircraft or more in at least {sm_min_windows} windows.\n\n"
    "**The centre.** Counts are medians — propulsive units only as a median, because a few hull "
    "arrays with tens of units would carry a mean. For small whole-number counts (tilting sets, "
    "propulsor types) the mean is printed beside the median, because a median of 1 or 2 can stand "
    "still while the mix moves. Shares are shares of the aircraft that answer the label.\n\n"
    "**The years read.** [YEARS: pending author decision.] The earliest windows hold a fraction "
    "of the aircraft of the later ones, so a curve drawn through them compares a handful of "
    "aircraft with a large set. Every trace figure marks the years that are read with a vertical "
    "line and greys the windows before it; the windows before the line stay visible and are not "
    "read.\n\n"
    "**Unit of analysis.** The unique aircraft, because a trace is a property of a design, and a "
    "design filed five times is still one design.\n\n"
    "**What a trace can and cannot say.** A trace that moves in the predicted direction is "
    "*consistent* with its driver; it does not prove it. When several drivers predict the same "
    "trace, the trace is called *overdetermined* and no one driver is named.\n"
)


# =============================================================================================
# New placeholders these texts need (name -> how to compute). The coordinator registers them.
# =============================================================================================
NEW_PLACEHOLDERS = {
    # STATS_BOX — add to sm_index._TRACE_POINTS; _driver_numbers then emits _first/_last/_rho/_p
    "sm_t_units_mr_first / _last / _rho / _p":
        '_TRACE_POINTS += ("units_mr", "propulsive units", "MR", "value", "1f")',
    "sm_t_joints_cvt_med_first / _last":
        '_TRACE_POINTS += ("joints_cvt_med", "tilting joint groups", "CVT", "value", "1f") '
        "(the MEDIAN columns; the existing joints_cvt reads the means)",
    # ARCHETYPE_METHOD
    "sm_arch_max": 'la_archetype_levels, how="max", col "archetypes", int',
    "sm_eff_max": 'la_archetype_levels, how="max", col "effective number ¹D", 1f',
    "sm_screen_frag": "la_tables.ARCHETYPE_SCREENS fragmentation line (0.05) as pct — read in "
                      "_method_numbers like sm_perms",
    "sm_screen_pop": "la_tables.ARCHETYPE_SCREENS population line (0.90) as pct",
    "sm_screen_readable": "la_tables.ARCHETYPE_SCREENS readable-shares line (3), int",
    "sm_screen_big": "the 'archetype of five or more' size, literal 5 in la_tables.archetype_levels "
                     "(counts >= 5) — make it a module constant and read it",
    "sm_screen_share": "the '5 % or more' share, literal 0.05 in la_tables.archetype_levels "
                       "(shares >= 0.05) — make it a module constant and read it",
    "sm_fam_b_n": 'la_family_dd, where id == "b", col "aircraft", int (one row per condition; '
                  "any row)",
    # DRIVERS_METHOD — apparatus constants, read in _method_numbers
    "sm_trend_min": "la_tables.TREND_MIN (20)",
    "sm_min_cell": "la_tables.MIN_CELL (5)",
    "sm_min_windows": "la_tables.MIN_WINDOWS (3)",
    # CLASS_RULES_TABLE_PROPOSED, if ruled: a new table (e.g. la_class_configs_rules) with the
    # modal share per class-window under the ruled rule; placeholders such as
    # sm_cfg_slc_2023 / sm_cfg_tr_2023 / sm_cfg_cvt_2023 (share in the modal configuration,
    # 2020-23) and sm_cfg_<class>_2023_n (configurations in 2020-23).
}

#: existing placeholders these texts rely on (for the coordinator's check)
USED_PLACEHOLDERS = (
    "unique_s", "sm_t_units_tr_first", "sm_t_units_tr_last", "sm_t_units_tr_rho",
    "sm_t_units_tr_p", "sm_fa_p", "sm_fa_p_sens", "sm_t_joints_cvt_first", "sm_t_joints_cvt_last",
    "sm_perm_n", "sm_perms", "sm_perm_seed", "sm_arch_levels", "sm_arch_pass",
    "sm_t_joints_tr_first", "sm_t_joints_tr_last", "sm_t_joints_tr_p", "sm_t_joints_all_first",
    "sm_t_joints_all_last", "sm_t_joints_all_p",
)
