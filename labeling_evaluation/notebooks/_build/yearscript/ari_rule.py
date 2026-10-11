"""Rule-based AAM-index company -> patent-dataset company: normalise both names (lower case, drop legal words and punctuation) and accept
a dataset company whose normalised name equals, contains or is contained in the index name, or whose first word equals. No model."""
import re, sys
sys.path.insert(0, ".")
import pandas as pd
from viz import config, thesis
STOP = {"aviation", "aerospace", "aircraft", "aero", "technologies", "technology", "company", "group", "inc", "ltd", "co", "motor", "air", "mobility", "the", "gmbh", "ag", "corporation", "corp", "flight", "systems"}
def norm(s): return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]
def match(oem, names):
    a = norm(re.sub(r"\(.*?\)", "", oem)); 
    if not a: return ""
    best = ""
    for n in names:
        b = norm(n)
        if not b: continue
        if a == b or (a[0] == b[0] and len(a[0]) >= 4): return n
    return best
if __name__ == "__main__":
    cfg = config.load(); v = thesis.context(cfg).v
    names = sorted({str(x) for x in v.company_canonical if str(x) not in ("Individual Inventor", "Unknown / Independent")})
    m = pd.read_csv(cfg.path("ari_firm_map"), keep_default_na=False)
    rev = pd.read_csv("review/decisions/ARI_FIRM_REVIEW_DECISIONS.csv", keep_default_na=False).set_index("oem")
    rows = []
    for _, r in m.iterrows():
        gold = rev.loc[r.oem, "company_canonical"] if r.oem in rev.index else r.company_canonical   # unanswered rows = blank, confirmed by the author
        s = match(r.oem, names)
        rows.append({"oem": r.oem, "script": s, "gold(author)": gold, "reading step": r.company_canonical, "script_ok": s == gold, "reading_ok": r.company_canonical == gold})
    d = pd.DataFrame(rows)
    print(d[~d.script_ok | ~d.reading_ok].to_string(index=False))
    print(f"\nscript agrees with the author on {int(d.script_ok.sum())} of {len(d)}; reading step on {int(d.reading_ok.sum())} of {len(d)}")
