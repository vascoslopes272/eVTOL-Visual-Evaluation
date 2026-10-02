"""Question 4 (notebook 43): the wrangling of viz.frames reproduces the archive (imported HERE ONLY, via the conftest fixtures)."""
import numpy as np
import pandas as pd
import pytest

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


def test_who_files(archive, ds, v, dsn, vn):
    from src.dataset_facts import la_tables, sm_open
    W = list(la_tables.WINDOW_NAMES)
    _same(frames.filer_mix(vn), la_tables.filer_mix(v))
    _same(frames.filer_mix_representative(dsn), sm_open.filer_mix_representative(ds))
    _same(frames.coverage_table(vn), la_tables.coverage_segments(v))
    _same(frames.filers_by_window(vn, W), la_tables.filers_by_window(v))


def test_concentration_and_leverage(archive, ds, v, vn):
    from src.dataset_facts import la_tables, sm_open
    W = list(la_tables.WINDOW_NAMES)
    complete = [w for w in W if not w.startswith("2024")]
    old = sm_open.class_concentration_brief(v)
    new = frames.class_concentration_brief(vn, complete)
    _same(new, old, [c for c in old.columns if c != "class"])
    assert [str(x).lower().replace("propulsor", "rotor") for x in new["class"]] == [str(x).lower() for x in old["class"]]
    lev_old, lev_new = la_tables.firm_leverage(v), frames.firm_leverage_table(vn, W)
    _same(lev_new, lev_old)
    _same(frames.firm_leverage_classes(vn, W, lev=lev_new), sm_open.firm_leverage_classes(v))


def test_funding(archive, ds, v, vn, cfg):
    from src.dataset_facts import sm_open
    old = sm_open.ari_funding(v)
    new = frames.ari_funding_frame(vn, cfg)
    _same(new, old)
    _same(frames.ari_funding_tests(new), sm_open.ari_funding_tests(v, old))


def test_entry_and_successions(archive, ds, v, vn):
    from src.dataset_facts import la_tables, sm_open
    W = list(la_tables.WINDOW_NAMES)
    complete = [w for w in W if not w.startswith("2024")]
    names = {"SLC": "Lift + Cruise", "TR": "Tilt Rotor", "CVT": "CVT", "TW": "Tilt Wing", "MR": "Multirotor", "other": "other classes"}
    w = frames.named_entries(vn, W)
    _same(frames.entry_split(w, complete, names), sm_open.entry_split(v))
    old_t, new_t = sm_open.entry_split_test(v), frames.entry_split_test(w, complete)
    _same(new_t, old_t, [c for c in old_t.columns if c not in ("p", "p without it")])
    for c in ("p", "p without it"):
        assert np.allclose(pd.to_numeric(new_t[c], errors="coerce"), pd.to_numeric(old_t[c], errors="coerce"), rtol=0, atol=1e-12, equal_nan=True)
    _same(frames.tw_entry(vn, complete), sm_open.tw_entry(v))
    pairs = frames.succession_pairs(vn)
    _same(pairs, sm_open._succession_pairs(v))
    old_m, new_m = sm_open.succession_matrix(v), frames.succession_matrix(pairs)
    assert [str(x).lower().replace("propulsor", "rotor") for x in new_m["class of origin"]] == [str(x).lower() for x in old_m["class of origin"]]
    _same(new_m, old_m, [c for c in old_m.columns if c != "class of origin"])
