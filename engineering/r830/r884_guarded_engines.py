"""R884 guarded adapters around recovered STEP 532/533/540/542 engines.
Original engine instances are injected; this module never edits original sources.
Approval evidence must be verified by an externally supplied verifier.
"""
import re

SHA = re.compile(r'^[0-9a-f]{64}$')

class GateError(ValueError):
    pass

def _valid_key(key):
    return type(key) is str and 1 <= len(key) <= 160 and key.strip() == key and key.startswith(('canon:', 'mind:'))

def _valid_payload(payload):
    return type(payload) is dict and bool(payload) and all(type(k) is str and k.strip() for k in payload)

def _verified(verifier, evidence, scope):
    if not callable(verifier) or type(evidence) is not dict:
        return False
    digest, source = evidence.get('sha256'), evidence.get('source')
    if type(digest) is not str or not SHA.fullmatch(digest) or type(source) is not str or not source.strip():
        return False
    try:
        return verifier(evidence, scope) is True
    except Exception:
        return False

class KnowledgeLifecycleGuard:
    def __init__(self, engine): self.engine = engine
    def create(self, key, payload):
        if not _valid_key(key) or not _valid_payload(payload): raise GateError('invalid_knowledge')
        return self.engine.create(key, payload)
    def revise(self, key, payload):
        if not _valid_key(key) or not _valid_payload(payload): raise GateError('invalid_knowledge')
        return self.engine.revise(key, payload)
    def deprecate(self, key, version, evidence, verifier):
        if not _valid_key(key) or (version is not None and (type(version) is not int or version < 1)):
            raise GateError('invalid_deprecation_target')
        if not _verified(verifier, evidence, {'operation':'deprecate','key':key,'version':version}):
            raise GateError('unverified_deprecation')
        return self.engine.deprecate(key, version)

class CanonBuilderGuard:
    def __init__(self, engine, verifier): self.engine, self.verifier = engine, verifier
    def add_experimental(self, key, payload):
        if not _valid_key(key) or not _valid_payload(payload): raise GateError('invalid_canon_entry')
        return self.engine.add_experimental(key, payload)
    def promote_to_canon(self, key, version, evidence):
        if not _valid_key(key) or (version is not None and (type(version) is not int or version < 1)):
            raise GateError('invalid_promotion_target')
        scope={'operation':'promote_to_canon','key':key,'version':version}
        if not _verified(self.verifier, evidence, scope): raise GateError('unverified_promotion')
        return self.engine.promote_to_canon(key, version)

class CognitiveTreatyGuard:
    def __init__(self, engine): self.engine=engine
    def negotiate(self, parties, proposal):
        if type(parties) is not list or len(parties)<2 or any(type(p) is not str or not p.strip() for p in parties) or len(set(parties))!=len(parties):
            raise GateError('invalid_parties')
        if type(proposal) is not dict or set(proposal)!={'mode','topics','max_data_sensitivity'}:
            raise GateError('invalid_treaty_contract')
        if proposal['mode']!='cooperation' or type(proposal['topics']) is not list or not proposal['topics'] or any(type(t) is not str or not t.strip() for t in proposal['topics']):
            raise GateError('invalid_treaty_topics')
        if any(t.lower() in ('aggression','unbounded_access') for t in proposal['topics']):
            raise GateError('prohibited_topic')
        sensitivity=proposal['max_data_sensitivity']
        if type(sensitivity) is not int or not 0<=sensitivity<=4:
            raise GateError('invalid_sensitivity')
        return self.engine.negotiate(parties, proposal)

class EthicalReviewGuard:
    def __init__(self, engine, verifier): self.engine,self.verifier=engine,verifier
    def submit(self, payload):
        if not _valid_payload(payload): raise GateError('invalid_review_payload')
        return self.engine.submit(payload)
    def approve(self, item_id, reviewer, evidence, notes=None):
        if type(item_id) is not str or not item_id.startswith('ERB-') or not item_id[4:].isdigit() or type(reviewer) is not str or not reviewer.strip():
            raise GateError('invalid_reviewer_or_item')
        item=self.engine._items.get(item_id)
        if item is None or item.status!='pending': raise GateError('item_not_pending')
        scope={'operation':'ethical_approve','item_id':item_id,'reviewer':reviewer}
        if not _verified(self.verifier,evidence,scope): raise GateError('unverified_ethical_approval')
        return self.engine.approve(item_id,reviewer,notes)
    def reject(self, item_id, reviewer, evidence, notes=None):
        if type(item_id) is not str or not item_id.startswith('ERB-') or not item_id[4:].isdigit() or type(reviewer) is not str or not reviewer.strip():
            raise GateError('invalid_reviewer_or_item')
        item=self.engine._items.get(item_id)
        if item is None or item.status!='pending': raise GateError('item_not_pending')
        scope={'operation':'ethical_reject','item_id':item_id,'reviewer':reviewer}
        if not _verified(self.verifier,evidence,scope): raise GateError('unverified_ethical_rejection')
        return self.engine.reject(item_id,reviewer,notes)
