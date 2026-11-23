import unittest
from r868_step_planner import plan
P = {'step_id': 136, 'module': 'risk_engine', 'approved': True, 'paper_only': True}
class Tests(unittest.TestCase):
    def test_plan(self): self.assertEqual(plan(P)['status'], 'planned_only')
    def test_agent(self): self.assertEqual(plan(P)['agent_id'], 'dev.step_planner_agent')
    def test_step(self): self.assertEqual(plan(P)['step_id'], 136)
    def test_implementation(self): self.assertEqual(plan(P)['plan'][0]['path'], 'engineering/steps/step_00136_risk_engine.py')
    def test_test_path(self): self.assertEqual(plan(P)['plan'][1]['path'], 'tests/test_step_00136_risk_engine.py')
    def test_review(self): self.assertEqual(plan(P)['plan'][2]['kind'], 'review')
    def test_no_execution(self): self.assertFalse(plan(P)['executed'])
    def test_no_e2e(self): self.assertFalse(plan(P)['certified_e2e'])
    def test_no_approval(self): self.assertEqual(plan(dict(P, approved=False))['status'], 'blocked')
    def test_no_paper(self): self.assertEqual(plan(dict(P, paper_only=False))['status'], 'blocked')
    def test_bool_step(self): self.assertEqual(plan(dict(P, step_id=True))['status'], 'blocked')
    def test_zero_step(self): self.assertEqual(plan(dict(P, step_id=0))['status'], 'blocked')
    def test_path_traversal(self): self.assertEqual(plan(dict(P, module='../bad'))['status'], 'blocked')
    def test_uppercase(self): self.assertEqual(plan(dict(P, module='Bad'))['status'], 'blocked')
    def test_missing(self): self.assertEqual(plan({})['status'], 'blocked')
    def test_extra(self): self.assertEqual(plan(dict(P, extra=1))['status'], 'blocked')
    def test_none(self): self.assertEqual(plan(None)['status'], 'blocked')
    def test_determinism(self): self.assertEqual(plan(P), plan(P))
if __name__ == '__main__': unittest.main()
