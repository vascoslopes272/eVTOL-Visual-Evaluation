"""The printed wording of every figure, table and number file (CONVENTIONS.md term rules; author's ruling 2026-10-15).

Labels only: nothing here touches a number, a computation or a layout choice. The rules are applied where text leaves the code:

* every matplotlib text (title, axis label, tick label, legend, annotation, note): ``Text.set_text`` is wrapped, so the text is
  final before any label-placement code measures it (in a figure "aircraft" is a count of designs: "design(s)"; in a table or number file it is left as the data names it);
* the headers and the text cells of every CSV written under the output folders (``DataFrame.to_csv``);
* every .json and .md written under the output folders (``Path.write_text``).

Identifiers (file names, ``q6_...`` item names, snake_case data codes) are never touched: every rule works on whole words, and an underscore
joins a word to its identifier. The EASA term "lift/thrust unit" has a slash, so no rule reaches it.
``install()`` is idempotent and is called when ``viz`` is imported.
"""
from __future__ import annotations

import re
from pathlib import Path

#: where the figures, tables and numbers are written (the Drive output folder of the thesis)
OUTPUT_MARK = "labelling_analysis_thesis"
WARNINGS: list = []


def _case(src: str, low: str) -> str:
    """The replacement in the case of the word it replaces (Firms -> Assignees, firms -> assignees)."""
    return low[:1].upper() + low[1:] if src[:1].isupper() else low


def _w(pattern: str, low: str):
    return re.compile(pattern), (lambda m, low=low: _case(m.group(0), low))


#: (pattern, replacement) in order; a replacement is a string (regex template) or a function of the match
RULES = [
    # levels of description
    (re.compile(r"\bC·W·T"), "A·W·T"),
    (re.compile(r"\bC·U"), "A·U"),
    # propulsor units -> propulsors (the lowest band is 0-3)
    (re.compile(r"\b([Pp]ropulsor|[Pp]ropulsive)[- ]units? bands?\b"), lambda m: _case(m.group(1), "propulsor band" if "bands" not in m.group(0) else "propulsor bands")),
    (re.compile(r"\b([Pp]ropulsor|[Pp]ropulsive)[- ]units\b"), lambda m: _case(m.group(1), "propulsors")),
    (re.compile(r"\b([Pp]ropulsor|[Pp]ropulsive)[- ]unit\b"), lambda m: _case(m.group(1), "propulsor")),
    (re.compile(r"\bunits on booms\b"), "propulsors on booms"),
    (re.compile(r"\bfixed units\b"), "fixed propulsors"),
    (re.compile(r"\blift units\b"), "lift propulsors"),
    (re.compile(r"\b(\d+(?:\.\d+)?) units\b"), r"\1 propulsors"),
    (re.compile(r"(?<!thrust )\b([Uu])nits\b"), lambda m: _case(m.group(1), "propulsors")),      # every other "unit(s)" is a propulsor; "lift/thrust unit" stays
    (re.compile(r"(?<!thrust )\b([Uu])nit\b"), lambda m: _case(m.group(1), "propulsor")),
    (re.compile(r"(?<![\d.])1([-–])3(?![\d])"), r"0\g<1>3"),
    # architecture / assignee / cohort / configuration / Multicopter
    (re.compile(r"\bclasses\b"), "architectures"), (re.compile(r"\bClasses\b"), "Architectures"),
    (re.compile(r"\bclass\b"), "architecture"), (re.compile(r"\bClass\b"), "Architecture"),
    (re.compile(r"\b[Ff]irst-time (?:firms|filers)\b"), lambda m: _case(m.group(0), "new assignees")),
    (re.compile(r"\b[Ff]irst-time (?:firm|filer)\b"), lambda m: _case(m.group(0), "new assignee")),
    (re.compile(r"(?<![Ii]ndex )\b[Ff]irms\b"), lambda m: _case(m.group(0), "assignees")),
    (re.compile(r"(?<![Ii]ndex )\b[Ff]irm\b"), lambda m: _case(m.group(0), "assignee")),
    (re.compile(r"\b[Ff]ilers\b"), lambda m: _case(m.group(0), "assignees")),
    (re.compile(r"\b[Ff]iler\b"), lambda m: _case(m.group(0), "assignee")),
    (re.compile(r"\b[Oo]ut of force\b"), lambda m: _case(m.group(0), "not actively protected")),
    (re.compile(r"\bMulti-?rotors\b"), "Multicopters"), (re.compile(r"\bMulti-?rotor\b"), "Multicopter"),
    (re.compile(r"\bevtol\.news directory"), "VFS eVTOL directory"), (re.compile(r"\bevtol\.news\b"), "VFS eVTOL directory"),
    (re.compile(r"\bwindows\b"), "cohorts"), (re.compile(r"\bWindows\b"), "Cohorts"),
    (re.compile(r"\bwindow\b"), "cohort"), (re.compile(r"\bWindow\b"), "Cohort"),
    (re.compile(r"\barchetypes\b"), "configurations"), (re.compile(r"\bArchetypes\b"), "Configurations"),
    (re.compile(r"\barchetype\b"), "configuration"), (re.compile(r"\bArchetype\b"), "Configuration"),
]
#: axis labels only: "design(s)" as a count (never aircraft)
AXIS_RULES = [
    (re.compile(r"\bper aircraft\b"), "per design"), (re.compile(r"\ban aircraft\b"), "a design"),
    (re.compile(r"\baircraft\b"), "designs"), (re.compile(r"\bAircraft\b"), "Designs"),
]
#: any text: a number then aircraft is a count of designs
COUNT_RULES = [(re.compile(r"(?<=\d) aircraft\b"), " designs")]

