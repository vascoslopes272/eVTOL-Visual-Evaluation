"""The labelled dataset, read once from the paths in ``labelling_analysis.yaml``.

Ported 2026-10-01 from ``archive/labeling_evaluation/src/dataset_facts/loaders.py`` (the code that
produced the 45-page document). The DEFINITIONS are copied unchanged — override rule (ruling
2026-09-19), domain gate (2026-09-15), whole-vehicle figures (refinement 3) — so the analysis unit is
the same aircraft set. Only the file locations changed: they now come from ``labelling_analysis.yaml``. The
``batch_xlsx`` source of the archive is dropped; the thesis reads the Stage 04 tables only.

    from viz import config, data
    cfg = config.load()
    ds = data.load_dataset(cfg)
    ds.variants          # THE ANALYSIS UNIT: one row per representative primary aircraft
    ds.counts            # headline counts

The analysis unit is the **primary representative variant** (one row per aircraft, D1/D2 duplicates
excluded): ``Dataset.variants``. Facts stated per patent use ``Dataset.patents`` and its representative
primary subset ``Dataset.patents_analysis``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

#: count columns, by name (archive batch_reader.COUNT_FIELDS_RE)
COUNT_FIELDS_RE = re.compile(r"(^|_)(count|ntypes|quickCount|wCount|archCount)$")

#: workbooks whose cells hold codebook option ids — two of those ids, ``NA`` (N/A) and ``None`` (no
#: chordwise sense), are in pandas' default ``na_values`` and would silently become missing on read.
OPTION_ID_FILES = {"aircraft_labels", "figure_labels"}

#: figure-sheet booleans (the figures sheet has no data-dictionary rows)
FIGURE_BOOLS = ("is_main", "hasLegends")


def read(cfg, key: str, required: bool = True) -> Optional[pd.DataFrame]:
    """Read one input of labelling_analysis.yaml by key (csv or xlsx), keeping option ids NA/None as text."""
    path: Path = cfg.path(key)
    if not path.exists():
        if required:
            raise FileNotFoundError(f"missing {key}: {path}")
        return None
    kw = dict(keep_default_na=False, na_values=[""]) if key in OPTION_ID_FILES else {}
    if path.suffix == ".csv":
        return pd.read_csv(path, low_memory=False, **kw)
    return pd.read_excel(path, **kw)


def _apply_kinds(df: pd.DataFrame, data_dictionary: Optional[pd.DataFrame],
                 extra_bools: tuple = ()) -> pd.DataFrame:
    """Give the Stage 04 tables nullable bool / Int64 dtypes (archive loaders._apply_kinds, unchanged)."""
    kinds: Dict[str, str] = {}
    if data_dictionary is not None and {"column", "kind"} <= set(data_dictionary.columns):
        kinds = dict(zip(data_dictionary["column"], data_dictionary["kind"]))
    int_cols = [c for c in df.columns
                if COUNT_FIELDS_RE.search(c) or kinds.get(c) == "int"
                or c in ("app_year", "pub_year", "dup_type", "arch")]
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    for c in df.columns:
        if c in int_cols or kinds.get(c) == "id":
            continue
        s = df[c]
        if c in extra_bools or kinds.get(c) == "bool" or (
                not c.startswith("ml_")
                and str(s.dtype) == "float64" and s.notna().any() and set(s.dropna().unique()) <= {0.0, 1.0}):
            df[c] = s.map(lambda v: (pd.NA if pd.isna(v) else str(v) in ("True", "1", "1.0"))
                          if not isinstance(v, bool) else v).astype("boolean")
    return df


# --------------------------------------------------------------------------
# rule 1 (ruling 2026-09-19): an override keeps only what it records
# --------------------------------------------------------------------------
#: "An override keeps only what it records. After a G1 override the aircraft has no type;
#: after an M1 or M2 override the skipped fields are not determinable; at an M3 station
#: only the propulsor count is kept. A value that is not determinable is never read as
#: zero, none or Fixed. It is left out, and the number left out is reported."
#: The wizard stores an overridden M3 station as ``<station>_count = 0`` and the real
#: number in ``<station>_quickCount``; notebook 04 lists the overrides in ``overrides``.
M3_STATIONS = ["fuselage", "wing1", "wing2", "wing3", "emp", "boom", "core_layout", "hull_array"]
#: what a G1 override hides (notebook 04's HIDDEN_BY): the type, nothing else
G1_HIDDEN = ("topType", "notPureArch")
#: the labelling-process columns an override never hides
OVERRIDE_PROCESS = ("humanUncertain", "quickOverride", "quickCount", "quickNote")
#: architecture types the codebook gives no propulsor record (no M3 card)
NO_UNITS_TYPES = ("HB", "PFV")


def override_sets(frame: pd.DataFrame) -> pd.Series:
    """The overrides ticked on each row, as a set of ``G1`` / ``M1`` / ``M2`` / ``M3:<station>``.

    Read from notebook 04's ``overrides`` column; a frame without it (the batch reader)
    falls back on the wizard's own ``*_quickOverride`` ticks.
    """
    if "overrides" in frame.columns:
        return frame["overrides"].fillna("").astype(str).map(lambda s: frozenset(s.split("|")) - {""})

    def tick(c):
        return frame[c].map(lambda x: str(x) == "True") if c in frame.columns else pd.Series(False, index=frame.index)
    parts = {s: tick(f"{s.lower()}_quickOverride") for s in ("G1", "M1", "M2")}
    parts.update({f"M3:{st}": tick(f"{st}_quickOverride") for st in M3_STATIONS})
    return pd.Series([frozenset(k for k, s in parts.items() if s.iat[i]) for i in range(len(frame))],
                     index=frame.index)


def override_stage(column: str, section: str) -> Optional[str]:
    """The override that hides ``column`` (``G1`` / ``M1`` / ``M2`` / ``M3:<station>``), or None.

    A count at an M3 station is not hidden: it is replaced by the quick count
    (:func:`apply_overrides`).
    """
    if any(p.lower() in column.lower() for p in OVERRIDE_PROCESS):
        return None
    if section == "G1":
        return "G1" if column in G1_HIDDEN else None
    if section in ("M1", "M2"):
        return section
    if section == "M3":
        st = next((s for s in M3_STATIONS if column.startswith(s + "_")), None)
        if st is None or column in (f"{st}_count",):
            return None
        return f"M3:{st}"
    return None


def hidden_by_override(frame: pd.DataFrame, column: str,
                       data_dictionary: Optional[pd.DataFrame]) -> pd.Series:
    """True on the rows where an override hides ``column`` (the value is not determinable)."""
    sections = {} if data_dictionary is None else dict(zip(data_dictionary["column"], data_dictionary["section"]))
    stage = override_stage(column, str(sections.get(column, "")))
    if stage is None:
        return pd.Series(False, index=frame.index)
    return override_sets(frame).map(lambda s: stage in s).astype(bool)


def apply_overrides(m: pd.DataFrame, data_dictionary: Optional[pd.DataFrame]) -> Dict[str, int]:
    """Blank every value an override hides, in place; an overridden M3 station counts its quick count.

    Returns how many cells were blanked and how many station counts were replaced, per
    override. A stored value behind an override is a leftover of the wizard (notebook 04
    flags it as OVERRIDE_HIDES_VALUE), never an answer.
    """
    if data_dictionary is None or not {"column", "section"} <= set(data_dictionary.columns):
        return {}
    ov = override_sets(m)
    has = ov.map(bool)
    log: Dict[str, int] = {}
    if not has.any():
        return log
    sections = dict(zip(data_dictionary["column"], data_dictionary["section"]))
    for c in m.columns:
        stage = override_stage(c, str(sections.get(c, "")))
        if stage is None:
            continue
        rows = has & ov.map(lambda s, st=stage: st in s) & m[c].notna()
        if rows.any():
            m.loc[rows, c] = None
            log[stage] = log.get(stage, 0) + int(rows.sum())
    for st in M3_STATIONS:
        cnt, qc = f"{st}_count", f"{st}_quickCount"
        if cnt not in m.columns:
            continue
        rows = ov.map(lambda s, st=st: f"M3:{st}" in s)
        if rows.any():
            q = pd.to_numeric(m[qc], errors="coerce") if qc in m.columns else pd.Series(pd.NA, index=m.index)
            m.loc[rows, cnt] = q[rows].astype("Int64") if str(m[cnt].dtype) == "Int64" else q[rows]
            log[f"M3:{st} count from the quick count"] = int(rows.sum())
    return log


#: the edge tags that take an aircraft out of the analysis (ruling 2026-09-15: only
#: electric, vertical-take-off, non-UAV aircraft enter). V/STOL carries no tag and stays;
#: a Hybrid or Unknown powertrain carries no tag and stays.
GATE_TAGS = ("UAVSimilar", "ElectricSimilar", "STOLSimilar")
#: the disapproval reason written on a patent the gate removes entirely
SIMILAR_REASON = {"UAVSimilar": "Similar: UAV", "ElectricSimilar": "Similar: not electric",
                  "STOLSimilar": "Similar: STOL only"}
#: the T2 `parts` value of a figure that shows the whole aircraft (refinement 3)
WHOLE_VEHICLE = "Whole Vehicle Layout"


# --------------------------------------------------------------------------
# the dataset
# --------------------------------------------------------------------------
@dataclass
class Dataset:
    """Every frame the thesis is measured on, plus the standard filtered views."""

    root: Path
    master: pd.DataFrame           # 1 row per (patent, variant) — the Stage 04 join
    figures: pd.DataFrame          # 1 row per figure that has a file
    identity: pd.DataFrame         # 1 row per patent — Stage 03a
    data_dictionary: Optional[pd.DataFrame] = None
    trl: Optional[pd.DataFrame] = None               # NASA TRL + programme status per aircraft

    #: which source the labels came from, and what the batch reader logged
    source: str = field(init=False, default="master_04")
    build_log: Dict = field(init=False, default_factory=dict)
    #: rule 1 (2026-09-19): cells blanked because an override hides them (apply_overrides)
    override_log: Dict = field(init=False, default_factory=dict)

    # derived views, built in __post_init__
    variants: pd.DataFrame = field(init=False)
    approved_variants: pd.DataFrame = field(init=False)
    patents: pd.DataFrame = field(init=False)
    patents_analysis: pd.DataFrame = field(init=False)
    approved_figures: pd.DataFrame = field(init=False)       # whole-aircraft figures: the image set
    approved_figures_all: pd.DataFrame = field(init=False)   # every approved figure of a representative patent
    figures_rep: pd.DataFrame = field(init=False)            # every figure on file of a representative patent
    gated_out: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        m = self.master
        # rule 1 (ruling 2026-09-19): a value an override hides is not determinable, so it is
        # blanked here once and every table reads the same record
        self.override_log = apply_overrides(m, self.data_dictionary)
        approved = m["is_approved"].fillna(False).astype(bool)
        primary = m["is_primary"].fillna(False).astype(bool)

        # ---- the domain gate (user ruling 2026-09-15): a Similar tag on an aircraft takes
        # it OUT of the analysis. The tag is per aircraft (per variant row), so a patent that
        # draws several aircraft stays representative while one of them survives; its figures
        # follow the patent. `is_approved` stays the wizard's recorded verdict.
        tags = m["edgeTags"].fillna("").astype(str).map(lambda v: set(v.split("|")) - {""})
        # 2026-09-17: a D1/D2 row carries no G1 block of its own — it POINTS at the aircraft it
        # repeats (`same_aircraft_as`, first target). It is gated with that aircraft's tags.
        if "same_aircraft_as" in m.columns and "aircraft_id" in m.columns:
            own = dict(zip(m["aircraft_id"], tags))
            target = m["same_aircraft_as"].fillna("").astype(str).str.split("; ").str[0]
            tags = pd.Series([own.get(t, tg) if t else tg for t, tg in zip(target, tags)], index=m.index)
        m["similar_tag"] = tags.map(lambda t: next((g for g in GATE_TAGS if g in t), None))
        m["is_representative"] = approved & m["similar_tag"].isna()
        patent_rep = m.groupby("patent_id")["is_representative"].transform("any")
        m["patent_representative"] = patent_rep
        # a wizard-approved patent none of whose aircraft survives gets the tag as its reason
        dropped = approved & ~patent_rep
        first_tag = m[dropped].groupby("patent_id")["similar_tag"].first()
        m.loc[dropped, "reason"] = m.loc[dropped, "patent_id"].map(first_tag).map(SIMILAR_REASON)
        rep = m["is_representative"]

        #: every representative aircraft variant, duplicates included
        self.approved_variants = m[rep].copy()
        #: THE ANALYSIS UNIT — primary representative variants, one row per aircraft
        self.variants = m[rep & primary].copy()
        #: one row per patent (1,639), the patent-level columns of the master
        self.patents = m.drop_duplicates("patent_id").copy()
        self.patents["is_representative"] = self.patents["patent_representative"]
        #: the representative primary patents behind the analysis set
        self.patents_analysis = self.variants.drop_duplicates("patent_id").copy()
        #: what the gate removed: wizard-approved rows carrying a Similar tag
        self.gated_out = m[approved & ~rep].copy()

        # ---- refinement 3 (user ruling 2026-09-15): of the approved figures of the
        # representative patents, only those showing the WHOLE aircraft are analysed; the
        # detail figures approved on purpose (tilt mechanism, rotor) stay on record only.
        status = self.figures["status"].astype(str).str.lower()
        rep_patents = set(self.patents.loc[self.patents["is_representative"], "patent_id"])
        #: every figure on file of a representative patent — what refinement 3 examines
        self.figures_rep = self.figures[self.figures["patent_id"].isin(rep_patents)].copy()
        self.approved_figures_all = self.figures_rep[status.loc[self.figures_rep.index].eq("approved")].copy()
        whole = self.approved_figures_all["parts"].astype(str).str.split("|").str[0].eq(WHOLE_VEHICLE)
        self.approved_figures = self.approved_figures_all[whole].copy()
        # the figures behind each aircraft (single-figure flag, medians) follow the same rule;
        # an inherited row (D1/D2) points at its root's figures, as notebook 04 does
        byv = self.approved_figures.groupby(["patent_id", "arch"]).size()
        m["n_approved_this_variant_all"] = m["n_approved_this_variant"]
        root = m["labels_inherited_from"].where(m["labels_inherited_from"].notna(), m["patent_id"])
        ua = m["points_to_ua"].where(m["points_to_ua"].notna(), m["variant"]) if "points_to_ua" in m.columns else m["variant"]
        m["n_approved_this_variant"] = [int(byv.get((r, int(v)), 0)) for r, v in zip(root, pd.to_numeric(ua, errors="coerce").fillna(1))]
        for view in (self.approved_variants, self.variants, self.patents, self.patents_analysis):
            view["n_approved_this_variant"] = m.loc[view.index, "n_approved_this_variant"]

    # ---- convenience ------------------------------------------------------
    def with_identity(
        self, frame: Optional[pd.DataFrame] = None, cols: Optional[list] = None
    ) -> pd.DataFrame:
        """Left-join Stage 03a identity columns onto a master-shaped frame."""
        left = self.variants if frame is None else frame
        right = self.identity if cols is None else self.identity[["patent_id", *cols]]
        overlap = [
            c for c in right.columns if c in left.columns and c != "patent_id"
        ]
        return left.merge(
            right.drop(columns=overlap), on="patent_id", how="left", validate="m:1"
        )

    @property
    def counts(self) -> Dict[str, int]:
        """The headline counts of A.2 D1, recomputed."""
        return {
            "patents_acquired": int(self.patents["patent_id"].nunique()),
            # the wizard's verdict alone (before the Similar gate)
            "patents_wizard_approved": int(
                self.patents["is_approved"].fillna(False).astype(bool).sum()
            ),
            # representative = wizard-approved AND at least one aircraft passes the gate
            "patents_approved": int(self.patents["is_representative"].sum()),
            "patents_gated_out": int(
                self.patents["is_approved"].fillna(False).astype(bool).sum()
                - self.patents["is_representative"].sum()
            ),
            "variants_gated_out": int(len(self.gated_out)),
            "primary_variants_gated_out": int(self.gated_out["is_primary"].fillna(False).astype(bool).sum()),
            "patents_analysis": int(self.patents_analysis["patent_id"].nunique()),
            "approved_variants": int(len(self.approved_variants)),
            "primary_approved_variants": int(len(self.variants)),
            # the image set analysed: approved AND whole aircraft, on representative patents
            "approved_figures": int(len(self.approved_figures)),
            "approved_figures_all": int(len(self.approved_figures_all)),
            "detail_figures": int(len(self.approved_figures_all) - len(self.approved_figures)),
        }



def load_dataset(cfg) -> Dataset:
    """Read the Stage 04 tables named in labelling_analysis.yaml and build the analysis views."""
    dd = read(cfg, "label_dictionary", required=False)
    master = _apply_kinds(read(cfg, "aircraft_labels"), dd)
    figures = _apply_kinds(read(cfg, "figure_labels"), None, extra_bools=FIGURE_BOOLS)
    ds = Dataset(
        root=cfg.roots["labelled"],
        master=master,
        figures=figures,
        identity=read(cfg, "patent_facts"),
        data_dictionary=dd,
        trl=read(cfg, "trl_per_aircraft", required=False),
    )
    return ds
