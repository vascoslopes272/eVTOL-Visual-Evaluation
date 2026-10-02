"""Generate notebooks/41_q2_design_space.ipynb (and execute it with --run).

    python3 notebooks/_build/build_41.py          # write the notebook
    python3 notebooks/_build/build_41.py --run    # write, then jupyter nbconvert --execute --inplace

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
OUT = PILLAR / "notebooks" / "41_q2_design_space.ipynb"
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
INTRO = "\n".join(_section("## 2 —", "### 2.1 —")).strip().replace("## 2 —", "### Chapter 2 —", 1)

md("""# 41 — Question 2: the design space

What is an eVTOL design made of, and where do designs concentrate?

Sub-questions 2.1, 2.2, 2.3 of the Labelling Analysis (2026-09-30). Every path comes from `labelling_analysis.yaml`; equations come from `lib/`, figures and tables from `viz/`.

This notebook reproduces every figure, table and number of chapter 2 of the 45-page document, and compares them with it (`viz.checks`). Nothing in chapter 2 uses the five-class fold (the archetype sets read the twelve classes), so the class fold of 2026-10-01 (Stopped/Slowed Rotor Wing into Lift + Cruise) moves no number here; the only differences from the document's tables are the display names of 2026-09-28 (Tilt Rotor is printed Tilt Propulsor, propulsive unit is printed propulsor unit), which `viz.checks` maps through `rename`.

Outputs are written to `<output>/q2_design_space/` (figures: pdf, png, csv, json; tables: csv, json). Regenerate this notebook with `python3 notebooks/_build/build_41.py`.""")
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

`frames.base` is the per-aircraft analysis frame (627 rows); `lib` holds every equation; `viz.checks` compares with the document. `verify` runs one table check and keeps its summary for the final overview; `numbers_check` does the same for the quoted numbers.""")
code(r"""import inspect
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import Bbox
from IPython.display import display
from viz import frames, style, plots, save, checks
from lib import diversity, concentration, dominant_design

style.apply(cfg)
v = frames.base(ds, cfg)                                   # one row per unique aircraft (627)
WIN_NAMES = list(cfg.analysis['windows'])
W, _ = style.size(cfg, 'full')
SEED = cfg.analysis['random_seed']
pct = lambda x: f"{x:.0%}".replace('%', ' %')              # 0.53 -> '53 %'
CHECKS, NUMBERS = [], []                                   # summaries kept for the overview at the end

def verify(frame, ref, name=None, **kw):
    r = checks.table(frame, ref, cfg, name=name, **kw)
    CHECKS.append(r)
    display(r.T.rename(columns={0: name or ref}))
    d = checks.detail(r)
    if len(d):
        display(d)

def numbers_check(values, expected=None):
    r = checks.numbers(values, '2', expected)
    NUMBERS.append(r)
    display(r)

def short(key):
    '''An archetype key of the C·U set as the figures print it: 'SLC · 9+' -> 'L+C 9+', 'HB · n/a (no M3 card)' -> 'HB'.'''
    c, _, b = key.partition(' · ')
    return f"{style.cls(c).short} {b.replace('n/a (no M3 card)', '')}".strip()

# the display names of 2026-09-28 against the document's tables (see the first cell)
RENAME_FIELDS = {frames.D3_PLACES_ROW: 'propulsor groups per aircraft', frames.D3_UNITS_ROW: 'propulsor units per aircraft'}""")
md("""### 0.1 The numbers of the Method common to every chapter

The rarefaction size, the seed and the number of permutations of the statistics box (shared with chapters 1 and 3).""")
code(r"""N0 = {'sm_perm_n': str(cfg.analysis['rarefy_n']), 'sm_perm_seed': str(SEED),
      'sm_perms': str(inspect.signature(dominant_design.balance_band).parameters['perms'].default)}
numbers_check(N0)""")

