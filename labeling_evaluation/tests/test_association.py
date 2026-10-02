"""lib.association reproduces the archived tests (Cramér's V, chi-square, rank, exact, permutation)."""
import itertools

import numpy as np
import pandas as pd
import pytest

from lib import association as A

ATOL = dict(rtol=0, atol=1e-12)


@pytest.fixture(scope="module")
def la(archive):
    from src.dataset_facts import la_tables
    return la_tables


@pytest.fixture(scope="module")
def so(archive):
    from src.dataset_facts import sm_open
    return sm_open


def _csv(reference, name):
    return pd.read_csv(reference / f"{name}.csv", keep_default_na=False)


# ---------------------------------------------------------------- Cramér's V
def test_cramers_v_bc_all_coupling_pairs(archive, ds, v, la, reference):
    F = la._coupling_fields(ds, v)
    ref = _csv(reference, "la_trace_couplings_all")
    refd = {(r["field a"], r["field b"]): r for _, r in ref.iterrows()}
    n_pairs = 0
    for a, b in itertools.combinations(F.attrs["fields"], 2):
        old, new = la.cramers_v_bc(F[a], F[b]), A.cramers_v_bc(F[a], F[b])
        assert old[1] == new[1] and np.allclose(old[0], new[0], **ATOL, equal_nan=True)
        r = refd[(a, b)]
        assert r["aircraft"] == new[1]
        if pd.notna(new[0]):
            assert round(new[0], 3) == float(r["V"])
        else:
            assert r["V"] == ""
        n_pairs += 1
    assert n_pairs > 100


def test_cramers_v_bc_edge_cases(la):
    x = pd.Series(["a", "b"] * 20 + [None] * 3)
    assert np.isnan(A.cramers_v_bc(x, pd.Series(["u"] * 43))[0])          # one level -> NaN
    assert A.cramers_v_bc(x.iloc[:10], x.iloc[:10]) == la.cramers_v_bc(x.iloc[:10], x.iloc[:10])  # n < 30
    y = pd.Series(["a", "b"] * 20 + ["a"] * 3)
    assert np.allclose(A.cramers_v_bc(x, y)[0], la.cramers_v_bc(x, y)[0], **ATOL)


# ---------------------------------------------------------------- chi-square family
def test_chi2_p_of_crosstab_and_entry_split_test(archive, v, so, reference):
    w = so._named_frame(v)
    for wn in so.CH4_WINDOWS:
        sub = w[w["window"].eq(wn)]
        old = so._chi_p(sub)
        new = A.chi2_p_of_crosstab(sub["_c"], sub["first_time"])
        assert (old is None) == (new is None) and (old is None or np.isclose(old, new, **ATOL))
    tab = so.entry_split_test(v)
    ref = _csv(reference, "la_entry_split_test")
    for (_, r), (_, rr) in zip(tab.iterrows(), ref.iterrows()):
        sub = w[w["window"].eq(r["window"])]
        if pd.notna(r["p"]):
            p = A.chi2_p_of_crosstab(sub["_c"], sub["first_time"])
            assert np.isclose(p, r["p"], **ATOL) and round(p, 6) == round(float(rr["p"]), 6)
            p2 = A.chi2_p_of_crosstab(sub[sub["firm"].ne(r["largest returning firm"])]["_c"],
                                      sub[sub["firm"].ne(r["largest returning firm"])]["first_time"])
            assert np.isclose(p2, r["p without it"], **ATOL)


def test_chi2_p_of_columns_and_region_tests(archive, ds, v, so, reference):
    w = so._ch5_frame(ds, v)
    for a, b in (("region3", "cls5"), ("region3", "rb"), ("region3", "tilt"), ("region3", "F")):
        old, new = so._chi(w, a, b), A.chi2_p_of_columns(w, a, b)
        assert old[1] == new[1] and np.allclose(old[0], new[0], **ATOL, equal_nan=True)
    tab = so.region_tests(ds, v)
    ref = _csv(reference, "la_region_tests")
    row = tab.iloc[0]
    assert round(A.chi2_p_of_columns(w, "region3", "cls5")[0], 4) == row["p (chi-square, region)"]
    assert row["p (chi-square, region)"] == float(ref.iloc[0]["p (chi-square, region)"])


