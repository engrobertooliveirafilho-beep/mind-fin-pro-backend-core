"""ET665.R276 — missing/malformed edge authority input fails closed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine():
    spec = importlib.util.spec_from_file_location("et665_r276", ENGINE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class EdgeAuthorityInput(unittest.TestCase):
    def test_missing_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(FileNotFoundError, "research edge input is missing"):
                engine().load_json(Path(temp) / "missing.json")

    def test_object_instead_of_array_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "edges.json"
            p.write_text('{"symbol":"SYN"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "list of objects"):
                engine().load_json(p)

    def test_non_object_array_entry_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "edges.json"
            p.write_text('[{"symbol":"SYN"}, null]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "list of objects"):
                engine().load_json(p)

    def test_valid_empty_array_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "edges.json"
            p.write_text("[]", encoding="utf-8")
            self.assertEqual(engine().load_json(p), [])

if __name__ == "__main__":
    unittest.main()
