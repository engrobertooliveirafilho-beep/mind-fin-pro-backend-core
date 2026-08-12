import json
import subprocess
import sys
from pathlib import Path

def test_p2000_real_depth_program():
    result = subprocess.run(
        [sys.executable, "_institutional/P2000_REAL_DEPTH_PROGRAM/p2000_real_depth_program.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2000/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2000_REAL_DEPTH_PROGRAM"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["real_orders"] == "FORBIDDEN"
    assert data["mission_count"] == 6
    assert data["approved_for_P2001"] is True
