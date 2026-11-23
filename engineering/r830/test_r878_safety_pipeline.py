import unittest
from unittest.mock import patch
from r878_safety_pipeline import inspect
A={'type':'normal','risk_hint':0.1}
P={'step_id':543,'title':'safe','risk_score':0.2,'alignment_score':0.9,'redundancy_score':0.1}
B=['legal','risk','ethics']
class Tests(unittest.TestCase):
    def run_gate(self,a=A,p=P,b=B,policy=['forbidden_example']):return inspect(a,policy,p,b)
    def test_candidate(self):self.assertEqual(self.run_gate()['status'],'dual_review_candidate_only')
    def test_no_dispatch(self):self.assertFalse(self.run_gate()['dispatch_authorized'])
    def test_human_required(self):self.assertTrue(self.run_gate()['human_approval_required'])
    def test_no_execution(self):self.assertFalse(self.run_gate()['executed'])
    def test_no_e2e(self):self.assertFalse(self.run_gate()['e2e_certified'])
    def test_action_block(self):self.assertEqual(self.run_gate(a={'type':'forbidden_example','risk_hint':0.1})['reason'],'action_compliance_policy')
    def test_high_action_risk(self):self.assertEqual(self.run_gate(a={'type':'normal','risk_hint':0.9})['reason'],'action_high_risk')
    def test_moderate_action_risk(self):self.assertEqual(self.run_gate(a={'type':'normal','risk_hint':0.6})['reason'],'action_moderate_risk')
    def test_governance_block(self):self.assertEqual(self.run_gate(p=dict(P,risk_score=0.9))['reason'],'governance_high_risk')
    def test_no_governance_on_action_failure(self):
        with patch('r878_safety_pipeline.review') as fn:
            self.run_gate(a={'type':'normal','risk_hint':float('nan')});fn.assert_not_called()
    def test_no_mutation(self):
        a=dict(A);p=dict(P);b=list(B);self.run_gate(a=a,p=p,b=b);self.assertEqual(a,A);self.assertEqual(p,P);self.assertEqual(b,B)
    def test_deterministic(self):self.assertEqual(self.run_gate(),self.run_gate())
if __name__=='__main__':unittest.main()
