import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r382_two_original_contracts import audit,SOURCES
class R382(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()
    def test_two_independent_historical_sources(self):
        self.assertEqual(self.report["historical_sources_recovered"],2)
        self.assertEqual(len({x["historical_drive_id"] for x in self.report["comparisons"]}),2)
    def test_nineteen_candidates_reexecuted(self):
        self.assertEqual(self.report["reconstructed_candidates_executed"],19)
    def test_historical_stubs_not_certified(self):
        self.assertTrue(all(x["historical_status"]=="not_implemented" and not x["original_functional_equivalence_verified"] for x in self.report["comparisons"]))
        self.assertEqual(self.report["official_hp19_certified"],0)
        self.assertEqual(self.report["phase_b_certified"],0)
    def test_missing_historical_identity_rejected(self):
        with patch.dict(SOURCES,{"fake.agent":{"drive_id":"fake","kind":"fake","step_count":0}}):
            with self.assertRaises(RuntimeError):audit()
if __name__=="__main__":unittest.main()
