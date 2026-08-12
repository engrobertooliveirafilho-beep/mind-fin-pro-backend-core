from app.companionship.self_reflection_engine import build_self_reflection

def test_self_reflection_unknowns():
    out=build_self_reflection({})
    assert out["confidence"] == "LOW"
    assert "digital_twin_profile" in out["unknown"]

def test_self_reflection_knowns():
    out=build_self_reflection({"p19p37a_digital_twin_real_shadow":{}, "p19p37d_long_term_memory_real_shadow":{}, "p19p37c_emotional_continuity_real_shadow":{}})
    assert out["confidence"] == "HIGH"
