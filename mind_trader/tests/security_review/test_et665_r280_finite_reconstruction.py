"""ET665.R280 — reject nonfinite reconstruction arithmetic."""
import importlib.util
import math
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r280", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

EDGE = {"dataset": "synthetic.csv", "fast": 2, "slow": 4}
CROSSOVERS = [2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1]

class NonfiniteReconstruction(unittest.TestCase):
    def test_overflowing_trade_return_rejected(self):
        module = engine()
        closes = [100.0] * 8
        closes[5], closes[6] = 1e-300, 1e300
        with patch.object(module, "load_dataset", return_value=[{"close": x} for x in closes]), patch.object(module, "sma", side_effect=CROSSOVERS):
            with self.assertRaisesRegex(ValueError, "nonfinite reconstructed trade return"):
                module.reconstruct(EDGE)

    def test_finite_trade_return_retained(self):
        module = engine()
        closes = [100.0] * 8
        closes[5], closes[6] = 100.0, 110.0
        with patch.object(module, "load_dataset", return_value=[{"close": x} for x in closes]), patch.object(module, "sma", side_effect=CROSSOVERS):
            trades, curve = module.reconstruct(EDGE)
        self.assertEqual(len(trades), 1)
        self.assertTrue(math.isfinite(trades[0]["return"]))
        self.assertTrue(math.isfinite(curve[0]))

if __name__ == "__main__":
    unittest.main()
