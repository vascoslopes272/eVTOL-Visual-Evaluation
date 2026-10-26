"""Build the four review pages for the LLM-sourced inputs behind Part I (domain, TRL, evtol.news year, AAM
Reality Index firm mapping): review/{domain,trl,year,ari_firm}_review.html, filled from their
*_review_template.html with __DATA__.

Sampling (author's ruling, 2026-10-11): z = 1.96 (95% confidence), p = 0.5 (max variance, no prior error-rate
estimate), e = 0.10 margin of error, finite-population corrected — the same equation `lib.intervals.wilson_fpc_interval`
already applies elsewhere in the thesis, solved for n instead of the interval:

    n0 = z^2 * p(1-p) / e^2
    n  = n0*N / (n0 + N - 1)

seed 42, matching `labelling_analysis.yaml`'s `analysis.random_seed`. The domain review's 22 contradictions
(excluded by the rule but linked to a patent) are a named, finite list, not a sampling population — every one
of them is reviewed; sampling applies to the remaining 331 "ordinary" exclusions, the TRL rows that rest on
actual evidence (105 of 798 — the other 693 are "no public evidence found, TRL 2 by construction" and are not
an LLM judgement call), and the full 1229-row evtol.news year table. The 43 AAM firm names are reviewed in
full (sampling would barely shrink the list).

Run: python3 notebooks/_build/prepare_review_pages.py
"""
from __future__ import annotations

import json
from urllib.parse import quote
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent))
from viz import config, frames

REVIEW = HERE.parent / "review"
SEED = 42
Z, P, E = 1.96, 0.5, 0.10


def sample_n(N: int) -> int:
    n0 = Z ** 2 * P * (1 - P) / E ** 2
    return max(1, min(N, math.ceil(n0 * N / (n0 + N - 1))))


def frag(url: str, s: str) -> str:
    from urllib.parse import quote
    w = s.split()
    enc = lambda t: quote(t, safe="").replace("-", "%2D")
    return url + "#:~:text=" + (enc(s) if len(w) <= 12 else enc(" ".join(w[:6])) + "," + enc(" ".join(w[-4:])))


def page_cites(text: str, url: str, pats: list[str], spec_fields: list[str]):
    """Verbatim lines of the crawled evtol.news page that carry the reason: spec-sheet lines first, then descriptive
    sentences (never Resources-list entries), each with a link that highlights it on the page."""
    out, seen = [], set()
    for line in re.split(r"\n+", text):
        s = line.strip()
        low = s.lower()
        if any(low.startswith(f.lower() + ":") for f in spec_fields) and s not in seen:
            seen.add(s); out.append({"kind": "spec sheet on the page", "text": s, "link": frag(url, s)})
    cand = []
    for s in re.split(r"(?<=[.!?])\s+|\n+", text):
        s = s.strip()
        if 50 < len(s) < 420 and not re.match(r"(Article|Video|Article/Video)\b", s) and s not in seen:
            score = sum(bool(re.search(p, s, re.I)) for p in pats)
            if score:
                cand.append((-score, len(cand), s))
    for sc, _, s in sorted(cand)[:3]:
        out.append({"kind": "page text", "text": s, "link": frag(url, s), "score": -sc})
    return out


def fill(template_name: str, out_name: str, data) -> Path:
    tpl = (REVIEW / template_name).read_text(encoding="utf-8")
    out = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    p = REVIEW / out_name
    p.write_text(out, encoding="utf-8")
    return p


