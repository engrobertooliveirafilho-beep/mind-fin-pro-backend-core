import unittest
from app.runtime.step_source_evidence_gate import inspect_step_source

class Gate(unittest.TestCase):
    def test_original_stub_124(self):
        self.assertEqual(inspect_step_source(124,'STEP_ID=124\nSTEP_STATUS="approved_stub"')['source_status'],'NOT_IMPLEMENTED')
    def test_original_stub_136(self):
        self.assertFalse(inspect_step_source(136,'STEP_ID=136\nSTEP_STATUS="approved_stub"')['certified'])
    def test_original_stub_170(self):
        self.assertFalse(inspect_step_source(170,'STEP_ID=170\nSTEP_STATUS="approved_stub"')['certified'])
    def test_implemented_not_certified(self):
        self.assertEqual(inspect_step_source(124,'STEP_ID=124\nSTEP_STATUS="implemented"')['source_status'],'IMPLEMENTATION_CLAIM')
    def test_wrong_identity(self):
        with self.assertRaises(ValueError): inspect_step_source(124,'STEP_ID=136\nSTEP_STATUS="implemented"')
    def test_dynamic_status_denied(self):
        self.assertFalse(inspect_step_source(124,'STEP_ID=124\nSTEP_STATUS=get_status()')['certified'])
    def test_duplicate_status_denied(self):
        self.assertFalse(inspect_step_source(124,'STEP_ID=124\nSTEP_STATUS="implemented"\nSTEP_STATUS="approved_stub"')['certified'])
    def test_syntax_denied(self):
        with self.assertRaises(ValueError): inspect_step_source(124,'STEP_ID=')
    def test_missing_id_denied(self):
        with self.assertRaises(ValueError): inspect_step_source(124,'STEP_STATUS="implemented"')
