"""R879 offline safeguards for recovered STEP 532/533/540/542 contracts.
All operations are pure validations; no canon mutation, treaty, or ethical approval.
"""
import math

DENY = {'status': 'blocked', 'executed': False, 'e2e_certified': False}

def validate_knowledge(key, version, payload, *, promotion=False, attested=False):
    if type(key) is not str or not key.startswith('canon:') or len(key) > 128:
        return {**DENY, 'reason': 'invalid_key'}
    if type(version) is not int or version < 1 or type(payload) is not dict or not payload:
        return {**DENY, 'reason': 'invalid_version_or_payload'}
    if any(type(k) is not str or not k for k in payload):
        return {**DENY, 'reason': 'invalid_payload_key'}
    if promotion and attested is not True:
        return {**DENY, 'reason': 'unattested_promotion'}
    return {'status': 'review_candidate_only', 'key': key, 'version': version,
            'promotion_authorized': False, 'executed': False, 'e2e_certified': False}

def validate_treaty(parties, proposal):
    if type(parties) is not list or len(parties) < 2 or len(set(map(str, parties))) != len(parties) or any(type(p) is not str or not p for p in parties):
        return {**DENY, 'reason': 'invalid_parties'}
    if type(proposal) is not dict or set(proposal) != {'mode', 'topics', 'max_data_sensitivity'}:
        return {**DENY, 'reason': 'invalid_proposal'}
    topics = proposal['topics']
    if proposal['mode'] != 'cooperation' or type(topics) is not list or not topics or any(type(t) is not str or not t for t in topics):
        return {**DENY, 'reason': 'invalid_topics_or_mode'}
    if any(t.lower() in ('aggression', 'unbounded_access') for t in topics):
        return {**DENY, 'reason': 'prohibited_topic'}
    sensitivity = proposal['max_data_sensitivity']
    if type(sensitivity) is not int or not 0 <= sensitivity <= 4:
        return {**DENY, 'reason': 'invalid_sensitivity'}
    return {'status': 'treaty_review_only', 'accepted': False, 'executed': False, 'e2e_certified': False}

def validate_ethics(item_id, reviewer, decision, evidence):
    if type(item_id) is not str or not item_id.startswith('ERB-') or not item_id[4:].isdigit():
        return {**DENY, 'reason': 'invalid_item'}
    if type(reviewer) is not str or not reviewer.strip() or type(decision) is not str or decision not in ('approve', 'reject'):
        return {**DENY, 'reason': 'invalid_reviewer_or_decision'}
    if type(evidence) is not dict or evidence.get('verified') is not True or type(evidence.get('source')) is not str or not evidence['source']:
        return {**DENY, 'reason': 'unverified_evidence'}
    return {'status': 'ethical_review_candidate_only', 'approval_authorized': False, 'executed': False, 'e2e_certified': False}
