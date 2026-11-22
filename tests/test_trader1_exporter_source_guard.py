"""Portable static regression for the isolated Trader1 MQL5 exporter source patcher."""
import unittest
import hashlib
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

def patched(source):
    return harden_exporter(source, expected_sha256=hashlib.sha256(source.encode('utf-8')).hexdigest())

class SourceGuard(unittest.TestCase):
    def test_original_patched_once(self):
        result = patched(ORIGINAL)
        self.assertEqual(result.count('TRADER1_CONFIG_REJECT'), 1)
        self.assertEqual(result.count('int OnInit()'), 1)

    def test_rejects_unexpected_source(self):
        with self.assertRaises(ValueError): patched('int OnInit() {}')

    def test_no_real_order_calls_added(self):
        result = patched(ORIGINAL)
        for forbidden in ('OrderSend(', 'OrderSendAsync(', 'trade.Buy(', 'trade.Sell('):
            self.assertNotIn(forbidden, result)

    def test_original_default_preserved(self):
        result = patched(ORIGINAL)
        for field in ('InpWindowDays = 31', 'InpMinimumBars = 500', 'InpMaximumBars = 0'):
            self.assertIn(field, result)

    def test_rejects_second_patch(self):
        with self.assertRaises(ValueError): harden_exporter(patched(ORIGINAL))

    def test_modified_original_rejected_by_default_digest(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            harden_exporter(ORIGINAL)

    def test_injected_trading_api_rejected_even_with_matching_hash(self):
        with self.assertRaisesRegex(ValueError, 'trading API'):
            patched(ORIGINAL + '\nOrderSend(request,result);')

    def test_missing_independent_digest_rejected(self):
        with self.assertRaises(ValueError):
            harden_exporter(ORIGINAL, expected_sha256='')
