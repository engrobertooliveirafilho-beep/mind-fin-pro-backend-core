from pathlib import Path
import re

SOURCE = Path("recovery/original/trader_1_001_r2_r1/TRADER_1_001_FTMO_M1_SATURATION_EXPORT.mq5")
V2 = Path("recovery/candidate/trader_1_001/TRADER_1_001_FTMO_M1_SATURATION_EXPORT_V2.mq5")
COMPILE_LOG = Path("recovery/original/trader_1_001_r2_r1/TRADER_1_001_COMPILE_HOTFIX_20260716_214032.log")

def _symbols(source):
    block = re.search(r"string\s+CanonicalSymbols\[\]\s*=\s*\{(.*?)\};", source, re.S)
    assert block, "CANONICAL_SYMBOL_ARRAY_NOT_FOUND"
    return re.findall(r'"([^"]+)"', block.group(1))

def test_original_exporter_has_58_unique_canonical_assets():
    source = SOURCE.read_text(encoding="utf-8")
    symbols = _symbols(source)
    assert len(symbols) == 58
    assert len(set(symbols)) == 58

def test_original_symbol_exist_hotfix_is_present():
    source = SOURCE.read_text(encoding="utf-8")
    assert "SymbolExist(canonical, isCustomSymbol)" in source
    assert "SymbolExist(canonical)" not in source

def test_original_exporter_is_read_only_no_trade_api():
    source = SOURCE.read_text(encoding="utf-8")
    forbidden = [r"\bOrderSend\s*\(", r"\bCTrade\b", r"\.Buy\s*\(", r"\.Sell\s*\(", r"\bPositionOpen\s*\("]
    assert not any(re.search(pattern, source) for pattern in forbidden)
    assert "CopyRates(" in source and "PERIOD_M1" in source

def test_historical_compile_log_reports_zero_errors_and_warnings():
    log = COMPILE_LOG.read_text(encoding="utf-8")
    assert "Result: 0 errors, 0 warnings" in log

def test_v2_does_not_mark_partial_export_as_complete():
    source = V2.read_text(encoding="utf-8")
    assert 'exportRunComplete = (exported == total && unavailable == 0 && manifestRenamed)' in source
    assert 'STATUS=" + (exportRunComplete ? "EXPORT_RUN_COMPLETE" : "EXPORT_RUN_INCOMPLETE")' in source
    assert 'status = "STABLE_AVAILABLE_HISTORY"' in source
    assert 'FileWrite(marker, "STATUS=COMPLETE")' not in source
