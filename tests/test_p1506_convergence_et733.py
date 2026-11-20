"""ET733: P1506 fail-closed regression, isolated and offline."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1506_convergence_payoff_scalp_engine.py"
BASE = {"asset":"XAUUSD","timeframe":"M5","family":"a","profile":"b","trades":12,"payoff_ratio_real":2.5,"expectancy_per_trade_real":0.1,"profit_factor_real":2.0,"win_rate":0.6,"avg_holding_bars":2,"ORDER_SENT":False,"REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

class TestP1506(unittest.TestCase):
    def check(self, rows=None):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "reports/P1505_DATA_INGESTION_ENGINE"
            p.mkdir(parents=True)
            if rows is not None:
                (p / "p1505n_edge_trade_metrics.json").write_text(json.dumps(rows))
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=d, capture_output=True, text=True)
            return cp, (p / "p1506_convergence_payoff_scalp_report.json").exists()
    def test_valid(self):
        cp, report = self.check([BASE])
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(report)
    def test_missing(self):
        cp, report = self.check()
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)
    def test_empty(self):
        cp, report = self.check([])
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)
    def test_nan(self):
        cp, report = self.check([{**BASE, "profit_factor_real": float("nan")}])
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)
    def test_unsafe(self):
        cp, report = self.check([{**BASE, "FTMO_REAL": "ALLOWED"}])
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)
    def test_duplicate(self):
        cp, report = self.check([BASE, BASE])
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)
    def test_no_eligible(self):
        cp, report = self.check([{**BASE, "trades": 2}])
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
