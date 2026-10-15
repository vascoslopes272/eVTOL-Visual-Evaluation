"""Question 4 of the thesis chapter: do the patented aircraft stand for the aircraft that get built?

Items (THESIS_CONTRACT.md §3, Q4): the coding agreement (Table 2), the class mix per window in the labelled dataset
and in the evtol.news directory (Figure 2 i / ii as two single graphs), the patent clock against the market clock
(Figure 3), the two representativeness tables (Tables 4 and 5); appendix: the dataset against the directory all
years together (Figure 5b i / ii), TRL per class (Table 3) and the name coverage (Figure 5).
Every computation is ported from notebooks/_build/build_40.py (§1.1 Figures 2-3, §1.3); nothing is typed.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from viz import flow, frames, plots, style
from lib import association, intervals

# ------------------------------------------------------------------------------------------ shared frames
#: the colour / hatch each directory class borrows (as build_40 Figure 2) and its printed short code
SPEC5 = {"LC": ("SLC", "L+C"), "VT": ("TR", "VT"), "WM": ("MR", "WM"), "ER": ("RC", "ER"), "HB": ("HB", "HB")}
O5 = ["VT", "LC", "WM", "ER", "HB"]                       # the order of Figure 5b
NAME5 = {"VT": "Vectored Thrust", "LC": "Lift + Cruise", "WM": "Wingless (Multicopter)", "ER": "Electric Rotorcraft",
         "HB": "Hoverbike / Personal Flying Device"}
SRC_PATENT = "patent corpus (unique aircraft, priority year)"
SRC_DIR = "evtol.news directory (aircraft, development year)"
LEGEND5 = {"LC": "Lift + Cruise", "VT": "Vectored Thrust", "WM": "Wingless (Multicopter)", "ER": "Electric Rotorcraft",
           "HB": "Hoverbike / PFV"}                        # the legend of the half-width class-mix graphs
WIN_LABEL = {"<= 2011": "≤2011", "2012-15": "2012–15", "2016-19": "2016–19", "2020-23": "2020–23"}
RENAME_CLASS = {"Tilt Rotor": "Tilt Propulsor"}


def _cache(ctx, key, build):
    store = ctx.__dict__.setdefault("_q4", {})
    if key not in store:
        store[key] = build()
    return store[key]


def class_mix(ctx, in_domain: bool = True) -> pd.DataFrame:
    """Figure 2's long table: aircraft and share per source, window and directory class (build_40 `class_mix`).
    2026-10-15: the directory side is the pages inside the technological domain (``in_domain``); False = all pages (the earlier build)."""
    def build():
        L = frames.evtolnews_long(ctx.v, ctx.cfg, ctx.WIN, in_domain_only=in_domain)
        names = {"patent": SRC_PATENT, "directory": SRC_DIR}
        rows = []
        for src in ("patent", "directory"):
            for w in ctx.WIN_NAMES:
                sw = L[(L["source"] == src) & (L["window"] == w)]
                for c in frames.CLASS5_ORDER:
                    k = int((sw["class5"] == c).sum())
                    rows.append({"source": names[src], "window": w, "class": frames.CLASS5_NAMES[c], "code": c,
                                 "aircraft": k, "window total": len(sw),
                                 "share": round(k / len(sw), 3) if len(sw) else np.nan})
        return pd.DataFrame(rows)
    return _cache(ctx, f"mix{in_domain}", build)


def ari_timeline(ctx) -> pd.DataFrame:
    return _cache(ctx, "tl", lambda: frames.ari_timeline(ctx.v, ctx.cfg))


def public_frame(ctx) -> pd.DataFrame:
    return _cache(ctx, "pub", lambda: frames.public_arch_frame(ctx.ds))


def pairwise(ctx) -> pd.DataFrame:
    """Table 2: three sources of a class two at a time, Wilson interval with the finite-population correction."""
    def build():
        pub = public_frame(ctx)
        m = pub["match"].astype(str)
        gt = pub["arch_gt"].fillna("").astype(str)
        has_gt = gt.ne("")
        agree = {"drawing label against the public aircraft": (int(m.isin(["yes", "taxonomy"]).sum()), len(pub)),
                 "patent text against the public aircraft": (int(m.isin(["yes", "taxonomy", "image"]).sum()), len(pub)),
                 "drawing label against the patent text": (int((gt.eq(pub["topType"].astype(str)) & has_gt).sum()), int(has_gt.sum()))}
        why = ["the patent describes another configuration than the one the firm built, or the drawing was misread",
               "the patent describes another configuration than the one the firm built",
               "the drawing was read as one class and the text states another"]
        rows = []
        for (name, (k, n)), w in zip(agree.items(), why):
            lo, hi = intervals.wilson_fpc_interval(k, n, len(ctx.v))
            rows.append({"comparison": name, "agree": k, "of": n, "share": round(k / n, 2),
                         "95 % interval": f"{lo:.2f}–{hi:.2f}", "the disagreements": w})
        return pd.DataFrame(rows)
    return _cache(ctx, "pairwise", build)


def name_coverage(ctx) -> pd.DataFrame:
    """Figure 5's table: real product names against generated identifiers, and what a name buys."""
    def build():
        v = ctx.v
        pub = public_frame(ctx)
        named = v["name_is_real"].fillna(False).astype(bool)
        linked = frames.linked_aircraft_ids(v, ctx.cfg)
        compared = set(pub["aircraft_id"])

        def row(label, mask):
            return {"aircraft": label, "unique aircraft": int(mask.sum()), "share of the analysis set": round(float(mask.mean()), 3),
                    "linked to an evtol.news page": int(v.loc[mask, "aircraft_id"].isin(linked).sum()),
                    "compared with the public aircraft": int(v.loc[mask, "aircraft_id"].isin(compared).sum()),
                    "filed by a named organisation": int(v.loc[mask, "named"].sum())}
        return pd.DataFrame([row("carry a real product name", named), row("carry a generated identifier", ~named),
                             row("all unique aircraft", named | ~named)])
    return _cache(ctx, "coverage", build)


