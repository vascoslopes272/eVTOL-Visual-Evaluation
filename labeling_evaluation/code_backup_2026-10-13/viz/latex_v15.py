"""Export of the Part I (Analysis I) figures to the dissertation folder LaTeX_v15/, with the data behind them and the numbers the
Results text quotes. Called by notebook 48 (section "Export to LaTeX_v15"); nothing here changes a number, a test or a result.

    LaTeX_v15/
      Figures/Part_I_evidence_base/<group>/<role>/<name>.pdf     vector PDF at the final width of the dissertation (text block 16 cm)
      Data_for_writing/csv/<name>.csv                            the data behind every figure
      Data_for_writing/csv/numbers_I_*.csv                       the tables behind the numbers file
      Data_for_writing/NUMBERS_I.md                              every number of the Results text of Analysis I, with its source
      Data_for_writing/MANIFEST.md                               one line per file (appended to, never overwritten)

The folder is created next to the other thesis outputs (…/labelling_analysis_thesis/LaTeX_v15) because the repository folder of the
dissertation is not on this machine; copy it over the repository's LaTeX_v15/.
"""
from __future__ import annotations

import datetime
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from lib import association
from viz import frames

#: figures of the remake prompt that stay in the dissertation text (yes) and those that leave it (no, still delivered)
USED = {"q1_filings_per_year": True, "q4_patent_vs_market_clock": True, "q4_class_mix": True,
        "q1_growth_rates": False, "q1_in_force_status": False, "q5_funding_vs_aircraft": False, "q5_patenting_vs_investment": False}
SHOWS = {
    "q1_filings_per_year": "Designs filed per priority year, stacked by architecture group, 2024-26 faded; patent families as a line; five dated sector events",
    "q1_growth_rates": "Growth of eVTOL architecture patents against aeronautics, transport and all patenting, relative to 2005-09, log scale (width not given: 1.0, as in the dissertation before)",
    "q4_patent_vs_market_clock": "One row per AAM Reality Index firm that files here: first to last patent, peak year, first flight, entry into service",
    "q1_in_force_status": "Share of designs not actively protected, by architecture and by filing office (US against the other offices), the nine architectures of ten designs or more, 604 designs (width not given: 1.0; appendix at most)",
    "q4_class_mix": "Architecture mix per priority-year cohort, patent dataset next to the VFS eVTOL directory",
    "q5_funding_vs_aircraft": "Disclosed funding of the index firms against their designs in the patent dataset (width not given: 0.6, as in the dissertation before)",
    "q5_patenting_vs_investment": "Designs per priority year against disclosed sector investment per year, one dot per published period (width not given: 0.6, as in the dissertation before)",
}


def root(cfg) -> Path:
    return cfg.out("thesis_figures").parent / "LaTeX_v15"


def _pdf_size_in(path: Path):
    """(width, height) in inches from the PDF's own page size, or None when pdfinfo is not installed."""
    exe = shutil.which("pdfinfo")
    if not exe:
        return None
    out = subprocess.run([exe, str(path)], capture_output=True, text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", out)
    return (float(m.group(1)) / 72, float(m.group(2)) / 72) if m else None


def export_figures(cfg, v2) -> pd.DataFrame:
    """Copy the final-size figures (items with a ``width``) and their CSV to LaTeX_v15/, check the PDF page size, append the manifest."""
    base = root(cfg)
    rows = []
    for it in v2.ITEMS:
        if not it.get("width"):
            continue
        name = it["name"]
        src = v2.out_root(cfg) / it["group"] / it["role"]
        dst = base / "Figures" / "Part_I_evidence_base" / it["group"] / it["role"]
        dst.mkdir(parents=True, exist_ok=True)
        (base / "Data_for_writing" / "csv").mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / f"{name}.pdf", dst / f"{name}.pdf")
        shutil.copy2(src / f"{name}.csv", base / "Data_for_writing" / "csv" / f"{name}.csv")
        size = _pdf_size_in(dst / f"{name}.pdf")
        want = it["width"] * v2.TEXT_W_IN
        rows.append({"file": name, "pdf": str((dst / f"{name}.pdf").relative_to(base)), "csv": f"Data_for_writing/csv/{name}.csv",
                     "final width fraction": it["width"], "width cm": round(size[0] * 2.54, 2) if size else "", "height cm": round(size[1] * 2.54, 2) if size else "",
                     "width ok": bool(size and abs(size[0] - want) < 0.01), "height / width": round(size[1] / size[0], 3) if size else "",
                     "height ok (<= 0.55)": bool(size and size[1] <= 0.55 * size[0] + 1e-3),
                     "used in the dissertation": "yes" if USED.get(name) else "no (leaves the text)"})
    rep = pd.DataFrame(rows)
    _append_manifest(base, [(r["pdf"], r["used in the dissertation"], SHOWS.get(r["file"], r["file"])) for _, r in rep.iterrows()]
                     + [(r["csv"], r["used in the dissertation"], "data behind " + r["file"]) for _, r in rep.iterrows()])
    return rep


def _append_manifest(base: Path, entries):
    """MANIFEST.md, in the format the other analyses already use: one bullet per file, ``- `LaTeX_v15/<path>` · used · what it shows``.
    Existing lines are kept; a line for a path written again is replaced, never duplicated."""
    p = base / "Data_for_writing" / "MANIFEST.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    head = ["# MANIFEST", "", "One line per file: path · used in the dissertation · what it shows.", ""]
    old = p.read_text(encoding="utf-8").splitlines() if p.exists() else head
    mine = {f"`LaTeX_v15/{e[0]}`" for e in entries}
    kept = [ln for ln in old if not ln.startswith("| ") and not (ln.startswith("- ") and ln[2:].split(" · ")[0].strip() in mine)]
    kept += [f"- `LaTeX_v15/{a}` · {'yes' if b in (True, 'yes') else ('no' if b is False else b)} · {c}" for a, b, c in entries]
    p.write_text("\n".join(kept) + "\n", encoding="utf-8")


