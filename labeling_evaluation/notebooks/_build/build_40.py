"""Generate notebooks/40_q1_growth_protection_fidelity.ipynb (and execute it with --run).

    python3 notebooks/_build/build_40.py          # write the notebook
    python3 notebooks/_build/build_40.py --run    # write, then jupyter nbconvert --execute --inplace

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
OUT = PILLAR / "notebooks" / "40_q1_growth_protection_fidelity.ipynb"
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


# ------------------------------------------------------------------------------------------ section 0 (kept)
md("""# 40 — Question 1: growth, protection and fidelity

How fast has eVTOL patenting grown, how much of it is still protected, and do the patented aircraft stand for the aircraft the sector builds?

Sub-questions 1.1, 1.2, 1.3 of the Labelling Analysis (2026-09-30). Every path comes from `labelling_analysis.yaml`; equations come from `lib/`, figures and tables from `viz/`.

This notebook reproduces every figure, table and number of chapter 1 of the 45-page document, and compares them with it (`viz.checks`). The one difference expected is the class fold of 2026-10-01 (Stopped/Slowed Rotor Wing folds into Lift + Cruise, no longer into Electric Rotorcraft); it only touches the five-class views and is labelled where it shows.

Outputs are written to `<output>/q1_growth_protection_fidelity/` (figures: pdf, png, csv, json; tables: csv, json). Regenerate this notebook with `python3 notebooks/_build/build_40.py`.""")
md("""## 0. Setup: paths and the analysis unit

The table lists every input this notebook can read, whether it exists and when it last changed. The load raises if a required input is missing.""")
code("""import sys, pathlib
PILLAR = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(PILLAR))
import pandas as pd
pd.set_option('display.max_colwidth', 120)
from viz import config, data
cfg = config.load()
config.show(cfg)[['group', 'key', 'exists', 'modified', 'size', 'path']]""")
md("""The analysis unit is the representative primary aircraft: wizard-approved, passes the domain gate (no UAV/not-electric/STOL-only tag), one row per aircraft. Counts below must match the document.""")
code("""ds = data.load_dataset(cfg)
pd.Series(ds.counts, name='count').to_frame()""")
md("""### Tools used below

`frames.base` is the per-aircraft analysis frame (627 rows); `lib` holds every equation; `viz.checks` compares with the document. `verify` runs one table check and keeps its summary for the final overview; `numbers_check` does the same for the quoted numbers.""")
code("""import inspect
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from viz import frames, style, plots, save, checks
from lib import growth, association, intervals, drivers, dominant_design

style.apply(cfg)
v = frames.base(ds, cfg)                                   # one row per unique aircraft, folded as in the yaml
WIN = frames.windows_from_config(cfg)
WIN_NAMES = [n for n, _, _ in WIN]
SEED = cfg.analysis['random_seed']
thin = lambda n: f"{int(n):,}".replace(',', ' ')           # 1 639, as the document prints thousands
pct = lambda x: f"{x:.0%}".replace('%', ' %')              # 0.53 -> '53 %'
pval = lambda p: '< 0.001' if p < 0.001 else f"{p:.3f}"
CHECKS, NUMBERS = [], []                                   # summaries kept for the overview at the end

def verify(frame, ref, name=None, **kw):
    r = checks.table(frame, ref, cfg, name=name, **kw)
    CHECKS.append(r)
    display(r.T.rename(columns={0: name or ref}))
    d = checks.detail(r)
    if len(d):
        display(d)

def numbers_check(values, expected=None):
    r = checks.numbers(values, '1', expected)
    NUMBERS.append(r)
    display(r)""")

md("""### 0.1 The numbers of the Method common to every chapter

Unit of analysis, time, the publication lag, how much of 2023 the snapshot already sees, and the apparatus of the statistics box (seed, permutations, rarefaction size). The two worked examples of the statistics box (the tilting classes' propulsor units, CVT's tilting sets) come from the design traces of chapter 3: the trace frame is built in `frames.trace_frame`, the drift and the Spearman trends by `lib.drivers`.""")
code("""lag = frames.publication_lag(ds, by='region').set_index('region').loc[frames.REGIONS]   # median and 90th percentile, three regions
vis = frames.visible_at_snapshot(ds, v, 2023)                                         # share of each region's 2023 aircraft the snapshot sees
pd.concat([lag, vis.rename('visible 2023')], axis=1)""")
code("""tf = frames.trace_frame(ds, v)
classes = drivers.class_selection(v)
drift = drivers.trace_drift(tf, classes)
trends = drivers.trace_trends(tf, drift, classes)
def trend(trace, code_):
    return trends[(trends['trace'] == trace) & (trends['code'] == code_)].iloc[0]
tr, mr, cvt = trend('propulsive units', 'TR'), trend('propulsive units', 'MR'), trend('tilting joint groups', 'CVT')
trends[trends['code'].isin(['TR', 'MR', 'CVT']) & trends['trace'].isin(['propulsive units', 'tilting joint groups'])][
    ['trace', 'code', 'aircraft', 'first window', 'first value', '2020-23 value', 'first mean', '2020-23 mean', 'rho', 'p', 'movement']]""")
code("""complete = v[~v['window'].str.contains('partial')]
N0 = {
    'acquired_s': thin(ds.counts['patents_acquired']), 'representative_s': thin(ds.counts['patents_approved']),
    'observations_s': thin(ds.counts['approved_variants']), 'unique_s': thin(len(v)),
    'snapshot': frames.snapshot_date(ds), 'partial_start': str(cfg.analysis['partial_window_start']),
    'lag_median_lo': str(int(lag['median lag'].min())), 'lag_median_hi': str(int(lag['median lag'].max())),
    'lag_p90': str(int(lag['90th percentile'].max())),
    'sm_vis2023_lo': pct(vis.min()), 'sm_vis2023_hi': pct(vis.max()),
    'sm_perm_n': str(cfg.analysis['rarefy_n']), 'sm_perm_seed': str(SEED),
    'sm_perms': str(inspect.signature(dominant_design.balance_band).parameters['perms'].default),
    'sm_win_min_n': str(int(complete['window'].value_counts().min())),
    'sm_t_units_tr_first': f"{tr['first value']:.1f}", 'sm_t_units_tr_last': f"{tr['2020-23 value']:.1f}", 'sm_t_units_tr_p': pval(tr['p']),
    'sm_t_units_mr_first': f"{mr['first value']:.1f}", 'sm_t_units_mr_last': f"{mr['2020-23 value']:.1f}",
    'sm_t_units_mr_n': str(int(mr['aircraft'])), 'sm_t_units_mr_p': pval(mr['p']), 'sm_t_units_mr_p100': str(round(mr['p'] * 100)),
    'sm_t_joints_cvt_first': f"{cvt['first mean']:.1f}", 'sm_t_joints_cvt_last': f"{cvt['2020-23 mean']:.1f}",
    'sm_t_joints_cvt_med_first': f"{cvt['first value']:.1f}", 'sm_t_joints_cvt_med_last': f"{cvt['2020-23 value']:.1f}",
}
numbers_check(N0)""")

# ------------------------------------------------------------------------------------------ 1.1
md(question_and_method("1.1", "", ""))
md("""### 1.1.1 Filings per priority year

