"""Read the wizard exports ``labels/reviewed_patents_Batch_0N.xlsx`` directly.

This is the ``batch_xlsx`` source of :func:`loaders.load_dataset`: the same
long-to-wide reshaping that ``Patent-Labelling-Tools/notebooks/04_master_labels``
performs, re-done here so the analysis rests on the batch files themselves and
not on 04's output. The two deliberately differ in three places, all of them
*values*:

* no re-codes (04 applies documented one-off corrections, e.g. one ``wing1_plan``
  ``Oth -> Trap``); here a value is what the batch file holds;
* no ``*_otherTag`` columns (04 maps every ``Other`` note to a tag from a CSV);
* rejected records keep whatever morphology they carry (04 blanks it) — the
  analysis set is approved-and-primary, so it never sees them either way.

Everything else follows 04 line for line: the ``" — "`` label separator is
stripped from coded columns, a count of 1 stored as ``True`` becomes 1, D1/D2
duplicates inherit G1–M3 from their chain root and are not primary, a D3 keeps
its own labels and is primary, ``(fig N)`` placeholder blocks are dropped, and
the per-variant figure counts are computed from the T2 rows.

The schema (which columns are coded, their option labels) still comes from
``joined/data_dictionary.csv``: that file describes the wizard, not the data.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

SEP = " — "
SECTIONS_PATENT = ("T1", "META")
SECTIONS_VARIANT = ("G1", "M1", "M2", "M3")

#: (wizard Field, master column) at patent level — the order 04 uses
PATENT_COLS = [
    ("isApproved", "is_approved"), ("aircraftName", "aircraft_name"), ("assignee", "assignee"),
    ("title", "title"), ("app_year", "app_year"), ("pub_year", "pub_year"), ("pdf_link", "pdf_link"),
    ("archCount", "n_variants_declared"),
    ("isDuplicate", "is_duplicate"), ("duplicateType", "dup_type"), ("duplicateId", "dup_of"),
    ("t1DisapproveReason", "reason_human"), ("t1DisapproveReason_otherNote", "reason_note"),
    ("imgNotReflect", "img_not_reflect"),
    ("t1_humanUncertain", "t1_humanUncertain"), ("t1_uncertainNote", "t1_uncertainNote"),
    ("t1_quickOverride", "t1_quickOverride"), ("t1_quickNote", "t1_quickNote"),
]
LEGACY_MERGE = {"disapproveOther": "reason_note"}
#: retired / structural variant fields that get no column (as in 04)
DROP_VARIANT_RE = [r"^longSym$", r"^empTiltsNote$", r"_symLong$", r"_symCirc$",
                   r"^footAmbiguous$", r"^boom\d+_cards$"]
COUNT_FIELDS_RE = re.compile(r"(^|_)(count|ntypes|quickCount|wCount|archCount)$")
#: coded columns that hold several ids joined by "|"
MULTI_SUFFIX = {"zone", "edgeTags", "parts"}
FIG_CODED = ["per", "acSty", "acCol", "bgSty", "bgCol", "acState", "qualityFlag", "parts"]


# --------------------------------------------------------------------------
# helpers, mirrored from 04
# --------------------------------------------------------------------------
def strip_label(v):
    s = str(v)
    return s.split(SEP, 1)[0].strip() if SEP in s else s.strip()


def is_empty(v) -> bool:
    return v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() in (
        "", "nan", "None", "NaT")


def base_id(p) -> str:
    return re.sub(r"_arch\d+$", "", str(p))


def arch_idx(p) -> int:
    m = re.search(r"_arch(\d+)$", str(p))
    return int(m.group(1)) if m else 1


def suffix(field: str) -> str:
    f = re.sub(r"^\d+_", "", str(field))
    f = re.sub(r"^(boom|wing|hull_array|core_layout|emp|fuselage)\d*_", "", f)
    return re.sub(r"^t\d+_", "", f)


def _pivot(rows: pd.DataFrame) -> pd.DataFrame:
    d = rows[["Patent_ID", "Field", "Value"]].drop_duplicates(["Patent_ID", "Field"], keep="last")
    out = d.pivot(index="Patent_ID", columns="Field", values="Value")
    out.index.name = None
    out.columns.name = None
    return out


# --------------------------------------------------------------------------
# the reader
# --------------------------------------------------------------------------
def read_long(labels_dir: Path, batches: List[str]) -> pd.DataFrame:
    """Concatenate the batch exports into one long table (one row per Field)."""
    frames = []
    for b in batches:
        f = Path(labels_dir) / f"reviewed_patents_{b}.xlsx"
        df = pd.read_excel(f, sheet_name="Review")
        df["batch"] = b
        frames.append(df)
    L = pd.concat(frames, ignore_index=True)
    L["Field"] = L["Field"].astype(str)
    L["Section"] = L["Section"].astype(str)
    L["base"] = L["Patent_ID"].map(base_id)
    L["arch"] = L["Patent_ID"].map(arch_idx)
    L["_pos"] = L.groupby("batch").cumcount()
    return L


def build(labels_dir: Path, batches: List[str], data_dictionary: Optional[pd.DataFrame]
          ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """Return ``(master, figures, log)`` shaped like 04's outputs."""
    log: Dict = {}
    L = read_long(labels_dir, batches)
    log["long_rows"] = int(len(L))
    log["patents"] = int(L["base"].nunique())

    PT = _pivot(L[L["Section"].isin(SECTIONS_PATENT)])
    VT = _pivot(L[L["Section"].isin(SECTIONS_VARIANT)])
    batch_of = L.drop_duplicates("base").set_index("base")["batch"].to_dict()
    pos_of = L.drop_duplicates("base").set_index("base")["_pos"].to_dict()

    # a patent with BOTH a bare-id morphology and _archN rows: prefer _archN (04)
    bare = {p for p in VT.index if arch_idx(p) == 1 and not str(p).endswith("_arch1")}
    archd = {base_id(p) for p in VT.index if re.search(r"_arch\d+$", str(p))}
    both = sorted(bare & archd)
    log["bare_and_arch"] = both
    VT = VT.drop(index=both)
    var_ids = collections.defaultdict(list)
    for v in VT.index:
        var_ids[base_id(v)].append(v)
    for k in var_ids:
        var_ids[k].sort(key=arch_idx)

    # ---- skeleton
    rows = []
    for pid in PT.index:
        variants = var_ids.get(pid, [])
        if not variants:
            rows.append(dict(patent_id=pid, variant=1, variant_id=pid, n_variants=0))
        for v in variants:
            rows.append(dict(patent_id=pid, variant=arch_idx(v), variant_id=v,
                             n_variants=len(variants)))
    M = pd.DataFrame(rows)
    M["batch"] = M["patent_id"].map(batch_of)
    for src, dst in PATENT_COLS:
        M[dst] = M["patent_id"].map(PT[src]) if src in PT.columns else np.nan
    for src, dst in LEGACY_MERGE.items():
        if src in PT.columns:
            legacy = M["patent_id"].map(PT[src])
            fill = M[dst].map(is_empty) & ~legacy.map(is_empty)
            M.loc[fill, dst] = legacy[fill]
    variant_cols = [c for c in VT.columns if not any(re.search(p, c) for p in DROP_VARIANT_RE)]
    VTm = VT[variant_cols].reindex(M["variant_id"])
    VTm.index = M.index
    M = pd.concat([M, VTm], axis=1)

    # ---- normalise: every empty marker is missing (the wizard writes "None" into
    # some chord cells), coded columns lose their label half, booleans, counts
    for c in variant_cols:
        M[c] = M[c].map(lambda v: np.nan if is_empty(v) else v)
    coded = set()
    if data_dictionary is not None:
        coded = set(data_dictionary.loc[data_dictionary["kind"] == "id", "column"])
    for c in variant_cols:
        multi = suffix(c) in MULTI_SUFFIX
        if c in coded or M[c].astype(str).str.contains(SEP, regex=False).any():
            M[c] = M[c].map(lambda v, m=multi: np.nan if is_empty(v) else "|".join(
                strip_label(p) for p in (str(v).split("|") if m else [str(v)]) if p.strip()))
    for c in ["reason_human", "dup_type"]:
        M[c] = M[c].map(lambda v: np.nan if is_empty(v) else strip_label(v))
    # counts first: the wizard writes a count of 1 as True, so a count column made only
    # of True/False must become 1/0, not a boolean
    int_cols = []
    for c in list(M.columns):
        if COUNT_FIELDS_RE.search(c):
            M[c] = M[c].map(lambda v: np.nan if is_empty(v) else (
                1 if str(v) == "True" else 0 if str(v) == "False" else int(float(v)))).astype("Int64")
            int_cols.append(c)
    bool_cols = []
    for c in list(M.columns):
        if c in int_cols:
            continue
        vals = {str(x) for x in M[c].dropna().unique()}
        if vals and vals <= {"True", "False"}:
            M[c] = M[c].map(lambda v: np.nan if is_empty(v) else str(v) == "True").astype("boolean")
            bool_cols.append(c)
    for c in ["app_year", "pub_year"]:
        M[c] = pd.to_numeric(M[c], errors="coerce").astype("Int64")
    # dup_type as the integer code 04 stores (1 / 2 / 3)
    M["dup_type"] = pd.to_numeric(M["dup_type"], errors="coerce").astype("Int64")

    # ---- duplicates: chain root, inheritance, primary flag (04 cell 15)
    dup_of = {p: strip_label(v) for p, v in PT["duplicateId"].dropna().items() if not is_empty(v)} \
        if "duplicateId" in PT.columns else {}
    dup_type = {p: strip_label(v) for p, v in PT["duplicateType"].dropna().items() if not is_empty(v)} \
        if "duplicateType" in PT.columns else {}
    known = set(PT.index)

    def chain_root(p):
        seen = [p]
        while p in dup_of and dup_type.get(p) in ("1", "2"):
            p = dup_of[p]
            if p in seen or p not in known:
                return p, False
            seen.append(p)
        return p, True

    def top_original(p):
        seen = [p]
        while p in dup_of:
            p = dup_of[p]
            if p in seen or p not in known:
                return p
            seen.append(p)
        return p

    M = M.assign(dup_root=np.nan, labels_inherited_from=np.nan, is_primary=True,
                 dup_of_missing=False).copy()
    dtypes = M.dtypes.to_dict()
    out_rows, missing_root = [], []
    for pid, grp in M.groupby("patent_id", sort=False):
        t = dup_type.get(pid)
        if t in ("1", "2"):
            root, ok = chain_root(pid)
            if not ok or root not in var_ids:
                missing_root.append((pid, root))
                grp = grp.copy()
                grp["dup_root"] = root
                grp["is_primary"] = False
                grp["dup_of_missing"] = True
                out_rows += grp.to_dict("records")
                continue
            src = M[M["patent_id"] == root].sort_values("variant")
            new = []
            for _, r in src.iterrows():
                row = grp.iloc[0].copy()
                for c in variant_cols:
                    row[c] = r[c]
                row["variant"] = r["variant"]
                row["variant_id"] = f"{pid}_arch{r['variant']}" if len(src) > 1 else pid
                row["n_variants"] = len(src)
                row["dup_root"] = root
                row["labels_inherited_from"] = root
                row["is_primary"] = False
                new.append(row.to_dict())
            out_rows += new
        elif t == "3":
            grp = grp.copy()
            grp["dup_root"] = top_original(pid)
            grp["is_primary"] = True
            out_rows += grp.to_dict("records")
        else:
            out_rows += grp.to_dict("records")
    # one construction, the original dtypes re-applied (booleans and Int64 counts survive)
    M = pd.DataFrame(out_rows, columns=list(dtypes))
    for c, dt in dtypes.items():
        try:
            M[c] = M[c].astype(dt)
        except (TypeError, ValueError):
            pass
    log["dup_links"] = len(dup_of)
    log["dup_root_missing"] = missing_root

    # ---- order under the original, as 04 does
    def anchor(pid):
        return top_original(pid) if pid in dup_of else pid
    M["_anchor"] = M["patent_id"].map(anchor)
    M["_abatch"] = M["_anchor"].map(batch_of).fillna(M["batch"])
    M["_apos"] = M["_anchor"].map(pos_of).fillna(10 ** 9)
    M["_self"] = (M["patent_id"] != M["_anchor"]).astype(int)
    M["_dt"] = M["dup_type"].astype(str).replace("<NA>", "0")
    M = M.sort_values(["_abatch", "_apos", "_self", "_dt", "patent_id", "variant"]).reset_index(drop=True)
    M = M.drop(columns=["_anchor", "_abatch", "_apos", "_self", "_dt"])

    # ---- figures (04 cell 19, without the parts free-text recode)
    T2 = L[L["Section"] == "T2"].copy()
    T2["block"] = T2["Sub_Dimension"].astype(str)
    placeholder = T2["block"].str.contains(r"\(fig", regex=True)
    n_placeholder = T2[placeholder & (T2["Field"] == "status")].groupby("base").size()
    T2 = T2[~placeholder]
    F = (T2.drop_duplicates(["base", "block", "Field"], keep="last")
           .pivot(index=["base", "block"], columns="Field", values="Value").reset_index())
    F.columns.name = None
    ip = (T2.dropna(subset=["Image_Path"]).drop_duplicates(["base", "block"])
            .set_index(["base", "block"])["Image_Path"])
    F["image_path"] = [ip.get((b, k), np.nan) for b, k in zip(F["base"], F["block"])]
    for c in [c for c in F.columns if c not in ("base", "block")]:
        F[c] = F[c].map(lambda v: np.nan if is_empty(v) else v)
    F = F.rename(columns={"base": "patent_id", "figKey": "fig_key", "isMain": "is_main",
                          "edgeTags": "fig_tags"})
    F["batch"] = F["patent_id"].map(batch_of)
    F["image_file"] = F["image_path"].map(lambda p: Path(str(p)).name if not is_empty(p) else np.nan)
    for c in FIG_CODED:
        if c in F.columns:
            F[c] = F[c].map(lambda v, m=(c == "parts"): np.nan if is_empty(v) else "|".join(
                strip_label(p) for p in (str(v).split("|") if m else [str(v)]) if p.strip()))
    F["arch"] = pd.to_numeric(F.get("arch"), errors="coerce").astype("Int64")
    for c in ["is_main", "hasLegends"]:
        if c in F.columns:
            F[c] = F[c].map(lambda v: np.nan if is_empty(v) else str(v) == "True").astype("boolean")
    F["status"] = F["status"].map(lambda v: np.nan if is_empty(v) else str(v))

    appr = F[F["status"] == "approved"]
    M["n_figures"] = M["patent_id"].map(F.groupby("patent_id").size()).fillna(0).astype(int)
    M["n_approved"] = M["patent_id"].map(appr.groupby("patent_id").size()).fillna(0).astype(int)
    M["n_fig_placeholders"] = M["patent_id"].map(n_placeholder).fillna(0).astype(int)
    byv = appr.groupby(["patent_id", "arch"]).size()
    M["n_approved_this_variant"] = [int(byv.get((p, v), 0)) for p, v in zip(M["patent_id"], M["variant"])]
    # inherited rows count the ROOT's figures (a D1/D2 is the same aircraft)
    for i in M.index[M["labels_inherited_from"].notna()]:
        root = M.at[i, "labels_inherited_from"]
        M.at[i, "n_approved_this_variant"] = int(byv.get((root, M.at[i, "variant"]), 0))
    M["reason"] = M["reason_human"]
    M["reason_source"] = np.where(M["reason_human"].notna(), "human", None)
    log["master_rows"] = int(len(M))
    log["figures"] = int(len(F))
    log["approved_figures"] = int(len(appr))
    return M, F, log


def read_identity(labels_dir: Path, batches: List[str]) -> pd.DataFrame:
    """Concatenate the per-batch Stage 03a identity workbooks."""
    frames = []
    for b in batches:
        f = Path(labels_dir) / b / f"aircraft_identity_{b}.xlsx"
        if f.exists():
            frames.append(pd.read_excel(f))
    if not frames:
        raise FileNotFoundError(f"no aircraft_identity_Batch_0N.xlsx under {labels_dir}")
    return pd.concat(frames, ignore_index=True).drop_duplicates("patent_id")
