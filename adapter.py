"""Strict offline preflight. No broker/network/real-order capability."""
from pathlib import Path
import json
from authority_audit import audit

ROOT = Path(__file__).resolve().parent

def evidence():
    report = audit(ROOT)
    return {phase: {'file': meta['filename'], 'sha256': meta['sha256']}
            for phase, meta in report['phases'].items()}

def preflight():
    report = audit(ROOT)
    docs = evidence()
    p2904 = {}
    p2907 = {}
    p2908 = {}
    for phase, target in [('P2904', 'risk'), ('P2907', 'permissions'), ('P2908', 'status')]:
        meta = docs.get(phase)
        if not meta:
            continue
        try:
            data = json.loads((ROOT / 'evidence' / meta['file']).read_text(encoding='utf-8-sig'))
        except (ValueError, OSError, UnicodeError):
            continue
        if phase == 'P2904':
            p2904 = data.get('rules', {})
        elif phase == 'P2907':
            p2907 = data.get('permissions', {})
        else:
            p2908 = data
    lock = (p2904.get('live_real_forbidden') is True
            and p2907.get('live') == 'FORBIDDEN'
            and p2907.get('real') == 'FORBIDDEN')
    clean = not report['findings'] and not report['missing_phases']
    return {
        'status': 'READ_ONLY_STAGING', 'evidence_count': len(docs),
        'missing_phases': report['missing_phases'], 'findings': report['findings'],
        'gates': {
            'DOSSIER_GROUNDING_GATE': 'PASS_EVIDENCE_ONLY' if clean else 'BLOCK',
            'FINALIZATION_LINE_GATE': 'PASS_READ_ONLY_NO_MERGE',
            'CHAT_DRIFT_INTERLOCK': 'PASS_READ_ONLY',
            'COST_GATE': 'PASS_NO_PAID_ACTION',
            'PAPER_ONLY_LOCK': 'PASS' if lock else 'BLOCK',
            'LONG_RUN_CERTIFICATION_GATE': 'BLOCK' if p2908.get('status') == 'CERTIFICATION_PLAN_READY' else 'REQUIRES_INDEPENDENT_PROOF',
            'CANONICAL_CODE_MERGE_GATE': 'BLOCK_NOT_ATTEMPTED',
            'S20_S21_JOIN_GATE': 'BLOCK_NOT_VERIFIED',
            'REAL_ORDER_GATE': 'BLOCK',
        },
        'evidence': docs,
        'next': 'VERIFY_CANONICAL_RUNTIME_AND_SYMBOL_TIME_JOIN_BEFORE_MERGE',
    }

if __name__ == '__main__':
    print(json.dumps(preflight(), ensure_ascii=False, indent=2))
