import unittest
from r876_action_safety import assess

class SafetyTests(unittest.TestCase):
    def run_gate(self, name='normal', risk=0.1, policy=('forbidden_example',), **kwargs):
        return assess({'type': name, 'risk_hint': risk}, policy, **kwargs)
    def test_low(self): self.assertEqual(self.run_gate()['status'], 'eligible_for_external_review_only')
    def test_mid(self): self.assertEqual(self.run_gate(risk=0.6)['status'], 'needs_confirmation')
    def test_high(self): self.assertEqual(self.run_gate(risk=0.9)['reason'], 'high_risk')
    def test_policy(self): self.assertEqual(self.run_gate(name='forbidden_example')['reason'], 'compliance_policy')
    def test_policy_priority(self): self.assertEqual(self.run_gate(name='forbidden_example',risk=0.9)['reason'], 'compliance_policy')
    def test_missing_policy(self): self.assertEqual(self.run_gate(policy=[])['reason'], 'missing_policy')
    def test_invalid_policy(self): self.assertEqual(self.run_gate(policy=[None])['reason'], 'invalid_policy')
    def test_none_action(self): self.assertEqual(assess(None, ['x'])['reason'], 'invalid_action')
    def test_extra_key(self): self.assertEqual(assess({'type':'x','risk_hint':0.1,'extra':1},['y'])['reason'], 'invalid_action')
    def test_missing_key(self): self.assertEqual(assess({'type':'x'},['y'])['reason'], 'invalid_action')
    def test_bad_name(self): self.assertEqual(self.run_gate(name='')['reason'], 'invalid_action_name')
    def test_bool_risk(self): self.assertEqual(self.run_gate(risk=True)['reason'], 'invalid_risk')
    def test_nan(self): self.assertEqual(self.run_gate(risk=float('nan'))['reason'], 'invalid_risk')
    def test_inf(self): self.assertEqual(self.run_gate(risk=float('inf'))['reason'], 'invalid_risk')
    def test_negative(self): self.assertEqual(self.run_gate(risk=-0.1)['reason'], 'invalid_risk')
    def test_over_one(self): self.assertEqual(self.run_gate(risk=1.1)['reason'], 'invalid_risk')
    def test_invalid_threshold_order(self): self.assertEqual(self.run_gate(confirm_threshold=0.9,block_threshold=0.8)['reason'], 'invalid_thresholds')
    def test_nan_threshold(self): self.assertEqual(self.run_gate(block_threshold=float('nan'))['reason'], 'invalid_thresholds')
    def test_boundary_confirm(self): self.assertEqual(self.run_gate(risk=0.5)['status'], 'needs_confirmation')
    def test_boundary_block(self): self.assertEqual(self.run_gate(risk=0.8)['status'], 'blocked')
    def test_no_execution(self): self.assertFalse(self.run_gate()['executed'])
    def test_no_cert(self): self.assertFalse(self.run_gate()['certified_e2e'])
    def test_deterministic(self): self.assertEqual(self.run_gate(), self.run_gate())
    def test_no_mutation(self):
        a={'type':'x','risk_hint':0.1};p=['y'];assess(a,p);self.assertEqual(a,{'type':'x','risk_hint':0.1});self.assertEqual(p,['y'])

if __name__=='__main__': unittest.main()
