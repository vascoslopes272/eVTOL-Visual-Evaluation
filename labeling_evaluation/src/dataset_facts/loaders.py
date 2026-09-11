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


def _read(root: Path, key: str, required: bool = True) -> Optional[pd.DataFrame]:
    path = root / FILES[key]
    if not path.exists():
        if required:
            raise FileNotFoundError(f"missing {key}: {path}")
        return None
    if path.suffix == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


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

    # derived views, built in __post_init__
    variants: pd.DataFrame = field(init=False)
    approved_variants: pd.DataFrame = field(init=False)
    patents: pd.DataFrame = field(init=False)
    patents_analysis: pd.DataFrame = field(init=False)
    approved_figures: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        m = self.master
        approved = m["is_approved"].fillna(False).astype(bool)
        primary = m["is_primary"].fillna(False).astype(bool)

        #: every approved aircraft variant, duplicates included (1,268)
        self.approved_variants = m[approved].copy()
        #: THE ANALYSIS UNIT — primary approved variants, one row per aircraft (805)
        self.variants = m[approved & primary].copy()
        #: one row per patent (1,639), the patent-level columns of the master
        self.patents = m.drop_duplicates("patent_id").copy()
        #: the approved primary patents behind the analysis set (695)
        self.patents_analysis = self.variants.drop_duplicates("patent_id").copy()

        status = self.figures["status"].astype(str).str.lower()
        self.approved_figures = self.figures[status.eq("approved")].copy()

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
            "patents_approved": int(
                self.patents["is_approved"].fillna(False).astype(bool).sum()
            ),
            "patents_analysis": int(self.patents_analysis["patent_id"].nunique()),
            "approved_variants": int(len(self.approved_variants)),
            "primary_approved_variants": int(len(self.variants)),
            "approved_figures": int(len(self.approved_figures)),
        }


def load_dataset(cfg: Dict[str, Any], strict: bool = False) -> Dataset:
    """Load every Part A input.

    ``strict=False`` (default) tolerates the optional text-side files being
    absent, so the corpus sections still run on a machine that only has the
    Stage 04 join.
    """
    root = labelled_root(cfg)
    return Dataset(
        root=root,
        master=_read(root, "master"),
        figures=_read(root, "figures"),
        identity=_read(root, "identity"),
        field_inventory=_read(root, "field_inventory", required=False),
        data_dictionary=_read(root, "data_dictionary", required=False),
        text_arch=_read(root, "text_arch", required=strict),
        text_arch_final=_read(root, "text_arch_final", required=False),
        known_aircraft=_read(root, "known_aircraft", required=strict),
        quote_check=_read(root, "quote_check", required=False),
        text_identity=_read(root, "text_identity", required=strict),
        text_identity_cmp=_read(root, "text_identity_cmp", required=strict),
    )
