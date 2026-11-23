"""R867: validate historical agent STEP declarations, without executing agents."""
import re
ID = re.compile(r'^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$')
def audit(registry):
    fail = {'status': 'blocked', 'executed': 0, 'e2e_certified': False}
    if type(registry) is not dict or type(registry.get('agents')) is not list or len(registry['agents']) > 1000:
        return {**fail, 'reason': 'invalid_registry'}
    seen = set()
    graph = {}
    for agent in registry['agents']:
        if type(agent) is not dict or type(agent.get('id')) is not str or not ID.fullmatch(agent['id']) or agent['id'] in seen:
            return {**fail, 'reason': 'invalid_agent'}
        seen.add(agent['id'])
        steps = agent.get('step_ids', [])
        if type(steps) is not list or len(steps) > 300 or any(type(s) is not int or not 1 <= s <= 100000 for s in steps) or len(steps) != len(set(steps)):
            return {**fail, 'reason': 'invalid_steps'}
        for step in steps:
            graph.setdefault(step, []).append(agent['id'])
    return {'status': 'audited_only', 'agent_count': len(seen), 'step_count': len(graph), 'links': sum(map(len, graph.values())), 'unmapped_agents': len(seen) - len({a for v in graph.values() for a in v}), 'executed': 0, 'e2e_certified': False}
