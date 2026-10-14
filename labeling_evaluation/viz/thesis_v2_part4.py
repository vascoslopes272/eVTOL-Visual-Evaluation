"""Part IV figures, v2: the two new Q6 figures of Analysis IV, drawn under the author's thesis style (viz/part1.mplstyle) and
written to thesis_figures_v2/Part_IV_<name>/ like Parts I and II. Every number comes from the existing frames unchanged:
viz.q6._data (config frame ``cf``), lib.drivers.trend_test, lib.dominant_design (Rao's Q, permutation band),
viz.frames.gower_inputs. Nothing else is computed; no existing figure is touched.

Terminology (author's ruling 2026-10-11): architecture, cohort, configuration, disparity; level codes A, A.W.T, A.U.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text

from lib import dominant_design as dd
from lib import drivers
from viz import frames, plots, style
from viz import thesis_q6 as q6

FS = 8.0
ARCH = ["TR", "CVT", "TW"]
NAME = {"TR": "Tilt Propulsor", "CVT": "CVT", "TW": "Tilt Wing"}


def fig_tilt_mechanisms_per_propulsor(ctx):
    d = q6._data(ctx)
    cf = d["cf"]
    x = cf[cf["topType"].isin(ARCH) & cf["units"].gt(0)].copy()
    x["per unit"] = x["sets"] / x["units"]
    wins = ctx.COMPLETE
    fr, rows, leg = {}, [], {}
    for c in ARCH:
        s = x[x["topType"].eq(c)]
        t = drivers.trend_test(s["year"], s["per unit"])
        fr[c] = pd.Series({w: (s.loc[s["window"].eq(w), "per unit"].mean() if s["window"].eq(w).sum() >= drivers.MIN_CELL else np.nan)
                           for w in wins})
        for w in wins:
            rows.append(dict(architecture=NAME[c], cohort=w, aircraft=int(s["window"].eq(w).sum()),
                             mean_per_unit=fr[c][w], rho=t["rho"], p=t["p"], aircraft_in_test=t["aircraft"]))
        leg[c] = f"{NAME[c]} (ρ {t['rho']:+.2f}, {q6._ptxt(t['p'])})".replace("-", "−")
    fig, ax = plt.subplots(figsize=(ctx.W * 0.7, 3.0), constrained_layout=True)
    plots.few_band(ax, 2)
    last = len(wins) - 1
    ax.axvspan(last - 0.5, last + 0.5, facecolor="none", zorder=0, linewidth=0, hatch=plots.PARTIAL_HATCH, edgecolor=style.GRID)
    plots.window_lines(ax, pd.DataFrame(fr)[ARCH], n_few=2, ticks=[ctx.WSHORT[w] for w in wins])
    ax.set_xlim(-0.5, len(wins) - 0.5)
    ax.set_ylim(0, 0.75)
    q6._ygrid(ax)
    ax.set_ylabel("mean tilt mechanisms per\npropulsor unit")
    h = q6._class_handles(ARCH, "line")
    for hh, c in zip(h, ARCH):
        hh.set_label(leg[c])
    fig.legend(handles=h, loc="outside lower center", ncol=1, fontsize=FS, handlelength=2.0)
    return fig, pd.DataFrame(rows)


def _between(D, a, b) -> float:
    """Rao between-group distance of two sets of rows of D: mean D over the pairs (i in a, j in b) minus the mean of their two Q."""
    return float(np.nanmean(D[np.ix_(a, b)])) - (dd.mean_pairwise_distance(D, a) + dd.mean_pairwise_distance(D, b)) / 2


def dispersion(ctx, perms: int = 200, seed: int = 42, min_aircraft: int = 10):
    """Condition 3 at A (every aircraft with an architecture), subsystem weighting: Q per cohort (cohesion_band) and the Rao
    between-group distance of each cohort to the first, with the band of the same shuffles of aircraft across cohorts."""
    v, ds = ctx.v, ctx.ds
    frame, fields, numeric = frames.gower_inputs(ds)
    at = {a: i for i, a in enumerate(frame["aircraft_id"].to_numpy())}
    w = frames._dist.subsystem_weights(fields, frames.SUBSYSTEM_OF)
    D = frames._dist.gower_distance(frame, fields, numeric, w)
    sub = v[frames.archetype_key(v, "A0").notna()].dropna(subset=["window"]).copy()
    sub["row"] = sub["aircraft_id"].map(at)
    sub = sub[sub["row"].notna()]
    rows, win = sub["row"].astype(int).to_numpy(), sub["window"].to_numpy()
    names = ctx.WIN_NAMES
    q = dd.cohesion_band(D, rows, win, names, perms=perms, seed=seed, min_aircraft=min_aircraft)
    per = {x: rows[win == x] for x in names}
    first = ctx.COMPLETE[0]
    obs = {x: _between(D, per[x], per[first]) for x in ctx.COMPLETE}
    rng = np.random.default_rng(seed)
    draws = {x: [] for x in ctx.COMPLETE}
    for _ in range(perms):
        sh, cut, blk = rng.permutation(rows), 0, {}
        for x in names:
            blk[x] = sh[cut:cut + len(per[x])]
            cut += len(per[x])
        for x in ctx.COMPLETE:
            draws[x].append(_between(D, blk[x], blk[first]))
    b = pd.DataFrame([dict(cohort=x, aircraft=len(per[x]), d_between=round(obs[x], 4),
                           d_between_low=round(float(np.percentile(draws[x], 2.5)), 4),
                           d_between_high=round(float(np.percentile(draws[x], 97.5)), 4)) for x in ctx.COMPLETE])
    q = q[q["window"].isin(ctx.COMPLETE)].rename(columns={"window": "cohort"})
    return b.merge(q.drop(columns="aircraft"), on="cohort"), len(fields), len(frame)


def fig_centroid_dispersion(ctx):
    t, _, _ = dispersion(ctx)
    wins = list(t["cohort"])
    x = np.arange(len(wins))
    ticks = [f"{ctx.WSHORT[w]}\nn {n}" for w, n in zip(wins, t["aircraft"])]
    fig, axs = plt.subplots(1, 2, figsize=(ctx.W, 3.4), constrained_layout=True)
    a = axs[0]
    a.fill_between(x, t["d_between_low"], t["d_between_high"], color="#dedcd8", zorder=1, linewidth=0)
    a.axhline(0, color=style.MUTED, linewidth=0.8, zorder=2)
    a.plot(x, t["d_between"], marker="o", markersize=3.6, linewidth=1.5, color=style.INK, zorder=4)
    a.set_ylabel("distance of the cohort from ≤2011\n(Rao between-cohort, Gower)")
    plots.cohesion_panel(axs[1], t, None, [False] * len(t), ticks)
    for ax, y, lo, hi in ((a, t["d_between"], t["d_between_low"], t["d_between_high"]), (axs[1], t["ΔQ"], t["ΔQ permutation low"], t["ΔQ permutation high"])):
        out = [i for i in range(len(t)) if y[i] < lo[i] or y[i] > hi[i]]        # outside the band, above or below
        if out:
            ax.plot(x[out], y.to_numpy()[out], "o", markersize=7.2, color=plots.MET, markeredgecolor=style.INK, markeredgewidth=0.8, zorder=5)
    axs[1].set_ylabel("ΔQ: change in how unlike two aircraft\nare, against the two earliest cohorts")
    a.set_xticks(x, ticks)
    a.set_xlim(-0.5, len(wins) - 0.5)
    a.grid(axis="y", color=style.GRID, linewidth=0.5)
    a.set_axisbelow(True)
    for ax in axs:
        ax.axvspan(len(wins) - 1.5, len(wins) - 0.5, facecolor="none", zorder=0, linewidth=0, hatch=plots.PARTIAL_HATCH, edgecolor=style.GRID)
        ax.set_xlabel("priority cohort", fontsize=FS)
    fig.legend(handles=[Patch(facecolor="#dedcd8", label="permutation band (95 %)"),
                        Line2D([], [], color=style.INK, marker="o", markersize=3.6, linewidth=1.5, label="observed"),
                        Line2D([], [], marker="o", markersize=7, color=plots.MET, markeredgecolor=style.INK, linestyle="none", label="outside the band")],
               loc="outside lower center", ncol=3, fontsize=FS, handlelength=1.8, columnspacing=1.2)
    return fig, t




def numbers(ctx) -> dict:
    """The numbers the text quotes, recomputed from the same frames the two figures draw."""
    cf = q6._data(ctx)["cf"]
    x = cf[cf["topType"].isin(ARCH) & cf["units"].gt(0) & cf["window"].isin(ctx.COMPLETE)].copy()
    x["per unit"] = x["sets"] / x["units"]
    t, n_fields, n_air = dispersion(ctx)
    return {"pooled mean tilt mechanisms per propulsor unit, three architectures": x.groupby("window")["per unit"].mean().reindex(ctx.COMPLETE).round(3),
            "distance and dispersion, per cohort": t, "fields in the distance": n_fields, "aircraft in the distance": n_air, **{"QUOTED: " + k: v for k, v in quoted_numbers(ctx).items()}}


# ================================================================================== the existing Q6 figures, relabelled and restyled
RELABEL = [(r"\bclasses\b", "architectures"), (r"\bclass's\b", "architecture's"), (r"\bclass\b", "architecture"),
           (r"\bwindows\b", "cohorts"), (r"\bwindow\b", "cohort"), (r"\barchetypes\b", "configurations"), (r"\barchetype\b", "configuration")]
COLUMNS = {"class": "architecture", "window": "cohort", "class aircraft": "architecture aircraft", "archetype": "configuration"}


def _relabel(text: str) -> str:
    for pat, rep in RELABEL:
        text = re.sub(pat, rep, text)
    return text


def restyled(builder, keep_panel_titles: bool = False):
    """A builder of viz/thesis_q6.py run UNCHANGED (same frame, same numbers), with every text clamped to FS pt or more while it
    draws (so its own label placement sees the final size), then every text relabelled in British English and the in-figure
    titles dropped (panel headings kept only where they name the architecture of a panel). The data's column names are relabelled."""
    def build(ctx):
        orig = Text.set_fontsize

        def clamp(self, size):
            orig(self, max(FS, size) if isinstance(size, (int, float)) else size)

        Text.set_fontsize = clamp
        try:
            fig, data = builder(ctx)
        finally:
            Text.set_fontsize = orig
        for t in fig.findobj(Text):
            if t.get_text():
                t.set_text(_relabel(t.get_text()))
        for ax in fig.axes:
            if not keep_panel_titles:
                ax.set_title("")
        if data is not None:
            data = data.rename(columns=lambda c: _relabel(COLUMNS.get(c, c)))
        return fig, data
    return build