def test_chi2_test_dict(archive, v, la):
    # duct_by_units attrs: chi2, dof, p of band / class / region / window against the duct answer
    out = la.duct_by_units(v)
    w = None
    for key in ("class", "region", "window"):
        assert "p" in out.attrs[key]
    # direct: a crosstab the archive tests
    tab = pd.crosstab(v["topType"], v["region3"])
    r = A.chi2_test(tab.values)
    from scipy.stats import chi2_contingency
    c, p, dof, _ = chi2_contingency(tab.values)
    assert (r["chi2"], r["p"], r["dof"]) == (c, p, dof)


def test_force_aircraft_test(archive, ds, v, so):
    w = so._force_frame(ds, v, so.FORCE_MAX_YEAR)
    size = w.groupby("topType").size()
    keep = w[w["topType"].isin(size[size.ge(so.FORCE_TEST_MIN)].index)]
    old = so.force_aircraft_test(ds, v)
    r = A.chi2_test(pd.crosstab(keep["topType"], keep["out"]).values)
    first = old.iloc[0]
    assert round(r["chi2"], 2) == first["chi2"] and r["dof"] == first["dof"] and np.isclose(r["p"], first["p"], **ATOL)


def test_representativeness_chi2_mw_tvd(archive, v, la, reference):
    # linked set vs the rest (la_linked_representativeness)
    w = v.copy()
    linked = set(la.linked_aircraft(v)["aircraft_id"])
    w["_linked"] = w["aircraft_id"].isin(linked)
    old = la.linked_representativeness(v)
    ref = _csv(reference, "la_linked_representativeness")
    checked = 0
    for name, col in la.LINKED_CATEGORICAL:
        a, b = w.loc[w["_linked"], col], w.loc[~w["_linked"], col]
        levels = list(pd.concat([a, b]).dropna().value_counts().index)
        if col == "window":
            levels = [x for x in la.WINDOW_NAMES if x in levels]
        ca, cb = a.value_counts().reindex(levels).fillna(0), b.value_counts().reindex(levels).fillna(0)
        p = A.chi2_p_two_groups(ca.to_numpy(), cb.to_numpy())
        tvd = A.total_variation_distance(ca.to_numpy(), cb.to_numpy(), len(a), len(b))
        r = old[(old["attribute"] == name)].iloc[0]
        assert round(p, 4) == r["p"] and round(tvd, 3) == r["total variation distance"]
        rr = ref[ref["attribute"] == name].iloc[0]
        assert round(p, 4) == float(rr["p"]) and round(tvd, 3) == float(rr["total variation distance"])
        checked += 1
    for name, col in la.LINKED_CONTINUOUS:
        a = pd.to_numeric(w.loc[w["_linked"], col], errors="coerce").dropna()
        b = pd.to_numeric(w.loc[~w["_linked"], col], errors="coerce").dropna()
        p = A.mann_whitney_p(a, b)
        r = old[(old["attribute"] == name) & (old["test"] == "Mann-Whitney")].iloc[0]
        assert round(p, 6) == r["p"]
        checked += 1
    assert checked >= 5
    # same two functions inside the generic _representativeness (index firms and TRL tables)
    firms = set(la.ari_firms(v)["company"])
    mask = v["company_canonical"].isin(firms)
    tab = la.ari_representativeness(v)
    for name, col in la.LINKED_CATEGORICAL:
        a, b = v.loc[mask, col], v.loc[~mask, col]
        levels = list(pd.concat([a, b]).dropna().value_counts().index)
        if col == "window":
            levels = [x for x in la.WINDOW_NAMES if x in levels]
        ca, cb = a.value_counts().reindex(levels).fillna(0), b.value_counts().reindex(levels).fillna(0)
        p = A.chi2_p_two_groups(ca.to_numpy(), cb.to_numpy())
        assert round(p, 4) == tab[tab["attribute"] == name]["p"].iloc[0]
    # degenerate input does not raise
    assert np.isnan(A.chi2_p_two_groups([0, 0], [0, 0]))


