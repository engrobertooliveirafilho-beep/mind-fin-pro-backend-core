"""Fail-closed source-level hardening for recovered PAPER-only Trader1 MT5 exporter.
Original Drive source is read-only. No MT5 execution or trading functions.
"""

def harden_exporter(source: str) -> str:
    if not isinstance(source, str):
        raise ValueError('MQL5 source required')
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
