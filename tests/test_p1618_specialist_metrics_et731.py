"""ET731: nonfinite specialist metrics must fail before any report generation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1618_to_p1624_market_intelligence_stack.py"
ORIGINAL = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical")) / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"

class TestET731(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ORIGINAL.is_file():
            raise AssertionError("canonical specialist library unavailable")
        cls.original = json.loads(ORIGINAL.read_text(encoding="utf-8"))

    def run_case(self, field=None, value=None):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"
            target.parent.mkdir(parents=True)
            data = copy.deepcopy(self.original)
            if field:
                data[0][field] = value
            target.write_text(json.dumps(data), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse((root / "reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1623_master_market_intelligence_report.json").exists())
            return cp.stderr

    def test_original_without_ohlc(self):
        self.assertIn("original OHLC feature CSV files unavailable", self.run_case())
    def test_nan_expectancy(self):
        self.assertIn("invalid specialist metric", self.run_case("expectancy_per_trade_real", float("nan")))
    def test_infinite_profit_factor(self):
        self.assertIn("invalid specialist metric", self.run_case("profit_factor_real", float("inf")))
    def test_nan_holding(self):
        self.assertIn("invalid specialist metric", self.run_case("avg_holding_bars", float("nan")))
    def test_infinite_entry_hour(self):
        self.assertIn("invalid specialist metric", self.run_case("best_entry_hour", float("inf")))

if __name__ == "__main__":
    unittest.main()
