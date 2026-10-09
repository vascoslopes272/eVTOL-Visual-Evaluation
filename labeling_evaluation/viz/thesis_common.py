"""The numbers the common thesis text quotes (Methodology, statistics table, Limitations, chapter map) and the
chapter-level flowcharts of the Methodology (METHOD_ITEMS, saved by notebook 46 to thesis_figures/common/).

    from viz import thesis, thesis_common
    n = thesis_common.numbers(thesis.context(cfg))     # dict[str, str], every value AS PRINTED
    for it in thesis_common.METHOD_ITEMS:              # common_chapter_flow, common_data_flow
        thesis_common.save_common(it, it["builder"](ctx)[0], cfg)

Ported from notebooks/_build/build_40.py section 0.1 ("N0": the Method common to every chapter and the statistics
box) plus the few counts the Limitations quote (public counterparts, TRL, index firms, classes) from the 1.1 / 1.3
number cells of the same notebook. Nothing here is typed: every value is computed from ``ctx`` or read from the
constants of ``lib`` / the yaml. The keys keep the names of build_40 so viz/thesis_q*.py can reuse them.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pandas as pd

from lib import diversity, dominant_design, drivers, growth, intervals
from viz import flow, frames, thesis


def _trend(trends: pd.DataFrame, trace: str, code: str) -> pd.Series:
    return trends[(trends["trace"] == trace) & (trends["code"] == code)].iloc[0]


def publication_lag(ctx) -> pd.DataFrame:
    """Median and 90th-percentile publication lag of the three regions (years), as build_40 §0.1 reads it."""
    return frames.publication_lag(ctx.ds, by="region").set_index("region").loc[frames.REGIONS]


def worked_examples(ctx) -> dict:
    """The two worked examples of the statistics box: propulsor units of TR / MR, tilting sets of CVT (lib.drivers)."""
    tf = frames.trace_frame(ctx.ds, ctx.v)
    classes = drivers.class_selection(ctx.v)
    drift = drivers.trace_drift(tf, classes)
    trends = drivers.trace_trends(tf, drift, classes)
    return {"tr": _trend(trends, "propulsive units", "TR"), "mr": _trend(trends, "propulsive units", "MR"),
            "cvt": _trend(trends, "tilting joint groups", "CVT")}


def public_agreement(ctx) -> tuple:
    """(agree, n, '0.83–0.94'): drawing label against the public aircraft, Wilson interval with N = len(v) (build_40 Table 2)."""
    pub = frames.public_arch_frame(ctx.ds)
    k, n = int(pub["match"].astype(str).isin(["yes", "taxonomy"]).sum()), len(pub)
    lo, hi = intervals.wilson_fpc_interval(k, n, len(ctx.v))
    return k, n, f"{lo:.2f}–{hi:.2f}"


def linked_subset_failures(ctx) -> tuple:
    """(attributes the public-page subset differs on, attributes tested): frames.representativeness on the linked aircraft."""
    linked = frames.linked_aircraft_ids(ctx.v, ctx.cfg)
    rep = frames.representativeness(ctx.v.copy(), ctx.v["aircraft_id"].isin(linked), "linked", ctx.WIN_NAMES)
    tested = rep[rep["test"].ne("")]
    return int(tested["verdict"].eq("does NOT match the rest").sum()), int(len(tested))


def _join(items: list) -> str:
    """'a, b, c and d' from the config's own window names, so the prose never types them."""
    return ", ".join(items[:-1]) + " and " + items[-1] if len(items) > 1 else "".join(items)


