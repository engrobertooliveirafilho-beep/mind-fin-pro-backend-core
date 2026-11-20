"""ET728 behavioral regressions for short OHLC feeds and duplicate market identity."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("et726", HERE / "test_p1618_ohlc_integrity_et726.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestET728(module.TestET726):
    def test_short_feed_rejected(self):
        cp, report = self.execute(lambda df: df.drop(index=range(50,130), inplace=True))
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("insufficient OHLC candles", cp.stderr)
        self.assertFalse(report)

    def test_short_feed_99_rejected(self):
        cp, report = self.execute(lambda df: df.drop(index=range(99,130), inplace=True))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
