import csv
import tempfile
import unittest
from pathlib import Path
from app.runtime.p2381_de40_loss_lesson_auto_patch_and_memory_graph import run


class P2381HistoricalFeedbackQuarantineTests(unittest.TestCase):
    def test_unattested_feedback_cannot_generate_blacklists_or_patches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feedback = root / "feedback.csv"
            with feedback.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["feedback_status", "realized_r", "family", "timeframe"])
                w.writeheader()
                for _ in range(40):
                    w.writerow({"feedback_status": "EVALUATED", "realized_r": -1,
                                "family": "TREND", "timeframe": "M5"})
            result = run(feedback, root / "out")
            self.assertEqual(result["signals_analyzed"], 0)
            self.assertEqual(result["loss_memory_nodes"], 0)
            self.assertEqual(result["patched_replay_candidates"], 0)
            self.assertEqual(result["blocked_family_timeframe_rules"], 0)
            self.assertEqual(result["certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
