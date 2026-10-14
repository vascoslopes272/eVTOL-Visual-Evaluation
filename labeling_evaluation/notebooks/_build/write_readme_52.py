"""Write thesis_figures_v2/Part_III_dominant_design/README.md from viz/thesis_v2_part3.ITEMS (run from notebook 52)."""
import sys
from pathlib import Path
PILLAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PILLAR))
from viz import config
from viz import thesis_v2_part3 as v3

OUT = v3.out_root(config.load())
OUT.mkdir(parents=True, exist_ok=True)
lines = ["# Part III — Dominant design\n", "Written by notebook 52 (`notebooks/_build/build_52.py`). One file per graph or table: `<group>/<role>/<name>.{pdf,png,csv,json}`.\n"]
for g in dict.fromkeys(i["group"] for i in v3.ITEMS):
    lines.append(f"## {g}\n")
    for it in v3.ITEMS:
        if it["group"] == g:
            lines.append(f"- `{it['name']}` ({it['role']}, {it['kind']}) — {it['title']} *({it['source_item']})*")
    lines.append("")
(OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
print("README written", OUT / "README.md")
