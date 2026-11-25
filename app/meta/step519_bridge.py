from .observed_dispatch import dispatch


def execute_plan(plan, *, role_map, registry, metrics, profile):
    """Execute explicitly mapped roles only; stop on any unaccepted result."""
    if not isinstance(profile, str) or not profile.strip():
        raise ValueError('Explicit profile required')
    steps = plan['steps']
    if not isinstance(steps, list) or not steps:
        raise ValueError('Nonempty steps required')
    prepared = []
    for index, step in enumerate(steps):
        if step['step_index'] != index:
            raise ValueError('Invalid step sequence')
        agent = role_map.get(step['assigned_agent_role'])
        if not isinstance(agent, str) or not callable(registry.get(agent)):
            return {'status': 'blocked', 'results': []}
        prepared.append((agent, step['description']))
    results = []
    for agent, description in prepared:
        result = dispatch(agent, {'description': description}, registry=registry,
                          metrics=metrics, profile=profile)
        results.append(result)
        if result.get('status') != 'ok' or result.get('mode') in ('stub', 'noop', 'dry_run'):
            return {'status': 'blocked', 'results': results}
    return {'status': 'completed', 'results': results}
