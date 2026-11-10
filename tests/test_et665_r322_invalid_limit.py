"""ET665.R322 — fail-closed CSV snapshot size configuration."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from mind_trader.research.et665_r315_immutable_csv_snapshot import snapshot_verified_csv


class InvalidLimitTests(unittest.TestCase):
    def test_invalid_limits_are_rejected_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.csv"
            payload = b"edge_id,timestamp,pnl_r\na,1,1\n"
            path.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            for limit in (None, -1, 0, True, 1.5, "10", 16_000_001):
                with self.subTest(limit=limit):
                    result = snapshot_verified_csv(path, digest, max_bytes=limit)
                    self.assertFalse(result["verified"])
                    self.assertEqual(result["issues"], ["INVALID_SIZE_LIMIT"])
                    self.assertFalse(result["runtime_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
