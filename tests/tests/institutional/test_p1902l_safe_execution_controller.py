import json
import subprocess
import sys
from pathlib import Path


def test_p1902l_safe_execution_controller_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902L_SAFE_EXECUTION_CONTROLLER/safe_execution_controller.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902L")
    assert (base / "SAFE_EXECUTION_CONTROLLER.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902L_SAFE_EXECUTION_CONTROLLER"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["allow_broker_connection"] is False
    assert data["allow_live_trading"] is False
    assert data["allow_real_orders"] is False
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["download_jobs"] == data["normalization_jobs"]
    assert data["controller_ready"] is True
    assert data["approved_for_P1903"] is True
