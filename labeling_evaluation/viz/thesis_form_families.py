"""Form-defined families (hand-over 2026-10-16, Task 6): tests for the convergence of a dominant design on families declared by FORM
(wing, tilt, booms, propulsor band, enclosure), not by architecture. Exploratory; after Task 1; on the w15 weighting and nothing else.

Nothing here changes F or any number of the dissertation: F stays as decided on 2026-10-14. Every reading reuses the code paths of
Task 1 (``lib.dominant_design``, ``viz.frames``, ``viz.thesis_q7``, ``viz.analysis3``); this module only declares the families, builds
the form variables, regroups the same designs and writes the tables. Driven by notebook 55 (``notebooks/55_form_families.ipynb``).

Steps (the brief's numbering):

* 6.1 :func:`form_variables`: one row per design with an architecture (625), the form variables read off the w15 frame.
* 6.2 :data:`FAMILIES`: the five families P1-P5, fixed before any result was seen; :func:`membership`.
* 6.3a :func:`membership_tables`: family x architecture, per cohort, empennage inside the family; "renamed architecture" above 85 %.
* 6.3b :func:`premise_check`: cohesion and separation of each family per cohort against random subsets of the same size (1000
  permutations, seed 42); :func:`q_decomposition`: Q of a cohort split into within-family, within-rest and between pairs.
* 6.3c :func:`condition1`: the family's share per priority year on the code path of ``q7_condition1_family``.
* 6.3d :func:`condition2`: ²D rarefied to 40 against the band on the partition {family} ∪ {each remaining architecture}, as F.
* 6.3e :func:`condition3`: quoted from Task 1 per base (family-independent).
* 6.4 :func:`verdict_table`, :func:`numbers_md`, :func:`write_outputs`.
"""
from __future__ import annotations

import pathlib
import re
import shutil
from typing import Dict, List

import numpy as np
import pandas as pd

from lib import dominant_design as dd
from viz import analysis3, frames, thesis_q7
from viz import thesis_v2_part2 as p2
from viz.thesis_latex_common import root, tables_md

PERMS = thesis_q7.PERMS                 # 1000 (200 until 2026-10), as conditions 2 and 3 of Task 1
MIN_READ = 10                           # a family needs 10 designs in a cohort for the premise check (the min_aircraft of the Task 1 bands)
RENAMED_SHARE = 0.85                    # above this share of one architecture a family is that architecture renamed
BAND_LABELS = list(frames.ROTOR_BINS[1])        # rank 0..4 -> "1-3", "4", "5-6", "7-8", "9+"
BAND_5_6 = 2                            # the rank of "5-6": `band >= 5-6` is rank >= 2
BASES = (("all designs", None), ("actively protected", "in_force"))
_LVL = {"A0": "A", "A1t": "A·W·T", "A0c": "A·U", "family_b": "F"}
_MD_NAME = "NUMBERS_VI_form_families.md"

#: 6.2 the declared families: fixed before running; none added or tuned after seeing results.
FAMILIES = [
    dict(id="P1", name="fixed wing, boom-borne distributed propulsion",
         rule="wing_n >= 1 AND wing_tilts = no AND boom_n >= 1 AND band >= 5-6",
         premise="F in form terms: a lifting wing for range, many small propulsors on booms; unit tilt free"),
    dict(id="P2", name="fixed wing, distributed propulsion",
         rule="wing_n >= 1 AND wing_tilts = no AND band >= 5-6",
         premise="P1 without the boom rule"),
    dict(id="P3", name="fixed wing, open distributed propulsion",
         rule="P2 AND enclosure = not ducted",
         premise="ducted propulsors are a distinct form"),
    dict(id="P4", name="wingless multicopter, distributed",
         rule="wing_n = 0 AND band >= 5-6 AND enclosure = not ducted",
         premise="the Multicopter counterpart of P3"),
    dict(id="P5", name="fixed wing with distributed propulsion, any tilt",
         rule="wing_n >= 1 AND band >= 5-6",
         premise="upper bound, includes Tilt Wing and Tilt Frame"),
]
FAMILY_IDS = [f["id"] for f in FAMILIES]
#: the form variables each rule reads (a design with any of them blank is not a member)
RULE_VARS = {"P1": ["wing_n", "wing_tilts", "boom_n", "band"], "P2": ["wing_n", "wing_tilts", "band"],
             "P3": ["wing_n", "wing_tilts", "band", "enclosure"], "P4": ["wing_n", "band", "enclosure"], "P5": ["wing_n", "band"]}


def arch_name(code: str) -> str:
    """The architecture's full name in prose (Separate Lift + Cruise, Combined Vectored Thrust, Multicopter, ...)."""
    return "Separate Lift + Cruise" if code == "SLC" else p2.arch(code).name


def family_label(fid: str) -> str:
    return f"{fid} {next(f['name'] for f in FAMILIES if f['id'] == fid)}"


# ------------------------------------------------------------------------------------------------------ cache per context
def _cache(ctx) -> dict:
    if getattr(ctx, "_form_families", None) is None:
        ctx._form_families = {}
    return ctx._form_families


