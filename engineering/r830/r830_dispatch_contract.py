"""Fail-closed agent dispatcher contract; dependencies are injected, never imported dynamically."""
from typing import Any, Callable, Mapping

class AgentDispatchError(RuntimeError):
    pass

def run_agent(agent_id: str, payload: Any = None, *, registry: Mapping[str, Callable] | None = None) -> dict:
    if not isinstance(agent_id, str) or not agent_id.strip():
        raise AgentDispatchError("invalid_agent_id")
    if registry is None or agent_id not in registry:
        raise AgentDispatchError("agent_not_registered")
    handler = registry[agent_id]
    if not callable(handler):
        raise AgentDispatchError("agent_handler_not_callable")
    result = handler(payload)
    if not isinstance(result, dict):
        raise AgentDispatchError("invalid_agent_result")
    status = str(result.get("status", "")).strip().lower()
    mode = str(result.get("mode", "")).strip().lower()
    if status in {"error", "stub", "noop", "not_implemented"} or mode in {"stub", "noop", "not_implemented"}:
        raise AgentDispatchError("nonfunctional_agent_result")
    if result.get("agent_id") not in (None, agent_id):
        raise AgentDispatchError("agent_identity_mismatch")
    return {"agent_id": agent_id, **result}
