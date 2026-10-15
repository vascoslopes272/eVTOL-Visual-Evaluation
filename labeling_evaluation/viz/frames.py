"""The per-aircraft analysis frame: one row per unique aircraft, with year, window, region, filer, firm,
class and the derived propulsion fields. Every table and figure of the Labelling Analysis starts here.

Wrangling only (no statistics). Ported from the archive (archive/labeling_evaluation/src/dataset_facts/):
``la_tables.base`` and everything it calls. The windows and the class fold come from the config
(``labelling_analysis.yaml``: ``analysis.windows`` / ``analysis.class_fold``), not from constants.

    from viz import config, data, frames
    cfg = config.load()
    v = frames.base(data.load_dataset(cfg), cfg)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

import numpy as np
import pandas as pd

from .data import M3_STATIONS, NO_UNITS_TYPES, override_sets

#: the regions kept apart; every other region is pooled as "Other regions".
#: Ported from: la_tables.py:REGIONS
REGIONS = ["North America", "Europe", "Asia-Pacific"]

#: the two catch-all buckets of company_canonical, which are not companies.
#: Ported from: a2.py:CATCH_ALL
CATCH_ALL = ("Individual Inventor", "Unknown / Independent")

#: propulsor units per aircraft -> bins of the archetype level A0c. The bottom band is "1-3": a recorded 0 is not an answer
#: (propulsor_units, rerun of 2026-10-15), so no design reaches the bin with fewer than one propulsor.
#: Ported from: a2.py:ROTOR_BINS (whose bottom label was "0-3")
ROTOR_BINS = ([-1, 3, 4, 6, 8, 10 ** 6], ["1-3", "4", "5-6", "7-8", "9+"])

#: display bands of the propulsor-unit count (the bottom band is written "1-3": no aircraft flies on nothing).
#: Ported from: la_tables.py:UNIT_BANDS
UNIT_BANDS = ([0, 3, 4, 6, 8, 10 ** 6], ["1-3", "4", "5-6", "7-8", "9+"])

#: archetype value of a type the codebook gives no propulsor card (HB, PFV).
#: Ported from: a2.py:NO_M3_CARD
NO_M3_CARD = "n/a (no M3 card)"

#: why a propulsion value is left out. Ported from: a2.py:LEFT_OUT_*
LEFT_OUT_HBPFV = "HB/PFV: no propulsor record (codebook)"
LEFT_OUT_G1 = "G1 override: no type"
LEFT_OUT_NONE = "no propulsor recorded"
LEFT_OUT_M3 = "M3 override: station detail not kept"
LEFT_OUT_M3_COUNT = "M3 override without a quick count"
LEFT_OUT_M2 = "M2 override: wing or tail tilt not determinable"
LEFT_OUT_M1 = "M1 override: boom groups not determinable"

#: columns that carry propulsor units, used by the batch-reader fallback of propulsor_units.
#: Ported from: a2.py:PROPULSOR_UNIT_COLUMNS
PROPULSOR_UNIT_COLUMNS = [
    "boom_count", "wing1_count", "wing2_count", "wing3_count",
    "emp_count", "fuselage_count", "hull_array_count", "core_layout_count",
]


def windows_from_config(cfg) -> List[tuple]:
    """``analysis.windows`` of the yaml ({label: [first, last]}) as the archive's [(label, lo, hi)] list.

    Ported from: a2.py:WINDOWS (the same five bounds, now read from labelling_analysis.yaml)."""
    return [(name, lo, hi) for name, (lo, hi) in cfg.analysis["windows"].items()]


def window_of(year: float, windows) -> Optional[str]:
    """The window a priority year falls in (None outside every window, or for a NaN year).

    ``windows`` is a list of (label, first, last) as returned by :func:`windows_from_config`.
    Ported from: a2.py:window_of (the archive defaulted to its WINDOWS constant; here it is required)."""
    for name, lo, hi in windows:
        if pd.notna(year) and lo <= year <= hi:
            return name
    return None


def rotor_bin(units: pd.Series) -> pd.Series:
    """Propulsor units -> 1-3 / 4 / 5-6 / 7-8 / 9+ (strings; NaN stays NaN, never 0).

    Ported from: a2.py:rotor_bin"""
    u = pd.to_numeric(units, errors="coerce")
    return pd.cut(u, bins=ROTOR_BINS[0], labels=ROTOR_BINS[1]).astype(object).where(u.notna())


def _s(v) -> str:
    """Cell -> stripped string; None/NaN/NA/"nan"/"None"/"NaT" -> "". Ported from: a2.py:_s"""
    if v is None or v is pd.NA or (isinstance(v, float) and np.isnan(v)):
        return ""
    s = str(v).strip()
    return "" if s in ("nan", "None", "NaT", "<NA>") else s


def _n(v) -> int:
    """Cell -> int; blank/"False" -> 0, "True" -> 1, unparsable -> 0. Ported from: a2.py:_n"""
    s = _s(v)
    if s in ("", "False"):
        return 0
    if s == "True":
        return 1
    try:
        return int(float(s))
    except ValueError:
        return 0



def _reason_of(note: str) -> str:
    """Notebook 04's ``propulsor_units_note`` -> one short reason (the first that applies).  Ported from: a2.py:_reason_of"""
    if re.match(r"^(HB|PFV):", note):
        return LEFT_OUT_HBPFV
    if "G1 override" in note:
        return LEFT_OUT_G1
    if "without a quick count" in note:
        return LEFT_OUT_M3_COUNT
    return note



def propulsor_units(v: pd.DataFrame) -> pd.DataFrame:
    """Total non-control propulsors per aircraft (rule 1), and why a blank is blank.

    Read from notebook 04's ``propulsor_units``: the quick count on a count-only
    (overridden) station; blank for HB/PFV (the codebook gives them no propulsor record),
    after a G1 override, and when an overridden station has no quick count. A blank is
    never read as 0. Columns ``units`` (float, NaN = left out) and ``left_out`` (reason).

    A recorded 0 is not a count either (rerun of 2026-10-15, author's ruling): the one design so recorded (GB202302720D0_ua1,
    Stopped/Slowed Rotor Wing) carries an M2 override that hid its wing-borne propulsors, which were never counted. It is left out
    (NaN, ``left_out`` = ``LEFT_OUT_ZERO``) of the band U and of everything that reads ``units``; no 0 band exists.
    

    Ported from: a2.py:propulsor_units"""
    if "propulsor_units" in v.columns:
        units = pd.to_numeric(v["propulsor_units"], errors="coerce").astype(float)
        note = v.get("propulsor_units_note", pd.Series("", index=v.index)).map(_s)
        reason = [(_reason_of(n) or "not determinable") if pd.isna(u) else "" for u, n in zip(units, note)]
        return _zero_left_out(pd.DataFrame({"units": units, "left_out": reason}, index=v.index))
    # batch-reader fallback: the loader already put the quick count on an overridden station
    counts = [c for c in PROPULSOR_UNIT_COLUMNS if c in v.columns]
    units = v[counts].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=len(counts))
    tt, ov = v["topType"].map(_s), override_sets(v)
    reason = [LEFT_OUT_HBPFV if t in NO_UNITS_TYPES else LEFT_OUT_G1 if "G1" in o
              else LEFT_OUT_M3_COUNT if pd.isna(u) else "" for t, o, u in zip(tt, ov, units)]
    units = units.where(pd.Series(reason, index=v.index).eq(""))
    return _zero_left_out(pd.DataFrame({"units": units.astype(float), "left_out": reason}, index=v.index))




#: why a recorded 0 propulsors is left out (rerun of 2026-10-15)
LEFT_OUT_ZERO = "0 recorded: the count was never entered (M2 override)"


def _zero_left_out(pu: pd.DataFrame) -> pd.DataFrame:
    """A recorded 0 propulsors is a missing answer, never a count: units -> NaN, with its reason."""
    zero = pu["units"].eq(0)
    pu.loc[zero, "units"] = np.nan
    pu.loc[zero, "left_out"] = LEFT_OUT_ZERO
    return pu

def _boom_categories(r: pd.Series, tilting_wings: set) -> set:
    """Notebook 04's boom classes per (propeller-carrying boom group x boom-card rotor type):
    on_tilting_wing, tilting (group ticked Booms tilt, or rotor propKin Tilt) or fixed.

    Ported from: a2.py:_boom_categories"""
    g = lambda c: r[c] if c in r.index else None
    groups = []
    for k in range(1, 7):
        att, cnt = _s(g(f"boom{k}_attach")), _n(g(f"boom{k}_count"))
        if (not att and cnt == 0) or _s(g(f"boom{k}_hasProps")) == "False":
            continue
        wi = _s(g(f"boom{k}_wingIdx"))
        rides = (att in ("Wings", "Both") and bool(tilting_wings) and _s(g(f"boom{k}_onFixedPart")) != "True"
                 and (wi in ("", "Multi") or (re.fullmatch(r"W\d", wi) is not None and int(wi[1]) in tilting_wings)))
        groups.append((rides, _s(g(f"boom{k}_tilts")) == "True"))
    nt = _n(g("boom_ntypes")) or 1
    kinds = []
    for pre in ([f"boom_t{t}_" for t in range(1, nt + 1)] if nt > 1 else ["boom_"]):
        if _n(g(pre + "count")) > 0 and _s(g(pre + "ctrlOnly")) != "True":
            kinds.append(_s(g(pre + "propKin")))
    cats = set()
    for pk in kinds:
        for rides, ticked in (groups or [(False, False)]):
            cats.add("on_tilting_wing" if rides else "tilting" if (ticked or pk == "Tilt") else "fixed")
    return cats


def _boom_state(cats: set) -> str:
    """Boom categories -> "none" / the single category / "mixed". Ported from: a2.py:_boom_state"""
    if not cats:
        return "none"
    return next(iter(cats)) if len(cats) == 1 else "mixed"


