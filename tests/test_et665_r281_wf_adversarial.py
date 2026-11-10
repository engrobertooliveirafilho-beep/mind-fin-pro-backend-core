"""ET665 R281 adversarial checks for historical research evaluator."""
import csv
import pytest
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

FIELDS=["signal_origin","strategy_rule_sha256","ohlc_sha256","timezone","edge_id","entry_time","exit_time","pnl_r","mode","real_orders","ftmo_real","real_execution_allowed"]
def row(entry,exit_,pnl="1",edge="E"):
    return dict(signal_origin="CAUSAL_STRATEGY_REPLAY",strategy_rule_sha256="a"*64,ohlc_sha256="b"*64,timezone="UTC",edge_id=edge,entry_time=entry,exit_time=exit_,pnl_r=pnl,
                mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",
                real_execution_allowed="False")
def evaluate(tmp_path, records, windows=5):
    src=tmp_path/"trades.csv"
    with src.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(records)
    return evaluate_trade_file(src,tmp_path/"report.json",windows=windows)
def test_duplicate_trade_rejected(tmp_path):
    t=row("2026-01-01T10:00+00:00","2026-01-01T10:05+00:00")
    r=evaluate(tmp_path,[t,t])
    assert r["trade_count"]==1 and any(x["error"]=="DUPLICATE_TRADE" for x in r["invalid_rows"])
    assert not r["runtime_promotion_allowed"]
def test_overlapping_trades_flagged(tmp_path):
    r=evaluate(tmp_path,[row("2026-01-01T10:00","2026-01-01T10:30+00:00"),row("2026-01-01T10:15+00:00","2026-01-01T10:40+00:00")])
    assert any(x["error"]=="OVERLAPPING_TRADES" for x in r["invalid_rows"])
    assert not r["runtime_promotion_allowed"]
def test_missing_edge_rejected(tmp_path):
    r=evaluate(tmp_path,[row("2026-01-01T10:00","2026-01-01T10:05",edge="")])
    assert r["trade_count"]==0 and len(r["invalid_rows"])==1
def test_invalid_window_count_rejected(tmp_path):
    with pytest.raises(ValueError):
        evaluate(tmp_path,[],windows=0)
def test_invalid_window_type_rejected(tmp_path):
    with pytest.raises(ValueError):
        evaluate(tmp_path,[],windows=True)
