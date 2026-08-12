import json
import subprocess
import sys
from pathlib import Path

def test_p1906_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P1906A_J_FEATURE_EXPLOSION_ENGINE_PACKAGE/p1906a_j_feature_explosion_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P1906A_J/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1906J_FEATURE_EXPLOSION_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["planned_feature_count"] >= 1000
    assert data["approved_for_P1907"] is True
