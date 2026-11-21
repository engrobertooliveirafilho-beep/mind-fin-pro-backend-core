import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2367TargetReasonTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_invalid_atr_is_not_misreported_as_sub_2r(self, _):
        out = decide_signal({"side": "BUY", "entry": 100, "stop": 99}, {"atr": True})
        self.assertEqual(out["targeting"]["decision"], "BLOCK_INVALID_INPUT")
        self.assertEqual(out["final_decision"], "BLOCK_SIGNAL_INVALID_TARGET")
        self.assertEqual(out["paper_lot"], 0)
        self.assertEqual(out["ftmo_real"], "FORBIDDEN")

    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_genuine_sub_2r_keeps_reason(self, _):
        out = decide_signal({"side": "BUY", "entry": 100, "stop": 98},
                            {"swing_high": 100.5, "swing_low": 99.5, "atr": 0.2,
                             "session_high": 101, "liquidity_high": 101})
        self.assertEqual(out["targeting"]["decision"], "BLOCK_TARGET_BELOW_2R")
        self.assertEqual(out["final_decision"], "BLOCK_SIGNAL_TARGET_BELOW_2R")


if __name__ == "__main__":
    unittest.main()
