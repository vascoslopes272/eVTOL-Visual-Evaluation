"""Generate notebooks/43_q4_filers.ipynb (and execute it with --run).

    python3 notebooks/_build/build_43.py          # write the notebook
    python3 notebooks/_build/build_43.py --run    # write, then jupyter nbconvert --execute --inplace

The markdown of each sub-question (its question and Method) and every caption are copied from the 45-page
document at build time, so the author's wording is exact. Everything else is written here, cell by cell.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import nbformat
import yaml
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

PILLAR = Path(__file__).resolve().parents[2]
OUT = PILLAR / "notebooks" / "43_q4_filers.ipynb"
REF = Path(yaml.safe_load((PILLAR / "labelling_analysis.yaml").read_text())["roots"]["reference"])
BRIEF = (REF / "LABELLING_ANALYSIS_BRIEF.md").read_text(encoding="utf-8").splitlines()


# ------------------------------------------------------------------------------------------ the document's text
def _section(start: str, stop: str) -> list:
    i = next(k for k, l in enumerate(BRIEF) if l.startswith(start))
    j = next(k for k, l in enumerate(BRIEF) if k > i and l.startswith(stop))
    return [l for l in BRIEF[i:j] if not l.startswith("<div") and not l.startswith("</div>")]


def question_and_method(sub: str, heading: str, next_heading: str) -> str:
    """The sub-question heading and its Method block, verbatim."""
    lines = _section(f"### {sub} —", "#### Results and discussion")
    text = "\n".join(lines).strip()
    return re.sub(r"^### ", "## ", text, count=1)


def caption(kind: str, n: int) -> str:
    """The caption of Figure n / Table n as the document prints it (markers stripped)."""
    if kind == "Figure":
        line = next(l for l in BRIEF if l.startswith(f"*Figure {n} —"))
        text = line.strip().strip("*")
        text = re.sub(r"^Figure \d+ — ", "", text)
        return text.replace("**", "")
    line = next(l for l in BRIEF if l.startswith(f"**Table {n} —"))
    return re.sub(r"^Table \d+ — ", "", line.strip().strip("*")).strip()


def q(text: str) -> str:
    return repr(text)


cells = []


def md(text: str):
    cells.append(new_markdown_cell(text.strip("\n")))


def code(text: str, **kw):
    """A code cell; ``@KEY@`` in the text is replaced by kw[KEY] (the captions, copied from the document)."""
    for k, val in kw.items():
        text = text.replace(f"@{k}@", val)
    cells.append(new_code_cell(text.strip("\n")))


# ------------------------------------------------------------------------------------------ section 0
INTRO = "\n".join(_section("## 4 —", "### 4.1 —")).strip().replace("## 4 —", "### Chapter 4 —", 1)

md("""# 43 — Question 4: the filers

Which kinds of firm, institute and inventor patent eVTOL aircraft, and which designs and filing strategies do firms of different maturity follow?

Sub-questions 4.1 and 4.2 of the Labelling Analysis (2026-09-30). Every path comes from `labelling_analysis.yaml`; equations come from `lib/`, figures and tables from `viz/`.

This notebook reproduces every figure, table and number of chapter 4 of the 45-page document, and compares them with it (`viz.checks`). Chapter 4 reads the twelve classes of the wizard (`topType`: the seven classes of 20 aircraft or more of Figure 17, the five of Figures 19 and 20), never the five-class fold, so the class fold of 2026-10-01 (Stopped/Slowed Rotor Wing into Lift + Cruise) moves no number here. The differences from the document's tables are only the display names of 2026-09-28 (Tilt Rotor is printed Tilt Propulsor), which `viz.checks` maps. The method is reproduced as the document has it: nothing is changed (METHOD_NOTES.md item 4: the firms of Figure 17 are ranked on `firm` and dropped on `company_canonical`; here the two columns are equal, so the difference does not arise).

Figure 3 of 4.1's funding test is printed in chapter 1 (notebook 40); this notebook reproduces its lead from first patent to first flight for the nine funded firms. Outputs are written to `<output>/q4_filers/` (figures: pdf, png, csv, json; tables: csv, json). Regenerate this notebook with `python3 notebooks/_build/build_43.py`.""")
md(INTRO)
md("""## 0. Setup: paths and the analysis unit

The table lists every input this notebook can read, whether it exists and when it last changed. The load raises if a required input is missing.""")
code(r"""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
pd.set_option('display.max_colwidth', 120)
from viz import config, data
cfg = config.load()
config.show(cfg)[['group', 'key', 'exists', 'modified', 'size', 'path']]""")
md("""The analysis unit is the representative primary aircraft: wizard-approved, passes the domain gate (no UAV/not-electric/STOL-only tag), one row per aircraft. Counts below must match the document.""")
code(r"""ds = data.load_dataset(cfg)
pd.Series(ds.counts, name='count').to_frame()""")
md("""### Tools used below

`frames.base` is the per-aircraft analysis frame (627 rows); `frames.filer_from_assignee` and `frames.firm_from_assignee` are the text rules that give a filer its type and a firm its name; `lib.concentration` holds the equations of 4.1 (coverage bands, effective number of filers, firm leverage), `lib.association` the tests (chi-square, Fisher, Spearman); `viz.checks` compares with the document. `verify` runs one table check and keeps its summary for the final overview; `numbers_check` does the same for the quoted numbers. A cell written in the thesis names (Tilt Propulsor) is compared with the document's wording through `checks.rename_map`.""")
code(r"""import inspect
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from IPython.display import display
from viz import frames, style, plots, save, checks
from lib import concentration, association

style.apply(cfg)
v = frames.base(ds, cfg)                                   # one row per unique aircraft (627)
WIN_NAMES = list(cfg.analysis['windows'])
COMPLETE = [w for w in WIN_NAMES if 'partial' not in w]    # the four windows with a complete priority year
W, _ = style.size(cfg, 'full')
pct = lambda x: f"{x:.0%}".replace('%', ' %')              # 0.53 -> '53 %'
pct1 = lambda x: f"{100 * x:.1f} %"                        # 0.0143 -> '1.4 %'
thin = lambda n: f"{int(n):,}".replace(',', ' ')           # 1 229
pval = lambda p: '< 0.001' if p < 0.001 else f"{p:.3f}" if p < 0.05 else f"{p:.2f}"   # the form of the document's p
WSHORT = {'<= 2011': '≤2011', '2012-15': '12–15', '2016-19': '16–19', '2020-23': '20–23', '2024-26 (partial)': '24–26*'}
CLASS_NAMES = {c: style.cls(c).name for c in style.CLASS_ORDER}
CHECKS, NUMBERS = [], []                                   # summaries kept for the overview at the end

def verify(frame, ref, name=None, doc_wording=True, **kw):
    if doc_wording and 'rename' not in kw:
        kw['rename'] = checks.rename_map(frame)
    r = checks.table(frame, ref, cfg, name=name, **kw)
    CHECKS.append(r)
    display(r.T.rename(columns={0: name or ref}))
    d = checks.detail(r)
    if len(d):
        display(d)

def numbers_check(values, expected=None):
    r = checks.numbers(values, '4', expected)
    NUMBERS.append(r)
    display(r)

def thesis_names(frame):
    '''A table as the thesis prints it: Tilt Rotor is Tilt Propulsor (the display rename of 2026-09-28).'''
    return frame.rename(columns=lambda c: str(c).replace('Tilt Rotor', 'Tilt Propulsor')).replace({'Tilt Rotor': 'Tilt Propulsor'})""")