def trl_table(ctx) -> pd.DataFrame:
    """Table 3: NASA TRL band per class, classes by size, a Total row."""
    def build():
        t = frames.trl_frame(ctx.ds)
        t["class"] = t["topType"].map(lambda c: style.cls(c).name if pd.notna(c) else "no type")
        bands = [b for b, _ in frames.TRL_BANDS]
        trl = pd.crosstab(t["class"], t["band"]).reindex(columns=bands, fill_value=0)
        trl = trl.loc[trl.sum(axis=1).sort_values(ascending=False, kind="stable").index]
        trl.insert(0, "unique aircraft", trl.sum(axis=1))
        trl["above TRL 2"] = trl["unique aircraft"] - trl["TRL 2"]
        trl.loc["Total"] = trl.sum()
        trl["share above TRL 2"] = (trl["above TRL 2"] / trl["unique aircraft"]).round(2)
        trl = trl.reset_index().rename(columns={"index": "class", "band": "class"})
        trl.columns.name = None
        return trl
    return _cache(ctx, "trl", build)


def representativeness(ctx) -> dict:
    """Tables 4 and 5 (full level tables and the printed six-row versions) and the two subset sizes."""
    def build():
        v = ctx.v
        tid = frames.trl_frame(ctx.ds)[["aircraft_id", "trl"]]
        wt = v.merge(tid, on="aircraft_id", how="left")
        above = pd.to_numeric(wt["trl"], errors="coerce").fillna(2).gt(2)
        rep_trl = frames.representativeness(wt, above, "above TRL 2", ctx.WIN_NAMES)
        firms = set(frames.ari_firms(v, ctx.cfg)["company"])
        in_ari = v["company_canonical"].isin(firms)
        rep_ari = frames.representativeness(v.copy(), in_ari, "index firms", ctx.WIN_NAMES)
        verdict = {"matches the rest": "no difference detected", "does NOT match the rest": "differs"}
        # 2026-10-12, new definition of "flown" (author): FLOWN = TRL 5 or more (5 sub-scale flight, 6 any other flight,
        # 7 piloted flight, 8 certification); FLOWN index-firm designs = designs of the index firms whose first flight, as the
        # index states it, is on or before the snapshot (the index prints years only: earliest year <= 2025; a 2026 year in
        # the May 2026 release is read as a plan, as in the market-clock figure). Everyone else is "the rest".
        flown = pd.to_numeric(wt["trl"], errors="coerce").fillna(2).ge(5)
        rep_flown = frames.representativeness(wt, flown, "flown", ctx.WIN_NAMES)
        tl = frames.ari_timeline(v, ctx.cfg)
        ff = pd.to_numeric(tl["first flight (ARI)"], errors="coerce")
        flown_firms = set(tl.loc[ff.notna() & ff.le(frames.ARI_RELEASE_YEAR - 1), "company"])
        in_fari = v["company_canonical"].isin(flown_firms)
        rep_fari = frames.representativeness(v.copy(), in_fari, "flown", ctx.WIN_NAMES)
        names = {"folded class": "architecture group", "filer type": "assignee type", "priority window": "priority-year cohort",
                 "propulsive units": "propulsor units"}

        def printed(rep, label):
            s = rep[rep["test"] != ""].copy()
            return pd.DataFrame({"attribute": s["attribute"].replace(names), f"n {label}": s[f"n {label}"].astype(int),
                                 "n rest": s["n rest"].astype(int), "largest gap": s["largest gap"].str.replace("<= ", "≤", regex=False), "test": s["test"],
                                 "p": s["p"].map(lambda p: "< 0.001" if p < 0.001 else (f"{p:.3f}" if p < 0.1 else f"{p:.2f}")),
                                 "verdict": s["verdict"].map(verdict)}).reset_index(drop=True)
        return {"trl": rep_trl, "ari": rep_ari, "flown": rep_flown, "fari": rep_fari,
                "tab4": printed(rep_flown, "flown"), "tab5": printed(rep_fari, "flown"),
                "n_above": int(above.sum()), "n_ari": int(in_ari.sum()), "n_firms": len(firms),
                "n_flown": int(flown.sum()), "n_fari": int(in_fari.sum()), "n_fari_firms": len(flown_firms), "fari_firms": sorted(flown_firms)}
    return _cache(ctx, "rep", build)


