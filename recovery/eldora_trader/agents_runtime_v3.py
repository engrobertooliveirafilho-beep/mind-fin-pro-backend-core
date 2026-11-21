"""Fail-closed dry-run dispatcher for five recovered historical agents."""
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
FORBIDDEN = frozenset({'real_orders','live_trading','execute_trade','gpu_provision','ftmo_real'})

def _check(value, seen, depth=0):
    if depth > 16:
        raise AgentRejected('payload too deep')
    if isinstance(value, (dict,list,tuple)):
        identity = id(value)
        if identity in seen:
            raise AgentRejected('cyclic payload')
        seen.add(identity)
        try:
            if isinstance(value,dict):
                for k,v in value.items():
                    if type(k) is not str or k.casefold() in FORBIDDEN:
                        raise AgentRejected('forbidden or invalid payload key')
                    _check(v,seen,depth+1)
            else:
                for v in value:
                    _check(v,seen,depth+1)
        finally:
            seen.remove(identity)
    elif type(value) not in (str,int,float,bool,type(None)):
        raise AgentRejected('unsupported payload value')

def run_agent(agent_id, payload=None, *, loader=None):
    if type(agent_id) is not str or agent_id not in AGENTS:
        raise AgentRejected('agent not allowlisted')
    if payload is not None and type(payload) is not dict:
        raise AgentRejected('payload must be dict')
    _check(payload or {}, set())
    try:
        module = (loader or import_module)('app.agents.' + AGENTS[agent_id])
        fn = getattr(module,'run_dry',None)
        if not callable(fn):
            raise AgentRejected('run_dry unavailable')
        result = fn(dict(payload or {}))
    except AgentRejected:
        raise
    except Exception as exc:
        raise AgentRejected('agent failed') from exc
    if (type(result) is not dict or result.get('agent_id') != agent_id or
        result.get('status') != 'ok' or result.get('mode') == 'stub' or 'error' in result):
        raise AgentRejected('unverified agent result')
    return result
