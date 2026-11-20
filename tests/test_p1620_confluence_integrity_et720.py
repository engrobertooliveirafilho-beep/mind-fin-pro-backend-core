"""ET720: fail-closed validation of historical P1620 confluence snapshots."""
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
CONF = "reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json"
INPUTS = (
    "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json",
    "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json",
    CONF,
    "reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json",
)

class TestET720(unittest.TestCase):
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
                path = root / CONF
                rows = json.loads(path.read_text(encoding="utf-8"))
                mutate(rows)
                path.write_text(json.dumps(rows), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / "reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json"
            return cp, report.exists()

    def test_canonical(self):
        cp, report = self.execute()
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(report)

    def test_duplicate_market(self):
        cp, report = self.execute(lambda rows: rows[1].update(asset=rows[0]["asset"], timeframe=rows[0]["timeframe"]))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_nan_confluence(self):
        cp, report = self.execute(lambda rows: rows[0].update(confluence_score=float("nan")))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_negative_structure(self):
        cp, report = self.execute(lambda rows: rows[0].update(structure_score=-1))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

    def test_missing_ftmo_gate(self):
        cp, report = self.execute(lambda rows: rows[0].pop("FTMO_REAL"))
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
