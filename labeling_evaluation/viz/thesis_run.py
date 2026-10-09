"""Run one thesis question end to end, as notebook 46/47 do cell by cell — for building and checking.

    python3 -m viz.thesis_run Q1            # build every item of viz/thesis_q1.py, write numbers.json, check the text
    python3 -m viz.thesis_run Q1 --no-save  # only check (builders still run)

Prints: one line per item (saved path, figure size), the numbers written, every unresolved {placeholder} or
[fig:/tab:] reference in viz/thesis_text_q1.py, and the density counts the contract asks for.
"""
from __future__ import annotations

import importlib
import json
import re
import sys

import matplotlib.pyplot as plt

from viz import config, thesis

REF = re.compile(r"\[(fig|tab):([a-z0-9_]+)\]")
PH = re.compile(r"(?<!\{)\{([a-zA-Z0-9_]+)\}(?!\})")
HL = re.compile(r"\[hl\](.*?)\[/hl\]", re.S)


def load_modules(qid: str):
    n = qid[1]
    items = importlib.import_module(f"viz.thesis_q{n}")
    text = importlib.import_module(f"viz.thesis_text_q{n}")
    return items, text


def build_items(qid: str, ctx, save: bool = True) -> list:
    mod, _ = load_modules(qid)
    done = []
    for it in mod.ITEMS:
        thesis.check_item(it)
        obj, data = it["builder"](ctx)
        if it["kind"] == "figure":
            assert hasattr(obj, "savefig"), f"{it['name']}: builder must return a matplotlib Figure"
            info = f"{obj.get_figwidth():.2f} x {obj.get_figheight():.2f} in"
        else:
            info = f"{len(obj)} rows x {len(obj.columns)} cols"
        path = thesis.save_item(it, obj, data, ctx.cfg) if save else None
        if it["kind"] == "figure":
            plt.close(obj)
        print(f"  {it['slot']:<8} {it['kind']:<6} {it['name']:<42} {info:<18} {path or ''}")
        done.append(it["name"])
    return done


def write_numbers(qid: str, ctx, save: bool = True) -> dict:
    mod, _ = load_modules(qid)
    nums = mod.numbers(ctx)
    bad = {k: v for k, v in nums.items() if not isinstance(v, str)}
    assert not bad, f"numbers() must return strings as printed; not strings: {bad}"
    if save:
        p = ctx.cfg.out("thesis_figures") / thesis.folder(qid) / "numbers.json"
        p.write_text(json.dumps(nums, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  numbers.json: {len(nums)} values -> {p}")
    return nums


def _sentences(text: str) -> list:
    text = HL.sub(r"\1", REF.sub("", text))
    return [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]


def _all_item_names() -> set:
    """The item names of every viz.thesis_qN module that imports (thesis_doc resolves any of them as a reference)."""
    names = set()
    for n in range(1, 8):
        try:
            names |= {it["name"] for it in importlib.import_module(f"viz.thesis_q{n}").ITEMS}
        except Exception:
            continue
    return names


def check_text(qid: str, nums: dict, item_names: list) -> list:
    """Problems found in the text module; [] when clean."""
    mod, text = load_modules(qid)
    problems = []
    known = set(item_names) | _all_item_names()        # a cross-question citation (Q1 reads Q3's entry-lag figure) is allowed
    blocks = [("METHOD", text.METHOD)] + [(f"RESULTS[{r['sub']}]", r["text"]) for r in text.RESULTS] + [("ANSWER", text.ANSWER)]
    blocks += [(f"APPENDIX[{k}]", v) for k, v in text.APPENDIX.items()]
    for label, body in blocks:
        for key in PH.findall(body):
            if key not in nums:
                problems.append(f"{label}: unresolved number {{{key}}}")
        for kind, name in REF.findall(body):
            if name not in known:
                problems.append(f"{label}: reference [{kind}:{name}] is not an item of any question")
        for s in _sentences(body):
            n_numbers = len(PH.findall(s)) + len(re.findall(r"(?<![\w{])\d+(?:[.,]\d+)?\s?%?(?![\w}])", s))
            if n_numbers > 2:
                problems.append(f"{label}: sentence with {n_numbers} numbers: '{s[:70]}…'")
            if re.search(r"\d", HL.sub("", s)) and not PH.search(s) and not re.search(r"\b(19|20)\d\d\b|\b\d+ %|\bn\s?\d", s):
                pass
        words = len(body.split())
        if label == "METHOD" and words > 300:
            problems.append(f"METHOD is {words} words (≤ 300)")
        if label.startswith("RESULTS") and words > 260:
            problems.append(f"{label} is {words} words (≤ 260)")
        if label.startswith("APPENDIX") and words > 45:
            problems.append(f"{label} is {words} words (≤ 45)")
    typed = []
    for label, body in blocks:
        for m in re.finditer(r"(?<![\w{])\d+(?:[.,]\d+)?(?![\w}])", HL.sub(r"\1", body)):
            if not re.fullmatch(r"(19|20)\d\d", m.group()) and m.group() not in ("50", "95", "2", "3", "1"):
                typed.append(f"{label}: typed number '{m.group()}' — use a {{placeholder}} from numbers()")
    problems += typed[:40]
    results_items = [it["name"] for it in mod.ITEMS if it["slot"] == "results"]
    cited = {n for r in text.RESULTS for _, n in REF.findall(r["text"])}
    for n in results_items:
        if n not in cited:
            problems.append(f"results item {n} is never cited in RESULTS text")
    for n in [it["name"] for it in mod.ITEMS if it["slot"] == "appendix"]:
        if n not in text.APPENDIX:
            problems.append(f"appendix item {n} has no APPENDIX takeaway line")
    per_sub = {}
    for it in mod.ITEMS:
        if it["slot"] == "results" and it["kind"] == "figure":
            per_sub[it["sub"]] = per_sub.get(it["sub"], 0) + 1
    for sub, k in per_sub.items():
        if k > 3:
            problems.append(f"sub-question {sub} has {k} result figures (≤ 3 single graphs)")
    return problems


def main(argv=None):
    argv = argv or sys.argv[1:]
    qid = argv[0].upper()
    save = "--no-save" not in argv
    cfg = config.load()
    ctx = thesis.context(cfg)
    print(f"== {qid}: items")
    names = build_items(qid, ctx, save)
    print(f"== {qid}: numbers")
    nums = write_numbers(qid, ctx, save)
    print(f"== {qid}: text checks")
    probs = check_text(qid, nums, names)
    for p in probs:
        print("  !", p)
    print(f"== {qid}: {len(names)} items, {len(nums)} numbers, {len(probs)} text problems")
    return 1 if probs else 0


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    sys.exit(main())
