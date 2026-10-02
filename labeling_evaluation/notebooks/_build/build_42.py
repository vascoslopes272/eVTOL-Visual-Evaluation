"""Generate notebooks/42_q3_evolution_dominant_design.ipynb (and execute it with --run).

    python3 notebooks/_build/build_42.py          # write the notebook
    python3 notebooks/_build/build_42.py --run    # write, then jupyter nbconvert --execute --inplace

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
OUT = PILLAR / "notebooks" / "42_q3_evolution_dominant_design.ipynb"
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
INTRO = "\n".join(_section("## 3 —", "### 3.1 —")).strip().replace("## 3 —", "### Chapter 3 —", 1)

md("""# 42 — Question 3: the evolution and the dominant-design test

Is there a dominant eVTOL design or is the field still experimenting, and how have the designs changed over twenty years of filing?

Sub-questions 3.1, 3.2, 3.3, 3.4 of the Labelling Analysis (2026-09-30). Every path comes from `labelling_analysis.yaml`; equations come from `lib/`, figures and tables from `viz/`.

This notebook reproduces every figure, table and number of chapter 3 of the 45-page document, and compares them with it (`viz.checks`). Chapter 3 reads the twelve classes (Figure 10, the archetype sets, the configurations and the traces), never the five-class fold, so the class fold of 2026-10-01 (Stopped/Slowed Rotor Wing into Lift + Cruise) moves no number here. The differences from the document's tables are the display names of 2026-09-28 (Tilt Rotor is printed Tilt Propulsor, propulsive unit is printed propulsor unit, rotor control is printed propulsor control), which `viz.checks` maps. The method is reproduced as the document has it: nothing is changed (METHOD_NOTES.md lists what the author is still deciding, e.g. condition 3's Q counts each aircraft's distance to itself, 0).

Figure 2 of 3.1 is printed in chapter 1 (notebook 40); this notebook reproduces the numbers of the directory's dating that 3.1 quotes. Outputs are written to `<output>/q3_evolution_dominant_design/` (figures: pdf, png, csv, json; tables: csv, json). Regenerate this notebook with `python3 notebooks/_build/build_42.py`.""")
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

`frames.base` is the per-aircraft analysis frame (627 rows); `lib` holds every equation (`lib.dominant_design`: the three conditions and their permutation bands; `lib.diversity`: ¹D, ²D with rarefaction; `lib.distance`: the Gower distance; `lib.drivers`: trace trends, driver verdicts, window centres); `viz.checks` compares with the document. `verify` runs one table check and keeps its summary for the final overview; `numbers_check` does the same for the quoted numbers. A cell written in the thesis names (Tilt Propulsor, propulsor units) is compared with the document's wording through `checks.rename_map`.""")
code(r"""import inspect
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from IPython.display import display
from viz import frames, style, plots, save, checks
from lib import dominant_design, diversity, drivers, distance

style.apply(cfg)
frames.set_window_bounds(cfg)                              # the yaml's windows, for the verdict of condition 1
v = frames.base(ds, cfg)                                   # one row per unique aircraft (627)
WIN_NAMES = list(cfg.analysis['windows'])
COMPLETE = [w for w in WIN_NAMES if 'partial' not in w]    # the four windows with a complete priority year
FEW = COMPLETE[:2]                                         # the two early windows hold few aircraft
W, _ = style.size(cfg, 'full')
SEED = cfg.analysis['random_seed']
LAST = cfg.analysis['last_complete_year']
pct = lambda x: f"{x:.0%}".replace('%', ' %')              # 0.53 -> '53 %'
pct1 = lambda x: f"{100 * x:.1f} %"                        # 0.518 -> '51.8 %' (condition 1 turns on whether 50.0 % is more than half)
thin = lambda n: f"{int(n):,}".replace(',', ' ')           # 1 229
pval3 = lambda p: '< 0.001' if p < 0.001 else f"{p:.3f}"   # the form of the Method's p
ptxt = lambda p: 'p < 0.001' if p < 0.001 else f"p {p:.2f}" if p >= 0.01 else f"p {p:.3f}"   # the form of the verdict table's p
CHECKS, NUMBERS = [], []                                   # summaries kept for the overview at the end
TICK = plots.WINDOW_TICKS                                  # '<= 2011' -> '≤2011'
WSHORT = {'<= 2011': '≤2011', '2012-15': '12–15', '2016-19': '16–19', '2020-23': '20–23'}
CLASS_NAMES = {c: style.cls(c).name for c in style.CLASS_ORDER}

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
    r = checks.numbers(values, '3', expected)
    NUMBERS.append(r)
    display(r)

def style_legend(codes):
    return [Patch(facecolor=style.cls(c).color, hatch=style.cls(c).hatch, edgecolor='white',
                  label=f"{style.cls(c).short} {style.cls(c).name}" if c != 'Other' else 'no class recorded') for c in codes]""")
md("""### 0.1 The numbers of the Method common to every chapter

The rarefaction size, the seed, the draws behind each rarefied ²D, the snapshot date, and the share of families of 2022 and 2023 still neither granted nor refused (the author's check of the PatSeer export, `assets/external/lapse_check`).""")
code(r"""status = pd.read_csv(cfg.path('grant_status_by_year'))
pending = lambda y: f"{float(status.loc[status['priority_year'] == y, 'pending_pct'].iloc[0]):.1f} %"
N0 = {'sm_perm_n': str(cfg.analysis['rarefy_n']), 'sm_perm_seed': str(SEED),
      'sm_perms': str(inspect.signature(dominant_design.balance_band).parameters['perms'].default),
      'sm_rare_draws': str(inspect.signature(dominant_design.balance_band).parameters['obs_draws'].default),
      'snapshot': frames.snapshot_date(ds), 'sm_lapse_p2022': pending(2022), 'sm_lapse_p2023': pending(2023)}
numbers_check(N0)""")

# ------------------------------------------------------------------------------------------ 3.1
md(question_and_method("3.1", "", ""))
md("""### The class mix per priority window

Unique aircraft per window and class (`frames.class_counts_by_window`), and each window's shares: the data of Figure 10. The four columns of the document's table (Tilt Propulsor, Lift + Cruise, CVT, Multirotor) are checked; the document's table holds only those four classes, the figure all twelve and the few aircraft of a window with no class recorded (they count in the window's total, as in the document).""")
code(r"""cnt = frames.class_counts_by_window(v, WIN_NAMES)         # windows x class (+ Other: no class recorded), the aircraft with a window
n_win = cnt.sum(axis=1)
share = cnt.div(n_win, axis=0)
d9 = pd.DataFrame({'window': WIN_NAMES, 'unique aircraft': n_win.to_numpy(), 'Tilt Rotor': share['TR'].round(2).to_numpy(),
                   'Lift + Cruise': share['SLC'].round(2).to_numpy(), 'Combined vectored thrust': share['CVT'].round(2).to_numpy(),
                   'Multirotor': share['MR'].round(2).to_numpy()})        # the document's column names (Tilt Rotor = Tilt Propulsor)
STALE = 'expected: different base, not an error. The document table divides by the 211 classed aircraft (50/211 = 24 %); its Figure 10 divides by all 213, two with no class recorded (50/213 = 23 %). See METHOD_NOTES.md #8'
verify(d9, 'a2_d9_architecture_by_window', key=['window'], doc_wording=False,
       expected=lambda k, c: STALE if (k, c) == ('2016-19', 'Tilt Rotor') else None)
(share.round(3).assign(n=n_win)).rename(columns={c: style.cls(c).short for c in share.columns})""")
md("""### Figure 10 — architecture mix per priority window

(i) Every class's share of the window's unique aircraft; the 2024-26 window is still filling and is drawn with a dashed frame and a star. (ii) The five largest classes over the windows, one line each (the class's colour, dash and marker).""")
code(r"""codes10 = [c for c in style.CLASS_ORDER if c in cnt.columns] + ['Other']      # Other: the aircraft with no class recorded
five = ['SLC', 'TR', 'CVT', 'TW', 'MR']
tick10 = [f"{WSHORT.get(w, '24–26*')}\nn {int(n)}" for w, n in zip(WIN_NAMES, n_win)]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 3.7), constrained_layout=True, gridspec_kw={'width_ratios': [1.15, 1]})
sh = share[codes10].copy(); sh.index = list(range(len(sh)))
plots.share_bars(ax, sh, partial=[len(sh) - 1], min_label=0.05, label_kind='pct')
ax.set_xticks(range(len(WIN_NAMES)), tick10); style.mark(ax, '(i)')
ax.set_ylabel("share of the window's unique aircraft")
lines = share[five].copy(); lines.index = list(range(len(lines)))
plots.window_lines(ax2, lines, n_few=0, ticks=[WSHORT.get(w, '24–26*') for w in WIN_NAMES])
ax2.axvspan(len(WIN_NAMES) - 1.5, len(WIN_NAMES) - 0.5, facecolor=plots.FEW_FILL, hatch=style.PARTIAL_HATCH, edgecolor=style.GRID, linewidth=0, zorder=0)
ax2.set_xlim(-0.3, len(WIN_NAMES) + 0.55)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax2.grid(axis='y', color=style.GRID, linewidth=0.5); ax2.set_axisbelow(True)
ax2.set_ylim(0.04, 0.37)
last = lines.iloc[-1]
plots.end_labels(ax2, len(WIN_NAMES) - 1, [last[c] for c in five], [style.cls(c).short for c in five], [style.cls(c).color for c in five], gap=0.024)
style.mark(ax2, '(ii)')
fig.legend(handles=style_legend(codes10), loc='outside lower center', ncol=4, fontsize=7.5, handlelength=1.2, columnspacing=1.0)
plt.show()
fig10_data = share.round(4).assign(aircraft=n_win)
save.figure(fig, cfg, 'q3', 'fig_10_class_mix_by_window', data=fig10_data,
            caption=@CAP@,
            source='human labelling (class) · PatSeer (priority date)',
            unit=f"unique aircraft ({int(n_win.sum())}) per four-year priority window; the window 2024-26 is still filling (hatched, dashed frame, star)",
            read="(i) Each bar is 100 % of one window; a segment of 5 % or more prints its share in percent, smaller ones are in the key. The number under each window is its aircraft. (ii) The five largest classes: one line each, in the class's colour, dash and marker; the line ends are named. Shares are read, never counts, because a share can fall while the count grows. The earliest window rests on few aircraft, so its shares are coarse.",
            panels={'(i)': 'class share per window', '(ii)': 'the five largest classes over time'})
plt.close(fig)""", CAP=q(caption("Figure", 10)))
md("""### The directory's dating

The evtol.news directory (crawled 2026-09-17) is dated by development year; two readers each named the dating sentence. The table counts, per directory class, the aircraft on the list, those the readers agree on (used), those they disagree on (left out until the author rules) and those whose page states no year (`frames.evtolnews_coverage`); it is checked against the document. The comparison of the two mixes is Figure 2, in chapter 1.""")
code(r"""cov = frames.evtolnews_coverage(cfg)
verify(cov, 'la_evtolnews_coverage', key=['directory class'])
save.table(cov, cfg, 'q3', 'tab_dating_evtolnews', caption='The evtol.news directory aircraft by the dating of their development year, per directory class.',
           source='evtol.news directory (Vertical Flight Society), crawled 2026-09-17; development year read by two readers (language-model instances)')
cov""")
md("""### 3.1 numbers""")
code(r"""allc = cov.set_index('directory class').loc['all classes']
N1 = {'tk_tr_w1': pct(share.loc['<= 2011', 'TR']), 'tk_tr_w4': pct(share.loc['2020-23', 'TR']),
      'tk_slc_w1': pct(share.loc['<= 2011', 'SLC']), 'tk_slc_w4': pct(share.loc['2020-23', 'SLC']),
      'sm_evn_list': thin(allc['aircraft on the list']), 'sm_evn_agreed': thin(allc['agreed by both readers']),
      'sm_evn_dated': thin(allc['dated (in the panel)']), 'sm_evn_conflict': thin(allc['conflict, not yet ruled']),
      'sm_evn_notstated': thin(allc['not stated on the page']), 'sm_evn_dated_share': pct(allc['dated share']),
      'sm_evn_min_n': str(cfg.analysis['evtolnews_min_n'])}
numbers_check(N1)
print('also quoted in the takeaway: with CVT', pct(share.loc['2020-23', 'CVT']), 'the three hold', pct(share.loc['2020-23', ['SLC', 'TR', 'CVT']].sum()),
      'of the 2020-23 aircraft; the earliest window rests on', int(n_win['<= 2011']), 'aircraft against', int(n_win['2020-23']), '; 2016-19: TP', pct(share.loc['2016-19', 'TR']), 'L+C', pct(share.loc['2016-19', 'SLC']))""")

