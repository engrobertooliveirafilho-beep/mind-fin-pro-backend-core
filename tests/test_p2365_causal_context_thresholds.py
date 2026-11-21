import unittest
import pandas as pd
from app.runtime.p2365_causal_context_thresholds import causal_context_thresholds


class P2365CausalThresholdTests(unittest.TestCase):
    def setUp(self):
        n = 320
        self.df = pd.DataFrame({
            "time": pd.date_range("2025-01-01", periods=n, freq="5min"),
            "close": [100 + i * 0.1 + (i % 7) for i in range(n)],
            "high": [101 + i * 0.1 + (i % 7) for i in range(n)],
            "low": [99 + i * 0.1 + (i % 7) for i in range(n)],
        })

    def test_prefix_invariance(self):
        a = causal_context_thresholds(self.df.iloc[:270])
        b = causal_context_thresholds(self.df)
        for key in ("vol_q30", "vol_q70", "price_median"):
            pd.testing.assert_series_equal(a[key], b[key].iloc[:270])

    def test_no_promotion(self):
        self.assertFalse(causal_context_thresholds(self.df)["promotion_allowed"].any())

    def test_unsorted_and_duplicate_times_block(self):
        for bad in (self.df.iloc[::-1], pd.concat([self.df, self.df.iloc[[-1]]])):
            with self.assertRaises(ValueError):
                causal_context_thresholds(bad)

    def test_impossible_ohlc_bars_block(self):
        for field, value in (("close", 0), ("high", -1), ("low", 100000)):
            bad = self.df.copy()
            bad.loc[220, field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                causal_context_thresholds(bad)

    def test_invalid_timestamp_blocks(self):
        bad = self.df.copy()
        bad["time"] = bad["time"].astype(str)
        bad.loc[220, "time"] = "not-a-date"
        with self.assertRaises(ValueError):
            causal_context_thresholds(bad)

    def test_timestamp_normalization(self):
        frame = self.df.copy()
        frame["time"] = frame["time"].astype(str)
        result = causal_context_thresholds(frame)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["time"]))

    def test_nonfinite_prices_block(self):
        bad = self.df.copy()
        bad.loc[220, "close"] = float("inf")
        with self.assertRaises(ValueError):
            causal_context_thresholds(bad)


if __name__ == "__main__":
    unittest.main()
