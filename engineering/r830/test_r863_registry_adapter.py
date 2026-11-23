import unittest
from r863_registry_adapter import adapt
A={'id':'meta.global_agent_mapper','governance':{'auto_run':True},'step_ids':[10,20]}
def go(a=None,**kw):return adapt({'agents':[A] if a is None else a},**kw)
class Test(unittest.TestCase):
 def test_good(self):self.assertEqual(go()['status'],'planned_only')
 def test_steps(self):self.assertEqual(go()['agents'][0]['step_ids'],[10,20])
 def test_auto_not_execute(self):self.assertFalse(go()['agents'][0]['executed'])
 def test_total_zero(self):self.assertEqual(go()['executed'],0)
 def test_not_cert(self):self.assertFalse(go()['e2e_certified'])
 def test_no_paper(self):self.assertEqual(go(paper_only=False)['status'],'blocked')
 def test_bad_registry(self):self.assertEqual(adapt(None)['status'],'blocked')
 def test_bad_agents(self):self.assertEqual(adapt({'agents':{}})['status'],'blocked')
 def test_empty(self):self.assertEqual(go([])['status'],'planned_only')
 def test_duplicate(self):self.assertEqual(go([A,A])['status'],'blocked')
 def test_bad_id(self):self.assertEqual(go([dict(A,id='bad')])['status'],'blocked')
 def test_bad_governance(self):self.assertEqual(go([dict(A,governance={'auto_run':1})])['status'],'blocked')
 def test_bad_step(self):self.assertEqual(go([dict(A,step_ids=[True])])['status'],'blocked')
 def test_bad_record(self):self.assertEqual(go([None])['status'],'blocked')
 def test_limit(self):self.assertEqual(go([A]*1001)['reason'],'limit')
 def test_no_steps(self):self.assertEqual(go([dict(A,step_ids=[])])['status'],'planned_only')
if __name__=='__main__':unittest.main()
