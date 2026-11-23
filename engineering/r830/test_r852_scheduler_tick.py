import unittest
from r852_scheduler_tick import run_tick
def entry(i,auto=True):return {'id':i,'governance':{'auto_run':auto}}
class SchedulerTests(unittest.TestCase):
 def test_valid(self):self.assertEqual(run_tick([entry('a')],lambda *a:None)['status'],'planned')
 def test_no_execution(self):
  calls=[]
  out=run_tick([entry('a')],lambda *a:calls.append(a))
  self.assertEqual(calls,[]);self.assertEqual(out['executed'],0)
 def test_disabled(self):self.assertEqual(run_tick([entry('a',False)],lambda *a:None)['agent_ids'],[])
 def test_offline(self):self.assertEqual(run_tick([],lambda *a:None,dry_run=False)['status'],'blocked')
 def test_bad_registry(self):self.assertEqual(run_tick(None,lambda *a:None)['status'],'blocked')
 def test_bad_dispatch(self):self.assertEqual(run_tick([],None)['status'],'blocked')
 def test_duplicate(self):self.assertEqual(run_tick([entry('a'),entry('a')],lambda *a:None)['status'],'blocked')
 def test_bad_entry(self):self.assertEqual(run_tick(['a'],lambda *a:None)['status'],'blocked')
 def test_extra_key(self):self.assertEqual(run_tick([dict(entry('a'),extra=1)],lambda *a:None)['status'],'blocked')
 def test_bad_governance(self):self.assertEqual(run_tick([{'id':'a','governance':[]}],lambda *a:None)['status'],'blocked')
 def test_bad_bool(self):self.assertEqual(run_tick([entry('a',1)],lambda *a:None)['status'],'blocked')
 def test_empty_id(self):self.assertEqual(run_tick([entry('')],lambda *a:None)['status'],'blocked')
 def test_not_integrated(self):self.assertFalse(run_tick([],lambda *a:None)['integration_authorized'])
 def test_not_certified(self):self.assertFalse(run_tick([],lambda *a:None)['runtime_certified'])
 def test_order(self):self.assertEqual(run_tick([entry('b'),entry('a')],lambda *a:None)['agent_ids'],['b','a'])
 def test_limit(self):self.assertEqual(run_tick([entry(str(i)) for i in range(101)],lambda *a:None)['reason'],'batch_limit')
if __name__=='__main__':unittest.main()
