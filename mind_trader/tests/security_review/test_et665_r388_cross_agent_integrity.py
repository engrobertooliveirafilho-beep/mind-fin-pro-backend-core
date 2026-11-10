import unittest
from unittest.mock import patch
from mind_trader.experimental import et665_r384_integrated_evidence as m
class R388(unittest.TestCase):
    def test_real_dependency_decision(self):
        r=m.build()
        self.assertEqual(r["cross_agent_decision"],"HOLD_SPEND")
        self.assertEqual(r["official_hp19_certified"],0)
    def test_forged_decision_rejected(self):
        original=m.run
        def tampered():
            r=original();r["cross_agent_decision"]="ALLOW_SPEND";return r
        with patch.object(m,"run",side_effect=tampered):
            with self.assertRaisesRegex(RuntimeError,"unsafe cross-agent decision"):m.build()
    def test_forged_e2e_status_rejected(self):
        original=m.run
        def tampered():
            r=original();r["candidate_e2e_status"]="PASS_FAKE";return r
        with patch.object(m,"run",side_effect=tampered):
            with self.assertRaisesRegex(RuntimeError,"unsafe cross-agent decision"):m.build()
    def test_cross_agent_independent_mismatch_rejected(self):
        original=m.original_e2e_build
        def tampered():
            r=original()
            r["dependent_workflow"]["creative"]["recommendation"]="ALLOW_SPEND"
            return r
        with patch.object(m,"original_e2e_build",side_effect=tampered):
            with self.assertRaisesRegex(RuntimeError,"cross-agent decision mismatch"):m.build()
if __name__=="__main__":unittest.main()
