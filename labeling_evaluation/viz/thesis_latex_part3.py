"""Part III hand-over to the dissertation (notebook 52, last section): the six figures redrawn at their final width in the
text block (16 cm), height at most 55 % of the width, written to LaTeX_v15/Figures/Part_III_dominant_design/<group>/<role>/;
the data behind every figure and table in LaTeX_v15/Data_for_writing/csv/; NUMBERS_III.md; MANIFEST.md (appended).
No number, test or result is recomputed differently: the builders are those of viz/thesis_v2_part3.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from viz import analysis3, figcheck, frames, thesis_q6 as q6, thesis_q7 as q7, thesis_v2_part3 as v3
from viz.thesis_latex_common import MAX_H, TEXT_CM, root, tables_md

#: name -> (final width as a share of the text block, in the dissertation)
FIGS = {"q6_architecture_shares_by_cohort": (1.0, True), "q7_condition2_balance": (1.0, True), "q7_condition3_cohesion": (1.0, True),
        "q7_family_conditions": (1.0, True), "q7_condition1_family": (1.0, False), "q6_largest_architectures_over_time": (1.0, False),
        "q7_iii4_directory_categories": (1.0, False)}
#: the figures drawn under notebooks/thesis_style.py (2026-10-20): built at 6.3 in by their builders, never resized, written with ts.save
RESTYLED = v3.RESTYLED
TABLES = {"q7_verdict_table": True, "q7_verdict_detail": True, "q7_condition3_weights": True, "q7_condition3_family": True, "q6_share_trend_spearman": True, "q7_three_year_check": True,
          "q7_granted_live_condition1": True, "q7_granted_live_condition2": True, "q7_iii4_directory_fold": True}
SHOWS = {"q6_architecture_shares_by_cohort": "share of each cohort's designs by architecture", "q7_condition2_balance": "condition 2: ²D against its permutation band, per level",
         "q7_condition3_cohesion": "condition 3: ΔQ against its permutation band, main weighting, levels A, A·W·T, A·U", "q7_condition1_family": "condition 1: F's share per priority year, two bases",
         "q7_family_conditions": "the three conditions on F: all designs (band) and actively protected (dashed)",
         "q6_largest_architectures_over_time": "five largest architectures' share per cohort", "q7_iii4_directory_categories": "III.4: Vectored Thrust share per year (met years as bars) and ²D against the band",
         "q7_verdict_table": "verdict per condition and level, all designs (main) and actively protected (sensitivity), each base read alone", "q7_verdict_detail": "the numbers behind the verdict on each base", "q7_condition3_weights": "weights of the form distance (w15): 15 dimensions, four systems each weighing 1", "q7_condition3_family": "condition 3 on F: actively protected, all designs, granted and live",
         "q6_share_trend_spearman": "Spearman rho of architecture share on priority year", "q7_three_year_check": "condition 1 with three consecutive years",
         "q7_granted_live_condition1": "F's share per year, granted and live patents", "q7_granted_live_condition2": "²D of F, granted and live patents",
         "q7_iii4_directory_fold": "architectures folded to the directory categories"}


def _item(name):
    return next(i for i in v3.ITEMS if i["name"] == name)


def draw(item, ctx, frac: float):
    """Build ``item`` at width frac × text block; height capped at 55 % of the width; return (figure, data, checks). The items in RESTYLED
    are built by their builders at the full text width (6.3 in) under notebooks/thesis_style.py and are returned as built."""
    if item["name"] in RESTYLED:
        fig, data = item["builder"](ctx)
        fig.canvas.draw()
        return fig, data, (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, 7.0)))
    from matplotlib import style as mstyle
    w_in = TEXT_CM / 2.54 * frac
    old = ctx.W
    ctx.W = w_in
    try:
        with plt.style.context(str(Path(v3.__file__).with_name("part1.mplstyle"))):
            fig, data = item["builder"](ctx)
            h = min(fig.get_figheight(), MAX_H * w_in)
            fig.set_size_inches(w_in, h)
            fig.canvas.draw()
            chk = (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, 7.0)))
    finally:
        ctx.W = old
    return fig, data, chk


def export(cfg, ctx):
    R = root(cfg)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    rows, manifest, checks = [], [], []
    for name, (frac, used) in FIGS.items():
        it = _item(name)
        fig, data, chk = draw(it, ctx, frac)
        out = R / "Figures" / "Part_III_dominant_design" / it["group"] / it["role"]
        out.mkdir(parents=True, exist_ok=True)
        if name in RESTYLED:
            v3.ts.save(fig, name, out)                    # pdf + 300 dpi png; refuses a width other than 6.3 in or text under 8 pt
        else:
            fig.savefig(out / f"{name}.pdf")
        info = (round(fig.get_figwidth() * 2.54, 2), round(fig.get_figheight() * 2.54, 2))
        plt.close(fig)
        if data is not None:
            data.to_csv(csvd / f"{name}.csv", index=False)
        checks.append({"figure": name, "width cm": info[0], "height cm": info[1], "height / width": round(info[1] / info[0], 3),
                       "text over text": chk[0], "under 7 pt": chk[1]})
        manifest.append((f"Figures/Part_III_dominant_design/{it['group']}/{it['role']}/{name}.pdf", used, SHOWS[name]))
        manifest.append((f"Data_for_writing/csv/{name}.csv", used, "data behind " + name))
    for name, used in TABLES.items():
        t, _ = _item(name)["builder"](ctx)
        t.to_csv(csvd / f"{name}.csv", index=False)
        manifest.append((f"Data_for_writing/csv/{name}.csv", used, SHOWS[name]))
    _numbers(cfg, ctx, R)
    manifest.append(("Data_for_writing/NUMBERS_III.md", True, "numbers of Analysis III with their sources"))
    mf = R / "Data_for_writing" / "MANIFEST.md"
    new = not mf.exists()
    with open(mf, "a", encoding="utf-8") as f:
        if new:
            f.write("# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n")
        have = mf.read_text(encoding="utf-8") if not new else ""
        for p, used, what in manifest:
            if f"`LaTeX_v15/{p}`" in have:
                continue
            f.write(f"- `LaTeX_v15/{p}` · {'yes' if used else 'no (leaves the text)'} · {what}\n")
    return pd.DataFrame(checks)


def _numbers(cfg, ctx, R: Path):
    d = q7._data(ctx)
    d6 = q6._data(ctx)
    share = d6["share"]
    n_win = d6["n_win"]
    cohort = lambda w: "2024–26*" if "partial" in w else w          # noqa: E731
    tpl = pd.DataFrame({"cohort": [cohort(w) for w in ctx.WIN_NAMES], "designs": n_win.to_numpy(),
                        "Tilt Propulsor": (share["TR"] * 100).round(1).astype(str) + " %", "Lift + Cruise": (share["SLC"] * 100).round(1).astype(str) + " %"})
    di = analysis3.directory(ctx, d)
    v = ctx.v
    state = frames.patent_state(ctx.ds, v)
    live = v["aircraft_id"].map(state["in_force"]).astype(bool)
    k = v["class5"].where(v["topType"].notna())
    sel = live & k.notna() & v["window"].notna()
    vt = pd.DataFrame({"cohort": [cohort(w) for w in ctx.WIN_NAMES]})
    vt["actively protected designs"] = [int((sel & v["window"].eq(w)).sum()) for w in ctx.WIN_NAMES]
    vt["VT designs"] = [int((sel & v["window"].eq(w) & k.eq("VT")).sum()) for w in ctx.WIN_NAMES]
    vt["VT share"] = (100 * vt["VT designs"] / vt["actively protected designs"]).round(1).astype(str) + " %"
    vy = di["yearly"]["in force"]
    vy = vy[vy["priority year"] >= 2016].assign(**{"share": lambda t: (100 * t["its share"]).round(1).astype(str) + " %"})[["priority year", "aircraft", "its aircraft", "share", "above 50 %"]]
    vy.to_csv(R / "Data_for_writing" / "csv" / "q7_iii4_vt_share_per_year.csv", index=False)
    bal = di["balance"][["window", "aircraft", "D2", "D2 permutation low", "D2 permutation high", "below band"]].rename(columns={"window": "cohort"})
    ver, _ = v3.tab_levels_verdict(ctx)
    wts, _ = v3.tab_condition3_weights(ctx)
    rho, _ = v3.tab_share_trend(ctx)
    t3, _ = v3.tab_three_year_check(ctx)
    fam, _ = v3.tab_condition3_family(ctx)
    gl1, _ = v3.tab_granted_live_condition1(ctx)
    gl2, _ = v3.tab_granted_live_condition2(ctx)
    form = d["form"]
    fm = form[form["weighting"].eq(frames.Q_WEIGHTINGS[0])]
    dist = pd.DataFrame({"cohort": [cohort(w) for w in ctx.WIN_NAMES]})
    # A·U has its own column: it leaves out GB202302720D0_ua1 (2020-23), whose recorded 0 propulsors is not a count (frames.propulsor_units)
    for lvl, nm in (("A0", "A and F"), ("A0c", "A·U"), ("A1t", "A·W·T")):
        c = fm[fm["level"].eq(lvl)].set_index("window")["aircraft"]
        dist[f"designs in the form distance, {nm}"] = [int(c.get(w, 0)) for w in ctx.WIN_NAMES]
    dist.insert(1, "designs in III.1 (denominator of the shares)", n_win.to_numpy())
    dist["difference to A"] = dist["designs in III.1 (denominator of the shares)"] - dist["designs in the form distance, A and F"]
    n7 = q7.numbers(ctx)
    n7 = {k_: x for k_, x in n7.items() if not k_.startswith(("r_", "px_", "pub_", "trl_", "ext_"))}
    import viz.thesis_text_q6 as tx6
    keys6 = sorted(set(re.findall(r"\{([a-z0-9_]+)\}", next(r["text"] for r in tx6.RESULTS if r["sub"] == "B"))))
    n6 = q6.numbers(ctx)
    L = ["# NUMBERS_III — Analysis III (dominant design)\n",
         "Written by notebook 52 (`viz/thesis_latex_part3.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`.\n",
         "## (a) III.1, cohort shares of Tilt Propulsor and Lift + Cruise\n", "Source: `q6_architecture_shares_by_cohort.csv` (share of the cohort's designs).\n", tables_md(tpl), "",
         "## III.1, Spearman rho of share on priority year (2008–2023)\n", "Source: `q6_share_trend_spearman.csv`.\n", tables_md(rho), "",
         "## (b) III.4, VT on the five directory categories, actively protected designs\n",
         "Source: `q7_iii4_directory_categories.csv` (balance), notebook 52 §III4. VT is the largest category in every year and cohort. Fold: `q7_iii4_directory_fold.csv`.\n",
         "VT share per cohort:\n", tables_md(vt), "", "VT share per priority year (read years, 20 designs or more, 2016–2023); condition 1 met in "
         + ", ".join(map(str, di["met"])) + " (all designs: " + ", ".join(map(str, di["met_all"])) + "):\n", tables_md(vy), "",
         "Balance (²D rarefied to 40, all designs, 1000 permutations) with the band, per cohort; 2024–26* is incomplete and not read:\n", tables_md(bal), "",
         "## Verdict table (each base read alone: all designs is the main reading, actively protected the sensitivity; condition 3 under the w15 weighting)\n", "Source: `q7_verdict_table.csv`.\n", tables_md(ver), "",
         "## The numbers behind the verdict\n", "Source: `q7_verdict_detail.csv`. Condition 1: the largest share of a read year (20 designs or more) and the years met; condition 2: ²D rarefied to 40 and the lower edge of its band; condition 3: ΔQ 2020-23 of the form distance under w15 (15 dimensions, each of the four systems weighing 1) and the lower edge of its band (1000 permutations, seed 42).\n", tables_md(analysis3.verdict_two_bases(ctx)[1]), "",
         "## Weights table (condition 3, the reported weighting w15: 15 dimensions of the codebook, each of the four systems weighing 1, 4 in all)\n", "Source: `q7_condition3_weights.csv`; 15 dimensions, 625 designs (two designs have no architecture recorded). "
         "Eleven dimensions are compared as options (0 same, 1 different); three are ordered and compared by rank difference over a fixed range: boom count (0 when no boom, 1, 2, 3 to 4, 5 or more; / 4), wing count (0 when no wing, 1, 2, 3; / 3) and the band of propulsors (1 to 3, 4, 5 to 6, 7 to 8, 9 or more; / 4, the bands of A·U); "
         "the tilt share is the share 0 to 1 of the design's propulsors whose thrust turns between hover and cruise (a propulsor that pivots on its mount, sits on a tilting wing, a tilting empennage or a tilting boom, or a Tilt Body design, which turns whole), compared by absolute difference; "
         "the mount locations are the set of stations carrying propulsors among fuselage, wing, boom and empennage, compared by Jaccard distance (the share of the stations used by either design that only one of them uses). "
         "The three wing dimensions read wing 1 (the primary wing of codebook R5-03, which is wing 1 in every design: the author checked the 4 designs whose role reading pointed to wing 2 on 2026-10-16); enclosure and tractor/pusher arrangement read the set with the most propulsors (first listed on a tie); a dimension that does not apply or that an override hides is blank and left out of the pair's average, and the propulsion dimensions are blank for designs with no propulsor card (Hoverbike, Personal Flying Vehicle). The 34-dimension weighting of 2026-10-14 (w34) stays in the code for the record and is no longer reported.\n", tables_md(wts), "",
         "## Condition 3 on F (the same w15 weights; Q on the designs of F's base, per cohort)\n", "Source: `q7_condition3_family.csv`. Q uses no architecture, so F on all designs is the same set as A.\n", tables_md(fam), "",
         "## Three-year check (condition 1, three consecutive years, actively protected designs)\n", "Source: `q7_three_year_check.csv`.\n", tables_md(t3), "",
         "## F on granted and live patents alone\n", "Source: `q7_granted_live_condition1.csv`, `q7_granted_live_condition2.csv`.\n", tables_md(gl1), "", tables_md(gl2), "",
         "## III.4, which VT share the figure draws\n",
         "`q7_iii4_directory_categories` draws VT's share per priority YEAR (left panel, condition 1: all designs solid, actively protected dashed, years under 20 designs hollow grey; the met years of each base as red bars), "
         "and ²D per COHORT against its band (right panel, condition 2, all designs). The per-cohort VT share above is not drawn; it is listed here for the text. "
         "Per-year values: the table 'VT share per priority year' above, also written to `Data_for_writing/csv/q7_iii4_vt_share_per_year.csv`.\n",
         "## Designs per cohort: III.1 against the form distance of condition 3\n", "Source: `q6_architecture_shares_by_cohort.csv` (`designs`), `q7_condition3_cohesion.csv` (`aircraft`, w15 weighting).\n", tables_md(dist), "",
         "Why they differ: the shares of III.1 divide by every design of the cohort, including the designs with no architecture recorded (a bar segment 'no architecture recorded'), "
         "while the form distance needs an architecture to place a design in a level, so those designs are left out. The two designs without an architecture "
         "(`CN109263914A_ua1`, `CN109263949A_ua1`) have priority year 2018, so only 2016–19 differs (213 against 211). A·W·T drops further designs whose wings or tilt are not recorded.\n",
         "## Numbers quoted by the Results text, III.1 (sub-question B)\n", "Source: `viz/thesis_q6.py` numbers(ctx), notebook cell of the III1 group.\n",
         "\n".join(f"- `{k_}` = {n6[k_]}" for k_ in keys6 if k_ in n6), "",
         "## Numbers quoted by the Results text, III.2 to III.4 (Q7, regions and external comparison left out)\n", "Source: `viz/thesis_q7.py` numbers(ctx), notebook cells of the III2_III3 group.\n",
         "\n".join(f"- `{k_}` = {x}" for k_, x in n7.items()), ""]
    (R / "Data_for_writing" / "NUMBERS_III.md").write_text("\n".join(L), encoding="utf-8")


# ================================================================================== the population figure (2026-10-16), after Frenken, Saviotti and Trommetter (1999), Fig. 2
#: Every characterised design of the four complete cohorts, the same base as the disparity (condition 3 at A, the w15 Gower distance over the
#: 15 codebook dimensions: viz.thesis_v2_part4.dispersion_base). The pairwise distance is projected on two axes by classical multidimensional
#: scaling (principal coordinates): B = -1/2 J D² J, the two largest eigenvalues. Black and greys only, font 9 pt, 16 cm wide.
import numpy as np                                  # noqa: E402
from matplotlib.lines import Line2D                 # noqa: E402
from matplotlib.offsetbox import AnnotationBbox, OffsetImage   # noqa: E402

PCOA_GREY = {"<= 2011": "#b4b4b4", "2012-15": "#828282", "2016-19": "#4c4c4c", "2020-23": "#000000"}
PCOA_NAME = {"<= 2011": "≤2011", "2012-15": "2012-15", "2016-19": "2016-19", "2020-23": "2020-23"}
PCOA_PT = 9.0
POP_STEM = "q6_population_cloud"
#: where the three drawings sit (axes fraction) and the width of each (cm); the leader line runs from the drawing to the design's point
POP_IMAGE_SPOTS = {"closest to the ≤2011 centroid": (0.12, 0.85), "closest to the 2020-23 centroid": (0.87, 0.85), "farthest from the 2020-23 centroid": (0.87, 0.33)}
POP_IMAGE_CM = 2.6


def pcoa(D: np.ndarray):
    """Classical MDS of a distance matrix: the coordinates on the two largest axes and every eigenvalue (largest first)."""
    n = len(D)
    J = np.eye(n) - np.full((n, n), 1.0 / n)
    B = -0.5 * J @ (D ** 2) @ J
    w, U = np.linalg.eigh(B)
    o = np.argsort(w)[::-1]
    w, U = w[o], U[:, o]
    return U[:, :2] * np.sqrt(np.clip(w[:2], 0, None)), w


def population(ctx):
    """One row per design of the disparity base in the four complete cohorts: publication number, design, cohort, axis 1, axis 2; and
    the share of the distance each axis explains (its eigenvalue over the sum of the positive eigenvalues; a Gower distance is not Euclidean,
    so some eigenvalues are negative and are reported too). The sign of each axis is set so that the 2020-23 centroid lies to the right of
    and above the ≤2011 centroid (the sign of a PCoA axis is arbitrary)."""
    from viz import thesis_v2_part4 as p4
    D, _, sub = p4.dispersion_base(ctx)
    sub = sub[sub["window"].isin(ctx.COMPLETE)].copy()
    rows = sub["row"].to_numpy()
    X, w = pcoa(D[np.ix_(rows, rows)])
    first, last = sub["window"].eq(ctx.COMPLETE[0]).to_numpy(), sub["window"].eq(ctx.COMPLETE[-1]).to_numpy()
    for j in range(2):
        if X[last, j].mean() < X[first, j].mean():
            X[:, j] *= -1
    pos = float(w[w > 0].sum())
    pop = pd.DataFrame({"publication number": sub["patent_id"].to_numpy(), "design": sub["aircraft_id"].to_numpy(), "cohort": sub["window"].to_numpy(),
                        "axis 1": X[:, 0], "axis 2": X[:, 1]})
    info = {"designs": int(len(pop)), "explained axis 1": float(w[0] / pos), "explained axis 2": float(w[1] / pos),
            "explained of the absolute total, axes 1 and 2": (float(w[0] / np.abs(w).sum()), float(w[1] / np.abs(w).sum())),
            "eigenvalues 1-5": [round(float(x), 3) for x in w[:5]], "sum of positive eigenvalues": round(pos, 3), "sum of negative eigenvalues": round(float(w[w < 0].sum()), 3)}
    return pop, info


def population_picks(pop: pd.DataFrame, ctx) -> pd.DataFrame:
    """The three designs drawn: among the designs of a cohort, the one closest to (or farthest from) that cohort's centroid in the plane."""
    cent = pop.groupby("cohort")[["axis 1", "axis 2"]].mean().reindex(ctx.COMPLETE)
    v = ctx.v.set_index("aircraft_id")
    rows = []
    for why, w, farthest in (("closest to the ≤2011 centroid", ctx.COMPLETE[0], False), ("closest to the 2020-23 centroid", "2020-23", False),
                             ("farthest from the 2020-23 centroid", "2020-23", True)):
        s = pop[pop["cohort"] == w]
        d = np.hypot(s["axis 1"] - cent.loc[w, "axis 1"], s["axis 2"] - cent.loc[w, "axis 2"])
        i = d.idxmax() if farthest else d.idxmin()
        r = s.loc[i]
        fr = _drawing(ctx, r["design"])
        rows.append({"role": why, "publication number": r["publication number"], "design": r["design"], "cohort": w, "axis 1": round(float(r["axis 1"]), 4),
                     "axis 2": round(float(r["axis 2"]), 4), "distance to the centroid in the plane": round(float(d[i]), 4),
                     "architecture": v.loc[r["design"], "topType"], "priority year": int(v.loc[r["design"], "year"]), "name": v.loc[r["design"], "aircraft_name"],
                     "assignee": v.loc[r["design"], "assignee"], "figure key": str(fr["fig_key"]), "view": fr["per"], "state": fr["acState"],
                     "image path": fr["image_path"], "rotation (deg)": float(fr["rotation_deg"]) if pd.notna(fr["rotation_deg"]) else 0.0})
    return pd.DataFrame(rows)


