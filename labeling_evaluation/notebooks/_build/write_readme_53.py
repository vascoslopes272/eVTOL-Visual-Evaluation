"""Write thesis_figures_v2/Part_V_assignees_and_regions/README.md from viz/thesis_v2_part5.ITEMS (run from notebook 53)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from viz import config
from viz import thesis_v2_part5 as v5

OUT = v5.out_root(config.load(strict=False))
OUT.mkdir(parents=True, exist_ok=True)
lines = ["# Part V: assignees and regions\n", "Written by notebook 53 (`notebooks/_build/build_53.py`). One file per graph or table: `<group>/<role>/<name>.{pdf,png,csv,json}`.\n"]
for g in dict.fromkeys(i["group"] for i in v5.ITEMS):
    lines.append(f"## {g}\n")
    lines += [f"- `{i['name']}` ({i['role']}, {i['kind']}): {i['title']} *({i['source_item']})*" for i in v5.ITEMS if i["group"] == g]
    lines.append("")
lines += ["## Labels (relabel only; data, cohorts, builders and layout unchanged)\n",
          "Multirotor → Multicopter; Tilt Body → Tilt Frame; Tilt Rotor → Tilt Propulsor; filer, firm, organisation → assignee; window → cohort; class → architecture; Q2, Q3, Part V → Analysis V. File names are unchanged, including those with filer and window in them.",
          "The notebook prints, under each figure, the words changed in it.\n",
          "## Removed marks\n", "- The hollow AAM Reality Index diamonds and their legend in `q2_largest_filers_share`, and the AAM text in its caption and source (JSON); the CSV column 'rated by the index' is gone.\n",
          "## Not in this folder, not regenerated, not deleted\n",
          "- `q3_firm_successions`, `q7_region_firm_proximity` and every funding figure: cut from the dissertation; their files stay in `thesis_figures/`.\n"]
(OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
print("README written", OUT / "README.md")
