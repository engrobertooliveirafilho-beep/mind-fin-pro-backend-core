import csv
import tempfile
import unittest
from pathlib import Path
from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import index_for_signal, run


class P2380CausalFeedbackGateTests(unittest.TestCase):
    def test_unattested_historical_bus_is_not_evaluated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bus = root / "signals.csv"
            with bus.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["signal_id", "timeframe", "direction", "family"])
                w.writeheader()
                w.writerow({"signal_id": "old1", "timeframe": "M5", "direction": "BUY_PAPER", "family": "TREND"})
            result = run(bus, root / "dataset", root / "out")
            self.assertEqual(result["signals_loaded"], 1)
            self.assertEqual(result["signals_evaluated"], 0)
            self.assertEqual(result["promoted_after_feedback"], 0)
            self.assertEqual(result["certification"], "NOT_CERTIFIED")
            with (root / "out" / "de40_forward_paper_feedback_all.csv").open(newline="") as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["paper_result"], "SKIPPED_UNCERTIFIED_CAUSAL_INPUT")

    def test_replay_anchor_is_deterministic(self):
        candles = [{"close": 100}] * 600
        self.assertEqual(index_for_signal({"signal_id": "stable"}, candles),
                         index_for_signal({"signal_id": "stable"}, candles))


if __name__ == "__main__":
    unittest.main()
