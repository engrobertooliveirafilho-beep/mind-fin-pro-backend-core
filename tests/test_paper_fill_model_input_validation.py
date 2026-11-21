import unittest
from mind_trader.app.execution.paper_fill_model import simulate_fill


class PaperFillModelInputValidationTests(unittest.TestCase):
    def test_valid_buy_and_sell(self):
        self.assertTrue(simulate_fill({"entry": 100, "stop": 95, "target": 110, "side": "BUY"})["filled"])
        self.assertTrue(simulate_fill({"entry": 100, "stop": 105, "target": 90, "side": "SELL"})["filled"])

    def test_rejects_invalid_bracket_geometry(self):
        self.assertFalse(simulate_fill({"entry": 100, "stop": 101, "target": 110, "side": "BUY"})["filled"])
        self.assertFalse(simulate_fill({"entry": 100, "stop": 105, "target": 101, "side": "SELL"})["filled"])

    def test_rejects_nonfinite_and_boolean_prices(self):
        for value in (float("nan"), float("inf"), True, "bad", None):
            with self.subTest(value=value):
                self.assertFalse(simulate_fill({"entry": value, "stop": 95, "target": 110})["filled"])

    def test_rejects_negative_or_nonfinite_costs(self):
        for costs in ({"spread": -1}, {"slippage": float("nan")}, {"commission": -0.1}):
            with self.subTest(costs=costs):
                self.assertFalse(simulate_fill({"entry": 100, "stop": 95, "target": 110}, **costs)["filled"])

    def test_rejects_non_dict_order_and_non_string_side(self):
        self.assertFalse(simulate_fill(None)["filled"])
        self.assertFalse(simulate_fill({"entry": 100, "stop": 95, "target": 110, "side": 1})["filled"])


if __name__ == "__main__":
    unittest.main()