def directory_mix(ctx, in_domain: bool = True) -> dict:
    """§1.3.5: the dataset against the directory all years together, the parts of the directory and the tests.
    2026-10-15: the directory is the pages inside the technological domain (electric, crewed: ``directory_frame()['in_domain']``) and
    the parts are subsets of those pages; ``in_domain=False`` is the earlier build (all pages, plus the in-domain part)."""
    def build():
        v = ctx.v
        dirf = frames.directory_frame(ctx.cfg)
        if in_domain:
            dirf = dirf[dirf["in_domain"]].reset_index(drop=True)
        n_set = v["class5"].value_counts().reindex(O5, fill_value=0)
        n_dir = dirf["class5"].value_counts().reindex(O5, fill_value=0)
        ct = np.vstack([n_set.to_numpy(), n_dir.to_numpy()])
        test = association.chi2_test(ct)
        resid = association.adjusted_residuals(ct)[0]
        subsets = {"labelled dataset (patented aircraft)": None,
                   "directory: in-domain pages" if in_domain else "directory: all pages": pd.Series(True, index=dirf.index)}
        if not in_domain:
            subsets["(a) in domain: electric, crewed"] = dirf["in_domain"]
        subsets.update({
            "(b) concept designs": dirf["status_group"].eq("concept design"),
            "(b) flying hardware": dirf["status_group"].eq("flying hardware"),
            "(d) linked to a patent of this dataset": dirf["patented"],
            "(d) not linked to a patent": ~dirf["patented"],
        })
        counts = {name: (n_set if m is None else dirf.loc[m, "class5"].value_counts().reindex(O5, fill_value=0))
                  for name, m in subsets.items()}
        rows = []
        for name, k in counts.items():
            row = {"source": name, "n": int(k.sum())}
            for c in O5:
                row[c] = round(k[c] / k.sum(), 3)
            if name != "labelled dataset (patented aircraft)":
                t = association.chi2_test(np.vstack([n_set.to_numpy(), k.to_numpy()]))
                row["chi-square vs dataset"], row["p vs dataset"] = round(t["chi2"], 1), ctx.pval(t["p"])
            rows.append(row)
        why = pd.DataFrame(rows)
        return {"n_set": n_set, "n_dir": n_dir, "test": test, "resid": resid, "counts": counts, "why": why}
    return _cache(ctx, f"dir{in_domain}", build)


def directory_keys(ctx, in_domain: bool = True) -> dict:
    """The numbers of the I.2 class-mix text that depend on which directory pages are used (2026-10-15), for one reading of the directory."""
    d, mix = directory_mix(ctx, in_domain), class_mix(ctx, in_domain)
    why = d["why"].set_index("source")
    dirrow = "directory: in-domain pages" if in_domain else "directory: all pages"
    res = d["resid"]
    closest = d["why"].dropna(subset=["chi-square vs dataset"])
    closest = closest[closest["source"] != dirrow] if in_domain else closest
    closest = closest.sort_values("chi-square vs dataset").iloc[0]
    out = {"dir_pages": ctx.thin(d["n_dir"].sum()), "mix_chi2": f"{d['test']['chi2']:.1f}", "mix_p": ctx.pval(d["test"]["p"]),
           "closest_subset": str(closest["source"]), "closest_chi2": f"{closest['chi-square vs dataset']:.1f}",
           "closest_p": str(closest["p vs dataset"]), "closest_n": ctx.thin(closest["n"]),
           "resid_low_class": NAME5[O5[int(np.argmin(res))]].split(" (")[0], "resid_low": minus(f"{res.min():.1f}"),
           "resid_high_class": NAME5[O5[int(np.argmax(res))]], "resid_high": f"+{res.max():.1f}",
           "wm_dir": ctx.pct(why.loc[dirrow, "WM"]), "wm_flying": ctx.pct(why.loc["(b) flying hardware", "WM"]),
           "wm_linked": ctx.pct(why.loc["(d) linked to a patent of this dataset", "WM"]),
           # "directory: in-domain pages" is itself the in-domain part, so the old "(a) in domain" share is now the directory's own
           "wm_domain": ctx.pct(why.loc[dirrow if in_domain else "(a) in domain: electric, crewed", "WM"])}
    for i, code in enumerate(O5):
        out[f"resid {code}"] = minus(f"{res[i]:+.1f}")
    return out


