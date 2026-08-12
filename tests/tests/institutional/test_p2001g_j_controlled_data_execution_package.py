import json
import subprocess
import sys
from pathlib import Path

def test_p2001g_j_package():

    result = subprocess.run(
        [sys.executable, "_institutional/P2001G_J_CONTROLLED_DATA_EXECUTION_PACKAGE/controlled_data_execution_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P2001G_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P2001J_CONTROLLED_DATA_EXECUTION_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_execution_performed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2002"] is True