# ------------------------------------------------------------------------------------------ 3.2
md(question_and_method("3.2", "", ""))
md("""### Condition 1: the largest archetype per priority year

`frames.dd_yearly` gives, per archetype set (C, C·W·T, C·U, F) and base (the aircraft with at least one patent in force, and every aircraft of the year), the largest archetype's share of each priority year 2008-2023 (`lib.dominant_design.yearly_top_share`: the largest archetype and its share, ties by first appearance, a year is read when its base holds 20 aircraft or more). `frames.family_yearly` is the same for F with the share of the in-force aircraft that hold a granted patent. Both are checked against the document. F is every Lift + Cruise aircraft plus every CVT aircraft whose tilting propulsor set sits on a wing that does not tilt (`frames.family_flags`, `frames.family_mask`).""")
code(r"""fy = frames.family_yearly(ds, v, LAST)
verify(fy, 'la_family_yearly', key=['priority year'])
dy = frames.dd_yearly(ds, v, LAST)
verify(dy, 'la_dd_yearly', key=['level id', 'base', 'priority year'])
fy""")
md("""### Figure 11 — condition 1 on F, per priority year

F's share of the year's aircraft on the two bases against the 50 % line. A year is read when its base holds 20 aircraft or more (from 2016 in force, from 2015 on all aircraft); condition 1 is met when one archetype is above 50 % in two consecutive read years (`lib.dominant_design.condition1_years`), ringed in red. Under each year: the aircraft in force, all aircraft, and the share of the in-force aircraft with a granted patent.""")
code(r"""yrs = fy['priority year'].to_numpy()
met = sorted(dominant_design.condition1_years(pd.DataFrame({'priority year': yrs, 'read': fy['read, in force'], 'above 50 %': fy['F share in force'] > 0.5})))
first_read = int(yrs[fy['read, in force'].to_numpy()][0])
fig, ax = plt.subplots(figsize=(W, 3.5), constrained_layout=True)
plots.condition1_years(ax, yrs, fy['F share in force'], fy['F share'], fy['read, in force'], fy['read, all'], met, first_read,
                       f"few aircraft in force\n(under {cfg.analysis['trend_min_n']} a year): not read")
fi, fa = fy.set_index('priority year')['F share in force'], fy.set_index('priority year')['F share']
for k, y in enumerate(met):                                  # the shares of the two met years, both bases
    side = -1 if k == 0 else 1
    ax.annotate(pct1(fi[y]), (y, fi[y]), textcoords='offset points', xytext=(side * 9, 10), ha='right' if side < 0 else 'left', va='bottom',
                fontsize=7.5, fontweight='bold', color=style.INK)
    ax.annotate(f"all: {pct1(fa[y])}", (y, fa[y]), xytext=(y + 0.15, 0.33 if k == 0 else 0.24), textcoords='data', ha='center', va='top', fontsize=7.5,
                color=style.MUTED, arrowprops=dict(arrowstyle='-', color=style.MUTED, linewidth=0.5, shrinkA=1, shrinkB=4))
ax.text((met[0] + met[-1]) / 2, 0.975, f"condition 1 met,\nin force: {met[0]}–{str(met[-1])[-2:]}", ha='center', va='top', fontsize=7.5,
        color=plots.MET, fontweight='bold', transform=ax.get_xaxis_transform())
ax.text(yrs[-1] + 0.5, 0.505, '50 %', ha='right', va='bottom', fontsize=7.5)
ax.set_ylabel("share of the year's aircraft\nin F (Lift + Cruise + CVT*)")
ax.set_xticks(yrs, [str(y) for y in yrs], fontsize=7)
from matplotlib.transforms import offset_copy
rows3 = [('aircraft in force', fy['aircraft in force']), ('all aircraft', fy['aircraft']),
         ('in force with a grant', fy['in force with a granted patent'].map(lambda g: '–' if not np.isfinite(g) else f'{100 * g:.0f}%'))]
for r, (name, vals) in enumerate(rows3):
    tr_ = offset_copy(ax.get_xaxis_transform(), fig=fig, y=-(20 + 10 * r), units='points')
    ax.text(-0.012, 0, name, transform=offset_copy(ax.transAxes, fig=fig, y=-(20 + 10 * r), units='points'), ha='right', va='top', fontsize=7, color=style.MUTED)
    for y_, t_, rd in zip(yrs, vals, fy['read, in force']):
        ax.text(y_, 0, str(t_), transform=tr_, ha='center', va='top', fontsize=7, color=style.INK if rd else style.MUTED)
for lab, rd in zip(ax.get_xticklabels(), fy['read, in force']):
    if not rd:
        lab.set_color(style.MUTED)
ax.set_xlabel('priority year', labelpad=43)
h = [Line2D([], [], color=style.INK, linewidth=1.7, marker='o', markersize=4.4, label='aircraft with a patent in force (main)'),
     Line2D([], [], color=style.MUTED, linewidth=1.2, linestyle='--', marker='s', markersize=4.2, markerfacecolor='white', label='all aircraft of the year'),
     Line2D([], [], marker='o', markersize=10, markerfacecolor='none', markeredgecolor=plots.MET, markeredgewidth=1.7, linestyle='none', label='two consecutive years above 50 %: met')]
fig.legend(handles=h, loc='outside lower center', ncol=3, fontsize=7.5, handlelength=2.2, columnspacing=1.2)
plt.show()
save.figure(fig, cfg, 'q3', 'fig_11_condition1_family', data=fy,
            caption=@CAP@,
            source='human labelling (class; the family F, defined after the first readings of the data) · PatSeer (priority date; legal status at the snapshot, 2026-06-08)',
            unit=f"unique aircraft by priority year, 2008-2023; F = every Lift + Cruise aircraft plus every CVT aircraft whose tilting propulsor set sits on a wing that does not tilt (CVT*); a year is read when its base holds {cfg.analysis['trend_min_n']} aircraft or more",
            read="Solid line, dots: F's share of the aircraft with at least one patent in force (granted and alive, or still under examination), the main base; dashed line, squares: F's share of every aircraft of the year. Dashed black line: 50 %. Condition 1 is met when the share is above 50 % in two consecutive read years: the ringed years and the red band. Faded years, left of the vertical line, hold fewer than 20 aircraft on the in-force base and are not read. Under each year: the aircraft in force, all aircraft, and the share of the in-force aircraft whose patent is granted (a low share is a base still made of pending applications).")
plt.close(fig)""", CAP=q(caption("Figure", 11)))
md("""### Conditions 2 and 3: balance and form

*Condition 2* (`frames.dd_balance_table` → `lib.dominant_design.balance_band`): per window and archetype set, ²D rarefied to 40 aircraft (300 draws averaged) against the middle 95 % of the ²D of the same archetypes shuffled among the windows (200 permutations, seed 42; C·U then C·W·T share one generator in that order, C and F each start a new one, as in the document). *Condition 3* (`frames.dd_form_table` → `lib.distance.gower_distance`, `lib.dominant_design.cohesion_band`): Q, the average Gower distance between two aircraft of the window under the main weighting (every subsystem equal) and the check (every field equal), ΔQ against the two earliest windows, and the band of ΔQ when the aircraft are shuffled among the windows. Q uses no archetype: C, C·U and F read the same aircraft (F's row is C's), C·W·T leaves out the aircraft whose wings or tilt are not recorded. Both tables are checked against the document.""")
code(r"""bal = frames.dd_balance_table(ds, v, WIN_NAMES, cfg.analysis['rarefy_n'], 200, SEED)
verify(bal, 'la_dd_balance', key=['level', 'window'])
form = frames.dd_form_table(ds, v, WIN_NAMES, 200, SEED)
verify(form, 'la_dd_form', key=['level', 'weighting', 'window'])
bal[['level name', 'window', 'aircraft', 'D2', 'D2 permutation low', 'D2 permutation high', 'below band']]""")
md("""### Figure 12 — conditions 2 and 3 per window

(i) ²D against its permutation band in the four archetype sets; (ii) ΔQ against its band, main weighting (solid, grey band) and check (dashed, dotted band edges). A red point is a window where the condition is met (below the band). The partial window is hatched and not read.""")
code(r"""LEVELS = frames.DD_LEVELS
TITLE = {'A0': 'C\nclass', 'A1t': 'C·W·T\nclass + wings + tilt', 'A0c': 'C·U\nclass + propulsor units', 'family_b': 'F\nLift + Cruise + CVT*'}
partial = [('partial' in w) for w in WIN_NAMES]
tk = [TICK[w] for w in WIN_NAMES]
fig = plt.figure(figsize=(W, 5.9), constrained_layout=True)
top, bot = fig.subfigures(2, 1, height_ratios=[1.0, 1.0])
axs = top.subplots(1, 4)
for ax, lvl in zip(axs, LEVELS):
    s = bal[bal['level'] == lvl].set_index('window').reindex(WIN_NAMES)
    metw = [bool(s.loc[w, 'below band']) and 'partial' not in w for w in WIN_NAMES]
    plots.balance_panel(ax, s.reset_index(), partial, metw, tk)
    ax.set_title(TITLE[lvl], fontsize=7.5, loc='left')
axs[0].set_ylabel('²D: large designs in play')
style.mark(axs[0], '(i)', lines_up=2.1)
top.legend(handles=[Patch(facecolor='#dedcd8', label='permutation band (95 %)'),
                    Line2D([], [], color=style.INK, marker='o', markersize=3.6, linewidth=1.3, label='²D rarefied to 40 (95 % of the draws)'),
                    Line2D([], [], marker='o', markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle='none', label='below the band: condition met')],
           loc='outside lower center', ncol=3, fontsize=7.5, handlelength=1.6, columnspacing=1.2)
axb = bot.subplots(1, 2, sharey=True)
main, alt = frames.Q_WEIGHTINGS
for ax, lvl, ttl in zip(axb, ('A0', 'A1t'), ('C, C·U and F (the same aircraft)', 'C·W·T')):
    s = form[form['level'] == lvl]
    sm = s[s['weighting'] == main].set_index('window').reindex(WIN_NAMES).reset_index()
    su = s[s['weighting'] == alt].set_index('window').reindex(WIN_NAMES).reset_index()
    plots.cohesion_panel(ax, sm, su, partial, [f"{WSHORT.get(w, '24–26*')}\nn {int(n)}" for w, n in zip(WIN_NAMES, sm['aircraft'])])
    ax.set_title(ttl, fontsize=7.5, loc='left')
axb[0].set_ylabel('ΔQ: change in how unlike two\naircraft are, against the\ntwo earliest windows')
style.mark(axb[0], '(ii)', lines_up=1.1)
bot.legend(handles=[Patch(facecolor='#dedcd8', label='permutation band, main weighting (every subsystem equal)'),
                    Line2D([], [], color=style.MUTED, linestyle=':', linewidth=0.9, label='band edges, every field equal'),
                    Line2D([], [], color=style.INK, marker='o', markersize=3.6, linewidth=1.5, label='ΔQ, main weighting (every subsystem equal)'),
                    Line2D([], [], color=style.MUTED, marker='^', markersize=3.8, linewidth=1.2, linestyle='--', label='ΔQ, every field equal')],
           loc='outside lower center', ncol=2, fontsize=7.5, handlelength=1.8, columnspacing=1.2)
plt.show()
fig12_data = pd.concat([bal.assign(condition='2, balance'), form.assign(condition='3, form')], ignore_index=True)
save.figure(fig, cfg, 'q3', 'fig_12_conditions_2_3', data=fig12_data,
            caption=@CAP@,
            source='human labelling (class, wings, tilt, propulsor units, every field of the distance) · PatSeer (priority date)',
            unit=f"unique aircraft per four-year priority window (C: {int(bal[(bal['level'] == 'A0') & (bal['window'] == '2020-23')]['aircraft'].iloc[0])} in 2020-23); 200 permutations, seed 42; ²D rarefied to {cfg.analysis['rarefy_n']} aircraft (300 draws); the partial window 2024-26 is hatched and not read; F = Lift + Cruise + CVT*, defined after the first readings of the data",
            read="(i) Dot: the window's ²D (how many large designs are in play) averaged over the rarefaction draws, whisker: the middle 95 % of the draws. Grey band: the middle 95 % of the ²D of the same archetypes shuffled among the windows at random, window sizes kept. A red dot is below the band: fewer designs in play than chance gives, condition 2 met. (ii) Q is the average Gower distance between two aircraft of the window (0 = alike on every design field, 1 = no field shared); ΔQ is the window's Q minus the average Q of the two earliest windows. Grey band: the middle 95 % of ΔQ when the aircraft are shuffled among the windows; a red dot is below it (condition 3 met). Solid line and band: every subsystem weighs the same (the main weighting); dashed line and dotted edges: every field weighs the same (the check). C, C·U and F read the same aircraft and share one panel; C·W·T leaves out the aircraft whose wings or tilt are not recorded.",
            panels={'(i)': 'condition 2: ²D against its permutation band, four archetype sets', '(ii)': 'condition 3: ΔQ against its permutation band, both weightings'})
plt.close(fig)""", CAP=q(caption("Figure", 12)))
md("""### Table 8 — the dominant-design verdict

`frames.dd_levels` writes, per condition and archetype set, where the condition is met (the years for condition 1, the windows for 2 and 3), by the rules of `lib.dominant_design` (`condition1_years`, `all_three_windows`). The raw table is checked against the document's `la_dd_levels`; the printed table (✓ met, ✗ not met) against the document's Table 8 as printed in the text.""")
code(r"""lv = frames.dd_levels(dy, bal, form, WIN_NAMES)
verify(lv, 'la_dd_levels', key=['condition'])
import re
def printed(cell):
    c = re.sub(r'(in force|all): no — ', r'\1: ✗ not met, ', cell)
    c = re.sub(r'(in force|all): met in', r'\1: ✓ met in', c)
    c = re.sub(r'^met in', '✓ met in', c)
    return '✗ not met' if c == 'no' else c
t8 = lv.copy()
t8['condition'] = t8['condition'].str.replace(' — ', ', ', n=1)
for c in t8.columns[1:]:
    t8[c] = t8[c].map(printed)
t8.columns = ['condition', 'C', 'C·W·T', 'C·U', 'F (defined after the first readings)']
doc8 = checks.brief_table(cfg, 8)
verify(t8, None, 'Table 8 as printed in the document', doc_wording=False, key=['condition'], ref_frame=doc8)
save.table(t8, cfg, 'q3', 'tab_8_dominant_design_verdict', caption=@CAP@, source='human labelling · PatSeer (priority date; legal status at the snapshot, 2026-06-08)')
t8""", CAP=q(caption("Table", 8)))
md("""### 3.2 numbers

The in-force and all-aircraft shares of F by year, the largest archetype of the other three sets, the apparatus constants of the Method, the granted-and-live check, and the external comparison of the Answer: of the AAM Reality Index firms that disclose funding, the share of their aircraft in F weighted by funding (`frames.ari_f_funding`), against F's share of the whole corpus (Table 7 of chapter 2).""")
code(r"""fyi = fy.set_index('priority year')
words = {6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
rest = dy[dy['read'] & dy['base'].eq('in force') & ~dy['level id'].eq('family_b')]
levels = frames.archetype_levels_table(ds, v, cfg)
brief7 = frames.archetype_levels_brief(ds, v, levels).set_index('level id')
ext = frames.ari_f_funding(ds, v, cfg)
N2 = {'sm_dd_year_min': str(cfg.analysis['trend_min_n']), 'sm_dd_read_years': words[int(fy['read, in force'].sum())],
      'sm_fy_first': str(first_read), 'sm_fy_first_all': str(int(yrs[fy['read, all'].to_numpy()][0])),
      'sm_dd_max_rest': pct1(float(rest['its share'].max())),
      'sm_fy_fa_2020': pct1(fyi.loc[2020, 'F share']), 'sm_fy_fak_2020': str(int(fyi.loc[2020, 'F aircraft'])), 'sm_fy_na_2020': str(int(fyi.loc[2020, 'aircraft'])),
      'sm3_f_gl_2020': pct(fyi.loc[2020, 'F share, granted and live']), 'sm3_f_gl_2021': pct(fyi.loc[2021, 'F share, granted and live']),
      'sm_ext_f_weighted': pct(ext.iloc[-1]['funding-weighted F share']), 'sm_ext_f_corpus': pct(brief7.loc['family_b', 'its share']),
      'c4_fund_n': str(int((ext['kind'] == 'firm').sum()))}
for y in (2020, 2021, 2022, 2023):
    N2[f'sm_fy_fi_{y}'] = pct1(fyi.loc[y, 'F share in force'])
    N2[f'sm_fy_gl_{y}'] = pct(fyi.loc[y, 'in force with a granted patent'])
numbers_check(N2)""")
code(r"""# also quoted in the takeaways and the verdict of 3.2 (not in the document's number list): each against the figure the document prints
b = bal.set_index(['level', 'window']); q = form.set_index(['level', 'weighting', 'window'])
topshare = lambda lvl: float(dy[(dy['level id'] == lvl) & (dy['base'] == 'in force') & dy['read']]['its share'].max())
top3 = lambda sid: frames.archetype_key(v[v['window'] == '2020-23'], sid).value_counts(normalize=True).head(3).sum()
EXTRA = {
    'F 2D 2020-23': (f"{b.loc[('family_b', '2020-23'), 'D2']:.2f}", '3.22'), 'F band edge': (f"{b.loc[('family_b', '2020-23'), 'D2 permutation low']:.2f}", '3.65'),
    'C 2D 2020-23': (f"{b.loc[('A0', '2020-23'), 'D2']:.2f}", '4.53'), 'C band edge': (f"{b.loc[('A0', '2020-23'), 'D2 permutation low']:.2f}", '4.74'),
    'C·U 2D <=2011': (f"{b.loc[('A0c', '<= 2011'), 'D2']:.2f}", '10.60'), 'C·U edge <=2011': (f"{b.loc[('A0c', '<= 2011'), 'D2 permutation low']:.2f}", '11.80'),
    'C·U 2D 2012-15': (f"{b.loc[('A0c', '2012-15'), 'D2']:.2f}", '10.10'), 'C·U edge 2012-15': (f"{b.loc[('A0c', '2012-15'), 'D2 permutation low']:.2f}", '11.22'),
    'dQ main 2020-23': (f"{q.loc[('A0', 'subsystem', '2020-23'), 'ΔQ']:+.3f}".replace('-', '−'), '−0.047'),
    'dQ main edge': (f"{q.loc[('A0', 'subsystem', '2020-23'), 'ΔQ permutation low']:+.3f}".replace('-', '−'), '−0.027'),
    'dQ every field equal': (f"{q.loc[('A0', 'uniform', '2020-23'), 'ΔQ']:+.3f}".replace('-', '−'), '−0.029'),
    'dQ every field equal edge': (f"{q.loc[('A0', 'uniform', '2020-23'), 'ΔQ permutation low']:+.3f}".replace('-', '−'), '−0.027'),
    'max C in force': (pct1(topshare('A0')), '39.0 %'), 'max C·W·T in force': (pct1(topshare('A1t')), '27.1 %'), 'max C·U in force': (pct1(topshare('A0c')), '23.7 %'),
    'F in force 2021': (f"{int(fyi.loc[2021, 'F aircraft in force'])} of {int(fyi.loc[2021, 'aircraft in force'])}", '35 of 59'),
    'F in force 2020': (f"{int(fyi.loc[2020, 'F aircraft in force'])} of {int(fyi.loc[2020, 'aircraft in force'])}", '28 of 54'),
    'top three C·W·T 2020-23': (pct(top3('A1t')), '47 %'), 'top three C·U 2020-23': (pct(top3('A0c')), '26 %'),
    'F share 2022 in force': (pct1(fyi.loc[2022, 'F share in force']), '42.9 %'),
}
extra = pd.DataFrame([{'quoted': k, 'notebook': m, 'document': d, 'match': 'yes' if m == d else 'NO'} for k, (m, d) in EXTRA.items()])
assert (extra['match'] == 'yes').all(), extra[extra['match'] == 'NO']
extra""")

