from app.companionship.production_safety_gate import evaluate_production_safety

def test_production_gate_default_blocked(monkeypatch):
    monkeypatch.delenv("P19P36_ENABLE_PRODUCTION_COGNITION", raising=False)
    out=evaluate_production_safety({})
    assert out["enabled"] is False
    assert out["default_safe"] is True
