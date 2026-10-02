"""lib.concentration reproduces the archived concentration equations."""
import numpy as np
import pandas as pd
import pytest

from lib import concentration as C

ATOL = dict(rtol=0, atol=1e-12)


@pytest.fixture(scope="module")
def la(archive):
    from src.dataset_facts import la_tables
    return la_tables


def _csv(reference, name):
    return pd.read_csv(reference / f"{name}.csv", keep_default_na=False)


def test_hhi_and_concentration(archive, ds, v, reference):
    from src.dataset_facts import metrics, a2
    cols = [v["company_canonical"], v["firm"], v["assignee_raw"], v["topType"], v["region3"]]
    for s in cols:
        assert np.isclose(C.hhi(s), metrics.hhi(s), **ATOL)
        assert np.isclose(C.top_k_share(s, 3), metrics.top_k_share(s, 3), **ATOL, equal_nan=True)
        for top_n in (3, 10):
            old, new = metrics.concentration(s, top_n), C.concentration(s, top_n)
            assert new["distinct"] == old["distinct"] and new["singletons"] == old["singletons"]
            assert round(new["top_n_share"], 2) == old[f"top{top_n}_share"]
            assert round(new["hhi"], 3) == old["hhi"]
            assert f"{new['largest']}, {new['largest_count']}" == old["largest"]
    # empty series
    e = pd.Series([], dtype=object)
    assert C.concentration(e)["distinct"] == 0 and np.isnan(C.concentration(e)["top_n_share"])
    # the document table (a2_d8_concentration) is built from these calls, on the same inputs
    j = a2._filers(ds)
    raw = a2.normalise_assignee(j["assignee_raw"])
    cc = j["company_canonical"]
    named = cc[~cc.isin(a2.CATCH_ALL) & cc.notna()]
    tab = a2.d8_concentration(ds).set_index("concentration measure")
    c = C.concentration(raw)
    assert c["distinct"] == tab.iloc[0, 0] and c["singletons"] == tab.iloc[1, 0]
    assert round(c["top_n_share"], 2) == tab.iloc[2, 0] and round(c["hhi"], 3) == tab.iloc[3, 0]
    assert f"{c['largest']}, {c['largest_count']}" == tab.iloc[4, 0]
    nc = named.value_counts()
    assert round(C.top_n_share_over_total(nc, len(j)), 2) == float(tab.iloc[2, 1].split()[0])
    assert round(C.hhi_over_total(nc, len(j)), 3) == float(tab.iloc[3, 1].split()[0])
    cn = C.concentration(named)
    assert f"{cn['largest']}, {cn['largest_count']}" == tab.iloc[4, 1]
    assert cn["singletons"] == int(tab.iloc[1, 1].split()[0])
    # and the numbers the document printed
    ref = pd.read_csv(reference / "a2_d8_concentration.csv", keep_default_na=False)
    assert c["distinct"] == int(ref.iloc[0, 1]) and round(c["hhi"], 3) == float(ref.iloc[3, 1])
    assert round(C.hhi_over_total(nc, len(j)), 3) == float(ref.iloc[3, 2].split()[0])


def test_coverage_segments(archive, la, v, reference):
    sizes = la.firm_sizes(v)
    old = la.coverage_segments(v)
    new = C.coverage_segments(sizes, len(v))
    assert len(old) == len(new)
    assert list(new["firms"]) == list(old["firms"])
    assert list(new["aircraft"]) == list(old["aircraft"])
    assert list(new["cumulative_firms"]) == list(old["cumulative firms"])
    assert list(new["cumulative_aircraft"]) == list(old["cumulative aircraft"])
    assert np.allclose(new["share"].round(3), old["share of the analysis set"], **ATOL)
    ref = _csv(reference, "la_coverage_segments")
    assert list(new["firms"]) == list(ref["firms"]) and list(new["aircraft"]) == list(ref["aircraft"])
    assert np.allclose(new["share"].round(3), ref["share of the analysis set"].astype(float), **ATOL)


def test_firm_leverage(archive, la, v, reference):
    old = la.firm_leverage(v)
    sizes = la.firm_sizes(v)
    cand = list(sizes[sizes >= 3].index)
    new = C.firm_leverage(v["topType"], v["company_canonical"], cand,
                          window=v["window"], windows=la.WINDOW_NAMES[:-1])
    new["mag"] = new["shift"].abs()
    new = new.sort_values("mag", ascending=False, kind="quicksort").reset_index(drop=True)
    # the archive sorts the rounded (pp) magnitude; compare per firm instead of by position
    o = old.set_index("firm")
    n = new.set_index("firm")
    assert set(o.index) == set(n.index)
    for f in o.index:
        assert n.loc[f, "class_moved"] == o.loc[f, "class most moved"]
        assert round(n.loc[f, "shift"] * 100, 2) == o.loc[f, "shift if the firm is dropped (pp)"]
        assert round(n.loc[f, "window_shift"] * 100, 1) == o.loc[f, "largest shift inside one window (pp)"]
        assert n.loc[f, "window"] == o.loc[f, "that window"]
        assert n.loc[f, "window_class"] == o.loc[f, "that class"]
    ref = _csv(reference, "la_firm_leverage").set_index("firm")
    for f in ref.index:
        assert round(n.loc[f, "shift"] * 100, 2) == float(ref.loc[f, "shift if the firm is dropped (pp)"])


