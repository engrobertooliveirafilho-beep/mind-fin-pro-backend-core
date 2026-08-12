from pathlib import Path
from app.p13_dataset_certification_automation.engine import certify_ingested_files, run

def test_p134_certification_returns_list():
    r=certify_ingested_files()
    assert isinstance(r,list)

def test_p134_manifest_blocks_live():
    m=run()
    assert m["STATUS"]=="P13.4_DATASET_CERTIFICATION_AUTOMATION_IMPLEMENTED"
    assert m["LIVE"]=="FORBIDDEN"
    assert m["REAL_BROKER"]=="DISABLED"

def test_p134_report_written():
    run()
    assert Path("reports/P13.4_DATASET_CERTIFICATION_AUTOMATION/P13.4_manifest.json").exists()
