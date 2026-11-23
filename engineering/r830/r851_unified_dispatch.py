"""Fail-closed replacement for the historical import-shadowed unified dispatcher.

No historical agent is imported or executed by this module.
"""
from collections.abc import Mapping

ALLOWED = frozenset({
    'dev.step_planner_agent',
    'dev.code_blueprint_agent',
    'dev.test_guardian_agent',
    'dev.refactor_assistant_agent',
    'dev.impl_squad_coordinator',
})


def dispatch(agent_id, payload=None, *, registry=None):
    """Dispatch only explicitly registered, reviewed handlers in offline mode.

    A registry entry is a (handler, evidence) pair. Evidence must explicitly
    attest review and offline authorization. This is not runtime certification.
    """
    blocked = {'status': 'blocked', 'integration_authorized': False,
               'runtime_certified': False}
    if type(agent_id) is not str or agent_id not in ALLOWED:
        return {**blocked, 'reason': 'unknown_agent'}
    if not isinstance(registry, Mapping):
        return {**blocked, 'reason': 'no_reviewed_registry'}
    item = registry.get(agent_id)
    if not isinstance(item, tuple) or len(item) != 2:
        return {**blocked, 'reason': 'missing_reviewed_handler'}
    handler, evidence = item
    if not callable(handler) or not isinstance(evidence, dict) or evidence != {
        'agent_id': agent_id, 'reviewed': True, 'offline_only': True,
        'source_attested': True,
    }:
        return {**blocked, 'reason': 'untrusted_handler'}
    if payload is not None and not isinstance(payload, dict):
        return {**blocked, 'reason': 'invalid_payload'}
    try:
        result = handler(payload)
    except Exception:
        return {**blocked, 'reason': 'handler_failed'}
    if not isinstance(result, dict) or result.get('status') != 'planned':
        return {**blocked, 'reason': 'handler_rejected'}
    return {**blocked, 'status': 'planned', 'agent_id': agent_id,
            'plan': result.get('plans', []), 'mode': 'offline_only'}
