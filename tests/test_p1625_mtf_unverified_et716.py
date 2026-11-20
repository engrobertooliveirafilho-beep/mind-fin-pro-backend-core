"""ET716: canonical historical replay must never claim unverified MTF alignment."""
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
INPUTS = [
    "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json",
    "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json",
    "reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json",
    "reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json",
]

class TestMTFUnverified(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / name).is_file() for name in INPUTS):
            raise AssertionError("canonical historical inputs unavailable; certification blocked")

    def test_canonical_mtf_not_certified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = json.loads((root / "reports/P1625_MULTI_TIMEFRAME_CONFIRMATION/p1625_mtf_confirmation.json").read_text(encoding="utf-8"))
            self.assertEqual(len(rows), 106)
            self.assertTrue(all(row["mtf_alignment_score"] is None for row in rows))
            self.assertTrue(all(row["status"] == "MTF_UNVERIFIED_HIGHER_TF_LINK_MISSING" for row in rows))
            self.assertTrue(any(row["timeframe"] in ("H4", "D1") for row in rows))
            master = json.loads((root / "reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json").read_text(encoding="utf-8"))
            self.assertIs(master["E2E_CERTIFIED"], False)

if __name__ == "__main__":
    unittest.main()
