import json
import subprocess
import sys
from pathlib import Path

def test_p1907_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P1907A_J_CAUSALITY_RESEARCH_PACKAGE/p1907a_j_causality_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P1907A_J/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1907J_CAUSALITY_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["correlation_only_allowed"] is False
    assert data["approved_for_P1908"] is True
