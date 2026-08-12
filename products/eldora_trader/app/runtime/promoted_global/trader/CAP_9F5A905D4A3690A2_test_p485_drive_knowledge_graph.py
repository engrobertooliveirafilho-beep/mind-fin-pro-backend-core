import json
from pathlib import Path

def test_p485_drive_knowledge_graph_exists_and_links_core_entities():
    p = Path("runtime/knowledge_graph/drive_knowledge_graph.json")
    assert p.exists()

    graph = json.loads(p.read_text(encoding="utf-8"))

    assert graph["milestone"] == "P4.85 COMPLETE"
    assert graph["graph"] == "DRIVE_KNOWLEDGE_GRAPH"
    assert graph["nodes_count"] >= 5
    assert graph["edges_count"] >= 5

    node_types = set(graph["node_types"])
    assert "PROJECT" in node_types
    assert "DOCUMENT" in node_types

    edge_types = set(graph["edge_types"])
    assert "HAS_DOCUMENT" in edge_types
