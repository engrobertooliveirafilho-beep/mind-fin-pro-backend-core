from app.companionship.emotional_continuity_engine import build_shadow, attach_shadow

def test_emotional_continuity_engine_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "04_P19P36R_EMOTIONAL_CONTINUITY_ENGINE"

def test_emotional_continuity_engine_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36r_emotional_continuity_shadow" in ctx
