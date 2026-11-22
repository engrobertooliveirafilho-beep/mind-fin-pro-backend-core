"""Original Drive V7 evidence-gate regression, plus adversarial type checks."""
import unittest
from app.runtime.certification_gate_v7 import REQUIRED, assess

class GateTests(unittest.TestCase):
    def test_absent_evidence_blocks(self):
        r=assess({},paper_tests_pass=True)
        self.assertFalse(r.release_authorized)
        self.assertEqual(len(r.missing),len(REQUIRED))
        self.assertEqual(r.real_orders,0)
    def test_partial_evidence_blocks(self):
        self.assertFalse(assess({REQUIRED[0]:True},paper_tests_pass=True).release_authorized)
    def test_false_test_blocks_even_if_evidence_complete(self):
        self.assertFalse(assess(dict.fromkeys(REQUIRED,True),paper_tests_pass=False).release_authorized)
    def test_all_verified_allows_gate_only(self):
        self.assertTrue(assess(dict.fromkeys(REQUIRED,True),paper_tests_pass=True).release_authorized)
    def test_reject_unknown_evidence(self):
        with self.assertRaises(ValueError):assess({'fabricated':True},paper_tests_pass=True)
    def test_reject_truthy_strings(self):
        with self.assertRaises(TypeError):assess({REQUIRED[0]:'PASS'},paper_tests_pass=True)

class AdversarialGateTests(unittest.TestCase):
    def test_truthy_string_cannot_authorize_release(self):
        with self.assertRaises(TypeError):
            assess(dict.fromkeys(REQUIRED,True),paper_tests_pass='FAIL')
    def test_numeric_one_cannot_authorize_release(self):
        with self.assertRaises(TypeError):
            assess(dict.fromkeys(REQUIRED,True),paper_tests_pass=1)
    def test_non_mapping_evidence_rejected(self):
        with self.assertRaises(TypeError):
            assess(None,paper_tests_pass=True)
