"""lib.intervals reproduces the archived Wilson and bootstrap intervals."""
import math

import numpy as np
import pandas as pd
import pytest

from lib import intervals as I

ATOL = dict(rtol=0, atol=1e-12)
GRID = [(k, n) for n in (0, 1, 2, 5, 10, 40, 100, 627) for k in sorted({0, 1, n // 2, max(n - 1, 0), n})]


def _csv(reference, name):
    return pd.read_csv(reference / f"{name}.csv", keep_default_na=False)


def test_wilson_matches_archive_and_copies_agree(archive):
    from src.dataset_facts import sm_figures, la_figures, sm_index
    for k, n in GRID:
        old, new = sm_figures._wilson(k, n), I.wilson_interval(k, n)
        assert np.allclose(old, new, **ATOL, equal_nan=True)
        # la_figures copy: half-width only
        assert np.allclose(la_figures._wilson_half(k, n), I.wilson_half_width(k, n), **ATOL, equal_nan=True)
        # sm_index copy without finite-population correction equals the sm_figures one
        fpc = sm_index.wilson_fpc(float(k), float(n), None)
        got = I.wilson_fpc_interval(float(k), float(n), None)
        if n == 0:
            assert fpc is None and got is None and np.isnan(new).all()
        else:
            assert np.allclose(fpc, got, **ATOL) and np.allclose(fpc, new, **ATOL)
            # half-width copy is (hi - lo)/2 whenever the interval is not clamped
            lo, hi = new
            if 0 < lo and hi < 1:
                assert np.isclose(I.wilson_half_width(k, n), (hi - lo) / 2, **ATOL)
        for N in (n, n + 1, 627, 1000):
            a, b = sm_index.wilson_fpc(float(k), float(n), N), I.wilson_fpc_interval(float(k), float(n), N)
            assert (a is None) == (b is None)
            if a is not None:
                assert np.allclose(a, b, **ATOL)


def test_wilson_known_value():
    # 50/100 at z = 1.96: textbook Wilson interval 0.4038 to 0.5962
    lo, hi = I.wilson_interval(50, 100)
    assert round(lo, 4) == 0.4038 and round(hi, 4) == 0.5962


def test_bootstrap_median_difference_reproduces_lag_offsets(archive, v, reference):
    from src.dataset_facts import sm_open, la_tables
    old = sm_open.lag_offsets(v)
    w = sm_open.lag_frame(v, sm_open.MIN_CELL)
    rng = np.random.default_rng(sm_open.SEED)
    rows = []
    for cls, sub in w.groupby("class", observed=True):
        ref = sub.loc[sub["region"].eq(sm_open.REFERENCE_REGION), "year"].to_numpy()
        for reg in la_tables.REGIONS:
            arr = sub.loc[sub["region"].eq(reg), "year"].to_numpy()
            if not len(arr) or not len(ref):
                continue
            r = I.bootstrap_median_difference(arr, ref, rng, draws=sm_open.DRAWS)
            rows.append((cls, reg, round(r["observed"], 1), round(r["low"], 1), round(r["high"], 1)))
    assert len(rows) == len(old)
    for (c, g, o, lo, hi), (_, r) in zip(rows, old.iterrows()):
        assert (c, g) == (r["class"], r["region"])
        assert (o, lo, hi) == (r["offset vs North America (years)"], r["95 % low"], r["95 % high"])
    ref_csv = _csv(reference, "la_lag_offsets")
    assert [x[2:] for x in rows] == [tuple(map(float, r)) for r in
                                     ref_csv[["offset vs North America (years)", "95 % low", "95 % high"]].values]


def _loglin_adapter(sm_open):
    return lambda years, counts: sm_open._loglin(years, counts)


def test_paired_year_bootstrap_reproduces_doubling_ratio(archive, ds, v, reference):
    from src.dataset_facts import sm_open
    old = sm_open.doubling_ratio(ds, v)
    series = sm_open._series_for_fit(ds, v)
    base_name = f"aeronautics — {sm_open.BASELINE_LABEL}"
    rng = np.random.default_rng(sm_open.SEED)
    got = []
    for lo, hi in [sm_open.FIT_WINDOW] + sm_open.FIT_SENSITIVITY:
        yrs, base = sm_open._window_frame(series[base_name], lo, hi)
        for name in ("eVTOL aircraft (this corpus)", "eVTOL patents (this corpus)"):
            _, top = sm_open._window_frame(series[name], lo, hi)
            if not sm_open._loglin(yrs, top) or not sm_open._loglin(yrs, base):
                continue
            d = I.paired_year_bootstrap_ratio(yrs, top, base, sm_open._loglin, rng, draws=sm_open.DRAWS)
            got.append((len(d), round(I.percentile_interval(d)[0], 3), round(I.percentile_interval(d)[1], 3)))
    assert len(got) == len(old)
    for (n, lo, hi), (_, r) in zip(got, old.iterrows()):
        assert n == r["draws used"] and lo == r["95 % low"] and hi == r["95 % high"]
    ref = _csv(reference, "la_doubling_ratio")
    assert [g[1] for g in got] == [float(x) for x in ref["95 % low"]]
    assert [g[2] for g in got] == [float(x) for x in ref["95 % high"]]


def test_paired_year_bootstrap_reproduces_growth_ratios(archive, ds, v, reference):
    from src.dataset_facts import sm_open
    old = sm_open.growth_ratios(ds, v)
    ser = sm_open.growth_series(ds, v)
    rng = np.random.default_rng(sm_open.SEED)
    got = []
    for lo, hi in (sm_open.GROWTH_WINDOW, sm_open.GROWTH_SENSITIVITY):
        for top_key in ("evtol_families", "evtol_aircraft"):
            yrs, top = sm_open._window_frame(ser[top_key], lo, hi)
            for base_key in ("b64", "secb", "all"):
                _, base = sm_open._window_frame(ser[base_key], lo, hi)
                if not sm_open._loglin(yrs, top) or not sm_open._loglin(yrs, base):
                    continue
                d = I.paired_year_bootstrap_ratio(yrs, top, base, sm_open._loglin, rng,
                                                  draws=sm_open.DRAWS, numerator="base")
                lo_ci, hi_ci = I.percentile_interval(d) if len(d) > 50 else (np.nan, np.nan)
                got.append(f"{lo_ci:.2f} to {hi_ci:.2f}")
    assert got == list(old["95 % interval"])
    assert got == list(_csv(reference, "la_growth_ratios")["95 % interval"])
