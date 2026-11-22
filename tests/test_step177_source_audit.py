import unittest
from app.runtime.step177_source_audit import audit_step177

class TestStep177Audit(unittest.TestCase):
    def test_original_source(self):
        source = 'from fastapi import APIRouter\nrouter = APIRouter()\n@router.get("/mind/step/177")\ndef run_step_177():\n    return {"version":"step177-v1","step":177,"status":"active"}'
        self.assertEqual(audit_step177(source)['kind'],'STATIC_METADATA_ENDPOINT')
    def test_active_is_not_certified(self):
        self.assertFalse(audit_step177('def run_step_177():\n return {"step":177,"status":"active"}')['certified'])
    def test_nonstatic_not_certified(self):
        self.assertFalse(audit_step177('def run_step_177():\n return compute()')['certified'])
    def test_wrong_step_not_static(self):
        self.assertEqual(audit_step177('def run_step_177():\n return {"step":239,"status":"active"}')['kind'],'UNVERIFIED_IMPLEMENTATION')
    def test_missing_function(self):
        with self.assertRaises(ValueError): audit_step177('x=1')
    def test_duplicate_function(self):
        with self.assertRaises(ValueError): audit_step177('def run_step_177():\n return 1\ndef run_step_177():\n return 2')
    def test_invalid_source(self):
        with self.assertRaises(ValueError): audit_step177('def x(')
    def test_invalid_type(self):
        with self.assertRaises(ValueError): audit_step177(None)
