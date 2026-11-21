"""Offline integration regression: contaminated historical outputs cannot flow through P2380-P2382."""
import csv
import tempfile
import unittest
from pathlib import Path
from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import run as feedback_run
from app.runtime.p2381_de40_loss_lesson_auto_patch_and_memory_graph import run as memory_run
from app.runtime.p2382_de40_replay_after_loss_patch import run as replay_run


class HistoricalCausalityChainTests(unittest.TestCase):
    def test_p2380_to_p2382_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bus = root / "legacy_bus.csv"
            with bus.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["signal_id", "timeframe", "direction",
                                                       "family", "profit_factor_proxy", "expectancy_r_proxy"])
                writer.writeheader()
                for i in range(40):
                    writer.writerow({"signal_id": str(i), "timeframe": "M5", "direction": "BUY_PAPER",
                                     "family": "TREND", "profit_factor_proxy": 999, "expectancy_r_proxy": 10})
            feedback = feedback_run(bus, root / "no_dataset", root / "feedback")
            self.assertEqual(feedback["signals_evaluated"], 0)
            self.assertEqual(feedback["promoted_after_feedback"], 0)

            memory = memory_run(root / "feedback" / "de40_forward_paper_feedback_all.csv", root / "memory")
            self.assertEqual(memory["signals_analyzed"], 0)
            self.assertEqual(memory["patched_replay_candidates"], 0)
            self.assertEqual(memory["loss_memory_nodes"], 0)

            replay = replay_run(root / "memory" / "de40_patched_replay_candidates.csv",
                                root / "replay", -0.08, 0.83, 61.3)
            self.assertEqual(replay["signals_replayed"], 0)
            self.assertEqual(replay["promoted_after_patch"], 0)
            self.assertFalse(replay["success"])
            self.assertEqual(replay["certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
