#!/usr/bin/env python3
"""Build the single-file browser page for adjudicating the text-vs-image architecture type.

Input : 1639_LABELLED/text_architecture/architecture_text_vs_image_<date>.xlsx (sheets REVIEW_disagree,
        agree_lowconf, not_stated) + joined/master_figures.xlsx (approved figures, original paths + rotation)
Output: 1639_LABELLED/text_architecture/03b_architecture_review.html  (open with file://, no network needed)

Decisions persist in localStorage (key archreview_v1) and are exported as
architecture_review_decisions.csv (Downloads).  Apply them with apply_architecture_review.py.
"""
import json, sys, html
from pathlib import Path
import pandas as pd

ROOT = Path("/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/1639_LABELLED")
XLSX = ROOT / "text_architecture" / "architecture_text_vs_image_20260909.xlsx"
OUT  = ROOT / "text_architecture" / "03b_architecture_review.html"

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

def s(v):
    return "" if pd.isna(v) else str(v)

allr = pd.read_excel(XLSX, sheet_name="ALL_695")
def grp(b):
    b = str(b)
    return {"0": "agree", "1": "disagree", "2": "lowconf", "3": "notstated"}[b[0]]
allr["group"] = allr.bucket.map(grp)
qc = pd.read_csv(ROOT / "text_architecture" / "quote_check.csv").set_index("pid")
idn = pd.read_excel(ROOT / "joined" / "aircraft_identity_ALL.xlsx", sheet_name="Identity")[["patent_id","aircraft_name","aircraft_name_source"]].set_index("patent_id")
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

# per-variant architecture types, for the patents that draw more than one aircraft
_ml = pd.read_excel(ROOT / "joined" / "master_labels.xlsx")
_prim = _ml[(_ml.is_primary == True) & (_ml.is_approved == True)]
VARIANTS = {pid: [str(v) for v in g.topType.tolist()] for pid, g in _prim.groupby("patent_id")}
rows = allr
assert rows.patent_id.is_unique
mf = pd.read_excel(ROOT / "joined" / "master_figures.xlsx")
mf = mf[(mf.status == "approved") & (mf.file_exists == True)]
figs = {}
for pid, g in mf.groupby("patent_id"):
    g = g.sort_values(["is_main", "arch"], ascending=[False, True])
    figs[pid] = [{"src": "file://" + str(r.image_path), "rot": int(r.rotation_deg or 0),
                  "arch": None if pd.isna(r.arch) else int(r.arch), "main": bool(r.is_main == 1),
                  "state": s(r.acState), "per": s(r.per)} for r in g.itertuples()]

data = []
for r in rows.itertuples():
    data.append({
        "pid": r.patent_id, "group": r.group,
        "image": s(r.image_label), "text": s(r.text_label), "conf": s(r.confidence),
        "quote": s(r.quote), "note": s(r.note),
        "company": s(r.company_canonical), "name": s(r.aircraft_name_final),
        "year": "" if pd.isna(r.priority_year) else int(r.priority_year),
        "title": s(r.title), "assignee": s(r.assignee), "nvar": int(r.n_var) if not pd.isna(r.n_var) else 1,
        "pdf": s(r.pdf_link), "figs": figs.get(r.patent_id, []),
        "qcheck": s(qc.quote_check.get(r.patent_id, "")), "qsec": s(qc.quote_section.get(r.patent_id, "")),
        "known": known_auto(r.patent_id, s(r.image_label), s(r.text_label)) or "",
        "variants": VARIANTS.get(r.patent_id, []),
        "realname": s(idn.aircraft_name.get(r.patent_id, "")) if (r.patent_id in idn.index and idn.aircraft_name_source.get(r.patent_id) == "gazetteer") else "",
    })
