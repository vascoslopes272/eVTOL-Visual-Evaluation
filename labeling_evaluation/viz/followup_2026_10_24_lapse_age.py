"""Follow-up 2026-10-24 to NUMBERS_I section 2: age at lapse of the lapsed patents of the 604 designs of ``q1_in_force_status`` and the
share of designs not actively protected per priority year. Appends "Age at lapse ..." to NUMBERS_I.md (once), CSVs next to it.

Lapse date = PatSeer 'Estimated Expiry Date' of a patent whose 'Legal Status Current' is INACTIVE (the raw export has no separate lapse-date
column; for an inactive record PatSeer sets this field to the date of the last status event: equals 'Register Legal Status Date' for 79 % of the
230 records that have one, and falls on or before the 2026-06-08 snapshot for all but 4). Age at lapse = lapse date - 'Priority Date (Record)'.

    python -m viz.followup_2026_10_24_lapse_age      (from labeling_evaluation/)
"""
from __future__ import annotations

import shutil
from datetime import datetime

import numpy as np
import pandas as pd

from viz import frames, thesis_q1
from viz.thesis_latex_common import root as latex_root, tables_md

HEADING = "Age at lapse and share not actively protected per priority year (follow-up 2026-10-24)"
RAW = "/mnt/storage_11tb/Drive_files_to_syncronize/2 - Patente & Validation/3 -Raw_Patent_Exports_PatSeer_&Gold_Standard/1639__dataset_08_06_26.xlsx"


def _stats(a: pd.Series) -> dict:
    a = a.dropna()
    return {"lapsed patents": len(a), "median (years)": round(a.median(), 2), "10th percentile (years)": round(a.quantile(0.10), 2),
            "90th percentile (years)": round(a.quantile(0.90), 2)} if len(a) else {"lapsed patents": 0}


def compute(ctx):
    c = thesis_q1._calc(ctx)
    wo, force, ds = c["wo"], c["force"], ctx.ds
    codes = list(force.loc[force["unique aircraft"] >= frames.FORCE_TEST_MIN, "code"])
    big = wo[wo["topType"].isin(codes)]
    links = wo.attrs["links"] if "links" in wo.attrs else c["w"].attrs["links"]
    links = links[links["aircraft_id"].isin(big["aircraft_id"])]
    raw = pd.read_excel(RAW, usecols=["Record Number", "Legal Status Current", "Estimated Expiry Date", "Priority Date (Record)", "Publication Country"])
    raw = raw.rename(columns={"Record Number": "patent_id"}).drop_duplicates("patent_id")
    p = links[links["inactive"]].drop_duplicates("patent_id").merge(raw, on="patent_id", how="left")
    p["priority"] = pd.to_datetime(p["Priority Date (Record)"], errors="coerce")
    p["lapse"] = pd.to_datetime(p["Estimated Expiry Date"], errors="coerce")
    snap = pd.Timestamp(ds.identity["snapshot_date"].dropna().iloc[0])
    p["after_snapshot"] = p["lapse"] > snap
    p["age"] = (p["lapse"] - p["priority"]).dt.days / 365.25
    ok = p[~p["after_snapshot"] & p["age"].notna()].copy()
    ok["office"] = np.where(ok["Publication Country"].eq("US"), "US office", "other offices")
    rows = [{"group": "all lapsed patents", **_stats(ok["age"])}]
    for o in ("US office", "other offices"):
        rows.append({"group": o, **_stats(ok.loc[ok["office"].eq(o), "age"])})
    ages = pd.DataFrame(rows)
    by_status = ok.groupby("Legal Status Current")["age"].agg(["size", "median"]).round(2).reset_index()
    by_status.columns = ["legal status", "lapsed patents", "median (years)"]
    yr = big.groupby("year")["out"].agg(["size", "sum", "mean"])
    yr = pd.DataFrame({"priority year": yr.index.astype(int), "designs": yr["size"].to_numpy(), "not actively protected": yr["sum"].astype(int).to_numpy(),
                       "share": (100 * yr["mean"]).round(1).astype(str).to_numpy() + " %"})
    meta = dict(designs=len(big), inactive_patents=len(p), dropped_after_snapshot=int(p["after_snapshot"].sum()), dropped_no_date=int((~p["after_snapshot"] & p["age"].isna()).sum()),
                negative=int((ok["age"] < 0).sum()), snapshot=snap.date().isoformat())
    return ages, by_status, yr, ok, meta


def run(cfg, ctx):
    ages, by_status, yr, ok, meta = compute(ctx)
    dfw = latex_root(cfg) / "Data_for_writing"
    ok[["patent_id", "aircraft_id", "Legal Status Current", "Publication Country", "priority", "lapse", "age"]].to_csv(dfw / "csv" / "q1_age_at_lapse_patents.csv", index=False)
    ages.to_csv(dfw / "csv" / "q1_age_at_lapse.csv", index=False)
    yr.to_csv(dfw / "csv" / "q1_not_protected_by_priority_year.csv", index=False)
    nf = dfw / "NUMBERS_I.md"
    txt = nf.read_text(encoding="utf-8")
    if HEADING in txt:
        print("already in NUMBERS_I.md - not appended")
        return ages, by_status, yr, meta
    shutil.copy2(nf, nf.with_name(f"PRE_FOLLOWUP_{datetime.now():%Y%m%d_%H%M%S}_NUMBERS_I.md"))
    L = [f"\n### {HEADING}\n",
         "Source: `viz/followup_2026_10_24_lapse_age.py`; CSV `q1_age_at_lapse.csv`, `q1_age_at_lapse_patents.csv`, `q1_not_protected_by_priority_year.csv`. "
         f"Designs: the {meta['designs']} of `q1_in_force_status`. Patents: every patent linked to those designs (own primary patent plus D1/D2 duplicates, "
         "`frames.aircraft_patents`) whose PatSeer legal status is INACTIVE. Age at lapse = lapse date minus priority date (`Priority Date (Record)`), in years of 365.25 days. "
         "**Lapse date = PatSeer `Estimated Expiry Date`** of an INACTIVE record: the export has no separate lapse-date column; for these records the field holds the date of the "
         "last status event (it equals `Register Legal Status Date` for 79 % of the 230 records that have one). Office = the patent's own publication office (US against all others, WO included), "
         f"not the design's. Snapshot {meta['snapshot']}. 'Lapsed' here is every INACTIVE status: nonpayment, expired, withdrawn / abandoned, rejected. "
         f"{meta['inactive_patents']} inactive patents; left out: {meta['dropped_after_snapshot']} with a date after the snapshot, {meta['dropped_no_date']} without a usable date.\n",
         tables_md(ages), "", "By legal status (median age at lapse):\n", tables_md(by_status), "",
         "Designs not actively protected, per priority year (no linked patent in force):\n", tables_md(yr), ""]
    cut = txt.index("\n## 3. ")                                  # the end of section 2
    nf.write_text(txt[:cut].rstrip("\n") + "\n" + "\n".join(L) + txt[cut:], encoding="utf-8")
    return ages, by_status, yr, meta


if __name__ == "__main__":
    from viz import config, thesis
    cfg = config.load()
    out = run(cfg, thesis.context(cfg))
    for o in out:
        print(o.to_string(index=False) if hasattr(o, "to_string") else o, "\n")
