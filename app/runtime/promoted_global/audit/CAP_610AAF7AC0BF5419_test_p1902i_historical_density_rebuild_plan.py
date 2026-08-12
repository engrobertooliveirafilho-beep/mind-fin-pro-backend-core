import json
import subprocess
import sys
from pathlib import Path


def test_p1902i_historical_density_rebuild_plan_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902I_HISTORICAL_DENSITY_REBUILD_PLAN/historical_density_rebuild_plan.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902I")
    assert (base / "HISTORICAL_DENSITY_REBUILD_PLAN.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902I_HISTORICAL_DENSITY_REBUILD_PLAN"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["rebuild_job_count"] > 0
    assert data["approved_for_P1902J"] is True
