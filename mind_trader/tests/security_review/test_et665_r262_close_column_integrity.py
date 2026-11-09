"""ET665.R262: missing and nonpositive close prices must fail closed."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r262", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class DatasetCloseIntegrity(unittest.TestCase):
    def check_csv(self, content, expected_error=None):
        with tempfile.TemporaryDirectory() as temp:
            before = Path.cwd()
            try:
                os.chdir(temp)
                root = Path("data/normalized")
                root.mkdir(parents=True)
                (root / "synthetic.csv").write_text(content, encoding="utf-8")
                if expected_error:
                    with self.assertRaisesRegex(ValueError, expected_error):
                        engine().load_dataset("synthetic.csv")
                else:
                    return engine().load_dataset("synthetic.csv")
            finally:
                os.chdir(before)

    def test_missing_column(self):
        self.check_csv("price\\n100\\n".replace("\\n", "\n"), "missing required close")

    def test_missing_cell(self):
        self.check_csv("close\\n\\n100\\n".replace("\\n", "\n"), "invalid numeric dataset value")

    def test_nonpositive_prices(self):
        for value in ("0", "-1"):
            with self.subTest(value=value):
                self.check_csv("close\\n" + value + "\\n", "must be positive")

    def test_positive_rows_retained(self):
        rows = self.check_csv("close\\n100.25\\n101.5\\n".replace("\\n", "\n"))
        self.assertEqual([row["close"] for row in rows], [100.25, 101.5])

if __name__ == "__main__":
    unittest.main()