missing = [d["pid"] for d in data if not d["figs"]]
from collections import Counter
print("rows:", len(data), Counter(d["group"] for d in data), "known-auto:", sum(1 for d in data if d["known"]), "no figures:", missing)

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>03b — architecture type adjudication</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1c2128;--mut:#6b7280;--line:#e3e6ea;--acc:#2456c7;--ok:#1a8f4a;--warn:#c2410c;--img:#7c3aed;--txt:#0e7490}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 Inter,system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{display:flex;gap:14px;align-items:center;padding:8px 14px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header h1{font-size:15px;margin:0 10px 0 0}header select,header button,header input{font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:#fff}
header button{cursor:pointer}#prog{color:var(--mut);font-size:13px}
main{display:grid;grid-template-columns:260px 1fr;min-height:calc(100vh - 46px)}
#list{border-right:1px solid var(--line);background:#fff;overflow:auto;max-height:calc(100vh - 46px)}
#list div{padding:5px 10px;border-bottom:1px solid #f0f1f3;cursor:pointer;font-size:12.5px;display:flex;justify-content:space-between;gap:6px}
#list div.cur{background:#e8efff}#list div.done{color:var(--mut)}#list b{font-weight:600}
#list .tag{font-size:11px;padding:0 5px;border-radius:4px;background:#eef;color:#334}
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
.decide button.on{outline:2px solid var(--acc);background:#e8efff}
.decide button kbd{font-size:11px;color:var(--mut);margin-right:4px}
.decide select,.decide input{font:inherit;padding:7px 8px;border:1px solid var(--line);border-radius:8px}
.decide input{flex:1;min-width:220px}
#zoom{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:20;cursor:zoom-out}
#zoom img{max-width:96vw;max-height:96vh;background:#fff}
.help{color:var(--mut);font-size:12px;margin-top:10px}
.multi{grid-column:1/3;background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:9px 12px;font-size:13px}
</style></head><body>
<header><h1>03b — architecture type: text vs image</h1>
<select id="view"><option value="todo">to confirm (not auto, not decided)</option><option value="review">everything you confirm (agree + disagree + low-conf)</option><option value="agree">agree — confirm the citation</option><option value="disagree">disagree (text ≠ image)</option><option value="lowconf">agree, low confidence</option><option value="known">known aircraft — cleared automatically</option><option value="notstated">text not stated (no citation exists)</option><option value="all">all 695</option></select>
<span id="prog"></span>
<button id="exp">Export CSV</button><label style="font-size:12px">Import CSV <input type="file" id="imp" accept=".csv" style="width:180px"></label>
<button id="clr" title="clear all decisions on this browser">Reset</button>
</header>
<main><div id="list"></div><div id="panel"></div></main>
<div id="zoom"><img></div>
<script>
const DATA = __DATA__; const TYPES = __TYPES__;
const KEY='archreview_v1'; let DEC={}; try{DEC=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){DEC={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(DEC))}catch(e){}}
let VIEW='todo', CUR=0, ROWS=[];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function label(t){const d=TYPES[t];return t?`<span class="big">${esc(t)}</span> <span class="def">${d?esc(d[0]):''}</span>`:'<span class="def">— (no image type: unclassifiable / quick override)</span>'}
function finalOf(r,d){if(!d)return'';if(d.choice==='confirm')return r.text;if(d.choice==='image')return r.image;if(d.choice==='text')return r.text;if(d.choice==='other')return d.other||'';return d.choice==='unsure'?'?':''}
const REVIEW=r=>!r.known&&r.group!=='notstated';
function filterRows(){ROWS=DATA.filter(r=>VIEW==='all'||(VIEW==='todo'?REVIEW(r)&&!DEC[r.pid]:VIEW==='review'?REVIEW(r):VIEW==='known'?!!r.known:r.group===VIEW&&!r.known));if(CUR>=ROWS.length)CUR=0}
function renderList(){const L=document.getElementById('list');L.innerHTML='';ROWS.forEach((r,i)=>{const d=DEC[r.pid];const el=document.createElement('div');el.className=(i===CUR?'cur ':'')+(d?'done':'');el.innerHTML=`<span><b>${esc(r.pid)}</b><br><span style="font-size:11px">${esc(r.company)}</span></span><span class="tag">${r.group==='agree'||r.group==='lowconf'?esc(r.text)+' ✓✓':esc(r.image||'—')+'→'+esc(r.text)}${d?' ✓ '+esc(finalOf(r,d)):r.known?' auto':''}</span>`;el.onclick=()=>{CUR=i;render()};L.appendChild(el)});
 const todo=DATA.filter(REVIEW);const n=todo.filter(r=>DEC[r.pid]).length;document.getElementById('prog').textContent=`${n} / ${todo.length} confirmed · ${DATA.filter(r=>r.known).length} known-aircraft auto · ${DATA.filter(r=>r.group==='notstated').length} not stated · showing ${ROWS.length}`;
 const cur=L.children[CUR];if(cur)cur.scrollIntoView({block:'nearest'})}
