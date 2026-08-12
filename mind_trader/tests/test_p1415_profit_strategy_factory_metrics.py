from pathlib import Path
import csv
from app.p1415_profit_strategy_factory_metrics.runner import run, inspect_results, CSV_FILE, METRICS_DIR

def test_p1415_manifest_runs_without_csv():
    m = run()
    assert m["STATUS"] == "P14.15_PROFIT_STRATEGY_FACTORY_METRICS_TRACKER_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"

def test_p1415_ranks_metrics_csv():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["strategy_id","file","net_profit","profit_factor","drawdown","win_rate","trades"])
        w.writerow(["a","a.nts","1000","2.0","100","55","100"])
        w.writerow(["b","b.nts","500","1.2","50","45","80"])
    r = inspect_results()
    assert r["valid"] is True
    assert r["rows"] == 2
    assert r["best"]["strategy_id"] == "a"
