from app.p9_runtime_consumption.consumption_gate import load_runtime_consumption_gate
from app.p9_runtime_consumption.context_bridge import build_read_only_runtime_context
from app.p9_runtime_consumption.planner_injection import inject_planner_artifact_dry_run
from app.p9_runtime_consumption.parity import assert_runtime_response_parity

def test_p9_gate_default_off(monkeypatch):
    monkeypatch.delenv("ENABLE_P9_RUNTIME_CONSUMPTION", raising=False)
    monkeypatch.delenv("P9_RUNTIME_CONSUMPTION_MODE", raising=False)
    gate = load_runtime_consumption_gate()
    assert gate.enabled is False
    assert gate.mode == "OFF"
    assert gate.may_modify_response is False
    assert gate.may_modify_runtime_state is False
    assert gate.may_modify_routes is False
    assert gate.may_modify_dispatcher is False

def test_p9_context_bridge_read_only():
    ctx = build_read_only_runtime_context({"message": "hello"})
    assert ctx["read_only"] is True
    assert ctx["runtime_modified"] is False
    assert ctx["state_modified"] is False
    assert ctx["routes_modified"] is False
    assert ctx["dispatcher_modified"] is False

def test_p9_injection_skipped_by_default():
    result = inject_planner_artifact_dry_run({"goal": "test"})
    assert result["status"] == "SKIPPED"
    assert result["runtime_response_modified"] is False
    assert result["runtime_state_modified"] is False
    assert result["runtime_authority_preserved"] is True

def test_p9_injection_dry_run_allowed(monkeypatch):
    monkeypatch.setenv("ENABLE_P9_RUNTIME_CONSUMPTION", "true")
    monkeypatch.setenv("P9_RUNTIME_CONSUMPTION_MODE", "DRY_RUN")
    result = inject_planner_artifact_dry_run({"goal": "test"})
    assert result["status"] == "PASS"
    assert result["consumption_allowed"] is True
    assert result["runtime_response_modified"] is False
    assert result["runtime_state_modified"] is False
    assert result["routes_modified"] is False
    assert result["dispatcher_modified"] is False

def test_p9_runtime_response_parity():
    before = {"answer": "runtime authoritative"}
    after = {"answer": "runtime authoritative"}
    result = assert_runtime_response_parity(before, after)
    assert result["status"] == "PASS"
    assert result["response_modified"] is False
    assert result["runtime_authority_preserved"] is True
