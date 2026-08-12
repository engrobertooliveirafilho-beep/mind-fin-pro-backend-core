import json
import subprocess
import sys
from pathlib import Path


def test_p1903d_j_package_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1903D_J_REAL_EVENT_MEMORY_PACKAGE/p1903d_j_event_memory_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1903D_J")
    required = [
        "P1903D_EVENT_CANONICAL_LEDGER.json",
        "P1903E_EVENT_MEMORY_STORAGE.json",
        "P1903F_EVENT_LINK_ENGINE.json",
        "P1903G_EVENT_RETRIEVAL_ENGINE.json",
        "P1903H_EVENT_SIMILARITY_ENGINE.json",
        "P1903I_EVENT_GRAPH.json",
        "P1903J_EVENT_READINESS_AUDIT.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1903J_EVENT_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["external_ingestion_executed"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P1904"] is True
    assert data["events"] == 14
