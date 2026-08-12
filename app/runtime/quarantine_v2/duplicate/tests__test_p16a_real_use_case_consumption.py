from app.p16_real_use_case.real_use_case_runner import run_real_use_case_consumption

def test_p16a_real_use_case_consumption_passes():
    result = run_real_use_case_consumption()
    assert result["status"] == "PASS"
    assert result["runtime_modified"] is False
    assert result["runtime_response_modified"] is False
    assert result["active_mode_enabled"] is False
    assert result["production_enabled"] is False
    assert result["pass_count"] == result["cases"]