# ======================================================================================== the numbers file
def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join("" if (isinstance(x, float) and np.isnan(x)) else str(x) for x in r) + " |")
    return "\n".join(lines)


def _placeholders(text: str):
    return re.findall(r"\{([a-z0-9_]+)\}", text)


def write_numbers_I(cfg, ctx) -> Path:
    """DATA/NUMBERS_I.md, built from live computations (no number is typed): the numbers of the remake prompt, the checks requested on
    2026-10-12, and every number the Results text of Analysis I quotes, each with its source."""
    from viz import data as vdata
    from viz import thesis_q1 as q1, thesis_q4 as q4, thesis_q5 as q5
    from viz import thesis_text_q1 as t1, thesis_text_q4 as t4, thesis_text_q5 as t5
    base = root(cfg)
    D = base / "Data_for_writing"
    CSV = D / "csv"
    CSV.mkdir(parents=True, exist_ok=True)
    v, ds = ctx.v, ctx.ds
    c = q1._calc(ctx)
    n1, n4, n5 = q1.numbers(ctx), q4.numbers(ctx), q5.numbers(ctx)
    out = [f"# NUMBERS_I — Analysis I (evidence base)",
           "", f"Generated {datetime.date.today().isoformat()} by notebook 48 (`viz/latex_v15.py:write_numbers_I`) from the current inputs "
           f"(external inputs: `{cfg.analysis.get('external_inputs', 'script')}`), 627 designs, snapshot {frames.snapshot_date(ds)}. "
           "Every value is computed when this file is written; the source column names the CSV or the code that holds it. "
           "A value marked **new** is a number the earlier text did not quote.", ""]

    def table(title, rows, cols=("number", "value", "source")):
        out.append(f"### {title}\n")
        out.append(_md_table(pd.DataFrame(rows, columns=list(cols))))
        out.append("")

    # ----------------------------------------------------------------------------------- 1 growth
    rates = c["rates"][c["rates"]["primary"]].set_index("key")
    ratios = c["ratios"][c["ratios"]["primary"]]
    tp = c["tp"]
    S1 = "csv/numbers_I_growth.csv"
    g = pd.concat([rates.reset_index()[["series", "window", "total", "doubling time (years)", "95 % interval", "growth per year"]],
                   ratios.rename(columns={"eVTOL counted as": "series", "against": "series against"})[["series", "series against", "times as fast", "95 % interval"]]
                   .assign(kind="ratio")], ignore_index=True)
    g.to_csv(CSV / "numbers_I_growth.csv", index=False)
    tpt = pd.DataFrame([{"series": k, "turning point year": d["break"], "jump factor": round(d["jump"], 2), "share of the resampled fits choosing it": round(d["share"], 3),
                         "95 % range of the resampled turning point, low": d["lo"], "95 % range, high": d["hi"]} for k, d in tp.items()])
    tpt.to_csv(CSV / "numbers_I_turning_points.csv", index=False)
    out.append("## 1. Growth\n")
    r = lambda k: rates.loc[k]                                                                                  # noqa: E731
    ra = lambda who, ag: ratios[(ratios["eVTOL counted as"] == who) & (ratios["against"].str.startswith(ag))].iloc[0]      # noqa: E731
    table("Doubling times, 2005-2023 (years, 95 % interval)", [
        ("eVTOL architecture patents (families)", f"{r('evtol_families')['doubling time (years)']} ({r('evtol_families')['95 % interval']})", f"csv/q1_growth_rates.csv; {S1}; q1.numbers()['dbl_fam']"),
        ("eVTOL unique designs", f"{r('evtol_aircraft')['doubling time (years)']} ({r('evtol_aircraft')['95 % interval']})", f"{S1}; q1.numbers()['dbl_ac']"),
        ("aeronautics (CPC B64)", f"{r('b64')['doubling time (years)']} ({r('b64')['95 % interval']})", f"{S1}; q1.numbers()['dbl_b64']"),
        ("transport and operations (CPC section B)", f"{r('secb')['doubling time (years)']} ({r('secb')['95 % interval']})", f"{S1}; q1.numbers()['dbl_secb']"),
        ("all patenting", f"{r('all')['doubling time (years)']} ({r('all')['95 % interval']})", f"{S1}; q1.numbers()['dbl_all']"),
        ("growth per year, eVTOL architecture patents", r("evtol_families")["growth per year"], f"{S1}")])
    table("Growth-rate ratio of eVTOL architecture patents (times as fast, 95 % interval)", [
        ("against aeronautics (CPC B64)", f"{ra('eVTOL architecture patents', 'aeronautics')['times as fast']} ({ra('eVTOL architecture patents', 'aeronautics')['95 % interval']})", f"{S1}; q1.numbers()['gr_fam_b64'], ['gr_fam_b64_ci']"),
        ("against transport and operations", f"{ra('eVTOL architecture patents', 'transport')['times as fast']} ({ra('eVTOL architecture patents', 'transport')['95 % interval']})", f"{S1}; q1.numbers()['gr_fam_secb']"),
        ("against all patents", f"{ra('eVTOL architecture patents', 'all')['times as fast']} ({ra('eVTOL architecture patents', 'all')['95 % interval']})", f"{S1}; q1.numbers()['gr_fam_all']"),
        ("against aeronautics with the fit ended at 2019 (sensitivity)", f"{n1['gr_fam_b64_19']} ({n1['gr_fam_b64_19_ci']})", "q1.numbers()['gr_fam_b64_19'], ['gr_fam_b64_19_ci']")])
    table("Turning point (two-segment log fit, residual bootstrap, 5 000 draws as set in lib/growth.py)", [
        (f"{k}", f"{d['break']} (jump x{d['jump']:.2f}; chosen by {100 * d['share']:.0f} % of the resampled fits; 95 % range of the resampled year {d['lo']} to {d['hi']})",
         "csv/numbers_I_turning_points.csv; lib/growth.py:turning_point") for k, d in tp.items()])

    # ----------------------------------------------------------------------------------- 2 active protection
    wo, force = c["wo"], c["force"]
    codes = list(force.loc[force["unique aircraft"] >= frames.FORCE_TEST_MIN, "code"])
    big = wo[wo["topType"].isin(codes)]                                       # the 604 designs of the nine architectures
    arch_t = association.chi2_test(pd.crosstab(big["topType"], big["out"]).values)
    off604 = association.chi2_test(pd.crosstab(big["office"], big["out"]).values)
    off625 = association.chi2_test(pd.crosstab(wo["office"], wo["out"]).values)
    by_off = big.groupby("office")["out"].agg(["size", "mean", "sum"])
    by_off625 = wo.groupby("office")["out"].agg(["size", "mean", "sum"])
    notplot = wo[~wo["topType"].isin(codes)].groupby("topType")["out"].agg(["size", "mean"])
    # all 627: the two designs without an architecture are read for their legal status too
    links = frames.aircraft_patents(ds, v)
    links["_live"] = links["status_known"] & ~links["inactive"]
    per = links.groupby("aircraft_id").agg(known=("status_known", "sum"), live=("_live", "any"))
    a627 = v[["aircraft_id", "topType"]].join(per, on="aircraft_id")
    a627["out"] = ~a627["live"].astype(bool)
    a627 = a627[a627["known"].fillna(0) > 0]
    cohort = wo.groupby("window")["out"].agg(["size", "mean"]).reindex(list(ctx.WIN_NAMES))
    cohort604 = big.groupby("window")["out"].agg(["size", "mean"]).reindex(list(ctx.WIN_NAMES))
    arch_rows = (force.set_index("code").loc[codes, ["unique aircraft", "out of force", "out of force share"]]
                 .rename(columns={"unique aircraft": "designs", "out of force": "not actively protected", "out of force share": "share"}).reset_index())
    arch_rows.insert(0, "architecture", [_arch_name(k) for k in arch_rows["code"]])
    arch_rows["code"] = [_arch_short(k) for k in arch_rows["code"]]
    arch_rows.to_csv(CSV / "numbers_I_active_protection_by_architecture.csv", index=False)
    pd.DataFrame({"cohort": [str(i) for i in cohort.index], "designs (625 read)": cohort["size"].astype(int).to_numpy(), "share not actively protected (625)": cohort["mean"].round(3).to_numpy(),
                  "designs (604 plotted)": cohort604["size"].astype(int).to_numpy(), "share not actively protected (604)": cohort604["mean"].round(3).to_numpy()}
                 ).to_csv(CSV / "numbers_I_active_protection_by_cohort.csv", index=False)
    S2 = "csv/q1_in_force_status.csv; csv/numbers_I_active_protection_by_architecture.csv"
    out.append("## 2. Active protection (every priority year; actively protected = any patent that shows the design is in force at the snapshot)\n")
    table("The 604 designs of the nine architectures of ten designs or more (the designs plotted in `q1_in_force_status`)", [
        ("designs plotted", len(big), "csv/q1_in_force_status.csv (sum of n)"),
        ("not actively protected, all 604", f"{int(big['out'].sum())} of {len(big)} = {100 * big['out'].mean():.1f} %", S2),
        ("US office: designs, share not actively protected", f"{int(by_off.loc['US office', 'size'])} designs, {int(by_off.loc['US office', 'sum'])} = {100 * by_off.loc['US office', 'mean']:.1f} %", "csv/q1_in_force_status.csv"),
        ("other offices: designs, share not actively protected", f"{int(by_off.loc['other offices', 'size'])} designs, {int(by_off.loc['other offices', 'sum'])} = {100 * by_off.loc['other offices', 'mean']:.1f} %", "csv/q1_in_force_status.csv"),
        ("test of the architecture (nine architectures x not actively protected)", f"chi-square {arch_t['chi2']:.2f}, df {arch_t['dof']}, p {arch_t['p']:.3f}", "lib/association.chi2_test on the 604 designs; q1.numbers()['fa_p']"),
        ("test of the office (US against other offices x not actively protected), on the 604", f"chi-square {off604['chi2']:.2f}, df {off604['dof']} (Yates correction, 2 x 2), p {off604['p']:.1e}", "lib/association.chi2_test on the 604 designs; **new**"),
        ("the same office test on all 625 designs with an architecture (the earlier text)", f"chi-square {off625['chi2']:.2f}, df {off625['dof']}, p {off625['p']:.1e}; US {100 * by_off625.loc['US office', 'mean']:.1f} % of {int(by_off625.loc['US office', 'size'])}, other offices {100 * by_off625.loc['other offices', 'mean']:.1f} % of {int(by_off625.loc['other offices', 'size'])}", "q1.numbers()['fo_us'], ['fo_else'], ['fo_n_us'], ['fo_n_else'], ['fo_p']")])
    out.append("Share not actively protected per architecture (the nine plotted):\n")
    out.append(_md_table(arch_rows.assign(share=(100 * arch_rows["share"]).round(0).astype(int).astype(str) + " %")))
    out.append("")
    table("Designs not plotted in `q1_in_force_status`", [
        (f"{k} ({_arch_name(k)})", f"{int(r_['size'])} designs, {100 * r_['mean']:.0f} % not actively protected", "csv/numbers_I_active_protection_by_architecture.csv") for k, r_ in notplot.iterrows()]
          + [("no architecture read", f"{int(v['topType'].isna().sum())} designs (read for legal status, see the 627 line)", "viz/frames.py:force_frame drops a design without an architecture"),
             ("designs not plotted, total", f"{len(v) - len(big)} of {len(v)} (604 plotted)", "")])
    table("The share if every one of the 627 designs is read", [
        ("designs with a legal status read", len(a627), "frames.aircraft_patents, every design has at least one patent with a status"),
        ("not actively protected", f"{int(a627['out'].sum())} of {len(a627)} = {100 * a627['out'].mean():.1f} %", "**new**"),
        ("(for comparison) the 625 designs with an architecture", f"{int(wo['out'].sum())} of {len(wo)} = {100 * wo['out'].mean():.1f} %", "q1.numbers()['fa_share'], ['fa_n']")])
    out.append("Share not actively protected per priority-year cohort (the age effect):\n")
    _c = pd.read_csv(CSV / "numbers_I_active_protection_by_cohort.csv")
    for col in [x for x in _c.columns if x.startswith("share")]:
        _c[col] = (100 * _c[col]).round(1).astype(str) + " %"
    out.append(_md_table(_c))
    out.append("")

    # ----------------------------------------------------------------------------------- 3 funnel
    cnt = ds.counts
    dirf = frames.directory_frame(cfg)
    links_f = pd.read_csv(cfg.path("evtolnews_patent_links"), keep_default_na=False)
    matched = links_f[links_f["use"].eq("yes")]
    tl = q4.ari_timeline(ctx)
    cmap = frames.ari_load(cfg)[2]
    firms22 = frames.ari_firms(v, cfg)
    out.append("## 3. The acquisition funnel of section 4.1\n")
    funnel = pd.DataFrame([
        ("patent query hits (PatSeer, snapshot " + frames.snapshot_date(ds) + ")", cnt["patents_acquired"], "ds.counts['patents_acquired']"),
        ("disapproved at labelling (no usable image, pure UAV, out of the domain, other)", cnt["patents_acquired"] - cnt["patents_wizard_approved"], "difference"),
        ("after the patent triage T1: patents approved at labelling", cnt["patents_wizard_approved"], "ds.counts['patents_wizard_approved']"),
        ("approved patents whose every aircraft is 'but similar' (UAV or not electric), set aside", cnt["patents_gated_out"], "ds.counts['patents_gated_out']"),
        ("representative patents (patent families)", cnt["patents_approved"], "ds.counts['patents_approved']"),
        ("aircraft observations (a patent can show several aircraft)", cnt["approved_variants"], "ds.counts['approved_variants']"),
        ("the 627 designs (unique aircraft), on primary patents", len(v), f"len(ctx.v); primary patents {cnt['patents_analysis']}"),
        ("after the image triage T2: whole-aircraft figures approved", cnt["approved_figures"], f"ds.counts['approved_figures']; on {ds.approved_figures['patent_id'].nunique()} patents"),
    ], columns=["step", "count", "source"])
    funnel.to_csv(CSV / "numbers_I_funnel.csv", index=False)
    out.append(_md_table(funnel))
    out.append("\n*Mapping of T1 and T2:* the repository names the stages above; **T1 = the patent triage at labelling (1 109 approved, then the domain gate to 879)** and **T2 = the figure approval (1 538 whole-aircraft figures on 578 patents)** is my reading of your two names. The 627 designs sit between them (a design needs approved figures). Tell me if your T1 or T2 is another step.\n")
    script_map = _script_company_matches(cfg, ctx)
    table("The VFS eVTOL directory and the company map", [
        ("directory aircraft pages", len(dirf), "frames.directory_frame; csv/numbers_I_funnel.csv"),
        ("kept by the corrected domain rules", int(dirf["in_domain"].sum()), "frames.directory_frame()['in_domain'] (rules of Section 3.1.1 and the author's single-page rulings)"),
        ("matched to a design (pages linked to a patent design, use = yes)", f"{int(dirf['patented'].sum())} pages, {matched['aircraft_uid'].nunique()} designs", "evtolnews_patent_links.csv, use = yes"),
        ("of those pages, kept in the domain", int((dirf['patented'] & dirf['in_domain']).sum()), "frames.directory_frame()"),
        ("index companies read in full (AAM Reality Index company map rows)", len(cmap), "ari_firm_map / review/script_outputs/COMPANY_MAP.csv"),
        ("companies the script matches to a company of the dataset (non-blank match)", script_map["script_nonblank"], "notebooks/_build/yearscript/ari_rule.py"),
        ("companies where the script's match equals the author's name", f"{script_map['agree']} of {len(cmap)}", "notebook 60, review/script_outputs/COMPANY_MAP.csv"),
        ("index companies that file in the dataset", len(firms22), "frames.ari_firms; csv/numbers_I_funnel.csv"),
        ("of them, in the current index release with a first flight and entry date (the clock figure)", len(tl), "frames.ari_timeline; csv/q4_patent_vs_market_clock.csv")],
        cols=("number", "value", "source"))
    out.append("*If any count differs from the ones you listed:* one reading differs. The directory's 1 229 pages, the 871 kept, the 97 matched pages, the 43 companies read and the 22 that file all match. The **35** is the number of the 43 companies on which the script's answer equals the author's, counting the companies both leave blank; the script returns a non-blank match for **18** of them. Say which of the two the text should print.\n")

    # ----------------------------------------------------------------------------------- 4 the checks of 2026-10-12
    out.append("## 4. Checks requested on 2026-10-12 (no figure or text changed by them)\n")
    out += _checks_section(cfg, ctx, c, q4, CSV)

    # ----------------------------------------------------------------------------------- 5 figure facts
    mix = q4.class_mix(ctx)
    out.append("## 5. What each figure plots\n")
    fpy = c["fpy"]
    rows = [
        ("q1_filings_per_year", f"627 designs over the priority years 2005 (pooled with the earlier ones) to {fpy.index.max()}; 625 have an architecture, 2 do not (grey segment); {n1['representative_s'] if 'representative_s' in n1 else int(cnt['patents_approved'])} patent families; cohort 2024-26 faded"),
        ("q1_growth_rates", "eVTOL architecture patents, aeronautics, transport and operations, all patents; 2005-2023 fitted, 2024-26 shown and never fitted"),
        ("q4_patent_vs_market_clock", f"{len(tl)} index firms with a first patent here; first flight {int(tl['first flight (ARI)'].notna().sum())} firms, entry into service {int(tl['entry into service (ARI)'].notna().sum())} firms"),
        ("q1_in_force_status", f"{len(big)} designs of the nine architectures, by office; {len(v) - len(big)} not plotted (see section 2)"),
        ("q4_class_mix", "patent dataset: " + ", ".join(f"{k} {int(t)}" for k, t in mix[mix['source'] == q4.SRC_PATENT].groupby('window')['window total'].first().reindex(ctx.WIN_NAMES).items())
                         + "; directory: " + ", ".join(f"{k} {int(t)}" for k, t in mix[mix['source'] == q4.SRC_DIR].groupby('window')['window total'].first().reindex(ctx.WIN_NAMES).items())),
        ("q5_funding_vs_aircraft", f"{n5['n_air']} firms with a disclosed amount; Spearman rho {n5['rho_air']}, p {n5['p_air']} (not printed in the figure)"),
        ("q5_patenting_vs_investment", "four published periods of disclosed sector investment (2010-20, 2021, 2023, 2024 to August); no test"),
    ]
    out.append(_md_table(pd.DataFrame(rows, columns=["figure", "what is plotted"])))
    out.append("")

    # ----------------------------------------------------------------------------------- 6 every other number the Results text quotes
    out.append("## 6. Every number the Results text of Analysis I quotes\n")
    out.append("Placeholders of `viz/thesis_text_q1.py`, `thesis_text_q4.py` and `thesis_text_q5.py` (results, answer and appendix lines) with the value they take now. "
               "A value that differs from the old Results text is marked (was X); section 7 lists them one line each.\n")
    OLD = _old_numbers()
    for qname, qid, text, nums in (("Q1 growth and active protection", "Q1", t1, n1), ("Q4 representativeness and the market clock", "Q4", t4, n4),
                                   ("Q5 funding and investment", "Q5", t5, n5)):
        used = {}
        blocks = [(f"results {r_['sub']} ({r_['title']})", r_["text"]) for r_ in text.RESULTS] + [("answer", text.ANSWER)] + [(f"appendix {k}", s_) for k, s_ in text.APPENDIX.items()]
        for label, body in blocks:
            clean = re.sub(r"\[hl\]|\[/hl\]|\[(?:fig|tab):[a-z0-9_]+\]", "", body)
            for sent in re.split(r"(?<=[.!?])\s+", clean.replace("\n", " ")):
                for k in _placeholders(sent):
                    used.setdefault(k, (label, sent.strip()))
        rows = []
        for k, (label, sent) in sorted(used.items()):
            val = nums.get(k, "(computed in the text builder)")
            flag = f" (was {OLD[qid][k]})" if k in OLD[qid] and OLD[qid][k] != val else ""
            rows.append((f"`{k}`", f"{val}{flag}", label, sent[:150] + ("…" if len(sent) > 150 else ""), f"viz/thesis_{qid.lower()}.py:numbers()"))
        out.append(f"### {qname}\n")
        out.append(_md_table(pd.DataFrame(rows, columns=["key", "value now", "where used", "sentence", "source"])))
        out.append("")
    out.append("`thesis_figures/Q1_growth/numbers.json`, `Q4_representativeness/numbers.json` and `Q5_money/numbers.json` were rewritten on 2026-10-13 from the current inputs (the corrected company map with EHang, the script TRL, the script years); "
               "the previous Q4 and Q5 files are kept beside them as `numbers.PRE_20261013.json`, and the values of the old Results text are in `review/numbers_old/`.\n")
    out += _changes_section(cfg, ctx, c, n1, n4, n5, OLD, CSV)
    out += _funnel_table(cfg, ctx, ds, v, dirf, matched, cmap, firms22, script_map, cnt)
    p = D / "NUMBERS_I.md"
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    _append_manifest(base, [("Data_for_writing/NUMBERS_I.md", "yes", "numbers of Analysis I with their sources")]
                     + [(f"Data_for_writing/csv/{f.name}", "no", "table behind NUMBERS_I.md (not printed)") for f in sorted(CSV.glob("numbers_I_*.csv"))])
    return p


