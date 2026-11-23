import unittest
from r874_step_titles import reconcile
S = 'STEP 464 — Agente de marketing criativo autônomo\nSTEP 472 — Creative Pipelines Sora-like\n'
class Tests(unittest.TestCase):
    def test_status(self): self.assertEqual(reconcile([464], S)['status'], 'titles_only')
    def test_found(self): self.assertEqual(reconcile([464], S)['defined']['464'], 'Agente de marketing criativo autônomo')
    def test_missing(self): self.assertEqual(reconcile([543], S)['unresolved'], [543])
    def test_multiple(self): self.assertEqual(len(reconcile([464,472], S)['defined']), 2)
    def test_dedup(self): self.assertEqual(len(reconcile([464,464], S)['defined']), 1)
    def test_order(self): self.assertEqual(reconcile([543,520], S)['unresolved'], [520,543])
    def test_conflict(self): self.assertEqual(reconcile([464], S+'STEP 464 — Other\n')['conflicts'], [464])
    def test_conflict_not_defined(self): self.assertEqual(reconcile([464], S+'STEP 464 — Other\n')['defined'], {})
    def test_duplicate_same(self): self.assertEqual(reconcile([464], S+S)['conflicts'], [])
    def test_invalid_steps(self): self.assertEqual(reconcile(None,S)['status'], 'blocked')
    def test_bool(self): self.assertEqual(reconcile([True],S)['status'], 'blocked')
    def test_zero(self): self.assertEqual(reconcile([0],S)['status'], 'blocked')
    def test_invalid_source(self): self.assertEqual(reconcile([464],None)['status'], 'blocked')
    def test_no_cert(self): self.assertEqual(reconcile([464],S)['certified'], 0)
    def test_no_exec(self): self.assertEqual(reconcile([464],S)['executed'], 0)
    def test_no_e2e(self): self.assertFalse(reconcile([464],S)['e2e_certified'])
if __name__ == '__main__': unittest.main()
