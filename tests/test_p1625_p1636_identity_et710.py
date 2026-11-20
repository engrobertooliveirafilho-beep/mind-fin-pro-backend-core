"""ET710: offline P1625-P1636 identity regression; historical files required."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_intelligence_stack.py"
ROOT = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical"))
INPUTS = [
    "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json",
    "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json",
    "reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json",
    "reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json",
]

class TestHistoricalIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / f).is_file() for f in INPUTS):
            raise unittest.SkipTest("original historical inputs unavailable; no synthetic substitution")

    def execute(self, change=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dest)
            if change:
                name, mutate = change
                dest = root / name
                obj = json.loads(dest.read_text(encoding="utf-8"))
                mutate(obj)
                dest.write_text(json.dumps(obj), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / "reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json"
            return result, report.exists()

    def test_canonical(self):
        result, report = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report)

    def test_no_score_based_promotion(self):
        for score in (85, 99.9):
            with self.subTest(score=score):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    for name in INPUTS:
                        dest = root / name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(ROOT / name, dest)
                    dest = root / INPUTS[1]
                    rows = json.loads(dest.read_text(encoding="utf-8"))
                    rows[0]["opportunity_score"] = score
                    dest.write_text(json.dumps(rows), encoding="utf-8")
                    result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    brain = json.loads((root / "reports/P1635_MASTER_PORTFOLIO_BRAIN/p1635_master_portfolio_brain.json").read_text(encoding="utf-8"))
                    self.assertEqual(brain["DECISION"], "WATCH_ONLY")
                    self.assertIs(brain["ORDER_SENT"], False)
                    self.assertEqual(brain["REAL_ORDERS"], "FORBIDDEN")

    def test_orphan_opportunity(self):
        result, report = self.execute((INPUTS[1], lambda rows: rows[0].update(specialist_id="UNKNOWN")))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report)

    def test_duplicate_opportunity(self):
        result, report = self.execute((INPUTS[1], lambda rows: rows[1].update(specialist_id=rows[0]["specialist_id"])))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report)

    def test_duplicate_specialist(self):
        result, report = self.execute((INPUTS[0], lambda rows: rows[1].update(specialist_id=rows[0]["specialist_id"])))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report)

    def test_asset_mismatch(self):
        result, report = self.execute((INPUTS[1], lambda rows: rows[0].update(asset="FAKE")))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report)

    def test_timeframe_mismatch(self):
        result, report = self.execute((INPUTS[1], lambda rows: rows[0].update(timeframe="H99")))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(report)

if __name__ == "__main__":
    unittest.main()