Per priority year: unique aircraft by applicant region, the patents acquired and the representative patents, whether the year is complete (the snapshot lies at least the 90th-percentile publication lag after its end: `lib.growth.lag_quantile`, `year_is_complete`), and the aeronautics baseline (CPC B64, PatSeer worldwide families) with the ratios built from it. Checked against the document's table.""")
code("""fpy = frames.filings_per_year(ds, v, cfg)
verify(fpy.reset_index(), 'la_filings_per_year', key=['priority year'])
fpy""")
md("""### 1.1.2 How fast each series grows

Each series is counted per priority year: the eVTOL architecture patents (the representative patents, one PatSeer family each), the unique aircraft, and three worldwide baselines (aeronautics CPC B64, all of CPC section B, all patents: WIPO). `log(count) = a + b·t` is fitted over 2005-2023 and the doubling time is ln 2 / b (`lib.growth.loglinear_fit`). The ratio of two doubling times has its interval from a bootstrap over years, 2 000 draws, seed 42 (`lib.growth.growth_ratio_table`).""")
code("""ser = frames.growth_series(ds, v, cfg)
SHAPE = {'exponential': 'exponential', 'bends_up': 'bends up — doubling time is a window average',
         'bends_down': 'bends down — doubling time is a window average'}
NAMES = dict(frames.GROWTH_SERIES)
rows = []
for lo, hi in (growth.FIT_WINDOW, growth.FIT_SENSITIVITY[0]):
    for key, name in frames.GROWTH_SERIES:
        yrs, cnt = growth.window_frame(ser[key], lo, hi)
        fit = growth.loglinear_fit(yrs, cnt)
        rows.append({'series': name, 'key': key, 'window': f"{lo}–{hi}", 'total': int(cnt.sum()),
                     'doubling time (years)': round(fit['doubling time (years)'], 1),
                     '95 % interval': f"{fit['doubling low']:.1f} to {fit['doubling high']:.1f}",
                     'growth per year': f"{fit['growth per year %']:.0f} %",
                     'shape': SHAPE[growth.curvature_shape(fit)], 'primary': (lo, hi) == growth.FIT_WINDOW})
rates = pd.DataFrame(rows)
verify(rates, 'la_growth_rates', key=['key', 'window'])
rates""")
code("""r = growth.growth_ratio_table(ser, ['evtol_families', 'evtol_aircraft'], ['b64', 'secb', 'all'])
ratios = pd.DataFrame({'eVTOL counted as': r['eVTOL counted as'].map(NAMES), 'against': r['against'].map(NAMES),
                       'window': r['window'], 'times as fast': r['times as fast'],
                       '95 % interval': [f"{a:.2f} to {b:.2f}" for a, b in zip(r['low'], r['high'])],
                       'reading': r['reading'], 'primary': r['primary']})
verify(ratios, 'la_growth_ratios', key=['eVTOL counted as', 'against', 'window'])
ratios""")
md("""### 1.1.3 The turning point

For every candidate year from 2009 to 2020, log(count) is fitted with one line before it and a second line (own level and slope) from it; the candidate with the smallest squared error is the turning point. Its firmness is the share of 2 000 residual resamples (seed 42) that choose the same year (`lib.growth.turning_point`). Run on 2006-2023, because the 2005 bar pools 1999-2005. One generator is shared by the three series, in this order.""")
code("""d = fpy.loc[2006:2023]
rng = np.random.default_rng(SEED)
TP = {name: growth.turning_point(d.index.to_numpy(float), np.log(d[col].to_numpy(float)), rng)
      for name, col in [('representative patents', 'patents representative'), ('unique aircraft', 'unique aircraft'),
                        ('aircraft per 1 000 B64', 'aircraft per 1 000 B64')]}
pd.DataFrame(TP).T""")
md("""### Figure 1 — filings per priority year, and how fast each series grows

(i) unique aircraft by priority year and applicant region (the years 1999-2005 pooled in one bar), the representative patents as a line, the dated sector events under the bars; a year still filling is faded with a dashed outline and carries its bar total. (ii) each series relative to its own 2005-09 mean on a log axis, with its fitted line over 2005-2023. The panel marks name the graphs; source, unit and how to read go to the caption file.""")
code("""regs = frames.REGIONS + ['Other regions']
t = fpy.loc[2005:, regs + ['patents representative', 'complete']].copy()
t.loc[2005, regs + ['patents representative']] = fpy.loc[:2005, regs + ['patents representative']].sum()   # 1999-2005 pooled in one bar
incomplete = list(t.index[~t['complete'].astype(bool)])
events = frames.sector_events(cfg, fpy.attrs['snapshot'])
fits = {k: growth.loglinear_fit(*growth.window_frame(ser[k], 2005, 2023)) for k in ser}
n_rep = int(t['patents representative'].sum())
years = list(t.index)""")
code("""W, _ = style.size(cfg, 'full')
fig, (ax, strip, ax2) = plt.subplots(3, 1, figsize=(W, 8.0), gridspec_kw=dict(height_ratios=[2.3, 1.75, 2.5]), constrained_layout=True)
plots.region_stack(ax, t[regs], line=t['patents representative'], line_label=f"representative patents ({thin(n_rep)})",
                   incomplete=incomplete, pooled_first='1999-2005 pooled')
ax.set_xticks([]); ax.set_ylabel('unique aircraft (bars)\\nrepresentative patents (line)')
first_inc = years.index(incomplete[0])
ax.axvline(first_inc - 0.5, color=style.INK, linewidth=0.8, linestyle='--')
ax.text(first_inc - 0.4, ax.get_ylim()[1] * 0.99, 'incomplete years', va='top', fontsize=7, color=style.MUTED,
        bbox=dict(fc='white', ec='none', pad=0.5))
ax.legend(loc='upper left'); style.mark(ax, '(i)')
plots.event_strip(strip, events, years, parent=ax)
strip.set_xlim(ax.get_xlim())
strip.set_xticks(range(len(years)), [('≤2005' if y == 2005 else str(y)) for y in years], rotation=90)
shown = ['evtol_families', 'b64', 'secb', 'all']                    # the aircraft series is fitted but not drawn
plots.growth_fits(ax2, {k: ser[k] for k in shown}, fits, NAMES, 2005, 2023)
ax2.set_xticks(range(2005, 2024, 2))
ax2.legend(loc='lower left', bbox_to_anchor=(0, 1.0)); style.mark(ax2, '(ii)', lines_up=4.7)
plt.show()""")
code("""fig1_data = t.join(pd.DataFrame({NAMES[k]: ser[k] for k in shown}).loc[2005:2023], how='left')
save.figure(fig, cfg, 'q1', 'fig_01_filings_per_year', data=fig1_data,
            caption=@CAP@,
            source='PatSeer (snapshot 2026-06-08) · human labelling · sector events: the author\\'s dated list (checked 2026-09-23) · baselines: PatSeer worldwide simple families for CPC B64 and CPC section B, WIPO patent families by origin (indicator 6a) for all patents, exported 2026-09-25',
            unit='(i) unique aircraft and representative patents per priority year; (ii) patent families per priority year, each relative to its own 2005-09 mean',
            read='(i) Bars: unique aircraft by the priority year of their first patent, stacked by applicant region; the first bar holds 1999-2005. A year is faded with a dashed outline while the snapshot is less than the 90th-percentile publication lag (3 years) after its end: it will still grow, and its bar total is printed on it. Line: the representative patents. Strip: dated sector events; an event stands on its calendar year. (ii) Equal slopes are equal growth rates; points are yearly counts, lines are least-squares fits of log count on year over 2005-2023.',
            panels={'(i)': 'filings per priority year by region', '(ii)': 'growth of each series, log axis'})
plt.close(fig)""", CAP=q(caption("Figure", 1)))