# ------------------------------------------------------------------------------------------ 4.1
md(question_and_method("4.1", "", ""))
md("""### Who a filer is

`frames.filer_from_assignee` reads a filer's type from the first assignee as PatSeer prints it (the fixed text rules of the Method; no model); `frames.firm_from_assignee` and the grouper's table give the firm's name, with ten spellings folded by hand (`frames.FIRM_ALIASES`). `frames.filer_mix` counts the types in primary patents and in unique aircraft; `frames.filer_mix_representative` counts the 879 representative patents. Both are checked against the document. The fourth type, *no assignee named*, is empty.""")
code(r"""assert int(v['filer'].eq(frames.NO_ASSIGNEE).sum()) == 0          # 'no assignee named' is empty in this corpus
fm = frames.filer_mix(v)
fmr = frames.filer_mix_representative(ds)
verify(fm, 'la_filer_mix', key=['filer'])
verify(fmr, 'la_filer_mix_rep', key=['filer'])
save.table(fm, cfg, 'q4', 'tab_filer_mix', caption='The filer types in primary patents and in unique aircraft, with the distinct filers of each.',
           source='PatSeer (assignee) · human labelling · fixed text rules of the Method')
save.table(fmr, cfg, 'q4', 'tab_filer_mix_representative', caption='The filer types counted over the 879 representative patents.',
           source='PatSeer (assignee) · human labelling · fixed text rules of the Method')
display(fm); fmr""")
md("""### The firm-size ranking and the filers per window

`frames.coverage_table` (`lib.concentration.coverage_segments`) cuts the named organisations, ranked by their unique aircraft, into the four disjoint bands of the Method (10 or more aircraft each, 5-9, 2-4, 1). `frames.filers_by_window` counts, per priority window, the named organisations that file, those filing for the first time (their earliest eVTOL aircraft in the corpus falls in the window) and those filing again, and the share of individual inventors and of universities. Both are checked against the document.""")
code(r"""cov = frames.coverage_table(v)
fw = frames.filers_by_window(v, WIN_NAMES)
verify(cov, 'la_coverage_segments', key=['aircraft per firm'])
verify(fw, 'la_filers_by_window', key=['window'])
save.table(cov, cfg, 'q4', 'tab_coverage_segments', caption='The named organisations by the aircraft each holds: four bands, with the cumulative firms and aircraft.',
           source='PatSeer (assignee) · human labelling · unit: unique aircraft')
save.table(fw, cfg, 'q4', 'tab_filers_by_window', caption='The named organisations filing in each priority window: first-time and returning, with the share of individual inventors and of universities and institutes.',
           source='PatSeer (assignee, priority date) · human labelling')
display(cov); fw""")
md("""### Figure 16 — who files the eVTOL patents

(i) The named organisations ranked by unique aircraft with the cumulative share of the 627 aircraft, cut into the four bands; the firms rated by the AAM Reality Index are marked. (ii) The share of each filer type: the 879 representative patents and the 627 aircraft over all years, then the aircraft of each priority window. (iii) The named organisations filing in each window: first-time (number inside the dark bar) and filing again (above the bar). The window 2024-26 is still filling (faded, star).""")
code(r"""sizes = frames.firm_sizes(v)
n_air = len(v)
cum = (sizes.cumsum() / n_air).to_numpy()
rank = np.arange(1, len(sizes) + 1)
rated_firms = set(frames.ari_firms(v, cfg)['company'])
rated_rank = [i + 1 for i, f in enumerate(sizes.index) if f in rated_firms]
edges = [0] + cov['cumulative firms'].astype(int).tolist()
BAND = 'ABCD'
FT = ['Named company', 'University / institute', 'Individual inventor']
FT_NAME = {'Named company': 'named companies', 'University / institute': 'universities / institutes', 'Individual inventor': 'individual inventors'}
fig = plt.figure(figsize=(W, 6.9), constrained_layout=True)
top, bot = fig.subfigures(2, 1, height_ratios=[1.0, 1.0])
ax = top.subplots()
for k in range(1, len(edges) - 1, 2):                       # every second band shaded, to tell the bands apart
    ax.axvspan(edges[k] + 0.5, edges[k + 1] + 0.5, color=plots.FEW_FILL, linewidth=0, zorder=0)
ax.step(rank, cum, where='post', color=style.INK, linewidth=1.5, zorder=3)
ax.plot(rated_rank, cum[np.array(rated_rank) - 1], linestyle='none', marker='D', markersize=4.6, markerfacecolor='white', markeredgecolor=style.INK,
        markeredgewidth=1.0, zorder=5)
for k, (x0, x1) in enumerate(zip(edges[:-1], edges[1:])):
    ax.text((x0 + x1) / 2 + 0.5, 0.025, BAND[k], ha='center', va='bottom', fontsize=8, fontweight='bold')
    y1 = float(cum[x1 - 1])
    dx, dy, ha, va = [(4, -8, 'left', 'top'), (4, -8, 'left', 'top'), (-4, 6, 'right', 'bottom'), (-3, -8, 'right', 'top')][k]
    ax.annotate(pct(y1), (x1, y1), textcoords='offset points', xytext=(dx, dy), ha=ha, va=va, fontsize=8, fontweight='bold')
share_named = float(sizes.sum() / n_air)
ax.axhline(share_named, color=style.MUTED, linewidth=0.8, linestyle='--', zorder=2)
ax.text(len(sizes), share_named + 0.015, f"all {len(sizes)} named organisations: {int(sizes.sum())} aircraft, {pct(share_named)}", ha='right', va='bottom', fontsize=7.5)
ax.axhline(1, color=style.GRID, linewidth=0.8, zorder=1)
ax.text(len(sizes), 1.012, f"all {n_air} aircraft (individual inventors hold the rest)", ha='right', va='bottom', fontsize=7.5, color=style.MUTED)
band_text = ['10 or more aircraft each', '5-9 aircraft each', '2-4 aircraft each', '1 aircraft each']
for k, r in cov.reset_index(drop=True).iterrows():
    ax.text(0.985, 0.36 - 0.085 * k, f"{BAND[k]}  {band_text[k]}: {int(r['firms'])} firms · {int(r['aircraft'])} aircraft", transform=ax.transAxes, ha='right', va='top', fontsize=7.5,
            bbox=dict(fc='white', ec='none', pad=1.2))
ax.legend(handles=[Line2D([], [], linestyle='none', marker='D', markersize=4.6, markerfacecolor='white', markeredgecolor=style.INK, label=f"rated by the AAM Reality Index ({len(rated_rank)} firms)")],
          loc='upper left', fontsize=7.5, handletextpad=0.4, borderaxespad=0.3)
ax.set_xlim(0, len(sizes) + 1); ax.set_ylim(0, 1.1)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax.grid(axis='y', color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
ax.set_xlabel('named organisations ranked by unique aircraft, largest first')
ax.set_ylabel(f"cumulative share of\nthe {n_air} aircraft"); style.mark(ax, '(i)')
# (ii) the filer types
a2, a3 = bot.subplots(1, 2, gridspec_kw={'width_ratios': [1.55, 1.0]})
win_counts = [v[v['window'] == w]['filer'].value_counts().reindex(FT).fillna(0) for w in WIN_NAMES]
rep_counts = fmr.set_index('filer')['representative patents']
parts = pd.DataFrame([[rep_counts['Named companies'], rep_counts['Universities and institutes'], rep_counts['Individual inventors']],
                      list(v['filer'].value_counts().reindex(FT).fillna(0))] + [list(c) for c in win_counts], columns=FT)
pos = [0, 1] + [2.4 + k for k in range(len(WIN_NAMES))]
parts_n = parts.sum(axis=1).astype(int).to_numpy()
plots.stack_bars(a2, parts, plots.FILER_STYLE, positions=pos, width=0.72, partial=[len(parts) - 1], min_label=0.06)
a2.axvline(1.7, color=style.MUTED, linewidth=0.8, linestyle=':')
a2.set_xticks(pos, [f"{t}\nn {n}" for t, n in zip(['all, repr.\npatents', 'all,\naircraft'] + [WSHORT[w] for w in WIN_NAMES], parts_n)], fontsize=7)
a2.set_ylim(0, 1); a2.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); a2.set_ylabel('share'); style.mark(a2, '(ii)')
a2.spines[['bottom']].set_visible(False); a2.tick_params(axis='x', length=0)
# (iii) the organisations per window
new, cont = fw['new firms'].to_numpy(), fw['continuing firms'].to_numpy()
x3 = np.arange(len(fw))
b1 = a3.bar(x3, new, 0.66, color=plots.ENTRY_COLORS[0], edgecolor='white', linewidth=0.6, zorder=3)
b2 = a3.bar(x3, cont, 0.66, bottom=new, color=plots.ENTRY_COLORS[1], edgecolor='white', linewidth=0.6, zorder=3)
for i, (p1, p2) in enumerate(zip(b1, b2)):
    if i == len(fw) - 1:
        for b in (p1, p2):
            b.set_alpha(0.5); b.set_hatch(style.PARTIAL_HATCH)
    a3.text(i, new[i] / 2, f"{new[i]}", ha='center', va='center', fontsize=7.5, color='white', fontweight='bold', zorder=5)
    a3.text(i, new[i] + cont[i] + 2, f"+{cont[i]} again", ha='center', va='bottom', fontsize=7.5)
a3.set_xticks(x3, [WSHORT[w] for w in WIN_NAMES], fontsize=7)
a3.set_xlim(-0.75, len(fw) - 0.3); a3.set_ylim(0, float((new + cont).max()) * 1.4); a3.set_ylabel('named organisations filing')
a3.grid(axis='y', color=style.GRID, linewidth=0.5); a3.set_axisbelow(True); style.mark(a3, '(iii)')
a3.legend(handles=[Patch(facecolor=plots.ENTRY_COLORS[0], label='first-time (number in the bar)'), Patch(facecolor=plots.ENTRY_COLORS[1], label='filing again (above the bar)')],
          loc='upper left', fontsize=7.5, handlelength=1.2)
bot.legend(handles=[Patch(facecolor=plots.FILER_STYLE[k][0], hatch=plots.FILER_STYLE[k][1], edgecolor='white', label=FT_NAME[k]) for k in FT], loc='outside lower center', ncol=3, fontsize=7.5, handlelength=1.4)
plt.show()
fig16_data = pd.concat([cov.assign(panel='(i) bands'), parts.assign(bar=['all, repr. patents', 'all, aircraft'] + WIN_NAMES, panel='(ii)'), fw.assign(panel='(iii)')], ignore_index=True)
save.figure(fig, cfg, 'q4', 'fig_16_who_files', data=fig16_data,
            caption=@CAP@,
            source='PatSeer (assignee, priority date) · human labelling · AAM Reality Index (the firms it has rated)',
            unit=f"(i) and (ii): unique aircraft ({n_air}), and in (ii) the {int(parts_n[0])} representative patents, each once; (iii) the named organisation; the window 2024-26 is still filling (faded, star)",
            read="(i) The curve climbs by one firm at a time, largest first; the four bands A to D cut it where firms hold 10 or more, 5-9, 2-4 and 1 aircraft each; the cumulative share is printed at the end of each band; the dashed line is the share all named organisations hold; hollow diamonds are the firms the index rates. (ii) Each bar is 100 %; a segment of 6 % or more prints its share. The first bar counts patents (the unit changes the answer little), the others aircraft. (iii) Dark: organisations whose earliest aircraft in the corpus falls in the window; light: organisations that filed in an earlier window.",
            panels={'(i)': 'cumulative share of aircraft by named organisation', '(ii)': 'filer type, all years and per window', '(iii)': 'first-time and returning organisations per window'})
plt.close(fig)""", CAP=q(caption("Figure", 16)))
md("""### Can one filer decide a class share?

`frames.class_concentration_brief` reads, for each class of 20 aircraft or more, its filers (a firm; an individual inventor's patent is its own filer), the effective number of filers (`lib.concentration.inverse_hhi` = 1 / Σ sᵢ², through `class_filer_concentration`), the largest filer over all years and the largest share one filer holds inside a single complete window of 10 aircraft or more of the class. `frames.firm_leverage_table` (`lib.concentration.firm_leverage`) removes, one firm at a time, every firm of 3 aircraft or more and keeps the class share that moves most, over all years and inside a window of 30 aircraft or more; `frames.firm_leverage_classes` keeps every class's move for the eight firms that move a share most (`lib.concentration.share_shift_when_dropped`), the reading of the "what largest change means" paragraph. All three are checked against the document.""")
code(r"""cb = frames.class_concentration_brief(v, COMPLETE)
lev = frames.firm_leverage_table(v, WIN_NAMES)
levc = frames.firm_leverage_classes(v, WIN_NAMES, lev=lev)
verify(cb, 'la_class_concentration_brief', key=['code'])
verify(lev, 'la_firm_leverage', key=['firm'])
verify(levc, 'la_firm_leverage_classes', key=['firm', 'class'], doc_wording=False)
save.table(cb, cfg, 'q4', 'tab_class_concentration', caption='The classes of 20 aircraft or more: filers, effective number of filers, the largest filer over all years and inside one priority window.',
           source='PatSeer (assignee, priority date) · human labelling · unit: unique aircraft')
save.table(lev, cfg, 'q4', 'tab_firm_leverage', caption='The largest change of a class share when one firm (3 aircraft or more) is removed, over all years and inside one priority window.',
           source='PatSeer (assignee, priority date) · human labelling · unit: unique aircraft')
display(cb); lev.head(10)""")
md("""### Figure 17 — whether one filer holds enough of a class to decide its share

(i) Per class of 20 aircraft or more, the share held by its largest filer over all years (bar) and the highest share one filer reaches inside a single priority window (diamond; windows with 10 or more aircraft of the class, 2024-26 left out); on the tick, the class's filers and its effective number of filers. (ii) The eight firms that move a class share most when removed: over all years (bar, coloured by the class that moves) and inside one window of 30 aircraft or more (diamond).""")
code(r"""WORD = lambda c: 'CVT' if c == 'CVT' else style.cls(c).name
who_short = lambda s: str(s).replace("an individual inventor's patent", 'one inventor')
winlab = lambda w: 'before 2012' if w == '<= 2011' else f"in {w}"
fig, (a1, a2) = plt.subplots(2, 1, figsize=(W, 6.6), constrained_layout=True, gridspec_kw={'height_ratios': [len(cb), 8 + 1]})
dia = dict(marker='D', s=24, color=style.INK, edgecolor='white', linewidth=0.6, zorder=5)
for i, r in cb.reset_index(drop=True).iterrows():
    s = style.cls(r['code'])
    a1.barh(i - 0.18, r['its share'], 0.3, color=s.color, hatch=s.hatch, edgecolor='white', linewidth=0.6, zorder=3)
    a1.text(r['its share'] + 0.008, i - 0.18, f"{who_short(r['largest filer'])} {pct(r['its share'])}", va='center', fontsize=7.5)
    a1.scatter(r['largest share inside one window'], i + 0.2, **dia)
    a1.text(r['largest share inside one window'] + 0.018, i + 0.2, f"{who_short(r['held by'])} {pct(r['largest share inside one window'])} {winlab(r['in window'])}", va='center', fontsize=7.5, color=style.MUTED)
a1.set_yticks(range(len(cb)), [f"{WORD(c)} · {int(n)} aircraft\n{int(f)} filers, as if {e:.0f} equal" for c, n, f, e in zip(cb['code'], cb['aircraft'], cb['filers'], cb['effective filers'])], fontsize=7.5)
a1.invert_yaxis(); a1.set_xlim(0, 0.62); a1.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
a1.set_xlabel("share of the class's aircraft held by one filer"); a1.grid(axis='x', color=style.GRID, linewidth=0.5); a1.set_axisbelow(True); style.mark(a1, '(i)')
l8 = lev.head(8).reset_index(drop=True)
for i, r in l8.iterrows():
    s = style.cls(r['class most moved'])
    a2.barh(i - 0.18, r['shift magnitude (pp)'], 0.3, color=s.color, hatch=s.hatch, edgecolor='white', linewidth=0.6, zorder=3)
    sign = '+' if r['shift if the firm is dropped (pp)'] > 0 else '−'
    a2.text(r['shift magnitude (pp)'] + 0.08, i - 0.18, f"{WORD(r['class most moved'])} {sign}{r['shift magnitude (pp)']:.1f} pts", va='center', fontsize=7.5)
    a2.scatter(r['largest shift inside one window (pp)'], i + 0.2, **dia)
    a2.text(r['largest shift inside one window (pp)'] + 0.16, i + 0.2, f"{r['largest shift inside one window (pp)']:.1f} pts {winlab(r['that window'])}", va='center', fontsize=7.5, color=style.MUTED)
a2.set_yticks(range(len(l8)), [f"{f} · {int(n)} aircraft" for f, n in zip(l8['firm'], l8['unique aircraft'])], fontsize=7.5)
a2.invert_yaxis(); a2.set_xlim(0, float(max(l8['largest shift inside one window (pp)'].max(), l8['shift magnitude (pp)'].max())) * 1.9)
a2.set_xlabel('largest change of a class share when the firm is removed (points)'); a2.grid(axis='x', color=style.GRID, linewidth=0.5); a2.set_axisbelow(True); style.mark(a2, '(ii)')
fig.legend(handles=[Patch(facecolor='#bdbdbd', label='bar: all years (in the colour and hatch of the class)'), Line2D([], [], linestyle='none', **{k: dia[k] for k in ('marker',)}, markersize=5, color=style.INK, label='diamond: within one priority window, the highest')],
           loc='outside lower center', ncol=2, fontsize=7.5, handlelength=1.4)
plt.show()
fig17_data = pd.concat([cb.assign(panel='(i)'), l8.assign(panel='(ii)')], ignore_index=True)
save.figure(fig, cfg, 'q4', 'fig_17_one_filer', data=fig17_data,
            caption=@CAP@,
            source='PatSeer (assignee, priority date) · human labelling',
            unit=f"unique aircraft; (i) the {len(cb)} classes of {frames.CH4_CLASS_MIN} aircraft or more, windows of {frames.CH4_CELL_MIN} aircraft or more, 2024-26 left out; (ii) firms of {frames.LEVERAGE_MIN_FIRM} aircraft or more, the eight that move a class share most, windows of {frames.LEVERAGE_MIN_WINDOW} aircraft or more",
            read="(i) Bar: the share of the class's aircraft held by its largest filer over all years, named at the bar's end; diamond: the highest share one filer holds inside a single complete priority window, with the filer and the window. On the tick: the class's aircraft, its filers and its effective number of filers, 1 / Σ sᵢ² (how many equally sized filers would give the same concentration). (ii) Removing a firm takes its aircraft out of every class it files in and recomputes every share; the class that moves most is the one drawn, in its colour, with the move in percentage points (+ = the share rises when the firm is removed). Diamond: the largest move inside one window.",
            panels={'(i)': 'largest filer of each class, all years and within one window', '(ii)': 'the weight of a single firm: removing one firm at a time'})
plt.close(fig)""", CAP=q(caption("Figure", 17)))
md("""### What the AAM Reality Index adds

`frames.ari_funding_frame` lists the index firms that file in the corpus (18) with the disclosed funding of the May 2026 release (US$ million; *corporate backed* and earlier-release firms have no amount), their unique aircraft, first patent, first flight and the lead from first patent to first flight (flights up to the release year, 2026). `frames.ari_funding_tests` gives the Spearman ρ and p (`lib.association.spearman_rho_p`) of funding against aircraft, first patent and lead, on the firms with an amount (the lead on those whose first flight has happened). Both are checked against the document.""")
code(r"""fund = frames.ari_funding_frame(v, cfg)
ftests = frames.ari_funding_tests(fund)
verify(fund, 'la_ari_funding', key=['company'])
verify(ftests, 'la_ari_funding_tests', key=['column'])
save.table(fund, cfg, 'q4', 'tab_ari_funding', caption='The AAM Reality Index firms that file here: disclosed funding, aircraft, first patent and lead to first flight.',
           source='AAM Reality Index (May 2026 release) · PatSeer · human labelling')
save.table(ftests, cfg, 'q4', 'tab_ari_funding_tests', caption='Spearman rank correlation of disclosed funding against three patent-side quantities, on the funded firms.',
           source='AAM Reality Index (May 2026 release) · PatSeer · human labelling')
display(fund); ftests""")
md("""### Figure 18 — funding against the aircraft filed and the patent-to-flight lead

The nine firms with a disclosed amount: funding (US$ million, log scale) against (i) their unique aircraft in the corpus and (ii) the lead from first patent to first flight, on the eight firms whose first flight has happened. ρ is the Spearman score of the statistics box of chapter 1.""")
code(r"""ARI_SHORT = {'Ascendance Flight Technologies': 'Ascendance', 'Wofei / Geely Aviation': 'Wofei / Geely', 'Embraer / Eve': 'Eve', 'Beta Technologies': 'Beta',
             'Vertical Aerospace': 'Vertical', 'Wollant Aviation': 'Wollant', 'Archer Aviation': 'Archer', 'Joby Aviation': 'Joby'}
d18 = fund[fund['funding $M'].notna()]
fig, axs = plt.subplots(1, 2, figsize=(W * 0.82, 3.1), constrained_layout=True)
for ax, (col, ylab, mk) in zip(axs, (('unique aircraft', 'unique aircraft in the corpus', '(i)'), ('years first patent to first flight', 'years, first patent to first flight', '(ii)'))):
    s = d18[['company', 'funding $M', col]].dropna()
    ax.scatter(s['funding $M'], s[col], s=26, color=style.INK, edgecolor='white', linewidth=0.6, zorder=4)
    ax.set_xscale('log'); ax.set_xlim(35, 14000)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x_, _p: f"{x_:,.0f}".replace(',', ' ')))
    ax.set_xlabel('disclosed funding, US$ M (log)'); ax.set_ylabel(ylab)
    ax.grid(color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
    if col.startswith('years'):
        ax.axhline(0, color=style.MUTED, linewidth=0.8, linestyle='--', zorder=2)
        ax.set_ylim(-1.9, 8.2); ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    else:
        ax.set_ylim(0.2, 9.3); ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    t = ftests[ftests['column'] == col].iloc[0]
    ax.set_title(f"ρ {t['rho']:+.2f} · p {t['p']:.3f} · n {int(t['firms'])}".replace('-', '−'), fontsize=7.5, loc='left')
    style.mark(ax, mk, lines_up=1.1)
fig.canvas.draw()
for ax, col in zip(axs, ('unique aircraft', 'years first patent to first flight')):
    s = d18[['company', 'funding $M', col]].dropna()
    failed = plots.place_labels(ax, s['funding $M'].to_numpy(), s[col].to_numpy(), [ARI_SHORT.get(c, c) for c in s['company']], [3.4] * len(s), fontsize=7)
    assert not failed, failed
plt.show()
save.figure(fig, cfg, 'q4', 'fig_18_ari_funding', data=d18,
            caption=@CAP@,
            source='AAM Reality Index (May 2026 release: disclosed funding, first flight) · PatSeer (priority date) · human labelling',
            unit='the firm: the nine AAM Reality Index firms with a disclosed funding amount; (ii) the eight whose first flight has happened (up to the release year, 2026); a lead below zero means the firm\'s earliest filing is not in this corpus',
            read="One dot per firm. Horizontal: disclosed funding in US$ million on a log scale. (i) Vertical: the firm's unique aircraft in the corpus. (ii) Vertical: the years from the firm's first patent to its first flight (below the dashed line: the first flight is dated before the first patent in this corpus). Above each panel: Spearman ρ (+1 when more funding always goes with a larger value, 0 when unrelated, −1 when it always goes with a smaller one), its p and the number of firms. On so few firms only a strong relation can be detected.",
            panels={'(i)': 'funding against unique aircraft', '(ii)': 'funding against the lead from first patent to first flight'})
plt.close(fig)""", CAP=q(caption("Figure", 18)))
md("""### 4.1 numbers

The counts and shares of the Method and of the Results, each written the way the document prints it. The two numbers of chapter 2 that 4.1's Answer quotes (the median filers per aircraft in the core and in the rim of Figure 8, and the CVT archetype with 5-6 propulsor units) come from `frames.zones`, `frames.zone_core` and `frames.archetype_filer_split`; the external comparison (the two best-funded firms' share of the disclosed funding against their share of the aircraft) from `frames.ari_f_funding`.""")
code(r"""fmi = fm.set_index('filer')
zones = frames.zones(v, WIN_NAMES, cfg.analysis['zone_min_aircraft'])
zz = zones[pd.to_numeric(zones['filers 2016-23']) > 0]
fpa, sh = zz['filers per aircraft'], zz['share 2016-23']
core_fpa = fpa[frames.zone_core(zones).reindex(zz.index).fillna(False).astype(bool)]
rim_fpa = fpa[sh <= sh.median()]
fs = frames.archetype_filer_split(v, cfg.analysis['filer_panel_min_aircraft']).set_index('archetype').loc['CVT · 5-6']
ext = frames.ari_f_funding(ds, v, cfg)
firms_ext = ext[ext['kind'] == 'firm']
top2 = firms_ext.nlargest(2, 'funding $M')
fwi = fw.set_index('window')
disc = fund['funding status'].eq('disclosed')
tt = ftests.set_index('column')
N1 = {'unique_s': thin(len(v)), 'c4_rep_n': thin(fmr.set_index('filer').loc['all filers', 'representative patents']),
      'c4_class_min': str(frames.CH4_CLASS_MIN), 'c4_cell_min': str(frames.CH4_CELL_MIN),
      'c4_co_share': pct(fmi.loc['Named companies', 'unique aircraft'] / len(v)), 'c4_uni_share': pct(fmi.loc['Universities and institutes', 'unique aircraft'] / len(v)),
      'c4_ind_share': pct(fmi.loc['Individual inventors', 'unique aircraft'] / len(v)),
      'c4_top4_n': str(int(cov.iloc[0]['firms'])), 'c4_top4_share': pct(cov.iloc[0]['aircraft'] / len(v)),
      'c4_single_n': str(int(cov.iloc[-1]['firms'])), 'c4_org_n': str(int(cov.iloc[-1]['cumulative firms'])),
      'c4_org_share': pct(cov.iloc[-1]['cumulative aircraft'] / len(v)),
      'c4_ind_w1': pct(fwi.loc['<= 2011', 'share individual inventors']), 'c4_ind_w4': pct(fwi.loc['2020-23', 'share individual inventors']),
      'c4_new_1619': str(int(fwi.loc['2016-19', 'new firms'])), 'c4_cont_1619': str(int(fwi.loc['2016-19', 'continuing firms'])),
      'c4_new_2023': str(int(fwi.loc['2020-23', 'new firms'])), 'c4_cont_2023': str(int(fwi.loc['2020-23', 'continuing firms'])),
      'c4_conc_n': str(len(cb)), 'c4_max_top_share': pct(cb['its share'].max()), 'c4_min_eff': f"{cb['effective filers'].min():.0f}",
      'c4_lev1_pp': f"{lev.iloc[0]['shift magnitude (pp)']:.1f}",
      'c4_ari_n': str(len(fund)), 'c4_ari_air': str(int(fund['unique aircraft'].sum())), 'c4_ari_share': pct(fund['unique aircraft'].sum() / len(v)),
      'c4_fund_n': str(int(disc.sum())), 'c4_corp_n': str(int(fund['funding status'].str.startswith('corporate').sum())),
      'c4_hist_n': str(int(fund['funding status'].str.startswith('not in').sum())),
      'c4_lead_n': str(int(tt.loc['years first patent to first flight', 'firms'])),
      'c4_rho_fp': f"{tt.loc['first patent', 'rho']:+.2f}", 'c4_p_fp': pval(tt.loc['first patent', 'p']),
      'c4_core_fpa': f"{core_fpa.median():.2f}", 'c4_rim_fpa': f"{rim_fpa.median():.2f}",
      'sm_cvt56_air': str(int(fs['aircraft'])), 'sm_cvt56_top': fs['largest filer'], 'sm_cvt56_top_n': str(int(fs['its aircraft'])),
      'sm_ext_top1': top2.iloc[0]['company'], 'sm_ext_top2': top2.iloc[1]['company'],
      'sm_ext_top2_fundshare': pct(top2['funding $M'].sum() / firms_ext['funding $M'].sum()),
      'sm_ext_top2_airshare': pct1(top2['unique aircraft'].sum() / v['aircraft_id'].nunique())}
numbers_check(N1)""")
code(r"""# also quoted in the takeaways of 4.1 (not in the document's number list): each against the figure the document prints
cbi = cb.set_index('code')
levi = lev.set_index('firm')
bell, airbus = 'Bell / Textron', 'Airbus'
bell_cls = levc[levc['firm'] == bell].set_index('class')
airbus_cls = levc[levc['firm'] == airbus].set_index('class')
fmri = fmr.set_index('filer')
EXTRA1 = {
    'aircraft held by the 4 firms of 10+': (str(int(cov.iloc[0]['aircraft'])), '102'), 'aircraft held by the next 12': (f"{int(cov.iloc[0]['firms'])}/{int(cov.iloc[1]['firms'])}/{int(cov.iloc[1]['aircraft'])}", '4/12/80'),
    'named companies, individuals, universities (aircraft)': (f"{int(fmi.loc['Named companies', 'unique aircraft'])} / {int(fmi.loc['Individual inventors', 'unique aircraft'])} / {int(fmi.loc['Universities and institutes', 'unique aircraft'])}", '397 / 186 / 44'),
    'companies and individuals over representative patents': (f"{pct(fmri.loc['Named companies', 'share per representative patent'])} / {pct(fmri.loc['Individual inventors', 'share per representative patent'])}", '75 % / 20 %'),
    'largest holdings: Tilt Body, Tilt Propulsor, CVT': (f"{pct(cbi.loc['TB', 'its share'])} / {pct(cbi.loc['TR', 'its share'])} / {pct(cbi.loc['CVT', 'its share'])}", '21 % / 18 % / 16 %'),
    'filer of those three': (' / '.join(cbi.loc[c, 'largest filer'] for c in ('TB', 'TR', 'CVT')), 'Bell / Textron / Bell / Textron / Bell / Textron'),
    'effective filers of the four largest classes (smallest)': (f"{cb.sort_values('aircraft', ascending=False).head(4)['effective filers'].min():.0f}", '24'),
    'effective filers of Lift + Cruise': (f"{cbi.loc['SLC', 'effective filers']:.0f}", '57'),
    'Bell / Textron share of Tilt Propulsor in 2016-19': (f"{pct(cbi.loc['TR', 'largest share inside one window'])} in {cbi.loc['TR', 'in window']}", '34 % in 2016-19'),
    'one inventor, Lift + Cruise, window and its aircraft': (f"{pct(cbi.loc['SLC', 'largest share inside one window'])} in {cbi.loc['SLC', 'in window']}, {int(cbi.loc['SLC', 'window aircraft'])} aircraft", '29 % in <= 2011, 17 aircraft'),
    'Bell / Textron: Lift + Cruise share rises (pts)': (f"{bell_cls.loc['SLC', 'shift all years (pp)']:.1f}", '2.6'),
    'Bell / Textron lowers Tilt Propulsor, CVT, Tilt Wing (pts)': (' / '.join(f"{abs(bell_cls.loc[c, 'shift all years (pp)']):.1f}" for c in ('TR', 'CVT', 'TW')), '2.2 / 1.2 / 0.5'),
    'Bell / Textron Lift + Cruise aircraft': (str(int(bell_cls.loc['SLC', 'firm aircraft in the class'])), '1'),
    'second firm and its move (pts)': (f"{lev.iloc[1]['firm']} {lev.iloc[1]['shift magnitude (pp)']:.1f}", 'Airbus 1.1'),
    'Airbus: Lift + Cruise aircraft of its total': (f"{int(airbus_cls.loc['SLC', 'firm aircraft in the class'])} of {int(airbus_cls.loc['SLC', 'firm aircraft'])}", '12 of 21'),
    'largest move inside one window (pts, firm, window)': (f"{lev['largest shift inside one window (pp)'].max():.1f} {lev.loc[lev['largest shift inside one window (pp)'].idxmax(), 'firm']} {lev.loc[lev['largest shift inside one window (pp)'].idxmax(), 'that window']}", '5.2 Bell / Textron 2016-19'),
    'Airbus move in 2012-15 (pts) and its window aircraft': (f"{abs(airbus_cls.loc['SLC', 'shift 2012-15 (pp)']):.1f}, {int(airbus_cls.loc['SLC', 'window aircraft 2012-15'])}", '3.0, 58'),
    'best-funded firm, its amount and first patent': (f"{d18.sort_values('funding $M').iloc[-1]['company']} {thin(d18['funding $M'].max())} {int(d18.sort_values('funding $M').iloc[-1]['first patent'])}", 'Joby Aviation 5 181 2013'),
    'funding against aircraft: rho, p': (f"{tt.loc['unique aircraft', 'rho']:+.2f}, p {tt.loc['unique aircraft', 'p']:.2f}", '+0.56, p 0.11'),
    'funding against lead: rho, p, n': (f"{tt.loc['years first patent to first flight', 'rho']:+.2f}, p {tt.loc['years first patent to first flight', 'p']:.2f}, {int(tt.loc['years first patent to first flight', 'firms'])}", '+0.48, p 0.23, 8'),
    'funding against first patent: p': (f"p {tt.loc['first patent', 'p']:.3f}", 'p 0.031'),
    'CVT 5-6: filers hold one each': (str(int(fs['filers holding one aircraft'])), '12'),
}
extra1 = pd.DataFrame([{'quoted': k, 'notebook': m, 'document': d, 'match': 'yes' if checks._norm(m) == checks._norm(d) else 'NO'} for k, (m, d) in EXTRA1.items()])
extra1""")

