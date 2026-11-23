"""P2397 read-only research gate; never promotes an edge or dispatches an order."""
from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True)
class ResearchDecision:
    allowed_for_runtime: bool
    allowed_for_research: bool
    decision: str
    reason: str
    hypotheses: int

def evaluate_research(scored_edge, policy, hypotheses):
    blocked = ResearchDecision(False, False, 'BLOCK', 'INVALID_RESEARCH_EVIDENCE', 0)
    if not isinstance(scored_edge, Mapping) or not isinstance(policy, Mapping):
        return blocked
    if not isinstance(hypotheses, (tuple, list)) or len(hypotheses) != 3:
        return blocked
    if (scored_edge.get('decision') != 'OBSERVE_SCORE' or
            scored_edge.get('real_execution_allowed') is not False or
            scored_edge.get('paper_stack_modified') is not False):
        return blocked
    required = {'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN',
                'runtime_modification_allowed':False,'broker_execution_allowed':False,
                'ftmo_real_allowed':False,'learning_scope':'OFFLINE_RESEARCH_ONLY'}
    if any(policy.get(k) != v or type(policy.get(k)) is not type(v) for k,v in required.items()):
        return blocked
    hard_rules = ['never promote OBSERVE_SCORE into runtime',
                  'never bypass P2392 walk-forward',
                  'never bypass P2394 score threshold',
                  'never allow real execution',
                  'generate candidates only as research hypotheses']
    if policy.get('hard_rules') != hard_rules:
        return blocked
    if not isinstance(policy.get('next_research_biases'), list) or len(policy['next_research_biases']) != 3:
        return blocked
    types = {'DD_REDUCTION','SESSION_FOOTPRINT_PRIORITY','CYCLE_TRANSITION_EXPANSION'}
    ids = set()
    for row in hypotheses:
        if not isinstance(row, Mapping) or row.get('type') not in types or row.get('paper_only') is not True:
            return blocked
        if row.get('base_context') != scored_edge.get('key'):
            return blocked
        hid = row.get('hypothesis_id')
        if not isinstance(hid, str) or not hid.startswith('P2397_HYP_') or hid in ids:
            return blocked
        ids.add(hid)
    if {row['type'] for row in hypotheses} != types:
        return blocked
    if [row.get('recommended_search_bias') for row in hypotheses] != policy['next_research_biases']:
        return blocked
    return ResearchDecision(False, True, 'RESEARCH_ONLY', 'OBSERVED_EDGE_OFFLINE_ONLY', 3)
