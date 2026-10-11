"""Agreement rate and 95 % Wilson interval (finite-population corrected) of each reviewed input, from the CSVs the four
review pages export.

    python3 notebooks/_build/review_confidence.py [--dir <folder with the CSVs>] [--threshold 0.90]

Reads, from --dir (default: review/decisions, else the Downloads folder): DOMAIN_REVIEW_DECISIONS.csv,
TRL_REVIEW_DECISIONS.csv, YEAR_REVIEW_SAMPLE.csv, ARI_FIRM_REVIEW_DECISIONS.csv. A missing file is skipped.

Agreement = the share of reviewed items the author kept as proposed. The interval is `lib.intervals.wilson_fpc_interval`
(z = 1.96), N = the size of the pool the sample was drawn from. The verdict compares the interval's LOWER bound with the
threshold (the conservative reading). Items the author could not judge ('unsure') are reported, not counted.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

PILLAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PILLAR))
from lib import intervals  # noqa: E402

REVIEW = PILLAR / "review"


def pool_data(name: str, var: str):
    h = (REVIEW / name).read_text(encoding="utf-8")
    return json.loads(re.search(rf"const {var}\s*=\s*(\{{.*?\}}|\[.*?\]);\s*\n?\s*const K", h, re.S).group(1))


def verdict(k, n, N, thr):
    lo, hi = intervals.wilson_fpc_interval(k, n, N)
    return {"agree": k, "of": n, "pool N": N, "share": round(k / n, 3), "95 % low": round(lo, 3), "95 % high": round(hi, 3),
            f"lower bound ≥ {thr:.0%}": "yes" if lo >= thr else "NO"}


def find(folder: Path, name: str):
    p = folder / name
    return p if p.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--threshold", type=float, default=0.90)
    a = ap.parse_args()
    folder = Path(a.dir) if a.dir else (REVIEW / "decisions" if (REVIEW / "decisions").exists() else Path.home() / "Downloads")
    thr = a.threshold
    rows, notes = [], []

    f = find(folder, "TRL_REVIEW_DECISIONS.csv")
    if f:
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        unsure = int((d["action"] == "unsure").sum())
        d = d[d["action"].isin(["confirmed", "changed"])]
        rows.append({"input": "TRL (evidence-based rows)", **verdict(int((d["action"] == "confirmed").sum()), len(d), 105, thr)})
        notes.append(f"TRL: {unsure} marked unsure (not counted)")

    f = find(folder, "YEAR_REVIEW_SAMPLE.csv")
    if f:
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        rows.append({"input": "evtol.news year (kept as proposed)", **verdict(int((d["action"] == "confirmed").sum()), len(d), 1229, thr)})
        t = d["event_type"].value_counts()
        notes.append("year, kind of date chosen by the author: " + ", ".join(f"{k or '(blank)'} {v}" for k, v in t.items()))
        kept = d[d["action"].isin(["confirmed", "changed"])]
        if len(kept):
            pub = int(kept["event_type"].isin(["publication", "existed_by"]).sum())
            notes.append(f"year: {pub} of {len(kept)} kept years are only 'existed by' / publication dates ({pub / len(kept):.0%})")

    f = find(folder, "ARI_FIRM_REVIEW_DECISIONS.csv")
    if f:
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        ans = d[d["action"].isin(["confirmed", "changed"])]
        n_changed = int((ans["action"] == "changed").sum())
        if len(ans) < 43:
            notes.append(f"AAM firm mapping INCOMPLETE: {len(ans)} of 43 rows answered ({n_changed} changed); no verdict until all 43 are answered")
        else:
            rows.append({"input": "AAM firm mapping (all 43; census)", **verdict(43 - n_changed, 43, 43, thr)})

    f = find(folder, "DOMAIN_REVIEW_DECISIONS.csv")
    if f:
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        # the page has been rebuilt since the author reviewed (the rules were fixed), so the stats use the decisions as exported
        # and the pool size the page had at the time (review/decisions/domain_review_pool.json)
        pool = json.loads((folder / "domain_review_pool.json").read_text())["pool_n"] if (folder / "domain_review_pool.json").exists() else None
        bsec = d[(d["section"] == "B") & d["decision"].isin(["exclude", "in_domain"])]
        if len(bsec) and pool:
            rows.append({"input": "domain exclusion (sample, rules as at review time)", **verdict(int((bsec["decision"] == "exclude").sum()), len(bsec), pool, thr)})
        a_dec = d[d["section"] == "A"]
        notes.append(f"domain contradictions: {int((a_dec['decision'] == 'in_domain').sum())} of {len(a_dec)} reviewed were overridden to in-domain "
                     "(a named list, not a sample: no interval)")

    f = find(folder, "DOMAIN_INCLUDED_REVIEW_DECISIONS.csv")
    if f:
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        D = pool_data("domain_review_included.html", "D")
        dd = d[d["decision"].isin(["in_domain", "exclude"])]
        rows.append({"input": "domain: pages KEPT in the domain (sample)", **verdict(int((dd["decision"] == "in_domain").sum()), len(dd), D["pool_n"], thr)})
        notes.append("domain kept pages overridden to out: " + ", ".join(dd.loc[dd["decision"] == "exclude", "slug_key"]))

    if not rows:
        print("No exported CSV found in", folder)
        return
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(out.to_string(index=False))
    print()
    print("\n".join(notes))
    out.to_csv(folder / "REVIEW_CONFIDENCE.csv", index=False)
    print("\nwritten", folder / "REVIEW_CONFIDENCE.csv")


if __name__ == "__main__":
    main()
