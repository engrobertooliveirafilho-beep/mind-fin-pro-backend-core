import unittest
import pandas as pd
from app.runtime.p2365_causal_de40_trainer import train_de40_contexts


class P2365TrainerTests(unittest.TestCase):
    def test_trainer_is_research_only_and_prefix_stable(self):
        n = 650
        frame = pd.DataFrame({
            "time": pd.date_range("2024-01-01", periods=n, freq="5min"),
            "close": [16000 + i * 0.1 + (i % 17) for i in range(n)],
            "high": [16001 + i * 0.1 + (i % 17) for i in range(n)],
            "low": [15999 + i * 0.1 + (i % 17) for i in range(n)],
        })
        rank, summary = train_de40_contexts(frame)
        self.assertEqual(summary["promoted_contexts"], 0)
        self.assertEqual(summary["certification"], "PENDING_INDEPENDENT_OOS_VALIDATION")
        self.assertFalse((rank["decision"] == "PROMOTE_CONTEXT").any())
        self.assertEqual(summary["real_orders"], "FORBIDDEN")

    def test_invalid_chronology_blocks(self):
        frame = pd.DataFrame({"time": [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-01")],
                              "close": [100, 101], "high": [102, 103], "low": [99, 100]})
        with self.assertRaises(ValueError):
            train_de40_contexts(frame)


if __name__ == "__main__":
    unittest.main()
