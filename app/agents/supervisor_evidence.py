from datetime import datetime, timezone
AGENT_ID = 'core.system_supervisor'
STEP_IDS = [1,15,19,31,42,71,90,190,221,248]

def run_dry(payload=None):
    payload = payload if isinstance(payload, dict) else {}
    evidence = payload.get('steps')
    evidence = evidence if isinstance(evidence, dict) else {}
    checks = {str(i): evidence.get(str(i)) is True for i in STEP_IDS}
    return {'agent_id': AGENT_ID, 'status': 'reported_healthy' if all(checks.values()) else 'unverified_or_unhealthy', 'mode': 'evidence_only', 'checks': checks, 'live_verified': False, 'generated_at': datetime.now(timezone.utc).isoformat()}
