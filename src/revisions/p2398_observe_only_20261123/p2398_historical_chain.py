"""Read-only historical chain: original P2394 -> safe P2395 -> P2398."""
from collections.abc import Mapping
from p2395_context_router_safe import build_router
from p2396_ensemble_safe import build_ensemble
from p2398_evidence_adapter import evaluate_evidence
from p2398_observe_gate import GateRejected

def evaluate_historical_chain(p2394, router_contract, ensemble_result):
    if not all(isinstance(x, Mapping) for x in (p2394, router_contract, ensemble_result)):
        raise GateRejected("historical evidence must be mappings")
    if not isinstance(p2394, Mapping):
        raise GateRejected("P2394 evidence must be mapping")
    if p2394.get("mission") != "P2394_EDGE_SCORING":
        raise GateRejected("invalid P2394 mission")
    if (p2394.get("mode"), p2394.get("real_orders"), p2394.get("ftmo_real")) != ("PAPER_ONLY", "FORBIDDEN", "FORBIDDEN"):
        raise GateRejected("P2394 safety violation")
    if p2394.get("real_execution_allowed") is not False or p2394.get("paper_stack_modified") is not False:
        raise GateRejected("P2394 state mismatch")
    edge = p2394.get("best_scored_edge")
    if not isinstance(edge, Mapping) or edge.get("decision") != "OBSERVE_SCORE":
        raise GateRejected("P2394 edge not observed")
    if edge.get("final_score") != router_contract.get("input_edge_score"):
        raise GateRejected("score provenance mismatch")
    if edge.get("decision") != router_contract.get("input_edge_decision"):
        raise GateRejected("decision provenance mismatch")
    context = {"key": edge.get("key"), "direction": edge.get("direction"),
               "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
    result = build_router(edge).route(context)
    if result.allowed or result.route != "OBSERVE_ONLY":
        raise GateRejected("P2395 router failed closed")
    # Validate the complete evidence schema before indexing quorum or members.
    final = evaluate_evidence(router_contract, ensemble_result)
    vote = build_ensemble([{
        'allowed': result.allowed, 'route': result.route,
        'source_edge': edge.get('source_candidate_id'),
        'mode': result.mode, 'real_orders': result.real_orders,
        'ftmo_real': result.ftmo_real,
    }], quorum=ensemble_result['quorum']).vote()
    if vote.allowed or vote.vote != 'OBSERVE_ONLY':
        raise GateRejected('P2396 runtime ensemble failed closed')
    if (vote.members != ensemble_result['members'] or
            vote.operational_members != ensemble_result['operational_members'] or
            vote.reason != ensemble_result['reason']):
        raise GateRejected('P2396 runtime/evidence mismatch')
    if final.get("order_dispatch") is not False or final.get("runtime_promotion") is not False:
        raise GateRejected("P2398 promotion violation")
    return final
