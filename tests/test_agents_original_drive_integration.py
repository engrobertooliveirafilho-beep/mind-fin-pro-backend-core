"""Integration regression against original Drive-recovered historical agent implementations."""
import unittest
from app.meta.agents_unified_runtime import run_agent, AgentDispatchError
from app.agents import sec_sentinel, sec_gatekeeper

class OriginalAgentsIntegration(unittest.TestCase):
    def test_sentinel_source_identity(self):
        self.assertEqual(sec_sentinel.AGENT_ID,'sec.sentinel')
    def test_gatekeeper_source_identity(self):
        self.assertEqual(sec_gatekeeper.AGENT_ID,'sec.gatekeeper')
    def test_sentinel_is_historical_stub(self):
        self.assertEqual(sec_sentinel.run_dry({})['status'],'not_implemented')
    def test_gatekeeper_is_historical_stub(self):
        self.assertEqual(sec_gatekeeper.run_dry({})['status'],'not_implemented')
    def test_dispatch_rejects_sentinel_original(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.sentinel',{})
    def test_dispatch_rejects_gatekeeper_original(self):
        with self.assertRaises(AgentDispatchError):run_agent('sec.gatekeeper',{})
if __name__=='__main__':unittest.main()
