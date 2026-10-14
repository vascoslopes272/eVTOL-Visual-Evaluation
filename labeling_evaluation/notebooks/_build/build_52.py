"""Generate notebooks/52_thesis_figures_v2_part3.ipynb (python3 notebooks/_build/build_52.py [--run]).
Part III (Dominant design): viz/thesis_v2_part3.py ITEMS, standard figure-notebook layout (figure_notebook.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_notebook import build
import nbformat as nbf

GROUPS = [("III1_architecture_shares", "III1. Architecture shares", "How does each architecture's share of the designs move across cohorts, and which trends are monotonic?"),
          ("III2_III3_dominant_design", "III2 and III3. Dominant design", "Does one level of description, A (architecture), A·W·T, A·U or the family F, meet the three conditions: share above half, balance below the band, form below the band?"),
          ("III4_directory_categories", "III4. The directory's five categories", "Do the conditions hold when the twelve architectures are folded to the five categories of the public directory?")]
SOURCES = """- **The patent dataset** (627 designs): the author's characterisation of the patent drawings, read through `viz/thesis_q6.py`, `thesis_q7.py` and `viz/analysis3.py`. This notebook only draws.
- **Legal status** (PatSeer, snapshot 2026-06-08): *actively protected* = at least one linked patent in force; *granted and live* = at least one granted patent in force.
- **Directory categories**: `analysis.class_fold` of `labelling_analysis.yaml` (SLC, SRW → LC; TR, TW, CVT, TB, PTC, DS → VT; MR → WM; RC → ER; HB, PFV → HB), the fold of the evtol.news comparison; Table architectureFold of Appendix D was not available to check against.
- **Permutations**: 200, seed 42; ²D rarefied to 40 designs. Disparity is not rerun for III4.
- **Terms used in the figures:** architecture, design, cohort (a window of priority years), assignee; levels of description A = architecture alone, A·W·T = architecture, number of wings and whether any propulsor tilts, A·U = architecture and propulsor-unit band; F = Lift + Cruise + CVT* family."""

build(52, "Thesis figures, Part III (Dominant design)", "viz.thesis_v2_part3", GROUPS, SOURCES, "write_readme_52.py",
      "thesis_figures_v2/Part_III_dominant_design", run="--run" in sys.argv,
      extra_cells=[nbf.v4.new_markdown_cell("## Hand-over to the dissertation (LaTeX_v15)\n\nThe four figures that stay in the text and the two that leave it, redrawn at their final width in the 16 cm text block (1.0, 0.9, 0.85, 1.0; height at most 55 % of the width), with the data behind every figure and table, `NUMBERS_III.md` and the manifest lines. Nothing is recomputed differently; the builders are those above."),
                   nbf.v4.new_code_cell("from viz import thesis_latex_part3 as hand\nchk = hand.export(cfg, ctx)\ndisplay(chk)\nprint('all pass' if (chk['text over text'] == 0).all() and (chk['under 7 pt'] == 0).all() and (chk['height / width'] <= 0.55).all() else 'FIX NEEDED')\nprint(hand.root(cfg))")])
