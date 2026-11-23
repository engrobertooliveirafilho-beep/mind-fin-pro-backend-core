import unittest
from unittest.mock import patch
from r872_approval_integrated_squad import compose_verified

P = {'step_id': 136, 'module': 'risk_engine', 'approved': True, 'paper_only': True}

class Tests(unittest.TestCase):
    def test_historical_unvalidated(self):
        self.assertEqual(compose_verified(P, [{'step_number':136,'status':'nao_validado'}])['reason'], 'insufficient_documentary_approval')
    def test_missing_step(self):
        self.assertEqual(compose_verified(P, [])['reason'], 'missing_or_ambiguous_step')
    def test_duplicated(self):
        self.assertEqual(compose_verified(P, [{'step_number':136}]*2)['reason'], 'missing_or_ambiguous_step')
    def test_apparent_approval_no_provenance(self):
        self.assertEqual(compose_verified(P, [{'step_number':136,'status':'aprovado','status_dev':'validado','status_prod':'validado'}])['reason'], 'missing_provenance')
    def test_unverified_hash(self):
        self.assertEqual(compose_verified(P, [{'step_number':136,'status':'aprovado','status_dev':'validado','status_prod':'validado','approval_evidence':'sha256:'+'a'*64}])['reason'], 'external_evidence_verification_required')
    def test_no_squad_dispatch_on_block(self):
        with patch('r872_approval_integrated_squad.compose') as c:
            compose_verified(P, [])
            c.assert_not_called()
    def test_no_squad_dispatch_with_fake_hash(self):
        with patch('r872_approval_integrated_squad.compose') as c:
            compose_verified(P, [{'step_number':136,'status':'aprovado','status_dev':'validado','status_prod':'validado','approval_evidence':'sha256:'+'a'*64}])
            c.assert_not_called()
    def test_invalid_payload(self): self.assertEqual(compose_verified(None, [])['reason'], 'invalid_payload')
    def test_bool_step(self): self.assertEqual(compose_verified(dict(P,step_id=True), [])['reason'], 'invalid_payload')
    def test_never_execute(self): self.assertFalse(compose_verified(P, [])['executed'])
    def test_never_e2e(self): self.assertFalse(compose_verified(P, [])['e2e_certified'])
    def test_no_mutation(self):
        p = dict(P); records=[]; compose_verified(p,records); self.assertEqual(p,P); self.assertEqual(records,[])

if __name__ == '__main__': unittest.main()
