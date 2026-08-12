from pathlib import Path
from app.p10_real_data_research_certification.engine import certify

def test_p106_certification_snapshot():
    s=certify()["P10_STATE_SNAPSHOT"]
    assert s["STATUS"]=="P10_REAL_DATA_RESEARCH_CERTIFIED"
    assert s["LIVE"]=="FORBIDDEN"
    assert s["REAL_BROKER"]=="DISABLED"
    assert s["EDGE"]=="NOT_PROVEN"
    assert s["EXPORT_READY"] is True

def test_p106_reports_written():
    certify()
    assert Path("reports/P10.6_REAL_DATA_RESEARCH_CERTIFICATION/P10_STATE_SNAPSHOT.json").exists()
    assert Path("reports/P10.6_REAL_DATA_RESEARCH_CERTIFICATION/P10.6_manifest.json").exists()

def test_p106_next_phase():
    s=certify()["P10_STATE_SNAPSHOT"]
    assert s["NEXT_PHASE"]=="P11_SCALE_REAL_DATA_AND_EDGE_EVIDENCE"
