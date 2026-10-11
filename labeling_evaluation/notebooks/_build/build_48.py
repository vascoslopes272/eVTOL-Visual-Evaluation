"""Generate notebooks/48_thesis_figures_v2_part1.ipynb (run with --run to execute it).

    python3 notebooks/_build/build_48.py          # write the notebook
    python3 notebooks/_build/build_48.py --run    # write, then jupyter nbconvert --execute --inplace

Part I (Evidence base) of the thesis, v2: reorganised, relabelled and simplified figures for a subset of the
Q1 / Q4 / Q5 items (viz/thesis_v2_part1.py; ITEMS). Every computation is read unchanged from thesis_q1.py /
thesis_q4.py / thesis_q5.py; this notebook only draws, relabels and writes them to
thesis_figures_v2/Part_I_evidence_base/, a sibling of thesis_figures/ that the original is never written to.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
PILLAR = HERE.parent
sys.path.insert(0, str(PILLAR))
from viz import thesis_v2_part1 as v2  # noqa: E402

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []

cells.append(md("""# 48 — Thesis figures, Part I (Evidence base), v2

Reorganised, relabelled and simplified versions of the Part I figures, grouped by sub-question instead of by
thesis question, with one shared terminology (designs, patent families, architecture, archetype) and the
twelve architecture codes of `viz/thesis_v2_part1.ARCH_NAME_OVERRIDE` / `style.py`. No number or computation
changes: every builder calls into `viz/thesis_q1.py`, `thesis_q4.py` or `thesis_q5.py` for the underlying
frame and only re-draws it. Written to

    <output>/thesis_figures_v2/Part_I_evidence_base/I1_patenting_rate/{main,auxiliary,appendix}/
    <output>/thesis_figures_v2/Part_I_evidence_base/I2_active_protection/main/
    <output>/thesis_figures_v2/Part_I_evidence_base/I3_construct_validity/{main,auxiliary}/
    <output>/thesis_figures_v2/Part_I_evidence_base/I4_external_validity/{main,appendix}/

a sibling of `thesis_figures/`, which this notebook never writes into. See the folder's own README.md for the
file-by-file role and the fold mapping. Regenerate with `python3 notebooks/_build/build_48.py --run`."""))

cells.append(md("## 0. Setup\n\nSame dataset and context as notebook 46 (627 unique designs)."))
cells.append(code("""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from viz import config, thesis
from viz import thesis_v2_part1 as v2
cfg = config.load()
ctx = thesis.context(cfg)
OUT = v2.out_root(cfg)
print(len(ctx.v), 'unique designs; writing to', OUT)

def item(name):
    it = next(i for i in v2.ITEMS if i['name'] == name)
    v2.save_v2_item(it, cfg, ctx)
    obj, data = it['builder'](ctx)
    print(it['group'], '|', it['role'], '|', it['source_item'])
    if it['kind'] == 'figure':
        plt.show()
    else:
        display(obj)
    plt.close('all')
    return data"""))

GROUPS = [("I1_patenting_rate", "I1. Patenting rate"), ("I2_active_protection", "I2. Active protection"),
          ("I3_construct_validity", "I3. Construct validity"), ("I4_external_validity", "I4. External validity")]
ROLES = ("main", "auxiliary", "appendix")

for gkey, gtitle in GROUPS:
    cells.append(md(f"## {gtitle}"))
    for role in ROLES:
        its = [it for it in v2.ITEMS if it["group"] == gkey and it["role"] == role]
        if not its:
            continue
        cells.append(md(f"### {gkey} — {role.capitalize()}"))
        for it in its:
            cells.append(md(f"#### {it['title']}\n\n*(from {it['source_item']})*"))
            cells.append(code(f"item('{it['name']}')"))

cells.append(md("## README and file list\n\nRewrite the folder's README.md (file-by-file role and fold mapping) and list every file written."))
cells.append(code("""import subprocess
print(subprocess.run([sys.executable, str(PILLAR / 'notebooks' / '_build' / 'write_readme_48.py')],
                     capture_output=True, text=True).stdout)
sorted(p.relative_to(OUT) for p in OUT.rglob('*') if p.is_file())"""))

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "48_thesis_figures_v2_part1.ipynb"
nbf.write(nb, p)
print("written", p, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
