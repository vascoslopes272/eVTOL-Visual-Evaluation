"""Analysis IV.2, two new figures (author's request 2026-10-15), drawn from the per-design characterised record (viz.thesis_q6._data: the
config frame ``cf`` and the layout mix ``pmix``, the frames behind q6_architecture_centres_tilting_units and q6_leading_layout_by_architecture):

* q6_iv2_merge_cvt_lc: CVT and Lift + Cruise designs of 2012-15 and 2020-23 on the axes of the centres plot (tilting sets per design,
  propulsors per design), one outline per architecture per cohort, and the centre path of each architecture over the four complete cohorts.
* q6_iv2_split_tp: Tilt Propulsor in the four complete cohorts as a branching schematic (Frenken, Saviotti and Trommetter 1999, Fig. 3 style):
  one bubble per branch per cohort, bubble area = design count; one patent drawing at three branch ends.

2024-26 is left out. Written to LaTeX_v15/Figures/Part_IV_design_space_evolution/IV2_attributes_and_drivers/main/ (PDF, PNG, CSV).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

from viz import figcheck, plots, style
from viz import thesis_q6 as q6
from viz.thesis_latex_common import root

FS = 8.0
COH = ["<= 2011", "2012-15", "2016-19", "2020-23"]
COH_LABEL = {"<= 2011": "≤2011", "2012-15": "2012-15", "2016-19": "2016-19", "2020-23": "2020-23"}
PART = "Part_IV_design_space_evolution"
GROUP = "IV2_attributes_and_drivers"
STEM_A, STEM_B = "q6_iv2_merge_cvt_lc", "q6_iv2_split_tp"
#: the three drawings (design id, figure key, why), looked at among the approved line drawings of each layout
PICKS_B = {
    ("one", "<= 2011"): ("US2013026303A1_ua1", "13", "Top view of the Project Zero layout: the two tilting rotor pairs on one wing show plainly (the choice of the layout figure's earlier version)"),
    ("one", "2020-23"): ("US2021331792A1_ua1", "Fu_D00006", "Top view: the two tilting rotors at the wing tips are the only tilting set, with the fixed tail; no reference numerals over the rotors"),
    ("two", "2020-23"): ("US2021229802A1_ua2", "18", "Top view of the hover configuration: four tilting rotors at the ends of a fore and an aft wing, two tilting sets in two places"),
}


def _poly_centroid(P: np.ndarray) -> tuple:
    x, y = P[:, 0], P[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cr = x * y1 - x1 * y
    a = cr.sum() / 2
    return float(((x + x1) * cr).sum() / (6 * a)), float(((y + y1) * cr).sum() / (6 * a))


# ============================================================================================== Gower distance CVT to Lift + Cruise
def _form_distance(ctx):
    from viz import frames
    frame, fields, numeric = frames.gower_inputs(ctx.ds)
    D = frames._dist.gower_distance(frame, fields, numeric, frames.form_weights(fields))
    return D, {a: i for i, a in enumerate(frame["aircraft_id"])}


def _groups(ctx, at):
    """Design rows (index into D) of Lift + Cruise, all CVT and CVT* (CVT with tilting propulsors on a fixed wing: the CVT designs of family F)."""
    from viz import frames
    v = ctx.v
    flags = frames.family_flags(ctx.ds, v)
    fam = set(flags.loc[frames.family_mask(flags), "aircraft_id"])
    w = v.dropna(subset=["window", "topType"])[["aircraft_id", "topType", "window"]]
    w = w[w["aircraft_id"].isin(at)].assign(row=lambda t: t["aircraft_id"].map(at))
    cvt = w[w["topType"] == "CVT"]
    return {"Lift + Cruise": w[w["topType"] == "SLC"], "CVT": cvt, "CVT*": cvt[cvt["aircraft_id"].isin(fam)]}


def _between(D, a, b) -> float:
    """Mean Gower distance over the pairs (one design of ``a``, one of ``b``), NaN-aware."""
    return float(np.nanmean(D[np.ix_(a, b)])) if len(a) and len(b) else float("nan")


def cvt_lc_distance(ctx, perms: int = 200) -> pd.DataFrame:
    """Between-group Gower distance (34 dimensions, the condition-3 weights) of Lift + Cruise to CVT* and to all CVT, per cohort; the change from
    2012-15 to 2020-23 with a permutation band: the cohort labels of the 2012-15 and 2020-23 designs are shuffled WITHIN each architecture
    (CVT*, CVT and Lift + Cruise keep their sizes), 200 permutations, seed 42, band = 2.5 and 97.5 percentiles of the change."""
    D, at = _form_distance(ctx)
    g = _groups(ctx, at)
    slc = g["Lift + Cruise"]
    rows = []
    for name in ("CVT*", "CVT"):
        c = g[name]
        row = {"group": name}
        for w in COH:
            a, b = c[c["window"] == w]["row"].to_numpy(), slc[slc["window"] == w]["row"].to_numpy()
            row[f"distance {COH_LABEL[w]}"] = round(_between(D, a, b), 4)
            row[f"designs {COH_LABEL[w]}"] = f"{len(a)} / {len(b)}"
        w0, w1 = COH[1], COH[3]
        rng = np.random.default_rng(ctx.SEED)
        pools = [(c, c[c["window"].isin([w0, w1])]), (slc, slc[slc["window"].isin([w0, w1])])]
        lab = [p[1]["window"].to_numpy() for p in pools]
        rws = [p[1]["row"].to_numpy() for p in pools]
        null = []
        for _ in range(perms):
            sh = [rng.permutation(x) for x in lab]
            d0 = _between(D, rws[0][sh[0] == w0], rws[1][sh[1] == w0])
            d1 = _between(D, rws[0][sh[0] == w1], rws[1][sh[1] == w1])
            null.append(d1 - d0)
        obs = row[f"distance {COH_LABEL[w1]}"] - row[f"distance {COH_LABEL[w0]}"]
        lo, hi = np.nanpercentile(null, [2.5, 97.5])
        row.update({"change 2012-15 to 2020-23": round(obs, 4), "band low": round(float(lo), 4), "band high": round(float(hi), 4),
                    "fall outside the band": bool(obs < lo)})
        rows.append(row)
    return pd.DataFrame(rows)


def boom_share(ds, ids) -> pd.Series:
    """Share of a design's propulsors (non-control sets) that sit on booms: boom propulsors / all propulsors; blank where no propulsor is recorded."""
    from viz import frames
    from viz.data import M3_STATIONS
    v = ds.variants.set_index("aircraft_id")
    out = {}
    for a in ids:
        r = v.loc[a]
        tot = boom = 0
        for card in M3_STATIONS:
            nt = frames._n(r.get(f"{card}_ntypes")) or 1
            for pre in ([f"{card}_t{t}_" for t in range(1, nt + 1)] if nt > 1 else [f"{card}_"]):
                c = frames._n(r.get(pre + "count"))
                if c > 0 and frames._s(r.get(pre + "ctrlOnly")) != "True":
                    tot += c
                    boom += c if card == "boom" else 0
        out[a] = boom / tot if tot else np.nan
    return pd.Series(out)


