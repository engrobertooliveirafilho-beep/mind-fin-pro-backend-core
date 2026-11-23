"""Offline source-attested STEP planner; never imports candidate source."""
import hashlib
import re
from r844_step_planner import run_dry

_SHA = re.compile(r'[0-9a-f]{64}\Z')

def plan_attested(payload, source_bytes, trusted_digests):
    if not isinstance(payload, dict) or not isinstance(source_bytes, dict) or not isinstance(trusted_digests, dict):
        return {'status': 'blocked', 'reason': 'invalid_inputs'}
    steps = payload.get('approved_steps')
    if not isinstance(steps, list) or not steps or len(steps) > 100:
        return {'status': 'blocked', 'reason': 'invalid_batch'}
    if set(source_bytes) != {s.get('id') for s in steps if isinstance(s, dict)} or set(trusted_digests) != set(source_bytes):
        return {'status': 'blocked', 'reason': 'source_set_mismatch'}
    for s in steps:
        if not isinstance(s, dict):
            return {'status': 'blocked', 'reason': 'invalid_step'}
        sid = s.get('id')
        blob = source_bytes.get(sid)
        expected = trusted_digests.get(sid)
        claimed = s.get('source_sha256')
        if not isinstance(blob, bytes) or not blob or not isinstance(expected, str) or not _SHA.fullmatch(expected) or not isinstance(claimed, str):
            return {'status': 'blocked', 'reason': 'invalid_evidence'}
        actual = hashlib.sha256(blob).hexdigest()
        if actual != expected or actual != claimed:
            return {'status': 'blocked', 'reason': 'digest_mismatch'}
    result = run_dry(payload)
    if result.get('status') != 'planned':
        return result
    return {**result, 'source_attested': True, 'runtime_certified': False, 'integration_authorized': False}
