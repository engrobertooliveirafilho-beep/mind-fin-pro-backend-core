"""ET665.R266 — SMA window parsing must not silently truncate or accept booleans."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r266", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class StrictWindowIntegrity(unittest.TestCase):
    def test_invalid_window_types_fail_closed(self):
        module = load_engine()
        with patch.object(module, "load_dataset", return_value=[{"close": 100.0}] * 30):
            for value in (1.9, True, False, "1.9", "1e2", "-1", " 5 ", None):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    module.reconstruct({"dataset": "synthetic.csv", "fast": value, "slow": 21})

    def test_valid_integer_and_decimal_string_windows(self):
        module = load_engine()
        with patch.object(module, "load_dataset", return_value=[{"close": 100.0}] * 30):
            for fast, slow in ((5, 21), ("5", "21")):
                with self.subTest(fast=fast, slow=slow):
                    trades, curve = module.reconstruct({"dataset": "synthetic.csv", "fast": fast, "slow": slow})
                    self.assertEqual((trades, curve), ([], []))

if __name__ == "__main__":
    unittest.main()
