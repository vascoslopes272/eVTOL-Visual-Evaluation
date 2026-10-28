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
              Exception (author 2026-10-28, legends pass): bottom_legend(rows=2) allows two rows for the figures of that
              pass, which also name their test under the panel label (panel_label(note=...)) and end with a footnote line.
  Colour     one colour per category, identical in every figure (dicts below):
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
#: the footnote line under the bottom legend wherever the asterisk appears (author 2026-10-28)
INCOMPLETE_FOOTNOTE = '* 2024–26 incomplete cohort, not tested'
#: the thin space before % ("95 %"): Nimbus Sans has no U+2009, so it is the mathtext \, (same line height)
THIN = r'$\,$'
NOTE = '#555555'                           # grey of the notes under the panel labels and of the footnote line


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


def panel_label(ax, text, color=None, note=None):
    """The panel label "(a) short title" (author 2026-10-23: at the bottom of every panel, centred under the x tick labels, axis-label
    size, nothing at the top). Recorded here, written by place_panel_labels (ts.save calls it), which puts it in the x-label slot under
    the panel's own x label, so constrained layout makes room for it. ``note`` (author 2026-10-28): lines directly under the label,
    same size, NOTE grey, e.g. the test of the panel in words."""
    for loc in ('left', 'center', 'right'):
        ax.set_title('', loc=loc)
    ax._ts_panel = (text, color)
    ax._ts_note = note


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
        n_note = max((len(a._ts_note.split('\n')) if getattr(a, '_ts_note', None) else 0) for a in row)
        for a in row:
            own = a._ts_own_xlabel.split('\n') if a._ts_own_xlabel else []
            text, color = a._ts_panel
            shared = getattr(a, '_ts_shared', None)
            assert not (n_note and shared), 'a note under the panel label and a shared x label in one row'
            # the note: blank lines in the x label hold its room in the layout; the grey text is drawn over them, anchored at the
            # bottom of the label, so its first line sits right under the panel label (a panel without a note keeps no blank lines;
            # the labels of a row are top-aligned, batch 4 2026-10-28)
            note = getattr(a, '_ts_note', None)
            k_note = len(note.split('\n')) if note else 0
            lines = own + [' '] * (n_own - len(own)) + text.split('\n') + [' '] * k_note + (shared.split('\n') if shared else [])
            a.set_xlabel('\n'.join(lines), ha='center', linespacing=1.25, **({'color': color} if color and not own and not shared else {}))
            if k_note:
                body = note
                art = getattr(a, '_ts_note_art', None)
                if art is None:
                    art = a.annotate(body, xy=(0.5, 0), xycoords=a.xaxis.label, ha='center', va='bottom', linespacing=1.25,
                                     fontsize=a.xaxis.label.get_fontsize(), color=NOTE, annotation_clip=False)
                    art.set_in_layout(False)
                    a._ts_note_art = art
                art.set_text(body)
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