def _drawing(ctx, aircraft_id: str) -> pd.Series:
    """The design's line drawing from the characterised figure record: its main approved image, else the first approved one by view
    (front-isometric, top, side, other)."""
    f = ctx.ds.figures
    a = f[(f["aircraft_id"] == aircraft_id) & (f["status"] == "approved")].copy()
    assert len(a), aircraft_id
    a["view rank"] = a["per"].map({"Front-Isometric": 0, "Top": 1, "Side": 2}).fillna(3)
    a["main rank"] = (~a["is_main"].fillna(False).astype(bool)).astype(int)
    return a.sort_values(["main rank", "view rank"]).iloc[0]


def fig_population_cloud(ctx):
    from viz import thesis_latex_part4 as l4
    pop, info = population(ctx)
    picks = population_picks(pop, ctx)
    cent = pop.groupby("cohort")[["axis 1", "axis 2"]].mean().reindex(ctx.COMPLETE)
    w_in = TEXT_CM / 2.54
    fig, ax = plt.subplots(figsize=(w_in, 0.68 * w_in), constrained_layout=True, dpi=100)
    for w in ctx.COMPLETE[::-1]:                                   # the later, larger cohorts first: the small early ones stay visible on top
        s = pop[pop["cohort"] == w]
        ax.scatter(s["axis 1"], s["axis 2"], s=7, color=PCOA_GREY[w], linewidths=0, zorder=2)
    ax.plot(cent["axis 1"], cent["axis 2"], color="black", linewidth=0.8, zorder=3)
    for w in ctx.COMPLETE:
        ax.scatter(cent.loc[w, "axis 1"], cent.loc[w, "axis 2"], s=80, color=PCOA_GREY[w], edgecolor="black", linewidth=0.9, zorder=4)
    offs = {"<= 2011": (7, -9), "2012-15": (8, 0), "2016-19": (8, -2), "2020-23": (-8, 6)}
    for w in ctx.COMPLETE:
        dx, dy = offs[w]
        ax.annotate(PCOA_NAME[w], (cent.loc[w, "axis 1"], cent.loc[w, "axis 2"]), textcoords="offset points", xytext=(dx, dy),
                    ha="left" if dx > 0 else "right", va="center", fontsize=PCOA_PT, zorder=6, bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.85))
    ax.set_xlabel("PCoA axis 1", fontsize=PCOA_PT)
    ax.set_ylabel("PCoA axis 2", fontsize=PCOA_PT)
    ax.tick_params(labelsize=PCOA_PT)
    ax.grid(False)
    ax.set_aspect("equal", adjustable="datalim")
    ax.text(0.99, 0.02, f"axis 1: {100 * info['explained axis 1']:.1f} %, axis 2: {100 * info['explained axis 2']:.1f} %\nof the distance (positive eigenvalues)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=PCOA_PT, linespacing=1.2)
    handles = [Line2D([], [], marker="o", markersize=4, color=PCOA_GREY[w], linestyle="none", label=f"{PCOA_NAME[w]}, n {int((pop['cohort'] == w).sum())}") for w in ctx.COMPLETE]
    handles += [Line2D([], [], marker="o", markersize=8, markerfacecolor="white", markeredgecolor="black", color="black", linewidth=0.8, label="cohort centroid, joined in time order")]
    ax.legend(handles=handles, loc="lower left", fontsize=PCOA_PT, frameon=True, framealpha=0.92, edgecolor="none", handlelength=1.4, labelspacing=0.3)
    # the three drawings beside their points, with a thin leader line and the publication number
    px_per_cm = fig.dpi / 2.54
    for _, r in picks.iterrows():
        im = np.asarray(l4._crop(r["image path"], r["rotation (deg)"]))
        zoom = POP_IMAGE_CM * px_per_cm / im.shape[1]
        bx, by = POP_IMAGE_SPOTS[r["role"]]
        ab = AnnotationBbox(OffsetImage(im, zoom=zoom, cmap="gray", clim=(0, 255)), (r["axis 1"], r["axis 2"]), xybox=(bx, by), xycoords="data",
                            boxcoords="axes fraction", frameon=False, pad=0, zorder=7, arrowprops=dict(arrowstyle="-", color="black", linewidth=0.6, shrinkA=0, shrinkB=2))
        ax.add_artist(ab)
        h_frac = im.shape[0] * zoom / (fig.get_figheight() * fig.dpi) / 0.8          # about the drawing's height as a share of the axes
        ax.text(bx, by - h_frac / 2 - 0.015, r["publication number"], transform=ax.transAxes, ha="center", va="top", fontsize=PCOA_PT, zorder=8)
    return fig, pop, picks, info


def export_population_cloud(cfg, ctx):
    """Write q6_population_cloud.pdf to LaTeX_v15/Figures/Part_III_dominant_design/III2_III3_dominant_design/main/ and its CSV (one row per
    design: publication number, design, cohort, axis 1, axis 2) to Data_for_writing/csv/; append the manifest lines.
    Returns (checks, the three designs drawn, the explained shares, the LaTeX_v15-relative paths written)."""
    from matplotlib.text import Text
    R = root(cfg)
    with plt.style.context(str(Path(v3.__file__).with_name("part1.mplstyle"))):
        fig, pop, picks, info = fig_population_cloud(ctx)
        for t in fig.findobj(Text):
            if t.get_text() and t.get_fontsize() < PCOA_PT:
                t.set_fontsize(PCOA_PT)
        fig.canvas.draw()
        chk = {"figure": POP_STEM, "width cm": round(fig.get_figwidth() * 2.54, 2), "height cm": round(fig.get_figheight() * 2.54, 2),
               "text over text": len(figcheck.overlaps(fig)), "under 9 pt": len(figcheck.small_text(fig, PCOA_PT))}
    out = R / "Figures" / "Part_III_dominant_design" / "III2_III3_dominant_design" / "main"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{POP_STEM}.pdf")
    plt.close(fig)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    pop.round({"axis 1": 5, "axis 2": 5}).to_csv(csvd / f"{POP_STEM}.csv", index=False)
    rel = [f"Figures/Part_III_dominant_design/III2_III3_dominant_design/main/{POP_STEM}.pdf", f"Data_for_writing/csv/{POP_STEM}.csv"]
    mf = R / "Data_for_writing" / "MANIFEST.md"
    have = mf.read_text(encoding="utf-8") if mf.exists() else ""
    with open(mf, "a", encoding="utf-8") as f:
        for p, what in ((rel[0], "population of designs (four complete cohorts) on the two principal coordinates of the w15 Gower distance, cohort centroids joined in time order, three drawings"),
                        (rel[1], f"data behind {POP_STEM}: one row per design, publication number, design, cohort, axis 1, axis 2")):
            if f"`LaTeX_v15/{p}`" not in have:
                f.write(f"- `LaTeX_v15/{p}` · yes · {what}\n")
    return pd.DataFrame([chk]), picks.drop(columns=["image path"]), info, rel
