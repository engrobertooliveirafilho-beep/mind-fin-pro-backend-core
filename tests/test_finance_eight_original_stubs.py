"""Read-only provenance regression for eight original Drive-approved stubs."""
import unittest
from pathlib import Path
from app.runtime.finance_step_reconciliation import DRIVE_STUBS, reconcile_finance_steps

ROOT = Path(__file__).resolve().parents[1]
class OriginalFinanceStubEvidence(unittest.TestCase):
    def test_all_eight_original_sources_are_stubs_not_engines(self):
        sources = {}
        for step in sorted(DRIVE_STUBS):
            path = ROOT / 'recovered' / 'finance_steps' / f'step{step}_approved_stub_original.py'
            self.assertTrue(path.is_file(), str(path))
            sources[step] = path.read_text(encoding='utf-8')
        result = reconcile_finance_steps(sources)
        classified = {r['step_id']: r for r in result}
        for step in sorted(DRIVE_STUBS):
            with self.subTest(step=step):
                self.assertEqual(classified[step]['state'], 'APPROVED_STUB')
                self.assertFalse(classified[step]['certified'])
                self.assertEqual(classified[step]['drive_source_id'], DRIVE_STUBS[step])
        self.assertEqual(sum(x['state'] == 'APPROVED_STUB' for x in result), 8)
        self.assertEqual(sum(x['certified'] for x in result), 0)
