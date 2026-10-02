#!/usr/bin/env python3
"""Build the single-file browser page for confirming the text-side architecture (and, later, the scope).

Input : 1639_LABELLED/text_architecture/architecture_text_vs_image_<date>.xlsx (sheet ALL_695)
        + text_architecture/variant_reading/architecture_text_variants_<date>.csv  (per-aircraft readings of the
          patents whose aircraft carry different figure types — these patents get one row PER AIRCRAFT)
        + joined/master_figures.xlsx (approved figures, original paths + rotation)
        + text_scope/scope_llm_<date>.csv                       (only with --with-scope)
Output: Patent-Labelling-Tools/notebooks/post-process/03b_architecture_review.html  (open with file://, no network needed)

    python build_architecture_review_page.py               # architecture only
    python build_architecture_review_page.py --with-scope  # + one scope citation per patent

--with-scope must wait until the blind 100-patent scope sample is exported: the page shows the claim-1
scope reading, and the sample is only a fair test of it if the reviewer has not seen it.

Decisions persist in localStorage (archreview_v1 for architecture — patent rows keyed by patent id, aircraft
rows by variant id; archreview_scope_v1 for scope, keyed by patent id) and are exported as
architecture_review_decisions.csv (saved into 1639_LABELLED/review_decisions). Apply them with apply_architecture_review.py.
The TEXT is the ground truth (user, 2026-09-14): a disagreement is not "figures right / text right" but whether
the architecture the text states is VISIBLE in the figures (column visible_in_figures: yes / no). The import
button reads both the new file and the older 8-column export.
"""
import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED/0_labelling/inputs")
XLSX = ROOT / "text_architecture" / "architecture_text_vs_image_20260909.xlsx"
# per-aircraft readings: the 18 patents with DIFFERENT figure types (2026-09-11) and, from 2026-09-15, the 50 patents
# whose aircraft share one figure type (their architecture had been confirmed once per patent and copied to every aircraft)
VARIANTS = [ROOT / "text_architecture" / "variant_reading" / "architecture_text_variants_20260911.csv",
            ROOT / "text_architecture" / "variant_reading" / "architecture_text_variants_sametype_20260915.csv"]
# the saved decisions file is embedded as a baseline: a decision in it that is newer than the one in this browser wins
DECISIONS = ROOT / "review_decisions" / "architecture_review_decisions.csv"
# decisions the annotator asked to review again (UTC stamp): a browser decision older than the stamp is dropped
# user 2026-09-16: rows to look at again, shown first in the view "🔎 your recheck list" (decided or not)
WATCH = {
    "DE102013001852A1": "still unsure: which type does the text state?",
    "US2023257132A1_arch1": "now the only aircraft of this patent (arch2 removed) — you ruled: no type",
    "EP3974315A1_arch2": "recheck: figure number uncertain (crops swapped) — the CVT ground truth rests on it",
    "EP3974315A1_arch3": "recheck: figure number uncertain (OCR says 1)",
    "EP3974315A1_arch4": "recheck: figure number uncertain (audit: printed Fig. 3)",
    "US11787551B1_arch1": "NEW aircraft (Midnight, D3 made in the wizard) — confirm the citation",
    "US2022388648A1_arch1": "NEW: the wizard splits this patent in 2 aircraft — aircraft 100 (FIGS 1-7)",
    "US2022388648A1_arch2": "NEW: aircraft 800 (FIGS 8-10)",
    "US2024002048A1_arch2": "NEW: arch2 is now aircraft 200 (FIGS 6, 8) — your figures say TR, the text says it propels like aircraft 100 (CVT)",
    "US2024002048A1_arch4": "the FIG. 11 photo you identified as Archer Maker (aircraft-level duplicate; old arch3 decision kept)",
}
REOPEN = {"US2021371117A1": "2026-09-15T21:18", "DE102023129326A1": "2026-09-15T21:18",
          "US2024002048A1_arch2": "2026-09-16T16:44"}   # arch2 is a different aircraft since the wizard renumbering   # user 2026-09-15: "by text shall be reviewed"
SCOPE = ROOT / "text_scope" / "scope_llm_20260911.csv"
# all review pages live together in Patent-Labelling-Tools/notebooks/post-process (user request 2026-09-11)
OUT = Path("/home/vasco/Vasco Workspace/Tese_Vasco_Lnx/Patent-Labelling-Tools/notebooks/post-process/03b_architecture_review.html")
WITH_SCOPE = "--with-scope" in sys.argv

TYPES = {
 "TW":  ("Tilt Wing", "Entire wing panel rotates to redirect thrust vertical→horizontal."),
 "TR":  ("Tilt Rotor", "Propulsors tilt independently of a fixed wing."),
 "DS":  ("Deflected Slipstream", "Fixed propulsors; flaps/surfaces deflect the slipstream downward."),
 "CVT": ("Combined Vectored Thrust", "FIXED and TILTING thrust mechanisms mixed on the same aircraft."),
 "TB":  ("Tilt Body", "Whole airframe rotates between hover and cruise (tail-sitter etc.)."),
 "PTC": ("Pitch-to-Cruise", "Fixed vertical lift rotors + fixed wing; the vehicle pitches to cruise, no cruise propulsor."),
 "SLC": ("Separate Lift + Cruise", "Two separate FIXED propulsion sets: hover rotors + a distinct cruise propulsor."),
 "SRW": ("Stopped/Slowed Rotor Wing", "The hover rotor stops/slows and becomes the cruise lifting surface."),
 "RC":  ("Rotorcraft", "Helicopter topologies (single, coaxial, tandem), no wing."),
 "MR":  ("Multirotor", "Distributed fixed lift rotors, no wing."),
 "HB":  ("Hoverbike", "Motorcycle posture, rider interface visible."),
 "PFV": ("Personal Flying Vehicle", "Wearable suits, jetpacks, standing platforms."),
 "NS":  ("Not stated", "The text does not commit to an architecture."),
}
# Words that make an architecture evident in a sentence. Used twice: to decide whether a citation
# actually carries its type (traffic light), and to highlight those words on the page.
# Plain regex that means the same in Python and JavaScript.
KW = {
 "TR":  r"tilt\w*|proprotor\w*|rotatable|pivotable|pivot\w*|vert(?:s|ed|ing)?\b|nacelles?",
 "TW":  r"tilt[- ]?wing\w*|(?:tilting|tiltable|rotatable|pivoting) wings?|wings?\s+(?:\w+\s+){0,4}(?:tilt\w*|pivot\w*|rotat\w*)",
 "CVT": r"tilt\w*|pivot\w*|vert(?:s|ed|ing)?\b|fixed\w*|lift[- ]fans?|(?:vertical[- ])?lift (?:rotor|propeller|fan)s?",
 "SLC": r"(?:lift|lifting|vertical\w*|hover\w*)\s+(?:\w+\s+){0,2}(?:rotor|propeller|fan|prop|motor|unit|thruster)s?|(?:cruise|cruising|pusher|push|forward|horizontal|rear|tail)\s+(?:\w+\s+){0,2}(?:rotor|propeller|fan|prop|engine|motor|thruster)s?",
 "MR":  r"multi[- ]?(?:rotor|copter)\w*|quad\w*|hexa\w*|octo\w*|drone",
 "RC":  r"helicopter\w*|coaxial|tandem rotor\w*|main rotor\w*|rotorcraft|autogyro\w*|gyroplane",
 "TB":  r"tail[- ]?sitt\w*|vertical attitude|(?:body|fuselage|airframe|aircraft|vehicle)\s+(?:\w+\s+){0,4}(?:tilt\w*|pitch\w*|rotat\w*|upright)",
 "DS":  r"deflect\w*|slipstream|flaps?",
 "SRW": r"(?:stop\w*|slow\w*|lock\w*)\s+(?:\w+\s+){0,3}rotor\w*|rotor\w*\s+(?:\w+\s+){0,3}(?:stop\w*|lock\w*)|rotor[- ]wing",
 "PTC": r"pitch\w*|nose[- ]?(?:down|over)",
 "HB":  r"hover[- ]?bike\w*|motorcycle|saddle|rider|straddl\w*",
 "PFV": r"jet[- ]?pack|wearable|backpack|suit\b|platform|standing",
}
KW["CVT_BOTH"] = (r"tilt\w*|pivot\w*|vert(?:s|ed|ing)?\b|rotat\w*", r"fixed\w*|lift[- ]fans?|lift (?:rotor|propeller|fan)s?|non[- ]tilt\w*")
# The confusions measured on the corpus (text reading vs figures, 2026-09-09): a disagreement between
# two of these is a judgement call between neighbours, not a different aircraft.
NEIGHBOURS = {frozenset(x) for x in [("CVT", "TR"), ("CVT", "SLC"), ("CVT", "TW"), ("TW", "TR"), ("PTC", "SLC"),
                                     ("PTC", "MR"), ("HB", "MR"), ("TW", "TB"), ("CVT", "PTC"), ("PFV", "MR"), ("TB", "TR")]}
import re as _re


def carries(t, quote):
    """Does the citation contain words that state type t?"""
    if not quote or t not in KW or t == "NS":
        return False
    if t == "CVT":
        a, b = KW["CVT_BOTH"]
        return bool(_re.search(a, quote, _re.I) and _re.search(b, quote, _re.I))
    if t == "SLC":
        hits = _re.findall(KW["SLC"], quote, _re.I)
        return len(hits) >= 1
    return bool(_re.search(KW[t], quote, _re.I))


