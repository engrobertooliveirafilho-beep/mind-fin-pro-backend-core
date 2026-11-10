"""ET665 R327 offline adversarial regression tests."""
import csv
import hashlib
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mind_trader.research.et665_r326_causal_walk_forward import evaluate_csv, MAX_SOURCE_BYTES


class WalkForwardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.path = self.root / "trades.csv"

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, n=30):
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        return [
            ("edge-a", (start + timedelta(days=i)).isoformat(), 2 if i % 3 else -1)
            for i in range(n)
        ]

    def write(self, rows):
        with self.path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["edge_id", "timestamp", "pnl_r"])
            writer.writerows(rows)

    def evaluate(self):
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        return evaluate_csv(self.path, expected_sha256=digest)

    def test_hash_required(self):
        self.write(self.rows())
        self.assertIn("EXPECTED_SOURCE_SHA256_REQUIRED", evaluate_csv(self.path)["issues"])

    def test_hash_mismatch_rejected(self):
        self.write(self.rows())
        result = evaluate_csv(self.path, expected_sha256="0" * 64)
        self.assertIn("SOURCE_SHA256_MISMATCH", result["issues"])

    def test_empirical_metrics_research_only(self):
        self.write(self.rows())
        result = self.evaluate()
        edge = result["edges"]["edge-a"]
        self.assertEqual(edge["samples"], 30)
        self.assertAlmostEqual(edge["pf"], 4.0)
        self.assertEqual(edge["decision"], "RESEARCH_ONLY_NOT_CERTIFIED")
        self.assertFalse(result["runtime_promotion_allowed"])
        self.assertFalse(result["real_execution_allowed"])
        self.assertIn("TRADING_COSTS_NOT_INCLUDED", result["issues"])

    def test_nonchronological_trades_rejected(self):
        rows = self.rows()
        rows[0], rows[1] = rows[1], rows[0]
        self.write(rows)
        self.assertIn("NONCHRONOLOGICAL_TRADES", self.evaluate()["issues"])

    def test_duplicate_edge_timestamp_rejected(self):
        rows = self.rows()
        rows.insert(1, rows[0])
        self.write(rows)
        self.assertIn("DUPLICATE_EDGE_TIMESTAMP", self.evaluate()["issues"])

    def test_same_instant_different_offsets_is_duplicate(self):
        self.write([
            ("edge-a", "2025-01-01T00:00:00+00:00", 1),
            ("edge-a", "2024-12-31T19:00:00-05:00", 1),
        ])
        self.assertIn("DUPLICATE_EDGE_TIMESTAMP", self.evaluate()["issues"])

    def test_timezone_required(self):
        self.write([("edge-a", "2025-01-01T00:00:00", 1)])
        self.assertIn("TIMEZONE_REQUIRED", self.evaluate()["issues"])

    def test_mixed_offsets_are_normalized(self):
        self.write([
            ("edge-a", "2025-01-01T00:00:00+00:00", 1),
            ("edge-a", "2025-01-01T02:00:00+01:00", 2),
        ])
        result = self.evaluate()
        self.assertNotIn("UNREADABLE_OR_INVALID_SOURCE", result["issues"])
        self.assertNotIn("NONCHRONOLOGICAL_TRADES", result["issues"])

    def test_invalid_timestamp_is_rejected_without_exception(self):
        self.write([("edge-a", "not-a-timestamp", 1)])
        self.assertIn("UNREADABLE_OR_INVALID_SOURCE", self.evaluate()["issues"])

    def test_short_sample_blocked(self):
        self.write(self.rows(29))
        result = self.evaluate()
        self.assertEqual(result["edges"]["edge-a"]["decision"], "BLOCKED_INSUFFICIENT_SAMPLES")

    def test_nan_rejected(self):
        rows = self.rows()
        rows[0] = ("edge-a", rows[0][1], "nan")
        self.write(rows)
        self.assertIn("INVALID_TRADE", self.evaluate()["issues"])

    def test_infinite_rejected(self):
        rows = self.rows()
        rows[0] = ("edge-a", rows[0][1], "inf")
        self.write(rows)
        self.assertIn("INVALID_TRADE", self.evaluate()["issues"])

    def test_empty_edge_id_rejected(self):
        self.write([("", "2025-01-01T00:00:00+00:00", 1)])
        self.assertIn("INVALID_EDGE_ID", self.evaluate()["issues"])

    def test_bad_header_rejected(self):
        self.path.write_text("wrong,header\na,b\n", encoding="utf-8")
        self.assertIn("INVALID_HEADER", self.evaluate()["issues"])

    def test_missing_file_rejected(self):
        result = evaluate_csv(self.path, expected_sha256="0" * 64)
        self.assertIn("INVALID_SOURCE", result["issues"])

    def test_symlink_rejected(self):
        target = self.root / "target.csv"
        target.write_text("edge_id,timestamp,pnl_r\n", encoding="utf-8")
        try:
            self.path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable on this platform")
        self.assertIn("INVALID_SOURCE", evaluate_csv(self.path, expected_sha256="0" * 64)["issues"])

    def test_oversized_source_rejected(self):
        with self.path.open("wb") as fh:
            fh.truncate(MAX_SOURCE_BYTES + 1)
        result = evaluate_csv(self.path, expected_sha256="0" * 64)
        self.assertIn("SOURCE_TOO_LARGE", result["issues"])


if __name__ == "__main__":
    unittest.main()
