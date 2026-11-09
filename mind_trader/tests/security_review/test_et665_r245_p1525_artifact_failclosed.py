"""ET665.R245 — P15.25 persisted-artifact and independent-authority regressions.

Offline standard-library tests. Never contacts MT5, broker, Drive, or the network.
Executes the actual research engine against synthetic mocked trade results in a
temporary working directory; checks the JSON written to disk, not just run().
"""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app" / "p1519_p1525_institutional_research_certification" / "engine.py"


@contextlib.contextmanager
def working_directory(directory):
    previous = Path.cwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(previous)


def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r245_p1525", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate():
    return {
        "symbol": "SYNTHETIC", "timeframe": "H1", "strategy": "sma",
        "fast": 5, "slow": 21, "dataset": "synthetic.csv",
    }


class PersistedCertificationGate(unittest.TestCase):
    def check_case(self, edges, trades, curve):
        engine = load_engine()
        with tempfile.TemporaryDirectory(prefix="et665_r245_") as temp:
            with working_directory(temp):
                with patch.object(engine, "load_json", return_value=edges), patch.object(
                    engine, "reconstruct", return_value=(trades, curve)
                ):
                    manifest = engine.run()
                output = Path("reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION")
                persisted = json.loads((output / "institutional_certification.json").read_text(encoding="utf-8"))
                reconstructed = json.loads((output / "trade_reconstruction.json").read_text(encoding="utf-8"))
                self.assertEqual(persisted, manifest)
                for document in (persisted, manifest):
                    self.assertEqual(document["P15_25_CERTIFICATION"], "RESEARCH_ONLY")
                    self.assertEqual(document["INDEPENDENT_APPROVAL"], "NOT_PROVEN")
                    self.assertEqual(document["APPROVED_EDGES"], 0)
                    self.assertEqual(document["EDGE"], "NOT_PROVEN")
                    self.assertEqual(document["CAUSALITY"], "NOT_PROVEN")
                    self.assertEqual(document["LIVE"], "FORBIDDEN")
                    self.assertEqual(document["REAL_ORDERS"], "FORBIDDEN")
                self.assertEqual(len(reconstructed), len(edges))
                for row in reconstructed:
                    self.assertEqual(row["status"], "RESEARCH_ONLY")
                    self.assertFalse(row["independent_approval"])
                    self.assertEqual(row["live"], "FORBIDDEN")
                    self.assertEqual(row["real_orders"], "FORBIDDEN")
                return persisted

    def test_profitable_high_trade_count_is_not_certification(self):
        trades = [{"return": 0.01} for _ in range(50)]
        curve = [1.01 ** (i + 1) for i in range(50)]
        self.check_case([candidate()], trades, curve)

    def test_no_candidates_is_not_certification(self):
        self.check_case([], [], [])

    def test_below_threshold_is_not_certification(self):
        trades = [{"return": 0.02} for _ in range(19)]
        curve = [1.02 ** (i + 1) for i in range(19)]
        self.check_case([candidate()], trades, curve)

    def test_untrusted_upstream_approval_does_not_certify(self):
        edge = {**candidate(), "approved": True, "status": "PAPER_RESEARCH_CERTIFIED",
                "independent_approval": True, "promoted": True}
        trades = [{"return": 0.01} for _ in range(30)]
        curve = [1.01 ** (i + 1) for i in range(30)]
        self.check_case([edge], trades, curve)


if __name__ == "__main__":
    unittest.main()
