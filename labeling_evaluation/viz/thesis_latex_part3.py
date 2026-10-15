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
FIGS = {"q6_architecture_shares_by_cohort": (1.0, True), "q7_condition2_balance": (0.9, True), "q7_condition3_cohesion": (0.85, True),
        "q7_condition1_family": (1.0, True), "q6_largest_architectures_over_time": (1.0, False), "q7_iii4_directory_categories": (1.0, False)}
TABLES = {"q7_verdict_table": True, "q7_verdict_detail": True, "q7_condition3_weights": True, "q7_condition3_family": True, "q6_share_trend_spearman": True, "q7_three_year_check": True,
          "q7_granted_live_condition1": True, "q7_granted_live_condition2": True, "q7_iii4_directory_fold": True}
SHOWS = {"q6_architecture_shares_by_cohort": "share of each cohort's designs by architecture", "q7_condition2_balance": "condition 2: ²D against its permutation band, per level",
         "q7_condition3_cohesion": "condition 3: ΔQ against its permutation band, system weighting only", "q7_condition1_family": "condition 1: F's share per priority year, two bases",
         "q6_largest_architectures_over_time": "five largest architectures' share per cohort", "q7_iii4_directory_categories": "III.4: largest directory category per year and its ²D against the band",
         "q7_verdict_table": "verdict per condition and level, all designs (main) and actively protected (sensitivity), each base read alone", "q7_verdict_detail": "the numbers behind the verdict on each base", "q7_condition3_weights": "weights of the form distance: four systems, each weighing 1", "q7_condition3_family": "condition 3 on F: actively protected, all designs, granted and live",
         "q6_share_trend_spearman": "Spearman rho of architecture share on priority year", "q7_three_year_check": "condition 1 with three consecutive years",
         "q7_granted_live_condition1": "F's share per year, granted and live patents", "q7_granted_live_condition2": "²D of F, granted and live patents",
         "q7_iii4_directory_fold": "architectures folded to the directory categories"}


def _item(name):
    return next(i for i in v3.ITEMS if i["name"] == name)


def draw(item, ctx, frac: float):
    """Build ``item`` at width frac × text block; height capped at 55 % of the width; return (figure, data, checks)."""
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
    fm = form[form["weighting"].eq("subsystem")]
    dist = pd.DataFrame({"cohort": [cohort(w) for w in ctx.WIN_NAMES]})
    for lvl, nm in (("A0", "A, A·U and F"), ("A1t", "A·W·T")):
        c = fm[fm["level"].eq(lvl)].set_index("window")["aircraft"]
        dist[f"designs in the form distance, {nm}"] = [int(c.get(w, 0)) for w in ctx.WIN_NAMES]
    dist.insert(1, "designs in III.1 (denominator of the shares)", n_win.to_numpy())
    dist["difference to A"] = dist["designs in III.1 (denominator of the shares)"] - dist["designs in the form distance, A, A·U and F"]
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
         "Balance (²D rarefied to 40, all designs, 200 permutations) with the band, per cohort; 2024–26* is incomplete and not read:\n", tables_md(bal), "",
         "## Verdict table (each base read alone: all designs is the main reading, actively protected the sensitivity)\n", "Source: `q7_verdict_table.csv`.\n", tables_md(ver), "",
         "## The numbers behind the verdict\n", "Source: `q7_verdict_detail.csv`. Condition 1: the largest share of a read year (20 designs or more) and the years met; condition 2: ²D rarefied to 40 and the lower edge of its band; condition 3: ΔQ 2020-23 and the lower edge of its band (200 permutations, seed 42).\n", tables_md(analysis3.verdict_two_bases(ctx)[1]), "",
         "## Weights table (condition 3, the only weighting: the 34 dimensions of the codebook, each of the four systems weighing 1)\n", "Source: `q7_condition3_weights.csv`; 34 dimensions, 625 designs (two designs have no architecture recorded). Per-wing dimensions read the primary wing (codebook R5-03: the largest wing, the forward-most when equal; the role reading pointed to wing 2 in 4 designs, but the author checked their drawings on 2026-10-16 and wing 1 is the largest as drawn in each, so every design reads wing 1); per-boom dimensions boom group 1; propulsor dimensions the set with the most propulsors (first listed on a tie); a dimension that does not apply is blank and left out of the average.\n", tables_md(wts), "",
         "## Condition 3 on F (same weights; Q on the designs of F's base, per cohort)\n", "Source: `q7_condition3_family.csv`. Q uses no architecture, so F on all designs is the same set as A.\n", tables_md(fam), "",
         "## Three-year check (condition 1, three consecutive years, actively protected designs)\n", "Source: `q7_three_year_check.csv`.\n", tables_md(t3), "",
         "## F on granted and live patents alone\n", "Source: `q7_granted_live_condition1.csv`, `q7_granted_live_condition2.csv`.\n", tables_md(gl1), "", tables_md(gl2), "",
         "## III.4, which VT share the figure draws\n",
         "`q7_iii4_directory_categories` draws VT's share per priority YEAR (left panel, condition 1: two actively protected curves, ringed years above 50 %), "
         "and ²D per COHORT against its band (right panel, condition 2, all designs). The per-cohort VT share above is not drawn; it is listed here for the text. "
         "Per-year values: the table 'VT share per priority year' above, also written to `Data_for_writing/csv/q7_iii4_vt_share_per_year.csv`.\n",
         "## Designs per cohort: III.1 against the form distance of condition 3\n", "Source: `q6_architecture_shares_by_cohort.csv` (`designs`), `q7_condition3_cohesion.csv` (`aircraft`, subsystem weighting).\n", tables_md(dist), "",
         "Why they differ: the shares of III.1 divide by every design of the cohort, including the designs with no architecture recorded (a bar segment 'no architecture recorded'), "
         "while the form distance needs an architecture to place a design in a level, so those designs are left out. The two designs without an architecture "
         "(`CN109263914A_ua1`, `CN109263949A_ua1`) have priority year 2018, so only 2016–19 differs (213 against 211). A·W·T drops further designs whose wings or tilt are not recorded.\n",
         "## Numbers quoted by the Results text, III.1 (sub-question B)\n", "Source: `viz/thesis_q6.py` numbers(ctx), notebook cell of the III1 group.\n",
         "\n".join(f"- `{k_}` = {n6[k_]}" for k_ in keys6 if k_ in n6), "",
         "## Numbers quoted by the Results text, III.2 to III.4 (Q7, regions and external comparison left out)\n", "Source: `viz/thesis_q7.py` numbers(ctx), notebook cells of the III2_III3 group.\n",
         "\n".join(f"- `{k_}` = {x}" for k_, x in n7.items()), ""]
    (R / "Data_for_writing" / "NUMBERS_III.md").write_text("\n".join(L), encoding="utf-8")
