import json
import subprocess
import sys
from pathlib import Path


def test_p1903c_event_ingestion_plan_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1903C_EVENT_INGESTION_PLAN/event_ingestion_plan.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1903C")
    required = [
        "EVENT_INGESTION_PLAN.json",
        "EVENT_WINDOWS.json",
        "EVENT_SCHEDULES.json",
        "EVENT_PRIORITY_QUEUE.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1903C_EVENT_INGESTION_PLAN"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["event_types"] == 14
    assert data["approved_for_P1903D"] is True
