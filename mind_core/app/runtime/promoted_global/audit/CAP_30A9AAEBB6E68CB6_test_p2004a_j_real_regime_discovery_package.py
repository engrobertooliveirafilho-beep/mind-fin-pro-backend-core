import json
import subprocess
import sys
from pathlib import Path

def test_p2004_package():

    result = subprocess.run(
        [sys.executable, "_institutional/P2004A_J_REAL_REGIME_DISCOVERY_PACKAGE/real_regime_discovery_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P2004A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P2004J_REAL_REGIME_DISCOVERY_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["clustering_engines"] == 5
    assert data["regime_targets"] == 10
    assert data["clustering_executed"] is False
    assert data["regimes_discovered"] == 0
    assert data["approved_for_P2005"] is True
