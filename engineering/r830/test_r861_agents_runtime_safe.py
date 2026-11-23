import unittest,importlib.util,sys,threading
from pathlib import Path
P=Path(__file__).with_name('r861_agents_runtime_safe.py')
class Tests(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('r861_isolated',P)
  self.m=importlib.util.module_from_spec(spec)
  spec.loader.exec_module(self.m)
 def test_import_no_threads(self):
  before=threading.active_count()
  self.setUp()
  self.assertEqual(threading.active_count(),before)
 def test_no_scheduler_module(self):self.assertNotIn('app.meta.agents_scheduler',sys.modules)
 def test_start_blocked(self):self.assertEqual(self.m.start_scheduler()['status'],'blocked')
 def test_start_zero(self):self.assertEqual(self.m.start_scheduler()['executed'],0)
 def test_start_args(self):self.assertEqual(self.m.start_scheduler(force=True)['status'],'blocked')
 def test_no_runtime(self):self.assertFalse(self.m.start_scheduler()['runtime_certified'])
 def test_no_integration(self):self.assertFalse(self.m.start_scheduler()['integration_authorized'])
 def test_missing_registry(self):
  old=self.m.REG_PATH
  try:
   self.m.REG_PATH=Path('/definitely_missing_r861.json')
   self.assertEqual(self.m.load_agents_registry(),{'agents':[]})
  finally:self.m.REG_PATH=old
 def test_list_empty(self):
  self.m.load_agents_registry=lambda:{'agents':[]}
  self.assertEqual(self.m.list_agents(),[])
 def test_list_bad(self):
  self.m.load_agents_registry=lambda:{'agents':{}}
  self.assertEqual(self.m.list_agents(),[])
 def test_get_missing(self):
  self.m.list_agents=lambda:[{'id':'meta.x'}]
  self.assertIsNone(self.m.get_agent('meta.y'))
 def test_get_present(self):
  self.m.list_agents=lambda:[{'id':'meta.x'}]
  self.assertEqual(self.m.get_agent('meta.x')['id'],'meta.x')
 def test_proposal_missing(self):
  self.m.get_agent=lambda _:None
  self.assertEqual(self.m.generate_agent_blueprints_for_global_mapper(),[])
 def test_proposal(self):
  self.m.get_agent=lambda _: {'artifacts_produced':{'fields':['x'],'proposal_type':'blueprint'}}
  r=self.m.generate_agent_blueprints_for_global_mapper()
  self.assertEqual(r[0]['__proposal_type'],'blueprint')
  self.assertIn('x',r[0])
 def test_proposal_evolution(self):
  self.m.get_agent=lambda _: {'artifacts_produced':{}}
  self.assertEqual(self.m.generate_step_proposals_for_evolution_agent()[0]['__agent_id'],'meta.autonomous_evolution_agent')
 def test_proposal_archives(self):
  self.m.get_agent=lambda _: {'artifacts_produced':{}}
  self.assertEqual(self.m.generate_archives_agent_proposals()[0]['__agent_id'],'meta.mind_archives_agent_mapper')
if __name__=='__main__':unittest.main()
