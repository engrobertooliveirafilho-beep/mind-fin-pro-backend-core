import unittest
from r865_registry_reconcile import reconcile
A={'id':'meta.global_agent_mapper','governance':{'auto_run':True},'step_ids':[10,20]}
B={'id':'dev.step_planner_agent','auto_run':True}
class Tests(unittest.TestCase):
 def test_status(self):self.assertEqual(reconcile({'agents':[A,B]})['status'],'reconciled_offline')
 def test_agents(self):self.assertEqual(reconcile({'agents':[A,B]})['agent_count'],2)
 def test_steps(self):self.assertEqual(reconcile({'agents':[A,B]})['unique_step_count'],2)
 def test_requests(self):self.assertEqual(reconcile({'agents':[A,B]})['autorun_requests'],2)
 def test_missing(self):self.assertEqual(reconcile({'agents':[A,B]})['agents_without_steps'],1)
 def test_zero(self):self.assertEqual(reconcile({'agents':[A,B]})['executed'],0)
 def test_no_e2e(self):self.assertFalse(reconcile({'agents':[A,B]})['e2e_certified'])
 def test_no_authority(self):self.assertFalse(reconcile({'agents':[A,B]})['execution_authorized'])
 def test_duplicate(self):self.assertEqual(reconcile({'agents':[A,A]})['status'],'blocked')
 def test_bad(self):self.assertEqual(reconcile(None)['status'],'blocked')
 def test_empty(self):self.assertEqual(reconcile({'agents':[]})['agent_count'],0)
 def test_unique_steps(self):self.assertEqual(reconcile({'agents':[A,dict(B,step_ids=[20])]})['unique_step_count'],2)
if __name__=='__main__':unittest.main()
