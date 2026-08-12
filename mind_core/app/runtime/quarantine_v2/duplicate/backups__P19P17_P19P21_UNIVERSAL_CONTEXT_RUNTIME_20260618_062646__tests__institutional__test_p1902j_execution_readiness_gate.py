import json
import subprocess
import sys
from pathlib import Path


def test_p1902j_execution_readiness_gate_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902J_EXECUTION_READINESS_GATE/execution_readiness_gate.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902J")
    assert (base / "EXECUTION_READINESS_GATE.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902J_EXECUTION_READINESS_GATE"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_jobs"] == data["normalization_jobs"]
    assert data["consistent"] is True
    assert data["approved_for_P1902K"] is True