# ------------------------------------------------------------------------------------------ 3.3
md(question_and_method("3.3", "", ""))
md("""### The configurations inside each class

`frames.config_frame` reads, per aircraft, what the rules are written in: the tilting sets, the stations that tilt, what tilts (propulsors, a wing, both), where the fixed propulsor units sit, where the lift units sit, whether a unit stows in cruise. `frames.class_config_keys` writes each aircraft's configuration under the rule of its class (the proposed rules of the Method; the earlier rules, which carry the propulsor-unit band in every class, are kept for the robustness reading); `frames.class_configs_brief` and `frames.class_config_mix` count them per class and complete window. A window under 5 aircraft of the class is blank. The three tables are checked against the document (the class column prints the thesis names).""")
code(r"""cf = frames.config_frame(ds, v)
keys = frames.class_config_keys(ds, v, cf, COMPLETE)
DOCCLASS = {'SLC': 'Lift + Cruise', 'TR': 'Tilt Rotor', 'CVT': 'Combined vectored thrust', 'TW': 'Tilt Wing', 'MR': 'Multirotor'}   # the document's class column
cc = frames.class_configs_brief(keys, COMPLETE, FEW, DOCCLASS)
mix = frames.class_config_mix(keys, DOCCLASS)
verify(cc, 'la_class_configs_brief', key=['rule set', 'code', 'window'], doc_wording=False)
verify(mix, 'la_class_config_mix', key=['rule set', 'code', 'window', 'configuration'], doc_wording=False)
cc[cc['rule set'] == 'proposed'][['code', 'window', 'aircraft', 'possible configurations', 'distinct configurations', 'aircraft outside the rule', 'most common configuration', 'share in it']]""")
md("""### Figure 13 — how each class spreads over its own configurations

(i) The share of the class in its most common configuration, per complete window, with at the 2020-23 end the configurations observed of those the rule allows. (ii) The whole composition of Lift + Cruise, Tilt Propulsor and CVT: the configuration that leads in 2020-23 at the bottom, the others stacked above it by their size in 2020-23. The two early windows are drawn faded behind a line: they hold few aircraft.""")
code(r"""prop = cc[cc['rule set'] == 'proposed']
pmix = mix[mix['rule set'] == 'proposed']
share_cfg = prop.pivot(index='window', columns='code', values='share in it').reindex(COMPLETE)
poss = prop.set_index(['code', 'window'])
DISPLAY = {'SLC': lambda s: s.replace('lift units ', '', 1), 'CVT': lambda s: s.replace('rotors', 'propulsors').replace('fixed units ', 'fixed '),
           'TR': lambda s: s.replace('two or more tilting sets', '2+ tilting sets').replace('on two or more stations', 'in 2+ places').replace('on one station', 'in one place')}
CLASSES5 = ['SLC', 'TR', 'CVT', 'TW', 'MR']
fig = plt.figure(figsize=(W, 6.3), constrained_layout=True)
top, bot = fig.subfigures(2, 1, height_ratios=[1.0, 1.25])
ax = top.subplots()
plots.few_band(ax, 2)
plots.window_lines(ax, share_cfg[CLASSES5], n_few=2, ticks=[WSHORT[w] for w in COMPLETE])
ends = []
for c in CLASSES5:
    r = poss.loc[(c, '2020-23')]
    K = r['possible configurations']
    ends.append((float(r['share in it']), f"{style.cls(c).short} {100 * r['share in it']:.0f} % · {int(r['distinct configurations'])} of {int(K) if np.isfinite(K) else '–'}", style.cls(c).color))
order = sorted(range(len(ends)), key=lambda i: ends[i][0])
plots.end_labels(ax, len(COMPLETE) - 1, [ends[i][0] for i in order], [ends[i][1] for i in order], [ends[i][2] for i in order], gap=0.075)
ax.set_xlim(-0.5, len(COMPLETE) - 1 + 1.75); ax.set_ylim(0, 0.92)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0)); ax.grid(axis='y', color=style.GRID, linewidth=0.5); ax.set_axisbelow(True)
ax.set_ylabel('share of the class in its\nmost common configuration'); style.mark(ax, '(i)')
axs = bot.subplots(1, 3, sharey=True)
TITLE13 = {'SLC': 'Lift + Cruise: where the\nlift units sit', 'TR': 'Tilt Propulsor: how the\ntilting thrust is split', 'CVT': 'CVT: what tilts · where\nthe fixed units sit'}
for ax, c in zip(axs, ['SLC', 'TR', 'CVT']):
    m = pmix[pmix['code'] == c]
    lastw = m[m['window'] == '2020-23'].sort_values('aircraft', ascending=False)
    ordc = [k for k in lastw['configuration'] if not frames.cfg_outside(k)]
    keep = ordc[:3] if len(ordc) > 4 else ordc[:4]
    frac = lambda k: (m[m['configuration'].isin(k)].groupby('window')['aircraft'].sum().reindex(COMPLETE).fillna(0)
                      / m.groupby('window')['class aircraft'].first().reindex(COMPLETE))
    comp = pd.DataFrame({DISPLAY[c](k): frac([k]) for k in keep})
    rest = frac([k for k in m['configuration'].unique() if k not in keep])
    if rest.sum() > 0:
        comp['other configurations'] = rest                      # the gaps of the record and every configuration beyond the largest
    plots.config_stack(ax, comp, style.cls(c).color, n_few=2)
    nwin = m.groupby('window')['aircraft'].sum().reindex(COMPLETE)
    ax.set_xticks(range(len(COMPLETE)), [f"{WSHORT[w]}\nn {int(n)}" for w, n in zip(COMPLETE, nwin)])
    ax.set_title(TITLE13[c], fontsize=7.5, loc='left')
    ax.legend(loc='upper left', bbox_to_anchor=(-0.04, -0.2), fontsize=7, handlelength=1.1, labelspacing=0.3, frameon=False)
    if c == 'SLC':
        style.mark(ax, '(ii)', lines_up=2.3)
    else:
        ax.tick_params(labelleft=False)
plt.show()
fig13_data = pd.concat([prop.assign(panel='(i)'), pmix.assign(panel='(ii)')], ignore_index=True)
save.figure(fig, cfg, 'q3', 'fig_13_class_configurations', data=fig13_data,
            caption=@CAP@,
            source='human labelling (class; wing, boom and propulsor cards)',
            unit=f"unique aircraft of the class in the window, with a complete priority year; a window under {drivers.MIN_CELL} aircraft of the class is not drawn; the two early windows (faded) hold {int(n_win['<= 2011'])} and {int(n_win['2012-15'])} aircraft of all classes against {int(n_win['2016-19'])} and {int(n_win['2020-23'])}; the rules were chosen after the shares under earlier rules had been seen",
            read="(i) One line per class: the share of the class held by its most common configuration (the class's own rule, Method of 3.3); hollow markers and the grey band: windows with few aircraft. At the right end: the share in 2020-23 and how many of the possible configurations the class uses. (ii) The whole composition: each block is one configuration's share of the class in the window (in percent), the bottom block is the configuration that leads in 2020-23, blocks of 12 % or more print their share, and every configuration beyond the three or four largest of 2020-23 is pooled in grey. The number under each window is the class's aircraft there. Convergence is a change across windows under one rule, a share that rises toward the whole class; the level of a share is not compared between classes, because a rule with fewer possible configurations gives a larger leading share by construction.",
            panels={'(i)': 'share of each class in its most common configuration', '(ii)': 'composition of Lift + Cruise, Tilt Propulsor and CVT'})
plt.close(fig)""", CAP=q(caption("Figure", 13)))
md("""### 3.3 numbers""")
code(r"""MIX = lambda code, w, key: float(pmix[(pmix['code'] == code) & (pmix['window'] == w) & (pmix['configuration'] == key)]['share'].sum())
MIXN = lambda code, w, key: int(pmix[(pmix['code'] == code) & (pmix['window'] == w) & (pmix['configuration'] == key)]['aircraft'].sum())
TW_ = lambda c, w: poss.loc[(c, w)]
RB, RE = 'rotors tilt · fixed units on booms', 'rotors tilt · fixed units elsewhere'
ONE, TWO_ST = 'one tilting set', 'two or more tilting sets, on two or more stations'
N3 = {'sm3b_min_cell': str(drivers.MIN_CELL), 'sm3b_cc_gaps': str(int(prop['aircraft outside the rule'].sum())),
      'sm3b_cc_slc_23': pct(TW_('SLC', '2020-23')['share in it']),
      'sm3b_cc_tr_11_k': str(int(TW_('TR', '<= 2011')['distinct configurations'])), 'sm3b_cc_tr_11_n': str(int(TW_('TR', '<= 2011')['aircraft'])),
      'sm3b_cc_tr_11_cpa': f"{TW_('TR', '<= 2011')['configurations per aircraft']:.2f}",
      'sm3b_cc_tr_23_k': str(int(TW_('TR', '2020-23')['distinct configurations'])), 'sm3b_cc_tr_23_n': str(int(TW_('TR', '2020-23')['aircraft'])),
      'sm3b_cc_tr_23_cpa': f"{TW_('TR', '2020-23')['configurations per aircraft']:.2f}",
      'sm3b_mix_cvt_rb_23': pct(MIX('CVT', '2020-23', RB)), 'sm3b_mix_cvt_re_11': pct(MIX('CVT', '<= 2011', RE)),
      'sm3b_mix_cvt_re_15': pct(MIX('CVT', '2012-15', RE)), 'sm3b_mix_cvt_re_19': pct(MIX('CVT', '2016-19', RE)),
      'sm3b_mix_tr_one_11': pct(MIX('TR', '<= 2011', ONE)), 'sm3b_mix_tr_twost_23': pct(MIX('TR', '2020-23', TWO_ST)),
      'sm3b_win_11_n': str(int(n_win['<= 2011'])), 'sm3b_win_15_n': str(int(n_win['2012-15'])),
      'sm3b_win_19_n': str(int(n_win['2016-19'])), 'sm3b_win_23_n': str(int(n_win['2020-23']))}
numbers_check(N3)
cur = cc[cc['rule set'] == 'current'].set_index(['code', 'window'])['share in it']
print('also quoted in the takeaway: SLC leader (booms) shares', [pct(TW_('SLC', w)['share in it']) for w in COMPLETE], '; SLC configurations in use', int(TW_('SLC', '2020-23')['distinct configurations']),
      'of', int(TW_('SLC', '2020-23')['possible configurations']), '; CVT 1 and 0 aircraft on booms in the two early windows:', MIXN('CVT', '<= 2011', RB), MIXN('CVT', '2012-15', RB),
      '; TR one set 2020-23', pct(MIX('TR', '2020-23', ONE)), '; TR 2016-19 aircraft (one, two+ one place, two+ two places):', MIXN('TR', '2016-19', ONE),
      MIXN('TR', '2016-19', 'two or more tilting sets, on one station'), MIXN('TR', '2016-19', TWO_ST), '; TW', pct(TW_('TW', '2020-23')['share in it']), 'MR', pct(TW_('MR', '2020-23')['share in it']),
      '; earlier rules 2011 to 2020-23: L+C', pct(cur[('SLC', '<= 2011')]), 'to', pct(cur[('SLC', '2020-23')]), ', TP', pct(cur[('TR', '<= 2011')]), 'to', pct(cur[('TR', '2020-23')]),
      ', CVT', pct(cur[('CVT', '<= 2011')]), 'to', pct(cur[('CVT', '2020-23')]))""")

