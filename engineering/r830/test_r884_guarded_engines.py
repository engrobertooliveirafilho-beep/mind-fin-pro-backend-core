import unittest
from unittest.mock import Mock
from r884_guarded_engines import *

E={'sha256':'a'*64,'source':'signed-ledger'}
def verifier(e, scope): return e is E and scope.get('operation') in {'promote_to_canon','ethical_approve','ethical_reject','deprecate'}

class R884Tests(unittest.TestCase):
 def setUp(self):
  from originals import KnowledgeLifecycleManager,CanonBuilder,CognitiveTreatyProtocol,EthicalReviewBoard
  self.k=KnowledgeLifecycleGuard(KnowledgeLifecycleManager());self.c=CanonBuilderGuard(CanonBuilder(),verifier);self.t=CognitiveTreatyGuard(CognitiveTreatyProtocol());self.e=EthicalReviewGuard(EthicalReviewBoard(),verifier)
 def test_knowledge_legacy_create(self): self.assertEqual(self.k.create('canon:x',{'v':1}).version,1)
 def test_knowledge_reject_empty_key(self):
  with self.assertRaises(GateError):self.k.create('',{'v':1})
 def test_knowledge_reject_non_dict(self):
  with self.assertRaises(GateError):self.k.create('canon:x',[])
 def test_deprecate_no_evidence(self):
  self.k.create('canon:x',{'v':1})
  with self.assertRaises(GateError):self.k.deprecate('canon:x',1,{},verifier)
 def test_deprecate_verified(self):
  self.k.create('canon:x',{'v':1});self.k.deprecate('canon:x',1,E,verifier);self.assertIsNone(self.k.engine.get_latest_active('canon:x'))
 def test_canon_add_experimental(self): self.assertEqual(self.c.add_experimental('mind:x',{'v':1}).status,'experimental')
 def test_canon_promote_no_evidence(self):
  self.c.add_experimental('mind:x',{'v':1})
  with self.assertRaises(GateError):self.c.promote_to_canon('mind:x',1,{})
 def test_canon_promote_bad_digest(self):
  self.c.add_experimental('mind:x',{'v':1})
  with self.assertRaises(GateError):self.c.promote_to_canon('mind:x',1,{'sha256':'bad','source':'x'})
 def test_canon_promote_verified(self):
  self.c.add_experimental('mind:x',{'v':1});self.assertEqual(self.c.promote_to_canon('mind:x',1,E).status,'canon')
 def test_treaty_legacy_valid(self):
  r=self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':3});self.assertEqual(r.status,'accepted')
 def test_treaty_missing_sensitivity(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics']})
 def test_treaty_bad_sensitivity(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':5})
 def test_treaty_duplicate_parties(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','a'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':2})
 def test_treaty_forbidden(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['aggression'],'max_data_sensitivity':2})
 def test_ethics_submit(self):self.assertEqual(self.e.submit({'risk':'high'}).status,'pending')
 def test_ethics_empty_reviewer(self):
  i=self.e.submit({'risk':'high'})
  with self.assertRaises(GateError):self.e.approve(i.item_id,'',E)
 def test_ethics_no_evidence(self):
  i=self.e.submit({'risk':'high'})
  with self.assertRaises(GateError):self.e.approve(i.item_id,'reviewer',{})
 def test_ethics_verified_approve(self):
  i=self.e.submit({'risk':'high'});self.assertEqual(self.e.approve(i.item_id,'reviewer',E).status,'approved')
 def test_ethics_double_approve(self):
  i=self.e.submit({'risk':'high'});self.e.approve(i.item_id,'reviewer',E)
  with self.assertRaises(GateError):self.e.approve(i.item_id,'reviewer',E)
 def test_no_original_promotion_without_gate(self):
  engine=Mock();guard=CanonBuilderGuard(engine,verifier)
  with self.assertRaises(GateError):guard.promote_to_canon('mind:x',1,{})
  engine.promote_to_canon.assert_not_called()
 def test_verifier_exception_fails_closed(self):
  engine=Mock();guard=CanonBuilderGuard(engine,lambda *_:1/0)
  with self.assertRaises(GateError):guard.promote_to_canon('mind:x',1,E)
  engine.promote_to_canon.assert_not_called()
if __name__=='__main__':unittest.main(verbosity=2)
