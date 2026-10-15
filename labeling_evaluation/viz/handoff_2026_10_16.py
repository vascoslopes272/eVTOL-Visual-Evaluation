"""Hand-over 2026-10-16 (five tasks): the extra copies each notebook writes after its normal cells.

The notebooks (50, 51, 52, 53) already write the v2 folder (`thesis_figures_v2/<Part>/<group>/<role>/`), the LaTeX_v15 pdf and the
`Data_for_writing/csv/` csv of every item. This module writes, for the items of the hand-over:

* png (300 dpi, the final width, as the pdf), csv and json beside the LaTeX_v15 pdf;
* a copy of the v2 (notebook-size) files under `LaTeX_v15/Figures/thesis_figures_v2/<Part>/<group>/<role>/` (the folder the brief names);
* the Q-item version through the builder and writer of notebook 46 (`thesis_figures/<Q>/results/`) where the item exists there;
* every file plus the changed scripts in `handoff_2026-10-16/taskN/` at the repository root.

Nothing is recomputed differently: the figures are drawn by the same builders as the notebook cells above."""
from __future__ import annotations

import json
import pathlib
import shutil

import matplotlib.pyplot as plt
import pandas as pd

HANDOFF = "handoff_2026-10-16"


def _pillar() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def _ho_root() -> pathlib.Path:
    return _pillar().parent / HANDOFF


def copy_scripts(task: str, scripts) -> list:
    ho = _ho_root() / task
    ho.mkdir(parents=True, exist_ok=True)
    out = []
    for s in scripts:
        src = _pillar() / s
        if src.exists():
            shutil.copy2(src, ho / pathlib.Path(s).name)
            out.append(ho / pathlib.Path(s).name)
    return out


def figure_copies(task: str, name: str, item: dict, part: str, v2dir: pathlib.Path, R: pathlib.Path, draw_final, data_csv=None) -> list:
    """One figure: ``draw_final()`` -> (fig, data) at the final width; ``v2dir`` the notebook-size folder of the item; ``R`` = LaTeX_v15."""
    ho = _ho_root() / task
    ho.mkdir(parents=True, exist_ok=True)
    written = []
    lx = R / "Figures" / part / item["group"] / item["role"]
    lx.mkdir(parents=True, exist_ok=True)
    meta = json.loads((v2dir / f"{name}.json").read_text(encoding="utf-8")) if (v2dir / f"{name}.json").exists() else {"name": name}
    fig, data = draw_final()
    fig.savefig(lx / f"{name}.pdf")
    fig.savefig(lx / f"{name}.png", dpi=300)
    w, h = round(fig.get_figwidth() * 2.54, 2), round(fig.get_figheight() * 2.54, 2)
    plt.close(fig)
    if data is not None:
        data.to_csv(lx / f"{name}.csv", index=False)
        data.to_csv(R / "Data_for_writing" / "csv" / f"{name}.csv", index=False)
    elif data_csv is not None and pathlib.Path(data_csv).exists():
        shutil.copy2(data_csv, lx / f"{name}.csv")
    (lx / f"{name}.json").write_text(json.dumps({**meta, "width_cm": w, "height_cm": h}, indent=1, ensure_ascii=False), encoding="utf-8")
    written += [lx / f"{name}.{e}" for e in ("pdf", "png", "csv", "json") if (lx / f"{name}.{e}").exists()]
    for e in ("pdf", "png", "csv", "json"):
        if (lx / f"{name}.{e}").exists():
            shutil.copy2(lx / f"{name}.{e}", ho / f"{name}.{e}")
    # the v2 (notebook-size) files: a copy under LaTeX_v15/Figures/thesis_figures_v2/... and in the hand-over folder as <name>_v2.*
    v2lx = R / "Figures" / "thesis_figures_v2" / part / item["group"] / item["role"]
    v2lx.mkdir(parents=True, exist_ok=True)
    for e in ("pdf", "png", "csv", "json"):
        if (v2dir / f"{name}.{e}").exists():
            shutil.copy2(v2dir / f"{name}.{e}", v2lx / f"{name}.{e}")
            shutil.copy2(v2dir / f"{name}.{e}", ho / f"{name}_v2.{e}")
            written.append(v2lx / f"{name}.{e}")
    return written


def table_copies(task: str, name: str, item: dict, part: str, v2dir: pathlib.Path, R: pathlib.Path, also_to=None) -> list:
    """One table: csv (already in Data_for_writing/csv by the export) + json beside it, optional extra folder, v2 copies, hand-over copies."""
    ho = _ho_root() / task
    ho.mkdir(parents=True, exist_ok=True)
    written = []
    csvd = R / "Data_for_writing" / "csv"
    if (v2dir / f"{name}.json").exists():
        shutil.copy2(v2dir / f"{name}.json", csvd / f"{name}.json")
        written.append(csvd / f"{name}.json")
    for e in ("csv", "json"):
        if (csvd / f"{name}.{e}").exists():
            shutil.copy2(csvd / f"{name}.{e}", ho / f"{name}.{e}")
    if also_to is not None:
        pathlib.Path(also_to).mkdir(parents=True, exist_ok=True)
        for e in ("csv", "json"):
            if (csvd / f"{name}.{e}").exists():
                shutil.copy2(csvd / f"{name}.{e}", pathlib.Path(also_to) / f"{name}.{e}")
                written.append(pathlib.Path(also_to) / f"{name}.{e}")
    v2lx = R / "Figures" / "thesis_figures_v2" / part / item["group"] / item["role"]
    v2lx.mkdir(parents=True, exist_ok=True)
    for e in ("csv", "json"):
        if (v2dir / f"{name}.{e}").exists():
            shutil.copy2(v2dir / f"{name}.{e}", v2lx / f"{name}.{e}")
            written.append(v2lx / f"{name}.{e}")
    return written


def q_item_copies(task: str, name: str, q_items, ctx, cfg, suffix: str = "qresults") -> list:
    """The Q-item version (the builder and writer of notebook 46): thesis_figures/<Q>/results/<name>.*; copies as <name>_<suffix>.* in the hand-over."""
    from viz import thesis
    it = next((i for i in q_items if i["name"] == name), None)
    if it is None:
        return []
    ho = _ho_root() / task
    ho.mkdir(parents=True, exist_ok=True)
    obj, data = it["builder"](ctx)
    p = thesis.save_item(it, obj, data, cfg)
    plt.close("all")
    written = []
    for e in ("pdf", "png", "csv", "json"):
        if p.with_suffix(f".{e}").exists():
            written.append(p.with_suffix(f".{e}"))
            shutil.copy2(p.with_suffix(f".{e}"), ho / f"{name}_{suffix}.{e}")
    return written


def plain_copies(task: str, files) -> list:
    ho = _ho_root() / task
    ho.mkdir(parents=True, exist_ok=True)
    out = []
    for f in files:
        f = pathlib.Path(f)
        if f.exists():
            shutil.copy2(f, ho / f.name)
            out.append(ho / f.name)
    return out


def listing(task: str) -> list:
    ho = _ho_root() / task
    return sorted(str(p.relative_to(_ho_root())) for p in ho.rglob("*") if p.is_file()) if ho.exists() else []
