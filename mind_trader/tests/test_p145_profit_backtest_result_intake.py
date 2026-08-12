import csv
from pathlib import Path
from app.p145_profit_backtest_result_intake.engine import inspect_result_file, scan_results, run, WATCH_DIR

def test_p145_inspect_valid_result(tmp_path):
    p=tmp_path/"result.csv"
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["strategy_id","asset","timeframe","profit_factor","drawdown","winrate","trades"])
        w.writerow(["s1","WIN","M1","1.5","100","55","20"])
    r=inspect_result_file(p)
    assert r["valid"] is True

def test_p145_scan_results_returns_list():
    assert isinstance(scan_results(), list)

def test_p145_manifest():
    m=run()
    assert m["STATUS"]=="P14.5_PROFIT_BACKTEST_RESULT_INTAKE_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

def test_p145_watch_dir_exists():
    run()
    assert WATCH_DIR.exists()
