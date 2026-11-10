"""ET665.R288 historical hash-derived P2403E input must not be laundered into metrics."""
import csv
import pytest
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

def test_historical_p2403e_filename_rejected(tmp_path):
    src=tmp_path/"p2403e_de40_edge_trade_series.csv"
    src.write_text("edge_id,entry_time,exit_time,pnl_r\n",encoding="utf-8")
    with pytest.raises(ValueError,match="HASH_SCHEDULED_P2403E_SOURCE_FORBIDDEN"):
        evaluate_trade_file(src,tmp_path/"report.json")

def test_unproven_trade_schema_rejected(tmp_path):
    src=tmp_path/"renamed.csv"
    src.write_text("edge_id,entry_time,exit_time,pnl_r,mode,real_orders,ftmo_real,real_execution_allowed\n",encoding="utf-8")
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate_trade_file(src,tmp_path/"report.json")

def test_noncausal_origin_quarantined(tmp_path):
    src=tmp_path/"candidate.csv"
    headers=["signal_origin","strategy_rule_sha256","ohlc_sha256","timezone","edge_id","entry_time","exit_time","pnl_r","mode","real_orders","ftmo_real","real_execution_allowed"]
    with src.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=headers);w.writeheader()
        w.writerow(dict(signal_origin="HASH_SCHEDULED",strategy_rule_sha256="a"*64,ohlc_sha256="b"*64,timezone="UTC",edge_id="E",entry_time="2026-01-01T10:00+00:00",exit_time="2026-01-01T10:15+00:00",pnl_r="1",mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",real_execution_allowed="False"))
    result=evaluate_trade_file(src,tmp_path/"report.json")
    assert result["valid_input"] is False
    assert result["trade_count"]==0
    assert result["runtime_promotion_allowed"] is False
