from app.companionship.canary_runtime_validation import validate_canary_context

def test_canary_validation():
    out=validate_canary_context({"p19p36k_memory_shadow":{}, "p19p36l_memory_fusion_shadow":{}, "p19p36m_memory_fusion_advisor_shadow":{}})
    assert out["canary_pass"] is True
