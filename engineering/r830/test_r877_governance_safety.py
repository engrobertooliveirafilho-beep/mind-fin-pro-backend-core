import unittest
from r877_governance_safety import review

P={'step_id':543,'title':'safe','risk_score':0.2,'alignment_score':0.9,'redundancy_score':0.1}
B=['legal','risk','ethics']
class Tests(unittest.TestCase):
    def check(self, **kw): return review(dict(P, **kw),B)
    def test_candidate(self): self.assertEqual(self.check()['status'],'candidate_for_human_review_only')
    def test_no_human_auth(self): self.assertFalse(self.check()['human_review_authorized'])
    def test_no_execution(self): self.assertFalse(self.check()['executed'])
    def test_no_e2e(self): self.assertFalse(self.check()['e2e_certified'])
    def test_high_risk(self): self.assertEqual(self.check(risk_score=0.9)['reason'],'high_risk')
    def test_low_alignment(self): self.assertEqual(self.check(alignment_score=0.2)['reason'],'low_alignment')
    def test_high_redundancy(self): self.assertEqual(self.check(redundancy_score=0.9)['reason'],'high_redundancy')
    def test_abstain(self): self.assertEqual(self.check(risk_score=0.5)['reason'],'board_abstains')
    def test_nan_risk(self): self.assertEqual(self.check(risk_score=float('nan'))['reason'],'invalid_risk_score')
    def test_nan_alignment(self): self.assertEqual(self.check(alignment_score=float('nan'))['reason'],'invalid_alignment_score')
    def test_nan_redundancy(self): self.assertEqual(self.check(redundancy_score=float('nan'))['reason'],'invalid_redundancy_score')
    def test_missing_risk(self): self.assertEqual(review({k:v for k,v in P.items() if k!='risk_score'},B)['reason'],'invalid_proposal')
    def test_extra_field(self): self.assertEqual(self.check(extra=True)['reason'],'invalid_proposal')
    def test_bad_step(self): self.assertEqual(self.check(step_id=True)['reason'],'invalid_identity')
    def test_bad_title(self): self.assertEqual(self.check(title=' ')['reason'],'invalid_identity')
    def test_empty_board(self): self.assertEqual(review(P,[])['reason'],'invalid_board')
    def test_duplicate_board(self): self.assertEqual(review(P,['legal','risk','ethics','ethics'])['reason'],'invalid_board')
    def test_missing_ethics(self): self.assertEqual(review(P,['legal','risk','ops'])['reason'],'incomplete_board')
    def test_no_mutation(self):
        p=dict(P); b=list(B);review(p,b);self.assertEqual(p,P);self.assertEqual(b,B)
    def test_deterministic(self): self.assertEqual(review(P,B),review(P,B))
if __name__=='__main__': unittest.main()
