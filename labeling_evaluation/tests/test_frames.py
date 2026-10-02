"""viz.frames reproduces the archived per-aircraft frame (la_tables.base) exactly."""
import pandas as pd
import pytest

from viz import config, data, frames


@pytest.fixture(scope="module")
def cfg():
    return config.load()


@pytest.fixture(scope="module")
def ds_new(cfg):
    return data.load_dataset(cfg)


@pytest.fixture(scope="module")
def fold5(archive):
    from src.dataset_facts import la_tables
    return la_tables.FOLD5


def test_base_equals_archive(ds_new, cfg, fold5, v):
    new = frames.base(ds_new, cfg, fold=fold5)
    pd.testing.assert_frame_equal(new, v, check_dtype=True, check_exact=True)
    assert list(new.columns) == list(v.columns)


def test_base_yaml_fold_differs_only_on_srw(ds_new, cfg, fold5, v):
    new = frames.base(ds_new, cfg)
    pd.testing.assert_frame_equal(new.drop(columns="class5"), v.drop(columns="class5"), check_exact=True)
    srw = v["topType"].eq("SRW")
    assert srw.sum() > 0
    assert (new.loc[srw, "class5"] == "LC").all() and (v.loc[srw, "class5"] == "ER").all()
    pd.testing.assert_series_equal(new.loc[~srw, "class5"], v.loc[~srw, "class5"])


def test_helpers_match_archive(archive, ds_new, cfg, fold5, v):
    from src.dataset_facts import la_tables
    new = frames.base(ds_new, cfg, fold=fold5)
    pd.testing.assert_series_equal(frames.firm_sizes(new), la_tables.firm_sizes(v))
    pd.testing.assert_series_equal(frames.patent_firm(new), la_tables.patent_firm(v))
    # the same functions applied to the archived frame
    pd.testing.assert_series_equal(frames.firm_sizes(v), la_tables.firm_sizes(v))
    pd.testing.assert_series_equal(frames.patent_firm(v), la_tables.patent_firm(v))


def test_assignee_functions_match_archive(archive, ds):
    from src.dataset_facts import la_tables
    raws = list(ds.identity["assignee_raw"]) + [None, "", "nan", "LUO AO", "株式会社 テスト", "Raytheon Co (US)"]
    for r in raws:
        assert frames.filer_from_assignee(r) == la_tables.filer_from_assignee(r)
        assert frames.firm_from_assignee(r) == la_tables.firm_from_assignee(r)


def test_windows_and_bins(archive, cfg):
    from src.dataset_facts import a2
    assert frames.windows_from_config(cfg) == a2.WINDOWS
    assert frames.ROTOR_BINS == a2.ROTOR_BINS and frames.CATCH_ALL == a2.CATCH_ALL
    for y in (float("nan"), 0, 2011, 2012, 2023, 2024, 2100, 2101):
        assert frames.window_of(y, frames.windows_from_config(cfg)) == a2.window_of(y)
