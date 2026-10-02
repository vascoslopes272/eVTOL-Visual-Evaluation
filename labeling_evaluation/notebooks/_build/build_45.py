"""Generate notebooks/45_export_latex.ipynb (run with --run to execute it)."""
import subprocess
import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb = nbf.v4.new_notebook()
nb.cells = [
    md("# 45 — Export to LaTeX\n\n"
       "Collects every figure and table that notebooks 40–44 saved into one folder for the thesis:\n\n"
       "- `latex/figures/*.pdf` — vector figures, drawn at their printed width;\n"
       "- `latex/tables/*.tex` — booktabs tables;\n"
       "- `latex/figures.tex` — one `figure` block per figure (graphic, caption, label);\n"
       "- `latex/tables.tex` — `\\input` of every table;\n"
       "- `latex/FIGURE_INDEX.md` — item → question → LaTeX label → file → source.\n\n"
       "It computes nothing: it only reads what the question notebooks saved. Re-run it after re-running any of them.\n\n"
       "In the thesis preamble: `\\usepackage{graphicx,booktabs,amssymb}`."),
    code("import sys, pathlib, re\n"
         "PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()\n"
         "sys.path.insert(0, str(PILLAR))\n"
         "import pandas as pd\n"
         "from viz import config, latex\n"
         "cfg = config.load()"),
    md("## Export"),
    code("res = latex.export(cfg)\n"
         "out = cfg.out('latex')\n"
         "print(len(res['figures']), 'figures and', len(res['tables']), 'tables written to', out)"),
    md("## Check the LaTeX\n\nEvery file must have balanced braces and matching `\\begin`/`\\end`; every figure block must point at a PDF that exists."),
    code("def balanced(s):\n"
         "    s = re.sub(r'\\\\[{}]', '', s)\n"
         "    depth = 0\n"
         "    for ch in s:\n"
         "        depth += (ch == '{') - (ch == '}')\n"
         "        if depth < 0: return False\n"
         "    return depth == 0\n"
         "rows = []\n"
         "for f in [out / 'figures.tex', out / 'tables.tex', *sorted((out / 'tables').glob('*.tex'))]:\n"
         "    s = f.read_text(encoding='utf-8')\n"
         "    envs = re.findall(r'\\\\(begin|end)\\{(\\w+)\\}', s)\n"
         "    ok_env = sum(1 for b, e in envs if b == 'begin') == sum(1 for b, e in envs if b == 'end')\n"
         "    rows.append(dict(file=f.name, braces=balanced(s), environments=ok_env))\n"
         "missing = [p for p in re.findall(r'figures/([\\w.-]+\\.pdf)', (out / 'figures.tex').read_text()) if not (out / 'figures' / p).exists()]\n"
         "chk = pd.DataFrame(rows)\n"
         "assert chk[['braces', 'environments']].all().all() and not missing, (chk, missing)\n"
         "print('all files balanced; every figure PDF present')\n"
         "chk"),
    md("## Index"),
    code("print((out / 'FIGURE_INDEX.md').read_text(encoding='utf-8'))"),
    md("## One example block, as it goes into the thesis"),
    code("print(res['figures'][0] if res['figures'] else 'no figures yet')"),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
p = HERE / "45_export_latex.ipynb"
nbf.write(nb, p)
print("written", p)
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", str(p)], check=True)
