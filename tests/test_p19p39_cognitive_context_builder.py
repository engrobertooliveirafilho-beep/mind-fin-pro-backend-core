from app.companionship.cognitive_context_builder import (
    build_cognitive_context,
    attach_cognitive_context_shadow,
)


def test_p19p39_builds_shadow_cognitive_context_without_runtime_mutation():
    result = build_cognitive_context(
        user_id="u1",
        relationship_memory={"trust": 0.9},
        goal_tracking={"active_goals": 2},
        digital_twin={"profile_confidence": 0.8},
        behavior_modeling={"pattern": "short_followup"},
        emotional_continuity={"tone": "stable"},
        long_term_memory={"items": 3},
        self_reflection={"quality": 0.95},
        live_cognition={"decision": "observe"},
        source_context={"existing": True},
        feature_flags={},
    )

    cc = result["cognitive_context"]

    assert cc["mode"] == "SHADOW_ONLY"
    assert cc["safety"]["default_enabled"] is False
    assert cc["safety"]["production_response_impact"] == "none"
    assert cc["telemetry"]["runtime_mutation"] is False
    assert cc["telemetry"]["response_mutation"] is False
    assert cc["relationship_memory"]["status"] == "ok"
    assert cc["goal_tracking"]["status"] == "ok"
    assert cc["digital_twin"]["status"] == "ok"
    assert cc["live_cognition"]["status"] == "ok"


def test_p19p39_attach_cognitive_context_shadow_preserves_existing_context():
    original = {
        "existing": "preserved",
        "p19p36o_relationship_memory_shadow": {"known": True},
        "p19p36p_goal_tracker_shadow": {"goal": "study"},
    }

    result = attach_cognitive_context_shadow(original, user_id="u2")

    assert result["existing"] == "preserved"
    assert "cognitive_context" in result
    assert result["cognitive_context"]["relationship_memory"]["data"]["known"] is True
    assert result["cognitive_context"]["goal_tracking"]["data"]["goal"] == "study"
    assert original.get("cognitive_context") is None
