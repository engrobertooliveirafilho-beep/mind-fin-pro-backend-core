"""ET665.R244: no operational certification from trade-count thresholds alone.

Offline unittest; no broker, network, Drive, or subprocess access.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ENGINE = Path(__file__).resolve().parents[2] / "app" / "p1519_p1525_institutional_research_certification" / "engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r244_p1525", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IndependentApprovalGate(unittest.TestCase):
    def test_profitable_twenty_trade_candidate_is_research_only(self):
        engine = load_engine()
        edge = {"symbol": "DEMO", "timeframe": "H1", "strategy": "sma",
                "fast": 5, "slow": 21, "dataset": "synthetic.csv"}
        trades = [{"return": 0.01} for _ in range(30)]
        curve = [1.01 ** (i + 1) for i in range(30)]
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "report"
            with patch.object(engine, "EDGES", Path(folder) / "edges.json"), \
                 patch.object(engine, "load_json", return_value=[edge]), \
                 patch.object(engine, "reconstruct", return_value=(trades, curve)), \
                 patch.object(engine, "OUT", out, create=True), \
                 patch("pathlib.Path.mkdir", autospec=True) as mkdir_mock:
                # Redirect the hard-coded report path by changing CWD inside an isolated temp folder.
                mkdir_mock.side_effect = lambda p, *a, **kw: None
                with patch("pathlib.Path.write_text", autospec=True) as write_mock:
                    report = engine.run()
            self.assertEqual(report["P15_25_CERTIFICATION"], "RESEARCH_ONLY")
            self.assertEqual(report["APPROVED_EDGES"], 0)
            self.assertEqual(report["EDGE"], "NOT_PROVEN")
            self.assertEqual(report["INDEPENDENT_APPROVAL"], "NOT_PROVEN")
            self.assertEqual(report["CAUSALITY"], "NOT_PROVEN")
            self.assertTrue(write_mock.called)

    def test_no_candidate_does_not_certify(self):
        engine = load_engine()
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(engine, "load_json", return_value=[]), \
                 patch("pathlib.Path.mkdir"), patch("pathlib.Path.write_text"):
                report = engine.run()
        self.assertEqual(report["APPROVED_EDGES"], 0)
        self.assertEqual(report["P15_25_CERTIFICATION"], "RESEARCH_ONLY")


if __name__ == "__main__":
    unittest.main()
