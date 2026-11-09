"""ET665.R272 — reject blank or padded CSV header names."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r272", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class HeaderIntegrity(unittest.TestCase):
    def check(self, content, invalid):
        with tempfile.TemporaryDirectory() as temp:
            previous = Path.cwd()
            try:
                os.chdir(temp)
                root = Path("data/normalized")
                root.mkdir(parents=True)
                (root / "synthetic.csv").write_text(content, encoding="utf-8")
                if invalid:
                    with self.assertRaisesRegex(ValueError, "invalid CSV column name"):
                        engine().load_dataset("synthetic.csv")
                else:
                    return engine().load_dataset("synthetic.csv")
            finally:
                os.chdir(previous)

    def test_blank_header_rejected(self):
        self.check("close,\n100,1\n", True)

    def test_padded_header_rejected(self):
        self.check("close, volume\n100,1\n", True)

    def test_valid_headers_retained(self):
        rows = self.check("close,volume\n100,1\n", False)
        self.assertEqual(rows[0]["close"], 100.0)

if __name__ == "__main__":
    unittest.main()