def ordination_axis(D) -> np.ndarray:
    """First axis of a classical (metric) ordination of the Gower distances (missing pairs set to the mean distance)."""
    M = np.where(np.isnan(D), np.nanmean(D), D)
    n = len(M)
    J = np.eye(n) - 1.0 / n
    B = -0.5 * J @ (M ** 2) @ J
    val, vec = np.linalg.eigh(B)
    return vec[:, -1] * np.sqrt(max(val[-1], 0))


def _separation(x, g1, g2) -> float:
    """Area under the ROC curve of x for telling group 1 from group 2 (0.5 = no separation, 1 = perfect), as max(AUC, 1 - AUC)."""
    a, b = np.asarray(x[g1], float), np.asarray(x[g2], float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    auc = (a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()
    return float(max(auc, 1 - auc))


# ============================================================================================== (a) CVT moving toward Lift + Cruise
def fig_merge(ctx):
    d = q6._data(ctx)
    cf, dw = d["cf"], d["dw"]
    archs, cohorts = ("CVT", "SLC"), ("2012-15", "2020-23")
    fig, ax = plt.subplots(figsize=(ctx.W * 0.8, 3.9), constrained_layout=True)
    rng = np.random.default_rng(ctx.SEED)
    rows, hulls = [], {}
    YMAX = 17.0
    ax.set_xlim(-0.3, 2.3)
    ax.set_ylim(0, YMAX)
    # dots
    for c in archs:
        s = style.cls(c)
        for w in cohorts:
            g = cf[(cf["topType"] == c) & (cf["window"] == w) & cf["sets"].notna() & cf["units"].gt(0)]
            jx = g["sets"].to_numpy(float) + rng.uniform(-0.09, 0.09, len(g))
            jy = g["units"].to_numpy(float) + rng.uniform(-0.18, 0.18, len(g))
            early = w == cohorts[0]
            ax.scatter(jx, jy, s=14, marker=s.marker, facecolor="white" if early else s.color, edgecolor=s.color, linewidth=0.8,
                       alpha=0.75, zorder=3, clip_on=True)
            for a_id, x0, y0, xx, yy in zip(g["aircraft_id"], g["sets"], g["units"], jx, jy):
                rows.append(dict(kind="design", architecture=s.name, cohort=w, design=a_id, **{"tilting sets": x0, "propulsors": y0,
                                 "x plotted": round(float(xx), 3), "y plotted": round(float(yy), 3)}))
    # centre path (the centres plot's own frame: mean tilting sets, median propulsor units), all four complete cohorts
    cent = {}
    for c in archs:
        t = dw[dw["code"] == c].set_index("window").reindex(COH)
        cent[c] = pd.DataFrame({"x": t["tilting sets (mean)"], "y": t["propulsive units (median)"]})
        for w in COH:
            rows.append(dict(kind="centre of the cohort (path)", architecture=style.cls(c).name, cohort=w, designs=int(t.loc[w, "aircraft"]),
                             **{"tilting sets": round(float(cent[c].loc[w, "x"]), 3), "propulsors": round(float(cent[c].loc[w, "y"]), 3)}))
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_xlabel("tilting sets per design")
    ax.set_ylabel("propulsors per design")
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 5, 10, 15])
    fig.canvas.draw()
    # outlines (rounded convex hull of the designs' own (sets, propulsors) positions), solid for 2020-23, dashed for 2012-15
    for c in archs:
        s = style.cls(c)
        for w in cohorts:
            g = cf[(cf["topType"] == c) & (cf["window"] == w) & cf["sets"].notna() & cf["units"].gt(0)]
            g = g[g["units"] <= g["units"].quantile(0.9)]               # the outline holds the central 90 % in propulsors (a few designs carry 30 to 138)
            u = g[["sets", "units"]].drop_duplicates().to_numpy(float)
            hull = plots.hull_ring(ax, u[:, 0], u[:, 1], [2.0] * len(u), pad_pt=5, linewidth=1.3, edgecolor=s.color,
                                   linestyle="-" if w == cohorts[1] else (0, (4, 2)))
            P = ax.transData.inverted().transform(hull)
            hulls[(c, w)] = _poly_centroid(P)
            rows.append(dict(kind="outline centre", architecture=s.name, cohort=w, designs=len(g),
                             **{"tilting sets": round(hulls[(c, w)][0], 3), "propulsors": round(hulls[(c, w)][1], 3)}))
    # the centre path on top
    pts = plots.centre_trajectory(ax, cent, n_few=2)
    leg = ax.legend(handles=[Line2D([], [], color=style.cls(c).color, marker=style.cls(c).marker, markersize=5, linewidth=1.3,
                                    label=f"{style.cls(c).name}") for c in archs]
                    + [Line2D([], [], color=style.MUTED, marker="o", markerfacecolor="white", linestyle="none", markersize=4.5, label="2012-15 design, dashed outline"),
                       Line2D([], [], color=style.MUTED, marker="o", linestyle="none", markersize=4.5, label="2020-23 design, solid outline")],
                    loc="upper right", fontsize=FS, frameon=True, framealpha=0.95, edgecolor="none", handlelength=1.6)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    lab = [COH_LABEL[COH[k]] for _, _, k, _ in pts]
    failed = plots.place_labels(ax, [p[0] for p in pts], [p[1] for p in pts], lab, [3.6] * len(pts),
                                obstacles=[leg.get_window_extent(rend).expanded(1.03, 1.1)], fontsize=FS,
                                extra_avoid=[(r_["x plotted"], r_["y plotted"], 2.5) for r_ in rows if r_["kind"] == "design" and r_["y plotted"] < YMAX])
    assert not failed, failed
    # distances CVT -> Lift + Cruise
    out = []
    for w in cohorts:
        dc = float(np.hypot(*(np.array(cent["CVT"].loc[w]) - np.array(cent["SLC"].loc[w]))))
        dh = float(np.hypot(*(np.array(hulls[("CVT", w)]) - np.array(hulls[("SLC", w)]))))
        out.append(dict(kind="distance CVT to Lift + Cruise, centres of the cohort", cohort=w, distance=round(dc, 3)))
        out.append(dict(kind="distance CVT to Lift + Cruise, centres of the outlines", cohort=w, distance=round(dh, 3)))
    n_clip = int((cf[cf["topType"].isin(archs) & cf["window"].isin(cohorts)]["units"] > YMAX).sum())
    out.append(dict(kind="designs above the top of the axis (not drawn)", designs=n_clip))
    ax.text(0.99, 0.02, f"{n_clip} designs with more than {YMAX:.0f} propulsors are not drawn", transform=ax.transAxes, ha="right", va="bottom", fontsize=FS, color=style.MUTED)
    data = pd.concat([pd.DataFrame(rows), pd.DataFrame(out)], ignore_index=True)
    data["cohort"] = data["cohort"].map(lambda w: COH_LABEL.get(w, w) if isinstance(w, str) else w)
    return fig, data


