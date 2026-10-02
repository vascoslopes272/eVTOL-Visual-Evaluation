#!/usr/bin/env python3
"""Merge the annotator's decisions from 03b_architecture_review.html (architecture_review_decisions.csv) into
the text-side readings and write the columns the analysis uses.

    python apply_architecture_review.py [decisions.csv]

Writes (1639_LABELLED/)
  text_architecture/architecture_text_final.csv            one row per patent (695) — unchanged shape
  text_architecture/architecture_text_final_variants.csv   one row per aircraft (the 805 primary approved variants)
  text_scope/scope_final.csv                                one row per patent (695)

The TEXT is the ground truth (user, 2026-09-14). arch_final is the type the patent's own words state;
the figure label is kept beside it, and visible_in_figures says whether the drawings show that type
(yes / no / blank when not asked). A disagreement is a visibility finding, not an error.

architecture provenance
  confirmed          image and text agree AND the annotator confirmed the citation states it (visible = yes)
  known_aircraft     depicted aircraft is a gazetteer-named model whose public architecture equals the label
  adjudicated_text   the citation states it; visible_in_figures = yes / no
  adjudicated_other  the text states a different type than the reader proposed
  adjudicated_image  LEGACY: chosen before the text rule — re-decide in the page (counted and warned)
  not_stated         also: the reviewer pressed "the text does not state an architecture" (decision ns)
  not_stated         text silent; no citation exists; image label stands (arch_final = image label)
  per_aircraft       (patent file only) the patent draws aircraft of different types; see the variants file
  unsure             annotator could not tell — arch_final blank
  pending            not yet confirmed (arch_final blank)

scope provenance
  user_sample        one of the 100 blind-sample patents: the reviewer's own reading of claim 1
  sbert_validated    SBERT passed the pre-registered bar on the sample (scope_sample_evaluation.csv)
  llm_confirmed / llm_overruled   the claim-1 citation confirmed / replaced in the 03b page
  unsure / pending
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED")
TA = ROOT / "text_architecture"
TS = ROOT / "text_scope"
# review-page exports live in 1639_LABELLED/review_decisions (2026-09-14); Downloads is the old fallback
RD = ROOT / "review_decisions"
_dec_default = next((p for p in [RD / "architecture_review_decisions.csv",
                                 Path.home() / "Downloads" / "architecture_review_decisions.csv"] if p.exists()),
                    RD / "architecture_review_decisions.csv")
dec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _dec_default
SAMPLE_DEC = [RD / "scope_sample_decisions.csv", TS / "scope_sample_decisions.csv",
              Path.home() / "Downloads" / "scope_sample_decisions.csv"]


def s(v):
    return "" if pd.isna(v) else str(v)


allrows = pd.read_excel(TA / "architecture_text_vs_image_20260909.xlsx", sheet_name="ALL_695")
# per-aircraft readings: the 18 multi-type patents (2026-09-11) + the 50 same-type multi-aircraft patents (2026-09-15).
# Every patent in either file is decided per aircraft; a patent-level decision no longer covers its aircraft.
var = pd.concat([pd.read_csv(TA / "variant_reading" / f) for f in
                 ("architecture_text_variants_20260911.csv", "architecture_text_variants_sametype_20260915.csv")], ignore_index=True)
if "basis" not in var.columns:
    var["basis"] = "aircraft"
var["basis"] = var["basis"].fillna("aircraft")
assert not var.variant_id.duplicated().any()
MULTI = set(var.patent_id)
idn = pd.read_excel(ROOT / "joined" / "aircraft_identity_ALL.xlsx", sheet_name="Identity")[["patent_id","aircraft_name","aircraft_name_source","scope","scope_source"]].set_index("patent_id")
_kn_raw = pd.read_csv(TA / "known_aircraft_architecture.csv")
_mixed = {c for c, g in _kn_raw.groupby("company") if g.known_type.nunique() > 1}
known = _kn_raw.drop_duplicates("aircraft_name").set_index("aircraft_name")


def known_auto(pid, img, txt):
    """Only exempt when the figure label, the text reading (or silence) and a documented aircraft of
    that assignee agree, AND the assignee's documented aircraft do not differ in architecture."""
    if pid not in idn.index or idn.at[pid, "aircraft_name_source"] != "gazetteer": return False
    nm = idn.at[pid, "aircraft_name"]
    if nm not in known.index or known.at[nm, "confidence"] != "high": return False
    if known.at[nm, "company"] in _mixed: return False
    return img == known.at[nm, "known_type"] and txt in (img, "NS")


