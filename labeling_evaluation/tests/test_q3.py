"""Question 3 (notebook 42): the wrangling of viz.frames reproduces the archive (imported HERE ONLY, via the conftest fixtures)."""
import numpy as np
import pandas as pd
import pytest

from lib import drivers
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
    frames.set_window_bounds(cfg)
    return frames.base(dsn, cfg, fold=la_tables.FOLD5)


def _same(a, b, cols=None):
    cols = cols or list(b.columns)
    assert len(a) == len(b)
    for c in cols:
        x, y = a[c].to_numpy(), b[c].to_numpy()
        if x.dtype.kind in "fiu" and y.dtype.kind in "fiu":
            assert np.allclose(x.astype(float), y.astype(float), rtol=0, atol=1e-12, equal_nan=True), c
        else:
            assert [str(i) for i in x] == [str(i) for i in y], c


def test_family_and_yearly(archive, ds, v, dsn, vn):
    from src.dataset_facts import sm_open
    _same(frames.family_yearly(dsn, vn, 2023), sm_open.family_yearly(ds, v))
    a = sm_open.dd_yearly(ds, v)
    b = frames.dd_yearly(dsn, vn, 2023)
    _same(b, a, ["level id", "base", "priority year", "aircraft", "its aircraft", "its share", "tied", "read", "above 50 %"])
    assert [x.replace("Tilt Propulsor", "Tilt Rotor").replace("propulsor units", "units") for x in b["largest archetype"]] == list(a["largest archetype"])


def test_dd_tables_and_verdict(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import sm_open, la_tables
    W = list(cfg.analysis["windows"])
    perms = 20
    ab = sm_open.dd_balance(ds, v, perms=perms)
    mb = frames.dd_balance_table(dsn, vn, W, 40, perms, 42)
    _same(mb, ab, ["level", "window", "aircraft", "top share", "top-2 share", "D2", "D2 low", "D2 high",
                   "D2 permutation low", "D2 permutation high", "below band"])
    af = sm_open.dd_form(ds, v, perms=perms)
    mf = frames.dd_form_table(dsn, vn, W, perms, 42)
    _same(mf, af, ["level", "weighting", "window", "aircraft", "Q", "ΔQ", "ΔQ permutation low", "ΔQ permutation high", "below band"])
    ay = sm_open.dd_yearly(ds, v)
    old = sm_open.dd_levels(ay, ab, af)
    new = frames.dd_levels(frames.dd_yearly(dsn, vn, 2023), mb, mf, W)
    assert new.astype(str).values.tolist() == old.astype(str).values.tolist()


def test_configs_and_drivers(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import sm_open, metrics, la_tables
    W = [w for w in cfg.analysis["windows"] if "partial" not in w]
    cf_new, cf_old = frames.config_frame(dsn, vn), sm_open.config_frame(ds, v)
    _same(cf_new, cf_old, [c for c in cf_old.columns if c not in ("topType", "window")])
    keys = frames.class_config_keys(dsn, vn, cf_new, W)
    old_keys = sm_open._class_config_keys(ds, v)
    assert keys.astype(str).values.tolist() == old_keys.astype(str).values.tolist()
    names = metrics.ARCH_NAMES
    _same(frames.class_configs_brief(keys, W, W[:2], names), sm_open.class_configs_brief(ds, v, old_keys))
    _same(frames.class_config_mix(keys, names), sm_open.class_config_mix(ds, v, old_keys))
    _same(drivers.driver_windows(cf_new, frames.CH3B_CLASSES, W, W[:2], class_names=names), sm_open.driver_windows(ds, v, cf_old))
    _same(drivers.driver_links(cf_new), sm_open.driver_links(ds, v, cf_old))
    ws = {"<= 2011": "≤2011", "2012-15": "12–15", "2016-19": "16–19", "2020-23": "20–23"}
    _same(frames.sets_per_unit_brief(cf_new, W, ws), sm_open.sets_per_unit_brief(ds, v, cf_old))


def test_directory_and_funding(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import sm_open
    old = sm_open.evtolnews_coverage()
    new = frames.evtolnews_coverage(cfg)
    assert new.astype(str).values.tolist() == old[new.columns].astype(str).values.tolist()
    ext = sm_open.external_tables(ds, v)["la_ext_f_funding"]
    mine = frames.ari_f_funding(dsn, vn, cfg)
    _same(mine, ext, ["kind", "company", "funding $M", "unique aircraft", "aircraft in family F", "share in family F", "funding-weighted F share"])
