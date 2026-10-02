import sys,difflib,re
from docx import Document
from docx.oxml.ns import qn
src=open('merge.py').read(); exec(src[src.index('def norm'):src.index('# ---------------------------------------------------------------- base -> theirs')])
o=[ "".join(t.text or "" for t in p.iter(qn("w:t"))) for p in Document(sys.argv[1]).element.body.iter(qn("w:p"))]
a=open(sys.argv[2]).read().split("\n")
newlines=set(plain(x) for x in open(sys.argv[3]).read().split("\n"))
ne=no=0
pairs=[]
for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,o,a,autojunk=False).get_opcodes():
    if op=='equal': continue
    if op=='replace' and i2-i1==j2-j1: pairs+=list(zip(o[i1:i2],a[j1:j2]))
    else: pairs+=[(x,'<<ADDED/REMOVED>>') for x in o[i1:i2]]+[('<<ADDED>>',y) for y in a[j1:j2]]
for x,y in pairs:
    if x==y: continue
    ok = norm(y) in newlines; ne+=ok; no+=(not ok)
    X,Y=x.split(),y.split(); out=[]
    for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,X,Y,autojunk=False).get_opcodes():
        if op=='equal':
            seg=X[i1:i2]; out.append(' '.join(seg) if len(seg)<=6 else ' '.join(seg[:3])+' … '+' '.join(seg[-3:]))
        else: out.append('[-'+' '.join(X[i1:i2])+'-]{+'+' '.join(Y[j1:j2])+'+}')
    print(('OK ' if ok else '?? ')+' '.join(out)[:900]); print()
print('changed paragraphs identical to a new-brief line:',ne,' merged into your wording:',no)
