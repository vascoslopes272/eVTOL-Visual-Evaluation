"""lib.distance reproduces the archived Gower distance, nearest neighbours and Jaffe proximity."""
import numpy as np
from lib import regional
import pandas as pd
import pytest

from lib import distance as dist

ATOL = dict(rtol=0, atol=1e-12)


@pytest.fixture(scope="module")
def setup(archive, ds):
    from src.dataset_facts import a3
    frame = a3.gower_frame(ds)
    return a3, frame


@pytest.mark.parametrize("pooled", [True, False])
@pytest.mark.parametrize("weighting", ["subsystem", "uniform"])
def test_gower_distance(archive, ds, setup, pooled, weighting):
    a3, frame = setup
    fields = a3.gower_fields(ds, pooled=pooled)
    numeric = {f for f in fields if a3._is_numeric(ds, f)}
    w = (dist.subsystem_weights(fields, a3.SUBSYSTEM_OF) if weighting == "subsystem"
         else dist.uniform_weights(fields))
    for fr in (frame, frame.iloc[::3]):
        a = a3.gower_distance(ds, fr, fields, weighting=weighting)
        b = dist.gower_distance(fr, fields, numeric, w)
        assert np.array_equal(np.isnan(a), np.isnan(b))
        assert np.allclose(a, b, **ATOL, equal_nan=True)


def test_nearest_neighbours(archive, ds, setup):
    a3, frame = setup
    fields = a3.gower_fields(ds, pooled=True)
    D = a3.gower_distance(ds, frame, fields)
    ids = frame["aircraft_id"].to_numpy()
    assert a3.nearest_neighbours(D, ids) == dist.nearest_neighbours(D, ids)
    # NaN handling and ties
    D2 = np.array([[0, 1, 1, np.nan], [1, 0, 2, np.nan], [1, 2, 0, 0.5], [np.nan, np.nan, 0.5, 0]])
    ids2 = np.array(["a", "b", "c", "d"])
    assert a3.nearest_neighbours(D2, ids2) == dist.nearest_neighbours(D2, ids2)


def _profiles(ds, a2, la, v):
    prof = a2.firm_profiles(ds, la.FIRM_MIN, "class")
    prox = a2.proximity_matrix(prof)
    clustered = a2.proximity_order(prox)
    reg = la.firm_region(v).reindex(clustered)
    blocks = la.REGIONS + sorted({str(r) for r in reg if r not in la.REGIONS})
    order = [f for b in blocks for f in clustered if reg[f] == b]
    return prof, prox, order, reg.reindex(order)


def test_jaffe_and_region_test(archive, ds, v, reference):
    from src.dataset_facts import a2, la_tables as la
    prof, prox, order, reg = _profiles(ds, a2, la, v)
    mine = dist.jaffe_proximity(prof)
    assert np.allclose(prox, mine, **ATOL)
    m = mine.loc[order, order]
    _, summ = la.proximity_by_region(ds, v, draws=500)
    r = regional.region_proximity_test(m, reg.to_numpy(), draws=500)
    a = summ.attrs
    assert round(r["same_mean"], 3) == a["same mean"] and r["same_pairs"] == a["same pairs"]
    assert round(r["different_mean"], 3) == a["different mean"] and r["different_pairs"] == a["different pairs"]
    assert round(r["gap"], 3) == a["gap"] and r["p"] == a["p"] and r["draws"] == a["draws"]


def test_region_test_default_vs_reference(archive, ds, v, reference):
    from src.dataset_facts import a2, la_tables as la
    _, prox, order, reg = _profiles(ds, a2, la, v)
    r = regional.region_proximity_test(prox.loc[order, order], reg.to_numpy())   # draws=10000
    ref = pd.read_csv(reference / "la_region_proximity_test.csv", keep_default_na=False).iloc[0]
    assert r["same_pairs"] == ref["same-region pairs"] and r["different_pairs"] == ref["different-region pairs"]
    assert round(r["same_mean"], 3) == ref["same-region mean"]
    assert round(r["different_mean"], 3) == ref["different-region mean"]
    assert r["p"] == ref["p (permutation)"] and r["draws"] == ref["draws"]
