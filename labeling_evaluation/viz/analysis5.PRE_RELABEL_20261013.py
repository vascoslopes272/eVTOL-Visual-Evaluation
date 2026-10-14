"""Analysis V in one place: the figures of V.1 (who files), V.2 (new and returning assignees), V.3 (what each region files and when it
enters) and V.4 (the regions and the tilting family F), re-exported from the existing builders of viz/thesis_q2.py, thesis_q3.py and
thesis_q7.py with only the labels changed, to thesis_figures_v2/Part_V_assignees_and_regions/ under the same file names as before. No analysis is added.

    python3 -m viz.analysis5          # every figure and the numbers for the text
Notebook: notebooks/analysis5_figures.ipynb (built by notebooks/_build/build_analysis5.py).

Labels follow the dissertation: assignee, cohort, architecture, configuration (never filer, firm, window, class).
"""
from __future__ import annotations

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator
from matplotlib.text import Text

from viz import config, frames, thesis
from viz import thesis_q2 as q2
from viz import thesis_q3 as q3
from viz import thesis_q7 as q7

# ---------------------------------------------------------------------------------------------- the label layer
_MAP = [(r"Architecture class", "Architecture"), (r"architecture class", "architecture"),
        (r"\bnamed organisations\b", "named assignees"), (r"\bnamed organisation\b", "named assignee"),
        (r"\borganisations\b", "assignees"), (r"\borganisation\b", "assignee"),
        (r"\bfilers\b", "assignees"), (r"\bFilers\b", "Assignees"), (r"\bfiler\b", "assignee"), (r"\bFiler\b", "Assignee"),
        (r"\bfirms\b", "assignees"), (r"\bFirms\b", "Assignees"), (r"\bfirm\b", "assignee"), (r"\bFirm\b", "Assignee"),
        (r"\bwindows\b", "cohorts"), (r"\bWindows\b", "Cohorts"), (r"\bwindow\b", "cohort"), (r"\bWindow\b", "Cohort"),
        (r"\bclasses\b", "architectures"), (r"\bClasses\b", "Architectures"), (r"\bclass\b", "architecture"), (r"\bClass\b", "Architecture"),
        (r"Tilt Rotor", "Tilt Propulsor")]


def relabel(s):
    if not isinstance(s, str):
        return s
    for a, b in _MAP:
        s = re.sub(a, b, s)
    return s


def relabel_fig(fig):
    """Every text of the figure through the label layer (tick labels fixed by the builder are set again, since a draw would restore them)."""
    fig.canvas.draw()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_locator(), FixedLocator):
                old = [t.get_text() for t in axis.get_ticklabels()]
                new = [relabel(t) for t in old]
                if new != old:
                    fs = axis.get_ticklabels()[0].get_fontsize()
                    axis.set_ticklabels(new, fontsize=fs)
    for t in fig.findobj(Text):
        if t.get_text():
            t.set_text(relabel(t.get_text()))
    return fig


def relabel_df(df):
    if df is None:
        return None
    df = df.copy()
    df.columns = [relabel(c) if isinstance(c, str) else c for c in df.columns]
    for c in ("architecture", "group", "variable"):         # category words inside the data, never the assignee names
        if c in df.columns:
            df[c] = df[c].map(relabel)
    return df


# ---------------------------------------------------------------------------------------------- the items
def _largest_assignees_share(ctx):
    """q2_largest_filers_share without the hollow AAM Reality Index diamonds and their legend (nothing else changes)."""
    fig, data = q2.fig_largest_filers_share(ctx)
    for ax in fig.axes:
        for ln in list(ax.lines):
            if ln.get_marker() == "D":
                ln.remove()
        if ax.get_legend() is not None:
            ax.get_legend().remove()
    return fig, data.drop(columns=["rated by the index"])


