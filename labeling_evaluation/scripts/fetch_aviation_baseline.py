#!/usr/bin/env python3
"""Rebuild the aviation-patenting baseline of Labelling Analysis 4.1.1.

Counts all aeronautics patent publications (classification B64) per *priority* year from
WIPO PATENTSCOPE and writes them to
``assets/external/aviation_baseline/b64_by_priority_year.csv``. The document reads that CSV
through :mod:`dataset_facts.la_baseline`; nothing is fetched at render time.

Four series are stored so the choice of baseline can be shown not to drive the answer:

===============  ===========================================================================
``cpc_world``    ``CPC:B64* AND PD:<year>``                     -- every PATENTSCOPE office
``ipc_world``    ``IC:B64* AND PD:<year>``                      -- the IPC reading of the same
``cpc_offices``  the CPC query restricted to the nine publication offices of the corpus
``ipc_offices``  the IPC query restricted to the same nine offices
===============  ===========================================================================

``PD`` is the PATENTSCOPE field for priority date; it was verified against the publication
field (``DP``) before use: for 2024 ``PD`` returns roughly a quarter of what ``DP`` returns,
which is the publication-lag signature a priority-date field must show.

Usage::

    python3 scripts/fetch_aviation_baseline.py            # 1999-2026, writes the CSV
    python3 scripts/fetch_aviation_baseline.py 2005 2024  # a narrower span

The fetch is deliberately slow (a pause between requests) and caches every answer under
``.cache/`` beside the CSV, so a re-run costs nothing and a partial run can be resumed.
"""
from __future__ import annotations

import csv
import hashlib
import http.cookiejar
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "external" / "aviation_baseline"
OUT_FILE = OUT_DIR / "b64_by_priority_year.csv"
CACHE_DIR = OUT_DIR / ".cache"

#: publication offices of the corpus (Labelling Analysis Table A.1, provenance by office)
OFFICES = ["US", "CN", "DE", "WO", "EP", "KR", "FR", "GB", "IT"]
OF = " OR ".join(OFFICES)

SERIES = {
    "cpc_world": "CPC:B64* AND PD:{y}",
    "ipc_world": "IC:B64* AND PD:{y}",
    "cpc_offices": "CPC:B64* AND PD:{y} AND OF:(" + OF + ")",
    "ipc_offices": "IC:B64* AND PD:{y} AND OF:(" + OF + ")",
}

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
COUNT_RE = re.compile(r'class="results-count">\s*([\d,]+)\s+results')
_JAR = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_JAR))
_OPENER.addheaders = [("User-Agent", UA), ("Accept", "text/html,application/xhtml+xml")]


def count(query: str, tries: int = 5) -> int:
    """Hits PATENTSCOPE reports for ``query``, cached on disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fp = CACHE_DIR / (hashlib.sha1(query.encode()).hexdigest() + ".json")
    if fp.exists():
        return json.loads(fp.read_text())["total"]
    url = "https://patentscope.wipo.int/search/en/result.jsf?query=" + urllib.parse.quote(query, safe="")
    for attempt in range(tries):
        try:
            with _OPENER.open(url, timeout=90) as f:
                html = f.read().decode("utf-8", "replace")
            hits = COUNT_RE.findall(html)
            if hits:
                total = int(hits[0].replace(",", ""))
            elif "No result found" in html or "No match for" in html:
                total = 0
            else:
                raise ValueError("result count not found on the page")
            fp.write_text(json.dumps({"query": query, "total": total}))
            time.sleep(2.0 + random.random())
            return total
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def main(first: int = 1999, last: int = 2026) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for year in range(first, last + 1):
        row = {"year": year}
        for name, template in SERIES.items():
            try:
                row[name] = count(template.format(y=year))
            except Exception as exc:                      # a gap is stored as a blank, never guessed
                row[name] = ""
                print(f"  ! {name} {year}: {exc}", file=sys.stderr, flush=True)
        rows.append(row)
        print(f"{year}: " + "  ".join(f"{k}={row[k]}" for k in SERIES), flush=True)
        with OUT_FILE.open("w", newline="") as fh:        # written every year, so a stop is safe
            writer = csv.DictWriter(fh, fieldnames=["year", *SERIES])
            writer.writeheader()
            writer.writerows(rows)
    print(f"wrote {OUT_FILE}", flush=True)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(*args) if args else main()
