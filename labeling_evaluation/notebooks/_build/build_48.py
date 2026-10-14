"""Generate notebooks/48_thesis_figures_v2_part1.ipynb (python3 notebooks/_build/build_48.py [--run]).
Part I (Evidence base): viz/thesis_v2_part1.py ITEMS, standard figure-notebook layout (figure_notebook.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figure_notebook import build

GROUPS = [("I1_patenting_rate", "I1. Patenting rate", "How fast is eVTOL patenting growing, against aeronautics and all patents, and where is it filed?"),
          ("I2_active_protection", "I2. Active protection", "How many designs are still protected by a patent in force?"),
          ("I3_construct_validity", "I3. Construct validity", "Do the drawings read the public aircraft correctly, and do the mature and the index-firm designs stand for the rest?"),
          ("I4_external_validity", "I4. External validity", "Does the patent dataset look like the market, read through the evtol.news directory?")]
SOURCES = """- **The patent dataset** (627 designs): the author's characterisation of the patent drawings, read through `viz/thesis_q1.py`, `thesis_q4.py` and `thesis_q5.py` unchanged. This notebook only draws.
- **The external inputs** of I1, I3 and I4 (evtol.news domain flag and development year, TRL, AAM Reality Index company map) come from **rule-based scripts with no model**, with the author's reading where he reviewed an item. Lists and their agreement with the author: notebook 60, `review/script_outputs/`. Switch: `analysis.external_inputs` in `labelling_analysis.yaml` (`script`, the default; `reading` = the old inputs)."""

import nbformat as nbf
from viz import figcheck

EXPORT = [nbf.v4.new_markdown_cell("""## Export to LaTeX_v15

The figures printed in the dissertation, or delivered for it (`width` in `ITEMS`: the seven figures of the Analysis I remake), are copied to
`LaTeX_v15/Figures/Part_I_evidence_base/<group>/<role>/` as vector PDF at their **final width** (text block 16 cm), with the data behind each figure in
`LaTeX_v15/Data_for_writing/csv/`, the manifest `MANIFEST.md` (appended, never overwritten) and `NUMBERS_I.md` with every number the Results text of
Analysis I quotes, each with its source. The page size of every PDF is read back from the file (`pdfinfo`) and must match the final width, with a height of at most 55 % of the width."""),
          nbf.v4.new_code_cell("""from viz import latex_v15
rep = latex_v15.export_figures(cfg, v2)
display(rep)
print('all PDFs at their final width and within 55 % of it' if rep['width ok'].all() and rep['height ok (<= 0.55)'].all() else 'CHECK THE PDF SIZES ABOVE')
p = latex_v15.write_numbers_I(cfg, ctx)
print('written', p)
print('LaTeX_v15 files:', sorted(str(f.relative_to(latex_v15.root(cfg))) for f in latex_v15.root(cfg).rglob('*') if f.is_file()))""")]
build(48, "Thesis figures, Part I (Evidence base)", "viz.thesis_v2_part1", GROUPS, SOURCES, "write_readme_48.py",
      "thesis_figures_v2/Part_I_evidence_base", run="--run" in sys.argv, forbidden=figcheck.FORBIDDEN_PART1, extra_cells=EXPORT)
