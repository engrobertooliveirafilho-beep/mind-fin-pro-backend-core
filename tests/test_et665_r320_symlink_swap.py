"""ET665.R320 — deterministic symlink-swap regression; offline only."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mind_trader.research.et665_r315_immutable_csv_snapshot import snapshot_verified_csv


class SymlinkSwapTests(unittest.TestCase):
    def test_source_swapped_to_symlink_at_open_is_rejected(self):
        if not hasattr(os, "O_NOFOLLOW"):
            self.skipTest("Platform has no O_NOFOLLOW; test requires POSIX")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            other = Path(tmp) / "other.csv"
            data = b"edge_id,timestamp,pnl_r\na,1,1\n"
            path.write_bytes(data)
            other.write_bytes(data)
            actual_open = os.open

            def swap_then_open(name, flags, *args, **kwargs):
                path.unlink()
                path.symlink_to(other)
                return actual_open(name, flags, *args, **kwargs)

            with patch("mind_trader.research.et665_r315_immutable_csv_snapshot.os.open", side_effect=swap_then_open):
                result = snapshot_verified_csv(path, hashlib.sha256(data).hexdigest())
            self.assertFalse(result["verified"])
            self.assertFalse(result["runtime_promotion_allowed"])
            self.assertEqual(result["issues"], ["SOURCE_UNREADABLE"])

    def test_no_atomic_nofollow_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            data = b"edge_id,timestamp,pnl_r\\na,1,1\\n"
            path.write_bytes(data)
            with patch("mind_trader.research.et665_r315_immutable_csv_snapshot.os", spec=[]):
                result = snapshot_verified_csv(path, hashlib.sha256(data).hexdigest())
            self.assertFalse(result["verified"])
            self.assertFalse(result["runtime_promotion_allowed"])
            self.assertEqual(result["issues"], ["ATOMIC_NOFOLLOW_UNAVAILABLE"])

    def test_regular_file_still_verifies(self):
        if not hasattr(os, "O_NOFOLLOW"):
            self.skipTest("Atomic no-follow unsupported; fail-closed is expected")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            data = b"edge_id,timestamp,pnl_r\na,1,1\n"
            path.write_bytes(data)
            result = snapshot_verified_csv(path, hashlib.sha256(data).hexdigest())
            self.assertTrue(result["verified"])
            self.assertFalse(result["runtime_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