# ------------------------------------------------------------------------------------------ 3.4
md(question_and_method("3.4", "", ""))
md("""### The traces, per class and over the priority years

`frames.trace_frame` reads every labelled trace of an aircraft (tilting sets, propulsor units, propulsor types, units on booms, a ducted unit, …). `lib.drivers.trace_drift` gives the share or the median per class and window, `lib.drivers.trace_trends` the Spearman test of the trace against each aircraft's own priority year (every year up to 2023, 20 aircraft or more, p < 0.05), inside each class and, as a contrast only, pooled over the five classes. The classes read are those with 5 aircraft or more in at least three windows (`lib.drivers.class_selection`). The trends are checked against the document's `la_trace_trends`.""")
code(r"""tf = frames.trace_frame(ds, v)
classes = drivers.class_selection(v)                      # SLC, TR, CVT, TW, MR: largest first
drift = drivers.trace_drift(tf, classes, class_names=CLASS_NAMES)
trends = drivers.trace_trends(tf, drift, classes, class_names=CLASS_NAMES)
verify(trends, 'la_trace_trends', key=['trace', 'code'])
trend = lambda trace, code: trends[(trends['trace'] == trace) & (trends['code'] == code)].iloc[0]
trends[trends['code'].isin(['TR', 'CVT', 'ALL5']) & trends['trace'].isin(['tilting joint groups', 'propulsive units', 'units carried on booms'])][
    ['trace', 'code', 'aircraft', 'first window', 'first value', '2020-23 value', 'first mean', '2020-23 mean', 'rho', 'p', 'movement']]""")
