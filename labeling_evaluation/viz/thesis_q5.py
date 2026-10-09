"""Q5 — Does the money follow the patents, in time and in design? (thesis chapter 4, part "Patents against the
built and funded sector").

Items (one graph per file, see THESIS_CONTRACT.md §3 Q5):
  A Timing                       appendix  q5_ari_timeline            Table 1            flag=decide
  B Funding vs filing and output results   q5_funding_vs_aircraft     Figure 18 (i)
                                 appendix  q5_patent_lead_to_flight   Figure 18 (ii)     flag=verify
  C Concentration of funding     appendix  q5_patenting_vs_investment new (sector_funding) flag=decide

The computations are ported from notebooks/_build/build_40.py (Table 1, "1.1 numbers", external comparison) and
build_43.py (Figure 18, "4.1 numbers"); the frames come from viz.frames (ari_timeline, ari_funding_frame,
ari_funding_tests, ari_f_funding, publication_lag, filings_per_year).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from viz import flow, frames, plots, style

#: short firm names for the dot labels of Figure 18 (as build_43 prints them)
ARI_SHORT = {"Ascendance Flight Technologies": "Ascendance", "Wofei / Geely Aviation": "Wofei / Geely", "Embraer / Eve": "Eve",
             "Beta Technologies": "Beta", "Vertical Aerospace": "Vertical", "Wollant Aviation": "Wollant",
             "Archer Aviation": "Archer", "Joby Aviation": "Joby"}
#: the periods of the sector_funding input and the priority years each one covers (a year is counted once)
FUND_PERIODS = {"2010-2020": (2010, 2020), "2021": (2021, 2021), "2023": (2023, 2023), "2024 (to August)": (2024, 2024)}
FUND_SHORT = {"2010-2020": "2010–20", "2021": "2021", "2023": "2023", "2024 (to August)": "2024*"}


# ------------------------------------------------------------------------------------------------- helpers
def _pct1(x: float) -> str:
    return f"{100 * x:.1f} %"


def _pval(p: float) -> str:
    """The form the document prints: 3 decimals below the line, 2 above, '< 0.001' when tiny (build_43)."""
    return "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.05 else f"{p:.2f}"


def timeline(ctx) -> pd.DataFrame:
    return frames.ari_timeline(ctx.v, ctx.cfg)


def funding(ctx) -> tuple:
    fund = frames.ari_funding_frame(ctx.v, ctx.cfg)
    return fund, frames.ari_funding_tests(fund)


def investment_by_period(ctx) -> pd.DataFrame:
    """One row per period of the sector_funding input: disclosed funding (US$ bn, and per year), unique aircraft and
    representative patents of the priority years it covers (totals and per year), and whether every year is complete."""
    fund = pd.read_csv(ctx.cfg.path("sector_funding"))
    fpy = frames.filings_per_year(ctx.ds, ctx.v, ctx.cfg)
    rows = []
    for _, r in fund.iterrows():
        lo, hi = FUND_PERIODS[r["period"]]
        yrs = fpy.loc[lo:hi]
        n = hi - lo + 1
        rows.append({"period": r["period"], "years": n, "funding US$ bn": float(r["funding_usd_bn"]),
                     "funding US$ bn per year": float(r["funding_usd_bn"]) / n,
                     "unique aircraft": int(yrs["unique aircraft"].sum()),
                     "unique aircraft per year": float(yrs["unique aircraft"].sum()) / n,
                     "representative patents": int(yrs["patents representative"].sum()),
                     "representative patents per year": float(yrs["patents representative"].sum()) / n,
                     "complete": bool(yrs["complete"].all()), "scope": r["scope"], "source": r["source"]})
    return pd.DataFrame(rows)


def level_year(fpy: pd.DataFrame, lo: int = 2006, hi: int = 2023, band: float = 0.8) -> int:
    """The first complete priority year at which unique aircraft reached their level: the first year within ``band`` of the
    highest complete year's count (80 % of the 2021 peak keeps 2018-2021 and leaves 2017 out)."""
    y = fpy.loc[lo:hi]
    y = y[y["complete"]]["unique aircraft"]
    return int(y[y >= band * y.max()].index.min())


