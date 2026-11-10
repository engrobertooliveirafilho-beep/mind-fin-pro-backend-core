"""ET665.R338 — actual P15.19–P15.25 report pipeline, synthetic PAPER inputs.

Runs engine.run() from a temporary directory. No real broker or network access.
"""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"
PRICES = [100,99,98,97,96,97,98,99,100,101,100,99,98,97,96,95,94,95,96,97,98,99,100,99,98,97,96]

def engine_module():
    spec = importlib.util.spec_from_file_location("et665_r338_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class ReportPipelineE2E(unittest.TestCase):
    def test_synthetic_csv_to_persisted_research_report(self):
        engine = engine_module()
        with tempfile.TemporaryDirectory(prefix="et665_r338_") as tmp:
            root = Path(tmp)
            dataset_dir = root / "data/normalized"
            dataset_dir.mkdir(parents=True)
            (dataset_dir / "synthetic.csv").write_text(
                "close\n" + "".join(f"{v}\n" for v in PRICES), encoding="utf-8")
            authority = root / "edges.json"
            authority.write_text(json.dumps([{
                "symbol":"SYNTH", "timeframe":"M1", "strategy":"SMA_CROSS",
                "dataset":"synthetic.csv", "fast":2, "slow":4
            }]), encoding="utf-8")
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch.object(engine, "EDGES", authority):
                    report = engine.run()
            finally:
                os.chdir(previous)
            out = root / "reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION"
            expected = ("trade_reconstruction.json", "correlation_engine.json",
                        "dynamic_allocator.json", "institutional_certification.json")
            self.assertTrue(all((out / name).is_file() for name in expected))
            trades = json.loads((out / expected[0]).read_text(encoding="utf-8"))
            persisted = json.loads((out / expected[3]).read_text(encoding="utf-8"))
            self.assertEqual(trades[0]["trades"], 2)
            self.assertEqual(trades[0]["status"], "RESEARCH_ONLY")
            self.assertFalse(trades[0]["paper_promotion_authorized"])
            self.assertFalse(trades[0]["independent_approval"])
            self.assertEqual(trades[0]["real_orders"], "FORBIDDEN")
            self.assertEqual(persisted["P15_19_TRADE_RECONSTRUCTION"], 1)
            self.assertEqual(persisted["APPROVED_EDGES"], 0)
            self.assertEqual(persisted["REAL_ORDERS"], "FORBIDDEN")
            self.assertFalse(persisted["EXPORT_READY"])
            self.assertEqual(report["STATUS"], persisted["STATUS"])

if __name__ == "__main__":
    unittest.main()
