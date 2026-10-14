"""The four external inputs of Part I set by rule-based scripts (no model), with the author's reading where he read the item.

    build(cfg)  -> writes review/script_outputs/{DOMAIN,YEAR,TRL,COMPANY_MAP}.csv   (run from notebook 60)
    year(cfg), trl(cfg), company_map(cfg) -> the final values the figures read when
    labelling_analysis.yaml analysis.external_inputs == "script" (the default).

final = the author's value where he reviewed the item (review/decisions/*), else the script's value. The scripts are in
notebooks/_build/yearscript/ (year_rule, trl_rule, ari_rule); the domain rules are viz/frames.directory_frame.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PILLAR = Path(__file__).resolve().parents[1]
OUT = PILLAR / "review" / "script_outputs"
DEC = PILLAR / "review" / "decisions"
RULES = PILLAR / "notebooks" / "_build" / "yearscript"


def enabled(cfg) -> bool:
    return str(cfg.analysis.get("external_inputs", "script")) == "script"


def _rules():
    if str(RULES) not in sys.path:
        sys.path.insert(0, str(RULES))


def build(cfg, v=None):
    """Write the four lists. ``v`` = the analysis frame (thesis.context(cfg).v), needed for the company names."""
    _rules()
    from year_rule import rule_year
    from trl_rule import rule_trl
    import ari_rule
    from viz import frames
    OUT.mkdir(parents=True, exist_ok=True)

    # 1 domain (rules + the author's single-page rulings)
    d = frames.directory_frame(cfg)
    d.to_csv(OUT / "DOMAIN.csv", index=False)

    # 2 year
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    by = {k: g for k, g in ev.groupby("slug_key")}
    pages = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False)
    rev = pd.read_csv(DEC / "YEAR_REVIEW_SAMPLE.csv", dtype=str, keep_default_na=False).set_index("slug_key") if (DEC / "YEAR_REVIEW_SAMPLE.csv").exists() else pd.DataFrame()
    rows = []
    for _, p in pages.iterrows():
        y, s = rule_year(by.get(p["slug_key"], ev.iloc[0:0]), p["model"])
        a = rev["year"].get(p["slug_key"]) if len(rev) else None
        rows.append({"slug_key": p["slug_key"], "evtol_class": p["evtol_class"], "script_year": y if y else "", "evidence_sentence": s,
                     "author_year": "" if a is None else a, "final_year": (a if a is not None else (y if y else "")),
                     "source": "author review" if a is not None else "script"})
    pd.DataFrame(rows).to_csv(OUT / "YEAR.csv", index=False)

    # 3 TRL
    t = pd.read_csv(cfg.path("trl_per_aircraft"), keep_default_na=False, dtype=str)
    rv = pd.read_csv(DEC / "TRL_REVIEW_DECISIONS.csv", dtype=str, keep_default_na=False) if (DEC / "TRL_REVIEW_DECISIONS.csv").exists() else pd.DataFrame(columns=["aircraft_id", "trl", "action"])
    rv = rv[rv["action"].isin(["confirmed", "changed"])].set_index("aircraft_id")["trl"]
    from trl_page_rule import all_designs
    R = all_designs(cfg)                                    # fully programmatic: read from the linked evtol.news pages
    t["script_trl"] = t["aircraft_id"].map(lambda a: str(R.get(a, (2, "", ""))[0]))
    t["script_sentence"] = t["aircraft_id"].map(lambda a: R.get(a, (2, "", ""))[1])
    t["script_page"] = t["aircraft_id"].map(lambda a: R.get(a, (2, "", ""))[2])
    t["author_trl"] = t["aircraft_id"].map(rv).fillna("")
    t["final_trl"] = t["author_trl"].where(t["author_trl"].ne(""), t["script_trl"])
    t["source"] = t["author_trl"].ne("").map({True: "author review", False: "script"})
    t[["aircraft_id", "patent_id", "aircraft_name", "company", "script_page", "script_sentence", "script_trl", "author_trl", "final_trl", "source"]].to_csv(OUT / "TRL.csv", index=False)

    # 4 company map (all 43 read by the author; rows he did not edit keep the proposed blank / name he confirmed)
    if v is None:
        from viz import thesis
        v = thesis.context(cfg).v
    names = sorted({str(x) for x in v["company_canonical"] if str(x) not in ("Individual Inventor", "Unknown / Independent")})
    m = pd.read_csv(cfg.path("ari_firm_map"), keep_default_na=False)
    ra = pd.read_csv(DEC / "ARI_FIRM_REVIEW_DECISIONS.csv", keep_default_na=False).set_index("oem")["company_canonical"] if (DEC / "ARI_FIRM_REVIEW_DECISIONS.csv").exists() else pd.Series(dtype=str)
    fix = {"Geely Aviation": "Wofei / Geely Aviation"}           # the author's spelling -> the dataset's exact name
    rows = []
    for _, r in m.iterrows():
        s = ari_rule.match(r["oem"], names)
        a = fix.get(ra.get(r["oem"], r["company_canonical"]), ra.get(r["oem"], r["company_canonical"]))
        rows.append({"oem": r["oem"], "script_match": s, "author": a, "company_canonical": a, "note": r.get("note", "")})
    pd.DataFrame(rows).to_csv(OUT / "COMPANY_MAP.csv", index=False)
    return {k: OUT / f"{k}.csv" for k in ["DOMAIN", "YEAR", "TRL", "COMPANY_MAP"]}


def year(cfg):
    f = OUT / "YEAR.csv"
    return pd.read_csv(f, dtype=str, keep_default_na=False).set_index("slug_key")["final_year"] if f.exists() else None


def trl(cfg):
    f = OUT / "TRL.csv"
    return pd.read_csv(f, dtype=str, keep_default_na=False).set_index("aircraft_id")["final_trl"] if f.exists() else None


def company_map(cfg):
    f = OUT / "COMPANY_MAP.csv"
    return pd.read_csv(f, keep_default_na=False)[["oem", "company_canonical", "note"]] if f.exists() else None
