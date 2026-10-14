"""Generate notebooks/analysis5_figures.ipynb (python3 notebooks/_build/build_analysis5.py [--run]): every figure of Analysis V, V.1 to V.4,
drawn by viz/analysis5.py (the same builders as before, labels only changed), then the numbers for the text."""
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent))
from viz import analysis5 as a5

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
rows = "\n".join(f"| {s[1]} | `{it['name']}` | {it['kind']} | {it['title']} |" for s in a5._SECTIONS for it in a5.ITEMS if it["section"] == s[0])
cells = [md(f"""# Analysis V, all figures

One notebook for every figure of Analysis V. Run it top to bottom, or regenerate everything with `python3 -m viz.analysis5`.
Each cell writes PDF, PNG, CSV and JSON to `thesis_figures_v2/Part_V_assignees_and_regions/<section>/<main|appendix>/` under the file names used before, shows the figure and prints the numbers behind it.
Nothing is analysed here: the data, cohorts, helper functions and styles are those of `viz/thesis_q2.py`, `viz/thesis_q3.py` and `viz/thesis_q7.py`;
only the labels change (assignee, cohort, architecture, configuration).

| section | file | kind | what it shows |
|---|---|---|---|
{rows}

Left out on purpose, being cut from the dissertation: `q3_firm_successions`, `q7_region_firm_proximity` and every funding figure.
In `q2_largest_filers_share` the hollow diamonds of the AAM Reality Index and their legend are removed."""),
         md("## Setup"),
         code("""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
from IPython.display import display, Image
from viz import config, thesis, analysis5 as a5
cfg = config.load(strict=False)
ctx = thesis.context(cfg)
print(len(ctx.v), 'designs')

def show(name):
    \"\"\"Build, relabel and write one item; show the written file and the numbers behind it.\"\"\"
    path, data = a5.build_item(name, cfg, ctx)
    if path.suffix == '.pdf':
        display(Image(filename=str(path.with_suffix('.png')), width=760))
    print(path)
    print(a5.key_numbers(data))""")]
for key, title, question, names in a5._SECTIONS:
    cells.append(md(f"## {title}\n\n*{question}*"))
    for n, _ in names:
        it = next(i for i in a5.ITEMS if i["name"] == n)
        cells.append(md(f"### {it['title']}\n\n`{n}` · {it['kind']} · {it['slot']}"))
        cells.append(code(f"show('{n}')"))
cells += [md("## Numbers for the text"),
          code("""n = a5.numbers_for_text(ctx)
a5.print_numbers(n)""")]
nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "analysis5_figures.ipynb"
nbf.write(nb, p)
print("written", p, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
