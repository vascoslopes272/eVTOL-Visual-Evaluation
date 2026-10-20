"""thesis_style.py - one figure style for every data plot of the dissertation.

Import at the top of every notebook that makes a thesis figure:
    import thesis_style as ts
    ts.use()
    fig, ax = plt.subplots(figsize=(ts.TEXTWIDTH, ts.H_ROW), layout='constrained')
    ...
    ts.save(fig, 'fig4_09')          # writes fig4_09.pdf (vector) + .png (300 dpi) and checks the rules

RULES (apply in every figure)
  Page        width exactly TEXTWIDTH = 6.3 in (16 cm); included with width=\\textwidth, never rescaled.
              Height: one row of panels 2.1-2.6 in (H_ROW); two rows <= 3.0 in (H_TWO_ROWS).
  Text        Helvetica (TeX Gyre Heros / Arial), 9 pt labels and titles, 8.4 pt ticks,
              NOTHING below 8 pt (save() refuses it). Sentence case. Units in parentheses: "share (%)".
  Axes        left + bottom spines only, ticks out, no background colour, no shaded zones, no hatching.
  Panels      titles "(a) short title", left aligned, one line when possible.
  Labels      direct labels at line ends first. A legend only when direct labels do not fit:
              ONE row, at the BOTTOM of the figure, under the x-axis label and above the caption
              (fig.legend(loc='outside lower center')), no frame. Same place as the key of the
              method diagrams (Figs 3.10-3.14), so every key in the thesis sits below its graphic.
  Colour      one colour per category, identical in every figure (dicts below):
                architectures ARCH, directory categories VFS, regions REGION (+ REGION_MARKER),
                assignee types ATYPE. One colour per ANALYSIS for single-series figures:
                levels of description (A, A.W.T, A.U), D and configurations -> black, cohorts GREYS;
                family F -> ARCH['F']; directory -> VFS['Vectored Thrust']; assignees -> BLUES.
  Line style  all designs = solid + filled marker; actively protected = dashed + hollow marker;
              patent dataset = solid; VFS directory = dashed + hollow marker.
  Incomplete  2024-26 cohort / years: hollow marker or outline-only bar, same colour, alpha 0.6,
              NEVER joined by a line to 2020-23 / 2023. Mark the cohort label with '*'.
  Cohorts     labels exactly: <=2011, 2012-15, 2016-19, 2020-23, 2024-26*  (en dash).
  Highlight   'condition met' = HIGHLIGHT red; permutation / chance band = BAND light grey fill.
  Numbers     print only the values the text cites; n per cohort goes to the caption if it crowds.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import text as _mtext
from pathlib import Path

TEXTWIDTH = 6.3          # in, = 16 cm text width of the IST template
H_ROW = 2.25             # in, one row of panels (range 2.1-2.6)
H_TWO_ROWS = 3.0         # in, two rows of panels (maximum)
MIN_PT = 8.0             # IST rule for this thesis

ARCH = {
    'SLC': '#0072B2',    # Separate Lift + Cruise   blue
    'TP':  '#E69F00',    # Tilt Propulsor           orange
    'CVT': '#009E73',    # Combined Vectored Thrust green
    'TW':  '#D55E00',    # Tilt Wing                vermilion
    'MR':  '#56B4E9',    # Multicopter              sky blue
    'PTC': '#CC79A7',    # Pitch-to-Cruise          reddish purple
    'TF':  '#8C564B',    # Tilt Frame               brown
    'HB':  '#333333',    # Hoverbike                near-black
    'F':   '#005A8C',    # family F                 dark blue
    'Other': '#B0B0B0',
}
ARCH_NAME = {'SLC': 'Separate Lift + Cruise', 'TP': 'Tilt Propulsor', 'CVT': 'Combined Vectored Thrust',
             'TW': 'Tilt Wing', 'MR': 'Multicopter', 'PTC': 'Pitch-to-Cruise', 'TF': 'Tilt Frame',
             'HB': 'Hoverbike', 'F': 'family F', 'Other': 'other'}
VFS = {'Lift + Cruise': ARCH['SLC'], 'Vectored Thrust': ARCH['TP'], 'Wingless (Multicopter)': ARCH['MR'],
       'Electric Rotorcraft': '#8C564B', 'Hover Bikes / PFD': ARCH['HB']}
REGION = {'North America': '#3A2D7D', 'Europe': '#D6457F', 'Asia-Pacific': '#8DB33A'}  # dark / mid / light grey in b&w
REGION_MARKER = {'North America': 'o', 'Europe': 's', 'Asia-Pacific': '^'}
ATYPE = {'Company': '#0072B2', 'Individual inventor': '#9E9E9E', 'University / institute': '#CC79A7'}
SERIES = {'eVTOL': ARCH['SLC'], 'aeronautics': '#555555', 'transport': '#8A8A8A', 'all patents': '#B5B5B5'}
GREYS = ['#BDBDBD', '#969696', '#636363', '#252525', '#000000']   # cohorts, early -> late
BLUES = ['#C6DBEF', '#9ECAE1', '#6BAED6', '#3182BD', '#08519C']   # ordered groups, light -> dark
HIGHLIGHT = '#D62728'
BAND = '#E3E3E3'
NEUTRAL = '#BDBDBD'
INCOMPLETE_ALPHA = 0.6
COHORTS = ['≤2011', '2012–15', '2016–19', '2020–23', '2024–26*']
COHORTS_2L = ['≤\n2011', '2012\n–15', '2016\n–19', '2020\n–23', '2024\n–26*']

# Coordinator addition (2026-10-20): this machine has no TeX Gyre Heros / Helvetica / Arial, but it has Nimbus Sans
# (the URW Helvetica clone, same metrics) and Liberation Sans (Arial metrics). Use the first family that is installed,
# so the text never falls back to the wider DejaVu Sans, and point mathtext at the same family.
from matplotlib import font_manager as _fm
_FAMILIES = ['TeX Gyre Heros', 'Helvetica', 'Arial', 'Nimbus Sans', 'Liberation Sans', 'DejaVu Sans']
_HAVE = {f.name for f in _fm.fontManager.ttflist}
SANS = next(f for f in _FAMILIES if f in _HAVE or f == 'DejaVu Sans')

RC = {
    'font.family': [SANS],
    'mathtext.fontset': 'custom', 'mathtext.rm': SANS,
    'mathtext.it': f'{SANS}:italic', 'mathtext.bf': f'{SANS}:bold',
    'font.size': 9, 'axes.titlesize': 9, 'axes.labelsize': 9,
    'xtick.labelsize': 8.4, 'ytick.labelsize': 8.4, 'legend.fontsize': 8.4, 'legend.frameon': False,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': .5,
    'xtick.major.width': .5, 'ytick.major.width': .5, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
    'lines.linewidth': 1.2, 'lines.markersize': 3.5, 'axes.titlelocation': 'left',
    'savefig.dpi': 300, 'savefig.bbox': None, 'figure.dpi': 150, 'pdf.fonttype': 42,
    'axes.prop_cycle': mpl.cycler(color=list(ARCH.values())),
}


def use():
    mpl.rcParams.update(RC)


def save(fig, name, outdir='.'):
    """Check the rules, then write <name>.pdf (vector, for LaTeX) and <name>.png (300 dpi, for review)."""
    w = fig.get_size_inches()[0]
    assert abs(w - TEXTWIDTH) < 1e-3, f'{name}: width {w:.2f} in, must be {TEXTWIDTH}'
    fig.canvas.draw()
    small = sorted({round(t.get_fontsize(), 1) for t in fig.findobj(_mtext.Text)
                    if t.get_text().strip() and t.get_visible() and t.get_fontsize() < MIN_PT - 1e-6})
    assert not small, f'{name}: text below {MIN_PT} pt: {small}'
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    # bbox_inches=None explicitly (coordinator, 2026-10-20): viz.style sets savefig.bbox='tight' globally, which would crop the page
    fig.savefig(out / f'{name}.pdf', bbox_inches=None)
    fig.savefig(out / f'{name}.png', dpi=300, bbox_inches=None)


def bottom_legend(fig, handles=None, labels=None, ncol=None):
    """The only legend form allowed: one row, bottom of the figure, no frame."""
    h, l = (handles, labels) if handles else fig.axes[0].get_legend_handles_labels()
    return fig.legend(h, l, loc='outside lower center', ncol=ncol or len(l), frameon=False,
                      handlelength=1.6, columnspacing=1.2)


def label_end(ax, x, y, text, color, dx=.12, dy=0, **kw):
    """Direct label at the end of a line (8.4 pt)."""
    return ax.text(x + dx, y + dy, text, color=color, va='center', ha='left', fontsize=8.4, **kw)


def incomplete_point(ax, x, y, color, marker='o', **kw):
    """2024-26: hollow, faded, never joined to the complete series."""
    return ax.plot(x, y, marker, mfc='white', mec=color, mew=.8, alpha=INCOMPLETE_ALPHA, ls='none', **kw)
