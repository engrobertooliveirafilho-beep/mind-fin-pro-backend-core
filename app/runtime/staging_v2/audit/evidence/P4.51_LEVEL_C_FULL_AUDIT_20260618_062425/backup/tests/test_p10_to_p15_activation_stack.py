from app.p10_activation_stack.activation_policy import load_activation_policy
from app.p10_activation_stack.controlled_consumption import run_controlled_consumption
from app.p10_activation_stack.rollback import rollback_controlled_consumption
from app.p10_activation_stack.risk_governance import evaluate_p12_risk
from app.p10_activation_stack.certification import certify_p10_to_p15

def test_p10_policy_default_off(monkeypatch):
    monkeypatch.delenv("ENABLE_P10_CONTROLLED_ACTIVATION", raising=False)
    monkeypatch.delenv("P10_ACTIVATION_MODE", raising=False)
    policy = load_activation_policy()
    assert policy.enabled is False
    assert policy.mode == "OFF"
    assert policy.may_modify_response is False
    assert policy.may_modify_runtime_state is False
    assert policy.may_modify_routes is False
    assert policy.may_modify_dispatcher is False
    assert policy.may_modify_whatsapp is False

def test_p10_controlled_consumption_preserves_core(monkeypatch):
    monkeypatch.setenv("ENABLE_P9_RUNTIME_CONSUMPTION", "true")
    monkeypatch.setenv("P9_RUNTIME_CONSUMPTION_MODE", "DRY_RUN")
    monkeypatch.setenv("ENABLE_P10_CONTROLLED_ACTIVATION", "true")
    monkeypatch.setenv("P10_ACTIVATION_MODE", "LIMITED_ACTIVE")
    monkeypatch.setenv("P10_ALLOW_RESPONSE_MODIFICATION", "false")

    result = run_controlled_consumption({"goal": "test"}, {"answer": "runtime"})
    assert result["status"] == "PASS"
    assert result["runtime_state_modified"] is False
    assert result["routes_modified"] is False
    assert result["dispatcher_modified"] is False
    assert result["whatsapp_webhook_modified"] is False
    assert result["runtime_authority_preserved"] is True

def test_p11_rollback_pass():
    result = rollback_controlled_consumption({"answer": "changed"}, {"answer": "original"})
    assert result["status"] == "PASS"
    assert result["rolled_back_response"] == {"answer": "original"}
    assert result["runtime_state_modified"] is False

def test_p12_risk_governance_blocks_mutation():
    result = evaluate_p12_risk({"routes_modified": True})
    assert result["status"] == "FAIL"
    assert result["activation_allowed"] is False

def test_p15_certification_pass():
    result = certify_p10_to_p15([
        {"status": "PASS", "runtime_state_modified": False, "routes_modified": False, "dispatcher_modified": False, "whatsapp_webhook_modified": False}
    ])
    assert result["status"] == "PASS"
    assert result["certification"] == "PASS"
