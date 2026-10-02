"""Three-way merge of the regenerated brief into the author's hand-edited docx, as Word tracked changes.

python merge.py <in.docx> <out.docx> <old_brief.md> <new_brief.md> <old_figs> <new_figs> <log.md>

base = old brief (what the docx was made from), theirs = new brief, mine = the author's docx.
A docx paragraph equal to an old brief line takes the new line exactly (positional word diff).
A paragraph the author edited is aligned word by word with its closest old line; a change is applied
only where the author's words still equal the old line's, otherwise it is logged for a manual edit.
Tables: rows matched by first cell + best agreement of the other cells; cells merged the same way.
Figures: images identical to an old figure file are replaced by the new file (not trackable).
"""
import copy, datetime, difflib, glob, hashlib, io, os, re, sys
from docx import Document
from docx.oxml.ns import qn
from lxml import etree
from PIL import Image

IN, OUT, OLDMD, NEWMD, OLDFIG, NEWFIG, LOG = sys.argv[1:8]
AUTHOR, DATE = "Claude", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
XS = "{http://www.w3.org/XML/1998/namespace}space"
_id = [9000]


def nid():
    _id[0] += 1
    return str(_id[0])


def norm(s):
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
         .replace(" ", " ").replace(" ", " ").replace(" ", " ").replace("‑", "-"))
    return re.sub(r"\s+", " ", s).strip()


def plain(md):
    s = md.strip()
    m = re.match(r"!\[(.*)\]\([^)]*\)(\{[^}]*\})?\s*$", s)
    if m:
        s = m.group(1)
    s = re.sub(r"\{:[^}]*\}", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"^#+\s*", "", s)
    s = re.sub(r"^[-*]\s+(?=\S)", "", s) if not s.startswith("**") else s
    s = s.replace("\\*", "\x00").replace("**", "")
    s = re.sub(r"(?<![\w*])\*(?!\s)|(?<!\s)\*(?![\w*])", "", s).replace("\x00", "*")
    return norm(s)


def cplain(c):
    return norm(c.replace("**", "").replace("\\*", "*"))


def is_row(x):
    return x.startswith("|")


def is_sep(x):
    return bool(re.match(r"^\|[:\- |]+\|$", x.strip()))


# ---------------------------------------------------------------- base -> theirs, line by line
old_md, new_md = open(OLDMD).read().split("\n"), open(NEWMD).read().split("\n")
line_map, row_map, row_del, row_ins = {}, [], [], []
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old_md, new_md, autojunk=False).get_opcodes():
    if op == "equal":
        continue
    O, N = old_md[i1:i2], new_md[j1:j2]
    ot = [x for x in O if is_row(x) and not is_sep(x)]; nt = [x for x in N if is_row(x) and not is_sep(x)]
    ok = {c(x)[0]: x for x in ot for c in [lambda y: [z.strip() for z in y.strip().strip("|").split("|")]]}
    nk = {c(x)[0]: x for x in nt for c in [lambda y: [z.strip() for z in y.strip().strip("|").split("|")]]}
    for k in ok:
        (row_map.append((ok[k], nk[k])) if k in nk else row_del.append(ok[k]))
    for k in nk:
        if k not in ok:
            row_ins.append(nk[k])
    ox = [plain(x) for x in O if not is_row(x) and plain(x)]
    nx = [plain(x) for x in N if not is_row(x) and plain(x)]
    if len(ox) == len(nx):
        for a, b in zip(ox, nx):
            if a != b:
                line_map.setdefault(a, b)
# a row deleted in one block and inserted in another is the same row, changed
_ins = {r.strip().strip("|").split("|")[0].strip(): r for r in row_ins}
for r in list(row_del):
    k = r.strip().strip("|").split("|")[0].strip()
    if k in _ins:
        row_map.append((r, _ins.pop(k))); row_del.remove(r)
row_ins = list(_ins.values())
# Figure 1 (ii) and Figure 8 (i): panel labels reworded by a code edit unrelated to the data; the
# figures themselves did not change design, so the author's captions stay as they are
for k in [k for k in line_map if k.startswith("Figure") and not re.search(r"\d", " ".join(
        w for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, k.split(), line_map[k].split()).get_opcodes()
        if op != "equal" for w in k.split()[i1:i2] + line_map[k].split()[j1:j2]))]:
    del line_map[k]
old_lines = list(line_map)


# ---------------------------------------------------------------- docx text model
def runs_of(p):
    out, pos = [], 0
    for r in p.iter(qn("w:r")):
        if r.getparent().tag == qn("w:del"):
            continue
        t = ""
        for ch in r:
            if ch.tag == qn("w:t"):
                t += ch.text or ""
            elif ch.tag == qn("w:tab"):
                t += "\t"
            elif ch.tag in (qn("w:br"), qn("w:cr")):
                t += "\n"
        out.append((r, pos, pos + len(t), t))
        pos += len(t)
    return out


