import json
import subprocess
import sys
from pathlib import Path

def test_p2001c_connector_detail_audit():
    result = subprocess.run(
        [sys.executable, "_institutional/P2001C_CONNECTOR_DETAIL_AUDIT/connector_detail_audit.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2001C/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2001C_CONNECTOR_DETAIL_AUDIT"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001D"] is True
