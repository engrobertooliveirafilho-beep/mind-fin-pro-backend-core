"""ET727: reject nonfinite market data and nonpositive OHLC prices."""
import unittest
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
BASE = HERE / "test_p1618_ohlc_integrity_et726.py"
spec = importlib.util.spec_from_file_location("et726", BASE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestET727(module.TestET726):
    def test_infinite_high(self):
        cp, report = self.execute(lambda df: df.loc.__setitem__((1, "high"), float("inf")))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_negative_ohlc(self):
        def mutate(df):
            for col in ("open", "high", "low", "close"):
                df.loc[1, col] = -1
        cp, report = self.execute(mutate)
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_nan_indicator(self):
        cp, report = self.execute(lambda df: df.loc.__setitem__((1, "rsi_14"), float("nan")))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
