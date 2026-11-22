"""Isolated fail-closed dispatch replacement for historical MIND unified runtime.
Never imports or executes historical agents implicitly.
"""
from typing import Callable, Mapping

class AgentDispatchDenied(ValueError):
    pass

def dispatch_paper_agent(agent_id: str, payload, *, handlers: Mapping[str, Callable],
                         certified_ids: frozenset[str]):
    if not isinstance(agent_id,str) or not agent_id.strip():
        raise AgentDispatchDenied("agent identity required")
    if not isinstance(handlers,Mapping) or type(certified_ids) is not frozenset:
        raise AgentDispatchDenied("explicit handlers and certification required")
    if agent_id not in certified_ids:
        raise AgentDispatchDenied("agent not PAPER-certified")
    handler=handlers.get(agent_id)
    if not callable(handler):
        raise AgentDispatchDenied("registered handler unavailable")
    return handler(payload)