cols = ["patent_id", "variant_id", "decision", "final_label", "visible_in_figures", "comment", "decided_at",
        "scope_decision", "scope_final", "scope_comment", "scope_decided_at"]
dec = pd.read_csv(dec_path, dtype=str) if dec_path.exists() else pd.DataFrame(columns=cols)
for c in cols:
    if c not in dec.columns:
        dec[c] = None
arch_dec = dec[dec.decision.notna() & (dec.decision.astype(str).str.strip() != "")]
pat_dec = arch_dec[arch_dec.variant_id.isna() | (arch_dec.variant_id.astype(str).str.strip() == "")].drop_duplicates("patent_id", keep="last").set_index("patent_id")
var_dec = arch_dec[arch_dec.variant_id.notna() & (arch_dec.variant_id.astype(str).str.strip() != "")].drop_duplicates("variant_id", keep="last").set_index("variant_id")
sc_dec = dec[dec.scope_decision.notna() & (dec.scope_decision.astype(str).str.strip() != "")].drop_duplicates("patent_id", keep="last").set_index("patent_id")
print(f"decisions read from {dec_path}: {len(pat_dec)} patent rows, {len(var_dec)} aircraft rows, {len(sc_dec)} scope")


def ruling(d, img, txt, basis="patent"):
    ch = d.decision
    final = {"confirm": txt, "image": img, "text": txt, "other": s(d.final_label) or None, "unsure": None,
             # the reviewer found the text silent: same treatment as the reader's own not-stated rows
             "ns": img}.get(ch)
    prov = {"confirm": "confirmed", "unsure": "unsure", "ns": "not_stated"}.get(ch, "adjudicated_" + str(ch))
    if ch == "confirm" and basis == "patent_level_only":
        # no sentence cites this aircraft's figures: the reviewer confirmed that the patent-level citation applies to it
        prov = "confirmed_patent_level"
    visible = "yes" if ch == "confirm" else s(d.get("visible_in_figures", ""))
    if not visible and final and img and final == img and ch != "ns":
        # the ground truth equals the figure label, so the figures show it (2026-09-15, comparison + visibility split)
        visible = "yes"
    return final, prov, visible


_legacy = int((arch_dec.decision == "image").sum())
if _legacy:
    print(f"⚠  {_legacy} decision(s) still say 'figures are right' (chosen before the text-ground-truth rule); "
          f"re-decide them in the page view '⚠ decided figures are right'")


# ---- per aircraft (multi-type patents) --------------------------------------------------------------
vfinal = {}
for v in var.itertuples():
    img, txt = (s(v.image_type) or None), s(v.text_type)
    if v.variant_id in var_dec.index:
        final, prov, vis = ruling(var_dec.loc[v.variant_id], img, txt, s(v.basis))
    elif txt == "NS" and not s(v.flags):
        final, prov, vis = img, "not_stated", ""
    else:
        final, prov, vis = None, "pending", ""
    vfinal[v.variant_id] = dict(arch_final=final, provenance=prov, visible_in_figures=vis, text_label=txt, text_confidence=s(v.confidence),
                                quote=s(v.quote), flags=s(v.flags), citation_basis=s(v.basis))

# ---- per patent ---------------------------------------------------------------------------------------
out = []
for r in allrows.itertuples():
    pid, img, txt, bucket = r.patent_id, r.image_label, r.text_label, str(r.bucket)
    img = None if pd.isna(img) else img
    d = pat_dec.loc[pid] if pid in pat_dec.index else None
    if pid in MULTI:
        vs = [vfinal[k] for k in sorted(vfinal) if k.rsplit("_", 1)[0] == pid]
        done = all(x["provenance"] != "pending" for x in vs)
        final = "|".join(sorted({x["arch_final"] for x in vs if x["arch_final"]})) if done else None
        prov = "per_aircraft" if done else "pending"
        vis = "|".join(x["visible_in_figures"] or "-" for x in vs) if done else ""
    elif d is not None:
        final, prov, vis = ruling(d, img, txt, "patent")
    elif known_auto(pid, img, txt):
        final, prov, vis = img, "known_aircraft", "yes"
    elif bucket.startswith("3"):
        final, prov, vis = img, "not_stated", ""
    else:
        final, prov, vis = None, "pending", ""
    out.append(dict(patent_id=pid, image_label=img, text_label=txt, text_confidence=r.confidence,
                    arch_final=final, provenance=prov, visible_in_figures=vis,
                    review_comment=(s(d.comment) if d is not None else ""),
                    decided_at=(s(d.decided_at) if d is not None else "")))
