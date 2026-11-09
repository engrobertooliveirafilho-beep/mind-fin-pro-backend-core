"""ET665.R270 — do not present trade-index correlation as time-aligned evidence."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r270", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class UnalignedTradeCorrelation(unittest.TestCase):
    def test_equal_length_trade_returns_remain_unverified(self):
        module = engine()
        edges = [
            {"symbol": symbol, "timeframe": "H1", "strategy": "sma", "fast": 5, "slow": 21}
            for symbol in ("A", "B")
        ]
        trades = [{"return": v} for v in (0.01, -0.02, 0.03)]
        curve = [1.01, 0.9898, 1.019494]
        with tempfile.TemporaryDirectory() as temp:
            before = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=edges), patch.object(module, "reconstruct", return_value=(trades, curve)):
                    module.run()
                output = Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION/correlation_engine.json")
                rows = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(len(rows), 1)
                self.assertIsNone(rows[0]["pearson_return_corr"])
                self.assertEqual(rows[0]["evidence"], "UNALIGNED_TRADE_TIMESTAMPS")
            finally:
                os.chdir(before)

if __name__ == "__main__":
    unittest.main()
