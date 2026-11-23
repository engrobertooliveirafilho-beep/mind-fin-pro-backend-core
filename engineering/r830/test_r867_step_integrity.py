import unittest
from r867_step_integrity import audit
A={'id':'meta.global_agent_mapper','step_ids':[10,20]}
B={'id':'dev.step_planner_agent','step_ids':[10]}
class Tests(unittest.TestCase):
 def test_status(self): self.assertEqual(audit({'agents':[A,B]})['status'],'audited_only')
 def test_agents(self): self.assertEqual(audit({'agents':[A,B]})['agent_count'],2)
 def test_steps(self): self.assertEqual(audit({'agents':[A,B]})['step_count'],2)
 def test_links(self): self.assertEqual(audit({'agents':[A,B]})['links'],3)
 def test_unmapped(self): self.assertEqual(audit({'agents':[A,dict(B,step_ids=[])]})['unmapped_agents'],1)
 def test_no_execution(self): self.assertEqual(audit({'agents':[A]})['executed'],0)
 def test_not_e2e(self): self.assertFalse(audit({'agents':[A]})['e2e_certified'])
 def test_empty(self): self.assertEqual(audit({'agents':[]})['links'],0)
 def test_invalid_registry(self): self.assertEqual(audit(None)['status'],'blocked')
 def test_duplicate_agent(self): self.assertEqual(audit({'agents':[A,A]})['status'],'blocked')
 def test_duplicate_step(self): self.assertEqual(audit({'agents':[dict(A,step_ids=[10,10])]})['status'],'blocked')
 def test_bool_step(self): self.assertEqual(audit({'agents':[dict(A,step_ids=[True])]})['status'],'blocked')
 def test_invalid_id(self): self.assertEqual(audit({'agents':[dict(A,id='../bad')]})['status'],'blocked')
 def test_missing_steps(self): self.assertEqual(audit({'agents':[{'id':'meta.empty'}]})['status'],'audited_only')
 def test_string_steps(self): self.assertEqual(audit({'agents':[dict(A,step_ids='10')]})['status'],'blocked')
 def test_too_many(self): self.assertEqual(audit({'agents':[A]*1001})['status'],'blocked')
if __name__=='__main__':unittest.main()
