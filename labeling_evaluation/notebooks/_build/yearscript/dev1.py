import re,sys,pandas as pd
Y="/mnt/storage_11tb/Drive_files_to_syncronize/3 - Images DataSets & Labelling Outputs/EVTOLNEWS_DS/0_source/years/"
ev=pd.read_csv(Y+'readers/evidence_ids.csv',dtype=str,keep_default_na=False)
dy=pd.read_csv(Y+'aircraft_dev_year.csv',dtype=str,keep_default_na=False).set_index('slug_key')
samp=set(pd.read_csv('review/decisions/YEAR_REVIEW_SAMPLE.csv',dtype=str).slug_key)   # hold-out: never used for development
dev=[k for k in dy.index if k not in samp and dy.loc[k,'dev_year_status']=='agreed']
print('dev pages',len(dev))
COMPANY=re.compile(r"\b(?:was|were) (?:founded|incorporated|established|formed|created|started|launched as a company|set up)\b|\bfounded\b|\bincorporated\b|\bestablished in\b|\bformed in\b|\bcompany\b.*\b(?:began|started)|\bheadquarter|\bfounder\b|\bsince (?:19|20)\d\d\b.*\b(?:company|has been)\b",re.I)
def years(s): return [int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-3]\d)\b",s)]
def pick(k,use_res=True):
    g=ev[ev.slug_key==k]
    c=[]
    for _,r in g.iterrows():
        if r.is_resource=='True' and not use_res: continue
        if COMPANY.search(r.sentence): continue
        ys=[y for y in years(r.sentence) if y<=2026]
        c+=ys
    return min(c) if c else None
