import unittest
from types import SimpleNamespace
from agents_runtime_v2 import run_agent, AgentRejected

class AgentTests(unittest.TestCase):
    def loader(self, path):
        return SimpleNamespace(run_dry=lambda p: {'agent_id': 'sec.sentinel', 'status':'ok', 'received':p})
    def test_dotted_id(self): self.assertEqual(run_agent('sec.sentinel',loader=self.loader)['agent_id'],'sec.sentinel')
    def test_payload(self): self.assertEqual(run_agent('sec.sentinel',{'x':1},loader=self.loader)['received'],{'x':1})
    def test_reject_underscore_alias(self):
        with self.assertRaises(AgentRejected): run_agent('sec_sentinel',loader=self.loader)
    def test_unknown(self):
        with self.assertRaises(AgentRejected): run_agent('sec.unknown',loader=self.loader)
    def test_traversal(self):
        with self.assertRaises(AgentRejected): run_agent('../os',loader=self.loader)
    def test_nested_real_order(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',{'nested':[{'real_orders':True}]},loader=self.loader)
    def test_case_insensitive_forbidden(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',{'FTMO_REAL':False},loader=self.loader)
    def test_missing_method(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',loader=lambda _:SimpleNamespace())
    def test_identity_mismatch(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.gatekeeper'}))
    def test_original_stub_rejected(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','status':'not_implemented','mode':'stub'}))
    def test_error_rejected(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','error':'failure'}))
    def test_non_dict_result(self):
        with self.assertRaises(AgentRejected): run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:'ok'))
    def test_no_call_when_invalid(self):
        called=[]
        with self.assertRaises(AgentRejected):run_agent('bad',loader=lambda path:called.append(path))
        self.assertEqual(called,[])
    def test_nonmapping_payload(self):
        with self.assertRaises(AgentRejected):run_agent('sec.sentinel',[],loader=self.loader)
if __name__=='__main__': unittest.main()
