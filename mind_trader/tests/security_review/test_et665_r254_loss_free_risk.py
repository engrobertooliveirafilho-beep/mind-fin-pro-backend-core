"""ET665.R254: a loss-free sample is not independently certified low risk."""
import importlib.util
from pathlib import Path
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r254", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class RiskSampleAdequacy(unittest.TestCase):
    def test_single_win_is_unknown(self):
        result = load_engine().risk_of_ruin([{"return":0.05}])
        self.assertEqual(result["risk_proxy"], "UNKNOWN")
        self.assertIsNone(result["profit_factor"])

    def test_many_wins_without_loss_are_unknown(self):
        result = load_engine().risk_of_ruin([{"return":0.01} for _ in range(100)])
        self.assertEqual(result["risk_proxy"], "UNKNOWN")
        self.assertIsNone(result["profit_factor"])

    def test_flat_returns_without_loss_are_unknown(self):
        result = load_engine().risk_of_ruin([{"return":0.0} for _ in range(30)])
        self.assertEqual(result["risk_proxy"], "UNKNOWN")

    def test_finite_wins_and_losses_keep_proxy(self):
        result = load_engine().risk_of_ruin([{"return":0.03}, {"return":-0.01}])
        self.assertEqual(result["risk_proxy"], "LOW")
        self.assertEqual(result["profit_factor"], 3.0)

if __name__ == "__main__":
    unittest.main()
