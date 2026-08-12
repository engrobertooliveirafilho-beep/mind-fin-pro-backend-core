from app.p8_shadow.planner_active_policy import (
    load_planner_active_policy,
    evaluate_planner_active_candidate,
)

def test_p8_12_policy_is_dry_run_only():
    policy = load_planner_active_policy()
    assert policy.enabled is False
    assert policy.mode == "LIMITED_ACTIVE_DRY_RUN"
    assert policy.may_modify_response is False
    assert policy.may_modify_runtime_state is False
    assert policy.may_route is False
    assert policy.may_call_external_tools is False

def test_p8_12_candidate_preserves_runtime_authority():
    result = evaluate_planner_active_candidate({"plan": ["a", "b"]})
    assert result["status"] == "PASS"
    assert result["active_enabled"] is False
    assert result["runtime_authority_preserved"] is True
    assert result["may_modify_response"] is False
    assert result["may_modify_runtime_state"] is False
