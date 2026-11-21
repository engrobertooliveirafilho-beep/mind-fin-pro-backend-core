import unittest
from types import SimpleNamespace
from agents_runtime import run_agent,AgentRejected
class Tests(unittest.TestCase):
 def setUp(self):self.calls=[]
 def loader(self,name):
  self.calls.append(name)
  return SimpleNamespace(run_dry=lambda p:{'agent':name,'payload':p})
 def test_dispatch(self):self.assertEqual(run_agent('sec_sentinel',loader=self.loader)['agent'],'app.agents.sec_sentinel')
 def test_distinct(self):self.assertNotEqual(run_agent('sec_sentinel',loader=self.loader)['agent'],run_agent('sec_gatekeeper',loader=self.loader)['agent'])
 def test_empty(self):self.assertEqual(run_agent('sec_sentinel',loader=self.loader)['payload'],{})
 def test_mapping(self):self.assertEqual(run_agent('sec_sentinel',{'x':1},loader=self.loader)['payload'],{'x':1})
 def test_unknown(self):
  with self.assertRaises(AgentRejected):run_agent('unlisted',loader=self.loader)
 def test_injection(self):
  with self.assertRaises(AgentRejected):run_agent('../os',loader=self.loader)
 def test_nonstring(self):
  with self.assertRaises(AgentRejected):run_agent(123,loader=self.loader)
 def test_nonmapping(self):
  with self.assertRaises(AgentRejected):run_agent('sec_sentinel',[],loader=self.loader)
 def test_real_orders(self):
  with self.assertRaises(AgentRejected):run_agent('sec_sentinel',{'real_orders':True},loader=self.loader)
 def test_live(self):
  with self.assertRaises(AgentRejected):run_agent('sec_sentinel',{'live_trading':False},loader=self.loader)
 def test_missing_method(self):
  with self.assertRaises(AgentRejected):run_agent('sec_sentinel',loader=lambda name:SimpleNamespace())
 def test_no_load_on_rejection(self):
  with self.assertRaises(AgentRejected):run_agent('bad',loader=self.loader)
  self.assertEqual(self.calls,[])
if __name__=='__main__':unittest.main()
