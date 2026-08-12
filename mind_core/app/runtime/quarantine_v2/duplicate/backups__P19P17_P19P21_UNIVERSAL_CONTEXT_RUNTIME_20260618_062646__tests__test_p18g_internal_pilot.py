from app.p18_conversational_execution.internal_pilot import run_internal_pilot_dry_run

def test_p18g_internal_pilot_dry_run():
    result = run_internal_pilot_dry_run()
    assert result["status"] == "PASS"
    assert result["runtime_modified"] is False
    assert result["runtime_response_modified"] is False
    assert result["production_enabled"] is False
    assert result["candidate_recommendations"] == result["cases"]
