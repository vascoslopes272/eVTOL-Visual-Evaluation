"""Generate notebooks/50_thesis_figures_v2_part2.ipynb (python3 notebooks/_build/build_50.py [--run]).
Part II (Design space): viz/thesis_v2_part2.py ITEMS, standard figure-notebook layout (figure_notebook.py)."""
import sys
from pathlib import Path
import nbformat as nbf
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_notebook import build

GROUPS = [("II1_varying_attributes", "II1. Varying attributes", "Which dimensions tell designs apart, and how do propulsor number and ducting vary by architecture?"),
          ("II2_levels_of_description", "II2. Levels of description", "How many configurations does each level of description give: C (architecture), C·W·T (architecture, wings and tilt), C·U (architecture and propulsor units)?"),
          ("II3_distribution_and_new_variety", "II3. Distribution and new variety", "How are the designs spread over the configurations, and is new variety still appearing?")]
SOURCES = """- **The patent dataset** (627 designs): the author's characterisation of the patent drawings, read through `viz/thesis_q6.py` and `thesis_q7.py` unchanged. This notebook only draws.
- No external input: every number of Part II comes from the patent dataset itself.
- **Terms used in the figures:** configuration (a combination of attributes), assignee (who filed), cohort (a window of priority years); levels of description C = architecture, C·W·T = architecture, number of wings and whether any propulsor tilts, C·U = architecture and propulsor-unit band."""

build(50, "Thesis figures, Part II (Design space)", "viz.thesis_v2_part2", GROUPS, SOURCES, "write_readme_50.py",
      "thesis_figures_v2/Part_II_design_space", run="--run" in sys.argv,
      extra_cells=[nbf.v4.new_markdown_cell("## Hand-over to the dissertation (LaTeX_v15)\n\nAnalysis II: `q6_configuration_core` (0.9 of the 16 cm text block), `q6_discovery_curve` (1.0), `q6_propulsor_units_per_class` (0.8, appendix) and `q6_half_of_cohort` (0.8, leaves the text), each drawn at its final width, height at most 55 % of the width, text 7 pt or more, no title; the data behind every figure and the three tables; `NUMBERS_II.md`; the manifest lines. Nothing is recomputed differently; the builders are those above."),
                   nbf.v4.new_code_cell("from viz import thesis_latex_part2 as hand\nchk = hand.export(cfg, ctx)\ndisplay(chk)\nprint('all pass' if (chk['text over text'] == 0).all() and (chk['under 7 pt'] == 0).all() and (chk['height / width'] <= 0.55).all() else 'FIX NEEDED')\nprint(hand.root(cfg))")])
