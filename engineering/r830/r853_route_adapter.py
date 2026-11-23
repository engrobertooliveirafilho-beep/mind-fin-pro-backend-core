"""Offline adapter for historical FastAPI unified-agent route contracts.

Does not import FastAPI, historical runtime, or execute agents.
"""
import re

AGENT_RE = re.compile(r'\A[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')

def route_dry(agent_id, payload, dispatcher, *, dry_run=True):
    if dry_run is not True or not isinstance(agent_id, str) or not AGENT_RE.fullmatch(agent_id):
        return {'status': 'blocked', 'reason': 'invalid_route', 'integration_authorized': False}
    if payload is not None and not isinstance(payload, dict):
        return {'status': 'blocked', 'reason': 'invalid_payload', 'integration_authorized': False}
    if not callable(dispatcher):
        return {'status': 'blocked', 'reason': 'missing_dispatcher', 'integration_authorized': False}
    try:
        result = dispatcher(agent_id, payload)
    except Exception:
        return {'status': 'blocked', 'reason': 'dispatch_failed', 'integration_authorized': False}
    if not isinstance(result, dict) or result.get('status') != 'planned' or result.get('integration_authorized') is not False or result.get('runtime_certified') is not False:
        return {'status': 'blocked', 'reason': 'unsafe_dispatch_result', 'integration_authorized': False}
    return {'status': 'planned', 'agent_id': agent_id, 'plan': result.get('plan', []), 'integration_authorized': False, 'runtime_certified': False}
