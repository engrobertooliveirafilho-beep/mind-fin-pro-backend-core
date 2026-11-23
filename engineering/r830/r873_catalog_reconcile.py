"""Reconcile historical STEP catalogs without inferring certification from filenames."""

def reconcile(agents, catalog, valid_only):
    blocked = {'status': 'blocked', 'certified': 0, 'executed': 0}
    if not isinstance(agents, list) or not isinstance(catalog, list) or not isinstance(valid_only, list):
        return {**blocked, 'reason': 'invalid_input'}
    if len(agents) > 1000 or len(catalog) > 10000 or len(valid_only) > 100000:
        return {**blocked, 'reason': 'limit'}
    declared = set()
    for agent in agents:
        if type(agent) is not dict or type(agent.get('step_ids', [])) is not list:
            return {**blocked, 'reason': 'invalid_agent'}
        for s in agent.get('step_ids', []):
            if type(s) is not int or s < 1:
                return {**blocked, 'reason': 'invalid_step'}
            declared.add(s)
    canonical = {}
    for item in catalog:
        if type(item) is not dict or type(item.get('step_number')) is not int or item['step_number'] in canonical:
            return {**blocked, 'reason': 'invalid_catalog'}
        canonical[item['step_number']] = item
    if any(type(x) is not int or x < 1 for x in valid_only):
        return {**blocked, 'reason': 'invalid_valid_only'}
    numbered = set(valid_only)
    outside = declared - canonical.keys()
    return {'status': 'reconciled_not_certified', 'declared_steps': len(declared),
            'catalog_matches': len(declared & canonical.keys()),
            'outside_catalog': sorted(outside),
            'outside_listed_only': sorted(outside & numbered),
            'outside_unlocated': sorted(outside - numbered),
            'unvalidated_catalog': sorted(s for s in declared & canonical.keys()
                                          if canonical[s].get('status') == 'nao_validado'),
            'certified': 0, 'executed': 0, 'e2e_certified': False}
