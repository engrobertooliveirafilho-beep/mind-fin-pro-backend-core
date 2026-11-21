import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.runtime import p2131_2150_ftmo_paper_compliance_assurance as ftmo

class FtmoDeclarationSafetyTests(unittest.TestCase):
    def test_missing_evidence_never_certifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(ftmo, "Path", Path):
                with patch("os.getcwd", return_value=tmp):
                    import os
                    old = os.getcwd()
                    try:
                        os.chdir(tmp)
                        result = ftmo.run_p2131_2150(output_dir="out")
                    finally:
                        os.chdir(old)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["readiness"], "NOT_CERTIFIED")
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
