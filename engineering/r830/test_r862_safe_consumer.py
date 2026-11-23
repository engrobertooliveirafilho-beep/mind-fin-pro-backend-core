import unittest
from r862_safe_consumer import plan
ID='meta.global_agent_mapper'
A={'id':ID,'artifacts_produced':{'fields':['name','role']}}
def p(agents=None,**kw):return plan(ID,{'agents':[A] if agents is None else agents},**kw)
class Tests(unittest.TestCase):
 def test_planned(self):self.assertEqual(p()['status'],'planned')
 def test_fields(self):self.assertEqual(p()['proposal_fields'],['name','role'])
 def test_zero(self):self.assertEqual(p()['executed'],0)
 def test_not_e2e(self):self.assertFalse(p()['certified_e2e'])
 def test_paper(self):self.assertEqual(p(paper_only=False)['status'],'blocked')
 def test_unknown(self):self.assertEqual(plan('meta.unknown',{'agents':[A]})['status'],'blocked')
 def test_bad_id(self):self.assertEqual(plan([],{'agents':[A]})['status'],'blocked')
 def test_duplicate(self):self.assertEqual(p([A,A])['status'],'blocked')
 def test_missing(self):self.assertEqual(p([])['status'],'blocked')
 def test_invalid_contract(self):self.assertEqual(p([{'id':ID}])['status'],'blocked')
 def test_invalid_field(self):self.assertEqual(p([{'id':ID,'artifacts_produced':{'fields':['__proposal_type']}}])['status'],'blocked')
 def test_duplicate_field(self):self.assertEqual(p([{'id':ID,'artifacts_produced':{'fields':['x','x']}}])['status'],'blocked')
 def test_bad_agent(self):self.assertEqual(p([A,1])['status'],'blocked')
 def test_batch(self):self.assertEqual(p([A]*101)['status'],'blocked')
 def test_empty_fields(self):self.assertEqual(p([{'id':ID,'artifacts_produced':{'fields':[]}}])['status'],'planned')
 def test_other_agent(self):self.assertEqual(plan('meta.autonomous_evolution_agent',{'agents':[dict(A,id='meta.autonomous_evolution_agent')]})['status'],'planned')
 def test_no_io(self):self.assertEqual(p()['source'],'registry_contract_only')
 def test_invalid_registry(self):self.assertEqual(plan(ID,None)['status'],'blocked')
if __name__=='__main__':unittest.main()
