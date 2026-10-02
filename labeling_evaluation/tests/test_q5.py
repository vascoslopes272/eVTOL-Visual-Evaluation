"""Question 5 (notebook 44): the wrangling of viz.frames reproduces the archive (imported HERE ONLY, via the conftest fixtures);
lib.distance.proximity_order equals the archive's."""
import numpy as np
import pandas as pd
import pytest

from lib import distance as dist
from lib import regional
from viz import config, data, frames


@pytest.fixture(scope="module")
def cfg():
    return config.load()


@pytest.fixture(scope="module")
def dsn(cfg):
    return data.load_dataset(cfg)


@pytest.fixture(scope="module")
def vn(dsn, cfg, archive):
    from src.dataset_facts import la_tables
    return frames.base(dsn, cfg, fold=la_tables.FOLD5)


def _same(a: pd.DataFrame, b: pd.DataFrame, cols=None):
    cols = cols or list(b.columns)
    assert len(a) == len(b)
    for c in cols:
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiu" and y.dtype.kind in "fiu":
            assert np.allclose(x.astype(float), y.astype(float), rtol=0, atol=1e-12, equal_nan=True), c
        else:
            assert [str(i) for i in x] == [str(i) for i in y], c


def test_regional_tables(archive, ds, v, dsn, vn):
    from src.dataset_facts import la_tables, sm_open
    W = list(la_tables.WINDOW_NAMES)
    wn = frames.regional_frame(dsn, vn)
    wo = sm_open._ch5_frame(ds, v)
    assert list(wn["aircraft_id"]) == list(wo["aircraft_id"])
    assert wn["F"].astype(str).tolist() == wo["F"].astype(str).tolist()
    _same(frames.region_countries(dsn, vn), sm_open.region_countries(ds, v))
    _same(frames.region_mix_change(wn), sm_open.region_mix_change(ds, v))
    _same(frames.region_window_mix(wn, W), sm_open.region_window_mix(ds, v))
    new, old = frames.region_tests(wn), sm_open.region_tests(ds, v)
    _same(new, old)
    assert new.attrs["left_out"] == old.attrs["left_out"]
    _same(frames.region_lean(wn), sm_open.region_lean(ds, v))
    _same(frames.region_years(dsn, vn), sm_open.region_years(ds, v))


def test_proximity_order(archive, ds, v):
    from src.dataset_facts import a2
    prof = a2.firm_profiles(ds, 5, "class")
    prox = a2.proximity_matrix(prof)
    assert dist.proximity_order(prox) == a2.proximity_order(prox)
    assert dist.proximity_order(prox.iloc[:2, :2]) == a2.proximity_order(prox.iloc[:2, :2])


def test_region_proximity_frame(archive, ds, v, vn):
    from src.dataset_facts import la_tables
    m, summ = la_tables.proximity_by_region(ds, v)
    mn, regn = frames.region_firm_proximity(vn)
    assert list(mn.index) == list(m.index)
    assert np.allclose(mn.to_numpy(), m.to_numpy(), rtol=0, atol=1e-12)
    assert list(regn) == list(m.attrs["region"])
    res = regional.region_proximity_test(mn.to_numpy(), regn.to_numpy())
    assert res["p"] == summ.attrs["p"] and res["gap"] == summ.attrs["gap"]
