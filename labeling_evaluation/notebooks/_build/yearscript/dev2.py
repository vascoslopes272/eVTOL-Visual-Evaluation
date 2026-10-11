import re,sys,itertools
sys.path.insert(0,'.')
import pandas as pd
exec(open('notebooks/_build/yearscript/dev1.py').read().split("def pick")[0])
from viz import config
cfg=config.load();A=pd.read_csv(cfg.path('evtolnews_aircraft'),keep_default_na=False).set_index('slug_key')
EVENT=re.compile(r"\b(?:announce[ds]?|unveil(?:ed|s)?|reveal(?:ed|s)?|introduc(?:ed|es)|first flight|maiden flight|flew|flown|test[- ]flights?|flight test(?:s|ing)?|hover(?:ed)? test|took off|successfully|began|begun|started|commenced|completed|rolled out|rollout|demonstrat(?:ed|es)|launched|showcased|displayed|presented|built|construct(?:ed|ion)|prototype|design(?:ed)? (?:in|began|started)|development (?:began|started|of)|patent(?:ed)? |filed|testing|tests?)\b",re.I)
FUT=re.compile(r"\b(?:will|plans? to|expected|aims? to|intends?|scheduled|target(?:s|ed)?|is planned|are planned|hopes?|goal)\b",re.I)
ASOF=re.compile(r"\bas of\b|\bno (?:information|specifications?|details?)\b|\bnot (?:been )?(?:released|reported|announced|disclosed|stated)\b|\bhas not\b|\bhave not\b|\bunknown\b",re.I)
def toks(k): return [t.lower() for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+",A.loc[k,'model']) if len(t)>=3]
def cands(k,res=True,need_tok=False,need_event=True,drop_fut=True,drop_asof=True):
    g=ev[ev.slug_key==k];tk=toks(k);out=[]
    for _,r in g.iterrows():
        s=r.sentence
        if COMPANY.search(s): continue
        ys=[y for y in years(s) if y<=2026]
        if not ys: continue
        if r.is_resource=='True':
            if res: out.append((min(ys),'R'))
            continue
        if need_event and not EVENT.search(s): continue
        if drop_asof and ASOF.search(s): continue
        if drop_fut and FUT.search(s) and not re.search(r"\b(?:was|were|had|did)\b",s): continue
        if need_tok and not any(t in s.lower() for t in tk): continue
        out.append((min(ys),'T'))
    return out
def score(**kw):
    ok=n=0
    for k in dev:
        c=cands(k,**kw);p=min(y for y,_ in c) if c else None;t=int(dy.loc[k,'dev_year']);n+=1;ok+=(p==t)
    return ok/n
if __name__=='__main__':
    for kw in [dict(),dict(need_event=False),dict(need_tok=True),dict(res=False),dict(drop_asof=False),dict(drop_fut=False),dict(need_event=False,drop_asof=True,drop_fut=True)]:
        print(kw,round(score(**kw),3))
