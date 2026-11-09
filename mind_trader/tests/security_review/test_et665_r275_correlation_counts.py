"""ET665.R275 — unverified pairs are not certified correlations."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r275", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class CorrelationCounts(unittest.TestCase):
    def test_three_edges_have_three_unverified_pairs_and_zero_verified(self):
        module = engine()
        edges = [{"symbol": symbol, "timeframe": "H1", "strategy": "sma", "fast": 5, "slow": 21}
                 for symbol in ("A", "B", "C")]
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=edges), patch.object(module, "reconstruct", return_value=([], [])):
                    report = module.run()
                self.assertEqual(report["P15_20_CORRELATIONS"], 0)
                self.assertEqual(report["P15_20_UNVERIFIED_PAIRS"], 3)
                self.assertFalse(report["EXPORT_READY"])
            finally:
                os.chdir(previous)

if __name__ == "__main__":
    unittest.main()
