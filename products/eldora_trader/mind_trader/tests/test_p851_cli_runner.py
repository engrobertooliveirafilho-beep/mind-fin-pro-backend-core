import csv, math
from mind_trader.app.cli.mind_trader_cli import run_cli
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
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

def test_cli_dry_run():
    r=run_cli(["--mode","daily-research","--dry-run"])
    assert r["decision"]=="DRY_RUN_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_cli_executes_daily_research(tmp_path):
    dbp,cfg=seed(tmp_path)
    r=run_cli(["--mode","daily-research","--symbols","TEST","--timeframes","1m","--db-path",str(dbp),"--ftmo-config",str(cfg),"--limit","3"])
    assert r["decision"]=="DAILY_RESEARCH_RUN_COMPLETE"
    assert r["production"]=="BLOCKED"
    assert r["edge_claim"]=="NONE"
