from app.eldora.core.persistent_social_memory import store_social_memory
from app.eldora.core.emotional_continuity_engine import emotional_continuity
from app.eldora.core.relational_cognition_engine import relational_analysis

def test_social_memory():
    r=store_social_memory("roberto","long term interaction")
    assert r["status"]=="ok"

def test_emotional_continuity():
    r=emotional_continuity("roberto","motivated","project evolution")
    assert r["status"]=="ok"

def test_relational_cognition():
    r=relational_analysis("roberto","strategic visionary")
    assert r["status"]=="ok"
