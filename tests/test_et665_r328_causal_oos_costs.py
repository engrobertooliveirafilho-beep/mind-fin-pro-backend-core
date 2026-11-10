"""ET665 R328 chronological OOS and execution-cost regressions."""
import csv
import hashlib
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mind_trader.research.et665_r328_causal_oos_costs import (
    EXPECTED_COLUMNS,
    evaluate_causal_oos_csv,
)


class CausalOOSTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "trades.csv"
        self.train_end = "2025-02-01T00:00:00Z"
        self.validation_end = "2025-04-01T00:00:00Z"
        self.test_end = "2025-06-01T00:00:00Z"

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, day, signal_id, *, edge="edge-a", gross="2", spread="0.1",
            slippage="0.1", commission="0.1", signal=None, entry=None, exit=None,
            logic_hash="a"*64, market_hash="b"*64, execution_hash="c"*64,
            review_id="review-1"):
        stamp = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=day)
        signal = signal or stamp
        entry = entry or (signal + timedelta(minutes=1))
        exit = exit or (entry + timedelta(minutes=5))
        return [
            edge, signal_id, signal.isoformat(), entry.isoformat(), exit.isoformat(),
            gross, spread, slippage, commission, logic_hash, market_hash,
            execution_hash, review_id,
        ]

    def dataset(self):
        rows = []
        for i in range(30):
            rows.append(self.row(i, f"train-{i}", gross="2" if i % 3 else "-1"))
        for i in range(30):
            rows.append(self.row(35+i, f"validation-{i}", gross="2" if i % 3 else "-1"))
        for i in range(30):
            rows.append(self.row(100+i, f"test-{i}", gross="2" if i % 3 else "-1"))
        return rows

    def write(self, rows):
        with self.path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(EXPECTED_COLUMNS)
            writer.writerows(rows)

    def evaluate(self, rows=None, **kwargs):
        self.write(self.dataset() if rows is None else rows)
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        args = dict(
            train_end=self.train_end,
            validation_end=self.validation_end,
            test_end=self.test_end,
            embargo_seconds=86400,
        )
        args.update(kwargs)
        return evaluate_causal_oos_csv(self.path, digest, **args)

    def test_three_chronological_windows_are_reported(self):
        result = self.evaluate()
        self.assertEqual(result["decision"], "RESEARCH_ONLY_OOS_METRICS_AVAILABLE")
        self.assertEqual(set(result["windows"]), {"train", "validation", "test"})
        self.assertEqual(result["windows"]["test"]["samples"], 30)

    def test_costs_are_subtracted_from_gross_pnl(self):
        result = self.evaluate()
        self.assertAlmostEqual(result["windows"]["test"]["net_expectancy_r"], 1.0)
        self.assertAlmostEqual(result["windows"]["test"]["net_total_r"], 30.0)

    def test_hash_mismatch_blocks(self):
        self.write(self.dataset())
        result = evaluate_causal_oos_csv(
            self.path, "0"*64, train_end=self.train_end,
            validation_end=self.validation_end, test_end=self.test_end,
        )
        self.assertIn("SOURCE_SHA256_MISMATCH", result["issues"])

    def test_missing_expected_hash_blocks(self):
        self.write(self.dataset())
        result = evaluate_causal_oos_csv(
            self.path, None, train_end=self.train_end,
            validation_end=self.validation_end, test_end=self.test_end,
        )
        self.assertIn("EXPECTED_SOURCE_SHA256_REQUIRED", result["issues"])

    def test_invalid_window_order_blocks(self):
        result = self.evaluate(
            train_end=self.validation_end,
            validation_end=self.train_end,
        )
        self.assertEqual(result["issues"], ["INVALID_WINDOW_CONFIGURATION"])

    def test_negative_embargo_blocks(self):
        result = self.evaluate(embargo_seconds=-1)
        self.assertEqual(result["issues"], ["INVALID_WINDOW_CONFIGURATION"])

    def test_naive_boundary_blocks(self):
        result = self.evaluate(train_end="2025-02-01T00:00:00")
        self.assertEqual(result["issues"], ["INVALID_WINDOW_CONFIGURATION"])

    def test_negative_execution_cost_blocks(self):
        rows = self.dataset()
        rows[0][6] = "-0.1"
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_nonfinite_gross_pnl_blocks(self):
        rows = self.dataset()
        rows[0][5] = "nan"
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_invalid_hash_metadata_blocks(self):
        rows = self.dataset()
        rows[0][9] = "not-a-hash"
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_duplicate_signal_id_blocks(self):
        rows = self.dataset()
        rows[1][1] = rows[0][1]
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_signal_after_entry_blocks(self):
        rows = self.dataset()
        stamp = datetime(2025, 1, 2, tzinfo=timezone.utc)
        rows[0][2] = (stamp + timedelta(minutes=2)).isoformat()
        rows[0][3] = (stamp + timedelta(minutes=1)).isoformat()
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_exit_before_entry_blocks(self):
        rows = self.dataset()
        stamp = datetime(2025, 1, 2, tzinfo=timezone.utc)
        rows[0][2] = stamp.isoformat()
        rows[0][3] = (stamp + timedelta(minutes=2)).isoformat()
        rows[0][4] = (stamp + timedelta(minutes=1)).isoformat()
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_missing_review_id_blocks(self):
        rows = self.dataset()
        rows[0][12] = ""
        result = self.evaluate(rows)
        self.assertIn("INVALID_TRADE_OR_PROVENANCE_METADATA", result["issues"])

    def test_purges_embargo_and_cross_boundary_trades(self):
        rows = self.dataset()
        boundary_signal = datetime(2025, 2, 1, 12, tzinfo=timezone.utc)
        rows.append(self.row(31, "purged-gap", signal=boundary_signal))
        result = self.evaluate(rows)
        self.assertEqual(result["windows"]["train"]["samples"], 30)
        self.assertEqual(result["windows"]["validation"]["samples"], 30)

    def test_insufficient_test_samples_blocks_decision(self):
        rows = self.dataset()[:-1]
        result = self.evaluate(rows)
        self.assertIn("TEST_INSUFFICIENT_SAMPLES", result["issues"])
        self.assertEqual(result["decision"], "BLOCKED")

    def test_no_runtime_promotion_even_when_windows_pass(self):
        result = self.evaluate()
        self.assertFalse(result["runtime_promotion_allowed"])
        self.assertFalse(result["real_execution_allowed"])
        self.assertFalse(result["causal_signal_verified"])
        self.assertFalse(result["independent_provenance_verified"])
        self.assertIn("RESEARCH_ONLY_NO_RUNTIME_PROMOTION", result["issues"])

    def test_nonchronological_rows_block(self):
        rows = self.dataset()
        rows[0], rows[1] = rows[1], rows[0]
        result = self.evaluate(rows)
        self.assertIn("NONCHRONOLOGICAL_SIGNALS", result["issues"])

    def test_wrong_schema_blocks(self):
        self.path.write_text("edge_id,signal_id\nx,y\n", encoding="utf-8")
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = evaluate_causal_oos_csv(
            self.path, digest, train_end=self.train_end,
            validation_end=self.validation_end, test_end=self.test_end,
        )
        self.assertTrue(any("INVALID_CSV_SCHEMA" in issue or "IMMUTABLE_SNAPSHOT_REJECTED" in issue
                            for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
