import json
import subprocess
import sys
from pathlib import Path

def test_p2001f_manual_download_unlock_gate():

    result = subprocess.run(
        [sys.executable, "_institutional/P2001F_MANUAL_DOWNLOAD_UNLOCK_GATE/manual_download_unlock_gate.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P2001F/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P2001F_MANUAL_DOWNLOAD_UNLOCK_GATE"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["default_state"] == "LOCKED"
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001G"] is True
