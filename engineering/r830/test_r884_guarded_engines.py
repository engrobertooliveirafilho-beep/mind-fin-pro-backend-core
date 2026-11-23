import unittest
from unittest.mock import Mock
from originals import KnowledgeLifecycleManager,CanonBuilder,CognitiveTreatyProtocol,EthicalReviewBoard
from r884_guarded_engines import *
E={'sha256':'a'*64,'source':'signed-ledger'}
def verifier(e,s):return e is E and s.get('operation') in {'promote_to_canon','ethical_approve','ethical_reject','deprecate'}
class Tests(unittest.TestCase):
 def setUp(self):self.k=KnowledgeLifecycleGuard(KnowledgeLifecycleManager());self.c=CanonBuilderGuard(CanonBuilder(),verifier);self.t=CognitiveTreatyGuard(CognitiveTreatyProtocol());self.e=EthicalReviewGuard(EthicalReviewBoard(),verifier)
 def test01(self):self.assertEqual(self.k.create('canon:x',{'v':1}).version,1)
 def test02(self):
  with self.assertRaises(GateError):self.k.create('',{'v':1})
 def test03(self):
  with self.assertRaises(GateError):self.k.create('canon:x',[])
 def test04(self):
  self.k.create('canon:x',{'v':1})
  with self.assertRaises(GateError):self.k.deprecate('canon:x',1,{},verifier)
 def test05(self):self.k.create('canon:x',{'v':1});self.k.deprecate('canon:x',1,E,verifier);self.assertIsNone(self.k.engine.get_latest_active('canon:x'))
 def test06(self):self.assertEqual(self.c.add_experimental('mind:x',{'v':1}).status,'experimental')
 def test07(self):
  self.c.add_experimental('mind:x',{'v':1})
  with self.assertRaises(GateError):self.c.promote_to_canon('mind:x',1,{})
 def test08(self):
  self.c.add_experimental('mind:x',{'v':1})
  with self.assertRaises(GateError):self.c.promote_to_canon('mind:x',1,{'sha256':'bad','source':'x'})
 def test09(self):self.c.add_experimental('mind:x',{'v':1});self.assertEqual(self.c.promote_to_canon('mind:x',1,E).status,'canon')
 def test10(self):self.assertEqual(self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':3}).status,'accepted')
 def test11(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics']})
 def test12(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':5})
 def test13(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','a'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':2})
 def test14(self):
  with self.assertRaises(GateError):self.t.negotiate(['a','b'],{'mode':'cooperation','topics':['aggression'],'max_data_sensitivity':2})
 def test15(self):self.assertEqual(self.e.submit({'risk':'high'}).status,'pending')
 def test16(self):
  i=self.e.submit({'risk':'high'})
  with self.assertRaises(GateError):self.e.approve(i.item_id,'',E)
 def test17(self):
  i=self.e.submit({'risk':'high'})
  with self.assertRaises(GateError):self.e.approve(i.item_id,'reviewer',{})
 def test18(self):i=self.e.submit({'risk':'high'});self.assertEqual(self.e.approve(i.item_id,'reviewer',E).status,'approved')
 def test19(self):
  i=self.e.submit({'risk':'high'});self.e.approve(i.item_id,'reviewer',E)
  with self.assertRaises(GateError):self.e.approve(i.item_id,'reviewer',E)
 def test20(self):
  engine=Mock();g=CanonBuilderGuard(engine,verifier)
  with self.assertRaises(GateError):g.promote_to_canon('mind:x',1,{})
  engine.promote_to_canon.assert_not_called()
if __name__=='__main__':unittest.main(verbosity=2)
