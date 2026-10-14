"""Rebuild the dated-sentence file (evidence_ids.csv) from pages.jsonl: every sentence of a page that contains a year, word for word,
with a fixed id, a Resources flag and a text-fragment link to the live page. No model involved."""
import json
import re
import urllib.parse

import pandas as pd

YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d|203[0-5])\b(?!\s*(?:lb|lbs|kg|km|m|ft|hp|kw|kwh|mph|km/h|nm|w|wh|rpm|cc|mm|cm|l)\b)", re.I)
ABBR = r"(?<!\bJan\.)(?<!\bFeb\.)(?<!\bMar\.)(?<!\bApr\.)(?<!\bJun\.)(?<!\bJul\.)(?<!\bAug\.)(?<!\bSep\.)(?<!\bOct\.)(?<!\bNov\.)(?<!\bDec\.)(?<!\bSept\.)(?<!\bDr\.)(?<!\bMr\.)(?<!\bMs\.)(?<!\bSt\.)(?<!\bInc\.)(?<!\bLtd\.)(?<!\bCo\.)(?<!\bNo\.)(?<!\bvs\.)(?<!\bU\.S\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bapprox\.)(?<!\bProf\.)(?<!\bJr\.)"
SENT = re.compile(ABBR + r"(?<=[.!?])\s+(?=[A-Z0-9\"“(])")
RES_LINE = re.compile(r"^(?:Article|Video|Press release|Paper|Podcast|Report|Presentation|Patent|Website|Book|Webinar|News)\b[^:]{0,20}:", re.I)


def sentences(text):
    """(sentence, is_resource) in page order; the lines after the 'Resources:' heading are one entry each."""
    body, _, res = text.partition("\nResources:")
    out = []
    for line in body.split("\n"):
        if RES_LINE.match(line.strip()):
            out.append((line.strip(), True))
            continue
        for s in SENT.split(line.strip()):
            if s.strip():
                out.append((s.strip(), False))
    for line in res.split("\n"):
        if line.strip():
            out.append((line.strip(), True))
    return out


def link(url, s):
    w = s.split()
    frag = urllib.parse.quote(" ".join(w)) if len(w) <= 6 else urllib.parse.quote(" ".join(w[:5])) + "," + urllib.parse.quote(" ".join(w[-4:]))
    return f"{url}#:~:text={frag}"


def build(pages_jsonl, aircraft_csv, out_csv=None):
    urls = pd.read_csv(aircraft_csv, keep_default_na=False).set_index("slug_key")["url"].to_dict()
    rows = []
    for p, line in enumerate(open(pages_jsonl, encoding="utf-8"), 1):
        r = json.loads(line)
        n = 0
        for s, res in sentences(r["text"]):
            ys = sorted(set(YEAR.findall(s)))
            if not ys:
                continue
            n += 1
            rows.append({"evidence_id": f"E{p:04d}.{n:02d}", "page_id": f"P{p:04d}", "slug_key": r["slug_key"], "is_resource": res,
                         "years": " ".join(ys), "sentence": s, "link": link(urls.get(r["slug_key"], "https://evtol.news/" + r["slug_key"]), s)})
    d = pd.DataFrame(rows)
    if out_csv:
        d.to_csv(out_csv, index=False)
    return d
