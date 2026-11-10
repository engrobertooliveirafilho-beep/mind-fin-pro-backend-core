"""Isolated deny-only result binding for the historical advisory GuardianMind."""
from copy import deepcopy
from guardian_gate import checked_scan, GuardianRejected

def bound_scan(guardian, *, explanation, reality, coherence, immunity):
    snapshot = dict(explanation=deepcopy(explanation), reality=deepcopy(reality),
                    coherence=deepcopy(coherence), immunity=deepcopy(immunity))
    result = checked_scan(guardian, **snapshot)
    sources = result.get('sources')
    if not isinstance(sources, dict) or set(sources) != {'explanation_tags','reality','immune','coherence'}:
        raise GuardianRejected('UNBOUND_SOURCES')
    if (sources['explanation_tags'] != snapshot['explanation']['tags'] or
        sources['reality'] != snapshot['reality'] or
        sources['immune'] != snapshot['immunity'] or
        sources['coherence'] != snapshot['coherence']):
        raise GuardianRejected('SOURCE_MISMATCH')
    alerts = []
    if 'ethics_attention' in snapshot['explanation']['tags']: alerts.append('ethics_attention')
    if snapshot['reality']['certainty'] < 0.3: alerts.append('low_reality_certainty')
    if snapshot['immunity']['flags']: alerts.append('cognitive_anomaly_detected')
    alerts.extend('coherence:'+a for a in snapshot['coherence']['alerts'])
    expected = max(0.0, min(1.0, 1.0 - (0.2 if 'ethics_attention' in alerts else 0)
      - (0.2 if 'low_reality_certainty' in alerts else 0)
      - (0.1 if 'cognitive_anomaly_detected' in alerts else 0)
      - (0.2 if any(a.startswith('coherence:') for a in alerts) else 0)))
    if result.get('alerts') != alerts or abs(result['protection_score']-expected)>1e-12:
        raise GuardianRejected('INCONSISTENT_GUARDIAN_RESULT')
    return result
