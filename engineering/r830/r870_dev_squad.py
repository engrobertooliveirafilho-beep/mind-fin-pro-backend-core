"""Offline composition of the previously published R868 and R869 Dev planners."""
from r868_step_planner import plan
from r869_dev_agents import AGENTS, run_dry


def compose(payload):
    """Fail closed; no dispatch, filesystem writes or execution."""
    blocked = {'status': 'blocked', 'executed': False, 'e2e_certified': False}
    first = plan(payload)
    if first.get('status') != 'planned_only':
        return {**blocked, 'reason': first.get('reason', 'planner_blocked')}
    results = []
    for agent in AGENTS:
        item = run_dry(agent, payload)
        if item.get('status') != 'planned_only' or item.get('executed') is not False:
            return {**blocked, 'reason': 'agent_blocked'}
        results.append(item)
    expected = first['plan'][0]['path']
    for item in results[:3]:
        target = item['result'].get('module', item['result'].get('target'))
        if target != expected:
            return {**blocked, 'reason': 'path_mismatch'}
    return {'status': 'composed_offline', 'step_id': first['step_id'],
            'planner': first['plan'], 'agents': results, 'executed': False,
            'e2e_certified': False}
