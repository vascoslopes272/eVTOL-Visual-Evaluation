"""Generate notebooks/51_thesis_figures_v2_part4.ipynb (python3 notebooks/_build/build_51.py [--run]).
Part IV (Evolution of the design space): viz/thesis_v2_part4.py ITEMS, standard figure-notebook layout (figure_notebook.py),
plus a cell that prints the numbers the text quotes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nbformat as nbf
from figure_notebook import build

GROUPS = [("IV1_layout_convergence", "IV1. Layout convergence", "Does each architecture converge on one layout?"),
          ("IV2_attributes_and_drivers", "IV2. Attributes and drivers", "Which attributes change, and which design drivers explain the change?"),
          ("IV3_centre_and_disparity", "IV3. Centre and disparity", "Does the centre of the design space move while disparity holds?")]
SOURCES = """- **The patent dataset** (627 designs): the author's characterisation of the patent drawings, read through `viz/thesis_q6.py` (the frames and builders of the seven existing figures, run unchanged and only relabelled and restyled; frame `cf` for the two new ones), `lib/drivers.py` (Spearman test), `lib/dominant_design.py` (Rao's Q, permutation band) and `viz/frames.py` (Gower distance, subsystem weights). This notebook only draws.
- No external input.
- **Terms used in the figures:** architecture, cohort (a window of priority years), configuration; Tilt Propulsor, CVT (combined vectored thrust), Tilt Wing. ρ and p are Spearman against the priority year, every year to 2023. Distance of a cohort from the first = mean Gower distance between the designs of the two cohorts minus the mean of their two Rao's Q; band = 1000 shuffles of designs across cohorts (seed 42, cohort sizes kept), 2.5th to 97.5th percentile."""

p = build(51, "Thesis figures, Part IV (Evolution of the design space)", "viz.thesis_v2_part4", GROUPS, SOURCES, "write_readme_51.py",
          "thesis_figures_v2/Part_IV_design_space_evolution", run=False)
nb = nbf.read(p, as_version=4)
i = next(k for k, c in enumerate(nb.cells) if c.source.startswith("## Layout check"))
nb.cells[i:i] = [nbf.v4.new_markdown_cell("## Numbers for the text\n\nRecomputed from the same frames the figures draw; nothing typed. The *QUOTED* blocks are the numbers the thesis text states, each with the text's value in its heading."),
                 nbf.v4.new_code_cell("from viz import thesis_v2_part4 as p4\nfor k, val in p4.numbers(ctx).items():\n    print('\\n' + k)\n    print(val.to_string() if hasattr(val, 'to_string') else val)")]
nb.cells += [nbf.v4.new_markdown_cell("## Hand-over to the dissertation (LaTeX_v15)\n\nThe layout figure (three rows, final width 16 cm) and the centroid figure (leaves the text) remade at their final width, height at most 55 % of the width, text 7 pt or more; the data behind them, `NUMBERS_IV.md` and the manifest lines are written to `LaTeX_v15/`. No number changes."),
             nbf.v4.new_code_cell("from viz import thesis_latex_part4 as l4\nl4.export(cfg, ctx)"),
             nbf.v4.new_markdown_cell("### Representative aircraft for IV.2\n\n`q6_iv2_representative_aircraft`: one patent drawing per architecture and cohort of the leading layout (PICKS in `viz/thesis_latex_part4.py`); patent numbers and reasons in the CSV and `NUMBERS_IV.md`."),
             nbf.v4.new_code_cell("dims, chk, rep = l4.export_representative(cfg, ctx)\nprint('cm', dims, '| text over text, under 7 pt:', chk)\nrep.drop(columns=['image path', \"layout in the figure's frame\"]).T"),
             nbf.v4.new_markdown_cell("### Representative aircraft for IV.2, alternatives\n\n`q6_iv2_representative_aircraft_alt`: the same six cells with a top view for CVT 2020-23 and a Tilt Propulsor 2020-23 drawing whose propulsor units equal the cohort median (PICKS_ALT)."),
             nbf.v4.new_code_cell("dims, chk, alt = l4.export_representative(cfg, ctx, picks=l4.PICKS_ALT, stem='q6_iv2_representative_aircraft_alt')\nprint('cm', dims, '| text over text, under 7 pt:', chk)\nalt[alt['cohort'] == '2020-23'].drop(columns=['image path']).T")]
nbf.write(nb, p)
if "--run" in sys.argv:
    import subprocess
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.timeout=1800", str(p)], check=True)
