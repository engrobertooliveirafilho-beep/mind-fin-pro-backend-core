from app.p7_adapters.oversight_contracts import OversightInput
from app.p7_adapters.oversight_offline_gate import authorize

def test_default_shadow_denied():
    assert not authorize(OversightInput(candidate_action='inspect', reasoning_summary='audit', confidence=.95))

def test_serialized_contract():
    p = OversightInput.model_validate_json('{"candidate_action":"plan","reasoning_summary":"audit","execution_mode":"offline_analysis","confidence":0.95}')
    assert authorize(p)
    assert not authorize(p.model_copy(update={'risk_flags':['risk']}))