md("""### Figure 2 — the class mix against the evtol.news directory

The 12 classes are folded to the five of the directory with the fold of the yaml (`analysis.class_fold`); the directory is counted by development year. Both sources use the same windows (the partial window is not drawn). The fold of the document sent Stopped/Slowed Rotor Wing to Electric Rotorcraft; the ruling of 2026-10-01 sends it to Lift + Cruise. `v_doc` re-folds with the document's own rule, to prove the table reproduces the document, and `changed_cells` then marks the cells the ruling moved.""")
code("""def class_mix(frame):
    L = frames.evtolnews_long(frame, cfg, WIN)
    names = {'patent': 'patent corpus (unique aircraft, priority year)', 'directory': 'evtol.news directory (aircraft, development year)'}
    rows = []
    for src in ('patent', 'directory'):
        for w in WIN_NAMES:
            sw = L[(L['source'] == src) & (L['window'] == w)]
            for c in frames.CLASS5_ORDER:
                k = int((sw['class5'] == c).sum())
                rows.append({'source': names[src], 'window': w, 'class': frames.CLASS5_NAMES[c], 'code': c, 'aircraft': k,
                             'window total': len(sw), 'share': round(k / len(sw), 3) if len(sw) else np.nan})
    return pd.DataFrame(rows)

mix = class_mix(v)                                                        # current fold: SRW -> LC
v_doc = frames.base(ds, cfg, fold={**cfg.analysis['class_fold'], 'SRW': 'ER'})   # the document's fold
mix_doc = class_mix(v_doc)
KEY = ['source', 'window', 'code']
verify(mix_doc, 'la_evtolnews_check', 'la_evtolnews_check, document fold, SRW to ER', key=KEY)                            # the document's own fold reproduces the document
verify(mix, 'la_evtolnews_check', 'la_evtolnews_check, current fold (SRW to LC)', key=KEY, expected=checks.changed_cells(mix, mix_doc, KEY))""")
code("""spec = {'LC': ('SLC', 'L+C'), 'VT': ('TR', 'VT'), 'WM': ('MR', 'WM'), 'ER': ('RC', 'ER'), 'HB': ('HB', 'HB')}
W5 = [w for w in WIN_NAMES if 'partial' not in w]
LABEL = {'<= 2011': '≤2011', '2012-15': '2012–15', '2016-19': '2016–19', '2020-23': '2020–23'}
fig, axes = plt.subplots(1, 2, figsize=(W, 2.9), sharey=True, constrained_layout=True)
for ax, (src, mark) in zip(axes, [('patent corpus (unique aircraft, priority year)', '(i)'), ('evtol.news directory (aircraft, development year)', '(ii)')]):
    s = mix[(mix['source'] == src) & mix['window'].isin(W5)]
    share = s.pivot(index='window', columns='code', values='share').reindex(index=W5, columns=frames.CLASS5_ORDER)
    total = s.groupby('window')['window total'].first().reindex(W5)
    plots.folded_bars(ax, share.rename(index=LABEL), spec, totals=[int(x) for x in total])
    style.mark(ax, mark)
axes[0].set_ylabel("share of the window's aircraft")
handles = axes[0].get_legend_handles_labels()[0]
fig.legend(handles, [f"{spec[c][1]}  {frames.CLASS5_NAMES[c]}" for c in frames.CLASS5_ORDER], loc='outside lower center', ncol=3,
           handlelength=1.2, columnspacing=1.0)
plt.show()""")
code("""fig2_data = mix[mix['window'].isin(W5)]
n_p = int(fig2_data[(fig2_data['source'].str.startswith('patent')) & (fig2_data['code'] == 'LC')]['window total'].sum())
n_d = int(fig2_data[(fig2_data['source'].str.startswith('evtol')) & (fig2_data['code'] == 'LC')]['window total'].sum())
save.figure(fig, cfg, 'q1', 'fig_02_evtolnews_check', data=fig2_data,
            caption=@CAP@,
            source='PatSeer · human labelling, folded to the five classes of the directory (analysis.class_fold) · evtol.news directory (Vertical Flight Society), crawled 2026-09-17, development year read by two readers',
            unit=f"unique aircraft by priority-year window (i), directory aircraft by development-year window (ii); the aircraft under each bar are printed with its window: {thin(n_p)} aircraft with a class in (i), {thin(n_d)} dated aircraft in (ii) of 1 229 listed",
            read='Each bar is 100 % of one window; segments print their share in percent (segments under 8 % carry no number). The class fold: L+C = Lift + Cruise (with Stopped/Slowed Rotor Wing since 2026-10-01), VT = every tilting class (Tilt Propulsor, CVT, Tilt Wing, Tilt Body, Pitch-to-Cruise) and Deflected Slipstream, WM = Multirotor, ER = Rotorcraft, HB = Hoverbike and Personal Flying Vehicle. The partial window 2024-26 is not drawn.',
            panels={'(i)': 'labelled dataset, priority-year windows', '(ii)': 'evtol.news directory, development-year windows'})
plt.close(fig)""", CAP=q(caption("Figure", 2)))

md("""### Table 1 and Figure 3 — the patent clock against the market clock

For the index firms of the AAM Reality Index (May 2026 release) that file in this corpus: first, peak and last priority year of the firm's unique aircraft, and the first flight and the entry into service the index states (the earliest year printed where a firm lists several vehicles). The gaps count from the firm's first patent IN THIS CORPUS, so they are floors: a firm that flew before it appears here prints a negative gap.""")
code("""tl = frames.ari_timeline(v, cfg)
verify(tl, 'la_ari_timeline', key=['company'])
tab1 = tl[['company', 'first patent', 'first flight (ARI)', 'entry into service (ARI)', 'years to first flight', 'years to entry into service']]
tab1 = tab1.astype(object).where(tab1.notna(), '')
for c in ['first flight (ARI)', 'entry into service (ARI)', 'years to first flight', 'years to entry into service']:
    tab1[c] = tab1[c].map(lambda x: f"{x:.0f}" if x != '' else '')
save.table(tab1, cfg, 'q1', 'tab_1_ari_timeline', caption=@CAP@,
           source='AAM Reality Index (May 2026 release: first_flight and eis fields, kept verbatim) · PatSeer · human labelling')
tab1""", CAP=q(caption("Table", 1)))
code("""fig, ax = plt.subplots(figsize=(W, 3.9), constrained_layout=True)
plots.clock_rows(ax, tl, today=2026.45, planned_after=frames.ARI_RELEASE_YEAR - 1)
ax.set_xlim(2012, 2031)
ax.text(2026.5, len(tl) - 0.7, 'mid-2026', fontsize=7, color=style.MUTED)
plots.clock_legend(fig, loc='outside lower center', ncol=3)
plt.show()
save.figure(fig, cfg, 'q1', 'fig_03_ari_clock', data=tl,
            caption=@CAP@,
            source='AAM Reality Index (May 2026 release; first_flight and eis as the index prints them) · PatSeer · human labelling',
            unit='the index firms that file here (13), one row each; priority years and index years; the number after a firm is its unique aircraft in this corpus',
            read='Each row is one firm: the bar runs from its first to its last priority year in this corpus, the tick marks the year it filed most. Squares: the first flight the index reports; triangles: entry into service. An open marker is a plan (a year after the index release of 2026). Nothing here is a flight record: both market dates are the index\\'s own statements, and the gap from first patent to first flight is a floor.')
plt.close(fig)""", CAP=q(caption("Figure", 3)))

