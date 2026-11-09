"""ET665.R255 — offline correlation evidence integrity."""
import importlib.util
from pathlib import Path
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r255", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CorrelationEvidence(unittest.TestCase):
    def test_unequal_samples_rejected(self):
        with self.assertRaises(ValueError):
            load_engine().corr([0.1, 0.2, 0.3], [0.1, 0.2])

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            load_engine().corr([0.1, float("nan"), 0.3], [0.1, 0.2, 0.3])

    def test_insufficient_samples_are_unknown(self):
        self.assertIsNone(load_engine().corr([0.1, 0.2], [0.2, 0.1]))

    def test_constant_series_undefined_not_zero(self):
        self.assertIsNone(load_engine().corr([0.1, 0.1, 0.1], [0.1, 0.2, 0.3]))

    def test_finite_aligned_series_remains_calculable(self):
        self.assertEqual(load_engine().corr([1, 2, 3], [2, 4, 6]), 1.0)

if __name__ == "__main__":
    unittest.main()
