from app.p17_value_proof.eldora_value_proof import run_eldora_value_proof

def test_p17_eldora_value_proof_runs():
    result = run_eldora_value_proof()
    assert result["cases"] == 20
    assert result["runtime_modified"] is False
    assert result["production_enabled"] is False
    assert result["real_user_sent"] is False
    assert result["avg_planner_score"] > result["avg_baseline_score"]
    assert result["avg_gain_pct"] > 0
