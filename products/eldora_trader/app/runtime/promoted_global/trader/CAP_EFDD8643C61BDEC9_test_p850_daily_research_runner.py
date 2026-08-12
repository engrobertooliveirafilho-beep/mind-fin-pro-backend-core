import csv, math
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.orchestration.daily_research_runner import run_daily_research
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

def seed(tmp_path):
    cfg=tmp_path/"ftmo.json"; save_default_ftmo_config(str(cfg))
    p=tmp_path/"ohlcv.csv"; dbp=tmp_path/"m.sqlite"
    price=100
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","open","high","low","close","volume"])
        for i in range(180):
            price += math.sin(i/8)*0.3 + 0.05
            w.writerow([f"2026-01-01T{i//60+9:02d}:{i%60:02d}:00",price-0.1,price+0.3,price-0.3,price,1000+i])
    ingest_ohlcv_csv(p,"TEST","1m",str(dbp))
    return dbp,cfg

def test_daily_research_run_complete(tmp_path):
    dbp,cfg=seed(tmp_path)
    r=run_daily_research(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=5,ftmo_config_path=str(cfg))
    assert r["decision"]=="DAILY_RESEARCH_RUN_COMPLETE"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
    assert r["session_close"]["decision"]=="SESSION_CLOSED"
    assert "report_hash" in r
    assert "ledger_hash" in r

def test_daily_research_aborts_without_config(tmp_path):
    dbp,_=seed(tmp_path)
    r=run_daily_research(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=5,ftmo_config_path=str(tmp_path/"missing.json"))
    assert r["decision"]=="DAILY_RUN_ABORTED_SESSION_NOT_OPENED"
    assert r["production"]=="BLOCKED"

def test_daily_research_writes_report(tmp_path):
    dbp,cfg=seed(tmp_path)
    run_daily_research(symbols=("TEST",),timeframes=("1m",),db_path=str(dbp),limit=3,ftmo_config_path=str(cfg))
    assert Path("mind_trader/reports/P8.50_daily_research_report.json").exists()
