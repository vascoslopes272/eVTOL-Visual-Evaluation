"""Write tests/reference/document_numbers.csv: every number the 45-page document's text quotes, as the document
resolved it (name -> printed value). Run once; the thesis notebooks compare their numbers with this file.

Uses the ARCHIVED code (archive/labeling_evaluation) exactly as scripts/render_summary.py did: numbers.live on the
dataset + sm_index.resolve on the document's own tables/*.csv. Test-side tool only; lib/ and viz/ never import it.
"""
import re
import sys
from pathlib import Path

import pandas as pd

PILLAR = Path(__file__).resolve().parents[1]
ARCH = PILLAR.parent / "archive" / "labeling_evaluation"
sys.path.insert(0, str(ARCH))
sys.path.insert(0, str(ARCH / "scripts"))
from src.config_loader import load_config                                # noqa: E402
from src.dataset_facts import load_dataset, numbers, sm_index            # noqa: E402
import render_summary                                                    # noqa: E402
import yaml                                                              # noqa: E402

ref = Path(yaml.safe_load((PILLAR / "labelling_analysis.yaml").read_text())["roots"]["reference"])
ds = load_dataset(load_config())
tables = render_summary.load_tables(ref)
values = sm_index.resolve(numbers.live(ds, 2024), tables)

# which chapter quotes each placeholder
used = {}
for node, txt in sm_index.TEXTS.items():
    for ph in re.findall(r"\{([a-z][a-z0-9_]*)\}", str(txt)):
        used.setdefault(ph, set()).add(str(node).split(".")[0])
for reg in ("CHAPTER_METHOD", "SM_ANSWER"):
    for ch, txt in getattr(sm_index, reg).items():
        for ph in re.findall(r"\{([a-z][a-z0-9_]*)\}", str(txt)):
            used.setdefault(ph, set()).add(str(ch))
rows = [{"name": k, "chapters": " ".join(sorted(used.get(k, []))), "value": str(v)}
        for k, v in sorted(values.items()) if k in used and not k.startswith("sm_here_")]
out = PILLAR / "tests" / "reference" / "document_numbers.csv"
pd.DataFrame(rows).to_csv(out, index=False)
missing = sorted(k for k in used if k not in values and not k.startswith("sm_here_"))
print(f"{len(rows)} numbers written to {out}; unresolved: {missing}")