def propulsion_states(v: pd.DataFrame) -> pd.DataFrame:
    """Per aircraft: a tilting thrust source? a fixed one? a ducted unit? all units ducted?

    A thrust source is every propulsion card (or each of its propeller types) with units that
    are not control-only. It TILTS when the propulsor pivots on its own mount (propKin Tilt),
    sits on a tilting wing, is on the empennage and the empennage tilts, or is on the boom
    card and ``boom_thrust_state`` says so (rule 3, 2026-09-19: the boom tick carries the
    tilt, so the boom card is read from notebook 04's state and never from the raw boom
    propKin). Otherwise it is FIXED (user ruling 2026-09-18).

    Rule 1 (2026-09-19): a value an override hides is not determinable, and it is never read
    as none or Fixed. A count-only (M3 override) station has no tilt or duct detail; an M2
    override hides the wing tilt; an M1 override hides the boom groups. An aircraft with no
    propulsor record at all (HB/PFV by codebook, or nothing entered) has no answer either.
    Each answer is True when a recorded source shows it, <NA> when a hidden part could
    change it, else False; ``left_out`` gives the reason for a <NA> tilt answer.
    

    Ported from: a2.py:propulsion_states"""
    ovs = override_sets(v)
    bmech = [c for c in v.columns if c.endswith("_bmech")]
    has_state = "boom_thrust_state" in v.columns
    rows = []
    for (_, r), ov in zip(v.iterrows(), ovs):
        g = lambda c: r[c] if c in r.index else None
        if _s(g("topType")) in NO_UNITS_TYPES:
            rows.append((pd.NA, pd.NA, pd.NA, pd.NA, LEFT_OUT_HBPFV))
            continue
        tw = {k for k in range(1, 5) if _s(g(f"wing{k}_tilt")) == "Tilt"}
        tilt = fixed = recorded = False
        why = []                                   # hidden parts that could carry an answer
        hidden_station = False
        for card in M3_STATIONS:
            if f"M3:{card}" in ov:
                q = _s(g(f"{card}_quickCount"))
                if not q or _n(q) > 0:             # units there, of unknown kind
                    hidden_station = True
                    recorded |= bool(q)
                    why.append(LEFT_OUT_M3 if q else LEFT_OUT_M3_COUNT)
                continue
            if card == "boom":
                continue                           # rule 3: read below from boom_thrust_state
            nt = _n(g(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                if _n(g(pre + "count")) <= 0 or _s(g(pre + "ctrlOnly")) == "True":
                    continue
                recorded = True
                pk = _s(g(pre + "propKin"))
                if pk == "Tilt":
                    tilt = True
                elif card.startswith("wing") or card == "emp":
                    if "M2" in ov:
                        why.append(LEFT_OUT_M2)
                    elif (card == "emp" and _s(g("empTilts")) == "True") or \
                            (card.startswith("wing") and int(card[4:]) in tw):
                        tilt = True
                    else:
                        fixed = True
                else:
                    fixed = True
        if "M3:boom" not in ov:
            state = _s(g("boom_thrust_state")) if has_state else ""
            if not state and "M1" not in ov:       # no notebook-04 state: the same rule, computed here
                state = _boom_state(_boom_categories(r, tw))
            if state == "":                        # an M1 override hides the boom groups
                nt = _n(g("boom_ntypes")) or 1
                pks = [_s(g(p + "propKin")) for p in ([f"boom_t{t}_" for t in range(1, nt + 1)] if nt > 1 else ["boom_"])
                       if _n(g(p + "count")) > 0 and _s(g(p + "ctrlOnly")) != "True"]
                if pks:
                    recorded = True
                    tilt |= "Tilt" in pks
                    why.append(LEFT_OUT_M1)
            elif state != "none":
                recorded = True
                tilt |= state in ("tilting", "on_tilting_wing", "mixed")
                fixed |= state == "fixed" or (state == "mixed" and "fixed" in _boom_categories(r, tw))
        if not recorded and not hidden_station:
            rows.append((pd.NA, pd.NA, pd.NA, pd.NA, LEFT_OUT_NONE))
            continue
        vals = [_s(g(c)) for c in bmech]
        ducted, open_ = "Ducted" in vals, "Open" in vals
        any_tilt = True if tilt else (pd.NA if why else False)
        any_fixed = True if fixed else (pd.NA if why else False)
        any_ducted = True if ducted else (pd.NA if hidden_station else False)
        all_ducted = False if open_ else (pd.NA if hidden_station else ducted)
        rows.append((any_tilt, any_fixed, any_ducted, all_ducted, "" if any_tilt is not pd.NA else why[0]))
    out = pd.DataFrame(rows, columns=["any_tilting", "any_fixed", "any_ducted", "all_ducted", "left_out"],
                       index=v.index)
    for c in ("any_tilting", "any_fixed", "any_ducted", "all_ducted"):
        out[c] = out[c].astype("boolean")
    return out



def archetype_columns(variants: pd.DataFrame) -> pd.DataFrame:
    """The three archetype fields ``base`` needs, one row per variant that has a ``topType``:
    ``aircraft_id``, ``rotorBin`` (propulsor units binned; HB/PFV = "n/a (no M3 card)"),
    ``anyTilt`` (True/False, None when not determinable, "n/a (no M3 card)" for HB/PFV) and
    ``nBooms`` (sum of boom1_count..boom6_count, the M1 structural count).

    Ported from: a2.py:archetype_frame (only the columns rotorBin, anyTilt, nBooms; boomBin and the
    other archetype fields were never used by base and are not computed)."""
    v = variants[variants["topType"].notna()].copy()
    boom_cols = [c for c in v.columns if re.match(r"boom\d_count$", c)]
    v["nBooms"] = v[boom_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1).astype(int)
    ts = propulsion_states(v)[["any_tilting", "any_fixed", "left_out"]]
    v["anyTilt"] = ts["any_tilting"].astype(object).where(ts["any_tilting"].notna(), None)
    v.loc[ts["left_out"].eq(LEFT_OUT_HBPFV), "anyTilt"] = NO_M3_CARD
    pu = propulsor_units(v)
    v["rotorBin"] = rotor_bin(pu["units"])
    v.loc[pu["left_out"].eq(LEFT_OUT_HBPFV), "rotorBin"] = NO_M3_CARD
    return v[["aircraft_id", "rotorBin", "anyTilt", "nBooms"]]


# ------------------------------------------------------------- filer type ---
# Who filed, read off the RAW PatSeer assignee string (not off company_canonical). Ported from
# la_tables.py (audit of 2026-09-23): the type is a different question from the firm's identity.
# Everything between here and the frame is copied unchanged from la_tables.py lines 81-266.

#: Universities, institutes, academies and national research agencies, read on the raw string.
#: Tested first, because an institute also carries a legal form ("... RESEARCH INSTITUTE CO LTD").
ASSIGNEE_INSTITUTE_RE = re.compile(r"""(?ix)
    \buniv\b | universi | universid | universita | universiteit | uniwersytet
  | \binst\b | \binstitut | \bistituto\b | \bhochschule\b | \bakadem | \bacademy\b
  | \bcollege\b | \bschool\b | polytech | \bdaigaku\b | \bgakuen\b
  | research \s+ (institute|inst\b|center|centre|establishment|organi[sz]ation|laborator|academy|council)
  | \b(res|rech) \s* (&|and)? \s* (development|dev) \s+ inst | \bres \s+ inst\b
  | national \s+ laborator | academy \s+ of \s+ sciences
  | \bkaist\b | \bkari\b | \bnasa\b | \bjaxa\b | \bonera\b | \bdlr\b | \bcnrs\b | \bcsic\b
  | \btsagi\b | \bcasic\b | \bnuaa\b | \bnudt\b | \bchrdi\b | comac \s+ research
  | national \s+ aeronautics | aerospace \s+ exploration | aerospace \s+ res
  | office \s+ national | agency \s+ .* \bdev | \bstichting\b | \bustav\b | zkusebni
  | aerogidrodinamicheskij | federalnoe \s+ gosudarstvennoe
  | 研究院 | 大学 | 學院 | 대학
""")

#: Legal forms, office by office -- US, CN, DE, JP, KR, FR, GB, IT, RU, IL, ES, CA and every other
#: office that files in the corpus. A legal form sits at the END of a name, so it is read only in
#: the last two tokens: that is what keeps a personal name such as "LUO AO" out of the company band
#: while "RAYTHEON CO", "AGUSTA SPA", "AISAN KOGYO KK", "PRADES IMASD SL" and "NORAERO AS" leave it.
ASSIGNEE_LEGAL_TOKENS = frozenset({
    # US / CA / GB / AU / IN — anglophone
    "inc", "incorporated", "llc", "llp", "lp", "pllc", "corp", "corporation", "co", "company",
    "companies", "ltd", "limited", "ltee", "ulc", "plc", "holding", "holdings", "trust",
    "pvt", "pte", "private", "pty", "pl",
    # DE / AT / CH
    "gmbh", "mbh", "ag", "kg", "kgaa", "gbr", "ohg", "ug", "se", "ev", "eg", "og",
    # FR / BE / LU
    "sa", "sas", "sasu", "sarl", "eurl", "snc", "scp", "sprl", "bvba",
    # IT
    "spa", "srl", "srls", "scarl", "sapa",
    # ES / PT / BR
    "sl", "slu", "sau", "lda", "ltda",
    # NL
    "bv", "nv", "cv", "coop",
    # SE / NO / DK / FI
    "ab", "asa", "aps", "oy", "oyj", "ky", "hb", "kb", "as",
    # CZ / SK / PL / HU
    "sro", "spol", "zoo", "kft", "zrt",
    # RU / UA / LT
    "ooo", "oao", "zao", "pao", "tov", "uab",
    # JP / KR
    "kk", "kabushiki", "kaisha", "gk",
    # IL / TR
    "bam", "sti",
})
#: Words that name an organisation wherever they stand in the string — an activity, not a person.
ASSIGNEE_ORG_WORDS = frozenset({
    "technology", "technologies", "tech", "techno", "technik", "technologie", "technologia",
    "aviation", "aviat", "aerospace", "aeronautics", "aeronautic", "aeronautical", "aero",
    "aircraft", "airplane", "aeroplane", "helicopter", "helicopters", "rotorcraft", "avia",
    "flight", "flying", "drone", "drones", "uav", "rotor", "propulsion", "turbine", "engines",
    "air", "airways", "airlines", "airspace", "airborne", "mobility", "aerodynamics", "flugzeug",
    "systems", "system", "solutions", "services", "service", "labs", "laboratory", "laboratories",
    "industrial", "industries", "industry", "ind", "manufacturing", "mfg", "mft", "works",
    "center", "centre", "research", "rech", "res", "development", "dev", "design", "designs",
    "engineering", "eng", "ingenieria", "ingenieurgesellschaft", "ingegneria", "luftfahrttechnik",
    "leichtbau", "energy", "power", "electric", "electrical", "electronics", "photonics",
    "robotics", "capital", "ventures", "venture", "innovation", "innovations", "innovative",
    "group", "international", "int", "global", "national", "nationaal", "state", "sist",
    "motor", "motors", "automobile", "automotive", "machinery", "equipment", "defense", "defence",
    "agency", "administration", "office", "bureau", "ministry", "federal", "govt", "government",
    "sciences", "science", "sci", "scientific", "logistics", "transport", "network", "enterprise",
    "enterprises", "partners", "partnership", "kogyo", "seisakusho", "sanayi", "ticaret",
    "obshchestvo", "obshhestvo", "aktsionernoe", "aktsionernoye", "predpriyatie", "kompaniya",
    "objedinenie", "obedinenie", "gosudarstvennoe", "unitarnoe", "sociedad", "cia",
})
#: Multi-word legal forms, and the ones written in a non-Latin script (CJK, Hangul, Cyrillic).
ASSIGNEE_ORG_RE = re.compile(r"""(?ix)
    \bs \s?\.?\s? p \s?\.?\s? a\b | \bs \s?\.?\s? r \s?\.?\s? l\b | \bs \s?\.?\s? a \s?\.?\s? s\b
  | \bs \s+ r \s+ o\b | \bsp \s+ z \s+ o+\b | \bd \s?\.?\s? o \s?\.?\s? o\b | \ba \s?/\s? s\b
  | 株式会社 | 有限会社 | 合同会社 | 工業 | 産業 | 주식회사 | 유한회사 | 인크 | 코퍼레이션
  | 公司 | 集团 | 有限
  | товариство | обществ | акционер | акціонер | компан | концерн | предприят
""")
#: Name particles: part of one person's name, so they do not count towards the five-word cap
#: ("DE LA BROISE DENIS PIERRE MARIE" is one Frenchman, not a six-word company description).
ASSIGNEE_NAME_PARTICLES = frozenset({
    "de", "del", "della", "di", "da", "das", "dos", "du", "la", "le", "van", "von", "der",
    "den", "ten", "ter", "af", "av", "al", "el", "bin", "ibn", "ben", "abu", "mac", "mc", "st",
})
#: The four filer types, in the order every table and figure prints them. The fourth band held the
#: aircraft whose assignee string never matched grouper.py's list until 2026-09-23; it now means
#: what it says, and in this corpus it is empty -- every one of the 665 aircraft names an assignee.
FILER_TYPES = ["Named company", "University / institute", "Individual inventor", "No assignee named"]
NO_ASSIGNEE = FILER_TYPES[3]

_ASSIGNEE_PUNCT = re.compile(r"[^\w\s]+", re.UNICODE)
_ASSIGNEE_CJK = re.compile(r"[぀-鿿가-힯]")


def first_assignee(raw) -> str:
    """The first assignee of a PatSeer string, with the trailing ``(CITY, CC)`` / ``(CC)`` gone.

    Same convention as ``grouper.py::_preprocess_assignee``, so the type and the firm identity are
    read off the same entity: PatSeer joins co-assignees with ``; `` and the first is the filer.

    Ported from: la_tables.py:first_assignee
    """
    s = "" if raw is None else str(raw).strip()
    if s.lower() in ("", "nan", "none"):
        return ""
    s = s.split(";")[0].strip()
    return re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()


def _assignee_tokens(s: str) -> List[str]:
    """Lower-cased word tokens of an assignee string, punctuation removed. Ported from: la_tables.py:_assignee_tokens"""
    return [t for t in _ASSIGNEE_PUNCT.sub(" ", s).lower().split() if t]


def filer_from_assignee(raw) -> str:
    """One of :data:`FILER_TYPES`, from the raw assignee string.

    Order: institute, then organisation (non-Latin or multi-word legal form, an activity word
    anywhere, a legal form in the last two tokens, a digit, or more than five name words), then
    individual. A lone Latin token is a brand and not a person -- PatSeer writes people
    "SURNAME GIVENNAME" -- while a lone CJK/Hangul token is a personal name.

    Ported from: la_tables.py:filer_from_assignee
    """
    s = first_assignee(raw)
    if not s:
        return NO_ASSIGNEE
    if ASSIGNEE_INSTITUTE_RE.search(s):
        return "University / institute"
    if ASSIGNEE_ORG_RE.search(s):
        return "Named company"
    toks = _assignee_tokens(s)
    if any(t in ASSIGNEE_ORG_WORDS for t in toks):
        return "Named company"
    if any(t in ASSIGNEE_LEGAL_TOKENS for t in toks[-2:]):
        return "Named company"
    if any(ch.isdigit() for ch in s):
        return "Named company"
    name = [t for t in toks if t not in ASSIGNEE_NAME_PARTICLES]
    if len(name) < 2:                 # the particle list must never eat a two-word name ("XU BIN")
        name = toks
    if len(name) > 5:
        return "Named company"
    if len(name) == 1:
        return "Individual inventor" if _ASSIGNEE_CJK.search(s) else "Named company"
    return "Individual inventor"


#: PatSeer's abbreviations, expanded so two spellings of one firm collapse to one name.
ASSIGNEE_EXPAND = {
    "tech": "technology", "techn": "technology", "technologies": "technology", "aviat": "aviation",
    "aeronaut": "aeronautics", "aeronautic": "aeronautics", "ind": "industries", "inds": "industries",
    "mfg": "manufacturing", "mft": "manufacturing", "int": "international", "intl": "international",
    "sci": "science", "univ": "university", "res": "research", "rech": "research",
    "inst": "institute", "dev": "development", "eng": "engineering", "sys": "systems",
    "syst": "systems", "sist": "systems", "corp": "corporation",
}
#: The firms whose raw-string name is a second spelling of a canonical name already on the list.
#: Folded by hand, because the alternative is a second fuzzy layer on firm identity and firm
#: identity feeds the firm tiers, the proximity matrix and the AAM Reality Index join. Ten strings,
#: every one checked against the patent. The durable fix is upstream, in grouper.py's table.
FIRM_ALIASES = {
    "Airbus Urban Mobility": "Airbus",
    "Safran Helicopter Engines": "Safran",
    "Leonardo Uk": "Leonardo",
    "Foshan Shenfeng Aviation Technology": "Shenfeng Aviation",
    "Foshan Shenfeng Aviation Science Technology": "Shenfeng Aviation",
    "Xian Innno Aviation Technology": "Xi'an Inno Aviation",       # PatSeer typo for XIAN INNO
    "Beijing Aeronautics Science Technology Research Institute Of Comac": "COMAC Research Institute",
    "Autoflightx International": "AutoFlight",
    "위스퍼 에어로 인크": "Whisper Aero",                              # Whisper Aero Inc, in Hangul
    "Texas A M University Systems": "Texas A M University",
    "Volkswagen Automotive": "Volkswagen",
    "Office National Detudes Et De Research Aerospatiales Onera": "Office National Detudes Research Aerospatiales",
}
_ASSIGNEE_TRAILING = ASSIGNEE_LEGAL_TOKENS | {"and"}


def firm_from_assignee(raw) -> str:
    """A firm name for an organisation grouper.py's table does not hold: the first assignee with
    the country code and the legal form removed, PatSeer's abbreviations expanded, title-cased.

    Ported from: la_tables.py:firm_from_assignee"""
    s = first_assignee(raw)
    if not s:
        return ""
    toks = [ASSIGNEE_EXPAND.get(t, t) for t in _assignee_tokens(s)]
    while toks and toks[-1] in _ASSIGNEE_TRAILING:
        toks.pop()
    if toks and toks[0] == "the":
        toks = toks[1:]
    toks = [t for t in toks if t not in _ASSIGNEE_TRAILING] or _assignee_tokens(s)
    name = " ".join(toks).title()
    return FIRM_ALIASES.get(name, name)



# ----------------------------------------------- which assignee a design is given to (rule of 2026-10-15) ---
_TOOLS_SRC = Path(__file__).resolve().parents[3] / "Patent-Labelling-Tools" / "src"


def _load_tool(name: str):
    """grouper.py / patent_geography.py of the labelling tools, loaded by path (the existing grouper, unchanged)."""
    import importlib.util
    import warnings
    spec = importlib.util.spec_from_file_location(f"_tools_{name}", _TOOLS_SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    root = str(_TOOLS_SRC.parent)
    added = root not in sys.path
    if added:
        sys.path.insert(0, root)              # patent_geography.py imports ``src.grouper``
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec.loader.exec_module(mod)
    finally:
        if added:
            sys.path.remove(root)
    return mod


def co_assignees(raw) -> List[str]:
    """Every assignee of a PatSeer string (joined by ``;``), in the order listed."""
    s = "" if raw is None else str(raw).strip()
    if s.lower() in ("", "nan", "none"):
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


def design_assignees(identity: pd.DataFrame) -> pd.DataFrame:
    """Per patent, the assignee its design goes to (author's rule 2026-10-15; before it was the first one listed).

    Every co-assignee is resolved to its canonical name with grouper.py (an organisation it does not list gets the name
    :func:`firm_from_assignee` derives). The design goes to the co-assignee that files the most patent FAMILIES in the whole
    dataset (``identity``, every patent); a tie keeps the first listed. An individual inventor counts only when no organisation
    is on the patent. Columns: patent_id, assignee_chosen (the co-assignee's own string), firm (canonical name, None for an
    individual), canon (grouper's name), country (the chosen co-assignee's country code, if it prints one), n_co, changed.

    Ported from: new (Analysis V, 2026-10-15)"""
    g = _load_tool("grouper")
    geo = _load_tool("patent_geography")
    rows = []
    for pid, raw, fam in zip(identity["patent_id"], identity["assignee_raw"], identity["family_id"]):
        cos = []
        for sraw in co_assignees(raw):
            canon = g._normalise_company(sraw)
            typ = filer_from_assignee(sraw)
            resolved = canon not in CATCH_ALL
            org = resolved or typ in ("Named company", "University / institute")
            name = canon if resolved else (firm_from_assignee(sraw) or None) if org else None
            key = name if name else "person:" + first_assignee(sraw).lower()
            cos.append(dict(raw=sraw, canon=canon, org=org, name=name, key=key))
        rows.append((pid, fam, cos))
    fams: Dict[str, set] = {}
    for pid, fam, cos in rows:
        for c in cos:
            fams.setdefault(c["key"], set()).add(fam if pd.notna(fam) else pid)
    out = []
    for pid, fam, cos in rows:
        pool = [c for c in cos if c["org"]] or cos
        best = None
        for c in pool:                                  # strictly greater: a tie keeps the first listed
            if best is None or len(fams[c["key"]]) > len(fams[best["key"]]):
                best = c
        if best is None:
            out.append(dict(patent_id=pid, assignee_chosen="", firm=None, canon=None, country=None, n_co=0, changed=False))
            continue
        m = geo._ASSIGNEE_CC_RE.search(best["raw"])
        out.append(dict(patent_id=pid, assignee_chosen=best["raw"], firm=best["name"], canon=best["canon"],
                        country=m.group(1) if m else None, n_co=len(cos), changed=best is not cos[0],
                        region_by_country=geo.REGION_BY_COUNTRY.get(m.group(1)) if m else None))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ frames --
def base(ds, cfg, fold: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """One row per unique aircraft with year, window, region, filer, firm, class and the derived
    propulsion fields; the frame every table and figure starts from.

    ``cfg.analysis["windows"]`` gives the windows, ``cfg.analysis["class_fold"]`` the G1 -> class5
    fold unless ``fold`` is passed. Columns are the variants' own, then identity columns, then
    rotorBin/anyTilt/nBooms, any_tilting/any_ducted/any_fixed, units, year, window, region3, filer,
    firm, company_canonical_grouper, company_canonical (= firm), named, filer_id, class5, archetype,
    lapsed, granted.

    Ported from: la_tables.py:base
    """
    windows = windows_from_config(cfg)
    fold = cfg.analysis["class_fold"] if fold is None else fold
    af = archetype_columns(ds.variants)
    v = ds.variants.merge(
        ds.identity[["patent_id", "priority_year", "region", "assignee_country", "company_canonical",
                     "assignee_raw",
                     "legal_status_raw", "pub_office", "industry_primary", "claim_count", "forward_citations",
                     "backward_citations", "forward_citations_in_corpus", "self_citations_in_corpus", "family_size",
                     "kind_code"]],
        on="patent_id", how="left", suffixes=("", "_id"))
    v = v.merge(af, on="aircraft_id", how="left")
    # the design goes to the co-assignee that files the most families (rule of 2026-10-15); the PatSeer string stays as assignee_raw_all
    da = design_assignees(ds.identity).set_index("patent_id")
    v["assignee_raw_all"] = v["assignee_raw"]
    v["assignee_raw"] = v["patent_id"].map(da["assignee_chosen"])
    v["company_canonical"] = v["patent_id"].map(da["canon"])
    own = v["patent_id"].map(da["country"])
    v["assignee_country"] = own.where(own.notna(), v["assignee_country"])
    v["region"] = v["patent_id"].map(da["region_by_country"]).where(own.notna() & v["patent_id"].map(da["region_by_country"]).notna(), v["region"])
    ps = propulsion_states(ds.variants)
    for c in ("any_tilting", "any_ducted", "any_fixed"):
        v[c] = ps[c].to_numpy()
    v["units"] = propulsor_units(ds.variants)["units"].to_numpy()
    v["year"] = pd.to_numeric(v["priority_year"], errors="coerce")
    v["window"] = v["year"].map(lambda y: window_of(y, windows))
    v["region3"] = v["region"].where(v["region"].isin(REGIONS), "Other regions")
    # who filed (type, from the raw assignee string) and which firm (identity: the grouper's canonical
    # name where it resolved a real firm, else a name derived from the assignee string)
    cc = v["company_canonical"]
    raw = v["assignee_raw"]
    v["filer"] = raw.map(filer_from_assignee)
    resolved = cc.notna() & ~cc.isin(CATCH_ALL)
    is_org = v["filer"].isin(["Named company", "University / institute"])
    v["firm"] = np.where(resolved, cc, np.where(is_org, raw.map(firm_from_assignee), None))
    v.loc[v["firm"].isin(["", "None"]) | v["firm"].isna(), "firm"] = None
    # the grouper's own field is kept under its own name; company_canonical carries the firm identity
    v["company_canonical_grouper"] = cc
    v["company_canonical"] = v["firm"]
    v["named"] = v["firm"].notna()
    # a filer id: the firm for an organisation, the patent for everyone else
    v["filer_id"] = np.where(v["named"], v["firm"].fillna(""), "patent:" + v["patent_id"].astype(str))
    v["class5"] = v["topType"].map(fold)
    # display: the bottom propulsor bin prints "1-3" (ROTOR_BINS and UNIT_BANDS now share the name; kept as a 1:1 rename)
    v["rotorBin"] = v["rotorBin"].replace(ROTOR_BINS[1][0], UNIT_BANDS[1][0])
    v["archetype"] = np.where(v["topType"].notna() & v["rotorBin"].notna(),
                              v["topType"].astype(str) + " · " + v["rotorBin"].astype(str), None)
    # (until 2026-10-15 the one design recorded with 0 propulsors printed its class's bottom key as " · 0-3"; that 0 is now left out
    # by propulsor_units, so every bottom key reads " · 1-3")
    status = v["legal_status_raw"].fillna("").astype(str)
    v["lapsed"] = status.str.startswith("INACTIVE")
    v["granted"] = status.str.contains("GRANTED")
    return v


def firm_sizes(v: pd.DataFrame) -> pd.Series:
    """Unique aircraft per firm, largest first. A firm is any organisation that filed: the canonical
    name where grouper.py resolved one, the assignee's own name where it did not.

    Ported from: la_tables.py:firm_sizes"""
    return v.loc[v["named"], "firm"].value_counts()


def patent_firm(v: pd.DataFrame) -> pd.Series:
    """``patent_id`` -> firm identity, read off the analysis frame (the stored ``company_canonical`` of
    ds.identity is the grouper's field and holds a placeholder for every organisation it does not list).

    Ported from: la_tables.py:patent_firm"""
    return v.dropna(subset=["firm"]).drop_duplicates("patent_id").set_index("patent_id")["firm"]


# =====================================================================================================
# Question 1 (growth, protection, fidelity): wrangling behind notebook 40
# Every function below only joins, filters and counts; the statistics come from lib/.
# =====================================================================================================
import datetime as _dt                                   # noqa: E402
from pathlib import Path as _Path                        # noqa: E402

from lib import growth as _growth                        # noqa: E402

#: the index release year: a first flight dated after it is a plan, not a flight.
#: Ported from: sm_index.py:ARI_RELEASE_YEAR
ARI_RELEASE_YEAR = 2026

#: NASA TRL bands of Table 3. Ported from: a2.py:TRL_BANDS
TRL_BANDS = [("TRL 2", (2,)), ("TRL 3-5", (3, 4, 5)), ("TRL 6-7", (6, 7)), ("TRL 8-9", (8, 9))]

#: the six attributes of the representativeness tables (Tables 4 and 5), (printed name, column of base()).
#: Ported from: la_tables.py:LINKED_CATEGORICAL / LINKED_CONTINUOUS
REP_CATEGORICAL = [("folded class", "class5"), ("applicant region", "region3"),
                   ("priority window", "window"), ("filer type", "filer")]
REP_CONTINUOUS = [("priority year", "year"), ("propulsive units", "units")]

#: the class of the evtol.news directory, in the order the tables and the figure print them
#: Ported from: sm_open.py:CLASS5_ORDER, la_tables.py:FOLD5_NAMES
CLASS5_ORDER = ["LC", "VT", "WM", "ER", "HB"]
CLASS5_NAMES = {"VT": "Vectored Thrust", "LC": "Lift + Cruise", "WM": "Wingless (Multicopter)",
                "ER": "Electric Rotorcraft", "HB": "Hover Bikes / Personal Flying Devices"}

#: priority-year bounds of the legal-status reading (the seven-year rule of 1.2). Ported from: sm_open.py:FORCE_MAX_YEAR
FORCE_MAX_YEAR = 2019
#: a class enters the class x out-of-force test with this many aircraft. Ported from: sm_open.py:FORCE_TEST_MIN
FORCE_TEST_MIN = 10


def snapshot_date(ds) -> str:
    """The PatSeer snapshot date of the dataset, 'YYYY-MM-DD'. Ported from: numbers.py:live (n['snapshot'])."""
    snap = ds.identity["snapshot_date"].dropna()
    return str(snap.iloc[0])[:10] if len(snap) else "unknown"


def publication_lag(ds, by: Optional[str] = None) -> pd.DataFrame:
    """Years from priority to publication of the representative primary patents, one row per patent
    (``by=None``), or summarised per ``by`` (median and 90th percentile, rounded to whole years).

    Ported from: a2.py:d9_publication_lag (summary, ``by="region"``) and la_tables.py:lag_p90 (rows)."""
    j = ds.patents_analysis.merge(
        ds.identity[["patent_id", "priority_year", "pub_year", "region", "pub_office"]],
        on="patent_id", how="left", suffixes=("", "_id"))
    year = j["pub_year"] if "pub_year" in j else j["pub_year_id"]
    j = j.assign(lag=pd.to_numeric(year, errors="coerce") - pd.to_numeric(j["priority_year"], errors="coerce"))
    if by is None:
        return j
    g = j.dropna(subset=["lag"]).groupby(by)["lag"]
    out = pd.DataFrame({"patents": g.size(), "median lag": g.median().round(0),
                        "90th percentile": g.quantile(0.90).round(0)})
    return out.sort_values("patents", ascending=False).reset_index()


def read_baseline(cfg, key: str) -> pd.Series:
    """One worldwide baseline as a year-indexed count series.

    ``baseline_patseer_b64`` / ``baseline_patseer_sectionb``: PatSeer simple families (CPC B64, CPC
    section B) by earliest priority year; ``baseline_world``: WIPO families of all patents (column ``world``).

    Ported from: la_baseline.py:series (PATSEER_WORLD, PATSEER_WORLD_B, WIPO_WORLD_ALL)."""
    u = pd.read_csv(cfg.path(key))
    if key == "baseline_world":
        return u.set_index("y")["world"].sort_index()
    u.columns = ["year", "count"]
    return u.set_index("year")["count"].sort_index()


def filings_per_year(ds, v: pd.DataFrame, cfg) -> pd.DataFrame:
    """Per priority year: unique aircraft by applicant region, patents acquired, representative
    patents, whether the year is complete, and the aeronautics (B64) baseline with its ratios.

    A year is complete when the snapshot lies at least the 90th-percentile publication lag after its end
    (lib.growth.lag_quantile / year_is_complete). ``index`` = priority year. Counts of the pooled early
    years stay separate rows; the figure pools them for display.

    Ported from: la_tables.py:filings_per_year, la_baseline.py:attach"""
    snapshot = snapshot_date(ds)
    p90 = _growth.lag_quantile(publication_lag(ds)["lag"])
    w = v.dropna(subset=["year"]).copy()
    w["year"] = w["year"].astype(int)
    tab = pd.crosstab(w["year"], w["region3"]).reindex(columns=REGIONS + ["Other regions"], fill_value=0)
    acq = ds.patents.merge(ds.identity[["patent_id", "priority_year"]], on="patent_id", how="left", suffixes=("", "_id"))
    acq_y = pd.to_numeric(acq["priority_year"], errors="coerce").dropna().astype(int).value_counts()
    rep_y = pd.to_numeric(acq.loc[acq["is_representative"].fillna(False), "priority_year"],
                          errors="coerce").dropna().astype(int).value_counts()
    years = range(int(tab.index.min()), int(tab.index.max()) + 1)
    tab = tab.reindex(years, fill_value=0)
    tab["unique aircraft"] = tab[REGIONS + ["Other regions"]].sum(axis=1)
    tab["patents acquired"] = acq_y.reindex(years, fill_value=0).to_numpy()
    tab["patents representative"] = rep_y.reindex(years, fill_value=0).to_numpy()
    elapsed, complete = _growth.year_is_complete(list(years), p90, snapshot)
    tab["years since year end"], tab["complete"] = elapsed, complete
    b = read_baseline(cfg, "baseline_patseer_b64").reindex(tab.index)
    tab["B64 families (worldwide)"] = b.astype("Int64")
    tab["aircraft per 1 000 B64"] = _growth.per_thousand(tab["unique aircraft"], b)
    tab["patents per 1 000 B64"] = _growth.per_thousand(tab["patents acquired"], b)
    tab["eVTOL index (2005-09 = 100)"] = _growth.index_to_base(tab["patents acquired"].astype(float)).round(0)
    tab["aviation index (2005-09 = 100)"] = _growth.index_to_base(b.astype(float)).round(0)
    tab.attrs.update(p90=p90, snapshot=snapshot)
    tab.index.name = "priority year"
    return tab


def growth_series(ds, v: pd.DataFrame, cfg) -> Dict[str, pd.Series]:
    """Count per priority year of every series of the growth comparison (Figure 1 ii): the eVTOL
    architecture patents (representative patents, one PatSeer family each), the unique aircraft and
    the three worldwide baselines.

    Ported from: sm_open.py:growth_series"""
    pid = set(ds.approved_variants["patent_id"].astype(str))
    rep = ds.identity[ds.identity["patent_id"].astype(str).isin(pid)]
    fam = pd.to_numeric(rep["priority_year"], errors="coerce").dropna().astype(int).value_counts().sort_index()
    ac = v.dropna(subset=["year"])["year"].astype(int).value_counts().sort_index()
    return {"evtol_families": fam, "evtol_aircraft": ac,
            "b64": read_baseline(cfg, "baseline_patseer_b64").dropna().astype(int),
            "secb": read_baseline(cfg, "baseline_patseer_sectionb").dropna().astype(int),
            "all": read_baseline(cfg, "baseline_world").dropna().astype(int)}


#: (key, printed name) of the series of Figure 1 (ii), in drawing order. Ported from: sm_open.py:GROWTH_SERIES
GROWTH_SERIES = [("evtol_families", "eVTOL architecture patents"), ("evtol_aircraft", "eVTOL unique aircraft"),
                 ("b64", "aeronautics (CPC B64)"), ("secb", "transport and operations (CPC section B)"),
                 ("all", "all patents")]


def sector_events(cfg, snapshot: Optional[str] = None) -> pd.DataFrame:
    """The dated sector events of the strip under Figure 1 (i), in date order with a calendar ``year``;
    events dated after the snapshot are dropped.

    Ported from: la_figures.py:sector_events"""
    e = pd.read_csv(cfg.path("sector_events"), dtype=str, keep_default_na=False)
    e["date"] = pd.to_datetime(e["date"].str.strip(), errors="coerce")
    e = e[e["date"].notna()]
    if snapshot:
        e = e[e["date"] <= pd.Timestamp(snapshot)]
    e = e.sort_values("date", kind="stable").reset_index(drop=True)
    e["year"] = e["date"].dt.year.astype(int)
    return e


# ------------------------------------------------------------------------------------ evtol.news class mix
def evtolnews_years(cfg, windows) -> pd.DataFrame:
    """The evtol.news directory aircraft with their final development year and the window it falls in.

    The final year is the two readers' common year (``dev_year``); aircraft the readers dated
    differently or not at all carry no year. The author's rulings on those disagreements are not stored
    in the yaml's inputs, so none is applied (the archive applied them only if its file existed).

    Ported from: sm_open.py:evtolnews_years"""
    d = pd.read_csv(cfg.path("evtolnews_dev_years"))
    d["year"] = pd.to_numeric(d["dev_year"], errors="coerce")
    from viz import script_inputs
    if script_inputs.enabled(cfg) and script_inputs.year(cfg) is not None:
        # rule-based year (the author's reading where he read the page); the year overrides below are then already in it
        d["year"] = pd.to_numeric(d["slug_key"].map(script_inputs.year(cfg)), errors="coerce")
        d["window"] = d["year"].map(lambda y: window_of(y, windows))
        return d
    # years the author corrected on the review page (review/year_overrides.csv); the source csv itself is never edited
    ov_path = _Path(__file__).resolve().parents[1] / "review" / "year_overrides.csv"
    if ov_path.exists():
        ov = pd.read_csv(ov_path, keep_default_na=False).set_index("slug_key")["dev_year"]
        hit = d["slug_key"].isin(ov.index)
        d.loc[hit, "year"] = pd.to_numeric(d.loc[hit, "slug_key"].map(ov), errors="coerce")
    d["window"] = d["year"].map(lambda y: window_of(y, windows))
    return d


def evtolnews_long(v: pd.DataFrame, cfg, windows, in_domain_only: bool = False) -> pd.DataFrame:
    """Both sources stacked, one row per dated, classed aircraft: ``source`` (patent / directory),
    ``window``, ``class5``. The patent side is every unique aircraft with a class and a priority window.
    ``in_domain_only``: the directory side keeps only the pages of ``directory_frame()['in_domain']``.

    Ported from: sm_open.py:_evn_long"""
    p = v.dropna(subset=["window", "class5"])[["window", "class5"]].assign(source="patent")
    d = evtolnews_years(cfg, windows)
    if in_domain_only:                      # 2026-10-15: only the pages the corrected domain rules keep (electric, crewed)
        d = d[d["slug_key"].isin(set(directory_frame(cfg).query("in_domain")["slug_key"]))]
    d = d.dropna(subset=["window"])
    d = d[["window", "evtol_class"]].rename(columns={"evtol_class": "class5"}).assign(source="directory")
    return pd.concat([p, d], ignore_index=True)


# ------------------------------------------------------------------------------------ AAM Reality Index
def _oem_key(s) -> str:
    s = re.sub(r"\(.*?\)", "", str(s)).strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _first_year(text) -> Optional[int]:
    """Earliest four-digit year printed in an index cell ('2021 / 2026 / 2023' -> 2021), or None."""
    yrs = [int(m.group(0)) for m in re.finditer(r"(19|20)\d{2}", str(text))]
    return min(yrs) if yrs else None


def ari_load(cfg) -> tuple:
    """(current release, history, company map) of the AAM Reality Index, as stored.

    Ported from: la_tables.py:_load_ari"""
    from viz import script_inputs
    cmap = script_inputs.company_map(cfg) if script_inputs.enabled(cfg) else None
    return (pd.read_csv(cfg.path("ari_scores"), keep_default_na=False),
            pd.read_csv(cfg.path("ari_history")),
            cmap if cmap is not None else pd.read_csv(cfg.path("ari_firm_map"), keep_default_na=False))


def ari_firms(v: pd.DataFrame, cfg) -> pd.DataFrame:
    """Every index OEM that files in the corpus, with its unique aircraft (``company`` = canonical firm name).

    Ported from: la_tables.py:ari_firms (the columns the Question 1 tables use)."""
    cur, hist, cmap = ari_load(cfg)
    cmap = cmap[cmap["company_canonical"].ne("")]
    sizes = firm_sizes(v)
    rows = [{"company": c, "unique aircraft": int(sizes.get(c, 0))} for c in sorted(set(cmap["company_canonical"]))]
    out = pd.DataFrame(rows)
    return out[out["unique aircraft"] > 0].reset_index(drop=True)


def ari_timeline(v: pd.DataFrame, cfg) -> pd.DataFrame:
    """The index firms of the May 2026 release that file in the corpus: first / peak / last priority year,
    first flight and entry into service as the index states them, and the two gaps in years.

    The gaps count from the firm's earliest priority year IN THIS CORPUS, so they are floors; a firm that
    flew before it appears here prints a negative gap. Where the index lists several vehicles the earliest
    year printed in the cell is taken.

    Ported from: la_tables.py:ari_timeline"""
    cur, hist, cmap = ari_load(cfg)
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows() if r["company_canonical"]}
    cur["company"] = cur["oem"].map(_oem_key).map(key_to_canon)
    rows = []
    for _, r in cur.dropna(subset=["company"]).iterrows():
        sub = v[v["company_canonical"].eq(r["company"])].dropna(subset=["year"])
        if not len(sub):
            continue
        yrs = sub["year"].astype(int)
        ff, eis = _first_year(r["first_flight"]), _first_year(r["eis"])
        rows.append({"company": r["company"], "ARI score": float(r["ari"]), "first patent": int(yrs.min()),
                     "peak filing year": int(yrs.value_counts().sort_index().idxmax()), "last patent": int(yrs.max()),
                     "unique aircraft": int(len(sub)), "first flight (ARI)": ff, "entry into service (ARI)": eis,
                     "years to first flight": (ff - int(yrs.min())) if ff else None,
                     "years to entry into service": (eis - int(yrs.min())) if eis else None,
                     "regulator (ARI)": r["cert_regulator"], "country (ARI)": r["country"],
                     "region": sub["region3"].mode().iloc[0], "ARI vehicle type": r["vehicle_type"]})
    return pd.DataFrame(rows).sort_values("first patent").reset_index(drop=True)


# ------------------------------------------------------------------------------------ legal status
def aircraft_patents(ds, v: pd.DataFrame, first_only: bool = False) -> pd.DataFrame:
    """Every patent linked to each unique aircraft of ``v``, one row per (aircraft, patent), with its
    PatSeer legal status. The links are the aircraft's own primary patent plus every patent of the master
    that points at it through ``same_aircraft_as`` (D1/D2 duplicates; a D3 is a new aircraft and is not linked).
    ``first_only=True`` links a duplicate that names several aircraft to its first target only (sensitivity).

    Ported from: sm_open.py:aircraft_patents"""
    prim = v[["aircraft_id", "patent_id"]].assign(link="primary")
    m = ds.master
    d = m.loc[m["same_aircraft_as"].notna(), ["patent_id", "same_aircraft_as"]].copy()
    d["aircraft_id"] = d["same_aircraft_as"].astype(str).str.split(";")
    if first_only:
        d["aircraft_id"] = d["aircraft_id"].str[:1]
    d = d.explode("aircraft_id")
    d["aircraft_id"] = d["aircraft_id"].str.strip()
    d = d[d["aircraft_id"].isin(set(prim["aircraft_id"]))][["aircraft_id", "patent_id"]]
    out = pd.concat([prim, d.assign(link="duplicate")]).drop_duplicates(["aircraft_id", "patent_id"])
    status = ds.identity.drop_duplicates("patent_id").set_index("patent_id")["legal_status_raw"]
    s = out["patent_id"].map(status)
    out["legal_status_raw"] = s
    out["status_known"] = s.notna() & s.fillna("").astype(str).str.strip().ne("")
    out["inactive"] = s.fillna("").astype(str).str.startswith("INACTIVE")
    return out.reset_index(drop=True)


def force_frame(ds, v: pd.DataFrame, max_year: int = FORCE_MAX_YEAR, first_only: bool = False) -> pd.DataFrame:
    """One row per unique aircraft with a class and priority year <= ``max_year``: ``out`` = no linked patent
    is in force (every one reads INACTIVE), ``lapsed`` = the primary patent alone (the earlier reading),
    ``linked`` = patents linked. An aircraft none of whose patents has a status is dropped.

    Ported from: sm_open.py:_force_frame"""
    links = aircraft_patents(ds, v, first_only=first_only)
    links["_live"] = links["status_known"] & ~links["inactive"]
    per = links.groupby("aircraft_id").agg(linked=("patent_id", "size"), known=("status_known", "sum"),
                                           live=("_live", "any"))
    keep = v["topType"].notna() if max_year is None else (v["year"].le(max_year) & v["topType"].notna())
    w = v[keep][["aircraft_id", "topType", "lapsed", "year"]]
    w = w.join(per, on="aircraft_id")
    unread = int(w["known"].fillna(0).eq(0).sum())
    w = w[w["known"].fillna(0).gt(0)].copy()
    w["out"] = ~w["live"].astype(bool)
    w["lapsed"] = w["lapsed"].astype(bool)
    w.attrs.update(unread=unread, links=links)
    return w


# ------------------------------------------------------------------------------------ TRL and public aircraft
def trl_frame(ds) -> pd.DataFrame:
    """One row per unique aircraft with its NASA TRL, band and programme status; an aircraft the TRL
    table does not list is TRL 2 ('patent only').

    Ported from: a2.py:trl_frame"""
    t = ds.trl[["aircraft_id", "trl", "trl_basis", "confidence", "programme_status"]]
    v = ds.variants[["aircraft_id", "topType"]].merge(t, on="aircraft_id", how="left")
    v["trl"] = pd.to_numeric(v["trl"], errors="coerce").fillna(2).astype(int)
    v["programme_status"] = v["programme_status"].fillna("not tracked")
    v["band"] = v["trl"].map({lvl: name for name, lvls in TRL_BANDS for lvl in lvls})
    return v


def public_arch_frame(ds) -> pd.DataFrame:
    """The unique aircraft that have a public counterpart, with how the patent's drawing label compares
    with it: ``match`` = yes / taxonomy (drawing agrees with the public aircraft), no (drawing and patent
    text agree with each other, not with the public aircraft) or image (the drawing departs from the text,
    which matches the public aircraft).

    Ported from: a2.py:public_arch_frame"""
    t = ds.trl[["aircraft_id", "aircraft_name", "trl", "arch_match", "public_arch"]].copy()
    t = t[t["arch_match"].fillna("").ne("")]
    cols = ["aircraft_id", "patent_id", "topType"] + (["arch_gt"] if "arch_gt" in ds.variants else [])
    v = ds.variants[cols].merge(t, on="aircraft_id", how="inner")
    v["match"] = v["arch_match"].astype(str).str.split(" ").str[0]
    if "arch_gt" in v:
        diff = v["match"].isin(["no", "image"])
        gt = v["arch_gt"].fillna("").astype(str)
        v.loc[diff & gt.ne("") & gt.eq(v["topType"].astype(str)), "match"] = "no"
        v.loc[diff & gt.ne("") & gt.ne(v["topType"].astype(str)), "match"] = "image"
    return v


def linked_aircraft_ids(v: pd.DataFrame, cfg) -> set:
    """Aircraft ids linked to an evtol.news page (patent_links.csv, use = yes, page present in the directory).

    Ported from: la_tables.py:linked_aircraft (the ids only)."""
    links = pd.read_csv(cfg.path("evtolnews_patent_links"), keep_default_na=False)
    links = links[links["use"].eq("yes")]
    pages = set(pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False)["slug_key"])
    keep = links["slug_keys"].astype(str).str.split("|").str[0].isin(pages)
    return set(links.loc[keep, "aircraft_uid"]) & set(v["aircraft_id"])


def representativeness(w: pd.DataFrame, mask: pd.Series, label: str, window_order=()) -> pd.DataFrame:
    """Does the subset ``mask`` stand for the rest of the analysis set? One row per level of each categorical
    attribute (Pearson chi-square of subset vs rest on the attribute, lib.association) and one per
    continuous attribute (Mann-Whitney); ``label`` names the subset's columns, ``window_order`` the window
    names in time order (the levels of the window attribute follow it). The test row of each
    attribute carries the group sizes and the level the groups differ most on.

    Ported from: la_tables.py:_representativeness"""
    from lib import association
    rows = []
    a_all, b_all = w[mask], w[~mask]
    for name, col in REP_CATEGORICAL:
        a, b = a_all[col], b_all[col]
        levels = list(pd.concat([a, b]).dropna().value_counts().index)
        if col == "window":
            levels = [x for x in window_order if x in levels]
        ca, cb = a.value_counts().reindex(levels).fillna(0), b.value_counts().reindex(levels).fillna(0)
        obs = np.vstack([ca.to_numpy(), cb.to_numpy()])
        obs = obs[:, obs.sum(axis=0) > 0]
        try:
            p = association.chi2_test(obs)["p"]
        except Exception:
            p = float("nan")
        for k, lev in enumerate(levels):
            pa, pb = float(ca[lev]) / max(len(a), 1) * 100, float(cb[lev]) / max(len(b), 1) * 100
            rows.append({"attribute": name, "level": str(lev), label: int(ca[lev]), f"{label} %": round(pa, 1),
                         "rest": int(cb[lev]), "rest %": round(pb, 1), "gap pp": round(pa - pb, 1),
                         "test": "chi-square" if k == 0 else "", "p": round(p, 4) if k == 0 else np.nan,
                         "verdict": (("matches the rest" if p >= 0.05 else "does NOT match the rest") if k == 0 else "")})
    for name, col in REP_CONTINUOUS:
        a = pd.to_numeric(a_all[col], errors="coerce").dropna()
        b = pd.to_numeric(b_all[col], errors="coerce").dropna()
        try:
            p = association.mann_whitney_p(a, b)
        except Exception:
            p = float("nan")
        rows.append({"attribute": name, "level": "median", label: len(a), f"{label} %": round(float(a.median()), 1),
                     "rest": len(b), "rest %": round(float(b.median()), 1),
                     "gap pp": round(float(a.median() - b.median()), 1), "test": "Mann-Whitney",
                     "p": round(p, 6), "verdict": "matches the rest" if p >= 0.05 else "does NOT match the rest"})
    out = pd.DataFrame(rows)
    n_in, n_rest = int(mask.sum()), int((~mask).sum())
    out[f"n {label}"] = np.where(out["test"].ne(""), n_in, np.nan)
    out["n rest"] = np.where(out["test"].ne(""), n_rest, np.nan)
    gap_of = {}
    for attr in out["attribute"].unique():
        sub = out[out["attribute"].eq(attr)]
        k = sub["gap pp"].abs().idxmax()
        gap_of[attr] = (f"{sub.loc[k, 'level']} ({sub.loc[k, 'gap pp']:+.1f} pp)"
                        if sub.loc[k, "level"] != "median" else f"median {sub.loc[k, 'gap pp']:+.1f}")
    out["largest gap"] = [gap_of[a] if t else "" for a, t in zip(out["attribute"], out["test"].ne(""))]
    out.attrs.update({"in": n_in, "rest": n_rest})
    return out


# ------------------------------------------------------------------------------------ design traces
_TRACE_CARDS = ["fuselage", "wing1", "wing2", "wing3", "emp", "boom", "core_layout", "hull_array"]


def trace_frame(ds, v: pd.DataFrame) -> pd.DataFrame:
    """One row per unique aircraft with every labelled design trace of ``lib.drivers.TRACES`` (tilting joint
    groups, propulsive units, ducting, ...), the frame lib.drivers.trace_drift / trace_trends read.

    Rule 1 (2026-09-19): a value an override hides is NaN, never 0 or False. A thrust type is a propulsor type
    with units that is not control-only; the M3 cards are read type by type as :func:`propulsion_states` does.
    Columns: aircraft_id, topType, window, year, units, then one column per trace key.

    Ported from: la_tables.py:trace_frame"""
    raw = ds.variants
    ovs = override_sets(raw)
    rows = []
    for (_, r), ov in zip(raw.iterrows(), ovs):
        g = lambda c: r[c] if c in r.index else None
        hidden = any(t.startswith("M3:") for t in ov)
        types = []
        for card in _TRACE_CARDS:
            if f"M3:{card}" in ov:
                continue
            nt = _n(g(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                if _n(g(pre + "count")) <= 0 or _s(g(pre + "ctrlOnly")) == "True":
                    continue
                types.append(dict(card=card, propKin=_s(g(pre + "propKin")), rmech=_s(g(pre + "rmech")),
                                  chord=_s(g(pre + "chord")),
                                  zc=_s(g(pre + "zoneChord")) or _s(g(f"{card}_zoneChord"))))
        rec = bool(types) and not hidden
        tw = sum(1 for k in range(1, 5) if _s(g(f"wing{k}_tilt")) == "Tilt")
        tb = sum(1 for k in range(1, 7) if _s(g(f"boom{k}_tilts")) == "True" and _s(g(f"boom{k}_hasProps")) != "False")
        stow = any(_s(g(f"boom{k}_retracts")) == "True" for k in range(1, 7))
        joints = tw + tb + sum(1 for t in types if t["propKin"] == "Tilt") + (1 if _s(g("empTilts")) == "True" else 0)
        on_wing = any(t["card"].startswith("wing") for t in types)
        fk, gear, plan = _s(g("fusKin")), _s(g("gearArch")), _s(g("wing1_plan"))
        wc = pd.to_numeric(g("wCount"), errors="coerce")
        rows.append(dict(
            aircraft_id=r["aircraft_id"],
            joints=(joints if rec and not ({"M1", "M2"} & set(ov)) else np.nan),
            fus_moves=((fk != "Fixed") if fk else np.nan),
            retract=(any(t["rmech"] in ("Retracting", "BladeFold") for t in types) if rec else np.nan),
            booms_stow=(stow if _s(g("boomsPresent")) == "True" and "M1" not in ov else np.nan),
            on_booms=(any(t["card"] == "boom" for t in types) if rec else np.nan),
            stations=(len({t["card"] for t in types}) if rec else np.nan),
            wing_LE=(any(t["zc"] == "LE" for t in types if t["card"].startswith("wing")) if rec and on_wing else np.nan),
            pusher=(any(t["chord"] == "Back" for t in types) if rec else np.nan),
            two_wings=((wc >= 2) if pd.notna(wc) else np.nan),
            swept=((plan in ("Swp", "Del")) if plan else np.nan),
            gear_drawn=((gear != "Unknown") if gear else np.nan),
            wheeled=((gear == "Wheeled Gear") if gear and gear != "Unknown" else np.nan),
            n_types=(len(types) if rec else np.nan),
        ))
    t = pd.DataFrame(rows)
    keep = v[["aircraft_id", "topType", "window", "year", "units", "any_ducted", "nBooms", "empType"]]
    t = keep.merge(t, on="aircraft_id", how="left")
    t["ducted"] = t["any_ducted"].map({True: True, False: False}).astype(object).where(t["any_ducted"].notna())
    t["tailless"] = t["empType"].astype(str).eq("Tailless").where(t["empType"].notna())
    nb = pd.to_numeric(t["nBooms"], errors="coerce")
    t["booms"] = (nb > 0).where(nb.notna())
    t["units"] = pd.to_numeric(t["units"], errors="coerce")
    return t


def visible_at_snapshot(ds, v: pd.DataFrame, year: int = 2023, ref_years=(2016, 2021)) -> pd.Series:
    """Per region, the part of the aircraft of priority ``year`` that the snapshot already sees (lib.growth.visible_share).

    The publication lag (publication year minus priority year) is read per region on its aircraft of
    ``ref_years`` (2016-21, whose publications are complete) and applied to ``year``.

    Ported from: sm_open.py:region_years (column 'visible at the snapshot')"""
    snap = pd.to_datetime(ds.identity["snapshot_date"].dropna().iloc[0])
    S, frac = int(snap.year), float(snap.dayofyear / 365.0)
    j = v.merge(ds.identity[["patent_id", "pub_year"]], on="patent_id", how="left", suffixes=("", "_pub"))
    pub = pd.to_numeric(j["pub_year_pub"] if "pub_year_pub" in j else j["pub_year"], errors="coerce")
    j = j.assign(lag=pub - j["year"])
    j = j[j["region3"].isin(REGIONS)]
    ref = j[j["year"].between(*ref_years)]
    return pd.Series({r: round(_growth.visible_share(ref.loc[ref["region3"].eq(r), "lag"].dropna(), S - year, frac), 3)
                      for r in REGIONS}, name=f"visible at the snapshot, {year}")


# =====================================================================================================
# Question 2 (the design space): wrangling behind notebook 41
# Only joins, filters and counts; the statistics (effective numbers, shares, rarefaction, Chao1) come from lib/.
# =====================================================================================================
from lib import concentration as _conc                  # noqa: E402
from lib import diversity as _div                        # noqa: E402
from .data import hidden_by_override as _hidden          # noqa: E402

#: the label fields Table 6 prints in full, in the document's order.
#: Ported from: a2.py:D3_FIELDS
D3_FIELDS = ["wCount", "empType", "fusKin", "wingConf", "gearArch", "latSym"]

#: printed name of each Table 6 field. Ported from: a2.py:FIELD_NAMES (the six used here)
D3_FIELD_NAMES = {"empType": "tail type", "wCount": "number of wings (winged designs)", "gearArch": "landing-gear type",
                  "fusKin": "fuselage motion hover to cruise", "wingConf": "wing configuration",
                  "latSym": "left-right symmetry"}

#: options Table 6 leaves out (author's ruling, rerun of 2026-10-15): 0 wings (the table reads the winged designs) and 0 places
#: carrying propulsors (the one design recorded with 0 propulsors, already left out by propulsor_units)
D3_DROP_OPTIONS = {"wCount": ["0"], "places carrying propulsor units per aircraft": ["0"]}

#: the two derived rows of Table 6, as the thesis prints them (display rename 2026-09-28 / 2026-09-29: "propulsor
#: units", "places"); the document's CSV calls them "propulsor units per aircraft" and "propulsor groups per aircraft".
D3_UNITS_ROW = "propulsor units per aircraft (band)"
D3_PLACES_ROW = "places carrying propulsor units per aircraft"

#: units band of the ducting tables: "no propulsor card" for HB / PFV, "0 recorded" for the one aircraft with 0 units.
#: Ported from: la_tables.py:NO_UNIT_CARD, UNIT_ZERO
NO_UNIT_CARD = "no propulsor card"
UNIT_ZERO = "0 recorded"

_TYPE_COUNT_RE = re.compile(r"^(boom|wing[123]|emp|fuselage|hull_array)_t(\d)_count$")
_GROUPS = ("boom", "wing1", "wing2", "wing3", "emp", "fuselage", "hull_array")


def option_names(data_dictionary: pd.DataFrame, column: str) -> Dict[str, str]:
    """``{option id: display name}`` for one coded column, from data_dictionary.csv.

    Ported from: metrics.py:option_names"""
    row = data_dictionary.loc[data_dictionary["column"] == column, "options"]
    if row.empty or not isinstance(row.iloc[0], str):
        return {}
    out = {}
    for part in row.iloc[0].split("|"):
        if "=" in part:
            key, name = part.split("=", 1)
            out[key.strip()] = name.strip()
    return out


def propulsor_groups(v: pd.DataFrame) -> pd.Series:
    """How many places (booms, wing panels, tail, fuselage, hull array, core layout) carry propulsor units: the number of
    propulsor-unit columns above zero.

    Ported from: a2.py:propulsor_groups"""
    cols = [c for c in PROPULSOR_UNIT_COLUMNS if c in v.columns]
    return (v[cols].apply(pd.to_numeric, errors="coerce") > 0).sum(axis=1)


def selected_fields(ds, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Table 6: per label field the aircraft that answer it, the number of different answers, the top share and the most
    common answers with their aircraft ("answer n · answer n"), then two derived propulsion rows: the propulsor units per
    aircraft in five bands and the places carrying propulsor units (4 or more pooled). HB / PFV and a G1 override have no
    propulsor record and are not counted (rule 1).

    top_share = (aircraft giving the most common answer) / (aircraft answering), from :func:`lib.concentration.top_k_share`.

    Ported from: a2.py:d3_selected_fields (the two derived rows carry the thesis names of D3_UNITS_ROW / D3_PLACES_ROW)"""
    rows = []
    for f in fields or D3_FIELDS:
        s = ds.variants[f]
        if f in D3_DROP_OPTIONS:                    # an option left out of the table (rerun of 2026-10-15)
            s = s.where(~s.astype(str).str.replace(r"\.0$", "", regex=True).isin(D3_DROP_OPTIONS[f]))
        names = option_names(ds.data_dictionary, f)
        top = s.dropna().value_counts().head(4)
        rows.append({"name": D3_FIELD_NAMES.get(f, f), "field": f, "answered": int(s.notna().sum()),
                     "answers": int(s.nunique(dropna=True)), "top_share": round(_conc.top_k_share(s, 1), 2),
                     "most common answers": " · ".join(f"{names.get(str(k), k)} {n}" for k, n in top.items())})
    if fields is None:
        units = propulsor_units(ds.variants)["units"]
        for name, field, s in [
            (D3_UNITS_ROW, "(derived) propulsor units, binned", rotor_bin(units)),
            (D3_PLACES_ROW, "(derived) M3 stations carrying units",
             propulsor_groups(ds.variants).map(lambda g: "4 or more" if g >= 4 else str(int(g))).where(units.notna())
             .where(lambda x: ~x.isin(D3_DROP_OPTIONS[D3_PLACES_ROW]))),
        ]:
            s = s.where(s.ne("nan")).dropna()
            top = s.value_counts().head(5)
            rows.append({"name": name, "field": field, "answered": int(len(s)), "answers": int(s.nunique()),
                         "top_share": round(_conc.top_k_share(s, 1), 2),
                         "most common answers": " · ".join(f"{k} {n}" for k, n in top.items())})
    return pd.DataFrame(rows)


def selected_field_series(ds) -> Dict[str, pd.Series]:
    """The series behind every row of :func:`selected_fields` (same options dropped, same blanks), keyed by the row's printed
    name, indexed like ``ds.variants`` and carrying the printed option names (data_dictionary names for a coded field, the
    band / place strings for the two derived rows). NaN = the aircraft does not answer the row.

    Used in: q6_fixed_by_architecture (dimension x architecture)"""
    out = {}
    for f in D3_FIELDS:
        s = ds.variants[f]
        if f in D3_DROP_OPTIONS:
            s = s.where(~s.astype(str).str.replace(r"\.0$", "", regex=True).isin(D3_DROP_OPTIONS[f]))
        names = option_names(ds.data_dictionary, f)
        ids = [str(k).replace(".0", "") if pd.notna(k) else None for k in s]        # option ids as strings ("2", not "2.0"; True/False as is)
        out[D3_FIELD_NAMES.get(f, f)] = pd.Series([names.get(k, k) if k is not None else np.nan for k in ids], index=s.index, dtype=object)
    units = propulsor_units(ds.variants)["units"]
    places = (propulsor_groups(ds.variants).map(lambda g: "4 or more" if g >= 4 else str(int(g))).where(units.notna())
              .where(lambda x: ~x.isin(D3_DROP_OPTIONS[D3_PLACES_ROW])))
    for name, s in [(D3_UNITS_ROW, rotor_bin(units)), (D3_PLACES_ROW, places)]:
        out[name] = s.where(s.ne("nan")).astype(object).where(s.notna())
    return out


def unit_band(v: pd.DataFrame) -> pd.Series:
    """Propulsor units per aircraft -> 1-3 / 4 / 5-6 / 7-8 / 9+ (a recorded 0 is no answer since 2026-10-15; kept as "0 recorded" if one reappears) and
    HB / PFV as "no propulsor card".

    Ported from: la_tables.py:unit_band"""
    u = pd.to_numeric(v["units"], errors="coerce")
    band = pd.cut(u, bins=UNIT_BANDS[0], labels=UNIT_BANDS[1]).astype(object).where(u.notna())
    band = band.mask(u.eq(0), UNIT_ZERO)
    return band.mask(v["rotorBin"].astype(str).eq(NO_M3_CARD), NO_UNIT_CARD)


def _type_slots(v: pd.DataFrame) -> List[str]:
    return [c[:-len("_count")] for c in v.columns if _TYPE_COUNT_RE.match(c)]


def per_aircraft_units(v: pd.DataFrame) -> pd.DataFrame:
    """Per aircraft: units in a duct, units that tilt, units that retract or fold, tilting / fixed / all propulsor types,
    and the sum of the slot counts. A place with ONE propulsor type keeps its answers on the place's columns; a place with
    two or more types keeps them on the ``_t<k>_`` slots, so each place is read from its slots when any slot carries a
    count and from the place's columns otherwise.

    Ported from: la_tables.py:_per_aircraft_units"""
    out = pd.DataFrame(0.0, index=v.index, columns=["slot units", "ducted units", "tilting units", "retracting units",
                                                    "tilting types", "fixed types", "types"])
    for g in _GROUPS:
        slots = [s for s in _type_slots(v) if s.startswith(f"{g}_t")]
        slot_cnt = {s: pd.to_numeric(v[f"{s}_count"], errors="coerce") for s in slots}
        has_slots = sum(c.notna() for c in slot_cnt.values()) > 0 if slots else pd.Series(False, index=v.index)
        readings = [(slot_cnt[s].fillna(0).where(has_slots, 0), v[f"{s}_bmech"], v[f"{s}_propKin"], v[f"{s}_rmech"])
                    for s in slots]
        if f"{g}_count" in v.columns:
            gc = pd.to_numeric(v[f"{g}_count"], errors="coerce").fillna(0).where(~has_slots, 0)
            readings.append((gc, v.get(f"{g}_bmech"), v.get(f"{g}_propKin"), v.get(f"{g}_rmech")))
        for cnt, bmech, kin, rmech in readings:
            b = bmech.astype(str) if bmech is not None else pd.Series("", index=v.index)
            k = kin.astype(str) if kin is not None else pd.Series("", index=v.index)
            r = rmech.astype(str) if rmech is not None else pd.Series("", index=v.index)
            out["slot units"] += cnt
            out["ducted units"] += cnt.where(b.eq("Ducted"), 0)
            out["tilting units"] += cnt.where(k.eq("Tilt"), 0)
            out["retracting units"] += cnt.where(r.isin(["Retracting", "BladeFold"]), 0)
            out["tilting types"] += ((cnt > 0) & k.eq("Tilt")).astype(int)
            out["fixed types"] += ((cnt > 0) & k.eq("Fixed")).astype(int)
            out["types"] += (cnt > 0).astype(int)
    return out


def _duct_base(v: pd.DataFrame) -> pd.DataFrame:
    """The aircraft whose duct answer can be read and that carry at least one propulsor unit, with their band and the
    ducted units of :func:`per_aircraft_units`."""
    w = v.copy()
    w["band"] = unit_band(w)
    w = w.join(per_aircraft_units(w))
    w["_u"] = pd.to_numeric(w["units"], errors="coerce")
    return w[w["band"].isin(UNIT_BANDS[1]) & w["any_ducted"].notna() & w["_u"].gt(0)]


def duct_count_by_units(v: pd.DataFrame) -> pd.DataFrame:
    """How MUCH of an aircraft is ducted, per propulsor-unit band and over all bands: aircraft, with any ducted unit and its
    share, the share of the band's UNITS that sit in a duct (pooled), the share of aircraft that duct EVERY unit, and the
    median ducted units among the aircraft that duct at all.

    Ported from: la_tables.py:duct_count_by_units"""
    w = _duct_base(v)
    rows = []
    for g in UNIT_BANDS[1] + ["all bands"]:
        sub = w if g == "all bands" else w[w["band"].eq(g)]
        if not len(sub):
            continue
        ducted = sub[sub["ducted units"] > 0]
        rows.append({"propulsive units": g, "aircraft": int(len(sub)), "with any ducted unit": int(len(ducted)),
                     "share with any": round(float(len(ducted) / len(sub)), 3),
                     "share of units ducted": round(float(sub["ducted units"].sum() / sub["_u"].sum()), 3),
                     "share ducting every unit": round(float((sub["ducted units"] >= sub["_u"]).mean()), 3),
                     "median ducted units (ducted aircraft)": (float(ducted["ducted units"].median())
                                                              if len(ducted) else np.nan)})
    return pd.DataFrame(rows)


#: the shares of an aircraft's units in a duct, binned for the distribution columns (the top bin is "every unit", exact).
#: Ported from: la_tables.py:DUCT_SHARE_BINS
DUCT_SHARE_BINS = [("under a quarter", 0.0, 0.25), ("a quarter to half", 0.25, 0.50),
                   ("half to three quarters", 0.50, 0.75), ("three quarters, not all", 0.75, 1.0)]
DUCT_EVERY = "every unit"


def duct_conditional(v: pd.DataFrame) -> pd.DataFrame:
    """Given that ONE unit is ducted, are they all? Per band and over all bands, among the aircraft that duct at least one
    unit: the share that duct every unit, the median and mean ducted share (ducted units / units, clipped at 1), the
    aircraft in each share bin, and the aircraft whose slot counts exceed the stored unit count ("unit counts that disagree").

    Ported from: la_tables.py:duct_conditional (the verdict sentence it attached is wording, not ported)"""
    w = _duct_base(v)
    w["_raw"] = w["ducted units"] / w["_u"]
    w["_share"] = w["_raw"].clip(upper=1.0)
    rows = []
    for g in UNIT_BANDS[1] + ["all bands"]:
        sub = w if g == "all bands" else w[w["band"].eq(g)]
        d = sub[sub["ducted units"] > 0]
        if not len(d):
            continue
        row = {"propulsive units": g, "aircraft in the band": int(len(sub)), "of them, duct at least one unit": int(len(d)),
               "share that duct every unit": round(float((d["_share"] >= 1.0).mean()), 3),
               "median ducted share": round(float(d["_share"].median()), 3),
               "mean ducted share": round(float(d["_share"].mean()), 3)}
        for name, lo, hi in DUCT_SHARE_BINS:
            row[name] = int((d["_share"].ge(lo) & d["_share"].lt(hi)).sum())
        row[DUCT_EVERY] = int((d["_share"] >= 1.0).sum())
        row["unit counts that disagree"] = int((d["_raw"] > 1.0).sum())
        rows.append(row)
    return pd.DataFrame(rows)


#: the four arrangement features of Figure 6 (ii), in the order the figure prints them
ARRANGEMENT_FEATURES = ["at least one tilting propulsor", "both fixed and tilting propulsors", "a ducted propulsor",
                        "more than 8 propulsors"]


def arrangement_features(v: pd.DataFrame, classes: List[str]) -> tuple:
    """Figure 6 (ii): per class the share of its aircraft with each arrangement feature, among the aircraft where the
    feature can be read; also the aircraft read and the aircraft of the class.

    Returns (share table: features x classes, read: Series of aircraft read per class, total: Series per class).

    Ported from: sm_figures.py:panel_propulsion_compact (the ``feat`` block)"""
    units = pd.to_numeric(v["units"], errors="coerce")
    feat = pd.DataFrame({"topType": v["topType"].to_numpy(),
                         ARRANGEMENT_FEATURES[0]: v["any_tilting"].to_numpy(),
                         ARRANGEMENT_FEATURES[1]: (v["any_tilting"] & v["any_fixed"]).where(v["any_tilting"].notna() & v["any_fixed"].notna(), pd.NA).to_numpy(),
                         ARRANGEMENT_FEATURES[2]: v["any_ducted"].to_numpy(),
                         ARRANGEMENT_FEATURES[3]: (units > 8).astype("boolean").where(units.notna(), pd.NA).to_numpy()})
    g = feat.groupby("topType")
    tab = g.agg(lambda s_: float(s_.dropna().astype(float).mean()) if s_.notna().any() else np.nan).reindex(classes).astype(float)
    read = g[ARRANGEMENT_FEATURES[0]].agg(lambda s_: int(s_.notna().sum())).reindex(classes).fillna(0).astype(int)
    total = feat.groupby("topType").size().reindex(classes).fillna(0).astype(int)
    return tab.T, read, total


# ------------------------------------------------------------------ archetype sets (2.2)
#: the archetype sets the codebook can form: set id -> (fields in key order, what it adds). Letters of the thesis:
#: C class, W wings, T any tilting propulsor, U propulsor-unit band, B booms present, B# booms binned, E tail.
#: Ported from: a2.py:ARCHETYPE_LEVELS
ARCHETYPE_SETS = {
    "A0": ["topType"],
    "A0c": ["topType", "rotorBin"],
    "A1": ["topType", "wCount", "boomsPresent"],
    "A1c": ["topType", "wCount", "boomsPresent", "rotorBin"],
    "A1b": ["topType", "wCount", "boomBin"],
    "A1t": ["topType", "wCount", "anyTilt"],
    "A1tc": ["topType", "wCount", "anyTilt", "rotorBin"],
    "A2": ["topType", "wCount", "boomsPresent", "empType"],
    "A2c": ["topType", "wCount", "boomsPresent", "empType", "rotorBin"],
}
#: set id -> (thesis code, printed name). Ported from: sm_text_methods.py:LEVEL_CODES (+ F for the family)
SET_CODES = {"A0": ("C", "class"), "A0c": ("C·U", "class + propulsor units"), "A1": ("C·W·B", "class + wings + booms"),
             "A1c": ("C·W·B·U", "class + wings + booms + propulsor units"), "A1b": ("C·W·B#", "class + wings + number of booms"),
             "A1t": ("C·W·T", "class + wings + tilt"), "A1tc": ("C·W·T·U", "class + wings + tilt + propulsor units"),
             "A2": ("C·W·B·E", "class + wings + booms + tail"), "A2c": ("C·W·B·E·U", "class + wings + booms + tail + propulsor units"),
             "family_b": ("F", "Lift + Cruise + CVT* family")}
#: the sets Table 7 reads, in the document's order
BRIEF_SETS = ["A0", "A1t", "A0c", "family_b"]
#: what each Table 7 set combines, in the words of the Method
SET_COMBINES = {"A0": "the architecture class", "A1t": "class · number of wings · whether any propulsor tilts",
                "A0c": "class · propulsor-unit band (1-3 / 4 / 5-6 / 7-8 / 9 or more)",
                "family_b": "the class, with the Lift + Cruise + CVT* family as one archetype"}
FAMILY_LABEL = "Lift + Cruise + CVT* family"

#: the printed words of every value of an archetype key, per field (display names of 2026-09-28).
#: Ported from: sm_text_methods.py:VALUE_WORDS (class name "Tilt Rotor" -> "Tilt Propulsor", "units" -> "propulsor units")
_NO_M3 = "no propulsion record"
_VALUE_WORDS = {
    "class": {"SLC": "Lift + Cruise", "TR": "Tilt Propulsor", "CVT": "Combined Vectored Thrust", "TW": "Tilt Wing",
              "MR": "Multirotor", "TB": "Tilt Body", "PTC": "Pitch-to-Cruise", "HB": "Hoverbike", "DS": "Deflected Slipstream",
              "PFV": "Personal Flying Vehicle", "SRW": "Stopped/Slowed Rotor Wing", "RC": "Rotorcraft"},
    "wings": {"0": "no wing", "1": "one wing", "True": "one wing", "2": "two wings", "3": "three wings", "4": "four wings",
              "blank": "wings not recorded"},
    "tilt": {"True": "a tilting propulsor", "False": "no tilting propulsor", "n/a (no M3 card)": _NO_M3},
    "units": {"0-3": "0-3 propulsor units", "1-3": "1-3 propulsor units", "4": "4 propulsor units", "5-6": "5-6 propulsor units",
              "7-8": "7-8 propulsor units", "9+": "9 or more propulsor units", "n/a (no M3 card)": _NO_M3},
}
_SET_FIELDS = {"A0": ["class"], "A0c": ["class", "units"], "A1t": ["class", "wings", "tilt"]}


def archetype_words(key, set_id: str, sep: str = " · ") -> str:
    """``"SLC · 1 · False"`` -> ``"Lift + Cruise · one wing · no tilting propulsor"`` for the sets the document names
    (C, C·U, C·W·T); any other key is returned as it is.

    Ported from: sm_text_methods.py:archetype_label"""
    fields = _SET_FIELDS.get(set_id)
    parts = [p.strip() for p in str(key).split("·")]
    if not fields or len(fields) != len(parts):
        return str(key)
    words = []
    for field, val in zip(fields, parts):
        val = val[:-2] if val.endswith(".0") else val
        words.append(_VALUE_WORDS.get(field, {}).get(val, val))
    out = []
    for w in words:
        if w == _NO_M3 and _NO_M3 in out:
            continue
        out.append(w)
    return sep.join(out)


def boom_bin(n_booms: pd.Series) -> pd.Series:
    """Number of booms -> none / 1-2 / 3 / 4+.

    Ported from: a2.py:boom_bin"""
    n = pd.to_numeric(n_booms, errors="coerce").fillna(0)
    return pd.cut(n, bins=[-1, 0, 2, 3, 10 ** 6], labels=["none", "1-2", "3", "4+"]).astype(str)


def with_boom_bin(v: pd.DataFrame) -> pd.DataFrame:
    """``v`` plus ``boomBin`` (the number of booms binned; blank where an M1 override hides the booms).

    Ported from: a2.py:archetype_frame (the boomBin column only)"""
    w = v.copy()
    w["boomBin"] = boom_bin(w["nBooms"]).where(~override_sets(w).map(lambda s: "M1" in s).astype(bool))
    return w


def level_key(frame: pd.DataFrame, set_id: str, data_dictionary: pd.DataFrame) -> pd.Series:
    """The archetype string of every aircraft in a set ("SLC · 1 · False"), blank (NaN) where the set cannot name it: a
    field hidden by a stage override, or a derived field that is not determinable. Any other blank is a design absence and
    is written "blank". Used for the counts of Tables 7 and the nine sets.

    Ported from: la_tables.py:_level_key"""
    fields = ARCHETYPE_SETS[set_id]
    left = pd.Series(False, index=frame.index)
    for f in fields:
        left |= (frame[f].isna() if f in ("anyTilt", "boomBin", "rotorBin") else _hidden(frame, f, data_dictionary))
    shown = frame[fields].astype(str).replace({"nan": "blank", "None": "blank", "<NA>": "blank"})
    return shown.agg(" · ".join, axis=1).where(~left)


def archetype_key(frame: pd.DataFrame, set_id: str) -> pd.Series:
    """The archetype string of every aircraft with an answer on every field of the set (NaN otherwise): the key the
    discovery curve and the zones count.

    Ported from: la_tables.py:_archetype_key"""
    cols = ARCHETYPE_SETS[set_id]
    fr = frame.copy()
    if "anyTilt" in cols and "anyTilt" not in fr:
        fr["anyTilt"] = None
    ok = fr[cols].notna().all(axis=1)
    return fr[cols].astype(str).agg(" · ".join, axis=1).where(ok)


#: Table 7 screens: (name, printed unit, rule text, line, direction). Ported from: la_tables.py:ARCHETYPE_SCREENS.
#: The lines come from the yaml (analysis.archetype_screens) and are filled in by :func:`archetype_screens`.
SCREEN_SOURCE = {"resolution": "archetypes", "fragmentation": "singleton share",
                 "population": "share in archetypes of five or more", "readable shares": "archetypes holding 5 % or more"}


def archetype_levels_table(ds, v: pd.DataFrame, cfg) -> pd.DataFrame:
    """Every archetype set the codebook can form: the archetypes, the aircraft that are alone in theirs, ¹D (the effective
    number, :func:`lib.diversity.effective_number`), ²D (1 / Σ p², :func:`lib.concentration.inverse_hhi`), the largest
    archetype with its share, the top three, and the archetypes of five aircraft or more. The whole corpus, all years.

    The five-aircraft size and the 5 % share line come from ``analysis.archetype_screens`` of the yaml.

    Ported from: la_tables.py:archetype_levels (the descriptive 'used in this document' column is not computed)"""
    big_n = int(cfg.analysis["archetype_screens"]["big_archetype_aircraft"])
    big_share = float(cfg.analysis["archetype_screens"]["big_archetype_share"])
    w = with_boom_bin(v[v["topType"].notna()])
    rows = []
    for sid in ARCHETYPE_SETS:
        key = level_key(w, sid, ds.data_dictionary)
        sub = w[key.notna()].copy()
        sub["key"] = key[key.notna()]
        n = len(sub)
        counts = sub["key"].value_counts()
        shares = counts / n
        big = counts[counts >= big_n]
        rows.append({"level": sid, "largest archetype": counts.index[0], "aircraft": int(n), "left out": int(key.isna().sum()),
                     "archetypes": int(len(counts)), "singletons": int((counts == 1).sum()),
                     "singleton share": round(float((counts == 1).sum() / n), 3),
                     "effective number ¹D": round(_div.effective_number(sub["key"]), 1),
                     "effective number ²D": round(_conc.inverse_hhi(counts), 1),
                     "largest share": round(float(shares.iloc[0]), 3),
                     "top three share": round(float(shares.iloc[:3].sum()), 3),
                     "archetypes of five or more": int(len(big)),
                     "share in archetypes of five or more": round(float(big.sum() / n), 3),
                     "archetypes holding 5 % or more": int((shares >= big_share).sum())})
    return pd.DataFrame(rows)


def archetype_screens(levels: pd.DataFrame, cfg) -> pd.DataFrame:
    """The four screens (fixed before the sets were compared) applied to :func:`archetype_levels_table`: at least twice as
    many archetypes as classes, at most 5 % of the aircraft alone, at least 90 % in archetypes of five or more, at least 3
    archetypes of 5 % or more. One row per set: each screen's value and pass / fail, and how many screens passed.

    Ported from: la_tables.py:archetype_level_choice (the verdict wording of the author's rulings is not ported)"""
    sc = cfg.analysis["archetype_screens"]
    classes = int(levels.loc[levels["level"].eq("A0"), "archetypes"].iloc[0])
    lines = {"resolution": 2 * classes, "fragmentation": float(sc["max_singleton_share"]),
             "population": float(sc["min_share_in_big"]), "readable shares": int(sc["min_big_share_archetypes"])}
    direction = {"resolution": "min", "fragmentation": "max", "population": "min", "readable shares": "min"}
    rows = []
    for _, r in levels.iterrows():
        row = {"level": r["level"]}
        passed = []
        for name, col in SCREEN_SOURCE.items():
            val, line = r[col], lines[name]
            ok = bool(val >= line) if direction[name] == "min" else bool(val <= line)
            row[name] = f"{val} (line {line}): {'pass' if ok else 'fail'}"
            row[name + " value"] = val
            row[name + " line"] = line
            row[name + " ok"] = ok
            passed.append(ok)
        row["screens passed"] = f"{sum(passed)} of {len(passed)}"
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ the Lift + Cruise + CVT* family F
#: the class the family is built on. Ported from: la_tables.py:FAMILY_BASE
FAMILY_BASE = "SLC"


def family_flags(ds, v: pd.DataFrame) -> pd.DataFrame:
    """Per aircraft, the three facts the family is built from: units carried on booms, a tilting propulsor set, a tilting
    wing panel. Read off ``ds.variants`` by the rules of :func:`trace_frame` (the same M3 override skip, the same
    control-only exclusion).

    Ported from: la_tables.py:family_flags"""
    raw = ds.variants
    ovs = override_sets(raw)
    rows = []
    for (_, r), ov in zip(raw.iterrows(), ovs):
        g = lambda c: r[c] if c in r.index else None
        kins, cards = [], []
        for card in _TRACE_CARDS:
            if f"M3:{card}" in ov:
                continue
            nt = _n(g(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                if _n(g(pre + "count")) <= 0 or _s(g(pre + "ctrlOnly")) == "True":
                    continue
                kins.append(_s(g(pre + "propKin")))
                cards.append(card)
        rows.append(dict(aircraft_id=r["aircraft_id"], units_on_booms=("boom" in cards),
                         tilting_set=any(k == "Tilt" for k in kins),
                         tilting_wing=any(_s(g(f"wing{k}_tilt")) == "Tilt" for k in range(1, 5))))
    return v[["aircraft_id", "topType", "window", "year"]].merge(pd.DataFrame(rows), on="aircraft_id", how="left")


def family_mask(flags: pd.DataFrame) -> pd.Series:
    """Membership of the family F: every Lift + Cruise aircraft plus every CVT* aircraft (a CVT with a tilting propulsor
    set and no tilting wing panel).

    Ported from: la_tables.py:family_mask (definition "b", the one the document reads)"""
    slc = flags["topType"].eq(FAMILY_BASE)
    cvt = flags["topType"].eq("CVT")
    return slc | (cvt & flags["tilting_set"].fillna(False) & ~flags["tilting_wing"].fillna(False))


def archetype_levels_brief(ds, v: pd.DataFrame, levels: pd.DataFrame) -> pd.DataFrame:
    """Table 7: the four archetype sets the document reads (C, C·W·T, C·U, F): aircraft, archetypes, aircraft alone in
    their archetype, ¹D, the largest archetype in words and its share, and the archetypes of five or more. The first three
    rows are :func:`archetype_levels_table`; F gives every aircraft its class except that the Lift + Cruise + CVT* family
    is one archetype.

    Ported from: sm_open.py:archetype_levels_brief"""
    lv = levels.set_index("level")
    rows = []
    for sid in BRIEF_SETS:
        code, name = SET_CODES[sid]
        if sid in lv.index:
            r = lv.loc[sid]
            rows.append({"level id": sid, "level": f"{code} — {name}", "combines": SET_COMBINES[sid],
                         "aircraft": int(r["aircraft"]), "archetypes": int(r["archetypes"]),
                         "aircraft alone in their archetype": int(r["singletons"]), "effective number ¹D": float(r["effective number ¹D"]),
                         "largest archetype": archetype_words(r["largest archetype"], sid), "its share": float(r["largest share"]),
                         "archetypes of five or more": int(r["archetypes of five or more"])})
            continue
        flags = family_flags(ds, v)
        flags = flags[flags["topType"].notna()].copy()
        key = flags["topType"].astype(str).where(~family_mask(flags), FAMILY_LABEL)
        counts = key.value_counts()
        rows.append({"level id": sid, "level": f"{code} — {name}", "combines": SET_COMBINES[sid],
                     "aircraft": int(counts.sum()), "archetypes": int(len(counts)),
                     "aircraft alone in their archetype": int((counts == 1).sum()),
                     "effective number ¹D": round(_div.effective_number(key), 1),
                     "largest archetype": str(counts.index[0]) if str(counts.index[0]) == FAMILY_LABEL
                     else archetype_words(counts.index[0], "A0"),
                     "its share": round(float(counts.iloc[0] / counts.sum()), 3),
                     "archetypes of five or more": int((counts >= 5).sum())})
    return pd.DataFrame(rows)


def top_archetype_share(v: pd.DataFrame, set_id: str, window: str, ds) -> tuple:
    """The largest archetype of one window in one set and its share of the window's aircraft (aircraft the set can name).

    Ported from: la_tables.py:top_archetypes (the 'top 1' cell)"""
    key = level_key(v, set_id, ds.data_dictionary)
    sub = key[v["window"].eq(window)].dropna()
    top = sub.value_counts(normalize=True)
    return top.index[0], float(top.iloc[0])


# ------------------------------------------------------------------ where designs concentrate (2.3)
def zones(v: pd.DataFrame, windows: List[str], min_aircraft: int = 5) -> pd.DataFrame:
    """C·U archetypes with ``min_aircraft`` or more: aircraft, distinct filers, named firms, filers per aircraft, share
    of the 2016-23 aircraft, filers in 2016-23, first and last window, the zone label and the aircraft per window.

    Zone: *new* = first seen in 2016-19 or later; *fading* = not seen after 2016-19; *persistent* otherwise. Filers =
    firms plus one per individual inventor's patent (``filer_id``). ``windows`` = the window names, in order.

    Ported from: la_tables.py:zones"""
    w = v.dropna(subset=["archetype", "window"])
    tab = pd.crosstab(w["archetype"], w["window"]).reindex(columns=windows, fill_value=0)
    recent = w[w["window"].isin(["2016-19", "2020-23"])]
    share_recent = recent["archetype"].value_counts(normalize=True)
    filers_recent = recent.groupby("archetype")["filer_id"].nunique()
    rows = []
    for a, sub in w.groupby("archetype"):
        if len(sub) < min_aircraft:
            continue
        present = [wn for wn in windows if tab.loc[a, wn] > 0]
        first, last = present[0], present[-1]
        if windows.index(first) >= 2:
            zone = "new"
        elif windows.index(last) <= 2:
            zone = "fading"
        else:
            zone = "persistent"
        cls = sub["topType"].iloc[0]
        rows.append({"archetype": a, "class": cls, "code": cls, "aircraft": int(len(sub)),
                     "filers": int(sub["filer_id"].nunique()),
                     "named firms": int(sub.loc[sub["named"], "company_canonical"].nunique()),
                     "filers per aircraft": round(float(sub["filer_id"].nunique() / len(sub)), 2),
                     "share 2016-23": round(float(share_recent.get(a, 0)), 3),
                     "filers 2016-23": int(filers_recent.get(a, 0)), "first window": first, "last window": last, "zone": zone,
                     **{wn: int(tab.loc[a, wn]) for wn in windows}})
    return pd.DataFrame(rows).sort_values(["aircraft"], ascending=False).reset_index(drop=True)


def zone_core(z: pd.DataFrame, window: str = "2020-23") -> pd.Series:
    """The crowded core: the largest archetypes (the table's order) up to and including the one that takes ``window`` past
    half of its aircraft, the columns left of that window's orange bar. Boolean mask aligned on ``z``.

    Ported from: la_tables.py:zone_core"""
    c = pd.to_numeric(z[window], errors="coerce").fillna(0).to_numpy(dtype=float)
    k = int(np.searchsorted(np.cumsum(c) / c.sum(), 0.5)) + 1
    return pd.Series([i < k for i in range(len(z))], index=z.index)


def half_column(counts) -> int:
    """Zero-based position of the first column whose cumulative aircraft pass half of the total (the orange bar of
    Figure 8 (ii)); ``counts`` in the column order of the figure.

    Ported from: la_figures.py:fig_zones (the ``half`` dict)"""
    c = np.asarray(counts, dtype=float)
    return int(np.searchsorted(np.cumsum(c) / c.sum(), 0.5))


def archetype_filer_split(v: pd.DataFrame, min_aircraft: int = 20) -> pd.DataFrame:
    """What 'few filers per aircraft' is made of, per C·U archetype with ``min_aircraft`` or more: its aircraft and
    filers, filers per aircraft, the largest filer and the aircraft it holds, and the filers holding a single aircraft.
    Filers are counted as :func:`zones` counts them.

    Ported from: sm_open.py:archetype_filer_split"""
    w = v.dropna(subset=["archetype"])
    rows = []
    for a, sub in w.groupby("archetype"):
        if len(sub) < min_aircraft:
            continue
        held = sub.groupby("filer_id").size().sort_values(ascending=False)
        top = str(held.index[0])
        rows.append({"archetype": a, "aircraft": int(len(sub)), "filers": int(len(held)),
                     "filers per aircraft": round(float(len(held) / len(sub)), 2),
                     "largest filer": ("one patent's inventor" if top.startswith("patent:") else top),
                     "its aircraft": int(held.iloc[0]), "filers holding one aircraft": int((held == 1).sum())})
    return pd.DataFrame(rows).sort_values("filers per aircraft").reset_index(drop=True)


def discovery_inputs(v: pd.DataFrame, set_ids: List[str], last_year: int) -> Dict[str, tuple]:
    """For the discovery curve: per archetype set the (priority years, archetype keys) of the aircraft of the complete
    years (priority year up to ``last_year``, the publication lag has run) that the set can name.

    Ported from: sm_open.py:discovery_curve (the aircraft selection: _complete, then the notna key)"""
    w = v.dropna(subset=["year"])
    w = w[w["year"].le(last_year)].copy()
    out = {}
    for sid in set_ids:
        key = archetype_key(w, sid)
        ok = key.notna()
        out[sid] = (w.loc[ok, "year"].to_numpy(), key[ok])
    return out


def discovery_estimators(inputs: Dict[str, tuple], curve: pd.DataFrame, tail: int = _div.TAIL) -> pd.DataFrame:
    """Per set: archetypes seen, seen once / twice, Chao1 with its interval and the estimated unseen
    (:func:`lib.diversity.chao1_jackknife`), the share of the estimated richness found, and the new archetypes in the last
    ``tail`` aircraft in date order against the same tail in random order (:func:`lib.diversity.discovery_tail`).

    Ported from: sm_open.py:discovery_estimators (the verdict sentence is wording; the rule is lib.diversity.discovery_verdict_code)"""
    rows = []
    for sid, (_, keys) in inputs.items():
        counts = keys.value_counts().to_numpy()
        est = _div.chao1_jackknife(counts)
        c = curve[curve["level"].eq(sid)].sort_values("aircraft")
        t = _div.discovery_tail(c["archetypes (date order)"].to_numpy(), c["archetypes (random order)"].to_numpy(), tail)
        rows.append({"level": sid, "aircraft": est["aircraft"], "archetypes observed": est["observed"],
                     "seen once (f1)": est["singletons f1"], "seen twice (f2)": est["doubletons f2"],
                     "Chao1": round(est["Chao1"], 1), "Chao1 95 % low": round(est["Chao1 low"], 1),
                     "Chao1 95 % high": round(est["Chao1 high"], 1), "estimated unseen": round(est["Chao1"] - est["observed"], 1),
                     "jackknife 1": round(est["jackknife 1"], 1), "jackknife 2": round(est["jackknife 2"], 1),
                     "coverage": round(est["coverage (Good–Turing)"], 4),
                     "share of richness found": round(est["observed"] / est["Chao1"], 3),
                     "archetypes by half the corpus": round(t["half"], 1),
                     f"new in the last {tail} aircraft": round(t["last"], 2),
                     f"new in the {tail} before that": round(t["prev"], 2),
                     f"new in the last {tail}, random order": round(t["rar_last"], 2),
                     "date order vs random, last tail": round(t["last"] - t["rar_last"], 2),
                     "verdict code": _div.discovery_verdict_code(est, t["last"], t["rar_last"])})
    return pd.DataFrame(rows)


# ====================================================================================== chapter 3 (notebook 42)
from lib import dominant_design as _dd                   # noqa: E402
from lib import drivers as _drv                          # noqa: E402
from lib import distance as _dist                        # noqa: E402

#: the four archetype sets of the dominant-design test, in the order the document prints them (F = the family).
#: Ported from: sm_open.py:DD_LEVELS
DD_LEVELS = ("A0", "A1t", "A0c", "family_b")
#: the years drawn in Figure 11, the minimum aircraft of a read year (the trend minimum) and the bases of condition 1.
#: Ported from: sm_open.py:DD_YEAR_FIRST, DD_YEAR_MIN, DD_BASES
DD_YEAR_FIRST = 2008
DD_YEAR_MIN = 20
DD_BASES = (("in force", "aircraft with a patent in force"), ("all", "all aircraft of the year"))
#: the two weightings of condition 3, main first: ``w15`` (the 15 dimensions the dissertation declares, 2026-10-15) and ``w34`` (the
#: 34-dimension weighting of 2026-10-14, kept for the record). Ported from: la_tables.py:Q_WEIGHTINGS (then "subsystem", "uniform")
Q_WEIGHTINGS = ("w15", "w34")
#: level id -> "C — Class" as the verdict table heads its columns. Ported from: sm_text_methods.py:LEVEL_CODES
DD_LEVEL_WORDS = {"A0": "C — Class", "A1t": "C·W·T — Class + wings + tilt", "A0c": "C·U — Class + units",
                  "family_b": "F — Lift + Cruise + CVT* family"}


def class_counts_by_window(v: pd.DataFrame, window_names: List[str]) -> pd.DataFrame:
    """Unique aircraft per priority window (rows) and architecture class (columns); the aircraft of a window with no class
    recorded are the column ``Other`` (the document counts them in the window's total).

    Ported from: atlas.py:fig_arch_time (the crosstab; the shares are counts / row sum)"""
    w = v.dropna(subset=["window"])
    return pd.crosstab(w["window"], w["topType"].fillna("Other")).reindex(window_names).fillna(0).astype(int)


def patent_state(ds, v: pd.DataFrame) -> pd.DataFrame:
    """Per unique aircraft: ``in_force`` = at least one linked patent (primary or duplicate) whose PatSeer status is known
    and not INACTIVE (granted and alive, or still under examination); ``granted_live`` = at least one linked patent
    ``ACTIVE - GRANTED``. Index = aircraft_id.

    Ported from: sm_open.py:_patent_state"""
    links = aircraft_patents(ds, v)
    links["_live"] = links["status_known"] & ~links["inactive"]
    links["_gl"] = links["legal_status_raw"].fillna("").astype(str).str.strip().eq("ACTIVE - GRANTED")
    per = links.groupby("aircraft_id").agg(in_force=("_live", "any"), granted_live=("_gl", "any"))
    out = v[["aircraft_id"]].join(per, on="aircraft_id")
    return out.fillna({"in_force": False, "granted_live": False}).set_index("aircraft_id")


def dd_level_keys(ds, v: pd.DataFrame) -> Dict[str, pd.Series]:
    """The archetype of every aircraft at each of :data:`DD_LEVELS` (index = ``v``'s), NaN where the level cannot name it.
    F keeps every aircraft's class except that the aircraft of the family share one archetype, FAMILY_LABEL.

    Ported from: sm_open.py:_level_keys"""
    keys = {lvl: archetype_key(v, lvl) for lvl in DD_LEVELS if lvl != "family_b"}
    flags = family_flags(ds, v)
    fam_ids = set(flags.loc[family_mask(flags), "aircraft_id"])
    f = v["topType"].astype(object).where(~v["aircraft_id"].isin(fam_ids), FAMILY_LABEL)
    keys["family_b"] = f.where(v["topType"].notna())
    return keys


def _key_words(key, level: str) -> str:
    """An archetype key in words (F's own archetype keeps its name). Ported from: sm_open.py:_key_word"""
    if key == FAMILY_LABEL or level == "family_b":
        return str(key) if key == FAMILY_LABEL else archetype_words(key, "A0")
    return archetype_words(key, level)


def dd_yearly(ds, v: pd.DataFrame, last_year: int) -> pd.DataFrame:
    """Condition 1: per level, base and priority year the largest archetype's share (:func:`lib.dominant_design.yearly_top_share`),
    2008 to ``last_year``; ``read`` = the year's base holds 20 aircraft or more.

    Ported from: sm_open.py:dd_yearly"""
    state = patent_state(ds, v)
    keys = dd_level_keys(ds, v)
    parts = []
    for level in DD_LEVELS:
        k = keys[level]
        w = v.assign(_k=k)[k.notna()]
        w = w.assign(_live=w["aircraft_id"].map(state["in_force"]).astype(bool))
        for base, _ in DD_BASES:
            b = w[w["_live"]] if base == "in force" else w
            t = _dd.yearly_top_share(b["_k"], b["year"], range(DD_YEAR_FIRST, last_year + 1), DD_YEAR_MIN)
            t["largest archetype"] = [_key_words(a, level) if n else "" for a, n in zip(t["largest archetype"], t["aircraft"])]
            t.insert(0, "base", base)
            t.insert(0, "level", DD_LEVEL_WORDS[level])
            t.insert(0, "level id", level)
            parts.append(t)
    return pd.concat(parts, ignore_index=True)


def family_yearly(ds, v: pd.DataFrame, last_year: int) -> pd.DataFrame:
    """Figure 11: F's share of each priority year on both bases of condition 1 (:func:`lib.dominant_design.family_share_by_year`),
    with the share of the in-force aircraft that hold a granted live patent.

    Ported from: sm_open.py:family_yearly"""
    state = patent_state(ds, v)
    f = dd_level_keys(ds, v)["family_b"]
    w = v.assign(_f=f.eq(FAMILY_LABEL))[f.notna()]
    w = w.assign(_live=w["aircraft_id"].map(state["in_force"]).astype(bool),
                 _gl=w["aircraft_id"].map(state["granted_live"]).astype(bool))
    years = range(DD_YEAR_FIRST, last_year + 1)
    allb = _dd.family_share_by_year(w["_f"], w["year"], years, DD_YEAR_MIN)
    live = w[w["_live"]]
    inf = _dd.family_share_by_year(live["_f"], live["year"], years, DD_YEAR_MIN)
    gl = w[w["_gl"]]
    glr = _dd.family_share_by_year(gl["_f"], gl["year"], years, 1)
    out = pd.DataFrame({
        "priority year": allb["priority year"], "aircraft": allb["aircraft"], "F aircraft": allb["F aircraft"],
        "F share": allb["F share"], "aircraft in force": inf["aircraft"], "F aircraft in force": inf["F aircraft"],
        "F share in force": inf["F share"],
        "in force with a granted patent": [round(g / n, 4) if n else np.nan for g, n in
                                           zip([int(w[w["_live"] & w["year"].eq(y) & w["_gl"]].shape[0]) for y in years], inf["aircraft"])],
        "F share, granted and live": glr["F share"].where(glr["aircraft"] > 0),
        "read, in force": inf["read"], "read, all": allb["read"]})
    return out


# ---- the Gower distance inputs (condition 3)
#: Ported from: a3.py:WING_BORNE
WING_BORNE = ("wing", "wing_boom", "both")
_LABEL_SECTIONS = ("G1", "M1", "M2", "M3")
_PROCESS_PATTERNS = ("humanUncertain", "quickOverride", "quickCount")


def wing_borne_thrust(v: pd.DataFrame) -> pd.Series:
    """Does the wing carry thrust (wing card, wing-attached boom, or both)? ``wing-borne`` / ``not wing-borne``; blank on a
    wingless aircraft, where an override hides it, and on HB/PFV.

    Ported from: a3.py:wing_borne_thrust"""
    if "wing_thrust_carrier" not in v.columns:
        return pd.Series(pd.NA, index=v.index, dtype=object)
    c = v["wing_thrust_carrier"].astype(object)
    out = c.map(lambda x: "wing-borne" if x in WING_BORNE else "not wing-borne" if x == "none" else pd.NA)
    out[v["topType"].isin(["HB", "PFV"])] = pd.NA
    return out


def derived_layer(variants: pd.DataFrame) -> pd.DataFrame:
    """Per aircraft the propulsion variables the distance reads: units, any tilting, fixed and tilting mixed, any ducted,
    all ducted, and the pooled wing-borne pair. A value an override hides is <NA>, never 0 or False (rule 1).

    Ported from: a3.py:derived_layer (the columns the distance uses)"""
    v = variants
    st = propulsion_states(v)
    pu = propulsor_units(v)
    out = pd.DataFrame({
        "propulsor_units": pu["units"].to_numpy(),
        "any_tilting_unit": st["any_tilting"].to_numpy(),
        "mixes_fixed_and_tilting": (st["any_tilting"] & st["any_fixed"]).to_numpy(),
        "any_ducted_unit": st["any_ducted"].to_numpy(),
        "all_units_ducted": st["all_ducted"].to_numpy(),
        "wing_borne_thrust": wing_borne_thrust(v).to_numpy(),
        "wing_borne_units": pd.to_numeric(v.get("wing_borne_units", pd.Series(index=v.index)), errors="coerce").to_numpy()},
        index=v.index)
    for c in ("any_tilting_unit", "mixes_fixed_and_tilting", "any_ducted_unit", "all_units_ducted"):
        out[c] = out[c].astype("boolean")
    return out


def informative_fields(ds, min_answered: int = 300, min_effk: float = 1.5) -> List[str]:
    """The label fields that carry information: coded G1-M3 columns (process columns removed) answered by at least
    ``min_answered`` aircraft with an effective number of answers (¹D) of ``min_effk`` or more, most informative first.

    Ported from: a2.py:answerable_slots, d2_field_inventory, d2_informative_fields"""
    dd = ds.data_dictionary
    keep = (dd["section"].isin(_LABEL_SECTIONS) & dd["kind"].isin(["id", "bool", "int"])
            & ~dd["column"].str.contains("|".join(_PROCESS_PATTERNS), case=False))
    slots = [c for c in dd.loc[keep, "column"] if c in ds.master.columns]
    rows = [{"field": s, "answered": int(ds.variants[s].notna().sum()), "eff": _div.effective_number(ds.variants[s])} for s in slots]
    inv = pd.DataFrame(rows)
    inv = inv[(inv["answered"] >= min_answered) & (inv["eff"] >= min_effk)].sort_values("eff", ascending=False)
    return list(inv["field"])


#: The w34 weighting of the form distance (author's ruling 2026-10-14, kept for the record; the reported weighting is :data:`FORM15`): the 34 dimensions of the codebook (Appendix A) follow its four
#: systems and each system weighs 1; inside a system the weight is shared equally by its dimensions, except in M2, where the wings
#: weigh twice the empennage. THE ONLY PLACE the weights are defined: (system, dimensions, weight of the group, numeric dimensions).
_PROP_DIMS = ["Propulsor count", "Thrust Kinematics", "Propulsor Articulation", "Tractor/Pusher Arrangement", "Propulsor Enclosure",
              "Retraction Kinematics", "Airframe Mounting Zone", "Empennage Mounting Zone", "Wing Chordwise Zone", "Wing Spanwise Zone"]
_BOOM_DIMS = ["Booms present", "Boom count", "Boom Attachment", "Boom-Wing Panel Index", "Boom Longitudinal Position",
              "Boom Spanwise Position", "Boom Orientation", "Boom-Wing Relationship", "Boom articulation", "Booms retract/stow"]
FORM_GROUPS = [
    ("G1 architecture", ["Architecture"], 1.0),
    ("M1 structure", ["Fuselage Shape", "Fuselage Kinematics", "Ground Contact Interface", "Airframe Lateral Symmetry"] + _BOOM_DIMS, 1.0),
    ("M2 wings", ["Wing Architecture", "Wing count", "Vertical Position", "Longitudinal Position", "Planform", "Tip-joined", "Tilt", "Role"], 2 / 3),
    ("M2 empennage", ["Empennage Type"], 1 / 3),
    ("M3 propulsion", _PROP_DIMS, 1.0),
]
FORM_NUMERIC = {"Wing count", "Boom count", "Propulsor count"}
#: dimension -> column of the data export (per-wing dimensions read the primary wing, :func:`primary_wing`; per-boom dimensions read boom group 1;
#: the propulsor dimensions are read by :func:`_propulsor_set`)
_FORM_COLUMN = {"Architecture": "topType", "Fuselage Shape": "fusShape", "Fuselage Kinematics": "fusKin", "Ground Contact Interface": "gearArch",
                "Airframe Lateral Symmetry": "latSym", "Booms present": "boomsPresent", "Boom count": "boom1_count", "Boom Attachment": "boom1_attach",
                "Boom-Wing Panel Index": "boom1_wingIdx", "Boom Longitudinal Position": "boom1_long", "Boom Spanwise Position": "boom1_span",
                "Boom Orientation": "boom1_orient", "Boom-Wing Relationship": "boom1_wingRel", "Boom articulation": "boom1_tilts",
                "Booms retract/stow": "boom1_retracts", "Wing Architecture": "wingConf", "Wing count": "wCount", "Vertical Position": "wing1_posV",
                "Longitudinal Position": "wing1_posL", "Planform": "wing1_plan", "Tip-joined": "wing1_tipJoin", "Tilt": "wing1_tilt",
                "Role": "wing1_role", "Empennage Type": "empType"}
#: propulsor dimension -> suffix of the column of the selected set (``<card>_`` or ``<card>_t<N>_`` + suffix)
_PROP_SUFFIX = {"Thrust Kinematics": "orient", "Propulsor Articulation": "propKin", "Tractor/Pusher Arrangement": "chord",
                "Propulsor Enclosure": "bmech", "Retraction Kinematics": "rmech"}
#: the "N/A" option of the boom position fields: the dimension does not apply, so it is left blank (delta = 0)
_NOT_APPLICABLE = {"Boom Longitudinal Position", "Boom Spanwise Position", "Boom-Wing Relationship"}
FORM_FIELDS = [d for _, dims, _ in FORM_GROUPS for d in dims]


#: per-wing dimensions of the form distance (read on the primary wing)
_WING_DIMS = {"Vertical Position", "Longitudinal Position", "Planform", "Tip-joined", "Tilt", "Role"}
_POSL_ORDER = {"Fwd": 0, "Cent": 1, "Aft": 2}


#: the author's check of R5-03 on the drawings (2026-10-16): in these designs the role reading gave wing 2, but wing 1 is the largest as drawn
PRIMARY_WING_RULED = {"US2019144107A1_ua1": 1, "US2019144109A1_ua1": 1, "US2018290736A1_ua1": 1, "GB201903200D0_ua1": 1}


def primary_wing(r) -> int:
    """Number (1-4) of the primary wing of a design, codebook rule R5-03: the wing with the largest area as drawn; with equal areas, the
    forward-most. The record holds no drawn area, only each wing's role: wing 1 is always the Main wing (the largest), and a wing whose
    role is Tandem (equal size) or Main ties with it, so among those the forward-most wing (``posL`` Fwd < Cent < Aft) is primary and a
    tie in position keeps the lower number. Canard, Aft stabiliser, Stacked (same position) and Other are not larger than wing 1.
    Where the author checked the drawing (:data:`PRIMARY_WING_RULED`), the ruling decides."""
    ruled = PRIMARY_WING_RULED.get(_s(r.get("aircraft_id")))
    if ruled:
        return ruled
    best = 1
    for k in (2, 3, 4):
        if _s(r.get(f"wing{k}_role")) in ("Tandem", "Main"):
            a, b = _s(r.get(f"wing{best}_posL")), _s(r.get(f"wing{k}_posL"))
            if a in _POSL_ORDER and b in _POSL_ORDER and _POSL_ORDER[b] < _POSL_ORDER[a]:
                best = k
    return best


# ---- the w15 weighting (the dissertation's declaration, 2026-10-15): 15 dimensions, each of the four systems weighing 1, 4 in all.
#: (system, dimension, codebook field, compared as, kind, weight). kind = "categorical" (0 same option, 1 different), ("ordered", r)
#: (a rank 0..r held in a numeric column; d = rank difference / r, the range fixed at r), ("number", r) (a number; d = difference / r),
#: or "set" (a frozenset of stations; d = Jaccard distance). THE ONLY PLACE the w15 weights are defined.
FORM15 = [
    ("G1 architecture", "Architecture", "topType", "0 same option, 1 different", "categorical", 1.0),
    ("M1 structure", "Fuselage Shape", "fusShape", "0 same option, 1 different", "categorical", 0.5),
    ("M1 structure", "Boom count", "boomsPresent, boom1..6_count", "ordered 0, 1, 2, 3 to 4, 5 or more; rank difference / 4", ("ordered", 4), 0.3),
    ("M1 structure", "Fuselage Kinematics", "fusKin", "0 same option, 1 different", "categorical", 0.2),
    ("M2 aerodynamics", "Wing count", "wCount", "ordered 0, 1, 2, 3; difference / 3", ("ordered", 3), 0.3),
    ("M2 aerodynamics", "Wing Architecture", "wingConf", "0 same option, 1 different", "categorical", 0.3),
    ("M2 aerodynamics", "Vertical Position", "wing1_posV", "0 same option, 1 different", "categorical", 1 / 45),
    ("M2 aerodynamics", "Longitudinal Position", "wing1_posL", "0 same option, 1 different", "categorical", 1 / 45),
    ("M2 aerodynamics", "Planform", "wing1_plan", "0 same option, 1 different", "categorical", 1 / 45),
    ("M2 aerodynamics", "Empennage Type", "empType", "0 same option, 1 different", "categorical", 1 / 3),
    ("M3 propulsion", "Propulsor band", "propulsor_units", "ordered 1 to 3, 4, 5 to 6, 7 to 8, 9 or more; rank difference / 4", ("ordered", 4), 0.35),
    ("M3 propulsion", "Tilt share", "<station>_count, propKin, wing tilt, empTilts, boom_thrust_state, fusKin",
     "share 0 to 1 of the propulsors whose thrust turns between hover and cruise; absolute difference", ("number", 1), 0.3),
    ("M3 propulsion", "Propulsor Enclosure", "<set>_bmech", "0 same option, 1 different (the set with the most propulsors)", "categorical", 0.15),
    ("M3 propulsion", "Tractor/Pusher Arrangement", "<set>_chord", "0 same option, 1 different (the set with the most propulsors)", "categorical", 0.1),
    ("M3 propulsion", "Mount locations", "<station>_count", "stations carrying propulsors among fuselage, wing, boom, empennage; Jaccard distance", "set", 0.1),
]
FORM15_FIELDS = [d for _, d, _, _, _, _ in FORM15]
FORM15_NUMERIC = {d for _, d, _, _, k, _ in FORM15 if isinstance(k, tuple)}
FORM15_RANGES = {d: float(k[1]) for _, d, _, _, k, _ in FORM15 if isinstance(k, tuple)}
FORM15_SETS = {d for _, d, _, _, k, _ in FORM15 if k == "set"}
#: boom count -> rank (0, 1, 2, 3-4, 5+) and the stations of the mount-location set
_BOOM_RANK = lambda n: 0 if n <= 0 else 1 if n == 1 else 2 if n == 2 else 3 if n <= 4 else 4          # noqa: E731
_MOUNT_STATION = {"fuselage": "fuselage", "core_layout": "fuselage", "hull_array": "fuselage", "wing1": "wing", "wing2": "wing",
                  "wing3": "wing", "wing4": "wing", "boom": "boom", "emp": "empennage"}


def form_weights(fields=None, weighting: str = None) -> Dict[str, float]:
    """Weight of each dimension in the form distance under ``weighting`` (default the main one, :data:`Q_WEIGHTINGS`):
    w15 reads :data:`FORM15`; w34 gives w = (weight of its group) / (number of dimensions of the group)."""
    weighting = weighting or Q_WEIGHTINGS[0]
    if weighting == "w15":
        w = {d: wt for _, d, _, _, _, wt in FORM15}
        return {f: w[f] for f in (FORM15_FIELDS if fields is None else fields)}
    if weighting != "w34":
        raise ValueError(f"unknown weighting {weighting!r}; one of {Q_WEIGHTINGS}")
    w = {d: g / len(dims) for _, dims, g in FORM_GROUPS for d in dims}
    return {f: w[f] for f in (FORM_FIELDS if fields is None else fields)}


def form_weights_table(weighting: str = None) -> pd.DataFrame:
    """The weights table. w15: one row per dimension (system, dimension, codebook field, compared as, weight) and a total row;
    w34: system, dimensions, count, weight of each, weight in all (a total row last)."""
    weighting = weighting or Q_WEIGHTINGS[0]
    if weighting == "w15":
        rows = [{"system": s, "dimension": d, "codebook field": c, "compared as": how, "weight": round(wt, 3)} for s, d, c, how, _, wt in FORM15]
        rows.append({"system": "total", "dimension": f"{len(FORM15)} dimensions", "codebook field": "", "compared as": "",
                     "weight": round(sum(wt for *_, wt in FORM15), 3)})
        return pd.DataFrame(rows)
    rows = [{"system": s, "dimensions": "; ".join(dims), "count": len(dims), "weight of each": round(g / len(dims), 3), "weight in all": round(g, 3)}
            for s, dims, g in FORM_GROUPS]
    rows.append({"system": "total", "dimensions": "", "count": sum(r["count"] for r in rows), "weight of each": np.nan,
                 "weight in all": round(sum(g for _, _, g in FORM_GROUPS), 3)})
    return pd.DataFrame(rows)


def _propulsor_set(r: pd.Series):
    """The propulsor set a design is read by: among the sets with propulsors (a card, or each of its types when it has several; a control-only set is
    not a propulsor set), the one with the most propulsors, a tie going to the first listed (card order of ``M3_STATIONS``, then type number).
    Returns (card, column prefix, count) or None.  A set of an overridden card has its quick count and no detail."""
    best = None
    for card in M3_STATIONS:
        nt = _n(r.get(f"{card}_ntypes")) or 1
        for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
            cnt = _n(r.get(pre + "count"))
            if cnt > 0 and _s(r.get(pre + "ctrlOnly")) != "True" and (best is None or cnt > best[2]):
                best = (card, pre, cnt)
    return best


def form_frame34(ds) -> pd.DataFrame:
    """The w34 frame: the designs with an architecture and their 34 dimensions (one column each, named as the codebook). A dimension that does not apply
    (no boom, no second wing, no propulsor of that kind, an N/A answer) or that an override hides is blank, and the distance leaves a blank out
    of the average (delta = 0), never counts it as a mismatch.  Per-wing dimensions read the primary wing (R5-03), per-boom dimensions boom group 1, the
    propulsor dimensions the set with the most propulsors (:func:`_propulsor_set`); the zone dimensions are blank unless that set sits on
    the fuselage (Airframe), the empennage or a wing (Chordwise, Spanwise)."""
    v = ds.variants
    v = v[v["topType"].notna()]
    out = pd.DataFrame({"aircraft_id": v["aircraft_id"].to_numpy()}, index=v.index)
    prim = v.apply(primary_wing, axis=1)                    # codebook R5-03: the wing the per-wing dimensions are read on
    for d, c in _FORM_COLUMN.items():
        if d in _WING_DIMS and c in v.columns:
            x = pd.Series([r_.get(f"wing{k}_{c.split('_', 1)[1]}") if k != 1 else r_.get(c) for (_, r_), k in zip(v.iterrows(), prim)],
                          index=v.index, dtype=object)
            if d == "Role":
                x = x.where(prim.eq(1), "Main")            # the primary wing is the main wing, whichever number it carries
        else:
            x = v[c].astype(object) if c in v.columns else pd.Series(pd.NA, index=v.index, dtype=object)
        x = x.where(x.notna(), np.nan)
        if d in _NOT_APPLICABLE:
            x = x.where(x.ne("NA"), np.nan)
        out[d] = x
    for d in FORM_NUMERIC:
        out[d] = pd.to_numeric(out[d], errors="coerce") if d in out else np.nan
    cols = {d: [] for d in _PROP_DIMS}
    for _, r in v.iterrows():
        sel = None if _s(r.get("topType")) in NO_UNITS_TYPES else _propulsor_set(r)
        card, pre, cnt = sel if sel else (None, None, np.nan)
        row = {d: np.nan for d in _PROP_DIMS}
        row["Propulsor count"] = cnt
        if sel:
            for d, suf in _PROP_SUFFIX.items():
                row[d] = _s(r.get(pre + suf)) or np.nan
            if card in ("fuselage", "hull_array", "core_layout"):
                row["Airframe Mounting Zone"] = _s(r.get(pre + "zone")) or np.nan
            elif card == "emp":
                row["Empennage Mounting Zone"] = _s(r.get(pre + "zone")) or np.nan
            elif card.startswith("wing"):
                row["Wing Chordwise Zone"] = _s(r.get(pre + "zoneChord")) or np.nan
                row["Wing Spanwise Zone"] = _s(r.get(pre + "zoneSpan")) or np.nan
        for d in _PROP_DIMS:
            cols[d].append(row[d])
    for d in _PROP_DIMS:
        out[d] = cols[d]
    for d in FORM_NUMERIC:
        out[d] = pd.to_numeric(out[d], errors="coerce").astype(float)
    return out


def _tilt_share(r: pd.Series, ov: frozenset) -> float:
    """Share of a design's propulsors whose thrust turns between hover and cruise (the w15 tilt-share dimension).

    Propulsors are counted per station and type as :func:`propulsion_states` reads them (``<station>_count`` or ``<station>_t<N>_count``
    when ``<station>_ntypes`` > 1, control-only sets left out). A propulsor tilts when its own ``propKin`` is Tilt; or it sits on wing k with
    ``wing{k}_tilt`` Tilt; or on the empennage with ``empTilts`` True; or on the boom card and notebook 04's ``boom_thrust_state`` is ``tilting``
    or ``on_tilting_wing`` (``mixed``: the boom types with propKin Tilt count; when no type says Tilt the tick sits on the boom groups, and the
    boom propulsors are prorated by the share of the propeller-carrying booms whose group is ticked ``tilts``); or the whole airframe
    reorients (``fusKin`` TiltBody, or a Tilt Body design): share 1. NaN when the design has no propulsor card (HB/PFV), when an override
    hides a station or the wing/boom tilt a propulsor would read, or when no propulsor is recorded."""
    g = lambda c: r[c] if c in r.index else None                                 # noqa: E731
    if _s(g("topType")) in NO_UNITS_TYPES:
        return np.nan
    if _s(g("fusKin")) == "TiltBody" or _s(g("topType")) == "TB":
        return 1.0
    if any(t.startswith("M3:") for t in ov):
        return np.nan
    tw = {k for k in range(1, 5) if _s(g(f"wing{k}_tilt")) == "Tilt"}
    total = tilting = 0.0
    for card in M3_STATIONS:
        nt = _n(g(f"{card}_ntypes")) or 1
        pres = [f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]
        kinds = [(_n(g(pre + "count")), _s(g(pre + "propKin"))) for pre in pres
                 if _n(g(pre + "count")) > 0 and _s(g(pre + "ctrlOnly")) != "True"]
        if not kinds:
            continue
        cnt = sum(c for c, _ in kinds)
        own = sum(c for c, pk in kinds if pk == "Tilt")
        total += cnt
        if card == "boom":
            state = _s(g("boom_thrust_state")) or ("" if "M1" in ov else _boom_state(_boom_categories(r, tw)))
            if state in ("tilting", "on_tilting_wing"):
                tilting += cnt
            elif state == "mixed":
                if own > 0:
                    tilting += own
                else:                                       # the tick sits on the boom groups: prorate by the ticked propeller booms
                    grp = [(_n(g(f"boom{k}_count")), _s(g(f"boom{k}_tilts")) == "True") for k in range(1, 7)
                           if (_s(g(f"boom{k}_attach")) or _n(g(f"boom{k}_count"))) and _s(g(f"boom{k}_hasProps")) != "False"]
                    nb = sum(c for c, _ in grp)
                    tilting += cnt * (sum(c for c, t in grp if t) / nb) if nb else 0.0
            elif state == "":                               # an M1 override hides the groups: only a propKin Tilt is sure
                if own < cnt:
                    return np.nan
                tilting += own
            else:                                           # fixed
                tilting += own
        elif card.startswith("wing"):
            if "M2" in ov and own < cnt:
                return np.nan
            tilting += cnt if int(card[4:]) in tw else own
        elif card == "emp":
            if "M2" in ov and own < cnt:
                return np.nan
            tilting += cnt if _s(g("empTilts")) == "True" else own
        else:
            tilting += own
    return tilting / total if total > 0 else np.nan


def _mount_locations(r: pd.Series, ov: frozenset):
    """The set of stations (fuselage, wing, boom, empennage) carrying non-control-only propulsors; None when the design has no propulsor
    card (HB/PFV), when an M3 override hides a station, or when no propulsor is recorded. M3 cards map: fuselage, core_layout and hull_array
    -> fuselage; wing1..4 -> wing; boom -> boom; emp -> empennage."""
    g = lambda c: r[c] if c in r.index else None                                 # noqa: E731
    if _s(g("topType")) in NO_UNITS_TYPES or any(t.startswith("M3:") for t in ov):
        return None
    where = set()
    for card in M3_STATIONS:
        nt = _n(g(f"{card}_ntypes")) or 1
        for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
            if _n(g(pre + "count")) > 0 and _s(g(pre + "ctrlOnly")) != "True":
                where.add(_MOUNT_STATION.get(card, card))
    return frozenset(where) if where else None


def form_frame15(ds) -> pd.DataFrame:
    """The w15 frame: the designs with an architecture and the 15 dimensions of :data:`FORM15` (one column each), plus ``aircraft_id``.
    Categorical dimensions hold the option; ordered dimensions the rank (Boom count: 0 when ``boomsPresent`` is not True, else the design's
    number of booms = boom1..6_count summed as :func:`archetype_columns` does, ranked 0, 1, 2, 3-4, 5+; Wing count: ``wCount``, 0 when blank
    or no wing, blank under an M2 override; Propulsor band: :func:`propulsor_units` in :data:`ROTOR_BINS`, rank 0..4, blank where the count is
    not determinable); Tilt share a number 0..1 (:func:`_tilt_share`); Mount locations a frozenset (:func:`_mount_locations`). The three
    wing-1 dimensions read the primary wing (:func:`primary_wing`, codebook R5-03), which is wing 1 in every design of the corpus (author's
    check of 2026-10-16), and are blank when the design has no wing. A blank is left out of the pair's average (delta = 0), never a mismatch;
    the propulsion dimensions are blank for designs with no propulsor card."""
    v = ds.variants
    v = v[v["topType"].notna()]
    ovs = override_sets(v)
    out = pd.DataFrame({"aircraft_id": v["aircraft_id"].to_numpy()}, index=v.index)
    cat = lambda c: (v[c].astype(object) if c in v.columns else pd.Series(pd.NA, index=v.index, dtype=object)).map(lambda x: _s(x) or np.nan)  # noqa: E731
    out["Architecture"] = cat("topType")
    out["Fuselage Shape"] = cat("fusShape")
    boom_cols = [c for c in v.columns if re.match(r"boom\d_count$", c)]
    nbooms = v[boom_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    nbooms = nbooms.where(v["boomsPresent"].map(_s).eq("True"), 0)
    out["Boom count"] = nbooms.map(_BOOM_RANK).astype(float)
    out["Fuselage Kinematics"] = cat("fusKin")
    wc = pd.to_numeric(v["wCount"], errors="coerce").fillna(0).clip(lower=0)
    out["Wing count"] = wc.where(~ovs.map(lambda o: "M2" in o), np.nan).astype(float)
    out["Wing Architecture"] = cat("wingConf")
    prim = v.apply(primary_wing, axis=1)
    for d, suf in (("Vertical Position", "posV"), ("Longitudinal Position", "posL"), ("Planform", "plan")):
        out[d] = pd.Series([_s(r_.get(f"wing{k}_{suf}")) or np.nan for (_, r_), k in zip(v.iterrows(), prim)], index=v.index, dtype=object)
    out["Empennage Type"] = cat("empType")
    units = propulsor_units(v)["units"]
    band = pd.cut(units, bins=ROTOR_BINS[0], labels=False).astype(float)
    out["Propulsor band"] = band.where(units.notna(), np.nan)
    out["Tilt share"] = [_tilt_share(r_, ov) for (_, r_), ov in zip(v.iterrows(), ovs)]
    enc, arr, mount = [], [], []
    for (_, r_), ov in zip(v.iterrows(), ovs):
        sel = None if _s(r_.get("topType")) in NO_UNITS_TYPES else _propulsor_set(r_)
        enc.append((_s(r_.get(sel[1] + "bmech")) or np.nan) if sel else np.nan)
        arr.append((_s(r_.get(sel[1] + "chord")) or np.nan) if sel else np.nan)
        mount.append(_mount_locations(r_, ov))
    out["Propulsor Enclosure"] = pd.Series(enc, index=v.index, dtype=object)
    out["Tractor/Pusher Arrangement"] = pd.Series(arr, index=v.index, dtype=object)
    out["Mount locations"] = pd.Series(mount, index=v.index, dtype=object)
    for d in FORM15_NUMERIC:
        out[d] = pd.to_numeric(out[d], errors="coerce").astype(float)
    return out[["aircraft_id"] + FORM15_FIELDS]


def form_frame(ds, weighting: str = None) -> pd.DataFrame:
    """The frame of the form distance under ``weighting`` (default the main one): :func:`form_frame15` or :func:`form_frame34`."""
    weighting = weighting or Q_WEIGHTINGS[0]
    if weighting == "w15":
        return form_frame15(ds)
    if weighting == "w34":
        return form_frame34(ds)
    raise ValueError(f"unknown weighting {weighting!r}; one of {Q_WEIGHTINGS}")


class FormInputs(NamedTuple):
    """Everything :func:`lib.distance.gower_distance` needs for the form distance of condition 3 under one weighting."""
    frame: pd.DataFrame
    fields: List[str]
    numeric: set
    weights: Dict[str, float]
    ranges: Dict[str, float]
    sets: set
    weighting: str


def gower_inputs(ds, weighting: str = None) -> FormInputs:
    """The inputs of the distance of condition 3 under ``weighting`` (default the main one, w15): the designs with an architecture and their
    dimensions (:func:`form_frame`), the dimensions, those compared by range (with their fixed range under w15), those compared by Jaccard
    distance (sets), and the weights (:func:`form_weights`)."""
    weighting = weighting or Q_WEIGHTINGS[0]
    frame = form_frame(ds, weighting)
    if weighting == "w15":
        return FormInputs(frame, list(FORM15_FIELDS), set(FORM15_NUMERIC), form_weights(None, "w15"), dict(FORM15_RANGES), set(FORM15_SETS), "w15")
    return FormInputs(frame, list(FORM_FIELDS), set(FORM_NUMERIC), form_weights(None, "w34"), {}, set(), "w34")


def form_distance(ds, weighting: str = None) -> tuple:
    """The Gower distance matrix of condition 3 under ``weighting`` (default w15) and its frame: (D, frame). The one entry point every
    reader of the form distance goes through (condition 3, condition 3 on F, the CVT to Lift + Cruise distance, the dispersion check)."""
    fi = gower_inputs(ds, weighting)
    D = _dist.gower_distance(fi.frame, fi.fields, fi.numeric, fi.weights, ranges=fi.ranges, sets=fi.sets)
    return D, fi.frame


def dd_balance_table(ds, v: pd.DataFrame, window_names: List[str], n: int, perms: int, seed: int) -> pd.DataFrame:
    """Condition 2 at the four levels (:func:`lib.dominant_design.balance_band`): C·U then C·W·T share ONE generator seeded
    ``seed`` in that order (the document's order); C and F each run on a fresh generator.

    Ported from: sm_open.py:dd_balance, la_tables.py:dominant_design"""
    w0 = v.dropna(subset=["window"])
    keys = dd_level_keys(ds, v)
    shared = np.random.default_rng(seed)
    parts = {}
    for level in ("A0c", "A1t", "A0", "family_b"):        # the generator runs C·U first, then C·W·T
        k = keys[level].loc[w0.index]
        ww = w0[k.notna()].assign(key=k[k.notna()])
        kw = dict(rng=shared) if level in ("A0c", "A1t") else dict(seed=seed)
        parts[level] = _dd.balance_band(ww["key"], ww["window"], window_names, n=n, perms=perms, **kw)
    out = []
    for level in DD_LEVELS:
        t = parts[level].copy()
        t["top archetype"] = [_key_words(a, level) for a in t["top archetype"]]
        t.insert(0, "level name", DD_LEVEL_WORDS[level])
        t.insert(0, "level", level)
        out.append(t)
    out = pd.concat(out, ignore_index=True)
    out["partial"] = out["window"].astype(str).str.contains("partial")
    return out


def dd_form_table(ds, v: pd.DataFrame, window_names: List[str], perms: int, seed: int) -> pd.DataFrame:
    """Condition 3: Q of the Gower distance per window against the two earliest windows and a permutation band
    (:func:`lib.dominant_design.cohesion_band`), under both weightings (w15 reported, w34 for the record; :data:`Q_WEIGHTINGS`),
    at C, C·U and C·W·T (F is C's row: Q uses no archetype and F only regroups the same aircraft). Fresh generator per (weighting, level).

    Ported from: sm_open.py:dd_form, la_tables.py:dominant_design_q"""
    parts = []
    for weighting in Q_WEIGHTINGS:
        D, frame = form_distance(ds, weighting)
        at = {a: i for i, a in enumerate(frame["aircraft_id"].to_numpy())}
        for level in ("A0", "A1t", "A0c"):                 # order of dominant_design_q(levels=("A0", "A1t", "A0c"))
            key = archetype_key(v, level)
            sub = v[key.notna()].dropna(subset=["window"]).copy()
            sub["row"] = sub["aircraft_id"].map(at)
            sub = sub[sub["row"].notna()]
            t = _dd.cohesion_band(D, sub["row"].astype(int).to_numpy(), sub["window"].to_numpy(), window_names,
                                  perms=perms, seed=seed)
            t.insert(0, "weighting", weighting)
            t.insert(0, "level", level)
            parts.append(t)
    q = pd.concat(parts, ignore_index=True)
    f = q[q["level"].eq("A0")].assign(level="family_b")
    out = pd.concat([q, f], ignore_index=True)
    out.insert(1, "level name", out["level"].map(DD_LEVEL_WORDS))
    out["partial"] = out["window"].astype(str).str.contains("partial")
    order = {lvl: i for i, lvl in enumerate(DD_LEVELS)}
    worder = {w: i for i, w in enumerate(window_names)}
    out = out.sort_values(["weighting", "level", "window"], key=lambda s: s.map(order) if s.name == "level"
                          else (s.map(worder) if s.name == "window" else s))
    return out.reset_index(drop=True)


def _pct1(x: float) -> str:
    return f"{100 * x:.1f} %"


def dd_levels(yearly: pd.DataFrame, balance: pd.DataFrame, form: pd.DataFrame, window_names: List[str]) -> pd.DataFrame:
    """Table 8 (verdict): one row per condition, one column per level, each cell naming where the condition is met: the years for
    condition 1, the windows for conditions 2 and 3 (complete windows only); the last row asks the three in the same period.
    The rules are :func:`lib.dominant_design.condition1_years` and :func:`all_three_windows`.

    Ported from: sm_open.py:dd_levels"""
    complete = [w for w in window_names if "partial" not in w]
    wof = lambda yy: next(w for w, lo, hi in _WIN_BOUNDS if lo <= yy <= hi)      # noqa: E731
    main, alt = Q_WEIGHTINGS
    cells = {}
    for level in DD_LEVELS:
        c, m = {}, {}
        y = yearly[yearly["level id"].eq(level)]
        parts, years_met = [], set()
        for base, _d in DD_BASES:
            b = y[y["base"].eq(base) & y["read"].astype(bool)]
            over = b[b["above 50 %"].astype(bool)]
            yrs = _dd.condition1_years(y[y["base"].eq(base)])
            if yrs:
                ys = sorted(yrs)
                shares = [float(b.loc[b["priority year"].eq(yy), "its share"].iloc[0]) for yy in ys]
                parts.append(f"{base}: met in " + " and ".join(str(x) for x in ys) + " (" + ", ".join(_pct1(s) for s in shares) + ")")
                if base == DD_BASES[0][0]:
                    years_met = set(ys)
            elif len(over):
                sh = dict(zip(b["priority year"].astype(int), b["its share"].astype(float)))
                txt = []
                for yy in over["priority year"].astype(int):
                    nb = [f"{x} ({_pct1(sh[x])})" for x in (yy - 1, yy + 1) if x in sh]
                    txt.append(f"{yy} ({_pct1(sh[yy])})" + (", not " + " or ".join(nb) if nb else ""))
                parts.append(f"{base}: no — above half only in " + "; ".join(txt))
            else:
                top = b.loc[b["its share"].astype(float).idxmax()]
                parts.append(f"{base}: no — at most {_pct1(float(top['its share']))} ({int(top['priority year'])})")
        c["1"], m["1"] = "; ".join(parts), years_met
        bl = balance[balance["level"].eq(level) & balance["window"].isin(complete)]
        below = bl[bl["below band"].astype(str).eq("True")]["window"].tolist()
        c["2"], m["2"] = (("met in " + ", ".join(below)) if below else "no"), set(below)
        fm = form[form["level"].eq(level) & form["window"].isin(complete)]
        hit = fm[fm["weighting"].eq(main) & fm["below band"].astype(str).eq("True")]["window"].tolist()
        hit_alt = fm[fm["weighting"].eq(alt) & fm["below band"].astype(str).eq("True")]["window"].tolist()
        if hit:
            only = [w for w in hit if w not in hit_alt]
            c["3"] = "met in " + ", ".join(hit)
        else:
            c["3"] = "no"
        m["3"] = set(hit)
        inside = _dd.all_three_windows(m["1"], m["2"], m["3"], wof)
        c["all"] = ("met in " + ", ".join(inside)) if inside else "no"
        cells[level] = c
    rows = []
    for cond, label in (("1", "1 — counts: one archetype above 50 % of the aircraft, two consecutive priority years"),
                        ("2", "2 — balance: ²D below the permutation band"),
                        ("3", "3 — form: Q below the two earliest windows by more than the band"),
                        ("all", "all three in the same period")):
        row = {"condition": label}
        for level in DD_LEVELS:
            row[DD_LEVEL_WORDS[level]] = cells[level][cond]
        rows.append(row)
    return pd.DataFrame(rows)


#: set by :func:`dd_levels` callers through :func:`set_window_bounds` (the windows of the yaml)
_WIN_BOUNDS: List[tuple] = []


def set_window_bounds(cfg) -> None:
    """Tell :func:`dd_levels` which years make up each window (the yaml's ``analysis.windows``)."""
    _WIN_BOUNDS[:] = windows_from_config(cfg)


# ---- 3.3 configurations inside each class
CH3B_CLASSES = ["SLC", "TR", "CVT", "TW", "MR"]
_CFG_STATION = {"fuselage": "body", "core_layout": "body", "hull_array": "body", "emp": "tail", "boom": "booms",
                "wing1": "wing 1", "wing2": "wing 2", "wing3": "wing 3"}


def config_frame(ds, v: pd.DataFrame) -> pd.DataFrame:
    """Per unique aircraft the facts the class rules and the driver links are written in: ``sets`` (tilting sets), ``tilt_stations``,
    ``what_tilts``, ``fixed_where``, ``lift_where``, ``stowed``, plus units, propulsor types, units on booms and ducted of the trace frame.

    Ported from: sm_open.py:config_frame"""
    raw = ds.variants
    ovs = override_sets(raw)
    rows = []
    for (_, r), ov in zip(raw.iterrows(), ovs):
        g = lambda c: r[c] if c in r.index else None                         # noqa: E731
        hidden = any(t.startswith("M3:") for t in ov)
        tw = {k for k in range(1, 5) if _s(g(f"wing{k}_tilt")) == "Tilt"}
        bstate = _s(g("boom_thrust_state"))
        boom_tilts = any(_s(g(f"boom{k}_tilts")) == "True" and _s(g(f"boom{k}_hasProps")) != "False" for k in range(1, 7))
        types = []
        for card in _TRACE_CARDS:
            if f"M3:{card}" in ov:
                continue
            nt = _n(g(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                if _n(g(pre + "count")) <= 0 or _s(g(pre + "ctrlOnly")) == "True":
                    continue
                k = _s(g(pre + "propKin"))
                if card == "boom":
                    how = ("wing" if bstate == "on_tilting_wing" else
                           "rotor" if (boom_tilts or k == "Tilt" or bstate == "tilting") else None)
                elif card.startswith("wing") and int(card[-1]) in tw:
                    how = "wing"
                elif card == "emp" and _s(g("empTilts")) == "True":
                    how = "wing"
                else:
                    how = "rotor" if k == "Tilt" else None
                types.append(dict(st=_CFG_STATION.get(card, card), how=how, vertical=_s(g(pre + "orient")) in ("Vertical", "Vert"),
                                  stow=_s(g(pre + "rmech")) in ("Retracting", "BladeFold")))
        rec = bool(types) and not hidden
        hows = {t["how"] for t in types if t["how"]}
        lift = {t["st"] for t in types if t["how"] is None and t["vertical"]}
        fixed = {t["st"] for t in types if t["how"] is None}
        rows.append(dict(
            aircraft_id=r["aircraft_id"], recorded=rec, tilt_stations=len({t["st"] for t in types if t["how"]}),
            what_tilts=("rotors and a wing tilt" if hows == {"rotor", "wing"} else "rotors tilt" if hows == {"rotor"} else
                        "a wing tilts" if hows == {"wing"} else "tilt not recorded"),
            fixed_where=("fixed units on booms" if "booms" in fixed else "fixed units elsewhere" if fixed else "no fixed unit"),
            any_fixed=bool(fixed),
            lift_where=("on booms" if "booms" in lift else "on the wing" if any(s.startswith("wing") for s in lift) else
                        "on the body" if "body" in lift else "elsewhere" if lift else "not recorded"),
            stowed=any(t["stow"] for t in types)))
    f = pd.DataFrame(rows)
    t = trace_frame(ds, v)[["aircraft_id", "joints", "units", "n_types", "on_booms", "ducted"]]
    out = v[["aircraft_id", "topType", "window", "year"]].merge(t, on="aircraft_id", how="left").merge(f, on="aircraft_id", how="left")
    out = out.rename(columns={"joints": "sets"})
    for c in ("sets", "units", "n_types"):
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


#: the two rule sets: class -> (rule as printed, configurations the rule allows; 0 = not defined).
#: Ported from: sm_open.py:CLASS_RULES_BRIEF
CLASS_RULES_BRIEF = {
    "proposed": {
        "SLC": ("where the lift units sit (booms, wing, body) · stowed in cruise or not", 6),
        "TR": ("tilting sets: one · two or more on one station · two or more on two or more stations", 3),
        "CVT": ("what tilts (rotors, a wing, both) · where the fixed units sit (booms, elsewhere, none)", 9),
        "TW": ("wings: one or two or more · propulsive-unit band", 10),
        "MR": ("booms or none · propulsive-unit band", 10)},
    "current": {
        "SLC": ("lift units fixed or retracting/folding · propulsive-unit band", 10),
        "TR": ("tilting types: one or two or more · propulsive-unit band", 10),
        "CVT": ("tilting types × fixed types · propulsive-unit band", 0),
        "TW": ("wings: one or two or more · propulsive-unit band", 10),
        "MR": ("booms or none · propulsive-unit band", 10)}}
#: the earlier rules' key fields. Ported from: la_tables.py:CLASS_CONFIG_RULES
_CUR_FIELDS = {"SLC": ["lift kinematics", "band"], "TR": ["tilting types", "band"], "CVT": ["tilt mix", "band"],
               "TW": ["wings", "band"], "MR": ["booms", "band"]}
#: configurations a rule does not provide for: a gap in the aircraft's propulsion record
_CFG_GAPS = ("no tilting set recorded", "tilt not recorded", "lift units not recorded", "lift units elsewhere")


def cfg_outside(key: str) -> bool:
    """Is this configuration a gap in the record (kept as its own configuration, not counted among the possible)?

    Ported from: sm_open.py:_cfg_outside"""
    return str(key).startswith(_CFG_GAPS)


def _cfg_key_proposed(r: pd.Series, code: str) -> str:
    if code == "SLC":
        where = r["lift_where"]
        key = f"lift units {where}" if where != "not recorded" else "lift units not recorded"
        return key + (", stowed in cruise" if r["stowed"] else "")
    if code == "TR":
        s = r["sets"]
        if pd.isna(s) or s < 1:
            return "no tilting set recorded"
        if s < 2:
            return "one tilting set"
        return ("two or more tilting sets, on two or more stations" if r["tilt_stations"] >= 2
                else "two or more tilting sets, on one station")
    if code == "CVT":
        return f"{r['what_tilts']} · {r['fixed_where']}"
    return ""


def class_config_keys(ds, v: pd.DataFrame, cf: pd.DataFrame, windows: List[str]) -> pd.DataFrame:
    """Long frame: one row per (rule set, aircraft of a drawn class with a complete window) and its configuration under the
    proposed rules and under the earlier ones.

    Ported from: sm_open.py:_class_config_keys"""
    w = v.dropna(subset=["window", "topType"]).copy()
    w = w[w["topType"].isin(CH3B_CLASSES) & w["window"].isin(windows)]
    u = per_aircraft_units(w)
    w["band"] = unit_band(w).astype(str)
    w["lift kinematics"] = np.where(u["retracting units"] > 0, "lift units retract/fold", "lift units fixed")
    w["tilting types"] = np.where(u["tilting types"] >= 2, "2+ tilting types", "1 tilting type")
    w["tilt mix"] = u["tilting types"].astype(int).astype(str) + " tilting × " + u["fixed types"].astype(int).astype(str) + " fixed"
    w["wings"] = np.where(pd.to_numeric(w["wCount"], errors="coerce").fillna(0) >= 2, "2+ wings", "1 wing")
    w["booms"] = np.where(w["nBooms"].fillna(0) > 0, "booms", "no booms")
    w = w.merge(cf.drop(columns=["topType", "window", "year"]), on="aircraft_id", how="left")
    rows = []
    for _, r in w.iterrows():
        code = r["topType"]
        cur = " · ".join(str(r[f]) for f in _CUR_FIELDS[code])
        prop = _cfg_key_proposed(r, code) if code in ("SLC", "TR", "CVT") else cur
        for rs, key in (("proposed", prop), ("current", cur)):
            rows.append({"rule set": rs, "code": code, "window": r["window"], "aircraft_id": r["aircraft_id"], "configuration": key})
    return pd.DataFrame(rows)


def class_configs_brief(keys: pd.DataFrame, windows: List[str], few: List[str], class_names: Dict[str, str],
                        min_cell: int = _drv.MIN_CELL) -> pd.DataFrame:
    """Per rule set, class and complete window: the rule, the aircraft, the configurations the rule allows and those observed,
    those outside the rule, configurations per aircraft, the most common configuration and the share of the class in it
    (blank under ``min_cell`` aircraft).

    Ported from: sm_open.py:class_configs_brief"""
    rows = []
    for rs, rules in CLASS_RULES_BRIEF.items():
        for code in CH3B_CLASSES:
            rule, possible = rules[code]
            sub_c = keys[keys["rule set"].eq(rs) & keys["code"].eq(code)]
            for wn in windows:
                sub = sub_c[sub_c["window"].eq(wn)]
                n = int(len(sub))
                gap = sub["configuration"].map(cfg_outside)
                inside = int(sub.loc[~gap, "configuration"].nunique())
                row = {"rule set": rs, "class": class_names.get(code, code), "code": code, "window": wn, "rule": rule, "aircraft": n,
                       "possible configurations": possible if possible else np.nan, "distinct configurations": inside,
                       "aircraft outside the rule": int(gap.sum()), "configurations per aircraft": np.nan,
                       "most common configuration": "", "aircraft in it": np.nan, "share in it": np.nan, "few aircraft": wn in few}
                if n >= min_cell:
                    vc = sub["configuration"].value_counts()
                    row.update({"configurations per aircraft": round(inside / n, 3), "most common configuration": str(vc.index[0]),
                                "aircraft in it": int(vc.iloc[0]), "share in it": round(float(vc.iloc[0] / n), 3)})
                rows.append(row)
    return pd.DataFrame(rows)


def class_config_mix(keys: pd.DataFrame, class_names: Dict[str, str]) -> pd.DataFrame:
    """The composition behind :func:`class_configs_brief`: per rule set, class, window and configuration, the aircraft and its
    share of the class-window.

    Ported from: sm_open.py:class_config_mix"""
    g = keys.groupby(["rule set", "code", "window", "configuration"]).size().rename("aircraft").reset_index()
    tot = keys.groupby(["rule set", "code", "window"]).size().rename("class aircraft").reset_index()
    g = g.merge(tot, on=["rule set", "code", "window"])
    g["share"] = (g["aircraft"] / g["class aircraft"]).round(3)
    g["class"] = g["code"].map(lambda c: class_names.get(c, c))
    return g[["rule set", "class", "code", "window", "configuration", "aircraft", "class aircraft", "share"]]


def sets_per_unit_brief(cf: pd.DataFrame, windows: List[str], win_short: Dict[str, str], min_cell: int = _drv.MIN_CELL) -> pd.DataFrame:
    """Tilting sets per aircraft and per propulsor unit for Tilt Propulsor, CVT and the five drawn classes pooled: the MEAN per
    complete window and the Spearman test on every year (:func:`lib.drivers.trend_test`), on the aircraft with a unit count.

    Ported from: sm_open.py:sets_per_unit_brief"""
    d = cf[cf["topType"].isin(CH3B_CLASSES) & cf["units"].gt(0)].copy()
    d["per unit"] = d["sets"] / d["units"]
    rows = []
    for code, label in (("TR", "Tilt Rotor"), ("CVT", "Combined vectored thrust"), ("ALL5", "five classes pooled")):
        sub = d if code == "ALL5" else d[d["topType"].eq(code)]
        for measure, col in (("tilting sets per aircraft", "sets"), ("tilting sets per propulsive unit", "per unit")):
            row = {"class": label, "code": code, "measure": measure}
            for wn in windows:
                vals = sub.loc[sub["window"].eq(wn), col].dropna()
                row[win_short.get(wn, wn)] = round(float(vals.mean()), 2) if len(vals) >= min_cell else np.nan
            row.update(_drv.trend_test(sub["year"], pd.to_numeric(sub[col], errors="coerce")))
            rows.append(row)
    return pd.DataFrame(rows)


# ---- 3.1 the directory's dating, 3.2 external comparison
#: the five classes of the evtol.news directory in the order of its coverage table. Ported from: la_tables.py:FOLD5_NAMES
EVN_CLASS_NAMES = [("LC", "Lift + Cruise"), ("VT", "Vectored Thrust"), ("WM", "Wingless (Multicopter)"),
                   ("ER", "Electric Rotorcraft"), ("HB", "Hover Bikes / Personal Flying Devices")]


def evtolnews_coverage(cfg) -> pd.DataFrame:
    """How many directory aircraft carry a development year, per directory class: on the list, agreed by both readers,
    conflict (not ruled), not stated on the page, dated (the agreed ones) and undated, with the dated share.

    Ported from: sm_open.py:evtolnews_coverage"""
    d = pd.read_csv(cfg.path("evtolnews_dev_years"))
    basis = {"agreed": "agreed by both readers", "conflict": "conflict, not yet ruled", "not_stated": "not stated on the page"}
    t = pd.crosstab(d["evtol_class"], d["dev_year_status"]).reindex(index=[c for c, _ in EVN_CLASS_NAMES],
                                                                    columns=list(basis), fill_value=0)
    t.columns = [basis[c] for c in t.columns]
    t.insert(1, "ruled by the author", 0)
    t = t[["agreed by both readers", "ruled by the author", "conflict, not yet ruled", "not stated on the page"]]
    t.index = [n for _, n in EVN_CLASS_NAMES]
    t.loc["all classes"] = t.sum(axis=0)
    t.insert(0, "aircraft on the list", t.sum(axis=1))
    dated = t[["agreed by both readers", "ruled by the author"]].sum(axis=1)
    t["dated (in the panel)"] = dated
    t["undated (left out)"] = t["aircraft on the list"] - dated
    t["dated share"] = (dated / t["aircraft on the list"]).round(3)
    t.index.name = "directory class"
    return t.reset_index()


def ari_f_funding(ds, v: pd.DataFrame, cfg) -> pd.DataFrame:
    """The AAM Reality Index firms that disclose a funding amount (May 2026 release) and file in the corpus: their unique
    aircraft and how many sit in the family F; a ``total`` row carries the plain and the funding-weighted share of F.

    Ported from: sm_open.py:external_tables (la_ext_f_funding) with la_tables.py:ari_firms and sm_open.py:ari_funding"""
    cur, _hist, cmap = ari_load(cfg)
    cmap = cmap[cmap["company_canonical"].ne("")]
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows()}
    cur = cur.assign(company_canonical=cur["oem"].map(_oem_key).map(key_to_canon))
    flags = family_flags(ds, v)
    fam_ids = set(flags.loc[family_mask(flags), "aircraft_id"])
    rows = []
    for canon in sorted(set(cmap["company_canonical"])):
        sub = v[v["company_canonical"].eq(canon)]
        c = cur[cur["company_canonical"].eq(canon)]
        if not len(sub) or not len(c):
            continue
        amt = pd.to_numeric(str(c["funding_musd"].iloc[0]).strip().replace(",", ""), errors="coerce")
        if pd.isna(amt):
            continue
        n_fam = int(sub["aircraft_id"].isin(fam_ids).sum())
        rows.append({"kind": "firm", "company": canon, "funding $M": float(amt), "unique aircraft": int(len(sub)),
                     "aircraft in family F": n_fam, "share in family F": round(n_fam / len(sub), 3)})
    firms = pd.DataFrame(rows).sort_values("funding $M", ascending=False).reset_index(drop=True)
    tot_f, tot_a, tot_m = float(firms["funding $M"].sum()), int(firms["unique aircraft"].sum()), int(firms["aircraft in family F"].sum())
    weighted = float((firms["funding $M"] * firms["share in family F"]).sum() / tot_f)
    total = pd.DataFrame([{"kind": "total", "company": "all firms with disclosed funding", "funding $M": tot_f,
                           "unique aircraft": tot_a, "aircraft in family F": tot_m, "share in family F": round(tot_m / tot_a, 3),
                           "funding-weighted F share": round(weighted, 3)}])
    firms["funding-weighted F share"] = np.nan
    return pd.concat([firms, total], ignore_index=True)


# =====================================================================================================
# Question 4 (the filers): wrangling behind notebook 43
# Joins, filters and counts only; the statistics (effective filers, leverage, chi-square, Fisher, Spearman)
# come from lib/ and are called in the notebook or here as one-line calls.
# =====================================================================================================
from lib import association as _assoc                    # noqa: E402

#: the classes chapter 4 reads one by one; every other class is pooled as "other classes".
#: Ported from: sm_open.py:CH4_CLASSES
CH4_CLASSES = ["SLC", "TR", "CVT", "TW", "MR"]
#: a class is read for concentration with this many aircraft or more / a class x window cell with this many.
#: Ported from: sm_open.py:CH4_CLASS_MIN, CH4_CELL_MIN
CH4_CLASS_MIN, CH4_CELL_MIN = 20, 10
#: a window's two groups are tested when the returning group holds this many aircraft; an origin class is drawn with this many successions.
#: Ported from: sm_open.py:CH4_TEST_MIN, CH4_SUCC_MIN
CH4_TEST_MIN, CH4_SUCC_MIN = 20, 10
#: the firm leverage reads firms with this many aircraft or more, and a window of this many aircraft or more.
#: Ported from: la_tables.py:firm_leverage (min_aircraft=3, the 30 inside)
LEVERAGE_MIN_FIRM, LEVERAGE_MIN_WINDOW = 3, 30


def filer_key(v: pd.DataFrame) -> pd.Series:
    """The identity a filer is counted by: the firm for an organisation, the printed assignee name for an individual
    inventor, blank where no assignee is named (ruling 2026-09-25).

    Ported from: la_tables.py:filer_key"""
    firm = v["firm"]
    person = v["assignee_raw"].map(first_assignee).replace("", np.nan)
    key = firm.where(firm.notna() & firm.astype(str).ne("None"), person)
    return key.where(~v["filer"].eq(NO_ASSIGNEE))


def filer_mix(v: pd.DataFrame) -> pd.DataFrame:
    """Who filed, in both units: primary patents and unique aircraft per filer type, with the distinct filers of each.

    Ported from: la_tables.py:filer_mix"""
    pat = v.drop_duplicates("patent_id")
    names = {"Named company": "Named companies", "University / institute": "Universities and institutes",
             "Individual inventor": "Individual inventors", NO_ASSIGNEE: "No assignee named"}
    key = filer_key(v)
    rows = []
    for k in FILER_TYPES:
        p, a = int(pat["filer"].eq(k).sum()), int(v["filer"].eq(k).sum())
        if not (p or a):
            continue
        n_filers = int(key[v["filer"].eq(k)].dropna().nunique())
        rows.append({"filer": names[k],
                     "distinct filers": (str(n_filers) if k in ("Named company", "University / institute") else f"{n_filers} distinct names"),
                     "primary patents": p, "share per primary patent": round(p / len(pat), 2),
                     "unique aircraft": a, "share of the analysis set": round(a / len(v), 2),
                     "aircraft per patent": round(a / p, 2) if p else np.nan})
    out = pd.DataFrame(rows)
    out.loc[len(out)] = {"filer": "all filers", "distinct filers": f"{int(key.dropna().nunique())} distinct names",
                         "primary patents": int(len(pat)), "share per primary patent": 1.0,
                         "unique aircraft": int(len(v)), "share of the analysis set": 1.0,
                         "aircraft per patent": round(len(v) / len(pat), 2)}
    return out


def filer_mix_representative(ds) -> pd.DataFrame:
    """The filer types counted over the REPRESENTATIVE patents (every patent kept for the analysis, once, including the
    patents that only draw an aircraft already counted on another patent).

    Ported from: sm_open.py:filer_mix_representative"""
    p = ds.patents.loc[ds.patents["is_representative"], ["patent_id"]]
    p = p.merge(design_assignees(ds.identity)[["patent_id", "assignee_chosen"]].drop_duplicates("patent_id"), on="patent_id", how="left")
    ft = p["assignee_chosen"].map(filer_from_assignee)
    names = {"Named company": "Named companies", "University / institute": "Universities and institutes",
             "Individual inventor": "Individual inventors", NO_ASSIGNEE: "No assignee named"}
    rows = [{"filer": names[k], "representative patents": int(ft.eq(k).sum()), "share per representative patent": round(int(ft.eq(k).sum()) / len(p), 3)}
            for k in FILER_TYPES if int(ft.eq(k).sum())]
    rows.append({"filer": "all filers", "representative patents": int(len(p)), "share per representative patent": 1.0})
    return pd.DataFrame(rows)


def coverage_table(v: pd.DataFrame) -> pd.DataFrame:
    """The firm-size ranking cut into four disjoint bands (10 or more, 5-9, 2-4, 1 aircraft each), printed as the document does.
    The numbers come from ``lib.concentration.coverage_segments``.

    Ported from: la_tables.py:coverage_segments (the labels and the rounding)"""
    seg = _conc.coverage_segments(firm_sizes(v), len(v), cuts=(10, 5, 2, 1))
    rows = []
    for _, r in seg.iterrows():
        lo, hi = int(r["lo"]), r["hi"]
        band = f"{lo} or more" if np.isnan(hi) else (f"{lo}" if lo == int(hi) - 1 else f"{lo}-{int(hi) - 1}")
        rows.append({"aircraft per firm": band, "firms": int(r["firms"]), "aircraft": int(r["aircraft"]),
                     "share of the analysis set": round(float(r["share"]), 3),
                     "cumulative firms": int(r["cumulative_firms"]), "cumulative aircraft": int(r["cumulative_aircraft"])})
    return pd.DataFrame(rows)


def filers_by_window(v: pd.DataFrame, window_names: List[str]) -> pd.DataFrame:
    """Named firms active per window: new (their first window), continuing, last seen (no later filing; not judged in the
    last two windows), with the aircraft of named firms and the shares of individual inventors and of universities.

    Ported from: la_tables.py:filers_by_window"""
    w = v.dropna(subset=["window"])
    named = w[w["named"]]
    first = named.groupby("company_canonical")["window"].agg(lambda s: min(s, key=window_names.index))
    last = named.groupby("company_canonical")["window"].agg(lambda s: max(s, key=window_names.index))
    rows = []
    for i, name in enumerate(window_names):
        sub = named[named["window"].eq(name)]
        firms = sub["company_canonical"].unique()
        new = sum(first[f] == name for f in firms)
        gone = sum(last[f] == name for f in firms) if i < len(window_names) - 2 else np.nan
        allw = w[w["window"].eq(name)]
        rows.append({"window": name, "unique aircraft": int(len(allw)), "named firms active": int(len(firms)), "new firms": int(new),
                     "continuing firms": int(len(firms) - new), "firms last seen": (int(gone) if not np.isnan(gone) else ""),
                     "aircraft by named firms": int(len(sub)),
                     "share individual inventors": round(float(allw["filer"].eq("Individual inventor").mean()), 2),
                     "share universities / institutes": round(float(allw["filer"].eq("University / institute").mean()), 2)})
    return pd.DataFrame(rows)


def class_concentration_brief(v: pd.DataFrame, windows: List[str], class_min: int = CH4_CLASS_MIN,
                              cell_min: int = CH4_CELL_MIN) -> pd.DataFrame:
    """Per class of ``class_min`` aircraft or more: its filers, the effective number of filers (``lib.concentration.inverse_hhi``),
    the largest filer over all years, and the largest share one filer holds inside a single complete window of ``windows``
    (cells of ``cell_min`` aircraft or more). A filer is a firm; an individual inventor's patent is its own filer (``filer_id``).
    A window cell's share is rounded to 3 decimals before the largest is chosen, and ties go to the larger cell, as in the document.

    Ported from: sm_open.py:class_concentration_brief with la_tables.py:class_filer_weight and class_window_filer_weight"""
    w = v.dropna(subset=["topType"])
    conc = _conc.class_filer_concentration(w["topType"], w["filer_id"]).set_index("class")
    wn = v.dropna(subset=["topType", "window"])
    cells = []
    for (c, win), sub in wn.groupby(["topType", "window"]):
        if len(sub) < cell_min or win not in windows:
            continue
        t = _conc.top_filer_share(sub["filer_id"])
        cells.append({"code": c, "window": win, "aircraft": t["aircraft"], "largest filer": t["largest_filer"],
                      "its aircraft": t["its_aircraft"], "its share": round(t["its_share"], 3)})
    cells = pd.DataFrame(cells)
    cells["_w"] = cells["window"].map({n: i for i, n in enumerate(windows)})
    cells = cells.sort_values(["aircraft", "_w"], ascending=[False, True]).drop(columns="_w").reset_index(drop=True)
    rows = []
    for c in conc.sort_values("aircraft", ascending=False, kind="stable").index:
        r = conc.loc[c]
        if r["aircraft"] < class_min:
            continue
        top = str(r["largest_filer"])
        row = {"class": cls_name(c), "code": c, "aircraft": int(r["aircraft"]), "filers": int(r["filers"]),
               "effective filers": round(float(r["effective_filers"]), 1),
               "largest filer": "an individual inventor's patent" if top.startswith("patent:") else top,
               "its aircraft": int(r["its_aircraft"]), "its share": round(float(r["its_share"]), 3), "top 3 share": round(float(r["top3_share"]), 3)}
        cc = cells[cells["code"].eq(c)]
        if len(cc):
            t = cc.sort_values(["its share", "aircraft"], ascending=False).iloc[0]
            who = str(t["largest filer"])
            row.update({"largest share inside one window": float(t["its share"]),
                        "held by": "an individual inventor's patent" if who.startswith("patent:") else who,
                        "in window": t["window"], "window aircraft": int(t["aircraft"]), "its aircraft in the window": int(t["its aircraft"])})
        rows.append(row)
    return pd.DataFrame(rows)


def cls_name(code: str) -> str:
    """The class name as the thesis prints it (``style.cls``), without importing the figure style here."""
    from .style import cls
    return cls(code).name


def firm_leverage_table(v: pd.DataFrame, windows: List[str]) -> pd.DataFrame:
    """How much any one firm can move the class reading: for each firm with 3 aircraft or more, the largest class-share move when it
    is dropped (all years, and the largest inside one complete window of 30 aircraft or more). Firms are ranked on ``firm`` and
    dropped on ``company_canonical`` (METHOD_NOTES.md item 4: the two columns are equal here). ``lib.concentration.firm_leverage``.

    Ported from: la_tables.py:firm_leverage"""
    sizes = firm_sizes(v)
    keep = sizes[sizes >= LEVERAGE_MIN_FIRM].index
    lev = _conc.firm_leverage(v["topType"], v["company_canonical"], list(keep), window=v["window"], windows=windows[:-1],
                              min_window_n=LEVERAGE_MIN_WINDOW)
    rows = []
    for _, r in lev.iterrows():
        f = r["firm"]
        own = v[v["company_canonical"].eq(f)]
        rows.append({"firm": f, "unique aircraft": int(sizes[f]), "share of the analysis set": round(float(sizes[f] / len(v)), 3),
                     "class most moved": r["class_moved"], "shift if the firm is dropped (pp)": round(float(r["shift"]) * 100, 2),
                     "largest shift inside one window (pp)": round(float(r["window_shift"]) * 100, 1),
                     "that window": r["window"], "that class": r["window_class"],
                     "modal class": own["topType"].mode().iloc[0] if own["topType"].notna().any() else ""})
    out = pd.DataFrame(rows)
    out["shift magnitude (pp)"] = out["shift if the firm is dropped (pp)"].abs()
    return out.sort_values("shift magnitude (pp)", ascending=False).reset_index(drop=True)


def firm_leverage_classes(v: pd.DataFrame, windows: List[str], top: int = 8, lev: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Every class's share change when one firm is removed, for the ``top`` firms that ``firm_leverage_table`` ranks first: over
    all years and inside each complete window of 30 aircraft or more, in percentage points, signed (+ = the class's share rises when
    the firm is removed). ``lib.concentration.share_shift_when_dropped``.

    Ported from: sm_open.py:firm_leverage_classes"""
    lev = firm_leverage_table(v, windows) if lev is None else lev
    base_all = v["topType"].value_counts(normalize=True)
    rows = []
    for f in lev["firm"].head(top):
        own = v[v["company_canonical"].eq(f)]
        d = _conc.share_shift_when_dropped(v["topType"], v["company_canonical"], f, base_index=base_all.index)
        for c in base_all.index:
            r = {"firm": f, "firm aircraft": int(len(own)), "class": c, "firm aircraft in the class": int(own["topType"].eq(c).sum()),
                 "shift all years (pp)": round(float(d[c]) * 100, 2)}
            for wn in windows[:-1]:
                sub = v[v["window"].eq(wn)]
                col = f"shift {wn} (pp)"
                if len(sub) < LEVERAGE_MIN_WINDOW or not sub["company_canonical"].eq(f).any():
                    r[col] = np.nan
                    continue
                dw = _conc.share_shift_when_dropped(sub["topType"], sub["company_canonical"], f)
                r[col] = round(float(dw.get(c, 0.0)) * 100, 1)
                r[f"window aircraft {wn}"] = int(len(sub))
            rows.append(r)
    return pd.DataFrame(rows)


def ari_funding_frame(v: pd.DataFrame, cfg) -> pd.DataFrame:
    """The AAM Reality Index firms that file in the corpus, with what the index says about their money (disclosed funding, US$ M,
    May 2026 release; 'corporate backed, no amount'; or not in the May 2026 release), their unique aircraft, first patent, first
    flight and the lead from first patent to first flight (flights up to the release year). Sorted by index score, highest first.

    Ported from: sm_open.py:ari_funding with la_tables.py:ari_firms"""
    cur, hist, cmap = ari_load(cfg)
    cmap = cmap[cmap["company_canonical"].ne("")]
    key_to_canon = {_oem_key(r["oem"]): r["company_canonical"] for _, r in cmap.iterrows()}
    cur = cur.assign(key=cur["oem"].map(_oem_key))
    cur["company_canonical"] = cur["key"].map(key_to_canon)
    hist = hist.assign(key=hist["oem"].map(_oem_key))
    hist["company_canonical"] = hist["key"].map(key_to_canon)
    dates = [c for c in hist.columns if c not in ("oem", "key", "company_canonical")]
    sizes = firm_sizes(v)
    tl = ari_timeline(v, cfg).set_index("company")
    rows = []
    for canon in sorted(set(cmap["company_canonical"])):
        if int(sizes.get(canon, 0)) == 0:
            continue
        c, h = cur[cur["company_canonical"].eq(canon)], hist[hist["company_canonical"].eq(canon)]
        score = last = None
        funding = ""
        if len(c):
            score, last, funding = float(c["ari"].iloc[0]), "May 2026", c["funding_musd"].iloc[0]
        elif len(h):
            s = h[dates].apply(pd.to_numeric, errors="coerce").iloc[0].dropna()
            if len(s):
                score, last = float(s.iloc[-1]), s.index[-1]
        sub = v[v["company_canonical"].eq(canon)]
        raw = str(funding if funding not in (None, "") else "").strip()
        amt = pd.to_numeric(raw.replace(",", ""), errors="coerce")
        status = ("disclosed" if pd.notna(amt) else "corporate backed, no amount" if raw.lower().startswith("corporate")
                  else "not in the May 2026 release")
        ff = pd.to_numeric(tl["first flight (ARI)"].get(canon) if canon in tl.index else None, errors="coerce")
        flown = bool(pd.notna(ff) and ff <= ARI_RELEASE_YEAR)
        fp = int(sub["year"].min()) if sub["year"].notna().any() else np.nan
        rows.append({"company": canon, "ARI score": score, "release": last, "funding $M": float(amt) if pd.notna(amt) else np.nan,
                     "funding status": status, "unique aircraft": int(sizes[canon]), "first patent": fp,
                     "first flight": float(ff) if pd.notna(ff) else np.nan, "first flight flown": flown,
                     "years first patent to first flight": float(ff - fp) if flown and pd.notna(fp) else np.nan})
    return pd.DataFrame(rows).sort_values("ARI score", ascending=False).reset_index(drop=True)


def ari_funding_tests(fr: pd.DataFrame) -> pd.DataFrame:
    """Spearman rho (``lib.association.spearman_rho_p``) of disclosed funding against three patent-side quantities, on the index firms
    with a disclosed amount (the lead only on those whose first flight has happened). rho to 2 decimals, p to 3, as the document prints.

    Ported from: sm_open.py:ari_funding_tests"""
    d = fr[fr["funding $M"].notna()]
    rows = []
    for col, label in (("unique aircraft", "unique aircraft in the corpus"), ("first patent", "priority year of the first patent"),
                       ("years first patent to first flight", "years from first patent to first flight")):
        s = d[["funding $M", col]].dropna()
        rho, p = _assoc.spearman_rho_p(s["funding $M"], s[col], min_n=3)
        rows.append({"against": label, "column": col, "firms": int(len(s)), "rho": round(rho, 2), "p": round(p, 3)})
    return pd.DataFrame(rows)


def named_entries(v: pd.DataFrame, window_names: List[str]) -> pd.DataFrame:
    """The aircraft of named organisations with a window, each flagged first-time (the firm's earliest window in the corpus is this
    window) or returning, and its class folded to the five read one by one plus 'other' (column ``_c``).

    Ported from: sm_open.py:_named_frame"""
    w = v[v["named"]].dropna(subset=["window", "year"]).copy()
    first = w.groupby("firm")["window"].agg(lambda s: min(s, key=window_names.index))
    w["first_time"] = w["firm"].map(first).eq(w["window"])
    w["_c"] = w["topType"].map(lambda c: c if c in CH4_CLASSES else "other")
    return w


def entry_split(w: pd.DataFrame, complete: List[str], names: Dict[str, str]) -> pd.DataFrame:
    """Per complete window, the class mix of the named organisations' aircraft in two groups: first-time and returning filers
    (columns in ``names``: code -> printed class name, 'other' -> 'other classes'). Unit: the unique aircraft.

    Ported from: sm_open.py:entry_split"""
    rows = []
    for wn in complete:
        sub = w[w["window"].eq(wn)]
        for grp, mask in (("first-time filers", sub["first_time"]), ("returning filers", ~sub["first_time"])):
            g = sub[mask]
            row = {"window": wn, "group": grp, "aircraft": int(len(g)), "firms": int(g["firm"].nunique())}
            for c in CH4_CLASSES + ["other"]:
                row[names[c]] = round(float(g["_c"].eq(c).mean()), 3) if len(g) else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def entry_split_test(w: pd.DataFrame, complete: List[str]) -> pd.DataFrame:
    """Per complete window whose returning group holds ``CH4_TEST_MIN`` aircraft or more: the chi-square p (``lib.association.chi2_p_of_crosstab``)
    of class against first-time / returning, and again without the returning firm that holds most of the window's returning aircraft
    (a test added after the first result was seen).

    Ported from: sm_open.py:entry_split_test"""
    rows = []
    for wn in complete:
        sub = w[w["window"].eq(wn)]
        ret = sub[~sub["first_time"]]
        row = {"window": wn, "first-time aircraft": int(sub["first_time"].sum()), "returning aircraft": int(len(ret)),
               "returning firms": int(ret["firm"].nunique())}
        if len(ret) >= CH4_TEST_MIN:
            big = ret["firm"].value_counts()
            rest = sub[sub["firm"].ne(big.index[0])]
            row.update({"p": _assoc.chi2_p_of_crosstab(sub["_c"], sub["first_time"]), "largest returning firm": big.index[0],
                        "its aircraft": int(big.iloc[0]), "p without it": _assoc.chi2_p_of_crosstab(rest["_c"], rest["first_time"])})
        rows.append(row)
    return pd.DataFrame(rows)


def tw_entry(v: pd.DataFrame, complete: List[str]) -> pd.DataFrame:
    """Per complete window: the named firms entering (their first aircraft falls in it), those whose first aircraft is a Tilt Wing, what kind
    of entrant they are (university / institute; no other aircraft), and Tilt Wing's share of the window's aircraft; the change of that
    aircraft share from the window before is tested with Fisher's exact test (``lib.association.fisher_exact_p``).

    The first aircraft of a firm is the first row after a sort on priority year (``groupby().first()``, as the document does).

    Ported from: sm_open.py:tw_entry"""
    w = v[v["named"]].dropna(subset=["window", "year"]).sort_values("year")
    first = w.groupby("company_canonical").first()
    first = first.assign(n_aircraft=firm_sizes(v).reindex(first.index).fillna(0).astype(int).to_numpy())
    rows = []
    for wn in complete:
        ent = first[first["window"].eq(wn)]
        tw = ent[ent["topType"].eq("TW")]
        allw = v[v["window"].eq(wn)]
        rows.append({"window": wn, "firms entering": int(len(ent)), "entering with Tilt Wing": int(len(tw)),
                     "Tilt Wing share of entrants": round(len(tw) / len(ent), 3) if len(ent) else np.nan,
                     "Tilt Wing entrants: universities / institutes": int(tw["filer"].eq("University / institute").sum()),
                     "Tilt Wing entrants: no other aircraft": int(tw["n_aircraft"].eq(1).sum()),
                     "all entrants: universities / institutes": int(ent["filer"].eq("University / institute").sum()),
                     "all entrants: no other aircraft": int(ent["n_aircraft"].eq(1).sum()),
                     "aircraft in the window": int(len(allw)), "Tilt Wing aircraft": int(allw["topType"].eq("TW").sum()),
                     "Tilt Wing share of the aircraft": round(float(allw["topType"].eq("TW").mean()), 3) if len(allw) else np.nan})
    out = pd.DataFrame(rows)
    ps = [np.nan]
    for i in range(1, len(out)):
        a, b = out.iloc[i - 1], out.iloc[i]
        ps.append(round(_assoc.fisher_exact_p([[int(a["Tilt Wing aircraft"]), int(a["aircraft in the window"] - a["Tilt Wing aircraft"])],
                                               [int(b["Tilt Wing aircraft"]), int(b["aircraft in the window"] - b["Tilt Wing aircraft"])]]), 3))
    out["Tilt Wing share, Fisher p against the window before"] = ps
    return out


def succession_pairs(v: pd.DataFrame) -> pd.DataFrame:
    """Every consecutive pair of a named firm's aircraft in priority order (aircraft of one year in the order of the labelled dataset,
    which is arbitrary): one row per succession, with the firm and the class of origin and of destination.

    Ported from: sm_open.py:_succession_pairs"""
    w = (v[v["named"] & v["topType"].notna()].dropna(subset=["year"]).sort_values(["company_canonical", "year", "aircraft_id"]))
    pairs = []
    for f, sub in w.groupby("company_canonical"):
        t = sub["topType"].tolist()
        pairs += [{"firm": f, "from": a, "to": b} for a, b in zip(t[:-1], t[1:])]
    return pd.DataFrame(pairs)


def succession_matrix(pairs: pd.DataFrame) -> pd.DataFrame:
    """Where a firm's next aircraft lands, by the class of the one before: one row per class of origin with ``CH4_SUCC_MIN`` successions or
    more, the share of each destination (a row sums to 1), and the share that stays once the firm with the most successions is left out.

    Ported from: sm_open.py:succession_matrix"""
    top_firm = pairs["firm"].value_counts().index[0]
    q = pairs[pairs["firm"].ne(top_firm)]
    dests = CH4_CLASSES + ["PTC"]
    rows = []
    for code, sub in pairs.groupby("from"):
        if len(sub) < CH4_SUCC_MIN:
            continue
        qs = q[q["from"].eq(code)]
        row = {"class of origin": cls_name(code), "code": code, "successions": int(len(sub)), "firms": int(sub["firm"].nunique()),
               "stays in the class": round(float(sub["to"].eq(code).mean()), 3)}
        for d in dests:
            row[f"→ {d}"] = round(float(sub["to"].eq(d).mean()), 3)
        row["→ other"] = round(float((~sub["to"].isin(dests)).mean()), 3)
        row.update({"firm left out": top_firm, "its successions, all classes": int(pairs["firm"].eq(top_firm).sum()),
                    "successions, all classes": int(len(pairs)), "firms with a succession": int(pairs["firm"].nunique()),
                    "successions without it": int(len(qs)), "stays without it": round(float(qs["to"].eq(code).mean()), 3) if len(qs) else np.nan})
        rows.append(row)
    return pd.DataFrame(rows).sort_values("successions", ascending=False).reset_index(drop=True)


# =====================================================================================================
# Question 5 (the regions): wrangling behind notebook 44
# Only joins, filters and counts; the statistics (chi-square, Spearman, bootstrap offsets, permutation tests, Jaffe proximity)
# come from lib/ (association, regional, distance).
# =====================================================================================================
from lib import regional as _reg                          # noqa: E402

#: the regional mix is read FROM 2012: the windows 2012-15, 2016-19 and 2020-23, and a trend over 2012-2023 (author's ruling 2026-09-27).
#: Ported from: sm_open.py:CH5_WINS, CH5_TREND
CH5_WINS = ["2012-15", "2016-19", "2020-23"]
CH5_TREND = (2012, 2023)
#: the answers the regional figure draws, per variable: (column of the regional frame, answers).
#: Ported from: sm_open.py:CH5_VARS (the columns are those of :func:`regional_frame`)
CH5_VARS = {"class": ("cls5", ["SLC", "TR", "CVT", "TW", "MR", "other"]),
            "propulsive units": ("rb", ["1-3", "4", "5-6", "7-8", "9+"]),
            "tilting unit": ("tilt", [True, False])}
#: the document's names of the classes of chapter 5 (Tilt Rotor is printed Tilt Propulsor since 2026-09-28).
#: Ported from: sm_open.py:CH5_CLASS_WORD
CH5_CLASS_WORD = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT", "TW": "Tilt Wing", "MR": "Multirotor", "other": "other classes"}
#: a region-window cell under this many aircraft is left blank. Ported from: sm_figures.py:CH5_THIN
CH5_THIN = 10
#: firms with this many aircraft carry a class profile (proximity of 5.3). Ported from: la_tables.py:FIRM_MIN
FIRM_MIN = 5
#: the class names the lag tables print (the document's). Ported from: metrics.py:ARCH_NAMES
LAG_CLASS_NAMES = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "Combined vectored thrust", "TW": "Tilt Wing", "MR": "Multirotor",
                   "TB": "Tilt Body", "PTC": "Pitch-to-Cruise", "HB": "Hoverbike", "PFV": "Personal Flying Vehicle", "RC": "Rotorcraft",
                   "SRW": "Stopped/Slowed Rotor Wing", "DS": "Deflected Slipstream"}
#: ISO 3166-1 alpha-2 codes written out. Ported from: la_figures.py:COUNTRY_NAMES
COUNTRY_NAMES = {
    "AT": "Austria", "AU": "Australia", "BR": "Brazil", "CA": "Canada", "CH": "Switzerland", "CN": "China", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "DZ": "Algeria", "ES": "Spain", "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece", "HR": "Croatia",
    "IL": "Israel", "IN": "India", "IR": "Iran", "IT": "Italy", "JP": "Japan", "KR": "South Korea", "LT": "Lithuania", "MY": "Malaysia",
    "NL": "Netherlands", "NO": "Norway", "PH": "Philippines", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "RU": "Russia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Türkiye", "TW": "Taiwan", "UA": "Ukraine", "US": "United States", "VN": "Vietnam", "ZA": "South Africa"}


def country_name(code) -> str:
    """'United States (US)'; 'not recorded' for an empty code. Ported from: la_figures.py:_country_name"""
    c = "" if code is None or (isinstance(code, float) and np.isnan(code)) else str(code).strip()
    if not c or c in ("?", "nan"):
        return "not recorded"
    return f"{COUNTRY_NAMES[c]} ({c})" if c in COUNTRY_NAMES else c


def regional_frame(ds, v: pd.DataFrame) -> pd.DataFrame:
    """The aircraft of the three regions with their class folded to the five read one by one plus 'other' (``cls5``), the propulsor-unit band
    (``rb``), whether any propulsor tilts (``tilt``) and whether the aircraft belongs to the family F of chapter 3 (``F``, NaN without a class).

    Ported from: sm_open.py:_ch5_frame"""
    keys = dd_level_keys(ds, v)["family_b"]
    w = v.assign(F=keys.eq(FAMILY_LABEL).where(keys.notna()))
    w = w[w["region3"].isin(REGIONS)].copy()
    w["cls5"] = w["topType"].where(w["topType"].isin(CH5_VARS["class"][1][:-1]), "other")
    w.loc[w["topType"].isna(), "cls5"] = np.nan
    w["rb"] = w["rotorBin"].where(w["rotorBin"].isin(CH5_VARS["propulsive units"][1]))
    w["tilt"] = w["any_tilting"].map({True: True, False: False})
    return w


def region_countries(ds, v: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """The applicant countries behind the three regions: per country (the first assignee's) its region, the patents acquired from it, the representative
    patents and the unique aircraft; the ``top`` countries by representative patents, then one row for all the others.

    Ported from: sm_open.py:region_countries"""
    j = ds.patents.merge(ds.identity[["patent_id", "region", "assignee_country"]], on="patent_id", how="left")
    j["rep"] = j["is_representative"].fillna(False).astype(bool)
    j["assignee_country"] = j["assignee_country"].fillna("not recorded")
    g = j.groupby("assignee_country").agg(region=("region", lambda x: x.mode().iloc[0] if x.notna().any() else ""),
                                          patents=("patent_id", "size"), representative=("rep", "sum"))
    air = v["assignee_country"].fillna("not recorded").value_counts()
    g["unique aircraft"] = air.reindex(g.index).fillna(0).astype(int)
    g = g.sort_values(["representative", "patents"], ascending=False)
    head = g.drop(index="not recorded", errors="ignore").head(top)
    rest = g.drop(index=head.index)
    out = head.reset_index().rename(columns={"assignee_country": "country", "patents": "patents acquired", "representative": "representative patents"})
    out["region"] = out["region"].where(out["region"].isin(REGIONS), "Other regions")
    out = pd.concat([out, pd.DataFrame([{"country": "other or not recorded", "region": "", "patents acquired": int(rest["patents"].sum()),
                                         "representative patents": int(rest["representative"].sum()), "unique aircraft": int(rest["unique aircraft"].sum())}])],
                    ignore_index=True)
    tot_r = int(g["representative"].sum())
    out["share of representative patents"] = (out["representative patents"] / tot_r).round(3)
    out["share of unique aircraft"] = (out["unique aircraft"] / len(v)).round(3)
    return out


def region_mix_change(w: pd.DataFrame) -> pd.DataFrame:
    """Per region, variable and answer: aircraft and share in 2012-15, 2016-19 and 2020-23, and the trend over 2012-2023, the Spearman rho of
    the answer (1/0) against each aircraft's own priority year (``lib.association.spearman_rho_p``, undefined when the answer never changes) and
    its p. The share is taken over the region-window's aircraft whose field is recorded. ``w`` = :func:`regional_frame`.

    Ported from: sm_open.py:region_mix_change"""
    lo, hi = CH5_TREND
    rows = []
    for reg in REGIONS:
        for var, (col, cats) in list(CH5_VARS.items()) + [("family F", ("F", [True]))]:
            s = w[w["region3"].eq(reg) & w[col].notna()]
            tr = s[s["year"].between(lo, hi)]
            for c in cats:
                row = {"region": reg, "variable": var, "answer": str(c),
                       "label": CH5_CLASS_WORD.get(c, "yes" if c is True else "no" if c is False else c)}
                for wn in CH5_WINS:
                    x = s[s["window"].eq(wn)]
                    k = int(x[col].eq(c).sum())
                    row[f"aircraft {wn}"], row[f"base {wn}"] = k, int(len(x))
                    row[f"share {wn}"] = round(k / len(x), 4) if len(x) else np.nan
                rho, p = _assoc.spearman_rho_p(tr["year"], tr[col].eq(c).astype(int), require_variation=True)
                row["aircraft 2012-23"] = int(len(tr))
                row["rho"] = round(rho, 3) if np.isfinite(rho) else np.nan
                row["p"] = round(p, 4) if np.isfinite(p) else np.nan
                rows.append(row)
    return pd.DataFrame(rows)


def region_window_mix(w: pd.DataFrame, window_names: List[str]) -> pd.DataFrame:
    """The bars of the regional figure as numbers: per region, variable, answer and window, the aircraft and the share of the region-window's
    aircraft whose field is recorded.

    Ported from: sm_open.py:region_window_mix"""
    rows = []
    for reg in REGIONS:
        for var, (col, cats) in CH5_VARS.items():
            s = w[w["region3"].eq(reg) & w[col].notna()]
            for wn in window_names:
                c = s[s["window"].eq(wn)]
                for a in cats:
                    k = int(c[col].eq(a).sum())
                    rows.append({"region": reg, "variable": var, "answer": str(a), "window": wn, "aircraft": k, "base": int(len(c)),
                                 "share": round(k / len(c), 4) if len(c) else np.nan})
    return pd.DataFrame(rows)


def region_tests(w: pd.DataFrame) -> pd.DataFrame:
    """Do the three regions differ? One chi-square of region against each measure (``lib.association.chi2_p_of_columns``), over all years and in
    each window from 2012, with all filers and again without the largest filer of North America (Bell / Textron). Base: the aircraft whose field
    is recorded. ``w`` = :func:`regional_frame`; the firm left out is kept in ``attrs['left_out']``.

    Ported from: sm_open.py:region_tests"""
    w = w.copy()
    big = w[w["region3"].eq("North America")]["firm"].value_counts().index[0]
    w["tr"] = w["topType"].eq("TR").where(w["topType"].notna())
    rows = []
    for name, col in [("class mix (five classes + other)", "cls5"), ("propulsive-unit band", "rb"), ("any tilting unit", "tilt"),
                      ("Tilt Rotor", "tr"), ("family F", "F")]:
        for per in ["all years"] + CH5_WINS:
            s = w if per == "all years" else w[w["window"].eq(per)]
            for who, sub in (("all filers", s), (f"without {big}", s[s["firm"].ne(big)])):
                p, n = _assoc.chi2_p_of_columns(sub, "region3", col)
                rows.append({"measure": name, "period": per, "filers": who, "aircraft": n, "p (chi-square, region)": round(p, 4)})
    out = pd.DataFrame(rows)
    out.attrs["left_out"] = big
    return out


def region_lean(w: pd.DataFrame) -> pd.DataFrame:
    """Per region, all years: its aircraft, its largest filer, the share with a tilting propulsor and the Tilt Rotor share (both also without the
    region's largest filer) and the family-F share per window from 2012.

    Ported from: sm_open.py:region_lean"""
    rows = []
    for reg in REGIONS:
        s = w[w["region3"].eq(reg)]
        big = s["firm"].value_counts()
        firm, fn = str(big.index[0]), int(big.iloc[0])
        wo = s[s["firm"].ne(firm)]
        t, t2 = s["tilt"].dropna(), wo["tilt"].dropna()
        tt, tt2 = s[s["topType"].notna()], wo[wo["topType"].notna()]
        row = {"region": reg, "aircraft": int(len(s)), "largest filer": firm, "its aircraft": fn,
               "its Tilt Rotor aircraft": int(s[s["firm"].eq(firm)]["topType"].eq("TR").sum()),
               "Tilt Rotor aircraft": int(tt["topType"].eq("TR").sum()),
               "its tilting aircraft": int(s[s["firm"].eq(firm)]["tilt"].eq(True).sum()), "tilting aircraft": int(t.eq(True).sum()),
               "tilting share": round(float(t.mean()), 4), "tilting share without it": round(float(t2.mean()), 4),
               "Tilt Rotor share": round(float(tt["topType"].eq("TR").mean()), 4),
               "Tilt Rotor share without it": round(float(tt2["topType"].eq("TR").mean()), 4)}
        for per in CH5_WINS:
            f = s[s["window"].eq(per)]["F"].dropna()
            row[f"F aircraft {per}"], row[f"F base {per}"] = int(f.sum()), int(len(f))
            row[f"F share {per}"] = round(float(f.mean()), 4) if len(f) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def with_publication(ds, v: pd.DataFrame) -> pd.DataFrame:
    """``v`` with the publication year of each aircraft's patent (column ``pub_year``) and the lag ``lag`` = publication year minus priority year.

    Ported from: sm_open.py:region_lag (the merge)"""
    j = v.merge(ds.identity[["patent_id", "pub_year"]], on="patent_id", how="left", suffixes=("", "_pub"))
    j["pub_year"] = pd.to_numeric(j["pub_year_pub"] if "pub_year_pub" in j else j["pub_year"], errors="coerce")
    return j.assign(lag=j["pub_year"] - j["year"])


def region_years(ds, v: pd.DataFrame, first: int = 2012) -> pd.DataFrame:
    """Aircraft per priority year and region, each region's share of the three regions' aircraft of that year, the part of them the snapshot
    already sees (``lib.growth.visible_share`` on the region's own publication lags of 2016-21) and the share corrected for publication lag
    (each count divided by that visibility, the shares recomputed).

    Ported from: sm_open.py:region_years"""
    snap = pd.to_datetime(ds.identity["snapshot_date"].dropna().iloc[0])
    S, frac = int(snap.year), float(snap.dayofyear / 365.0)
    j = with_publication(ds, v)
    j = j[j["region3"].isin(REGIONS)]
    ref = j[j["year"].between(2016, 2021)]
    lagd = {r: ref.loc[ref["region3"].eq(r), "lag"].dropna().to_numpy() for r in REGIONS}
    rows = []
    for y in range(first, S + 1):
        s = j[j["year"].eq(y)]
        n = {r: int(s["region3"].eq(r).sum()) for r in REGIONS}
        tot = sum(n.values())
        vv = {r: _growth.visible_share(lagd[r], S - y, frac) for r in REGIONS}
        corr = {r: (n[r] / vv[r] if vv[r] and vv[r] > 0 else np.nan) for r in REGIONS}
        ctot = np.nansum(list(corr.values()))
        for r in REGIONS:
            rows.append({"priority year": y, "region": r, "aircraft": n[r], "share of the year": round(n[r] / tot, 4) if tot else np.nan,
                         "visible at the snapshot": round(vv[r], 3),
                         "share corrected for publication lag": round(corr[r] / ctot, 4) if ctot and np.isfinite(corr[r]) else np.nan,
                         "complete": bool(y <= _reg.LAST_COMPLETE)})
    return pd.DataFrame(rows)


def firm_class_profiles(v: pd.DataFrame, min_aircraft: int = FIRM_MIN) -> pd.DataFrame:
    """Firm x class counts of unique aircraft with a class, for the named firms (the grouper's canonical company, the two catch-all buckets
    are not firms) with ``min_aircraft`` or more. An aircraft with no class (two of Shenfeng Aviation) is not counted, as in the archive.

    Ported from: a2.py:firm_profiles (by='class')"""
    w = v[v["company_canonical_grouper"].notna() & ~v["company_canonical_grouper"].isin(CATCH_ALL) & v["topType"].notna()]
    tab = pd.crosstab(w["company_canonical_grouper"], w["topType"].astype(str))
    return tab[tab.sum(axis=1) >= min_aircraft]


def firm_region_of(v: pd.DataFrame) -> pd.Series:
    """Modal applicant region of each named firm's aircraft.

    Ported from: la_tables.py:firm_region"""
    w = v[v["named"]]
    return w.groupby("company_canonical_grouper")["region3"].agg(lambda s: s.value_counts().index[0])


def region_firm_proximity(v: pd.DataFrame, min_aircraft: int = FIRM_MIN):
    """The Jaffe proximity of the firms' class profiles (``lib.distance.jaffe_proximity``) with the firms grouped by region: region blocks in the
    order of REGIONS, inside a block the clustered order of ``lib.distance.proximity_order``. Returns (matrix in that order, region of each firm
    in that order). The order fixes the random stream of the permutation test of ``lib.regional.region_proximity_test``.

    Ported from: la_tables.py:proximity_by_region (ordering)"""
    prox = _dist.jaffe_proximity(firm_class_profiles(v, min_aircraft))
    clustered = _dist.proximity_order(prox)
    reg = firm_region_of(v).reindex(clustered)
    blocks = REGIONS + sorted({str(r) for r in reg if r not in REGIONS})
    order = [f for b in blocks for f in clustered if reg[f] == b]
    return prox.loc[order, order], reg.reindex(order)


# ------------------------------------------------------------------ Question 1, 1.3.5: dataset against the directory
#: directory status → group (the page's list status, else its spec-sheet status)
DIRECTORY_FLYING = ("prototype", "technology demonstrator", "production model", "production aircraft",
                    "subscale prototype", "proof of concept")


#: regexes of the 2026-10-11 cargo / drone test (aircraft type, page name) and of a capacity that names a person
DIRECTORY_CARGO_TYPE = r"cargo|drone|unmanned|uncrewed|uav|delivery|logistic|freight|agricultur|spray|surveillance|inspection"
DIRECTORY_CARGO_NAME = r"cargo|drone|uav|freight|logistic|delivery|agri|spray"
DIRECTORY_PEOPLE = r"passenger|pilot|person|people|seat|occupant|patient|human"


#: a sentence of the page's own text saying THIS aircraft can be crewed / piloted ("crewed and uncrewed", "piloted or remotely
#: piloted", "optionally piloted", "can be flown by a pilot"); negations ("no pilot or passengers", "autopilot or remote") and
#: sector-wide statements ("low-altitude economy") do not count
DIRECTORY_CREWED = (r"(?<!un)crewed (?:and|or) |(?<!un)manned (?:and|or) |(?<!auto)(?<!no )(?<!remotely )(?<!remote )piloted or (?:remote|un|autonom)|"
                    r"(?<!auto)(?<!no )pilot(?:ed)? (?:or|and/or) (?:remote|pilotless)|optionally[- ]piloted|"
                    r"can (?:also )?be (?:flown|piloted|operated) (?:by|with|as) (?:a |an |one |1 )?(?:pilot|crew|person|human)")


def directory_crewed_pages(cfg) -> dict:
    """slug_key -> True when a non-Resources sentence of the crawled evtol.news page matches DIRECTORY_CREWED."""
    import json
    import re
    rx = re.compile(DIRECTORY_CREWED, re.I)
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    resources = {k: " ".join(g.loc[g["is_resource"].eq("True"), "sentence"]) for k, g in ev.groupby("slug_key")}
    out = {}
    for line in open(cfg.path("evtolnews_aircraft").parent / "pages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        res = resources.get(r["slug_key"], "")
        out[r["slug_key"]] = any(rx.search(s) and "low-altitude economy" not in s and s.strip()[:60] not in res
                                 for s in re.split(r"(?<=[.!?])\s+|\n+", r["text"]))
    return out


#: sentence says the aircraft (or its maker's product line) is built for people: passengers, air taxi, seats, optionally piloted,
#: cabin / cockpit. Negations ("no passengers", "carries no passengers", "no pilot") do not count. Used only to rescue the
#: WEAK exclusions ("no passengers" capacity, uncrewed type): a demonstrator that flew empty is still a passenger design.
DIRECTORY_PAXDESIGN = (r"(?<!no )(?<!without )(?<!carries no )(?<!carry no )(?<!carrying no )\bpassengers?\b(?! (?:or cargo|aircraft only))|air[- ]taxi|"
                       r"personal air ?(?:vehicle|craft)|\b(?:one|two|three|four|five|six|1|2|3|4|5|6)[- ]?(?:seat|seater|person)\b|crash rated seat|"
                       r"optionally[- ]piloted|pilot[- ]optional|\bcabin\b|\bcockpit\b|(?<!un)(?<!auto)(?<!remotely )(?<!remote )(?<!no )\bpiloted (?:eVTOL|electric|all-electric|hybrid|aircraft|VTOL)")


DIRECTORY_PAXNOT = __import__("re").compile(r"low-altitude economy|original plan|decided that|instead|NASA has continued|no plans|might include|registered as a drone|passenger compartment has|\bairlines?\b|Korean Air services|grocery", __import__("re").I)


def directory_paxdesign_pages(cfg) -> dict:
    """slug_key -> True when a non-Resources sentence of the crawled page matches DIRECTORY_PAXDESIGN."""
    import json
    import re
    rx = re.compile(DIRECTORY_PAXDESIGN, re.I)
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    resources = {k: " ".join(g.loc[g["is_resource"].eq("True"), "sentence"]) for k, g in ev.groupby("slug_key")}
    out = {}
    for line in open(cfg.path("evtolnews_aircraft").parent / "pages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        res = resources.get(r["slug_key"], "")
        out[r["slug_key"]] = any(rx.search(x) and not DIRECTORY_PAXNOT.search(x) and x.strip()[:60] not in res
                                 for x in re.split(r"(?<=[.!?])\s+|\n+", r["text"]))
    return out


def directory_frame(cfg, use_overrides: bool = True) -> pd.DataFrame:
    """One row per evtol.news aircraft page (1 229) with what can explain a different class mix.

    Columns: ``slug_key``, ``class5`` (the directory's own class), ``status`` (list status, else page status),
    ``status_group`` (concept design / flying hardware / defunct / not stated), ``not_combustion`` (power source
    does not name ONLY a combustion, hybrid or fuel-cell source; blank counts as not combustion), ``crewed``
    (not cargo-only, not 'no passengers', not listed as a cargo drone, and not unmanned with no capacity
    stated), ``in_domain`` (both), ``patented`` (the page is linked to a patented aircraft of the labelled
    dataset in patent_links.csv, use = yes).

    The unit is the directory PAGE: a model or a version of it (e.g. four CityAirbus pages), not an aircraft
    family. The two filters approximate the labelled dataset's domain gate (electric, not UAV) from the
    directory's free-text spec fields; they are a check, not a ruling.
    New 2026-10-02."""
    d = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False)
    status = d["list_status"].where(d["list_status"].ne(""), d["status"]).str.lower()
    group = np.select([status.eq("concept design"), status.isin(DIRECTORY_FLYING), status.eq("defunct"),
                       status.eq("")], ["concept design", "flying hardware", "defunct", "not stated"], "other")
    power = d["spec_power_source"].str.lower()
    # 2026-10-11 ruling: a power source that offers an electric version ("hybrid-electric", "or all-electric") counts as
    # electric (as the 2026-09-13 ruling); only a source naming no battery and no electric option is combustion-only
    # 2026-10-11 ruling: "hybrid-electric" is NOT an electric option (it carries a combustion engine or fuel cell); an electric option is
    # a battery or an all-electric alternative. Fuel cells / engine "and" / "plus" batteries with no "or" is one hybrid system, not a choice.
    power_nohy = power.str.replace(r"hybrid[- ]?electric|hybrid", "", regex=True)
    electric_option = power_nohy.str.contains("batter|electric")
    one_system = power.str.contains(r"fuel cell|engine|turbine|hydrogen") & power.str.contains(r"\band\b|\bplus\b|\+") & ~power.str.contains(r"\bor\b|,")
    combustion_only = power.str.contains("hybrid|fuel cell|turbine|engine|gas|hydrogen") & (~electric_option | one_system)
    cap = d["spec_capacity"].str.lower()
    # 2026-10-11 ruling: only truly unmanned pages are UAVs; autonomous / remote pages are taken as piloted first
    # ... unless the same capacity text says it CAN hold people ("capable of holding 4 passengers but no passengers flew")
    can_carry = cap.str.contains(r"capable of|designed (?:for|to)|can (?:carry|hold|seat)|holding|\d+\s*(?:passengers?|seats?|people|persons?|pilots?)|(?:one|two|three|four|five|six)\s+(?:passengers?|seats?|people)")
    strong_cap = cap.str.contains("cargo only|cargo") & cap.str.contains("cargo only|no passengers")   # explicit cargo-only capacity
    weak_cap = cap.str.contains("no passengers") & ~strong_cap
    uav_cap = (cap.str.contains("cargo only") | cap.str.contains("no passengers")) & ~can_carry
    title_l = d["title"].str.lower()
    type_l = d["spec_aircraft_type"].str.lower()
    cargo_name = title_l.str.contains(DIRECTORY_CARGO_NAME)
    cargo_type = type_l.str.contains(DIRECTORY_CARGO_TYPE)
    # a person named in the type ("passenger or air cargo") or the piloting field ("1 pilot", "2 pilots") is a crewed design
    people_other = (type_l + " " + d["spec_piloting"].str.lower()).str.contains(r"passengers?|\b[1-9] pilots?\b|\bseats?\b")
    typ_rule = (cargo_type | cargo_name) & ~cap.str.contains(DIRECTORY_PEOPLE) & ~people_other
    # 2026-10-11 ruling (multicopters were far too many against the patents): type / name saying cargo / drone ... with no person
    # in the capacity is a UAV. 2026-10-11 ruling: only truly unmanned pages are UAVs; autonomous / remote count as piloted
    cargo_cap = cap.str.contains(r"(?<!no )\bcargo\b") & cap.str.contains(r"\bonly\b|no passengers|no pilot") & ~cap.str.contains(r"no passengers? or cargo")
    strong = (cargo_cap & ~can_carry) | (cargo_name & cap.str.contains(r"(?<!no )\bcargo\b")) | (type_l.str.contains(r"\bcargo\b|drone") & ~can_carry & ~people_other & ~cap.str.replace(r"no (?:passengers?|pilots?)", "", regex=True).str.contains(DIRECTORY_PEOPLE)) | status.eq("cargo drone") | (typ_rule & ~people_other & (cargo_name | type_l.str.contains("cargo|drone|delivery|logistic|freight|agricultur|spray")))
    weak = ((weak_cap & uav_cap) | typ_rule) & ~strong
    # 2026-10-11, after the author's review: an uncrewed demonstrator is OUT even when its maker builds passenger aircraft
    # (Section 3.1.1 occupancy rule: piloted, passenger-carrying). directory_paxdesign_pages is kept for reference only.
    pax_design = d["slug_key"].map(directory_paxdesign_pages(cfg)).astype(object).where(lambda x: x.notna(), False).astype(bool)
    uav = strong | weak
    # 2026-10-11 ruling: a UAV is excluded only when it is uncrewed EXCLUSIVELY; if the page text says it can be crewed /
    # piloted (own description, not the Resources list), it is not a UAV
    crewed_text = d["slug_key"].map(directory_crewed_pages(cfg)).astype(object).where(lambda s: s.notna(), False).astype(bool)
    uav = uav & ~crewed_text
    # author's individual rulings on the review page (review/domain_overrides.csv): in domain whatever the rules say
    ov_path = _Path(__file__).resolve().parents[1] / "review" / "domain_overrides.csv"
    if use_overrides and ov_path.exists():
        ovd = pd.read_csv(ov_path, keep_default_na=False)
        ov = set(ovd.query("decision == 'in_domain'")["slug_key"])
        ovx = set(ovd.query("decision == 'exclude'")["slug_key"])
        uav = (uav & ~d["slug_key"].isin(ov)) | d["slug_key"].isin(ovx)
        combustion_only = combustion_only & ~d["slug_key"].isin(ov)
    links = pd.read_csv(cfg.path("evtolnews_patent_links"), keep_default_na=False)
    linked = {s for x in links.loc[links["use"].eq("yes"), "slug_keys"] for s in str(x).split("|") if s}
    return pd.DataFrame({"slug_key": d["slug_key"], "class5": d["evtol_class"], "status": status,
                         "status_group": group, "not_combustion": ~combustion_only, "crewed": ~uav,
                         "in_domain": ~combustion_only & ~uav, "patented": d["slug_key"].isin(linked)})
