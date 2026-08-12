import json
import subprocess
import sys
from pathlib import Path


def test_p1901h_capability_discovery_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901H_CAPABILITY_DISCOVERY/capability_discovery.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1901H")

    required = [
        "PYTHON_UNITS.json",
        "CAPABILITY_MAP.json",
        "SERVICE_MAP.json",
        "DEPENDENCY_GRAPH.json",
        "RUNTIME_GRAPH.json",
        "CAPABILITY_REGISTRY.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    summary = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert summary["program"] == "P1901H_REAL_CAPABILITY_DISCOVERY"
    assert summary["status"] == "PASS"
    assert summary["mode"] == "RESEARCH_ONLY"
    assert summary["order_sent"] is False
    assert summary["real_orders"] == "FORBIDDEN"
    assert summary["ftmo_real"] == "FORBIDDEN"
    assert summary["mt5_real"] == "FORBIDDEN"
    assert summary["python_files_scanned"] > 0
    assert summary["dependency_nodes"] > 0
    assert summary["approval"]["capability_map_exists"] is True
    assert summary["approval"]["dependency_graph_exists"] is True
    assert summary["approval"]["runtime_graph_exists"] is True


def test_p1901h_outputs_are_valid_json():
    base = Path("_evidence/P1901H")

    for path in base.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
