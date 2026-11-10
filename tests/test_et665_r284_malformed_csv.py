"""ET665.R284: malformed CSV inputs never bypass quarantine."""
import csv
import pytest
from mind_trader.research.et665_r278_chronological_wf import evaluate_trade_file

def test_null_columns_fail_closed(tmp_path):
    src=tmp_path/"bad.csv"
    src.write_text("edge_id,entry_time,exit_time,pnl_r,mode,real_orders,ftmo_real,real_execution_allowed\nE,2026-01-01T10:00:00+00:00,2026-01-01T10:05:00+00:00,1,PAPER_ONLY,FORBIDDEN,FORBIDDEN\n",encoding="utf-8")
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate_trade_file(src,tmp_path/"out.json")

def test_bad_datetime_fails_closed(tmp_path):
    src=tmp_path/"bad.csv"
    src.write_text("edge_id,entry_time,exit_time,pnl_r,mode,real_orders,ftmo_real,real_execution_allowed\nE,not-a-date,2026-01-01T10:05:00+00:00,1,PAPER_ONLY,FORBIDDEN,FORBIDDEN,False\n",encoding="utf-8")
    with pytest.raises(ValueError,match="CSV_SCHEMA_INVALID"):
        evaluate_trade_file(src,tmp_path/"out.json")
