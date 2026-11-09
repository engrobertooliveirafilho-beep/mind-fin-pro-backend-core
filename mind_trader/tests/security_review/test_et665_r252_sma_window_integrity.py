"""ET665.R252: invalid SMA parameters fail closed before simulation."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r252", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SmaWindowIntegrity(unittest.TestCase):
    def test_invalid_windows_rejected(self):
        m = engine()
        for fast, slow in ((0, 21), (-1, 21), (5, 0), (5, -2), (21, 21), (22, 21)):
            with self.subTest(fast=fast, slow=slow):
                with patch.object(m, "load_dataset", return_value=[]):
                    with self.assertRaises(ValueError):
                        m.reconstruct({"dataset":"synthetic.csv","fast":fast,"slow":slow})

    def test_valid_window_rejects_insufficient_history(self):
        m = engine()
        with patch.object(m, "load_dataset", return_value=[]):
            with self.assertRaisesRegex(ValueError, "insufficient dataset observations"):
                m.reconstruct({"dataset":"synthetic.csv","fast":5,"slow":21})

if __name__ == "__main__":
    unittest.main()