# ================================================================================== the numbers the text quotes
def quoted_numbers(ctx) -> dict:
    """Each number the thesis text quotes for the Analysis IV figures, read from the frames the figures draw (nothing typed)."""
    d = q6._data(ctx)
    dw, lk, w = d["dw"], d["links"], ctx.COMPLETE
    cv = dw[dw["code"] == "CVT"].set_index("window").reindex(w)
    sl = dw[dw["code"] == "SLC"].set_index("window").reindex(w)
    tr = dw[dw["code"] == "TR"].set_index("window").reindex(w)
    pm = d["pmix"]

    top = {c: pm[(pm["code"] == c) & (pm["window"] == w[-1])].assign(share=lambda t: t["aircraft"] / t["class aircraft"])
           .sort_values("share", ascending=False)[["configuration", "aircraft", "class aircraft", "share"]] for c in ("SLC", "TR", "CVT")}
    lt = lk[lk["link"].str.startswith("CVT")].set_index("group")
    tp = lk[lk["link"].str.startswith("Tilt Rotor")][["group", "aircraft", "median"]]
    tab = lambda s, f=lambda v: f"{100 * v:.1f} %": [f(v) if v == v else "n/a" for v in s]            # noqa: E731
    return {
        "CVT, share with propulsor units on booms, per cohort (text: 20 % -> 62 %)": dict(zip(w, tab(cv["share with units on booms"]))),
        "Lift + Cruise, share with propulsor units on booms, per cohort (text: 56 %)": dict(zip(w, tab(sl["share with units on booms"]))),
        "CVT, share with a ducted propulsor unit, per cohort (caption 80 % -> 32 %; structure document 75 % -> 32 %)": dict(zip(w, tab(cv["share with a ducted unit"]))),
        "CVT ducted share by boom layout, units on booms (text: 35 % -> 6.1 %)": dict(zip(w, tab(cv["ducted share, units on booms"]))),
        "CVT ducted share by boom layout, no units on booms": dict(zip(w, tab(cv["ducted share, no units on booms"]))),
        "CVT ducted share by boom layout, trend tests": lt[["aircraft", "rho", "p", "movement"]].round(4).to_dict("index"),
        "Tilt Propulsor, median propulsor units by tilting sets (text: 2 -> 4)": tp.to_dict("records"),
        "Tilt Propulsor, median propulsor units per cohort": dict(zip(w, tr["propulsive units (median)"].round(2))),
        "layout shares in 2020-23, largest first (text: Lift + Cruise 48 %, CVT 53 %, Tilt Propulsor second tilting set 39 %)":
            {c: t.assign(share=t["share"].map(lambda v: f"{100 * v:.1f} %")).drop(columns="class aircraft").to_dict("records") for c, t in top.items()},
    }


