"""R862: explicit, offline-only consumer for recovered meta agent contracts."""
from r861_agents_runtime_safe import _build_generic_proposal

ALLOWED = frozenset({
    'meta.autonomous_evolution_agent',
    'meta.global_agent_mapper',
    'meta.mind_archives_agent_mapper',
})

def plan(agent_id, registry, *, paper_only=True):
    blocked = {'status': 'blocked', 'executed': 0, 'certified_e2e': False}
    if paper_only is not True:
        return {**blocked, 'reason': 'paper_only_required'}
    if type(agent_id) is not str or agent_id not in ALLOWED:
        return {**blocked, 'reason': 'unknown_agent'}
    if type(registry) is not dict or set(registry) != {'agents'} or type(registry['agents']) is not list:
        return {**blocked, 'reason': 'invalid_registry'}
    if len(registry['agents']) > 100:
        return {**blocked, 'reason': 'batch_limit'}
    matches = [a for a in registry['agents'] if type(a) is dict and a.get('id') == agent_id]
    if len(matches) != 1:
        return {**blocked, 'reason': 'ambiguous_or_missing_agent'}
    agent = matches[0]
    artifacts = agent.get('artifacts_produced')
    if type(artifacts) is not dict or type(artifacts.get('fields')) is not list:
        return {**blocked, 'reason': 'invalid_artifact_contract'}
    fields = artifacts['fields']
    if len(fields) > 50 or any(type(f) is not str or not f.isidentifier() or f.startswith('_') for f in fields) or len(set(fields)) != len(fields):
        return {**blocked, 'reason': 'invalid_fields'}
    if any(type(a) is not dict or type(a.get('id')) is not str for a in registry['agents']):
        return {**blocked, 'reason': 'invalid_agent_record'}
    return {'status': 'planned', 'agent_id': agent_id, 'proposal_fields': list(fields),
            'executed': 0, 'certified_e2e': False, 'source': 'registry_contract_only'}