# ------------------------------------------------------------------------------------------ 4.2
md(question_and_method("4.2", "", ""))
md("""### First-time against returning filers

`frames.named_entries` keeps the aircraft of named organisations that have a window and flags each as first-time (the firm's earliest window in the corpus is this window) or returning; the class is kept for Lift + Cruise, Tilt Propulsor, CVT, Tilt Wing and Multirotor, the rest is pooled. `frames.entry_split` gives the class mix of the two groups per complete window, `frames.entry_split_test` the chi-square p of class against group (`lib.association.chi2_p_of_crosstab`) where the returning group holds 20 aircraft or more, and again without the returning firm that holds most of them (a test added after the first result was seen). `frames.tw_entry` reads Tilt Wing's entering firms against its share of all aircraft, with Fisher's exact test (`lib.association.fisher_exact_p`) of the change from the window before. The three tables are checked against the document (the class columns print the document's names, Tilt Rotor for Tilt Propulsor).""")
code(r"""DOCCLS = {'SLC': 'Lift + Cruise', 'TR': 'Tilt Rotor', 'CVT': 'CVT', 'TW': 'Tilt Wing', 'MR': 'Multirotor', 'other': 'other classes'}
ent = frames.named_entries(v, WIN_NAMES)
es = frames.entry_split(ent, COMPLETE, DOCCLS)
et = frames.entry_split_test(ent, COMPLETE)
twe = frames.tw_entry(v, COMPLETE)
verify(es, 'la_entry_split', key=['window', 'group'], doc_wording=False)
verify(et, 'la_entry_split_test', key=['window'], doc_wording=False)
verify(twe, 'la_tw_entry', key=['window'], doc_wording=False)
save.table(thesis_names(es), cfg, 'q4', 'tab_entry_split', caption='The class mix of the aircraft of first-time and returning named organisations, per priority window.',
           source='PatSeer (assignee, priority date) · human labelling · unit: unique aircraft')
save.table(et, cfg, 'q4', 'tab_entry_split_test', caption='Chi-square test of class against first-time or returning, in the windows where the returning group holds 20 aircraft or more, with and without the largest returning firm.',
           source='PatSeer (assignee, priority date) · human labelling · unit: unique aircraft')
save.table(twe, cfg, 'q4', 'tab_tilt_wing_entry', caption="Tilt Wing's entering firms against its share of all aircraft, per priority window.",
           source='PatSeer (assignee, priority date) · human labelling')
display(thesis_names(es)); display(et); twe""")
md("""### Figure 19 — who moves the class mix

(i) The classes of the aircraft of first-time and returning filers in the two windows that can be tested, with the chi-square p and the returning firm that holds most of the returning aircraft. (ii) Tilt Wing's share of the firms entering in each window (hatched; above it that share, then the firms entering with a Tilt Wing of all firms entering) beside its share of all the window's aircraft (grey; under each window, Tilt Wing aircraft over all the window's aircraft).""")
code(r"""tested = et[et['p'].notna()]
codes19 = ['SLC', 'TR', 'CVT', 'TW', 'MR', 'other']
style19 = {c: (style.cls(c) if c != 'other' else ('#e3e3e3', '||||')) for c in codes19}
rows, labels, pos, notes = [], [], [], []
y0 = 0.0
for _, t_ in tested.iterrows():
    sub = es[es['window'] == t_['window']].set_index('group')
    for g, lab in (('first-time filers', 'first-time'), ('returning filers', 'returning')):
        rows.append(sub.loc[g, [DOCCLS[c] for c in codes19]].astype(float).to_numpy())
        labels.append(f"{WSHORT[t_['window']]} {lab}\n{int(sub.loc[g, 'aircraft'])} aircraft"); pos.append(y0); y0 += 1.0
    notes.append((y0 - 0.5 + 0.12, f"χ² p {t_['p']:.3f} · {t_['largest returning firm']}: {int(t_['its aircraft'])} of the {int(t_['returning aircraft'])} returning aircraft"))
    y0 += 0.95
parts19 = pd.DataFrame(rows, columns=codes19)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 3.9), constrained_layout=True, gridspec_kw={'width_ratios': [1.75, 1.0]})
plots.stack_bars(a1, parts19, style19, positions=pos, width=0.8, horizontal=True, min_label=0.07, fontsize=7.5)
for y_, t_ in notes:
    a1.text(0.0, y_, t_, ha='left', va='top', fontsize=7.5, color=style.MUTED)
a1.set_yticks(pos, labels, fontsize=7.5); a1.invert_yaxis(); a1.set_xlim(0, 1); a1.set_ylim(pos[-1] + 1.05, -0.55)
a1.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); a1.spines[['left']].set_visible(False); a1.tick_params(axis='y', length=0)
a1.set_xlabel("share of the group's aircraft"); style.mark(a1, '(i)')
x = np.arange(len(twe))
ea, aa = twe['Tilt Wing share of entrants'].to_numpy(), twe['Tilt Wing share of the aircraft'].to_numpy()
tws = style.cls('TW')
a2.bar(x - 0.19, aa, 0.36, color='#bdbdbd', edgecolor='white', linewidth=0.6, zorder=3)
a2.bar(x + 0.19, ea, 0.36, color=tws.color, hatch=tws.hatch, edgecolor='white', linewidth=0.6, zorder=3)
for i in range(len(x)):
    a2.text(x[i] + 0.19, ea[i] + 0.004, f"{100 * ea[i]:.0f} %\n{int(twe['entering with Tilt Wing'][i])} of\n{int(twe['firms entering'][i])}", ha='center', va='bottom', fontsize=7, linespacing=1.0)
    a2.text(x[i] - 0.19, aa[i] - 0.004, f"{100 * aa[i]:.0f} %", ha='center', va='top', fontsize=7, rotation=90)
a2.set_xticks(x, [f"{WSHORT[w]}\n{int(a)}/{int(n)}" for w, a, n in zip(twe['window'], twe['Tilt Wing aircraft'], twe['aircraft in the window'])], fontsize=7)
a2.set_ylim(0, float(max(ea.max(), aa.max())) + 0.06); a2.yaxis.set_major_locator(mticker.MultipleLocator(0.04)); a2.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
a2.grid(axis='y', color=style.GRID, linewidth=0.5); a2.set_axisbelow(True); style.mark(a2, '(ii)')
a2.set_ylabel('Tilt Wing share')
fig.legend(handles=[Patch(facecolor=style19[c].color if hasattr(style19[c], 'color') else style19[c][0], hatch=style19[c].hatch if hasattr(style19[c], 'hatch') else style19[c][1], edgecolor='white',
                          label=DOCCLS[c].replace('Tilt Rotor', 'Tilt Propulsor')) for c in codes19] +
           [Patch(facecolor='#bdbdbd', label="Tilt Wing, share of all the window's aircraft"), Patch(facecolor=tws.color, hatch=tws.hatch, edgecolor='white', label='Tilt Wing, share of the firms entering')],
           loc='outside lower center', ncol=4, fontsize=7.5, handlelength=1.3, columnspacing=1.0)
plt.show()
fig19_data = pd.concat([es.assign(panel='(i)'), et.assign(panel='(i) test'), twe.assign(panel='(ii)')], ignore_index=True)
save.figure(fig, cfg, 'q4', 'fig_19_entry_split', data=fig19_data,
            caption=@CAP@,
            source='PatSeer (assignee, priority date) · human labelling',
            unit=f"(i) unique aircraft of named organisations, in the windows where the returning group holds {frames.CH4_TEST_MIN} aircraft or more; (ii) the named organisation (hatched), the unique aircraft (grey, individuals included)",
            read="(i) Each bar is 100 % of one group of aircraft: those of firms filing for the first time in the window, and those of firms that filed in an earlier window; a segment of 7 % or more prints its share. Under each pair: the chi-square p of class against group and the returning firm holding most of the returning aircraft. (ii) Hatched: the share of the firms entering the dataset in the window whose first aircraft is a Tilt Wing (above it, that share, then the firms entering with a Tilt Wing of all firms entering). Grey: Tilt Wing's share of all the window's aircraft (printed inside the bar; under each window, Tilt Wing aircraft over all the window's aircraft).",
            panels={'(i)': 'class of first-time and returning filers', '(ii)': "Tilt Wing's entering firms and aircraft"})
plt.close(fig)""", CAP=q(caption("Figure", 19)))
md("""### Where a firm's next aircraft lands

`frames.succession_pairs` follows each named organisation's aircraft in priority order (aircraft of the same year in the order of the labelled dataset, which is arbitrary) and keeps every consecutive pair; `frames.succession_matrix` gives, per class of origin with 10 successions or more, the share of the next aircraft that stay in the class and where the others go (the row sums to 100 %), and the share that stays without the firm with the most successions. Checked against the document.""")
code(r"""pairs = frames.succession_pairs(v)
succ = frames.succession_matrix(pairs)
verify(succ, 'la_succession_matrix', key=['code'])
save.table(succ, cfg, 'q4', 'tab_succession_matrix', caption="Where a named organisation's next aircraft lands, by the class of the one before: successions, firms and the share of each destination.",
           source='PatSeer (assignee, priority date) · human labelling · unit: succession')
succ""")
md("""### Figure 20 — where a firm's next aircraft lands

One row per class of origin with 10 successions or more; each row sums to 100 %; the boxed cell is the share that stays in the class.""")
code(r"""dest = [('SLC', 'Lift +\nCruise'), ('TR', 'Tilt\nPropulsor'), ('CVT', 'CVT'), ('TW', 'Tilt\nWing'), ('MR', 'Multi-\nrotor'), ('PTC', 'Pitch-to-\nCruise'), ('other', 'other')]
M = succ[[f"→ {c}" for c, _ in dest]].to_numpy(dtype=float)
fig, ax = plt.subplots(figsize=(W, 3.4), constrained_layout=True)
im = ax.imshow(M, cmap='Greys', vmin=0, vmax=0.8, aspect='auto')
for i, r in succ.reset_index(drop=True).iterrows():
    for j, (c, _) in enumerate(dest):
        val = M[i, j]
        ax.text(j, i, f"{100 * val:.0f} %" if val > 0 else '–', ha='center', va='center', fontsize=7.5, color='white' if val >= 0.4 else style.INK,
                fontweight='bold' if c == r['code'] else None)
        if c == r['code']:
            ax.add_patch(matplotlib.patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=style.INK, linewidth=1.8, zorder=5, clip_on=False))
ax.set_xticks(range(len(dest)), [d[1] for d in dest], fontsize=7.5); ax.xaxis.tick_top()
ax.set_yticks(range(len(succ)), [f"{'CVT' if c == 'CVT' else style.cls(c).name}\n{int(n)} successions · {int(f)} firms" for c, n, f in zip(succ['code'], succ['successions'], succ['firms'])], fontsize=7.5)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_ylabel("class of the firm's aircraft")
ax.set_xlabel("class of the same firm's next aircraft"); ax.xaxis.set_label_position('top'); ax.xaxis.labelpad = 8
plt.show()
save.figure(fig, cfg, 'q4', 'fig_20_successions', data=succ,
            caption=@CAP@,
            source='PatSeer (assignee, priority date) · human labelling',
            unit=f"the succession: a named organisation's aircraft and the same firm's next aircraft in priority order ({int(succ.iloc[0]['successions, all classes'])} of them, from the {int(succ.iloc[0]['firms with a succession'])} firms with two aircraft or more); the classes of origin with {frames.CH4_SUCC_MIN} successions or more",
            read="Each row is the class of a firm's aircraft; each cell the share of the firm's next aircraft that lands in the column's class (a row sums to 100 %; – is none). Darker is a larger share. The boxed cell, in bold, is the share that stays in the class. Under each class: its successions and the firms that make them; a firm with many aircraft contributes many successions.")
plt.close(fig)""", CAP=q(caption("Figure", 20)))
md("""### 4.2 numbers""")
code(r"""eti, twi, si = et.set_index('window'), twe.set_index('window'), succ.set_index('code')
N2 = {'c4_test_min': str(frames.CH4_TEST_MIN), 'c4_succ_min': str(frames.CH4_SUCC_MIN),
      'c4_p_1619': pval(eti.loc['2016-19', 'p']), 'c4_p_2023': pval(eti.loc['2020-23', 'p']),
      'c4_big_1619': eti.loc['2016-19', 'largest returning firm'], 'c4_big_ret_1619': str(int(eti.loc['2016-19', 'its aircraft'])),
      'c4_ret_1619': str(int(eti.loc['2016-19', 'returning aircraft'])),
      'c4_ent_1619': str(int(twi.loc['2016-19', 'firms entering'])), 'c4_ent_2023': str(int(twi.loc['2020-23', 'firms entering'])),
      'c4_tw_n_1619': str(int(twi.loc['2016-19', 'entering with Tilt Wing'])), 'c4_tw_n_2023': str(int(twi.loc['2020-23', 'entering with Tilt Wing'])),
      'c4_pairs': str(len(pairs)), 'c4_pair_firms': str(pairs['firm'].nunique()),
      'c4_slc_stay': pct(si.loc['SLC', 'stays in the class']), 'c4_tr_stay': pct(si.loc['TR', 'stays in the class']), 'c4_tw_stay': pct(si.loc['TW', 'stays in the class'])}
numbers_check(N2)""")
code(r"""# also quoted in the takeaways of 4.2 (not in the document's number list): each against the figure the document prints
e16, e20 = es[es['window'] == '2016-19'].set_index('group'), es[es['window'] == '2020-23'].set_index('group')
tw23 = twi.loc['2020-23']
EXTRA2 = {
    'first-time aircraft of named organisations 2016-19, 2020-23': (f"{int(eti.loc['2016-19', 'first-time aircraft'])} of {int(eti.loc['2016-19', 'first-time aircraft'] + eti.loc['2016-19', 'returning aircraft'])}, {int(eti.loc['2020-23', 'first-time aircraft'])} of {int(eti.loc['2020-23', 'first-time aircraft'] + eti.loc['2020-23', 'returning aircraft'])}", '98 of 155, 120 of 181'),
    '2016-19 returning: Tilt Propulsor against first-time': (f"{pct(e16.loc['returning filers', 'Tilt Rotor'])} against {pct(e16.loc['first-time filers', 'Tilt Rotor'])}", '35 % against 13 %'),
    '2016-19 first-time: Lift + Cruise against returning': (f"{pct(e16.loc['first-time filers', 'Lift + Cruise'])} against {pct(e16.loc['returning filers', 'Lift + Cruise'])}", '32 % against 14 %'),
    'chi-square p without the largest returning firm': (f"{pval(eti.loc['2016-19', 'p without it'])}, {pval(eti.loc['2020-23', 'p without it'])}", '0.59, 0.38'),
    'Tilt Wing entering share 2016-19, 2020-23': (f"{pct(twi.loc['2016-19', 'Tilt Wing share of entrants'])}, {pct(twi.loc['2020-23', 'Tilt Wing share of entrants'])}", '12 %, 11 %'),
    'Tilt Wing share of the aircraft 2016-19, 2020-23': (f"{pct(twi.loc['2016-19', 'Tilt Wing share of the aircraft'])}, {pct(twi.loc['2020-23', 'Tilt Wing share of the aircraft'])}", '11 %, 8 %'),
    'Fisher p of that fall': (f"p {tw23['Tilt Wing share, Fisher p against the window before']:.2f}", 'p 0.33'),
    'Tilt Wing entrants 2020-23: universities, no other aircraft': (f"{int(tw23['Tilt Wing entrants: universities / institutes'])} ({pct(tw23['Tilt Wing entrants: universities / institutes'] / tw23['entering with Tilt Wing'])}), {int(tw23['Tilt Wing entrants: no other aircraft'])} ({pct(tw23['Tilt Wing entrants: no other aircraft'] / tw23['entering with Tilt Wing'])})", '3 (33 %), 6 (67 %)'),
    'all entrants 2020-23: universities, no other aircraft': (f"{int(tw23['all entrants: universities / institutes'])} ({pct(tw23['all entrants: universities / institutes'] / tw23['firms entering'])}), {int(tw23['all entrants: no other aircraft'])} ({pct(tw23['all entrants: no other aircraft'] / tw23['firms entering'])})", '15 (18 %), 56 (68 %)'),
    'CVT stays': (pct(si.loc['CVT', 'stays in the class']), '44 %'),
    'Tilt Wing successions and firms': (f"{int(si.loc['TW', 'successions'])}, {int(si.loc['TW', 'firms'])}", '23, 13'),
    'Tilt Wing goes to Tilt Propulsor, Lift + Cruise': (f"{pct(si.loc['TW', '→ TR'])}, {pct(si.loc['TW', '→ SLC'])}", '44 %, 22 %'),
    'successions of the largest filer': (f"{succ.iloc[0]['firm left out']}, {int(succ.iloc[0]['its successions, all classes'])} of {int(succ.iloc[0]['successions, all classes'])}", 'Bell / Textron, 59 of 240'),
}
extra2 = pd.DataFrame([{'quoted': k, 'notebook': m, 'document': d, 'match': 'yes' if checks._norm(m) == checks._norm(d) else 'NO'} for k, (m, d) in EXTRA2.items()])
extra2""")

