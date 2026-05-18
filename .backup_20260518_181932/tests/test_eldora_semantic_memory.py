from app.eldora.core.semantic_memory_engine import (
    store_memory,
    retrieve_memory,
    semantic_graph_report
)

def test_store_memory():
    r = store_memory("eldora semantic memory", {"node": "knowledge"})
    assert r["stored"] is True

def test_retrieve_memory():
    store_memory("jwt authentication runtime", {"node": "security"})
    result = retrieve_memory("authentication")
    assert result["status"] == "ok"
    assert len(result["results"]) >= 1

def test_graph_report():
    report = semantic_graph_report()
    assert report["status"] == "ok"
