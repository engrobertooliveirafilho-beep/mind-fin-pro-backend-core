"""ET665.R332 — adversarial causal execution gate; PAPER only.

A signal formed at bar i close cannot fill at that same close.
This test is expected to FAIL against the historical implementation.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r332_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class CausalFillGate(unittest.TestCase):
    def test_signal_bar_cannot_be_execution_bar(self):
        mod = load_engine()
        prices = [100., 100., 100., 100., 100., 100., 110., 120., 120., 120.]
        # For i=5, prior fast<=slow, current fast>slow: BUY signal.
        # For i=7, prior fast>=slow, current fast<slow: SELL signal.
        fast = {4: 0., 5: 2., 6: 2., 7: 0.}
        slow = {4: 1., 5: 1., 6: 1., 7: 1.}
        def indicator(_closes, window, i):
            return (fast if window == 2 else slow).get(i, 1.)
        edge = {"dataset": "synthetic.csv", "fast": 2, "slow": 4}
        with patch.object(mod, "load_dataset", return_value=[{"close": p} for p in prices]), patch.object(mod, "sma", side_effect=indicator):
            trades, _ = mod.reconstruct(edge)
        self.assertTrue(trades, "fixture must generate at least one trade")
        for trade in trades:
            self.assertGreaterEqual(trade["entry_index"], 6, "entry filled on signal close: lookahead")
            self.assertGreaterEqual(trade["exit_index"], 8, "exit filled on signal close: lookahead")

if __name__ == "__main__":
    unittest.main()
