"""Q6 — the design space: where do eVTOL designs concentrate, and how have they moved? (thesis layer, one graph per file)

Sources: notebook 41 (build_41.py §2.1–2.3: Table 6, Figures 6–9) and notebook 42 (build_42.py §3.1, §3.3, §3.4:
Figures 10, 13, 14, 15, Table 9). Every panel of a multi-panel document figure is its own item here; the three class
panels of Figure 13 (ii) (one variable, the composition of a class) stay one figure. The frames are computed once per
context (``_data``) and shared by the builders and by ``numbers``.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import Bbox

from lib import diversity, drivers
from viz import config, flow, frames, plots, style

CLASSES5 = ["SLC", "TR", "CVT", "TW", "MR"]
SETS3 = ["A0", "A0c", "A1t"]
#: Holm families of Analysis IV (sweep of 2026-10-23, promised in 3.4.1): each trace is one family over the three largest architectures
#: (four cohorts to 2023; a constant or too-thin trace leaves the family); the two CVT ducted-by-boom-layout tests are one family of two
HOLM_ARCH = ["SLC", "TR", "CVT"]
HOLM_LINKS = ["units on booms", "no units on booms"]                               # the order of the document's discovery-curve generator
NAMES3 = {"A0": "C", "A0c": "C·U", "A1t": "C·W·T"}
FOCUS, NEIGH = "CVT · 5-6", "CVT · 4"
_AN = config.load(strict=False).analysis                   # the cut-offs the captions print, never typed
MIN_LABEL13 = 0.12                                         # a block of Figure 13 (ii) prints its share from this size
WLAB = {"<= 2011": "≤2011", "2012-15": "2012-15", "2016-19": "2016-19", "2020-23": "2020-23", "2024-26 (partial)": "2024-26*"}


# ------------------------------------------------------------------------------------------------- helpers
def _short(key: str) -> str:
    """A C·U archetype key as the figures print it: 'SLC · 9+' -> 'L+C 9+', 'HB · n/a (no M3 card)' -> 'HB'."""
    c, _, b = key.partition(" · ")
    return f"{style.cls(c).short} {b.replace('n/a (no M3 card)', '')}".strip()


def _ptxt(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p {p:.2f}" if p >= 0.01 else f"p {p:.3f}"


def _pt(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


def _pc(ax):
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))


def _ygrid(ax):
    ax.grid(axis="y", color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def _class_handles(codes, kind: str = "patch"):
    if kind == "patch":
        return [Patch(facecolor=style.cls(c).color, hatch=style.cls(c).hatch, edgecolor="white",
                      label=f"{style.cls(c).short} {style.cls(c).name}" if c != "Other" else "no architecture recorded") for c in codes]
    return [Line2D([], [], color=style.cls(c).color, linestyle=style.cls(c).dash, marker=style.cls(c).marker, markersize=4.6,
                   linewidth=1.4, label=f"{style.cls(c).short} {style.cls(c).name}") for c in codes]


def _data(ctx):
    """Every frame the Q6 items read, computed once per context and cached on it."""
    if getattr(ctx, "_q6", None) is not None:
        return ctx._q6
    cfg, ds, v = ctx.cfg, ctx.ds, ctx.v
    d = {}
    # 2.1 fields and propulsion
    d["t6"] = frames.selected_fields(ds)
    d["cut"] = cfg.analysis["field_drop_top_share"]
    d["dcount"] = frames.duct_count_by_units(v)
    d["dcond"] = frames.duct_conditional(v)
    d["codes"] = [c for c in style.CLASS_ORDER if c in set(v["topType"].dropna())]
    d["feat"], d["read"], d["total"] = frames.arrangement_features(v, d["codes"])
    d["units_by_class"] = [pd.to_numeric(v.loc[v["topType"] == c, "units"], errors="coerce").to_numpy() for c in d["codes"]]
    d["unit"] = frames.propulsor_units(ds.variants)["units"].dropna()
    # 2.2 archetype sets
    levels = frames.archetype_levels_table(ds, v, cfg)
    d["levels"] = levels
    d["brief"] = frames.archetype_levels_brief(ds, v, levels).set_index("level id")
    # 2.3 zones, filers, discovery
    zones = frames.zones(v, ctx.WIN_NAMES, cfg.analysis["zone_min_aircraft"])
    d["zones"] = zones
    d["split"] = frames.archetype_filer_split(v, cfg.analysis["filer_panel_min_aircraft"])
    zz = zones[zones["filers 2016-23"] > 0]
    d["zz"] = zz
    # core (ruling 2026-10-15): the configurations ranked by share of the 2016-23 designs, taken in order until the cumulative share reaches 50 %
    # of those designs (the one that crosses 50 % is included, and so is any configuration tied with it); read on the unrounded shares
    n_recent = int(v["window"].isin(["2016-19", "2020-23"]).sum())
    exact = (zz["2016-19"].astype(float) + zz["2020-23"].astype(float)) / n_recent
    ranked = exact.sort_values(ascending=False, kind="stable")
    k_cross = int(np.searchsorted(ranked.cumsum().to_numpy(), 0.5 - 1e-12))
    d["share_exact"] = exact
    d["core_rank"] = ranked[ranked >= ranked.iloc[k_cross] - 1e-12].index
    d["core"] = zz.loc[d["core_rank"]]
    d["core_share_exact"] = float(ranked.loc[d["core_rank"]].sum())
    d["rim"] = zz[zz["share 2016-23"] <= zz["share 2016-23"].median()]
    d["half"] = {w: frames.half_column(zones[w]) for w in ("2016-19", "2020-23")}
    inputs = frames.discovery_inputs(v, SETS3, cfg.analysis["last_complete_year"])
    curve = diversity.discovery_curve_levels(inputs, orders=cfg.analysis["discovery_orders"], seed=ctx.SEED)
    d["curve"] = curve
    d["est"] = frames.discovery_estimators(inputs, curve, tail=cfg.analysis["discovery_tail"]).set_index("level")
    a0 = curve[curve["level"] == "A0"]
    d["a0"] = a0
    d["hit"] = a0[a0["archetypes (date order)"] >= a0["archetypes (date order)"].max() - 1e-9].iloc[0]
    # 3.1 class mix per window
    cnt = frames.class_counts_by_window(v, ctx.WIN_NAMES)
    d["cnt"] = cnt
    d["n_win"] = cnt.sum(axis=1)
    d["share"] = cnt.div(d["n_win"], axis=0)
    # 3.3 configurations
    frames.set_window_bounds(cfg)
    cf = frames.config_frame(ds, v)
    d["cf"] = cf
    keys = frames.class_config_keys(ds, v, cf, ctx.COMPLETE)
    cn = {c: style.cls(c).name for c in style.CLASS_ORDER}
    d["cn"] = cn
    cc = frames.class_configs_brief(keys, ctx.COMPLETE, ctx.COMPLETE[:2], cn)
    mix = frames.class_config_mix(keys, cn)
    d["cc"] = cc
    d["prop"] = cc[cc["rule set"] == "proposed"]
    d["cur"] = cc[cc["rule set"] == "current"].set_index(["code", "window"])["share in it"]
    d["pmix"] = mix[mix["rule set"] == "proposed"]
    d["poss"] = d["prop"].set_index(["code", "window"])
    # 3.4 traces and drivers
    tf = frames.trace_frame(ds, v)
    classes = drivers.class_selection(v)
    d["classes"] = classes
    drift = drivers.trace_drift(tf, classes, class_names=cn)
    d["trends"] = drivers.trace_trends(tf, drift, classes, class_names=cn)
    d["dw"] = drivers.driver_windows(cf, CLASSES5, ctx.COMPLETE, ctx.COMPLETE[:2], class_names=cn)
    d["links"] = drivers.driver_links(cf)
    d["trends"], d["links"] = _with_holm(d["trends"], d["links"])
    d["spu"] = frames.sets_per_unit_brief(cf, ctx.COMPLETE, ctx.WSHORT)
    # the same two frames over the five cohorts, the incomplete 2024-26 one included (refresh of 2026-10-16: it is DRAWN, never tested;
    # every test above and every number of NUMBERS_IV.md stays on the four complete cohorts). On the complete cohorts they equal dw and pmix.
    d["dw5"] = drivers.driver_windows(cf, CLASSES5, ctx.WIN_NAMES, ctx.COMPLETE[:2], class_names=cn)
    mix5 = frames.class_config_mix(frames.class_config_keys(ds, v, cf, ctx.WIN_NAMES), cn)
    d["pmix5"] = mix5[mix5["rule set"] == "proposed"]
    same = lambda a, b, keys: a[a["window"].isin(ctx.COMPLETE)].sort_values(keys).reset_index(drop=True).equals(b.sort_values(keys).reset_index(drop=True))  # noqa: E731
    assert same(d["dw5"], d["dw"], ["code", "window"]) and same(d["pmix5"], d["pmix"], ["code", "window", "configuration"])
    ctx._q6 = d
    return d


def _with_holm(trends: pd.DataFrame, links: pd.DataFrame):
    """Column ``p_holm`` after ``p``: Holm step-down inside each family (HOLM_ARCH per trace; HOLM_LINKS for the CVT links); NaN outside one."""
    from lib.multiple import holm_by
    trends, links = trends.copy(), links.copy()
    inn = trends["code"].isin(HOLM_ARCH)
    ph = pd.Series(np.nan, index=trends.index)
    ph[inn] = holm_by(trends[inn], "p", ["trace"])
    trends.insert(trends.columns.get_loc("p") + 1, "p_holm", ph)
    inn = links["link"].str.startswith("CVT") & links["group"].isin(HOLM_LINKS)
    ph = pd.Series(np.nan, index=links.index)
    ph[inn] = holm_by(links[inn], "p", [])
    links.insert(links.columns.get_loc("p") + 1, "p_holm", ph)
    return trends, links


def _trend(d, trace: str, code: str) -> pd.Series:
    t = d["trends"]
    return t[(t["trace"] == trace) & (t["code"] == code)].iloc[0]


# ------------------------------------------------------------------------------------------------- A: the design space
def tab_selected_fields(ctx):
    d = _data(ctx)
    t6, cut = d["t6"], d["cut"]
    kept = t6[t6["top_share"] < cut]
    colon = lambda s: " · ".join(f"{a.rsplit(' ', 1)[0]}: {a.rsplit(' ', 1)[1]}" for a in s.split(" · "))
    tab = pd.DataFrame({"field": kept["name"], "aircraft answering": kept["answered"].astype(int),
                        "different answers": kept["answers"].astype(int), "top share": kept["top_share"].map(ctx.pct),
                        "most common answers: aircraft": kept["most common answers"].map(colon)}).reset_index(drop=True)
    return tab, None


#: q6_fixed_by_architecture: an architecture is read when at least this many of its designs answer the dimension; the dimension is
#: "fixed" in it when its leading option holds at least this share of them; permutations of the architecture column
FIXED_MIN_DESIGNS = 10
FIXED_SHARE = 0.80
FIXED_PERMS = 1000


def fixed_by_architecture(ctx, share: float = FIXED_SHARE, min_designs: int = FIXED_MIN_DESIGNS):
    """Which of the dimensions of Table 6 the architecture (topType) fixes: per dimension, on the designs that answer it AND have an
    architecture, the bias-corrected Cramér's V (Bergsma 2013) of dimension x architecture, a permutation p (the architecture column
    shuffled FIXED_PERMS times with one numpy Generator seeded ctx.SEED, dimensions in the order of Table 6 as the v2 table prints it:
    top share ascending), and per architecture the leading option and its share of the architecture's answering designs
    (tie: the option more common over all answering designs). Architectures with fewer than FIXED_MIN_DESIGNS answering designs are
    "too few to read"; the dimension is fixed in an architecture when the leading share is >= ``share`` (FIXED_SHARE, 0.80; the
    sensitivity of supervisor review 2 reads 0.70 and 0.90, the V and p do not depend on it). ``p (Holm)``: the permutation p values of
    the dimensions as ONE family, Holm-adjusted (lib.multiple.holm; supervisor review 2, 2026-10). ``min_designs``: an architecture is
    read when it has at least this many answering designs (FIXED_MIN_DESIGNS, 10; the dissertation's table of 2026-10 reads 20). V and p
    use every architecture and do not depend on it.

    The series are those of :func:`viz.frames.selected_field_series` (the same options dropped as Table 6), so "designs answering"
    equals Table 6's column less the designs without an architecture.
    An architecture with no answering design (HB / PFV on the propulsor rows) counts among the too few. The Cramér's V table drops it.
    Returns (summary, detail): summary one row per dimension with the architecture CODES in the two list columns
    (``fixed codes``, ``too few codes``); detail one row per dimension x architecture (code), designs, leading option, share."""
    from lib import association
    from lib.multiple import holm
    d = _data(ctx)
    t6, cut = d["t6"], d["cut"]
    kept = t6[t6["top_share"] < cut]
    kept = kept.iloc[np.argsort(kept["top_share"].to_numpy(), kind="stable")]
    series = frames.selected_field_series(ctx.ds)
    arch = pd.Series(ctx.v["topType"].to_numpy(), index=ctx.ds.variants.index)       # ctx.v = frames.base(ds), one row per variant, same order
    assert (ctx.v["aircraft_id"].to_numpy() == ctx.ds.variants["aircraft_id"].to_numpy()).all()
    codes = [c for c in style.CLASS_ORDER if c in set(arch.dropna())]
    rng = np.random.default_rng(ctx.SEED)
    rows, detail = [], []
    for name in kept["name"]:
        s = series[name]
        m = s.notna() & arch.notna()
        x, a = s[m].astype(str), arch[m].astype(str)
        order = list(x.value_counts().index)                       # the option order: most common first (Table 6's order)
        ct = pd.crosstab(x, a).reindex(index=order, columns=codes, fill_value=0)      # every architecture: one with no answering design is "too few"
        xi = pd.Categorical(x, categories=ct.index).codes
        ai = pd.Categorical(a, categories=ct.columns).codes
        res = association.cramers_v_permutation(xi, ai, perms=FIXED_PERMS, rng=rng)
        fixed, few = [], []
        for c in ct.columns:
            i, lead = association.leading_share(ct[c].to_numpy())
            n_c = int(ct[c].sum())
            detail.append({"dimension": name, "code": c, "designs": n_c, "leading option": ct.index[i] if i >= 0 else "", "share": lead,
                           "read": n_c >= min_designs})
            (few if n_c < min_designs else (fixed if lead >= share else [])).append(c)
        n_read = sum(int(ct[c].sum()) >= min_designs for c in ct.columns)
        rows.append({"dimension": name, "designs answering": int(res["n"]), "options": int(ct.shape[0]), "architectures": int(ct.shape[1]),
                     "cramers_v": res["v"], "p": res["p"], "fixed": len(fixed), "read": n_read, "fixed codes": fixed, "too few codes": few})
    summary = pd.DataFrame(rows)
    summary.insert(summary.columns.get_loc("p") + 1, "p (Holm)", holm(summary["p"]))
    return summary, pd.DataFrame(detail)


def fig_propulsor_units_per_class(ctx):
    d = _data(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W, 2.7), constrained_layout=True)
    plots.unit_strips(ax, d["codes"], d["units_by_class"], cap=30, seed=ctx.SEED)
    plots.class_ticks(ax, d["codes"], [str(int(n)) for n in d["total"]])
    ax.set_ylabel("propulsor units per aircraft\n(capped at 30)")
    ax.set_xlabel("architecture class, with its aircraft")
    data = pd.concat([pd.DataFrame({"class": style.cls(c).name, "propulsor units": u}) for c, u in zip(d["codes"], d["units_by_class"])],
                     ignore_index=True)
    return fig, data


def fig_arrangement_by_class(ctx):
    d = _data(ctx)
    ROWS = {"at least one tilting propulsor": "≥ 1 tilting", "both fixed and tilting propulsors": "fixed and tilting",
            "a ducted propulsor": "≥ 1 ducted", "more than 8 propulsors": "more than 8"}
    fig, ax = plt.subplots(figsize=(ctx.W, 1.9), constrained_layout=True)
    plots.feature_heat(ax, d["feat"].rename(index=ROWS))
    plots.class_ticks(ax, d["codes"], [f"{n}" if r == n else f"{r}/{n}" for r, n in zip(d["read"], d["total"])])
    data = d["feat"].round(3).reset_index().rename(columns={"index": "feature"})
    return fig, data


def fig_ducting_by_units(ctx):
    d = _data(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.1), constrained_layout=True)
    plots.duct_bands(ax, d["dcount"], d["dcond"])
    ax.set_ylabel("share of the band's aircraft")
    ax.set_xlabel("propulsor-unit band; under it: aircraft · aircraft that duct · median ducted propulsors of those", fontsize=7.5)
    ax.legend(loc="upper left", ncol=2, fontsize=7.5)
    return fig, d["dcount"].merge(d["dcond"], on="propulsive units")


def fig_archetype_filers(ctx):
    d = _data(ctx)
    split, zones = d["split"], d["zones"]
    f7 = split.sort_values("filers per aircraft", ascending=False).merge(zones[["archetype", "code"]], on="archetype")
    f7["label"] = f7["archetype"].map(_short)
    top = split.set_index("archetype").loc[FOCUS]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    plots.filer_bars(ax, f7, [FOCUS, NEIGH], FOCUS,
                     f"{top['largest filer']} holds {int(top['its aircraft'])} of the {int(top['aircraft'])}; {int(top['filers holding one aircraft'])} filers hold one each")
    ax.set_xlim(0, 1.75)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("distinct filers per aircraft (1.00 = every aircraft a different filer)")
    return fig, f7.drop(columns="label")


def _bubble(n):
    return 14 + 2.2 * np.asarray(n, dtype=float)                   # marker area, pt²


def _radius(df):
    return np.sqrt(_bubble(df["aircraft"]) / np.pi)                  # marker radius, pt


def fig_archetype_core(ctx):
    d = _data(ctx)
    zz, core, rim, split = d["zz"], d["core"], d["rim"], d["split"]
    top = split.set_index("archetype").loc[FOCUS]
    mx, my = zz["share 2016-23"].median(), zz["filers per aircraft"].median()
    fig, ax = plt.subplots(figsize=(ctx.W, 5.0), constrained_layout=True)
    for _, r in zz.iterrows():
        s = style.cls(r["code"])
        ax.scatter(r["share 2016-23"], r["filers per aircraft"], s=_bubble(r["aircraft"]), color=s.color, hatch=s.hatch, edgecolor="white",
                   linewidth=0.6, marker={"new": "^", "fading": "v"}.get(r["zone"], "o"), zorder=3)
    ax.set_xlim(-0.002, zz["share 2016-23"].max() * 1.12)
    ax.set_ylim(0.3, 1.06)
    ax.axvline(mx, color=style.GRID, linewidth=1, zorder=0)
    ax.axhline(my, color=style.GRID, linewidth=1, zorder=0)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1, decimals=0))
    ax.set_xlabel("share of the 2016–23 aircraft")
    ax.set_ylabel("distinct filers per aircraft")
    codes8 = [c for c in style.CLASS_ORDER if c in set(zz["code"])]
    handles = _class_handles(codes8) + [Line2D([], [], marker="o", color=style.INK, linestyle="none", label="throughout"),
                                        Line2D([], [], marker="^", color=style.INK, linestyle="none", label="first seen 2016 or later")]
    fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=7.5, handlelength=1.2, columnspacing=1.0)
    fig.canvas.draw()
    ring_core = plots.hull_ring(ax, core["share 2016-23"], core["filers per aircraft"], _radius(core), pad_pt=3, linewidth=1.5)
    ring_rim = plots.hull_ring(ax, rim["share 2016-23"], rim["filers per aircraft"], _radius(rim), pad_pt=3.5, linewidth=1.2,
                               linestyle=(0, (4, 2)), edgecolor=style.MUTED)

    def along(h, pad=3):
        pts = [a + (b - a) * t for a, b in zip(h, np.roll(h, -1, axis=0)) for t in np.linspace(0, 1, 12)]
        return [Bbox([[x - pad, y - pad], [x + pad, y + pad]]) for x, y in pts]

    t_core = ax.text(0.985, 0.03, f"crowded core ({len(core)} archetypes): the\nlargest archetypes, which together hold\nhalf of the 2020-23 aircraft",
                     transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, linespacing=1.15)
    t_rim = ax.text(0.01, 0.3, f"empty rim ({len(rim)} archetypes):\nat or under the median share", transform=ax.transAxes, ha="left", va="bottom",
                    fontsize=7.5, linespacing=1.15, color=style.MUTED)
    cvt = zz[zz["archetype"] == FOCUS].iloc[0]
    callout = (f"{_short(FOCUS)}: {int(cvt['filers'])} filers for {int(cvt['aircraft'])} aircraft,\nthe fewest per aircraft of the {len(split)}\n"
               f"archetypes with {ctx.cfg.analysis['filer_panel_min_aircraft']}+ aircraft; {top['largest filer'].split(' / ')[0]} /\n"
               f"{top['largest filer'].split(' / ')[-1]} holds {int(top['its aircraft'])} of them,\n{int(top['filers holding one aircraft'])} filers hold one each")
    t_cv = ax.text(0.01, 0.02, callout, transform=ax.transAxes, ha="left", va="bottom", fontsize=7.5, linespacing=1.15,
                   bbox=dict(fc="white", ec=style.MUTED, lw=0.6, pad=2.5))
    ax.annotate("", xy=(cvt["share 2016-23"], cvt["filers per aircraft"]), xytext=(0.355, 0.075), textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-", lw=0.8, color=style.INK, shrinkA=0, shrinkB=float(_radius(cvt.to_frame().T)[0]) + 1))
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    obstacles = along(ring_core) + along(ring_rim) + [t.get_window_extent(rend).expanded(1.03, 1.1) for t in (t_core, t_rim, t_cv)]
    lab = zz[(zz["aircraft"] >= 12) | (zz["share 2016-23"] >= 0.03) | (zz["filers per aircraft"] < 0.75)]
    failed = plots.place_labels(ax, lab["share 2016-23"].to_numpy(), lab["filers per aircraft"].to_numpy(), [_short(a) for a in lab["archetype"]],
                                _radius(lab), obstacles=obstacles, fontsize=7,
                                extra_avoid=list(zip(zz["share 2016-23"], zz["filers per aircraft"], _radius(zz))))
    assert not failed, failed
    cols = ["archetype", "class", "aircraft", "filers", "filers per aircraft", "share 2016-23", "zone"]
    return fig, zz[cols].reset_index(drop=True)


def fig_archetype_windows(ctx):
    d = _data(ctx)
    zones, half = d["zones"], d["half"]
    mat = zones.set_index("archetype")[ctx.WIN_NAMES].astype(float).T
    m2 = mat.rename(index=WLAB)
    m2.columns = [_short(a) for a in m2.columns]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.0), constrained_layout=True)
    plots.window_heat(ax, m2, {WLAB[w]: j for w, j in half.items()})
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlabel("C·U archetype, largest first (orange bar: half of the window's aircraft reached)", fontsize=7.5)
    return fig, mat.T.reset_index()


def fig_discovery_curve(ctx):
    d = _data(ctx)
    curve, est, hit = d["curve"], d["est"], d["hit"]
    tail = ctx.cfg.analysis["discovery_tail"]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.4), constrained_layout=True)
    plots.discovery_lines(ax, curve, NAMES3, tail)
    ax.set_xlabel("aircraft, in priority order")
    ax.set_ylabel("distinct archetypes seen")
    ax.set_ylim(0, 48)
    h, l = ax.get_legend_handles_labels()
    h += [Line2D([], [], color="#8c8c8c", linewidth=0.9, linestyle=(0, (1, 1.8))), Patch(facecolor="#bdbdbd", alpha=0.6, linewidth=0)]
    l += ["the same aircraft in random order", "spread over the orderings inside a year"]
    fig.legend(h, l, loc="outside upper center", ncol=3, fontsize=7.5, handlelength=2.6)
    ax.annotate(f"12th class: aircraft {int(hit['aircraft'])}\n(priority {int(hit['priority year reached'])})", xy=(hit["aircraft"], 12),
                xytext=(hit["aircraft"] + 25, 5.5), fontsize=7.5, va="center", arrowprops=dict(arrowstyle="-", lw=0.5))
    lines = [f"the last {tail} aircraft (grey band)", "new archetypes: date order · by chance"] + [
        f"{NAMES3[s]}: {est.loc[s, 'new in the last 100 aircraft']:.1f} · {est.loc[s, 'new in the last 100, random order']:.1f}" for s in SETS3]
    ax.text(0.77, 0.42, "\n".join(lines), transform=ax.transAxes, ha="right", va="center", fontsize=7.5, linespacing=1.3,
            bbox=dict(fc="white", ec="none", pad=2))
    return fig, curve


# ------------------------------------------------------------------------------------------------- B: between classes
def fig_class_shares_by_window(ctx):
    d = _data(ctx)
    cnt, share, n_win = d["cnt"], d["share"], d["n_win"]
    codes10 = [c for c in style.CLASS_ORDER if c in cnt.columns] + ["Other"]
    tick10 = [f"{ctx.WSHORT.get(w, '24–26*')}\nn {int(n)}" for w, n in zip(ctx.WIN_NAMES, n_win)]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    sh = share[codes10].copy()
    sh.index = list(range(len(sh)))
    plots.share_bars(ax, sh, partial=[len(sh) - 1], min_label=0.05, label_kind="pct")
    ax.set_xticks(range(len(ctx.WIN_NAMES)), tick10)
    ax.set_ylabel("share of the cohort's\naircraft")
    ax.set_xlabel("priority cohort (* still filling)")
    fig.legend(handles=_class_handles(codes10), loc="outside lower center", ncol=5, fontsize=7.5, handlelength=1.2, columnspacing=1.0)
    return fig, share.round(4).assign(aircraft=n_win)


def fig_largest_classes_over_time(ctx):
    d = _data(ctx)
    share = d["share"]
    fig, ax = plt.subplots(figsize=(ctx.W, 2.9), constrained_layout=True)
    lines = share[CLASSES5].copy()
    lines.index = list(range(len(lines)))
    plots.window_lines(ax, lines, n_few=0, ticks=[ctx.WSHORT.get(w, "24–26*") for w in ctx.WIN_NAMES])
    ax.axvspan(len(ctx.WIN_NAMES) - 1.5, len(ctx.WIN_NAMES) - 0.5, facecolor=plots.FEW_FILL, hatch=style.PARTIAL_HATCH, edgecolor=style.GRID,
               linewidth=0, zorder=0)
    ax.set_xlim(-0.3, len(ctx.WIN_NAMES) + 0.55)
    _pc(ax)
    _ygrid(ax)
    ax.set_ylim(0.04, 0.37)
    last = lines.iloc[-1]
    plots.end_labels(ax, len(ctx.WIN_NAMES) - 1, [last[c] for c in CLASSES5], [style.cls(c).short for c in CLASSES5],
                     [style.cls(c).color for c in CLASSES5], gap=0.024)
    ax.set_ylabel("share of the cohort's\naircraft")
    ax.set_xlabel("priority cohort (* still filling)")
    fig.legend(handles=_class_handles(CLASSES5, "line"), loc="outside lower center", ncol=5, fontsize=7.5, handlelength=2.0, columnspacing=1.0)
    return fig, share[CLASSES5].round(4)


# ------------------------------------------------------------------------------------------------- C: inside each class
DISPLAY = {"SLC": lambda s: s.replace("lift units ", "", 1),
           "CVT": lambda s: s.replace("rotors", "propulsors").replace("fixed units ", "fixed "),
           "TR": lambda s: s.replace("two or more tilting sets", "2+ tilting sets").replace("on two or more stations", "in 2+ places").replace("on one station", "in one place")}
TITLE13 = {"SLC": "Lift + Cruise: where the\nlift units sit", "TR": "Tilt Propulsor: how the\ntilting thrust is split",
           "CVT": "CVT: what tilts · where\nthe fixed units sit"}


def fig_leading_layout_by_class(ctx):
    d = _data(ctx)
    pmix = d["pmix"]
    fig, axs = plt.subplots(1, 3, figsize=(ctx.W, 3.6), constrained_layout=True, sharey=True)
    for ax, c in zip(axs, ["SLC", "TR", "CVT"]):
        m = pmix[pmix["code"] == c]
        lastw = m[m["window"] == "2020-23"].sort_values("aircraft", ascending=False)
        ordc = [k for k in lastw["configuration"] if not frames.cfg_outside(k)]
        keep = ordc[:3] if len(ordc) > 4 else ordc[:4]
        frac = lambda k: (m[m["configuration"].isin(k)].groupby("window")["aircraft"].sum().reindex(ctx.COMPLETE).fillna(0)
                          / m.groupby("window")["class aircraft"].first().reindex(ctx.COMPLETE))
        comp = pd.DataFrame({DISPLAY[c](k): frac([k]) for k in keep})
        rest = frac([k for k in m["configuration"].unique() if k not in keep])
        if rest.sum() > 0:
            comp["other configurations"] = rest
        plots.config_stack(ax, comp, style.cls(c).color, n_few=2, min_label=MIN_LABEL13)
        nwin = m.groupby("window")["aircraft"].sum().reindex(ctx.COMPLETE)
        ax.set_xticks(range(len(ctx.COMPLETE)), [f"{ctx.WSHORT[w]}\nn {int(n)}" for w, n in zip(ctx.COMPLETE, nwin)])
        ax.set_title(TITLE13[c], fontsize=7.5, loc="left")
        ax.legend(loc="upper left", bbox_to_anchor=(-0.04, -0.17), fontsize=7, handlelength=1.1, labelspacing=0.3, frameon=False)
        if c != "SLC":
            ax.tick_params(labelleft=False)
    axs[0].set_ylabel("share of the class's aircraft")
    return fig, pmix.reset_index(drop=True)


def fig_leading_configuration_share(ctx):
    d = _data(ctx)
    prop, poss = d["prop"], d["poss"]
    share_cfg = prop.pivot(index="window", columns="code", values="share in it").reindex(ctx.COMPLETE)
    fig, ax = plt.subplots(figsize=(ctx.W, 2.9), constrained_layout=True)
    plots.few_band(ax, 2)
    plots.window_lines(ax, share_cfg[CLASSES5], n_few=2, ticks=[ctx.WSHORT[w] for w in ctx.COMPLETE])
    ends = []
    for c in CLASSES5:
        r = poss.loc[(c, "2020-23")]
        K = r["possible configurations"]
        ends.append((float(r["share in it"]), f"{style.cls(c).short} {100 * r['share in it']:.0f} % · {int(r['distinct configurations'])} of {int(K) if np.isfinite(K) else '–'}",
                     style.cls(c).color))
    order = sorted(range(len(ends)), key=lambda i: ends[i][0])
    plots.end_labels(ax, len(ctx.COMPLETE) - 1, [ends[i][0] for i in order], [ends[i][1] for i in order], [ends[i][2] for i in order], gap=0.075)
    ax.set_xlim(-0.5, len(ctx.COMPLETE) - 1 + 1.75)
    ax.set_ylim(0, 0.92)
    _pc(ax)
    _ygrid(ax)
    ax.set_ylabel("share of the class in its\nmost common configuration")
    ax.set_xlabel("priority window; at the line ends: the 2020-23 share and the configurations in use of those the rule allows", fontsize=7)
    return fig, prop[["code", "window", "aircraft", "possible configurations", "distinct configurations", "most common configuration", "share in it"]].reset_index(drop=True)


# ------------------------------------------------------------------------------------------------- D: across classes
def _tw(d, c):
    return d["dw"][d["dw"]["code"] == c].set_index("window")


def fig_class_centres_tilting_units(ctx):
    d = _data(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W * 0.62, 3.5), constrained_layout=True)
    cent = {c: pd.DataFrame({"x": _tw(d, c).reindex(ctx.COMPLETE)["tilting sets (mean)"],
                             "y": _tw(d, c).reindex(ctx.COMPLETE)["propulsive units (median)"]}) for c in ("SLC", "TR", "CVT")}
    pts = plots.centre_trajectory(ax, cent, n_few=2)
    ax.set_xlim(-0.15, 2.15)
    ax.set_ylim(0, 10.6)
    ax.set_xlabel("tilting sets per aircraft (mean)")
    ax.set_ylabel("propulsor units per aircraft (median)")
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    leg = ax.legend(handles=[Line2D([], [], color=style.cls(c).color, marker=style.cls(c).marker, markersize=5, linewidth=1.3,
                                    label=f"{style.cls(c).short} {style.cls(c).name}") for c in ("SLC", "TR", "CVT")],
                    loc="upper right", fontsize=7, frameon=True, framealpha=0.95, edgecolor="none", handlelength=1.6)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    lab = [ctx.WSHORT[ctx.COMPLETE[k]] for _, _, k, _ in pts]
    failed = plots.place_labels(ax, [p[0] for p in pts], [p[1] for p in pts], lab, [3.6] * len(pts),
                                obstacles=[leg.get_window_extent(rend).expanded(1.03, 1.1)], fontsize=7)
    assert not failed, failed
    data = d["dw"][d["dw"]["code"].isin(["SLC", "TR", "CVT"])][["class", "window", "aircraft", "tilting sets (mean)", "propulsive units (median)"]]
    return fig, data.reset_index(drop=True)


def fig_tp_units_by_tilting_sets(ctx):
    d = _data(ctx)
    lk = d["links"][d["links"]["link"].str.startswith("Tilt Rotor")]
    s = style.cls("TR")
    fig, ax = plt.subplots(figsize=(ctx.HALF, 2.6), constrained_layout=True)
    ax.bar(range(len(lk)), lk["median"], width=0.6, color=s.color, hatch=s.hatch, edgecolor="white", linewidth=0.6, zorder=3)
    for i, (m, n) in enumerate(zip(lk["median"], lk["aircraft"])):
        ax.text(i, m + 0.2, f"{m:g} units\nn = {int(n)}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(range(len(lk)), list(lk["group"].astype(str)))
    ax.set_ylim(0, float(lk["median"].max()) + 2.6)
    ax.set_xlabel("tilting sets on the aircraft")
    ax.set_ylabel("propulsor units (median)")
    _ygrid(ax)
    return fig, lk[["group", "aircraft", "median"]].reset_index(drop=True)


def fig_cvt_units_on_booms(ctx):
    d = _data(ctx)
    cv = _tw(d, "CVT").reindex(ctx.COMPLETE)
    sc = style.cls("CVT")
    x = np.arange(len(ctx.COMPLETE))
    nb, nn = cv["aircraft, units on booms"].to_numpy(), cv["aircraft, no units on booms"].to_numpy()
    fig, ax = plt.subplots(figsize=(ctx.HALF, 2.6), constrained_layout=True)
    plots.few_band(ax, 2)
    y3 = cv["share with units on booms"].to_numpy(dtype=float)
    ax.plot(x, y3, color=sc.color, linestyle=sc.dash, linewidth=1.5, marker=sc.marker, markersize=4.6, zorder=3)
    for xi in x:
        dip = 0 < xi < len(y3) - 1 and y3[xi] <= min(y3[xi - 1], y3[xi + 1])
        ax.annotate(f"{100 * y3[xi]:.0f} %", (xi, y3[xi]), textcoords="offset points", xytext=(0, -7 if dip else 6), ha="center",
                    va="top" if dip else "bottom", fontsize=7.5, color=style.INK)
    ax.set_xticks(x, [f"{ctx.WSHORT[w]}\nn {int(a + b)}" for w, a, b in zip(ctx.COMPLETE, nb, nn)])
    ax.set_ylim(0, 1.05)
    _pc(ax)
    ax.set_xlim(-0.5, len(x) - 0.5)
    _ygrid(ax)
    ax.set_ylabel("share of CVT aircraft with\npropulsor units on booms")
    return fig, cv[["aircraft", "aircraft, units on booms", "share with units on booms"]].reset_index()


def fig_cvt_ducted_by_boom_layout(ctx):
    d = _data(ctx)
    cv = _tw(d, "CVT").reindex(ctx.COMPLETE)
    sc = style.cls("CVT")
    x = np.arange(len(ctx.COMPLETE))
    nb, nn = cv["aircraft, units on booms"].to_numpy(), cv["aircraft, no units on booms"].to_numpy()
    lt = d["links"][d["links"]["link"].str.startswith("CVT")].set_index("group")
    test_txt = lambda r: f"{r['movement']} (ρ {r['rho']:+.2f}, {_ptxt(r['p'])})".replace("-", "−")
    fig, ax = plt.subplots(figsize=(ctx.HALF + 0.4, 2.9), constrained_layout=True)
    plots.few_band(ax, 2)
    for name, col, c, ns, txt in (("units on booms", "ducted share, units on booms", sc.color, nb, "units on booms"),
                                  ("no units on booms", "ducted share, no units on booms", style.MUTED, nn, "no units on booms")):
        y = cv[col].to_numpy(dtype=float)
        ok = np.isfinite(y)
        ax.plot(x[ok], y[ok], color=c, linewidth=1.5, marker="o", markersize=4.4, zorder=3, label=f"{txt}: {test_txt(lt.loc[name])}")
        for xi in x[ok]:
            below = name.startswith("units")
            ax.annotate(f"{int(ns[xi])}/{int(nb[xi] + nn[xi])}", (xi, y[xi]), textcoords="offset points", xytext=(-5, 0) if below else (0, 6),
                        ha="right" if below else "center", va="center" if below else "bottom", fontsize=7, color=style.INK,
                        bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
    ax.set_xticks(x, [ctx.WSHORT[w] for w in ctx.COMPLETE])
    ax.set_ylim(0, 1.05)
    ax.set_xlim(-0.5, len(x) - 0.5)
    _pc(ax)
    _ygrid(ax)
    ax.set_ylabel("share of CVT aircraft with\na ducted propulsor unit")
    fig.legend(loc="outside lower center", ncol=1, fontsize=7, handlelength=2.0)
    return fig, cv[["aircraft, units on booms", "ducted share, units on booms", "aircraft, no units on booms", "ducted share, no units on booms"]].reset_index()


def _trace_lines(ctx, col: str, ylabel: str):
    d = _data(ctx)
    dw = d["dw"]
    fig, ax = plt.subplots(figsize=(ctx.W * 0.7, 2.9), constrained_layout=True)
    plots.few_band(ax, 2)
    fr = dw.pivot(index="window", columns="code", values=col).reindex(ctx.COMPLETE)[CLASSES5]
    plots.window_lines(ax, fr, n_few=2, ticks=[ctx.WSHORT[w] for w in ctx.COMPLETE])
    ax.set_xlim(-0.5, len(ctx.COMPLETE) - 0.5)
    ax.set_ylim(-0.04, 1.05)                                  # a share of 0 keeps its whole marker
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    _pc(ax)
    _ygrid(ax)
    ax.set_ylabel(ylabel)
    fig.legend(handles=_class_handles(CLASSES5, "line"), loc="outside lower center", ncol=3, fontsize=7, handlelength=2.0, columnspacing=1.0)
    return fig, dw[["class", "code", "window", "aircraft", col]].reset_index(drop=True)


def fig_boom_share_by_class(ctx):
    return _trace_lines(ctx, "share with units on booms", "share of the class with\npropulsor units on booms")


def fig_ducted_share_by_class(ctx):
    return _trace_lines(ctx, "share with a ducted unit", "share of the class with\na ducted propulsor unit")


CLASS_WORD = {"SLC": "Lift + Cruise", "TR": "Tilt Propulsor", "CVT": "CVT", "TW": "Tilt Wing", "MR": "Multirotor"}
TRACE_WORD = {"joints": "tilting sets per aircraft", "fus_moves": "a body that tilts or rotates", "units": "propulsor units per aircraft",
              "on_booms": "propulsor units carried on booms", "stations": "places carrying propulsor units per aircraft", "booms": "booms present",
              "pusher": "a pusher unit", "two_wings": "two or more wing panels", "tailless": "no tail surface", "gear_drawn": "landing gear drawn",
              "n_types": "propulsor types per aircraft"}
READ_HERE = {"joints", "units", "on_booms", "ducted", "n_types"}
READING = {"opposed": "drivers disagree; it moved with those under 'goes with'", "overdetermined": "{n} drivers predict it; the labelled dataset cannot say which acts",
           "single": "one driver predicts it, and it moved that way", "against_all": "moved against the only direction any driver predicts",
           "fixed_only": "no driver predicts a direction; only physical limits bear on it", "mixed_by_class": "classes move in opposite directions; no driver reading"}
READING_EXTRA = {"joints": "; per propulsor unit it falls", "ducted": "; in CVT it follows the boom layout",
                 "n_types": "; in Tilt Propulsor the added type is a second tilting set"}


def tab_driver_verdicts(ctx):
    d = _data(ctx)
    trends, classes = d["trends"], d["classes"]
    verd = drivers.driver_verdicts(trends)
    dname = lambda c: drivers.DRIVERS[c][1].replace("rotor control", "propulsor control")
    rows = []
    for tr, vr in zip(drivers.TRACES, verd.iloc[:len(drivers.TRACES)].itertuples()):
        t = trends[trends["trace"] == tr["label"]].set_index("code")
        moved = [c for c in classes if t.loc[c, "movement"] in ("rises", "falls")]
        if not moved and t.loc["ALL5", "movement"] not in ("rises", "falls"):
            continue
        parts = [f"{t.loc[c, 'movement']} in {CLASS_WORD[c]} (ρ {t.loc[c, 'rho']:+.2f}, {_ptxt(t.loc[c, 'p'])})" for c in moved]
        where = ("; ".join(parts) if parts else "no trend detected in any class") + f"; pooled: {t.loc['ALL5', 'movement']}"
        inside = {t.loc[c, "movement"] for c in moved} or {t.loc["ALL5", "movement"]}   # only pooled moved: its direction
        dd = "+" if inside == {"rises"} else "-" if inside == {"falls"} else "mixed"
        with_, against = [], []
        for code_, sign in tr["drivers"].items():
            if sign in "+-" and dd != "mixed":
                (with_ if sign == dd else against).append(f"{dname(code_)} ({'more' if sign == '+' else 'fewer'})")
            elif sign == "±" and dd != "mixed" and drivers.DRIVERS[code_][0] != "A2":     # predicts a move either way: counted as 'with' by the rule
                with_.append(f"{dname(code_)} (either way)")
        meaning = READING[vr.verdict].format(n=len(tr["drivers"])) + READING_EXTRA.get(tr["key"], "")
        if vr.verdict == "fixed_only":
            meaning += " (" + ", ".join(dname(c) for c in tr["drivers"]) + ")"
        rows.append({"trace": ("● " if tr["key"] in READ_HERE else "") + TRACE_WORD.get(tr["key"], tr["label"]),
                     "where it moved (every year to 2023)": where, "goes with (driver: what it predicts)": "; ".join(with_) or "—",
                     "goes against (driver: what it predicts)": "; ".join(against) or "—", "what it means": meaning})
    return pd.DataFrame(rows), None


# ------------------------------------------------------------------------------------------------- the numbers
def numbers(ctx) -> dict:
    d = _data(ctx)
    cfg, v, pct, thin = ctx.cfg, ctx.v, ctx.pct, ctx.thin
    t6i = d["t6"].set_index("name")
    dci = d["dcount"].set_index("propulsive units")
    dcd = d["dcond"].set_index("propulsive units")
    L, est, hit, a0 = d["brief"], d["est"], d["hit"], d["a0"]
    zones, zz, core, rim, half, split = d["zones"], d["zz"], d["core"], d["rim"], d["half"], d["split"]
    share, n_win = d["share"], d["n_win"]
    poss, pmix, cur = d["poss"], d["pmix"], d["cur"]
    dwi = d["dw"].set_index(["code", "window"])
    links, spu = d["links"], d["spu"]
    fs = split.set_index("archetype").loc[FOCUS]
    _, top_share = frames.top_archetype_share(v, "A0c", "2020-23", ctx.ds)
    MIX = lambda code, w, key: float(pmix[(pmix["code"] == code) & (pmix["window"] == w) & (pmix["configuration"] == key)]["share"].sum())
    RB, RE = "rotors tilt · fixed units on booms", "rotors tilt · fixed units elsewhere"
    ONE, TWO_ST = "one tilting set", "two or more tilting sets, on two or more stations"
    lk = links[links["link"].str.startswith("Tilt Rotor")]
    lt = links[links["link"].str.startswith("CVT")].set_index("group")
    sp = spu.set_index(["code", "measure"])
    sp_unit = lambda c, w: float(sp.loc[(c, "tilting sets per propulsive unit"), ctx.WSHORT[w]])
    tr = lambda trace, code: _trend(d, trace, code)
    moving_inside = sum(1 for t in drivers.TRACES if any(tr(t["label"], c)["movement"] in ("rises", "falls") for c in d["classes"]))
    fw = lambda r: f"{r:.1f}"
    g = lambda r: f"{r:g}"
    n = {
        # common
        "n_aircraft": thin(len(v)), "last_year": str(cfg.analysis["last_complete_year"]), "partial_start": str(cfg.analysis["partial_window_start"]),
        "trend_min": str(cfg.analysis["trend_min_n"]), "alpha": f"{cfg.analysis['alpha']:g}", "rarefy_n": str(cfg.analysis["rarefy_n"]),
        "w1": "up to 2011", "w2": "2012-15", "w3": "2016-19", "w4": "2020-23", "span_recent": "2016-23",
        "w1_n": str(int(n_win["<= 2011"])), "w2_n": str(int(n_win["2012-15"])), "w3_n": str(int(n_win["2016-19"])), "w4_n": str(int(n_win["2020-23"])),
        # A: fields (Table 6) and propulsion (Figure 6)
        "field_cut": pct(d["cut"]), "fields_kept": str(int((d["t6"]["top_share"] < d["cut"]).sum())),
        "fields_dropped": ", ".join(d["t6"].loc[d["t6"]["top_share"] >= d["cut"], "name"]),
        "tail_top": pct(t6i.loc["tail type", "top_share"]), "units_top": pct(t6i.loc[frames.D3_UNITS_ROW, "top_share"]),
        "fus_top": pct(t6i.loc["fuselage motion hover to cruise", "top_share"]), "wings_top": pct(t6i.loc[frames.D3_FIELD_NAMES["wCount"], "top_share"]),
        "places_top": pct(t6i.loc[frames.D3_PLACES_ROW, "top_share"]), "gear_top": pct(t6i.loc["landing-gear type", "top_share"]),
        "units_n": str(len(d["unit"])), "units_median": g(d["unit"].median()),
        "slc_more8": pct(d["feat"].loc["more than 8 propulsors", "SLC"]), "mr_more8": pct(d["feat"].loc["more than 8 propulsors", "MR"]),
        "cvt_both": pct(d["feat"].loc["both fixed and tilting propulsors", "CVT"]), "tr_tilting": pct(d["feat"].loc["at least one tilting propulsor", "TR"]),
        "duct13_share": pct(dci.loc["1-3", "share with any"]), "duct78_share": pct(dci.loc["7-8", "share with any"]), "duct9_share": pct(dci.loc["9+", "share with any"]),
        "duct13_med": f"{dci.loc['1-3', 'median ducted units (ducted aircraft)']:.0f}", "duct9_med": g(dci.loc['9+', 'median ducted units (ducted aircraft)']),
        "duct9_units": pct(dci.loc["9+", "share of units ducted"]), "duct_every": pct(dcd.loc["all bands", "share that duct every unit"]),
        # A: archetype sets (Table 7, context only)
        "c_arch": str(int(L.loc["A0", "archetypes"])), "c_eff": f"{L.loc['A0', 'effective number ¹D']:.1f}",
        "cwt_arch": str(int(L.loc["A1t", "archetypes"])), "cwt_eff": f"{L.loc['A1t', 'effective number ¹D']:.1f}", "cwt_big": str(int(L.loc["A1t", "archetypes of five or more"])),
        "cu_arch": str(int(L.loc["A0c", "archetypes"])), "cu_eff": f"{L.loc['A0c', 'effective number ¹D']:.1f}", "cu_big": str(int(L.loc["A0c", "archetypes of five or more"])),
        "cu_largest_share": pct(L.loc["A0c", "its share"]), "f_share": pct(L.loc["family_b", "its share"]), "lc_share_all": pct(L.loc["A0", "its share"]),
        # A: the core and the rim (Figure 8), the filers (Figure 7)
        "zones_n": str(len(zones)), "zones_min": str(cfg.analysis["zone_min_aircraft"]), "filers_min": str(cfg.analysis["filer_panel_min_aircraft"]),
        "filers_n": str(len(split)), "recent_n": str(int(v["window"].isin(["2016-19", "2020-23"]).sum())),
        "recent_share": pct(v["window"].isin(["2016-19", "2020-23"]).sum() / len(v)),
        "core_n": str(len(core)), "core_share": pct(d["core_share_exact"]), "rim_n": str(len(rim)), "rim_share": pct(rim["share 2016-23"].sum()),
        "half_w3": str(half["2016-19"] + 1), "half_w4": str(half["2020-23"] + 1), "cu_top_w4": pct(top_share),
        "zones_throughout": str(int((zones["zone"] == "persistent").sum())), "zones_new": str(int((zones["zone"] == "new").sum())),
        "zones_fading": str(int((zones["zone"] == "fading").sum())),
        "core_lead_n": str(int(zz.loc[zz["archetype"] == "TR · 1-3", "aircraft"].iloc[0])), "core_lead_filers": str(int(zz.loc[zz["archetype"] == "TR · 1-3", "filers"].iloc[0])),
        "cvt56_n": str(int(fs["aircraft"])), "cvt56_top": str(fs["largest filer"]), "cvt56_top_short": str(fs["largest filer"]).split(" / ")[0],
        "cvt56_top_n": str(int(fs["its aircraft"])), "cvt56_filers": str(int(fs["filers"])), "cvt56_fpa": f"{fs['filers per aircraft']:.2f}",
        "cvt4_fpa": f"{split.set_index('archetype').loc[NEIGH, 'filers per aircraft']:.2f}",
        # A: discovery (Figure 9)
        "disc_tail": str(cfg.analysis["discovery_tail"]), "disc_orders": str(cfg.analysis["discovery_orders"]),
        "disc_after_last_class": str(int(a0["aircraft"].max() - hit["aircraft"])), "class12_at": str(int(hit["aircraft"])), "class12_year": str(int(hit["priority year reached"])),
        "disc_n": str(int(est.loc["A0", "aircraft"])),
        "cu_new": fw(est.loc["A0c", "new in the last 100 aircraft"]), "cu_exp": fw(est.loc["A0c", "new in the last 100, random order"]),
        "cu_unseen": fw(est.loc["A0c", "estimated unseen"]),
        "cwt_new": fw(est.loc["A1t", "new in the last 100 aircraft"]), "cwt_exp": fw(est.loc["A1t", "new in the last 100, random order"]),
        "cwt_seen": str(int(est.loc["A1t", "archetypes observed"])), "cwt_chao": fw(est.loc["A1t", "Chao1"]), "cwt_found": pct(est.loc["A1t", "share of richness found"]),
        # B: class shares (Figure 10)
        "tp_w1": pct(share.loc["<= 2011", "TR"]), "tp_w3": pct(share.loc["2016-19", "TR"]), "tp_w4": pct(share.loc["2020-23", "TR"]),
        "lc_w1": pct(share.loc["<= 2011", "SLC"]), "lc_w3": pct(share.loc["2016-19", "SLC"]), "lc_w4": pct(share.loc["2020-23", "SLC"]),
        "cvt_w4": pct(share.loc["2020-23", "CVT"]), "three_w4": pct(share.loc["2020-23", ["SLC", "TR", "CVT"]].sum()),
        "mr_w1": pct(share.loc["<= 2011", "MR"]), "mr_w4": pct(share.loc["2020-23", "MR"]),
        # C: configurations (Figure 13)
        "cfg_min_cell": str(drivers.MIN_CELL), "cfg_gaps": str(int(d["prop"]["aircraft outside the rule"].sum())),
        "slc_lead_w1": pct(poss.loc[("SLC", "<= 2011"), "share in it"]), "slc_lead_w2": pct(poss.loc[("SLC", "2012-15"), "share in it"]),
        "slc_lead_w3": pct(poss.loc[("SLC", "2016-19"), "share in it"]), "slc_lead_w4": pct(poss.loc[("SLC", "2020-23"), "share in it"]),
        "slc_poss": str(int(poss.loc[("SLC", "2020-23"), "possible configurations"])), "slc_used_w4": str(int(poss.loc[("SLC", "2020-23"), "distinct configurations"])),
        "tr_poss": str(int(poss.loc[("TR", "2020-23"), "possible configurations"])), "cvt_poss": str(int(poss.loc[("CVT", "2020-23"), "possible configurations"])),
        "cvt_re_w1": pct(MIX("CVT", "<= 2011", RE)), "cvt_re_w2": pct(MIX("CVT", "2012-15", RE)), "cvt_re_w3": pct(MIX("CVT", "2016-19", RE)),
        "cvt_rb_w4": pct(MIX("CVT", "2020-23", RB)),
        "tr_one_w1": pct(MIX("TR", "<= 2011", ONE)), "tr_one_w4": pct(MIX("TR", "2020-23", ONE)), "tr_twost_w4": pct(MIX("TR", "2020-23", TWO_ST)),
        "tw_lead_w4": pct(poss.loc[("TW", "2020-23"), "share in it"]), "mr_lead_w4": pct(poss.loc[("MR", "2020-23"), "share in it"]),
        "old_lc_w1": pct(cur[("SLC", "<= 2011")]), "old_lc_w4": pct(cur[("SLC", "2020-23")]), "old_tp_w1": pct(cur[("TR", "<= 2011")]), "old_tp_w4": pct(cur[("TR", "2020-23")]),
        "old_cvt_w1": pct(cur[("CVT", "<= 2011")]), "old_cvt_w4": pct(cur[("CVT", "2020-23")]),
        # D: traces (Figures 14, 15, Table 9)
        "tr_sets_w1": fw(dwi.loc[("TR", "<= 2011"), "tilting sets (mean)"]), "tr_sets_w4": fw(dwi.loc[("TR", "2020-23"), "tilting sets (mean)"]),
        "tr_units_w1": g(dwi.loc[("TR", "<= 2011"), "propulsive units (median)"]), "tr_units_w4": g(dwi.loc[("TR", "2020-23"), "propulsive units (median)"]),
        "cvt_sets_w1": fw(dwi.loc[("CVT", "<= 2011"), "tilting sets (mean)"]), "cvt_sets_w4": fw(dwi.loc[("CVT", "2020-23"), "tilting sets (mean)"]),
        "cvt_units_w1": g(dwi.loc[("CVT", "<= 2011"), "propulsive units (median)"]), "cvt_units_w4": g(dwi.loc[("CVT", "2020-23"), "propulsive units (median)"]),
        "tr_units_rho": f"{tr('propulsive units', 'TR')['rho']:+.2f}", "tr_units_p": _pt(tr("propulsive units", "TR")["p"]),
        "cvt_units_rho": f"{tr('propulsive units', 'CVT')['rho']:+.2f}", "cvt_units_p": _pt(tr("propulsive units", "CVT")["p"]),
        "tr_sets_rho": f"{tr('tilting joint groups', 'TR')['rho']:+.2f}", "tr_sets_p": _pt(tr("tilting joint groups", "TR")["p"]),
        "cvt_sets_rho": f"{tr('tilting joint groups', 'CVT')['rho']:+.2f}", "cvt_sets_p": _pt(tr("tilting joint groups", "CVT")["p"]),
        "pooled_sets_w1": fw(tr("tilting joint groups", "ALL5")["first mean"]), "pooled_sets_w4": fw(tr("tilting joint groups", "ALL5")["2020-23 mean"]),
        "pooled_sets_p": _pt(tr("tilting joint groups", "ALL5")["p"]),
        "tr_med_one": g(lk["median"].iloc[0]), "tr_med_two": g(lk["median"].iloc[1]), "tr_med_three": g(lk["median"].iloc[2]),
        "tr_twoplus_w4": pct(dwi.loc[("TR", "2020-23"), "share with two or more tilting sets"]), "tr_fixed_w4": pct(dwi.loc[("TR", "2020-23"), "share with a fixed unit"]),
        "cvt_onb_w1": pct(tr("units carried on booms", "CVT")["first value"]), "cvt_onb_w4": pct(tr("units carried on booms", "CVT")["2020-23 value"]),
        "cvt_onb_p": _pt(tr("units carried on booms", "CVT")["p"]), "cvt_onb_w1_n": str(int(dwi.loc[("CVT", "<= 2011"), "aircraft, units on booms"])),
        "cvt_w1_n": str(int(dwi.loc[("CVT", "<= 2011"), "aircraft"])), "cvt_onb_w4_n": str(int(dwi.loc[("CVT", "2020-23"), "aircraft, units on booms"])),
        "cvt_w4_n": str(int(dwi.loc[("CVT", "2020-23"), "aircraft"])),
        "slc_onb_w4": pct(tr("units carried on booms", "SLC")["2020-23 value"]), "slc_onb_p": _pt(tr("units carried on booms", "SLC")["p"]),
        "tw_onb_w4": pct(tr("units carried on booms", "TW")["2020-23 value"]), "tw_onb_p": _pt(tr("units carried on booms", "TW")["p"]),
        "mr_onb_w1": pct(tr("units carried on booms", "MR")["first value"]), "mr_onb_w4": pct(tr("units carried on booms", "MR")["2020-23 value"]),
        "mr_onb_p": _pt(tr("units carried on booms", "MR")["p"]),
        "cvt_duct_w1": pct(tr("a ducted unit", "CVT")["first value"]), "cvt_duct_w4": pct(tr("a ducted unit", "CVT")["2020-23 value"]),
        "cvt_duct_rho": f"{tr('a ducted unit', 'CVT')['rho']:+.2f}", "cvt_duct_p": _pt(tr("a ducted unit", "CVT")["p"]),
        "slc_duct_w4": pct(tr("a ducted unit", "SLC")["2020-23 value"]),
        "cvt_duct_booms_w3": pct(dwi.loc[("CVT", "2016-19"), "ducted share, units on booms"]), "cvt_duct_booms_w4": f"{100 * dwi.loc[('CVT', '2020-23'), 'ducted share, units on booms']:.1f} %",
        "cvt_duct_booms_rho": f"{lt.loc['units on booms', 'rho']:+.2f}", "cvt_duct_booms_p": _pt(lt.loc["units on booms", "p"]),
        "cvt_duct_nob_w3": pct(dwi.loc[("CVT", "2016-19"), "ducted share, no units on booms"]), "cvt_duct_nob_w4": pct(dwi.loc[("CVT", "2020-23"), "ducted share, no units on booms"]),
        "spu_w1": f"{sp_unit('TR', '<= 2011'):.2f}", "spu_w4": f"{sp_unit('TR', '2020-23'):.2f}",
        "spu_rho": f"{sp.loc[('TR', 'tilting sets per propulsive unit'), 'rho']:+.2f}", "spu_p": _pt(sp.loc[("TR", "tilting sets per propulsive unit"), "p"]),
        "spu_cvt_p": _pt(sp.loc[("CVT", "tilting sets per propulsive unit"), "p"]),
        "traces_moving": str(moving_inside),
    }
    return {k: str(val).replace("-", "−") if k.endswith(("_rho",)) else str(val) for k, val in n.items()}


# ------------------------------------------------------------------------------------------------- the method flowchart
def fig_method_flow(ctx):
    nodes = [
        dict(id="data", kind="data",   col=0, text="Unique aircraft\nlabel fields"),
        dict(id="arch", kind="step",   col=1, text="Archetypes\nC · C·W·T · C·U"),
        dict(id="conf", kind="step",   col=1, text="Class configurations\nper window"),
        dict(id="test", kind="test",   col=2, text="Discovery curve\nSpearman ρ on year"),
        dict(id="figA", kind="figure", col=3, text="Crowded core ·\nDiscovery curve"),
        dict(id="figB", kind="figure", col=3, text="Class shares ·\nLayouts inside classes"),
        dict(id="ans",  kind="answer", col=4, text="Answer\nwhere, how moved"),
    ]
    edges = [("data", "arch"), ("data", "conf"), ("arch", "test"), ("conf", "test"),
             ("test", "figA"), ("test", "figB"), ("figA", "ans"), ("figB", "ans")]
    return flow.chart(ctx.cfg, nodes, edges), None


# ------------------------------------------------------------------------------------------------- the items
_DECIDE_T6 = "Table 6 and Figure 6 (i) say the same thing from two sides; the author decides which of the two stays in the main text"
_SRC_LAB = "human labelling (627 unique aircraft)"

ITEMS = [
    dict(name="q6_method_flow", slot="method", kind="figure", sub="", title="How Q6 is answered",
         caption="How Q6 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source="method flowchart", unit="", read=""),
    # A — the design space
    dict(name="q6_selected_fields", slot="results", kind="table", sub="A", title="Label fields that tell designs apart",
         caption=f"The label fields whose most common answer holds under {100 * _AN['field_drop_top_share']:.0f} % of the aircraft: aircraft answering, different answers, top share and the most common answers.",
         source_item="Table 6", flag="decide", flag_note=_DECIDE_T6, builder=tab_selected_fields,
         source="human labelling (the codebook fields; the two derived propulsion rows read the aircraft with a propulsion record)",
         unit="unique aircraft", read="a low top share means the field tells many designs apart"),
    dict(name="q6_propulsor_units_per_class", slot="appendix", kind="figure", sub="A", title="Propulsor units per class",
         caption="Propulsor units of every aircraft of each class: one dot per aircraft, the bar over the middle half, the ring at the median.",
         source_item="Figure 6 (i)", flag="decide",
         flag_note=_DECIDE_T6 + "; the contract lists it beside Table 6 in the results, the limit of three result graphs per sub-question put it in the appendix",
         builder=fig_propulsor_units_per_class, source="human labelling (the propulsion record of each place)",
         unit="unique aircraft with a propulsion record", read="dots are jittered sideways; units above 30 are drawn at 30; the median is not pulled by the few aircraft with very many units"),
    dict(name="q6_archetype_core", slot="results", kind="figure", sub="A", title="Crowded core and empty rim",
         caption="C·U archetypes of five aircraft or more by their share of the 2016–23 aircraft and their distinct filers per aircraft; solid ring the crowded core, dashed the empty rim.",
         source_item="Figure 8 (i)", flag=None, flag_note="", builder=fig_archetype_core,
         source="human labelling (class, propulsor units) · PatSeer (applicant, priority date)",
         unit="C·U archetypes with five or more unique aircraft and at least one in 2016-23",
         read="right: a large share of the recent aircraft; up: many different filers per aircraft; bubble area: aircraft; triangle up: first seen 2016 or later"),
    dict(name="q6_archetype_windows", slot="results", kind="figure", sub="A", title="Aircraft per archetype and window",
         caption="Unique aircraft of each C·U archetype per priority window, largest archetype first; the orange bar marks the column by which half the window's aircraft are reached.",
         source_item="Figure 8 (ii)", flag=None, flag_note="", builder=fig_archetype_windows,
         source="human labelling (class, propulsor units) · PatSeer (priority date)",
         unit="unique aircraft per C·U archetype of five or more, per priority window; 2024-26 is partial",
         read="a cell is shaded by the archetype's own busiest window; the arrow joins the half-marks of 2016-19 and 2020-23"),
    dict(name="q6_discovery_curve", slot="results", kind="figure", sub="A", title="Is the design space still opening",
         caption="Distinct archetypes seen as the aircraft accumulate in priority order, at C, C·U and C·W·T, against the same aircraft in random order.",
         source_item="Figure 9", flag=None, flag_note="", builder=fig_discovery_curve,
         source="human labelling (class, wings, tilt, propulsor units) · PatSeer (priority date)",
         unit="unique aircraft with a priority year up to 2023",
         read="a curve still climbing at the right edge means the space is still opening; the box prints the new archetypes of the last 100 aircraft against chance"),
    dict(name="q6_arrangement_by_class", slot="appendix", kind="figure", sub="A", title="Arrangement features per class",
         caption="Share of each class's aircraft with each arrangement feature; under the class its aircraft (read/total where a propulsion record is missing).",
         source_item="Figure 6 (ii)", flag=None, flag_note="", builder=fig_arrangement_by_class,
         source="human labelling (tilt and duct per propulsor type)", unit="unique aircraft of the class where the feature can be read",
         read="a hatched cell is a class with no propulsor card in the codebook"),
    dict(name="q6_ducting_by_units", slot="appendix", kind="figure", sub="A", title="Ducting per propulsor-unit band",
         caption="Share of each band's aircraft with a ducted propulsor, split by how much of the aircraft is ducted; the diamond is the share of the band's propulsor units in a duct.",
         source_item="Figure 6 (iii)", flag=None, flag_note="", builder=fig_ducting_by_units,
         source="human labelling (propulsor units and duct per propulsor type)", unit="unique aircraft with a unit count above zero",
         read="the white figure in the dark block is the share of the ducting aircraft that duct every propulsor"),
    dict(name="q6_archetype_filers", slot="appendix", kind="figure", sub="A", title="Filers per aircraft per archetype",
         caption=f"Distinct filers per aircraft for the C·U archetypes with {_AN['filer_panel_min_aircraft']} aircraft or more; CVT with 5-6 propulsor units is outlined, CVT with 4 beside it.",
         source_item="Figure 7", flag="drop", flag_note="redundant with Figure 8 (i), whose vertical axis is the same ratio and whose callout names the one archetype that leans on one firm",
         builder=fig_archetype_filers, source="human labelling (class, propulsor units) · PatSeer (applicant, read as filer)",
         unit=f"C·U archetypes with {_AN['filer_panel_min_aircraft']} or more unique aircraft", read="1.00 means every aircraft has a different filer; a low value is one firm's line of variants"),
    # B — between classes
    dict(name="q6_class_shares_by_window", slot="results", kind="figure", sub="B", title="Class share per priority window",
         caption="Share of each architecture class in the unique aircraft of each priority window; the last window is still filling.",
         source_item="Figure 10 (i)", flag=None, flag_note="", builder=fig_class_shares_by_window,
         source="human labelling (class) · PatSeer (priority date)", unit="unique aircraft per four-year priority window",
         read="each bar is one window at 100 %; a segment of 5 % or more prints its share; the number under the window is its aircraft"),
    dict(name="q6_largest_classes_over_time", slot="results", kind="figure", sub="B", title="Five largest classes over time",
         caption="The five largest classes' share of the window's unique aircraft, one line each; the last window is still filling.",
         source_item="Figure 10 (ii)", flag=None, flag_note="", builder=fig_largest_classes_over_time,
         source="human labelling (class) · PatSeer (priority date)", unit="unique aircraft per four-year priority window",
         read="shares are read, never counts, because a share can fall while the count grows; the earliest window rests on few aircraft"),
    # C — inside each class
    dict(name="q6_leading_layout_by_class", slot="results", kind="figure", sub="C", title="Layouts inside the three largest classes",
         caption="Composition of Lift + Cruise, Tilt Propulsor and CVT over their own configurations per window, the configuration that leads in 2020-23 at the bottom.",
         source_item="Figure 13 (ii)", flag=None, flag_note="", builder=fig_leading_layout_by_class,
         source="human labelling (class; wing, boom and propulsor cards)",
         unit="unique aircraft of the class per complete priority window; the two early windows (faded) hold few aircraft",
         read=f"each block is one configuration's share of the class; blocks of {100 * MIN_LABEL13:.0f} % or more print their share; configurations beyond the largest are pooled in grey; the rules were chosen after the shares under earlier rules had been seen"),
    dict(name="q6_leading_configuration_share", slot="appendix", kind="figure", sub="C", title="Share in the leading configuration",
         caption="Share of each class in its most common configuration per complete window; at the right end the 2020–23 share and the configurations in use of those the rule allows.",
         source_item="Figure 13 (i)", flag=None, flag_note="", builder=fig_leading_configuration_share,
         source="human labelling (class; wing, boom and propulsor cards)",
         unit="unique aircraft of the class per complete priority window; a window under 5 aircraft of the class is not drawn",
         read="a level is not compared between classes, because a rule with fewer possible configurations gives a larger leading share by construction"),
    # D — across classes
    dict(name="q6_class_centres_tilting_units", slot="appendix", kind="figure", sub="D", title="Class centres in tilting sets and units",
         caption="Each class's centre per window, mean tilting sets against median propulsor units, joined by arrows in time order.",
         source_item="Figure 14 (i)", flag=None, flag_note="", builder=fig_class_centres_tilting_units,
         source="human labelling (class; wing, boom and propulsor cards)", unit="unique aircraft of the class in the window (5 or more), complete priority years",
         read="right means more tilting sets per aircraft, up more propulsor units; hollow and faint: windows with few aircraft"),
    dict(name="q6_tp_units_by_tilting_sets", slot="appendix", kind="figure", sub="D", title="Tilt Propulsor units by tilting sets",
         caption="Median propulsor units of the Tilt Propulsor aircraft with one, two, and three or more tilting sets, all years.",
         source_item="Figure 14 (ii)", flag=None, flag_note="", builder=fig_tp_units_by_tilting_sets,
         source="human labelling (propulsor cards)", unit="Tilt Propulsor aircraft with a unit count, all years", read="above each bar its aircraft"),
    dict(name="q6_cvt_units_on_booms", slot="appendix", kind="figure", sub="D", title="CVT aircraft with units on booms",
         caption="Share of CVT aircraft that carry propulsor units on booms per complete window.",
         source_item="Figure 14 (iii)", flag=None, flag_note="", builder=fig_cvt_units_on_booms,
         source="human labelling (boom and propulsor cards)", unit="CVT aircraft per complete priority window", read="under each window the CVT aircraft there"),
    dict(name="q6_cvt_ducted_by_boom_layout", slot="appendix", kind="figure", sub="D", title="CVT ducting inside each boom layout",
         caption="Share of CVT aircraft with a ducted propulsor unit, one line for the aircraft with propulsor units on booms and one for those without, each with its trend test.",
         source_item="Figure 14 (iv)", flag=None, flag_note="", builder=fig_cvt_ducted_by_boom_layout,
         source="human labelling (boom and propulsor cards) · Spearman against the priority year, every year to 2023",
         unit="CVT aircraft per complete priority window; a share is drawn when the layout holds 5 aircraft or more",
         read="a point is labelled with the layout's aircraft over all CVT of the window"),
    dict(name="q6_boom_share_by_class", slot="appendix", kind="figure", sub="D", title="Propulsor units on booms per class",
         caption="Share of each class's aircraft that carry propulsor units on booms per complete window.",
         source_item="Figure 15 (i)", flag=None, flag_note="", builder=fig_boom_share_by_class,
         source="human labelling (class; propulsor cards: the places carrying propulsor units)",
         unit="unique aircraft of the class in the window (5 or more)", read="hollow markers and the grey band: windows with few aircraft"),
    dict(name="q6_ducted_share_by_class", slot="appendix", kind="figure", sub="D", title="Ducted propulsor unit per class",
         caption="Share of each class's aircraft with at least one ducted propulsor unit per complete window.",
         source_item="Figure 15 (ii)", flag=None, flag_note="", builder=fig_ducted_share_by_class,
         source="human labelling (class; propulsor cards: the ducted flag)",
         unit="unique aircraft of the class in the window (5 or more)", read="hollow markers and the grey band: windows with few aircraft"),
    dict(name="q6_driver_verdicts", slot="appendix", kind="table", sub="D", title="Traces that move and their drivers",
         caption="The traces that move inside at least one class or in the five classes pooled: where each moved, with ρ and p, and the drivers it goes with and against.",
         source_item="Table 9", flag=None, flag_note="", builder=tab_driver_verdicts,
         source="human labelling (class; wing, boom and propulsor cards) · Spearman against the priority year, every year to 2023",
         unit="unique aircraft of the class with a value and a priority year up to 2023", read="● marks the traces the text reads"),
]