# ------------------------------------------------------------------------------------------ 2.1
md(question_and_method("2.1", "", ""))
md("""### Table 6 — the label fields that tell designs apart

Per label field: the unique aircraft that answer it, the number of different answers, the top share (`lib.concentration.top_k_share` of order 1) and the most common answers with their aircraft. Two derived rows close the table: the propulsor units per aircraft in the five bands and the places carrying propulsor units, read on the aircraft with a propulsion record (`frames.selected_fields`). A field whose top share reaches the cut of the yaml (`analysis.field_drop_top_share`) is left out of the printed table and named under it.""")
code(r"""t6 = frames.selected_fields(ds)
verify(t6, 'a2_d3_selected_fields', key=['field'], rename=RENAME_FIELDS)
t6""")
code(r"""cut = cfg.analysis['field_drop_top_share']
kept = t6[t6['top_share'] < cut]
dropped = t6.loc[t6['top_share'] >= cut, 'name'].tolist()
colon = lambda s: ' · '.join(f"{a.rsplit(' ', 1)[0]}: {a.rsplit(' ', 1)[1]}" for a in s.split(' · '))
tab6 = pd.DataFrame({'field': kept['name'], 'aircraft answering': kept['answered'], 'different answers': kept['answers'],
                     'top share': kept['top_share'], 'most common answers: aircraft': kept['most common answers'].map(colon)}).reset_index(drop=True)
save.table(tab6, cfg, 'q2', 'tab_6_selected_fields', caption=@CAP@,
           source='human labelling (the codebook fields of the labelled dataset, 627 unique aircraft; the derived propulsion rows read the 596 aircraft with a propulsion record)')
print('left out as near-constant (top share of', pct(cut), 'or more):', ', '.join(dropped))
tab6""", CAP=q(caption("Table", 6)))
md("""### Figure 6 — how the propulsion varies

Three graphs on the unique aircraft. (i) The propulsor units of every aircraft of each class: a dot per aircraft (jittered, capped at 30), the bar over the middle half, the ring at the median. (ii) The share of each class's aircraft with each arrangement feature (`frames.arrangement_features`; the share is over the aircraft where the feature can be read, printed under the class as read/total where some cannot). (iii) Ducting per propulsor-unit band: the tables `frames.duct_count_by_units` and `frames.duct_conditional` are checked against the document before they are drawn.""")
code(r"""dcount = frames.duct_count_by_units(v)
dcond = frames.duct_conditional(v)
verify(dcount, 'la_duct_count', key=['propulsive units'])
verify(dcond, 'la_duct_conditional', key=['propulsive units'])
codes = [c for c in style.CLASS_ORDER if c in set(v['topType'].dropna())]
feat, read, total = frames.arrangement_features(v, codes)
units_by_class = [pd.to_numeric(v.loc[v['topType'] == c, 'units'], errors='coerce').to_numpy() for c in codes]
unit = frames.propulsor_units(ds.variants)['units'].dropna()       # the 596 aircraft with a propulsion record
display(feat.round(3)); display(pd.DataFrame({'read': read, 'aircraft': total}).T)""")
code(r"""fig = plt.figure(figsize=(W, 7.4), constrained_layout=True)
gs = fig.add_gridspec(3, 1, height_ratios=[2.0, 1.25, 2.6])
ax1, ax2, ax3 = (fig.add_subplot(g) for g in gs)
plots.unit_strips(ax1, codes, units_by_class, cap=30, seed=SEED)
ax1.set_xlim(-0.6, len(codes) - 0.4); ax1.set_xticks(range(len(codes)), [])
ax1.set_ylabel('propulsor units\n(capped at 30)'); style.mark(ax1, '(i)')
ROWS = {'at least one tilting propulsor': '≥ 1 tilting', 'both fixed and tilting propulsors': 'fixed and tilting',
        'a ducted propulsor': '≥ 1 ducted', 'more than 8 propulsors': 'more than 8'}
plots.feature_heat(ax2, feat.rename(index=ROWS))
plots.class_ticks(ax2, codes, [f"{n}" if r == n else f"{r}/{n}" for r, n in zip(read, total)])
style.mark(ax2, '(ii)')
plots.duct_bands(ax3, dcount, dcond)
ax3.set_ylabel("share of the band's aircraft")
ax3.set_xlabel('propulsor-unit band\nunder each band: aircraft · aircraft with a ducted propulsor · median ducted propulsors of those', fontsize=7.5)
ax3.legend(loc='upper left', ncol=2, fontsize=7.5); style.mark(ax3, '(iii)')
plt.show()""")
code(r"""fig6_units = pd.concat([pd.DataFrame({'class': style.cls(c).name, 'propulsor units': u}) for c, u in zip(codes, units_by_class)], ignore_index=True)
save.table(fig6_units, cfg, 'q2', 'fig_06_i_units_per_aircraft', caption='Figure 6 (i), the propulsor units of every aircraft by class.', source='human labelling')
save.table(feat.round(3).reset_index().rename(columns={'index': 'feature'}), cfg, 'q2', 'fig_06_ii_arrangement_share',
           caption='Figure 6 (ii), share of each class with each arrangement feature.', source='human labelling')
save.figure(fig, cfg, 'q2', 'fig_06_propulsion_compact', data=dcount.merge(dcond, on='propulsive units'),
            caption=@CAP@,
            source='human labelling (the propulsion record of each place: propulsor units, tilt and duct per propulsor type)',
            unit=f"unique aircraft (627); units read on the {len(unit)} with a propulsion record ({int(dcount['aircraft'].iloc[-1])} with a unit count above zero in (iii)); a column of (ii) under HB and PFV is empty because the codebook gives them no propulsor card",
            read='(i) Dot: one aircraft (jittered sideways, units above 30 drawn at 30); bar: the middle half of the class; ring: the median, which a few aircraft with very many propulsor units do not pull. (ii) Cell: the share of the class with the feature (tilting: at least one propulsor tilts, on its mount, on a tilting wing, on a tilting boom group or on a tilting tail; fixed and tilting: both kinds on one aircraft; ducted: at least one ducted propulsor; more than 8 propulsors); under the class: aircraft (read/total where a propulsion record is missing). (iii) Bar height: share of the band\'s aircraft with at least one ducted propulsor, split into the aircraft that duct every propulsor (dark, with its share of the ducting aircraft printed in white), half or more but not all, and under half; diamond: the share of all the band\'s propulsor units that sit in a duct; under each band: aircraft, aircraft that duct, median ducted propulsors of those.',
            panels={'(i)': 'propulsor units per class', '(ii)': 'arrangement features per class', '(iii)': 'ducting per propulsor-unit band'})
plt.close(fig)""", CAP=q(caption("Figure", 6)))
md("""### 2.1 numbers""")
code(r"""t6i = t6.set_index('name')
dci = dcount.set_index('propulsive units')
N1 = {
    'units_n': str(len(unit)), 'units_median': f"{unit.median():g}",
    'tk_emptype': pct(t6i.loc['tail type', 'top_share']), 'tk_units_top': pct(t6i.loc[frames.D3_UNITS_ROW, 'top_share']),
    'sm_d3_wings_top': pct(t6i.loc['number of wings', 'top_share']), 'sm_d3_drop_share': pct(cut),
    'sm_duct13_med': f"{dci.loc['1-3', 'median ducted units (ducted aircraft)']:.0f}",
    'sm_duct9_med': f"{dci.loc['9+', 'median ducted units (ducted aircraft)']:.1f}",
    'sm_duct9_units': pct(dci.loc['9+', 'share of units ducted']),
}
numbers_check(N1)""")