# ------------------------------------------------------------------------------------------------------ 6.1 form variables
def form_variables(ctx) -> pd.DataFrame:
    """One row per design with an architecture (the 625 of the w15 frame): ``topType``, ``wing_n`` (wCount, 0 when no wing; blank under
    an M2 override), ``wing_tilts`` (yes when any ``wing{k}_tilt`` is Tilt; blank with ``wing_n``), ``boom_n`` (boom1..6_count summed, 0 when
    ``boomsPresent`` is not True: the raw total, not the w15 rank), ``band`` (the w15 propulsor band as a label 1-3, 4, 5-6, 7-8, 9+; blank when
    the count is not determinable or the design has no propulsor card), ``band_rank`` (0..4), ``tilt_share`` (the w15 definition),
    ``enclosure`` (the w15 Propulsor Enclosure of the set with most propulsors: Ducted or Open), ``mounts`` (the w15 mount locations joined
    by '/'), ``empType``; plus ``year``, ``window`` and ``in_force`` (actively protected) for the readings."""
    c = _cache(ctx)
    if "fv" in c:
        return c["fv"]
    ds, v = ctx.ds, ctx.v
    f15 = frames.form_frame15(ds).set_index("aircraft_id")
    raw = ds.variants.set_index("aircraft_id").loc[f15.index]
    boom_cols = [col for col in raw.columns if re.match(r"boom\d_count$", col)]
    nbooms = raw[boom_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    nbooms = nbooms.where(raw["boomsPresent"].map(frames._s).eq("True"), 0).astype(int)
    tilts = pd.Series(False, index=raw.index)
    for k in range(1, 5):
        col = f"wing{k}_tilt"
        if col in raw.columns:
            tilts |= raw[col].map(frames._s).eq("Tilt")
    wing_n = f15["Wing count"]
    out = pd.DataFrame({"aircraft_id": f15.index, "topType": f15["Architecture"].to_numpy(),
                        "wing_n": wing_n.to_numpy(),
                        "wing_tilts": np.where(wing_n.notna(), np.where(tilts, "yes", "no"), None),
                        "boom_n": nbooms.to_numpy(),
                        "band": f15["Propulsor band"].map(lambda r: BAND_LABELS[int(r)] if pd.notna(r) else None).to_numpy(),
                        "band_rank": f15["Propulsor band"].to_numpy(),
                        "tilt_share": f15["Tilt share"].round(4).to_numpy(),
                        "enclosure": f15["Propulsor Enclosure"].map(lambda x: x if isinstance(x, str) else None).to_numpy(),
                        "mounts": f15["Mount locations"].map(lambda s: "/".join(sorted(s)) if isinstance(s, frozenset) else None).to_numpy(),
                        "empType": f15["Empennage Type"].map(lambda x: x if isinstance(x, str) else None).to_numpy()})
    state = frames.patent_state(ds, v)
    meta = v.set_index("aircraft_id")[["year", "window"]]
    out = out.join(meta, on="aircraft_id")
    out["in_force"] = out["aircraft_id"].map(state["in_force"]).fillna(False).astype(bool)
    out = out.reset_index(drop=True)
    c["fv"] = out
    return out


# ------------------------------------------------------------------------------------------------------ 6.2 membership
def membership(ctx) -> pd.DataFrame:
    """The form variables with one boolean column per family (P1..P5) and one ``<id>_blank`` column saying a rule variable of the design is
    blank (hidden by an override, or no propulsor card / count): such a design is not a member."""
    c = _cache(ctx)
    if "mem" in c:
        return c["mem"]
    fv = form_variables(ctx).copy()
    wn, bn, br = fv["wing_n"], fv["boom_n"], fv["band_rank"]
    fixed = fv["wing_tilts"].eq("no")
    open_ = fv["enclosure"].eq("Open")
    rules = {"P1": wn.ge(1) & fixed & bn.ge(1) & br.ge(BAND_5_6),
             "P2": wn.ge(1) & fixed & br.ge(BAND_5_6),
             "P3": wn.ge(1) & fixed & br.ge(BAND_5_6) & open_,
             "P4": wn.eq(0) & br.ge(BAND_5_6) & open_,
             "P5": wn.ge(1) & br.ge(BAND_5_6)}
    for fid in FAMILY_IDS:
        blank = fv[RULE_VARS[fid]].isna().any(axis=1)
        fv[fid] = (rules[fid] & ~blank).astype(bool)
        fv[f"{fid}_blank"] = blank.astype(bool)
    c["mem"] = fv
    return fv


def declared_families() -> pd.DataFrame:
    return pd.DataFrame(FAMILIES)[["id", "name", "rule", "premise"]]


def _base_mask(fv: pd.DataFrame, state) -> pd.Series:
    return fv["in_force"] if state == "in_force" else pd.Series(True, index=fv.index)


# ------------------------------------------------------------------------------------------------------ 6.3a membership tables
def membership_tables(ctx) -> Dict[str, pd.DataFrame]:
    """``summary``: per family and base the size, the designs left out for a blank rule variable, the top architecture and its share and
    whether the family is that architecture renamed (share above 85 %). ``long``: per family and base the crosstab family x architecture
    (kind ``architecture``), the designs per cohort (kind ``cohort``) and the empennage distribution inside the family (kind ``empennage``),
    one row per value with the count and the share of the family."""
    c = _cache(ctx)
    if "memtab" in c:
        return c["memtab"]
    fv = membership(ctx)
    summ, long = [], []
    for fid in FAMILY_IDS:
        for base, st in BASES:
            b = fv[_base_mask(fv, st)]
            m = b[b[fid]]
            n = len(m)
            arch = m["topType"].value_counts()
            top, top_n = (str(arch.index[0]), int(arch.iloc[0])) if n else ("", 0)
            summ.append({"family": fid, "name": family_label(fid)[3:], "base": base, "designs in base": len(b), "members": n,
                         "share of base": round(n / len(b), 4) if len(b) else np.nan,
                         "not members for a blank rule variable": int(b[f"{fid}_blank"].sum()),
                         "top architecture": top, "top architecture designs": top_n,
                         "top architecture share": round(top_n / n, 4) if n else np.nan,
                         "renamed architecture (> 85 %)": bool(n and top_n / n > RENAMED_SHARE),
                         "architectures (code: designs)": "; ".join(f"{k}: {int(x)}" for k, x in arch.items())})
            for code, x in arch.items():
                long.append({"family": fid, "base": base, "kind": "architecture", "value": code, "designs": int(x), "share of family": round(x / n, 4)})
            for w in ctx.WIN_NAMES:
                x = int(m["window"].eq(w).sum())
                long.append({"family": fid, "base": base, "kind": "cohort", "value": w, "designs": x, "share of family": round(x / n, 4) if n else np.nan})
            emp = m["empType"].fillna("blank").value_counts()
            for e, x in emp.items():
                long.append({"family": fid, "base": base, "kind": "empennage", "value": e, "designs": int(x), "share of family": round(x / n, 4)})
    out = {"summary": pd.DataFrame(summ), "long": pd.DataFrame(long)}
    c["memtab"] = out
    return out


def crosstab(ctx, base: str = "all designs") -> pd.DataFrame:
    """Family x architecture crosstab (codes in the columns) on one base, families as rows; last column the family size."""
    fv = membership(ctx)
    st = dict(BASES)[base]
    b = fv[_base_mask(fv, st)]
    rows = {fid: b.loc[b[fid], "topType"].value_counts() for fid in FAMILY_IDS}
    codes = [k for k in frames.CH3B_CLASSES] + sorted(set(b["topType"]) - set(frames.CH3B_CLASSES))
    t = pd.DataFrame(rows).T.reindex(columns=codes).fillna(0).astype(int)
    t.insert(0, "family", t.index)
    t["members"] = t[codes].sum(axis=1)
    return t.reset_index(drop=True)


# ------------------------------------------------------------------------------------------------------ 6.3b premise check
def _distance(ctx):
    c = _cache(ctx)
    if "D" not in c:
        D, frame = frames.form_distance(ctx.ds)                  # w15, the main weighting; the only one read here
        c["D"], c["at"] = D, {a: i for i, a in enumerate(frame["aircraft_id"].to_numpy())}
    return c["D"], c["at"]


def _offdiag_mean(D: np.ndarray, idx: np.ndarray) -> float:
    """Mean distance over the unordered pairs of ``idx`` (diagonal left out); NaN with fewer than 2 designs."""
    if len(idx) < 2:
        return float("nan")
    sub = D[np.ix_(idx, idx)]
    n = len(idx)
    return float((np.nansum(sub) - np.nansum(np.diag(sub))) / (n * (n - 1)))


def _between_mean(D: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    return float(np.nanmean(D[np.ix_(a, b)]))


def premise_check(ctx) -> pd.DataFrame:
    """Per family, base and cohort: cohesion = mean w15 Gower distance over the pairs of the family's designs in the cohort (diagonal
    left out) against the 2.5-97.5 % band of the same mean on PERMS (1000) random subsets of the cohort's designs of the family's size (seed 42,
    one fresh generator per family and base); separation = mean distance from the family's designs to the rest of the cohort against the
    band of the same statistic on the same random subsets. The premise holds in a cohort when cohesion is below its band AND separation is
    above its band. A family with fewer than MIN_READ designs in the cohort, or no rest, is not read."""
    c = _cache(ctx)
    if "premise" in c:
        return c["premise"]
    D, at = _distance(ctx)
    fv = membership(ctx)
    fv = fv[fv["window"].notna()]
    rows = []
    for fid in FAMILY_IDS:
        for base, st in BASES:
            rng = np.random.default_rng(ctx.SEED)
            b = fv[_base_mask(fv, st)]
            for w in ctx.WIN_NAMES:
                coh = b[b["window"].eq(w)]
                idx = coh["aircraft_id"].map(at).to_numpy(dtype=int)
                is_f = coh[fid].to_numpy(bool)
                fam, rest = idx[is_f], idx[~is_f]
                n, nf = len(idx), len(fam)
                r = {"family": fid, "base": base, "cohort": w, "partial": "partial" in w, "designs in cohort": n, "family designs": nf,
                     "rest designs": len(rest), "read": bool(nf >= MIN_READ and len(rest) >= 1)}
                if r["read"]:
                    coh_v, sep_v = _offdiag_mean(D, fam), _between_mean(D, fam, rest)
                    cb, sb = [], []
                    for _ in range(PERMS):
                        pick = rng.choice(n, size=nf, replace=False)
                        mask = np.zeros(n, dtype=bool)
                        mask[pick] = True
                        cb.append(_offdiag_mean(D, idx[mask]))
                        sb.append(_between_mean(D, idx[mask], idx[~mask]))
                    cb, sb = np.array(cb), np.array(sb)
                    r.update({"cohesion": round(coh_v, 4), "cohesion band low": round(float(np.percentile(cb, 2.5)), 4),
                              "cohesion band high": round(float(np.percentile(cb, 97.5)), 4), "cohesion below band": bool(coh_v < np.percentile(cb, 2.5)),
                              "separation": round(sep_v, 4), "separation band low": round(float(np.percentile(sb, 2.5)), 4),
                              "separation band high": round(float(np.percentile(sb, 97.5)), 4), "separation above band": bool(sep_v > np.percentile(sb, 97.5))})
                    r["premise holds"] = bool(r["cohesion below band"] and r["separation above band"])
                else:
                    r.update({k: np.nan for k in ("cohesion", "cohesion band low", "cohesion band high", "separation", "separation band low", "separation band high")})
                    r.update({"cohesion below band": None, "separation above band": None, "premise holds": None})
                rows.append(r)
    out = pd.DataFrame(rows)
    c["premise"] = out
    return out


def q_decomposition(ctx) -> pd.DataFrame:
    """Q of each complete cohort (all designs, w15) split by family into three blocks of ordered pairs: within-family, within-rest and
    between (family-rest and rest-family). Q is Task 1's definition (:func:`lib.dominant_design.mean_pairwise_distance`: the mean of D over
    all ordered pairs, diagonal included), so share of pairs x mean distance of each block sums exactly to Q. ``change 2020-23`` = the
    block's contribution in 2020-23 minus its mean over the two earliest cohorts (the reference of ΔQ in Task 1): which pairs carry ΔQ."""
    c = _cache(ctx)
    if "qdec" in c:
        return c["qdec"]
    D, at = _distance(ctx)
    fv = membership(ctx)
    fv = fv[fv["window"].notna()]
    rows = []
    for fid in FAMILY_IDS:
        for w in ctx.COMPLETE:
            coh = fv[fv["window"].eq(w)]
            idx = coh["aircraft_id"].map(at).to_numpy(dtype=int)
            is_f = coh[fid].to_numpy(bool)
            fam, rest = idx[is_f], idx[~is_f]
            n, nf, nr = len(idx), len(fam), len(rest)
            Q = dd.mean_pairwise_distance(D, idx)
            blocks = {"within family": (D[np.ix_(fam, fam)], nf * nf), "within rest": (D[np.ix_(rest, rest)], nr * nr),
                      "between": (D[np.ix_(fam, rest)], 2 * nf * nr)}
            for blk, (sub, pairs) in blocks.items():
                mean = float(np.nanmean(sub)) if pairs else float("nan")
                share = pairs / (n * n)
                rows.append({"family": fid, "cohort": w, "designs": n, "family designs": nf, "block": blk, "pairs": pairs,
                             "share of pairs": round(share, 4), "mean distance": round(mean, 4) if pairs else np.nan,
                             "contribution to Q": round(share * mean, 4) if pairs else 0.0, "Q of cohort": round(Q, 4)})
    out = pd.DataFrame(rows)
    ref = out[out["cohort"].isin(ctx.COMPLETE[:2])].groupby(["family", "block"])["contribution to Q"].mean()
    out["contribution, mean of the two earliest cohorts"] = [round(float(ref[(f, b)]), 4) for f, b in zip(out["family"], out["block"])]
    out["change 2020-23"] = np.where(out["cohort"].eq("2020-23"), (out["contribution to Q"] - out["contribution, mean of the two earliest cohorts"]).round(4), np.nan)
    c["qdec"] = out
    return out


# ------------------------------------------------------------------------------------------------------ 6.3c condition 1
def condition1(ctx) -> Dict[str, object]:
    """The family's share per priority year on both bases, the same code path as ``q7_condition1_family`` (the base of F: every design with
    an architecture; :func:`lib.dominant_design.family_share_by_year` with DD_YEAR_FIRST..last complete year and DD_YEAR_MIN = 20 read years);
    years met = :func:`lib.dominant_design.condition1_years` on ``read`` and ``above 50 %``; three consecutive years as sensitivity
    (:func:`viz.analysis3.runs`). Returns ``yearly`` (long table) and ``met`` {(family, base): {"two": [...], "three": [...]}}."""
    c = _cache(ctx)
    if "c1" in c:
        return c["c1"]
    fv = membership(ctx)
    last = ctx.cfg.analysis["last_complete_year"]
    years = range(frames.DD_YEAR_FIRST, last + 1)
    tabs, met = [], {}
    for fid in FAMILY_IDS:
        for base, st in BASES:
            b = fv[_base_mask(fv, st)]
            t = dd.family_share_by_year(b[fid].astype(bool), b["year"], years, frames.DD_YEAR_MIN)
            t = t.rename(columns={"F aircraft": "family designs", "F share": "family share", "aircraft": "designs"})
            t["above 50 %"] = t["read"].astype(bool) & t["family share"].gt(0.5)
            yrs = sorted(dd.condition1_years(t.rename(columns={"designs": "aircraft"})))
            three = analysis3.runs(t.loc[t["above 50 %"], "priority year"], analysis3.RUN3)
            met[(fid, base)] = {"two": yrs, "three": three}
            t.insert(0, "base", base)
            t.insert(0, "family", fid)
            tabs.append(t)
    out = {"yearly": pd.concat(tabs, ignore_index=True), "met": met}
    c["c1"] = out
    return out


# ------------------------------------------------------------------------------------------------------ 6.3d condition 2
def condition2(ctx) -> pd.DataFrame:
    """Condition 2 per family and base: ²D rarefied to 40 against the 1000-permutation band (seed 42, a fresh generator per family and base,
    as F), on the partition {family} ∪ {each remaining architecture as its own option}: the key is the design's architecture code, replaced by
    the family's id for its members; designs with a blank rule variable keep their architecture. Exactly :func:`frames.dd_level_keys`'s
    construction of F's key, with the family's member set, then :func:`lib.dominant_design.balance_band`."""
    c = _cache(ctx)
    if "c2" in c:
        return c["c2"]
    fv = membership(ctx)
    fv = fv[fv["window"].notna()]
    out = []
    for fid in FAMILY_IDS:
        for base, st in BASES:
            b = fv[_base_mask(fv, st)]
            key = b["topType"].astype(object).where(~b[fid], family_label(fid))
            t = dd.balance_band(key, b["window"], ctx.WIN_NAMES, n=ctx.cfg.analysis["rarefy_n"], perms=PERMS, seed=ctx.SEED)
            t.insert(0, "partition", f"{{{fid}}} ∪ {{each remaining architecture}}")
            t.insert(0, "base", base)
            t.insert(0, "family", fid)
            out.append(t)
    out = pd.concat(out, ignore_index=True).rename(columns={"window": "cohort", "aircraft": "designs", "top archetype": "top option"})
    out["partial"] = out["cohort"].astype(str).str.contains("partial")
    c["c2"] = out
    return out


# ------------------------------------------------------------------------------------------------------ 6.3e condition 3
def condition3(ctx) -> pd.DataFrame:
    """Condition 3 as Task 1 read it (w15, complete cohorts), per base and level: ΔQ of 2020-23 against the lower edge of its band and
    the cohorts below the band. Rao's Q is cohort-wide and blind to the family, so it is never recomputed per family: this table is
    family-independent and the verdict quotes it for every family."""
    c = _cache(ctx)
    if "c3" in c:
        return c["c3"]
    main = frames.Q_WEIGHTINGS[0]
    rows = []
    for base, (_, form) in analysis3._base_frames(ctx).items():
        fm = form[form["weighting"].eq(main) & form["window"].isin(ctx.COMPLETE)]
        for lvl, name in _LVL.items():
            t = fm[fm["level"].eq(lvl)]
            below = t[t["below band"].astype(str).eq("True")]["window"].tolist()
            q = t[t["window"].eq("2020-23")]
            rows.append({"base": base, "level": name, "weighting": main, "ΔQ 2020-23": float(q["ΔQ"].iloc[0]),
                         "ΔQ lower band edge 2020-23": float(q["ΔQ permutation low"].iloc[0]),
                         "below band 2020-23": bool(q["below band"].astype(str).eq("True").iloc[0]),
                         "cohorts met": ", ".join(below) or "none", "family-independent": True})
    out = pd.DataFrame(rows)
    c["c3"] = out
    return out


# ------------------------------------------------------------------------------------------------------ 6.4 verdict
_pc = lambda x: f"{100 * x:.1f} %"                                                      # noqa: E731
_and = lambda ys: " and ".join(map(str, ys)) if len(ys) <= 2 else ", ".join(map(str, ys[:-1])) + " and " + str(ys[-1])   # noqa: E731


def _cells(ctx) -> Dict[tuple, dict]:
    """Per (family, base) the printed cell of every row of the verdict table and the numbers behind them."""
    frames.set_window_bounds(ctx.cfg)
    wof = lambda yy: next(w for w, lo, hi in frames._WIN_BOUNDS if lo <= yy <= hi)      # noqa: E731
    c1, c2, c3, pr = condition1(ctx), condition2(ctx), condition3(ctx), premise_check(ctx)
    out = {}
    for fid in FAMILY_IDS:
        for base, _ in BASES:
            y = c1["yearly"]
            y = y[y["family"].eq(fid) & y["base"].eq(base) & y["read"].astype(bool)]
            yrs, three = c1["met"][(fid, base)]["two"], c1["met"][(fid, base)]["three"]
            sh = dict(zip(y["priority year"].astype(int), y["family share"].astype(float)))
            top = y.loc[y["family share"].astype(float).idxmax()] if len(y) else None
            cell1 = (("✓ met in " + _and(yrs) + " (" + ", ".join(_pc(sh[x]) for x in yrs) + ")") if yrs else
                     (f"✗ not met, at most {_pc(float(top['family share']))} ({int(top['priority year'])})" if top is not None else "✗ not met, no read year"))
            b2 = c2[c2["family"].eq(fid) & c2["base"].eq(base) & c2["cohort"].isin(ctx.COMPLETE)]
            below2 = b2[b2["below band"].astype(bool)]["cohort"].tolist()
            t3 = c3[c3["base"].eq(base) & c3["level"].eq("A")].iloc[0]
            below3 = [w for w in t3["cohorts met"].split(", ") if w and w != "none"]
            inside = dd.all_three_windows(set(yrs), set(below2), set(below3), wof)
            p = pr[pr["family"].eq(fid) & pr["base"].eq(base) & pr["cohort"].eq("2020-23")].iloc[0]
            pw = pr[pr["family"].eq(fid) & pr["base"].eq(base) & pr["read"].astype(bool) & ~pr["partial"]]
            holds = pw[pw["premise holds"].astype(bool)]["cohort"].tolist()
            fmt = lambda v, lo, hi: f"{v:.4f} (band {lo:.4f} to {hi:.4f})"             # noqa: E731
            out[(fid, base)] = {
                "cohesion": (fmt(p["cohesion"], p["cohesion band low"], p["cohesion band high"]) + (" ✓ below" if p["cohesion below band"] else " ✗ not below")) if p["read"] else "not read",
                "separation": (fmt(p["separation"], p["separation band low"], p["separation band high"]) + (" ✓ above" if p["separation above band"] else " ✗ not above")) if p["read"] else "not read",
                "premise": ("✓ holds in " + ", ".join(holds)) if holds else "✗ does not hold",
                "1": cell1, "1 three-year": ("✓ " + ", ".join(map(str, three))) if three else "✗ not met",
                "2": ("✓ met in " + ", ".join(below2)) if below2 else "✗ not met",
                "3": ("✓ met in " + ", ".join(below3)) if below3 else "✗ not met",
                "all": ("✓ met in " + ", ".join(inside)) if inside else "✗ not met",
                "_yrs": yrs, "_three": three, "_below2": below2, "_below3": below3, "_inside": inside, "_holds": holds,
                "_top": (float(top["family share"]), int(top["priority year"])) if top is not None else (np.nan, None),
                "_sh": sh, "_n": dict(zip(y["priority year"].astype(int), y["designs"].astype(int))),
                "_fam_n": dict(zip(y["priority year"].astype(int), y["family designs"].astype(int))),
                "_p": p, "_c3": t3}
    return out


ROWS = [("premise: cohesion 2020-23", "cohesion"), ("premise: separation 2020-23", "separation"),
        ("premise: cohesion below AND separation above the band (complete cohorts)", "premise"),
        ("1, counts: the family above 50 % of the designs, two consecutive priority years", "1"),
        ("1, sensitivity: three consecutive priority years", "1 three-year"),
        ("2, balance: ²D below the permutation band, partition {family} ∪ {each remaining architecture}", "2"),
        ("3, form: Q below the two earliest cohorts by more than the band (Task 1, level A; family-independent)", "3"),
        ("all three in the same period", "all")]


def verdict_table(ctx) -> pd.DataFrame:
    """The shape of ``q7_verdict_table.csv`` (base, condition, one column per family) with the cohesion and separation rows added."""
    c = _cache(ctx)
    if "verdict" in c:
        return c["verdict"]
    cells = _cells(ctx)
    rows = [{"base": base, "condition": label, **{fid: cells[(fid, base)][key] for fid in FAMILY_IDS}}
            for base, _ in BASES for label, key in ROWS]
    out = pd.DataFrame(rows)
    c["verdict"] = out
    return out


def verdict_md_table(ctx, base: str) -> pd.DataFrame:
    """The md's verdict table on one base: rows P1-P5; premise, condition 1 (largest share and years met), condition 2 cohorts met,
    condition 3 cohort verdict, all three same period."""
    cells = _cells(ctx)
    rows = []
    for fid in FAMILY_IDS:
        ce = cells[(fid, base)]
        top, yr = ce["_top"]
        rows.append({"family": fid, "premise": ce["premise"],
                     "condition 1: largest share (year); years met": f"{_pc(top)} ({yr}); " + (", ".join(map(str, ce["_yrs"])) or "none"),
                     "condition 2: cohorts met": ", ".join(ce["_below2"]) or "none",
                     "condition 3 (cohort verdict, family-independent)": ce["3"],
                     "all three, same period": ce["all"]})
    return pd.DataFrame(rows)


def _paragraph(ctx, fid: str, base: str) -> str:
    cells = _cells(ctx)[(fid, base)]
    ms = membership_tables(ctx)["summary"]
    s = ms[ms["family"].eq(fid) & ms["base"].eq(base)].iloc[0]
    fam = next(f for f in FAMILIES if f["id"] == fid)
    fv = membership(ctx)
    b = fv[_base_mask(fv, dict(BASES)[base])]
    m = b[b[fid]]
    arch = m["topType"].value_counts()
    joins = ", ".join(f"{arch_name(k)} {int(x)}" for k, x in arch.items())
    renamed = (f" More than 85 % of it is one architecture, so it is {arch_name(s['top architecture'])} renamed."
               if s["renamed architecture (> 85 %)"] else
               f" Its largest architecture is {arch_name(s['top architecture'])} at {_pc(s['top architecture share'])}, so it is not one architecture renamed.")
    emp = m["empType"].fillna("blank").value_counts()
    emp_s = ", ".join(f"{k} {int(x)}" for k, x in emp.head(4).items())
    p = cells["_p"]
    prem = (f"In 2020-23 its cohesion is {p['cohesion']:.4f} against a band of {p['cohesion band low']:.4f} to {p['cohesion band high']:.4f} "
            f"({'below' if p['cohesion below band'] else 'not below'}) and its separation {p['separation']:.4f} against {p['separation band low']:.4f} to "
            f"{p['separation band high']:.4f} ({'above' if p['separation above band'] else 'not above'}); the premise "
            + (("holds in " + ", ".join(cells["_holds"])) if cells["_holds"] else "does not hold in any complete cohort") + ".") if p["read"] else \
        "It has too few designs in 2020-23 for the premise check."
    top, yr = cells["_top"]
    sh, nn, fn = cells["_sh"], cells["_n"], cells["_fam_n"]
    if cells["_yrs"]:
        c1 = "Condition 1 is met in " + _and(cells["_yrs"]) + " (" + "; ".join(f"{_pc(sh[y])}: {fn[y]} of {nn[y]}" for y in cells["_yrs"]) + ")"
        c1 += (", and with three consecutive years in " + ", ".join(map(str, cells["_three"]))) if cells["_three"] else ", but not with three consecutive years"
        c1 += "."
    else:
        need = [(y, int(np.floor(nn[y] / 2)) + 1 - fn[y]) for y in sorted(nn) if y >= 2016]
        short = "; ".join(f"{y}: {_pc(sh[y])}, {d} more design{'s' if d != 1 else ''} needed" for y, d in need if d > 0)
        c1 = f"Condition 1 is not met: its largest share of a read year is {_pc(top)} in {yr} ({short})."
    c2 = ("Condition 2 is met in " + ", ".join(cells["_below2"])) if cells["_below2"] else "Condition 2 is not met in any complete cohort"
    c2 += " on the partition {" + fid + "} ∪ {each remaining architecture}."
    t3 = cells["_c3"]
    c3 = (f"Condition 3 is the cohort verdict of Task 1 on this base, independent of the family: ΔQ 2020-23 {t3['ΔQ 2020-23']:+.4f} against a lower band edge of "
          f"{t3['ΔQ lower band edge 2020-23']:+.4f}, {'met' if t3['below band 2020-23'] else 'not met'}.")
    allv = ("All three hold in the same period: " + ", ".join(cells["_inside"]) + ".") if cells["_inside"] else "The three conditions do not hold in the same period, so the family is not a dominant design on this base."
    return (f"**{fid}, {fam['name']}** ({fam['rule']}). On {base} it joins {int(s['members'])} designs ({_pc(s['share of base'])} of {int(s['designs in base'])}): {joins}; "
            f"{int(s['not members for a blank rule variable'])} designs are not members because a rule variable is blank.{renamed} Empennage inside the family: {emp_s}. "
            f"{prem} {c1} {c2} {c3} {allv}")


def numbers_md(ctx) -> str:
    c3 = condition3(ctx)
    qd = q_decomposition(ctx)
    ms = membership_tables(ctx)["summary"]
    L = ["# NUMBERS_VI — form-defined families (Task 6, exploratory)\n",
         "Written by notebook 55 (`viz/thesis_form_families.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/` "
         "(`q8_form_variables.csv`, `q8_families_membership.csv`, `q8_families_premise.csv`, `q8_families_q_decomposition.csv`, `q8_families_condition1.csv`, "
         "`q8_families_condition2.csv`, `q8_families_condition3.csv`, `q8_families_verdict.csv`).\n",
         "Exploratory, after Task 1, on the w15 weighting only. Nothing here changes F or any number of the dissertation (F stays as decided on 2026-10-14). "
         "The question: is there a family defined by form (wing, tilt, booms, propulsor count, enclosure), not by architecture, that is coherent in form AND meets "
         "share dominance (condition 1) and balance reduction (condition 2)? Condition 3 (Rao's Q) is cohort-wide and blind to the family, so it is never recomputed "
         "per family: the Task 1 cohort verdict is quoted per base. \"Met\" only when all three hold in the same period on the same base.\n",
         "## Declared families (fixed before running; none added or tuned after seeing results)\n", tables_md(declared_families()), "",
         "Rule variables: wing_n (wCount, 0 when no wing), wing_tilts (any wing panel Tilt), boom_n (boom1..6_count summed, 0 without booms), band (propulsor band 1-3, 4, 5-6, 7-8, 9+), "
         "enclosure (of the set with most propulsors). Empennage type is never a membership rule. A design whose rule variable is blank (hidden by an override, or no propulsor card / count) is not a member.\n",
         "## Membership (size, largest architecture, renamed?)\n", "Source: `q8_families_membership.csv` (summary rows) and the crosstabs below.\n",
         tables_md(ms[["family", "base", "designs in base", "members", "share of base", "not members for a blank rule variable", "top architecture", "top architecture share", "renamed architecture (> 85 %)"]]), "",
         "Family x architecture, all designs (codes):\n", tables_md(crosstab(ctx, "all designs")), "",
         "Family x architecture, actively protected (codes):\n", tables_md(crosstab(ctx, "actively protected")), ""]
    for base, _ in BASES:
        L += [f"## Verdict table, {base}" + (" (main)" if base == "all designs" else " (sensitivity)") + "\n",
              "Source: `q8_families_verdict.csv`. Premise = cohesion below AND separation above the band of 1000 random subsets of the cohort of the family's size (seed 42); "
              "condition 1 read years only (20 designs or more), two consecutive years above 50 %; condition 2 ²D rarefied to 40 against the 1000-permutation band on the partition "
              "{family} ∪ {each remaining architecture as its own option}, complete cohorts; condition 3 = Task 1, level A, w15, family-independent.\n",
              tables_md(verdict_md_table(ctx, base)), ""]
        for fid in FAMILY_IDS:
            L += [_paragraph(ctx, fid, base), ""]
    L += ["## Condition 3 as quoted (Task 1, w15, complete cohorts; family-independent)\n", "Source: `q8_families_condition3.csv` (from `q7_condition3_cohesion.csv` / the verdict detail of Task 1).\n", tables_md(c3), "",
          "## Which pairs carry ΔQ (all designs, w15): Q of each complete cohort split into within-family, within-rest and between pairs\n",
          "Source: `q8_families_q_decomposition.csv`. Q is Task 1's definition (mean of the distance over all ordered pairs of the cohort, diagonal included), so the three contributions sum to Q; "
          "`change 2020-23` is the block's contribution in 2020-23 minus its mean over the two earliest cohorts (the reference of Task 1's ΔQ).\n",
          tables_md(qd[qd["cohort"].eq("2020-23")][["family", "cohort", "designs", "family designs", "block", "share of pairs", "mean distance", "contribution to Q", "contribution, mean of the two earliest cohorts", "change 2020-23", "Q of cohort"]]), ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------------ outputs
def out_dir(cfg) -> pathlib.Path:
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_III_dominant_design" / "III3_form_families" / "exploratory"


def tables(ctx) -> Dict[str, pd.DataFrame]:
    """Every csv of Task 6 by file name (without extension)."""
    mt = membership_tables(ctx)
    long = mt["long"].copy()
    summ = mt["summary"].copy()
    summ.insert(2, "kind", "summary")
    return {"q8_form_variables": form_variables(ctx),
            "q8_families_membership": pd.concat([summ, long], ignore_index=True, sort=False),
            "q8_families_premise": premise_check(ctx),
            "q8_families_q_decomposition": q_decomposition(ctx),
            "q8_families_condition1": condition1(ctx)["yearly"],
            "q8_families_condition2": condition2(ctx),
            "q8_families_condition3": condition3(ctx),
            "q8_families_verdict": verdict_table(ctx)}


def write_outputs(ctx, task: str = "task6") -> List[pathlib.Path]:
    """Write every csv and the md to the results folder, copy the csvs to LaTeX_v15/Data_for_writing/csv/ and the md to LaTeX_v15/Data_for_writing/,
    and copy everything plus this module and notebook 55 to handoff_2026-10-16/task6/."""
    from viz import handoff_2026_10_16 as ho
    cfg = ctx.cfg
    od = out_dir(cfg)
    od.mkdir(parents=True, exist_ok=True)
    R = root(cfg)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    written = []
    for name, t in tables(ctx).items():
        t.to_csv(od / f"{name}.csv", index=False)
        shutil.copy2(od / f"{name}.csv", csvd / f"{name}.csv")
        written += [od / f"{name}.csv", csvd / f"{name}.csv"]
    md = numbers_md(ctx)
    (od / _MD_NAME).write_text(md, encoding="utf-8")
    shutil.copy2(od / _MD_NAME, R / "Data_for_writing" / _MD_NAME)
    written += [od / _MD_NAME, R / "Data_for_writing" / _MD_NAME]
    written += ho.plain_copies(task, [od / f"{n}.csv" for n in tables(ctx)] + [od / _MD_NAME])
    written += ho.copy_scripts(task, ["viz/thesis_form_families.py", "notebooks/55_form_families.ipynb"])
    return written
