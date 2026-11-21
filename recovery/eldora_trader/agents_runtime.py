"""Safe dry-run dispatcher replacing colliding wildcard imports in legacy agent runtime."""
import importlib

class AgentRejected(ValueError):
    pass

ALLOWED = frozenset({'sec_gatekeeper','sec_sentinel','dev_test_guardian_agent','domain_economics_finance_markets','core_safety_compliance_hub'})

def run_agent(agent_id, payload=None, *, loader=None):
    if not isinstance(agent_id,str) or agent_id not in ALLOWED:
        raise AgentRejected('agent not allowlisted')
    if payload is not None and not isinstance(payload,dict):
        raise AgentRejected('payload must be a mapping')
    if payload and any(k in payload for k in ('real_orders','live_trading','execute_trade','gpu_provision')):
        raise AgentRejected('unsafe payload key')
    load = loader or importlib.import_module
    module = load('app.agents.'+agent_id)
    fn = getattr(module,'run_dry',None)
    if not callable(fn):
        raise AgentRejected('run_dry unavailable')
    return fn(dict(payload or {}))
