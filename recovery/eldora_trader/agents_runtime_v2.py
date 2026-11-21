"""Fail-closed recovery of legacy dotted agent identifiers. Dry-run only."""
from importlib import import_module

class AgentRejected(ValueError):
    pass

AGENTS = {
    'sec.sentinel': 'sec_sentinel',
    'sec.gatekeeper': 'sec_gatekeeper',
    'dev.test_guardian_agent': 'dev_test_guardian_agent',
    'domain.economics_finance_markets': 'domain_economics_finance_markets',
    'core.safety_compliance_hub': 'core_safety_compliance_hub',
}
FORBIDDEN = {'real_orders', 'live_trading', 'execute_trade', 'gpu_provision', 'ftmo_real'}

def _safe_payload(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str) or k.lower() in FORBIDDEN:
                raise AgentRejected('forbidden payload key')
            _safe_payload(v)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _safe_payload(item)

def run_agent(agent_id, payload=None, *, loader=None):
    if type(agent_id) is not str or agent_id not in AGENTS:
        raise AgentRejected('agent not allowlisted')
    if payload is not None and not isinstance(payload, dict):
        raise AgentRejected('payload must be dict')
    _safe_payload(payload or {})
    module = (loader or import_module)('app.agents.' + AGENTS[agent_id])
    fn = getattr(module, 'run_dry', None)
    if not callable(fn):
        raise AgentRejected('run_dry unavailable')
    result = fn(dict(payload or {}))
    if not isinstance(result, dict) or result.get('agent_id') != agent_id:
        raise AgentRejected('agent identity mismatch')
    if result.get('status') in ('not_implemented', 'error', 'failed') or result.get('mode') == 'stub' or 'error' in result:
        raise AgentRejected('agent stub or failure')
    return result
