"""Follow-up 2026-10-24 to NUMBERS_I (Analysis I.1, professor comments 35 and 71): the yearly total of designs corrected for publication lag,
with the same correction V.3 applies per region (``frames.region_years``, the frame behind na_share_2023_corr). Reads ctx only; draws no
figure. Writes LaTeX_v15/Data_for_writing/csv/q1_filings_per_year_lag_corrected.csv and appends the section "Follow-up 2026-10-24,
lag-corrected total" to NUMBERS_I.md (a rerun replaces it). Also run by ``latex_v15.write_numbers_I`` (notebook 48).

    python -m viz.followup_2026_10_24_parti      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import numpy as np
import pandas as pd

from lib import growth as _growth
from viz import frames
from viz.thesis_latex_common import drop_section, root as latex_root, tables_md

HEADING = "## Follow-up 2026-10-24, lag-corrected total"
YEARS = range(2016, 2024)


def lag_corrected_total(ctx):
    """Per priority year 2016-23: designs counted, the part the snapshot already sees (``lib.growth.visible_share`` on the publication lags of
    all designs of priority years 2016-21, as ``frames.region_years`` does per region) and the designs expected = counted / visible.
    Check column: the sum of the per-region corrections (each region on its own 2016-21 lags, 'Other regions' included)."""
    ds, v = ctx.ds, ctx.v
    snap = pd.to_datetime(ds.identity["snapshot_date"].dropna().iloc[0])
    S, frac = int(snap.year), float(snap.dayofyear / 365.0)
    j = frames.with_publication(ds, v)
    ref = j[j["year"].between(2016, 2021)]
    lags = ref["lag"].dropna().to_numpy()
    lagr = {r: ref.loc[ref["region3"].eq(r), "lag"].dropna().to_numpy() for r in j["region3"].dropna().unique()}
    rows = []
    for y in YEARS:
        s = j[j["year"].eq(y)]
        n = len(s)
        vis = _growth.visible_share(lags, S - y, frac)
        by_reg = sum(int(s["region3"].eq(r).sum()) / _growth.visible_share(lagr[r], S - y, frac) for r in lagr if s["region3"].eq(r).any())
        rows.append({"priority year": y, "designs counted (raw)": n, "visible at the snapshot (%)": round(100 * vis, 1),
                     "estimated not yet published": round(n / vis - n, 1), "designs expected after correction": round(n / vis, 1),
                     "check: sum of per-region corrections": round(by_reg, 1)})
    out = pd.DataFrame(rows)
    assert out["designs counted (raw)"].tolist() == [int(v["year"].eq(y).sum()) for y in YEARS]
    return out, dict(snapshot=snap.date().isoformat(), n_ref=len(lags), lag_counts=pd.Series(lags).value_counts().sort_index().astype(int).to_dict())


def run(cfg, ctx):
    dfw = latex_root(cfg) / "Data_for_writing"
    t, meta = lag_corrected_total(ctx)
    t.to_csv(dfw / "csv" / "q1_filings_per_year_lag_corrected.csv", index=False)

    nf = dfw / "NUMBERS_I.md"
    txt = drop_section(nf.read_text(encoding="utf-8"), HEADING)
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_I.md"))
    ti = t.set_index("priority year")
    raw21, e21 = ti.loc[2021, "designs counted (raw)"], ti.loc[2021, "designs expected after correction"]
    e22, e23 = ti.loc[2022, "designs expected after correction"], ti.loc[2023, "designs expected after correction"]
    raw_dec = 100 * (1 - 48 / raw21)
    dec22, dec23 = 100 * (1 - e22 / e21), 100 * (1 - e23 / e21)
    lagtxt = ", ".join(f"{int(k)} y: {c}" for k, c in meta["lag_counts"].items())
    L = [f"\n{HEADING}\n",
         "Source: `viz/followup_2026_10_24_parti.py` (`frames.with_publication`, `lib.growth.visible_share`; no figure changed). "
         "Professor comments 35 and 71.\n",
         "Method: the correction of V.3 (`frames.region_years`, behind na_share_2023_corr) applied to the total instead of per region. "
         f"Reference = the {meta['n_ref']} designs of priority years 2016-21, whole years from priority to publication ({lagtxt}). "
         f"Snapshot {meta['snapshot']}. Part visible for priority year y, with k = 2026 - y and f = day of year / 365: "
         "P(lag <= k - 1) + f * P(lag = k). Designs expected = designs counted / part visible. "
         "The check column sums the same correction run region by region on each region's own lags. "
         "CSV: `q1_filings_per_year_lag_corrected.csv`.\n",
         tables_md(t), "",
         f"Reading: the decrease from {raw21} (2021) to 48 (2022 and 2023), {raw_dec:.0f} % raw, survives the correction: "
         f"{e21:.1f} to {e22:.1f} (2022) and {e23:.1f} (2023), a decrease of {dec22:.0f} % and {dec23:.0f} %; the correction adds "
         f"{e22 - 48:.1f} designs to 2022 and {e23 - 48:.1f} to 2023, against the {raw21 - 48} needed to close the gap.\n"]
    nf.write_text(txt.rstrip("\n") + "\n" + "\n".join(L), encoding="utf-8")
    return t, meta


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    ctx = thesis.context(cfg)
    t, meta = run(cfg, ctx)
    print(t.to_string(index=False), "\n", meta)
