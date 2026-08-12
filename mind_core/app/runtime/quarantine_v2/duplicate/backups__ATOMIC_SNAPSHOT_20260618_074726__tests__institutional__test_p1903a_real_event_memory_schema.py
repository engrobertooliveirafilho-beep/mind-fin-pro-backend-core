import json
import subprocess
import sys
from pathlib import Path


def test_p1903a_real_event_memory_schema_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1903A_REAL_EVENT_MEMORY_SCHEMA/real_event_memory_schema.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1903A")
    assert (base / "REAL_EVENT_MEMORY_SCHEMA.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1903A_REAL_EVENT_MEMORY_SCHEMA"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["event_type_count"] >= 10
    assert data["approved_for_P1903B"] is True
