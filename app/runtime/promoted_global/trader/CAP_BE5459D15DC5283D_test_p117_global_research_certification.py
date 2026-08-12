from pathlib import Path
from app.p11_global_research_certification.engine import certify

def test_p117_certification_snapshot():
    s=certify()["P11_STATE_SNAPSHOT"]
    assert s["STATUS"]=="P11_GLOBAL_RESEARCH_CERTIFIED"
    assert s["LIVE"]=="FORBIDDEN"
    assert s["REAL_BROKER"]=="DISABLED"
    assert s["EDGE"]=="NOT_PROVEN"
    assert s["EXPORT_READY"] is True

def test_p117_reports_written():
    certify()
    assert Path("reports/P11.7_GLOBAL_RESEARCH_CERTIFICATION/P11_STATE_SNAPSHOT.json").exists()
    assert Path("reports/P11.7_GLOBAL_RESEARCH_CERTIFICATION/P11.7_manifest.json").exists()

def test_p117_next_phase():
    s=certify()["P11_STATE_SNAPSHOT"]
    assert s["NEXT_PHASE"]=="P12_REAL_DATA_LOADING_AND_CLOUD_EXPORT"