def test_fisher_and_tw_entry(archive, v, so, reference):
    out = so.tw_entry(v)
    col = "Tilt Wing share, Fisher p against the window before"
    got = [np.nan]
    for i in range(1, len(out)):
        a, b = out.iloc[i - 1], out.iloc[i]
        tab = [[int(a["Tilt Wing aircraft"]), int(a["aircraft in the window"] - a["Tilt Wing aircraft"])],
               [int(b["Tilt Wing aircraft"]), int(b["aircraft in the window"] - b["Tilt Wing aircraft"])]]
        got.append(round(A.fisher_exact_p(tab), 3))
    assert np.allclose(got, out[col].astype(float), **ATOL, equal_nan=True)
    ref = _csv(reference, "la_tw_entry")[col].replace("", np.nan).astype(float)
    assert np.allclose(got, ref, **ATOL, equal_nan=True)


# ---------------------------------------------------------------- Spearman
def test_spearman_trend(archive, v, so, la, reference):
    checked = 0
    cols = ["wCount", "nBooms", "year", "units", "rotorN"]
    cand = [c for c in v.columns if v[c].dtype.kind in "fi"][:40]
    for c in dict.fromkeys(cols + cand):
        if c not in v.columns:
            continue
        old = so._spearman(v["year"], v[c])
        new = A.spearman_trend(v["year"], v[c])
        assert old["aircraft"] == new["aircraft"] and old["movement"] == new["movement"]
        if "rho" in old and pd.notna(old["rho"]):
            assert old["rho"] == round(new["rho"], 2) and np.isclose(old["p"], new["p"], **ATOL)
        else:
            assert np.isnan(new["rho"]) and np.isnan(new["p"])
        checked += 1
    assert checked >= 10
    # defaults are the document's constants
    assert (A.LAST_COMPLETE, A.TREND_MIN, A.TREND_ALPHA) == (la.LAST_COMPLETE, la.TREND_MIN, la.TREND_ALPHA)


def test_spearman_trend_reproduces_trace_trends_rows(archive, ds, v, la, reference):
    ref = _csv(reference, "la_trace_trends")
    tt = la.trace_trends(ds, v)
    assert len(tt) == len(ref)
    # the rows are produced by exactly this test: re-run it on the same toy input twice
    s = pd.Series(np.arange(40) % 7, dtype=float)
    yr = pd.Series(2000 + np.arange(40) % 24)
    from src.dataset_facts import sm_open
    o, n = sm_open._spearman(yr, s), A.spearman_trend(yr, s)
    assert o["aircraft"] == n["aircraft"] and o["movement"] == n["movement"] and o["rho"] == round(n["rho"], 2)


def test_spearman_rho_p_ari_funding_tests(archive, v, so, reference):
    fr = so.ari_funding(v)
    d = fr[fr["funding $M"].notna()]
    old = so.ari_funding_tests(v, fr)
    for (_, r) in old.iterrows():
        s = d[["funding $M", r["column"]]].dropna()
        rho, p = A.spearman_rho_p(s["funding $M"], s[r["column"]], min_n=3)
        assert (np.isnan(rho) and np.isnan(r["rho"])) or (round(rho, 2) == r["rho"] and round(p, 3) == r["p"])
    ref = _csv(reference, "la_ari_funding_tests")
    assert list(old["rho"].astype(float)) == [float(x) for x in ref["rho"]]
    assert np.isnan(A.spearman_rho_p([1, 2], [1, 2], min_n=3)[0])
    assert np.isnan(A.spearman_rho_p([1, 2, 3, 4], [1, 1, 1, 1], require_variation=True)[0])


def test_spearman_in_region_mix_change(archive, ds, v, so, la, reference):
    w = so._ch5_frame(ds, v)
    old = so.region_mix_change(ds, v)
    lo, hi = so.CH5_TREND
    n_checked = 0
    for _, r in old.iterrows():
        col = so._ch5_col(r["variable"])
        s = w[w["region3"].eq(r["region"]) & w[col].notna()]
        tr = s[s["year"].between(lo, hi)]
        cats = dict(list(so.CH5_VARS.items()) + [("family F", ("F", [True]))])[r["variable"]][1]
        c = [x for x in cats if str(x) == r["answer"]][0]
        rho, p = A.spearman_rho_p(tr["year"], tr[col].eq(c).astype(int), require_variation=True)
        if np.isnan(r["rho"]):
            assert np.isnan(rho)
        else:
            assert round(rho, 3) == r["rho"] and round(p, 4) == r["p"]
        n_checked += 1
    assert n_checked == len(old) > 30


