"""R872: fail-closed documentary gate before composing the offline Dev squad."""
from r870_dev_squad import compose
from r871_approval_gate import authorize


def compose_verified(payload, records):
    blocked = {'status': 'blocked', 'executed': False, 'e2e_certified': False}
    if type(payload) is not dict or type(payload.get('step_id')) is not int:
        return {**blocked, 'reason': 'invalid_payload'}
    gate = authorize(payload['step_id'], records)
    if gate.get('approved') is not True:
        return {**blocked, 'reason': gate.get('reason', 'documentary_gate_blocked')}
    # Even if the documentary contract changes, this integration never executes code.
    result = compose(payload)
    if result.get('status') != 'composed_offline' or result.get('executed') is not False:
        return {**blocked, 'reason': 'squad_blocked'}
    return {**result, 'status': 'documentary_verified_plan_only', 'executed': False, 'e2e_certified': False}
