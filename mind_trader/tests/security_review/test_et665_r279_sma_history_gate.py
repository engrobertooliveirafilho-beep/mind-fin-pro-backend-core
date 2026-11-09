"""ET665.R279 — insufficient history cannot masquerade as a zero-trade reconstruction."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r279", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

EDGE = {"dataset": "synthetic.csv", "fast": 2, "slow": 4}

class SmaHistoryGate(unittest.TestCase):
    def test_short_history_rejected(self):
        module = engine()
        with patch.object(module, "load_dataset", return_value=[{"close": 100.0}] * 5):
            with self.assertRaisesRegex(ValueError, "insufficient dataset observations"):
                module.reconstruct(EDGE)

    def test_boundary_history_allowed(self):
        module = engine()
        with patch.object(module, "load_dataset", return_value=[{"close": 100.0}] * 6):
            trades, curve = module.reconstruct(EDGE)
            self.assertEqual(trades, [])
            self.assertEqual(curve, [])

if __name__ == "__main__":
    unittest.main()
