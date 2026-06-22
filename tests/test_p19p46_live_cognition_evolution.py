from app.companionship.live_cognition_gated import (
    build_p19p46_live_cognition_evolution,
)


def test_p19p46_live_cognition_builds_rankings():
    result = build_p19p46_live_cognition_evolution(
        contexts=["context_a","context_b"],
        goals=["goal_a","goal_b","goal_c"],
        memories=["memory_a"],
        reflections=["reflection_a"],
    )

    evo = result["live_cognition_evolution"]

    assert result["program"] == "P19P46"
    assert result["mode"] == "SHADOW_ONLY"

    assert len(evo["context_ranking"]) == 2
    assert len(evo["goal_ranking"]) == 3
    assert len(evo["memory_ranking"]) == 1
    assert len(evo["reflection_ranking"]) == 1

    assert evo["decision_engine"]["recommended_focus"] == "goal"


def test_p19p46_live_cognition_safety_contract():
    result = build_p19p46_live_cognition_evolution()

    safety = result["safety"]

    assert safety["runtime_mutation"] is False
    assert safety["response_mutation"] is False
    assert safety["rollbackable"] is True
    assert safety["canary_ready"] is True


def test_p19p46_live_cognition_empty_inputs():
    result = build_p19p46_live_cognition_evolution()

    evo = result["live_cognition_evolution"]

    assert evo["decision_engine"]["signal_count"] == 0
    assert len(evo["context_ranking"]) == 0
    assert len(evo["goal_ranking"]) == 0
