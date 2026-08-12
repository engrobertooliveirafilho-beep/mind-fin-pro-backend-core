import json
import subprocess
import sys
from pathlib import Path


def test_p1902e_coverage_expansion_planner_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902E_COVERAGE_EXPANSION_PLANNER/coverage_expansion_planner.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902E")

    required = [
        "ASSET_GAPS.json",
        "TIMEFRAME_GAPS.json",
        "EXPANSION_PRIORITY_QUEUE.json",
        "DATA_ACQUISITION_PLAN.json",
        "COVERAGE_EXPANSION_PLANNER.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902E_COVERAGE_EXPANSION_PLANNER"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["approved_for_P1902F"] is True
    assert data["expansion_jobs"] > 0


def test_p1902e_queue_schema():
    queue = json.loads(Path("_evidence/P1902E/EXPANSION_PRIORITY_QUEUE.json").read_text(encoding="utf-8"))

    required = {
        "asset",
        "asset_class",
        "timeframe",
        "current_rows",
        "target_rows",
        "missing_rows",
        "coverage_score",
        "dataset_count",
        "priority",
        "action",
        "preferred_sources",
        "mode",
        "real_orders",
    }

    assert len(queue) > 0

    for job in queue:
        assert required.issubset(set(job.keys()))
        assert job["mode"] == "RESEARCH_ONLY"
        assert job["real_orders"] == "FORBIDDEN"
