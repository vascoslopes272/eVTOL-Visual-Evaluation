"""Generate notebooks/50_thesis_figures_v2_part2.ipynb (run with --run to execute it).

    python3 notebooks/_build/build_50.py          # write the notebook
    python3 notebooks/_build/build_50.py --run    # write, then jupyter nbconvert --execute --inplace

Part II (Design space) of the thesis, v2: relabelled, simplified and regrouped figures for a subset of the Q6 / Q7
items (viz/thesis_v2_part2.py; ITEMS). Every frame is read unchanged from thesis_q6.py / thesis_q7.py; this
notebook only draws, relabels and writes them to thesis_figures_v2/Part_II_design_space/, a sibling of
Part_I_evidence_base/ and of thesis_figures/ (never written into). (Notebook 49 is the LLM-input review, so this one is 50.)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
PILLAR = HERE.parent
sys.path.insert(0, str(PILLAR))
from viz import thesis_v2_part2 as v2  # noqa: E402

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []

cells.append(md("""# 50 — Thesis figures, Part II (Design space), v2

Relabelled, simplified and regrouped versions of the Part II figures, grouped by sub-question, with one shared
terminology (configuration, design, assignee, cohort, architecture; levels C, C·W·T, C·U). No number or
computation changes: every builder calls into `viz/thesis_q6.py` / `thesis_q7.py` for the underlying frame and
only re-draws it. Written to

    <output>/thesis_figures_v2/Part_II_design_space/II1_varying_attributes/{main,auxiliary,appendix}/
    <output>/thesis_figures_v2/Part_II_design_space/II2_levels_of_description/main/
    <output>/thesis_figures_v2/Part_II_design_space/II3_distribution_and_new_variety/{main,auxiliary}/

a sibling of `Part_I_evidence_base/` and of `thesis_figures/`, which this notebook never writes into. See the
folder's own README.md for the file-by-file role, the judgement calls and the number checks.
Regenerate with `python3 notebooks/_build/build_50.py --run`."""))

cells.append(md("## 0. Setup\n\nSame dataset and context as notebooks 46 and 48 (627 unique designs)."))
cells.append(code("""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from viz import config, thesis
from viz import thesis_v2_part2 as v2
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

GROUPS = [("II1_varying_attributes", "II1. Varying attributes"), ("II2_levels_of_description", "II2. Levels of description"),
          ("II3_distribution_and_new_variety", "II3. Distribution and new variety")]
for gkey, gtitle in GROUPS:
    cells.append(md(f"## {gtitle}"))
    for role in ("main", "auxiliary", "appendix"):
        its = [it for it in v2.ITEMS if it["group"] == gkey and it["role"] == role]
        if not its:
            continue
        cells.append(md(f"### {gkey} — {role.capitalize()}"))
        for it in its:
            cells.append(md(f"#### {it['title']}\n\n*(from {it['source_item']})*"))
            cells.append(code(f"item('{it['name']}')"))

cells.append(md("## README and file list\n\nRewrite the folder's README.md (files, roles, judgement calls, number checks) and list every file written."))
cells.append(code("""import subprocess
print(subprocess.run([sys.executable, str(PILLAR / 'notebooks' / '_build' / 'write_readme_50.py')],
                     capture_output=True, text=True).stdout)
sorted(p.relative_to(OUT) for p in OUT.rglob('*') if p.is_file())"""))

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "50_thesis_figures_v2_part2.ipynb"
nbf.write(nb, p)
print("written", p, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
