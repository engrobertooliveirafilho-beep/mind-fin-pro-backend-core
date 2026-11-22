import unittest
from app.runtime.finance_step_reconciliation import FINANCE_STEPS, DRIVE_STUBS, reconcile_finance_steps

class FinanceStepReconciliationTests(unittest.TestCase):
    def test_thirteen(self):
        self.assertEqual(len(reconcile_finance_steps({})),13)
    def test_no_automatic_certification(self):
        self.assertFalse(any(x["certified"] for x in reconcile_finance_steps({})))
    def test_original_stub(self):
        s='"""A lógica REAL deste STEP deve ser implementada"""\nSTEP_ID = 139\nSTEP_STATUS = "approved_stub"'
        self.assertEqual(reconcile_finance_steps({139:s})[2]["state"],"APPROVED_STUB")
    def test_claim_not_certification(self):
        self.assertFalse(reconcile_finance_steps({139:'STEP_ID = 139\nSTEP_STATUS = "implemented"'})[2]["certified"])
    def test_wrong_id(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 154'})
    def test_unknown_id(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({999:'STEP_ID = 999'})
    def test_bool_id(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({True:'STEP_ID = 1'})
    def test_nonstring(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:None})
    def test_mapping(self):
        with self.assertRaises(TypeError):
            reconcile_finance_steps([])
    def test_eight_originals(self):
        self.assertEqual(len(DRIVE_STUBS),8)
    def test_prefix_collision_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 1399'})
    def test_comment_spoof_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'# STEP_ID = 139\nSTEP_ID = 154'})
    def test_duplicate_metadata_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 139\nSTEP_ID = 154'})
    def test_marker_only_in_comment_not_stub(self):
        s='STEP_ID = 139\nSTEP_STATUS = "approved_stub"\n# A lógica REAL deste STEP deve ser implementada'
        self.assertEqual(reconcile_finance_steps({139:s})[2]['state'],'REQUIRES_CODE_REVIEW')
    def test_nonliteral_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = int("139")'})

    def test_late_string_spoof_not_stub(self):
        s='STEP_ID = 139\nSTEP_STATUS = "approved_stub"\n"A lógica REAL deste STEP deve ser implementada"'
        self.assertEqual(reconcile_finance_steps({139:s})[2]['state'],'REQUIRES_CODE_REVIEW')
    def test_annotated_metadata_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 139\nSTEP_ID: int = 154'})
    def test_nested_metadata_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 139\ndef foo():\n    STEP_ID = 154'})
    def test_augmented_metadata_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_finance_steps({139:'STEP_ID = 139\nSTEP_ID += 1'})
