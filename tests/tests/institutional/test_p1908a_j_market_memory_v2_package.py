import json
import subprocess
import sys
from pathlib import Path

def test_p1908_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P1908A_J_MARKET_MEMORY_V2_PACKAGE/p1908a_j_market_memory_v2_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P1908A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P1908J_MARKET_MEMORY_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["memory_capacity"] == 1000
    assert data["approved_for_P1909"] is True
