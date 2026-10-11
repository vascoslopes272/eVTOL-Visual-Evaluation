"""Score year_rule against (a) the readers' agreed year on the pages the author did not review (development set) and
(b) the author's own review sample (hold-out, scored once)."""
import sys
sys.path.insert(0, "notebooks/_build/yearscript"); sys.path.insert(0, ".")
import pandas as pd
from year_rule import rule_year
from viz import config
from lib import intervals
cfg = config.load()
Y = "/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/EVTOLNEWS_DS/0_source/years/"
ev = pd.read_csv(Y + "readers/evidence_ids.csv", dtype=str, keep_default_na=False)
by = {k: g for k, g in ev.groupby("slug_key")}
A = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False).set_index("slug_key")
dy = pd.read_csv(Y + "aircraft_dev_year.csv", dtype=str, keep_default_na=False).set_index("slug_key")
rev = pd.read_csv("review/decisions/YEAR_REVIEW_SAMPLE.csv", dtype=str, keep_default_na=False)

def run(keys, gold):
    rows = []
    for k in keys:
        y, s = rule_year(by.get(k, ev.iloc[0:0]), A.loc[k, "model"])
        g = gold(k)
        rows.append({"slug_key": k, "script": y, "gold": g, "sentence": s})
    d = pd.DataFrame(rows)
    d["exact"] = d["script"].astype("Int64").eq(d["gold"].astype("Int64"))
    d["within1"] = (d["script"].astype(float) - d["gold"].astype(float)).abs().le(1)
    return d

dev_keys = [k for k in dy.index if k not in set(rev.slug_key) and dy.loc[k, "dev_year_status"] == "agreed"]
dd = run(dev_keys, lambda k: int(dy.loc[k, "dev_year"]))
print(f"development set (pages the author did not review, readers' agreed year): exact {dd.exact.mean():.3f}, within 1 year {dd.within1.mean():.3f}, n={len(dd)}")

rv = rev[rev.year.ne("")].copy()
ho = run(list(rv.slug_key), lambda k: int(rv.set_index("slug_key").loc[k, "year"]))
n = len(ho); k = int(ho.exact.sum()); k1 = int(ho.within1.sum())
print(f"HOLD-OUT, the author's reviewed years (n={n} with a year): exact {k}/{n} = {k/n:.3f}  95% interval (finite pop 1229) {intervals.wilson_fpc_interval(k, n, 1229)}")
print(f"                                          within 1 year {k1}/{n} = {k1/n:.3f}  95% interval {intervals.wilson_fpc_interval(k1, n, 1229)}")
print("script gave no year for", int(ho.script.isna().sum()), "of", n)
ho.to_csv("review/decisions/YEAR_RULE_VS_AUTHOR.csv", index=False)
