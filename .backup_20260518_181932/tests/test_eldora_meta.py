from app.eldora.core.meta_cognition_engine import analyze_internal_state
from app.eldora.core.self_awareness_engine import self_awareness
from app.eldora.core.recursive_introspection_engine import recursive_introspection

def test_meta_cognition():
    r=analyze_internal_state("runtime_active","distributed cognition")
    assert r["status"]=="ok"

def test_self_awareness():
    r=self_awareness("stable","optimize cognition")
    assert r["status"]=="ok"

def test_recursive_introspection():
    r=recursive_introspection("layer_1","runtime self analysis")
    assert r["status"]=="ok"
