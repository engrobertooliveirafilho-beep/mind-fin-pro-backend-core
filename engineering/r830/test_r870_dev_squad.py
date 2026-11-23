import unittest
from unittest.mock import patch
from r870_dev_squad import compose

P = {'step_id': 136, 'module': 'risk_engine', 'approved': True, 'paper_only': True}

class Tests(unittest.TestCase):
    def test_success(self): self.assertEqual(compose(P)['status'], 'composed_offline')
    def test_four_agents(self): self.assertEqual(len(compose(P)['agents']), 4)
    def test_three_plan_items(self): self.assertEqual(len(compose(P)['planner']), 3)
    def test_step(self): self.assertEqual(compose(P)['step_id'], 136)
    def test_no_execution(self): self.assertFalse(compose(P)['executed'])
    def test_no_e2e(self): self.assertFalse(compose(P)['e2e_certified'])
    def test_no_approval(self): self.assertEqual(compose(dict(P, approved=False))['status'], 'blocked')
    def test_no_paper(self): self.assertEqual(compose(dict(P, paper_only=False))['status'], 'blocked')
    def test_path_traversal(self): self.assertEqual(compose(dict(P, module='../x'))['status'], 'blocked')
    def test_bool_step(self): self.assertEqual(compose(dict(P, step_id=True))['status'], 'blocked')
    def test_missing(self): self.assertEqual(compose({})['status'], 'blocked')
    def test_none(self): self.assertEqual(compose(None)['status'], 'blocked')
    def test_extra(self): self.assertEqual(compose(dict(P, extra=1))['status'], 'blocked')
    def test_determinism(self): self.assertEqual(compose(P), compose(P))
    def test_no_mutation(self):
        p = dict(P); compose(p); self.assertEqual(p, P)
    def test_agent_failure(self):
        with patch('r870_dev_squad.run_dry', return_value={'status':'blocked'}):
            self.assertEqual(compose(P)['reason'], 'agent_blocked')
    def test_path_mismatch(self):
        from r870_dev_squad import run_dry
        def altered(agent, payload):
            r = run_dry(agent, payload)
            if agent.endswith('code_blueprint_agent'):
                r['result']['module'] = 'different.py'
            return r
        with patch('r870_dev_squad.run_dry', side_effect=altered):
            self.assertEqual(compose(P)['reason'], 'path_mismatch')
    def test_no_dispatch(self): self.assertFalse(compose(P)['agents'][-1]['result']['dispatched'])

if __name__ == '__main__': unittest.main()
