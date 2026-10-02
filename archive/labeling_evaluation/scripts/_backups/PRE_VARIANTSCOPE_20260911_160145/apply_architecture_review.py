#!/usr/bin/env python3
"""Merge the annotator's adjudication (architecture_review_decisions.csv, exported by
03b_architecture_review.html) into the text-side reading (results.csv) and write
text_architecture/architecture_text_final.csv — the column the analysis uses.

provenance values
  confirmed          image and text agree AND the annotator confirmed the citation states it
  known_aircraft     depicted aircraft is a gazetteer-named model whose public architecture equals the label
  adjudicated_image / adjudicated_text / adjudicated_other   annotator's ruling (disagreements, or an
                     agreement the annotator overruled from the citation)
  not_stated         text silent; no citation exists; image label stands (arch_final = image label)
  unsure             annotator could not tell — arch_final blank
  pending            not yet confirmed (arch_final blank)
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED")
TA = ROOT / "text_architecture"
dec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "architecture_review_decisions.csv"

allrows = pd.read_excel(TA / "architecture_text_vs_image_20260909.xlsx", sheet_name="ALL_695")
idn = pd.read_excel(ROOT / "joined" / "aircraft_identity_ALL.xlsx", sheet_name="Identity")[["patent_id","aircraft_name","aircraft_name_source"]].set_index("patent_id")
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
dec = pd.read_csv(dec_path) if dec_path.exists() else pd.DataFrame(columns=["patent_id","decision","final_label","comment","decided_at"])
dec = dec.drop_duplicates("patent_id", keep="last").set_index("patent_id")
print(f"decisions read: {len(dec)} from {dec_path}")

out = []
for r in allrows.itertuples():
    pid, img, txt, bucket = r.patent_id, r.image_label, r.text_label, str(r.bucket)
    img = None if pd.isna(img) else img
    d = dec.loc[pid] if pid in dec.index else None
    if d is not None:
        ch = d.decision
        final = {"confirm": txt, "image": img, "text": txt, "other": d.final_label, "unsure": None}.get(ch)
        prov = {"confirm": "confirmed", "unsure": "unsure"}.get(ch, "adjudicated_" + ch)
    elif known_auto(pid, img, txt):
        final, prov = img, "known_aircraft"
    elif bucket.startswith("3"):
        final, prov = img, "not_stated"
    else:
        final, prov = None, "pending"
    out.append(dict(patent_id=pid, image_label=img, text_label=txt, text_confidence=r.confidence,
                    arch_final=final, provenance=prov,
                    review_comment=(d.comment if d is not None and not pd.isna(d.comment) else ""),
                    decided_at=(d.decided_at if d is not None else "")))
df = pd.DataFrame(out)
df.to_csv(TA / "architecture_text_final.csv", index=False)
print(df.provenance.value_counts().to_string())
n_done = (df.provenance != "pending").sum()
print(f"arch_final set for {df.arch_final.notna().sum()} / {len(df)}; pending {len(df)-n_done}")
