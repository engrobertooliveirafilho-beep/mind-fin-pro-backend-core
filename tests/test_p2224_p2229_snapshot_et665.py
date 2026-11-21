"""ET665 regression: historical strategy snapshots must not alias mutable state."""
import unittest
from unittest.mock import patch
from app.runtime import p2224_2226_institutional_core as core
from app.runtime import p2227_2229_advanced_layer as advanced

class StrategySnapshotTests(unittest.TestCase):
    def test_core_history_not_aliased(self):
        with patch.object(core.random, "uniform", return_value=1):
            result = core.run(3)
        self.assertEqual([row["strategies"][0]["score"] for row in result["log_sample"]], [51,52,53])
    def test_advanced_history_not_aliased(self):
        with patch.object(advanced.random, "uniform", return_value=1), patch.object(advanced.random, "choice", return_value="NONE"):
            result = advanced.run(3)
        self.assertNotEqual(result["sample"][0]["strategies"][0]["score"], result["sample"][2]["strategies"][0]["score"])
    def test_core_snapshot_independent(self):
        engine=core.StrategyEvolutionEngine()
        with patch.object(core.random, "uniform", return_value=1):
            snapshot=engine.evolve()
            engine.evolve()
        self.assertEqual(snapshot[0]["score"],51)
    def test_advanced_snapshot_independent(self):
        engine=advanced.StrategyEcoSystem()
        with patch.object(advanced.random, "uniform", return_value=1):
            snapshot=engine.evolve({"VOLATILITY":20})
            engine.evolve({"VOLATILITY":20})
        self.assertAlmostEqual(snapshot[0]["score"],50+1-20/50)
if __name__=="__main__":
    unittest.main()
