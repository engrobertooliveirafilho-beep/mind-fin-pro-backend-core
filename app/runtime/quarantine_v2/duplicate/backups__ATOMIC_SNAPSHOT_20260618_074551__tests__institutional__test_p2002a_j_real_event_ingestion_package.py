import json
import subprocess
import sys
from pathlib import Path

def test_p2002_package():

    result = subprocess.run(
        [sys.executable, "_institutional/P2002A_J_REAL_EVENT_INGESTION_PACKAGE/real_event_ingestion_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P2002A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P2002J_REAL_EVENT_INGESTION_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["event_types"] == 14
    assert data["records_ingested"] == 0
    assert data["download_executed"] is False
    assert data["approved_for_P2003"] is True
