"""Analysis III, one pass: the Spearman table of the architecture shares (III.1), the weights of condition 3, the three-year
check of condition 1, the granted-and-live base of F, and III.4 (condition 1 and 2 on the five directory categories).

Drawn and written by notebook 52 through viz/thesis_v2_part3.py.
Reuses viz.thesis_q7 / viz.thesis_q6 builders, lib.dominant_design and viz.frames; no method of them is changed.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy import stats

from lib import dominant_design as dd
from viz import config, frames, plots, style, thesis, thesis_q6, thesis_q7

RUN3 = 3


def runs(years, k: int) -> list:
    """Years that sit in a run of at least ``k`` consecutive years (k = 2 is :func:`lib.dominant_design.condition1_years`)."""
    ys = sorted(int(y) for y in years)
    out, cur = set(), []
    for y in ys:
        cur = cur + [y] if cur and y == cur[-1] + 1 else [y]
        if len(cur) >= k:
            out.update(cur)
    return sorted(out)


# ---- III.1
def rho_table(ctx) -> pd.DataFrame:
    """Spearman rho and p of each architecture's share of the year's aircraft on the priority year (2008 to the last complete
    year), architectures with 20 aircraft or more over those years; all unique aircraft with an architecture recorded."""
    v = ctx.v
    last = ctx.cfg.analysis["last_complete_year"]
    w = v[v["topType"].notna() & v["year"].between(frames.DD_YEAR_FIRST, last)]
    cnt = pd.crosstab(w["year"], w["topType"])
    share = cnt.div(cnt.sum(axis=1), axis=0)
    rows = []
    for c in cnt.columns:
        n = int(cnt[c].sum())
        if n < 20:
            continue
        r, p = stats.spearmanr(share.index, share[c])
        ok = cnt.sum(axis=1) >= frames.DD_YEAR_MIN
        r2, p2 = stats.spearmanr(share.index[ok], share.loc[ok, c]) if ok.sum() > 3 else (np.nan, np.nan)
        rows.append({"code": c, "architecture": style.cls(c).name, "aircraft": n, "years": len(share), "rho": round(float(r), 3),
                     "p": float(p), "rho, years with 20+ aircraft": round(float(r2), 3), "p, years with 20+ aircraft": float(p2),
                     "years with 20+ aircraft": int(ok.sum())})
    t = pd.DataFrame(rows)
    first = {"SLC": 0, "TR": 1}
    t = t.assign(_o=t["code"].map(first).fillna(2)).sort_values(["_o", "aircraft"], ascending=[True, False]).drop(columns="_o")
    return t.reset_index(drop=True)


# ---- condition 3 weights
def weights_report(ctx) -> dict:
    frame, fields, numeric = frames.gower_inputs(ctx.ds)
    return {"table": frames.form_weights_table(), "n_fields": len(fields), "n_aircraft": len(frame), "numeric": sorted(numeric)}


# ---- condition 3 on F, three bases
def form_family(ctx) -> pd.DataFrame:
    """Condition 3 on F: Q of the form distance per cohort against the two earliest cohorts and its permutation band, on the designs of F's
    base (an architecture recorded, as at A: Q uses no architecture, F only regroups the designs), for the actively protected designs, all
    designs and the granted-and-live designs. A fresh generator (seed) per base; the same weights as :func:`weights_report`."""
    ds, v = ctx.ds, ctx.v
    frame, fields, numeric = frames.gower_inputs(ds)
    at = {a: i for i, a in enumerate(frame["aircraft_id"].to_numpy())}
    D = frames._dist.gower_distance(frame, fields, numeric, frames.form_weights(fields))
    state = frames.patent_state(ds, v)
    f = frames.dd_level_keys(ds, v)["family_b"]
    out = []
    for base, st in (("actively protected", "in_force"), ("all designs", None), ("granted and live", "granted_live")):
        m = f.notna() & v["window"].notna()
        if st:
            m &= v["aircraft_id"].map(state[st]).astype(bool)
        sub = v[m].copy()
        sub["row"] = sub["aircraft_id"].map(at)
        sub = sub[sub["row"].notna()]
        t = dd.cohesion_band(D, sub["row"].astype(int).to_numpy(), sub["window"].to_numpy(), ctx.WIN_NAMES, perms=thesis_q7.PERMS, seed=ctx.SEED)
        t.insert(0, "base", base)
        out.append(t)
    t = pd.concat(out, ignore_index=True).rename(columns={"window": "cohort", "aircraft": "designs", "Q of the earliest windows": "Q of the earliest cohorts"})
    t["partial"] = t["cohort"].astype(str).str.contains("partial")
    return t


# ---- item 4: three consecutive years on the in-force base
def three_year(d) -> dict:
    dy, fy = d["dy"], d["fy"]
    out = {}
    for lvl, name in (("A0", "A"), ("A1t", "A·W·T"), ("A0c", "A·U")):
        y = dy[(dy["level id"] == lvl) & (dy["base"] == "in force") & dy["read"].astype(bool)]
        out[name] = runs(y[y["above 50 %"].astype(bool)]["priority year"], RUN3)
    out["F"] = runs(fy[fy["read, in force"].astype(bool) & (fy["F share in force"] > 0.5)]["priority year"], RUN3)
    return out


# ---- item 5: granted and live
def granted_live(ctx, d) -> dict:
    ds, v = ctx.ds, ctx.v
    state = frames.patent_state(ds, v)
    f = frames.dd_level_keys(ds, v)["family_b"]
    gl = v["aircraft_id"].map(state["granted_live"]).astype(bool)
    m = f.notna() & gl
    last = ctx.cfg.analysis["last_complete_year"]
    yearly = []
    for y in range(frames.DD_YEAR_FIRST, last + 1):
        s = f[m & v["year"].eq(y)]
        k = int((s == frames.FAMILY_LABEL).sum())
        yearly.append({"priority year": y, "aircraft": len(s), "F aircraft": k, "F share": k / len(s) if len(s) else np.nan,
                       "read": len(s) >= frames.DD_YEAR_MIN})
    y = pd.DataFrame(yearly)
    over = y[y["read"] & (y["F share"] > 0.5)]
    met = runs(over["priority year"], 2)
    w0 = v[m].dropna(subset=["window"])
    bal = dd.balance_band(f[w0.index], w0["window"], ctx.WIN_NAMES, n=ctx.cfg.analysis["rarefy_n"], perms=thesis_q7.PERMS, seed=ctx.SEED)
    return {"yearly": y, "met": met, "balance": bal}


# ---- item 6: directory categories
def directory(ctx, d) -> dict:
    ds, v = ctx.ds, ctx.v
    state = frames.patent_state(ds, v)
    k = v["class5"].where(v["topType"].notna())
    live = v["aircraft_id"].map(state["in_force"]).astype(bool)
    last = ctx.cfg.analysis["last_complete_year"]
    yrs = range(frames.DD_YEAR_FIRST, last + 1)
    res = {}
    for base, mask in (("in force", live & k.notna()), ("all", k.notna())):
        t = dd.yearly_top_share(k[mask], v.loc[mask, "year"], yrs, frames.DD_YEAR_MIN)
        res[base] = t
    met = sorted(dd.condition1_years(res["in force"]))
    met_all = sorted(dd.condition1_years(res["all"]))
    w0 = v[k.notna()].dropna(subset=["window"])
    bal = dd.balance_band(k[w0.index], w0["window"], ctx.WIN_NAMES, n=ctx.cfg.analysis["rarefy_n"], perms=thesis_q7.PERMS, seed=ctx.SEED)
    return {"yearly": res, "met": met, "met_all": met_all, "balance": bal, "counts": k.value_counts().to_dict()}


def fig_directory(ctx, r):
    win = ctx.WIN_NAMES
    bal = r["balance"].set_index("window").reindex(win)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(ctx.W, 3.2), constrained_layout=True)
    fi, fa = r["yearly"]["in force"].set_index("priority year"), r["yearly"]["all"].set_index("priority year")
    yrs = fi.index.to_numpy()
    rd_i, rd_a = fi["read"].to_numpy(bool), fa["read"].to_numpy(bool)
    first = int(yrs[rd_i][0])
    plots.condition1_years(a1, yrs, fi["its share"], fa["its share"], rd_i, rd_a, r["met"], first, "")
    a1.set_ylim(0, 1.05)
    a1.text((yrs[0] + first - 1) / 2, 0.05, f"under {frames.DD_YEAR_MIN} aircraft:\nnot read", ha="center", va="bottom", fontsize=7, color=style.MUTED)
    a1.set_xticks(yrs, [str(y)[2:] for y in yrs], fontsize=7)
    a1.set_xlabel("priority year", fontsize=7.5)
    a1.set_ylabel(f"share of the year's aircraft in the\nlargest category ({r['yearly']['in force']['largest archetype'].mode().iloc[0]})", fontsize=7.5)
    a1.set_title("Condition 1", fontsize=7.5, loc="left")
    a1.text(yrs[-1] + 0.5, 0.505, "50 %", ha="right", va="bottom", fontsize=7.5)
    partial = ["partial" in w for w in win]
    metw = [bool(bal.loc[w, "below band"]) and "partial" not in w for w in win]
    plots.balance_panel(a2, bal.reset_index(), partial, metw, [plots.WINDOW_TICKS[w] for w in win])
    a2.set_ylabel("²D: large designs in play", fontsize=7.5)
    a2.set_xlabel("priority cohort", fontsize=7.5)
    a2.set_title("Condition 2", fontsize=7.5, loc="left")
    fig.legend(handles=[Line2D([], [], color=style.INK, linewidth=1.7, marker="o", markersize=4.4, label="actively protected aircraft"),
                        Line2D([], [], color=style.MUTED, linewidth=1.2, linestyle="--", marker="s", markersize=4.2, markerfacecolor="white", label="all aircraft"),
                        Patch(facecolor="#dedcd8", label="permutation band (95 %)"),
                        Line2D([], [], color=style.INK, marker="o", markersize=3.6, linewidth=1.3, label=f"²D rarefied to {ctx.cfg.analysis['rarefy_n']}")],
               loc="outside lower center", ncol=4, fontsize=7.5, handlelength=1.8, columnspacing=1.2)
    return fig
