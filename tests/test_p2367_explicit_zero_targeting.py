import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2367ExplicitZeroTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_explicit_zero_atr_is_not_replaced(self, _):
        signal = {"side": "BUY", "entry": 100, "stop": 99}
        context = {"atr": 0, "swing_high": 100, "swing_low": 100}
        result = decide_signal(signal, context)
        self.assertFalse(result["targeting"]["approved"])
        self.assertEqual(result["paper_lot"], 0.0)
        self.assertEqual(result["real_orders"], "FORBIDDEN")

    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_negative_and_boolean_atr_fail_closed(self, _):
        signal = {"side": "BUY", "entry": 100, "stop": 99}
        for value in (-1, True):
            with self.subTest(value=value):
                result = decide_signal(signal, {"atr": value, "swing_high": 100, "swing_low": 100})
                self.assertFalse(result["targeting"]["approved"])
                self.assertEqual(result["paper_lot"], 0.0)


if __name__ == "__main__":
    unittest.main()
