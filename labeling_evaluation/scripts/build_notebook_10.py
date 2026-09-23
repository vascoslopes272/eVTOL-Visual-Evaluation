#!/usr/bin/env python3
"""Build notebooks/10_preliminary_analysis.ipynb from src/dataset_facts/index.py.

The notebook follows the Preliminary Analysis node by node (chapters 1-4, three
numbering levels). Every heading and every line of prose comes from ``index.py``
at run time, with the live numbers filled in, so the notebook, the draft and the
PDF never drift. Re-run this after changing the index, then execute:

    python3 scripts/build_notebook_10.py
    jupyter nbconvert --to notebook --execute --inplace notebooks/10_preliminary_analysis.ipynb
"""
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.dataset_facts import index, index_notes  # noqa: E402


def notes(key):
    """The annotated-index notes filed under this node, verbatim, as markdown cells."""
    return [md(index_notes.PROVENANCE, "", text) for text in index_notes.NOTES.get(key, [])]


def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": "\n".join(lines)}


def code(*lines):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": "\n".join(lines)}


cells = [
md("# Preliminary Analysis — the labelled eVTOL patent data set",
   "",
   "This notebook produces the *Preliminary Analysis* document node by node: chapter 1 to 4, three",
   "numbering levels (`2.1`, `2.1.1`), every table and figure named by the subsection that owns it.",
   "The structure and the prose live in `src/dataset_facts/index.py`; every number in the prose is a",
   "placeholder filled from `numbers.live(ds)` at run time, and the three schemes (document pipeline,",
   "refinement funnel, design-space order) are SVG files whose numbers are interpolated the same way,",
   "so a figure can never disagree with the table beside it.",
   "",
   "**Source of the labels** is the `dataset_facts.source` switch in `config.yaml`: `batch_xlsx` reads",
   "`labels/reviewed_patents_Batch_0N.xlsx` and the per-batch identity workbooks directly; `master_04`",
   "reads notebook 04's join. Same tables either way. A review of several labelling decisions is still",
   "open, so some counts will move; the structure does not depend on which way they move.",
   "",
   "Thin notebook: it only **imports**, **calls** `src/dataset_facts/`, and **displays**. `show(id)` prints",
   "a node's prose with the live numbers and the figures it owns; the code under it produces its tables."),
code("import sys",
     "from pathlib import Path",
     "",
     "ROOT = Path.cwd()",
     "while not (ROOT / 'config.yaml').exists() and ROOT != ROOT.parent:",
     "    ROOT = ROOT.parent",
     "sys.path.insert(0, str(ROOT))",
     "",
     "import pandas as pd",
     "import matplotlib.pyplot as plt",
     "from IPython.display import Markdown, Image, SVG, display",
     "",
     "from src.config_loader import load_config",
     "from src.dataset_facts import (load_dataset, a1, a2, a3, a4, a5, a6, roster, rules, index,",
     "                               figures, numbers, report, published, export, ch5, register)",
     "",
     "pd.set_option('display.width', 200)",
     "pd.set_option('display.max_colwidth', 90)",
     "pd.set_option('display.max_rows', 250)",
     "",
     "cfg = load_config()",
     "F = cfg['dataset_facts']",
     "OUT = ROOT / F['output_dir']",
     "PARTIAL = F.get('partial_window_start', 2024)",
     "ds = load_dataset(cfg)",
     "",
     "print('source:', ds.source, '|', ds.root)",
     "if ds.build_log: print('batch reader:', {k: v for k, v in ds.build_log.items() if k != 'dup_root_missing'})",
     "ds.counts"),
md("The analysis unit is the **unique aircraft** (`ds.variants`, one row per aircraft; O1 / O2 observations",
   "excluded, S3 similars included). Patent-level facts use `ds.patents` (all acquired) or",
   "`ds.patents_analysis` (the representative primary patents); image-level facts use `ds.approved_figures`.",
   "The labelling batches are provenance only — nothing is split by batch."),
code("N = numbers.live(ds, PARTIAL)          # every number the prose and the diagrams quote",
     "FIGS = figures.render_all(ds, OUT, PARTIAL)   # PNG charts + the three SVG schemes -> outputs/.../figures",
     "plt.close('all')",
     "",
     "def show(node_id):",
     "    \"\"\"Heading, level line, prose (numbers filled in) and the figures of one node.\"\"\"",
     "    n = index.node(node_id)",
     "    parts = [index.heading(node_id, N).replace('## Chapter', '### Chapter')]",
     "    if index.level_line(node_id): parts.append(index.level_line(node_id))",
     "    if index.text(node_id, N): parts.append(index.text(node_id, N))",
     "    display(Markdown('\\n\\n'.join(parts)))",
     "    for name in n.get('figures', []):",
     "        p = FIGS[name]",
     "        display(SVG(filename=str(p)) if p.suffix == '.svg' else Image(filename=str(p), width=760))",
     "    if index.after(node_id, N): display(Markdown(index.after(node_id, N)))",
     "",
     "{k: v.shape for k, v in {",
     "    'master (patent, variant)': ds.master,",
     "    'aircraft observations': ds.approved_variants,",
     "    'unique aircraft - the analysis unit': ds.variants,",
     "    'patents acquired': ds.patents,",
     "    'representative primary patents': ds.patents_analysis,",
     "    'approved figures': ds.approved_figures,",
     "    'identity (Stage 03a)': ds.identity,",
     "}.items()}"),
]