# ------------------------------------------------------------------------------------------ builders
def tab_coding_agreement(ctx):
    return pairwise(ctx), None


def _class_mix_figure(ctx, src: str):
    mix = class_mix(ctx)
    s = mix[(mix["source"] == src) & mix["window"].isin(ctx.COMPLETE)]
    share = s.pivot(index="window", columns="code", values="share").reindex(index=ctx.COMPLETE, columns=frames.CLASS5_ORDER)
    total = s.groupby("window")["window total"].first().reindex(ctx.COMPLETE)
    fig, ax = plt.subplots(figsize=(ctx.HALF, 3.3), constrained_layout=True)
    plots.folded_bars(ax, share.rename(index=WIN_LABEL), SPEC5, totals=[int(x) for x in total])
    ax.set_ylabel("share of the window's aircraft")
    handles = ax.get_legend_handles_labels()[0]
    fig.legend(handles, [f"{SPEC5[c][1]}  {LEGEND5[c]}" for c in frames.CLASS5_ORDER], loc="outside lower center",
               ncol=2, handlelength=1.2, columnspacing=1.0, fontsize=mpl.rcParams["legend.fontsize"] - 0.5)
    return fig, s.reset_index(drop=True)


def fig_class_mix_dataset(ctx):
    return _class_mix_figure(ctx, SRC_PATENT)


def fig_class_mix_directory(ctx):
    return _class_mix_figure(ctx, SRC_DIR)


def fig_patent_vs_market_clock(ctx):
    tl = ari_timeline(ctx)
    fig, ax = plt.subplots(figsize=(ctx.W, 3.9), constrained_layout=True)
    plots.clock_rows(ax, tl, today=2026.45, planned_after=frames.ARI_RELEASE_YEAR - 1)
    ax.set_xlim(2012, 2031)
    ax.text(2026.5, len(tl) - 0.7, "mid-2026", fontsize=7, color=style.MUTED)
    plots.clock_legend(fig, loc="outside lower center", ncol=3)
    return fig, tl


def tab_trl_representativeness(ctx):
    return representativeness(ctx)["tab4"], None


def tab_index_firm_representativeness(ctx):
    return representativeness(ctx)["tab5"], None


def fig_dataset_vs_directory_classes(ctx):
    d = directory_mix(ctx)
    n_set, n_dir = d["n_set"], d["n_dir"]
    fig, ax = plt.subplots(figsize=(ctx.W, 3.1), constrained_layout=True)
    x = np.arange(len(O5))
    bw = 0.38
    small = mpl.rcParams["xtick.labelsize"] - 1
    for i, c in enumerate(O5):
        s = style.cls(SPEC5[c][0])
        for j, (k, n, face, hatch) in enumerate([(n_set[c], n_set.sum(), s.color, s.hatch), (n_dir[c], n_dir.sum(), "white", "")]):
            xx = x[i] + (j - 0.5) * bw
            ax.bar(xx, k, bw * 0.92, color=face, hatch=hatch, edgecolor=s.color if j else "white", linewidth=1.0 if j else 0.5)
            lo, hi = intervals.wilson_interval(k, n)
            ax.plot([xx, xx], [lo * n, hi * n], color=style.INK, linewidth=0.8)
            ax.text(xx, hi * n + 6, f"{ctx.thin(k)}\n({k / n:.0%})".replace("%", " %"), ha="center", va="bottom", fontsize=small)
    ax.set_xticks(x, [f"{c}\n{NAME5[c].split(' (')[0].split(' /')[0]}" for c in O5])
    ax.set_ylim(0, max(n_set.max(), n_dir.max()) * 1.55)
    ax.set_ylabel("unique aircraft")
    ax.legend(handles=[Patch(facecolor=style.INK, label=f"labelled dataset ({ctx.thin(n_set.sum())} aircraft; filled)"),
                       Patch(facecolor="white", edgecolor=style.INK, label=f"evtol.news directory ({ctx.thin(n_dir.sum())} pages; outline)")],
              loc="upper right")
    data = pd.DataFrame({"class": [NAME5[c] for c in O5], "code": O5, "labelled dataset": n_set.to_numpy(),
                         "evtol.news directory": n_dir.to_numpy(), "adjusted residual": d["resid"].round(1)})
    return fig, data


