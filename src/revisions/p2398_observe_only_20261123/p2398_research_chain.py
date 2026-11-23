"""Isolated PAPER-only composition of P2397 research and P2398 observe gates.

No broker, runtime writer, or order dispatcher is imported.
"""
from dataclasses import dataclass
from collections.abc import Mapping
from p2397_historical_bridge import evaluate_historical_research
from p2398_historical_chain import evaluate_historical_chain
from p2398_observe_gate import GateRejected

@dataclass(frozen=True)
class ResearchChainDecision:
    decision: str
    research_allowed: bool
    runtime_promotion: bool
    order_dispatch: bool
    hypotheses: int

def evaluate_research_chain(p2394, router_contract, ensemble_result):
    # The P2397 bridge is anchored to the original P2394 artifact on disk.
    # Reject an unrelated caller-supplied P2394 before combining independent gates.
    from pathlib import Path
    import json
    if not isinstance(p2394, Mapping):
        raise GateRejected('P2394 evidence must be mapping')
    canonical = json.loads((Path(__file__).resolve().parent / 'p2394_original_summary.json').read_text(encoding='utf-8'))
    if p2394 != canonical:
        raise GateRejected('P2394 evidence differs from historical research source')
    # Fail closed before considering P2398 evidence if research is uncertified.
    research = evaluate_historical_research()
    if (research.decision != 'RESEARCH_ONLY' or
            research.allowed_for_research is not True or
            research.allowed_for_runtime is not False or
            research.hypotheses != 3):
        raise GateRejected('P2397 historical research not certified')
    observe = evaluate_historical_chain(p2394, router_contract, ensemble_result)
    if (observe.get('decision') != 'OBSERVE_ONLY' or
            observe.get('runtime_promotion') is not False or
            observe.get('order_dispatch') is not False):
        raise GateRejected('P2398 observe chain not certified')
    return ResearchChainDecision('RESEARCH_ONLY', True, False, False, 3)