md("""### 1.1.4 External comparison: investment and market forecasts

Disclosed funding and published market forecasts, collected for scale only (`assets/external/investment`). Funding trackers differ in scope (VFS counts eVTOL companies, McKinsey future air mobility), and the forecasts are commercial revenue projections: the comparison is by eye, never a test.""")
code("""fund = pd.read_csv(cfg.path('sector_funding')).set_index('period')['funding_usd_bn']
fc = pd.read_csv(cfg.path('market_forecasts'))
fc[['publisher', 'value_2034_usd_bn', 'cagr_pct']]""")
md("""### 1.1 numbers

Every number the document's text quotes for 1.1, written as the document prints it. The first flight is a flight only if the index dates it no later than its own release (2026); a later date is a plan and is not counted.""")
code("""flown = tl[tl['first flight (ARI)'] <= frames.ARI_RELEASE_YEAR]
gap = flown['years to first flight']
lead = gap[gap > 0].median()
y18 = int(fpy.loc[2018, 'unique aircraft'])
ge = lambda a, w: ratios[(ratios['eVTOL counted as'] == 'eVTOL architecture patents') & (ratios['against'] == a) & (ratios['window'] == w)].iloc[0]
dbl = lambda key: rates[(rates['key'] == key) & (rates['primary'])].iloc[0]['doubling time (years)']
main, sens = ge('aeronautics (CPC B64)', '2005–2023'), ge('aeronautics (CPC B64)', '2005–2019')
N1 = {
    'tk_y2018': str(y18), 'sm_pat_2018': str(int(fpy.loc[2018, 'patents representative'])),
    'sm_turn_draws': thin(growth.TURNING_DRAWS),
    'sm_turn_pat_year': str(TP['representative patents']['break']), 'sm_turn_pat_x': f"{TP['representative patents']['jump']:.1f}",
    'sm_turn_pat_boot': pct(TP['representative patents']['share']),
    'sm_turn_pat_prev': str(int(fpy.loc[TP['representative patents']['break'] - 1, 'patents representative'])),
    'sm_turn_pat_prev_year': str(TP['representative patents']['break'] - 1),
    'sm_turn_pat_after': str(int(fpy.loc[TP['representative patents']['break'], 'patents representative'])),
    'sm_turn_ac_year': str(TP['unique aircraft']['break']), 'sm_turn_ac_x': f"{TP['unique aircraft']['jump']:.1f}",
    'sm_turn_ac_lo': str(TP['unique aircraft']['lo']), 'sm_turn_ac_hi': str(TP['unique aircraft']['hi']),
    'sm_turn_sh_lo': str(TP['aircraft per 1 000 B64']['lo']), 'sm_turn_sh_hi': str(TP['aircraft per 1 000 B64']['hi']),
    'sm_g_fam_dbl': f"{dbl('evtol_families'):.1f}", 'sm_g_b64_dbl': f"{dbl('b64'):.1f}",
    'sm_g_secb_dbl': f"{dbl('secb'):.1f}", 'sm_g_all_dbl': f"{dbl('all'):.1f}",
    'sm_gr_fam_b64': f"{main['times as fast']:.2f}", 'sm_gr_fam_b64_ci': main['95 % interval'],
    'sm_gr_fam_all': f"{ge('all patents', '2005–2023')['times as fast']:.2f}",
    'sm_gr_fam_b64_19': f"{sens['times as fast']:.2f}", 'sm_gr_fam_b64_19_ci': sens['95 % interval'],
    'sm_gr_fam_b64_19_va': 'the edge still holds' if sens['reading'] == 'faster' else
                           'it can no longer be told from equal pace' if sens['reading'] == 'cannot be told apart' else 'eVTOL is slower',
    'sm_ff_flown': str(len(flown)), 'sm_ff_before': str(int((gap > 0).sum())), 'sm_ff_lead': f"{lead:.0f}",
    'sm_ff_visible': f"{lead - int(N0['lag_p90']):.0f}", 'tk_ari_timeline_n': str(len(tl)),
    'sm_ext_fund_1020': f"{fund['2010-2020']:.1f}", 'sm_ext_fund_2021': f"{fund['2021']:.1f}", 'sm_ext_fund_2023': f"{fund['2023']:.1f}",
    'sm_ext_fc_n': str(len(fc)), 'sm_ext_fc_min': f"{fc['value_2034_usd_bn'].min():.1f}", 'sm_ext_fc_max': f"{fc['value_2034_usd_bn'].max():.1f}",
    'sm_ext_fc_cagr_min': f"{fc['cagr_pct'].min():.1f}", 'sm_ext_fc_cagr_max': f"{fc['cagr_pct'].max():.1f}",
}
numbers_check(N1)""")

# ------------------------------------------------------------------------------------------ 1.2
md(question_and_method("1.2", "", ""))
md("""### 1.2.1 The seven-year rule, measured

97.7 % of the dated grants arrive within seven years of priority, and the share of families still pending collapses at the rule's boundary. Read from the author's checks of the PatSeer export (`assets/external/lapse_check`).""")
code("""lagsum = pd.read_csv(cfg.path('grant_lag'), index_col=0)['value']
status = pd.read_csv(cfg.path('grant_status_by_year'))
rows = [('dated grants in the corpus', f"{int(lagsum['with_grant_date']):d}"),
        ('median priority-to-grant lag (years)', f"{lagsum['median_lag_years']:.1f}"),
        ('90th percentile lag (years)', f"{lagsum['p90_lag_years']:.1f}"),
        ('grants arriving within 7 years of priority', f"{lagsum['pct_granted_within_7y']:.1f} %")]
for y in range(2019, 2024):
    rows.append((f'families still pending, {y} cohort', f"{float(status.loc[status['priority_year'] == y, 'pending_pct'].iloc[0]):.1f} %"))
span = status[status['priority_year'].between(2020, 2023)]
rows.append(('families still pending, 2020-23 cohort', f"{100 * span['pending'].sum() / span['n'].sum():.1f} %"))
lapse = pd.DataFrame(rows, columns=['measure', 'value'])
verify(lapse, 'la_lapse_check', key=['measure'])
lapse""")
md("""### 1.2.2 Aircraft with no patent in force

An aircraft is out of force only when EVERY patent linked to it reads INACTIVE at the snapshot: its own primary patent and every duplicate that points at it (`frames.force_frame`). Priority year 2019 or earlier, aircraft with a class. A class with ten or more aircraft enters the chi-square test of class against out of force (`lib.association.chi2_test`); the same test is repeated counting a patent that names several aircraft for its first aircraft only.""")
code("""w = frames.force_frame(ds, v)                                     # priority <= 2019; out = no linked patent in force
g = w.groupby('topType').agg(**{'unique aircraft': ('aircraft_id', 'size'), 'out of force': ('out', 'sum'), '_old': ('lapsed', 'mean')})
g['out of force share'] = (g['out of force'] / g['unique aircraft']).round(2)
g['out of force, primary patent only'] = g['_old'].round(2)
g['class'] = [style.cls(c).name for c in g.index]
force = g.sort_values(['unique aircraft', 'class'], ascending=[False, True]).reset_index().rename(columns={'topType': 'code'})
force = force[['class', 'code', 'unique aircraft', 'out of force', 'out of force share', 'out of force, primary patent only']]
tot = pd.DataFrame([{'class': 'all classes', 'code': 'ALL', 'unique aircraft': len(w), 'out of force': int(w['out'].sum()),
                     'out of force share': round(float(w['out'].mean()), 2),
                     'out of force, primary patent only': round(float(w['lapsed'].mean()), 2)}])
force = pd.concat([force, tot], ignore_index=True)
RENAME = {'Tilt Rotor': 'Tilt Propulsor'}
verify(force.drop(columns='code'), 'la_force_aircraft', key=['class'], rename=RENAME)
force""")
code("""w_first = frames.force_frame(ds, v, first_only=True).set_index('aircraft_id')['out']
w['out_first'] = w['aircraft_id'].map(w_first).astype(bool)               # a multi-target duplicate linked to its first target only
tested = force.loc[force['unique aircraft'] >= frames.FORCE_TEST_MIN, 'code']
big = w[w['topType'].isin(tested)]
def class_test(frame, col):
    table = pd.crosstab(frame['topType'], frame[col])
    return association.chi2_test(table.values)['p'], int(table.shape[0])
p_all, k_tested = class_test(big, 'out')
p_first, _ = class_test(big, 'out_first')
pd.DataFrame({'reading': ['every linked patent INACTIVE', 'multi-target duplicates to the first target only'],
              'classes tested': k_tested, 'p': [p_all, p_first]})""")