def ptext(p):
    return "".join(t for *_, t in runs_of(p))


def split_run(r, k):
    ts = [c for c in r if c.tag == qn("w:t")]
    if len(ts) != 1 or any(c.tag in (qn("w:tab"), qn("w:br"), qn("w:cr")) for c in r):
        raise ValueError("complex run")
    t = ts[0].text or ""
    r2 = copy.deepcopy(r)
    ts[0].text = t[:k]; ts[0].set(XS, "preserve")
    t2 = [c for c in r2 if c.tag == qn("w:t")][0]; t2.text = t[k:]; t2.set(XS, "preserve")
    r.addnext(r2)


def mk_run(template, text):
    r = etree.Element(qn("w:r"))
    if template is not None and template.find(qn("w:rPr")) is not None:
        r.append(copy.deepcopy(template.find(qn("w:rPr"))))
    t = etree.SubElement(r, qn("w:t")); t.text = text; t.set(XS, "preserve")
    return r


def mark(tag):
    e = etree.Element(qn(tag)); e.set(qn("w:id"), nid()); e.set(qn("w:author"), AUTHOR); e.set(qn("w:date"), DATE)
    return e


def track_replace(p, s, e, new):
    for cut in (s, e):
        for r, a, b, t in runs_of(p):
            if a < cut < b:
                split_run(r, cut - a)
                break
    runs = runs_of(p)
    inside = [r for r, a, b, t in runs if a >= s and b <= e and b > a]
    before = [r for r, a, b, t in runs if b <= s and b > a]
    tmpl = inside[0] if inside else (before[-1] if before else (runs[0][0] if runs else None))
    anchor = None
    for r in inside:
        d = mark("w:del"); r.addprevious(d); d.append(r)
        for t in r.findall(qn("w:t")):
            t.tag = qn("w:delText")
        anchor = d
    if new:
        ins = mark("w:ins"); ins.append(mk_run(tmpl, new))
        if anchor is not None:
            anchor.addnext(ins)
        elif before:
            (before[-1].getparent() if before[-1].getparent().tag == qn("w:ins") else before[-1]).addnext(ins)
        elif runs:
            runs[0][0].addprevious(ins)
        else:
            p.append(ins)


def tokens(s):
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", s)]


def apply_ops(p, raw, ops):
    """ops: (start, end, new_text) on raw; applied right to left so offsets stay valid."""
    n = 0
    for s, e, new in sorted(ops, key=lambda x: -x[0]):
        track_replace(p, s, e, new); n += 1
    return n


def diff_ops(raw, target):
    """Word diff raw -> target as char ops on raw."""
    A, B = tokens(raw), [t for t, *_ in tokens(target)]
    ops = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(t) for t, *_ in A], [norm(t) for t in B], autojunk=False).get_opcodes():
        if op == "equal":
            continue
        new = " ".join(B[j1:j2])
        if i1 < i2:
            s, e = A[i1][1], A[i2 - 1][2]
            if not new and i2 < len(A):
                e = A[i2][1]                        # a deleted word takes its following space
            elif not new and i1 > 0:
                s = A[i1 - 1][2]
        else:                                       # insertion before token i1 (or at the end)
            if i1 < len(A):
                s = e = A[i1][1]; new = new + " "
            else:
                s = e = len(raw.rstrip()); new = " " + new
        ops.append((s, e, new))
    return ops


PUNCT = ".,;:"


def tkey(t):
    """A token's identity for alignment: case and trailing sentence punctuation ignored."""
    return norm(t).lower().rstrip(PUNCT)


def trail(t):
    return t[len(t.rstrip(PUNCT)):]


