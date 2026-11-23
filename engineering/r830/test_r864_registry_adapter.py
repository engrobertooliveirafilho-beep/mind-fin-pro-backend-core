import unittest
from r864_registry_adapter import adapt
A={'id':'dev.step_planner_agent','governance':{'auto_run':True},'step_ids':[10]}
class Test(unittest.TestCase):
 def test_base(self):self.assertEqual(adapt({'agents':[A]})['status'],'planned_only')
 def test_missing_steps(self):self.assertEqual(adapt({'agents':[{'id':'cog.self_optimizer','auto_run':True}]})['status'],'planned_only')
 def test_missing_governance(self):self.assertEqual(adapt({'agents':[{'id':'cog.self_optimizer'}]})['agents'][0]['auto_run_recorded'],None)
 def test_zero(self):self.assertEqual(adapt({'agents':[A]})['executed'],0)
 def test_no_e2e(self):self.assertFalse(adapt({'agents':[A]})['e2e_certified'])
 def test_bad_id(self):self.assertEqual(adapt({'agents':[{'id':'bad'}]})['status'],'blocked')
 def test_duplicate(self):self.assertEqual(adapt({'agents':[A,A]})['status'],'blocked')
 def test_bad_step(self):self.assertEqual(adapt({'agents':[dict(A,step_ids=[True])]})['status'],'blocked')
 def test_bad_gov(self):self.assertEqual(adapt({'agents':[dict(A,governance=1)]})['status'],'blocked')
 def test_bad_autorun(self):self.assertEqual(adapt({'agents':[dict(A,auto_run=1,governance={})]})['status'],'blocked')
 def test_missing_registry(self):self.assertEqual(adapt(None)['status'],'blocked')
 def test_empty(self):self.assertEqual(adapt({'agents':[]})['status'],'planned_only')
if __name__=='__main__':unittest.main()