md("""### 1.2.3 Does the class difference survive the filing office?

Two checks on the difference between classes: without the largest filer (Bell / Textron) and within the US office alone; then the office split itself (the US against the rest, with WO and CN singled out), and what the patents at each office are.""")
code("""meta = v.drop_duplicates('aircraft_id').set_index('aircraft_id')[['firm', 'pub_office', 'legal_status_raw']]
wo = w.join(meta, on='aircraft_id')
wo['status'] = wo['legal_status_raw'].fillna('').astype(str)
def class_p(x):
    big_ = x[x['topType'].isin(x['topType'].value_counts()[lambda s: s >= frames.FORCE_TEST_MIN].index)]
    p, k = class_test(big_, 'out')
    return p, len(big_), k
rows = []
for reading, x in [('all aircraft', wo), ('without Bell / Textron', wo[~wo['firm'].astype(str).str.contains('Bell')]),
                   ('US office only', wo[wo['pub_office'] == 'US'])]:
    p, n_, k = class_p(x)
    rows.append({'reading': reading, 'aircraft': n_, 'classes tested': k, 'out of force share': round(float(x['out'].mean()), 2), 'class p': round(p, 3)})
for reading, x in [('filed at the US office', wo[wo['pub_office'] == 'US']), ('filed elsewhere', wo[wo['pub_office'] != 'US']),
                   ('filed as WO (international)', wo[wo['pub_office'] == 'WO']), ('filed at CN', wo[wo['pub_office'] == 'CN'])]:
    rows.append({'reading': reading, 'aircraft': len(x), 'classes tested': None, 'out of force share': round(float(x['out'].mean()), 2), 'class p': None})
mr = wo[wo['topType'] == 'MR']
rows.append({'reading': 'Multirotor, multi-target duplicates to first target only', 'aircraft': len(mr), 'classes tested': None,
             'out of force share': round(float(mr['out_first'].mean()), 2), 'class p': None})
for reading, x, hit in [('WO, expired', wo[wo['pub_office'] == 'WO'], lambda s: s.eq('INACTIVE - EXPIRED')),
                        ('CN, withdrawn or refused', wo[wo['pub_office'] == 'CN'], lambda s: s.str.contains('WITHDRAWN|REFUSED')),
                        ('US, granted and in force', wo[wo['pub_office'] == 'US'], lambda s: s.eq('ACTIVE - GRANTED'))]:
    rows.append({'reading': reading, 'aircraft': len(x), 'classes tested': None, 'out of force share': int(hit(x['status']).sum()), 'class p': None})
office = pd.DataFrame(rows)
verify(office, 'la_force_office_check', key=['reading'])
office""")
md("""### Figure 4 — aircraft with no patent in force, per class

One bar per class with ten or more aircraft (colour and hatch of the class), the share out of force with its n; the dash is the earlier reading (the first patent alone); the dashed line is all classes.""")
code("""fd = force[(force['unique aircraft'] >= frames.FORCE_TEST_MIN) & (force['code'] != 'ALL')]
fig, ax = plt.subplots(figsize=(W, 2.9), constrained_layout=True)
plots.class_value_bars(ax, list(fd['code']), fd['out of force share'].tolist(), fd['unique aircraft'].astype(int).tolist(),
                       marks=fd['out of force, primary patent only'].tolist(), mark_label='first patent alone (earlier reading)',
                       overall=float(w['out'].mean()), overall_label=f"all classes\\n{w['out'].mean():.0%} of {len(w)}")
ax.set_ylabel("share of the class's aircraft\\nout of force"); ax.set_ylim(0, 0.8)
ax.legend(loc='upper right')
plt.show()""")
code("""save.figure(fig, cfg, 'q1', 'fig_04_force_aircraft', data=fd,
            caption=@CAP@,
            source='PatSeer legal status at the snapshot (2026-06-08) · human labelling (class, duplicates)',
            unit=f"unique aircraft with priority year 2019 or earlier, classes of {frames.FORCE_TEST_MIN} or more ({len(fd)} classes, {int(fd['unique aircraft'].sum())} of {len(w)} aircraft); share of the class",
            read=f"An aircraft is out of force only when none of its patents is in force. Bar: share of the class's aircraft out of force (n under the class); black dash across a bar: the share when only the aircraft's first patent is read; dashed line: all classes. Class against out of force over the {k_tested} classes drawn: chi-square p = {p_all:.3f}; counting a patent that names several aircraft for its first aircraft only: p = {p_first:.3f}.")
plt.close(fig)""", CAP=q(caption("Figure", 4)))
md("""### 1.2 numbers""")
code("""fa = lambda c: force.loc[force['class'] == c, 'out of force share'].iloc[0]
of = lambda r, c='out of force share': office.loc[office['reading'] == r, c].iloc[0]
lp = lambda m: lapse.loc[lapse['measure'] == m, 'value'].iloc[0]
N2 = {
    'sm_fa_share': pct(fa('all classes')), 'sm_fa_cvt': pct(fa('Combined Vectored Thrust')), 'sm_fa_slc': pct(fa('Lift + Cruise')),
    'sm_fa_tr': pct(fa('Tilt Propulsor')), 'sm_fa_mr': pct(fa('Multirotor')),
    'sm_fa_mr_first': pct(of('Multirotor, multi-target duplicates to first target only')),
    'sm_fa_p': f"{p_all:.3f}", 'sm_fa_p_sens': f"{p_first:.3f}",
    'sm_fo_us': pct(of('filed at the US office')), 'sm_fo_else': pct(of('filed elsewhere')),
    'sm_fo_wo': pct(of('filed as WO (international)')), 'sm_fo_cn': pct(of('filed at CN')),
    'sm_fo_p_us': f"{of('US office only', 'class p'):.2f}",
    'sm_fo_why_wo_n': str(int(of('WO, expired', 'aircraft'))),
    'sm_fo_why_cn_k': str(int(of('CN, withdrawn or refused'))), 'sm_fo_why_cn_n': str(int(of('CN, withdrawn or refused', 'aircraft'))),
    'sm_fo_why_us_k': str(int(of('US, granted and in force'))), 'sm_fo_why_us_n': str(int(of('US, granted and in force', 'aircraft'))),
    'sm_lapse_grants': lp('dated grants in the corpus'), 'sm_lapse_7y': lp('grants arriving within 7 years of priority'),
    'sm_lapse_p2020': lp('families still pending, 2020 cohort'), 'sm_lapse_p2023': lp('families still pending, 2023 cohort'),
    'sm_lapse_p2020_23': lp('families still pending, 2020-23 cohort'),
}
numbers_check(N2)""")

