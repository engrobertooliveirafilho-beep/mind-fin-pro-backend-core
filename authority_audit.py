"""Offline, fail-closed evidence audit for the recovered Trader R3 staging package.
No broker, network, orders, or mutation of canonical sources.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
EXPECTED = {f'P{i}' for i in range(2900, 2909)}


def audit(root=ROOT):
    root = Path(root)
    findings = []
    phases = {}
    files = sorted((root / 'evidence').glob('*.json'))
    for path in files:
        raw = path.read_bytes()
        try:
            obj = json.loads(raw.decode('utf-8-sig'))
        except (UnicodeError, json.JSONDecodeError) as exc:
            findings.append(f'INVALID_JSON:{path.name}:{type(exc).__name__}')
            continue
        if not isinstance(obj, dict):
            findings.append(f'INVALID_DOCUMENT:{path.name}')
            continue
        if '_TO_' in path.name:
            continue  # Chain-level audits are not engine implementations.
        phase = str(obj.get('phase', ''))
        match = re.match(r'^(P29\d{2})(?:\b|[_-])', phase)
        if not match or match.group(1) not in EXPECTED:
            findings.append(f'UNKNOWN_PHASE:{path.name}:{phase}')
            continue
        key = match.group(1)
        if key in phases:
            findings.append(f'DUPLICATE_PHASE:{key}:{path.name}')
        phases[key] = {'filename': path.name, 'sha256': hashlib.sha256(raw).hexdigest()}
    missing = sorted(EXPECTED - phases.keys())
    if missing:
        findings.append('MISSING_PHASES:' + ','.join(missing))
    # Evidence presence does not establish implementation, runtime wiring, or FTMO eligibility.
    return {
        'mode': 'READ_ONLY_PAPER_ONLY', 'status': 'BLOCK_CERTIFICATION',
        'phases': phases, 'missing_phases': missing, 'findings': findings,
        'runtime_verified': False, 'riskguard_wired': False,
        's20_s21_join_verified': False, 'ohlc_real_verified': False,
        'out_of_sample_certified': False, 'ftmo_ready': False,
        'merge_authorized': False, 'real_orders_authorized': False,
    }

if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, ensure_ascii=False))