# ------------------------------------------------------------------------------------------------ domain
def build_domain(cfg, keys=None):
    raw = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False)
    d = frames.directory_frame(cfg).rename(columns={"status": "status_resolved"})
    w = raw.merge(d[["slug_key", "class5", "status_resolved", "in_domain", "patented"]], on="slug_key", how="left")
    power = w["spec_power_source"].str.lower()
    combustion_only = power.str.contains("hybrid|fuel cell|turbine|engine|gas|hydrogen") & ~power.str.contains("batter|electric")
    cap = w["spec_capacity"].str.lower()
    cargo_only = cap.str.contains("cargo only|no passengers") | w["status"].eq("cargo drone")

    kw = re.compile(r"hybrid|fuel cell|turbine|engine|gas|hydrogen")

    def trigger(i):
        """(short reason, the exact spec-sheet text that triggers it): what the rule actually matched."""
        r = w.iloc[i]
        if combustion_only.iloc[i]:
            hit = sorted(set(kw.findall(str(r["spec_power_source"]).lower())))
            return "combustion / fuel cell: " + ", ".join(hit), "Power source: " + r["spec_power_source"]
        if r["status_resolved"] == "cargo drone":
            return "cargo drone (listed status)", "Status: " + (r["list_status"] or r["status"])
        cp = str(r["spec_capacity"]).lower()
        if (re.search(frames.DIRECTORY_CARGO_TYPE, str(r["spec_aircraft_type"]).lower())
                or re.search(frames.DIRECTORY_CARGO_NAME, str(r["title"]).lower())) and not re.search(frames.DIRECTORY_PEOPLE, cp) \
                and "no passengers" not in cp and "cargo only" not in cp:
            how = "name" if re.search(frames.DIRECTORY_CARGO_NAME, str(r["title"]).lower()) else "aircraft type"
            return "cargo / drone aircraft (" + how + ")", ("Aircraft type: " + r["spec_aircraft_type"]) if how == "aircraft type" else "Name: " + r["title"]
        if "no passengers" in cp:
            return "no passengers", "Capacity: " + r["spec_capacity"] + (" · Piloting: " + r["spec_piloting"] if r["spec_piloting"] else "")
        if "cargo only" in cp:
            return "cargo only", "Capacity: " + r["spec_capacity"]
        return "other", ""

    pages = {r["slug_key"]: r["text"] for r in map(json.loads, open(cfg.path("evtolnews_aircraft").parent / "pages.jsonl"))}
    PATS = {"combustion": [r"engine|turbine|turboshaft", r"hybrid|hydrogen|fuel cell", r"combustion|petrol|gasoline|diesel|\bgas\b|fuel"],
            "unmanned": [r"cargo (aircraft|drone|delivery|transport|only)|air cargo|cargo-only", r"drone|unmanned|uncrewed|uninhabited", r"remotely|remote[- ]controlled|autonomous|no passengers|without a pilot|pilotless"]}

    dec = pd.read_csv(cfg.path("evtolnews_aircraft").parent.parent / "1_filter" / "image_decisions.csv", keep_default_na=False,
                      usecols=["slug_key", "img_pos", "local_path", "keep", "p_aircraft"])
    dec = dec[dec["keep"].astype(str).eq("True")].sort_values(["slug_key", "img_pos"])
    IMGS = {k: ["file://" + quote(x) for x in g["local_path"].head(2)] for k, g in dec.groupby("slug_key")}

    def row(i, section):
        r = w.iloc[i]
        why, text = trigger(i)
        kind = "combustion" if why.startswith("combustion") else "unmanned"
        cites = page_cites(pages.get(r["slug_key"], ""), r["url"], PATS[kind],
                           (["Power source"] if kind == "combustion" else ["Capacity", "Piloting"]))
        spec = [c for c in cites if c["kind"].startswith("spec")]
        desc = [c for c in cites if c["kind"] == "page text"]
        trig = next((c for c in spec if c["text"].startswith("Capacity")), None) if kind == "unmanned" else (spec[0] if spec else None)
        best = (desc[0] if desc and desc[0]["score"] >= 3 else trig or (desc[0] if desc else None)
                or {"kind": "structured field", "text": text, "link": r["url"]})
        name_hint = bool(re.search(r"cargo|drone|freighter", str(r["title"]), re.I)) and kind == "unmanned"
        grp = why.split(":")[0]
        return {"key": r["slug_key"], "title": r["title"] or r["model"] or r["slug_key"], "url": r["url"],
                "patented": bool(r["patented"]), "why": why, "text": text, "best": best, "name_hint": name_hint, "cur": "exclude", "section": section,
                "reason": grp if section == "B" else None, "imgs": IMGS.get(r["slug_key"], [])}

    excluded = w.index[~w["in_domain"].astype(bool)].tolist()
    contra_idx = [i for i in excluded if bool(w.iloc[i]["patented"])]
    bulk_idx = [i for i in excluded if not bool(w.iloc[i]["patented"])]
    n = sample_n(len(bulk_idx))
    rng = np.random.default_rng(SEED)
    sample_idx = list(rng.choice(bulk_idx, size=n, replace=False))
    if keys is not None:  # resample: the given pages, patent-linked ones included, all as section B
        sample_idx = [i for i in excluded if w.iloc[i]["slug_key"] in set(keys)]; contra_idx = []; bulk_idx = excluded; n = len(sample_idx)

    data = {"contradictions": [row(i, "A") for i in contra_idx], "sample": [row(i, "B") for i in sample_idx],
            "pool_n": len(bulk_idx), "opts": [["exclude", "confirm excluded"], ["in_domain", "override: actually in-domain"]]}
    print(f"domain: {len(contra_idx)} contradictions (reviewed in full), {len(bulk_idx)} ordinary exclusions, "
          f"sampled {n}")
    return data


