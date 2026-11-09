"""ET665.R274 — persisted research report must not overclaim certification."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r274", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class ResearchClaimIntegrity(unittest.TestCase):
    def test_manifest_and_persisted_report_do_not_overclaim(self):
        module = engine()
        with tempfile.TemporaryDirectory() as temp:
            original = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[]):
                    report = module.run()
                persisted = json.loads(Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION/institutional_certification.json").read_text(encoding="utf-8"))
                self.assertEqual(report, persisted)
                self.assertEqual(report["STATUS"], "P15.25_RESEARCH_IMPLEMENTED_CERTIFICATION_NOT_PROVEN")
                self.assertEqual(report["P15_20_CORRELATION_EVIDENCE"], "UNALIGNED_NOT_CERTIFIED")
                self.assertEqual(report["P15_21_RISK_OF_RUIN"], "PROXY_ONLY_NOT_CERTIFIED")
                self.assertEqual(report["P15_22_PORTFOLIO_HEAT"], "NOT_VERIFIED")
                self.assertFalse(report["EXPORT_READY"])
                self.assertEqual(report["APPROVED_EDGES"], 0)
            finally:
                os.chdir(original)

if __name__ == "__main__":
    unittest.main()
