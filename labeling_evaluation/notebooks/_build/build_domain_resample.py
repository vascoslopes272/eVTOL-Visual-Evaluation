"""Review pages for the 2026-10-25 domain resample (corrected rules, 871 in / 358 out):
review/domain_resample_{in,out}_review.html from review/decisions/DOMAIN_RESAMPLE_2026-10-25_TO_JUDGE.csv.
Own localStorage keys and own export names, so the 2026-10-11 decision files are never touched.
Run: python3 notebooks/_build/build_domain_resample.py"""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import prepare_review_pages as P
from viz import config
cfg = config.load()
s = pd.read_csv(P.REVIEW / "decisions" / "DOMAIN_RESAMPLE_2026-10-25_TO_JUDGE.csv", keep_default_na=False)
tpl = (P.REVIEW / "domain_review_template.html").read_text(encoding="utf-8")
for side, fn, keyold, keynew, nameold, namenew, data in [
    ("in_domain", "domain_resample_in_review.html", "domainReviewIncluded_v1", "domainResampleIn_v1",
     "DOMAIN_INCLUDED_REVIEW_DECISIONS.csv", "DOMAIN_RESAMPLE_IN_DECISIONS.csv", None),
    ("exclude", "domain_resample_out_review.html", "domainReview_v1", "domainResampleOut_v1",
     "DOMAIN_REVIEW_DECISIONS.csv", "DOMAIN_RESAMPLE_OUT_DECISIONS.csv", None)]:
    keys = set(s[s.script_answer == side].slug_key)
    d = P.build_domain_included(cfg, keys) if side == "in_domain" else P.build_domain(cfg, keys)
    d["pool_n"] = 871 if side == "in_domain" else 358
    assert len(d["sample"]) == len(keys), (side, len(d["sample"]), len(keys))
    t = tpl.replace(keyold, keynew).replace(nameold, namenew)
    (P.REVIEW / fn).write_text(t.replace("__DATA__", __import__("json").dumps(d, ensure_ascii=False)), encoding="utf-8")
    print(fn, len(keys))
