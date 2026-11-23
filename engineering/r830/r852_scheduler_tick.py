"""R852: isolated scheduler tick, no threads, file reads, or autonomous execution."""
def run_tick(registry, dispatch, *, dry_run=True):
    if dry_run is not True or not isinstance(registry, list) or not callable(dispatch):
        return {'status': 'blocked', 'reason': 'offline_only'}
    if len(registry) > 100:
        return {'status': 'blocked', 'reason': 'batch_limit'}
    planned = []
    seen = set()
    for entry in registry:
        if not isinstance(entry, dict) or set(entry) != {'id', 'governance'}:
            return {'status': 'blocked', 'reason': 'invalid_entry'}
        agent_id, governance = entry['id'], entry['governance']
        if not isinstance(agent_id, str) or not agent_id or agent_id in seen or not isinstance(governance, dict) or set(governance) != {'auto_run'} or type(governance['auto_run']) is not bool:
            return {'status': 'blocked', 'reason': 'invalid_entry'}
        seen.add(agent_id)
        if governance['auto_run']:
            planned.append(agent_id)
    return {'status': 'planned', 'agent_ids': planned, 'executed': 0,
            'integration_authorized': False, 'runtime_certified': False}
