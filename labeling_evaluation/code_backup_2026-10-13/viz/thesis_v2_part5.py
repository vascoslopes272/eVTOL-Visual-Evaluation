"""Part V (assignees and regions) figures, v2 layout: the figures of V.1 to V.4 of viz/analysis5.py (the Q2, Q3 and Q7 builders with only the
labels changed) registered as ITEMS for the standard figure notebook (notebook 53), written to thesis_figures_v2/Part_V_assignees_and_regions/.
No analysis is added; nothing is drawn here."""
from __future__ import annotations

from viz import analysis5 as a5

ITEMS = []
for _it in a5.ITEMS:
    _d = dict(_it)
    _d["group"] = a5.FOLDER[_it["section"]]
    _d["role"] = a5.ROLE[_it["slot"]]
    ITEMS.append(_d)


def out_root(cfg):
    return a5.out_root(cfg)


def save_v2_item(item: dict, cfg, ctx):
    """Build, relabel and write one item (PDF, PNG, CSV, JSON); returns (figure or table, data) for the notebook's checks."""
    a5.CURRENT[0] = item["name"]
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
