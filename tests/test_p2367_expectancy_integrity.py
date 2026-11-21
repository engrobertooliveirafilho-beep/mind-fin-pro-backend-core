import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2367ExpectancyTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot", return_value={"recommended_paper_lot": 0})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit", return_value={"emit_allowed": False})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_target_rr_does_not_inflate_expected_payoff(self, _edge, precheck, _sizing):
        signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 0.8}
        out = decide_signal(signal, {"swing_high": 110, "swing_low": 90})
        self.assertTrue(out["targeting"]["approved"])
        self.assertEqual(precheck.call_args.args[0]["expected_payoff"], 0.8)
        self.assertEqual(out["real_orders"], "FORBIDDEN")

    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_invalid_payoff_blocks_before_precheck(self, _edge):
        for value in ("bad", float("nan"), True, -1):
            with self.subTest(value=value):
                signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": value}
                out = decide_signal(signal, {"swing_high": 110, "swing_low": 90})
                self.assertEqual(out["final_decision"], "BLOCK_INVALID_EXPECTANCY")
                self.assertEqual(out["paper_lot"], 0)
                self.assertEqual(out["ftmo_real"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