df = pd.DataFrame(out)
df.to_csv(TA / "architecture_text_final.csv", index=False)
print("patents:", df.provenance.value_counts().to_dict())

# ---- one row per primary approved aircraft ------------------------------------------------------------
# The image labels are FROZEN as they stood before the 2026-09-15 wizard relabel session: the comparison measures the
# figure-based labels the annotator made BEFORE seeing the ground truth, so corrections made after it must not leak in.
FROZEN = TA / "image_labels_frozen_20260915.csv"
prim = pd.read_csv(FROZEN, dtype=str, keep_default_na=False).rename(columns={"image_label_frozen": "topType"})
bypat = df.set_index("patent_id")
vrows = []
for v in prim.itertuples():
    if v.variant_id in vfinal:
        x = vfinal[v.variant_id]
        vrows.append(dict(variant_id=v.variant_id, patent_id=v.patent_id, image_label=s(v.topType), level="aircraft", **x))
    else:
        p = bypat.loc[v.patent_id]
        vrows.append(dict(variant_id=v.variant_id, patent_id=v.patent_id, image_label=s(v.topType), level="patent",
                          arch_final=p.arch_final, provenance=p.provenance, visible_in_figures=p.visible_in_figures,
                          text_label=p.text_label,
                          text_confidence=p.text_confidence, quote="", flags="", citation_basis="patent"))
vdf = pd.DataFrame(vrows)
vdf.to_csv(TA / "architecture_text_final_variants.csv", index=False)
print("aircraft:", len(vdf), vdf.provenance.value_counts().to_dict())

# ---- scope --------------------------------------------------------------------------------------------
llm = pd.read_csv(TS / "scope_llm_20260911.csv").set_index("patent_id") if (TS / "scope_llm_20260911.csv").exists() else None
sample_path = next((p for p in SAMPLE_DEC if p.exists()), None)
sample = pd.read_csv(sample_path).drop_duplicates("patent_id", keep="last").set_index("patent_id") if sample_path else None
ev = TS / "scope_sample_evaluation.csv"
sbert_ok = False
if ev.exists():
    e = pd.read_csv(ev).set_index("method")
    sbert_ok = "sbert_pipeline" in e.index and str(e.at["sbert_pipeline", "passes_bar"]).lower() == "true"
srows = []
for pid in allrows.patent_id:
    if sample is not None and pid in sample.index and s(sample.at[pid, "decision"]) != "U":
        final, prov = s(sample.at[pid, "scope_label"]), "user_sample"
    elif sbert_ok and pid in idn.index and s(idn.at[pid, "scope"]):
        final, prov = s(idn.at[pid, "scope"]), "sbert_validated"
    elif pid in sc_dec.index:
        d = sc_dec.loc[pid]
        final = s(d.scope_final) or None
        prov = {"confirm": "llm_confirmed", "other": "llm_overruled", "unsure": "unsure"}.get(d.scope_decision, "pending")
    else:
        final, prov = None, "pending"
    srows.append(dict(patent_id=pid, scope_final=final, provenance=prov,
                      scope_llm=s(llm.at[pid, "scope_llm"]) if llm is not None and pid in llm.index else "",
                      scope_sbert=s(idn.at[pid, "scope"]) if pid in idn.index else ""))
sdf = pd.DataFrame(srows)
sdf.to_csv(TS / "scope_final.csv", index=False)
print("scope:", sdf.provenance.value_counts().to_dict(), "| sample decisions:", sample_path, "| SBERT passed the bar:", sbert_ok)
