import json
import subprocess
import sys
from pathlib import Path

def test_p2007_real_depth_readiness_audit():
    result = subprocess.run(
        [sys.executable, "_institutional/P2007_REAL_DEPTH_READINESS_AUDIT/real_depth_readiness_audit.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2007/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2007_REAL_DEPTH_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["real_orders"] == "FORBIDDEN"
    assert "NO_REAL_DATA_DOWNLOADED" in data["blockers"]
    assert data["approved_for_P2010"] is True
