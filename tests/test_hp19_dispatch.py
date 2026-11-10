"""Contract regression with synthetic handlers; not HP19 certification."""
import json
import sys
import types
from pathlib import Path
import pytest
from app.meta.agents_unified_runtime import AgentDispatchError, run_agent
from app.meta.agents_scheduler import start_scheduler

@pytest.fixture
def registry(tmp_path, monkeypatch):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps({"agents":[{"id":"core.alpha","active":True},{"id":"core.beta","active":True}]}))
    for name in ("alpha","beta"):
        module = types.ModuleType("app.agents.core_"+name)
        module.run_dry = lambda payload, n=name: {"agent_id":"core."+n,"value":n}
        monkeypatch.setitem(sys.modules, module.__name__, module)
    return p

def test_routes_to_requested_handler(registry):
    assert run_agent("core.alpha", {}, registry_path=registry)["value"] == "alpha"
    assert run_agent("core.beta", {}, registry_path=registry)["value"] == "beta"

def test_unknown_agent_rejected(registry):
    with pytest.raises(AgentDispatchError): run_agent("core.unknown", {}, registry_path=registry)

def test_error_response_rejected(registry, monkeypatch):
    monkeypatch.setattr(sys.modules["app.agents.core_alpha"], "run_dry", lambda _: {"agent_id":"core.alpha","error":"broken"})
    with pytest.raises(AgentDispatchError): run_agent("core.alpha", {}, registry_path=registry)

def test_identity_mismatch_rejected(registry, monkeypatch):
    monkeypatch.setattr(sys.modules["app.agents.core_alpha"], "run_dry", lambda _: {"agent_id":"core.beta","status":"ok"})
    with pytest.raises(AgentDispatchError): run_agent("core.alpha", {}, registry_path=registry)

def test_scheduler_disabled():
    assert start_scheduler() is False
    with pytest.raises(AgentDispatchError): start_scheduler(enabled=True)

def test_duplicate_registry_rejected(registry):
    registry.write_text(json.dumps({"agents":[{"id":"core.alpha","active":True},{"id":"core.alpha","active":True}]}))
    with pytest.raises(AgentDispatchError): run_agent("core.alpha", {}, registry_path=registry)
