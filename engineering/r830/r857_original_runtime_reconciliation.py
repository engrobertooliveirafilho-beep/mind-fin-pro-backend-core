"""R857: audit recovered historical runtime signals without importing originals.

The manifest is an explicit set of source observations, not an E2E certificate.
"""
from r856_import_side_effect_gate import inspect_import_safety

ORIGINALS = {
    'agents_runtime': '1' + '0WByay5ageFVa7fDPGsF4s-6mg2DDTxT',
    'dev_runtime': '1oTubBWLh_V7YUvtl0M7eMXe3VBwmZ4ga',
    'scheduler': '1UwXyDGXmPmVTXFUdahyUX14m4Fdl2tLX',
}

def audit_recovered(sources):
    if not isinstance(sources, dict) or set(sources) != set(ORIGINALS):
        return {'status': 'blocked', 'reason': 'incomplete_evidence', 'runtime_certified': False}
    reports = {}
    for key in ORIGINALS:
        report = inspect_import_safety(sources[key])
        reports[key] = report
        if report['status'] not in ('blocked', 'candidate_only'):
            return {'status': 'blocked', 'reason': 'unexpected_audit', 'runtime_certified': False}
    return {'status': 'audited_only', 'reports': reports,
            'runtime_certified': False, 'integration_authorized': False}
