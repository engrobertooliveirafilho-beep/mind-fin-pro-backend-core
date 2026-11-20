"""Offline historical regression for P1625-P1636. No broker or network calls.
Set ELDORA_HISTORICAL_DIR to a directory containing the four original JSON
inputs under reports/P1610, P1505, P1620 and P1623.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'mind_trader/reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_intelligence_stack.py'
ROOT = Path(os.environ.get('ELDORA_HISTORICAL_DIR', '/mnt/data'))
INPUTS = (
    'reports/P1610_SPECIALIST_LIBRARY/specialist_library.json',
    'reports/P1505_DATA_INGESTION_ENGINE/p1505n_trade_level_trades.json',
    'reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json',
    'reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json',
)
REPORT = 'reports/P1636_SELF_LEARNING_RESEARCH_LOOP/p1625_to_p1636_master_report.json'

class CanonicalStackRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all((ROOT / p).is_file() for p in INPUTS):
            raise unittest.SkipTest('canonical input files unavailable; never substitute synthetic data')

    def run_stack(self, missing=None, invalid=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in INPUTS:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dest)
            if missing:
                (root / missing).unlink()
            if invalid:
                (root / invalid).write_text('{}', encoding='utf-8')
            result = subprocess.run([sys.executable, str(SOURCE)], cwd=root, capture_output=True, text=True)
            report = root / REPORT
            return result, json.loads(report.read_text()) if report.exists() else None

    def test_canonical_replay(self):
        result, report = self.run_stack()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['CONFLUENCE_PATTERNS'], 106)
        self.assertFalse(report['ORDER_SENT'])

    def test_missing_trades_fail_closed(self):
        result, report = self.run_stack(missing=INPUTS[1])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('required historical input', result.stderr)
        self.assertIsNone(report)

    def test_missing_opportunities_fail_closed(self):
        result, report = self.run_stack(missing=INPUTS[3])
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(report)

    def test_invalid_specialists_fail_closed(self):
        result, report = self.run_stack(invalid=INPUTS[0])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('nonempty list', result.stderr)
        self.assertIsNone(report)

if __name__ == '__main__':
    unittest.main()
