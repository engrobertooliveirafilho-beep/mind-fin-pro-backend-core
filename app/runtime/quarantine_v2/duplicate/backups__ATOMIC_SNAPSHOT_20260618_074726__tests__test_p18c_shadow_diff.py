from app.p18_conversational_execution.response_executor import execute_conversational_response
from app.p18_conversational_execution.shadow_diff import compare_runtime_vs_shadow

def test_p18c_candidate_beats_bad_runtime_response():
    candidate = execute_conversational_response("tenho um problema me ajuda")
    diff = compare_runtime_vs_shadow(
        "tenho um problema me ajuda",
        {"answer": "Claro! Vamos seguir algumas etapas em um checklist."},
        {"answer": candidate["answer"]},
    )
    assert diff["status"] == "PASS"
    assert diff["candidate_better"] is True
    assert diff["runtime_modified"] is False
    assert diff["candidate_visible_to_user"] is False
