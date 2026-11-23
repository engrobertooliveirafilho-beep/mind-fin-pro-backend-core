import unittest
from r869_dev_agents import AGENTS, run_dry

P = {'step_id': 136, 'module': 'risk_engine', 'approved': True, 'paper_only': True}

class Tests(unittest.TestCase):
    def test_each_agent_plans(self):
        for a in AGENTS:
            with self.subTest(a=a): self.assertEqual(run_dry(a, P)['status'], 'planned_only')
    def test_each_agent_no_execution(self):
        for a in AGENTS:
            with self.subTest(a=a): self.assertFalse(run_dry(a, P)['executed'])
    def test_each_agent_no_e2e(self):
        for a in AGENTS:
            with self.subTest(a=a): self.assertFalse(run_dry(a, P)['e2e_certified'])
    def test_blueprint(self): self.assertEqual(run_dry(AGENTS[0], P)['result']['module'], 'engineering/steps/step_00136_risk_engine.py')
    def test_blueprint_no_write(self): self.assertFalse(run_dry(AGENTS[0], P)['result']['write_authorized'])
    def test_guardian(self): self.assertFalse(run_dry(AGENTS[1], P)['result']['suite_executed'])
    def test_guardian_checks(self): self.assertIn('regression', run_dry(AGENTS[1], P)['result']['checks'])
    def test_refactor(self): self.assertFalse(run_dry(AGENTS[2], P)['result']['patch_applied'])
    def test_refactor_contract(self): self.assertIn('preserve_contract', run_dry(AGENTS[2], P)['result']['changes'])
    def test_squad(self): self.assertEqual(len(run_dry(AGENTS[3], P)['result']['backlog']), 3)
    def test_squad_no_dispatch(self): self.assertFalse(run_dry(AGENTS[3], P)['result']['dispatched'])
    def test_unknown(self): self.assertEqual(run_dry('dev.unknown', P)['status'], 'blocked')
    def test_none(self): self.assertEqual(run_dry(AGENTS[0], None)['status'], 'blocked')
    def test_extra(self): self.assertEqual(run_dry(AGENTS[0], dict(P, extra=True))['status'], 'blocked')
    def test_approval(self): self.assertEqual(run_dry(AGENTS[0], dict(P, approved=False))['status'], 'blocked')
    def test_paper(self): self.assertEqual(run_dry(AGENTS[0], dict(P, paper_only=False))['status'], 'blocked')
    def test_bool_step(self): self.assertEqual(run_dry(AGENTS[0], dict(P, step_id=True))['status'], 'blocked')
    def test_path(self): self.assertEqual(run_dry(AGENTS[0], dict(P, module='../evil'))['status'], 'blocked')
    def test_deterministic(self): self.assertEqual(run_dry(AGENTS[0], P), run_dry(AGENTS[0], P))
    def test_no_mutation(self):
        p = dict(P); run_dry(AGENTS[0], p); self.assertEqual(p, P)

if __name__ == '__main__': unittest.main()