def numbers(ctx) -> dict:
    """Every number the common text quotes, as printed ('1 639', '53 %', '0.031', '< 0.001')."""
    ds, v, cfg, thin, pct, pval = ctx.ds, ctx.v, ctx.cfg, ctx.thin, ctx.pct, ctx.pval
    lag = publication_lag(ctx)
    vis = frames.visible_at_snapshot(ds, v, 2023)
    ex = worked_examples(ctx)
    tr, mr, cvt = ex["tr"], ex["mr"], ex["cvt"]
    complete = v[~v["window"].str.contains("partial")]
    partial_start = int(cfg.analysis["partial_window_start"])

    # ---- the Method common to every chapter (build_40 §0.1, N0)
    n = {
        "acquired_s": thin(ds.counts["patents_acquired"]), "representative_s": thin(ds.counts["patents_approved"]),
        "observations_s": thin(ds.counts["approved_variants"]), "unique_s": thin(len(v)),
        "snapshot": frames.snapshot_date(ds), "partial_start": str(partial_start), "last_complete": str(partial_start - 1),
        "lag_median_lo": str(int(lag["median lag"].min())), "lag_median_hi": str(int(lag["median lag"].max())),
        "lag_p90": str(int(lag["90th percentile"].max())),
        "sm_vis2023_lo": pct(vis.min()), "sm_vis2023_hi": pct(vis.max()),
        "sm_perm_n": str(cfg.analysis["rarefy_n"]), "sm_perm_seed": str(ctx.SEED),
        "sm_perms": str(inspect.signature(dominant_design.balance_band).parameters["perms"].default),
        "sm_cohesion_perms": str(inspect.signature(dominant_design.cohesion_band).parameters["perms"].default),
        "sm_obs_draws": str(inspect.signature(dominant_design.balance_band).parameters["obs_draws"].default),
        "sm_win_min_n": str(int(complete["window"].value_counts().min())),
        "sm_win_n": str(len(ctx.COMPLETE)),
        "sm_windows": _join([w.replace("<= ", "≤ ") for w in ctx.COMPLETE]),
        "sm_t_units_tr_first": f"{tr['first value']:.1f}", "sm_t_units_tr_last": f"{tr['2020-23 value']:.1f}",
        "sm_t_units_tr_p": pval(tr["p"]),
        "sm_t_units_mr_first": f"{mr['first value']:.1f}", "sm_t_units_mr_last": f"{mr['2020-23 value']:.1f}",
        "sm_t_units_mr_n": str(int(mr["aircraft"])), "sm_t_units_mr_p": pval(mr["p"]),
        "sm_t_units_mr_p100": str(round(mr["p"] * 100)),
        "sm_t_joints_cvt_first": f"{cvt['first mean']:.1f}", "sm_t_joints_cvt_last": f"{cvt['2020-23 mean']:.1f}",
        "sm_t_joints_cvt_med_first": f"{cvt['first value']:.1f}", "sm_t_joints_cvt_med_last": f"{cvt['2020-23 value']:.1f}",
    }

    # ---- the apparatus of the statistics table (constants of lib, never typed in the text)
    n.update({
        "sm_alpha": f"{drivers.TREND_ALPHA:.2f}", "sm_trend_min": str(drivers.TREND_MIN),
        "sm_wilson_z": f"{inspect.signature(intervals.wilson_interval).parameters['z'].default:.2f}",
        "sm_boot_draws": thin(growth.DRAWS), "sm_turn_draws": thin(growth.TURNING_DRAWS),
        "sm_fit_lo": str(growth.FIT_WINDOW[0]), "sm_fit_hi": str(growth.FIT_WINDOW[1]),
        "sm_base_lo": str(growth.BASE_YEARS[0]), "sm_base_hi": str(growth.BASE_YEARS[1]),
        "sm_discovery_tail": str(diversity.TAIL), "sm_discovery_orders": str(diversity.ORDERS),
    })

    # ---- the counts the Limitations quote (build_40 §1.1 and §1.3 number cells)
    k, n_pub, ci = public_agreement(ctx)
    named = v["name_is_real"].fillna(False).astype(bool)
    trl = frames.trl_frame(ds)
    tl = frames.ari_timeline(v, cfg)
    flown = tl[tl["first flight (ARI)"] <= frames.ARI_RELEASE_YEAR]
    fail, tested = linked_subset_failures(ctx)
    n.update({
        "sm_pw_img_pub": str(k), "sm_pw_n": str(n_pub), "sm_pw_ci": ci, "tk_pw_share": pct(k / n_pub),
        "sm_nc_named": str(int(named.sum())), "sm_nc_gen": str(int((~named).sum())),
        "sm_trl_above_n": str(int((trl["trl"] > 2).sum())),
        "tk_ari_firms_n": str(len(tl)), "sm_ff_firms_n": str(len(flown)),
        "sm_class_n": str(int(v["topType"].nunique())), "sm_class5_n": str(int(v["class5"].nunique())),
        "sm_linked_fail_n": str(fail), "sm_rep_attr_n": str(tested),
        "sm_region_n": str(len(frames.REGIONS)),
    })
    bad = {key: val for key, val in n.items() if not isinstance(val, str)}
    assert not bad, f"numbers() must return strings as printed; not strings: {bad}"
    return n