# ------------------------------------------------------------------------------------------ 2.2
md(question_and_method("2.2", "", ""))
md("""### The nine archetype sets and the four screens

Nine archetype sets can be formed from the codebook (the class with wings, booms, tail, tilt and the propulsor-unit band). For each: the archetypes, the aircraft alone in theirs, ¹D (`lib.diversity.effective_number`), ²D (`lib.concentration.inverse_hhi`), the largest archetype and the archetypes of five or more (`frames.archetype_levels_table`), over the whole corpus and all years. The four screens (lines from `analysis.archetype_screens`) are applied in `frames.archetype_screens`; both tables are checked against the document.""")
code(r"""levels = frames.archetype_levels_table(ds, v, cfg)
LV_COLS = ['level', 'largest archetype', 'aircraft', 'left out', 'archetypes', 'singletons', 'singleton share', 'effective number ¹D',
           'effective number ²D', 'largest share', 'top three share', 'archetypes of five or more', 'share in archetypes of five or more',
           'archetypes holding 5 % or more']
verify(levels, 'la_archetype_levels', key=['level'], columns=LV_COLS)
screens = frames.archetype_screens(levels, cfg)
verify(screens, 'la_archetype_choice', key=['level'], columns=['level', 'screens passed'])
sets9 = levels.assign(set=levels['level'].map(lambda s: frames.SET_CODES[s][0]))[['set', 'archetypes', 'singletons', 'effective number ¹D', 'effective number ²D', 'archetypes of five or more']]
sets9.merge(screens[['level', 'screens passed']].assign(set=screens['level'].map(lambda s: frames.SET_CODES[s][0]))[['set', 'screens passed']], on='set')""")
md("""### ¹D and ²D on the worked example

The worked example of the statistics box (invented round numbers), computed by the same two lib functions: four archetypes of 25 / 25 / 25 / 25 aircraft, and of 70 / 10 / 10 / 10 aircraft.""")
code(r"""rows = []
for sizes in ([25, 25, 25, 25], [70, 10, 10, 10]):
    labels = pd.Series(np.repeat(list('abcd'), sizes))
    d1, d2 = diversity.effective_number(labels), concentration.inverse_hhi(labels.value_counts())
    rows.append({'shares': ' / '.join(str(s) for s in sizes) + ' %', 'H = −Σ pᵢ ln pᵢ': f"{np.log(d1):.2f}", '¹D = exp(H)': f"{d1:.2f}".rstrip('0').rstrip('.') if d1 == 4 else f"{d1:.2f}",
                 'Σ pᵢ²': f"{1 / d2:.2f}", '²D = 1 / Σ pᵢ²': f"{d2:.2f}"})
worked = pd.DataFrame(rows)
DOC_WORKED = [['25 / 25 / 25 / 25 %', '1.39', '4', '0.25', '4.00'], ['70 / 10 / 10 / 10 %', '0.94', '2.56', '0.52', '1.92']]     # as the Method box prints them (4.0 = 4.00)
assert worked.values.tolist() == DOC_WORKED, worked
worked""")
md("""### Table 7 — the four archetype sets the document reads

C, C·W·T, C·U and the Lift + Cruise + CVT* family F (every Lift + Cruise aircraft plus every CVT whose tilting part is a propulsor set on a fixed wing: `frames.family_flags`, `frames.family_mask`). Over the whole corpus, all years: ¹D is therefore not rarefied. The comparison maps the display names (Tilt Propulsor, propulsor units) to the document's.""")
code(r"""brief = frames.archetype_levels_brief(ds, v, levels)
BRIEF_COLS = ['level id', 'aircraft', 'archetypes', 'aircraft alone in their archetype', 'effective number ¹D', 'largest archetype', 'its share',
              'archetypes of five or more']
verify(brief, 'la_archetype_levels_brief', key=['level id'], columns=BRIEF_COLS,
       rename={'Tilt Propulsor · 1-3 propulsor units': 'Tilt Rotor · 1-3 units'})
SET_LABEL = {'A0': 'C (class)', 'A1t': 'C·W·T (class + wings + tilt)', 'A0c': 'C·U (class + propulsor units)', 'family_b': 'F (Lift + Cruise + CVT* family)'}
tab7 = pd.DataFrame({'archetype set': brief['level id'].map(SET_LABEL), 'archetypes': brief['archetypes'], 'singletons': brief['aircraft alone in their archetype'],
                     '¹D': brief['effective number ¹D'], 'largest archetype': brief['largest archetype'], 'its share': brief['its share']})
save.table(tab7, cfg, 'q2', 'tab_7_archetype_sets', caption=@CAP@, source='human labelling')
tab7""", CAP=q(caption("Table", 7)))
md("""### 2.2 numbers""")
code(r"""flags = frames.family_flags(ds, v)
fam_n = int(frames.family_mask(flags[flags['topType'].notna()]).sum())
winn = v['window'].value_counts()
active = int(winn['2016-19'] + winn['2020-23'])
sc = cfg.analysis['archetype_screens']
L = brief.set_index('level id')
N2 = {
    'sm_arch_levels': str(len(levels)), 'sm_arch_max': str(int(levels['archetypes'].max())),
    'sm_arch_pass': str(int((screens['screens passed'] == '4 of 4').sum())),
    'sm_screen_big': str(sc['big_archetype_aircraft']), 'sm_screen_frag': pct(sc['max_singleton_share']), 'sm_screen_pop': pct(sc['min_share_in_big']),
    'sm_screen_readable': str(sc['min_big_share_archetypes']), 'sm_screen_share': pct(sc['big_archetype_share']),
    'sm_fam_b_n': str(fam_n),
    'sm_lv_c_arch': str(L.loc['A0', 'archetypes']), 'sm_lv_c_eff': f"{L.loc['A0', 'effective number ¹D']:.1f}",
    'sm_lv_cu_arch': str(L.loc['A0c', 'archetypes']), 'sm_lv_cu_big': str(L.loc['A0c', 'archetypes of five or more']),
    'sm_lv_cwt_arch': str(L.loc['A1t', 'archetypes']), 'sm_lv_cwt_big': str(L.loc['A1t', 'archetypes of five or more']),
    'sm_lv_f_share': pct(L.loc['family_b', 'its share']),
}
numbers_check(N2)""")

