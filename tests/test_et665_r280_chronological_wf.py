"""Offline tests for ET665.R278 chronological evaluator; synthetic fixture only."""
import csv
from pathlib import Path
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

FIELDS = ["edge_id","entry_time","exit_time","pnl_r","mode","real_orders","ftmo_real","real_execution_allowed"]

def write_fixture(path: Path, records):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(records)

def trade(edge, day, pnl, mode="PAPER_ONLY"):
    t = f"2026-01-{day:02d} 10:00:00+00:00"
    return dict(edge_id=edge,entry_time=t,exit_time=f"2026-01-{day:02d} 10:15:00+00:00",
                pnl_r=pnl,mode=mode,real_orders="FORBIDDEN",
                ftmo_real="FORBIDDEN",real_execution_allowed="False")

def test_valid_trade_folds_are_chronological_and_never_promoted(tmp_path):
    src, dst = tmp_path/"trades.csv",tmp_path/"audit.json"
    write_fixture(src,[trade("EDGE_A",i,(-1)**i) for i in range(1,11)])
    result=evaluate_trade_file(src,dst)
    assert result["trade_count"] == 10 and result["edge_count"] == 1
    assert result["invalid_rows"] == []
    assert len(result["edges"][0]["folds"]) == 5
    assert all(f["count"]==2 for f in result["edges"][0]["folds"])
    assert result["runtime_promotion_allowed"] is False and dst.exists()

def test_reject_live_mode_and_nan(tmp_path):
    src,dst=tmp_path/"trades.csv",tmp_path/"audit.json"
    write_fixture(src,[trade("EDGE_A",1,1.0,"LIVE"),trade("EDGE_A",2,"nan")])
    result=evaluate_trade_file(src,dst)
    assert result["trade_count"] == 0
    assert len(result["invalid_rows"]) == 2
    assert result["runtime_promotion_allowed"] is False

def test_empty_input_remains_closed(tmp_path):
    src,dst=tmp_path/"trades.csv",tmp_path/"audit.json"
    write_fixture(src,[])
    result=evaluate_trade_file(src,dst)
    assert result["edge_count"] == 0 and result["trade_count"] == 0
    assert result["runtime_promotion_allowed"] is False
