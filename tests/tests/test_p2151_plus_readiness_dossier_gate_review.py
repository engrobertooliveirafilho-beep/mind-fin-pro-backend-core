from app.runtime.p2151_plus_readiness_dossier_gate_review import run_p2151_plus, enforce

def test_p2151_plus_readiness(tmp_path):
    r = run_p2151_plus(str(tmp_path))
    assert r["status"] == "PASS"
    assert r["readiness"] == "PAPER_ONLY_SIMULATION_REVIEW_READY"
    assert r["gate_review"]["deployment_decision"] == "APPROVED_FOR_PAPER_ONLY_SIMULATION_REVIEW"
    assert r["gate_review"]["real_execution_decision"] == "FORBIDDEN"
    assert r["absolute_restrictions"]["REAL_ORDERS"] == "FORBIDDEN"
    assert r["absolute_restrictions"]["BROKER_EXECUTION"] == "DISABLED"
    assert r["absolute_restrictions"]["FINANCIAL_EXECUTION"] == "DISABLED"

def test_p2151_plus_locks():
    locks = enforce()
    assert locks["MIND_MODE"] == "PAPER_ONLY"
    assert locks["SEND_ORDER"] == "BLOCKED"
    assert locks["MT5_ORDER_SEND"] == "BLOCKED"
