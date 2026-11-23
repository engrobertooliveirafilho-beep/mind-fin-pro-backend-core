"""Offline dev-squad dispatcher. Replaces shadowed-import dynamic dispatch safely."""
from r844_step_planner import run_dry as plan_step

KNOWN = frozenset({
    'dev.step_planner_agent',
    'dev.code_blueprint_agent',
    'dev.test_guardian_agent',
    'dev.refactor_assistant_agent',
    'dev.impl_squad_coordinator',
})

def dispatch(agent_id, payload=None):
    if not isinstance(agent_id, str) or agent_id not in KNOWN:
        return {'status': 'blocked', 'reason': 'unknown_agent', 'integration_authorized': False}
    if agent_id != 'dev.step_planner_agent':
        return {'status': 'blocked', 'reason': 'historical_stub_not_activated', 'agent_id': agent_id, 'integration_authorized': False}
    try:
        result = plan_step(payload)
    except (TypeError, ValueError, KeyError):
        return {'status': 'blocked', 'reason': 'invalid_payload', 'agent_id': agent_id, 'integration_authorized': False}
    if not isinstance(result, dict) or result.get('status') != 'planned':
        return {'status': 'blocked', 'reason': 'planner_rejected', 'agent_id': agent_id, 'integration_authorized': False}
    return {**result, 'integration_authorized': False, 'runtime_certified': False, 'mode': 'offline_only'}
