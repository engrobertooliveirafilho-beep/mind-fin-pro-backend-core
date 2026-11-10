import unittest
from mind_trader.experimental.et665_r377_e2e_phase_b_report import run
class R377(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=run()
    def test_nineteen_executed(self):
        self.assertEqual(self.report["candidate_executed"],19)
        self.assertEqual(len(set(x["agent_id"] for x in self.report["candidate_outputs"])),19)
    def test_real_component_and_dependency(self):
        self.assertEqual(self.report["component"],"monthly_cashflow")
        self.assertEqual(self.report["cross_agent_decision"],"HOLD_SPEND")
    def test_fail_closed_official_hp19(self):
        self.assertEqual(self.report["official_hp19_verified"],0)
        self.assertEqual(self.report["official_hp19_total"],19)
    def test_fail_closed_phase_b(self):
        self.assertEqual(self.report["phase_b_certified"],0)
        self.assertEqual(len(self.report["phase_b_missing_evidence"]),16)
    def test_no_real_execution(self):
        self.assertFalse(self.report["production_modified"])
        self.assertFalse(self.report["strategy_promotion_authorized"])
        self.assertEqual(self.report["real_orders"],"FORBIDDEN")
    def test_deterministic(self):
        self.assertEqual(run()["sha256"],self.report["sha256"])
if __name__=="__main__":unittest.main()
