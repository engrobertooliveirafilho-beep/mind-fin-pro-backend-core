"""ET665.R265 — absent dataset must not look like a valid empty backtest."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r265", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class MissingDatasetFailClosed(unittest.TestCase):
    def test_missing_dataset_raises(self):
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with self.assertRaisesRegex(FileNotFoundError, "dataset not found"):
                    load_engine().load_dataset("missing.csv")
            finally:
                os.chdir(previous)

    def test_missing_dataset_blocks_reconstruction(self):
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                with self.assertRaises(FileNotFoundError):
                    load_engine().reconstruct({"dataset": "missing.csv", "fast": 5, "slow": 21})
            finally:
                os.chdir(previous)

if __name__ == "__main__":
    unittest.main()
