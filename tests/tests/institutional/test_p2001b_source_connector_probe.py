import json
import subprocess
import sys
from pathlib import Path

def test_p2001b_source_connector_probe():
    result = subprocess.run(
        [sys.executable, "_institutional/P2001B_SOURCE_CONNECTOR_PROBE/source_connector_probe.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2001B/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2001B_SOURCE_CONNECTOR_PROBE"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001C"] is True
