from app.modules.usde_core.red_team_engine import RedTeamEngine

def test_red_team_blocks_temporal_leakage():
    r = RedTeamEngine().audit(
        {"avg_accuracy": 0.95},
        {"overfitting_score": 0.8, "final_scientific_score": 0.9},
        {"sample_size": 100, "baseline": 0.5, "uses_future": True}
    )
    assert r["status"] == "BLOCKED"
    assert "TEMPORAL_LEAKAGE_DETECTED" in r["flags"]

def test_red_team_clear_normal_case():
    r = RedTeamEngine().audit(
        {"avg_accuracy": 0.55},
        {"overfitting_score": 0.2, "final_scientific_score": 0.6},
        {"sample_size": 200, "baseline": 0.5}
    )
    assert r["status"] == "CLEAR"
