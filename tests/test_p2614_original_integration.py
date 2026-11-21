"""Integration against original P2614 execution.py recovered from Drive."""
import importlib.util
import pathlib
import unittest
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1] / "src" / "revisions"
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

simulate_fill = load("p2614_execution_original").simulate_fill
replay = load("p2614_replay_chronological").replay_chronological
C = [{"time": datetime(2026, 1, 1) + timedelta(hours=i), "open": 100., "close": 101.} for i in range(100)]
F = {i: {"session":"NY", "regime":"LOW_VOL", "trend":"TREND_UP",
         "wick_ratio":.5, "body_ratio":.6, "atr":1., "atr_med":1.} for i in range(100)}
E = [{"edge_id":str(i), "direction":"BUY_PAPER", "family":"TREND", "timeframe":"M5"} for i in range(10)]

class Integration(unittest.TestCase):
    def test_original_execution(self):
        summary, curve, trades = replay(E[:1], C, F, simulate_fill)
        self.assertGreater(len(trades), 0)
        self.assertEqual(curve[-1]["capital"], summary["final_capital_usd"])
    def test_risk_cap(self):
        _, _, trades = replay(E, C, F, simulate_fill)
        first = [t for t in trades if t["signal_i"] == 60]
        self.assertEqual(len(first), 5)
        self.assertLessEqual(sum(t["risk_usd"] for t in first), 5.000001)
    def test_no_real_direction(self):
        with self.assertRaises(ValueError):
            replay([dict(E[0], direction="BUY_REAL")], C, F, simulate_fill)
    def test_determinism(self):
        self.assertEqual(replay(E, C, F, simulate_fill)[0],
                         replay(E, C, F, simulate_fill)[0])
