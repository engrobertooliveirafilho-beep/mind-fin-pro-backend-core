import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2362PrecheckGateTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot")
    def test_malformed_precheck_never_calls_sizing(self, sizing, _edge):
        signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 2.1}
        context = {"swing_high": 110, "swing_low": 90}
        for response in (None, False, {"emit_allowed": "true"}, {"emit_allowed": 1}, {}):
            with self.subTest(response=response):
                with patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit",
                           return_value=response):
                    result = decide_signal(signal, context)
                self.assertEqual(result["final_decision"], "BLOCK_PRECHECK")
                self.assertEqual(result["paper_lot"], 0)
                self.assertEqual(result["real_orders"], "FORBIDDEN")
                self.assertEqual(result["ftmo_real"], "FORBIDDEN")
        sizing.assert_not_called()


if __name__ == "__main__":
    unittest.main()
