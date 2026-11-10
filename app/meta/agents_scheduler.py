"""Explicit, bounded, opt-in scheduler interface. No background thread."""
from .agents_unified_runtime import AgentDispatchError, run_agent

def start_scheduler(*, enabled=False):
    if not enabled:
        return False
    raise AgentDispatchError("scheduler activation blocked pending certification")

def run_once(agent_id, payload=None, *, registry_path=None):
    return run_agent(agent_id, payload, registry_path=registry_path)
