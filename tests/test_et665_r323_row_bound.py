"""ET665.R323: row cap is enforced before appending the 100001st record."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from mind_trader.research.et665_r315_immutable_csv_snapshot import snapshot_verified_csv

class CsvRowBoundTests(unittest.TestCase):
    def test_100001_rows_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "many.csv"
            data = b"edge_id,timestamp,pnl_r\n" + b"a,1,1\n" * 100001
            path.write_bytes(data)
            result = snapshot_verified_csv(path, hashlib.sha256(data).hexdigest())
            self.assertFalse(result["verified"])
            self.assertEqual(result["issues"], ["INVALID_CSV_ROWS"])
            self.assertEqual(result["rows"], [])
            self.assertFalse(result["runtime_promotion_allowed"])

    def test_100000_rows_allowed_but_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "many.csv"
            data = b"edge_id,timestamp,pnl_r\n" + b"a,1,1\n" * 100000
            path.write_bytes(data)
            result = snapshot_verified_csv(path, hashlib.sha256(data).hexdigest())
            self.assertTrue(result["verified"])
            self.assertEqual(len(result["rows"]), 100000)
            self.assertFalse(result["runtime_promotion_allowed"])

if __name__ == "__main__":
    unittest.main()
