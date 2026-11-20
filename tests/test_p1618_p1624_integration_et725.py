"""ET725 seven-engine integration: original specialists + explicitly synthetic OHLC."""
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

class TestSevenEngineIntegration(unittest.TestCase):
    def test_seven_engines_paper_only(self):
        if not ORIGINAL.is_file():
            raise AssertionError("canonical specialist library unavailable")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ORIGINAL, p)
            f = root / "data/features/XAUUSD_M5_features.csv"
            f.parent.mkdir(parents=True, exist_ok=True)
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
                "fibo_zone": ["NONE"]*n,
            })
            df.to_csv(f, index=False)
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            reports = root / "reports"
            paths = [
                "P1618_MARKET_STRUCTURE_ENGINE/market_structure_snapshot.json",
                "P1619_CANDLE_TRIGGER_ENGINE/candle_trigger_snapshot.json",
                "P1620_CONFLUENCE_ENGINE/confluence_snapshot.json",
                "P1621_ASSET_INTELLIGENCE_LIBRARY/asset_intelligence_library.json",
                "P1622_SPECIALIST_KNOWLEDGE_BASE/specialist_knowledge_base.json",
                "P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json",
                "P1624_SEASONALITY_ENGINE/seasonality_snapshot.json",
            ]
            outputs = [json.loads((reports / name).read_text(encoding="utf-8")) for name in paths]
            self.assertTrue(all(isinstance(rows, list) and rows for rows in outputs))
            self.assertEqual(len(outputs[2]), 1)
            self.assertTrue(all(row["decision"] == "WATCH_ONLY" and row["ORDER_SENT"] is False and row["FTMO_REAL"] == "FORBIDDEN" for row in outputs[5]))
            master = json.loads((reports / "P1623_OPPORTUNITY_RANKING_ENGINE/p1623_master_market_intelligence_report.json").read_text(encoding="utf-8"))
            self.assertEqual(master["CONFLUENCE_ROWS"], 1)
            self.assertEqual(master["OPPORTUNITIES_RANKED"], len(outputs[5]))
            self.assertFalse(master["ORDER_SENT"])

if __name__ == "__main__":
    unittest.main()
