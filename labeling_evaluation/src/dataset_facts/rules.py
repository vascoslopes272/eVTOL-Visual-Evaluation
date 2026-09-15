"""Index section 4.3 — the codebook's consistency rules, counted before and after correction.

The rules are the codebook's own (the L-series in ``consistency_audit.py`` and the
N-series in ``codebook_v156_audit.py``, both in
``Patent-Labelling-Tools/scripts/conformance/``). This module does not restate
them: it runs those two scripts on each batch export and counts what they flag,
so the numbers here are the harness's numbers. Run once on the pass-1 human
exports (``03_HUMAN_wizard_exports``, frozen) and once on the live batch files
(``1639_LABELLED/labels``) to get "before" and "after".

The legacy 02a rule sidecars (``rule_decisions_*.json``) are a different thing —
automated corrections applied by Stage 02a on two batches — and are kept only as
:func:`d12_rule_counts` for the record.
"""

from __future__ import annotations

import glob
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import pandas as pd

AUDITS = {"L": "consistency_audit.py", "N": "codebook_v156_audit.py"}
_FLAG_LINE = re.compile(r"^\s*\[([A-Z]\d+[a-z]?)\]\s+(.*?)\s+—\s+(\d+)\s*$")


def _export_path(directory: Path, batch: str) -> Optional[Path]:
    """The batch export in a directory — tolerating the stray space in one filename."""
    for pat in (f"reviewed_patents_{batch}.xlsx", f"reviewed_patents_{batch} .xlsx"):
        p = Path(directory) / pat
        if p.exists():
            return p
    return None


def run_audit(script: Path, batch: str, xlsx: Path) -> List[Dict]:
    """Run one audit script on one export and parse its ``[rule] message — n`` lines."""
    r = subprocess.run([sys.executable, str(script), batch, str(xlsx)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return [{"rule": "(script failed)", "message": r.stderr.strip()[-300:], "count": 0}]
    rows = []
    for line in r.stdout.splitlines():
        m = _FLAG_LINE.match(line)
        if m:
            rows.append({"rule": m.group(1), "message": m.group(2), "count": int(m.group(3))})
    return rows


def codebook_rule_counts(conformance_dir: Union[str, Path], stages: Dict[str, Union[str, Path]],
                         batches: Iterable[str]) -> pd.DataFrame:
    """Rule violations per rule x batch x stage.

    ``stages`` maps a stage name to a directory of ``reviewed_patents_Batch_0N.xlsx``
    files, e.g. ``{"before correction": <03_HUMAN>, "after correction": <labels/>}``.
    A batch missing from a stage is reported as such, not silently skipped.
    """
    conformance_dir = Path(conformance_dir)
    rows = []
    missing = []
    for stage, directory in stages.items():
        for b in batches:
            xlsx = _export_path(Path(directory), b)
            if xlsx is None:
                missing.append((stage, b))
                continue
            for series, script in AUDITS.items():
                for hit in run_audit(conformance_dir / script, b, xlsx):
                    rows.append({"stage": stage, "batch": b, "series": series, **hit})
    out = pd.DataFrame(rows, columns=["stage", "batch", "series", "rule", "message", "count"])
    out.attrs["missing"] = missing
    out.attrs["stages"] = list(stages)
    return out.sort_values(["stage", "batch", "rule"]).reset_index(drop=True)


def codebook_by_rule(counts: pd.DataFrame) -> pd.DataFrame:
    """Violations per rule, one column per stage, summed over the batches both stages have.

    A batch that one stage lacks (Batch_04 has no pass-1 export) is left out of
    both columns, so the two are comparable; ``attrs["batches_compared"]`` says
    which batches went in.
    """
    if counts.empty:
        return counts
    stages = counts.attrs.get("stages") or list(counts["stage"].unique())
    missing = {b for _, b in counts.attrs.get("missing", [])}
    c = counts[~counts["batch"].isin(missing)]
    g = c.pivot_table(index=["rule", "message"], columns="stage", values="count",
                      aggfunc="sum", fill_value=0)
    g = g.reindex(columns=[s for s in stages if s in g.columns], fill_value=0).reset_index()
    g.columns.name = None
    g["batches flagged"] = g["rule"].map(c.groupby("rule")["batch"].nunique())
    g = g.sort_values(list(stages[-1:]) + ["rule"], ascending=[False, True]).reset_index(drop=True)
    g.attrs["batches_compared"] = sorted(set(c["batch"]))
    return g


def codebook_by_batch(counts: pd.DataFrame) -> pd.DataFrame:
    """Total violations per batch and stage; a stage that lacks the batch shows as <NA>."""
    if counts.empty:
        return counts
    stages = counts.attrs.get("stages") or list(counts["stage"].unique())
    g = counts.pivot_table(index="batch", columns="stage", values="count", aggfunc="sum")
    g = g.reindex(columns=[s for s in stages if s in g.columns])
    for stage, b in counts.attrs.get("missing", []):
        if stage in g.columns and b in g.index:
            g.loc[b, stage] = pd.NA
        elif stage in g.columns:
            g.loc[b, stage] = pd.NA
    g = g.astype("Int64").reset_index()
    g.columns.name = None
    return g


# --------------------------------------------------------------------------
# the legacy 02a sidecars, kept for the record
# --------------------------------------------------------------------------
def d12_rule_counts(pattern: Union[str, Iterable[str]]) -> pd.DataFrame:
    """Rule x batch from ``rule_decisions_*.json``: records each 02a rule was applied to / skipped on."""
    patterns = [pattern] if isinstance(pattern, str) else list(pattern)
    paths = sorted({p for pat in patterns for p in glob.glob(pat, recursive=True)})
    rows = []
    for path in paths:
        batch = re.search(r"(Batch_\d+)", Path(path).name)
        batch = batch.group(1) if batch else Path(path).stem
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            rows.append({"rule": f"(unreadable: {exc})", "batch": batch, "applied": 0, "skipped": 0,
                         "saved_utc": ""})
            continue
        for rule, entry in data.items():
            rows.append({"rule": rule, "batch": batch, "applied": len(entry.get("applied", [])),
                         "skipped": len(entry.get("skipped", [])),
                         "saved_utc": str(entry.get("saved_utc", ""))[:10]})
    out = pd.DataFrame(rows, columns=["rule", "batch", "applied", "skipped", "saved_utc"])
    out.attrs["files"] = paths
    out.attrs["batches"] = sorted(out["batch"].unique()) if len(out) else []
    out.attrs["partial"] = len(out.attrs["batches"]) < 5
    return out.sort_values(["batch", "rule"]).reset_index(drop=True)


def d12_by_rule(counts: pd.DataFrame) -> pd.DataFrame:
    if counts.empty:
        return counts
    g = counts.groupby("rule")[["applied", "skipped"]].sum()
    g["batches"] = counts.groupby("rule")["batch"].nunique()
    return g.sort_values("applied", ascending=False).reset_index()
