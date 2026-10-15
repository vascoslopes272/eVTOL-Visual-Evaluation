"""Part II hand-over to the dissertation (notebook 50, last section): the figures of Analysis II redrawn at their final width in the text block
(16 cm), height at most 55 % of the width, text 7 pt or more, thesis style (viz/part1.mplstyle), no title; written to
LaTeX_v15/Figures/Part_II_design_space/<group>/<role>/; the data behind every figure and table in LaTeX_v15/Data_for_writing/csv/; NUMBERS_II.md;
MANIFEST.md (appended). No number, test or result changes: the builders are those of viz/thesis_v2_part2.py, which read viz/thesis_q6.py and
thesis_q7.py unchanged. Levels of description are printed A, A·W·T, A·U."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from viz import figcheck, thesis_q6 as q6, thesis_q7 as q7, thesis_v2_part2 as v2
from viz.thesis_latex_common import MAX_H, TEXT_CM, root, tables_md

#: name -> (final width as a share of the text block, in the dissertation)
FIGS = {"q6_configuration_core": (0.9, True), "q6_discovery_curve": (1.0, True),
        "q6_half_of_cohort": (0.8, False),                 # width not given: 0.8; leaves the text
        "q6_propulsor_units_per_class": (0.8, True)}       # appendix
TABLES = {"q6_selected_fields": True, "q7_levels_of_description": True, "q7_hill_numbers_by_level": True}
SHOWS = {"q6_configuration_core": "configurations by share of the 2016–23 designs and assignees per design; core and rim",
         "q6_discovery_curve": "distinct configurations seen as the designs accumulate, at A, A·W·T and A·U, against random order; 2024–26 not yet all published",
         "q6_half_of_cohort": "cumulative share of each cohort's designs held by its largest A·U configurations; where each crosses 50 %",
         "q6_propulsor_units_per_class": "propulsor units per design, by architecture (appendix)",
         "q6_selected_fields": "dimensions that vary: designs answering, options, top share, most common options",
         "q7_levels_of_description": "the three levels of description A, A·W·T, A·U: configurations, single-design configurations, ¹D, largest configuration",
         "q7_hill_numbers_by_level": "Hill numbers of each level: ⁰D (configurations), ¹D, ²D"}


def _item(name):
    return next(i for i in v2.ITEMS if i["name"] == name)


def tab_hill_numbers_by_level(ctx):
    """⁰D, ¹D and ²D of the three levels of description, from the frame of thesis_q6 (frames.archetype_levels_table), all years."""
    lv = q6._data(ctx)["levels"].set_index("level")
    t = pd.DataFrame({"level": [v2.LEVEL[k] for k in ("A0", "A1t", "A0c")],
                      "designs": [int(lv.loc[k, "aircraft"]) for k in ("A0", "A1t", "A0c")],
                      "⁰D (configurations)": [int(lv.loc[k, "archetypes"]) for k in ("A0", "A1t", "A0c")],
                      "¹D": [round(float(lv.loc[k, "effective number ¹D"]), 1) for k in ("A0", "A1t", "A0c")],
                      "²D": [round(float(lv.loc[k, "effective number ²D"]), 1) for k in ("A0", "A1t", "A0c")]})
    return t


def draw(item, ctx, frac: float):
    """Build ``item`` AT its final size (label placement is done in that size): width frac × text block, height capped at 55 % of the width."""
    w_in = TEXT_CM / 2.54 * frac
    ctx.W, ctx.fig_h = w_in, MAX_H * w_in
    try:
        with plt.style.context(str(Path(v2.__file__).with_name("part1.mplstyle"))):
            fig, data = item["builder"](ctx)
            fig.canvas.draw()
            chk = (len(figcheck.overlaps(fig)), len(figcheck.small_text(fig, 7.0)))
    finally:
        del ctx.fig_h
        ctx.W = 6.3
    return fig, data, chk


def export(cfg, ctx):
    R = root(cfg)
    csvd = R / "Data_for_writing" / "csv"
    csvd.mkdir(parents=True, exist_ok=True)
    manifest, checks = [], []
    for name, (frac, used) in FIGS.items():
        it = _item(name)
        fig, data, chk = draw(it, ctx, frac)
        out = R / "Figures" / "Part_II_design_space" / it["group"] / it["role"]
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / f"{name}.pdf")
        wh = (round(fig.get_figwidth() * 2.54, 2), round(fig.get_figheight() * 2.54, 2))
        plt.close(fig)
        data.to_csv(csvd / f"{name}.csv", index=False)
        checks.append({"figure": name, "width cm": wh[0], "height cm": wh[1], "height / width": round(wh[1] / wh[0], 3),
                       "text over text": chk[0], "under 7 pt": chk[1]})
        manifest.append((f"Figures/Part_II_design_space/{it['group']}/{it['role']}/{name}.pdf", used, SHOWS[name]))
        manifest.append((f"Data_for_writing/csv/{name}.csv", used, "data behind " + name))
    for name, used in TABLES.items():
        t = tab_hill_numbers_by_level(ctx) if name == "q7_hill_numbers_by_level" else _item(name)["builder"](ctx)[0]
        t.to_csv(csvd / f"{name}.csv", index=False)
        manifest.append((f"Data_for_writing/csv/{name}.csv", used, SHOWS[name]))
    est = q6._data(ctx)["est"].reset_index()
    est["level"] = est["level"].map(v2.LEVEL)
    est.to_csv(csvd / "q6_discovery_estimators.csv", index=False)
    manifest.append(("Data_for_writing/csv/q6_discovery_estimators.csv", True, "Chao1, coverage and new configurations in the last 100 designs, per level (complete years)"))
    _numbers(cfg, ctx, R)
    manifest.append(("Data_for_writing/NUMBERS_II.md", True, "numbers of Analysis II with their sources"))
    mf = R / "Data_for_writing" / "MANIFEST.md"
    head = "# MANIFEST\n\nOne line per file: path · used in the dissertation · what it shows.\n\n"
    old = mf.read_text(encoding="utf-8").splitlines() if mf.exists() else head.splitlines()
    mine = {f"`LaTeX_v15/{p}`" for p, _, _ in manifest}
    kept = [ln for ln in old if not any(ln.startswith(f"- {m} ") for m in mine)]          # append, never duplicate: a rerun replaces only its own lines
    kept += [f"- `LaTeX_v15/{p}` · {'yes' if used else 'no (leaves the text)'} · {what}" for p, used, what in manifest]
    mf.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return pd.DataFrame(checks)


def _numbers(cfg, ctx, R: Path):
    d6 = q6._data(ctx)
    z, n_win = d6["zones"], d6["n_win"]
    cohort = lambda w: "2024–26 (incomplete)" if "partial" in w else w.replace("<= ", "≤").replace("-", "–")      # noqa: E731
    rows = []
    for w in ctx.WIN_NAMES:
        c = np.sort(z[w].astype(float).to_numpy())[::-1]
        cs = np.cumsum(c) / c.sum()
        k = int(np.searchsorted(cs, 0.5)) + 1
        k_all = int(np.searchsorted(np.cumsum(z[w].astype(float).to_numpy()) / c.sum(), 0.5)) + 1
        rows.append({"cohort": cohort(w), "designs": int(n_win[w]), "designs in the 33 A·U configurations of five or more": int(c.sum()),
                     "configurations that hold half (ranked by size within the cohort)": k,
                     "same, columns in overall-size order (the old heatmap)": k_all})
    half = pd.DataFrame(rows)
    t6, _ = _item("q6_selected_fields")["builder"](ctx)
    t7, _ = _item("q7_levels_of_description")["builder"](ctx)
    hill = tab_hill_numbers_by_level(ctx)
    est = d6["est"]
    est_t = pd.DataFrame({"level": [v2.LEVEL[k] for k in ("A0", "A1t", "A0c")],
                          "designs (complete years)": [int(est.loc[k, "aircraft"]) for k in ("A0", "A1t", "A0c")],
                          "configurations seen": [int(est.loc[k, "archetypes observed"]) for k in ("A0", "A1t", "A0c")],
                          "Chao1": [round(float(est.loc[k, "Chao1"]), 1) for k in ("A0", "A1t", "A0c")],
                          "new in the last 100 designs": [round(float(est.loc[k, "new in the last 100 aircraft"]), 1) for k in ("A0", "A1t", "A0c")],
                          "new in the last 100, random order": [round(float(est.loc[k, "new in the last 100, random order"]), 1) for k in ("A0", "A1t", "A0c")]})
    import viz.thesis_text_q6 as tx6
    keys6 = sorted(set(re.findall(r"\{([a-z0-9_]+)\}", next(r["text"] for r in tx6.RESULTS if r["sub"] == "A"))))
    n6 = q6.numbers(ctx)
    core = d6["core"]
    L = ["# NUMBERS_II — Analysis II (design space)\n",
         "Written by notebook 50 (`viz/thesis_latex_part2.py`); every value is recomputed when the notebook runs. CSVs are in `Data_for_writing/csv/`. "
         "Levels are A (architecture), A·W·T (architecture, wings, tilt), A·U (architecture, propulsor units); the lowest propulsor-unit band is named 0–3.\n",
         "## Configurations that hold half of each cohort's designs, at A·U (`q6_half_of_cohort`, which leaves the text)\n",
         "Source: `q6_half_of_cohort.csv`. The figure ranks the configurations by size within the cohort (first column); the old heatmap used the overall-size order (second), "
         "which gives 10 for 2016–19 where the text says 10. 2024–26 is incomplete and not read.\n", tables_md(half), "",
         "## Table: dimensions that vary\n", "Source: `q6_selected_fields.csv` (notebook 50, group II1).\n", tables_md(t6), "",
         "## Table: levels of description\n", "Source: `q7_levels_of_description.csv` (notebook 50, group II2). The family F row is in Analysis III.\n", tables_md(t7), "",
         "## Table: Hill numbers of each level\n", "Source: `q7_hill_numbers_by_level.csv`; all years, 627 designs less those the level cannot name.\n", tables_md(hill), "",
         "## Discovery (`q6_discovery_curve`): complete years (to 2023)\n", "Source: `q6_discovery_estimators.csv`; the figure's last-100 window and these numbers are on the complete years.\n", tables_md(est_t), "",
         f"## Core (`q6_configuration_core`)\n\nSource: `q6_configuration_core.csv`. Core: {len(core)} A·U configurations holding {100 * core['share 2016-23'].sum():.1f} % of the 2016–23 designs; "
         f"rim: {len(d6['rim'])} configurations holding {100 * d6['rim']['share 2016-23'].sum():.1f} %. 2024–26 is not drawn.\n",
         "## Numbers quoted by the Results text, Analysis II (sub-question A)\n", "Source: `viz/thesis_q6.py` numbers(ctx), notebook cells of groups II1–II3.\n",
         "\n".join(f"- `{k_}` = {n6[k_]}" for k_ in keys6 if k_ in n6), ""]
    (R / "Data_for_writing" / "NUMBERS_II.md").write_text("\n".join(L), encoding="utf-8")
