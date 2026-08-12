from app.modules.usde_core.evidence_engine import EvidenceEngine

def test_evidence_engine_score():
    e = EvidenceEngine().score(
        {"avg_accuracy": 0.55, "red_team_status": "NO_CRITICAL_FLAGS"},
        metadata={"sample_size": 100, "baseline": 0.50, "seed": 42}
    )
    assert 0 <= e["final_scientific_score"] <= 1
    assert e["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
