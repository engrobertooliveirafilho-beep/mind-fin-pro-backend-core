"""ET726: reject OHLC temporal disorder and invalid price bounds."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import pandas as pd

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1618_to_p1624_market_intelligence_stack.py"
ORIGINAL = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical")) / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"

class TestET726(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ORIGINAL.is_file():
            raise AssertionError("original specialist library unavailable")

    def execute(self, mutate=None):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"
            target.parent.mkdir(parents=True)
            shutil.copyfile(ORIGINAL, target)
            f = root / "data/features/XAUUSD_M5_features.csv"
            f.parent.mkdir(parents=True)
            n = 130
            df = pd.DataFrame({
                "time": pd.date_range("2025-01-01", periods=n, freq="5min"),
                "open": [100+i*.01 for i in range(n)],
                "high": [101+i*.01 for i in range(n)],
                "low": [99+i*.01 for i in range(n)],
                "close": [100.5+i*.01 for i in range(n)],
                "ema_21": [100]*n, "ema_55": [99]*n,
                "donchian_high_20": [102]*n, "donchian_low_20": [98]*n,
                "rsi_14": [50]*n, "bb_position": [.5]*n,
                "macd": [1]*n, "macd_signal": [0]*n,
                "fibo_zone": ["NONE"]*n
            })
            if mutate:
                mutate(df)
            df.to_csv(f, index=False)
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / "reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1623_master_market_intelligence_report.json"
            return cp, report.exists()

    def test_valid_controlled_ohlc(self):
        cp, exists = self.execute()
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(exists)

    def test_reversed_time(self):
        cp, exists = self.execute(lambda df: df.sort_values("time", ascending=False, inplace=True))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(exists)

    def test_duplicate_time(self):
        cp, exists = self.execute(lambda df: df.loc.__setitem__((1, "time"), df.loc[0, "time"]))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(exists)

    def test_invalid_high(self):
        cp, exists = self.execute(lambda df: df.loc.__setitem__((1, "high"), 0))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(exists)

if __name__ == "__main__":
    unittest.main()
