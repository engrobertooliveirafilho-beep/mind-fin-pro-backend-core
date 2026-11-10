import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r380_identity_bound_execution import verify
class R380(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=verify()
    def test_nineteen_identity_bound(self):
        self.assertEqual(self.report["candidate_executed"],19)
        self.assertEqual(len(set(p["module"] for p in self.report["proof"])),19)
    def test_evidence_per_module(self):
        self.assertTrue(all(len(p["output_sha256"])==64 for p in self.report["proof"]))
    def test_no_official_certification(self):
        self.assertEqual(self.report["official_hp19_certified"],0)
        self.assertEqual(self.report["phase_b_certified"],0)
    def test_no_external_execution(self):
        self.assertEqual(self.report["real_orders"],"FORBIDDEN")
        self.assertFalse(self.report["production_modified"])
    def test_swapped_executor_rejected(self):
        from mind_trader.experimental import et665_r380_identity_bound_execution as m
        original=m.import_module
        def swapped(path):
            if path=="app.agents.cognition_os_kernel_agent":
                return original("app.agents.business_strategy_cashflow_agent")
            return original(path)
        with patch.object(m,"import_module",side_effect=swapped):
            with self.assertRaises(RuntimeError):m.verify()
if __name__=="__main__":unittest.main()
