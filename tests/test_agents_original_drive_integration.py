"""Integration regression against original Drive-recovered historical agent implementations."""
import unittest
from app.meta.agents_unified_runtime import run_agent, AgentDispatchError
from app.agents import sec_sentinel, sec_gatekeeper, domain_economics_finance_markets, core_safety_compliance_hub, dev_test_guardian_agent

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
    def test_finance_steps_original(self):
        self.assertEqual(domain_economics_finance_markets.STEP_IDS,[124,136,139,154,170,177,190,210,211,239,281,497,498])
    def test_safety_steps_original(self):
        self.assertEqual(len(core_safety_compliance_hub.STEP_IDS),23)
    def test_five_originals_are_stubs(self):
        for module in (sec_sentinel,sec_gatekeeper,domain_economics_finance_markets,core_safety_compliance_hub,dev_test_guardian_agent):
            with self.subTest(agent=module.AGENT_ID):
                self.assertEqual(module.run_dry({})['status'],'not_implemented')
                self.assertEqual(module.run_dry({})['mode'],'stub')
    def test_five_originals_fail_closed_in_dispatch(self):
        for module in (sec_sentinel,sec_gatekeeper,domain_economics_finance_markets,core_safety_compliance_hub,dev_test_guardian_agent):
            with self.subTest(agent=module.AGENT_ID):
                with self.assertRaises(AgentDispatchError):run_agent(module.AGENT_ID,{})
if __name__=='__main__':unittest.main()