# ------------------------------------------------------------------------------------------ 1.3
md(question_and_method("1.3", "", ""))
md("""### 1.3.1 Names, and what a name buys

An aircraft carries a real product name when the labeller recognised it (`name_is_real`), else a name generated for this study. Only an aircraft with a real name can be matched to a public product, and the class comparison is run on the aircraft with a public counterpart (`frames.public_arch_frame`: the TRL table's `arch_match`, split by the whole-patent reading `arch_gt`).""")
code("""pub = frames.public_arch_frame(ds)
named = v['name_is_real'].fillna(False).astype(bool)
linked = frames.linked_aircraft_ids(v, cfg)
compared = set(pub['aircraft_id'])
def name_row(label, mask, why):
    return {'aircraft': label, 'unique aircraft': int(mask.sum()), 'share of the analysis set': round(float(mask.mean()), 3),
            'linked to an evtol.news page': int(v.loc[mask, 'aircraft_id'].isin(linked).sum()),
            'compared with the public aircraft': int(v.loc[mask, 'aircraft_id'].isin(compared).sum()),
            'filed by a named organisation': int(v.loc[mask, 'named'].sum()), 'why': why}
coverage = pd.DataFrame([name_row('carry a real product name', named, 'the labeller recognised the aircraft and NAME_DECISIONS.csv records the product name'),
                         name_row('carry a generated identifier', ~named, 'no public product was recognised behind the drawing, so no match could be attempted'),
                         name_row('all unique aircraft', named | ~named, '')])
verify(coverage, 'la_name_coverage', key=['aircraft'])
coverage""")
md("""### Figure 5 — unique aircraft by name and public match""")
code("""cr = coverage.set_index('aircraft')
real, gen = cr.loc['carry a real product name'], cr.loc['carry a generated identifier']
m_ = [int(real['compared with the public aircraft']), int(gen['compared with the public aircraft'])]
u_ = [int(real['unique aircraft']) - m_[0], int(gen['unique aircraft']) - m_[1]]
fig, ax = plt.subplots(figsize=(W, 1.9), constrained_layout=True)
plots.split_hbars(ax, [f"Real product name ({int(real['unique aircraft'])})", f"Generated identifier ({int(gen['unique aircraft'])})"],
                  m_, u_, 'matched to a public product', 'not matched')
ax.set_xlabel('unique aircraft'); ax.legend(loc='upper right')
plt.show()
save.figure(fig, cfg, 'q1', 'fig_05_name_coverage', data=coverage.drop(columns='why'),
            caption=@CAP@,
            source='human labelling (aircraft names, NAME_DECISIONS) · evtol.news (public aircraft)',
            unit='unique aircraft (627), no time axis, counts',
            read='One bar per kind of name: a real product name recognised by the labeller, or a generated identifier. Within a bar, the dark hatched segment is the aircraft matched to a public product and compared with it, the light segment the rest. Only a named aircraft could be matched at all.')
plt.close(fig)""", CAP=q(caption("Figure", 5)))
md("""### Table 2 — three sources of a class compared two at a time

The drawing label (wizard), the patent text (whole-patent reading) and the public aircraft (evtol.news), compared on the aircraft that have a public counterpart. Each agreement share has its 95 % Wilson interval with the finite-population correction N = 627 (`lib.intervals.wilson_fpc_interval`), because 97 aircraft are a sample of the 627.""")
code("""m = pub['match'].astype(str)
gt = pub['arch_gt'].fillna('').astype(str)
has_gt = gt.ne('')
agree = {'drawing label against the public aircraft': (int(m.isin(['yes', 'taxonomy']).sum()), len(pub)),
         'patent text against the public aircraft': (int(m.isin(['yes', 'taxonomy', 'image']).sum()), len(pub)),
         'drawing label against the patent text': (int((gt.eq(pub['topType'].astype(str)) & has_gt).sum()), int(has_gt.sum()))}
WHY = ['the patent describes another configuration than the one the firm built, or the drawing was misread',
       'the patent describes another configuration than the one the firm built',
       'the drawing was read as one class and the text states another']
rows = []
for (name, (k, n)), why in zip(agree.items(), WHY):
    lo, hi = intervals.wilson_fpc_interval(k, n, len(v))
    rows.append({'comparison': 'architecture class: ' + name, 'agree': k, 'of': n, 'share': round(k / n, 2),
                 '95 % interval': f"{lo:.2f}–{hi:.2f}", 'the disagreements': why})
pairwise = pd.DataFrame(rows)
PW = {'architecture class: ' + k: k for k in agree}
verify(pairwise, 'la_public_pairwise', key=['comparison'], rename=PW)
save.table(pairwise, cfg, 'q1', 'tab_2_public_pairwise', caption=@CAP@,
           source='human labelling (drawing label) · whole-patent reading · evtol.news (public aircraft, matched by name)')
pairwise""", CAP=q(caption("Table", 2)))
md("""### Table 3 — NASA TRL per class

TRL per aircraft from the TRL table (assessed from public evidence by a language model, not yet checked by hand); an aircraft no public source follows is TRL 2 by construction. Bands: 2 / 3-5 / 6-7 / 8-9.""")
code("""t = frames.trl_frame(ds)
t['class'] = t['topType'].map(lambda c: style.cls(c).name if pd.notna(c) else 'no type')
bands = [b for b, _ in frames.TRL_BANDS]
trl = pd.crosstab(t['class'], t['band']).reindex(columns=bands, fill_value=0)
trl = trl.loc[trl.sum(axis=1).sort_values(ascending=False, kind='stable').index]
trl.insert(0, 'unique aircraft', trl.sum(axis=1))
trl['above TRL 2'] = trl['unique aircraft'] - trl['TRL 2']
trl.loc['Total'] = trl.sum()
trl['share above TRL 2'] = (trl['above TRL 2'] / trl['unique aircraft']).round(2)
trl = trl.reset_index().rename(columns={'index': 'class', 'band': 'class'}); trl.columns.name = None
verify(trl, 'a2_d15_trl_by_class', key=['class'], rename=RENAME)
save.table(trl, cfg, 'q1', 'tab_3_trl_by_class', caption=@CAP@,
           source='NASA TRL per aircraft (inputs/trl/aircraft_trl.csv; evtol.news, evtolindex.org, company statements) · human labelling')
trl""", CAP=q(caption("Table", 3)))
md("""### Tables 4 and 5 — do the aircraft above TRL 2, and those of the index firms, stand for the corpus?

The subset against the rest on six attributes, one at a time: chi-square for a category (class folded to five, region, priority window, filer type), Mann-Whitney for a number (priority year, propulsor units); both from `lib.association` through `frames.representativeness`. The folded class changes under the ruling of 2026-10-01, so the rows of the folded class (and the p and the largest gap that rest on it) are the cells expected to differ; `*_doc` re-folds with the document's own rule to prove the rest.""")
code("""tid = frames.trl_frame(ds)[['aircraft_id', 'trl']]
wt = v.merge(tid, on='aircraft_id', how='left')
above = pd.to_numeric(wt['trl'], errors='coerce').fillna(2).gt(2)
rep_trl = frames.representativeness(wt, above, 'above TRL 2', WIN_NAMES)
firms = set(frames.ari_firms(v, cfg)['company'])
rep_ari = frames.representativeness(v.copy(), v['company_canonical'].isin(firms), 'index firms', WIN_NAMES)
# the same two tables under the document's fold
wt_doc = v_doc.merge(tid, on='aircraft_id', how='left')
rep_trl_doc = frames.representativeness(wt_doc, pd.to_numeric(wt_doc['trl'], errors='coerce').fillna(2).gt(2), 'above TRL 2', WIN_NAMES)
rep_ari_doc = frames.representativeness(v_doc.copy(), v_doc['company_canonical'].isin(firms), 'index firms', WIN_NAMES)
KEY = ['attribute', 'level']
verify(rep_trl_doc, 'la_trl_representativeness', 'la_trl_representativeness, document fold', key=KEY)
verify(rep_trl, 'la_trl_representativeness', 'la_trl_representativeness, current fold', key=KEY, expected=checks.changed_cells(rep_trl, rep_trl_doc, KEY))
verify(rep_ari_doc, 'la_ari_representativeness', 'la_ari_representativeness, document fold', key=KEY)
verify(rep_ari, 'la_ari_representativeness', 'la_ari_representativeness, current fold', key=KEY, expected=checks.changed_cells(rep_ari, rep_ari_doc, KEY))""")
code("""VERDICT = {'matches the rest': 'no difference detected', 'does NOT match the rest': 'differs'}
def printed(rep, label):
    s = rep[rep['test'] != ''].copy()
    return pd.DataFrame({'attribute': s['attribute'], f'n {label}': s[f'n {label}'].astype(int), 'n rest': s['n rest'].astype(int),
                         'largest gap': s['largest gap'], 'test': s['test'],
                         'p': s['p'].map(lambda p: '< 0.001' if p < 0.001 else f"{p:.2f}"), 'verdict': s['verdict'].map(VERDICT)}).reset_index(drop=True)
tab4, tab5 = printed(rep_trl, 'above TRL 2'), printed(rep_ari, 'index firms')
save.table(tab4, cfg, 'q1', 'tab_4_trl_representativeness', caption=@CAP4@,
           source='NASA TRL (inputs/trl/aircraft_trl.csv) · human labelling · PatSeer')
save.table(rep_trl, cfg, 'q1', 'tab_4_trl_representativeness_levels', caption='Table 4, every level of every attribute: the share of the 63 aircraft above TRL 2 and of the rest.',
           source='NASA TRL (inputs/trl/aircraft_trl.csv) · human labelling · PatSeer')
save.table(tab5, cfg, 'q1', 'tab_5_ari_representativeness', caption=@CAP5@,
           source='AAM Reality Index · human labelling · PatSeer')
save.table(rep_ari, cfg, 'q1', 'tab_5_ari_representativeness_levels', caption='Table 5, every level of every attribute: the share of the 147 aircraft of the index firms and of the rest.',
           source='AAM Reality Index · human labelling · PatSeer')
display(tab4); display(tab5)""", CAP4=q(caption("Table", 4)), CAP5=q(caption("Table", 5)))
# ------------------------------------------------------------------------------------------ 1.3.5 (new 2026-10-02)
md("""### 1.3.5 The labelled dataset against the evtol.news directory, class by class

**Question.** Does the class mix of the patented aircraft stand for the aircraft the sector announces? If not, which class makes the difference, and why?

**Method.** Both sources are counted in unique aircraft and folded to the directory's five classes (`analysis.class_fold` in the yaml: L+C → LC; TP, TW, CVT, TB, PTC, DS → VT; MR → WM; RC → ER; SRW → LC by the ruling of 2026-10-01; HB, PFV → HB). The labelled dataset is the 627 analysis aircraft (625 with a class); the directory is every evtol.news aircraft page (1 229; a page is a model or a version of it, so a family can count more than once). The two mixes are compared with a chi-square test, and each cell with its adjusted standardized residual (`lib.association.adjusted_residuals`: |r| > 1.96 marks the classes that make the difference). Shares carry a 95 % Wilson interval (`lib.intervals`).

**Why the mixes could differ — each tested by rebuilding the directory side:** (a) **domain**: the dataset keeps only electric, non-UAV aircraft, the directory keeps everything → the directory restricted to pages whose power source is not only combustion/hybrid/fuel cell and that are not cargo-only or unmanned with no capacity (`frames.directory_frame`, an approximation from the free-text spec sheet); (b) **maturity**: concept designs against flying hardware; (c) **time**: answered per window by Figure 2; (d) **patenting**: the directory pages that are linked to a patented aircraft of this dataset against those that are not. A subset whose mix matches the dataset's points at the reason.

**Caveat on (d).** The linked pages are the directory aircraft that were matched by name to a patented aircraft, so they are the named, company-backed part of the dataset (Table 2: 97 aircraft). Their class here is the DIRECTORY's own class, not the wizard label, so a match is not circular: it says the directory itself classes the patented aircraft like the dataset does. It cannot say whether unnamed patented aircraft would behave the same.""")
code("""O5 = ['VT', 'LC', 'WM', 'ER', 'HB']
NAME5 = {'VT': 'Vectored Thrust', 'LC': 'Lift + Cruise', 'WM': 'Wingless (Multicopter)', 'ER': 'Electric Rotorcraft', 'HB': 'Hoverbike / Personal Flying Device'}
dirf = frames.directory_frame(cfg)
n_set = v['class5'].value_counts().reindex(O5, fill_value=0)              # labelled dataset, unique aircraft
n_dir = dirf['class5'].value_counts().reindex(O5, fill_value=0)           # directory, unique pages
ct = np.vstack([n_set.to_numpy(), n_dir.to_numpy()])
mix_test = association.chi2_test(ct)
resid = association.adjusted_residuals(ct)[0]                           # dataset row: + = more than expected
def ci(k, n):
    lo, hi = intervals.wilson_interval(k, n)
    return f"{lo * 100:.0f}–{hi * 100:.0f} %"
mix5 = pd.DataFrame({'class': [NAME5[c] for c in O5], 'code': O5,
                     'labelled dataset': n_set.to_numpy(), 'share in dataset': (n_set / n_set.sum()).round(3).to_numpy(),
                     'dataset 95 % interval': [ci(k, n_set.sum()) for k in n_set],
                     'evtol.news directory': n_dir.to_numpy(), 'share in directory': (n_dir / n_dir.sum()).round(3).to_numpy(),
                     'directory 95 % interval': [ci(k, n_dir.sum()) for k in n_dir],
                     'difference (points)': ((n_set / n_set.sum() - n_dir / n_dir.sum()) * 100).round(1).to_numpy(),
                     'adjusted residual': resid.round(1)})
print(f"dataset {n_set.sum()} aircraft · directory {n_dir.sum()} pages · chi-square {mix_test['chi2']:.1f}, dof {mix_test['dof']}, p {pval(mix_test['p'])}")
mix5""")
md("""Which part of the directory looks like the dataset? The same five shares for each subset of the directory, each tested against the dataset (chi-square, 5 classes). The subset with the smallest chi-square is the one whose mix is closest to the patented aircraft.""")
code("""subsets = {
    'labelled dataset (patented aircraft)': None,
    'directory: all pages': pd.Series(True, index=dirf.index),
    '(a) in domain: electric, crewed': dirf['in_domain'],
    '(b) concept designs': dirf['status_group'].eq('concept design'),
    '(b) flying hardware': dirf['status_group'].eq('flying hardware'),
    '(d) linked to a patent of this dataset': dirf['patented'],
    '(d) not linked to a patent': ~dirf['patented'],
}
rows = []
for name, m in subsets.items():
    k = n_set if m is None else dirf.loc[m, 'class5'].value_counts().reindex(O5, fill_value=0)
    row = {'source': name, 'n': int(k.sum())}
    for c in O5:
        row[c] = round(k[c] / k.sum(), 3)
    if m is not None:
        t = association.chi2_test(np.vstack([n_set.to_numpy(), k.to_numpy()]))
        row['chi-square vs dataset'], row['p vs dataset'] = round(t['chi2'], 1), pval(t['p'])
    rows.append(row)
why = pd.DataFrame(rows)
why""")
code("""closest = why.dropna(subset=['chi-square vs dataset']).sort_values('chi-square vs dataset').iloc[0]
wm = why.set_index('source')['WM']
print(f"The class that makes the difference: {NAME5[O5[int(np.argmin(resid))]]} (adjusted residual {resid.min():.1f}) "
      f"and {NAME5[O5[int(np.argmax(resid))]]} (+{resid.max():.1f}).")
print(f"Multicopter share: dataset {wm.iloc[0]:.0%}, directory {wm['directory: all pages']:.0%}, in domain {wm['(a) in domain: electric, crewed']:.0%}, "
      f"flying hardware {wm['(b) flying hardware']:.0%}, linked to a patent {wm['(d) linked to a patent of this dataset']:.0%}.")
print(f"Closest directory subset to the dataset: {closest['source']} (chi-square {closest['chi-square vs dataset']}, p {closest['p vs dataset']}, n {closest['n']}).")
save.table(mix5, cfg, 'q1', 'tab_1_3_5_dataset_vs_directory',
           caption='Unique aircraft per evtol.news class in the labelled dataset and in the evtol.news directory, with 95 % Wilson intervals, the difference in points and the adjusted standardized residual of the dataset cell.',
           source='human labelling, folded by analysis.class_fold · evtol.news directory pages (crawled 2026-09-17)')
save.table(why, cfg, 'q1', 'tab_1_3_5_directory_subsets',
           caption='The class shares of each subset of the directory against the labelled dataset; chi-square of the subset against the dataset over the five classes.',
           source='evtol.news directory pages (status, power source, capacity, piloting) · patent_links.csv · human labelling')""")
