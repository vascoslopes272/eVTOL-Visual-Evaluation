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
  Panels      labels "(a) short title" UNDER the panel, centred below the x tick labels (and the panel's
              own x label), axis-label size; nothing at the top (panel_label + place_panel_labels, 2026-10-23).
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
  Cohorts     labels exactly: <= 2011, 2012-15, 2016-19, 2020-23, 2024-26* (asterisk restored, author 2026-10-23)  (en dash), ONE line; rotated 30 deg
              (fit_cohort_ticks) when a panel is too narrow. x label 'priority-year cohort' / 'priority year'.
  Bases       the y label (or a note top-left) names the base: all designs / actively protected designs /
              designs of the architecture / VFS directory aircraft (2026-10-23).
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
COHORTS = ['≤ 2011', '2012–15', '2016–19', '2020–23', '2024–26*']
#: author 2026-10-23: cohort ticks on ONE line everywhere (the two-line form was hard to read); where a panel is too narrow,
#: fit_cohort_ticks rotates them by 30 degrees. The old name is kept so every builder picks up the one-line form.
COHORTS_2L = COHORTS
COHORT_X = 'priority-year cohort'          # x label of every cohort chart
#: the two marks the whole dissertation uses one way (author 2026-10-23): a hollow marker = a cohort with FEW_MAX designs or fewer
#: (of the series drawn: architecture, region, ...); the incomplete 2024-26 cohort = the asterisk on its label, both named in the legend
FEW_MAX = 20
HOLLOW_LABEL = f'hollow marker: cohort with {FEW_MAX} designs or fewer'
INCOMPLETE_LABEL = '* incomplete cohort, not tested'
INCOMPLETE_YEAR_LABEL = '* incomplete year, not tested'   # the same mark for the yearly figures (4.2, 4.3, investment)


def is_few(n) -> bool:
    """The hollow-marker rule: a cohort with FEW_MAX designs or fewer (n = the designs of the series in that cohort)."""
    return n is not None and n == n and n <= FEW_MAX


def hollow_handle(color='#555555', marker='o'):
    """Legend entry for the hollow-marker rule."""
    from matplotlib.lines import Line2D
    return Line2D([], [], marker=marker, ms=4.2, mfc='white', mec=color, color=color, ls='none', label=HOLLOW_LABEL)


def incomplete_handle(color='#555555', marker='o'):
    """Legend entry for the incomplete 2024-26 cohort: its hollow light marker, labelled with the asterisk rule."""
    from matplotlib.lines import Line2D
    return Line2D([], [], marker=marker, ms=4.2, mfc='white', mec=color, color=color, ls='none', alpha=INCOMPLETE_ALPHA,
                  label=INCOMPLETE_LABEL)
YEAR_X = 'priority year'                   # x label of every yearly chart

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
    fit_cohort_ticks(fig)
    place_panel_labels(fig)
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


def shared_xlabel(ax, text):
    """An x label that names the axis of the whole row (set on one panel): written UNDER the row of panel labels, not between the
    ticks and the panel label."""
    ax._ts_shared = text


def panel_label(ax, text, color=None):
    """The panel label "(a) short title" (author 2026-10-23: at the bottom of every panel, centred under the x tick labels, axis-label
    size, nothing at the top). Recorded here, written by place_panel_labels (ts.save calls it), which puts it in the x-label slot under
    the panel's own x label, so constrained layout makes room for it."""
    for loc in ('left', 'center', 'right'):
        ax.set_title('', loc=loc)
    ax._ts_panel = (text, color)


def place_panel_labels(fig):
    """Write every recorded panel label as the last lines of its axes' x label. Panels of one row get the same number of lines above
    the label (blank where a panel has no x label of its own), so the labels of a row sit on one line. Safe to call more than once."""
    axs = [a for a in fig.axes if getattr(a, '_ts_panel', None)]
    if not axs:
        return
    for a in axs:
        if not hasattr(a, '_ts_own_xlabel') or a.get_xlabel() != getattr(a, '_ts_done', None):
            a._ts_own_xlabel = a.get_xlabel()          # the panel's own x label, set by the builder
    rows = {}
    for a in axs:
        ss = a.get_subplotspec()
        key = (id(ss.get_gridspec()), ss.rowspan.stop) if ss is not None else round(a.get_position().y0, 2)
        rows.setdefault(key, []).append(a)
    for row in rows.values():
        n_own = max((len(a._ts_own_xlabel.split('\n')) if a._ts_own_xlabel else 0) for a in row)
        for a in row:
            own = a._ts_own_xlabel.split('\n') if a._ts_own_xlabel else []
            text, color = a._ts_panel
            shared = getattr(a, '_ts_shared', None)
            lines = own + [' '] * (n_own - len(own)) + text.split('\n') + (shared.split('\n') if shared else [])
            a.set_xlabel('\n'.join(lines), ha='center', linespacing=1.25, **({'color': color} if color and not own and not shared else {}))
            # centred under the drawn x axis: a figure that keeps room right of the data for end labels shortens the bottom spine
            b = a.spines['bottom'].get_bounds()
            x0, x1 = a.get_xlim()
            a.xaxis.label.set_x(((b[0] + b[1]) / 2 - x0) / (x1 - x0) if b and x1 != x0 else 0.5)
            a._ts_done = a.get_xlabel()
        fig.align_xlabels(row)


def fit_cohort_ticks(fig, rotation=30):
    """Cohort ticks stay on one line; on an axes where two neighbouring tick labels would touch, rotate them by ``rotation``
    degrees (anchored at their right end). Called by ts.save; safe to call more than once."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    for ax in fig.axes:
        labs = [t for t in ax.get_xticklabels() if t.get_visible() and t.get_text().strip()]
        if len(labs) < 2 or not any(t.get_text() in COHORTS for t in labs):
            continue
        if any(t.get_rotation() for t in labs):
            continue
        boxes = sorted((t.get_window_extent(rend) for t in labs), key=lambda b: b.x0)
        if any(b1.x0 - b0.x1 < 2 for b0, b1 in zip(boxes, boxes[1:])):
            for t in ax.get_xticklabels():
                t.set_rotation(rotation)
                t.set_ha('right')
                t.set_rotation_mode('anchor')
    fig.canvas.draw()


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
