import unittest
from app.runtime.step497_498_mock_guard import classify_pipeline,classify_ceo_briefing
class MockGuard(unittest.TestCase):
    def test_497_historical_mock(self): self.assertEqual(classify_pipeline({'version':'step497-v1','status':'ok'})['state'],'HISTORICAL_MOCK_DATA')
    def test_497_live_claim_cannot_override(self): self.assertFalse(classify_pipeline({'version':'step497-v1'},verified_live_source=True)['certified'])
    def test_497_unknown(self): self.assertEqual(classify_pipeline({'version':'other'})['state'],'UNVERIFIED')
    def test_497_invalid(self):
        with self.assertRaises(ValueError): classify_pipeline(None)
    def test_497_bad_flag(self):
        with self.assertRaises(ValueError): classify_pipeline({},verified_live_source=1)
    def test_498_mock_contamination(self):
        self.assertEqual(classify_ceo_briefing({'version':'step498-v1','pipeline':{'version':'step497-v1'}})['state'],'MOCK_CONTAMINATED_BRIEFING')
    def test_498_missing_pipeline(self): self.assertEqual(classify_ceo_briefing({'version':'step498-v1'})['state'],'INCOMPLETE_DEPENDENCIES')
    def test_498_unknown_pipeline(self): self.assertEqual(classify_ceo_briefing({'version':'step498-v1','pipeline':{}})['state'],'UNVERIFIED_DEPENDENCIES')
    def test_498_invalid(self):
        with self.assertRaises(ValueError): classify_ceo_briefing(None)
