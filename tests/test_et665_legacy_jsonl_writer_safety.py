"""Regression for recovered historical JSONL writer; offline, temp-directory only."""
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.engines.core import DualModeEngine, TradeIntent


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

    def test_empty_symbol_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = DualModeEngine(base=directory)
            with self.assertRaisesRegex(ValueError, "SYMBOL_REQUIRED"):
                engine.process_trade(intent(symbol=""))
            self.assertFalse((Path(directory) / "logs" / "FTMO_SIMULATION_LEDGER.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
