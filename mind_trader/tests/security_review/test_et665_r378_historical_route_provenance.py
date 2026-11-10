import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r378_historical_route_provenance import audit,HISTORICAL_FIRST_19
class R378(unittest.TestCase):
    def test_historical_route_match(self):
        r=audit()
        self.assertEqual(r["matched_candidates"],19)
        self.assertEqual(r["status"],"HISTORICAL_ROUTE_IDENTITY_MATCH")
    def test_no_official_certification(self):
        r=audit()
        self.assertFalse(r["official_hp19_membership_verified"])
        self.assertEqual(r["official_hp19_certified"],0)
        self.assertEqual(r["phase_b_certified"],0)
    def test_dispatcher_tampering_rejected(self):
        with patch("mind_trader.experimental.et665_r378_historical_route_provenance.AGENT_MODULES",("fake",)*19):
            with self.assertRaises(RuntimeError):audit()
    def test_historical_source_has_nineteen_unique_names(self):
        self.assertEqual(len(HISTORICAL_FIRST_19),19)
        self.assertEqual(len(set(HISTORICAL_FIRST_19)),19)
if __name__=="__main__":unittest.main()