# ------------------------------------------------------------------------------------------------ TRL
def build_trl(cfg):
    t = pd.read_csv(cfg.path("trl_per_aircraft"), keep_default_na=False)
    ev = t[t["trl_basis"].eq("evidence")].reset_index(drop=True)
    n = sample_n(len(ev))
    rng = np.random.default_rng(SEED)
    idx = sorted(rng.choice(len(ev), size=n, replace=False).tolist())
    s = ev.iloc[idx]
    data = [{"s": r["aircraft_id"], "n": r["aircraft_id"], "co": r["company"], "tt": r["topType"],
             "y": r["app_year"], "trl": str(r["trl"]), "conf": r["confidence"], "src": r["source"],
             "q": r["evidence_quote"], "def": r["nasa_definition"], "note": r["note"], "prog": r["programme_trl"], "pstat": r["programme_status"], "link": r["source"]} for _, r in s.iterrows()]
    print(f"TRL: {len(ev)} evidence-based rows, sampled {n}")
    return data


# ------------------------------------------------------------------------------------------------ evtol.news year
NOFLIGHT = re.compile(r"(?<!proof of )(?<!proof-of-)concep|mock-?up")


def status_check(cfg, y: pd.DataFrame) -> pd.DataFrame:
    """evtol.news status consistency (author's test, 2026-10-11): a page still listed as a concept design (or a mock-up) has
    not flown and has no prototype, so a reader basis of 'flight' or 'existed_by' (= a prototype existed) cannot be right;
    both are lowered to 'publication' (publication date only). Returns one row per reader decision changed."""
    raw = pd.read_csv(cfg.path("evtolnews_aircraft"), dtype=str, keep_default_na=False)
    st = raw.set_index("slug_key").apply(lambda r: (r["list_status"] or r["status"]).lower(), axis=1)
    rows = []
    for _, r in y.iterrows():
        s = st.get(r["slug_key"], "")
        if not NOFLIGHT.search(s):
            continue
        for who in ("a", "b"):
            if r[f"basis_{who}"] in ("flight", "existed_by"):
                rows.append({"slug_key": r["slug_key"], "list_name": r["list_name"], "evtolnews_status": s, "reader": who.upper(),
                             "year": r[f"year_{who}"], "basis_was": r[f"basis_{who}"], "basis_now": "publication"})
    return pd.DataFrame(rows)


