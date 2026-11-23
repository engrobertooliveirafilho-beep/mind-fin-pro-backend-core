import unittest
from app.runtime.p2614_real_fill_replay.montecarlo import monte_carlo_from_trades as mc

class MonteCarloBootstrap(unittest.TestCase):
    def test_bootstrap_terminal_distribution(self):
        r=mc([{'r':-1},{'r':2}],runs=100,risk_pct=.1)
        self.assertLess(r['p05_final'],r['p95_final'])
    def test_determinism(self):
        a=[{'r':-1},{'r':2},{'r':.5}]
        self.assertEqual(mc(a,runs=20),mc(a,runs=20))
    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_MONTE_CARLO_TRADE'):
            mc([{'r':float('nan')}])
    def test_bad_runs_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_MONTE_CARLO_INPUT'):
            mc([{'r':1}],runs=0)
    def test_empty(self):
        self.assertEqual(mc([])['runs'],0)