# ------------------------------------------------------------------------------------------ overview
md("""## Overview: what matched

Every number the document quotes for chapter 4 (56) and every table, with the differences labelled.""")
code(r"""allnum = pd.concat(NUMBERS, ignore_index=True)
n_doc = len(checks.reference_numbers('4'))
missing = checks.missing_numbers(dict.fromkeys(allnum['name']), '4')
print(f"numbers: {int((allnum['match'] == 'yes').sum())} of {len(allnum)} match the document; "
      f"{int(allnum['match'].str.startswith('expected').sum())} expected differences; {int((allnum['match'] == 'NO').sum())} failures; "
      f"{len(missing)} of the document's {n_doc} not computed here: {missing}")
overview = pd.DataFrame([c.iloc[0].to_dict() for c in CHECKS])
overview""")
code(r"""assert (allnum['match'] != 'NO').all(), allnum[allnum['match'] == 'NO']
assert not missing
assert (overview['differences'] == 0).all(), overview[overview['differences'] > 0]
assert (extra1['match'] == 'yes').all(), extra1[extra1['match'] == 'NO']
assert (extra2['match'] == 'yes').all(), extra2[extra2['match'] == 'NO']""")


nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, OUT)
print("written", OUT, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(OUT)], check=True, cwd=str(OUT.parent))
