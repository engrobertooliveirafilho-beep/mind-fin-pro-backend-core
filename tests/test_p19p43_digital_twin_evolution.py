from app.companionship.digital_twin_real import (
    build_p19p43_digital_twin_evolution,
)


def test_p19p43_digital_twin_evolution_builds_shadow_profile():
    result = build_p19p43_digital_twin_evolution(
        user_profile={"name": "Roberto", "style": "direct"},
        interests=["study", "fitness"],
        goals=["launch", "retention"],
        relationship_memory={"trust": 0.9},
        behavior_model={"prefers_short_answers": True},
    )

    evo = result["digital_twin_evolution"]

    assert result["program"] == "P19P43"
    assert result["mode"] == "SHADOW_ONLY"
    assert evo["user_profile_evolution"]["name"] == "Roberto"
    assert "study" in evo["interest_evolution"]
    assert "launch" in evo["goal_evolution"]
    assert evo["relationship_evolution"]["trust"] == 0.9
    assert evo["behavior_evidence"]["prefers_short_answers"] is True
    assert evo["confidence_scoring"]["score"] > 0


def test_p19p43_digital_twin_evolution_safety_contract():
    result = build_p19p43_digital_twin_evolution()

    safety = result["safety"]

    assert safety["runtime_mutation"] is False
    assert safety["response_mutation"] is False
    assert safety["rollbackable"] is True
    assert safety["canary_ready"] is True


def test_p19p43_confidence_scoring_caps_at_one():
    result = build_p19p43_digital_twin_evolution(
        user_profile={str(i): i for i in range(20)},
        interests=list(range(20)),
        goals=list(range(20)),
        relationship_memory={str(i): i for i in range(20)},
        behavior_model={str(i): i for i in range(20)},
    )

    score = result["digital_twin_evolution"]["confidence_scoring"]["score"]

    assert score == 1.0
