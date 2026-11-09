from app.p1621f_transcript_download_strategy_extraction.engine import extract_rules, run
import pytest

def test_p1621f_extract_rules():
    r=extract_rules("setup com rsi vwap stop alvo rompimento",{})
    assert "RSI_SIGNAL" in r
    assert "VWAP_FILTER" in r
    assert "BREAKOUT" in r

def test_p1621f_run_blocks_live():
    with pytest.raises(RuntimeError, match="ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"):
        run()
