"""Extended Abstract versions of Figs 4.9 (architecture shares), 4.11 (the three conditions on F) and 4.15 (architecture centres)
(author 2026-10-28/29): the IST two-column template, 160 mm text width, 78 mm column, every text at 8 pt or more at the printed width
(in-plot labels at 7 pt where 8 pt does not fit). Same data, colours, markers and labels as the dissertation builders
(thesis_v2_part3.fig_architecture_shares_by_cohort, thesis_v2_part3.fig_family_conditions, thesis_latex_part4.fig_centres5); only
the layout and the font sizes change. Written to LaTeX_v16/Figures/Extended_Abstract/ as vector PDF with the fonts embedded."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.text import Text

from viz import thesis_q6 as q6
from viz import thesis_latex_part4 as l4
from viz import thesis_v2_part3 as v2
from viz.thesis_latex_common import root

ts = v2.ts
MM = 1 / 25.4
COL_W, TEXT_W = 78 * MM, 160 * MM
PT, IN_PLOT = 8.0, 7.0                     # axis titles, ticks, legends / labels inside the plot where 8 pt does not fit
RC = {**ts.RC, "font.size": PT, "axes.labelsize": PT, "axes.titlesize": PT, "xtick.labelsize": PT, "ytick.labelsize": PT,
      "legend.fontsize": PT, "savefig.bbox": "standard", "pdf.fonttype": 42}
#: the two long end labels of Fig 4.9 on two lines (the words kept), so the panel keeps its width at 78 mm
WRAP = {"SLC": "Separate\nLift + Cruise", "CVT": "Combined\nVectored Thrust"}
OPEN_NOTE = f"open marker = {ts.FEW_MAX} designs or fewer, or 2024–26 (incomplete)"


def out_dir(cfg) -> Path:
    return root(cfg).parent / "LaTeX_v16" / "Figures" / "Extended_Abstract"


def _letter(ax, s, x=-0.22):
    """Panel letter at the top left of the panel, above the axes (a left title, so the constrained layout keeps room for it)."""
    ax.set_title(s, loc="left", x=x, fontsize=PT, fontweight="bold", pad=7)


# ---- centres (Fig 4.15)
def centres(sf, ctx):
    """Fig 4.15 in a (sub)figure ``sf``: the centre of SLC, TP and CVT per cohort, arrows cohort to cohort; the key in rows under it."""
    dw, wins = q6._data(ctx)["dw5"], l4._wins(ctx)
    k = len(wins) - 1
    ax = sf.subplots()
    pts = []
    for c in l4.ARCH3:
        col, mk = l4.TS_COL[c], l4.TS_MARK[c]
        d = dw[dw["code"] == c].set_index("window").reindex(wins)
        xs, ys, nd = d["tilting sets (mean)"].to_numpy(float), d["propulsive units (median)"].to_numpy(float), d["aircraft"].to_numpy(float)
        for i in range(k):
            if not (np.isfinite(xs[i]) and np.isfinite(ys[i])):
                continue
            ax.plot(xs[i], ys[i], marker=mk, ms=5.0, mfc="white" if ts.is_few(nd[i]) else col, mec=col, mew=1.0, ls="none", zorder=4)
            j = i + 1
            if j < k and np.isfinite(xs[j]) and np.isfinite(ys[j]):
                ax.annotate("", xy=(xs[j], ys[j]), xytext=(xs[i], ys[i]), zorder=3,
                            arrowprops=dict(arrowstyle="->", color=col, lw=1.0, shrinkA=4, shrinkB=4, alpha=0.45 if ts.is_few(nd[j]) else 1.0))
            pts.append((c, i, xs[i], ys[i]))
        if np.isfinite(xs[k]) and np.isfinite(ys[k]):
            ax.plot(xs[k], ys[k], marker=mk, ms=6.2, mfc="none", mec=col, mew=0.9, alpha=ts.INCOMPLETE_ALPHA, ls="none", zorder=5)
            pts.append((c, k, xs[k], ys[k]))
    for c, i, x, y in pts:                                       # the placement rule of fig_centres5
        same = [(cc, ii, xx, yy) for cc, ii, xx, yy in pts if (cc, ii) != (c, i) and cc == c]
        off, ha, va = ((5, -3), "left", "top") if i == k else ((5, 0), "left", "center")
        if i < k:
            twin = [ii for _, ii, xx, yy in same if ii < k and abs(xx - x) < 0.08 and abs(yy - y) < 0.3]
            if twin:
                off, va = ((5, -4), "top") if i < twin[0] else ((5, 4), "bottom")
            elif any(ii == k and abs(xx - x) < 0.05 and abs(yy - y) < 0.3 for _, ii, xx, yy in same) or \
                    any(ii < k and abs(yy - y) < 0.3 and 0 < xx - x < 0.35 for _, ii, xx, yy in same):
                off, ha = (-5, 0), "right"
        ax.annotate(l4.CENTRE_TAG[i], (x, y), textcoords="offset points", xytext=off, ha=ha, va=va, fontsize=IN_PLOT,
                    color=l4.TS_COL[c], alpha=ts.INCOMPLETE_ALPHA if i == k else 1.0, zorder=6)
    ax.set_xlim(-0.4, 2.95)
    ax.set_ylim(0, 11.0)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.set_xlabel("tilting sets per design (mean)")
    ax.set_ylabel("propulsors per design (median)")
    h = [Line2D([], [], color=l4.TS_COL[c], marker=l4.TS_MARK[c], ms=4.0, lw=1.0) for c in l4.ARCH3]
    names = [ts.ARCH_NAME["TP" if c == "TR" else c] for c in l4.ARCH3]
    order = [0, 2, 1]                                              # fig.legend fills columns: row 1 = SLC TP, row 2 = CVT
    sf.legend([h[i] for i in order], [names[i] for i in order], loc="outside lower center", ncol=2, frameon=False,
              handlelength=1.6, columnspacing=1.0, handletextpad=0.5, labelspacing=0.25, borderaxespad=1.4)
    sf.text(0.5, 0.0, OPEN_NOTE, ha="center", va="bottom", fontsize=PT, color=ts.NOTE)
    data = dw[dw["code"].isin(l4.ARCH3)][["class", "window", "aircraft", "tilting sets (mean)", "propulsive units (median)"]]
    return ax, l4._csv_cohorts(data.reset_index(drop=True))


# ---- shares (Fig 4.9)
def shares(sf, ctx):
    """Fig 4.9 in a (sub)figure ``sf``: each architecture's share of the cohort, labels at the right end of the lines, n under the ticks;
    no legend box (the open 2024-26 marker is named in the tick's asterisk and in the caption)."""
    d = q6._data(ctx)
    n_win = d["n_win"]
    share, _, _ = v2.joined_shares(ctx)
    codes = list(share.columns)
    big = ("SLC", "TR", "CVT")
    ax = sf.subplots()
    n = len(share)
    x = np.arange(n)
    last_v = share.iloc[-1].to_numpy(dtype=float) * 100
    groups, dodge = {}, {}
    for c, yv in zip(codes, last_v):
        key = next((g for g in groups if abs(g - yv) < 0.6), yv)
        groups.setdefault(key, []).append(c)
    for members in groups.values():
        for i, c in enumerate(members):
            dodge[c] = ((len(members) - 1) / 2 - i) * v2.DODGE
    for c in codes[::-1]:
        col = ts.ARCH[v2.TS_CODE.get(c, c)]
        y = share[c].to_numpy(dtype=float) * 100
        main = c in big
        ax.plot(x[:-1], y[:-1], marker="o", color=col, linewidth=1.6 if main else 0.8, markersize=3.2 if main else 2.2,
                alpha=1.0 if main else 0.6, zorder=4 if main else 3)
        ts.incomplete_point(ax, x[-1] + dodge[c], y[-1], col, markersize=3.2 if main else 2.4, zorder=4)
    top = float(np.ceil(share.to_numpy().max() * 100 / 5) * 5 + 2)
    ax.set_ylim(0, top)
    ax.set_xlim(-0.3, n - 1 + 0.3)
    ax.set_xticks(x, [f"{t}\nn {int(m)}" for t, m in zip(l4.CENTRE_TAG, n_win)])   # the short cohort tags of Fig 4.15 (the full ones
    #                                                                                  do not fit 78 mm); n under each
    ax.set_ylabel("share of all designs (%)")
    ax.set_xlabel(ts.COHORT_X)
    v2._grid(ax)
    sf.canvas.draw()
    gap = abs(ax.transData.inverted().transform((0, 0))[1] - ax.transData.inverted().transform((0, 8.4 * sf.dpi / 72))[1])
    big_gap = {c: 1.9 if v2.TS_CODE.get(c, c) in WRAP else 1.0 for c in codes}
    pos = _spread_var(last_v, [gap * big_gap[c] for c in codes], 0.6, top - 0.5)
    xl = n - 1 + 0.38
    for c, yv, yp in zip(codes, last_v, pos):
        k = v2.TS_CODE.get(c, c)
        col = ts.ARCH[k]
        main = c in big
        ax.plot([n - 1 + dodge[c] + 0.07, xl - 0.06], [yv, yp], color=col, linewidth=0.5, alpha=1.0 if main else 0.7, zorder=2)
        ax.text(xl, yp, WRAP.get(k, ts.ARCH_NAME[k] if k != "Other" else "Other"), color=col, ha="left", va="center", fontsize=IN_PLOT, linespacing=0.95,
                fontweight="bold" if main else "normal", clip_on=False)
    return ax, share.round(4).assign(designs=n_win)


def _spread_var(ys, gaps, lo, hi):
    """v2._spread with a gap per label: label i sits at least (gap_i + gap_j) / 2 from its neighbour j."""
    ys, g = np.asarray(ys, float), np.asarray(gaps, float)
    o = np.argsort(ys, kind="stable")
    p, go = ys[o].copy(), g[o]
    p[0] = max(p[0], lo + go[0] / 2 - g.min() / 2)
    for i in range(1, len(p)):
        p[i] = max(p[i], p[i - 1] + (go[i] + go[i - 1]) / 2)
    p[-1] = min(p[-1], hi)
    for i in range(len(p) - 2, -1, -1):
        p[i] = min(p[i], p[i + 1] - (go[i] + go[i + 1]) / 2)
    out = np.empty_like(p)
    out[o] = p
    return out


# ---- the three conditions on F (Fig 4.11)
def family_conditions(fig, ctx):
    """Fig 4.11 at 160 x 60 mm: the panel titles dropped (they repeat the y labels), the letters at the top left, each panel's test under
    its x label, the key in two rows under the panels. Values from thesis_v2_part3.fig_family_conditions (panel c: actively protected
    against the all-designs baseline and band)."""
    from lib import dominant_design as _dd
    f0, data = v2.fig_family_conditions(ctx)
    plt.close(f0)
    win, col = ctx.WIN_NAMES, ts.ARCH["F"]
    bases = (("all designs", False, 0.0), ("actively protected", True, 0.14))
    a1, a2, a3 = fig.subplots(1, 3)
    p1 = data[data["panel"] == "(a) condition 1"]
    for base, dashed, _ in bases:
        s = p1[(p1["base"] == base) & p1["drawn"]]
        yrs, y = s["year / cohort"].astype(int).to_numpy(), s["value"].to_numpy(float) * 100
        look = dict(linestyle="--", markerfacecolor="white", markeredgewidth=0.8) if dashed else dict(linestyle="-")
        a1.plot(yrs, y, marker="o", color=col, markeredgecolor=col, zorder=3 if dashed else 4, **look)
        for yr in sorted(_dd.condition1_years(pd.DataFrame({"priority year": yrs, "read": True, "above 50 %": y > 50}))):
            yy = y[list(yrs).index(yr)]
            if dashed:
                a1.plot(yr, yy, "o", markersize=4.6, markerfacecolor="white", markeredgecolor=ts.HIGHLIGHT, markeredgewidth=1.1, zorder=6)
            else:
                a1.plot(yr, yy, "o", markersize=4.6, color=ts.HIGHLIGHT, zorder=6)
    s_all = p1[(p1["base"] == "all designs") & p1["drawn"]]
    for yr, sh in zip(s_all["year / cohort"].astype(int), s_all["value"].astype(float)):
        if sh > 0.5:                                                 # under the lines, a leader up to the solid marker (as Fig 4.11)
            a1.annotate(f"{100 * sh:.1f}{ts.THIN}%", (yr, 100 * sh), xytext=(yr, v2.LABEL_Y), textcoords="data", ha="center", va="top",
                        fontsize=PT, color=col, arrowprops=dict(arrowstyle="-", color=col, lw=0.6, shrinkA=1, shrinkB=3))
    a1.axhline(50, color=v2.REF, linewidth=0.8, linestyle=(0, (4, 2)), zorder=2)
    yrs_all = sorted(p1["year / cohort"].astype(int).unique())
    a1.text(yrs_all[0] - 0.4, 51, f"50{ts.THIN}% threshold", ha="left", va="bottom", fontsize=PT, color=v2.REF)
    a1.set_xlim(yrs_all[0] - 0.5, yrs_all[-1] + 0.5)
    a1.set_xticks(yrs_all, [str(y) if (y - yrs_all[0]) % 2 == 0 else "" for y in yrs_all])
    a1.set_ylim(0, 75)
    a1.set_yticks([0, 20, 40, 60])
    a1.set_ylabel("share of designs in F (%)")
    a1.set_xlabel(f"priority year\nmet above 50{ts.THIN}% in two consecutive years")
    v2._grid(a1)
    for ax, panel, whisk in ((a2, "(b) condition 2", True), (a3, "(c) condition 3", False)):
        p = data[data["panel"] == panel]
        for base, dashed, dx in bases:
            s = p[p["base"] == base].set_index("year / cohort").reindex(win)
            v2._band_series(ax, s["value"], s["band low"], s["band high"], col, wlo=s["whisker low"] if whisk and not dashed else None,
                            whi=s["whisker high"] if whisk and not dashed else None, met=s["met"].astype(bool).tolist(), dashed=dashed, dx=dx,
                            band=not dashed)
        ax.set_xlabel(f"{ts.COHORT_X}\nmet below the band")
    a2.set_ylim(0, float(np.nanmax(data.loc[data["panel"] == "(b) condition 2", ["value", "band high", "whisker high"]].to_numpy(float))) * 1.12)
    a2.set_ylabel("²D of F")
    a3.axhline(0, color=v2.REF, linewidth=0.5, zorder=2)
    a3.set_ylabel("ΔQ of F against the\ntwo earliest cohorts")
    for ax in (a2, a3):
        ax.set_xticks(np.arange(len(win)), l4.CENTRE_TAG, rotation=30, ha="right", rotation_mode="anchor")   # short tags, turned as
        #                                                                       ts.fit_cohort_ticks does where a panel is too narrow
    h = [Line2D([], [], color=col, marker="o"),
         Line2D([], [], color=col, marker="o", linestyle="--", markerfacecolor="white", markeredgewidth=0.8),
         mpl.patches.Patch(facecolor=ts.BAND, edgecolor="none"),
         Line2D([], [], marker="o", color=ts.HIGHLIGHT, linestyle="none", markersize=4.6),
         Line2D([], [], linestyle="none")]
    lab = ["all designs", "actively protected designs", f"95{ts.THIN}% permutation band", "condition met", ts.INCOMPLETE_FOOTNOTE]
    order = [0, 3, 1, 4, 2]                                         # fig.legend fills columns: row 1 = 0 1 2, row 2 = 3 4
    leg = fig.legend([h[i] for i in order], [lab[i] for i in order], loc="outside lower center", ncol=3, frameon=False,
                     handlelength=1.6, columnspacing=1.2, handletextpad=0.5, labelspacing=0.25)
    leg.get_texts()[order.index(4)].set_color(ts.NOTE)
    return (a1, a2, a3), data


# ---- the writer
def _smallest(fig) -> float:
    return min(t.get_fontsize() for t in fig.findobj(Text) if t.get_text().strip() and t.get_visible())


def _clipped(fig) -> int:
    """Texts that run past the canvas."""
    fig.canvas.draw()
    r, W, H = fig.canvas.get_renderer(), fig.bbox.width, fig.bbox.height
    n = 0
    for t in fig.findobj(Text):
        if t.get_text().strip() and t.get_visible():
            b = t.get_window_extent(r)
            n += int(b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > W + 0.5 or b.y1 > H + 0.5)
    return n


def build(ctx, cfg) -> pd.DataFrame:
    """Write the four Extended Abstract PDFs (and a 300 dpi PNG beside each for checking); return their size and smallest font."""
    out = out_dir(cfg)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with mpl.rc_context(RC):
        jobs = {
            "ea_centres_and_shares": (TEXT_W, 70 * MM, "pair"),
            "ea_centres_1col": (COL_W, 65 * MM, centres),
            "ea_shares_1col": (COL_W, 65 * MM, shares),
            "ea_family_conditions": (TEXT_W, 60 * MM, family_conditions),
        }
        for name, (w, h, how) in jobs.items():
            fig = plt.figure(figsize=(w, h), layout="constrained")
            if how == "pair":
                sa, sb = fig.subfigures(1, 2, wspace=0.02)
                axa, _ = centres(sa, ctx)
                axb, _ = shares(sb, ctx)
                fig.canvas.draw()
                _letter(axa, "(a)", -0.12); _letter(axb, "(b)", -0.2)
            elif how is family_conditions:
                axs, _ = how(fig, ctx)
                fig.canvas.draw()
                for ax, s in zip(axs, ("(a)", "(b)", "(c)")):
                    _letter(ax, s, -0.2)
            else:
                ax, _ = how(fig, ctx)
                _letter(ax, "", 0)
            fig.canvas.draw()
            fig.savefig(out / f"{name}.pdf")
            fig.savefig(out / f"{name}.png", dpi=300)
            rows.append({"file": f"{name}.pdf", "width mm": round(fig.get_figwidth() / MM, 1), "height mm": round(fig.get_figheight() / MM, 1),
                         "smallest font pt": _smallest(fig), "texts past the edge": _clipped(fig)})
            plt.close(fig)
    return pd.DataFrame(rows)
