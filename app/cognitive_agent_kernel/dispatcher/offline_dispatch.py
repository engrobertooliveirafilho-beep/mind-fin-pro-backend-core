from .dispatcher import ExecutionDispatcher
from app.p7_adapters.oversight_contracts import OversightInput
from app.p7_adapters.oversight_offline_gate import authorize


def dispatch_offline(plan, payload: OversightInput):
    status = ExecutionDispatcher().dispatch(plan)
    if status != 'AWAITING_AUTHORIZATION':
        return status
    if not isinstance(payload, OversightInput) or payload.candidate_action != 'plan' or not authorize(payload):
        return 'BLOCKED'
    return 'AUTHORIZED_OFFLINE_PLANNING'
