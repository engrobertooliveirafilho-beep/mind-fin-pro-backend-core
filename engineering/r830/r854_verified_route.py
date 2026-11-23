"""R854: integrated offline route -> independently attested source -> planner.

No dynamic registry, no FastAPI imports, no historical runtime execution.
"""
from r847_source_gate import attest_batch
from r844_step_planner import run_dry
from r853_route_adapter import route_dry

AGENT = 'dev.step_planner_agent'

def verified_route(agent_id, payload, sources, trusted, *, dry_run=True):
    def verified_dispatch(target, request):
        blocked = {'status': 'blocked', 'integration_authorized': False,
                   'runtime_certified': False}
        if target != AGENT or not isinstance(request, dict):
            return {**blocked, 'reason': 'unknown_or_invalid_agent'}
        evidence = attest_batch(request.get('approved_steps'), sources, trusted)
        if evidence.get('status') != 'attested':
            return {**blocked, 'reason': 'source_not_attested'}
        result = run_dry(request)
        if result.get('status') != 'planned':
            return {**blocked, 'reason': 'planner_rejected'}
        return {'status': 'planned', 'plan': result['plans'],
                'source_attested': True, **{k: blocked[k] for k in ('integration_authorized', 'runtime_certified')}}
    return route_dry(agent_id, payload, verified_dispatch, dry_run=dry_run)
