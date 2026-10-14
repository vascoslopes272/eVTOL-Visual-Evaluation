"""Programmatic TRL straight from the evtol.news pages: no sentence is chosen by hand or by a model.

For a patent design linked to one or more evtol.news pages (evtolnews_patent_links, use = yes), every sentence of the page text
(source list excluded) is passed through trl_rule.rule_trl, after dropping plans and future statements, company-history sentences
and "as of / no information" statements. The design's TRL is the highest level reached by any kept sentence. A design with no linked
page, or no sentence above TRL 2, is TRL 2 (patent only), as before.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trl_rule import rule_trl
from year_rule import COMPANY, FUT, ASOF, PAST

SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def page_sentences(cfg):
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    res = {k: set(s.strip()[:60] for s in g.loc[g["is_resource"].eq("True"), "sentence"]) for k, g in ev.groupby("slug_key")}
    out = {}
    for line in open(cfg.path("evtolnews_aircraft").parent / "pages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        rs = res.get(r["slug_key"], set())
        out[r["slug_key"]] = [s for s in SPLIT.split(r["text"]) if s.strip() and s.strip()[:60] not in rs]
    return out


def page_trl(sentences):
    best, why = 2, ""
    for s in sentences:
        if COMPANY.search(s) or ASOF.search(s) or (FUT.search(s) and not PAST.search(s)):
            continue
        t = rule_trl(s)
        if t > best:
            best, why = t, s
    return best, why


def all_designs(cfg):
    links = pd.read_csv(cfg.path("evtolnews_patent_links"), keep_default_na=False)
    links = links[links["use"].eq("yes")]
    pages = page_sentences(cfg)
    rows = {}
    for _, l in links.iterrows():
        sents = [s for k in str(l["slug_keys"]).split("|") if k for s in pages.get(k, [])]
        rows[l["aircraft_uid"]] = page_trl(sents)
    return rows