# ------------------------------------------------------------------------------------------ the chapter-level flowcharts
#: short names of the three parts for the boxes of the chapter flowchart, keyed by the part name of thesis.QUESTIONS
PART_SHORT = {
    "eVTOL sector stand-outs":                     "Sector stand-outs\n",
    "Patents against the built and funded sector": "Patents against\nthe sector,",
    "Convergence analysis":                        "Convergence\nanalysis,",
}
assert set(PART_SHORT) == {p for _, _, p, _ in thesis.QUESTIONS}, "PART_SHORT drifted from thesis.QUESTIONS"


def _parts() -> list:
    """[(part name, [qids])] in the order of thesis.QUESTIONS."""
    parts = []
    for qid, _slug, part, _q in thesis.QUESTIONS:
        if not parts or parts[-1][0] != part:
            parts.append((part, []))
        parts[-1][1].append(qid)
    return parts


def _fit_arrows(fig) -> None:
    """Trim every arrow of a flow chart to the edge of the boxes it joins, so the arrowheads are not hidden under a
    wide box (flow.chart shrinks by a fixed 22 pt from the box centre; a box wider than 44 pt swallows the head)."""
    from matplotlib.patches import FancyArrowPatch
    ax = fig.axes[0]
    fig.canvas.draw()
    pt = 72.0 / fig.dpi                                           # pixels → points
    boxes = {}
    for t in ax.texts:
        if t.get_bbox_patch() is None:
            continue
        ext = t.get_bbox_patch().get_window_extent()
        cx, cy = ax.transData.transform(t.get_position())
        boxes[(round(cx), round(cy))] = (ext.width / 2, ext.height / 2)
    for a in ax.patches:
        if not isinstance(a, FancyArrowPatch):
            continue
        (xa, ya), (xb, yb) = a._posA_posB
        pa, pb = ax.transData.transform((xa, ya)), ax.transData.transform((xb, yb))
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        norm = max((dx ** 2 + dy ** 2) ** 0.5, 1e-9)
        ux, uy = abs(dx) / norm, abs(dy) / norm
        for key, attr in ((pa, "shrinkA"), (pb, "shrinkB")):
            hw, hh = boxes.get((round(key[0]), round(key[1])), (22 / pt, 22 / pt))
            reach = min(hw / ux if ux > 1e-9 else float("inf"), hh / uy if uy > 1e-9 else float("inf"))
            setattr(a, attr, reach * pt + 2.0)                    # to the box edge, plus a 2 pt gap


def _parts_boxes() -> list:
    """(box text, [qids]) per part, two lines each, the question range on the second line."""
    out = []
    for part, ids in _parts():
        qs = f"{ids[0]}–{ids[-1]}" if len(ids) > 1 else ids[0]
        first, second = PART_SHORT[part].split("\n")
        out.append((f"{first}\n{second} {qs}", ids))
    return out