# ============================================================================================== (b) Tilt Propulsor splitting
def _tp_counts(ctx) -> pd.DataFrame:
    m = q6._data(ctx)["pmix"]
    m = m[m["code"] == "TR"]
    key = {"one tilting set": "one", "two or more tilting sets, on one station": "st1",
           "two or more tilting sets, on two or more stations": "st2", "no tilting set recorded": "none"}
    t = m.assign(b=m["configuration"].map(key)).pivot_table(index="window", columns="b", values="aircraft", aggfunc="sum", fill_value=0).reindex(COH)
    t["total"] = m.groupby("window")["class aircraft"].first().reindex(COH)
    return t


def fig_split(ctx):
    from viz import thesis_latex_part4 as h4
    t = _tp_counts(ctx)
    f = ctx.ds.figures
    v = ctx.v.set_index("aircraft_id")
    s = style.cls("TR")
    ONE, ST1, ST2 = 3.0, 1.45, 0.15
    fig, ax = plt.subplots(figsize=(ctx.W, 3.9), constrained_layout=True)
    X = np.arange(4, dtype=float)
    rows = []
    # branch lines: trunk, fork to the two-or-more stem, fork of the stem into one station / two or more stations
    c = style.INK
    ax.plot([-0.95, 3.0], [ONE, ONE], color=s.color, linewidth=1.6, zorder=1, solid_capstyle="butt")
    for (x0, y0, x1, y1) in ((-0.8, ONE, -0.55, (ST1 + ST2) / 2), ):
        ax.add_patch(PathPatch(MPath([(x0, y0), (x0 + 0.25, y0), (x1 - 0.2, y1), (x1, y1)], [1, 4, 4, 4]), fill=False, edgecolor=s.color, linewidth=1.6, zorder=1))
    xs = -0.55
    for yy in (ST1, ST2):
        ax.add_patch(PathPatch(MPath([(xs, (ST1 + ST2) / 2), (xs + 0.2, (ST1 + ST2) / 2), (xs + 0.15, yy), (xs + 0.45, yy)], [1, 4, 4, 4]),
                               fill=False, edgecolor=s.color, linewidth=1.6, zorder=1))
        ax.plot([xs + 0.45, 3.0], [yy, yy], color=s.color, linewidth=1.6, zorder=1, solid_capstyle="butt")
    k = 42.0                                                         # bubble area in pt² per design
    names = {"one": ("one tilting set", ONE), "st1": ("two or more tilting sets,\non one station", ST1), "st2": ("two or more tilting sets,\non two or more stations", ST2)}
    for b, (nm, y) in names.items():
        for i, w in enumerate(COH):
            n = int(t.loc[w, b])
            if n == 0:
                continue
            ax.scatter(X[i], y, s=n * k, color=s.color, alpha=0.9, edgecolor="white", linewidth=0.8, zorder=3)
            r_pt = np.sqrt(n * k / np.pi)
            ax.annotate(f"{n} · {100 * n / t.loc[w, 'total']:.0f} %", (X[i], y), textcoords="offset points",
                        xytext=(0, -(r_pt + 3)), ha="center", va="top", fontsize=FS, color=style.INK, zorder=5)
            rows.append(dict(kind="bubble", cohort=COH_LABEL[w], branch=nm.replace("\n", " "), designs=n, **{"Tilt Propulsor designs in the cohort": int(t.loc[w, "total"]),
                             "share of the cohort": round(n / t.loc[w, "total"], 4)}))
        ax.text(0.5 if b != "one" else 0.5, y + 0.42 if b == "one" else y + 0.62, nm, fontsize=FS, color=style.INK, ha="center", va="bottom") if False else None
    for b, (nm, y) in names.items():
        ax.text(3.45, y, nm, fontsize=FS, color=style.INK, ha="left", va="center")
    for i, w in enumerate(COH):
        if int(t.loc[w, "none"]):
            rows.append(dict(kind="not recorded", cohort=COH_LABEL[w], branch="no tilting set recorded", designs=int(t.loc[w, "none"]),
                             **{"Tilt Propulsor designs in the cohort": int(t.loc[w, "total"])}))
    ax.set_xlim(-2.75, 7.4)
    ax.set_ylim(-1.0, 4.35)
    ax.set_xticks(X, [f"{COH_LABEL[w]}\nn {int(t.loc[w, 'total'])}" for w in COH])
    ax.spines["bottom"].set_bounds(-0.4, 3.4)
    ax.set_yticks([])
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel("priority cohort")
    ax.text(1.5, -0.75, "2020-23: 1 design with no tilting set recorded is not drawn", fontsize=FS, color=style.MUTED, ha="center", va="center") if int(t.loc["2020-23", "none"]) else None
    # three drawings
    pos = {("one", "<= 2011"): (-2.7, ONE), ("one", "2020-23"): (5.5, ONE), ("two", "2020-23"): (5.5, (ST1 + ST2) / 2)}
    for key, (a, fk, why) in PICKS_B.items():
        fr = f[(f.aircraft_id == a) & (f.fig_key.astype(str) == fk) & (f.status == "approved")].iloc[0]
        im = h4._crop(fr["image_path"], float(fr["rotation_deg"]) if pd.notna(fr["rotation_deg"]) else 0.0)
        cx, cy = pos[key]
        W_, H_ = 1.5, 1.45
        ins = ax.inset_axes([cx - (0 if key[1] == "<= 2011" else 0.0), cy - H_ / 2 + 0.1, W_, H_], transform=ax.transData)
        ins.imshow(im, cmap="gray", vmin=0, vmax=255)
        ins.set_xticks([]), ins.set_yticks([])
        for sp in ins.spines.values():
            sp.set_visible(False)
        pn = v.loc[a, "patent_id"]
        ax.text(cx + W_ / 2, cy - H_ / 2 + 0.02, pn, fontsize=FS, ha="center", va="top", color=style.INK)
        rows.append(dict(kind="drawing", cohort=COH_LABEL[key[1]], branch="one tilting set" if key[0] == "one" else "two or more tilting sets",
                         **{"patent number": pn, "design": a, "figure key": fk, "why": why}))
    ax.plot([5.38, 5.38], [ST1, ST2], color=style.MUTED, linewidth=0.8)          # the two branches that end in the one drawing
    for yy in (ST1, ST2):
        ax.plot([5.3, 5.38], [yy, yy], color=style.MUTED, linewidth=0.8)
    return fig, pd.DataFrame(rows)


# ============================================================================================== export
def export(cfg, ctx):
    R = root(cfg)
    out = R / "Figures" / PART / GROUP / "main"
    out.mkdir(parents=True, exist_ok=True)
    chk = []
    for stem, fn in ((STEM_A, fig_merge), (STEM_B, fig_split)):
        with plt.style.context(str(Path(__file__).with_name("part1.mplstyle"))):
            fig, data = fn(ctx)
            fig.canvas.draw()
            chk.append({"figure": stem, "text over text": len(figcheck.overlaps(fig)), "under 7 pt": len(figcheck.small_text(fig, 7.0)),
                        "overlaps": figcheck.overlaps(fig)[:4]})
            fig.savefig(out / f"{stem}.pdf")
            fig.savefig(out / f"{stem}.png", dpi=200)
            data.to_csv(out / f"{stem}.csv", index=False)
            plt.close(fig)
    cvt_lc_distance(ctx).to_csv(out / f"{STEM_A}_distance.csv", index=False)
    return pd.DataFrame(chk), out
