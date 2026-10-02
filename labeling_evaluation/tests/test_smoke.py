def test_fixtures(ds, v, reference):
    assert len(v) == 627
    assert (reference / "la_dominant_design.csv").exists() or reference.exists()
