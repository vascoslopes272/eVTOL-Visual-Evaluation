"""Hand-written tracked edits for the findings-for-decision document (the author's own summaries).

python handedit.py <in.docx> <out.docx> <log.md>
Each edit: (locator: text the paragraph must contain, old words, new words). Applied only where the old
words occur exactly once in exactly one paragraph that also holds the locator.
"""
import sys, re, copy
from lxml import etree
src = open(__file__.replace("handedit.py", "merge.py")).read()
exec(src[src.index("def nid"):src.index("# ---------------------------------------------------------------- base -> theirs")])
exec(src[src.index("def runs_of"):src.index("def tokens")])
from docx import Document
from docx.oxml.ns import qn
IN, OUT, LOG = sys.argv[1:4]
import datetime
AUTHOR, DATE = "Claude", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
XS = "{http://www.w3.org/XML/1998/namespace}space"
_id = [20000]

EDITS = [
    # section 1 box and section 2
    ("The drawings give the built aircraft", "for 88 of 98 aircraft", "for 87 of 97 aircraft"),
    ("which together hold", "649 of the 665 aircraft", "613 of the 627 aircraft"),
    # decision table, 1.1
    ("Architecture related eVTOL patents double", "every 3.8 years", "every 3.6 years"),
    ("Architecture related eVTOL patents double", "1.26 times as fast as aeronautics (1.14 to 1.39)", "1.32 times as fast as aeronautics (1.20 to 1.46)"),
    ("Architecture related eVTOL patents double", "the ratio falls to 1.19 (0.99 to 1.33), which cannot be told apart from equal pace.",
     "the ratio is 1.26 (1.07 to 1.41), so the edge over aeronautics still holds."),
    # 1.2
    ("have no patent left in force (PatSeer legal status). The classes appear", "44 % of the 356 aircraft", "43 % of the 332 aircraft"),
    ("have no patent left in force (PatSeer legal status). The classes appear", "(p 0.035; Tilt Propulsor 35 %, Multirotor 30 %, Lift + Cruise 52 %, CVT 57 %)",
     "(p 0.043; Tilt Propulsor 34 %, Multirotor 31 %, Lift + Cruise 53 %, CVT 53 %)"),
    ("have no patent left in force (PatSeer legal status). The classes appear", "(32 % out of force at the US office against 71 % elsewhere; within the US office p 0.29)",
     "(31 % out of force at the US office against 69 % elsewhere; within the US office p 0.43)"),
    # 1.3
    ("Where a public aircraft exists, the drawing", "for 88 of 98", "for 87 of 97"),
    ("Where a public aircraft exists, the drawing", "are company-backed, recent and carry more propulsor units",
     "are company-backed and carry more propulsor units (the index firms' aircraft are also more recent)"),
    # 2.1
    ("The empennage (tail) and the propulsor-unit count vary most", "hold only 30 % and 23 %", "hold only 29 % and 23 %"),
    ("The empennage (tail) and the propulsor-unit count vary most", "306 of 633", "286 of 596"),
    # 2.2
    ("Four archetype sets are read", "40 archetypes at C·W·T", "39 archetypes at C·W·T"),
    ("Four archetype sets are read", "with 40 % of all aircraft", "with 39 % of all aircraft"),
    # 2.3
    ("Half of the 2020-23 aircraft sit in 7", "the largest holds only 10 %", "the largest holds only 11 %"),
    # 3.1 (decision table and the other occurrences are merged; this cell is the author's)
    ("while Tilt Propulsor falls from 32 % to 21 %. The evtol.news directory shows a similar mix, but", "rises from 26 % to 32 %", "rises from 27 % to 32 %"),
    # 3.2
    ("Only the family F, Lift + Cruise with the fixed-wing CVT", "(52.6 % and 58.3 % of the in-force aircraft", "(51.8 % and 59.3 % of the in-force aircraft"),
    ("Only the family F, Lift + Cruise with the fixed-wing CVT", "passes 40.4 % of a year", "passes 39.0 % of a year"),
    ("Only the family F, Lift + Cruise with the fixed-wing CVT", "on all aircraft 2020 stops at 50.0 %.", "on all aircraft 2020 does not pass half (49.3 %)."),
    # 3.3
    ("No class settles on one layout, but the leading layout changes", "(47 % of the class in 2020-23)", "(48 % of the class in 2020-23)"),
    ("No class settles on one layout, but the leading layout changes", "(73 % up to 2011)", "(75 % up to 2011)"),
    # 3.4
    ("Tilt Propulsor adds a second tilting set and its median propulsor units go from 2 to 4. CVT moves its fixed propulsor units onto booms (25",
     "(25 % to 62 %, p 0.02)", "(20 % to 62 %, p 0.03)"),
    ("CVT moves its fixed propulsor units onto booms (", "and sheds its ducts (75 % to 32 %)",
     "and its share with a ducted unit drops (80 % to 32 %, though as a year trend this is not detected)"),
    ("CVT moves its fixed propulsor units onto booms (", "Of the 12 traces that move,", "Of the 8 traces that move inside a class,"),
    # 4.1
    ("Organisations (companies, universities and institutes) file 70 %", "208 named organisations, 134 of them", "199 named organisations, 130 of them"),
    ("Organisations (companies, universities and institutes) file 70 %", "no filer holds more than 20 % of any class", "no filer holds more than 21 % of any class"),
    # 4.2
    ("First-time firms bring most of each window's aircraft", "(p 0.015), where 33 of the 58 returning", "(p 0.017), where 33 of the 57 returning"),
    ("First-time firms bring most of each window's aircraft", "Lift + Cruise (62 %) or Tilt Propulsor (57 %)", "Lift + Cruise (61 %) or Tilt Propulsor (56 %)"),
    ("First-time firms bring most of each window's aircraft", "(only 15 % stay in Tilt Wing)", "(only 17 % stay in Tilt Wing)"),
    ("First-time firms bring most of each window's aircraft", "(12 % of the entering firms in both 2016-19 and 2020-23)",
     "(12 % and 11 % of the entering firms in 2016-19 and 2020-23)"),
    ("First-time firms bring most of each window's aircraft", "from 11 % to 8.1 %", "from 11 % to 8 %"),
    ("First-time firms bring most of each window's aircraft", "for Tilt Propulsor (38 %) or Lift + Cruise (31 %)", "for Tilt Propulsor (44 %) or Lift + Cruise (22 %)"),
    # 5.1
    ("All years together, Europe and Asia-Pacific lead", "with Lift + Cruise (32 % and 34 %)", "with Lift + Cruise (30 % and 34 %)"),
    ("All years together, Europe and Asia-Pacific lead", "tilting aircraft (66 %)", "tilting aircraft (67 %)"),
    ("All years together, Europe and Asia-Pacific lead", "CVT holds 23 % of its aircraft in 2012-15, 9 % in 2016-19 and 35 % in 2020-23",
     "CVT holds 24 % of its aircraft in 2012-15, 10 % in 2016-19 and 36 % in 2020-23"),
    # 5.2
    ("Median priority year: North America 2018, Europe 2019, Asia-Pacific 2020, with Asia-Pacific", "3-4 years late", "2-4 years late"),
    # 5.3
    ("In 2020-23 the family F holds", "holds 47 % of North American", "holds 48 % of North American"),
    ("In 2020-23 the family F holds", "(59 %, p 0.019)", "(60 %, p 0.023)"),
]
# Table 7 (a copy with the author's own number format): row first cell, old cell text, new cell text
CELLS = [
    ("C (class)", "7.2", "7.3"), ("C (class)", "27.8 %", "26.4 %"),
    ("C·W·T (class + wings + tilt)", "40", "39"), ("C·W·T (class + wings + tilt)", "16.3", "16.4"),
    ("C·W·T (class + wings + tilt)", "17.4 %", "16.7 %"),
    ("C·U (class + propulsor units)", "29.0", "29.4"), ("C·U (class + propulsor units)", "9.7 %", "9.8 %"),
    ("F (Lift + Cruise + CVT* family)", "40.0 %", "39.4 %"),
]

