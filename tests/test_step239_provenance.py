import unittest
from app.runtime.step239_provenance import reconcile_step239

class Step239ProvenanceTests(unittest.TestCase):
    def test_planned_but_missing(self):
        e = reconcile_step239()
        self.assertEqual(e.step_id, 239)
        self.assertEqual(e.planned_name, "Cognitive success metrics v3")
        self.assertEqual(e.status, "PLANNED_MISSING_SOURCE")
    def test_never_certify_runtime(self):
        e = reconcile_step239()
        self.assertFalse(e.runtime_verified)
        self.assertFalse(e.finance_engine_certified)
    def test_source_lineage(self):
        e = reconcile_step239()
        self.assertEqual(e.planned_drive_id, "1OFDxRE-Dm850rV52m98ehhZWMweeKqKX")
        self.assertEqual(e.missing_drive_id, "1mOVJ_DvAE9Pg4XmB_U6CwJ34RSKr5-cK")
