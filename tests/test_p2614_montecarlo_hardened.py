import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "src" / "revisions" / "p2614_montecarlo_hardened.py"
spec = importlib.util.spec_from_file_location("p2614_montecarlo_hardened", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
mc = module.monte_carlo_from_trades

class TestP2614MonteCarlo(unittest.TestCase):
    def test_empty(self): self.assertEqual(mc([])["runs"], 0)
    def test_one_run(self): self.assertEqual(mc([{"r": 1}], runs=1)["runs"], 1)
    def test_determinism(self):
        x = [{"r": r} for r in [-1, 2, 0.5, -0.4]]
        self.assertEqual(mc(x, runs=20), mc(x, runs=20))
    def test_bad_runs(self):
        for n in [0, -1, True, 1.5]:
            with self.subTest(n=n), self.assertRaises(ValueError): mc([{"r": 1}], runs=n)
    def test_bad_capital(self):
        for n in [0, -1, float("nan"), float("inf")]:
            with self.subTest(n=n), self.assertRaises(ValueError): mc([], initial_capital=n)
    def test_bad_risk(self):
        for n in [0, -1, 1.1, float("nan")]:
            with self.subTest(n=n), self.assertRaises(ValueError): mc([], risk_pct=n)
    def test_nonfinite_r(self):
        with self.assertRaises(ValueError): mc([{"r": float("nan")}])
    def test_loss(self):
        self.assertGreater(mc([{"r": -1}], runs=5)["p95_dd"], 0)
    def test_paper_only(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertNotIn("MetaTrader5", source)
        self.assertNotIn("send_order", source)
