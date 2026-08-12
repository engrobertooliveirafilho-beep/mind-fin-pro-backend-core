from app.p11_data_coverage_engine.engine import build_coverage_matrix, coverage_summary, run

def test_p114_matrix_has_all_timeframes():
    m=build_coverage_matrix()
    tfs={x["timeframe"] for x in m}
    assert {"TICK","M1","M5","M15","M30","H1","H4","D1"} <= tfs

def test_p114_summary_starts_missing_without_real_data():
    s=coverage_summary(build_coverage_matrix())
    assert s["total_slots"] > 0
    assert s["missing"] == s["total_slots"]
    assert s["certified"] == 0

def test_p114_manifest():
    m=run()
    assert m["STATUS"]=="P11.4_DATA_COVERAGE_ENGINE_IMPLEMENTED"
    assert m["EXPORT_READY"] is True
