import unittest
from app.runtime.ftmo_v8_historical_evidence import reconcile_v8_regression_log

class V8EvidenceTests(unittest.TestCase):
    def test_empty_log_fails_closed(self):
        e=reconcile_v8_regression_log('')
        self.assertFalse(e.historically_reported_pass)
        self.assertEqual(e.count,0)
    def test_forged_footer_not_enough(self):
        e=reconcile_v8_regression_log('Ran 37 tests in 0.003s\n\nOK\n')
        self.assertFalse(e.historically_reported_pass)
    def test_duplicate_not_accepted(self):
        s='test_one (test_execution_v4.ExecutionTests.test_one) ... ok\n'
        with self.assertRaises(ValueError):
            reconcile_v8_regression_log(s+s)
    def test_unknown_suite_not_certified(self):
        e=reconcile_v8_regression_log('test_one (test_unknown.X.test_one) ... ok\nRan 37 tests in 0.003s\nOK\n')
        self.assertFalse(e.historically_reported_pass)
    def test_nontext_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_v8_regression_log(None)
    def test_no_e2e_promotion(self):
        e=reconcile_v8_regression_log('')
        self.assertFalse(e.source_code_verified)
        self.assertFalse(e.runtime_e2e_certified)
