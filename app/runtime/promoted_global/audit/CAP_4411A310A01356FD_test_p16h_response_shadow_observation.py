from app.p16_real_use_case.response_shadow_observation import run_response_shadow_observation

def test_p16h_response_shadow_observation_passes(tmp_path):
    log = tmp_path / "p16h_observation.jsonl"
    result = run_response_shadow_observation(str(log), iterations=30)
    assert result["status"] == "PASS"
    assert result["runtime_modified"] is False
    assert result["runtime_response_modified"] is False
    assert result["active_mode_enabled"] is False
    assert result["production_enabled"] is False
    assert result["pass_count"] == result["iterations"]
    assert result["unsafe_count"] == 0
    assert result["leaks"] == 0
    assert result["mutations"] == 0
    assert log.exists()
