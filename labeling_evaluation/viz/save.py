"""Save a thesis figure: vector PDF for LaTeX, PNG for preview, the plotted data, and the caption text.

    from viz import save
    save.figure(fig, cfg, "q1", "fig_01_filings_per_year", data=frame,
                caption="Unique aircraft per priority year.",
                source="labelled dataset (627 aircraft)", unit="unique aircraft",
                read="each bar is one priority year; hatched years are not complete yet")

Writes, inside <output>/<q>/figures/:  <name>.pdf  <name>.png  <name>.csv  <name>.json
No text is stamped inside the image: source / unit / how to read go to the .json and become the caption.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd


def figure(fig, cfg, q: str, name: str, data: Optional[pd.DataFrame] = None, caption: str = "",
           source: str = "", unit: str = "", read: str = "", panels: Optional[dict] = None) -> Path:
    out = cfg.out(q) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    for ext in cfg.style.get("formats", ["pdf", "png"]):
        fig.savefig(out / f"{name}.{ext}")
    if data is not None:
        data.to_csv(out / f"{name}.csv")
    meta = dict(name=name, caption=caption, source=source, unit=unit, how_to_read=read,
                panels=panels or {}, width_in=round(fig.get_figwidth(), 3),
                height_in=round(fig.get_figheight(), 3))
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return out / f"{name}.pdf"


def table(frame: pd.DataFrame, cfg, q: str, name: str, caption: str = "", source: str = "") -> Path:
    """The table as CSV (exact numbers) plus a .json with its caption; the LaTeX version is made by
    notebook 45 from these two files."""
    out = cfg.out(q) / "tables"
    out.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out / f"{name}.csv", index=False)
    (out / f"{name}.json").write_text(json.dumps(dict(name=name, caption=caption, source=source),
                                                 indent=1, ensure_ascii=False), encoding="utf-8")
    return out / f"{name}.csv"
