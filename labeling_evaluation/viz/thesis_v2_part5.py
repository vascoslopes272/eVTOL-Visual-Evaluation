"""Part V (assignees and regions) figures, v2 layout: the figures of V.1 to V.4 of viz/analysis5.py (the Q2, Q3 and Q7 builders with only the
labels changed) registered as ITEMS for the standard figure notebook (notebook 53), written to thesis_figures_v2/Part_V_assignees_and_regions/.
No analysis is added; nothing is drawn here."""
from __future__ import annotations

import matplotlib as mpl

from viz import analysis5 as a5
from viz import thesis_style_partv as sp

#: the dissertation figures 4.17-4.21 are drawn in the thesis style (notebooks/thesis_style.py) by viz/thesis_style_partv.py, the same
#: builders as the LaTeX_v15 export, so both copies match (2026-10-20); their words are written final, so the label layer is not run on them
RESTYLED = set(sp.BUILDERS)
ITEMS = []
for _it in a5.ITEMS:
    _d = dict(_it)
    _d["group"] = a5.FOLDER[_it["section"]]
    _d["role"] = a5.ROLE[_it["slot"]]
    if _d["name"] in RESTYLED:
        _d["builder"] = sp.BUILDERS[_d["name"]]
    ITEMS.append(_d)


def out_root(cfg):
    return a5.out_root(cfg)


def save_v2_item(item: dict, cfg, ctx):
    """Build, relabel and write one item (PDF, PNG, CSV, JSON); returns (figure or table, data) for the notebook's checks."""
    a5.CURRENT[0] = item["name"]
    if item["name"] in RESTYLED:
        with mpl.rc_context(sp.ts.RC):
            obj, data = item["builder"](ctx)
            data = a5.relabel_df(data)
            sp.ts.save(obj, item["name"], a5.out_root(cfg) / item["group"] / item["role"])    # checks 6.3 in and >= 8 pt
            a5.save_item(item, obj, data, cfg)                                                  # same files + CSV and JSON sidecar
        a5.print_log(item["name"])
        a5.CURRENT[0] = None
        return obj, data
    obj, data = item["builder"](ctx)
    if item["kind"] == "figure":
        a5.relabel_fig(obj)
    else:
        obj = a5.relabel_df(obj)
    data = a5.relabel_df(data)
    a5.save_item(item, obj, data, cfg)
    a5.print_log(item["name"])
    a5.CURRENT[0] = None
    return obj, data
