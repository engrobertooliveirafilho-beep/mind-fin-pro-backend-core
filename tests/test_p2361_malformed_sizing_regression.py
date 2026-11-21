import unittest
from app.runtime.p2361_dynamic_position_sizing_engine import dynamic_paper_lot


class MalformedPaperSizingTests(unittest.TestCase):
    def test_malformed_inputs_fail_closed(self):
        base = dict(base_lot=0.1, institutional_score=95, expected_payoff=3.5,
                    current_drawdown=0, correlation_ok=True)
        cases = (("base_lot", None), ("base_lot", "bad"),
                 ("base_lot", object()), ("base_lot", 1.7e308),
                 ("institutional_score", "bad"),
                 ("expected_payoff", None), ("current_drawdown", "bad"))
        for key, value in cases:
            with self.subTest(key=key, value=value):
                result = dynamic_paper_lot(dict(base, **{key: value}))
                self.assertEqual(result["recommended_paper_lot"], 0)
                self.assertEqual(result["real_orders"], "FORBIDDEN")

    def test_non_mapping_context_blocks(self):
        self.assertEqual(dynamic_paper_lot(None)["recommended_paper_lot"], 0)


if __name__ == "__main__":
    unittest.main()
