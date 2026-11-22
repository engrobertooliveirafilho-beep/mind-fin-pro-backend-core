import unittest
from app.runtime.step239_provenance_gate import assess_step239
class Step239Provenance(unittest.TestCase):
    def test_actual_historical_state(self):
        self.assertEqual(assess_step239({'step':239,'status':'unknown'},'STEP238\nSTEP239\nSTEP240')['state'],'HISTORICAL_UNKNOWN_AND_MISSING')
    def test_never_certified(self):
        self.assertFalse(assess_step239({'step':239,'status':'done'},'')['certified'])
    def test_partial_token_not_accepted(self):
        self.assertEqual(assess_step239({'step':239,'status':'unknown'},'STEP2399')['state'],'CONFLICT_OR_UNVERIFIED')
    def test_missing_inventory(self):
        self.assertEqual(assess_step239({'step':239,'status':'unknown'},'')['state'],'CONFLICT_OR_UNVERIFIED')
    def test_bad_step(self):
        with self.assertRaises(ValueError): assess_step239({'step':238,'status':'unknown'},'STEP239')
    def test_missing_step(self):
        with self.assertRaises(ValueError): assess_step239({},'STEP239')
    def test_bad_inventory(self):
        with self.assertRaises(ValueError): assess_step239({'step':239},None)
    def test_historical_done_not_proof(self):
        self.assertEqual(assess_step239({'step':239,'status':'done'},'STEP239')['state'],'CONFLICT_OR_UNVERIFIED')
