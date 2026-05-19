from app.training.conversation_maturity_simulator import run
def test_conversation_maturity_simulation_gate():
    r=run(1000)
    assert r["total"] >= 1000
    assert r["identity_fallback_rate"] < 0.01
    assert r["humanization_score"] >= 95
    assert r["passed"] is True