function render(){filterRows();renderList();const P=document.getElementById('panel');const r=ROWS[CUR];if(!r){P.innerHTML='<p class="help">Nothing in this view.</p>';return}
 const d=DEC[r.pid]||{};const other=Object.keys(TYPES).filter(t=>t!=='NS');
 P.innerHTML=`<div class="head"><h2>${esc(r.pid)}</h2><span>${esc(r.company)}</span><span class="mut">${esc(r.realname||r.name)} · ${esc(r.year)} · ${r.nvar>1?r.nvar+' aircraft in this patent':'1 aircraft'}</span><a href="${esc(r.pdf)}" target="_blank">PDF ↗</a></div>
 <div class="mut" style="font-size:13px">${esc(r.title)} — <i>${esc(r.assignee)}</i></div>
 <div class="figs">${r.figs.map(f=>`<div class="fig ${f.main?'main':''}"><img src="${esc(f.src)}" style="transform:rotate(${f.rot}deg)" loading="lazy"><small>${f.main?'MAIN · ':''}${f.arch?'aircraft '+f.arch+' · ':''}${esc(f.state)} ${esc(f.per)} ${f.rot?'· rotated '+f.rot+'°':''}</small></div>`).join('')||'<p class="help">no approved figure on disk</p>'}</div>
 <div class="cards">
  <div class="card"><h3>Image label (annotator, from the figures)</h3><div class="big img">${label(r.image)}</div><div class="def">${esc((TYPES[r.image]||['',''])[1])}</div></div>
  <div class="card"><h3>Text label (reader, from title / abstract / claim 1 / description) · confidence ${esc(r.conf)}</h3><div class="big txt">${label(r.text)}</div><div class="def">${esc((TYPES[r.text]||['',''])[1])}</div>${r.quote?`<blockquote>“${esc(r.quote)}”</blockquote><div class="def">citation: ${r.qcheck==='verbatim'?'<b style="color:var(--ok)">verbatim in the patent text</b>':r.qcheck==='partial'?'<b style="color:var(--warn)">partly verbatim (ellipses / paraphrase) — check the PDF if in doubt</b>':'<b style="color:var(--warn)">not found verbatim — check the PDF</b>'}${r.qsec?' · '+esc(r.qsec):''}</div>`:''}${r.known?`<div class="def" style="color:var(--ok)">cleared automatically: known aircraft ${esc(r.known)}</div>`:''}${r.note?`<div class="def">reader's note: ${esc(r.note)}</div>`:''}</div>
  ${(new Set(r.variants)).size>1?`<div class="multi"><b>This patent draws ${r.variants.length} aircraft with different architectures: ${r.variants.map(esc).join(' · ')}.</b> The image label above is the set of them. One citation describes one embodiment, so the decision here records <i>which architecture the citation states</i>; the per-aircraft figure labels are not changed by it. Use "Other" to name that type.</div>`:''}
  <div class="decide">
   ${(r.group==='agree'||r.group==='lowconf')&&(new Set(r.variants)).size<2?`<button data-c="confirm" class="${d.choice==='confirm'?'on':''}"><kbd>1</kbd>Confirm ${esc(r.text)} — the citation states it</button>`:
   `<button data-c="image" class="${d.choice==='image'?'on':''}" ${(r.image && (new Set(r.variants)).size<2)?'':'disabled'}><kbd>1</kbd>Keep image label${r.image?' ('+esc(r.image)+')':' (none — pick 2 or 3)'}</button>
   <button data-c="text" class="${d.choice==='text'?'on':''}" ${r.text==='NS'?'disabled':''}><kbd>2</kbd>Take text label (${esc(r.text)})</button>`}
   <button data-c="other" class="${d.choice==='other'?'on':''}"><kbd>3</kbd>Other:</button>
   <select id="other">${other.map(t=>`<option value="${t}" ${d.other===t?'selected':''}>${t} — ${TYPES[t][0]}</option>`).join('')}</select>
   <button data-c="unsure" class="${d.choice==='unsure'?'on':''}"><kbd>4</kbd>Cannot tell / both defensible</button>
   <input id="cmt" placeholder="comment (optional)" value="${esc(d.comment||'')}">
  </div></div>
 <p class="help">Keys: 1 confirm/keep · 2 take text · 3 other · 4 cannot tell · ←/→ or Enter = next · click a figure to zoom. Decisions are saved in this browser; press Export CSV when done (goes to Downloads).</p>`;
 P.querySelectorAll('.decide button').forEach(b=>b.onclick=()=>decide(r,b.dataset.c));
 P.querySelector('#other').onchange=e=>{if(DEC[r.pid]){DEC[r.pid].other=e.target.value;save();render()}};
 P.querySelector('#cmt').onchange=e=>{DEC[r.pid]=DEC[r.pid]||{choice:''};DEC[r.pid].comment=e.target.value;save()};
 P.querySelectorAll('.fig img').forEach(im=>im.onclick=()=>{const z=document.getElementById('zoom');z.querySelector('img').src=im.src;z.querySelector('img').style.transform=im.style.transform;z.style.display='flex'});
}
function decide(r,c){const o=document.getElementById('other');DEC[r.pid]={choice:c,other:c==='other'?o.value:'',comment:document.getElementById('cmt').value,at:new Date().toISOString().slice(0,16)};save();
 if(VIEW==='todo'){render()}else{CUR=Math.min(CUR+1,ROWS.length-1);render()}}
document.getElementById('zoom').onclick=e=>e.currentTarget.style.display='none';
document.getElementById('view').onchange=e=>{VIEW=e.target.value;CUR=0;render()};
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT'){if(e.key==='Enter'){e.target.blur()}else return}
 const r=ROWS[CUR];if(!r)return;
 const AG=r.group==='agree'||r.group==='lowconf';const MV=(new Set(r.variants)).size>1;if(e.key==='1'&&AG&&!MV)decide(r,'confirm');else if(e.key==='1'&&r.image&&!MV)decide(r,'image');else if(e.key==='2'&&!AG&&r.text!=='NS')decide(r,'text');else if(e.key==='3')decide(r,'other');else if(e.key==='4')decide(r,'unsure');
 else if(e.key==='ArrowRight'||e.key==='Enter'){CUR=Math.min(CUR+1,ROWS.length-1);render()}else if(e.key==='ArrowLeft'){CUR=Math.max(CUR-1,0);render()}else if(e.key==='Escape')document.getElementById('zoom').style.display='none'});
document.getElementById('exp').onclick=()=>{const q=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const lines=[['patent_id','group','image_label','text_label','decision','final_label','comment','decided_at'].join(',')];
 DATA.forEach(r=>{const d=DEC[r.pid];if(!d||!d.choice)return;lines.push([r.pid,r.group,r.image,r.text,d.choice,finalOf(r,d),d.comment||'',d.at||''].map(q).join(','))});
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/csv'}));a.download='architecture_review_decisions.csv';a.click()};
document.getElementById('imp').onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();rd.onload=()=>{const t=rd.result.split(/\r?\n/).slice(1);let n=0;t.forEach(l=>{if(!l.trim())return;const c=l.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map(x=>x.replace(/,$/,'').replace(/^"|"$/g,'').replace(/""/g,'"'));
 const [pid,,img,txt,choice,fin,cmt,at]=c;if(!pid||!choice)return;DEC[pid]={choice,other:choice==='other'?fin:'',comment:cmt||'',at:at||''};n++});save();render();alert(n+' decisions imported')};rd.readAsText(f)};
document.getElementById('clr').onclick=()=>{if(confirm('Clear every decision saved in this browser?')){DEC={};save();render()}};
render();
</script></body></html>"""
out = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__TYPES__", json.dumps(TYPES, ensure_ascii=False))
OUT.write_text(out, encoding="utf-8")
print("wrote", OUT, f"{OUT.stat().st_size/1024:.0f} KB")
