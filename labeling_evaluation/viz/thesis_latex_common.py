"""Helpers shared by the five LaTeX_v15 exporters (latex_v15.py = Part I, thesis_latex_part2/3/4.py = Parts II-IV, latex_v15_partv.py = Part V).
No exporter imports another part's exporter; whatever two or more of them need lives here."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

TEXT_CM = 16.0          # text block of the dissertation
MAX_H = 0.55            # a figure is at most 55 % as tall as it is wide
MANIFEST_HEAD = "# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n"


def root(cfg) -> Path:
    """The LaTeX_v15/ folder, next to the other thesis outputs."""
    return cfg.out("thesis_figures").parent / "LaTeX_v15"


def tables_md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) if hasattr(df, "to_markdown") else df.to_string(index=False)


def drop_section(txt: str, heading: str) -> str:
    """``txt`` without the section that starts at the line ``heading`` (a markdown heading, '#'s included) and runs to the next heading of
    the same or a higher level, or to the end; every copy goes. A follow-up that inserts a section into a NUMBERS file calls this first, so a
    rerun replaces its section instead of adding a second one, whatever order the notebooks ran in."""
    level = len(heading) - len(heading.lstrip("#"))
    start, nxt = re.compile(rf"^{re.escape(heading)}[ \t]*$", re.M), re.compile(rf"^#{{1,{level}}} ", re.M)
    while m := start.search(txt):
        e = nxt.search(txt, m.end())
        txt = txt[:m.start()] + (txt[e.start():] if e else "")
    return txt
