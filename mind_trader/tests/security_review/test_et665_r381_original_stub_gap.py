import unittest
from mind_trader.experimental.et665_r381_original_stub_gap import audit,classify_original,ORIGINAL_RUN_DRY_SOURCE
class R381(unittest.TestCase):
    def test_historical_original_stub(self):
        self.assertTrue(classify_original(ORIGINAL_RUN_DRY_SOURCE)["stub"])
    def test_historical_stub_not_functional(self):
        self.assertEqual(classify_original(ORIGINAL_RUN_DRY_SOURCE)["status"],"not_implemented")
    def test_reconstructed_candidate_does_process(self):
        self.assertTrue(audit()["reconstructed_candidate_processed"])
    def test_official_certification_blocked(self):
        r=audit()
        self.assertFalse(r["original_functional_equivalence_verified"])
        self.assertEqual(r["official_hp19_certified"],0)
        self.assertEqual(r["phase_b_certified"],0)
if __name__=="__main__":unittest.main()
