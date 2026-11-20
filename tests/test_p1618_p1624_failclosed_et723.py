"""ET723 original P1618-P1624: no false completion without OHLC, no auto-promotion."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1618_to_p1624_market_intelligence_stack.py"
ROOT = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical"))
SPECIALISTS = "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"

class TestP1618FailClosed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / SPECIALISTS).is_file():
            raise AssertionError("original specialist input unavailable; certification blocked")

    def test_no_ohlc_does_not_generate_false_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / SPECIALISTS
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / SPECIALISTS, target)
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("original OHLC feature CSV files unavailable", result.stderr)
            self.assertFalse((root / "reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json").exists())

    def test_no_auto_promotion_in_original_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn('"ELITE_CANDIDATE"', source)
        self.assertIn('"decision":"WATCH_ONLY"', source)

if __name__ == "__main__":
    unittest.main()
