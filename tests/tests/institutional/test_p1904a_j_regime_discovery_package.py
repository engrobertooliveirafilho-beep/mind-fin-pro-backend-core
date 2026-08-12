import json
import subprocess
import sys
from pathlib import Path

def test_p1904a_j_package_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1904A_J_REGIME_DISCOVERY_ENGINE_PACKAGE/p1904a_j_regime_discovery_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1904A_J")
    required = [
        "P1904A_REGIME_SCHEMA.json",
        "P1904B_REGIME_FEATURE_MAP.json",
        "P1904C_REGIME_CLUSTER_PLAN.json",
        "P1904D_REGIME_TRANSITION_MATRIX.json",
        "P1904E_REGIME_MEMORY.json",
        "P1904F_REGIME_RETRIEVAL.json",
        "P1904G_REGIME_SIMILARITY.json",
        "P1904H_REGIME_GRAPH.json",
        "P1904I_REGIME_COVERAGE_AUDIT.json",
        "P1904J_REGIME_READINESS_AUDIT.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1904J_REGIME_READINESS_AUDIT"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["real_orders"] == "FORBIDDEN"
    assert data["regime_count"] == 10
    assert data["feature_count"] == 10
    assert data["manual_labels_allowed"] is False
    assert data["clustering_executed"] is False
    assert data["approved_for_P1905"] is True
