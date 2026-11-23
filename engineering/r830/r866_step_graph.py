"""Read-only deterministic graph of agent-to-STEP declarations."""
import re

ID = re.compile(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')

def reconcile(registry):
    blocked = {'status': 'blocked', 'executed': 0, 'certified_e2e': False}
    if type(registry) is not dict or type(registry.get('agents')) is not list or len(registry['agents']) > 1000:
        return {**blocked, 'reason': 'invalid_registry'}
    ids = set()
    graph = {}
    for agent in registry['agents']:
        if type(agent) is not dict or type(agent.get('id')) is not str or not ID.fullmatch(agent['id']) or agent['id'] in ids:
            return {**blocked, 'reason': 'invalid_agent'}
        ids.add(agent['id'])
        steps = agent.get('step_ids', [])
        if type(steps) is not list or len(steps) > 300 or any(type(s) is not int or not 1 <= s <= 100000 for s in steps) or len(steps) != len(set(steps)):
            return {**blocked, 'reason': 'invalid_steps'}
        for step in steps:
            graph.setdefault(step, []).append(agent['id'])
    return {'status': 'mapped_offline', 'agents': len(ids), 'steps': len(graph),
            'links': sum(map(len, graph.values())),
            'step_to_agents': {str(s): sorted(graph[s]) for s in sorted(graph)},
            'executed': 0, 'certified_e2e': False}
