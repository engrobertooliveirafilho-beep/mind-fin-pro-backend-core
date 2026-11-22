"""Portable static regression for the isolated Trader1 MQL5 exporter source patcher."""
import unittest
from app.runtime.trader1_exporter_source_guard import harden_exporter

ORIGINAL = """#property strict
input int InpWindowDays = 31;
input int InpMinimumBars = 500;
input long InpMaximumBars = 0;
int OnInit()
{
   g_base = InpExportLinkName;
   EventSetTimer(5);
   return INIT_SUCCEEDED;
}
"""

class SourceGuard(unittest.TestCase):
    def test_original_patched_once(self):
        result = harden_exporter(ORIGINAL)
        self.assertEqual(result.count('TRADER1_CONFIG_REJECT'), 1)
        self.assertEqual(result.count('int OnInit()'), 1)

    def test_rejects_unexpected_source(self):
        with self.assertRaises(ValueError): harden_exporter('int OnInit() {}')

    def test_no_real_order_calls_added(self):
        result = harden_exporter(ORIGINAL)
        for forbidden in ('OrderSend(', 'OrderSendAsync(', 'trade.Buy(', 'trade.Sell('):
            self.assertNotIn(forbidden, result)

    def test_original_default_preserved(self):
        result = harden_exporter(ORIGINAL)
        for field in ('InpWindowDays = 31', 'InpMinimumBars = 500', 'InpMaximumBars = 0'):
            self.assertIn(field, result)

    def test_rejects_second_patch(self):
        with self.assertRaises(ValueError): harden_exporter(harden_exporter(ORIGINAL))
