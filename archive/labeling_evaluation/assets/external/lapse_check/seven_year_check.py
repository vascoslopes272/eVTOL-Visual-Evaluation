"""Check of the seven-years-from-priority rule on the eVTOL corpus (1,639 simple families).
Input: PatSeer record export (one row per simple family), exported 8 Jun 2026.
Outputs: status_by_priority_year.csv, grant_lag_summary.csv"""
import re
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
REF_YEAR = 2026  # year of the export

d = pd.read_excel(HERE / "1639__dataset_08_06_26.xlsx")
d["priority_year"] = d["SFAM Earliest Priority date"].dt.year
s = d["Legal Status Current"]
d["status"] = np.where(s.str.contains("APPLIED"), "pending",
               np.where(s.str.contains("GRANTED"), "granted", "dead"))

# 1) Status by priority-year cohort
t = pd.crosstab(d["priority_year"], d["status"])
t["n"] = t.sum(axis=1)
t["pending_pct"] = (100 * t["pending"] / t["n"]).round(1)
t["age_years"] = REF_YEAR - t.index
t.to_csv(HERE / "status_by_priority_year.csv")

# 2) Priority-to-grant lag (first grant event in the INPADOC legal status text)
def first_date(txt, pat=r"PATENT GRANT|GRANTED|PATENTED CASE"):
    if not isinstance(txt, str):
        return None
    ds = [m.group(1) for line in txt.split("\n") if re.search(pat, line, re.I)
          for m in [re.search(r"\b(\d{8})\b", line)] if m]
    return min(ds) if ds else None

d["grant_date"] = pd.to_datetime(d["INPADOC Legal Status"].apply(first_date),
                                 format="%Y%m%d", errors="coerce")
g = d[(d["status"] == "granted") & d["grant_date"].notna()]
lag = (g["grant_date"] - g["SFAM Earliest Priority date"]).dt.days / 365.25
summary = {"granted_families": int((d["status"] == "granted").sum()),
           "with_grant_date": len(lag),
           "median_lag_years": round(lag.median(), 2),
           "p75_lag_years": round(lag.quantile(.75), 2),
           "p90_lag_years": round(lag.quantile(.90), 2)}
for n in range(3, 9):
    summary[f"pct_granted_within_{n}y"] = round(100 * (lag <= n).mean(), 1)
pd.Series(summary).to_csv(HERE / "grant_lag_summary.csv", header=["value"])
print(t.to_string()); print(pd.Series(summary).to_string())