md("""### The windowed centres, the two links and the sets per propulsor unit

`lib.drivers.driver_windows`: per class and complete window, the centre of each trace drawn (propulsor units as a median, tilting sets and propulsor types as a mean, shares as shares of the aircraft that answer; blank under 5 values). `lib.drivers.driver_links`: Tilt Propulsor's propulsor units by tilting sets, and CVT's ducted share inside each boom layout with its own trend test. `frames.sets_per_unit_brief`: tilting sets per aircraft and per propulsor unit. All three are checked against the document.""")
code(r"""dw = drivers.driver_windows(cf, CLASSES5, COMPLETE, FEW, class_names=CLASS_NAMES)
links = drivers.driver_links(cf)
spu = frames.sets_per_unit_brief(cf, COMPLETE, WSHORT)
verify(dw, 'la_driver_windows', key=['code', 'window'])
verify(links, 'la_driver_links', key=['link', 'group'])
verify(spu, 'la_sets_per_unit_brief', key=['code', 'measure'], doc_wording=False)
dw[['code', 'window', 'aircraft', 'tilting sets (mean)', 'propulsive units (median)', 'share with units on booms', 'share with a ducted unit']]""")
md("""### Figure 14 — the move of the tilting classes

(i) Each class's centre per window, mean tilting sets against median propulsor units, joined by arrows in time order (hollow, faint: windows with few aircraft). (ii) Tilt Propulsor: median propulsor units by the number of tilting sets. (iii) CVT: the share with propulsor units on booms. (iv) CVT: the share with a ducted propulsor unit inside each boom layout, labelled with the layout's aircraft over all CVT of the window. (v) Tilting sets per propulsor unit, mean, with its trend test.""")
code(r"""tw = lambda c: dw[dw['code'] == c].set_index('window').reindex(COMPLETE)
test_txt = lambda r: f"{r['movement']} (ρ {r['rho']:+.2f}, {ptxt(r['p'])})".replace('-', '−')
fig = plt.figure(figsize=(W, 7.4), constrained_layout=True)
top, bot = fig.subfigures(2, 1, height_ratios=[1.0, 0.95])
a1, a2 = top.subplots(1, 2, gridspec_kw={'width_ratios': [1.25, 1.0]})
# (i) the centres
cent = {c: pd.DataFrame({'x': tw(c)['tilting sets (mean)'], 'y': tw(c)['propulsive units (median)']}) for c in ('SLC', 'TR', 'CVT')}
pts = plots.centre_trajectory(a1, cent, n_few=2)
a1.set_xlim(-0.15, 2.15); a1.set_ylim(0, 10.6)
a1.set_xlabel('tilting sets per aircraft (mean)'); a1.set_ylabel('propulsor units per aircraft (median)')
a1.grid(color=style.GRID, linewidth=0.5); a1.set_axisbelow(True); style.mark(a1, '(i)')
leg = a1.legend(handles=[Line2D([], [], color=style.cls(c).color, marker=style.cls(c).marker, markersize=5, linewidth=1.3, label=f"{style.cls(c).short} {style.cls(c).name}") for c in ('SLC', 'TR', 'CVT')],
                loc='upper right', fontsize=7, frameon=True, framealpha=0.95, edgecolor='none', handlelength=1.6)
# (ii) Tilt Propulsor: units by tilting sets
lk = links[links['link'].str.startswith('Tilt Rotor')]
s = style.cls('TR')
a2.bar(range(len(lk)), lk['median'], width=0.6, color=s.color, hatch=s.hatch, edgecolor='white', linewidth=0.6, zorder=3)
for i, (m, n) in enumerate(zip(lk['median'], lk['aircraft'])):
    a2.text(i, m + 0.2, f"{m:g} units\nn = {int(n)}", ha='center', va='bottom', fontsize=7.5)
a2.set_xticks(range(len(lk)), list(lk['group'].astype(str))); a2.set_ylim(0, float(lk['median'].max()) + 2.6)
a2.set_xlabel('tilting sets on the aircraft'); a2.set_ylabel('propulsor units (median)')
a2.grid(axis='y', color=style.GRID, linewidth=0.5); a2.set_axisbelow(True); style.mark(a2, '(ii)')
# (iii)-(v)
b3, b4, b5 = bot.subplots(1, 3, gridspec_kw={'width_ratios': [1.25, 1.05, 1.05]})
x = np.arange(len(COMPLETE)); cv = tw('CVT'); sc = style.cls('CVT')
nb, nn = cv['aircraft, units on booms'].to_numpy(), cv['aircraft, no units on booms'].to_numpy()
pc = lambda a: a.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
plots.few_band(b3, 2); y3 = cv['share with units on booms'].to_numpy(dtype=float)
b3.plot(x, y3, color=sc.color, linestyle=sc.dash, linewidth=1.5, marker=sc.marker, markersize=4.6, zorder=3)
for xi in x:
    dip = 0 < xi < len(y3) - 1 and y3[xi] <= min(y3[xi - 1], y3[xi + 1])
    b3.annotate(f"{100 * y3[xi]:.0f} %", (xi, y3[xi]), textcoords='offset points', xytext=(0, -7 if dip else 6), ha='center', va='top' if dip else 'bottom', fontsize=7.5, color=style.INK)
b3.set_xticks(x, [f"{WSHORT[w]}\nn {int(a + b)}" for w, a, b in zip(COMPLETE, nb, nn)]); b3.set_ylim(0, 1.05); pc(b3)
b3.set_xlim(-0.5, len(x) - 0.5); b3.grid(axis='y', color=style.GRID, linewidth=0.5); b3.set_axisbelow(True); style.mark(b3, '(iii)', lines_up=2.3)
b3.set_title('CVT: share with\npropulsor units on booms', fontsize=7.5, loc='left')
plots.few_band(b4, 2)
lt = links[links['link'].str.startswith('CVT')].set_index('group')
for name, col, c, ns, txt in (('units on booms', 'ducted share, units on booms', sc.color, nb, 'on booms'), ('no units on booms', 'ducted share, no units on booms', style.MUTED, nn, 'no booms')):
    y = cv[col].to_numpy(dtype=float); ok = np.isfinite(y)
    b4.plot(x[ok], y[ok], color=c, linewidth=1.5, marker='o', markersize=4.4, zorder=3, label=f"(iv) {txt}: {test_txt(lt.loc[name])}")
    for xi in x[ok]:
        below = name.startswith('units')
        b4.annotate(f"{int(ns[xi])}/{int(nb[xi] + nn[xi])}", (xi, y[xi]), textcoords='offset points', xytext=(-5, 0) if below else (0, 6), ha='right' if below else 'center',
                    va='center' if below else 'bottom', fontsize=7, color=style.INK, bbox=dict(fc='white', ec='none', pad=0.6, alpha=0.85))
b4.set_xticks(x, [WSHORT[w] for w in COMPLETE]); b4.set_ylim(0, 1.05); b4.set_xlim(-0.5, len(x) - 0.5); pc(b4)
b4.grid(axis='y', color=style.GRID, linewidth=0.5); b4.set_axisbelow(True); style.mark(b4, '(iv)', lines_up=2.3)
b4.set_title('CVT: share with a ducted unit,\nin each boom layout', fontsize=7.5, loc='left')
plots.few_band(b5, 2)
su = spu[spu['measure'] == 'tilting sets per propulsive unit'].set_index('code')
for code, lbl in (('TR', 'Tilt Propulsor'), ('CVT', 'CVT'), ('ALL5', 'five classes pooled')):
    r = su.loc[code]; y = np.array([r[WSHORT[w]] for w in COMPLETE], dtype=float); ok = np.isfinite(y)
    if code == 'ALL5':
        kw = dict(color=style.MUTED, linestyle=':', marker='o')
    else:
        st_ = style.cls(code); kw = dict(color=st_.color, linestyle=st_.dash, marker=st_.marker)
    b5.plot(x[ok], y[ok], linewidth=1.4, markersize=4.6, zorder=3, label=f"(v) {lbl}: {test_txt(r)}", **kw)
b5.set_xticks(x, [WSHORT[w] for w in COMPLETE]); b5.set_ylim(0, 0.75); b5.set_xlim(-0.5, len(x) - 0.5)
b5.grid(axis='y', color=style.GRID, linewidth=0.5); b5.set_axisbelow(True); b5.set_ylabel('tilting sets per propulsor unit (mean)')
style.mark(b5, '(v)', lines_up=2.3)
b5.set_title('Tilting sets per\npropulsor unit', fontsize=7.5, loc='left')
hh, ll = b4.get_legend_handles_labels(); h5, l5 = b5.get_legend_handles_labels()
bot.legend(hh + h5, ll + l5, loc='outside lower center', ncol=2, fontsize=7, handlelength=2.0, columnspacing=1.2)
fig.canvas.draw()
rend = fig.canvas.get_renderer()
lab = [WSHORT[COMPLETE[k]] for _, _, k, _ in pts]
failed = plots.place_labels(a1, [p[0] for p in pts], [p[1] for p in pts], lab, [3.6] * len(pts), obstacles=[leg.get_window_extent(rend).expanded(1.03, 1.1)], fontsize=7)
assert not failed, failed
plt.show()
fig14_data = pd.concat([dw.assign(panel='(i), (iii), (iv)'), links.assign(panel='(ii), (iv)'), spu.assign(panel='(v)')], ignore_index=True)
save.figure(fig, cfg, 'q3', 'fig_14_tilting_classes_move', data=fig14_data,
            caption=@CAP@,
            source='human labelling (class; wing, boom and propulsor cards)',
            unit=f"unique aircraft of the class in the window (5 or more), complete priority years; (ii) the {int(lk['aircraft'].sum())} Tilt Propulsor aircraft with a unit count, all years; (v) aircraft of the class with a unit count; trend tests on every year up to 2023",
            read="(i) Each point is a class's centre in one window (hollow and faint: windows with few aircraft); arrows join the windows in time order; right means more tilting sets per aircraft, up more propulsor units. (ii) Bar: the median propulsor units of the Tilt Propulsor aircraft with one, two, and three or more tilting sets; above it its aircraft. (iii) Share of CVT aircraft that carry propulsor units on booms. (iv) Share of CVT with a ducted propulsor unit, one line for the aircraft with propulsor units on booms and one for those without, each with its Spearman trend against the priority year (every year to 2023); a point is labelled with the layout's aircraft over all CVT of the window, and a share is drawn only when the layout holds 5 aircraft or more of that window. (v) Tilting sets per propulsor unit, mean per window, with the trend test of each line.",
            panels={'(i)': "each class's centre per window", '(ii)': 'Tilt Propulsor: propulsor units by tilting sets', '(iii)': 'CVT: share with units on booms',
                    '(iv)': 'CVT: ducted share inside each boom layout', '(v)': 'tilting sets per propulsor unit'})
plt.close(fig)""", CAP=q(caption("Figure", 14)))
md("""### Figure 15 — two traces per class and window

(i) The share of each class's aircraft that carry propulsor units on booms; (ii) the share with a ducted propulsor unit. A point needs 5 aircraft of the class in the window.""")
code(r"""fig, axs = plt.subplots(1, 2, figsize=(W, 3.3), constrained_layout=True, sharey=True)
for ax, col, mk in zip(axs, ('share with units on booms', 'share with a ducted unit'), ('(i)', '(ii)')):
    plots.few_band(ax, 2)
    fr = dw.pivot(index='window', columns='code', values=col).reindex(COMPLETE)[CLASSES5]
    plots.window_lines(ax, fr, n_few=2, ticks=[WSHORT[w] for w in COMPLETE])
    ax.set_xlim(-0.5, len(COMPLETE) - 0.5); ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.grid(axis='y', color=style.GRID, linewidth=0.5); ax.set_axisbelow(True); style.mark(ax, mk, lines_up=1.2)
axs[0].set_title('Share with propulsor units on booms', fontsize=8, loc='left', pad=4); axs[1].set_title('Share with a ducted propulsor unit', fontsize=8, loc='left', pad=4)
fig.legend(handles=[Line2D([], [], color=style.cls(c).color, linestyle=style.cls(c).dash, marker=style.cls(c).marker, markersize=4.6, linewidth=1.4,
                           label=f"{style.cls(c).short} {style.cls(c).name}") for c in CLASSES5], loc='outside lower center', ncol=3, fontsize=7.5, handlelength=2.2)
plt.show()
save.figure(fig, cfg, 'q3', 'fig_15_boom_duct_traces', data=dw[['class', 'code', 'window', 'aircraft', 'share with units on booms', 'share with a ducted unit']],
            caption=@CAP@,
            source='human labelling (class; propulsor cards: the places carrying propulsor units, the ducted flag)',
            unit='unique aircraft of the class in the window (5 or more); the two early windows (faded) hold few aircraft',
            read='One line per class, in the class\'s colour, dash and marker; hollow markers and the grey band: windows with few aircraft (63 and 58 aircraft of all classes against 213 and 237 in the two after). (i) The share of the class\'s aircraft that carry propulsor units on booms. (ii) The share with at least one ducted propulsor unit. A window with fewer than 5 aircraft of the class is not drawn.',
            panels={'(i)': 'share of aircraft with propulsor units on booms', '(ii)': 'share of aircraft with a ducted propulsor unit'})
plt.close(fig)""", CAP=q(caption("Figure", 15)))

