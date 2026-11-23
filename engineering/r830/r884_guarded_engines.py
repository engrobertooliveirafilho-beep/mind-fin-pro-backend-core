import re
SHA=re.compile(r'^[0-9a-f]{64}$')
class GateError(ValueError): pass
def _valid_key(k): return type(k) is str and 1<=len(k)<=160 and k.strip()==k and k.startswith(('canon:','mind:'))
def _valid_payload(p): return type(p) is dict and bool(p) and all(type(k) is str and k.strip() for k in p)
def _verified(v,e,s):
 if not callable(v) or type(e) is not dict:return False
 d,src=e.get('sha256'),e.get('source')
 if type(d) is not str or not SHA.fullmatch(d) or type(src) is not str or not src.strip():return False
 try:return v(e,s) is True
 except Exception:return False
class KnowledgeLifecycleGuard:
 def __init__(self,e):self.engine=e
 def create(self,k,p):
  if not _valid_key(k) or not _valid_payload(p):raise GateError('invalid_knowledge')
  return self.engine.create(k,p)
 def revise(self,k,p):
  if not _valid_key(k) or not _valid_payload(p):raise GateError('invalid_knowledge')
  return self.engine.revise(k,p)
 def deprecate(self,k,v,evidence,verifier):
  if not _valid_key(k) or (v is not None and (type(v) is not int or v<1)):raise GateError('invalid_deprecation_target')
  if not _verified(verifier,evidence,{'operation':'deprecate','key':k,'version':v}):raise GateError('unverified_deprecation')
  return self.engine.deprecate(k,v)
class CanonBuilderGuard:
 def __init__(self,e,v):self.engine,self.verifier=e,v
 def add_experimental(self,k,p):
  if not _valid_key(k) or not _valid_payload(p):raise GateError('invalid_canon_entry')
  return self.engine.add_experimental(k,p)
 def promote_to_canon(self,k,v,evidence):
  if not _valid_key(k) or (v is not None and (type(v) is not int or v<1)):raise GateError('invalid_promotion_target')
  if not _verified(self.verifier,evidence,{'operation':'promote_to_canon','key':k,'version':v}):raise GateError('unverified_promotion')
  return self.engine.promote_to_canon(k,v)
class CognitiveTreatyGuard:
 def __init__(self,e):self.engine=e
 def negotiate(self,parties,p):
  if type(parties) is not list or len(parties)<2 or any(type(x) is not str or not x.strip() for x in parties) or len(set(parties))!=len(parties):raise GateError('invalid_parties')
  if type(p) is not dict or set(p)!={'mode','topics','max_data_sensitivity'}:raise GateError('invalid_treaty_contract')
  if p['mode']!='cooperation' or type(p['topics']) is not list or not p['topics'] or any(type(x) is not str or not x.strip() for x in p['topics']):raise GateError('invalid_treaty_topics')
  if any(x.lower() in ('aggression','unbounded_access') for x in p['topics']):raise GateError('prohibited_topic')
  if type(p['max_data_sensitivity']) is not int or not 0<=p['max_data_sensitivity']<=4:raise GateError('invalid_sensitivity')
  return self.engine.negotiate(parties,p)
class EthicalReviewGuard:
 def __init__(self,e,v):self.engine,self.verifier=e,v
 def submit(self,p):
  if not _valid_payload(p):raise GateError('invalid_review_payload')
  return self.engine.submit(p)
 def _decide(self,op,item_id,reviewer,evidence,notes):
  if type(item_id) is not str or not item_id.startswith('ERB-') or not item_id[4:].isdigit() or type(reviewer) is not str or not reviewer.strip():raise GateError('invalid_reviewer_or_item')
  item=self.engine._items.get(item_id)
  if item is None or item.status!='pending':raise GateError('item_not_pending')
  if not _verified(self.verifier,evidence,{'operation':'ethical_'+op,'item_id':item_id,'reviewer':reviewer}):raise GateError('unverified_ethical_'+op)
  return getattr(self.engine,op)(item_id,reviewer,notes)
 def approve(self,item_id,reviewer,evidence,notes=None):return self._decide('approve',item_id,reviewer,evidence,notes)
 def reject(self,item_id,reviewer,evidence,notes=None):return self._decide('reject',item_id,reviewer,evidence,notes)
