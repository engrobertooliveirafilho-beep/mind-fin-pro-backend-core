from app.eldora.core.long_term_memory import store_cognitive_memory
from app.eldora.core.memory_compression_engine import compress_memory
from app.eldora.core.tool_learning_engine import learn_tool

def test_long_term_memory():
    r = store_cognitive_memory("eldora persistent cognition")
    assert r["stored"] is True

def test_memory_compression():
    r = compress_memory("eldora runtime semantic compression engine validation")
    assert r["status"] == "ok"

def test_tool_learning():
    r = learn_tool("supabase", "persistent_memory")
    assert r["status"] == "ok"