def light(group, image, text, conf, qcheck, quote, flags):
    """green = evident: text and figures agree, the reader was sure, the quote is verbatim and names the type.
    yellow = not that evident: agreement with a weaker citation, or a disagreement between neighbouring types.
    red = really different: the text and the figures point at unrelated architectures.
    Returns (colour, reason)."""
    if group == "notstated":
        return "grey", "the text does not state an architecture"
    imgs = [x for x in str(image).split("|") if x]
    if group in ("agree", "lowconf"):
        # Two independent readings (your figures, the text) landed on the same type and the reader was
        # sure. The keyword test is NOT a gate: patents state architectures in too many words
        # ("tiltable lifting rotors", "vertically oriented motor"); it only drives the highlighting.
        why = []
        if group == "lowconf" or conf != "H": why.append(f"reader confidence {conf or '?'}")
        if qcheck not in ("verbatim", "partial"): why.append("quote not found verbatim in the patent")
        if flags: why.append("aircraft row flagged")
        return ("green", "your figures and the text agree, and the text states it plainly") if not why \
            else ("yellow", "agree, but " + "; ".join(why))
    if not imgs:
        return "yellow", "no figure type to compare (quick override)"
    if text in imgs:
        return "yellow", "one of the drawn aircraft matches the text"
    if any(frozenset((i, text)) in NEIGHBOURS for i in imgs):
        return "yellow", f"neighbouring types ({'|'.join(imgs)} vs {text}) — a known confusion"
    return "red", f"different architectures: figures {'|'.join(imgs)}, text {text}"


SCOPES = {"Whole Aircraft Architecture": "W", "Architectural Subsystem Enabler": "S",
          "Component-Level Generic": "C", "NS": "NS"}


def s(v):
    return "" if pd.isna(v) else str(v)


import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from arch_gt_adjustments import NEW_PATENTS, frozen_labels, readings
allr = pd.read_excel(XLSX, sheet_name="ALL_695")
allr = pd.concat([allr, pd.DataFrame([dict(patent_id=k, **v) for k, v in NEW_PATENTS.items()])], ignore_index=True)
allr["group"] = allr.bucket.map(lambda b: {"0": "agree", "1": "disagree", "2": "lowconf", "3": "notstated"}[str(b)[0]])
qc = pd.read_csv(ROOT / "text_architecture" / "quote_check.csv").set_index("pid")
idn = pd.read_excel(ROOT / "identity" / "aircraft_identity_ALL.xlsx", sheet_name="Identity")[["patent_id", "aircraft_name", "aircraft_name_source"]].set_index("patent_id")
_kn_raw = pd.read_csv(ROOT / "text_architecture" / "known_aircraft_architecture.csv")
# a company whose documented aircraft do not all share one architecture cannot disambiguate by name:
# the gazetteer picks between its models by filing-year window, which is only a guess.
_mixed = {c for c, g in _kn_raw.groupby("company") if g.known_type.nunique() > 1}
known = _kn_raw.drop_duplicates("aircraft_name").set_index("aircraft_name")


def known_auto(pid, img, txt):
    """Exempt a patent from citation confirmation only when three independent things agree:
    the annotator's figure label, the independent text reading (or silence), and the published
    architecture of a documented aircraft of that assignee. Assignees whose documented aircraft
    differ in architecture are excluded, because the gazetteer picks between them by filing year."""
    if pid not in idn.index or idn.at[pid, "aircraft_name_source"] != "gazetteer": return None
    nm = idn.at[pid, "aircraft_name"]
    if nm not in known.index or known.at[nm, "confidence"] != "high": return None
    if known.at[nm, "company"] in _mixed: return None
    kt = known.at[nm, "known_type"]
    if img == kt and (txt == img or txt == "NS"): return f"{nm} = {kt} ({known.at[nm, 'basis']})"
    return None


# image labels frozen before the 2026-09-15 wizard relabel session (same file apply_architecture_review.py reads)
_prim = frozen_labels()   # frozen labels + the aircraft made after the freeze (arch_gt_adjustments.py)
_prim["variant"] = _prim.variant_id.map(lambda v: int(v.rsplit("_arch", 1)[1]) if "_arch" in v else 1)
TYPES_OF = {pid: [s(v) for v in g.sort_values("variant").image_label_frozen] for pid, g in _prim.groupby("patent_id")}
var = readings(pd.read_csv(p).assign(basis=lambda d: d["basis"] if "basis" in d.columns else "aircraft") for p in VARIANTS)
MULTI = set(var.patent_id)
SAMETYPE = {p for p in MULTI if len(set(TYPES_OF.get(p, []))) == 1}
base_dec = {}
if DECISIONS.exists():
    _d = pd.read_csv(DECISIONS, dtype=str, keep_default_na=False)
    for x in _d[_d.decision != ""].itertuples():
        base_dec[x.variant_id or x.patent_id] = {"choice": x.decision, "other": x.final_label if x.decision in ("other", "gt") else "",
                                                 "visible": x.visible_in_figures, "comment": x.comment, "at": x.decided_at}
mf = pd.read_csv(ROOT.parent / "outputs" / "tables" / "figure_table.csv", keep_default_na=False, na_values=[""], low_memory=False)
mf = mf[(mf.status == "approved") & (mf.file_exists == True)]
figs = {}
for pid, g in mf.groupby("patent_id"):
    g = g.sort_values(["is_main", "arch"], ascending=[False, True])
    figs[pid] = [{"src": "file://" + str(r.image_path), "rot": int(r.rotation_deg or 0),
                  "arch": None if pd.isna(r.arch) else int(r.arch), "main": bool(r.is_main == 1),
                  "state": s(r.acState), "per": s(r.per)} for r in g.itertuples()]
scope = {}
if WITH_SCOPE:
    sc = pd.read_csv(SCOPE)
    scope = {r.patent_id: {"code": SCOPES.get(s(r.scope_llm), "NS"), "label": s(r.scope_llm), "field": s(r.field_llm),
                           "quote": s(r.quote), "conf": s(r.confidence), "note": s(r.note)} for r in sc.itertuples()}

data = []
for r in allr.itertuples():
    base = {"pid": r.patent_id, "company": s(r.company_canonical), "name": s(r.aircraft_name_final),
            "year": "" if pd.isna(r.priority_year) else int(r.priority_year), "title": s(r.title),
            "assignee": s(r.assignee), "pdf": s(r.pdf_link), "variants": TYPES_OF.get(r.patent_id, []),
            "realname": s(idn.aircraft_name.get(r.patent_id, "")) if (r.patent_id in idn.index and idn.aircraft_name_source.get(r.patent_id) == "gazetteer") else "",
            "scope": scope.get(r.patent_id)}
    if r.patent_id not in MULTI:
        data.append(dict(base, key=r.patent_id, kind="patent", vn=0, nvar=int(r.n_var) if not pd.isna(r.n_var) else 1,
                         group=r.group, image=s(r.image_label), text=s(r.text_label), conf=s(r.confidence),
                         quote=s(r.quote), note=s(r.note), flags="", figs=figs.get(r.patent_id, []),
                         qcheck=s(qc.quote_check.get(r.patent_id, "")), qsec=s(qc.quote_section.get(r.patent_id, "")),
                         known=known_auto(r.patent_id, s(r.image_label), s(r.text_label)) or "",
                         basis="patent", sametype=False, ptext=""))
        data[-1]["light"], data[-1]["why"] = light(r.group, s(r.image_label), s(r.text_label), s(r.confidence),
                                                   data[-1]["qcheck"], s(r.quote), "")
        continue
    rows_v = var[var.patent_id == r.patent_id].sort_values("variant_id")
    for v in rows_v.itertuples():
        n = int(v.variant_id.rsplit("arch", 1)[1])
        img, txt = s(v.image_type), s(v.text_type)
        group = "notstated" if txt == "NS" else ("agree" if img == txt else "disagree")
        # a patent-level-only citation cites no figure of this aircraft: it can never be "evident", so it is flagged
        pl_only = s(v.basis) == "patent_level_only"
        flags = "; ".join(x for x in [s(v.flags), "no sentence cites this aircraft's figures — patent-level citation" if pl_only else ""] if x)
        data.append(dict(base, key=v.variant_id, kind="aircraft", vn=n, nvar=len(rows_v), group=group,
                         image=img, text=txt, conf=s(v.confidence), quote=s(v.quote), note=s(v.note),
                         flags=flags, figs=[f for f in figs.get(r.patent_id, []) if f["arch"] == n],
                         qcheck="verbatim" if s(v.quote) else "", qsec=s(v.quote_section), known="",
                         basis=s(v.basis), sametype=r.patent_id in SAMETYPE,
                         ptext=f"{s(r.text_label)} — “{s(r.quote)[:220]}”"))
        data[-1]["light"], data[-1]["why"] = light(group, img, txt, s(v.confidence), data[-1]["qcheck"], s(v.quote), s(v.flags))

