import unittest
from app.runtime.p2614_real_fill_replay.montecarlo import monte_carlo_from_trades as mc

class MonteCarloCanonical(unittest.TestCase):
    def test_bootstrap_changes_trade_mix(self):
        result=mc([{'r':-1.0},{'r':2.0}],risk_pct=.1,runs=100)
        self.assertEqual(result['method'],'bootstrap_with_replacement')
        self.assertLess(result['p05_final'],result['p95_final'])
    def test_deterministic(self):
        x=[{'r':-1.0},{'r':2.0},{'r':0.5}]
        self.assertEqual(mc(x,runs=20),mc(x,runs=20))
    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_TRADE_R'):
            mc([{'r':float('nan')}])
    def test_runs_zero_rejected(self):
        with self.assertRaisesRegex(ValueError,'INVALID_RUN_COUNT'):
            mc([{'r':1.0}],runs=0)
    def test_empty(self):
        self.assertEqual(mc([])['runs'],0)
