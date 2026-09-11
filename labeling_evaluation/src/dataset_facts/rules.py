"""D12 — the 02a consistency-rule counts (index section 4.3).

Stage 02a of ``Patent-Labelling-Tools`` writes one ``rule_decisions_<batch>.json``
per batch it is run on: a dict ``rule name -> {applied: [ids], skipped: [ids],
saved_utc}``. This module only counts them. Until 02a has been run on every batch
the table is partial, and it says so in its ``attrs``.
"""

from __future__ import annotations

import glob
import json
import re
from pathlib import Path
from typing import Iterable, Union

import pandas as pd


def d12_rule_counts(pattern: Union[str, Iterable[str]]) -> pd.DataFrame:
    """Rule x batch: how many records each rule was applied to, and skipped on."""
    patterns = [pattern] if isinstance(pattern, str) else list(pattern)
    paths = sorted({p for pat in patterns for p in glob.glob(pat, recursive=True)})
    rows = []
    for path in paths:
        batch = re.search(r"(Batch_\d+)", Path(path).name)
        batch = batch.group(1) if batch else Path(path).stem
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            rows.append({"rule": f"(unreadable: {exc})", "batch": batch,
                         "applied": 0, "skipped": 0, "saved_utc": ""})
            continue
        for rule, entry in data.items():
            rows.append({
                "rule": rule,
                "batch": batch,
                "applied": len(entry.get("applied", [])),
                "skipped": len(entry.get("skipped", [])),
                "saved_utc": str(entry.get("saved_utc", ""))[:10],
            })
    out = pd.DataFrame(rows, columns=["rule", "batch", "applied", "skipped", "saved_utc"])
    out.attrs["files"] = paths
    out.attrs["batches"] = sorted(out["batch"].unique()) if len(out) else []
    out.attrs["partial"] = len(out.attrs["batches"]) < 5
    return out.sort_values(["batch", "rule"]).reset_index(drop=True)


def d12_by_rule(counts: pd.DataFrame) -> pd.DataFrame:
    """The same, summed over batches."""
    if counts.empty:
        return counts
    g = counts.groupby("rule")[["applied", "skipped"]].sum()
    g["batches"] = counts.groupby("rule")["batch"].nunique()
    return g.sort_values("applied", ascending=False).reset_index()
