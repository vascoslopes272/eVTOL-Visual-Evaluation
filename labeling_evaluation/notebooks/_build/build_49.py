"""Generate notebooks/49_review_llm_inputs.ipynb (run with --run to execute it).

    python3 notebooks/_build/build_49.py          # write the notebook
    python3 notebooks/_build/build_49.py --run    # write, then jupyter nbconvert --execute --inplace

Builds the four review/*_review.html pages for the LLM-sourced inputs behind Part I: evtol.news domain
classification, TRL, evtol.news development year, and the AAM Reality Index firm mapping. The sampling
(z=1.96, e=10%, seed 42, finite-population corrected) and every data choice are in
notebooks/_build/prepare_review_pages.py; this notebook just runs it and opens each page's local file:// link.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = []

cells.append(md("""# 49 — Review the LLM-sourced inputs behind Part I

Four of Part I's inputs were made by an LLM and are marked `review: later` in `labelling_analysis.yaml`:
TRL per design, the evtol.news development year, the AAM Reality Index firm-name mapping, and (rule-based,
but worth eyeballing) the evtol.news domain classification (cargo drones, hybrids, etc. excluded). This
notebook builds one review page per input in `review/`. No number or figure is touched here — these pages
are a read/decide loop over local HTML; their CSV exports are a separate, later step.

**Sampling**: 95% confidence, z = 1.96, p = 0.5, margin of error e = 10%, finite-population corrected — the
same equation `lib.intervals.wilson_fpc_interval` already applies elsewhere in the thesis. The domain review's
22 contradictions (excluded by the rule but linked to a patent in the dataset) and the 43 AAM firm names are
reviewed in full; the rest are a random sample (seed 42)."""))

cells.append(code("""import sys, pathlib, webbrowser
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
sys.path.insert(0, str(PILLAR / 'notebooks' / '_build'))
import prepare_review_pages as prep
prep.main()"""))

cells.append(md("## Open each page\n\nEach opens in your browser; decisions save to localStorage as you go, "
                "and \"export CSV\" writes the decisions out whenever you stop."))
cells.append(code("""REVIEW = PILLAR / 'review'
for name in ['domain_review.html', 'trl_review.html', 'year_review.html', 'ari_firm_review.html']:
    p = REVIEW / name
    print(p)"""))

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "49_review_llm_inputs.ipynb"
nbf.write(nb, p)
print("written", p, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=600", str(p)], check=True)
