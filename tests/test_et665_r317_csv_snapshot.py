"""ET665.R317 — isolated offline CSV snapshot regressions (no broker/network).
Run: python -m unittest discover -s tests -p 'test_et665_r317_csv_snapshot.py' -v
These tests do not certify causality, FTMO eligibility, or runtime execution.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from mind_trader.research.et665_r315_immutable_csv_snapshot import snapshot_verified_csv


class SnapshotFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "paper.csv"

    def check(self, payload, *, expected=None, **kwargs):
        self.path.write_bytes(payload)
        digest = expected if expected is not None else hashlib.sha256(payload).hexdigest()
        return snapshot_verified_csv(self.path, digest, **kwargs)

    def test_valid_pinned_snapshot_is_readable_but_not_promotable(self):
        result = self.check(b"edge_id,timestamp,pnl_r\na,2026-01-01,1.0\n")
        self.assertTrue(result["verified"])
        self.assertFalse(result["runtime_promotion_allowed"])
        self.assertEqual(len(result["rows"]), 1)

    def test_tampered_bytes_are_rejected(self):
        result = self.check(b"edge_id,timestamp,pnl_r\na,2026-01-01,1\n",
                            expected="0" * 64)
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["SOURCE_HASH_MISMATCH"])

    def test_malformed_extra_column_is_rejected(self):
        result = self.check(b"edge_id,timestamp,pnl_r\na,2026-01-01,1,extra\n")
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["INVALID_CSV_ROWS"])

    def test_wrong_header_is_rejected(self):
        result = self.check(b"timestamp,edge_id,pnl_r\n2026-01-01,a,1\n")
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["INVALID_CSV_SCHEMA"])

    def test_source_size_limit_is_enforced(self):
        result = self.check(b"edge_id,timestamp,pnl_r\na,2026-01-01,1\n", max_bytes=8)
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["SOURCE_TOO_LARGE"])

    def test_invalid_hash_is_rejected(self):
        result = self.check(b"edge_id,timestamp,pnl_r\n", expected="not-a-hash")
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["EXPECTED_HASH_REQUIRED"])

    def test_symlink_source_is_rejected(self):
        target = Path(self.temp.name) / "original.csv"
        payload = b"edge_id,timestamp,pnl_r\na,2026-01-01,1\n"
        target.write_bytes(payload)
        self.path.symlink_to(target)
        result = snapshot_verified_csv(self.path, hashlib.sha256(payload).hexdigest())
        self.assertFalse(result["verified"])
        self.assertEqual(result["issues"], ["INVALID_SOURCE_PATH"])


if __name__ == "__main__":
    unittest.main()
