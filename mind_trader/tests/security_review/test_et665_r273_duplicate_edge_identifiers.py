"""ET665.R273 — duplicate edge IDs must not overwrite research evidence."""
import importlib.util
from pathlib import Path
import tempfile
import os
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r273", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def edge():
    return {"symbol": "SYN", "timeframe": "H1", "strategy": "sma", "fast": 5, "slow": 21, "dataset": "synthetic.csv"}

class DuplicateEdgeIntegrity(unittest.TestCase):
    def test_duplicate_edges_fail_closed(self):
        module = engine()
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[edge(), dict(edge())]), patch.object(module, "reconstruct", return_value=([], [])):
                    with self.assertRaisesRegex(ValueError, "duplicate edge identifier"):
                        module.run()
            finally:
                os.chdir(previous)

    def test_unique_edges_remain_research_only(self):
        module = engine()
        other = {**edge(), "symbol": "SYN2"}
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with patch.object(module, "load_json", return_value=[edge(), other]), patch.object(module, "reconstruct", return_value=([], [])):
                    result = module.run()
                    self.assertEqual(result["APPROVED_EDGES"], 0)
                    self.assertEqual(result["P15_19_TRADE_RECONSTRUCTION"], 2)
            finally:
                os.chdir(previous)

if __name__ == "__main__":
    unittest.main()
