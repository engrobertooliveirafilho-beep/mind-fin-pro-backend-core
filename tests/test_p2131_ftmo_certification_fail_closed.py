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
    def test_midrun_lock_drift_aborts_evidence_write(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            try:
                os.chdir(tmp)
                original = ftmo.load_json
                def tamper(path):
                    os.environ["REAL_ORDERS"] = "ALLOWED"
                    return original(path)
                p = Path("data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json")
                p.parent.mkdir(parents=True)
                p.write_text('{"status":"PASS"}', encoding="utf-8")
                with patch.object(ftmo, "load_json", side_effect=tamper):
                    with self.assertRaisesRegex(RuntimeError, "LOCK_BREACH"):
                        ftmo.run_p2131_2150(output_dir="out")
                self.assertFalse(Path("out/P2131_2150_FINAL_CERTIFICATION.json").exists())
            finally:
                os.chdir(old)
                os.environ["REAL_ORDERS"] = "FORBIDDEN"
    def test_public_enforce_rejects_unsafe_configuration(self):
        import os
        with patch.dict(os.environ, {"FTMO_REAL": "ALLOWED"}):
            with self.assertRaisesRegex(RuntimeError, "LOCK_BREACH"):
                ftmo.enforce()
            self.assertEqual(os.environ["FTMO_REAL"], "ALLOWED")
    def test_six_self_declared_pass_files_cannot_certify_integrity(self):
        import os
        blocks = ("P2071_2080", "P2081_2090", "P2091_2100",
                  "P2101_2110", "P2111_2120", "P2121_PLUS")
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            try:
                os.chdir(tmp)
                for block in blocks:
                    evidence = Path("data/runtime") / block / "evidence"
                    evidence.mkdir(parents=True, exist_ok=True)
                    (evidence / (block + "_FINAL_CERTIFICATION.json")).write_text(
                        '{"status":"PASS","readiness":"CERTIFIED"}', encoding="utf-8")
                    (evidence / (block + "_AUDIT.md")).write_text(
                        "# Self-declared PASS", encoding="utf-8")
                result = ftmo.run_p2131_2150(output_dir="out")
            finally:
                os.chdir(old)
        self.assertEqual(result["missing_dependencies"], [])
        self.assertEqual(result["invalid_dependencies"], [])
        self.assertEqual(result["mission_status"]["P2131_FTMO_RULE_FRAMEWORK_AUDIT"], "UNVERIFIED")
        self.assertEqual(result["mission_status"]["P2141_DATA_INTEGRITY_AUDIT"], "UNVERIFIED")
        self.assertEqual(result["mission_status"]["P2142_METRICS_CONSISTENCY_AUDIT"], "UNVERIFIED")
        self.assertEqual(result["mission_status"]["P2147_EVIDENCE_CHAIN_VERIFICATION"], "UNVERIFIED")
        self.assertEqual(result["readiness"], "NOT_CERTIFIED")