def fig_dataset_vs_directory_subsets(ctx):
    d = directory_mix(ctx)
    counts, n_set = d["counts"], d["n_set"]
    order = list(counts)
    ylab = ["dataset", "directory, in domain", "(b) concept", "(b) flying", "(d) patented", "(d) not patented"]
    fig, axes = plt.subplots(1, len(O5), figsize=(ctx.W, 2.7), constrained_layout=True)
    for i, (c, a) in enumerate(zip(O5, axes)):
        s = style.cls(SPEC5[c][0])
        for r, name in enumerate(order):
            k = counts[name]
            lo, hi = intervals.wilson_interval(k[c], k.sum())
            y = len(order) - 1 - r
            own = name == order[0]
            a.plot([lo * k.sum(), hi * k.sum()], [y, y], color=style.MUTED, linewidth=1)
            a.plot(k[c], y, marker=s.marker, markersize=5, linestyle="none", color=s.color if own else "white",
                   markeredgecolor=s.color if own else style.INK, markeredgewidth=0.8)
            a.annotate(ctx.thin(k[c]), (k[c], y), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                       fontsize=mpl.rcParams["xtick.labelsize"] - 2, color=style.INK, clip_on=False)
        a.axvline(n_set[c], color=s.color, linewidth=0.8, linestyle=":", zorder=0)   # behind the count labels
        a.set_yticks(range(len(order)), ylab[::-1] if i == 0 else [""] * len(order))
        top = max(max(k[c], intervals.wilson_interval(k[c], k.sum())[1] * k.sum()) for k in counts.values())
        a.set_xlim(-top * 0.06, top * 1.15)                 # room for the count printed over a near-zero marker
        a.set_ylim(-0.6, len(order) - 0.3)
        a.set_title(c, fontsize=mpl.rcParams["font.size"])
        a.tick_params(axis="x", labelsize=mpl.rcParams["xtick.labelsize"] - 1)
        a.xaxis.set_major_locator(mpl.ticker.MaxNLocator(3, integer=True))
    fig.supxlabel("unique aircraft of the class in each source (95 % Wilson interval); dotted line: the labelled dataset",
                  fontsize=mpl.rcParams["xtick.labelsize"])
    return fig, d["why"]


def tab_trl_by_class(ctx):
    return trl_table(ctx), None


def fig_name_coverage(ctx):
    cr = name_coverage(ctx).set_index("aircraft")
    real, gen = cr.loc["carry a real product name"], cr.loc["carry a generated identifier"]
    m_ = [int(real["compared with the public aircraft"]), int(gen["compared with the public aircraft"])]
    u_ = [int(real["unique aircraft"]) - m_[0], int(gen["unique aircraft"]) - m_[1]]
    fig, ax = plt.subplots(figsize=(ctx.W, 1.9), constrained_layout=True)
    plots.split_hbars(ax, [f"Real product name ({int(real['unique aircraft'])})", f"Generated identifier ({int(gen['unique aircraft'])})"],
                      m_, u_, "matched to a public product", "not matched")
    ax.set_xlabel("unique aircraft")
    ax.legend(loc="upper right")
    return fig, name_coverage(ctx)


# ------------------------------------------------------------------------------------------ items
SRC_LABEL = "human labelling · evtol.news directory (Vertical Flight Society), crawled 2026-09-17 · PatSeer"
VERIFY_NOTE = ("author re-verifies these values and the evtol.news class mapping; the folded-class row differs from the "
               "45-page document by the SRW to Lift + Cruise ruling of 2026-10-01")