def test_market_vs_patents_mw_and_spearman(archive, v, la, reference):
    from scipy.stats import mannwhitneyu
    f = la.firm_frame(v)
    old = la.market_vs_patents(v)
    for col, idx in (("unique aircraft", 1), ("patents", 2), ("first priority year", 3),
                     ("distinct classes", 4)):
        a = f.loc[f["on the AAM index"], col].dropna()
        b = f.loc[~f["on the AAM index"], col].dropna()
        assert round(A.mann_whitney_p(a, b, alternative="two-sided"), 3) == old.iloc[idx]["p"]
        assert A.mann_whitney_p(a, b) == A.mann_whitney_p(a, b, alternative="two-sided")
    ref = _csv(reference, "la_market_vs_patents")
    assert [float(x) if x != "" else np.nan for x in ref["p"]] == pytest.approx(
        [float(x) for x in old["p"].fillna(np.nan)], nan_ok=True)


# ---------------------------------------------------------------- Cohen's kappa
def test_cohen_kappa(archive, v):
    from src.dataset_facts import metrics
    rng = np.random.default_rng(0)
    a = v["topType"].copy()
    b = a.copy()
    flip = rng.random(len(b)) < 0.3
    b[flip] = rng.permutation(b[flip].to_numpy())
    b[rng.random(len(b)) < 0.05] = np.nan
    assert np.allclose(A.cohen_kappa(a, b), metrics.cohen_kappa(a, b), **ATOL)
    assert A.raw_agreement(a, b)[0] == metrics.agreement(a, b)["n"]
    assert round(A.raw_agreement(a, b)[1], 3) == metrics.agreement(a, b)["agreement"]
    # known values: perfect, chance-level, constant (NaN), empty (NaN)
    assert A.cohen_kappa(["x", "y"] * 5, ["x", "y"] * 5) == 1.0
    assert np.isnan(A.cohen_kappa(["x"] * 4, ["x"] * 4)) and np.isnan(A.cohen_kappa([], []))
    # textbook 2x2: a=20,b=5,c=10,d=15 -> kappa = 0.4
    xs = ["Y"] * 20 + ["Y"] * 5 + ["N"] * 10 + ["N"] * 15
    ys = ["Y"] * 20 + ["N"] * 5 + ["Y"] * 10 + ["N"] * 15
    assert np.isclose(A.cohen_kappa(xs, ys), 0.4, atol=1e-12)


# ---------------------------------------------------------------- BH and Holm
def test_bh_qvalues_reproduces_ari_correlation(archive, ds, v, la, monkeypatch, reference):
    import scipy.stats as st
    seen = []
    real = st.spearmanr

    def spy(*a, **k):
        r = real(*a, **k)
        seen.append(float(r.pvalue))
        return r

    monkeypatch.setattr(st, "spearmanr", spy)
    firms = la.ari_firms(v)
    out = la.ari_correlation(firms, v, ds)
    p_raw = np.array(seen[-len(out):])
    assert len(p_raw) == len(out)
    q = A.bh_qvalues(p_raw)
    assert np.allclose(np.sort(np.round(q, 3)), np.sort(out["q (BH)"].to_numpy()), **ATOL)
    ref = _csv(reference, "la_ari_correlation")
    assert np.allclose(np.sort(np.round(q, 3)), np.sort(ref["q (BH)"].astype(float).to_numpy()), **ATOL)


