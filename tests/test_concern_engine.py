from app.companionship.concern_engine import build_shadow, attach_shadow

def test_concern_engine_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "05_P19P36S_CONCERN_ENGINE"

def test_concern_engine_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36s_concern_shadow" in ctx