for n in index.NODES:
    nid = n["id"]
    d = index.depth(nid)
    if d == 0:
        cells.append(md("---", index.heading(nid)))
    lines = [f"show('{nid}')"] + list(n.get("code", []))
    cells.append(code(*lines))
    cells += notes(nid)          # the annotated-index notes that belong to this section

cells += notes("export") + [
# ---------------- export ----------------
md("---", "## Export — tables, figures, the document and its PDF",
   "",
   "`outputs/preliminary_analysis/` gets every table as CSV and markdown (`tables/`, including the",
   "codebook-rule counts and the framework appendix tables that the document does not print), every",
   "figure (`figures/`, PNG charts and the three SVG schemes), `PRELIMINARY_ANALYSIS.md` and its PDF.",
   "Edit the prose in `index.py`; never the numbers. The PDF must stay at ten pages or fewer."),
code("TABLES = export.build_all(ds, F)",
     "written = export.write_all(TABLES, OUT)",
     "doc = report.write_markdown(ds, TABLES, FIGS, OUT, values=N, partial_window_start=PARTIAL)",
     "print(f'{len(written)} tables, {len(FIGS)} figures -> {OUT}')",
     "print('document:', doc.name, f'{doc.stat().st_size / 1024:.0f} KB')"),
code("import subprocess",
     "pdf = doc.with_suffix('.pdf')",
     "subprocess.run([sys.executable, str(ROOT.parent / 'scripts' / 'build_styled_md_pdf.py'), str(doc), str(pdf), '--compact'], check=True)",
     "pages = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout",
     "print(pdf.name, [l for l in pages.splitlines() if l.startswith('Pages')])"),
md("## Figure atlas — the document as pictures only",
   "",
   "User ruling 2026-09-17: the figures without the prose. `atlas.render` draws every figure from the",
   "live dataset into `atlas/` (PNG) and `PRELIMINARY_ANALYSIS_FIGURES.pdf` (one figure per page)."),
code("from src.dataset_facts import atlas",
     "atlas_pdf, atlas_pngs = atlas.render(ds, OUT, N)",
     "print(atlas_pdf.name, len(atlas_pngs), 'figures')"),

# ---------------- appendix ----------------
*notes("appendix"),
md("---", "## Appendix — the framework-document sections the document does not print",
   "",
   "Kept here because they are measured on the same data and because `published.check` (the drift",
   "check of every number the framework document prints) depends on them. They are results of",
   "Ch. 4–7, not of the preliminary analysis. The codebook consistency rules (the L- and N-series of",
   "the conformance harness) are run by `export.build_all` and written to `tables/rules_codebook*.csv`."),
md("### A.4 Architecture from the text, and its confirmation"),
code("display(a4.what_was_done(ds))",
     "display(a4.agreement_with_images(ds))",
     "display(a4.agreement_by_type(ds))",
     "display(a4.disagreements(ds))",
     "a4.confusion_matrix(ds)"),
code("protocol = a4.confirmation_protocol(ds)",
     "display(protocol)",
     "print(protocol.attrs)",
     "display(a4.citation_quality(ds))",
     "display(a4.known_aircraft_list(ds).head(10))",
     "multi = a4.multi_aircraft_patents(ds)",
     "display(multi)",
     "print(multi.attrs)",
     "a4.final_state(ds)"),
md("### A.6 The identity variables: what the patents themselves say"),
code("display(a6.evidence_per_variable(ds))",
     "display(a6.powertrain_without_evidence(ds))",
     "outcome = a6.reading_outcome(ds)",
     "display(outcome)",
     "print(outcome.attrs)",
     "display(a6.powertrain_vocabulary(ds))",
     "display(a6.contradiction_summary(ds))",
     "display(a6.contradictions(ds))",
     "a6.gazetteer_ambiguous_companies(ds).head(10)"),
md("### A.1 Where each information source stands (framework table)"),
code("a1.source_state_table(ds)"),
md("### Does the framework document still match the data?",
   "",
   "`published.py` holds every number Part A of the framework document prints, next to the call that",
   "recomputes it. A **drift** row means the dataset moved after the document was written, that the",
   "document's definition was wrong and the package uses the corrected one, or — with",
   "`source: batch_xlsx` — that the document was measured on notebook 04's join and the batch files",
   "differ from it. Read the note column."),
code("check = published.check(ds, tolerance=F.get('tolerance', 0.006))",
     "print(check['status'].str.split(':').str[0].value_counts().to_dict())",
     "check[check['status'] != 'match']"),
code("published.summary(ds)"),
]

nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"c{i:03d}-{uuid.uuid5(uuid.NAMESPACE_URL, c['source'][:80]).hex[:6]}"
out = ROOT / "notebooks" / "10_preliminary_analysis.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print("wrote", out, len(cells), "cells")
