"""Static fail-closed checks for isolated recovered MQL5 SIMBROKER.
These checks do NOT compile or execute MQL5.
"""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "recovered/mt5/MIND_FileBridge_P2829_SIMBROKER_SAFE.mq5"

class TestSimBrokerStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_no_real_trade_api(self):
        for forbidden in ("OrderSend(", "OrderSendAsync(", "CTrade ", "trade.Buy(", "trade.Sell("):
            self.assertNotIn(forbidden, self.source)

    def test_no_chart_symbol_price_fallback(self):
        self.assertNotIn("SymbolInfoDouble(_Symbol", self.source)
        self.assertIn("SYMBOL_SELECT_REJECT", self.source)
        self.assertIn("PRICE_UNAVAILABLE_REJECT", self.source)

    def test_only_acknowledge_after_ledger_success(self):
        self.assertIn("if(SimAccept(symbol,side,lot,price,tag,raw)) last_raw=raw;", self.source)
        self.assertIn("SIM_LEDGER_OPEN_FAIL", self.source)
        self.assertIn("SIM_LEDGER_WRITE_FAIL", self.source)

    def test_simulated_ledger(self):
        self.assertIn("ACCEPTED,SIM_BROKER", self.source)
        self.assertIn("REAL_ORDERS=FORBIDDEN", self.source)

    def test_ledger_header_failure_blocks_startup(self):
        self.assertIn("if(!EnsureLedgerHeader()) return INIT_FAILED;", self.source)
        self.assertIn("return n==StringLen(header);", self.source)

    def test_csv_quotes_raw_signal(self):
        self.assertIn("CsvField(raw)", self.source)
        self.assertIn("CsvField(tag)", self.source)
        self.assertIn('StringReplace(value,"\\\"","\\\"\\\"")', self.source)

    def test_strict_lot_grammar(self):
        self.assertIn("StringGetCharacter(lot_raw,i)", self.source)
        self.assertIn("NormalizeDouble(lot,2)<=0.0", self.source)

    def test_validate_lot_and_symbol(self):
        self.assertIn("MathIsValidNumber(lot)", self.source)
        self.assertIn("SymbolSelect(symbol,true)", self.source)

if __name__ == "__main__":
    unittest.main()
