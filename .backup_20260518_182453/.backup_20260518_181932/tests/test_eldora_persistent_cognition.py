from app.eldora.core.persistent_cognitive_graph import store_persistent_memory, retrieve_persistent_memory, cognitive_store_report

def test_persistent_cognitive_store():
    r = store_persistent_memory("eldora pgvector memory", priority=5)
    assert r["stored"] is True

def test_persistent_cognitive_retrieve():
    store_persistent_memory("adaptive retrieval ranking", priority=10)
    r = retrieve_persistent_memory("retrieval")
    assert r["status"] == "ok"
    assert len(r["results"]) >= 1

def test_cognitive_store_report():
    assert cognitive_store_report()["status"] == "ok"