# ================================================================================== items + writer
def _it(name, group, role, builder, title, source_item, **kw):
    return dict(name=name, group=group, role=role, kind="figure", builder=builder, title=title, source_item=source_item, **kw)


ITEMS = [
    _it("q6_leading_layout_by_architecture", "IV1_layout_convergence", "main", restyled(q6.fig_leading_layout_by_class, keep_panel_titles=True),
        "Layouts inside the three largest architectures", "v2 of q6_leading_layout_by_class (Figure 13 (ii))", old="q6_leading_layout_by_class"),
    _it("q6_architecture_centres_tilting_units", "IV1_layout_convergence", "appendix", restyled(q6.fig_class_centres_tilting_units),
        "Architecture centres in tilting sets and propulsor units", "v2 of q6_class_centres_tilting_units (Figure 14 (i))", old="q6_class_centres_tilting_units"),
    _it("q6_tp_units_by_tilting_sets", "IV1_layout_convergence", "appendix", restyled(q6.fig_tp_units_by_tilting_sets),
        "Tilt Propulsor units by tilting sets", "v2 of q6_tp_units_by_tilting_sets (Figure 14 (ii))", old="q6_tp_units_by_tilting_sets"),
    _it("q6_cvt_units_on_booms", "IV2_attributes_and_drivers", "appendix", restyled(q6.fig_cvt_units_on_booms),
        "CVT designs with propulsor units on booms", "v2 of q6_cvt_units_on_booms (Figure 14 (iii))", old="q6_cvt_units_on_booms"),
    _it("q6_boom_share_by_architecture", "IV2_attributes_and_drivers", "appendix", restyled(q6.fig_boom_share_by_class),
        "Propulsor units on booms per architecture", "v2 of q6_boom_share_by_class (Figure 15 (i))", old="q6_boom_share_by_class"),
    _it("q6_ducted_share_by_architecture", "IV2_attributes_and_drivers", "appendix", restyled(q6.fig_ducted_share_by_class),
        "Ducted propulsor unit per architecture", "v2 of q6_ducted_share_by_class (Figure 15 (ii))", old="q6_ducted_share_by_class"),
    _it("q6_cvt_ducted_by_boom_layout", "IV2_attributes_and_drivers", "appendix", restyled(q6.fig_cvt_ducted_by_boom_layout),
        "CVT ducting inside each boom layout", "v2 of q6_cvt_ducted_by_boom_layout (Figure 14 (iv))", old="q6_cvt_ducted_by_boom_layout"),
    _it("q6_tilt_mechanisms_per_propulsor", "IV2_attributes_and_drivers", "appendix", fig_tilt_mechanisms_per_propulsor,
        "Tilt mechanisms per propulsor unit", "new (Analysis IV)", old="new"),
    _it("q6_centroid_dispersion", "IV3_centre_and_disparity", "main", fig_centroid_dispersion,
        "Distance between cohorts and dispersion within them", "new (Analysis IV)", old="new"),
]


def out_root(cfg):
    """thesis_figures_v2/Part_IV_design_space_evolution/, a sibling of Part_I_ and Part_II_ (the originals are never written into)."""
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_IV_design_space_evolution"


def save_v2_item(item: dict, cfg, ctx):
    """Build one item under viz/part1.mplstyle and write <out_root>/<group>/<role>/<name>.{pdf,png,csv,json}; returns (obj, data)."""
    with plt.style.context(str(Path(__file__).with_name("part1.mplstyle"))):
        obj, data = item["builder"](ctx)
        out = out_root(cfg) / item["group"] / item["role"]
        out.mkdir(parents=True, exist_ok=True)
        name = item["name"]
        for ext in cfg.style.get("formats", ["pdf", "png"]):
            obj.savefig(out / f"{name}.{ext}")
        data.to_csv(out / f"{name}.csv", index=False)
        meta = {k: item[k] for k in ("name", "group", "role", "kind", "title", "source_item", "old")}
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
        (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return obj, data