def test_bh_and_holm_reference_values():
    p = np.array([0.01, 0.04, 0.03, 0.005, 0.5])
    # BH by hand: sorted .005 .01 .03 .04 .5 -> p*m/i = .025 .025 .05 .05 .5 ; cummin from the end
    assert np.allclose(A.bh_qvalues(p), [0.025, 0.05, 0.05, 0.025, 0.5], **ATOL)
    # Holm by hand: sorted .005*5 .01*4 .03*3 .04*2 .5*1 = .025 .04 .09 .08 .5 ; cummax
    assert np.allclose(A.holm_adjust(p), [0.04, 0.09, 0.09, 0.025, 0.5], **ATOL)
    # the archive's expression on sorted input
    ps = np.sort(p)
    arch = (ps * 5 / (np.arange(5) + 1))[::-1]
    arch = pd.Series(arch).cummin().to_numpy()[::-1]
    assert np.allclose(A.bh_qvalues(ps), arch, **ATOL)


# ---------------------------------------------------------------- permutation tests
def test_interaction_permutation_and_holm(archive, v, so, reference):
    perms = 300
    old = so.lag_constancy(v, perms=perms)
    w = so.lag_frame(v)
    from scipy import stats as st
    y = st.rankdata(w["year"].to_numpy())
    Xf, Xa = A.design_matrix(w["class"], w["region"], True), A.design_matrix(w["class"], w["region"], False)
    assert np.array_equal(Xf, so._design(w, True)) and np.array_equal(Xa, so._design(w, False))
    r = A.interaction_permutation_test(Xf, Xa, y, perms=perms)
    row = old.iloc[0]
    assert r["df"] == row["df"] and round(r["F"], 2) == row["F (on ranks)"]
    assert np.isclose(r["p_param"], row["p (parametric)"], **ATOL) and np.isclose(r["p_perm"], row["p (permutation)"], **ATOL)
    assert round(r["partial_eta2"], 4) == row["partial η²"]
    # main effects
    Xcls = np.column_stack([np.ones(len(w)), pd.get_dummies(w["class"], drop_first=True, dtype=float).to_numpy()])
    Xreg = np.column_stack([np.ones(len(w)), pd.get_dummies(w["region"], drop_first=True, dtype=float).to_numpy()])
    m = A.nested_f_test(Xcls, Xa, y)
    mrow = old.iloc[1]
    assert round(m["F"], 2) == mrow["F (on ranks)"] and np.isclose(m["p_param"], mrow["p (parametric)"], **ATOL)
    assert round(m["partial_eta2"], 4) == mrow["partial η²"] and m["df"] == mrow["df"]
    m2 = A.nested_f_test(Xreg, Xa, y)
    assert round(m2["F"], 2) == old.iloc[2]["F (on ranks)"]
    # per-region homogeneity tests and Holm
    regs = old[old["effect"].str.startswith("class × region,")]
    ps = []
    for _, rr in regs.iterrows():
        sub = w[w["region"].isin([so.REFERENCE_REGION, rr["region tested"]])].copy()
        sub["region"] = sub["region"].astype(str)
        ysub = st.rankdata(sub["year"].to_numpy())
        res = A.interaction_permutation_test(A.design_matrix(sub["class"], sub["region"], True),
                                             A.design_matrix(sub["class"], sub["region"], False), ysub, perms=perms)
        assert np.isclose(res["p_perm"], rr["p (permutation)"], **ATOL) and round(res["F"], 2) == rr["F (on ranks)"]
        ps.append(res["p_perm"])
    holm = A.holm_adjust(ps)
    assert np.allclose(np.round(holm, 4), regs["p (Holm, across the two regions)"].to_numpy(), **ATOL)
    # the document's own full-size run (5000 permutations): F and parametric p are deterministic
    ref = _csv(reference, "la_lag_constancy")
    assert round(r["F"], 2) == float(ref.iloc[0]["F (on ranks)"])
    assert np.isclose(r["p_param"], float(ref.iloc[0]["p (parametric)"]), **ATOL)
    assert round(r["partial_eta2"], 4) == float(ref.iloc[0]["partial η²"])


def test_interaction_permutation_full_5000_matches_document(archive, v, so, reference):
    from scipy import stats as st
    w = so.lag_frame(v)
    y = st.rankdata(w["year"].to_numpy())
    r = A.interaction_permutation_test(A.design_matrix(w["class"], w["region"], True),
                                       A.design_matrix(w["class"], w["region"], False), y)
    ref = _csv(reference, "la_lag_constancy").iloc[0]
    assert np.isclose(r["p_perm"], float(ref["p (permutation)"]), **ATOL)