def _arch_short(code: str) -> str:
    from viz import thesis_v2_part1 as v2
    return v2.arch(code).short


def _arch_name(code: str) -> str:
    from viz import thesis_v2_part1 as v2
    return v2.arch(code).name


def _script_company_matches(cfg, ctx) -> dict:
    """How many of the 43 index companies the name-matching script maps to a company of the dataset, and how many agree with the author."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks" / "_build" / "yearscript"))
    import ari_rule
    names = sorted({str(x) for x in ctx.v["company_canonical"] if str(x) not in ("Individual Inventor", "Unknown / Independent")})
    f = Path(__file__).resolve().parents[1] / "review" / "script_outputs" / "COMPANY_MAP.csv"
    m = pd.read_csv(f, keep_default_na=False) if f.exists() else pd.DataFrame(columns=["oem", "script_match", "author"])
    sm = [ari_rule.match(o, names) for o in m["oem"]]
    return {"script_nonblank": int(sum(1 for x in sm if x)), "agree": int(sum(1 for x, a in zip(sm, m["author"]) if x == a))}


def _checks_section(cfg, ctx, c, q4, CSV: Path) -> list:
    """Items 3, 4 and 5 of the 2026-10-12 report request: the flown groups, the flown index-firm group, the turning points and the lead to flight."""
    from viz import data as vdata
    v = ctx.v
    out = []
    # ---- the flown group: definition and the difference with the earlier group
    from viz import config as vconfig
    cfg_old = vconfig.load()
    cfg_old.analysis["external_inputs"] = "reading"
    ds_old = vdata.load_dataset(cfg_old)
    t_old = frames.trl_frame(ds_old)[["aircraft_id", "trl"]].rename(columns={"trl": "TRL, earlier inputs"})
    t_new = frames.trl_frame(ctx.ds)[["aircraft_id", "trl"]].rename(columns={"trl": "TRL, script inputs"})
    m = v[["aircraft_id", "company_canonical", "topType", "year"]].merge(t_old, on="aircraft_id", how="left").merge(t_new, on="aircraft_id", how="left")
    m["in the old group (TRL above 2, earlier inputs)"] = m["TRL, earlier inputs"] > 2
    m["in the new group (TRL 5 or more, script inputs)"] = m["TRL, script inputs"] >= 5
    diff = m[m["in the old group (TRL above 2, earlier inputs)"] != m["in the new group (TRL 5 or more, script inputs)"]].copy()
    diff.to_csv(CSV / "numbers_I_flown_group_difference.csv", index=False)
    out.append("### Flown designs (TRL 5 or more)\n")
    out.append("- **Definition in the code** (`viz/thesis_q4.py:representativeness`): flown = `trl >= 5`, where `trl` is `frames.trl_frame(ds)`: the NASA TRL of each design from "
               "`0_labelling/inputs/trl/aircraft_trl.csv`, overridden, design by design, by the TRL of the rule-based scripts (the author's own reading where he reviewed the design) "
               "when `analysis.external_inputs` is `script` (`viz/script_inputs.py`, `review/script_outputs/TRL.csv`). A design without a TRL is TRL 2. "
               "TRL 3-4 (ground and wind-tunnel tests) is not flown; no design of the 627 sits at TRL 3 or 4 under the script inputs.\n"
               f"- **Sizes:** the earlier group (TRL above 2 on the earlier inputs) has {int(m['in the old group (TRL above 2, earlier inputs)'].sum())} designs, of which "
               f"{int(((m['TRL, earlier inputs'] > 2) & (m['TRL, earlier inputs'] < 5)).sum())} sit at TRL 3 or 4 and {int((m['TRL, earlier inputs'] >= 5).sum())} at TRL 5 or more. "
               f"The new group (TRL 5 or more on the script inputs) has {int(m['in the new group (TRL 5 or more, script inputs)'].sum())} designs, none at TRL 3 or 4.\n"
               f"- **Why 68 against 63:** the TRL values differ between the two input sets, and the definition moves the TRL 3-4 design out. "
               f"{int((diff['in the new group (TRL 5 or more, script inputs)'] & ~diff['in the old group (TRL above 2, earlier inputs)']).sum())} designs are in the new group and were not in the old one, "
               f"{int((~diff['in the new group (TRL 5 or more, script inputs)'] & diff['in the old group (TRL above 2, earlier inputs)']).sum())} were in the old one and are not in the new "
               f"(63 + {int((diff['in the new group (TRL 5 or more, script inputs)'] & ~diff['in the old group (TRL above 2, earlier inputs)']).sum())} - {int((~diff['in the new group (TRL 5 or more, script inputs)'] & diff['in the old group (TRL above 2, earlier inputs)']).sum())} = {int(m['in the new group (TRL 5 or more, script inputs)'].sum())}). "
               "A design moves from the old group to the rest when the script finds no flight sentence on its linked directory pages where the earlier reading had found one (and the reverse). They are listed below and in `csv/numbers_I_flown_group_difference.csv`.\n")
    out.append(_md_table(diff.drop(columns=["year"]).rename(columns={"company_canonical": "company", "topType": "architecture"})))
    out.append("")
    # ---- the flown index-firm group
    rep = q4.representativeness(ctx)
    fari = rep["fari"]
    cls = fari[fari["attribute"] == "folded class"][["level", "flown", "flown %", "rest", "rest %", "gap pp"]].rename(
        columns={"level": "directory category", "flown": "flown index-firm designs", "flown %": "% of the flown index-firm designs", "rest": "the rest", "rest %": "% of the rest"})
    cls.to_csv(CSV / "numbers_I_flown_index_firm_architecture_counts.csv", index=False)
    cur = frames.ari_load(cfg)[0]
    tl = q4.ari_timeline(ctx)
    firm_rows = []
    for _, r in tl.iterrows():
        ff = r["first flight (ARI)"]
        firm_rows.append({"company": r["company"], "designs": int(r["unique aircraft"]), "first flight in the index (earliest year)": "" if pd.isna(ff) else int(ff),
                          "counts as flown before the snapshot": bool(pd.notna(ff) and ff <= frames.ARI_RELEASE_YEAR - 1),
                          "reason if not": "" if (pd.notna(ff) and ff <= frames.ARI_RELEASE_YEAR - 1) else ("a planned first flight (after the index release of 2026)" if pd.notna(ff) else "no first flight in the index")})
    firms = pd.DataFrame(firm_rows)
    firms.to_csv(CSV / "numbers_I_flown_index_firms.csv", index=False)
    out.append("### Flown index-firm group\n")
    out.append(f"- **Definition:** the designs of the index firms of the current AAM Reality Index release whose first flight, as the index prints it, is a year before 2026 "
               f"(the index prints years only; a 2026 year is read as a plan, as in the clock figure). The other index firms, and the 22 - 14 firms with no row in the current release, go to the rest. "
               f"The group has {rep['n_fari']} designs of {rep['n_fari_firms']} firms.\n")
    out.append("Architecture groups behind \"LC +21.5 pp, p 0.047\" (flown index-firm designs against the rest, the five directory categories):\n")
    out.append(_md_table(cls))
    out.append(f"\nchi-square on this 2 x 5 table: p {rep['fari'][rep['fari']['attribute'] == 'folded class']['p'].dropna().iloc[0]:.3f}. "
               f"The two designs without an architecture group are in the rest of the other attributes but not in this table (the five rows add to {int(cls['flown index-firm designs'].sum())} and {int(cls['the rest'].sum())}, not {rep['n_fari']} and {len(v) - rep['n_fari']}).\n")
    out.append("Index firms and whether their first flight counts as flown:\n")
    out.append(_md_table(firms))
    out.append("")
    # ---- turning points and the lead from first patent to first flight
    tp = c["tp"]
    out.append("### I.1 turning points and the lead from the first patent to the first flight\n")
    out.append(_md_table(pd.DataFrame([{"series": k, "turning point": d["break"], "95 % range of the resampled year": f"{d['lo']} to {d['hi']}",
                                        "share of the fits choosing it": f"{100 * d['share']:.0f} %", "jump factor": f"x{d['jump']:.2f}"} for k, d in tp.items()])))
    out.append("\n(`unique aircraft` = the designs series; `representative patents` = the patent-families series.)\n")
    flown = tl[tl["first flight (ARI)"] <= frames.ARI_RELEASE_YEAR]
    gap = flown["years to first flight"]
    lag = frames.publication_lag(ctx.ds, by="region").set_index("region").loc[frames.REGIONS]
    lag_p90 = int(lag["90th percentile"].max())
    lead = flown[["company", "first patent", "first flight (ARI)", "years to first flight"]].rename(columns={"first flight (ARI)": "first flight", "years to first flight": "years from the first patent to the first flight"})
    lead = lead.astype({"first patent": int, "first flight": int, "years from the first patent to the first flight": int})
    lead.to_csv(CSV / "numbers_I_lead_to_first_flight.csv", index=False)
    out.append(_md_table(lead))
    pos = gap[gap > 0]
    out.append(f"\n- firms with a first flight on record (year 2026 or before): n = {len(gap)}; with the first patent before the flight: n = {len(pos)}; "
               f"median lead among those {pos.median():.0f} years (range {pos.min():.0f} to {pos.max():.0f}); median over all {len(gap)}: {gap.median():.1f} years.\n"
               f"- 90th-percentile publication lag: {lag_p90} years (the largest of the three regions, `frames.publication_lag`). Median lead minus that lag: {pos.median() - lag_p90:.0f} years "
               f"(`q5.numbers()['ff_visible']`), the \"about 1 year\" figure, on the same n = {len(pos)} firms. The lag is subtracted as one number, from the median, not firm by firm.\n")
    return out



# ======================================================================================== old -> new, unchanged, funnel table
def _old_numbers() -> dict:
    import json
    d = Path(__file__).resolve().parents[1] / "review" / "numbers_old"
    return {"Q1": json.loads((d / "Q1_numbers_OLD_before_all_years.json").read_text(encoding="utf-8")),
            "Q4": json.loads((d / "Q4_numbers_OLD_before_script_inputs.json").read_text(encoding="utf-8")),
            "Q5": json.loads((d / "Q5_numbers_OLD_before_script_inputs.json").read_text(encoding="utf-8"))}


def _load_text_module(path: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.stem.replace(".", "_"), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _changes_section(cfg, ctx, c, n1, n4, n5, OLD, CSV: Path) -> list:
    """Section 7: every number the OLD Results text quoted that changed (old -> new), then the ones that did not change."""
    here = Path(__file__).resolve().parent
    old_text = {"Q1": _load_text_module(here / "thesis_text_q1.PRE_I2ALL_20261012.py"), "Q4": _load_text_module(here / "thesis_text_q4.PRE_I3FLOWN_20261012.py"),
                "Q5": _load_text_module(here / "thesis_text_q5.py")}
    new = {"Q1": n1, "Q4": n4, "Q5": n5}
    out = ["## 7. What changed since the old Results text (old -> new)\n",
           "Old = the values the old Results text printed (the `numbers.json` files before the changes of 2026-10-12: the all-years protection method, the flown definition, the "
           "script inputs and the corrected company map with EHang). New = the values now. A key that the new text no longer quotes reads \"(no longer quoted)\".\n"]
    tp = c["tp"]
    ap, ds_ = tp["representative patents"], tp["unique aircraft"]
    o4, o5, o1 = OLD["Q4"], OLD["Q5"], OLD["Q1"]
    out.append("### The statistics you listed, one line each\n")
    lines = [
        f"- **Index firms that file here** (rows of the clock figure, the firms of the current index release with a first patent in the dataset): {o5['ari_timeline_n']} -> {n5['ari_timeline_n']} (Q5 `ari_timeline_n`)",
        f"- **Index companies that file in the dataset** (whole company map): {o4['ari_firms_n']} -> {n4['ari_firms_n']} (Q4 `ari_firms_n`); their designs {o4['ari_n']} -> {n4['ari_n']} (Q4 `ari_n`)",
        f"- **Firms with a first flight on record** (year 2026 or before): {o5['ff_record_n']} -> {n5['ff_record_n']} (Q5 `ff_record_n`; Q4 `ff_flown` {o4['ff_flown']} -> {n4['ff_flown']})",
        f"- **Firms that filed their first patent before flying**: {o5['ff_before_n']} -> {n5['ff_before_n']} (Q5 `ff_before_n`; Q4 `ff_before` {o4['ff_before']} -> {n4['ff_before']}); firms with a first flight at or before the first patent: {o5['ff_after_n']} -> {n5['ff_after_n']} (`ff_after_n`)",
        f"- **Median lead from the first patent to the first flight**, years: {o5['ff_lead']} -> {n5['ff_lead']} (Q5 `ff_lead`; Q4 {o4['ff_lead']} -> {n4['ff_lead']}), on the {n5['ff_before_n']} firms with the patent before the flight (was {o5['ff_before_n']}); range {o5['ff_lead_min']} to {o5['ff_lead_max']} -> {n5['ff_lead_min']} to {n5['ff_lead_max']}",
        f"- **The lead left after the 90th-percentile publication lag** ({n5['lag_p90']} years, unchanged): {o5['ff_visible']} -> {n5['ff_visible']} years (Q5 `ff_visible`)",
        f"- **Median years from the first patent to the planned entry into service**: {o5['eis_lead']} -> {n5['eis_lead']} (Q5 `eis_lead`), on {o5['eis_n']} -> {n5['eis_n']} firms that state one (`eis_n`)",
        f"- **Firms behind each statistic (now)**: first flights {n5['ff_record_n']}; the lead median {n5['ff_before_n']}; planned entry into service {n5['eis_n']}; clock rows {n5['ari_timeline_n']}; funding tests {n5['n_air']} firms with a disclosed amount, {n5['n_fp']} for the first-patent year, {n5['n_lead']} for the lead (before {o5['n_air']}, {o5['n_fp']}, {o5['n_lead']})",
        f"- **Size of the flown group**: {o4['trl_n']} (designs above TRL 2, earlier inputs) -> {n4['flown_n']} (designs at TRL 5 or more, script inputs); the rest {o4['trl_rest']} -> {n4['flown_rest']} (Q4 `trl_n` -> `flown_n`); 10 designs entered and 5 left (section 4)",
        f"- **Turning point, patent families**: {o1['turn_pat_year']} -> {n1['turn_pat_year']} (unchanged), chosen by {o1['turn_pat_boot']} -> {n1['turn_pat_boot']} of the resampled fits, 95 % range of the resampled year {ap['lo']} to {ap['hi']} (not quoted before)",
        f"- **Turning point, designs**: {o1['turn_ac_year']} -> {n1['turn_ac_year']} (unchanged), chosen by {100 * ds_['share']:.0f} % of the resampled fits (not quoted before), 95 % range {o1['turn_ac_lo']} to {o1['turn_ac_hi']} -> {n1['turn_ac_lo']} to {n1['turn_ac_hi']} (unchanged)",
    ]
    out += lines
    out.append("\nNone of the turning-point numbers depends on the company map, the TRL or the years of the directory: they come from the patent counts per priority year.\n")
    # the full list: every placeholder of the old text
    changed, same = [], []
    for q in ("Q1", "Q4", "Q5"):
        blocks = [r_["text"] for r_ in old_text[q].RESULTS] + [old_text[q].ANSWER] + list(old_text[q].APPENDIX.values())
        seen = {}
        for body in blocks:
            clean = re.sub(r"\[hl\]|\[/hl\]|\[(?:fig|tab):[a-z0-9_]+\]", "", body)
            for sent in re.split(r"(?<=[.!?])\s+", clean.replace("\n", " ")):
                for k in _placeholders(sent):
                    seen.setdefault(k, sent.strip())
        for k, sent in sorted(seen.items()):
            ov = OLD[q].get(k)
            nv = new[q].get(k, "(no longer quoted)")
            if ov is None:
                continue
            (changed if ov != nv else same).append((q, k, ov, nv, sent[:110] + ("…" if len(sent) > 110 else "")))
    out.append("### Every number the old Results text quoted that changed\n")
    out += [f"- {q} `{k}`: {ov} -> {nv}   ({sent})" for q, k, ov, nv, sent in changed]
    out.append("")
    out.append(f"### Numbers that did NOT change ({len(same)})\n")
    out.append(_md_table(pd.DataFrame([(q, f"`{k}`", ov, sent) for q, k, ov, nv, sent in same], columns=["question", "key", "value (old = new)", "used in the sentence"])))
    out.append("")
    pd.DataFrame(changed, columns=["question", "key", "old", "new", "sentence"]).to_csv(CSV / "numbers_I_changed_old_new.csv", index=False)
    pd.DataFrame(same, columns=["question", "key", "value", "new", "sentence"]).drop(columns="new").to_csv(CSV / "numbers_I_unchanged.csv", index=False)
    return out


def _funnel_table(cfg, ctx, ds, v, dirf, matched, cmap, firms22, script_map, cnt) -> list:
    """Section 9: the funnel counts of section 4.1 once more, as one short table."""
    rows = [
        ("patent query hits (PatSeer, snapshot %s)" % frames.snapshot_date(ds), f"{cnt['patents_acquired']:,}".replace(",", " ")),
        ("T1: patents approved at labelling (patent triage)", f"{cnt['patents_wizard_approved']:,}".replace(",", " ") + f" (879 after the domain gate)"),
        ("T2: whole-aircraft figures approved (image triage), and the patents they sit on", f"{cnt['approved_figures']:,}".replace(",", " ") + f" figures on {ds.approved_figures['patent_id'].nunique()} patents"),
        ("designs characterised", f"{len(v)} (on {cnt['patents_analysis']} primary patents)"),
        ("directory pages (VFS eVTOL directory)", f"{len(dirf):,}".replace(",", " ")),
        ("kept by the corrected domain rules", int(dirf["in_domain"].sum())),
        ("pages matched to a design (and the designs they give)", f"{int(dirf['patented'].sum())} pages, {matched['aircraft_uid'].nunique()} designs"),
        ("companies read in full (index company map)", len(cmap)),
        ("companies where the script and the author agree (counting the companies both leave blank)", f"{script_map['agree']} of {len(cmap)}"),
        ("companies where the script returns a match", script_map["script_nonblank"]),
        ("index companies that file in the dataset", len(firms22)),
    ]
    out = ["## 8. The funnel of section 4.1 in one table\n", _md_table(pd.DataFrame(rows, columns=["step", "count"])), ""]
    return out
