"""Read ``labelling_analysis.yaml``, resolve every path, and check that every input exists.

    from viz.config import load
    cfg = load()                 # raises if an input is missing
    cfg.path("aircraft_labels")  # absolute Path of any input, by key
    cfg.out("q1")                # output folder of question 1 (created on demand)

Run ``python -m viz.config`` from ``labeling_evaluation/`` to print the path table.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

PILLAR = Path(__file__).resolve().parent.parent
YAML = PILLAR / "labelling_analysis.yaml"

#: an input's file is relative to roots.labelled unless it says `root:`; a file under assets/ is relative
#: to this folder
DEFAULT_ROOT = "labelled"


@dataclass
class Config:
    raw: Dict[str, Any]
    roots: Dict[str, Path]
    inputs: Dict[str, Path]           # key -> absolute path
    groups: Dict[str, str]            # key -> group name
    meta: Dict[str, Dict[str, Any]]   # key -> made_by, variables, review

    # ---- access -------------------------------------------------------------
    def path(self, key: str) -> Path:
        if key not in self.inputs:
            raise KeyError(f"labelling_analysis.yaml has no input '{key}'. Known: {sorted(self.inputs)}")
        return self.inputs[key]

    def out(self, key: str, make: bool = True) -> Path:
        sub = self.raw["outputs"].get(key)
        if sub is None:
            raise KeyError(f"labelling_analysis.yaml has no output '{key}'. Known: {sorted(self.raw['outputs'])}")
        p = self.roots["output"] / sub
        if make:
            p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def analysis(self) -> Dict[str, Any]:
        return self.raw["analysis"]

    @property
    def style(self) -> Dict[str, Any]:
        return self.raw["style"]

    # ---- checking -----------------------------------------------------------
    def table(self) -> List[Dict[str, Any]]:
        """One row per root and input: key, group, path, exists, size, modified."""
        rows = []
        for k, p in self.roots.items():
            rows.append(_row(k, "root", p))
        for k, p in self.inputs.items():
            rows.append({**_row(k, self.groups[k], p), **self.meta.get(k, {})})
        return rows

    def missing(self) -> List[str]:
        optional = set(self.raw.get("optional_inputs") or [])
        return [r["key"] for r in self.table()
                if not r["exists"] and r["key"] not in optional
                and not (r["group"] == "root" and r["key"] == "output")]


def stale(cfg: "Config") -> List[str]:
    """Is the labelled dataset older than what notebook 04 built it from? Read from notebook 04's own
    BUILD_LOG.md (the record it read) and the decisions folder beside the record; the yaml lists neither."""
    if "aircraft_labels" not in cfg.inputs:
        return []
    table = cfg.inputs["aircraft_labels"]
    log = table.parent.parent / "BUILD_LOG.md"
    if not (table.exists() and log.exists()):
        return []
    built = table.stat().st_mtime
    record = next((Path(l.split(":", 1)[1].strip()) for l in log.read_text(encoding="utf-8").splitlines()
                   if l.startswith("record")), None)
    out = []
    if record is not None and record.exists():
        newer = [p for p in [record, *(record.parent.parent / "review_decisions").glob("*.csv")]
                 if p.stat().st_mtime > built + 60]
        out = [f"{p.name} is newer than the labelled dataset: run build_identity_all.py and notebook 04 "
               "(Patent-Labelling-Tools) before the analysis" for p in newer]
    return out


def files_of(p: Path) -> List[Path]:
    """The files behind an input: itself, or every match of a wildcard path."""
    if "*" in str(p):
        return sorted(Path(p.anchor).glob(str(p.relative_to(p.anchor))))
    return [p] if p.exists() else []


def mtime(p: Path) -> float:
    fs = files_of(p)
    return max(f.stat().st_mtime for f in fs) if fs else 0.0


def _row(key: str, group: str, p: Path) -> Dict[str, Any]:
    fs = files_of(p)
    ok = bool(fs)
    size = ""
    when = ""
    if ok:
        if len(fs) > 1:
            size = f"{len(fs)} files"
        else:
            size = "dir" if fs[0].is_dir() else f"{fs[0].stat().st_size / 1024:,.0f} KB"
        when = dt.datetime.fromtimestamp(mtime(p)).strftime("%Y-%m-%d %H:%M")
    return dict(key=key, group=group, path=str(p), exists=ok, size=size, modified=when)


def load(path: Path | str = YAML, strict: bool = True) -> Config:
    """Load labelling_analysis.yaml. ``strict`` raises when any input or root (except the output) is missing."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    roots = {k: Path(v) for k, v in raw["roots"].items()}
    inputs: Dict[str, Path] = {}
    groups: Dict[str, str] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for group, entries in raw["inputs"].items():
        for key, e in entries.items():
            if key in inputs:
                raise ValueError(f"labelling_analysis.yaml: input key '{key}' appears twice")
            e = e if isinstance(e, dict) else {"file": e}
            rel = Path(e["file"])
            if rel.is_absolute():
                p = rel
            elif str(rel).startswith("assets/"):
                p = PILLAR / rel
            else:
                p = roots[e.get("root", DEFAULT_ROOT)] / rel
            inputs[key], groups[key] = p, group
            var = e.get("variables", "")
            if isinstance(var, dict):
                var = " · ".join(f"{who}: {v}" for who, v in var.items())
            meta[key] = {"made_by": e.get("made_by", ""), "variables": var, "review": e.get("review", "")}
    cfg = Config(raw=raw, roots=roots, inputs=inputs, groups=groups, meta=meta)
    if strict:
        miss = cfg.missing()
        if miss:
            lines = [f"  {r['key']:<20} {r['path']}" for r in cfg.table() if r["key"] in miss]
            raise FileNotFoundError("labelling_analysis.yaml: missing inputs:\n" + "\n".join(lines))
    if strict and stale(cfg):
        raise RuntimeError("the labelled dataset is out of date:\n  " + "\n  ".join(stale(cfg)))
    return cfg


def show(cfg: Config | None = None):
    """The path table as a DataFrame (for the notebooks)."""
    import pandas as pd
    cfg = cfg or load(strict=False)
    return pd.DataFrame(cfg.table())


if __name__ == "__main__":
    c = load(strict=False)
    rows = c.table()
    w = max(len(r["key"]) for r in rows)
    for r in rows:
        opt = r["key"] in set(c.raw.get("optional_inputs") or [])
        mark = "ok " if r["exists"] else ("absent*" if opt else "MISSING")
        print(f"{mark:7} {r['group']:9} {r['key']:<{w}}  {r['modified']:16}  {r['size']:>10}  {r['path']}")
    m = c.missing()
    print(f"\n{len(rows)} paths, {len(m)} missing" + (f": {', '.join(m)}" if m else "")
          + "   (* = optional input, allowed to be absent)")
    for w in stale(c):
        print("WARNING:", w)
    if not stale(c):
        print("labelled dataset is newer than the wizard record and every decision file: up to date")
