"""ET665.R256 — research output must not claim export-ready certification."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r256", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CertificationExportGate(unittest.TestCase):
    def test_empty_research_is_not_export_ready(self):
        module = engine()
        with tempfile.TemporaryDirectory() as temp:
            before = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[]):
                    result = module.run()
                path = Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION/institutional_certification.json")
                persisted = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(result["EXPORT_READY"])
                self.assertFalse(persisted["EXPORT_READY"])
                self.assertEqual(persisted["CERTIFICATION_EVIDENCE"], "NOT_EXECUTED_OR_INDEPENDENTLY_VERIFIED")
                self.assertEqual(persisted["APPROVED_EDGES"], 0)
                self.assertEqual(persisted["REAL_ORDERS"], "FORBIDDEN")
            finally:
                os.chdir(before)

if __name__ == "__main__":
    unittest.main()