doc = Document(IN)
body = doc.element.body
log, n_ok = [], 0
for loc, old, new in EDITS:
    hits = [p for p in body.iter(qn("w:p")) if loc in ptext(p) and ptext(p).count(old) == 1]
    if len(hits) != 1:
        log.append(f"- NOT APPLIED ({len(hits)} paragraphs): «{old}» → «{new}»"); continue
    p = hits[0]; raw = ptext(p); s = raw.index(old)
    track_replace(p, s, s + len(old), new); n_ok += 1
for key, old, new in CELLS:
    done = False
    for tr in body.iter(qn("w:tr")):
        tcs = tr.findall(qn("w:tc"))
        if not tcs or norm(ptext(tcs[0].find(qn("w:p")))) != key:
            continue
        for tc in tcs[1:]:
            for p in tc.findall(qn("w:p")):
                if norm(ptext(p)) == old:
                    raw = ptext(p); s = raw.index(old); track_replace(p, s, s + len(old), new); done = True; break
            if done:
                break
        if done:
            break
    n_ok += done
    if not done:
        log.append(f"- TABLE 7 CELL NOT FOUND (maybe already updated by the merge): {key}: «{old}» → «{new}»")
doc.save(OUT)
open(LOG, "a").write("\n## Hand edits (the author's own summaries)\n" + f"{n_ok} applied\n" + "\n".join(log) + "\n")
print(n_ok, "hand edits applied;", len(log), "not applied"); print("\n".join(log))
