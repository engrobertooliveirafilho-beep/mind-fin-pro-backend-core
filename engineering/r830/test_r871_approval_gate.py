import unittest
from r871_approval_gate import authorize

class Tests(unittest.TestCase):
    def test_unvalidated(self): self.assertEqual(authorize(1,[{'step_number':1,'status':'nao_validado'}])['reason'],'insufficient_documentary_approval')
    def test_outside(self): self.assertEqual(authorize(543,[])['reason'],'missing_or_ambiguous_step')
    def test_duplicated(self): self.assertEqual(authorize(1,[{'step_number':1},{'step_number':1}])['reason'],'missing_or_ambiguous_step')
    def test_bad_id(self): self.assertEqual(authorize(True,[])['reason'],'invalid_input')
    def test_none(self): self.assertEqual(authorize(1,None)['reason'],'invalid_input')
    def test_bad_record(self): self.assertEqual(authorize(1,[None])['reason'],'invalid_record')
    def test_missing_status(self): self.assertEqual(authorize(1,[{'step_number':1}])['status'],'blocked')
    def test_approval_no_evidence(self): self.assertEqual(authorize(1,[{'step_number':1,'status':'aprovado','status_dev':'validado','status_prod':'validado'}])['reason'],'missing_provenance')
    def test_candidate_not_approved(self):
        r=authorize(1,[{'step_number':1,'status':'aprovado','status_dev':'validado','status_prod':'validado','approval_evidence':'sha256:'+'a'*64}]);self.assertFalse(r['approved'])
    def test_candidate_no_e2e(self):
        r=authorize(1,[{'step_number':1,'status':'aprovado','status_dev':'validado','status_prod':'validado','approval_evidence':'sha256:'+'a'*64}]);self.assertFalse(r['e2e_certified'])
    def test_no_execution(self): self.assertFalse(authorize(1,[])['executed'])
    def test_zero(self): self.assertEqual(authorize(0,[])['status'],'blocked')
if __name__=='__main__': unittest.main()
