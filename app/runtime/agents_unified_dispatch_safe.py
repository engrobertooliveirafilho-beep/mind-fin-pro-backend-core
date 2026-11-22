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


def dispatch_evidence_gated_agent(agent_id: str, payload, *, handlers: Mapping[str, Callable],
                                  evidence_by_id):
    """Bind PAPER authorization to the exact agent identity and evidence, not caller claims."""
    from app.runtime.trader_agent_evidence_gate import AgentEvidence, certify_paper_agent
    if not isinstance(agent_id, str) or not agent_id.strip():
        raise AgentDispatchDenied("agent identity required")
    if not isinstance(evidence_by_id, Mapping):
        raise AgentDispatchDenied("agent evidence mapping required")
    evidence = evidence_by_id.get(agent_id)
    if not isinstance(evidence, AgentEvidence) or evidence.agent_id != agent_id:
        raise AgentDispatchDenied("matching agent evidence required")
    try:
        certified = certify_paper_agent(evidence)
    except (TypeError, ValueError) as exc:
        raise AgentDispatchDenied("invalid agent evidence") from exc
    if not certified:
        raise AgentDispatchDenied("agent evidence not PAPER-certified")
    return dispatch_paper_agent(agent_id, payload, handlers=handlers,
                                certified_ids=frozenset((agent_id,)))
