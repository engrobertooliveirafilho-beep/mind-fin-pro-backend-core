from app.p8_shadow.planner_sandbox import run_limited_active_sandbox

def test_p8_19_sandbox_preserves_runtime_authority():
    result = run_limited_active_sandbox({"goal": "controlled sandbox review"})
    assert result["status"] == "PASS"
    assert result["runtime_modified"] is False
    assert result["response_modified"] is False
    assert result["state_modified"] is False
    assert result["routes_modified"] is False
    assert result["dispatcher_modified"] is False
    assert result["active_mode_enabled"] is False
    assert result["block_mode_enabled"] is False
    assert result["runtime_authority_preserved"] is True
    assert result["plan"]["depth"] >= 3
    assert result["plan"]["step_count"] >= 5