def merge_ops(raw, base, theirs):
    """Author's paragraph `raw`, made from base line `base`; carry base->theirs where raw still equals base."""
    R, Bs = tokens(raw), [t for t, *_ in tokens(base)]
    Rn, Bn = [tkey(t) for t, *_ in R], [tkey(t) for t in Bs]
    amap = {}
    for a, b, size in difflib.SequenceMatcher(None, Bn, Rn, autojunk=False).get_matching_blocks():
        for k in range(size):
            amap[a + k] = b + k
    T = [t for t, *_ in tokens(theirs)]
    ops, lost = [], []
    Tk = [tkey(t) for t in T]
    # base and theirs are compared exactly (a punctuation change of the generator is a change),
    # the author's paragraph loosely (the author's own punctuation and capitals are kept)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [norm(t) for t in Bs], [norm(t) for t in T], autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if i2 - i1 == j2 - j1 and all(tkey(Bs[i1 + k]) == Tk[j1 + k] for k in range(i2 - i1)):
            continue                                   # punctuation-only change: the author's stands
        new_toks = T[j1:j2]
        if i1 < i2:
            idx = [amap.get(i) for i in range(i1, i2)]
            if None in idx or idx != list(range(idx[0], idx[0] + len(idx))):
                lost.append((" ".join(Bs[i1:i2]), " ".join(new_toks))); continue
            a_last, b_last = R[idx[-1]][0], Bs[i2 - 1]
            if new_toks:
                last = new_toks[-1]
                # the author's own trailing punctuation wins where the author changed it
                if trail(a_last) != trail(b_last):
                    new_toks = new_toks[:-1] + [last.rstrip(PUNCT) + trail(a_last)]
                s, e = R[idx[0]][1], R[idx[-1]][2]
                if R[idx[0]][0][:1].isupper() and not Bs[i1][:1].isupper() and new_toks[0][:1].islower():
                    new_toks[0] = new_toks[0][:1].upper() + new_toks[0][1:]
                ops.append((s, e, " ".join(new_toks)))
            else:
                if trail(a_last) != trail(b_last) and idx[0] > 0:
                    # the author closed the deleted words with their own punctuation: keep it
                    s = R[idx[0] - 1][2]; e = R[idx[-1]][2] - len(trail(a_last))
                else:
                    s = R[idx[0]][1]
                    e = R[idx[-1] + 1][1] if idx[-1] + 1 < len(R) else R[idx[-1]][2]
                    if idx[-1] + 1 >= len(R) and idx[0] > 0:
                        s = R[idx[0] - 1][2]
                ops.append((s, e, ""))
        else:
            new = " ".join(new_toks)
            if i1 in amap:
                s = e = R[amap[i1]][1]; ops.append((s, e, new + " "))
            elif i1 - 1 in amap:
                s = e = R[amap[i1 - 1]][2]; ops.append((s, e, " " + new))
            else:
                lost.append(("", new))
    return ops, lost


doc = Document(IN)
body = doc.element.body
log, applied, exact, merged = [], 0, 0, 0
in_table = lambda p: any(a.tag == qn("w:tc") for a in p.iterancestors())
for p in list(body.iter(qn("w:p"))):
    raw = ptext(p)
    key = norm(raw)
    if not key:
        continue
    if key in line_map:                                  # untouched paragraph: take the new line exactly
        applied += apply_ops(p, raw, diff_ops(raw, line_map[key])); exact += 1
        continue
    if in_table(p) and len(key) < 60:
        continue                                         # table cells are handled with their rows
    # an edited paragraph: its closest changed base line
    best, br = None, 0.0
    kw = key.split(" ")
    for ol in old_lines:
        sm = difflib.SequenceMatcher(None, ol.split(" "), kw, autojunk=False)
        if sm.real_quick_ratio() < 0.5 or sm.quick_ratio() < 0.5:
            continue
        r = sm.ratio()
        if r > br:
            best, br = ol, r
    if best is None or br < 0.6:
        continue
    ops, lost = merge_ops(raw, best, line_map[best])
    # read the merged sentence back; where the author's sentence split left a seam, write the target in the
    # author's style and diff to it instead (two known seams, checked by hand)
    sim = raw
    for s_, e_, n_ in sorted(ops, key=lambda x: -x[0]):
        sim = sim[:s_] + n_ + sim[e_:]
    fixed = re.sub(r"nor\. In any other class; it sits", "nor in any other class. It sits", sim)
    fixed = re.sub(r"\(Figure (\d+), v\)\. the propulsor-type count", r"(Figure \1, v). The propulsor-type count", fixed)
    if fixed != sim:
        ops, lost = diff_ops(raw, fixed), []
        log.append(f"- seam fixed by hand-written target: {fixed[:90]}…")
    if ops:
        applied += apply_ops(p, raw, ops); merged += 1
    for o, n in lost:
        log.append(f"- MANUAL (your wording differs here): «{o}» → «{n}»   [in: {key[:110]}…]")

# ---------------------------------------------------------------- tables
def cells_of(line):
    return [cplain(c) for c in line.strip().strip("|").split("|")]


def row_texts(tr):
    return [norm("".join(t.text or "" for t in tc.iter(qn("w:t")))) for tc in tr.findall(qn("w:tc"))]


def find_row(cs):
    rows = list(body.iter(qn("w:tr")))
    cand = [tr for tr in rows if (lambda c: len(c) == len(cs) and c[0] == cs[0])(row_texts(tr))]
    if not cand:
        return None
    score = lambda tr: sum(a == b for a, b in zip(row_texts(tr), cs))
    cand.sort(key=score, reverse=True)
    if len(cand) > 1 and score(cand[0]) == score(cand[1]):
        return None
    return cand[0]