# 2026-09-17: the ground truth is the author's reading of the WHOLE patent. Rows still to decide (list written by
# text_architecture/build_architecture_ground_truth.py): copied-from-figure rows, aircraft of multi-aircraft patents
# decided once per patent, and "visible but the wizard still differs". Shown in the view "🎯 ground truth still to decide".
GTLIST = ROOT / "text_architecture" / "GT_TO_REVIEW_20260917.xlsx"
GTTODO = {}
_keys = {d["key"] for d in data}
if GTLIST.exists():
    for x in pd.read_excel(GTLIST, keep_default_na=False).itertuples():
        k = x.aircraft_id if x.aircraft_id in _keys else x.patent_id if x.patent_id in _keys else None
        if k is None:
            print("⚠ GT row not on the page:", x.aircraft_id); continue
        GTTODO[k] = {"why": s(x.to_review), "proposed": s(x.proposed_ground_truth) or s(x.ground_truth),
                     "fig": s(x.figure_label_frozen), "wiz": s(x.wizard_label_now)}
print("ground truth still to decide:", len(GTTODO))

from collections import Counter
print("rows:", len(data), Counter((d["kind"], d["group"]) for d in data), "known-auto:", sum(1 for d in data if d["known"]),
      "flagged aircraft:", sum(1 for d in data if d["flags"]), "no figures:", [d["key"] for d in data if not d["figs"]],
      "scope:", "on" if WITH_SCOPE else "off")
