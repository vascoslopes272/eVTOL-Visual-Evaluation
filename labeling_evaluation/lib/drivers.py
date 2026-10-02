"""Design-driver analysis: per-class trend of a trace against priority year, driver verdicts, coupling test.

Science only: pure functions of DataFrames and parameters; no file reading, no config, no text.
The data definitions (DRIVERS, TRACES, PREDICTED_COUPLINGS, ...) are copied verbatim from the archive.
The coupling measure (bias-corrected Cramér's V) is NOT implemented here: `coupling_table` takes a `measure`
callable (x: Series, y: Series) -> (V, n); lib.association is expected to supply `cramers_v_bc`.
Wrangling that builds the trace frame from the raw label records (la_tables.trace_frame, config_frame) is not
part of lib: callers pass the finished frame (columns topType, window, year, one column per trace key).
"""
from __future__ import annotations

import itertools
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats as _st

#: copied from la_tables.py:26-27 (a2.WINDOWS names), in time order
WINDOW_NAMES: List[str] = ["<= 2011", "2012-15", "2016-19", "2020-23", "2024-26 (partial)"]
#: copied from la_tables.py:44 (every trend claim ends here, ruling 2026-09-10)
LAST_COMPLETE = 2023
#: copied from la_tables.py:2137 (a cell under this many aircraft is blank)
MIN_CELL = 5
#: copied from la_tables.py:2138
MIN_WINDOWS = 3

# ---- copied from la_tables.py:2392-2413 (DRIVERS, DRIVER_KIND_NAMES)
#: The drivers, verbatim in substance from the author's table: code -> (kind, name). A1 =
#: technological, moved over the window; A2 = physical, fixed (predicts couplings, not trends);
#: B = requirement; C = life-cycle cost. Battery specific energy is left out on the author's
#: ruling: a sector-level enabler with no morphology trace of its own (Appendix C holds it).
DRIVERS: Dict[str, Tuple[str, str]] = {
    "A1.transition": ("A1", "regime transition"),
    "A1.dep": ("A1", "distributed propulsion and rotor control"),
    "A2.hover": ("A2", "hover load path"),
    "A2.wing": ("A2", "wing structural and aeroelastic limits"),
    "A2.stability": ("A2", "cruise stability and control"),
    "A2.drag": ("A2", "flow interference and drag"),
    "B.range": ("B", "mission range and speed"),
    "B.payload": ("B", "payload"),
    "B.occupant": ("B", "occupant presence"),
    "B.failure": ("B", "failure tolerance"),
    "B.noise": ("B", "community noise"),
    "B.environment": ("B", "operating environment"),
    "C.development": ("C", "development and certification cost"),
    "C.production": ("C", "production cost"),
    "C.maintenance": ("C", "maintenance cost"),
}
DRIVER_KIND_NAMES = {"A1": "A1 technological", "A2": "A2 physical", "B": "B requirement", "C": "C life-cycle cost"}

# ---- copied from la_tables.py:2414-2471 (TRACES, TRACE_OF)