rows_done = 0
for o, n in row_map:
    oc, nc = cells_of(o), cells_of(n)
    tr = find_row(oc)
    if tr is None:
        log.append(f"- MANUAL table row not found: {oc[0][:60]} → {' | '.join(nc)[:160]}"); continue
    for tc, a, b in zip(tr.findall(qn("w:tc")), oc, nc):
        if a == b:
            continue
        ps = [p for p in tc.findall(qn("w:p")) if norm(ptext(p))]
        if len(ps) == 1 and norm(ptext(ps[0])) == a:
            applied += apply_ops(ps[0], ptext(ps[0]), diff_ops(ptext(ps[0]), b))
        else:
            log.append(f"- MANUAL table cell: row {oc[0][:40]}: «{a[:70]}» → «{b[:70]}»")
    rows_done += 1
for o in row_del:
    oc = cells_of(o); tr = find_row(oc)
    if tr is None:
        log.append(f"- MANUAL row to delete not found: {oc[0][:60]}"); continue
    for p in tr.iter(qn("w:p")):
        raw = ptext(p)
        if raw:
            track_replace(p, 0, len(raw), "")
    trpr = tr.find(qn("w:trPr"))
    if trpr is None:
        trpr = etree.Element(qn("w:trPr")); tr.insert(0, trpr)
    trpr.append(mark("w:del")); applied += 1
for n in row_ins:
    # anchor: the table row printed just before it in the new brief (its new text is live in the docx now)
    j = new_md.index(n)
    prev = next((new_md[k] for k in range(j - 1, -1, -1) if is_row(new_md[k]) and not is_sep(new_md[k])), None)
    ref = find_row(cells_of(prev)) if prev else None
    if ref is None:
        log.append(f"- MANUAL row to add: {' | '.join(cells_of(n))[:200]}"); continue
    new = copy.deepcopy(ref)
    for tc, val in zip(new.findall(qn("w:tc")), cells_of(n)):
        ps = tc.findall(qn("w:p"))
        for extra in ps[1:]:
            tc.remove(extra)
        par = ps[0]
        tmpl = next((r for r in par.iter(qn("w:r")) if r.getparent().tag != qn("w:del")), None)
        tmpl = copy.deepcopy(tmpl) if tmpl is not None else None
        for x in list(par):
            if x.tag in (qn("w:r"), qn("w:ins"), qn("w:del"), qn("w:hyperlink")):
                par.remove(x)
        ins = mark("w:ins"); ins.append(mk_run(tmpl, val)); par.append(ins)
    trpr = new.find(qn("w:trPr"))
    if trpr is None:
        trpr = etree.Element(qn("w:trPr")); new.insert(0, trpr)
    for x in list(trpr):
        if x.tag in (qn("w:ins"), qn("w:del")):
            trpr.remove(x)
    trpr.append(mark("w:ins"))
    ref.addnext(new); applied += 1
    log.append(f"- row added (tracked): {cells_of(n)[0]}")

# ---------------------------------------------------------------- figures
oldh = {hashlib.sha256(open(f, "rb").read()).hexdigest(): os.path.basename(f) for f in glob.glob(OLDFIG + "/*.png")}
swapped = []
for rel in doc.part.rels.values():
    if "image" not in rel.reltype:
        continue
    part = rel.target_part
    name = oldh.get(hashlib.sha256(part.blob).hexdigest())
    if not name or not os.path.exists(os.path.join(NEWFIG, name)):
        continue
    newb = open(os.path.join(NEWFIG, name), "rb").read()
    if newb == part.blob:
        continue
    ow, oh = Image.open(io.BytesIO(part.blob)).size; nw, nh = Image.open(io.BytesIO(newb)).size
    part._blob = newb
    if abs(ow / oh - nw / nh) > 0.005:
        for inl in body.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline"):
            blip = inl.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip")
            if blip is not None and blip.get(qn("r:embed")) == rel.rId:
                ext = inl.find("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent")
                cx = int(ext.get("cx")); cy = int(round(cx * nh / nw)); oldcy = ext.get("cy"); ext.set("cy", str(cy))
                for a in inl.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}ext"):
                    if a.get("cy") == oldcy:
                        a.set("cy", str(cy))
    swapped.append(name)

doc.save(OUT)
head = (f"{applied} tracked edits · {exact} paragraphs taken exactly from the new brief · {merged} edited paragraphs "
        f"merged · {rows_done} table rows · {len(swapped)} figures replaced · {sum(1 for x in log if 'MANUAL' in x)} spots for a manual edit")
open(LOG, "w").write("# Merge log\n\n" + head + "\n\n" + "\n".join(log) + "\n")
print(head)