def _funding_axes(ax, ylab: str):
    ax.set_xscale("log")
    ax.set_xlim(35, 14000)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x_, _p: f"{x_:,.0f}".replace(",", " ")))
    ax.set_xlabel("disclosed funding, US$ M (log)")
    ax.set_ylabel(ylab)
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def _funding_panel(ctx, col: str, ylab: str):
    """One panel of Figure 18: funding (log) against ``col``, Spearman ρ, p and n as the title, labels placed free of each other."""
    fund, tests = funding(ctx)
    d = fund[fund["funding $M"].notna()]
    s = d[["company", "funding $M", col]].dropna()
    fig, ax = plt.subplots(figsize=(ctx.HALF * 1.25, 3.0), constrained_layout=True)
    ax.scatter(s["funding $M"], s[col], s=26, color=style.INK, edgecolor="white", linewidth=0.6, zorder=4)
    _funding_axes(ax, ylab)
    if col.startswith("years"):
        ax.axhline(0, color=style.MUTED, linewidth=0.8, linestyle="--", zorder=2)
        ax.set_ylim(-1.9, 8.2)
    else:
        ax.set_ylim(0.2, 9.3)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    t = tests[tests["column"] == col].iloc[0]
    ax.set_title(f"Spearman ρ {t['rho']:+.2f} · p {t['p']:.3f} · n {int(t['firms'])}".replace("-", "−"), fontsize=7.5, loc="left")
    fig.canvas.draw()
    failed = plots.place_labels(ax, s["funding $M"].to_numpy(), s[col].to_numpy(), [ARI_SHORT.get(c, c) for c in s["company"]],
                                [3.4] * len(s), fontsize=7)
    assert not failed, failed
    return fig, s.reset_index(drop=True)


# ------------------------------------------------------------------------------------------------- builders
def tab_ari_timeline(ctx):
    """Table 1: first patent here, first flight and entry into service as the index states them, and the years between."""
    tl = timeline(ctx)
    t = tl[["company", "first patent", "unique aircraft", "first flight (ARI)", "entry into service (ARI)",
            "years to first flight", "years to entry into service"]].copy()
    t = t.astype(object).where(t.notna(), "")
    for c in ["first flight (ARI)", "entry into service (ARI)", "years to first flight", "years to entry into service"]:
        t[c] = t[c].map(lambda x: f"{x:.0f}" if x != "" else "")
    t = t.rename(columns={"first flight (ARI)": "first flight", "entry into service (ARI)": "entry into service",
                          "unique aircraft": "aircraft"})
    return t, None


def fig_funding_vs_aircraft(ctx):
    """Figure 18 (i): disclosed funding against the firm's unique aircraft in the corpus."""
    return _funding_panel(ctx, "unique aircraft", "unique aircraft in the corpus")


def fig_patent_lead_to_flight(ctx):
    """Figure 18 (ii): disclosed funding against the years from first patent to first flight."""
    return _funding_panel(ctx, "years first patent to first flight", "years, first patent to first flight")


