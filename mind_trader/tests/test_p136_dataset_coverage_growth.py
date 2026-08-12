from pathlib import Path
from app.p136_dataset_coverage_growth.engine import run

def test_p136_report():
    r=run()
    assert r["STATUS"]=="P13.6_DATASET_COVERAGE_GROWTH_IMPLEMENTED"

def test_p136_export_ready():
    r=run()
    assert r["EXPORT_READY"] is True

def test_p136_file():
    run()
    assert Path("reports/P13.6_DATASET_COVERAGE_GROWTH/coverage_growth.json").exists()