_rev = [d for d in data if (not d["known"] and d["group"] != "notstated") or d["flags"]]
print("traffic light on the rows you confirm:", Counter(d["light"] for d in _rev))
_air = [d for d in data if d["kind"] == "aircraft"]
print("aircraft rows:", len(_air), "| same-type:", sum(d["sametype"] for d in _air), "| undecided in the saved file:",
      sum(1 for d in _air if d["key"] not in base_dec), "| baseline decisions embedded:", len(base_dec))

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>03b — architecture type adjudication</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c2128;--mut:#6b7280;--line:#e3e6ea;--acc:#2456c7;--ok:#1a8f4a;--warn:#c2410c;--img:#7c3aed;--txt:#0e7490}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 Inter,system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;padding:8px 14px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header h1{font-size:15px;margin:0 10px 0 0}header select,header button,header input{font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:#fff}
header button{cursor:pointer}#prog{color:var(--mut);font-size:13px}
main{display:grid;grid-template-columns:260px 1fr;min-height:calc(100vh - 46px)}
#list{border-right:1px solid var(--line);background:#fff;overflow:auto;max-height:calc(100vh - 46px)}
#list div{padding:5px 10px;border-bottom:1px solid #f0f1f3;cursor:pointer;font-size:12.5px;display:flex;justify-content:space-between;gap:6px}
#list div.cur{background:#e8efff}#list div.done{color:var(--mut)}#list b{font-weight:600}
#list .tag{font-size:11px;padding:0 5px;border-radius:4px;background:#eef;color:#334;white-space:nowrap}
#panel{padding:14px 18px;overflow:auto}
.head{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline;margin-bottom:8px}
.head h2{margin:0;font-size:18px}.head a{color:var(--acc)}.head .mut{color:var(--mut)}
.figs{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 12px}
.fig{background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px;max-width:420px}
.fig.main{border-color:var(--ok);box-shadow:0 0 0 2px #cdeedb}
.fig img{max-width:400px;max-height:320px;display:block;margin:auto;cursor:zoom-in}
.fig small{display:block;color:var(--mut);font-size:11px;margin-top:4px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.card h3{margin:0 0 6px;font-size:13px;letter-spacing:.02em;text-transform:uppercase;color:var(--mut)}
.big{font-size:22px;font-weight:700}.big.img{color:var(--img)}.big.txt{color:var(--txt)}
.def{color:var(--mut);font-size:12.5px;margin-top:2px}
blockquote{margin:8px 0;padding:8px 10px;background:#f3f6fb;border-left:3px solid var(--txt);border-radius:4px;font-size:13px}
.decide{grid-column:1/3;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.decide button{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;cursor:pointer}
.decide button.on{outline:2px solid var(--acc);background:#e8efff}.decide button:disabled{opacity:.4}
.decide button kbd{font-size:11px;color:var(--mut);margin-right:4px}
.decide select,.decide input{font:inherit;padding:7px 8px;border:1px solid var(--line);border-radius:8px}
.decide input{flex:1;min-width:220px}
#zoom{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:20;cursor:zoom-out}
#zoom img{max-width:96vw;max-height:96vh;background:#fff}
.help{color:var(--mut);font-size:12px;margin-top:10px}
.multi{grid-column:1/3;background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:9px 12px;font-size:13px}
.flag{grid-column:1/3;background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:9px 12px;font-size:13px}
.scope{grid-column:1/3;border-left:4px solid var(--acc)}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:middle}
.Lgreen{background:#16a34a}.Lyellow{background:#eab308}.Lred{background:#dc2626}.Lgrey{background:#9ca3af}
.band{grid-column:1/3;border-radius:10px;padding:10px 14px;font-size:14px;display:flex;gap:10px;align-items:center}
.band.green{background:#dcfce7;border:1px solid #86efac}.band.yellow{background:#fef9c3;border:1px solid #fde047}
.band.red{background:#fee2e2;border:1px solid #fca5a5}.band.grey{background:#f3f4f6;border:1px solid #d1d5db}
.cite{grid-column:1/3;background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.cite .q{font-size:16px;line-height:1.6;margin:6px 0}
mark.t{background:#a7f3d0;padding:0 2px;border-radius:3px}mark.o{background:#fde68a;padding:0 2px;border-radius:3px}
.vs{display:flex;gap:18px;flex-wrap:wrap;align-items:baseline;margin-top:4px}
.figs.small .fig img{max-width:260px;max-height:190px}
details.figbox{grid-column:1/3}
table.batch{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
table.batch td{border-top:1px solid #eef0f3;padding:8px 10px;vertical-align:top;font-size:13.5px}
table.batch tr.off td{background:#fef2f2;color:#6b7280}table.batch tr{cursor:pointer}
table.batch input{width:18px;height:18px;cursor:pointer}
.thumb{width:190px;text-align:center}.thumb img{max-width:180px;max-height:150px;cursor:zoom-in;background:#fff;border:1px solid var(--line);border-radius:6px}
.bt{font-weight:600;font-size:14px;margin-bottom:3px}.bq{line-height:1.5}.btype{font-size:19px;font-weight:700;color:var(--txt)}
.bbar{display:flex;gap:12px;align-items:center;margin:10px 0}.bbar button{font:inherit;font-size:15px;padding:10px 18px;border-radius:8px;border:1px solid #15803d;background:#16a34a;color:#fff;cursor:pointer}
.side{display:grid;grid-template-columns:minmax(300px,45%) 1fr;gap:16px;margin-top:10px;align-items:start}
.side > div{min-width:0}
.sfig{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px;text-align:center}
.sfig img{max-width:100%;max-height:520px;cursor:zoom-in}
.pick2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.pick2 button{font:inherit;padding:14px 10px;border-radius:10px;border:2px solid var(--line);background:#fff;cursor:pointer;text-align:center;line-height:1.35}
.pick2 button b{font-size:24px;display:block}.pick2 button small{color:var(--mut);display:block}
.pick2 .pi{border-color:#c4b5fd}.pick2 .pi b{color:var(--img)}.pick2 .pt{border-color:#a5f3fc}.pick2 .pt b{color:var(--txt)}
.pick2 button.on{outline:3px solid var(--acc)}.pick2 button:disabled{opacity:.4}details.figbox summary{cursor:pointer;color:var(--mut);font-size:13px}
</style></head><body>
<header><h1>03b — architecture type: text vs image</h1>
<select id="view"><option value="gt" selected>🎯 ground truth still to decide (whole patent)</option><option value="gtall">🎯 ground-truth list — decided and open</option><option value="watch">🔎 your recheck list (decided or not)</option><option value="final">🏁 FINAL PASS — everything still open</option><option value="peraircraft">✈ per aircraft + reopened patents — not yet decided</option><option value="vis">👁 visibility still missing (decided, text ≠ figures)</option><option value="lgreen">📋 🟢 evident agreements — 20 at a time</option><option value="lyellow">📋 🟡 other agreements — 20 at a time</option><option value="side">⚖ disagreements — figures vs text</option><option value="unticked">↩ unticked in a list — one per screen</option><option value="recent">✎ already decided — newest first (relabel)</option><option value="legacy">⚠ decided “figures are right” before the text rule</option><option value="todo">to confirm (not auto, not decided)</option><option value="green">🟢 evident — to confirm</option><option value="yellow">🟡 not that evident — to confirm</option><option value="red">🔴 really different — to confirm</option><option value="review">everything you confirm</option><option value="agree">agree — confirm the citation</option><option value="disagree">disagree (text ≠ image)</option><option value="lowconf">agree, low confidence</option><option value="aircraft">aircraft rows (patents with several types)</option><option value="flags">aircraft rows with a flag</option><option value="known">known aircraft — cleared automatically</option><option value="notstated">text not stated (no citation exists)</option><option value="scope">scope — to confirm</option><option value="all">all rows</option></select>
<button id="last" title="everything you already decided, newest first — open one and press another button to relabel it">✎ relabel a decided patent</button>
<input type="text" id="jump" placeholder="jump to patent ID" title="type part of a patent ID and press Enter — works for patents you already decided" style="width:170px">
<span id="prog"></span>
<button id="exp">Export CSV</button><label style="font-size:12px">Import CSV <input type="file" id="imp" accept=".csv" style="width:180px"></label>
<button id="clr" title="clear all decisions on this browser">Reset</button>
</header>
<main><div id="list"></div><div id="panel"></div></main>
<div id="zoom"><img></div>
<script>
// Save straight into 1639_LABELLED/review_decisions (request 2026-09-14). Chrome's save dialog opens on the
// folder chosen last time for this id, so after the first save it lands there by default. Browsers without
// the save dialog fall back to a normal download.
function saveToFolder(blob, name){
  function fallback(){ var a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=name; a.click(); return Promise.resolve('downloads'); }
  if (!window.showSaveFilePicker) return fallback();
  return window.showSaveFilePicker({suggestedName: name, id: 'review_decisions'})
    .then(function(h){ return h.createWritable().then(function(w){ return w.write(blob).then(function(){ return w.close(); }); }); })
    .then(function(){ return 'folder'; })
    .catch(function(e){ return (e && e.name === 'AbortError') ? 'cancelled' : fallback(); });
}

const DATA = __DATA__; const TYPES = __TYPES__; const WITH_SCOPE = __WITH_SCOPE__;
const SLAB={W:'Whole Aircraft Architecture',S:'Architectural Subsystem Enabler',C:'Component-Level Generic'};
const KEY='archreview_v1', SKEY='archreview_scope_v1';
let DEC={}, SDEC={}; try{DEC=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){DEC={}} try{SDEC=JSON.parse(localStorage.getItem(SKEY)||'{}')}catch(e){SDEC={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(DEC));localStorage.setItem(SKEY,JSON.stringify(SDEC))}catch(e){}}
// the saved decisions file (review_decisions/architecture_review_decisions.csv) is embedded when the page is built:
// a decision this browser does not have, or has with an OLDER date, is taken from it (e.g. corrections made in the file)
const BASE=__BASE__;let NBASE=0;
Object.entries(BASE).forEach(([k,b])=>{const d=DEC[k];if(!d||!d.choice||String(b.at||'')>String(d.at||'')){DEC[k]=b;NBASE++}});
const REOPEN=__REOPEN__;
const WATCH=__WATCH__;
// 2026-09-17: ground truth = your reading of the WHOLE patent (text + figures), decided per aircraft
const GTTODO=__GTTODO__;
const GTDONE=r=>{const d=DEC[r.key];return !!d&&(d.choice==='gt'||d.choice==='gt_unsure')};
Object.entries(REOPEN).forEach(([k,t])=>{const d=DEC[k];if(d&&String(d.at||'')<=t){delete DEC[k];NBASE++}});
if(NBASE)save();
let VIEW='gt', CUR=0, ROWS=[], PENDVIS=null;
// rows you unticked in a 20-row list: they leave the list and wait in the "unticked" view
const LKEY='archreview_listskip_v1';let LSKIP={};try{LSKIP=JSON.parse(localStorage.getItem(LKEY)||'{}')}catch(e){LSKIP={}}
function saveSkip(){try{localStorage.setItem(LKEY,JSON.stringify(LSKIP))}catch(e){}}
const LISTMODE=()=>VIEW==='lgreen'||VIEW==='lyellow';
const BATCH=20;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const KW=__KW__;
// words of the text's own type in green, words of any other type in amber
function hl(q,t){let h=esc(q);const own=KW[t]?new RegExp('('+KW[t]+')','gi'):null;
 const others=Object.keys(KW).filter(k=>k!==t&&k!=='CVT_BOTH').map(k=>KW[k]).join('|');
 const tmp=[];const keep=s=>{tmp.push(s);return'\u0000'+(tmp.length-1)+'\u0001'};
 if(own)h=h.replace(own,m=>keep('<mark class="t">'+m+'</mark>'));
 if(others)h=h.replace(new RegExp('('+others+')','gi'),m=>/\u0000|\u0001/.test(m)?m:keep('<mark class="o">'+m+'</mark>'));
 return h.replace(/\u0000(\d+)\u0001/g,(_,i)=>tmp[+i])}
const LNAME={green:'Evident',yellow:'Not that evident',red:'Really different',grey:'Not stated'};
const ALLKW=Object.keys(KW).filter(k=>k!=='CVT_BOTH').map(k=>KW[k]).join('|');
// the citation cut down to its parts that carry architecture words
function shortQ(q){if(!q)return'';const segs=q.split(/\s*(?:\.\.\.|…)\s*|(?<=[.;])\s+/).map(x=>x.trim()).filter(Boolean);
 const re=new RegExp(ALLKW,'i');let keep=segs.filter(x=>re.test(x));if(!keep.length)keep=segs;
 let out=keep.join(' … ');return out.length>380?out.slice(0,377)+'…':out}
function badge(r){return r.qcheck==='verbatim'?'<span style="color:var(--ok)">verbatim</span>':r.qcheck==='partial'?'<span style="color:var(--warn)">partly verbatim</span>':'<span style="color:var(--warn)">not found verbatim</span>'}
function renderBatch(){const P=document.getElementById('panel');const rows=ROWS.slice(0,BATCH);
 if(!rows.length){P.innerHTML='<p class="help">Nothing left in this list. '+(VIEW==='lgreen'?'Next: 📋 🟡 other agreements.':'Next: ⚖ disagreements, then ↩ unticked.')+'</p>';return}
 const bar=`<div class="bbar"><button class="okall">✔ Confirm the ticked rows (<span class="nt">${rows.length}</span>) — Enter</button><span class="help">Read each row. Untick any citation that does not state its type; unticked rows move to “↩ unticked”. ${ROWS.length} left in this list.</span></div>`;
 P.innerHTML=bar+`<table class="batch">${rows.map(r=>`<tr data-k="${esc(r.key)}"><td><input type="checkbox" checked></td>
  <td class="thumb">${r.figs.length?(f=>`<img src="${esc(f.src)}" style="transform:rotate(${f.rot}deg)" loading="lazy">`)(r.figs.find(f=>f.main)||r.figs[0])+(r.figs.length>1?`<br><small class="mut">+${r.figs.length-1} more · figures: ${esc(r.image||'—')}</small>`:`<br><small class="mut">figures: ${esc(r.image||'—')}</small>`):'<small class="mut">no figure</small>'}</td>
  <td style="white-space:nowrap"><span class="dot L${r.light}"></span><b>${esc(r.pid)}</b>${r.kind==='aircraft'?'<br><small>aircraft '+r.vn+'</small>':''}<br><small class="mut">${esc(r.company)} · ${esc(r.year)}</small><br><small>${r.pdf?`<a class="plink" href="${esc(r.pdf)}" target="_blank">PDF ↗</a> · `:''}<a class="plink" href="https://patents.google.com/patent/${esc(r.pid.split('_arch')[0])}/en" target="_blank">Google ↗</a></small></td>
  <td style="white-space:nowrap"><span class="btype">${esc(r.text)}</span><br><small class="mut">${esc((TYPES[r.text]||[''])[0])}</small></td>
  <td><div class="bt">${esc(r.title)}</div><div class="bq">“${hl(shortQ(r.quote),r.text)}”</div><small class="mut">${badge(r)}${r.qsec?' · '+esc(r.qsec):''} · confidence ${esc(r.conf)}${r.light!=='green'?' · '+esc(r.why):''}</small></td></tr>`).join('')}</table>`+bar;
 const count=()=>{const n=P.querySelectorAll('tr[data-k] input:checked').length;P.querySelectorAll('.nt').forEach(x=>x.textContent=n)};
 P.querySelectorAll('tr[data-k]').forEach(tr=>{const cb=tr.querySelector('input');
  const sync=()=>{tr.classList.toggle('off',!cb.checked);count()};
  cb.onchange=()=>{sync();cb.blur()};tr.onclick=e=>{if(e.target!==cb&&!e.target.closest('a')&&!e.target.closest('.thumb')){cb.checked=!cb.checked;sync()}}});
 P.querySelectorAll('.thumb img').forEach(im=>im.onclick=()=>{const z=document.getElementById('zoom');z.querySelector('img').src=im.src;z.querySelector('img').style.transform=im.style.transform;z.style.display='flex'});
 P.querySelectorAll('.okall').forEach(b=>b.onclick=confirmBatch)}
function confirmBatch(){const P=document.getElementById('panel');const at=new Date().toISOString().slice(0,16);
 P.querySelectorAll('tr[data-k]').forEach(tr=>{const k=tr.dataset.k;
  if(tr.querySelector('input').checked)DEC[k]={choice:'confirm',other:'',visible:'yes',comment:'',at:at,ts:Date.now(),n:nextN()};else LSKIP[k]=1});
 save();saveSkip();render();window.scrollTo(0,0)}
function figHTML(f,big){return `<img src="${esc(f.src)}" style="transform:rotate(${f.rot}deg)" loading="lazy"><small>${f.main?'MAIN · ':''}${f.arch?'aircraft '+f.arch+' · ':''}${esc(f.state)} ${esc(f.per)}</small>`}
function sideHTML(r,d,other,legacy){const f0=r.figs.find(f=>f.main)||r.figs[0];const rest=r.figs.filter(f=>f!==f0);
 return `<div class="head"><h2>${esc(r.pid)}${r.kind==='aircraft'?' · aircraft '+r.vn+' of '+r.nvar:''}</h2><span>${esc(r.company)} · ${esc(r.year)}</span>${r.pdf?`<a href="${esc(r.pdf)}" target="_blank">PDF ↗</a>`:''}<a href="https://patents.google.com/patent/${esc(r.pid)}/en" target="_blank">Google Patents ↗</a></div>
 <div class="ptitle2" style="font-size:16px;font-weight:600">${esc(r.title)}</div>${undoBar(r)}
 <div class="side"><div class="sfig">${f0?`<div class="fig" style="border:0;max-width:none">${figHTML(f0)}</div>`:'<p class="help">no approved figure on disk</p>'}${rest.length?`<div class="help">${rest.length} more figure(s) below</div>`:''}</div>
  <div><div class="band ${r.light}"><span class="dot L${r.light}" style="width:14px;height:14px"></span><b>${LNAME[r.light]}</b><span>${esc(r.why)}</span></div>
   <div class="cite" style="margin-top:10px">${r.quote?`<div class="q">“${hl(r.quote,r.text)}”</div><div class="def">${badge(r)}${r.qsec?' · '+esc(r.qsec):''} · confidence ${esc(r.conf)}${r.note?' · note: '+esc(r.note):''}</div>`:'<div class="def">no citation</div>'}</div>
   <div class="def" style="margin-top:8px">The text is the ground truth: the architecture is <b>${esc(r.text)}</b> if the citation states it. The only question is whether the figures show it.</div>
   <div class="pick2"><button data-c="text" data-v="no" class="pi ${d.choice==='text'&&d.visible==='no'?'on':''}" ${r.text==='NS'?'disabled':''}><kbd>1</kbd> Not visible in the figures<b>${esc(r.text)}</b><small>the figures read as ${esc(r.image||'—')} ${esc((TYPES[r.image]||[''])[0])}</small></button>
    <button data-c="text" data-v="yes" class="pt ${d.choice==='text'&&d.visible==='yes'?'on':''}" ${r.text==='NS'?'disabled':''}><kbd>2</kbd> Visible in the figures too<b>${esc(r.text)}</b><small>${esc((TYPES[r.text]||[''])[0])} can be seen in the drawings</small></button></div>
   <div class="decide"><button data-c="other" class="${d.choice==='other'?'on':''}"><kbd>3</kbd>The text states another type:</button>
    <select id="other">${other.map(t=>`<option value="${t}" ${d.other===t?'selected':''}>${t} — ${TYPES[t][0]}</option>`).join('')}</select>
    <button data-c="unsure" class="${d.choice==='unsure'?'on':''}"><kbd>4</kbd>The text does not settle it</button>
    <button data-c="ns" class="${d.choice==='ns'?'on':''}"><kbd>5</kbd>The text says nothing about the architecture</button>
    <input id="cmt" placeholder="comment (optional)" value="${esc(d.comment||'')}"></div>
   ${d.choice==='image'?`<div class="flag" style="margin-top:8px">⚠ decided earlier as “figures are right”. The text is the ground truth now — choose 1, 2, 3 or 4 again.</div>`:''}
   ${r.kind==='aircraft'?`<div style="margin-top:8px">${airBox(r,legacy)}</div>`:''}
   ${r.flags?`<div class="flag" style="margin-top:8px">⚑ ${esc(r.flags)}</div>`:''}
   <div class="def" style="margin-top:8px">${r.image&&TYPES[r.image]?esc(r.image)+' = '+esc(TYPES[r.image][1])+'<br>':''}${TYPES[r.text]?esc(r.text)+' = '+esc(TYPES[r.text][1]):''}</div></div></div>
 ${rest.length?`<div class="figs small">${rest.map(f=>`<div class="fig">${figHTML(f)}</div>`).join('')}</div>`:''}
 <p class="help">1 not visible in the figures · 2 visible in the figures too · 3 the text states another type · 4 the text does not settle it · 5 the text says nothing about the architecture · ←/→ navigate · click a figure to zoom</p>`}
function bind(r,P){
 const u=P.querySelector('button.undo');if(u)u.onclick=()=>undo(r);
 P.querySelectorAll('button[data-vis]').forEach(b=>b.onclick=()=>setVis(r,b.dataset.vis));
 P.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>decide(r,b.dataset.c,b.dataset.v));
 P.querySelectorAll('.decide button[data-s]').forEach(b=>b.onclick=()=>decideScope(r,b.dataset.s));
 const ot=P.querySelector('#other');if(ot)ot.onchange=e=>{if(DEC[r.key]){DEC[r.key].other=e.target.value;save();render()}};
 const cm=P.querySelector('#cmt');if(cm)cm.onchange=e=>{DEC[r.key]=DEC[r.key]||{choice:''};DEC[r.key].comment=e.target.value;save()};
 const so=P.querySelector('#sother');if(so)so.onchange=e=>{if(SDEC[r.pid]){SDEC[r.pid].other=e.target.value;save();render()}};
 const sc=P.querySelector('#scmt');if(sc)sc.onchange=e=>{SDEC[r.pid]=SDEC[r.pid]||{choice:''};SDEC[r.pid].comment=e.target.value;save()};
 P.querySelectorAll('.fig img, .sfig img').forEach(im=>im.onclick=()=>{const z=document.getElementById('zoom');z.querySelector('img').src=im.src;z.querySelector('img').style.transform=im.style.transform;z.style.display='flex'});
}
function label(t){const d=TYPES[t];return t?`<span class="big">${esc(t)}</span> <span class="def">${d?esc(d[0]):''}</span>`:'<span class="def">— (no image type: unclassifiable / quick override)</span>'}
function finalOf(r,d){if(!d)return'';if(d.choice==='gt')return d.other||'';if(d.choice==='gt_unsure')return'?';if(d.choice==='ns')return'NS';if(d.choice==='confirm')return r.text;if(d.choice==='image')return r.image;if(d.choice==='text')return r.text;if(d.choice==='other')return d.other||'';return d.choice==='unsure'?'?':''}
const AG=r=>r.group==='agree'||r.group==='lowconf';
const REVIEW=r=>(!r.known&&r.group!=='notstated')||!!r.flags;
const SNEED=r=>WITH_SCOPE&&!!r.scope&&!(SDEC[r.pid]&&SDEC[r.pid].choice);
const firstOfPid=r=>DATA.find(x=>x.pid===r.pid)===r;
const ORDER={green:0,yellow:1,red:2,grey:3};
// a decided row whose ground truth differs from the figure type must say whether the figures show it
const needVis=(r,d)=>{if(!d||!d.choice||d.visible)return false;const f=finalOf(r,d);return !!f&&f!=='?'&&f!=='NS'&&f!==r.image};
// FINAL PASS (2026-09-15): 1 reopened · 2 aircraft not decided · 3 patent rows not decided · 4 legacy "figures are right" ·
// 5 "the text does not settle it" not yet re-checked in this pass · 6 decided but visibility missing
function openStage(r){const d=DEC[r.key];
 if(r.key in REOPEN&&!d)return 1;
 if(r.kind==='aircraft'&&(REVIEW(r)||r.basis==='patent_level_only')&&!d)return 2;
 if(REVIEW(r)&&!d)return 3;
 if(d&&d.choice==='image')return 4;
 if(d&&d.choice==='unsure'&&!d.lastcheck)return 5;
 if(needVis(r,d))return 6;
 return 0}
const STAGE={1:'reopened by you',2:'aircraft not decided yet',3:'patent not decided yet',4:'decided “figures are right” before the text rule — decide again',5:'you chose “the text does not settle it” — last check: press 4 again to keep it, or decide',6:'decided — only the visibility answer is missing'};
function filterRows(){
 if(VIEW==='gt'||VIEW==='gtall'){ROWS=DATA.filter(r=>r.key in GTTODO&&(VIEW==='gtall'||!GTDONE(r)||r.key===GTKEEP));if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='watch'){const ks=Object.keys(WATCH);ROWS=DATA.filter(r=>r.key in WATCH).sort((a,b)=>ks.indexOf(a.key)-ks.indexOf(b.key));if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='final'){ROWS=DATA.filter(r=>openStage(r)||r.key===PENDVIS).sort((a,b)=>(openStage(a)||9)-(openStage(b)||9));if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='peraircraft'){ROWS=DATA.filter(r=>((r.kind==='aircraft'&&(REVIEW(r)||r.basis==='patent_level_only'))||r.key in REOPEN)&&(!DEC[r.key]||r.key===PENDVIS));
  ROWS.sort((a,b)=>(b.key in REOPEN)-(a.key in REOPEN));if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='vis'){ROWS=DATA.filter(r=>needVis(r,DEC[r.key])||r.key===PENDVIS);if(CUR>=ROWS.length)CUR=0;return}
 if(LISTMODE()){ROWS=DATA.filter(r=>REVIEW(r)&&AG(r)&&!DEC[r.key]&&!LSKIP[r.key]&&(VIEW==='lgreen'?r.light==='green':r.light!=='green'));CUR=0;return}
 if(VIEW==='unticked'){ROWS=DATA.filter(r=>LSKIP[r.key]&&!DEC[r.key]);if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='recent'){ROWS=DATA.filter(r=>DEC[r.key]&&DEC[r.key].choice).sort((a,b)=>when(DEC[b.key])-when(DEC[a.key]));if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='legacy'){ROWS=DATA.filter(r=>DEC[r.key]&&DEC[r.key].choice==='image');if(CUR>=ROWS.length)CUR=0;return}
 if(VIEW==='side'){ROWS=DATA.filter(r=>REVIEW(r)&&!AG(r)&&!DEC[r.key]).sort((a,b)=>ORDER[a.light]-ORDER[b.light]);if(CUR>=ROWS.length)CUR=0;return}
 if(['green','yellow','red'].includes(VIEW)){ROWS=DATA.filter(r=>REVIEW(r)&&!DEC[r.key]&&r.light===VIEW);if(CUR>=ROWS.length)CUR=0;return}
 ROWS=DATA.filter(r=>VIEW==='all'||(VIEW==='todo'?(REVIEW(r)&&!DEC[r.key])||(SNEED(r)&&firstOfPid(r)):VIEW==='review'?REVIEW(r):VIEW==='known'?!!r.known:VIEW==='aircraft'?r.kind==='aircraft':VIEW==='flags'?!!r.flags:VIEW==='scope'?SNEED(r)&&firstOfPid(r):r.group===VIEW&&!r.known));if(VIEW==='todo')ROWS.sort((a,b)=>ORDER[a.light]-ORDER[b.light]);if(CUR>=ROWS.length)CUR=0}
function tagOf(r){const d=DEC[r.key];return (AG(r)?esc(r.text)+' ✓✓':esc(r.image||'—')+'→'+esc(r.text))+(d?' ✓ '+esc(finalOf(r,d)):r.known?' auto':'')+(r.flags?' ⚑':'')}
function renderList(){const L=document.getElementById('list');L.innerHTML='';ROWS.forEach((r,i)=>{const d=DEC[r.key];const el=document.createElement('div');el.className=(i===CUR?'cur ':'')+(d?'done':'');el.innerHTML=`<span><span class="dot L${r.light}"></span><b>${esc(r.pid)}</b>${r.kind==='aircraft'?' · aircraft '+r.vn:''}<br><span style="font-size:11px">${esc(r.company)}</span></span><span class="tag">${tagOf(r)}</span>`;el.onclick=()=>{CUR=i;render()};L.appendChild(el)});
 const todo=DATA.filter(REVIEW);const n=todo.filter(r=>DEC[r.key]).length;
 const sp=WITH_SCOPE?` · scope ${Object.values(SDEC).filter(x=>x&&x.choice).length} / ${new Set(DATA.filter(r=>r.scope).map(r=>r.pid)).size}`:'';
 const left=c=>todo.filter(r=>(!DEC[r.key]||DEC[r.key].choice==='image')&&r.light===c).length;const nun=Object.keys(LSKIP).filter(k=>!DEC[k]).length;
 document.getElementById('prog').textContent=`🟢 ${left('green')} · 🟡 ${left('yellow')} · 🔴 ${left('red')} left${nun?' · ↩ '+nun+' unticked':''} · ${n} / ${todo.length} architecture rows confirmed${sp} · ${DATA.filter(r=>r.known).length} known-aircraft auto · showing ${ROWS.length}`;
 const cur=L.children[CUR];if(cur)cur.scrollIntoView({block:'nearest'})}
function scopeCard(r){if(!WITH_SCOPE||!r.scope)return'';const sc=r.scope,d=SDEC[r.pid]||{};
 return `<div class="card scope"><h3>Scope of the patent (claim 1) — one answer per patent · confidence ${esc(sc.conf)}</h3>
  <div><span class="big txt">${esc(sc.code)}</span> <span class="def">${esc(sc.label)}${sc.field?' · field: '+esc(sc.field):''}</span></div>
  ${sc.quote?`<blockquote>“${esc(sc.quote)}”</blockquote><div class="def">citation: verbatim words of claim 1${sc.note?' · reader\'s note: '+esc(sc.note):''}</div>`:'<div class="def">no claim text in the export — use the PDF</div>'}
  <div class="decide" style="margin-top:8px"><button data-s="confirm" class="${d.choice==='confirm'?'on':''}" ${sc.code==='NS'?'disabled':''}><kbd>5</kbd>Confirm ${esc(sc.code)} — the claim says it</button>
  <button data-s="other" class="${d.choice==='other'?'on':''}"><kbd>6</kbd>Other:</button>
  <select id="sother">${Object.entries(SLAB).map(([k,v])=>`<option value="${k}" ${d.other===k?'selected':''}>${k} — ${v}</option>`).join('')}</select>
  <button data-s="unsure" class="${d.choice==='unsure'?'on':''}"><kbd>7</kbd>Cannot tell</button>
  <input id="scmt" placeholder="scope comment (optional)" value="${esc(d.comment||'')}"></div></div>`}
// the orange box on aircraft rows: which kind of multi-aircraft patent, and how far the citation reaches
function airBox(r,legacy){if(r.kind!=='aircraft')return'';
 const lead=r.sametype?`This patent draws ${r.nvar} aircraft, all labelled <b>${esc(r.image)}</b> in the figures. Until 2026-09-15 one patent-level decision covered all of them; now each aircraft is decided on its own.`
  :`This patent draws ${r.nvar} aircraft with different figure types (${r.variants.map(esc).join(' · ')}).`;
 const reach=r.basis==='patent_level_only'?' <b>No sentence of the Description cites this aircraft’s figures</b> — the citation is the patent-level one: confirm only if it applies to this aircraft, otherwise 4 (the text does not settle it).'
  :r.basis==='claim'?' The sentence places this aircraft inside the invention; the type-deciding words come from the claim.':'';
 return `<div class="multi">${lead} This row is <b>aircraft ${r.vn}</b> only: its own figures, and the sentences that cite them.${reach} Patent-level reading: ${esc(r.ptext)}${legacy&&legacy.choice?` · <b>your earlier patent-level decision: ${esc(legacy.choice)} ${esc(finalOf(r,legacy)||legacy.other||'')}${legacy.visible?' · visible '+esc(legacy.visible):''}</b>`:''}</div>`}
// shown after a decision whose type differs from the figure type and has no visibility yet
function visBox(r,d){if(!needVis(r,d))return'';const f=finalOf(r,d);
 return `<div class="band yellow" style="margin-top:10px"><b>One more:</b><span>is <b>${esc(f)}</b> (${esc((TYPES[f]||[''])[0])}) visible in the figures? The figures were labelled ${esc(r.image||'—')}.</span>
  <button data-vis="no" style="font:inherit;padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:#fff;cursor:pointer"><kbd>1</kbd> not visible</button>
  <button data-vis="yes" style="font:inherit;padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:#fff;cursor:pointer"><kbd>2</kbd> visible too</button></div>`}
function setVis(r,v){const d=DEC[r.key];if(!d)return;d.visible=v;d.at=new Date().toISOString().slice(0,16);d.ts=Date.now();save();PENDVIS=null;next()}
let GTKEEP=null, GTPICK={};
function gtHTML(r,d){const g=GTTODO[r.key];const pick=GTPICK[r.key]||(d.choice==='gt'?d.other:'')||g.proposed||'';
 const f0=r.figs.find(f=>f.main)||r.figs[0];const rest=r.figs.filter(f=>f!==f0);
 const types=Object.keys(TYPES).filter(t=>t!=='NS');const same=pick&&pick===g.fig;
 return `<div class="band yellow" style="margin-bottom:8px"><b>🎯 why this one</b><span>${esc(g.why)}</span></div>
 <div class="head"><h2>${esc(r.pid)}${r.kind==='aircraft'?' · aircraft '+r.vn+' of '+r.nvar:''}</h2><span>${esc(r.company)} · ${esc(r.year)}</span>${r.pdf?`<a href="${esc(r.pdf)}" target="_blank">PDF ↗</a>`:''}<a href="https://patents.google.com/patent/${esc(r.pid)}/en" target="_blank">Google Patents ↗</a></div>
 <div style="font-size:16px;font-weight:600">${esc(r.title)}</div>${undoBar(r)}
 <div class="side"><div class="sfig">${f0?`<div class="fig" style="border:0;max-width:none">${figHTML(f0)}</div>`:'<p class="help">no approved figure on disk</p>'}${rest.length?`<div class="help">${rest.length} more figure(s) below</div>`:''}</div>
  <div>
   <div class="cite"><div class="vs"><span>your figure label: <span class="big img">${esc(g.fig||'—')}</span></span><span>wizard now: <b>${esc(g.wiz||'—')}</b></span></div>
    ${r.kind==='aircraft'?`<div class="def" style="margin-top:6px">This row is <b>aircraft ${r.vn}</b> only — its own figures are shown. The patent draws ${r.nvar} aircraft.</div>`:''}
    <div class="def" style="margin-top:6px">Automatic text reading (context only, not the answer): <b>${esc(r.text)}</b>${r.quote?` — “${hl(shortQ(r.quote),r.text)}”`:' — no citation found'}</div></div>
   <div style="margin-top:10px"><b>1 · Which architecture is this aircraft?</b> <span class="def">read the whole patent: text and figures</span></div>
   <div class="gtt" style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0">${types.map(t=>`<button data-t="${t}" title="${esc(TYPES[t][1])}" style="font:inherit;padding:6px 10px;border-radius:8px;cursor:pointer;border:2px solid ${t===pick?'var(--acc)':'var(--line)'};background:${t===pick?'#e8efff':'#fff'}"><b>${t}</b> <small class="mut">${esc(TYPES[t][0])}</small></button>`).join('')}</div>
   ${pick&&TYPES[pick]?`<div class="def">${esc(pick)} = ${esc(TYPES[pick][1])}</div>`:''}
   <div style="margin-top:10px"><b>2 · Can the figures show ${esc(pick||'it')}?</b> ${same?'<span class="def">same as your figure label, so yes</span>':''}</div>
   <div class="pick2"><button data-g="yes" class="pt ${d.choice==='gt'&&d.visible==='yes'?'on':''}" ${pick?'':'disabled'}><kbd>1</kbd> Visible in the figures<b>${esc(pick||'—')}</b><small>the drawings are enough to see it</small></button>
    <button data-g="no" class="pi ${d.choice==='gt'&&d.visible==='no'?'on':''}" ${pick&&!same?'':'disabled'}><kbd>2</kbd> Not visible in the figures<b>${esc(pick||'—')}</b><small>only the rest of the patent shows it</small></button></div>
   <div class="decide"><button data-g="unsure" class="${d.choice==='gt_unsure'?'on':''}"><kbd>3</kbd>The patent does not settle it</button>
    <input id="cmt" placeholder="comment (optional)" value="${esc(d.comment||'')}"></div></div></div>
 ${rest.length?`<div class="figs small">${rest.map(f=>`<div class="fig">${figHTML(f)}</div>`).join('')}</div>`:''}
 <p class="help">click a type (it starts on the proposal) · 1 visible · 2 not visible · 3 the patent does not settle it · ←/→ navigate · click a figure to zoom · Export CSV when done</p>`}
function decideGT(r,g){const pick=GTPICK[r.key]||(DEC[r.key]&&DEC[r.key].choice==='gt'?DEC[r.key].other:'')||GTTODO[r.key].proposed||'';
 const cm=document.getElementById('cmt');const base={comment:cm?cm.value:'',at:new Date().toISOString().slice(0,16),ts:Date.now(),n:nextN()};
 if(g==='unsure')DEC[r.key]=Object.assign({choice:'gt_unsure',other:'',visible:''},base);
 else{if(!pick)return;const vis=pick===GTTODO[r.key].fig?'yes':g;DEC[r.key]=Object.assign({choice:'gt',other:pick,visible:vis},base)}
 save();delete GTPICK[r.key];GTKEEP=null;next()}
function render(){filterRows();renderList();const P=document.getElementById('panel');const nopen=DATA.filter(openStage).length;const ngt=DATA.filter(r=>r.key in GTTODO&&!GTDONE(r)).length;document.getElementById('prog').textContent='🎯 '+ngt+' / '+Object.keys(GTTODO).length+' ground truth to decide · 🏁 '+nopen+' still open · '+document.getElementById('prog').textContent;
 if(LISTMODE())return renderBatch();
 const r=ROWS[CUR];if(!r&&VIEW==='gt'){P.innerHTML='<p class="help"><b>Every ground-truth row is decided — press Export CSV.</b></p>';return}
 if(!r){P.innerHTML='<p class="help">Nothing in this view.'+(VIEW==='final'?' <b>The final pass is complete — press Export CSV.</b>':'')+(VIEW==='peraircraft'?' Every aircraft row is decided — next: 👁 visibility still missing, then Export CSV.':'')+'</p>';return}
 const d=DEC[r.key]||{};const other=Object.keys(TYPES).filter(t=>t!=='NS');const legacy=r.kind==='aircraft'?(DEC[r.pid]||BASE[r.pid]):null;
 if(VIEW==='gt'||VIEW==='gtall'){P.innerHTML=gtHTML(r,d);bind(r,P);
  P.querySelectorAll('.gtt button').forEach(b=>b.onclick=()=>{GTPICK[r.key]=b.dataset.t;GTKEEP=r.key;render()});
  P.querySelectorAll('button[data-g]').forEach(b=>b.onclick=()=>decideGT(r,b.dataset.g));return}
 const stg=openStage(r);const wb=(r.key in WATCH)?`<div class="band yellow" style="margin-bottom:8px"><b>🔎 recheck</b><span>${esc(WATCH[r.key])}</span></div>`:'';const sb=wb+(stg?`<div class="band grey" style="margin-bottom:8px"><b>Final pass · step ${stg}</b><span>${STAGE[stg]}</span></div>`:'');
 if(!AG(r)){P.innerHTML=sb+sideHTML(r,d,other,legacy);const vb=visBox(r,d);if(vb)P.querySelector('.side > div').insertAdjacentHTML('afterbegin',vb);bind(r,P);return}
 P.innerHTML=sb+`<div class="head"><h2>${esc(r.pid)}${r.kind==='aircraft'?' · aircraft '+r.vn+' of '+r.nvar:''}</h2><span>${esc(r.company)}</span><span class="mut">${esc(r.realname||r.name)} · ${esc(r.year)} · ${r.nvar>1?r.nvar+' aircraft in this patent':'1 aircraft'}</span><a href="${esc(r.pdf)}" target="_blank">PDF ↗</a></div>
 <div class="mut" style="font-size:13px">${esc(r.title)} — <i>${esc(r.assignee)}</i></div>${undoBar(r)}
 <div class="cards" style="margin-top:10px">
  <div class="band ${r.light}"><span class="dot L${r.light}" style="width:14px;height:14px"></span><b>${LNAME[r.light]}</b><span>${esc(r.why)}</span></div>
  <div class="cite"><div class="vs"><span>figures: <span class="big img">${esc(r.image||'—')}</span></span><span>text: <span class="big txt">${esc(r.text)}</span> <span class="def">${esc((TYPES[r.text]||[''])[0])} · confidence ${esc(r.conf)}</span></span></div>
   ${r.quote?`<div class="q">“${hl(r.quote,r.text)}”</div><div class="def">${r.qcheck==='verbatim'?'<b style="color:var(--ok)">verbatim</b>':r.qcheck==='partial'?'<b style="color:var(--warn)">partly verbatim</b>':'<b style="color:var(--warn)">not found verbatim</b>'}${r.qsec?' · '+esc(r.qsec):''} · <mark class="t">green</mark> = words of ${esc(r.text)}, <mark class="o">amber</mark> = words of other types${r.note?' · note: '+esc(r.note):''}</div>`:'<div class="def">no citation</div>'}
   ${r.image&&TYPES[r.image]?`<div class="def">figures ${esc(r.image)} = ${esc(TYPES[r.image][0])}: ${esc(TYPES[r.image][1])}</div>`:''}
   ${TYPES[r.text]?`<div class="def">text ${esc(r.text)} = ${esc(TYPES[r.text][0])}: ${esc(TYPES[r.text][1])}</div>`:''}
  ${r.known?`<div class="def" style="color:var(--ok)">cleared automatically: known aircraft ${esc(r.known)}</div>`:''}</div>
  ${airBox(r,legacy)}
  ${r.flags?`<div class="flag">⚑ ${esc(r.flags)}</div>`:''}
  ${visBox(r,d)?`<div style="grid-column:1/3">${visBox(r,d)}</div>`:''}
  <div class="decide">
   ${AG(r)?`<button data-c="confirm" class="${d.choice==='confirm'?'on':''}"><kbd>1</kbd>Confirm ${esc(r.text)} — ${r.basis==='patent_level_only'?'the patent-level citation applies to this aircraft':'the citation states it'}</button>`:
   `<button data-c="image" class="${d.choice==='image'?'on':''}" ${r.image?'':'disabled'}><kbd>1</kbd>Keep image label${r.image?' ('+esc(r.image)+')':' (none — pick 2 or 3)'}</button>
   <button data-c="text" class="${d.choice==='text'?'on':''}" ${r.text==='NS'?'disabled':''}><kbd>2</kbd>Take text label (${esc(r.text)})</button>`}
   <button data-c="other" class="${d.choice==='other'?'on':''}"><kbd>3</kbd>Other:</button>
   <select id="other">${other.map(t=>`<option value="${t}" ${d.other===t?'selected':''}>${t} — ${TYPES[t][0]}</option>`).join('')}</select>
   <button data-c="unsure" class="${d.choice==='unsure'?'on':''}"><kbd>4</kbd>The text does not settle it</button>
   <button data-c="ns" class="${d.choice==='ns'?'on':''}"><kbd>5</kbd>The text says nothing about the architecture</button>
   <input id="cmt" placeholder="comment (optional)" value="${esc(d.comment||'')}">
  </div>${scopeCard(r)}</div>
 <div class="figs small">${r.figs.map(f=>`<div class="fig ${f.main?'main':''}"><img src="${esc(f.src)}" style="transform:rotate(${f.rot}deg)" loading="lazy"><small>${f.main?'MAIN · ':''}${f.arch?'aircraft '+f.arch+' · ':''}${esc(f.state)} ${esc(f.per)} ${f.rot?'· rotated '+f.rot+'°':''}</small></div>`).join('')||'<p class="help">no approved figure on disk</p>'}</div>
 <p class="help">Read the highlighted citation, then: 1 confirm · 3 the text states another type · 4 the text does not settle it · 5 the text says nothing about the architecture${WITH_SCOPE?' · 5 confirm scope · 6 scope other · 7 scope cannot tell':''} · ←/→ or Enter = next · click a figure to zoom. Decisions are saved in this browser; press Export CSV when done (goes to Downloads).</p>`;
 bind(r,P);
}
const SHRINKING=['gt','todo','side','unticked','green','yellow','red','scope','legacy','peraircraft','vis','final'];
// change a decision you already made: clear it (the patent goes back into the lists) or pick another button
// order of decisions: exact time for new ones, the saved minute for older ones
const when=d=>(d.n||0)*1e13+(d.ts||Date.parse(d.at||'')||0);
// a running number, so decisions made in the same millisecond still keep their order
const nextN=()=>1+Object.values(DEC).reduce((m,d)=>Math.max(m,(d&&d.n)||0),0);
function undo(r){delete DEC[r.key];delete LSKIP[r.key];save();saveSkip();render()}
function undoBar(r){const d=DEC[r.key];if(!d||!d.choice)return'';
 return `<div class="band grey" style="margin-top:8px"><b>Your decision:</b><span>${esc(d.choice)}${d.visible?' · visible in figures: '+esc(d.visible):''}${finalOf(r,d)?' → '+esc(finalOf(r,d)):''} · ${esc(d.at||'')}</span><button class="undo" style="margin-left:auto;font:inherit;padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:#fff;cursor:pointer">↺ clear my decision</button><span class="def">or just press another button</span></div>`}
function next(){if(VIEW==='recent'){const k=ROWS[CUR]&&ROWS[CUR].key;filterRows();CUR=Math.max(0,ROWS.findIndex(r=>r.key===k));renderList();render();return}
 if(!SHRINKING.includes(VIEW)){CUR=Math.min(CUR+1,ROWS.length-1)}render()}
// visible = does the drawing show the architecture the text states? (text = ground truth, 2026-09-14)
function decide(r,c,v){const o=document.getElementById('other');
 // "the text states another type" equal to the figure type is visible by construction; a different one asks
 const vis=c==='confirm'?'yes':c==='other'&&o.value===r.image?'yes':(v||'');
 DEC[r.key]={choice:c,other:c==='other'?o.value:'',visible:vis,comment:document.getElementById('cmt').value,at:new Date().toISOString().slice(0,16),ts:Date.now(),n:nextN(),lastcheck:true};save();
 if(needVis(r,DEC[r.key])){PENDVIS=r.key;render();return}
 PENDVIS=null;next()}
function decideScope(r,c){if(!r.scope)return;if(c==='confirm'&&r.scope.code==='NS')return;const o=document.getElementById('sother'),m=document.getElementById('scmt');
 SDEC[r.pid]={choice:c,other:c==='other'?o.value:'',comment:m?m.value:'',at:new Date().toISOString().slice(0,16)};save();next()}
document.getElementById('zoom').onclick=e=>e.currentTarget.style.display='none';
document.getElementById('view').onchange=e=>{VIEW=e.target.value;CUR=0;render()};
document.getElementById('last').onclick=()=>{VIEW='recent';document.getElementById('view').value='recent';CUR=0;render();window.scrollTo(0,0)};
document.getElementById('jump').addEventListener('keydown',function(e){if(e.key!=='Enter')return;e.stopPropagation();const q=this.value.trim().toUpperCase();if(!q)return;
 const hit=DATA.find(r=>r.key.toUpperCase().includes(q));if(!hit){alert(q+' is not in this review');return}
 VIEW=(hit.key in GTTODO)?'gtall':REVIEW(hit)?'review':'all';document.getElementById('view').value=VIEW;filterRows();CUR=Math.max(0,ROWS.indexOf(hit));this.blur();render();window.scrollTo(0,0)});
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT'){if(e.key==='Enter'){e.target.blur()}else return}
 if(LISTMODE()){if(e.key==='Enter'||e.key===' '){e.preventDefault();confirmBatch()}return}
 const r=ROWS[CUR];if(!r)return;
 if((VIEW==='gt'||VIEW==='gtall')&&r.key in GTTODO){if(e.key==='1')return decideGT(r,'yes');if(e.key==='2')return decideGT(r,'no');if(e.key==='3')return decideGT(r,'unsure');
  if(e.key==='ArrowRight'||e.key==='Enter'){CUR=Math.min(CUR+1,ROWS.length-1);render()}else if(e.key==='ArrowLeft'){CUR=Math.max(CUR-1,0);render()}else if(e.key==='Escape')document.getElementById('zoom').style.display='none';return}
 if(needVis(r,DEC[r.key])&&(e.key==='1'||e.key==='2')){setVis(r,e.key==='1'?'no':'yes');return}
 if(e.key===' '){e.preventDefault();if(AG(r))decide(r,'confirm');return}
 if(e.key==='1'&&AG(r))decide(r,'confirm');else if(e.key==='1'&&!AG(r)&&r.text!=='NS')decide(r,'text','no');else if(e.key==='2'&&!AG(r)&&r.text!=='NS')decide(r,'text','yes');else if(e.key==='3')decide(r,'other');else if(e.key==='4')decide(r,'unsure');else if(e.key==='5')decide(r,'ns');
 else if(WITH_SCOPE&&e.key==='5')decideScope(r,'confirm');else if(WITH_SCOPE&&e.key==='6')decideScope(r,'other');else if(WITH_SCOPE&&e.key==='7')decideScope(r,'unsure');
 else if(e.key==='ArrowRight'||e.key==='Enter'){CUR=Math.min(CUR+1,ROWS.length-1);render()}else if(e.key==='ArrowLeft'){CUR=Math.max(CUR-1,0);render()}else if(e.key==='Escape')document.getElementById('zoom').style.display='none'});
const HDR=['patent_id','variant_id','group','image_label','text_label','decision','final_label','visible_in_figures','comment','decided_at','scope_llm','scope_decision','scope_final','scope_comment','scope_decided_at'];
function scopeFinal(r,sd){if(!sd||!sd.choice)return'';return sd.choice==='confirm'?(SLAB[r.scope.code]||''):sd.choice==='other'?(SLAB[sd.other]||''):''}
document.getElementById('exp').onclick=()=>{const q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const lines=[HDR.join(',')];const scoped=new Set();
 DATA.forEach(r=>{const d=DEC[r.key];const sd=SDEC[r.pid];const addScope=WITH_SCOPE&&r.scope&&sd&&sd.choice&&!scoped.has(r.pid);
  if(!(d&&d.choice)&&!addScope)return;if(addScope)scoped.add(r.pid);
  const a=d&&d.choice?[r.group,r.image,r.text,d.choice,finalOf(r,d),d.visible||(d.choice==='confirm'?'yes':''),d.comment||'',d.at||'']:['','','','','','','',''];
  const s=addScope?[r.scope.label,sd.choice,scopeFinal(r,sd),sd.comment||'',sd.at||'']:['','','','',''];
  lines.push([r.pid,r.kind==='aircraft'&&d&&d.choice?r.key:'',...a,...s].map(q).join(','))});
 saveToFolder(new Blob([lines.join('\n')],{type:'text/csv'}),'architecture_review_decisions.csv')};
function parseCSV(t){const out=[];let row=[],f='',Q=false;for(let i=0;i<t.length;i++){const c=t[i];
 if(Q){if(c==='"'){if(t[i+1]==='"'){f+='"';i++}else Q=false}else f+=c}else if(c==='"')Q=true;else if(c===','){row.push(f);f=''}
 else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;row.push(f);out.push(row);row=[];f=''}else f+=c}if(f||row.length){row.push(f);out.push(row)}return out}
const SREV=Object.fromEntries(Object.entries(SLAB).map(([k,v])=>[v,k]));
document.getElementById('imp').onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();rd.onload=()=>{const rows=parseCSV(rd.result).filter(c=>c.some(x=>x));const h=rows.shift();let n=0,ns=0;
 const old=!h.includes('variant_id');
 rows.forEach(c=>{const o=old?{patent_id:c[0],decision:c[4],final_label:c[5],comment:c[6],decided_at:c[7]}:Object.fromEntries(h.map((k,i)=>[k,c[i]]));
  if(!o.patent_id)return;
  if(o.decision){const key=o.variant_id||o.patent_id;DEC[key]={choice:o.decision,other:(o.decision==='other'||o.decision==='gt')?o.final_label:'',visible:o.visible_in_figures||'',comment:o.comment||'',at:o.decided_at||''};n++}
  if(o.scope_decision){SDEC[o.patent_id]={choice:o.scope_decision,other:o.scope_decision==='other'?(SREV[o.scope_final]||''):'',comment:o.scope_comment||'',at:o.scope_decided_at||''};ns++}});
 save();render();alert(n+' architecture and '+ns+' scope decisions imported')};rd.readAsText(f)};
document.getElementById('clr').onclick=()=>{if(confirm('Clear every decision saved in this browser?')){DEC={};SDEC={};LSKIP={};save();saveSkip();render()}};
render();
</script></body></html>"""
out = (PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
           .replace("__TYPES__", json.dumps(TYPES, ensure_ascii=False))
           .replace("__KW__", json.dumps(KW, ensure_ascii=False))
           .replace("__BASE__", json.dumps(base_dec, ensure_ascii=False))
           .replace("__REOPEN__", json.dumps(REOPEN))
           .replace("__WATCH__", json.dumps(WATCH))
           .replace("__GTTODO__", json.dumps(GTTODO, ensure_ascii=False))
           .replace("__WITH_SCOPE__", "true" if WITH_SCOPE else "false"))
OUT.write_text(out, encoding="utf-8")
print("wrote", OUT, f"{OUT.stat().st_size/1024:.0f} KB")
