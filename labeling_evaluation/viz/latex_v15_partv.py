"""LaTeX_v15 export of Analysis V (assignees and regions): seven figures remade at their FINAL width in the dissertation (text block 16 cm),
height at most 55 % of the width, text 7 pt or more, the thesis style (viz/part1.mplstyle), labels as in viz/analysis5.py. No number, test or result
changes: every builder is the one of viz/thesis_q2.py, thesis_q3.py or thesis_q7.py; only the figure size is imposed. Writes to LaTeX_v15/:
    Figures/Part_V_assignees_and_regions/<group>/<role>/<name>.pdf, Data_for_writing/csv/<name>.csv, NUMBERS_V.md, MANIFEST.md (appended)
(The module of the other parts is viz/latex_v15.py; this one is separate so the two never overwrite each other.)
Driver: python3 -m viz.latex_v15_partv
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.text import Text

from viz import analysis5 as a5
from viz import config, figcheck, thesis
from viz import thesis_q2 as q2
from viz import thesis_q3 as q3
from viz import thesis_q7 as q7
from viz.thesis_latex_common import MAX_H, TEXT_CM, root as latex_root

CM, MIN_PT = 2.54, 7.0
PNG_PREVIEW = {"q2_filer_types"}                        # figures that also write a .png preview beside the pdf
PART = "Part_V_assignees_and_regions"
FIGS = {
    # flat style since 2026-10-17 (viz/flatstyle.py, thesis_q2.fig_filer_types_flat); 11 / 16 = the 11 cm the author gave, a PNG preview beside the pdf
    "q2_filer_types": (q2.fig_filer_types_flat, 11.0 / TEXT_CM, "V1_who_files", "main", True, "share of each assignee type, all years and per cohort"),
    "q3_region_design_all_years": (q3.fig_region_design_all_years, 1.0, "V3_regions_what_and_when", "main", True,
                                   "architecture, propulsor units and tilting per region, all years"),
    "q7_region_family_share": (q7.fig_region_family_share, 0.7, "V4_regions_and_family_F", "main", True,
                               "share of designs in F per region and cohort, chi-square p under each cohort"),
    "q2_largest_filers_share": (a5._largest_assignees_share, 1.0, "V1_who_files", "main", False,
                                "cumulative share of the designs held by the largest assignees (width not given: 1.0)"),
    "q3_region_entry_lag": (q3.fig_region_entry_lag, 0.72, "V3_regions_what_and_when", "main", False,
                            "years after North America per architecture, median difference with 95 % bootstrap interval (width not given: 0.72, as before)"),
    "q7_region_firm_proximity": (q7.fig_region_firm_proximity, 0.7, "V4_regions_and_family_F", "appendix", False,
                                 "proximity of the assignees' architecture mixes within and across regions (width not given: 0.7, as the 0.5 of before overlapped its labels at 7 pt)"),
    "q3_firm_successions": (q3.fig_firm_successions, 1.0, "V3_regions_what_and_when", "appendix", False,
                            "where an assignee's next design lands, by the architecture of the one before (width not given: 1.0)"),
    "q3_region_mix_by_window_class": (q3.fig_region_mix_by_window_class, 1.0, "V3_regions_what_and_when", "appendix", True,
                                      "architecture mix of each region per cohort, the two strongest 2012-2023 trends above each panel (appendix; added 2026-10-17, width 1.0)"),
}


@contextmanager
def _final_size(width_in: float):
    """Every plt.subplots of the builder is drawn at the final width; its height keeps its proportion, capped at 55 % of the width."""
    orig = plt.subplots

    def sub(*a, **k):
        fs = k.get("figsize")
        if fs:
            k["figsize"] = (width_in, min(fs[1] * width_in / fs[0], MAX_H * width_in))
        return orig(*a, **k)

    plt.subplots = sub
    try:
        yield
    finally:
        plt.subplots = orig


def build(name: str, cfg, ctx):
    builder, frac = FIGS[name][:2]
    a5.CURRENT[0] = name
    with plt.style.context(str(Path(__file__).with_name("part1.mplstyle"))), _final_size(frac * TEXT_CM / CM):
        fig, data = builder(ctx)
        a5.relabel_fig(fig)
        for t in fig.findobj(Text):                       # 7 pt or more at final size
            if t.get_text() and t.get_fontsize() < MIN_PT:
                t.set_fontsize(MIN_PT)
        if name == "q7_region_family_share":              # the y label ran past the shorter axis: two lines, same words
            fig.axes[0].set_ylabel("share of aircraft\nin family F")
        fig.canvas.draw()
    a5.print_log(name)
    a5.CURRENT[0] = None
    return fig, a5.relabel_df(data)


def export_figure(name: str, cfg, ctx) -> dict:
    fig, data = build(name, cfg, ctx)
    _, frac, group, role, used, shows = FIGS[name]
    root = latex_root(cfg)
    pdf = root / "Figures" / PART / group / role / f"{name}.pdf"
    csv = root / "Data_for_writing" / "csv" / f"{name}.csv"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    csv.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf)
    if name in PNG_PREVIEW:
        fig.savefig(pdf.with_suffix(".png"), dpi=300)
    data.to_csv(csv, index=False)
    info = dict(name=name, pdf=pdf, csv=csv, width_cm=round(fig.get_figwidth() * CM, 2), height_cm=round(fig.get_figheight() * CM, 2),
                height_over_width=round(fig.get_figheight() / fig.get_figwidth(), 3), overlaps=figcheck.overlaps(fig),
                smallest_pt=min(t.get_fontsize() for t in fig.findobj(Text) if t.get_text()), used=used, shows=shows)
    plt.close(fig)
    return info


def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join("" if pd.isna(x) else str(x) for x in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


def numbers_md(cfg, ctx) -> str:
    fr = q2._frames(ctx)
    sizes, cov = fr["sizes"], fr["cov"]
    n_air, n_named = len(ctx.v), len(sizes)
    top4 = sizes.iloc[:4]
    one = int((sizes == 1).sum())
    n = a5.numbers_for_text(ctx)
    lag = n["lag"].copy()
    lo_hi = lag["interval"].str.extract(r"([+-][\d.]+) to ([+-][\d.]+)").astype(float)
    lag["excludes zero"] = ["yes" if (a > 0 or b < 0) else ("no" if not pd.isna(a) else "no interval") for a, b in zip(lo_hi[0], lo_hi[1])]
    lag["note"] = ["lower bound +0.0 (rounded to 1 decimal)" if str(i).startswith("+0.0 ") else "" for i in lag["interval"]]
    lag = lag.drop(columns=["touches or includes 0"])
    L = ["# NUMBERS_V: Analysis V (assignees and regions)\n",
         "Source tags: `CSV` = Data_for_writing/csv/<name>.csv; `nb53` = notebooks/53_thesis_figures_v2_part5.ipynb (`viz/analysis5.py:numbers_for_text`); "
         "`q2.numbers`, `q3.numbers`, `q7.numbers` = `viz/thesis_q2.py`, `thesis_q3.py`, `thesis_q7.py` numbers(ctx). Every value was recomputed from the frames when this file was written.\n",
         "## (a) The largest assignees\n",
         "Source: `viz.thesis_q2._frames(ctx)['sizes']` and `['cov']` (the data of `q2_largest_filers_share`, CSV `q2_largest_filers_share.csv`).\n",
         f"- The 4 largest assignees ({', '.join(f'{a} {int(b)}' for a, b in top4.items())} designs) hold {int(top4.sum())} designs: "
         f"{100 * top4.sum() / n_air:.1f} % of the {n_air} designs and {100 * top4.sum() / sizes.sum():.1f} % of the {int(sizes.sum())} designs of named assignees.",
         f"- Named assignees: {n_named} (\"named organisations\"); together {int(sizes.sum())} designs, {100 * sizes.sum() / n_air:.1f} % of the {n_air}; individual inventors hold the rest ({n_air - int(sizes.sum())} designs).",
         f"- Assignees with exactly one design: {one} of {n_named} ({100 * one / n_named:.1f} %), {one} designs ({100 * one / n_air:.1f} % of all designs).",
         "- Bands:\n", _md_table(cov.rename(columns=a5.relabel)), "",
         "## (b) Entry lag: Europe and Asia-Pacific against North America\n",
         "Source: `viz.thesis_q3._frames(ctx)['off']` (all years to the last complete year) and `['off16']` (priority years 2016 onward); CSV `q3_region_entry_lag.csv` holds the five drawn architectures. "
         "Offset = median priority year of the region minus North America's; positive = later. Interval = 95 % bootstrap, 2000 draws, seed 42 (`lib/regional.py`), rounded to 1 decimal. "
         "'Excludes zero' means the rounded interval is entirely above or below 0; a rounded bound of +0.0 is marked.\n",
         _md_table(lag), "",
         "**Check of your expectation.** Over all years only Asia-Pacific excludes zero: Lift + Cruise (+1.0 to +4.0), Tilt Propulsor (+1.0 to +4.5), Tilt Wing (+1.0 to +5.0) and Multicopter (+1.5 to +16.0). "
         "Confirmed. No Europe interval excludes zero over all years; Lift + Cruise Europe (+0.0 to +4.0) only touches it. "
         "Combined vectored thrust, Hoverbike and Tilt Frame include zero in both regions (Hoverbike and Tilt Frame have 5 to 8 designs in a region and are not drawn). "
         "**On 2016 onward the picture changes**: only Tilt Wing in Europe excludes zero (+1.0 to +5.0). Lift + Cruise, Tilt Propulsor and Tilt Wing in Asia-Pacific have a lower bound of +0.0, so they touch zero; "
         "Multicopter and combined vectored thrust include it. The all-architectures rows (2016 onward) carry no interval.\n",
         "## Other numbers quoted by the Results text of Analysis V\n",
         "### Region shares of designs (nb53)\n", _md_table(n["shares"]), "",
         "### Entrants and incumbents per cohort (nb53; `viz.thesis_q2._frames(ctx)['fw']`)\n", n["entrant_rule"] + "\n", _md_table(n["entrants"]), "",
         "### North America tilting share without its largest assignee (nb53; `viz.thesis_q7._data(ctx)['ln']`, `['ts']`)\n"]
    t = n["na_tilt"]
    L += [f"- Largest assignee left out: {t['largest assignee left out']}; tilting share {100 * t['NA tilting share, all']:.1f} % with, {100 * t['NA tilting share without it']:.1f} % without; "
          f"chi-square p {q7.pval5(t['chi-square p, all assignees'])} with all assignees, {q7.pval5(t['chi-square p without it'])} without.", ""]
    for title, mod, keep in (("Analysis V.1 and V.2 (`q2.numbers`)", q2, None), ("Analysis V.3 (`q3.numbers`)", q3, None), ("Analysis V.4, regional keys (`q7.numbers`)", q7, ("r_", "px_"))):
        d = {k: v for k, v in mod.numbers(ctx).items() if keep is None or k.startswith(keep)}
        L += [f"### {title}\n", "| key | value |", "|---|---|"] + [f"| `{k}` | {a5.relabel(str(v))} |" for k, v in d.items()] + [""]
        if mod is q2:
            L += tw_fisher_section(ctx)
    return "\n".join(L)


def tw_fisher_section(ctx) -> list:
    """V.2, Tilt Wing among entrants: the three Fisher exact tests behind the text's p values, with their 2x2 counts (author's request, 2026-10-17)."""
    twf = q2._frames(ctx)["twf"]
    twe = q2._frames(ctx)["twe"].set_index("window")
    t = twf[twf["window"].isin(["2016-19", "2020-23"])].rename(columns={"window": "cohort"})
    t1 = t[["cohort", "entrants with Tilt Wing", "other entrants", "Tilt Wing aircraft", "other aircraft", "p against all the window's aircraft"]]
    t2 = t[["cohort", "entrants with Tilt Wing", "other entrants", "other aircraft with Tilt Wing", "other aircraft without", "p against the window's other aircraft"]]
    w16, w20 = twe.loc["2016-19"], twe.loc["2020-23"]
    return ["### V.2, Tilt Wing among entrants: Fisher exact tests per cohort\n",
            "Source: `viz.frames.tw_entry_tests` on `viz.thesis_q2._frames(ctx)['twe']` (`lib.association.fisher_exact_p`, two-sided). "
            "An entrant is a named assignee whose first design (first row after a sort on priority year) falls in the cohort; its first design counts as "
            "Tilt Wing when that design is a Tilt Wing. The cohort's aircraft are every design of the cohort, named or not.\n",
            "**(1) Entrants against all the cohort's aircraft** (keys `tw_fisher_p_1619`, `tw_fisher_p_2023`): 2x2 of (entrants with Tilt Wing, other entrants) x "
            "(Tilt Wing aircraft, other aircraft).\n", _md_table(t1), "",
            "**(2) Entrants against the cohort's other aircraft** (keys `tw_fisher_rest_p_1619`, `tw_fisher_rest_p_2023`): the same rows against the cohort's aircraft "
            "without the entrants' first designs (disjoint sets). These are the \"0.46 and 0.22\" of the Results text.\n", _md_table(t2), "",
            f"**(3) `tw_fisher_p` = {w20['Tilt Wing share, Fisher p against the window before']:.2f}** is a third test, between cohorts and without entrants: "
            f"Tilt Wing's share of the aircraft in 2020-23 ({int(w20['Tilt Wing aircraft'])} of {int(w20['aircraft in the window'])}) against 2016-19 "
            f"({int(w16['Tilt Wing aircraft'])} of {int(w16['aircraft in the window'])}), the test of the fall of the share named in the text.\n"]


def lag_two_decimals(ctx) -> pd.DataFrame:
    """The bootstrap of lib.regional.lag_offsets without the rounding: same frames, classes, seed and draw order, asserted equal after
    rounding to 1 decimal to the existing frames (so no result moves). Offset, low and high with every decimal, all years and 2016 onward."""
    from lib import regional
    from viz import frames
    v = frames.with_publication(ctx.ds, ctx.v)

    def boot(w):
        rng = np.random.default_rng(regional.SEED)
        rows = []
        for cls, sub in w.groupby("class", observed=True):
            ref = sub.loc[sub["region"].eq(regional.REFERENCE_REGION), "year"].to_numpy()
            for reg in regional.REGIONS:
                arr = sub.loc[sub["region"].eq(reg), "year"].to_numpy()
                if not len(arr) or not len(ref):
                    continue
                d = np.array([np.median(rng.choice(arr, len(arr), replace=True)) - np.median(rng.choice(ref, len(ref), replace=True))
                              for _ in range(regional.DRAWS)])
                rows.append({"architecture": cls, "region": reg, "designs": len(arr), "offset": float(np.median(arr) - np.median(ref)),
                             "low": float(np.percentile(d, 2.5)), "high": float(np.percentile(d, 97.5))})
        return pd.DataFrame(rows)

    lf = regional.lag_frame(v, class_names=frames.LAG_CLASS_NAMES)
    since = v[pd.to_numeric(v["year"], errors="coerce").ge(regional.LAG_SINCE)]
    lf16 = regional.lag_frame(since, class_names=frames.LAG_CLASS_NAMES)
    f3 = q3._frames(ctx)
    out = []
    for label, w, ref in (("all years to 2023", lf, f3["off"]), ("2016 to 2023", lf16, f3["off16"])):
        t = boot(w)
        ref = ref[ref["class"] != "all classes"].reset_index(drop=True)
        assert len(t) == len(ref) and (t["low"].round(1).to_numpy() == ref["95 % low"].to_numpy()).all() \
            and (t["high"].round(1).to_numpy() == ref["95 % high"].to_numpy()).all(), "unrounded bootstrap differs from the frame"
        out.append(t.assign(period=label))
    t = pd.concat(out, ignore_index=True)
    t["architecture"] = t["architecture"].map(a5.relabel)
    return t


def append_two_decimals(cfg, ctx) -> str:
    """Append the two-decimal entry-lag section to NUMBERS_V.md (once) and write its CSV."""
    from viz import frames
    t = lag_two_decimals(ctx)
    drawn = {a5.relabel(frames.LAG_CLASS_NAMES[c]) for c in q3._lag_classes(q3._frames(ctx)["off"])}
    t = t[t["region"] != "North America"].copy()
    t["drawn in q3_region_entry_lag"] = t["architecture"].isin(drawn).map({True: "yes", False: "no"})
    t["marker"] = ["lower bound rounds to +0.0" if round(x, 1) == 0 else "" for x in t["low"]]
    t["lower bound above zero"] = ["yes" if x > 0 else "no" for x in t["low"]]
    show = t.assign(offset=t["offset"].map("{:+.2f}".format), low=t["low"].map("{:+.2f}".format), high=t["high"].map("{:+.2f}".format))
    cols = ["architecture", "region", "designs", "offset", "low", "high", "lower bound above zero", "marker"]
    parts = ["\n## Entry lag with two decimals (follow-up)\n",
             "Source: `viz/latex_v15_partv.py:lag_two_decimals`, the bootstrap of `lib/regional.lag_offsets` without the rounding (same frames, same seed 42, same draw order; "
             "2000 draws). Asserted equal, after rounding to 1 decimal, to `viz.thesis_q3._frames(ctx)['off']` and `['off16']`, so no result moves. "
             "Offset = median priority year of the region minus that of North America; lower and upper bound = 2.5 and 97.5 percentiles of the bootstrap offsets; "
             "'lower bound above zero' tests the two-decimal value; the marker flags every lower bound whose 1-decimal value is 0.0. CSV: `q3_region_entry_lag_two_decimals.csv`.\n"]
    for period in ("2016 to 2023", "all years to 2023"):
        for flag, ttl in (("yes", "architectures drawn in `q3_region_entry_lag`"), ("no", "architectures the figure does not draw (fewer than 10 designs in a region)")):
            s = show[(t["period"] == period) & (t["drawn in q3_region_entry_lag"] == flag)]
            if len(s):
                parts += [f"### {period}: {ttl}\n", _md_table(s[cols].rename(columns={"low": "lower bound", "high": "upper bound"})), ""]
    text = "\n".join(parts)
    f = latex_root(cfg) / "Data_for_writing" / "NUMBERS_V.md"
    old = f.read_text(encoding="utf-8")
    if "## Entry lag with two decimals (follow-up)" not in old:
        f.write_text(old.rstrip("\n") + "\n" + text + "\n", encoding="utf-8")
    csv = latex_root(cfg) / "Data_for_writing" / "csv" / "q3_region_entry_lag_two_decimals.csv"
    t.to_csv(csv, index=False)
    mf = latex_root(cfg) / "Data_for_writing" / "MANIFEST.md"
    line = "- `LaTeX_v15/Data_for_writing/csv/q3_region_entry_lag_two_decimals.csv` · no (leaves the text) · entry lag of Europe and Asia-Pacific against North America with two decimals, all years and 2016 onward"
    if line not in mf.read_text(encoding="utf-8"):
        mf.write_text(mf.read_text(encoding="utf-8").rstrip("\n") + "\n" + line + "\n", encoding="utf-8")
    return text


def export_part_v(cfg=None, ctx=None) -> list:
    cfg = cfg or config.load(strict=False)
    ctx = ctx or thesis.context(cfg)
    infos = [export_figure(n, cfg, ctx) for n in FIGS]
    root = latex_root(cfg)
    dfw = root / "Data_for_writing"
    nf = dfw / "NUMBERS_V.md"
    nf.write_text(numbers_md(cfg, ctx), encoding="utf-8")
    append_two_decimals(cfg, ctx)                     # the follow-up section and its CSV, recomputed every run (never carried over)
    yn = lambda u: "yes" if u else "no (leaves the text)"                                           # noqa: E731
    lines = [(f"LaTeX_v15/{i['pdf'].relative_to(root)}", yn(i["used"]), i["shows"]) for i in infos]
    lines += [(f"LaTeX_v15/{i['csv'].relative_to(root)}", yn(i["used"]), f"data behind {i['name']}") for i in infos]
    lines += [("LaTeX_v15/Data_for_writing/NUMBERS_V.md", "yes", "numbers of Analysis V with their sources")]
    mf = dfw / "MANIFEST.md"
    old = mf.read_text(encoding="utf-8") if mf.exists() else "# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n"
    new = [f"- `{a}` · {b} · {c}" for a, b, c in lines if f"`{a}`" not in old]
    if new:
        mf.write_text(old.rstrip("\n") + "\n" + "\n".join(new) + "\n", encoding="utf-8")
    return infos


def export_filer_types_flat(cfg=None, ctx=None) -> dict:
    """The one-figure entry of the flat-style q2_filer_types (author, 2026-10-17): the registry path (build + export_figure, so a full
    Part V export writes the very same files), plus the png path and the font facts for the notebook to print."""
    cfg = cfg or config.load(strict=False)
    ctx = ctx or thesis.context(cfg)
    info = export_figure("q2_filer_types", cfg, ctx)
    info["png"] = info["pdf"].with_suffix(".png")
    fig, _ = build("q2_filer_types", cfg, ctx)
    info["fonts"] = sorted({t.get_fontsize() for t in fig.findobj(Text) if t.get_text()})
    info["font_name"] = next(t for t in fig.findobj(Text) if t.get_text()).get_fontname()
    plt.close(fig)
    return info

if __name__ == "__main__":
    for i in export_part_v():
        print(i["name"], i["width_cm"], "x", i["height_cm"], "cm | h/w", i["height_over_width"], "| smallest", i["smallest_pt"], "pt | overlaps", len(i["overlaps"]))
