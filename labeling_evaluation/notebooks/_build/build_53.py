"""Generate notebooks/53_thesis_figures_v2_part5.ipynb (python3 notebooks/_build/build_53.py [--run]).
Part V (assignees and regions): viz/thesis_v2_part5.py ITEMS, standard figure-notebook layout (figure_notebook.py), plus the numbers for the text."""
import sys
from pathlib import Path

import nbformat as nbf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_notebook import HERE, build
sys.path.insert(0, str(HERE.parent))
from viz import analysis5 as a5

GROUPS = [(a5.FOLDER[s[0]], s[1], s[2]) for s in a5._SECTIONS]
SOURCES = """- **The patent dataset** (627 designs): the author's characterisation of the patent drawings, with the assignee and priority date of each design from PatSeer, read through `viz/thesis_q2.py`, `thesis_q3.py` and `thesis_q7.py` unchanged. This notebook only draws; the figures are the earlier ones with the labels changed.
- **Assignee of a design**: the first assignee of its representative patent. **Entrant**: an assignee whose first design falls in the cohort.
- No external input.
- **Terms used in the figures:** assignee, cohort (a window of priority years), architecture, configuration, design.
- Cut from the dissertation and not drawn here: `q3_firm_successions`, `q7_region_firm_proximity`, every funding figure."""

p = build(53, "Thesis figures, Part V (Assignees and regions)", "viz.thesis_v2_part5", GROUPS, SOURCES, "write_readme_53.py",
          "thesis_figures_v2/Part_V_assignees_and_regions", run=False)
nb = nbf.read(p, as_version=4)
i = next(k for k, c in enumerate(nb.cells) if c.cell_type == "markdown" and c.source.startswith("## Layout check"))
nb.cells[i:i] = [nbf.v4.new_markdown_cell("## Numbers for the text"),
                 nbf.v4.new_code_cell("from viz import analysis5 as a5\nn = a5.numbers_for_text(ctx)\na5.print_numbers(n)")]
nb.cells += [nbf.v4.new_markdown_cell('## Hand-over to the dissertation (LaTeX_v15)\n\nThe seven figures of Analysis V remade at their final width (text block 16 cm, height at most 55 % of the width, text 7 pt or more) by `viz/latex_v15_partv.py`, with the data behind each, `NUMBERS_V.md` and the manifest lines. Nothing is recomputed differently; the builders are those above.'),
             nbf.v4.new_code_cell("from viz import latex_v15_partv as hand\ninfos = hand.export_part_v(cfg, ctx)\nfor i in infos:\n    print(i['name'], i['width_cm'], 'x', i['height_cm'], 'cm | h/w', i['height_over_width'], '| smallest', i['smallest_pt'], 'pt | overlaps', len(i['overlaps']))")]
nbf.write(nb, p)
target = HERE / "53_thesis_figures_v2_part5.ipynb"
p.replace(target)
print("written", target, len(nb.cells), "cells")
if "--run" in sys.argv:
    import subprocess
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.timeout=1800", str(target)], check=True)