_cache: dict = {}


def text(s, axis: bool = False):
    """The text with the term rules applied (non-strings come back unchanged)."""
    if not isinstance(s, str) or not s:
        return s
    key = (s, axis)
    r = _cache.get(key)
    if r is None:
        r = s
        for pat, rep in RULES + COUNT_RULES + (AXIS_RULES if axis else []):
            r = pat.sub(rep, r)
        if len(_cache) < 200000:
            _cache[key] = r
    return r


def frame(df):
    """A copy of ``df`` with the headers and the text cells relabelled. A header whose new name would repeat another column keeps its name (recorded in WARNINGS)."""
    out = df.copy()
    names = [text(c) if isinstance(c, str) else c for c in out.columns]
    seen: dict = {}
    final = []
    for old, new in zip(out.columns, names):
        if new in seen or (new != old and new in set(out.columns)):
            WARNINGS.append(f"header kept: {old!r} -> {new!r} would repeat a column")
            new = old
        seen[new] = 1
        final.append(new)
    out.columns = final
    for c in out.columns:
        if out[c].dtype == object:
            out[c] = out[c].map(lambda x: text(x) if isinstance(x, str) else x)
    return out


def _is_output(path) -> bool:
    try:
        return OUTPUT_MARK in str(path)
    except Exception:
        return False


_installed = False


def install():
    global _installed
    if _installed:
        return
    _installed = True
    import matplotlib.text as mtext
    import matplotlib.axis as maxis
    import pandas as pd

    orig_set_text = mtext.Text.set_text

    def set_text(self, s):
        return orig_set_text(self, text(s, axis=True) if isinstance(s, str) else s)

    mtext.Text.set_text = set_text

    orig_label = maxis.Axis.set_label_text

    def set_label_text(self, label, fontdict=None, **kwargs):
        return orig_label(self, text(label, axis=True) if isinstance(label, str) else label, fontdict, **kwargs)

    maxis.Axis.set_label_text = set_label_text

    orig_csv = pd.DataFrame.to_csv

    def to_csv(self, path_or_buf=None, *a, **k):
        if path_or_buf is not None and not hasattr(path_or_buf, "write") and _is_output(path_or_buf):
            return orig_csv(frame(self), path_or_buf, *a, **k)
        return orig_csv(self, path_or_buf, *a, **k)

    pd.DataFrame.to_csv = to_csv

    orig_write = Path.write_text

    def write_text(self, data, *a, **k):
        if _is_output(self) and self.suffix in (".json", ".md") and isinstance(data, str) and self.name.upper() != "README.MD":
            data = text(data)
        return orig_write(self, data, *a, **k)

    Path.write_text = write_text
