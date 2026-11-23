import unittest
from r831_contract import audit, audit_file

class ContractTests(unittest.TestCase):
    def test_alias_import(self):
        self.assertEqual(audit('import importlib as il\nil.import_module("x")')["findings"][0]["resolved"], "importlib.import_module")
    def test_from_import_alias(self):
        self.assertEqual(audit('from importlib import import_module as im\nim("x")')["findings"][0]["resolved"], "importlib.import_module")
    def test_dynamic_fn(self):
        self.assertTrue(audit("fn()")["findings"])
    def test_constructor(self):
        self.assertTrue(audit("cls()")["findings"])
    def test_bridge_report(self):
        self.assertTrue(audit("capability_recovery_report()")["findings"])
    def test_import_rejected(self):
        self.assertTrue(audit("importlib.import_module('x')")["findings"])
    def test_static_not_certified(self):
        self.assertFalse(audit("x=1")["certified"])
    def test_syntax_fail_closed(self):
        self.assertEqual(audit("def (")["error"], "SYNTAX_ERROR")
    def test_missing_file_fail_closed(self):
        self.assertFalse(audit_file("/nonexistent/r831.py")["certified"])
if __name__ == "__main__":
    unittest.main()
