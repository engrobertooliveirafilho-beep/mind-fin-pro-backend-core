import csv
import tempfile
import unittest
from pathlib import Path
from app.runtime.p2382_de40_replay_after_loss_patch import run


class P2382UnverifiedReplayGateTests(unittest.TestCase):
    def test_legacy_winning_patch_cannot_promote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "patched.csv"
            with source.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["realized_r", "profit_factor_proxy",
                                                      "expectancy_r_proxy", "family", "timeframe"])
                writer.writeheader()
                for _ in range(50):
                    writer.writerow({"realized_r": 2, "profit_factor_proxy": 999,
                                     "expectancy_r_proxy": 2, "family": "TREND", "timeframe": "M5"})
            result = run(source, root / "out", -0.08, 0.83, 61.3)
            self.assertEqual(result["signals_replayed"], 0)
            self.assertEqual(result["promoted_after_patch"], 0)
            self.assertEqual(result["promoted_groups_after_patch"], 0)
            self.assertFalse(result["success"])
            self.assertEqual(result["certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
