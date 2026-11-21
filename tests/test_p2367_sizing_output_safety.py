import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2367SizingOutputSafetyTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit", return_value={"emit_allowed": True, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"})
    def test_malformed_lot_never_emits(self, _precheck, _edge):
        signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 2.1}
        context = {"swing_high": 110, "swing_low": 90}
        for lot in (None, "invalid", True, float("nan"), float("inf"), -1, 0):
            with self.subTest(lot=lot):
                with patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot",
                           return_value={"recommended_paper_lot": lot, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}):
                    result = decide_signal(signal, context)
                self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")
                self.assertEqual(result["paper_lot"], 0)
                self.assertEqual(result["real_orders"], "FORBIDDEN")
                self.assertEqual(result["ftmo_real"], "FORBIDDEN")

    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit", return_value={"emit_allowed": "true"})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot", return_value={"recommended_paper_lot": 0.01})
    def test_string_precheck_does_not_authorize(self, _sizing, _precheck, _edge):
        out = decide_signal({"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 2.1},
                            {"swing_high": 110, "swing_low": 90})
        self.assertEqual(out["final_decision"], "BLOCK_PRECHECK")


if __name__ == "__main__":
    unittest.main()
