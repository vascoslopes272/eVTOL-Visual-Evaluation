"""Generate notebooks/47_thesis_document.ipynb (run with --run to execute it)."""
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb = nbf.v4.new_notebook()
nb.cells = [
    md("# 47 — The thesis analysis document (LaTeX → PDF)\n\n"
       "Writes `<output>/thesis_document/main.tex` from the text modules (`viz/thesis_text_common.py`, `viz/thesis_text_qN.py`),\n"
       "the item registers (`viz/thesis_qN.py`) and what notebook 46 saved (graphs, tables, numbers), then compiles it with\n"
       "tectonic (path in `labelling_analysis.yaml: tools.tectonic`).\n\n"
       "Structure: Methodology → Results and discussion (three parts, seven questions, Answer box each) → Limitations →\n"
       "Appendix by question. Yellow = the author's open decisions (decide / verify / drop). It computes nothing: run notebook 46 first."),
    code("import sys, pathlib\n"
         "PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()\n"
         "sys.path.insert(0, str(PILLAR))\n"
         "import pandas as pd\n"
         "from IPython.display import display, Image\n"
         "from viz import config, thesis_doc\n"
         "cfg = config.load()"),
    md("## Build and compile"),
    code("pdf, report = thesis_doc.build(cfg)\n"
         "print(report['pages'], 'pages ->', pdf)\n"
         "print(report['items'], 'items placed;', len(report['missing']), 'missing')\n"
         "for m in report['missing']: print('  missing:', m)"),
    md("## The author's open decisions (yellow in the PDF)"),
    code("pd.DataFrame(report['flags'], columns=['question', 'item', 'flag', 'note'])"),
    md("## A look at the pages"),
    code("pages = thesis_doc.pages_png(pdf, pdf.parent / 'preview', dpi=50)\n"
         "print(len(pages), 'pages rendered to', pages[0].parent)\n"
         "for p in pages[:4]:\n"
         "    display(Image(filename=str(p), width=380))"),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "47_thesis_document.ipynb"
nbf.write(nb, p)
print("written", p)
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", str(p)], check=True)
