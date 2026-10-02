"""Check every Table/Figure number the Labelling Analysis cites against the live NODES walk.

    python3 scripts/audit_la_cross_references.py

Run it before rendering, and again after any agent adds, removes or re-orders a node: a table that
gains a sibling turns "Table 3.3" into "Table 3.3a" and silently breaks every Source line citing it.
Handles 'Table 4.1.3', 'Tables 4.2.5a/b' and 'Tables 4.1.7a/b'. Comment lines are skipped.

One hit is expected and correct:
  * la_figures.py, design_space_cards_svg docstring - 'Figure 3.3c' is the PRELIMINARY ANALYSIS's
    number for the drawing this one is derived from, not a number in this document.
Anything else listed is a real broken cross-reference.

The la_flags caption also records tables that WERE REMOVED on the author's rulings; since the
reorganisation of 2026-09-23 it names them by section ("the table of 2.1.7") rather than as
"Table N", so it no longer shows up here and cannot be mistaken for a live citation.
"""
import re, sys, pathlib
ROOT = "/home/vasco/Vasco Workspace/Tese_Vasco_Lnx/eVTOL-Visual-Evaluation/labeling_evaluation"
sys.path.insert(0, ROOT)
from src.dataset_facts import la_index as L

tab_num, fig_num = {}, {}
for n in L.NODES:
    figs, tabs = n.get("figures", []), n.get("tables", [])
    for k, f in enumerate(figs):
        fig_num[f] = L.figure_number(n["id"], k, len(figs))
    for k, t in enumerate(tabs):
        tab_num[t] = L.table_number(n["id"], k, len(tabs))

def cited(text):
    """yield (kind, number) for singular and plural citations"""
    for kind, body in re.findall(r"\b(Tables?|Figures?) ((?:\d+\.)*\d+[a-z]?(?:/[a-z])*)", text):
        k = "Table" if kind.startswith("Table") else "Figure"
        if "/" in body:                      # 'Tables 4.2.5a/b' -> 4.2.5a, 4.2.5b
            head, *rest = body.split("/")
            stem = head[:-1] if head[-1].isalpha() else head
            yield k, head
            for r in rest:
                yield k, stem + r
        else:
            yield k, body

bad = []
for fname in ("la_figures.py", "la_index.py", "la_tables.py"):
    for i, ln in enumerate(pathlib.Path(ROOT, "src/dataset_facts", fname).read_text(encoding="utf-8").splitlines(), 1):
        if ln.lstrip().startswith("#"):
            continue                          # explanatory comments, not printed text
        for kind, num in cited(ln):
            pool = tab_num if kind == "Table" else fig_num
            if num not in set(pool.values()):
                bad.append((fname, i, kind, num, ln.strip()[:95]))

print("citations that the NODES walk does NOT produce:", len(bad))
for b in bad:
    print("  ", b[0], "line", b[1], "->", b[2], b[3])
    print("      ", b[4])
print("\nbuilt-but-never-placed check runs in the render test.")
