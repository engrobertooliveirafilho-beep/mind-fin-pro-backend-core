from app.companionship.companion_cognition_stack import build_shadow, attach_shadow

def test_companion_cognition_stack_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "07_P19P36U_COMPANION_COGNITION_STACK"

def test_companion_cognition_stack_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36u_companion_cognition_shadow" in ctx
