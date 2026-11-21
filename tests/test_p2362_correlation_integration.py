import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class PipelineCorrelationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.signal = {"symbol": "EURUSD", "side": "BUY", "entry": 1.1, "stop": 1.09,
                       "base_lot": 0.1, "expected_payoff": 3.5}
        self.context = {"entry": 1.1, "stop": 1.09, "atr": 0.002}
        self.patches = [
            patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={}),
            patch("app.runtime.p2362_full_signal_decision_pipeline.institutional_targets",
                  return_value={"approved": True, "rr": 3.5}),
            patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit",
                  return_value={"emit_allowed": True, "institutional_score": 95}),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def test_missing_correlation_blocks_pipeline(self):
        result = decide_signal(self.signal, self.context)
        self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")
        self.assertEqual(result["paper_lot"], 0)
        self.assertEqual(result["real_orders"], "FORBIDDEN")

    def test_truthy_correlation_text_blocks_pipeline(self):
        result = decide_signal(self.signal, dict(self.context, correlation_ok="false"))
        self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")

    def test_explicit_false_blocks_pipeline(self):
        result = decide_signal(self.signal, dict(self.context, correlation_ok=False))
        self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")

    def test_truthy_precheck_cannot_emit(self):
        with patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit",
                   return_value={"emit_allowed": "false", "institutional_score": 95}):
            result = decide_signal(self.signal, dict(self.context, correlation_ok=True))
        self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")
        self.assertEqual(result["paper_lot"], 0)
        self.assertEqual(result["real_orders"], "FORBIDDEN")

    def test_explicit_true_can_emit_paper(self):
        result = decide_signal(self.signal, dict(self.context, correlation_ok=True))
        self.assertEqual(result["final_decision"], "EMIT_TO_MT5_PAPER")
        self.assertGreater(result["paper_lot"], 0)
        self.assertEqual(result["ftmo_real"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
