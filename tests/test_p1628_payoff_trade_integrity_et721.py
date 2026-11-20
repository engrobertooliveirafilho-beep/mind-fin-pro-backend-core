"""ET721 offline canonical P1628 payoff-trade safety regressions."""
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
TRADES = "reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json"
INPUTS = [
    "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json",
    "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json",
    "reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json",
    TRADES,
]

class TestET721(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / name).is_file() for name in INPUTS):
            raise AssertionError("canonical historical inputs unavailable; certification blocked")

    def execute(self, mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            if mutate:
                target = root / TRADES
                rows = json.loads(target.read_text(encoding="utf-8"))
                mutate(rows[0])
                target.write_text(json.dumps(rows), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / "reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json"
            return result, report.exists()

    def test_canonical(self):
        result, exists = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(exists)

    def test_nan_pnl(self):
        result, exists = self.execute(lambda row: row.update(pnl_pct=float("nan")))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(exists)

    def test_inf_mae(self):
        result, exists = self.execute(lambda row: row.update(mae_pct=float("inf")))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(exists)

    def test_missing_ftmo_block(self):
        result, exists = self.execute(lambda row: row.pop("FTMO_REAL"))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(exists)

    def test_missing_edge_id(self):
        result, exists = self.execute(lambda row: row.update(edge_id=""))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(exists)

if __name__ == "__main__":
    unittest.main()