def test_share_shift_when_dropped(archive, la, v):
    from src.dataset_facts import sm_open
    old = sm_open.firm_leverage_classes(v)
    lev = la.firm_leverage(v)
    for f in lev["firm"].head(8):
        d = C.share_shift_when_dropped(v["topType"], v["company_canonical"], f)
        sub = old[old["firm"].eq(f)].set_index("class")
        for c in sub.index:
            assert round(float(d[c]) * 100, 2) == sub.loc[c, "shift all years (pp)"]


def test_class_concentration(archive, la, v, reference):
    old = la.class_concentration(v)
    new = C.class_concentration(v["topType"], v["company_canonical"], v["named"])
    assert list(new["class"]) == list(old["class"])
    assert list(new["aircraft"]) == list(old["aircraft"])
    assert list(new["named_firms"]) == list(old["named firms filing in it"])
    assert list(new["largest_firm"]) == list(old["largest firm"])
    for a, b in (("largest_share", "its share of the class"), ("top3_share", "top 3 firms' share"),
                 ("named_share", "share held by named firms")):
        assert np.allclose(new[a].round(2), old[b], **ATOL)
    ref = _csv(reference, "la_class_concentration")
    assert np.allclose(new["largest_share"].round(2), ref["its share of the class"].astype(float), **ATOL)


def test_class_filer_concentration_and_votes(archive, la, v, reference):
    old = la.class_filer_weight(v).set_index("code")
    w = v.dropna(subset=["topType"])
    new = C.class_filer_concentration(w["topType"], w["filer_id"]).set_index("class")
    assert set(new.index) == set(old.index)
    for c in old.index:
        r, o = new.loc[c], old.loc[c]
        assert r["aircraft"] == o["aircraft"] and r["filers"] == o["filers"]
        assert r["its_aircraft"] == o["its aircraft"]
        assert round(r["its_share"], 3) == o["its share"]
        assert round(r["top3_share"], 3) == o["top 3 share"]
        assert round(r["effective_filers"], 1) == o["effective filers"]
        counts = w.loc[w["topType"].eq(c), "filer_id"].value_counts()
        assert np.isclose(C.inverse_hhi(counts), r["effective_filers"], **ATOL)
    votes = C.vote_counts_size_tiebreak(w["topType"], w["filer_id"])
    for c in old.index:
        by_vote = float(votes.get(c, 0)) / float(votes.sum())
        assert round(by_vote, 3) == old.loc[c, "share one vote per filer"]
    ref = _csv(reference, "la_class_filer_weight").set_index("code")
    for c in ref.index:
        assert round(new.loc[c, "effective_filers"], 1) == float(ref.loc[c, "effective filers"])
        assert round(float(votes.get(c, 0)) / float(votes.sum()), 3) == float(ref.loc[c, "share one vote per filer"])


def test_vote_shares_modal(archive, la, v, reference):
    old = la.firm_weighted_shares(v)
    w = v.dropna(subset=["window", "topType"])
    for name in la.WINDOW_NAMES:
        sub = w[w["window"].eq(name)]
        by_filer = C.vote_shares_modal(sub["topType"], sub["filer_id"])
        for t in ["TR", "SLC", "CVT", "MR", "TW"]:
            row = old[(old["window"] == name) & (old["class"] == archive.metrics.ARCH_NAMES.get(t, t))]
            assert round(float(by_filer.get(t, 0)), 3) == row["share by filer"].iloc[0]
    ref = _csv(reference, "la_firm_weighted_shares")
    assert np.allclose(old["share by filer"], ref["share by filer"].astype(float), **ATOL)


def test_top_filer_share(archive, la, v):
    old = la.class_window_filer_weight(v)
    w = v.dropna(subset=["topType", "window"])
    for _, r in old.iterrows():
        sub = w[w["topType"].eq(r["code"]) & w["window"].eq(r["window"])]
        t = C.top_filer_share(sub["filer_id"])
        assert t["aircraft"] == r["aircraft"] and t["filers"] == r["filers"]
        assert t["its_aircraft"] == r["its aircraft"]
        assert round(t["its_share"], 3) == r["its share"]
