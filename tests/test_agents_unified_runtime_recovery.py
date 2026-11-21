"""Offline contract regression for recovered 52-agent dispatcher."""
import unittest
from types import SimpleNamespace
from app.meta.agents_unified_runtime import AGENT_IDS, AgentDispatchError, run_agent

class DispatchTests(unittest.TestCase):
    def loader(self, path):
        agent=path[len('app.agents.'):].replace('_','.',1)
        # Map the original prefix only, preserving underscores in the suffix.
        return SimpleNamespace(run_dry=lambda payload:{'agent_id':agent,'status':'ok','mode':'dry_run','payload':payload})
    def test_inventory(self): self.assertEqual(len(AGENT_IDS),52)
    def test_all_registered(self):
        for agent in AGENT_IDS:
            with self.subTest(agent=agent):
                self.assertEqual(run_agent(agent,loader=self.loader)['agent_id'],agent)
    def test_stub_rejected(self):
        with self.assertRaises(AgentDispatchError):
            run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','status':'not_implemented','mode':'stub'}))
    def test_wrong_agent(self):
        with self.assertRaises(AgentDispatchError):
            run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.gatekeeper','status':'ok','mode':'dry_run'}))
    def test_unregistered(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.other',loader=self.loader)
    def test_real_order(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',{'real_orders':False},loader=self.loader)
    def test_nested_order(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',{'x':[{'submit_order':1}]},loader=self.loader)
    def test_cycle(self):
        payload={};payload['self']=payload
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',payload,loader=self.loader)
    def test_missing_mode(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',loader=lambda _:SimpleNamespace(run_dry=lambda p:{'agent_id':'sec.sentinel','status':'ok'}))
    def test_missing_module(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',loader=lambda _:(_ for _ in ()).throw(ImportError()))
if __name__=='__main__':unittest.main()
