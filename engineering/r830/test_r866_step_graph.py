import unittest
from r866_step_graph import reconcile
A = {'id': 'meta.global_agent_mapper', 'step_ids': [136, 190]}
B = {'id': 'dev.step_planner_agent', 'step_ids': [136]}
class Tests(unittest.TestCase):
    def test_map(self): self.assertEqual(reconcile({'agents': [A, B]})['status'], 'mapped_offline')
    def test_agents(self): self.assertEqual(reconcile({'agents': [A, B]})['agents'], 2)
    def test_steps(self): self.assertEqual(reconcile({'agents': [A, B]})['steps'], 2)
    def test_links(self): self.assertEqual(reconcile({'agents': [A, B]})['links'], 3)
    def test_order(self): self.assertEqual(reconcile({'agents': [B, A]})['step_to_agents']['136'], ['dev.step_planner_agent', 'meta.global_agent_mapper'])
    def test_no_execution(self): self.assertEqual(reconcile({'agents': [A]})['executed'], 0)
    def test_no_e2e(self): self.assertFalse(reconcile({'agents': [A]})['certified_e2e'])
    def test_empty(self): self.assertEqual(reconcile({'agents': []})['steps'], 0)
    def test_bad_registry(self): self.assertEqual(reconcile(None)['status'], 'blocked')
    def test_duplicate_agent(self): self.assertEqual(reconcile({'agents': [A, A]})['status'], 'blocked')
    def test_duplicate_step(self): self.assertEqual(reconcile({'agents': [dict(A, step_ids=[136, 136])]})['status'], 'blocked')
    def test_bool_step(self): self.assertEqual(reconcile({'agents': [dict(A, step_ids=[True])]})['status'], 'blocked')
    def test_bad_id(self): self.assertEqual(reconcile({'agents': [dict(A, id='../bad')]})['status'], 'blocked')
    def test_no_steps(self): self.assertEqual(reconcile({'agents': [{'id': 'meta.empty'}]})['links'], 0)
    def test_nonlist(self): self.assertEqual(reconcile({'agents': [dict(A, step_ids='136')]})['status'], 'blocked')
    def test_limit(self): self.assertEqual(reconcile({'agents': [A] * 1001})['status'], 'blocked')
if __name__ == '__main__': unittest.main()
