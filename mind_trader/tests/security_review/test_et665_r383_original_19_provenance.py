import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r383_original_19_provenance import audit,ORIGINAL_DRIVE_IDS
class R383(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()
    def test_nineteen_historical_sources(self):
        self.assertEqual(self.report["historical_sources_recovered"],19)
        self.assertEqual(len({r["historical_drive_id"] for r in self.report["records"]}),19)
    def test_nineteen_original_stubs(self):
        self.assertEqual(self.report["historical_stubs_observed"],19)
        self.assertTrue(all(r["historical_run_dry_status"]=="not_implemented" for r in self.report["records"]))
    def test_nineteen_candidates_executed(self):
        self.assertEqual(self.report["candidate_modules_executed"],19)
        self.assertTrue(all(len(r["candidate_output_sha256"])==64 for r in self.report["records"]))
    def test_no_false_certification(self):
        self.assertFalse(self.report["official_hp19_membership_verified"])
        self.assertEqual(self.report["official_hp19_certified"],0)
        self.assertEqual(self.report["phase_b_certified"],0)
    def test_duplicate_provenance_rejected(self):
        first,second=list(ORIGINAL_DRIVE_IDS)[:2]
        with patch.dict(ORIGINAL_DRIVE_IDS,{second:ORIGINAL_DRIVE_IDS[first]}):
            with self.assertRaises(RuntimeError):audit()
if __name__=="__main__":unittest.main()
