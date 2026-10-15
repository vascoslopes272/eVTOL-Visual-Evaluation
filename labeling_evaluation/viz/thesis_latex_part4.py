"""Part IV hand-over to the dissertation (notebook 51, last section): q6_leading_layout_by_architecture (final width 1.0, three rows) and
q6_centroid_dispersion (leaves the dissertation) remade at their final width in the 16 cm text block, height at most 55 % of the width,
text 7 pt or more, no title inside; written to LaTeX_v15/Figures/Part_IV_design_space_evolution/<group>/<role>/ with the data behind each,
NUMBERS_IV.md and MANIFEST.md (appended). No number, test or result changes: the data are those of viz/thesis_q6.py and
viz/thesis_v2_part4.py; only the layout of the layout figure (three rows instead of three columns) is new."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    pmix = d["pmix"]
    w = ctx.W
    fig, axs = plt.subplots(3, 2, figsize=(w, 3.4), gridspec_kw=dict(width_ratios=[1.0, 0.95], hspace=0.62, wspace=0.02))
    for (ax, kx), c in zip(axs, ["SLC", "TR", "CVT"]):
        m = pmix[pmix["code"] == c]
        lastw = m[m["window"] == "2020-23"].sort_values("aircraft", ascending=False)
        ordc = [k for k in lastw["configuration"] if not frames.cfg_outside(k)]
        keep = ordc[:3] if len(ordc) > 4 else ordc[:4]
        frac = lambda k: (m[m["configuration"].isin(k)].groupby("window")["aircraft"].sum().reindex(ctx.COMPLETE).fillna(0)
                          / m.groupby("window")["class aircraft"].first().reindex(ctx.COMPLETE))
        comp = pd.DataFrame({q6.DISPLAY[c](k): frac([k]) for k in keep})
        rest = frac([k for k in m["configuration"].unique() if k not in keep])
        if rest.sum() > 0:
            comp["other configurations"] = rest
        plots.config_stack(ax, comp, style.cls(c).color, n_few=2, min_label=MIN_LABEL)
        nwin = m.groupby("window")["aircraft"].sum().reindex(ctx.COMPLETE)
        ax.set_xticks(range(len(ctx.COMPLETE)), [f"{ctx.WSHORT[x]}  n {int(n)}" for x, n in zip(ctx.COMPLETE, nwin)])
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_ylabel({"SLC": "Separate\nLift + Cruise", "TR": "Tilt\nPropulsor", "CVT": "Combined\nVectored Thrust"}[c])
        h, lab = ax.get_legend_handles_labels()
        kx.axis("off")
        kx.legend(h[::-1], [p4._relabel(t) for t in lab[::-1]], loc="center left", fontsize=MIN_PT, handlelength=1.1, labelspacing=0.3, frameon=False,
                  title={"SLC": "where the lift units sit", "TR": "how the tilting thrust is split", "CVT": "what tilts · where the fixed units sit"}[c],
                  title_fontsize=MIN_PT, alignment="left")
    fig.subplots_adjust(left=0.125, right=0.995, top=0.985, bottom=0.07)      # room for the two-line architecture names (rerun 2026-10-15)
    return fig, pmix.reset_index(drop=True)


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
