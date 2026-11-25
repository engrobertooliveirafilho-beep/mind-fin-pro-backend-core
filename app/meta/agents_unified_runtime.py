def run_agent(agent_id, payload=None, *, registry):
    handler = registry.get(agent_id)
    if not callable(handler):
        return {'agent_id': agent_id, 'status': 'unavailable'}
    try:
        result = handler(payload)
    except Exception:
        return {'agent_id': agent_id, 'status': 'failed'}
    if not isinstance(result, dict) or result.get('agent_id') != agent_id:
        return {'agent_id': agent_id, 'status': 'identity_mismatch'}
    return result
