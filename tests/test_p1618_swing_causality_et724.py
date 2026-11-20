"""ET724: causal confirmation of centered five-candle swing observations."""
import unittest
import pandas as pd
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1618_to_p1624_market_intelligence_stack.py"

class TestSwingCausality(unittest.TestCase):
    def check_prefix_invariance(self, values, high):
        series = pd.Series(values)
        def confirmed(v):
            x = pd.Series(v)
            swing = (x.rolling(5, center=True).max() if high else x.rolling(5, center=True).min()) == x
            return x.where(swing).ffill().shift(3)
        full = confirmed(values)
        for end in range(7, len(values)):
            actual = confirmed(values[:end]).iloc[-1]
            expected = full.iloc[end-1]
            if pd.isna(expected):
                self.assertTrue(pd.isna(actual))
            else:
                self.assertEqual(actual, expected)

    def test_swing_high_no_future_leakage(self):
        self.check_prefix_invariance([3,4,9,4,3,2,1,2,3,10,4,2,1,3,4,8,2,1,4,5], True)

    def test_swing_low_no_future_leakage(self):
        self.check_prefix_invariance([9,8,1,7,8,9,10,8,7,0,8,9,10,7,8,2,9,10,7,6], False)

    def test_source_confirmed_lag(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(source.count(".ffill().shift(3)"), 2)
        self.assertNotIn(".ffill().shift(1)", source)

if __name__ == "__main__":
    unittest.main()