def fig_patenting_vs_investment(ctx):
    """New: unique aircraft per priority year against disclosed sector investment per year, one dot per published period.
    One axis each (no dual axis): the two trackers' scopes differ, so the figure is read by eye and carries no test."""
    inv = investment_by_period(ctx)
    fig, ax = plt.subplots(figsize=(ctx.HALF * 1.25, 3.0), constrained_layout=True)
    for _, r in inv.iterrows():
        ax.scatter(r["funding US$ bn per year"], r["unique aircraft per year"], s=30, zorder=4,
                   color=style.INK if r["complete"] else "white", edgecolor=style.INK, linewidth=0.9)
    ax.set_xscale("log")
    ax.set_xlim(0.2, 12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x_, _p: f"{x_:g}"))
    ax.xaxis.set_major_locator(mticker.FixedLocator([0.25, 0.5, 1, 2, 4, 8]))
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.set_ylim(0, 85)
    ax.set_xlabel("disclosed sector investment, US$ bn per year (log)")
    ax.set_ylabel("unique aircraft per priority year")
    ax.grid(color=style.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.text(0.99, 0.03, "open dot: year still filling (publication lag)\n* January to August, not annualised",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color=style.MUTED)
    fig.canvas.draw()
    failed = plots.place_labels(ax, inv["funding US$ bn per year"].to_numpy(), inv["unique aircraft per year"].to_numpy(),
                                [FUND_SHORT[p] for p in inv["period"]], [3.6] * len(inv), fontsize=7)
    assert not failed, failed
    return fig, inv


def fig_method_flow(ctx):
    """Methodology flowchart: from the index firms to the Q5 figures and the answer."""
    nodes = [
        dict(id="data", kind="data", col=0, text="AAM Reality Index\nfirms filing here"),
        dict(id="lead", kind="step", col=1, text="First patent to\nfirst flight, less lag"),
        dict(id="fund", kind="step", col=1, text="Funding per firm,\ntwo-firm share"),
        dict(id="test", kind="test", col=2, text="Spearman ρ, funding\nvs aircraft, year, lead"),
        dict(id="figA", kind="figure", col=3, text="Patent clock against\nmarket clock"),
        dict(id="figB", kind="figure", col=3, text="Funding against\naircraft filed"),
        dict(id="ans", kind="answer", col=4, text="Money follows\nin time, not output"),
    ]
    edges = [("data", "lead"), ("data", "fund"), ("lead", "figA"), ("lead", "test"), ("fund", "test"),
             ("test", "figB"), ("figA", "ans"), ("figB", "ans")]
    fig = flow.chart(ctx.cfg, nodes, edges)
    _trim_arrows(fig, nodes, edges)
    return fig, None


def _trim_arrows(fig, nodes, edges):
    """Shorten every arrow to the edge of its boxes along its own (curved) path, and draw it above the boxes.

    viz.flow draws arc3 curves with one fixed shrink; a curve that bends into a box keeps its head under the box.
    FancyArrowPatch clips the path where it leaves a circle of radius shrink (points) round each end, so the shrink
    is the straight distance from the end to the point where the curve leaves the box, plus a small gap.
    """
    from matplotlib.patches import FancyArrowPatch
    ax = fig.axes[0]
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    boxes = {}
    for t in ax.texts:
        bb = t.get_bbox_patch().get_window_extent(rend)
        boxes[t.get_text()] = bb
    text_of = {n["id"]: n["text"] for n in nodes}
    arrows = [a for a in ax.patches if isinstance(a, FancyArrowPatch)]
    pt = 72.0 / fig.dpi                                   # pixels -> points
    gap = 2.5                                             # px between the box edge and the arrow tip / tail

    def curve(a):
        pa = ax.transData.transform(a._posA_posB[0])
        pb = ax.transData.transform(a._posA_posB[1])
        path = a.get_connectionstyle()(pa, pb, shrinkA=0.0, shrinkB=0.0)
        v = path.vertices
        s = np.linspace(0.0, 1.0, 400)[:, None]
        if len(v) == 3:                                   # quadratic bezier (arc3)
            pts = (1 - s) ** 2 * v[0] + 2 * (1 - s) * s * v[1] + s ** 2 * v[2]
        else:                                             # straight line
            pts = (1 - s) * v[0] + s * v[-1]
        return pts

    def exit_shrink(pts, bb, from_end):
        """Distance from one end of the curve to where it leaves box bb (box padded by `gap`)."""
        seq = pts[::-1] if from_end else pts
        inside = ((seq[:, 0] >= bb.x0 - gap) & (seq[:, 0] <= bb.x1 + gap)
                  & (seq[:, 1] >= bb.y0 - gap) & (seq[:, 1] <= bb.y1 + gap))
        k = int(np.argmin(inside)) if not inside.all() else len(seq) - 1
        return float(np.hypot(*(seq[k] - seq[0]))) * pt

    for a, e in zip(arrows, edges):
        pts = curve(a)
        a.shrinkA = exit_shrink(pts, boxes[text_of[e[0]]], from_end=False)
        a.shrinkB = exit_shrink(pts, boxes[text_of[e[1]]], from_end=True)
        a.set_zorder(5)                                   # above the boxes: the head is never hidden


# ------------------------------------------------------------------------------------------------- items
ITEMS = [
    dict(name="q5_method_flow", slot="method", kind="figure", sub="",
         title="How Q5 is answered",
         caption="How Q5 is answered.",
         source_item="new", flag=None, flag_note="",
         builder=fig_method_flow,
         source="this chapter", unit="the step", read="left to right: data, transform, test, figures, answer"),
    dict(name="q5_ari_timeline", slot="appendix", kind="table", sub="A",
         title="Patent clock against market clock",
         caption="The index firms that file in this corpus: first patent here, first flight and entry into service as the AAM Reality Index "
                 "states them, and the years between. A negative value means the firm flew before its first filing in this corpus.",
         source_item="Table 1", flag="decide",
         flag_note="appendix as proposed, or main text beside the Timing paragraph; the lead is a floor (first patent IN THIS CORPUS)",
         builder=tab_ari_timeline,
         source="AAM Reality Index (May 2026 release: first_flight and eis fields, kept verbatim) · PatSeer · human labelling",
         unit="the firm: the index firms of the May 2026 release that file in this corpus, one row each, sorted by first patent",
         read="first flight and entry into service are the index's own statements, not flight records; a year after 2026 is a plan"),
    dict(name="q5_funding_vs_aircraft", slot="results", kind="figure", sub="B",
         title="Funding against aircraft filed",
         caption="Disclosed funding of the AAM Reality Index firms against their unique aircraft in the corpus, one dot per firm, "
                 "with the Spearman ρ, its p and the number of firms.",
         source_item="Figure 18 (i)", flag=None, flag_note="",
         builder=fig_funding_vs_aircraft,
         source="AAM Reality Index (May 2026 release: disclosed funding) · PatSeer (priority date) · human labelling",
         unit="the firm: the index firms with a disclosed funding amount (US$ million)",
         read="horizontal: funding on a log scale; vertical: the firm's unique aircraft; ρ +1 when more funding always goes with "
              "more aircraft, 0 when unrelated; on so few firms only a strong relation can be detected"),
    dict(name="q5_patent_lead_to_flight", slot="appendix", kind="figure", sub="B",
         title="Funding against patent-to-flight lead",
         caption="Disclosed funding of the AAM Reality Index firms against the years from their first patent in this corpus to their "
                 "first flight, one dot per firm whose first flight has happened.",
         source_item="Figure 18 (ii)", flag="verify",
         flag_note="check caption/image: the 45-page document showed no caption or image for this panel",
         builder=fig_patent_lead_to_flight,
         source="AAM Reality Index (May 2026 release: disclosed funding, first flight) · PatSeer (priority date) · human labelling",
         unit="the firm: the index firms with a disclosed amount whose first flight is dated no later than the release year (2026)",
         read="below the dashed line the first flight precedes the firm's first patent in this corpus, which only means its earliest "
              "filing is not here; ρ, p and n above the graph as in the results figure"),
    dict(name="q5_patenting_vs_investment", slot="appendix", kind="figure", sub="C",
         title="Patenting against sector investment",
         caption="Unique aircraft per priority year against the disclosed eVTOL investment per year, one dot per published "
                 "funding period. An open dot is a period whose priority years are still filling.",
         source_item="new", flag="decide",
         flag_note="new figure from the sector_funding input; the two trackers differ in scope (VFS: eVTOL companies, cumulative "
                   "2010-2020; McKinsey: future air mobility, single years), so it is a comparison by eye, never a test",
         builder=fig_patenting_vs_investment,
         source="Vertical Flight Society (2010-2020, cumulative) · McKinsey Center for Future Mobility via Urban Air Mobility News "
                "(2021, 2023, 2024 to August) · PatSeer · human labelling",
         unit="the period: four published funding figures, each divided by the years it covers; aircraft are the unique aircraft "
              "whose first priority year falls in the period, per year",
         read="a dot to the right has more money per year, a dot higher more aircraft per year; the 2010-2020 dot averages "
              "eleven years that include the 2016 take-off, so it sits low on both axes; the 2024 money covers January to August only "
              "and is not annualised"),
]


# ------------------------------------------------------------------------------------------------- numbers
def numbers(ctx) -> dict:
    """Every number the Q5 text quotes, as printed (build_40 '1.1 numbers' and build_43 '4.1 numbers')."""
    thin, pct = ctx.thin, ctx.pct
    tl = timeline(ctx)
    flown = tl[tl["first flight (ARI)"] <= frames.ARI_RELEASE_YEAR]
    gap = flown["years to first flight"]
    lead = gap[gap > 0].median()
    planned = tl[tl["first flight (ARI)"] > frames.ARI_RELEASE_YEAR]
    eis = tl["years to entry into service"].dropna()
    lag = frames.publication_lag(ctx.ds, by="region").set_index("region").loc[frames.REGIONS]
    lag_p90 = int(lag["90th percentile"].max())
    fund, tests = funding(ctx)
    tt = tests.set_index("column")
    d = fund[fund["funding $M"].notna()]
    best = d.sort_values("funding $M").iloc[-1]
    disc = fund["funding status"].eq("disclosed")
    ext = frames.ari_f_funding(ctx.ds, ctx.v, ctx.cfg)
    firms_ext = ext[ext["kind"] == "firm"]
    top2 = firms_ext.nlargest(2, "funding $M")
    inv = investment_by_period(ctx).set_index("period")
    fpy = frames.filings_per_year(ctx.ds, ctx.v, ctx.cfg)
    peak_year = int(fpy.loc[2006:2023, "unique aircraft"].idxmax())
    fund_peak = inv["funding US$ bn per year"].idxmax()
    return {
        # A Timing
        "ari_timeline_n": str(len(tl)), "ff_record_n": str(len(flown)), "ff_before_n": str(int((gap > 0).sum())),
        "ff_after_n": str(int((gap <= 0).sum())), "ff_plan_n": str(len(planned)),
        "ff_lead": f"{lead:.0f}", "lag_p90": str(lag_p90), "ff_visible": f"{lead - lag_p90:.0f}",
        "ff_lead_min": f"{gap[gap > 0].min():.0f}", "ff_lead_max": f"{gap[gap > 0].max():.0f}",
        "eis_n": str(len(eis)), "eis_lead": f"{eis.median():.0f}",
        # B Funding vs filing and output
        "ari_firms_n": str(len(fund)), "ari_air_n": str(int(fund["unique aircraft"].sum())),
        "ari_air_share": pct(fund["unique aircraft"].sum() / len(ctx.v)),
        "fund_disc_n": str(int(disc.sum())), "fund_corp_n": str(int(fund["funding status"].str.startswith("corporate").sum())),
        "fund_hist_n": str(int(fund["funding status"].str.startswith("not in").sum())),
        "rho_air": f"{tt.loc['unique aircraft', 'rho']:+.2f}".replace("-", "−"), "p_air": _pval(tt.loc["unique aircraft", "p"]),
        "n_air": str(int(tt.loc["unique aircraft", "firms"])),
        "rho_lead": f"{tt.loc['years first patent to first flight', 'rho']:+.2f}".replace("-", "−"),
        "p_lead": _pval(tt.loc["years first patent to first flight", "p"]),
        "n_lead": str(int(tt.loc["years first patent to first flight", "firms"])),
        "rho_fp": f"{tt.loc['first patent', 'rho']:+.2f}".replace("-", "−"), "p_fp": _pval(tt.loc["first patent", "p"]),
        "n_fp": str(int(tt.loc["first patent", "firms"])),
        "best_firm": best["company"], "best_fund_musd": thin(best["funding $M"]), "best_first_patent": str(int(best["first patent"])),
        "best_air": str(int(best["unique aircraft"])),
        "fund_air_min": str(int(d["unique aircraft"].min())), "fund_air_max": str(int(d["unique aircraft"].max())),
        # C Concentration of funding
        "top1": top2.iloc[0]["company"], "top2": top2.iloc[1]["company"],
        "top2_fundshare": pct(top2["funding $M"].sum() / firms_ext["funding $M"].sum()),
        "top2_airshare": _pct1(top2["unique aircraft"].sum() / ctx.v["aircraft_id"].nunique()),
        "top2_air_n": str(int(top2["unique aircraft"].sum())),
        "disc_total_busd": f"{firms_ext['funding $M'].sum() / 1000:.1f}",
        "ext_fund_1020": f"{inv.loc['2010-2020', 'funding US$ bn']:.1f}", "ext_fund_2021": f"{inv.loc['2021', 'funding US$ bn']:.1f}",
        "ext_fund_2023": f"{inv.loc['2023', 'funding US$ bn']:.1f}",
        "ext_fund_1020_py": f"{inv.loc['2010-2020', 'funding US$ bn per year']:.1f}",
        "air_2015": str(int(fpy.loc[2015, "unique aircraft"])), "air_2018": str(int(fpy.loc[2018, "unique aircraft"])),
        "air_peak_year": str(peak_year), "air_2021": str(int(fpy.loc[2021, "unique aircraft"])),
        "air_1020_py": f"{inv.loc['2010-2020', 'unique aircraft per year']:.0f}",
        "air_level_year": str(level_year(fpy)), "fund_peak_period": FUND_SHORT[fund_peak],
        "ext_fund_1020_start": str(FUND_PERIODS["2010-2020"][0]), "ext_fund_1020_end": str(FUND_PERIODS["2010-2020"][1]),
    }
