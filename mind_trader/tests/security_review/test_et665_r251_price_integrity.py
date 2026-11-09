"""ET665.R251: reject malformed or nonfinite research prices."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r251", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class PriceIntegrity(unittest.TestCase):
    def test_nonfinite_prices_rejected(self):
        m = engine()
        for value in ("nan", "inf", "-inf", "NaN"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.f(value)

    def test_invalid_price_rejected(self):
        m = engine()
        for value in ("not-a-price", None, ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.f(value)

    def test_finite_price_allowed(self):
        self.assertEqual(engine().f("101.25"), 101.25)

    def test_malformed_csv_does_not_return_empty_success(self):
        m = engine()
        with tempfile.TemporaryDirectory() as temp:
            import os
            before = Path.cwd()
            try:
                os.chdir(temp)
                root = Path("data/normalized")
                root.mkdir(parents=True)
                (root / "synthetic.csv").write_text("close\nnot-a-price\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    m.load_dataset("synthetic.csv")
            finally:
                os.chdir(before)

if __name__ == "__main__":
    unittest.main()
