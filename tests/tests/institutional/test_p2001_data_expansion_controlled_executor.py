import json
import subprocess
import sys
from pathlib import Path

def test_p2001_data_expansion_controlled_executor():
    result = subprocess.run(
        [sys.executable, "_institutional/P2001_DATA_EXPANSION_CONTROLLED_EXECUTOR/data_expansion_controlled_executor.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2001/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2001_DATA_EXPANSION_CONTROLLED_EXECUTOR"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["allow_data_download"] is False
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001B"] is True
