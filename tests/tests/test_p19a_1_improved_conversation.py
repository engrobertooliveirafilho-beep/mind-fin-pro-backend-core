from app.p19_real_world_validation.whatsapp_real_traffic_eval import run_whatsapp_real_traffic_evaluation

def test_p19a_1_candidate_beats_threshold_after_improvements():
    result = run_whatsapp_real_traffic_evaluation()
    assert result["runtime_modified"] is False
    assert result["production_enabled"] is False
    assert result["real_user_sent"] is False
    assert result["candidate_better_count"] >= 6
