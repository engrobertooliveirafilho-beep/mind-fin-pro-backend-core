from app.companionship.digital_twin_foundation import build_shadow, attach_shadow

def test_digital_twin_foundation_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "08_P19P36V_DIGITAL_TWIN_FOUNDATION"

def test_digital_twin_foundation_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36v_digital_twin_shadow" in ctx
