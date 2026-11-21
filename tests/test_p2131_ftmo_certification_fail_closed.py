import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.runtime import p2131_2150_ftmo_paper_compliance_assurance as ftmo

class FtmoDeclarationSafetyTests(unittest.TestCase):
    def test_missing_evidence_never_certifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            import os
            old = os.getcwd()
            try:
                os.chdir(tmp)
                result = ftmo.run_p2131_2150(output_dir="out")
            finally:
                os.chdir(old)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["mission_status"]["P2142_METRICS_CONSISTENCY_AUDIT"], "FAIL")
        self.assertEqual(result["readiness"], "NOT_CERTIFIED")
        self.assertEqual(result["mission_status"]["P2141_DATA_INTEGRITY_AUDIT"], "FAIL")
        self.assertEqual(result["mission_status"]["P2148_COMPLIANCE_REGRESSION_SUITE"], "PENDING")
        self.assertEqual(result["mission_status"]["P2140_FTMO_PAPER_COMPLIANCE_CERTIFICATION"], "PENDING")
        self.assertEqual(result["mission_status"]["P2150_OPERATIONAL_READINESS_CERTIFICATION"], "PENDING")
    def test_declaration_not_behavioral_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            import os
            old = os.getcwd()
            try:
                os.chdir(tmp)
                result = ftmo.run_p2131_2150(output_dir="out")
            finally:
                os.chdir(old)
        self.assertEqual(result["mission_status"]["P2132_DAILY_LOSS_GUARD_DECLARATION"], "UNVERIFIED")
        self.assertEqual(result["mission_status"]["P2138_RUNTIME_RISK_KILL_SWITCH_AUDIT"], "UNVERIFIED")
        self.assertEqual(result["final_state"]["ftmo_paper_compliance"], "NOT_CERTIFIED")
    def test_unsafe_real_order_environment_rejected_before_write(self):
        import os
        with patch.dict(os.environ, {"REAL_ORDERS":"ALLOWED"}):
            with self.assertRaisesRegex(RuntimeError, "LOCK_BREACH"):
                ftmo.assert_locks()
            self.assertEqual(os.environ["REAL_ORDERS"], "ALLOWED")
    def test_safe_environment_accepted(self):
        import os
        with patch.dict(os.environ, {}, clear=True):
            ftmo.assert_locks()
            self.assertEqual(os.environ["REAL_ORDERS"], "FORBIDDEN")
            self.assertEqual(os.environ["FTMO_REAL"], "FORBIDDEN")
    def test_malformed_dependency_fails_closed(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            try:
                os.chdir(tmp)
                p = Path("data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json")
                p.parent.mkdir(parents=True)
                p.write_text("{invalid-json", encoding="utf-8")
                result = ftmo.run_p2131_2150(output_dir="out")
            finally:
                os.chdir(old)
        self.assertIn(str(p), result["invalid_dependencies"])
        self.assertEqual(result["dependencies"]["p2071"]["status"], "INVALID")
        self.assertEqual(result["status"], "FAIL")
    def test_nonobject_dependency_fails_closed(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            try:
                os.chdir(tmp)
                p = Path("data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json")
                p.parent.mkdir(parents=True)
                p.write_text("[]", encoding="utf-8")
                result = ftmo.run_p2131_2150(output_dir="out")
            finally:
                os.chdir(old)
        self.assertIn(str(p), result["invalid_dependencies"])
        self.assertEqual(result["status"], "FAIL")
