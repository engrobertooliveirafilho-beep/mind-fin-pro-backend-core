import unittest
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot


class CorrelationClearanceTests(unittest.TestCase):
    def setUp(self):
        self.ctx = dict(base_lot=0.1, institutional_score=95, expected_payoff=3.2,
                        current_drawdown=0, last_trade_loss=False)

    def test_missing_correlation_blocks(self):
        self.assertEqual(dynamic_paper_lot(self.ctx)["recommended_paper_lot"], 0)

    def test_truthy_string_correlation_blocks(self):
        self.assertEqual(dynamic_paper_lot(dict(self.ctx, correlation_ok="false"))["recommended_paper_lot"], 0)

    def test_explicit_false_blocks(self):
        self.assertEqual(dynamic_paper_lot(dict(self.ctx, correlation_ok=False))["recommended_paper_lot"], 0)

    def test_explicit_true_allows_paper_only(self):
        result = dynamic_paper_lot(dict(self.ctx, correlation_ok=True))
        self.assertGreater(result["recommended_paper_lot"], 0)
        self.assertEqual(result["real_orders"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
