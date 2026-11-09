"""ET665.R247: P15.25 dataset root containment (offline, synthetic)."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r247", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class DatasetContainment(unittest.TestCase):
    def test_absolute_path_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset("/tmp/forbidden.csv")

    def test_windows_drive_path_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset("C:\\\\private\\\\trades.csv")

    def test_windows_unc_path_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset("\\\\\\\\server\\\\share\\\\trades.csv")

    def test_windows_backslash_traversal_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset("..\\\\private.csv")

    def test_parent_traversal_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset("../../private.csv")

    def test_non_string_rejected(self):
        with self.assertRaises(ValueError):
            engine().load_dataset(None)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "data/normalized"
            root.mkdir(parents=True)
            outside = Path(temp) / "private.csv"
            outside.write_text("close\n1\n", encoding="utf-8")
            link = root / "escape.csv"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            import os
            before = Path.cwd()
            try:
                os.chdir(temp)
                with self.assertRaises(ValueError):
                    engine().load_dataset("escape.csv")
            finally:
                os.chdir(before)

if __name__ == "__main__":
    unittest.main()
