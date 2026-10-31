"""Quarantined, dependency-injected MIND agent dispatcher.
No automatic imports, network, scheduler, or side effects.
"""
from typing import Any, Callable, Mapping

class AgentDispatchError(RuntimeError):
    pass

def run_agent(agent_id: str, payload: Any = None, *, registry: Mapping[str, Callable] = None):
    if not isinstance(agent_id, str) or not agent_id.strip():
        raise AgentDispatchError("INVALID_AGENT_ID")
    if registry is None or agent_id not in registry:
        raise AgentDispatchError("AGENT_NOT_REGISTERED")
    fn = registry[agent_id]
    if not callable(fn):
        raise AgentDispatchError("INVALID_EXECUTOR")
    result = fn(payload)
    if not isinstance(result, dict):
        raise AgentDispatchError("INVALID_RESULT")
    if result.get("error") or result.get("status") in ("stub", "noop", "error", "not_implemented"):
        raise AgentDispatchError("UNVERIFIED_EXECUTION")
    return result
