from app.p9_final_certification.engine import certify

def test_p9100_certification_snapshot():
    s=certify()["P9_STATE_SNAPSHOT"]
    assert s["STATUS"]=="P9_EDGE_DISCOVERY_AT_SCALE_CERTIFIED"
    assert s["LIVE"]=="FORBIDDEN"
    assert s["REAL_BROKER"]=="DISABLED"
    assert s["EDGE"]=="NOT_PROVEN"
    assert s["EXPORT_READY"] is True

def test_p9100_reports_exist():
    from pathlib import Path
    certify()
    assert Path("reports/P9.100_FINAL_CERTIFICATION/P9_STATE_SNAPSHOT.json").exists()
    assert Path("reports/P9.100_FINAL_CERTIFICATION/P9.100_final_certification.json").exists

def test_p9100_next_phase():
    s=certify()["P9_STATE_SNAPSHOT"]
    assert s["NEXT_PHASE"]=="P10_REAL_DATA_INGESTION_AND_DISTRIBUTED_SCALE"
