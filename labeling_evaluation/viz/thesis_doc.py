"""Write the thesis analysis document (LaTeX) from the thesis layer and compile it: used by notebook 47.

    from viz import thesis_doc
    pdf = thesis_doc.build(cfg)            # <output>/thesis_document/main.tex + main.pdf (tectonic)

Reads: viz/thesis_text_common.py, viz/thesis_text_qN.py (the prose, with {placeholders} and [fig:]/[tab:]/[hl] markup),
viz/thesis_qN.py ITEMS (what each figure/table is), and what notebook 46 saved under <output>/thesis_figures/
(the graphs as pdf, the tables as csv, numbers.json per question). Computes nothing.

Document: Methodology (common method, statistics table, one Method per question) → Results and discussion (three
parts, seven questions, sub-questions A–D with their main-text figures and tables, an Answer box per question) →
Limitations → Appendix (per question: the appendix items, each with its caption and one takeaway line).
Flags of the author (decide / verify / drop) print yellow (\\hl) with a margin tag.
"""
from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from viz import latex, thesis

PH = re.compile(r"(?<!\{)\{([a-zA-Z0-9_]+)\}(?!\})")
TOKEN = re.compile(r"(\[fig:[a-z0-9_]+\]|\[tab:[a-z0-9_]+\]|\[hl\]|\[/hl\]|\*\*)")
FLAG_WORDS = {"decide": "to decide", "verify": "to verify", "drop": "proposed to drop"}

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[british]{babel}
\usepackage[a4paper,textwidth=6.3in,top=26mm,bottom=26mm,marginparwidth=18mm]{geometry}   % textwidth = style.text_width_in of the yaml
\usepackage{graphicx,booktabs,amssymb,amsmath,xcolor,soul,array,longtable,caption,setspace,microtype,ragged2e,enumitem}
\usepackage{placeins}
\usepackage[hidelinks]{hyperref}
\sethlcolor{yellow}
\captionsetup{font=small,labelfont=bf,width=0.92\textwidth}
\setstretch{1.15}
\setlist{nosep}
\newcommand{\flagtag}[1]{\marginpar{\footnotesize\colorbox{yellow}{\strut #1}}}
\newcommand{\flagline}[1]{{\footnotesize\colorbox{yellow}{\strut Author: #1}}\par\smallskip}
\newenvironment{answerbox}{\par\medskip\noindent\begin{minipage}{\textwidth}\hrule\smallskip\small\noindent\textbf{Answer.}\ }{\smallskip\hrule\end{minipage}\par\medskip}
\setcounter{secnumdepth}{4}
\setcounter{tocdepth}{2}
\title{Chapter 4 --- Analysis\\[2pt]\large eVTOL patents: the sector, the built sector, and convergence}
\date{\today}
\author{}
"""


# ------------------------------------------------------------------------------------------ text → LaTeX
def resolve(text: str, nums: Dict[str, str], where: str) -> str:
    def rep(m):
        k = m.group(1)
        if k not in nums:
            raise KeyError(f"{where}: unresolved number {{{k}}}")
        return nums[k]
    return PH.sub(rep, text)


def _inline(text: str, where: str) -> str:
    """Inline markup of one line or paragraph: [fig:x] → Figure~\\ref, [hl] → \\hl, **b** → \\textbf; the rest escaped."""
    out, bold, hl = [], False, False
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("[fig:") or part.startswith("[tab:"):
            ref = (r"Figure~\ref{fig:" if part.startswith("[fig:") else r"Table~\ref{tab:") + part[5:-1] + "}"
            out.append(("}" + ref + r"\hl{") if hl else ref)      # soul's \hl cannot hold a \ref: close and reopen
        elif part == "[hl]":
            out.append(r"\hl{"); hl = True
        elif part == "[/hl]":
            out.append("}"); hl = False
        elif part == "**":
            out.append("}" if bold else r"\textbf{"); bold = not bold
        else:
            out.append(re.sub(r" {2,}", " ", latex.escape(part)))
    assert not bold and not hl, f"{where}: unclosed ** or [hl]"
    return "".join(out)


def _para(p: str, where: str) -> str:
    """One paragraph; lines starting with "- " form an itemize (a "**Label:**" start becomes the bold label)."""
    lines = [l.strip() for l in p.strip("\n").split("\n") if l.strip()]
    if not lines:
        return ""
    if all(l.startswith("- ") for l in lines):
        return "\\begin{itemize}\n" + "\n".join(r"\item " + _inline(l[2:].strip(), where) for l in lines) + "\n\\end{itemize}"
    return _inline(" ".join(lines), where)


def render(text: str, nums: Dict[str, str], where: str) -> str:
    """Markup → LaTeX: numbers resolved, paragraphs split on blank lines, "- " lines itemised, inline markup applied."""
    text = resolve(text.strip(), nums, where)
    paras = re.split(r"\n[ \t]*\n", text)
    return "\n\n".join(x for x in (_para(p, where) for p in paras) if x)


def cites(text: str) -> List[str]:
    """Item names cited, in order of first appearance."""
    seen = []
    for m in re.finditer(r"\[(?:fig|tab):([a-z0-9_]+)\]", text):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


# ------------------------------------------------------------------------------------------ items → LaTeX
def _flag_prefix(item: dict) -> str:
    if not item.get("flag"):
        return ""
    note = latex.escape(item.get("flag_note") or FLAG_WORDS[item["flag"]])
    return rf"\hl{{[{FLAG_WORDS[item['flag']].capitalize()}: {note}]}} "


def _caption(item: dict, takeaway: str = "", nums=None) -> str:
    cap = latex.escape(item["caption"].rstrip("."))
    if takeaway:
        cap += ". " + r"\textit{" + render(takeaway.rstrip("."), nums or {}, item["name"]) + "}"
    return _flag_prefix(item) + cap + "."


def figure_block(item: dict, src: Path, docdir: Path, textwidth_in: float, takeaway: str = "", nums=None) -> str:
    meta = json.loads(src.with_suffix(".json").read_text(encoding="utf-8"))
    w = min(float(meta.get("width_in", textwidth_in)), textwidth_in - 0.01)
    (docdir / "figures").mkdir(exist_ok=True)
    shutil.copy2(src, docdir / "figures" / src.name)
    tag = rf"\flagline{{{FLAG_WORDS[item['flag']]}}}" if item.get("flag") else ""
    return "\n".join([r"\begin{figure}[htb]", r"\centering",
                      rf"\includegraphics[width={w:.2f}in]{{figures/{src.name}}}",
                      tag, rf"\caption{{{_caption(item, takeaway, nums)}}}", rf"\label{{fig:{item['name']}}}",
                      r"\end{figure}", ""])


def table_block(item: dict, src: Path, takeaway: str = "", nums=None) -> str:
    frame = pd.read_csv(src, keep_default_na=False, na_values=[""])
    meta = {"caption": _caption(item, takeaway, nums).rstrip(".")}
    tex = latex.table_tex(frame, {"caption": ""}, item["name"])
    # latex.table_tex escapes the caption; ours is already LaTeX → swap it in
    tex = tex.replace(r"\caption{.}", rf"\caption{{{meta['caption']}.}}", 1)
    if item.get("flag"):
        tex = tex.replace(r"\centering", r"\centering" + "\n" + rf"\flagline{{{FLAG_WORDS[item['flag']]}}}", 1)
    lens = frame.astype(str).apply(lambda c: max(c.str.len().max(), len(str(c.name))))
    width_chars = int(lens.sum()) + 3 * len(frame.columns)
    if width_chars > 70:
        tex = tex.replace(r"\small", r"\footnotesize", 1)
    if width_chars > 95:                       # wider than the page: wrapped columns, widths by content, text still ≥ 7 pt
        capped = lens.clip(lower=6, upper=44).astype(float)
        tex = tex.replace(r"\footnotesize", r"\scriptsize", 1) if capped.sum() + 3 * len(frame.columns) > 150 else tex
        share = (capped / capped.sum()) * 0.96
        spec = "".join(f"p{{{w:.3f}\\textwidth}}" for w in share)
        tex = re.sub(r"\\begin\{tabular\}\{[lr]+\}", lambda m: r"\begin{tabular}{" + spec + "}", tex, count=1)
        tex = tex.replace(r"\begin{tabular}", r"\setlength{\tabcolsep}{3pt}\RaggedRight" + "\n" + r"\begin{tabular}", 1)
    return tex


# ------------------------------------------------------------------------------------------ the document
def _load(qid: str):
    n = qid[1]
    return importlib.import_module(f"viz.thesis_q{n}"), importlib.import_module(f"viz.thesis_text_q{n}")


def _numbers(cfg, qid: str) -> Dict[str, str]:
    p = cfg.out("thesis_figures") / thesis.folder(qid) / "numbers.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} — run notebook 46 first")
    return json.loads(p.read_text(encoding="utf-8"))


def _item_path(cfg, item: dict) -> Path:
    qid = item["name"][:2].upper()
    d = thesis.out_dir(cfg, qid, item["slot"], make=False)
    return d / (item["name"] + (".pdf" if item["kind"] == "figure" else ".csv"))


def stats_table(stats: List[dict], nums: Dict[str, str] = None) -> str:
    rows = []
    for s in stats:
        rows.append(" & ".join(latex.escape(resolve(str(s.get(k, "")), nums or {}, "STATS")) for k in ("test", "answers", "formula_unicode", "used_in")) + r" \\")
    return "\n".join([r"\begin{table}[htb]", r"\centering", r"\footnotesize",
                      r"\caption{The statistics used, what each answers, and where.}", r"\label{tab:stats}",
                      r"\begin{tabular}{p{0.2\textwidth}p{0.3\textwidth}p{0.26\textwidth}p{0.14\textwidth}}", r"\toprule",
                      r"\textbf{Test} & \textbf{What it answers} & \textbf{Formula} & \textbf{Used in} \\", r"\midrule",
                      *rows, r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])


def build(cfg, compile: bool = True) -> Tuple[Path, Dict]:
    """Write main.tex (+ figures/) and compile it. Returns (pdf or tex path, report dict)."""
    docdir = cfg.out("thesis_document")
    tw = float(cfg.style["text_width_in"])
    common = importlib.import_module("viz.thesis_text_common")
    importlib.reload(common)
    cpath = cfg.out("thesis_figures") / "common" / "numbers.json"
    cnums = json.loads(cpath.read_text(encoding="utf-8")) if cpath.exists() else {}
    report = {"flags": [], "items": 0, "missing": []}

    tex = [PREAMBLE, r"\begin{document}", r"\maketitle", r"\tableofcontents", r"\clearpage", ""]
    tex.append(render(common.CHAPTER_MAP, cnums, "CHAPTER_MAP") + "\n")

    # ---- Methodology
    tex.append(r"\section{Methodology}" + "\n")
    tex.append(r"\subsection{The dataset and the unit of analysis}" + "\n")
    tex.append(render(common.METHOD_COMMON, cnums, "METHOD_COMMON") + "\n")
    cdir = cfg.out("thesis_figures") / "common"
    for js in sorted(cdir.glob("*.json")):                       # chapter-level flowcharts saved by notebook 46
        if js.stem == "numbers":
            continue
        it = json.loads(js.read_text(encoding="utf-8"))
        src = js.with_suffix(".pdf")
        if it.get("slot") == "method" and src.exists():
            tex.append(figure_block(it, src, docdir, tw)); report["items"] += 1
    tex.append(r"\subsection{The statistics}" + "\n")
    tex.append(r"Table~\ref{tab:stats} lists every test the chapter uses." + "\n")
    tex.append(stats_table(common.STATS, cnums))
    for qid, slug, part, question in thesis.QUESTIONS:
        items, text = _load(qid)
        importlib.reload(items); importlib.reload(text)
        nums = {**cnums, **_numbers(cfg, qid)}
        tex.append(rf"\subsection{{{qid}. {latex.escape(question)}}}" + "\n")
        tex.append(render(text.METHOD, nums, f"{qid}.METHOD") + "\n")
        for it in items.ITEMS:
            if it["slot"] == "method":
                src = _item_path(cfg, it)
                if src.exists():
                    tex.append(figure_block(it, src, docdir, tw) if it["kind"] == "figure" else table_block(it, src))
                    report["items"] += 1
                else:
                    report["missing"].append(str(src))

    # ---- Results and discussion
    tex.append(r"\clearpage" + "\n" + r"\section{Results and discussion}" + "\n")
    last_part = None
    for qid, slug, part, question in thesis.QUESTIONS:
        items, text = _load(qid)
        nums = {**cnums, **_numbers(cfg, qid)}
        by_name = {it["name"]: it for it in items.ITEMS}
        if part != last_part:
            tex.append(rf"\subsection{{{latex.escape(part)}}}" + "\n")
            last_part = part
        tex.append(r"\FloatBarrier" + "\n" + rf"\subsubsection{{{qid}. {latex.escape(question)}}}" + "\n")
        placed = set()
        for sub in text.RESULTS:
            tex.append(rf"\paragraph{{{sub['sub']}. {latex.escape(sub['title'])}}}" + "\n")
            paras = re.split(r"\n\s*\n", sub["text"].strip())
            for p in paras:
                tex.append(render(p, nums, f"{qid}.RESULTS[{sub['sub']}]") + "\n")
                for name in cites(p):
                    it = by_name.get(name)
                    if it is None or it["slot"] != "results" or name in placed:
                        continue
                    placed.add(name)
                    src = _item_path(cfg, it)
                    if not src.exists():
                        report["missing"].append(str(src)); continue
                    tex.append(figure_block(it, src, docdir, tw) if it["kind"] == "figure" else table_block(it, src))
                    report["items"] += 1
                    if it.get("flag"):
                        report["flags"].append((qid, name, it["flag"], it["flag_note"]))
        for it in items.ITEMS:   # results items never cited: placed at the end, so nothing is lost
            if it["slot"] == "results" and it["name"] not in placed:
                src = _item_path(cfg, it)
                if src.exists():
                    tex.append(figure_block(it, src, docdir, tw) if it["kind"] == "figure" else table_block(it, src))
                    report["items"] += 1
        tex.append(r"\FloatBarrier" + "\n" + r"\begin{answerbox}" + "\n" + render(text.ANSWER, nums, f"{qid}.ANSWER") + "\n" + r"\end{answerbox}" + "\n")

    # ---- Limitations
    tex.append(r"\clearpage" + "\n" + r"\section{Limitations}" + "\n")
    tex.append(render(common.LIMITATIONS, cnums, "LIMITATIONS") + "\n")
    for qid, *_ in thesis.QUESTIONS:
        items, text = _load(qid)
        for it in items.ITEMS:
            if it["sub"] == "" and it["slot"] == "appendix" and "limitation" in (it.get("flag_note") or "").lower():
                src = _item_path(cfg, it)
                if src.exists():
                    nums = {**cnums, **_numbers(cfg, qid)}
                    tex.append(table_block(it, src, text.APPENDIX.get(it["name"], ""), nums) if it["kind"] == "table"
                               else figure_block(it, src, docdir, tw, text.APPENDIX.get(it["name"], ""), nums))
                    report["flags"].append((qid, it["name"], it["flag"], it["flag_note"]))

    # ---- Appendix
    tex.append(r"\clearpage" + "\n" + r"\appendix" + "\n" + r"\section{Supporting figures and tables, by question}" + "\n")
    tex.append("Each item carries its caption and, in italics, the one finding it supports. Yellow marks are the author's open decisions.\n")
    for qid, slug, part, question in thesis.QUESTIONS:
        items, text = _load(qid)
        nums = {**cnums, **_numbers(cfg, qid)}
        app = [it for it in items.ITEMS if it["slot"] == "appendix" and not (it["sub"] == "" and "limitation" in (it.get("flag_note") or "").lower())]
        if not app:
            continue
        tex.append(r"\FloatBarrier" + "\n" + rf"\subsection{{{qid}. {latex.escape(question)}}}" + "\n")
        for it in app:
            src = _item_path(cfg, it)
            if not src.exists():
                report["missing"].append(str(src)); continue
            take = text.APPENDIX.get(it["name"], "")
            tex.append(figure_block(it, src, docdir, tw, take, nums) if it["kind"] == "figure" else table_block(it, src, take, nums))
            report["items"] += 1
            if it.get("flag"):
                report["flags"].append((qid, it["name"], it["flag"], it["flag_note"]))
        tex.append(r"\clearpage" + "\n")
    tex.append(r"\end{document}" + "\n")

    main = docdir / "main.tex"
    main.write_text("\n".join(tex), encoding="utf-8")
    report["tex"] = str(main)
    if not compile:
        return main, report
    pdf = compile_tex(cfg, main)
    report["pdf"] = str(pdf)
    report["pages"] = page_count(pdf)
    return pdf, report


def compile_tex(cfg, main: Path) -> Path:
    engine = cfg.raw.get("tools", {}).get("tectonic", "tectonic")
    r = subprocess.run([engine, "--keep-logs", str(main.name)], cwd=main.parent, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("tectonic failed:\n" + r.stdout[-3000:] + r.stderr[-3000:])
    return main.with_suffix(".pdf")


def page_count(pdf: Path) -> int:
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    m = re.search(r"Pages:\s+(\d+)", r.stdout)
    return int(m.group(1)) if m else -1


def pages_png(pdf: Path, out: Path, dpi: int = 60, first: int = 1, last: int = 0) -> List[Path]:
    """Render pages to PNG (pdftoppm) for a look in the notebook; returns the files."""
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("page*.png"):                  # stale pages of a longer earlier build
        old.unlink()
    args = ["pdftoppm", "-png", "-r", str(dpi), "-f", str(first)]
    if last:
        args += ["-l", str(last)]
    subprocess.run(args + [str(pdf), str(out / "page")], check=True)
    return sorted(out.glob("page*.png"))
