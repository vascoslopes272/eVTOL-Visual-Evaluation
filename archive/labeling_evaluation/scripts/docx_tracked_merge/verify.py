import sys, re, difflib
from docx import Document
from docx.oxml.ns import qn
def text(p, mode):
    out = ""
    for el in p.iter():
        if el.tag in (qn("w:t"), qn("w:delText")):
            anc = [a.tag for a in el.iterancestors()]
            if mode == "accept" and qn("w:del") in anc: continue
            if mode == "reject" and qn("w:ins") in anc: continue
            out += el.text or ""
    return out
def rows_state(d, mode):
    out=[]
    for tr in d.element.body.iter(qn("w:tr")):
        pr = tr.find(qn("w:trPr"))
        if pr is not None:
            if mode=="accept" and pr.find(qn("w:del")) is not None: continue
            if mode=="reject" and pr.find(qn("w:ins")) is not None: continue
        out.append(tr)
    return out
orig, new = Document(sys.argv[1]), Document(sys.argv[2])
def paras(d, mode):
    rs = set(id(x) for x in rows_state(d, mode))
    res=[]
    for p in d.element.body.iter(qn("w:p")):
        tr = next((a for a in p.iterancestors() if a.tag == qn("w:tr")), None)
        if tr is not None and all(id(tr)!=id(x) for x in rows_state(d, mode)): continue
        res.append(text(p, mode))
    return res
o = [text(p, "accept") for p in orig.element.body.iter(qn("w:p"))]
r = paras(new, "reject")
print("reject-all == original:", o == r, len(o), len(r))
if o != r:
    for i,(a,b) in enumerate(zip(o,r)):
        if a!=b: print(" first diff at",i, repr(a[:120]), "|", repr(b[:120])); break
a = paras(new, "accept")
open(sys.argv[3], "w").write("\n".join(a))
print("accepted paragraphs:", len(a))
