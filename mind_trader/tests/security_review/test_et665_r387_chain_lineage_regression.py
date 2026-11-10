import unittest
from unittest.mock import patch
from mind_trader.experimental import et665_r384_integrated_evidence as m
class R387(unittest.TestCase):
    def test_independent_chain_baseline(self):
        self.assertEqual(m.build()["candidate_executed"],19)
    def test_chain_only_tampering_rejected(self):
        original=m.run
        def tamper():
            r=original();r["candidate_chain_sha256"]="0"*64;return r
        with patch.object(m,"run",side_effect=tamper):
            with self.assertRaisesRegex(RuntimeError,"chain digest mismatch"):m.build()
    def test_input_lineage_tampering_rejected(self):
        original=m.run
        def tamper():
            r=original();r["input_sha256"]="0"*64;return r
        with patch.object(m,"run",side_effect=tamper):
            with self.assertRaisesRegex(RuntimeError,"input lineage mismatch"):m.build()
    def test_duplicate_output_identity_rejected(self):
        original=m.run
        def tamper():
            r=original();r["candidate_outputs"][0]["agent_id"]=r["candidate_outputs"][1]["agent_id"];return r
        with patch.object(m,"run",side_effect=tamper):
            with self.assertRaises(RuntimeError):m.build()
    def test_no_official_certification(self):
        r=m.build()
        self.assertEqual((r["official_hp19_certified"],r["phase_b_certified"]),(0,0))
        self.assertEqual(r["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
