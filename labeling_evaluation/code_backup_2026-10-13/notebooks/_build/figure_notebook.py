"""The standard layout of every thesis figure notebook (author's ruling 2026-10-12: notebook 48's layout, for every one).

    build(number, title, module, groups, sources, readme_script, run=False)

Cells, in order:
  1. title + overview table (group, role, file, kind, what it shows) built from the module's ITEMS
  2. where the numbers come from (``sources``, markdown)
  3. look and layout rules (thesis style 1, the six rules, checked by viz/figcheck.py)
  4. setup: show(name) builds each item ONCE under the style, writes it, checks its layout, shows the written file
  5. one section per group (its question), one cell per item
  6. layout check table for every figure (must be all zeros)
  7. README rewrite and file list
The figure module must provide ITEMS (name, group, role, kind, title, source_item, builder), out_root(cfg) and
save_v2_item(item, cfg, ctx) -> (obj, data) drawn under viz/part1.mplstyle.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import nbformat as nbf

ROLES = ("main", "auxiliary", "appendix")
HERE = Path(__file__).resolve().parents[1]

RULES = """## Look and layout rules

Every figure is drawn under the author's thesis style, `viz/part1.mplstyle` (style 1, chosen 2026-10-12 among five in `viz/style_options/`):
Arial-type sans (Liberation Sans here), 9 pt labels, 8 pt ticks and legends, no top or right frame, a light horizontal grid, 6.3 in wide, PDF with embedded fonts.

The rules each figure is held to, and checked against in this notebook (`viz/figcheck.py`):

1. **No text on top of other text or of a mark.** Checked automatically: the check table at the end must read 0.
2. **Anything in columns is placed at fixed positions, never padded with spaces** (for example a numbered key), so rows line up exactly.
3. **One grid per plot**: a right-hand second axis draws no grid of its own.
4. **Words, not codes**: every abbreviation in a figure is spelled out in the figure or its key.
5. **No title inside the figure**: the caption in the thesis carries it.
6. **Nothing under 6.5 pt** at print size. Checked automatically."""

SETUP = """import sys, pathlib, importlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
from viz import config, thesis, figcheck
v2 = importlib.import_module('{module}')
cfg = config.load()
ctx = thesis.context(cfg)
OUT = v2.out_root(cfg)
print(len(ctx.v), 'designs | external inputs:', cfg.analysis.get('external_inputs', 'script'), '| writing to', OUT)
CHECKS = []
FORBIDDEN = {forbidden}

def show(name):
    \"\"\"Build the item once under the thesis style, write it, check its layout, and show the written file.\"\"\"
    it = next(i for i in v2.ITEMS if i['name'] == name)
    obj, data = v2.save_v2_item(it, cfg, ctx)
    folder = OUT / it['group'] / it['role']
    if it['kind'] == 'figure':
        final = bool(it.get('width'))
        rep = figcheck.final_figure_report(obj, width_in=it['width'] * v2.TEXT_W_IN if final else None,
                                           forbid=FORBIDDEN, floor_pt=7.0 if final else 6.5)
        ov = figcheck.overlaps(obj)
        row = {{'file': name, 'group': it['group'], 'role': it['role'], 'final size': final, **rep,
                'problems': '; '.join(f'{{a}} | {{b}}' for a, b in ov[:3])}}
        CHECKS.append(row)
        plt.close('all')
        display(Image(filename=str(folder / f'{{name}}.png'), width=760))
        bad = {{k: v for k, v in rep.items() if (isinstance(v, bool) and not v) or (not isinstance(v, (bool, float)) and v not in (0,))}}
        print(('layout OK' if not bad else f'CHECK: {{bad}} {{ov[:3]}}'), '|', folder / f'{{name}}.pdf')
    else:
        CHECKS.append({{'file': name, 'group': it['group'], 'role': it['role'], 'final size': False, 'problems': 'table'}})
        display(obj)
        print(folder / f'{{name}}.csv')"""

CHECK = """chk = pd.DataFrame(CHECKS)
display(chk)
figs = chk[chk['problems'] != 'table']
num = [c for c in figs.columns if c in ('text over text', 'under 7 pt', 'under 6 pt', 'outside canvas', 'forbidden words')]
flags = [c for c in ('width_ok', 'height_ok') if c in figs.columns]
ok = all((figs[c].fillna(0) == 0).all() for c in num) and all(figs[c].dropna().astype(bool).all() for c in flags)
print('all figures pass' if ok else 'SOME FIGURES NEED A FIX (see the table)')"""

README = """import subprocess
print(subprocess.run([sys.executable, str(PILLAR / 'notebooks' / '_build' / '{script}')], capture_output=True, text=True).stdout)
files = sorted(p.relative_to(OUT) for p in OUT.rglob('*') if p.is_file())
print(len(files), 'files'); files"""


def build(number, title, module, groups, sources, readme_script, folder_note, run=False, forbidden=(), extra_cells=()):
    import importlib
    import sys
    sys.path.insert(0, str(HERE.parent))
    mod = importlib.import_module(module)
    md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    kind = lambda it: "figure" if it["kind"] == "figure" else "table"            # noqa: E731
    rows = "\n".join(f"| {g[1]} | {r} | `{it['name']}` | {kind(it)} | {it['title']} |"
                     for g in groups for r in ROLES for it in mod.ITEMS if it["group"] == g[0] and it["role"] == r)
    cells = [md(f"""# {number} — {title}

This notebook draws every figure and table of this part of the thesis and writes them, as PDF (for the thesis), PNG and CSV, to
`{folder_note}/<group>/<role>/`. Run it top to bottom; every cell shows exactly the file that was written.

| group | role | file | kind | what it shows |
|---|---|---|---|---|
{rows}

**Roles:** *main* goes in the chapter, *auxiliary* backs a statement of the chapter, *appendix* goes to the appendix."""),
             md("## Where the numbers come from\n\n" + sources), md(RULES), md("## Setup"), code(SETUP.format(module=module, forbidden=repr(forbidden)))]
    for gkey, gtitle, question in groups:
        cells.append(md(f"## {gtitle}\n\n*{question}*"))
        for role in ROLES:
            for it in [i for i in mod.ITEMS if i["group"] == gkey and i["role"] == role]:
                cells.append(md(f"### {it['title']}\n\n`{it['name']}` · {role} · {kind(it)} · from {it['source_item']}"))
                cells.append(code(f"show('{it['name']}')"))
    cells += [md("## Layout check, all figures\n\nEvery count must read 0 and every flag True: text over text, text under the font floor (7 pt for the figures printed in the dissertation, 6.5 pt for the others), text outside the canvas, forbidden words, the final width, and the height of at most 55 % of the width."), code(CHECK),
              *extra_cells,
              md("## README and file list\n\nRewrite the folder's README.md and list every file written."), code(README.format(script=readme_script))]
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = next(HERE.glob(f"{number}_*.ipynb"), None) or HERE / f"{number}_figures.ipynb"
    nbf.write(nb, p)
    print("written", p, len(cells), "cells")
    if run:
        subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
    return p
