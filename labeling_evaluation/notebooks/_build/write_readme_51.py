"""Write thesis_figures_v2/Part_IV_design_space_evolution/README.md from viz/thesis_v2_part4.ITEMS."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from viz import config
from viz import thesis_v2_part4 as v4

OUT = v4.out_root(config.load())
rows = "\n".join(f"| {it['group']} | {it['role']} | `{it['name']}` | `{it['old']}` | {it['title']} |" for it in v4.ITEMS)
(OUT / "README.md").write_text(f"""# Part IV, evolution of the design space

Written by notebook 51 (`notebooks/51_thesis_figures_v2_part4.ipynb`) from `viz/thesis_v2_part4.py`. Each file comes as PDF, PNG, CSV (the plotted numbers) and JSON.
The seven existing figures run their builders of `viz/thesis_q6.py` unchanged; only the words (architecture, cohort, configuration) and the style differ.

| group | role | file | earlier file | what it shows |
|---|---|---|---|---|
{rows}

Cohorts: the four complete ones; the first two (few designs) hollow on a grey band.
""", encoding="utf-8")
print("README written to", OUT)
