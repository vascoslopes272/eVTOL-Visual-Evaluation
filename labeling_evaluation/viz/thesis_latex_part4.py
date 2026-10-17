"""Part IV hand-over to the dissertation (notebook 51, last section): q6_leading_layout_by_architecture (final width 1.0, three rows) and
q6_centroid_dispersion (leaves the dissertation) remade at their final width in the 16 cm text block, height at most 55 % of the width,
text 7 pt or more, no title inside; written to LaTeX_v15/Figures/Part_IV_design_space_evolution/<group>/<role>/ with the data behind each,
NUMBERS_IV.md and MANIFEST.md (appended). No number, test or result changes: the data are those of viz/thesis_q6.py and
viz/thesis_v2_part4.py; only the layout of the layout figure (three rows instead of three columns) is new."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.text import Text

from lib import drivers
from viz import figcheck, frames, plots, style
from viz import thesis_q6 as q6
from viz import thesis_v2_part4 as p4
from viz.thesis_latex_common import MAX_H, TEXT_CM, root, tables_md

MIN_PT = 7.0
PART = "Part_IV_design_space_evolution"
MIN_LABEL = 0.15            # a block prints its share from 15 % (a row is 0.7 in tall: 12 % would be under the 7 pt text height)
#: name -> (final width as a share of the text block, group, role, in the dissertation, what it shows)
FIGS = {
    "q6_leading_layout_by_architecture": (1.0, "IV1_layout_convergence", "main", True,
                                          "composition of Lift + Cruise, Tilt Propulsor and CVT over their layouts per cohort, one row each"),
    "q6_centroid_dispersion": (1.0, "IV3_centre_and_disparity", "main", False,
                               "distance of each cohort from the first and Rao's Q per cohort, with permutation bands (future work)"),
}


def fig_layout_rows(ctx):
    """The same data and blocks as q6.fig_leading_layout_by_class (pmix, DISPLAY, config_stack), three rows instead of three columns:
    one row per architecture, the bars on the left, the key of that row on the right."""
    d = q6._data(ctx)
    pmix = d["pmix5"]                                      # the five cohorts (refresh of 2026-10-16); equals pmix on the complete ones
    wins = list(ctx.WIN_NAMES)
    w = ctx.W
    fig, axs = plt.subplots(3, 2, figsize=(w, 3.4), gridspec_kw=dict(width_ratios=[1.0, 0.95], hspace=0.62, wspace=0.02))
    for (ax, kx), c in zip(axs, ["SLC", "TR", "CVT"]):
        m = pmix[pmix["code"] == c]
        lastw = m[m["window"] == "2020-23"].sort_values("aircraft", ascending=False)       # the leader and the stacking order: 2020-23, as before
        ordc = [k for k in lastw["configuration"] if not frames.cfg_outside(k)]
        keep = ordc[:3] if len(ordc) > 4 else ordc[:4]
        frac = lambda k: (m[m["configuration"].isin(k)].groupby("window")["aircraft"].sum().reindex(wins).fillna(0)
                          / m.groupby("window")["class aircraft"].first().reindex(wins))
        comp = pd.DataFrame({q6.DISPLAY[c](k): frac([k]) for k in keep})
        rest = frac([k for k in m["configuration"].unique() if k not in keep])
        if rest.sum() > 0:
            comp["other configurations"] = rest
        plots.config_stack(ax, comp, style.cls(c).color, n_few=2, min_label=MIN_LABEL)
        _fade_incomplete_column(ax, len(wins) - 1)
        nwin = m.groupby("window")["aircraft"].sum().reindex(wins)
        ax.set_xticks(range(len(wins)), [f"{COHORT_TICK[x]}\nn {int(n)}" + ("\n(incomplete)" if x == INCOMPLETE else "") for x, n in zip(wins, nwin)])
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_ylabel({"SLC": "Separate\nLift + Cruise", "TR": "Tilt\nPropulsor", "CVT": "Combined\nVectored Thrust"}[c])
        h, lab = ax.get_legend_handles_labels()
        kx.set_xticks([]), kx.set_yticks([])
        kx.axis("off")
        kx.legend(h[::-1], [p4._relabel(t) for t in lab[::-1]], loc="center left", fontsize=MIN_PT, handlelength=1.1, labelspacing=0.3, frameon=False,
                  title={"SLC": "where the lift units sit", "TR": "how the tilting thrust is split", "CVT": "what tilts · where the fixed units sit"}[c],
                  title_fontsize=MIN_PT, alignment="left")
    fig.subplots_adjust(left=0.125, right=0.995, top=0.985, bottom=0.125)     # room for the two-line architecture names and three-line cohort ticks
    return fig, _csv_cohorts(pmix.reset_index(drop=True))


def _draw(name, ctx):
    frac = FIGS[name][0]
    w_in = TEXT_CM / 2.54 * frac
    old = ctx.W
    ctx.W = w_in
    try:
        with plt.style.context(str(Path(p4.__file__).with_name("part1.mplstyle"))):
            if name == "q6_leading_layout_by_architecture":
                fig, data = fig_layout_rows(ctx)
                data = data.rename(columns=lambda c: p4._relabel(p4.COLUMNS.get(c, c)))
            else:
                fig, data = p4.fig_centroid_dispersion(ctx)
            for t in fig.findobj(Text):
                if t.get_text() and t.get_fontsize() < MIN_PT:
                    t.set_fontsize(MIN_PT)
            h = min(fig.get_figheight(), MAX_H * w_in)
            fig.set_size_inches(w_in, h)
            fig.canvas.draw()
            chk = (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, MIN_PT)))
    finally:
        ctx.W = old
    return fig, data, chk


def export(cfg, ctx):
    R = root(cfg)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    checks, manifest = [], []
    for name, (frac, group, role, used, shows) in FIGS.items():
        fig, data, chk = _draw(name, ctx)
        out = R / "Figures" / PART / group / role
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / f"{name}.pdf")
        checks.append({"figure": name, "width cm": round(fig.get_figwidth() * 2.54, 2), "height cm": round(fig.get_figheight() * 2.54, 2),
                       "height / width": round(fig.get_figheight() / fig.get_figwidth(), 3), "text over text": chk[0], "under 7 pt": chk[1]})
        plt.close(fig)
        data.to_csv(csvd / f"{name}.csv", index=False)
        manifest += [(f"Figures/{PART}/{group}/{role}/{name}.pdf", used, shows), (f"Data_for_writing/csv/{name}.csv", used, "data behind " + name)]
    _medians(ctx).to_csv(csvd / "q6_propulsor_units_median_by_cohort.csv", index=False)
    extra = _extra_csv(ctx, csvd)
    extra["q6_propulsor_units_median_by_cohort"] = "median propulsor units of Tilt Propulsor, CVT and Lift + Cruise per cohort"
    manifest += [(f"Data_for_writing/csv/{n}.csv", True, s) for n, s in extra.items()]
    _numbers(ctx, R)
    manifest.append(("Data_for_writing/NUMBERS_IV.md", True, "numbers of Analysis IV with their sources"))
    mf = R / "Data_for_writing" / "MANIFEST.md"
    new = not mf.exists()
    with open(mf, "a", encoding="utf-8") as f:
        if new:
            f.write("# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n")
        have = set(mf.read_text(encoding="utf-8").splitlines()) if not new else set()
        for p, used, what in manifest:
            line = f"- `LaTeX_v15/{p}` · {'yes' if used else 'no (leaves the text)'} · {what}"
            if line not in have:                     # appended once, however often the notebook runs
                f.write(line + "\n")
    return pd.DataFrame(checks)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: p4._relabel(p4.COLUMNS.get(c, c)))
    return df.apply(lambda s: s.map(lambda x: p4._relabel(x) if isinstance(x, str) else x))


def _extra_csv(ctx, csvd) -> dict:
    d = q6._data(ctx)
    tr = _clean(d["trends"])
    tr.to_csv(csvd / "q6_driver_trends.csv", index=False)
    ver, _ = q6.tab_driver_verdicts(ctx)
    _clean(ver).to_csv(csvd / "q6_driver_verdicts.csv", index=False)
    dw = _clean(d["dw"])
    dw.to_csv(csvd / "q6_architecture_traces_by_cohort.csv", index=False)
    _, tm = p4.fig_tilt_mechanisms_per_propulsor(ctx)
    plt.close("all")
    tm.to_csv(csvd / "q6_tilt_mechanisms_per_propulsor.csv", index=False)
    return {"q6_driver_trends": "Spearman rho and p of every trace per architecture and pooled (every year to 2023)",
            "q6_driver_verdicts": "traces that move and the drivers they go with and against (the driver table)",
            "q6_architecture_traces_by_cohort": "per architecture and cohort: aircraft, tilting sets, propulsor units, booms and ducted shares",
            "q6_tilt_mechanisms_per_propulsor": "mean tilt mechanisms per propulsor unit per architecture and cohort, with rho and p"}


def _numbers(ctx, R: Path):
    import viz.thesis_text_q6 as tx6
    d = q6._data(ctx)
    n6 = q6.numbers(ctx)
    keys = {s: sorted(set(re.findall(r"\{([a-z0-9_]+)\}", next(r["text"] for r in tx6.RESULTS if r["sub"] == s)))) for s in ("C", "D")}
    pm = d["pmix"]
    w = ctx.COMPLETE
    cohort = lambda x: x                                                                      # noqa: E731
    lay = []
    for c, nm in (("SLC", "Lift + Cruise"), ("TR", "Tilt Propulsor"), ("CVT", "Combined Vectored Thrust")):
        m = pm[pm["code"] == c]
        for k in m["configuration"].unique():
            row = {"architecture": nm, "layout": q6.DISPLAY[c](k)}
            for x in w:
                r = m[(m["configuration"] == k) & (m["window"] == x)]
                n = m[m["window"] == x]["class aircraft"].iloc[0] if (m["window"] == x).any() else np.nan
                row[x] = f"{100 * r['aircraft'].sum() / n:.1f} % ({int(r['aircraft'].sum())}/{int(n)})" if n == n else "n/a"
            lay.append(row)
    lay = pd.DataFrame(lay)
    dw = _clean(d["dw"])
    cols = ["architecture", "cohort", "aircraft", "tilting sets (mean)", "propulsive units (median)", "share with units on booms", "share with a ducted unit",
            "ducted share, units on booms", "ducted share, no units on booms"]
    traces = dw[[c for c in cols if c in dw.columns]].copy()
    for c in traces.columns[3:]:
        traces[c] = pd.to_numeric(traces[c], errors="coerce").round(3)
    trends = _clean(d["trends"])
    ver, _ = q6.tab_driver_verdicts(ctx)
    tm, pooled = _tilt(ctx)
    dist, nf, na = p4.dispersion(ctx)
    med = _medians(ctx)
    lk = d["links"]
    L = ["# NUMBERS_IV — Analysis IV (evolution of the design space)\n",
         "Written by notebook 51 (`viz/thesis_latex_part4.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`.\n",
         "## IV.1 Layout shares per cohort (share of the architecture's designs; count/architecture total)\n",
         "Source: `q6_leading_layout_by_architecture.csv`. The first two cohorts hold few designs.\n", tables_md(lay), "",
         "## IV.1 and IV.2 Traces per architecture and cohort\n", "Source: `q6_architecture_traces_by_cohort.csv` (frame `dw` of `viz/thesis_q6.py`).\n", tables_md(traces), "",
         "## IV.2 Median propulsor units per architecture and cohort\n",
         "Source: `q6_propulsor_units_median_by_cohort.csv` (the aircraft of the architecture with a unit count above zero, as the traces frame; 2024–26 is incomplete and not read). "
         "The median of Tilt Propulsor goes 2, 2, 4, 4: 2 to 4 is right. The 6 is the median of one layout inside Tilt Propulsor (tilting sets in 2+ places), see below.\n", tables_md(med), "",
         "Median propulsor units of the leading layouts, per cohort:\n", tables_md(_layout_medians(ctx)), "",
         "## IV.2 Spearman rho and p of every trace (every year to 2023; too thin / constant where not tested)\n", "Source: `q6_driver_trends.csv`.\n", tables_md(trends), "",
         "## IV.2 The driver table\n", "Source: `q6_driver_verdicts.csv`.\n", tables_md(_clean(ver)), "",
         "## IV.2 Links: Tilt Propulsor units by tilting sets, CVT ducting by boom layout\n", "Source: frame `links` of `viz/thesis_q6.py`.\n", tables_md(_clean(lk)), "",
         "## IV.2 Tilt mechanisms per propulsor unit, per architecture and cohort\n", "Source: `q6_tilt_mechanisms_per_propulsor.csv` (tilting sets / propulsor units, mean per cohort, cohorts of 5 designs or more).\n",
         tables_md(tm), "", "Pooled over Tilt Propulsor, CVT and Tilt Wing (mean per cohort): " + ", ".join(f"{k} {v:.3f}" for k, v in pooled.items()), "",
         f"## Future work: distance of each cohort from the first, and Rao's Q (`q6_centroid_dispersion`; leaves the dissertation)\n",
         f"Source: `q6_centroid_dispersion.csv`. Gower distance over {nf} dimensions (four systems, each weighing 1), {na} designs; 200 permutations, seed 42, cohort sizes kept; "
         "band = 2.5th to 97.5th percentile. Distance of a cohort = mean Gower distance between its designs and those of ≤2011 minus the mean of the two Rao's Q.\n",
         tables_md(dist), "",
         "## Numbers quoted by the Results text, IV.1 (sub-question C)\n", "Source: `viz/thesis_q6.py` numbers(ctx).\n", "\n".join(f"- `{k}` = {n6[k]}" for k in keys["C"] if k in n6), "",
         "## Numbers quoted by the Results text, IV.2 (sub-question D)\n", "Source: `viz/thesis_q6.py` numbers(ctx).\n", "\n".join(f"- `{k}` = {n6[k]}" for k in keys["D"] if k in n6), ""]
    (R / "Data_for_writing" / "NUMBERS_IV.md").write_text("\n".join(L), encoding="utf-8")


def _medians(ctx) -> pd.DataFrame:
    cf = q6._data(ctx)["cf"]
    x = cf[cf["topType"].isin(["TR", "CVT", "SLC"]) & cf["units"].gt(0) & cf["window"].notna()]
    rows = []
    for c, nm in (("TR", "Tilt Propulsor"), ("CVT", "Combined Vectored Thrust"), ("SLC", "Lift + Cruise")):
        r = {"architecture": nm}
        for w in ctx.WIN_NAMES:
            u = x[(x.topType == c) & (x.window == w)]["units"]
            r[w if "partial" not in w else "2024-26 (incomplete)"] = f"{u.median():g} (n {len(u)})"
        rows.append(r)
    out = pd.DataFrame(rows)
    dw = q6._data(ctx)["dw"].set_index(["code", "window"])["propulsive units (median)"]
    for c, nm in (("TR", "Tilt Propulsor"), ("CVT", "Combined Vectored Thrust"), ("SLC", "Lift + Cruise")):
        for w in ctx.COMPLETE:
            assert f"{dw[(c, w)]:g}" == out.loc[out.architecture == nm, w].iloc[0].split(" ")[0], (c, w)       # the same medians as the traces frame
    return out


def _layout_medians(ctx) -> pd.DataFrame:
    d = q6._data(ctx)
    keys = frames.class_config_keys(ctx.ds, ctx.v, d["cf"], ctx.COMPLETE)
    k = keys[keys["rule set"] == "proposed"]
    units = d["cf"].set_index("aircraft_id")["units"]
    rows = []
    for (c, w), lay in LEADING.items():
        ids = k[(k.code == c) & (k.window == w) & (k.configuration == lay)]["aircraft_id"]
        rows.append({"architecture": ARCH_NAME[c], "cohort": w, "leading layout": WORDS[(c, w)], "designs": len(ids), "median propulsor units": f"{units.reindex(ids).median():g}"})
    return pd.DataFrame(rows)


def _tilt(ctx):
    _, tm = p4.fig_tilt_mechanisms_per_propulsor(ctx)
    plt.close("all")
    nm = p4.numbers(ctx)
    pooled = nm["pooled mean tilt mechanisms per propulsor unit, three architectures"]
    return tm.round(4), pooled


# ================================================================================== q6_iv2_representative_aircraft (new, IV.2)
#: cell -> (aircraft_id, fig_key of the drawing, why). The candidates of a cell are the designs of the architecture in the cohort whose layout is
#: the leading one (the layout figure's rule), with an approved, clean, whole-vehicle line drawing; they are ranked by how close their propulsor
#: units are to the median of that layout in that cohort, then by view (top view first); the six below were chosen from the top of each ranking
#: after looking at the drawings.
PICKS = {
    ("SLC", "<= 2011"): ("US2013020429A1_ua1", "1", "ranks first with its twin (US2012012692A1) at 10 propulsor units against a median of 8.5; the top view shows the lift units on the two booms plainly"),
    ("SLC", "2020-23"): ("US2022281593A1_ua1", "1", "ranks first: 8 propulsor units, equal to the median of the layout; named aircraft (VoloConnect); the top view shows the lift units on two booms"),
    ("TR", "<= 2011"): ("US2013026303A1_ua1", "13", "ranks fourth by units (2, the median) and is the clearest top view of one tilting set; a named aircraft (Project Zero); the first three are drawn with the reference numerals over the rotors"),
    ("TR", "2020-23"): ("US2023331379A1_ua1", "5", "tilting rotors at the tips of a fore and an aft wing, so two tilting sets in two places show in one view; 4 propulsor units against a median of 6 (the nearest drawings at 6 units show the rotors only as dashed circles)"),
    ("CVT", "<= 2011"): ("US2012091257A1_ua1", "3", "ranks first: 3 propulsor units against a median of 3.5; the top view shows the tilting wing-tip rotor and the fixed ducted fan on the body"),
    ("CVT", "2020-23"): ("US2022306292A1_ua1", "Fu_D00000", "6 propulsor units, equal to the median; tilting rotors on the wings and fixed rotors on booms; a hover view, since the patent has no top view of this variant"),
}
#: the alternatives for the two cells the author questioned: CVT 2020-23 in a TOP view (like the other five) and Tilt Propulsor 2020-23 with the cohort's median of propulsor units (4)
PICKS_ALT = {**PICKS,
    ("CVT", "2020-23"): ("US2022388648A1_ua1", "3", "top view, 6 propulsor units, equal to the median of the layout; of the three top views of the layout (this, US2024124134A1 cropped through the wing, US2025304249A1 with 8 units) the only one that shows the whole aircraft with its tilting rotors on the long outer pods and the fixed rotor at the tail"),
    ("TR", "2020-23"): ("US2021229802A1_ua2", "18", "4 propulsor units, equal to the median of the Tilt Propulsor cohort (the first pick, US2023331379A1, has 4 as well; the median 6 of the leading layout is a different number); Overair, two wings with a tilting rotor at each tip: tilting sets in two places; hover top view"),
}
WORDS = {("SLC", "<= 2011"): "lift units on booms", ("SLC", "2020-23"): "lift units on booms",
         ("TR", "<= 2011"): "one tilting set", ("TR", "2020-23"): "tilting sets in 2+ places",
         ("CVT", "<= 2011"): "tilting rotors, fixed elsewhere", ("CVT", "2020-23"): "tilting rotors, fixed on booms"}
LEADING = {("SLC", "<= 2011"): "lift units on booms", ("SLC", "2020-23"): "lift units on booms",
           ("TR", "<= 2011"): "one tilting set", ("TR", "2020-23"): "two or more tilting sets, on two or more stations",
           ("CVT", "<= 2011"): "rotors tilt · fixed units elsewhere", ("CVT", "2020-23"): "rotors tilt · fixed units on booms"}
ARCH_NAME = {"CVT": "Combined Vectored Thrust", "TR": "Tilt Propulsor", "SLC": "Lift + Cruise"}
#: the rotated row names of the representative-aircraft figure, on two lines so they stay beside their drawing (rerun of 2026-10-15)
ROW_NAME = {"CVT": "Combined\nVectored Thrust", "TR": "Tilt\nPropulsor", "SLC": "Separate\nLift + Cruise"}


def _crop(path, rotation=0.0, pad=6):
    from PIL import Image
    im = Image.open(path).convert("L")
    if rotation:
        im = im.rotate(-rotation, expand=True, fillcolor=255)
    a = np.asarray(im)
    ys, xs = np.where(a < 235)
    return im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, a.shape[1]), min(ys.max() + pad, a.shape[0])))


def representative(ctx, picks=None) -> pd.DataFrame:
    """One row per cell: the cohort, the layout, its share of the architecture (from the layout figure's frame), the design, patent, drawing, why."""
    d = q6._data(ctx)
    cf, v, f = d["cf"], ctx.v.set_index("aircraft_id"), ctx.ds.figures
    keys = frames.class_config_keys(ctx.ds, ctx.v, cf, ctx.COMPLETE)
    k = keys[keys["rule set"] == "proposed"]
    units = cf.set_index("aircraft_id")["units"]
    rows = []
    for (c, w), (a, fk, why) in (picks or PICKS).items():
        cell = k[(k.code == c) & (k.window == w)]
        ids = cell[cell.configuration == LEADING[(c, w)]]["aircraft_id"]
        assert a in set(ids), (c, w, a)
        fr = f[(f.aircraft_id == a) & (f.fig_key.astype(str) == fk) & (f.status == "approved")].iloc[0]
        rows.append({"architecture": ARCH_NAME[c], "cohort": w, "layout": WORDS[(c, w)], "layout in the figure's frame": LEADING[(c, w)],
                     "share of the architecture": round(len(ids) / len(cell), 4), "designs in the layout": len(ids), "designs in the architecture": len(cell),
                     "patent number": v.loc[a, "patent_id"], "design identifier": a, "name": v.loc[a, "aircraft_name"], "assignee": v.loc[a, "assignee"],
                     "title": v.loc[a, "title"], "priority year": int(v.loc[a, "year"]), "propulsor units": int(units[a]),
                     "median units of the layout in the cohort": float(units.reindex(ids).median()), "figure key": fk, "view": fr["per"], "state": fr["acState"],
                     "image file": fr["image_file"], "image path": fr["image_path"], "rotation (deg)": float(fr["rotation_deg"]) if pd.notna(fr["rotation_deg"]) else 0.0, "why": why})
    return pd.DataFrame(rows)


def fig_representative(ctx, picks=None):
    t = representative(ctx, picks)
    w_in = 0.9 * TEXT_CM / 2.54
    fig = plt.figure(figsize=(w_in, 0.70 * w_in))
    gs = fig.add_gridspec(6, 2, height_ratios=[1, 0.14] * 3, left=0.105, right=0.995, top=0.995, bottom=0.005, hspace=0.05, wspace=0.04)
    order = [("CVT", "<= 2011"), ("CVT", "2020-23"), ("TR", "<= 2011"), ("TR", "2020-23"), ("SLC", "<= 2011"), ("SLC", "2020-23")]
    for i, (c, w) in enumerate(order):
        r = t[(t["architecture"] == ARCH_NAME[c]) & (t["cohort"] == w)].iloc[0]
        ax = fig.add_subplot(gs[2 * (i // 2), i % 2])
        ax.imshow(_crop(r["image path"], r["rotation (deg)"]), cmap="gray", vmin=0, vmax=255)
        ax.set_xticks([]), ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        tx = fig.add_subplot(gs[2 * (i // 2) + 1, i % 2])
        tx.set_xticks([]), tx.set_yticks([])
        tx.axis("off")
        tx.text(0.5, 0.5, f"{ctx.WSHORT[w].replace('–', '-')} · {r['layout']} · {100 * r['share of the architecture']:.0f} %", ha="center", va="center", fontsize=MIN_PT)
        if i % 2 == 0:
            ax.text(-0.03, 0.5, ROW_NAME[c], transform=ax.transAxes, rotation=90, ha="right", va="center", fontsize=MIN_PT + 1, linespacing=1.0)
    return fig, t


def export_representative(cfg, ctx, picks=None, stem="q6_iv2_representative_aircraft"):
    R = root(cfg)
    with plt.style.context(str(Path(p4.__file__).with_name("part1.mplstyle"))):
        fig, t = fig_representative(ctx, picks)
        for tx in fig.findobj(Text):
            if tx.get_text() and tx.get_fontsize() < MIN_PT:
                tx.set_fontsize(MIN_PT)
        fig.canvas.draw()
        chk = (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, MIN_PT)))
    out = R / "Figures" / PART / "IV2_drivers" / "main"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.pdf")
    dims = (round(fig.get_figwidth() * 2.54, 2), round(fig.get_figheight() * 2.54, 2))
    plt.close(fig)
    csvd = R / "Data_for_writing" / "csv"
    t.drop(columns=["image path"]).to_csv(csvd / f"{stem}.csv", index=False)
    alt = stem.endswith("_alt")
    lines = [f"- `LaTeX_v15/Figures/{PART}/IV2_drivers/main/{stem}.pdf` · {'no (alternative)' if alt else 'yes'} · " + ("the same six cells with a top view for CVT 2020-23 and a Tilt Propulsor 2020-23 drawing with the cohort median of 4 propulsor units" if alt else "one patent drawing per architecture and cohort (CVT, Tilt Propulsor, Lift + Cruise; ≤2011 and 2020-23) showing the leading layout"),
             f"- `LaTeX_v15/Data_for_writing/csv/{stem}.csv` · {'no (alternative)' if alt else 'yes'} · the six designs: patent number, identifier, drawing, share of the architecture, why chosen"]
    mf = R / "Data_for_writing" / "MANIFEST.md"
    have = set(mf.read_text(encoding="utf-8").splitlines())
    with open(mf, "a", encoding="utf-8") as f:
        for l in lines:
            if l not in have:
                f.write(l + "\n")
    return _numbers_rep(R, t, stem, dims, chk)


def _numbers_rep(R, t, stem, dims, chk):
    nf = R / "Data_for_writing" / "NUMBERS_IV.md"
    head = "## IV.2 Representative aircraft (`q6_iv2_representative_aircraft`)" if not stem.endswith("_alt") else "## IV.2 Representative aircraft, alternatives (`q6_iv2_representative_aircraft_alt`)"
    txt = nf.read_text(encoding="utf-8")
    keep = [blk for blk in re.split(r"\n(?=## )", txt) if not blk.startswith(head)]
    cols = ["architecture", "cohort", "layout", "share of the architecture", "designs in the layout", "designs in the architecture", "patent number", "design identifier",
            "propulsor units", "median units of the layout in the cohort", "view", "figure key"]
    body = f"{head}\n\nSource: `{stem}.csv`; shares are those of the layout figure.\n\n" + tables_md(t[cols]) + "\n"
    nf.write_text("\n".join(keep).rstrip("\n") + "\n\n" + body, encoding="utf-8")
    return dims, chk, t


# ================================================================================== refresh of 2026-10-16: the 2024-26 cohort, drawn and never tested
#: Rules (author's brief of 2026-10-16). Data and tests do not change: every Spearman test, the disparity and every number of NUMBERS_IV.md stay
#: on the four complete cohorts; the 2024-26 cohort is a fifth column or point, hollow, dashed, under a grey band like the "few designs" band.
#: Only the three largest architectures are drawn. Each figure is drawn at 0.62 of the 16 cm text block (the layout figure and the composite
#: at the full width) with no text under 7 pt, and its CSV (same columns as before, the 2024-26 rows added) goes to Data_for_writing/csv/.
ARCH3 = ["SLC", "TR", "CVT"]
LABEL3 = {"SLC": "Separate Lift + Cruise (SLC)", "TR": "Tilt Propulsor (TP)", "CVT": "Combined Vectored Thrust (CVT)"}
SHORT3 = {"SLC": "SLC", "TR": "TP", "CVT": "CVT"}
INCOMPLETE = "2024-26 (partial)"                      # the record's name of the incomplete cohort
COHORT_TICK = {"<= 2011": "≤2011", "2012-15": "2012-15", "2016-19": "2016-19", "2020-23": "2020-23", INCOMPLETE: "2024-26*"}
COHORT_CSV = {INCOMPLETE: "2024-26 (incomplete)"}     # how the CSVs name it
N_FEW = 2                                             # the first two cohorts hold few designs (as every Analysis IV figure)
FRAC62 = 0.62
#: the Spearman test of each share drawn (frame ``trends`` of viz/thesis_q6.py: every year to 2023, the complete cohorts only)
TRACE_TEST = {"share with units on booms": "units carried on booms", "share with a ducted unit": "a ducted unit"}
OUTPUTS = "outputs_for_thesis_2026-10-16"             # the hand-over folder at the repository root, mirroring LaTeX_v15/
MIRROR = "handoff_2026-10-16/COPY_TO_LaTeX_v15"       # the same files, in the folder git carries to the dissertation's computer


def _wins(ctx) -> list:
    return list(ctx.WIN_NAMES)                         # the four complete cohorts, then the incomplete one


def _csv_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """The CSV copy of a frame: the incomplete cohort named "2024-26 (incomplete)" (column ``window``, printed ``cohort``)."""
    out = df.copy()
    if "window" in out.columns:
        out["window"] = out["window"].map(lambda w: COHORT_CSV.get(w, w))
    return out


def _fade_incomplete_column(ax, k: int) -> None:
    """The bars of column ``k`` faded like the few-design columns of :func:`viz.plots.config_stack`, behind the same dashed line."""
    for b in ax.patches:
        if abs(b.get_x() + b.get_width() / 2 - k) < 1e-6:
            b.set_alpha(0.55)
    ax.axvline(k - 0.5, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=5)


def _cohort_bands(ax, k: int, bottom: bool = False) -> None:
    """The two grey bands of a trace figure, drawn alike: few designs (the first N_FEW cohorts) and incomplete (the last). Their labels sit at
    the top of the band, or at its foot (``bottom``) in a composite panel, where the tests take the top."""
    plots.few_band(ax, N_FEW, text=None)
    ax.axvspan(k - 1.5, k - 0.5, color=plots.FEW_FILL, zorder=0, linewidth=0)
    ax.axvline(k - 1.5, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=1)
    y, va = (0.02, "bottom") if bottom else (0.985, "top")
    ax.text((N_FEW - 1) / 2, y, "few designs", transform=ax.get_xaxis_transform(), ha="center", va=va, fontsize=MIN_PT, color=style.MUTED, zorder=6)
    ax.text(k - 0.95, y, "incomplete", transform=ax.get_xaxis_transform(), ha="center", va=va, fontsize=MIN_PT, color=style.MUTED, zorder=6)


def _tick(w: str, ns) -> str:
    return f"{COHORT_TICK[w]}\n" + "·".join(str(int(n)) for n in ns)


def _line5(ax, y, color, dash, marker, ms: float = 4.4, lw: float = 1.4) -> None:
    """One trace over the five cohorts: the line through the complete cohorts, a dashed segment to the incomplete one; the markers of the
    few-design cohorts and of the incomplete cohort hollow. A blank cohort (under 5 designs) breaks nothing: the line joins the drawn ones."""
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y))
    ok = np.isfinite(y)
    k = len(y) - 1
    xc = x[:k][ok[:k]]
    ax.plot(xc, y[xc], color=color, linestyle=dash, linewidth=lw, zorder=3, solid_capstyle="round")
    if ok[k] and len(xc):
        ax.plot([xc[-1], k], [y[xc[-1]], y[k]], color=color, linestyle=(0, (2.2, 2.0)), linewidth=lw * 0.9, zorder=3, alpha=0.75)
    for xi in x[ok]:
        hollow = xi < N_FEW or xi == k
        ax.plot(xi, y[xi], marker=marker, markersize=ms, color=color, markeredgecolor=color, markeredgewidth=1.0,
                markerfacecolor="white" if hollow else color, linestyle="none", zorder=4, alpha=0.8 if xi == k else 1.0)


def _handles3(labels=None, codes=ARCH3) -> list:
    return [Line2D([], [], color=style.cls(c).color, linestyle=style.cls(c).dash, marker=style.cls(c).marker, markersize=4.4, linewidth=1.4,
                   label=(labels or LABEL3)[c]) for c in codes]


def _hollow_handle(label: str, color=style.MUTED) -> Line2D:
    return Line2D([], [], marker="o", markersize=4.4, color=color, markerfacecolor="white", markeredgecolor=color, linestyle="none", label=label)


def _test_txt(rho, p) -> str:
    return (f"ρ {rho:+.2f}, {q6._ptxt(p)}" if rho == rho else "not tested").replace("-", "−")


def _trace_tests(ctx, col: str) -> dict:
    t = q6._data(ctx)["trends"]
    return {c: t[(t["trace"] == TRACE_TEST[col]) & (t["code"] == c)].iloc[0] for c in ARCH3}


def _share_axes(ax, k: int, ylabel: str, headroom: bool) -> None:
    ax.set_xlim(-0.5, k - 0.5)
    ax.set_ylim(-0.04, 1.30 if headroom else 1.05)        # headroom: the tests are printed above the 100 % line inside the panel
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    q6._pc(ax)
    q6._ygrid(ax)
    ax.set_ylabel(ylabel)


def _panel_tests(ax, lines: list) -> None:
    """The Spearman tests of a composite panel, printed above the 100 % line (the headroom), between the two grey bands."""
    ax.text(0.5, 0.985, "\n".join(lines), transform=ax.transAxes, ha="center", va="top", fontsize=MIN_PT, linespacing=1.25,
            bbox=dict(fc="white", ec="none", pad=1.2, alpha=0.9))


# ---- the four trace panels (each a standalone figure and a panel of the composite)
def panel_share(ax, ctx, col: str, ylabel: str, in_panel: bool):
    """Share ``col`` of the three architectures over the five cohorts; the Spearman test of each architecture (every year to 2023)."""
    dw, wins = q6._data(ctx)["dw5"], _wins(ctx)
    k = len(wins)
    fr = dw.pivot(index="window", columns="code", values=col).reindex(wins)[ARCH3]
    ns = dw.pivot(index="window", columns="code", values="aircraft").reindex(wins)[ARCH3]
    _cohort_bands(ax, k, bottom=in_panel)
    for c in ARCH3:
        s = style.cls(c)
        _line5(ax, fr[c], s.color, s.dash, s.marker)
    ax.set_xticks(range(k), [_tick(w, ns.loc[w]) for w in wins])
    _share_axes(ax, k, ylabel, in_panel)
    tests = _trace_tests(ctx, col)
    if in_panel:
        _panel_tests(ax, [f"{SHORT3[c]} {_test_txt(tests[c]['rho'], tests[c]['p'])}" for c in ARCH3])
    data = _csv_cohorts(dw[["class", "code", "window", "aircraft", col]].reset_index(drop=True))
    return _handles3({c: f"{LABEL3[c]}: {_test_txt(tests[c]['rho'], tests[c]['p'])}" for c in ARCH3}), data


def panel_cvt_booms(ax, ctx, in_panel: bool):
    """CVT designs with propulsors on booms, share per cohort with its value at each point; the Spearman test of CVT."""
    dw, wins = q6._data(ctx)["dw5"], _wins(ctx)
    k = len(wins)
    cv = dw[dw["code"] == "CVT"].set_index("window").reindex(wins)
    sc = style.cls("CVT")
    y = cv["share with units on booms"].to_numpy(dtype=float)
    _cohort_bands(ax, k, bottom=in_panel)
    _line5(ax, y, sc.color, sc.dash, sc.marker)
    for xi in range(k):
        if not np.isfinite(y[xi]):
            continue
        dip = (not in_panel) and 0 < xi < k - 1 and y[xi] <= min(y[xi - 1], y[xi + 1])      # in a panel the band label takes the foot
        ax.annotate(f"{100 * y[xi]:.0f} %", (xi, y[xi]), textcoords="offset points", xytext=(0, -7 if dip else 6), ha="center",
                    va="top" if dip else "bottom", fontsize=MIN_PT, color=style.INK)
    ax.set_xticks(range(k), [_tick(w, [cv.loc[w, "aircraft"]]) for w in wins])
    _share_axes(ax, k, "share of CVT designs with\npropulsors on booms", in_panel)
    t = _trace_tests(ctx, "share with units on booms")["CVT"]
    if in_panel:
        _panel_tests(ax, [f"CVT {_test_txt(t['rho'], t['p'])}"])
    data = _csv_cohorts(cv[["aircraft", "aircraft, units on booms", "share with units on booms"]].reset_index())
    return _handles3({"CVT": f"{LABEL3['CVT']}: {_test_txt(t['rho'], t['p'])}"}, ["CVT"]), data


def panel_cvt_ducted_booms(ax, ctx, in_panel: bool):
    """CVT ducted share inside each boom layout (propulsors on booms, none on booms), with the two Spearman tests (frame ``links``)."""
    d = q6._data(ctx)
    dw, wins = d["dw5"], _wins(ctx)
    k = len(wins)
    cv = dw[dw["code"] == "CVT"].set_index("window").reindex(wins)
    sc = style.cls("CVT")
    nb, nn = cv["aircraft, units on booms"].to_numpy(), cv["aircraft, no units on booms"].to_numpy()
    lt = d["links"][d["links"]["link"].str.startswith("CVT")].set_index("group")
    _cohort_bands(ax, k, bottom=in_panel)
    handles = []
    for name, col, color, marker, ns in (("units on booms", "ducted share, units on booms", sc.color, sc.marker, nb),
                                         ("no units on booms", "ducted share, no units on booms", style.MUTED, "o", nn)):
        y = cv[col].to_numpy(dtype=float)
        _line5(ax, y, color, "-", marker)
        for xi in range(k):
            if np.isfinite(y[xi]):
                below = name.startswith("units")
                ax.annotate(f"{int(ns[xi])}/{int(nb[xi] + nn[xi])}", (xi, y[xi]), textcoords="offset points", xytext=(-5, 0) if below else (0, 6),
                            ha="right" if below else "center", va="center" if below else "bottom", fontsize=MIN_PT, color=style.INK,
                            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
        r = lt.loc[name]
        handles.append(Line2D([], [], color=color, marker=marker, markersize=4.4, linewidth=1.4,
                              label=f"CVT, {name}: {r['movement']} ({_test_txt(r['rho'], r['p'])})"))
    ax.set_xticks(range(k), [_tick(w, [a, b]) for w, a, b in zip(wins, nb, nn)])
    _share_axes(ax, k, "share of CVT designs with\na ducted propulsor", in_panel)
    if in_panel:
        _panel_tests(ax, [f"on booms: {lt.loc['units on booms', 'movement']} ({_test_txt(lt.loc['units on booms', 'rho'], lt.loc['units on booms', 'p'])})",
                          f"none on booms: {lt.loc['no units on booms', 'movement']} ({_test_txt(lt.loc['no units on booms', 'rho'], lt.loc['no units on booms', 'p'])})"])
    data = _csv_cohorts(cv[["aircraft, units on booms", "ducted share, units on booms", "aircraft, no units on booms", "ducted share, no units on booms"]].reset_index())
    return handles, data


def _standalone(ctx, draw, height_in: float, legend_rows: int):
    """One trace figure at 0.62 of the text block: the panel, its legend (with the tests) under it."""
    w_in = TEXT_CM / 2.54 * FRAC62
    fig, ax = plt.subplots(figsize=(w_in, height_in), constrained_layout=True)
    handles, data = draw(ax, ctx, False)
    ax.set_xlabel("priority cohort; under it, the designs of each line in legend order", fontsize=MIN_PT)
    fig.legend(handles=handles, loc="outside lower center", ncol=1, fontsize=MIN_PT, handlelength=2.0, labelspacing=0.35)
    return fig, data


def fig_boom_share5(ctx):
    return _standalone(ctx, lambda ax, c, p: panel_share(ax, c, "share with units on booms", "share of the architecture with\npropulsors on booms", p), 3.35, 3)


def fig_ducted_share5(ctx):
    return _standalone(ctx, lambda ax, c, p: panel_share(ax, c, "share with a ducted unit", "share of the architecture with\na ducted propulsor", p), 3.35, 3)


def fig_cvt_booms5(ctx):
    return _standalone(ctx, panel_cvt_booms, 2.9, 1)


def fig_cvt_ducted_booms5(ctx):
    return _standalone(ctx, panel_cvt_ducted_booms, 3.2, 2)


# ---- the composite (rebuilt 2026-10-17: one compact 16 x 9.3 cm figure, two rows of two panels)
TRACE_PT = 7.0                 # ticks, legends, axis labels and point labels of the composite
TRACE_PT_MIN = 6.5             # the band words; nothing in the composite is smaller
TRACE_H_CM = 9.6               # the height of the composite (row 2 carries two legend lines: the five entries do not fit one)
#: figure name -> the smallest text it may carry (default MIN_PT)
FLOOR = {"q6_iv1_traces": TRACE_PT_MIN}


def _n_str(ns) -> str:
    return "·".join(str(int(n)) for n in ns)


def _trace_axes(fig):
    """The four panels of the composite at fixed positions (cm from the bottom-left corner): two rows of two, each 7.3 x 3.5 cm, a 4 mm gap
    with a thin rule between the rows, room for the shared y labels on the left, the ticks, one legend line under each row and the x label."""
    W, H = TEXT_CM, TRACE_H_CM
    pw, ph = 7.3, 3.5                                  # panel size
    x0, xgap = 1.05, 0.35                              # left margin (y label + tick labels), gap between the columns
    top, tick, leg, gap, xlab, bot = 0.10, 0.46, 0.28, 0.40, 0.28, 0.06      # tick: a 7 pt label plus tick and pad is 0.38 cm
    y1 = H - top - ph                                  # row 1 panel bottom
    y2 = y1 - tick - leg - gap - ph                    # row 2 panel bottom
    assert y2 - tick - 2 * leg - xlab - bot >= -0.01, y2        # row 2: the legend of (c) and, under it, the legend of (d)
    f = lambda x, y, w, h: fig.add_axes([x / W, y / H, w / W, h / H])       # noqa: E731
    axs = np.array([[f(x0, y1, pw, ph), f(x0 + pw + xgap, y1, pw, ph)],
                    [f(x0, y2, pw, ph), f(x0 + pw + xgap, y2, pw, ph)]])
    ylegend = ((y1 - tick) / H, (y2 - tick) / H, (y2 - tick - leg) / H)       # the top of each legend line: row 1, row 2 (c), row 2 (d)
    yrule = (y1 - tick - leg - gap / 2) / H
    yxlabel = (y2 - tick - 2 * leg) / H
    return axs, ylegend, yrule, yxlabel, (x0 / W, (x0 + 2 * pw + xgap) / W)


def _trace_line(ax, y, color, dash, marker) -> None:
    _line5(ax, y, color, dash, marker, ms=3.0, lw=1.0)


def _trace_bands(ax, k: int, words: bool) -> None:
    """The few-design and incomplete bands; the words once per row, in the left panel only, at the top of the band, 6.5 pt grey."""
    plots.few_band(ax, N_FEW, text=None)
    ax.axvspan(k - 1.5, k - 0.5, color=plots.FEW_FILL, zorder=0, linewidth=0)
    ax.axvline(k - 1.5, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=1)
    if words:
        kw = dict(transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=TRACE_PT_MIN, color=style.MUTED, zorder=6)
        ax.text((N_FEW - 1) / 2, 0.985, "few designs", **kw)
        ax.text(k - 1, 0.985, "incomplete", **kw)


def _trace_axes_style(ax, k: int, wins, left: bool, ylabel: str = "share of designs, %") -> None:
    ax.set_xlim(-0.5, k - 0.5)
    ax.set_ylim(-0.04, 1.05)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xticks(range(k), [COHORT_TICK[w] for w in wins])
    ax.tick_params(axis="both", labelsize=TRACE_PT, length=2.5, pad=1.8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{100 * v:.0f}"))
    q6._ygrid(ax)
    if left:
        ax.set_ylabel(ylabel, fontsize=TRACE_PT, labelpad=2)
    else:
        ax.tick_params(axis="y", labelleft=False)      # same range as the panel on its left; ticks only


def _trace_legend(fig, handles, y_top: float, xspan) -> None:
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=((xspan[0] + xspan[1]) / 2, y_top), ncol=len(handles), fontsize=TRACE_PT,
               handlelength=1.5, handletextpad=0.5, columnspacing=0.9, borderpad=0.0, borderaxespad=0.0, frameon=False)


def _h(color, dash, marker, label) -> Line2D:
    return Line2D([], [], color=color, linestyle=dash, marker=marker, markersize=3.0, linewidth=1.0, label=label)


def fig_iv1_traces(ctx):
    """The composite: panels (a) to (d) of the four trace figures, two rows of two at 7.3 x 3.5 cm, 16 cm wide and 9.6 cm tall. Row 1 the
    boom traces, row 2 the duct traces, a thin rule between them; one y label per row (left panel), one x label for the figure, one legend
    line per row carrying the n of each line and its Spearman test (every year to 2023), row 2 on two lines ((c), then (d): its five entries
    do not fit one line at 7 pt); the band words once per row in the left panel.
    The same data, tests, point labels and hollow markers as the four single-panel figures (panel_share, panel_cvt_booms,
    panel_cvt_ducted_booms); only the layout is new."""
    d = q6._data(ctx)
    dw, wins = d["dw5"], _wins(ctx)
    k = len(wins)
    fig = plt.figure(figsize=(TEXT_CM / 2.54, TRACE_H_CM / 2.54))
    axs, yleg, yrule, yxlab, xspan = _trace_axes(fig)
    cv = dw[dw["code"] == "CVT"].set_index("window").reindex(wins)
    sc = style.cls("CVT")
    legends = []
    # row 1 (a) booms per architecture, (b) CVT on booms with its values; row 2 (c) ducted per architecture, (d) CVT ducted by boom layout
    for row, col in enumerate(["share with units on booms", "share with a ducted unit"]):
        ax = axs[row, 0]
        fr = dw.pivot(index="window", columns="code", values=col).reindex(wins)[ARCH3]
        ns = dw.pivot(index="window", columns="code", values="aircraft").reindex(wins)[ARCH3]
        _trace_bands(ax, k, words=True)
        tests = _trace_tests(ctx, col)
        hs = []
        for c in ARCH3:
            s = style.cls(c)
            _trace_line(ax, fr[c], s.color, s.dash, s.marker)
            hs.append(_h(s.color, s.dash, s.marker, f"{SHORT3[c]}, n {_n_str(ns[c])} ({_test_txt(tests[c]['rho'], tests[c]['p'])})"))
        _trace_axes_style(ax, k, wins, left=True)
        legends.append(hs)
    # (b)
    ax = axs[0, 1]
    y = cv["share with units on booms"].to_numpy(dtype=float)
    _trace_bands(ax, k, words=False)
    _trace_line(ax, y, sc.color, sc.dash, sc.marker)
    for xi in range(k):
        if np.isfinite(y[xi]):
            ax.annotate(f"{100 * y[xi]:.0f} %", (xi, y[xi]), textcoords="offset points", xytext=(0, 4.5), ha="center", va="bottom",
                        fontsize=TRACE_PT, color=style.INK)
    _trace_axes_style(ax, k, wins, left=False)
    # (d)
    ax = axs[1, 1]
    nb, nn = cv["aircraft, units on booms"].to_numpy(), cv["aircraft, no units on booms"].to_numpy()
    lt = d["links"][d["links"]["link"].str.startswith("CVT")].set_index("group")
    _trace_bands(ax, k, words=False)
    legends.append([])                                 # the legend line of (d), under the one of (c)
    for name, short, col, color, marker, ns in (("units on booms", "CVT on booms", "ducted share, units on booms", sc.color, sc.marker, nb),
                                                ("no units on booms", "CVT no booms", "ducted share, no units on booms", style.MUTED, "o", nn)):
        yv = cv[col].to_numpy(dtype=float)
        _trace_line(ax, yv, color, "-", marker)
        for xi in range(k):
            if np.isfinite(yv[xi]):
                side = "below" if name.startswith("units") else "above"       # on booms: under the point; none on booms: over it
                if side == "below" and yv[xi] < 0.15:
                    side = "right"                                            # a point near the axis: the label to its right
                xy, ha, va = {"below": ((0, -4.5), "center", "top"), "above": ((0, 4.5), "center", "bottom"), "right": ((5, 0), "left", "center")}[side]
                ax.annotate(f"{int(ns[xi])}/{int(nb[xi] + nn[xi])}", (xi, yv[xi]), textcoords="offset points", xytext=xy, ha=ha, va=va,
                            fontsize=TRACE_PT, color=style.INK, bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.85))
        r = lt.loc[name]
        legends[2].append(_h(color, "-", marker, f"{short}, n {_n_str(ns)}, {r['movement']} ({_test_txt(r['rho'], r['p'])})"))
    _trace_axes_style(ax, k, wins, left=False)
    # letters, legends, rule, x label
    for ax, letter in zip(axs.ravel(), ["(a)", "(b)", "(c)", "(d)"]):
        ax.text(0.012, 0.97, letter, transform=ax.transAxes, ha="left", va="top", fontsize=8, fontweight="bold", zorder=7)
    for hs, yt in zip(legends, yleg):
        _trace_legend(fig, hs, yt, xspan)
    fig.add_artist(Line2D([xspan[0], xspan[1]], [yrule, yrule], color=style.MUTED, linewidth=0.5, alpha=0.7, transform=fig.transFigure))
    fig.text((xspan[0] + xspan[1]) / 2, yxlab, "priority cohort", ha="center", va="top", fontsize=TRACE_PT)
    return fig, None


def export_iv1_traces(cfg, ctx, png_dir: Path = None):
    """Write the composite alone (vector PDF at 16 x 9.3 cm, no bounding-box crop) to LaTeX_v15 and the two hand-over folders; a PNG copy
    for a quick look next to it (and in ``png_dir`` if given). Returns the check row."""
    name = "q6_iv1_traces"
    group, role, _, _, _ = REFRESH[name]
    fig, _, chk = draw_refresh(name, ctx)
    outside = len(_outside(fig))                       # measured at the figure's own dpi, before any save changes the renderer
    R = root(cfg)
    out = R / "Figures" / PART / group / role
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.pdf", bbox_inches=None)
    fig.savefig(out / f"{name}.png", bbox_inches=None, dpi=300)
    if png_dir is not None:
        fig.savefig(Path(png_dir) / f"{name}.png", bbox_inches=None, dpi=300)
    row = {"figure": name, "width cm": round(fig.get_figwidth() * 2.54, 2), "height cm": round(fig.get_figheight() * 2.54, 2),
           "text over text": chk[0], f"under {FLOOR[name]} pt": chk[1], "outside the page": outside}
    plt.close(fig)
    rel = [f"Figures/{PART}/{group}/{role}/{name}.{ext}" for ext in ("pdf", "png")]
    _manifest(R, [(rel[1], "PNG copy of the composite q6_iv1_traces, for a quick look")], used=False)
    handover_copy(cfg, rel)
    return row


def _outside(fig) -> list:
    """Texts whose box leaves the figure (the composite is saved without a bounding-box crop)."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    bad = []
    for t in fig.findobj(Text):
        if not t.get_text():
            continue
        b = t.get_window_extent(rend)
        if b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > W + 0.5 or b.y1 > H + 0.5:
            bad.append(t.get_text())
    return bad


# ---- the architecture centres
def _centre_trajectory5(ax, centres: dict, markersize: float = 6.0) -> list:
    """:func:`viz.plots.centre_trajectory` with the incomplete cohort (the last row): a hollow grey point at the end of each arrow chain,
    reached by a dashed grey arrow. The few-design cohorts (the first N_FEW) hollow and faint, as before."""
    pts = []
    for code, d in centres.items():
        s = style.cls(code)
        xs, ys = d["x"].to_numpy(dtype=float), d["y"].to_numpy(dtype=float)
        last = len(d) - 1
        for k in range(len(d)):
            if not (np.isfinite(xs[k]) and np.isfinite(ys[k])):
                continue
            early, inc = k < N_FEW, k == last
            col = style.MUTED if inc else s.color
            ax.plot(xs[k], ys[k], marker=s.marker, markersize=markersize * 1.3 if inc else markersize, color=col, markeredgecolor=col,
                    markerfacecolor="none" if inc else ("white" if early else s.color), alpha=0.6 if early else 1.0, linestyle="none", zorder=5 if inc else 4)
            pts.append((xs[k], ys[k], k, code))
            if k + 1 < len(d) and np.isfinite(xs[k + 1]) and np.isfinite(ys[k + 1]):
                to_inc = k + 1 == last
                ax.annotate("", xy=(xs[k + 1], ys[k + 1]), xytext=(xs[k], ys[k]), zorder=3,
                            arrowprops=dict(arrowstyle="->", color=style.MUTED if to_inc else s.color, linewidth=1.1 if to_inc else 1.3,
                                            linestyle=(0, (2.5, 2)) if to_inc else "-", shrinkA=4, shrinkB=4, alpha=0.4 if k + 1 < N_FEW else 1.0))
    return pts


def fig_centres5(ctx):
    dw, wins = q6._data(ctx)["dw5"], _wins(ctx)
    w_in = TEXT_CM / 2.54 * FRAC62
    fig, ax = plt.subplots(figsize=(w_in, 3.7), constrained_layout=True)
    tw = lambda c: dw[dw["code"] == c].set_index("window").reindex(wins)                                       # noqa: E731
    cent = {c: pd.DataFrame({"x": tw(c)["tilting sets (mean)"], "y": tw(c)["propulsive units (median)"]}) for c in ARCH3}
    pts = _centre_trajectory5(ax, cent)
    ax.set_xlim(-0.15, 2.95)
    ax.set_ylim(0, 10.6)
    ax.set_xlabel("tilting sets per design (mean)")
    ax.set_ylabel("propulsors per design (median)")
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    handles = [Line2D([], [], color=style.cls(c).color, marker=style.cls(c).marker, markersize=5, linewidth=1.3, label=LABEL3[c]) for c in ARCH3]
    handles += [_hollow_handle("hollow, in colour: few designs (≤2015)", style.INK), _hollow_handle("hollow, grey: 2024-26* (incomplete)")]
    leg = ax.legend(handles=handles, loc="upper right", fontsize=MIN_PT, frameon=True, framealpha=0.95, edgecolor="none", handlelength=1.6, labelspacing=0.3)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    lab = [COHORT_TICK[wins[k]] for _, _, k, _ in pts]
    failed = plots.place_labels(ax, [p[0] for p in pts], [p[1] for p in pts], lab, [3.6] * len(pts),
                                obstacles=[leg.get_window_extent(rend).expanded(1.03, 1.1)], fontsize=MIN_PT)
    assert not failed, failed
    for t in ax.texts:
        if t.get_text() == COHORT_TICK[INCOMPLETE]:
            t.set_color(style.MUTED)
    data = dw[dw["code"].isin(ARCH3)][["class", "window", "aircraft", "tilting sets (mean)", "propulsive units (median)"]]
    return fig, _csv_cohorts(data.reset_index(drop=True))


# ---- the writer
#: name -> (group, role, builder, width as a share of the text block, what it shows); the composite has no CSV of its own
REFRESH = {
    "q6_leading_layout_by_architecture": ("IV1_layout_convergence", "main", fig_layout_rows, 1.0,
                                          "layouts inside Separate Lift + Cruise, Tilt Propulsor and CVT per cohort, one row each; 2024-26 drawn, incomplete"),
    "q6_architecture_centres_tilting_units": ("IV1_layout_convergence", "main", fig_centres5, FRAC62,
                                              "centre of each architecture per cohort (mean tilting sets, median propulsors), arrows in time order; 2024-26 hollow grey"),
    "q6_boom_share_by_architecture": ("IV2_attributes_and_drivers", "main", fig_boom_share5, FRAC62,
                                      "share with propulsors on booms per architecture and cohort, Spearman tests; 2024-26 drawn, not tested"),
    "q6_cvt_units_on_booms": ("IV2_attributes_and_drivers", "main", fig_cvt_booms5, FRAC62,
                              "CVT share with propulsors on booms per cohort, with rho and p; 2024-26 drawn, not tested"),
    "q6_ducted_share_by_architecture": ("IV2_attributes_and_drivers", "main", fig_ducted_share5, FRAC62,
                                        "share with a ducted propulsor per architecture and cohort; 2024-26 drawn, not tested"),
    "q6_cvt_ducted_by_boom_layout": ("IV2_attributes_and_drivers", "main", fig_cvt_ducted_booms5, FRAC62,
                                     "CVT ducted share with and without propulsors on booms, with the tests; 2024-26 drawn, not tested"),
    "q6_iv1_traces": ("IV2_attributes_and_drivers", "main", fig_iv1_traces, 1.0,
                      "composite of q6_boom_share_by_architecture, q6_cvt_units_on_booms, q6_ducted_share_by_architecture, q6_cvt_ducted_by_boom_layout "
                      "as panels (a) to (d), 16 x 9.3 cm, one legend line per row (rebuilt 2026-10-17)"),
}


def draw_refresh(name: str, ctx):
    """Build one refreshed figure under the thesis style at its final width, every text at 7 pt or more; returns (fig, data, (overlaps, small))."""
    group, role, builder, frac, _ = REFRESH[name]
    old = ctx.W
    ctx.W = TEXT_CM / 2.54 * frac
    try:
        with plt.style.context(str(Path(p4.__file__).with_name("part1.mplstyle"))):
            fig, data = builder(ctx)
            floor = FLOOR.get(name, MIN_PT)
            for t in fig.findobj(Text):
                if t.get_text() and t.get_fontsize() < floor:
                    t.set_fontsize(floor)
            fig.canvas.draw()
            chk = (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, floor)))
    finally:
        ctx.W = old
    return fig, data, chk


def incomplete_cohort_numbers(ctx) -> dict:
    """The values of the 2024-26 cohort behind every refreshed figure (drawn, never tested), for the report: layout shares per architecture,
    the traces per architecture, and the CVT ducted shares by boom layout."""
    d = q6._data(ctx)
    pm = d["pmix5"]
    pm = pm[pm["window"].eq(INCOMPLETE) & pm["code"].isin(ARCH3)]
    lay = pd.DataFrame([{"architecture": LABEL3[r["code"]], "layout": q6.DISPLAY[r["code"]](r["configuration"]), "designs": int(r["aircraft"]),
                         "of": int(r["class aircraft"]), "share": f"{100 * r['aircraft'] / r['class aircraft']:.1f} %"} for _, r in pm.iterrows()])
    dw = d["dw5"]
    tr = dw[dw["window"].eq(INCOMPLETE) & dw["code"].isin(ARCH3)][["class", "aircraft", "tilting sets (mean)", "propulsive units (median)", "share with units on booms",
                                                                   "share with a ducted unit", "aircraft, units on booms", "ducted share, units on booms",
                                                                   "aircraft, no units on booms", "ducted share, no units on booms"]].copy()
    tr["class"] = tr["class"].map(lambda c: next(LABEL3[k] for k in ARCH3 if style.cls(k).name == c))
    return {"layouts": lay.reset_index(drop=True), "traces": tr.reset_index(drop=True)}


def export_refresh(cfg, ctx):
    """Write the seven refreshed figures (pdf) to LaTeX_v15/Figures/Part_IV_design_space_evolution/<group>/main/, the six CSVs to
    Data_for_writing/csv/, the 2024-26 values to Data_for_writing/NUMBERS_IV_incomplete_cohort.md (NUMBERS_IV.md itself stays on the four
    complete cohorts), append the manifest lines; returns (checks, the LaTeX_v15-relative paths written)."""
    R = root(cfg)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    checks, rel = [], []
    for name, (group, role, _, frac, shows) in REFRESH.items():
        fig, data, chk = draw_refresh(name, ctx)
        out = R / "Figures" / PART / group / role
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / f"{name}.pdf", bbox_inches=None if name in FLOOR else "tight")      # the composite is laid out at its exact size
        checks.append({"figure": name, "width cm": round(fig.get_figwidth() * 2.54, 2), "height cm": round(fig.get_figheight() * 2.54, 2),
                       "text over text": chk[0], "under 7 pt": chk[1]})
        plt.close(fig)
        rel.append(f"Figures/{PART}/{group}/{role}/{name}.pdf")
        lines = [(rel[-1], shows)]
        if data is not None:
            data.to_csv(csvd / f"{name}.csv", index=False)
            rel.append(f"Data_for_writing/csv/{name}.csv")
            lines.append((rel[-1], f"data behind {name}, the 2024-26 (incomplete) rows added"))
        _manifest(R, lines)
    nums = incomplete_cohort_numbers(ctx)
    md = ["# NUMBERS_IV, the incomplete 2024-26 cohort (drawn, never tested)\n",
          "Written by notebook 51 (`viz/thesis_latex_part4.py`, refresh of 2026-10-16). The 2024-26 cohort is the fifth column or point of the Analysis IV figures; "
          "it enters no test, no disparity and no number of `NUMBERS_IV.md`, which stays on the four complete cohorts. Designs with a priority year of 2024 or later.\n",
          "## Layout shares, 2024-26 (share of the architecture's designs)\n", "Source: `q6_leading_layout_by_architecture.csv`, rows `2024-26 (incomplete)`.\n",
          tables_md(nums["layouts"]), "",
          "## Traces, 2024-26 (per architecture)\n",
          "Source: `q6_architecture_centres_tilting_units.csv`, `q6_boom_share_by_architecture.csv`, `q6_cvt_units_on_booms.csv`, `q6_ducted_share_by_architecture.csv`, "
          "`q6_cvt_ducted_by_boom_layout.csv`, rows `2024-26 (incomplete)`. A cell is blank under 5 designs (the same rule as every other cohort).\n",
          tables_md(nums["traces"]), ""]
    (R / "Data_for_writing" / "NUMBERS_IV_incomplete_cohort.md").write_text("\n".join(md), encoding="utf-8")
    rel.append("Data_for_writing/NUMBERS_IV_incomplete_cohort.md")
    _manifest(R, [(rel[-1], "the values of the incomplete 2024-26 cohort drawn in the Analysis IV figures (never tested)")])
    return pd.DataFrame(checks), rel


def _manifest(R: Path, lines, used: bool = True) -> None:
    mf = R / "Data_for_writing" / "MANIFEST.md"
    new = not mf.exists()
    with open(mf, "a", encoding="utf-8") as f:
        if new:
            f.write("# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n")
        have = mf.read_text(encoding="utf-8") if not new else ""
        for p, what in lines:
            if f"`LaTeX_v15/{p}`" not in have:
                f.write(f"- `LaTeX_v15/{p}` · {'yes' if used else 'no (leaves the text)'} · {what}\n")


def handover_copy(cfg, rel_paths) -> list:
    """Copy the LaTeX_v15-relative files to <repository root>/outputs_for_thesis_2026-10-16/<same path>; returns the folder's tree."""
    import shutil
    R = root(cfg)
    repo = Path(__file__).resolve().parents[2]
    dst = repo / OUTPUTS
    for d in (dst, repo / MIRROR):                        # the hand-over folder and the git-tracked mirror the Windows side reads
        for p in rel_paths:
            (d / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(R / p, d / p)
    return sorted(str(p.relative_to(dst)) for p in dst.rglob("*") if p.is_file())
