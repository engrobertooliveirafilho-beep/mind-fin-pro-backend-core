from app.companionship.humanized_meta_cognition import (
    build_p19p49_humanized_meta_cognition_stack,
)


def test_p19p49_builds_full_humanized_meta_cognition_stack():
    result = build_p19p49_humanized_meta_cognition_stack(
        interactions=["prossiga", "como faço?", "ok"],
        confirmations=["funcionou"],
        ruptures=[],
        repairs=["corrigido"],
        continuity_events=["voltou ao mesmo projeto"],
        dependency_signals=["pede continuidade"],
        autonomy_signals=["decide prioridade"],
        message_count=120,
        people=["Roberto", "Eldora"],
        roles={"Roberto": "owner", "Eldora": "companion"},
        organizations=["MIND"],
        social_contexts=["runtime", "whatsapp"],
        life_events=[{"date": "2026-06-22", "type": "project", "summary": "P19P48 aprovado", "importance": 1.0}],
        previous_preferences={"style": "direct"},
        current_preferences={"style": "direct", "depth": "high"},
        identity_snapshots=[{"role": "builder"}, {"role": "builder"}],
        historical_threads=["Eldora cognition stack P19P39 P19P48"],
        current_message="continuar Eldora cognition stack",
        mood_events=[{"mood": "positive", "source": "progress"}],
        reasoning_trace=["observe", "rank", "decide"],
        confidence=0.9,
        uncertainty=0.1,
        draft="old",
        critique="needs depth",
        revised="new improved",
        observations=["user wants deeper humanization"],
        beliefs={"state": "shadow"},
        evidence={"state": "shadow"},
        claims=[{"key": "mode", "value": "shadow"}, {"key": "mode", "value": "shadow"}],
        outcomes=["canary passed"],
        feedback=["continue"],
        known_topics=["runtime", "memory"],
        requested_topics=["runtime", "memory", "attachment"],
        long_goals=["controlled production promotion"],
        constraints=["feature flags disabled"],
        timeline=["next phase"],
    )

    stack = result["humanized_meta_cognition"]

    assert result["program"] == "P19P49"
    assert result["mode"] == "SHADOW_ONLY"

    required = [
        "trust_evolution",
        "attachment_modeling",
        "relationship_stage_modeling",
        "social_context_graph",
        "life_event_timeline",
        "preference_drift_tracking",
        "longitudinal_identity_modeling",
        "conversation_recovery_across_months",
        "user_mood_trajectory",
        "relationship_health_scoring",
        "meta_cognition",
        "self_correction_loop",
        "hypothesis_engine",
        "belief_revision_engine",
        "contradiction_resolution",
        "autonomous_learning_loop",
        "knowledge_gap_discovery",
        "long_horizon_planning",
    ]

    for key in required:
        assert key in stack

    assert result["safety"]["runtime_mutation"] is False
    assert result["safety"]["response_mutation"] is False
    assert result["safety"]["outbound_text_mutation"] is False
    assert result["safety"]["shadow_only"] is True
    assert result["safety"]["rollbackable"] is True


def test_p19p49_empty_inputs_return_valid_shadow_contract():
    result = build_p19p49_humanized_meta_cognition_stack()

    assert result["program"] == "P19P49"
    assert result["mode"] == "SHADOW_ONLY"
    assert result["safety"]["production_promotion"] == "NOT_YET"
    assert result["humanized_meta_cognition"]["relationship_health_scoring"]["relationship_health_score"] >= 0
