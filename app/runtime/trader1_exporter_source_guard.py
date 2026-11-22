"""Fail-closed source-level hardening for recovered PAPER-only Trader1 MT5 exporter.
Original Drive source is read-only. No MT5 execution or trading functions.
"""

import hashlib

ORIGINAL_SHA256_UTF8 = "0c3f8cc58a13aaa0f7acc1fdfaae6ada89304c68cd3616f677679a211a6fa19e"

def harden_exporter(source: str, *, expected_sha256: str = ORIGINAL_SHA256_UTF8) -> str:
    if not isinstance(source, str):
        raise ValueError('MQL5 source required')
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ValueError('independent SHA-256 required')
    actual = hashlib.sha256(source.encode('utf-8')).hexdigest()
    if actual != expected_sha256:
        raise ValueError('source SHA-256 mismatch; refuse patch')
    if any(api in source for api in ('OrderSend(', 'OrderSendAsync(', 'trade.Buy(', 'trade.Sell(')):
        raise ValueError('trading API found in source; refuse patch')
    anchor = 'int OnInit()\n{\n   g_base = InpExportLinkName;'
    if source.count(anchor) != 1:
        raise ValueError('unexpected OnInit source; refuse patch')
    validation = '''int OnInit()
{
    // Reject invalid exporter windows before file creation or timers.
    if(InpWindowDays < 1 || InpWindowDays > 365 || InpMinimumBars < 1 ||
       InpMaximumBars < 0 || (InpMaximumBars > 0 && InpMaximumBars < InpMinimumBars))
    {
       Print("TRADER1_CONFIG_REJECT");
       return INIT_PARAMETERS_INCORRECT;
    }
   g_base = InpExportLinkName;'''
    return source.replace(anchor, validation, 1)
