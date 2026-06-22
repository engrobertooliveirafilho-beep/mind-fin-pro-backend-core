from app.companionship.self_reflection_engine import (
    build_p19p45_self_reflection_evolution,
)


def test_p19p45_self_reflection_scores_response_memory_and_cognition():
    result = build_p19p45_self_reflection_evolution(
        response_text="Resposta direta, útil e com contexto suficiente.",
        memory_items=["Roberto prefere direto", "projeto Eldora", "Roberto prefere direto"],
        cognitive_context={"a": 1, "b": 2, "c": 3},
        prior_reflections=[{"program": "prior"}],
    )

    evo = result["self_reflection_evolution"]

    assert result["program"] == "P19P45"
    assert result["mode"] == "SHADOW_ONLY"
    assert evo["response_quality_scoring"]["score"] > 0
    assert evo["memory_usefulness_scoring"]["score"] > 0
    assert evo["cognition_usefulness_scoring"]["score"] > 0
    assert len(evo["reflection_ledger"]) == 2
    assert evo["reflection_ledger"][-1]["program"] == "P19P45"


def test_p19p45_self_reflection_safety_contract():
    result = build_p19p45_self_reflection_evolution()

    safety = result["safety"]

    assert safety["runtime_mutation"] is False
    assert safety["response_mutation"] is False
    assert safety["rollbackable"] is True
    assert safety["canary_ready"] is True


def test_p19p45_empty_inputs_score_zero_but_return_valid_contract():
    result = build_p19p45_self_reflection_evolution()

    evo = result["self_reflection_evolution"]

    assert evo["response_quality_scoring"]["score"] == 0.0
    assert evo["memory_usefulness_scoring"]["score"] == 0.0
    assert evo["cognition_usefulness_scoring"]["score"] == 0.0
    assert len(evo["reflection_ledger"]) == 1