#: The labelled traces, in the order the figure draws them (by the kind of the first driver:
#: A1, A2, B, C). ``kind`` is ``share`` (a share of the row's aircraft) or ``median`` (a count);
#: ``base`` names the aircraft a share divides by when it is narrower than the class-window;
#: ``drivers`` maps each driver that predicts the trace to the direction it predicts over time
#: ("+" more, "-" less, "±" the driver names the trace without a direction over time — every A2
#: driver, which is fixed, and the requirement and cost drivers where the author's table gives
#: no sign). ``drawn`` = a panel of the figure; the rest are in the tables only. ``from_215``
#: marks the four traces Figure 2.3b already draws: they are computed here by the same formula
#: so the two figures cannot disagree, and are read in the verdict table, not redrawn. ``show_mean``
#: prints the mean beside the median of a small-integer count (a median of 1 or 2 can stand still
#: while the distribution moves); propulsive units has no mean, because a handful of hull arrays
#: with 40-80 units would carry it.
TRACES: List[Dict] = [
    dict(key="joints", label="tilting joint groups", kind="median", panel="median tilting\njoint groups",
         drivers={"A1.transition": "+", "C.development": "-", "C.maintenance": "-"}, drawn=True, show_mean=True,
         note="a tilting wing panel, a tilting boom group, a tilting propulsor type and a tilting empennage "
              "each count one; 0 for a fixed-thrust aircraft"),
    dict(key="fus_moves", label="fuselage kinematics not fixed", kind="share", panel="% fuselage\nkinematics not fixed",
         drivers={"A1.transition": "+", "B.occupant": "-"}, drawn=True,
         note="whole-body pitch, tail-sitter or variable incidence"),
    dict(key="retract", label="a propulsor retracts or folds its blades", kind="share",
         panel="% with a retracting\nor blade-folding unit",
         drivers={"A2.drag": "+"}, drawn=True,
         note="any thrust type recorded Retracting or Blade-folding; base = aircraft with a propulsor record"),
    dict(key="booms_stow", label="booms stow", kind="share", base="aircraft with booms",
         drivers={"B.environment": "+", "A2.drag": "+"}, drawn=False),
    dict(key="units", label="propulsive units", kind="median", panel="median\npropulsive units",
         drivers={"A1.dep": "+", "B.failure": "+", "B.noise": "+"}, drawn=True, from_215=True),
    dict(key="on_booms", label="units carried on booms", kind="share", panel="% with units\non booms",
         drivers={"A1.dep": "+", "A2.hover": "±"}, drawn=True),
    dict(key="stations", label="stations carrying units", kind="median",
         drivers={"A1.dep": "+"}, drawn=False, show_mean=True),
    dict(key="booms", label="booms present", kind="share",
         drivers={"A2.hover": "±", "A2.drag": "±"}, drawn=False, from_215=True),
    dict(key="wing_LE", label="wing units at the leading edge", kind="share", base="aircraft with units on a wing",
         panel="% wing units at\nleading edge",
         drivers={"A2.drag": "±", "A2.wing": "±"}, drawn=True),
    dict(key="pusher", label="a pusher unit", kind="share", panel="% with a\npusher unit",
         drivers={"A2.drag": "±"}, drawn=True),
    dict(key="two_wings", label="two or more wing panels", kind="share", panel="% with two or\nmore wing panels",
         drivers={"A2.hover": "±", "A2.wing": "±", "A2.stability": "±", "B.range": "±"}, drawn=True),
    dict(key="swept", label="swept or delta main wing", kind="share", base="aircraft with a planform",
         panel="% swept or\ndelta main wing",
         drivers={"B.range": "±", "A2.wing": "±"}, drawn=True),
    dict(key="tailless", label="no tail surface", kind="share",
         drivers={"A2.stability": "±"}, drawn=False, from_215=True),
    dict(key="ducted", label="a ducted unit", kind="share",
         drivers={"B.noise": "+"}, drawn=False, from_215=True),
    dict(key="gear_drawn", label="ground contact drawn", kind="share", panel="% ground\ncontact drawn",
         drivers={"B.payload": "±", "B.environment": "±", "C.maintenance": "±"}, drawn=True),
    dict(key="wheeled", label="wheeled gear, of the ground contact drawn", kind="share",
         base="aircraft with ground contact drawn",
         drivers={"B.payload": "±", "B.environment": "±", "C.maintenance": "±"}, drawn=False),
    dict(key="n_types", label="propulsor types", kind="median", panel="median\npropulsor types",
         drivers={"C.development": "-", "C.production": "-"}, drawn=True, show_mean=True),
]
TRACE_OF = {t["key"]: t for t in TRACES}

# ---- copied from la_tables.py:2473-2481 (UNLABELLED_TRACES)
#: Traces the drivers table predicts that no label carries; one row each in the verdict table
#: and one entry each in ``la_index.UNLABELLED_DRIVERS`` (Appendix C).
UNLABELLED_TRACES: List[Tuple[str, str]] = [
    ("rotor diameter", "A1.dep, B.noise"),
    ("hub mechanism (blade pitch against RPM control)", "A1.dep, C.maintenance"),
    ("cabin dimensions", "B.occupant, B.payload"),
    ("aircraft size", "B.environment"),
    ("tilting joint count within a group", "C.development, C.maintenance"),
]

# ---- copied from la_tables.py:2486-2487 (TREND_MIN, TREND_ALPHA)
TREND_MIN = 20          # a trend is read on at least this many aircraft with a value, complete years
TREND_ALPHA = 0.05

# ---- copied from la_tables.py:2552-2553 (POOLED)
#: pooled rows of :func:`trace_drift` and :func:`trace_trends`: code -> printed name
POOLED = {"ALL5": "five drawn classes pooled", "ALL": "all classed aircraft"}

# ---- copied from la_tables.py:2765-2811 (PREDICTED_COUPLINGS, DEFINITIONAL_RULES, _DEF_PAIRS, COUPLING_*)
#: field b, printed name). A fixed driver predicts no trend; it predicts that two traces are
#: chosen together, so each pair is tested against the distribution of every other field pair.
PREDICTED_COUPLINGS: List[Tuple[str, str, str, str]] = [
    ("A2.hover", "boomsPresent", "wCount", "boom presence ↔ wing panel count"),
    ("A2.hover", "boomsPresent", "wing1_zoneSpan", "boom presence ↔ spanwise placement of the wing units"),
    ("A2.stability", "empType", "wCount", "empennage type ↔ wing panel count"),
    ("A2.stability", "empType", "wing1_posL", "empennage type ↔ longitudinal wing position"),
    ("A2.wing", "wing1_count", "wing1_plan", "units on the main wing ↔ planform"),
    ("A2.wing", "wing1_count", "wCount", "units on the main wing ↔ wing panel count"),
    ("A2.drag", "wing1_zoneChord", "retract", "chordwise position of the wing units ↔ retraction"),
    ("A2.drag", "wing1_chord", "retract", "tractor or pusher ↔ retraction"),
]

