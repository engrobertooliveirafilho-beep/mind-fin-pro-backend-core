import csv
from pathlib import Path
from app.p1410_profit_compile_validation_tracker.engine import inspect_compile_file, run, WATCH_DIR

def test_p1410_inspect_valid_compile_file(tmp_path):
    p=tmp_path/"compile.csv"
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["strategy_id","file","compiled","error"])
        w.writerow(["s1","x.nts","true",""])
    r=inspect_compile_file(p)
    assert r["valid"] is True
    assert r["compiled"]==1

def test_p1410_manifest():
    m=run()
    assert m["STATUS"]=="P14.10_PROFIT_COMPILE_VALIDATION_TRACKER_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

def test_p1410_watch_dir_exists():
    run()
    assert WATCH_DIR.exists()
