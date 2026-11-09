"""ET665.R269 — duplicate CSV headers are ambiguous and must be rejected."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r269", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class DuplicateCsvColumns(unittest.TestCase):
    def check(self, content, rejected):
        with tempfile.TemporaryDirectory() as temp:
            original = Path.cwd()
            try:
                os.chdir(temp)
                root = Path("data/normalized")
                root.mkdir(parents=True)
                (root / "synthetic.csv").write_text(content, encoding="utf-8")
                if rejected:
                    with self.assertRaisesRegex(ValueError, "duplicate CSV columns"):
                        engine().load_dataset("synthetic.csv")
                else:
                    return engine().load_dataset("synthetic.csv")
            finally:
                os.chdir(original)

    def test_duplicate_close_rejected(self):
        self.check("close,close\n100,200\n", True)

    def test_duplicate_other_column_rejected(self):
        self.check("close,volume,volume\n100,1,2\n", True)

    def test_unique_columns_allowed(self):
        rows = self.check("close,volume\n100,1\n", False)
        self.assertEqual(rows[0]["close"], 100.0)

if __name__ == "__main__":
    unittest.main()
