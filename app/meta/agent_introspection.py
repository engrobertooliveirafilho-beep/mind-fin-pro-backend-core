def inspect_agent(agent):
    points = []
    for field in ('planned_modules', 'expected_capabilities', 'critical_dependencies'):
        for name in getattr(agent, field, ()) or ():
            if not isinstance(name, str) or not name:
                raise ValueError('Invalid declaration')
            if field == 'planned_modules' or (field == 'expected_capabilities' and not callable(getattr(agent, name, None))) or (field == 'critical_dependencies' and getattr(agent, name, None) is None):
                points.append(f'{field}: {name}')
    for name in ('run', 'update', 'reset', 'status'):
        if not callable(getattr(agent, name, None)):
            points.append(f'missing_method: {name}')
    for field in ('managed_routes', 'managed_agents'):
        if hasattr(agent, field):
            points.append(f'{field}: {getattr(agent, field)}')
    return points