def fig_chapter_flow(ctx):
    """Ground files → patents → wizard labels → unique aircraft → the three parts → figures and tables → Answer boxes."""
    ds, thin = ctx.ds, ctx.thin
    nodes = [
        dict(id="files", col=0, kind="data", text="Ground\nfiles"),
        dict(id="patents", col=1, kind="data", text=f"{thin(ds.counts['patents_acquired'])}\npatents"),
        dict(id="labels", col=2, kind="step", text="Wizard labels\n(codebook)"),
        dict(id="aircraft", col=3, kind="data", text=f"{thin(len(ctx.v))} unique\naircraft"),
    ]
    edges = [("files", "patents"), ("patents", "labels"), ("labels", "aircraft")]
    for k, (text, _ids) in enumerate(_parts_boxes()):
        pid = f"part{k}"
        nodes.append(dict(id=pid, col=4, kind="step", text=text))
        edges += [("aircraft", pid), (pid, "figs")]
    nodes += [dict(id="figs", col=5, kind="figure", text="Figures\nand tables"),
              dict(id="answers", col=6, kind="answer", text="Answer box\nper question")]
    edges.append(("figs", "answers"))
    fig = flow.chart(ctx.cfg, nodes, edges, fontsize=float(ctx.cfg.style.get("min_font_pt", 7)))
    _fit_arrows(fig)
    return fig, None


def fig_data_flow(ctx):
    """The ground files → notebook 04 join → aircraft_table.csv → the analysis frame (INPUTS.md)."""
    nodes = [
        dict(id="record", col=0, kind="data", text="Wizard record\n(labels, figures)"),
        dict(id="patseer", col=0, kind="data", text="PatSeer export\n(dates, assignee)"),
        dict(id="identity", col=0, kind="data", text="Identity review\n(name, electric, VTOL)"),
        dict(id="decisions", col=0, kind="data", text="Review decisions\n(duplicates, powertrain)"),
        dict(id="join", col=1, kind="step", text="Notebook 04\njoin"),
        dict(id="table", col=2, kind="data", text="aircraft_table.csv\none row per aircraft"),
        dict(id="frame", col=3, kind="step", text=f"Analysis frame\n{ctx.thin(len(ctx.v))} unique aircraft"),
    ]
    edges = [(a, "join") for a in ("record", "patseer", "identity", "decisions")] + [("join", "table"), ("table", "frame")]
    fig = flow.chart(ctx.cfg, nodes, edges, aspect=0.40)
    _fit_arrows(fig)
    return fig, None


METHOD_ITEMS = [
    dict(name="common_chapter_flow", slot="method", kind="figure", sub="", title="How the chapter is organised",
         caption="From the ground files to the Answer box of each question, through the labelled aircraft and the three parts.",
         source_item="new", flag=None, flag_note="", builder=fig_chapter_flow,
         source="labelled dataset, 627 unique aircraft", unit="unique aircraft", read=""),
    dict(name="common_data_flow", slot="method", kind="figure", sub="", title="How the dataset is built",
         caption="The four ground files notebook 04 joins into aircraft_table.csv, the one table every question reads.",
         source_item="new", flag=None, flag_note="", builder=fig_data_flow,
         source="1639_LABELLED/0_labelling (INPUTS.md)", unit="unique aircraft", read=""),
]


def check_common(item: dict) -> None:
    """thesis.check_item without its question-prefix rule: common items start with 'common_'."""
    missing = [k for k in thesis.ITEM_KEYS if k not in item]
    assert not missing, f"item {item.get('name')} misses {missing}"
    assert item["slot"] in thesis.SLOTS and item["kind"] in thesis.KINDS and item["flag"] in thesis.FLAGS, item["name"]
    assert item["name"].startswith("common_"), item["name"]


def save_common(item: dict, fig, cfg) -> Path:
    """Write one chapter-level figure to <output>/thesis_figures/common/<name>.{pdf,png,json}; json keys as thesis.save_item."""
    check_common(item)
    out = cfg.out("thesis_figures") / "common"
    out.mkdir(parents=True, exist_ok=True)
    name = item["name"]
    meta = {k: item[k] for k in ("name", "slot", "kind", "sub", "title", "caption", "source_item", "flag", "flag_note",
                                 "source", "unit", "read")}
    for ext in cfg.style.get("formats", ["pdf", "png"]):
        fig.savefig(out / f"{name}.{ext}")
    meta.update(width_in=round(fig.get_figwidth(), 3), height_in=round(fig.get_figheight(), 3))
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return out / f"{name}.pdf"
