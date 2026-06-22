from app.companionship.human_depth_layer import build_shadow, attach_shadow

def test_human_depth_layer_builds_shadow():
    out=build_shadow({}, text="quero melhorar mas estou com dor", sender="u")
    assert out["mode"] == "SHADOW_ONLY"
    assert out["response_impact"] == "NONE"
    assert out["version"] == "06_P19P36T_HUMAN_DEPTH_LAYER"

def test_human_depth_layer_attaches_shadow():
    ctx=attach_shadow({}, sender="u", text="quero melhorar")
    assert "p19p36t_human_depth_shadow" in ctx