_SECTIONS = [("V1", "V.1 Who files",
              "Who are the assignees, and how much of the field do the largest hold?",
              [("q2_filer_types", None), ("q2_largest_filers_share", _largest_assignees_share), ("q2_largest_filer_per_class", None)]),
             ("V2", "V.2 New and returning assignees",
              "Does the pool of assignees renew itself, and do the new ones file different architectures?",
              [("q2_first_vs_returning_filers", None), ("q2_entrant_class_mix", None), ("q2_tilt_wing_entrants", None)]),
             ("V3", "V.3 What each region files, and when it enters",
              "Do the regions file different designs, and do they enter each architecture at different times?",
              [("q3_region_design_all_years", None), ("q3_region_mix_by_window_class", None), ("q3_region_mix_by_window_units", None),
               ("q3_region_mix_by_window_tilting", None), ("q3_region_entry_lag", None), ("q3_region_countries", None)]),
             ("V4", "V.4 The regions and the tilting family F",
              "Does the share of F, or the tilting lean, differ between the regions?",
              [("q7_region_family_share", None), ("q7_region_lean_without_largest_filer", None)])]
_ALL = {it["name"]: it for m in (q2, q3, q7) for it in m.ITEMS}
ITEMS = []
for _sec, _title, _q, _names in _SECTIONS:
    for _n, _b in _names:
        _it = dict(_ALL[_n])
        if _b is not None:
            _it["builder"] = _b
        for k in ("title", "caption", "read", "unit", "source_item"):
            _it[k] = relabel(_it[k])
        _it["section"] = _sec
        ITEMS.append(_it)


FOLDER = {"V1": "V1_who_files", "V2": "V2_new_and_returning_assignees", "V3": "V3_regions_what_and_when", "V4": "V4_regions_and_family_F"}
ROLE = {"results": "main", "appendix": "appendix"}


def out_root(cfg):
    """thesis_figures_v2/Part_V_assignees_and_regions/, beside the folders of the other parts."""
    return cfg.out("thesis_figures").parent / "thesis_figures_v2" / "Part_V_assignees_and_regions"


def save_item(it, obj, data, cfg):
    """<out_root>/<section>/<main|appendix>/<name>.{pdf,png,csv,json}; returns the PDF (figure) or CSV (table) path."""
    import json
    out = out_root(cfg) / FOLDER[it["section"]] / ROLE[it["slot"]]
    out.mkdir(parents=True, exist_ok=True)
    name = it["name"]
    meta = {k: it[k] for k in ("name", "section", "slot", "kind", "title", "caption", "source_item", "source", "unit", "read")}
    if it["kind"] == "figure":
        for ext in ("pdf", "png"):
            obj.savefig(out / f"{name}.{ext}")
        if data is not None:
            data.to_csv(out / f"{name}.csv", index=False)
        meta.update(width_in=round(obj.get_figwidth(), 3), height_in=round(obj.get_figheight(), 3))
        main = out / f"{name}.pdf"
    else:
        obj.to_csv(out / f"{name}.csv", index=False)
        main = out / f"{name}.csv"
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    return main


def build_item(name: str, cfg, ctx):
    """Build one item, relabel it, write it (PDF, PNG, CSV, JSON) to its folder of today, close the figure; return (path, data)."""
    it = next(i for i in ITEMS if i["name"] == name)
    obj, data = it["builder"](ctx)
    if it["kind"] == "figure":
        relabel_fig(obj)
    else:
        obj = relabel_df(obj)
    data = relabel_df(data)
    path = save_item(it, obj, data, cfg)
    if it["kind"] == "figure":
        plt.close(obj)
    return path, (obj if it["kind"] == "table" else data)


def key_numbers(df, n: int = 14) -> str:
    """The numbers behind a figure: its data frame, rounded, at most ``n`` rows."""
    if df is None:
        return ""
    t = df.head(n).copy()
    for c in t.columns:
        if t[c].dtype.kind == "f":
            t[c] = t[c].round(3)
    return t.to_string(index=False, max_colwidth=46) + (f"\n… {len(df)} rows in the CSV" if len(df) > n else "")


