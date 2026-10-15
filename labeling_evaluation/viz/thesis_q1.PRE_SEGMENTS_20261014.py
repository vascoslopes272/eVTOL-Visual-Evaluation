"""Thesis question 1, growth: "How fast does it grow, and where?" (THESIS_CONTRACT.md §3, Q1).

Items (one graph per file) ported from notebook 40 (§1.1, §1.2: Figure 1 (i), Figure 1 (ii), Figure 4, the growth
tables) and notebook 44 (Figure 23 (i)). The number computations are ported from the same cells; everything is
computed once per context (``_calc``) and shared by the builders and ``numbers``.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib import association, growth, regional
from viz import flow, frames, plots, style

_CACHE: dict = {}


# ------------------------------------------------------------------------------------------------ computations
def _calc(ctx):
    """Every frame the Q1 items and numbers rest on, built once per context (notebook 40 §1.1, §1.2; 44 §5.2)."""
    key = id(ctx)
    if key in _CACHE:
        return _CACHE[key]
    ds, v, cfg = ctx.ds, ctx.v, ctx.cfg
    c = {}
    # §1.1.1 filings per priority year, §1.1.2 growth series, rates and ratios
    fpy = frames.filings_per_year(ds, v, cfg)
    ser = frames.growth_series(ds, v, cfg)
    names = dict(frames.GROWTH_SERIES)
    rows = []
    for lo, hi in (growth.FIT_WINDOW, growth.FIT_SENSITIVITY[0]):
        for k, name in frames.GROWTH_SERIES:
            yrs, cnt = growth.window_frame(ser[k], lo, hi)
            fit = growth.loglinear_fit(yrs, cnt)
            rows.append({"series": name, "key": k, "window": f"{lo}–{hi}", "total": int(cnt.sum()),
                         "doubling time (years)": round(fit["doubling time (years)"], 1),
                         "95 % interval": f"{fit['doubling low']:.1f} to {fit['doubling high']:.1f}",
                         "growth per year": f"{fit['growth per year %']:.0f} %", "primary": (lo, hi) == growth.FIT_WINDOW})
    rates = pd.DataFrame(rows)
    r = growth.growth_ratio_table(ser, ["evtol_families", "evtol_aircraft"], ["b64", "secb", "all"])
    ratios = pd.DataFrame({"eVTOL counted as": r["eVTOL counted as"].map(names), "against": r["against"].map(names),
                           "window": r["window"], "times as fast": r["times as fast"],
                           "95 % interval": [f"{a:.2f} to {b:.2f}" for a, b in zip(r["low"], r["high"])],
                           "reading": r["reading"], "primary": r["primary"]})
    # §1.1.3 the turning point (one generator shared by the three series, in this order)
    d = fpy.loc[2006:2023]
    rng = np.random.default_rng(ctx.SEED)
    tp = {name: growth.turning_point(d.index.to_numpy(float), np.log(d[col].to_numpy(float)), rng)
          for name, col in [("representative patents", "patents representative"), ("unique aircraft", "unique aircraft"),
                            ("aircraft per 1 000 B64", "aircraft per 1 000 B64")]}
    fits = {k: growth.loglinear_fit(*growth.window_frame(ser[k], *growth.FIT_WINDOW)) for k in ser}
    lag = frames.publication_lag(ds, by="region").set_index("region").loc[frames.REGIONS]
    # §5.2 aircraft per year and region, the lag correction and the regional delays
    ry = frames.region_years(ds, v)
    _, ll = regional.lead_lag(v, "region3")
    off = regional.lag_offsets(regional.lag_frame(v, class_names=frames.LAG_CLASS_NAMES))
    # §1.2 active protection (method of 2026-10-12): EVERY priority year; a design is actively protected when any patent that
    # shows it is in force at the snapshot. The old priority <= 2019 cut, the primary-patent-only reading and the US-only test
    # are dropped.
    w = frames.force_frame(ds, v, max_year=None)
    g = w.groupby("topType").agg(**{"unique aircraft": ("aircraft_id", "size"), "out of force": ("out", "sum")})
    g["out of force share"] = (g["out of force"] / g["unique aircraft"]).round(2)
    g["class"] = [style.cls(x).name for x in g.index]
    force = g.sort_values(["unique aircraft", "class"], ascending=[False, True]).reset_index().rename(columns={"topType": "code"})
    force = force[["class", "code", "unique aircraft", "out of force", "out of force share"]]
    tested = force.loc[force["unique aircraft"] >= frames.FORCE_TEST_MIN, "code"]
    big = w[w["topType"].isin(tested)]
    p_all, k_tested = _class_test(big, "out")
    meta = v.drop_duplicates("aircraft_id").set_index("aircraft_id")[["firm", "pub_office", "legal_status_raw", "window"]]
    wo = w.join(meta, on="aircraft_id")
    wo["office"] = np.where(wo["pub_office"].eq("US"), "US office", "other offices")
    p_office = association.chi2_test(pd.crosstab(wo["office"], wo["out"]).values)["p"]
    cohort = wo.groupby("window").agg(n=("aircraft_id", "size"), not_protected=("out", "mean"))
    c.update(fpy=fpy, ser=ser, names=names, rates=rates, ratios=ratios, tp=tp, fits=fits, lag=lag, ry=ry, ll=ll, off=off,
             w=w, force=force, p_all=p_all, k_tested=k_tested, wo=wo, p_office=p_office, cohort=cohort)
    _CACHE[key] = c
    return c


def _class_test(frame, col):
    table = pd.crosstab(frame["topType"], frame[col])
    return association.chi2_test(table.values)["p"], int(table.shape[0])


# ------------------------------------------------------------------------------------------------ builders
def fig_filings_per_year(ctx):
    """Figure 1 (i): unique aircraft per priority year by applicant region, the representative patents as a line,
    the dated sector events under the bars (the strip belongs to the year axis, so it stays with the graph)."""
    c = _calc(ctx)
    fpy = c["fpy"]
    regs = frames.REGIONS + ["Other regions"]
    t = fpy.loc[2005:, regs + ["patents representative", "complete"]].copy()
    t.loc[2005, regs + ["patents representative"]] = fpy.loc[:2005, regs + ["patents representative"]].sum()
    incomplete = list(t.index[~t["complete"].astype(bool)])
    events = frames.sector_events(ctx.cfg, fpy.attrs["snapshot"])
    years = list(t.index)
    n_rep = int(t["patents representative"].sum())
    fig, (ax, strip) = plt.subplots(2, 1, figsize=(ctx.W, 4.6), gridspec_kw=dict(height_ratios=[2.4, 1.75]), constrained_layout=True)
    plots.region_stack(ax, t[regs], line=t["patents representative"], line_label=f"representative patents ({ctx.thin(n_rep)})",
                       incomplete=incomplete, pooled_first="1999-2005 pooled")
    ax.set_xticks([])
    ax.set_ylabel("unique aircraft (bars)\nrepresentative patents (line)")
    first_inc = years.index(incomplete[0])
    ax.axvline(first_inc - 0.5, color=style.INK, linewidth=0.8, linestyle="--")
    ax.text(first_inc - 0.4, ax.get_ylim()[1] * 0.99, "incomplete years", va="top", fontsize=7, color=style.MUTED,
            bbox=dict(fc="white", ec="none", pad=0.5))
    ax.legend(loc="upper left")
    plots.event_strip(strip, events, years, parent=ax)
    strip.set_xlim(ax.get_xlim())
    strip.set_xticks(range(len(years)), [("≤2005" if y == 2005 else str(y)) for y in years], rotation=90)
    data = t.drop(columns="complete")
    return fig, data


def fig_growth_rates(ctx):
    """Figure 1 (ii): each series relative to its own 2005-09 mean on a log axis, with its fitted line over 2005-2023."""
    c = _calc(ctx)
    shown = ["evtol_families", "b64", "secb", "all"]          # the aircraft series is fitted but not drawn (as the document)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.3), constrained_layout=True)
    plots.growth_fits(ax, {k: c["ser"][k] for k in shown}, c["fits"], c["names"], 2005, 2023)
    ax.set_xticks(range(2005, 2024, 2))
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi * 2.0)                                  # room for the legend above the 2016-23 points
    ax.set_xlabel("priority year")
    ax.legend(loc="upper left", fontsize=7.5)
    data = pd.DataFrame({c["names"][k]: c["ser"][k] for k in shown}).loc[2005:2023]
    return fig, data


def tab_growth_rates(ctx):
    """Doubling times of every series over 2005-2023 and how many times as fast eVTOL architecture patents grow
    against each baseline (la_growth_rates and la_growth_ratios, primary window)."""
    c = _calc(ctx)
    rates = c["rates"][c["rates"]["primary"]].set_index("series")
    ratios = c["ratios"][(c["ratios"]["primary"]) & (c["ratios"]["eVTOL counted as"] == "eVTOL architecture patents")].set_index("against")
    rows = []
    for k, name in frames.GROWTH_SERIES:
        r = rates.loc[name]
        q = ratios.loc[name] if name in ratios.index else None
        rows.append({"series": name, "families 2005-2023": int(r["total"]), "doubling time (years)": f"{r['doubling time (years)']:.1f}",
                     "95 % interval": r["95 % interval"], "growth per year": r["growth per year"],
                     "eVTOL patents grow ... times as fast": "" if q is None else f"{q['times as fast']:.2f} ({q['95 % interval']})"})
    return pd.DataFrame(rows), None


def fig_na_drop_is_real(ctx):
    """Figure 23 (i): aircraft per priority year and region from 2012, North America's share of the year on its
    segment, the years the snapshot has not fully seen faded, the four dated sector events under the bars."""
    c = _calc(ctx)
    ry, ll = c["ry"], c["ll"]
    REGIONS = frames.REGIONS
    NA = REGIONS[0]
    ev_dates = ["2016-10-27", "2019-07-02", "2021-08-11", "2023-10-13"]
    ev_all = frames.sector_events(ctx.cfg, frames.snapshot_date(ctx.ds))
    events = ev_all[ev_all["date"].dt.strftime("%Y-%m-%d").isin(ev_dates)].reset_index(drop=True)
    tab = ry.pivot(index="priority year", columns="region", values="aircraft")[REGIONS]
    share = ry.pivot(index="priority year", columns="region", values="share of the year")[REGIONS]
    years = list(tab.index)
    incomplete = [y for y in years if y > regional.LAST_COMPLETE]
    med = ll.set_index("region3")["50 %"]
    fig, (a1, strip) = plt.subplots(2, 1, figsize=(ctx.W, 3.9), gridspec_kw=dict(height_ratios=[3.0, 1.35]), constrained_layout=True)
    plots.region_stack(a1, tab, incomplete=incomplete)
    first_inc = years.index(incomplete[0])
    a1.axvspan(first_inc - 0.5, len(years) - 0.3, color=plots.FEW_FILL, zorder=0, linewidth=0)
    a1.text(first_inc - 0.4, a1.get_ylim()[1] * 0.99, "not yet all\npublished", va="top", fontsize=7, color=style.MUTED)
    for i, y in enumerate(years):
        n_na = tab.loc[y, NA]
        if 2016 <= y <= regional.LAST_COMPLETE and n_na >= 8:
            a1.text(i, n_na / 2 if n_na >= 12 else 0.4, ctx.pct(share.loc[y, NA]), ha="center", va="center" if n_na >= 12 else "bottom",
                    rotation=90, fontsize=7, color=style.INK, zorder=6, bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))
    a1.set_xticks([])
    a1.set_ylabel("unique aircraft")
    h, _ = a1.get_legend_handles_labels()
    a1.legend(h, [f"{r} (median year {int(med[r])})" for r in REGIONS], loc="upper left", fontsize=7.5, handlelength=1.2)
    plots.event_strip(strip, events.assign(year=events["year"]), years, parent=a1)
    strip.set_xlim(a1.get_xlim())
    strip.set_xticks(range(len(years)), [str(y) for y in years], rotation=90, fontsize=7)
    return fig, ry


def fig_in_force_status(ctx):
    """Figure 4: the share of each architecture's designs (every priority year) that no patent in force protects at the
    snapshot; architectures of ten designs or more, n under each bar, the all-architectures share as a dashed line."""
    import textwrap
    from matplotlib.lines import Line2D
    from viz.thesis_v2_part1 import arch
    c = _calc(ctx)
    force, w = c["force"], c["w"]
    fd = force[(force["unique aircraft"] >= frames.FORCE_TEST_MIN) & (force["code"] != "ALL")].reset_index(drop=True)
    overall = float(w["out"].mean())
    fig, ax = plt.subplots(figsize=(ctx.W, 3.4), constrained_layout=True)
    x = np.arange(len(fd))
    small = plt.rcParams["xtick.labelsize"] - 1
    for i, r in fd.iterrows():
        s = arch(r["code"])
        ax.bar(x[i], r["out of force share"], 0.62, color=s.color, hatch=s.hatch, edgecolor="white", linewidth=0.6, zorder=3)
        ax.text(x[i], r["out of force share"] + 0.015, f"{r['out of force share']:.0%}", ha="center", va="bottom", fontsize=small)
        ax.annotate(f"n {int(r['unique aircraft'])}", (x[i], 0), xycoords=("data", "axes fraction"), xytext=(0, -3),
                    textcoords="offset points", ha="center", va="top", fontsize=small - 0.5, color=style.MUTED, annotation_clip=False)
    ax.set_xticks(x, ["\n".join(textwrap.wrap(arch(code).name, 10, break_long_words=False)) for code in fd["code"]], fontsize=small)   # names never touch
    ax.tick_params(axis="x", pad=14, length=0)          # n under each bar first, then the architecture name
    ax.axhline(overall, color=style.INK, linewidth=1, linestyle="--", zorder=2)
    ax.set_ylabel("Designs not actively protected (%)")
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(handles=[Line2D([], [], color=style.INK, linewidth=1, linestyle="--",
                              label=f"all architectures: {overall:.0%} of {len(w)} designs")], loc="upper right")
    return fig, fd


def fig_method_flow(ctx):
    """Methodology flowchart: how Q1 is answered, from the data to the figures and the Answer box."""
    nodes = [
        dict(id="data", kind="data", col=0, text="Aircraft, patents,\nthree baselines"),
        dict(id="scale", kind="step", col=1, text="Scale to 2005-09\nmean, log axis"),
        dict(id="region", kind="step", col=1, text="Count per year\nand region"),
        dict(id="fit", kind="test", col=2, text="Log-linear fit,\nturning point"),
        dict(id="f_year", kind="figure", col=3, text="Unique aircraft per\npriority year"),
        dict(id="f_growth", kind="figure", col=3, text="Growth of each\nseries, log axis"),
        dict(id="answer", kind="answer", col=4, text="How fast\nand where"),
    ]
    edges = [("data", "scale"), ("data", "region"), ("scale", "fit"), ("region", "fit"),
             ("fit", "f_year"), ("fit", "f_growth"), ("f_year", "answer"), ("f_growth", "answer")]
    return flow.chart(ctx.cfg, nodes, edges), None


# ------------------------------------------------------------------------------------------------ items
ITEMS = [
    dict(name="q1_method_flow", slot="method", kind="figure", sub="",
         title="How Q1 is answered",
         caption="How Q1 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source="viz.flow (Methodology flowchart)", unit="", read=""),
    dict(name="q1_filings_per_year", slot="results", kind="figure", sub="A",
         title="Unique aircraft per priority year",
         caption="Unique aircraft by the priority year of their first patent, stacked by applicant region, with the representative patents as a line and the dated sector events under the bars.",
         source_item="Figure 1 (i)", flag=None, flag_note="", builder=fig_filings_per_year,
         source="PatSeer (snapshot 2026-06-08) · human labelling · sector events: the author's dated list (checked 2026-09-23)",
         unit="unique aircraft and representative patents per priority year",
         read="The first bar holds 1999-2005. A year is faded with a dashed outline while the snapshot is less than the 90th-percentile publication lag (3 years) after its end; its bar total is printed on it. An event stands on its calendar year."),
    dict(name="q1_growth_rates", slot="results", kind="figure", sub="A",
         title="Growth of each series, log axis",
         caption="eVTOL architecture patents against three worldwide baselines (WIPO, PatSeer), each relative to its own 2005-09 mean on a log axis, with its fitted line over 2005-2023.",
         source_item="Figure 1 (ii)", flag=None, flag_note="", builder=fig_growth_rates,
         source="PatSeer worldwide simple families for CPC B64 and CPC section B · WIPO patent families by origin (indicator 6a) for all patents, exported 2026-09-25 · human labelling",
         unit="patent families per priority year, each relative to its own 2005-09 mean",
         read="Equal slopes are equal growth rates; points are yearly counts, lines are least-squares fits of log count on year over 2005-2023; the legend prints each doubling time."),
    dict(name="q1_growth_rates_table", slot="appendix", kind="table", sub="A",
         title="Doubling times against the baselines",
         caption="Doubling time of every series over 2005-2023 with its bootstrap interval, and how many times as fast the eVTOL architecture patents grow against each baseline.",
         source_item="la_growth_rates / la_growth_ratios (Figure 1 ii data)", flag=None, flag_note="", builder=tab_growth_rates,
         source="PatSeer · WIPO · human labelling (lib.growth.loglinear_fit, growth_ratio_table: 2 000 bootstrap draws over years, seed 42)",
         unit="patent families per priority year (the eVTOL unique aircraft row counts aircraft)",
         read="A ratio whose interval excludes 1 is a growth rate told apart from the baseline's."),
    dict(name="q1_na_drop_is_real", slot="appendix", kind="figure", sub="B",
         title="Aircraft per priority year and region",
         caption="Unique aircraft per priority year and applicant region from 2012, North America's share printed on its segment, the years the snapshot has not fully seen faded.",
         source_item="Figure 23 (i)", flag=None, flag_note="", builder=fig_na_drop_is_real,
         source="PatSeer (applicant country, priority and publication date) · human labelling · sector events: the author's dated list",
         unit="unique aircraft per priority year, the three regions",
         read="The number on the North America segment is its share of that year's aircraft (years from 2016 with 8 aircraft or more). Faded and shaded: years the snapshot of June 2026 has not fully seen. Dotted lines: dated sector events, hypotheses never tested as causes. The legend gives each region's median priority year to 2023."),
    dict(name="q1_in_force_status", slot="appendix", kind="figure", sub="B",
         title="Designs not actively protected, by architecture",
         caption="Share of each architecture's designs that no patent in force protects at the snapshot (2026-06-08), every priority year, architectures of ten designs or more.",
         source_item="Figure 4", flag=None, flag_note="", builder=fig_in_force_status,
         source="PatSeer legal status at the snapshot (2026-06-08) · human labelling (class, duplicates)",
         unit="designs, every priority year; share of the architecture's designs",
         read="A design is actively protected when any patent that shows it is in force at the snapshot. Number under each bar: its designs; dashed line: all architectures."),
]


# ------------------------------------------------------------------------------------------------ numbers
def numbers(ctx) -> dict:
    """Every number the Q1 text quotes, as printed (notebook 40 §1.1 and §1.2 numbers; notebook 44 §5.2 extras)."""
    c = _calc(ctx)
    thin, pct, pval = ctx.thin, ctx.pct, ctx.pval
    fpy, rates, ratios, tp, lag = c["fpy"], c["rates"], c["ratios"], c["tp"], c["lag"]
    ry, off, force, wo = c["ry"], c["off"], c["force"], c["wo"]
    NA, EU, AP = frames.REGIONS
    ge = lambda a, w: ratios[(ratios["eVTOL counted as"] == "eVTOL architecture patents") & (ratios["against"] == a) & (ratios["window"] == w)].iloc[0]
    dbl = lambda key: rates[(rates["key"] == key) & (rates["primary"])].iloc[0]["doubling time (years)"]
    main, sens = ge("aeronautics (CPC B64)", "2005–2023"), ge("aeronautics (CPC B64)", "2005–2019")
    ryi = ry.set_index(["priority year", "region"])
    late = ry[ry["priority year"] > regional.LAST_COMPLETE]
    last2 = ry[ry["priority year"] > regional.LAST_COMPLETE + 1]
    y23 = ry[ry["priority year"] == 2023]
    ap_mid = ry[(ry["region"] == AP) & ry["priority year"].between(2021, 2023)]["aircraft"]
    offi = off.set_index(["class", "region"])
    ap_old = [offi.loc[(frames.LAG_CLASS_NAMES[k], AP), "offset vs North America (years)"] for k in ("SLC", "TR", "TW")]
    fa = lambda code: force.loc[force["code"] == code, "out of force share"].iloc[0]
    share_of = lambda mask: float(wo.loc[mask, "out"].mean())
    n_all = int(len(c["w"]))
    return {
        # the dataset
        "unique_s": thin(len(ctx.v)), "representative_s": thin(ctx.ds.counts["patents_approved"]),
        "lag_p90": str(int(lag["90th percentile"].max())),
        "boot_draws": thin(growth.DRAWS), "turn_draws": thin(growth.TURNING_DRAWS), "seed": str(ctx.SEED),
        # §1.1 filings per year and the turning point
        "ac_2015": str(int(fpy.loc[2015, "unique aircraft"])), "ac_2018": str(int(fpy.loc[2018, "unique aircraft"])),
        "pat_2018": str(int(fpy.loc[2018, "patents representative"])),
        "turn_pat_year": str(tp["representative patents"]["break"]), "turn_pat_x": f"{tp['representative patents']['jump']:.1f}",
        "turn_pat_boot": pct(tp["representative patents"]["share"]),
        "turn_pat_prev": str(int(fpy.loc[tp["representative patents"]["break"] - 1, "patents representative"])),
        "turn_pat_after": str(int(fpy.loc[tp["representative patents"]["break"], "patents representative"])),
        "turn_ac_year": str(tp["unique aircraft"]["break"]), "turn_ac_x": f"{tp['unique aircraft']['jump']:.1f}",
        "turn_ac_lo": str(tp["unique aircraft"]["lo"]), "turn_ac_hi": str(tp["unique aircraft"]["hi"]),
        "turn_sh_lo": str(tp["aircraft per 1 000 B64"]["lo"]), "turn_sh_hi": str(tp["aircraft per 1 000 B64"]["hi"]),
        # §1.1 growth rates and ratios
        "dbl_fam": f"{dbl('evtol_families'):.1f}", "dbl_ac": f"{dbl('evtol_aircraft'):.1f}", "dbl_b64": f"{dbl('b64'):.1f}",
        "dbl_secb": f"{dbl('secb'):.1f}", "dbl_all": f"{dbl('all'):.1f}",
        "gr_fam_b64": f"{main['times as fast']:.2f}", "gr_fam_b64_ci": main["95 % interval"],
        "gr_fam_secb": f"{ge('transport and operations (CPC section B)', '2005–2023')['times as fast']:.2f}",
        "gr_fam_all": f"{ge('all patents', '2005–2023')['times as fast']:.2f}",
        "gr_fam_b64_19": f"{sens['times as fast']:.2f}", "gr_fam_b64_19_ci": sens["95 % interval"],
        # §5.2 North America's share and count, the lag correction
        "na_share_2021": pct(ryi.loc[(2021, NA), "share of the year"]), "na_share_2023": pct(ryi.loc[(2023, NA), "share of the year"]),
        "na_share_2023_corr": pct(ryi.loc[(2023, NA), "share corrected for publication lag"]),
        "na_share_2024_corr": pct(ryi.loc[(2024, NA), "share corrected for publication lag"]),
        "vis_2023_lo": pct(y23["visible at the snapshot"].min()), "vis_2023_hi": pct(y23["visible at the snapshot"].max()),
        "na_2021": str(int(ryi.loc[(2021, NA), "aircraft"])), "na_2023": str(int(ryi.loc[(2023, NA), "aircraft"])),
        "ap_2123_lo": str(int(ap_mid.min())), "ap_2123_hi": str(int(ap_mid.max())),
        "na_share_partial": pct(late.groupby("region")["aircraft"].sum()[NA] / late["aircraft"].sum()),
        "ap_2526": str(int(last2[last2["region"] == AP]["aircraft"].sum())),
        "other_2526": str(int(last2[last2["region"] != AP]["aircraft"].sum())),
        "vis_2025_ap": pct(ryi.loc[(2025, AP), "visible at the snapshot"]), "vis_2025_na": pct(ryi.loc[(2025, NA), "visible at the snapshot"]),
        "ap_delay_range": f"{int(min(ap_old))} to {int(max(ap_old))}" if min(ap_old) != max(ap_old) else f"{int(min(ap_old))}",
        "ap_delay_cvt": _yrs(offi.loc[(frames.LAG_CLASS_NAMES["CVT"], AP), "offset vs North America (years)"]),
        "ap_delay_cvt_ci": f"{_yrs(offi.loc[(frames.LAG_CLASS_NAMES['CVT'], AP), '95 % low'])} to {_yrs(offi.loc[(frames.LAG_CLASS_NAMES['CVT'], AP), '95 % high'])}",
        # §1.2 active protection, every priority year (method of 2026-10-12)
        "fa_n": str(n_all), "fa_share": pct(float(c["w"]["out"].mean())), "fa_out": str(int(c["w"]["out"].sum())),
        "fa_cvt": pct(fa("CVT")), "fa_slc": pct(fa("SLC")), "fa_tr": pct(fa("TR")), "fa_mr": pct(fa("MR")),
        "fa_p": pval(c["p_all"]), "fa_k": str(c["k_tested"]),
        "fo_us": pct(share_of(wo["pub_office"] == "US")), "fo_else": pct(share_of(wo["pub_office"] != "US")),
        "fo_wo": pct(share_of(wo["pub_office"] == "WO")), "fo_cn": pct(share_of(wo["pub_office"] == "CN")),
        "fo_n_us": str(int((wo["pub_office"] == "US").sum())), "fo_n_else": str(int((wo["pub_office"] != "US").sum())),
        "fo_p": pval(c["p_office"]),
        **{f"fa_c_{k}": pct(float(c["cohort"].loc[w_, "not_protected"])) for k, w_ in COHORT_KEYS.items() if w_ in c["cohort"].index},
        **{f"fa_c_{k}_n": str(int(c["cohort"].loc[w_, "n"])) for k, w_ in COHORT_KEYS.items() if w_ in c["cohort"].index},
    }


#: the priority-year cohorts of the active-protection age read, numbers.json key -> window label
COHORT_KEYS = {"le2011": "<= 2011", "1215": "2012-15", "1619": "2016-19", "2023": "2020-23", "2426": "2024-26 (partial)"}


def _yrs(x) -> str:
    """A signed offset in years as printed: 0, +2, −1, +4.5 (a true minus sign)."""
    return "0" if abs(x) == 0 else f"{x:+.1f}".replace(".0", "").replace("-", "−")
