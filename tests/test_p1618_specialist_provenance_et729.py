"""ET729 specialist provenance regression; original library required."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mind_trader/reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1618_to_p1624_market_intelligence_stack.py"
ORIGINAL = Path(os.environ.get("ELDORA_HISTORICAL_DIR", "/mnt/data/et709_canonical")) / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"

class TestSpecialistProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ORIGINAL.is_file():
            raise AssertionError("canonical specialist library unavailable")
        cls.original = json.loads(ORIGINAL.read_text(encoding="utf-8"))

    def check(self, mutate, expected):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "reports/P1610_SPECIALIST_LIBRARY/specialist_library.json"
            target.parent.mkdir(parents=True)
            data = copy.deepcopy(self.original)
            mutate(data)
            target.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)

    def test_original_requires_ohlc(self):
        self.check(lambda data: None, "original OHLC feature CSV files unavailable")
    def test_duplicate(self):
        self.check(lambda data: data.append(copy.deepcopy(data[0])), "missing or duplicate specialist identity")
    def test_unsafe(self):
        self.check(lambda data: data[0].update(FTMO_REAL="ALLOWED"), "unsafe specialist execution flags")
    def test_nonfinite(self):
        self.check(lambda data: data[0].update(deployment_score=float("nan")), "invalid specialist metric")
    def test_market_identity(self):
        self.check(lambda data: data[0].update(asset=""), "invalid specialist market identity")
    def test_score_bounds(self):
        self.check(lambda data: data[0].update(deployment_score=101), "specialist deployment score out of bounds")

if __name__ == "__main__":
    unittest.main()
