"""Generate notebooks/56_supervisor_review_2.ipynb (python3 notebooks/_build/build_56.py [--run])."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
c = []
c.append(md("""# 56 — Supervisor's second review (October 2026): Holm register and threshold sensitivity

Run after notebooks 48, 50, 52, 51, 53, 54 and 55. The changes of the review that touch the main analysis (resampling counts set
to 1000, Holm columns next to every raw p, the rebuilt Figure 4.2) are in the modules those notebooks call. This notebook writes
the tables that only exist for the review. All the logic is in `viz/review2.py`.

| step | function | output (`LaTeX_v15/Data_for_writing/csv/`) |
|---|---|---|
| 2 Holm | `holm_register` | `holm_register.csv`: every test of the four families, raw p, Holm p, verdict at 0.05 before and after |
| 3a share rule | `fixed_share_tables`, `readable_architectures` | `q6_fixed_by_architecture[_detail]_share70.csv`, `_share90.csv` (80 % is the main table); at 20 designs: `…_min20_share70/80/90.csv`; `q6_fixed_by_architecture_readable.csv` |
| 3b rarefaction | `rarefied_hill_table`, `edge_cell` | `q7_hill_by_cohort_rarefied30.csv`, `…40.csv`, `…50.csv`; `q7_condition2_awt_2020_23_by_rarefaction.csv` |
| 4.2.3 | `q4.pairwise`, `funnel_steps`, `publication_lead` | `q4_coding_agreement.csv` (with Cohen's kappa), `q4_funnel_steps.csv`, `q4_publication_lead.csv`, `q4_publication_lead_summary.csv` |
| 3c acceptance | `acceptance_table` | `script_acceptance_thresholds.csv` (also `review/decisions/ACCURACY_THRESHOLD_SENSITIVITY.csv`) |

What changed and why is in `../RERUN_NOTES_2026-10.md` at the repository root."""))
c.append(code("""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
from IPython.display import display
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_colwidth', 80)
from viz import config, thesis, review2
cfg = config.load()
ctx = thesis.context(cfg)"""))
c.append(md("## Step 2. Holm within each family\n\nFamilies: I.2 the directory readings against the dataset; II.1 the dimensions of Table 4.3; III.1 the architectures, one family per span; V the region × measure chi-squares, one family per assignee reading, and the regional trends, one family."))
c.append(code("""hr = review2.holm_register(ctx)
display(hr.groupby('family', sort=False).agg(tests=('p', 'size'), below_raw=('below 0.05, raw', 'sum'), below_holm=('below 0.05, Holm', 'sum')))
display(hr[hr['verdict changes']])"""))
c.append(md("## Step 3a. The 80 % share rule at 70 % and 90 %\n\nOnly the column of architectures where the leading option holds the share moves; V and p are the same shuffles."))
c.append(code("""from viz import thesis_v2_part2 as p2
base = p2._fixed_tables(ctx)[0]
tabs = review2.fixed_share_tables(ctx, (0.70, 0.90))
cmp = base[['dimension', 'architectures at 80 % or more']].copy()
for s, (t1, _) in tabs.items():
    cmp[f'at {round(100 * s)} %'] = t1[f'architectures at {round(100 * s)} % or more']
display(cmp)"""))
c.append(md("### 3a, second reading: an architecture read from 20 designs (2026-10-22)\n\nThe code reads an architecture from 10 answering designs (`thesis_q6.FIXED_MIN_DESIGNS`); the dissertation's 80 % table reads it from 20. The three shares again at 20, and which architectures each rule reads per dimension."))
c.append(code("""t20 = review2.fixed_share_tables(ctx, (0.70, 0.80, 0.90), min_designs=review2.MIN_READ_THESIS)
cmp20 = t20[0.80][0][['dimension']].copy()
for s, (t1, _) in t20.items():
    cmp20[f'at {round(100 * s)} %'] = t1[f'architectures at {round(100 * s)} % or more']
display(cmp20)
display(review2.readable_architectures(ctx))"""))
c.append(md("## Step 3b. Rarefied to 30, 40 (main) and 50 designs\n\nThe smallest complete cohort is 2012-15 with 58 designs, so every size draws without replacement from every complete cohort. The partial cohort 2024-26 is listed and never read."))
c.append(code("""h = review2.rarefied_hill_table(ctx)
read = h[~h['partial cohort (not read)']]
display(read.pivot_table(index=['level', 'cohort'], columns='rarefied to n', values=['²D', 'band low', 'below band (condition 2 met)'], aggfunc='first'))"""))
c.append(md("The one cell that changes with the size, A·W·T in 2020-23 (all designs): observed ²D, the middle 95 % of its rarefaction draws, the permutation band and the distance to its lower edge."))
c.append(code("""display(review2.edge_cell(ctx, h=h))"""))
c.append(md("## Step 3c. Acceptance threshold of the script inputs\n\nThe rule in `review/HOW_THE_REVIEWS_WERE_DONE.md` accepts a source when the lower bound of its 95 % Wilson interval is at or above the threshold (default 90 %). Both readings, point share and lower bound, are shown at 60, 70, 80 and 90 %."))
c.append(code("""display(review2.acceptance_table())"""))
c.append(md("""## Section 4.2.3 (2026-10-22): agreement as Cohen's kappa, the funnel, the lead from the first publication

No new reading of any patent. Kappa: `viz/thesis_q4.py: pairwise` (the public aircraft's label rebuilt per pair from the existing match
record, `public_labels`; asserted to give back Table 2's agreement counts). Funnel and lead: `viz/review2.py`."""))
c.append(code("""from viz import thesis_q4 as q4
display(q4.pairwise(ctx)[['comparison', 'agree', 'of', 'share', "Cohen's kappa"]])
display(review2.funnel_steps(ctx).set_index('population').T)
display(review2.publication_lead(ctx))
display(review2.publication_lead_summary(ctx))"""))
c.append(md("""## B64 without its drone and VTOL parts (2026-10-22)

Is the 2016 step of aeronautics made by drones (B64U) or by the VTOL class itself (B64C 29/00)? The same three models and bootstrap as Fig 4.2,
2005-2022, on B64 with each part left out. Needs two PatSeer exports in `assets/external/aviation_baseline/patseer_worldwide/` (see
`review2.B64_PARTS`); without them this cell says so and writes nothing."""))
c.append(code("""rf = review2.b64_refits(ctx)
if rf is None:
    print('not run: export', list(review2.B64_PARTS.values()), 'to', review2.B64_DIR)
else:
    display(rf['models'][['series', 'model', 'ΔAIC', 'ΔBIC', 'wins clearly']])
    display(rf['estimates'][rf['estimates']['model'].str.startswith('(a)')][['series', 'break year', 'break low', 'break high', 'level step (factor)', 'step low', 'step high']])"""))
c.append(md("## Write every table"))
c.append(code("""for p in review2.write_all(cfg, ctx):
    print(p)"""))

nb = nbf.v4.new_notebook(cells=c, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
out = HERE / "56_supervisor_review_2.ipynb"
nbf.write(nb, out)
print("written", out)
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.timeout=-1", str(out)], check=True)