# ------------------------------------------------------------------------------------------ 2.3
md(re.sub(r"\*SLC 9\+\*", "*L+C 9+*", question_and_method("2.3", "", "")))
md("""### The C·U archetypes: zones and filers

`frames.zones` gives, for every C·U archetype of five aircraft or more (`analysis.zone_min_aircraft`), its aircraft, distinct filers (a firm, or an individual inventor's patent as its own filer), the share of the 2016-23 aircraft, the zone (new since 2016 / fading / persistent) and the aircraft per window. `frames.zone_core` marks the crowded core by rule, `frames.archetype_filer_split` says who the largest filer of each archetype of 20 aircraft or more is. Both tables are checked against the document (the class column prints the codes of the data; the display names are in the figures).""")
code(r"""zones = frames.zones(v, WIN_NAMES, cfg.analysis['zone_min_aircraft'])
verify(zones, 'la_zones', key=['archetype'], columns=[c for c in zones.columns if c != 'class'])
split = frames.archetype_filer_split(v, cfg.analysis['filer_panel_min_aircraft'])
verify(split, 'la_archetype_filer_split', key=['archetype'])
zz = zones[zones['filers 2016-23'] > 0]
core = zz[frames.zone_core(zones).reindex(zz.index).fillna(False).astype(bool)]
rim = zz[zz['share 2016-23'] <= zz['share 2016-23'].median()]
half = {w: frames.half_column(zones[w]) for w in ('2016-19', '2020-23')}
display(zones[['archetype', 'aircraft', 'filers', 'filers per aircraft', 'share 2016-23', 'zone'] + WIN_NAMES])
display(split)""")
md("""### Figure 7 — distinct filers per aircraft for the largest C·U archetypes

One bar per C·U archetype with 20 aircraft or more (colour and hatch of its class); Combined Vectored Thrust with 5-6 propulsor units and CVT · 4 beside it are outlined.""")
code(r"""f7 = split.sort_values('filers per aircraft', ascending=False).merge(zones[['archetype', 'code']], on='archetype')
f7['label'] = f7['archetype'].map(short)
FOCUS, NEIGH = 'CVT · 5-6', 'CVT · 4'
top = split.set_index('archetype').loc[FOCUS]
fig, ax = plt.subplots(figsize=(W, 3.3), constrained_layout=True)
plots.filer_bars(ax, f7, [FOCUS, NEIGH], FOCUS, f"{top['largest filer']} holds {int(top['its aircraft'])} of the {int(top['aircraft'])}; {int(top['filers holding one aircraft'])} filers hold one each")
ax.set_xlim(0, 1.75); ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_xlabel('distinct filers per aircraft (1.00 = every aircraft a different filer)')
plt.show()
save.figure(fig, cfg, 'q2', 'fig_07_archetype_filers', data=f7.drop(columns='label'),
            caption=@CAP@,
            source='human labelling (class, propulsor units) · PatSeer (applicant, read as filer)',
            unit=f"C·U archetypes with {cfg.analysis['filer_panel_min_aircraft']} or more unique aircraft ({len(f7)}); on fewer, one filer moves the ratio by a large step",
            read="Bar: the archetype's distinct filers divided by its aircraft (a filer is a firm; an individual inventor's patent is its own filer). 1.00 means every aircraft has a different filer; a low value is the trace of one firm's line of variants. After the bar: the ratio and (filers / aircraft). Outlined: CVT with 5-6 propulsor units, the lowest, with the split of its filers, and CVT with 4 propulsor units beside it.")
plt.close(fig)""", CAP=q(caption("Figure", 7)))
md("""### Figure 8 — where the recent aircraft concentrate

(i) Each C·U archetype of five aircraft or more by its share of the 2016-23 aircraft (the two windows whose publication lag has run: 450 aircraft) and its distinct filers per aircraft; bubble area is the archetype's aircraft; ▲ first seen in 2016-19 or later, ▼ not seen after 2016-19, ● throughout. The crowded core (solid ring) is the largest archetypes that together hold half of the 2020-23 aircraft (`frames.zone_core`); the empty rim (dashed) is at or below the median share (the vertical grey line). (ii) Aircraft per window for each archetype, largest first; the orange bar marks the column by which half the window's aircraft are reached. An archetype is labelled in (i) when it holds 12 aircraft or more, 3 % of the 2016-23 aircraft or more, or has fewer than 0.75 filers per aircraft; every archetype is named in (ii).""")
code(r"""WLAB = {'<= 2011': '≤2011', '2012-15': '2012–15', '2016-19': '2016–19', '2020-23': '2020–23', '2024-26 (partial)': '2024–26*'}
mx, my = zz['share 2016-23'].median(), zz['filers per aircraft'].median()
bubble = lambda n: 14 + 2.2 * np.asarray(n, dtype=float)                      # marker area, pt²
radius = lambda d: np.sqrt(bubble(d['aircraft']) / np.pi)                      # marker radius, pt
fig = plt.figure(figsize=(W, 9.2), constrained_layout=True)
gs = fig.add_gridspec(2, 1, height_ratios=[1.45, 1])
ax = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1])
for _, r in zz.iterrows():
    s = style.cls(r['code'])
    ax.scatter(r['share 2016-23'], r['filers per aircraft'], s=bubble(r['aircraft']), color=s.color, hatch=s.hatch, edgecolor='white',
               linewidth=0.6, marker={'new': '^', 'fading': 'v'}.get(r['zone'], 'o'), zorder=3)
ax.set_xlim(-0.002, zz['share 2016-23'].max() * 1.12); ax.set_ylim(0.3, 1.06)
ax.axvline(mx, color=style.GRID, linewidth=1, zorder=0); ax.axhline(my, color=style.GRID, linewidth=1, zorder=0)
ax.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
ax.set_xlabel('share of the 2016–23 aircraft'); ax.set_ylabel('distinct filers per aircraft'); style.mark(ax, '(i)')
# (ii)
mat = zones.set_index('archetype')[WIN_NAMES].astype(float).T
m2 = mat.rename(index=WLAB); m2.columns = [short(a) for a in m2.columns]
plots.window_heat(ax2, m2, {WLAB[w]: j for w, j in half.items()})
ax2.tick_params(axis='x', labelsize=7); style.mark(ax2, '(ii)')
# the key, then the layout is final and the labels can be placed
codes8 = [c for c in style.CLASS_ORDER if c in set(zz['code'])]
handles = [Patch(facecolor=style.cls(c).color, hatch=style.cls(c).hatch, edgecolor='white', label=f"{style.cls(c).short} {style.cls(c).name}") for c in codes8]
handles += [Line2D([], [], marker='o', color=style.INK, linestyle='none', label='throughout'),
            Line2D([], [], marker='^', color=style.INK, linestyle='none', label='first seen 2016 or later')]
fig.legend(handles=handles, loc='outside lower center', ncol=4, fontsize=7.5, handlelength=1.2, columnspacing=1.0)
fig.canvas.draw()
ring_core = plots.hull_ring(ax, core['share 2016-23'], core['filers per aircraft'], radius(core), pad_pt=3, linewidth=1.5)
ring_rim = plots.hull_ring(ax, rim['share 2016-23'], rim['filers per aircraft'], radius(rim), pad_pt=3.5, linewidth=1.2, linestyle=(0, (4, 2)), edgecolor=style.MUTED)
def along(h, pad=3):
    pts = [a + (b - a) * t for a, b in zip(h, np.roll(h, -1, axis=0)) for t in np.linspace(0, 1, 12)]
    return [Bbox([[x - pad, y - pad], [x + pad, y + pad]]) for x, y in pts]
t_core = ax.text(0.985, 0.03, f"crowded core ({len(core)} archetypes): the\nlargest archetypes, which together hold\nhalf of the 2020–23 aircraft", transform=ax.transAxes,
                 ha='right', va='bottom', fontsize=7.5, linespacing=1.15)
t_rim = ax.text(0.01, 0.3, f"empty rim ({len(rim)} archetypes):\nat or under the median share", transform=ax.transAxes, ha='left', va='bottom',
                fontsize=7.5, linespacing=1.15, color=style.MUTED)
cvt = zz[zz['archetype'] == FOCUS].iloc[0]
callout = (f"{short(FOCUS)}: {int(cvt['filers'])} filers for {int(cvt['aircraft'])} aircraft,\nthe fewest per aircraft of the {len(split)}\n"
           f"archetypes with {cfg.analysis['filer_panel_min_aircraft']}+ aircraft; {top['largest filer'].split(' / ')[0]} /\n{top['largest filer'].split(' / ')[-1]} holds {int(top['its aircraft'])} of them,\n"
           f"{int(top['filers holding one aircraft'])} filers hold one each")
t_cv = ax.text(0.01, 0.02, callout, transform=ax.transAxes, ha='left', va='bottom', fontsize=7.5, linespacing=1.15, bbox=dict(fc='white', ec=style.MUTED, lw=0.6, pad=2.5))
ax.annotate('', xy=(cvt['share 2016-23'], cvt['filers per aircraft']), xytext=(0.355, 0.075), textcoords='axes fraction',
            arrowprops=dict(arrowstyle='-', lw=0.8, color=style.INK, shrinkA=0, shrinkB=float(radius(cvt.to_frame().T)[0]) + 1))
fig.canvas.draw()
rend = fig.canvas.get_renderer()
obstacles = along(ring_core) + along(ring_rim) + [t.get_window_extent(rend).expanded(1.03, 1.1) for t in (t_core, t_rim, t_cv)]
lab = zz[(zz['aircraft'] >= 12) | (zz['share 2016-23'] >= 0.03) | (zz['filers per aircraft'] < 0.75)]
failed = plots.place_labels(ax, lab['share 2016-23'].to_numpy(), lab['filers per aircraft'].to_numpy(), [short(a) for a in lab['archetype']], radius(lab),
                            obstacles=obstacles, fontsize=7, extra_avoid=list(zip(zz['share 2016-23'], zz['filers per aircraft'], radius(zz))))
assert not failed, failed
plt.show()""")
code(r"""save.figure(fig, cfg, 'q2', 'fig_08_zones', data=zones,
            caption=@CAP@,
            source='human labelling (class, propulsor units) · PatSeer (applicant, priority date)',
            unit=f"C·U archetypes with {cfg.analysis['zone_min_aircraft']} or more unique aircraft ({len(zones)}); (i) the {len(zz)} that have an aircraft in 2016-23, (ii) unique aircraft ({int(mat.to_numpy().sum())}) in the same {mat.shape[1]} archetypes per priority window; * the window 2024-26 is partial",
            read=f"(i) Right: the archetype holds a large share of the 2016-23 aircraft; up: it is filed by many different filers per aircraft (an open field), down: by few filers with many aircraft each. Bubble area: the archetype's aircraft; colour and hatch: its class; shape: first seen in 2016-19 or later (triangle up), not seen after 2016-19 (triangle down), throughout (circle). Solid ring: the crowded core ({len(core)} archetypes); dashed ring: the empty rim ({len(rim)} archetypes). Not every archetype is labelled in (i): those with fewer than 12 aircraft, under 3 % of the 2016-23 aircraft and 0.75 filers per aircraft or more are named in (ii). (ii) Columns: the same archetypes, largest first; cell: its aircraft in the window, shaded by its own busiest window; orange bar: the column by which half of the window's aircraft are reached (the largest {half['2016-19'] + 1} archetypes in 2016-19, the largest {half['2020-23'] + 1} in 2020-23).",
            panels={'(i)': 'the crowded core and the empty rim', '(ii)': 'aircraft per window for each archetype'})
plt.close(fig)""", CAP=q(caption("Figure", 8)))
md("""### Figure 9 — is the design space still opening?

Aircraft with a priority year up to 2023 are added in priority order and the distinct archetypes seen so far are counted (`lib.diversity.discovery_curve_levels`: 400 orderings of the aircraft inside a year, seed 42, one generator shared by the sets in the order C, C·U, C·W·T); the dotted line is the same aircraft in random order (`lib.diversity.rarefaction_curve`). Chao1 and the new archetypes of the last 100 aircraft come from `lib.diversity.chao1_jackknife` and `discovery_tail` (`frames.discovery_estimators`). The curve and the estimators are checked against the document.""")
code(r"""SETS3 = ['A0', 'A0c', 'A1t']                                       # the order of the document's generator
inputs = frames.discovery_inputs(v, SETS3, cfg.analysis['last_complete_year'])
curve = diversity.discovery_curve_levels(inputs, orders=cfg.analysis['discovery_orders'], seed=SEED)
est = frames.discovery_estimators(inputs, curve, tail=cfg.analysis['discovery_tail'])
verify(curve, 'la_discovery_curve', key=['level', 'aircraft'])
EST_COLS = ['level', 'aircraft', 'archetypes observed', 'seen once (f1)', 'seen twice (f2)', 'Chao1', 'Chao1 95 % low', 'Chao1 95 % high', 'estimated unseen',
            'jackknife 1', 'jackknife 2', 'coverage', 'share of richness found', 'archetypes by half the corpus', 'new in the last 100 aircraft',
            'new in the 100 before that', 'new in the last 100, random order', 'date order vs random, last tail']
verify(est, 'la_discovery_estimators', key=['level'], columns=EST_COLS)
est""")
code(r"""NAMES3 = {'A0': 'C', 'A0c': 'C·U', 'A1t': 'C·W·T'}
fig, ax = plt.subplots(figsize=(W, 3.4), constrained_layout=True)
plots.discovery_lines(ax, curve, NAMES3, cfg.analysis['discovery_tail'])
ax.set_xlabel('aircraft, in priority order'); ax.set_ylabel('distinct archetypes seen'); ax.set_ylim(0, 48)
h, l = ax.get_legend_handles_labels()
h += [Line2D([], [], color='#8c8c8c', linewidth=0.9, linestyle=(0, (1, 1.8))), Patch(facecolor='#bdbdbd', alpha=0.6, linewidth=0)]
l += ['the same aircraft in random order', 'spread over the orderings inside a year']
fig.legend(h, l, loc='outside upper center', ncol=3, fontsize=7.5, handlelength=2.6)
a0 = curve[curve['level'] == 'A0']
hit = a0[a0['archetypes (date order)'] >= a0['archetypes (date order)'].max() - 1e-9].iloc[0]
ax.annotate(f"12th class: aircraft {int(hit['aircraft'])}\n(priority {int(hit['priority year reached'])})", xy=(hit['aircraft'], 12),
            xytext=(hit['aircraft'] + 25, 5.5), fontsize=7.5, va='center', arrowprops=dict(arrowstyle='-', lw=0.5))
ei = est.set_index('level')
lines = ['the last 100 aircraft (grey band)', 'new archetypes: date order · by chance'] + [
    f"{NAMES3[s]}: {ei.loc[s, 'new in the last 100 aircraft']:.1f} · {ei.loc[s, 'new in the last 100, random order']:.1f}" for s in SETS3]
ax.text(0.77, 0.42, '\n'.join(lines), transform=ax.transAxes, ha='right', va='center', fontsize=7.5, linespacing=1.3, bbox=dict(fc='white', ec='none', pad=2))
plt.show()
save.figure(fig, cfg, 'q2', 'fig_09_discovery_curve', data=curve,
            caption=@CAP@,
            source='human labelling (class, wings, tilt, propulsor units) · PatSeer (priority date)',
            unit=f"unique aircraft with a priority year up to {cfg.analysis['last_complete_year']}, whose publication lag has run ({int(ei.loc['A0', 'aircraft'])} at C and C·U, {int(ei.loc['A1t', 'aircraft'])} at C·W·T, where one aircraft has no answer on a field)",
            read="Solid, dashed and dotted black lines: the distinct archetypes seen as aircraft are added in priority order, at C, C·U and C·W·T; the grey ribbon is the spread over the random orderings of the aircraft inside one priority year. The light dotted line of each set: the same aircraft in a fully random order, the reference for what accumulation alone gives. The grey band is the last 100 aircraft: the box prints the new archetypes the date order brought in that span against what a random 100 aircraft would have brought. A curve still climbing at the right edge means the space is still opening; a flat line means it is not producing new archetypes.")
plt.close(fig)""", CAP=q(caption("Figure", 9)))
md("""### 2.3 numbers""")
code(r"""fs = split.set_index('archetype').loc[FOCUS]
top_key, top_share = frames.top_archetype_share(v, 'A0c', '2020-23', ds)
N3 = {
    'sm_zones_n': str(len(zones)), 'sm_zones_min': str(cfg.analysis['filer_panel_min_aircraft']), 'sm_zones_big_n': str(int((zones['aircraft'] >= cfg.analysis['filer_panel_min_aircraft']).sum())),
    'sm_cvt56_air': str(int(fs['aircraft'])), 'sm_cvt56_top': fs['largest filer'], 'sm_cvt56_top_n': str(int(fs['its aircraft'])),
    'sm_ch2_w1_n': str(winn['<= 2011']), 'sm_ch2_w2_n': str(winn['2012-15']),
    'sm_win_active_n': str(active), 'sm_win_active_share': pct(active / len(v)),
    'sm_z_core_n': str(len(core)), 'sm_z_core_share': pct(core['share 2016-23'].sum()),
    'sm_z_half_1619': str(half['2016-19'] + 1), 'sm_z_half_2023': str(half['2020-23'] + 1),
    'sm_cu_top_2023_share': pct(top_share),
    'sm_disc_a0_after': str(int(a0['aircraft'].max() - hit['aircraft'])),
    'sm_disc_a1t_new100': f"{ei.loc['A1t', 'new in the last 100 aircraft']:.1f}", 'sm_disc_a1t_exp100': f"{ei.loc['A1t', 'new in the last 100, random order']:.1f}",
}
numbers_check(N3)
print('also quoted in the text of 2.3 (not in the document\'s number list): rim', len(rim), 'archetypes,', pct(rim['share 2016-23'].sum()), 'of the 2016-23 aircraft;',
      '12th class at aircraft', int(hit['aircraft']), '(priority', int(hit['priority year reached']), '); C·U new in the last 100:', f"{ei.loc['A0c', 'new in the last 100 aircraft']:.1f}",
      'against', f"{ei.loc['A0c', 'new in the last 100, random order']:.1f}", ';', int(ei.loc['A1t', 'archetypes observed']), 'of', f"{ei.loc['A1t', 'Chao1']:.1f}", 'at C·W·T (', pct(ei.loc['A1t', 'share of richness found']), ');',
      'zones:', zones['zone'].value_counts().to_dict())""")

# ------------------------------------------------------------------------------------------ overview
md("""## Overview: what matched

Every number the document quotes for chapter 2 (46) and every table, with the differences labelled.""")
code(r"""allnum = pd.concat(NUMBERS, ignore_index=True)
n_doc = len(checks.reference_numbers('2'))
missing = checks.missing_numbers(dict.fromkeys(allnum['name']), '2')
print(f"numbers: {int((allnum['match'] == 'yes').sum())} of {len(allnum)} match the document; "
      f"{int(allnum['match'].str.startswith('expected').sum())} expected differences; {int((allnum['match'] == 'NO').sum())} failures; "
      f"{len(missing)} of the document's {n_doc} not computed here: {missing}")
overview = pd.DataFrame([c.iloc[0].to_dict() for c in CHECKS])
overview""")
code(r"""assert (allnum['match'] != 'NO').all(), allnum[allnum['match'] == 'NO']
assert not missing
assert (overview['differences'] == 0).all(), overview[overview['differences'] > 0]""")


nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, OUT)
print("written", OUT, len(cells), "cells")
if "--run" in sys.argv:
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=1800", str(OUT)], check=True, cwd=str(OUT.parent))
