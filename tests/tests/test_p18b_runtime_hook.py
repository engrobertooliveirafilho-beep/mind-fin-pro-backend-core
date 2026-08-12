from app.p18_conversational_execution.runtime_hook import run_p18_runtime_hook_shadow

def test_p18b_runtime_hook_shadow_preserves_runtime():
    result = run_p18_runtime_hook_shadow(
        "tenho um problema me ajuda",
        {"answer": "runtime original"}
    )
    assert result["status"] == "PASS"
    assert result["mode"] == "SHADOW"
    assert result["selected_response"] == {"answer": "runtime original"}
    assert result["candidate_visible_to_user"] is False
    assert result["runtime_response_modified"] is False
    assert result["runtime_modified"] is False
    assert result["routes_modified"] is False
    assert result["dispatcher_modified"] is False
    assert result["whatsapp_webhook_modified"] is False
    assert result["production_enabled"] is False
