"""The names the brief PRINTS, applied to finished text and to every figure label (2026-09-28).

The author renamed three terms across the whole document:

* the class **Tilt Rotor (TR)** becomes **Tilt Propulsor (TP)**;
* **propulsive unit** becomes **propulsor unit**, and a generic **rotor** becomes **propulsor**
  (class names such as Rotorcraft and Stopped/Slowed Rotor Wing keep their word);
* an **archetype level** becomes an **archetype set**.

The data keep their codes (``topType == "TR"`` everywhere in the code): only what is printed
changes, here, in one place. ``rename_text`` runs on the brief's markdown after it is written
(``report.write_markdown`` through ``sm_index.POST_TEXT``) and ``rename_figure`` on every text
artist of a figure just before it is saved, before the width fit, so wrapped labels still fit.
"""
import re

_RULES = [
    # 2026-09-29 (decision document, T6): "station" read as unclear; where the propulsor units
    # sit is a "place". The data keep "station" in their configuration names; only the print
    # changes, specific phrasings first
    (re.compile(r"\bstations carrying units\b"), "places carrying propulsor units"),
    (re.compile(r"\bon two or more stations\b"), "in two or more places"),
    (re.compile(r"\bon one station\b"), "in one place"),
    (re.compile(r"\bon (\w+) stations\b"), r"in \1 places"),
    (re.compile(r"\b2\+ stations\b"), "2+ places"),
    (re.compile(r"\bStations\b"), "Places"),
    (re.compile(r"\bstations\b"), "places"),
    (re.compile(r"\bStation\b"), "Place"),
    (re.compile(r"\bstation\b"), "place"),
    # the class: full name and code (the code only as a whole token: never inside "TRL")
    (re.compile(r"Tilt Rotors?\b"), "Tilt Propulsor"),
    (re.compile(r"\bTR\b"), "TP"),
    # propulsor units
    (re.compile(r"\bPropulsive units\b"), "Propulsor units"),
    (re.compile(r"\bpropulsive units\b"), "propulsor units"),
    (re.compile(r"\bPropulsive unit\b"), "Propulsor unit"),
    (re.compile(r"\bpropulsive unit\b"), "propulsor unit"),
    (re.compile(r"\bpropulsive-unit\b"), "propulsor-unit"),
    (re.compile(r"\bRotors\b"), "Propulsors"),
    (re.compile(r"\brotors\b"), "propulsors"),
    (re.compile(r"\brotor\b"), "propulsor"),
    # archetype sets (the two non-archetype uses of "level" are left alone)
    (re.compile(r"\bat which level of detail\b"), "in which archetype set"),
    (re.compile(r"\blevels of detail\b"), "archetype sets"),
    (re.compile(r"\blevel of detail\b"), "archetype set"),
    (re.compile(r"\barchetype levels\b"), "archetype sets"),
    (re.compile(r"\barchetype level\b"), "archetype set"),
    # always the full "archetype set": a bare "set" would clash with "tilting set"
    (re.compile(r"\ba level-window"), "an archetype-set window"),
    (re.compile(r"\blevel-windows?\b"), lambda m: m.group(0).replace("level", "archetype-set")),
    (re.compile(r"\bat (the |each |any |a named |every |three |four |the four |the class )?levels?\b"),
     lambda m: "in " + (m.group(1) or "") + ("archetype sets" if m.group(0).endswith("s")
                                             else "archetype set")),
    (re.compile(r"(?<!that )(?<!draws )(?<!archetype )\blevels\b"), "archetype sets"),
    (re.compile(r"(?<!that )(?<!draws )(?<!archetype )(?<!Readiness )(?<!readiness )\blevel\b(?! with)"),
     "archetype set"),
    (re.compile(r"\bLevels\b"), "Archetype sets"),
    (re.compile(r"(?<!Readiness )\bLevel\b"), "Archetype set"),     # never TRL's own "Level"
    (re.compile(r"\b([Aa]) archetype"), lambda m: m.group(1) + "n archetype"),
]

#: lines of markdown never touched: image paths and HTML tags carry file names and classes
_SKIP = re.compile(r"^\s*!\[")          # only image lines: their path must not change


def rename_text(text: str) -> str:
    out = []
    for line in text.split("\n"):
        if _SKIP.match(line):
            # keep the path of an image intact but rename its alt text
            if line.lstrip().startswith("!["):
                m = re.match(r"(\s*!\[)(.*?)(\]\(.*)", line)
                if m:
                    alt = m.group(2)
                    for rx, rep in _RULES:
                        alt = rx.sub(rep, alt)
                    line = m.group(1) + alt + m.group(3)
            out.append(line)
            continue
        for rx, rep in _RULES:
            line = rx.sub(rep, line)
        out.append(line)
    return "\n".join(out)


def rename_figure(fig) -> None:
    """Rename every text artist of a matplotlib figure (titles, labels, ticks, legends, notes).

    Tick labels are regenerated from the axis formatter at every draw, so renaming their Text
    objects is lost at save time: each axis formatter is wrapped instead (2026-09-28 fix)."""
    try:
        from matplotlib.text import Text
        from matplotlib.ticker import FuncFormatter
    except Exception:
        return
    try:                                   # tick labels only exist once the figure is drawn
        fig.canvas.draw()
    except Exception:
        pass
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for which in ("major", "minor"):
                get = axis.get_major_formatter if which == "major" else axis.get_minor_formatter
                put = axis.set_major_formatter if which == "major" else axis.set_minor_formatter
                orig = get()
                if getattr(orig, "_renamed", False):
                    continue
                # only text tick labels (class names, categories); numeric formatters need the
                # tick locations the axis hands them and would print nothing once wrapped
                if type(orig).__name__ not in ("FixedFormatter", "StrCategoryFormatter", "FuncFormatter"):
                    continue
                def _fmt(x, pos=None, _o=orig):
                    return rename_text(str(_o(x, pos)))
                new = FuncFormatter(_fmt)
                new._renamed = True
                try:
                    new.set_axis(axis)
                except Exception:
                    pass
                put(new)
    for t in fig.findobj(Text):
        s = t.get_text()
        if not s:
            continue
        new = s
        for rx, rep in _RULES:
            new = rx.sub(rep, new)
        if new != s:
            t.set_text(new)
