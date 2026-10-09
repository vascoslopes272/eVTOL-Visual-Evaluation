"""Generate notebooks/46_thesis_figures_by_question.ipynb (run with --run to execute it).

    python3 notebooks/_build/build_46.py          # write the notebook
    python3 notebooks/_build/build_46.py --run    # write, then jupyter nbconvert --execute --inplace

One section per thesis question (Q1–Q7, the order of the author's index), each with a Results part and an Appendix
part; one cell per graph or table. The items come from viz/thesis_qN.py at build time, so the notebook lists them
explicitly (a reader sees every graph by name). Numbers per question go to numbers.json; the text checks of
viz/thesis_run run at the end of each question.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
PILLAR = HERE.parent
sys.path.insert(0, str(PILLAR))
from viz import thesis  # noqa: E402

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []

cells.append(md("""# 46 — The thesis graphs, by question

Every graph and table of the thesis analysis chapter, drawn one per file and saved per question and per slot:

    <output>/thesis_figures/Q1_growth/results/   … /appendix/      (pdf, png, csv, json per item; numbers.json per question)

The seven questions are the author's index (`viz/thesis.QUESTIONS`); what each graph is and where it comes from in the
45-page document is in `viz/thesis_qN.py` (ITEMS). Numbers the document quotes are computed in `numbers(ctx)` of the same
module, never typed. Notebooks 40–44 remain the computation and the check against the document; this notebook only
draws what the thesis prints. Regenerate it with `python3 notebooks/_build/build_46.py`."""))
cells.append(md("## 0. Setup\n\nPaths from `labelling_analysis.yaml`; the analysis frame (627 unique aircraft) built once."))
cells.append(code("""import sys, pathlib, importlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
from viz import config, thesis, thesis_run
cfg = config.load()
ctx = thesis.context(cfg)
OUT = cfg.out('thesis_figures')
print(len(ctx.v), 'unique aircraft;', 'output:', OUT)

def item(mod, name):
    it = next(i for i in mod.ITEMS if i['name'] == name)
    obj, data = it['builder'](ctx)
    path = thesis.save_item(it, obj, data, cfg)
    print(it['slot'], '|', it['source_item'], '|', ('FLAG ' + it['flag'] + ': ' + it['flag_note']) if it['flag'] else '', '->', path.name)
    if it['kind'] == 'figure':
        plt.show()
    else:
        display(obj)
    return path"""))

cells.append(md("## Common numbers\n\nThe dataset, the unit of analysis, the windows and the publication lag, as the Methodology quotes them; then the chapter-level flowcharts of the Methodology (`thesis_common.METHOD_ITEMS`), saved to `common/`."))
cells.append(code("""from viz import thesis_common
import json
nums = thesis_common.numbers(ctx)
p = OUT / 'common' / 'numbers.json'; p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps(nums, indent=1, ensure_ascii=False), encoding='utf-8')
for it in thesis_common.METHOD_ITEMS:                       # common_chapter_flow, common_data_flow
    fig, _ = it['builder'](ctx)
    print(it['slot'], '|', it['title'], '->', thesis_common.save_common(it, fig, cfg))
    plt.show()
pd.Series(nums, name='value').to_frame()"""))

modules = []
for qid, slug, part, question in thesis.QUESTIONS:
    n = qid[1]
    mod = importlib.import_module(f"viz.thesis_q{n}")
    modules.append(mod)
    cells.append(md(f"## {qid}. {question}\n\n*{part}.* Module `viz/thesis_q{n}.py`; text `viz/thesis_text_q{n}.py`."))
    cells.append(code(f"from viz import thesis_q{n} as m{n}\nimportlib.reload(m{n})\nprint(len(m{n}.ITEMS), 'items')"))
    for slot in thesis.SLOTS:
        its = [it for it in mod.ITEMS if it["slot"] == slot]
        if not its:
            continue
        cells.append(md(f"### {qid} — {slot.capitalize()}"))
        for it in its:
            sub = f"{it['sub']}. " if it["sub"] else ""
            flag = f" — **{it['flag']}**: {it['flag_note']}" if it["flag"] else ""
            cells.append(md(f"#### {sub}{it['title']}\n\n{it['caption']} *(from {it['source_item']})*{flag}"))
            cells.append(code(f"item(m{n}, '{it['name']}')"))
    cells.append(md(f"### {qid} — numbers and text checks\n\nEvery number the {qid} text quotes, written to `numbers.json`; then the text module is checked (unresolved placeholders, missing references, density)."))
    cells.append(code(f"""nums = thesis_run.write_numbers('{qid}', ctx)
problems = thesis_run.check_text('{qid}', nums, [i['name'] for i in m{n}.ITEMS])
print('\\n'.join(problems) if problems else 'text checks: clean')
pd.Series(nums, name='value').to_frame()"""))

cells.append(md("## Figure map\n\nOne row per item: question, sub-question, slot, where it comes from, the author's flag, and the folder."))
cells.append(code("""mods = [importlib.import_module(f'viz.thesis_q{q[1]}') for q, *_ in thesis.QUESTIONS]
fm = thesis.figure_map(cfg, mods)
print(len(fm), 'items ->', OUT / 'FIGURE_MAP.csv')
fm[['question', 'sub', 'slot', 'kind', 'name', 'from document', 'flag']]"""))

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "46_thesis_figures_by_question.ipynb"
nbf.write(nb, p)
print("written", p, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
