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
    "master": "joined/master_labels.xlsx",
    "figures": "joined/master_figures.xlsx",
    "identity": "joined/aircraft_identity_ALL.xlsx",
    "field_inventory": "joined/phase1_field_inventory.csv",
    "data_dictionary": "joined/data_dictionary.csv",
    "text_arch": "text_architecture/architecture_text_Claude_20260909.csv",
    "text_arch_final": "text_architecture/architecture_text_final.csv",
    "known_aircraft": "text_architecture/known_aircraft_architecture.csv",
    "quote_check": "text_architecture/quote_check.csv",
    "text_identity": "text_identity/results.csv",
    "text_identity_cmp": "text_identity/comparison_237.csv",
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

    #: which source the labels came from, and what the batch reader logged
    source: str = field(init=False, default="master_04")
    build_log: Dict = field(init=False, default_factory=dict)

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
        approved = m["is_approved"].fillna(False).astype(bool)
        primary = m["is_primary"].fillna(False).astype(bool)

        # ---- the domain gate (user ruling 2026-09-15): a Similar tag on an aircraft takes
        # it OUT of the analysis. The tag is per aircraft (per variant row), so a patent that
        # draws several aircraft stays representative while one of them survives; its figures
        # follow the patent. `is_approved` stays the wizard's recorded verdict.
        tags = m["edgeTags"].fillna("").astype(str).map(lambda v: set(v.split("|")) - {""})
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
        m["n_approved_this_variant"] = [int(byv.get((r, v), 0)) for r, v in zip(root, m["variant"])]
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
    )
    ds.source = source
    ds.build_log = log
    return ds
