import json
import subprocess
import sys
from pathlib import Path


def test_p1901j_runtime_graph_rebuild_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901J_RUNTIME_GRAPH_REBUILD/runtime_graph_rebuild.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    graph = Path("_evidence/P1901J/RUNTIME_GRAPH_V2.json")
    summary = Path("_evidence/P1901J/SUMMARY.json")

    assert graph.exists()
    assert summary.exists()

    data = json.loads(graph.read_text(encoding="utf-8"))

    assert data["program"] == "P1901J_RUNTIME_GRAPH_REBUILD"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["node_count"] > 0
    assert data["edge_count"] > 0
    assert len(data["nodes"]) == data["node_count"]
    assert len(data["edges"]) == data["edge_count"]
    assert data["approved_for_P1901K"] is True


def test_p1901j_graph_schema_integrity():
    data = json.loads(Path("_evidence/P1901J/RUNTIME_GRAPH_V2.json").read_text(encoding="utf-8"))

    node_required = {
        "id",
        "file",
        "owner_module",
        "category",
        "type",
        "maturity",
        "institutional_score",
        "criticality",
        "runtime_candidate",
        "inbound_degree",
        "outbound_degree",
        "total_degree",
    }

    edge_required = {"source", "target", "type", "weight"}

    for node in data["nodes"]:
        assert node_required.issubset(set(node.keys()))

    for edge in data["edges"]:
        assert edge_required.issubset(set(edge.keys()))
