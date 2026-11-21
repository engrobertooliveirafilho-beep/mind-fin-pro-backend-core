import unittest
from types import SimpleNamespace
from agents_runtime_v3 import run_agent,AgentRejected,AGENTS
class Tests(unittest.TestCase):
 def loader(self,path):
  agent=[k for k,v in AGENTS.items() if path.endswith(v)][0]
  return SimpleNamespace(run_dry=lambda payload:{'agent_id':agent,'status':'ok','received':payload})
 def test_all_five(self):
  for a in AGENTS:self.assertEqual(run_agent(a,loader=self.loader)['agent_id'],a)
 def test_payload(self):self.assertEqual(run_agent('sec.sentinel',{'x':[1,2]},loader=self.loader)['received'],{'x':[1,2]})
 def test_original_stub(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','status':'not_implemented','mode':'stub'}))
 def test_no_status(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel'}))
 def test_unknown(self):
  with self.assertRaises(AgentRejected):run_agent('unknown',loader=self.loader)
 def test_dotted_path_injection(self):
  with self.assertRaises(AgentRejected):run_agent('sec.__dict__',loader=self.loader)
 def test_nested_forbidden(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',{'nested':[{'REAL_ORDERS':False}]},loader=self.loader)
 def test_cycle(self):
  d={};d['self']=d
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',d,loader=self.loader)
 def test_depth(self):
  d={};v=d
  for _ in range(18):v['a']={};v=v['a']
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',d,loader=self.loader)
 def test_nonstring_key(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',{1:'x'},loader=self.loader)
 def test_unsupported_object(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',{'x':object()},loader=self.loader)
 def test_exception(self):
  def broken(p):raise RuntimeError('sensitive details')
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=broken))
 def test_wrong_id(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.gatekeeper','status':'ok'}))
 def test_missing_method(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace())
 def test_failed_status(self):
  with self.assertRaises(AgentRejected):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','status':'failed'}))
 def test_bool_id(self):
  with self.assertRaises(AgentRejected):run_agent(True,loader=self.loader)
if __name__=='__main__':unittest.main()
