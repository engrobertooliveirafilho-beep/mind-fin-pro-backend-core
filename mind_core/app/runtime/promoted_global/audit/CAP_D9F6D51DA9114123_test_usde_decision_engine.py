from app.modules.usde_core.decision_engine import DecisionEngine

def test_decision_engine_blocks_100_percent():
    r = DecisionEngine().decide(
        {"avg_accuracy": 1.0, "red_team_status": "AUDIT_REQUIRED"},
        {"final_scientific_score": 0.95, "overfitting_score": 0.90, "verdict": "STRONG_EVIDENCE"},
        {"baseline": 0.5}
    )
    assert r["scientific_decision"] == "INCONCLUSIVA"
    assert "EXTREME_ACCURACY_90_PLUS_AUDIT_REQUIRED" in r["audit_flags"]

def test_decision_engine_rejects_weak_score():
    r = DecisionEngine().decide(
        {"avg_accuracy": 0.1, "red_team_status": "NO_CRITICAL_FLAGS"},
        {"final_scientific_score": 0.2, "overfitting_score": 0.1, "verdict": "WEAK_OR_INCONCLUSIVE"},
        {"baseline": 0.5}
    )
    assert r["scientific_decision"] in {"INCONCLUSIVA", "HIPOTESE_REJEITADA"}
