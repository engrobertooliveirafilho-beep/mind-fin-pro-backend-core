"""ME-RS-068: isolated synthetic regression for late R4/R5 approvals."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

EXECUTOR = Path(__file__).resolve().parents[1] / "code" / "engineering_pipeline" / "post_r6.py"
spec = importlib.util.spec_from_file_location("me_rs_068_r7", EXECUTOR)
r7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r7)


class TestR7LateApproval(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="me_rs_068_")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / "r6.jsonl"
        self.db = root / "ledger.sqlite"
        self.approval = root / "approval.jsonl"
        self.item = dict(stage="R6", seq=1, r5_seq=1, r4_sha256="a"*64, r5_sha256="b"*64)
        self.raw = (json.dumps(self.item) + "\n").encode()
        self.source.write_bytes(self.raw)

    def manifest(self, bad=None):
        item = dict(r6_sha256=hashlib.sha256(self.raw).hexdigest(),
                    r4_sha256="c"*64 if bad == "r4" else "a"*64,
                    r5_sha256="d"*64 if bad == "r5" else "b"*64,
                    decision="APPROVED", authority="ISOLATED_TEST_ONLY")
        self.approval.write_text(json.dumps(item) + "\n", encoding="utf-8")

    def rows(self):
        with sqlite3.connect(self.db) as con:
            return con.execute("SELECT decision,authority FROM records").fetchall()

    def test_late_r4_mismatch(self):
        r7.consume(self.source, self.db, None, 1)
        self.manifest("r4")
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            r7.consume(self.source, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("PENDING", None)])

    def test_late_r5_mismatch(self):
        r7.consume(self.source, self.db, None, 1)
        self.manifest("r5")
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            r7.consume(self.source, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("PENDING", None)])

    def test_new_r4_mismatch(self):
        self.manifest("r4")
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            r7.consume(self.source, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [])

    def test_new_r5_mismatch(self):
        self.manifest("r5")
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            r7.consume(self.source, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [])

    def test_valid_late_approval_and_replay(self):
        r7.consume(self.source, self.db, None, 1)
        self.manifest()
        r7.consume(self.source, self.db, self.approval, 1)
        r7.consume(self.source, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("APPROVED", "ISOLATED_TEST_ONLY")])


if __name__ == "__main__":
    unittest.main()
