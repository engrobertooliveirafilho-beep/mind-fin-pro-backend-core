import json
import subprocess
import sys
from pathlib import Path

def test_p1905_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P1905A_J_MULTI_ASSET_EXPANSION_PACKAGE/p1905a_j_multi_asset_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P1905A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P1905J_MULTI_ASSET_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["asset_count"] == 21
    assert data["approved_for_P1906"] is True
