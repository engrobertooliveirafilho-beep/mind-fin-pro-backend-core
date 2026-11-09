"""ET665.R253: risk proxy must not certify zero observations."""
import importlib.util
import math
from pathlib import Path
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r253", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class RiskEvidence(unittest.TestCase):
    def test_no_trades_is_unknown_not_low(self):
        result = load_engine().risk_of_ruin([])
        self.assertEqual(result["risk_proxy"], "UNKNOWN")
        self.assertIsNone(result["profit_factor"])

    def test_invalid_returns_rejected(self):
        module = load_engine()
        for value in (float("nan"), float("inf"), -float("inf"), "0.01", True):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                module.risk_of_ruin([{"return":value}])

    def test_finite_trades_still_evaluated(self):
        result = load_engine().risk_of_ruin([{"return":0.03},{"return":-0.01}])
        self.assertEqual(result["risk_proxy"], "LOW")
        self.assertEqual(result["max_loss_streak"], 1)

if __name__ == "__main__":
    unittest.main()
