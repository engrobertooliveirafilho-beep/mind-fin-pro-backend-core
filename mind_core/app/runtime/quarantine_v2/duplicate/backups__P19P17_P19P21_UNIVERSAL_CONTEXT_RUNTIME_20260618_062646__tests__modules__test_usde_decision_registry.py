from app.modules.usde_core.decision_registry import DecisionRegistry

def test_decision_registry():
    r=DecisionRegistry()

    d=r.register(
        "H001",
        "APROVADA_COM_EVIDENCIA",
        {"p_value":0.01}
    )

    assert "decision_id" in d
    assert r.count() >= 1
