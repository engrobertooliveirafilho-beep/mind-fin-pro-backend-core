import unittest
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot


class InvalidPaperSizingTests(unittest.TestCase):
    def test_nonfinite_or_nonpositive_inputs_block(self):
        base = dict(base_lot=0.1, institutional_score=95, expected_payoff=3.5,
                    current_drawdown=0, correlation_ok=True)
        cases = (("base_lot", -0.1), ("base_lot", 0),
                 ("base_lot", float("nan")), ("base_lot", float("inf")),
                 ("institutional_score", float("nan")),
                 ("expected_payoff", float("inf")),
                 ("current_drawdown", -1), ("current_drawdown", float("nan")))
        for field, value in cases:
            with self.subTest(field=field, value=value):
                result = dynamic_paper_lot(dict(base, **{field: value}))
                self.assertEqual(result["recommended_paper_lot"], 0)
                self.assertEqual(result["real_orders"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