# ---------------------------------------------------------------------------------------------- numbers for the text
def numbers_for_text(ctx) -> dict:
    v = ctx.v
    out = {}
    # 1. regional shares
    f3 = q3._frames(ctx)
    groups = [("all years", v)] + [(w, v[v["window"] == w]) for w in ctx.WIN_NAMES if w != "<= 2011"]
    rows = []
    for lab, s in groups:
        n = len(s)
        sh = {r: float((s["region3"] == r).mean()) for r in frames.REGIONS}
        rows.append({"cohort": relabel(lab), "designs": n, **{r: f"{100 * x:.1f} %" for r, x in sh.items()},
                     "others": f"{100 * float((s['region3'] == 'Other regions').mean()):.1f} %",
                     "sum of the three": f"{100 * sum(sh.values()):.1f} %"})
    out["shares"] = pd.DataFrame(rows)
    # 2. entry-lag intervals
    def lag(off, label):
        t = off[off["region"] != frames.REGIONS[0]].copy()
        t["interval"] = [f"{lo:+.1f} to {hi:+.1f}" if np.isfinite(lo) else "none (all-architecture row)" for lo, hi in zip(t["95 % low"], t["95 % high"])]
        t["touches or includes 0"] = [("YES" if lo <= 0 <= hi else "no") if np.isfinite(lo) else "–" for lo, hi in zip(t["95 % low"], t["95 % high"])]
        t = t.drop(columns=["priority years"], errors="ignore")
        t.insert(0, "priority years", label)
        t["class"] = [relabel(c) for c in t["class"]]
        return t.rename(columns={"class": "architecture"})[["priority years", "architecture", "region", "aircraft", "offset vs North America (years)", "interval", "touches or includes 0"]]
    last = ctx.cfg.analysis["last_complete_year"]
    out["lag"] = pd.concat([lag(f3["off"], f"all years to {last}"), lag(f3["off16"], f"2016 to {last}")], ignore_index=True)
    # 3. entrants
    fw = q2._frames(ctx)["fw"]
    out["entrants"] = relabel_df(fw[["window", "named firms active", "new firms", "continuing firms"]]).rename(
        columns={"cohort": "cohort", "named assignees active": "assignees active", "new assignees": "entrants", "continuing assignees": "incumbents"})
    out["entrant_rule"] = ("An entrant is an assignee whose earliest cohort in the dataset is this cohort: the cohort of its first design "
                           "(by the priority year of the design's representative patent), not of its first patent. The assignee of a design is the "
                           "FIRST assignee of its representative patent's PatSeer string (co-assignees after ';' are ignored), resolved to a "
                           "canonical name by the grouper where it has one, else read from the string; not the assignee with the most patents. "
                           "Individual inventors are not assignees here (they are not counted as entrants).")
    # 4. NA tilting without the largest assignee
    d7 = q7._data(ctx)
    big = d7["ts"].attrs["left_out"]
    na = d7["ln"].set_index("region").loc[frames.REGIONS[0]]
    out["na_tilt"] = {"largest assignee left out": big, "NA tilting share, all": float(na["tilting share"]),
                      "NA tilting share without it": float(na["tilting share without it"]),
                      "chi-square p without it": q7._tp(d7, "any tilting unit", "all years", f"without {big}"),
                      "chi-square p, all assignees": q7._tp(d7, "any tilting unit", "all years")}
    return out


def print_numbers(n: dict) -> None:
    print("1. Share of designs per region (all aircraft of the cohort in the denominator)\n" + n["shares"].to_string(index=False))
    print("\n2. Entry lag, median priority-year offset from North America, 95 % bootstrap interval\n" + n["lag"].to_string(index=False))
    print("\n3. " + n["entrant_rule"] + "\n" + n["entrants"].to_string(index=False))
    t = n["na_tilt"]
    print(f"\n4. North America, tilting share without {t['largest assignee left out']}: {100 * t['NA tilting share without it']:.1f} % "
          f"(all assignees {100 * t['NA tilting share, all']:.1f} %); chi-square p {q7.pval5(t['chi-square p without it'])} "
          f"(with all assignees p {q7.pval5(t['chi-square p, all assignees'])})")


def run():
    cfg = config.load(strict=False)
    ctx = thesis.context(cfg)
    for it in ITEMS:
        path, data = build_item(it["name"], cfg, ctx)
        print(f"\n[{it['section']}] {it['name']} -> {path}\n{key_numbers(data)}")
    print_numbers(numbers_for_text(ctx))


if __name__ == "__main__":
    run()
