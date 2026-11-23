import unittest
from r830_safe_consumer_audit import audit_source, audit_paths

class R830Tests(unittest.TestCase):
    def test_import_is_rejected(self):
        self.assertFalse(audit_source("importlib.import_module('x')")["safe"])
    def test_function_call_rejected(self):
        self.assertFalse(audit_source("fn()")["safe"])
    def test_constructor_rejected(self):
        self.assertFalse(audit_source("cls()")["safe"])
    def test_bridge_consumer_rejected(self):
        self.assertFalse(audit_source("capability_recovery_report()")["safe"])
    def test_static_data_allowed(self):
        self.assertTrue(audit_source("x = {'module': 'a'}")["safe"])
    def test_syntax_fail_closed(self):
        self.assertFalse(audit_source("def (")["safe"])
    def test_missing_file_fail_closed(self):
        self.assertFalse(next(iter(audit_paths(["/nonexistent/r830.py"]).values()))["safe"])

if __name__ == "__main__":
    unittest.main()
