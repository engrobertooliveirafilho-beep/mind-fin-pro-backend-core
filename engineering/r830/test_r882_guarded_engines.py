import unittest
from unittest.mock import Mock
from r882_guarded_engines import promote, negotiate, approve

class GuardedEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = Mock()
    def test_promotion_without_attestation_blocked(self):
        self.assertEqual(promote(self.engine,'canon:x',1,{'text':'v'}, {})['reason'],'unattested_promotion')
    def test_promotion_with_attestation_still_blocked(self):
        self.assertEqual(promote(self.engine,'canon:x',1,{'text':'v'}, {'verified':True})['reason'],'external_authorization_not_implemented')
    def test_promotion_does_not_call_original(self):
        promote(self.engine,'canon:x',1,{'text':'v'}, {'verified':True}); self.engine.promote_to_canon.assert_not_called()
    def test_bad_key(self):
        self.assertEqual(promote(self.engine,'bad',1,{'text':'v'}, {})['reason'],'invalid_key')
    def test_invalid_version(self):
        self.assertEqual(promote(self.engine,'canon:x',True,{'text':'v'}, {})['reason'],'invalid_version_or_payload')
    def test_treaty_valid_is_review_only(self):
        r=negotiate(self.engine,['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':2});self.assertFalse(r['accepted'])
    def test_treaty_no_original_call(self):
        negotiate(self.engine,['a','b'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':2});self.engine.negotiate.assert_not_called()
    def test_treaty_missing_sensitivity(self):
        self.assertEqual(negotiate(self.engine,['a','b'],{'mode':'cooperation','topics':['metrics']})['reason'],'invalid_proposal')
    def test_treaty_forbidden(self):
        self.assertEqual(negotiate(self.engine,['a','b'],{'mode':'cooperation','topics':['aggression'],'max_data_sensitivity':2})['reason'],'prohibited_topic')
    def test_treaty_duplicate_parties(self):
        self.assertEqual(negotiate(self.engine,['a','a'],{'mode':'cooperation','topics':['metrics'],'max_data_sensitivity':2})['reason'],'invalid_parties')
    def test_ethics_empty_reviewer(self):
        self.assertEqual(approve(self.engine,'ERB-1','',{})['reason'],'invalid_reviewer_or_decision')
    def test_ethics_no_evidence(self):
        self.assertEqual(approve(self.engine,'ERB-1','reviewer',{})['reason'],'unverified_evidence')
    def test_ethics_verified_review_only(self):
        self.assertFalse(approve(self.engine,'ERB-1','reviewer',{'verified':True,'source':'ledger'})['approval_authorized'])
    def test_ethics_does_not_call_original(self):
        approve(self.engine,'ERB-1','reviewer',{'verified':True,'source':'ledger'});self.engine.approve.assert_not_called()
    def test_ethics_bad_id(self):
        self.assertEqual(approve(self.engine,'x','reviewer',{})['reason'],'invalid_item')
    def test_no_dispatch_any_path(self):
        promote(self.engine,'canon:x',1,{'text':'v'},{});negotiate(self.engine,[],{});approve(self.engine,'ERB-1','',{});self.engine.assert_not_called()

if __name__=='__main__':unittest.main()
