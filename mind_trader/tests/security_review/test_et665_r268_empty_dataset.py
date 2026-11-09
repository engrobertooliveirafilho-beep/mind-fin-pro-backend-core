"""ET665.R268 — empty CSV dataset must fail closed."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r268", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class EmptyDatasetIntegrity(unittest.TestCase):
    def check(self, csv_content):
        with tempfile.TemporaryDirectory() as temp:
            original = Path.cwd()
            try:
                os.chdir(temp)
                root = Path("data/normalized")
                root.mkdir(parents=True)
                (root / "synthetic.csv").write_text(csv_content, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "no price observations"):
                    load_engine().load_dataset("synthetic.csv")
            finally:
                os.chdir(original)

    def test_header_only_rejected(self):
        self.check("close\n")

    def test_blank_rows_rejected(self):
        self.check("close\n\n\n")

if __name__ == "__main__":
    unittest.main()
