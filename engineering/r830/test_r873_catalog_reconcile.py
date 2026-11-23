import unittest
from r873_catalog_reconcile import reconcile

A=[{'id':'dev.a','step_ids':[1,2,464]}]
C=[{'step_number':1,'status':'nao_validado'}, {'step_number':2,'status':'nao_validado'}]
V=[1,2,464]
class Tests(unittest.TestCase):
    def test_status(self): self.assertEqual(reconcile(A,C,V)['status'],'reconciled_not_certified')
    def test_declared(self): self.assertEqual(reconcile(A,C,V)['declared_steps'],3)
    def test_catalog(self): self.assertEqual(reconcile(A,C,V)['catalog_matches'],2)
    def test_outside(self): self.assertEqual(reconcile(A,C,V)['outside_catalog'],[464])
    def test_listed(self): self.assertEqual(reconcile(A,C,V)['outside_listed_only'],[464])
    def test_unlocated(self): self.assertEqual(reconcile(A,C,[])['outside_unlocated'],[464])
    def test_unvalidated(self): self.assertEqual(reconcile(A,C,V)['unvalidated_catalog'],[1,2])
    def test_not_certified(self): self.assertEqual(reconcile(A,C,V)['certified'],0)
    def test_no_e2e(self): self.assertFalse(reconcile(A,C,V)['e2e_certified'])
    def test_no_execution(self): self.assertEqual(reconcile(A,C,V)['executed'],0)
    def test_bad_agents(self): self.assertEqual(reconcile(None,C,V)['status'],'blocked')
    def test_bad_catalog(self): self.assertEqual(reconcile(A,None,V)['status'],'blocked')
    def test_bad_valid(self): self.assertEqual(reconcile(A,C,None)['status'],'blocked')
    def test_duplicate_catalog(self): self.assertEqual(reconcile(A,C+C,V)['reason'],'invalid_catalog')
    def test_bool_step(self): self.assertEqual(reconcile([{'step_ids':[True]}],C,V)['status'],'blocked')
    def test_bad_valid_entry(self): self.assertEqual(reconcile(A,C,[True])['status'],'blocked')
    def test_empty(self): self.assertEqual(reconcile([],[],[])['declared_steps'],0)
    def test_duplicate_agent_steps(self): self.assertEqual(reconcile([{'step_ids':[1,1]}],C,V)['declared_steps'],1)
if __name__=='__main__': unittest.main()
