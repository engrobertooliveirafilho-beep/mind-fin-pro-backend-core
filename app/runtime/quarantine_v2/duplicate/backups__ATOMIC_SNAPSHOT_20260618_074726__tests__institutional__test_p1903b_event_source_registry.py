import json
import subprocess
import sys
from pathlib import Path


def test_p1903b_event_source_registry_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1903B_EVENT_SOURCE_REGISTRY/event_source_registry.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1903B")
    assert (base / "EVENT_SOURCE_REGISTRY.json").exists()
    assert (base / "SUMMARY.json").exists()

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1903B_EVENT_SOURCE_REGISTRY"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["event_type_count"] >= 10
    assert data["source_count"] > 0
    assert data["approved_for_P1903C"] is True
