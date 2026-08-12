import json
import subprocess
import sys
from pathlib import Path

def test_p2006_package():

    result = subprocess.run(
        [sys.executable, "_institutional/P2006A_J_REAL_SPECIALIST_EVOLUTION_PACKAGE/real_specialist_evolution_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P2006A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P2006J_REAL_SPECIALIST_EVOLUTION_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["target_generated_specialists"] == 10000
    assert data["target_survivors"] == 1000
    assert data["target_certified"] == 100
    assert data["generated_specialists"] == 0
    assert data["certified_specialists"] == 0
    assert data["execution_enabled"] is False
    assert data["approved_for_P2007"] is True
