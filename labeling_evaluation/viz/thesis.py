"""The thesis layer: which graph goes where (notebook 46) and the shared context every item builder receives.

    from viz import thesis
    ctx = thesis.context(cfg)                      # data, frames, windows, widths, formatters — built once
    path = thesis.save_item(item, fig, data, cfg)  # <output>/thesis_figures/Q1_growth/results/<name>.{pdf,png,csv,json}

One thesis question = one module ``viz/thesis_qN.py`` exposing ``ITEMS`` (list of dicts, see ``ITEM_KEYS``)
and ``numbers(ctx) -> dict[str, str]``; its text lives in ``viz/thesis_text_qN.py`` (see THESIS_CONTRACT.md).
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import pandas as pd

#: thesis questions, in chapter order: (id, folder slug, part, question as the index words it)
QUESTIONS = [
    ("Q1", "growth",             "eVTOL sector stand-outs",                     "How fast does it grow, and where?"),
    ("Q2", "filers",             "eVTOL sector stand-outs",                     "Who fills the field, and does anyone control it?"),
    ("Q3", "regions",            "eVTOL sector stand-outs",                     "Do the regions, and the firms within them, take different routes?"),
    ("Q4", "representativeness", "Patents against the built and funded sector", "Do the patented aircraft stand for the aircraft that get built?"),
    ("Q5", "money",              "Patents against the built and funded sector", "Does the money follow the patents, in time and in design?"),
    ("Q6", "design_space",       "Convergence analysis",                        "Where do eVTOL designs concentrate, and how have they moved?"),
    ("Q7", "dominant_design",    "Convergence analysis",                        "Is there a dominant design?"),
]
SLOTS = ("method", "results", "appendix")      # method = flowcharts of the Methodology
KINDS = ("figure", "table")
FLAGS = (None, "decide", "verify", "drop")      # yellow in the document: author decides / re-verifies values / to be dropped
ITEM_KEYS = {
    "name":       "file stem, e.g. q1_filings_per_year (lowercase, underscores, starts with the question id)",
    "slot":       "results | appendix",
    "kind":       "figure | table",
    "sub":        "sub-question letter of the thesis index: A, B, C, D (or '' for an item outside the index)",
    "title":      "short title (≤ 8 words) printed in the notebook heading and the figure map",
    "caption":    "≤ 2 lines, what the graph shows (no Source/Unit/How-to-read inside it)",
    "source_item": "where it comes from in the 45-page document: 'Figure 13 (ii)', 'Table 8', 'new'",
    "flag":       "None | decide | verify | drop",
    "flag_note":  "one line for the author when flag is set, else ''",
    "builder":    "callable(ctx) -> (fig_or_frame, data_or_None): a matplotlib Figure for a figure, a DataFrame for a table",
    "source":     "data source tag for the json sidecar (as notebooks 40-44 use)",
    "unit":       "unit of analysis",
    "read":       "how to read, one clause, or ''",
}


def folder(qid: str) -> str:
    slug = next(s for i, s, _, _ in QUESTIONS if i == qid)
    return f"{qid}_{slug}"


def out_dir(cfg, qid: str, slot: str, make: bool = True) -> Path:
    assert slot in SLOTS, slot
    p = cfg.out("thesis_figures") / folder(qid) / slot
    if make:
        p.mkdir(parents=True, exist_ok=True)
    return p


def check_item(item: dict) -> None:
    missing = [k for k in ITEM_KEYS if k not in item]
    assert not missing, f"item {item.get('name')} misses {missing}"
    assert item["slot"] in SLOTS and item["kind"] in KINDS and item["flag"] in FLAGS, item["name"]
    assert item["name"].startswith(("q1_", "q2_", "q3_", "q4_", "q5_", "q6_", "q7_")), item["name"]


def save_item(item: dict, obj, data: Optional[pd.DataFrame], cfg) -> Path:
    """Write one graph or table to its question/slot folder; returns the pdf (figure) or csv (table) path."""
    check_item(item)
    qid = item["name"][:2].upper()
    out = out_dir(cfg, qid, item["slot"])
    name = item["name"]
    meta = {k: item[k] for k in ("name", "slot", "kind", "sub", "title", "caption", "source_item", "flag", "flag_note",
                                 "source", "unit", "read")}
    if item["kind"] == "figure":
        for ext in cfg.style.get("formats", ["pdf", "png"]):
            obj.savefig(out / f"{name}.{ext}")
        if data is not None:
            data.to_csv(out / f"{name}.csv")
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
        main = out / f"{name}.pdf"
    else:
        obj.to_csv(out / f"{name}.csv", index=False)
        main = out / f"{name}.csv"
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return main


def context(cfg) -> SimpleNamespace:
    """Everything an item builder needs, built once per notebook run (same names as notebooks 40-44 use)."""
    import inspect  # noqa: F401  (kept for builders that read defaults)
    import numpy as np
    from viz import data, frames, style
    style.apply(cfg)
    ds = data.load_dataset(cfg)
    v = frames.base(ds, cfg)
    WIN = frames.windows_from_config(cfg)
    WIN_NAMES = list(cfg.analysis["windows"])
    COMPLETE = [w for w in WIN_NAMES if "partial" not in w]
    W, _ = style.size(cfg, "full")
    HALF, _ = style.size(cfg, "half") if _has_half(style, cfg) else (W / 2, None)
    WSHORT = {"<= 2011": "≤2011", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23", "2024-26 (partial)": "24–26*"}
    thin = lambda n: f"{int(n):,}".replace(",", " ")          # 1 639
    pct = lambda x: f"{x:.0%}".replace("%", " %")             # 0.53 -> '53 %'
    pval = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"
    return SimpleNamespace(cfg=cfg, ds=ds, v=v, WIN=WIN, WIN_NAMES=WIN_NAMES, COMPLETE=COMPLETE, W=W, HALF=HALF,
                           WSHORT=WSHORT, SEED=cfg.analysis["random_seed"], thin=thin, pct=pct, pval=pval, np=np)


def _has_half(style, cfg) -> bool:
    try:
        style.size(cfg, "half")
        return True
    except Exception:
        return False


def figure_map(cfg, modules: list) -> pd.DataFrame:
    """One row per item of every question module: the map the author reads (written by notebook 46)."""
    rows = []
    for mod in modules:
        for it in mod.ITEMS:
            qid = it["name"][:2].upper()
            rows.append({"question": qid, "sub": it["sub"], "slot": it["slot"], "kind": it["kind"], "name": it["name"],
                         "title": it["title"], "from document": it["source_item"], "flag": it["flag"] or "",
                         "flag note": it["flag_note"], "folder": str(out_dir(cfg, qid, it["slot"], make=False))})
    df = pd.DataFrame(rows)
    df.to_csv(cfg.out("thesis_figures") / "FIGURE_MAP.csv", index=False)
    return df
