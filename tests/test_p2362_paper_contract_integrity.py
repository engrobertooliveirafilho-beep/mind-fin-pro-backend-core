import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class PaperContractTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    def test_unsafe_precheck_contract_blocks_before_sizing(self, _edge):
        signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 2}
        context = {"swing_high": 110, "swing_low": 90}
        for field, value in (("mode", "LIVE"), ("real_orders", "ALLOWED"), ("ftmo_real", "ALLOWED")):
            precheck = {"emit_allowed": True, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
            precheck[field] = value
            with self.subTest(field=field):
                with patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit", return_value=precheck):
                    with patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot") as sizing:
                        result = decide_signal(signal, context)
                        sizing.assert_not_called()
                self.assertEqual(result["final_decision"], "BLOCK_PRECHECK")
                self.assertEqual(result["paper_lot"], 0)

    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge", return_value={})
    @patch("app.runtime.p2362_full_signal_decision_pipeline.precheck_before_mt5_emit",
           return_value={"emit_allowed": True, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"})
    def test_unsafe_sizing_contract_blocks(self, _precheck, _edge):
        signal = {"side": "BUY", "entry": 100, "stop": 99, "expected_payoff": 2}
        context = {"swing_high": 110, "swing_low": 90}
        for field, value in (("mode", "LIVE"), ("real_orders", "ALLOWED"), ("ftmo_real", "ALLOWED")):
            sizing = {"recommended_paper_lot": 0.01, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
            sizing[field] = value
            with self.subTest(field=field):
                with patch("app.runtime.p2362_full_signal_decision_pipeline.dynamic_paper_lot", return_value=sizing):
                    result = decide_signal(signal, context)
                self.assertEqual(result["final_decision"], "BLOCK_SIGNAL")
                self.assertEqual(result["paper_lot"], 0)


if __name__ == "__main__":
    unittest.main()
