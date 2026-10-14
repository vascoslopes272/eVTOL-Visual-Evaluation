"""Fully programmatic TRL, straight from the evtol.news pages (no sentence chosen by hand or by a model).

A patent design linked to evtol.news pages (evtolnews_patent_links, use = yes) takes its TRL only from the linked pages whose directory
class equals the design's folded architecture (the page shows the same kind of aircraft as the patent drawing). On those pages, every
sentence outside the source list is read, after dropping company history, plans / future statements and "as of" statements, and keeping
only sentences that name the aircraft's model or say "the aircraft / vehicle / prototype / demonstrator". Each kept sentence gets
trl_rule.rule_trl; a page whose aircraft type or title says sub-scale / scaled is capped at TRL 5. The design's TRL is the highest level
reached. No linked page of the same class, or no sentence above TRL 2: TRL 2 (patent only).
Developed on the 53 linked designs the author did not review (the earlier TRL table as stand-in target), frozen, scored once on the
author's 50 reviewed designs (notebook 60).
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trl_rule import rule_trl, SCALE
from year_rule import COMPANY, FUT, ASOF, PAST, model_tokens

SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
GEN = re.compile(r"\b(?:the|this|its) (?:aircraft|evtol|vehicle|prototype|demonstrator|craft)\b", re.I)


def page_sentences(cfg):
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    res = {k: set(s.strip()[:60] for s in g.loc[g["is_resource"].eq("True"), "sentence"]) for k, g in ev.groupby("slug_key")}
    out = {}
    for line in open(cfg.path("evtolnews_aircraft").parent / "pages.jsonl", encoding="utf-8"):
        r = json.loads(line)
        rs = res.get(r["slug_key"], set())
        out[r["slug_key"]] = [s for s in SPLIT.split(r["text"]) if s.strip() and s.strip()[:60] not in rs]
    return out


def all_designs(cfg):
    """aircraft_id -> (TRL, the sentence that set it, the page)."""
    links = pd.read_csv(cfg.path("evtolnews_patent_links"), keep_default_na=False)
    links = links[links["use"].eq("yes")]
    A = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False).set_index("slug_key")
    fold = cfg.analysis["class_fold"]
    P = page_sentences(cfg)
    out = {}
    for _, l in links.iterrows():
        cls = fold.get(l["topType"], "")
        best = (2, "", "")
        for k in [k for k in str(l["slug_keys"]).split("|") if k and k in A.index and A.loc[k, "evtol_class"] == cls]:
            tk = model_tokens(A.loc[k, "model"])
            sub = bool(SCALE.search(A.loc[k, "spec_aircraft_type"] + " " + A.loc[k, "title"]))
            for s in P.get(k, []):
                if COMPANY.search(s) or ASOF.search(s) or (FUT.search(s) and not PAST.search(s)):
                    continue
                if not (any(x in s.lower() for x in tk) or GEN.search(s)):
                    continue
                v = rule_trl(s)
                if sub and v > 5:
                    v = 5
                if v > best[0]:
                    best = (v, s, k)
        out[l["aircraft_uid"]] = best
    return out
