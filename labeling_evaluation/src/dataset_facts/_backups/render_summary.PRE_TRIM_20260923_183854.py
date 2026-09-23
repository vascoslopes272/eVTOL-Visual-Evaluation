#!/usr/bin/env python3
"""Generate LABELLING_ANALYSIS_BRIEF.md and its PDF — the compact Labelling Analysis.

    python3 scripts/render_summary.py [--pdf] [--out <folder>]

The brief is the eight sector questions, each answered in a paragraph and carried by the two
to four items the question map grades **core**. It is a SECOND VIEW OF THE SAME DATA, not a
second analysis:

* every table is read from ``tables/<name>.csv`` as the full render wrote it — never rebuilt.
  A round-trip check confirms the CSV reproduces the markdown the full document printed for
  all 148 tables, byte for byte;
* every figure is the PNG or SVG already in ``figures/`` — never redrawn, so a figure obeys
  the document's rules (7.09 in wide, 200 dpi, 7 pt floor, monochrome) by being the same file;
* only ``numbers.live`` is recomputed, in about five seconds, and it is a pure function of the
  same master labels.

It therefore CANNOT be run before ``render_labelling_analysis.py`` has produced that folder,
and it never runs it: this script writes one new pair of files into the folder and touches
nothing else in it.

Guards, all of them fatal rather than cosmetic:
  1. every item the brief lists must exist on disk;
  2. every item must be graded ``core`` in ``la_index.GRADE``, or be named in
     ``sm_index.NOT_CORE`` with its reason;
  3. no ``{placeholder}`` may survive into the rendered markdown — a grey line may degrade to
     an ellipsis, a stated answer may not;
  4. LABELLING_ANALYSIS.md must not change; its mtime and size are checked around the run.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

PILLAR = Path(__file__).resolve().parent.parent
REPO = PILLAR.parent
sys.path.insert(0, str(PILLAR))
from src.config_loader import load_config                                        # noqa: E402
from src.dataset_facts import la_index, numbers, report, sm_index                 # noqa: E402
from src.dataset_facts import load_dataset                                        # noqa: E402

#: name -> file stem, where the drawn file is not ``<name>.png``. Same mapping the full
#: render uses: the two codebook drawings are copied in under their own file names, and two
#: schemes are SVG.
SPECIAL = {
    "codebook_classes": "codebook_architecture_classes.png",
    "codebook_dimensions": "codebook_every_dimension.png",
    "design_space_cards": "design_space_cards.svg",
    "fig_02_refinement_funnel": "fig_02_refinement_funnel.svg",
}


def escape_pipes(frame: pd.DataFrame) -> pd.DataFrame:
    """A cell's own ``|`` escaped, so the markdown table survives it.

    ``to_markdown`` writes a cell's ``|`` straight into the row; python-markdown's ``tables``
    extension then reads it as a column separator and DROPS everything after it, silently. One
    cell in the whole ``tables/`` folder carries one — Gower's coefficient in
    ``la_dd_conditions``, ``1 − |xi − xj| / range`` — and it is the cell that says where
    condition 3's threshold comes from, so it is escaped rather than lost. A cell with no ``|``
    is returned untouched, which is every other cell of every other table: the escape cannot
    move a number or a word anywhere else in the document.

    The same cell is truncated in the FULL document, which prints the same table from the same
    CSV through the same renderer. That is not fixed here — this script must leave
    LABELLING_ANALYSIS.md byte-identical — and is reported to the author instead.
    """
    for col in frame.columns[frame.dtypes.eq(object)]:
        frame[col] = frame[col].map(
            lambda v: v.replace("|", r"\|") if isinstance(v, str) and "|" in v else v)
    return frame


def load_tables(out: Path) -> dict:
    """Every table the full render wrote, read back from its CSV. Nothing is recomputed.

    ``keep_default_na=False`` is deliberate: several option ids in this corpus are literally
    "NA" or "None" and pandas would turn them into blanks.
    """
    tdir = out / "tables"
    if not tdir.is_dir():
        raise SystemExit(f"no tables/ under {out} — run render_labelling_analysis.py first")
    return {c.stem: escape_pipes(pd.read_csv(c, keep_default_na=False))
            for c in sorted(tdir.glob("*.csv"))}


def load_figures(out: Path) -> dict:
    """Every figure the full render drew, by name. Nothing is redrawn."""
    fdir = out / "figures"
    if not fdir.is_dir():
        raise SystemExit(f"no figures/ under {out} — run render_labelling_analysis.py first")
    figs = {}
    for name in {n for node in la_index.NODES for n in node.get("figures", [])}:
        path = fdir / SPECIAL.get(name, f"{name}.png")
        if path.exists():
            figs[name] = path
    return figs


def fit_widths(figs: dict) -> None:
    """Print every PNG at its drawn size, as the full render does: 200 dpi against a 7.087 in
    text block, so a 7 pt letter stays 7 pt on paper. Writes into ``sm_index.FIG_WIDTH``,
    which is a copy — ``la_index.FIG_WIDTH`` is never touched."""
    from PIL import Image
    for name, path in figs.items():
        if str(path).endswith(".png") and name not in sm_index.LANDSCAPE:
            with Image.open(path) as im:
                sm_index.FIG_WIDTH[name] = f"{min(100, round(im.size[0] / 200 / 7.087 * 100))}%"


def check_selection(figs: dict, tables: dict) -> list:
    """Guards 1 and 2: every listed item exists, and every one of them is graded core."""
    problems = []
    for node in sm_index.NODES:
        for name in node.get("figures", []):
            if name not in figs:
                problems.append(f"{node['id']}: figure {name} is not in figures/")
        for name in node.get("tables", []):
            if name not in tables:
                problems.append(f"{node['id']}: table {name} is not in tables/")
    listed = [n for node in sm_index.NODES
              for n in node.get("figures", []) + node.get("tables", [])]
    for name in listed:
        grade = la_index.GRADE.get(name)
        if grade != "core" and name not in sm_index.NOT_CORE:
            problems.append(f"{name} is graded {grade!r}, and is not in sm_index.NOT_CORE")
    return problems


def check_placeholders(md: Path) -> list:
    """Guard 3: nothing of the form ``{key}`` may reach the reader."""
    text = md.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"\{[a-z_][a-z0-9_]*\}", text)))


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--flow", action="store_true",
                    help="let the page flow instead of binding each heading to the "
                         "figure under it (test setting; the binding is the default)")
    ap.add_argument("--out", default=None,
                    help="write here instead of the labelling_analysis folder (for a test run; "
                         "figures/ and tables/ must resolve from it)")
    args = ap.parse_args(argv)
    KEEP = not args.flow

    cfg = load_config()
    facts = dict(cfg["dataset_facts"])
    partial = facts.get("partial_window_start", 2024)
    source = Path(facts["output_dir"]).parent / "labelling_analysis"
    out = Path(args.out) if args.out else source
    out.mkdir(parents=True, exist_ok=True)

    full_md = source / "LABELLING_ANALYSIS.md"
    before = (full_md.stat().st_mtime_ns, full_md.stat().st_size) if full_md.exists() else None

    tables = load_tables(out)
    figs = load_figures(out)
    problems = check_selection(figs, tables)
    if problems:
        for p in problems:
            print("SELECTION:", p)
        return 2
    fit_widths(figs)

    # the item's number in the FULL document, computed the way that document numbers it
    sm_index.set_full_reference(set(figs), set(tables))

    ds = load_dataset(cfg)
    values = sm_index.resolve(numbers.live(ds, partial), tables)
    values["partial_start"] = partial

    import json
    panels_file = out / "figures" / "panels.json"
    panels = json.loads(panels_file.read_text(encoding="utf-8")) if panels_file.exists() else {}
    panels = {k: [tuple(p) for p in v] for k, v in panels.items()}

    generated = (
        f"Date: {dt.date.today().isoformat()} · Generated by "
        f"`labeling_evaluation/scripts/render_summary.py` from the tables and figures of "
        f"LABELLING_ANALYSIS (notebook 04; PatSeer snapshot {values['snapshot']}) · The short "
        f"form: one section per sector question, only the items graded core, every number read "
        f"from `tables/` at render time. The other items, and the unit-base-transform line of "
        f"every item here, are in LABELLING_ANALYSIS.pdf.")

    # the writer gets a copy with ``sm_index.ROW_FILTER`` applied (the most-common-answers
    # table without its near-unanimous rows); every number above was read from the unfiltered
    # tables, so no placeholder changes value
    md = report.write_markdown(None, sm_index.filter_rows(tables), figs, out,
                               filename="LABELLING_ANALYSIS_BRIEF.md",
                               values=values, partial_window_start=partial, idx=sm_index,
                               generated_by=generated, keep_with_next=KEEP, panels=panels)

    left = check_placeholders(md)
    if left:
        print("UNRESOLVED PLACEHOLDERS:", ", ".join(left))
        return 3

    n_fig = sum(len(n.get("figures", [])) for n in sm_index.NODES)
    n_tab = sum(len(n.get("tables", [])) for n in sm_index.NODES)
    print(f"items: {n_fig} figures + {n_tab} tables   "
          f"(full document: {sum(len(n.get('figures', [])) + len(n.get('tables', [])) for n in la_index.NODES)})")
    print(f"document: {md}  ({md.stat().st_size / 1024:.0f} KB)")

    if args.pdf:
        pdf = md.with_suffix(".pdf")
        subprocess.run([sys.executable, str(REPO / "scripts" / "build_styled_md_pdf.py"),
                        str(md), str(pdf), "--compact"], check=True)
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        print(pdf.name, [l for l in info.splitlines() if l.startswith("Pages")])

    if before is not None:
        now = (full_md.stat().st_mtime_ns, full_md.stat().st_size)
        print("LABELLING_ANALYSIS.md unchanged:", now == before)
        if now != before:
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
