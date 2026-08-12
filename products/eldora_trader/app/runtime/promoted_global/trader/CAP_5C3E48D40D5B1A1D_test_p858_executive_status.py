from pathlib import Path
from mind_trader.app.audits.executive_status import (
    build_executive_status,
    save_executive_status_reports
)

def test_executive_status_structure():
    r=build_executive_status(157)

    assert r["report"]=="P8.58_EXECUTIVE_STATUS_REPORT"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_save_executive_status_reports(tmp_path):
    r=save_executive_status_reports(
        157,
        str(tmp_path/"status.json"),
        str(tmp_path/"status.md")
    )

    assert Path(tmp_path/"status.json").exists()
    assert Path(tmp_path/"status.md").exists()
    assert r["tests_passed"]==157
