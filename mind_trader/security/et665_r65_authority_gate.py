"""ET665 R65 GitHub-only evidence integrity gate; offline, fail-closed.

This is an evidence consistency checker, not a safety certifier.
Trust roots are explicitly supplied by the operator, never by the evidence itself.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROLES = ('git_inventory','historical_provenance','reconciliation','isolation_p77','isolation_p79','regression_junit','security_opinion')
SHA = re.compile(r'^[a-f0-9]{64}$')
COMMIT = re.compile(r'^[a-f0-9]{40}$')

def assess(evidence, trust, root):
    checks = {}
    used = set()
    pinned = trust.get('git_commit')
    trust_hashes = trust.get('sha256_by_role', {})
    if not isinstance(trust_hashes, dict):
        trust_hashes = {}
    commit_ok = isinstance(pinned, str) and COMMIT.fullmatch(pinned) is not None
    for role in ROLES:
        item = evidence.get(role)
        expected = trust_hashes.get(role)
        if not isinstance(item, dict) or not isinstance(expected, str) or not SHA.fullmatch(expected):
            checks[role] = 'MISSING_TRUST_ROOT_OR_EVIDENCE'
            continue
        path = item.get('path')
        if not isinstance(path, str) or not path or Path(path).is_absolute():
            checks[role] = 'INVALID_PATH'
            continue
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
            checks[role] = 'MISSING_OR_UNSAFE_PATH'
        elif resolved in used:
            checks[role] = 'REUSED_EVIDENCE'
        elif hashlib.sha256(resolved.read_bytes()).hexdigest() != expected:
            checks[role] = 'HASH_MISMATCH'
        elif item.get('git_commit') != pinned or not commit_ok:
            checks[role] = 'COMMIT_NOT_PINNED'
        else:
            checks[role] = 'INTEGRITY_OK_NOT_AUTHORITY'
        used.add(resolved)
    return {'schema':'ET665_R65_V1','checks':checks,
            'integrity_complete': commit_ok and all(x == 'INTEGRITY_OK_NOT_AUTHORITY' for x in checks.values()),
            'authority_certified':False,'isolation_certified':False,'phase_b_certified':False,
            'real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--evidence',required=True,type=Path)
    p.add_argument('--trust-roots',required=True,type=Path)
    p.add_argument('--root',required=True,type=Path)
    a=p.parse_args()
    try:
        evidence=json.loads(a.evidence.read_text(encoding='utf-8'))
        trust=json.loads(a.trust_roots.read_text(encoding='utf-8'))
        if not isinstance(evidence,dict) or not isinstance(trust,dict):
            raise ValueError('JSON_OBJECT_REQUIRED')
        result=assess(evidence,trust,a.root)
    except (OSError, ValueError) as ex:
        result={'phase_b_certified':False,'real_orders':'FORBIDDEN','error':type(ex).__name__}
    print(json.dumps(result,sort_keys=True))
    return 0 if result.get('integrity_complete') else 2

if __name__=='__main__':
    raise SystemExit(main())
