"""Follow-up 2026-10-24 to NUMBERS_I section 4 (the lead from the first patent to the first flight): the 90th-percentile publication lag per
region, all priority years against 2016-21 only, and the share of the aircraft of 2022 and 2023 already published at the snapshot. This block
was first patched into NUMBERS_I.md by hand on 2026-10-24 (backup PRE_LAGKEYS_20261024_203710_NUMBERS_I.md); it is now computed here and
inserted at the end of section 4, just before section 5 (a rerun replaces it). Reads ctx only; draws no figure, writes no CSV. Run by
``latex_v15.write_numbers_I`` (notebook 48).

    python -m viz.followup_2026_10_24_lag_keys      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import pandas as pd

from lib import growth as _growth
from viz import frames
from viz.thesis_latex_common import root as latex_root

START = "- Publication lag, 90th percentile in years ("        # the block has no heading of its own: it starts at this bullet
AFTER = "## 5. What each figure plots"                          # and ends just before this heading
KEY = {"North America": "na", "Europe": "eu", "Asia-Pacific": "ap"}


def lag_keys(ctx) -> dict:
    """The 90th-percentile lag (whole years) per region and overall, on all priority years and on 2016-21 (``frames.publication_lag``, the
    representative primary patents), and the visible share of 2022 and 2023 per region and overall (``lib.growth.visible_share`` on the
    2016-21 lags of the designs, as ``frames.region_years`` per region and the lag-corrected total of NUMBERS_I overall)."""
    ds, v = ctx.ds, ctx.v
    lag = frames.publication_lag(ds).dropna(subset=["lag"])
    py = pd.to_numeric(lag["priority_year"], errors="coerce")
    late = lag[py.between(2016, 2021)]
    p90 = lambda d: float(round(_growth.lag_quantile(d["lag"])))             # noqa: E731
    pl = {r: (p90(lag[lag["region"].eq(r)]), p90(late[late["region"].eq(r)])) for r in frames.REGIONS}
    pl["all"] = (p90(lag), p90(late))

    snap = pd.to_datetime(ds.identity["snapshot_date"].dropna().iloc[0])
    S, frac = int(snap.year), float(snap.dayofyear / 365.0)
    j = frames.with_publication(ds, v)
    ref = j[j["year"].between(2016, 2021)]
    lagr = {r: ref.loc[ref["region3"].eq(r), "lag"].dropna().to_numpy() for r in frames.REGIONS}
    lagr["all"] = ref["lag"].dropna().to_numpy()
    vis = {r: (len(a), [100 * _growth.visible_share(a, S - y, frac) for y in (2022, 2023)]) for r, a in lagr.items()}
    return dict(patents=len(lag), first=int(py.min()), last=int(py.max()), snapshot=snap.date().isoformat(), p90=pl, visible=vis)


def run(cfg, ctx) -> dict:
    k = lag_keys(ctx)
    nf = latex_root(cfg) / "Data_for_writing" / "NUMBERS_I.md"
    txt = nf.read_text(encoding="utf-8")
    if START in txt:                                                          # rerun: drop the block before writing it again
        txt = txt[:txt.index(START)] + txt[txt.index(AFTER):]
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_I.md"))
    p90 = k["p90"]
    same = len({x for pair in p90.values() for x in pair}) == 1
    names = {**{r: r for r in frames.REGIONS}, "all": "overall, all regions"}
    L = [f"{START}`frames.publication_lag`, {k['patents']} representative primary patents, snapshot {k['snapshot']}). It takes ALL priority years "
         f"({k['first']}-{k['last']}), with no filter for years complete at the snapshot; `frames.filings_per_year` feeds the same all-years lag to "
         "`lag_quantile`. (b) is the same on priority years 2016-2021 only. "
         + (f"Both give {p90['all'][0]:.0f} years in every region, so the choice of years does not change the figure." if same else
            "NOTE: the two columns differ; see the table."), "",
         "| key | all priority years | 2016-2021 only |", "|---|---|---|"]
    for r, (a, b) in p90.items():
        c = KEY.get(r, r)
        L.append(f"| `pub_lag_{c}_allyears` / `pub_lag_{c}_1621` ({names[r]}) | {a:.1f} | {b:.1f} |")
    L += ["", "- Share of the aircraft already published at the snapshot (`lib.growth.visible_share`, lags of the designs of priority years 2016-21 "
          f"per region, as `frames.region_years`; overall = all {k['visible']['all'][0]} designs, other regions included, as the lag-corrected total below):",
          "", "| key | 2022 | 2023 |", "|---|---|---|"]
    for r, (n, (v22, v23)) in k["visible"].items():
        L.append(f"| `visible_{{2022,2023}}_{KEY.get(r, r)}` ({'overall' if r == 'all' else r}, n ref = {n}) | {v22:.1f} % | {v23:.1f} % |")
    L += ["", ""]
    i = txt.index(AFTER)
    nf.write_text(txt[:i] + "\n".join(L) + txt[i:], encoding="utf-8")
    return k


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    print(run(cfg, thesis.context(cfg)))
