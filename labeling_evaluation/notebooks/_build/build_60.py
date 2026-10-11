"""Generate notebooks/60_review_scripts_vs_author.ipynb (python3 notebooks/_build/build_60.py [--run])."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
c = []
c.append(md("""# 60 — The author's reviews, and rule-based scripts scored against them

The author's review is the yardstick. Each input is shown as (a) how often the author agreed with what the pipeline proposed, with a
95 % Wilson interval (finite-population corrected, z = 1.96), and (b) for the three inputs that had been proposed by a reading step
(year, TRL, company map), how a **rule-based script with no model** compares with the same review.

How each value was obtained (stated plainly):
- **Domain flag of the evtol.news pages** — fixed text rules run by script (`viz/frames.py`, `directory_frame`); the author's individual rulings sit in `review/domain_overrides.csv`.
- **Year, TRL, company map** — proposed by a reading step over the public page text, then checked by the author. The scripts below are the rule-based alternatives.

Inputs: the CSVs the review pages export, copied to `review/decisions/`. Nothing here changes a figure."""))
c.append(code("""import subprocess, sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR)); sys.path.insert(0, str(PILLAR / 'notebooks' / '_build' / 'yearscript'))
import os; os.chdir(PILLAR)
def run(script, *a):
    r = subprocess.run([sys.executable, script, *a], capture_output=True, text=True, cwd=PILLAR)
    print(r.stdout + (r.stderr if r.returncode else ''))
print(PILLAR)"""))
c.append(md("## 1. Agreement with the author, input by input\n\nDomain rules (kept / excluded sides), development year, TRL; company map is a census."))
c.append(code("run('notebooks/_build/review_confidence.py', '--dir', 'review/decisions')"))
c.append(md("## 2. Domain flag under the current rules\n\nThe rules now include the author's rulings: an electric option counts as electric, **hybrid-electric is not** an electric option, only unmanned pages are UAVs, a \"no passengers\" demonstrator stays in when the page says it is built for people, plus the author's individual rulings. The table crosses the author's answers on the sample of KEPT pages with what the current rules say."))
c.append(code("""import pandas as pd
from viz import config, frames
cfg = config.load(); d = frames.directory_frame(cfg).set_index('slug_key')
print('designs in the domain:', int(d.in_domain.sum()), '| multicopters:', int((d.in_domain & d.class5.eq('WM')).sum()),
      '| patent-linked kept:', int(d.loc[d.patented, 'in_domain'].sum()), 'of', int(d.patented.sum()))
print(d.groupby('class5').in_domain.sum().to_dict())
k = pd.read_csv('review/decisions/DOMAIN_INCLUDED_REVIEW_DECISIONS.csv', keep_default_na=False)
k['rules_now_say_in'] = k.slug_key.map(d.in_domain)
print(pd.crosstab(k.decision, k.rules_now_say_in))
print('patent-linked pages the rules now exclude (they are in the patent dataset):')
print(sorted(d[d.patented & ~d.in_domain].index))"""))
c.append(md("## 3. Development year: rule-based script vs the author\n\n`year_rule.py` keeps Resources entries and event sentences about the aircraft, drops company-history and future statements, and takes the earliest year. It was developed on the pages the author did **not** review and scored once on the author's sample."))
c.append(code("run('notebooks/_build/yearscript/evaluate_year_rule.py')"))
c.append(md("## 4. TRL: rule-based script vs the author\n\n`trl_rule.py`: certification 8; piloted flight 7; flight of a sub-scale model 5; any other flight 6; ground / wind-tunnel / simulation 4; otherwise 2. The rules were written before scoring and not tuned on the answers."))
c.append(code("""import pandas as pd
from trl_rule import rule_trl
from lib import intervals
t = pd.read_csv(cfg.path('trl_per_aircraft'), keep_default_na=False, dtype=str).set_index('aircraft_id')
r = pd.read_csv('review/decisions/TRL_REVIEW_DECISIONS.csv', dtype=str, keep_default_na=False)
r = r[r.action.isin(['confirmed', 'changed'])].copy()
r['author'] = r.trl.astype(int); r['script'] = r.aircraft_id.map(lambda a: rule_trl(t.loc[a, 'evidence_quote'])); r['reading step'] = r.aircraft_id.map(lambda a: int(t.loc[a, 'trl']))
n = len(r); ex = int((r.script == r.author).sum()); w1 = int(((r.script - r.author).abs() <= 1).sum()); rd = int((r['reading step'] == r.author).sum())
print(f'rows answered: {n}')
print(f'reading step agrees with the author: {rd}/{n} = {rd/n:.3f}  95% {intervals.wilson_fpc_interval(rd, n, 105)}')
print(f'script exact:  {ex}/{n} = {ex/n:.3f}  95% {intervals.wilson_fpc_interval(ex, n, 105)}')
print(f'script within one level: {w1}/{n} = {w1/n:.3f}  95% {intervals.wilson_fpc_interval(w1, n, 105)}')
print(pd.crosstab(r.author, r.script, rownames=['author'], colnames=['script']))"""))
c.append(md("## 5. AAM Reality Index company map: rule-based script vs the author (all 43 rows)\n\n`ari_rule.py` matches normalised names. Rows the author did not export are blank in the dataset and counted as confirmed blank (author's statement)."))
c.append(code("run('notebooks/_build/yearscript/ari_rule.py')"))
c.append(md("""## 6. One table: accuracy against the author's review

