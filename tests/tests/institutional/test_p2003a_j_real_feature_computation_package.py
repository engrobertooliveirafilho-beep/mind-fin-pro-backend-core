import json
import subprocess
import sys
from pathlib import Path

def test_p2003_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P2003A_J_REAL_FEATURE_COMPUTATION_PACKAGE/real_feature_computation_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2003A_J/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2003J_REAL_FEATURE_COMPUTATION_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["planned_features"] >= 1000
    assert data["features_computed"] == 0
    assert data["write_enabled"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2004"] is True
