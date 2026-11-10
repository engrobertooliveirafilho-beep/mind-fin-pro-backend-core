import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r384_integrated_evidence import build
class R384(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=build()
    def test_nineteen_outputs(self):
        self.assertEqual(self.report["candidate_executed"],19)
        self.assertEqual(len(self.report["agent_proofs"]),19)
        self.assertTrue(all(len(x["candidate_output_sha256"])==64 for x in self.report["agent_proofs"]))
    def test_sixteen_independent_blockers(self):
        self.assertEqual(len(self.report["phase_b_fronts"]),16)
        self.assertTrue(all(x=="MISSING" for x in self.report["phase_b_fronts"].values()))
    def test_no_official_certification(self):
        self.assertEqual(self.report["official_hp19_certified"],0)
        self.assertEqual(self.report["phase_b_certified"],0)
        self.assertFalse(self.report["independent_reviewer_approval"])
    def test_no_orders_or_promotion(self):
        self.assertEqual(self.report["real_orders"],"FORBIDDEN")
        self.assertFalse(self.report["promotion_authorized"])
    def test_report_deterministic(self):
        self.assertEqual(build(),self.report)
    def test_mismatched_agent_hash_rejected(self):
        from mind_trader.experimental import et665_r384_integrated_evidence as m
        original=m.provenance
        def tampered():
            p=original()
            p["records"][0]["candidate_output_sha256"]="0"*64
            return p
        with patch.object(m,"provenance",side_effect=tampered):
            with self.assertRaises(RuntimeError):m.build()
if __name__=="__main__":unittest.main()
