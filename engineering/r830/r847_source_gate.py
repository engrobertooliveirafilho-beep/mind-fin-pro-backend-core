"""Fail-closed source evidence gate; no execution of supplied code."""
import hashlib
import re

SHA = re.compile(r'[0-9a-f]{64}\Z')

def attest_batch(steps, sources, trusted):
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100 or not isinstance(sources, dict) or not isinstance(trusted, dict):
        return {'status': 'blocked', 'reason': 'invalid_batch'}
    ids = set()
    for step in steps:
        if not isinstance(step, dict) or set(step) != {'id', 'title', 'approved', 'source_sha256'}:
            return {'status': 'blocked', 'reason': 'invalid_step'}
        sid = step['id']
        if type(sid) is not int or sid <= 0 or sid in ids or step['approved'] is not True or not isinstance(step['title'], str) or not step['title'].strip() or len(step['title']) > 240:
            return {'status': 'blocked', 'reason': 'invalid_step'}
        ids.add(sid)
        claimed = step['source_sha256']
        if not isinstance(claimed, str) or not SHA.fullmatch(claimed):
            return {'status': 'blocked', 'reason': 'invalid_digest'}
    if set(sources) != ids or set(trusted) != ids:
        return {'status': 'blocked', 'reason': 'source_set_mismatch'}
    for step in steps:
        sid = step['id']
        blob, expected = sources[sid], trusted[sid]
        if not isinstance(blob, bytes) or not blob or not isinstance(expected, str) or not SHA.fullmatch(expected):
            return {'status': 'blocked', 'reason': 'invalid_evidence'}
        if hashlib.sha256(blob).hexdigest() != expected or expected != step['source_sha256']:
            return {'status': 'blocked', 'reason': 'digest_mismatch'}
    return {'status': 'attested', 'step_ids': sorted(ids), 'runtime_certified': False, 'integration_authorized': False}
