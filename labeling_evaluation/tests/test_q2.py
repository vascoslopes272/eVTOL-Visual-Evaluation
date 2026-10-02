"""Question 2 (notebook 41): the wrangling of viz.frames reproduces the archive (imported HERE ONLY, via the conftest fixtures)."""
import numpy as np
import pandas as pd
import pytest

from lib import diversity
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


def _same(a: pd.DataFrame, b: pd.DataFrame):
    assert list(a.columns) == list(b.columns)
    pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True), check_dtype=False)


def test_selected_fields(archive, ds, dsn):
    from src.dataset_facts import a2
    old = a2.d3_selected_fields(ds)
    new = frames.selected_fields(dsn)
    new["name"] = new["name"].replace({frames.D3_UNITS_ROW: "propulsor units per aircraft",
                                       frames.D3_PLACES_ROW: "propulsor groups per aircraft"})
    _same(new, old)


def test_duct_tables_and_features(archive, ds, v, vn):
    from src.dataset_facts import la_tables
    _same(frames.duct_count_by_units(vn), la_tables.duct_count_by_units(v))
    _same(frames.duct_conditional(vn), la_tables.duct_conditional(v))


def test_archetype_sets(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import la_tables, sm_open
    old = la_tables.archetype_levels(ds, v)
    new = frames.archetype_levels_table(dsn, vn, cfg)
    for c in new.columns:
        if c != "level":
            assert (new[c].astype(str).to_numpy() == old[c].astype(str).to_numpy()).all(), c
    choice = la_tables.archetype_level_choice(old)
    scr = frames.archetype_screens(new, cfg)
    assert list(scr["screens passed"]) == list(choice["screens passed"])
    b_old = sm_open.archetype_levels_brief(ds, v)
    b_new = frames.archetype_levels_brief(dsn, vn, new)
    for c in ["aircraft", "archetypes", "aircraft alone in their archetype", "effective number ¹D", "its share", "archetypes of five or more"]:
        assert np.allclose(b_new[c].astype(float), b_old[c].astype(float), rtol=0, atol=1e-12), c
    assert list(b_new["largest archetype"]) == [x.replace("Tilt Rotor", "Tilt Propulsor").replace(" units", " propulsor units")
                                                  if "Tilt" in x else x for x in b_old["largest archetype"]]


def test_zones_filers_discovery(archive, ds, v, dsn, vn, cfg):
    from src.dataset_facts import la_tables, sm_open
    wn = list(cfg.analysis["windows"])
    z_old, z_new = la_tables.zones(v), frames.zones(vn, wn)
    _same(z_new.drop(columns="class"), z_old.drop(columns="class"))
    assert (frames.zone_core(z_new) == la_tables.zone_core(z_old)).all()
    _same(frames.archetype_filer_split(vn, 20), sm_open.archetype_filer_split(v, 20))
    inputs = frames.discovery_inputs(vn, ["A0", "A0c", "A1t"], 2023)
    curve = diversity.discovery_curve_levels(inputs, orders=400, seed=42)
    old = sm_open.discovery_curve(ds, v)
    _same(curve, old)
    est_old = sm_open.discovery_estimators(ds, v, curve=old)
    est = frames.discovery_estimators(inputs, curve)
    for c in ["aircraft", "archetypes observed", "Chao1", "Chao1 95 % low", "Chao1 95 % high", "estimated unseen", "coverage",
              "share of richness found", "new in the last 100 aircraft", "new in the last 100, random order"]:
        assert np.allclose(est[c].astype(float), est_old[c].astype(float), rtol=0, atol=1e-12), c
    fl_old, fl_new = la_tables.family_flags(ds, v), frames.family_flags(dsn, vn)
    assert (la_tables.family_mask(fl_old, "b").to_numpy() == frames.family_mask(fl_new).to_numpy()).all()
