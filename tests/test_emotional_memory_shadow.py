from app.companionship.emotional_memory_shadow import build_shadow, attach_shadow

def test_emotional_memory_shadow_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "03_P19P36Q_EMOTIONAL_MEMORY_SHADOW"

def test_emotional_memory_shadow_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36q_emotional_memory_shadow" in ctx
