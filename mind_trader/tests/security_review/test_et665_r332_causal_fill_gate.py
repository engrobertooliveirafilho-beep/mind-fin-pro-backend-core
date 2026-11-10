"""ET665.R333 — causal SMA regression, no broker access.

SMA at execution index i must use prices strictly before i.
Changing the execution-bar close must not change either signal.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / "app/p1519_p1525_institutional_research_certification/engine.py"

def load_engine():
    spec = importlib.util.spec_from_file_location("et665_r333_engine", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CausalFillGate(unittest.TestCase):
    def test_sma_excludes_current_and_future_bar(self):
        module = load_engine()
        closes = [10., 20., 30., 40., 50., 60., 70.]
        for window in (2, 4):
            for i in range(window, len(closes)):
                original = module.sma(closes, window, i)
                mutated = closes.copy()
                for j in range(i, len(mutated)):
                    mutated[j] = 1e6 + j
                self.assertEqual(original, module.sma(mutated, window, i))

    def test_reconstruct_uses_only_pre_fill_prices_for_signal(self):
        module = load_engine()
        observed = []
        original = module.sma
        def tracked(vals, window, i):
            observed.append((window, i, tuple(vals[i-window:i])))
            return original(vals, window, i)
        edge = {"dataset": "synthetic.csv", "fast": 2, "slow": 4}
        rows = [{"close": float(v)} for v in [100, 99, 98, 97, 98, 99, 100, 99, 98, 97, 96, 95]]
        with patch.object(module, "load_dataset", return_value=rows), patch.object(module, "sma", side_effect=tracked):
            module.reconstruct(edge)
        self.assertTrue(observed)
        for window, index, history in observed:
            self.assertEqual(history, tuple(r["close"] for r in rows[index-window:index]))
            self.assertEqual(len(history), window)

if __name__ == "__main__":
    unittest.main()