#: Pairs whose coupling is the codebook's own construction, never a finding (the trap of
#: DEEPER_ANALYSES.md §2): each rule names why. They are marked in the figure and left out of
#: the distribution a predicted pair is ranked against.
DEFINITIONAL_RULES: List[Tuple[str, str]] = [
    ("topType × any_tilting_unit, mixes_fixed_and_tilting, fusKin, wCount, wing1_propKin, wing1_orient",
     "the class is defined by whether and where thrust tilts, by the body's kinematics and by the wing count"),
    ("boomsPresent × boom_count, boom_ntypes; boom_count × boom_ntypes",
     "the boom fields are only asked when booms are present"),
    ("any_tilting_unit × mixes_fixed_and_tilting; any_ducted_unit × all_units_ducted",
     "one derived answer contains the other"),
    ("wing1_bmech, wing1_propKin, wing1_orient × the derived tilt and duct answers",
     "the aircraft-level answer is built from the card"),
    ("fuselage_count × fuselage_sym; wing1_count × the other wing1 card fields; wCount × wingConf",
     "a card field is only asked when the card holds units, and the wing configuration names the wing count"),
]
DEFINITIONAL_PAIRS = set()
for _a in ("any_tilting_unit", "mixes_fixed_and_tilting", "fusKin", "wCount", "wing1_propKin", "wing1_orient"):
    DEFINITIONAL_PAIRS.add(frozenset(("topType", _a)))
for _a in ("boom_count", "boom_ntypes"):
    DEFINITIONAL_PAIRS.add(frozenset(("boomsPresent", _a)))
DEFINITIONAL_PAIRS.add(frozenset(("boom_count", "boom_ntypes")))
DEFINITIONAL_PAIRS.add(frozenset(("any_tilting_unit", "mixes_fixed_and_tilting")))
DEFINITIONAL_PAIRS.add(frozenset(("any_ducted_unit", "all_units_ducted")))
for _a in ("wing1_bmech", "wing1_propKin", "wing1_orient"):
    for _b in ("any_tilting_unit", "mixes_fixed_and_tilting", "any_ducted_unit", "all_units_ducted"):
        DEFINITIONAL_PAIRS.add(frozenset((_a, _b)))
DEFINITIONAL_PAIRS.add(frozenset(("fuselage_count", "fuselage_sym")))
DEFINITIONAL_PAIRS.add(frozenset(("wCount", "wingConf")))
for _a in ("wing1_zoneSpan", "wing1_zoneChord", "wing1_orient", "wing1_propKin", "wing1_bmech", "wing1_chord"):
    DEFINITIONAL_PAIRS.add(frozenset(("wing1_count", _a)))
del _a, _b

COUPLING_MIN_N = 30     # a pair is measured on at least this many aircraft answering both fields
COUPLING_STRONG = 0.75  # a predicted pair "stronger than most" sits above this quantile of the rest


# =============================================================================== functions
def class_selection(frame: pd.DataFrame, min_cell: int = MIN_CELL, min_windows: int = MIN_WINDOWS,
                    windows: Sequence[str] = WINDOW_NAMES) -> List[str]:
    """The class codes drawn: classes with at least `min_cell` aircraft in at least `min_windows` windows, largest first.

    RULE: cross-tabulate topType x window over rows with both; class kept when (#windows with count >= min_cell)
    >= min_windows; ordered by total aircraft, descending (pandas default sort).
    `frame` has columns topType, window.

    Ported from: archive la_tables.py:class_selection / drawn_classes (the list of codes)
    Used in: la_driver_*, la_trace_*
    """
    w = frame.dropna(subset=["window", "topType"])
    ct = pd.crosstab(w["topType"], w["window"]).reindex(columns=list(windows), fill_value=0)
    windows_ok = (ct >= min_cell).sum(axis=1)
    sizes = ct.sum(axis=1).sort_values(ascending=False)
    return [c for c in sizes.index if windows_ok[c] >= min_windows]


def trace_values(s: pd.Series, kind: str) -> pd.Series:
    """A trace column as floats: a share trace maps True/False to 1.0/0.0 (anything else NaN); a median trace is numeric.

    Ported from: archive la_tables.py:_trace_values
    """
    if kind == "share":
        return s.map({True: 1.0, False: 0.0}).astype(float)
    return pd.to_numeric(s, errors="coerce").astype(float)


def _class_rows(t: pd.DataFrame, code: str, classes: Sequence[str]) -> pd.DataFrame:
    return t[t["topType"].eq(code)] if code in classes else (
        t[t["topType"].isin(classes)] if code == "ALL5" else t)


