"""ET665.R62 regression tests: synthetic offline fixtures only."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "security" / "et665_r62_phase_b_evidence_gate.py"
spec = importlib.util.spec_from_file_location("et665_r62_gate", SOURCE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class PhaseBEvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        f = self.root / "proof.txt"
        f.write_text("synthetic evidence", encoding="utf-8")
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        self.data = {key: {"path": "proof.txt", "sha256": sha, "approved": True} for key in gate.REQUIRED}

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_does_not_certify(self):
        result = gate.assess(self.data, self.root)
        self.assertTrue(result["evidence_complete"])
        self.assertFalse(result["phase_b_certified"])

    def test_missing(self):
        del self.data["drive_manifest"]
        self.assertEqual(gate.assess(self.data, self.root)["checks"]["drive_manifest"], "MISSING")

    def test_hash_mismatch(self):
        self.data["git_manifest"]["sha256"] = "0" * 64
        self.assertEqual(gate.assess(self.data, self.root)["checks"]["git_manifest"], "HASH_MISMATCH")

    def test_unapproved(self):
        self.data["security_review"]["approved"] = False
        self.assertEqual(gate.assess(self.data, self.root)["checks"]["security_review"], "NOT_APPROVED")

    def test_path_traversal(self):
        self.data["reconciliation"]["path"] = "../outside"
        self.assertEqual(gate.assess(self.data, self.root)["checks"]["reconciliation"], "MISSING_OR_UNSAFE_PATH")

    def test_invalid_metadata(self):
        self.data["p77_p79_isolation"]["sha256"] = "x"
        self.assertEqual(gate.assess(self.data, self.root)["checks"]["p77_p79_isolation"], "INVALID_METADATA")

    def test_real_orders_forbidden(self):
        self.assertEqual(gate.assess(self.data, self.root)["real_orders"], "FORBIDDEN")
        self.assertEqual(gate.assess(self.data, self.root)["ftmo_real"], "FORBIDDEN")

if __name__ == "__main__":
    unittest.main()
