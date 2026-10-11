"""Rule-based development year of an evtol.news aircraft: no model involved.

Candidates are the dated sentences of the page (script-split, fixed ids in readers/evidence_ids.csv). Kept: Resources entries (their
year = publication year) and text sentences with an event word (announced, unveiled, first flight, built, prototype, ...) that name
the aircraft's model or say "the aircraft / prototype / demonstrator". Dropped: company-history sentences (founded, incorporated, ...),
future statements (will, plans to, expected ...), "as of / no information" statements, years after 2026. Year = the earliest kept year.
Developed on the pages the author did NOT review (agreed readers' year as the stand-in target); frozen, then scored once on the author's
review sample (see evaluate_year_rule.py).
"""
import re
import pandas as pd

COMPANY = re.compile(r"\b(?:was|were) (?:founded|incorporated|established|formed|created|started|launched as a company|set up)\b|\bfounded\b|\bincorporated\b|\bestablished in\b|\bformed in\b|\bcompany\b.*\b(?:began|started)|\bheadquarter|\bfounder\b|\bsince (?:19|20)\d\d\b.*\b(?:company|has been)\b", re.I)
EVENT = re.compile(r"\b(?:announce[ds]?|unveil(?:ed|s)?|reveal(?:ed|s)?|introduc(?:ed|es)|first flight|maiden flight|flew|flown|test[- ]flights?|flight test(?:s|ing)?|hover(?:ed)? test|took off|successfully|began|begun|started|commenced|completed|rolled out|rollout|demonstrat(?:ed|es)|launched|showcased|displayed|presented|built|construct(?:ed|ion)|prototype|design(?:ed)? (?:in|began|started)|development (?:began|started|of)|patent(?:ed)? |filed|testing|tests?)\b", re.I)
FUT = re.compile(r"\b(?:will|plans? to|expected|aims? to|intends?|scheduled|target(?:s|ed)?|is planned|are planned|hopes?|goal)\b", re.I)
ASOF = re.compile(r"\bas of\b|\bno (?:information|specifications?|details?)\b|\bnot (?:been )?(?:released|reported|announced|disclosed|stated)\b|\bhas not\b|\bhave not\b|\bunknown\b", re.I)
GEN = re.compile(r"\b(?:the|this|its) (?:aircraft|evtol|vehicle|prototype|demonstrator|design|model|craft|drone|jetpack|helicopter|multicopter)\b", re.I)
PAST = re.compile(r"\b(?:was|were|had|did)\b")


def years(s):
    return [int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-3]\d)\b", s)]


def model_tokens(model):
    return [t.lower() for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", str(model)) if len(t) >= 3]


def rule_year(sentences: pd.DataFrame, model: str):
    """sentences: the page's rows of evidence_ids.csv. Returns (year or None, the sentence that gave it)."""
    tk = model_tokens(model)
    best = None
    for _, r in sentences.iterrows():
        s = r["sentence"]
        if COMPANY.search(s):
            continue
        ys = [y for y in years(s) if y <= 2026]
        if not ys:
            continue
        if r["is_resource"] != "True":
            if not EVENT.search(s) or ASOF.search(s):
                continue
            if FUT.search(s) and not PAST.search(s):
                continue
            if not (any(t in s.lower() for t in tk) or GEN.search(s)):
                continue
        y = min(ys)
        if best is None or y < best[0]:
            best = (y, s)
    return best if best else (None, "")
