"""Regression for recovered historical JSONL writer; offline, temp-directory only."""
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.engines.core import DualModeEngine, TradeIntent, FTMOGuardian, RiskGuardian


def intent(mode="FTMO_SIMULATION_MODE", symbol="EURUSD"):
    return TradeIntent(mode=mode, symbol=symbol, strategy_id="fixture", regime="test",
        entry=1.1, stop=1.0, target=1.3, risk_amount=10.0,
        open_risk=0.0, daily_pnl=0.0, total_pnl=0.0,
        daily_trades=0, loss_streak=0)


class LegacyWriterSafetyTests(unittest.TestCase):
    def test_ftmo_simulation_persists_symbol_in_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            result = engine.process_trade(intent())
            records = (Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").read_text().splitlines()
            self.assertEqual(len(records), 1)
            self.assertEqual(json.loads(records[0])["symbol"], "EURUSD")
            self.assertEqual(result["mode"], "FTMO_SIMULATION_MODE")

    def test_live_mode_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            with self.assertRaisesRegex(ValueError, "PAPER_ONLY_MODE_REQUIRED"):
                engine.process_trade(intent(mode="LIVE"))
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())

    def test_unknown_mode_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            with self.assertRaisesRegex(ValueError, "PAPER_ONLY_MODE_REQUIRED"):
                engine.process_trade(intent(mode="UNKNOWN"))
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())

    def test_positive_pnl_does_not_count_as_loss(self):
        trade = intent()
        trade.daily_pnl = 6000.0
        trade.total_pnl = 12000.0
        ok, reasons = FTMOGuardian().validate(trade)
        self.assertTrue(ok, reasons)

    def test_negative_pnl_consumes_loss_budget(self):
        trade = intent()
        trade.daily_pnl = -4995.0
        trade.total_pnl = -9995.0
        ok, reasons = FTMOGuardian().validate(trade)
        self.assertFalse(ok)
        self.assertIn("DAILY_LOSS_LIMIT_RISK", reasons)
        self.assertIn("TOTAL_LOSS_LIMIT_RISK", reasons)

    def test_nan_rejected_before_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            trade = intent()
            trade.daily_pnl = float("nan")
            with self.assertRaisesRegex(ValueError, "INVALID_NUMERIC_INPUT"):
                engine.process_trade(trade)
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())

    def test_infinite_risk_rejected_before_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            trade = intent()
            trade.risk_amount = float("inf")
            with self.assertRaisesRegex(ValueError, "INVALID_NUMERIC_INPUT"):
                engine.process_trade(trade)
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())

    def test_empty_symbol_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            with self.assertRaisesRegex(ValueError, "SYMBOL_REQUIRED"):
                engine.process_trade(intent(symbol=""))
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
