from app.companionship.behavior_modeling import (
    build_p19p44_behavior_modeling_evolution,
)


def test_p19p44_behavior_modeling_evolution_builds_patterns():
    result = build_p19p44_behavior_modeling_evolution(
        interactions=["prossiga", "como faço?", "ok"],
        responses=["direto, sem enrolação", "curto"],
        topics=["fitness", "study", "fitness"],
        engagement_events=["reply", "continue"],
    )

    model = result["behavior_modeling_evolution"]

    assert result["program"] == "P19P44"
    assert result["mode"] == "SHADOW_ONLY"
    assert model["interaction_patterns"]["total_interactions"] == 3
    assert model["interaction_patterns"]["short_followups"] == 3
    assert model["interaction_patterns"]["question_count"] == 1
    assert model["response_preference"]["prefers_direct_style"] is True
    assert model["topic_affinity"][0] == ("fitness", 2)
    assert model["engagement_prediction"]["score"] > 0


def test_p19p44_behavior_modeling_evolution_safety_contract():
    result = build_p19p44_behavior_modeling_evolution()

    safety = result["safety"]

    assert safety["runtime_mutation"] is False
    assert safety["response_mutation"] is False
    assert safety["rollbackable"] is True
    assert safety["canary_ready"] is True


def test_p19p44_engagement_prediction_caps_at_one():
    result = build_p19p44_behavior_modeling_evolution(
        interactions=list(range(50)),
        responses=list(range(50)),
        topics=list(range(50)),
        engagement_events=list(range(50)),
    )

    score = result["behavior_modeling_evolution"]["engagement_prediction"]["score"]

    assert score == 1.0
