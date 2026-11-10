"""ET665.R339 — negative-path research gate; no broker, no production."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def engine_module():
    spec = importlib.util.spec_from_file_location("et665_r339_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class FailClosedResearchGate(unittest.TestCase):
    def test_path_traversal_rejected(self):
        engine = engine_module()
        for name in ("../outside.csv", "/etc/passwd", r"C:\\Windows\\win.ini"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                engine.load_dataset(name)

    def test_nonfinite_csv_price_rejected(self):
        engine = engine_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "data/normalized"
            folder.mkdir(parents=True)
            (folder / "bad.csv").write_text("close\n100\nnan\n", encoding="utf-8")
            old = Path.cwd()
            try:
                os.chdir(root)
                with self.assertRaises(ValueError):
                    engine.load_dataset("bad.csv")
            finally:
                os.chdir(old)

    def test_missing_authority_fails_closed(self):
        engine = engine_module()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                engine.load_json(Path(tmp) / "absent.json")

    def test_duplicate_edge_identifiers_fail_closed(self):
        engine = engine_module()
        edge = {"symbol":"SYNTH","timeframe":"M1","strategy":"SMA","dataset":"synthetic.csv","fast":2,"slow":4}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority = root / "edges.json"
            authority.write_text(json.dumps([edge,edge]), encoding="utf-8")
            old = Path.cwd()
            try:
                os.chdir(root)
                with patch.object(engine,"EDGES",authority), patch.object(engine,"reconstruct",return_value=([],[])):
                    with self.assertRaisesRegex(ValueError,"duplicate edge identifier"):
                        engine.run()
            finally:
                os.chdir(old)

if __name__ == "__main__":
    unittest.main()
