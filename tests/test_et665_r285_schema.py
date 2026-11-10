"""ET665.R285 schema and empty-dataset regression tests."""
import pytest
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

HEADER="signal_origin,strategy_rule_sha256,ohlc_sha256,timezone,edge_id,entry_time,exit_time,pnl_r,mode,real_orders,ftmo_real,real_execution_allowed\n"
def evaluate(tmp_path, text):
    src=tmp_path/"input.csv";src.write_text(text,encoding="utf-8")
    return evaluate_trade_file(src,tmp_path/"out.json")
def test_missing_required_column_rejected(tmp_path):
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate(tmp_path,"edge_id,pnl_r\nE,1\n")
def test_duplicate_column_rejected(tmp_path):
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate(tmp_path,HEADER.strip()+",mode\n")
def test_header_only_is_invalid_not_certified(tmp_path):
    result=evaluate(tmp_path,HEADER)
    assert result["valid_input"] is False
    assert result["invalid_rows"][0]["error"]=="EMPTY_DATASET"
    assert result["runtime_promotion_allowed"] is False
def test_zero_byte_input_rejected(tmp_path):
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate(tmp_path,"")
