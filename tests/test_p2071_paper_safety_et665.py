"""Offline PAPER-only regression for the original P2071 runtime; no broker access."""
import importlib.util
import math
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "app/runtime/p2071_2080_realtime_paper_runtime.py"
spec = importlib.util.spec_from_file_location("p2071_runtime", path)
runtime = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)

class TestP2071PaperSafety(unittest.TestCase):
    def setUp(self):
        self.engine = runtime.PaperPortfolioExecutor()
    def signal(self, side="BUY", confidence=0.9):
        return runtime.PaperSignal(ts=1, symbol="XAUUSD", specialist_id="test",
                                   side=side, confidence=confidence, reason="offline")
    def frame(self, mid):
        return runtime.FeatureFrame(ts=2, symbol="XAUUSD", mid=mid, spread=0.1,
                                    return_1=0, volatility_20=0, body_to_range=0,
                                    rsi_14=50, stoch_14=50, close_position=0.5)
    def test_invalid_side_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            self.engine.on_signal(self.signal("HOLD"), 100.0)
        self.assertEqual(len(self.engine.positions), 0)
        self.assertEqual(self.engine.seq, 0)
    def test_invalid_entry_prices(self):
        for price in (float("nan"), float("inf"), -1.0, 0.0, True):
            with self.subTest(price=price):
                with self.assertRaises(ValueError):
                    self.engine.on_signal(self.signal(), price)
        self.assertEqual(self.engine.seq, 0)
    def test_invalid_confidence(self):
        for confidence in (float("nan"), float("inf"), "0.9", True):
            with self.subTest(confidence=confidence):
                with self.assertRaises(ValueError):
                    self.engine.on_signal(self.signal(confidence=confidence), 100)
    def test_position_quantity_scales_unrealized_pnl(self):
        pos = self.engine.on_signal(self.signal(), 100)
        pos.qty = 2.5
        self.assertEqual(self.engine.unrealized_pnl(102), 5.0)
        self.assertEqual(self.engine.current_equity(102), 100005.0)

    def test_position_quantity_scales_realized_pnl(self):
        pos = self.engine.on_signal(self.signal(), 100)
        pos.qty = 2.5
        self.engine.mark_to_market(self.frame(106))
        self.assertEqual(self.engine.equity, 100015.0)
        self.assertEqual(self.engine.closed[0]["pnl"], 15.0)

    def test_invalid_quantity_blocks_without_partial_close(self):
        pos = self.engine.on_signal(self.signal(), 100)
        for qty in (0, -1, float("nan"), float("inf"), True, "2"):
            pos.qty = qty
            with self.subTest(qty=qty):
                with self.assertRaises(ValueError):
                    self.engine.mark_to_market(self.frame(106))
            self.assertEqual(self.engine.equity, 100000.0)
            self.assertEqual(len(self.engine.closed), 0)
        pos.qty = 1.0

    def test_low_price_paper_stop_and_target_positive(self):
        for side in ("BUY", "SELL"):
            with self.subTest(side=side):
                engine = runtime.PaperPortfolioExecutor()
                pos = engine.on_signal(self.signal(side), 1.1)
                self.assertGreater(pos.sl, 0)
                self.assertGreater(pos.tp, 0)
                self.assertNotEqual(pos.sl, pos.entry)
                self.assertNotEqual(pos.tp, pos.entry)

    def test_tiny_price_rejected_without_position_mutation(self):
        with self.assertRaises(ValueError):
            self.engine.on_signal(self.signal("SELL"), 0.000001)
        self.assertEqual(self.engine.seq, 0)
        self.assertEqual(len(self.engine.positions), 0)

    def test_valid_buy_tp(self):
        self.engine.on_signal(self.signal("BUY"), 100)
        self.engine.mark_to_market(self.frame(106))
        self.assertEqual(self.engine.equity, 100006.0)
        self.assertEqual(len(self.engine.closed), 1)
    def test_valid_sell_tp(self):
        self.engine.on_signal(self.signal("SELL"), 100)
        self.engine.mark_to_market(self.frame(94))
        self.assertEqual(self.engine.equity, 100006.0)
    def test_invalid_mark_does_not_close_position(self):
        self.engine.on_signal(self.signal(), 100)
        for price in (float("nan"), float("inf"), -1, 0, True):
            with self.subTest(price=price):
                with self.assertRaises(ValueError):
                    self.engine.mark_to_market(self.frame(price))
        self.assertEqual(len(self.engine.positions), 1)
        self.assertEqual(len(self.engine.closed), 0)
    def test_invalid_existing_position_side(self):
        position = self.engine.on_signal(self.signal(), 100)
        position.side = "UNKNOWN"
        with self.assertRaises(ValueError):
            self.engine.mark_to_market(self.frame(106))
        self.assertEqual(len(self.engine.positions), 1)

    def test_invalid_second_position_no_partial_close(self):
        first = self.engine.on_signal(self.signal("BUY"), 100)
        second = self.engine.on_signal(self.signal("SELL"), 100)
        second.side = "UNKNOWN"
        with self.assertRaises(ValueError):
            self.engine.mark_to_market(self.frame(106))
        self.assertEqual(len(self.engine.positions), 2)
        self.assertEqual(len(self.engine.closed), 0)
        self.assertEqual(self.engine.equity, 100000.0)
        self.assertEqual(first.status, "OPEN")

    def test_unrealized_pnl_rejects_invalid_price(self):
        self.engine.on_signal(self.signal(), 100)
        for price in (float("nan"), float("inf"), -1, 0, True):
            with self.subTest(price=price):
                with self.assertRaises(ValueError):
                    self.engine.unrealized_pnl(price)

    def test_unrealized_pnl_rejects_invalid_side(self):
        pos = self.engine.on_signal(self.signal(), 100)
        pos.side = "UNKNOWN"
        with self.assertRaises(ValueError):
            self.engine.unrealized_pnl(101)

    def test_cross_symbol_mark_does_not_close(self):
        self.engine.on_signal(self.signal("BUY"), 100)
        foreign = self.frame(106)
        foreign.symbol = "EURUSD"
        self.engine.mark_to_market(foreign)
        self.assertEqual(len(self.engine.positions), 1)
        self.assertEqual(len(self.engine.closed), 0)
        self.assertEqual(self.engine.equity, 100000.0)

    def test_confidence_out_of_range(self):
        for confidence in (-0.01, 1.01):
            with self.subTest(confidence=confidence):
                with self.assertRaises(ValueError):
                    self.engine.on_signal(self.signal(confidence=confidence), 100)
        self.assertEqual(self.engine.seq, 0)

    def test_blank_symbol_rejected(self):
        signal = self.signal()
        signal.symbol = " "
        with self.assertRaises(ValueError):
            self.engine.on_signal(signal, 100)
        self.assertEqual(len(self.engine.positions), 0)

if __name__ == "__main__":
    unittest.main()
