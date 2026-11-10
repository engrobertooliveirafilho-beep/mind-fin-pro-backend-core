"""Fail-closed adapter for recovered P2408, PAPER only; no broker interface."""
from et665_r434_context_consensus_gate import decide

def dispatch_paper(context, votes, policy, original_dispatch, now=None):
    result = decide(context, votes, policy, now)
    if not result.get('allowed'):
        return result
    try:
        legacy = original_dispatch(context)
    except Exception:
        return {'allowed':False,'route':'OBSERVE_ONLY','reason':'LEGACY_EXCEPTION','real_execution_allowed':False}
    if not isinstance(legacy,dict) or legacy.get('allowed') is not True or legacy.get('real_execution_allowed') is not False:
        return {'allowed':False,'route':'OBSERVE_ONLY','reason':'LEGACY_REJECTED','real_execution_allowed':False}
    return {**result,'reason':'DIRECTIONAL_CONSENSUS_AND_LEGACY_PASS','real_execution_allowed':False}
