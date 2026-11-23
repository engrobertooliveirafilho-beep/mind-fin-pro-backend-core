import unittest
from r844_step_planner import run_dry,describe_capabilities
S={'id':10,'title':'memory','approved':True,'source_sha256':'a'*64}
class TestPlanner(unittest.TestCase):
 def test_id(self):self.assertEqual(describe_capabilities()['id'],'dev.step_planner_agent')
 def test_empty(self):self.assertEqual(run_dry()['status'],'blocked')
 def test_bad_payload(self):self.assertEqual(run_dry([])['status'],'blocked')
 def test_good(self):self.assertEqual(run_dry({'approved_steps':[S]})['status'],'planned')
 def test_not_certified(self):self.assertFalse(run_dry({'approved_steps':[S]})['runtime_certified'])
 def test_not_integrated(self):self.assertFalse(run_dry({'approved_steps':[S]})['integration_authorized'])
 def test_unapproved(self):self.assertEqual(run_dry({'approved_steps':[dict(S,approved=False)]})['status'],'blocked')
 def test_hash(self):self.assertEqual(run_dry({'approved_steps':[dict(S,source_sha256='x')]})['status'],'blocked')
 def test_duplicate(self):self.assertEqual(run_dry({'approved_steps':[S,S]})['status'],'blocked')
 def test_schema(self):self.assertEqual(run_dry({'approved_steps':[dict(S,extra=1)]})['status'],'blocked')
 def test_limit(self):self.assertEqual(run_dry({'approved_steps':[S]*101})['reason'],'batch_limit')
 def test_bool(self):self.assertEqual(run_dry({'approved_steps':[dict(S,id=True)]})['status'],'blocked')
 def test_title(self):self.assertEqual(run_dry({'approved_steps':[dict(S,title=' ')]})['status'],'blocked')
 def test_paths(self):self.assertEqual(run_dry({'approved_steps':[S]})['plans'][0]['test_path'],'tests/test_step_0010.py')
 def test_atomic(self):self.assertNotIn('plans',run_dry({'approved_steps':[S,dict(S,id=11,approved=False)]}))
 def test_mode(self):self.assertEqual(describe_capabilities()['mode'],'offline_planning_only')
if __name__=='__main__':unittest.main()
