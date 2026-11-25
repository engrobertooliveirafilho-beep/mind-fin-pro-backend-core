from hashlib import sha256
from hmac import compare_digest
import re

def assess(required, evidence, expected_hashes=None):
    if not required or len(set(required)) != len(required):
        raise ValueError('invalid requirements')
    expected_hashes = expected_hashes or {}
    missing = []
    for key in required:
        data = evidence.get(key)
        digest = expected_hashes.get(key)
        if (not isinstance(data, bytes) or not data
                or not isinstance(digest, str)
                or not re.fullmatch(r'[0-9a-f]{64}', digest)
                or not compare_digest(sha256(data).hexdigest(), digest)):
            missing.append(key)
    return {'status': 'blocked' if missing else 'integrity_verified',
            'missing': missing, 'certified': False}