md("""### Figure 5b — the labelled dataset against the evtol.news directory""")
code("""SPEC5 = {'LC': 'SLC', 'VT': 'TR', 'WM': 'MR', 'ER': 'RC', 'HB': 'HB'}         # the colour/hatch each class borrows (as Figure 2)
W, _ = style.size(cfg, 'full')
fig = plt.figure(figsize=(W, 5.8), constrained_layout=True)
gs = fig.add_gridspec(2, 5, height_ratios=[1.0, 1.25])
# (i) the two sources side by side, in number of aircraft
ax = fig.add_subplot(gs[0, :])
x = np.arange(len(O5)); bw = 0.38
for i, c in enumerate(O5):
    s = style.cls(SPEC5[c])
    for j, (k, n, face, hatch) in enumerate([(n_set[c], n_set.sum(), s.color, s.hatch),
                                             (n_dir[c], n_dir.sum(), 'white', '')]):
        xx = x[i] + (j - 0.5) * bw
        ax.bar(xx, k, bw * 0.92, color=face, hatch=hatch, edgecolor=s.color if j else 'white', linewidth=1.0 if j else 0.5)
        lo, hi = intervals.wilson_interval(k, n)
        ax.plot([xx, xx], [lo * n, hi * n], color=style.INK, linewidth=0.8)
        ax.text(xx, hi * n + 6, f"{thin(k)}\\n({k / n:.0%})".replace('%', ' %'), ha='center', va='bottom',
                fontsize=plt.rcParams['xtick.labelsize'] - 1)
ax.set_xticks(x, [f"{c}\\n{NAME5[c].split(' (')[0].split(' /')[0]}" for c in O5])
ax.set_ylim(0, max(n_set.max(), n_dir.max()) * 1.6)                    # room for the legend above the labels
ax.set_ylabel('unique aircraft')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=style.INK, label=f'labelled dataset ({thin(n_set.sum())} aircraft; filled)'),
                   Patch(facecolor='white', edgecolor=style.INK, label=f'evtol.news directory ({thin(n_dir.sum())} pages; outline)')],
          loc='upper right')
style.mark(ax, '(i)')
# (ii) one panel per class: the aircraft of the class in the dataset and in each part of the directory
order = [s for s in why['source']]
ylab = ['dataset', 'directory, all', '(a) in domain', '(b) concept', '(b) flying', '(d) patented', '(d) not patented']
counts = {name: (n_set if m is None else dirf.loc[m, 'class5'].value_counts().reindex(O5, fill_value=0)) for name, m in subsets.items()}
for i, c in enumerate(O5):
    a = fig.add_subplot(gs[1, i])
    s = style.cls(SPEC5[c])
    for r, (name, m) in enumerate(subsets.items()):
        k = counts[name]
        lo, hi = intervals.wilson_interval(k[c], k.sum())
        y = len(order) - 1 - r
        a.plot([lo * k.sum(), hi * k.sum()], [y, y], color=style.MUTED, linewidth=1)
        a.plot(k[c], y, marker=s.marker, markersize=5, linestyle='none',
               color=s.color if m is None else 'white', markeredgecolor=s.color if m is None else style.INK, markeredgewidth=0.8)
        a.annotate(thin(k[c]), (k[c], y), xytext=(0, 4), textcoords='offset points', ha='center', va='bottom',
                   fontsize=plt.rcParams['xtick.labelsize'] - 2, color=style.INK)
    a.axvline(n_set[c], color=s.color, linewidth=0.8, linestyle=':')
    a.set_yticks(range(len(order)), ylab[::-1] if i == 0 else [''] * len(order))
    top = max(max(k[c], intervals.wilson_interval(k[c], k.sum())[1] * k.sum()) for k in counts.values())
    a.set_xlim(0, top * 1.12)
    a.set_ylim(-0.6, len(order) - 0.3)
    a.set_title(c, fontsize=plt.rcParams['font.size'])
    a.tick_params(axis='x', labelsize=plt.rcParams['xtick.labelsize'] - 1)
    if i == 0:
        style.mark(a, '(ii)', lines_up=1)
fig.supxlabel('unique aircraft of the class in each source (95 % Wilson interval); dotted line: the labelled dataset', fontsize=plt.rcParams['xtick.labelsize'])
plt.show()""")
code("""save.figure(fig, cfg, 'q1', 'fig_05b_dataset_vs_directory', data=why,
            caption='The labelled dataset against the evtol.news directory in the directory\\'s five classes: (i) the unique aircraft of each class in the two sources; (ii) for each class, the aircraft in the dataset and in parts of the directory that could explain a difference.',
            source='human labelling, folded by analysis.class_fold (SRW to LC, ruling 2026-10-01) · evtol.news directory, 1 229 aircraft pages crawled 2026-09-17 (class, status, power source, capacity, piloting) · patent_links.csv',
            unit='unique aircraft (dataset) and aircraft pages (directory); in (i) the share of the source in brackets',
            read=f"(i) Filled bar: labelled dataset; outlined bar: directory; whisker: 95 % Wilson interval of the count; label: aircraft and, in brackets, the share of the source (the sources differ in size: {n_set.sum()} against {thin(n_dir.sum())}). Chi-square of the two mixes {mix_test['chi2']:.0f}, p {pval(mix_test['p'])}. (ii) One panel per class, in aircraft; each row is a source: the dataset (filled marker, dotted line) and five parts of the directory (open markers): in domain (electric, crewed), concept designs, flying hardware, pages linked to a patent of this dataset, and pages not linked. The parts differ in size, so compare their mixes with the shares in the table above.",
            panels={'(i)': 'aircraft per class in the two sources', '(ii)': 'aircraft of the class per part of the directory'})""")