def build_year(cfg):
    y = pd.read_csv(cfg.path("evtolnews_dev_years"), keep_default_na=False)
    n = sample_n(len(y))
    rng = np.random.default_rng(SEED)
    idx = sorted(rng.choice(len(y), size=n, replace=False).tolist())
    chk = status_check(cfg, y)
    chk.to_csv(REVIEW / "YEAR_BASIS_STATUS_CHECK.csv", index=False)
    fixed = {(r.slug_key, r.reader): r.basis_was for r in chk.itertuples()}
    print(f"year status check: {chk.slug_key.nunique()} concept-design / mock-up pages carry a flight or prototype-existed basis "
          f"({len(chk)} reader decisions lowered to publication only); written to review/YEAR_BASIS_STATUS_CHECK.csv")
    s = y.iloc[idx]
    ev = pd.read_csv(cfg.path("evtolnews_dev_years").parent / "readers" / "evidence_ids.csv", dtype=str, keep_default_na=False)
    by = {k: g[["evidence_id", "years", "sentence", "link", "is_resource"]].values.tolist() for k, g in ev.groupby("slug_key")}
    air = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False).set_index("slug_key")
    STOP = set("concept design demonstrator prototype defunct aircraft evtol electric vtol the and of for with air cargo drone passenger personal vehicle".split())

    def fill(slug, company):
        """Earliest dated Resources entry whose text names this aircraft (a distinctive token of its model name)."""
        a = air.loc[slug]
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", str(a["model"]))
        co = set(re.findall(r"[a-z0-9]+", str(company).lower()))
        tok = {w.lower() for w in words if len(w) >= 3 and w.lower() not in STOP and w.lower() not in co}
        tok = {w for w in tok if re.search(r"\d|-", w) or len(w) >= 5}
        best = None
        for e_id, yrs, sent, link, isr in by.get(slug, []):
            if isr != "True" or not yrs.strip():
                continue
            if any(w in sent.lower() for w in tok):
                yr = min(yrs.split())
                if best is None or yr < best[0]:
                    best = (yr, e_id)
        return best

    data = [{"s": r["slug_key"], "sents": by.get(r["slug_key"], [])[:60], "eid": r["evidence_id"], "n": r["list_name"], "u": r["url"], "co": r["company"], "st0": r["status"],
             "c": r["evtol_class"], "st": r["dev_year_status"], "y": r["dev_year"], "tier": r["year_tier"],
             "ev": r["evidence"], "el": r["evidence_link"],
             "fy": (fill(r["slug_key"], r["company"]) or ("", ""))[0] if not r["dev_year"] else "", "fid": (fill(r["slug_key"], r["company"]) or ("", ""))[1] if not r["dev_year"] else "", "chk": "; ".join(f"Reader {w}: {fixed[(r['slug_key'], w)]} → publication only" for w in "AB" if (r["slug_key"], w) in fixed), "ya": r["year_a"], "ba": "publication" if (r["slug_key"], "A") in fixed else r["basis_a"], "na": r["note_a"], "ida": r["id_a"],
             "yb": r["year_b"], "bb": "publication" if (r["slug_key"], "B") in fixed else r["basis_b"], "nb": r["note_b"], "idb": r["id_b"]} for _, r in s.iterrows()]
    print(f"year: {len(y)} rows, sampled {n}")
    return data


# ------------------------------------------------------------------------------------------------ AAM firm map
def build_ari(cfg):
    f = pd.read_csv(cfg.path("ari_firm_map"), keep_default_na=False)
    data = [{"oem": r["oem"], "canon": r["company_canonical"], "note": r["note"]} for _, r in f.iterrows()]
    print(f"AAM firm map: {len(f)} rows, reviewed in full")
    return data


