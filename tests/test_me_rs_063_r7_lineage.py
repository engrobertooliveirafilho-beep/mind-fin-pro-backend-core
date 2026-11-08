"""ME-RS-063 isolated regression: original post_r6.consume approval lineage.

Usage:
  set ME_R7_ORIGINAL_EXECUTOR=...\\post_r6.py
  set ME_R6_SOURCE=...\\r6_output.jsonl
  python -m unittest discover -s tests -p 'test_me_rs_063_r7_lineage.py' -v

Tests intentionally fail when late-approval mismatches are silently ignored.
Never point at a production DB: each test creates its own temporary SQLite DB.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest


class R7LineageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exe = os.environ.get("ME_R7_ORIGINAL_EXECUTOR")
        src = os.environ.get("ME_R6_SOURCE")
        if not exe or not src:
            raise unittest.SkipTest("Set ME_R7_ORIGINAL_EXECUTOR and ME_R6_SOURCE")
        cls.executor = Path(exe).resolve(strict=True)
        cls.source = Path(src).resolve(strict=True)
        expected = "58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63"
        actual = hashlib.sha256(cls.executor.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError("ORIGINAL_EXECUTOR_HASH_MISMATCH")
        spec = importlib.util.spec_from_file_location("me_rs_063_original", cls.executor)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        with cls.source.open("rb") as handle:
            cls.raw = handle.readline()
        cls.item = json.loads(cls.raw)
        if cls.item.get("stage") != "R6" or cls.item.get("seq") != 1 or cls.item.get("r5_seq") != 1:
            raise RuntimeError("INVALID_FIRST_R6_RECORD")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="me_rs_063_")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.sample = root / "source.jsonl"
        self.db = root / "isolated.sqlite"
        self.approval = root / "approvals.jsonl"
        self.sample.write_bytes(self.raw)

    def manifest(self, bad=False):
        r4 = self.item["r4_sha256"]
        if bad:
            r4 = "0" * 64 if r4 != "0" * 64 else "1" * 64
        data = {
            "r6_sha256": hashlib.sha256(self.raw).hexdigest(),
            "r4_sha256": r4,
            "r5_sha256": self.item["r5_sha256"],
            "decision": "APPROVED",
            "authority": "ISOLATED_TEST_ONLY",
        }
        self.approval.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")

    def rows(self):
        with sqlite3.connect(self.db) as con:
            return con.execute("SELECT decision,authority FROM records").fetchall()

    def test_mismatch_on_new_record_is_rejected(self):
        self.manifest(bad=True)
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            self.module.consume(self.sample, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [])

    def test_mismatch_on_existing_pending_is_explicitly_rejected(self):
        self.module.consume(self.sample, self.db, None, 1)
        self.assertEqual(self.rows(), [("PENDING", None)])
        self.manifest(bad=True)
        with self.assertRaisesRegex(ValueError, "APPROVAL_LINEAGE_MISMATCH"):
            self.module.consume(self.sample, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("PENDING", None)])

    def test_valid_late_approval_and_replay(self):
        self.module.consume(self.sample, self.db, None, 1)
        self.manifest(bad=False)
        self.module.consume(self.sample, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("APPROVED", "ISOLATED_TEST_ONLY")])
        self.module.consume(self.sample, self.db, self.approval, 1)
        self.assertEqual(self.rows(), [("APPROVED", "ISOLATED_TEST_ONLY")])


if __name__ == "__main__":
    unittest.main()