md("""### 1.3 numbers""")
code("""pw = pairwise.iloc[0]
N3 = {
    'sm_nc_named': str(int(real['unique aircraft'])), 'sm_nc_gen': str(int(gen['unique aircraft'])),
    'sm_pw_img_pub': str(int(pw['agree'])), 'sm_pw_n': str(int(pw['of'])), 'sm_pw_ci': pw['95 % interval'], 'tk_pw_share': pct(pw['share']),
    'sm_trl_share': pct(float(trl.loc[trl['class'] == 'Total', 'share above TRL 2'].iloc[0])),
    'tk_ari_firms_n': str(len(firms)),
}
numbers_check(N3)""")

# ------------------------------------------------------------------------------------------ overview
md("""## Overview: what matched

Every number the document quotes for chapter 1 (96) and every table, with the differences labelled.""")
code("""allnum = pd.concat(NUMBERS, ignore_index=True)
missing = checks.missing_numbers(dict.fromkeys(allnum['name']), '1')
print(f"numbers: {int((allnum['match'] == 'yes').sum())} of {len(allnum)} match the document; "
      f"{int(allnum['match'].str.startswith('expected').sum())} expected differences; {int((allnum['match'] == 'NO').sum())} failures; "
      f"{len(missing)} of the document's 96 not computed here: {missing}")
overview = pd.DataFrame([c.iloc[0].to_dict() for c in CHECKS])
overview""")
code("""assert (allnum['match'] != 'NO').all(), allnum[allnum['match'] == 'NO']
assert not missing
assert (overview['differences'] == 0).all(), overview[overview['differences'] > 0]""")


nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, OUT)
print("written", OUT, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=900", str(OUT)], check=True, cwd=str(OUT.parent))
