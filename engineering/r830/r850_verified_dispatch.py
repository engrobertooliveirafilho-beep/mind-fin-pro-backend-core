"""Offline verified dispatcher: no plans without independently supplied source digests."""
from r847_source_gate import attest_batch
from r849_dev_dispatch import dispatch

def dispatch_verified(agent_id, payload, sources, trusted):
    if agent_id != 'dev.step_planner_agent':
        return {'status': 'blocked', 'reason': 'not_authorized', 'integration_authorized': False}
    if not isinstance(payload, dict):
        return {'status': 'blocked', 'reason': 'invalid_payload', 'integration_authorized': False}
    gate = attest_batch(payload.get('approved_steps'), sources, trusted)
    if gate.get('status') != 'attested':
        return {'status': 'blocked', 'reason': 'source_attestation_failed', 'detail': gate.get('reason'), 'integration_authorized': False}
    result = dispatch(agent_id, payload)
    if result.get('status') != 'planned':
        return result
    return {**result, 'source_attested': True, 'runtime_certified': False, 'integration_authorized': False}
