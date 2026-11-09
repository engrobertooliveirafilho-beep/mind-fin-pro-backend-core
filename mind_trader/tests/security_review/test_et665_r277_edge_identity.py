"""ET665.R277 — reject invalid edge identity before research reconstruction."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r277", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

BASE = {"symbol": "SYN", "timeframe": "H1", "strategy": "sma", "fast": 5, "slow": 21}

class EdgeIdentity(unittest.TestCase):
    def check_invalid(self, changed):
        module = engine()
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[{**BASE, **changed}]), patch.object(module, "reconstruct", return_value=([], [])) as reconstruct:
                    with self.assertRaisesRegex(ValueError, "invalid research edge metadata"):
                        module.run()
                    reconstruct.assert_not_called()
            finally:
                os.chdir(previous)

    def test_missing_symbol(self):
        item = dict(BASE)
        del item["symbol"]
        module = engine()
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[item]), patch.object(module, "reconstruct") as reconstruct:
                    with self.assertRaisesRegex(ValueError, "invalid research edge metadata"):
                        module.run()
                    reconstruct.assert_not_called()
            finally:
                os.chdir(previous)

    def test_blank_timeframe(self):
        self.check_invalid({"timeframe": ""})

    def test_padded_strategy(self):
        self.check_invalid({"strategy": " sma "})

    def test_nonstring_symbol(self):
        self.check_invalid({"symbol": 123})

if __name__ == "__main__":
    unittest.main()