md("""### Table 9 — the traces that move, and the drivers they go with and against

`lib.drivers.driver_verdicts` codes, per trace, the direction it moved (a class that rises or falls counts; the pooled row counts; mixed when classes move both ways) and the verdict from the drivers that predict it (`lib.drivers.driver_verdict`: a fixed physical driver, A2, never makes a trace rise or fall). The table prints the traces that move in at least one class or pooled: where each moved (every year to 2023), the drivers it goes with (it moved the way they predict) and against, and what it means. The raw verdicts are checked against the document's `la_driver_verdicts`, the printed table against the document's Table 9 as printed.""")
code(r"""verd = drivers.driver_verdicts(trends)
CODE_TEXT = {'does_not_move': 'trace does not move', 'mixed_by_class': 'mixed by class', 'fixed_only': 'moves, but only fixed physical drivers predict this trace',
             'opposed': 'opposed drivers', 'single': 'single driver', 'against_all': 'moved against every driver that predicts a direction',
             'overdetermined': 'overdetermined', 'not_labelled': 'not labelled'}
raw_verdicts = pd.DataFrame({'trace': [t['label'] + ('' if t['kind'] == 'share' else ' (median)') for t in drivers.TRACES] + [u[0] for u in drivers.UNLABELLED_TRACES],
                             'driver kind': verd['driver kind'], 'verdict class': verd['verdict'].map(CODE_TEXT)})
verify(raw_verdicts, 'la_driver_verdicts', key=['trace'], columns=['trace', 'driver kind', 'verdict class'], doc_wording=False)""")
code(r"""CLASS_WORD = {'SLC': 'Lift + Cruise', 'TR': 'Tilt Propulsor', 'CVT': 'CVT', 'TW': 'Tilt Wing', 'MR': 'Multirotor'}
TRACE_WORD = {'joints': 'tilting sets per aircraft', 'fus_moves': 'a body that tilts or rotates', 'units': 'propulsor units per aircraft',
              'on_booms': 'propulsor units carried on booms', 'stations': 'places carrying propulsor units per aircraft', 'booms': 'booms present',
              'pusher': 'a pusher unit', 'two_wings': 'two or more wing panels', 'tailless': 'no tail surface', 'gear_drawn': 'landing gear drawn',
              'n_types': 'propulsor types per aircraft'}
READ_HERE = {'joints', 'units', 'on_booms', 'ducted', 'n_types'}                      # the traces 3.4 reads: marked ●
READING = {'opposed': 'drivers disagree; it moved with those under *goes with*', 'overdetermined': '{n} drivers predict it; the labelled dataset cannot say which acts',
           'single': 'one driver predicts it, and it moved that way', 'against_all': 'moved against the only direction any driver predicts',
           'fixed_only': 'no driver predicts a direction; only physical limits bear on it', 'mixed_by_class': 'classes move in opposite directions; no driver reading'}
READING_EXTRA = {'joints': '; per propulsor unit it falls (trajectory figure, v)', 'ducted': '; in CVT it follows the boom layout (trajectory figure, iv)',
                 'n_types': '; in Tilt Propulsor the added type is a second tilting set'}
dname = lambda c: drivers.DRIVERS[c][1].replace('rotor control', 'propulsor control')
rows = []
for tr, vr in zip(drivers.TRACES, verd.iloc[:len(drivers.TRACES)].itertuples()):
    t = trends[trends['trace'] == tr['label']].set_index('code')
    moved = [c for c in classes if t.loc[c, 'movement'] in ('rises', 'falls')]
    if not moved and t.loc['ALL5', 'movement'] not in ('rises', 'falls'):
        continue                                                       # the trace does not move anywhere: not printed
    parts = [f"{t.loc[c, 'movement']} in {CLASS_WORD[c]} (ρ {t.loc[c, 'rho']:+.2f}, {ptxt(t.loc[c, 'p'])})" for c in moved]
    where = ('; '.join(parts) if parts else 'no trend detected in any class') + f"; pooled: {t.loc['ALL5', 'movement']}"
    inside = {t.loc[c, 'movement'] for c in moved}
    d = '+' if inside == {'rises'} else '-' if inside == {'falls'} else 'mixed'          # inside the classes only; a pooled move alone is 'mixed'
    with_, against = [], []
    for code_, sign in tr['drivers'].items():
        if sign in '+-' and d != 'mixed':
            (with_ if sign == d else against).append(f"{dname(code_)} ({'more' if sign == '+' else 'fewer'})")
    meaning = READING[vr.verdict].format(n=len(tr['drivers'])) + READING_EXTRA.get(tr['key'], '')
    if vr.verdict == 'fixed_only':
        meaning += ' (' + ', '.join(dname(c) for c in tr['drivers']) + ')'
    rows.append({'trace': ('● ' if tr['key'] in READ_HERE else '') + TRACE_WORD.get(tr['key'], tr['label']), 'where it moved (every year to 2023)': where,
                 'goes with (driver: what it predicts)': '; '.join(with_) or '—', 'goes against (driver: what it predicts)': '; '.join(against) or '—',
                 'what it means': meaning})
t9 = pd.DataFrame(rows)
doc9 = checks.brief_table(cfg, 9)
verify(t9, None, 'Table 9 as printed in the document', doc_wording=False, key=['trace'], ref_frame=doc9)
save.table(t9, cfg, 'q3', 'tab_9_driver_verdicts', caption=@CAP@, source='human labelling (class; wing, boom and propulsor cards) · Spearman rank correlation against the priority year, every year to 2023')
t9""", CAP=q(caption("Table", 9)))
md("""### 3.4 numbers""")
code(r"""fw = lambda r: f"{r:.1f}"
words5 = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}
from fractions import Fraction
def frac_words(x, long=False):
    f = Fraction(x).limit_denominator(5)
    a, b = words5.get(f.numerator, str(f.numerator)), words5.get(f.denominator, str(f.denominator))
    return f"{a} tilting {'set' if f.numerator == 1 else 'sets'} for every {b} propulsor units" if long else f"{a} for every {b}"
pt = lambda p: '< 0.001' if p < 0.001 else f"{p:.3f}" if p < 0.01 else f"{p:.2f}"
jt, jall = trend('tilting joint groups', 'TR'), trend('tilting joint groups', 'ALL5')
onb_cvt, onb_slc = trend('units carried on booms', 'CVT'), trend('units carried on booms', 'SLC')
duc_cvt, duc_slc = trend('a ducted unit', 'CVT'), trend('a ducted unit', 'SLC')
sp = spu.set_index(['code', 'measure'])
sp_unit = lambda c, w: float(sp.loc[(c, 'tilting sets per propulsive unit'), WSHORT[w]])
dwi = dw.set_index(['code', 'window'])
span = f"{pct(duc_cvt['first value'])} to {pct(duc_cvt['2020-23 value'])}"
below = f", to below Lift + Cruise's {pct(duc_slc['2020-23 value'])}"
duct_answer = (f"CVT also sheds its ducts ({span}){below}." if duc_cvt['movement'] == 'falls' else
               f"CVT's share with a ducted unit also drops ({span}){below}, though as a year trend this is not detected (p {pt(duc_cvt['p'])}).")
N4 = {'sm3b_trend_min': str(cfg.analysis['trend_min_n']),
      'sm3b_dw_cvt_11_n': str(int(dwi.loc[('CVT', '<= 2011'), 'aircraft'])), 'sm3b_dw_cvt_11_nb': str(int(dwi.loc[('CVT', '<= 2011'), 'aircraft, units on booms'])),
      'sm3b_dw_cvt_23_n': str(int(dwi.loc[('CVT', '2020-23'), 'aircraft'])), 'sm3b_dw_cvt_23_nb': str(int(dwi.loc[('CVT', '2020-23'), 'aircraft, units on booms'])),
      'sm3b_dw_tr_11_units': f"{dwi.loc[('TR', '<= 2011'), 'propulsive units (median)']:g}", 'sm3b_dw_tr_23_units': f"{dwi.loc[('TR', '2020-23'), 'propulsive units (median)']:g}",
      'sm3b_t_onb_cvt_first': pct(onb_cvt['first value']), 'sm3b_t_onb_cvt_last': pct(onb_cvt['2020-23 value']), 'sm3b_t_onb_cvt_p': pt(onb_cvt['p']),
      'sm3b_t_onb_slc_last': pct(onb_slc['2020-23 value']),
      'sm3b_spu_tr_unit_11': f"{sp_unit('TR', '<= 2011'):.2f}", 'sm3b_spu_tr_unit_23': f"{sp_unit('TR', '2020-23'):.2f}",
      'sm3b_spu_tr_unit_11_frac_long': frac_words(sp_unit('TR', '<= 2011'), long=True), 'sm3b_spu_tr_unit_23_frac': frac_words(sp_unit('TR', '2020-23')),
      'sm3b_duct_answer': duct_answer,
      'sm_t_joints_tr_first': fw(jt['first mean']), 'sm_t_joints_tr_last': fw(jt['2020-23 mean']), 'sm_t_joints_tr_p': pval3(jt['p']),
      'sm_t_joints_all_first': fw(jall['first mean']), 'sm_t_joints_all_last': fw(jall['2020-23 mean']), 'sm_t_joints_all_p': pval3(jall['p'])}
# the document prints the old names in this one sentence-valued number (the display rename of 2026-09-28 came after): compare in its words
N4 = {k: (checks.doc_wording(v_) if k == 'sm3b_duct_answer' else v_) for k, v_ in N4.items()}
numbers_check(N4)""")
code(r"""# also quoted in the takeaways of 3.4 (not in the document's number list): each against the figure the document prints
tc = lambda code, w, col: dwi.loc[(code, w), col]
tt_ = lambda trace, code: trend(trace, code)
moving_inside = sum(1 for tr in drivers.TRACES if any(trend(tr['label'], c)['movement'] in ('rises', 'falls') for c in classes))
EXTRA4 = {
    'TR sets 11 / 23': (f"{fw(tc('TR', '<= 2011', 'tilting sets (mean)'))} / {fw(tc('TR', '2020-23', 'tilting sets (mean)'))}", '1.4 / 1.8'),
    'CVT sets 11 / 23 and units': (f"{fw(tc('CVT', '<= 2011', 'tilting sets (mean)'))} / {fw(tc('CVT', '2020-23', 'tilting sets (mean)'))}; {tc('CVT', '<= 2011', 'propulsive units (median)'):g} / {tc('CVT', '2020-23', 'propulsive units (median)'):g}", '1.0 / 1.4; 4 / 6'),
    'units rho TR, CVT': (f"{tt_('propulsive units', 'TR')['rho']:+.2f} / {tt_('propulsive units', 'CVT')['rho']:+.2f}", '+0.41 / +0.31'),
    'units p TR, CVT': (f"{ptxt(tt_('propulsive units', 'TR')['p'])} / {ptxt(tt_('propulsive units', 'CVT')['p'])}", 'p < 0.001 / p 0.002'),
    'sets rho TR, CVT': (f"{tt_('tilting joint groups', 'TR')['rho']:+.2f} / {tt_('tilting joint groups', 'CVT')['rho']:+.2f}", '+0.22 / +0.25'),
    'TR median units by sets': (' / '.join(f"{m:g}" for m in lk['median']), '2 / 4 / 6'),
    'TR two or more sets 2020-23, any fixed unit': (f"{pct(tc('TR', '2020-23', 'share with two or more tilting sets'))} / {pct(tc('TR', '2020-23', 'share with a fixed unit'))}", '67 % / 2 %'),
    'CVT no booms ducted 2016-19, 2020-23': (f"{pct(tc('CVT', '2016-19', 'ducted share, no units on booms'))} / {pct(tc('CVT', '2020-23', 'ducted share, no units on booms'))}", '64 % / 75 %'),
    'CVT booms ducted 2016-19, 2020-23': (f"{pct(tc('CVT', '2016-19', 'ducted share, units on booms'))} / {pct1(tc('CVT', '2020-23', 'ducted share, units on booms'))}", '35 % / 6.1 %'),
    'CVT booms ducted trend': (f"{lt.loc['units on booms', 'rho']:+.2f}, {ptxt(lt.loc['units on booms', 'p'])}", '-0.31, p 0.02'),
    'CVT no booms trend': (f"{lt.loc['no units on booms', 'movement']}", 'flat'),
    'CVT duct 80 to 32, rho p': (f"{pct(duc_cvt['first value'])} to {pct(duc_cvt['2020-23 value'])}; {duc_cvt['rho']:+.2f}, {ptxt(duc_cvt['p'])}", '80 % to 32 %; -0.20, p 0.05'),
    'TR sets per aircraft rho p': (f"{sp.loc[('TR', 'tilting sets per aircraft'), 'rho']:+.2f}, {ptxt(sp.loc[('TR', 'tilting sets per aircraft'), 'p'])}", '+0.22, p 0.01'),
    'TR per unit rho p': (f"{sp.loc[('TR', 'tilting sets per propulsive unit'), 'rho']:+.2f}, {ptxt(sp.loc[('TR', 'tilting sets per propulsive unit'), 'p'])}", '-0.32, p < 0.001'),
    'CVT per unit p': (ptxt(sp.loc[('CVT', 'tilting sets per propulsive unit'), 'p']), 'p 0.41'),
    'wing panels trend': (', '.join(trend('two or more wing panels', c)['movement'] for c in classes), 'flat, flat, flat, flat, flat'),
    'booms rise TW, MR, SLC, TR': (f"{pct(trend('units carried on booms', 'TW')['2020-23 value'])}; {pct(trend('units carried on booms', 'MR')['first value'])} to {pct(trend('units carried on booms', 'MR')['2020-23 value'])}, {ptxt(trend('units carried on booms', 'MR')['p'])}", '26 %; 11 % to 60 %, p 0.05'),
    'traces that move inside a class': (str(moving_inside), '8'),
}
extra4 = pd.DataFrame([{'quoted': k, 'notebook': m, 'document': d, 'match': 'yes' if checks._norm(m) == checks._norm(d) else 'NO'} for k, (m, d) in EXTRA4.items()])
extra4""")

# ------------------------------------------------------------------------------------------ overview
md("""## Overview: what matched

Every number the document quotes for chapter 3 (78) and every table, with the differences labelled.""")
code(r"""allnum = pd.concat(NUMBERS, ignore_index=True)
n_doc = len(checks.reference_numbers('3'))
missing = checks.missing_numbers(dict.fromkeys(allnum['name']), '3')
print(f"numbers: {int((allnum['match'] == 'yes').sum())} of {len(allnum)} match the document; "
      f"{int(allnum['match'].str.startswith('expected').sum())} expected differences; {int((allnum['match'] == 'NO').sum())} failures; "
      f"{len(missing)} of the document's {n_doc} not computed here: {missing}")
overview = pd.DataFrame([c.iloc[0].to_dict() for c in CHECKS])
overview""")
code(r"""assert (allnum['match'] != 'NO').all(), allnum[allnum['match'] == 'NO']
assert not missing
assert (overview['differences'] == 0).all(), overview[overview['differences'] > 0]
assert (extra['match'] == 'yes').all()""")


nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, OUT)
print("written", OUT, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(OUT)], check=True, cwd=str(OUT.parent))
