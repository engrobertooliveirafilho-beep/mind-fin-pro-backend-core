from app.p18_conversational_execution.selection_gate import run_limited_internal_selection_gate

def test_p18d_selection_gate_recommends_candidate_without_modifying_runtime():
    result = run_limited_internal_selection_gate(
        "tenho um problema me ajuda",
        {"answer": "Claro! Vamos seguir algumas etapas em um checklist."}
    )
    assert result["status"] == "PASS"
    assert result["recommendation"] == "USE_CANDIDATE_INTERNAL_ONLY"
    assert result["selected_response"] == {"answer": "Claro! Vamos seguir algumas etapas em um checklist."}
    assert result["candidate_visible_to_user"] is False
    assert result["runtime_response_modified"] is False
    assert result["runtime_modified"] is False
    assert result["production_enabled"] is False