def bottom_legend(fig, handles=None, labels=None, ncol=None, rows=1, footnote=None, **kw):
    """The only legend form allowed: one row, bottom of the figure, no frame. ``rows=2`` only for the figures of the 2026-10-28 legends
    pass (author); the entries fill column by column, so the reading order is down each column. ``footnote``: one NOTE-grey line under
    the entries (e.g. INCOMPLETE_FOOTNOTE), drawn over a blank last row so constrained layout makes room for it. ``kw`` goes to fig.legend."""
    from matplotlib.lines import Line2D
    assert rows in (1, 2), 'a bottom legend has one row, two in the 2026-10-28 legends pass'
    h, l = (handles, labels) if handles else fig.axes[0].get_legend_handles_labels()
    h, l = list(h), list(l)
    nc = ncol or -(-len(l) // rows)
    if footnote:
        per = -(-len(l) // nc)                     # entries per column, then one blank row under every column
        blank = lambda: Line2D([], [], linestyle='none')   # noqa: E731
        hh, ll = [], []
        for c in range(nc):
            col_h, col_l = h[c * per:(c + 1) * per], l[c * per:(c + 1) * per]
            k = per + 1 - len(col_h)
            hh += col_h + [blank() for _ in range(k)]
            ll += col_l + [' '] * k
        h, l = hh, ll
    leg = fig.legend(h, l, **{**dict(loc='outside lower center', ncol=nc, frameon=False, handlelength=1.6, columnspacing=1.2), **kw})
    if footnote:
        from matplotlib.text import Annotation
        fs = leg.get_texts()[0].get_fontsize()
        fig._ts_footnote = fig.add_artist(Annotation(footnote, xy=(0.5, 0), xycoords=leg, xytext=(0, leg.borderpad * fs),
                                                     textcoords='offset points', ha='center', va='bottom', fontsize=fs, color=NOTE,
                                                     annotation_clip=False))
        fig._ts_footnote.set_in_layout(False)
    return leg


def compact_legend(target, handles, labels, footnote=None, breaks=(), bare=(), loc='outside lower center', width_in=None,
                   colsep=1.0, keyline=None, **kw):
    """Legends pass, batch 4 (author 2026-10-28): the key laid out in rows across the page width instead of one entry per line.
    The entries keep their order and fill a row while they fit the width (``width_in``, the page width by default); ``breaks`` = entry
    indices that must start a new row. ``bare`` = entry indices drawn without a handle (a note such as "x axis, ..."). ``footnote`` (e.g.
    INCOMPLETE_FOOTNOTE) ends the last row, NOTE grey, right-aligned with the widest row; it starts a row of its own only when it does not
    fit. ``keyline``: a NOTE-grey line of its own, centred under the rows (the key of the point labels). ``target`` is the figure (a bottom legend, constrained layout makes room) or a key axes (loc 'upper center'). Returns the
    legend; ``legend._ts_rows`` = the labels of each row, for the report."""
    from matplotlib.offsetbox import DrawingArea, HPacker, TextArea, VPacker
    fig = target if hasattr(target, 'add_axes') and not hasattr(target, 'transData') else target.figure
    kw = {**dict(frameon=False, handlelength=1.6, handletextpad=0.5, borderaxespad=0.5), **kw}
    if loc != 'outside lower center' and 'bbox_to_anchor' not in kw:
        kw['bbox_to_anchor'] = (0.5, 1.0)
    leg = target.legend(list(handles), list(labels), loc=loc, ncol=len(labels), **kw)
    fs = leg.get_texts()[0].get_fontsize()
    entries = [col.get_children()[0] for col in leg._legend_handle_box.get_children()]
    for i in bare:                                          # no handle and no gap before the text
        entries[i].get_children()[0].width, entries[i].sep = 0, 0
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    pt = rend.points_to_pixels(1.0)
    wid = [e.get_bbox(rend).width / pt for e in entries]
    avail = (width_in or fig.get_figwidth()) * 72 - 2 * (leg.borderpad + leg.borderaxespad) * fs - 4
    sep = colsep * fs
    rows, cur, w = [], [], 0.0
    for i, (e, x) in enumerate(zip(entries, wid)):
        if cur and (i in breaks or w + sep + x > avail):
            rows.append((cur, w))
            cur, w = [], 0.0
        w = x if not cur else w + sep + x
        cur.append(i)
    rows.append((cur, w))
    boxes = []
    if footnote:
        fn = TextArea(footnote, textprops=dict(color=NOTE, fontsize=fs))
        fn.set_figure(fig)
        fn_w = fn.get_bbox(rend).width / pt
        widest = max(r[1] for r in rows)
        last, lw = rows[-1]
        if lw + sep + fn_w > avail:                         # does not fit the last row: a row of its own, right-aligned
            rows.append(([], 0.0))
            last, lw = [], 0.0
        full = max(widest, lw + sep + fn_w)
        gap = full - lw - fn_w if last else full - fn_w
    for k, (idx, w) in enumerate(rows):
        kids = [entries[i] for i in idx]
        if footnote and k == len(rows) - 1:
            kids = kids + [DrawingArea(max(gap - (sep if kids else 0), 0), 1), fn]
        boxes.append(HPacker(children=kids, sep=sep, pad=0, align='center'))
    if keyline:
        boxes.append(TextArea(keyline, textprops=dict(color=NOTE, fontsize=fs)))
    box = VPacker(children=boxes, sep=leg.labelspacing * fs, pad=0, align='center')
    leg._legend_box._children = [leg._legend_title_box, box]
    leg._legend_handle_box = box
    leg._legend_box.set_figure(fig)
    leg._ts_rows = [[leg.get_texts()[i].get_text() for i in r[0]] + ([footnote] if footnote and k == len(rows) - 1 else [])
                    for k, r in enumerate(rows)]
    return leg


def label_end(ax, x, y, text, color, dx=.12, dy=0, **kw):
    """Direct label at the end of a line (8.4 pt)."""
    return ax.text(x + dx, y + dy, text, color=color, va='center', ha='left', fontsize=8.4, **kw)


def incomplete_point(ax, x, y, color, marker='o', **kw):
    """2024-26: hollow, faded, never joined to the complete series."""
    return ax.plot(x, y, marker, mfc='white', mec=color, mew=.8, alpha=INCOMPLETE_ALPHA, ls='none', **kw)