def fig_method_flow(ctx):
    """How Q4 is answered: data -> steps -> tests -> figures -> answer (THESIS_CONTRACT.md §5)."""
    nodes = [
        dict(id="data", kind="data", col=0, text="Unique aircraft\nevtol.news, TRL"),
        dict(id="match", kind="step", col=1, text="Match named aircraft\nto public product"),
        dict(id="fold", kind="step", col=1, text="Fold to five classes\nper year window"),
        dict(id="test", kind="test", col=2, text="Wilson interval\nchi-square, Mann-Whitney"),
        dict(id="figA", kind="figure", col=3, text="Three sources\nof a class"),
        dict(id="figB", kind="figure", col=3, text="Class mix per window\nAircraft against the rest"),
        dict(id="ans", kind="answer", col=4, text="Answer Q4\ncoding and mix"),
    ]
    edges = [("data", "match"), ("data", "fold"), ("match", "test"), ("fold", "test"),
             ("test", "figA"), ("test", "figB"), ("figA", "ans"), ("figB", "ans")]
    return flow.chart(ctx.cfg, nodes, edges), None


ITEMS = [
    dict(name="q4_method_flow", slot="method", kind="figure", sub="",
         title="How Q4 is answered",
         caption="How Q4 is answered.",
         source_item="new", flag=None, flag_note="", builder=fig_method_flow,
         source="this document", unit="", read=""),
    dict(name="q4_coding_agreement", slot="results", kind="table", sub="A",
         title="Three sources of a class, two at a time",
         caption="Agreement on the architecture class between the drawing label, the patent text and the public aircraft, "
                 "on the aircraft with a public counterpart; 95 % Wilson interval with the finite-population correction.",
         source_item="Table 2", flag=None, flag_note="", builder=tab_coding_agreement,
         source="human labelling (drawing label) · whole-patent reading · evtol.news (public aircraft, matched by name)",
         unit="unique aircraft with a public counterpart", read=""),
    dict(name="q4_class_mix_dataset", slot="results", kind="figure", sub="B",
         title="Class mix per window, labelled dataset",
         caption="The class mix of the labelled dataset per priority-year window, folded to the five classes of the "
                 "evtol.news directory; the aircraft of each window under its bar.",
         source_item="Figure 2 (i)", flag=None, flag_note="", builder=fig_class_mix_dataset,
         source="PatSeer · human labelling, folded to the five classes of the directory (analysis.class_fold)",
         unit="unique aircraft by priority-year window; share of the window",
         read="Each bar is 100 % of one window; segments print their share in percent (segments under 8 % carry no number). "
              "L+C = Lift + Cruise (with Stopped/Slowed Rotor Wing since 2026-10-01), VT = every tilting class and Deflected "
              "Slipstream, WM = Multirotor, ER = Rotorcraft, HB = Hoverbike and Personal Flying Vehicle. The partial window is not drawn."),
    dict(name="q4_class_mix_directory", slot="results", kind="figure", sub="B",
         title="Class mix per window, evtol.news directory",
         caption="The evtol.news directory's own class mix per development-year window, on the same axis and class "
                 "order as the labelled dataset; the aircraft of each window under its bar.",
         source_item="Figure 2 (ii)", flag=None, flag_note="", builder=fig_class_mix_directory,
         source="evtol.news directory (Vertical Flight Society), crawled 2026-09-17, development year read by two readers",
         unit="directory aircraft by development-year window; share of the window",
         read="Each bar is 100 % of one window; segments print their share in percent. Same class fold and window bounds as "
              "the labelled dataset; the directory is not filtered to the dataset's domain."),
    dict(name="q4_patent_vs_market_clock", slot="results", kind="figure", sub="B",
         title="The patent clock against the market clock",
         caption="The AAM Reality Index firms that file in this corpus, one row each: first to last priority year, the peak "
                 "filing year, and the first flight and entry into service the index states.",
         source_item="Figure 3", flag="decide", flag_note="main text or appendix", builder=fig_patent_vs_market_clock,
         source="AAM Reality Index (May 2026 release; first_flight and eis as the index prints them) · PatSeer · human labelling",
         unit="index firms that file here, one row each; priority years and index years; the number after a firm is its unique aircraft",
         read="Bar: first to last priority year in this corpus; tick: the year the firm filed most. Square: first flight; "
              "triangle: entry into service; an open marker is a plan (after the index release of 2026). The gap from first "
              "patent to first flight is a floor, since an earlier filing may lie outside this corpus."),
    dict(name="q4_flown_representativeness", slot="results", kind="table", sub="B",
         title="Flown designs against the rest",
         caption="The flown designs (NASA TRL 5 or more: a sub-scale, full-scale, piloted or certified flight) against the rest "
                 "of the patent dataset on six attributes, one test per attribute: chi-square for a category, Mann-Whitney for a number.",
         source_item="Table 4", flag="verify", flag_note=VERIFY_NOTE, builder=tab_trl_representativeness,
         source="NASA TRL per design (rule-based script on the evtol.news pages, the author's reading where reviewed) · human labelling · PatSeer", unit="designs", read=""),
    dict(name="q4_flown_index_firm_representativeness", slot="results", kind="table", sub="B",
         title="Flown index-firm designs against the rest",
         caption="The designs of the AAM Reality Index firms whose first flight, as the index states it, is before the snapshot, "
                 "against the rest of the patent dataset on six attributes, one test per attribute.",
         source_item="Table 5", flag="verify", flag_note=VERIFY_NOTE, builder=tab_index_firm_representativeness,
         source="AAM Reality Index (first_flight as the index prints it; years only, a 2026 year read as a plan) · human labelling · PatSeer", unit="designs", read=""),
    dict(name="q4_dataset_vs_directory_classes", slot="appendix", kind="figure", sub="B",
         title="Dataset against directory, all years",
         caption="Unique aircraft per directory class in the labelled dataset (filled) and in the evtol.news directory "
                 "(outline), all years together, with the share of each source and its 95 % Wilson interval.",
         source_item="Figure 5b (i)", flag=None, flag_note="", builder=fig_dataset_vs_directory_classes,
         source="human labelling, folded by analysis.class_fold · evtol.news directory, 1 229 aircraft pages crawled 2026-09-17",
         unit="unique aircraft (dataset) and aircraft pages (directory); share of the source in brackets",
         read="Whisker: 95 % Wilson interval of the count; the sources differ in size, so compare the shares in brackets. "
              "Two aircraft with no architecture class are left out, so the dataset counts 625 of its 627."),
    dict(name="q4_dataset_vs_directory_subsets", slot="appendix", kind="figure", sub="B",
         title="Aircraft of each class per part of the directory",
         caption="For each directory class, the aircraft in the labelled dataset and in five parts of the directory that "
                 "could explain a different mix: in domain, concept designs, flying hardware, linked to a patent or not.",
         source_item="Figure 5b (ii)", flag=None, flag_note="", builder=fig_dataset_vs_directory_subsets,
         source="evtol.news directory pages (class, status, power source, capacity, piloting) · patent_links.csv · human labelling",
         unit="unique aircraft of the class in each source",
         read="One panel per class; each row a source: the dataset (filled marker, dotted line) and parts of the directory "
              "(open markers), with the 95 % Wilson interval. The parts differ in size, so read the shares in the csv."),
    dict(name="q4_trl_by_class", slot="appendix", kind="table", sub="B",
         title="NASA TRL per class",
         caption="Technology readiness (NASA TRL) reached by the unique aircraft, per architecture class; an aircraft no "
                 "public source follows is TRL 2 by construction.",
         source_item="Table 3", flag="drop", flag_note="kept in the appendix; proposed to be dropped", builder=tab_trl_by_class,
         source="NASA TRL per aircraft (inputs/trl/aircraft_trl.csv; evtol.news, evtolindex.org, company statements) · human labelling",
         unit="unique aircraft per class and TRL band", read=""),
    dict(name="q4_name_coverage", slot="appendix", kind="figure", sub="B",
         title="Unique aircraft by name and public match",
         caption="Unique aircraft that carry a real product name or an identifier generated for this study, and within "
                 "each the aircraft matched to a public product.",
         source_item="Figure 5", flag="drop", flag_note="kept in the appendix; proposed to be dropped", builder=fig_name_coverage,
         source="human labelling (aircraft names, NAME_DECISIONS) · evtol.news (public aircraft)",
         unit="unique aircraft, counts",
         read="Dark hatched segment: matched to a public product and compared with it; light: the rest. Only a named aircraft could be matched."),
]


