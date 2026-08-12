import json
import subprocess
import sys
from pathlib import Path

def test_p1909_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P1909A_J_SPECIALIST_EVOLUTION_V2_PACKAGE/p1909a_j_specialist_evolution_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(
        Path("_evidence/P1909A_J/SUMMARY.json").read_text(encoding="utf-8")
    )

    assert data["program"] == "P1909J_SPECIALIST_EVOLUTION_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["planned_specialists"] == 1000
    assert data["mutation_jobs"] == 1000
    assert data["crossover_jobs"] == 1000
    assert data["approved_for_P1910"] is True
    assert data["real_orders"] == "FORBIDDEN"
