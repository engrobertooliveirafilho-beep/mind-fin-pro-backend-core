"""ET665.R334 — deterministic PAPER research reconstruction integration regression.

Uses actual research engine and a synthetic, isolated price feed.
No network, broker, production, promotion or real orders.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"
PRICES = [100,99,98,97,96,97,98,99,100,101,100,99,98,97,96,95,94,95,96,97,98,99,100,99,98,97,96]

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r334_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class DeterministicResearchPipeline(unittest.TestCase):
    def test_synthetic_feed_to_trades_to_equity(self):
        engine = load_engine()
        rows = [{"close": float(p)} for p in PRICES]
        with patch.object(engine, "load_dataset", return_value=rows):
            trades, curve = engine.reconstruct({"dataset":"synthetic.csv","fast":2,"slow":4})
        self.assertEqual([(t["entry_index"],t["exit_index"]) for t in trades], [(7,12),(19,25)])
        self.assertEqual([(t["entry_price"],t["exit_price"]) for t in trades], [(99.,98.),(97.,97.)])
        self.assertEqual(len(curve), 2)
        self.assertAlmostEqual(curve[0],98/99)
        self.assertAlmostEqual(curve[1],98/99)
        self.assertAlmostEqual(trades[0]["return"],-1/99)
        self.assertEqual(trades[1]["return"],0.0)
        self.assertEqual(engine.risk_of_ruin(trades)["max_loss_streak"],1)
        self.assertAlmostEqual(engine.max_drawdown(curve),1-98/99)

if __name__ == "__main__":
    unittest.main()