def dimension_drift(v: pd.DataFrame, classes: Sequence[str], windows: Sequence[str] = WINDOW_NAMES,
                    min_cell: int = MIN_CELL, class_names: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """Per class and window: medians / shares of the morphology dimensions and how many aircraft answered each.

    RULE: for each class x window a row; fewer than `min_cell` aircraft -> blank measures and zero answered counts.
    Otherwise: median propulsive units (units), share with a ducted unit (any_ducted mean, 2 dp), share with no tail
    surface (empType == 'Tailless', 2 dp, over ALL aircraft of the cell, NaN counted as not Tailless), share with booms
    (nBooms > 0 over aircraft with nBooms, 2 dp), share offering another source (powertrain_review == 'multi_source'
    among aircraft whose is_electric_final != 'Unknown'; blank when fewer than `min_cell` state a powertrain), share
    with a tilting unit (any_tilting mean, 2 dp), median wings (wCount), and the 'answered' counts.
    `v` = analysis frame; `class_names` maps class code -> printed name.

    Ported from: archive la_tables.py:dimension_drift
    Used in: la_dimension_drift (Figure B.3b)
    """
    class_names = class_names or {}
    w = v.dropna(subset=["window", "topType"])
    rows = []
    for c in classes:
        for name in windows:
            sub = w[w["topType"].eq(c) & w["window"].eq(name)]
            if len(sub) < min_cell:
                rows.append({"class": class_names.get(c, c), "code": c, "window": name,
                             "aircraft": int(len(sub)), "median propulsive units": np.nan,
                             "share with a ducted unit": np.nan, "share with no tail surface": np.nan,
                             "share with booms": np.nan, "share offering another source": np.nan,
                             "share with a tilting unit": np.nan, "median wings": np.nan,
                             "propulsive units answered": 0, "ducted answered": 0, "tail answered": 0,
                             "booms answered": 0, "powertrain stated": 0, "tilting answered": 0})
                continue
            power = sub["is_electric_final"].astype(str)
            stated = power.ne("Unknown")
            rows.append({"class": class_names.get(c, c), "code": c, "window": name, "aircraft": int(len(sub)),
                         "median propulsive units": float(pd.to_numeric(sub["units"], errors="coerce").median()),
                         "share with a ducted unit": round(float(sub["any_ducted"].map({True: 1, False: 0}).mean()), 2),
                         "share with no tail surface": round(float(sub["empType"].astype(str).eq("Tailless").mean()), 2),
                         "share with booms": round(float((pd.to_numeric(sub["nBooms"], errors="coerce")
                                                          .dropna() > 0).mean()), 2),
                         "share offering another source": (round(float(sub.get("powertrain_review", pd.Series(index=sub.index, dtype=object))
                                                         [stated].astype(str).eq("multi_source").mean()), 2)
                                                 if int(stated.sum()) >= min_cell else np.nan),
                         "share with a tilting unit": round(float(sub["any_tilting"].map({True: 1, False: 0}).mean()), 2),
                         "median wings": float(pd.to_numeric(sub["wCount"], errors="coerce").median()),
                         "propulsive units answered": int(pd.to_numeric(sub["units"], errors="coerce").notna().sum()),
                         "ducted answered": int(sub["any_ducted"].notna().sum()),
                         "tail answered": int(sub["empType"].notna().sum()),
                         "booms answered": int(pd.to_numeric(sub["nBooms"], errors="coerce").notna().sum()),
                         "powertrain stated": int(stated.sum()),
                         "tilting answered": int(sub["any_tilting"].notna().sum())})
    return pd.DataFrame(rows)


def trace_drift(t: pd.DataFrame, classes: Sequence[str], traces: Sequence[Dict] = TRACES,
                windows: Sequence[str] = WINDOW_NAMES, min_cell: int = MIN_CELL,
                class_names: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """Per class (and two pooled rows) and window: the share (or median) of each trace and the aircraft it rests on.

    RULE: rows = classes, then 'ALL5' (the drawn classes pooled), then 'ALL' (every classed aircraft); for each
    window one row. A cell is the mean of the 0/1 trace (share, rounded 2 dp) or the median (kind 'median')
    over the aircraft that answer it, and is blank unless the row has >= min_cell aircraft AND >= min_cell answers.
    '<trace label> n' = number of answers. `t` = trace frame (columns topType, window, year and one per trace key).

    Ported from: archive la_tables.py:trace_drift
    Used in: la_trace_drift (Figure 2.6a)
    """
    class_names = class_names or {}
    t = t.dropna(subset=["window", "topType"])
    rows = []
    for code in list(classes) + list(POOLED):
        sub_c = _class_rows(t, code, classes)
        for name in windows:
            sub = sub_c[sub_c["window"].eq(name)]
            row = {"class": class_names.get(code, POOLED.get(code, code)), "code": code,
                   "window": name, "aircraft": int(len(sub))}
            for tr in traces:
                vals = trace_values(sub[tr["key"]], tr["kind"]).dropna()
                ok = len(sub) >= min_cell and len(vals) >= min_cell
                row[tr["label"]] = (round(float(vals.mean()), 2) if tr["kind"] == "share" else float(vals.median())) if ok else np.nan
                row[tr["label"] + " n"] = int(len(vals))
            rows.append(row)
    return pd.DataFrame(rows)


def trend_test(year, x, trend_min: int = TREND_MIN, alpha: float = TREND_ALPHA,
               last_complete: int = LAST_COMPLETE) -> Dict:
    """Did a trace move with priority year? Spearman rank correlation with the document's reading rules.

    RULE: keep pairs with both values and year <= last_complete; fewer than `trend_min` (20) pairs -> 'too thin';
    x constant -> 'constant'; otherwise Spearman rho (scipy.stats.spearmanr) and its two-sided p;
    'rises' / 'falls' (sign of rho) if p < `alpha` (0.05), else 'flat'. rho rounded to 2 dp, p unrounded.
    Returns dict(aircraft, rho, p, movement).

    Ported from: archive la_tables.py:trace_trends (inner test); sm_open.py:_spearman
    Used in: la_trace_trends, la_driver_verdicts, la_driver_links
    """
    s = pd.DataFrame({"y": pd.to_numeric(pd.Series(year), errors="coerce"),
                      "x": pd.Series(x)}).dropna()
    s = s[s["y"].le(last_complete)]
    out = {"aircraft": int(len(s)), "rho": np.nan, "p": np.nan}
    if len(s) < trend_min:
        out["movement"] = "too thin"
    elif s["x"].nunique() < 2:
        out["movement"] = "constant"
    else:
        rho, p = _st.spearmanr(s["y"], s["x"])
        out["rho"], out["p"] = round(float(rho), 2), float(p)
        out["movement"] = ("rises" if rho > 0 else "falls") if p < alpha else "flat"
    return out


def trace_trends(t: pd.DataFrame, drift: pd.DataFrame, classes: Sequence[str], traces: Sequence[Dict] = TRACES,
                 windows: Sequence[str] = WINDOW_NAMES, min_cell: int = MIN_CELL,
                 class_names: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """Did each trace move inside each class? One row per trace x (class, ALL5, ALL) with the test and the size of the movement.

    RULE: the test is trend_test(year, trace) on the aircraft of the row with a value (complete years, >= 20 aircraft,
    p < 0.05). Beside it: the value in the earliest window of the row that is reportable in `drift` (not blank; the
    partial last window excluded) and in '2020-23'; for traces with show_mean the mean in those two windows (blank
    below `min_cell` answers, 2 dp). 'driver kind' = kind of the first driver of the trace. `drift` is the output of
    trace_drift on the same inputs.

    Ported from: archive la_tables.py:trace_trends
    Used in: la_trace_trends
    """
    class_names = class_names or {}
    t = t.dropna(subset=["window", "topType"])
    rows = []
    for tr in traces:
        for code in list(classes) + list(POOLED):
            sub_c = _class_rows(t, code, classes)
            s = pd.DataFrame({"y": pd.to_numeric(sub_c["year"], errors="coerce"),
                              "x": trace_values(sub_c[tr["key"]], tr["kind"])}).dropna()
            s = s[s["y"].le(LAST_COMPLETE)]
            d = drift[drift["code"].eq(code)].set_index("window")
            solid = [w for w in list(windows)[:-1] if pd.notna(d.loc[w, tr["label"]])]
            first_w = solid[0] if solid else None
            first = d.loc[first_w, tr["label"]] if first_w else np.nan
            last = d.loc["2020-23", tr["label"]]
            means = {}
            if tr.get("show_mean"):
                for tag, w in (("first mean", first_w), ("2020-23 mean", "2020-23")):
                    vals = trace_values(sub_c[sub_c["window"].eq(w)][tr["key"]], tr["kind"]).dropna() if w else pd.Series(dtype=float)
                    means[tag] = round(float(vals.mean()), 2) if len(vals) >= min_cell else np.nan
            row = {"trace": tr["label"], "driver kind": DRIVERS[next(iter(tr["drivers"]))][0],
                   "class": class_names.get(code, POOLED.get(code, code)), "code": code,
                   "aircraft": int(len(s)), "first window": first_w or "", "first value": first,
                   "2020-23 value": last, "first mean": means.get("first mean", np.nan),
                   "2020-23 mean": means.get("2020-23 mean", np.nan), "rho": np.nan, "p": np.nan}
            res = trend_test(s["y"], s["x"])
            row["rho"], row["p"], row["movement"] = res["rho"], res["p"], res["movement"]
            rows.append(row)
    return pd.DataFrame(rows)


def trace_direction(trend_rows: pd.DataFrame) -> str:
    """Overall direction of one trace from its trends rows: '+', '-', 'mixed' or '0'.

    RULE: `trend_rows` = the trends rows of ONE trace (columns code, movement). A class that 'rises' counts up, one that
    'falls' counts down; the pooled 'ALL5' row counts the same way; 'ALL' is ignored. 'mixed' if both up and down,
    '+' if only up, '-' if only down, '0' if neither.

    Ported from: archive la_tables.py:_moved_text (the direction part)
    Used in: la_driver_verdicts
    """
    sub = trend_rows.set_index("code")
    cls = [c for c in sub.index if c not in POOLED]
    moved = [c for c in cls if sub.loc[c, "movement"] in ("rises", "falls")]
    p5 = sub.loc["ALL5"]
    ups = [c for c in moved if sub.loc[c, "movement"] == "rises"] + (["ALL5"] if p5["movement"] == "rises" else [])
    downs = [c for c in moved if sub.loc[c, "movement"] == "falls"] + (["ALL5"] if p5["movement"] == "falls" else [])
    return "mixed" if ups and downs else "+" if ups else "-" if downs else "0"


def driver_verdict(drivers: Mapping[str, str], direction: str) -> Dict:
    """The verdict code for one trace from the drivers that predict it and the observed direction.

    RULE (drivers = {code: predicted sign '+', '-' or '±'}; A2 drivers are fixed and never candidates for a movement):
      moving = drivers whose kind is not A2 ; fixed = A2 drivers
      direction '0'                              -> 'does_not_move'
      direction 'mixed'                          -> 'mixed_by_class'
      no moving driver                           -> 'fixed_only'
      '+' and '-' both among moving signs        -> 'opposed'   (with = moving drivers whose sign == direction or '±';
                                                                  against = moving with sign in '+-' and != direction)
      else consistent = moving whose sign == direction or '±':
           exactly 1 -> 'single'; 0 -> 'against_all'; >= 2 -> 'overdetermined'
    For 'single', 'against_all' and 'overdetermined' the fixed drivers are reported in `fixed` (coupling only).
    Returns dict(verdict, with, against, consistent, fixed, moving, n_drivers).

    Ported from: archive la_tables.py:driver_verdicts (rule part; the archive builds sentences)
    Used in: la_driver_verdicts
    """
    moving = {c: s for c, s in drivers.items() if DRIVERS[c][0] != "A2"}
    fixed = [c for c in drivers if DRIVERS[c][0] == "A2"]
    signs = set(moving.values())
    out = {"verdict": None, "with": [], "against": [], "consistent": [], "fixed": [],
           "moving": moving, "n_drivers": len(drivers)}
    if direction == "0":
        out["verdict"] = "does_not_move"
    elif direction == "mixed":
        out["verdict"] = "mixed_by_class"
    elif not moving:
        out["verdict"] = "fixed_only"
    elif "+" in signs and "-" in signs:
        out["verdict"] = "opposed"
        out["with"] = [c for c, s in moving.items() if s == direction or s == "±"]
        out["against"] = [c for c, s in moving.items() if s in "+-" and s != direction]
    else:
        consistent = [c for c, s in moving.items() if s == direction or s == "±"]
        out["consistent"] = consistent
        out["verdict"] = "single" if len(consistent) == 1 else "against_all" if len(consistent) == 0 else "overdetermined"
        out["fixed"] = fixed
    return out


def driver_verdicts(trends: pd.DataFrame, traces: Sequence[Dict] = TRACES,
                    unlabelled: Sequence[Tuple[str, str]] = UNLABELLED_TRACES) -> pd.DataFrame:
    """One row per trace: observed direction and the coded verdict; then one 'not_labelled' row per unlabelled trace.

    Columns: trace (label), driver kind (name from DRIVER_KIND_NAMES of the first driver), direction, verdict, with,
    against, consistent, fixed, n_drivers. See driver_verdict for the rule and trace_direction for the direction.
    The archive's 'verdict class' column is the first clause of its sentence; the codes map to it as:
    does_not_move='trace does not move', mixed_by_class='mixed by class', fixed_only='moves, but only fixed physical
    drivers predict this trace', opposed='opposed drivers', single='single driver', against_all='moved against every
    driver that predicts a direction', overdetermined='overdetermined', not_labelled='not labelled'.
    `trends` is the output of trace_trends.

    Ported from: archive la_tables.py:driver_verdicts
    Used in: la_driver_verdicts
    """
    rows = []
    for tr in traces:
        direction = trace_direction(trends[trends["trace"].eq(tr["label"])])
        r = driver_verdict(tr["drivers"], direction)
        rows.append({"trace": tr["label"], "driver kind": DRIVER_KIND_NAMES[DRIVERS[next(iter(tr["drivers"]))][0]],
                     "direction": direction, "verdict": r["verdict"], "with": r["with"], "against": r["against"],
                     "consistent": r["consistent"], "fixed": r["fixed"], "n_drivers": r["n_drivers"]})
    for name, codes in unlabelled:
        rows.append({"trace": name, "driver kind": DRIVER_KIND_NAMES[DRIVERS[codes.split(",")[0].strip()][0]],
                     "direction": None, "verdict": "not_labelled", "with": [], "against": [], "consistent": [],
                     "fixed": [], "n_drivers": len(codes.split(","))})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- coupling test
def coupling_table(F: pd.DataFrame, fields: Sequence[str],
                   measure: Optional[Callable[[pd.Series, pd.Series], Tuple[float, int]]] = None,
                   predicted: Sequence[Tuple[str, str, str, str]] = PREDICTED_COUPLINGS,
                   definitional=DEFINITIONAL_PAIRS) -> pd.DataFrame:
    """Association of every pair of fields, flagged definitional / predicted, with each pair's percentile among the rest.

    `measure` defaults to lib.association.cramers_v_bc (bias-corrected Cramér's V, as the document).
    RULE: for each unordered pair (a, b) of `fields` in itertools.combinations order: (V, n) = measure(F[a], F[b])
    (the document uses bias-corrected Cramér's V, V rounded 3 dp, NaN if n < 30); 'definitional' if the pair is in
    `definitional`; driver and printed name from `predicted` when the pair is a predicted coupling.
    'rest' = measured, non-definitional V. percentile of a measured V = round(mean(rest < V), 2).
    attrs: pairs, measured, definitional, rest, median / q75 / q90 of `rest` (3 dp), fields.

    Ported from: archive la_tables.py:trace_couplings
    Used in: la_trace_couplings_all, la_trace_couplings
    """
    if measure is None:
        from .association import cramers_v_bc as measure
    rows = []
    pred = {frozenset((a, b)): (drv, name) for drv, a, b, name in predicted}
    for a, b in itertools.combinations(fields, 2):
        V, n = measure(F[a], F[b])
        key = frozenset((a, b))
        rows.append({"field a": a, "field b": b, "V": (round(V, 3) if pd.notna(V) else np.nan), "aircraft": n,
                     "definitional": key in definitional,
                     "driver": pred.get(key, ("", ""))[0], "predicted pair": pred.get(key, ("", ""))[1]})
    out = pd.DataFrame(rows)
    rest = out[out["V"].notna() & ~out["definitional"]]["V"]
    out["percentile"] = np.nan
    ok = out["V"].notna()
    out.loc[ok, "percentile"] = [round(float((rest < x).mean()), 2) for x in out.loc[ok, "V"]]
    q = rest.quantile([0.5, 0.75, 0.9]).to_dict()
    out.attrs.update({"pairs": int(len(out)), "measured": int(out["V"].notna().sum()),
                      "definitional": int(out["definitional"].sum()), "rest": int(len(rest)),
                      "median": round(float(q[0.5]), 3), "q75": round(float(q[0.75]), 3), "q90": round(float(q[0.9]), 3),
                      "fields": list(fields)})
    return out


def coupling_reading(V: float, median: float, q75: float, q90: float) -> str:
    """Code for how a pair's V compares with the non-definitional pairs.

    RULE: NaN -> 'not_measurable'; V >= q90 -> 'strongest_tenth'; V >= q75 -> 'above_upper_quartile';
    V >= median -> 'typical'; else 'weaker'.

    Ported from: archive la_tables.py:predicted_couplings (reading)
    Used in: la_trace_couplings
    """
    if pd.isna(V):
        return "not_measurable"
    if V >= q90:
        return "strongest_tenth"
    if V >= q75:
        return "above_upper_quartile"
    if V >= median:
        return "typical"
    return "weaker"


def predicted_couplings(P: pd.DataFrame, predicted: Sequence[Tuple[str, str, str, str]] = PREDICTED_COUPLINGS,
                        top: int = 3) -> pd.DataFrame:
    """One row per predicted pair with V, n, percentile and reading code, then the `top` strongest non-definitional pairs.

    RULE: for each predicted pair found in `P` (either field order): its V, aircraft, percentile and
    coupling_reading(V, P.attrs median / q75 / q90); then the `top` (3) rows of P that are non-definitional and measured,
    sorted by V descending (pandas default sort), with driver None and reading 'for_scale'.
    `P` is the output of coupling_table.

    Ported from: archive la_tables.py:predicted_couplings
    Used in: la_trace_couplings
    """
    q75, q90, med = P.attrs["q75"], P.attrs["q90"], P.attrs["median"]
    rows = []
    for drv, a, b, name in predicted:
        r = P[((P["field a"] == a) & (P["field b"] == b)) | ((P["field a"] == b) & (P["field b"] == a))]
        if not len(r):
            continue
        r = r.iloc[0]
        rows.append({"driver": drv, "predicted pair": name, "fields": f"{a} × {b}", "V": r["V"],
                     "aircraft": int(r["aircraft"]), "percentile": r["percentile"],
                     "reading": coupling_reading(r["V"], med, q75, q90)})
    t = P[~P["definitional"] & P["V"].notna()].sort_values("V", ascending=False).head(top)
    for _, r in t.iterrows():
        rows.append({"driver": None, "predicted pair": "strongest pair in the matrix",
                     "fields": f"{r['field a']} × {r['field b']}", "V": r["V"], "aircraft": int(r["aircraft"]),
                     "percentile": r["percentile"], "reading": "for_scale"})
    out = pd.DataFrame(rows)
    out.attrs.update(P.attrs)
    return out


# ----------------------------------------------------------------------------- driver windows / links (chapter 3.4)
def window_centre(s: pd.Series, how: str, min_cell: int = MIN_CELL) -> float:
    """Centre of a trace in a window: median or mean of its non-missing values, 3 dp; NaN under `min_cell` values.

    Ported from: archive sm_open.py:driver_windows (inner `_c`)
    Used in: la_driver_windows
    """
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) < min_cell:
        return np.nan
    return round(float(s.median() if how == "median" else s.mean()), 3)


def driver_windows(cf: pd.DataFrame, classes: Sequence[str], windows: Sequence[str], few: Sequence[str],
                   min_cell: int = MIN_CELL, class_names: Optional[Mapping[str, str]] = None) -> pd.DataFrame:
    """Per class and complete window: the centre of each trace drawn in chapter 3.4.

    RULE: propulsive units = MEDIAN; tilting sets, propulsor types and tilting sets per propulsive unit = MEAN (the
    median kept beside the mean for the two counts); shares are shares of the aircraft answering; every cell is
    blank under `min_cell` values (window_centre). Ducted share is split by units-on-booms only for class 'CVT'.
    `cf` = config frame (columns topType, window, year, units, sets, n_types, any_fixed, recorded, on_booms, ducted).

    Ported from: archive sm_open.py:driver_windows
    Used in: la_driver_windows
    """
    class_names = class_names or {}
    rows = []
    for code in classes:
        for wn in windows:
            d = cf[cf["topType"].eq(code) & cf["window"].eq(wn)]
            u = d["units"].where(d["units"] > 0)
            spu = d["sets"] / u
            onb = d["on_booms"].map({True: 1.0, False: 0.0})
            duc = d["ducted"].map({True: 1.0, False: 0.0})
            row = {"class": class_names.get(code, code), "code": code, "window": wn,
                   "aircraft": int(len(d)), "few aircraft": wn in few,
                   "tilting sets (mean)": window_centre(d["sets"], "mean", min_cell),
                   "tilting sets (median)": window_centre(d["sets"], "median", min_cell),
                   "propulsive units (median)": window_centre(d["units"], "median", min_cell),
                   "propulsor types (mean)": window_centre(d["n_types"], "mean", min_cell),
                   "propulsor types (median)": window_centre(d["n_types"], "median", min_cell),
                   "tilting sets per propulsive unit (mean)": window_centre(spu, "mean", min_cell),
                   "share with two or more tilting sets": window_centre((d["sets"] >= 2).astype(float).where(d["sets"].notna()), "mean", min_cell),
                   "share with a fixed unit": window_centre(d["any_fixed"].map({True: 1.0, False: 0.0}).where(d["recorded"].fillna(False)), "mean", min_cell),
                   "share with units on booms": window_centre(onb, "mean", min_cell),
                   "share with a ducted unit": window_centre(duc, "mean", min_cell)}
            for tag, m in (("units on booms", onb.eq(1.0)), ("no units on booms", onb.eq(0.0))):
                row[f"aircraft, {tag}"] = int(m.sum())
                row[f"ducted share, {tag}"] = window_centre(duc[m], "mean", min_cell) if code == "CVT" else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def driver_links(cf: pd.DataFrame) -> pd.DataFrame:
    """The two chapter-3 links as small tests: Tilt Rotor units by tilting sets; CVT ducted share by boom layout.

    RULE: TR aircraft with units > 0 and >= 1 tilting set, grouped 1 / 2 / 3+ sets: n, median and mean (2 dp) of units.
    CVT aircraft: ducted share (mean 3 dp) and trend_test(year, ducted 0/1) inside 'units on booms', 'no units on booms'
    and 'all CVT' (every CVT aircraft with a ducted record).

    Ported from: archive sm_open.py:driver_links
    Used in: la_driver_links
    """
    rows = []
    tr = cf[cf["topType"].eq("TR") & cf["units"].gt(0) & cf["sets"].ge(1)]
    for label, m in (("1", tr["sets"].eq(1)), ("2", tr["sets"].eq(2)), ("3 or more", tr["sets"].ge(3))):
        s = tr.loc[m, "units"]
        rows.append({"link": "Tilt Rotor: propulsive units by tilting sets", "group": label,
                     "aircraft": int(len(s)), "median": float(s.median()) if len(s) else np.nan,
                     "mean": round(float(s.mean()), 2) if len(s) else np.nan,
                     "rho": np.nan, "p": np.nan, "movement": ""})
    cvt = cf[cf["topType"].eq("CVT")]
    duc = cvt["ducted"].map({True: 1.0, False: 0.0})
    onb = cvt["on_booms"].map({True: 1.0, False: 0.0})
    for label, m in (("units on booms", onb.eq(1.0)), ("no units on booms", onb.eq(0.0)),
                     ("all CVT", duc.notna())):
        t = trend_test(cvt.loc[m, "year"], pd.to_numeric(duc[m], errors="coerce"))
        rows.append({"link": "CVT: ducted share by boom layout", "group": label,
                     "aircraft": t["aircraft"], "median": np.nan,
                     "mean": round(float(duc[m].dropna().mean()), 3) if m.any() else np.nan,
                     "rho": t["rho"], "p": t["p"], "movement": t["movement"]})
    return pd.DataFrame(rows)
