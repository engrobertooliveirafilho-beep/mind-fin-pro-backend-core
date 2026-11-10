"""ET665.R283: timezone, overlap and fail-closed adversarial regression."""
import csv
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

FIELDS=("signal_origin","strategy_rule_sha256","ohlc_sha256","timezone","edge_id","entry_time","exit_time","pnl_r","mode","real_orders","ftmo_real","real_execution_allowed")
def row(entry,exit_,edge="E"):
    return dict(signal_origin="CAUSAL_STRATEGY_REPLAY",strategy_rule_sha256="a"*64,ohlc_sha256="b"*64,timezone="UTC",edge_id=edge,entry_time=entry,exit_time=exit_,pnl_r="1",
                mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",
                real_execution_allowed="False")
def run(tmp_path,records):
    src=tmp_path/"input.csv";out=tmp_path/"audit.json"
    with src.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader();writer.writerows(records)
    return evaluate_trade_file(src,out)
def test_naive_timestamp_rejected(tmp_path):
    result=run(tmp_path,[row("2026-01-01T10:00","2026-01-01T10:05")])
    assert not result["valid_input"]
    assert result["trade_count"]==0
    assert result["invalid_rows"][0]["error"]=="TIMEZONE_REQUIRED"
def test_timezone_aware_input_accepted_but_not_promoted(tmp_path):
    result=run(tmp_path,[row("2026-01-01T10:00:00+00:00","2026-01-01T10:05:00+00:00")])
    assert result["valid_input"] and result["trade_count"]==1
    assert not result["runtime_promotion_allowed"]
def test_overlaps_suppress_all_metrics(tmp_path):
    result=run(tmp_path,[row("2026-01-01T10:00:00+00:00","2026-01-01T10:30:00+00:00"),
                            row("2026-01-01T10:15:00+00:00","2026-01-01T10:40:00+00:00")])
    assert not result["valid_input"]
    assert result["edges"][0]["folds"]==[]
    assert result["edges"][0]["status"]=="INVALID_INPUT_QUARANTINE"
def test_mixed_invalid_row_suppresses_valid_edge_metrics(tmp_path):
    a=row("2026-01-01T10:00:00+00:00","2026-01-01T10:05:00+00:00")
    b=row("2026-01-02T10:00:00+00:00","2026-01-02T10:05:00+00:00",edge="F")
    b["mode"]="LIVE"
    result=run(tmp_path,[a,b])
    assert not result["valid_input"]
    assert result["edges"][0]["folds"]==[]
