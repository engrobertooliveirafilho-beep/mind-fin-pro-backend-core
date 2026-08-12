import json
import subprocess
import sys
from pathlib import Path


def test_p1902k_dry_run_execution_simulator_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902K_DRY_RUN_EXECUTION_SIMULATOR/dry_run_execution_simulator.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902K")
    assert (base / "DRY_RUN_EXECUTION_SIMULATOR.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902K_DRY_RUN_EXECUTION_SIMULATOR"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P1902L"] is True
