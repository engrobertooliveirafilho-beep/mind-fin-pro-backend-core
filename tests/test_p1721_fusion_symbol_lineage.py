"""Offline behavioral regression for P1721 fusion symbol lineage."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION/p1721_to_p1735_fusion_stack.py"
INPUT = Path("reports/P1711_TO_P1720_ADAPTIVE_SPECIALIST_PORTFOLIO/adaptive_specialist_portfolio.json")
OUTPUT = Path("reports/P1721_TO_P1735_MARKET_INTELLIGENCE_FUSION/market_intelligence_fusion.json")

class FusionSymbolTests(unittest.TestCase):
    def run_fusion(self, record):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / INPUT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps([record]), encoding="utf-8")
            (root / OUTPUT).parent.mkdir(parents=True)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=root,
                                    env=env, capture_output=True, text=True, timeout=15)
            rows = json.loads((root / OUTPUT).read_text(encoding="utf-8")) if (root / OUTPUT).exists() else None
            return result, rows

    def test_attested_symbol_preserved(self):
        proc, rows = self.run_fusion({"asset": "EURUSD", "symbol": "eurusd", "timeframe": "H1"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(rows[0]["symbol"], "EURUSD")

    def test_missing_symbol_not_invented(self):
        proc, rows = self.run_fusion({"asset": "EURUSD", "timeframe": "H1"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIsNone(rows[0]["symbol"])

    def test_conflicting_symbol_blocks(self):
        proc, rows = self.run_fusion({"asset": "EURUSD", "symbol": "XAUUSD", "timeframe": "H1"})
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ASSET_SYMBOL_CONFLICT", proc.stderr)
        self.assertIsNone(rows)

    def test_invalid_symbol_blocks(self):
        proc, rows = self.run_fusion({"asset": "EURUSD", "symbol": "EUR/USD", "timeframe": "H1"})
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("INVALID_SOURCE_SYMBOL", proc.stderr)
        self.assertIsNone(rows)

    def test_missing_mandatory_source_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=td,
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SPECIALISTS_SOURCE_UNAVAILABLE", result.stderr)
            self.assertFalse((Path(td) / OUTPUT).exists())

    def test_empty_mandatory_source_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / INPUT
            path.parent.mkdir(parents=True)
            path.write_text("[]", encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=td,
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INVALID_SPECIALISTS_SOURCE", result.stderr)
            self.assertFalse((Path(td) / OUTPUT).exists())

if __name__ == "__main__":
    unittest.main()