def build_domain_included(cfg, keys=None):
    """Random sample (95 % CI, e = 10 %) of the pages the rules KEPT in the domain: is any of them really out?"""
    raw = pd.read_csv(cfg.path("evtolnews_aircraft"), keep_default_na=False)
    d = frames.directory_frame(cfg).rename(columns={"status": "status_resolved"})
    w = raw.merge(d[["slug_key", "class5", "in_domain", "patented"]], on="slug_key", how="left")
    inc = w.index[w["in_domain"].astype(bool)].tolist()
    n = sample_n(len(inc))
    idx = list(np.random.default_rng(SEED).choice(inc, size=n, replace=False))
    if keys is not None:  # resample: the given pages
        idx = [i for i in inc if w.iloc[i]["slug_key"] in set(keys)]; n = len(idx)
    dec = pd.read_csv(cfg.path("evtolnews_aircraft").parent.parent / "1_filter" / "image_decisions.csv", keep_default_na=False,
                      usecols=["slug_key", "img_pos", "local_path", "keep"])
    dec = dec[dec["keep"].astype(str).eq("True")].sort_values(["slug_key", "img_pos"])
    IMGS = {k: ["file://" + quote(x) for x in g["local_path"].head(2)] for k, g in dec.groupby("slug_key")}
    names = [("Power source", "spec_power_source"), ("Capacity", "spec_capacity"), ("Aircraft type", "spec_aircraft_type"), ("Piloting", "spec_piloting")]

    def row(i):
        r = w.iloc[i]
        lines = " · ".join(f"{k}: {r[c]}" for k, c in names if str(r[c]).strip())
        return {"key": r["slug_key"], "title": r["title"] or r["model"] or r["slug_key"], "url": r["url"], "patented": bool(r["patented"]),
                "why": "kept in the domain", "text": "", "best": {"kind": "spec sheet on the page", "text": lines or "(no spec lines on the page)", "link": r["url"]},
                "cur": "in_domain", "section": "B", "reason": str(r["class5"]), "imgs": IMGS.get(r["slug_key"], [])}
    data = {"contradictions": [], "sample": [row(i) for i in idx], "pool_n": len(inc), "mode": "included",
            "opts": [["in_domain", "confirm in domain"], ["exclude", "override: actually out of the domain"]]}
    print(f"domain, kept pages: {len(inc)} in the domain, sampled {n}")
    return data


def build_trl_above2(cfg):
    """Every design with TRL above 2 (all rest on page evidence), the author's earlier answers pre-filled."""
    t = pd.read_csv(cfg.path("trl_per_aircraft"), keep_default_na=False)
    ev = t[pd.to_numeric(t["trl"], errors="coerce").gt(2)]
    prior = {}
    f = REVIEW / "decisions" / "TRL_REVIEW_DECISIONS.csv"
    if f.exists():
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        prior = {r["aircraft_id"]: {"trl": r["trl"], "action": r["action"], "t": r["reviewed_at"]} for _, r in d.iterrows()}
    data = [{"s": r["aircraft_id"], "n": r["aircraft_id"], "co": r["company"], "tt": r["topType"],
             "y": r["app_year"], "trl": str(r["trl"]), "conf": r["confidence"], "src": r["source"],
             "q": r["evidence_quote"], "def": r["nasa_definition"], "note": r["note"], "prog": r["programme_trl"],
             "pstat": r["programme_status"], "link": r["source"], "prior": prior.get(r["aircraft_id"])} for _, r in ev.iterrows()]
    print(f"TRL above 2: {len(ev)} designs, {sum(1 for x in data if x['prior'])} already answered")
    return data


def main():
    cfg = config.load()
    fill("domain_review_template.html", "domain_review.html", build_domain(cfg))
    fill("trl_review_template.html", "trl_review.html", build_trl(cfg))
    fill("year_review_template.html", "year_review.html", build_year(cfg))
    fill("ari_firm_review_template.html", "ari_firm_review.html", build_ari(cfg))
    fill("trl_review_template.html", "trl_review_above2.html", build_trl_above2(cfg))
    fill("domain_review_template.html", "domain_review_included.html", build_domain_included(cfg))
    print("written to", REVIEW)


if __name__ == "__main__":
    main()
