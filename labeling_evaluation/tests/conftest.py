"""Shared fixtures for the lib tests.

The tests prove that every lib equation reproduces the archived code that produced the 45-page document.
The ARCHIVED code (archive/labeling_evaluation/src/dataset_facts) is imported HERE ONLY, to build the same
inputs and the expected outputs. lib/ and viz/ never import it.
"""
import sys
from pathlib import Path

import pytest

PILLAR = Path(__file__).resolve().parents[1]
ARCHIVE = PILLAR.parent / "archive" / "labeling_evaluation"
sys.path.insert(0, str(PILLAR))


def _archive():
    if str(ARCHIVE) not in sys.path:
        sys.path.insert(0, str(ARCHIVE))
    import src.dataset_facts as df          # noqa: E402  (archive package named `src`)
    return df


@pytest.fixture(scope="session")
def archive():
    """The archived dataset_facts package (la_tables, sm_open, metrics, a3, …)."""
    return _archive()


@pytest.fixture(scope="session")
def ds(archive):
    """The archived Dataset, loaded exactly as the document did."""
    from src.config_loader import load_config
    return archive.load_dataset(load_config())


@pytest.fixture(scope="session")
def v(archive, ds):
    """The archived base frame: one row per unique aircraft (la_tables.base)."""
    from src.dataset_facts import la_tables
    return la_tables.base(ds)


@pytest.fixture(scope="session")
def reference():
    """The 45-page document's tables folder (read-only)."""
    import yaml
    y = yaml.safe_load((PILLAR / "labelling_analysis.yaml").read_text())
    return Path(y["roots"]["reference"]) / "tables"