**How the domain "estimation" works.** The author checked a random sample of each side. If k of n sampled pages were right, the share right in the whole pool is estimated as k/n, with a 95 % Wilson interval corrected for the finite pool. Multiplying the share by the pool size gives an estimated **number of pages**: e.g. 67 of 88 kept pages right in a pool of 1 040 gives about 792 right and about 248 wrong, with an interval around each. The two sides are kept separate because their pools were drawn at different times.

Domain rows are the rules **as they stood when the author reviewed** (an honest test). The rules were fixed afterwards; a fresh sample would be needed to state a figure for the current rules. Year, TRL and company map: \"LLM\" = the reading step that proposed the value; \"script\" = the rule-based alternative."""))
c.append(code("""import numpy as np
rows = []
def add(inp, who, k, n, N, what):
    lo, hi = intervals.wilson_fpc_interval(k, n, N) if N else (np.nan, np.nan)
    rows.append({'input': inp, 'method': who, 'agree': k, 'of': n, 'share %': round(100*k/n, 1),
                 '95% interval %': (f'{100*lo:.1f}-{100*hi:.1f}' if N else 'census (all rows)'), 'what it measures': what})
dec_ex = pd.read_csv('review/decisions/DOMAIN_REVIEW_DECISIONS.csv', keep_default_na=False); dec_ex = dec_ex[(dec_ex.section == 'B') & dec_ex.decision.isin(['exclude', 'in_domain'])]
dec_in = pd.read_csv('review/decisions/DOMAIN_INCLUDED_REVIEW_DECISIONS.csv', keep_default_na=False)
add('Domain flag: deleting pages as out of domain', 'script rules', int((dec_ex.decision == 'exclude').sum()), len(dec_ex), 223, 'share of excluded pages that really are out')
add('Domain flag: keeping pages in the domain', 'script rules', int((dec_in.decision == 'in_domain').sum()), len(dec_in), 1040, 'share of kept pages that really are in')
ye = pd.read_csv('review/decisions/YEAR_REVIEW_SAMPLE.csv', keep_default_na=False, dtype=str)
add('Development year', 'LLM (reading step)', int((ye.action == 'confirmed').sum()), len(ye), 1229, 'proposed year kept by the author')
yr = pd.read_csv('review/decisions/YEAR_RULE_VS_AUTHOR.csv')
add('Development year', 'script, exact year', int(yr.exact.sum()), len(yr), 1229, 'script year = the author year')
add('Development year', 'script, within 1 year', int(yr.within1.sum()), len(yr), 1229, 'script year within +-1 of the author')
add('TRL', 'LLM (reading step)', 50, 50, 105, 'proposed TRL kept by the author (evidence-based rows)')
add('TRL', 'script, exact level', ex, n, 105, 'script TRL = the author TRL')
add('TRL', 'script, within 1 level', w1, n, 105, 'script TRL within +-1 of the author')
import ari_rule
from viz import thesis
v_ = thesis.context(cfg).v
nm = sorted({str(x) for x in v_.company_canonical if str(x) not in ('Individual Inventor', 'Unknown / Independent')})
m_ = pd.read_csv(cfg.path('ari_firm_map'), keep_default_na=False)
rv_ = pd.read_csv('review/decisions/ARI_FIRM_REVIEW_DECISIONS.csv', keep_default_na=False).set_index('oem')
gold = [rv_.loc[o, 'company_canonical'] if o in rv_.index else c0 for o, c0 in zip(m_.oem, m_.company_canonical)]
add('AAM index company map (all 43 rows)', 'LLM (reading step)', sum(a == b for a, b in zip(m_.company_canonical, gold)), 43, None, 'proposed name = the author name')
add('AAM index company map (all 43 rows)', 'script, name match', sum(ari_rule.match(o, nm) == g for o, g in zip(m_.oem, gold)), 43, None, 'script name = the author name')
T = pd.DataFrame(rows); T.to_csv('review/decisions/ACCURACY_TABLE.csv', index=False)
from IPython.display import display; display(T)
print()
for side, k_, n_, N_ in [('deleted as out of domain', int((dec_ex.decision == 'exclude').sum()), len(dec_ex), 223), ('kept in the domain', int((dec_in.decision == 'in_domain').sum()), len(dec_in), 1040)]:
    lo, hi = intervals.wilson_fpc_interval(k_, n_, N_)
    print(f'{side}: pool {N_} pages -> estimated RIGHT {round(N_*k_/n_)} ({round(N_*lo)}-{round(N_*hi)}), estimated WRONG {round(N_*(1-k_/n_))} ({round(N_*(1-hi))}-{round(N_*(1-lo))})')"""))
c.append(md("## 7. Reading the numbers\n\n- A script is acceptable as a stand-in when its agreement with the author is at or above the author's threshold; otherwise report it as a transparent baseline.\n- The author's threshold for the reading-step inputs was a lower bound of 90 %; the question of whether a script may be judged on \"within one year / one level\" is the author's to decide."))
nb = nbf.v4.new_notebook(); nb.cells = c
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = HERE / "60_review_scripts_vs_author.ipynb"
nbf.write(nb, out); print("written", out)
if "--run" in sys.argv:
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", str(out)], check=True)
