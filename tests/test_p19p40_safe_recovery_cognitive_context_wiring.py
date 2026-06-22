from app.companionship.safe_recovery_adapter import attach_p19p40_cognitive_context_shadow


def test_p19p40_safe_recovery_adapter_attaches_cognitive_context_shadow_only():
    ctx = {
        "existing": "preserved",
        "p19p36o_relationship_memory_shadow": {"relationship": "known"},
        "p19p36p_goal_tracker_shadow": {"goal": "study"},
    }

    result = attach_p19p40_cognitive_context_shadow(ctx, user_id="u1")

    assert result["existing"] == "preserved"
    assert "cognitive_context" in result
    assert "p19p40_cognitive_context_shadow_telemetry" in result

    telemetry = result["p19p40_cognitive_context_shadow_telemetry"]

    assert telemetry["program"] == "P19P40"
    assert telemetry["mode"] == "SHADOW_ONLY"
    assert telemetry["adapter"] == "safe_recovery_adapter"
    assert telemetry["context_attached"] is True
    assert telemetry["runtime_mutation"] is False
    assert telemetry["response_mutation"] is False
    assert telemetry["rollbackable"] is True


def test_p19p40_safe_recovery_adapter_does_not_mutate_original_context():
    ctx = {"existing": True}

    result = attach_p19p40_cognitive_context_shadow(ctx, user_id="u2")

    assert ctx == {"existing": True}
    assert result is not ctx
    assert "cognitive_context" in result
