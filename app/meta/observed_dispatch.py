import logging
from .agents_unified_runtime import run_agent

def dispatch(agent_id, payload=None, *, registry, metrics, profile):
    if not isinstance(profile, str) or not profile.strip():
        raise ValueError('Explicit profile required')
    result = run_agent(agent_id, payload, registry=registry)
    # Count dispatch attempts, never infer tool success or functional certification.
    try:
        metrics.record_agent_turn(profile)
    except Exception:
        logging.getLogger(__name__).warning("Agent telemetry write failed")
    return result
