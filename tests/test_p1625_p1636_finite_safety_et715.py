"""ET715 canonical replay: finite metrics and mandatory forbidden safety flags."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical"))
SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_intelligence_stack.py"
OP = "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json"
INPUTS = (
    "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json",
    OP,
    "reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json",
    "reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json",
)

class TestET715(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / p).is_file() for p in INPUTS):
            raise AssertionError("canonical historical inputs unavailable; certification blocked")

    def execute(self, mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dst)
            if mutate:
                p = root / OP
                rows = json.loads(p.read_text(encoding="utf-8"))
                mutate(rows[0])
                p.write_text(json.dumps(rows), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / "reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json"
            return cp, report.exists()

    def test_canonical(self):
        cp, report = self.execute()
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(report)

    def test_nan(self):
        cp, report = self.execute(lambda row: row.update(opportunity_score=float("nan")))
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("invalid historical opportunity metric", cp.stderr)
        self.assertFalse(report)

    def test_infinity(self):
        cp, report = self.execute(lambda row: row.update(deployment_score=float("inf")))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_boolean_score(self):
        cp, report = self.execute(lambda row: row.update(confluence_score=True))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_negative_score_rejected(self):
        cp, report = self.execute(lambda row: row.update(opportunity_score=-0.01))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_score_above_hundred_rejected(self):
        cp, report = self.execute(lambda row: row.update(opportunity_score=100.01))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_score_hundred_accepted(self):
        cp, report = self.execute(lambda row: row.update(opportunity_score=100))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(report)

    def test_missing_ftmo_block(self):
        cp, report = self.execute(lambda row: row.pop("FTMO_REAL"))
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("unsafe historical opportunity safety flag", cp.stderr)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
