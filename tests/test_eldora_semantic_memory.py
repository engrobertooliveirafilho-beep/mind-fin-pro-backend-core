import os
import pytest

from app.eldora.core.semantic_memory_engine import store_memory, retrieve_memory, semantic_graph_report


pytestmark = pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL required for real pgvector semantic memory")


def test_store_memory():
    r = store_memory("eldora semantic memory", {"node": "knowledge", "sender_id": "pytest_semantic"})
    assert r["stored"] is True
    assert r["source"] == "pgvector" if "source" in r else True


def test_retrieve_memory():
    store_memory("jwt authentication runtime", {"node": "security", "sender_id": "pytest_semantic"})
    result = retrieve_memory("authentication")
    assert result["status"] == "ok"
    assert len(result["results"]) >= 1


def test_graph_report():
    report = semantic_graph_report()
    assert report["status"] == "ok"
    assert report["source"] == "pgvector"