# ------------------------------------------------------------------------------------------ numbers
def minus(s: str) -> str:
    """A negative number as printed: plain unicode minus, never a hyphen-minus (THESIS_CONTRACT.md §1)."""
    return str(s).replace("-", "−")


def numbers(ctx) -> dict:
    """Every number the Q4 text quotes, as printed."""
    thin, pct, pval = ctx.thin, ctx.pct, ctx.pval
    v = ctx.v
    pw = pairwise(ctx).set_index("comparison")
    cov = name_coverage(ctx).set_index("aircraft")
    trl = trl_table(ctx).set_index("class")
    rep = representativeness(ctx)
    d = directory_mix(ctx)
    mix = class_mix(ctx)
    tl = ari_timeline(ctx)

    def share(src, win, code):
        s = mix[(mix["source"] == src) & (mix["window"] == win) & (mix["code"] == code)]
        return float(s["share"].iloc[0])
    first, last = ctx.COMPLETE[0], ctx.COMPLETE[-1]

    def p_of(tab, attr):
        return tab.set_index("attribute").loc[attr, "p"]
    tab4, tab5 = rep["tab4"], rep["tab5"]
    flown = tl[tl["first flight (ARI)"] <= frames.ARI_RELEASE_YEAR]
    gap = flown["years to first flight"]
    eis = tl["years to entry into service"].dropna()
    resid = d["resid"]
    why = d["why"].set_index("source")
    img_pub, txt_pub, img_txt = (pw.loc["drawing label against the public aircraft"],
                                 pw.loc["patent text against the public aircraft"],
                                 pw.loc["drawing label against the patent text"])
    return {
        **directory_keys(ctx, True),                  # 2026-10-15: mix_p, residuals, closest part, directory share of WM, pages: the in-domain directory
        "unique": thin(len(v)),
        "nc_named": str(int(cov.loc["carry a real product name", "unique aircraft"])),
        "nc_gen": str(int(cov.loc["carry a generated identifier", "unique aircraft"])),
        "nc_gen_matched": str(int(cov.loc["carry a generated identifier", "compared with the public aircraft"])),
        "pw_img_pub": str(int(img_pub["agree"])), "pw_n": str(int(img_pub["of"])), "pw_share": pct(img_pub["share"]),
        "pw_ci": img_pub["95 % interval"],
        "pw_txt_pub": str(int(txt_pub["agree"])), "pw_txt_pub_share": pct(txt_pub["share"]),
        "pw_img_txt": str(int(img_txt["agree"])), "pw_img_txt_share": pct(img_txt["share"]),
        "lc_ds_first": pct(share(SRC_PATENT, first, "LC")), "lc_ds_last": pct(share(SRC_PATENT, last, "LC")),
        "lc_dir_first": pct(share(SRC_DIR, first, "LC")), "lc_dir_last": pct(share(SRC_DIR, last, "LC")),
        "wm_dir_last": pct(share(SRC_DIR, last, "WM")), "wm_ds_last": f"{100 * share(SRC_PATENT, last, 'WM'):.1f} %",
        "hb_dir_first": pct(share(SRC_DIR, first, "HB")), "hb_ds_first": f"{100 * share(SRC_PATENT, first, 'HB'):.1f} %",
        "wm_set": pct(why.loc["labelled dataset (patented aircraft)", "WM"]),
        "ff_flown": str(len(flown)), "ff_before": str(int((gap > 0).sum())), "ff_after": str(int((gap <= 0).sum())),
        "ff_lead": f"{gap[gap > 0].median():.0f}", "eis_lead": f"{eis.median():.0f}", "ari_timeline_n": str(len(tl)),
        "trl_n": str(rep["n_above"]), "trl_rest": thin(len(v) - rep["n_above"]),
        "trl_share": pct(float(trl.loc["Total", "share above TRL 2"])),
        "trl_lc": str(int(trl.loc["Lift + Cruise", "above TRL 2"])), "trl_tp": str(int(trl.loc["Tilt Propulsor", "above TRL 2"])),
        "trl_mr_share": pct(float(trl.loc["Multirotor", "share above TRL 2"])),
        "flown_n": str(rep["n_flown"]), "flown_rest": thin(len(v) - rep["n_flown"]),
        "flown_class_p": p_of(tab4, "architecture group"), "flown_region_p": p_of(tab4, "applicant region"),
        "flown_window_p": p_of(tab4, "priority-year cohort"), "flown_filer_p": p_of(tab4, "assignee type"),
        "flown_year_p": p_of(tab4, "priority year"), "flown_units_p": p_of(tab4, "propulsor units"),
        "flown_differs": str(int((tab4["verdict"] == "differs").sum())),
        "ari_n": str(rep["n_ari"]), "ari_rest": thin(len(v) - rep["n_ari"]), "ari_firms_n": str(rep["n_firms"]),
        "fari_n": str(rep["n_fari"]), "fari_rest": thin(len(v) - rep["n_fari"]), "fari_firms_n": str(rep["n_fari_firms"]),
        "fari_class_p": p_of(tab5, "architecture group"), "fari_region_p": p_of(tab5, "applicant region"),
        "fari_window_p": p_of(tab5, "priority-year cohort"), "fari_filer_p": p_of(tab5, "assignee type"),
        "fari_year_p": p_of(tab5, "priority year"), "fari_units_p": p_of(tab5, "propulsor units"),
        "fari_differs": str(int((tab5["verdict"] == "differs").sum())),
        "fari_region_gap": tab5.set_index("attribute").loc["applicant region", "largest gap"],
        "fari_class_gap": tab5.set_index("attribute").loc["architecture group", "largest gap"],
    }
