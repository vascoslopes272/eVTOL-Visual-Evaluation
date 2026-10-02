"""Read ``1639_LABELLED`` once and hand every Part A module the same frames.

The only path that has to be configured is ``paths.labelled_root`` in
``labeling_evaluation/config.yaml``; every file below is found relative to it.

The analysis unit of Part A is the **primary approved variant** (one row per
aircraft, D1/D2 duplicates excluded): ``Dataset.variants``. Facts stated per
patent use ``Dataset.patents`` (one row per patent) and its approved primary
subset ``Dataset.patents_analysis``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# --------------------------------------------------------------------------
# file layout inside 1639_LABELLED
# --------------------------------------------------------------------------
FILES = {
    # 2026-09-17 layout: 0_labelling/inputs (what 04 reads) and 0_labelling/outputs (what 04 writes)
    "master": "0_labelling/outputs/tables/aircraft_table.csv",
    "figures": "0_labelling/outputs/tables/figure_table.csv",
    "identity": "0_labelling/inputs/identity/aircraft_identity_ALL.xlsx",
    "field_inventory": "_archive/joined_leftovers_20260916/phase1_field_inventory.csv",
    "data_dictionary": "0_labelling/outputs/tables/data_dictionary.csv",
    "text_arch": "0_labelling/inputs/text_architecture/architecture_text_Claude_20260909.csv",
    "text_arch_final": "0_labelling/inputs/text_architecture/architecture_text_final.csv",
    "known_aircraft": "0_labelling/inputs/text_architecture/known_aircraft_architecture.csv",
    "quote_check": "0_labelling/inputs/text_architecture/quote_check.csv",
    "text_identity": "0_labelling/inputs/text_identity/results.csv",
    "text_identity_cmp": "0_labelling/inputs/text_identity/comparison_237.csv",
    # 2026-09-22: NASA TRL + programme status per aircraft (Patent-Labelling-Tools/scripts/build_aircraft_trl.py)
    "trl": "0_labelling/inputs/trl/aircraft_trl.csv",
}


def labelled_root(cfg: Dict[str, Any]) -> Path:
    """The ``1639_LABELLED`` folder, from ``paths.labelled_root`` in config.yaml."""
    root = cfg.get("paths", {}).get("labelled_root")
    if root is None or "EDIT-ME" in str(root):
        raise KeyError(
            "config.yaml: set paths.labelled_root to the 1639_LABELLED folder"
        )
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"paths.labelled_root does not exist: {root}")
    return root


#: workbooks whose cells hold codebook option ids — two of those ids, ``NA`` (N/A)
#: and ``None`` (no chordwise sense), are in pandas' default ``na_values`` and would
#: silently become missing on read. These are read with that conversion off.
OPTION_ID_FILES = {"master", "figures"}


def _read(root: Path, key: str, required: bool = True) -> Optional[pd.DataFrame]:
    path = root / FILES[key]
    if not path.exists():
        if required:
            raise FileNotFoundError(f"missing {key}: {path}")
        return None
    if path.suffix == ".csv":
        if key in OPTION_ID_FILES:   # option ids NA / None must stay text
            return pd.read_csv(path, keep_default_na=False, na_values=[""], low_memory=False)
        return pd.read_csv(path)
    if key in OPTION_ID_FILES:
        return pd.read_excel(path, keep_default_na=False, na_values=[""])
    return pd.read_excel(path)


#: figure-sheet booleans (the figures sheet has no data-dictionary rows) — the same
#: list batch_reader types, so both sources agree
FIGURE_BOOLS = ("is_main", "hasLegends")


def _apply_kinds(df: pd.DataFrame, data_dictionary: Optional[pd.DataFrame],
                 extra_bools: tuple = ()) -> pd.DataFrame:
    """Give the Stage 04 sheets the dtypes batch_reader produces.

    Excel keeps booleans and counts as such, but a column with blanks comes back
    from ``read_excel`` as float ``1.0 / 0.0`` — which the roster's ``str(x) == "True"``
    test never matches and which prints as ``1.0 507`` in the tables. The data
    dictionary's ``kind`` says which columns are bool / int; those become the
    nullable ``boolean`` / ``Int64`` dtypes batch_reader uses (2026-09-15).
    """
    from .batch_reader import COUNT_FIELDS_RE      # the same name rule for count columns

    kinds: Dict[str, str] = {}
    if data_dictionary is not None and {"column", "kind"} <= set(data_dictionary.columns):
        kinds = dict(zip(data_dictionary["column"], data_dictionary["kind"]))
    # the dictionary infers `kind` from the values it saw, so a sparse count reads as
    # "bool" and a boolean card field as "text" — the name rule and the values decide
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
                not c.startswith("ml_")           # ML pre-label codes (e.g. ml_duplicateType) stay as they are
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
    """Every frame Part A is measured on, plus the standard filtered views."""

    root: Path
    master: pd.DataFrame           # 1 row per (patent, variant) — the Stage 04 join
    figures: pd.DataFrame          # 1 row per figure that has a file
    identity: pd.DataFrame         # 1 row per patent — Stage 03a
    field_inventory: Optional[pd.DataFrame] = None
    data_dictionary: Optional[pd.DataFrame] = None
    text_arch: Optional[pd.DataFrame] = None        # the 2026-09-09 reading pass
    text_arch_final: Optional[pd.DataFrame] = None  # after the confirmation page
    known_aircraft: Optional[pd.DataFrame] = None
    quote_check: Optional[pd.DataFrame] = None
    text_identity: Optional[pd.DataFrame] = None
    text_identity_cmp: Optional[pd.DataFrame] = None
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


#: the two places the labels can be read from
SOURCES = ("batch_xlsx", "master_04")
BATCHES = ["Batch_01", "Batch_02", "Batch_03", "Batch_04", "Batch_05"]


def load_dataset(cfg: Dict[str, Any], strict: bool = False,
                 source: Optional[str] = None) -> Dataset:
    """Load every input.

    ``source`` (or ``dataset_facts.source`` in config.yaml) chooses where the
    labels come from:

    * ``batch_xlsx`` — straight from ``labels/reviewed_patents_Batch_0N.xlsx`` and
      ``labels/Batch_0N/aircraft_identity_Batch_0N.xlsx``, reshaped by
      :mod:`batch_reader` (values exactly as the batch files hold them);
    * ``master_04`` — the Stage 04 join ``joined/master_labels.xlsx`` +
      ``master_figures.xlsx`` and ``joined/aircraft_identity_ALL.xlsx``.

    The :class:`Dataset` is the same either way. ``strict=False`` (default)
    tolerates the optional text-side files being absent.
    """
    root = labelled_root(cfg)
    facts = cfg.get("dataset_facts", {}) or {}
    source = source or facts.get("source", "master_04")
    if source not in SOURCES:
        raise ValueError(f"dataset_facts.source must be one of {SOURCES}, got {source!r}")
    data_dictionary = _read(root, "data_dictionary", required=False)

    if source == "batch_xlsx":
        from . import batch_reader
        batches = list(facts.get("batches", BATCHES))
        master, figures, log = batch_reader.build(root / "labels", batches, data_dictionary)
        identity = batch_reader.read_identity(root / "labels", batches)
    else:
        master = _apply_kinds(_read(root, "master"), data_dictionary)
        figures = _apply_kinds(_read(root, "figures"), None, extra_bools=FIGURE_BOOLS)
        log = {}
        identity = _read(root, "identity")

    ds = Dataset(
        root=root,
        master=master,
        figures=figures,
        identity=identity,
        field_inventory=_read(root, "field_inventory", required=False),
        data_dictionary=data_dictionary,
        text_arch=_read(root, "text_arch", required=strict),
        text_arch_final=_read(root, "text_arch_final", required=False),
        known_aircraft=_read(root, "known_aircraft", required=strict),
        quote_check=_read(root, "quote_check", required=False),
        text_identity=_read(root, "text_identity", required=strict),
        text_identity_cmp=_read(root, "text_identity_cmp", required=strict),
        trl=_read(root, "trl", required=False),
    )
    ds.source = source
    ds.build_log = log
    return ds
