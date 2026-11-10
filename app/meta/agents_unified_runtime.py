"""Fail-closed recovered agent dispatcher; no implicit activation."""
import importlib
import json
from pathlib import Path

REG_PATH = Path(__file__).with_name("agents_registry.json")

class AgentDispatchError(RuntimeError):
    pass

def run_agent(agent_id: str, payload=None, *, registry_path=None):
    if not isinstance(agent_id, str) or not agent_id or not isinstance(payload, (dict, type(None))):
        raise AgentDispatchError("invalid agent request")
    path = Path(registry_path) if registry_path is not None else REG_PATH
    try:
        agents = json.loads(path.read_text(encoding="utf-8"))["agents"]
        if not isinstance(agents, list):
            raise ValueError("invalid registry")
        matches = [a for a in agents if isinstance(a, dict) and a.get("id") == agent_id]
        if len(matches) != 1 or matches[0].get("active") is not True:
            raise AgentDispatchError("agent unavailable or ambiguous")
        module_name = agent_id.replace(".", "_")
        if not module_name.isidentifier() or not all(c.isalnum() or c == "_" for c in module_name):
            raise AgentDispatchError("invalid module name")
        module = importlib.import_module("app.agents." + module_name)
        handler = getattr(module, "run_dry", None)
        if not callable(handler):
            raise AgentDispatchError("missing run_dry")
        result = handler(payload)
        if not isinstance(result, dict) or any(k in result for k in ("error", "not_implemented")) or result.get("status") in ("stub", "noop", "not_implemented", "error"):
            raise AgentDispatchError("nonfunctional agent response")
        if result.get("agent_id") != agent_id:
            raise AgentDispatchError("agent identity mismatch")
        return result
    except AgentDispatchError:
        raise
    except Exception as exc:
        raise AgentDispatchError("agent execution failed") from exc
