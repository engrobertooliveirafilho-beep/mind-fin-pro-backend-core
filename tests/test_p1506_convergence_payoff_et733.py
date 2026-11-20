"""P1506 fail-closed behavioral regressions. Original P1505 metrics are not required for synthetic tests."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1506_convergence_payoff_scalp_engine.py"
BASE = {"asset":"XAUUSD","timeframe":"M5","family":"alpha","profile":"paper","edge_id":"canonical-test-edge","trades":20,"payoff_ratio_real":2.2,"expectancy_per_trade_real":0.1,"profit_factor_real":1.8,"win_rate":0.6,"avg_holding_bars":3,"ORDER_SENT":False,"REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

class TestP1506(unittest.TestCase):
    def check(self, mutation=None, accepted=False):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "reports/P1505_DATA_INGESTION_ENGINE/p1505n_edge_trade_metrics.json"
            source.parent.mkdir(parents=True)
            rows = [dict(BASE)]
            if mutation:
                mutation(rows)
            source.write_text(json.dumps(rows), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=td, capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0 if accepted else 1, cp.stderr)
            output = source.parent / "p1506_convergence_payoff_scalp_report.json"
            self.assertEqual(output.exists(), accepted)
            if accepted:
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["VALID_EDGES"], 1)
                self.assertFalse(report["ORDER_SENT"])
    def test_canonical_p1505_historical_integration(self):
        import os
        canonical = Path(os.environ.get("ELDORA_P1505_CANONICAL", "/mnt/data/p1505n_edge_trade_metrics.json"))
        if not canonical.is_file():
            self.skipTest("original P1505 metrics not available on this runner")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "reports/P1505_DATA_INGESTION_ENGINE/p1505n_edge_trade_metrics.json"
            target.parent.mkdir(parents=True)
            target.write_bytes(canonical.read_bytes())
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=td, capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            report = json.loads((target.parent / "p1506_convergence_payoff_scalp_report.json").read_text(encoding="utf-8"))
            ranked = json.loads((target.parent / "p1506_ranked_convergence_payoff_edges.json").read_text(encoding="utf-8"))
            self.assertEqual(report["INPUT_EDGES"], 245)
            self.assertEqual(report["VALID_EDGES"], 106)
            self.assertEqual(report["SCALP_CANDIDATES"], 58)
            self.assertTrue(all(edge["ORDER_SENT"] is False and edge["FTMO_REAL"] == "FORBIDDEN" for edge in ranked))
    def test_valid(self): self.check(accepted=True)
    def test_empty(self): self.check(lambda rows: rows.clear())
    def test_duplicate(self): self.check(lambda rows: rows.append(dict(rows[0])))
    def test_nan(self): self.check(lambda rows: rows[0].update(win_rate=math.nan))
    def test_unsafe(self): self.check(lambda rows: rows[0].update(FTMO_REAL="ALLOWED"))
    def test_out_of_bounds(self): self.check(lambda rows: rows[0].update(win_rate=1.1))
    def test_no_eligible(self): self.check(lambda rows: rows[0].update(trades=1))

if __name__ == "__main__":
    unittest.main()
