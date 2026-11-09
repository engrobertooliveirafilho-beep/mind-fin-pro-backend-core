"""ET665.R278: trade count alone must never promote PAPER candidates."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r278", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class NoAutomaticPaperPromotion(unittest.TestCase):
    def check(self, count):
        module = engine()
        edge = {"symbol": "SYN", "timeframe": "H1", "strategy": "sma", "fast": 5, "slow": 21}
        trades = [{"return": 0.01} for _ in range(count)]
        curve = [1.01 ** i for i in range(1, count + 1)]
        with tempfile.TemporaryDirectory() as temp:
            before = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[edge]), patch.object(module, "reconstruct", return_value=(trades, curve)):
                    module.run()
                import json
                rows = json.loads(Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION/trade_reconstruction.json").read_text(encoding="utf-8"))
                self.assertEqual(rows[0]["research_eligibility"], "RESEARCH_ONLY_UNVERIFIED")
                self.assertIs(rows[0]["paper_promotion_authorized"], False)
                self.assertIs(rows[0]["independent_approval"], False)
            finally:
                os.chdir(before)

    def test_many_trades_do_not_promote(self):
        self.check(25)

    def test_few_trades_do_not_promote(self):
        self.check(2)

if __name__ == "__main__":
    unittest.main()
