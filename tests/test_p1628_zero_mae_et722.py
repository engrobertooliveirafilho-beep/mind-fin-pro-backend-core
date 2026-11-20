"""ET722: real historical zero-MAE observations must not fabricate R."""
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

class TestET722(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / name).is_file() for name in INPUTS):
            raise AssertionError("canonical historical inputs unavailable; certification blocked")

    def execute(self, zero_edge=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dst)
            if zero_edge:
                path = root / INPUTS[3]
                rows = json.loads(path.read_text(encoding="utf-8"))
                edge = rows[0]["edge_id"]
                for row in rows:
                    if row["edge_id"] == edge:
                        row["mae_pct"] = 0
                path.write_text(json.dumps(rows), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            return json.loads((root / "reports/P1628_PAYOFF_FORENSICS_ENGINE/p1628_payoff_forensics.json").read_text(encoding="utf-8"))

    def test_canonical_zero_mae_accounting(self):
        rows = self.execute()
        self.assertEqual(sum(row["trades"] for row in rows), 8482)
        self.assertEqual(sum(row["undefined_R_zero_mae"] for row in rows), 23)
        self.assertEqual(sum(row["valid_R_samples"] for row in rows), 8459)

    def test_entire_edge_zero_mae(self):
        rows = self.execute(zero_edge=True)
        self.assertTrue(any(row["valid_R_samples"] == 0 and row["avg_R"] is None for row in rows))

    def test_valid_payoff_remains(self):
        rows = self.execute()
        self.assertTrue(any(row["valid_R_samples"] > 0 and row["avg_R"] is not None for row in rows))

if __name__ == "__main__":
    unittest.main()
